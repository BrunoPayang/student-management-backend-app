from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample

from .models import User
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    PasswordChangeSerializer, FCMTokenSerializer
)
from .permissions import IsOwnerOrAdmin


@extend_schema_view(
    post=extend_schema(
        summary="Connexion utilisateur",
        description="Authentification JWT avec nom d'utilisateur et mot de passe",
        tags=["authentication"],
        examples=[
            OpenApiExample(
                "Exemple de connexion",
                value={
                    "username": "utilisateur",
                    "password": "motdepasse123"
                },
                request_only=True,
            ),
        ],
    )
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vue personnalisée pour l'obtention de tokens JWT avec données utilisateur
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Get user data
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                user_serializer = UserSerializer(user)
                
                # Add user data to response
                response.data['user'] = user_serializer.data
                
                # Log the login
                import logging
                logger = logging.getLogger('schoolconnect')
                logger.info(f"Utilisateur {user.username} connecté avec succès")
        
        return response


@extend_schema_view(
    post=extend_schema(
        summary="Inscription utilisateur",
        description="Création d'un nouveau compte utilisateur",
        tags=["authentication"],
        examples=[
            OpenApiExample(
                "Exemple d'inscription parent",
                value={
                    "username": "parent123",
                    "email": "parent@example.com",
                    "password": "motdepasse123",
                    "password_confirm": "motdepasse123",
                    "first_name": "Jean",
                    "last_name": "Dupont",
                    "user_type": "parent",
                    "phone": "+22712345678"
                },
                request_only=True,
            ),
        ],
    )
)
class RegisterView(generics.CreateAPIView):
    """
    Endpoint d'inscription utilisateur
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Return user data with tokens
        user_serializer = UserSerializer(user)
        
        return Response({
            'user': user_serializer.data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(access_token),
            }
        }, status=status.HTTP_201_CREATED)


@extend_schema_view(
    post=extend_schema(
        summary="Déconnexion utilisateur",
        description="Déconnexion et invalidation du token de rafraîchissement",
        tags=["authentication"],
        examples=[
            OpenApiExample(
                "Exemple de déconnexion",
                value={
                    "refresh_token": "token_de_rafraichissement"
                },
                request_only=True,
            ),
        ],
    )
)
class LogoutView(APIView):
    """
    Endpoint de déconnexion qui blacklist le token de rafraîchissement
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                # If token is invalid, just continue with logout
                pass
        
        # Clear FCM token on logout
        request.user.fcm_token = ''
        request.user.save()
        
        return Response({
            'message': 'Déconnexion réussie'
        }, status=status.HTTP_200_OK)


@extend_schema_view(
    get=extend_schema(
        summary="Profil utilisateur",
        description="Récupération du profil de l'utilisateur connecté",
        tags=["authentication"],
    ),
    put=extend_schema(
        summary="Mise à jour du profil",
        description="Mise à jour des informations du profil utilisateur",
        tags=["authentication"],
    ),
    patch=extend_schema(
        summary="Mise à jour partielle du profil",
        description="Mise à jour partielle des informations du profil utilisateur",
        tags=["authentication"],
    ),
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Vue du profil utilisateur pour les utilisateurs authentifiés
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


@extend_schema_view(
    post=extend_schema(
        summary="Changement de mot de passe",
        description="Changement du mot de passe de l'utilisateur connecté",
        tags=["authentication"],
        examples=[
            OpenApiExample(
                "Exemple de changement de mot de passe",
                value={
                    "old_password": "ancien_mot_de_passe",
                    "new_password": "nouveau_mot_de_passe",
                    "new_password_confirm": "nouveau_mot_de_passe"
                },
                request_only=True,
            ),
        ],
    )
)
class ChangePasswordView(APIView):
    """
    Endpoint de changement de mot de passe
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Mot de passe modifié avec succès'
            }, status=status.HTTP_200_OK)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema_view(
    post=extend_schema(
        summary="Mise à jour du token FCM",
        description="Mise à jour du token Firebase Cloud Messaging pour les notifications push",
        tags=["authentication"],
        examples=[
            OpenApiExample(
                "Exemple de mise à jour du token FCM",
                value={
                    "fcm_token": "token_fcm_pour_notifications_push"
                },
                request_only=True,
            ),
        ],
    )
)
class UpdateFCMTokenView(APIView):
    """
    Mise à jour du token FCM pour les notifications push
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = FCMTokenSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Token FCM mis à jour avec succès'
            }, status=status.HTTP_200_OK)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema_view(
    post=extend_schema(
        summary="Demande de réinitialisation de mot de passe",
        description="Envoi d'un email de réinitialisation de mot de passe",
        tags=["authentication"],
        examples=[
            OpenApiExample(
                "Exemple de demande de réinitialisation",
                value={
                    "email": "utilisateur@example.com"
                },
                request_only=True,
            ),
        ],
    )
)
class PasswordResetRequestView(APIView):
    """
    Demande de réinitialisation de mot de passe par email
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({
                'error': 'L\'email est requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link (you'll need to implement frontend route)
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            
            # Send email
            send_mail(
                subject='SchoolConnect - Réinitialisation du mot de passe',
                message=f'Cliquez sur le lien pour réinitialiser votre mot de passe: {reset_link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            return Response({
                'message': 'Email de réinitialisation du mot de passe envoyé'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Don't reveal if email exists or not
            return Response({
                'message': 'Si l\'email existe, un lien de réinitialisation a été envoyé'
            }, status=status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(
        summary="Confirmation de réinitialisation de mot de passe",
        description="Confirmation de la réinitialisation avec token",
        tags=["authentication"],
        examples=[
            OpenApiExample(
                "Exemple de confirmation de réinitialisation",
                value={
                    "uid": "uid_encode",
                    "token": "token_de_reinitialisation",
                    "new_password": "nouveau_mot_de_passe"
                },
                request_only=True,
            ),
        ],
    )
)
class PasswordResetConfirmView(APIView):
    """
    Confirmation de la réinitialisation de mot de passe avec token
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        if not all([uid, token, new_password]):
            return Response({
                'error': 'Tous les champs sont requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Decode user ID
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            
            # Verify token
            if default_token_generator.check_token(user, token):
                # Validate password
                from django.contrib.auth.password_validation import validate_password
                validate_password(new_password)
                
                # Set new password
                user.set_password(new_password)
                user.save()
                
                return Response({
                    'message': 'Réinitialisation du mot de passe réussie'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Token invalide ou expiré'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except (User.DoesNotExist, ValueError, OverflowError):
            return Response({
                'error': 'Lien de réinitialisation invalide'
            }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Utilisateur actuel",
    description="Récupération des informations de l'utilisateur connecté",
    tags=["authentication"],
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    """
    Récupération des informations de l'utilisateur authentifié actuel
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@extend_schema(
    summary="Contexte utilisateur",
    description="Récupération du contexte utilisateur pour le frontend (école, permissions, etc.)",
    tags=["authentication"],
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_context(request):
    """
    Récupération des informations de contexte utilisateur pour le frontend (école, permissions, etc.)
    """
    user = request.user
    context = {
        'user_id': user.id,
        'username': user.username,
        'user_type': user.user_type,
        'permissions': {
            'is_admin': user.is_system_admin(),
            'is_school_staff': user.is_school_staff(),
            'is_parent': user.is_parent(),
        }
    }
    
    # Add school context if applicable
    school_context = user.get_school_context()
    if school_context:
        context['school'] = school_context
    
    return Response(context)
