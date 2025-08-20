from rest_framework import serializers
from .models import Notification, NotificationDelivery

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications - READ ONLY"""
    school_name = serializers.CharField(source='school.name', read_only=True)
    target_user_ids = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'body', 'notification_type', 'school', 'school_name',
            'target_user_ids', 'sent_via_fcm', 'sent_via_email', 'data',
            'created_at', 'sent_at'
        ]
        read_only_fields = [
            'id', 'title', 'body', 'notification_type', 'school', 'school_name',
            'target_user_ids', 'sent_via_fcm', 'sent_via_email', 'data',
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
    
    class Meta:
        model = Notification
        fields = [
            'title', 'body', 'notification_type', 'target_user_ids', 'data'
        ]
        # No read_only_fields needed for create serializer
    
    def validate_notification_type(self, value):
        """Validate notification type"""
        valid_types = [choice[0] for choice in Notification._meta.get_field('notification_type').choices]
        if value not in valid_types:
            raise serializers.ValidationError(f"Invalid notification type. Must be one of: {', '.join(valid_types)}")
        return value
    
    def create(self, validated_data):
        """Create notification with school from user context"""
        # Extract target_user_ids before creating the notification
        target_user_ids = validated_data.pop('target_user_ids', [])
        
        # Get school from user context
        user = self.context['request'].user
        if not hasattr(user, 'school') or not user.school:
            raise serializers.ValidationError("User must be associated with a school to create notifications")
        
        # Add school to validated data
        validated_data['school'] = user.school
        
        # Create notification
        notification = Notification.objects.create(**validated_data)
        
        # Handle target users if specified
        if target_user_ids:
            try:
                from apps.authentication.models import User
                users = User.objects.filter(id__in=target_user_ids, school=user.school)
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
    
    class Meta:
        model = Notification
        fields = [
            'title', 'body', 'notification_type', 'target_user_ids', 'data'
        ]
    
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
            'delivered_via_fcm', 'delivered_via_email', 'fcm_message_id',
            'fcm_error', 'created_at', 'delivered_at'
        ]
        read_only_fields = [
            'id', 'notification_title', 'user_name', 'fcm_message_id',
            'fcm_error', 'created_at', 'delivered_at'
        ]
