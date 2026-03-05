from django.contrib import admin

# Register your models here.
from .models import ScriptExecution, BackupFile

from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    PathDirOpera, PathDirTransv, DirectoriosOperacion, 
    DirectoriosTransv, ArchivosOperacion, ArchivosTransv
)

from django.contrib import admin
from django.utils.html import format_html


@admin.register(ScriptExecution)
class ScriptExecutionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'script_name', 'status', 'user', 
        'created_at', 'started_at', 'completed_at'
    ]
    list_filter = ['script_name', 'status', 'created_at']
    search_fields = ['user__username', 'error_message']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información General', {
            'fields': ('id', 'script_name', 'status', 'user')
        }),
        ('Tiempos', {
            'fields': ('created_at', 'updated_at', 'started_at', 'completed_at')
        }),
        ('Resultados', {
            'fields': ('output_file', 'output_log', 'error_message'),
            'classes': ('collapse',)
        }),
    )

@admin.register(BackupFile)
class BackupFileAdmin(admin.ModelAdmin):
    list_display = ['filename', 'execution', 'file_size_mb', 'created_at']
    list_filter = ['created_at', 'execution__status']
    search_fields = ['filename', 'execution__id']
    readonly_fields = ['file_size_mb']
    ordering = ['-created_at']
    
    def file_size_mb(self, obj):
        return f"{obj.file_size / (1024 * 1024):.2f} MB" if obj.file_size else "0 MB"
    file_size_mb.short_description = "Tamaño (MB)"



@admin.register(PathDirOpera)
class PathDirOperaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cod_municipio', 'path_corto', 'fecha_creacion']
    list_filter = ['cod_municipio', 'fecha_creacion']
    search_fields = ['path', 'cod_municipio']
    ordering = ['-fecha_creacion']
    
    def path_corto(self, obj):
        """Muestra una versión abreviada del path"""
        if len(obj.path) > 50:
            return f"{obj.path[:47]}..."
        return obj.path
    path_corto.short_description = 'Ruta'


@admin.register(PathDirTransv)
class PathDirTransvAdmin(admin.ModelAdmin):
    list_display = ['id', 'cod_municipio', 'path_corto', 'fecha_creacion']
    list_filter = ['cod_municipio', 'fecha_creacion']
    search_fields = ['path', 'cod_municipio']
    ordering = ['-fecha_creacion']
    
    def path_corto(self, obj):
        """Muestra una versión abreviada del path"""
        if len(obj.path) > 50:
            return f"{obj.path[:47]}..."
        return obj.path
    path_corto.short_description = 'Ruta'


@admin.register(DirectoriosOperacion)
class DirectoriosOperacionAdmin(admin.ModelAdmin):
    list_display = [
        'cod_dir_operacion', 'nombre_directorio', 'cod_municipio', 
        'nivel_profundidad', 'total_archivos', 'peso_mb', 'activo'
    ]
    list_filter = [
        'cod_municipio', 'nivel_profundidad', 'activo', 
        'fecha_creacion', 'usuario_propietario'
    ]
    search_fields = [
        'nombre_directorio', 'path_directorio', 'usuario_propietario'
    ]
    ordering = ['cod_municipio', 'nivel_profundidad', 'nombre_directorio']
    list_per_page = 25
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('cod_municipio', 'nombre_directorio', 'path_directorio')
        }),
        ('Jerarquía', {
            'fields': ('directorio_padre', 'nivel_profundidad')
        }),
        ('Estadísticas', {
            'fields': ('total_archivos', 'total_subdirectorios', 'peso_total_bytes')
        }),
        ('Metadatos', {
            'fields': (
                'usuario_propietario', 'fecha_creacion', 
                'fecha_ultima_modificacion', 'activo'
            )
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['fecha_registro', 'fecha_actualizacion']
    
    def peso_mb(self, obj):
        """Muestra el peso en MB"""
        if obj.peso_total_bytes:
            mb = obj.peso_total_bytes / (1024 * 1024)
            return f"{mb:.2f} MB"
        return "0 MB"
    peso_mb.short_description = 'Peso Total'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('directorio_padre')


@admin.register(DirectoriosTransv)
class DirectoriosTransvAdmin(admin.ModelAdmin):
    list_display = [
        'cod_dir_transv', 'nombre_directorio', 'cod_municipio',
        'nivel_jerarquia', 'total_archivos', 'peso_mb', 'activo'
    ]
    list_filter = [
        'cod_municipio', 'nivel_jerarquia', 'activo',
        'fecha_creacion', 'fecha_ultimo_escaneo'
    ]
    search_fields = ['nombre_directorio', 'ruta_completa']
    ordering = ['cod_municipio', 'nivel_jerarquia', 'nombre_directorio']
    list_per_page = 25
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('cod_municipio', 'nombre_directorio')
        }),
        ('Rutas', {
            'fields': ('ruta_completa', 'ruta_relativa')
        }),
        ('Jerarquía', {
            'fields': ('directorio_padre', 'nivel_jerarquia')
        }),
        ('Estadísticas', {
            'fields': ('total_archivos', 'total_subdirectorios', 'peso_total_bytes')
        }),
        ('Fechas', {
            'fields': (
                'fecha_creacion', 'fecha_actualizacion', 
                'fecha_ultimo_escaneo'
            )
        }),
        ('Estado y Metadatos', {
            'fields': ('activo', 'metadatos')
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        })
    )
    
    def peso_mb(self, obj):
        """Muestra el peso en MB"""
        if obj.peso_total_bytes:
            mb = obj.peso_total_bytes / (1024 * 1024)
            return f"{mb:.2f} MB"
        return "0 MB"
    peso_mb.short_description = 'Peso Total'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('directorio_padre')


