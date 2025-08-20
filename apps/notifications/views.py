from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from rest_framework import serializers

from .models import Notification, NotificationDelivery
from .serializers import NotificationSerializer, NotificationCreateSerializer, NotificationDeliverySerializer
from .services import NotificationService
from apps.authentication.permissions import IsSchoolStaff
from apps.common.pagination import StandardResultsSetPagination

@extend_schema_view(
    list=extend_schema(
        summary="List Notifications",
        description="Retrieve a list of notifications with pagination and filtering",
        tags=['notifications'],
        parameters=[
            OpenApiParameter(name='notification_type', description='Filter by notification type', required=False),
            OpenApiParameter(name='sent_via_fcm', description='Filter by FCM delivery status', required=False),
            OpenApiParameter(name='created_at', description='Filter by creation date', required=False),
        ]
    ),
    create=extend_schema(
        summary="Create Notification",
        description="Create a new notification. The school will be automatically assigned from your user account.",
        tags=['notifications'],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': 'Notification title'},
                    'body': {'type': 'string', 'description': 'Notification content'},
                    'notification_type': {
                        'type': 'string', 
                        'enum': ['academic', 'behavior', 'payment', 'general'],
                        'description': 'Type of notification'
                    },
                    'target_users': {
                        'type': 'array', 
                        'items': {'type': 'integer'},
                        'description': 'Target user IDs (optional)'
                    },
                    'data': {
                        'type': 'object',
                        'description': 'Additional data for the notification (optional)'
                    }
                },
                'required': ['title', 'body', 'notification_type']
            }
        ),
        responses={
            201: NotificationSerializer,
            400: {'description': 'Validation error - check that user has a school assigned'},
            500: {'description': 'Creation failed'}
        },
        examples=[
            OpenApiExample(
                'Test Notification',
                value={
                    'title': 'Test Notification from Postman',
                    'body': 'This is a test notification sent via Postman to test Phase 5 features',
                    'notification_type': 'general',
                    'data': {
                        'test_source': 'postman',
                        'feature': 'notifications',
                        'timestamp': '2024-01-19'
                    }
                },
                request_only=True
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Get Notification Details",
        description="Retrieve detailed information about a specific notification",
        tags=['notifications']
    ),
    update=extend_schema(
        summary="Update Notification",
        description="Update notification content and settings",
        tags=['notifications']
    ),
    destroy=extend_schema(
        summary="Delete Notification",
        description="Delete a notification",
        tags=['notifications']
    )
)
class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for notification management with FCM and email support"""
    queryset = Notification.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['notification_type', 'sent_via_fcm', 'created_at']

    def get_queryset(self):
        """Filter by school and permissions"""
        user = self.request.user

        if user.is_system_admin():
            return Notification.objects.all()
        elif user.is_school_staff():
            return Notification.objects.filter(school=user.school)
        elif user.is_parent():
            return Notification.objects.filter(
                target_users=user,
                school__students__parents__parent=user
            ).distinct()
        else:
            return Notification.objects.none()

    def get_serializer_class(self):
        """Return appropriate serializer"""
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]  # Allow any authenticated user for testing
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Create notification with proper school assignment"""
        # Check if user has a school
        if not hasattr(self.request.user, 'school') or not self.request.user.school:
            raise serializers.ValidationError("User must be associated with a school to create notifications")
        
        # The serializer will handle the rest
        return serializer.save()

    @extend_schema(
        summary="Send Bulk Notification",
        description="""
        Send a notification to multiple users simultaneously.
        
        **Features:**
        - Multi-user targeting
        - Automatic delivery tracking
        - FCM push notifications (when configured)
        - Email fallback (when configured)
        - Mock service for development (free)
        
        **Delivery Channels:**
        - **FCM**: Firebase Cloud Messaging for push notifications
        - **Email**: SMTP-based email delivery
        - **Mock**: Local logging for development/testing
        
        **Notification Types:**
        - Academic updates
        - Behavior reports
        - Payment reminders
        - General announcements
        
        **Targeting Options:**
        - Specific user IDs
        - All school users (if no user_ids provided)
        - School-based filtering
        """,
        tags=['notifications'],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': 'Notification title'},
                    'body': {'type': 'string', 'description': 'Notification content'},
                    'notification_type': {
                        'type': 'string', 
                        'enum': ['academic', 'behavior', 'payment', 'general'],
                        'description': 'Type of notification'
                    },
                    'user_ids': {
                        'type': 'array', 
                        'items': {'type': 'integer'},
                        'description': 'Target user IDs (empty for all school users)'
                    },
                    'data': {
                        'type': 'object',
                        'description': 'Additional data for the notification'
                    }
                },
                'required': ['title', 'body', 'notification_type']
            }
        },
        responses={
            200: {
                'description': 'Bulk notification sent successfully',
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'results': {
                        'type': 'object',
                        'properties': {
                            'fcm_sent': {'type': 'integer'},
                            'email_sent': {'type': 'integer'},
                            'total_targets': {'type': 'integer'}
                        }
                    }
                }
            },
            400: {'description': 'Validation error'},
            500: {'description': 'Sending failed'}
        },
        examples=[
            OpenApiExample(
                'Academic Update',
                value={
                    'title': 'New Grade Posted',
                    'body': 'Your child\'s latest grades have been posted. Check the portal for details.',
                    'notification_type': 'academic',
                    'user_ids': [1, 2, 3],
                    'data': {'subject': 'Mathematics', 'grade': 'A'}
                },
                request_only=True
            ),
            OpenApiExample(
                'General Announcement',
                value={
                    'title': 'School Event Reminder',
                    'body': 'Don\'t forget about the parent-teacher meeting tomorrow at 3 PM.',
                    'notification_type': 'general',
                    'data': {'event_date': '2024-01-20', 'event_time': '15:00'}
                },
                request_only=True
            )
        ]
    )
    @action(detail=False, methods=['post'])
    def send_bulk(self, request):
        """Send bulk notification to multiple users"""
        try:
            title = request.data.get('title')
            body = request.data.get('body')
            notification_type = request.data.get('notification_type', 'general')
            user_ids = request.data.get('user_ids', [])

            if not title or not body:
                return Response(
                    {'error': 'Title and body are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get target users
            if user_ids:
                from apps.authentication.models import User
                users = User.objects.filter(id__in=user_ids, school=request.user.school)
            else:
                from apps.authentication.models import User
                users = User.objects.filter(school=request.user.school)

            # Send notification
            notification_service = NotificationService()
            results = notification_service.send_bulk_notification(
                users=users,
                title=title,
                body=body,
                notification_type=notification_type,
                school=request.user.school,
                data=request.data.get('data', {})
            )

            return Response({
                'message': 'Bulk notification sent successfully',
                'results': results
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Resend Notification",
        description="Resend a notification to all target users",
        tags=['notifications'],
        responses={
            200: {
                'description': 'Notification resent successfully',
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'results': {
                        'type': 'object',
                        'properties': {
                            'fcm_sent': {'type': 'integer'},
                            'email_sent': {'type': 'integer'},
                            'total_targets': {'type': 'integer'}
                        }
                    }
                }
            },
            500: {'description': 'Resending failed'}
        }
    )
    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        """Resend notification"""
        notification = self.get_object()

        try:
            notification_service = NotificationService()
            results = notification_service.send_notification(notification)

            return Response({
                'message': 'Notification resent successfully',
                'results': results
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@extend_schema_view(
    list=extend_schema(
        summary="List Notification Deliveries",
        description="Retrieve delivery tracking information for notifications",
        tags=['notifications']
    ),
    retrieve=extend_schema(
        summary="Get Delivery Details",
        description="Retrieve detailed delivery information for a specific notification",
        tags=['notifications']
    )
)
class NotificationDeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for notification delivery tracking"""
    queryset = NotificationDelivery.objects.all()
    serializer_class = NotificationDeliverySerializer
    permission_classes = [IsAuthenticated, IsSchoolStaff]

    def get_queryset(self):
        """Filter by school"""
        return NotificationDelivery.objects.filter(
            notification__school=self.request.user.school
        )
