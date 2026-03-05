<template>
  <div class="gestion-backups">
    <!-- Header -->
    <div class="backups-header">
      <div class="header-content">
        <h1 class="page-title">
          <i class="material-icons">backup</i>
          Gestión de Copias de Seguridad
        </h1>
        <p class="page-description">
          Administre las copias de seguridad de la base de datos, descargue archivos y monitoree el estado
        </p>
      </div>
      
      <div class="header-actions">
        <button 
          @click="refreshData" 
          :disabled="isRefreshing"
          class="btn btn-outline refresh-btn"
        >
          <i class="material-icons" :class="{ 'spinning': isRefreshing }">refresh</i>
          {{ isRefreshing ? 'Actualizando...' : 'Actualizar' }}
        </button>
        
        <button 
          @click="executeBackup"
          :disabled="isExecutingBackup"
          class="btn btn-primary"
        >
          <i class="material-icons">play_arrow</i>
          {{ isExecutingBackup ? 'Ejecutando...' : 'Nuevo Backup' }}
        </button>
      </div>
    </div>

    <!-- Estado general de backups -->
    <div class="backup-status-card">
      <div class="status-header">
        <h2 class="status-title">
          <i class="material-icons">dashboard</i>
          Estado General
        </h2>
      </div>
      
      <div class="status-grid" v-if="backupStatus">
        <div class="status-item">
          <div class="status-value">{{ backupStatus.total_executions }}</div>
          <div class="status-label">Total Ejecuciones</div>
        </div>
        
        <div class="status-item success">
          <div class="status-value">{{ backupStatus.successful_executions }}</div>
          <div class="status-label">Exitosas</div>
        </div>
        
        <div class="status-item error">
          <div class="status-value">{{ backupStatus.failed_executions }}</div>
          <div class="status-label">Fallidas</div>
        </div>
        
        <div class="status-item">
          <div class="status-value">{{ backupStatus.backup_files_count }}</div>
          <div class="status-label">Archivos de Backup</div>
        </div>
        
        <div class="status-item">
          <div class="status-value">{{ backupStatus.total_backup_size_mb.toFixed(1) }} MB</div>
          <div class="status-label">Tamaño Total</div>
        </div>
        
        <div class="status-item" v-if="backupStatus.last_execution">
          <div class="status-value">
            <span 
              class="status-badge"
              :style="{ backgroundColor: getStatusColor(backupStatus.last_execution.status) }"
            >
              {{ getStatusText(backupStatus.last_execution.status) }}
            </span>
          </div>
          <div class="status-label">Último Estado</div>
        </div>
      </div>
      
      <div v-else class="loading-status">
        <i class="material-icons spinning">refresh</i>
        <span>Cargando estado...</span>
      </div>
    </div>

    <!-- Acciones rápidas -->
    <div class="quick-actions">
      <div class="action-card download-card">
        <div class="action-header">
          <i class="material-icons">download</i>
          <h3>Descargar Último Backup</h3>
        </div>
        <p class="action-description">
          Descarga el archivo de backup más reciente en formato ZIP
        </p>
        <button 
          @click="downloadLatestBackup"
          :disabled="!hasBackups || isDownloading"
          class="btn btn-primary action-btn"
        >
          <i class="material-icons">file_download</i>
          {{ isDownloading ? 'Descargando...' : 'Descargar' }}
        </button>
      </div>
      
      <div class="action-card clean-card">
        <div class="action-header">
          <i class="material-icons">delete_sweep</i>
          <h3>Limpiar Directorio</h3>
        </div>
        <p class="action-description">
          Elimina todos los archivos de backup del servidor (irreversible)
        </p>
        <button 
          @click="showCleanConfirmation = true"
          :disabled="isCleaning"
          class="btn btn-danger action-btn"
        >
          <i class="material-icons">delete</i>
          {{ isCleaning ? 'Limpiando...' : 'Limpiar' }}
        </button>
      </div>
    </div>

    <!-- Lista de archivos de backup -->
    <div class="backup-files-section">
      <div class="section-header">
        <h2 class="section-title">
          <i class="material-icons">folder</i>
          Archivos de Backup Disponibles
        </h2>
        
        <div class="section-filters">
          <select v-model="sortBy" @change="sortFiles" class="filter-select">
            <option value="date_desc">Más recientes primero</option>
            <option value="date_asc">Más antiguos primero</option>
            <option value="size_desc">Mayor tamaño primero</option>
            <option value="size_asc">Menor tamaño primero</option>
            <option value="name_asc">Nombre A-Z</option>
            <option value="name_desc">Nombre Z-A</option>
          </select>
        </div>
      </div>
      
      <div v-if="sortedBackupFiles.length > 0" class="backup-files-grid">
        <div 
          v-for="file in sortedBackupFiles" 
          :key="file.id"
          class="backup-file-card"
        >
          <div class="file-header">
            <div class="file-icon">
              <i class="material-icons">insert_drive_file</i>
            </div>
            <div class="file-info">
              <h4 class="file-name">{{ file.filename }}</h4>
              <div class="file-meta">
                <span class="file-size">{{ file.file_size_mb }} MB</span>
                <span class="file-date">{{ formatDate(file.created_at) }}</span>
              </div>
            </div>
          </div>
          
          <div class="file-actions">
            <button 
              @click="downloadFile(file)"
              :disabled="isDownloadingFile[file.id]"
              class="btn btn-sm btn-primary"
              title="Descargar archivo"
            >
              <i class="material-icons">download</i>
              {{ isDownloadingFile[file.id] ? '...' : 'Descargar' }}
            </button>
            
            <button 
              @click="showFileDetails(file)"
              class="btn btn-sm btn-outline"
              title="Ver detalles"
            >
              <i class="material-icons">info</i>
              Detalles
            </button>
          </div>
        </div>
      </div>
      
      <div v-else-if="!isLoadingFiles" class="no-files">
        <i class="material-icons">folder_open</i>
        <h3>No hay archivos de backup</h3>
        <p>Ejecute un backup para generar archivos</p>
        <button 
          @click="executeBackup"
          :disabled="isExecutingBackup"
          class="btn btn-primary"
        >
          <i class="material-icons">play_arrow</i>
          Crear Primer Backup
        </button>
      </div>
      
      <div v-if="isLoadingFiles" class="loading-files">
        <i class="material-icons spinning">refresh</i>
        <span>Cargando archivos...</span>
      </div>
    </div>

    <!-- Instrucciones de restauración -->
    <div class="restoration-guide">
      <div class="guide-header">
        <h2 class="guide-title">
          <i class="material-icons">help_outline</i>
          Guía de Restauración de Backup
        </h2>
        <button 
          @click="showGuide = !showGuide"
          class="btn btn-outline btn-sm"
        >
          <i class="material-icons">{{ showGuide ? 'expand_less' : 'expand_more' }}</i>
          {{ showGuide ? 'Ocultar' : 'Mostrar' }}
        </button>
      </div>
      
      <div v-if="showGuide" class="guide-content">
        <div class="guide-section">
          <h4>Requisitos Previos (Solo una vez)</h4>
          <ol>
            <li>
              <strong>Instalar PostgreSQL:</strong> Asegúrese de tener PostgreSQL instalado en el sistema
            </li>
            <li>
              <strong>Configurar Variables de Entorno:</strong>
              <div class="code-block">
                Agregar al PATH del sistema: <code>C:\Program Files\PostgreSQL\16\bin</code>
              </div>
              <div class="note">
                <i class="material-icons">info</i>
                Reemplace "16" por su versión de PostgreSQL
              </div>
            </li>
          </ol>
        </div>
        
        <div class="guide-section">
          <h4>Proceso de Restauración</h4>
          <ol>
            <li>
              <strong>Descargar el archivo de backup</strong> desde esta interfaz
            </li>
            <li>
              <strong>Abrir Símbolo del Sistema (CMD)</strong> como Administrador
            </li>
            <li>
              <strong>Navegar al directorio</strong> donde descargó el archivo
            </li>
            <li>
              <strong>Ejecutar el comando de restauración:</strong>
              <div class="code-block">
                <code>psql -U postgres -h localhost -p 5432 -d postgres -f "NOMBRE_DEL_ARCHIVO.sql"</code>
              </div>
            </li>
            <li>
              <strong>Ingresar la contraseña</strong> del usuario postgres cuando se solicite
            </li>
          </ol>
        </div>
        
        <div class="guide-section">
          <h4>Ejemplo Completo</h4>
          <div class="code-block">
            <div># Ejemplo de restauración completa</div>
            <div>cd C:\Users\Usuario\Downloads</div>
            <div>psql -U postgres -h localhost -p 5432 -d postgres -f "gestion_dato_db_20241215_143022.sql"</div>
          </div>
        </div>
        
        <div class="warning-box">
          <i class="material-icons">warning</i>
          <div>
            <strong>¡IMPORTANTE!</strong>
            <p>
              La restauración sobrescribirá completamente la base de datos actual. 
              Asegúrese de hacer un backup de la base de datos actual antes de proceder 
              si contiene datos importantes.
            </p>
          </div>
        </div>
        
        <div class="tips-box">
          <i class="material-icons">lightbulb</i>
          <div>
            <strong>Consejos:</strong>
            <ul>
              <li>Los archivos .sql incluyen comandos DROP y CREATE automáticamente</li>
              <li>No es necesario crear la base de datos manualmente</li>
              <li>El proceso puede tomar varios minutos dependiendo del tamaño</li>
              <li>Verifique que no haya aplicaciones conectadas durante la restauración</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de confirmación para limpiar -->
    <div v-if="showCleanConfirmation" class="modal-overlay" @click="showCleanConfirmation = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Confirmar Limpieza</h3>
          <button @click="showCleanConfirmation = false" class="modal-close">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="warning-content">
            <i class="material-icons warning-icon">warning</i>
            <div>
              <p><strong>¿Está seguro de que desea limpiar el directorio de backups?</strong></p>
              <p>Esta acción eliminará permanentemente todos los archivos de backup del servidor.</p>
              <p class="emphasis">Esta operación es <strong>irreversible</strong>.</p>
            </div>
          </div>
          
          <div class="confirmation-actions">
            <button 
              @click="showCleanConfirmation = false"
              class="btn btn-outline"
            >
              Cancelar
            </button>
            <button 
              @click="cleanBackupDirectory"
              :disabled="isCleaning"
              class="btn btn-danger"
            >
              <i class="material-icons">delete</i>
              {{ isCleaning ? 'Limpiando...' : 'Confirmar Limpieza' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de detalles del archivo -->
    <div v-if="selectedFile" class="modal-overlay" @click="selectedFile = null">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Detalles del Archivo</h3>
          <button @click="selectedFile = null" class="modal-close">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="file-details">
            <div class="detail-row">
              <label>Nombre del archivo:</label>
              <span class="file-name-detail">{{ selectedFile.filename }}</span>
            </div>
            
            <div class="detail-row">
              <label>Tamaño:</label>
              <span>{{ selectedFile.file_size_mb }} MB ({{ formatBytes(selectedFile.file_size) }})</span>
            </div>
            
            <div class="detail-row">
              <label>Fecha de creación:</label>
              <span>{{ formatDateTime(selectedFile.created_at) }}</span>
            </div>
            
            <div class="detail-row">
              <label>Ruta en servidor:</label>
              <span class="file-path">{{ selectedFile.filepath }}</span>
            </div>
            
            <div class="detail-actions">
              <button 
                @click="downloadFile(selectedFile)"
                :disabled="isDownloadingFile[selectedFile.id]"
                class="btn btn-primary"
              >
                <i class="material-icons">download</i>
                {{ isDownloadingFile[selectedFile.id] ? 'Descargando...' : 'Descargar Archivo' }}
              </button>
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
import type { BackupStatus, BackupFile } from '@/api/scripts'

export default defineComponent({
  name: 'GestionBackups',
  
  setup() {
    // Estado reactivo
    const isRefreshing = ref(false)
    const isExecutingBackup = ref(false)
    const isDownloading = ref(false)
    const isCleaning = ref(false)
    const isLoadingFiles = ref(false)
    const isDownloadingFile = ref<Record<number, boolean>>({})
    
    const backupStatus = ref<BackupStatus | null>(null)
    const backupFiles = ref<BackupFile[]>([])
    const selectedFile = ref<BackupFile | null>(null)
    
    const showCleanConfirmation = ref(false)
    const showGuide = ref(false)
    const sortBy = ref('date_desc')
    
    // Computed
    const hasBackups = computed(() => {
      return backupStatus.value && backupStatus.value.backup_files_count > 0
    })
    
    const sortedBackupFiles = computed(() => {
      const files = [...backupFiles.value]
      
      switch (sortBy.value) {
        case 'date_desc':
          return files.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        case 'date_asc':
          return files.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
        case 'size_desc':
          return files.sort((a, b) => b.file_size - a.file_size)
        case 'size_asc':
          return files.sort((a, b) => a.file_size - b.file_size)
        case 'name_asc':
          return files.sort((a, b) => a.filename.localeCompare(b.filename))
        case 'name_desc':
          return files.sort((a, b) => b.filename.localeCompare(a.filename))
        default:
          return files
      }
    })
    
    // Métodos principales
    const refreshData = async () => {
      if (isRefreshing.value) return
      
      try {
        isRefreshing.value = true
        await Promise.all([
          loadBackupStatus(),
          loadBackupFiles()
        ])
      } catch (error) {
        console.error('Error refrescando datos:', error)
      } finally {
        isRefreshing.value = false
      }
    }
    
    const loadBackupStatus = async () => {
      try {
        backupStatus.value = await scriptsService.getBackupStatus()
      } catch (error) {
        console.error('Error cargando estado de backup:', error)
      }
    }
    
    const loadBackupFiles = async () => {
      try {
        isLoadingFiles.value = true
        const response = await scriptsService.listBackupFiles()
        backupFiles.value = response.database_files || []
      } catch (error) {
        console.error('Error cargando archivos de backup:', error)
      } finally {
        isLoadingFiles.value = false
      }
    }
    
    const executeBackup = async () => {
      if (isExecutingBackup.value) return
      
      try {
        isExecutingBackup.value = true
        
        const execution = await scriptsService.executeScript('backup_db')
        console.log('Backup iniciado:', execution)
        
        alert('Backup iniciado correctamente. El proceso puede tomar varios minutos.')
        
        // Polling para verificar el estado
        const pollInterval = setInterval(async () => {
          try {
            const updatedExecution = await scriptsService.getExecution(execution.id)
            
            if (updatedExecution.status === 'completed' || updatedExecution.status === 'failed') {
              clearInterval(pollInterval)
              
              if (updatedExecution.status === 'completed') {
                alert('Backup completado exitosamente.')
                await refreshData()
              } else {
                alert('Error al crear el backup. Verifique los logs.')
              }
            }
          } catch (error) {
            console.error('Error en polling:', error)
            clearInterval(pollInterval)
          }
        }, 5000)
        
      } catch (error: any) {
        console.error('Error ejecutando backup:', error)
        alert(`Error al ejecutar el backup: ${error.message || error}`)
      } finally {
        isExecutingBackup.value = false
      }
    }
    
    const downloadLatestBackup = async () => {
      if (isDownloading.value || !hasBackups.value) return
      
      try {
        isDownloading.value = true
        
        const { blob, filename } = await scriptsService.downloadLatestBackupZip()
        scriptsService.downloadFile(blob, filename)
        
        alert(`Archivo descargado: ${filename}`)
        
      } catch (error: any) {
        console.error('Error descargando backup:', error)
        alert(`Error al descargar el backup: ${error.message || error}`)
      } finally {
        isDownloading.value = false
      }
    }
    
    const downloadFile = async (file: BackupFile) => {
      if (isDownloadingFile.value[file.id]) return
      
      try {
        isDownloadingFile.value[file.id] = true
        
        const { blob, filename } = await scriptsService.downloadBackupFile(file.id)
        scriptsService.downloadFile(blob, filename)
        
        // Cerrar modal si está abierto
        if (selectedFile.value?.id === file.id) {
          selectedFile.value = null
        }
        
      } catch (error: any) {
        console.error('Error descargando archivo:', error)
        alert(`Error al descargar el archivo: ${error.message || error}`)
      } finally {
        isDownloadingFile.value[file.id] = false
      }
    }
    
    const cleanBackupDirectory = async () => {
      if (isCleaning.value) return
      
      try {
        isCleaning.value = true
        showCleanConfirmation.value = false
        
        await scriptsService.cleanBackupDirectory()
        
        alert('Directorio de backups limpiado exitosamente.')
        await refreshData()
        
      } catch (error: any) {
        console.error('Error limpiando directorio:', error)
        alert(`Error al limpiar el directorio: ${error.message || error}`)
      } finally {
        isCleaning.value = false
      }
    }
    
    const showFileDetails = (file: BackupFile) => {
      selectedFile.value = file
    }
    
    const sortFiles = () => {
      // La ordenación se maneja automáticamente por el computed
    }
    
    // Métodos de utilidad
    const getStatusColor = (status: string) => {
      return scriptsService.getStatusColor(status)
    }
    
    const getStatusText = (status: string) => {
      return scriptsService.getStatusText(status)
    }
    
    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleDateString('es-ES')
    }
    
    const formatDateTime = (dateString: string) => {
      return new Date(dateString).toLocaleString('es-ES')
    }
    
    const formatBytes = (bytes: number) => {
      return scriptsService.formatFileSize(bytes)
    }
    
    // Lifecycle
    onMounted(() => {
      refreshData()
    })
    
    return {
      // Estado
      isRefreshing,
      isExecutingBackup,
      isDownloading,
      isCleaning,
      isLoadingFiles,
      isDownloadingFile,
      backupStatus,
      backupFiles,
      selectedFile,
      showCleanConfirmation,
      showGuide,
      sortBy,
      hasBackups,
      sortedBackupFiles,
      
      // Métodos
      refreshData,
      executeBackup,
      downloadLatestBackup,
      downloadFile,
      cleanBackupDirectory,
      showFileDetails,
      sortFiles,
      
      // Utilidades
      getStatusColor,
      getStatusText,
      formatDate,
      formatDateTime,
      formatBytes
    }
  }
})
</script>

<style scoped>
.gestion-backups {
  padding: 0;
}

/* Header */
.backups-header {
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

/* Estado general */
.backup-status-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.status-header {
  margin-bottom: 1.5rem;
}

.status-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1.5rem;
}

.status-item {
  text-align: center;
  padding: 1rem;
  border-radius: 8px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.status-item.success {
  background: #f0fdf4;
  border-color: #22c55e;
}

.status-item.error {
  background: #fef2f2;
  border-color: #ef4444;
}

.status-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 0.25rem;
}

.status-label {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}

.loading-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
  color: #64748b;
}

