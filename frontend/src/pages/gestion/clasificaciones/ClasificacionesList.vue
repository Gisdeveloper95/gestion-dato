<template>
    <div class="clasificaciones-list">
      <div class="list-header">
        <h2 class="list-title">
          <i class="material-icons">category</i>
          Clasificaciones de Insumos
        </h2>
        
        <div class="header-actions">
          <div class="search-box">
            <i class="material-icons">search</i>
            <input 
              type="text" 
              v-model="searchQuery" 
              @input="handleSearch" 
              placeholder="Buscar clasificación..."
            />
            <button v-if="searchQuery" @click="clearSearch">
              <i class="material-icons">close</i>
            </button>
          </div>
          
          <button 
            v-if="puedeCrear" 
            class="btn-add" 
            @click="mostrarFormulario()"
            title="Añadir clasificación"
          >
            <i class="material-icons">add</i>
            Nueva Clasificación
          </button>
        </div>
      </div>
      
      <div class="filters-row">
        <div class="filter-group">
          <label for="insumo-filter">Filtrar por Insumo:</label>
          <select id="insumo-filter" v-model="filtros.insumo" @change="aplicarFiltros">
            <option value="">Todos los insumos</option>
            <option 
              v-for="insumo in insumos" 
              :key="insumo.cod_insumo" 
              :value="insumo.cod_insumo"
            >
              {{ insumo.municipio?.nom_municipio }} - {{ insumo.categoria?.nom_categoria }}
            </option>
          </select>
        </div>
        
        <div class="actions-group">
          <button class="btn-filter" @click="aplicarFiltros">
            <i class="material-icons">filter_list</i>
            Filtrar
          </button>
          
          <button class="btn-clear" @click="limpiarFiltros">
            <i class="material-icons">clear_all</i>
            Limpiar
          </button>
        </div>
      </div>
      
      <!-- Estado de carga -->
      <div v-if="cargando" class="loading-container">
        <div class="spinner"></div>
        <span>Cargando clasificaciones...</span>
      </div>
      
      <!-- Mensaje de error -->
      <div v-else-if="error" class="error-container">
        <i class="material-icons">error</i>
        <span>{{ error }}</span>
        <button @click="cargarClasificaciones">Reintentar</button>
      </div>
      
      <!-- Mensaje cuando no hay resultados -->
      <div v-else-if="clasificacionesFiltradas.length === 0" class="empty-container">
        <i class="material-icons">category</i>
        <span>No se encontraron clasificaciones</span>
        <p v-if="searchQuery || filtros.insumo">Intente con otros criterios de búsqueda o filtros</p>
        <button 
          v-if="puedeCrear" 
          class="btn-primary" 
          @click="mostrarFormulario()"
        >
          Crear Nueva Clasificación
        </button>
      </div>
      
      <!-- Lista de clasificaciones -->
      <div v-else class="clasificaciones-grid">
        <div 
          v-for="clasificacion in clasificacionesPaginadas" 
          :key="clasificacion.cod_clasificacion" 
          class="clasificacion-card"
        >
          <div class="card-header">
            <h3 class="card-title">{{ clasificacion.nombre }}</h3>
            <div class="card-actions">
              <button 
                class="action-btn"
                @click="verDetalles(clasificacion)"
                title="Ver detalles"
              >
                <i class="material-icons">visibility</i>
              </button>
              
              <button 
                v-if="puedeEditar"
                class="action-btn"
                @click="editarClasificacion(clasificacion)"
                title="Editar"
              >
                <i class="material-icons">edit</i>
              </button>
              
              <button 
                v-if="puedeEliminar"
                class="action-btn delete"
                @click="confirmarEliminacion(clasificacion)"
                title="Eliminar"
              >
                <i class="material-icons">delete</i>
              </button>
            </div>
          </div>
          
          <div class="card-body">
            <div class="info-item">
              <span class="info-label">Insumo:</span>
              <span class="info-value">
                {{ clasificacion.insumo?.municipio?.nom_municipio }} - 
                {{ clasificacion.insumo?.categoria?.nom_categoria }}
              </span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Código:</span>
              <span class="info-value">{{ clasificacion.cod_clasificacion }}</span>
            </div>
            
            <div v-if="clasificacion.ruta" class="info-item">
              <span class="info-label">Ruta:</span>
              <span class="info-value path">{{ linuxToWindowsPath(clasificacion.ruta) }}</span>
            </div>
            
            <div v-if="clasificacion.observacion" class="info-item">
              <span class="info-label">Observación:</span>
              <p class="info-value description">{{ clasificacion.observacion }}</p>
            </div>
          </div>
          
          <div class="card-footer">
            <button 
              class="btn-text"
              @click="verDetalleCompleto(clasificacion)"
            >
              Ver detalle completo
              <i class="material-icons">arrow_forward</i>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Paginación -->
      <div v-if="clasificacionesFiltradas.length > elementosPorPagina" class="pagination-container">
        <button 
          class="pagination-btn"
          @click="irAPagina(paginaActual - 1)"
          :disabled="paginaActual === 1"
        >
          <i class="material-icons">chevron_left</i>
        </button>
        
        <span 
          v-for="pagina in paginas" 
          :key="pagina.numero"
          :class="{ 
            'page-number': true, 
            'active': pagina.numero === paginaActual,
            'ellipsis': pagina.esEllipsis
          }"
          @click="pagina.esEllipsis ? null : irAPagina(pagina.numero)"
        >
          {{ pagina.esEllipsis ? '...' : pagina.numero }}
        </span>
        
        <button 
          class="pagination-btn"
          @click="irAPagina(paginaActual + 1)"
          :disabled="paginaActual >= totalPaginas"
        >
          <i class="material-icons">chevron_right</i>
        </button>
      </div>
      
      <!-- Modal de confirmación de eliminación -->
      <div v-if="mostrarConfirmacion" class="modal-backdrop" @click="cancelarEliminacion">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">Confirmar Eliminación</h3>
            <button class="close-btn" @click="cancelarEliminacion">
              <i class="material-icons">close</i>
            </button>
          </div>
          
          <div class="modal-body">
            <p>¿Está seguro que desea eliminar la clasificación <strong>{{ clasificacionAEliminar?.nombre }}</strong>?</p>
            <p class="warning-text">Esta acción no se puede deshacer.</p>
          </div>
          
          <div class="modal-footer">
            <button class="btn-cancel" @click="cancelarEliminacion">
              Cancelar
            </button>
            <button class="btn-danger" @click="eliminarClasificacion">
              <i class="material-icons">delete</i>
              Confirmar Eliminación
            </button>
          </div>
        </div>
      </div>
      
      <!-- Modal para el formulario de clasificación -->
      <div v-if="mostrarModal" class="modal-backdrop" @click="cerrarFormulario">
        <div class="modal-container form-modal" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">
              {{ modoEdicion ? 'Editar' : 'Nueva' }} Clasificación
            </h3>
            <button class="close-btn" @click="cerrarFormulario">
              <i class="material-icons">close</i>
            </button>
          </div>
          
          <div class="modal-body">
            <ClasificacionForm 
              :clasificacion="clasificacionEnEdicion"
              :insumos="insumos"
              :modo-edicion="modoEdicion"
              @guardar="guardarClasificacion"
              @cancelar="cerrarFormulario"
            />
          </div>
        </div>
      </div>
      
      <!-- Modal para ver detalles completos -->
      <div v-if="mostrarDetalles" class="modal-backdrop" @click="cerrarDetalles">
        <div class="modal-container details-modal" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">Detalle de Clasificación</h3>
            <button class="close-btn" @click="cerrarDetalles">
              <i class="material-icons">close</i>
            </button>
          </div>
          
          <div class="modal-body" v-if="clasificacionDetalle">
            <div class="detail-section">
              <h4>Información Básica</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <span class="detail-label">Código:</span>
                  <span class="detail-value">{{ clasificacionDetalle.cod_clasificacion }}</span>
                </div>
                
                <div class="detail-item">
                  <span class="detail-label">Nombre:</span>
                  <span class="detail-value">{{ clasificacionDetalle.nombre }}</span>
                </div>
                
                <div class="detail-item">
                  <span class="detail-label">Insumo:</span>
                  <span class="detail-value">
                    {{ clasificacionDetalle.insumo?.municipio?.nom_municipio }} - 
                    {{ clasificacionDetalle.insumo?.categoria?.nom_categoria }}
                  </span>
                </div>
                
                <div class="detail-item">
                  <span class="detail-label">Tipo de Insumo:</span>
                  <span class="detail-value">{{ clasificacionDetalle.insumo?.tipo_insumo }}</span>
                </div>
              </div>
            </div>
            
            <div class="detail-section">
              <h4>Detalles Adicionales</h4>
              <div class="detail-item full-width">
                <span class="detail-label">Ruta:</span>
                <span class="detail-value path">{{ linuxToWindowsPath(clasificacionDetalle.ruta) || 'No especificada' }}</span>
              </div>
              
              <div class="detail-item full-width">
                <span class="detail-label">Observación:</span>
                <p class="detail-value description">{{ clasificacionDetalle.observacion || 'Sin observaciones' }}</p>
              </div>
              
              <div class="detail-item full-width">
                <span class="detail-label">Descripción:</span>
                <p class="detail-value description">{{ clasificacionDetalle.descripcion || 'Sin descripción' }}</p>
              </div>
            </div>
            
            <div class="detail-section" v-if="archivosAsociados && archivosAsociados.length > 0">
              <h4>Archivos Asociados</h4>
              <ul class="files-list">
                <li v-for="(archivo, index) in archivosAsociados" :key="index" class="file-item">
                  <i class="material-icons">insert_drive_file</i>
                  <span class="file-name">{{ archivo.nombre_insumo }}</span>
                  <span class="file-date">{{ formatearFecha(archivo.fecha_disposicion) }}</span>
                </li>
              </ul>
            </div>
            
            <div class="detail-section" v-else>
              <h4>Archivos Asociados</h4>
              <p class="empty-message">No hay archivos asociados a esta clasificación</p>
            </div>
          </div>
          
          <div class="modal-footer">
            <button 
              v-if="puedeEditar" 
              class="btn-primary" 
              @click="editarClasificacion(clasificacionDetalle)"
            >
              <i class="material-icons">edit</i>
              Editar
            </button>
            
            <button class="btn-secondary" @click="cerrarDetalles">
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, computed, onMounted, watch } from 'vue'
import { linuxToWindowsPath } from '@/utils/pathUtils'
  import { useRouter } from 'vue-router'
  import { useAuthStore } from '@/store/auth'
  import ClasificacionForm from './ClasificacionForm.vue'
  import { format, parseISO } from 'date-fns'
  import { es } from 'date-fns/locale'
  import type { ClasificacionInsumo, Insumo } from '@/models/municipio'
  
  // Simulación de servicios API (reemplazar por llamadas reales)
  const getClasificaciones = async (): Promise<ClasificacionInsumo[]> => {
    // Simular carga
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // Datos de ejemplo
    return [
      {
        cod_clasificacion: 1,
        cod_insumo: 101,
        nombre: "Cartografía Base Digital",
        ruta: "/carpetas/municipios/101/cartografia/",
        observacion: "Archivos actualizados en 2024",
        descripcion: "Contiene la cartografía base del municipio en formato digital",
        insumo: {
          cod_insumo: 101,
          cod_municipio: 1001,
          cod_categoria: 1,
          tipo_insumo: "primario",
          municipio: {
            cod_municipio: 1001,
            nom_municipio: "Bogotá",
            cod_depto: 11
          },
          categoria: {
            cod_categoria: 1,
            nom_categoria: "Cartografía Básica"
          }
        }
      },
      {
        cod_clasificacion: 2,
        cod_insumo: 102,
        nombre: "Ortofotomosaicos",
        ruta: "/carpetas/municipios/101/ortofotomosaicos/",
        observacion: "Resolución de 10cm",
        descripcion: "Mosaico de ortofotografías aéreas georeferenciadas",
        insumo: {
          cod_insumo: 102,
          cod_municipio: 1001,
          cod_categoria: 1,
          tipo_insumo: "primario",
          municipio: {
            cod_municipio: 1001,
            nom_municipio: "Bogotá",
            cod_depto: 11
          },
          categoria: {
            cod_categoria: 1,
            nom_categoria: "Cartografía Básica"
          }
        }
      },
      {
        cod_clasificacion: 3,
        cod_insumo: 201,
        nombre: "Modelo Digital de Terreno",
        ruta: "/carpetas/municipios/201/mdt/",
        observacion: "Resolución de 5m",
        descripcion: "Modelo digital de terreno con precisión mejorada",
        insumo: {
          cod_insumo: 201,
          cod_municipio: 1002,
          cod_categoria: 2,
          tipo_insumo: "primario",
          municipio: {
            cod_municipio: 1002,
            nom_municipio: "Medellín",
            cod_depto: 5
          },
          categoria: {
            cod_categoria: 2,
            nom_categoria: "Estudio Agrológico"
          }
        }
      },
      {
        cod_clasificacion: 4,
        cod_insumo: 301,
        nombre: "Registros Catastrales 2023",
        ruta: "/carpetas/municipios/301/registros/",
        observacion: "Actualizado en enero de 2024",
        descripcion: "Base de datos de registros catastrales completa",
        insumo: {
          cod_insumo: 301,
          cod_municipio: 1003,
          cod_categoria: 3,
          tipo_insumo: "secundario",
          municipio: {
            cod_municipio: 1003,
            nom_municipio: "Cali",
            cod_depto: 76
          },
          categoria: {
            cod_categoria: 3,
            nom_categoria: "Información Catastral"
          }
        }
      },
      {
        cod_clasificacion: 5,
        cod_insumo: 401,
        nombre: "Límites Municipales",
        ruta: "/carpetas/municipios/401/limites/",
        observacion: "Versión actualizada 2023",
        descripcion: "Archivo shape con límites municipales aprobados",
        insumo: {
          cod_insumo: 401,
          cod_municipio: 1004,
          cod_categoria: 4,
          tipo_insumo: "primario",
          municipio: {
            cod_municipio: 1004,
            nom_municipio: "Barranquilla",
            cod_depto: 8
          },
          categoria: {
            cod_categoria: 4,
            nom_categoria: "Deslinde"
          }
        }
      }
    ]
  }
  
  const getInsumos = async (): Promise<Insumo[]> => {
    // Simular carga
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // Datos de ejemplo
    return [
      {
        cod_insumo: 101,
        cod_municipio: 1001,
        cod_categoria: 1,
        tipo_insumo: "primario",
        municipio: {
          cod_municipio: 1001,
          nom_municipio: "Bogotá",
          cod_depto: 11
        },
        categoria: {
          cod_categoria: 1,
          nom_categoria: "Cartografía Básica"
        }
      },
      {
        cod_insumo: 102,
        cod_municipio: 1001,
        cod_categoria: 1,
        tipo_insumo: "primario",
        municipio: {
          cod_municipio: 1001,
          nom_municipio: "Bogotá",
          cod_depto: 11
        },
        categoria: {
          cod_categoria: 1,
          nom_categoria: "Cartografía Básica"
        }
      },
      {
        cod_insumo: 201,
        cod_municipio: 1002,
        cod_categoria: 2,
        tipo_insumo: "primario",
        municipio: {
          cod_municipio: 1002,
          nom_municipio: "Medellín",
          cod_depto: 5
        },
        categoria: {
          cod_categoria: 2,
          nom_categoria: "Estudio Agrológico"
        }
      },
      {
        cod_insumo: 301,
        cod_municipio: 1003,
        cod_categoria: 3,
        tipo_insumo: "secundario",
        municipio: {
          cod_municipio: 1003,
          nom_municipio: "Cali",
          cod_depto: 76
        },
        categoria: {
          cod_categoria: 3,
          nom_categoria: "Información Catastral"
        }
      },
      {
        cod_insumo: 401,
        cod_municipio: 1004,
        cod_categoria: 4,
        tipo_insumo: "primario",
        municipio: {
          cod_municipio: 1004,
          nom_municipio: "Barranquilla",
          cod_depto: 8
        },
        categoria: {
          cod_categoria: 4,
          nom_categoria: "Deslinde"
        }
      }
    ]
  }
  
  const getArchivosByClasificacion = async (clasificacionId: number): Promise<any[]> => {
    // Simular carga
    await new Promise(resolve => setTimeout(resolve, 300))
    
    // Datos de ejemplo
    const archivos = [
      {
        id_lista_archivo: 1,
        cod_insumo: 1,
        nombre_insumo: "Cartografía Base 2024.zip",
        fecha_disposicion: "2024-03-15",
        observacion: "Archivo actualizado",
        path_file: "/ruta/al/archivo.zip"
      },
      {
        id_lista_archivo: 2,
        cod_insumo: 1,
        nombre_insumo: "Ortofotomapa.tif",
        fecha_disposicion: "2024-03-10",
        observacion: "Ortofotomapa de alta resolución",
        path_file: "/ruta/al/ortofoto.tif"
      },
      {
        id_lista_archivo: 3,
        cod_insumo: 2,
        nombre_insumo: "MDT_5m.tif",
        fecha_disposicion: "2024-02-20",
        observacion: "Modelo digital del terreno",
        path_file: "/ruta/al/mdt.tif"
      }
    ]
    
    // Filtrar por clasificación
    return archivos.filter(a => a.cod_insumo === clasificacionId)
  }
  
  export default defineComponent({
    name: 'ClasificacionesList',
    
    components: {
      ClasificacionForm
    },
    
    setup() {
      const router = useRouter()
      const authStore = useAuthStore()
      
      // Estado general
      const clasificaciones = ref<ClasificacionInsumo[]>([])
      const insumos = ref<Insumo[]>([])
      const cargando = ref(false)
      const error = ref<string | null>(null)
      
      // Estado de filtros y búsqueda
      const searchQuery = ref('')
      const filtros = ref({
        insumo: ''
      })
      
      // Estado de paginación
      const paginaActual = ref(1)
      const elementosPorPagina = ref(9) // 9 tarjetas en una cuadrícula 3x3
      
      // Estado de modales
      const mostrarModal = ref(false)
      const mostrarConfirmacion = ref(false)
      const mostrarDetalles = ref(false)
      const modoEdicion = ref(false)
      const clasificacionEnEdicion = ref<Partial<ClasificacionInsumo> | null>(null)
      const clasificacionAEliminar = ref<ClasificacionInsumo | null>(null)
      const clasificacionDetalle = ref<ClasificacionInsumo | null>(null)
      const archivosAsociados = ref<any[]>([])
      
      // Permisos basados en autenticación
      const puedeCrear = computed(() => authStore.isAuthenticated)
      const puedeEditar = computed(() => authStore.isAuthenticated)
      const puedeEliminar = computed(() => authStore.isAuthenticated)
      
      // Cargar datos iniciales
      onMounted(async () => {
        await Promise.all([
          cargarClasificaciones(),
          cargarInsumos()
        ])
      })
      
      // Cargar clasificaciones
      const cargarClasificaciones = async () => {
        try {
          cargando.value = true
          error.value = null
          const data = await getClasificaciones()
          clasificaciones.value = data
          return true
        } catch (err: any) {
          console.error('Error al cargar clasificaciones:', err)
          error.value = err.message || 'Error al cargar clasificaciones'
          return false
        } finally {
          cargando.value = false
        }
      }
      
      // Cargar insumos
      const cargarInsumos = async () => {
        try {
          const data = await getInsumos()
          insumos.value = data
          return true
        } catch (err: any) {
          console.error('Error al cargar insumos:', err)
          return false
        }
      }
      
      // Filtrar clasificaciones
      const clasificacionesFiltradas = computed(() => {
        let resultado = [...clasificaciones.value]
        
        // Aplicar filtro de búsqueda
        if (searchQuery.value.trim()) {
          const query = searchQuery.value.toLowerCase()
          resultado = resultado.filter(c => 
            c.nombre.toLowerCase().includes(query) || 
            c.observacion?.toLowerCase().includes(query) || 
            c.descripcion?.toLowerCase().includes(query) ||
            c.insumo?.municipio?.nom_municipio.toLowerCase().includes(query)
          )
        }
        
        // Aplicar filtro de insumo
        if (filtros.value.insumo) {
          resultado = resultado.filter(c => 
            c.cod_insumo.toString() === filtros.value.insumo
          )
        }
        
        return resultado
      })
      
      // Obtener elementos para la página actual
      const clasificacionesPaginadas = computed(() => {
        const inicio = (paginaActual.value - 1) * elementosPorPagina.value
        const fin = inicio + elementosPorPagina.value
        return clasificacionesFiltradas.value.slice(inicio, fin)
      })
      
      // Calcular total de páginas
      const totalPaginas = computed(() => {
        return Math.ceil(clasificacionesFiltradas.value.length / elementosPorPagina.value) || 1
      })
      
      // Generar array de páginas para mostrar en paginación
      const paginas = computed(() => {
        const total = totalPaginas.value
        const actual = paginaActual.value
        
        // Si hay menos de 7 páginas, mostrar todas
        if (total <= 7) {
          return Array.from({ length: total }, (_, i) => ({
            numero: i + 1,
            esEllipsis: false
          }))
        }
        
        // Si estamos cerca del inicio
        if (actual <= 3) {
          return [
            { numero: 1, esEllipsis: false },
            { numero: 2, esEllipsis: false },
            { numero: 3, esEllipsis: false },
            { numero: 4, esEllipsis: false },
            { numero: 0, esEllipsis: true },
            { numero: total, esEllipsis: false }
          ]
        }
        
        // Si estamos cerca del final
        if (actual >= total - 2) {
          return [
            { numero: 1, esEllipsis: false },
            { numero: 0, esEllipsis: true },
            { numero: total - 3, esEllipsis: false },
            { numero: total - 2, esEllipsis: false },
            { numero: total - 1, esEllipsis: false },
            { numero: total, esEllipsis: false }
          ]
        }
        
        // Estamos en el medio
        return [
          { numero: 1, esEllipsis: false },
          { numero: 0, esEllipsis: true },
          { numero: actual - 1, esEllipsis: false },
          { numero: actual, esEllipsis: false },
          { numero: actual + 1, esEllipsis: false },
          { numero: 0, esEllipsis: true },
          { numero: total, esEllipsis: false }
        ]
      })
      
      // Manejar cambio de página
      const irAPagina = (pagina: number) => {
        if (pagina < 1 || pagina > totalPaginas.value) return
        paginaActual.value = pagina
      }
      
      // Manejar búsqueda
      const handleSearch = () => {
        paginaActual.value = 1 // Reiniciar a primera página
      }
      
      // Limpiar búsqueda
      const clearSearch = () => {
        searchQuery.value = ''
        paginaActual.value = 1
      }
      
      // Aplicar filtros
      const aplicarFiltros = () => {
        paginaActual.value = 1 // Reiniciar a primera página
      }
      
      // Limpiar filtros
      const limpiarFiltros = () => {
        filtros.value = {
          insumo: ''
        }
        paginaActual.value = 1
      }
      
      // Ver detalles de clasificación
      const verDetalles = async (clasificacion: ClasificacionInsumo) => {
        try {
          cargando.value = true
          clasificacionDetalle.value = clasificacion
          
          // Cargar archivos asociados
          const archivos = await getArchivosByClasificacion(clasificacion.cod_clasificacion)
          archivosAsociados.value = archivos
          
          mostrarDetalles.value = true
        } catch (err) {
          console.error('Error al cargar detalles:', err)
        } finally {
          cargando.value = false
        }
      }
      
      // Cerrar modal de detalles
      const cerrarDetalles = () => {
        mostrarDetalles.value = false
        clasificacionDetalle.value = null
        archivosAsociados.value = []
      }
      
      // Ver detalle completo (navegar a la página de detalle)
      const verDetalleCompleto = (clasificacion: ClasificacionInsumo) => {
        // Aquí se podría navegar a una página de detalle específica
        // router.push(`/clasificaciones/${clasificacion.cod_clasificacion}`)
        
        // Por ahora, simplemente mostrar los detalles en el modal
        verDetalles(clasificacion)
      }
      
      // Mostrar formulario para nueva clasificación
      const mostrarFormulario = (clasificacion?: ClasificacionInsumo) => {
        modoEdicion.value = !!clasificacion
        clasificacionEnEdicion.value = clasificacion ? { ...clasificacion } : { 
          nombre: '',
          cod_insumo: filtros.value.insumo ? parseInt(filtros.value.insumo) : undefined,
          observacion: '',
          ruta: '',
          descripcion: ''
        }
        mostrarModal.value = true
      }
      
      // Editar una clasificación existente
      const editarClasificacion = (clasificacion: ClasificacionInsumo) => {
        mostrarFormulario(clasificacion)
      }
      
      // Cerrar formulario
      const cerrarFormulario = () => {
        mostrarModal.value = false
        clasificacionEnEdicion.value = null
      }
      
      // Confirmar eliminación
      const confirmarEliminacion = (clasificacion: ClasificacionInsumo) => {
        clasificacionAEliminar.value = clasificacion
        mostrarConfirmacion.value = true
      }
      
      // Cancelar eliminación
      const cancelarEliminacion = () => {
        mostrarConfirmacion.value = false
        clasificacionAEliminar.value = null
      }
      
      // Eliminar clasificación
      const eliminarClasificacion = async () => {
        if (!clasificacionAEliminar.value) return
        
        try {
          cargando.value = true
          
          // Aquí iría la llamada real a la API
          await new Promise(resolve => setTimeout(resolve, 500))
          
          // Eliminar de la lista local
          clasificaciones.value = clasificaciones.value.filter(
            c => c.cod_clasificacion !== clasificacionAEliminar.value?.cod_clasificacion
          )
          
          // Cerrar el modal de confirmación
          mostrarConfirmacion.value = false
          clasificacionAEliminar.value = null
          
          // Ajustar página actual si es necesario
          if (clasificacionesPaginadas.value.length === 0 && paginaActual.value > 1) {
            paginaActual.value -= 1
          }
        } catch (err: any) {
          console.error('Error al eliminar clasificación:', err)
          error.value = err.message || 'Error al eliminar la clasificación'
        } finally {
          cargando.value = false
        }
      }
      
      // Guardar clasificación (nueva o editada)
      const guardarClasificacion = async (clasificacion: Partial<ClasificacionInsumo>) => {
        try {
          cargando.value = true
          
          // Aquí iría la llamada real a la API
          await new Promise(resolve => setTimeout(resolve, 700))
          
          if (modoEdicion.value && clasificacionEnEdicion.value) {
            // Actualizar clasificación existente
            const index = clasificaciones.value.findIndex(
              c => c.cod_clasificacion === clasificacionEnEdicion.value?.cod_clasificacion
            )
            
            if (index !== -1) {
              clasificaciones.value[index] = {
                ...clasificaciones.value[index],
                ...clasificacion
              } as ClasificacionInsumo
            }
          } else {
            // Crear nueva clasificación
            const nuevaClasificacion: ClasificacionInsumo = {
              cod_clasificacion: Math.max(0, ...clasificaciones.value.map(c => c.cod_clasificacion)) + 1,
              cod_insumo: clasificacion.cod_insumo!,
              nombre: clasificacion.nombre!,
              observacion: clasificacion.observacion || null,
              ruta: clasificacion.ruta || null,
              descripcion: clasificacion.descripcion || null,
              // Buscar datos del insumo
              insumo: insumos.value.find(i => i.cod_insumo === clasificacion.cod_insumo)
            }
            
            clasificaciones.value.unshift(nuevaClasificacion)
            paginaActual.value = 1 // Ir a la primera página para ver la nueva clasificación
          }
          
          // Cerrar el formulario
          cerrarFormulario()
        } catch (err: any) {
          console.error('Error al guardar clasificación:', err)
          error.value = err.message || 'Error al guardar la clasificación'
        } finally {
          cargando.value = false
        }
      }
      
      // Formatear fecha
      const formatearFecha = (fecha: string | null): string => {
        if (!fecha) return 'N/A'
        try {
          return format(parseISO(fecha), 'dd/MM/yyyy', { locale: es })
        } catch (error) {
          return fecha
        }
      }
      
      // Resetear paginación cuando cambian los filtros o búsqueda
      watch([filtros, searchQuery], () => {
        paginaActual.value = 1
      })
      
      return {
        // Estado general
        clasificaciones,
        insumos,
        cargando,
        error,
        
        // Filtros y búsqueda
        searchQuery,
        filtros,
        handleSearch,
        clearSearch,
        aplicarFiltros,
        limpiarFiltros,
        
        // Paginación
        paginaActual,
        elementosPorPagina,
        clasificacionesFiltradas,
        clasificacionesPaginadas,
        totalPaginas,
        paginas,
        irAPagina,
        
        // Acciones de clasificaciones
        cargarClasificaciones,
        verDetalles,
        verDetalleCompleto,
        editarClasificacion,
        confirmarEliminacion,
        eliminarClasificacion,
        
        // Modales
        mostrarModal,
        mostrarConfirmacion,
        mostrarDetalles,
        modoEdicion,
        clasificacionEnEdicion,
        clasificacionAEliminar,
        clasificacionDetalle,
        archivosAsociados,
        mostrarFormulario,
        cerrarFormulario,
        cancelarEliminacion,
        cerrarDetalles,
        
        // Permisos
        puedeCrear,
        puedeEditar,
        puedeEliminar,

        // Guardar
        guardarClasificacion,

        // Utilidades
        formatearFecha,
        linuxToWindowsPath,
      }
    }
  })

