"""
Development settings for schoolconnect project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allow ngrok domains for development and Render domains
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    '0.0.0.0',
    'b461159c6436.ngrok-free.app',
    '.ngrok-free.app',  # Allow all ngrok-free.app subdomains
    '.ngrok.io',        # Allow all ngrok.io subdomains
    '10.0.2.2',
    'schoolconnect-qeaf.onrender.com',  # Render domain
    'dashboard-app-287c.onrender.com',  # Dashboard app domain
    '.onrender.com'     # Allow all onrender.com subdomains
]

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

# Celery Configuration for Development
CELERY_TASK_ALWAYS_EAGER = True  # Run tasks synchronously in development
CELERY_TASK_EAGER_PROPAGATES = True

# Redis Configuration for Development
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0 