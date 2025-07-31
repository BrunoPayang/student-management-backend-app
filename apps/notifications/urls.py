from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notification management
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('create/', views.NotificationCreateView.as_view(), name='notification-create'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('<int:pk>/update/', views.NotificationUpdateView.as_view(), name='notification-update'),
    path('<int:pk>/delete/', views.NotificationDeleteView.as_view(), name='notification-delete'),
    
    # FCM token management
    path('fcm-token/', views.FCMTokenView.as_view(), name='fcm-token'),
    path('fcm-token/update/', views.FCMTokenUpdateView.as_view(), name='fcm-token-update'),
    path('fcm-token/delete/', views.FCMTokenDeleteView.as_view(), name='fcm-token-delete'),
    
    # Notification sending
    path('send/', views.SendNotificationView.as_view(), name='send-notification'),
    path('send-bulk/', views.SendBulkNotificationView.as_view(), name='send-bulk-notification'),
    
    # Notification templates
    path('templates/', views.NotificationTemplateListView.as_view(), name='template-list'),
    path('templates/create/', views.NotificationTemplateCreateView.as_view(), name='template-create'),
    path('templates/<int:pk>/', views.NotificationTemplateDetailView.as_view(), name='template-detail'),
    path('templates/<int:pk>/update/', views.NotificationTemplateUpdateView.as_view(), name='template-update'),
    path('templates/<int:pk>/delete/', views.NotificationTemplateDeleteView.as_view(), name='template-delete'),
    
    # Notification history and analytics
    path('history/', views.NotificationHistoryView.as_view(), name='notification-history'),
    path('analytics/', views.NotificationAnalyticsView.as_view(), name='notification-analytics'),
    path('stats/', views.NotificationStatsView.as_view(), name='notification-stats'),
    
    # User notification preferences
    path('preferences/', views.NotificationPreferencesView.as_view(), name='preferences'),
    path('preferences/update/', views.NotificationPreferencesUpdateView.as_view(), name='preferences-update'),
] 