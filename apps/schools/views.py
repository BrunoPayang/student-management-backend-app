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
        
        if user.is_superuser or user.user_type == 'admin':
            return School.objects.all()
        elif user.user_type == 'school_staff' and user.school:
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
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated]
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
