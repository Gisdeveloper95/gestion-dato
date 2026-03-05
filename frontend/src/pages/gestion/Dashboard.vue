<template>
  <div class="gestion-dashboard">
    <!-- Sidebar de navegación -->
    <aside class="gestion-sidebar" :class="{ 'collapsed': sidebarCollapsed }">
      <div class="sidebar-header">
        <h2 v-if="!sidebarCollapsed">Gestión de Información</h2>
        <button @click="toggleSidebar" class="toggle-sidebar-btn">
          <i class="material-icons">{{ sidebarCollapsed ? 'menu_open' : 'menu' }}</i>
        </button>
      </div>
      
      <div class="sidebar-content">
        <nav class="sidebar-nav">
          <ul>
            <li>
              <router-link to="/gestion-informacion/inicio" exact>
                <i class="material-icons">dashboard</i>
                <span v-if="!sidebarCollapsed">Panel Principal</span>
              </router-link>
            </li>
            
            <div class="nav-group">
              <div class="nav-group-title" @click="toggleGroup('insumos')">
                <i class="material-icons">description</i>
                <span v-if="!sidebarCollapsed">Gestión de Insumos</span>
                <i v-if="!sidebarCollapsed" class="material-icons expand-icon">
                  {{ expandedGroups.insumos ? 'expand_less' : 'expand_more' }}
                </i>
              </div>
              
              <ul v-if="expandedGroups.insumos || sidebarCollapsed" class="nav-group-items">
                <!-- Municipios -->
                <li>
                  <router-link to="/gestion-informacion/municipios">
                    <i class="material-icons">location_city</i>
                    <span v-if="!sidebarCollapsed">Municipios</span>
                  </router-link>
                </li>
                
                <!-- 🆕 Centros Poblados -->
                <li>
                  <router-link to="/gestion-informacion/centros-poblados" class="new-feature">
                    <i class="material-icons">place</i>
                    <span v-if="!sidebarCollapsed">Centros Poblados</span>
                  </router-link>
                </li>
                
                <!-- 🆕 Información Administrativa -->
                <li>
                  <router-link to="/gestion-informacion/info-administrativa" class="new-feature">
                    <i class="material-icons">admin_panel_settings</i>
                    <span v-if="!sidebarCollapsed">Información Administrativa</span>
                  </router-link>
                </li>
                
                <!-- Insumos -->
                <li>
                  <router-link to="/gestion-informacion/insumos">
                    <i class="material-icons">folder</i>
                    <span v-if="!sidebarCollapsed">Insumos</span>
                  </router-link>
                </li>
                
                <!-- Profesionales -->
                <li>
                  <router-link to="/gestion-informacion/profesionales">
                    <i class="material-icons">people</i>
                    <span v-if="!sidebarCollapsed">Profesionales</span>
                  </router-link>
                </li>
                
                <!-- Detalles -->
                <li>
                  <router-link to="/gestion-informacion/detalles">
                    <i class="material-icons">list_alt</i>
                    <span v-if="!sidebarCollapsed">Detalles</span>
                  </router-link>
                </li>
                
                <!-- Conceptos -->
                <li>
                  <router-link to="/gestion-informacion/conceptos">
                    <i class="material-icons">comment</i>
                    <span v-if="!sidebarCollapsed">Conceptos</span>
                  </router-link>
                </li>
              </ul>
            </div>

            <div class="nav-group">
              <div class="nav-group-title" @click="toggleGroup('productos')">
                <i class="material-icons">inventory_2</i>
                <span v-if="!sidebarCollapsed">Gestión de Productos</span>
                <i v-if="!sidebarCollapsed" class="material-icons expand-icon">
                  {{ expandedGroups.productos ? 'expand_less' : 'expand_more' }}
                </i>
              </div>
              
              <ul v-if="expandedGroups.productos || sidebarCollapsed" class="nav-group-items">
                <li>
                  <router-link to="/gestion-informacion/productos">
                    <i class="material-icons">archive</i>
                    <span v-if="!sidebarCollapsed">Productos</span>
                  </router-link>
                </li>
              </ul>
            </div>

            <div class="nav-group">
              <div class="nav-group-title" @click="toggleGroup('reportes')">
                <i class="material-icons">file_present</i>
                <span v-if="!sidebarCollapsed">Gestión de Reportes</span>
                <i v-if="!sidebarCollapsed" class="material-icons expand-icon">
                  {{ expandedGroups.reportes ? 'expand_less' : 'expand_more' }}
                </i>
              </div>
              
              <ul v-if="expandedGroups.reportes || sidebarCollapsed" class="nav-group-items">
                <li>
                  <router-link to="/gestion-informacion/reportes/insumos">
                    <i class="material-icons">category</i>
                    <span v-if="!sidebarCollapsed">Reportes de Preoperación</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/gestion-informacion/reportes/productos">
                    <i class="material-icons">output</i>
                    <span v-if="!sidebarCollapsed">Reportes de Post-operación</span>
                  </router-link>
                </li>
              </ul>
            </div>

            <!-- 📊 GESTIÓN OPERACIONES - TODOS LOS ADMINS -->
            <div class="nav-group" v-if="isSuperAdmin">
              <div class="nav-group-title" @click="toggleGroup('operaciones')">
                <i class="material-icons">sync_alt</i>
                <span v-if="!sidebarCollapsed">Gestión de Operaciones</span>
                <i v-if="!sidebarCollapsed" class="material-icons expand-icon">
                  {{ expandedGroups.operaciones ? 'expand_less' : 'expand_more' }}
                </i>
              </div>
              
              <ul v-if="expandedGroups.operaciones || sidebarCollapsed" class="nav-group-items">
                <li>
                  <router-link to="/gestion-informacion/database/postoperacion">
                    <i class="material-icons">upload</i>
                    <span v-if="!sidebarCollapsed">Post-operación</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/gestion-informacion/database/preoperacion">
                    <i class="material-icons">download</i>
                    <span v-if="!sidebarCollapsed">Pre-operación</span>
                  </router-link>
                </li>
              </ul>
            </div>

            <!-- 🔐 GESTIÓN BASE DE DATOS - SOLO USUARIOS ESPECIALES -->
            <div class="nav-group" v-if="esUsuarioEspecial">
              <div class="nav-group-title" @click="toggleGroup('database')">
                <i class="material-icons">storage</i>
                <span v-if="!sidebarCollapsed">Gestión Base de Datos</span>
                <i v-if="!sidebarCollapsed" class="material-icons expand-icon">
                  {{ expandedGroups.database ? 'expand_less' : 'expand_more' }}
                </i>
              </div>
              
              <ul v-if="expandedGroups.database || sidebarCollapsed" class="nav-group-items">
                <li>
                  <router-link to="/gestion-informacion/database">
                    <i class="material-icons">dashboard</i>
                    <span v-if="!sidebarCollapsed">Panel Principal</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/gestion-informacion/database/dominios">
                    <i class="material-icons">category</i>
                    <span v-if="!sidebarCollapsed">Dominios</span>
                  </router-link>
                </li>
              </ul>
            </div>

            <!-- 🔐 ADMINISTRACIÓN DE SERVIDOR - SOLO USUARIOS ESPECIALES -->
            <div class="nav-group" v-if="esUsuarioEspecial">
              <div class="nav-group-title" @click="toggleGroup('servidor')">
                <i class="material-icons">settings_applications</i>
                <span v-if="!sidebarCollapsed">Administración de Servidor</span>
                <i v-if="!sidebarCollapsed" class="material-icons expand-icon">
                  {{ expandedGroups.servidor ? 'expand_less' : 'expand_more' }}
                </i>
              </div>
              
              <ul v-if="expandedGroups.servidor || sidebarCollapsed" class="nav-group-items">
                <li>
                  <router-link to="/gestion-informacion/servidor">
                    <i class="material-icons">dashboard</i>
                    <span v-if="!sidebarCollapsed">Panel de Servidor</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/gestion-informacion/servidor/scripts">
                    <i class="material-icons">code</i>
                    <span v-if="!sidebarCollapsed">Gestión de Scripts</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/gestion-informacion/servidor/backups">
                    <i class="material-icons">backup</i>
                    <span v-if="!sidebarCollapsed">Copias de Seguridad</span>
                  </router-link>
                </li>
              </ul>
            </div>

            <!-- 🔐 ADMINISTRACIÓN DE USUARIOS - SOLO USUARIOS ESPECIALES -->
            <div class="nav-group" v-if="esUsuarioEspecial">
              <div class="nav-group-title" @click="toggleGroup('usuarios')">
                <i class="material-icons">supervisor_account</i>
                <span v-if="!sidebarCollapsed">Administración Usuarios</span>
                <i v-if="!sidebarCollapsed" class="material-icons expand-icon">
                  {{ expandedGroups.usuarios ? 'expand_less' : 'expand_more' }}
                </i>
              </div>
              
              <ul v-if="expandedGroups.usuarios || sidebarCollapsed" class="nav-group-items">
                <li>
                  <router-link to="/gestion-informacion/usuarios-admin">
                    <i class="material-icons">people</i>
                    <span v-if="!sidebarCollapsed">Gestionar Usuarios</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/gestion-informacion/usuarios-admin/nuevo">
                    <i class="material-icons">person_add</i>
                    <span v-if="!sidebarCollapsed">Registrar Usuario</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/gestion-informacion/usuarios">
                    <i class="material-icons">assignment_ind</i>
                    <span v-if="!sidebarCollapsed">Lista Usuarios</span>
                  </router-link>
                </li>
              </ul>
            </div>

            <li>
              <router-link to="/gestion-informacion/auditoria">
                <i class="material-icons">history</i>
                <span v-if="!sidebarCollapsed">Historial de Actividad</span>
              </router-link>
            </li>
          </ul>
        </nav>
      </div>
    </aside>
    
    <!-- Contenido principal -->
    <main class="gestion-content">
      <header class="content-header">
        <div class="header-left">
          <h1 class="page-title">{{ pageTitle }}</h1>
          <nav class="breadcrumb" aria-label="breadcrumb">
            <ol>
              <li>
                <router-link to="/">
                  <i class="material-icons">home</i>
                </router-link>
              </li>
              <li>
                <router-link to="/gestion-informacion/inicio">
                  Gestión de Información
                </router-link>
              </li>
              <li v-if="currentRoute.meta.parent">
                <router-link :to="currentRoute.meta.parentPath || '#'">
                  {{ currentRoute.meta.parent }}
                </router-link>
              </li>
              <li class="active" aria-current="page">
                {{ currentRoute.meta.title || '...' }}
              </li>
            </ol>
          </nav>
        </div>
        
        <div class="header-right">
          <div class="user-info">
            <span>{{ userName }}</span>
            <!-- 🔐 Indicador visual para usuarios especiales -->
            <span v-if="esUsuarioEspecial" class="admin-badge">ADMIN COMPLETO</span>
            <span v-else-if="isSuperAdmin" class="admin-badge">ADMIN</span>
            <div class="user-avatar">
              <span>{{ userInitials }}</span>
            </div>
          </div>
        </div>
      </header>
      
      
      <div class="content-body">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth'

