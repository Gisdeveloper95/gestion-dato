from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado para permitir lectura a cualquier usuario,
    pero requere autenticación para modificar, crear o eliminar (POST UPDATE DELETE).
    """

    def has_permission(self, request, view):
        # Permitir métodos GET, HEAD, OPTIONS para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Requerir autenticación para cualquier otro método
        return request.user and request.user.is_authenticated
    

class ReadPublicWriteAdminOnly(BasePermission):
    """
    Permission personalizada que permite:
    - Lectura (GET, HEAD, OPTIONS): Acceso público (sin autenticación)
    - Escritura (POST, PUT, PATCH, DELETE): Solo administradores autenticados
    """
    
    def has_permission(self, request, view):
        # ✅ OPERACIONES DE LECTURA: Permitir a todos
        if request.method in SAFE_METHODS:
            return True
        
        # 🔒 OPERACIONES DE ESCRITURA: Solo administradores autenticados
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_staff or request.user.is_superuser)
        )

class ReadAuthenticatedWriteAdminOnly(BasePermission):
    """
    Permission alternativa más restrictiva:
    - Lectura (GET): Solo usuarios autenticados
    - Escritura (POST, PUT, PATCH, DELETE): Solo administradores
    """
    
    def has_permission(self, request, view):
        # 🔐 OPERACIONES DE LECTURA: Solo autenticados
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # 🔒 OPERACIONES DE ESCRITURA: Solo administradores
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_staff or request.user.is_superuser)
        )

class IsAdminUserOrReadOnly(BasePermission):
    """
    Permission simple: Solo administradores pueden escribir, lectura libre
    """
    
    def has_permission(self, request, view):
        # Lectura libre
        if request.method in SAFE_METHODS:
            return True
            
        # Escritura solo para admins
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_staff
        )

class ReadOnlyOrSuperAdminWrite(BasePermission):
    """
    Permission ultra restrictiva: Solo super admins pueden escribir
    """
    
    def has_permission(self, request, view):
        # Lectura libre
        if request.method in SAFE_METHODS:
            return True
            
        # Escritura solo para super admins
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_superuser
        )