<template>
  <div class="servidor-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-content">
        <h1 class="page-title">
          <i class="material-icons">settings_applications</i>
          Administración de Servidor
        </h1>
        <p class="page-description">
          Centro de control para la gestión de scripts, copias de seguridad y mantenimiento del servidor
        </p>
      </div>
      
      <div class="header-actions">
        <button 
          @click="refreshData" 
          :disabled="isRefreshing"
          class="btn btn-outline refresh-btn"
        >
          <i class="material-icons" :class="{ 'spinning': isRefreshing }">refresh</i>
          {{ isRefreshing ? 'Actualizando...' : 'Actualizar Estado' }}
        </button>
      </div>
    </div>

    <!-- Estado general del sistema -->
    <div class="system-status-grid">
      <!-- Estado de Scripts -->
      <div class="status-card scripts-status">
        <div class="status-header">
          <div class="status-icon">
            <i class="material-icons">code</i>
          </div>
          <div class="status-info">
            <h3>Scripts del Sistema</h3>
            <p>Estado general de los scripts disponibles</p>
          </div>
        </div>
        
        <div class="status-metrics" v-if="scriptsStatus && scriptsStatus.length > 0">
          <div class="metric">
            <span class="metric-value">{{ totalScripts }}</span>
            <span class="metric-label">Scripts Disponibles</span>
          </div>
          <div class="metric">
            <span class="metric-value">{{ runningScripts }}</span>
            <span class="metric-label">En Ejecución</span>
          </div>
          <div class="metric">
            <span class="metric-value">{{ getLastExecutionTime('scripts') }}</span>
            <span class="metric-label">Última Ejecución</span>
          </div>
        </div>
        
        <div v-else class="loading-metrics">
          <i class="material-icons spinning">refresh</i>
          <span>Cargando estado...</span>
        </div>
        
        <div class="status-actions">
          <router-link to="/gestion-informacion/servidor/scripts" class="btn btn-primary">
            <i class="material-icons">play_arrow</i>
            Gestionar Scripts
          </router-link>
        </div>
      </div>

      
    </div>

    <!-- Accesos directos -->
    <div class="quick-actions-section">
      <h2 class="section-title">
        <i class="material-icons">flash_on</i>
        Acciones Rápidas
      </h2>
      
      <div class="quick-actions-grid">
        <!-- Ejecutar Backup -->
        <div class="quick-action-card backup-action">
          <div class="action-icon">
            <i class="material-icons">backup</i>
          </div>
          <div class="action-content">
            <h4>Crear Backup de BD</h4>
            <p>Generar una copia de seguridad completa de la base de datos PostgreSQL</p>
            <button 
              @click="executeBackup"
              :disabled="isExecutingBackup"
              class="btn btn-primary action-btn"
            >
              <i class="material-icons">play_arrow</i>
              {{ isExecutingBackup ? 'Ejecutando...' : 'Ejecutar Backup' }}
            </button>
          </div>
        </div>

        <!-- Actualizar Rutas -->
        <div class="quick-action-card routes-action">
          <div class="action-icon">
            <i class="material-icons">folder_open</i>
          </div>
          <div class="action-content">
            <h4>Actualizar Rutas de Directorios</h4>
            <p>Actualizar las rutas PRE y POST operación en las tablas de la base de datos</p>
            <button 
              @click="executeRouteUpdate"
              :disabled="isExecutingRoutes"
              class="btn btn-primary action-btn"
            >
              <i class="material-icons">refresh</i>
              {{ isExecutingRoutes ? 'Ejecutando...' : 'Actualizar Rutas' }}
            </button>
          </div>
        </div>

        <!-- Descargar Último Backup -->
        <div class="quick-action-card download-action">
          <div class="action-icon">
            <i class="material-icons">download</i>
          </div>
          <div class="action-content">
            <h4>Descargar Último Backup</h4>
            <p>Descargar el archivo de backup más reciente en formato ZIP</p>
            <button 
              @click="downloadLatestBackup"
              :disabled="!hasBackups || isDownloading"
              class="btn btn-secondary action-btn"
            >
              <i class="material-icons">file_download</i>
              {{ isDownloading ? 'Descargando...' : 'Descargar' }}
            </button>
          </div>
        </div>

        <!-- Ver Historial -->
        <div class="quick-action-card history-action">
          <div class="action-icon">
            <i class="material-icons">history</i>
          </div>
          <div class="action-content">
            <h4>Ver Historial de Ejecuciones</h4>
            <p>Consultar el historial completo de ejecuciones de scripts</p>
            <router-link to="/gestion-informacion/servidor/scripts" class="btn btn-outline action-btn">
              <i class="material-icons">visibility</i>
              Ver Historial
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Actividad reciente -->
    <div class="recent-activity-section">
      <h2 class="section-title">
        <i class="material-icons">schedule</i>
        Actividad Reciente
      </h2>
      
      <div class="activity-content">
        <div v-if="recentExecutions && recentExecutions.length > 0" class="executions-list">
          <div 
            v-for="execution in recentExecutions" 
            :key="execution.id"
            class="execution-item"
          >
            <div class="execution-icon">
              <i class="material-icons">
                {{ execution.script_name === 'backup_db' ? 'backup' : 'folder_open' }}
              </i>
            </div>
            
            <div class="execution-info">
              <h4 class="execution-title">{{ getScriptDisplayName(execution.script_name) }}</h4>
              <p class="execution-meta">
                <span class="execution-user">{{ execution.user_name || 'Sistema' }}</span>
                <span class="execution-separator">•</span>
                <span class="execution-time">{{ formatRelativeTime(execution.created_at) }}</span>
              </p>
            </div>
            
            <div class="execution-status">
              <span 
                class="status-badge"
                :style="{ backgroundColor: getStatusColor(execution.status) }"
              >
                {{ getStatusText(execution.status) }}
              </span>
            </div>
          </div>
          
          <div class="view-all-link">
            <router-link to="/gestion-informacion/servidor/scripts" class="btn btn-outline btn-sm">
              Ver todas las ejecuciones
              <i class="material-icons">arrow_forward</i>
            </router-link>
          </div>
        </div>
        
        <div v-else-if="!isLoadingExecutions" class="no-activity">
          <i class="material-icons">inbox</i>
          <h3>No hay actividad reciente</h3>
          <p>Ejecute un script para ver la actividad aquí</p>
        </div>
        
        <div v-if="isLoadingExecutions" class="loading-activity">
          <i class="material-icons spinning">refresh</i>
          <span>Cargando actividad...</span>
        </div>
      </div>
    </div>

    <!-- Información del sistema -->
    <div class="system-info-section">
      <h2 class="section-title">
        <i class="material-icons">info</i>
        Información del Sistema
      </h2>
      
      <div class="info-grid">
        <div class="info-card">
          <h4>Scripts Disponibles</h4>
          <ul class="scripts-list">
            <li>
              <i class="material-icons">backup</i>
              <span>Copia de Seguridad de Base de Datos</span>
            </li>
            <li>
              <i class="material-icons">folder_open</i>
              <span>Actualizar Rutas Base Directorios</span>
            </li>
          </ul>
        </div>
        
        <div class="info-card">
          <h4>Características</h4>
          <ul class="features-list">
            <li>✓ Ejecución asíncrona de scripts</li>
            <li>✓ Monitoreo en tiempo real</li>
            <li>✓ Historial completo de ejecuciones</li>
            <li>✓ Descarga automática de backups</li>
            <li>✓ Limpieza automática de directorios</li>
          </ul>
        </div>
        
        <div class="info-card">
          <h4>Notas Importantes</h4>
          <ul class="notes-list">
            <li>• Los scripts se ejecutan de forma asíncrona</li>
            <li>• Los backups incluyen comandos DROP/CREATE</li>
            <li>• La restauración sobrescribe la BD actual</li>
            <li>• Se requiere PostgreSQL en el PATH para restaurar</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Mensaje de servicio no disponible -->
    <div v-if="serviceError" class="service-error">
      <div class="error-content">
        <i class="material-icons">warning</i>
        <h3>Servicio no disponible</h3>
        <p>{{ serviceError }}</p>
        <button @click="refreshData" class="btn btn-primary">
          <i class="material-icons">refresh</i>
          Reintentar
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

