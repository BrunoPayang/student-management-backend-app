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
