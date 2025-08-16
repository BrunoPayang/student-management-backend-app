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
