from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    USER_TYPES = [
        ('admin', 'System Admin'),
        ('school_staff', 'School Staff'),
        ('parent', 'Parent/Guardian'),
    ]
    
    # Additional fields
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPES,
        default='parent'
    )
    
    # School relationship (nullable for system admins)
    school = models.ForeignKey(
        'schools.School', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='users'
    )
    
    # Contact information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{8,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True,
        help_text="Phone number for SMS notifications"
    )
    
    # Firebase Cloud Messaging token for push notifications
    fcm_token = models.TextField(
        blank=True,
        help_text="Firebase Cloud Messaging token for push notifications"
    )
    
    # Profile fields
    profile_picture = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def is_system_admin(self):
        return self.user_type == 'admin'
    
    def is_school_staff(self):
        return self.user_type == 'school_staff'
    
    def is_parent(self):
        return self.user_type == 'parent'
    
    def get_school_context(self):
        """Return school context for multi-tenant operations"""
        if self.school:
            return {
                'school_id': self.school.id,
                'school_slug': self.school.slug,
                'school_name': self.school.name
            }
        return None


class UserProfile(models.Model):
    """
    Extended profile information for users
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Additional contact information
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=17, blank=True)
    
    # Preferences
    language_preference = models.CharField(
        max_length=10,
        choices=[
            ('en', 'English'),
            ('fr', 'French'),
            ('ha', 'Hausa'),
        ],
        default='fr'
    )
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"


# Signal to create user profile automatically
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
