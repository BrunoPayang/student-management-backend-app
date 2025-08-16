# Phase 3: Core Models & Database (Week 1 - Days 5-7)

## Overview
Implement the core database models for multi-tenant school management system, including School, Student, Parent relationships, and academic records with proper data isolation and validation.

## Task 3.1: School Management Models

### Step 1: Create School Model
**apps/schools/models.py**
```python
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
        """Auto-generate slug if not provided"""
        if not self.slug:
            self.slug = slugify(self.name)
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
```

### Step 2: Create School Admin Interface
**apps/schools/admin.py**
```python
from django.contrib import admin
from django.utils.html import format_html
from .models import School, SchoolConfiguration


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'school_type', 'city', 'is_active', 
        'is_verified', 'created_at', 'student_count', 'staff_count'
    ]
    list_filter = ['is_active', 'is_verified', 'school_type', 'city', 'state']
    search_fields = ['name', 'contact_email', 'address']
    readonly_fields = ['id', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'school_type', 'academic_year')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'website')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Branding', {
            'fields': ('logo', 'primary_color', 'secondary_color')
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def student_count(self, obj):
        return obj.get_student_count()
    student_count.short_description = 'Students'
    
    def staff_count(self, obj):
        return obj.get_staff_count()
    staff_count.short_description = 'Staff'


@admin.register(SchoolConfiguration)
class SchoolConfigurationAdmin(admin.ModelAdmin):
    list_display = ['school', 'current_semester', 'currency', 'created_at']
    list_filter = ['current_semester', 'currency']
    search_fields = ['school__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Academic Settings', {
            'fields': ('academic_year_start', 'academic_year_end', 'current_semester')
        }),
        ('Notification Settings', {
            'fields': ('enable_sms_notifications', 'enable_email_notifications', 'enable_push_notifications')
        }),
        ('Payment Settings', {
            'fields': ('currency', 'payment_reminder_days')
        }),
        ('File Upload Settings', {
            'fields': ('max_file_size_mb', 'allowed_file_types')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
```

## Task 3.2: Student & Relationship Models

### Step 1: Create Student Model
**apps/students/models.py**
```python
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid


class Student(models.Model):
    """
    Student model with school-specific data isolation
    """
    # Core identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='students'
    )
    
    # Personal information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    
    # School-specific student ID
    student_id = models.CharField(
        max_length=50,
        help_text="School-specific student identification number"
    )
    
    # Academic information
    class_level = models.CharField(
        max_length=50,
        help_text="Current class/grade level (e.g., 'Class 6A', 'Grade 10')"
    )
    section = models.CharField(
        max_length=20,
        blank=True,
        help_text="Class section (e.g., 'A', 'B', 'Science')"
    )
    
    # Personal details
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other')
        ]
    )
    
    # Contact information
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{8,15}$',
                message="Phone number must be entered in the format: '+999999999'"
            )
        ],
        blank=True
    )
    
    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    
    # Academic status
    enrollment_date = models.DateField(default=timezone.now)
    graduation_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_graduated = models.BooleanField(default=False)
    
    # Additional information
    blood_group = models.CharField(
        max_length=5,
        blank=True,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-')
        ]
    )
    emergency_contact = models.CharField(max_length=20, blank=True)
    medical_conditions = models.TextField(blank=True)
    
    # Profile
    profile_picture = models.URLField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'students_student'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        unique_together = ['school', 'student_id']
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['school', 'is_active']),
            models.Index(fields=['class_level']),
            models.Index(fields=['enrollment_date']),
            models.Index(fields=['date_of_birth']),
            models.Index(fields=['gender']),
            models.Index(fields=['school', 'class_level', 'is_active'])
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"
    
    @property
    def full_name(self):
        """Return full name with middle name if available"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calculate current age"""
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def get_parents(self):
        """Return all parents/guardians"""
        return self.parents.all()
    
    def get_primary_parent(self):
        """Return primary parent/guardian"""
        return self.parents.filter(is_primary=True).first()
    
    def get_academic_records(self):
        """Return all academic records"""
        return self.transcripts.all()
    
    def get_behavior_reports(self):
        """Return all behavior reports"""
        return self.behavior_reports.all()
    
    def get_payment_records(self):
        """Return all payment records"""
        return self.payment_records.all()


class ParentStudent(models.Model):
    """
    Many-to-many relationship between parents and students
    """
    parent = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='student_relationships'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='parents'
    )
    
    # Relationship details
    relationship = models.CharField(
        max_length=50,
        choices=[
            ('father', 'Father'),
            ('mother', 'Mother'),
            ('guardian', 'Guardian'),
            ('grandfather', 'Grandfather'),
            ('grandmother', 'Grandmother'),
            ('uncle', 'Uncle'),
            ('aunt', 'Aunt'),
            ('other', 'Other')
        ]
    )
    
    # Primary contact status
    is_primary = models.BooleanField(
        default=False,
        help_text="Primary contact for school communications"
    )
    is_emergency_contact = models.BooleanField(
        default=False,
        help_text="Emergency contact for the student"
    )
    
    # Communication preferences
    receive_sms = models.BooleanField(default=True)
    receive_email = models.BooleanField(default=True)
    receive_push = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'students_parent_student'
        verbose_name = 'Parent-Student Relationship'
        verbose_name_plural = 'Parent-Student Relationships'
        unique_together = ['parent', 'student']
        indexes = [
            models.Index(fields=['parent', 'is_primary']),
            models.Index(fields=['student', 'is_primary'])
        ]
    
    def __str__(self):
        return f"{self.parent.full_name} - {self.student.full_name} ({self.get_relationship_display()})"
    
    def save(self, *args, **kwargs):
        """Ensure only one primary contact per student"""
        if self.is_primary:
            # Set all other relationships for this student as non-primary
            ParentStudent.objects.filter(
                student=self.student,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
```

