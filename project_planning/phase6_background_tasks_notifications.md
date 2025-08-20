# Phase 6: Background Tasks & Notifications (Week 3 - Days 1-2)

## Overview
Implement Celery for asynchronous task processing, enhanced notification delivery, and background job management for the school management system.

## Task 6.1: Celery Setup & Configuration

### Step 1: Install Dependencies
```bash
pip install celery[redis] redis django-celery-results django-celery-beat
```

### Step 2: Celery Configuration
**schoolconnect/celery.py**
```python
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schoolconnect.settings.development')

app = Celery('schoolconnect')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

### Step 3: Celery Settings
**schoolconnect/settings/base.py**
```python
# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'send-scheduled-notifications': {
        'task': 'apps.notifications.tasks.send_scheduled_notifications',
        'schedule': 300.0,  # Every 5 minutes
    },
    'cleanup-old-files': {
        'task': 'apps.files.tasks.cleanup_old_files',
        'schedule': 86400.0,  # Daily
    },
    'generate-monthly-reports': {
        'task': 'apps.reports.tasks.generate_monthly_reports',
        'schedule': 2592000.0,  # Monthly
    },
}

# Celery Results
CELERY_RESULT_EXPIRES = 3600  # 1 hour
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
```

### Step 4: Update Requirements
**requirements/base.txt**
```
celery[redis]>=5.3.0
redis>=4.5.0
django-celery-results>=2.5.0
django-celery-beat>=2.5.0
```

## Task 6.2: Enhanced Notification System

### Step 1: Notification Tasks
**apps/notifications/tasks.py**
```python
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, NotificationDelivery, ScheduledNotification
from .services import NotificationService
from .fcm_service import FCMService

@shared_task(bind=True, max_retries=3)
def send_notification_task(self, notification_id):
    """Send notification asynchronously"""
    try:
        notification = Notification.objects.get(id=notification_id)
        service = NotificationService()
        results = service.send_notification(notification)
        
        # Update notification status
        notification.sent_via_fcm = results['fcm_sent'] > 0
        notification.sent_via_email = results['email_sent'] > 0
        notification.sent_at = timezone.now()
        notification.save()
        
        return results
        
    except Notification.DoesNotExist:
        raise self.retry(countdown=60, max_retries=3)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60, max_retries=3)

@shared_task
def send_bulk_notification_task(user_ids, title, body, notification_type, school_id, data=None):
    """Send bulk notifications asynchronously"""
    from apps.authentication.models import User
    from apps.schools.models import School
    
    try:
        school = School.objects.get(id=school_id)
        users = User.objects.filter(id__in=user_ids, school=school)
        
        # Create notification
        notification = Notification.objects.create(
            school=school,
            title=title,
            body=body,
            notification_type=notification_type,
            data=data or {}
        )
        
        # Add target users
        notification.target_users.set(users)
        
        # Send asynchronously
        send_notification_task.delay(str(notification.id))
        
        return {
            'notification_id': str(notification.id),
            'target_users': len(users),
            'status': 'queued'
        }
        
    except Exception as e:
        return {'error': str(e), 'status': 'failed'}

@shared_task
def send_scheduled_notifications():
    """Process scheduled notifications"""
    now = timezone.now()
    scheduled = ScheduledNotification.objects.filter(
        scheduled_time__lte=now,
        sent=False
    )
    
    for scheduled_notif in scheduled:
        try:
            # Create and send notification
            notification = Notification.objects.create(
                school=scheduled_notif.school,
                title=scheduled_notif.title,
                body=scheduled_notif.body,
                notification_type=scheduled_notif.notification_type,
                data=scheduled_notif.data
            )
            
            # Add target users
            if scheduled_notif.target_users.exists():
                notification.target_users.set(scheduled_notif.target_users.all())
            
            # Send notification
            send_notification_task.delay(str(notification.id))
            
            # Mark as sent
            scheduled_notif.sent = True
            scheduled_notif.sent_at = now
            scheduled_notif.save()
            
        except Exception as e:
            print(f"Error processing scheduled notification {scheduled_notif.id}: {e}")

