from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/schools/', include('apps.schools.urls')),
    path('api/students/', include('apps.students.urls')),
    path('api/parents/', include('apps.parents.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/files/', include('apps.files.urls')),
    path('api/common/', include('apps.common.urls')),
    
    # Health check endpoint for Railway
    path('health/', csrf_exempt(lambda request: JsonResponse({
        'status': 'healthy',
        'message': 'SchoolConnect API is running',
        'timestamp': '2025-08-02T01:05:21Z'
    })), name='health-check'),
    
    # API root endpoint
    path('', csrf_exempt(lambda request: JsonResponse({
        'message': 'SchoolConnect API',
        'version': '1.0.0',
        'endpoints': {
            'authentication': '/api/auth/',
            'schools': '/api/schools/',
            'students': '/api/students/',
            'parents': '/api/parents/',
            'notifications': '/api/notifications/',
            'files': '/api/files/',
            'common': '/api/common/',
            'admin': '/admin/',
            'health': '/health/',
        }
    })), name='api-root'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Add debug toolbar URLs
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns