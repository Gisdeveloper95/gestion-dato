from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import secrets


# Tablas de dominio para zonas
class Zonas(models.Model):
    zona = models.CharField(primary_key=True, max_length=100)

    def __str__(self):
        return self.zona

    class Meta:
        managed = False
        db_table = 'zonas'
        db_table_comment = 'Catálogo de zonas disponibles'

# Tablas de dominio para municipios
class MecanismoGeneral(models.Model):
    cod_mecanismo = models.CharField(primary_key=True, max_length=100)
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.cod_mecanismo

    class Meta:
        managed = False
        db_table = 'mecanismo_general'
        db_table_comment = 'Mecanismos generales 2025 disponibles'

class MecanismoDetalle(models.Model):
    cod_mecanismo_detalle = models.CharField(primary_key=True, max_length=100)
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.cod_mecanismo_detalle

    class Meta:
        managed = False
        db_table = 'mecanismo_detalle'
        db_table_comment = 'Detalles de los mecanismos de operación'



class AlcanceOperacion(models.Model):
    cod_alcance = models.CharField(primary_key=True, max_length=100)

    def __str__(self):
        return self.cod_alcance

    class Meta:
        managed = False
        db_table = 'alcance_operacion'
        db_table_comment = 'Alcances de operación 2025 disponibles'

class Grupo(models.Model):
    cod_grupo = models.CharField(primary_key=True, max_length=50)
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.descripcion or self.cod_grupo

    class Meta:
        managed = False
        db_table = 'grupo'
        db_table_comment = 'Grupos para clasificación de municipios'

class MecanismoOperacion(models.Model):
    cod_operacion = models.CharField(primary_key=True, max_length=100)
    descripcion = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.cod_operacion

    class Meta:
        db_table = 'mecanismo_operacion'
        managed = False
        db_table_comment = 'Dominio para operaciones directas en municipios'

# Departamentos
class Departamentos(models.Model):
    cod_depto = models.IntegerField(primary_key=True)
    nom_depto = models.CharField(max_length=100)

    def __str__(self):
        return self.nom_depto

    class Meta:
        managed = False
        db_table = 'departamentos'
        db_table_comment = 'Catálogo de departamentos'

# Municipios

class Municipios(models.Model):
    cod_municipio = models.IntegerField(primary_key=True)
    nom_municipio = models.CharField(max_length=100)
    cod_depto = models.ForeignKey(Departamentos, on_delete=models.CASCADE, db_column='cod_depto')
    fecha_inicio = models.DateField(null=True, blank=True)
    
    # Nuevos campos para nom_territorial
    nom_territorial = models.CharField(max_length=100, null=True, blank=True)
    area = models.CharField(max_length=100, null=True, blank=True)
    # Campos de dominio como CharFields para referenciar a las tablas de dominio
    mecanismo_general = models.CharField(max_length=100, null=True, blank=True)
    mecanismo_detalle = models.CharField(max_length=100, null=True, blank=True)
    alcance_operacion = models.CharField(max_length=100, null=True, blank=True)
    grupo = models.CharField(max_length=50, null=True, blank=True)
    mecanismo_operacion = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return self.nom_municipio

    class Meta:
        managed = False
        db_table = 'municipios'
        db_table_comment = 'Catálogo de municipios con su departamento correspondiente e información de operación'
# Usuarios
class Usuarios(models.Model):
    cod_usuario = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    correo = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.nombre

    class Meta:
        managed = False
        db_table = 'usuarios'
        db_table_comment = 'Información de usuarios del sistema'

# Tipos de Insumos
class TiposInsumos(models.Model):
    tipo_insumo = models.CharField(primary_key=True, max_length=100)

    def __str__(self):
        return self.tipo_insumo

    class Meta:
        managed = False
        db_table = 'tipos_insumos'
        db_table_comment = 'Dominio de tipos de insumos: primarios y secundarios'

# Categorias
class Categorias(models.Model):
    cod_categoria = models.IntegerField(primary_key=True)
    nom_categoria = models.CharField(max_length=100)

    def __str__(self):
        return self.nom_categoria

    class Meta:
        managed = False
        db_table = 'categorias'
        db_table_comment = 'Catálogo de categorías para insumos'