export default defineComponent({
  name: 'GestionDashboard',
  
  setup() {
    const route = useRoute()
    const router = useRouter();
    const authStore = useAuthStore()
    
    // 🔐 LISTA DE USUARIOS CON ACCESO COMPLETO
    const USUARIOS_ESPECIALES = [
      'andres.osorio',
      'elizabeth.eraso', 
      'felipe.vargas',
      'carlos.zarate'
    ];
    
    // Estado del sidebar
    const sidebarCollapsed = ref(false)
    const expandedGroups = ref({
      insumos: true,        // Expandido por defecto para mostrar las nuevas funciones
      productos: false,
      reportes: false,
      operaciones: false,   // 🆕 NUEVO: Grupo de operaciones para todos los admins
      database: false,      // 🔐 RESTRINGIDO: Solo usuarios especiales
      usuarios: false,
      servidor: false       // 🔐 RESTRINGIDO: Solo usuarios especiales
    })
    
    // Comprobar si el usuario es administrador
    const isAdmin = computed(() => 
      authStore.user?.isAdmin || authStore.user?.isStaff || false
    )
    
    // 🔐 NUEVO COMPUTED: Verificar si es usuario especial con acceso completo
    const esUsuarioEspecial = computed(() => {
      if (!authStore.user) {
        console.log('❌ No hay usuario autenticado')
        return false
      }
      
      const username = authStore.user.username;
      const esEspecial = USUARIOS_ESPECIALES.includes(username);
      
      console.log('🔐 Verificando usuario especial:', {
        username,
        esEspecial,
        usuariosPermitidos: USUARIOS_ESPECIALES
      });
      
      return esEspecial;
    });
    
    // 🆕 Comprobar si el usuario es super administrador (para otros usos)
    const isSuperAdmin = computed(() => {
      if (!authStore.user) {
        console.log('No hay usuario autenticado')
        return false
      }
      
      const user = authStore.user
      console.log('Verificando permisos de super admin:', {
        isSuperUser: user.isSuperUser,
        is_superuser: user.is_superuser,
        isSuperAdmin: user.isSuperAdmin,
        isStaff: user.isStaff,
        isAdmin: user.isAdmin,
        rol_tipo: user.rol_tipo
      })
      
      // Verificar diferentes posibles campos para super admin
      const superAdminCheck = !!(
        user.isSuperUser || 
        user.is_superuser || 
        user.isSuperAdmin ||
        user.rol_tipo === 'super_admin' ||
        user.rol_tipo === 'administrador' ||
        user.isStaff ||
        user.isAdmin
      )
      
      console.log('Resultado isSuperAdmin:', superAdminCheck)
      return superAdminCheck
    })
    
    // Obtener nombre de usuario
    const userName = computed(() => {
      if (!authStore.user) return ''
      return authStore.user.firstName || authStore.user.username
    })
    
    // Obtener iniciales del usuario para el avatar
    const userInitials = computed(() => {
      if (!authStore.user) return ''
      
      if (authStore.user.firstName && authStore.user.lastName) {
        return `${authStore.user.firstName.charAt(0)}${authStore.user.lastName.charAt(0)}`
      }
      
      return authStore.user.username.charAt(0).toUpperCase()
    })
    
    // Ruta actual
    const currentRoute = computed(() => route)
    
    // Título de la página
    const pageTitle = computed(() => {
      return route.meta.title || 'Gestión de Información'
    })
    
    // Alternar sidebar
    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value
      localStorage.setItem('gestion-sidebar-collapsed', sidebarCollapsed.value.toString())
    }
    
    // Alternar grupos de navegación
    const toggleGroup = (group: string) => {
      console.log('Toggling group:', group)
      if (expandedGroups.value[group] !== undefined) {
        expandedGroups.value[group] = !expandedGroups.value[group]
        console.log('Group state after toggle:', expandedGroups.value[group])
      }
    }
    
    // Recuperar estado del sidebar del localStorage
    onMounted(async () => {
      try {
        // Comprobar autenticación
        const isAuthenticated = await authStore.verifyAuthentication();
        if (!isAuthenticated) {
          router.push('/login');
        }
      
        // Resto del código para el sidebar
        const savedState = localStorage.getItem('gestion-sidebar-collapsed');
        if (savedState) {
          sidebarCollapsed.value = savedState === 'true';
        }
        
        // Si estamos en móvil, colapsamos el sidebar por defecto
        if (window.innerWidth < 992 && savedState === null) {
          sidebarCollapsed.value = true;
        }

        // 🆕 Debug inicial
        console.log('Dashboard montado. Usuario:', authStore.user)
        console.log('isSuperAdmin:', isSuperAdmin.value)
        console.log('🔐 esUsuarioEspecial:', esUsuarioEspecial.value)
        console.log('📊 Grupos expandidos:', expandedGroups.value)
        
      } catch (error) {
        console.error("Error al verificar autenticación:", error);
        router.push('/login');
      }
    });
    
    // Expandir el grupo correspondiente a la ruta actual
    watch(
      () => route.path,
      (path) => {
        console.log('Ruta cambió a:', path)
        
        // 🆕 Expandir grupo de insumos para las nuevas rutas también
        if (path.includes('/insumos') || path.includes('/municipios') || 
            path.includes('/centros-poblados') || path.includes('/info-administrativa') ||
            path.includes('/profesionales') || path.includes('/detalles') || 
            path.includes('/conceptos')) {
          expandedGroups.value.insumos = true
        }

        if (path.includes('/productos')) {
          expandedGroups.value.productos = true
        }

        if (path.includes('/reportes')) {
          expandedGroups.value.reportes = true
        }

        // Expandir grupo de operaciones (todos los admins pueden ver post/pre operación)
        if (path.includes('/database/postoperacion') || path.includes('/database/preoperacion')) {
          expandedGroups.value.operaciones = true
        }

        // Expandir grupo de base de datos (solo si es usuario especial y accede al panel o dominios)
        if ((path.includes('/database') && !path.includes('/postoperacion') && !path.includes('/preoperacion')) && esUsuarioEspecial.value) {
          expandedGroups.value.database = true
        }

        // Expandir grupo de usuarios (solo si es usuario especial)
        if (path.includes('/usuarios-admin') && esUsuarioEspecial.value) {
          expandedGroups.value.usuarios = true
        }

        // 🆕 Expandir grupo de servidor (solo si es usuario especial)
        if (path.includes('/servidor') && esUsuarioEspecial.value) {
          console.log('Expandiendo grupo servidor')
          expandedGroups.value.servidor = true
        }
      },
      { immediate: true }
    )
    
    return {
      sidebarCollapsed,
      expandedGroups,
      currentRoute,
      pageTitle,
      isAdmin,
      isSuperAdmin,
      esUsuarioEspecial,  // 🔐 NUEVO: Control de acceso especial
      userName,
      userInitials,
      toggleSidebar,
      toggleGroup
    }
  }
})
</script>

