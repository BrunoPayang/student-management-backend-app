from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from django_celery_results.models import TaskResult
from celery import current_app
from drf_spectacular.utils import extend_schema, extend_schema_view
from .serializers import TaskResultSerializer


class TaskResultPermission(BasePermission):
    """Custom permission for TaskResult access"""
    
    def has_permission(self, request, view):
        # Only admin users and school staff can access task results
        if not request.user.is_authenticated:
            return False
        
        # Admin users can access all tasks
        if hasattr(request.user, 'is_system_admin') and request.user.is_system_admin():
            return True
        
        # School staff can access tasks for their school
        if hasattr(request.user, 'user_type') and request.user.user_type in ['school_staff']:
            return True
        
        # Parents and other users cannot access tasks
        return False


# Create your views here.

@extend_schema_view(
    list=extend_schema(
        summary="List Task Results",
        description="Retrieve a list of completed task results",
        tags=['tasks']
    ),
    retrieve=extend_schema(
        summary="Get Task Result",
        description="Retrieve detailed information about a specific task result",
        tags=['tasks']
    )
)
class TaskResultViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for monitoring task results"""
    queryset = TaskResult.objects.all()
    serializer_class = TaskResultSerializer
    permission_classes = [TaskResultPermission]
    
    def get_queryset(self):
        """Filter by user's school or show all for admin users"""
        if hasattr(self.request.user, 'is_system_admin') and self.request.user.is_system_admin():
            # Admin users can see all task results
            return TaskResult.objects.all()
        elif hasattr(self.request.user, 'school') and self.request.user.school:
            # School staff can see tasks for their school
            return TaskResult.objects.filter(
                task_name__startswith=f'school_{self.request.user.school.id}'
            )
        else:
            # Users without school assignment see no tasks
            return TaskResult.objects.none()
    
    @extend_schema(
        summary="Get Active Tasks",
        description="Get list of currently running tasks",
        tags=['tasks']
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active tasks"""
        try:
            inspector = current_app.control.inspect()
            active_tasks = inspector.active()
            
            return Response({
                'active_tasks': active_tasks or {},
                'total_active': sum(len(tasks) for tasks in (active_tasks or {}).values())
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Get Worker Status",
        description="Get status of Celery workers",
        tags=['tasks']
    )
    @action(detail=False, methods=['get'])
    def workers(self, request):
        """Get worker status"""
        try:
            inspector = current_app.control.inspect()
            stats = inspector.stats()
            ping = inspector.ping()
            
            return Response({
                'workers': stats or {},
                'ping': ping or {},
                'total_workers': len(stats or {})
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