# Tipos de Formato
class TiposFormato(models.Model):
    cod_formato_tipo = models.CharField(primary_key=True, max_length=20)

    def __str__(self):
        return self.cod_formato_tipo

    class Meta:
        managed = False
        db_table = 'tipos_formato'
        db_table_comment = 'Catálogo de tipos de formato/extensiones de archivos'

# Entidades
class Entidades(models.Model):
    cod_entidad = models.CharField(primary_key=True, max_length=20)
    nom_entidad = models.CharField(max_length=200)

    def __str__(self):
        return self.nom_entidad

    class Meta:
        managed = False
        db_table = 'entidades'
        db_table_comment = 'Catálogo de entidades con códigos en formato de siglas'



# Detalle de Insumo - Sin referencia a concepto
class DetalleInsumo(models.Model):
    cod_detalle = models.IntegerField(primary_key=True)
    escala = models.CharField(max_length=50, null=True, blank=True)
    estado = models.CharField(max_length=50, null=True, blank=True)
    cubrimiento = models.CharField(max_length=100, null=True, blank=True)
    fecha_entrega = models.DateField(null=True, blank=True)
    fecha_disposicion = models.DateField(null=True, blank=True)
    area = models.CharField(max_length=100, null=True, blank=True)
    cod_entidad = models.ForeignKey('Entidades', models.DO_NOTHING, db_column='cod_entidad')
    observacion = models.TextField(null=True, blank=True)
    vigencia = models.CharField(max_length=50, null=True, blank=True)
    formato_tipo = models.ForeignKey('TiposFormato', models.DO_NOTHING, db_column='formato_tipo')
    cod_usuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='cod_usuario')
    cod_clasificacion = models.ForeignKey('ClasificacionInsumo', models.DO_NOTHING, db_column='cod_clasificacion')
    zona = models.ForeignKey('Zonas', models.DO_NOTHING, db_column='zona', null=True, blank=True)
    ruta_archivo = models.TextField(max_length=500, null=True, blank=True)
    porcentaje_cubrimiento = models.TextField(max_length=3, null=True, blank=True)
    
    # 🆕 NUEVA COLUMNA - FOREIGN KEY OPCIONAL
    cod_centro_poblado = models.ForeignKey(
        'CentrosPoblados', 
        models.DO_NOTHING, 
        db_column='cod_centro_poblado',
        null=True,      # ✅ Permite NULL en la base de datos
        blank=True,     # ✅ Permite vacío en formularios Django
        related_name='detalles_insumo'  # Nombre para la relación inversa
    )

    cod_sub_clasificacion = models.ForeignKey(
        'SubClasificacionFuenteSecundaria',
        models.DO_NOTHING,
        db_column='cod_sub_clasificacion',
        null=True,
        blank=True,
        related_name='detalles_sub_clasificacion'
    )

    def __str__(self):
        return f"Detalle {self.cod_detalle}"

    class Meta:
        managed = False
        db_table = 'detalle_insumo'
        db_table_comment = 'Detalles específicos de los insumos, ahora incluyendo información de usuario, clasificación, zona y centro poblado'

# Concepto - Con referencia a detalle_insumo
class Concepto(models.Model):
    cod_concepto = models.IntegerField(primary_key=True)
    concepto = models.CharField(max_length=200)
    fecha = models.DateField(null=True, blank=True)
    evaluacion = models.CharField(max_length=100, null=True, blank=True)
    detalle_concepto = models.CharField(max_length=10000, null=True, blank=True)
    observacion = models.TextField(null=True, blank=True)
    pdf = models.CharField(max_length=500, null=True, blank=True)
    cod_detalle = models.ForeignKey('DetalleInsumo', models.DO_NOTHING, db_column='cod_detalle', null=True, related_name='conceptos')

    def __str__(self):
        return self.concepto

    class Meta:
        managed = False
        db_table = 'concepto'
        db_table_comment = 'Conceptos asociados a los insumos'

