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

# Database configuration for development
# Use SQLite for local development, PostgreSQL for production
if config('DATABASE_URL', default=None):
    # Use PostgreSQL if DATABASE_URL is provided
    import dj_database_url
    DATABASES['default'] = dj_database_url.parse(config('DATABASE_URL'))
else:
    # Use SQLite for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Add browsable API renderer for development
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append(
    'rest_framework.renderers.BrowsableAPIRenderer'
) 