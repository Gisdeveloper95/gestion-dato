from rest_framework import serializers
from django.contrib.auth.models import User
from backend.path_utils import linux_to_windows_path  # Conversión Linux -> Windows para frontend
from .models import (
    Departamentos, Municipios, Usuarios, TiposInsumos, Categorias,
    TiposFormato, Concepto, Entidades, DetalleInsumo, Insumos, ClasificacionInsumo, Notificaciones,
    MecanismoGeneral, MecanismoDetalle, AlcanceOperacion, Grupo, EstadosInsumo,InfoAdministrativa,
     Zonas, PathDirPre, PathDirPost ,ListaArchivosPre,TerritorialesIgac,CentrosPoblados,
    RolesSeguimiento,ProfesionalesSeguimiento,ProfesionalTerritorial, ProfesionalMunicipio,MecanismoOperacion,Auditoria,
    DirectorioPreoperacion, ArchivoPreoperacion,  # Nuevos modelos para indexación pre-operación
    SubClasificacionFuenteSecundaria
)

# Serializer para el modelo User de Django
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# Serializer para Zonas
class ZonasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zonas
        fields = '__all__'



class MecanismoGeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = MecanismoGeneral
        fields = '__all__'

class MecanismoDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MecanismoDetalle
        fields = '__all__'



class AlcanceOperacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlcanceOperacion
        fields = '__all__'

class GrupoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grupo
        fields = '__all__'

# Serializers para las tablas principales
class DepartamentosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamentos
        fields = '__all__'

class MunicipiosSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipios
        fields = '__all__'

class MunicipiosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipios
        fields = '__all__'
    
    # Nested serialization for related models
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['departamento'] = DepartamentosSerializer(instance.cod_depto).data
        
        # Añadir información del territorial si existe
        if instance.nom_territorial:
            try:
                territorial = TerritorialesIgac.objects.get(nom_territorial=instance.nom_territorial)
                representation['territorial_info'] = TerritorialesIgacSerializer(territorial).data
            except TerritorialesIgac.DoesNotExist:
                representation['territorial_info'] = {'nom_territorial': instance.nom_territorial}
        
        if instance.mecanismo_detalle:
            try:
                mecanismo_detalle = MecanismoDetalle.objects.get(cod_mecanismo_detalle=instance.mecanismo_detalle)
                representation['mecanismo_detalle_info'] = MecanismoDetalleSerializer(mecanismo_detalle).data
            except MecanismoDetalle.DoesNotExist:
                representation['mecanismo_detalle_info'] = {'cod_mecanismo_detalle': instance.mecanismo_detalle}
        

        
        if instance.alcance_operacion:
            try:
                alcance = AlcanceOperacion.objects.get(cod_alcance=instance.alcance_operacion)
                representation['alcance_operacion_info'] = AlcanceOperacionSerializer(alcance).data
            except AlcanceOperacion.DoesNotExist:
                representation['alcance_operacion_info'] = {'cod_alcance': instance.alcance_operacion}
        
        if instance.grupo:
            try:
                grupo = Grupo.objects.get(cod_grupo=instance.grupo)
                representation['grupo_info'] = GrupoSerializer(grupo).data
            except Grupo.DoesNotExist:
                representation['grupo_info'] = {'cod_grupo': instance.grupo}
            
        # Añadir el campo mecanismo_operacion si existe
        if instance.mecanismo_operacion:
            try:
                operacion = MecanismoOperacion.objects.get(cod_operacion=instance.mecanismo_operacion)
                representation['mecanismo_operacion_info'] = MecanismoOperacionSerializer(operacion).data
            except MecanismoOperacion.DoesNotExist:
                representation['mecanismo_operacion_info'] = {'cod_operacion': instance.mecanismo_operacion}
        
        return representation

class UsuariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = '__all__'

class TiposInsumosSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposInsumos
        fields = '__all__'

class CategoriasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorias
        fields = '__all__'

class TiposFormatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposFormato
        fields = '__all__'

class ConceptoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concepto
        fields = '__all__'

class EntidadesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entidades
        fields = '__all__'

class ClasificacionInsumoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClasificacionInsumo
        fields = '__all__'

class SubClasificacionFuenteSecundariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubClasificacionFuenteSecundaria
        fields = ['cod_sub_clasificacion', 'dominio', 'nombre', 'orden']

# Serializador simple para Insumos
class InsumosSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insumos
        fields = '__all__'

# Serializador completo para Insumos con relaciones anidadas
class InsumosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insumos
        fields = '__all__'
    
    # Nested serialization for related models
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['municipio'] = MunicipiosSimpleSerializer(instance.cod_municipio).data
        representation['categoria'] = CategoriasSerializer(instance.cod_categoria).data
        representation['tipo_insumo'] = TiposInsumosSerializer(instance.tipo_insumo).data
        return representation

# Serializador detallado para ClasificacionInsumo
class ClasificacionInsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClasificacionInsumo
        fields = '__all__'
    
    # Nested serialization for related models
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['insumo'] = InsumosSerializer(instance.cod_insumo).data
        return representation

# En preoperacion/serializers.py - Agregar nuevo serializer

class DetalleInsumoOptimizadoSerializer(serializers.ModelSerializer):
    """Serializer optimizado que incluye datos relacionados"""
    
    # Campos calculados para evitar consultas adicionales
    municipio_nombre = serializers.CharField(
        source='cod_clasificacion.cod_insumo.cod_municipio.nom_municipio', 
        read_only=True
    )
    municipio_codigo = serializers.CharField(
        source='cod_clasificacion.cod_insumo.cod_municipio.cod_municipio', 
        read_only=True
    )
    departamento_nombre = serializers.CharField(
        source='cod_clasificacion.cod_insumo.cod_municipio.cod_depto.nom_depto', 
        read_only=True
    )
    clasificacion_nombre = serializers.CharField(
        source='cod_clasificacion.nombre', 
        read_only=True
    )
    categoria_nombre = serializers.CharField(
        source='cod_clasificacion.cod_insumo.cod_categoria.nom_categoria', 
        read_only=True
    )
    entidad_nombre = serializers.CharField(
        source='cod_entidad.nom_entidad', 
        read_only=True
    )
    usuario_nombre = serializers.CharField(
        source='cod_usuario.nombre', 
        read_only=True
    )
    centro_poblado_nombre = serializers.CharField(
        source='cod_centro_poblado.nom_centro_poblado',
        read_only=True
    )
    sub_clasificacion_nombre = serializers.CharField(
        source='cod_sub_clasificacion.nombre',
        read_only=True,
        default=None
    )

    class Meta:
        model = DetalleInsumo
        fields = [
            'cod_detalle', 'escala', 'estado', 'cubrimiento', 'area',
            'fecha_entrega', 'fecha_disposicion', 'observacion', 'vigencia',
            'formato_tipo', 'zona', 'ruta_archivo', 'porcentaje_cubrimiento',
            # Campos relacionados pre-cargados
            'municipio_nombre', 'municipio_codigo', 'departamento_nombre',
            'clasificacion_nombre', 'categoria_nombre', 'entidad_nombre',
            'usuario_nombre', 'centro_poblado_nombre', 'sub_clasificacion_nombre'
        ]
        
# Serializador simple para DetalleInsumo
class DetalleInsumoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleInsumo
        fields = '__all__'

# Serializador detallado para DetalleInsumo
# Actualizado para auto-generar cod_detalle en creación
class DetalleInsumoSerializer(serializers.ModelSerializer):
    # cod_detalle es opcional en creación - se auto-genera si no se proporciona
    cod_detalle = serializers.IntegerField(required=False)

    class Meta:
        model = DetalleInsumo
        fields = [
            'cod_detalle', 'escala', 'estado', 'cubrimiento',
            'fecha_entrega', 'fecha_disposicion', 'area',
            'cod_entidad', 'observacion', 'vigencia',
            'formato_tipo', 'cod_usuario', 'cod_clasificacion',
            'zona', 'cod_centro_poblado', 'ruta_archivo', 'porcentaje_cubrimiento',
            'cod_sub_clasificacion'
        ]

    def create(self, validated_data):
        """Auto-genera cod_detalle si no se proporciona o si ya existe"""
        from django.db import connection

        # Obtener el máximo cod_detalle actual directamente de la BD
        with connection.cursor() as cursor:
            cursor.execute("SELECT COALESCE(MAX(cod_detalle), 0) FROM detalle_insumo")
            max_cod = cursor.fetchone()[0]

        # Siempre usar el siguiente disponible para evitar conflictos
        validated_data['cod_detalle'] = max_cod + 1

        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['entidad'] = EntidadesSerializer(instance.cod_entidad).data
        representation['formato'] = TiposFormatoSerializer(instance.formato_tipo).data
        representation['usuario'] = UsuariosSerializer(instance.cod_usuario).data
        representation['clasificacion'] = ClasificacionInsumoSimpleSerializer(instance.cod_clasificacion).data

        if instance.zona:
            representation['zona_info'] = ZonasSerializer(instance.zona).data


        if instance.cod_centro_poblado:
            representation['centro_poblado_info'] = CentrosPobladosSimpleSerializer(instance.cod_centro_poblado).data

        if instance.cod_sub_clasificacion:
            representation['sub_clasificacion_info'] = SubClasificacionFuenteSecundariaSerializer(instance.cod_sub_clasificacion).data

        return representation
    

