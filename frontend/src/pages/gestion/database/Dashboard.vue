<template>
  <div class="database-dashboard-page" :class="{ 'solo-contenido': !mostrarDashboard }">
    <!-- 🎯 MOSTRAR DASHBOARD SOLO EN RUTA BASE -->
    <div v-if="mostrarDashboard">
      <!-- Hero Section -->
      <div class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">Gestión de Base de Datos</h1>
          <p class="hero-subtitle">
            Centro de administración para la gestión completa de tablas de dominio, 
            archivos municipales y configuraciones del sistema
          </p>
        </div>
        <div class="hero-stats">
          <div class="stat-item">
            <div class="stat-number">{{ globalStats.totalTablas }}</div>
            <div class="stat-label">Tablas Gestionadas</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ globalStats.totalRegistros }}</div>
            <div class="stat-label">Total Registros</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ globalStats.municipiosActivos }}</div>
            <div class="stat-label">Municipios Activos</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions Section -->
    <div class="quick-actions-section">
      <h2 class="section-title">Acciones Rápidas</h2>
      <div class="quick-actions-grid">
        <div class="quick-action-card" @click="navegarA('/gestion-informacion/database/dominios/categorias-insumos')">
          <div class="action-icon categorias">
            <i class="material-icons">category</i>
          </div>
          <div class="action-content">
            <h3>Categorías de Insumos</h3>
            <p>Gestionar categorías para clasificación</p>
            <div class="action-stats">
              <span class="stat-badge">{{ domainStats.categorias || 0 }} registros</span>
            </div>
          </div>
          <i class="material-icons action-arrow">arrow_forward</i>
        </div>

        <div class="quick-action-card" @click="navegarA('/gestion-informacion/database/dominios/tipos-insumos')">
          <div class="action-icon tipos">
            <i class="material-icons">engineering</i>
          </div>
          <div class="action-content">
            <h3>Tipos de Insumos</h3>
            <p>Administrar tipos y formatos</p>
            <div class="action-stats">
              <span class="stat-badge">{{ domainStats.tipos || 0 }} registros</span>
            </div>
          </div>
          <i class="material-icons action-arrow">arrow_forward</i>
        </div>

        <div class="quick-action-card" @click="navegarA('/gestion-informacion/database/preoperacion/archivos')">
          <div class="action-icon preoperacion">
            <i class="material-icons">upload_file</i>
          </div>
          <div class="action-content">
            <h3>Archivos Pre-operación</h3>
            <p>Gestión de archivos municipales</p>
            <div class="action-stats">
              <span class="stat-badge">{{ fileStats.preoperacion || 0 }} archivos</span>
            </div>
          </div>
          <i class="material-icons action-arrow">arrow_forward</i>
        </div>

        <div class="quick-action-card" @click="navegarA('/gestion-informacion/database/postoperacion/archivos')">
          <div class="action-icon postoperacion">
            <i class="material-icons">download</i>
          </div>
          <div class="action-content">
            <h3>Archivos Post-operación</h3>
            <p>Resultados y productos finales</p>
            <div class="action-stats">
              <span class="stat-badge">{{ fileStats.postoperacion || 0 }} archivos</span>
            </div>
          </div>
          <i class="material-icons action-arrow">arrow_forward</i>
        </div>
      </div>
    </div>

    <!-- Sections Overview -->
    <div class="sections-overview">
      <div class="section-card">
        <div class="section-header">
          <div class="section-icon dominios">
            <i class="material-icons">storage</i>
          </div>
          <div class="section-info">
            <h3>Tablas de Dominio</h3>
            <p>Configuraciones maestras del sistema</p>
          </div>
          <div class="section-count">{{ domainTables.length }} tablas</div>
        </div>
        
        <div class="section-content">
          <div class="table-grid">
            <div 
              v-for="table in domainTables" 
              :key="table.id"
              class="table-item"
              @click="navegarA(table.route)"
            >
              <div class="table-icon" :class="table.iconClass">
                <i class="material-icons">{{ table.icon }}</i>
              </div>
              <div class="table-info">
                <h4>{{ table.name }}</h4>
                <p>{{ table.description }}</p>
                <div class="table-meta">
                  <span class="record-count">{{ table.recordCount || 0 }} registros</span>
                  <span class="last-update">{{ formatLastUpdate(table.lastUpdate) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="section-card">
        <div class="section-header">
          <div class="section-icon municipales">
            <i class="material-icons">location_city</i>
          </div>
          <div class="section-info">
            <h3>Tablas Municipales</h3>
            <p>Datos organizados por municipio</p>
          </div>
          <div class="section-count">{{ municipalTables.length }} tipos</div>
        </div>
        
        <div class="section-content">
          <div class="municipal-overview">
            <div 
              v-for="table in municipalTables" 
              :key="table.id"
              class="municipal-item"
              @click="navegarA(table.route)"
            >
              <div class="municipal-header">
                <div class="municipal-icon" :class="table.iconClass">
                  <i class="material-icons">{{ table.icon }}</i>
                </div>
                <div class="municipal-info">
                  <h4>{{ table.name }}</h4>
                  <p>{{ table.description }}</p>
                </div>
              </div>
              
              <div class="municipal-stats">
                <div class="municipal-stat">
                  <span class="stat-value">{{ table.totalFiles || 0 }}</span>
                  <span class="stat-label">Archivos</span>
                </div>
                <div class="municipal-stat">
                  <span class="stat-value">{{ table.municipiosConDatos || 0 }}</span>
                  <span class="stat-label">Municipios</span>
                </div>
                <div class="municipal-stat">
                  <span class="stat-value">{{ formatFileSize(table.totalSize || 0) }}</span>
                  <span class="stat-label">Tamaño</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="recent-activity-section">
      <div class="activity-header">
        <h2 class="section-title">Actividad Reciente</h2>
        <button class="btn btn-outline-primary" @click="verTodaActividad">
          <i class="material-icons">history</i>
          Ver Todo
        </button>
      </div>
      
      <div class="activity-timeline">
        <div 
          v-for="activity in recentActivities" 
          :key="activity.id"
          class="activity-item"
        >
          <div class="activity-icon" :class="activity.type">
            <i class="material-icons">{{ getActivityIcon(activity.type) }}</i>
          </div>
          <div class="activity-content">
            <div class="activity-title">{{ activity.title }}</div>
            <div class="activity-description">{{ activity.description }}</div>
            <div class="activity-meta">
              <span class="activity-user">{{ activity.user }}</span>
              <span class="activity-time">{{ formatActivityTime(activity.timestamp) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- System Status -->
    <div class="system-status-section">
      <h2 class="section-title">Estado del Sistema</h2>
      <div class="status-grid">
        <div class="status-card database">
          <div class="status-icon">
            <i class="material-icons">storage</i>
          </div>
          <div class="status-info">
            <h3>Base de Datos</h3>
            <div class="status-indicator healthy">
              <i class="material-icons">check_circle</i>
              <span>Saludable</span>
            </div>
            <div class="status-details">
              <div class="detail-item">
                <span class="detail-label">Conexiones:</span>
                <span class="detail-value">{{ systemStatus.dbConnections }}/100</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Uso de disco:</span>
                <span class="detail-value">{{ systemStatus.diskUsage }}%</span>
              </div>
            </div>
          </div>
        </div>

        <div class="status-card api">
          <div class="status-icon">
            <i class="material-icons">api</i>
          </div>
          <div class="status-info">
            <h3>API Backend</h3>
            <div class="status-indicator healthy">
              <i class="material-icons">check_circle</i>
              <span>Operativo</span>
            </div>
            <div class="status-details">
              <div class="detail-item">
                <span class="detail-label">Respuesta:</span>
                <span class="detail-value">{{ systemStatus.apiResponseTime }}ms</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Peticiones/min:</span>
                <span class="detail-value">{{ systemStatus.apiRequests }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="status-card backup">
          <div class="status-icon">
            <i class="material-icons">backup</i>
          </div>
          <div class="status-info">
            <h3>Respaldos</h3>
            <div class="status-indicator healthy">
              <i class="material-icons">check_circle</i>
              <span>Actualizado</span>
            </div>
            <div class="status-details">
              <div class="detail-item">
                <span class="detail-label">Último respaldo:</span>
                <span class="detail-value">{{ formatLastBackup(systemStatus.lastBackup) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Tamaño:</span>
                <span class="detail-value">{{ formatFileSize(systemStatus.backupSize) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Floating Action Button -->
    <div class="fab-container">
      <button class="fab-main" @click="toggleFabMenu" :class="{ 'active': fabMenuOpen }">
        <i class="material-icons">{{ fabMenuOpen ? 'close' : 'add' }}</i>
      </button>
      
      <Transition name="fab-menu">
        <div v-if="fabMenuOpen" class="fab-menu">
          <button class="fab-item" @click="abrirConfiguracion" title="Configuración">
            <i class="material-icons">settings</i>
          </button>
          <button class="fab-item" @click="exportarTodo" title="Exportar Todo">
            <i class="material-icons">file_download</i>
          </button>
          <button class="fab-item" @click="generarReporte" title="Generar Reporte">
            <i class="material-icons">assessment</i>
          </button>
        </div>
      </Transition>
    </div>

    <!-- Toast de notificaciones -->
    <Transition name="notification">
      <div v-if="notification.show" :class="notificationClass" class="notification-toast">
        <i class="material-icons">{{ notification.icon }}</i>
        <div class="notification-content">
          <div class="notification-title">{{ notification.title }}</div>
          <div class="notification-message">{{ notification.message }}</div>
        </div>
        <button @click="closeNotification" class="btn-close">
          <i class="material-icons">close</i>
        </button>
      </div>
    </Transition>
    </div>

    <!-- ⭐ CRÍTICO: Router View para mostrar las rutas anidadas -->
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'

// =============== COMPOSABLES ===============
const router = useRouter()
const route = useRoute()

// =============== ESTADO REACTIVO ===============
const fabMenuOpen = ref(false)

// Estadísticas globales
const globalStats = reactive({
  totalTablas: 18,
  totalRegistros: 0,
  municipiosActivos: 0
})

// Estadísticas por sección
const domainStats = reactive({
  categorias: 0,
  tipos: 0,
  entidades: 0,
  estados: 0
})

const fileStats = reactive({
  preoperacion: 0,
  postoperacion: 0
})

// Estado del sistema
const systemStatus = reactive({
  dbConnections: 25,
  diskUsage: 67,
  apiResponseTime: 85,
  apiRequests: 142,
  lastBackup: new Date(),
  backupSize: 2147483648 // 2GB en bytes
})

// Actividad reciente
const recentActivities = ref([
  {
    id: 1,
    type: 'create',
    title: 'Nueva categoría creada',
    description: 'Se agregó la categoría "Imágenes Satelitales"',
    user: 'Juan Pérez',
    timestamp: new Date(Date.now() - 30 * 60 * 1000) // 30 min ago
  },
  {
    id: 2,
    type: 'update',
    title: 'Archivo validado',
    description: 'Archivo cartográfico del municipio de Bogotá validado',
    user: 'María González',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000) // 2 hours ago
  },
  {
    id: 3,
    type: 'upload',
    title: 'Archivos subidos',
    description: '15 archivos pre-operación subidos para Antioquia',
    user: 'Carlos Ruiz',
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000) // 4 hours ago
  },
  {
    id: 4,
    type: 'delete',
    title: 'Registros eliminados',
    description: 'Se eliminaron 3 tipos de insumos obsoletos',
    user: 'Ana López',
    timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000) // 1 day ago
  }
])

// Sistema de notificaciones
const notification = ref({
  show: false,
  type: 'success' as 'success' | 'error' | 'warning' | 'info',
  title: '',
  message: '',
  icon: 'check_circle'
})

// =============== CONFIGURACIÓN DE TABLAS ===============
const domainTables = ref([
  {
    id: 1,
    name: 'Categorías de Insumos',
    description: 'Clasificación de insumos cartográficos',
    route: '/gestion-informacion/database/dominios/categorias-insumos',
    icon: 'category',
    iconClass: 'categorias',
    recordCount: 0,
    lastUpdate: new Date()
  },
  {
    id: 2,
    name: 'Tipos de Insumos',
    description: 'Tipos y formatos de datos',
    route: '/gestion-informacion/database/dominios/tipos-insumos',
    icon: 'engineering',
    iconClass: 'tipos',
    recordCount: 0,
    lastUpdate: new Date()
  },
  {
    id: 3,
    name: 'Estados de Insumos',
    description: 'Estados del proceso de insumos',
    route: '/gestion-informacion/database/dominios/estado-insumos',
    icon: 'assignment_turned_in',
    iconClass: 'estados',
    recordCount: 0,
    lastUpdate: new Date()
  },
  {
    id: 4,
    name: 'Entidades',
    description: 'Entidades responsables',
    route: '/gestion-informacion/database/dominios/entidades-operacion',
    icon: 'business',
    iconClass: 'entidades',
    recordCount: 0,
    lastUpdate: new Date()
  },
  {
    id: 5,
    name: 'Grupos de Operación',
    description: 'Agrupaciones operativas',
    route: '/gestion-informacion/database/dominios/grupos-operacion',
    icon: 'group_work',
    iconClass: 'grupos',
    recordCount: 0,
    lastUpdate: new Date()
  },
  {
    id: 6,
    name: 'Zonas de Operación',
    description: 'Delimitación de zonas',
    route: '/gestion-informacion/database/dominios/zonas-operacion',
    icon: 'map',
    iconClass: 'zonas',
    recordCount: 0,
    lastUpdate: new Date()
  }
])

const municipalTables = ref([
  {
    id: 1,
    name: 'Archivos Pre-operación',
    description: 'Archivos de entrada por municipio',
    route: '/gestion-informacion/database/preoperacion/archivos',
    icon: 'upload_file',
    iconClass: 'preoperacion',
    totalFiles: 0,
    municipiosConDatos: 0,
    totalSize: 0
  },
  {
    id: 2,
    name: 'Rutas Pre-operación',
    description: 'Rutas de directorios preoperativos',
    route: '/gestion-informacion/database/preoperacion/rutas',
    icon: 'folder',
    iconClass: 'rutas-pre',
    totalFiles: 0,
    municipiosConDatos: 0,
    totalSize: 0
  },
  {
    id: 3,
    name: 'Archivos Post-operación',
    description: 'Productos y resultados finales',
    route: '/gestion-informacion/database/postoperacion/archivos',
    icon: 'download',
    iconClass: 'postoperacion',
    totalFiles: 0,
    municipiosConDatos: 0,
    totalSize: 0
  },
  {
    id: 4,
    name: 'Rutas Post-operación',
    description: 'Rutas de productos finales',
    route: '/gestion-informacion/database/postoperacion/rutas',
    icon: 'folder_shared',
    iconClass: 'rutas-post',
    totalFiles: 0,
    municipiosConDatos: 0,
    totalSize: 0
  }
])

// =============== COMPUTED ===============
const mostrarDashboard = computed(() => {
  // Mostrar dashboard solo en la ruta base
  const rutaActual = route.path
  const rutaBase = '/gestion-informacion/database'
  
  // Si estamos exactamente en la ruta base, mostrar dashboard
  // Si estamos en cualquier subruta, NO mostrar dashboard
  return rutaActual === rutaBase || rutaActual === rutaBase + '/'
})

const notificationClass = computed(() => {
  return `notification-toast notification-toast--${notification.value.type}`
})

// =============== MÉTODOS PRINCIPALES ===============
const navegarA = (route: string) => {
  console.log('🧭 Navegando a:', route) // Debug
  router.push(route)
}

const toggleFabMenu = () => {
  fabMenuOpen.value = !fabMenuOpen.value
}

const abrirConfiguracion = () => {
  fabMenuOpen.value = false
  showNotification('info', 'Configuración', 'Abriendo panel de configuración...')
}

const exportarTodo = () => {
  fabMenuOpen.value = false
  showNotification('info', 'Exportación iniciada', 'Generando exportación completa del sistema...')
}

const generarReporte = () => {
  fabMenuOpen.value = false
  showNotification('info', 'Generando reporte', 'Creando reporte consolidado del sistema...')
}

const verTodaActividad = () => {
  showNotification('info', 'Actividad completa', 'Mostrando historial completo de actividades...')
}

// =============== MÉTODOS AUXILIARES ===============
const formatFileSize = (bytes: number): string => {
  if (!bytes) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const formatLastUpdate = (date: Date): string => {
  const now = new Date()
  const diffHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)
  
  if (diffHours < 1) {
    return 'Hace pocos minutos'
  } else if (diffHours < 24) {
    return `Hace ${Math.floor(diffHours)} horas`
  } else {
    return date.toLocaleDateString('es-CO', {
      month: 'short',
      day: '2-digit'
    })
  }
}

const formatActivityTime = (date: Date): string => {
  const now = new Date()
  const diffMinutes = (now.getTime() - date.getTime()) / (1000 * 60)
  
  if (diffMinutes < 60) {
    return `Hace ${Math.floor(diffMinutes)} min`
  } else if (diffMinutes < 1440) {
    return `Hace ${Math.floor(diffMinutes / 60)} h`
  } else {
    return `Hace ${Math.floor(diffMinutes / 1440)} días`
  }
}

const formatLastBackup = (date: Date): string => {
  return date.toLocaleDateString('es-CO', {
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getActivityIcon = (type: string): string => {
  const iconMap: Record<string, string> = {
    'create': 'add_circle',
    'update': 'edit',
    'delete': 'delete',
    'upload': 'upload',
    'download': 'download',
    'validate': 'verified'
  }
  return iconMap[type] || 'info'
}

const showNotification = (
  type: 'success' | 'error' | 'warning' | 'info',
  title: string,
  message: string
) => {
  const icons = {
    success: 'check_circle',
    error: 'error',
    warning: 'warning',
    info: 'info'
  }
  
  notification.value = {
    show: true,
    type,
    title,
    message,
    icon: icons[type]
  }
  
  const duration = type === 'error' ? 6000 : 4000
  setTimeout(() => {
    closeNotification()
  }, duration)
}

const closeNotification = () => {
  notification.value.show = false
}

// =============== CARGA DE DATOS ===============
const cargarEstadisticas = async () => {
  try {
    // Simular carga de estadísticas reales
    globalStats.totalRegistros = 12547
    globalStats.municipiosActivos = 1102
    
    domainStats.categorias = 25
    domainStats.tipos = 18
    domainStats.entidades = 42
    domainStats.estados = 8
    
    fileStats.preoperacion = 3842
    fileStats.postoperacion = 2156
    
  } catch (error) {
    console.error('Error cargando estadísticas:', error)
  }
}

const actualizarContadores = () => {
  // Actualizar contadores de las tablas
  domainTables.value.forEach(table => {
    switch (table.id) {
      case 1: table.recordCount = domainStats.categorias; break
      case 2: table.recordCount = domainStats.tipos; break
      case 3: table.recordCount = domainStats.estados; break
      case 4: table.recordCount = domainStats.entidades; break
      default: table.recordCount = Math.floor(Math.random() * 50) + 10
    }
  })
  
  municipalTables.value.forEach(table => {
    switch (table.id) {
      case 1: 
        table.totalFiles = fileStats.preoperacion
        table.totalSize = 5368709120 // 5GB
        break
      case 3: 
        table.totalFiles = fileStats.postoperacion
        table.totalSize = 3221225472 // 3GB
        break
      default:
        table.totalFiles = Math.floor(Math.random() * 1000) + 100
        table.totalSize = Math.floor(Math.random() * 2147483648) + 1073741824
    }
    table.municipiosConDatos = Math.floor(Math.random() * 300) + 50
  })
}

// =============== LIFECYCLE ===============
onMounted(async () => {
  await cargarEstadisticas()
  actualizarContadores()
  
  // Mostrar notificación de bienvenida
  setTimeout(() => {
    showNotification(
      'info',
      'Bienvenido',
      'Sistema de gestión de base de datos cargado correctamente'
    )
  }, 1000)
})
</script>

<style scoped>
.database-dashboard-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding-bottom: 2rem;
}

/* Cuando solo se muestra el contenido específico */
.database-dashboard-page.solo-contenido {
  background: #f8f9fa;
  padding: 0;
}

.database-dashboard-page.solo-contenido > :last-child {
  min-height: 100vh;
  width: 100%;
}

/* Hero Section */
.hero-section {
  padding: 4rem 2rem;
  text-align: center;
  color: white;
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
}

.hero-text {
  margin-bottom: 3rem;
}

.hero-title {
  font-size: 4rem;
  font-weight: 800;
  margin: 0 0 1rem;
  text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.3);
  letter-spacing: -1px;
}

.hero-subtitle {
  font-size: 1.3rem;
  margin: 0;
  opacity: 0.9;
  font-weight: 300;
  line-height: 1.6;
  max-width: 800px;
  margin: 0 auto;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.stat-item {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.2);
}

.stat-number {
  font-size: 3rem;
  font-weight: 700;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 1rem;
  opacity: 0.9;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 500;
}

/* Quick Actions */
.quick-actions-section {
  margin: 0 2rem 3rem;
}

.section-title {
  color: white;
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 2rem;
  text-align: center;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.quick-action-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.quick-action-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.2);
  background: white;
}

.action-icon {
  width: 60px;
  height: 60px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.action-icon.categorias {
  background: linear-gradient(135deg, #ff6b6b, #ee5a52);
}

.action-icon.tipos {
  background: linear-gradient(135deg, #4ecdc4, #44a08d);
}

.action-icon.preoperacion {
  background: linear-gradient(135deg, #45b7d1, #96c93d);
}

.action-icon.postoperacion {
  background: linear-gradient(135deg, #f093fb, #f5576c);
}

.action-icon .material-icons {
  color: white;
  font-size: 30px;
}

.action-content {
  flex: 1;
}

.action-content h3 {
  margin: 0 0 0.5rem;
  color: #333;
  font-size: 1.3rem;
  font-weight: 600;
}

.action-content p {
  margin: 0 0 1rem;
  color: #666;
  font-size: 0.95rem;
  line-height: 1.4;
}

.action-stats {
  display: flex;
  gap: 0.5rem;
}

.stat-badge {
  background: #f8f9fa;
  color: #495057;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.action-arrow {
  color: #ccc;
  font-size: 24px;
  transition: all 0.3s ease;
}

.quick-action-card:hover .action-arrow {
  color: #667eea;
  transform: translateX(5px);
}

/* Sections Overview */
.sections-overview {
  margin: 0 2rem 3rem;
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

.section-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.section-header {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  border-bottom: 1px solid #dee2e6;
}

.section-icon {
  width: 60px;
  height: 60px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.section-icon.dominios {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.section-icon.municipales {
  background: linear-gradient(135deg, #f093fb, #f5576c);
}

.section-icon .material-icons {
  color: white;
  font-size: 30px;
}

.section-info {
  flex: 1;
}

.section-info h3 {
  margin: 0 0 0.5rem;
  color: #333;
  font-size: 1.5rem;
  font-weight: 600;
}

.section-info p {
  margin: 0;
  color: #666;
  font-size: 1rem;
}

.section-count {
  background: white;
  color: #495057;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-content {
  padding: 2rem;
}

/* Domain Tables Grid */
.table-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.table-item {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.table-item:hover {
  background: white;
  border-color: #667eea;
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.table-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.table-icon.categorias { background: linear-gradient(135deg, #ff6b6b, #ee5a52); }
.table-icon.tipos { background: linear-gradient(135deg, #4ecdc4, #44a08d); }
.table-icon.estados { background: linear-gradient(135deg, #45b7d1, #96c93d); }
.table-icon.entidades { background: linear-gradient(135deg, #f093fb, #f5576c); }
.table-icon.grupos { background: linear-gradient(135deg, #ffeaa7, #fdcb6e); }
.table-icon.zonas { background: linear-gradient(135deg, #fd79a8, #e84393); }

.table-icon .material-icons {
  color: white;
  font-size: 20px;
}

.table-info h4 {
  margin: 0 0 0.5rem;
  color: #333;
  font-size: 1.1rem;
  font-weight: 600;
}

.table-info p {
  margin: 0 0 1rem;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
}

.table-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
}

.record-count {
  color: #495057;
  font-weight: 600;
}

.last-update {
  color: #6c757d;
}

/* Municipal Tables */
.municipal-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.municipal-item {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.municipal-item:hover {
  background: white;
  border-color: #f093fb;
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.municipal-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.municipal-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.municipal-icon.preoperacion { background: linear-gradient(135deg, #45b7d1, #96c93d); }
.municipal-icon.postoperacion { background: linear-gradient(135deg, #f093fb, #f5576c); }
.municipal-icon.rutas-pre { background: linear-gradient(135deg, #4ecdc4, #44a08d); }
.municipal-icon.rutas-post { background: linear-gradient(135deg, #fd79a8, #e84393); }

.municipal-icon .material-icons {
  color: white;
  font-size: 24px;
}

.municipal-info h4 {
  margin: 0 0 0.25rem;
  color: #333;
  font-size: 1.2rem;
  font-weight: 600;
}

.municipal-info p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

.municipal-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.municipal-stat {
  text-align: center;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.municipal-stat .stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 0.25rem;
}

.municipal-stat .stat-label {
  font-size: 0.8rem;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Recent Activity */
.recent-activity-section {
  margin: 0 2rem 3rem;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.activity-timeline {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.activity-item {
  display: flex;
  gap: 1.5rem;
  padding: 1.5rem 0;
  border-bottom: 1px solid #e9ecef;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon.create { background: linear-gradient(135deg, #4ecdc4, #44a08d); }
.activity-icon.update { background: linear-gradient(135deg, #45b7d1, #96c93d); }
.activity-icon.upload { background: linear-gradient(135deg, #f093fb, #f5576c); }
.activity-icon.delete { background: linear-gradient(135deg, #ff6b6b, #ee5a52); }

.activity-icon .material-icons {
  color: white;
  font-size: 20px;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 0.25rem;
}

.activity-description {
  color: #666;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.activity-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: #6c757d;
}

/* System Status */
.system-status-section {
  margin: 0 2rem 3rem;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.status-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.status-icon {
  width: 60px;
  height: 60px;
  border-radius: 15px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.status-icon .material-icons {
  color: white;
  font-size: 30px;
}

.status-info h3 {
  margin: 0 0 1rem;
  color: #333;
  font-size: 1.3rem;
  font-weight: 600;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.status-indicator.healthy {
  color: #28a745;
}

.status-indicator .material-icons {
  font-size: 20px;
}

.status-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  color: #666;
  font-size: 0.9rem;
}

.detail-value {
  color: #333;
  font-weight: 600;
  font-size: 0.9rem;
}

/* FAB */
.fab-container {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 1000;
}

.fab-main {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.fab-main:hover,
.fab-main.active {
  transform: scale(1.1);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
}

.fab-main .material-icons {
  font-size: 28px;
  transition: transform 0.3s ease;
}

.fab-main.active .material-icons {
  transform: rotate(45deg);
}

.fab-menu {
  position: absolute;
  bottom: 80px;
  right: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.fab-item {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  color: #667eea;
  border: none;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fab-item:hover {
  background: white;
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.fab-item .material-icons {
  font-size: 20px;
}

.fab-menu-enter-active,
.fab-menu-leave-active {
  transition: all 0.3s ease;
}

.fab-menu-enter-from,
.fab-menu-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.8);
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  text-decoration: none;
  border: 2px solid;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.btn-outline-primary {
  color: white;
  border-color: rgba(255, 255, 255, 0.3);
  background: transparent;
}

.btn-outline-primary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: white;
}

/* Notificaciones */
.notification-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  z-index: 1060;
  min-width: 350px;
  max-width: 500px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 0.25rem;
}

.notification-message {
  font-size: 0.9rem;
  opacity: 0.9;
  line-height: 1.4;
}

.notification-toast--success {
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.95), rgba(32, 134, 55, 0.95));
  color: white;
}

.notification-toast--error {
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.95), rgba(176, 42, 55, 0.95));
  color: white;
}

.notification-toast--warning {
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.95), rgba(204, 154, 5, 0.95));
  color: #333;
}

.notification-toast--info {
  background: linear-gradient(135deg, rgba(23, 162, 184, 0.95), rgba(18, 130, 147, 0.95));
  color: white;
}

.notification-toast .material-icons {
  font-size: 1.5rem;
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.notification-toast .btn-close {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 50%;
  transition: all 0.2s;
  opacity: 0.8;
  flex-shrink: 0;
}

.notification-toast .btn-close:hover {
  opacity: 1;
  background-color: rgba(255, 255, 255, 0.2);
}

.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

/* Responsive */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .quick-actions-grid {
    grid-template-columns: 1fr;
  }
  
  .quick-action-card {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .sections-overview {
    margin: 0 1rem 2rem;
  }
  
  .section-header {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .table-grid,
  .municipal-overview {
    grid-template-columns: 1fr;
  }
  
  .municipal-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .fab-container {
    bottom: 20px;
    right: 20px;
  }
  
  .notification-toast {
    top: 10px;
    right: 10px;
    left: 10px;
    min-width: auto;
    max-width: none;
  }
}

@media (max-width: 480px) {
  .hero-stats,
  .municipal-stats {
    grid-template-columns: 1fr;
  }
  
  .quick-action-card {
    padding: 1.5rem;
  }
  
  .activity-header {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>