### Step 2: Create Academic Record Models
**apps/students/models.py** (continued)
```python
class Transcript(models.Model):
    """
    Academic transcript/grade records
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='transcripts'
    )
    
    # Academic period
    academic_year = models.CharField(max_length=20)
    semester = models.CharField(
        max_length=20,
        choices=[
            ('first', 'First Semester'),
            ('second', 'Second Semester'),
            ('summer', 'Summer Session'),
            ('annual', 'Annual Report')
        ]
    )
    
    # File information
    file_url = models.URLField(help_text="Firebase Storage URL")
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text="File size in bytes")
    
    # Academic details
    gpa = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Grade Point Average"
    )
    total_credits = models.IntegerField(blank=True, null=True)
    rank_in_class = models.IntegerField(blank=True, null=True)
    class_size = models.IntegerField(blank=True, null=True)
    
    # Upload information
    uploaded_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='uploaded_transcripts'
    )
    
    # Status
    is_public = models.BooleanField(
        default=False,
        help_text="Visible to parents"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'students_transcript'
        verbose_name = 'Transcript'
        verbose_name_plural = 'Transcripts'
        unique_together = ['student', 'academic_year', 'semester']
        ordering = ['-academic_year', '-semester']
        indexes = [
            models.Index(fields=['student', 'academic_year']),
            models.Index(fields=['uploaded_by', 'created_at'])
        ]
    
    def __str__(self):
        return f"{self.student.full_name} - {self.academic_year} {self.semester}"
    
    @property
    def file_size_mb(self):
        """Return file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)


class BehaviorReport(models.Model):
    """
    Student behavior and conduct reports
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='behavior_reports'
    )
    
    # Report details
    report_type = models.CharField(
        max_length=50,
        choices=[
            ('positive', 'Positive Behavior'),
            ('negative', 'Negative Behavior'),
            ('neutral', 'General Observation'),
            ('achievement', 'Achievement'),
            ('discipline', 'Disciplinary Action')
        ]
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Location and context
    location = models.CharField(max_length=100, blank=True)
    incident_date = models.DateField()
    incident_time = models.TimeField(blank=True, null=True)
    
    # Severity and impact
    severity_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical')
        ],
        default='medium'
    )
    
    # Actions taken
    actions_taken = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(blank=True, null=True)
    
    # Reporting
    reported_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='reported_behaviors'
    )
    
    # Visibility
    notify_parents = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'students_behavior_report'
        verbose_name = 'Behavior Report'
        verbose_name_plural = 'Behavior Reports'
        ordering = ['-incident_date', '-created_at']
        indexes = [
            models.Index(fields=['student', 'report_type']),
            models.Index(fields=['reported_by', 'created_at']),
            models.Index(fields=['incident_date'])
        ]
    
    def __str__(self):
        return f"{self.student.full_name} - {self.title} ({self.get_report_type_display()})"


class PaymentRecord(models.Model):
    """
    Student payment and fee records
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='payment_records'
    )
    
    # Payment details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Payment amount"
    )
    currency = models.CharField(max_length=3, default="NGN")
    
    payment_type = models.CharField(
        max_length=50,
        choices=[
            ('tuition', 'Tuition Fee'),
            ('library', 'Library Fee'),
            ('laboratory', 'Laboratory Fee'),
            ('sports', 'Sports Fee'),
            ('transport', 'Transport Fee'),
            ('meal', 'Meal Fee'),
            ('uniform', 'Uniform Fee'),
            ('examination', 'Examination Fee'),
            ('other', 'Other')
        ]
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('overdue', 'Overdue'),
            ('cancelled', 'Cancelled'),
            ('refunded', 'Refunded')
        ],
        default='pending'
    )
    
    # Dates
    due_date = models.DateField()
    paid_date = models.DateField(blank=True, null=True)
    
    # Payment method
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('cash', 'Cash'),
            ('bank_transfer', 'Bank Transfer'),
            ('card', 'Credit/Debit Card'),
            ('mobile_money', 'Mobile Money'),
            ('check', 'Check'),
            ('other', 'Other')
        ]
    )
    
    # Reference information
    reference_number = models.CharField(max_length=100, blank=True)
    receipt_url = models.URLField(blank=True, null=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Created by
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='created_payments'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'students_payment_record'
        verbose_name = 'Payment Record'
        verbose_name_plural = 'Payment Records'
        ordering = ['-due_date', '-created_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['payment_type'])
        ]
    
    def __str__(self):
        return f"{self.student.full_name} - {self.payment_type} ({self.amount} {self.currency})"
    
    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        from django.utils import timezone
        return self.status == 'pending' and self.due_date < timezone.now().date()
    
    @property
    def days_overdue(self):
        """Calculate days overdue"""
        from django.utils import timezone
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0
```

