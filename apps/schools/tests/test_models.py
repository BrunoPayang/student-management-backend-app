"""
Tests for School models
"""
import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone

# Import models inside tests to avoid import errors
# from apps.schools.models import School, SchoolConfiguration


@pytest.mark.models
class TestSchoolModel:
    """Test School model functionality"""
    
    def test_school_creation(self, create_school):
        """Test that a school can be created with valid data"""
        from apps.schools.models import School
        school = create_school()
        assert 'Test School' in school.name
        assert 'test-school' in school.slug
        assert school.address == '123 Test St'
        assert school.contact_phone == '+1234567890'
        assert 'test' in school.contact_email and '@school.com' in school.contact_email
    
    def test_school_str_representation(self, create_school):
        """Test the string representation of a school"""
        from apps.schools.models import School
        school = create_school()
        assert 'Test School' in str(school)
    
    def test_school_slug_uniqueness(self, create_school):
        """Test that school slugs must be unique"""
        from apps.schools.models import School
        # Create first school
        school1 = create_school()
        
        # Try to create second school with same slug
        with pytest.raises(IntegrityError):
            School.objects.create(
                name='Duplicate School',
                slug=school1.slug,  # Use the same slug
                address='456 Duplicate St',
                contact_phone='+1234567890',
                contact_email='duplicate@school.com',
                city='Duplicate City',
                state='Duplicate State',
                country='Niger'
            )
    
    def test_school_slug_generation(self, create_school):
        """Test that school slug is generated from name if not provided"""
        from apps.schools.models import School
        school = create_school(name='New School Name', slug='')
        assert school.slug == 'new-school-name'
    
    def test_school_phone_validation(self, create_school):
        """Test phone number validation"""
        from apps.schools.models import School
        # Valid phone number
        school = create_school(contact_phone='+1234567890')
        assert school.contact_phone == '+1234567890'
        
        # Invalid phone number (too short)
        with pytest.raises(ValidationError):
            school = create_school(contact_phone='123')
            school.full_clean()
    
    def test_school_email_validation(self, create_school):
        """Test email validation"""
        from apps.schools.models import School
        # Valid email
        school = create_school(contact_email='valid@email.com')
        assert school.contact_email == 'valid@email.com'
        
        # Invalid email
        with pytest.raises(ValidationError):
            school = create_school(contact_email='invalid-email')
            school.full_clean()
    
    def test_school_city_state(self, create_school):
        """Test city and state handling"""
        from apps.schools.models import School
        # With city and state
        school = create_school(city='Test City', state='Test State')
        assert school.city == 'Test City'
        assert school.state == 'Test State'
        
        # Check full address property
        assert 'Test City' in school.full_address
        assert 'Test State' in school.full_address
    
    def test_school_website_validation(self, create_school):
        """Test website URL validation"""
        from apps.schools.models import School
        # Valid URL
        school = create_school(website='https://example.com')
        assert school.website == 'https://example.com'
        
        # Invalid URL
        with pytest.raises(ValidationError):
            school = create_school(website='not-a-url')
            school.full_clean()
    
    def test_school_meta_options(self, create_school):
        """Test school model meta options"""
        from apps.schools.models import School
        school = create_school()
        
        # Check table name
        assert school._meta.db_table == 'schools_school'
        
        # Check verbose names
        assert school._meta.verbose_name == 'School'
        assert school._meta.verbose_name_plural == 'Schools'
        
        # Check ordering
        assert school._meta.ordering == ['name']


@pytest.mark.models
class TestSchoolConfigurationModel:
    """Test SchoolConfiguration model functionality"""
    
    def test_configuration_creation(self, create_school_configuration):
        """Test that a school configuration can be created"""
        from apps.schools.models import SchoolConfiguration
        
        config = create_school_configuration()
        
        # Check that the date fields are properly set
        assert config.academic_year_start == '2024-09-01'
        assert config.current_semester == 'first'
        assert config.enable_sms_notifications is True
        assert config.enable_email_notifications is True
        assert config.enable_push_notifications is True
        assert config.currency == 'NGN'
        assert config.max_file_size_mb == 10
    
    def test_configuration_str_representation(self, create_school_configuration):
        """Test the string representation of a school configuration"""
        from apps.schools.models import SchoolConfiguration
        config = create_school_configuration()
        expected = f"Configuration for {config.school.name}"
        assert str(config) == expected
    
    def test_configuration_school_relationship(self, create_school, create_school_configuration):
        """Test the relationship between school and configuration"""
        from apps.schools.models import SchoolConfiguration
        school = create_school()
        config = create_school_configuration(school=school)
        
        assert config.school == school
        assert school.configuration == config
    
    def test_configuration_semester_choices(self, create_school_configuration):
        """Test semester choice validation"""
        from apps.schools.models import SchoolConfiguration
        # Valid semester
        config = create_school_configuration(current_semester='second')
        assert config.current_semester == 'second'
        
        # Invalid semester
        with pytest.raises(ValidationError):
            config = create_school_configuration(current_semester='Invalid')
            config.full_clean()
    
    def test_configuration_notification_settings(self, create_school_configuration):
        """Test notification settings"""
        from apps.schools.models import SchoolConfiguration
        # Test notification settings
        config = create_school_configuration(
            enable_sms_notifications=False,
            enable_email_notifications=False,
            enable_push_notifications=False
        )
        assert config.enable_sms_notifications is False
        assert config.enable_email_notifications is False
        assert config.enable_push_notifications is False
    
    def test_configuration_file_settings(self, create_school_configuration):
        """Test file upload settings"""
        from apps.schools.models import SchoolConfiguration
        # Test file settings
        config = create_school_configuration(
            max_file_size_mb=20,
            allowed_file_types=['pdf', 'doc', 'docx']
        )
        assert config.max_file_size_mb == 20
        assert 'pdf' in config.allowed_file_types
    
    def test_configuration_meta_options(self, create_school_configuration):
        """Test configuration model meta options"""
        from apps.schools.models import SchoolConfiguration
        config = create_school_configuration()
        
        # Check table name
        assert config._meta.db_table == 'schools_school_configuration'
        
        # Check verbose names
        assert config._meta.verbose_name == 'School Configuration'
        assert config._meta.verbose_name_plural == 'School Configurations'
        
        # Check that school relationship is one-to-one
        assert config.school is not None


@pytest.mark.models
class TestSchoolModelMethods:
    """Test School model methods"""
    
    def test_get_student_count(self, create_school, create_student):
        """Test getting student count for a school"""
        from apps.schools.models import School
        school = create_school()
        
        # No students initially
        assert school.get_student_count() == 0
        
        # Add students
        create_student(school=school)
        create_student(school=school)
        create_student(school=school)
        
        assert school.get_student_count() == 3
    
    def test_get_staff_count(self, create_school, create_user):
        """Test getting staff count for a school"""
        from apps.schools.models import School
        school = create_school()
        
        # No staff initially
        assert school.get_staff_count() == 0
        
        # Add staff
        create_user(school=school, user_type='school_staff')
        create_user(school=school, user_type='school_staff')
        
        assert school.get_staff_count() == 2
    
    def test_get_parent_count(self, create_school, create_user):
        """Test getting parent count for a school"""
        from apps.schools.models import School
        school = create_school()
        
        # No parents initially
        assert school.get_parent_count() == 0
        
        # Add parents
        create_user(school=school, user_type='parent')
        create_user(school=school, user_type='parent')
        create_user(school=school, user_type='parent')
        
        assert school.get_parent_count() == 3
