from django.db import models
from django.utils.text import slugify
from django.core.validators import RegexValidator
import uuid


class School(models.Model):
    """
    School model for multi-tenant architecture
    Each school is a separate tenant with isolated data
    """
    # Core identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text="Full school name")
    slug = models.SlugField(
        unique=True, 
        max_length=100,
        help_text="URL-friendly identifier for the school"
    )
    
    # Branding and appearance
    logo = models.URLField(
        blank=True, 
        null=True,
        help_text="Firebase Storage URL for school logo"
    )
    primary_color = models.CharField(
        max_length=7, 
        default="#1976D2",
        help_text="Primary brand color in hex format (e.g., #1976D2)"
    )
    secondary_color = models.CharField(
        max_length=7, 
        default="#424242",
        help_text="Secondary brand color in hex format"
    )
    
    # Contact information
    contact_email = models.EmailField(help_text="Primary contact email")
    contact_phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{8,15}$',
                message="Phone number must be entered in the format: '+999999999'"
            )
        ],
        help_text="Primary contact phone number"
    )
    website = models.URLField(blank=True, null=True)
    
    # Location
    address = models.TextField(help_text="Full school address")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Niger")
    postal_code = models.CharField(max_length=20, blank=True)
    
    # School details
    school_type = models.CharField(
        max_length=50,
        choices=[
            ('primary', 'Primary School'),
            ('secondary', 'Secondary School'),
            ('both', 'Primary & Secondary'),
            ('university', 'University'),
            ('other', 'Other')
        ],
        default='both'
    )
    academic_year = models.CharField(
        max_length=20,
        default="2024-2025",
        help_text="Current academic year"
    )
    
    # Status and timestamps
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'schools_school'
        verbose_name = 'School'
        verbose_name_plural = 'Schools'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'is_verified']),
            models.Index(fields=['city', 'state']),
            models.Index(fields=['created_at'])
        ]
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided, handling duplicates"""
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            
            # Check if slug exists and generate unique one
            while School.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        super().save(*args, **kwargs)
    
    @property
    def full_address(self):
        """Return formatted full address"""
        parts = [self.address, self.city, self.state, self.country]
        return ", ".join(filter(None, parts))
    
    def get_student_count(self):
        """Return active student count"""
        return self.students.filter(is_active=True).count()
    
    def get_staff_count(self):
        """Return active staff count"""
        return self.users.filter(user_type='school_staff', is_active=True).count()
    
    def get_parent_count(self):
        """Return active parent count"""
        return self.users.filter(user_type='parent', is_active=True).count()


class SchoolConfiguration(models.Model):
    """
    School-specific configuration settings
    """
    school = models.OneToOneField(
        School, 
        on_delete=models.CASCADE,
        related_name='configuration'
    )
    
    # Academic settings
    academic_year_start = models.DateField(help_text="Start date of academic year")
    academic_year_end = models.DateField(help_text="End date of academic year")
    current_semester = models.CharField(
        max_length=20,
        choices=[
            ('first', 'First Semester'),
            ('second', 'Second Semester'),
            ('summer', 'Summer Session')
        ],
        default='first'
    )
    
    # Notification settings
    enable_sms_notifications = models.BooleanField(default=True)
    enable_email_notifications = models.BooleanField(default=True)
    enable_push_notifications = models.BooleanField(default=True)
    
    # Payment settings
    currency = models.CharField(max_length=3, default="NGN")
    payment_reminder_days = models.IntegerField(default=7)
    
    # File upload settings
    max_file_size_mb = models.IntegerField(default=10)
    allowed_file_types = models.JSONField(
        default=list,
        help_text="List of allowed file extensions"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'schools_school_configuration'
        verbose_name = 'School Configuration'
        verbose_name_plural = 'School Configurations'
    
    def __str__(self):
        return f"Configuration for {self.school.name}"
    
    def get_allowed_file_types(self):
        """Return list of allowed file extensions"""
        if not self.allowed_file_types:
            return ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
        return self.allowed_file_types
