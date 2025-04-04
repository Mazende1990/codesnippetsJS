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

template_rendered = Signal()

# Settings that may not work well when using 'override_settings' (#19031)
COMPLEX_OVERRIDE_SETTINGS = {'DATABASES'}


@receiver(setting_changed)
def _clear_cache_handlers(setting, **kwargs):
    """Clears cache-related settings and connections."""
    if setting == 'CACHES':
        from django.core.cache import caches, close_caches

        close_caches()
        caches._settings = caches.settings = caches.configure_settings(None)
        caches._connections = Local()


@receiver(setting_changed)
def _update_installed_apps(setting, **kwargs):
    """Updates caches related to installed applications."""
    if setting == 'INSTALLED_APPS':
        from django.contrib.staticfiles.finders import get_finder
        from django.core.management import get_commands
        from django.template.utils import get_app_template_dirs
        from django.utils.translation import trans_real

        get_finder.cache_clear()
        get_commands.cache_clear()
        get_app_template_dirs.cache_clear()
        trans_real._translations = {}


@receiver(setting_changed)
def _update_connections_time_zone(setting, value, **kwargs):
    """Updates time zone settings and database connections."""
    if setting == 'TIME_ZONE':
        if hasattr(time, 'tzset'):
            if value:
                os.environ['TZ'] = value
            else:
                os.environ.pop('TZ', None)
            time.tzset()

        timezone.get_default_timezone.cache_clear()

    if setting in {'TIME_ZONE', 'USE_TZ'}:
        for conn in connections.all():
            try:
                del conn.timezone
            except AttributeError:
                pass
            try:
                del conn.timezone_name
            except AttributeError:
                pass
            conn.ensure_timezone()


@receiver(setting_changed)
def _clear_routers_cache(setting, **kwargs):
    """Clears the database routers cache."""
    if setting == 'DATABASE_ROUTERS':
        router.routers = ConnectionRouter().routers


@receiver(setting_changed)
def _reset_template_engines(setting, **kwargs):
    """Resets template engine configurations."""
    if setting in {'TEMPLATES', 'DEBUG', 'INSTALLED_APPS'}:
        from django.template import engines
        from django.template.engine import Engine
        from django.forms.renderers import get_default_renderer

        try:
            del engines.templates
        except AttributeError:
            pass
        engines._templates = None
        engines._engines = {}
        Engine.get_default.cache_clear()
        get_default_renderer.cache_clear()


@receiver(setting_changed)
def _clear_serializers_cache(setting, **kwargs):
    """Clears the serializers cache."""
    if setting == 'SERIALIZATION_MODULES':
        from django.core import serializers

        serializers._serializers = {}


@receiver(setting_changed)
def _language_changed(setting, **kwargs):
    """Updates language-related settings and caches."""
    if setting in {'LANGUAGES', 'LANGUAGE_CODE', 'LOCALE_PATHS'}:
        from django.utils.translation import trans_real

        trans_real._default = None
        trans_real._active = Local()
    if setting in {'LANGUAGES', 'LOCALE_PATHS'}:
        from django.utils.translation import trans_real

        trans_real._translations = {}
        trans_real.check_for_language.cache_clear()


@receiver(setting_changed)
def _localize_settings_changed(setting, **kwargs):
    """Resets localization format caches."""
    if setting in FORMAT_SETTINGS or setting == 'USE_THOUSAND_SEPARATOR':
        reset_format_cache()


@receiver(setting_changed)
def _file_storage_changed(setting, **kwargs):
    """Resets the default file storage."""
    if setting == 'DEFAULT_FILE_STORAGE':
        from django.core.files.storage import default_storage

        default_storage._wrapped = empty


@receiver(setting_changed)
def _complex_setting_changed(setting, enter, **kwargs):
    """Warns about overriding complex settings."""
    if enter and setting in COMPLEX_OVERRIDE_SETTINGS:
        warnings.warn(
            f"Overriding setting {setting} can lead to unexpected behavior.",
            stacklevel=6,
        )


@receiver(setting_changed)
def _root_urlconf_changed(setting, **kwargs):
    """Resets URL configuration caches."""
    if setting == 'ROOT_URLCONF':
        from django.urls import clear_url_caches, set_urlconf

        clear_url_caches()
        set_urlconf(None)


@receiver(setting_changed)
def _static_storage_changed(setting, **kwargs):
    """Resets static file storage."""
    if setting in {'STATICFILES_STORAGE', 'STATIC_ROOT', 'STATIC_URL'}:
        from django.contrib.staticfiles.storage import staticfiles_storage

        staticfiles_storage._wrapped = empty


@receiver(setting_changed)
def _static_finders_changed(setting, **kwargs):
    """Resets static file finders cache."""
    if setting in {'STATICFILES_DIRS', 'STATIC_ROOT'}:
        from django.contrib.staticfiles.finders import get_finder

        get_finder.cache_clear()


@receiver(setting_changed)
def _auth_password_validators_changed(setting, **kwargs):
    """Resets password validators cache."""
    if setting == 'AUTH_PASSWORD_VALIDATORS':
        from django.contrib.auth.password_validation import (
            get_default_password_validators,
        )

        get_default_password_validators.cache_clear()


@receiver(setting_changed)
def _user_model_swapped(setting, **kwargs):
    """Updates user model references when swapped."""
    if setting == 'AUTH_USER_MODEL':
        apps.clear_cache()
        try:
            from django.contrib.auth import get_user_model

            UserModel = get_user_model()
        except ImproperlyConfigured:
            pass
        else:
            from django.contrib.auth import backends, forms, handlers, management, views

            backends.UserModel = UserModel
            forms.UserModel = UserModel
            handlers.modwsgi.UserModel = UserModel
            management.commands.changepassword.UserModel = UserModel
            views.UserModel = UserModel