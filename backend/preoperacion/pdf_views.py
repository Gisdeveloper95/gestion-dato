import os
import mimetypes
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.conf import settings

# Importar utilidades de conversión de rutas
from backend.path_utils import windows_to_linux_path, linux_to_windows_path


def autenticar_por_token_query(request):
    """
    Autentica usuario por token en query param O header Authorization.
    """
    if hasattr(request, 'user') and request.user and request.user.is_authenticated:
        return request.user, None

    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Token '):
        token_str = auth_header[6:]
        try:
            token = Token.objects.select_related('user').get(key=token_str)
            if not token.user.is_active:
                return None, HttpResponse("Usuario inactivo", status=401)
            return token.user, None
        except Token.DoesNotExist:
            pass

    token_str = request.GET.get('token') or request.query_params.get('token')
    if not token_str:
        return None, HttpResponse("Token requerido", status=401)

    try:
        token = Token.objects.select_related('user').get(key=token_str)
        if not token.user.is_active:
            return None, HttpResponse("Usuario inactivo", status=401)
        return token.user, None
    except Token.DoesNotExist:
        return None, HttpResponse("Token inválido", status=401)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verificar_pdf(request):
    """Verifica si un archivo PDF existe en la ruta especificada"""
    ruta_pdf = request.data.get('ruta_pdf')

    if not ruta_pdf:
        return JsonResponse({'existe': False, 'error': 'No se proporcionó ruta'})

    # Convertir ruta de Windows a Linux si es necesario
    ruta_pdf = windows_to_linux_path(ruta_pdf)
    print(f"[verificar_pdf] Ruta después de conversión: {ruta_pdf}")

    # Verificar si es una ruta relativa o absoluta
    is_relative = not os.path.isabs(ruta_pdf)
    
    if is_relative:
        # Si es relativa, usar el directorio base configurado para PDFs
        base_dir = settings.NETWORK_SHARES.get('PDF_REPOSITORY', {}).get('path')
        if base_dir:
            ruta_completa = os.path.join(base_dir, ruta_pdf)
        else:
            return JsonResponse({'existe': False, 'error': 'No hay directorio base configurado para PDFs'})
    else:
        # Si es absoluta, usar directamente
        ruta_completa = ruta_pdf
    
    # Verificar si la ruta existe y es un archivo
    existe = os.path.isfile(ruta_completa)
    
    # También verificar si el archivo es un PDF (por la extensión)
    es_pdf = False
    if existe:
        _, extension = os.path.splitext(ruta_completa)
        es_pdf = extension.lower() == '.pdf'
    
    return JsonResponse({
        'existe': existe and es_pdf,
        'es_pdf': es_pdf,
        'ruta_utilizada': ruta_completa
    })



@api_view(['GET'])
@permission_classes([AllowAny])
def ver_pdf(request):
    """Envía cualquier tipo de archivo para visualización o descarga"""
    # Autenticar por token en query param O header (para window.open con barra de progreso)
    user, error_response = autenticar_por_token_query(request)
    if error_response:
        return error_response

    ruta_archivo = request.query_params.get('ruta')
    es_descarga = request.query_params.get('download', 'false').lower() == 'true'

    if not ruta_archivo:
        return HttpResponse("No se proporcionó ruta", status=400)

    # Convertir ruta de Windows a Linux si es necesario
    # Esto permite que el frontend envíe rutas tipo Windows y el backend las convierta
    ruta_archivo = windows_to_linux_path(ruta_archivo)
    print(f"[ver_pdf] Ruta después de conversión: {ruta_archivo}")

    # Normalizar ruta
    if not os.path.isabs(ruta_archivo):
        base_dir = settings.NETWORK_SHARES.get('PDF_REPOSITORY', {}).get('path')
        if base_dir:
            ruta_completa = os.path.join(base_dir, ruta_archivo)
        else:
            return HttpResponse("No hay directorio base configurado", status=500)
    else:
        ruta_completa = ruta_archivo
    
    # Verificar existencia
    if not os.path.isfile(ruta_completa):
        ruta_windows = linux_to_windows_path(ruta_completa)
        return HttpResponse(f"El archivo no existe: {ruta_windows}", status=404)

    # Detectar tipo de archivo
    _, extension = os.path.splitext(ruta_completa)
    extension_lower = extension.lower()
    
    # Determinar content-type
    content_type = 'application/octet-stream'  # Por defecto
    
    if extension_lower == '.pdf':
        content_type = 'application/pdf'
    elif extension_lower in ['.zip', '.rar', '.7z']:
        content_type = 'application/zip'
    elif extension_lower in ['.jpg', '.jpeg']:
        content_type = 'image/jpeg'
    elif extension_lower == '.png':
        content_type = 'image/png'
    elif extension_lower in ['.xls', '.xlsx']:
        content_type = 'application/vnd.ms-excel'
    elif extension_lower in ['.doc', '.docx']:
        content_type = 'application/msword'
    elif extension_lower in ['.shp', '.dbf', '.shx']:
        content_type = 'application/octet-stream'
    elif extension_lower == '.dwg':
        content_type = 'application/acad'
    elif extension_lower == '.dxf':
        content_type = 'application/dxf'
    elif extension_lower in ['.tif', '.tiff']:
        content_type = 'image/tiff'
    
    # Enviar archivo con STREAMING (FileResponse)
    try:
        filename = os.path.basename(ruta_completa)
        file_size = os.path.getsize(ruta_completa)

        # Usar FileResponse para streaming automático
        response = FileResponse(
            open(ruta_completa, 'rb'),
            content_type=content_type,
            as_attachment=(es_descarga or extension_lower != '.pdf'),
            filename=filename
        )

        # Si no es descarga y es PDF, mostrar inline
        if not es_descarga and extension_lower == '.pdf':
            response['Content-Disposition'] = f'inline; filename="{filename}"'

        # Headers para streaming
        response['Content-Length'] = file_size
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['X-Accel-Buffering'] = 'no'  # Desactivar buffering en nginx

        # CORS headers
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

        return response
    except Exception as e:
        return HttpResponse(f"Error al leer el archivo: {str(e)}", status=500)
     
