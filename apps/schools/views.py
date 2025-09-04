from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import School, SchoolConfiguration
from .serializers import (
    SchoolListSerializer, SchoolDetailSerializer,
    SchoolCreateSerializer, SchoolUpdateSerializer,
    SchoolConfigurationSerializer, SchoolConfigurationDetailSerializer
)
from apps.common.pagination import StandardResultsSetPagination


@extend_schema_view(
    list=extend_schema(
        summary="List Schools",
        description="""
        Retrieve a list of schools with filtering and pagination.
        
        **Permissions:**
        - Super admins: Can view all schools
        - School staff: Can only view their own school
        - Other users: No access
        """,
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search schools by name, email, or address'
            ),
            OpenApiParameter(
                name='school_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by school type: primary, secondary, both, university, other'
            ),
            OpenApiParameter(
                name='city',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by city'
            ),
            OpenApiParameter(
                name='state',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by state'
            ),
            OpenApiParameter(
                name='is_active',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by active status'
            ),
            OpenApiParameter(
                name='is_verified',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by verification status'
            ),
        ],
        examples=[
            OpenApiExample(
                'List all schools',
                summary='List all schools',
                description='Get a paginated list of all schools',
                value={
                    "count": 25,
                    "next": "http://api.example.com/api/schools/?page=2",
                    "previous": None,
                    "results": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "École Primaire de Niamey",
                            "slug": "ecole-primaire-niamey",
                            "school_type": "primary",
                            "city": "Niamey",
                            "state": "Niamey",
                            "is_active": True,
                            "is_verified": True,
                            "student_count": 150,
                            "staff_count": 12
                        }
                    ]
                }
            )
        ]
    ),
    create=extend_schema(
        summary="Create School",
        description="""
        Create a new school with default configuration.
        
        **Permissions:**
        - Only super admins can create schools
        
        **Note:** A default school configuration will be automatically created.
        
        **Request Body Fields:**
        - **Required**: `name`, `school_type`, `contact_email`
        - **Optional**: `academic_year`, `logo`, `primary_color`, `secondary_color`, `contact_phone`, `website`, `address`, `city`, `state`, `country`, `postal_code`, `is_active`, `is_verified`
        """,
        request=SchoolCreateSerializer,
        examples=[
            OpenApiExample(
                'Create school - Minimal',
                summary='Create school with minimal required fields',
                description='Create a new school with only required fields',
                value={
                    "name": "École Primaire de Zinder",
                    "school_type": "primary",
                    "contact_email": "contact@ecole-zinder.ne"
                }
            ),
            OpenApiExample(
                'Create school - Complete',
                summary='Create school with all fields',
                description='Create a new school with all available fields',
                value={
                    "name": "École Secondaire de Maradi",
                    "school_type": "secondary",
                    "academic_year": "2024-2025",
                    "logo": "https://firebase-storage.com/schools/logos/maradi-logo.png",
                    "primary_color": "#1976D2",
                    "secondary_color": "#424242",
                    "contact_email": "contact@ecole-maradi.ne",
                    "contact_phone": "+22712345678",
                    "website": "https://ecole-maradi.ne",
                    "address": "Quartier Sabon Gari, Maradi",
                    "city": "Maradi",
                    "state": "Maradi",
                    "country": "Niger",
                    "postal_code": "8000",
                    "is_active": True,
                    "is_verified": False
                }
            ),
            OpenApiExample(
                'Create school - University',
                summary='Create university',
                description='Create a university with specific settings',
                value={
                    "name": "Université Abdou Moumouni de Niamey",
                    "school_type": "university",
                    "academic_year": "2024-2025",
                    "primary_color": "#8E24AA",
                    "secondary_color": "#E1BEE7",
                    "contact_email": "info@uam.ne",
                    "contact_phone": "+22720734567",
                    "website": "https://www.uam.ne",
                    "address": "Campus Universitaire, Niamey",
                    "city": "Niamey",
                    "state": "Niamey",
                    "country": "Niger",
                    "postal_code": "10000",
                    "is_active": True,
                    "is_verified": True
                }
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Retrieve School",
        description="""
        Retrieve detailed information about a specific school.
        
        **Permissions:**
        - Super admins: Can view any school
        - School staff: Can only view their own school
        - Other users: No access
        """,
        examples=[
            OpenApiExample(
                'School details',
                summary='Get school details',
                description='Retrieve complete school information including configuration',
                value={
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "École Primaire de Niamey",
                    "slug": "ecole-primaire-niamey",
                    "school_type": "primary",
                    "academic_year": "2024-2025",
                    "logo": "https://firebase-storage.com/schools/logos/logo.png",
                    "primary_color": "#1976D2",
                    "secondary_color": "#424242",
                    "contact_email": "contact@ecole-niamey.ne",
                    "contact_phone": "+22712345678",
                    "website": "https://ecole-niamey.ne",
                    "address": "Quartier Plateau, Niamey",
                    "city": "Niamey",
                    "state": "Niamey",
                    "country": "Niger",
                    "postal_code": "10000",
                    "is_active": True,
                    "is_verified": True,
                    "student_count": 150,
                    "staff_count": 12,
                    "configuration": {
                        "academic_year_start": "2024-09-01",
                        "academic_year_end": "2025-06-30",
                        "current_semester": "first",
                        "enable_sms_notifications": True,
                        "enable_email_notifications": True,
                        "enable_push_notifications": True,
                        "currency": "NGN",
                        "payment_reminder_days": 7,
                        "max_file_size_mb": 10,
                        "allowed_file_types": [".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"]
                    },
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-09-04T14:20:00Z"
                }
            )
        ]
    ),
    update=extend_schema(
        summary="Update School",
        description="""
        Update school information (full update).
        
        **Permissions:**
        - Super admins: Can update any school
        - School staff: Can only update their own school
        - Other users: No access
        
        **Request Body Fields:**
        - **School Fields**: `name`, `school_type`, `academic_year`, `logo`, `primary_color`, `secondary_color`, `contact_email`, `contact_phone`, `website`, `address`, `city`, `state`, `country`, `postal_code`, `is_active`, `is_verified`
        - **Configuration Fields**: `academic_year_start`, `academic_year_end`, `current_semester`, `enable_sms_notifications`, `enable_email_notifications`, `enable_push_notifications`, `currency`, `payment_reminder_days`, `max_file_size_mb`, `allowed_file_types`
        """,
        request=SchoolUpdateSerializer,
        examples=[
            OpenApiExample(
                'Update school - Complete',
                summary='Update school with all fields',
                description='Update school details including configuration',
                value={
                    "name": "École Primaire de Niamey - Updated",
                    "school_type": "both",
                    "academic_year": "2024-2025",
                    "logo": "https://firebase-storage.com/schools/logos/new-logo.png",
                    "primary_color": "#FF5722",
                    "secondary_color": "#607D8B",
                    "contact_email": "new-contact@ecole-niamey.ne",
                    "contact_phone": "+22798765432",
                    "website": "https://new-ecole-niamey.ne",
                    "address": "Nouveau Quartier, Niamey",
                    "city": "Niamey",
                    "state": "Niamey",
                    "country": "Niger",
                    "postal_code": "10001",
                    "is_active": True,
                    "is_verified": True,
                    "configuration": {
                        "academic_year_start": "2024-09-01",
                        "academic_year_end": "2025-06-30",
                        "current_semester": "first",
                        "enable_sms_notifications": False,
                        "enable_email_notifications": True,
                        "enable_push_notifications": True,
                        "currency": "USD",
                        "payment_reminder_days": 14,
                        "max_file_size_mb": 20,
                        "allowed_file_types": [".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png", ".gif"]
                    }
                }
            ),
            OpenApiExample(
                'Update school - School only',
                summary='Update school without configuration',
                description='Update only school fields, configuration remains unchanged',
                value={
                    "name": "École Internationale de Niamey",
                    "school_type": "both",
                    "academic_year": "2024-2025",
                    "logo": "https://firebase-storage.com/schools/logos/international-logo.png",
                    "primary_color": "#4CAF50",
                    "secondary_color": "#2196F3",
                    "contact_email": "info@ecole-internationale.ne",
                    "contact_phone": "+22712345678",
                    "website": "https://www.ecole-internationale.ne",
                    "address": "Avenue de la République, Niamey",
                    "city": "Niamey",
                    "state": "Niamey",
                    "country": "Niger",
                    "postal_code": "10000",
                    "is_active": True,
                    "is_verified": True
                }
            )
        ]
    ),
    partial_update=extend_schema(
        summary="Partially Update School",
        description="""
        Partially update school information.
        
        **Permissions:**
        - Super admins: Can update any school
        - School staff: Can only update their own school
        - Other users: No access
        
        **Request Body Fields (All Optional):**
        - **School Fields**: `name`, `school_type`, `academic_year`, `logo`, `primary_color`, `secondary_color`, `contact_email`, `contact_phone`, `website`, `address`, `city`, `state`, `country`, `postal_code`, `is_active`, `is_verified`
        - **Configuration Fields**: `academic_year_start`, `academic_year_end`, `current_semester`, `enable_sms_notifications`, `enable_email_notifications`, `enable_push_notifications`, `currency`, `payment_reminder_days`, `max_file_size_mb`, `allowed_file_types`
        """,
        request=SchoolUpdateSerializer,
        examples=[
            OpenApiExample(
                'Update branding only',
                summary='Update school branding',
                description='Update only school branding elements (name, logo, colors)',
                value={
                    "name": "École Primaire de Niamey - New Name",
                    "logo": "https://firebase-storage.com/schools/logos/brand-new-logo.png",
                    "primary_color": "#4CAF50",
                    "secondary_color": "#2196F3"
                }
            ),
            OpenApiExample(
                'Update contact info only',
                summary='Update contact information',
                description='Update only contact details',
                value={
                    "contact_email": "info@ecole-niamey.ne",
                    "contact_phone": "+22712345678",
                    "website": "https://www.ecole-niamey.ne",
                    "address": "Avenue de la République, Niamey",
                    "city": "Niamey",
                    "state": "Niamey",
                    "postal_code": "10000"
                }
            ),
            OpenApiExample(
                'Update status only',
                summary='Update school status',
                description='Update only school status fields',
                value={
                    "is_active": True,
                    "is_verified": True
                }
            ),
            OpenApiExample(
                'Update configuration only',
                summary='Update configuration settings',
                description='Update only configuration fields',
                value={
                    "configuration": {
                        "enable_sms_notifications": False,
                        "currency": "EUR",
                        "max_file_size_mb": 15,
                        "payment_reminder_days": 10
                    }
                }
            ),
            OpenApiExample(
                'Update mixed fields',
                summary='Update school and configuration',
                description='Update both school and configuration fields',
                value={
                    "name": "École Moderne de Niamey",
                    "primary_color": "#FF9800",
                    "contact_email": "modern@ecole-niamey.ne",
                    "configuration": {
                        "current_semester": "second",
                        "enable_email_notifications": True,
                        "currency": "NGN"
                    }
                }
            )
        ]
    ),
    destroy=extend_schema(
        summary="Delete School",
        description="""
        Delete a school permanently.
        
        **Permissions:**
        - Only super admins can delete schools
        
        **Warning:** This action cannot be undone!
        """
    )
)
class SchoolViewSet(viewsets.ModelViewSet):
    """
    ViewSet for school management with comprehensive permission system.
    
    **Permission Matrix:**
    - **Super Admins**: Full access to all schools (create, read, update, delete)
    - **School Staff**: Can only view and update their own school
    - **Other Users**: No access to school management
    
    **Features:**
    - Multi-tenant architecture with school isolation
    - Comprehensive filtering and search
    - School configuration management
    - Statistics and analytics
    - Automatic slug generation
    - Default configuration creation
    """
    queryset = School.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school_type', 'city', 'state', 'is_active', 'is_verified']
    search_fields = ['name', 'contact_email', 'address']
    ordering_fields = ['name', 'created_at', 'student_count']
    ordering = ['name']
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        
        # Super admins can see all schools
        if user.is_superuser:
            return School.objects.all()
        # School staff can only see their own school
        elif user.user_type == 'school_staff' and user.school:
            return School.objects.filter(id=user.school.id)
        # All other users cannot see any schools
        else:
            return School.objects.none()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return SchoolListSerializer
        elif self.action == 'create':
            return SchoolCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SchoolUpdateSerializer
        else:
            return SchoolDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'destroy']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def check_permissions(self, request):
        """Check permissions before processing the request"""
        super().check_permissions(request)
        
        # For create action, check if user is superuser
        if self.action == 'create':
            if not request.user.is_superuser:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Only super admins can create schools.")
    
    def check_object_permissions(self, request, obj):
        """Check object-level permissions"""
        super().check_object_permissions(request, obj)
        
        user = request.user
        
        # For read operations (list, retrieve), allow broader access
        if self.action in ['list', 'retrieve', 'statistics']:
            # Super admins can access all schools
            if user.is_superuser:
                return
            
            # School staff can view their own school
            if user.user_type == 'school_staff' and user.school and obj.id == user.school.id:
                return
            
            # For other users, deny access
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to access this school.")
        
        # For write operations (create, update, partial_update, destroy, activate, deactivate, configuration)
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'activate', 'deactivate', 'configuration']:
            # Super admins can manage all schools
            if user.is_superuser:
                return
            
            # School staff can only manage their own school
            if user.user_type == 'school_staff' and user.school and obj.id == user.school.id:
                return
            
            # All other users are denied
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only super admins and school staff of this school can perform this action.")
        
        # For any other actions, deny by default
        else:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to perform this action.")
    
    def perform_create(self, serializer):
        """Create school with default configuration"""
        school = serializer.save()
        
        # Create default configuration if not provided
        if not hasattr(school, 'configuration'):
            SchoolConfiguration.objects.create(school=school)
    
    @extend_schema(
        summary="Get School Statistics",
        description="""
        Retrieve comprehensive statistics for a specific school.
        
        **Statistics Include:**
        - Total student count
        - Class level distribution
        - Gender distribution
        - Recent enrollments (last 30 days)
        - Payment statistics (total, paid, overdue)
        
        **Permissions:**
        - Super admins: Can view statistics for any school
        - School staff: Can only view statistics for their own school
        - Other users: No access
        """,
        examples=[
            OpenApiExample(
                'School statistics',
                summary='Get school statistics',
                description='Retrieve comprehensive school analytics',
                value={
                    "total_students": 150,
                    "class_distribution": [
                        {"class_level": "Grade 1", "count": 25},
                        {"class_level": "Grade 2", "count": 30},
                        {"class_level": "Grade 3", "count": 28},
                        {"class_level": "Grade 4", "count": 32},
                        {"class_level": "Grade 5", "count": 35}
                    ],
                    "gender_distribution": [
                        {"gender": "M", "count": 78},
                        {"gender": "F", "count": 72}
                    ],
                    "recent_enrollments": 12,
                    "payment_statistics": {
                        "total_payments": 450,
                        "paid_payments": 380,
                        "overdue_payments": 70
                    }
                }
            )
        ]
    )
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get school statistics"""
        school = self.get_object()
        
        # Get student statistics
        students = school.students.filter(is_active=True)
        total_students = students.count()
        
        # Get class level distribution
        class_distribution = students.values('class_level').annotate(
            count=Count('id')
        ).order_by('class_level')
        
        # Get gender distribution
        gender_distribution = students.values('gender').annotate(
            count=Count('id')
        )
        
        # Get recent enrollments
        recent_enrollments = students.filter(
            enrollment_date__gte=timezone.now().date() - timezone.timedelta(days=30)
        ).count()
        
        # Get payment statistics
        payment_stats = school.students.aggregate(
            total_payments=Count('payment_records'),
            paid_payments=Count('payment_records', filter=Q(payment_records__status='paid')),
            overdue_payments=Count('payment_records', filter=Q(payment_records__status='overdue'))
        )
        
        return Response({
            'total_students': total_students,
            'class_distribution': class_distribution,
            'gender_distribution': gender_distribution,
            'recent_enrollments': recent_enrollments,
            'payment_statistics': payment_stats
        })
    
    @extend_schema(
        summary="Manage School Configuration",
        description="""
        Get, update, or partially update school configuration settings.
        
        **GET Response Includes:**
        - **Complete School Information**: All school details (name, branding, contact, location, status)
        - **School Statistics**: Student count, staff count
        - **Configuration Settings**: Academic, notification, payment, and file upload settings
        - **Timestamps**: School and configuration creation/update times
        
        **Configuration Settings:**
        - **Academic Settings**: Academic year dates, current semester
        - **Notification Settings**: SMS, email, and push notification toggles
        - **Payment Settings**: Currency, payment reminder days
        - **File Upload Settings**: Max file size, allowed file types
        
        **Permissions:**
        - Super admins: Can manage configuration for any school
        - School staff: Can only manage configuration for their own school
        - Other users: No access
        
        **Methods:**
        - `GET`: Retrieve complete school information with configuration
        - `PUT`: Update entire configuration (full replacement)
        - `PATCH`: Partially update configuration
        
        **Request Body Fields (for PUT/PATCH):**
        - **Academic Settings**: `academic_year_start`, `academic_year_end`, `current_semester`
        - **Notification Settings**: `enable_sms_notifications`, `enable_email_notifications`, `enable_push_notifications`
        - **Payment Settings**: `currency`, `payment_reminder_days`
        - **File Upload Settings**: `max_file_size_mb`, `allowed_file_types`
        """,
        request=SchoolConfigurationSerializer,
        examples=[
            OpenApiExample(
                'Get configuration with school details',
                summary='Get school configuration and details',
                description='Retrieve complete school information including configuration settings',
                value={
                    # School basic information
                    "school_id": "123e4567-e89b-12d3-a456-426614174000",
                    "school_name": "École Primaire de Niamey",
                    "school_slug": "ecole-primaire-niamey",
                    "school_type": "primary",
                    "academic_year": "2024-2025",
                    
                    # School branding
                    "logo": "https://firebase-storage.com/schools/logos/logo.png",
                    "primary_color": "#1976D2",
                    "secondary_color": "#424242",
                    
                    # School contact information
                    "contact_email": "contact@ecole-niamey.ne",
                    "contact_phone": "+22712345678",
                    "website": "https://ecole-niamey.ne",
                    
                    # School location
                    "address": "Quartier Plateau, Niamey",
                    "city": "Niamey",
                    "state": "Niamey",
                    "country": "Niger",
                    "postal_code": "10000",
                    
                    # School status
                    "is_active": True,
                    "is_verified": True,
                    
                    # School statistics
                    "student_count": 150,
                    "staff_count": 12,
                    
                    # Timestamps
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-09-04T14:20:00Z",
                    "config_created_at": "2024-01-15T10:30:00Z",
                    "config_updated_at": "2024-09-04T14:20:00Z",
                    
                    # Configuration settings
                    "academic_year_start": "2024-09-01",
                    "academic_year_end": "2025-06-30",
                    "current_semester": "first",
                    "enable_sms_notifications": True,
                    "enable_email_notifications": True,
                    "enable_push_notifications": True,
                    "currency": "NGN",
                    "payment_reminder_days": 7,
                    "max_file_size_mb": 10,
                    "allowed_file_types": [".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"]
                }
            ),
            OpenApiExample(
                'Update configuration - PUT (Full)',
                summary='Update entire configuration',
                description='Update all configuration settings (full replacement)',
                value={
                    "academic_year_start": "2024-09-01",
                    "academic_year_end": "2025-06-30",
                    "current_semester": "second",
                    "enable_sms_notifications": False,
                    "enable_email_notifications": True,
                    "enable_push_notifications": True,
                    "currency": "USD",
                    "payment_reminder_days": 14,
                    "max_file_size_mb": 20,
                    "allowed_file_types": [".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png", ".gif", ".txt"]
                }
            ),
            OpenApiExample(
                'Update configuration - PATCH (Partial)',
                summary='Partially update configuration',
                description='Update only specific configuration fields',
                value={
                    "enable_sms_notifications": False,
                    "currency": "EUR",
                    "max_file_size_mb": 15
                }
            ),
            OpenApiExample(
                'Update academic settings only',
                summary='Update academic year settings',
                description='Update only academic year and semester settings',
                value={
                    "academic_year_start": "2024-08-15",
                    "academic_year_end": "2025-07-15",
                    "current_semester": "first"
                }
            ),
            OpenApiExample(
                'Update notification settings only',
                summary='Update notification preferences',
                description='Update only notification settings',
                value={
                    "enable_sms_notifications": True,
                    "enable_email_notifications": False,
                    "enable_push_notifications": True
                }
            ),
            OpenApiExample(
                'Update payment settings only',
                summary='Update payment configuration',
                description='Update only payment-related settings',
                value={
                    "currency": "NGN",
                    "payment_reminder_days": 7
                }
            ),
            OpenApiExample(
                'Update file upload settings only',
                summary='Update file upload configuration',
                description='Update only file upload settings',
                value={
                    "max_file_size_mb": 25,
                    "allowed_file_types": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mp3"]
                }
            )
        ]
    )
    @action(detail=True, methods=['get', 'put', 'patch'])
    def configuration(self, request, pk=None):
        """Manage school configuration"""
        school = self.get_object()
        
        # Ensure school has a configuration object
        if not hasattr(school, 'configuration') or school.configuration is None:
            # Create default configuration if it doesn't exist
            from datetime import date
            current_year = date.today().year
            SchoolConfiguration.objects.create(
                school=school,
                academic_year_start=date(current_year, 9, 1),  # September 1st
                academic_year_end=date(current_year + 1, 6, 30),  # June 30th next year
                current_semester='first'
            )
            school.refresh_from_db()  # Refresh to get the new configuration
        
        if request.method == 'GET':
            serializer = SchoolConfigurationDetailSerializer(school.configuration)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            serializer = SchoolConfigurationSerializer(
                school.configuration,
                data=request.data,
                partial=request.method == 'PATCH'
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Activate School",
        description="""
        Activate a school to make it available for use.
        
        **Permissions:**
        - Super admins: Can activate any school
        - School staff: Can only activate their own school
        - Other users: No access
        
        **Note:** This action sets `is_active=True` for the school.
        """,
        examples=[
            OpenApiExample(
                'Activate school',
                summary='Activate school',
                description='Activate a school',
                value={
                    "message": "School activated successfully"
                }
            )
        ]
    )
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a school"""
        school = self.get_object()
        school.is_active = True
        school.save()
        return Response({'message': 'School activated successfully'})
    
    @extend_schema(
        summary="Deactivate School",
        description="""
        Deactivate a school to make it unavailable for use.
        
        **Permissions:**
        - Super admins: Can deactivate any school
        - School staff: Can only deactivate their own school
        - Other users: No access
        
        **Note:** This action sets `is_active=False` for the school.
        """,
        examples=[
            OpenApiExample(
                'Deactivate school',
                summary='Deactivate school',
                description='Deactivate a school',
                value={
                    "message": "School deactivated successfully"
                }
            )
        ]
    )
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a school"""
        school = self.get_object()
        school.is_active = False
        school.save()
        return Response({'message': 'School deactivated successfully'})
