from django.db import models
from django.utils import timezone
# Create your models here.
from django.contrib.auth.models import User
import uuid
try:
    from preoperacion.models import Municipios
except ImportError:
    # Fallback si no está disponible
    Municipios = None


class ScriptExecution(models.Model):
    SCRIPT_CHOICES = [
        ('backup_db', 'Copia de Seguridad de Base de Datos'),
        ('llenar_datos', 'Llenar Datos de Directorios'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('running', 'Ejecutando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    script_name = models.CharField(max_length=50, choices=SCRIPT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    output_file = models.CharField(max_length=255, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    output_log = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Ejecución de Script'
        verbose_name_plural = 'Ejecuciones de Scripts'
    
    def __str__(self):
        return f"{self.get_script_name_display()} - {self.get_status_display()}"

class BackupFile(models.Model):
    execution = models.ForeignKey(ScriptExecution, on_delete=models.CASCADE, related_name='backup_files')
    filename = models.CharField(max_length=255)
    filepath = models.CharField(max_length=500)
    file_size = models.BigIntegerField(default=0)  # en bytes
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.filename
    

class PathDirOpera(models.Model):
    """Almacena las rutas de directorios de operación (02_opera) para cada municipio"""
    cod_municipio = models.ForeignKey(
        Municipios,
        on_delete=models.CASCADE,
        db_column='cod_municipio',
        help_text="Código del municipio (FK a municipios)"
    )
    path = models.TextField(
        help_text="Ruta completa del directorio de operación"
    )
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha y hora de creación del registro"
    )

    class Meta:
        db_table = 'path_dir_opera'
        verbose_name = 'Ruta de Directorio Operativo'
        verbose_name_plural = 'Rutas de Directorios Operativos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Opera - Municipio {self.cod_municipio}: {self.path}"


class PathDirTransv(models.Model):
    """Rutas de directorios postoperativos para municipios"""
    
    cod_municipio = models.ForeignKey(
        'preoperacion.Municipios',
        on_delete=models.CASCADE,
        db_column='cod_municipio',
        help_text="Código del municipio (FK a municipios)"
    )
    path = models.TextField(
        help_text="Ruta completa del directorio de transversal"
    )
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha y hora de creación del registro"
    )

    class Meta:
        db_table = 'path_dir_transv'
        verbose_name = 'Ruta de Directorio Transversal'
        verbose_name_plural = 'Rutas de Directorios Transversal'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Opera - Municipio {self.cod_municipio}: {self.path}"


# 🔧 CORRECCIÓN CONFIRMADA POR ESQUEMA DE BD
# Basado en tables_schema.sql - Los nombres de columna son exactamente estos:

class DirectoriosOperacion(models.Model):
    """Tabla para almacenar información de directorios encontrados en las rutas de operación"""
    
    cod_dir_operacion = models.AutoField(primary_key=True)
    cod_municipio = models.ForeignKey(
        'preoperacion.Municipios',  # Referencia al modelo Municipios
        on_delete=models.CASCADE,
        db_column='cod_municipio',  # Especifica la columna en la BD
        help_text="Código del municipio (FK a municipios)"
    )
    path_directorio = models.CharField(
        max_length=600,
        help_text="Ruta completa del directorio (hasta 600 caracteres)"
    )
    nombre_directorio = models.CharField(max_length=255)
    
    # 🔧 CORREGIR: Agregar db_column para que coincida con la BD
    directorio_padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='directorio_padre',  # ← ESTO ES LO IMPORTANTE
        help_text="Referencia al directorio padre para crear jerarquía"
    )
    
    nivel_profundidad = models.IntegerField(
        default=0,
        null=True,
        help_text="Nivel de profundidad en la jerarquía (0=raíz)"
    )
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        null=True
    )
    fecha_ultima_modificacion = models.DateTimeField(
        null=True,
        blank=True
    )
    usuario_propietario = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    total_archivos = models.IntegerField(default=0, null=True)
    total_subdirectorios = models.IntegerField(default=0, null=True)
    peso_total_bytes = models.BigIntegerField(default=0, null=True)
    observaciones = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True, null=True)
    fecha_registro = models.DateTimeField(
        default=timezone.now,
        null=True
    )
    fecha_actualizacion = models.DateTimeField(
        default=timezone.now,
        null=True
    )

    class Meta:
        db_table = 'directorios_operacion'
        verbose_name = 'Directorio de Operación'
        verbose_name_plural = 'Directorios de Operación'
        ordering = ['cod_municipio', 'nivel_profundidad', 'nombre_directorio']

    def __str__(self):
        return f"{self.nombre_directorio} - Municipio {self.cod_municipio}"

    def save(self, *args, **kwargs):
        self.fecha_actualizacion = timezone.now()
        super().save(*args, **kwargs)


