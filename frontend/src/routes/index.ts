import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/store/auth'

// ========================================
// IMPORTACIONES ESTÁTICAS (componentes básicos)
// ========================================
import Home from '@/pages/Home.vue'
import Login from '@/pages/Login.vue'
import NotFound from '@/pages/NotFound.vue'

// Recuperación de contraseña
const ForgotPassword = () => import('@/pages/ForgotPassword.vue')
const ResetPassword = () => import('@/pages/ResetPassword.vue')

// ========================================
// IMPORTACIONES DINÁMICAS (componentes de funcionalidades)
// ========================================

// Páginas principales
const EstadoProducto = () => import('@/pages/EstadoProducto.vue')
const Indicadores = () => import('@/pages/Indicadores.vue')
const Geoportal = () => import('@/pages/Geoportal.vue')
const MunicipioDetalle = () => import('@/pages/MunicipioDetalle.vue')
const Notificaciones = () => import('@/pages/Notificaciones.vue')
const Perfil = () => import('@/pages/Perfil.vue')

// ===== DISPOSICIÓN DE INFORMACIÓN (PÚBLICO) =====
const DisposicionDashboard = () => import('@/pages/disposicion/Dashboard.vue')
const DisposicionMunicipiosList = () => import('@/pages/disposicion/municipios/MunicipiosList.vue')

// Insumos disposición
const DisposicionInsumosList = () => import('@/pages/disposicion/insumos/InsumosList.vue')
const DisposicionInsumoDetalle = () => import('@/pages/disposicion/insumos/InsumoDetalle.vue')

// Productos disposición
const DisposicionProductosList = () => import('@/pages/disposicion/productos/ProductosList.vue')
const DisposicionProductosDetalle = () => import('@/pages/disposicion/productos/ProductosDetalle.vue')

// Profesionales disposición
const DisposicionProfesionalesList = () => import('@/pages/disposicion/profesionales/ProfesionalesList.vue')

// Reportes disposicion
const DisposicionReportesPreoperacion = () => import('@/pages/disposicion/reportes/ReportesPreoperacion.vue')
const DisposicionReportesPreoperacionCompleto = () => import('@/pages/disposicion/reportes/ReportesPreoperacionCompleto.vue')
const DisposicionReportesPostoperacion = () => import('@/pages/disposicion/reportes/ReportesPostoperacion.vue')
const DisposicionReportesOperacion = () => import('@/pages/disposicion/reportes/ReportesOperacion.vue')
const DisposicionReportesTransversales = () => import('@/pages/disposicion/reportes/ReportesTransversales.vue')

// Pre-operación disposición (árbol de directorios)
const DisposicionPreoperacionList = () => import('@/pages/disposicion/preoperacion/PreoperacionList.vue')
const DisposicionPreoperacionDetalle = () => import('@/pages/disposicion/preoperacion/PreoperacionDetalle.vue')

// Transversal disposición (árbol de directorios)
const DisposicionTransversalList = () => import('@/pages/disposicion/transversal/TransversalList.vue')
const DisposicionTransversalDetalle = () => import('@/pages/disposicion/transversal/TransversalDetalle.vue')

// Operación disposición (árbol de directorios)
const DisposicionOperacionList = () => import('@/pages/disposicion/operacion/OperacionList.vue')
const DisposicionOperacionDetalle = () => import('@/pages/disposicion/operacion/OperacionDetalle.vue')

// ===== GESTIÓN DE INFORMACIÓN (PROTEGIDO) =====
const GestionDashboard = () => import('@/pages/gestion/Dashboard.vue')
const GestionInicio = () => import('@/pages/gestion/inicio.vue')

// Auditoría
const HistorialAuditoria = () => import('@/pages/gestion/auditoria/HistorialAuditoria.vue')

// Municipios gestión
const GestionMunicipiosList = () => import('@/pages/gestion/municipios/MunicipiosList.vue')
const GestionMunicipioForm = () => import('@/pages/gestion/municipios/MunicipioForm.vue')
const GestionMunicipioDetalle = () => import('@/pages/gestion/municipios/MunicipioDetalle.vue')

// 🆕 CENTROS POBLADOS gestión
const CentrosPobList = () => import('@/pages/gestion/centros-poblados/CentrosPobList.vue')
const CentrosPobForm = () => import('@/pages/gestion/centros-poblados/CentrosPobForm.vue')
const CentrosPobDetalles = () => import('@/pages/gestion/centros-poblados/CentrosPobDetalles.vue')

