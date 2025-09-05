"""
Shared test fixtures for the Django project
"""
import pytest

# Django imports
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

# We'll import these inside the fixtures when needed
DRF_AVAILABLE = True  # Will be checked in fixtures
MODELS_AVAILABLE = True  # Will be checked in fixtures


@pytest.fixture
def api_client():
    """Return an API client for testing"""
    try:
        from rest_framework.test import APIClient
        return APIClient()
    except ImportError:
        pytest.skip("DRF not available")


@pytest.fixture
def test_password():
    """Return a test password"""
    return 'testpass123'


@pytest.fixture
def create_user(db, test_password):
    """Create and return a user factory function"""
    def _create_user(**kwargs):
        import uuid
        
        # Generate unique username and email
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            'username': f'testuser{unique_id}',
            'email': f'test{unique_id}@example.com',
            'password': test_password,
            'first_name': 'Test',
            'last_name': 'User',
            'user_type': 'parent'
        }
        user_data.update(kwargs)
        
        from apps.authentication.models import User
        user = User.objects.create_user(**user_data)
        return user
    return _create_user


@pytest.fixture
def create_school(db):
    """Create and return a school factory function"""
    def _create_school(**kwargs):
        from apps.schools.models import School
        import uuid
        
        # Generate unique slug and name
        unique_id = str(uuid.uuid4())[:8]
        school_data = {
            'name': f'Test School {unique_id}',
            'slug': f'test-school-{unique_id}',
            'address': '123 Test St',
            'contact_phone': '+1234567890',
            'contact_email': f'test{unique_id}@school.com',
            'website': 'https://testschool.com',
            'city': 'Test City',
            'state': 'Test State',
            'country': 'Niger',
            'school_type': 'both'
        }
        school_data.update(kwargs)
        
        school = School.objects.create(**school_data)
        return school
    return _create_school


@pytest.fixture
def create_school_configuration(db, create_school):
    """Create and return a school configuration factory function"""
    def _create_school_configuration(**kwargs):
        school = kwargs.get('school') or create_school()
        
        config_data = {
            'school': school,
            'academic_year_start': '2024-09-01',
            'academic_year_end': '2025-06-30',
            'current_semester': 'first',
            'enable_sms_notifications': True,
            'enable_email_notifications': True,
            'enable_push_notifications': True,
            'currency': 'NGN',
            'payment_reminder_days': 7,
            'max_file_size_mb': 10,
            'allowed_file_types': ['pdf', 'doc', 'docx', 'jpg', 'png']
        }
        config_data.update(kwargs)
        
        from apps.schools.models import SchoolConfiguration
        config = SchoolConfiguration.objects.create(**config_data)
        return config
    return _create_school_configuration


@pytest.fixture
def create_student(db, create_school):
    """Create and return a student factory function"""
    def _create_student(**kwargs):
        import uuid
        
        school = kwargs.get('school') or create_school()
        
        student_data = {
            'school': school,
            'first_name': 'John',
            'last_name': 'Doe',
            'student_id': f'ST{str(uuid.uuid4())[:6].upper()}',
            'class_assigned': None,
            'date_of_birth': '2010-01-01',
            'gender': 'male',
            'enrollment_date': '2024-09-01',
            'is_active': True
        }
        student_data.update(kwargs)
        
        from apps.students.models import Student
        student = Student.objects.create(**student_data)
        return student
    return _create_student


@pytest.fixture
def create_transcript(db, create_student):
    """Create and return a transcript factory function"""
    def _create_transcript(**kwargs):
        student = kwargs.get('student') or create_student()
        
        transcript_data = {
            'student': student,
            'academic_year': '2024-2025',
            'semester': 'Fall',
            'gpa': 3.8,
            'total_credits': 15,
            'is_public': True
        }
        transcript_data.update(kwargs)
        
        from apps.students.models import Transcript
        transcript = Transcript.objects.create(**transcript_data)
        return transcript
    return _create_transcript


@pytest.fixture
def create_behavior_report(db, create_student):
    """Create and return a behavior report factory function"""
    def _create_behavior_report(**kwargs):
        student = kwargs.get('student') or create_student()
        
        report_data = {
            'student': student,
            'report_type': 'positive',
            'description': 'Excellent behavior in class',
            'reported_by': 'teacher',
            'incident_date': '2024-01-15',
            'is_public': True
        }
        report_data.update(kwargs)
        
        from apps.students.models import BehaviorReport
        report = BehaviorReport.objects.create(**report_data)
        return report
    return _create_behavior_report


@pytest.fixture
def create_payment_record(db, create_student):
    """Create and return a payment record factory function"""
    def _create_payment_record(**kwargs):
        student = kwargs.get('student') or create_student()
        
        payment_data = {
            'student': student,
            'amount': 100.00,
            'payment_type': 'tuition',
            'due_date': '2024-02-01',
            'status': 'pending',
            'description': 'Monthly tuition payment'
        }
        payment_data.update(kwargs)
        
        from apps.students.models import PaymentRecord
        payment = PaymentRecord.objects.create(**payment_data)
        return payment
    return _create_payment_record


