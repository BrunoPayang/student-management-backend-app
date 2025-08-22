"""
Test settings for Django project
"""
import os
from .base import *

# Test-specific settings
DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = False

# Use in-memory SQLite database for testing (faster than PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use console email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable Celery tasks during testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Use fast cache backend for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Disable external services for testing
FIREBASE_CREDENTIALS_PATH = None
FIREBASE_STORAGE_BUCKET = 'test-bucket'
FIREBASE_PROJECT_ID = 'test-project'

# Use mock FCM service for testing
USE_MOCK_FCM = True
USE_MOCK_STORAGE = True

# Test file upload settings
MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')
MEDIA_URL = '/test_media/'

# Disable static file collection during tests
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Test-specific secret key
SECRET_KEY = 'test-secret-key-for-testing-only'

# Test-specific allowed hosts
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# Test-specific timezone
TIME_ZONE = 'UTC'

# Disable debug toolbar during tests
if 'debug_toolbar' in INSTALLED_APPS:
    INSTALLED_APPS.remove('debug_toolbar')

# Disable CSRF for API tests
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# Enable migrations for tests to create tables
MIGRATION_MODULES = {}
