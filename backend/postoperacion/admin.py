from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from datetime import datetime
from .models import (
    ComponentesPost, DisposicionPost, ArchivosPost, 
    PathDirPost, NotificacionesPost, HistorialPropietarios,
    CalificacionInfoPost, EvaluacionArchivosPost
)

# ================================
# 🔄 ADMIN POST V2 - ACTUALIZADO
# ================================

class ArchivosPostInline(admin.TabularInline):
    """🔄 ACTUALIZADO - Inline para archivos POST V2"""
    model = ArchivosPost
    extra = 1
    fields = ('nombre_archivo', 'ruta_completa', 'fecha_disposicion', 'usuario_windows', 'peso_memoria')
    readonly_fields = ('fecha_disposicion',)

@admin.register(ComponentesPost)
class ComponentesPostAdmin(admin.ModelAdmin):
    """
    ⚠️ DEPRECATED - Mantenido solo para compatibilidad
    Ya no se usa en la nueva arquitectura POST V2
    """
    list_display = ('id_componente', 'nombre_componente', 'deprecated_warning')
    search_fields = ('nombre_componente',)
    ordering = ('id_componente',)
    
    def deprecated_warning(self, obj):
        return format_html(
            '<span style="color: #dc3545; font-weight: bold;">⚠️ DEPRECATED</span>'
        )
    deprecated_warning.short_description = "Estado"
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = 'Componentes Post (DEPRECATED - Solo Compatibilidad)'
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(DisposicionPost)
class DisposicionPostAdmin(admin.ModelAdmin):
    """🔄 ACTUALIZADO - Admin POST V2 sin componentes"""
    
    list_display = (
        'id_disposicion', 'cod_municipio', 'nombre_directorio_display', 
        'dispuesto', 'evaluado', 'aprobado', 'fecha_disposicion',
        'total_archivos_display', 'ruta_truncada_display'
    )
    
    list_filter = (
        'dispuesto', 'evaluado', 'aprobado', 
        'fecha_disposicion',
        'cod_municipio__cod_depto'
    )
    
    search_fields = (
        'cod_municipio__nom_municipio', 
        'ruta_acceso',
        'observaciones'
        # ❌ ELIMINADO: 'id_componente__nombre_componente'
    )
    
    ordering = ('id_disposicion',)
    inlines = [ArchivosPostInline]
    
    readonly_fields = ('id_disposicion', 'nivel_jerarquia_display', 'total_archivos_display')
    
    fieldsets = (
        ('🏛️ Información Principal', {
            'fields': ('id_disposicion', 'cod_municipio', 'ruta_acceso')
        }),
        ('📁 Información del Directorio', {
            'fields': ('nivel_jerarquia_display', 'total_archivos_display')
        }),
        ('📊 Estado de Disposición', {
            'fields': ('dispuesto', 'evaluado', 'aprobado', 'fecha_disposicion')
        }),
        ('📝 Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        })
    )
    
    # 🆕 MÉTODOS DISPLAY ACTUALIZADOS POST V2
    
    def nombre_directorio_display(self, obj):
        """Muestra el nombre del directorio extraído de la ruta"""
        nombre = obj.get_nombre_directorio()
        if len(nombre) > 30:
            return f"{nombre[:27]}..."
        return nombre
    nombre_directorio_display.short_description = "Directorio"
    nombre_directorio_display.admin_order_field = "ruta_acceso"
    
    def total_archivos_display(self, obj):
        """Muestra el total de archivos en este directorio"""
        total = obj.archivos_relacionados.count()
        if total > 0:
            return format_html(
                '<span style="color: #198754; font-weight: bold;">{} archivos</span>',
                total
            )
        return format_html('<span style="color: #6c757d;">Sin archivos</span>')
    total_archivos_display.short_description = "Total Archivos"
    
    def ruta_truncada_display(self, obj):
        """Muestra la ruta truncada para mejor visualización"""
        if obj.ruta_acceso:
            ruta = obj.ruta_acceso
            if len(ruta) > 50:
                return f"...{ruta[-47:]}"
            return ruta
        return "Sin ruta"
    ruta_truncada_display.short_description = "Ruta Acceso"
    ruta_truncada_display.admin_order_field = "ruta_acceso"
    
    def nivel_jerarquia_display(self, obj):
        """Muestra el nivel de jerarquía del directorio"""
        nivel = obj.get_nivel_jerarquia()
        return format_html(
            '<span style="background: #0d6efd; color: white; padding: 2px 6px; '
            'border-radius: 10px; font-size: 11px;">Nivel {}</span>',
            nivel
        )
    nivel_jerarquia_display.short_description = "Nivel Jerarquía"
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = 'Disposiciones POST V2 (Por Directorios)'
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(ArchivosPost)
class ArchivosPostAdmin(admin.ModelAdmin):
    """🔄 ACTUALIZADO - Admin para archivos POST V2"""
    
    list_display = (
        'id_archivo', 'nombre_archivo_truncado', 'municipio_display',
        'directorio_display', 'fecha_disposicion', 'usuario_windows',
        'peso_display'
    )
    
    list_filter = (
        'fecha_disposicion',
        'usuario_windows',
        'id_disposicion__cod_municipio__cod_depto',
        'id_disposicion__cod_municipio'
    )
    
    search_fields = (
        'nombre_archivo', 'ruta_completa', 'usuario_windows',
        'id_disposicion__cod_municipio__nom_municipio',
        'id_disposicion__ruta_acceso'
        # ❌ ELIMINADO: 'id_disposicion__id_componente__nombre_componente'
    )
    
    ordering = ('id_archivo',)
    
    readonly_fields = ('id_archivo', 'municipio_display', 'directorio_display')
    
    fieldsets = (
        ('📄 Información del Archivo', {
            'fields': ('id_archivo', 'nombre_archivo', 'ruta_completa')
        }),
        ('🔗 Relaciones', {
            'fields': ('id_disposicion', 'municipio_display', 'directorio_display')
        }),
        ('📊 Información Adicional', {
            'fields': ('fecha_disposicion', 'observacion', 'hash_contenido')
        }),
        ('👤 Información del Usuario', {
            'fields': ('usuario_windows', 'peso_memoria')
        })
    )
    
    def nombre_archivo_truncado(self, obj):
        """Muestra el nombre del archivo truncado"""
        if len(obj.nombre_archivo) > 40:
            return f"{obj.nombre_archivo[:37]}..."
        return obj.nombre_archivo
    nombre_archivo_truncado.short_description = "Archivo"
    nombre_archivo_truncado.admin_order_field = "nombre_archivo"
    
    def municipio_display(self, obj):
        """🔄 ACTUALIZADO - Muestra el municipio sin componente"""
        municipio = obj.get_municipio()
        if municipio:
            try:
                url = reverse('admin:preoperacion_municipios_change', args=[municipio.cod_municipio])
                return format_html(
                    '<a href="{}" target="_blank">{}</a>',
                    url,
                    municipio.nom_municipio
                )
            except:
                return municipio.nom_municipio
        return "Sin municipio"
    municipio_display.short_description = "Municipio"
    
    def directorio_display(self, obj):
        """🆕 NUEVO - Muestra el directorio contenedor"""
        if obj.id_disposicion:
            nombre_dir = obj.id_disposicion.get_nombre_directorio()
            try:
                url = reverse('admin:postoperacion_disposicionpost_change', args=[obj.id_disposicion.id_disposicion])
                return format_html(
                    '<a href="{}" target="_blank" title="{}">{}</a>',
                    url,
                    obj.id_disposicion.ruta_acceso,
                    nombre_dir[:25] + "..." if len(nombre_dir) > 25 else nombre_dir
                )
            except:
                return nombre_dir
        return "Sin directorio"
    directorio_display.short_description = "Directorio"
    
    def peso_display(self, obj):
        """Muestra el peso formateado"""
        if obj.peso_memoria:
            try:
                peso_bytes = int(obj.peso_memoria)
                if peso_bytes < 1024:
                    return f"{peso_bytes} B"
                elif peso_bytes < 1024*1024:
                    return f"{peso_bytes/1024:.1f} KB"
                elif peso_bytes < 1024*1024*1024:
                    return f"{peso_bytes/(1024*1024):.1f} MB"
                else:
                    return f"{peso_bytes/(1024*1024*1024):.1f} GB"
            except:
                return obj.peso_memoria
        return "N/A"
    peso_display.short_description = "Peso"

@admin.register(PathDirPost)
class PathDirPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'cod_municipio', 'path_truncado', 'fecha_creacion')
    list_filter = ('fecha_creacion', 'cod_municipio__cod_depto')
    search_fields = ('cod_municipio__nom_municipio', 'path')
    ordering = ('id',)
    
    def path_truncado(self, obj):
        if len(obj.path) > 60:
            return f"...{obj.path[-57:]}"
        return obj.path
    path_truncado.short_description = "Ruta"
    path_truncado.admin_order_field = "path"

