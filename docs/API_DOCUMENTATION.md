# API Documentation - Student Management System

## Overview
The Student Management System provides a comprehensive REST API for managing schools, students, parents, notifications, and related educational data. This API is built using Django REST Framework and follows RESTful conventions.

## Quick Reference - All Available Endpoints

| Category | Endpoint | Methods | Description |
|----------|----------|---------|-------------|
| **Authentication** | `/api/auth/login/` | POST | User login |
| | `/api/auth/register/` | POST | User registration |
| | `/api/auth/refresh/` | POST | Refresh JWT token |
| | `/api/auth/logout/` | POST | User logout |
| | `/api/auth/profile/` | GET, PATCH | User profile management |
| | `/api/auth/change-password/` | POST | Change password |
| | `/api/auth/password-reset/` | POST | Request password reset |
| | `/api/auth/password-reset-confirm/` | POST | Confirm password reset |
| | `/api/auth/current-user/` | GET | Get current user info |
| | `/api/auth/user-context/` | GET | Get user context |
| | `/api/auth/fcm-token/` | POST | Update FCM token |
| **Schools** | `/api/schools/` | GET, POST | List/create schools |
| | `/api/schools/{id}/` | GET, PATCH, DELETE | School details |
| | `/api/schools/{id}/statistics/` | GET | School statistics |
| | `/api/schools/{id}/configuration/` | GET, PUT, PATCH | School configuration |
| | `/api/schools/{id}/activate/` | POST | Activate school |
| | `/api/schools/{id}/deactivate/` | POST | Deactivate school |
| **Students** | `/api/students/` | GET, POST | List/create students |
| | `/api/students/{id}/` | GET, PATCH, DELETE | Student details |
| | `/api/students/{id}/academic_records/` | GET | Student transcripts |
| | `/api/students/{id}/behavior_reports/` | GET | Student behavior reports |
| | `/api/students/{id}/payment_records/` | GET | Student payments |
| | `/api/students/{id}/statistics/` | GET | Student statistics |
| **Transcripts** | `/api/transcripts/` | GET, POST | List/create transcripts |
| | `/api/transcripts/{id}/` | GET, PATCH, DELETE | Transcript details |
| **Behavior Reports** | `/api/behavior-reports/` | GET, POST | List/create behavior reports |
| | `/api/behavior-reports/{id}/` | GET, PATCH, DELETE | Behavior report details |
| **Payment Records** | `/api/payment-records/` | GET, POST | List/create payment records |
| | `/api/payment-records/{id}/` | GET, PATCH, DELETE | Payment record details |
| | `/api/payment-records/overdue_payments/` | GET | Get overdue payments |
| | `/api/payment-records/payment_summary/` | GET | Payment statistics |
| **Parent Dashboard** | `/api/parent-dashboard/my_children/` | GET | List parent's children |
| | `/api/parent-dashboard/{id}/child_details/` | GET | Child details |
| | `/api/parent-dashboard/{id}/child_transcripts/` | GET | Child transcripts |
| | `/api/parent-dashboard/{id}/child_behavior/` | GET | Child behavior reports |
| | `/api/parent-dashboard/{id}/child_payments/` | GET | Child payments |
| | `/api/parent-dashboard/{id}/child_statistics/` | GET | Child statistics |
| | `/api/parent-dashboard/notifications/` | GET | Parent notifications |
| | `/api/parent-dashboard/notification_preferences/` | GET, PUT, PATCH | Notification preferences |
| | `/api/parent-dashboard/{id}/mark_notification_read/` | POST | Mark notification read |
| | `/api/parent-dashboard/unread_notifications_count/` | GET | Unread count |
| | `/api/parent-dashboard/test_notification/` | POST | Test notification |
| | `/api/parent-dashboard/profile/` | GET, PATCH | Parent profile |
| **Parent-Student Relations** | `/api/parent-students/` | GET, POST | List/create relationships |
| | `/api/parent-students/{id}/` | GET, PATCH, DELETE | Relationship details |
| **Notifications** | `/api/notifications/` | GET, POST | List/create notifications |
| | `/api/notifications/{id}/` | GET, PATCH, DELETE | Notification details |
| **Notification Deliveries** | `/api/notification-deliveries/` | GET, POST | List/create deliveries |
| | `/api/notification-deliveries/{id}/` | GET, PATCH, DELETE | Delivery details |
| **Files** | `/api/files/` | GET, POST | List/upload files |
| | `/api/files/{id}/` | GET, PATCH, DELETE | File details |
| **Tasks** | `/api/task-results/` | GET | List background tasks |
| | `/api/task-results/{id}/` | GET | Task details |

