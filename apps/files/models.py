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
    tags = models.TextField(blank=True, help_text="Comma-separated tags (optional)")
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
