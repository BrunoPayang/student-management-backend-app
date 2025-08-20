from rest_framework import serializers
from .models import Notification, NotificationDelivery

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    school_name = serializers.CharField(source='school.name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'body', 'notification_type', 'school', 'school_name',
            'target_users', 'sent_via_fcm', 'sent_via_email', 'data',
            'created_at', 'sent_at'
        ]
        read_only_fields = ['id', 'sent_via_fcm', 'sent_via_email', 'created_at', 'sent_at']

class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications"""
    target_users = serializers.ListField(required=False, allow_empty=True)
    
    class Meta:
        model = Notification
        fields = [
            'title', 'body', 'notification_type', 'target_users', 'data'
        ]
    
    def validate_notification_type(self, value):
        """Validate notification type"""
        valid_types = [choice[0] for choice in Notification._meta.get_field('notification_type').choices]
        if value not in valid_types:
            raise serializers.ValidationError("Invalid notification type")
        return value
    
    def create(self, validated_data):
        """Create notification with school from user context"""
        # Get school from user context
        user = self.context['request'].user
        if not hasattr(user, 'school') or not user.school:
            raise serializers.ValidationError("User must be associated with a school to create notifications")
        
        # Add school to validated data
        validated_data['school'] = user.school
        
        # Create notification
        notification = Notification.objects.create(**validated_data)
        
        # Handle target users if specified
        target_users = validated_data.get('target_users', [])
        if target_users:
            from apps.authentication.models import User
            users = User.objects.filter(id__in=target_users, school=user.school)
            notification.target_users.set(users)
        
        return notification

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
