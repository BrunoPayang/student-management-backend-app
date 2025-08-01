from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    # File upload and download
    path('upload/', views.FileUploadView, name='file-upload'),
    path('download/<int:pk>/', views.FileDownloadView, name='file-download'),
    path('preview/<int:pk>/', views.FilePreviewView, name='file-preview'),
    
    # File management
    path('', views.FileListView, name='file-list'),
    path('create/', views.FileCreateView, name='file-create'),
    path('<int:pk>/', views.FileDetailView, name='file-detail'),
    path('<int:pk>/update/', views.FileUpdateView, name='file-update'),
    path('<int:pk>/delete/', views.FileDeleteView, name='file-delete'),
    
    # File categories and organization
    path('categories/', views.FileCategoryListView, name='category-list'),
    path('categories/create/', views.FileCategoryCreateView, name='category-create'),
    path('categories/<int:pk>/', views.FileCategoryDetailView, name='category-detail'),
    path('categories/<int:pk>/files/', views.CategoryFilesView, name='category-files'),
    
    # Bulk file operations
    path('bulk-upload/', views.BulkFileUploadView, name='bulk-upload'),
    path('bulk-delete/', views.BulkFileDeleteView, name='bulk-delete'),
    
    # File sharing and permissions
    path('<int:pk>/share/', views.FileShareView, name='file-share'),
    path('<int:pk>/permissions/', views.FilePermissionsView, name='file-permissions'),
    
    # File analytics
    path('analytics/', views.FileAnalyticsView, name='file-analytics'),
    path('stats/', views.FileStatsView, name='file-stats'),
    
    # Firebase Storage integration
    path('firebase/upload/', views.FirebaseUploadView, name='firebase-upload'),
    path('firebase/download/<str:file_path>/', views.FirebaseDownloadView, name='firebase-download'),
    path('firebase/delete/<str:file_path>/', views.FirebaseDeleteView, name='firebase-delete'),
] 