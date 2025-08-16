from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'address', 'emergency_contact', 'language_preference',
            'email_notifications', 'sms_notifications', 'push_notifications'
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    school_name = serializers.CharField(source='school.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'user_type', 'school', 'school_name', 
            'phone', 'profile_picture', 'is_verified', 'profile',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_verified']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'user_type', 'school', 'phone'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas")
        
        # Validate school assignment based on user type
        # Only 'school_staff' users must be linked to a school; parents do not require a school assignment.
        if attrs['user_type'] == 'school_staff' and not attrs.get('school'):
            raise serializers.ValidationError("L'école est obligatoire pour les utilisateurs du personnel de l'école.")
        
        if attrs['user_type'] == 'admin' and attrs.get('school'):
            raise serializers.ValidationError("L'administrateur du système ne doit pas être affecté à une école")
        
        #validate username
        # Username validation: must be alphanumeric, 4-30 chars, no spaces or special chars except underscore
        import re
        username = attrs.get('username')
        if not username:
            raise serializers.ValidationError("Le nom d'utilisateur est requis")
        if not re.match(r'^[a-zA-Z0-9_]{4,30}$', username):
            raise serializers.ValidationError(
                "Le nom d'utilisateur doit être composé de 4 à 30 caractères, ne contenir que des lettres, des chiffres ou des traits de soulignement, et ne pas comporter d'espaces."
            )
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Le nom d'utilisateur est déjà pris")
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError('Informations d\'identification invalides')
            
            if not user.is_active:
                raise serializers.ValidationError('Le compte d\'utilisateur est désactivé')
            
            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError('Doit inclure le nom d\'utilisateur et le mot de passe')


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Les nouveaux mots de passe ne correspondent pas")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("L'ancien mot de passe est incorrect")
        return value
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class FCMTokenSerializer(serializers.Serializer):
    fcm_token = serializers.CharField(max_length=500)
    
    def save(self):
        user = self.context['request'].user
        user.fcm_token = self.validated_data['fcm_token']
        user.save()
        return user 