"""
OperacionArbolCombinadoViewSet - Vista de árbol para directorios de operación (02_oper)

Similar a ProductosViewSet pero enfocado en operación, con:
- Listado de municipios con operación
- Árbol de directorios/archivos
- Calificación masiva
- Evaluación de archivos
"""
import os
import uuid
from datetime import datetime
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.db.models import Count, Sum, Value, Q
from django.db.models.functions import Coalesce

from preoperacion.models import Municipios
from .models import (
    DirectoriosOperacion, ArchivosOperacion,
    CalificacionInfoOperacion, EvaluacionArchivosOperacion
)
from .serializers import (
    CalificacionInfoOperacionSerializer,
    EvaluacionArchivosOperacionSerializer,
    EvaluacionArchivosOperacionListSerializer
)


def get_municipios_permitidos(user):
    """
    Obtiene los municipios permitidos para el usuario.
    Retorna 'todos' para administradores o lista de códigos para profesionales.
    """
    import logging
    logger = logging.getLogger(__name__)

    if not user.is_authenticated:
        logger.warning(f"[PERMISOS] Usuario no autenticado")
        return []

    logger.info(f"[PERMISOS] Usuario: {user.username}, superuser: {user.is_superuser}, staff: {user.is_staff}")

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
        logger.info(f"[PERMISOS] Profesional encontrado: {profesional.nombre_profesional}")

        municipios_ids = ProfesionalMunicipio.objects.filter(
            cod_profesional=profesional
        ).values_list('cod_municipio', flat=True)

        result = list(municipios_ids)
        logger.info(f"[PERMISOS] Municipios permitidos: {result}")
        return result
    except ProfesionalesSeguimiento.DoesNotExist:
        logger.warning(f"[PERMISOS] No existe profesional con cod_profesional={user.username}")
    except Exception as e:
        logger.error(f"[PERMISOS] Error: {e}")

    return []


