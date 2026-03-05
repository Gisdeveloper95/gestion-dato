"""
TransversalArbolCombinadoViewSet - Vista de árbol para directorios transversales (04_transv)

Similar a PreoperacionArbolCombinadoViewSet pero para la estructura transversal.
"""
import os
from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.db.models import Count, Sum, Value
from django.db.models.functions import Coalesce

from preoperacion.models import Municipios
from .models import DirectoriosTransv, ArchivosTransv, PathDirTransv


def get_municipios_permitidos(user):
    """
    Obtiene los municipios permitidos para el usuario.
    Retorna 'todos' para administradores o lista de códigos para profesionales.
    """
    if not user.is_authenticated:
        return []

    # Verificar si es superusuario o staff
    if user.is_superuser or user.is_staff:
        return 'todos'

    # Verificar si pertenece al grupo Administradores
    if user.groups.filter(name='Administradores').exists():
        return 'todos'

    # Buscar si el usuario tiene un profesional asociado por username
    # (no requiere grupo, busca directamente en la tabla profesionales_seguimiento)
    try:
        from preoperacion.models import ProfesionalMunicipio, ProfesionalesSeguimiento

        profesional = ProfesionalesSeguimiento.objects.get(
            cod_profesional=user.username
        )

        municipios_ids = ProfesionalMunicipio.objects.filter(
            cod_profesional=profesional
        ).values_list('cod_municipio', flat=True)

        return list(municipios_ids)
    except ProfesionalesSeguimiento.DoesNotExist:
        pass
    except Exception:
        pass

    return []


