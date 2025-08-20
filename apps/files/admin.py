from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django import forms
from .models import FileUpload
from .services import FirebaseStorageService

class FileUploadAdminForm(forms.ModelForm):
    """Custom form for FileUpload with file upload handling"""
    
    file = forms.FileField(
        required=False,
        help_text="Upload a file to automatically fill metadata. Leave empty if adding existing file record."
    )
    
    class Meta:
        model = FileUpload
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields optional when uploading new file
        if not self.instance.pk:  # New object
            self.fields['firebase_path'].required = False
            self.fields['firebase_url'].required = False
            self.fields['file_size'].required = False
            self.fields['content_type'].required = False
        else:
            self.fields['file'].help_text = "Upload new file to replace existing one"
    
    def clean(self):
        cleaned_data = super().clean()
        file_obj = cleaned_data.get('file')
        
        if file_obj and not self.instance.pk:  # New upload
            # Validate file
            if file_obj.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError("File size cannot exceed 10MB")
            
            # Set metadata automatically
            cleaned_data['original_name'] = file_obj.name
            cleaned_data['file_size'] = file_obj.size
            cleaned_data['content_type'] = file_obj.content_type
            
            # Generate Firebase path
            if cleaned_data.get('school'):
                school_id = cleaned_data['school'].id
                file_type = cleaned_data.get('file_type', 'other')
                import uuid
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                extension = file_obj.name.split('.')[-1] if '.' in file_obj.name else ''
                filename = f"{timestamp}_{unique_id}.{extension}"
                cleaned_data['firebase_path'] = f"schools/{school_id}/{file_type}/{filename}"
        else:
            # If no file is uploaded, ensure required fields are provided
            if not cleaned_data.get('original_name'):
                raise forms.ValidationError("Original name is required when no file is uploaded")
            
            # Set default values for optional fields if not provided
            if not cleaned_data.get('file_size'):
                cleaned_data['file_size'] = None
            if not cleaned_data.get('content_type'):
                cleaned_data['content_type'] = None
            if not cleaned_data.get('firebase_path'):
                cleaned_data['firebase_path'] = None
            if not cleaned_data.get('firebase_url'):
                cleaned_data['firebase_url'] = None
        
        return cleaned_data

