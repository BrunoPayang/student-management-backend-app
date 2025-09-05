from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid


class Class(models.Model):
    """
    Class model for school classes/grade levels
    Each school can create and manage their own classes
    """
    # Core identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='classes'
    )
    
    # Class information
    name = models.CharField(max_length=100, help_text="Nom de la classe (ex: 'Grade 1', 'CP', '6ème')")
    level = models.CharField(
        max_length=50,
        help_text="Niveau de classe pour le tri (ex: '1', '2', '3')"
    )
    section = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Section dans la classe (ex: 'A', 'B', 'Science', 'Arts')"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description optionnelle de la classe"
    )
    
    # Academic settings
    academic_year = models.CharField(
        max_length=20,
        help_text="Année académique de cette classe (ex: '2024-2025')"
    )
    max_students = models.PositiveIntegerField(
        default=30,
        help_text="Nombre maximum d'étudiants autorisés dans cette classe"
    )
    
    # Status and metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        unique_together = ['school', 'name', 'section', 'academic_year']
        ordering = ['level', 'name', 'section']
    
    def __str__(self):
        if self.section:
            return f"{self.name} - {self.section} ({self.school.name})"
        return f"{self.name} ({self.school.name})"
    
    @property
    def full_name(self):
        """Return full class name with section if available"""
        if self.section:
            return f"{self.name} - {self.section}"
        return self.name
    
    @property
    def student_count(self):
        """Return number of students currently in this class"""
        return self.students.filter(is_active=True).count()
    
    @property
    def available_spots(self):
        """Return number of available spots in this class"""
        return max(0, self.max_students - self.student_count)


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
        help_text="Numéro d'identification spécifique à l'école"
    )
    
    # Academic information
    class_assigned = models.ForeignKey(
        'Class',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        help_text="Classe assignée à cet étudiant"
    )
    
    # Personal details
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'Masculin'),
            ('female', 'Féminin'),
            ('other', 'Autre')
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
        verbose_name = 'Étudiant'
        verbose_name_plural = 'Étudiants'
        unique_together = ['school', 'student_id']
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['school', 'is_active']),
            models.Index(fields=['class_assigned']),
            models.Index(fields=['enrollment_date']),
            models.Index(fields=['date_of_birth']),
            models.Index(fields=['gender']),
            models.Index(fields=['school', 'class_assigned', 'is_active'])
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
            ('father', 'Père'),
            ('mother', 'Mère'),
            ('guardian', 'Tuteur'),
            ('grandfather', 'Grand-père'),
            ('grandmother', 'Grand-mère'),
            ('uncle', 'Oncle'),
            ('aunt', 'Tante'),
            ('other', 'Autre')
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
        verbose_name = 'Relation Parent-Étudiant'
        verbose_name_plural = 'Relations Parent-Étudiant'
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
            ('first', 'Premier Semestre'),
            ('second', 'Deuxième Semestre'),
            
            ('annual', 'Rapport Annuel')
        ]
    )
    
    # File information
    file_url = models.URLField(help_text="Firebase Storage URL")
    file_name = models.CharField(max_length=255)
    
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
        verbose_name = 'Relevé de Notes'
        verbose_name_plural = 'Relevés de Notes'
        unique_together = ['student', 'academic_year', 'semester']
        ordering = ['-academic_year', '-semester']
        indexes = [
            models.Index(fields=['student', 'academic_year']),
            models.Index(fields=['uploaded_by', 'created_at'])
        ]
    
    def __str__(self):
        return f"{self.student.full_name} - {self.academic_year} {self.semester}"
    


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
            ('positive', 'Comportement Positif'),
            ('negative', 'Comportement Négatif'),
            ('neutral', 'Observation Générale'),
            ('achievement', 'Réussite'),
            ('discipline', 'Mesure Disciplinaire')
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
            ('low', 'Faible'),
            ('medium', 'Moyen'),
            ('high', 'Élevé'),
            ('critical', 'Critique')
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
        verbose_name = 'Rapport de Comportement'
        verbose_name_plural = 'Rapports de Comportement'
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
            ('tuition', 'Frais de Scolarité'),
            ('library', 'Frais de Bibliothèque'),
            ('laboratory', 'Frais de Laboratoire'),
            ('sports', 'Frais de Sport'),
            ('transport', 'Frais de Transport'),
            ('meal', 'Frais de Repas'),
            ('uniform', 'Frais d\'Uniforme'),
            ('examination', 'Frais d\'Examen'),
            ('other', 'Autre')
        ]
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'En Attente'),
            ('paid', 'Payé'),
            ('overdue', 'En Retard'),
            ('cancelled', 'Annulé'),
            ('refunded', 'Remboursé')
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
            ('cash', 'Espèces'),
            ('bank_transfer', 'Virement Bancaire'),
            ('card', 'Carte de Crédit/Débit'),
            ('mobile_money', 'Mobile Money'),
            ('check', 'Chèque'),
            ('other', 'Autre')
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
        verbose_name = 'Enregistrement de Paiement'
        verbose_name_plural = 'Enregistrements de Paiement'
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