@shared_task
def retry_failed_deliveries():
    """Retry failed notification deliveries"""
    failed_deliveries = NotificationDelivery.objects.filter(
        delivered_via_fcm=False,
        delivered_via_email=False,
        fcm_error__isnull=False
    )
    
    for delivery in failed_deliveries:
        try:
            # Retry FCM delivery
            if delivery.notification.sent_via_fcm:
                fcm_service = FCMService()
                success = fcm_service.send_to_token(
                    delivery.user.fcm_token,
                    delivery.notification.title,
                    delivery.notification.body,
                    delivery.notification.data
                )
                
                if success:
                    delivery.delivered_via_fcm = True
                    delivery.fcm_error = ''
                    delivery.delivered_at = timezone.now()
                    delivery.save()
                    
        except Exception as e:
            delivery.fcm_error = str(e)
            delivery.save()
```

### Step 2: Scheduled Notification Model
**apps/notifications/models.py** (add to existing)
```python
class ScheduledNotification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='scheduled_notifications')
    
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
    
    target_users = models.ManyToManyField(User, related_name='scheduled_notifications')
    scheduled_time = models.DateTimeField()
    data = models.JSONField(default=dict, blank=True)
    
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications_scheduled_notification'
        ordering = ['scheduled_time']
        indexes = [
            models.Index(fields=['school', 'scheduled_time']),
            models.Index(fields=['scheduled_time', 'sent'])
        ]
    
    def __str__(self):
        return f"{self.title} - {self.scheduled_time}"
```

### Step 3: Enhanced Notification Service
**apps/notifications/services.py** (update existing)
```python
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, NotificationDelivery, ScheduledNotification
from .fcm_service import FCMService
from .tasks import send_notification_task

class NotificationService:
    def __init__(self):
        self.fcm_service = FCMService()
    
    def send_notification(self, notification: Notification) -> dict:
        """Send notification via multiple channels"""
        results = {
            'fcm_sent': 0,
            'email_sent': 0,
            'total_targets': notification.target_users.count()
        }
        
        for user in notification.target_users.all():
            delivery, created = NotificationDelivery.objects.get_or_create(
                notification=notification,
                user=user
            )
            
            # Send via FCM
            if hasattr(user, 'fcm_token') and user.fcm_token and getattr(user, 'receive_push', True):
                fcm_success = self._send_fcm_to_user(user, notification)
                if fcm_success:
                    delivery.delivered_via_fcm = True
                    results['fcm_sent'] += 1
            
            # Send via email
            if user.email and getattr(user, 'receive_email', True):
                email_success = self._send_email_to_user(user, notification)
                if email_success:
                    delivery.delivered_via_email = True
                    results['email_sent'] += 1
            
            delivery.delivered_at = timezone.now()
            delivery.save()
        
        notification.sent_via_fcm = results['fcm_sent'] > 0
        notification.sent_via_email = results['email_sent'] > 0
        notification.sent_at = timezone.now()
        notification.save()
        
        return results
    
    def send_bulk_notification(self, users, title, body, notification_type, school, data=None):
        """Send bulk notification asynchronously"""
        # Queue the task
        task_result = send_bulk_notification_task.delay(
            user_ids=[str(user.id) for user in users],
            title=title,
            body=body,
            notification_type=notification_type,
            school_id=str(school.id),
            data=data or {}
        )
        
        return {
            'task_id': task_result.id,
            'status': 'queued',
            'message': 'Bulk notification queued for processing'
        }
    
    def schedule_notification(self, title, body, notification_type, target_users, 
                            scheduled_time, school, data=None):
        """Schedule a notification for future delivery"""
        scheduled = ScheduledNotification.objects.create(
            school=school,
            title=title,
            body=body,
            notification_type=notification_type,
            scheduled_time=scheduled_time,
            data=data or {}
        )
        
        # Add target users
        if target_users:
            scheduled.target_users.set(target_users)
        
        return scheduled
    
    def _send_fcm_to_user(self, user, notification):
        """Send FCM notification to user"""
        try:
            data = {
                'notification_id': str(notification.id),
                'type': notification.notification_type,
                'school_id': str(notification.school.id)
            }
            
            return self.fcm_service.send_to_token(
                user.fcm_token,
                notification.title,
                notification.body,
                data
            )
        except Exception as e:
            print(f"FCM send error for user {user.id}: {e}")
            return False
    
    def _send_email_to_user(self, user, notification):
        """Send email notification to user"""
        try:
            subject = f"[{notification.school.name}] {notification.title}"
            body = f"{notification.body}\n\nSent: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )
            return True
        except Exception as e:
            print(f"Email send error for user {user.id}: {e}")
            return False
