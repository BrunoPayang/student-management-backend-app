# EduSync Niger - Backend Django REST API Implementation Guide

## Project Overview
Django REST Framework backend with multi-tenant architecture, JWT authentication, and Firebase integration for notifications and file storage.

## Tech Stack
- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL (multi-tenant aware)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **File Storage**: Firebase Storage
- **Notifications**: Firebase Cloud Messaging
- **Hosting**: Railway
- **Additional**: Celery for background tasks, Redis for caching

## Project Structure
```
edusync_backend/
├── edusync/                    # Main project directory
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

## Database Schema Design

### Core Models

#### 1. School Model
```python
class School(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)  # For URL routing
    logo = models.URLField(blank=True)    # Firebase Storage URL
    primary_color = models.CharField(max_length=7)  # Hex color
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 2. User Model (Extended)
```python
class User(AbstractUser):
    USER_TYPES = [
        ('admin', 'System Admin'),
        ('school_staff', 'School Staff'),
        ('parent', 'Parent/Guardian'),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    phone = models.CharField(max_length=20, blank=True)
    fcm_token = models.TextField(blank=True)  # For push notifications
```

#### 3. Student Model
```python
class Student(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=50)  # School-specific ID
    class_level = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    enrollment_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school', 'student_id']
```

#### 4. Parent-Student Relationship
```python
class ParentStudent(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    relationship = models.CharField(max_length=50)  # Father, Mother, Guardian
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['parent', 'student']
```

