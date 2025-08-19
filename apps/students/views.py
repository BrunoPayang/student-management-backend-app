from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import date

from .models import Student, ParentStudent, Transcript, BehaviorReport, PaymentRecord
from .serializers import (
    StudentListSerializer, StudentDetailSerializer,
    StudentCreateSerializer, StudentUpdateSerializer,
    ParentStudentSerializer, TranscriptSerializer,
    BehaviorReportSerializer, PaymentRecordSerializer
)
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
        
        if user.user_type == 'admin':
            # System Admin can see all students
            return Student.objects.all()
        elif user.user_type == 'school_staff' and user.school:
            # School Staff can only see students from their school
            return Student.objects.filter(school=user.school)
        elif user.user_type == 'parent':
            # Parents can only see their own children
            return Student.objects.filter(parents__parent=user)
        else:
            # For other cases, return empty queryset
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
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Create student with school context"""
        # Use school from request data if provided, otherwise use user's school
        school = serializer.validated_data.get('school')
        if not school and hasattr(self.request.user, 'school') and self.request.user.school:
            school = self.request.user.school
            serializer.save(school=school)
        else:
            serializer.save()
    
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
    permission_classes = [IsAuthenticated]
    
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
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]
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
