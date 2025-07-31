from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    # Health check and system status
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    path('status/', views.SystemStatusView.as_view(), name='system-status'),
    
    # API documentation and info
    path('api-info/', views.APIInfoView.as_view(), name='api-info'),
    path('docs/', views.APIDocumentationView.as_view(), name='api-docs'),
    
    # Utility endpoints
    path('utils/validate-email/', views.ValidateEmailView.as_view(), name='validate-email'),
    path('utils/validate-phone/', views.ValidatePhoneView.as_view(), name='validate-phone'),
    path('utils/generate-slug/', views.GenerateSlugView.as_view(), name='generate-slug'),
    
    # Multi-tenant utilities
    path('tenant/switch/', views.SwitchTenantView.as_view(), name='switch-tenant'),
    path('tenant/info/', views.TenantInfoView.as_view(), name='tenant-info'),
    
    # Search and filtering utilities
    path('search/', views.GlobalSearchView.as_view(), name='global-search'),
    path('filter/', views.GlobalFilterView.as_view(), name='global-filter'),
    
    # Export and import utilities
    path('export/', views.ExportDataView.as_view(), name='export-data'),
    path('import/', views.ImportDataView.as_view(), name='import-data'),
    
    # Analytics and reporting
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
] 