<template>
  <div class="centro-poblado-detalles">
    <!-- Header con navegación -->
    <div class="page-header">
      <div class="header-content">
        <nav class="breadcrumb">
          <router-link to="/gestion-informacion/centros-poblados" class="breadcrumb-link">
            <i class="material-icons">location_city</i>
            Centros Poblados
          </router-link>
          <i class="material-icons breadcrumb-separator">chevron_right</i>
          <span class="breadcrumb-current">Detalles</span>
        </nav>
        
        <div v-if="loading" class="title-skeleton">
          <div class="skeleton-line long"></div>
          <div class="skeleton-line short"></div>
        </div>
        
        <div v-else-if="centroPoblado" class="title-section">
          <h1 class="page-title">
            <i class="material-icons">place</i>
            {{ centroPoblado.nom_centro_poblado }}
          </h1>
          <div class="subtitle-info">
            <span class="codigo-badge">{{ centroPoblado.cod_centro_poblado }}</span>
            <span class="ubicacion">
              {{ centroPoblado.municipio_nombre }} - {{ centroPoblado.departamento_nombre }}
            </span>
          </div>
        </div>
      </div>
      
      <div v-if="!loading && centroPoblado" class="header-actions">
        <router-link 
          :to="`/gestion-informacion/centros-poblados/${centroPoblado.cod_centro_poblado}/editar`"
          class="btn btn-primary"
        >
          <i class="material-icons">edit</i>
          Editar
        </router-link>
        
        <router-link 
          to="/gestion-informacion/centros-poblados"
          class="btn btn-outline"
        >
          <i class="material-icons">arrow_back</i>
          Volver
        </router-link>
      </div>
    </div>

    <!-- Estados de carga -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Cargando información del centro poblado...</p>
    </div>

    <div v-else-if="error" class="error-container">
      <i class="material-icons">error</i>
      <h3>Error al cargar los datos</h3>
      <p>{{ error }}</p>
      <button @click="cargarDatos" class="btn btn-outline">
        <i class="material-icons">refresh</i>
        Reintentar
      </button>
    </div>

    <!-- Contenido principal -->
    <div v-else-if="centroPoblado" class="details-container">
      
      <!-- Información del Centro Poblado -->
      <div class="info-card">
        <div class="card-header">
          <h2 class="card-title">
            <i class="material-icons">info</i>
            Información del Centro Poblado
          </h2>
        </div>
        
        <div class="card-content">
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Código</span>
              <span class="info-value code-value">{{ centroPoblado.cod_centro_poblado }}</span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Nombre</span>
              <span class="info-value">{{ centroPoblado.nom_centro_poblado }}</span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Área Oficial</span>
              <span class="info-value">
                {{ centroPoblado.area_oficial_ha || 'No especificada' }}
                <span v-if="centroPoblado.area_oficial_ha" class="unit">Ha</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Información de Ubicación -->
      <div class="info-card">
        <div class="card-header">
          <h2 class="card-title">
            <i class="material-icons">location_on</i>
            Ubicación Geográfica
          </h2>
        </div>
        
        <div class="card-content">
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Departamento</span>
              <span class="info-value">{{ centroPoblado.departamento_nombre }}</span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Municipio</span>
              <router-link 
                v-if="centroPoblado.cod_municipio"
                :to="`/gestion-informacion/municipios/${centroPoblado.cod_municipio}`"
                class="info-link"
              >
                {{ centroPoblado.municipio_nombre }}
                <i class="material-icons">open_in_new</i>
              </router-link>
              <span v-else class="info-value">{{ centroPoblado.municipio_nombre }}</span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Código de Municipio</span>
              <span class="info-value code-value">{{ centroPoblado.cod_municipio }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Enlaces Relacionados -->
      <div class="info-card">
        <div class="card-header">
          <h2 class="card-title">
            <i class="material-icons">link</i>
            Enlaces Relacionados
          </h2>
        </div>
        
        <div class="card-content">
          <div class="related-links">
            <router-link 
              v-if="centroPoblado.cod_municipio"
              :to="`/gestion-informacion/municipios/${centroPoblado.cod_municipio}`"
              class="related-link"
            >
              <i class="material-icons">location_city</i>
              <div class="link-content">
                <span class="link-title">Ver Municipio</span>
                <span class="link-description">{{ centroPoblado.municipio_nombre }}</span>
              </div>
              <i class="material-icons">chevron_right</i>
            </router-link>
            
            <router-link 
              to="/gestion-informacion/centros-poblados"
              class="related-link"
            >
              <i class="material-icons">list</i>
              <div class="link-content">
                <span class="link-title">Todos los Centros Poblados</span>
                <span class="link-description">Volver a la lista completa</span>
              </div>
              <i class="material-icons">chevron_right</i>
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Estado sin datos -->
    <div v-else class="empty-container">
      <i class="material-icons">place</i>
      <h3>Centro poblado no encontrado</h3>
      <p>No se pudo encontrar el centro poblado solicitado.</p>
      <router-link to="/gestion-informacion/centros-poblados" class="btn btn-primary">
        <i class="material-icons">arrow_back</i>
        Volver a la Lista
      </router-link>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

// Importar APIs REALES
import { centrosPobladosApi } from '@/api/centrosPoblados'
import { departamentosApi, getMunicipioById } from '@/api/municipios'

// Interface simplificada para el detalle
interface CentroPobladoDetalle {
  cod_centro_poblado: string
  cod_municipio: number
  nom_centro_poblado: string
  area_oficial_ha?: string
  municipio_nombre?: string
  departamento_nombre?: string
}

export default defineComponent({
  name: 'CentrosPobladosDetalles',
  
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    // Estado reactivo
    const loading = ref(true)
    const error = ref<string | null>(null)
    
    // Datos
    const centroPoblado = ref<CentroPobladoDetalle | null>(null)
    const centroId = route.params.id as string
    
    // Método principal para cargar datos
    const cargarDatos = async () => {
      try {
        loading.value = true
        error.value = null
        
        console.log('🔍 Cargando centro poblado:', centroId)
        
        // 1. Cargar datos básicos del centro poblado
        const centroData = await centrosPobladosApi.getById(centroId)
        
        if (!centroData) {
          throw new Error('Centro poblado no encontrado')
        }
        
        console.log('📋 Datos del centro cargados:', centroData)
        
        // 2. Enriquecer con información del municipio y departamento
        let municipioNombre = 'Municipio no encontrado'
        let departamentoNombre = 'Departamento no encontrado'
        
        if (centroData.cod_municipio) {
          try {
            // Cargar información del municipio
            const municipioData = await getMunicipioById(centroData.cod_municipio)
            municipioNombre = municipioData?.nom_municipio || `Municipio ${centroData.cod_municipio}`
            
            console.log('📍 Datos del municipio:', municipioData)
            
            // Cargar información del departamento
            if (municipioData?.cod_depto) {
              try {
                const departamentosData = await departamentosApi.getAll()
                const departamento = departamentosData.find(d => d.cod_depto === municipioData.cod_depto)
                departamentoNombre = departamento?.nom_depto || `Departamento ${municipioData.cod_depto}`
                
                console.log('🗺️ Departamento encontrado:', departamento?.nom_depto)
              } catch (deptoError) {
                console.warn('⚠️ Error cargando departamento:', deptoError)
              }
            }
          } catch (munError) {
            console.warn('⚠️ Error cargando municipio:', munError)
          }
        }
        
        // 3. Construir objeto completo para mostrar
        centroPoblado.value = {
          cod_centro_poblado: centroData.cod_centro_poblado,
          cod_municipio: centroData.cod_municipio,
          nom_centro_poblado: centroData.nom_centro_poblado,
          area_oficial_ha: centroData.area_oficial_ha,
          municipio_nombre: municipioNombre,
          departamento_nombre: departamentoNombre
        }
        
        console.log('✅ Centro poblado completo:', centroPoblado.value)
        
      } catch (err) {
        console.error('❌ Error al cargar datos:', err)
        error.value = err.message || 'Error al cargar la información del centro poblado'
      } finally {
        loading.value = false
      }
    }
    
    // Lifecycle
    onMounted(() => {
      if (centroId) {
        cargarDatos()
      } else {
        error.value = 'ID de centro poblado no proporcionado'
        loading.value = false
      }
    })
    
    return {
      // Estado
      loading,
      error,
      
      // Datos
      centroPoblado,
      
      // Métodos
      cargarDatos
    }
  }
})
</script>

