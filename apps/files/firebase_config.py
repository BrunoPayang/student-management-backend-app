import firebase_admin
from firebase_admin import credentials, storage
from django.conf import settings

class FirebaseConfig:
    def __init__(self):
        self.bucket = None
        self.use_local_storage = True  # Default to local storage
        self._initialize_firebase()

    def _initialize_firebase(self):
        try:
            cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': settings.FIREBASE_STORAGE_BUCKET
                })
                self.bucket = storage.bucket()
                self.use_local_storage = False
                print("✅ Firebase initialized successfully")
            else:
                print("⚠️  Firebase credentials not found, using local storage")
                self.use_local_storage = True
        except Exception as e:
            print(f"⚠️  Firebase initialization error: {e}")
            print("🔄 Falling back to local storage")
            self.use_local_storage = True

    def get_bucket(self):
        """Get Firebase storage bucket"""
        return self.bucket

    def is_using_local_storage(self):
        """Check if using local storage"""
        return self.use_local_storage

# Import os for path checking
import os
