// src/api/scripts.ts
import api from './config'
import { API_URL } from './config' 

// Tipos para el API de scripts
export interface ScriptExecution {
  id: string
  script_name: 'backup_db' | 'llenar_datos'
  status: 'pending' | 'running' | 'completed' | 'failed'
  user_name?: string
  created_at: string
  updated_at: string
  started_at?: string
  completed_at?: string
  output_file?: string
  error_message?: string
  output_log?: string
  backup_files: BackupFile[]
  duration_seconds?: number
}

export interface BackupFile {
  id: number
  filename: string
  filepath: string
  file_size: number
  file_size_mb: number
  created_at: string
}

export interface BackupStatus {
  total_executions: number
  successful_executions: number
  failed_executions: number
  last_execution?: ScriptExecution
  backup_files_count: number
  total_backup_size_mb: number
}

export interface ScriptStatus {
  script_name: string
  is_available: boolean
  last_execution?: ScriptExecution
  total_executions: number
  successful_executions: number
  failed_executions: number
}

// Función para verificar si el backend está disponible
const isBackendAvailable = async (): Promise<boolean> => {
  try {
    // Intenta hacer una petición básica para verificar conectividad
    await api.get('/scripts/api/executions/', { 
      timeout: 5000,
      params: { page: 1, page_size: 1 }
    })
    return true
  } catch (error) {
    console.warn('Backend de scripts no disponible:', error)
    return false
  }
}

// Datos mock para cuando el backend no esté disponible
const getMockData = () => ({
  executions: {
    results: [],
    count: 0
  },
  scriptsStatus: [],
  backupStatus: {
    total_executions: 0,
    successful_executions: 0,
    failed_executions: 0,
    backup_files_count: 0,
    total_backup_size_mb: 0
  }
})

