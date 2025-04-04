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

# Signal that will be sent when a template is rendered
template_rendered = Signal()

# Settings that may cause issues when using 'override_settings' (#19031)
COMPLEX_OVERRIDE_SETTINGS = {'DATABASES'}


@receiver(setting_changed)
def clear_cache_handlers(**kwargs):
    """Reset the cache configuration when CACHES setting changes."""
    if kwargs['setting'] == 'CACHES':
        from django.core.cache import caches, close_caches
        close_caches()
        caches._settings = caches.settings = caches.configure_settings(None)
        caches._connections = Local()


@receiver(setting_changed)
def update_installed_apps(**kwargs):
    """Update various caches when INSTALLED_APPS changes."""
    if kwargs['setting'] == 'INSTALLED_APPS':
        # Clear static files finder cache
        from django.contrib.staticfiles.finders import get_finder
        get_finder.cache_clear()
        
        # Clear management commands cache
        from django.core.management import get_commands
        get_commands.cache_clear()
        
        # Clear template directories cache
        from django.template.utils import get_app_template_dirs
        get_app_template_dirs.cache_clear()
        
        # Clear translations cache
        from django.utils.translation import trans_real
        trans_real._translations = {}


@receiver(setting_changed)
def update_connections_time_zone(**kwargs):
    """Update timezone settings for process and database connections."""
    if kwargs['setting'] == 'TIME_ZONE':
        # Reset process time zone if supported
        if hasattr(time, 'tzset'):
            if kwargs['value']:
                os.environ['TZ'] = kwargs['value']
            else:
                os.environ.pop('TZ', None)
            time.tzset()

        # Clear default timezone cache
        timezone.get_default_timezone.cache_clear()

    # Reset database connections' time zone settings
    if kwargs['setting'] in {'TIME_ZONE', 'USE_TZ'}:
        for conn in connections.all():
            # Remove timezone attributes safely
            for attr in ('timezone', 'timezone_name'):
                if hasattr(conn, attr):
                    delattr(conn, attr)
            
            # Reestablish timezone settings
            conn.ensure_timezone()


@receiver(setting_changed)
def clear_routers_cache(**kwargs):
    """Rebuild database routers when DATABASE_ROUTERS changes."""
    if kwargs['setting'] == 'DATABASE_ROUTERS':
        router.routers = ConnectionRouter().routers


@receiver(setting_changed)
def reset_template_engines(**kwargs):
    """Reset template engine configuration when relevant settings change."""
    template_related_settings = {
        'TEMPLATES',
        'DEBUG',
        'INSTALLED_APPS',
    }
    
    if kwargs['setting'] in template_related_settings:
        from django.template import engines
        
        # Reset engines attributes safely
        if hasattr(engines, 'templates'):
            delattr(engines, 'templates')
        
        engines._templates = None
        engines._engines = {}
        
        # Clear related caches
        from django.template.engine import Engine
        Engine.get_default.cache_clear()
        
        from django.forms.renderers import get_default_renderer
        get_default_renderer.cache_clear()


@receiver(setting_changed)
def clear_serializers_cache(**kwargs):
    """Reset serializers when SERIALIZATION_MODULES changes."""
    if kwargs['setting'] == 'SERIALIZATION_MODULES':
        from django.core import serializers
        serializers._serializers = {}


@receiver(setting_changed)
def language_changed(**kwargs):
    """Update language and translation settings."""
    language_code_settings = {'LANGUAGES', 'LANGUAGE_CODE', 'LOCALE_PATHS'}
    translation_path_settings = {'LANGUAGES', 'LOCALE_PATHS'}
    
    if kwargs['setting'] in language_code_settings:
        from django.utils.translation import trans_real
        trans_real._default = None
        trans_real._active = Local()
        
    if kwargs['setting'] in translation_path_settings:
        from django.utils.translation import trans_real
        trans_real._translations = {}
        trans_real.check_for_language.cache_clear()


@receiver(setting_changed)
def localize_settings_changed(**kwargs):
    """Reset formatting caches when localization settings change."""
    if kwargs['setting'] in FORMAT_SETTINGS or kwargs['setting'] == 'USE_THOUSAND_SEPARATOR':
        reset_format_cache()


@receiver(setting_changed)
def file_storage_changed(**kwargs):
    """Reset default file storage when DEFAULT_FILE_STORAGE changes."""
    if kwargs['setting'] == 'DEFAULT_FILE_STORAGE':
        from django.core.files.storage import default_storage
        default_storage._wrapped = empty


@receiver(setting_changed)
def complex_setting_changed(**kwargs):
    """Warn when complex settings are overridden."""
    if kwargs['enter'] and kwargs['setting'] in COMPLEX_OVERRIDE_SETTINGS:
        # Stack level 6 shows the line with the override_settings call
        warnings.warn(
            f"Overriding setting {kwargs['setting']} can lead to unexpected behavior.",
            stacklevel=6
        )


@receiver(setting_changed)
def root_urlconf_changed(**kwargs):
    """Reset URL configuration when ROOT_URLCONF changes."""
    if kwargs['setting'] == 'ROOT_URLCONF':
        from django.urls import clear_url_caches, set_urlconf
        clear_url_caches()
        set_urlconf(None)


@receiver(setting_changed)
def static_storage_changed(**kwargs):
    """Reset static files storage when related settings change."""
    static_storage_settings = {
        'STATICFILES_STORAGE',
        'STATIC_ROOT',
        'STATIC_URL',
    }
    
    if kwargs['setting'] in static_storage_settings:
        from django.contrib.staticfiles.storage import staticfiles_storage
        staticfiles_storage._wrapped = empty


@receiver(setting_changed)
def static_finders_changed(**kwargs):
    """Reset static file finders when related settings change."""
    static_finder_settings = {
        'STATICFILES_DIRS',
        'STATIC_ROOT',
    }
    
    if kwargs['setting'] in static_finder_settings:
        from django.contrib.staticfiles.finders import get_finder
        get_finder.cache_clear()


@receiver(setting_changed)
def auth_password_validators_changed(**kwargs):
    """Reset password validators when AUTH_PASSWORD_VALIDATORS changes."""
    if kwargs['setting'] == 'AUTH_PASSWORD_VALIDATORS':
        from django.contrib.auth.password_validation import get_default_password_validators
        get_default_password_validators.cache_clear()


@receiver(setting_changed)
def user_model_swapped(**kwargs):
    """Update references to the user model when AUTH_USER_MODEL changes."""
    if kwargs['setting'] == 'AUTH_USER_MODEL':
        # Clear apps cache to reload model relationships
        apps.clear_cache()
        
        try:
            # Get the new user model
            from django.contrib.auth import get_user_model
            UserModel = get_user_model()
            
            # Update UserModel references in various auth modules
            update_modules = [
                'django.contrib.auth.backends',
                'django.contrib.auth.forms',
                'django.contrib.auth.handlers.modwsgi',
                'django.contrib.auth.management.commands.changepassword',
                'django.contrib.auth.views',
            ]
            
            for module_path in update_modules:
                module_parts = module_path.split('.')
                module_name = module_parts[-1]
                module_path = '.'.join(module_parts[:-1])
                
                module = __import__(module_path, fromlist=[module_name])
                submodule = getattr(module, module_name)
                submodule.UserModel = UserModel
                
        except ImproperlyConfigured:
            # Some tests set an invalid AUTH_USER_MODEL
            pass