// ✅ IMPORTAR EL SERVICIO REAL (no el mock)
import scriptsService from '@/api/scripts'

export default defineComponent({
  name: 'ServidorDashboard',
  
  setup() {
    const router = useRouter()
    
    // Estado reactivo
    const isRefreshing = ref(false)
    const isExecutingBackup = ref(false)
    const isExecutingRoutes = ref(false)
    const isDownloading = ref(false)
    const isLoadingExecutions = ref(false)
    const serviceError = ref<string | null>(null)
    
    const scriptsStatus = ref<any[]>([])
    const backupStatus = ref<any | null>(null)
    const recentExecutions = ref<any[]>([])
    
    // Computed
    const totalScripts = computed(() => scriptsStatus.value?.length || 0)
    
    const runningScripts = computed(() => {
      if (!scriptsStatus.value || !Array.isArray(scriptsStatus.value)) return 0
      return scriptsStatus.value.filter(script => 
        script?.last_execution?.status === 'running'
      ).length
    })
    
    const hasBackups = computed(() => {
      return backupStatus.value && backupStatus.value.backup_files_count > 0
    })
    
    // Métodos principales
    const refreshData = async () => {
      if (isRefreshing.value) return
      
      try {
        isRefreshing.value = true
        serviceError.value = null
        
        await Promise.all([
          loadScriptsStatus(),
          loadBackupStatus(),
          loadRecentExecutions()
        ])
      } catch (error: any) {
        console.error('Error refrescando datos:', error)
        serviceError.value = error.message || 'Error al conectar con el servicio de scripts'
      } finally {
        isRefreshing.value = false
      }
    }
    
    const loadScriptsStatus = async () => {
      try {
        scriptsStatus.value = await scriptsService.getScriptsStatusSummary()
      } catch (error: any) {
        console.error('Error cargando estado de scripts:', error)
        scriptsStatus.value = []
      }
    }
    
    const loadBackupStatus = async () => {
      try {
        backupStatus.value = await scriptsService.getBackupStatus()
      } catch (error: any) {
        console.error('Error cargando estado de backup:', error)
        backupStatus.value = null
      }
    }
    
    const loadRecentExecutions = async () => {
      try {
        isLoadingExecutions.value = true
        const response = await scriptsService.getExecutions()
        recentExecutions.value = response?.results || []
      } catch (error: any) {
        console.error('Error cargando ejecuciones recientes:', error)
        recentExecutions.value = []
      } finally {
        isLoadingExecutions.value = false
      }
    }
    
    const executeBackup = async () => {
      if (isExecutingBackup.value) return
      
      try {
        isExecutingBackup.value = true
        
        await scriptsService.executeScript('backup_db')
        alert('Backup iniciado correctamente.')
        
        await refreshData()
        router.push('/gestion-informacion/servidor/scripts')
        
      } catch (error: any) {
        console.error('Error ejecutando backup:', error)
        alert(`Error: ${error.message}`)
      } finally {
        isExecutingBackup.value = false
      }
    }
    
    const executeRouteUpdate = async () => {
      if (isExecutingRoutes.value) return
      
      try {
        isExecutingRoutes.value = true
        
        await scriptsService.executeScript('llenar_datos')
        alert('Actualización de rutas iniciada correctamente.')
        
        await refreshData()
        router.push('/gestion-informacion/servidor/scripts')
        
      } catch (error: any) {
        console.error('Error ejecutando actualización de rutas:', error)
        alert(`Error: ${error.message}`)
      } finally {
        isExecutingRoutes.value = false
      }
    }
    
const downloadLatestBackup = async () => {
  if (isDownloading.value || !hasBackups.value) return
  
  try {
    isDownloading.value = true
    
    const { blob, filename } = await scriptsService.downloadLatestBackupZip()
    
    // ✅ ACTIVAR DESCARGA MANUAL:
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    console.log('✅ Backup descargado:', filename)
    
  } catch (error: any) {
    console.error('Error descargando backup:', error)
    alert(`Error al descargar el backup: ${error.message || error}`)
  } finally {
    isDownloading.value = false
  }
}
    
    // Métodos de utilidad
    const getLastExecutionTime = (type: 'scripts' | 'backup') => {
      try {
        if (type === 'backup') {
          if (!backupStatus.value?.last_execution) return 'Nunca'
          return formatRelativeTime(backupStatus.value.last_execution.created_at)
        } else {
          if (!scriptsStatus.value || !Array.isArray(scriptsStatus.value)) return 'Nunca'
          
          const mostRecent = scriptsStatus.value
            .map(s => s?.last_execution)
            .filter(e => e)
            .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0]
          
          return mostRecent ? formatRelativeTime(mostRecent.created_at) : 'Nunca'
        }
      } catch (error) {
        console.error('Error getting last execution time:', error)
        return 'Error'
      }
    }
    
    const getStatusColor = (status: string) => {
      return scriptsService.getStatusColor(status)
    }
    
    const getStatusText = (status: string) => {
      return scriptsService.getStatusText(status)
    }
    
    const getScriptDisplayName = (scriptName: string) => {
      return scriptsService.getScriptDisplayName(scriptName)
    }
    
    const formatRelativeTime = (dateString: string) => {
      try {
        const date = new Date(dateString)
        const now = new Date()
        const diffMs = now.getTime() - date.getTime()
        const diffMins = Math.floor(diffMs / (1000 * 60))
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
        
        if (diffMins < 1) {
          return 'Hace un momento'
        } else if (diffMins < 60) {
          return `Hace ${diffMins} min`
        } else if (diffHours < 24) {
          return `Hace ${diffHours} h`
        } else if (diffDays < 7) {
          return `Hace ${diffDays} día${diffDays > 1 ? 's' : ''}`
        } else {
          return date.toLocaleDateString('es-ES')
        }
      } catch (error) {
        console.error('Error formatting date:', error)
        return 'Fecha inválida'
      }
    }
    
    // Lifecycle
    onMounted(() => {
      refreshData()
    })
    
    return {
      // Estado
      isRefreshing,
      isExecutingBackup,
      isExecutingRoutes,
      isDownloading,
      isLoadingExecutions,
      serviceError,
      scriptsStatus,
      backupStatus,
      recentExecutions,
      totalScripts,
      runningScripts,
      hasBackups,
      
      // Métodos
      refreshData,
      executeBackup,
      executeRouteUpdate,
      downloadLatestBackup,
      
      // Utilidades
      getLastExecutionTime,
      getStatusColor,
      getStatusText,
      getScriptDisplayName,
      formatRelativeTime
    }
  }
})
</script>

