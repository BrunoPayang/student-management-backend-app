import os
import uuid
import shutil
from datetime import datetime
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

class LocalStorageService:
    """Local file storage service for development/testing (free alternative to Firebase)"""
    
    def __init__(self):
        self.base_path = os.path.join(settings.MEDIA_ROOT, 'uploads')
        self.allowed_types = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.txt']
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # Create uploads directory if it doesn't exist
        os.makedirs(self.base_path, exist_ok=True)
    
    def upload_file(self, file: UploadedFile, folder: str) -> dict:
        """Upload file to local storage"""
        self._validate_file(file)
        
        # Generate unique filename
        filename = self._generate_filename(file.name)
        
        # Create folder path
        folder_path = os.path.join(self.base_path, folder)
        os.makedirs(folder_path, exist_ok=True)
        
        # Full file path
        file_path = os.path.join(folder_path, filename)
        
        # Save file using Django's storage
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Generate public URL (for local development)
        public_url = f"/media/uploads/{folder}/{filename}"
        
        return {
            'url': public_url,
            'path': f"uploads/{folder}/{filename}",
            'filename': filename,
            'size': file.size,
            'content_type': file.content_type,
            'local_path': file_path
        }
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from local storage"""
        try:
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            return False
        except Exception:
            return False
    
    def get_file_url(self, file_path: str) -> str:
        """Get public URL for file"""
        return f"/media/{file_path}"
    
    def _validate_file(self, file: UploadedFile):
        """Validate file size and type"""
        if file.size > self.max_file_size:
            raise ValueError(f"File size exceeds 10MB limit")
        
        file_extension = os.path.splitext(file.name)[1].lower()
        if file_extension not in self.allowed_types:
            raise ValueError(f"File type {file_extension} not allowed")
    
    def _generate_filename(self, original_name: str) -> str:
        """Generate unique filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        extension = os.path.splitext(original_name)[1]
        return f"{timestamp}_{unique_id}{extension}"
    
    def cleanup_old_files(self, days_old: int = 30):
        """Clean up old files (optional maintenance)"""
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.getctime(file_path) < cutoff_date.timestamp():
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass
