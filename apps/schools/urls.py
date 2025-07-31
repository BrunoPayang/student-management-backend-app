from django.urls import path
from . import views

app_name = 'schools'

urlpatterns = [
    # School management endpoints
    path('', views.SchoolListView.as_view(), name='school-list'),
    path('create/', views.SchoolCreateView.as_view(), name='school-create'),
    path('<int:pk>/', views.SchoolDetailView.as_view(), name='school-detail'),
    path('<int:pk>/update/', views.SchoolUpdateView.as_view(), name='school-update'),
    path('<int:pk>/delete/', views.SchoolDeleteView.as_view(), name='school-delete'),
    
    # School configuration endpoints
    path('<int:pk>/config/', views.SchoolConfigView.as_view(), name='school-config'),
    path('<int:pk>/branding/', views.SchoolBrandingView.as_view(), name='school-branding'),
    
    # School analytics endpoints
    path('<int:pk>/analytics/', views.SchoolAnalyticsView.as_view(), name='school-analytics'),
    path('<int:pk>/stats/', views.SchoolStatsView.as_view(), name='school-stats'),
] 