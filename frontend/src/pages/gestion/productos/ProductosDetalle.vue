<template>
  <div class="productos-detalle-page">
    <!-- Header -->
    <header class="page-header">
      <div class="header-content">
        <button @click="goBack" class="btn-back">
          <i class="material-icons">arrow_back</i>
          Volver
        </button>
        <div class="header-info">
          <h1>Productos - {{ municipioName }}</h1>
          <div class="access-badge" :class="accessLevelClass">
            <i class="material-icons">{{ accessLevelIcon }}</i>
            <span>{{ accessLevelText }}</span>
          </div>
        </div>
      </div>
    </header>

    <!-- ✅ MENSAJE ESPECÍFICO PARA PROFESIONALES SIN ACCESO -->
    <div v-if="!loading && isProfesionalSinAcceso" class="access-denied-container">
      <div class="access-denied-card">
        <i class="material-icons">lock</i>
        <h2>Acceso Restringido</h2>
        <p>Como profesional de seguimiento, no tienes permisos para acceder a los productos de postoperación de este municipio.</p>
        <div class="access-info">
          <p><strong>Tu rol:</strong> {{ accessLevelText }}</p>
          <p><strong>Municipio:</strong> {{ municipioName }}</p>
          <p><strong>Contacta al administrador</strong> si necesitas acceso a esta información.</p>
        </div>
        <button @click="goBack" class="btn-back-denied">
          <i class="material-icons">arrow_back</i>
          Volver a productos
        </button>
      </div>
    </div>

    <!-- Loading/Error States -->
    <div v-else-if="loading" class="loading-container">
      <div class="spinner"></div>
      <span>Cargando productos...</span>
    </div>

    <div v-else-if="error && !isProfesionalSinAcceso" class="error-container">
      <i class="material-icons">error</i>
      <p>{{ error }}</p>
      <button @click="reloadData" class="btn-retry">Reintentar</button>
    </div>

    <!-- Main Content - Solo se muestra si hay datos Y tiene permisos -->
    <main v-else-if="tieneAccesoADatos" class="main-content">
      <!-- Filters -->
      <section class="filters-section">
        <div class="filters-container">
          <select v-model="filtroComponente" @change="aplicarFiltros">
            <option value="">Todos los componentes</option>
            <option v-for="comp in componentesResumidos" :key="comp" :value="comp">
              {{ formatComponenteName(comp) }}
            </option>
          </select>
          
          <div class="search-box">
            <i class="material-icons">search</i>
            <input 
              v-model="searchTerm"
              placeholder="Buscar archivo..."
              @input="aplicarFiltros"
            />
            <button v-if="searchTerm" @click="clearSearch" class="clear-btn">
              <i class="material-icons">close</i>
            </button>
          </div>
          
          <button @click="refreshData" class="btn-refresh" :disabled="loading">
            <i class="material-icons">refresh</i>
            Actualizar
          </button>
        </div>
      </section>

      <!-- Disposiciones Table -->
      <section class="disposiciones-section">
        <div class="section-header">
          <h2>Estado de Componentes</h2>
          <span class="count-badge">{{ disposicionesFiltradas.length }} componentes</span>
        </div>
        
        <div class="table-responsive">
          <table class="disposiciones-table" v-if="disposicionesFiltradas.length > 0">
            <thead>
              <tr>
                <th>Componente</th>
                <th>Estado</th>
                <th>Fecha</th>
                <th>Observaciones</th>
                <th v-if="canEdit">Acciones</th>
                <th>Archivos</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="disposicion in disposicionesFiltradas" :key="disposicion.id_disposicion">
                <td>
                  <div class="component-info">
                    <strong>{{ getComponenteName(disposicion.id_componente) }}</strong>
                  </div>
                </td>
                <td>
                  <div class="status-badges">
                    <span :class="getStatusClass('evaluado', disposicion.evaluado)">
                      {{ getStatusText('evaluado', disposicion.evaluado) }}
                    </span>
                    <span :class="getStatusClass('aprobado', disposicion.aprobado)">
                      {{ getStatusText('aprobado', disposicion.aprobado) }}
                    </span>
                    <span :class="getStatusClass('dispuesto', disposicion.dispuesto)">
                      {{ getStatusText('dispuesto', disposicion.dispuesto) }}
                    </span>
                  </div>
                </td>
                <td>{{ formatDate(disposicion.fecha_disposicion) }}</td>
                <td>
                  <div class="observaciones-cell">
                    {{ disposicion.observaciones || 'Sin observaciones' }}
                  </div>
                </td>
                <td v-if="canEdit">
                  <button @click="editarEstado(disposicion)" class="btn-edit">
                    <i class="material-icons">edit</i>
                  </button>
                </td>
                <td>
                  <button 
                    @click="verArchivos(disposicion)" 
                    class="btn-view-files"
                    :class="{ active: componenteSeleccionado?.id_disposicion === disposicion.id_disposicion }"
                  >
                    <i class="material-icons">folder</i>
                    {{ getArchivoCount(disposicion.id_disposicion) }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-else class="empty-state">
            <i class="material-icons">inbox</i>
            <h3>No se encontraron componentes</h3>
            <p>No hay componentes para mostrar con los filtros aplicados.</p>
          </div>
        </div>
      </section>

      <!-- Archivos Section -->
      <section v-if="mostrarArchivos && componenteSeleccionado" class="archivos-section">
        <div class="section-header">
          <h3>Archivos - {{ getComponenteName(componenteSeleccionado.id_componente) }}</h3>
          <button @click="cerrarArchivos" class="btn-close">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <!-- ✅ ARCHIVOS EN TABLA EN LUGAR DE TARJETAS MOLESTAS -->
        <div class="table-responsive" v-if="archivosFiltrados.length > 0">
          <table class="archivos-table">
            <thead>
              <tr>
                <th>Archivo</th>
                <th>Fecha</th>
                <th>Observaciones</th>
                <th v-if="canDownload">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="archivo in archivosFiltrados" :key="archivo.id_archivo">
                <td>
                  <div class="archivo-info">
                    <i class="material-icons archivo-icon-small">{{ getFileIcon(archivo.nombre_archivo) }}</i>
                    <span class="archivo-nombre">{{ archivo.nombre_archivo }}</span>
                  </div>
                </td>
                <td>{{ formatDate(archivo.fecha_disposicion) }}</td>
                <td>
                  <span class="archivo-observacion">{{ archivo.observacion || 'Sin observaciones' }}</span>
                </td>
<td v-if="canDownload">
  <div class="archivo-actions-inline">
    <!-- ✅ NUEVO: Botón Info -->
    <button @click="showFileInfo(archivo)" class="btn-icon small info" title="Ver información del archivo">
      <i class="material-icons">info</i>
    </button>
    
    <button @click="viewFile(archivo)" class="btn-icon small primary" title="Ver archivo">
      <i class="material-icons">visibility</i>
    </button>
    <button @click="downloadFile(archivo)" class="btn-icon small success" title="Descargar archivo">
      <i class="material-icons">download</i>
    </button>
  </div>
</td>

<!-- 2. AGREGAR EL MODAL DE INFORMACIÓN (después del modal de edición existente) -->
<!-- File Info Modal -->
<div v-if="showFileInfoModal" class="modal-overlay" @click="closeFileInfoModal">
  <div class="modal-content file-info-modal" @click.stop>
    <div class="modal-header">
      <h3>
        <i class="material-icons">info</i>
        Información del Archivo
      </h3>
      <button @click="closeFileInfoModal" class="modal-close">
        <i class="material-icons">close</i>
      </button>
    </div>
    
    <div class="modal-body">
      <div v-if="selectedFileInfo" class="file-info-container">
        <!-- Información básica -->
        <div class="info-section">
          <h4>📄 Información Básica</h4>
          <div class="info-grid">
            <div class="info-item">
              <label>ID Archivo:</label>
              <span class="info-value">{{ selectedFileInfo.id_archivo || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <label>Nombre:</label>
              <span class="info-value">{{ selectedFileInfo.nombre_archivo || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <label>Fecha:</label>
              <span class="info-value">{{ formatDate(selectedFileInfo.fecha_disposicion) }}</span>
            </div>
            <div class="info-item">
              <label>ID Disposición:</label>
              <span class="info-value">{{ selectedFileInfo.id_disposicion || 'N/A' }}</span>
            </div>
          </div>
        </div>

        <!-- Información de ruta (la más importante para debugging) -->
        <div class="info-section highlight">
          <h4>🔗 Información de Ruta</h4>
          <div class="info-item full-width">
            <label>Ruta Completa:</label>
            <div class="ruta-container">
              <span class="info-value ruta-value">{{ linuxToWindowsPath(selectedFileInfo.ruta_completa) || 'Sin ruta' }}</span>
              <button 
                v-if="selectedFileInfo.ruta_completa" 
                @click="copyToClipboard(selectedFileInfo.ruta_completa)"
                class="btn-copy"
                title="Copiar ruta"
              >
                <i class="material-icons">content_copy</i>
              </button>
            </div>
          </div>
        </div>

        <!-- Observaciones -->
        <div class="info-section">
          <h4>📝 Observaciones</h4>
          <div class="info-item full-width">
            <span class="info-value observacion">{{ selectedFileInfo.observacion || 'Sin observaciones' }}</span>
          </div>
        </div>


      </div>
    </div>
    
    <div class="modal-footer">

      <button @click="closeFileInfoModal" class="btn-secondary">Cerrar</button>
    </div>
  </div>
</div>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-else class="empty-state">
          <i class="material-icons">folder_open</i>
          <h3>No hay archivos</h3>
          <p>No se encontraron archivos para este componente.</p>
        </div>
      </section>
    </main>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Editar Estado</h3>
          <button @click="closeModal" class="modal-close">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="editForm.evaluado" />
              <span>Evaluado</span>
            </label>
          </div>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="editForm.aprobado" />
              <span>Aprobado</span>
            </label>
          </div>
          
          <div class="form-group">
            <label>Observaciones:</label>
            <textarea 
              v-model="editForm.observaciones"
              placeholder="Observaciones..."
              rows="4"
            ></textarea>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeModal" class="btn-secondary">Cancelar</button>
          <button @click="saveEditChanges" class="btn-primary">Guardar</button>
        </div>
      </div>
    </div>

    <!-- Notification -->
    <div v-if="notification.show" :class="['notification', notification.type]">
      <div class="notification-content">
        <i class="material-icons">{{ notification.icon }}</i>
        <span>{{ notification.message }}</span>
      </div>
      <button @click="closeNotification" class="notification-close">
        <i class="material-icons">close</i>
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, nextTick } from 'vue'
import { linuxToWindowsPath } from '@/utils/pathUtils'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { format, parseISO } from 'date-fns'
import { es } from 'date-fns/locale'
import { getMunicipioById } from '@/api/municipios'
import { API_URL } from '@/api/config'
import api from '@/api/config'

export default defineComponent({
  name: 'ProductosDetalle',
  
  setup() {
    const route = useRoute()
    const router = useRouter()
    const authStore = useAuthStore()
    
    // Estado principal
    const loading = ref(false)
    const error = ref<string | null>(null)
    const municipioName = ref('')
    
    // ✅ ESTADO ESPECÍFICO PARA MANEJO DE PERMISOS
    const accessDenied = ref(false)
    const permissionError = ref<string | null>(null)
    
    // Datos
    const disposiciones = ref<any[]>([])
    const archivos = ref<any[]>([])
    const componentes = ref<any[]>([])
    
    // Filtros
    const searchTerm = ref('')
    const filtroComponente = ref('')
    
    // Estado de archivos
    const mostrarArchivos = ref(false)
    const componenteSeleccionado = ref<any>(null)
    
    // Modal de edición
    const showEditModal = ref(false)
    const editingDisposicion = ref<any>(null)
    const editForm = ref({
      evaluado: false,
      aprobado: false,
      observaciones: ''
    })
    
    // Notificaciones
    const notification = ref({
      show: false,
      message: '',
      type: 'success',
      icon: 'check_circle',
      timeout: null as number | null
    })

    const showFileInfoModal = ref(false)
    const selectedFileInfo = ref<any>(null)
    // ============ COMPUTED ============
    
    const userPermissions = computed(() => ({
      isSuperAdmin: authStore.isSuperAdmin,
      isAdmin: authStore.isAdmin,
      isProfesional: authStore.isProfesional,
      isAnyAdmin: authStore.isAnyAdmin
    }))
    
    // ✅ LÓGICA ESPECÍFICA PARA DETECTAR PROFESIONAL SIN ACCESO
    const isProfesionalSinAcceso = computed(() => {
      return userPermissions.value.isProfesional && 
             !userPermissions.value.isAnyAdmin && 
             accessDenied.value &&
             disposiciones.value.length === 0
    })
    
    // ✅ VERIFICAR SI TIENE ACCESO A LOS DATOS
    const tieneAccesoADatos = computed(() => {
      // Admin y super admin siempre tienen acceso
      if (userPermissions.value.isAnyAdmin) return true
      
      // Profesional solo si no está denegado Y tiene datos
      if (userPermissions.value.isProfesional) {
        return !accessDenied.value && disposiciones.value.length > 0
      }
      
      // Para otros roles, si no hay error y hay datos
      return !error.value && disposiciones.value.length > 0
    })
    
    const canEdit = computed(() => userPermissions.value.isSuperAdmin || userPermissions.value.isAdmin)
    const canDownload = computed(() => userPermissions.value.isSuperAdmin || userPermissions.value.isAdmin || userPermissions.value.isProfesional)
    
    const accessLevelText = computed(() => {
      if (userPermissions.value.isSuperAdmin) return 'Super Administrador'
      if (userPermissions.value.isAdmin) return 'Administrador'  
      if (userPermissions.value.isProfesional) return 'Profesional de Seguimiento'
      return 'Solo Lectura'
    })
    
    const accessLevelIcon = computed(() => {
      if (userPermissions.value.isSuperAdmin) return 'admin_panel_settings'
      if (userPermissions.value.isAdmin) return 'settings'
      if (userPermissions.value.isProfesional) return 'work'
      return 'visibility'
    })
    
    const accessLevelClass = computed(() => {
      if (userPermissions.value.isSuperAdmin) return 'super-admin'
      if (userPermissions.value.isAdmin) return 'admin'
      if (userPermissions.value.isProfesional) return 'profesional'
      return 'readonly'
    })
    
    const componentesResumidos = computed(() => {
      const nombres = componentes.value.map(comp => {
        const nombreCompleto = comp.nombre_componente || comp.tipo_componente || ''
        return formatComponenteName(nombreCompleto)
      })
      
      return [...new Set(nombres)].filter(n => n && n !== 'Sin nombre').sort()
    })
    
    const disposicionesFiltradas = computed(() => {
      let result = [...disposiciones.value]
      
      if (filtroComponente.value) {
        result = result.filter(disp => {
          const componenteName = getComponenteName(disp.id_componente)
          return componenteName.includes(filtroComponente.value) || 
                 componenteName.toLowerCase().includes(filtroComponente.value.toLowerCase())
        })
      }
      
      if (searchTerm.value.trim()) {
        const search = searchTerm.value.toLowerCase()
        result = result.filter(disp => {
          const componenteName = getComponenteName(disp.id_componente).toLowerCase()
          const observaciones = (disp.observaciones || '').toLowerCase()
          return componenteName.includes(search) || observaciones.includes(search)
        })
      }
      
      return result
    })
    
    const archivosFiltrados = computed(() => {
      if (!componenteSeleccionado.value) return []
      
      return archivos.value.filter(archivo => 
        archivo.id_disposicion === componenteSeleccionado.value.id_disposicion
      )
    })

    // ============ MANEJO DE ERRORES ESPECÍFICO PARA PROFESIONALES ============
    
    const handleApiError = (error: any, funcionName: string) => {
      console.error(`Error en ${funcionName}:`, error)
      
      // ✅ MANEJO ESPECÍFICO PARA PROFESIONALES
      if (error.response?.status === 401 || error.response?.status === 403) {
        const errorMessage = error.response?.data?.detail || error.response?.data?.message || ''
        
        console.log(`🔍 Error de permisos en ${funcionName}:`, {
          status: error.response?.status,
          message: errorMessage,
          isProfesional: userPermissions.value.isProfesional,
          isAdmin: userPermissions.value.isAnyAdmin
        })
        
        // Si es profesional y error de permisos, marcar como acceso denegado
        if (userPermissions.value.isProfesional && !userPermissions.value.isAnyAdmin) {
          console.warn(`⚠️ Profesional sin acceso a ${funcionName}`)
          accessDenied.value = true
          permissionError.value = `Sin permisos para acceder a ${funcionName}`
          return [] // No hacer logout, solo devolver array vacío
        }
        
        // Solo logout en casos específicos de token inválido para admins
        if (errorMessage.includes('Invalid token') || 
            errorMessage.includes('Token has expired') ||
            errorMessage.includes('Authentication credentials were not provided')) {
          console.warn('Token inválido detectado, redirigiendo al login')
          authStore.logout()
          router.push('/login')
        }
      }
      
      return []
    }
    
    // ============ API FUNCTIONS ADAPTADAS PARA PROFESIONALES ============
    
    const getDisposicionesByMunicipio = async (municipioId: number) => {
      try {
        console.log(`📡 [${userPermissions.value.isProfesional ? 'PROFESIONAL' : 'ADMIN'}] Solicitando disposiciones para municipio ${municipioId}`)
        
        const response = await api.get('/postoperacion/disposiciones/por_municipio/', {
          params: { municipio_id: municipioId }
        })
        
        console.log('📋 Respuesta de disposiciones:', response)
        
        let data = response
        if (response && typeof response === 'object' && 'data' in response) {
          data = response.data
        }
        
        if (Array.isArray(data)) {
          console.log(`✅ ${data.length} disposiciones obtenidas`)
          accessDenied.value = false // Restablecer si tuvo éxito
          return data
        } else if (data && typeof data === 'object') {
          if (Array.isArray(data.results)) {
            console.log(`✅ ${data.results.length} disposiciones obtenidas (paginadas)`)
            accessDenied.value = false
            return data.results
          }
          if (Array.isArray(data.disposiciones)) {
            console.log(`✅ ${data.disposiciones.length} disposiciones obtenidas`)
            accessDenied.value = false
            return data.disposiciones
          }
        }
        
        console.warn('⚠️ Formato de respuesta inesperado para disposiciones:', data)
        return []
        
      } catch (error) {
        console.error('❌ Error obteniendo disposiciones:', error)
        return handleApiError(error, 'getDisposicionesByMunicipio')
      }
    }
    
    const getArchivosByMunicipio = async (municipioId: number) => {
      try {
        console.log(`📡 [${userPermissions.value.isProfesional ? 'PROFESIONAL' : 'ADMIN'}] Solicitando archivos para municipio ${municipioId}`)
        
        const response = await api.get('/postoperacion/archivos/por_municipio/', {
          params: { municipio_id: municipioId }
        })
        
        console.log('📋 Respuesta de archivos:', response)
        
        let data = response
        if (response && typeof response === 'object' && 'data' in response) {
          data = response.data
        }
        
        if (Array.isArray(data)) {
          console.log(`✅ ${data.length} archivos obtenidos`)
          return data
        } else if (data && typeof data === 'object') {
          if (Array.isArray(data.results)) {
            console.log(`✅ ${data.results.length} archivos obtenidos (paginados)`)
            return data.results
          }
          if (Array.isArray(data.archivos)) {
            console.log(`✅ ${data.archivos.length} archivos obtenidos`)
            return data.archivos
          }
        }
        
        console.warn('⚠️ Formato de respuesta inesperado para archivos:', data)
        return []
        
      } catch (error) {
        if (error.response?.status === 404) {
          console.info('ℹ️ No se encontraron archivos para este municipio (404)')
          return []
        }
        console.error('❌ Error obteniendo archivos:', error)
        return handleApiError(error, 'getArchivosByMunicipio')
      }
    }
    
    const getComponentes = async () => {
      try {
        console.log(`📡 [${userPermissions.value.isProfesional ? 'PROFESIONAL' : 'ADMIN'}] Solicitando componentes`)
        
        const response = await api.get('/postoperacion/componentes/')
        
        console.log('📋 Respuesta de componentes:', response)
        
        let data = response
        if (response && typeof response === 'object' && 'data' in response) {
          data = response.data
        }
        
        if (Array.isArray(data)) {
          console.log(`✅ ${data.length} componentes obtenidos`)
          return data
        } else if (data && typeof data === 'object') {
          if (Array.isArray(data.results)) {
            console.log(`✅ ${data.results.length} componentes obtenidos (paginados)`)
            return data.results
          }
          if (Array.isArray(data.componentes)) {
            console.log(`✅ ${data.componentes.length} componentes obtenidos`)
            return data.componentes
          }
        }
        
        console.warn('⚠️ Formato de respuesta inesperado para componentes:', data)
        return []
        
      } catch (error) {
        console.error('❌ Error obteniendo componentes:', error)
        return handleApiError(error, 'getComponentes')
      }
    }
    
    // ✅ FUNCIONES DE ARCHIVOS ADAPTADAS
    const downloadFile = async (archivo: any) => {
      if (!archivo.ruta_completa) {
        showNotification('No hay ruta disponible para descargar este archivo', 'warning')
        return
      }
      
      try {
        showNotification('Iniciando descarga...', 'info')
        
        const response = await api.get('/preoperacion/ver_pdf/', {
          params: { ruta: archivo.ruta_completa },
          responseType: 'blob'
        })
        
        let blobData = response
        if (response && typeof response === 'object' && 'data' in response) {
          blobData = response.data
        }
        
        const blob = new Blob([blobData])
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = obtenerNombreArchivo(archivo.ruta_completa)
        
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        window.URL.revokeObjectURL(url)
        showNotification(`Descargando: ${link.download}`, 'success')
        
      } catch (error) {
        console.error('Error al descargar archivo:', error)
        if (error.response?.status === 403) {
          showNotification('No tienes permisos para descargar este archivo', 'error')
        } else if (error.response?.status === 404) {
          showNotification('Archivo no encontrado', 'error')
        } else {
          showNotification(`Error al descargar archivo: ${error.response?.data?.detail || error.message}`, 'error')
        }
      }
    }
    
  const viewFile = async (archivo: any) => {
    if (!archivo.ruta_completa) {
      showNotification('No hay ruta disponible para este archivo', 'warning')
      return
    }
    
    try {
      const fileName = obtenerNombreArchivo(archivo.ruta_completa)
      const fileExtension = getFileExtension(fileName)
      
      if (['gdb', 'zip', 'rar', '7z'].includes(fileExtension)) {
        await downloadFile(archivo)
      } else {
        showNotification('Abriendo archivo...', 'info')
        
        // ✅ CORREGIDO: Usar la misma ruta que funciona en downloadFile
        const response = await api.get('/preoperacion/ver_pdf/', {
          params: { ruta: archivo.ruta_completa },
          responseType: 'blob'
        })
        
        let blobData = response
        if (response && typeof response === 'object' && 'data' in response) {
          blobData = response.data
        }
        
        const blob = new Blob([blobData], { type: blobData.type || 'application/octet-stream' })
        const url = window.URL.createObjectURL(blob)
        
        window.open(url, '_blank')
        showNotification(`Abriendo: ${fileName}`, 'success')
        
        setTimeout(() => window.URL.revokeObjectURL(url), 10000)
      }
      
    } catch (error) {
      console.error('Error al visualizar archivo:', error)
      if (error.response?.status === 403) {
        showNotification('No tienes permisos para ver este archivo', 'error')
      } else if (error.response?.status === 404) {
        showNotification('Archivo no encontrado', 'error')
      } else {
        showNotification(`Error al abrir archivo: ${error.response?.data?.detail || error.message}`, 'error')
      }
    }
  }

    // ============ UTILITY FUNCTIONS ============
    
    const obtenerNombreArchivo = (ruta: string): string => {
      if (!ruta) return 'archivo'
      const partes = ruta.split(/[\/\\]/)
      return partes[partes.length - 1]
    }
    
    const getFileExtension = (fileName: string): string => {
      if (!fileName) return ''
      return fileName.split('.').pop()?.toLowerCase() || ''
    }
    
    const getComponenteName = (componenteId: number): string => {
      const comp = componentes.value.find(c => c.id_componente === componenteId)
      // ✅ CORREGIDO: Usar nombre_componente en lugar de tipo_componente
      return comp?.nombre_componente || comp?.tipo_componente || `Componente ${componenteId}`
    }
    
    const getComponenteByDisposicion = (disposicionId: number) => {
      return disposiciones.value.find(d => d.id_disposicion === disposicionId)
    }
    
    const formatComponenteName = (name: string): string => {
      return name.length > 50 ? `${name.substring(0, 47)}...` : name
    }
    
    const formatDate = (dateStr: string): string => {
      if (!dateStr) return 'Sin fecha'
      try {
        return format(parseISO(dateStr), 'dd/MM/yyyy', { locale: es })
      } catch {
        return 'Fecha inválida'
      }
    }
    
    const getStatusClass = (type: string, value: boolean): string => {
      const baseClass = `status-badge ${type}`
      return value ? `${baseClass} active` : baseClass
    }
    
    const getStatusText = (type: string, value: boolean): string => {
      const texts = {
        evaluado: value ? 'Evaluado' : 'Pendiente',
        aprobado: value ? 'Aprobado' : 'No aprobado', 
        dispuesto: value ? 'Dispuesto' : 'No dispuesto'
      }
      return texts[type] || (value ? 'Sí' : 'No')
    }
    
    const getArchivoCount = (disposicionId: number): string => {
      const count = archivos.value.filter(a => a.id_disposicion === disposicionId).length
      return `${count} archivo${count !== 1 ? 's' : ''}`
    }
    
    const getFileIcon = (fileName: string): string => {
      const extension = getFileExtension(fileName)
      const icons = {
        pdf: 'picture_as_pdf',
        zip: 'archive', rar: 'archive', '7z': 'archive',
        gdb: 'storage',
        jpg: 'image', jpeg: 'image', png: 'image', gif: 'image',
        doc: 'description', docx: 'description',
        xls: 'table_chart', xlsx: 'table_chart'
      }
      return icons[extension] || 'insert_drive_file'
    }

    // ============ MAIN FUNCTIONS ============
    
    const loadData = async () => {
      try {
        loading.value = true
        error.value = null
        accessDenied.value = false // ✅ Restablecer estado
        permissionError.value = null
        
        const municipioId = Number(route.params.id)
        if (!municipioId || isNaN(municipioId)) {
          error.value = 'ID de municipio inválido'
          return
        }
        
        console.log(`📊 [${userPermissions.value.isProfesional ? 'PROFESIONAL' : 'ADMIN'}] Cargando datos para municipio ${municipioId}...`)
        
        // Cargar municipio primero
        try {
          const municipio = await getMunicipioById(municipioId)
          municipioName.value = municipio?.nom_municipio || `Municipio ${municipioId}`
          console.log(`✅ Municipio cargado: ${municipioName.value}`)
        } catch (err) {
          console.warn('Error cargando municipio, usando ID como nombre:', err)
          municipioName.value = `Municipio ${municipioId}`
        }
        
        // ✅ CARGA SECUENCIAL CON MANEJO ESPECÍFICO PARA PROFESIONALES
        console.log('📡 Cargando componentes...')
        const componentesData = await getComponentes()
        componentes.value = componentesData
        console.log(`✅ ${componentesData.length} componentes cargados`)
        
        // ✅ DEBUG: Verificar estructura de componentes
        if (componentesData.length > 0) {
          console.log('🔍 Estructura del primer componente:', componentesData[0])
          console.log('🔍 Campos disponibles:', Object.keys(componentesData[0]))
        }
        
        console.log('📡 Cargando disposiciones...')
        const disposicionesData = await getDisposicionesByMunicipio(municipioId)
        disposiciones.value = disposicionesData
        console.log(`✅ ${disposicionesData.length} disposiciones cargadas`)
        
        console.log('📡 Cargando archivos...')
        const archivosData = await getArchivosByMunicipio(municipioId)
        archivos.value = archivosData
        console.log(`✅ ${archivosData.length} archivos cargados`)

        // ✅ VERIFICAR SI PROFESIONAL TIENE ACCESO
        if (userPermissions.value.isProfesional && !userPermissions.value.isAnyAdmin) {
          if (disposicionesData.length === 0 && accessDenied.value) {
            console.warn('⚠️ Profesional sin acceso a postoperación para este municipio')
            showNotification('No tienes permisos para acceder a los productos de este municipio', 'warning')
          } else {
            console.log('✅ Profesional con acceso confirmado')
          }
        }

        console.log('✅ Todos los datos cargados exitosamente')

      } catch (err) {
        console.error('Error cargando datos:', err)
        
        // ✅ NO ESTABLECER ERROR GENERAL SI ES PROBLEMA DE PERMISOS DE PROFESIONAL
        if (!(userPermissions.value.isProfesional && accessDenied.value)) {
          error.value = 'Error al cargar los datos del municipio. Por favor, recarga la página.'
        }
      } finally {
        loading.value = false
      }
    }
    
    const reloadData = () => {
      console.log('🔄 Recargando datos...')
      loadData()
    }
    
    const goBack = () => {
      console.log('🔙 Volviendo a la lista de productos')
      
      // ✅ DETECTAR EL CONTEXTO ACTUAL DESDE LA RUTA
      const currentPath = route.path
      
      if (currentPath.includes('/disposicion-informacion/')) {
        // Contexto público - disposición de información
        router.push('/disposicion-informacion/productos')
      } else if (currentPath.includes('/gestion-informacion/')) {
        // Contexto administrativo - gestión de información
        router.push('/gestion-informacion/productos')
      } else {
        // Fallback - intentar ir a disposición pública
        console.warn('⚠️ Contexto no reconocido, redirigiendo a disposición pública')
        router.push('/disposicion-informacion/productos')
      }
    }
    
    const clearSearch = () => {
      searchTerm.value = ''
      console.log('🧹 Búsqueda limpiada')
    }
    
    const refreshData = async () => {
      console.log('🔄 Refrescando datos...')
      await loadData()
    }
    
    const aplicarFiltros = () => {
      // Los filtros se aplican automáticamente via computed properties
    }
    
    const verArchivos = (disposicion: any) => {
      if (componenteSeleccionado.value?.id_disposicion === disposicion.id_disposicion) {
        cerrarArchivos()
      } else {
        componenteSeleccionado.value = disposicion
        mostrarArchivos.value = true
        nextTick(() => {
          document.querySelector('.archivos-section')?.scrollIntoView({ behavior: 'smooth' })
        })
      }
    }
    
    const cerrarArchivos = () => {
      mostrarArchivos.value = false
      componenteSeleccionado.value = null
    }
    
    const editarEstado = (disposicion: any) => {
      editingDisposicion.value = disposicion
      editForm.value = {
        evaluado: disposicion.evaluado,
        aprobado: disposicion.aprobado,
        observaciones: disposicion.observaciones || ''
      }
      showEditModal.value = true
    }
    
    const saveEditChanges = async () => {
      if (!editingDisposicion.value) return
      
      try {
        showNotification('Guardando cambios...', 'info')
        
        const response = await api.patch(`/postoperacion/disposiciones/${editingDisposicion.value.id_disposicion}/`, {
          evaluado: editForm.value.evaluado,
          aprobado: editForm.value.aprobado,
          observaciones: editForm.value.observaciones
        })
        
        const index = disposiciones.value.findIndex(d => d.id_disposicion === editingDisposicion.value.id_disposicion)
        if (index !== -1) {
          disposiciones.value[index] = { ...disposiciones.value[index], ...editForm.value }
        }
        
        showNotification('Estado actualizado exitosamente', 'success')
        closeModal()
        
      } catch (error) {
        console.error('Error actualizando disposición:', error)
        if (error.response?.status === 403) {
          showNotification('No tienes permisos para editar este estado', 'error')
        } else if (error.response?.status === 404) {
          showNotification('Disposición no encontrada', 'error')
        } else {
          showNotification(`Error al actualizar: ${error.response?.data?.detail || error.message}`, 'error')
        }
      }
    }
    
    const closeModal = () => {
      showEditModal.value = false
      editingDisposicion.value = null
    }
    
    const showNotification = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'success') => {
      const icons = {
        success: 'check_circle',
        error: 'error',
        warning: 'warning',
        info: 'info'
      }
      
      notification.value = {
        show: true,
        message,
        type,
        icon: icons[type],
        timeout: null
      }
      
      if (notification.value.timeout) {
        clearTimeout(notification.value.timeout)
      }
      
      notification.value.timeout = window.setTimeout(() => {
        notification.value.show = false
      }, 5000)
    }

    // Función principal (mantener igual)
    const showFileInfo = (archivo: any) => {
      console.log('📋 Mostrando información del archivo:', archivo)
      selectedFileInfo.value = archivo
      showFileInfoModal.value = true
    }

    // Cerrar modal (mantener igual)
    const closeFileInfoModal = () => {
      showFileInfoModal.value = false
      selectedFileInfo.value = null
    }

    // Copiar al portapapeles (mantener igual)
    const copyToClipboard = async (text: string) => {
      try {
        await navigator.clipboard.writeText(text)
        showNotification('Texto copiado al portapapeles', 'success')
      } catch (error) {
        console.error('Error copiando al portapapeles:', error)
        
        // Fallback para navegadores que no soporten clipboard API
        const textArea = document.createElement('textarea')
        textArea.value = text
        document.body.appendChild(textArea)
        textArea.select()
        
        try {
          document.execCommand('copy')
          showNotification('Texto copiado al portapapeles', 'success')
        } catch (fallbackError) {
          showNotification('No se pudo copiar al portapapeles', 'error')
        }
        
        document.body.removeChild(textArea)
      }
    }

    
    const closeNotification = () => {
      if (notification.value.timeout) {
        clearTimeout(notification.value.timeout)
      }
      notification.value.show = false
    }
    
    onMounted(() => {
      loadData()
    })
    
    return {
      // Estado
      loading,
      error,
      municipioName,
      searchTerm,
      filtroComponente,
      mostrarArchivos,
      componenteSeleccionado,
      showEditModal,
      editingDisposicion,
      editForm,
      notification,
      
      // ✅ Estados específicos para profesionales
      accessDenied,
      permissionError,
      isProfesionalSinAcceso,
      tieneAccesoADatos,
      
      // Permisos
      userPermissions,
      canEdit,
      canDownload,
      accessLevelText,
      accessLevelIcon,
      accessLevelClass,
      
      // Datos
      disposiciones,
      archivos,
      componentes,
      componentesResumidos,
      
      // Computed
      disposicionesFiltradas,
      archivosFiltrados,
      
      // Métodos principales
      clearSearch,
      aplicarFiltros,
      refreshData,
      reloadData,
      goBack,
      verArchivos,
      cerrarArchivos,
      editarEstado,
      saveEditChanges,
      viewFile,
      downloadFile,
      closeModal,
      showNotification,
      closeNotification,
      
      // Utilidades
      getComponenteName,
      getComponenteByDisposicion,
      formatComponenteName,
      formatDate,
      getStatusClass,
      getStatusText,
      getFileIcon,
      getArchivoCount,
      handleApiError,
      showFileInfoModal,
      selectedFileInfo,
      showFileInfo,
      closeFileInfoModal,
      copyToClipboard,
      // Utilidades de rutas
      linuxToWindowsPath,
    }
  }
})
</script>

<style scoped>

/* Botón Info (mantener igual) */
.btn-icon.info {
  background: #17a2b8;
  color: white;
}

.btn-icon.info:hover {
  background: #138496;
  transform: translateY(-1px);
}

/* Modal de información de archivo (simplificado) */
.file-info-modal {
  max-width: 600px;
  width: 95%;
  max-height: 80vh;
}

.file-info-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.info-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid #e9ecef;
}

.info-section.highlight {
  background: #e7f3ff;
  border-color: #b3d9ff;
}

.info-section h4 {
  margin: 0 0 1rem 0;
  color: #495057;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-item label {
  font-weight: 600;
  color: #6c757d;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  color: #212529;
  font-family: 'Courier New', monospace;
  background: white;
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #ced4da;
  word-break: break-all;
}

.info-value.observacion {
  font-family: inherit;
  min-height: 2.5rem;
  white-space: pre-wrap;
}

/* Contenedor de ruta con botón de copiar */
.ruta-container {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
}

.ruta-value {
  flex: 1;
  background: #fff3cd;
  border-color: #ffc107;
  color: #856404;
  font-weight: 500;
}

.btn-copy {
  background: #17a2b8;
  color: white;
  border: none;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  min-width: 36px;
  height: 36px;
}

.btn-copy:hover {
  background: #138496;
  transform: translateY(-1px);
}

.btn-copy i {
  font-size: 1rem;
}

.productos-detalle-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
  background-color: #f8f9fa;
  min-height: 100vh;
}

/* ============ HEADER ============ */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 2rem;
  color: white;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.header-info {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-info h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 600;
}

.access-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.access-badge.super-admin {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.access-badge.admin {
  background: rgba(245, 158, 11, 0.2);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.access-badge.profesional {
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.access-badge.readonly {
  background: rgba(107, 114, 128, 0.2);
  border: 1px solid rgba(107, 114, 128, 0.3);
}

/* ============ ACCESS DENIED ============ */
.access-denied-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 3rem;
}

.access-denied-card {
  background: white;
  border-radius: 16px;
  padding: 3rem;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  border-left: 4px solid #f59e0b;
}

.access-denied-card i {
  font-size: 4rem;
  color: #f59e0b;
  margin-bottom: 1.5rem;
}

.access-denied-card h2 {
  margin: 0 0 1rem 0;
  color: #374151;
  font-size: 1.5rem;
}

.access-denied-card p {
  margin: 0 0 1.5rem 0;
  color: #6b7280;
  line-height: 1.6;
}

.access-info {
  background: #fef3c7;
  border-radius: 8px;
  padding: 1rem;
  margin: 1.5rem 0;
  text-align: left;
}

.access-info p {
  margin: 0.5rem 0;
  font-size: 0.875rem;
}

.btn-back-denied {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #667eea;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-back-denied:hover {
  background: #5a6fd8;
  transform: translateY(-2px);
}

/* ============ LOADING/ERROR ============ */
.loading-container, .error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background: white;
  border-radius: 12px;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.btn-retry {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

/* ============ FILTERS ============ */
.filters-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filters-container {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.filters-container select {
  padding: 0.75rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  min-width: 200px;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 250px;
}

.search-box input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background: white;
}

.search-box i {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
}

.clear-btn {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: #6b7280;
  padding: 0.25rem;
}

.btn-refresh {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

.btn-refresh:hover:not(:disabled) {
  background: #5a6fd8;
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ============ SECTIONS ============ */
.disposiciones-section, .archivos-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.section-header h2, .section-header h3 {
  margin: 0;
  color: #374151;
}

.count-badge {
  background: #f3f4f6;
  color: #6b7280;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
}

.btn-close {
  background: #fee2e2;
  color: #dc2626;
  border: none;
  padding: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
}

/* ============ TABLE ============ */
.table-responsive {
  overflow-x: auto;
}

.disposiciones-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.disposiciones-table th,
.disposiciones-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.disposiciones-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.component-info strong {
  color: #374151;
}

.status-badges {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  text-align: center;
  background: #f3f4f6;
  color: #6b7280;
}

.status-badge.active {
  background: #dcfce7;
  color: #166534;
}

.observaciones-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-edit, .btn-view-files {
  background: none;
  border: 1px solid #d1d5db;
  padding: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
}

.btn-edit {
  color: #667eea;
  border-color: #667eea;
}

.btn-view-files {
  color: #059669;
  border-color: #059669;
}

.btn-view-files.active {
  background: #dcfce7;
}

.btn-edit:hover {
  background: #f0f4ff;
}

.btn-view-files:hover {
  background: #ecfdf5;
}

/* ============ TABLA DE ARCHIVOS ============ */
.archivos-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.archivos-table th,
.archivos-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: middle;
}

.archivos-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
  position: sticky;
  top: 0;
}

.archivo-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.archivo-icon-small {
  font-size: 1.5rem;
  color: #667eea;
  background: #f0f4ff;
  padding: 0.5rem;
  border-radius: 6px;
}

.archivo-nombre {
  font-weight: 500;
  color: #374151;
  word-break: break-all;
}

.archivo-observacion {
  color: #6b7280;
  font-size: 0.875rem;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.archivo-actions-inline {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.btn-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.btn-icon.small {
  width: 32px;
  height: 32px;
}

.btn-icon.primary {
  background: #667eea;
  color: white;
}

.btn-icon.primary:hover {
  background: #5a6fd8;
  transform: translateY(-1px);
}

.btn-icon.success {
  background: #059669;
  color: white;
}

.btn-icon.success:hover {
  background: #047857;
  transform: translateY(-1px);
}

.archivos-table tbody tr:hover {
  background: #f8f9fa;
}

.archivos-table tbody tr:nth-child(even) {
  background: #fafbfc;
}

.archivos-table tbody tr:nth-child(even):hover {
  background: #f1f3f4;
}

/* ============ MODAL ============ */
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
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #374151;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  resize: vertical;
  font-family: inherit;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-primary, .btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-primary:hover {
  background: #5a6fd8;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

/* ============ NOTIFICATION ============ */
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 1000;
  min-width: 300px;
  max-width: 400px;
}

.notification.success {
  border-left: 4px solid #10b981;
}

.notification.error {
  border-left: 4px solid #ef4444;
}

.notification.warning {
  border-left: 4px solid #f59e0b;
}

.notification.info {
  border-left: 4px solid #3b82f6;
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.notification-content i {
  font-size: 1.25rem;
}

.notification.success i {
  color: #10b981;
}

.notification.error i {
  color: #ef4444;
}

.notification.warning i {
  color: #f59e0b;
}

.notification.info i {
  color: #3b82f6;
}

.notification-close {
  background: none;
  border: none;
  cursor: pointer;
  color: #6b7280;
  padding: 0.25rem;
}

/* ============ EMPTY STATE ============ */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  color: #374151;
}

.empty-state p {
  margin: 0;
}

/* ============ RESPONSIVE ============ */
@media (max-width: 768px) {

 .file-info-modal {
    width: 98%;
    max-width: none;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .ruta-container {
    flex-direction: column;
  }
  
  .archivo-actions-inline {
    flex-wrap: wrap;
    justify-content: flex-start;
  }
  
  .btn-icon.small {
    width: 28px;
    height: 28px;
  }
  .productos-detalle-page {
    padding: 1rem;
    gap: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .header-info {
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .filters-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filters-container select,
  .search-box {
    min-width: 100%;
  }
  
  .disposiciones-table {
    font-size: 0.875rem;
  }
  
  /* ✅ ARCHIVOS TABLE RESPONSIVE */
  .archivos-table {
    font-size: 0.875rem;
  }
  
  .archivos-table th,
  .archivos-table td {
    padding: 0.5rem;
  }
  
  .archivo-nombre {
    font-size: 0.8rem;
  }
  
  .archivo-observacion {
    max-width: 150px;
  }
  
  .btn-icon.small {
    width: 28px;
    height: 28px;
  }
  
  .access-denied-card {
    padding: 2rem;
    margin: 1rem;
  }
}
</style>