<style scoped>
.centro-poblado-detalles {
  padding: 1.5rem;
  max-width: 1000px;
  margin: 0 auto;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  gap: 2rem;
}

.header-content {
  flex: 1;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.breadcrumb-link {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #3b82f6;
  text-decoration: none;
}

.breadcrumb-link:hover {
  text-decoration: underline;
}

.breadcrumb-separator {
  color: #9ca3af;
  font-size: 1rem;
}

.breadcrumb-current {
  color: #6b7280;
}

.title-skeleton {
  animation: pulse 2s infinite;
}

.skeleton-line {
  height: 1rem;
  background: #e5e7eb;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.skeleton-line.long {
  width: 300px;
  height: 2rem;
}

.skeleton-line.short {
  width: 200px;
}

.title-section {
  margin-bottom: 0;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.75rem 0;
  font-size: 1.875rem;
  font-weight: 600;
  color: #1f2937;
}

.subtitle-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.codigo-badge {
  background: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
  font-family: 'Courier New', monospace;
}

.ubicacion {
  color: #6b7280;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

/* Estados */
.loading-container, .error-container, .empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.error-container i,
.empty-container i {
  font-size: 3rem;
  color: #ef4444;
  margin-bottom: 1rem;
}

.empty-container i {
  color: #6b7280;
}

/* Contenido */
.details-container {
  display: grid;
  gap: 1.5rem;
}

.info-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  padding: 1.5rem 1.5rem 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f8f9fa;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.card-content {
  padding: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  font-size: 1.125rem;
  color: #1f2937;
  font-weight: 500;
  word-break: break-word;
}

.code-value {
  font-family: 'Courier New', monospace;
  background: #f9fafb;
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
  display: inline-block;
}

.unit {
  color: #6b7280;
  font-size: 0.875rem;
  margin-left: 0.25rem;
}

.info-link {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  color: #3b82f6;
  text-decoration: none;
  font-size: 1.125rem;
  font-weight: 500;
}

.info-link:hover {
  text-decoration: underline;
}

.related-links {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.related-link {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  text-decoration: none;
  color: #374151;
  transition: all 0.2s;
  border: 1px solid #e5e7eb;
}

.related-link:hover {
  background: #f3f4f6;
  transform: translateX(4px);
  border-color: #d1d5db;
}

.link-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.link-title {
  font-weight: 600;
  color: #1f2937;
  font-size: 1rem;
}

.link-description {
  font-size: 0.875rem;
  color: #6b7280;
}

/* Botones */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  text-decoration: none;
  border: 1px solid transparent;
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

.btn-outline {
  background: white;
  color: #374151;
  border-color: #d1d5db;
}

.btn-outline:hover {
  background: #f3f4f6;
}

/* Responsive */
@media (max-width: 768px) {
  .centro-poblado-detalles {
    padding: 1rem;
  }
  
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .subtitle-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .header-actions {
    justify-content: stretch;
  }
  
  .header-actions .btn {
    flex: 1;
    justify-content: center;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>