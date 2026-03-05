import os
import mimetypes
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
import logging

# Importar utilidades de conversión de rutas
from backend.path_utils import windows_to_linux_path, linux_to_windows_path

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verificar_pdf(request):
    """Verifica si un archivo PDF existe en la ruta especificada - POST-OPERACIÓN"""
    ruta_pdf = request.data.get('ruta_pdf')

    if not ruta_pdf:
        return JsonResponse({'existe': False, 'error': 'No se proporcionó ruta'})

    # Usar función centralizada para convertir ruta de Windows a Linux
    ruta_pdf = windows_to_linux_path(ruta_pdf)
    logger.info(f"[verificar_pdf POST] Ruta después de conversión: {ruta_pdf}")

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

    logger.info(f"Verificación PDF: {ruta_completa} - Existe: {existe}, Es PDF: {es_pdf}")

    return JsonResponse({
        'existe': existe and es_pdf,
        'es_pdf': es_pdf,
        'ruta_utilizada': ruta_completa
    })



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ver_pdf(request):
    """Envía cualquier tipo de archivo para visualización o descarga - POST-OPERACIÓN"""
    ruta_archivo = request.query_params.get('ruta')
    token = request.query_params.get('token')
    es_descarga = request.query_params.get('download', 'false').lower() == 'true'

    logger.info(f"Solicitud ver_pdf POST - Ruta: {ruta_archivo}, Descarga: {es_descarga}")

    if not ruta_archivo:
        return HttpResponse("No se proporcionó ruta", status=400)

    # Usar función centralizada para convertir ruta de Windows a Linux
    ruta_archivo = windows_to_linux_path(ruta_archivo)
    logger.info(f"[ver_pdf POST] Ruta después de conversión: {ruta_archivo}")

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
        logger.error(f"❌ Archivo no existe: {ruta_completa}")
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

        logger.info(f"✅ Archivo streaming iniciado: {filename} ({content_type}, {file_size} bytes)")
        return response
    except Exception as e:
        logger.error(f"❌ Error al leer archivo: {str(e)}")
        return HttpResponse(f"Error al leer el archivo: {str(e)}", status=500)