### Step 3: Create Student Admin Interface
**apps/students/admin.py**
```python
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Student, ParentStudent, Transcript, BehaviorReport, PaymentRecord


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'student_id', 'school', 'class_level', 
        'gender', 'is_active', 'enrollment_date'
    ]
    list_filter = [
        'school', 'is_active', 'gender', 'class_level', 
        'enrollment_date', 'is_graduated'
    ]
    search_fields = [
        'first_name', 'last_name', 'student_id', 
        'email', 'phone'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('school', 'first_name', 'last_name', 'middle_name', 'student_id')
        }),
        ('Academic Information', {
            'fields': ('class_level', 'section', 'enrollment_date', 'graduation_date')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'gender', 'blood_group')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'emergency_contact')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state')
        }),
        ('Medical Information', {
            'fields': ('medical_conditions',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_graduated', 'profile_picture')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('school')


@admin.register(ParentStudent)
class ParentStudentAdmin(admin.ModelAdmin):
    list_display = [
        'parent_name', 'student_name', 'relationship', 
        'is_primary', 'is_emergency_contact'
    ]
    list_filter = [
        'relationship', 'is_primary', 'is_emergency_contact',
        'receive_sms', 'receive_email', 'receive_push'
    ]
    search_fields = [
        'parent__first_name', 'parent__last_name',
        'student__first_name', 'student__last_name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    def parent_name(self, obj):
        return obj.parent.full_name
    parent_name.short_description = 'Parent'
    
    def student_name(self, obj):
        return obj.student.full_name
    student_name.short_description = 'Student'


@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'academic_year', 'semester', 
        'gpa', 'is_public', 'uploaded_by'
    ]
    list_filter = [
        'academic_year', 'semester', 'is_public',
        'uploaded_by__user_type'
    ]
    search_fields = [
        'student__first_name', 'student__last_name',
        'student__student_id'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    def student_name(self, obj):
        return obj.student.full_name
    student_name.short_description = 'Student'


@admin.register(BehaviorReport)
class BehaviorReportAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'report_type', 'title', 
        'severity_level', 'incident_date', 'reported_by'
    ]
    list_filter = [
        'report_type', 'severity_level', 'incident_date',
        'notify_parents', 'is_public'
    ]
    search_fields = [
        'student__first_name', 'student__last_name',
        'title', 'description'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    def student_name(self, obj):
        return obj.student.full_name
    student_name.short_description = 'Student'


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'payment_type', 'amount', 
        'currency', 'status', 'due_date', 'paid_date'
    ]
    list_filter = [
        'payment_type', 'status', 'currency',
        'payment_method', 'due_date'
    ]
    search_fields = [
        'student__first_name', 'student__last_name',
        'reference_number', 'notes'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    def student_name(self, obj):
        return obj.student.full_name
    student_name.short_description = 'Student'
```