/* Acciones rápidas */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.action-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  transition: transform 0.2s;
}

.action-card:hover {
  transform: translateY(-2px);
}

.action-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.action-header i {
  font-size: 1.5rem;
}

.download-card .action-header i {
  color: #3b82f6;
}

.clean-card .action-header i {
  color: #ef4444;
}

.action-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1a202c;
}

.action-description {
  margin: 0 0 1rem;
  color: #64748b;
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

/* Archivos de backup */
.backup-files-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.section-header {
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

.section-filters {
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

.backup-files-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
}

.backup-file-card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  background: #fafafa;
  transition: all 0.2s;
}

.backup-file-card:hover {
  border-color: #cbd5e1;
  background: white;
}

.file-header {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.file-icon {
  width: 40px;
  height: 40px;
  background: #f1f5f9;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  margin: 0 0 0.25rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: #1a202c;
  word-break: break-all;
}

.file-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: #64748b;
}

.file-actions {
  display: flex;
  gap: 0.5rem;
}

.no-files {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #64748b;
  text-align: center;
}

.no-files i {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.no-files h3 {
  margin: 0 0 0.5rem;
  color: #374151;
}

.loading-files {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
  color: #64748b;
}

/* Guía de restauración */
.restoration-guide {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.guide-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.guide-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
}

.guide-content {
  margin-top: 1.5rem;
}

.guide-section {
  margin-bottom: 2rem;
}

.guide-section h4 {
  margin: 0 0 1rem;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
}

.guide-section ol {
  margin: 0 0 1rem;
  padding-left: 1.5rem;
}

.guide-section li {
  margin-bottom: 0.75rem;
  line-height: 1.6;
}

.code-block {
  margin: 0.5rem 0;
  padding: 1rem;
  background: #1a202c;
  color: #e2e8f0;
  border-radius: 6px;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  overflow-x: auto;
}

.code-block div {
  margin: 0.25rem 0;
}

.note {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0.5rem 0;
  padding: 0.75rem;
  background: #dbeafe;
  border: 1px solid #3b82f6;
  border-radius: 6px;
  color: #1e40af;
  font-size: 0.875rem;
}

.warning-box,
.tips-box {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
}

.warning-box {
  background: #fef3c7;
  border: 1px solid #f59e0b;
  color: #92400e;
}

.tips-box {
  background: #f0fdf4;
  border: 1px solid #22c55e;
  color: #166534;
}

.warning-box i,
.tips-box i {
  color: inherit;
  margin-top: 0.125rem;
  flex-shrink: 0;
}

/* Modales */
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
  max-width: 500px;
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

.warning-content {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.warning-icon {
  color: #f59e0b;
  font-size: 2rem;
  flex-shrink: 0;
}

.emphasis {
  font-weight: 600;
  color: #dc2626;
}

.confirmation-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.file-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-row {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.detail-row label {
  font-weight: 500;
  color: #4a5568;
  font-size: 0.875rem;
}

.file-name-detail,
.file-path {
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  word-break: break-all;
  background: #f8fafc;
  padding: 0.5rem;
  border-radius: 4px;
}

.detail-actions {
  margin-top: 1rem;
  display: flex;
  justify-content: center;
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

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
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

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
}

/* Responsive */
@media (max-width: 768px) {
  .backups-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .header-actions {
    width: 100%;
    justify-content: stretch;
  }
  
  .status-grid {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }
  
  .quick-actions {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .backup-files-grid {
    grid-template-columns: 1fr;
  }
  
  .guide-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .modal-content {
    margin: 1rem;
    max-height: calc(100vh - 2rem);
  }
  
  .confirmation-actions {
    flex-direction: column;
  }
}
</style>