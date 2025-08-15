#!/usr/bin/env python
"""
Test script for parent dashboard child behavior endpoint
"""
import requests
import json
from django.core.management import execute_from_command_line
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schoolconnect.settings.development')
django.setup()

from apps.authentication.models import User
from apps.schools.models import School
from apps.students.models import Student, ParentStudent, BehaviorReport
from django.utils import timezone
from datetime import date

def create_test_data():
    """Create test data for parent dashboard testing"""
    print("=== Creating Test Data ===")
    
    # Get or create a school
    school, created = School.objects.get_or_create(
        name="Test School",
        defaults={
            'contact_email': 'test@school.com',
            'contact_phone': '+22790123456',
            'address': 'Test Address',
            'city': 'Test City',
            'state': 'Test State',
            'is_verified': True
        }
    )
    print(f"School: {school.name}")
    
    # Get or create a parent user
    parent, created = User.objects.get_or_create(
        username='testparent',
        defaults={
            'email': 'parent@test.com',
            'first_name': 'Test',
            'last_name': 'Parent',
            'user_type': 'parent',
            'is_active': True
        }
    )
    if created:
        parent.set_password('testpass123')
        parent.save()
    print(f"Parent: {parent.full_name}")
    
    # Get or create a student
    student, created = Student.objects.get_or_create(
        student_id='TEST001',
        school=school,
        defaults={
            'first_name': 'Test',
            'last_name': 'Student',
            'date_of_birth': date(2010, 1, 1),
            'gender': 'male',
            'class_level': 'Class 5',
            'enrollment_date': date.today(),
            'is_active': True
        }
    )
    print(f"Student: {student.full_name}")
    
    # Create parent-student relationship
    parent_student, created = ParentStudent.objects.get_or_create(
        parent=parent,
        student=student,
        defaults={
            'relationship': 'father',
            'is_primary': True,
            'is_emergency_contact': True,
            'receive_sms': True,
            'receive_email': True,
            'receive_push': True
        }
    )
    print(f"Parent-Student relationship created: {parent_student}")
    
    # Create some behavior reports
    behavior_reports = []
    for i in range(3):
        report, created = BehaviorReport.objects.get_or_create(
            student=student,
            title=f"Test Behavior Report {i+1}",
            incident_date=date.today(),
            defaults={
                'report_type': 'positive' if i == 0 else 'negative' if i == 1 else 'neutral',
                'description': f"This is test behavior report {i+1}",
                'severity_level': 'low' if i == 0 else 'medium' if i == 1 else 'high',
                'reported_by': parent,
                'notify_parents': True,
                'is_public': True
            }
        )
        behavior_reports.append(report)
        print(f"Behavior report created: {report.title}")
    
    return parent, student, behavior_reports

def test_parent_dashboard_endpoints():
    """Test parent dashboard endpoints"""
    print("\n=== Testing Parent Dashboard Endpoints ===")
    
    BASE_URL = "http://localhost:8000"
    
    # First, let's login as the parent
    print("1. Logging in as parent...")
    login_data = {
        'username': 'testparent',
        'password': 'testpass123'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access']
            print("   ✅ Login successful")
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Test my_children endpoint
            print("\n2. Testing my_children endpoint...")
            response = requests.get(f"{BASE_URL}/api/parent-dashboard/my_children/", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                children = response.json()
                print(f"   ✅ Found {len(children)} children")
                for child in children:
                    print(f"      - {child['first_name']} {child['last_name']} (ID: {child['id']})")
            else:
                print(f"   ❌ Error: {response.text}")
            
            # Test child_behavior endpoint
            print("\n3. Testing child_behavior endpoint...")
            # Get the first child's ID
            response = requests.get(f"{BASE_URL}/api/parent-dashboard/my_children/", headers=headers)
            if response.status_code == 200:
                children = response.json()
                if children:
                    child_id = children[0]['id']
                    print(f"   Testing with child ID: {child_id}")
                    
                    response = requests.get(f"{BASE_URL}/api/parent-dashboard/{child_id}/child_behavior/", headers=headers)
                    print(f"   Status: {response.status_code}")
                    if response.status_code == 200:
                        behavior_reports = response.json()
                        print(f"   ✅ Found {len(behavior_reports)} behavior reports")
                        for report in behavior_reports:
                            print(f"      - {report['title']} ({report['report_type']})")
                    else:
                        print(f"   ❌ Error: {response.text}")
                else:
                    print("   ❌ No children found")
            else:
                print(f"   ❌ Error getting children: {response.text}")
            
            # Test child_statistics endpoint
            print("\n4. Testing child_statistics endpoint...")
            if children:
                child_id = children[0]['id']
                response = requests.get(f"{BASE_URL}/api/parent-dashboard/{child_id}/child_statistics/", headers=headers)
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    stats = response.json()
                    print("   ✅ Statistics retrieved:")
                    print(f"      - Academic: {stats.get('academic', {})}")
                    print(f"      - Behavior: {stats.get('behavior', {})}")
                    print(f"      - Payments: {stats.get('payments', {})}")
                else:
                    print(f"   ❌ Error: {response.text}")
            
        else:
            print(f"   ❌ Login failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error during testing: {e}")

def main():
    """Main test function"""
    print("=== Parent Dashboard Child Behavior Test ===")
    
    # Create test data
    parent, student, behavior_reports = create_test_data()
    
    # Test the endpoints
    test_parent_dashboard_endpoints()
    
    print("\n=== Test Summary ===")
    print("✅ Test data created successfully")
    print("✅ Parent dashboard endpoints tested")
    print("🔗 Child behavior endpoint: /api/parent-dashboard/{child_id}/child_behavior/")
    print("📊 Child statistics endpoint: /api/parent-dashboard/{child_id}/child_statistics/")

if __name__ == "__main__":
    main() 