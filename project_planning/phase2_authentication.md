# Phase 2: Authentication System (Week 1 - Days 3-4)

## Overview
Implement JWT-based authentication with custom User model, role-based access control, and multi-tenant user management.

## Task 2.1: User Model & JWT Setup

### Step 1: Create Custom User Model
**apps/authentication/models.py**
```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    USER_TYPES = [
        ('admin', 'System Admin'),
        ('school_staff', 'School Staff'),
        ('parent', 'Parent/Guardian'),
    ]
    
    # Additional fields
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPES,
        default='parent'
    )
    
    # School relationship (nullable for system admins)
    school = models.ForeignKey(
        'schools.School', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='users'
    )
    
    # Contact information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{8,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True,
        help_text="Phone number for SMS notifications"
    )
    
    # Firebase Cloud Messaging token for push notifications
    fcm_token = models.TextField(
        blank=True,
        help_text="Firebase Cloud Messaging token for push notifications"
    )
    
    # Profile fields
    profile_picture = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def is_system_admin(self):
        return self.user_type == 'admin'
    
    def is_school_staff(self):
        return self.user_type == 'school_staff'
    
    def is_parent(self):
        return self.user_type == 'parent'
    
    def get_school_context(self):
        """Return school context for multi-tenant operations"""
        if self.school:
            return {
                'school_id': self.school.id,
                'school_slug': self.school.slug,
                'school_name': self.school.name
            }
        return None


class UserProfile(models.Model):
    """
    Extended profile information for users
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Additional contact information
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=17, blank=True)
    
    # Preferences
    language_preference = models.CharField(
        max_length=10,
        choices=[
            ('en', 'English'),
            ('fr', 'French'),
            ('ha', 'Hausa'),
        ],
        default='fr'
    )
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"


# Signal to create user profile automatically
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
```

### Step 2: Create User Serializers
**apps/authentication/serializers.py**
```python
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'address', 'emergency_contact', 'language_preference',
            'email_notifications', 'sms_notifications', 'push_notifications'
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    school_name = serializers.CharField(source='school.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'user_type', 'school', 'school_name', 
            'phone', 'profile_picture', 'is_verified', 'profile',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_verified']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'user_type', 'school', 'phone'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas")
        
        # Validate school assignment based on user type
        # Only 'school_staff' users must be linked to a school; parents do not require a school assignment.
        if attrs['user_type'] == 'school_staff' and not attrs.get('school'):
            raise serializers.ValidationError("L'école est obligatoire pour les utilisateurs du personnel de l'école.")
        
        if attrs['user_type'] == 'admin' and attrs.get('school'):
            raise serializers.ValidationError("L'administrateur du système ne doit pas être affecté à une école")
        
        #validate username
        # Username validation: must be alphanumeric, 4-30 chars, no spaces or special chars except underscore
        import re
        username = attrs.get('username')
        if not username:
            raise serializers.ValidationError("Le nom d'utilisateur est requis")
        if not re.match(r'^[a-zA-Z0-9_]{4,30}$', username):
            raise serializers.ValidationError(
                "Le nom d'utilisateur doit être composé de 4 à 30 caractères, ne contenir que des lettres, des chiffres ou des traits de soulignement, et ne pas comporter d'espaces."
            )
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Le nom d'utilisateur est déjà pris")
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError('Informations d\'identification invalides')
            
            if not user.is_active:
                raise serializers.ValidationError('Le compte d\'utilisateur est désactivé')
            
            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError('Doit inclure le nom d\'utilisateur et le mot de passe')


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


### Step 3: Create Authentication Views
**apps/authentication/views.py**
```python
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404

