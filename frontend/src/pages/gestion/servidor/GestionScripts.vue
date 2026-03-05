<template>
  <div class="gestion-scripts">
    <!-- Header con título y resumen -->
    <div class="scripts-header">
      <div class="header-content">
        <h1 class="page-title">
          <i class="material-icons">code</i>
          Gestión de Scripts del Servidor
        </h1>
        <p class="page-description">
          Ejecute scripts de mantenimiento y administración del sistema de forma controlada
        </p>
      </div>
      
      <!-- Botón de actualizar -->
      <div class="header-actions">
        <button 
          @click="refreshData" 
          :disabled="isRefreshing"
          class="btn btn-outline refresh-btn"
        >
          <i class="material-icons" :class="{ 'spinning': isRefreshing }">refresh</i>
          {{ isRefreshing ? 'Actualizando...' : 'Actualizar' }}
        </button>
      </div>
    </div>

    <!-- Tarjetas de scripts disponibles -->
    <div class="scripts-grid">
      <!-- Script 1: Backup de Base de Datos -->
      <div class="script-card">
        <div class="script-header">
          <div class="script-icon backup-icon">
            <i class="material-icons">backup</i>
          </div>
          <div class="script-info">
            <h3 class="script-title">Copia de Seguridad de Base de Datos</h3>
            <p class="script-description">
              Genera una copia de seguridad completa de la base de datos PostgreSQL
            </p>
          </div>
        </div>
        
        <div class="script-stats">
          <div class="stat">
            <span class="stat-label">Última ejecución:</span>
            <span class="stat-value">
              {{ getLastExecutionText('backup_db') }}
            </span>
          </div>
          <div class="stat">
            <span class="stat-label">Estado:</span>
            <span 
              class="stat-value status-badge"
              :style="{ backgroundColor: getStatusColor(getLastExecutionStatus('backup_db')) }"
            >
              {{ getStatusText(getLastExecutionStatus('backup_db')) }}
            </span>
          </div>
        </div>
        
        <div class="script-actions">
          <button 
            @click="executeScript('backup_db')"
            :disabled="isExecuting['backup_db'] || isRefreshing"
            class="btn btn-primary action-btn"
          >
            <i class="material-icons">play_arrow</i>
            {{ isExecuting['backup_db'] ? 'Ejecutando...' : 'Ejecutar Backup' }}
          </button>
          
          <button 
            @click="downloadLatestBackup"
            :disabled="!hasBackups || isDownloading"
            class="btn btn-secondary action-btn"
          >
            <i class="material-icons">download</i>
            {{ isDownloading ? 'Descargando...' : 'Descargar Último' }}
          </button>
        </div>
        
        <!-- Instrucciones de uso del backup -->
        <div class="backup-instructions" v-if="showInstructions.backup">
          <div class="instructions-header">
            <h4>Instrucciones para Restaurar Backup</h4>
            <button @click="showInstructions.backup = false" class="close-btn">
              <i class="material-icons">close</i>
            </button>
          </div>
          <div class="instructions-content">
            <ol>
              <li>
                <strong>Configurar Variables de Entorno (solo una vez):</strong>
                <div class="code-block">
                  Agregar al PATH: <code>C:\Program Files\PostgreSQL\16\bin</code>
                </div>
              </li>
              <li>
                <strong>Abrir Símbolo del Sistema (CMD) como Administrador</strong>
              </li>
              <li>
                <strong>Ejecutar comando de restauración:</strong>
                <div class="code-block">
                  <code>psql -U postgres -h localhost -p 5432 -d postgres -f "RUTA_AL_ARCHIVO_BACKUP.sql"</code>
                </div>
              </li>
              <li>
                <strong>Ingresar la contraseña del usuario postgres cuando se solicite</strong>
              </li>
              <li>
                <strong>Para restaurar completamente:</strong>
                <ul>
                  <li>Eliminar la base de datos actual si existe</li>
                  <li>Ejecutar los pasos anteriores</li>
                  <li>El backup incluye comandos CREATE y DROP automáticamente</li>
                </ul>
              </li>
            </ol>
            <div class="warning-note">
              <i class="material-icons">warning</i>
              <strong>Precaución:</strong> La restauración sobrescribirá la base de datos actual. 
              Asegúrese de tener un backup antes de proceder.
            </div>
          </div>
        </div>
      </div>

      <!-- Script 2: Actualizar Rutas de Directorios -->
      <div class="script-card">
        <div class="script-header">
          <div class="script-icon routes-icon">
            <i class="material-icons">folder_open</i>
          </div>
          <div class="script-info">
            <h3 class="script-title">Actualizar Rutas Base Directorios</h3>
            <p class="script-description">
              Actualiza las rutas de directorios PRE y POST operación en las tablas correspondientes
            </p>
          </div>
        </div>
        
        <div class="script-stats">
          <div class="stat">
            <span class="stat-label">Última ejecución:</span>
            <span class="stat-value">
              {{ getLastExecutionText('llenar_datos') }}
            </span>
          </div>
          <div class="stat">
            <span class="stat-label">Estado:</span>
            <span 
              class="stat-value status-badge"
              :style="{ backgroundColor: getStatusColor(getLastExecutionStatus('llenar_datos')) }"
            >
              {{ getStatusText(getLastExecutionStatus('llenar_datos')) }}
            </span>
          </div>
        </div>
        
        <div class="script-actions">
          <button 
            @click="executeScript('llenar_datos')"
            :disabled="isExecuting['llenar_datos'] || isRefreshing"
            class="btn btn-primary action-btn"
          >
            <i class="material-icons">play_arrow</i>
            {{ isExecuting['llenar_datos'] ? 'Ejecutando...' : 'Actualizar Rutas' }}
          </button>
          
          <button 
            @click="showInstructions.routes = !showInstructions.routes"
            class="btn btn-outline action-btn"
          >
            <i class="material-icons">info</i>
            {{ showInstructions.routes ? 'Ocultar Info' : 'Ver Detalles' }}
          </button>
        </div>
        
        <!-- Información adicional del script de rutas -->
        <div class="routes-info" v-if="showInstructions.routes">
          <div class="info-header">
            <h4>Detalles del Proceso</h4>
            <button @click="showInstructions.routes = false" class="close-btn">
              <i class="material-icons">close</i>
            </button>
          </div>
          <div class="info-content">
            <p><strong>Este script realiza las siguientes acciones:</strong></p>
            <ul>
              <li>Escanea el sistema de archivos en busca de directorios de municipios</li>
              <li>Actualiza la tabla <code>path_dir_pre</code> con rutas de preoperación</li>
              <li>Actualiza la tabla <code>path_dir_post</code> con rutas de postoperación</li>
              <li>Valida que los códigos de municipio existan en la base de datos</li>
              <li>Limpia las tablas antes de insertar nuevos datos</li>
            </ul>
            
            <div class="info-note">
              <i class="material-icons">info</i>
              <strong>Nota:</strong> Este proceso puede tomar varios minutos dependiendo 
              del tamaño del sistema de archivos y la disponibilidad de la red.
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Historial de ejecuciones recientes -->
    <div class="executions-history">
      <div class="history-header">
        <h2 class="section-title">
          <i class="material-icons">history</i>
          Historial de Ejecuciones Recientes
        </h2>
        
        <div class="history-filters">
          <select v-model="selectedScript" @change="loadExecutions" class="filter-select">
            <option value="">Todos los scripts</option>
            <option value="backup_db">Backup de Base de Datos</option>
            <option value="llenar_datos">Actualizar Rutas</option>
          </select>
          
          <select v-model="selectedStatus" @change="loadExecutions" class="filter-select">
            <option value="">Todos los estados</option>
            <option value="completed">Completados</option>
            <option value="failed">Fallidos</option>
            <option value="running">En ejecución</option>
            <option value="pending">Pendientes</option>
          </select>
        </div>
      </div>
      
      <div class="executions-table" v-if="executions.length > 0">
        <table class="table">
          <thead>
            <tr>
              <th>Script</th>
              <th>Estado</th>
              <th>Usuario</th>
              <th>Iniciado</th>
              <th>Duración</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="execution in executions" :key="execution.id">
              <td>
                <div class="script-name">
                  <i class="material-icons">
                    {{ execution.script_name === 'backup_db' ? 'backup' : 'folder_open' }}
                  </i>
                  {{ getScriptDisplayName(execution.script_name) }}
                </div>
              </td>
              <td>
                <span 
                  class="status-badge small"
                  :style="{ backgroundColor: getStatusColor(execution.status) }"
                >
                  {{ getStatusText(execution.status) }}
                </span>
              </td>
              <td>{{ execution.user_name || '--' }}</td>
              <td>{{ formatDateTime(execution.started_at) }}</td>
              <td>{{ formatDuration(execution.duration_seconds) }}</td>
              <td>
                <div class="execution-actions">
                  <button 
                    @click="viewExecutionDetails(execution)"
                    class="btn btn-sm btn-outline"
                    title="Ver detalles"
                  >
                    <i class="material-icons">visibility</i>
                  </button>
                  
                  <button 
                    v-if="execution.status === 'failed'"
                    @click="retryExecution(execution.id)"
                    :disabled="isRetrying[execution.id]"
                    class="btn btn-sm btn-primary"
                    title="Reintentar"
                  >
                    <i class="material-icons">replay</i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <!-- Paginación -->
        <div class="pagination" v-if="totalPages > 1">
          <button 
            @click="changePage(currentPage - 1)"
            :disabled="currentPage <= 1"
            class="btn btn-outline btn-sm"
          >
            <i class="material-icons">chevron_left</i>
          </button>
          
          <span class="page-info">
            Página {{ currentPage }} de {{ totalPages }}
          </span>
          
          <button 
            @click="changePage(currentPage + 1)"
            :disabled="currentPage >= totalPages"
            class="btn btn-outline btn-sm"
          >
            <i class="material-icons">chevron_right</i>
          </button>
        </div>
      </div>
      
      <div v-else-if="!isLoadingExecutions" class="no-executions">
        <i class="material-icons">inbox</i>
        <p>No se encontraron ejecuciones</p>
      </div>
      
      <div v-if="isLoadingExecutions" class="loading-executions">
        <i class="material-icons spinning">refresh</i>
        <p>Cargando historial...</p>
      </div>
    </div>

    <!-- Modal de detalles de ejecución -->
    <div v-if="selectedExecution" class="modal-overlay" @click="closeExecutionDetails">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Detalles de Ejecución</h3>
          <button @click="closeExecutionDetails" class="modal-close">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="execution-details">
            <div class="detail-row">
              <label>Script:</label>
              <span>{{ getScriptDisplayName(selectedExecution.script_name) }}</span>
            </div>
            
            <div class="detail-row">
              <label>Estado:</label>
              <span 
                class="status-badge"
                :style="{ backgroundColor: getStatusColor(selectedExecution.status) }"
              >
                {{ getStatusText(selectedExecution.status) }}
              </span>
            </div>
            
            <div class="detail-row">
              <label>Usuario:</label>
              <span>{{ selectedExecution.user_name || '--' }}</span>
            </div>
            
            <div class="detail-row">
              <label>Creado:</label>
              <span>{{ formatDateTime(selectedExecution.created_at) }}</span>
            </div>
            
            <div class="detail-row" v-if="selectedExecution.started_at">
              <label>Iniciado:</label>
              <span>{{ formatDateTime(selectedExecution.started_at) }}</span>
            </div>
            
            <div class="detail-row" v-if="selectedExecution.completed_at">
              <label>Completado:</label>
              <span>{{ formatDateTime(selectedExecution.completed_at) }}</span>
            </div>
            
            <div class="detail-row" v-if="selectedExecution.duration_seconds">
              <label>Duración:</label>
              <span>{{ formatDuration(selectedExecution.duration_seconds) }}</span>
            </div>
            
            <div class="detail-section" v-if="selectedExecution.output_log">
              <label>Log de Salida:</label>
              <pre class="log-output">{{ selectedExecution.output_log }}</pre>
            </div>
            
            <div class="detail-section" v-if="selectedExecution.error_message">
              <label>Mensaje de Error:</label>
              <pre class="error-output">{{ selectedExecution.error_message }}</pre>
            </div>
            
            <div class="detail-section" v-if="selectedExecution.backup_files && selectedExecution.backup_files.length > 0">
              <label>Archivos Generados:</label>
              <div class="backup-files">
                <div 
                  v-for="file in selectedExecution.backup_files" 
                  :key="file.id"
                  class="backup-file"
                >
                  <i class="material-icons">insert_drive_file</i>
                  <span class="file-name">{{ file.filename }}</span>
                  <span class="file-size">({{ file.file_size_mb }} MB)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue'
