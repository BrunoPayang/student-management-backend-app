from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Student management endpoints
    path('', views.StudentListView, name='student-list'),
    path('create/', views.StudentCreateView, name='student-create'),
    path('<int:pk>/', views.StudentDetailView, name='student-detail'),
    path('<int:pk>/update/', views.StudentUpdateView, name='student-update'),
    path('<int:pk>/delete/', views.StudentDeleteView, name='student-delete'),
    
    # Bulk operations
    path('bulk-import/', views.StudentBulkImportView, name='student-bulk-import'),
    path('bulk-export/', views.StudentBulkExportView, name='student-bulk-export'),
    
    # Academic records
    path('<int:pk>/transcripts/', views.TranscriptListView, name='transcript-list'),
    path('<int:pk>/transcripts/create/', views.TranscriptCreateView, name='transcript-create'),
    path('<int:pk>/transcripts/<int:transcript_id>/', views.TranscriptDetailView, name='transcript-detail'),
    
    # Behavior reports
    path('<int:pk>/behavior/', views.BehaviorReportListView, name='behavior-list'),
    path('<int:pk>/behavior/create/', views.BehaviorReportCreateView, name='behavior-create'),
    path('<int:pk>/behavior/<int:report_id>/', views.BehaviorReportDetailView, name='behavior-detail'),
    
    # Payment records
    path('<int:pk>/payments/', views.PaymentRecordListView, name='payment-list'),
    path('<int:pk>/payments/create/', views.PaymentRecordCreateView, name='payment-create'),
    path('<int:pk>/payments/<int:payment_id>/', views.PaymentRecordDetailView, name='payment-detail'),
    
    # Search and filtering
    path('search/', views.StudentSearchView, name='student-search'),
    path('filter/', views.StudentFilterView, name='student-filter'),
] 