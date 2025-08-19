#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schoolconnect.settings.development')
django.setup()

from apps.files.models import FileUpload
from apps.authentication.models import User
from apps.schools.models import School

def test_file_upload_setup():
    print("=== FILE UPLOAD TEST SETUP ===")
    
    # Check users and their schools
    print("\n--- Users and Schools ---")
    users = User.objects.all()
    for user in users:
        school_info = f"School: {user.school.name}" if user.school else "No school assigned"
        print(f"- {user.username} (Type: {user.user_type}) - {school_info}")
    
    # Check if we have any users with schools
    users_with_schools = [u for u in users if u.school]
    if users_with_schools:
        print(f"\n✅ Found {len(users_with_schools)} users with schools - file uploads should work")
        print("Recommended test users:")
        for user in users_with_schools[:3]:
            print(f"  - {user.username} (school: {user.school.name})")
    else:
        print("\n❌ No users have schools assigned - file uploads will fail")
        print("You need to assign a school to a user first")
    
    # Check schools
    print("\n--- Available Schools ---")
    schools = School.objects.all()
    for school in schools:
        print(f"- {school.name} (ID: {school.id})")
    
    # Check file uploads
    print("\n--- Current File Uploads ---")
    files = FileUpload.objects.all()
    print(f"Total files: {files.count()}")
    
    if files.exists():
        for file in files[:3]:
            print(f"- {file.original_name} (Type: {file.file_type}, Tags: '{file.tags}')")

if __name__ == "__main__":
    test_file_upload_setup()