import scriptsService from '@/api/scripts'
import type { ScriptExecution, ScriptStatus } from '@/api/scripts'

export default defineComponent({
  name: 'GestionScripts',
  
  setup() {
    // Estado reactivo
    const isRefreshing = ref(false)
    const isExecuting = ref({
      backup_db: false,
      llenar_datos: false
    })
    const isDownloading = ref(false)
    const isRetrying = ref<Record<string, boolean>>({})
    const isLoadingExecutions = ref(false)
    
    const scriptsStatus = ref<ScriptStatus[]>([])
    const executions = ref<ScriptExecution[]>([])
    const selectedExecution = ref<ScriptExecution | null>(null)
    
    const showInstructions = ref({
      backup: false,
      routes: false
    })
    
    // Filtros y paginación
    const selectedScript = ref('')
    const selectedStatus = ref('')
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalExecutions = ref(0)
    
    // Computed
    const totalPages = computed(() => Math.ceil(totalExecutions.value / pageSize.value))
    
    const hasBackups = computed(() => {
      const backupStatus = scriptsStatus.value.find(s => s.script_name === 'backup_db')
      return backupStatus && backupStatus.successful_executions > 0
    })
    
    // Métodos principales
    const refreshData = async () => {
      if (isRefreshing.value) return
      
      try {
        isRefreshing.value = true
        await Promise.all([
          loadScriptsStatus(),
          loadExecutions()
        ])
      } catch (error) {
        console.error('Error refrescando datos:', error)
      } finally {
        isRefreshing.value = false
      }
    }
    
    const loadScriptsStatus = async () => {
      try {
        scriptsStatus.value = await scriptsService.getScriptsStatusSummary()
      } catch (error) {
        console.error('Error cargando estado de scripts:', error)
      }
    }
    
    const loadExecutions = async () => {
      try {
        isLoadingExecutions.value = true
        const response = await scriptsService.getExecutions(currentPage.value, pageSize.value)
        
        // Filtrar por script y estado si están seleccionados
        let filteredExecutions = response.results
        
        if (selectedScript.value) {
          filteredExecutions = filteredExecutions.filter(e => e.script_name === selectedScript.value)
        }
        
        if (selectedStatus.value) {
          filteredExecutions = filteredExecutions.filter(e => e.status === selectedStatus.value)
        }
        
        executions.value = filteredExecutions
        totalExecutions.value = response.count
      } catch (error) {
        console.error('Error cargando ejecuciones:', error)
      } finally {
        isLoadingExecutions.value = false
      }
    }
    
    const executeScript = async (scriptName: 'backup_db' | 'llenar_datos') => {
      if (isExecuting.value[scriptName]) return
      
      try {
        isExecuting.value[scriptName] = true
        
        const execution = await scriptsService.executeScript(scriptName)
        console.log(`Script ${scriptName} iniciado:`, execution)
        
        // Mostrar notificación de éxito
        alert(`Script "${scriptsService.getScriptDisplayName(scriptName)}" iniciado correctamente. 
Puede ver el progreso en el historial de ejecuciones.`)
        
        // Actualizar datos
        await refreshData()
        
        // Polling para actualizar el estado cada 5 segundos
        const pollInterval = setInterval(async () => {
          try {
            const updatedExecution = await scriptsService.getExecution(execution.id)
            
            if (updatedExecution.status === 'completed' || updatedExecution.status === 'failed') {
              clearInterval(pollInterval)
              await refreshData()
              
              // Mostrar notificación del resultado
              if (updatedExecution.status === 'completed') {
                alert(`Script "${scriptsService.getScriptDisplayName(scriptName)}" completado exitosamente.`)
                
                // Si es un backup y se completó, mostrar instrucciones
                if (scriptName === 'backup_db') {
                  showInstructions.value.backup = true
                }
              } else {
                alert(`Script "${scriptsService.getScriptDisplayName(scriptName)}" falló. Verifique los detalles en el historial.`)
              }
            }
          } catch (error) {
            console.error('Error en polling:', error)
            clearInterval(pollInterval)
          }
        }, 5000)
        
      } catch (error: any) {
        console.error(`Error ejecutando script ${scriptName}:`, error)
        alert(`Error al ejecutar el script: ${error.message || error}`)
      } finally {
        isExecuting.value[scriptName] = false
      }
    }
    
    const downloadLatestBackup = async () => {
      if (isDownloading.value) return
      
      try {
        isDownloading.value = true
        
        const { blob, filename } = await scriptsService.downloadLatestBackupZip()
        scriptsService.downloadFile(blob, filename)
        
        // Mostrar instrucciones después de la descarga
        setTimeout(() => {
          showInstructions.value.backup = true
        }, 1000)
        
      } catch (error: any) {
        console.error('Error descargando backup:', error)
        alert(`Error al descargar el backup: ${error.message || error}`)
      } finally {
        isDownloading.value = false
      }
    }
    
    const retryExecution = async (executionId: string) => {
      if (isRetrying.value[executionId]) return
      
      try {
        isRetrying.value[executionId] = true
        
        const newExecution = await scriptsService.retryExecution(executionId)
        console.log('Ejecución reintentada:', newExecution)
        
        alert('Ejecución reintentada correctamente. Puede ver el progreso en el historial.')
        await refreshData()
        
      } catch (error: any) {
        console.error('Error reintentando ejecución:', error)
        alert(`Error al reintentar la ejecución: ${error.message || error}`)
      } finally {
        isRetrying.value[executionId] = false
      }
    }
    
    const changePage = (page: number) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadExecutions()
      }
    }
    
    const viewExecutionDetails = (execution: ScriptExecution) => {
      selectedExecution.value = execution
    }
    
    const closeExecutionDetails = () => {
      selectedExecution.value = null
    }
    
    // Métodos de utilidad
    const getLastExecutionText = (scriptName: string) => {
      const script = scriptsStatus.value.find(s => s.script_name === scriptName)
      if (!script || !script.last_execution) {
        return 'Nunca ejecutado'
      }
      
      const date = new Date(script.last_execution.created_at)
      return date.toLocaleString('es-ES')
    }
    
    const getLastExecutionStatus = (scriptName: string) => {
      const script = scriptsStatus.value.find(s => s.script_name === scriptName)
      return script?.last_execution?.status || 'unknown'
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
    
    const formatDateTime = (dateString?: string) => {
      if (!dateString) return '--'
      return new Date(dateString).toLocaleString('es-ES')
    }
    
    const formatDuration = (seconds?: number) => {
      return scriptsService.formatDuration(seconds)
    }
    
    // Lifecycle
    onMounted(() => {
      refreshData()
    })
    
    return {
      // Estado
      isRefreshing,
      isExecuting,
      isDownloading,
      isRetrying,
      isLoadingExecutions,
      scriptsStatus,
      executions,
      selectedExecution,
      showInstructions,
      selectedScript,
      selectedStatus,
      currentPage,
      totalPages,
      hasBackups,
      
      // Métodos
      refreshData,
      executeScript,
      downloadLatestBackup,
      retryExecution,
      changePage,
      viewExecutionDetails,
      closeExecutionDetails,
      loadExecutions,
      
      // Utilidades
      getLastExecutionText,
      getLastExecutionStatus,
      getStatusColor,
      getStatusText,
      getScriptDisplayName,
      formatDateTime,
      formatDuration
    }
  }
})
</script>