<style scoped>
.servidor-dashboard {
  padding: 0;
}

/* Header */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding: 0 0.5rem;
}

.header-content {
  flex: 1;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 0.5rem;
  font-size: 1.75rem;
  font-weight: 600;
  color: #1a202c;
}

.page-description {
  margin: 0;
  color: #64748b;
  font-size: 1rem;
  line-height: 1.5;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Estado del sistema */
.system-status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.status-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  transition: transform 0.2s;
}

.status-card:hover {
  transform: translateY(-2px);
}

.status-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.status-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.scripts-status .status-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.backup-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.status-icon i {
  font-size: 2rem;
}

.status-info {
  flex: 1;
}

.status-info h3 {
  margin: 0 0 0.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
}

.status-info p {
  margin: 0;
  color: #64748b;
  line-height: 1.5;
}

.status-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.metric {
  text-align: center;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.metric-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 0.25rem;
}

.metric-label {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
}

.loading-metrics {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
  color: #64748b;
  margin-bottom: 1.5rem;
}

.status-actions {
  display: flex;
  justify-content: center;
}

/* Acciones rápidas */
.quick-actions-section {
  margin-bottom: 3rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 1.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.quick-action-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s;
}

.quick-action-card:hover {
  transform: translateY(-2px);
}

.action-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 1rem;
  flex-shrink: 0;
}

