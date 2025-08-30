# Bulk Notification API Guide

## Overview

This guide explains how to send bulk notifications to all parents using the SchoolConnect notification API. The system automatically handles targeting all parents associated with a school, including those who may not have the school directly assigned to their user account.

## Endpoint Details

### **Endpoint**: `POST /api/notifications/send_bulk/`

### **Authentication**: Required
- Include your authentication token in the request header
- Format: `Authorization: Bearer <your_token>`

## Request Payload

### **Basic Payload (Send to All Parents in Your School)**

```json
{
    "title": "Important Announcement",
    "body": "This is an important message for all parents.",
    "notification_type": "general"
}
```

### **Advanced Payload (With Additional Options)**

```json
{
    "title": "Payment Reminder",
    "body": "Please complete your payment for this month's fees.",
    "notification_type": "payment",
    "user_ids": [],
    "data": {
        "action": "payment_reminder",
        "due_date": "2024-01-15",
        "amount": 500.00
    }
}
```

### **Admin User Payload (Send to Specific School)**

```json
{
    "title": "School Update",
    "body": "Important update for all parents.",
    "notification_type": "academic",
    "school": 1,
    "data": {
        "event_type": "parent_meeting",
        "date": "2024-01-20"
    }
}
```

## Payload Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | string | ✅ | Notification title (max 200 characters) |
| `body` | string | ✅ | Notification content |
| `notification_type` | string | ✅ | Type of notification: `academic`, `behavior`, `payment`, `general` |
| `user_ids` | array | ❌ | Specific user IDs to target (empty for all parents) |
| `school` | integer | ❌ | School ID (required for admin users) |
| `data` | object | ❌ | Additional data for the notification |

## Notification Types

- **`academic`**: Academic updates, grades, assignments
- **`behavior`**: Behavior reports, disciplinary actions
- **`payment`**: Payment reminders, fee updates
- **`general`**: General announcements, events

## How It Works

### **Automatic Parent Targeting**

When you send a bulk notification without specifying `user_ids`, the system automatically targets:

1. **Direct School Parents**: Users with `user_type='parent'` and `school` assigned
2. **Student Parents**: Parents who have students enrolled in the school (via `ParentStudent` relationship)
3. **Combined List**: The system merges both groups to ensure no parent is missed

### **User Permission Logic**

- **School Staff**: Can only send to their assigned school
- **System Admin**: Must specify a `school` ID in the payload
- **Parents**: Cannot send bulk notifications (restricted)

## Response Format

### **Success Response (200)**

```json
{
    "message": "Bulk notification sent successfully",
    "results": {
        "fcm_sent": 45,
        "email_sent": 42,
        "total_targets": 50
    }
}
```

### **Error Response (400)**

```json
{
    "error": "Title and body are required"
}
```

## Examples

### **Example 1: Simple Announcement**

```bash
curl -X POST "http://localhost:8000/api/notifications/send_bulk/" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Parent-Teacher Meeting",
    "body": "We will have a parent-teacher meeting next Friday at 3 PM.",
    "notification_type": "general"
  }'
```

### **Example 2: Payment Reminder**

```bash
curl -X POST "http://localhost:8000/api/notifications/send_bulk/" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Payment Due",
    "body": "Your monthly payment of $500 is due on January 15th.",
    "notification_type": "payment",
    "data": {
      "due_date": "2024-01-15",
      "amount": 500.00,
      "payment_link": "https://school.com/pay"
    }
  }'
```

### **Example 3: Academic Update**

```bash
curl -X POST "http://localhost:8000/api/notifications/send_bulk/" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Report Cards Available",
    "body": "Your child\'s report card is now available in the portal.",
    "notification_type": "academic",
    "data": {
      "action": "view_report_card",
      "portal_url": "https://school.com/portal"
    }
  }'
```

### **Example 4: Admin Sending to Specific School**

```bash
curl -X POST "http://localhost:8000/api/notifications/send_bulk/" \
  -H "Authorization: Bearer admin_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "School Closure",
    "body": "School will be closed tomorrow due to weather conditions.",
    "notification_type": "general",
    "school": 2,
    "data": {
      "closure_date": "2024-01-16",
      "reason": "weather"
    }
  }'
```

## JavaScript/Frontend Examples

### **Using Fetch API**

```javascript
async function sendBulkNotification(payload) {
    try {
        const response = await fetch('/api/notifications/send_bulk/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            console.log('Notification sent successfully:', data);
            return data;
        } else {
            console.error('Error sending notification:', data.error);
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Request failed:', error);
        throw error;
    }
}

// Usage
const notificationPayload = {
    title: "Important Update",
    body: "Please check the latest updates in your portal.",
    notification_type: "general"
};

sendBulkNotification(notificationPayload)
    .then(result => {
        console.log(`Sent to ${result.results.total_targets} parents`);
    })
    .catch(error => {
        console.error('Failed to send notification:', error);
    });
```

### **Using Axios**

```javascript
import axios from 'axios';

const sendBulkNotification = async (payload) => {
    try {
        const response = await axios.post('/api/notifications/send_bulk/', payload, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json',
            }
        });
        
        return response.data;
    } catch (error) {
        console.error('Error sending notification:', error.response?.data || error.message);
        throw error;
    }
};

// Usage
const payload = {
    title: "Emergency Alert",
    body: "School will close early today due to weather.",
    notification_type: "general",
    data: {
        emergency: true,
        closure_time: "2:00 PM"
    }
};

sendBulkNotification(payload)
    .then(result => {
        alert(`Notification sent to ${result.results.total_targets} parents`);
    })
    .catch(error => {
        alert('Failed to send notification');
    });
```

## Best Practices

### **1. Notification Content**
- Keep titles concise (under 50 characters)
- Provide clear, actionable content in the body
- Use appropriate notification types for better organization
- Include relevant data for app-specific actions

### **2. Timing and Frequency**
- Avoid sending too many notifications at once
- Consider time zones when sending time-sensitive messages
- Use appropriate urgency levels

### **3. Testing**
- Test with a small group first using `user_ids`
- Verify delivery status through the admin interface
- Monitor delivery success rates

### **4. Error Handling**
- Always handle API errors gracefully
- Check response status and error messages
- Implement retry logic for failed requests

## Monitoring and Tracking

### **Admin Interface**
- Monitor delivery status at `/admin/notifications/notificationdelivery/`
- Track read status and delivery success rates
- Use bulk actions to manage notifications

### **API Tracking**
- Check the `results` object in the response
- Monitor `fcm_sent`, `email_sent`, and `total_targets`
- Use delivery tracking endpoints for detailed status

## Troubleshooting

### **Common Issues**

1. **"School ID is required for admin users"**
   - Add `school` parameter to your payload

2. **"User must be associated with a school"**
   - Ensure your user account has a school assigned
   - Contact admin if you need school assignment

3. **Low delivery success rate**
   - Check FCM configuration
   - Verify user FCM tokens are valid
   - Review notification service logs

4. **Permission denied**
   - Ensure you have proper authentication
   - Check user permissions and school access

### **Getting Help**

- Check the notification admin interface for delivery status
- Review server logs for detailed error information
- Use the resend functionality for failed notifications
- Contact system administrator for permission issues

