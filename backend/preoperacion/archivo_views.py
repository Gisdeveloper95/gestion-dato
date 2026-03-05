# preoperacion/archivo_views.py
import os
import re
import zipfile
import tempfile
import mimetypes
from pathlib import Path
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.conf import settings
import shutil
import logging
from .views import get_municipios_permitidos
from preoperacion.models import ProfesionalesSeguimiento, ProfesionalMunicipio
from preoperacion.models import ListaArchivosPre
# Y si necesitas referencias a modelos de postoperación:
from postoperacion.models import ArchivosPost
# Importar utilidades de conversión de rutas
from backend.path_utils import linux_to_windows_path

logger = logging.getLogger(__name__)


def autenticar_por_token_query(request):
    """
    Autentica usuario por token en query param O header Authorization.
    Soporta ambos métodos para compatibilidad con:
    - window.open() con token en URL (barra de progreso del navegador)
    - axios/fetch con header Authorization (peticiones AJAX)
    """
    # Si ya está autenticado por header (DRF lo hace con AllowAny también si hay token), usar ese usuario
    if hasattr(request, 'user') and request.user and request.user.is_authenticated:
        return request.user, None

    # Intentar autenticar por header Authorization primero
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Token '):
        token_str = auth_header[6:]  # Quitar "Token "
        try:
            token = Token.objects.select_related('user').get(key=token_str)
            if not token.user.is_active:
                return None, HttpResponse("Usuario inactivo", status=401)
            return token.user, None
        except Token.DoesNotExist:
            pass  # Continuar con query param

    # Intentar autenticar por query param (para window.open)
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


# Mapeo de extensiones agrupadas MEJORADO
EXTENSIONES_AGRUPAR = {
    'geodatabase': ['.gdb', '.mdb', '.sde'],
    'shapefile': ['.shp', '.shx', '.dbf', '.prj', '.sbn', '.sbx', '.cpg', '.qix', '.fix'],
    'imagen_compleja': ['.tif', '.tiff', '.tfw', '.jgw', '.xml', '.aux', '.ovr', 
                       '.pyr', '.rdx', '.tif.aux.xml', '.tif.ovr', '.tif.xml'],
    'cad': ['.dwg', '.dxf', '.dgn', '.bak', '.dng', '.dwl', '.dwl2']
}

# Extensiones que requieren descarga de directorio completo
DESCARGAR_DIRECTORIO_COMPLETO = ['.tif', '.tiff', '.gdb']

def extraer_municipio_de_ruta(ruta):
    """Extrae el código de municipio de una ruta de archivo"""
    # Buscar el patrón después de 01_actualiz_catas\
    regex = r'01_actualiz_catas[/\\](\d+)[/\\](\d+)[/\\]'
    match = re.search(regex, ruta)
    
    if match and match.group(1) and match.group(2):
        # Combinar código de departamento y municipio
        cod_depto = match.group(1)
        cod_muni = match.group(2)
        
        # Formato de código completo: DDDMMM (ej: 05001)
        codigo_municipio = int(f"{cod_depto}{cod_muni}")
        return codigo_municipio
    
    return None

def detectar_tipo_agrupacion(archivo_path):
    """Detecta si un archivo pertenece a un grupo de extensiones"""
    extension = Path(archivo_path).suffix.lower()
    nombre_base = Path(archivo_path).stem
    
    for grupo, extensiones in EXTENSIONES_AGRUPAR.items():
        if extension in extensiones:
            return grupo, nombre_base
    
    return None, None

