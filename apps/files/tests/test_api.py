"""
API tests for files endpoints
"""
import pytest
from django.urls import reverse
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.files
class TestFilesAPI:
    """Test files API endpoints"""
    
    def test_list_files_unauthorized(self, api_client):
        """Test listing files without authentication"""
        url = reverse('files:file-upload-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_files_authorized(self, api_client, create_user, create_school, create_file_upload):
        """Test listing files with authentication"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school and files
        school = create_school()
        file1 = create_file_upload(school=school, uploaded_by=admin_user)
        file2 = create_file_upload(school=school, uploaded_by=admin_user)
        
        url = reverse('files:file-upload-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 2
        
        # Check that our files are in the results
        file_names = [file_obj['original_name'] for file_obj in response.data['results']]
        assert file1.original_name in file_names
        assert file2.original_name in file_names
    
    def test_upload_file_success(self, api_client, create_user, create_school):
        """Test successful file upload"""
        # Create school first
        school = create_school()
        
        # Create admin user with school (admin users need schools for file uploads)
        admin_user = create_user(user_type='admin', school=school)
        api_client.force_authenticate(user=admin_user)
        
        # Create a test file
        test_file = SimpleUploadedFile(
            "test_document.pdf",
            b"file_content_here",
            content_type="application/pdf"
        )
        
        url = reverse('files:file-upload-list')
        data = {
            'description': 'A test document for testing',
            'file': test_file,
            'file_type': 'student_document',
            'tags': 'test,document,pdf'
        }
        
        response = api_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['original_name'] == 'test_document.pdf'
        assert response.data['file_type'] == 'student_document'
        assert 'test' in response.data['tags']
    
    def test_upload_file_unauthorized(self, api_client, create_user, create_school):
        """Test file upload by unauthorized user"""
        # Create regular user and authenticate
        regular_user = create_user(user_type='parent')
        api_client.force_authenticate(user=regular_user)
        
        # Create school
        school = create_school()
        
        # Create a test file
        test_file = SimpleUploadedFile(
            "unauthorized.pdf",
            b"file_content_here",
            content_type="application/pdf"
        )
        
        url = reverse('files:file-upload-list')
        data = {
            'description': 'This should fail',
            'file': test_file,
            'file_type': 'student_document'
        }
        
        response = api_client.post(url, data, format='multipart')
        # Parents can't upload files (only school staff and admins can)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_retrieve_file_success(self, api_client, create_user, create_file_upload):
        """Test successful file retrieval"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create a file
        file_obj = create_file_upload(uploaded_by=admin_user)
        
        url = reverse('files:file-upload-detail', kwargs={'pk': file_obj.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['original_name'] == file_obj.original_name
        assert response.data['file_type'] == file_obj.file_type
    
    def test_retrieve_file_not_found(self, api_client, create_user):
        """Test retrieving non-existent file"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        url = reverse('files:file-upload-detail', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_file_admin_success(self, api_client, create_user, create_file_upload):
        """Test successful file update by admin"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create a file
        file_obj = create_file_upload(uploaded_by=admin_user)
        
        url = reverse('files:file-upload-detail', kwargs={'pk': file_obj.pk})
        data = {
            'description': 'Updated description'
        }
        
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['description'] == 'Updated description'
    
    def test_update_file_non_admin_forbidden(self, api_client, create_user, create_file_upload):
        """Test file update by non-admin user is forbidden"""
        # Create regular user and authenticate
        regular_user = create_user(user_type='parent')
        api_client.force_authenticate(user=regular_user)

        # Create a file
        file_obj = create_file_upload(uploaded_by=regular_user)
        
        url = reverse('files:file-upload-detail', kwargs={'pk': file_obj.pk})
        data = {'description': 'Unauthorized Update'}
        
        response = api_client.patch(url, data, format='json')
        # Parents can't update files (only school staff and admins can)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_file_admin_success(self, api_client, create_user, create_file_upload):
        """Test successful file deletion by admin"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create a file
        file_obj = create_file_upload(uploaded_by=admin_user)
        
        url = reverse('files:file-upload-detail', kwargs={'pk': file_obj.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify file is deleted
        get_response = api_client.get(url)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_file_search(self, api_client, create_user, create_school, create_file_upload):
        """Test file search functionality"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)

        # Create school and files
        school = create_school()
        create_file_upload(original_name='Alpha Document', school=school, uploaded_by=admin_user)        
        create_file_upload(original_name='Beta Report', school=school, uploaded_by=admin_user)
        create_file_upload(original_name='Gamma Image', school=school, uploaded_by=admin_user)

        url = reverse('files:file-upload-list')

        # Search by title
        response = api_client.get(url, {'search': 'Alpha'})
        assert response.status_code == status.HTTP_200_OK
        # Search should return files containing 'Alpha' in name, description, or tags
        assert any('Alpha' in file_obj['original_name'] for file_obj in response.data['results'])
        
        # Search by file type
        response = api_client.get(url, {'search': 'Report'})
        assert response.status_code == status.HTTP_200_OK
        # Search should return files containing 'Report' in name, description, or tags
        assert any('Report' in file_obj['original_name'] for file_obj in response.data['results'])
    
    def test_file_filtering(self, api_client, create_user, create_school, create_file_upload):
        """Test file filtering by various criteria"""
        # Create admin user and authenticate
        admin_user = create_user(user_type='admin')
        api_client.force_authenticate(user=admin_user)
        
        # Create school and files
        school = create_school()
        create_file_upload(file_type='student_document', school=school, uploaded_by=admin_user)
        create_file_upload(file_type='other', school=school, uploaded_by=admin_user)
        create_file_upload(file_type='student_document', school=school, uploaded_by=admin_user)
        
        url = reverse('files:file-upload-list')
        
        # Filter by file type
        response = api_client.get(url, {'file_type': 'student_document'})
        assert response.status_code == status.HTTP_200_OK
        assert all(file_obj['file_type'] == 'student_document' for file_obj in response.data['results'])
        
        # Filter by multiple criteria
        response = api_client.get(url, {'file_type': 'student_document', 'school': school.pk})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
