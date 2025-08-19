from rest_framework import serializers
from .models import FileUpload

class FileUploadSerializer(serializers.ModelSerializer):
    """Serializer for file uploads"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    file_size_mb = serializers.ReadOnlyField()
    tags = serializers.CharField(read_only=True, help_text="Comma-separated tags")
    
    class Meta:
        model = FileUpload
        fields = [
            'id', 'original_name', 'firebase_url', 'file_size_mb',
            'content_type', 'file_type', 'description', 'tags',
            'is_public', 'uploaded_by', 'uploaded_by_name',
            'school_name', 'uploaded_at'
        ]
        read_only_fields = [
            'id', 'firebase_url', 'file_size_mb', 'uploaded_by',
            'uploaded_by_name', 'school_name', 'uploaded_at'
        ]

class FileUploadCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating file uploads"""
    file = serializers.FileField(write_only=True, required=True, help_text="File to upload")
    tags = serializers.CharField(required=False, allow_blank=True, help_text="Comma-separated tags (optional)")
    
    class Meta:
        model = FileUpload
        fields = [
            'file', 'file_type', 'description', 'tags', 'is_public'
        ]
    
    def validate_file_type(self, value):
        """Validate file type"""
        valid_types = [choice[0] for choice in FileUpload._meta.get_field('file_type').choices]
        if value not in valid_types:
            raise serializers.ValidationError("Invalid file type")
        return value
    
    def validate_tags(self, value):
        """Validate and clean tags"""
        if value:
            # Remove extra whitespace and split by comma
            tags = [tag.strip() for tag in value.split(',') if tag.strip()]
            # Join back with comma and space for consistency
            return ', '.join(tags)
        return value
