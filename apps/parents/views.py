from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count, Avg

from apps.students.models import Student, Transcript, BehaviorReport, PaymentRecord
from apps.students.serializers import (
    StudentDetailSerializer, TranscriptSerializer,
    BehaviorReportSerializer, PaymentRecordSerializer
)
from apps.common.pagination import StandardResultsSetPagination


class ParentDashboardViewSet(viewsets.ViewSet):
    """
    ViewSet for parent dashboard functionality
    Parents can view their children's information
    """
    permission_classes = [IsAuthenticated]
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