#### 5. Academic Records
```python
class Transcript(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=20)
    file_url = models.URLField()  # Firebase Storage URL
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class BehaviorReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=50)  # Positive, Negative, Neutral
    description = models.TextField()
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class PaymentRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=50)  # Tuition, Fees, etc.
    status = models.CharField(max_length=20)  # Paid, Pending, Overdue
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## API Endpoints Structure

### Authentication Endpoints
- `POST /api/auth/login/` - JWT login
- `POST /api/auth/refresh/` - Token refresh
- `POST /api/auth/register/` - User registration (school-specific)

### School Management (Admin only)
- `GET /api/schools/` - List all schools
- `POST /api/schools/` - Create new school
- `GET /api/schools/{id}/` - School details
- `PUT /api/schools/{id}/` - Update school
- `DELETE /api/schools/{id}/` - Deactivate school

### Student Management (School Staff)
- `GET /api/students/` - List school students
- `POST /api/students/` - Create student
- `GET /api/students/{id}/` - Student details
- `PUT /api/students/{id}/` - Update student
- `DELETE /api/students/{id}/` - Deactivate student

### Parent Endpoints
- `GET /api/parents/students/` - List parent's children
- `GET /api/parents/students/{id}/transcripts/` - Student transcripts
- `GET /api/parents/students/{id}/behavior/` - Behavior reports
- `GET /api/parents/students/{id}/payments/` - Payment status

### File Management
- `POST /api/files/upload/` - Upload files to Firebase
- `GET /api/files/{id}/download/` - Download file (authenticated)

### Notifications
- `POST /api/notifications/send/` - Send notification
- `GET /api/notifications/` - List user notifications

## Implementation Tasks Breakdown

### Phase 1: Project Setup (Week 1 - Days 1-2)
**Task 1.1: Initialize Django Project**
- [ ] Create Django project with proper structure
- [ ] Set up virtual environment and requirements files
- [ ] Configure Django settings (base, dev, prod)
- [ ] Set up PostgreSQL database connection
- [ ] Initialize Git repository

**Task 1.2: Configure Development Environment**
- [ ] Set up Django REST Framework
- [ ] Configure CORS settings
- [ ] Set up environment variables management
- [ ] Create base Docker configuration
- [ ] Set up pre-commit hooks and code formatting

### Phase 2: Authentication System (Week 1 - Days 3-4)
**Task 2.1: User Model & JWT Setup**
- [ ] Extend Django User model
- [ ] Install and configure djangorestframework-simplejwt
- [ ] Create custom authentication backends
- [ ] Implement JWT token generation/validation
- [ ] Create user registration/login views

**Task 2.2: Role-Based Access Control**
- [ ] Implement custom permissions classes
- [ ] Create decorators for role-based access
- [ ] Set up middleware for tenant isolation
- [ ] Create user profile management endpoints

### Phase 3: Core Models & Database (Week 1 - Days 5-7)
**Task 3.1: School Management Models**
- [ ] Create School model with branding fields
- [ ] Implement school slug generation
- [ ] Create school configuration model
- [ ] Set up model managers for multi-tenancy

**Task 3.2: Student & Relationship Models**
- [ ] Create Student model with school foreign key
- [ ] Implement ParentStudent relationship model
- [ ] Create academic record models (Transcript, Behavior, Payment)
- [ ] Set up model serializers for API responses

**Task 3.3: Database Migrations & Seeding**
- [ ] Create and run all database migrations
- [ ] Create management commands for data seeding
- [ ] Set up database indexes for performance
- [ ] Create sample data for testing

### Phase 4: Core API Endpoints (Week 2 - Days 1-3)
**Task 4.1: School Management APIs**
- [ ] Create school CRUD viewsets
- [ ] Implement school configuration endpoints
- [ ] Add school branding upload functionality
- [ ] Create school analytics endpoints

**Task 4.2: Student Management APIs**
- [ ] Create student CRUD viewsets with school filtering
- [ ] Implement bulk student import functionality
- [ ] Create student search and filtering
- [ ] Add student academic record endpoints

**Task 4.3: Parent/Guardian APIs**
- [ ] Create parent dashboard endpoints
- [ ] Implement multi-student viewing
- [ ] Create notification preference management
- [ ] Add parent-student linking functionality

### Phase 5: Firebase Integration (Week 2 - Days 4-5)
**Task 5.1: Firebase Storage Setup**
- [ ] Configure Firebase SDK for Python
- [ ] Create file upload service
- [ ] Implement secure file download with authentication
- [ ] Set up file type validation and size limits

**Task 5.2: Firebase Cloud Messaging**
- [ ] Set up FCM for push notifications
- [ ] Create notification sending service
- [ ] Implement notification templates
- [ ] Add FCM token management for users

### Phase 6: Background Tasks & Notifications (Week 2 - Days 6-7)
**Task 6.1: Celery Setup**
- [ ] Install and configure Celery with Redis
- [ ] Create background task for sending notifications
- [ ] Implement email/SMS fallback system
- [ ] Set up periodic tasks for payment reminders

**Task 6.2: Notification System**
- [ ] Create notification triggering system
- [ ] Implement notification history tracking
- [ ] Add notification preferences management
- [ ] Create notification analytics

### Phase 7: Testing & Documentation (Week 3 - Days 1-3)
**Task 7.1: Unit & Integration Tests**
- [ ] Write model tests for all models
- [ ] Create API endpoint tests
- [ ] Implement authentication flow tests
- [ ] Add file upload/download tests

**Task 7.2: API Documentation**
- [ ] Set up Django REST Framework browsable API
- [ ] Create comprehensive API documentation
- [ ] Add Postman collection for testing
- [ ] Create deployment documentation

### Phase 8: Deployment Preparation (Week 3 - Days 4-5)
**Task 8.1: Production Configuration**
- [ ] Configure production settings
- [ ] Set up Railway deployment configuration
- [ ] Configure production database
- [ ] Set up environment variables for production

**Task 8.2: Security & Performance**
- [ ] Implement rate limiting
- [ ] Add security headers and HTTPS enforcement
- [ ] Set up database connection pooling
- [ ] Configure static file serving

## Environment Variables Required
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# Firebase
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json
FIREBASE_STORAGE_BUCKET=your-bucket.appspot.com

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_EXPIRATION_DELTA=3600

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0

# Email (fallback notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password

# SMS (fallback notifications)
SMS_API_KEY=your-sms-api-key
SMS_API_URL=https://api.sms-provider.com
```

## Success Criteria for Backend Validation
1. **Authentication**: JWT login/logout working for all user types
2. **Multi-tenancy**: Data properly isolated by school
3. **CRUD Operations**: All models can be created, read, updated, deleted
4. **File Upload**: Transcripts can be uploaded to Firebase Storage
5. **Notifications**: FCM notifications sent when student data updates
6. **API Documentation**: Complete and testable API documentation
7. **Performance**: API responses under 500ms for typical requests
8. **Security**: Proper authorization checks on all endpoints

## Next Steps After Backend Completion
Once backend is validated, we'll move to:
1. React Web Admin Portal (for school staff)
2. Flutter Mobile App (white-label parent interface)

Would you like me to elaborate on any specific task or shall we start with Phase 1 implementation?