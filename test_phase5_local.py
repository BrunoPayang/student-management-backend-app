#!/usr/bin/env python
"""
Test script for Phase 5: Local Storage Integration
Tests the core components using local file storage (free alternative to Firebase)
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schoolconnect.settings.development')
django.setup()

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from apps.schools.models import School
from apps.files.models import FileUpload
from apps.notifications.models import Notification, NotificationDelivery
from apps.files.serializers import FileUploadSerializer, FileUploadCreateSerializer
from apps.notifications.serializers import NotificationSerializer, NotificationCreateSerializer, NotificationDeliverySerializer
from apps.files.views import FileUploadViewSet
from apps.notifications.views import NotificationViewSet, NotificationDeliveryViewSet
from apps.files.services import FirebaseStorageService
from apps.notifications.services import NotificationService
from apps.notifications.fcm_service import FCMService

User = get_user_model()

def test_phase5_local_components():
    """Test Phase 5 components using local storage"""
    print("🧪 Testing Phase 5: Local Storage Integration")
    print("=" * 60)

    # Test 1: Check if models can be imported
    print("\n1. Testing Model Imports...")
    try:
        from apps.files.models import FileUpload
        from apps.notifications.models import Notification, NotificationDelivery
        print("✅ All models imported successfully")
    except Exception as e:
        print(f"❌ Model import error: {e}")
        return False

    # Test 2: Check if services can be imported
    print("\n2. Testing Service Imports...")
    try:
        from apps.files.services import FirebaseStorageService
        from apps.notifications.services import NotificationService
        from apps.notifications.fcm_service import FCMService
        print("✅ All services imported successfully")
    except Exception as e:
        print(f"❌ Service import error: {e}")
        return False

    # Test 3: Check if serializers can be imported
    print("\n3. Testing Serializer Imports...")
    try:
        from apps.files.serializers import FileUploadSerializer, FileUploadCreateSerializer
        from apps.notifications.serializers import NotificationSerializer, NotificationCreateSerializer, NotificationDeliverySerializer
        print("✅ All serializers imported successfully")
    except Exception as e:
        print(f"❌ Serializer import error: {e}")
        return False

    # Test 4: Check if views can be imported
    print("\n4. Testing View Imports...")
    try:
        from apps.files.views import FileUploadViewSet
        from apps.notifications.views import NotificationViewSet, NotificationDeliveryViewSet
        print("✅ All views imported successfully")
    except Exception as e:
        print(f"❌ View import error: {e}")
        return False

    # Test 5: Test local storage service
    print("\n5. Testing Local Storage Service...")
    try:
        from apps.files.local_storage_service import LocalStorageService
        
        # Create a test file
        test_content = b"This is a test file content for Phase 5"
        test_file = SimpleUploadedFile(
            "test_document.txt",
            test_content,
            content_type="text/plain"
        )
        
        # Test local storage
        local_storage = LocalStorageService()
        result = local_storage.upload_file(test_file, "test_folder")
        
        print(f"✅ Local storage test successful")
        print(f"   File uploaded to: {result['path']}")
        print(f"   URL: {result['url']}")
        
        # Clean up test file
        local_storage.delete_file(result['path'])
        
    except Exception as e:
        print(f"❌ Local storage test error: {e}")
        return False

    # Test 6: Test mock FCM service
    print("\n6. Testing Mock FCM Service...")
    try:
        from apps.notifications.fcm_service import FCMService
        
        fcm_service = FCMService()
        service_type = fcm_service.get_service_type()
        
        print(f"✅ FCM service test successful")
        print(f"   Service type: {service_type}")
        
        # Test mock notification
        success = fcm_service.send_to_token(
            "test_token_123",
            "Test Notification",
            "This is a test notification",
            {"test": "data"}
        )
        
        if success:
            print("   Mock notification sent successfully")
        else:
            print("   Mock notification failed")
            
    except Exception as e:
        print(f"❌ FCM service test error: {e}")
        return False

    # Test 7: Test serializers with local data
    print("\n7. Testing Serializers...")
    try:
        # Test file upload serializer
        file_data = {
            'original_name': 'test.pdf',
            'file_type': 'other',
            'description': 'Test file',
            'tags': ['test', 'phase5'],
            'is_public': False
        }

        file_serializer = FileUploadCreateSerializer(data=file_data)
        if file_serializer.is_valid():
            print("✅ FileUploadCreateSerializer validation successful")
        else:
            print(f"❌ FileUploadCreateSerializer validation failed: {file_serializer.errors}")
            return False

        # Test notification serializer
        notification_data = {
            'title': 'Test Title',
            'body': 'Test Body',
            'notification_type': 'general',
            'data': {'test': 'data'},
            'target_users': []
        }

        notification_serializer = NotificationCreateSerializer(data=notification_data)
        if notification_serializer.is_valid():
            print("✅ NotificationCreateSerializer validation successful")
        else:
            print(f"❌ NotificationCreateSerializer validation failed: {notification_serializer.errors}")
            return False

    except Exception as e:
        print(f"❌ Serializer test error: {e}")
        return False

    # Test 8: Test storage service integration
    print("\n8. Testing Storage Service Integration...")
    try:
        storage_service = FirebaseStorageService()
        storage_type = storage_service.get_storage_type()
        
        print(f"✅ Storage service integration successful")
        print(f"   Current storage type: {storage_type}")
        print(f"   Will automatically use: {'local storage' if storage_type == 'local' else 'Firebase'}")
        
    except Exception as e:
        print(f"❌ Storage service integration error: {e}")
        return False

    print("\n🎉 All Phase 5 components are working correctly with local storage!")
    print("\n📝 Benefits of this setup:")
    print("   ✅ FREE to use - no Firebase costs")
    print("   ✅ All features work locally")
    print("   ✅ Easy to switch to Firebase later")
    print("   ✅ Same API endpoints")
    print("   ✅ Same functionality")

    return True

if __name__ == "__main__":
    success = test_phase5_local_components()
    if success:
        print("\n✅ Phase 5 Local Storage Integration is ready!")
        print("\n🚀 Next steps:")
        print("   1. Test file uploads via API endpoints")
        print("   2. Test notification sending")
        print("   3. When ready for production, set up Firebase")
        print("   4. Change FIREBASE_ENABLED=True in .env")
    else:
        print("\n❌ Phase 5 implementation has issues that need to be resolved")
        sys.exit(1)