@pytest.fixture
def create_file_upload(db, create_school, create_user):
    """Create and return a file upload factory function"""
    def _create_file_upload(**kwargs):
        school = kwargs.get('school') or create_school()
        user = kwargs.get('uploaded_by') or create_user()
        
        file_data = {
            'school': school,
            'uploaded_by': user,
            'original_name': 'test.txt',
            'file_type': 'transcript',
            'description': 'Test file upload',
            'tags': 'test,transcript',
            'file_size': 1024,  # 1KB
            'content_type': 'text/plain',
            'is_public': False
        }
        file_data.update(kwargs)
        
        from apps.files.models import FileUpload
        file_upload = FileUpload.objects.create(**file_data)
        return file_upload
    return _create_file_upload


@pytest.fixture
def create_notification(db, create_school):
    """Create and return a notification factory function"""
    def _create_notification(**kwargs):
        # Handle recipient parameter (for backward compatibility)
        target_users = kwargs.get('target_users', [])
        if 'recipient' in kwargs:
            target_users = [kwargs.pop('recipient')]
        
        # If we have target users, use their school if no school is specified
        school = kwargs.get('school')
        if not school and target_users:
            # Get school from the first target user
            first_user = target_users[0] if isinstance(target_users, list) else target_users
            if hasattr(first_user, 'school') and first_user.school:
                school = first_user.school
        
        # If still no school, create a new one
        if not school:
            school = create_school()
        
        notification_data = {
            'school': school,
            'title': 'Test Notification',
            'body': 'This is a test notification',
            'notification_type': 'general',
            'data': {'test': True}
        }
        notification_data.update(kwargs)
        
        from apps.notifications.models import Notification
        notification = Notification.objects.create(**notification_data)
        
        # Set target users if provided
        if target_users:
            notification.target_users.set(target_users)
        
        return notification
    return _create_notification


@pytest.fixture
def authenticated_client(db, create_user):
    """Return an authenticated API client"""
    try:
        from rest_framework.test import APIClient
        
        def _authenticated_client(user=None, **kwargs):
            if user is None:
                user = create_user(**kwargs)
            
            client = APIClient()
            client.force_authenticate(user=user)
            return client, user
        return _authenticated_client
    except ImportError:
        pytest.skip("DRF not available")


@pytest.fixture
def jwt_authenticated_client(db, create_user):
    """Return a JWT authenticated API client"""
    try:
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken
        
        def _jwt_authenticated_client(user=None, **kwargs):
            if user is None:
                user = create_user(**kwargs)
            
            client = APIClient()
            refresh = RefreshToken.for_user(user)
            client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
            return client, user, refresh
        return _jwt_authenticated_client
    except ImportError:
        pytest.skip("DRF not available")


@pytest.fixture
def admin_user(db, create_user):
    """Create and return an admin user"""
    return create_user(user_type='admin')


@pytest.fixture
def school_staff_user(db, create_user, create_school):
    """Create and return a school staff user"""
    school = create_school()
    return create_user(user_type='school_staff', school=school)


@pytest.fixture
def parent_user(db, create_user, create_school):
    """Create and return a parent user"""
    school = create_school()
    return create_user(user_type='parent', school=school)


@pytest.fixture
def complete_test_data(db, create_school, create_student, create_transcript, 
                       create_behavior_report, create_payment_record):
    """Create a complete set of test data"""
    school = create_school()
    student = create_student(school=school)
    transcript = create_transcript(student=student)
    behavior_report = create_behavior_report(student=student)
    payment_record = create_payment_record(student=student)
    
    return {
        'school': school,
        'student': student,
        'transcript': transcript,
        'behavior_report': behavior_report,
        'payment_record': payment_record
    }


# Performance testing fixtures
@pytest.fixture
def performance_test_data(db, create_school):
    """Create large datasets for performance testing"""
    school = create_school()
    
    # Create multiple students
    students = []
    for i in range(100):
        student = create_student(
            school=school,
            first_name=f'Student{i}',
            last_name=f'Test{i}',
            username=f'student{i}'
        )
        students.append(student)
    
    # Create multiple transcripts
    transcripts = []
    for student in students:
        for year in range(2020, 2025):
            transcript = create_transcript(
                student=student,
                academic_year=f'{year}-{year+1}',
                semester='Fall'
            )
            transcripts.append(transcript)
    
    return {
        'school': school,
        'students': students,
        'transcripts': transcripts
    }


# Security testing fixtures
@pytest.fixture
def malicious_inputs():
    """Return various malicious inputs for security testing"""
    return {
        'sql_injection': [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --"
        ],
        'xss': [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>"
        ],
        'path_traversal': [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd"
        ]
    }
