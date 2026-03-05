from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import path
from django.shortcuts import render, redirect
from django.db import connection
from django import forms
# Añadir a los imports existentes
from .models import (
    Departamentos, Municipios, Usuarios, TiposInsumos, Categorias,
    TiposFormato, Concepto, Entidades, DetalleInsumo, Insumos, ClasificacionInsumo,
    MecanismoGeneral, MecanismoDetalle,
    AlcanceOperacion, Grupo, Notificaciones,MecanismoOperacion, Zonas, PathDirPre, PathDirPost, ListaArchivosPre,
    RolesSeguimiento, TerritorialesIgac, ProfesionalesSeguimiento,
    ProfesionalTerritorial, ProfesionalMunicipio,EstadosInsumo,
    InfoAdministrativa, CentrosPoblados
)

# Formulario para actualización directa de cod_usuario
class CambiarCodUsuarioForm(forms.Form):
    nuevo_cod_usuario = forms.IntegerField(label="Nuevo código de usuario")

# Admin para Usuarios que incluye una vista personalizada
class UsuariosAdmin(admin.ModelAdmin):
    list_display = ('cod_usuario', 'nombre', 'correo')
    search_fields = ('nombre', 'correo')
    ordering = ('cod_usuario',)
    readonly_fields = ()  # No hacemos ningún campo readonly por defecto
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/cambiar_codigo/',
                self.admin_site.admin_view(self.cambiar_codigo_view),
                name='api_usuarios_cambiar_codigo',
            ),
        ]
        return custom_urls + urls
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_cambiar_codigo'] = True
        extra_context['cod_usuario_actual'] = object_id
        return super().change_view(request, object_id, form_url, extra_context)
    
    def cambiar_codigo_view(self, request, object_id):
        # Obtener el usuario actual
        try:
            usuario = Usuarios.objects.get(pk=object_id)
        except Usuarios.DoesNotExist:
            return redirect('admin:api_usuarios_changelist')
        
        if request.method == 'POST':
            form = CambiarCodUsuarioForm(request.POST)
            if form.is_valid():
                nuevo_codigo = form.cleaned_data['nuevo_cod_usuario']
                
                # Ejecutar SQL directo para actualizar solo el código sin tocar el correo
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "UPDATE usuarios SET cod_usuario = %s WHERE cod_usuario = %s",
                            [nuevo_codigo, usuario.cod_usuario]
                        )
                    
                    self.message_user(request, f"Código de usuario actualizado correctamente de {usuario.cod_usuario} a {nuevo_codigo}")
                    return redirect('admin:api_usuarios_changelist')
                except Exception as e:
                    self.message_user(request, f"Error: {str(e)}", level='error')
        else:
            form = CambiarCodUsuarioForm(initial={'nuevo_cod_usuario': usuario.cod_usuario})
        
        context = {
            'title': f'Cambiar código para {usuario.nombre}',
            'form': form,
            'usuario': usuario,
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/usuarios_cambiar_codigo.html', context)


# En preoperacion/admin.py
class MunicipiosAdmin(admin.ModelAdmin):
    list_display = ('cod_municipio', 'nom_municipio', 'cod_depto', 'fecha_inicio', 'mecanismo_general', 'grupo')

    list_filter = ('cod_depto', 'mecanismo_general', 'mecanismo_detalle', 'grupo', 'mecanismo_operacion', 'nom_territorial')
    search_fields = ('nom_municipio', 'cod_municipio')
    ordering = ('cod_municipio',)


# Admin para DetalleInsumo con filtros mejorados
class DetalleInsumoAdmin(admin.ModelAdmin):
    list_display = ('cod_detalle', 'cod_usuario', 'cod_clasificacion', 'cod_entidad', 'estado', 'zona', 'fecha_entrega')
    list_filter = ('estado', 'zona', 'formato_tipo', 'cod_entidad')
    search_fields = ('cod_detalle', 'observacion')
    date_hierarchy = 'fecha_entrega'

# Admin para ClasificacionInsumo
class ClasificacionInsumoAdmin(admin.ModelAdmin):
    list_display = ('cod_clasificacion', 'nombre', 'cod_insumo')
    search_fields = ('nombre', 'cod_clasificacion')
    list_filter = ('cod_insumo',)

# Admin para Insumos
class InsumosAdmin(admin.ModelAdmin):
    list_display = ('cod_insumo', 'cod_municipio', 'cod_categoria', 'tipo_insumo')
    list_filter = ('cod_categoria', 'tipo_insumo')
    search_fields = ('cod_insumo',)

# Admin para Notificaciones
class NotificacionesAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_entidad', 'id_entidad', 'accion', 'fecha_cambio', 'leido')
    list_filter = ('tipo_entidad', 'accion', 'leido')
    search_fields = ('descripcion',)
    date_hierarchy = 'fecha_cambio'
    
    actions = ['marcar_como_leidas', 'marcar_como_no_leidas']
    
    def marcar_como_leidas(self, request, queryset):
        queryset.update(leido=True)
        self.message_user(request, f"Se marcaron {queryset.count()} notificaciones como leídas")
    marcar_como_leidas.short_description = "Marcar seleccionadas como leídas"
    
    def marcar_como_no_leidas(self, request, queryset):
        queryset.update(leido=False)
        self.message_user(request, f"Se marcaron {queryset.count()} notificaciones como no leídas")
    marcar_como_no_leidas.short_description = "Marcar seleccionadas como no leídas"


# Configuración de administración para PathDirPre
class PathDirPreAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_municipio', 'get_short_path', 'fecha_creacion')
    list_filter = ('fecha_creacion',)
    search_fields = ('cod_municipio__nom_municipio', 'path')
    raw_id_fields = ('cod_municipio',)
    
    def get_municipio(self, obj):
        return obj.cod_municipio.nom_municipio
    get_municipio.short_description = 'Municipio'
    get_municipio.admin_order_field = 'cod_municipio__nom_municipio'
    
    def get_short_path(self, obj):
        return obj.path[:50] + "..." if len(obj.path) > 50 else obj.path
    get_short_path.short_description = 'Ruta'


# Configuración de administración para PathDirPost

class PathDirPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_municipio', 'get_short_path', 'fecha_creacion')
    list_filter = ('fecha_creacion',)
    search_fields = ('cod_municipio__nom_municipio', 'path')
    raw_id_fields = ('cod_municipio',)
    
    def get_municipio(self, obj):
        return obj.cod_municipio.nom_municipio
    get_municipio.short_description = 'Municipio'
    get_municipio.admin_order_field = 'cod_municipio__nom_municipio'
    
    def get_short_path(self, obj):
        return obj.path[:50] + "..." if len(obj.path) > 50 else obj.path
    get_short_path.short_description = 'Ruta'

@admin.register(ListaArchivosPre)
class ListaArchivosPreAdmin(admin.ModelAdmin):
    list_display = ('id_lista_archivo', 'cod_insumo', 'nombre_insumo', 'fecha_disposicion')
    list_filter = ('fecha_disposicion',)
    search_fields = ('nombre_insumo', 'observacion')


# Agregar estas clases en preoperacion/admin.py

@admin.register(RolesSeguimiento)
class RolesSeguimientoAdmin(admin.ModelAdmin):
    list_display = ('rol_profesional',)
    search_fields = ('rol_profesional',)

@admin.register(TerritorialesIgac)
class TerritorialesIgacAdmin(admin.ModelAdmin):
    list_display = ('nom_territorial',)
    search_fields = ('nom_territorial',)

@admin.register(ProfesionalesSeguimiento)
class ProfesionalesSeguimientoAdmin(admin.ModelAdmin):
    list_display = ('cod_profesional', 'nombre_profesional', 'correo_profesional', 'rol_profesional', 'get_territoriales_count', 'get_municipios_count')
    list_filter = ('rol_profesional',)
    search_fields = ('cod_profesional', 'nombre_profesional', 'correo_profesional')
    ordering = ('cod_profesional',)
    
    def get_territoriales_count(self, obj):
        """Contar territoriales asignadas"""
        return ProfesionalTerritorial.objects.filter(cod_profesional=obj).count()
    get_territoriales_count.short_description = 'Territoriales'
    
    def get_municipios_count(self, obj):
        """Contar municipios asignados"""
        return ProfesionalMunicipio.objects.filter(cod_profesional=obj).count()
    get_municipios_count.short_description = 'Municipios'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/eliminar_cascada/',
                self.admin_site.admin_view(self.eliminar_cascada_view),
                name='preoperacion_profesionalesseguimiento_eliminar_cascada',
            ),
        ]
        return custom_urls + urls
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        
        # Obtener información de relaciones para mostrar en el admin
        try:
            profesional = ProfesionalesSeguimiento.objects.get(pk=object_id)
            
            # Contar relaciones
            territoriales_count = ProfesionalTerritorial.objects.filter(cod_profesional=profesional).count()
            municipios_count = ProfesionalMunicipio.objects.filter(cod_profesional=profesional).count()
            
            extra_context.update({
                'show_eliminar_cascada': True,
                'territoriales_count': territoriales_count,
                'municipios_count': municipios_count,
                'total_relaciones': territoriales_count + municipios_count
            })
        except ProfesionalesSeguimiento.DoesNotExist:
            pass
            
        return super().change_view(request, object_id, form_url, extra_context)
    
    def eliminar_cascada_view(self, request, object_id):
        """Vista personalizada para eliminar en cascada"""
        try:
            profesional = ProfesionalesSeguimiento.objects.get(pk=object_id)
        except ProfesionalesSeguimiento.DoesNotExist:
            messages.error(request, "El profesional no existe.")
            return redirect('admin:preoperacion_profesionalesseguimiento_changelist')
        
        if request.method == 'POST':
            confirmar = request.POST.get('confirmar')
            if confirmar == 'si':
                try:
                    with transaction.atomic():
                        # Contar registros que se van a eliminar
                        territoriales_count = ProfesionalTerritorial.objects.filter(cod_profesional=profesional).count()
                        municipios_count = ProfesionalMunicipio.objects.filter(cod_profesional=profesional).count()
                        
                        # Eliminar en cascada manualmente para tener control
                        ProfesionalTerritorial.objects.filter(cod_profesional=profesional).delete()
                        ProfesionalMunicipio.objects.filter(cod_profesional=profesional).delete()
                        
                        # Eliminar el profesional
                        profesional.delete()
                        
                        messages.success(
                            request, 
                            f"Profesional {profesional.nombre_profesional} eliminado exitosamente. "
                            f"Se eliminaron {territoriales_count} asignaciones territoriales y "
                            f"{municipios_count} asignaciones de municipios."
                        )
                        
                        return redirect('admin:preoperacion_profesionalesseguimiento_changelist')
                        
                except Exception as e:
                    messages.error(request, f"Error al eliminar: {str(e)}")
            else:
                messages.info(request, "Eliminación cancelada.")
                return redirect('admin:preoperacion_profesionalesseguimiento_change', object_id=object_id)
        
        # Obtener información detallada para la confirmación
        territoriales = ProfesionalTerritorial.objects.filter(cod_profesional=profesional).select_related('territorial_seguimiento')
        municipios = ProfesionalMunicipio.objects.filter(cod_profesional=profesional).select_related('cod_municipio')
        
        context = {
            'title': f'Eliminar en cascada: {profesional.nombre_profesional}',
            'profesional': profesional,
            'territoriales': territoriales,
            'municipios': municipios,
            'territoriales_count': territoriales.count(),
            'municipios_count': municipios.count(),
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/profesional_eliminar_cascada.html', context)
    
    actions = ['eliminar_seleccionados_cascada']
    
    def eliminar_seleccionados_cascada(self, request, queryset):
        """Acción para eliminar múltiples profesionales en cascada"""
        total_eliminados = 0
        total_territoriales = 0
        total_municipios = 0
        
        try:
            with transaction.atomic():
                for profesional in queryset:
                    # Contar antes de eliminar
                    territoriales_count = ProfesionalTerritorial.objects.filter(cod_profesional=profesional).count()
                    municipios_count = ProfesionalMunicipio.objects.filter(cod_profesional=profesional).count()
                    
                    # Eliminar relaciones
                    ProfesionalTerritorial.objects.filter(cod_profesional=profesional).delete()
                    ProfesionalMunicipio.objects.filter(cod_profesional=profesional).delete()
                    
                    # Acumular contadores
                    total_territoriales += territoriales_count
                    total_municipios += municipios_count
                    total_eliminados += 1
                
                # Eliminar los profesionales
                queryset.delete()
                
                self.message_user(
                    request, 
                    f"Se eliminaron {total_eliminados} profesionales, "
                    f"{total_territoriales} asignaciones territoriales y "
                    f"{total_municipios} asignaciones de municipios."
                )
                
        except Exception as e:
            self.message_user(request, f"Error en eliminación masiva: {str(e)}", level=messages.ERROR)
    
    eliminar_seleccionados_cascada.short_description = "Eliminar seleccionados en cascada"


class ProfesionalTerritorialInline(admin.TabularInline):
    model = ProfesionalTerritorial
    extra = 1

class ProfesionalMunicipioInline(admin.TabularInline):
    model = ProfesionalMunicipio
    extra = 1
    autocomplete_fields = ['cod_municipio']

@admin.register(ProfesionalTerritorial)
class ProfesionalTerritorialAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_profesional_nombre', 'get_profesional_codigo', 'territorial_seguimiento')
    list_filter = ('territorial_seguimiento', 'cod_profesional__rol_profesional')
    search_fields = ('cod_profesional__nombre_profesional', 'cod_profesional__cod_profesional', 'territorial_seguimiento__nom_territorial')
    
    def get_profesional_nombre(self, obj):
        return obj.cod_profesional.nombre_profesional
    get_profesional_nombre.short_description = 'Profesional'
    get_profesional_nombre.admin_order_field = 'cod_profesional__nombre_profesional'
    
    def get_profesional_codigo(self, obj):
        return obj.cod_profesional.cod_profesional
    get_profesional_codigo.short_description = 'Código'
    get_profesional_codigo.admin_order_field = 'cod_profesional__cod_profesional'

@admin.register(ProfesionalMunicipio)
class ProfesionalMunicipioAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_profesional_nombre', 'get_profesional_codigo', 'get_municipio')
    list_filter = ('cod_profesional__rol_profesional', 'cod_municipio__cod_depto')
    search_fields = ('cod_profesional__nombre_profesional', 'cod_profesional__cod_profesional', 'cod_municipio__nom_municipio')
    
    def get_profesional_nombre(self, obj):
        return obj.cod_profesional.nombre_profesional
    get_profesional_nombre.short_description = 'Profesional'
    get_profesional_nombre.admin_order_field = 'cod_profesional__nombre_profesional'
    
    def get_profesional_codigo(self, obj):
        return obj.cod_profesional.cod_profesional
    get_profesional_codigo.short_description = 'Código'
    get_profesional_codigo.admin_order_field = 'cod_profesional__cod_profesional'
    
    def get_municipio(self, obj):
        return f"{obj.cod_municipio.nom_municipio} ({obj.cod_municipio.cod_municipio})"
    get_municipio.short_description = 'Municipio'
    get_municipio.admin_order_field = 'cod_municipio__nom_municipio'

@admin.register(EstadosInsumo)
class EstadosInsumoAdmin(admin.ModelAdmin):
    list_display = ('estado',)
    search_fields = ('estado',)
    ordering = ('estado',)


@admin.register(InfoAdministrativa)
class InfoAdministrativaAdmin(admin.ModelAdmin):
    """Administración de Información Administrativa"""
    
    # Campos a mostrar en la lista
    list_display = [
        'cod_info_admin',
        'get_municipio_nombre', 
        'get_departamento_nombre',
        'gestor_prestador_servicio',
        'publicacion_year',
        'estado_rural',
        'estado_urbano',
        'total_predios'
    ]
    
    # Filtros laterales
    list_filter = [
        'publicacion_year',
        'estado_rural', 
        'estado_urbano',
        'gestor_prestador_servicio',
        'cod_municipio__cod_depto'
    ]
    
    # Campos de búsqueda
    search_fields = [
        'cod_municipio__nom_municipio',
        'cod_municipio__cod_depto__nom_depto',
        'gestor_prestador_servicio',
        'id_gestor_catas',
        'observacion'
    ]
    
    # Organización en fieldsets
    fieldsets = (
        ('Información General', {
            'fields': (
                'cod_municipio',
                'id_gestor_catas',
                'gestor_prestador_servicio',
                'publicacion_year'
            )
        }),
        ('Vigencias', {
            'fields': (
                'vigencia_rural',
                'vigencia_urbana'
            )
        }),
        ('Estados Catastrales', {
            'fields': (
                'estado_rural',
                'estado_urbano'
            )
        }),
        ('Información Rural', {
            'fields': (
                'predios_rurales',
                'area_terreno_rural_m2',
                'area_terreno_rural_ha',
                'area_construida_rural_m2',
                'avaluo_rural',
                'area_geografica_rural_ha',
                'area_rural_estados_catastrales_ha'
            ),
            'classes': ('collapse',)  # Colapsable
        }),
        ('Información Urbana', {
            'fields': (
                'predios_urbanos',
                'area_terreno_urbana_m2',
                'area_terreno_urbana_ha',
                'area_construida_urbana_m2',
                'avaluo_urbano_1',
                'avaluo_urbano_2',
                'area_geografica_urbana_ha',
                'area_urbana_estados_catastrales_ha'
            ),
            'classes': ('collapse',)  # Colapsable
        }),
        ('Totales', {
            'fields': (
                'total_predios',
                'total_area_terreno_m2',
                'total_area_terreno_ha',
                'total_area_construida_m2',
                'total_avaluos'
            )
        }),
        ('Observaciones', {
            'fields': ('observacion',)
        })
    )
    
    # Campos de solo lectura
    readonly_fields = ['cod_info_admin']
    
    # Ordenamiento por defecto
    ordering = ['-publicacion_year', 'cod_municipio__nom_municipio']
    
    # Paginación
    list_per_page = 25
    
    # Métodos personalizados para mostrar información relacionada
    def get_municipio_nombre(self, obj):
        return obj.cod_municipio.nom_municipio if obj.cod_municipio else '-'
    get_municipio_nombre.short_description = 'Municipio'
    get_municipio_nombre.admin_order_field = 'cod_municipio__nom_municipio'
    
    def get_departamento_nombre(self, obj):
        return obj.cod_municipio.cod_depto.nom_depto if obj.cod_municipio and obj.cod_municipio.cod_depto else '-'
    get_departamento_nombre.short_description = 'Departamento'
    get_departamento_nombre.admin_order_field = 'cod_municipio__cod_depto__nom_depto'


# =============== ADMIN PARA CENTROS POBLADOS ===============

@admin.register(CentrosPoblados)
class CentrosPobladosAdmin(admin.ModelAdmin):
    """Administración de Centros Poblados"""
    
    # Campos a mostrar en la lista
    list_display = [
        'cod_centro_poblado',
        'nom_centro_poblado',
        'get_municipio_nombre',
        'get_departamento_nombre',
        'area_oficial_ha'
    ]
    
    # Filtros laterales
    list_filter = [
        'cod_municipio__cod_depto',
        'cod_municipio'
    ]
    
    # Campos de búsqueda
    search_fields = [
        'cod_centro_poblado',
        'nom_centro_poblado',
        'cod_municipio__nom_municipio',
        'cod_municipio__cod_depto__nom_depto'
    ]
    
    # Organización en fieldsets
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'cod_centro_poblado',
                'nom_centro_poblado',
                'cod_municipio'
            )
        }),
        ('Características', {
            'fields': (
                'area_oficial_ha',
            )
        })
    )
    
    # Ordenamiento por defecto
    ordering = ['cod_municipio__nom_municipio', 'nom_centro_poblado']
    
    # Paginación
    list_per_page = 30
    
    # Métodos personalizados
    def get_municipio_nombre(self, obj):
        return obj.cod_municipio.nom_municipio if obj.cod_municipio else '-'
    get_municipio_nombre.short_description = 'Municipio'
    get_municipio_nombre.admin_order_field = 'cod_municipio__nom_municipio'
    
    def get_departamento_nombre(self, obj):
        return obj.cod_municipio.cod_depto.nom_depto if obj.cod_municipio and obj.cod_municipio.cod_depto else '-'
    get_departamento_nombre.short_description = 'Departamento'
    get_departamento_nombre.admin_order_field = 'cod_municipio__cod_depto__nom_depto'


    
# Registrar los modelos

admin.site.site_header = "Administración - Sistema de Gestión Catastral"
admin.site.site_title = "Admin Gestión Catastral"
admin.site.index_title = "Panel de Administración"

admin.site.register(PathDirPre, PathDirPreAdmin)
admin.site.register(PathDirPost, PathDirPostAdmin)


# Registrar los modelos
admin.site.register(Departamentos)
admin.site.register(Municipios, MunicipiosAdmin)
admin.site.register(Usuarios, UsuariosAdmin)
admin.site.register(TiposInsumos)
admin.site.register(Categorias)
admin.site.register(TiposFormato)
admin.site.register(Concepto)
admin.site.register(Entidades)
admin.site.register(DetalleInsumo, DetalleInsumoAdmin)
admin.site.register(Insumos, InsumosAdmin)
admin.site.register(ClasificacionInsumo, ClasificacionInsumoAdmin)
admin.site.register(MecanismoGeneral)
admin.site.register(MecanismoDetalle)
admin.site.register(AlcanceOperacion)
admin.site.register(Grupo)
admin.site.register(Notificaciones, NotificacionesAdmin)
admin.site.register(MecanismoOperacion)
admin.site.register(Zonas)