# Insumos - ACTUALIZADO: Eliminado el campo cod_usuario, mantenido cod_categoria
class Insumos(models.Model):
    cod_insumo = models.IntegerField(primary_key=True)
    cod_municipio = models.ForeignKey(Municipios, models.DO_NOTHING, db_column='cod_municipio')
    cod_categoria = models.ForeignKey(Categorias, models.DO_NOTHING, db_column='cod_categoria')
    tipo_insumo = models.ForeignKey(TiposInsumos, models.DO_NOTHING, db_column='tipo_insumo')

    def __str__(self):
        return f"Insumo {self.cod_insumo}"

    class Meta:
        managed = False
        db_table = 'insumos'
        db_table_comment = 'Registro principal de insumos, con información de categoría pero sin usuario'

# Clasificación de Insumo - ACTUALIZADO: Eliminados los campos tipo_insumo, cod_detalle y zona
class ClasificacionInsumo(models.Model):
    cod_clasificacion = models.IntegerField(primary_key=True)
    cod_insumo = models.ForeignKey(Insumos, models.DO_NOTHING, db_column='cod_insumo')
    nombre = models.CharField(max_length=200)
    observacion = models.TextField(blank=True, null=True)
    ruta = models.CharField(max_length=500, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        managed = False
        db_table = 'clasificacion_insumo'
        db_table_comment = 'Clasificación y características adicionales de los insumos'

class SubClasificacionFuenteSecundaria(models.Model):
    cod_sub_clasificacion = models.AutoField(primary_key=True)
    dominio = models.CharField(max_length=50)
    nombre = models.CharField(max_length=200)
    orden = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.dominio} - {self.nombre}"

    class Meta:
        managed = False
        db_table = 'sub_clasificacion_fuente_secundaria'
        ordering = ['dominio', 'orden']

class EstadosInsumo(models.Model):
    estado = models.CharField(primary_key=True, max_length=100)
    
    def __str__(self):
        return self.estado

    class Meta:
        managed = False
        db_table = 'estados_insumo'
        verbose_name = 'Estado de Insumo'
        verbose_name_plural = 'Estados de Insumos'
        db_table_comment = 'Catálogo de estados posibles para insumos'


        
# Notificaciones
class Notificaciones(models.Model):
    id = models.AutoField(primary_key=True)
    tipo_entidad = models.CharField(max_length=50)
    id_entidad = models.IntegerField()
    accion = models.CharField(max_length=20)
    descripcion = models.TextField(blank=True, null=True)
    datos_contexto = models.JSONField(blank=True, null=True)
    fecha_cambio = models.DateTimeField(
        auto_now_add=True,
        db_index=True,  # IMPORTANTE: Índice para rendimiento
        help_text="Fecha y hora del cambio"
    )
    leido = models.BooleanField(blank=True, null=True)

    class Meta:
        db_table = 'notificaciones'
        ordering = ['-fecha_cambio']  # Ordenamiento por defecto
        indexes = [
            # IMPORTANTE: Índices adicionales para optimización
            models.Index(fields=['fecha_cambio']),
            models.Index(fields=['fecha_cambio', 'tipo_entidad']),
            models.Index(fields=['fecha_cambio', 'leido']),
            models.Index(fields=['-fecha_cambio']),  # Para ordenamiento descendente
            
            # Índices compuestos para consultas comunes
            models.Index(fields=['tipo_entidad', 'leido', 'fecha_cambio']),
            models.Index(fields=['leido', '-fecha_cambio']),
        ]
        
    def __str__(self):
        return f"{self.tipo_entidad} - {self.accion} - {self.fecha_cambio}"

# Señal para crear usuario personalizado cuando se crea un User de Django
@receiver(post_save, sender=User)
def crear_usuario_personalizado(sender, instance, created, **kwargs):
    """Crea un usuario en la tabla Usuarios cuando se crea un User de Django"""
    if created and instance.email:
        # Buscar el último código de usuario para crear uno nuevo
        ultimo_usuario = Usuarios.objects.all().order_by('-cod_usuario').first()
        nuevo_codigo = 1 if not ultimo_usuario else ultimo_usuario.cod_usuario + 1
        
        # Crear el usuario personalizado
        Usuarios.objects.create(
            cod_usuario=nuevo_codigo,
            nombre=f"{instance.first_name} {instance.last_name}".strip(),
            correo=instance.email
        )

