from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParentDashboardViewSet, ParentStudentViewSet
from apps.authentication.views import ParentListView

app_name = 'parents'

router = DefaultRouter()
router.register(r'parent-dashboard', ParentDashboardViewSet, basename='parent-dashboard')
router.register(r'parent-students', ParentStudentViewSet, basename='parent-student')

urlpatterns = [
    # Main dashboard list endpoint (redirects to my_children)
    path('parent-dashboard/', ParentDashboardViewSet.as_view({'get': 'my_children'}), name='parent-dashboard-list'),
    
    path('', include(router.urls)),
    
    # Parent management (for school staff) - placed after router to avoid conflicts
    path('parents/', ParentListView.as_view(), name='parent_list'),
] 