// 🆕 INFORMACIÓN ADMINISTRATIVA gestión
const InfoAdminList = () => import('@/pages/gestion/info-administrativa/InfoAdminList.vue')
const InfoAdminForm = () => import('@/pages/gestion/info-administrativa/InfoAdminForm.vue')
const InfoAdminDetalles = () => import('@/pages/gestion/info-administrativa/InfoAdminDetalles.vue')

// Productos gestión
const GestionProductosList = () => import('@/pages/gestion/productos/ProductosList.vue')
const GestionProductosDetalle = () => import('@/pages/gestion/productos/ProductosDetalle.vue')

// Insumos gestión
const GestionInsumosList = () => import('@/pages/gestion/insumos/InsumosList.vue')
const GestionInsumoForm = () => import('@/pages/gestion/insumos/InsumoForm.vue')

// Clasificaciones gestión
const GestionClasificacionesList = () => import('@/pages/gestion/clasificaciones/ClasificacionesList.vue')
const GestionClasificacionForm = () => import('@/pages/gestion/clasificaciones/ClasificacionForm.vue')

// Detalles gestión
const GestionDetallesList = () => import('@/pages/gestion/detalles/DetallesList.vue')
const GestionDetalleForm = () => import('@/pages/gestion/detalles/DetalleForm.vue')

// Conceptos gestión
const GestionConceptosList = () => import('@/pages/gestion/conceptos/ConceptosList.vue')
const GestionConceptoForm = () => import('@/pages/gestion/conceptos/ConceptoForm.vue')

// Entidades y categorías gestión
// COMENTADO: Archivos vacíos eliminados
// const GestionEntidadesList = () => import('@/pages/gestion/entidades/EntidadesList.vue')
// const GestionCategoriasList = () => import('@/pages/gestion/categorias/CategoriasList.vue')

// Profesionales gestión
const GestionProfesionalesList = () => import('@/pages/gestion/profesionales/ProfesionalesList.vue')
const AsignacionesProfesionales = () => import('@/pages/gestion/profesionales/AsignacionesProfesionales.vue')
const AsignacionesMasivas = () => import('@/pages/gestion/profesionales/AsignacionesMasivas.vue')

// Reportes gestión
const ReportesPreoperacion = () => import('@/pages/gestion/reportes/ReportesPreoperacion.vue')
const ReportesPostoperacion = () => import('@/pages/gestion/reportes/ReportesPostoperacion.vue')

// ===== USUARIOS (DIFERENTES NIVELES) =====
// Lista básica de usuarios
const UsuariosList = () => import('@/pages/gestion/usuarios/UsuariosList.vue')

// Administración avanzada de usuarios
const UsuariosAdmin = () => import('@/pages/gestion/usuarios/UsuariosAdmin.vue')

// Formulario de usuarios
const UsuarioForm = () => import('@/pages/gestion/usuarios/UsuarioForm.vue')

// ===== GESTIÓN BASE DE DATOS =====
const DatabaseDashboard = () => import('@/pages/gestion/database/Dashboard.vue')

// Post-operación database
const PostOperacionDashboard = () => import('@/pages/gestion/database/postoperacion/Dashboard.vue')
const ArchivosPostOperacion = () => import('@/pages/gestion/database/postoperacion/ArchivosPostOperacion.vue')
const RutasPostOperacion = () => import('@/pages/gestion/database/postoperacion/RutasPostOperacion.vue')

// Pre-operación database
const PreOperacionDashboard = () => import('@/pages/gestion/database/preoperacion/Dashboard.vue')
const ArchivosPreOperacion = () => import('@/pages/gestion/database/preoperacion/ArchivosPreOperacion.vue')
const RutasPreOperacion = () => import('@/pages/gestion/database/preoperacion/RutasPreOperacion.vue')

// Dominios database
const DominiosDashboard = () => import('@/pages/gestion/database/dominios/DominiosDashboard.vue')
const AlcanceOperacion = () => import('@/pages/gestion/database/dominios/AlcanceOperacion.vue')
const CategoriasInsumos = () => import('@/pages/gestion/database/dominios/CategoriasInsumos.vue')
const ComponentesPostOperacion = () => import('@/pages/gestion/database/dominios/ComponentesPostOperacion.vue')
const EntidadesOperacion = () => import('@/pages/gestion/database/dominios/EntidadesOperacion.vue')
const EstadoInsumos = () => import('@/pages/gestion/database/dominios/EstadoInsumos.vue')
const GruposOperacion = () => import('@/pages/gestion/database/dominios/GruposOperacion.vue')
const MecanismoDetalle = () => import('@/pages/gestion/database/dominios/MecanismoDetalle.vue')
const MecanismoGeneral = () => import('@/pages/gestion/database/dominios/MecanismoGeneral.vue')
const MecanismoOperacion = () => import('@/pages/gestion/database/dominios/MecanismoOperacion.vue')
const RolesSeguimiento = () => import('@/pages/gestion/database/dominios/RolesSeguimiento.vue')
const TerritorialesIGAC = () => import('@/pages/gestion/database/dominios/TerritorialesIGAC.vue')
const TiposFormato = () => import('@/pages/gestion/database/dominios/TiposFormato.vue')
const TiposInsumos = () => import('@/pages/gestion/database/dominios/TiposInsumos.vue')
const ZonasOperacion = () => import('@/pages/gestion/database/dominios/ZonasOperacion.vue')