.backup-action .action-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.routes-action .action-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.download-action .action-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.history-action .action-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.action-icon i {
  font-size: 1.5rem;
}

.action-content {
  flex: 1;
}

.action-content h4 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #1a202c;
}

.action-content p {
  margin: 0 0 1rem;
  color: #64748b;
  font-size: 0.875rem;
  line-height: 1.5;
}

.action-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
}

/* Actividad reciente */
.recent-activity-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 3rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.executions-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.execution-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  transition: background-color 0.2s;
}

.execution-item:hover {
  background: #f1f5f9;
}

.execution-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  flex-shrink: 0;
}

.execution-info {
  flex: 1;
  min-width: 0;
}

.execution-title {
  margin: 0 0 0.25rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: #1a202c;
}

.execution-meta {
  margin: 0;
  font-size: 0.75rem;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.execution-separator {
  opacity: 0.5;
}

.execution-status {
  flex-shrink: 0;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  color: white;
  font-size: 0.75rem;
  font-weight: 500;
}

.view-all-link {
  margin-top: 1rem;
  text-align: center;
}

.no-activity,
.loading-activity {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #64748b;
  text-align: center;
}

.no-activity i,
.loading-activity i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.no-activity h3 {
  margin: 0 0 0.5rem;
  color: #374151;
}

/* Información del sistema */
.system-info-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 3rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.info-card {
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.info-card h4 {
  margin: 0 0 1rem;
  font-size: 1rem;
  font-weight: 600;
  color: #1a202c;
}

.scripts-list,
.features-list,
.notes-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.scripts-list li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #4a5568;
  font-size: 0.875rem;
}

.scripts-list i {
  color: #64748b;
}

.features-list li,
.notes-list li {
  color: #4a5568;
  font-size: 0.875rem;
  line-height: 1.5;
}

/* Error de servicio */
.service-error {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #fecaca;
  background: #fef2f2;
}

.error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  color: #dc2626;
}

.error-content i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-content h3 {
  margin: 0 0 0.5rem;
  color: #991b1b;
}

.error-content p {
  margin: 0 0 1.5rem;
  color: #7f1d1d;
}

/* Botones */
.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
  font-size: 0.875rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-sm {
  padding: 0.5rem 0.75rem;
  font-size: 0.8rem;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-secondary {
  background: #64748b;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #475569;
}

.btn-outline {
  background: transparent;
  color: #64748b;
  border-color: #d1d5db;
}

.btn-outline:hover:not(:disabled) {
  background: #f8fafc;
  border-color: #9ca3af;
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .header-actions {
    width: 100%;
    justify-content: stretch;
  }
  
  .system-status-grid {
    grid-template-columns: 1fr;
  }
  
  .status-metrics {
    grid-template-columns: 1fr;
  }
  
  .quick-actions-grid {
    grid-template-columns: 1fr;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .execution-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  
  .execution-status {
    align-self: flex-end;
  }
}
</style>