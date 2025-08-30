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
    
    def to_internal_value(self, data):
        """Handle both UUID strings and UUID objects"""
        try:
            # If it's already a UUID object, return it
            if hasattr(data, 'uuid'):
                return data
            
            # If it's a string, try to convert to UUID
            if isinstance(data, str):
                import uuid
                uuid_obj = uuid.UUID(data)
                # Get the actual School object
                from apps.schools.models import School
                return School.objects.get(id=uuid_obj)
            
            # If it's already a School object, return it
            if hasattr(data, 'id') and hasattr(data, 'name'):
                return data
                
            # Default behavior
            return super().to_internal_value(data)
            
        except (ValueError, TypeError, School.DoesNotExist) as e:
            raise serializers.ValidationError(f"Invalid school ID: {data}. Error: {str(e)}")


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
    school_name = serializers.CharField(source='school.name', read_only=True)
    target_user_ids = serializers.SerializerMethodField()
    school = DynamicSchoolField(
        required=False,  # Make it optional since we can get it from user context
        help_text="School ID (optional - will use user's school if not provided)"
    )
    
    def to_internal_value(self, data):
        """Handle target_user_ids input"""
        internal_value = super().to_internal_value(data)
        # Store target_user_ids for later use in create method
        if 'target_user_ids' in data:
            self._target_user_ids_input = data['target_user_ids']
        else:
            self._target_user_ids_input = []
        return internal_value
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'body', 'notification_type', 'target_user_ids', 'school', 'school_name', 'data',
            'sent_via_fcm', 'sent_via_email', 'sent_via_sms', 'created_at', 'sent_at'
        ]
        read_only_fields = ['id', 'school_name', 'sent_via_fcm', 'sent_via_email', 'sent_via_sms', 'created_at', 'sent_at']
    
    def get_target_user_ids(self, obj):
        """Return list of target user IDs safely"""
        try:
            if obj and hasattr(obj, 'target_users'):
                return list(obj.target_users.values_list('id', flat=True))
            return []
        except Exception:
            return []
    
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
        """Create notification with proper school assignment and target users"""
        # Extract target_user_ids from the stored input
        target_user_ids = getattr(self, '_target_user_ids_input', [])
        
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
        
        # Handle target users
        if target_user_ids and len(target_user_ids) > 0:
            # If specific users are specified, use them
            try:
                from apps.authentication.models import User
                
                # First try to find users directly in the specified school
                users = User.objects.filter(id__in=target_user_ids, school=school)
                
                # If no users found directly in school, check for parents who have students in this school
                if not users.exists():
                    from apps.students.models import ParentStudent
                    parent_students = ParentStudent.objects.filter(
                        student__school=school,
                        parent_id__in=target_user_ids
                    ).values_list('parent_id', flat=True).distinct()
                    
                    if parent_students.exists():
                        additional_users = User.objects.filter(id__in=parent_students)
                        users = additional_users
                
                # If still no users found and user is admin, try to find them anywhere
                if not users.exists() and user.is_system_admin():
                    users = User.objects.filter(id__in=target_user_ids)
                
                if users.exists():
                    notification.target_users.set(users)
                    print(f"Notification created with {users.count()} specific target users")
                else:
                    print(f"Warning: No users found with IDs {target_user_ids} in school {school.name} or with students in school")
                    
            except Exception as e:
                print(f"Warning: Could not set target users: {e}")
        else:
            # If no specific users, automatically target all parents in the school
            try:
                from apps.authentication.models import User
                from apps.students.models import ParentStudent
                
                # Get direct school parents
                direct_parents = User.objects.filter(
                    user_type='parent',
                    school=school
                )
                
                # Get parents who have students in this school but don't have school set
                parent_students = ParentStudent.objects.filter(
                    student__school=school
                ).values_list('parent_id', flat=True).distinct()
                
                additional_parents = User.objects.filter(
                    id__in=parent_students,
                    school__isnull=True
                )
                
                # Combine the querysets
                from django.db.models import Q
                all_parents = direct_parents | additional_parents
                
                # Set target users
                notification.target_users.set(all_parents)
                print(f"Notification created with {all_parents.count()} total target parents (auto-targeted)")
                
            except Exception as e:
                print(f"Warning: Could not auto-target parents: {e}")
        
        return notification

class NotificationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating notifications"""
    target_user_ids = serializers.SerializerMethodField()
    school = DynamicSchoolField(
        required=False,
        help_text="School ID (admin users can change, school users cannot)"
    )
    
    class Meta:
        model = Notification
        fields = [
            'title', 'body', 'notification_type', 'target_user_ids', 'school', 'data'
        ]
    
    def to_internal_value(self, data):
        """Handle target_user_ids input"""
        internal_value = super().to_internal_value(data)
        # Store target_user_ids for later use in update method
        if 'target_user_ids' in data:
            self._target_user_ids_input = data['target_user_ids']
        else:
            self._target_user_ids_input = None
        return internal_value
    
    def get_target_user_ids(self, obj):
        """Return list of target user IDs safely"""
        try:
            if obj and hasattr(obj, 'target_users'):
                return list(obj.target_users.values_list('id', flat=True))
            return []
        except Exception:
            return []
    
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
        target_user_ids = getattr(self, '_target_user_ids_input', None)
        
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
