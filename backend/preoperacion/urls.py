from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .explorer_views import DirectoryExplorerView
from rest_framework.authtoken.views import obtain_auth_token
from . import pdf_views
from . import archivo_views
from . import report_views
from . import password_views

from .views import (
    VerifyTokenView, InfoAdministrativaViewSet, CentrosPobladosViewSet,
    DirectorioPreoperacionViewSet, ArchivoPreoperacionViewSet,  # Viewsets indexación pre-operación
    PreoperacionArbolCombinadoViewSet  # Vista árbol combinada
)
# Crear un router para ViewSets
router = DefaultRouter()
router.register(r'departamentos', views.DepartamentosViewSet)
router.register(r'municipios', views.MunicipiosViewSet)
# CAMBIO: Comentar la línea del router de usuarios para evitar conflictos
# router.register(r'usuarios', views.UsuariosViewSet)  # <-- COMENTAR ESTA LÍNEA
router.register(r'tipos-insumo', views.TiposInsumosViewSet)
router.register(r'categorias', views.CategoriasViewSet)

router.register(r'tipos-formato', views.TiposFormatoViewSet)
router.register(r'conceptos', views.ConceptoViewSet)
router.register(r'entidades', views.EntidadesViewSet)
router.register(r'detalles-insumo', views.DetalleInsumoViewSet)
router.register(r'insumos', views.InsumosViewSet)
router.register(r'clasificaciones', views.ClasificacionInsumoViewSet)
router.register(r'mecanismos-operacion', views.MecanismoOperacionViewSet)

# Nuevos endpoints para las tablas de dominio
router.register(r'mecanismos-general', views.MecanismoGeneralViewSet)
router.register(r'mecanismos-detalle', views.MecanismoDetalleViewSet)

router.register(r'alcances-operacion', views.AlcanceOperacionViewSet)
router.register(r'grupos', views.GrupoViewSet)
router.register(r'zonas', views.ZonasViewSet)
router.register(r'path-pre', views.PathDirPreViewSet)
router.register(r'archivos-pre', views.ListaArchivosPreViewSet)

router.register(r'roles-seguimiento', views.RolesSeguimientoViewSet)
router.register(r'territoriales', views.TerritorialesIgacViewSet)
router.register(r'profesionales-seguimiento', views.ProfesionalesSeguimientoViewSet)
router.register(r'profesional-territorial', views.ProfesionalTerritorialViewSet)
router.register(r'profesional-municipio', views.ProfesionalMunicipioViewSet)

router.register(r'estados-insumo', views.EstadosInsumoViewSet)

router.register(r'auditoria', views.AuditoriaViewSet)
router.register(r'notificaciones', views.NotificacionesViewSet, basename='notificaciones')

router.register(r'info-administrativa', InfoAdministrativaViewSet)
router.register(r'centros-poblados', CentrosPobladosViewSet)

# Nuevos viewsets para indexación pre-operación (excluyendo 07_insu)
router.register(r'directorios-preoperacion', DirectorioPreoperacionViewSet)
router.register(r'archivos-preoperacion', ArchivoPreoperacionViewSet)
router.register(r'preoperacion-arbol', PreoperacionArbolCombinadoViewSet, basename='preoperacion-arbol')
router.register(r'sub-clasificaciones-secundarias', views.SubClasificacionFuenteSecundariaViewSet)


