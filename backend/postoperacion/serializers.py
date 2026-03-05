from rest_framework import serializers
from .models import (ComponentesPost, DisposicionPost, ArchivosPost, PathDirPost, NotificacionesPost,HistorialPropietarios,
CalificacionInfoPost, EvaluacionArchivosPost
)
from preoperacion.serializers import MunicipiosSerializer, MunicipiosSimpleSerializer
from preoperacion.models import (Municipios)

class ComponentesPostSerializer(serializers.ModelSerializer):
    """
    ⚠️ SERIALIZER DEPRECATED - Mantenido solo para compatibilidad
    Ya no se usa en la nueva arquitectura POST V2
    """
    class Meta:
        model = ComponentesPost
        fields = '__all__'

class DisposicionPostSerializer(serializers.ModelSerializer):
    """
    🔄 SERIALIZER ACTUALIZADO POST V2 - SIN dependencia de componentes_post
    """
    cod_municipio_info = MunicipiosSerializer(source='cod_municipio', read_only=True)
    # ❌ ELIMINADO: id_componente_info = ComponentesPostSerializer(source='id_componente', read_only=True)
    
    # 🆕 NUEVOS CAMPOS CALCULADOS para POST V2
    nombre_directorio = serializers.SerializerMethodField()
    nivel_jerarquia = serializers.SerializerMethodField()
    total_archivos = serializers.SerializerMethodField()
    ruta_relativa = serializers.SerializerMethodField()
    
    class Meta:
        model = DisposicionPost
        fields = [
            'id_disposicion', 'cod_municipio', 'cod_municipio_info',
            'dispuesto', 'fecha_disposicion', 'ruta_acceso', 'evaluado', 
            'aprobado', 'observaciones',
            # 🆕 Nuevos campos POST V2
            'nombre_directorio', 'nivel_jerarquia', 'total_archivos', 'ruta_relativa'
        ]
    
    def get_nombre_directorio(self, obj):
        """Obtiene el nombre del directorio"""
        return obj.get_nombre_directorio()
    
    def get_nivel_jerarquia(self, obj):
        """Obtiene el nivel de jerarquía"""
        return obj.get_nivel_jerarquia()
    
    def get_total_archivos(self, obj):
        """Cuenta los archivos relacionados"""
        return obj.archivos_relacionados.count()
    
    def get_ruta_relativa(self, obj):
        """Genera una ruta relativa más legible"""
        if obj.ruta_acceso:
            partes = obj.ruta_acceso.split('\\')
            if len(partes) > 3:
                return '\\'.join(partes[-3:])  # Últimas 3 partes
            return obj.ruta_acceso
        return "Sin ruta"

class DisposicionPostSimpleSerializer(serializers.ModelSerializer):
    """
    🔄 SERIALIZER SIMPLE ACTUALIZADO - SIN componentes
    """
    municipio_nombre = serializers.CharField(source='cod_municipio.nom_municipio', read_only=True)
    # ❌ ELIMINADO: componente_nombre = serializers.CharField(source='id_componente.nombre_componente', read_only=True)
    
    # 🆕 NUEVOS CAMPOS POST V2
    nombre_directorio = serializers.SerializerMethodField()
    total_archivos = serializers.SerializerMethodField()
    
    class Meta:
        model = DisposicionPost
        fields = [
            'id_disposicion', 'cod_municipio', 'municipio_nombre',
            # ❌ ELIMINADO: 'id_componente', 'componente_nombre',
            'dispuesto', 'evaluado', 'aprobado', 'fecha_disposicion',
            'ruta_acceso', 'nombre_directorio', 'total_archivos'
        ]
    
    def get_nombre_directorio(self, obj):
        return obj.get_nombre_directorio()
    
    def get_total_archivos(self, obj):
        return obj.archivos_relacionados.count()