@admin.register(NotificacionesPost)
class NotificacionesPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_entidad', 'id_entidad', 'accion', 'leido_display', 'fecha_cambio_display')
    list_filter = ('tipo_entidad', 'accion', 'leido', 'fecha_cambio')
    search_fields = ('descripcion', 'tipo_entidad', 'accion')
    ordering = ('-fecha_cambio',)
    readonly_fields = ('id', 'fecha_cambio')
    
    def leido_display(self, obj):
        if obj.leido:
            return format_html('<span style="color: #198754;">✅ Leído</span>')
        return format_html('<span style="color: #dc3545;">❌ No Leído</span>')
    leido_display.short_description = "Estado"
    leido_display.admin_order_field = "leido"
    
    def fecha_cambio_display(self, obj):
        if obj.fecha_cambio:
            return obj.fecha_cambio.strftime('%d/%m/%Y %H:%M:%S')
        return "Sin fecha"
    fecha_cambio_display.short_description = "Fecha"
    fecha_cambio_display.admin_order_field = "fecha_cambio"

@admin.register(HistorialPropietarios)
class HistorialPropietariosAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_archivo', 'nombre_archivo_display', 'propietario_anterior', 
                    'propietario_nuevo', 'fecha_inicio', 'fecha_fin', 'estado_display')
    list_filter = ('tipo_archivo', 'fecha_inicio', ('fecha_fin', admin.EmptyFieldListFilter))
    search_fields = ('propietario_anterior', 'propietario_nuevo', 'detalles__nombre_archivo')
    date_hierarchy = 'fecha_inicio'
    
    def nombre_archivo_display(self, obj):
        if obj.detalles and 'nombre_archivo' in obj.detalles:
            return obj.detalles['nombre_archivo']
        return "Sin nombre"
    nombre_archivo_display.short_description = "Nombre del archivo"
    
    def estado_display(self, obj):
        return "Actual" if obj.fecha_fin is None else "Anterior"
    estado_display.short_description = "Estado"

