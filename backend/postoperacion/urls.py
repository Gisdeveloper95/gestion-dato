# postoperacion/urls.py - VERSIÓN CORREGIDA

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import archivo_views
from . import pdf_views
from .views import (
    HistorialPropietariosViewSet, CalificacionInfoPostViewSet,
    calificacion_completa, inicializar_calificaciones, EvaluacionArchivosPostViewSet
)

# Crear un router para ViewSets
router = DefaultRouter()
router.register(r'componentes', views.ComponentesPostViewSet)
router.register(r'disposiciones', views.DisposicionPostViewSet)
router.register(r'archivos', views.ArchivosPostViewSet)
router.register(r'rutas', views.PathDirPostViewSet)
router.register(r'notificaciones', views.NotificacionesPostViewSet, basename='notificaciones_post')
router.register(r'historial-propietarios', HistorialPropietariosViewSet, basename='historial-propietarios')
router.register(r'calificaciones-post', CalificacionInfoPostViewSet)
router.register(r'evaluacion-archivos', EvaluacionArchivosPostViewSet, basename='evaluacion-archivos-post')

urlpatterns = [
    # Incluir rutas del router
    path('', include(router.urls)),
    
    # ===============================================
    # 🚀 ENDPOINTS PRINCIPALES
    # ===============================================
    
    # Test básico
    path('test/', views.test_post, name='test_post'),
    
    # Reportes principales
    path('generar-reportes/', views.generar_reportes_postoperacion, name='generar_reportes_postoperacion'),
    path('reportes/excel/', views.generar_reportes_postoperacion, name='generar_reportes_excel'),
    
    # Estadísticas
    path('estadisticas/', views.estadisticas_post, name='estadisticas_post'),
    path('estadisticas-generales/', views.estadisticas_generales_post, name='estadisticas_generales_post'),
    path('reporte-consolidado/', views.reporte_consolidado_post, name='reporte_consolidado_post'),

    # Mecanismos de financiación por municipio
    path('mecanismos/<str:municipio_id>/', views.mecanismos_municipio, name='mecanismos_municipio'),
    
    # Validación
    path('validacion/directorios/', views.validar_directorios_post, name='validar_directorios_post'),
    
    # ===============================================
    # 🔧 ENDPOINTS DE ADMINISTRACIÓN
    # ===============================================
    
    # Health check
    path('health-check/', views.health_check_post, name='health_check_post'),
    
    # Migración y limpieza
    path('migrar-datos/', views.migrar_datos_post, name='migrar_datos_post'),
    path('limpiar-duplicados/', views.limpiar_duplicados_post, name='limpiar_duplicados_post'),
    
    # ===============================================
    # 📊 ENDPOINTS ESPECÍFICOS DE VIEWSETS
    # ===============================================
    
    # Endpoints específicos para disposiciones
    path('municipios-con-productos/', views.DisposicionPostViewSet.as_view({'get': 'municipios_con_productos'}), name='municipios-con-productos'),
    path('disposiciones/por-municipio/', views.DisposicionPostViewSet.as_view({'get': 'por_municipio'}), name='disposiciones-por-municipio'),
    path('disposiciones/resumen-estado/', views.DisposicionPostViewSet.as_view({'get': 'resumen_estado'}), name='disposiciones-resumen-estado'),
    path('disposiciones/directorios-por-municipio/', views.DisposicionPostViewSet.as_view({'get': 'directorios_por_municipio'}), name='disposiciones-directorios-por-municipio'),
    
    # Endpoints específicos para archivos
    path('archivos/por-municipio/', views.ArchivosPostViewSet.as_view({'get': 'por_municipio'}), name='archivos-por-municipio'),
    path('archivos/por-directorio/', views.ArchivosPostViewSet.as_view({'get': 'por_directorio'}), name='archivos-por-directorio'),
    
    # Endpoints específicos para notificaciones
    path('notificaciones/no-leidas/', views.NotificacionesPostViewSet.as_view({'get': 'no_leidas'}), name='notificaciones-no-leidas'),
    path('notificaciones/resumen/', views.NotificacionesPostViewSet.as_view({'get': 'resumen'}), name='notificaciones-resumen'),

    # ===============================================
    # 📥 ENDPOINTS DE DESCARGA DE ARCHIVOS
    # ===============================================

    path('descargar_archivo/', archivo_views.descargar_archivo, name='descargar_archivo_post'),
    path('verificar_archivo/', archivo_views.verificar_archivo, name='verificar_archivo_post'),
    path('preview_descarga/', archivo_views.preview_descarga, name='preview_descarga_post'),

    # ===============================================
    # 📤 ENDPOINT DE SUBIDA DE ARCHIVOS
    # ===============================================
    path('subir_archivo/', archivo_views.subir_archivo, name='subir_archivo_post'),

    # ===============================================
    # 📋 ENDPOINT DE AUDITORÍA DE ARCHIVOS
    # ===============================================
    path('historial_archivo/', archivo_views.historial_archivo, name='historial_archivo_post'),
    path('exportar_auditoria_csv/<int:municipio_id>/', archivo_views.exportar_auditoria_csv, name='exportar_auditoria_csv'),

    # Endpoints para visualización de PDFs y archivos
    path('verificar_pdf/', pdf_views.verificar_pdf, name='verificar_pdf_post'),
    path('ver_pdf/', pdf_views.ver_pdf, name='ver_pdf_post'),

    # Endpoints específicos para historial propietarios
    path('historial-propietarios/por-archivo/', views.HistorialPropietariosViewSet.as_view({'get': 'por_archivo'}), name='historial-por-archivo'),
    path('historial-propietarios/por-usuario/', views.HistorialPropietariosViewSet.as_view({'get': 'por_usuario'}), name='historial-por-usuario'),
    path('historial-propietarios/estadisticas/', views.HistorialPropietariosViewSet.as_view({'get': 'estadisticas'}), name='historial-estadisticas'),
    path('historial-propietarios/test/', views.HistorialPropietariosViewSet.as_view({'get': 'test'}), name='historial-test'),
    
    # ===============================================
    # 📋 ENDPOINTS DE CALIFICACIONES
    # ===============================================
    
    # Calificaciones básicas
    path('calificaciones-post/valor-completo/', calificacion_completa, name='calificacion_completa'),
    path('calificaciones-post/inicializar/', inicializar_calificaciones, name='inicializar_calificaciones'),
    path('calificacion-completa/', views.calificacion_completa, name='calificacion_completa_alt'),
    path('inicializar-calificaciones/', views.inicializar_calificaciones, name='inicializar_calificaciones_alt'),
    
    # Endpoints específicos de calificaciones
    path('calificaciones-post/estadisticas/', CalificacionInfoPostViewSet.as_view({'get': 'estadisticas'}), name='calificaciones-estadisticas'),
    path('calificaciones-post/niveles-calidad/', CalificacionInfoPostViewSet.as_view({'get': 'niveles_calidad'}), name='calificaciones-niveles-calidad'),
    path('calificaciones-post/buscar-por-valor/', CalificacionInfoPostViewSet.as_view({'get': 'buscar_por_valor'}), name='calificaciones-buscar-por-valor'),
    
    # ===============================================
    # 📊 ENDPOINTS DE EVALUACIONES
    # ===============================================
    
    # Estadísticas de evaluación
    path('evaluacion-archivos/estadisticas/', 
         EvaluacionArchivosPostViewSet.as_view({'get': 'estadisticas'}), 
         name='evaluacion-archivos-estadisticas'),
    
    # Evaluaciones por criterios
    path('evaluacion-archivos/por-municipio/', 
         EvaluacionArchivosPostViewSet.as_view({'get': 'por_municipio'}), 
         name='evaluacion-archivos-por-municipio'),
    
    path('evaluacion-archivos/por-directorio/', 
         EvaluacionArchivosPostViewSet.as_view({'get': 'por_directorio'}), 
         name='evaluacion-archivos-por-directorio'),
    
    path('evaluacion-archivos/por-estado/', 
         EvaluacionArchivosPostViewSet.as_view({'get': 'por_estado'}), 
         name='evaluacion-archivos-por-estado'),
    
    # Evaluaciones pendientes
    path('evaluacion-archivos/pendientes/', 
         EvaluacionArchivosPostViewSet.as_view({'get': 'pendientes'}), 
         name='evaluacion-archivos-pendientes'),
    
    # Resumen del usuario actual
    path('evaluacion-archivos/resumen-usuario/', 
         EvaluacionArchivosPostViewSet.as_view({'get': 'resumen_usuario'}), 
         name='evaluacion-archivos-resumen-usuario'),
    
    # ===============================================
    # ⚡ ACCIONES DE EVALUACIÓN
    # ===============================================
    
    # Acciones individuales
    path('evaluacion-archivos/<int:pk>/aprobar/', 
         EvaluacionArchivosPostViewSet.as_view({'post': 'aprobar'}), 
         name='evaluacion-archivos-aprobar'),
    
    path('evaluacion-archivos/<int:pk>/rechazar/', 
         EvaluacionArchivosPostViewSet.as_view({'post': 'rechazar'}), 
         name='evaluacion-archivos-rechazar'),
    
    path('evaluacion-archivos/<int:pk>/marcar-en-revision/', 
         EvaluacionArchivosPostViewSet.as_view({'post': 'marcar_en_revision'}), 
         name='evaluacion-archivos-marcar-revision'),
    
    # Acciones masivas
    path('evaluacion-archivos/aprobar-masivo/', 
         EvaluacionArchivosPostViewSet.as_view({'post': 'aprobar_masivo'}), 
         name='evaluacion-archivos-aprobar-masivo'),
    
    # ===============================================
    # 🔄 RUTAS DE COMPATIBILIDAD
    # ===============================================
    
    # Para mantener compatibilidad con frontend existente
    path('estadisticas-old/', views.estadisticas_post, name='estadisticas_old'),
    path('reporte-consolidado-old/', views.reporte_consolidado_post, name='reporte_consolidado_old'),
    
    # Aliases adicionales
    path('test-post/', views.test_post, name='test_post_alias'),
    path('reportes/', views.generar_reportes_postoperacion, name='reportes_alias'),





    path('evaluacion-datos/<int:municipio_id>/', 
     views.obtener_datos_evaluacion_municipio, 
     name='obtener_datos_evaluacion_municipio'),

     # Actualizar evaluación individual
     path('evaluacion-actualizar/<int:evaluacion_id>/', 
          views.actualizar_evaluacion_archivo, 
          name='actualizar_evaluacion_archivo'),

     # Eliminar evaluación individual
     path('evaluacion-eliminar/<int:evaluacion_id>/', 
          views.eliminar_evaluacion_archivo, 
          name='eliminar_evaluacion_archivo'),
]