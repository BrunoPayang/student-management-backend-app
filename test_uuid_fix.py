#!/usr/bin/env python
"""
Test script to verify the UUID handling fix for notifications.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schoolconnect.settings.development')
django.setup()

from apps.notifications.models import Notification
from apps.authentication.models import User
from apps.schools.models import School
from apps.notifications.serializers import NotificationCreateSerializer
from rest_framework.test import APIRequestFactory

def test_uuid_handling():
    """Test that UUID school IDs are handled correctly"""
    
    print("🔍 Testing UUID Handling Fix...")
    print("=" * 50)
    
    # Get the first school for testing
    try:
        school = School.objects.first()
        if not school:
            print("❌ No schools found in database")
            return
        print(f"🏫 Using school: {school.name} (ID: {school.id})")
        print(f"🏫 School ID type: {type(school.id)}")
    except Exception as e:
        print(f"❌ Error getting school: {e}")
        return
    
    # Test 1: Test the serializer with UUID string
    print("\n📝 Test 1: Testing serializer with UUID string")
    try:
        # Create a mock request context
        factory = APIRequestFactory()
        request = factory.post('/')
        
        # Create serializer context
        context = {'request': request}
        
        # Test data with UUID string
        test_data = {
            'title': 'Test UUID Fix',
            'body': 'This should work with UUID school ID',
            'notification_type': 'general',
            'school': str(school.id),  # UUID as string
            'data': {}
        }
        
        print(f"📤 Input data: {test_data}")
        
        # Create serializer
        serializer = NotificationCreateSerializer(data=test_data, context=context)
        
        if serializer.is_valid():
            print("✅ Serializer validation passed")
            
            # Create the notification
            notification = serializer.save()
            print(f"✅ Notification created with ID: {notification.id}")
            print(f"✅ School assigned: {notification.school.id}")
            print(f"✅ Target users count: {notification.target_users.count()}")
            
            # Check if target users were auto-assigned
            if notification.target_users.exists():
                print("✅ Target users were auto-assigned")
                for user in notification.target_users.all()[:3]:  # Show first 3
                    print(f"   • {user.full_name} ({user.user_type})")
            else:
                print("⚠️  No target users assigned - this might indicate an issue")
                
        else:
            print("❌ Serializer validation failed:")
            print(f"   Errors: {serializer.errors}")
            
    except Exception as e:
        print(f"❌ Error testing serializer: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Test direct model creation
    print("\n📝 Test 2: Testing direct model creation")
    try:
        notification2 = Notification.objects.create(
            school=school,
            title="Test Direct Creation",
            body="Testing direct model creation",
            notification_type="general"
        )
        
        # Call auto-target method
        parent_count = notification2.auto_target_all_parents()
        print(f"✅ Direct notification created with ID: {notification2.id}")
        print(f"✅ Auto-targeted {parent_count} parents")
        print(f"✅ Total target users: {notification2.target_users.count()}")
        
    except Exception as e:
        print(f"❌ Error in direct creation: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")

def show_database_info():
    """Show current database information"""
    print("🔍 Database Information")
    print("=" * 30)
    
    try:
        school_count = School.objects.count()
        user_count = User.objects.count()
        parent_count = User.objects.filter(user_type='parent').count()
        staff_count = User.objects.filter(user_type='school_staff').count()
        admin_count = User.objects.filter(user_type='admin').count()
        notification_count = Notification.objects.count()
        
        print(f"🏫 Schools: {school_count}")
        print(f"👥 Total Users: {user_count}")
        print(f"👨‍👩‍👧‍👦 Parents: {parent_count}")
        print(f"👨‍🏫 Staff: {staff_count}")
        print(f"👨‍💼 Admins: {admin_count}")
        print(f"📢 Notifications: {notification_count}")
        
        # Show school details
        schools = School.objects.all()[:3]
        for school in schools:
            print(f"   • {school.name}: {school.id} ({type(school.id)})")
        
    except Exception as e:
        print(f"❌ Error getting database info: {e}")

if __name__ == "__main__":
    print("🚀 SchoolConnect UUID Fix Test")
    print("=" * 50)
    
    # Show database info
    show_database_info()
    print()
    
    # Test UUID handling
    test_uuid_handling()
    
    print("\n💡 Next Steps:")
    print("1. Test the API endpoint with your UUID school ID")
    print("2. Check that target users are automatically assigned")
    print("3. Verify the response shows target_user_ids populated")
    print("4. Use the admin interface to monitor target users")

