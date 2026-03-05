<template>
  <div class="disposicion-dashboard">
    <!-- Sidebar de navegación -->
    <aside class="disposicion-sidebar" :class="{ 'collapsed': sidebarCollapsed }">
      <div class="sidebar-header">
        <h2 v-if="!sidebarCollapsed">Disposición de Información</h2>
        <button @click="toggleSidebar" class="toggle-sidebar-btn">
          <i class="material-icons">{{ sidebarCollapsed ? 'menu_open' : 'menu' }}</i>
        </button>
      </div>
      
      <div class="sidebar-content">
        <nav class="sidebar-nav">
          <ul>
            <!-- Municipios - Vista inicial -->
            <li>
              <router-link to="/disposicion-informacion/municipios" exact>
                <i class="material-icons">location_city</i>
                <span v-if="!sidebarCollapsed">Municipios</span>
              </router-link>
            </li>
            
            <!-- Profesionales -->
            <li>
              <router-link to="/disposicion-informacion/profesionales">
                <i class="material-icons">people</i>
                <span v-if="!sidebarCollapsed">Profesionales</span>
              </router-link>
            </li>
            
            <!-- Insumos -->
            <li>
              <router-link to="/disposicion-informacion/insumos">
                <i class="material-icons">folder</i>
                <span v-if="!sidebarCollapsed">Insumos</span>
              </router-link>
            </li>

            <!-- Etapas Operativas -->
            <div class="nav-group">
              <div class="nav-group-title" @click="toggleGroup('etapas')">
                <i class="material-icons">work_history</i>
                <span v-if="!sidebarCollapsed">Etapas Operativas</span>
                <i v-if="!sidebarCollapsed" class="material-icons expand-icon">
                  {{ expandedGroups.etapas ? 'expand_less' : 'expand_more' }}
                </i>
              </div>

              <ul v-if="expandedGroups.etapas || sidebarCollapsed" class="nav-group-items">
                <li>
                  <router-link to="/disposicion-informacion/preoperacion">
                    <i class="material-icons">account_tree</i>
                    <span v-if="!sidebarCollapsed">Pre-Operación</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/disposicion-informacion/operacion">
                    <i class="material-icons">engineering</i>
                    <span v-if="!sidebarCollapsed">Operación</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/disposicion-informacion/productos">
                    <i class="material-icons">inventory_2</i>
                    <span v-if="!sidebarCollapsed">Productos</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/disposicion-informacion/transversal">
                    <i class="material-icons">swap_horiz</i>
                    <span v-if="!sidebarCollapsed">Transversal</span>
                  </router-link>
                </li>
              </ul>
            </div>

            <!-- Gestión de Reportes -->
            <div class="nav-group">
              <div class="nav-group-title" @click="toggleGroup('reportes')">
                <i class="material-icons">assessment</i>
                <span v-if="!sidebarCollapsed">Gestión de Reportes</span>
                <i v-if="!sidebarCollapsed" class="material-icons expand-icon">
                  {{ expandedGroups.reportes ? 'expand_less' : 'expand_more' }}
                </i>
              </div>
              
              <ul v-if="expandedGroups.reportes || sidebarCollapsed" class="nav-group-items">
                <li>
                  <router-link to="/disposicion-informacion/reportes/insumos">
                    <i class="material-icons">category</i>
                    <span v-if="!sidebarCollapsed">Reportes de Insumos</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/disposicion-informacion/reportes/preoperacion-completo">
                    <i class="material-icons">folder_open</i>
                    <span v-if="!sidebarCollapsed">Reportes Pre Operacion</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/disposicion-informacion/reportes/postoperacion">
                    <i class="material-icons">output</i>
                    <span v-if="!sidebarCollapsed">Reportes de Post-operacion</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/disposicion-informacion/reportes/operacion">
                    <i class="material-icons">output</i>
                    <span v-if="!sidebarCollapsed">Reportes de Operación</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/disposicion-informacion/reportes/transversales">
                    <i class="material-icons">output</i>
                    <span v-if="!sidebarCollapsed">Reportes Transversales</span>
                  </router-link>
                </li>

              </ul>
            </div>
          </ul>
        </nav>
      </div>
      
      <!-- Info del usuario y sus permisos -->
      <div class="sidebar-footer" v-if="!sidebarCollapsed">
        <div class="user-role-info">
          <div class="role-badge" :class="userRoleClass">
            <i class="material-icons">{{ userRoleIcon }}</i>
            <span>{{ userRoleText }}</span>
          </div>
          <div v-if="isProfesional && municipiosAsignados.length > 0" class="assigned-info">
            <small>{{ municipiosAsignados.length }} municipios asignados</small>
          </div>
        </div>
      </div>
    </aside>
    
    <!-- Contenido principal -->
    <main class="disposicion-content">
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
                <router-link to="/disposicion-informacion/municipios">
                  Disposición de Información
                </router-link>
              </li>
              <li v-if="currentRoute.meta.parent">
                <router-link :to="currentRoute.meta.parentPath || '#'">
                  {{ currentRoute.meta.parent }}
                </router-link>
              </li>
              <li class="active" aria-current="page">
                {{ currentRoute.meta.title || pageTitle }}
              </li>
            </ol>
          </nav>
        </div>
        
        <div class="header-right">
          <div class="access-info">
            <div class="access-badge" :class="accessLevelClass">
              <i class="material-icons">{{ accessLevelIcon }}</i>
              <span>{{ accessLevelText }}</span>
            </div>
          </div>
          
          <div class="user-info">
            <span>{{ userName }}</span>
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
  name: 'DisposicionDashboard',
  
  setup() {
    const route = useRoute()
    const router = useRouter();
    const authStore = useAuthStore()
    
    // Estado del sidebar
    const sidebarCollapsed = ref(false)
    const expandedGroups = ref({
      etapas: false,
      reportes: false
    })
    
    // Verificar roles y permisos - MEJORADO PARA DISTINGUIR TIPOS DE ADMIN
    const isSuperAdmin = computed(() => authStore.isSuperAdmin);
    const isAdmin = computed(() => authStore.isAdmin);
    const isProfesional = computed(() => authStore.isProfesional);
    
    // Municipios asignados para profesionales
    const municipiosAsignados = computed(() => {
      if (!isProfesional.value || !authStore.user?.municipios_asignados) return [];
      
      let municipios: number[] = [];
      
      if (typeof authStore.user.municipios_asignados === 'string') {
        municipios = authStore.user.municipios_asignados.split(',')
          .map(m => parseInt(m.trim()))
          .filter(m => !isNaN(m));
      } else if (Array.isArray(authStore.user.municipios_asignados)) {
        municipios = authStore.user.municipios_asignados;
      }
      
      return municipios;
    });
    
    // Información del usuario
    const userName = computed(() => {
      if (!authStore.user) return 'Usuario'
      return authStore.user.firstName || authStore.user.username || 'Usuario'
    })
    
    const userInitials = computed(() => {
      if (!authStore.user) return 'U'
      
      if (authStore.user.firstName && authStore.user.lastName) {
        return `${authStore.user.firstName.charAt(0)}${authStore.user.lastName.charAt(0)}`
      }
      
      return (authStore.user.username || 'U').charAt(0).toUpperCase()
    })
    
    // Información de rol del usuario
    const userRoleText = computed(() => {
      if (isSuperAdmin.value) return 'Super Administrador';
      if (isAdmin.value) return 'Administrador';
      if (isProfesional.value) return 'Profesional';
      return 'Usuario Público';
    });
    
    const userRoleIcon = computed(() => {
      if (isSuperAdmin.value) return 'admin_panel_settings';
      if (isAdmin.value) return 'manage_accounts';
      if (isProfesional.value) return 'engineering';
      return 'account_circle';
    });
    
    const userRoleClass = computed(() => {
      if (isSuperAdmin.value) return 'role-super-admin';
      if (isAdmin.value) return 'role-admin';
      if (isProfesional.value) return 'role-profesional';
      return 'role-publico';
    });
    
    // Nivel de acceso y permisos
    const accessLevelText = computed(() => {
      if (isSuperAdmin.value) return 'Acceso Total';
      if (isAdmin.value) return 'Solo Lectura + Descarga';
      if (isProfesional.value) return `Solo Municipios Asignados`;
      return 'Solo Lectura';
    });
    
    const accessLevelIcon = computed(() => {
      if (isSuperAdmin.value) return 'all_inclusive';
      if (isAdmin.value) return 'download';
      if (isProfesional.value) return 'location_on';
      return 'visibility';
    });
    
    const accessLevelClass = computed(() => {
      if (isSuperAdmin.value) return 'access-total';
      if (isAdmin.value) return 'access-admin';
      if (isProfesional.value) return 'access-profesional';
      return 'access-publico';
    });
    
    // Ruta actual y título de página
    const currentRoute = computed(() => route)
    
    const pageTitle = computed(() => {
      const routeTitle = route.meta.title;
      if (routeTitle) return routeTitle as string;

      // Titulos por defecto segun la ruta
      const path = route.path;
      if (path.includes('/municipios')) return 'Municipios';
      if (path.includes('/profesionales')) return 'Profesionales';
      if (path.includes('/insumos')) return 'Insumos';
      if (path.includes('/productos')) return 'Productos';
      if (path.includes('/reportes/preoperacion-completo')) return 'Reportes Pre Operacion';
      if (path.includes('/reportes/insumos')) return 'Reportes de Insumos';
      if (path.includes('/reportes/postoperacion')) return 'Reportes de Post-operacion';

      return 'Disposicion de Informacion';
    })
    
    // Métodos de navegación
    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value
      localStorage.setItem('disposicion-sidebar-collapsed', sidebarCollapsed.value.toString())
    }
    
    const toggleGroup = (group: string) => {
      if (expandedGroups.value[group] !== undefined) {
        expandedGroups.value[group] = !expandedGroups.value[group]
      }
    }
    
    // Inicialización
    onMounted(async () => {
      try {
        // Verificar autenticación (opcional, ya que todos pueden acceder)
        if (authStore.isAuthenticated) {
          await authStore.checkAuth();
        }
        
        // Recuperar estado del sidebar
        const savedState = localStorage.getItem('disposicion-sidebar-collapsed');
        if (savedState) {
          sidebarCollapsed.value = savedState === 'true';
        }
        
        // Collapsar en móvil por defecto
        if (window.innerWidth < 992 && savedState === null) {
          sidebarCollapsed.value = true;
        }
        
        // Redirigir a municipios si estamos en la ruta base
        if (route.path === '/disposicion-informacion' || route.path === '/disposicion-informacion/') {
          router.replace('/disposicion-informacion/municipios');
        }
        
      } catch (error) {
        console.error("Error al inicializar disposición:", error);
      }
    });
    
    // Expandir grupos según la sección actual
    watch(
      () => route.path,
      (path) => {
        if (path.includes('/reportes')) {
          expandedGroups.value.reportes = true;
        }
        if (path.includes('/preoperacion') || path.includes('/productos') ||
            path.includes('/operacion') || path.includes('/transversal')) {
          expandedGroups.value.etapas = true;
        }
      },
      { immediate: true }
    )
    
    return {
      // Estado del sidebar
      sidebarCollapsed,
      expandedGroups,
      
      // Información de ruta y página
      currentRoute,
      pageTitle,
      
      // Información del usuario
      userName,
      userInitials,
      userRoleText,
      userRoleIcon,
      userRoleClass,
      
      // Información de acceso
      accessLevelText,
      accessLevelIcon,
      accessLevelClass,
      
      // Roles y permisos
      isSuperAdmin,
      isAdmin,
      isProfesional,
      municipiosAsignados,
      
      // Métodos
      toggleSidebar,
      toggleGroup
    }
  }
})
</script>

