# Phase 1: Project Setup (Week 1 - Days 1-2)

## Overview
Set up the Django project foundation with proper structure, database configuration, and development environment.

## Task 1.1: Initialize Django Project

### Step 1: Create Project Directory and Virtual Environment
```bash
# Create project directory
mkdir edusync_backend
cd edusync_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 2: Create Requirements Files
Create `requirements/` directory with three files:

**requirements/base.txt**
```txt
Django==4.2.7
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.0
django-cors-headers==4.3.1
psycopg2-binary==2.9.9
python-decouple==3.8
Pillow==10.1.0
celery==5.3.4
redis==5.0.1
firebase-admin==6.2.0
requests==2.31.0
django-extensions==3.2.3
```

**requirements/development.txt**
```txt
-r base.txt
django-debug-toolbar==4.2.0
pytest==7.4.3
pytest-django==4.7.0
pytest-cov==4.1.0
factory-boy==3.3.0
black==23.11.0
flake8==6.1.0
isort==5.12.0
pre-commit==3.5.0
```

**requirements/production.txt**
```txt
-r base.txt
gunicorn==21.2.0
whitenoise==6.6.0
sentry-sdk==1.38.0
django-storages==1.14.2
```

### Step 3: Install Base Requirements
```bash
pip install -r requirements/development.txt
```

### Step 4: Create Django Project Structure
```bash
# Create Django project
django-admin startproject edusync .

# Create apps directory
mkdir apps
touch apps/__init__.py

# Create Django apps
cd apps
python ../manage.py startapp authentication
python ../manage.py startapp schools
python ../manage.py startapp students
python ../manage.py startapp parents
python ../manage.py startapp notifications
python ../manage.py startapp files
python ../manage.py startapp common
```

### Step 5: Create Settings Structure
```bash
# Create settings directory
mkdir edusync/settings
touch edusync/settings/__init__.py
```

**edusync/settings/base.py**
```python
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
]

LOCAL_APPS = [
    'apps.authentication',
    'apps.schools',
    'apps.students',
    'apps.parents',
    'apps.notifications',
    'apps.files',
    'apps.common',
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
]

ROOT_URLCONF = 'edusync.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'edusync.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='edusync_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Niamey'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'authentication.User'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
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
    ]
}

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# Celery Configuration
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH = config('FIREBASE_CREDENTIALS_PATH', default='')
FIREBASE_STORAGE_BUCKET = config('FIREBASE_STORAGE_BUCKET', default='')

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
            'filename': BASE_DIR / 'logs' / 'edusync.log',
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
        'edusync': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

**edusync/settings/development.py**
```python
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
```

**edusync/settings/production.py**
```python
from .base import *
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Database
DATABASES['default'] = dj_database_url.parse(config('DATABASE_URL'))

# Static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CORS settings for production
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',')

# Sentry for error tracking
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if config('SENTRY_DSN', default=''):
    sentry_sdk.init(
        dsn=config('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True
    )
```

**edusync/settings/__init__.py**
```python
from decouple import config

if config('ENVIRONMENT', default='development') == 'production':
    from .production import *
else:
    from .development import *
```

## Task 1.2: Configure Development Environment

### Step 1: Create Environment Variables File
Create `.env` file in project root:
```bash
# Django
SECRET_KEY=your-super-secret-key-here
ENVIRONMENT=development
DEBUG=True

# Database
DB_NAME=edusync_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Firebase (leave empty for now, will configure later)
FIREBASE_CREDENTIALS_PATH=
FIREBASE_STORAGE_BUCKET=

# Email (for development)
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# SMS (for development)
SMS_API_KEY=
SMS_API_URL=
```

### Step 2: Update URLs Configuration
**edusync/urls.py**
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/schools/', include('apps.schools.urls')),
    path('api/students/', include('apps.students.urls')),
    path('api/parents/', include('apps.parents.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/files/', include('apps.files.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Add debug toolbar URLs
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
```

### Step 3: Create Basic URL Files for Apps
Create `urls.py` in each app directory:

**apps/authentication/urls.py**
```python
from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Will be implemented in Phase 2
]
```

**apps/schools/urls.py**
```python
from django.urls import path
from . import views

app_name = 'schools'

urlpatterns = [
    # Will be implemented in Phase 4
]
```

**apps/students/urls.py**
```python
from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Will be implemented in Phase 4
]
```

**apps/parents/urls.py**
```python
from django.urls import path
from . import views

app_name = 'parents'

urlpatterns = [
    # Will be implemented in Phase 4
]
```

**apps/notifications/urls.py**
```python
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Will be implemented in Phase 6
]
```

**apps/files/urls.py**
```python
from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    # Will be implemented in Phase 5
]
```

### Step 4: Create Docker Configuration
**Dockerfile**
```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/production.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create logs directory
RUN mkdir -p /app/logs

# Collect static files
RUN python manage.py collectstatic --noinput

# Run server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "edusync.wsgi:application"]
```

**railway.json**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:$PORT edusync.wsgi:application",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Step 5: Set Up Git Repository
Create `.gitignore`:
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Django
*.log
local_settings.py
db.sqlite3
media/
staticfiles/

# Environment variables
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Firebase
firebase-credentials.json
*.pem
```

Initialize git:
```bash
git init
git add .
git commit -m "Initial Django project setup"
```

### Step 6: Set Up Pre-commit Hooks
Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]
```

Install pre-commit:
```bash
pre-commit install
```

### Step 7: Create Directory Structure
```bash
# Create additional directories
mkdir logs
mkdir media
mkdir staticfiles
mkdir templates

# Create empty __init__.py files where needed
touch logs/.gitkeep
touch media/.gitkeep
touch templates/.gitkeep
```

## Testing Phase 1 Completion

### Verification Steps:
1. **Virtual Environment**: Activate and verify packages installed
```bash
pip list | grep Django
```

2. **Database Connection**: Test database connection
```bash
python manage.py check --database default
```

3. **Run Development Server**: Start server without errors
```bash
python manage.py runserver
```

4. **Git Status**: Verify all files are tracked
```bash
git status
```

5. **Pre-commit**: Test pre-commit hooks
```bash
pre-commit run --all-files
```

## Success Criteria:
- [ ] Django project runs without errors
- [ ] All apps are created and registered
- [ ] Database connection is configured
- [ ] Environment variables are properly loaded
- [ ] Git repository is initialized with proper .gitignore
- [ ] Pre-commit hooks are working
- [ ] Docker configuration is ready
- [ ] Railway deployment configuration is set

## Common Issues and Solutions:

### Issue 1: PostgreSQL Connection Error
**Problem**: `django.db.utils.OperationalError: could not connect to server`
**Solution**: 
- Install PostgreSQL locally or use Railway's development database
- Update DATABASE_URL in .env file

### Issue 2: Module Import Errors
**Problem**: `ModuleNotFoundError: No module named 'apps.authentication'`
**Solution**:
- Ensure `apps/__init__.py` exists
- Check that all app directories have `__init__.py` files

### Issue 3: Secret Key Warning
**Problem**: Django complains about insecure secret key
**Solution**:
- Generate a new secret key: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- Update SECRET_KEY in .env file

## Next Steps:
Once Phase 1 is complete and verified, we'll move to **Phase 2: Authentication System** where we'll:
- Create custom User model
- Implement JWT authentication
- Set up role-based access control
- Create user registration/login endpoints

Ready to proceed to Phase 1 implementation, or do you have any questions about the setup?