@admin.register(CalificacionInfoPost)
class CalificacionInfoPostAdmin(admin.ModelAdmin):
    """Admin para CalificacionInfoPost"""
    
    list_display = [
        'concepto_truncado',
        'valor_display',
        'porcentaje_display',
        'nivel_calidad_display'
    ]
    
    list_filter = [
        'valor',
    ]
    
    search_fields = [
        'concepto',
    ]
    
    readonly_fields = [
        'porcentaje_display',
        'nivel_calidad_display'
    ]
    
    ordering = ['valor', 'concepto']
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('concepto', 'valor')
        }),
        ('Información Calculada', {
            'fields': ('porcentaje_display', 'nivel_calidad_display'),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 20
    list_max_show_all = 100
    save_on_top = True
    
    def concepto_truncado(self, obj):
        """Muestra el concepto truncado para mejor visualización"""
        if len(obj.concepto) > 50:
            return obj.concepto[:47] + "..."
        return obj.concepto
    concepto_truncado.short_description = "Concepto"
    concepto_truncado.admin_order_field = "concepto"
    
    def valor_display(self, obj):
        """Muestra el valor con formato mejorado"""
        return f"{float(obj.valor):.2f}"
    valor_display.short_description = "Valor"
    valor_display.admin_order_field = "valor"
    
    def porcentaje_display(self, obj):
        """Muestra el valor como porcentaje con color"""
        porcentaje = obj.get_porcentaje()
        
        # Determinar color según el porcentaje
        if porcentaje >= 90:
            color = "#28a745"  # Verde
        elif porcentaje >= 75:
            color = "#ffc107"  # Amarillo
        elif porcentaje >= 50:
            color = "#fd7e14"  # Naranja
        else:
            color = "#dc3545"  # Rojo
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color,
            porcentaje
        )
    porcentaje_display.short_description = "Porcentaje"
    
    def nivel_calidad_display(self, obj):
        """Muestra el nivel de calidad con badge"""
        nivel = obj.get_nivel_calidad()
        
        # Mapear colores según el nivel
        color_map = {
            'Sin información': '#6c757d',
            'Muy bajo': '#dc3545',
            'Bajo': '#fd7e14',
            'Medio': '#ffc107',
            'Alto': '#20c997',
            'Completo': '#28a745'
        }
        
        color = color_map.get(nivel, '#6c757d')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            nivel
        )
    nivel_calidad_display.short_description = "Nivel de Calidad"
    
    def has_delete_permission(self, request, obj=None):
        """Controla permisos de eliminación"""
        return request.user.is_superuser
    
    def save_model(self, request, obj, form, change):
        """Personaliza el guardado del modelo"""
        obj.concepto = obj.concepto.strip().upper()
        super().save_model(request, obj, form, change)

