from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    # Health check and system status
    path('health/', views.HealthCheckView, name='health-check'),
    path('status/', views.SystemStatusView, name='system-status'),
    
    # API documentation and info
    path('api-info/', views.APIInfoView, name='api-info'),
    path('docs/', views.APIDocumentationView, name='api-docs'),
    
    # Utility endpoints
    path('utils/validate-email/', views.ValidateEmailView, name='validate-email'),
    path('utils/validate-phone/', views.ValidatePhoneView, name='validate-phone'),
    path('utils/generate-slug/', views.GenerateSlugView, name='generate-slug'),
    
    # Multi-tenant utilities
    path('tenant/switch/', views.SwitchTenantView, name='switch-tenant'),
    path('tenant/info/', views.TenantInfoView, name='tenant-info'),
    
    # Search and filtering utilities
    path('search/', views.GlobalSearchView, name='global-search'),
    path('filter/', views.GlobalFilterView, name='global-filter'),
    
    # Export and import utilities
    path('export/', views.ExportDataView, name='export-data'),
    path('import/', views.ImportDataView, name='import-data'),
    
    # Analytics and reporting
    path('analytics/', views.AnalyticsView, name='analytics'),
    path('reports/', views.ReportsView, name='reports'),
    path('dashboard/', views.DashboardView, name='dashboard'),
] 