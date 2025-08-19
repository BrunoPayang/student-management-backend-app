from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'notifications'

router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'notification-deliveries', views.NotificationDeliveryViewSet, basename='notification-delivery')

urlpatterns = [
    path('api/', include(router.urls)),
] 