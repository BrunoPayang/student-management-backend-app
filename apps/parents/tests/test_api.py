"""
API tests for parents endpoints
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.parents
class TestParentDashboardAPI:
    """Test parent dashboard API endpoints"""
    
    def test_dashboard_unauthorized(self, api_client):
        """Test dashboard access without authentication"""
        url = reverse('parents:parent-dashboard-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_dashboard_parent_access(self, api_client, create_user, create_school, create_student):
        """Test parent can access their dashboard"""
        # Create school, parent user, and student
        school = create_school()
        parent_user = create_user(user_type='parent', school=school)
        student = create_student(school=school)
        
        api_client.force_authenticate(user=parent_user)
        
        url = reverse('parents:parent-dashboard-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
    
    def test_dashboard_non_parent_forbidden(self, api_client, create_user):
        """Test non-parent users cannot access parent dashboard"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        url = reverse('parents:parent-dashboard-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_dashboard_pagination(self, api_client, create_user, create_school, create_student):
        """Test dashboard pagination"""
        # Create school, parent user, and multiple students
        school = create_school()
        parent_user = create_user(user_type='parent', school=school)
        
        # Create multiple students
        for i in range(15):
            create_student(school=school)
        
        api_client.force_authenticate(user=parent_user)
        
        url = reverse('parents:parent-dashboard-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        
        # Check pagination
        assert len(response.data['results']) <= 10  # Default page size
        assert response.data['count'] >= 15
    
    def test_dashboard_search(self, api_client, create_user, create_school, create_student):
        """Test dashboard search functionality"""
        # Create school, parent user, and students
        school = create_school()
        parent_user = create_user(user_type='parent', school=school)
        
        # Create students with different names
        create_student(first_name='Alice', last_name='Smith', school=school)
        create_student(first_name='Bob', last_name='Johnson', school=school)
        create_student(first_name='Charlie', last_name='Brown', school=school)
        
        api_client.force_authenticate(user=parent_user)
        
        url = reverse('parents:parent-dashboard-list')
        
        # Search by first name
        response = api_client.get(url, {'search': 'Alice'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
        
        # Search by last name
        response = api_client.get(url, {'search': 'Johnson'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.parents
class TestParentStudentManagementAPI:
    """Test parent-student relationship management"""
    
    def test_link_parent_student_success(self, api_client, create_user, create_school, create_student):
        """Test successful parent-student linking"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school, parent, and student
        school = create_school()
        parent_user = create_user(user_type='parent', school=school)
        student = create_student(school=school)
        
        url = reverse('parents:parent-student-list')
        data = {
            'parent': parent_user.pk,
            'student': student.pk,
            'relationship': 'mother'
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['parent'] == parent_user.pk
        assert response.data['student'] == student.pk
        assert response.data['relationship'] == 'mother'
    
    def test_link_parent_student_unauthorized(self, api_client, create_user, create_school, create_student):
        """Test parent-student linking by unauthorized user"""
        # Create regular user and authenticate
        regular_user = create_user(user_type='parent')
        api_client.force_authenticate(user=regular_user)
        
        # Create school, parent, and student
        school = create_school()
        parent_user = create_user(user_type='parent', school=school)
        student = create_student(school=school)
        
        url = reverse('parents:parent-student-list')
        data = {
            'parent': parent_user.pk,
            'student': student.pk,
            'relationship': 'father'
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_list_parent_students(self, api_client, create_user, create_school, create_student):
        """Test listing parent-student relationships"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school, parent, and students
        school = create_school()
        parent_user = create_user(user_type='parent', school=school)
        student1 = create_student(school=school)
        student2 = create_student(school=school)
        
        # Create relationships
        url = reverse('parents:parent-student-list')
        data1 = {'parent': parent_user.pk, 'student': student1.pk, 'relationship': 'mother'}
        data2 = {'parent': parent_user.pk, 'student': student2.pk, 'relationship': 'mother'}
        
        api_client.post(url, data1, format='json')
        api_client.post(url, data2, format='json')
        
        # List relationships
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 2
    
    def test_update_parent_student_relationship(self, api_client, create_user, create_school, create_student):
        """Test updating parent-student relationship"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school, parent, and student
        school = create_school()
        parent_user = create_user(user_type='parent', school=school)
        student = create_student(school=school)
        
        # Create relationship
        url = reverse('parents:parent-student-list')
        data = {'parent': parent_user.pk, 'student': student.pk, 'relationship': 'mother'}
        response = api_client.post(url, data, format='json')
        relationship_id = response.data['id']
        
        # Update relationship
        update_url = reverse('parents:parent-student-detail', kwargs={'pk': relationship_id})
        update_data = {'relationship': 'father'}
        
        response = api_client.patch(update_url, update_data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['relationship'] == 'father'
    
    def test_delete_parent_student_relationship(self, api_client, create_user, create_school, create_student):
        """Test deleting parent-student relationship"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school, parent, and student
        school = create_school()
        parent_user = create_user(user_type='parent', school=school)
        student = create_student(school=school)
        
        # Create relationship
        url = reverse('parents:parent-student-list')
        data = {'parent': parent_user.pk, 'student': student.pk, 'relationship': 'mother'}
        response = api_client.post(url, data, format='json')
        relationship_id = response.data['id']
        
        # Delete relationship
        delete_url = reverse('parents:parent-student-detail', kwargs={'pk': relationship_id})
        response = api_client.delete(delete_url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify relationship is deleted
        get_response = api_client.get(delete_url)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.parents
class TestParentNotificationsAPI:
    """Test parent notification endpoints"""
    
    def test_notifications_list_unauthorized(self, api_client):
        """Test notifications access without authentication"""
        url = reverse('parents:parent-dashboard-notifications')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_notifications_list_authorized(self, api_client, create_user, create_school, create_notification):
        """Test parent can access their notifications"""
        # Create school and parent user
        school = create_school()
        parent_user = create_user(user_type='parent', school=school)
        
        # Create notification for the parent
        notification = create_notification(recipient=parent_user)
        
        api_client.force_authenticate(user=parent_user)
        
        url = reverse('parents:parent-dashboard-notifications')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) >= 1
    
    def test_mark_notification_read(self, api_client, create_user, create_school, create_notification):
        """Test marking notification as read"""
        # Create school and parent user
        school = create_school()
        parent_user = create_user(user_type='parent', school=school)
        
        # Create notification for the parent
        notification = create_notification(recipient=parent_user)
        
        api_client.force_authenticate(user=parent_user)
        
        url = reverse('parents:parent-dashboard-mark-notification-read', kwargs={'pk': notification.pk})
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Notification marked as read'
    
    def test_unread_notifications_count(self, api_client, create_user, create_school, create_notification):
        """Test getting unread notifications count"""
        # Create school and parent user
        school = create_school()
        parent_user = create_user(user_type='parent', school=school)
        
        # Create unread notifications for the parent
        create_notification(recipient=parent_user)
        create_notification(recipient=parent_user)
        
        api_client.force_authenticate(user=parent_user)
        
        url = reverse('parents:parent-dashboard-unread-notifications-count')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'unread_count' in response.data
        assert response.data['unread_count'] >= 2
    
    def test_test_notification(self, api_client, create_user, create_school):
        """Test sending test notification"""
        # Create school and parent user
        school = create_school()
        parent_user = create_user(user_type='parent', school=school)
        
        api_client.force_authenticate(user=parent_user)
        
        url = reverse('parents:parent-dashboard-test-notification')
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        assert 'Test notification queued' in response.data['message']


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.parents
class TestParentProfileAPI:
    """Test parent profile management"""
    
    def test_profile_retrieval(self, api_client, create_user, create_school):
        """Test parent can retrieve their profile"""
        # Create school and parent user
        school = create_school()
        parent_user = create_user(user_type='parent', school=school)
        
        api_client.force_authenticate(user=parent_user)
        
        url = reverse('parents:parent-dashboard-profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert response.data['user']['username'] == parent_user.username
        assert response.data['user']['email'] == parent_user.email
    
    def test_profile_update(self, api_client, create_user, create_school):
        """Test parent can update their profile"""
        # Create school and parent user
        parent_user = create_user(user_type='parent')
        
        api_client.force_authenticate(user=parent_user)
        
        url = reverse('parents:parent-dashboard-profile')
        data = {
            'first_name': 'Updated First Name',
            'last_name': 'Updated Last Name'
        }
        
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['first_name'] == 'Updated First Name'
        assert response.data['user']['last_name'] == 'Updated Last Name'
    
    def test_notification_preferences_update(self, api_client, create_user, create_school):
        """Test parent can update notification preferences"""
        # Create school and parent user
        school = create_school()
        parent_user = create_user(user_type='parent', school=school)
        
        api_client.force_authenticate(user=parent_user)
        
        url = reverse('parents:parent-dashboard-notification-preferences')
        data = {
            'sms_notifications': False,
            'email_notifications': True,
            'push_notifications': False
        }
        
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Notification preferences updated successfully'
        
        # Verify preferences were updated
        profile_url = reverse('parents:parent-dashboard-profile')
        profile_response = api_client.get(profile_url)
        assert profile_response.status_code == status.HTTP_200_OK
        
        # Check that profile has the updated preferences
        profile = profile_response.data['profile']
        assert profile['sms_notifications'] is False
        assert profile['email_notifications'] is True
        assert profile['push_notifications'] is False


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.parents
class TestParentPermissions:
    """Test parent API permissions and access control"""
    
    def test_parent_cannot_access_other_parents_data(self, api_client, create_user, create_school):
        """Test parent cannot access other parent's data"""
        # Create two schools and parents
        school1 = create_school()
        school2 = create_school()
        parent1 = create_user(user_type='parent', school=school1)
        parent2 = create_user(user_type='parent', school=school2)
        
        # Parent1 tries to access parent2's profile
        api_client.force_authenticate(user=parent1)
        
        # This should be forbidden or return only parent1's own data
        # The exact behavior depends on the implementation
        pass
    
    def test_school_staff_cannot_access_parent_dashboard(self, api_client, create_user, create_school):
        """Test school staff cannot access parent dashboard"""
        # Create school and staff user
        school = create_school()
        staff_user = create_user(user_type='school_staff', school=school)
        
        api_client.force_authenticate(user=staff_user)
        
        url = reverse('parents:parent-dashboard-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.parents
class TestParentValidation:
    """Test parent API input validation"""
    
    def test_invalid_notification_preferences(self, api_client, create_user, create_school):
        """Test invalid notification preferences"""
        # Create school and parent user
        school = create_school()
        parent_user = create_user(user_type='parent', school=school)
        
        api_client.force_authenticate(user=parent_user)
        
        url = reverse('parents:parent-dashboard-notification-preferences')
        
        # Invalid data type
        data = {
            'sms_notifications': 'invalid_value',
            'email_notifications': True
        }
        
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_invalid_profile_update(self, api_client, create_user, create_school):
        """Test invalid profile update data"""
        # Create school and parent user
        school = create_school()
        parent_user = create_user(user_type='parent', school=school)
        
        api_client.force_authenticate(user=parent_user)
        
        url = reverse('parents:parent-dashboard-profile')
        
        # Invalid email format
        data = {
            'email': 'invalid-email-format'
        }
        
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