def obtener_archivos_relacionados(archivo_path):
    """Obtiene todos los archivos relacionados para un archivo agrupado"""
    extension = Path(archivo_path).suffix.lower()
    
    logger.info(f"🔍 Procesando archivo: {archivo_path}")
    logger.info(f"📁 Extensión detectada: {extension}")
    
    # Para .tif/.tiff, descargar todo el directorio padre
    if extension in ['.tif', '.tiff']:
        directorio_padre = os.path.dirname(archivo_path)
        logger.info(f"🖼️ Archivo TIF detectado - Directorio padre: {directorio_padre}")
        
        if os.path.isdir(directorio_padre):
            return [directorio_padre]
        else:
            logger.warning(f"⚠️ Directorio padre no existe: {directorio_padre}")
            return [archivo_path]
    
    # Para .gdb, manejar como directorio
    elif extension == '.gdb':
        logger.info(f"🗄️ Geodatabase detectada: {archivo_path}")
        
        # Verificar si la ruta ya es un directorio
        if os.path.isdir(archivo_path):
            logger.info(f"✅ GDB es directorio válido: {archivo_path}")
            return [archivo_path]
        else:
            # Si no es directorio, buscar directorio con nombre similar
            directorio_gdb = archivo_path
            logger.warning(f"⚠️ GDB no es directorio, intentando como ruta: {directorio_gdb}")
            
            if os.path.exists(directorio_gdb) and os.path.isdir(directorio_gdb):
                return [directorio_gdb]
            else:
                # Intentar sin extensión
                directorio_sin_ext = os.path.splitext(archivo_path)[0]
                if os.path.exists(directorio_sin_ext) and os.path.isdir(directorio_sin_ext):
                    return [directorio_sin_ext]
                else:
                    logger.error(f"❌ No se puede acceder a la geodatabase: {archivo_path}")
                    raise FileNotFoundError(f"La geodatabase no es accesible: {archivo_path}")
    
    # Para otros tipos agrupados (shapefiles, CAD, etc.)
    else:
        grupo, nombre_base = detectar_tipo_agrupacion(archivo_path)
        if not grupo:
            logger.info(f"📄 Archivo individual: {archivo_path}")
            return [archivo_path]
        
        directorio = os.path.dirname(archivo_path)
        archivos_relacionados = []
        
        logger.info(f"🔗 Buscando archivos relacionados para {grupo}: {nombre_base}")
        
        if os.path.exists(directorio):
            extensiones_grupo = EXTENSIONES_AGRUPAR.get(grupo, [])
            
            for archivo in os.listdir(directorio):
                archivo_path_completo = os.path.join(directorio, archivo)
                archivo_stem = Path(archivo).stem
                archivo_ext = Path(archivo).suffix.lower()
                
                if archivo_stem.lower() == nombre_base.lower() and archivo_ext in extensiones_grupo:
                    if os.path.isfile(archivo_path_completo):
                        archivos_relacionados.append(archivo_path_completo)
        
        logger.info(f"📦 Archivos relacionados encontrados: {len(archivos_relacionados)}")
        return archivos_relacionados if archivos_relacionados else [archivo_path]

