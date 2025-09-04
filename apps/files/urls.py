from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'files'

router = DefaultRouter()
router.register(r'files', views.FileUploadViewSet, basename='file-upload')

urlpatterns = [
    path('', include(router.urls)),
] 