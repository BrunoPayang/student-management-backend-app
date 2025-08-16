# Phase 4: Core API Endpoints (Week 2 - Days 1-3)

## Overview
Implement comprehensive REST API endpoints for school management, student operations, and parent access with proper authentication, permissions, and data filtering.

## Task 4.1: School Management APIs

### Step 1: Create School Serializers
**apps/schools/serializers.py**
```python
from rest_framework import serializers
from .models import School, SchoolConfiguration


class SchoolConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for school configuration settings"""
    
    class Meta:
        model = SchoolConfiguration
        fields = [
            'academic_year_start', 'academic_year_end', 'current_semester',
            'enable_sms_notifications', 'enable_email_notifications', 
            'enable_push_notifications', 'currency', 'payment_reminder_days',
            'max_file_size_mb', 'allowed_file_types'
        ]


class SchoolListSerializer(serializers.ModelSerializer):
    """Serializer for school list view (limited fields)"""
    student_count = serializers.SerializerMethodField()
    staff_count = serializers.SerializerMethodField()
    
    class Meta:
        model = School
        fields = [
            'id', 'name', 'slug', 'school_type', 'city', 'state',
            'is_active', 'is_verified', 'student_count', 'staff_count'
        ]
    
    def get_student_count(self, obj):
        return obj.get_student_count()
    
    def get_staff_count(self, obj):
        return obj.get_staff_count()


class SchoolDetailSerializer(serializers.ModelSerializer):
    """Serializer for school detail view (all fields)"""
    configuration = SchoolConfigurationSerializer(read_only=True)
    student_count = serializers.SerializerMethodField()
    staff_count = serializers.SerializerMethodField()
    
    class Meta:
        model = School
        fields = [
            'id', 'name', 'slug', 'school_type', 'academic_year',
            'logo', 'primary_color', 'secondary_color',
            'contact_email', 'contact_phone', 'website',
            'address', 'city', 'state', 'country', 'postal_code',
            'is_active', 'is_verified', 'configuration',
            'student_count', 'staff_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_student_count(self, obj):
        return obj.get_student_count()
    
    def get_staff_count(self, obj):
        return obj.get_staff_count()
    
    def validate_slug(self, value):
        """Ensure slug is unique"""
        if School.objects.filter(slug=value).exists():
            raise serializers.ValidationError("A school with this slug already exists.")
        return value


class SchoolCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new schools"""
    configuration = SchoolConfigurationSerializer(required=False)
    
    class Meta:
        model = School
        fields = [
            'name', 'school_type', 'academic_year',
            'logo', 'primary_color', 'secondary_color',
            'contact_email', 'contact_phone', 'website',
            'address', 'city', 'state', 'country', 'postal_code',
            'configuration'
        ]
    
    def create(self, validated_data):
        """Create school and configuration"""
        configuration_data = validated_data.pop('configuration', None)
        school = School.objects.create(**validated_data)
        
        if configuration_data:
            SchoolConfiguration.objects.create(school=school, **configuration_data)
        else:
            # Create default configuration
            SchoolConfiguration.objects.create(school=school)
        
        return school


class SchoolUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating schools"""
    configuration = SchoolConfigurationSerializer(required=False)
    
    class Meta:
        model = School
        fields = [
            'name', 'school_type', 'academic_year',
            'logo', 'primary_color', 'secondary_color',
            'contact_email', 'contact_phone', 'website',
            'address', 'city', 'state', 'country', 'postal_code',
            'is_active', 'is_verified', 'configuration'
        ]
    
    def update(self, instance, validated_data):
        """Update school and configuration"""
        configuration_data = validated_data.pop('configuration', None)
        
        # Update school
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update configuration if provided
        if configuration_data and hasattr(instance, 'configuration'):
            config = instance.configuration
            for attr, value in configuration_data.items():
                setattr(config, attr, value)
            config.save()
        
        return instance
```

