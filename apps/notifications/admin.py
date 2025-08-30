from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Notification, NotificationDelivery

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'notification_type', 'school', 'target_users_count',
        'sent_via_fcm', 'sent_via_email', 'sent_via_sms', 'created_at', 'sent_at'
    ]
    list_filter = [
        'notification_type', 'sent_via_fcm', 'sent_via_email', 'sent_via_sms',
        'created_at', 'sent_at', 'school'
    ]
    search_fields = ['title', 'body', 'school__name']
    readonly_fields = ['id', 'created_at', 'sent_at', 'target_users_info']
    filter_horizontal = ['target_users']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'school', 'title', 'body', 'notification_type')
        }),
        ('Target Users', {
            'fields': ('target_users', 'target_users_info'),
            'description': 'Select users who should receive this notification'
        }),
        ('Delivery Methods', {
            'fields': ('sent_via_fcm', 'sent_via_email', 'sent_via_sms'),
            'description': 'Track which delivery methods have been used'
        }),
        ('Additional Data', {
            'fields': ('data',),
            'description': 'Extra data for the notification (JSON format)'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'sent_at'),
            'classes': ('collapse',)
        })
    )
    
    def target_users_count(self, obj):
        """Display count of target users"""
        count = obj.target_users.count()
        if count > 0:
            url = reverse('admin:authentication_user_changelist')
            return format_html('<a href="{}?notifications__id={}">{} users</a>', url, obj.id, count)
        return "0 users"
    target_users_count.short_description = "Target Users"
    
    def target_users_info(self, obj):
        """Display detailed target users information"""
        if not obj.target_users.exists():
            return "No target users set"
        
        info = obj.get_target_users_info()
        html = f"""
        <div style="background: #f9f9f9; padding: 10px; border-radius: 5px;">
            <strong>Total: {info['total_count']} users</strong><br>
            <strong>By Type:</strong><br>
            • Parents: {info['by_type']['parent']}<br>
            • Staff: {info['by_type']['school_staff']}<br>
            • Admins: {info['by_type']['admin']}<br>
            <strong>By School:</strong><br>
            • Direct School: {info['by_school']['direct_school']}<br>
            • Other Schools: {info['by_school']['other_schools']}<br>
            • No School: {info['by_school']['no_school']}
        </div>
        """
        return format_html(html)
    target_users_info.short_description = "Target Users Details"
    
    def get_queryset(self, request):
        """Optimize queryset with related fields"""
        return super().get_queryset(request).select_related('school').prefetch_related('target_users')
    
    actions = ['mark_as_sent', 'resend_notifications', 'auto_target_all_parents', 'clear_target_users']
    
    def mark_as_sent(self, request, queryset):
        """Mark selected notifications as sent"""
        from django.utils import timezone
        updated = queryset.update(sent_at=timezone.now())
        self.message_user(request, f'{updated} notification(s) marked as sent.')
    mark_as_sent.short_description = "Mark selected notifications as sent"
    
    def resend_notifications(self, request, queryset):
        """Resend selected notifications"""
        from .services import NotificationService
        notification_service = NotificationService()
        success_count = 0
        
        for notification in queryset:
            try:
                notification_service.send_notification(notification)
                success_count += 1
            except Exception as e:
                self.message_user(request, f'Failed to resend notification {notification.id}: {str(e)}', level='ERROR')
        
        if success_count > 0:
            self.message_user(request, f'{success_count} notification(s) resent successfully.')
    resend_notifications.short_description = "Resend selected notifications"
    
    def auto_target_all_parents(self, request, queryset):
        """Automatically target all parents in the school for selected notifications"""
        updated = 0
        for notification in queryset:
            try:
                count = notification.auto_target_all_parents()
                if count > 0:
                    updated += 1
            except Exception as e:
                self.message_user(request, f'Failed to auto-target parents for notification {notification.id}: {str(e)}', level='ERROR')
        
        if updated > 0:
            self.message_user(request, f'{updated} notification(s) updated with auto-targeted parents.')
    auto_target_all_parents.short_description = "Auto-target all parents in school"
    
    def clear_target_users(self, request, queryset):
        """Clear target users for selected notifications"""
        updated = 0
        for notification in queryset:
            try:
                notification.target_users.clear()
                updated += 1
            except Exception as e:
                self.message_user(request, f'Failed to clear target users for notification {notification.id}: {str(e)}', level='ERROR')
        
        if updated > 0:
            self.message_user(request, f'{updated} notification(s) target users cleared.')
    clear_target_users.short_description = "Clear target users"

@admin.register(NotificationDelivery)
class NotificationDeliveryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'notification_title', 'user', 'delivery_status', 'read_status',
        'created_at', 'delivered_at', 'read_at'
    ]
    list_filter = [
        'delivered_via_fcm', 'delivered_via_email', 'delivered_via_sms',
        'created_at', 'delivered_at', 'read_at',
        'notification__notification_type', 'notification__school'
    ]
    search_fields = [
        'notification__title', 'user__email', 'user__first_name', 'user__last_name'
    ]
    readonly_fields = ['id', 'created_at', 'delivered_at', 'read_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'notification', 'user')
        }),
        ('Delivery Status', {
            'fields': (
                'delivered_via_fcm', 'delivered_via_email', 'delivered_via_sms',
                'fcm_message_id', 'fcm_error'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'delivered_at', 'read_at'),
            'classes': ('collapse',)
        })
    )
    
    def notification_title(self, obj):
        """Display notification title with link"""
        if obj.notification:
            url = reverse('admin:notifications_notification_change', args=[obj.notification.id])
            return format_html('<a href="{}">{}</a>', url, obj.notification.title)
        return "N/A"
    notification_title.short_description = "Notification"
    
    def delivery_status(self, obj):
        """Display delivery status with color coding"""
        if obj.delivered_via_fcm or obj.delivered_via_email or obj.delivered_via_sms:
            return format_html('<span style="color: green;">✓ Delivered</span>')
        elif obj.fcm_error:
            return format_html('<span style="color: red;">✗ Failed</span>')
        else:
            return format_html('<span style="color: orange;">⏳ Pending</span>')
    delivery_status.short_description = "Delivery Status"
    
    def read_status(self, obj):
        """Display read status with color coding"""
        if obj.read_at:
            return format_html('<span style="color: green;">✓ Read</span>')
        else:
            return format_html('<span style="color: gray;">○ Unread</span>')
    read_status.short_description = "Read Status"
    
    def get_queryset(self, request):
        """Optimize queryset with related fields"""
        return super().get_queryset(request).select_related('notification', 'user')
    
    actions = ['mark_as_delivered', 'mark_as_read']
    
    def mark_as_delivered(self, request, queryset):
        """Mark selected deliveries as delivered"""
        from django.utils import timezone
        updated = queryset.update(
            delivered_at=timezone.now(),
            delivered_via_fcm=True,
            delivered_via_email=True
        )
        self.message_user(request, f'{updated} delivery record(s) marked as delivered.')
    mark_as_delivered.short_description = "Mark selected deliveries as delivered"
    
    def mark_as_read(self, request, queryset):
        """Mark selected deliveries as read"""
        from django.utils import timezone
        updated = queryset.update(read_at=timezone.now())
        self.message_user(request, f'{updated} delivery record(s) marked as read.')
    mark_as_read.short_description = "Mark selected deliveries as read"

# Customize admin site
admin.site.site_header = "SchoolConnect Administration"
admin.site.site_title = "SchoolConnect Admin"
admin.site.index_title = "Welcome to SchoolConnect Administration"
