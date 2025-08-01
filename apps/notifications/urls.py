from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notification management
    path('', views.NotificationListView, name='notification-list'),
    path('create/', views.NotificationCreateView, name='notification-create'),
    path('<int:pk>/', views.NotificationDetailView, name='notification-detail'),
    path('<int:pk>/update/', views.NotificationUpdateView, name='notification-update'),
    path('<int:pk>/delete/', views.NotificationDeleteView, name='notification-delete'),
    
    # FCM token management
    path('fcm-token/', views.FCMTokenView, name='fcm-token'),
    path('fcm-token/update/', views.FCMTokenUpdateView, name='fcm-token-update'),
    path('fcm-token/delete/', views.FCMTokenDeleteView, name='fcm-token-delete'),
    
    # Notification sending
    path('send/', views.SendNotificationView, name='send-notification'),
    path('send-bulk/', views.SendBulkNotificationView, name='send-bulk-notification'),
    
    # Notification templates
    path('templates/', views.NotificationTemplateListView, name='template-list'),
    path('templates/create/', views.NotificationTemplateCreateView, name='template-create'),
    path('templates/<int:pk>/', views.NotificationTemplateDetailView, name='template-detail'),
    path('templates/<int:pk>/update/', views.NotificationTemplateUpdateView, name='template-update'),
    path('templates/<int:pk>/delete/', views.NotificationTemplateDeleteView, name='template-delete'),
    
    # Notification history and analytics
    path('history/', views.NotificationHistoryView, name='notification-history'),
    path('analytics/', views.NotificationAnalyticsView, name='notification-analytics'),
    path('stats/', views.NotificationStatsView, name='notification-stats'),
    
    # User notification preferences
    path('preferences/', views.NotificationPreferencesView, name='preferences'),
    path('preferences/update/', views.NotificationPreferencesUpdateView, name='preferences-update'),
] 