@admin.register(EvaluacionArchivosPost)
class EvaluacionArchivosPostAdmin(admin.ModelAdmin):
    """🔄 ACTUALIZADO - Admin para evaluaciones POST V2 sin componentes"""
    
    # 📋 CONFIGURACIÓN DE LISTADO ACTUALIZADA
    list_display = [
        'id_evaluacion',
        'nombre_archivo_truncado',
        'municipio_display',
        'directorio_display',  # ✅ Cambio: directorio en lugar de componente
        'estado_archivo_badge',
        'evaluacion_display',
        'usuario_evaluacion',
        'fecha_creacion_display',
        'acciones_rapidas'
    ]
    
    # 🔍 FILTROS ACTUALIZADOS SIN COMPONENTES
    list_filter = [
        'estado_archivo',
        'evaluacion_archivo',
        ('fecha_creacion', admin.DateFieldListFilter),
        ('fecha_actualizacion', admin.DateFieldListFilter),
        'id_disposicion__cod_municipio__cod_depto',
        'id_disposicion__cod_municipio',
        # ❌ ELIMINADO: 'id_disposicion__id_componente',
        'usuario_evaluacion'
    ]
    
    # 🔍 BÚSQUEDA ACTUALIZADA SIN COMPONENTES
    search_fields = [
        'nombre_archivo',
        'observaciones_evaluacion',
        'usuario_evaluacion',
        'id_disposicion__cod_municipio__nom_municipio',
        'id_disposicion__ruta_acceso',  # ✅ Cambio: ruta_acceso en lugar de componente
        'hash_contenido'
        # ❌ ELIMINADO: 'id_disposicion__id_componente__nombre_componente',
    ]
    
    readonly_fields = [
        'id_evaluacion',
        'id_archivo',
        'fecha_creacion',
        'fecha_actualizacion',
        'archivo_original_link',
        'porcentaje_evaluacion_display',
        'nivel_calidad_display'
    ]
    
    ordering = ['-fecha_creacion', 'estado_archivo']
    
    # 📊 CONFIGURACIÓN DE PAGINACIÓN
    list_per_page = 25
    list_max_show_all = 100
    
    # 🎨 CONFIGURACIÓN DE FORMULARIO ACTUALIZADA
    fieldsets = (
        ('📄 Información del Archivo', {
            'fields': (
                'id_evaluacion',
                'id_archivo',
                'archivo_original_link',
                'nombre_archivo',
                'ruta_completa'
            )
        }),
        ('🔗 Relaciones', {
            'fields': (
                'id_disposicion',
            )
        }),
        ('📊 Información Original', {
            'fields': (
                'fecha_disposicion',
                'observacion_original',
                'hash_contenido',
                'usuario_windows',
                'peso_memoria'
            ),
            'classes': ('collapse',)
        }),
        ('⭐ Evaluación', {
            'fields': (
                'evaluacion_archivo',
                'porcentaje_evaluacion_display',
                'nivel_calidad_display',
                'estado_archivo',
                'observaciones_evaluacion'
            )
        }),
        ('👤 Auditoría', {
            'fields': (
                'usuario_evaluacion',
                'fecha_creacion',
                'fecha_actualizacion'
            ),
            'classes': ('collapse',)
        })
    )
    
    # 🔍 MÉTODOS DE DISPLAY ACTUALIZADOS
    
    def nombre_archivo_truncado(self, obj):
        """Muestra el nombre del archivo truncado"""
        if len(obj.nombre_archivo) > 40:
            return f"{obj.nombre_archivo[:37]}..."
        return obj.nombre_archivo
    nombre_archivo_truncado.short_description = "Archivo"
    nombre_archivo_truncado.admin_order_field = "nombre_archivo"
    
    def municipio_display(self, obj):
        """Muestra el municipio con enlace"""
        if obj.id_disposicion and obj.id_disposicion.cod_municipio:
            municipio = obj.id_disposicion.cod_municipio
            try:
                url = reverse('admin:preoperacion_municipios_change', args=[municipio.cod_municipio])
                return format_html(
                    '<a href="{}" target="_blank" title="{}">{}</a>',
                    url,
                    municipio.nom_municipio,
                    municipio.nom_municipio[:25] + "..." if len(municipio.nom_municipio) > 25 else municipio.nom_municipio
                )
            except:
                return municipio.nom_municipio
        return "Sin municipio"
    municipio_display.short_description = "Municipio"
    municipio_display.admin_order_field = "id_disposicion__cod_municipio__nom_municipio"
    
    def directorio_display(self, obj):
        """🔄 ACTUALIZADO - Muestra el directorio en lugar del componente"""
        if obj.id_disposicion:
            nombre_dir = obj.id_disposicion.get_nombre_directorio()
            try:
                url = reverse('admin:postoperacion_disposicionpost_change', args=[obj.id_disposicion.id_disposicion])
                return format_html(
                    '<a href="{}" target="_blank" title="{}">{}</a>',
                    url,
                    obj.id_disposicion.ruta_acceso,
                    nombre_dir[:30] + "..." if len(nombre_dir) > 30 else nombre_dir
                )
            except:
                return nombre_dir
        return "Sin directorio"
    directorio_display.short_description = "Directorio"  # ✅ Cambio: Directorio en lugar de Componente
    directorio_display.admin_order_field = "id_disposicion__ruta_acceso"
    
    def estado_archivo_badge(self, obj):
        """Muestra el estado como badge con colores"""
        color_map = {
            'PENDIENTE': '#6c757d',
            'EN_REVISION': '#0d6efd',
            'APROBADO': '#198754',
            'RECHAZADO': '#dc3545',
            'REQUIERE_AJUSTES': '#fd7e14'
        }
        
        icon_map = {
            'PENDIENTE': '⏳',
            'EN_REVISION': '👀',
            'APROBADO': '✅',
            'RECHAZADO': '❌',
            'REQUIERE_AJUSTES': '🔧'
        }
        
        color = color_map.get(obj.estado_archivo, '#6c757d')
        icon = icon_map.get(obj.estado_archivo, '❓')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold; white-space: nowrap;">'
            '{} {}</span>',
            color,
            icon,
            obj.get_estado_archivo_display()
        )
    estado_archivo_badge.short_description = "Estado"
    estado_archivo_badge.admin_order_field = "estado_archivo"
    
    def evaluacion_display(self, obj):
        """Muestra la evaluación con porcentaje y color"""
        if obj.evaluacion_archivo:
            porcentaje = obj.get_porcentaje_evaluacion()
            nivel = obj.get_nivel_calidad()
            
            # Determinar color según el porcentaje
            if porcentaje >= 90:
                color = "#198754"  # Verde
            elif porcentaje >= 75:
                color = "#fd7e14"  # Naranja
            elif porcentaje >= 50:
                color = "#ffc107"  # Amarillo
            else:
                color = "#dc3545"  # Rojo
            
            return format_html(
                '<span style="color: {}; font-weight: bold;" title="{}">{:.1f}%</span><br>'
                '<small style="color: #6c757d;">{}</small>',
                color,
                nivel,
                porcentaje,
                nivel
            )
        return format_html('<span style="color: #6c757d;">Sin evaluar</span>')
    evaluacion_display.short_description = "Evaluación"
    evaluacion_display.admin_order_field = "evaluacion_archivo__valor"
    
    def fecha_creacion_display(self, obj):
        """Muestra la fecha de creación formateada"""
        if obj.fecha_creacion:
            # Mostrar tiempo relativo si es reciente
            ahora = datetime.now()
            if hasattr(obj.fecha_creacion, 'replace'):
                fecha = obj.fecha_creacion.replace(tzinfo=None) if obj.fecha_creacion.tzinfo else obj.fecha_creacion
            else:
                fecha = obj.fecha_creacion
            
            diferencia = ahora - fecha
            
            if diferencia.days == 0:
                if diferencia.seconds < 3600:
                    minutos = diferencia.seconds // 60
                    tiempo = f"Hace {minutos} min"
                else:
                    horas = diferencia.seconds // 3600
                    tiempo = f"Hace {horas}h"
                color = "#198754"
            elif diferencia.days == 1:
                tiempo = "Ayer"
                color = "#fd7e14"
            elif diferencia.days < 7:
                tiempo = f"Hace {diferencia.days} días"
                color = "#6c757d"
            else:
                tiempo = fecha.strftime('%d/%m/%Y')
                color = "#6c757d"
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span><br>'
                '<small style="color: #6c757d;">{}</small>',
                color,
                tiempo,
                fecha.strftime('%d/%m/%Y %H:%M')
            )
        return "Sin fecha"
    fecha_creacion_display.short_description = "Creado"
    fecha_creacion_display.admin_order_field = "fecha_creacion"
    
    def acciones_rapidas(self, obj):
        """Botones de acciones rápidas"""
        botones = []
        
        if obj.puede_ser_evaluado():
            # Botón aprobar
            botones.append(
                f'<a href="#" onclick="aprobarEvaluacion({obj.id_evaluacion})" '
                f'style="background: #198754; color: white; padding: 2px 6px; '
                f'border-radius: 3px; text-decoration: none; font-size: 10px; margin-right: 2px;">✅</a>'
            )
            
            # Botón rechazar
            botones.append(
                f'<a href="#" onclick="rechazarEvaluacion({obj.id_evaluacion})" '
                f'style="background: #dc3545; color: white; padding: 2px 6px; '
                f'border-radius: 3px; text-decoration: none; font-size: 10px; margin-right: 2px;">❌</a>'
            )
        
        # Botón ver archivo original
        if obj.id_archivo:
            try:
                archivo_original = obj.get_archivo_original()
                if archivo_original:
                    url = reverse('admin:postoperacion_archivospost_change', args=[archivo_original.id_archivo])
                    botones.append(
                        f'<a href="{url}" target="_blank" '
                        f'style="background: #0d6efd; color: white; padding: 2px 6px; '
                        f'border-radius: 3px; text-decoration: none; font-size: 10px;">📄</a>'
                    )
            except:
                pass
        
        return format_html(''.join(botones)) if botones else "N/A"
    acciones_rapidas.short_description = "Acciones"
    
    def archivo_original_link(self, obj):
        """Enlace al archivo original"""
        try:
            archivo_original = obj.get_archivo_original()
            if archivo_original:
                url = reverse('admin:postoperacion_archivospost_change', args=[archivo_original.id_archivo])
                return format_html(
                    '<a href="{}" target="_blank">📄 Ver Archivo Original (ID: {})</a>',
                    url,
                    archivo_original.id_archivo
                )
            return format_html('<span style="color: #dc3545;">❌ Archivo no encontrado</span>')
        except Exception as e:
            return format_html('<span style="color: #dc3545;">❌ Error: {}</span>', str(e))
    archivo_original_link.short_description = "Archivo Original"
    
    def porcentaje_evaluacion_display(self, obj):
        """Muestra el porcentaje de evaluación"""
        porcentaje = obj.get_porcentaje_evaluacion()
        
        if porcentaje >= 90:
            color = "#198754"
        elif porcentaje >= 75:
            color = "#fd7e14"
        elif porcentaje >= 50:
            color = "#ffc107"
        else:
            color = "#dc3545"
        
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 14px;">{:.1f}%</span>',
            color,
            porcentaje
        )
    porcentaje_evaluacion_display.short_description = "Porcentaje"
    
    def nivel_calidad_display(self, obj):
        """Muestra el nivel de calidad con badge"""
        nivel = obj.get_nivel_calidad()
        
        color_map = {
            'Sin información': '#6c757d',
            'Muy bajo': '#dc3545',
            'Bajo': '#fd7e14',
            'Medio': '#ffc107',
            'Alto': '#20c997',
            'Completo': '#198754'
        }
        
        color = color_map.get(nivel, '#6c757d')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            nivel
        )
    nivel_calidad_display.short_description = "Nivel de Calidad"
    
    # 🔧 MÉTODOS DE CONFIGURACIÓN
    
    def get_queryset(self, request):
        """🔄 ACTUALIZADO - Optimiza el queryset sin componentes"""
        return super().get_queryset(request).select_related(
            'id_disposicion',
            'id_disposicion__cod_municipio',
            'id_disposicion__cod_municipio__cod_depto',
            # ❌ ELIMINADO: 'id_disposicion__id_componente',
            'evaluacion_archivo'
        )
    
    def has_delete_permission(self, request, obj=None):
        """Controla permisos de eliminación - solo superusuarios"""
        return request.user.is_superuser
    
    def save_model(self, request, obj, form, change):
        """Personaliza el guardado del modelo"""
        if change:  # Si es una actualización
            obj.usuario_evaluacion = request.user.username
        super().save_model(request, obj, form, change)
    
    def changelist_view(self, request, extra_context=None):
        """🔄 ACTUALIZADO - Personaliza la vista de lista con estadísticas"""
        extra_context = extra_context or {}
        extra_context['title'] = 'Evaluaciones de Archivos POST V2'
        
        # Obtener estadísticas para mostrar en la parte superior
        try:
            stats = EvaluacionArchivosPost.get_estadisticas_evaluacion()
            extra_context['estadisticas_evaluacion'] = stats
        except:
            pass
        
        return super().changelist_view(request, extra_context=extra_context)
    
    # 🎨 MEDIA PARA JAVASCRIPT PERSONALIZADO
    class Media:
        js = ('admin/js/evaluacion_archivos_custom.js',)
        css = {
            'all': ('admin/css/evaluacion_archivos_custom.css',)
        }