# Serializador para Notificaciones
class NotificacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificaciones
        fields = '__all__'

# Serializers corregidos

class PathDirPreSerializer(serializers.ModelSerializer):
    """Serializer para rutas preoperativas"""
    municipio_nombre = serializers.ReadOnlyField(source='cod_municipio.nom_municipio')
    
    class Meta:
        model = PathDirPre
        fields = ['id', 'cod_municipio', 'municipio_nombre', 'path', 'fecha_creacion']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Si necesitas incluir información completa del municipio
        representation['municipio'] = MunicipiosSimpleSerializer(instance.cod_municipio).data
        return representation


class PathDirPostSerializer(serializers.ModelSerializer):
    """Serializer para rutas postoperativas"""
    municipio_nombre = serializers.ReadOnlyField(source='cod_municipio.nom_municipio')
    
    class Meta:
        model = PathDirPost
        fields = ['id', 'cod_municipio', 'municipio_nombre', 'path', 'fecha_creacion']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Si necesitas incluir información completa del municipio
        representation['municipio'] = MunicipiosSimpleSerializer(instance.cod_municipio).data
        return representation

class ListaArchivosPreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListaArchivosPre
        fields = '__all__'


# Agregar estos serializers a preoperacion/serializers.py

class RolesSeguimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolesSeguimiento
        fields = '__all__'

class TerritorialesIgacSerializer(serializers.ModelSerializer):
    class Meta:
        model = TerritorialesIgac
        fields = '__all__'

class ProfesionalesSeguimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfesionalesSeguimiento
        fields = '__all__'
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['rol'] = RolesSeguimientoSerializer(instance.rol_profesional).data
        return representation

class ProfesionalTerritorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfesionalTerritorial
        fields = '__all__'
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['profesional'] = ProfesionalesSeguimientoSerializer(instance.cod_profesional).data
        representation['territorial'] = TerritorialesIgacSerializer(instance.territorial_seguimiento).data
        return representation

class ProfesionalMunicipioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfesionalMunicipio
        fields = '__all__'
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['profesional'] = ProfesionalesSeguimientoSerializer(instance.cod_profesional).data
        representation['municipio'] = MunicipiosSimpleSerializer(instance.cod_municipio).data
        return representation
    

class MecanismoOperacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MecanismoOperacion
        fields = '__all__'

# Add this serializer to the serializers.py file
class EstadosInsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadosInsumo
        fields = '__all__'

class AuditoriaSerializer(serializers.ModelSerializer):
    # Campos calculados
    usuario_nombre = serializers.ReadOnlyField(source='usuario.nombre')
    entidad_info = serializers.SerializerMethodField()

    class Meta:
        model = Auditoria
        fields = '__all__'
        
    def get_entidad_info(self, obj):
        """Obtiene información adicional sobre la entidad relacionada"""
        try:
            # Intentar obtener información según el tipo de entidad
            if obj.tipo_entidad == 'municipio':
                municipio = Municipios.objects.get(cod_municipio=obj.id_entidad)
                return {
                    'nombre': municipio.nom_municipio,
                    'departamento': municipio.cod_depto.nom_depto
                }
            elif obj.tipo_entidad == 'insumo':
                insumo = Insumos.objects.get(cod_insumo=obj.id_entidad)
                return {
                    'municipio': insumo.cod_municipio.nom_municipio,
                    'categoria': insumo.cod_categoria.nom_categoria
                }
            elif obj.tipo_entidad == 'clasificacion':
                clasificacion = ClasificacionInsumo.objects.get(cod_clasificacion=obj.id_entidad)
                return {
                    'nombre': clasificacion.nombre,
                    'insumo': clasificacion.cod_insumo.cod_insumo
                }
            elif obj.tipo_entidad == 'detalle':
                detalle = DetalleInsumo.objects.get(cod_detalle=obj.id_entidad)
                return {
                    'clasificacion': detalle.cod_clasificacion.nombre,
                    'entidad': detalle.cod_entidad.nom_entidad
                }
            elif obj.tipo_entidad == 'concepto':
                concepto = Concepto.objects.get(cod_concepto=obj.id_entidad)
                return {
                    'concepto': concepto.concepto[:50] + '...' if len(concepto.concepto) > 50 else concepto.concepto
                }
        except Exception:
            # Si hay error al obtener datos, devolver solo el ID
            return {'id': obj.id_entidad}
        
        # Si no se maneja el tipo de entidad, devolver solo el ID
        return {'id': obj.id_entidad}
    