class ArchivosPostSerializer(serializers.ModelSerializer):
    """
    🔄 SERIALIZER ACTUALIZADO - Con nueva relación a disposición
    """
    disposicion_info = DisposicionPostSimpleSerializer(source='id_disposicion', read_only=True)
    
    # 🆕 NUEVOS CAMPOS CALCULADOS
    municipio_info = serializers.SerializerMethodField()
    directorio_contenedor = serializers.SerializerMethodField()
    extension_archivo = serializers.SerializerMethodField()
    
    class Meta:
        model = ArchivosPost
        fields = [
            'id_archivo', 'id_disposicion', 'nombre_archivo', 'ruta_completa',
            'fecha_disposicion', 'observacion', 'hash_contenido', 
            'usuario_windows', 'peso_memoria',
            'disposicion_info', 'municipio_info', 'directorio_contenedor', 'extension_archivo'
        ]
    
    def get_municipio_info(self, obj):
        """Obtiene información del municipio"""
        municipio = obj.get_municipio()
        if municipio:
            return {
                'cod_municipio': municipio.cod_municipio,
                'nom_municipio': municipio.nom_municipio,
                'cod_depto': municipio.cod_depto.cod_depto if municipio.cod_depto else None,
                'nom_depto': municipio.cod_depto.nom_depto if municipio.cod_depto else None
            }
        return None
    
    def get_directorio_contenedor(self, obj):
        """Obtiene el directorio contenedor"""
        return obj.get_directorio_contenedor()
    
    def get_extension_archivo(self, obj):
        """Obtiene la extensión del archivo"""
        if obj.nombre_archivo and '.' in obj.nombre_archivo:
            return obj.nombre_archivo.split('.')[-1].upper()
        return "SIN EXTENSION"

class PathDirPostSerializer(serializers.ModelSerializer):
    municipio_info = MunicipiosSerializer(source='cod_municipio', read_only=True)
    
    class Meta:
        model = PathDirPost
        fields = '__all__'

class NotificacionesPostSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones de postoperación"""
    
    class Meta:
        model = NotificacionesPost
        fields = [
            'id', 'tipo_entidad', 'id_entidad', 'accion', 
            'descripcion', 'datos_contexto', 'fecha_cambio', 'leido'
        ]
        read_only_fields = ['id', 'fecha_cambio']
    
    def to_representation(self, instance):
        """Personalizar la representación de salida"""
        data = super().to_representation(instance)
        
        # Asegurar que datos_contexto sea un dict si es None
        if data.get('datos_contexto') is None:
            data['datos_contexto'] = {}
            
        # Agregar campos calculados si es necesario
        data['tipo_sistema'] = 'postoperacion'
        
        return data

class HistorialPropietariosSerializer(serializers.ModelSerializer):
    estado = serializers.SerializerMethodField()
    duracion = serializers.SerializerMethodField()
    nombre_archivo = serializers.SerializerMethodField()
    
    class Meta:
        model = HistorialPropietarios
        fields = [
            'id', 'tipo_archivo', 'id_archivo', 'id_notificacion', 
            'propietario_anterior', 'propietario_nuevo', 'fecha_inicio', 
            'fecha_fin', 'detalles', 'estado', 'duracion', 'nombre_archivo'
        ]
        read_only_fields = ['id', 'fecha_inicio']
    
    def get_estado(self, obj):
        """Determina si es el propietario actual o anterior"""
        return "Propietario actual" if obj.fecha_fin is None else "Propietario anterior"
    
    def get_duracion(self, obj):
        """Calcula la duración del período de propiedad - VERSIÓN ULTRA ROBUSTA"""
        try:
            if not obj.fecha_inicio:
                return "Sin fecha de inicio"
            
            # ✅ ENFOQUE SIMPLIFICADO: Convertir todo a datetime naive
            from datetime import datetime, timezone as dt_timezone
            
            # Obtener fecha de inicio como datetime naive
            if hasattr(obj.fecha_inicio, 'replace') and obj.fecha_inicio.tzinfo:
                # Es un datetime con timezone, convertir a naive UTC
                inicio = obj.fecha_inicio.astimezone(dt_timezone.utc).replace(tzinfo=None)
            elif hasattr(obj.fecha_inicio, 'date'):
                # Es un datetime sin timezone
                inicio = obj.fecha_inicio.replace(tzinfo=None) if hasattr(obj.fecha_inicio, 'tzinfo') else obj.fecha_inicio
            else:
                # Es string, intentar parsearlo
                if isinstance(obj.fecha_inicio, str):
                    inicio = datetime.fromisoformat(obj.fecha_inicio.replace('Z', '+00:00')).replace(tzinfo=None)
                else:
                    return "Formato de fecha inválido"
            
            # Obtener fecha de fin
            if obj.fecha_fin:
                if hasattr(obj.fecha_fin, 'replace') and obj.fecha_fin.tzinfo:
                    fin = obj.fecha_fin.astimezone(dt_timezone.utc).replace(tzinfo=None)
                elif hasattr(obj.fecha_fin, 'date'):
                    fin = obj.fecha_fin.replace(tzinfo=None) if hasattr(obj.fecha_fin, 'tzinfo') else obj.fecha_fin
                else:
                    if isinstance(obj.fecha_fin, str):
                        fin = datetime.fromisoformat(obj.fecha_fin.replace('Z', '+00:00')).replace(tzinfo=None)
                    else:
                        fin = datetime.now()
            else:
                # Usar fecha actual como fin
                fin = datetime.now()
            
            # Calcular diferencia
            diferencia = fin - inicio
            dias_totales = diferencia.days
            
            # ✅ FORMATEO SIMPLE Y SEGURO
            if dias_totales < 0:
                return "Fecha inválida"
            elif dias_totales == 0:
                return "0 días"
            elif dias_totales == 1:
                return "1 día"
            elif dias_totales < 30:
                return f"{dias_totales} días"
            elif dias_totales < 365:
                meses = dias_totales // 30
                dias_restantes = dias_totales % 30
                
                if meses == 1:
                    if dias_restantes == 0:
                        return "1 mes"
                    elif dias_restantes == 1:
                        return "1 mes, 1 día"
                    else:
                        return f"1 mes, {dias_restantes} días"
                else:
                    if dias_restantes == 0:
                        return f"{meses} meses"
                    elif dias_restantes == 1:
                        return f"{meses} meses, 1 día"
                    else:
                        return f"{meses} meses, {dias_restantes} días"
            else:
                años = dias_totales // 365
                resto = dias_totales % 365
                
                if años == 1:
                    if resto == 0:
                        return "1 año"
                    elif resto < 30:
                        return f"1 año, {resto} días"
                    else:
                        meses = resto // 30
                        return f"1 año, {meses} {'mes' if meses == 1 else 'meses'}"
                else:
                    if resto == 0:
                        return f"{años} años"
                    elif resto < 30:
                        return f"{años} años, {resto} días"
                    else:
                        meses = resto // 30
                        return f"{años} años, {meses} {'mes' if meses == 1 else 'meses'}"
                
        except Exception as e:
            # ✅ DEBUG: Imprimir más información del error
            print(f"❌ Error calculando duración para objeto {getattr(obj, 'id', 'N/A')}: {e}")
            print(f"   fecha_inicio tipo: {type(obj.fecha_inicio)}, valor: {obj.fecha_inicio}")
            print(f"   fecha_fin tipo: {type(obj.fecha_fin) if obj.fecha_fin else 'None'}, valor: {obj.fecha_fin}")
            
            # ✅ FALLBACK SÚPER SIMPLE
            try:
                if obj.fecha_inicio and hasattr(obj.fecha_inicio, 'date'):
                    from datetime import date
                    hoy = date.today()
                    if hasattr(obj.fecha_inicio, 'date'):
                        inicio_date = obj.fecha_inicio.date()
                    else:
                        inicio_date = obj.fecha_inicio
                    
                    dias = (hoy - inicio_date).days
                    if dias >= 0:
                        return f"{dias} días (aprox)"
                
                return "No calculable"
            except:
                return "Error de fecha"
    
    def get_nombre_archivo(self, obj):
        """Extrae el nombre del archivo de los detalles JSON"""
        try:
            if obj.detalles and isinstance(obj.detalles, dict):
                return obj.detalles.get('nombre_archivo', 'Sin nombre')
            return "Sin nombre"
        except Exception as e:
            print(f"❌ Error obteniendo nombre archivo: {e}")
            return "Error obteniendo nombre"
    
    def to_representation(self, instance):
        """Personalizar la representación de salida - CORREGIDO"""
        try:
            data = super().to_representation(instance)
            
            # ✅ CORRECCIÓN: Formatear fechas de manera segura
            if data.get('fecha_inicio'):
                try:
                    if isinstance(instance.fecha_inicio, str):
                        data['fecha_inicio_formateada'] = instance.fecha_inicio
                    else:
                        data['fecha_inicio_formateada'] = instance.fecha_inicio.strftime('%d/%m/%Y %H:%M:%S')
                except Exception as e:
                    print(f"❌ Error formateando fecha_inicio: {e}")
                    data['fecha_inicio_formateada'] = str(instance.fecha_inicio)
            
            if data.get('fecha_fin'):
                try:
                    if isinstance(instance.fecha_fin, str):
                        data['fecha_fin_formateada'] = instance.fecha_fin
                    else:
                        data['fecha_fin_formateada'] = instance.fecha_fin.strftime('%d/%m/%Y %H:%M:%S')
                except Exception as e:
                    print(f"❌ Error formateando fecha_fin: {e}")
                    data['fecha_fin_formateada'] = str(instance.fecha_fin)
            else:
                data['fecha_fin_formateada'] = None
            
            return data
            
        except Exception as e:
            print(f"❌ Error en to_representation: {e}")
            # Devolver representación mínima en caso de error
            return {
                'id': instance.id,
                'tipo_archivo': instance.tipo_archivo,
                'id_archivo': instance.id_archivo,
                'propietario_anterior': instance.propietario_anterior,
                'propietario_nuevo': instance.propietario_nuevo,
                'fecha_inicio': str(instance.fecha_inicio),
                'fecha_fin': str(instance.fecha_fin) if instance.fecha_fin else None,
                'estado': "Propietario actual" if instance.fecha_fin is None else "Propietario anterior",
                'duracion': "Error calculando",
                'nombre_archivo': "Error obteniendo"
            }


class CalificacionInfoPostSerializer(serializers.ModelSerializer):
    """Serializer para CalificacionInfoPost con campos calculados"""
    
    porcentaje = serializers.SerializerMethodField()
    nivel_calidad = serializers.SerializerMethodField()
    valor_display = serializers.SerializerMethodField()
    archivos_evaluados_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CalificacionInfoPost
        fields = [
            'id', 'concepto', 'valor', 'valor_display',
            'porcentaje', 'nivel_calidad', 'archivos_evaluados_count'
        ]
    
    def get_porcentaje(self, obj):
        return obj.get_porcentaje()
    
    def get_nivel_calidad(self, obj):
        return obj.get_nivel_calidad()
    
    def get_valor_display(self, obj):
        return f"{float(obj.valor):.2f}"
    
    def get_archivos_evaluados_count(self, obj):
        """Retorna la cantidad de archivos evaluados con esta calificación"""
        try:
            return obj.get_archivos_evaluados_count()
        except:
            return 0
        
class CalificacionInfoPostCreateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para creación"""
    
    class Meta:
        model = CalificacionInfoPost
        fields = ['concepto', 'valor']
    
    def validate(self, data):
        """Validación a nivel de objeto"""
        # Verificar que no exista un concepto duplicado
        if CalificacionInfoPost.objects.filter(
            concepto__iexact=data['concepto']
        ).exists():
            raise serializers.ValidationError(
                "Ya existe una calificación con este concepto"
            )
        return data

class CalificacionInfoPostListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listados"""
    
    nivel_calidad = serializers.SerializerMethodField()
    
    class Meta:
        model = CalificacionInfoPost
        fields = [
            'id',
            'concepto',
            'valor',
            'nivel_calidad'
        ]
    
    def get_nivel_calidad(self, obj):
        return obj.get_nivel_calidad()
    

class EvaluacionArchivosPostSerializer(serializers.ModelSerializer):
    """
    🔄 SERIALIZER ACTUALIZADO - SIN referencias a componentes
    """
    
    # 🔗 CAMPOS RELACIONADOS (READ ONLY)
    disposicion_info = DisposicionPostSimpleSerializer(source='id_disposicion', read_only=True)
    evaluacion_info = CalificacionInfoPostSerializer(source='evaluacion_archivo', read_only=True)
    
    # 📊 CAMPOS CALCULADOS (ACTUALIZADOS SIN COMPONENTE)
    municipio_nombre = serializers.CharField(source='id_disposicion.cod_municipio.nom_municipio', read_only=True)
    # ❌ ELIMINADO: componente_nombre = serializers.CharField(source='id_disposicion.id_componente.nombre_componente', read_only=True)
    
    # 🆕 NUEVOS CAMPOS POST V2
    directorio_nombre = serializers.SerializerMethodField()
    directorio_ruta = serializers.SerializerMethodField()
    porcentaje_evaluacion = serializers.SerializerMethodField()
    nivel_calidad = serializers.SerializerMethodField()
    archivo_original = serializers.SerializerMethodField()
    
    # 🎨 CAMPOS DE DISPLAY
    estado_archivo_display = serializers.CharField(source='get_estado_archivo_display', read_only=True)
    fecha_creacion_formateada = serializers.SerializerMethodField()
    fecha_actualizacion_formateada = serializers.SerializerMethodField()

    # 🆕 CAMPO PARA PERMISOS DE ELIMINACIÓN
    subido_por_plataforma = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluacionArchivosPost
        fields = [
            # Campos principales
            'id_evaluacion', 'id_archivo', 'id_disposicion',
            'nombre_archivo', 'ruta_completa', 'fecha_disposicion',
            'observacion_original', 'hash_contenido', 'usuario_windows', 'peso_memoria',
            
            # Campos de evaluación
            'evaluacion_archivo', 'estado_archivo', 'observaciones_evaluacion',
            
            # Campos de auditoría
            'fecha_creacion', 'fecha_actualizacion', 'usuario_evaluacion',
            
            # evaluacion
            'evaluado', 'aprobado',
            # Campos relacionados
            'disposicion_info', 'evaluacion_info',
            
            # Campos calculados (ACTUALIZADOS)
            'municipio_nombre', 'directorio_nombre', 'directorio_ruta',
            'porcentaje_evaluacion', 'nivel_calidad', 'archivo_original',
            
            # Campos de display
            'estado_archivo_display', 'fecha_creacion_formateada', 'fecha_actualizacion_formateada',

            # Campo para permisos de eliminación (usuario que subió desde plataforma)
            'subido_por_plataforma'
        ]
        read_only_fields = [
            'id_evaluacion', 'fecha_creacion', 'fecha_actualizacion',
            'id_archivo',  # No se debe modificar una vez creado
        ]
    
    def get_directorio_nombre(self, obj):
        """🆕 Obtiene el nombre del directorio contenedor"""
        try:
            return obj.get_directorio_contenedor()
        except:
            return "Sin directorio"
    
    def get_directorio_ruta(self, obj):
        """🆕 Obtiene la ruta del directorio contenedor"""
        try:
            if obj.id_disposicion:
                return obj.id_disposicion.ruta_acceso
            return "Sin ruta"
        except:
            return "Error obteniendo ruta"
    
    def get_porcentaje_evaluacion(self, obj):
        """Obtiene el porcentaje de evaluación"""
        try:
            return obj.get_porcentaje_evaluacion()
        except:
            return 0
    
    def get_nivel_calidad(self, obj):
        """Obtiene el nivel de calidad"""
        try:
            return obj.get_nivel_calidad()
        except:
            return "Sin evaluación"
    
    def get_archivo_original(self, obj):
        """Obtiene información básica del archivo original"""
        try:
            archivo_original = obj.get_archivo_original()
            if archivo_original:
                return {
                    'id_archivo': archivo_original.id_archivo,
                    'nombre_archivo': archivo_original.nombre_archivo,
                    'fecha_disposicion': archivo_original.fecha_disposicion
                }
            return None
        except:
            return None
    
    def get_fecha_creacion_formateada(self, obj):
        """Formatea la fecha de creación"""
        try:
            if obj.fecha_creacion:
                return obj.fecha_creacion.strftime('%d/%m/%Y %H:%M:%S')
            return None
        except:
            return None
    
    def get_fecha_actualizacion_formateada(self, obj):
        """Formatea la fecha de actualización"""
        try:
            if obj.fecha_actualizacion:
                return obj.fecha_actualizacion.strftime('%d/%m/%Y %H:%M:%S')
            return None
        except:
            return None

    def get_subido_por_plataforma(self, obj):
        """
        Obtiene el username del usuario que subió el archivo desde la plataforma web.
        Busca en AuditoriaArchivos el registro de UPLOAD más reciente para este archivo.
        Retorna None si el archivo no fue subido desde la plataforma (ej: copiado por NAS).
        """
        try:
            from .models import AuditoriaArchivos

            # Buscar el registro de UPLOAD más reciente para esta ruta
            ruta_archivo = obj.ruta_completa
            if not ruta_archivo:
                return None

            # Normalizar la ruta para búsqueda (puede estar en formato Windows o Linux)
            ruta_buscar = ruta_archivo.replace('\\', '/')
            if ruta_buscar.startswith('//repositorio/DirGesCat'):
                ruta_buscar = ruta_buscar.replace('//repositorio/DirGesCat', '/mnt/repositorio', 1)

            # Buscar el registro de UPLOAD
            registro = AuditoriaArchivos.objects.filter(
                ruta_completa=ruta_buscar,
                accion='UPLOAD',
                plataforma='WEB'
            ).order_by('-fecha_accion').first()

            if registro:
                return registro.usuario

            return None
        except Exception as e:
            return None

    def validate_estado_archivo(self, value):
        """Valida las transiciones de estado"""
        if self.instance:  # Si es una actualización
            estado_actual = self.instance.estado_archivo
            
            # Definir transiciones válidas
            transiciones_validas = {
                'PENDIENTE': ['EN_REVISION', 'APROBADO', 'RECHAZADO'],
                'EN_REVISION': ['APROBADO', 'RECHAZADO', 'REQUIERE_AJUSTES'],
                'REQUIERE_AJUSTES': ['EN_REVISION', 'APROBADO', 'RECHAZADO'],
                'APROBADO': [],  # No se puede cambiar desde aprobado
                'RECHAZADO': ['EN_REVISION'],  # Solo se puede volver a revisar
            }
            
            if value != estado_actual and value not in transiciones_validas.get(estado_actual, []):
                raise serializers.ValidationError(
                    f"No se puede cambiar de '{estado_actual}' a '{value}'"
                )
        
        return value
    
    def update(self, instance, validated_data):
        """Personaliza la actualización para manejar cambios de estado"""
        # Si se está cambiando el estado, registrar el usuario
        if 'estado_archivo' in validated_data:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                validated_data['usuario_evaluacion'] = request.user.username
        
        return super().update(instance, validated_data)


class EvaluacionArchivosPostSimpleSerializer(serializers.ModelSerializer):
    """
    🔄 SERIALIZER SIMPLE ACTUALIZADO - SIN componente
    """
    
    municipio_nombre = serializers.CharField(source='id_disposicion.cod_municipio.nom_municipio', read_only=True)
    # ❌ ELIMINADO: componente_nombre = serializers.CharField(source='id_disposicion.id_componente.nombre_componente', read_only=True)
    
    # 🆕 NUEVOS CAMPOS POST V2
    directorio_nombre = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_archivo_display', read_only=True)
    nivel_calidad = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluacionArchivosPost
        fields = [
            'id_evaluacion', 'id_archivo', 'nombre_archivo',
            'estado_archivo', 'estado_display', 'evaluacion_archivo',
            'municipio_nombre', 'directorio_nombre', 'nivel_calidad',
            'fecha_creacion', 'usuario_evaluacion', 'evaluado', 'aprobado',
        ]
    
    def get_directorio_nombre(self, obj):
        """Obtiene el nombre del directorio"""
        try:
            if obj.id_disposicion:
                return obj.id_disposicion.get_nombre_directorio()
            return "Sin directorio"
        except:
            return "Error directorio"
    
    def get_nivel_calidad(self, obj):
        try:
            return obj.get_nivel_calidad()
        except:
            return "Sin evaluación"


class EvaluacionArchivosPostCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para creación (casos especiales donde no se use el trigger)
    """
    
    class Meta:
        model = EvaluacionArchivosPost
        fields = [
            'id_archivo', 'id_disposicion', 'nombre_archivo', 'ruta_completa',
            'fecha_disposicion', 'observacion_original', 'hash_contenido',
            'usuario_windows', 'peso_memoria', 'evaluacion_archivo',
            'estado_archivo', 'observaciones_evaluacion', 'usuario_evaluacion',
            'evaluado', 'aprobado',
        ]
    
    def create(self, instance):
        """Personaliza la creación"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            instance['usuario_evaluacion'] = request.user.username
        
        return super().create(instance)


class EvaluacionArchivosPostUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer específico para actualizar evaluaciones
    """
    
    class Meta:
        model = EvaluacionArchivosPost
        fields = [
            'evaluacion_archivo', 'estado_archivo', 
            'observaciones_evaluacion', 'usuario_evaluacion',
            'evaluado', 'aprobado',
        ]
        read_only_fields = ['usuario_evaluacion']
    
    def update(self, instance, validated_data):
        """Actualiza automáticamente el usuario evaluador"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['usuario_evaluacion'] = request.user.username
        
        return super().update(instance, validated_data)


class EstadisticasEvaluacionSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de evaluación
    """
    
    total = serializers.IntegerField()
    pendientes = serializers.IntegerField()
    en_revision = serializers.IntegerField()
    aprobados = serializers.IntegerField()
    rechazados = serializers.IntegerField()
    requiere_ajustes = serializers.IntegerField()
    
    # Campos calculados
    porcentaje_pendientes = serializers.SerializerMethodField()
    porcentaje_aprobados = serializers.SerializerMethodField()
    porcentaje_completados = serializers.SerializerMethodField()
    
    def get_porcentaje_pendientes(self, obj):
        total = obj.get('total', 0)
        if total > 0:
            return round((obj.get('pendientes', 0) / total) * 100, 2)
        return 0
    
    def get_porcentaje_aprobados(self, obj):
        total = obj.get('total', 0)
        if total > 0:
            return round((obj.get('aprobados', 0) / total) * 100, 2)
        return 0
    
    def get_porcentaje_completados(self, obj):
        total = obj.get('total', 0)
        if total > 0:
            completados = obj.get('aprobados', 0) + obj.get('rechazados', 0)
            return round((completados / total) * 100, 2)
        return 0


class EvaluacionesPorMunicipioSerializer(serializers.Serializer):
    """
    🔄 SERIALIZER ACTUALIZADO - SIN componente
    """
    
    id_disposicion__cod_municipio__cod_municipio = serializers.IntegerField()
    id_disposicion__cod_municipio__nom_municipio = serializers.CharField()
    total_evaluaciones = serializers.IntegerField()
    pendientes = serializers.IntegerField()
    aprobados = serializers.IntegerField()
    
    # Rename fields para mejor legibilidad
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        return {
            'cod_municipio': data['id_disposicion__cod_municipio__cod_municipio'],
            'nom_municipio': data['id_disposicion__cod_municipio__nom_municipio'],
            'total_evaluaciones': data['total_evaluaciones'],
            'pendientes': data['pendientes'],
            'aprobados': data['aprobados'],
            'porcentaje_aprobados': round(
                (data['aprobados'] / data['total_evaluaciones']) * 100, 2
            ) if data['total_evaluaciones'] > 0 else 0
        }