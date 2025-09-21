from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'authentication'

urlpatterns = [
    # JWT Authentication endpoints
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # User management endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # Password reset endpoints
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Utility endpoints
    path('current-user/', views.current_user, name='current_user'),
    path('user-context/', views.user_context, name='user_context'),
    
    # FCM token management
    path('fcm-token/', views.UpdateFCMTokenView.as_view(), name='update_fcm_token'),
    
    # Parent management (for school staff)
    path('parents/', views.ParentListView.as_view(), name='parent_list'),
] 