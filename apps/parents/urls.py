from django.urls import path
from . import views

app_name = 'parents'

urlpatterns = [
    # Parent dashboard
    path('dashboard/', views.ParentDashboardView.as_view(), name='parent-dashboard'),
    
    # Parent's children management
    path('children/', views.ParentChildrenListView.as_view(), name='children-list'),
    path('children/<int:student_id>/', views.ParentChildDetailView.as_view(), name='child-detail'),
    
    # Child academic records (parent view)
    path('children/<int:student_id>/transcripts/', views.ParentTranscriptListView.as_view(), name='child-transcripts'),
    path('children/<int:student_id>/transcripts/<int:transcript_id>/', views.ParentTranscriptDetailView.as_view(), name='child-transcript-detail'),
    
    # Child behavior reports (parent view)
    path('children/<int:student_id>/behavior/', views.ParentBehaviorListView.as_view(), name='child-behavior'),
    path('children/<int:student_id>/behavior/<int:report_id>/', views.ParentBehaviorDetailView.as_view(), name='child-behavior-detail'),
    
    # Child payment status (parent view)
    path('children/<int:student_id>/payments/', views.ParentPaymentListView.as_view(), name='child-payments'),
    path('children/<int:student_id>/payments/<int:payment_id>/', views.ParentPaymentDetailView.as_view(), name='child-payment-detail'),
    
    # Parent profile management
    path('profile/', views.ParentProfileView.as_view(), name='parent-profile'),
    path('profile/update/', views.ParentProfileUpdateView.as_view(), name='parent-profile-update'),
    
    # Notification preferences
    path('notifications/preferences/', views.NotificationPreferencesView.as_view(), name='notification-preferences'),
    path('notifications/preferences/update/', views.NotificationPreferencesUpdateView.as_view(), name='notification-preferences-update'),
    
    # Parent-student linking
    path('link-student/', views.LinkStudentView.as_view(), name='link-student'),
    path('unlink-student/<int:student_id>/', views.UnlinkStudentView.as_view(), name='unlink-student'),
] 