class DirectoriosTransv(models.Model):
    """Almacena información de directorios transversales (04_transv) para cada municipio"""
    
    cod_dir_transv = models.AutoField(primary_key=True)
    cod_municipio = models.ForeignKey(
        'preoperacion.Municipios', 
        on_delete=models.CASCADE,
        db_column='cod_municipio'
    )
    nombre_directorio = models.CharField(max_length=255)
    ruta_completa = models.CharField(max_length=600)
    ruta_relativa = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )
    nivel_jerarquia = models.IntegerField(default=0, null=True)
    
    # 🔧 CORREGIR: Agregar db_column
    directorio_padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='directorio_padre'  # ← ESTO ES LO IMPORTANTE
    )
    
    total_archivos = models.IntegerField(default=0, null=True)
    total_subdirectorios = models.IntegerField(default=0, null=True)
    peso_total_bytes = models.BigIntegerField(default=0, null=True)
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        null=True
    )
    fecha_actualizacion = models.DateTimeField(
        default=timezone.now,
        null=True
    )
    fecha_ultimo_escaneo = models.DateTimeField(
        null=True,
        blank=True
    )
    activo = models.BooleanField(default=True, null=True)
    observaciones = models.TextField(null=True, blank=True)
    metadatos = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'directorios_transv'
        verbose_name = 'Directorio Transversal'
        verbose_name_plural = 'Directorios Transversales'
        ordering = ['cod_municipio', 'nivel_jerarquia', 'nombre_directorio']

    def __str__(self):
        return f"{self.nombre_directorio} - Municipio {self.cod_municipio}"

    def save(self, *args, **kwargs):
        self.fecha_actualizacion = timezone.now()
        super().save(*args, **kwargs)


class ArchivosOperacion(models.Model):
    """Tabla para almacenar información de archivos encontrados en los directorios de operación"""
    
    id_archivo_operacion = models.AutoField(primary_key=True)
    
    # 🔧 CORREGIR: Agregar db_column
    cod_dir_operacion = models.ForeignKey(
        DirectoriosOperacion,
        on_delete=models.CASCADE,
        db_column='cod_dir_operacion',  # ← ESTO ES LO IMPORTANTE
        help_text="Referencia al directorio de operación"
    )
    
    path_file = models.CharField(
        max_length=600,
        help_text="Ruta completa del archivo (hasta 600 caracteres)"
    )
    nombre_archivo = models.CharField(max_length=255)
    extension = models.CharField(max_length=50, null=True, blank=True)
    fecha_disposicion = models.DateTimeField(null=True, blank=True)
    usuario_windows = models.CharField(max_length=100, null=True, blank=True)
    peso_memoria = models.BigIntegerField(
        default=0,
        null=True,
        help_text="Peso del archivo en bytes"
    )
    tipo_archivo = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Tipo: archivo normal o directorio especial (.gdb, .eslpk, etc.)"
    )
    hash_archivo = models.CharField(max_length=64, null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True, null=True)
    fecha_registro = models.DateTimeField(
        default=timezone.now,
        null=True
    )
    fecha_actualizacion = models.DateTimeField(
        default=timezone.now,
        null=True
    )

    class Meta:
        db_table = 'archivos_operacion'
        verbose_name = 'Archivo de Operación'
        verbose_name_plural = 'Archivos de Operación'
        ordering = ['-fecha_registro', 'nombre_archivo']

    def __str__(self):
        return f"{self.nombre_archivo} - Dir: {self.cod_dir_operacion.nombre_directorio}"

    def save(self, *args, **kwargs):
        self.fecha_actualizacion = timezone.now()
        super().save(*args, **kwargs)

    @property
    def peso_memoria_mb(self):
        """Convierte el peso de bytes a MB"""
        if self.peso_memoria:
            return round(self.peso_memoria / (1024 * 1024), 2)
        return 0


class ArchivosTransv(models.Model):
    """Archivos encontrados en directorios transversales"""
    
    id_archivo_transv = models.AutoField(primary_key=True)
    
    # 🔧 CORREGIR: Agregar db_column
    cod_dir_transv = models.ForeignKey(
        DirectoriosTransv,
        on_delete=models.CASCADE,
        db_column='cod_dir_transv',  # ← ESTO ES LO IMPORTANTE
        help_text="Referencia al directorio transversal"
    )
    
    nombre_archivo = models.CharField(max_length=255)
    path_file = models.CharField(max_length=600)
    extension = models.CharField(max_length=20, null=True, blank=True)
    fecha_disposicion = models.DateTimeField(null=True, blank=True)
    usuario_windows = models.CharField(max_length=100, null=True, blank=True)
    peso_memoria = models.BigIntegerField(default=0, null=True)
    observaciones = models.TextField(null=True, blank=True)
    es_directorio_especial = models.BooleanField(default=False, null=True)
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        null=True
    )
    fecha_actualizacion = models.DateTimeField(
        default=timezone.now,
        null=True
    )
    fecha_ultimo_escaneo = models.DateTimeField(
        default=timezone.now,
        null=True
    )
    activo = models.BooleanField(default=True, null=True)
    metadatos = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'archivos_transv'
        verbose_name = 'Archivo Transversal'
        verbose_name_plural = 'Archivos Transversales'
        ordering = ['-fecha_creacion', 'nombre_archivo']

    def __str__(self):
        return f"{self.nombre_archivo} - Dir: {self.cod_dir_transv.nombre_directorio}"

    def save(self, *args, **kwargs):
        self.fecha_actualizacion = timezone.now()
        super().save(*args, **kwargs)

    @property
    def peso_memoria_mb(self):
        """Convierte el peso de bytes a MB"""
        if self.peso_memoria:
            return round(self.peso_memoria / (1024 * 1024), 2)
        return 0


# ============================================================================
# MODELOS DE CALIFICACIÓN PARA OPERACIÓN (02_oper)
# Espejo de CalificacionInfoPost y EvaluacionArchivosPost para operaciones
# ============================================================================

from django.core.validators import MinValueValidator, MaxValueValidator


class CalificacionInfoOperacion(models.Model):
    """
    Modelo para la calificación de información de operación.
    Define los conceptos y valores para evaluar la calidad de la información.
    Espejo de CalificacionInfoPost pero independiente para operaciones.
    """

    concepto = models.CharField(
        max_length=255,
        verbose_name="Concepto",
        help_text="Descripción del concepto de calificación"
    )

    valor = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[
            MinValueValidator(0.0, message="El valor no puede ser menor a 0"),
            MaxValueValidator(1.0, message="El valor no puede ser mayor a 1")
        ],
        verbose_name="Valor",
        help_text="Valor numérico de la calificación (0.0 a 1.0)"
    )

    class Meta:
        db_table = 'calificacion_info_operacion'
        verbose_name = "Calificación de Información Operación"
        verbose_name_plural = "Calificaciones de Información Operación"
        ordering = ['valor', 'concepto']

    def __str__(self):
        return f"{self.concepto} - {self.valor}"

    def get_porcentaje(self):
        """Retorna el valor como porcentaje"""
        return float(self.valor) * 100

    def get_nivel_calidad(self):
        """Retorna el nivel de calidad basado en el valor"""
        if self.valor == 0:
            return "Sin información"
        elif self.valor <= 0.25:
            return "Muy bajo"
        elif self.valor <= 0.5:
            return "Bajo"
        elif self.valor <= 0.75:
            return "Medio"
        elif self.valor < 1:
            return "Alto"
        else:
            return "Completo"

    @classmethod
    def get_valor_completo(cls):
        """Retorna el valor para documento completo"""
        try:
            return cls.objects.get(concepto__icontains="DOCUMENTO COMPLETO").valor
        except cls.DoesNotExist:
            return 1.0

    @classmethod
    def get_concepto_por_valor(cls, valor):
        """Obtiene el concepto más cercano al valor dado"""
        return cls.objects.filter(valor__lte=valor).order_by('-valor').first()


class EvaluacionArchivosOperacion(models.Model):
    """
    Modelo para evaluación de archivos de operación.
    Espejo de EvaluacionArchivosPost pero para 02_oper.
    """

    id_evaluacion = models.AutoField(
        primary_key=True,
        verbose_name="ID Evaluación",
        help_text="Identificador único de la evaluación"
    )

    id_archivo = models.IntegerField(
        verbose_name="ID Archivo Original",
        help_text="Referencia al archivo original en archivos_operacion",
        db_index=True
    )

    cod_dir_operacion = models.ForeignKey(
        'DirectoriosOperacion',
        on_delete=models.CASCADE,
        db_column='cod_dir_operacion',
        verbose_name="Directorio",
        help_text="Directorio de operación asociado al archivo",
        related_name='evaluaciones_archivos'
    )

    # 📄 INFORMACIÓN DEL ARCHIVO (COPIADA DEL ORIGINAL)
    nombre_archivo = models.CharField(
        max_length=255,
        verbose_name="Nombre del Archivo",
        help_text="Nombre del archivo evaluado"
    )

    ruta_completa = models.TextField(
        verbose_name="Ruta Completa",
        help_text="Ruta completa del archivo en el sistema"
    )

    fecha_disposicion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Fecha de Disposición",
        help_text="Fecha cuando se dispuso el archivo"
    )

    observacion_original = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Observación Original",
        help_text="Observación original del archivo"
    )

    hash_contenido = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Hash del Contenido",
        help_text="Hash para verificar integridad del archivo"
    )

    usuario_windows = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Usuario Windows",
        help_text="Usuario Windows que creó el archivo"
    )

    peso_memoria = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Peso en Memoria",
        help_text="Peso del archivo en memoria"
    )

    # 🆕 CAMPOS ESPECÍFICOS DE EVALUACIÓN
    evaluacion_archivo = models.IntegerField(
        null=True,
        blank=True,
        default=1,
        verbose_name="Evaluación del Archivo",
        help_text="ID de la calificación en calificacion_info_operacion"
    )

    ESTADOS_ARCHIVO = [
        ('PENDIENTE', 'Pendiente de Evaluación'),
        ('EN_REVISION', 'En Revisión'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
        ('REQUIERE_AJUSTES', 'Requiere Ajustes'),
    ]

    estado_archivo = models.CharField(
        max_length=50,
        choices=ESTADOS_ARCHIVO,
        default='PENDIENTE',
        verbose_name="Estado del Archivo",
        help_text="Estado actual de la evaluación del archivo",
        db_index=True
    )

    observaciones_evaluacion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones de Evaluación",
        help_text="Observaciones específicas de la evaluación realizada"
    )

    # 📅 CAMPOS DE AUDITORÍA
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación",
        help_text="Fecha cuando se creó el registro de evaluación",
        db_index=True
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización",
        help_text="Fecha de la última actualización"
    )

    usuario_evaluacion = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Usuario Evaluador",
        help_text="Usuario que realizó o actualizó la evaluación"
    )

    evaluado = models.BooleanField(default=False)
    aprobado = models.BooleanField(default=False)

    # 🆕 CAMPOS PARA CALIFICACIÓN MASIVA
    evaluacion_archivo_anterior = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Evaluación Anterior",
        help_text="ID de la calificación anterior (para restaurar)"
    )

    lote_calificacion_masiva = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Lote Calificación Masiva",
        help_text="Identificador del lote de calificación masiva (UUID)"
    )

    fecha_calificacion_masiva = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha Calificación Masiva",
        help_text="Fecha de la última calificación masiva"
    )

    class Meta:
        db_table = 'evaluacion_archivos_operacion'
        verbose_name = 'Evaluación de Archivo Operación'
        verbose_name_plural = 'Evaluaciones de Archivos Operación'
        ordering = ['-fecha_creacion', 'nombre_archivo']

        indexes = [
            models.Index(fields=['cod_dir_operacion'], name='eval_arch_oper_dir_idx'),
            models.Index(fields=['id_archivo'], name='eval_arch_oper_arch_idx'),
            models.Index(fields=['estado_archivo'], name='eval_arch_oper_estado_idx'),
            models.Index(fields=['evaluacion_archivo'], name='eval_arch_oper_eval_idx'),
            models.Index(fields=['fecha_creacion'], name='eval_arch_oper_fecha_idx'),
            models.Index(fields=['usuario_evaluacion'], name='eval_arch_oper_usuario_idx'),
        ]

        permissions = [
            ("can_evaluate_files_oper", "Puede evaluar archivos de operación"),
            ("can_approve_files_oper", "Puede aprobar archivos de operación"),
            ("can_view_evaluations_oper", "Puede ver evaluaciones de operación"),
        ]

    def __str__(self):
        return f"Evaluación {self.id_evaluacion} - {self.nombre_archivo} ({self.get_estado_archivo_display()})"

    def get_archivo_original(self):
        """Obtiene el archivo original de archivos_operacion"""
        try:
            return ArchivosOperacion.objects.get(id_archivo_operacion=self.id_archivo)
        except ArchivosOperacion.DoesNotExist:
            return None

    def get_municipio(self):
        """Obtiene el municipio a través del directorio"""
        if self.cod_dir_operacion and self.cod_dir_operacion.cod_municipio:
            return self.cod_dir_operacion.cod_municipio
        return None

    def get_directorio_contenedor(self):
        """Obtiene el directorio contenedor"""
        if self.cod_dir_operacion:
            return self.cod_dir_operacion.path_directorio
        return None

    def is_pendiente(self):
        """Verifica si el archivo está pendiente de evaluación"""
        return self.estado_archivo == 'PENDIENTE'

    def is_aprobado(self):
        """Verifica si el archivo está aprobado"""
        return self.estado_archivo == 'APROBADO'

    def puede_ser_evaluado(self):
        """Verifica si el archivo puede ser evaluado"""
        return self.estado_archivo in ['PENDIENTE', 'EN_REVISION', 'REQUIERE_AJUSTES']

    def aprobar(self, usuario=None, observaciones=None):
        """Método para aprobar el archivo"""
        self.estado_archivo = 'APROBADO'
        self.aprobado = True
        self.evaluado = True
        if observaciones:
            self.observaciones_evaluacion = observaciones
        if usuario:
            self.usuario_evaluacion = usuario
        self.save()

    def rechazar(self, usuario=None, observaciones=None):
        """Método para rechazar el archivo"""
        self.estado_archivo = 'RECHAZADO'
        self.aprobado = False
        self.evaluado = True
        if observaciones:
            self.observaciones_evaluacion = observaciones
        if usuario:
            self.usuario_evaluacion = usuario
        self.save()

    @classmethod
    def get_estadisticas_evaluacion(cls):
        """Obtiene estadísticas de evaluación"""
        from django.db.models import Count

        return cls.objects.aggregate(
            total=Count('id_evaluacion'),
            pendientes=Count('id_evaluacion', filter=models.Q(estado_archivo='PENDIENTE')),
            en_revision=Count('id_evaluacion', filter=models.Q(estado_archivo='EN_REVISION')),
            aprobados=Count('id_evaluacion', filter=models.Q(estado_archivo='APROBADO')),
            rechazados=Count('id_evaluacion', filter=models.Q(estado_archivo='RECHAZADO')),
            requiere_ajustes=Count('id_evaluacion', filter=models.Q(estado_archivo='REQUIERE_AJUSTES'))
        )

    @classmethod
    def get_evaluaciones_por_municipio(cls, municipio_id=None):
        """Obtiene evaluaciones agrupadas por municipio"""
        from django.db.models import Count

        queryset = cls.objects.select_related('cod_dir_operacion__cod_municipio')

        if municipio_id:
            queryset = queryset.filter(cod_dir_operacion__cod_municipio=municipio_id)

        return queryset.values(
            'cod_dir_operacion__cod_municipio__cod_municipio',
            'cod_dir_operacion__cod_municipio__nom_municipio'
        ).annotate(
            total_evaluaciones=Count('id_evaluacion'),
            pendientes=Count('id_evaluacion', filter=models.Q(estado_archivo='PENDIENTE')),
            aprobados=Count('id_evaluacion', filter=models.Q(estado_archivo='APROBADO'))
        ).order_by('cod_dir_operacion__cod_municipio__nom_municipio')