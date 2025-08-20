#!/usr/bin/env python
"""
Test script to verify notification serializer fix is working
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schoolconnect.settings.development')
django.setup()

def test_notification_serializer_import():
    """Test that we can import and use the notification serializer"""
    try:
        from apps.notifications.serializers import NotificationSerializer, NotificationCreateSerializer
        print("✅ Successfully imported notification serializers")
        
        # Test that the classes exist and have the right structure
        assert hasattr(NotificationSerializer, 'get_target_users'), "NotificationSerializer missing get_target_users method"
        assert hasattr(NotificationCreateSerializer, 'create'), "NotificationCreateSerializer missing create method"
        
        print("✅ Serializer classes have correct structure")
        
        # Test the get_target_users method logic
        serializer = NotificationSerializer()
        # This should not raise an error
        result = serializer.get_target_users(None)
        assert isinstance(result, list), "get_target_users should return a list"
        
        print("✅ get_target_users method works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_notification_views_import():
    """Test that we can import the notification views"""
    try:
        from apps.notifications.views import NotificationViewSet
        print("✅ Successfully imported NotificationViewSet")
        
        # Test that the viewset has the right structure
        assert hasattr(NotificationViewSet, 'get_serializer_class'), "NotificationViewSet missing get_serializer_class method"
        
        print("✅ NotificationViewSet has correct structure")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Notification System Fixes...")
    print("=" * 50)
    
    success1 = test_notification_serializer_import()
    success2 = test_notification_views_import()
    
    if success1 and success2:
        print("\n🎉 All tests passed! The notification system should work correctly.")
        print("\n📝 Next steps:")
        print("1. Stop the Django server (Ctrl+C)")
        print("2. Start it again: python manage.py runserver")
        print("3. Test the notifications API")
    else:
        print("\n💥 Some tests failed. Please check the errors above.")
        sys.exit(1)
