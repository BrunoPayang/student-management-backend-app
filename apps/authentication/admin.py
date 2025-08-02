from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'user_type', 'school', 'is_verified', 'is_active'
    ]
    list_filter = [
        'user_type', 'school', 'is_verified', 'is_active',
        'is_staff', 'is_superuser', 'created_at'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Additional Info'), {
            'fields': ('user_type', 'school', 'phone', 'profile_picture', 'fcm_token', 'is_verified')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    inlines = [UserProfileInline]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'language_preference', 'email_notifications', 'push_notifications']
    list_filter = ['language_preference', 'email_notifications', 'sms_notifications', 'push_notifications']
    search_fields = ['user__username', 'user__email']