<style scoped>
.gestion-scripts {
  padding: 0;
}

/* Header */
.scripts-header {
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

/* Scripts Grid */
.scripts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.script-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  transition: all 0.2s;
}

.script-card:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.script-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.script-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.backup-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.routes-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.script-icon i {
  font-size: 2rem;
}

.script-info {
  flex: 1;
}

.script-title {
  margin: 0 0 0.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
}

.script-description {
  margin: 0;
  color: #64748b;
  line-height: 1.5;
}

.script-stats {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  font-weight: 500;
  color: #4a5568;
}

.stat-value {
  font-weight: 600;
  color: #1a202c;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-badge.small {
  padding: 0.125rem 0.5rem;
  font-size: 0.75rem;
}

.script-actions {
  display: flex;
  gap: 0.75rem;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  font-weight: 500;
}

/* Instrucciones */
.backup-instructions,
.routes-info {
  margin-top: 1.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.instructions-header,
.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.instructions-header h4,
.info-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1a202c;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #64748b;
  padding: 0.25rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background: #e2e8f0;
}

.instructions-content,
.info-content {
  padding: 1rem;
}

.instructions-content ol {
  margin: 0 0 1rem;
  padding-left: 1.5rem;
}

.instructions-content li {
  margin-bottom: 1rem;
}