# Señal para sincronizar usuario personalizado cuando se actualiza un User de Django
@receiver(post_save, sender=User)
def sincronizar_usuario_personalizado(sender, instance, created, **kwargs):
    if instance.email and not created:
        try:
            # Buscar si existe un usuario con el mismo correo
            usuario_custom = Usuarios.objects.get(correo=instance.email)
            # Actualizar el nombre si el usuario ya existe
            usuario_custom.nombre = f"{instance.first_name} {instance.last_name}".strip()
            usuario_custom.save()
        except Usuarios.DoesNotExist:
            # Crear nuevo usuario si no existe
            ultimo_usuario = Usuarios.objects.all().order_by('-cod_usuario').first()
            nuevo_codigo = 1 if not ultimo_usuario else ultimo_usuario.cod_usuario + 1
            
            Usuarios.objects.create(
                cod_usuario=nuevo_codigo,
                nombre=f"{instance.first_name} {instance.last_name}".strip(),
                correo=instance.email
            )

# Agregar estos modelos al final del archivo models.py

class PathDirPre(models.Model):
    """Modelo para almacenar rutas de directorios preoperativos"""
    id = models.AutoField(primary_key=True)
    cod_municipio = models.ForeignKey('Municipios', on_delete=models.CASCADE, db_column='cod_municipio')
    path = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'path_dir_pre'
        verbose_name = 'Ruta Preoperativa'
        verbose_name_plural = 'Rutas Preoperativas'

    def __str__(self):
        return f"Ruta Pre: {self.cod_municipio.nom_municipio} - {self.path[:30]}..."


class PathDirPost(models.Model):
    """Modelo para almacenar rutas de directorios postoperativos"""
    id = models.AutoField(primary_key=True)
    cod_municipio = models.ForeignKey(
        'Municipios',  # O el nombre exacto de tu modelo
        on_delete=models.CASCADE, 
        db_column='cod_municipio',
        related_name='pathdirpost_preoperacion'  # Añade esto
    )
    path = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'path_dir_post'
        verbose_name = 'Ruta Postoperativa'
        verbose_name_plural = 'Rutas Postoperativas'

    def __str__(self):
        return f"Ruta Post: {self.cod_municipio.nom_municipio} - {self.path[:30]}..."

class ListaArchivosPre(models.Model):
    id_lista_archivo = models.AutoField(primary_key=True)
    cod_insumo = models.ForeignKey(ClasificacionInsumo, on_delete=models.CASCADE, db_column='cod_insumo')
    nombre_insumo = models.CharField(max_length=500, blank=True, null=True)
    fecha_disposicion = models.DateField(blank=True, null=True)
    observacion = models.CharField(max_length=1000, blank=True, null=True)
    path_file = models.CharField(max_length=500, blank=True, null=True)
    hash_contenido = models.CharField(max_length=255, blank=True, null=True)
    usuario_windows = models.CharField(max_length=100, blank=True, null=True)
    peso_memoria = models.CharField(max_length=100, blank=True, null=True, help_text="Peso del archivo en memoria")

    class Meta:
        managed = False
        db_table = 'lista_archivos_preo'
        db_table_comment = 'Tabla que almacena la lista de archivos preoperativos relacionados con clasificaciones de insumos'




# Tabla de roles de seguimiento
class RolesSeguimiento(models.Model):
    rol_profesional = models.CharField(primary_key=True, max_length=100)

    def __str__(self):
        return self.rol_profesional

    class Meta:
        managed = False
        db_table = 'roles_seguimiento'
        verbose_name = 'Rol de Seguimiento'
        verbose_name_plural = 'Roles de Seguimiento'

# Tabla de territoriales IGAC
class TerritorialesIgac(models.Model):
    nom_territorial = models.CharField(primary_key=True, max_length=100)

    def __str__(self):
        return self.nom_territorial

    class Meta:
        managed = False
        db_table = 'territoriales_igac'
        verbose_name = 'Territorial IGAC'
        verbose_name_plural = 'Territoriales IGAC'

