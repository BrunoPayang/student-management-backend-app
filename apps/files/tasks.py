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
    return {'status': 'success', 'file_id': file_upload_id, 'type': 'transcript'}

@shared_task
def process_behavior_report(file_upload_id):
    """Process behavior report files"""
    # Text extraction, categorization, etc.
    return {'status': 'success', 'file_id': file_upload_id, 'type': 'behavior_report'}

@shared_task
def process_payment_receipt(file_upload_id):
    """Process payment receipt files"""
    # Receipt data extraction, validation, etc.
    return {'status': 'success', 'file_id': file_upload_id, 'type': 'payment_receipt'}