### Step 2: Create School Views
**apps/schools/views.py**
```python
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone

from .models import School, SchoolConfiguration
from .serializers import (
    SchoolListSerializer, SchoolDetailSerializer,
    SchoolCreateSerializer, SchoolUpdateSerializer,
    SchoolConfigurationSerializer
)
from apps.authentication.permissions import IsSystemAdmin, IsSchoolStaff
from apps.common.pagination import StandardResultsSetPagination


class SchoolViewSet(viewsets.ModelViewSet):
    """
    ViewSet for school management
    System admins can manage all schools
    School staff can view their own school
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
        
        if user.is_system_admin():
            return School.objects.all()
        elif user.is_school_staff():
            return School.objects.filter(id=user.school.id)
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
            permission_classes = [IsAuthenticated, IsSystemAdmin]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsSystemAdmin | IsSchoolStaff]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Create school with default configuration"""
        school = serializer.save()
        
        # Create default configuration if not provided
        if not hasattr(school, 'configuration'):
            SchoolConfiguration.objects.create(school=school)
    
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
    
    @action(detail=True, methods=['get', 'put', 'patch'])
    def configuration(self, request, pk=None):
        """Manage school configuration"""
        school = self.get_object()
        
        if request.method == 'GET':
            serializer = SchoolConfigurationSerializer(school.configuration)
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
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a school"""
        school = self.get_object()
        school.is_active = True
        school.save()
        return Response({'message': 'School activated successfully'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a school"""
        school = self.get_object()
        school.is_active = False
        school.save()
        return Response({'message': 'School deactivated successfully'})
```

### Step 3: Create School URLs
**apps/schools/urls.py**
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SchoolViewSet

router = DefaultRouter()
router.register(r'schools', SchoolViewSet, basename='school')

urlpatterns = [
    path('api/', include(router.urls)),
]
```

## Task 4.2: Student Management APIs

### Step 1: Create Student Serializers
**apps/students/serializers.py**
```python
from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import Student, ParentStudent, Transcript, BehaviorReport, PaymentRecord


class StudentListSerializer(serializers.ModelSerializer):
    """Serializer for student list view"""
    school_name = serializers.CharField(source='school.name', read_only=True)
    primary_parent = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'last_name', 'student_id',
            'school', 'school_name', 'class_level', 'section',
            'gender', 'is_active', 'enrollment_date', 'primary_parent'
        ]
    
    def get_primary_parent(self, obj):
        primary_parent = obj.get_primary_parent()
        if primary_parent:
            return {
                'id': primary_parent.parent.id,
                'name': primary_parent.parent.full_name,
                'phone': primary_parent.parent.phone
            }
        return None


class StudentDetailSerializer(serializers.ModelSerializer):
    """Serializer for student detail view"""
    school_name = serializers.CharField(source='school.name', read_only=True)
    parents = serializers.SerializerMethodField()
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'last_name', 'middle_name', 'student_id',
            'school', 'school_name', 'class_level', 'section',
            'date_of_birth', 'age', 'gender', 'email', 'phone',
            'address', 'city', 'state', 'blood_group', 'emergency_contact',
            'medical_conditions', 'enrollment_date', 'graduation_date',
            'is_active', 'is_graduated', 'profile_picture', 'parents',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_parents(self, obj):
        parents = obj.parents.all()
        return [{
            'id': parent.parent.id,
            'name': parent.parent.full_name,
            'relationship': parent.relationship,
            'is_primary': parent.is_primary,
            'is_emergency_contact': parent.is_emergency_contact,
            'phone': parent.parent.phone,
            'email': parent.parent.email
        } for parent in parents]


class StudentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating students"""
    
    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'middle_name', 'student_id',
            'class_level', 'section', 'date_of_birth', 'gender',
            'email', 'phone', 'address', 'city', 'state',
            'blood_group', 'emergency_contact', 'medical_conditions',
            'profile_picture'
        ]
    
    def validate_student_id(self, value):
        """Ensure student ID is unique within school"""
        school = self.context['request'].user.school
        if Student.objects.filter(school=school, student_id=value).exists():
            raise serializers.ValidationError("A student with this ID already exists in this school.")
        return value
    
    def create(self, validated_data):
        """Create student with school context"""
        validated_data['school'] = self.context['request'].user.school
        return super().create(validated_data)


class StudentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating students"""
    
    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'middle_name', 'student_id',
            'class_level', 'section', 'date_of_birth', 'gender',
            'email', 'phone', 'address', 'city', 'state',
            'blood_group', 'emergency_contact', 'medical_conditions',
            'enrollment_date', 'graduation_date', 'is_active',
            'is_graduated', 'profile_picture'
        ]


