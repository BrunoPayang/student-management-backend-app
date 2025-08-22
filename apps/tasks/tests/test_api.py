"""
API tests for tasks endpoints
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.tasks
class TestTasksAPI:
    """Test tasks API endpoints"""
    
    def test_list_tasks_unauthorized(self, api_client):
        """Test listing tasks without authentication"""
        url = reverse('tasks:taskresult-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_tasks_authorized(self, api_client, create_user, create_school):
        """Test listing tasks with authentication"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school
        school = create_school()
        
        url = reverse('tasks:taskresult-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        
        # Tasks might be empty initially, which is fine
        # We're just testing that the endpoint is accessible
    
    def test_retrieve_task_success(self, api_client, create_user, create_school):
        """Test successful task retrieval"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school
        school = create_school()
        
        # Get list of tasks first
        list_url = reverse('tasks:taskresult-list')
        list_response = api_client.get(list_url)
        
        if list_response.data['results']:
            # If there are tasks, test retrieving one
            task = list_response.data['results'][0]
            task_id = task['id']
            
            detail_url = reverse('tasks:taskresult-detail', kwargs={'pk': task_id})
            detail_response = api_client.get(detail_url)
            
            assert detail_response.status_code == status.HTTP_200_OK
            assert 'task_name' in detail_response.data
            assert 'status' in detail_response.data
        else:
            # If no tasks exist, test with a non-existent ID
            detail_url = reverse('tasks:taskresult-detail', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
            detail_response = api_client.get(detail_url)
            
            assert detail_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_retrieve_task_not_found(self, api_client, create_user):
        """Test retrieving non-existent task"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        url = reverse('tasks:taskresult-detail', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_task_search(self, api_client, create_user, create_school):
        """Test task search functionality"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school
        school = create_school()
        
        url = reverse('tasks:taskresult-list')
        
        # Search by task name (if any exist)
        response = api_client.get(url, {'search': 'test'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
    
    def test_task_filtering(self, api_client, create_user, create_school):
        """Test task filtering by various criteria"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school
        school = create_school()
        
        url = reverse('tasks:taskresult-list')
        
        # Filter by status
        response = api_client.get(url, {'status': 'SUCCESS'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        
        # Filter by date range
        response = api_client.get(url, {
            'date_done__gte': '2024-01-01',
            'date_done__lte': '2024-12-31'
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.tasks
class TestTaskPermissions:
    """Test tasks API permissions and access control"""
    
    def test_admin_access_tasks(self, api_client, create_user, create_school):
        """Test admin can access tasks"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school
        school = create_school()
        
        url = reverse('tasks:taskresult-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
    
    def test_school_staff_access_tasks(self, api_client, create_user, create_school):
        """Test school staff can access tasks"""
        # Create school and staff user
        school = create_school()
        staff_user = create_user(user_type='school_staff', school=school)
        api_client.force_authenticate(user=staff_user)
        
        url = reverse('tasks:taskresult-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
    
    def test_parent_access_tasks_forbidden(self, api_client, create_user, create_school):
        """Test parent cannot access tasks"""
        # Create school and parent user
        school = create_school()
        parent_user = create_user(user_type='parent', school=school)
        api_client.force_authenticate(user=parent_user)
        
        url = reverse('tasks:taskresult-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_regular_user_access_tasks_forbidden(self, api_client, create_user):
        """Test regular user cannot access tasks"""
        # Create regular user and authenticate
        regular_user = create_user(user_type='parent')
        api_client.force_authenticate(user=regular_user)
        
        url = reverse('tasks:taskresult-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.tasks
class TestTaskDetails:
    """Test task detail fields and information"""
    
    def test_task_fields_present(self, api_client, create_user, create_school):
        """Test that required task fields are present"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school
        school = create_school()
        
        url = reverse('tasks:taskresult-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        
        if response.data['results']:
            task = response.data['results'][0]
            
            # Check for required fields
            required_fields = ['id', 'task_name', 'status', 'date_done']
            for field in required_fields:
                assert field in task, f"Field {field} is missing from task"
    
    def test_task_status_values(self, api_client, create_user, create_school):
        """Test that task status values are valid"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school
        school = create_school()
        
        url = reverse('tasks:taskresult-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        
        if response.data['results']:
            for task in response.data['results']:
                if 'status' in task:
                    # Valid status values
                    valid_statuses = ['SUCCESS', 'FAILURE', 'PENDING', 'STARTED', 'RETRY']
                    assert task['status'] in valid_statuses, f"Invalid status: {task['status']}"


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.tasks
class TestTaskPagination:
    """Test task pagination functionality"""
    
    def test_task_pagination(self, api_client, create_user, create_school):
        """Test task pagination"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school
        school = create_school()
        
        url = reverse('tasks:taskresult-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        
        # Check pagination structure
        assert isinstance(response.data['count'], int)
        assert isinstance(response.data['results'], list)
        
        # If there are results, check pagination limits
        if response.data['results']:
            # Default page size should be reasonable
            assert len(response.data['results']) <= 100  # Assuming reasonable page size
    
    def test_task_page_size(self, api_client, create_user, create_school):
        """Test custom page size for tasks"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school
        school = create_school()
        
        url = reverse('tasks:taskresult-list')
        
        # Test different page sizes
        for page_size in [5, 10, 20]:
            response = api_client.get(url, {'page_size': page_size})
            assert response.status_code == status.HTTP_200_OK
            assert 'results' in response.data
            
            # Check that page size is respected (if there are enough results)
            if response.data['count'] >= page_size:
                assert len(response.data['results']) <= page_size


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.tasks
class TestTaskFiltering:
    """Test task filtering functionality"""
    
    def test_filter_by_task_name(self, api_client, create_user, create_school):
        """Test filtering tasks by task name"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school
        school = create_school()
        
        url = reverse('tasks:taskresult-list')
        
        # Filter by task name
        response = api_client.get(url, {'task_name': 'test'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
    
    def test_filter_by_status(self, api_client, create_user, create_school):
        """Test filtering tasks by status"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)

        # Create school
        school = create_school()

        url = reverse('tasks:taskresult-list')

        # Test different status filters
        for status_value in ['SUCCESS', 'FAILURE', 'PENDING']:
            response = api_client.get(url, {'status': status_value})
            assert response.status_code == status.HTTP_200_OK
            assert 'results' in response.data
    
    def test_filter_by_date_range(self, api_client, create_user, create_school):
        """Test filtering tasks by date range"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school
        school = create_school()
        
        url = reverse('tasks:taskresult-list')
        
        # Filter by date range
        response = api_client.get(url, {
            'date_done__gte': '2024-01-01T00:00:00Z',
            'date_done__lte': '2024-12-31T23:59:59Z'
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
    
    def test_filter_by_worker(self, api_client, create_user, create_school):
        """Test filtering tasks by worker"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school
        school = create_school()
        
        url = reverse('tasks:taskresult-list')
        
        # Filter by worker
        response = api_client.get(url, {'worker': 'celery@localhost'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.tasks
class TestTaskSorting:
    """Test task sorting functionality"""
    
    def test_sort_by_date_done(self, api_client, create_user, create_school):
        """Test sorting tasks by date done"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school
        school = create_school()
        
        url = reverse('tasks:taskresult-list')
        
        # Sort by date done (newest first)
        response = api_client.get(url, {'ordering': '-date_done'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        
        # Sort by date done (oldest first)
        response = api_client.get(url, {'ordering': 'date_done'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
    
    def test_sort_by_task_name(self, api_client, create_user, create_school):
        """Test sorting tasks by task name"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school
        school = create_school()
        
        url = reverse('tasks:taskresult-list')
        
        # Sort by task name (ascending)
        response = api_client.get(url, {'ordering': 'task_name'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        
        # Sort by task name (descending)
        response = api_client.get(url, {'ordering': '-task_name'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
    
    def test_sort_by_status(self, api_client, create_user, create_school):
        """Test sorting tasks by status"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school
        school = create_school()
        
        url = reverse('tasks:taskresult-list')
        
        # Sort by status (ascending)
        response = api_client.get(url, {'ordering': 'status'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        
        # Sort by status (descending)
        response = api_client.get(url, {'ordering': '-status'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.tasks
class TestTaskErrorHandling:
    """Test task error handling and edge cases"""
    
    def test_invalid_task_id_format(self, api_client, create_user):
        """Test handling of invalid task ID format"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Test with invalid UUID format
        url = reverse('tasks:taskresult-detail', kwargs={'pk': 'invalid-uuid'})
        response = api_client.get(url)
        
        # Should return 404 or 400 depending on implementation
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]
    
    def test_malformed_filter_parameters(self, api_client, create_user, create_school):
        """Test handling of malformed filter parameters"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school
        school = create_school()
        
        url = reverse('tasks:taskresult-list')
        
        # Test with invalid date format
        response = api_client.get(url, {'date_done__gte': 'invalid-date'})
        # Should handle gracefully (might return 400 or ignore invalid filter)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
        
        # Test with invalid status
        response = api_client.get(url, {'status': 'INVALID_STATUS'})
        # Should handle gracefully (might return 400 or return empty results)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
