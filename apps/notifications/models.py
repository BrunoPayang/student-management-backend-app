from django.db import models
from django.contrib.auth import get_user_model
from apps.schools.models import School
import uuid

User = get_user_model()

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='notifications')
    
    title = models.CharField(max_length=200)
    body = models.TextField()
    notification_type = models.CharField(
        max_length=50,
        choices=[
            ('academic', 'Academic Update'),
            ('behavior', 'Behavior Report'),
            ('payment', 'Payment Reminder'),
            ('general', 'General Announcement')
        ]
    )
    
    target_users = models.ManyToManyField(User, related_name='notifications')
    sent_via_fcm = models.BooleanField(default=False)
    sent_via_email = models.BooleanField(default=False)
    
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications_notification'
        ordering = ['-created_at']

class NotificationDelivery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='deliveries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_deliveries')
    
    delivered_via_fcm = models.BooleanField(default=False)
    delivered_via_email = models.BooleanField(default=False)
    fcm_message_id = models.CharField(max_length=100, blank=True)
    fcm_error = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications_notification_delivery'
        unique_together = ['notification', 'user']