// Servicio principal de scripts
export const scriptsService = {
  // ==================== Ejecuciones de Scripts ====================
  
  /**
   * Obtener todas las ejecuciones de scripts
   */
  async getExecutions(page = 1, pageSize = 10): Promise<{
    results: ScriptExecution[]
    count: number
    next?: string
    previous?: string
  }> {
    try {
      if (!(await isBackendAvailable())) {
        return getMockData().executions
      }

      const response = await api.get('/scripts/api/executions/', {
        params: { page, page_size: pageSize }
      })
      return response.data || response || getMockData().executions
    } catch (error) {
      console.error('Error obteniendo ejecuciones:', error)
      return getMockData().executions
    }
  },

  /**
   * Ejecutar un script de forma asíncrona
   */
  async executeScript(scriptName: 'backup_db' | 'llenar_datos'): Promise<ScriptExecution> {
    try {
      if (!(await isBackendAvailable())) {
        throw new Error('El servicio de scripts no está disponible. Verifique que el backend esté ejecutándose.')
      }

      const response = await api.post('/scripts/api/executions/', {
        script_name: scriptName
      })
      return response.data || response
    } catch (error: any) {
      console.error('Error ejecutando script:', error)
      if (error.response?.status === 404) {
        throw new Error('El endpoint de scripts no está disponible. Asegúrese de que el backend tenga configurada la app de scripts.')
      }
      throw error
    }
  },

  /**
   * Obtener detalles de una ejecución específica
   */
  async getExecution(executionId: string): Promise<ScriptExecution> {
    try {
      if (!(await isBackendAvailable())) {
        throw new Error('Servicio no disponible')
      }

      const response = await api.get(`/scripts/api/executions/${executionId}/`)
      return response.data || response
    } catch (error) {
      console.error('Error obteniendo ejecución:', error)
      throw error
    }
  },

  /**
   * Reintentar una ejecución
   */
  async retryExecution(executionId: string): Promise<ScriptExecution> {
    try {
      if (!(await isBackendAvailable())) {
        throw new Error('Servicio no disponible')
      }

      const response = await api.post(`/scripts/api/executions/${executionId}/retry/`)
      return response.data || response
    } catch (error) {
      console.error('Error reintentando ejecución:', error)
      throw error
    }
  },

  /**
   * Obtener resumen de estado de scripts
   */
  async getScriptsStatusSummary(): Promise<ScriptStatus[]> {
    try {
      if (!(await isBackendAvailable())) {
        return getMockData().scriptsStatus
      }

      const response = await api.get('/scripts/api/executions/status_summary/')
      return response.data || response || getMockData().scriptsStatus
    } catch (error) {
      console.error('Error obteniendo resumen de scripts:', error)
      return getMockData().scriptsStatus
    }
  },

  // ==================== Gestión de Backups ====================
  
  /**
   * Obtener estado general de backups
   */
  async getBackupStatus(): Promise<BackupStatus> {
    try {
      if (!(await isBackendAvailable())) {
        return getMockData().backupStatus
      }

      const response = await api.get('/scripts/api/backup/status/')
      return response.data || response || getMockData().backupStatus
    } catch (error) {
      console.error('Error obteniendo estado de backup:', error)
      return getMockData().backupStatus
    }
  },

  /**
   * Ejecutar backup de forma síncrona (para testing)
   */
  async executeBackupSync(): Promise<ScriptExecution> {
    try {
      if (!(await isBackendAvailable())) {
        throw new Error('Servicio no disponible')
      }

      const response = await api.post('/scripts/api/backup/execute/')
      return response.data || response
    } catch (error) {
      console.error('Error ejecutando backup síncrono:', error)
      throw error
    }
  },

  /**
   * Descargar último backup como ZIP
   */
async downloadLatestBackupZip(): Promise<{ blob: Blob; filename: string }> {
  try {
    const token = localStorage.getItem('token')
    const url = `${API_URL}/scripts/api/backup/download-zip/`
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Token ${token}`
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    
    // Extraer nombre del archivo
    const contentDisposition = response.headers.get('content-disposition')
    let filename = 'backup.zip'
    
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="([^"]+)"/)
      if (filenameMatch) {
        filename = filenameMatch[1]
      }
    }
    
    const blob = await response.blob()
    
    // ✅ AGREGAR DESCARGA AUTOMÁTICA:
    this.downloadFile(blob, filename)
    
    return {
      blob,
      filename
    }
  } catch (error) {
    console.error('Error descargando backup ZIP:', error)
    throw error
  }
},

  /**
   * Listar archivos de backup disponibles
   */
  async listBackupFiles(): Promise<{
    filesystem_files: any[]
    database_files: BackupFile[]
  }> {
    try {
      if (!(await isBackendAvailable())) {
        return {
          filesystem_files: [],
          database_files: []
        }
      }

      const response = await api.get('/scripts/api/backup/files/')
      return response.data || response || {
        filesystem_files: [],
        database_files: []
      }
    } catch (error) {
      console.error('Error listando archivos de backup:', error)
      return {
        filesystem_files: [],
        database_files: []
      }
    }
  },

  /**
   * Descargar un archivo de backup específico
   */
  async downloadBackupFile(fileId: number): Promise<{ blob: Blob; filename: string }> {
    try {
      if (!(await isBackendAvailable())) {
        throw new Error('Servicio de descarga no disponible')
      }

      const response = await api.get(`/scripts/api/backup/files/${fileId}/download/`, {
        responseType: 'blob'
      })
      
      // Extraer nombre del archivo
      const contentDisposition = response.headers['content-disposition']
      let filename = 'backup_file'
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="([^"]+)"/)
        if (filenameMatch) {
          filename = filenameMatch[1]
        }
      }
      
      return {
        blob: response.data || response,
        filename
      }
    } catch (error) {
      console.error('Error descargando archivo de backup:', error)
      throw error
    }
  },

  /**
   * Limpiar directorio de backups
   */
  async cleanBackupDirectory(): Promise<{ message: string }> {
    try {
      if (!(await isBackendAvailable())) {
        throw new Error('Servicio no disponible')
      }

      const response = await api.delete('/scripts/api/backup/clean/')
      return response.data || response || { message: 'Directorio limpiado' }
    } catch (error) {
      console.error('Error limpiando directorio de backup:', error)
      throw error
    }
  },

  // ==================== Utilidades ====================
  
  /**
   * Descargar archivo desde blob
   */
  downloadFile(blob: Blob, filename: string): void {
    try {
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error descargando archivo:', error)
      throw new Error('Error al descargar el archivo')
    }
  },

  /**
   * Formatear tamaño de archivo
   */
  formatFileSize(bytes: number): string {
    if (!bytes || bytes === 0) return '0 Bytes'
    
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  },

  /**
   * Formatear duración
   */
  formatDuration(seconds?: number): string {
    if (!seconds || isNaN(seconds)) return '--'
    
    if (seconds < 60) {
      return `${Math.round(seconds)}s`
    } else if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = Math.round(seconds % 60)
      return `${minutes}m ${remainingSeconds}s`
    } else {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      return `${hours}h ${minutes}m`
    }
  },

  /**
   * Obtener color del estado
   */
  getStatusColor(status: string): string {
    switch (status) {
      case 'completed':
        return '#28a745'
      case 'running':
        return '#17a2b8'
      case 'pending':
        return '#ffc107'
      case 'failed':
        return '#dc3545'
      default:
        return '#6c757d'
    }
  },

  /**
   * Obtener texto del estado en español
   */
  getStatusText(status: string): string {
    switch (status) {
      case 'pending':
        return 'Pendiente'
      case 'running':
        return 'Ejecutando'
      case 'completed':
        return 'Completado'
      case 'failed':
        return 'Fallido'
      default:
        return 'Desconocido'
    }
  },

  /**
   * Obtener nombre del script en español
   */
  getScriptDisplayName(scriptName: string): string {
    switch (scriptName) {
      case 'backup_db':
        return 'Copia de Seguridad de Base de Datos'
      case 'llenar_datos':
        return 'Actualizar Rutas Base Directorios'
      default:
        return scriptName
    }
  },

  /**
   * Verificar disponibilidad del servicio
   */
  async checkServiceAvailability(): Promise<boolean> {
    return await isBackendAvailable()
  }
}

export default scriptsService