urlpatterns = [
    # ✅ GESTIÓN DE USUARIOS (ANTES del router para tener prioridad)
    path('usuarios/crear/', views.crear_usuario, name='crear-usuario'),
    path('usuarios/listar/', views.listar_usuarios, name='listar-usuarios'),
    path('usuarios/<int:user_id>/', views.obtener_usuario, name='obtener-usuario'),
    path('usuarios/<int:user_id>/actualizar/', views.actualizar_usuario, name='actualizar-usuario'),
    path('usuarios/<int:user_id>/eliminar/', views.eliminar_usuario, name='eliminar-usuario'),
    path('usuarios/<int:user_id>/cambiar-password/', views.cambiar_password_usuario, name='cambiar-password-usuario'),
    path('usuarios/estadisticas/', views.estadisticas_usuarios, name='estadisticas-usuarios'),
    path('usuarios/me/', views.usuario_actual, name='usuario-actual'),
    
    # ✅ USUARIOS LEGACY (ViewSet con prefijo diferente para evitar conflictos)
    path('usuarios-legacy/', include([
        path('', views.UsuariosViewSet.as_view({'get': 'list', 'post': 'create'})),
        path('<int:pk>/', views.UsuariosViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
        path('<int:pk>/detalles/', views.UsuariosViewSet.as_view({'get': 'detalles'})),
    ])),

    # ✅ ASIGNACIONES MASIVAS (ANTES del router para tener prioridad)
    path('profesional-municipio/bulk/', views.asignacion_masiva_municipios, name='asignacion-masiva-municipios'),
    path('municipios-por-territorial/<str:territorial>/', views.municipios_por_territorial, name='municipios-por-territorial'),

    # Incluir rutas del router
    path('', include(router.urls)),
    
    # Autenticación
    path('token/', obtain_auth_token, name='api_token_auth'),
    path('register/', views.CreateUserView.as_view(), name='register'),

    # Recuperación de contraseña
    path('auth/request-password-reset/', password_views.request_password_reset, name='request-password-reset'),
    path('auth/confirm-password-reset/', password_views.confirm_password_reset, name='confirm-password-reset'),
    path('auth/validate-reset-token/', password_views.validate_reset_token, name='validate-reset-token'),

    # Endpoints personalizados para consultas específicas
    path('municipios/<int:municipio_id>/insumos/', views.InsumosByMunicipioView.as_view(), name='municipio-insumos'),
    path('insumos/<int:insumo_id>/clasificaciones/', views.ClasificacionesByInsumoView.as_view(), name='insumo-clasificaciones'),
    path('categorias/<int:categoria_id>/insumos/', views.InsumosByCategoriaView.as_view(), name='categoria-insumos'),
    path('tipos-insumo/<str:tipo_id>/insumos/', views.InsumosByTipoView.as_view(), name='tipo-insumos'),
    path('usuarios-legacy/<int:usuario_id>/detalles/', views.DetallesByUsuarioView.as_view(), name='usuario-detalles'),
    path('clasificaciones/<int:clasificacion_id>/detalles/', views.DetallesByClasificacionView.as_view(), name='clasificacion-detalles'),
    path('detalles-insumo/centro-poblado/<str:centro_poblado_id>/', views.DetalleInsumoViewSet.as_view({'get': 'por_centro_poblado'}), name='detalles-por-centro-poblado'),
    
    # Endpoints de estadísticas
    path('estadisticas/', views.estadisticas_generales, name='estadisticas'),
    path('estadisticas/municipios/', views.estadisticas_municipios, name='estadisticas-municipios'),
    path('estadisticas/insumos/', views.estadisticas_insumos, name='estadisticas-insumos'),
    path('estadisticas/detalles/', views.estadisticas_detalles, name='estadisticas-detalles'),
    
    #Endpoint para listar archivos Pre-operacion
    path('clasificaciones/<int:clasificacion_id>/archivos-pre/', views.ListaArchivosPreByClasificacionView.as_view(), name='clasificacion-archivos-pre'),

    # URLs de autenticación de DRF
    path('api-auth/', include('rest_framework.urls')),
    path('verify-token/', VerifyTokenView.as_view(), name='verify-token'),
    path('explorer/', DirectoryExplorerView.as_view(), name='directory-explorer'),

    #End point para Profesionales_apoyo
    path('territoriales/<str:territorial_id>/profesionales/', views.ProfesionalesByTerritorialView.as_view(), name='territorial-profesionales'),
    path('municipios/<int:municipio_id>/profesionales/', views.ProfesionalesByMunicipioView.as_view(), name='municipio-profesionales'),

    path('verificar_pdf/', pdf_views.verificar_pdf, name='verificar_pdf'),
    path('ver_pdf/', pdf_views.ver_pdf, name='ver_pdf'),
    
    #Para estadisticas
    path('usuario-actual/', views.usuario_actual, name='usuario-actual'),
    path('actualizar-perfil/', views.actualizar_perfil, name='actualizar-perfil'),
    path('cambiar-password/', views.cambiar_password, name='cambiar-password'),
    path('estadisticas/dashboard/', views.estadisticas_dashboard, name='estadisticas-dashboard'),

    #Para Notificaciones
    path('notificaciones/hoy/', views.NotificacionesViewSet.as_view({'get': 'hoy'}), name='notificaciones-hoy'),
    path('notificaciones/por-mes/', views.NotificacionesViewSet.as_view({'get': 'por_mes'}), name='notificaciones-por-mes'),
    path('notificaciones/resumen/', views.NotificacionesViewSet.as_view({'get': 'resumen'}), name='notificaciones-resumen'),
    path('notificaciones/no-leidas/', views.NotificacionesViewSet.as_view({'get': 'no_leidas'}), name='notificaciones-no-leidas'),
    
    path('archivos-pre/por-municipio/', views.ListaArchivosPreViewSet.as_view({'get': 'por_municipio'}), name='archivos-pre-por-municipio'),
    # Nuevos endpoints para manejo de archivos
    path('descargar_archivo/', archivo_views.descargar_archivo, name='descargar_archivo'),
    path('verificar_archivo/', archivo_views.verificar_archivo, name='verificar_archivo'),
    path('preview_descarga/', archivo_views.preview_descarga, name='preview_descarga'),
    # Descarga múltiple y de directorios
    path('descargar_multiples/', archivo_views.descargar_multiples, name='descargar_multiples'),
    path('descargar_directorio/', archivo_views.descargar_directorio, name='descargar_directorio'),

    path('generar-reportes/', views.generar_reportes_preoperacion, name='generar-reportes-preoperacion'),
    path('generar-reportes-completo/', views.generar_reporte_preoperacion_completo, name='generar-reportes-preoperacion-completo'),
    path('debug-datos-preo/', views.debug_datos_preoperacion, name='debug-datos-preo'),
    path('informe-usuarios-especificos/', views.generar_informe_usuarios_especificos, name='informe-usuarios-especificos'),
    path('debug-campos-archivos-post/', views.debug_campos_archivos_post, name='debug-campos-archivos-post'),

    # Mecanismos de financiación por municipio (preoperación)
    path('mecanismos-preoperacion/<str:municipio_id>/', views.mecanismos_preoperacion_municipio, name='mecanismos_preoperacion_municipio'),

    # Reportes Excel
    path('reportes/asignaciones-profesionales/', report_views.reporte_asignaciones_profesionales, name='reporte-asignaciones-profesionales'),

    # Endpoints para info administrativa y centros poblados
    path('info-administrativa/municipio/<int:municipio_id>/', 
         InfoAdministrativaViewSet.as_view({'get': 'por_municipio'}), name='info-administrativa-municipio'),
    
    path('centros-poblados/municipio/<int:municipio_id>/', 
         CentrosPobladosViewSet.as_view({'get': 'por_municipio'}), name='centros-poblados-municipio'),
    
    path('info-administrativa/departamento/<int:departamento_id>/', 
         InfoAdministrativaViewSet.as_view({'get': 'por_departamento'}),name='info-administrativa-departamento'),
    
    path('centros-poblados/departamento/<int:departamento_id>/', 
         CentrosPobladosViewSet.as_view({'get': 'por_departamento'}), name='centros-poblados-departamento'),
]