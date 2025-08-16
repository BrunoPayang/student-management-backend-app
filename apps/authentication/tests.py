from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.schools.models import School

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name="Test School",
            address="123 Test Street",
            phone="+22712345678"
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='parent'
        )
    
    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.user_type, 'parent')
        self.assertTrue(self.user.is_parent())
        self.assertFalse(self.user.is_school_staff())
    
    def test_user_profile_created(self):
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsNotNone(self.user.profile)
    
    def test_school_staff_user(self):
        staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='testpass123',
            user_type='school_staff',
            school=self.school
        )
        self.assertTrue(staff_user.is_school_staff())
        self.assertEqual(staff_user.school, self.school)
    
    def test_admin_user(self):
        admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='testpass123',
            user_type='admin'
        )
        self.assertTrue(admin_user.is_system_admin())
        self.assertIsNone(admin_user.school)


class AuthenticationAPITest(APITestCase):
    def setUp(self):
        self.school = School.objects.create(
            name="Test School",
            address="123 Test Street",
            phone="+22712345678"
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='parent'
        )
    
    def test_user_registration(self):
        url = reverse('authentication:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'user_type': 'parent'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
    
    def test_user_login(self):
        url = reverse('authentication:login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_get_current_user(self):
        # Login first
        self.client.force_authenticate(user=self.user)
        url = reverse('authentication:current_user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_user_context(self):
        # Login first
        self.client.force_authenticate(user=self.user)
        url = reverse('authentication:user_context')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('permissions', response.data)
        self.assertTrue(response.data['permissions']['is_parent'])
    
    def test_password_change(self):
        # Login first
        self.client.force_authenticate(user=self.user)
        url = reverse('authentication:change_password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_fcm_token_update(self):
        # Login first
        self.client.force_authenticate(user=self.user)
        url = reverse('authentication:update_fcm_token')
        data = {
            'fcm_token': 'test_fcm_token_123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_logout(self):
        # Login first
        self.client.force_authenticate(user=self.user)
        url = reverse('authentication:logout')
        data = {
            'refresh_token': 'dummy_token'
        }
        response = self.client.post(url, data)
        # Logout should work even with invalid token (just clear FCM token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SchoolStaffRegistrationTest(APITestCase):
    def setUp(self):
        self.school = School.objects.create(
            name="Test School",
            address="123 Test Street",
            phone="+22712345678"
        )
    
    def test_school_staff_registration_with_school(self):
        url = reverse('authentication:register')
        data = {
            'username': 'staffuser',
            'email': 'staff@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Staff',
            'last_name': 'User',
            'user_type': 'school_staff',
            'school': self.school.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_school_staff_registration_without_school(self):
        url = reverse('authentication:register')
        data = {
            'username': 'staffuser2',
            'email': 'staff2@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Staff',
            'last_name': 'User',
            'user_type': 'school_staff'
            # No school provided
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AdminRegistrationTest(APITestCase):
    def test_admin_registration_with_school(self):
        school = School.objects.create(
            name="Test School",
            address="123 Test Street"
        )
        
        url = reverse('authentication:register')
        data = {
            'username': 'adminuser',
            'email': 'admin@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Admin',
            'last_name': 'User',
            'user_type': 'admin',
            'school': school.id  # Admin shouldn't have school
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_admin_registration_without_school(self):
        url = reverse('authentication:register')
        data = {
            'username': 'adminuser2',
            'email': 'admin2@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Admin',
            'last_name': 'User',
            'user_type': 'admin'
            # No school - this should work
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
