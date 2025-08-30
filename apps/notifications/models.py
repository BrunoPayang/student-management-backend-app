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
    sent_via_sms = models.BooleanField(default=False)
    
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications_notification'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.school.name}"
    
    @property
    def target_users_count(self):
        """Return count of target users"""
        return self.target_users.count()
    
    def get_target_users_info(self):
        """Get detailed information about target users"""
        users = self.target_users.all()
        return {
            'total_count': users.count(),
            'by_type': {
                'parent': users.filter(user_type='parent').count(),
                'school_staff': users.filter(user_type='school_staff').count(),
                'admin': users.filter(user_type='admin').count(),
            },
            'by_school': {
                'direct_school': users.filter(school=self.school).count(),
                'other_schools': users.exclude(school=self.school).count(),
                'no_school': users.filter(school__isnull=True).count(),
            }
        }
    
    def auto_target_all_parents(self):
        """Automatically target all parents in the school"""
        try:
            from apps.students.models import ParentStudent
            
            # Get direct school parents
            direct_parents = User.objects.filter(
                user_type='parent',
                school=self.school
            )
            
            # Get parents who have students in this school but don't have school set
            parent_students = ParentStudent.objects.filter(
                student__school=self.school
            ).values_list('parent_id', flat=True).distinct()
            
            additional_parents = User.objects.filter(
                id__in=parent_students,
                school__isnull=True
            )
            
            # Combine the querysets
            from django.db.models import Q
            all_parents = direct_parents | additional_parents
            
            # Set target users
            self.target_users.set(all_parents)
            return all_parents.count()
            
        except Exception as e:
            print(f"Error auto-targeting parents: {e}")
            return 0

class NotificationDelivery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='deliveries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_deliveries')
    
    delivered_via_fcm = models.BooleanField(default=False)
    delivered_via_email = models.BooleanField(default=False)
    delivered_via_sms = models.BooleanField(default=False)
    fcm_message_id = models.CharField(max_length=100, blank=True)
    fcm_error = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications_notification_delivery'
        unique_together = ['notification', 'user']
