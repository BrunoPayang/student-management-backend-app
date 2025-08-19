import os
import uuid
from datetime import datetime
from django.core.files.uploadedfile import UploadedFile
from .firebase_config import FirebaseConfig
from .local_storage_service import LocalStorageService

class FirebaseStorageService:
    def __init__(self):
        self.firebase_config = FirebaseConfig()
        self.local_storage = LocalStorageService()
        self.use_local_storage = self.firebase_config.is_using_local_storage()

    def upload_file(self, file: UploadedFile, folder: str) -> dict:
        """Upload file to storage (Firebase or local)"""
        if self.use_local_storage:
            print("📁 Using local storage for file upload")
            return self.local_storage.upload_file(file, folder)
        else:
            print("🔥 Using Firebase storage for file upload")
            return self._upload_to_firebase(file, folder)

    def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        if self.use_local_storage:
            return self.local_storage.delete_file(file_path)
        else:
            return self._delete_from_firebase(file_path)

    def get_file_url(self, file_path: str) -> str:
        """Get public URL for file"""
        if self.use_local_storage:
            return self.local_storage.get_file_url(file_path)
        else:
            return self._get_firebase_url(file_path)

    def _upload_to_firebase(self, file: UploadedFile, folder: str) -> dict:
        """Upload file to Firebase Storage"""
        if not self.firebase_config.bucket:
            raise Exception("Firebase not initialized")

        self._validate_file(file)
        filename = self._generate_filename(file.name)
        blob_path = f"{folder}/{filename}"
        blob = self.firebase_config.bucket.blob(blob_path)

        blob.upload_from_file(file, content_type=file.content_type)
        blob.make_public()

        return {
            'url': blob.public_url,
            'path': blob_path,
            'filename': filename,
            'size': file.size,
            'content_type': file.content_type
        }

    def _delete_from_firebase(self, file_path: str) -> bool:
        """Delete file from Firebase Storage"""
        if not self.firebase_config.bucket:
            return False

        try:
            blob = self.firebase_config.bucket.blob(file_path)
            blob.delete()
            return True
        except Exception:
            return False

    def _get_firebase_url(self, file_path: str) -> str:
        """Get public URL for file from Firebase"""
        if not self.firebase_config.bucket:
            return None

        blob = self.firebase_config.bucket.blob(file_path)
        return blob.public_url

    def _validate_file(self, file: UploadedFile):
        """Validate file size and type"""
        if file.size > self.local_storage.max_file_size:
            raise ValueError(f"File size exceeds 10MB limit")

        file_extension = os.path.splitext(file.name)[1].lower()
        if file_extension not in self.local_storage.allowed_types:
            raise ValueError(f"File type {file_extension} not allowed")

    def _generate_filename(self, original_name: str) -> str:
        """Generate unique filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        extension = os.path.splitext(original_name)[1]
        return f"{timestamp}_{unique_id}{extension}"

    def get_storage_type(self) -> str:
        """Get current storage type being used"""
        return "local" if self.use_local_storage else "firebase"
