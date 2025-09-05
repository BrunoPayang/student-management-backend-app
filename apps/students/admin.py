from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Class, Student, ParentStudent, Transcript, BehaviorReport, PaymentRecord


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'school', 'academic_year', 'level', 
        'student_count', 'max_students', 'is_active'
    ]
    list_filter = [
        'school', 'academic_year', 'level', 'is_active'
    ]
    search_fields = [
        'name', 'section', 'description', 'school__name'
    ]
    readonly_fields = ['id', 'student_count', 'available_spots', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de Base', {
            'fields': ('school', 'name', 'level', 'section', 'description')
        }),
        ('Paramètres Académiques', {
            'fields': ('academic_year', 'max_students')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Statistiques', {
            'fields': ('student_count', 'available_spots'),
            'classes': ('collapse',)
        }),
        ('Horodatage', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('school')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'student_id', 'school', 'class_assigned', 
        'gender', 'is_active', 'enrollment_date'
    ]
    list_filter = [
        'school', 'is_active', 'gender', 'class_assigned', 
        'enrollment_date', 'is_graduated'
    ]
    search_fields = [
        'first_name', 'last_name', 'student_id', 
        'email', 'phone'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de Base', {
            'fields': ('school', 'first_name', 'last_name', 'middle_name', 'student_id')
        }),
        ('Informations Académiques', {
            'fields': ('class_assigned', 'enrollment_date', 'graduation_date')
        }),
        ('Informations Personnelles', {
            'fields': ('date_of_birth', 'gender', 'blood_group')
        }),
        ('Informations de Contact', {
            'fields': ('email', 'phone', 'emergency_contact')
        }),
        ('Adresse', {
            'fields': ('address', 'city', 'state')
        }),
        ('Informations Médicales', {
            'fields': ('medical_conditions',),
            'classes': ('collapse',)
        }),
        ('Statut', {
            'fields': ('is_active', 'is_graduated', 'profile_picture')
        }),
        ('Horodatage', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Nom Complet'
    
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
    student_name.short_description = 'Étudiant'


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
    student_name.short_description = 'Étudiant'


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
    student_name.short_description = 'Étudiant'


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
    student_name.short_description = 'Étudiant'
