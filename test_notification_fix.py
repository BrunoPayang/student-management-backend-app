#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schoolconnect.settings.development')
django.setup()

from apps.notifications.models import Notification
from apps.authentication.models import User
from apps.schools.models import School

def test_notification_setup():
    print("=== NOTIFICATION TEST SETUP ===")
    
    # Check users and their schools
    print("\n--- Users and Schools ---")
    users = User.objects.all()
    for user in users:
        school_info = f"School: {user.school.name}" if user.school else "No school assigned"
        print(f"- {user.username} (Type: {user.user_type}) - {school_info}")
    
    # Check if we have any users with schools
    users_with_schools = [u for u in users if u.school]
    if users_with_schools:
        print(f"\n✅ Found {len(users_with_schools)} users with schools - notifications should work")
        print("Recommended test users:")
        for user in users_with_schools[:3]:
            print(f"  - {user.username} (school: {user.school.name})")
    else:
        print("\n❌ No users have schools assigned - notifications will fail")
        print("You need to assign a school to a user first")
    
    # Check schools
    print("\n--- Available Schools ---")
    schools = School.objects.all()
    for school in schools:
        print(f"- {school.name} (ID: {school.id})")
    
    # Check notifications
    print("\n--- Current Notifications ---")
    notifications = Notification.objects.all()
    print(f"Total notifications: {notifications.count()}")
    
    if notifications.exists():
        for notification in notifications[:3]:
            print(f"- {notification.title} (Type: {notification.notification_type}, School: {notification.school.name})")
    
    # Test notification creation
    print("\n--- Testing Notification Creation ---")
    if users_with_schools:
        test_user = users_with_schools[0]
        print(f"Testing with user: {test_user.username}")
        
        try:
            # Create a test notification
            notification = Notification.objects.create(
                school=test_user.school,
                title="Test Notification",
                body="This is a test notification to verify the fix",
                notification_type="general",
                data={"test": True, "source": "python_script"}
            )
            print(f"✅ Successfully created notification: {notification.title}")
            
            # Clean up
            notification.delete()
            print("✅ Test notification cleaned up")
            
        except Exception as e:
            print(f"❌ Failed to create notification: {e}")
    else:
        print("❌ Cannot test notification creation - no users with schools")

if __name__ == "__main__":
    test_notification_setup()
