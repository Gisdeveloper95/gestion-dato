"""
Autenticación personalizada con tokens que expiran.

Este módulo implementa:
- ExpiringTokenAuthentication: Tokens que expiran después de un tiempo configurado
- Funciones auxiliares para manejo de tokens
"""
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed


# Tiempo de expiración por defecto: 8 horas (una jornada laboral)
TOKEN_EXPIRATION_HOURS = getattr(settings, 'TOKEN_EXPIRATION_HOURS', 8)


class ExpiringTokenAuthentication(TokenAuthentication):
    """
    Autenticación por token con expiración.

    Los tokens expiran después del tiempo configurado en TOKEN_EXPIRATION_HOURS.
    Por defecto: 8 horas.

    Configuración en settings.py:
        TOKEN_EXPIRATION_HOURS = 8  # Número de horas

    O via variable de entorno:
        TOKEN_EXPIRATION_HOURS=8
    """

    def authenticate_credentials(self, key):
        """
        Autentica el token y verifica que no haya expirado.
        """
        try:
            token = Token.objects.select_related('user').get(key=key)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Token inválido.')

        if not token.user.is_active:
            raise AuthenticationFailed('Usuario inactivo o eliminado.')

        # Verificar expiración
        token_age = timezone.now() - token.created
        expiration_time = timedelta(hours=TOKEN_EXPIRATION_HOURS)

        if token_age > expiration_time:
            # Token expirado - eliminarlo
            token.delete()
            raise AuthenticationFailed(
                f'Token expirado. Por favor, inicie sesión nuevamente. '
                f'(Los tokens expiran después de {TOKEN_EXPIRATION_HOURS} horas)'
            )

        return (token.user, token)


def refresh_token(user):
    """
    Refresca el token de un usuario eliminando el anterior y creando uno nuevo.

    Args:
        user: Instancia del usuario

    Returns:
        Token: Nuevo token
    """
    # Eliminar token anterior si existe
    Token.objects.filter(user=user).delete()

    # Crear nuevo token
    return Token.objects.create(user=user)


def get_token_expiration_info(token):
    """
    Obtiene información sobre la expiración de un token.

    Args:
        token: Instancia del Token

    Returns:
        dict: Información de expiración
    """
    token_age = timezone.now() - token.created
    expiration_time = timedelta(hours=TOKEN_EXPIRATION_HOURS)
    time_remaining = expiration_time - token_age

    return {
        'created': token.created.isoformat(),
        'expires_at': (token.created + expiration_time).isoformat(),
        'expires_in_seconds': max(0, int(time_remaining.total_seconds())),
        'expires_in_hours': max(0, time_remaining.total_seconds() / 3600),
        'is_expired': token_age > expiration_time
    }


def cleanup_expired_tokens():
    """
    Limpia todos los tokens expirados de la base de datos.
    Útil para ejecutar como tarea programada.

    Returns:
        int: Número de tokens eliminados
    """
    expiration_threshold = timezone.now() - timedelta(hours=TOKEN_EXPIRATION_HOURS)
    deleted_count, _ = Token.objects.filter(created__lt=expiration_threshold).delete()
    return deleted_count