# ===============================================
# 📋 RESUMEN ADMIN POST V2
# ===============================================

"""
✅ ADMIN.PY POST V2 - COMPLETAMENTE ACTUALIZADO

🔄 CAMBIOS PRINCIPALES:
❌ ELIMINADO: Todas las referencias a id_componente
❌ ELIMINADO: Filtros y búsquedas por componentes
❌ ELIMINADO: Métodos que dependían de componentes

✅ ACTUALIZADO: DisposicionPostAdmin sin componentes
✅ ACTUALIZADO: EvaluacionArchivosPostAdmin sin componentes
✅ NUEVO: Campos para directorios (nombre_directorio_display, directorio_display)
✅ NUEVO: Información de jerarquía de directorios
✅ NUEVO: Contadores de archivos por directorio
✅ MANTENIDO: ComponentesPostAdmin marcado como DEPRECATED

🎯 FUNCIONALIDADES MEJORADAS:
- Display de nombres de directorios extraídos de rutas
- Niveles de jerarquía de directorios
- Contadores de archivos por directorio
- Enlaces directos entre relacionados
- Búsquedas por ruta_acceso
- Filtros optimizados sin componentes
- Estadísticas en tiempo real
- Acciones rápidas para evaluaciones

🚀 BENEFICIOS:
- Admin interface 100% funcional con POST V2
- Sin errores de campos faltantes
- Mejor navegación entre entidades relacionadas
- Información más rica sobre directorios
- Rendimiento mejorado en consultas
"""