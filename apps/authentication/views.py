from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Create your views here.

@api_view(['POST'])
def RegisterView(request):
    """Placeholder for user registration - will be implemented in Phase 2"""
    return Response({'message': 'Registration endpoint - coming soon'}, status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProfileView(request):
    """Placeholder for user profile - will be implemented in Phase 2"""
    return Response({'message': 'Profile endpoint - coming soon'}, status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ChangePasswordView(request):
    """Placeholder for password change - will be implemented in Phase 2"""
    return Response({'message': 'Change password endpoint - coming soon'}, status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def LogoutView(request):
    """Placeholder for logout - will be implemented in Phase 2"""
    return Response({'message': 'Logout endpoint - coming soon'}, status=status.HTTP_501_NOT_IMPLEMENTED)