# Tabla de profesionales de seguimiento
# En preoperacion/models.py - AGREGAR este campo a ProfesionalesSeguimiento
class ProfesionalesSeguimiento(models.Model):
    cod_profesional = models.CharField(primary_key=True, max_length=100)
    nombre_profesional = models.CharField(max_length=100)
    correo_profesional = models.CharField(max_length=100, blank=True, null=True)
    rol_profesional = models.ForeignKey(RolesSeguimiento, models.DO_NOTHING, db_column='rol_profesional')
    
    # AGREGAR ESTA LÍNEA:
    usuario_django = models.OneToOneField(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        db_column='usuario_django_id',
        related_name='profesional_seguimiento'
    )

    def __str__(self):
        return self.nombre_profesional

    class Meta:
        managed = False
        db_table = 'profesionales_seguimiento'  
        verbose_name = 'Profesional de Seguimiento'
        verbose_name_plural = 'Profesionales de Seguimiento'

# Tabla de relación entre profesionales y territoriales
class ProfesionalTerritorial(models.Model):
    id = models.AutoField(primary_key=True)
    cod_profesional = models.ForeignKey(
        ProfesionalesSeguimiento, 
        models.CASCADE,  # CAMBIO: De DO_NOTHING a CASCADE
        db_column='cod_profesional'
    )
    territorial_seguimiento = models.ForeignKey(
        TerritorialesIgac, 
        models.DO_NOTHING, 
        db_column='territorial_seguimiento'
    )

    class Meta:
        managed = False
        db_table = 'profesional_territorial'
        verbose_name = 'Asignación Profesional-Territorial'
        verbose_name_plural = 'Asignaciones Profesionales-Territoriales'

# Tabla de relación entre profesionales y municipios

class ProfesionalMunicipio(models.Model):
    id = models.AutoField(primary_key=True)
    cod_profesional = models.ForeignKey(
        ProfesionalesSeguimiento, 
        models.CASCADE,  # CAMBIO: De DO_NOTHING a CASCADE
        db_column='cod_profesional'
    )
    cod_municipio = models.ForeignKey(
        Municipios, 
        models.DO_NOTHING, 
        db_column='cod_municipio'
    )
    
    class Meta:
        managed = False
        db_table = 'profesional_municipio'
        verbose_name = 'Asignación Profesional-Municipio'
        verbose_name_plural = 'Asignaciones Profesionales-Municipios'


class Auditoria(models.Model):
    """Registro de auditoría de acciones en el sistema"""
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuarios, on_delete=models.SET_NULL, null=True, db_column='cod_usuario')
    fecha_hora = models.DateTimeField(auto_now_add=True)
    tipo_entidad = models.CharField(max_length=50)  # 'detalle', 'concepto', 'insumo', etc.
    id_entidad = models.IntegerField()  # ID de la entidad afectada
    accion = models.CharField(max_length=20)  # 'crear', 'actualizar', 'eliminar', 'consultar'
    detalles = models.JSONField(blank=True, null=True)  # Para almacenar detalles adicionales
    ip_origen = models.CharField(max_length=50, blank=True, null=True)  # IP desde donde se realizó la acción
    
    class Meta:
        db_table = 'auditoria'
        managed = False  # Se creará manualmente en la BD
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-fecha_hora']
        
    def __str__(self):
        return f"{self.usuario} - {self.accion} {self.tipo_entidad} #{self.id_entidad} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
    


