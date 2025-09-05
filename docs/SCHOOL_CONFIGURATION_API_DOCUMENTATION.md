# School Configuration API Documentation

This document provides comprehensive documentation for all school configuration related API endpoints, including detailed request payloads, response formats, and usage examples.

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Permissions](#permissions)
4. [Endpoints](#endpoints)
   - [School Management](#school-management)
   - [School Configuration](#school-configuration)
5. [Request/Response Examples](#requestresponse-examples)
6. [Error Handling](#error-handling)
7. [Testing Examples](#testing-examples)

## Overview

The School Configuration API provides comprehensive management of school information and configuration settings. It includes endpoints for creating, reading, updating, and managing school data along with their associated configuration settings.

### Base URL
```
http://localhost:8000/api/schools/
```

## Authentication

All endpoints require authentication. Include the authentication token in the request headers:

```http
Authorization: Token <your-token>
```

## Permissions

### School Management Permissions
- **Super Admins**: Full access to all schools and configurations
- **School Staff**: Can only access and manage their own school
- **Other Users**: No access

### Configuration Management Permissions
- **Super Admins**: Can manage configuration for any school
- **School Staff**: Can only manage configuration for their own school
- **Other Users**: No access

## Endpoints

### School Management

#### 1. List Schools
**GET** `/api/schools/`

Retrieve a paginated list of schools with filtering options.

**Query Parameters:**
- `search` (string): Search schools by name, email, or address
- `school_type` (string): Filter by school type (`primary`, `secondary`, `both`, `university`, `other`)
- `city` (string): Filter by city
- `state` (string): Filter by state
- `country` (string): Filter by country
- `is_active` (boolean): Filter by active status
- `is_verified` (boolean): Filter by verification status
- `page` (integer): Page number for pagination
- `page_size` (integer): Number of items per page

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/schools/?page=2",
  "previous": null,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "École Primaire de Niamey",
      "slug": "ecole-primaire-niamey",
      "school_type": "primary",
      "city": "Niamey",
      "state": "Niamey",
      "is_active": true,
      "is_verified": true,
      "student_count": 150,
      "staff_count": 12
    }
  ]
}
```

#### 2. Create School
**POST** `/api/schools/`

Create a new school with default configuration.

**Request Body:**
```json
{
  "name": "École Secondaire de Maradi",
  "school_type": "secondary",
  "academic_year": "2024-2025",
  "logo": "https://firebase-storage.com/schools/logos/maradi-logo.png",
  "primary_color": "#1976D2",
  "secondary_color": "#424242",
  "contact_email": "contact@ecole-maradi.ne",
  "contact_phone": "+22712345678",
  "website": "https://ecole-maradi.ne",
  "address": "Quartier Sabon Gari, Maradi",
  "city": "Maradi",
  "state": "Maradi",
  "country": "Niger",
  "postal_code": "8000",
  "is_active": true,
  "is_verified": false
}
```

**Required Fields:**
- `name` (string): School name
- `school_type` (string): Type of school (`primary`, `secondary`, `both`, `university`, `other`)
- `contact_email` (string): Contact email address

**Optional Fields:**
- `academic_year` (string): Academic year (e.g., "2024-2025")
- `logo` (string): URL to school logo
- `primary_color` (string): Primary brand color (hex code)
- `secondary_color` (string): Secondary brand color (hex code)
- `contact_phone` (string): Contact phone number
- `website` (string): School website URL
- `address` (string): School address
- `city` (string): City
- `state` (string): State/Province
- `country` (string): Country
- `postal_code` (string): Postal/ZIP code
- `is_active` (boolean): Whether school is active
- `is_verified` (boolean): Whether school is verified

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "École Secondaire de Maradi",
  "slug": "ecole-secondaire-maradi",
  "school_type": "secondary",
  "academic_year": "2024-2025",
  "logo": "https://firebase-storage.com/schools/logos/maradi-logo.png",
  "primary_color": "#1976D2",
  "secondary_color": "#424242",
  "contact_email": "contact@ecole-maradi.ne",
  "contact_phone": "+22712345678",
  "website": "https://ecole-maradi.ne",
  "address": "Quartier Sabon Gari, Maradi",
  "city": "Maradi",
  "state": "Maradi",
  "country": "Niger",
  "postal_code": "8000",
  "is_active": true,
  "is_verified": false,
  "student_count": 0,
  "staff_count": 0,
  "configuration": {
    "academic_year_start": "2024-09-01",
    "academic_year_end": "2025-06-30",
    "current_semester": "first",
    "enable_sms_notifications": true,
    "enable_email_notifications": true,
    "enable_push_notifications": true,
    "currency": "NGN",
    "payment_reminder_days": 7,
    "max_file_size_mb": 10,
    "allowed_file_types": [".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"]
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### 3. Retrieve School
**GET** `/api/schools/{id}/`

Get detailed information about a specific school.

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "École Primaire de Niamey",
  "slug": "ecole-primaire-niamey",
  "school_type": "primary",
  "academic_year": "2024-2025",
  "logo": "https://firebase-storage.com/schools/logos/logo.png",
  "primary_color": "#1976D2",
  "secondary_color": "#424242",
  "contact_email": "contact@ecole-niamey.ne",
  "contact_phone": "+22712345678",
  "website": "https://ecole-niamey.ne",
  "address": "Quartier Plateau, Niamey",
  "city": "Niamey",
  "state": "Niamey",
  "country": "Niger",
  "postal_code": "10000",
  "is_active": true,
  "is_verified": true,
  "student_count": 150,
  "staff_count": 12,
  "configuration": {
    "academic_year_start": "2024-09-01",
    "academic_year_end": "2025-06-30",
    "current_semester": "first",
    "enable_sms_notifications": true,
    "enable_email_notifications": true,
    "enable_push_notifications": true,
    "currency": "NGN",
    "payment_reminder_days": 7,
    "max_file_size_mb": 10,
    "allowed_file_types": [".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"]
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-09-04T14:20:00Z"
}
```

#### 4. Update School (Full Update)
**PUT** `/api/schools/{id}/`

Update all school information (full replacement).

**Request Body:**
```json
{
  "name": "École Primaire de Niamey - Updated",
  "school_type": "both",
  "academic_year": "2024-2025",
  "logo": "https://firebase-storage.com/schools/logos/new-logo.png",
  "primary_color": "#FF5722",
  "secondary_color": "#607D8B",
  "contact_email": "new-contact@ecole-niamey.ne",
  "contact_phone": "+22798765432",
  "website": "https://new-ecole-niamey.ne",
  "address": "Nouveau Quartier, Niamey",
  "city": "Niamey",
  "state": "Niamey",
  "country": "Niger",
  "postal_code": "10001",
  "is_active": true,
  "is_verified": true,
  "configuration": {
    "academic_year_start": "2024-09-01",
    "academic_year_end": "2025-06-30",
    "current_semester": "first",
    "enable_sms_notifications": false,
    "enable_email_notifications": true,
    "enable_push_notifications": true,
    "currency": "USD",
    "payment_reminder_days": 14,
    "max_file_size_mb": 20,
    "allowed_file_types": [".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png", ".gif"]
  }
}
```

#### 5. Partially Update School
**PATCH** `/api/schools/{id}/`

Partially update school information.

**Request Body Examples:**

**Update branding only:**
```json
{
  "name": "École Primaire de Niamey - New Name",
  "logo": "https://firebase-storage.com/schools/logos/brand-new-logo.png",
  "primary_color": "#4CAF50",
  "secondary_color": "#2196F3"
}
```

**Update contact information only:**
```json
{
  "contact_email": "info@ecole-niamey.ne",
  "contact_phone": "+22712345678",
  "website": "https://www.ecole-niamey.ne",
  "address": "Avenue de la République, Niamey",
  "city": "Niamey",
  "state": "Niamey",
  "postal_code": "10000"
}
```

**Update status only:**
```json
{
  "is_active": true,
  "is_verified": true
}
```

**Update configuration only:**
```json
{
  "configuration": {
    "enable_sms_notifications": false,
    "currency": "EUR",
    "max_file_size_mb": 15,
    "payment_reminder_days": 10
  }
}
```

**Update mixed fields:**
```json
{
  "name": "École Moderne de Niamey",
  "primary_color": "#FF9800",
  "contact_email": "modern@ecole-niamey.ne",
  "configuration": {
    "current_semester": "second",
    "enable_email_notifications": true,
    "currency": "NGN"
  }
}
```

#### 6. Delete School
**DELETE** `/api/schools/{id}/`

Permanently delete a school and its configuration.

**Response:**
```json
{
  "message": "School deleted successfully"
}
```

### School Configuration

#### 7. Get School Configuration
**GET** `/api/schools/{id}/configuration/`

Retrieve complete school information including configuration settings.

**Response:**
```json
{
  "school_id": "123e4567-e89b-12d3-a456-426614174000",
  "school_name": "École Primaire de Niamey",
  "school_slug": "ecole-primaire-niamey",
  "school_type": "primary",
  "academic_year": "2024-2025",
  "logo": "https://firebase-storage.com/schools/logos/logo.png",
  "primary_color": "#1976D2",
  "secondary_color": "#424242",
  "contact_email": "contact@ecole-niamey.ne",
  "contact_phone": "+22712345678",
  "website": "https://ecole-niamey.ne",
  "address": "Quartier Plateau, Niamey",
  "city": "Niamey",
  "state": "Niamey",
  "country": "Niger",
  "postal_code": "10000",
  "is_active": true,
  "is_verified": true,
  "student_count": 150,
  "staff_count": 12,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-09-04T14:20:00Z",
  "config_created_at": "2024-01-15T10:30:00Z",
  "config_updated_at": "2024-09-04T14:20:00Z",
  "academic_year_start": "2024-09-01",
  "academic_year_end": "2025-06-30",
  "current_semester": "first",
  "enable_sms_notifications": true,
  "enable_email_notifications": true,
  "enable_push_notifications": true,
  "currency": "NGN",
  "payment_reminder_days": 7,
  "max_file_size_mb": 10,
  "allowed_file_types": [".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"]
}
```

#### 8. Update School Configuration (Full Update)
**PUT** `/api/schools/{id}/configuration/`

Update entire configuration settings (full replacement).

**Request Body:**
```json
{
  "academic_year_start": "2024-09-01",
  "academic_year_end": "2025-06-30",
  "current_semester": "second",
  "enable_sms_notifications": false,
  "enable_email_notifications": true,
  "enable_push_notifications": true,
  "currency": "USD",
  "payment_reminder_days": 14,
  "max_file_size_mb": 20,
  "allowed_file_types": [".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png", ".gif", ".txt"]
}
```

**Configuration Fields:**
- `academic_year_start` (date): Start date of academic year (YYYY-MM-DD)
- `academic_year_end` (date): End date of academic year (YYYY-MM-DD)
- `current_semester` (string): Current semester (`first`, `second`, `third`)
- `enable_sms_notifications` (boolean): Enable SMS notifications
- `enable_email_notifications` (boolean): Enable email notifications
- `enable_push_notifications` (boolean): Enable push notifications
- `currency` (string): Currency code (e.g., "NGN", "USD", "EUR")
- `payment_reminder_days` (integer): Days before payment reminder
- `max_file_size_mb` (integer): Maximum file size in MB
- `allowed_file_types` (array): List of allowed file extensions

#### 9. Partially Update School Configuration
**PATCH** `/api/schools/{id}/configuration/`

Partially update configuration settings.

**Request Body Examples:**

**Update academic settings only:**
```json
{
  "academic_year_start": "2024-08-15",
  "academic_year_end": "2025-07-15",
  "current_semester": "first"
}
```

**Update notification settings only:**
```json
{
  "enable_sms_notifications": true,
  "enable_email_notifications": false,
  "enable_push_notifications": true
}
```

**Update payment settings only:**
```json
{
  "currency": "NGN",
  "payment_reminder_days": 7
}
```

**Update file upload settings only:**
```json
{
  "max_file_size_mb": 25,
  "allowed_file_types": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mp3"]
}
```

**Update specific fields:**
```json
{
  "enable_sms_notifications": false,
  "currency": "EUR",
  "max_file_size_mb": 15
}
```

### Additional Endpoints

#### 10. Get School Statistics
**GET** `/api/schools/{id}/statistics/`

Retrieve comprehensive statistics for a school.

**Response:**
```json
{
  "total_students": 150,
  "class_distribution": [
    {"class_assigned__level": "1", "count": 25},
    {"class_assigned__level": "2", "count": 30},
    {"class_assigned__level": "3", "count": 28},
    {"class_assigned__level": "4", "count": 32},
    {"class_assigned__level": "5", "count": 35}
  ],
  "class_details": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Grade 1",
      "level": "1",
      "section": "A",
      "full_name": "Grade 1 - A",
      "academic_year": "2024-2025",
      "max_students": 30,
      "student_count": 25,
      "available_spots": 5,
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-09-04T14:20:00Z"
    }
  ],
  "class_statistics": {
    "total_classes": 12,
    "active_classes": 10,
    "total_capacity": 360,
    "utilization_rate": 41.67
  },
  "gender_distribution": [
    {"gender": "M", "count": 78},
    {"gender": "F", "count": 72}
  ],
  "recent_enrollments": 12,
  "payment_statistics": {
    "total_payments": 450,
    "paid_payments": 380,
    "overdue_payments": 70
  }
}
```

#### 11. Activate School
**POST** `/api/schools/{id}/activate/`

Activate a school to make it available for use.

**Response:**
```json
{
  "message": "School activated successfully",
  "is_active": true
}
```

#### 12. Deactivate School
**POST** `/api/schools/{id}/deactivate/`

Deactivate a school to make it unavailable.

**Response:**
```json
{
  "message": "School deactivated successfully",
  "is_active": false
}
```

## Error Handling

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### Error Response Format

```json
{
  "error": "Error message",
  "details": "Detailed error information",
  "field_errors": {
    "field_name": ["Error message for this field"]
  }
}
```

### Common Error Examples

**Validation Error (400):**
```json
{
  "name": ["This field is required."],
  "contact_email": ["Enter a valid email address."],
  "school_type": ["\"invalid_type\" is not a valid choice."]
}
```

**Permission Denied (403):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Not Found (404):**
```json
{
  "detail": "Not found."
}
```

## Testing Examples

### Using cURL

**Create a school:**
```bash
curl -X POST http://localhost:8000/api/schools/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test School",
    "school_type": "primary",
    "contact_email": "test@school.com"
  }'
```

**Update school configuration:**
```bash
curl -X PATCH http://localhost:8000/api/schools/{school-id}/configuration/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "enable_sms_notifications": false,
    "currency": "USD",
    "max_file_size_mb": 20
  }'
```

**Get school configuration:**
```bash
curl -X GET http://localhost:8000/api/schools/{school-id}/configuration/ \
  -H "Authorization: Token your-token-here"
```

### Using Python requests

```python
import requests

# Base configuration
base_url = "http://localhost:8000/api/schools"
headers = {
    "Authorization": "Token your-token-here",
    "Content-Type": "application/json"
}

# Create a school
school_data = {
    "name": "Test School",
    "school_type": "primary",
    "contact_email": "test@school.com",
    "primary_color": "#1976D2",
    "secondary_color": "#424242"
}

response = requests.post(f"{base_url}/", json=school_data, headers=headers)
school = response.json()

# Update configuration
config_data = {
    "enable_sms_notifications": False,
    "currency": "USD",
    "max_file_size_mb": 20
}

response = requests.patch(
    f"{base_url}/{school['id']}/configuration/", 
    json=config_data, 
    headers=headers
)
```

### Using JavaScript fetch

```javascript
const baseUrl = 'http://localhost:8000/api/schools';
const headers = {
  'Authorization': 'Token your-token-here',
  'Content-Type': 'application/json'
};

// Create a school
const schoolData = {
  name: 'Test School',
  school_type: 'primary',
  contact_email: 'test@school.com',
  primary_color: '#1976D2',
  secondary_color: '#424242'
};

fetch(`${baseUrl}/`, {
  method: 'POST',
  headers: headers,
  body: JSON.stringify(schoolData)
})
.then(response => response.json())
.then(data => {
  console.log('School created:', data);
  
  // Update configuration
  const configData = {
    enable_sms_notifications: false,
    currency: 'USD',
    max_file_size_mb: 20
  };
  
  return fetch(`${baseUrl}/${data.id}/configuration/`, {
    method: 'PATCH',
    headers: headers,
    body: JSON.stringify(configData)
  });
})
.then(response => response.json())
.then(config => console.log('Configuration updated:', config));
```

## Notes

1. **Auto-Configuration Creation**: When a school is created, a default configuration is automatically created if not provided.

2. **Configuration Auto-Creation**: If a school doesn't have a configuration when accessing the configuration endpoint, one will be automatically created with default values.

3. **Field Validation**: All fields are validated according to their data types and constraints. Check the error response for specific validation errors.

4. **Pagination**: List endpoints support pagination with `page` and `page_size` parameters.

5. **Filtering**: List endpoints support various filtering options for efficient data retrieval.

6. **Permissions**: Always ensure the authenticated user has the appropriate permissions before making requests.

7. **Rate Limiting**: Be aware of any rate limiting that may be in place for the API.

8. **Token Expiration**: Authentication tokens may expire, requiring re-authentication.

This documentation covers all school configuration related endpoints with comprehensive examples and usage instructions.
