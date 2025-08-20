from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, NotificationDelivery
from .fcm_service import FCMService

class NotificationService:
    def __init__(self):
        self.fcm_service = FCMService()
    
    def send_notification(self, notification: Notification) -> dict:
        results = {
            'fcm_sent': 0,
            'email_sent': 0,
            'sms_sent': 0,
            'total_targets': notification.target_users.count()
        }
        
        for user in notification.target_users.all():
            delivery, created = NotificationDelivery.objects.get_or_create(
                notification=notification,
                user=user
            )
            
            # Send via FCM
            if user.fcm_token and getattr(user.profile, 'push_notifications', True):
                fcm_success = self._send_fcm_to_user(user, notification)
                if fcm_success:
                    delivery.delivered_via_fcm = True
                    results['fcm_sent'] += 1
            
            # Send via email
            if user.email and getattr(user.profile, 'email_notifications', True):
                email_success = self._send_email_to_user(user, notification)
                if email_success:
                    delivery.delivered_via_email = True
                    results['email_sent'] += 1
            
            # Send via SMS (if configured)
            if user.phone and getattr(user.profile, 'sms_notifications', True):
                sms_success = self._send_sms_to_user(user, notification)
                if sms_success:
                    delivery.delivered_via_sms = True
                    results['sms_sent'] = results.get('sms_sent', 0) + 1
            
            delivery.delivered_at = timezone.now()
            delivery.save()
        
        notification.sent_via_fcm = results['fcm_sent'] > 0
        notification.sent_via_email = results['email_sent'] > 0
        notification.sent_via_sms = results.get('sms_sent', 0) > 0
        notification.sent_at = timezone.now()
        notification.save()
        
        return results
    
    def _send_fcm_to_user(self, user, notification):
        try:
            data = {
                'notification_id': str(notification.id),
                'type': notification.notification_type,
                'school_id': str(notification.school.id)
            }
            
            return self.fcm_service.send_to_token(
                user.fcm_token,
                notification.title,
                notification.body,
                data
            )
        except Exception as e:
            print(f"FCM send error for user {user.id}: {e}")
            return False
    
    def _send_email_to_user(self, user, notification):
        try:
            subject = f"[{notification.school.name}] {notification.title}"
            body = f"{notification.body}\n\nSent: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )
            return True
        except Exception as e:
            print(f"Email send error for user {user.id}: {e}")
            return False
    
    def _send_sms_to_user(self, user, notification):
        """Send SMS notification to user"""
        try:
            # This would integrate with an SMS service provider
            # For now, we'll just log the attempt
            message = f"[{notification.school.name}] {notification.title}: {notification.body}"
            print(f"SMS would be sent to {user.phone}: {message}")
            
            # In production, you would use a service like Twilio, AWS SNS, etc.
            # Example with Twilio:
            # from twilio.rest import Client
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(
            #     body=message,
            #     from_=settings.TWILIO_PHONE_NUMBER,
            #     to=user.phone
            # )
            
            return True
        except Exception as e:
            print(f"SMS send error for user {user.id}: {e}")
            return False
    
    def send_bulk_notification(self, users: list, title: str, body: str, 
                              notification_type: str, school, data: dict = None) -> dict:
        """Send bulk notification to multiple users"""
        # Create notification record
        notification = Notification.objects.create(
            school=school,
            title=title,
            body=body,
            notification_type=notification_type,
            data=data or {}
        )
        
        # Add target users
        notification.target_users.set(users)
        
        # Send notifications
        return self.send_notification(notification)