// Municipios database
const MunicipiosAdmin = () => import('@/pages/gestion/database/municipios/MunicipiosAdmin.vue')

// ===== ADMINISTRACIÓN DE SERVIDOR =====
const ServidorDashboard = () => import('@/pages/gestion/servidor/Dashboard.vue')
const GestionScripts = () => import('@/pages/gestion/servidor/GestionScripts.vue')
const GestionBackups = () => import('@/pages/gestion/servidor/GestionBackups.vue')

// ===== ADMINISTRACIÓN AVANZADA =====
// COMENTADO: Archivos vacíos eliminados
// const AdminDashboard = () => import('@/pages/admin/Dashboard.vue')
// const ComponentesAdmin = () => import('@/pages/admin/ComponentesAdmin.vue')
// const DisposicionesAdmin = () => import('@/pages/admin/DisposicionesAdmin.vue')

// ========================================
// DEFINICIÓN DE RUTAS
// ========================================
const routes: Array<RouteRecordRaw> = [
  // ============ RUTAS BÁSICAS ============
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: 'Inicio', requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: 'Iniciar Sesión', requiresAuth: false }
  },
  {
    path: '/recuperar-contrasena',
    name: 'ForgotPassword',
    component: ForgotPassword,
    meta: { title: 'Recuperar Contraseña', requiresAuth: false }
  },
  {
    path: '/restablecer-contrasena',
    name: 'ResetPassword',
    component: ResetPassword,
    meta: { title: 'Restablecer Contraseña', requiresAuth: false }
  },
  {
    path: '/notificaciones',
    name: 'Notificaciones',
    component: Notificaciones,
    meta: { title: 'Notificaciones', requiresAuth: false }
  },

  // ============ RUTAS INDEPENDIENTES ============

  {
    path: '/indicadores',
    name: 'Indicadores',
    component: Indicadores,
    meta: { title: 'Indicadores', requiresAuth: false }
  },
  {
    path: '/geoportal',
    name: 'Geoportal',
    component: Geoportal,
    meta: { title: 'Geoportal', requiresAuth: false }
  },
  {
    path: '/municipio/:id',
    name: 'MunicipioDetalle',
    component: MunicipioDetalle,
    props: true,
    meta: { title: 'Detalle de Municipio', requiresAuth: false }
  },
  {
    path: '/perfil',
    name: 'Perfil',
    component: Perfil,
    meta: { 
      title: 'Mi Perfil',
      requiresAuth: true
    }
  },

  // ============ DISPOSICIÓN DE INFORMACIÓN (PÚBLICO) ============
  {
    path: '/disposicion-informacion',
    name: 'DisposicionInformacion',
    component: DisposicionDashboard,
    meta: { 
      title: 'Disposición de Información', 
      requiresAuth: false 
    },
    redirect: '/disposicion-informacion/municipios',
    children: [
      // Municipios - Vista principal/inicial
      {
        path: 'municipios',
        name: 'DisposicionMunicipios',
        component: DisposicionMunicipiosList,
        meta: { title: 'Municipios', requiresAuth: false }
      },
      
      // Insumos
      {
        path: 'insumos',
        name: 'DisposicionInsumos',
        component: DisposicionInsumosList,
        meta: { title: 'Insumos', requiresAuth: false }
      },
      {
        path: 'insumos/:id',
        name: 'DisposicionInsumoDetalle',
        component: DisposicionInsumoDetalle,
        meta: { title: 'Detalle de Insumo', requiresAuth: false },
        props: true
      },
      
      // Productos
      {
        path: 'productos',
        name: 'DisposicionProductos',
        component: DisposicionProductosList,
        meta: { title: 'Productos', requiresAuth: false }
      },
      {
        path: 'productos/:id',
        name: 'DisposicionProductoDetalle',
        component: DisposicionProductosDetalle,
        meta: { title: 'Detalle de Producto', requiresAuth: false },
        props: true
      },
      
      // Profesionales
      {
        path: 'profesionales',
        name: 'DisposicionProfesionales',
        component: DisposicionProfesionalesList,
        meta: { title: 'Profesionales', requiresAuth: false }
      },

      // Pre-operación (árbol de directorios)
      {
        path: 'preoperacion',
        name: 'DisposicionPreoperacion',
        component: DisposicionPreoperacionList,
        meta: { title: 'Pre-Operación', requiresAuth: false }
      },
      {
        path: 'preoperacion/:id',
        name: 'DisposicionPreoperacionDetalle',
        component: DisposicionPreoperacionDetalle,
        meta: { title: 'Detalle Pre-Operación', requiresAuth: false },
        props: true
      },

      // Transversal (árbol de directorios)
      {
        path: 'transversal',
        name: 'DisposicionTransversal',
        component: DisposicionTransversalList,
        meta: { title: 'Transversal', requiresAuth: false }
      },
      {
        path: 'transversal/:id',
        name: 'DisposicionTransversalDetalle',
        component: DisposicionTransversalDetalle,
        meta: { title: 'Detalle Transversal', requiresAuth: false },
        props: true
      },

      // Operación (árbol de directorios)
      {
        path: 'operacion',
        name: 'DisposicionOperacion',
        component: DisposicionOperacionList,
        meta: { title: 'Operación', requiresAuth: false }
      },
      {
        path: 'operacion/:id',
        name: 'DisposicionOperacionDetalle',
        component: DisposicionOperacionDetalle,
        meta: { title: 'Detalle Operación', requiresAuth: false },
        props: true
      },

      // Reportes
      {
        path: 'reportes/insumos',
        name: 'DisposicionReportesInsumos',
        component: DisposicionReportesPreoperacion,
        meta: { title: 'Reportes de Insumos', requiresAuth: false }
      },
      {
        path: 'reportes/preoperacion-completo',
        name: 'DisposicionReportesPreoperacionCompleto',
        component: DisposicionReportesPreoperacionCompleto,
        meta: { title: 'Reportes Pre Operacion', requiresAuth: false }
      },
      {
        path: 'reportes/postoperacion',
        name: 'DisposicionReportesPostoperacion',
        component: DisposicionReportesPostoperacion,
        meta: { title: 'Reportes de Post-operacion', requiresAuth: false }
      },
      
      {
        path: 'reportes/operacion',
        name: 'DisposicionReportesOperacion',
        component: DisposicionReportesOperacion,
        meta: { title: 'Reportes de Operación', requiresAuth: false }
      },
      {
        path: 'reportes/transversales',
        name: 'DisposicionReportesTransversales',
        component: DisposicionReportesTransversales,
        meta: { title: 'Reportes Transversales', requiresAuth: false }
      },


    ]
  },

  // ============ GESTIÓN DE INFORMACIÓN (PROTEGIDO) ============
  {
    path: '/gestion-informacion',
    name: 'GestionInformacion',
    component: GestionDashboard,
    meta: { title: 'Gestión de Información', requiresAuth: true },
    redirect: '/gestion-informacion/inicio',
    children: [
      // Inicio
      {
        path: 'inicio',
        name: 'GestionInicio',
        component: GestionInicio,
        meta: { title: 'Panel de Gestión', requiresAuth: true }
      },

      // Auditoría
      {
        path: 'auditoria',
        name: 'Auditoria',
        component: HistorialAuditoria,
        meta: { title: 'Historial de Actividad', requiresAuth: true }
      },

      // ============ MUNICIPIOS ============
      {
        path: 'municipios',
        name: 'GestionMunicipios',
        component: GestionMunicipiosList,
        meta: { title: 'Gestión de Municipios', requiresAuth: true }
      },
      {
        path: 'municipios/crear',
        name: 'CrearMunicipio',
        component: GestionMunicipioForm,
        meta: { title: 'Crear Municipio', requiresAuth: true }
      },
      {
        path: 'municipios/:id/editar',
        name: 'EditarMunicipio',
        component: GestionMunicipioForm,
        meta: { title: 'Editar Municipio', requiresAuth: true },
        props: true
      },
      {
        path: 'municipios/:id',
        name: 'GestionMunicipioDetalle',
        component: GestionMunicipioDetalle,
        meta: { title: 'Detalle de Municipio', requiresAuth: true },
        props: true
      },

      // ============ 🆕 CENTROS POBLADOS ============
      {
        path: 'centros-poblados',
        name: 'GestionCentrosPoblados',
        component: CentrosPobList,
        meta: { 
          title: 'Gestión de Centros Poblados', 
          requiresAuth: true,
          parent: 'Gestión de Información',
          parentPath: '/gestion-informacion/inicio'
        }
      },
      {
        path: 'centros-poblados/crear',
        name: 'CrearCentroPoblado',
        component: CentrosPobForm,
        meta: { 
          title: 'Crear Centro Poblado', 
          requiresAuth: true,
          parent: 'Centros Poblados',
          parentPath: '/gestion-informacion/centros-poblados'
        }
      },
      {
        path: 'centros-poblados/:id/editar',
        name: 'EditarCentroPoblado',
        component: CentrosPobForm,
        meta: { 
          title: 'Editar Centro Poblado', 
          requiresAuth: true,
          parent: 'Centros Poblados',
          parentPath: '/gestion-informacion/centros-poblados'
        },
        props: true
      },
      {
        path: 'centros-poblados/:id',
        name: 'DetallesCentroPoblado',
        component: CentrosPobDetalles,
        meta: { 
          title: 'Detalles de Centro Poblado', 
          requiresAuth: true,
          parent: 'Centros Poblados',
          parentPath: '/gestion-informacion/centros-poblados'
        },
        props: true
      },

      // ============ 🆕 INFORMACIÓN ADMINISTRATIVA ============
      {
        path: 'info-administrativa',
        name: 'GestionInfoAdministrativa',
        component: InfoAdminList,
        meta: { 
          title: 'Gestión de Información Administrativa', 
          requiresAuth: true,
          parent: 'Gestión de Información',
          parentPath: '/gestion-informacion/inicio'
        }
      },
      {
        path: 'info-administrativa/crear',
        name: 'CrearInfoAdministrativa',
        component: InfoAdminForm,
        meta: { 
          title: 'Crear Información Administrativa', 
          requiresAuth: true,
          parent: 'Información Administrativa',
          parentPath: '/gestion-informacion/info-administrativa'
        }
      },
      {
        path: 'info-administrativa/:id/editar',
        name: 'EditarInfoAdministrativa',
        component: InfoAdminForm,
        meta: { 
          title: 'Editar Información Administrativa', 
          requiresAuth: true,
          parent: 'Información Administrativa',
          parentPath: '/gestion-informacion/info-administrativa'
        },
        props: true
      },
      {
        path: 'info-administrativa/:id',
        name: 'DetallesInfoAdministrativa',
        component: InfoAdminDetalles,
        meta: { 
          title: 'Detalles de Información Administrativa', 
          requiresAuth: true,
          parent: 'Información Administrativa',
          parentPath: '/gestion-informacion/info-administrativa'
        },
        props: true
      },

      // ============ PRODUCTOS ============
      {
        path: 'productos',
        name: 'GestionProductosList',
        component: GestionProductosList,
        meta: {
          title: 'Gestión de Productos',
          requiresAuth: true,
          parent: 'Gestión de Información',
          parentPath: '/gestion-informacion/inicio',
          breadcrumb: [
            { name: 'Inicio', path: '/' },
            { name: 'Gestión de Información', path: '/gestion-informacion/inicio' },
            { name: 'Productos', path: '/gestion-informacion/productos' }
          ]
        }
      },
      {
        path: 'productos/:id',
        name: 'GestionProductosDetalle',
        component: GestionProductosDetalle,
        meta: { 
          title: 'Detalle de Producto',
          requiresAuth: true,
          parent: 'Gestión de Productos',
          parentPath: '/gestion-informacion/productos'
        },
        props: true
      },

      // ============ INSUMOS ============
      {
        path: 'insumos',
        name: 'GestionInsumos',
        component: GestionInsumosList,
        meta: { title: 'Gestión de Insumos', requiresAuth: true }
      },
      {
        path: 'insumos/crear',
        name: 'CrearInsumo',
        component: GestionInsumoForm,
        meta: { title: 'Crear Insumo', requiresAuth: true }
      },
      {
        path: 'insumos/:id',
        name: 'EditarInsumo',
        component: GestionInsumoForm,
        meta: { title: 'Editar Insumo', requiresAuth: true },
        props: true
      },

      // ============ CLASIFICACIONES ============
      {
        path: 'clasificaciones',
        name: 'GestionClasificaciones',
        component: GestionClasificacionesList,
        meta: { title: 'Gestión de Clasificaciones', requiresAuth: true }
      },
      {
        path: 'clasificaciones/crear',
        name: 'CrearClasificacion',
        component: GestionClasificacionForm,
        meta: { title: 'Crear Clasificación', requiresAuth: true }
      },
      {
        path: 'clasificaciones/:id',
        name: 'EditarClasificacion',
        component: GestionClasificacionForm,
        meta: { title: 'Editar Clasificación', requiresAuth: true },
        props: true
      },

      // ============ DETALLES ============
      {
        path: 'detalles',
        name: 'GestionDetalles',
        component: GestionDetallesList,
        meta: { title: 'Gestión de Detalles de Insumo', requiresAuth: true }
      },
      {
        path: 'detalles/crear',
        name: 'CrearDetalle',
        component: GestionDetalleForm,
        meta: { title: 'Crear Detalle de Insumo', requiresAuth: true }
      },
      {
        path: 'detalles/:id',
        name: 'EditarDetalle',
        component: GestionDetalleForm,
        meta: { title: 'Editar Detalle de Insumo', requiresAuth: true },
        props: true
      },

      // ============ CONCEPTOS ============
      {
        path: 'conceptos',
        name: 'GestionConceptos',
        component: GestionConceptosList,
        meta: { title: 'Gestión de Conceptos', requiresAuth: true }
      },
      {
        path: 'conceptos/crear',
        name: 'CrearConcepto',
        component: GestionConceptoForm,
        meta: { title: 'Crear Concepto', requiresAuth: true }
      },
      {
        path: 'conceptos/:id',
        name: 'EditarConcepto',
        component: GestionConceptoForm,
        meta: { title: 'Editar Concepto', requiresAuth: true },
        props: true
      },

      // ============ ENTIDADES Y CATEGORÍAS ============
      // COMENTADO: Componentes vacíos eliminados
      // {
      //   path: 'entidades',
      //   name: 'GestionEntidades',
      //   component: GestionEntidadesList,
      //   meta: { title: 'Gestión de Entidades', requiresAuth: true }
      // },
      // {
      //   path: 'categorias',
      //   name: 'GestionCategorias',
      //   component: GestionCategoriasList,
      //   meta: { title: 'Gestión de Categorías', requiresAuth: true }
      // },

      // ============ USUARIOS BÁSICOS ============
      {
        path: 'usuarios',
        name: 'GestionUsuarios',
        component: UsuariosList,
        meta: { 
          title: 'Gestión de Usuarios', 
          requiresAuth: true, 
          requiresAdmin: true 
        }
      },

      // ============ PROFESIONALES ============
      {
        path: 'profesionales',
        name: 'GestionProfesionales',
        component: GestionProfesionalesList,
        meta: { title: 'Gestión de Profesionales', requiresAuth: true }
      },
      {
        path: 'profesionales/asignaciones',
        name: 'AsignacionesProfesionales',
        component: AsignacionesProfesionales,
        meta: { title: 'Asignaciones de Profesionales', requiresAuth: true }
      },
      {
        path: 'profesionales/asignaciones-masivas',
        name: 'AsignacionesMasivas',
        component: AsignacionesMasivas,
        meta: { title: 'Asignaciones Masivas', requiresAuth: true }
      },

      // ============ REPORTES ============
      {
        path: 'reportes/insumos',
        name: 'ReportesPreoperacion',
        component: ReportesPreoperacion,
        meta: { 
          title: 'Reportes de Preoperación',
          requiresAuth: true,
          requiresAdmin: true,
          parent: 'Gestión de Información',
          parentPath: '/gestion-informacion/inicio'
        }
      },
      {
        path: 'reportes/productos',
        name: 'ReportesPostoperacion',
        component: ReportesPostoperacion,
        meta: { 
          title: 'Reportes de Post-operación',
          requiresAuth: true,
          requiresAdmin: true,
          parent: 'Gestión de Información',
          parentPath: '/gestion-informacion/inicio'
        }
      },

      // ============ GESTIÓN BASE DE DATOS ============
      {
        path: 'database',
        name: 'DatabaseManagement',
        component: DatabaseDashboard,
        meta: { 
          title: 'Gestión Base de Datos',
          requiresAuth: true,
          requiresAdmin: true
        },
        children: [
          // ========== POST-OPERACIÓN ==========
          {
            path: 'postoperacion',
            name: 'PostOperacionRoot',
            component: PostOperacionDashboard,
            meta: { title: 'Post-operación', requiresAuth: true, requiresAdmin: true },
            children: [
              {
                path: '',
                name: 'PostOperacionDashboard',
                component: PostOperacionDashboard
              },
              {
                path: 'archivos',
                name: 'ArchivosPostOperacion',
                component: ArchivosPostOperacion,
                meta: { title: 'Archivos Post-operación', requiresAuth: true, requiresAdmin: true }
              },
              {
                path: 'rutas',
                name: 'RutasPostOperacion',
                component: RutasPostOperacion,
                meta: { title: 'Rutas POST', requiresAuth: true, requiresAdmin: true }
              }
            ]
          },

          // ========== PRE-OPERACIÓN ==========
          {
            path: 'preoperacion',
            name: 'PreOperacionRoot',
            component: PreOperacionDashboard,
            meta: { title: 'Pre-operación', requiresAuth: true, requiresAdmin: true },
            children: [
              {
                path: '',
                name: 'PreOperacionDashboard',
                component: PreOperacionDashboard
              },
              {
                path: 'archivos',
                name: 'ArchivosPreOperacion',
                component: ArchivosPreOperacion,
                meta: { title: 'Archivos Pre-operación', requiresAuth: true, requiresAdmin: true }
              },
              {
                path: 'rutas',
                name: 'RutasPreOperacion',
                component: RutasPreOperacion,
                meta: { title: 'Rutas PRE', requiresAuth: true, requiresAdmin: true }
              }
            ]
          },

          // ========== DASHBOARD PRINCIPAL DE DOMINIOS ==========
          {
            path: 'dominios',
            name: 'DominiosDashboard',
            component: DominiosDashboard,
            meta: { title: 'Gestión de Dominios', requiresAuth: true, requiresAdmin: true }
          },

          // ========== DOMINIOS ESPECÍFICOS ==========
          {
            path: 'dominios/alcance-operacion',
            name: 'AlcanceOperacion',
            component: AlcanceOperacion,
            meta: { title: 'Alcance de Operación', requiresAuth: true, requiresAdmin: true }
          },
          {
            path: 'dominios/categorias-insumos',
            name: 'CategoriasInsumos',
            component: CategoriasInsumos,
            meta: { title: 'Categorías de Insumos', requiresAuth: true, requiresAdmin: true }
          },
          {
            path: 'dominios/componentes-postoperacion',
            name: 'ComponentesPostOperacion',
            component: ComponentesPostOperacion,
            meta: { title: 'Componentes Post-operación', requiresAuth: true, requiresAdmin: true }
          },
          {
            path: 'dominios/entidades-operacion',
            name: 'EntidadesOperacion',
            component: EntidadesOperacion,
            meta: { title: 'Entidades de Operación', requiresAuth: true, requiresAdmin: true }
          },
          {
            path: 'dominios/estado-insumos',
            name: 'EstadoInsumos',
            component: EstadoInsumos,
            meta: { title: 'Estado de Insumos', requiresAuth: true, requiresAdmin: true }
          },
          {
            path: 'dominios/grupos-operacion',
            name: 'GruposOperacion',
            component: GruposOperacion,
            meta: { title: 'Grupos de Operación', requiresAuth: true, requiresAdmin: true }
          },
          {
            path: 'dominios/mecanismo-detalle',
            name: 'MecanismoDetalle',
            component: MecanismoDetalle,
            meta: { title: 'Mecanismo Detalle', requiresAuth: true, requiresAdmin: true }
          },
          {
            path: 'dominios/mecanismo-general',
            name: 'MecanismoGeneral',
            component: MecanismoGeneral,
            meta: { title: 'Mecanismo General', requiresAuth: true, requiresAdmin: true }
          },
          {
            path: 'dominios/mecanismo-operacion',
            name: 'MecanismoOperacion',
            component: MecanismoOperacion,
            meta: { title: 'Mecanismo de Operación', requiresAuth: true, requiresAdmin: true }
          },
          {
            path: 'dominios/roles-seguimiento',
            name: 'RolesSeguimiento',
            component: RolesSeguimiento,
            meta: { title: 'Roles de Seguimiento', requiresAuth: true, requiresAdmin: true }
          },
          {
            path: 'dominios/territoriales-igac',
            name: 'TerritorialesIGAC',
            component: TerritorialesIGAC,
            meta: { title: 'Territoriales IGAC', requiresAuth: true, requiresAdmin: true }
          },
          {
            path: 'dominios/tipos-formato',
            name: 'TiposFormato',
            component: TiposFormato,
            meta: { title: 'Tipos de Formato', requiresAuth: true, requiresAdmin: true }
          },
          {
            path: 'dominios/tipos-insumos',
            name: 'TiposInsumos',
            component: TiposInsumos,
            meta: { title: 'Tipos de Insumos', requiresAuth: true, requiresAdmin: true }
          },
          {
            path: 'dominios/zonas-operacion',
            name: 'ZonasOperacion',
            component: ZonasOperacion,
            meta: { title: 'Zonas de Operación', requiresAuth: true, requiresAdmin: true }
          },

          // ========== MUNICIPIOS ESPECIALES ==========
          {
            path: 'municipios',
            name: 'MunicipiosDatabase',
            component: MunicipiosAdmin,
            meta: { title: 'Administración de Municipios', requiresAuth: true, requiresAdmin: true }
          }
        ]
      },

      // ============ ADMINISTRACIÓN DE SERVIDOR ============
      {
        path: 'servidor',
        name: 'ServidorManagement', 
        component: ServidorDashboard,
        meta: { 
          title: 'Administración de Servidor',
          requiresAuth: true,
          requiresAdmin: true
        },
        children: [
          {
            path: '',
            name: 'ServidorDashboard',
            component: ServidorDashboard
          },
          {
            path: 'scripts',
            name: 'GestionScripts',
            component: GestionScripts,
            meta: { title: 'Gestión de Scripts', requiresAuth: true, requiresAdmin: true }
          },
          {
            path: 'backups',
            name: 'GestionBackups', 
            component: GestionBackups,
            meta: { title: 'Gestión de Backups', requiresAuth: true, requiresAdmin: true }
          }
        ]
      },

      // ============ GESTIÓN DE USUARIOS AMPLIADA ============
      {
        path: 'usuarios-admin',
        name: 'UsuariosAdminRoot',
        component: UsuariosAdmin,
        meta: { 
          title: 'Administración de Usuarios', 
          requiresAuth: true, 
          requiresAdmin: true 
        }
      },
      {
        path: 'usuarios-admin/nuevo',
        name: 'UsuarioNuevo',
        component: UsuarioForm,
        meta: { 
          title: 'Crear Usuario', 
          requiresAuth: true, 
          requiresAdmin: true 
        }
      },
      {
        path: 'usuarios-admin/:id/editar',
        name: 'UsuarioEditar',
        component: UsuarioForm,
        props: true,
        meta: { 
          title: 'Editar Usuario', 
          requiresAuth: true, 
          requiresAdmin: true 
        }
      }
    ]
  },
  
  // ============ RUTAS ADMINISTRATIVAS (protegidas) ============
  // COMENTADO: Componentes vacíos eliminados
  // {
  //   path: '/admin',
  //   name: 'Admin',
  //   component: AdminDashboard,
  //   meta: { title: 'Panel Administrativo', requiresAuth: true, requiresAdmin: true },
  //   children: [
  //     {
  //       path: 'componentes',
  //       name: 'AdminComponentes',
  //       component: ComponentesAdmin,
  //       meta: { title: 'Administración de Componentes', requiresAuth: true, requiresAdmin: true }
  //     },
  //     {
  //       path: 'disposiciones',
  //       name: 'AdminDisposiciones',
  //       component: DisposicionesAdmin,
  //       meta: { title: 'Administración de Disposiciones', requiresAuth: true, requiresAdmin: true }
  //     }
  //   ]
  // },

  // ============ RUTA PARA 404 ============
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { title: 'Página no encontrada', requiresAuth: false }
  }
]

