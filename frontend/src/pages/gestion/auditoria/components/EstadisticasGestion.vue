<template>
    <div class="stats-cards">
      <div v-if="cargando" class="loading-container">
        <div class="spinner"></div>
        <span>Cargando estadísticas...</span>
      </div>
      
      <div v-else-if="error" class="error-container">
        <i class="material-icons">error</i>
        <span>{{ error }}</span>
        <button @click="cargarEstadisticas">Reintentar</button>
      </div>
      
      <template v-else>
        <div class="stat-card">
          <div class="stat-icon">
            <i class="material-icons">location_city</i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ estadisticas.total_municipios_pre }}</h3>
            <p class="stat-label">Municipios</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="material-icons">folder</i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ estadisticas.total_archivos_pre }}</h3>
            <p class="stat-label">Insumos</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="material-icons">category</i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ conteoClasificaciones }}</h3>
            <p class="stat-label">Clasificaciones</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="material-icons">list_alt</i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ conteoDetalles }}</h3>
            <p class="stat-label">Detalles</p>
          </div>
        </div>
        
        <!-- Agregamos el recuadro para conceptos -->
        <div class="stat-card">
          <div class="stat-icon">
            <i class="material-icons">comment</i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ conteoConceptos }}</h3>
            <p class="stat-label">Conceptos</p>
          </div>
        </div>
      </template>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, onMounted } from 'vue'
  import { getEstadisticasDashboard } from '@/api/estadisticas'
  import type { EstadisticasDashboard } from '@/api/estadisticas'
  import api from '@/api/config'
  
  export default defineComponent({
    name: 'EstadisticasGestion',
    
    setup() {
      // Estado
      const estadisticas = ref<EstadisticasDashboard>({
        total_municipios_pre: 0,
        total_municipios_post: 0,
        total_archivos_pre: 0,
        total_archivos_post: 0,
        total_territoriales: 0,
        total_profesionales_las: 0,
        total_profesionales_pas: 0,
        total_municipios_sin_insumos: 0
      })
      
      // Conteos directos desde la base de datos
      const conteoClasificaciones = ref<number>(0)
      const conteoDetalles = ref<number>(0)
      const conteoConceptos = ref<number>(0)
      
      const cargando = ref(false)
      const error = ref<string | null>(null)
      
      // Función para obtener conteo directo de clasificaciones
      const cargarConteoClasificaciones = async () => {
        try {
          const response = await api.get('/preoperacion/clasificaciones/', { 
            params: { limit: 1 } // Solo pedimos un elemento para obtener el conteo total
          })
          
          // La respuesta probablemente sea paginada con un campo 'count' que tiene el total
          if (response && typeof response.count === 'number') {
            conteoClasificaciones.value = response.count
          } else if (Array.isArray(response) && response.length > 0) {
            // Si es un array, usamos la longitud como primera aproximación
            conteoClasificaciones.value = response.length
          } else if (response && typeof response.results === 'object' && Array.isArray(response.results)) {
            // Si es una respuesta paginada sin count explícito
            conteoClasificaciones.value = response.results.length
          } else {
            console.warn('No se pudo determinar el conteo de clasificaciones desde la respuesta de la API')
          }
        } catch (err) {
          console.error('Error al obtener conteo de clasificaciones:', err)
        }
      }
      
      // Función para obtener conteo directo de detalles
      const cargarConteoDetalles = async () => {
        try {
          const response = await api.get('/preoperacion/detalles-insumo/', { 
            params: { limit: 1 } // Solo pedimos un elemento para obtener el conteo total
          })
          
          // La respuesta probablemente sea paginada con un campo 'count' que tiene el total
          if (response && typeof response.count === 'number') {
            conteoDetalles.value = response.count
          } else if (Array.isArray(response) && response.length > 0) {
            // Si es un array, usamos la longitud como primera aproximación
            conteoDetalles.value = response.length
          } else if (response && typeof response.results === 'object' && Array.isArray(response.results)) {
            // Si es una respuesta paginada sin count explícito
            conteoDetalles.value = response.results.length
          } else {
            console.warn('No se pudo determinar el conteo de detalles desde la respuesta de la API')
          }
        } catch (err) {
          console.error('Error al obtener conteo de detalles:', err)
        }
      }
      
      // Función para obtener conteo directo de conceptos
      const cargarConteoConceptos = async () => {
        try {
          const response = await api.get('/preoperacion/conceptos/', { 
            params: { limit: 1 } // Solo pedimos un elemento para obtener el conteo total
          })
          
          // La respuesta probablemente sea paginada con un campo 'count' que tiene el total
          if (response && typeof response.count === 'number') {
            conteoConceptos.value = response.count
          } else if (Array.isArray(response) && response.length > 0) {
            // Si es un array, usamos la longitud como primera aproximación
            conteoConceptos.value = response.length
          } else if (response && typeof response.results === 'object' && Array.isArray(response.results)) {
            // Si es una respuesta paginada sin count explícito
            conteoConceptos.value = response.results.length
          } else {
            console.warn('No se pudo determinar el conteo de conceptos desde la respuesta de la API')
          }
        } catch (err) {
          console.error('Error al obtener conteo de conceptos:', err)
        }
      }
      
      // Cargar estadísticas
      const cargarEstadisticas = async () => {
        try {
          cargando.value = true
          error.value = null
          
          console.log("Iniciando carga de estadísticas del dashboard de gestión...")
          
          // Llamar a la API de estadísticas generales
          const data = await getEstadisticasDashboard()
          
          console.log("Datos de estadísticas recibidos:", data)
          
          // Actualizar estado con los datos de la API
          estadisticas.value = data
          
          // Cargar conteos específicos directamente
          await Promise.all([
            cargarConteoClasificaciones(),
            cargarConteoDetalles(),
            cargarConteoConceptos()
          ])
          
          return true
        } catch (err: any) {
          console.error('Error al cargar estadísticas del dashboard de gestión:', err)
          
          // Mostrar mensaje de error amigable
          error.value = 'Error al cargar estadísticas. Por favor, intente de nuevo más tarde.'
          
          // Registrar el error detallado en la consola
          if (err.response) {
            console.error('Error de respuesta:', {
              status: err.response.status,
              data: err.response.data
            })
          } else if (err.request) {
            console.error('Error de solicitud (sin respuesta):', err.request)
          } else {
            console.error('Error de configuración:', err.message)
          }
          
          return false
        } finally {
          cargando.value = false
        }
      }
      
      // Cargar estadísticas al montar el componente
      onMounted(() => {
        cargarEstadisticas()
      })
      
      return {
        estadisticas,
        conteoClasificaciones,
        conteoDetalles,
        conteoConceptos,
        cargando,
        error,
        cargarEstadisticas
      }
    }
  })
  </script>
  
  <style scoped>
  /* Estilos sin cambios */
  .stats-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1.5rem;
  }
  
  .stat-card {
    background-color: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  
  .stat-icon {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    background-color: rgba(0, 123, 255, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .stat-icon i {
    font-size: 2rem;
    color: #007bff;
  }
  
  .stat-content {
    flex: 1;
  }
  
  .stat-value {
    font-size: 1.8rem;
    font-weight: 600;
    margin: 0 0 0.25rem;
    color: #343a40;
  }
  
  .stat-label {
    margin: 0;
    color: #6c757d;
    font-size: 0.9rem;
  }
  
  .loading-container,
  .error-container {
    grid-column: 1 / -1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    text-align: center;
    color: #6c757d;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  }
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #007bff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .error-container i {
    font-size: 3rem;
    color: #dc3545;
    margin-bottom: 0.75rem;
  }
  
  .error-container button {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .error-container button:hover {
    background-color: #0069d9;
  }
  
  @media (max-width: 768px) {
    .stats-cards {
      grid-template-columns: repeat(2, 1fr);
    }
    
    .stat-value {
      font-size: 1.5rem;
    }
  }
  
  @media (max-width: 576px) {
    .stats-cards {
      grid-template-columns: 1fr;
    }
  }
  </style>