## Task 3.3: Database Migrations & Seeding

### Step 1: Create and Run Migrations
```bash
# Create migrations for all apps
python manage.py makemigrations authentication
python manage.py makemigrations schools
python manage.py makemigrations students
python manage.py makemigrations parents
python manage.py makemigrations notifications
python manage.py makemigrations files
python manage.py makemigrations common

# Run migrations
python manage.py migrate
```

### Step 2: Create Management Commands for Data Seeding
**apps/schools/management/commands/seed_schools.py**
```python
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.schools.models import School, SchoolConfiguration
from apps.authentication.models import User
import random


class Command(BaseCommand):
    help = 'Seed sample schools for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of schools to create'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Sample school data
        schools_data = [
            {
                'name': 'École Primaire Publique de Niamey',
                'school_type': 'primary',
                'city': 'Niamey',
                'state': 'Niamey',
                'contact_email': 'contact@epp-niamey.ne',
                'contact_phone': '+22790123456',
                'address': 'Quartier Plateau, Niamey, Niger'
            },
            {
                'name': 'Lycée Technique National',
                'school_type': 'secondary',
                'city': 'Niamey',
                'state': 'Niamey',
                'contact_email': 'info@ltn-niamey.ne',
                'contact_phone': '+22790123457',
                'address': 'Zone Industrielle, Niamey, Niger'
            },
            {
                'name': 'Collège Privé Sainte Marie',
                'school_type': 'both',
                'city': 'Maradi',
                'state': 'Maradi',
                'contact_email': 'admin@cpsm-maradi.ne',
                'contact_phone': '+22790123458',
                'address': 'Centre-ville, Maradi, Niger'
            },
            {
                'name': 'École Secondaire de Zinder',
                'school_type': 'secondary',
                'city': 'Zinder',
                'state': 'Zinder',
                'contact_email': 'contact@esz-zinder.ne',
                'contact_phone': '+22790123459',
                'address': 'Quartier Birni, Zinder, Niger'
            },
            {
                'name': 'Institut Supérieur de Formation',
                'school_type': 'university',
                'city': 'Agadez',
                'state': 'Agadez',
                'contact_email': 'info@isf-agadez.ne',
                'contact_phone': '+22790123460',
                'address': 'Campus Universitaire, Agadez, Niger'
            }
        ]
        
        created_schools = []
        
        for i, school_data in enumerate(schools_data[:count]):
            school = School.objects.create(
                name=school_data['name'],
                school_type=school_data['school_type'],
                city=school_data['city'],
                state=school_data['state'],
                contact_email=school_data['contact_email'],
                contact_phone=school_data['contact_phone'],
                address=school_data['address'],
                is_verified=True
            )
            
            # Create school configuration
            SchoolConfiguration.objects.create(
                school=school,
                academic_year_start=timezone.now().date().replace(month=9, day=1),
                academic_year_end=timezone.now().date().replace(month=6, day=30),
                current_semester='first',
                currency='NGN',
                payment_reminder_days=7,
                max_file_size_mb=10,
                allowed_file_types=['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            )
            
            created_schools.append(school)
            self.stdout.write(
                self.style.SUCCESS(f'Created school: {school.name}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(created_schools)} schools')
        )
```