<style scoped>
.disposicion-dashboard {
  display: flex;
  min-height: calc(100vh - 140px);
}

/* ========== SIDEBAR ========== */
.disposicion-sidebar {
  width: 280px;
  background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
  color: #ecf0f1;
  transition: width 0.3s ease;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 2px 0 10px rgba(0,0,0,0.1);
}

.disposicion-sidebar.collapsed {
  width: 80px;
}

.sidebar-header {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(236, 240, 241, 0.1);
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
}

.sidebar-header h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  white-space: nowrap;
  color: white;
}

.toggle-sidebar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  cursor: pointer;
  border-radius: 50%;
  transition: all 0.2s;
}

.toggle-sidebar-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding-top: 1rem;
}

.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-nav > ul > li > a {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  color: rgba(236, 240, 241, 0.8);
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.sidebar-nav > ul > li > a:hover {
  background: rgba(52, 152, 219, 0.2);
  color: #ecf0f1;
  border-left-color: #3498db;
}

.sidebar-nav > ul > li > a.router-link-active {
  color: white;
  background: rgba(52, 152, 219, 0.3);
  border-left-color: #3498db;
  font-weight: 600;
}

.sidebar-nav i {
  font-size: 1.2rem;
  min-width: 24px;
}

/* Grupos de navegación */
.nav-group {
  border-bottom: 1px solid rgba(236, 240, 241, 0.05);
}

.nav-group-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  color: rgba(236, 240, 241, 0.8);
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.nav-group-title:hover {
  background: rgba(149, 165, 166, 0.1);
  color: #ecf0f1;
}

.expand-icon {
  position: absolute;
  right: 1.5rem;
  transition: transform 0.3s;
}

.nav-group-items {
  margin: 0;
  overflow: hidden;
  background: rgba(44, 62, 80, 0.3);
}

.disposicion-sidebar.collapsed .nav-group-items {
  max-height: none !important;
}

.nav-group-items li a {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem 0.75rem 3rem;
  color: rgba(236, 240, 241, 0.7);
  text-decoration: none;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.disposicion-sidebar.collapsed .nav-group-items li a {
  padding: 0.75rem 1.5rem;
  justify-content: center;
}

.nav-group-items li a:hover {
  background: rgba(52, 152, 219, 0.15);
  color: #ecf0f1;
}

.nav-group-items li a.router-link-active {
  background: rgba(52, 152, 219, 0.2);
  color: white;
  font-weight: 500;
}

/* Footer del sidebar */
.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid rgba(236, 240, 241, 0.1);
  background: rgba(44, 62, 80, 0.3);
}

.user-role-info {
  text-align: center;
}

.role-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.role-super-admin {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
}

.role-admin {
  background: linear-gradient(135deg, #f39c12, #d68910);
  color: white;
}

.role-profesional {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  color: white;
}

.role-publico {
  background: linear-gradient(135deg, #95a5a6, #7f8c8d);
  color: white;
}

.assigned-info {
  color: rgba(236, 240, 241, 0.7);
  font-size: 0.75rem;
}

/* ========== CONTENIDO PRINCIPAL ========== */
.disposicion-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f8f9fa;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: white;
  border-bottom: 1px solid #e9ecef;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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
  color: #2c3e50;
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
  color: #3498db;
  text-decoration: none;
  font-size: 0.9rem;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

.breadcrumb .active {
  color: #6c757d;
  font-size: 0.9rem;
}

.breadcrumb i {
  font-size: 1.1rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.access-info {
  display: flex;
  align-items: center;
}

.access-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.access-total {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
}

.access-admin {
  background: linear-gradient(135deg, #f39c12, #d68910);
  color: white;
}

.access-profesional {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  color: white;
}

.access-publico {
  background: linear-gradient(135deg, #95a5a6, #7f8c8d);
  color: white;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
  color: #2c3e50;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3498db, #2980b9);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
}

.content-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

/* ========== TRANSICIONES ========== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* ========== RESPONSIVE ========== */
@media (max-width: 992px) {
  .disposicion-sidebar {
    position: fixed;
    z-index: 100;
    height: 100%;
    top: 0;
    left: 0;
  }
  
  .disposicion-content {
    margin-left: 80px;
  }
  
  .content-header {
    padding: 1rem;
  }
  
  .content-body {
    padding: 1rem;
  }
  
  .header-left {
    max-width: 60%;
  }
  
  .page-title {
    font-size: 1.25rem;
  }
}

@media (max-width: 768px) {
  .disposicion-content {
    margin-left: 0;
  }
  
  .header-right .user-info span {
    display: none;
  }
  
  .breadcrumb {
    display: none;
  }
  
  .access-info {
    display: none;
  }
  
  .content-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .header-right {
    width: 100%;
    justify-content: flex-end;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.1rem;
  }
  
  .content-body {
    padding: 0.5rem;
  }
}
</style>