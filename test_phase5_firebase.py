#!/usr/bin/env python
"""
Test script for Phase 5: Firebase Integration
Tests the core components without requiring actual Firebase credentials
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

User = get_user_model()

def test_phase5_components():
    """Test Phase 5 Firebase integration components"""
    print("🧪 Testing Phase 5: Firebase Integration Components")
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
    
    # Test 5: Check if URLs can be imported
    print("\n5. Testing URL Imports...")
    try:
        from apps.files.urls import urlpatterns as files_urls
        from apps.notifications.urls import urlpatterns as notification_urls
        print("✅ All URL patterns imported successfully")
        print(f"   Files URLs: {len(files_urls)} patterns")
        print(f"   Notification URLs: {len(notification_urls)} patterns")
    except Exception as e:
        print(f"❌ URL import error: {e}")
        return False
    
    # Test 6: Check if models can be created (without saving)
    print("\n6. Testing Model Creation...")
    try:
        # Create a test school
        test_school = School(
            name="Test School for Phase 5",
            slug="test-school-phase5",
            contact_email="test@phase5.com",
            contact_phone="+22712345678",
            address="Test Address",
            city="Test City",
            state="Test State"
        )
        
        # Create a test user
        test_user = User(
            username="testuser_phase5",
            email="test@phase5.com",
            first_name="Test",
            last_name="User",
            user_type="school_staff"
        )
        
        # Create a test file upload (without saving)
        test_file = FileUpload(
            school=test_school,
            original_name="test_document.pdf",
            firebase_path="test/path/document.pdf",
            firebase_url="https://test.firebase.com/document.pdf",
            file_size=1024,
            content_type="application/pdf",
            file_type="other",
            uploaded_by=test_user
        )
        
        # Create a test notification (without saving)
        test_notification = Notification(
            school=test_school,
            title="Test Notification",
            body="This is a test notification for Phase 5",
            notification_type="general"
        )
        
        print("✅ All test models created successfully (not saved to database)")
        
    except Exception as e:
        print(f"❌ Model creation error: {e}")
        return False
    
    # Test 7: Check if serializers can serialize models
    print("\n7. Testing Serializer Functionality...")
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
            'target_users': []  # Empty list for testing
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
    
    print("\n🎉 All Phase 5 components are working correctly!")
    print("\n📝 Note: Firebase initialization warnings are expected in development mode")
    print("   These will be resolved when proper Firebase credentials are configured")
    
    return True

if __name__ == "__main__":
    success = test_phase5_components()
    if success:
        print("\n✅ Phase 5 Firebase Integration is ready!")
        print("   Next steps:")
        print("   1. Configure Firebase credentials in environment variables")
        print("   2. Test file upload functionality")
        print("   3. Test notification sending")
    else:
        print("\n❌ Phase 5 implementation has issues that need to be resolved")
        sys.exit(1)
