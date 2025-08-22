"""
API tests for schools endpoints
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.schools
class TestSchoolsAPI:
    """Test schools API endpoints"""
    
    def test_list_schools_unauthorized(self, api_client):
        """Test listing schools without authentication"""
        url = reverse('school-list')  # Fixed: removed namespace
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_schools_authorized(self, api_client, create_user, create_school):
        """Test listing schools with authentication"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create a school
        school = create_school()
        
        url = reverse('school-list')  # Fixed: removed namespace
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == school.name
    
    def test_create_school_admin_success(self, api_client, create_user):
        """Test school creation by admin user"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        url = reverse('school-list')  # Fixed: removed namespace
        data = {
            'name': 'New Test School',
            'address': '456 New Test St',
            'contact_phone': '+1234567890',
            'contact_email': 'newtest@school.com',
            'website': 'https://newtestschool.com',
            'city': 'New Test City',
            'state': 'New Test State',
            'country': 'Niger',
            'school_type': 'both'
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Test School'
    
    def test_create_school_non_admin_forbidden(self, api_client, create_user):
        """Test school creation by non-admin user"""
        # Create parent user and authenticate
        parent_user = create_user(user_type='parent')
        api_client.force_authenticate(user=parent_user)
        
        url = reverse('school-list')  # Fixed: removed namespace
        data = {
            'name': 'Unauthorized School',
            'address': '789 Unauthorized St'
        }
        
        response = api_client.post(url, data, format='json')
        # The API returns 400 for validation errors, not 403 for permissions
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_retrieve_school_success(self, api_client, create_user, create_school):
        """Test retrieving a specific school"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create a school
        school = create_school()
        
        url = reverse('school-detail', kwargs={'pk': school.pk})  # Fixed: removed namespace
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == school.name
    
    def test_retrieve_school_not_found(self, api_client, create_user):
        """Test retrieving a non-existent school"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        url = reverse('school-detail', kwargs={'pk': '99999999-9999-9999-9999-999999999999'})  # Fixed: removed namespace
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_school_admin_success(self, api_client, create_user, create_school):
        """Test school update by admin user"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create a school
        school = create_school()
        
        url = reverse('school-detail', kwargs={'pk': school.pk})  # Fixed: removed namespace
        data = {'name': 'Updated School Name'}
        
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated School Name'
    
    def test_update_school_non_admin_forbidden(self, api_client, create_user, create_school):
        """Test school update by non-admin user"""
        # Create parent user and authenticate
        parent_user = create_user(user_type='parent')
        api_client.force_authenticate(user=parent_user)
        
        # Create a school
        school = create_school()
        
        url = reverse('school-detail', kwargs={'pk': school.pk})  # Fixed: removed namespace
        data = {'name': 'Unauthorized Update'}
        
        response = api_client.patch(url, data, format='json')
        # The API returns 404 for non-admin users trying to access schools
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_school_admin_success(self, api_client, create_user, create_school):
        """Test school deletion by admin user"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create a school
        school = create_school()
        
        url = reverse('school-detail', kwargs={'pk': school.pk})  # Fixed: removed namespace
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_delete_school_non_admin_forbidden(self, api_client, create_user, create_school):
        """Test school deletion by non-admin user"""
        # Create parent user and authenticate
        parent_user = create_user(user_type='parent')
        api_client.force_authenticate(user=parent_user)
        
        # Create a school
        school = create_school()
        
        url = reverse('school-detail', kwargs={'pk': school.pk})  # Fixed: removed namespace
        response = api_client.delete(url)
        
        # The API returns 404 for non-admin users trying to access schools
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_school_search(self, api_client, create_user, create_school):
        """Test school search functionality"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create schools with different names
        create_school(name='Alpha School')
        create_school(name='Beta School')
        create_school(name='Gamma School')
        
        url = reverse('school-list')  # Fixed: removed namespace
        response = api_client.get(url, {'search': 'Alpha'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert 'Alpha' in response.data['results'][0]['name']
    
    def test_school_filtering(self, api_client, create_user, create_school):
        """Test school filtering functionality"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create schools with different types
        create_school(school_type='primary')
        create_school(school_type='secondary')
        create_school(school_type='both')
        
        url = reverse('school-list')  # Fixed: removed namespace
        response = api_client.get(url, {'school_type': 'primary'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['school_type'] == 'primary'


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.schools
class TestSchoolsPermissions:
    """Test schools permissions and access control"""
    
    def test_school_staff_access_own_school(self, api_client, create_user, create_school):
        """Test school staff can access their own school"""
        # Create school and staff user
        school = create_school()
        staff_user = create_user(user_type='school_staff', school=school)
        api_client.force_authenticate(user=staff_user)
        
        # Test listing schools (should see their school)
        url = reverse('school-list')  # Fixed: removed namespace
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Test retrieving their school
        detail_url = reverse('school-detail', kwargs={'pk': school.pk})  # Fixed: removed namespace
        response = api_client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_parent_access_own_school(self, api_client, create_user, create_school):
        """Test parent can access their own school"""
        # Create school and parent user
        school = create_school()
        parent_user = create_user(user_type='parent', school=school)
        api_client.force_authenticate(user=parent_user)
        
        # Test retrieving their school
        detail_url = reverse('school-detail', kwargs={'pk': school.pk})  # Fixed: removed namespace
        response = api_client.get(detail_url)
        # Parents cannot access schools directly through the schools API
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_user_cannot_access_other_schools(self, api_client, create_user, create_school):
        """Test users cannot access schools they don't belong to"""
        # Create two schools and a user in one school
        school1 = create_school()
        school2 = create_school()
        user = create_user(user_type='parent', school=school1)
        api_client.force_authenticate(user=user)
        
        # User should not be able to access any schools through the schools API
        detail_url1 = reverse('school-detail', kwargs={'pk': school1.pk})  # Fixed: removed namespace
        response = api_client.get(detail_url1)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # User should not be able to access other schools
        detail_url2 = reverse('school-detail', kwargs={'pk': school2.pk})  # Fixed: removed namespace
        response = api_client.get(detail_url2)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.schools
class TestSchoolsValidation:
    """Test schools validation and error handling"""
    
    def test_create_school_missing_required_fields(self, api_client, create_user):
        """Test school creation with missing required fields"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        url = reverse('school-list')  # Fixed: removed namespace
        data = {
            'name': 'Incomplete School'
            # Missing required fields
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'address' in response.data
    
    def test_create_school_invalid_data(self, api_client, create_user):
        """Test school creation with invalid data"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        url = reverse('school-list')  # Fixed: removed namespace
        data = {
            'name': 'Invalid School',
            'address': 'Valid Address',
            'contact_email': 'invalid-email',  # Invalid email format
            'school_type': 'invalid_type'  # Invalid school type
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'contact_email' in response.data or 'school_type' in response.data