<style scoped>
.gestion-dashboard {
  display: flex;
  min-height: calc(100vh - 140px); /* Ajustar según altura de header y footer */
}

/* Sidebar */
.gestion-sidebar {
  width: 280px;
  background-color: #343a40;
  color: #f8f9fa;
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.gestion-sidebar.collapsed {
  width: 80px;
}

.sidebar-header {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-header h2 {
  margin: 0;
  font-size: 1.2rem;
  white-space: nowrap;
}

.toggle-sidebar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: none;
  border: none;
  color: #f8f9fa;
  cursor: pointer;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.toggle-sidebar-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
}

.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-nav > ul > li > a,
.nav-group-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;
}

.sidebar-nav > ul > li > a:hover,
.nav-group-title:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.sidebar-nav > ul > li > a.router-link-active {
  color: #fff;
  background-color: rgba(0, 123, 255, 0.2);
  border-left: 3px solid #007bff;
}

.sidebar-nav i {
  font-size: 1.2rem;
}

.nav-group {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.nav-group-title {
  position: relative;
}

.expand-icon {
  position: absolute;
  right: 1.5rem;
  transition: transform 0.3s;
}

.nav-group-items {
  margin: 0;
  overflow: hidden;
  transition: max-height 0.3s;
}

.gestion-sidebar.collapsed .nav-group-items {
  max-height: none !important;
}

.nav-group-items li a {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem 0.75rem 3rem;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: background-color 0.2s, color 0.2s;
  position: relative;
}

.gestion-sidebar.collapsed .nav-group-items li a {
  padding: 0.75rem 1.5rem;
  justify-content: center;
}

.nav-group-items li a:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.nav-group-items li a.router-link-active {
  background-color: rgba(0, 123, 255, 0.1);
  color: #fff;
}

/* 🆕 Estilos para nuevas funcionalidades */
.new-feature {
  position: relative;
}

.new-feature i {
  color: #10b981 !important; /* Verde para centros poblados */
}

.new-feature[href*="info-administrativa"] i {
  color: #f59e0b !important; /* Amarillo para info administrativa */
}

.new-feature.router-link-active i {
  color: #fff !important;
}

.new-badge {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: #ef4444;
  color: white;
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  border-radius: 9999px;
  font-weight: 600;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.gestion-sidebar.collapsed .new-badge {
  display: none;
}

/* Badge general */
.badge {
  display: inline-block;
  padding: 0.125rem 0.375rem;
  font-size: 0.625rem;
  font-weight: 600;
  line-height: 1;
  text-align: center;
  white-space: nowrap;
  vertical-align: baseline;
  border-radius: 0.375rem;
}

/* 🆕 Estilos específicos para administración de servidor */
.nav-group-items li a[href*="/servidor"] {
  border-left: 3px solid transparent;
  transition: border-left-color 0.2s;
}

.nav-group-items li a[href*="/servidor"]:hover {
  border-left-color: #28a745;
}

.nav-group-items li a[href*="/servidor"].router-link-active {
  border-left-color: #007bff;
  background-color: rgba(0, 123, 255, 0.15);
}

/* Iconos específicos para servidor */
.nav-group-items li a[href*="/servidor/scripts"] i {
  color: #17a2b8;
}

.nav-group-items li a[href*="/servidor/backups"] i {
  color: #28a745;
}

/* 📊 Estilos específicos para operaciones (accesible por todos los admins) */
.nav-group-items li a[href*="/database/postoperacion"] {
  border-left: 3px solid transparent;
  transition: border-left-color 0.2s;
}

.nav-group-items li a[href*="/database/preoperacion"] {
  border-left: 3px solid transparent;
  transition: border-left-color 0.2s;
}

.nav-group-items li a[href*="/database/postoperacion"]:hover,
.nav-group-items li a[href*="/database/preoperacion"]:hover {
  border-left-color: #17a2b8;
}

.nav-group-items li a[href*="/database/postoperacion"].router-link-active,
.nav-group-items li a[href*="/database/preoperacion"].router-link-active {
  border-left-color: #007bff;
  background-color: rgba(23, 162, 184, 0.15);
}

/* Iconos específicos para operaciones */
.nav-group-items li a[href*="/database/postoperacion"] i {
  color: #28a745; /* Verde para upload/post */
}

.nav-group-items li a[href*="/database/preoperacion"] i {
  color: #ffc107; /* Amarillo para download/pre */
}

/* Contenido principal */
.gestion-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #fff;
  border-bottom: 1px solid #e9ecef;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.page-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #343a40;
}

.breadcrumb {
  display: flex;
  align-items: center;
}

.breadcrumb ol {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  padding: 0;
  margin: 0;
  list-style: none;
}

.breadcrumb li {
  display: flex;
  align-items: center;
}

.breadcrumb li:not(:first-child)::before {
  content: "/";
  display: inline-block;
  padding: 0 0.5rem;
  color: #6c757d;
}

.breadcrumb a {
  color: #007bff;
  text-decoration: none;
}

.breadcrumb .active {
  color: #6c757d;
}

.breadcrumb i {
  font-size: 1.2rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* 🔐 ESTILOS PARA BADGES DE ADMIN */
.admin-badge {
  font-size: 0.7rem;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.admin-badge:contains("COMPLETO") {
  background-color: #dc2626;
  color: white;
}

.admin-badge:not(:contains("COMPLETO")) {
  background-color: #ea580c;
  color: white;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #007bff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
}

.content-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  background-color: #f8f9fa;
}

/* Transiciones de página */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 🆕 Debug visual para desarrollo */
.nav-group[data-debug="servidor"] {
  border: 2px solid red !important;
}

/* Responsive */
@media (max-width: 992px) {
  .gestion-sidebar {
    position: fixed;
    z-index: 100;
    height: 100%;
    top: 0;
    left: 0;
  }
  
  .gestion-content {
    margin-left: 80px;
  }
  
  .content-header {
    padding: 1rem;
  }
  
  .content-body {
    padding: 1rem;
  }
  
  .header-left {
    max-width: 70%;
  }
  
  .page-title {
    font-size: 1.25rem;
  }
}

@media (max-width: 768px) {
  .gestion-content {
    margin-left: 0;
  }
  
  .header-right span {
    display: none;
  }
  
  .breadcrumb {
    display: none;
  }
  
  .new-badge {
    display: none;
  }
  
  .admin-badge {
    display: none;
  }
}

/* 🆕 Estilos de depuración para desarrollo */
.debug-info {
  position: fixed;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 10px;
  border-radius: 5px;
  font-size: 12px;
  z-index: 9999;
}
</style>