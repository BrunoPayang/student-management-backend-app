from django.urls import path
from . import views

app_name = 'schools'

urlpatterns = [
    # School management endpoints
    path('', views.SchoolListView, name='school-list'),
    path('create/', views.SchoolCreateView, name='school-create'),
    path('<int:pk>/', views.SchoolDetailView, name='school-detail'),
    path('<int:pk>/update/', views.SchoolUpdateView, name='school-update'),
    path('<int:pk>/delete/', views.SchoolDeleteView, name='school-delete'),
    
    # School configuration endpoints
    path('<int:pk>/config/', views.SchoolConfigView, name='school-config'),
    path('<int:pk>/branding/', views.SchoolBrandingView, name='school-branding'),
    
    # School analytics endpoints
    path('<int:pk>/analytics/', views.SchoolAnalyticsView, name='school-analytics'),
    path('<int:pk>/stats/', views.SchoolStatsView, name='school-stats'),
] 