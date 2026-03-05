from django.utils import timezone
from .models import Auditoria, Usuarios

def registrar_auditoria(request, tipo_entidad, id_entidad, accion, detalles=None):
    """
    Registra un evento de auditoría en el sistema
    
    Args:
        request: objeto HttpRequest
        tipo_entidad: string que indica el tipo de entidad ('detalle', 'concepto', etc.)
        id_entidad: ID de la entidad a la que se refiere la acción
        accion: string que indica la acción realizada ('crear', 'actualizar', 'eliminar', 'consultar')
        detalles: diccionario con información adicional sobre la acción (opcional)
    
    Returns:
        Instancia de Auditoria creada, o None si hubo un error
    """
    try:
        # Determinar el usuario
        usuario = None
        if request.user.is_authenticated:
            try:
                # Intentar encontrar usuario por correo electrónico
                usuario = Usuarios.objects.get(correo=request.user.email)
            except Usuarios.DoesNotExist:
                # Intentar por username
                try:
                    usuario = Usuarios.objects.filter(nombre__icontains=request.user.username).first()
                except:
                    pass
        
        # Obtener la IP del cliente
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_origen = x_forwarded_for.split(',')[0].strip()
        else:
            ip_origen = request.META.get('REMOTE_ADDR')
        
        # Crear el registro de auditoría
        auditoria = Auditoria.objects.create(
            usuario=usuario,
            fecha_hora=timezone.now(),
            tipo_entidad=tipo_entidad,
            id_entidad=id_entidad,
            accion=accion,
            detalles=detalles,
            ip_origen=ip_origen
        )
        
        return auditoria
        
    except Exception as e:
        # Registrar error en consola pero no interrumpir el flujo principal
        print(f"Error al registrar auditoría: {str(e)}")
        return None