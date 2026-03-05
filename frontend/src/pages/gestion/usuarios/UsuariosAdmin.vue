<template>
  <div class="usuarios-admin-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">
            <i class="material-icons">admin_panel_settings</i>
            Panel de Administración de Usuarios
          </h1>
          <p class="page-description">
            Dashboard completo para la gestión y monitoreo de usuarios del sistema
          </p>
        </div>
        
        <div class="header-actions">
          <router-link 
            to="/gestion-informacion/usuarios-admin/nuevo" 
            class="btn btn-primary"
            v-if="puedeCrearUsuarios"
          >
            <i class="material-icons">person_add</i>
            Crear Usuario
          </router-link>
          
          <router-link 
            to="/gestion-informacion/usuarios" 
            class="btn btn-secondary"
          >
            <i class="material-icons">list</i>
            Ver Lista Completa
          </router-link>
        </div>
      </div>
    </div>

    <!-- Dashboard Content -->
    <div class="page-content">
      
      <!-- Loading -->
      <div v-if="cargando" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Cargando dashboard...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="error-container">
        <i class="material-icons">error</i>
        <h3>Error al cargar dashboard</h3>
        <p>{{ error }}</p>
        <button @click="cargarDatos" class="btn btn-primary">
          <i class="material-icons">refresh</i>
          Reintentar
        </button>
      </div>

      <!-- Dashboard -->
      <div v-else class="dashboard-grid">
        
        <!-- Estadísticas principales -->
        <div class="dashboard-section stats-section">
          <h2 class="section-title">
            <i class="material-icons">analytics</i>
            Estadísticas Generales
          </h2>
          
          <div class="stats-grid">
            <div class="stat-card total">
              <div class="stat-icon">
                <i class="material-icons">groups</i>
              </div>
              <div class="stat-content">
                <h3>{{ estadisticas?.total_usuarios || 0 }}</h3>
                <p>Total Usuarios</p>
                <span class="stat-change positive" v-if="estadisticas?.usuarios_recientes">
                  +{{ estadisticas.usuarios_recientes }} este mes
                </span>
              </div>
            </div>
            
            <div class="stat-card active">
              <div class="stat-icon">
                <i class="material-icons">check_circle</i>
              </div>
              <div class="stat-content">
                <h3>{{ estadisticas?.usuarios_activos || 0 }}</h3>
                <p>Usuarios Activos</p>
                <span class="stat-percentage">
                  {{ estadisticas?.porcentaje_activos || 0 }}% del total
                </span>
              </div>
            </div>
            
            <div class="stat-card inactive">
              <div class="stat-icon">
                <i class="material-icons">block</i>
              </div>
              <div class="stat-content">
                <h3>{{ estadisticas?.usuarios_inactivos || 0 }}</h3>
                <p>Usuarios Inactivos</p>
                <span class="stat-percentage">
                  {{ 100 - (estadisticas?.porcentaje_activos || 0) }}% del total
                </span>
              </div>
            </div>
            
            <div class="stat-card recent">
              <div class="stat-icon">
                <i class="material-icons">schedule</i>
              </div>
              <div class="stat-content">
                <h3>{{ estadisticas?.usuarios_recientes || 0 }}</h3>
                <p>Nuevos (30 días)</p>
                <span class="stat-help">Usuarios registrados recientemente</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Distribución por roles -->
        <div class="dashboard-section roles-section">
          <h2 class="section-title">
            <i class="material-icons">verified_user</i>
            Distribución por Roles
          </h2>
          
          <div class="roles-grid">
            <div class="role-card super-admin">
              <div class="role-header">
                <i class="material-icons">admin_panel_settings</i>
                <h3>Super Administradores</h3>
              </div>
              <div class="role-count">{{ estadisticas?.super_admins || 0 }}</div>
              <div class="role-description">
                Control total del sistema
              </div>
            </div>
            
            <div class="role-card admin">
              <div class="role-header">
                <i class="material-icons">manage_accounts</i>
                <h3>Administradores</h3>
              </div>
              <div class="role-count">{{ estadisticas?.admins || 0 }}</div>
              <div class="role-description">
                Gestión de usuarios y configuración
              </div>
            </div>
            
            <div class="role-card profesional">
              <div class="role-header">
                <i class="material-icons">person</i>
                <h3>Profesionales</h3>
              </div>
              <div class="role-count">{{ estadisticas?.profesionales || 0 }}</div>
              <div class="role-description">
                Acceso básico al sistema
              </div>
            </div>
          </div>
        </div>

        <!-- Acciones rápidas -->
        <div class="dashboard-section actions-section">
          <h2 class="section-title">
            <i class="material-icons">bolt</i>
            Acciones Rápidas
          </h2>
          
          <div class="actions-grid">
            <router-link 
              to="/gestion-informacion/usuarios-admin/nuevo" 
              class="action-card create"
              v-if="puedeCrearUsuarios"
            >
              <div class="action-icon">
                <i class="material-icons">person_add</i>
              </div>
              <div class="action-content">
                <h3>Crear Usuario</h3>
                <p>Agregar nuevo usuario al sistema</p>
              </div>
              <i class="material-icons arrow">arrow_forward</i>
            </router-link>
            
            <router-link 
              to="/gestion-informacion/usuarios" 
              class="action-card manage"
            >
              <div class="action-icon">
                <i class="material-icons">manage_accounts</i>
              </div>
              <div class="action-content">
                <h3>Gestionar Usuarios</h3>
                <p>Ver, editar y administrar usuarios</p>
              </div>
              <i class="material-icons arrow">arrow_forward</i>
            </router-link>
            
            <button 
              @click="cargarDatos" 
              class="action-card refresh"
            >
              <div class="action-icon">
                <i class="material-icons">refresh</i>
              </div>
              <div class="action-content">
                <h3>Actualizar Datos</h3>
                <p>Refrescar estadísticas del dashboard</p>
              </div>
              <i class="material-icons arrow">refresh</i>
            </button>
          </div>
        </div>

        <!-- Información del sistema -->
        <div class="dashboard-section system-section">
          <h2 class="section-title">
            <i class="material-icons">info</i>
            Información del Sistema
          </h2>
          
          <div class="system-info">
            <div class="info-item">
              <i class="material-icons">account_circle</i>
              <div>
                <strong>Usuario Actual:</strong>
                <span>{{ usuarioActual?.firstName }} {{ usuarioActual?.lastName }}</span>
              </div>
            </div>
            
            <div class="info-item">
              <i class="material-icons">verified_user</i>
              <div>
                <strong>Rol:</strong>
                <span class="role-badge" :class="usuarioActual?.rol_tipo">
                  {{ getRolDisplayName(usuarioActual?.rol_tipo) }}
                </span>
              </div>
            </div>
            
            <div class="info-item">
              <i class="material-icons">schedule</i>
              <div>
                <strong>Última actualización:</strong>
                <span>{{ formatearFecha(new Date()) }}</span>
              </div>
            </div>
            
            <div class="info-item">
              <i class="material-icons">security</i>
              <div>
                <strong>Permisos:</strong>
                <span>{{ usuarioActual?.isSuperUser ? 'Control Total' : (usuarioActual?.isStaff ? 'Administrador' : 'Limitado') }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { usuariosService, type EstadisticasUsuarios } from '@/api/usuarios'
import { useAuthStore } from '@/store/auth'

// =============== STATE ===============
const authStore = useAuthStore()

const cargando = ref(false)
const error = ref<string | null>(null)
const estadisticas = ref<EstadisticasUsuarios | null>(null)

// =============== COMPUTED ===============
const usuarioActual = computed(() => authStore.user)

const puedeCrearUsuarios = computed(() => {
  return usuarioActual.value?.isStaff || usuarioActual.value?.isSuperUser
})

// =============== METHODS ===============
const cargarDatos = async () => {
  try {
    cargando.value = true
    error.value = null

    estadisticas.value = await usuariosService.obtenerEstadisticas()

  } catch (err: any) {
    error.value = err.message
    console.error('Error cargando estadísticas:', err)
  } finally {
    cargando.value = false
  }
}

const getRolDisplayName = (rolTipo: string): string => {
  const roles = {
    'super_admin': 'Super Administrador',
    'admin': 'Administrador',
    'profesional': 'Profesional'
  }
  return roles[rolTipo as keyof typeof roles] || 'Desconocido'
}

const formatearFecha = (fecha: Date): string => {
  return fecha.toLocaleDateString('es-CO', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// =============== LIFECYCLE ===============
onMounted(() => {
  cargarDatos()
})
</script>

<style scoped>
.usuarios-admin-page {
  min-height: 100vh;
  background: #f8f9fa;
}

/* Header */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  margin-bottom: 2rem;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 700;
}

.page-description {
  margin: 0;
  opacity: 0.9;
  font-size: 1.1rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

/* Contenido principal */
.page-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.dashboard-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 1.5rem 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: #1f2937;
}

/* Estadísticas */
.stats-section {
  grid-column: 1 / -1;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  border: 2px solid;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-card.total {
  border-color: #3b82f6;
}

.stat-card.active {
  border-color: #10b981;
}

.stat-card.inactive {
  border-color: #ef4444;
}

.stat-card.recent {
  border-color: #f59e0b;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
}

.total .stat-icon {
  background: #eff6ff;
  color: #3b82f6;
}

.active .stat-icon {
  background: #f0fdf4;
  color: #10b981;
}

.inactive .stat-icon {
  background: #fef2f2;
  color: #ef4444;
}

.recent .stat-icon {
  background: #fffbeb;
  color: #f59e0b;
}

.stat-content h3 {
  margin: 0 0 0.25rem 0;
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
}

.stat-content p {
  margin: 0 0 0.5rem 0;
  color: #6b7280;
  font-size: 0.9rem;
}

.stat-change {
  font-size: 0.8rem;
  font-weight: 500;
}

.stat-change.positive {
  color: #10b981;
}

.stat-percentage,
.stat-help {
  font-size: 0.8rem;
  color: #6b7280;
}

/* Roles */
.roles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.role-card {
  padding: 1.5rem;
  border-radius: 12px;
  text-align: center;
  border: 2px solid;
}

.role-card.super-admin {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-color: #fecaca;
}

.role-card.admin {
  background: linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%);
  border-color: #fdba74;
}

.role-card.profesional {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border-color: #bbf7d0;
}

.role-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.role-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.role-count {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.role-description {
  font-size: 0.8rem;
  color: #6b7280;
}

/* Acciones */
.actions-grid {
  display: grid;
  gap: 1rem;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 8px;
  text-decoration: none;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
  cursor: pointer;
  background: white;
}

.action-card:hover {
  border-color: #d1d5db;
  transform: translateY(-1px);
}

.action-card.create {
  border-left: 4px solid #10b981;
}

.action-card.manage {
  border-left: 4px solid #3b82f6;
}

.action-card.refresh {
  border-left: 4px solid #f59e0b;
}

.action-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  color: #6b7280;
}

.action-content {
  flex: 1;
}

.action-content h3 {
  margin: 0 0 0.25rem 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #1f2937;
}

.action-content p {
  margin: 0;
  font-size: 0.8rem;
  color: #6b7280;
}

.action-card .arrow {
  color: #9ca3af;
  transition: transform 0.2s;
}

.action-card:hover .arrow {
  transform: translateX(4px);
}

/* Sistema */
.system-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
}

.info-item i {
  color: #6b7280;
  font-size: 1.2rem;
}

.info-item strong {
  color: #374151;
}

.role-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  color: white;
}

.role-badge.super_admin {
  background: #dc2626;
}

.role-badge.admin {
  background: #ea580c;
}

.role-badge.profesional {
  background: #16a34a;
}

/* Estados */
.loading-container,
.error-container {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-left-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

.error-container i {
  font-size: 4rem;
  margin-bottom: 1rem;
  color: #ef4444;
}

/* Botones */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Responsive */
@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 1.5rem 1rem;
  }
  
  .header-content {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .header-actions {
    align-self: stretch;
  }
  
  .page-content {
    padding: 0 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .roles-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-section {
    padding: 1rem;
  }
}
</style>