class InfoAdministrativa(models.Model):
    """Información administrativa catastral por municipio"""
    cod_info_admin = models.AutoField(primary_key=True)
    cod_municipio = models.ForeignKey(
        Municipios, 
        on_delete=models.CASCADE, 
        db_column='cod_municipio'
    )
    id_gestor_catas = models.CharField(max_length=200, blank=True, null=True)
    gestor_prestador_servicio = models.CharField(max_length=200, blank=True, null=True)
    publicacion_year = models.CharField(max_length=50, blank=True, null=True)
    vigencia_rural = models.CharField(max_length=100, blank=True, null=True)
    vigencia_urbana = models.CharField(max_length=100, blank=True, null=True)
    estado_rural = models.CharField(max_length=100, blank=True, null=True)
    estado_urbano = models.CharField(max_length=100, blank=True, null=True)
    predios_rurales = models.CharField(max_length=100, blank=True, null=True)
    area_terreno_rural_m2 = models.CharField(max_length=100, blank=True, null=True)
    area_terreno_rural_ha = models.CharField(max_length=100, blank=True, null=True)
    area_construida_rural_m2 = models.CharField(max_length=100, blank=True, null=True)
    avaluo_rural = models.CharField(max_length=100, blank=True, null=True)
    predios_urbanos = models.CharField(max_length=100, blank=True, null=True)
    area_terreno_urbana_m2 = models.CharField(max_length=100, blank=True, null=True)
    area_terreno_urbana_ha = models.CharField(max_length=100, blank=True, null=True)
    area_construida_urbana_m2 = models.CharField(max_length=100, blank=True, null=True)
    avaluo_urbano_1 = models.CharField(max_length=100, blank=True, null=True)
    avaluo_urbano_2 = models.CharField(max_length=100, blank=True, null=True)
    total_predios = models.CharField(max_length=100, blank=True, null=True)
    total_area_terreno_m2 = models.CharField(max_length=100, blank=True, null=True)
    total_area_terreno_ha = models.CharField(max_length=100, blank=True, null=True)
    total_area_construida_m2 = models.CharField(max_length=100, blank=True, null=True)
    total_avaluos = models.CharField(max_length=100, blank=True, null=True)
    area_geografica_rural_ha = models.CharField(max_length=100, blank=True, null=True)
    area_geografica_urbana_ha = models.CharField(max_length=100, blank=True, null=True)
    area_rural_estados_catastrales_ha = models.CharField(max_length=100, blank=True, null=True)
    area_urbana_estados_catastrales_ha = models.CharField(max_length=100, blank=True, null=True)
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Info Admin {self.cod_info_admin} - {self.cod_municipio.nom_municipio}"

    class Meta:
        managed = True
        db_table = 'info_administrativa'
        verbose_name = 'Información Administrativa'
        verbose_name_plural = 'Información Administrativa'
        db_table_comment = 'Información administrativa catastral por municipio'


class CentrosPoblados(models.Model):
    """Centros poblados por municipio"""
    cod_centro_poblado = models.CharField(primary_key=True, max_length=50)
    cod_municipio = models.ForeignKey(
        Municipios,
        on_delete=models.CASCADE,
        db_column='cod_municipio'
    )
    nom_centro_poblado = models.CharField(max_length=200, blank=True, null=True)
    area_oficial_ha = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nom_centro_poblado} - {self.cod_municipio.nom_municipio}"

    class Meta:
        managed = True # 🔧 CAMBIAR ESTO
        db_table = 'centros_poblados'
        verbose_name = 'Centro Poblado'
        verbose_name_plural = 'Centros Poblados'
        db_table_comment = 'Centros poblados por municipio'


