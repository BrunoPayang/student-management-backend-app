from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.students.models import Student, Transcript, BehaviorReport, PaymentRecord
from apps.students.serializers import (
    StudentDetailSerializer, TranscriptSerializer,
    BehaviorReportSerializer, PaymentRecordSerializer
)
from apps.common.pagination import StandardResultsSetPagination


@extend_schema_view(
    my_children=extend_schema(
        summary="Get My Children",
        description="Retrieve all children of the authenticated parent",
        tags=['parents']
    ),
    child_details=extend_schema(
        summary="Get Child Details",
        description="Get detailed information about a specific child",
        tags=['parents']
    ),
    child_transcripts=extend_schema(
        summary="Get Child Transcripts",
        description="Retrieve academic transcripts for a specific child",
        tags=['parents']
    ),
    child_behavior=extend_schema(
        summary="Get Child Behavior Reports",
        description="Retrieve behavior reports for a specific child",
        tags=['parents']
    ),
    child_payments=extend_schema(
        summary="Get Child Payment Records",
        description="Retrieve payment records for a specific child",
        tags=['parents']
    ),
    child_statistics=extend_schema(
        summary="Get Child Statistics",
        description="Get comprehensive statistics for a specific child",
        tags=['parents']
    ),
    notifications=extend_schema(
        summary="Get Parent Notifications",
        description="Retrieve notifications relevant to the parent",
        tags=['parents']
    ),
    notification_preferences=extend_schema(
        summary="Get/Update Notification Preferences",
        description="Get current notification preferences or update them",
        tags=['parents']
    ),
    mark_notification_read=extend_schema(
        summary="Mark Notification as Read",
        description="Mark a specific notification as read for the parent",
        tags=['parents']
    ),
    unread_notifications_count=extend_schema(
        summary="Get Unread Notifications Count",
        description="Get the count of unread notifications for the parent",
        tags=['parents']
    ),
    test_notification=extend_schema(
        summary="Test Notification System",
        description="Send a test notification to all parents in the school (for development/testing)",
        tags=['parents']
    )
)
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
        try:
            # Get notifications for the parent's school
            from apps.notifications.models import Notification, NotificationDelivery
            
            # Determine the parent's school - either from user.school or from student relationships
            parent_school = request.user.school
            if not parent_school:
                # If user.school is not set, get it from their student relationships
                from apps.students.models import ParentStudent
                parent_student = ParentStudent.objects.filter(parent=request.user).first()
                if parent_student:
                    parent_school = parent_student.student.school
            
            if not parent_school:
                return Response(
                    {'error': 'Parent is not associated with any school'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get notifications that target this parent OR are general school notifications
            # For bulk notifications, we need to check if the parent is in target_users
            parent_notifications = Notification.objects.filter(
                Q(school=parent_school) &
                (Q(target_users=request.user) | Q(target_users__isnull=True))
            ).distinct().order_by('-created_at')
            
            # Debug: Log the query and results
            print(f"Parent notifications query: {parent_notifications.query}")
            print(f"Parent user: {request.user.username}, School: {parent_school}")
            print(f"Found {parent_notifications.count()} notifications")
            
            # Apply pagination manually since this is a ViewSet, not ModelViewSet
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(parent_notifications, request)
            if page is not None:
                from apps.notifications.serializers import NotificationSerializer
                serializer = NotificationSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            
            # If no pagination, return all
            from apps.notifications.serializers import NotificationSerializer
            serializer = NotificationSerializer(parent_notifications, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Error retrieving notifications: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['put'])
    def notification_preferences(self, request):
        """Update notification preferences"""
        user = request.user
        
        # Get or create user profile
        profile, created = user.profile.get_or_create()
        
        # Update notification preferences
        if 'receive_sms' in request.data:
            profile.sms_notifications = request.data['receive_sms']
        if 'receive_email' in request.data:
            profile.email_notifications = request.data['receive_email']
        if 'receive_push' in request.data:
            profile.push_notifications = request.data['receive_push']
        
        profile.save()
        
        return Response({
            'message': 'Notification preferences updated successfully',
            'preferences': {
                'receive_sms': profile.sms_notifications,
                'receive_email': profile.email_notifications,
                'receive_push': profile.push_notifications
            }
        })
    
    @action(detail=True, methods=['post'])
    def mark_notification_read(self, request, pk=None):
        """Mark a notification as read for the parent"""
        try:
            from apps.notifications.models import Notification, NotificationDelivery
            
            notification = Notification.objects.get(
                id=pk,
                school=request.user.school
            )
            
            # Create or update delivery record
            delivery, created = NotificationDelivery.objects.get_or_create(
                notification=notification,
                user=request.user
            )
            
            # Mark as read
            delivery.read_at = timezone.now()
            delivery.save()
            
            return Response({
                'message': 'Notification marked as read',
                'notification_id': str(notification.id)
            })
            
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notification not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error marking notification as read: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def unread_notifications_count(self, request):
        """Get count of unread notifications for the parent"""
        try:
            from apps.notifications.models import Notification, NotificationDelivery
            from django.utils import timezone
            
            # Count unread notifications
            unread_count = NotificationDelivery.objects.filter(
                user=request.user,
                read_at__isnull=True
            ).count()
            
            return Response({
                'unread_count': unread_count
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error counting unread notifications: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def notification_preferences(self, request):
        """Get current notification preferences"""
        try:
            # Get or create user profile
            profile, created = request.user.profile.get_or_create()
            
            return Response({
                'preferences': {
                    'receive_sms': profile.sms_notifications,
                    'receive_email': profile.email_notifications,
                    'receive_push': profile.push_notifications
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error retrieving notification preferences: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def test_notification(self, request):
        """Test notification system (for development/testing)"""
        try:
            from apps.notifications.tasks import send_bulk_notification_task
            
            # Get all parents in the same school
            from apps.authentication.models import User
            school_parents = User.objects.filter(
                school=request.user.school,
                user_type='parent'
            )
            
            if not school_parents.exists():
                return Response(
                    {'error': 'No parents found in this school'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Queue a test notification
            task_result = send_bulk_notification_task.delay(
                user_ids=[str(parent.id) for parent in school_parents],
                title="Test Notification from Parent Dashboard",
                body="This is a test notification to verify the Celery system is working",
                notification_type="general",
                school_id=str(request.user.school.id),
                data={'test_source': 'parent_dashboard', 'timestamp': timezone.now().isoformat()}
            )
            
            return Response({
                'message': 'Test notification queued successfully',
                'task_id': task_result.id,
                'target_parents': school_parents.count(),
                'status': 'queued'
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error sending test notification: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