**apps/students/management/commands/seed_students.py**
```python
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.schools.models import School
from apps.students.models import Student, ParentStudent
from apps.authentication.models import User
import random
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Seed sample students for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--school-id',
            type=str,
            help='Specific school ID to seed students for'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of students to create per school'
        )

    def handle(self, *args, **options):
        count = options['count']
        school_id = options['school_id']
        
        if school_id:
            schools = School.objects.filter(id=school_id)
        else:
            schools = School.objects.filter(is_active=True)
        
        if not schools.exists():
            self.stdout.write(
                self.style.ERROR('No active schools found')
            )
            return
        
        # Sample names for students
        first_names = [
            'Amina', 'Fatima', 'Hassan', 'Ibrahim', 'Mariam',
            'Omar', 'Zara', 'Yusuf', 'Aisha', 'Mohammed',
            'Khadija', 'Ali', 'Hawa', 'Abdullah', 'Safiya',
            'Ahmed', 'Fadima', 'Moussa', 'Hadjara', 'Boubacar'
        ]
        
        last_names = [
            'Diallo', 'Traore', 'Keita', 'Cisse', 'Konate',
            'Soumaoro', 'Coulibaly', 'Diakite', 'Sidibe', 'Toure',
            'Camara', 'Bah', 'Barry', 'Balde', 'Sylla',
            'Kone', 'Sangare', 'Diarra', 'Fofana', 'Kante'
        ]
        
        class_levels = [
            'Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5',
            'Class 6', 'Form 1', 'Form 2', 'Form 3', 'Form 4',
            'Form 5', 'Form 6'
        ]
        
        created_students = []
        
        for school in schools:
            self.stdout.write(f'Creating students for {school.name}...')
            
            for i in range(count):
                # Generate student data
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                student_id = f"{school.slug.upper()}{random.randint(1000, 9999)}"
                
                # Random birth date (5-18 years old)
                years_old = random.randint(5, 18)
                birth_date = date.today() - timedelta(days=years_old * 365)
                
                # Random enrollment date (within last 3 years)
                enrollment_days_ago = random.randint(0, 1095)
                enrollment_date = date.today() - timedelta(days=enrollment_days_ago)
                
                student = Student.objects.create(
                    school=school,
                    first_name=first_name,
                    last_name=last_name,
                    student_id=student_id,
                    class_level=random.choice(class_levels),
                    date_of_birth=birth_date,
                    gender=random.choice(['male', 'female']),
                    enrollment_date=enrollment_date,
                    is_active=random.choice([True, True, True, False])  # 75% active
                )
                
                created_students.append(student)
                
                if i % 10 == 0:
                    self.stdout.write(f'Created {i+1} students...')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(created_students)} students')
        )
```

### Step 3: Create Database Indexes for Performance
**apps/schools/models.py** (add to School model)
```python
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
```

**apps/students/models.py** (add to Student model)
```python
class Meta:
    db_table = 'students_student'
    verbose_name = 'Student'
    verbose_name_plural = 'Students'
    unique_together = ['school', 'student_id']
    ordering = ['last_name', 'first_name']
    indexes = [
        models.Index(fields=['school', 'is_active']),
        models.Index(fields=['class_level']),
        models.Index(fields=['enrollment_date']),
        models.Index(fields=['date_of_birth']),
        models.Index(fields=['gender']),
        models.Index(fields=['school', 'class_level', 'is_active'])
    ]
```

### Step 4: Run Seeding Commands
```bash
# Seed schools
python manage.py seed_schools --count 5

# Seed students for all schools
python manage.py seed_students --count 30

# Or seed students for specific school
python manage.py seed_students --school-id <school-uuid> --count 50
```

## Validation Checklist

### Database Models
- [ ] School model with all required fields and proper validation
- [ ] SchoolConfiguration model with academic and notification settings
- [ ] Student model with school-specific data isolation
- [ ] ParentStudent relationship model with proper constraints
- [ ] Transcript model for academic records
- [ ] BehaviorReport model for conduct tracking
- [ ] PaymentRecord model for fee management
- [ ] All models have proper indexes for performance
- [ ] Unique constraints are properly defined
- [ ] Foreign key relationships are correctly established

### Admin Interface
- [ ] School admin with proper list display and filters
- [ ] Student admin with search and filtering capabilities
- [ ] ParentStudent admin for relationship management
- [ ] Transcript admin for academic records
- [ ] BehaviorReport admin for conduct tracking
- [ ] PaymentRecord admin for fee management
- [ ] All admin interfaces have proper readonly fields

### Data Seeding
- [ ] Management command for seeding schools
- [ ] Management command for seeding students
- [ ] Sample data is realistic and diverse
- [ ] Seeding commands accept parameters for customization
- [ ] Proper error handling in seeding commands

### Database Performance
- [ ] Indexes created for frequently queried fields
- [ ] Composite indexes for multi-field queries
- [ ] Foreign key indexes for relationship queries
- [ ] Unique constraints properly enforced
- [ ] Database migrations run successfully

### Multi-tenancy
- [ ] School-based data isolation implemented
- [ ] Student data properly linked to schools
- [ ] Parent relationships respect school boundaries
- [ ] Academic records tied to specific schools
- [ ] Payment records isolated by school

## Next Steps
After completing Phase 3, proceed to Phase 4: Core API Endpoints to implement the REST API endpoints for all the models created in this phase. 