```

## Task 6.3: File Management Tasks

### Step 1: File Processing Tasks
**apps/files/tasks.py**
```python
from celery import shared_task
from django.utils import timezone
from django.core.files.storage import default_storage
from datetime import timedelta
import os
from .models import FileUpload
from .services import FirebaseStorageService

@shared_task
def process_file_upload(file_upload_id):
    """Process file upload asynchronously"""
    try:
        file_upload = FileUpload.objects.get(id=file_upload_id)
        
        # Process file based on type
        if file_upload.file_type == 'transcript':
            process_transcript_file.delay(str(file_upload.id))
        elif file_upload.file_type == 'behavior_report':
            process_behavior_report.delay(str(file_upload.id))
        elif file_upload.file_type == 'payment_receipt':
            process_payment_receipt.delay(str(file_upload.id))
        
        return {'status': 'success', 'file_id': str(file_upload.id)}
        
    except FileUpload.DoesNotExist:
        return {'status': 'error', 'message': 'File not found'}

@shared_task
def cleanup_old_files():
    """Clean up old, deleted files"""
    # Find files marked as deleted more than 30 days ago
    cutoff_date = timezone.now() - timedelta(days=30)
    old_deleted_files = FileUpload.objects.filter(
        is_deleted=True,
        uploaded_at__lt=cutoff_date
    )
    
    firebase_service = FirebaseStorageService()
    cleaned_count = 0
    
    for file_upload in old_deleted_files:
        try:
            # Delete from Firebase
            firebase_service.delete_file(file_upload.firebase_path)
            
            # Delete database record
            file_upload.delete()
            cleaned_count += 1
            
        except Exception as e:
            print(f"Error cleaning up file {file_upload.id}: {e}")
    
    return {'cleaned_count': cleaned_count}

@shared_task
def generate_file_thumbnails(file_upload_id):
    """Generate thumbnails for image files"""
    try:
        file_upload = FileUpload.objects.get(id=file_upload_id)
        
        # Only process image files
        if file_upload.content_type.startswith('image/'):
            # Generate thumbnail logic here
            # This would integrate with PIL/Pillow for image processing
            pass
        
        return {'status': 'success', 'file_id': str(file_upload.id)}
        
    except FileUpload.DoesNotExist:
        return {'status': 'error', 'message': 'File not found'}

@shared_task
def process_transcript_file(file_upload_id):
    """Process academic transcript files"""
    # OCR processing, data extraction, etc.
    pass

@shared_task
def process_behavior_report(file_upload_id):
    """Process behavior report files"""
    # Text extraction, categorization, etc.
    pass

@shared_task
def process_payment_receipt(file_upload_id):
    """Process payment receipt files"""
    # Receipt data extraction, validation, etc.
    pass
```

## Task 6.4: Report Generation Tasks

### Step 1: Report Tasks
**apps/reports/tasks.py**
```python
from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Avg, Sum
from datetime import datetime, timedelta
from apps.schools.models import School
from apps.students.models import Student, BehaviorReport, PaymentRecord
from apps.notifications.models import Notification

@shared_task
def generate_monthly_reports():
    """Generate monthly reports for all schools"""
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    for school in School.objects.all():
        try:
            generate_school_monthly_report.delay(str(school.id), current_month, current_year)
        except Exception as e:
            print(f"Error queuing report for school {school.id}: {e}")

@shared_task
def generate_school_monthly_report(school_id, month, year):
    """Generate monthly report for a specific school"""
    try:
        school = School.objects.get(id=school_id)
        
        # Calculate statistics
        stats = {
            'total_students': Student.objects.filter(school=school).count(),
            'new_enrollments': Student.objects.filter(
                school=school,
                enrollment_date__month=month,
                enrollment_date__year=year
            ).count(),
            'behavior_incidents': BehaviorReport.objects.filter(
                student__school=school,
                incident_date__month=month,
                incident_date__year=year
            ).count(),
            'total_payments': PaymentRecord.objects.filter(
                student__school=school,
                payment_date__month=month,
                payment_date__year=year
            ).aggregate(total=Sum('amount'))['total'] or 0,
            'notifications_sent': Notification.objects.filter(
                school=school,
                created_at__month=month,
                created_at__year=year
            ).count()
        }
        
        # Generate report file (PDF, Excel, etc.)
        # This would integrate with report generation libraries
        
        return {
            'status': 'success',
            'school_id': str(school.id),
            'month': month,
            'year': year,
            'stats': stats
        }
        
    except School.DoesNotExist:
        return {'status': 'error', 'message': 'School not found'}

