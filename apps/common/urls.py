from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .views import HealthCheckView

@api_view(['GET'])
def api_root(request, format=None):
    """
    API Root - Lists all available endpoints
    """
    return Response({
        'authentication': {
            'login': reverse('authentication:login', request=request, format=format),
            'register': reverse('authentication:register', request=request, format=format),
            'refresh': reverse('authentication:token_refresh', request=request, format=format),
            'logout': reverse('authentication:logout', request=request, format=format),
            'profile': reverse('authentication:profile', request=request, format=format),
        },
        'schools': {
            'list': reverse('school-list', request=request, format=format),
        },
        'students': {
            'list': reverse('student-list', request=request, format=format),
            'transcripts': reverse('transcript-list', request=request, format=format),
            'behavior_reports': reverse('behavior-report-list', request=request, format=format),
            'payment_records': reverse('payment-record-list', request=request, format=format),
        },
        'parents': {
            'dashboard': reverse('parent-dashboard-list', request=request, format=format),
        },
        'documentation': {
            'swagger': reverse('swagger-ui', request=request, format=format),
            'redoc': reverse('redoc', request=request, format=format),
            'schema': reverse('schema', request=request, format=format),
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('health/', HealthCheckView, name='health-check'),
] 