class OperacionArbolCombinadoViewSet(viewsets.ViewSet):
    """
    ViewSet para obtener la vista de árbol de directorios de operación (02_oper).

    Endpoints:
    - GET /api/operacion-arbol/municipios_con_operacion/
    - GET /api/operacion-arbol/arbol_directorios/?municipio_id=17380
    - GET /api/operacion-arbol/evaluaciones/?municipio_id=17380
    - POST /api/operacion-arbol/calificacion_masiva/
    - GET /api/operacion-arbol/calificaciones/
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
    def municipios_con_operacion(self, request):
        """
        Lista todos los municipios que tienen directorios de operación indexados.
        Incluye estadísticas de directorios, archivos, tamaño y estados de evaluación.
        """
        try:
            # Obtener municipios que tienen directorios de operación
            municipios_con_dirs = DirectoriosOperacion.objects.filter(
                activo=True
            ).values(
                'cod_municipio'
            ).annotate(
                total_directorios=Count('cod_dir_operacion')
            ).values_list('cod_municipio', flat=True).distinct()

            # Obtener información de municipios
            municipios = Municipios.objects.filter(
                cod_municipio__in=municipios_con_dirs
            ).select_related('cod_depto').annotate(
                total_directorios=Coalesce(
                    Count('directoriosoperacion', distinct=True),
                    Value(0)
                ),
                total_archivos=Coalesce(
                    Count('directoriosoperacion__archivosoperacion', distinct=True),
                    Value(0)
                ),
                tamano_bytes=Coalesce(
                    Sum('directoriosoperacion__archivosoperacion__peso_memoria'),
                    Value(0)
                )
            ).order_by('nom_municipio')

            # Obtener estadísticas de evaluación por municipio
            stats_evaluacion = EvaluacionArchivosOperacion.objects.filter(
                cod_dir_operacion__cod_municipio__in=municipios_con_dirs
            ).values(
                'cod_dir_operacion__cod_municipio'
            ).annotate(
                total_evaluaciones=Count('id_evaluacion'),
                pendientes=Count('id_evaluacion', filter=Q(estado_archivo='PENDIENTE')),
                evaluados=Count('id_evaluacion', filter=Q(estado_archivo='EVALUADO')),
                aprobados=Count('id_evaluacion', filter=Q(estado_archivo='APROBADO'))
            )

            # Crear diccionario de estadísticas
            stats_dict = {
                s['cod_dir_operacion__cod_municipio']: {
                    'total_evaluaciones': s['total_evaluaciones'],
                    'pendientes': s['pendientes'],
                    'evaluados': s['evaluados'],
                    'aprobados': s['aprobados']
                }
                for s in stats_evaluacion
            }

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

                # Obtener estadísticas de evaluación
                eval_stats = stats_dict.get(mun.cod_municipio, {
                    'total_evaluaciones': 0,
                    'pendientes': 0,
                    'evaluados': 0,
                    'aprobados': 0
                })

                resultado.append({
                    'cod_municipio': mun.cod_municipio,
                    'nom_municipio': mun.nom_municipio,
                    'cod_depto': mun.cod_depto.cod_depto if mun.cod_depto else None,
                    'nom_depto': mun.cod_depto.nom_depto if mun.cod_depto else None,
                    'nom_territorial': mun.nom_territorial,
                    'total_directorios': mun.total_directorios,
                    'total_archivos': mun.total_archivos,
                    'tamano_total': tamano_str,
                    'pendientes': eval_stats['pendientes'],
                    'evaluados': eval_stats['evaluados'],
                    'aprobados': eval_stats['aprobados']
                })

            return Response(resultado)

        except Exception as e:
            import traceback
            return Response(
                {'error': f'Error listando municipios: {str(e)}', 'trace': traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def arbol_directorios(self, request):
        """
        Obtiene el árbol de directorios de operación para un municipio.
        Similar a productos pero para 02_oper.
        """
        municipio_id = request.query_params.get('municipio_id')

        if not municipio_id:
            return Response(
                {'error': 'Parámetro municipio_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            municipio_id = int(municipio_id)
        except ValueError:
            return Response(
                {'error': 'municipio_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar permisos
        if not self._verificar_acceso_municipio(request.user, municipio_id):
            return Response(
                {'error': 'No tiene permisos para acceder a este municipio'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            # Obtener directorios del municipio
            directorios = DirectoriosOperacion.objects.filter(
                cod_municipio=municipio_id,
                activo=True
            ).order_by('nivel_profundidad', 'nombre_directorio')

            # Construir árbol
            resultado = []
            for dir_obj in directorios:
                # Extraer jerarquía relativa desde path_directorio
                path = dir_obj.path_directorio or ''
                # Buscar después de /02_opera/ para obtener la jerarquía relativa
                jerarquia = ''
                if '/02_opera/' in path:
                    jerarquia = path.split('/02_opera/')[-1]
                elif '/02_opera' in path:
                    jerarquia = '02_opera'
                else:
                    # Usar el nombre del directorio como fallback
                    jerarquia = dir_obj.nombre_directorio

                dir_data = {
                    'id_directorio': dir_obj.cod_dir_operacion,
                    'id_disposicion': dir_obj.cod_dir_operacion,  # Alias para frontend
                    'nombre_directorio': dir_obj.nombre_directorio,
                    'path_directorio': dir_obj.path_directorio,
                    'jerarquia_completa': jerarquia,  # Campo que espera el frontend
                    'nivel': dir_obj.nivel_profundidad or 0,
                    'directorio_padre': dir_obj.directorio_padre_id,
                    'total_archivos': dir_obj.total_archivos or 0,
                    'total_subdirectorios': dir_obj.total_subdirectorios or 0,
                    'peso_total': self._formatear_tamano(dir_obj.peso_total_bytes),
                    'observaciones': dir_obj.observaciones,
                    'fecha_creacion': dir_obj.fecha_creacion.isoformat() if dir_obj.fecha_creacion else None
                }
                resultado.append(dir_data)

            return Response({
                'municipio_id': municipio_id,
                'total_directorios': len(resultado),
                'directorios': resultado
            })

        except Exception as e:
            import traceback
            return Response(
                {'error': f'Error obteniendo árbol: {str(e)}', 'trace': traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def evaluaciones(self, request):
        """
        Obtiene las evaluaciones de archivos de operación para un municipio.
        """
        municipio_id = request.query_params.get('municipio_id')

        if not municipio_id:
            return Response(
                {'error': 'Parámetro municipio_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            municipio_id = int(municipio_id)
        except ValueError:
            return Response(
                {'error': 'municipio_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar permisos
        if not self._verificar_acceso_municipio(request.user, municipio_id):
            return Response(
                {'error': 'No tiene permisos para acceder a este municipio'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            # Obtener evaluaciones
            evaluaciones = EvaluacionArchivosOperacion.objects.filter(
                cod_dir_operacion__cod_municipio=municipio_id
            ).select_related('cod_dir_operacion').order_by('-fecha_creacion')

            serializer = EvaluacionArchivosOperacionListSerializer(evaluaciones, many=True)

            # Estadísticas
            stats = {
                'total_archivos': evaluaciones.count(),
                'pendientes': evaluaciones.filter(estado_archivo='PENDIENTE').count(),
                'evaluados': evaluaciones.filter(evaluado=True).count(),
                'aprobados': evaluaciones.filter(aprobado=True).count()
            }

            return Response({
                'municipio_id': municipio_id,
                'estadisticas': stats,
                'evaluaciones': serializer.data
            })

        except Exception as e:
            import traceback
            return Response(
                {'error': f'Error obteniendo evaluaciones: {str(e)}', 'trace': traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def calificaciones(self, request):
        """
        Lista todas las calificaciones disponibles para operación.
        """
        try:
            calificaciones = CalificacionInfoOperacion.objects.all().order_by('valor')
            serializer = CalificacionInfoOperacionSerializer(calificaciones, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Error obteniendo calificaciones: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def calificacion_masiva(self, request):
        """
        Aplica calificación masiva a archivos de operación.
        Solo disponible para Super Administradores.
        """
        # Verificar permisos
        if not request.user.is_superuser:
            return Response(
                {'error': 'Solo los Super Administradores pueden realizar calificaciones masivas'},
                status=status.HTTP_403_FORBIDDEN
            )

        archivos_ids = request.data.get('archivos_ids', [])
        calificacion_id = request.data.get('calificacion_id')
        filtro = request.data.get('filtro', 'todos')
        observaciones = request.data.get('observaciones', '')

        if not archivos_ids:
            return Response(
                {'error': 'Debe proporcionar al menos un archivo'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not calificacion_id:
            return Response(
                {'error': 'Debe proporcionar una calificación'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Verificar que la calificación existe
            calificacion = CalificacionInfoOperacion.objects.get(id=calificacion_id)

            # Obtener archivos a calificar
            evaluaciones = EvaluacionArchivosOperacion.objects.filter(
                id_evaluacion__in=archivos_ids
            )

            # Aplicar filtro
            if filtro == 'no_calificados':
                evaluaciones = evaluaciones.filter(
                    Q(evaluacion_archivo=1) | Q(evaluacion_archivo__isnull=True)
                )
            elif filtro == 'excepto_aprobados':
                evaluaciones = evaluaciones.filter(aprobado=False)

            # Generar lote
            lote_id = str(uuid.uuid4())[:8]
            fecha_masiva = timezone.now()
            usuario = request.user.username

            # Actualizar archivos
            archivos_calificados = 0
            archivos_ignorados = 0
            archivos_misma_calificacion = 0

            for evaluacion in evaluaciones:
                if evaluacion.evaluacion_archivo == calificacion_id:
                    archivos_misma_calificacion += 1
                    continue

                # Guardar calificación anterior para posible restauración
                evaluacion.evaluacion_archivo_anterior = evaluacion.evaluacion_archivo
                evaluacion.evaluacion_archivo = calificacion_id
                evaluacion.lote_calificacion_masiva = lote_id
                evaluacion.fecha_calificacion_masiva = fecha_masiva
                evaluacion.usuario_evaluacion = usuario
                evaluacion.evaluado = True

                # Si la calificación es "DOCUMENTO COMPLETO" (valor = 1.0), marcar como aprobado
                if calificacion.valor == 1.0:
                    evaluacion.aprobado = True
                    evaluacion.estado_archivo = 'APROBADO'

                evaluacion.save()
                archivos_calificados += 1

            return Response({
                'message': f'{archivos_calificados} archivos calificados exitosamente',
                'archivos_calificados': archivos_calificados,
                'archivos_ignorados_por_filtro': archivos_ignorados,
                'archivos_ya_tenian_misma_calificacion': archivos_misma_calificacion,
                'total_seleccionados': len(archivos_ids),
                'lote_id': lote_id,
                'calificacion_aplicada': calificacion.concepto
            })

        except CalificacionInfoOperacion.DoesNotExist:
            return Response(
                {'error': 'Calificación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            import traceback
            return Response(
                {'error': f'Error aplicando calificación masiva: {str(e)}', 'trace': traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def restaurar_calificacion(self, request):
        """
        Restaura las calificaciones anteriores de un lote masivo.
        Solo disponible para Super Administradores.
        """
        if not request.user.is_superuser:
            return Response(
                {'error': 'Solo los Super Administradores pueden restaurar calificaciones'},
                status=status.HTTP_403_FORBIDDEN
            )

        lote_id = request.data.get('lote_id')

        if not lote_id:
            return Response(
                {'error': 'Debe proporcionar un lote_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            evaluaciones = EvaluacionArchivosOperacion.objects.filter(
                lote_calificacion_masiva=lote_id
            )

            if not evaluaciones.exists():
                return Response(
                    {'error': 'No se encontraron archivos con ese lote'},
                    status=status.HTTP_404_NOT_FOUND
                )

            archivos_restaurados = 0
            for evaluacion in evaluaciones:
                if evaluacion.evaluacion_archivo_anterior is not None:
                    evaluacion.evaluacion_archivo = evaluacion.evaluacion_archivo_anterior
                    evaluacion.evaluacion_archivo_anterior = None
                    evaluacion.lote_calificacion_masiva = None
                    evaluacion.fecha_calificacion_masiva = None
                    evaluacion.save()
                    archivos_restaurados += 1

            return Response({
                'message': f'{archivos_restaurados} archivos restaurados',
                'archivos_restaurados': archivos_restaurados
            })

        except Exception as e:
            import traceback
            return Response(
                {'error': f'Error restaurando calificaciones: {str(e)}', 'trace': traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def ultimo_lote_masivo(self, request):
        """
        Obtiene información del último lote de calificación masiva para un municipio.
        """
        municipio_id = request.query_params.get('municipio_id')

        if not municipio_id:
            return Response(
                {'error': 'Parámetro municipio_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Buscar el último lote
            ultimo = EvaluacionArchivosOperacion.objects.filter(
                cod_dir_operacion__cod_municipio=municipio_id,
                lote_calificacion_masiva__isnull=False
            ).order_by('-fecha_calificacion_masiva').first()

            if not ultimo:
                return Response({
                    'tiene_lote': False,
                    'lote_id': None,
                    'fecha': None,
                    'archivos_en_lote': 0,
                    'usuario': None
                })

            # Contar archivos en el lote
            archivos_en_lote = EvaluacionArchivosOperacion.objects.filter(
                lote_calificacion_masiva=ultimo.lote_calificacion_masiva
            ).count()

            return Response({
                'tiene_lote': True,
                'lote_id': ultimo.lote_calificacion_masiva,
                'fecha': ultimo.fecha_calificacion_masiva.isoformat() if ultimo.fecha_calificacion_masiva else None,
                'archivos_en_lote': archivos_en_lote,
                'usuario': ultimo.usuario_evaluacion
            })

        except Exception as e:
            return Response(
                {'error': f'Error obteniendo último lote: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['patch'], url_path='actualizar')
    def actualizar_evaluacion(self, request, pk=None):
        """
        Actualiza una evaluación de archivo específica.
        """
        try:
            evaluacion = EvaluacionArchivosOperacion.objects.get(id_evaluacion=pk)

            # Verificar permisos - incluir grupo Administradores
            is_admin = (
                request.user.is_superuser or
                request.user.is_staff or
                request.user.groups.filter(name='Administradores').exists()
            )

            if not is_admin:
                municipio_id = evaluacion.cod_dir_operacion.cod_municipio_id
                if not self._verificar_acceso_municipio(request.user, municipio_id):
                    return Response(
                        {'error': 'No tiene permisos para modificar esta evaluación'},
                        status=status.HTTP_403_FORBIDDEN
                    )

            # Actualizar campos
            if 'evaluacion_archivo' in request.data:
                evaluacion.evaluacion_archivo = request.data['evaluacion_archivo']

                # Actualizar estado basado en el valor de la calificación
                try:
                    cal = CalificacionInfoOperacion.objects.get(id=request.data['evaluacion_archivo'])
                    if cal.valor == 0:
                        # Sin calificación - pendiente
                        evaluacion.estado_archivo = 'PENDIENTE'
                        evaluacion.evaluado = False
                        evaluacion.aprobado = False
                    elif cal.valor == 1.0:
                        # Documento completo - aprobado
                        evaluacion.estado_archivo = 'APROBADO'
                        evaluacion.evaluado = True
                        evaluacion.aprobado = True
                    else:
                        # Calificación intermedia - evaluado pero no aprobado
                        evaluacion.estado_archivo = 'EVALUADO'
                        evaluacion.evaluado = True
                        evaluacion.aprobado = False
                except CalificacionInfoOperacion.DoesNotExist:
                    evaluacion.estado_archivo = 'PENDIENTE'
                    evaluacion.evaluado = False
                    evaluacion.aprobado = False

            if 'estado_archivo' in request.data:
                evaluacion.estado_archivo = request.data['estado_archivo']
                if request.data['estado_archivo'] == 'APROBADO':
                    evaluacion.aprobado = True

            if 'observaciones_evaluacion' in request.data:
                evaluacion.observaciones_evaluacion = request.data['observaciones_evaluacion']

            if 'ruta_completa' in request.data:
                evaluacion.ruta_completa = request.data['ruta_completa']

            evaluacion.usuario_evaluacion = request.user.username
            evaluacion.save()

            serializer = EvaluacionArchivosOperacionSerializer(evaluacion)
            return Response(serializer.data)

        except EvaluacionArchivosOperacion.DoesNotExist:
            return Response(
                {'error': 'Evaluación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            import traceback
            return Response(
                {'error': f'Error actualizando evaluación: {str(e)}', 'trace': traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar_evaluacion(self, request, pk=None):
        """
        Elimina una evaluación de archivo.
        Solo disponible para administradores.
        """
        is_admin = (
            request.user.is_superuser or
            request.user.is_staff or
            request.user.groups.filter(name='Administradores').exists()
        )
        if not is_admin:
            return Response(
                {'error': 'Solo los administradores pueden eliminar evaluaciones'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            evaluacion = EvaluacionArchivosOperacion.objects.get(id_evaluacion=pk)
            nombre = evaluacion.nombre_archivo
            evaluacion.delete()

            return Response({
                'message': f'Archivo "{nombre}" eliminado exitosamente'
            })

        except EvaluacionArchivosOperacion.DoesNotExist:
            return Response(
                {'error': 'Evaluación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error eliminando evaluación: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['delete'], url_path='eliminar-directorio')
    def eliminar_directorio(self, request):
        """
        Elimina un directorio y todos sus archivos asociados.
        Solo disponible para administradores.
        """
        is_admin = (
            request.user.is_superuser or
            request.user.is_staff or
            request.user.groups.filter(name='Administradores').exists()
        )
        if not is_admin:
            return Response(
                {'error': 'Solo los administradores pueden eliminar directorios'},
                status=status.HTTP_403_FORBIDDEN
            )

        directorio_id = request.data.get('directorio_id')

        if not directorio_id:
            return Response(
                {'error': 'Debe proporcionar directorio_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            directorio = DirectoriosOperacion.objects.get(cod_dir_operacion=directorio_id)

            # Contar archivos a eliminar
            archivos_count = EvaluacionArchivosOperacion.objects.filter(
                cod_dir_operacion=directorio
            ).count()

            # Eliminar evaluaciones
            EvaluacionArchivosOperacion.objects.filter(
                cod_dir_operacion=directorio
            ).delete()

            # Eliminar archivos originales
            ArchivosOperacion.objects.filter(
                cod_dir_operacion=directorio
            ).delete()

            nombre = directorio.nombre_directorio

            # Eliminar subdirectorios recursivamente
            def eliminar_subdirectorios(parent_id):
                subdirs = DirectoriosOperacion.objects.filter(directorio_padre_id=parent_id)
                for subdir in subdirs:
                    eliminar_subdirectorios(subdir.cod_dir_operacion)
                    EvaluacionArchivosOperacion.objects.filter(cod_dir_operacion=subdir).delete()
                    ArchivosOperacion.objects.filter(cod_dir_operacion=subdir).delete()
                    subdir.delete()

            eliminar_subdirectorios(directorio_id)

            # Eliminar el directorio principal
            directorio.delete()

            return Response({
                'message': f'Directorio "{nombre}" eliminado exitosamente',
                'archivos_eliminados': archivos_count
            })

        except DirectoriosOperacion.DoesNotExist:
            return Response(
                {'error': 'Directorio no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            import traceback
            return Response(
                {'error': f'Error eliminando directorio: {str(e)}', 'trace': traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
