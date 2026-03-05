# postoperacion/archivo_views.py
import os
import re
import zipfile
import tempfile
import mimetypes
from pathlib import Path
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from preoperacion.auth import ExpiringTokenAuthentication
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.conf import settings
import shutil
import logging
from preoperacion.models import ProfesionalesSeguimiento, ProfesionalMunicipio, Municipios
from postoperacion.models import ArchivosPost, AuditoriaArchivos, DisposicionPost, EvaluacionArchivosPost
from django.utils import timezone
from datetime import date
import hashlib

# ✅ AGREGADO: Importar validadores seguros
from app.validadores_parametros import PathParameterValidator, BooleanParameterValidator
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


def get_client_ip(request):
    """Obtiene la IP del cliente desde el request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ============================================================================
# EXTENSIONES PELIGROSAS BLOQUEADAS PARA UPLOAD
# ============================================================================
EXTENSIONES_BLOQUEADAS = [
    '.exe', '.bat', '.cmd', '.com', '.msi', '.scr',
    '.vbs', '.js', '.ps1', '.dll', '.sh', '.bin',
    '.app', '.jar', '.pif', '.gadget', '.wsf', '.wsh',
    '.hta', '.cpl', '.msc', '.lnk', '.inf', '.reg',
    '.scf', '.msp', '.chm', '.hlp', '.sys', '.drv'
]

# Tamaño máximo de archivo: 2500 MB
MAX_UPLOAD_SIZE = 2500 * 1024 * 1024

# Mapeo de extensiones agrupadas
EXTENSIONES_AGRUPAR = {
    'geodatabase': ['.gdb', '.mdb', '.sde'],
    'shapefile': ['.shp', '.shx', '.dbf', '.prj', '.sbn', '.sbx', '.cpg', '.qix', '.fix'],
    'imagen_compleja': ['.tif', '.tiff', '.tfw', '.jgw', '.xml', '.aux', '.ovr',
                       '.pyr', '.rdx', '.tif.aux.xml', '.tif.ovr', '.tif.xml'],
    'cad': ['.dwg', '.dxf', '.dgn', '.bak', '.dng', '.dwl', '.dwl2']
}

# Extensiones que requieren descarga de directorio completo
DESCARGAR_DIRECTORIO_COMPLETO = ['.tif', '.tiff', '.gdb']

# Configuración de streaming
CHUNK_SIZE = 8 * 1024 * 1024  # 8MB chunks para streaming óptimo


def crear_zip_streaming(archivos_o_directorios, nombre_base="descarga"):
    """
    Genera un ZIP con streaming REAL - el usuario ve la descarga iniciar inmediatamente.
    Usa archivo temporal pero envía chunks mientras se lee.
    """
    def generar():
        temp_zip_path = None
        try:
            # Crear archivo temporal para el ZIP
            temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            temp_zip_path = temp_zip.name
            temp_zip.close()

            # Crear el ZIP en el archivo temporal con compresión mínima para velocidad
            with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
                for item_path in archivos_o_directorios:
                    if not os.path.exists(item_path):
                        logger.warning(f"Item no existe, omitiendo: {item_path}")
                        continue

                    if os.path.isdir(item_path):
                        base_name = os.path.basename(item_path)
                        for root, dirs, files in os.walk(item_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                if os.path.isfile(file_path):
                                    rel_path = os.path.relpath(file_path, item_path)
                                    arcname = os.path.join(base_name, rel_path).replace('\\', '/')
                                    try:
                                        zf.write(file_path, arcname)
                                    except Exception as e:
                                        logger.warning(f"Error agregando {file_path}: {e}")
                    else:
                        try:
                            zf.write(item_path, os.path.basename(item_path))
                        except Exception as e:
                            logger.warning(f"Error agregando {item_path}: {e}")

            # Streaming del ZIP en chunks grandes
            with open(temp_zip_path, 'rb') as f:
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    yield chunk

        except Exception as e:
            logger.error(f"Error en streaming ZIP: {e}")
            raise
        finally:
            # Limpiar archivo temporal
            if temp_zip_path and os.path.exists(temp_zip_path):
                try:
                    os.unlink(temp_zip_path)
                except:
                    pass

    return generar()


def file_iterator(file_path, chunk_size=CHUNK_SIZE):
    """Generador que lee un archivo en chunks para streaming."""
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


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


def registrar_archivo_en_bd(ruta_completa, nombre_archivo, tamano_archivo, usuario):
    """
    Registra un archivo subido en las tablas de indexación:
    - DisposicionPost (directorio)
    - ArchivosPost (archivo)
    - EvaluacionArchivosPost (para que aparezca en la interfaz)

    Returns: dict con información del registro o None si falla
    """
    try:
        # 1. Extraer código de municipio de la ruta
        cod_municipio = extraer_municipio_de_ruta(ruta_completa)
        if not cod_municipio:
            logger.warning(f"⚠️ No se pudo extraer municipio de ruta: {ruta_completa}")
            return None

        # 2. Obtener el municipio de la BD
        try:
            municipio = Municipios.objects.get(cod_municipio=cod_municipio)
        except Municipios.DoesNotExist:
            logger.warning(f"⚠️ Municipio {cod_municipio} no existe en la BD")
            return None

        # 3. Construir ruta del directorio (sin el archivo)
        # Usar formato Linux para que coincida con el indexador (Script_POST_Linux.py)
        # El indexador almacena ruta_acceso en formato Linux (/mnt/repositorio/...)
        directorio_linux = os.path.dirname(ruta_completa)

        # 4. Buscar o crear DisposicionPost para el directorio
        disposicion, created = DisposicionPost.objects.get_or_create(
            ruta_acceso=directorio_linux,
            defaults={
                'cod_municipio': municipio,
                'dispuesto': True,
                'fecha_disposicion': date.today(),
                'evaluado': False,
                'aprobado': False,
                'observaciones': f'Directorio creado automáticamente por upload web - {usuario}'
            }
        )

        if created:
            logger.info(f"📁 DisposicionPost creado: ID {disposicion.id_disposicion} - {directorio_linux}")
        else:
            logger.info(f"📁 DisposicionPost existente: ID {disposicion.id_disposicion}")

        # 5. Calcular hash del archivo (opcional pero útil)
        try:
            hash_md5 = hashlib.md5()
            with open(ruta_completa, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_md5.update(chunk)
            hash_contenido = hash_md5.hexdigest()
        except Exception:
            hash_contenido = None

        # 6. Formatear tamaño del archivo
        def formatear_tamano(bytes_size):
            if bytes_size < 1024:
                return f"{bytes_size} B"
            elif bytes_size < 1024 * 1024:
                return f"{bytes_size / 1024:.1f} KB"
            elif bytes_size < 1024 * 1024 * 1024:
                return f"{bytes_size / (1024 * 1024):.1f} MB"
            else:
                return f"{bytes_size / (1024 * 1024 * 1024):.1f} GB"

        peso_memoria = formatear_tamano(tamano_archivo)

        # 7. Crear ArchivosPost
        # IMPORTANTE: Usar ruta_completa (formato Linux) para que coincida con el indexador
        # El indexador (Script_POST_Linux.py) busca por ruta Linux en archivos_post.ruta_completa
        archivo_post, archivo_created = ArchivosPost.objects.get_or_create(
            ruta_completa=ruta_completa,  # Formato Linux para evitar duplicados con indexador
            defaults={
                'id_disposicion': disposicion,
                'nombre_archivo': nombre_archivo,
                'fecha_disposicion': date.today(),
                'observacion': f'Subido via web por {usuario}',
                'hash_contenido': hash_contenido,
                'usuario_windows': usuario,
                'peso_memoria': peso_memoria
            }
        )

        if archivo_created:
            logger.info(f"📄 ArchivosPost creado: ID {archivo_post.id_archivo} - {nombre_archivo}")
        else:
            # Si ya existe, actualizar algunos campos
            archivo_post.hash_contenido = hash_contenido
            archivo_post.peso_memoria = peso_memoria
            archivo_post.save()
            logger.info(f"📄 ArchivosPost actualizado: ID {archivo_post.id_archivo}")

        # 8. Crear EvaluacionArchivosPost para que aparezca en la interfaz
        # IMPORTANTE: También usar formato Linux para consistencia
        evaluacion, eval_created = EvaluacionArchivosPost.objects.get_or_create(
            ruta_completa=ruta_completa,  # Formato Linux para consistencia con archivos_post
            defaults={
                'id_archivo': archivo_post.id_archivo,
                'id_disposicion': disposicion,
                'nombre_archivo': nombre_archivo,
                'fecha_disposicion': date.today(),
                'observacion_original': f'Subido via web por {usuario}',
                'hash_contenido': hash_contenido,
                'usuario_windows': usuario,
                'peso_memoria': peso_memoria
            }
        )

        if eval_created:
            logger.info(f"✅ EvaluacionArchivosPost creado: ID {evaluacion.id_evaluacion} - {nombre_archivo}")
        else:
            logger.info(f"✅ EvaluacionArchivosPost ya existía: ID {evaluacion.id_evaluacion}")

        return {
            'disposicion_id': disposicion.id_disposicion,
            'archivo_id': archivo_post.id_archivo,
            'evaluacion_id': evaluacion.id_evaluacion,
            'municipio': cod_municipio,
            'directorio': directorio_linux,
            'registrado': True
        }

    except Exception as e:
        logger.error(f"❌ Error registrando archivo en BD: {e}")
        import traceback
        logger.error(traceback.format_exc())
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
                    logger.error(f"❌ No se encontró GDB como directorio: {archivo_path}")
                    return [archivo_path]

    # Para otros archivos agrupados (shapefile, CAD, etc.)
    tipo_grupo, nombre_base = detectar_tipo_agrupacion(archivo_path)

    if tipo_grupo:
        logger.info(f"📦 Tipo de agrupación detectado: {tipo_grupo}")
        directorio_padre = os.path.dirname(archivo_path)
        extensiones_buscar = EXTENSIONES_AGRUPAR[tipo_grupo]

        archivos_relacionados = []

        # Buscar archivos con el mismo nombre base y extensiones relacionadas
        for ext in extensiones_buscar:
            archivo_posible = os.path.join(directorio_padre, f"{nombre_base}{ext}")
            if os.path.exists(archivo_posible) and os.path.isfile(archivo_posible):
                archivos_relacionados.append(archivo_posible)

        logger.info(f"✅ Encontrados {len(archivos_relacionados)} archivos relacionados")
        return archivos_relacionados if archivos_relacionados else [archivo_path]

    # Archivo individual
    logger.info(f"📄 Archivo individual sin agrupación")
    return [archivo_path]

def normalizar_ruta(ruta):
    """Normaliza la ruta para soportar tanto Windows como Linux"""
    # Convertir barras invertidas a barras normales
    ruta_normalizada = ruta.replace('\\', '/')

    # Si la ruta ya está en formato Linux, devolverla tal cual
    if ruta_normalizada.startswith('/mnt/repositorio'):
        return ruta_normalizada

    # Si la ruta está en formato relativo de Windows, convertirla a Linux
    if not ruta_normalizada.startswith('/'):
        # Remover prefijos comunes de Windows
        ruta_normalizada = re.sub(r'^\\\\repositorio\\DirGesCat\\', '/mnt/repositorio/', ruta_normalizada)
        ruta_normalizada = re.sub(r'^repositorio/DirGesCat/', '/mnt/repositorio/', ruta_normalizada)

    return ruta_normalizada

# ============================================================================
# ✅ FUNCIÓN CORREGIDA: descargar_archivo
# ============================================================================
@api_view(['GET'])
@permission_classes([AllowAny])
def descargar_archivo(request):
    """Descarga archivos individuales o crea ZIPs para archivos agrupados - POST-OPERACIÓN"""

    # Autenticar por token en query param (para window.open con barra de progreso)
    user, error_response = autenticar_por_token_query(request)
    if error_response:
        return error_response

    # ✅ VALIDAR PARÁMETROS DE FORMA SEGURA
    try:
        ruta_archivo = PathParameterValidator.get_safe_path_param(
            request, 'ruta', required=True
        )
        forzar_individual = BooleanParameterValidator.get_boolean_param(
            request, 'individual', default=False
        )
    except ValidationError as e:
        return Response(e.detail, status=400)

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
                # Buscar en archivos post-operacionales
                archivo_post = ArchivosPost.objects.filter(
                    ruta_completa=ruta_archivo
                ).first()

                if archivo_post:
                    # Intentar obtener el municipio de la relación
                    if hasattr(archivo_post, 'cod_municipio'):
                        municipio_ruta = archivo_post.cod_municipio.cod_municipio
                    elif hasattr(archivo_post, 'cod_path_dir'):
                        if hasattr(archivo_post.cod_path_dir, 'cod_municipio'):
                            municipio_ruta = archivo_post.cod_path_dir.cod_municipio.cod_municipio

            # Verificar si el municipio está en la lista de permitidos
            if municipio_ruta and municipio_ruta not in municipios_permitidos:
                return HttpResponse("No tiene permisos para acceder a este archivo", status=403)

        except ProfesionalesSeguimiento.DoesNotExist:
            return HttpResponse("No tiene permisos para acceder a archivos", status=403)

    # Normalizar ruta
    ruta_archivo = normalizar_ruta(ruta_archivo)
    logger.info(f"📂 Ruta normalizada para descarga: {ruta_archivo}")

    # Verificar si el archivo existe
    if not os.path.exists(ruta_archivo):
        logger.error(f"❌ Archivo no encontrado: {ruta_archivo}")
        ruta_windows = linux_to_windows_path(ruta_archivo)
        return HttpResponse(f"El archivo no existe: {ruta_windows}", status=404)

    # Si es un directorio, crear ZIP con STREAMING
    if os.path.isdir(ruta_archivo):
        try:
            nombre_carpeta = os.path.basename(ruta_archivo.rstrip('/'))
            nombre_zip = f"{nombre_carpeta}.zip"

            # Usar streaming para que la descarga inicie inmediatamente
            response = StreamingHttpResponse(
                crear_zip_streaming([ruta_archivo], nombre_carpeta),
                content_type='application/zip'
            )
            response['Content-Disposition'] = f'attachment; filename="{nombre_zip}"'
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['X-Accel-Buffering'] = 'no'  # Desactivar buffering en nginx

            logger.info(f"✅ ZIP streaming iniciado: {nombre_zip}")
            return response

        except Exception as e:
            logger.error(f"❌ Error al crear ZIP: {str(e)}")
            return HttpResponse(f"Error al crear ZIP: {str(e)}", status=500)

    # Si es un archivo individual
    extension = Path(ruta_archivo).suffix.lower()

    # Si es un archivo que debe agruparse y no se fuerza descarga individual
    if not forzar_individual and extension in [ext for exts in EXTENSIONES_AGRUPAR.values() for ext in exts]:
        archivos_relacionados = obtener_archivos_relacionados(ruta_archivo)

        # Si hay múltiples archivos o directorios, crear ZIP con STREAMING
        if len(archivos_relacionados) > 1 or (len(archivos_relacionados) == 1 and os.path.isdir(archivos_relacionados[0])):
            try:
                nombre_base = Path(ruta_archivo).stem
                nombre_zip = f"{nombre_base}.zip"

                # Usar streaming para que la descarga inicie inmediatamente
                response = StreamingHttpResponse(
                    crear_zip_streaming(archivos_relacionados, nombre_base),
                    content_type='application/zip'
                )
                response['Content-Disposition'] = f'attachment; filename="{nombre_zip}"'
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response['X-Accel-Buffering'] = 'no'  # Desactivar buffering en nginx

                logger.info(f"✅ ZIP streaming con archivos relacionados iniciado: {nombre_zip}")
                return response

            except Exception as e:
                logger.error(f"❌ Error al crear ZIP: {str(e)}")
                return HttpResponse(f"Error al crear ZIP: {str(e)}", status=500)

    # Descarga individual con STREAMING
    try:
        content_type, _ = mimetypes.guess_type(ruta_archivo)
        if not content_type:
            content_type = 'application/octet-stream'

        file_size = os.path.getsize(ruta_archivo)
        nombre_archivo = os.path.basename(ruta_archivo)

        # Usar FileResponse para streaming automático (mejor para archivos individuales)
        response = FileResponse(
            open(ruta_archivo, 'rb'),
            content_type=content_type,
            as_attachment=True,
            filename=nombre_archivo
        )
        response['Content-Length'] = file_size
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['X-Accel-Buffering'] = 'no'  # Desactivar buffering en nginx

        logger.info(f"✅ Archivo streaming iniciado: {nombre_archivo} ({file_size} bytes)")
        return response

    except Exception as e:
        logger.error(f"❌ Error al descargar archivo: {str(e)}")
        return HttpResponse(f"Error al descargar archivo: {str(e)}", status=500)


# ============================================================================
# ✅ FUNCIÓN CORREGIDA: verificar_archivo
# ============================================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verificar_archivo(request):
    """Verifica si un archivo existe y si el usuario tiene permisos"""

    # ✅ VALIDAR PARÁMETRO DE FORMA SEGURA
    try:
        ruta_archivo = PathParameterValidator.get_safe_path_param(
            request, 'ruta', required=True
        )
    except ValidationError as e:
        return Response(e.detail, status=400)

    # Normalizar ruta
    ruta_archivo = normalizar_ruta(ruta_archivo)

    # Verificar permisos (similar a descargar_archivo)
    es_admin = request.user.is_staff or request.user.is_superuser or request.user.groups.filter(name='Administradores').exists()

    if not es_admin:
        try:
            profesional = ProfesionalesSeguimiento.objects.get(cod_profesional=request.user.username)
            municipios_permitidos = list(ProfesionalMunicipio.objects.filter(
                cod_profesional=profesional
            ).values_list('cod_municipio', flat=True))

            if not municipios_permitidos:
                return JsonResponse({'existe': False, 'error': 'No tiene municipios asignados'}, status=403)

            municipio_ruta = extraer_municipio_de_ruta(ruta_archivo)

            if not municipio_ruta:
                archivo_post = ArchivosPost.objects.filter(ruta_completa=ruta_archivo).first()
                if archivo_post:
                    if hasattr(archivo_post, 'cod_municipio'):
                        municipio_ruta = archivo_post.cod_municipio.cod_municipio

            if municipio_ruta and municipio_ruta not in municipios_permitidos:
                return JsonResponse({'existe': False, 'error': 'No tiene permisos'}, status=403)

        except ProfesionalesSeguimiento.DoesNotExist:
            return JsonResponse({'existe': False, 'error': 'No tiene permisos'}, status=403)

    # Verificar existencia
    existe = os.path.exists(ruta_archivo)

    return JsonResponse({
        'existe': existe,
        'es_directorio': os.path.isdir(ruta_archivo) if existe else False,
        'ruta_normalizada': ruta_archivo
    })


# ============================================================================
# ✅ FUNCIÓN CORREGIDA: preview_descarga
# ============================================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def preview_descarga(request):
    """Vista previa de lo que se descargará (archivos relacionados)"""

    # ✅ VALIDAR PARÁMETRO DE FORMA SEGURA
    try:
        ruta_archivo = PathParameterValidator.get_safe_path_param(
            request, 'ruta', required=True
        )
    except ValidationError as e:
        return Response(e.detail, status=400)

    # Normalizar ruta
    ruta_archivo = normalizar_ruta(ruta_archivo)

    # Verificar existencia
    if not os.path.exists(ruta_archivo):
        ruta_windows = linux_to_windows_path(ruta_archivo)
        return JsonResponse({'error': f'El archivo no existe: {ruta_windows}'}, status=404)

    # Obtener archivos relacionados
    archivos_relacionados = obtener_archivos_relacionados(ruta_archivo)

    archivos_info = []
    for archivo in archivos_relacionados:
        if os.path.isdir(archivo):
            # Contar archivos en directorio
            total_archivos = sum([len(files) for _, _, files in os.walk(archivo)])
            archivos_info.append({
                'ruta': archivo,
                'nombre': os.path.basename(archivo),
                'tipo': 'directorio',
                'archivos_dentro': total_archivos
            })
        else:
            archivos_info.append({
                'ruta': archivo,
                'nombre': os.path.basename(archivo),
                'tipo': 'archivo',
                'tamano': os.path.getsize(archivo)
            })

    return JsonResponse({
        'archivos': archivos_info,
        'total': len(archivos_info),
        'se_creara_zip': len(archivos_info) > 1 or (len(archivos_info) == 1 and archivos_info[0]['tipo'] == 'directorio')
    })


# ============================================================================
# ✅ FUNCIÓN NUEVA: subir_archivo - Upload de archivos al repositorio
# ============================================================================
@csrf_exempt
@api_view(['POST'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAuthenticated])
def subir_archivo(request):
    """
    Sube un archivo al repositorio NAS.

    Permisos:
    - Admin/SuperAdmin: Pueden subir a cualquier ubicación
    - Profesionales: Solo pueden subir a municipios que tienen asignados

    Parámetros POST (multipart/form-data):
        - file: El archivo a subir
        - path: Ruta relativa dentro del repositorio (ej: "01_actualiz_catas/13/654")
        - filename: (opcional) Nombre personalizado para el archivo

    Returns:
        JSON con resultado de la operación
    """
    logger.info(f"📤 UPLOAD REQUEST - Usuario: {request.user}, Method: {request.method}")
    logger.info(f"📤 FILES: {list(request.FILES.keys())}")
    logger.info(f"📤 POST: {dict(request.POST)}")

    # 1. Verificar permisos del usuario
    es_admin = (
        request.user.is_staff or
        request.user.is_superuser or
        request.user.groups.filter(name='Administradores').exists()
    )

    # Si no es admin, verificar si es profesional con municipio asignado
    es_profesional_autorizado = False
    municipios_permitidos = []

    if not es_admin:
        try:
            # Buscar profesional asociado al usuario
            profesional = ProfesionalesSeguimiento.objects.get(cod_profesional=request.user.username)

            # Obtener lista de municipios asignados
            municipios_permitidos = list(ProfesionalMunicipio.objects.filter(
                cod_profesional=profesional
            ).values_list('cod_municipio', flat=True))

            if municipios_permitidos:
                es_profesional_autorizado = True
                logger.info(f"📤 Profesional {request.user.username} tiene {len(municipios_permitidos)} municipios asignados")
            else:
                logger.warning(f"⚠️ Profesional {request.user.username} no tiene municipios asignados")

        except ProfesionalesSeguimiento.DoesNotExist:
            logger.warning(f"⚠️ Usuario {request.user.username} no es profesional registrado")

    # Si no es admin ni profesional autorizado, rechazar
    if not es_admin and not es_profesional_autorizado:
        logger.warning(f"⚠️ Usuario {request.user.username} intentó subir archivo sin permisos")
        return JsonResponse({
            'success': False,
            'error': 'No tienes permisos para subir archivos. Contacta al administrador.'
        }, status=403)

    # 2. Verificar que se envió un archivo
    if 'file' not in request.FILES:
        return JsonResponse({
            'success': False,
            'error': 'No se envió ningún archivo'
        }, status=400)

    archivo = request.FILES['file']

    # 3. Obtener la ruta de destino
    ruta_destino = request.POST.get('path', '')
    nombre_archivo = request.POST.get('filename', archivo.name)

    # Limpiar nombre de archivo
    nombre_archivo = nombre_archivo.strip()
    if not nombre_archivo:
        nombre_archivo = archivo.name

    # 4. Validar extensión del archivo
    extension = os.path.splitext(nombre_archivo)[1].lower()
    if extension in EXTENSIONES_BLOQUEADAS:
        logger.warning(f"⚠️ Intento de subir archivo con extensión bloqueada: {extension} por {request.user.username}")
        return JsonResponse({
            'success': False,
            'error': f'La extensión "{extension}" no está permitida por seguridad'
        }, status=400)

    # 5. Validar tamaño del archivo
    if archivo.size > MAX_UPLOAD_SIZE:
        return JsonResponse({
            'success': False,
            'error': f'El archivo excede el tamaño máximo permitido ({MAX_UPLOAD_SIZE // (1024*1024)} MB)'
        }, status=400)

    # 6. Construir ruta completa de destino
    # Ruta base del repositorio
    base_path = getattr(settings, 'REPOSITORY_BASE_PATH', '/mnt/repositorio/2510SP/H_Informacion_Consulta/Sub_Proy')

    # Normalizar la ruta de destino
    ruta_destino = ruta_destino.replace('\\', '/').strip('/')

    # Validar que la ruta no contenga caracteres peligrosos
    if '..' in ruta_destino or ruta_destino.startswith('/'):
        logger.warning(f"⚠️ Intento de path traversal por {request.user.username}: {ruta_destino}")
        return JsonResponse({
            'success': False,
            'error': 'Ruta de destino inválida'
        }, status=400)

    # 6.1 Si es profesional (no admin), validar que la ruta pertenezca a su municipio asignado
    if es_profesional_autorizado and not es_admin:
        # Extraer código de municipio de la ruta
        municipio_ruta = extraer_municipio_de_ruta(ruta_destino)

        if municipio_ruta:
            if municipio_ruta not in municipios_permitidos:
                logger.warning(f"⚠️ Profesional {request.user.username} intentó subir a municipio {municipio_ruta} no asignado")
                return JsonResponse({
                    'success': False,
                    'error': f'No tienes permisos para subir archivos al municipio {municipio_ruta}. Solo puedes subir a tus municipios asignados.'
                }, status=403)
            else:
                logger.info(f"✅ Profesional {request.user.username} autorizado para municipio {municipio_ruta}")
        else:
            # Si no se puede extraer el municipio de la ruta, rechazar para profesionales
            logger.warning(f"⚠️ No se pudo determinar el municipio de la ruta: {ruta_destino}")
            return JsonResponse({
                'success': False,
                'error': 'No se pudo determinar el municipio de destino. Verifica la ruta.'
            }, status=400)

    # Construir ruta completa
    if ruta_destino:
        ruta_completa = os.path.join(base_path, ruta_destino, nombre_archivo)
    else:
        ruta_completa = os.path.join(base_path, nombre_archivo)

    # Normalizar la ruta
    ruta_completa = os.path.normpath(ruta_completa)

    # 7. Verificar que la ruta está dentro del repositorio (seguridad)
    if not ruta_completa.startswith(base_path.rstrip('/')):
        logger.warning(f"⚠️ Intento de escribir fuera del repositorio por {request.user.username}: {ruta_completa}")
        return JsonResponse({
            'success': False,
            'error': 'Ruta de destino fuera del repositorio permitido'
        }, status=400)

    # 8. Verificar/crear directorio de destino
    directorio_destino = os.path.dirname(ruta_completa)

    # 🔍 DEBUG: Información detallada del directorio
    logger.info(f"🔍 DEBUG UPLOAD - Directorio destino: {directorio_destino}")
    logger.info(f"🔍 DEBUG UPLOAD - Directorio existe: {os.path.exists(directorio_destino)}")
    logger.info(f"🔍 DEBUG UPLOAD - Es directorio: {os.path.isdir(directorio_destino) if os.path.exists(directorio_destino) else 'N/A'}")

    # Verificar permisos del directorio si existe
    if os.path.exists(directorio_destino):
        try:
            # Verificar si podemos escribir
            test_file = os.path.join(directorio_destino, '.write_test_tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            logger.info(f"✅ DEBUG UPLOAD - Directorio tiene permisos de escritura")
        except PermissionError as pe:
            logger.error(f"❌ DEBUG UPLOAD - SIN PERMISOS DE ESCRITURA en {directorio_destino}: {pe}")
            # Intentar obtener info de permisos
            try:
                import stat
                st = os.stat(directorio_destino)
                logger.error(f"❌ DEBUG UPLOAD - Permisos: {oct(st.st_mode)}, UID: {st.st_uid}, GID: {st.st_gid}")
            except Exception as stat_err:
                logger.error(f"❌ DEBUG UPLOAD - No se pudo obtener stat: {stat_err}")
            return JsonResponse({
                'success': False,
                'error': f'Error de permisos: No se puede escribir en el directorio destino. Contacte al administrador del NAS.'
            }, status=500)
        except Exception as test_err:
            logger.warning(f"⚠️ DEBUG UPLOAD - Error en test de escritura: {test_err}")

    if not os.path.exists(directorio_destino):
        try:
            os.makedirs(directorio_destino, exist_ok=True)
            logger.info(f"📁 Directorio creado: {directorio_destino}")
        except Exception as e:
            logger.error(f"❌ Error creando directorio {directorio_destino}: {e}")
            return JsonResponse({
                'success': False,
                'error': f'No se pudo crear el directorio de destino: {str(e)}'
            }, status=500)

    # 9. Verificar si el archivo ya existe
    if os.path.exists(ruta_completa):
        # Generar nombre único
        base_nombre, ext = os.path.splitext(nombre_archivo)
        contador = 1
        while os.path.exists(ruta_completa):
            nombre_nuevo = f"{base_nombre}_{contador}{ext}"
            ruta_completa = os.path.join(directorio_destino, nombre_nuevo)
            contador += 1
        nombre_archivo = os.path.basename(ruta_completa)
        logger.info(f"📝 Archivo renombrado a: {nombre_archivo}")

    # 10. Guardar el archivo
    try:
        with open(ruta_completa, 'wb+') as destino:
            for chunk in archivo.chunks():
                destino.write(chunk)

        # Establecer permisos del archivo
        os.chmod(ruta_completa, 0o664)

        logger.info(f"✅ Archivo subido exitosamente: {ruta_completa} por {request.user.username}")

        # Construir ruta Windows para mostrar al usuario
        ruta_windows = ruta_completa.replace('/mnt/repositorio', r'\\repositorio\DirGesCat')
        ruta_windows = ruta_windows.replace('/', '\\')

        # 11. Registrar en auditoría
        try:
            auditoria = AuditoriaArchivos.registrar_accion(
                archivo=None,  # El archivo aún no existe en la BD
                nombre_archivo=nombre_archivo,
                ruta_completa=ruta_completa,
                accion='UPLOAD',
                usuario=request.user.username,
                usuario_email=request.user.email,
                plataforma='WEB',
                detalles={
                    'ruta_destino': ruta_destino,
                    'ruta_windows': ruta_windows,
                    'extension': extension,
                    'tamaño_original': archivo.size,
                },
                ip_cliente=get_client_ip(request),
                tamano_archivo=archivo.size
            )
            logger.info(f"📋 Auditoría registrada: ID {auditoria.id}")
        except Exception as audit_error:
            # No fallar si la auditoría falla, el archivo ya se subió
            logger.warning(f"⚠️ Error al registrar auditoría: {audit_error}")

        # 12. Registrar en tablas de indexación (para que aparezca en el frontend)
        registro_bd = None
        try:
            registro_bd = registrar_archivo_en_bd(
                ruta_completa=ruta_completa,
                nombre_archivo=nombre_archivo,
                tamano_archivo=archivo.size,
                usuario=request.user.username
            )
            if registro_bd:
                logger.info(f"📊 Archivo indexado en BD: {registro_bd}")
            else:
                logger.warning(f"⚠️ No se pudo indexar el archivo en la BD (puede que la ruta no tenga formato esperado)")
        except Exception as index_error:
            # No fallar si la indexación falla, el archivo ya se subió
            logger.warning(f"⚠️ Error al indexar archivo en BD: {index_error}")

        return JsonResponse({
            'success': True,
            'mensaje': f'Archivo "{nombre_archivo}" subido exitosamente',
            'archivo': {
                'nombre': nombre_archivo,
                'ruta_linux': ruta_completa,
                'ruta_windows': ruta_windows,
                'tamano': archivo.size,
                'subido_por': request.user.username,
                'fecha_subida': auditoria.fecha_accion.isoformat() if 'auditoria' in locals() else None,
                'indexado': registro_bd is not None,
                'registro_bd': registro_bd
            }
        }, status=201)

    except PermissionError as e:
        logger.error(f"❌ Error de permisos al guardar archivo en {ruta_completa}: {e}")
        # Convertir ruta a Windows para el mensaje al usuario
        ruta_win_error = directorio_destino.replace('/mnt/repositorio', r'\\repositorio\DirGesCat').replace('/', '\\')
        return JsonResponse({
            'success': False,
            'error': f'Error de permisos: No se puede escribir en "{ruta_win_error}". El directorio no tiene permisos de escritura en el NAS. Contacte al administrador.'
        }, status=500)

    except Exception as e:
        logger.error(f"❌ Error al guardar archivo {ruta_completa}: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Error al guardar el archivo: {str(e)}'
        }, status=500)


# ============================================================================
# ✅ FUNCIÓN NUEVA: historial_archivo - Obtiene historial de auditoría
# ============================================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historial_archivo(request):
    """
    Obtiene el historial de auditoría de un archivo.

    Parámetros GET:
        - ruta: Ruta completa del archivo (Linux o Windows)
        - limite: Número máximo de registros a retornar (default: 50)

    Returns:
        JSON con el historial de acciones sobre el archivo
    """
    ruta = request.GET.get('ruta', '')

    if not ruta:
        return JsonResponse({
            'success': False,
            'error': 'Se requiere el parámetro "ruta"'
        }, status=400)

    # Normalizar la ruta (convertir Windows a Linux si es necesario)
    if ruta.startswith('\\\\') or '\\' in ruta:
        # Es una ruta Windows, convertir a Linux
        ruta_linux = ruta.replace('\\\\repositorio\\DirGesCat', '/mnt/repositorio')
        ruta_linux = ruta_linux.replace('\\', '/')
    else:
        ruta_linux = ruta

    limite = int(request.GET.get('limite', 50))

    # Obtener historial
    historial = AuditoriaArchivos.objects.filter(
        ruta_completa=ruta_linux
    ).order_by('-fecha_accion')[:limite]

    # Construir respuesta
    registros = []
    for reg in historial:
        registros.append({
            'id': reg.id,
            'accion': reg.accion,
            'accion_display': reg.get_accion_display(),
            'usuario': reg.usuario,
            'usuario_email': reg.usuario_email,
            'plataforma': reg.plataforma,
            'plataforma_display': reg.get_plataforma_display(),
            'fecha_accion': reg.fecha_accion.isoformat(),
            'detalles': reg.detalles,
            'ip_cliente': reg.ip_cliente,
            'tamano_archivo': reg.tamano_archivo
        })

    # Verificar si el archivo fue subido por la plataforma web
    subido_por_web = AuditoriaArchivos.objects.filter(
        ruta_completa=ruta_linux,
        accion='UPLOAD',
        plataforma='WEB'
    ).first()

    return JsonResponse({
        'success': True,
        'ruta': ruta_linux,
        'total_registros': len(registros),
        'historial': registros,
        'subido_por_plataforma': subido_por_web is not None,
        'info_subida': {
            'usuario': subido_por_web.usuario if subido_por_web else None,
            'fecha': subido_por_web.fecha_accion.isoformat() if subido_por_web else None,
            'ip': subido_por_web.ip_cliente if subido_por_web else None
        } if subido_por_web else None
    })


# ============================================
# EXPORTAR AUDITORÍA A CSV
# ============================================
@api_view(['GET'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAuthenticated])
def exportar_auditoria_csv(request, municipio_id):
    """
    Exporta el historial de auditoría de un municipio a CSV.

    Parámetros GET:
        - fecha_desde: (opcional) Fecha inicial YYYY-MM-DD
        - fecha_hasta: (opcional) Fecha final YYYY-MM-DD
        - accion: (opcional) Filtrar por tipo de acción (UPLOAD, DELETE, etc.)
        - usuario: (opcional) Filtrar por usuario

    Returns:
        Archivo CSV con el historial de auditoría
    """
    import csv
    from datetime import datetime, timedelta

    logger.info(f"📊 Exportando auditoría para municipio {municipio_id} - Usuario: {request.user}")

    # Verificar permisos - solo admin puede exportar
    es_admin = (
        request.user.is_staff or
        request.user.is_superuser or
        request.user.groups.filter(name='Administradores').exists()
    )

    if not es_admin:
        return JsonResponse({
            'success': False,
            'error': 'Solo los administradores pueden exportar auditoría'
        }, status=403)

    try:
        # Construir patrón de ruta para el municipio
        municipio_str = str(municipio_id).zfill(5)
        depto = municipio_str[:2]
        muni = municipio_str[2:5]

        # Patrón de búsqueda: /mnt/repositorio/.../depto/muni/...
        patron_ruta = f"/mnt/repositorio/2510SP/H_Informacion_Consulta/Sub_Proy/01_actualiz_catas/{depto}/{muni}/"

        # Construir query base
        queryset = AuditoriaArchivos.objects.filter(
            ruta_completa__startswith=patron_ruta
        )

        # Aplicar filtros opcionales
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        accion_filtro = request.GET.get('accion')
        usuario_filtro = request.GET.get('usuario')

        if fecha_desde:
            try:
                fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
                queryset = queryset.filter(fecha_accion__gte=fecha_desde_dt)
            except ValueError:
                pass

        if fecha_hasta:
            try:
                fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
                # Añadir un día para incluir todo el día final
                fecha_hasta_dt = fecha_hasta_dt + timedelta(days=1)
                queryset = queryset.filter(fecha_accion__lt=fecha_hasta_dt)
            except ValueError:
                pass

        if accion_filtro:
            queryset = queryset.filter(accion=accion_filtro.upper())

        if usuario_filtro:
            queryset = queryset.filter(usuario__icontains=usuario_filtro)

        # Ordenar por fecha descendente
        queryset = queryset.order_by('-fecha_accion')

        # Crear respuesta CSV
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="auditoria_municipio_{municipio_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        # Escribir BOM para Excel
        response.write('\ufeff')

        writer = csv.writer(response, delimiter=';')

        # Escribir encabezados
        writer.writerow([
            'ID',
            'Fecha y Hora',
            'Acción',
            'Usuario',
            'Email',
            'Nombre Archivo',
            'Ruta Completa',
            'Plataforma',
            'IP Cliente',
            'Tamaño (bytes)',
            'Detalles'
        ])

        # Escribir datos
        for reg in queryset:
            # Extraer detalles como string
            detalles_str = ''
            if reg.detalles:
                try:
                    import json
                    detalles_str = json.dumps(reg.detalles, ensure_ascii=False)
                except:
                    detalles_str = str(reg.detalles)

            writer.writerow([
                reg.id,
                reg.fecha_accion.strftime('%Y-%m-%d %H:%M:%S') if reg.fecha_accion else '',
                reg.get_accion_display(),
                reg.usuario or '',
                reg.usuario_email or '',
                reg.nombre_archivo or '',
                reg.ruta_completa or '',
                reg.get_plataforma_display(),
                reg.ip_cliente or '',
                reg.tamano_archivo or '',
                detalles_str
            ])

        logger.info(f"✅ Auditoría exportada: {queryset.count()} registros para municipio {municipio_id}")

        return response

    except Exception as e:
        logger.error(f"❌ Error exportando auditoría: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'Error al exportar auditoría: {str(e)}'
        }, status=500)
