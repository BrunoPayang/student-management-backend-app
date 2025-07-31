from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    # File upload and download
    path('upload/', views.FileUploadView.as_view(), name='file-upload'),
    path('download/<int:pk>/', views.FileDownloadView.as_view(), name='file-download'),
    path('preview/<int:pk>/', views.FilePreviewView.as_view(), name='file-preview'),
    
    # File management
    path('', views.FileListView.as_view(), name='file-list'),
    path('create/', views.FileCreateView.as_view(), name='file-create'),
    path('<int:pk>/', views.FileDetailView.as_view(), name='file-detail'),
    path('<int:pk>/update/', views.FileUpdateView.as_view(), name='file-update'),
    path('<int:pk>/delete/', views.FileDeleteView.as_view(), name='file-delete'),
    
    # File categories and organization
    path('categories/', views.FileCategoryListView.as_view(), name='category-list'),
    path('categories/create/', views.FileCategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/', views.FileCategoryDetailView.as_view(), name='category-detail'),
    path('categories/<int:pk>/files/', views.CategoryFilesView.as_view(), name='category-files'),
    
    # Bulk file operations
    path('bulk-upload/', views.BulkFileUploadView.as_view(), name='bulk-upload'),
    path('bulk-delete/', views.BulkFileDeleteView.as_view(), name='bulk-delete'),
    
    # File sharing and permissions
    path('<int:pk>/share/', views.FileShareView.as_view(), name='file-share'),
    path('<int:pk>/permissions/', views.FilePermissionsView.as_view(), name='file-permissions'),
    
    # File analytics
    path('analytics/', views.FileAnalyticsView.as_view(), name='file-analytics'),
    path('stats/', views.FileStatsView.as_view(), name='file-stats'),
    
    # Firebase Storage integration
    path('firebase/upload/', views.FirebaseUploadView.as_view(), name='firebase-upload'),
    path('firebase/download/<str:file_path>/', views.FirebaseDownloadView.as_view(), name='firebase-download'),
    path('firebase/delete/<str:file_path>/', views.FirebaseDeleteView.as_view(), name='firebase-delete'),
] 