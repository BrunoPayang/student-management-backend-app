"""
Django settings for schoolconnect project.
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_extensions',
    'drf_spectacular',
    'django_filters',
    'django_celery_results',
    'django_celery_beat',
]

LOCAL_APPS = [
    'apps.authentication',
    'apps.schools',
    'apps.students',
    'apps.parents',
    'apps.notifications',
    'apps.files',
    'apps.common',
    'apps.tasks',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.common.middleware.SchoolTenantMiddleware',
    'apps.common.middleware.APILoggingMiddleware',
]

ROOT_URLCONF = "schoolconnect.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "schoolconnect.wsgi.application"

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='schoolconnect_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FileUploadParser',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Spectacular settings for Swagger documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'SchoolConnect API',
    'DESCRIPTION': '''
    # SchoolConnect API - Gestion des écoles au Niger
    
    ## 🚀 Phase 5 Features (Firebase Integration)
    
    ### 📁 File Management
    - **File Upload**: Upload documents, images, and files
    - **File Storage**: Local storage (free) or Firebase storage (optional)
    - **File Types**: PDF, DOC, DOCX, JPG, PNG, GIF, TXT
    - **File Organization**: School-based folder structure
    
    ### 📱 Notifications
    - **Push Notifications**: Firebase Cloud Messaging (FCM)
    - **Email Notifications**: SMTP-based email delivery
    - **Multi-channel**: Automatic fallback to local/mock services
    - **Bulk Notifications**: Send to multiple users at once
    
    ### 🔧 Storage Options
    - **Local Storage**: Free, immediate use (default)
    - **Firebase Storage**: Cloud-based, scalable (when configured)
    - **Automatic Fallback**: Seamless switching between storage types
    
    ## 📚 Available Endpoints
    
    ### Authentication
    - User registration and login
    - JWT token management
    - Role-based access control
    
    ### Core Management
    - Schools and school configuration
    - Students and academic records
    - Parents and family connections
    - Behavior reports and transcripts
    
    ### Phase 5 Features
    - File upload and management
    - Notification system
    - Real-time updates
    ''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
    'TAGS': [
        {'name': 'authentication', 'description': 'Endpoints d\'authentification - Login, register, token management'},
        {'name': 'schools', 'description': 'Gestion des écoles - CRUD operations for schools and configuration'},
        {'name': 'students', 'description': 'Gestion des étudiants - Student records, transcripts, behavior reports'},
        {'name': 'parents', 'description': 'Gestion des parents - Parent accounts and child connections'},
        {'name': 'notifications', 'description': 'Système de notifications - Push notifications, email, FCM integration'},
        {'name': 'files', 'description': 'Gestion des fichiers - File upload, storage, and management with local/Firebase support'},
        {'name': 'common', 'description': 'Utilitaires communs - Shared endpoints and utilities'},
    ],
    'CONTACT': {
        'name': 'SchoolConnect Support',
        'email': 'support@schoolconnect.ne',
    },
    'LICENSE': {
        'name': 'MIT License',
    },
    'EXTERNAL_DOCS': {
        'description': 'Documentation complète',
        'url': 'https://docs.schoolconnect.ne',
    },
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
        'tryItOutEnabled': True,
    },
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# JWT settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# Custom user model
AUTH_USER_MODEL = 'authentication.User'

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'send-scheduled-notifications': {
        'task': 'apps.notifications.tasks.send_scheduled_notifications',
        'schedule': 300.0,  # Every 5 minutes
    },
    'cleanup-old-files': {
        'task': 'apps.files.tasks.cleanup_old_files',
        'schedule': 86400.0,  # Daily
    },
    'generate-monthly-reports': {
        'task': 'apps.reports.tasks.generate_monthly_reports',
        'schedule': 2592000.0,  # Monthly
    },
}

# Celery Results
CELERY_RESULT_EXPIRES = 3600  # 1 hour
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

# Firebase Configuration (Optional - will fall back to local storage if not configured)
FIREBASE_ENABLED = config('FIREBASE_ENABLED', default=False, cast=bool)
FIREBASE_CREDENTIALS_PATH = config('FIREBASE_CREDENTIALS_PATH', default='')
FIREBASE_STORAGE_BUCKET = config('FIREBASE_STORAGE_BUCKET', default='')
FIREBASE_PROJECT_ID = config('FIREBASE_PROJECT_ID', default='')

# File Upload Settings
ALLOWED_FILE_TYPES = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif']
MAX_FILE_SIZE_MB = 10

# Notification Settings
ENABLE_FCM_NOTIFICATIONS = config('ENABLE_FCM_NOTIFICATIONS', default=True, cast=bool)
ENABLE_EMAIL_NOTIFICATIONS = config('ENABLE_EMAIL_NOTIFICATIONS', default=True, cast=bool)

# Email Configuration (for fallback notifications)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# SMS Configuration (for fallback notifications)
SMS_API_KEY = config('SMS_API_KEY', default='')
SMS_API_URL = config('SMS_API_URL', default='')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'schoolconnect.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'schoolconnect': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
} 