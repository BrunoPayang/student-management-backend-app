# API Documentation - Student Management System

## Overview
The Student Management System provides a comprehensive REST API for managing schools, students, parents, notifications, and related educational data. This API is built using Django REST Framework and follows RESTful conventions.

## Base URL
```
http://localhost:8000/api/
```

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
GET /schools/
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
POST /schools/
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
GET /schools/{id}/
```

### Update School (Admin only)
```http
PATCH /schools/{id}/
```

### Delete School (Admin only)
```http
DELETE /schools/{id}/
```

## Students API

### List Students
```http
GET /students/
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
POST /students/
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

### Student Transcripts
```http
GET /students/transcripts/
POST /students/transcripts/
GET /students/transcripts/{id}/
PATCH /students/transcripts/{id}/
```

### Behavior Reports
```http
GET /students/behavior-reports/
POST /students/behavior-reports/
GET /students/behavior-reports/{id}/
PATCH /students/behavior-reports/{id}/
```

## Notifications API

### List Notifications
```http
GET /notifications/
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
POST /notifications/
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

### Notification Delivery Tracking
```http
GET /notifications/deliveries/
GET /notifications/deliveries/{id}/
```

### Bulk Send Notifications
```http
POST /notifications/send-bulk/
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
GET /parents/dashboard/my-children/
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
GET /parents/dashboard/profile/
PATCH /parents/dashboard/profile/
```

### Notification Preferences
```http
PUT /parents/dashboard/notification-preferences/
PATCH /parents/dashboard/notification-preferences/
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
GET /parents/dashboard/unread-notifications-count/
```
**Response:**
```json
{
    "count": 5
}
```

### Test Notification
```http
POST /parents/dashboard/test-notification/
```

## Files API

### List Files
```http
GET /files/
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
POST /files/
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
PATCH /files/{id}/
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
DELETE /files/{id}/
```

## Tasks API (Admin/Staff only)

### List Background Tasks
```http
GET /tasks/
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
GET /tasks/{task_id}/
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

## Support and Documentation
- **Swagger UI**: Available at `/api/schema/swagger-ui/`
- **ReDoc**: Available at `/api/schema/redoc/`
- **OpenAPI Schema**: Available at `/api/schema/`

For technical support, contact: api-support@studentmanagement.com 