@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    """Admin interface for FileUpload model"""
    
    form = FileUploadAdminForm
    
    list_display = [
        'id', 'original_name', 'file_type', 'school', 'uploaded_by', 
        'file_size_mb', 'uploaded_at', 'is_public', 'is_deleted'
    ]
    
    list_filter = [
        'file_type', 'school', 'is_public', 'is_deleted', 'uploaded_at',
        ('uploaded_by', admin.RelatedOnlyFieldListFilter)
    ]
    
    search_fields = [
        'original_name', 'description', 'tags', 'school__name', 
        'uploaded_by__username', 'uploaded_by__first_name', 'uploaded_by__last_name'
    ]
    
    list_per_page = 25
    
    readonly_fields = [
        'id', 'firebase_path', 'firebase_url', 'file_size', 'content_type',
        'uploaded_at', 'uploaded_by'
    ]
    
    fieldsets = (
        ('File Upload', {
            'fields': ('file',),
            'description': 'Upload a file to automatically fill metadata, or leave empty to add existing file record manually.'
        }),
        ('File Information', {
            'fields': ('id', 'original_name', 'file_type', 'description', 'tags')
        }),
        ('Storage Details', {
            'fields': ('firebase_path', 'firebase_url', 'file_size', 'content_type')
        }),
        ('School & Access', {
            'fields': ('school', 'is_public', 'is_deleted')
        }),
        ('Upload Details', {
            'fields': ('uploaded_by', 'uploaded_at')
        }),
    )
    
    def file_size_mb(self, obj):
        """Display file size in MB"""
        if obj.file_size is None:
            return "N/A"
        return f"{obj.file_size_mb} MB"
    file_size_mb.short_description = 'File Size (MB)'
    
    def get_queryset(self, request):
        """Custom queryset for admin"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif hasattr(request.user, 'school'):
            return qs.filter(school=request.user.school)
        return qs.none()
    
    def has_add_permission(self, request):
        """Allow superusers and school staff to add files"""
        return request.user.is_authenticated and (
            request.user.is_superuser or 
            getattr(request.user, 'user_type', None) in ['admin', 'school_staff']
        )
    
    def has_change_permission(self, request, obj=None):
        """Allow superusers and school staff to edit files"""
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
            
        if obj and hasattr(request.user, 'school'):
            return obj.school == request.user.school
            
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow superusers and school staff to delete files"""
        return self.has_change_permission(request, obj)
    
    def has_view_permission(self, request, obj=None):
        """Allow superusers and school staff to view files"""
        return self.has_change_permission(request, obj)
    
    def get_list_display(self, request):
        """Customize list display based on user permissions"""
        if request.user.is_superuser:
            return self.list_display
        else:
            # Remove school field for non-superusers as they only see their school's files
            return [field for field in self.list_display if field != 'school']
    
    def get_list_filter(self, request):
        """Customize filters based on user permissions"""
        if request.user.is_superuser:
            return self.list_filter
        else:
            # Remove school filter for non-superusers
            return [filter for filter in self.list_filter if not isinstance(filter, str) or filter != 'school']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Limit school choices for non-superusers"""
        if db_field.name == "school" and not request.user.is_superuser:
            if hasattr(request.user, 'school') and request.user.school:
                kwargs["queryset"] = type(db_field.related_model).objects.filter(id=request.user.school.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """Customize form fields"""
        # This method doesn't have access to request context
        # We'll handle the uploaded_by field in save_model instead
        return super().formfield_for_dbfield(db_field, **kwargs)
    
    def save_model(self, request, obj, form, change):
        """Set uploaded_by automatically if not set and handle file uploads"""
        if not change:  # Only for new objects
            obj.uploaded_by = request.user
            
            # Handle file upload if provided
            if form.cleaned_data.get('file'):
                file_obj = form.cleaned_data['file']
                try:
                    # Upload to Firebase or local storage
                    firebase_service = FirebaseStorageService()
                    folder = f"schools/{obj.school.id}/{obj.file_type}"
                    upload_result = firebase_service.upload_file(file_obj, folder)
                    
                    # Update object with upload results
                    obj.firebase_path = upload_result['path']
                    obj.firebase_url = upload_result['url']
                    obj.file_size = upload_result['size']
                    obj.content_type = upload_result['content_type']
                    
                except Exception as e:
                    # If Firebase fails, fall back to local storage or show error
                    from django.contrib import messages
                    messages.warning(request, f"File upload failed: {str(e)}. Please check storage configuration.")
        
        super().save_model(request, obj, form, change)
    
    actions = ['mark_as_public', 'mark_as_private', 'mark_as_deleted', 'mark_as_active']
    
    def mark_as_public(self, request, queryset):
        """Mark selected files as public"""
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} files marked as public.')
    mark_as_public.short_description = "Mark selected files as public"
    
    def mark_as_private(self, request, queryset):
        """Mark selected files as private"""
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} files marked as private.')
    mark_as_private.short_description = "Mark selected files as private"
    
    def mark_as_deleted(self, request, queryset):
        """Mark selected files as deleted"""
        updated = queryset.update(is_deleted=True)
        self.message_user(request, f'{updated} files marked as deleted.')
    mark_as_deleted.short_description = "Mark selected files as deleted"
    
    def mark_as_active(self, request, queryset):
        """Mark selected files as active (not deleted)"""
        updated = queryset.update(is_deleted=False)
        self.message_user(request, f'{updated} files marked as active.')
    mark_as_active.short_description = "Mark selected files as active"
