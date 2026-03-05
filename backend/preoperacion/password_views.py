"""
Vistas para recuperación de contraseña.

Endpoints:
- POST /preoperacion/auth/request-password-reset/  - Solicitar recuperación
- POST /preoperacion/auth/confirm-password-reset/  - Confirmar nueva contraseña
- GET  /preoperacion/auth/validate-reset-token/    - Validar token (para frontend)
"""
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import PasswordResetToken


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    Solicita un token de recuperación de contraseña.

    Body:
    {
        "email_or_username": "usuario@ejemplo.com"  // o nombre de usuario
    }

    Respuesta (siempre exitosa por seguridad):
    {
        "success": true,
        "message": "Si existe una cuenta asociada, recibirás un correo con instrucciones"
    }
    """
    email_or_username = request.data.get('email_or_username', '').strip()

    if not email_or_username:
        return Response(
            {'error': 'Usuario o correo requerido'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Buscar usuario por email o username
        user = User.objects.get(
            Q(email=email_or_username) | Q(username=email_or_username),
            is_active=True
        )

        # Verificar que el usuario tenga email configurado
        if not user.email:
            print(f"[WARN] Usuario {user.username} no tiene email configurado")
            # Por seguridad, respondemos lo mismo
            return Response({
                'success': True,
                'message': 'Si existe una cuenta asociada, recibirás un correo con instrucciones'
            })

        # Invalidar tokens anteriores del usuario
        PasswordResetToken.objects.filter(user=user, used=False).update(used=True)

        # Crear nuevo token
        reset_token = PasswordResetToken.create_token(user)

        # Construir el enlace de recuperación
        frontend_url = getattr(settings, 'FRONTEND_URL', 'https://gestiondato.duckdns.org')
        reset_url = f"{frontend_url}/restablecer-contrasena?token={reset_token.token}"

        # Enviar correo
        try:
            send_mail(
                subject='Recuperación de contraseña - Sistema de Gestión de Datos IGAC',
                message=f'''Hola {user.first_name or user.username},

Has solicitado recuperar tu contraseña para el Sistema de Gestión de Datos IGAC.

Para restablecer tu contraseña, haz clic en el siguiente enlace (válido por 1 hora):

{reset_url}

Si no solicitaste este cambio, ignora este correo.

Saludos,
Equipo de Gestión de Datos IGAC''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            print(f"[INFO] Correo de recuperación enviado a {user.email}")
        except Exception as e:
            print(f"[ERROR] No se pudo enviar correo: {e}")
            import traceback
            traceback.print_exc()
            # En desarrollo, mostrar el enlace en consola
            print(f"[DEBUG] Enlace de recuperación: {reset_url}")

        return Response({
            'success': True,
            'message': 'Si existe una cuenta asociada, recibirás un correo con instrucciones'
        })

    except User.DoesNotExist:
        # Por seguridad, respondemos lo mismo incluso si el usuario no existe
        return Response({
            'success': True,
            'message': 'Si existe una cuenta asociada, recibirás un correo con instrucciones'
        })
    except Exception as e:
        print(f"[ERROR] Error inesperado en request_password_reset: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': 'Error al procesar la solicitud'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset(request):
    """
    Confirma el cambio de contraseña con el token.

    Body:
    {
        "token": "abc123...",
        "new_password": "nuevaContraseña123"
    }

    Respuestas:
    - 200: Contraseña actualizada exitosamente
    - 400: Token inválido/expirado o contraseña no proporcionada
    """
    token_str = request.data.get('token', '').strip()
    new_password = request.data.get('new_password', '').strip()

    if not token_str or not new_password:
        return Response(
            {'error': 'Token y nueva contraseña requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validar longitud mínima de contraseña
    if len(new_password) < 8:
        return Response(
            {'error': 'La contraseña debe tener al menos 8 caracteres'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Buscar token
        token = PasswordResetToken.objects.get(token=token_str)

        # Verificar validez
        if not token.is_valid():
            return Response(
                {'error': 'Token inválido o expirado. Solicita un nuevo enlace de recuperación.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Cambiar contraseña
        user = token.user
        user.set_password(new_password)
        user.save()

        # Marcar token como usado
        token.mark_as_used()

        print(f"[INFO] Contraseña restablecida para usuario: {user.username}")

        return Response({
            'success': True,
            'message': 'Contraseña actualizada exitosamente. Ya puedes iniciar sesión.'
        })

    except PasswordResetToken.DoesNotExist:
        return Response(
            {'error': 'Token inválido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        print(f"[ERROR] Error inesperado en confirm_password_reset: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': 'Error al procesar la solicitud'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def validate_reset_token(request):
    """
    Valida si un token de recuperación es válido.
    Útil para el frontend antes de mostrar el formulario de nueva contraseña.

    Query params:
        token: El token a validar

    Respuestas:
    - 200: { "valid": true, "username": "..." }
    - 200: { "valid": false, "error": "..." }
    """
    token_str = request.query_params.get('token', '').strip()

    if not token_str:
        return Response({
            'valid': False,
            'error': 'Token no proporcionado'
        })

    try:
        token = PasswordResetToken.objects.select_related('user').get(token=token_str)

        if token.is_valid():
            return Response({
                'valid': True,
                'username': token.user.username,
                'email': token.user.email[:3] + '***' + token.user.email[token.user.email.find('@'):] if token.user.email else None
            })
        else:
            return Response({
                'valid': False,
                'error': 'Token expirado o ya utilizado'
            })

    except PasswordResetToken.DoesNotExist:
        return Response({
            'valid': False,
            'error': 'Token inválido'
        })