## Base URL
```
http://localhost:8000/api/
```

**Note**: Most endpoints are prefixed with `/api/` except authentication which uses `/api/auth/`

## Authentication
The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### Authentication Endpoints

#### Register User
```http
POST /auth/register/
```
**Request Body:**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123",
    "user_type": "parent",
    "first_name": "John",
    "last_name": "Doe"
}
```

#### Login
```http
POST /auth/login/
```
**Request Body:**
```json
{
    "username": "john_doe",
    "password": "SecurePass123"
}
```
**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "user_type": "parent"
    }
}
```

#### Refresh Token
```http
POST /auth/token/refresh/
```
**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## User Roles
- **Admin**: Full system access, can manage all schools
- **School Staff**: Access to their assigned school's data
- **Parent**: Access to their children's information and school notifications

## Schools API

### List Schools
```http
GET /api/schools/
```
**Response:**
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/schools/?page=2",
    "previous": null,
    "results": [
        {
            "id": "uuid-here",
            "name": "Springfield Elementary",
            "address": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62701",
            "phone": "555-1234",
            "email": "contact@springfield.edu",
            "website": "https://springfield.edu",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

### Create School (Admin only)
```http
POST /api/schools/
```
**Request Body:**
```json
{
    "name": "New School",
    "address": "456 Oak Ave",
    "city": "Shelbyville",
    "state": "IL",
    "zip_code": "62565",
    "phone": "555-5678",
    "email": "info@newschool.edu",
    "website": "https://newschool.edu"
}
```

### Get School Details
```http
GET /api/schools/{id}/
```

### School Custom Actions
```http
GET /api/schools/{id}/statistics/
GET /api/schools/{id}/configuration/
PUT /api/schools/{id}/configuration/
PATCH /api/schools/{id}/configuration/
POST /api/schools/{id}/activate/
POST /api/schools/{id}/deactivate/
```

### Update School (Admin only)
```http
PATCH /api/schools/{id}/
```

### Delete School (Admin only)
```http
DELETE /api/schools/{id}/
```

## Students API

### List Students
```http
GET /api/students/
```
**Query Parameters:**
- `search`: Search by name or student ID
- `class_level`: Filter by class level
- `school`: Filter by school ID
- `is_active`: Filter by active status

**Response:**
```json
{
    "count": 150,
    "results": [
        {
            "id": "uuid-here",
            "first_name": "Alice",
            "last_name": "Johnson",
            "student_id": "ST001",
            "school": "school-uuid",
            "school_name": "Springfield Elementary",
            "class_level": "5th",
            "section": "A",
            "gender": "female",
            "is_active": true,
            "enrollment_date": "2024-09-01",
            "primary_parent": null
        }
    ]
}
```

### Create Student (Admin/Staff only)
```http
POST /api/students/
```
**Request Body:**
```json
{
    "first_name": "Bob",
    "last_name": "Smith",
    "school": "school-uuid",
    "class_level": "6th",
    "section": "B",
    "gender": "male",
    "enrollment_date": "2024-09-01"
}
```

### Student Custom Actions
```http
GET /api/students/{id}/academic_records/
GET /api/students/{id}/behavior_reports/
GET /api/students/{id}/payment_records/
GET /api/students/{id}/statistics/
```

### Student Transcripts
```http
GET /api/transcripts/
POST /api/transcripts/
GET /api/transcripts/{id}/
PATCH /api/transcripts/{id}/
DELETE /api/transcripts/{id}/
```

### Behavior Reports
```http
GET /api/behavior-reports/
POST /api/behavior-reports/
GET /api/behavior-reports/{id}/
PATCH /api/behavior-reports/{id}/
DELETE /api/behavior-reports/{id}/
```

### Payment Records
```http
GET /api/payment-records/
POST /api/payment-records/
GET /api/payment-records/{id}/
PATCH /api/payment-records/{id}/
DELETE /api/payment-records/{id}/
GET /api/payment-records/overdue_payments/
GET /api/payment-records/payment_summary/
```

## Notifications API

### List Notifications
```http
GET /api/notifications/
```
**Query Parameters:**
- `search`: Search in title and body
- `notification_type`: Filter by type (general, academic, behavior, payment)
- `school`: Filter by school ID

**Response:**
```json
{
    "count": 50,
    "results": [
        {
            "id": "uuid-here",
            "title": "Parent-Teacher Conference",
            "body": "Please schedule your conference by Friday",
            "notification_type": "academic",
            "school": "school-uuid",
            "school_name": "Springfield Elementary",
            "data": {
                "deadline": "2024-03-15",
                "priority": "high"
            },
            "created_at": "2024-03-01T10:00:00Z",
            "target_users_count": 25
        }
    ]
}
```

### Create Notification (Admin/Staff only)
```http
POST /api/notifications/
```
**Request Body:**
```json
{
    "title": "School Closure Notice",
    "body": "School will be closed tomorrow due to weather",
    "notification_type": "general",
    "school": "school-uuid",
    "data": {
        "closure_date": "2024-03-02",
        "reason": "weather"
    }
}
```

### Update Notification (Admin/Staff only)
```http
PATCH /api/notifications/{id}/
```

### Delete Notification (Admin/Staff only)  
```http
DELETE /api/notifications/{id}/
```

### Notification Delivery Tracking
```http
GET /api/notification-deliveries/
GET /api/notification-deliveries/{id}/
POST /api/notification-deliveries/
PATCH /api/notification-deliveries/{id}/
DELETE /api/notification-deliveries/{id}/
```
**Request Body:**
```json
{
    "notification_ids": ["uuid1", "uuid2"],
    "target_user_types": ["parent", "school_staff"]
}
```

## Parents API

### Parent Dashboard
```http
GET /api/parent-dashboard/my_children/
GET /api/parent-dashboard/{student_id}/child_details/
GET /api/parent-dashboard/{student_id}/child_transcripts/
GET /api/parent-dashboard/{student_id}/child_behavior/
GET /api/parent-dashboard/{student_id}/child_payments/
GET /api/parent-dashboard/{student_id}/child_statistics/
GET /api/parent-dashboard/notifications/
POST /api/parent-dashboard/{notification_id}/mark_notification_read/
GET /api/parent-dashboard/unread_notifications_count/
POST /api/parent-dashboard/test_notification/
```
**Response:**
```json
{
    "count": 2,
    "results": [
        {
            "id": "student-uuid",
            "first_name": "Emma",
            "last_name": "Wilson",
            "student_id": "ST045",
            "class_level": "3rd",
            "section": "A",
            "school_name": "Springfield Elementary"
        }
    ]
}
```

### Parent Profile
```http
GET /api/parent-dashboard/profile/
PATCH /api/parent-dashboard/profile/
```

### Notification Preferences
```http
GET /api/parent-dashboard/notification_preferences/
PUT /api/parent-dashboard/notification_preferences/
PATCH /api/parent-dashboard/notification_preferences/
```

### Parent-Student Relationships
```http
GET /api/parent-students/
POST /api/parent-students/
GET /api/parent-students/{id}/
PATCH /api/parent-students/{id}/
DELETE /api/parent-students/{id}/
```
**Request Body:**
```json
{
    "email_notifications": true,
    "sms_notifications": false,
    "push_notifications": true
}
```

### Unread Notifications Count
```http
GET /api/parent-dashboard/unread_notifications_count/
```
**Response:**
```json
{
    "unread_count": 5
}
```

### Test Notification
```http
POST /api/parent-dashboard/test_notification/
```

## Files API

### List Files
```http
GET /api/files/
```
**Query Parameters:**
- `search`: Search in filename, description, or tags
- `file_type`: Filter by file type
- `is_public`: Filter by public status

**Response:**
```json
{
    "count": 75,
    "results": [
        {
            "id": "uuid-here",
            "original_name": "transcript_2024.pdf",
            "firebase_url": "https://storage.example.com/file.pdf",
            "file_size_mb": 2.5,
            "content_type": "application/pdf",
            "file_type": "transcript",
            "description": "Student academic transcript",
            "tags": "academic, transcript, 2024",
            "is_public": false,
            "uploaded_by": 1,
            "uploaded_by_name": "Jane Smith",
            "school_name": "Springfield Elementary",
            "uploaded_at": "2024-03-01T09:00:00Z"
        }
    ]
}
```

### Upload File (Staff/Admin only)
```http
POST /api/files/
Content-Type: multipart/form-data
```
**Form Data:**
- `file`: File to upload
- `file_type`: One of: transcript, behavior_report, payment_receipt, student_document, other
- `description`: File description (optional)
- `tags`: Comma-separated tags (optional)
- `is_public`: Boolean (default: false)

### Update File Metadata (Staff/Admin only)
```http
PATCH /api/files/{id}/
Content-Type: application/json
```
**Request Body:**
```json
{
    "description": "Updated description",
    "tags": "updated, tags",
    "is_public": true
}
```

### Delete File (Staff/Admin only)
```http
DELETE /api/files/{id}/
```

## Tasks API (Admin/Staff only)

### List Background Tasks
```http
GET /api/task-results/
```
**Query Parameters:**
- `status`: Filter by task status (SUCCESS, PENDING, FAILURE)
- `task_name`: Filter by task name
- `date_done__gte`: Filter by completion date

**Response:**
```json
{
    "count": 100,
    "results": [
        {
            "task_id": "celery-task-uuid",
            "task_name": "send_notification",
            "status": "SUCCESS",
            "result": "Notification sent successfully",
            "traceback": null,
            "date_created": "2024-03-01T10:00:00Z",
            "date_done": "2024-03-01T10:00:05Z",
            "worker": "worker-1"
        }
    ]
}
```

### Get Task Details
```http
GET /api/task-results/{task_id}/
```

## Error Responses

### Standard Error Format
```json
{
    "detail": "Error message here"
}
```

### Validation Errors
```json
{
    "field_name": ["This field is required."],
    "another_field": ["Invalid value."]
}
```

### Common HTTP Status Codes
- `200 OK`: Successful GET/PATCH requests
- `201 Created`: Successful POST requests
- `204 No Content`: Successful DELETE requests
- `400 Bad Request`: Validation errors
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server errors

## Rate Limiting
API requests are subject to rate limiting:
- **Authenticated users**: 1000 requests per hour
- **Unauthenticated users**: 100 requests per hour

## Pagination
List endpoints support pagination with the following parameters:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10, max: 100)

Example paginated response:
```json
{
    "count": 1000,
    "next": "http://localhost:8000/api/students/?page=2",
    "previous": null,
    "results": [...]
}
```

## Search and Filtering
Most list endpoints support:
- **Search**: Use the `search` parameter for text-based searching
- **Filtering**: Use field names as query parameters
- **Ordering**: Use the `ordering` parameter (e.g., `ordering=-created_at`)

Example:
```http
GET /students/?search=alice&class_level=5th&ordering=-enrollment_date
```

## WebSocket Integration (Future)
Real-time notifications will be available via WebSocket connections:
```javascript
const socket = new WebSocket('ws://localhost:8000/ws/notifications/');
```

## SDK and Libraries
- **Python SDK**: Available for server-side integrations
- **JavaScript SDK**: For web applications
- **Mobile SDKs**: iOS and Android libraries planned

## Additional Authentication Endpoints

### Change Password
```http
POST /api/auth/change-password/
```
**Request Body:**
```json
{
    "old_password": "current_password",
    "new_password": "new_secure_password"
}
```

### Password Reset
```http
POST /api/auth/password-reset/
```
**Request Body:**
```json
{
    "email": "user@example.com"
}
```

### Password Reset Confirm
```http
POST /api/auth/password-reset-confirm/
```
**Request Body:**
```json
{
    "token": "reset_token",
    "new_password": "new_secure_password"
}
```

### Current User Info
```http
GET /api/auth/current-user/
```

### User Context
```http
GET /api/auth/user-context/
```

### Update FCM Token
```http
POST /api/auth/fcm-token/
```
**Request Body:**
```json
{
    "fcm_token": "firebase_cloud_messaging_token"
}
```

## Payment Records API

### Payment Summary Statistics
```http
GET /api/payment-records/payment_summary/
```
**Response:**
```json
{
    "total_payments": 150,
    "total_amount": 7500000.00,
    "paid_amount": 5000000.00,
    "pending_amount": 2000000.00,
    "overdue_amount": 500000.00,
    "payment_types": [
        {
            "payment_type": "tuition",
            "count": 100,
            "total_amount": 5000000.00
        }
    ]
}
```

### Overdue Payments
```http
GET /api/payment-records/overdue_payments/
```
**Response:**
```json
[
    {
        "id": "payment-uuid",
        "student_name": "John Doe",
        "amount": "50000.00",
        "currency": "NGN",
        "payment_type": "tuition",
        "status": "pending",
        "due_date": "2024-01-15",
        "days_overdue": 10
    }
]
```

## Support and Documentation
- **Swagger UI**: Available at `/api/docs/`
- **ReDoc**: Available at `/api/redoc/`
- **OpenAPI Schema**: Available at `/api/schema/`
- **API Root**: Available at `/api/` (lists all available endpoints)

For technical support, contact: api-support@studentmanagement.com 