class InfoAdministrativaSerializer(serializers.ModelSerializer):
    """Serializer para información administrativa"""
    municipio_nombre = serializers.ReadOnlyField(source='cod_municipio.nom_municipio')
    departamento_nombre = serializers.ReadOnlyField(source='cod_municipio.cod_depto.nom_depto')
    
    class Meta:
        model = InfoAdministrativa
        fields = '__all__'
    
    def to_representation(self, instance):
        """Incluir información detallada del municipio"""
        representation = super().to_representation(instance)
        representation['municipio'] = MunicipiosSimpleSerializer(instance.cod_municipio).data
        return representation


class InfoAdministrativaSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple para información administrativa (para listas)"""
    municipio_nombre = serializers.ReadOnlyField(source='cod_municipio.nom_municipio')
    departamento_nombre = serializers.ReadOnlyField(source='cod_municipio.cod_depto.nom_depto')

    class Meta:
        model = InfoAdministrativa
        fields = [
            'cod_info_admin',
            'cod_municipio',
            'municipio_nombre',
            'departamento_nombre',
            'id_gestor_catas',
            'gestor_prestador_servicio',
            'publicacion_year',
            'vigencia_rural',
            'vigencia_urbana',
            'estado_rural',
            'estado_urbano',
            'predios_rurales',              
            'area_terreno_rural_m2',        
            'area_terreno_rural_ha',        
            'area_construida_rural_m2',     
            'avaluo_rural',                 
            'predios_urbanos',              
            'area_terreno_urbana_m2',       
            'area_terreno_urbana_ha',       
            'area_construida_urbana_m2',    
            'avaluo_urbano_1',              
            'avaluo_urbano_2',              
            'total_predios',
            'total_area_terreno_m2',        
            'total_area_terreno_ha',
            'total_area_construida_m2',     
            'total_avaluos',
            'area_geografica_rural_ha',     
            'area_geografica_urbana_ha',    
            'area_rural_estados_catastrales_ha',    
            'area_urbana_estados_catastrales_ha',   
            'observacion'                   
        ]


class CentrosPobladosSerializer(serializers.ModelSerializer):
    """Serializer para centros poblados"""
    municipio_nombre = serializers.ReadOnlyField(source='cod_municipio.nom_municipio')
    departamento_nombre = serializers.ReadOnlyField(source='cod_municipio.cod_depto.nom_depto')
    
    class Meta:
        model = CentrosPoblados
        fields = '__all__'
    
    def to_representation(self, instance):
        """Incluir información detallada del municipio"""
        representation = super().to_representation(instance)
        representation['municipio'] = MunicipiosSimpleSerializer(instance.cod_municipio).data
        return representation


class CentrosPobladosSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple para centros poblados (para listas)"""
    municipio_nombre = serializers.ReadOnlyField(source='cod_municipio.nom_municipio')

    class Meta:
        model = CentrosPoblados
        fields = [
            'cod_centro_poblado', 'cod_municipio', 'municipio_nombre',
            'nom_centro_poblado', 'area_oficial_ha'
        ]


# ============================================================================
# SERIALIZERS PARA INDEXACIÓN PRE-OPERACIÓN (EXCLUYENDO 07_insu)
# ============================================================================

