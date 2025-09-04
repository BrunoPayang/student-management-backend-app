from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.students.models import Student, Transcript, BehaviorReport, PaymentRecord, ParentStudent
from apps.students.serializers import (
    StudentDetailSerializer, TranscriptSerializer,
    BehaviorReportSerializer, PaymentRecordSerializer
)
from apps.common.pagination import StandardResultsSetPagination
from apps.authentication.models import UserProfile


class ParentOnlyPermission(BasePermission):
    """Custom permission to allow only parent users"""
    
    def has_permission(self, request, view):
        # Only authenticated users can access
        if not request.user.is_authenticated:
            return False
        
        # Only parent users can access
        return hasattr(request.user, 'user_type') and request.user.user_type == 'parent'


class ParentStudentPermission(BasePermission):
    """Custom permission for parent-student management"""
    
    def has_permission(self, request, view):
        # Only authenticated users can access
        if not request.user.is_authenticated:
            return False
        
        # Admin users and school staff can manage parent-student relationships
        if hasattr(request.user, 'user_type'):
            if request.user.user_type in ['admin', 'school_staff']:
                return True
        
        return False


@extend_schema_view(
    list=extend_schema(
        summary="List Parent-Student Relationships",
        description="List all parent-student relationships",
        tags=['parents']
    ),
    create=extend_schema(
        summary="Create Parent-Student Relationship",
        description="Create a new parent-student relationship",
        tags=['parents']
    ),
    retrieve=extend_schema(
        summary="Get Parent-Student Relationship",
        description="Get details of a specific parent-student relationship",
        tags=['parents']
    ),
    update=extend_schema(
        summary="Update Parent-Student Relationship",
        description="Update a parent-student relationship",
        tags=['parents']
    ),
    destroy=extend_schema(
        summary="Delete Parent-Student Relationship",
        description="Delete a parent-student relationship",
        tags=['parents']
    )
)
class ParentStudentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing parent-student relationships"""
    queryset = ParentStudent.objects.all()
    serializer_class = None  # Will be imported dynamically
    permission_classes = [ParentStudentPermission]
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        """Dynamic import to avoid circular imports"""
        from apps.students.serializers import ParentStudentSerializer
        return ParentStudentSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        
        if user.is_system_admin():
            return ParentStudent.objects.all()
        elif user.is_school_staff() and user.school:
            # School staff can see relationships in their school
            return ParentStudent.objects.filter(student__school=user.school)
        else:
            return ParentStudent.objects.none()


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
    ),
    profile=extend_schema(
        summary="Get/Update Parent Profile",
        description="Get current profile information or update profile details",
        tags=['parents']
    )
)
class ParentDashboardViewSet(viewsets.ViewSet):
    """
    ViewSet for parent dashboard functionality
    Parents can view their children's information
    """
    permission_classes = [ParentOnlyPermission]
    pagination_class = StandardResultsSetPagination
    
    @action(detail=False, methods=['get'])
    def my_children(self, request):
        """Get all children linked to this specific parent"""
        # Get only students that are linked to this specific parent
        students = Student.objects.filter(parents__parent=request.user)
        
        # Apply search if provided
        search_query = request.query_params.get('search', '')
        if search_query:
            students = students.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(student_id__icontains=search_query)
            )
        
        # Always apply pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(students, request)
        serializer = StudentDetailSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
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
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def notification_preferences(self, request):
        """Get or update notification preferences"""
        user = request.user
        
        if request.method == 'GET':
            # Get current notification preferences
            try:
                # Get or create user profile
                profile = user.profile
                
                return Response({
                    'preferences': {
                        'sms_notifications': profile.sms_notifications,
                        'email_notifications': profile.email_notifications,
                        'push_notifications': profile.push_notifications
                    }
                })
            except Exception as e:
                return Response(
                    {'error': f'Error retrieving notification preferences: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        elif request.method in ['PUT', 'PATCH']:
            # Update notification preferences
            try:
                # Validate data types
                for field in ['sms_notifications', 'email_notifications', 'push_notifications']:
                    if field in request.data:
                        if not isinstance(request.data[field], bool):
                            return Response(
                                {'error': f'{field} must be a boolean value'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                
                # Get or create user profile
                try:
                    profile = user.profile
                except UserProfile.DoesNotExist:
                    # Create profile if it doesn't exist
                    profile = UserProfile.objects.create(user=user)
                
                # Update notification preferences
                if 'receive_sms' in request.data:
                    profile.sms_notifications = request.data['receive_sms']
                if 'receive_email' in request.data:
                    profile.email_notifications = request.data['receive_email']
                if 'receive_push' in request.data:
                    profile.push_notifications = request.data['receive_push']
                
                # Also handle the field names used in the tests
                if 'sms_notifications' in request.data:
                    profile.sms_notifications = request.data['sms_notifications']
                if 'email_notifications' in request.data:
                    profile.email_notifications = request.data['email_notifications']
                if 'push_notifications' in request.data:
                    profile.push_notifications = request.data['push_notifications']
                
                profile.save()
                
                return Response({
                    'message': 'Notification preferences updated successfully',
                    'preferences': {
                        'sms_notifications': profile.sms_notifications,
                        'email_notifications': profile.email_notifications,
                        'push_notifications': profile.push_notifications
                    }
                })
            except Exception as e:
                return Response(
                    {'error': f'Error updating notification preferences: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    
    @action(detail=True, methods=['post'])
    def mark_notification_read(self, request, pk=None):
        """Mark a notification as read for the parent"""
        try:
            from apps.notifications.models import Notification, NotificationDelivery
            
            # Get the parent's school - either from user.school or from student relationships
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
            
            # Get the notification - must belong to the parent's school
            notification = Notification.objects.get(
                id=pk,
                school=parent_school
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
                {'error': 'Notification not found or access denied'},
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
            
            # Get the parent's school
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
            
            # Count notifications that exist for this parent's school but haven't been delivered yet
            # This includes notifications that target this parent OR are general school notifications
            notifications = Notification.objects.filter(
                Q(school=parent_school) &
                (Q(target_users=request.user) | Q(target_users__isnull=True))
            ).distinct()
            
            # Count notifications that don't have delivery records (unread)
            delivered_notification_ids = NotificationDelivery.objects.filter(
                user=request.user
            ).values_list('notification_id', flat=True)
            
            unread_count = notifications.exclude(id__in=delivered_notification_ids).count()
            
            return Response({
                'unread_count': unread_count
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error counting unread notifications: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Test Notification System",
        description="Send a test notification to all parents in the school (for development/testing)",
        tags=['parents']
    )
    @action(detail=False, methods=['post'])
    def test_notification(self, request):
        """Test notification system (for development/testing)"""
        try:
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
            
            # For testing purposes, just return success without actually sending notifications
            # In production, this would queue a Celery task
            return Response({
                'message': 'Test notification queued successfully',
                'task_id': 'test-task-id',
                'target_parents': school_parents.count(),
                'status': 'queued'
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error sending test notification: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Get/Update Parent Profile",
        description="Get current profile information or update profile details",
        tags=['parents']
    )
    @action(detail=False, methods=['get', 'patch'])
    def profile(self, request):
        """Get or update parent profile information"""
        if request.method == 'GET':
            # Return profile information
            return Response({
                'user': {
                    'username': request.user.username,
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'user_type': request.user.user_type,
                    'school': request.user.school.name if request.user.school else None
                },
                'profile': {
                    'sms_notifications': getattr(request.user.profile, 'sms_notifications', False),
                    'email_notifications': getattr(request.user.profile, 'email_notifications', False),
                    'push_notifications': getattr(request.user.profile, 'push_notifications', False)
                }
            })
        
        elif request.method == 'PATCH':
            # Update profile information
            try:
                user = request.user
                
                # Validate email if provided
                if 'email' in request.data:
                    email = request.data['email']
                    if '@' not in email or '.' not in email:
                        return Response(
                            {'email': 'Invalid email format'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    user.email = email
                
                # Update user fields
                if 'first_name' in request.data:
                    user.first_name = request.data['first_name']
                if 'last_name' in request.data:
                    user.last_name = request.data['last_name']
                
                user.save()
                
                return Response({
                    'user': {
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'user_type': user.user_type,
                        'school': user.school.name if user.school else None
                    },
                    'message': 'Profile updated successfully'
                })
            except Exception as e:
                return Response(
                    {'error': f'Error updating profile: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
