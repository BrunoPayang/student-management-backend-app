"""
Simple School model tests without custom fixtures
"""
import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

class TestSchoolModelSimple(TestCase):
    """Simple School model tests without custom fixtures"""
    
    def test_school_creation_simple(self):
        """Test that a school can be created with valid data"""
        from apps.schools.models import School
        
        # Create a school with minimal data
        school = School.objects.create(
            name='Simple Test School',
            slug='simple-test-school',
            address='123 Simple St',
            contact_phone='+1234567890',
            contact_email='simple@school.com',
            city='Simple City',
            state='Simple State',
            country='Niger'
        )
        
        # Verify it was created
        assert school.name == 'Simple Test School'
        assert school.slug == 'simple-test-school'
        assert school.address == '123 Simple St'
        assert school.contact_phone == '+1234567890'
        assert school.contact_email == 'simple@school.com'
    
    def test_school_str_representation_simple(self):
        """Test the string representation of a school"""
        from apps.schools.models import School
        
        school = School.objects.create(
            name='String Test School',
            slug='string-test-school',
            address='456 String St',
            contact_phone='+1234567890',
            contact_email='string@school.com',
            city='String City',
            state='String State',
            country='Niger'
        )
        
        assert str(school) == 'String Test School'
    
    def test_school_slug_uniqueness_simple(self):
        """Test that school slugs must be unique"""
        from apps.schools.models import School
        
        # Create first school
        School.objects.create(
            name='First Unique School',
            slug='unique-slug-test',
            address='123 First St',
            contact_phone='+1234567890',
            contact_email='first@school.com',
            city='First City',
            state='First State',
            country='Niger'
        )
        
        # Try to create second school with same slug
        with pytest.raises(IntegrityError):
            School.objects.create(
                name='Second Unique School',
                slug='unique-slug-test',  # Same slug
                address='456 Second St',
                contact_phone='+1234567890',
                contact_email='second@school.com',
                city='Second City',
                state='Second State',
                country='Niger'
            )
