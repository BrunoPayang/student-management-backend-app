"""
Development settings for schoolconnect project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Add debug toolbar for development
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# Debug toolbar configuration
INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Database URL for development (can be overridden by environment variable)
import dj_database_url
if config('DATABASE_URL', default=None):
    DATABASES['default'] = dj_database_url.parse(config('DATABASE_URL'))

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Add browsable API renderer for development
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append(
    'rest_framework.renderers.BrowsableAPIRenderer'
) 