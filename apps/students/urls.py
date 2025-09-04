from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet, ParentStudentViewSet,
    TranscriptViewSet, BehaviorReportViewSet, PaymentRecordViewSet
)

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'parent-students', ParentStudentViewSet, basename='parent-student')
router.register(r'transcripts', TranscriptViewSet, basename='transcript')
router.register(r'behavior-reports', BehaviorReportViewSet, basename='behavior-report')
router.register(r'payment-records', PaymentRecordViewSet, basename='payment-record')

urlpatterns = [
    path('', include(router.urls)),
] 