class ParentStudentSerializer(serializers.ModelSerializer):
    """Serializer for parent-student relationships"""
    parent_name = serializers.CharField(source='parent.full_name', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = ParentStudent
        fields = [
            'id', 'parent', 'parent_name', 'student', 'student_name',
            'relationship', 'is_primary', 'is_emergency_contact',
            'receive_sms', 'receive_email', 'receive_push',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TranscriptSerializer(serializers.ModelSerializer):
    """Serializer for academic transcripts"""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    file_size_mb = serializers.ReadOnlyField()
    
    class Meta:
        model = Transcript
        fields = [
            'id', 'student', 'student_name', 'academic_year', 'semester',
            'file_url', 'file_name', 'file_size_mb', 'gpa', 'total_credits',
            'rank_in_class', 'class_size', 'uploaded_by', 'uploaded_by_name',
            'is_public', 'created_at'
        ]
        read_only_fields = ['id', 'file_size_mb', 'created_at']


class BehaviorReportSerializer(serializers.ModelSerializer):
    """Serializer for behavior reports"""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    reported_by_name = serializers.CharField(source='reported_by.full_name', read_only=True)
    
    class Meta:
        model = BehaviorReport
        fields = [
            'id', 'student', 'student_name', 'report_type', 'title',
            'description', 'location', 'incident_date', 'incident_time',
            'severity_level', 'actions_taken', 'follow_up_required',
            'follow_up_date', 'reported_by', 'reported_by_name',
            'notify_parents', 'is_public', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PaymentRecordSerializer(serializers.ModelSerializer):
    """Serializer for payment records"""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    days_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = PaymentRecord
        fields = [
            'id', 'student', 'student_name', 'amount', 'currency',
            'payment_type', 'status', 'due_date', 'paid_date',
            'payment_method', 'reference_number', 'receipt_url',
            'notes', 'created_by', 'created_by_name', 'days_overdue',
            'created_at'
        ]
        read_only_fields = ['id', 'days_overdue', 'created_at']
```

### Step 2: Create Student Views
**apps/students/views.py**
```python
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import date

from .models import Student, ParentStudent, Transcript, BehaviorReport, PaymentRecord
from .serializers import (
    StudentListSerializer, StudentDetailSerializer,
    StudentCreateSerializer, StudentUpdateSerializer,
    ParentStudentSerializer, TranscriptSerializer,
    BehaviorReportSerializer, PaymentRecordSerializer
)
from apps.authentication.permissions import IsSchoolStaff, IsParent
from apps.common.pagination import StandardResultsSetPagination


class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for student management
    School staff can manage students in their school
    Parents can view their children
    """
    queryset = Student.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['class_level', 'section', 'gender', 'is_active', 'is_graduated']
    search_fields = ['first_name', 'last_name', 'student_id', 'email']
    ordering_fields = ['first_name', 'last_name', 'enrollment_date', 'date_of_birth']
    ordering = ['last_name', 'first_name']
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        
        if user.is_school_staff():
            return Student.objects.filter(school=user.school)
        elif user.is_parent():
            return Student.objects.filter(parents__parent=user)
        else:
            return Student.objects.none()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return StudentListSerializer
        elif self.action == 'create':
            return StudentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return StudentUpdateSerializer
        else:
            return StudentDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsSchoolStaff]
        else:
            permission_classes = [IsAuthenticated, IsSchoolStaff | IsParent]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Create student with school context"""
        serializer.save(school=self.request.user.school)
    
    @action(detail=True, methods=['get'])
    def academic_records(self, request, pk=None):
        """Get student's academic records"""
        student = self.get_object()
        transcripts = student.transcripts.filter(is_public=True)
        serializer = TranscriptSerializer(transcripts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def behavior_reports(self, request, pk=None):
        """Get student's behavior reports"""
        student = self.get_object()
        reports = student.behavior_reports.filter(is_public=True)
        serializer = BehaviorReportSerializer(reports, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payment_records(self, request, pk=None):
        """Get student's payment records"""
        student = self.get_object()
        payments = student.payment_records.all()
        serializer = PaymentRecordSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get student statistics"""
        student = self.get_object()
        
        # Academic statistics
        transcripts = student.transcripts.all()
        total_transcripts = transcripts.count()
        average_gpa = transcripts.aggregate(avg_gpa=Avg('gpa'))['avg_gpa']
        
        # Behavior statistics
        behavior_reports = student.behavior_reports.all()
        positive_reports = behavior_reports.filter(report_type='positive').count()
        negative_reports = behavior_reports.filter(report_type='negative').count()
        
        # Payment statistics
        payments = student.payment_records.all()
        total_payments = payments.count()
        paid_payments = payments.filter(status='paid').count()
        overdue_payments = payments.filter(status='overdue').count()
        total_amount = payments.aggregate(total=Sum('amount'))['total'] or 0
        
        return Response({
            'academic': {
                'total_transcripts': total_transcripts,
                'average_gpa': average_gpa
            },
            'behavior': {
                'positive_reports': positive_reports,
                'negative_reports': negative_reports,
                'total_reports': behavior_reports.count()
            },
            'payments': {
                'total_payments': total_payments,
                'paid_payments': paid_payments,
                'overdue_payments': overdue_payments,
                'total_amount': total_amount
            }
        })


class ParentStudentViewSet(viewsets.ModelViewSet):
    """ViewSet for parent-student relationships"""
    queryset = ParentStudent.objects.all()
    serializer_class = ParentStudentSerializer
    permission_classes = [IsAuthenticated, IsSchoolStaff]
    
    def get_queryset(self):
        """Filter by school"""
        return ParentStudent.objects.filter(student__school=self.request.user.school)
    
    def perform_create(self, serializer):
        """Create relationship with validation"""
        # Ensure only one primary contact per student
        if serializer.validated_data.get('is_primary'):
            ParentStudent.objects.filter(
                student=serializer.validated_data['student'],
                is_primary=True
            ).update(is_primary=False)
        
        serializer.save()


class TranscriptViewSet(viewsets.ModelViewSet):
    """ViewSet for academic transcripts"""
    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer
    permission_classes = [IsAuthenticated, IsSchoolStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['academic_year', 'semester', 'is_public']
    search_fields = ['student__first_name', 'student__last_name', 'student__student_id']
    
    def get_queryset(self):
        """Filter by school"""
        return Transcript.objects.filter(student__school=self.request.user.school)
    
    def perform_create(self, serializer):
        """Create transcript with uploader info"""
        serializer.save(uploaded_by=self.request.user)


class BehaviorReportViewSet(viewsets.ModelViewSet):
    """ViewSet for behavior reports"""
    queryset = BehaviorReport.objects.all()
    serializer_class = BehaviorReportSerializer
    permission_classes = [IsAuthenticated, IsSchoolStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['report_type', 'severity_level', 'notify_parents', 'is_public']
    search_fields = ['student__first_name', 'student__last_name', 'title', 'description']
    
    def get_queryset(self):
        """Filter by school"""
        return BehaviorReport.objects.filter(student__school=self.request.user.school)
    
    def perform_create(self, serializer):
        """Create report with reporter info"""
        report = serializer.save(reported_by=self.request.user)
        
        # Send notification to parents if enabled
        if report.notify_parents:
            self.send_parent_notification(report)
    
    def send_parent_notification(self, report):
        """Send notification to student's parents"""
        # This will be implemented in Phase 6 with Firebase
        pass


class PaymentRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for payment records"""
    queryset = PaymentRecord.objects.all()
    serializer_class = PaymentRecordSerializer
    permission_classes = [IsAuthenticated, IsSchoolStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['payment_type', 'status', 'currency']
    search_fields = ['student__first_name', 'student__last_name', 'reference_number']
    
    def get_queryset(self):
        """Filter by school"""
        return PaymentRecord.objects.filter(student__school=self.request.user.school)
    
    def perform_create(self, serializer):
        """Create payment record with creator info"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def overdue_payments(self, request):
        """Get all overdue payments"""
        overdue_payments = self.get_queryset().filter(
            status='pending',
            due_date__lt=date.today()
        )
        serializer = self.get_serializer(overdue_payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def payment_summary(self, request):
        """Get payment summary statistics"""
        payments = self.get_queryset()
        
        summary = {
            'total_payments': payments.count(),
            'total_amount': payments.aggregate(total=Sum('amount'))['total'] or 0,
            'paid_amount': payments.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0,
            'pending_amount': payments.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0,
            'overdue_amount': payments.filter(status='overdue').aggregate(total=Sum('amount'))['total'] or 0,
            'payment_types': payments.values('payment_type').annotate(
                count=Count('id'),
                total_amount=Sum('amount')
            )
        }
        
        return Response(summary)
```

### Step 3: Create Student URLs
**apps/students/urls.py**
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet, ParentStudentViewSet,
    TranscriptViewSet, BehaviorReportViewSet, PaymentRecordViewSet
)

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'parent-students', ParentStudentViewSet, basename='parent-student')
router.register(r'transcripts', TranscriptViewSet, basename='transcript')
router.register(r'behavior-reports', BehaviorReportViewSet, basename='behavior-report')
router.register(r'payment-records', PaymentRecordViewSet, basename='payment-record')

urlpatterns = [
    path('api/', include(router.urls)),
]
```

## Task 4.3: Parent/Guardian APIs

### Step 1: Create Parent Views
**apps/parents/views.py**
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from apps.students.models import Student, Transcript, BehaviorReport, PaymentRecord
from apps.students.serializers import (
    StudentDetailSerializer, TranscriptSerializer,
    BehaviorReportSerializer, PaymentRecordSerializer
)
from apps.authentication.permissions import IsParent
from apps.common.pagination import StandardResultsSetPagination


class ParentDashboardViewSet(viewsets.ViewSet):
    """
    ViewSet for parent dashboard functionality
    Parents can view their children's information
    """
    permission_classes = [IsAuthenticated, IsParent]
    pagination_class = StandardResultsSetPagination
    
    @action(detail=False, methods=['get'])
    def my_children(self, request):
        """Get all children of the parent"""
        children = Student.objects.filter(parents__parent=request.user)
        serializer = StudentDetailSerializer(children, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def child_details(self, request, pk=None):
        """Get detailed information about a specific child"""
        try:
            child = Student.objects.get(
                id=pk,
                parents__parent=request.user
            )
            serializer = StudentDetailSerializer(child)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def child_transcripts(self, request, pk=None):
        """Get child's academic transcripts"""
        try:
            child = Student.objects.get(
                id=pk,
                parents__parent=request.user
            )
            transcripts = child.transcripts.filter(is_public=True)
            serializer = TranscriptSerializer(transcripts, many=True)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def child_behavior(self, request, pk=None):
        """Get child's behavior reports"""
        try:
            child = Student.objects.get(
                id=pk,
                parents__parent=request.user
            )
            reports = child.behavior_reports.filter(is_public=True)
            serializer = BehaviorReportSerializer(reports, many=True)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def child_payments(self, request, pk=None):
        """Get child's payment records"""
        try:
            child = Student.objects.get(
                id=pk,
                parents__parent=request.user
            )
            payments = child.payment_records.all()
            serializer = PaymentRecordSerializer(payments, many=True)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def child_statistics(self, request, pk=None):
        """Get child's statistics"""
        try:
            child = Student.objects.get(
                id=pk,
                parents__parent=request.user
            )
            
            # Academic statistics
            transcripts = child.transcripts.filter(is_public=True)
            total_transcripts = transcripts.count()
            average_gpa = transcripts.aggregate(avg_gpa=Avg('gpa'))['avg_gpa']
            
            # Behavior statistics
            behavior_reports = child.behavior_reports.filter(is_public=True)
            positive_reports = behavior_reports.filter(report_type='positive').count()
            negative_reports = behavior_reports.filter(report_type='negative').count()
            
            # Payment statistics
            payments = child.payment_records.all()
            total_payments = payments.count()
            paid_payments = payments.filter(status='paid').count()
            overdue_payments = payments.filter(status='overdue').count()
            total_amount = payments.aggregate(total=Sum('amount'))['total'] or 0
            
            return Response({
                'academic': {
                    'total_transcripts': total_transcripts,
                    'average_gpa': average_gpa
                },
                'behavior': {
                    'positive_reports': positive_reports,
                    'negative_reports': negative_reports,
                    'total_reports': behavior_reports.count()
                },
                'payments': {
                    'total_payments': total_payments,
                    'paid_payments': paid_payments,
                    'overdue_payments': overdue_payments,
                    'total_amount': total_amount
                }
            })
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def notifications(self, request):
        """Get parent's notifications"""
        # This will be implemented in Phase 6
        return Response({'message': 'Notifications endpoint - to be implemented'})
    
    @action(detail=False, methods=['put'])
    def notification_preferences(self, request):
        """Update notification preferences"""
        user = request.user
        
        # Update notification preferences
        if 'receive_sms' in request.data:
            user.receive_sms = request.data['receive_sms']
        if 'receive_email' in request.data:
            user.receive_email = request.data['receive_email']
        if 'receive_push' in request.data:
            user.receive_push = request.data['receive_push']
        
        user.save()
        
        return Response({
            'message': 'Notification preferences updated successfully',
            'preferences': {
                'receive_sms': user.receive_sms,
                'receive_email': user.receive_email,
                'receive_push': user.receive_push
            }
        })
```

### Step 2: Create Parent URLs
**apps/parents/urls.py**
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParentDashboardViewSet

router = DefaultRouter()
router.register(r'parent-dashboard', ParentDashboardViewSet, basename='parent-dashboard')

urlpatterns = [
    path('api/', include(router.urls)),
]
```

## Task 4.4: Update Main URLs

### Step 1: Update Project URLs
**schoolconnect/urls.py**
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.schools.urls')),
    path('', include('apps.students.urls')),
    path('', include('apps.parents.urls')),
    path('', include('apps.authentication.urls')),
    path('', include('apps.files.urls')),
    path('', include('apps.notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Validation Checklist

### School Management APIs
- [ ] School list endpoint with proper filtering and pagination
- [ ] School detail endpoint with full information
- [ ] School creation endpoint with validation
- [ ] School update endpoint with proper permissions
- [ ] School statistics endpoint
- [ ] School configuration management
- [ ] School activation/deactivation endpoints
- [ ] Proper permission checks for all endpoints

### Student Management APIs
- [ ] Student list endpoint with school filtering
- [ ] Student detail endpoint with full information
- [ ] Student creation endpoint with validation
- [ ] Student update endpoint with proper permissions
- [ ] Student academic records endpoint
- [ ] Student behavior reports endpoint
- [ ] Student payment records endpoint
- [ ] Student statistics endpoint
- [ ] Parent-student relationship management
- [ ] Transcript management endpoints
- [ ] Behavior report management endpoints
- [ ] Payment record management endpoints

### Parent APIs
- [ ] Parent dashboard with children list
- [ ] Child detail access with proper permissions
- [ ] Child academic records access
- [ ] Child behavior reports access
- [ ] Child payment records access
- [ ] Child statistics endpoint
- [ ] Notification preferences management
- [ ] Proper data isolation between parents

### API Features
- [ ] Proper authentication on all endpoints
- [ ] Role-based access control implemented
- [ ] Data filtering by school (multi-tenancy)
- [ ] Search functionality on relevant endpoints
- [ ] Pagination on list endpoints
- [ ] Proper error handling and validation
- [ ] Serializer validation for all data
- [ ] API documentation with browsable interface

### Performance & Security
- [ ] Database queries optimized with select_related/prefetch_related
- [ ] Proper indexing for frequently queried fields
- [ ] Rate limiting implemented (to be added in Phase 8)
- [ ] Input validation and sanitization
- [ ] SQL injection prevention
- [ ] XSS protection through proper serialization

## Next Steps
After completing Phase 4, proceed to Phase 5: Firebase Integration to implement file storage and push notifications functionality. 