"""
@api_view(['GET'])
def ver_pdf(request):

    ruta_pdf = request.query_params.get('ruta')
    token = request.query_params.get('token')
    es_descarga = request.query_params.get('download', False) == 'true'
    
    # Añadir logs para depuración
    print(f"Solicitud PDF recibida - Ruta: {ruta_pdf}, Descarga: {es_descarga}")
    
    if not ruta_pdf:
        return HttpResponse("No se proporcionó ruta", status=400)
        
    # Verificar si es una ruta relativa o absoluta
    is_relative = not os.path.isabs(ruta_pdf)
        
    if is_relative:
        # Si es relativa, usar el directorio base configurado para PDFs
        base_dir = settings.NETWORK_SHARES.get('PDF_REPOSITORY', {}).get('path')
        if base_dir:
            ruta_completa = os.path.join(base_dir, ruta_pdf)
        else:
            return HttpResponse("No hay directorio base configurado para PDFs", status=500)
    else:
        # Si es absoluta, usar directamente
        ruta_completa = ruta_pdf
        
        # Solo para rutas absolutas, verificar que esté en el directorio autorizado
        base_dir = settings.NETWORK_SHARES.get('PDF_REPOSITORY', {}).get('path')
        
        # Imprimir rutas para depuración
        print(f"Ruta base: {base_dir}")
        print(f"Ruta solicitada: {ruta_completa}")
        
        if base_dir:
            # No aplicar restricción si la ruta comienza con la base permitida
            if not ruta_completa.startswith(base_dir):
                print(f"Advertencia: La ruta {ruta_completa} está fuera del directorio base {base_dir}")
                # Comentado para pruebas: return HttpResponse("Acceso denegado: ruta no autorizada", status=403)
    
    # Verificar si la ruta existe y es un archivo
    print(f"Verificando existencia de archivo: {ruta_completa}")
    if not os.path.isfile(ruta_completa):
        ruta_windows = linux_to_windows_path(ruta_completa)
        return HttpResponse(f"El archivo no existe: {ruta_windows}", status=404)
        
    # Verificar si es un PDF
    _, extension = os.path.splitext(ruta_completa)
    if extension.lower() != '.pdf':
        return HttpResponse("El archivo no es un PDF", status=400)
        
    # Devolver el archivo como respuesta
    try:
        with open(ruta_completa, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            
            # Configurar cabeceras según si es descarga o visualización
            filename = os.path.basename(ruta_completa)
            if es_descarga:
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
            else:
                response['Content-Disposition'] = f'inline; filename="{filename}"'
                
            # Añadir cabeceras CORS para permitir visualización desde el frontend
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            
            return response
    except Exception as e:
        print(f"Error al leer el archivo: {str(e)}")
        return HttpResponse(f"Error al leer el archivo: {str(e)}", status=500)
    def is_safe_path(base_path, requested_path):

        # Normalizar rutas (usar os.path.realpath para resolver enlaces simbólicos)
        base_path = os.path.normpath(os.path.realpath(base_path))
        requested_path = os.path.normpath(os.path.realpath(requested_path))
        
        # Asegurarse de que la ruta base termine con separador
        if not base_path.endswith(os.sep):
            base_path += os.sep
        
        # Comprobar si la ruta solicitada está dentro de la ruta base
        return requested_path.startswith(base_path) or requested_path == base_path.rstrip(os.sep)
def is_safe_path(base_path, requested_path):

    # Normalizar rutas (usar os.path.realpath para resolver enlaces simbólicos)
    base_path = os.path.normpath(os.path.realpath(base_path))
    requested_path = os.path.normpath(os.path.realpath(requested_path))
    
    # Asegurarse de que la ruta base termine con separador
    if not base_path.endswith(os.sep):
        base_path += os.sep
    
    # Comprobar si la ruta solicitada está dentro de la ruta base
    return requested_path.startswith(base_path) or requested_path == base_path.rstrip(os.sep)


"""