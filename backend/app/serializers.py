from rest_framework import serializers

from .models import (
    PathDirOpera, PathDirTransv, DirectoriosOperacion, 
    DirectoriosTransv, ArchivosOperacion, ArchivosTransv,
    ScriptExecution, BackupFile
)

class BackupFileSerializer(serializers.ModelSerializer):
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = BackupFile
        fields = ['id', 'filename', 'filepath', 'file_size', 'file_size_mb', 'created_at']
    
    def get_file_size_mb(self, obj):
        return round(obj.file_size / (1024 * 1024), 2) if obj.file_size else 0

class ScriptExecutionSerializer(serializers.ModelSerializer):
    backup_files = BackupFileSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    duration_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = ScriptExecution
        fields = [
            'id', 'script_name', 'status', 'user_name', 
            'created_at', 'updated_at', 'started_at', 'completed_at',
            'output_file', 'error_message', 'output_log', 
            'backup_files', 'duration_seconds'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_duration_seconds(self, obj):
        if obj.started_at and obj.completed_at:
            duration = obj.completed_at - obj.started_at
            return duration.total_seconds()
        return None

class ScriptExecutionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScriptExecution
        fields = ['script_name']
    
    def validate_script_name(self, value):
        valid_scripts = ['backup_db', 'llenar_datos']
        if value not in valid_scripts:
            raise serializers.ValidationError(f"Script debe ser uno de: {valid_scripts}")
        return value

class BackupStatusSerializer(serializers.Serializer):
    total_executions = serializers.IntegerField()
    successful_executions = serializers.IntegerField()
    failed_executions = serializers.IntegerField()
    last_execution = ScriptExecutionSerializer(read_only=True)
    backup_files_count = serializers.IntegerField()
    total_backup_size_mb = serializers.FloatField()

class ScriptStatusSerializer(serializers.Serializer):
    script_name = serializers.CharField()
    is_available = serializers.BooleanField()
    last_execution = ScriptExecutionSerializer(read_only=True)
    total_executions = serializers.IntegerField()
    successful_executions = serializers.IntegerField()
    failed_executions = serializers.IntegerField()



class PathDirOperaSerializer(serializers.ModelSerializer):
    """Serializer para rutas de directorios operativos"""
    
    class Meta:
        model = PathDirOpera
        fields = ['id', 'cod_municipio', 'path', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']


class PathDirTransvSerializer(serializers.ModelSerializer):
    """Serializer para rutas de directorios postoperativos"""
    
    class Meta:
        model = PathDirTransv
        fields = ['id', 'cod_municipio', 'path', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']


class DirectoriosOperacionSerializer(serializers.ModelSerializer):
    """Serializer para directorios de operación"""
    
    directorio_padre_nombre = serializers.CharField(
        source='directorio_padre.nombre_directorio', 
        read_only=True
    )
    peso_total_mb = serializers.SerializerMethodField()
    hijos = serializers.SerializerMethodField()
    
    class Meta:
        model = DirectoriosOperacion
        fields = [
            'cod_dir_operacion', 'cod_municipio', 'path_directorio', 
            'nombre_directorio', 'directorio_padre', 'directorio_padre_nombre',
            'nivel_profundidad', 'fecha_creacion', 'fecha_ultima_modificacion',
            'usuario_propietario', 'total_archivos', 'total_subdirectorios',
            'peso_total_bytes', 'peso_total_mb', 'observaciones', 'activo',
            'fecha_registro', 'fecha_actualizacion', 'hijos'
        ]
        read_only_fields = [
            'cod_dir_operacion', 'fecha_registro', 'fecha_actualizacion',
            'directorio_padre_nombre', 'peso_total_mb', 'hijos'
        ]
    
    def get_peso_total_mb(self, obj):
        """Convierte bytes a MB"""
        if obj.peso_total_bytes:
            return round(obj.peso_total_bytes / (1024 * 1024), 2)
        return 0
    
    def get_hijos(self, obj):
        """Obtiene subdirectorios hijos"""
        hijos = DirectoriosOperacion.objects.filter(directorio_padre=obj)
        return DirectoriosOperacionListSerializer(hijos, many=True).data


# 🔧 CORREGIDO: Agregado path_directorio
class DirectoriosOperacionListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas de directorios de operación"""
    
    peso_total_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = DirectoriosOperacion
        fields = [
            'cod_dir_operacion', 'nombre_directorio', 'path_directorio',  # ← AGREGADO path_directorio
            'nivel_profundidad', 'total_archivos', 'total_subdirectorios', 
            'peso_total_mb', 'activo'
        ]
    
    def get_peso_total_mb(self, obj):
        if obj.peso_total_bytes:
            return round(obj.peso_total_bytes / (1024 * 1024), 2)
        return 0


class DirectoriosTransvSerializer(serializers.ModelSerializer):
    """Serializer para directorios transversales"""
    
    directorio_padre_nombre = serializers.CharField(
        source='directorio_padre.nombre_directorio', 
        read_only=True
    )
    peso_total_mb = serializers.SerializerMethodField()
    hijos = serializers.SerializerMethodField()
    
    class Meta:
        model = DirectoriosTransv
        fields = [
            'cod_dir_transv', 'cod_municipio', 'nombre_directorio',
            'ruta_completa', 'ruta_relativa', 'nivel_jerarquia',
            'directorio_padre', 'directorio_padre_nombre', 'total_archivos',
            'total_subdirectorios', 'peso_total_bytes', 'peso_total_mb',
            'fecha_creacion', 'fecha_actualizacion', 'fecha_ultimo_escaneo',
            'activo', 'observaciones', 'metadatos', 'hijos'
        ]
        read_only_fields = [
            'cod_dir_transv', 'fecha_creacion', 'fecha_actualizacion',
            'directorio_padre_nombre', 'peso_total_mb', 'hijos'
        ]
    
    def get_peso_total_mb(self, obj):
        """Convierte bytes a MB"""
        if obj.peso_total_bytes:
            return round(obj.peso_total_bytes / (1024 * 1024), 2)
        return 0
    
    def get_hijos(self, obj):
        """Obtiene subdirectorios hijos"""
        hijos = DirectoriosTransv.objects.filter(directorio_padre=obj)
        return DirectoriosTransvListSerializer(hijos, many=True).data


# 🔧 CORREGIDO: Agregado ruta_completa
class DirectoriosTransvListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas de directorios transversales"""
    
    peso_total_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = DirectoriosTransv
        fields = [
            'cod_dir_transv', 'nombre_directorio', 'ruta_completa',  # ← AGREGADO ruta_completa
            'nivel_jerarquia', 'total_archivos', 'total_subdirectorios', 
            'peso_total_mb', 'activo'
        ]
    
    def get_peso_total_mb(self, obj):
        if obj.peso_total_bytes:
            return round(obj.peso_total_bytes / (1024 * 1024), 2)
        return 0


class ArchivosOperacionSerializer(serializers.ModelSerializer):
    """Serializer para archivos de operación"""
    
    directorio_nombre = serializers.CharField(
        source='cod_dir_operacion.nombre_directorio', 
        read_only=True
    )
    municipio_codigo = serializers.IntegerField(
        source='cod_dir_operacion.cod_municipio',
        read_only=True
    )
    peso_memoria_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = ArchivosOperacion
        fields = [
            'id_archivo_operacion', 'cod_dir_operacion', 'directorio_nombre',
            'municipio_codigo', 'path_file', 'nombre_archivo', 'extension',
            'fecha_disposicion', 'usuario_windows', 'peso_memoria', 'peso_memoria_mb',
            'tipo_archivo', 'hash_archivo', 'observaciones', 'activo',
            'fecha_registro', 'fecha_actualizacion'
        ]
        read_only_fields = [
            'id_archivo_operacion', 'fecha_registro', 'fecha_actualizacion',
            'directorio_nombre', 'municipio_codigo', 'peso_memoria_mb'
        ]
    
    def get_peso_memoria_mb(self, obj):
        """Convierte bytes a MB"""
        return obj.peso_memoria_mb


# 🔧 CORREGIDO: Agregado path_file
class ArchivosOperacionListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas de archivos de operación"""
    
    directorio_nombre = serializers.CharField(
        source='cod_dir_operacion.nombre_directorio', 
        read_only=True
    )
    peso_memoria_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = ArchivosOperacion
        fields = [
            'id_archivo_operacion', 'nombre_archivo', 'path_file',  # ← AGREGADO path_file
            'extension', 'directorio_nombre', 'peso_memoria_mb', 
            'tipo_archivo', 'activo'
        ]
    
    def get_peso_memoria_mb(self, obj):
        return obj.peso_memoria_mb


class ArchivosTransvSerializer(serializers.ModelSerializer):
    """Serializer para archivos transversales"""
    
    directorio_nombre = serializers.CharField(
        source='cod_dir_transv.nombre_directorio', 
        read_only=True
    )
    municipio_codigo = serializers.IntegerField(
        source='cod_dir_transv.cod_municipio',
        read_only=True
    )
    peso_memoria_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = ArchivosTransv
        fields = [
            'id_archivo_transv', 'cod_dir_transv', 'directorio_nombre',
            'municipio_codigo', 'nombre_archivo', 'path_file', 'extension',
            'fecha_disposicion', 'usuario_windows', 'peso_memoria', 'peso_memoria_mb',
            'observaciones', 'es_directorio_especial', 'fecha_creacion',
            'fecha_actualizacion', 'fecha_ultimo_escaneo', 'activo', 'metadatos'
        ]
        read_only_fields = [
            'id_archivo_transv', 'fecha_creacion', 'fecha_actualizacion',
            'directorio_nombre', 'municipio_codigo', 'peso_memoria_mb'
        ]
    
    def get_peso_memoria_mb(self, obj):
        """Convierte bytes a MB"""
        return obj.peso_memoria_mb


# 🔧 CORREGIDO: Agregado path_file
class ArchivosTransvListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas de archivos transversales"""
    
    directorio_nombre = serializers.CharField(
        source='cod_dir_transv.nombre_directorio', 
        read_only=True
    )
    peso_memoria_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = ArchivosTransv
        fields = [
            'id_archivo_transv', 'nombre_archivo', 'path_file',  # ← AGREGADO path_file
            'extension', 'directorio_nombre', 'peso_memoria_mb', 
            'es_directorio_especial', 'activo'
        ]
    
    def get_peso_memoria_mb(self, obj):
        return obj.peso_memoria_mb


# Serializers para estadísticas y resúmenes

class MunicipioPermitidoSerializer(serializers.Serializer):
    """Serializer para municipios permitidos por usuario"""
    
    cod_municipio = serializers.IntegerField()
    nom_municipio = serializers.CharField()
    es_admin = serializers.BooleanField()
    total_directorios_opera = serializers.IntegerField(required=False)
    total_directorios_transv = serializers.IntegerField(required=False)
    total_archivos_opera = serializers.IntegerField(required=False)
    total_archivos_transv = serializers.IntegerField(required=False)


class UsuarioMunicipiosSerializer(serializers.Serializer):
    """Serializer para respuesta de municipios del usuario"""
    
    tipo_usuario = serializers.CharField()  # 'administrador', 'profesional', 'sin_permisos'
    municipios = MunicipioPermitidoSerializer(many=True)
    total = serializers.IntegerField()
    mensaje = serializers.CharField(required=False)


class EstadisticasDirectorioSerializer(serializers.Serializer):
    """Serializer para estadísticas de directorios"""
    
    total_directorios = serializers.IntegerField()
    total_archivos = serializers.IntegerField()
    peso_total_mb = serializers.FloatField()
    directorio_mas_grande = serializers.CharField()
    ultimo_escaneo = serializers.DateTimeField()


class ResumenMunicipioSerializer(serializers.Serializer):
    """Serializer para resumen por municipio"""
    
    cod_municipio = serializers.IntegerField()
    total_directorios_opera = serializers.IntegerField()
    total_directorios_transv = serializers.IntegerField()
    total_archivos_opera = serializers.IntegerField()
    total_archivos_transv = serializers.IntegerField()
    peso_total_opera_mb = serializers.FloatField()
    peso_total_transv_mb = serializers.FloatField()


class JerarquiaDirectorioSerializer(serializers.Serializer):
    """Serializer para estructura jerárquica de directorios"""

    id = serializers.IntegerField()
    nombre = serializers.CharField()
    tipo = serializers.CharField()  # 'operacion' o 'transversal'
    nivel = serializers.IntegerField()
    total_archivos = serializers.IntegerField()
    peso_total_mb = serializers.FloatField()
    hijos = serializers.ListField(child=serializers.DictField(), read_only=True)


# ============================================================================
# SERIALIZERS PARA CALIFICACIÓN DE OPERACIÓN (02_oper)
# ============================================================================

from .models import CalificacionInfoOperacion, EvaluacionArchivosOperacion


class CalificacionInfoOperacionSerializer(serializers.ModelSerializer):
    """Serializer para calificaciones de información de operación"""

    nivel_calidad = serializers.SerializerMethodField()
    porcentaje = serializers.SerializerMethodField()

    class Meta:
        model = CalificacionInfoOperacion
        fields = ['id', 'concepto', 'valor', 'nivel_calidad', 'porcentaje']

    def get_nivel_calidad(self, obj):
        return obj.get_nivel_calidad()

    def get_porcentaje(self, obj):
        return obj.get_porcentaje()


class EvaluacionArchivosOperacionSerializer(serializers.ModelSerializer):
    """Serializer completo para evaluación de archivos de operación"""

    municipio_codigo = serializers.IntegerField(
        source='cod_dir_operacion.cod_municipio.cod_municipio',
        read_only=True
    )
    municipio_nombre = serializers.CharField(
        source='cod_dir_operacion.cod_municipio.nom_municipio',
        read_only=True
    )
    directorio_nombre = serializers.CharField(
        source='cod_dir_operacion.nombre_directorio',
        read_only=True
    )
    directorio_path = serializers.CharField(
        source='cod_dir_operacion.path_directorio',
        read_only=True
    )
    calificacion_concepto = serializers.SerializerMethodField()
    estado_display = serializers.CharField(
        source='get_estado_archivo_display',
        read_only=True
    )
    fecha_disposicion = serializers.DateTimeField(read_only=True)

    class Meta:
        model = EvaluacionArchivosOperacion
        fields = [
            'id_evaluacion', 'id_archivo', 'cod_dir_operacion',
            'municipio_codigo', 'municipio_nombre',
            'directorio_nombre', 'directorio_path',
            'nombre_archivo', 'ruta_completa', 'fecha_disposicion',
            'observacion_original', 'hash_contenido', 'usuario_windows',
            'peso_memoria', 'evaluacion_archivo', 'calificacion_concepto',
            'estado_archivo', 'estado_display', 'observaciones_evaluacion',
            'fecha_creacion', 'fecha_actualizacion', 'usuario_evaluacion',
            'evaluado', 'aprobado', 'evaluacion_archivo_anterior',
            'lote_calificacion_masiva', 'fecha_calificacion_masiva'
        ]
        read_only_fields = [
            'id_evaluacion', 'fecha_creacion', 'fecha_actualizacion',
            'municipio_codigo', 'municipio_nombre', 'directorio_nombre',
            'directorio_path', 'calificacion_concepto', 'estado_display'
        ]

    def get_calificacion_concepto(self, obj):
        if obj.evaluacion_archivo:
            try:
                cal = CalificacionInfoOperacion.objects.get(id=obj.evaluacion_archivo)
                return cal.concepto
            except CalificacionInfoOperacion.DoesNotExist:
                pass
        return None


class EvaluacionArchivosOperacionListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas de evaluaciones de operación"""

    directorio_nombre = serializers.CharField(
        source='cod_dir_operacion.nombre_directorio',
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_archivo_display',
        read_only=True
    )
    fecha_disposicion = serializers.DateTimeField(read_only=True)

    class Meta:
        model = EvaluacionArchivosOperacion
        fields = [
            'id_evaluacion', 'id_archivo', 'cod_dir_operacion',
            'directorio_nombre', 'nombre_archivo', 'ruta_completa',
            'fecha_disposicion', 'usuario_windows', 'peso_memoria',
            'evaluacion_archivo', 'estado_archivo', 'estado_display',
            'evaluado', 'aprobado', 'fecha_creacion'
        ]
