# Parent Management Module - School Staff API Documentation

**Version:** 1.0  
**Last Updated:** January 2024  
**For:** School Staff Dashboard Development

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Parent Directory Management](#parent-directory-management)
4. [Parent-Student Relationship Management](#parent-student-relationship-management)
5. [Parent Communication & Notifications](#parent-communication--notifications)
6. [Data Models](#data-models)
7. [Error Handling](#error-handling)

---

## 🏗️ Overview

This document provides API documentation for **School Staff** to manage parents through the administrative dashboard. These endpoints allow staff to:

- Manage parent directory and profiles
- Create and manage parent-student relationships
- Send communications and notifications to parents
- Track notification delivery and engagement

**Base URL:** `https://your-domain.com/api/`  
**Authentication:** JWT Bearer Token required (Staff/Admin only)  
**Content-Type:** `application/json` for all requests

### Key Features
- ✅ Parent directory with contact management
- ✅ Parent-student relationship linking
- ✅ Bulk parent operations
- ✅ Multi-channel communication system (FCM, Email, SMS)
- ✅ Targeted notification system
- ✅ Emergency alert capabilities
- ✅ Communication analytics and tracking

---

## 🔐 Authentication

All parent management endpoints require JWT authentication with staff/admin permissions:

```http
Authorization: Bearer your_jwt_token_here
```

**Required Permissions:**
- **School Staff**: Access to parents in their school only
- **System Admin**: Full access to all parent management features

---

## 📂 Parent Directory Management

### **1. List All Parents**
```http
GET /api/auth/users/?user_type=parent
```

**Query Parameters:**
- `school` (UUID): Filter by school ID
- `search` (string): Search by name, email, or phone
- `page` (int): Page number for pagination
- `page_size` (int): Items per page (default: 20)

**Response:**
```json
{
    "count": 150,
    "next": "/api/auth/users/?user_type=parent&page=2",
    "previous": null,
    "results": [
        {
            "id": 15,
            "username": "john_smith",
            "email": "john.smith@email.com",
            "first_name": "John",
            "last_name": "Smith",
            "phone": "+1234567890",
            "user_type": "parent",
            "school": "550e8400-e29b-41d4-a716-446655440000",
            "is_active": true,
            "fcm_token": "fcm_token_string",
            "created_at": "2024-01-15T10:00:00Z",
            "last_login": "2024-03-01T08:30:00Z"
        }
    ]
}
```

### **2. Create New Parent**
```http
POST /api/auth/register/
Content-Type: application/json
```

**Request Body:**
```json
{
    "username": "jane_doe",
    "email": "jane.doe@email.com",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123",
    "user_type": "parent",
    "first_name": "Jane",
    "last_name": "Doe",
    "phone": "+1987654321",
    "school": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
    "id": 25,
    "username": "jane_doe",
    "email": "jane.doe@email.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "user_type": "parent",
    "school": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2024-03-01T10:00:00Z"
}
```

### **3. Get Parent Details**
```http
GET /api/auth/users/{parent_id}/
```

**Response:**
```json
{
    "id": 15,
    "username": "john_smith",
    "email": "john.smith@email.com",
    "first_name": "John",
    "last_name": "Smith",
    "phone": "+1234567890",
    "user_type": "parent",
    "school": "550e8400-e29b-41d4-a716-446655440000",
    "is_active": true,
    "fcm_token": "fcm_token_string",
    "created_at": "2024-01-15T10:00:00Z",
    "last_login": "2024-03-01T08:30:00Z",
    "children_count": 2,
    "notification_preferences": {
        "sms_notifications": true,
        "email_notifications": true,
        "push_notifications": true
    }
}
```

### **4. Update Parent Information**
```http
PATCH /api/auth/users/{parent_id}/
Content-Type: application/json
```

**Request Body:**
```json
{
    "phone": "+1555123456",
    "email": "newemail@example.com",
    "is_active": true
}
```

### **5. Deactivate Parent Account**
```http
PATCH /api/auth/users/{parent_id}/
Content-Type: application/json
```

**Request Body:**
```json
{
    "is_active": false
}
```

---

## 👨‍👩‍👧‍👦 Parent-Student Relationship Management

### **1. List Parent-Student Relationships**
```http
GET /api/parent-students/
```

**Query Parameters:**
- `parent` (int): Filter by parent ID
- `student` (UUID): Filter by student ID
- `school` (UUID): Filter by school ID
- `relationship` (string): Filter by relationship type
- `is_primary` (boolean): Filter primary contacts
- `is_emergency_contact` (boolean): Filter emergency contacts

**Response:**
```json
{
    "count": 75,
    "next": "/api/parent-students/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "parent": 15,
            "parent_name": "John Smith",
            "student": "ce695f13-acef-4dac-8c21-b83a2c37d204",
            "student_name": "Emma Smith",
            "relationship": "father",
            "is_primary": true,
            "is_emergency_contact": true,
            "receive_sms": true,
            "receive_email": true,
            "receive_push": true,
            "created_at": "2024-01-15T10:00:00Z"
        }
    ]
}
```

### **2. Create Parent-Student Relationship**
```http
POST /api/parent-students/
Content-Type: application/json
```

**Request Body:**
```json
{
    "parent": 15,
    "student": "ce695f13-acef-4dac-8c21-b83a2c37d204",
    "relationship": "mother",
    "is_primary": true,
    "is_emergency_contact": true,
    "receive_sms": true,
    "receive_email": true,
    "receive_push": true
}
```

**Relationship Types:**
- `"father"`, `"mother"`, `"guardian"`, `"grandparent"`, `"aunt"`, `"uncle"`, `"sibling"`, `"other"`

### **3. Update Parent-Student Relationship**
```http
PATCH /api/parent-students/{relationship_id}/
Content-Type: application/json
```

**Request Body:**
```json
{
    "is_primary": false,
    "receive_sms": false,
    "receive_email": true,
    "receive_push": true
}
```

### **4. Delete Parent-Student Relationship**
```http
DELETE /api/parent-students/{relationship_id}/
```

### **5. Get Student's Parents**
```http
GET /api/students/{student_id}/parents/
```

**Response:**
```json
{
    "student_id": "ce695f13-acef-4dac-8c21-b83a2c37d204",
    "student_name": "Emma Smith",
    "parents": [
        {
            "parent_id": 15,
            "parent_name": "John Smith",
            "relationship": "father",
            "is_primary": true,
            "is_emergency_contact": true,
            "phone": "+1234567890",
            "email": "john.smith@email.com"
        },
        {
            "parent_id": 20,
            "parent_name": "Jane Smith",
            "relationship": "mother",
            "is_primary": false,
            "is_emergency_contact": true,
            "phone": "+1987654321",
            "email": "jane.smith@email.com"
        }
    ]
}
```

---

## 📢 Parent Communication & Notifications

### **1. Send Individual Notification**
```http
POST /api/notifications/
Content-Type: application/json
```

**Request Body:**
```json
{
    "title": "Student Absence Notice",
    "body": "Emma Smith was absent from school today. Please contact the office if this was unexcused.",
    "notification_type": "behavior",
    "target_user_ids": [15, 20],
    "data": {
        "student_id": "ce695f13-acef-4dac-8c21-b83a2c37d204",
        "absence_date": "2024-03-01",
        "absence_type": "unexcused"
    }
}
```

**Response:**
```json
{
    "id": "notification-uuid",
    "title": "Student Absence Notice",
    "body": "Emma Smith was absent from school today...",
    "notification_type": "behavior",
    "target_users": [15, 20],
    "created_at": "2024-03-01T10:00:00Z",
    "sent_via_fcm": false,
    "sent_via_email": false,
    "sent_via_sms": false,
    "sent_at": null,
    "delivery_status": "pending"
}
```

### **2. Send Bulk Notification to All Parents**
```http
POST /api/notifications/bulk/
Content-Type: application/json
```

**Request Body:**
```json
{
    "title": "School Holiday Notice",
    "body": "School will be closed on Monday, January 15th for Martin Luther King Jr. Day",
    "notification_type": "general",
    "target_type": "parents",
    "school_filter": true,
    "data": {
        "holiday_date": "2024-01-15",
        "type": "federal_holiday",
        "next_school_day": "2024-01-16"
    }
}
```

**Target Types:**
- `"parents"` - All parents in the school
- `"staff"` - All school staff
- `"emergency_contacts"` - Only emergency contacts
- `"primary_contacts"` - Only primary contacts

### **3. Send Class-Specific Notification**
```http
POST /api/notifications/
Content-Type: application/json
```

**Request Body:**
```json
{
    "title": "Grade 5 Field Trip",
    "body": "Grade 5 students will visit the Science Museum on Friday. Please send $20 for lunch.",
    "notification_type": "academic",
    "target_user_ids": "class:Grade 5",
    "data": {
        "field_trip_date": "2024-03-15",
        "cost": "20.00",
        "deadline": "2024-03-10"
    }
}
```

### **4. Send Emergency Alert**
```http
POST /api/notifications/
Content-Type: application/json
```

**Request Body:**
```json
{
    "title": "EMERGENCY: School Lockdown",
    "body": "The school is currently in lockdown as a precautionary measure. All students are safe. We will update you as soon as possible.",
    "notification_type": "general",
    "target_user_ids": "all_parents",
    "data": {
        "emergency_type": "lockdown",
        "priority": "critical",
        "status": "ongoing",
        "contact_number": "+1-800-SCHOOL"
    }
}
```

### **5. Get Notification List**
```http
GET /api/notifications/
```

**Query Parameters:**
- `notification_type` (string): Filter by type (academic, behavior, payment, general)
- `sent_at__gte` (datetime): Filter by sent date
- `page` (int): Page number

**Response:**
```json
{
    "count": 50,
    "results": [
        {
            "id": "notification-uuid",
            "title": "School Holiday Notice",
            "body": "School will be closed...",
            "notification_type": "general",
            "target_users_count": 150,
            "created_at": "2024-03-01T10:00:00Z",
            "sent_at": "2024-03-01T10:05:00Z",
            "delivery_stats": {
                "fcm_delivered": 140,
                "email_delivered": 135,
                "sms_delivered": 0
            }
        }
    ]
}
```

### **6. Get Notification Details**
```http
GET /api/notifications/{notification_id}/
```

**Response:**
```json
{
    "id": "notification-uuid",
    "title": "School Holiday Notice",
    "body": "School will be closed on Monday, January 15th for Martin Luther King Jr. Day",
    "notification_type": "general",
    "target_users": [15, 20, 25, 30],
    "sent_via_fcm": true,
    "sent_via_email": true,
    "sent_via_sms": false,
    "created_at": "2024-03-01T10:00:00Z",
    "sent_at": "2024-03-01T10:05:00Z",
    "data": {
        "holiday_date": "2024-01-15",
        "type": "federal_holiday"
    }
}
```

### **7. Get Bulk Notification Status**
```http
GET /api/notifications/bulk/{task_id}/status/
```

**Response:**
```json
{
    "task_id": "bulk-notification-123",
    "status": "completed",
    "progress": {
        "total_targets": 200,
        "notifications_sent": 200,
        "failed": 0
    },
    "started_at": "2024-03-01T10:00:00Z",
    "completed_at": "2024-03-01T10:05:00Z"
}
```

### **8. Get Notification Analytics**
```http
GET /api/notifications/{notification_id}/analytics/
```

**Response:**
```json
{
    "notification_id": "notification-uuid",
    "total_targets": 150,
    "delivery_stats": {
        "fcm_delivered": 140,
        "email_delivered": 135,
        "sms_delivered": 0
    },
    "read_stats": {
        "total_read": 120,
        "read_rate": 80.0
    },
    "delivery_timeline": {
        "queued_at": "2024-03-01T10:00:00Z",
        "first_delivery": "2024-03-01T10:02:00Z",
        "last_delivery": "2024-03-01T10:08:00Z"
    }
}
```

### **9. Get Parent Communication History**
```http
GET /api/notification-deliveries/?user={parent_id}
```

**Response:**
```json
{
    "count": 25,
    "results": [
        {
            "id": 1,
            "notification_title": "School Holiday Notice",
            "notification_type": "general",
            "user": 15,
            "user_name": "John Smith",
            "delivered_via_fcm": true,
            "delivered_via_email": true,
            "delivered_via_sms": false,
            "read_at": "2024-03-01T11:00:00Z",
            "delivered_at": "2024-03-01T10:05:00Z"
        }
    ]
}
```

---

## 📊 Data Models

### **ParentStudent Model**
```json
{
    "id": "integer",
    "parent": "integer (User ID)",
    "parent_name": "string (read-only)",
    "student": "string (Student UUID)",
    "student_name": "string (read-only)",
    "relationship": "string (choice)",
    "is_primary": "boolean",
    "is_emergency_contact": "boolean",
    "receive_sms": "boolean",
    "receive_email": "boolean",
    "receive_push": "boolean",
    "created_at": "datetime (read-only)"
}
```

### **Notification Model**
```json
{
    "id": "string (UUID)",
    "school": "string (School UUID)",
    "title": "string (max 200 chars)",
    "body": "text",
    "notification_type": "string (academic|behavior|payment|general)",
    "target_users": "array of integers (User IDs)",
    "sent_via_fcm": "boolean",
    "sent_via_email": "boolean",
    "sent_via_sms": "boolean",
    "data": "object (JSON)",
    "created_at": "datetime",
    "sent_at": "datetime (nullable)"
}
```

### **User Model (Parent)**
```json
{
    "id": "integer",
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "phone": "string",
    "user_type": "string (parent)",
    "school": "string (School UUID)",
    "is_active": "boolean",
    "fcm_token": "string (nullable)",
    "created_at": "datetime",
    "last_login": "datetime (nullable)"
}
```

---

## ⚠️ Error Handling

### **Common HTTP Status Codes**

| Status Code | Description | Example Response |
|-------------|-------------|------------------|
| `200` | Success | Data returned successfully |
| `201` | Created | Resource created successfully |
| `400` | Bad Request | Invalid request data |
| `401` | Unauthorized | Authentication required |
| `403` | Forbidden | Insufficient permissions |
| `404` | Not Found | Resource not found |
| `500` | Server Error | Internal server error |

### **Error Response Format**
```json
{
    "error": "Error message description",
    "details": {
        "field_name": ["Specific field error message"]
    }
}
```

### **Common Errors**

#### **400 Bad Request**
```json
{
    "error": "Validation failed",
    "details": {
        "email": ["This field must be unique"],
        "phone": ["Enter a valid phone number"]
    }
}
```

#### **403 Forbidden**
```json
{
    "error": "You do not have permission to access this parent's information"
}
```

#### **404 Not Found**
```json
{
    "error": "Parent not found or access denied"
}
```

---

## 📊 API Endpoint Summary

### **Parent Management Endpoints**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/users/?user_type=parent` | GET | List all parents |
| `/api/auth/register/` | POST | Create new parent |
| `/api/auth/users/{parent_id}/` | GET, PATCH | Get/update parent details |

### **Parent-Student Relationship Endpoints**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/parent-students/` | GET, POST | List/create parent-student relationships |
| `/api/parent-students/{id}/` | GET, PATCH, DELETE | Manage individual relationships |
| `/api/students/{student_id}/parents/` | GET | Get student's parents |

### **Communication & Notification Endpoints**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/notifications/` | GET, POST | List/send notifications |
| `/api/notifications/{id}/` | GET, PATCH, DELETE | Manage individual notifications |
| `/api/notifications/bulk/` | POST | Send bulk notifications |
| `/api/notifications/bulk/{task_id}/status/` | GET | Check bulk notification status |
| `/api/notifications/{id}/analytics/` | GET | Get notification analytics |
| `/api/notification-deliveries/` | GET | Track notification deliveries |

---

## 📞 Support and Documentation

- **Swagger UI**: Available at `/api/docs/`
- **ReDoc**: Available at `/api/redoc/`
- **API Root**: Available at `/api/` (lists all endpoints)

For technical support regarding parent management APIs:
- Backend Team: backend@school.com
- API Issues: Create issue in project repository
- Emergency: Contact system administrator

**Last Updated:** January 2024  
**API Version:** v1.0