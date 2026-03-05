from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .transversal_views import TransversalArbolCombinadoViewSet
from .operacion_views import OperacionArbolCombinadoViewSet

router = DefaultRouter()
router.register(r'executions', views.ScriptExecutionViewSet)
# Registrar ViewSets para rutas de directorios
router.register(r'path-opera', views.PathDirOperaViewSet, basename='path-dir-opera')
router.register(r'path-post', views.PathDirTransvViewSet, basename='path-dir-post')

# Registrar ViewSets para directorios
router.register(r'directorios-operacion', views.DirectoriosOperacionViewSet, basename='directorios-operacion')
router.register(r'directorios-transversales', views.DirectoriosTransvViewSet, basename='directorios-transversales')

# Registrar ViewSets para archivos
router.register(r'archivos-operacion', views.ArchivosOperacionViewSet, basename='archivos-operacion')
router.register(r'archivos-transversales', views.ArchivosTransvViewSet, basename='archivos-transversales')

# Transversal árbol combinado (similar a preoperacion-arbol)
router.register(r'transversal-arbol', TransversalArbolCombinadoViewSet, basename='transversal-arbol')

# Operación árbol combinado (similar a productos)
router.register(r'operacion-arbol', OperacionArbolCombinadoViewSet, basename='operacion-arbol')


urlpatterns = [
    # Router URLs
    path('api/', include(router.urls)),
    
    # Backup específico
    path('api/backup/status/', views.backup_status, name='backup_status'),
    path('api/backup/execute/', views.execute_backup, name='execute_backup'),
    path('api/backup/download-zip/', views.download_latest_backup_zip, name='download_backup_zip'),
    path('api/backup/files/', views.list_backup_files, name='list_backup_files'),
    path('api/backup/files/<int:file_id>/download/', views.download_backup_file, name='download_backup_file'),
    path('api/backup/clean/', views.clean_backup_directory, name='clean_backup_directory'),
        # Estadísticas generales
    path('api/estadisticas/generales/', views.estadisticas_generales, name='estadisticas-generales'),
    path('api/estadisticas/municipio/', views.resumen_por_municipio, name='resumen-municipio'),
    
    # Búsqueda global
    path('api/busqueda/archivos/', views.busqueda_archivos, name='busqueda-archivos'),
    
    # ✅ NUEVO: Municipios asignados al usuario
    path('api/mis-municipios/', views.mis_municipios_asignados, name='mis-municipios'),
    #Reportes
    path('api/generar-reportes-operacion/', views.generar_reportes_operacion, name='generar-reportes-operacion'),
    path('api/generar-reportes-transversal/', views.generar_reportes_transversal, name='generar-reportes-transversal'),
    path('reportes/excel-definitivo/', views.excel_definitivo, name='excel_definitivo'),

    # Mecanismos de financiación por municipio
    path('api/mecanismos-operacion/<str:municipio_id>/', views.mecanismos_operacion_municipio, name='mecanismos_operacion_municipio'),
    path('api/mecanismos-transversal/<str:municipio_id>/', views.mecanismos_transversal_municipio, name='mecanismos_transversal_municipio'),

]