from .models import User
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    PasswordChangeSerializer, FCMTokenSerializer
)
from .permissions import IsOwnerOrAdmin


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view that includes user data in response
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Get user data
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                user_serializer = UserSerializer(user)
                
                # Add user data to response
                response.data['user'] = user_serializer.data
                
                # Log the login
                import logging
                logger = logging.getLogger('edusync')
                logger.info(f"User {user.username} logged in successfully")
        
        return response


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Return user data with tokens
        user_serializer = UserSerializer(user)
        
        return Response({
            'user': user_serializer.data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """
    Logout endpoint that blacklists the refresh token
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Clear FCM token on logout
            request.user.fcm_token = ''
            request.user.save()
            
            return Response({
                'message': 'Successfully logged out'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile view for authenticated users
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """
    Change password endpoint
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UpdateFCMTokenView(APIView):
    """
    Update FCM token for push notifications
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = FCMTokenSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'FCM token updated successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class PasswordResetRequestView(APIView):
    """
    Request password reset via email
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link (you'll need to implement frontend route)
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            
            # Send email
            send_mail(
                subject='EduSync Niger - Password Reset',
                message=f'Click the link to reset your password: {reset_link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            return Response({
                'message': 'Password reset email sent'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Don't reveal if email exists or not
            return Response({
                'message': 'If the email exists, a reset link has been sent'
            }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with token
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        if not all([uid, token, new_password]):
            return Response({
                'error': 'All fields are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Decode user ID
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            
            # Verify token
            if default_token_generator.check_token(user, token):
                # Validate password
                from django.contrib.auth.password_validation import validate_password
                validate_password(new_password)
                
                # Set new password
                user.set_password(new_password)
                user.save()
                
                return Response({
                    'message': 'Password reset successful'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Invalid or expired token'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except (User.DoesNotExist, ValueError, OverflowError):
            return Response({
                'error': 'Invalid reset link'
            }, status=status.HTTP_400_BAD_REQUEST)


# API endpoint to get current user info
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    """
    Get current authenticated user information
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_context(request):
    """
    Get user context information for frontend (school, permissions, etc.)
    """
    user = request.user
    context = {
        'user_id': user.id,
        'username': user.username,
        'user_type': user.user_type,
        'permissions': {
            'is_admin': user.is_system_admin(),
            'is_school_staff': user.is_school_staff(),
            'is_parent': user.is_parent(),
        }
    }
    
    # Add school context if applicable
    school_context = user.get_school_context()
    if school_context:
        context['school'] = school_context
    
    return Response(context)
```

## Task 2.2: Role-Based Access Control

### Step 1: Create Custom Permissions
**apps/authentication/permissions.py**
```python
from rest_framework import permissions


class IsSystemAdmin(permissions.BasePermission):
    """
    Permission class for system administrators only
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.is_system_admin()
        )


class IsSchoolStaff(permissions.BasePermission):
    """
    Permission class for school staff only
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.is_school_staff()
        )


class IsParent(permissions.BasePermission):
    """
    Permission class for parents only
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.is_parent()
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class that allows owners and system admins
    """
    def has_object_permission(self, request, view, obj):
        # System admins can access everything
        if request.user.is_system_admin():
            return True
        
        # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return obj == request.user


class IsInSameSchool(permissions.BasePermission):
    """
    Permission class that checks if users are in the same school
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.school is not None
    
    def has_object_permission(self, request, view, obj):
        # System admins can access everything
        if request.user.is_system_admin():
            return True
        
        # Check if object belongs to the same school
        if hasattr(obj, 'school'):
            return obj.school == request.user.school
        
        return False


class IsSchoolStaffOrSystemAdmin(permissions.BasePermission):
    """
    Permission class for school staff and system administrators
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.is_school_staff() or request.user.is_system_admin())
        )


class CanManageUsers(permissions.BasePermission):
    """
    Permission class for user management operations
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # System admins can manage all users
        if request.user.is_system_admin():
            return True
        
        # School staff can manage users in their school
        if request.user.is_school_staff():
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # System admins can manage all users
        if request.user.is_system_admin():
            return True
        
        # School staff can only manage users in their school
        if request.user.is_school_staff():
            return obj.school == request.user.school
        
        return False
```

### Step 2: Create Multi-Tenant Middleware
**apps/common/middleware.py**
```python
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from apps.schools.models import School


class SchoolTenantMiddleware(MiddlewareMixin):
    """
    Middleware to handle multi-tenant school context
    """
    def process_request(self, request):
        # Skip for admin and authentication endpoints
        if request.path.startswith('/admin/') or request.path.startswith('/api/auth/'):
            return None
        
        # Get school context from user or request headers
        school = None
        
        if request.user.is_authenticated:
            if request.user.school:
                school = request.user.school
            elif request.user.is_system_admin():
                # System admin can access all schools
                # Check for school_id in headers or query params
                school_id = request.headers.get('X-School-ID') or request.GET.get('school_id')
                if school_id:
                    try:
                        school = School.objects.get(id=school_id)
                    except School.DoesNotExist:
                        pass
        
        # Set school context in request
        request.school = school
        return None


class APILoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log API requests for monitoring
    """
    def process_request(self, request):
        if request.path.startswith('/api/'):
            import logging
            logger = logging.getLogger('edusync')
            
            user_info = 'Anonymous'
            if request.user.is_authenticated:
                user_info = f"{request.user.username} ({request.user.user_type})"
            
            logger.info(
                f"API Request: {request.method} {request.path} - User: {user_info}"
            )
        
        return None
```

### Step 3: Create Utility Decorators
**apps/common/decorators.py**
```python
from functools import wraps
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status


def require_user_type(*allowed_types):
    """
    Decorator to restrict views to specific user types
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({
                    'error': 'Authentication required'
                }, status=401)
            
            if request.user.user_type not in allowed_types:
                return JsonResponse({
                    'error': 'Insufficient permissions'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def require_same_school(view_func):
    """
    Decorator to ensure users can only access data from their school
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'error': 'Authentication required'
            }, status=401)
        
        # System admins can access everything
        if request.user.is_system_admin():
            return view_func(request, *args, **kwargs)
        
        # Check if user has school context
        if not request.user.school:
            return JsonResponse({
                'error': 'User not associated with any school'
            }, status=403)
        
        return view_func(request, *args, **kwargs)
    return wrapped_view


def log_user_action(action_type):
    """
    Decorator to log user actions for audit purposes
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            import logging
            logger = logging.getLogger('edusync')
            
            user_info = 'Anonymous'
            if request.user.is_authenticated:
                user_info = f"{request.user.username} ({request.user.user_type})"
            
            logger.info(f"Action: {action_type} - User: {user_info} - Path: {request.path}")
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
```

### Step 4: Update Authentication URLs
**apps/authentication/urls.py**
```python
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'authentication'

urlpatterns = [
    # JWT Authentication endpoints
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # User management endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # Password reset endpoints
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Utility endpoints
    path('current-user/', views.current_user, name='current_user'),
    path('user-context/', views.user_context, name='user_context'),
    
    # FCM token management
    path('fcm-token/', views.UpdateFCMTokenView.as_view(), name='update_fcm_token'),
]
```

### Step 5: Create Database Migration
Create and run migrations for the new User model:

```bash
# Create migration for authentication app
python manage.py makemigrations authentication

# Since we're using a custom user model, we need to create the schools app first
# We'll do this in Phase 3, but for now create a minimal School model

# Create migration
python manage.py migrate
```

### Step 6: Update Django Admin
**apps/authentication/admin.py**
```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'user_type', 'school', 'is_verified', 'is_active'
    ]
    list_filter = [
        'user_type', 'school', 'is_verified', 'is_active',
        'is_staff', 'is_superuser', 'created_at'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Additional Info'), {
            'fields': ('user_type', 'school', 'phone', 'profile_picture', 'fcm_token', 'is_verified')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    inlines = [UserProfileInline]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'language_preference', 'email_notifications', 'push_notifications']
    list_filter = ['language_preference', 'email_notifications', 'sms_notifications', 'push_notifications']
    search_fields = ['user__username', 'user__email']
```

## Testing Phase 2 Completion

### Step 1: Create Test Cases
**apps/authentication/tests.py**
```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
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


class AuthenticationAPITest(APITestCase):
    def setUp(self):
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
```

### Step 2: Run Tests
```bash
# Run authentication app tests
python manage.py test apps.authentication

# Run all tests
python manage.py test
```

### Step 3: Manual API Testing
Create a test script or use Postman to test endpoints:

**test_auth_endpoints.py**
```python
import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api/auth'

# Test user registration
def test_registration():
    url = f'{BASE_URL}/register/'
    data = {
        'username': 'testparent',
        'email': 'parent@test.com',
        'password': 'testpass123',
        'password_confirm': 'testpass123',
        'first_name': 'Test',
        'last_name': 'Parent',
        'user_type': 'parent',
        'phone': '+22712345678'
    }
    
    response = requests.post(url, json=data)
    print(f"Registration: {response.status_code}")
    print(response.json())
    return response.json()

# Test login
def test_login():
    url = f'{BASE_URL}/login/'
    data = {
        'username': 'testparent',
        'password': 'testpass123'
    }
    
    response = requests.post(url, json=data)
    print(f"Login: {response.status_code}")
    result = response.json()
    print(result)
    return result.get('access')

# Test protected endpoint
def test_current_user(access_token):
    url = f'{BASE_URL}/current-user/'
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(url, headers=headers)
    print(f"Current User: {response.status_code}")
    print(response.json())

if __name__ == '__main__':
    # Run tests
    test_registration()
    access_token = test_login()
    if access_token:
        test_current_user(access_token)
```

## Success Criteria for Phase 2:
- [ ] Custom User model created and migrated
- [ ] JWT authentication working (login/logout/refresh)
- [ ] User registration with validation
- [ ] Role-based permissions implemented
- [ ] Password change functionality
- [ ] FCM token management
- [ ] Password reset via email
- [ ] User profile management
- [ ] All authentication tests passing
- [ ] API endpoints properly documented and testable

## Common Issues and Solutions:

### Issue 1: Migration Problems with Custom User Model
**Problem**: Django complains about changing AUTH_USER_MODEL
**Solution**: 
- Ensure AUTH_USER_MODEL is set before first migration
- If needed, reset migrations and start fresh

### Issue 2: JWT Token Issues
**Problem**: Tokens not being accepted
**Solution**:
- Check SIMPLE_JWT configuration in settings
- Verify Authorization header format: "Bearer {token}"

### Issue 3: Permission Denied Errors
**Problem**: Users can't access endpoints they should have access to
**Solution**:
- Check permission classes on views
- Verify user.user_type is set correctly
- Test with is_authenticated check first

## Next Steps:
Once Phase 2 is validated and all authentication endpoints are working, we'll move to **Phase 3: Core Models & Database** where we'll:
- Create School model with branding fields
- Create Student and relationship models
- Set up academic record models
- Configure database migrations and seeding

Ready to implement Phase 2, or do you have questions about the authentication system?


class FCMTokenSerializer(serializers.Serializer):
    fcm_token = serializers.CharField(max_length=500)
    
    def save(self):
        user = self.context['request'].user
        user.fcm_token = self.validated_data['fcm_token']
        user.save()
        return user