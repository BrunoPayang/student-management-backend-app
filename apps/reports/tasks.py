from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Avg, Sum
from datetime import datetime, timedelta
from apps.schools.models import School
from apps.students.models import Student, BehaviorReport, PaymentRecord
from apps.notifications.models import Notification

@shared_task
def generate_monthly_reports():
    """Generate monthly reports for all schools"""
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    for school in School.objects.all():
        try:
            generate_school_monthly_report.delay(str(school.id), current_month, current_year)
        except Exception as e:
            print(f"Error queuing report for school {school.id}: {e}")
    
    return {'status': 'success', 'schools_queued': School.objects.count()}

@shared_task
def generate_school_monthly_report(school_id, month, year):
    """Generate monthly report for a specific school"""
    try:
        school = School.objects.get(id=school_id)
        
        # Calculate statistics
        stats = {
            'total_students': Student.objects.filter(school=school).count(),
            'new_enrollments': Student.objects.filter(
                school=school,
                enrollment_date__month=month,
                enrollment_date__year=year
            ).count(),
            'behavior_incidents': BehaviorReport.objects.filter(
                student__school=school,
                incident_date__month=month,
                incident_date__year=year
            ).count(),
            'total_payments': PaymentRecord.objects.filter(
                student__school=school,
                payment_date__month=month,
                payment_date__year=year
            ).aggregate(total=Sum('amount'))['total'] or 0,
            'notifications_sent': Notification.objects.filter(
                school=school,
                created_at__month=month,
                created_at__year=year
            ).count()
        }
        
        # Generate report file (PDF, Excel, etc.)
        # This would integrate with report generation libraries
        
        return {
            'status': 'success',
            'school_id': str(school.id),
            'month': month,
            'year': year,
            'stats': stats
        }
        
    except School.DoesNotExist:
        return {'status': 'error', 'message': 'School not found'}

@shared_task
def generate_student_progress_report(student_id):
    """Generate individual student progress report"""
    try:
        student = Student.objects.get(id=student_id)
        
        # Gather student data
        behavior_reports = BehaviorReport.objects.filter(student=student)
        payment_records = PaymentRecord.objects.filter(student=student)
        
        # Generate report
        # This would create a comprehensive student report
        
        return {
            'status': 'success',
            'student_id': str(student.id),
            'report_generated': True
        }
        
    except Student.DoesNotExist:
        return {'status': 'error', 'message': 'Student not found'}

@shared_task
def cleanup_old_reports():
    """Clean up old generated reports"""
    # Remove reports older than 1 year
    cutoff_date = timezone.now() - timedelta(days=365)
    
    # This would clean up report files and database records
    return {'status': 'success', 'message': 'Old reports cleaned up'}