.code-block {
  margin: 0.5rem 0;
  padding: 0.5rem;
  background: #1a202c;
  color: #e2e8f0;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
}

.warning-note,
.info-note {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  margin-top: 1rem;
  border-radius: 8px;
}

.warning-note {
  background: #fef3c7;
  border: 1px solid #f59e0b;
  color: #92400e;
}

.info-note {
  background: #dbeafe;
  border: 1px solid #3b82f6;
  color: #1e40af;
}

.warning-note i,
.info-note i {
  color: inherit;
  margin-top: 0.125rem;
}

/* Historial */
.executions-history {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
}

.history-filters {
  display: flex;
  gap: 1rem;
}

.filter-select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  font-size: 0.875rem;
}

/* Tabla */
.executions-table {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th {
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.table td {
  padding: 0.75rem;
  border-bottom: 1px solid #f3f4f6;
  vertical-align: middle;
}

.script-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.execution-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

/* Paginación */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
}

.page-info {
  color: #64748b;
  font-size: 0.875rem;
}

/* Estados de carga */
.no-executions,
.loading-executions {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #64748b;
}

.no-executions i,
.loading-executions i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
}

.modal-close {
  background: none;
  border: none;
  cursor: pointer;
  color: #64748b;
  padding: 0.5rem;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.modal-close:hover {
  background: #f1f5f9;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.execution-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.detail-row label {
  font-weight: 500;
  color: #4a5568;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-section label {
  font-weight: 500;
  color: #4a5568;
}

.log-output,
.error-output {
  padding: 1rem;
  background: #1a202c;
  color: #e2e8f0;
  border-radius: 6px;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}

.error-output {
  background: #7f1d1d;
  color: #fecaca;
}

.backup-files {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.backup-file {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #f8fafc;
  border-radius: 6px;
}

.file-name {
  flex: 1;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
}

.file-size {
  color: #64748b;
  font-size: 0.875rem;
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
  .scripts-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .scripts-grid {
    grid-template-columns: 1fr;
  }
  
  .script-actions {
    flex-direction: column;
  }
  
  .history-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .history-filters {
    width: 100%;
    justify-content: stretch;
  }
  
  .filter-select {
    flex: 1;
  }
  
  .modal-content {
    margin: 1rem;
    max-height: calc(100vh - 2rem);
  }
}
</style>