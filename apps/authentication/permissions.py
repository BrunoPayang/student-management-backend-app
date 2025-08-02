from rest_framework import permissions


class IsSystemAdmin(permissions.BasePermission):
    """
    Permission class for system administrators only
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.is_system_admin()
        )


class IsSchoolStaff(permissions.BasePermission):
    """
    Permission class for school staff only
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.is_school_staff()
        )


class IsParent(permissions.BasePermission):
    """
    Permission class for parents only
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.is_parent()
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class that allows owners and system admins
    """
    def has_object_permission(self, request, view, obj):
        # System admins can access everything
        if request.user.is_system_admin():
            return True
        
        # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return obj == request.user


class IsInSameSchool(permissions.BasePermission):
    """
    Permission class that checks if users are in the same school
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.school is not None
    
    def has_object_permission(self, request, view, obj):
        # System admins can access everything
        if request.user.is_system_admin():
            return True
        
        # Check if object belongs to the same school
        if hasattr(obj, 'school'):
            return obj.school == request.user.school
        
        return False


class IsSchoolStaffOrSystemAdmin(permissions.BasePermission):
    """
    Permission class for school staff and system administrators
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.is_school_staff() or request.user.is_system_admin())
        )


class CanManageUsers(permissions.BasePermission):
    """
    Permission class for user management operations
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # System admins can manage all users
        if request.user.is_system_admin():
            return True
        
        # School staff can manage users in their school
        if request.user.is_school_staff():
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # System admins can manage all users
        if request.user.is_system_admin():
            return True
        
        # School staff can only manage users in their school
        if request.user.is_school_staff():
            return obj.school == request.user.school
        
        return False 