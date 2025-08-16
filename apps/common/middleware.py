from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from apps.schools.models import School


class SchoolTenantMiddleware(MiddlewareMixin):
    """
    Middleware to handle multi-tenant school context
    """
    def process_request(self, request):
        # Skip for admin and authentication endpoints
        if request.path.startswith('/admin/') or request.path.startswith('/api/auth/'):
            return None
        
        # Get school context from user or request headers
        school = None
        
        if request.user.is_authenticated:
            if request.user.school:
                school = request.user.school
            elif request.user.is_system_admin():
                # System admin can access all schools
                # Check for school_id in headers or query params
                school_id = request.headers.get('X-School-ID') or request.GET.get('school_id')
                if school_id:
                    try:
                        school = School.objects.get(id=school_id)
                    except School.DoesNotExist:
                        pass
        
        # Set school context in request
        request.school = school
        return None


class APILoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log API requests for monitoring
    """
    def process_request(self, request):
        if request.path.startswith('/api/'):
            import logging
            logger = logging.getLogger('schoolconnect')
            
            user_info = 'Anonymous'
            if request.user.is_authenticated:
                user_info = f"{request.user.username} ({request.user.user_type})"
            
            logger.info(
                f"API Request: {request.method} {request.path} - User: {user_info}"
            )
        
        return None 