class ArchivoPreoperacionSerializer(serializers.ModelSerializer):
    """Serializer para archivos de pre-operación (excluyendo insumos)"""
    tamano_legible = serializers.SerializerMethodField()
    municipio_nombre = serializers.SerializerMethodField()
    ruta_windows = serializers.SerializerMethodField()  # Ruta convertida para frontend

    class Meta:
        model = ArchivoPreoperacion
        fields = [
            'cod_archivo', 'nom_archivo', 'ruta_archivo', 'ruta_windows', 'extension',
            'tamano_bytes', 'tamano_legible', 'propietario', 'hash_contenido',
            'cod_directorio', 'fecha_creacion', 'fecha_modificacion',
            'fecha_indexacion', 'municipio_nombre'
        ]

    def get_tamano_legible(self, obj):
        return obj.get_tamano_legible()

    def get_municipio_nombre(self, obj):
        municipio = obj.get_municipio()
        return municipio.nom_municipio if municipio else None

    def get_ruta_windows(self, obj):
        """Convierte la ruta Linux a formato Windows para el frontend"""
        return linux_to_windows_path(obj.ruta_archivo)


class ArchivoPreoperacionSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple para archivos (listas)"""
    tamano_legible = serializers.SerializerMethodField()

    class Meta:
        model = ArchivoPreoperacion
        fields = [
            'cod_archivo', 'nom_archivo', 'extension',
            'tamano_legible', 'propietario', 'fecha_modificacion'
        ]

    def get_tamano_legible(self, obj):
        return obj.get_tamano_legible()


class DirectorioPreoperacionSerializer(serializers.ModelSerializer):
    """Serializer para directorios de pre-operación"""
    archivos_count = serializers.SerializerMethodField()
    subdirectorios_count = serializers.SerializerMethodField()
    tamano_total = serializers.SerializerMethodField()
    municipio_nombre = serializers.ReadOnlyField(source='cod_mpio.nom_municipio')
    ruta_windows = serializers.SerializerMethodField()  # Ruta convertida para frontend
    archivos = ArchivoPreoperacionSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = DirectorioPreoperacion
        fields = [
            'cod_directorio', 'nom_directorio', 'ruta_directorio', 'ruta_windows', 'nivel',
            'parent', 'cod_mpio', 'municipio_nombre', 'fecha_creacion',
            'fecha_modificacion', 'propietario', 'fecha_indexacion',
            'archivos_count', 'subdirectorios_count', 'tamano_total', 'archivos'
        ]

    def get_archivos_count(self, obj):
        return obj.get_archivos_count()

    def get_subdirectorios_count(self, obj):
        return obj.get_subdirectorios_count()

    def get_tamano_total(self, obj):
        tamano = obj.get_tamano_total()
        # Convertir a formato legible
        if not tamano:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if tamano < 1024.0:
                return f"{tamano:.2f} {unit}"
            tamano /= 1024.0
        return f"{tamano:.2f} PB"

    def get_ruta_windows(self, obj):
        """Convierte la ruta Linux a formato Windows para el frontend"""
        return linux_to_windows_path(obj.ruta_directorio)


class DirectorioPreoperacionSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple para directorios (listas y árbol)"""
    archivos_count = serializers.SerializerMethodField()
    subdirectorios_count = serializers.SerializerMethodField()

    class Meta:
        model = DirectorioPreoperacion
        fields = [
            'cod_directorio', 'nom_directorio', 'nivel', 'parent',
            'archivos_count', 'subdirectorios_count'
        ]

    def get_archivos_count(self, obj):
        return obj.get_archivos_count()

    def get_subdirectorios_count(self, obj):
        return obj.get_subdirectorios_count()


class DirectorioPreoperacionArbolSerializer(serializers.ModelSerializer):
    """Serializer para vista de árbol con hijos anidados"""
    hijos = serializers.SerializerMethodField()
    archivos_count = serializers.SerializerMethodField()
    tipo = serializers.SerializerMethodField()

    class Meta:
        model = DirectorioPreoperacion
        fields = [
            'cod_directorio', 'nom_directorio', 'nivel',
            'archivos_count', 'hijos', 'tipo'
        ]

    def get_hijos(self, obj):
        subdirectorios = obj.subdirectorios.all()
        return DirectorioPreoperacionArbolSerializer(subdirectorios, many=True).data

    def get_archivos_count(self, obj):
        return obj.get_archivos_count()

    def get_tipo(self, obj):
        return 'directorio'