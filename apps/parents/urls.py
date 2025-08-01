from django.urls import path
from . import views

app_name = 'parents'

urlpatterns = [
    # Parent dashboard
    path('dashboard/', views.ParentDashboardView, name='parent-dashboard'),
    
    # Parent's children management
    path('children/', views.ParentChildrenListView, name='children-list'),
    path('children/<int:student_id>/', views.ParentChildDetailView, name='child-detail'),
    
    # Child academic records (parent view)
    path('children/<int:student_id>/transcripts/', views.ParentTranscriptListView, name='child-transcripts'),
    path('children/<int:student_id>/transcripts/<int:transcript_id>/', views.ParentTranscriptDetailView, name='child-transcript-detail'),
    
    # Child behavior reports (parent view)
    path('children/<int:student_id>/behavior/', views.ParentBehaviorListView, name='child-behavior'),
    path('children/<int:student_id>/behavior/<int:report_id>/', views.ParentBehaviorDetailView, name='child-behavior-detail'),
    
    # Child payment status (parent view)
    path('children/<int:student_id>/payments/', views.ParentPaymentListView, name='child-payments'),
    path('children/<int:student_id>/payments/<int:payment_id>/', views.ParentPaymentDetailView, name='child-payment-detail'),
    
    # Parent profile management
    path('profile/', views.ParentProfileView, name='parent-profile'),
    path('profile/update/', views.ParentProfileUpdateView, name='parent-profile-update'),
    
    # Notification preferences
    path('notifications/preferences/', views.NotificationPreferencesView, name='notification-preferences'),
    path('notifications/preferences/update/', views.NotificationPreferencesUpdateView, name='notification-preferences-update'),
    
    # Parent-student linking
    path('link-student/', views.LinkStudentView, name='link-student'),
    path('unlink-student/<int:student_id>/', views.UnlinkStudentView, name='unlink-student'),
] 