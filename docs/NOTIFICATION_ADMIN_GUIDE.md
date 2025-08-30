# Notification Admin Interface Guide

## Overview

The SchoolConnect system now includes a comprehensive admin interface for managing notifications. Administrators can view, create, edit, and manage all notifications and their delivery status through the Django admin panel.

## Accessing the Admin Interface

1. Navigate to `/admin/` in your browser
2. Log in with your admin credentials
3. You'll see the "SchoolConnect Administration" dashboard

## Available Admin Sections

### 1. Notifications

**Location**: Admin → Notifications → Notifications

**Features**:
- **List View**: Shows all notifications with key information
  - ID, Title, Type, School, Target Users Count
  - Delivery method status (FCM, Email, SMS)
  - Creation and sent timestamps

**Filters**:
- Notification Type (Academic, Behavior, Payment, General)
- Delivery Method Status
- Creation Date
- School

**Search**: Search by title, body, or school name

**Actions**:
- **Mark as Sent**: Update sent timestamp for selected notifications
- **Resend Notifications**: Resend selected notifications to all target users

**Creating/Editing Notifications**:
- Basic Information: Title, body, type, school
- Target Users: Select specific users or leave empty for all school users
- Delivery Methods: Track which methods have been used
- Additional Data: JSON field for extra notification data

### 2. Notification Deliveries

**Location**: Admin → Notifications → Notification Deliveries

**Features**:
- **List View**: Shows delivery tracking for each notification-user combination
  - Notification title (with link)
  - Target user
  - Delivery status (color-coded)
  - Read status (color-coded)
  - Timestamps

**Filters**:
- Delivery method status
- Creation, delivery, and read dates
- Notification type and school

**Search**: Search by notification title, user email, or user names

**Actions**:
- **Mark as Delivered**: Update delivery status and timestamp
- **Mark as Read**: Update read timestamp

## Admin Interface Features

### Color-Coded Status Indicators

- **Delivery Status**:
  - 🟢 Green ✓: Successfully delivered
  - 🔴 Red ✗: Failed delivery
  - 🟠 Orange ⏳: Pending delivery

- **Read Status**:
  - 🟢 Green ✓: Read by user
  - ⚪ Gray ○: Unread

### Optimized Queries

The admin interface uses optimized database queries with:
- `select_related()` for foreign key relationships
- `prefetch_related()` for many-to-many relationships
- Efficient filtering and search

### Bulk Operations

- Select multiple notifications/deliveries
- Apply actions to all selected items
- Batch status updates

## Common Admin Tasks

### 1. Creating a New Notification

1. Go to Admin → Notifications → Notifications
2. Click "Add Notification"
3. Fill in required fields:
   - **School**: Select the target school
   - **Title**: Brief notification title
   - **Body**: Detailed notification content
   - **Type**: Choose from available types
   - **Target Users**: Select specific users or leave empty for all
4. Save the notification

### 2. Monitoring Delivery Status

1. Go to Admin → Notifications → Notification Deliveries
2. Use filters to narrow down results:
   - Filter by school or notification type
   - Filter by delivery status
3. Check delivery and read status for each user
4. Use bulk actions to update multiple records

### 3. Troubleshooting Failed Deliveries

1. Look for red ✗ status indicators
2. Check the FCM error field for specific error messages
3. Verify user FCM tokens are valid
4. Use the "Resend Notifications" action to retry

### 4. School-Specific Management

- School staff can only see notifications for their school
- System admins can see and manage all notifications
- Use school filters to focus on specific institutions

## Best Practices

### 1. Notification Creation
- Use clear, concise titles
- Provide detailed information in the body
- Select appropriate notification types for better organization
- Test with a small group before sending to all users

### 2. Monitoring and Maintenance
- Regularly check delivery status
- Monitor failed deliveries and investigate errors
- Use bulk actions for efficiency
- Archive old notifications when appropriate

### 3. User Management
- Keep target user lists updated
- Monitor user engagement through read status
- Use delivery data to improve notification strategies

## Troubleshooting

### Common Issues

1. **Notifications not appearing in admin**:
   - Check if models are properly registered
   - Verify admin user has proper permissions
   - Check Django admin configuration

2. **Delivery status not updating**:
   - Verify notification service is working
   - Check FCM configuration
   - Review error logs

3. **Performance issues**:
   - Admin uses optimized queries
   - Consider pagination for large datasets
   - Use filters to narrow results

### Getting Help

If you encounter issues:
1. Check the Django admin logs
2. Verify notification service configuration
3. Review FCM and email service settings
4. Check user permissions and school assignments

## API Integration

The admin interface works alongside the notification API:
- Admin changes are reflected in API responses
- API-created notifications appear in admin
- Bulk operations can be performed through both interfaces
- Real-time status updates are maintained

## Security Considerations

- Only authenticated admin users can access the interface
- School staff are limited to their school's data
- System admins have full access to all notifications
- User privacy is maintained through proper filtering