// ========================================
// CREAR EL ROUTER
// ========================================
const router = createRouter({
  history: createWebHistory(),
  routes,
  // Scroll behavior mejorado
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth'
      }
    } else {
      return { top: 0, behavior: 'smooth' }
    }
  }
})

// ========================================
// NAVIGATION GUARDS
// ========================================
router.beforeEach(async (to, from, next) => {
  // Actualizar título de la página
  document.title = `${to.meta.title} | Sistema de Gestión de Datos` || 'Sistema de Gestión de Datos'
  
  // Verificar si la ruta requiere autenticación o permisos admin
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)
  const authStore = useAuthStore()
  
  // Para rutas que requieren autenticación
  if (requiresAuth) {
    // En desarrollo, ser más tolerante con la autenticación
    if (import.meta.env.DEV) {
      // Verificación básica: ¿hay token?
      const token = localStorage.getItem('token')
      if (!token) {
        console.warn('⚠️ No hay token, redirigiendo a login...')
        next('/login')
        return
      }
      
      // Para permisos de admin en desarrollo, ser permisivo
      if (requiresAdmin) {
        console.log('🔓 Modo desarrollo: permitiendo acceso admin')
      }
      
      next()
      return
    }
    
    // En producción, verificar autenticación completa
    try {
      if (!authStore.isAuthenticated) {
        await authStore.checkAuth()
      }
      
      if (!authStore.isAuthenticated) {
        next('/login')
        return
      }
      
      if (requiresAdmin && !authStore.isAdmin && !authStore.isSuperAdmin) {
        console.error('❌ Acceso denegado: se requieren permisos de administrador')
        next('/') // Redirigir a home si no es admin
        return
      }
      
    } catch (error) {
      console.error('❌ Error en verificación de autenticación:', error)
      next('/login')
      return
    }
  }
  
  next()
})

export default router