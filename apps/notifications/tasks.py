from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, NotificationDelivery
from .services import NotificationService
from .fcm_service import FCMService

@shared_task(bind=True, max_retries=3)
def send_notification_task(self, notification_id):
    """Send notification asynchronously"""
    try:
        notification = Notification.objects.get(id=notification_id)
        service = NotificationService()
        results = service.send_notification(notification)
        
        # Update notification status
        notification.sent_via_fcm = results['fcm_sent'] > 0
        notification.sent_via_email = results['email_sent'] > 0
        notification.sent_at = timezone.now()
        notification.save()
        
        return results
        
    except Notification.DoesNotExist:
        raise self.retry(countdown=60, max_retries=3)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60, max_retries=3)

@shared_task
def send_bulk_notification_task(user_ids, title, body, notification_type, school_id, data=None):
    """Send bulk notifications asynchronously"""
    from apps.authentication.models import User
    from apps.schools.models import School
    
    try:
        school = School.objects.get(id=school_id)
        users = User.objects.filter(id__in=user_ids, school=school)
        
        # Create notification
        notification = Notification.objects.create(
            school=school,
            title=title,
            body=body,
            notification_type=notification_type,
            data=data or {}
        )
        
        # Add target users
        notification.target_users.set(users)
        
        # Send asynchronously
        send_notification_task.delay(str(notification.id))
        
        return {
            'notification_id': str(notification.id),
            'target_users': len(users),
            'status': 'queued'
        }
        
    except Exception as e:
        return {'error': str(e), 'status': 'failed'}

@shared_task
def retry_failed_deliveries():
    """Retry failed notification deliveries"""
    failed_deliveries = NotificationDelivery.objects.filter(
        delivered_via_fcm=False,
        delivered_via_email=False,
        fcm_error__isnull=False
    )
    
    for delivery in failed_deliveries:
        try:
            # Retry FCM delivery
            if delivery.notification.sent_via_fcm:
                fcm_service = FCMService()
                success = fcm_service.send_to_token(
                    delivery.user.fcm_token,
                    delivery.notification.title,
                    delivery.notification.body,
                    delivery.notification.data
                )
                
                if success:
                    delivery.delivered_via_fcm = True
                    delivery.fcm_error = ''
                    delivery.delivered_at = timezone.now()
                    delivery.save()
                    
        except Exception as e:
            delivery.fcm_error = str(e)
            delivery.save()
    
    return {'retried_count': failed_deliveries.count()}