</script>
<style scoped>
.clasificaciones-list {
  width: 100%;
}

/* Encabezado */
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.list-title {
  display: flex;
  align-items: center;
  margin: 0;
  font-size: 1.8rem;
  color: #343a40;
}

.list-title i {
  margin-right: 0.5rem;
  color: #007bff;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.search-box {
  position: relative;
  min-width: 300px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding: 0 0.75rem;
}

.search-box i {
  color: #6c757d;
  margin-right: 0.5rem;
}

.search-box input {
  flex: 1;
  border: none;
  outline: none;
  padding: 0.75rem 0;
  font-size: 1rem;
}

.search-box button {
  background: none;
  border: none;
  cursor: pointer;
  color: #6c757d;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-add {
  display: flex;
  align-items: center;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.6rem 1rem;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-add i {
  margin-right: 0.5rem;
}

.btn-add:hover {
  background-color: #218838;
}

/* Filtros */
.filters-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  flex-wrap: wrap;
  gap: 1rem;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.filter-group label {
  font-weight: 500;
  color: #495057;
  white-space: nowrap;
}

.filter-group select {
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  min-width: 200px;
}

.actions-group {
  display: flex;
  gap: 0.5rem;
}

.btn-filter, 
.btn-clear {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-filter {
  background-color: #007bff;
  color: white;
  border: none;
}

.btn-filter:hover {
  background-color: #0069d9;
}

.btn-clear {
  background-color: #6c757d;
  color: white;
  border: none;
}

.btn-clear:hover {
  background-color: #5a6268;
}

/* Estados de carga, error y vacío */
.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
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

.error-container i,
.empty-container i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-container i {
  color: #dc3545;
}

.empty-container i {
  color: #6c757d;
}

.error-container button,
.empty-container button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

/* Grid de clasificaciones */
.clasificaciones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.clasificacion-card {
  display: flex;
  flex-direction: column;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  height: 100%;
  transition: transform 0.2s, box-shadow 0.2s;
}

.clasificacion-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.card-header {
  padding: 1rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.card-title {
  margin: 0;
  font-size: 1.2rem;
  color: #343a40;
  word-break: break-word;
}

.card-actions {
  display: flex;
  gap: 0.25rem;
  margin-left: 0.5rem;
}

.action-btn {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.action-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.action-btn.delete {
  color: #dc3545;
}

.action-btn.delete:hover {
  background-color: rgba(220, 53, 69, 0.1);
}

.card-body {
  padding: 1rem;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-weight: 600;
  color: #6c757d;
  font-size: 0.85rem;
  margin-bottom: 0.25rem;
}

.info-value {
  color: #212529;
}

.info-value.path {
  word-break: break-all;
  font-family: monospace;
  font-size: 0.9rem;
  background-color: #f8f9fa;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.info-value.description {
  max-height: 60px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  margin: 0;
}

.card-footer {
  padding: 1rem;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: center;
}

.btn-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;
  font-weight: 500;
}

.btn-text:hover {
  background-color: rgba(0, 123, 255, 0.05);
}

/* Paginación */
.pagination-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 2rem;
  margin-bottom: 2rem;
}

.pagination-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 4px;
  border: 1px solid #dee2e6;
  background-color: white;
  cursor: pointer;
  transition: background-color 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #f8f9fa;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 4px;
  border: 1px solid #dee2e6;
  background-color: white;
  cursor: pointer;
}

.page-number:hover:not(.active):not(.ellipsis) {
  background-color: #f8f9fa;
}

.page-number.active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
  cursor: default;
}

