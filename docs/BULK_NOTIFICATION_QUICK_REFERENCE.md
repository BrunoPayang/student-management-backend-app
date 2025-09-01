and this was # Bulk Notification Quick Reference

## 🚀 Quick Start

**Endpoint**: `POST /api/notifications/send_bulk/`

**Headers**: 
```
Authorization: Bearer <your_token>
Content-Type: application/json
```

## 📝 Basic Payload (All Parents)

```json
{
    "title": "Your Title Here",
    "body": "Your message content here",
    "notification_type": "general"
}
```

## 🎯 Notification Types

- `general` - General announcements
- `academic` - Academic updates, grades
- `behavior` - Behavior reports
- `payment` - Payment reminders

## 📋 Complete Payload Options

```json
{
    "title": "Required: Notification title",
    "body": "Required: Notification content",
    "notification_type": "Required: general|academic|behavior|payment",
    "user_ids": "Optional: [1,2,3] - specific users (empty = all parents)",
    "school": "Optional: 1 - school ID (required for admin users)",
    "data": "Optional: {} - additional data for app actions"
}
```

## ✅ Success Response

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

## 🔧 Common Examples

### Simple Announcement
```bash
curl -X POST "http://127.0.0.1:8000/api/notifications/send_bulk/" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Parent Meeting",
    "body": "Meeting next Friday at 3 PM",
    "notification_type": "general"
  }'
```

### Payment Reminder
```bash
curl -X POST "http://127.0.0.1:8000/api/notifications/send_bulk/" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Payment Due",
    "body": "Monthly payment due on Jan 15th",
    "notification_type": "payment",
    "data": {
      "due_date": "2024-01-15",
      "amount": 500.00
    }
  }'
```

### Admin to Specific School
```bash
curl -X POST "http://127.0.0.1:8000/api/notifications/send_bulk/" \
  -H "Authorization: Bearer admin_token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "School Update",
    "body": "Important update for all parents",
    "notification_type": "academic",
    "school": 2
  }'
```

## 🎯 How Targeting Works

**Without `user_ids`**: Automatically targets ALL parents in your school:
- Direct school parents (user_type='parent' + school assigned)
- Parents with students in the school (via ParentStudent relationship)

**With `user_ids`**: Targets only specified users

## 🔍 Monitoring

- **Admin Interface**: `/admin/notifications/notificationdelivery/`
- **API Response**: Check `results.total_targets` for delivery count
- **Delivery Status**: Monitor `fcm_sent` and `email_sent` counts

## ⚠️ Common Errors

| Error | Solution |
|-------|----------|
| "Title and body are required" | Add both fields to payload |
| "School ID is required for admin users" | Add `school` parameter |
| "User must be associated with a school" | Ensure user has school assigned |
| 401 Unauthorized | Check authentication token |

## 🚀 JavaScript Example

```javascript
const sendNotification = async (payload) => {
    const response = await fetch('/api/notifications/send_bulk/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    });
    return response.json();
};

// Usage
sendNotification({
    title: "Important Update",
    body: "Check your portal for updates",
    notification_type: "general"
});
```