class ArchivosOperacionInline(admin.TabularInline):
    model = ArchivosOperacion
    extra = 0
    fields = ['nombre_archivo', 'extension', 'peso_memoria', 'tipo_archivo', 'activo']
    readonly_fields = ['fecha_registro', 'fecha_actualizacion']


class ArchivosTransvInline(admin.TabularInline):
    model = ArchivosTransv
    extra = 0
    fields = ['nombre_archivo', 'extension', 'peso_memoria', 'es_directorio_especial', 'activo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(ArchivosOperacion)
class ArchivosOperacionAdmin(admin.ModelAdmin):
    list_display = [
        'id_archivo_operacion', 'nombre_archivo', 'extension',
        'directorio_link', 'municipio_codigo', 'peso_mb', 'activo'
    ]
    list_filter = [
        'extension', 'tipo_archivo', 'activo', 'fecha_registro',
        'cod_dir_operacion__cod_municipio'
    ]
    search_fields = [
        'nombre_archivo', 'path_file', 'usuario_windows', 'hash_archivo'
    ]
    ordering = ['-fecha_registro']
    list_per_page = 30
    
    fieldsets = (
        ('Información del Archivo', {
            'fields': (
                'nombre_archivo', 'path_file', 'extension', 'tipo_archivo'
            )
        }),
        ('Ubicación', {
            'fields': ('cod_dir_operacion',)
        }),
        ('Propiedades', {
            'fields': (
                'peso_memoria', 'hash_archivo', 'fecha_disposicion', 
                'usuario_windows'
            )
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['fecha_registro', 'fecha_actualizacion']
    
    def directorio_link(self, obj):
        """Link al directorio padre"""
        if obj.cod_dir_operacion:
            url = reverse('admin:directorios_directoriosoperacion_change', 
                         args=[obj.cod_dir_operacion.cod_dir_operacion])
            return format_html('<a href="{}">{}</a>', 
                             url, obj.cod_dir_operacion.nombre_directorio)
        return '-'
    directorio_link.short_description = 'Directorio'
    
    def municipio_codigo(self, obj):
        """Código del municipio"""
        if obj.cod_dir_operacion:
            return obj.cod_dir_operacion.cod_municipio
        return '-'
    municipio_codigo.short_description = 'Municipio'
    
    def peso_mb(self, obj):
        """Muestra el peso en MB"""
        return f"{obj.peso_memoria_mb} MB"
    peso_mb.short_description = 'Peso'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cod_dir_operacion')


@admin.register(ArchivosTransv)
class ArchivosTransvAdmin(admin.ModelAdmin):
    list_display = [
        'id_archivo_transv', 'nombre_archivo', 'extension',
        'directorio_link', 'municipio_codigo', 'peso_mb', 
        'es_directorio_especial', 'activo'
    ]
    list_filter = [
        'extension', 'es_directorio_especial', 'activo', 
        'fecha_creacion', 'cod_dir_transv__cod_municipio'
    ]
    search_fields = [
        'nombre_archivo', 'path_file', 'usuario_windows'
    ]
    ordering = ['-fecha_creacion']
    list_per_page = 30
    
    fieldsets = (
        ('Información del Archivo', {
            'fields': ('nombre_archivo', 'path_file', 'extension')
        }),
        ('Ubicación', {
            'fields': ('cod_dir_transv',)
        }),
        ('Propiedades', {
            'fields': (
                'peso_memoria', 'fecha_disposicion', 'usuario_windows',
                'es_directorio_especial'
            )
        }),
        ('Fechas', {
            'fields': (
                'fecha_creacion', 'fecha_actualizacion', 
                'fecha_ultimo_escaneo'
            )
        }),
        ('Estado y Metadatos', {
            'fields': ('activo', 'metadatos')
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        })
    )
    
    def directorio_link(self, obj):
        """Link al directorio padre"""
        if obj.cod_dir_transv:
            url = reverse('admin:directorios_directoriotransv_change', 
                         args=[obj.cod_dir_transv.cod_dir_transv])
            return format_html('<a href="{}">{}</a>', 
                             url, obj.cod_dir_transv.nombre_directorio)
        return '-'
    directorio_link.short_description = 'Directorio'
    
    def municipio_codigo(self, obj):
        """Código del municipio"""
        if obj.cod_dir_transv:
            return obj.cod_dir_transv.cod_municipio
        return '-'
    municipio_codigo.short_description = 'Municipio'
    
    def peso_mb(self, obj):
        """Muestra el peso en MB"""
        return f"{obj.peso_memoria_mb} MB"
    peso_mb.short_description = 'Peso'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cod_dir_transv')


# Agregar inlines a los admins de directorios
DirectoriosOperacionAdmin.inlines = [ArchivosOperacionInline]
DirectoriosTransvAdmin.inlines = [ArchivosTransvInline]


# Personalización del título del admin
admin.site.site_header = "Administración de Directorios y Archivos"
admin.site.site_title = "Admin Directorios"
admin.site.index_title = "Gestión de Directorios y Archivos"