class TransversalArbolCombinadoViewSet(viewsets.ViewSet):
    """
    ViewSet para obtener la vista de árbol de directorios transversales (04_transv).

    Endpoints:
    - GET /api/transversal-arbol/municipios_con_transversal/
    - GET /api/transversal-arbol/arbol_realtime/?cod_mpio=17380

    Permisos:
    - Administradores y Super Administradores: acceso a todos los municipios
    - Profesionales: solo municipios asignados
    """
    permission_classes = [IsAuthenticated]

    def _verificar_acceso_municipio(self, user, cod_mpio):
        """
        Verifica si el usuario tiene acceso al municipio solicitado.
        """
        municipios_permitidos = get_municipios_permitidos(user)

        if municipios_permitidos == 'todos':
            return True

        if isinstance(municipios_permitidos, list):
            return cod_mpio in municipios_permitidos

        return False

    def _formatear_tamano(self, tamano_bytes):
        """Formatea el tamaño en bytes a formato legible"""
        if not tamano_bytes:
            return "0 B"
        tamano = float(tamano_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if tamano < 1024.0:
                return f"{tamano:.2f} {unit}"
            tamano /= 1024.0
        return f"{tamano:.2f} PB"

    @action(detail=False, methods=['get'], permission_classes=[AllowAny], authentication_classes=[])
    def municipios_con_transversal(self, request):
        """
        Lista todos los municipios que tienen directorios transversales indexados.
        Incluye estadísticas de directorios, archivos y tamaño.

        Endpoint público para compatibilidad con frontend.
        """
        try:
            # Obtener municipios que tienen directorios transversales
            municipios_con_dirs = DirectoriosTransv.objects.filter(
                activo=True
            ).values(
                'cod_municipio'
            ).annotate(
                total_directorios=Count('cod_dir_transv')
            ).values_list('cod_municipio', flat=True).distinct()

            # Obtener información de municipios
            municipios = Municipios.objects.filter(
                cod_municipio__in=municipios_con_dirs
            ).select_related('cod_depto').annotate(
                total_directorios=Coalesce(
                    Count('directoriostransv', distinct=True),
                    Value(0)
                ),
                total_archivos=Coalesce(
                    Count('directoriostransv__archivostransv', distinct=True),
                    Value(0)
                ),
                tamano_bytes=Coalesce(
                    Sum('directoriostransv__archivostransv__peso_memoria'),
                    Value(0)
                )
            ).order_by('nom_municipio')

            # Formatear respuesta
            resultado = []
            for mun in municipios:
                tamano = mun.tamano_bytes or 0
                if tamano >= 1024 * 1024 * 1024:
                    tamano_str = f"{tamano / (1024*1024*1024):.2f} GB"
                elif tamano >= 1024 * 1024:
                    tamano_str = f"{tamano / (1024*1024):.2f} MB"
                elif tamano >= 1024:
                    tamano_str = f"{tamano / 1024:.2f} KB"
                else:
                    tamano_str = f"{tamano} B"

                resultado.append({
                    'cod_municipio': mun.cod_municipio,
                    'nom_municipio': mun.nom_municipio,
                    'cod_depto': mun.cod_depto.cod_depto if mun.cod_depto else None,
                    'nom_territorial': mun.nom_territorial,
                    'total_directorios': mun.total_directorios,
                    'total_archivos': mun.total_archivos,
                    'tamano_total': tamano_str
                })

            return Response(resultado)

        except Exception as e:
            return Response(
                {'error': f'Error listando municipios: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def arbol_realtime(self, request):
        """
        Obtiene el árbol de transversal leyendo DIRECTAMENTE del sistema de archivos.
        NO depende de datos indexados - acceso en tiempo real al NAS.

        Parámetros:
        - cod_mpio: Código del municipio (requerido)
        - path: Subdirectorio a explorar (opcional, relativo a 04_transv)
        """
        cod_mpio = request.query_params.get('cod_mpio')
        subpath = request.query_params.get('path', '')
        mecanismo_param = request.query_params.get('mecanismo', '')

        if not cod_mpio:
            return Response(
                {'error': 'Parámetro cod_mpio es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cod_mpio = int(cod_mpio)
        except ValueError:
            return Response(
                {'error': 'cod_mpio debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar permisos de acceso al municipio
        if not self._verificar_acceso_municipio(request.user, cod_mpio):
            return Response(
                {'error': 'No tiene permisos para acceder a este municipio'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            # Obtener información del municipio
            municipio = Municipios.objects.select_related('cod_depto').filter(
                cod_municipio=cod_mpio
            ).first()

            if not municipio:
                return Response(
                    {'error': f'Municipio {cod_mpio} no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Construir la ruta base al filesystem
            resultado_ruta = self._construir_ruta_transversal(municipio, mecanismo=mecanismo_param)

            if not resultado_ruta or not resultado_ruta.get('path'):
                from backend.path_utils import linux_to_windows_path
                error_msg = resultado_ruta.get('error', 'No se encontró directorio transversal') if resultado_ruta else 'No se encontró directorio transversal'
                ruta_esperada = resultado_ruta.get('ruta_esperada') if resultado_ruta else None
                # Convertir ruta a formato Windows para mostrar al usuario
                ruta_windows = linux_to_windows_path(ruta_esperada) if ruta_esperada else None
                # También convertir el mensaje de error si contiene la ruta
                if ruta_esperada and ruta_esperada in error_msg:
                    error_msg = error_msg.replace(ruta_esperada, ruta_windows)
                return Response({
                    'cod_mpio': cod_mpio,
                    'nom_municipio': municipio.nom_municipio,
                    'estructura': [],
                    'mensaje': error_msg,
                    'ruta_buscada': ruta_windows
                })

            base_path = resultado_ruta['path']
            mecanismo = resultado_ruta.get('mecanismo', 'desconocido')

            # Si hay subpath, añadirlo
            if subpath:
                full_path = os.path.join(base_path, subpath)
            else:
                full_path = base_path

            # Verificar que el directorio existe
            if not os.path.isdir(full_path):
                return Response({
                    'cod_mpio': cod_mpio,
                    'nom_municipio': municipio.nom_municipio,
                    'estructura': [],
                    'mensaje': f'Directorio no encontrado: {full_path}',
                    'ruta_buscada': full_path
                })

            # Leer el directorio recursivamente
            estructura = self._leer_directorio_recursivo(full_path, base_path, max_depth=10)

            return Response({
                'cod_mpio': cod_mpio,
                'nom_municipio': municipio.nom_municipio,
                'nom_depto': municipio.cod_depto.nom_depto if municipio.cod_depto else None,
                'estructura': estructura,
                'ruta_base': base_path,
                'total_elementos': len(estructura)
            })

        except Exception as e:
            import traceback
            return Response(
                {'error': f'Error leyendo filesystem: {str(e)}', 'trace': traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _construir_ruta_transversal(self, municipio, mecanismo=''):
        """
        Construye la ruta al directorio 04_transv del municipio.
        Busca en el filesystem el mecanismo (PGN, SGP, etc.)

        Retorna:
        - dict con 'path' y 'error' si hubo problema
        - dict con 'path' si encontró el directorio
        """
        # Ruta base del repositorio
        repo_base = '/mnt/repositorio/2510SP/H_Informacion_Consulta/Sub_Proy/01_actualiz_catas'

        # Obtener código de departamento (2 dígitos)
        cod_depto = str(municipio.cod_depto.cod_depto).zfill(2) if municipio.cod_depto else None
        if not cod_depto:
            return {'path': None, 'error': 'Municipio sin departamento asignado'}

        # Obtener código de municipio (3 dígitos, sin el depto)
        cod_mpio_str = str(municipio.cod_municipio)
        if len(cod_mpio_str) == 5:
            cod_mpio_short = cod_mpio_str[2:]
        else:
            cod_mpio_short = cod_mpio_str.zfill(3)

        # Construir ruta al directorio del municipio
        mpio_base = os.path.join(repo_base, cod_depto, cod_mpio_short)

        try:
            if not os.path.isdir(mpio_base):
                return {'path': None, 'error': f'Directorio del municipio no existe: {mpio_base}', 'ruta_esperada': mpio_base}
        except OSError as e:
            return {'path': None, 'error': f'Error accediendo al repositorio: {str(e)}. Verifique el montaje del NAS.', 'ruta_esperada': mpio_base}

        # Buscar el mecanismo (PGN, SGP, CONPES, etc.)
        mecanismos_encontrados = []
        try:
            for item in os.listdir(mpio_base):
                item_path = os.path.join(mpio_base, item)
                try:
                    if os.path.isdir(item_path):
                        # Verificar si tiene 04_transv dentro
                        transv_path = os.path.join(item_path, '04_transv')
                        if os.path.isdir(transv_path):
                            mecanismos_encontrados.append({
                                'mecanismo': item,
                                'path': transv_path
                            })
                except OSError:
                    continue
        except PermissionError:
            return {'path': None, 'error': f'Permiso denegado para leer: {mpio_base}', 'ruta_esperada': mpio_base}
        except OSError as e:
            return {'path': None, 'error': f'Error de sistema de archivos: {str(e)}. Verifique conexión al NAS.', 'ruta_esperada': mpio_base}

        if not mecanismos_encontrados:
            return {'path': None, 'error': f'No se encontró carpeta 04_transv en ningún mecanismo dentro de {mpio_base}', 'ruta_esperada': mpio_base}

        # Si se especificó un mecanismo, buscar ese específicamente
        if mecanismo:
            for m in mecanismos_encontrados:
                if m['mecanismo'].upper() == mecanismo.upper():
                    return {'path': m['path'], 'mecanismo': m['mecanismo']}
            # Si no se encontró el mecanismo solicitado, informar
            disponibles = [m['mecanismo'] for m in mecanismos_encontrados]
            return {'path': None, 'error': f'Mecanismo {mecanismo} no encontrado. Disponibles: {", ".join(disponibles)}'}

        # Si hay múltiples mecanismos y no se especificó, usar el primero
        return {'path': mecanismos_encontrados[0]['path'], 'mecanismo': mecanismos_encontrados[0]['mecanismo']}

    def _leer_directorio_recursivo(self, dir_path, base_path, current_depth=0, max_depth=10):
        """
        Lee un directorio y sus contenidos recursivamente.
        Retorna estructura de árbol con archivos y carpetas.

        NOTA: Los directorios .gdb (geodatabases) se tratan como archivos descargables.
        """
        # Extensiones de directorios que deben tratarse como archivos
        DIRECTORY_AS_FILE_EXTENSIONS = ['.gdb', '.mdb', '.geodatabase']

        if current_depth > max_depth:
            return []

        items = []

        try:
            entries = sorted(os.listdir(dir_path))
        except PermissionError:
            return [{
                'id': f'error_{current_depth}',
                'nombre': '[Sin acceso]',
                'tipo': 'error',
                'mensaje': 'Permiso denegado'
            }]
        except Exception as e:
            return [{
                'id': f'error_{current_depth}',
                'nombre': f'[Error: {str(e)}]',
                'tipo': 'error'
            }]

        for entry in entries:
            entry_path = os.path.join(dir_path, entry)
            relative_path = os.path.relpath(entry_path, base_path)

            try:
                stat_info = os.stat(entry_path)
                is_dir = os.path.isdir(entry_path)

                # Verificar si es un directorio especial (.gdb, etc.)
                _, ext = os.path.splitext(entry)
                is_gdb_or_special = ext.lower() in DIRECTORY_AS_FILE_EXTENSIONS

                if is_dir and is_gdb_or_special:
                    # Calcular tamaño total del directorio .gdb
                    total_size = 0
                    try:
                        for dirpath, dirnames, filenames in os.walk(entry_path):
                            for f in filenames:
                                fp = os.path.join(dirpath, f)
                                total_size += os.path.getsize(fp)
                    except:
                        total_size = 0

                    item = {
                        'id': f'gdb_{relative_path.replace("/", "_").replace(" ", "_")}',
                        'nombre': entry,
                        'tipo': 'archivo',
                        'subtipo': 'geodatabase',
                        'ruta_relativa': relative_path,
                        'ruta_absoluta': entry_path,
                        'nivel': current_depth,
                        'fecha_modificacion': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                        'extension': ext.lower(),
                        'tamano_bytes': total_size,
                        'tamano_legible': self._formatear_tamano(total_size),
                        'archivos_count': 0,
                        'hijos': [],
                        'es_geodatabase': True
                    }
                elif is_dir:
                    # Directorio normal
                    try:
                        hijos_count = len(os.listdir(entry_path))
                    except:
                        hijos_count = 0

                    item = {
                        'id': f'dir_{relative_path.replace("/", "_").replace(" ", "_")}',
                        'nombre': entry,
                        'tipo': 'directorio',
                        'ruta_relativa': relative_path,
                        'ruta_absoluta': entry_path,
                        'nivel': current_depth,
                        'fecha_modificacion': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                        'archivos_count': hijos_count,
                        'hijos': self._leer_directorio_recursivo(
                            entry_path, base_path, current_depth + 1, max_depth
                        )
                    }
                else:
                    # Archivo normal
                    _, extension = os.path.splitext(entry)
                    item = {
                        'id': f'file_{relative_path.replace("/", "_").replace(" ", "_")}',
                        'nombre': entry,
                        'tipo': 'archivo',
                        'ruta_relativa': relative_path,
                        'ruta_absoluta': entry_path,
                        'nivel': current_depth,
                        'fecha_modificacion': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                        'extension': extension.lower() if extension else None,
                        'tamano_bytes': stat_info.st_size,
                        'tamano_legible': self._formatear_tamano(stat_info.st_size),
                        'archivos_count': 0,
                        'hijos': []
                    }

                items.append(item)

            except Exception as e:
                items.append({
                    'id': f'error_{entry}',
                    'nombre': entry,
                    'tipo': 'error',
                    'mensaje': str(e)
                })

        return items