class PasswordResetToken(models.Model):
    """
    Token para recuperación de contraseña.

    Cada token es válido por 1 hora y solo puede usarse una vez.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        verbose_name='Usuario'
    )
    token = models.CharField('Token', max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    expires_at = models.DateTimeField('Fecha de expiración')
    used = models.BooleanField('Usado', default=False)
    used_at = models.DateTimeField('Fecha de uso', null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'password_reset_token'
        verbose_name = 'Token de recuperación de contraseña'
        verbose_name_plural = 'Tokens de recuperación de contraseña'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'used']),
        ]

    def __str__(self):
        return f"Token para {self.user.username} - {'Usado' if self.used else 'Activo'}"

    @classmethod
    def create_token(cls, user):
        """Crea un nuevo token para el usuario (válido por 1 hora)"""
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=1)

        return cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )

    def is_valid(self):
        """Verifica si el token es válido (no usado y no expirado)"""
        return not self.used and timezone.now() < self.expires_at

    def mark_as_used(self):
        """Marca el token como usado"""
        self.used = True
        self.used_at = timezone.now()
        self.save(update_fields=['used', 'used_at'])


# ============================================================================
# MODELOS PARA INDEXACIÓN COMPLETA DE PRE-OPERACIÓN (EXCLUYENDO 07_insu)
# ============================================================================
# Estos modelos almacenan los directorios y archivos de pre-operación
# que NO están en 07_insu (que ya se indexa con el sistema de insumos existente)
# ============================================================================

class DirectorioPreoperacion(models.Model):
    """
    Directorios de pre-operación (EXCLUYENDO 07_insu que se maneja en insumos)
    Similar a directorios_operacion pero para pre-operación.

    Estructura indexada:
    - 01_prop (Propuesta)
    - 02_carta_acept (Carta de Aceptación)
    - 03_cto_modif (Contrato/Modificación)
    - 04_acta_ini (Acta de Inicio)
    - 05_plan_gest_proy (Plan de Gestión del Proyecto)
    - 06_precono (Pre-Conocimiento)
    - 08_contr_pers (Control de Personal)

    NOTA: 07_insu se EXCLUYE porque ya está indexado en insumos/clasificacion_insumo
    """
    cod_directorio = models.AutoField(primary_key=True)
    nom_directorio = models.CharField(max_length=255)
    ruta_directorio = models.TextField(unique=True)
    nivel = models.IntegerField(default=0, help_text="Nivel de profundidad: 0=raíz de 01_preo")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subdirectorios',
        db_column='parent_id'
    )
    cod_mpio = models.ForeignKey(
        Municipios,
        on_delete=models.CASCADE,
        db_column='cod_mpio',
        related_name='directorios_preoperacion'
    )
    fecha_creacion = models.DateTimeField(null=True, blank=True)
    fecha_modificacion = models.DateTimeField(null=True, blank=True)
    propietario = models.CharField(max_length=255, null=True, blank=True)
    fecha_indexacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'directorios_preoperacion'
        verbose_name = 'Directorio Pre-Operación'
        verbose_name_plural = 'Directorios Pre-Operación'
        ordering = ['nivel', 'nom_directorio']
        indexes = [
            models.Index(fields=['cod_mpio'], name='dir_preo_mpio_idx'),
            models.Index(fields=['parent'], name='dir_preo_parent_idx'),
            models.Index(fields=['nivel'], name='dir_preo_nivel_idx'),
        ]

    def __str__(self):
        return f"{self.nom_directorio} (Nivel {self.nivel})"

    def get_ruta_completa(self):
        """Retorna la ruta completa del directorio"""
        return self.ruta_directorio

    def get_archivos_count(self):
        """Cuenta los archivos en este directorio"""
        return self.archivos.count()

    def get_subdirectorios_count(self):
        """Cuenta los subdirectorios inmediatos"""
        return self.subdirectorios.count()

    def get_tamano_total(self):
        """Calcula el tamaño total de archivos en el directorio"""
        total = self.archivos.aggregate(total=models.Sum('tamano_bytes'))['total']
        return total or 0


class ArchivoPreoperacion(models.Model):
    """
    Archivos de pre-operación (EXCLUYENDO archivos de 07_insu)
    Similar a archivos_operacion pero para pre-operación.
    """
    cod_archivo = models.AutoField(primary_key=True)
    nom_archivo = models.CharField(max_length=500)
    ruta_archivo = models.TextField(unique=True)
    extension = models.CharField(max_length=50, null=True, blank=True)
    tamano_bytes = models.BigIntegerField(null=True, blank=True)
    propietario = models.CharField(max_length=255, null=True, blank=True)
    hash_contenido = models.CharField(max_length=255, null=True, blank=True)
    cod_directorio = models.ForeignKey(
        DirectorioPreoperacion,
        on_delete=models.CASCADE,
        db_column='cod_directorio',
        related_name='archivos'
    )
    fecha_creacion = models.DateTimeField(null=True, blank=True)
    fecha_modificacion = models.DateTimeField(null=True, blank=True)
    fecha_indexacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'archivos_preoperacion'
        verbose_name = 'Archivo Pre-Operación'
        verbose_name_plural = 'Archivos Pre-Operación'
        ordering = ['nom_archivo']
        indexes = [
            models.Index(fields=['cod_directorio'], name='arch_preo_dir_idx'),
            models.Index(fields=['extension'], name='arch_preo_ext_idx'),
            models.Index(fields=['propietario'], name='arch_preo_prop_idx'),
        ]

    def __str__(self):
        return self.nom_archivo

    def get_tamano_legible(self):
        """Retorna el tamaño en formato legible (KB, MB, GB)"""
        if not self.tamano_bytes:
            return "0 B"

        tamano = float(self.tamano_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if tamano < 1024.0:
                return f"{tamano:.2f} {unit}"
            tamano /= 1024.0
        return f"{tamano:.2f} PB"

    def get_municipio(self):
        """Obtiene el municipio a través del directorio"""
        return self.cod_directorio.cod_mpio if self.cod_directorio else None