from rest_framework import serializers
from .models import School, SchoolConfiguration


class SchoolConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for school configuration settings"""
    
    class Meta:
        model = SchoolConfiguration
        fields = [
            'academic_year_start', 'academic_year_end', 'current_semester',
            'enable_sms_notifications', 'enable_email_notifications', 
            'enable_push_notifications', 'currency', 'payment_reminder_days',
            'max_file_size_mb', 'allowed_file_types'
        ]


class SchoolListSerializer(serializers.ModelSerializer):
    """Serializer for school list view (limited fields)"""
    student_count = serializers.SerializerMethodField()
    staff_count = serializers.SerializerMethodField()
    
    class Meta:
        model = School
        fields = [
            'id', 'name', 'slug', 'school_type', 'city', 'state',
            'is_active', 'is_verified', 'student_count', 'staff_count'
        ]
    
    def get_student_count(self, obj):
        return obj.get_student_count()
    
    def get_staff_count(self, obj):
        return obj.get_staff_count()


class SchoolDetailSerializer(serializers.ModelSerializer):
    """Serializer for school detail view (all fields)"""
    configuration = SchoolConfigurationSerializer(read_only=True)
    student_count = serializers.SerializerMethodField()
    staff_count = serializers.SerializerMethodField()
    
    class Meta:
        model = School
        fields = [
            'id', 'name', 'slug', 'school_type', 'academic_year',
            'logo', 'primary_color', 'secondary_color',
            'contact_email', 'contact_phone', 'website',
            'address', 'city', 'state', 'country', 'postal_code',
            'is_active', 'is_verified', 'configuration',
            'student_count', 'staff_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_student_count(self, obj):
        return obj.get_student_count()
    
    def get_staff_count(self, obj):
        return obj.get_staff_count()
    
    def validate_slug(self, value):
        """Ensure slug is unique"""
        if School.objects.filter(slug=value).exists():
            raise serializers.ValidationError("A school with this slug already exists.")
        return value


class SchoolCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new schools"""
    configuration = SchoolConfigurationSerializer(required=False)
    
    class Meta:
        model = School
        fields = [
            'name', 'school_type', 'academic_year',
            'logo', 'primary_color', 'secondary_color',
            'contact_email', 'contact_phone', 'website',
            'address', 'city', 'state', 'country', 'postal_code',
            'configuration'
        ]
    
    def create(self, validated_data):
        """Create school and configuration"""
        configuration_data = validated_data.pop('configuration', None)
        school = School.objects.create(**validated_data)
        
        if configuration_data:
            SchoolConfiguration.objects.create(school=school, **configuration_data)
        else:
            # Create default configuration
            SchoolConfiguration.objects.create(school=school)
        
        return school


class SchoolUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating schools"""
    configuration = SchoolConfigurationSerializer(required=False)
    
    class Meta:
        model = School
        fields = [
            'name', 'school_type', 'academic_year',
            'logo', 'primary_color', 'secondary_color',
            'contact_email', 'contact_phone', 'website',
            'address', 'city', 'state', 'country', 'postal_code',
            'is_active', 'is_verified', 'configuration'
        ]
    
    def update(self, instance, validated_data):
        """Update school and configuration"""
        configuration_data = validated_data.pop('configuration', None)
        
        # Update school
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update configuration if provided
        if configuration_data and hasattr(instance, 'configuration'):
            config = instance.configuration
            for attr, value in configuration_data.items():
                setattr(config, attr, value)
            config.save()
        
        return instance 