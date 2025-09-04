from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from .models import School, SchoolConfiguration


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Default configuration',
            summary='Default school configuration',
            description='Default configuration settings for a new school',
            value={
                "academic_year_start": "2024-09-01",
                "academic_year_end": "2025-06-30",
                "current_semester": "first",
                "enable_sms_notifications": True,
                "enable_email_notifications": True,
                "enable_push_notifications": True,
                "currency": "NGN",
                "payment_reminder_days": 7,
                "max_file_size_mb": 10,
                "allowed_file_types": [".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"]
            }
        )
    ]
)
class SchoolConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializer for school configuration settings.
    
    **Configuration Fields:**
    - `academic_year_start`: Start date of academic year (YYYY-MM-DD)
    - `academic_year_end`: End date of academic year (YYYY-MM-DD)
    - `current_semester`: Current semester (first, second, summer)
    - `enable_sms_notifications`: Enable SMS notifications (boolean)
    - `enable_email_notifications`: Enable email notifications (boolean)
    - `enable_push_notifications`: Enable push notifications (boolean)
    - `currency`: Currency code (e.g., NGN, USD, EUR)
    - `payment_reminder_days`: Days before payment reminder (integer)
    - `max_file_size_mb`: Maximum file size in MB (integer)
    - `allowed_file_types`: List of allowed file extensions (array)
    """
    
    class Meta:
        model = SchoolConfiguration
        fields = [
            'academic_year_start', 'academic_year_end', 'current_semester',
            'enable_sms_notifications', 'enable_email_notifications', 
            'enable_push_notifications', 'currency', 'payment_reminder_days',
            'max_file_size_mb', 'allowed_file_types'
        ]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'School list item',
            summary='School list item',
            description='Basic school information for list views',
            value={
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "École Primaire de Niamey",
                "slug": "ecole-primaire-niamey",
                "school_type": "primary",
                "city": "Niamey",
                "state": "Niamey",
                "is_active": True,
                "is_verified": True,
                "student_count": 150,
                "staff_count": 12
            }
        )
    ]
)
class SchoolListSerializer(serializers.ModelSerializer):
    """
    Serializer for school list view (limited fields).
    
    **Fields:**
    - `id`: Unique school identifier (UUID)
    - `name`: School name
    - `slug`: URL-friendly school identifier
    - `school_type`: Type of school (primary, secondary, both, university, other)
    - `city`: School city
    - `state`: School state
    - `is_active`: Whether school is active
    - `is_verified`: Whether school is verified
    - `student_count`: Number of active students (computed)
    - `staff_count`: Number of active staff (computed)
    """
    student_count = serializers.SerializerMethodField()
    staff_count = serializers.SerializerMethodField()
    
    class Meta:
        model = School
        fields = [
            'id', 'name', 'slug', 'school_type', 'city', 'state',
            'is_active', 'is_verified', 'student_count', 'staff_count'
        ]
    
    def get_student_count(self, obj) -> int:
        return obj.get_student_count()
    
    def get_staff_count(self, obj) -> int:
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
    
    def get_student_count(self, obj) -> int:
        return obj.get_student_count()
    
    def get_staff_count(self, obj) -> int:
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
            # Create default configuration with required fields
            from datetime import date
            current_year = date.today().year
            SchoolConfiguration.objects.create(
                school=school,
                academic_year_start=date(current_year, 9, 1),  # September 1st
                academic_year_end=date(current_year + 1, 6, 30),  # June 30th next year
                current_semester='first'
            )
        
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
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def update(self, instance, validated_data):
        """Update school and configuration"""
        configuration_data = validated_data.pop('configuration', None)
        
        # Update school fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update configuration if provided
        if configuration_data:
            # Ensure school has a configuration object
            if not hasattr(instance, 'configuration') or instance.configuration is None:
                from datetime import date
                current_year = date.today().year
                SchoolConfiguration.objects.create(
                    school=instance,
                    academic_year_start=date(current_year, 9, 1),
                    academic_year_end=date(current_year + 1, 6, 30),
                    current_semester='first'
                )
                instance.refresh_from_db()
            
            config = instance.configuration
            for attr, value in configuration_data.items():
                setattr(config, attr, value)
            config.save()
        
        return instance


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Complete school configuration response',
            summary='School configuration with all details',
            description='Complete school information including configuration settings',
            value={
                # School basic information
                "school_id": "123e4567-e89b-12d3-a456-426614174000",
                "school_name": "École Primaire de Niamey",
                "school_slug": "ecole-primaire-niamey",
                "school_type": "primary",
                "academic_year": "2024-2025",
                
                # School branding
                "logo": "https://firebase-storage.com/schools/logos/logo.png",
                "primary_color": "#1976D2",
                "secondary_color": "#424242",
                
                # School contact information
                "contact_email": "contact@ecole-niamey.ne",
                "contact_phone": "+22712345678",
                "website": "https://ecole-niamey.ne",
                
                # School location
                "address": "Quartier Plateau, Niamey",
                "city": "Niamey",
                "state": "Niamey",
                "country": "Niger",
                "postal_code": "10000",
                
                # School status
                "is_active": True,
                "is_verified": True,
                
                # School statistics
                "student_count": 150,
                "staff_count": 12,
                
                # Timestamps
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-09-04T14:20:00Z",
                "config_created_at": "2024-01-15T10:30:00Z",
                "config_updated_at": "2024-09-04T14:20:00Z",
                
                # Configuration settings
                "academic_year_start": "2024-09-01",
                "academic_year_end": "2025-06-30",
                "current_semester": "first",
                "enable_sms_notifications": True,
                "enable_email_notifications": True,
                "enable_push_notifications": True,
                "currency": "NGN",
                "payment_reminder_days": 7,
                "max_file_size_mb": 10,
                "allowed_file_types": [".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"]
            }
        )
    ]
)
class SchoolConfigurationDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for school configuration with complete school details.
    Used for GET /configuration endpoint to return all school information.
    
    **Response Fields:**
    - **School Basic Info**: ID, name, slug, type, academic year
    - **School Branding**: Logo, primary color, secondary color
    - **School Contact**: Email, phone, website
    - **School Location**: Address, city, state, country, postal code
    - **School Status**: Active status, verification status
    - **School Statistics**: Student count, staff count
    - **Timestamps**: School and configuration creation/update times
    - **Configuration Settings**: All configuration options
    """
    # School basic information
    school_id = serializers.UUIDField(source='school.id', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    school_slug = serializers.CharField(source='school.slug', read_only=True)
    school_type = serializers.CharField(source='school.school_type', read_only=True)
    academic_year = serializers.CharField(source='school.academic_year', read_only=True)
    
    # School branding
    logo = serializers.URLField(source='school.logo', read_only=True)
    primary_color = serializers.CharField(source='school.primary_color', read_only=True)
    secondary_color = serializers.CharField(source='school.secondary_color', read_only=True)
    
    # School contact information
    contact_email = serializers.EmailField(source='school.contact_email', read_only=True)
    contact_phone = serializers.CharField(source='school.contact_phone', read_only=True)
    website = serializers.URLField(source='school.website', read_only=True)
    
    # School location
    address = serializers.CharField(source='school.address', read_only=True)
    city = serializers.CharField(source='school.city', read_only=True)
    state = serializers.CharField(source='school.state', read_only=True)
    country = serializers.CharField(source='school.country', read_only=True)
    postal_code = serializers.CharField(source='school.postal_code', read_only=True)
    
    # School status
    is_active = serializers.BooleanField(source='school.is_active', read_only=True)
    is_verified = serializers.BooleanField(source='school.is_verified', read_only=True)
    
    # School statistics
    student_count = serializers.SerializerMethodField()
    staff_count = serializers.SerializerMethodField()
    
    # Timestamps
    created_at = serializers.DateTimeField(source='school.created_at', read_only=True)
    updated_at = serializers.DateTimeField(source='school.updated_at', read_only=True)
    config_created_at = serializers.DateTimeField(source='created_at', read_only=True)
    config_updated_at = serializers.DateTimeField(source='updated_at', read_only=True)
    
    class Meta:
        model = SchoolConfiguration
        fields = [
            # School basic info
            'school_id', 'school_name', 'school_slug', 'school_type', 'academic_year',
            # School branding
            'logo', 'primary_color', 'secondary_color',
            # School contact
            'contact_email', 'contact_phone', 'website',
            # School location
            'address', 'city', 'state', 'country', 'postal_code',
            # School status
            'is_active', 'is_verified',
            # School statistics
            'student_count', 'staff_count',
            # Timestamps
            'created_at', 'updated_at', 'config_created_at', 'config_updated_at',
            # Configuration settings
            'academic_year_start', 'academic_year_end', 'current_semester',
            'enable_sms_notifications', 'enable_email_notifications', 
            'enable_push_notifications', 'currency', 'payment_reminder_days',
            'max_file_size_mb', 'allowed_file_types'
        ]
    
    def get_student_count(self, obj) -> int:
        return obj.school.get_student_count()
    
    def get_staff_count(self, obj) -> int:
        return obj.school.get_staff_count() 