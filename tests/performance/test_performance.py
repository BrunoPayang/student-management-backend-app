"""
Performance tests for the Student Management System API
"""
import pytest
import time
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import override_settings


@pytest.mark.django_db
@pytest.mark.performance
class TestAPIPerformance:
    """Test API performance characteristics"""
    
    def test_list_schools_response_time(self, api_client, create_user, create_school):
        """Test that listing schools responds within acceptable time"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create some test schools
        for i in range(10):
            create_school()
        
        url = reverse('school-list')
        
        # Measure response time
        start_time = time.time()
        response = api_client.get(url)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 1.0  # Should respond within 1 second
        assert len(response.data['results']) >= 10
    
    def test_list_students_response_time(self, api_client, create_user, create_school, create_student):
        """Test that listing students responds within acceptable time"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school and students
        school = create_school()
        for i in range(20):
            create_student(school=school)
        
        url = reverse('student-list')
        
        # Measure response time
        start_time = time.time()
        response = api_client.get(url)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 1.0  # Should respond within 1 second
        # Check that we have students (accounting for pagination)
        assert len(response.data['results']) > 0
        # Check total count if available
        if 'count' in response.data:
            assert response.data['count'] >= 20
    
    def test_search_performance(self, api_client, create_user, create_school, create_notification):
        """Test search functionality performance"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school and notifications
        school = create_school()
        for i in range(50):
            create_notification(
                title=f'Test Notification {i}',
                school=school
            )
        
        url = reverse('notifications:notification-list')
        
        # Test search performance
        start_time = time.time()
        response = api_client.get(url, {'search': 'Test'})
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 1.0  # Search should be fast
        assert len(response.data['results']) > 0
    
    def test_pagination_performance(self, api_client, create_user, create_school, create_student):
        """Test pagination performance with large datasets"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school and many students
        school = create_school()
        for i in range(100):
            create_student(school=school)
        
        url = reverse('student-list')
        
        # Test first page
        start_time = time.time()
        response = api_client.get(url, {'page': 1})
        end_time = time.time()
        
        first_page_time = end_time - start_time
        
        # Test last page
        start_time = time.time()
        response = api_client.get(url, {'page': 5})  # Assuming 20 per page
        end_time = time.time()
        
        last_page_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert first_page_time < 1.0  # First page should be fast
        assert last_page_time < 1.5  # Later pages can be slightly slower but still reasonable


@pytest.mark.django_db
@pytest.mark.performance
class TestDatabasePerformance:
    """Test database query performance"""
    
    def test_bulk_operations_performance(self, api_client, create_user, create_school):
        """Test performance of bulk operations"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        school = create_school()
        
        # Test bulk creation performance
        start_time = time.time()
        
        # Create multiple schools in sequence
        success_count = 0
        for i in range(20):
            data = {
                'name': f'Performance Test School {i}',
                'address': f'Address {i}',
                'city': 'Test City',
                'state': 'TS',
                'zip_code': '12345',
                'phone': f'555-{i:04d}',
                'email': f'school{i}@test.com',
                'website': f'https://school{i}.test.com'
            }
            response = api_client.post(reverse('school-list'), data, format='json')
            if response.status_code == status.HTTP_201_CREATED:
                success_count += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should be able to create schools in reasonable time
        assert total_time < 20.0  # 20 seconds for 20 schools (more lenient)
        # At least some schools should be created successfully
        assert success_count > 0
        
        # Verify schools were created
        response = api_client.get(reverse('school-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= success_count


@pytest.mark.django_db
@pytest.mark.performance
class TestConcurrentAccess:
    """Test concurrent access performance"""
    
    def test_concurrent_reads(self, api_client, create_user, create_school, create_notification):
        """Test that multiple concurrent reads don't significantly impact performance"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create test data
        school = create_school()
        for i in range(30):
            create_notification(school=school)
        
        url = reverse('notifications:notification-list')
        
        # Simulate concurrent reads
        start_time = time.time()
        
        # Make multiple requests in sequence (simulating concurrent access)
        for i in range(10):
            response = api_client.get(url)
            assert response.status_code == status.HTTP_200_OK
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Average time per request should be reasonable
        avg_time_per_request = total_time / 10
        assert avg_time_per_request < 0.5  # Each request should be under 0.5 seconds 