def crear_zip_streaming_optimizado(archivos_o_directorios, nombre_base="descarga"):
    """Genera un ZIP en streaming optimizado para archivos grandes"""
    def generar():
        buffer_size = 1024 * 1024  # 1MB chunks
        
        with tempfile.NamedTemporaryFile(mode='w+b', delete=False) as tmp_file:
            try:
                with zipfile.ZipFile(tmp_file, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
                    for item_path in archivos_o_directorios:
                        logger.info(f"📂 Agregando al ZIP: {item_path}")
                        
                        if os.path.isdir(item_path):
                            # Si es un directorio, agregar todos sus archivos recursivamente
                            base_name = os.path.basename(item_path)
                            
                            for root, dirs, files in os.walk(item_path):
                                # Agregar directorios vacíos
                                rel_dir = os.path.relpath(root, item_path)
                                if rel_dir != '.':
                                    dir_arcname = os.path.join(base_name, rel_dir).replace('\\', '/') + '/'
                                    zf.writestr(zipfile.ZipInfo(dir_arcname), '')
                                
                                # Agregar archivos
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    if os.path.isfile(file_path):
                                        rel_path = os.path.relpath(file_path, item_path)
                                        arcname = os.path.join(base_name, rel_path).replace('\\', '/')
                                        
                                        try:
                                            zf.write(file_path, arcname)
                                            logger.debug(f"✅ Archivo agregado: {arcname}")
                                        except Exception as e:
                                            logger.warning(f"⚠️ Error agregando archivo {file_path}: {e}")
                        
                        elif os.path.isfile(item_path):
                            # Si es un archivo individual
                            zf.write(item_path, os.path.basename(item_path))
                            logger.debug(f"📄 Archivo individual agregado: {os.path.basename(item_path)}")
                
                # Finalizar el ZIP
                tmp_file.flush()
                tmp_file.seek(0)
                
                logger.info("📦 ZIP creado exitosamente, iniciando streaming...")
                
                # Leer y enviar el archivo en chunks grandes
                while True:
                    chunk = tmp_file.read(buffer_size)
                    if not chunk:
                        break
                    yield chunk
                    
            finally:
                # Limpiar archivo temporal
                try:
                    os.unlink(tmp_file.name)
                    logger.debug("🗑️ Archivo temporal eliminado")
                except:
                    pass
    
    return generar()
@api_view(['GET'])
@permission_classes([AllowAny])
def descargar_archivo(request):
    """Descarga archivos individuales o crea ZIPs para archivos agrupados"""
    # Autenticar por token en query param (para window.open con barra de progreso)
    user, error_response = autenticar_por_token_query(request)
    if error_response:
        return error_response

    ruta_archivo = request.query_params.get('ruta')
    forzar_individual = request.query_params.get('individual', 'false').lower() == 'true'
    if not ruta_archivo:
        return HttpResponse("No se proporcionó ruta", status=400)

    # Verificar permisos según el rol del usuario
    es_admin = user.is_staff or user.is_superuser or user.groups.filter(name='Administradores').exists()

    # Los administradores tienen acceso a todo
    if not es_admin:
        # Para profesionales, verificar municipios asignados
        try:
            # Buscar profesional asociado al usuario
            profesional = ProfesionalesSeguimiento.objects.get(cod_profesional=user.username)
            
            # Obtener lista de municipios asignados
            municipios_permitidos = list(ProfesionalMunicipio.objects.filter(
                cod_profesional=profesional
            ).values_list('cod_municipio', flat=True))
            
            # Si no tiene municipios asignados, denegar acceso
            if not municipios_permitidos:
                return HttpResponse("No tiene municipios asignados para acceder a archivos", status=403)
            
            # Verificar si la ruta pertenece a alguno de sus municipios
            municipio_ruta = extraer_municipio_de_ruta(ruta_archivo)
            
            # Si no se pudo extraer el municipio, intentar buscar en base de datos
            if not municipio_ruta:
                # Buscar en archivos pre-operacionales
                archivo_pre = ListaArchivosPre.objects.filter(
                    path_file=ruta_archivo
                ).first()
                
                if archivo_pre:
                    # Obtener el municipio a través de las relaciones
                    insumo = archivo_pre.cod_insumo
                    municipio_id = insumo.cod_insumo.cod_municipio.cod_municipio
                    municipio_ruta = municipio_id
                else:
                    # Buscar en archivos post-operacionales
                    from postoperacion.models import ArchivosPost
                    archivo_post = ArchivosPost.objects.filter(
                        ruta_completa=ruta_archivo
                    ).first()
                    
                    if archivo_post:
                        municipio_id = archivo_post.id_disposicion.cod_municipio.cod_municipio
                        municipio_ruta = municipio_id
            
            # Si no se encontró el municipio, denegar acceso
            if not municipio_ruta or municipio_ruta not in municipios_permitidos:
                return HttpResponse("No tiene permisos para acceder a este archivo", status=403)
                
        except ProfesionalesSeguimiento.DoesNotExist:
            # Si el usuario no es un profesional registrado, denegar acceso
            return HttpResponse("Usuario no tiene rol asignado para acceder a archivos", status=403)
        except Exception as e:
            # Cualquier otro error, log y denegar acceso
            print(f"Error verificando permisos: {str(e)}")
            return HttpResponse("Error verificando permisos de acceso", status=403)
    
    print(f"DEBUG DESCARGA - Ruta normalizada: {ruta_archivo}")
    logger.info(f"🚀 Solicitud de descarga pública: {ruta_archivo}")
    
    # Obtener información del archivo
    nombre_archivo = os.path.basename(ruta_archivo)
    extension = Path(ruta_archivo).suffix.lower()
    
    logger.info(f"📄 Archivo: {nombre_archivo}, Extensión: {extension}")
    
    # Verificación especial para .gdb
    if extension == '.gdb':
        if not os.path.isdir(ruta_archivo):
            logger.error(f"❌ Geodatabase no accesible: {ruta_archivo}")
            ruta_windows = linux_to_windows_path(ruta_archivo)
            return HttpResponse(f"La geodatabase no es accesible: {ruta_windows}", status=404)
    else:
        # Para otros archivos, verificar existencia normal
        if not os.path.exists(ruta_archivo):
            logger.error(f"❌ Archivo no existe: {ruta_archivo}")
            ruta_windows = linux_to_windows_path(ruta_archivo)
            return HttpResponse(f"El archivo no existe: {ruta_windows}", status=404)
    
    # Si es PDF, servir directamente como descarga
    if extension == '.pdf':
        logger.info("📋 Archivo PDF - sirviendo como descarga")
        try:
            filename = os.path.basename(ruta_archivo)
            file_size = os.path.getsize(ruta_archivo)

            response = FileResponse(
                open(ruta_archivo, 'rb'),
                content_type='application/pdf',
                as_attachment=True,
                filename=filename
            )
            response['Content-Length'] = file_size
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            logger.error(f"❌ Error sirviendo PDF: {e}")
            return HttpResponse(f"Error al descargar PDF: {str(e)}", status=500)
    
    # Detectar si requiere manejo especial
    grupo, nombre_base = detectar_tipo_agrupacion(ruta_archivo)
    requiere_zip = extension in DESCARGAR_DIRECTORIO_COMPLETO or grupo is not None
    
    logger.info(f"🔍 Grupo detectado: {grupo}, Requiere ZIP: {requiere_zip}")
    
    if requiere_zip and not forzar_individual:
        try:
            # Obtener archivos/directorios a comprimir
            items_a_comprimir = obtener_archivos_relacionados(ruta_archivo)
            
            if not items_a_comprimir:
                return HttpResponse("No se encontraron archivos para comprimir", status=404)
            
            # Verificar que todos los items existen
            items_validos = []
            for item in items_a_comprimir:
                if os.path.exists(item):
                    items_validos.append(item)
                    logger.info(f"✅ Item válido: {item}")
                else:
                    logger.warning(f"⚠️ Item no encontrado: {item}")
            
            if not items_validos:
                return HttpResponse("No se encontraron archivos válidos para comprimir", status=404)
            
            # Determinar nombre del ZIP
            if extension in ['.tif', '.tiff']:
                directorio_nombre = os.path.basename(os.path.dirname(ruta_archivo))
                nombre_zip = f"{directorio_nombre}_ortofotos_completo.zip"
            elif extension == '.gdb':
                nombre_zip = f"{nombre_base}_geodatabase.zip"
            else:
                nombre_zip = f"{nombre_base}_{grupo}.zip"
            
            logger.info(f"📦 Creando ZIP: {nombre_zip}")
            
            # Crear respuesta de streaming
            response = StreamingHttpResponse(
                crear_zip_streaming_optimizado(items_validos, nombre_base),
                content_type='application/zip'
            )
            
            # Headers para descarga inmediata
            response['Content-Disposition'] = f'attachment; filename="{nombre_zip}"'
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['X-Accel-Buffering'] = 'no'  # Para nginx
            
            # Headers CORS
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response["Access-Control-Expose-Headers"] = "Content-Disposition"
            
            logger.info(f"✅ Descarga ZIP pública iniciada: {nombre_zip}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error creando ZIP: {str(e)}")
            return HttpResponse(f"Error al crear el archivo ZIP: {str(e)}", status=500)
    
    else:
        # Para archivos individuales normales - SIEMPRE usar FileResponse para streaming
        try:
            # Detectar tipo MIME
            content_type, _ = mimetypes.guess_type(ruta_archivo)
            if not content_type:
                content_type = 'application/octet-stream'

            # Obtener tamaño del archivo
            file_size = os.path.getsize(ruta_archivo)

            logger.info(f"📄 Descarga individual pública: {nombre_archivo} ({file_size} bytes)")

            # Usar FileResponse para streaming automático (sin umbral de tamaño)
            response = FileResponse(
                open(ruta_archivo, 'rb'),
                content_type=content_type,
                as_attachment=True,
                filename=nombre_archivo
            )

            # Headers para descarga
            response['Content-Length'] = file_size
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['X-Accel-Buffering'] = 'no'  # Desactivar buffering en nginx

            # Headers CORS
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response["Access-Control-Expose-Headers"] = "Content-Disposition, Content-Length"

            logger.info(f"✅ Descarga streaming iniciada: {nombre_archivo}")
            return response

        except Exception as e:
            logger.error(f"❌ Error leyendo archivo: {str(e)}")
            return HttpResponse(f"Error al leer el archivo: {str(e)}", status=500)

def verificar_permiso_archivo(ruta_archivo, municipios_permitidos):
    """
    Verifica si un archivo pertenece a los municipios permitidos del usuario
    """
    try:
        # Buscar en archivos pre-operacionales
        archivo_pre = ListaArchivosPre.objects.filter(
            path_file=ruta_archivo
        ).first()
        
        if archivo_pre:
            municipio_archivo = archivo_pre.cod_insumo.cod_insumo.cod_municipio.cod_municipio
            return municipio_archivo in municipios_permitidos
        
        # Buscar en archivos post-operacionales
        archivo_post = ArchivosPost.objects.filter(
            ruta_completa=ruta_archivo
        ).first()
        
        if archivo_post:
            municipio_archivo = archivo_post.id_disposicion.cod_municipio.cod_municipio
            return municipio_archivo in municipios_permitidos
        
        return False
    except:
        return False


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verificar_archivo(request):
    """Verifica si un archivo existe y devuelve información sobre él"""
    ruta_archivo = request.query_params.get('ruta')
    
    if not ruta_archivo:
        return JsonResponse({'existe': False, 'error': 'No se proporcionó ruta'})
    
    # Normalizar ruta
    if not os.path.isabs(ruta_archivo):
        base_dir = settings.NETWORK_SHARES.get('REPOSITORY_BASE', {}).get('path', '')
        if not base_dir:
            base_dir = r'\\repositorio\DirGesCat'
        ruta_archivo = os.path.join(base_dir, ruta_archivo)
    
    extension = Path(ruta_archivo).suffix.lower()
    
    # Verificación especial para .gdb
    if extension == '.gdb':
        existe = os.path.isdir(ruta_archivo)
        es_directorio = True
    else:
        existe = os.path.exists(ruta_archivo)
        es_directorio = os.path.isdir(ruta_archivo) if existe else False
    
    info = {
        'existe': existe,
        'es_directorio': es_directorio,
        'ruta_utilizada': ruta_archivo
    }
    
    if existe:
        grupo, _ = detectar_tipo_agrupacion(ruta_archivo)
        
        info.update({
            'extension': extension,
            'es_agrupado': grupo is not None or extension in DESCARGAR_DIRECTORIO_COMPLETO,
            'tipo_agrupacion': grupo,
            'requiere_zip': extension in DESCARGAR_DIRECTORIO_COMPLETO or grupo is not None
        })
        
        if not es_directorio:
            try:
                info['tamaño'] = os.path.getsize(ruta_archivo)
            except:
                info['tamaño'] = 0
        
        # Información sobre qué se descargará
        if extension in ['.tif', '.tiff']:
            info['metodo_descarga'] = 'directorio_completo'
            info['descripcion'] = 'Se descargará el directorio completo como ZIP'
        elif extension == '.gdb':
            info['metodo_descarga'] = 'geodatabase_completa'
            info['descripcion'] = 'Se descargará la geodatabase completa como ZIP'
        elif grupo:
            info['metodo_descarga'] = 'archivos_relacionados'
            info['descripcion'] = f'Se descargarán los archivos {grupo} relacionados como ZIP'
        else:
            info['metodo_descarga'] = 'archivo_individual'
            info['descripcion'] = 'Se descargará el archivo individual'
    
    return JsonResponse(info)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def preview_descarga(request):
    """Obtiene una vista previa de qué archivos se incluirán en la descarga"""
    ruta_archivo = request.query_params.get('ruta')
    
    if not ruta_archivo:
        return JsonResponse({'error': 'No se proporcionó ruta'}, status=400)
    
    # Normalizar ruta
    if not os.path.isabs(ruta_archivo):
        base_dir = settings.NETWORK_SHARES.get('REPOSITORY_BASE', {}).get('path', '')
        if not base_dir:
            base_dir = r'\\repositorio\DirGesCat'
        ruta_archivo = os.path.join(base_dir, ruta_archivo)
    
    extension = Path(ruta_archivo).suffix.lower()
    
    # Verificación especial para .gdb
    if extension == '.gdb':
        if not os.path.isdir(ruta_archivo):
            ruta_windows = linux_to_windows_path(ruta_archivo)
            return JsonResponse({'error': f'La geodatabase no existe: {ruta_windows}'}, status=404)
    else:
        if not os.path.exists(ruta_archivo):
            ruta_windows = linux_to_windows_path(ruta_archivo)
            return JsonResponse({'error': f'El archivo no existe: {ruta_windows}'}, status=404)

    try:
        items_a_descargar = obtener_archivos_relacionados(ruta_archivo)
        archivos_info = []
        total_size = 0
        
        for item in items_a_descargar:
            if os.path.isdir(item):
                # Contar archivos en el directorio
                dir_info = {
                    'tipo': 'directorio',
                    'ruta': item,
                    'nombre': os.path.basename(item),
                    'archivos': []
                }
                
                for root, dirs, files in os.walk(item):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            file_size = os.path.getsize(file_path)
                            total_size += file_size
                            
                            rel_path = os.path.relpath(file_path, item)
                            dir_info['archivos'].append({
                                'nombre': file,
                                'ruta_relativa': rel_path,
                                'tamaño': file_size
                            })
                        except:
                            # Si no se puede acceder al archivo, omitirlo
                            pass
                
                archivos_info.append(dir_info)
            
            elif os.path.isfile(item):
                try:
                    file_size = os.path.getsize(item)
                    total_size += file_size
                    
                    archivos_info.append({
                        'tipo': 'archivo',
                        'nombre': os.path.basename(item),
                        'ruta': item,
                        'tamaño': file_size
                    })
                except:
                    pass
        
        return JsonResponse({
            'archivos': archivos_info,
            'total_archivos': sum(len(info.get('archivos', [1])) for info in archivos_info),
            'tamaño_total': total_size,
            'tamaño_total_mb': round(total_size / (1024 * 1024), 2)
        })
        
    except Exception as e:
        logger.error(f"Error en preview: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


# ============================================================================
# NUEVOS ENDPOINTS PARA DESCARGA MÚLTIPLE Y DE DIRECTORIOS
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def descargar_multiples(request):
    """
    Descarga múltiples archivos y/o directorios como un único ZIP.

    Request body:
    {
        "archivos": [
            "/mnt/repositorio/.../file1.pdf",
            "/mnt/repositorio/.../file2.shp",
            "/mnt/repositorio/.../directory.gdb"
        ],
        "nombre_zip": "descarga_seleccion"  // opcional
    }
    """
    import json

    try:
        # Obtener datos del request
        archivos = request.data.get('archivos', [])
        nombre_zip = request.data.get('nombre_zip', 'descarga_multiple')

        if not archivos:
            return HttpResponse("No se proporcionaron archivos para descargar", status=400)

        # Límite máximo de archivos
        MAX_FILES = 500
        if len(archivos) > MAX_FILES:
            return HttpResponse(f"Máximo {MAX_FILES} archivos permitidos por descarga", status=400)

        # Verificar permisos según el rol del usuario
        es_admin = (
            request.user.is_staff or
            request.user.is_superuser or
            request.user.groups.filter(name='Administradores').exists()
        )

        municipios_permitidos = []
        if not es_admin:
            try:
                profesional = ProfesionalesSeguimiento.objects.get(cod_profesional=request.user.username)
                municipios_permitidos = list(ProfesionalMunicipio.objects.filter(
                    cod_profesional=profesional
                ).values_list('cod_municipio', flat=True))

                if not municipios_permitidos:
                    return HttpResponse("No tiene municipios asignados para acceder a archivos", status=403)
            except ProfesionalesSeguimiento.DoesNotExist:
                return HttpResponse("Usuario no tiene rol asignado para acceder a archivos", status=403)

        # Validar y filtrar archivos
        items_validos = []
        items_sin_permiso = []
        items_no_encontrados = []

        for ruta in archivos:
            if not ruta:
                continue

            # Verificar existencia
            if not os.path.exists(ruta):
                items_no_encontrados.append(ruta)
                continue

            # Verificar permisos (solo para no-admins)
            if not es_admin:
                municipio_ruta = extraer_municipio_de_ruta(ruta)
                if municipio_ruta and municipio_ruta not in municipios_permitidos:
                    items_sin_permiso.append(ruta)
                    continue

            items_validos.append(ruta)

        if not items_validos:
            mensaje = "No se encontraron archivos válidos para descargar."
            if items_no_encontrados:
                mensaje += f" {len(items_no_encontrados)} archivos no existen."
            if items_sin_permiso:
                mensaje += f" {len(items_sin_permiso)} archivos sin permisos."
            return HttpResponse(mensaje, status=404)

        logger.info(f"📦 Descarga múltiple: {len(items_validos)} items válidos, {len(items_no_encontrados)} no encontrados")

        # Crear nombre del ZIP con sanitización
        nombre_zip_safe = "".join(c for c in nombre_zip if c.isalnum() or c in '_-').strip()
        if not nombre_zip_safe:
            nombre_zip_safe = 'descarga_multiple'
        nombre_zip_final = f"{nombre_zip_safe}.zip"

        # Crear respuesta streaming
        response = StreamingHttpResponse(
            crear_zip_streaming_optimizado(items_validos, nombre_zip_safe),
            content_type='application/zip'
        )

        response['Content-Disposition'] = f'attachment; filename="{nombre_zip_final}"'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        response['X-Accel-Buffering'] = 'no'
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response["Access-Control-Expose-Headers"] = "Content-Disposition"

        logger.info(f"✅ Descarga múltiple iniciada: {nombre_zip_final} ({len(items_validos)} items)")
        return response

    except Exception as e:
        logger.error(f"❌ Error en descarga múltiple: {str(e)}")
        return HttpResponse(f"Error al crear la descarga: {str(e)}", status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def descargar_directorio(request):
    """
    Descarga cualquier directorio como ZIP.

    Query params:
    - ruta: Ruta del directorio a descargar (puede ser absoluta o relativa)
    - municipio_id: (opcional) ID del municipio para construir ruta si es relativa
    - token: Token de autenticación (para window.open con barra de progreso)
    """
    # Autenticar por token en query param
    user, error_response = autenticar_por_token_query(request)
    if error_response:
        return error_response

    ruta_directorio = request.query_params.get('ruta')
    municipio_id = request.query_params.get('municipio_id')

    if not ruta_directorio:
        return HttpResponse("No se proporcionó ruta del directorio", status=400)

    # Si la ruta ya contiene la estructura del repositorio, agregar solo /mnt/repositorio
    if ruta_directorio.startswith('2510SP/'):
        base_path = os.environ.get('REPOSITORY_BASE_PATH', '/mnt/repositorio')
        ruta_directorio = os.path.join(base_path, ruta_directorio)
        logger.info(f"📁 Ruta con prefijo 2510SP detectada: {ruta_directorio}")
    # Si la ruta no es absoluta, construir usando municipio_id
    elif not ruta_directorio.startswith('/mnt/repositorio') and not ruta_directorio.startswith('/'):
        if municipio_id:
            try:
                municipio_str = str(municipio_id).zfill(5)
                depto = municipio_str[:2]
                muni = municipio_str[2:5]
                base_path = os.environ.get('REPOSITORY_BASE_PATH', '/mnt/repositorio')

                # Detectar el tipo de carpeta para construir la ruta correcta
                # Estructura del repositorio:
                # - 01_actualiz_catas/{depto}/{muni}/PGN/{subdirectorio} (Pre-operación)
                # - 02_oper/{depto}/{muni}/{subdirectorio} (Operación)
                # - 03_post_oper/{depto}/{muni}/{subdirectorio} (Post-operación)
                # - 04_hseq/{depto}/{muni}/{subdirectorio} (HSEQ)
                # - 05_trans/{depto}/{muni}/{subdirectorio} (Transversal)

                carpetas_principales = ['02_oper', '03_post_oper', '04_hseq', '05_trans']

                # Verificar si la ruta empieza con alguna carpeta principal
                ruta_empieza_con_carpeta = None
                for carpeta in carpetas_principales:
                    if ruta_directorio.startswith(f'{carpeta}/') or ruta_directorio == carpeta:
                        ruta_empieza_con_carpeta = carpeta
                        break

                if ruta_empieza_con_carpeta:
                    # Para Operación, Post-operación, HSEQ, Transversal
                    # Extraer la ruta después de la carpeta principal
                    if ruta_directorio == ruta_empieza_con_carpeta:
                        resto_ruta = ''
                    else:
                        resto_ruta = ruta_directorio[len(ruta_empieza_con_carpeta) + 1:]

                    ruta_directorio = os.path.join(
                        base_path,
                        '2510SP/H_Informacion_Consulta/Sub_Proy',
                        ruta_empieza_con_carpeta,
                        depto,
                        muni,
                        resto_ruta
                    )
                else:
                    # Para Pre-operación (ruta original)
                    ruta_directorio = os.path.join(
                        base_path,
                        '2510SP/H_Informacion_Consulta/Sub_Proy/01_actualiz_catas',
                        depto,
                        muni,
                        'PGN',
                        ruta_directorio
                    )

                logger.info(f"📁 Ruta construida para descarga: {ruta_directorio}")
            except Exception as e:
                logger.error(f"❌ Error construyendo ruta: {e}")
                return HttpResponse(f"Error construyendo ruta del directorio", status=400)
        else:
            return HttpResponse(f"Ruta relativa proporcionada sin municipio_id", status=400)

    # Verificar que es un directorio
    if not os.path.isdir(ruta_directorio):
        return HttpResponse(f"La ruta no es un directorio válido: {ruta_directorio}", status=400)

    # Verificar permisos según el rol del usuario
    es_admin = (
        user.is_staff or
        user.is_superuser or
        user.groups.filter(name='Administradores').exists()
    )

    if not es_admin:
        try:
            profesional = ProfesionalesSeguimiento.objects.get(cod_profesional=user.username)
            municipios_permitidos = list(ProfesionalMunicipio.objects.filter(
                cod_profesional=profesional
            ).values_list('cod_municipio', flat=True))

            if not municipios_permitidos:
                return HttpResponse("No tiene municipios asignados para acceder a archivos", status=403)

            municipio_ruta = extraer_municipio_de_ruta(ruta_directorio)
            if municipio_ruta and municipio_ruta not in municipios_permitidos:
                return HttpResponse("No tiene permisos para acceder a este directorio", status=403)

        except ProfesionalesSeguimiento.DoesNotExist:
            return HttpResponse("Usuario no tiene rol asignado para acceder a archivos", status=403)

    try:
        # Verificar tamaño total (límite 50GB)
        MAX_SIZE = 50 * 1024 * 1024 * 1024  # 50GB en bytes
        total_size = 0

        for root, dirs, files in os.walk(ruta_directorio):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)

                    if total_size > MAX_SIZE:
                        return HttpResponse(
                            f"El directorio excede el límite de 50GB ({total_size / (1024*1024*1024):.2f} GB)",
                            status=413
                        )
                except (OSError, FileNotFoundError):
                    continue

        # Nombre del ZIP basado en el directorio
        nombre_directorio = os.path.basename(ruta_directorio) or 'directorio'
        nombre_zip = f"{nombre_directorio}.zip"

        logger.info(f"📁 Descarga directorio: {ruta_directorio} ({total_size / (1024*1024):.2f} MB)")

        # Crear respuesta streaming
        response = StreamingHttpResponse(
            crear_zip_streaming_optimizado([ruta_directorio], nombre_directorio),
            content_type='application/zip'
        )

        response['Content-Disposition'] = f'attachment; filename="{nombre_zip}"'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        response['X-Accel-Buffering'] = 'no'
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response["Access-Control-Expose-Headers"] = "Content-Disposition"

        logger.info(f"✅ Descarga directorio iniciada: {nombre_zip}")
        return response

    except Exception as e:
        logger.error(f"❌ Error descargando directorio: {str(e)}")
        return HttpResponse(f"Error al descargar el directorio: {str(e)}", status=500)