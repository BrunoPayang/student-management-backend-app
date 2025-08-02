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
                    'error': 'Authentification requise'
                }, status=401)
            
            if request.user.user_type not in allowed_types:
                return JsonResponse({
                    'error': 'Permissions insuffisantes'
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
                'error': 'Authentification requise'
            }, status=401)
        
        # System admins can access everything
        if request.user.is_system_admin():
            return view_func(request, *args, **kwargs)
        
        # Check if user has school context
        if not request.user.school:
            return JsonResponse({
                'error': 'Utilisateur non associé à une école'
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
            logger = logging.getLogger('schoolconnect')
            
            user_info = 'Anonymous'
            if request.user.is_authenticated:
                user_info = f"{request.user.username} ({request.user.user_type})"
            
            logger.info(f"Action: {action_type} - User: {user_info} - Path: {request.path}")
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator 