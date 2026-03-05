from django.db import models
from preoperacion.models import Municipios
from django.core.validators import MinValueValidator, MaxValueValidator

class ComponentesPost(models.Model):
    """
    ⚠️ MODELO DEPRECATED - Mantenido solo para compatibilidad
    Ya no se usa en la nueva arquitectura POST V2
    """
    id_componente = models.AutoField(primary_key=True)
    nombre_componente = models.CharField(max_length=300, unique=True)
    
    def __str__(self):
        return self.nombre_componente
    
    class Meta:
        db_table = 'componentes_post'
        verbose_name = 'Componente Post (DEPRECATED)'
        verbose_name_plural = 'Componentes Post (DEPRECATED)'
 

class DisposicionPost(models.Model):
    """
    🆕 MODELO ACTUALIZADO POST V2 - SIN dependencia de componentes_post
    Ahora representa DIRECTORIOS directamente, no componentes
    """
    id_disposicion = models.AutoField(primary_key=True)
    cod_municipio = models.ForeignKey(
        Municipios, 
        on_delete=models.CASCADE, 
        db_column='cod_municipio',
        related_name='disposicion_postoperacion'
    )
    # ❌ ELIMINADO: id_componente (ya no existe la relación)
    
    dispuesto = models.BooleanField(default=False)
    fecha_disposicion = models.DateField(null=True, blank=True)
    ruta_acceso = models.CharField(max_length=300, null=True, blank=True, unique=True)  # ✅ UNIQUE
    evaluado = models.BooleanField(default=False)
    aprobado = models.BooleanField(default=False)
    observaciones = models.CharField(max_length=500, null=True, blank=True)
    
    def __str__(self):
        # ✅ Nuevo string representation sin componentes
        directorio_nombre = self.ruta_acceso.split('\\')[-1] if self.ruta_acceso else 'Sin directorio'
        return f"Disposición {self.id_disposicion} - {self.cod_municipio.nom_municipio} - {directorio_nombre}"
    
    def get_nombre_directorio(self):
        """Extrae el nombre del directorio de la ruta_acceso"""
        if self.ruta_acceso:
            return self.ruta_acceso.split('\\')[-1] if '\\' in self.ruta_acceso else self.ruta_acceso
        return "Directorio sin nombre"
    
    def get_nivel_jerarquia(self):
        """Calcula el nivel de jerarquía basado en la ruta"""
        if self.ruta_acceso:
            return self.ruta_acceso.count('\\')
        return 0
    
    class Meta:
        db_table = 'disposicion_post'
        verbose_name = 'Disposición Post V2'
        verbose_name_plural = 'Disposiciones Post V2'
        # ❌ ELIMINADO: unique_together con id_componente
        # ✅ NUEVO: constraint único en ruta_acceso
        indexes = [
            models.Index(fields=['cod_municipio'], name='disp_post_municipio_idx'),
            models.Index(fields=['ruta_acceso'], name='disp_post_ruta_idx'),
            models.Index(fields=['fecha_disposicion'], name='disp_post_fecha_idx'),
        ]

class ArchivosPost(models.Model):
    """
    🔄 MODELO ACTUALIZADO - Relación directa con disposicion_post
    """
    id_archivo = models.AutoField(primary_key=True)
    id_disposicion = models.ForeignKey(
        'DisposicionPost', 
        models.DO_NOTHING, 
        db_column='id_disposicion',
        related_name='archivos_relacionados'  # ✅ Relación inversa más clara
    )
    nombre_archivo = models.CharField(max_length=255)
    ruta_completa = models.TextField(unique=True)  # ✅ UNIQUE constraint
    fecha_disposicion = models.DateField(blank=True, null=True)
    observacion = models.CharField(max_length=500, blank=True, null=True)
    hash_contenido = models.CharField(max_length=255, blank=True, null=True)
    usuario_windows = models.CharField(max_length=100, blank=True, null=True)
    peso_memoria = models.CharField(max_length=100, blank=True, null=True, help_text="Peso del archivo en memoria")
    
    def __str__(self):
        return f"{self.nombre_archivo} - {self.id_disposicion.get_nombre_directorio()}"
    
    def get_municipio(self):
        """Obtiene el municipio a través de la disposición"""
        return self.id_disposicion.cod_municipio if self.id_disposicion else None
    
    def get_directorio_contenedor(self):
        """Obtiene el directorio que contiene este archivo"""
        return self.id_disposicion.ruta_acceso if self.id_disposicion else None
    
    class Meta:
        db_table = 'archivos_post'
        verbose_name = 'Archivo Post V2'
        verbose_name_plural = 'Archivos Post V2'
        indexes = [
            models.Index(fields=['id_disposicion'], name='arch_post_disposicion_idx'),
            models.Index(fields=['nombre_archivo'], name='arch_post_nombre_idx'),
            models.Index(fields=['fecha_disposicion'], name='arch_post_fecha_idx'),
            models.Index(fields=['usuario_windows'], name='arch_post_usuario_idx'),
        ]

class PathDirPost(models.Model):
    id = models.AutoField(primary_key=True)
    cod_municipio = models.ForeignKey(
        Municipios, 
        on_delete=models.CASCADE, 
        db_column='cod_municipio',
        related_name='pathdirpost_postoperacion'
    )
    path = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Ruta Post {self.id} - {self.cod_municipio.nom_municipio}"
    
    class Meta:
        db_table = 'path_dir_post'
        verbose_name = 'Ruta de Directorio Post'
        verbose_name_plural = 'Rutas de Directorios Post'

class NotificacionesPost(models.Model):
    id = models.AutoField(primary_key=True)
    tipo_entidad = models.CharField(max_length=50)
    id_entidad = models.IntegerField()
    accion = models.CharField(max_length=20)
    descripcion = models.TextField(null=True, blank=True)
    datos_contexto = models.JSONField(null=True, blank=True)
    fecha_cambio = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Fecha y hora del cambio"
    )
    leido = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.tipo_entidad} {self.id_entidad}: {self.accion}"
    
    class Meta:
        db_table = 'notificaciones_post'
        verbose_name = 'Notificación Post'
        verbose_name_plural = 'Notificaciones Post'
        ordering = ['-fecha_cambio']
        
        indexes = [
            models.Index(fields=['fecha_cambio'], name='notif_post_fecha_idx'),
            models.Index(fields=['fecha_cambio', 'tipo_entidad'], name='notif_post_fecha_tipo_idx'),
            models.Index(fields=['fecha_cambio', 'leido'], name='notif_post_fecha_leido_idx'),
            models.Index(fields=['-fecha_cambio'], name='notif_post_fecha_desc_idx'),
            models.Index(fields=['tipo_entidad', 'leido', 'fecha_cambio'], name='noti_post_tipo_leido_fecha_idx'),
            models.Index(fields=['leido', '-fecha_cambio'], name='noti_post_leido_fecha_desc_idx'),
        ]

class HistorialPropietarios(models.Model):
    id = models.AutoField(primary_key=True)
    tipo_archivo = models.CharField(
        max_length=20, 
        choices=[('preoperacion', 'Pre-operación'), ('postoperacion', 'Post-operación')],
        help_text="Tipo de archivo: preoperación o postoperación"
    )
    id_archivo = models.IntegerField(help_text="ID del archivo según el tipo")
    id_notificacion = models.IntegerField(null=True, blank=True, help_text="Referencia a la notificación que registró el cambio")
    propietario_anterior = models.CharField(max_length=100, null=True, blank=True, help_text="Usuario que era propietario")
    propietario_nuevo = models.CharField(max_length=100, help_text="Usuario que se convirtió en propietario")
    fecha_inicio = models.DateTimeField(auto_now_add=True, help_text="Momento en que comenzó la propiedad del nuevo propietario")
    fecha_fin = models.DateTimeField(null=True, blank=True, help_text="NULL si es el propietario actual, timestamp cuando fue reemplazado")
    detalles = models.JSONField(null=True, blank=True, help_text="Información adicional como ruta, nombre archivo, etc.")
    
    def __str__(self):
        archivo_info = self.detalles.get('nombre_archivo', 'Sin nombre') if self.detalles else 'Sin detalles'
        return f"{self.tipo_archivo} - {archivo_info} - {self.propietario_nuevo}"
    
    class Meta:
        db_table = 'historial_propietarios'
        verbose_name = 'Historial de Propietario'
        verbose_name_plural = 'Historial de Propietarios'
        ordering = ['-fecha_inicio']
        
        indexes = [
            models.Index(fields=['tipo_archivo', 'id_archivo'], name='hist_tipo_id_idx'),
            models.Index(fields=['propietario_nuevo'], name='hist_prop_nuevo_idx'),
            models.Index(fields=['propietario_anterior'], name='hist_prop_ant_idx'),
            models.Index(fields=['fecha_inicio', 'fecha_fin'], name='hist_fechas_idx')
        ]

class CalificacionInfoPost(models.Model):
    """
    Modelo para la calificación de información post-operación.
    Define los conceptos y valores para evaluar la calidad de la información.
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
        db_table = 'calificacion_info_post'
        verbose_name = "Calificación de Información Post"
        verbose_name_plural = "Calificaciones de Información Post"
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
    
    def CalificacionInfoPost_get_archivos_evaluados_count(self):
        """Cuenta cuántos archivos han sido evaluados con esta calificación"""
        return self.archivos_evaluados.count()


class EvaluacionArchivosPost(models.Model):
    """
    🔄 MODELO ACTUALIZADO - Sin referencias a componentes
    """
    
    id_evaluacion = models.AutoField(
        primary_key=True,
        verbose_name="ID Evaluación",
        help_text="Identificador único de la evaluación"
    )
    
    id_archivo = models.IntegerField(
        verbose_name="ID Archivo Original",
        help_text="Referencia al archivo original en archivos_post",
        db_index=True
    )
    
    id_disposicion = models.ForeignKey(
        'DisposicionPost',
        on_delete=models.CASCADE,
        db_column='id_disposicion',
        verbose_name="Disposición",
        help_text="Disposición asociada al archivo",
        related_name='evaluaciones_archivos'
    )
    
    # 📄 INFORMACIÓN DEL ARCHIVO (COPIADA DEL ORIGINAL)
    nombre_archivo = models.CharField(
        max_length=255,
        verbose_name="Nombre del Archivo",
        help_text="Nombre del archivo evaluado"
    )
    
    ruta_completa = models.TextField(
        unique=True,
        verbose_name="Ruta Completa",
        help_text="Ruta completa del archivo en el sistema"
    )
    
    fecha_disposicion = models.DateField(
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
    help_text="ID de la calificación en calificacion_info_post"
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
        db_table = 'evaluacion_archivos_post'
        verbose_name = 'Evaluación de Archivo Post'
        verbose_name_plural = 'Evaluaciones de Archivos Post'
        ordering = ['-fecha_creacion', 'nombre_archivo']
        
        indexes = [
            models.Index(fields=['id_disposicion'], name='eval_arch_post_disp_idx'),
            models.Index(fields=['id_archivo'], name='eval_arch_post_arch_idx'),
            models.Index(fields=['estado_archivo'], name='eval_arch_post_estado_idx'),
            models.Index(fields=['evaluacion_archivo'], name='eval_arch_post_eval_idx'),
            models.Index(fields=['fecha_creacion'], name='eval_arch_post_fecha_idx'),
            models.Index(fields=['usuario_evaluacion'], name='eval_arch_post_usuario_idx'),
        ]
        
        permissions = [
            ("can_evaluate_files", "Puede evaluar archivos"),
            ("can_approve_files", "Puede aprobar archivos"),
            ("can_view_evaluations", "Puede ver evaluaciones"),
        ]
    
    def __str__(self):
        return f"Evaluación {self.id_evaluacion} - {self.nombre_archivo} ({self.get_estado_archivo_display()})"
    
    def get_archivo_original(self):
        """Obtiene el archivo original de archivos_post"""
        try:
            return ArchivosPost.objects.get(id_archivo=self.id_archivo)
        except ArchivosPost.DoesNotExist:
            return None
    
    def get_municipio(self):
        """🔄 ACTUALIZADO - Obtiene el municipio a través de la disposición (sin componente)"""
        if self.id_disposicion and self.id_disposicion.cod_municipio:
            return self.id_disposicion.cod_municipio
        return None
    
    def get_directorio_contenedor(self):
        """🆕 NUEVO - Obtiene el directorio contenedor desde la disposición"""
        if self.id_disposicion:
            return self.id_disposicion.ruta_acceso
        return None
    
    def get_porcentaje_evaluacion(self):
        """Obtiene el porcentaje de la evaluación"""
        if self.evaluacion_archivo:
            return self.evaluacion_archivo.get_porcentaje()
        return 0
    
    def get_nivel_calidad(self):
        """Obtiene el nivel de calidad de la evaluación"""
        if self.evaluacion_archivo:
            return self.evaluacion_archivo.get_nivel_calidad()
        return "Sin evaluación"
    
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
        if observaciones:
            self.observaciones_evaluacion = observaciones
        if usuario:
            self.usuario_evaluacion = usuario
        self.save()
    
    def rechazar(self, usuario=None, observaciones=None):
        """Método para rechazar el archivo"""
        self.estado_archivo = 'RECHAZADO'
        if observaciones:
            self.observaciones_evaluacion = observaciones
        if usuario:
            self.usuario_evaluacion = usuario
        self.save()
    
    def marcar_como_en_revision(self, usuario=None):
        """Marca el archivo como en revisión"""
        self.estado_archivo = 'EN_REVISION'
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
        """🔄 ACTUALIZADO - Obtiene evaluaciones agrupadas por municipio (sin componente)"""
        from django.db.models import Count

        queryset = cls.objects.select_related('id_disposicion__cod_municipio')

        if municipio_id:
            queryset = queryset.filter(id_disposicion__cod_municipio=municipio_id)

        return queryset.values(
            'id_disposicion__cod_municipio__cod_municipio',
            'id_disposicion__cod_municipio__nom_municipio'
        ).annotate(
            total_evaluaciones=Count('id_evaluacion'),
            pendientes=Count('id_evaluacion', filter=models.Q(estado_archivo='PENDIENTE')),
            aprobados=Count('id_evaluacion', filter=models.Q(estado_archivo='APROBADO'))
        ).order_by('id_disposicion__cod_municipio__nom_municipio')


class AuditoriaArchivos(models.Model):
    """
    Modelo para auditoría de operaciones sobre archivos.
    Registra todas las acciones realizadas sobre archivos desde la plataforma web.
    """

    ACCIONES = [
        ('UPLOAD', 'Archivo subido'),
        ('DOWNLOAD', 'Archivo descargado'),
        ('RENAME', 'Archivo renombrado'),
        ('DELETE', 'Archivo eliminado'),
        ('MOVE', 'Archivo movido'),
        ('COPY', 'Archivo copiado'),
        ('MODIFY', 'Archivo modificado'),
    ]

    PLATAFORMAS = [
        ('WEB', 'Plataforma Web'),
        ('WINDOWS', 'Windows/Red'),
        ('API', 'API Externa'),
        ('SCRIPT', 'Script Automático'),
    ]

    id = models.AutoField(primary_key=True)

    # Referencia al archivo (puede ser null si el archivo fue eliminado)
    id_archivo = models.ForeignKey(
        'ArchivosPost',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_archivo',
        related_name='auditoria_registros',
        verbose_name="Archivo",
        help_text="Referencia al archivo en archivos_post"
    )

    # Datos del archivo (guardados para mantener historial incluso si se elimina)
    nombre_archivo = models.CharField(
        max_length=255,
        verbose_name="Nombre del Archivo",
        help_text="Nombre del archivo al momento de la acción"
    )

    ruta_completa = models.TextField(
        verbose_name="Ruta Completa",
        help_text="Ruta completa del archivo"
    )

    # Acción realizada
    accion = models.CharField(
        max_length=20,
        choices=ACCIONES,
        verbose_name="Acción",
        help_text="Tipo de acción realizada",
        db_index=True
    )

    # Usuario que realizó la acción
    usuario = models.CharField(
        max_length=150,
        verbose_name="Usuario",
        help_text="Usuario que realizó la acción",
        db_index=True
    )

    usuario_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email del Usuario",
        help_text="Email del usuario que realizó la acción"
    )

    # Plataforma desde donde se realizó
    plataforma = models.CharField(
        max_length=20,
        choices=PLATAFORMAS,
        default='WEB',
        verbose_name="Plataforma",
        help_text="Plataforma desde donde se realizó la acción"
    )

    # Fecha y hora
    fecha_accion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Acción",
        help_text="Fecha y hora de la acción",
        db_index=True
    )

    # Detalles adicionales (JSON para flexibilidad)
    detalles = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Detalles",
        help_text="Información adicional de la acción (nombre anterior, tamaño, etc.)"
    )

    # IP del cliente (para seguridad)
    ip_cliente = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="IP del Cliente",
        help_text="Dirección IP desde donde se realizó la acción"
    )

    # Tamaño del archivo
    tamano_archivo = models.BigIntegerField(
        blank=True,
        null=True,
        verbose_name="Tamaño del Archivo",
        help_text="Tamaño del archivo en bytes"
    )

    class Meta:
        db_table = 'auditoria_archivos'
        verbose_name = 'Auditoría de Archivo'
        verbose_name_plural = 'Auditoría de Archivos'
        ordering = ['-fecha_accion']

        indexes = [
            models.Index(fields=['id_archivo'], name='audit_arch_archivo_idx'),
            models.Index(fields=['accion'], name='audit_arch_accion_idx'),
            models.Index(fields=['usuario'], name='audit_arch_usuario_idx'),
            models.Index(fields=['fecha_accion'], name='audit_arch_fecha_idx'),
            models.Index(fields=['ruta_completa'], name='audit_arch_ruta_idx'),
            models.Index(fields=['-fecha_accion', 'accion'], name='audit_arch_fecha_acc_idx'),
        ]

    def __str__(self):
        return f"{self.get_accion_display()} - {self.nombre_archivo} por {self.usuario} ({self.fecha_accion})"

    @classmethod
    def registrar_accion(cls, archivo=None, nombre_archivo=None, ruta_completa=None,
                         accion=None, usuario=None, usuario_email=None,
                         plataforma='WEB', detalles=None, ip_cliente=None,
                         tamano_archivo=None):
        """
        Método de conveniencia para registrar una acción de auditoría.
        """
        return cls.objects.create(
            id_archivo=archivo,
            nombre_archivo=nombre_archivo or (archivo.nombre_archivo if archivo else ''),
            ruta_completa=ruta_completa or (archivo.ruta_completa if archivo else ''),
            accion=accion,
            usuario=usuario,
            usuario_email=usuario_email,
            plataforma=plataforma,
            detalles=detalles,
            ip_cliente=ip_cliente,
            tamano_archivo=tamano_archivo
        )

    @classmethod
    def get_historial_archivo(cls, ruta_completa):
        """
        Obtiene el historial completo de un archivo por su ruta.
        """
        return cls.objects.filter(ruta_completa=ruta_completa).order_by('-fecha_accion')

    @classmethod
    def get_acciones_usuario(cls, usuario, dias=30):
        """
        Obtiene las acciones de un usuario en los últimos N días.
        """
        from django.utils import timezone
        from datetime import timedelta

        fecha_limite = timezone.now() - timedelta(days=dias)
        return cls.objects.filter(
            usuario=usuario,
            fecha_accion__gte=fecha_limite
        ).order_by('-fecha_accion')