from rest_framework import serializers
from .models import Notification, NotificationDelivery


class DynamicSchoolField(serializers.PrimaryKeyRelatedField):
    """Dynamic school field that adjusts queryset based on user permissions"""
    
    def get_queryset(self):
        """Get the appropriate school queryset based on user permissions"""
        if 'request' in self.context:
            user = self.context['request'].user
            if hasattr(user, 'is_system_admin') and user.is_system_admin():
                # Admin users can select any school
                from apps.schools.models import School
                return School.objects.all()
            else:
                # Non-admin users can only use their assigned school
                if hasattr(user, 'school') and user.school:
                    from apps.schools.models import School
                    return School.objects.filter(id=user.school.id)
        # Default fallback
        from apps.schools.models import School
        return School.objects.all()


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications - READ ONLY"""
    school_name = serializers.CharField(source='school.name', read_only=True)
    target_user_ids = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'body', 'notification_type', 'school', 'school_name',
            'target_user_ids', 'sent_via_fcm', 'sent_via_email', 'sent_via_sms', 'data',
            'created_at', 'sent_at'
        ]
        read_only_fields = [
            'id', 'title', 'body', 'notification_type', 'school', 'school_name',
            'target_user_ids', 'sent_via_fcm', 'sent_via_email', 'sent_via_sms', 'data',
            'created_at', 'sent_at'
        ]
    
    def get_target_user_ids(self, obj):
        """Return list of target user IDs safely"""
        try:
            if obj and hasattr(obj, 'target_users'):
                return list(obj.target_users.values_list('id', flat=True))
            return []
        except Exception:
            return []

class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications - WRITE ONLY"""
    target_user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False, 
        allow_empty=True,
        help_text="List of user IDs to target (optional)"
    )
    school = DynamicSchoolField(
        required=True,  # Changed from False to True - school is always required
        help_text="School ID (required for all users)"
    )
    
    class Meta:
        model = Notification
        fields = [
            'title', 'body', 'notification_type', 'target_user_ids', 'school', 'data'
        ]
        # No read_only_fields needed for create serializer
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial value and read-only for non-admin users
        if 'request' in self.context:
            user = self.context['request'].user
            if not (hasattr(user, 'is_system_admin') and user.is_system_admin()):
                if hasattr(user, 'school') and user.school:
                    self.fields['school'].initial = user.school.id
                    self.fields['school'].read_only = True
    
    def validate_notification_type(self, value):
        """Validate notification type"""
        valid_types = [choice[0] for choice in Notification._meta.get_field('notification_type').choices]
        if value not in valid_types:
            raise serializers.ValidationError(f"Invalid notification type. Must be one of: {', '.join(valid_types)}")
        return value
    
    def validate_school(self, value):
        """Validate school assignment"""
        user = self.context['request'].user
        
        if hasattr(user, 'is_system_admin') and user.is_system_admin():
            # Admin users must specify a school if they don't have one assigned
            if not value and not (hasattr(user, 'school') and user.school):
                raise serializers.ValidationError("School is required for admin users who don't have a school assigned")
        else:
            # Non-admin users must have a school assigned
            if not hasattr(user, 'school') or not user.school:
                raise serializers.ValidationError("User must be associated with a school to create notifications")
            # Non-admin users can only use their assigned school
            if value and value.id != user.school.id:
                raise serializers.ValidationError("You can only create notifications for your assigned school")
        
        return value
    
    def create(self, validated_data):
        """Create notification with proper school assignment"""
        # Extract target_user_ids before creating the notification
        target_user_ids = validated_data.pop('target_user_ids', [])
        
        # Get school from validated data or user context
        user = self.context['request'].user
        if 'school' in validated_data:
            school = validated_data['school']
        else:
            # For non-admin users, get school from user context
            if not hasattr(user, 'school') or not user.school:
                raise serializers.ValidationError("User must be associated with a school to create notifications")
            school = user.school
        
        # Add school to validated data
        validated_data['school'] = school
        
        # Create notification
        notification = Notification.objects.create(**validated_data)
        
        # Handle target users if specified
        if target_user_ids:
            try:
                from apps.authentication.models import User
                users = User.objects.filter(id__in=target_user_ids, school=school)
                notification.target_users.set(users)
            except Exception as e:
                # Log the error but don't fail the creation
                print(f"Warning: Could not set target users: {e}")
        
        return notification

class NotificationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating notifications"""
    target_user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False, 
        allow_empty=True
    )
    school = DynamicSchoolField(
        required=False,
        help_text="School ID (admin users can change, school users cannot)"
    )
    
    class Meta:
        model = Notification
        fields = [
            'title', 'body', 'notification_type', 'target_user_ids', 'school', 'data'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set read-only for non-admin users
        if 'request' in self.context:
            user = self.context['request'].user
            if not (hasattr(user, 'is_system_admin') and user.is_system_admin()):
                self.fields['school'].read_only = True
    
    def validate_school(self, value):
        """Validate school assignment"""
        user = self.context['request'].user
        
        if not (hasattr(user, 'is_system_admin') and user.is_system_admin()):
            # Non-admin users cannot change the school
            if value and value.id != self.instance.school.id:
                raise serializers.ValidationError("You cannot change the school of a notification")
        
        return value
    
    def update(self, instance, validated_data):
        """Update notification"""
        target_user_ids = validated_data.pop('target_user_ids', None)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Handle target users if specified
        if target_user_ids is not None:
            try:
                from apps.authentication.models import User
                users = User.objects.filter(id__in=target_user_ids, school=instance.school)
                instance.target_users.set(users)
            except Exception as e:
                print(f"Warning: Could not update target users: {e}")
        
        instance.save()
        return instance

class NotificationDeliverySerializer(serializers.ModelSerializer):
    """Serializer for notification delivery tracking"""
    notification_title = serializers.CharField(source='notification.title', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = NotificationDelivery
        fields = [
            'id', 'notification', 'notification_title', 'user', 'user_name',
            'delivered_via_fcm', 'delivered_via_email', 'delivered_via_sms',
            'fcm_message_id', 'fcm_error', 'created_at', 'delivered_at', 'read_at'
        ]
        read_only_fields = [
            'id', 'notification_title', 'user_name', 'fcm_message_id',
            'fcm_error', 'created_at', 'delivered_at'
        ]
