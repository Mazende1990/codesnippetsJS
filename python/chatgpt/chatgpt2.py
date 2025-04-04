import os
import time
import warnings

from asgiref.local import Local
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.core.signals import setting_changed
from django.db import connections, router
from django.db.utils import ConnectionRouter
from django.dispatch import Signal, receiver
from django.utils import timezone
from django.utils.formats import FORMAT_SETTINGS, reset_format_cache
from django.utils.functional import empty

# Custom signal
template_rendered = Signal()

# Settings that are known to behave poorly with override_settings
COMPLEX_OVERRIDE_SETTINGS = {'DATABASES'}


@receiver(setting_changed)
def clear_cache_handlers(**kwargs):
    """Clear cache handlers when CACHES setting changes."""
    if kwargs['setting'] == 'CACHES':
        from django.core.cache import caches, close_caches
        close_caches()
        caches._settings = caches.settings = caches.configure_settings(None)
        caches._connections = Local()


@receiver(setting_changed)
def update_installed_apps(**kwargs):
    """Clear caches affected by changes in INSTALLED_APPS."""
    if kwargs['setting'] == 'INSTALLED_APPS':
        from django.contrib.staticfiles.finders import get_finder
        from django.core.management import get_commands
        from django.template.utils import get_app_template_dirs
        from django.utils.translation import trans_real

        get_finder.cache_clear()
        get_commands.cache_clear()
        get_app_template_dirs.cache_clear()
        trans_real._translations = {}


@receiver(setting_changed)
def update_connections_time_zone(**kwargs):
    """Handle time zone-related changes."""
    setting = kwargs['setting']
    value = kwargs['value']

    if setting == 'TIME_ZONE' and hasattr(time, 'tzset'):
        if value:
            os.environ['TZ'] = value
        else:
            os.environ.pop('TZ', None)
        time.tzset()
        timezone.get_default_timezone.cache_clear()

    if setting in {'TIME_ZONE', 'USE_TZ'}:
        for conn in connections.all():
            for attr in ('timezone', 'timezone_name'):
                if hasattr(conn, attr):
                    delattr(conn, attr)
            conn.ensure_timezone()


@receiver(setting_changed)
def clear_routers_cache(**kwargs):
    """Reset database routers when DATABASE_ROUTERS changes."""
    if kwargs['setting'] == 'DATABASE_ROUTERS':
        router.routers = ConnectionRouter().routers


@receiver(setting_changed)
def reset_template_engines(**kwargs):
    """Reset template engine when relevant settings change."""
    if kwargs['setting'] in {'TEMPLATES', 'DEBUG', 'INSTALLED_APPS'}:
        from django.template import engines
        from django.template.engine import Engine
        from django.forms.renderers import get_default_renderer

        engines._templates = None
        engines._engines = {}
        Engine.get_default.cache_clear()
        get_default_renderer.cache_clear()
        try:
            del engines.templates
        except AttributeError:
            pass


@receiver(setting_changed)
def clear_serializers_cache(**kwargs):
    """Clear serializers cache on change to SERIALIZATION_MODULES."""
    if kwargs['setting'] == 'SERIALIZATION_MODULES':
        from django.core import serializers
        serializers._serializers = {}


@receiver(setting_changed)
def language_changed(**kwargs):
    """Handle language/locale related changes."""
    setting = kwargs['setting']
    from django.utils.translation import trans_real

    if setting in {'LANGUAGES', 'LANGUAGE_CODE', 'LOCALE_PATHS'}:
        trans_real._default = None
        trans_real._active = Local()
    if setting in {'LANGUAGES', 'LOCALE_PATHS'}:
        trans_real._translations = {}
        trans_real.check_for_language.cache_clear()


@receiver(setting_changed)
def localize_settings_changed(**kwargs):
    """Clear format cache on localization-related setting changes."""
    if kwargs['setting'] in FORMAT_SETTINGS or kwargs['setting'] == 'USE_THOUSAND_SEPARATOR':
        reset_format_cache()


@receiver(setting_changed)
def file_storage_changed(**kwargs):
    """Reset default file storage wrapper when DEFAULT_FILE_STORAGE changes."""
    if kwargs['setting'] == 'DEFAULT_FILE_STORAGE':
        from django.core.files.storage import default_storage
        default_storage._wrapped = empty


@receiver(setting_changed)
def complex_setting_changed(**kwargs):
    """Warn when overriding complex settings that may cause side effects."""
    if kwargs['enter'] and kwargs['setting'] in COMPLEX_OVERRIDE_SETTINGS:
        warnings.warn(
            f"Overriding setting {kwargs['setting']} can lead to unexpected behavior.",
            stacklevel=6
        )


@receiver(setting_changed)
def root_urlconf_changed(**kwargs):
    """Clear URL caches when ROOT_URLCONF changes."""
    if kwargs['setting'] == 'ROOT_URLCONF':
        from django.urls import clear_url_caches, set_urlconf
        clear_url_caches()
        set_urlconf(None)


@receiver(setting_changed)
def static_storage_changed(**kwargs):
    """Reset static file storage when related settings change."""
    if kwargs['setting'] in {'STATICFILES_STORAGE', 'STATIC_ROOT', 'STATIC_URL'}:
        from django.contrib.staticfiles.storage import staticfiles_storage
        staticfiles_storage._wrapped = empty


@receiver(setting_changed)
def static_finders_changed(**kwargs):
    """Clear static files finder cache when directory settings change."""
    if kwargs['setting'] in {'STATICFILES_DIRS', 'STATIC_ROOT'}:
        from django.contrib.staticfiles.finders import get_finder
        get_finder.cache_clear()


@receiver(setting_changed)
def auth_password_validators_changed(**kwargs):
    """Clear password validators cache on change."""
    if kwargs['setting'] == 'AUTH_PASSWORD_VALIDATORS':
        from django.contrib.auth.password_validation import get_default_password_validators
        get_default_password_validators.cache_clear()


@receiver(setting_changed)
def user_model_swapped(**kwargs):
    """Reset and reassign user model across auth modules when AUTH_USER_MODEL changes."""
    if kwargs['setting'] == 'AUTH_USER_MODEL':
        apps.clear_cache()
        try:
            from django.contrib.auth import get_user_model
            UserModel = get_user_model()
        except ImproperlyConfigured:
            return

        from django.contrib.auth import backends, forms, views
        from django.contrib.auth.handlers import modwsgi
        from django.contrib.auth.management.commands import changepassword

        backends.UserModel = UserModel
        forms.UserModel = UserModel
        modwsgi.UserModel = UserModel
        changepassword.UserModel = UserModel
        views.UserModel = UserModel
