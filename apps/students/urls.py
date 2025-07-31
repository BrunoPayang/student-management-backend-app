from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Student management endpoints
    path('', views.StudentListView.as_view(), name='student-list'),
    path('create/', views.StudentCreateView.as_view(), name='student-create'),
    path('<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    path('<int:pk>/update/', views.StudentUpdateView.as_view(), name='student-update'),
    path('<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student-delete'),
    
    # Bulk operations
    path('bulk-import/', views.StudentBulkImportView.as_view(), name='student-bulk-import'),
    path('bulk-export/', views.StudentBulkExportView.as_view(), name='student-bulk-export'),
    
    # Academic records
    path('<int:pk>/transcripts/', views.TranscriptListView.as_view(), name='transcript-list'),
    path('<int:pk>/transcripts/create/', views.TranscriptCreateView.as_view(), name='transcript-create'),
    path('<int:pk>/transcripts/<int:transcript_id>/', views.TranscriptDetailView.as_view(), name='transcript-detail'),
    
    # Behavior reports
    path('<int:pk>/behavior/', views.BehaviorReportListView.as_view(), name='behavior-list'),
    path('<int:pk>/behavior/create/', views.BehaviorReportCreateView.as_view(), name='behavior-create'),
    path('<int:pk>/behavior/<int:report_id>/', views.BehaviorReportDetailView.as_view(), name='behavior-detail'),
    
    # Payment records
    path('<int:pk>/payments/', views.PaymentRecordListView.as_view(), name='payment-list'),
    path('<int:pk>/payments/create/', views.PaymentRecordCreateView.as_view(), name='payment-create'),
    path('<int:pk>/payments/<int:payment_id>/', views.PaymentRecordDetailView.as_view(), name='payment-detail'),
    
    # Search and filtering
    path('search/', views.StudentSearchView.as_view(), name='student-search'),
    path('filter/', views.StudentFilterView.as_view(), name='student-filter'),
] 