.page-number.ellipsis {
  border: none;
  cursor: default;
}

/* Modales */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-container.form-modal {
  width: 95%;
  max-width: 700px;
}

.modal-container.details-modal {
  width: 95%;
  max-width: 800px;
}

.modal-header {
  padding: 1rem 1.5rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  color: #343a40;
}

.close-btn {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
}

.close-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
}

.modal-footer {
  padding: 1rem 1.5rem;
  background-color: #f8f9fa;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.btn-primary,
.btn-secondary,
.btn-danger,
.btn-cancel {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
  border: none;
}

.btn-primary:hover {
  background-color: #0069d9;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
  border: none;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
  border: none;
}

.btn-danger:hover {
  background-color: #c82333;
}

.btn-cancel {
  background-color: transparent;
  color: #6c757d;
  border: 1px solid #6c757d;
}

.btn-cancel:hover {
  background-color: #6c757d;
  color: white;
}

.warning-text {
  color: #dc3545;
  font-weight: 500;
}

/* Estilos del detalle completo */
.detail-section {
  margin-bottom: 1.5rem;
}

.detail-section h4 {
  font-size: 1.1rem;
  color: #343a40;
  margin-top: 0;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e9ecef;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.detail-item {
  margin-bottom: 0.75rem;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-label {
  font-weight: 600;
  color: #6c757d;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
  display: block;
}

.detail-value {
  color: #212529;
}

.detail-value.path {
  word-break: break-all;
  font-family: monospace;
  font-size: 0.9rem;
  background-color: #f8f9fa;
  padding: 0.5rem;
  border-radius: 4px;
}

.detail-value.description {
  white-space: pre-line;
  margin: 0;
}

.files-list {
  list-style: none;
  padding: 0;
  margin: 0;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e9ecef;
}

.file-item:last-child {
  border-bottom: none;
}

.file-item i {
  margin-right: 0.75rem;
  color: #6c757d;
}

.file-name {
  flex: 1;
  word-break: break-all;
}

.file-date {
  color: #6c757d;
  font-size: 0.875rem;
  margin-left: 1rem;
  white-space: nowrap;
}

.empty-message {
  color: #6c757d;
  text-align: center;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
}

/* Media queries */
@media (max-width: 992px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .list-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    flex-direction: column;
  }
  
  .search-box {
    width: 100%;
    min-width: auto;
  }
  
  .btn-add {
    width: 100%;
    justify-content: center;
  }
  
  .filters-row {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-group {
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-group select {
    width: 100%;
  }
  
  .actions-group {
    width: 100%;
    justify-content: space-between;
  }
  
  .btn-filter,
  .btn-clear {
    flex: 1;
    justify-content: center;
  }
  
  .modal-footer {
    flex-direction: column-reverse;
  }
  
  .modal-footer button {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 576px) {
  .clasificaciones-grid {
    grid-template-columns: 1fr;
  }
}
</style>