from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # API Root
    path('api/', include('apps.common.urls')),
    
    # Authentication URLs with api/auth/ prefix
    path('api/auth/', include('apps.authentication.urls')),
    
    # App URLs
    path('', include('apps.schools.urls')),
    path('', include('apps.students.urls')),
    path('', include('apps.parents.urls')),
    path('', include('apps.files.urls')),
    path('', include('apps.notifications.urls')),
    path('', include('apps.tasks.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)