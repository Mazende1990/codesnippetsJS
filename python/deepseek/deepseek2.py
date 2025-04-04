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

# Settings that may not work well when using 'override_settings'
COMPLEX_OVERRIDE_SETTINGS = {'DATABASES'}

# --------------------------
# Cache Management Handlers
# --------------------------

@receiver(setting_changed)
def clear_cache_handlers(**kwargs):
    """Handle changes to CACHES setting by resetting cache connections."""
    if kwargs['setting'] == 'CACHES':
        from django.core.cache import caches, close_caches
        close_caches()
        caches._settings = caches.settings = caches.configure_settings(None)
        caches._connections = Local()


# --------------------------
# App Configuration Handlers
# --------------------------

@receiver(setting_changed)
def update_installed_apps(**kwargs):
    """Reset various caches when INSTALLED_APPS changes."""
    if kwargs['setting'] == 'INSTALLED_APPS':
        # Rebuild static files finder cache
        from django.contrib.staticfiles.finders import get_finder
        get_finder.cache_clear()
        
        # Rebuild management commands cache
        from django.core.management import get_commands
        get_commands.cache_clear()
        
        # Rebuild template directories cache
        from django.template.utils import get_app_template_dirs
        get_app_template_dirs.cache_clear()
        
        # Rebuild translations cache
        from django.utils.translation import trans_real
        trans_real._translations = {}


# --------------------------
# Timezone Configuration
# --------------------------

@receiver(setting_changed)
def update_connections_time_zone(**kwargs):
    """Update timezone settings when TIME_ZONE or USE_TZ changes."""
    setting = kwargs['setting']
    
    if setting == 'TIME_ZONE':
        # Update process timezone
        if hasattr(time, 'tzset'):
            if kwargs['value']:
                os.environ['TZ'] = kwargs['value']
            else:
                os.environ.pop('TZ', None)
            time.tzset()
        
        # Clear timezone cache
        timezone.get_default_timezone.cache_clear()

    if setting in {'TIME_ZONE', 'USE_TZ'}:
        # Reset database connection timezones
        for conn in connections.all():
            for attr in ['timezone', 'timezone_name']:
                try:
                    delattr(conn, attr)
                except AttributeError:
                    pass
            conn.ensure_timezone()


# --------------------------
# Database Configuration
# --------------------------

@receiver(setting_changed)
def clear_routers_cache(**kwargs):
    """Reset database routers when DATABASE_ROUTERS changes."""
    if kwargs['setting'] == 'DATABASE_ROUTERS':
        router.routers = ConnectionRouter().routers


# --------------------------
# Template System Handlers
# --------------------------

@receiver(setting_changed)
def reset_template_engines(**kwargs):
    """Reset template engines when related settings change."""
    if kwargs['setting'] in {'TEMPLATES', 'DEBUG', 'INSTALLED_APPS'}:
        from django.template import engines
        try:
            del engines.templates
        except AttributeError:
            pass
        engines._templates = None
        engines._engines = {}
        
        from django.template.engine import Engine
        Engine.get_default.cache_clear()
        
        from django.forms.renderers import get_default_renderer
        get_default_renderer.cache_clear()


# --------------------------
# Serialization Handlers
# --------------------------

@receiver(setting_changed)
def clear_serializers_cache(**kwargs):
    """Reset serializers when SERIALIZATION_MODULES changes."""
    if kwargs['setting'] == 'SERIALIZATION_MODULES':
        from django.core import serializers
        serializers._serializers = {}


# --------------------------
# Internationalization
# --------------------------

@receiver(setting_changed)
def language_changed(**kwargs):
    """Handle changes to language-related settings."""
    setting = kwargs['setting']
    
    if setting in {'LANGUAGES', 'LANGUAGE_CODE', 'LOCALE_PATHS'}:
        from django.utils.translation import trans_real
        trans_real._default = None
        trans_real._active = Local()
    
    if setting in {'LANGUAGES', 'LOCALE_PATHS'}:
        from django.utils.translation import trans_real
        trans_real._translations = {}
        trans_real.check_for_language.cache_clear()


@receiver(setting_changed)
def localize_settings_changed(**kwargs):
    """Reset format cache when localization settings change."""
    if kwargs['setting'] in FORMAT_SETTINGS or kwargs['setting'] == 'USE_THOUSAND_SEPARATOR':
        reset_format_cache()


# --------------------------
# File Storage Handlers
# --------------------------

@receiver(setting_changed)
def file_storage_changed(**kwargs):
    """Reset default file storage when DEFAULT_FILE_STORAGE changes."""
    if kwargs['setting'] == 'DEFAULT_FILE_STORAGE':
        from django.core.files.storage import default_storage
        default_storage._wrapped = empty


# --------------------------
# URL Configuration
# --------------------------

@receiver(setting_changed)
def root_urlconf_changed(**kwargs):
    """Reset URL caches when ROOT_URLCONF changes."""
    if kwargs['setting'] == 'ROOT_URLCONF':
        from django.urls import clear_url_caches, set_urlconf
        clear_url_caches()
        set_urlconf(None)


# --------------------------
# Static Files Handlers
# --------------------------

@receiver(setting_changed)
def static_storage_changed(**kwargs):
    """Reset static files storage when related settings change."""
    if kwargs['setting'] in {'STATICFILES_STORAGE', 'STATIC_ROOT', 'STATIC_URL'}:
        from django.contrib.staticfiles.storage import staticfiles_storage
        staticfiles_storage._wrapped = empty


@receiver(setting_changed)
def static_finders_changed(**kwargs):
    """Reset static files finders when related settings change."""
    if kwargs['setting'] in {'STATICFILES_DIRS', 'STATIC_ROOT'}:
        from django.contrib.staticfiles.finders import get_finder
        get_finder.cache_clear()


# --------------------------
# Authentication Handlers
# --------------------------

@receiver(setting_changed)
def auth_password_validators_changed(**kwargs):
    """Reset password validators cache when AUTH_PASSWORD_VALIDATORS changes."""
    if kwargs['setting'] == 'AUTH_PASSWORD_VALIDATORS':
        from django.contrib.auth.password_validation import get_default_password_validators
        get_default_password_validators.cache_clear()


@receiver(setting_changed)
def user_model_swapped(**kwargs):
    """Handle changes to AUTH_USER_MODEL by resetting related caches."""
    if kwargs['setting'] == 'AUTH_USER_MODEL':
        apps.clear_cache()
        try:
            from django.contrib.auth import get_user_model
            UserModel = get_user_model()
        except ImproperlyConfigured:
            # Some tests set an invalid AUTH_USER_MODEL
            pass
        else:
            # Update all modules that reference UserModel
            modules_to_update = [
                'django.contrib.auth.backends',
                'django.contrib.auth.forms',
                'django.contrib.auth.handlers.modwsgi',
                'django.contrib.auth.management.commands.changepassword',
                'django.contrib.auth.views'
            ]
            
            for module_path in modules_to_update:
                module = __import__(module_path, fromlist=['UserModel'])
                module.UserModel = UserModel


# --------------------------
# Complex Settings Warning
# --------------------------

@receiver(setting_changed)
def complex_setting_changed(**kwargs):
    """Warn about potential issues with complex setting overrides."""
    if kwargs['enter'] and kwargs['setting'] in COMPLEX_OVERRIDE_SETTINGS:
        warnings.warn(
            f"Overriding setting {kwargs['setting']} can lead to unexpected behavior.",
            stacklevel=6
        )