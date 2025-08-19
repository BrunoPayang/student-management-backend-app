# Phase 5: Firebase Integration (Week 2 - Days 4-5)

## Overview
Implement Firebase Storage for file uploads/downloads and Firebase Cloud Messaging for push notifications.

## Task 5.1: Firebase Storage Setup

### Step 1: Install Dependencies
```bash
pip install firebase-admin python-magic
```

### Step 2: Firebase Configuration
**apps/files/firebase_config.py**
```python
import firebase_admin
from firebase_admin import credentials, storage
from django.conf import settings

class FirebaseConfig:
    def __init__(self):
        self.bucket = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        try:
            cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)
            if cred_path:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': settings.FIREBASE_STORAGE_BUCKET
                })
            else:
                firebase_admin.initialize_app()
            
            self.bucket = storage.bucket()
        except Exception as e:
            print(f"Firebase initialization error: {e}")
            self.bucket = None

firebase_config = FirebaseConfig()
```

### Step 3: File Upload Service
**apps/files/services.py**
```python
import os
import uuid
from datetime import datetime
from django.core.files.uploadedfile import UploadedFile
from .firebase_config import firebase_config

class FirebaseStorageService:
    def __init__(self):
        self.bucket = firebase_config.get_bucket()
        self.allowed_types = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif']
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    def upload_file(self, file: UploadedFile, folder: str) -> dict:
        if not self.bucket:
            raise Exception("Firebase not initialized")
        
        self._validate_file(file)
        filename = self._generate_filename(file.name)
        blob_path = f"{folder}/{filename}"
        blob = self.bucket.blob(blob_path)
        
        blob.upload_from_file(file, content_type=file.content_type)
        blob.make_public()
        
        return {
            'url': blob.public_url,
            'path': blob_path,
            'filename': filename,
            'size': file.size,
            'content_type': file.content_type
        }
    
    def _validate_file(self, file: UploadedFile):
        if file.size > self.max_file_size:
            raise ValueError(f"File size exceeds 10MB limit")
        
        file_extension = os.path.splitext(file.name)[1].lower()
        if file_extension not in self.allowed_types:
            raise ValueError(f"File type {file_extension} not allowed")
    
    def _generate_filename(self, original_name: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        extension = os.path.splitext(original_name)[1]
        return f"{timestamp}_{unique_id}{extension}"
```

### Step 4: File Upload Model
**apps/files/models.py**
```python
from django.db import models
from django.contrib.auth import get_user_model
from apps.schools.models import School
import uuid

User = get_user_model()

class FileUpload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='files')
    
    original_name = models.CharField(max_length=255)
    firebase_path = models.CharField(max_length=500)
    firebase_url = models.URLField()
    file_size = models.BigIntegerField()
    content_type = models.CharField(max_length=100)
    
    file_type = models.CharField(
        max_length=50,
        choices=[
            ('transcript', 'Academic Transcript'),
            ('behavior_report', 'Behavior Report'),
            ('payment_receipt', 'Payment Receipt'),
            ('student_document', 'Student Document'),
            ('other', 'Other')
        ]
    )
    
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    is_public = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploads')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'files_file_upload'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['school', 'file_type']),
            models.Index(fields=['uploaded_by', 'uploaded_at'])
        ]
    
    def __str__(self):
        return f"{self.original_name} ({self.file_type})"
    
    @property
    def file_size_mb(self):
        return round(self.file_size / (1024 * 1024), 2)
```

## Task 5.2: Firebase Cloud Messaging

### Step 1: FCM Service
**apps/notifications/fcm_service.py**
```python
import firebase_admin
from firebase_admin import messaging

class FCMService:
    def __init__(self):
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        try:
            if not firebase_admin._apps:
                firebase_admin.initialize_app()
        except Exception as e:
            print(f"FCM initialization error: {e}")
    
    def send_to_token(self, token: str, title: str, body: str, data: dict = None) -> bool:
        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=data or {},
                token=token
            )
            messaging.send(message)
            return True
        except Exception as e:
            print(f"FCM send error: {e}")
            return False
    
    def send_to_topic(self, topic: str, title: str, body: str, data: dict = None) -> bool:
        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=data or {},
                topic=topic
            )
            messaging.send(message)
            return True
        except Exception as e:
            print(f"FCM topic send error: {e}")
            return False
```

### Step 2: Notification Models
**apps/notifications/models.py**
```python
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
```

### Step 3: Notification Service
**apps/notifications/services.py**
```python
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, NotificationDelivery
from .fcm_service import FCMService

class NotificationService:
    def __init__(self):
        self.fcm_service = FCMService()
    
    def send_notification(self, notification: Notification) -> dict:
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
            if user.fcm_token and user.receive_push:
                fcm_success = self._send_fcm_to_user(user, notification)
                if fcm_success:
                    delivery.delivered_via_fcm = True
                    results['fcm_sent'] += 1
            
            # Send via email
            if user.email and user.receive_email:
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
    
    def _send_fcm_to_user(self, user, notification):
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

## Task 5.3: Settings and Configuration

### Step 1: Firebase Settings
**schoolconnect/settings/base.py**
```python
# Firebase Configuration
FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', '')
FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET', '')
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', '')

# File Upload Settings
ALLOWED_FILE_TYPES = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif']
MAX_FILE_SIZE_MB = 10

# Notification Settings
ENABLE_FCM_NOTIFICATIONS = os.getenv('ENABLE_FCM_NOTIFICATIONS', 'True').lower() == 'true'
ENABLE_EMAIL_NOTIFICATIONS = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'True').lower() == 'true'
```

### Step 2: Update Requirements
**requirements/base.txt**
```
firebase-admin>=6.2.0
python-magic>=0.4.27
```

## Validation Checklist

### Firebase Storage
- [ ] Firebase SDK properly initialized
- [ ] File upload service working
- [ ] File type validation implemented
- [ ] File size limits enforced
- [ ] Secure file URLs generated

### Firebase Cloud Messaging
- [ ] FCM service initialized
- [ ] Push notifications sent successfully
- [ ] Notification delivery tracking
- [ ] Error handling implemented

### File Management
- [ ] File upload endpoints working
- [ ] File download endpoints working
- [ ] File categorization
- [ ] Access control implemented

### Notification System
- [ ] Notification creation endpoints
- [ ] Multi-channel delivery (FCM, Email)
- [ ] Notification preferences respected
- [ ] Delivery tracking

## Next Steps
After completing Phase 5, proceed to Phase 6: Background Tasks & Notifications to implement Celery for asynchronous processing.
