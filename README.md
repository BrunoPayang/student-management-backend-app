# SchoolConnect Backend

A Django REST API backend for school management system with multi-tenant architecture, JWT authentication, and Firebase integration.

## Features

- **Multi-tenant Architecture**: Support for multiple schools with data isolation
- **JWT Authentication**: Secure token-based authentication
- **Firebase Integration**: File storage and push notifications
- **REST API**: Comprehensive API endpoints for all operations
- **Background Tasks**: Celery integration for async operations
- **Production Ready**: Optimized for deployment on Railway

## Tech Stack

- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL (multi-tenant aware)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **File Storage**: Firebase Storage
- **Notifications**: Firebase Cloud Messaging
- **Background Tasks**: Celery with Redis
- **Hosting**: Railway

## Project Structure

```
schoolconnect_backend/
├── schoolconnect/              # Main project directory
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   └── urls.py
├── apps/
│   ├── authentication/         # JWT auth & user management
│   ├── schools/               # School model & management
│   ├── students/              # Student CRUD operations
│   ├── parents/               # Parent/Guardian management
│   ├── notifications/         # FCM integration
│   ├── files/                 # File upload/download
│   └── common/                # Shared utilities
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── manage.py
├── Dockerfile
├── railway.json
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis
- Firebase project

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd schoolconnect_backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/development.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Environment Variables

Create a `.env` file with the following variables:

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# Firebase
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json
FIREBASE_STORAGE_BUCKET=your-bucket.appspot.com

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
```

## API Documentation

The API documentation is available at `/api/docs/` when running the development server.

### Key Endpoints

- **Authentication**: `/api/auth/`
- **Schools**: `/api/schools/`
- **Students**: `/api/students/`
- **Parents**: `/api/parents/`
- **Files**: `/api/files/`
- **Notifications**: `/api/notifications/`

## Development

### Running Tests
```bash
python manage.py test
```

### Code Formatting
```bash
black .
isort .
```

### Linting
```bash
flake8 .
```

## Deployment

### Railway Deployment

1. Connect your repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to main branch

### Manual Deployment

1. **Build Docker image**
   ```bash
   docker build -t schoolconnect .
   ```

2. **Run container**
   ```bash
   docker run -p 8000:8000 schoolconnect
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, email support@schoolconnect.com or create an issue in the repository. 