@shared_task
def generate_student_progress_report(student_id):
    """Generate individual student progress report"""
    try:
        student = Student.objects.get(id=student_id)
        
        # Gather student data
        behavior_reports = BehaviorReport.objects.filter(student=student)
        payment_records = PaymentRecord.objects.filter(student=student)
        
        # Generate report
        # This would create a comprehensive student report
        
        return {
            'status': 'success',
            'student_id': str(student.id),
            'report_generated': True
        }
        
    except Student.DoesNotExist:
        return {'status': 'error', 'message': 'Student not found'}

@shared_task
def cleanup_old_reports():
    """Clean up old generated reports"""
    # Remove reports older than 1 year
    cutoff_date = timezone.now() - timedelta(days=365)
    
    # This would clean up report files and database records
    return {'status': 'success', 'message': 'Old reports cleaned up'}
```

## Task 6.5: Task Monitoring & Management

### Step 1: Task Views
**apps/tasks/views.py**
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_celery_results.models import TaskResult
from celery import current_app
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    list=extend_schema(
        summary="List Task Results",
        description="Retrieve a list of completed task results",
        tags=['tasks']
    ),
    retrieve=extend_schema(
        summary="Get Task Result",
        description="Retrieve detailed information about a specific task result",
        tags=['tasks']
    )
)
class TaskResultViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for monitoring task results"""
    queryset = TaskResult.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by user's school"""
        if hasattr(self.request.user, 'school'):
            return TaskResult.objects.filter(
                task_name__startswith=f'school_{self.request.user.school.id}'
            )
        return TaskResult.objects.none()
    
    @extend_schema(
        summary="Get Active Tasks",
        description="Get list of currently running tasks",
        tags=['tasks']
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active tasks"""
        try:
            inspector = current_app.control.inspect()
            active_tasks = inspector.active()
            
            return Response({
                'active_tasks': active_tasks or {},
                'total_active': sum(len(tasks) for tasks in (active_tasks or {}).values())
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Get Worker Status",
        description="Get status of Celery workers",
        tags=['tasks']
    )
    @action(detail=False, methods=['get'])
    def workers(self, request):
        """Get worker status"""
        try:
            inspector = current_app.control.inspect()
            stats = inspector.stats()
            ping = inspector.ping()
            
            return Response({
                'workers': stats or {},
                'ping': ping or {},
                'total_workers': len(stats or {})
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
```

### Step 2: Task URLs
**apps/tasks/urls.py**
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'task-results', views.TaskResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

## Task 6.6: Environment Configuration

### Step 1: Environment Variables
**.env.template** (add to existing)
```bash
# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Task Configuration
CELERY_TASK_ALWAYS_EAGER=False
CELERY_TASK_EAGER_PROPAGATES=True
```

### Step 2: Development Settings
**schoolconnect/settings/development.py** (add to existing)
```python
# Celery Configuration for Development
CELERY_TASK_ALWAYS_EAGER = True  # Run tasks synchronously in development
CELERY_TASK_EAGER_PROPAGATES = True

# Redis Configuration
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
```

## Validation Checklist

### Celery Setup
- [ ] Celery worker processes running
- [ ] Redis broker accessible
- [ ] Task discovery working
- [ ] Beat scheduler configured

### Background Tasks
- [ ] Notification sending tasks working
- [ ] File processing tasks working
- [ ] Report generation tasks working
- [ ] Task retry mechanism working

### Enhanced Notifications
- [ ] Asynchronous notification delivery
- [ ] Scheduled notifications working
- [ ] Bulk notification queuing
- [ ] Failed delivery retry

### Task Monitoring
- [ ] Task result tracking
- [ ] Worker status monitoring
- [ ] Active task monitoring
- [ ] Error handling and logging

### Performance
- [ ] Tasks not blocking API responses
- [ ] Proper task queuing
- [ ] Resource usage optimization
- [ ] Scalability considerations

## Next Steps
After completing Phase 6, proceed to Phase 7: Advanced Features & Optimization to implement caching, search functionality, and performance improvements.

## Running the System

### Start Redis
```bash
redis-server
```

### Start Celery Worker
```bash
celery -A schoolconnect worker -l info
```

### Start Celery Beat (Scheduler)
```bash
celery -A schoolconnect beat -l info
```

### Monitor Tasks
```bash
celery -A schoolconnect flower  # Web-based monitoring
```

This phase establishes a robust foundation for handling background operations, ensuring the system can scale and handle complex operations without blocking user interactions.
