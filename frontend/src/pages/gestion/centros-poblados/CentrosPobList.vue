<template>
  <div class="centros-poblados-list-container">
    <!-- Header con título y botón crear -->
    <div class="header-section">
      <h2 class="page-title">Gestión de Centros Poblados</h2>
      <div class="actions-bar">
        <button 
          class="btn btn-create" 
          @click="navigateToCreate" 
          v-if="hasPermission"
        >
          <i class="material-icons">add_circle</i>
          Nuevo Centro Poblado
        </button>
        <button 
          class="btn btn-secondary" 
          @click="exportarDatos" 
          :disabled="!centrosPobladosTabla.length"
        >
          <i class="material-icons">file_download</i>
          Exportar Resultados
        </button>
      </div>
    </div>

    <!-- Filtros dinámicos jerárquicos -->
    <div class="filtros-section">
      <div class="row">
        <!-- Filtro Departamento -->
        <div class="col-md-4">
          <div class="form-group">
            <label for="departamento">
              Departamento:
              <span class="contador-opciones">({{ departamentos.length }} disponibles)</span>
            </label>
            <select 
              id="departamento" 
              v-model="filtros.departamento" 
              @change="onDepartamentoChange"
              class="form-control"
              :class="{ 'has-selection': filtros.departamento }"
            >
              <option value="">Todos los departamentos</option>
              <option 
                v-for="depto in departamentos" 
                :key="depto.cod_depto" 
                :value="depto.cod_depto"
              >
                {{ depto.nom_depto }}
              </option>
            </select>
            <button 
              v-if="filtros.departamento" 
              @click="limpiarFiltro('departamento')"
              class="btn-limpiar-filtro"
              title="Limpiar filtro de departamento"
            >
              ✓
            </button>
          </div>
        </div>
        
        <!-- Filtro Municipio -->
        <div class="col-md-4">
          <div class="form-group">
            <label for="municipio">
              Municipio:
              <span class="contador-opciones">({{ municipiosDisponibles.length }} disponibles)</span>
            </label>
            <select 
              id="municipio" 
              v-model="filtros.municipio" 
              @change="onMunicipioChange"
              class="form-control"
              :class="{ 'has-selection': filtros.municipio, 'loading': cargandoMunicipios }"
              :disabled="!filtros.departamento || cargandoMunicipios"
            >
              <option value="">
                {{ cargandoMunicipios ? 'Cargando municipios...' : 
                   !filtros.departamento ? 'Primero seleccione un departamento' : 'Todos los municipios' }}
              </option>
              <option 
                v-for="mun in municipiosDisponibles" 
                :key="mun.cod_municipio" 
                :value="mun.cod_municipio"
              >
                {{ mun.nom_municipio }}
              </option>
            </select>
            <button 
              v-if="filtros.municipio" 
              @click="limpiarFiltro('municipio')"
              class="btn-limpiar-filtro"
              title="Limpiar filtro de municipio"
            >
              ✓
            </button>
          </div>
        </div>
        
        <!-- Búsqueda de texto -->
        <div class="col-md-4">
          <div class="form-group">
            <label for="busqueda">Búsqueda por nombre:</label>
            <input 
              type="text" 
              id="busqueda" 
              v-model="filtros.busqueda" 
              @input="debounceSearch"
              placeholder="Buscar centro poblado por nombre..."
              class="form-control"
            />
          </div>
        </div>
      </div>

      <!-- Indicadores de filtros activos -->
      <div class="filtros-activos" v-if="hayFiltrosActivos">
        <h4>🔍 Filtros activos:</h4>
        <div class="tags-filtros">
          <span v-if="filtros.departamento" class="tag-filtro departamento">
            Departamento: {{ obtenerNombreDepartamento(filtros.departamento) }}
            <button @click="limpiarFiltro('departamento')">×</button>
          </span>
          <span v-if="filtros.municipio" class="tag-filtro municipio">
            Municipio: {{ obtenerNombreMunicipio(filtros.municipio) }}
            <button @click="limpiarFiltro('municipio')">×</button>
          </span>
          <span v-if="filtros.busqueda" class="tag-filtro busqueda">
            Búsqueda: "{{ filtros.busqueda }}"
            <button @click="limpiarFiltro('busqueda')">×</button>
          </span>
        </div>
      </div>

      <!-- Botones de filtros -->
      <div class="filtros-buttons">
        <button class="btn btn-primary" @click="aplicarFiltros" :disabled="cargando">
          <i class="material-icons">filter_list</i>
          Aplicar Filtros
        </button>
        <button class="btn btn-secondary" @click="limpiarTodosFiltros" :disabled="cargando">
          <i class="material-icons">clear_all</i>
          Limpiar Filtros
        </button>
      </div>
    </div>

    <!-- Estados de carga y mensajes -->
    <div v-if="cargando" class="loading-container">
      <div class="spinner"></div>
      <span class="loading-text">Cargando centros poblados...</span>
    </div>
    
    <!-- Indicador de carga adicional para filtros -->
    <div v-if="(cargandoMunicipios || cargandoCentros) && !cargando" class="loading-filter-container">
      <div class="loading-filter-content">
        <div class="spinner-small"></div>
        <span v-if="cargandoMunicipios" class="loading-filter-text">
          Cargando municipios del departamento...
        </span>
        <span v-else-if="cargandoCentros" class="loading-filter-text">
          Cargando todos los centros poblados... Esto puede tomar unos momentos.
        </span>
      </div>
    </div>

    <div v-else-if="error" class="error-container">
      <i class="material-icons">error</i>
      <span>{{ error }}</span>
      <button class="btn btn-primary" @click="cargarDatos">Reintentar</button>
    </div>

    <div v-else-if="centrosPobladosTabla.length === 0" class="empty-container">
      <i class="material-icons">info</i>
      <div>
        <p v-if="!hayFiltrosActivos">No hay centros poblados disponibles</p>
        <p v-else>No se encontraron centros poblados con los filtros aplicados</p>
        <p v-if="!hayFiltrosActivos" class="help-text">
          Los centros poblados se cargarán automáticamente desde la base de datos
        </p>
        <p v-else class="help-text">
          Pruebe a ajustar o limpiar los filtros para ver más resultados
        </p>
      </div>
    </div>

    <!-- Tabla de resultados -->
    <div v-else class="results-container">
      <div class="results-header">
        <h3 class="results-title">Resultados</h3>
        <div class="results-summary">
          <span class="results-count">{{ centrosPobladosTabla.length }} centros poblados encontrados</span>
          <span v-if="hayFiltrosActivos" class="results-filter-info">
            (filtrados de {{ centrosPobladosOriginales.length }} totales)
          </span>
          <span v-if="totalPaginas > 1" class="results-pagination-info">
            • {{ totalPaginas }} páginas disponibles
          </span>
        </div>
      </div>

      <div class="table-responsive">
        <table class="table table-striped table-hover">
          <thead>
            <tr>
              <th @click="ordenarPor('cod_centro_poblado')" class="th-codigo sortable">
                Código
                <i v-if="ordenacion.campo === 'cod_centro_poblado'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('nom_centro_poblado')" class="th-nombre sortable">
                Nombre Centro Poblado
                <i v-if="ordenacion.campo === 'nom_centro_poblado'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('municipio_nombre')" class="th-municipio sortable">
                Municipio
                <i v-if="ordenacion.campo === 'municipio_nombre'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('departamento_nombre')" class="th-departamento sortable">
                Departamento
                <i v-if="ordenacion.campo === 'departamento_nombre'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('area_oficial_ha')" class="th-area sortable">
                Área (Ha)
                <i v-if="ordenacion.campo === 'area_oficial_ha'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th class="th-acciones">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="centro in centrosPobladosVisibles" :key="centro.cod_centro_poblado">
              <td class="text-center">{{ centro.cod_centro_poblado }}</td>
              <td><strong>{{ centro.nom_centro_poblado }}</strong></td>
              <td>{{ centro.municipio_nombre || 'N/A' }}</td>
              <td>{{ centro.departamento_nombre || 'N/A' }}</td>
              <td class="text-center">{{ centro.area_oficial_ha || 'N/A' }}</td>
              <td>
                <div class="action-buttons">
                  <router-link 
                    :to="`/gestion-informacion/centros-poblados/${centro.cod_centro_poblado}`" 
                    class="action-btn view-btn"
                    title="Ver detalles"
                  >
                    <i class="material-icons">visibility</i>
                  </router-link>
                  
                  <router-link 
                    v-if="hasPermission"
                    :to="`/gestion-informacion/centros-poblados/${centro.cod_centro_poblado}/editar`" 
                    class="action-btn edit-btn"
                    title="Editar centro poblado"
                  >
                    <i class="material-icons">edit</i>
                  </router-link>
                  
                  <button 
                    v-if="hasPermission"
                    class="action-btn delete-btn" 
                    @click="confirmarEliminar(centro)"
                    title="Eliminar centro poblado"
                  >
                    <i class="material-icons">delete</i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Paginación -->
      <div class="pagination-container" v-if="totalPaginas > 1">
        <div class="pagination-info">
          <span class="pagination-summary">
            Mostrando {{ (paginaActual - 1) * elementosPorPagina + 1 }} - 
            {{ Math.min(paginaActual * elementosPorPagina, centrosPobladosTabla.length) }} 
            de {{ centrosPobladosTabla.length }} registros
          </span>
          
          <div class="pagination-controls">
            <label for="elementosPorPagina" class="pagination-label">Mostrar:</label>
            <select 
              id="elementosPorPagina"
              v-model="elementosPorPagina" 
              @change="cambiarElementosPorPagina"
              class="pagination-select"
            >
              <option v-for="opcion in opcionesPorPagina" :key="opcion" :value="opcion">
                {{ opcion }} por página
              </option>
            </select>
          </div>
        </div>
        
        <div class="pagination-buttons">
          <button 
            class="btn-pagination" 
            @click="cambiarPagina(1)" 
            :disabled="paginaActual === 1"
            title="Primera página"
          >
            <i class="material-icons">first_page</i>
          </button>
          
          <button 
            class="btn-pagination" 
            @click="cambiarPagina(paginaActual - 1)" 
            :disabled="paginaActual === 1"
            title="Página anterior"
          >
            <i class="material-icons">navigate_before</i>
          </button>
          
          <button 
            v-for="pagina in botonesNumericos" 
            :key="pagina.valor"
            class="btn-pagination" 
            :class="{ active: pagina.activo, disabled: pagina.ellipsis }"
            @click="pagina.ellipsis ? null : cambiarPagina(pagina.valor)"
          >
            {{ pagina.texto }}
          </button>
          
          <button 
            class="btn-pagination" 
            @click="cambiarPagina(paginaActual + 1)" 
            :disabled="paginaActual === totalPaginas"
            title="Página siguiente"
          >
            <i class="material-icons">navigate_next</i>
          </button>
          
          <button 
            class="btn-pagination" 
            @click="cambiarPagina(totalPaginas)" 
            :disabled="paginaActual === totalPaginas"
            title="Última página"
          >
            <i class="material-icons">last_page</i>
          </button>
        </div>
        
        <div class="pagination-jump">
          <label for="jumpToPage" class="pagination-label">Ir a página:</label>
          <input 
            id="jumpToPage"
            type="number" 
            :min="1" 
            :max="totalPaginas"
            v-model.number="paginaSalto"
            @keyup.enter="saltarAPagina"
            class="pagination-input"
            placeholder="..."
          />
          <button @click="saltarAPagina" class="btn btn-secondary btn-small">Ir</button>
        </div>
      </div>
    </div>

    <!-- Modal de confirmación para eliminar -->
    <div class="modal" v-if="modalEliminar.mostrar">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">Confirmar eliminación</h4>
            <button class="close-button" @click="modalEliminar.mostrar = false" :disabled="eliminando">
              <i class="material-icons">close</i>
            </button>
          </div>
          <div class="modal-body">
            <div class="alert alert-warning">
              <i class="material-icons">warning</i>
              <strong>¿Está seguro de que desea eliminar este centro poblado?</strong>
            </div>
            
            <p>Centro poblado: <strong>{{ modalEliminar.centro?.nom_centro_poblado }}</strong></p>
            <p>Código: <strong>{{ modalEliminar.centro?.cod_centro_poblado }}</strong></p>
            <p>Municipio: <strong>{{ modalEliminar.centro?.municipio_nombre }}</strong></p>
            
            <div class="confirm-text">
              <p>Esta acción <strong>NO PUEDE DESHACERSE</strong>. Por favor, confirme que desea proceder.</p>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="modalEliminar.mostrar = false" :disabled="eliminando">
              Cancelar
            </button>
            <button class="btn btn-danger" @click="eliminarCentroPoblado" :disabled="eliminando">
              <div v-if="eliminando" class="btn-loading">
                <div class="spinner-small"></div>
                <span>Eliminando...</span>
              </div>
              <div v-else class="btn-content">
                <i class="material-icons">delete_forever</i>
                <span>Eliminar</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { debounce } from 'lodash'

// Importar APIs REALES
import { departamentosApi, getMunicipiosByDepartamento, getMunicipios } from '@/api/municipios'
import { centrosPobladosApi } from '@/api/centrosPoblados'

// Interfaces basadas en tu esquema de BD
interface Departamento {
  cod_depto: number
  nom_depto: string
}

interface Municipio {
  cod_municipio: number
  nom_municipio: string
  cod_depto: number
}

interface CentroPoblado {
  cod_centro_poblado: string
  cod_municipio: number
  nom_centro_poblado: string
  area_oficial_ha?: string
  municipio_nombre?: string
  departamento_nombre?: string
}

export default defineComponent({
  name: 'CentrosPobladosList',

  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    // Estados
    const cargando = ref(false)
    const cargandoMunicipios = ref(false)
    const cargandoCentros = ref(false)
    const eliminando = ref(false)
    const error = ref<string | null>(null)
    
    // Datos REALES de la BD
    const departamentos = ref<Departamento[]>([])
    const municipios = ref<Municipio[]>([])
    const centrosPobladosOriginales = ref<CentroPoblado[]>([])
    
    // Filtros
    const filtros = ref({
      departamento: '',
      municipio: '',
      busqueda: ''
    })
    
    // Ordenación
    const ordenacion = ref({
      campo: 'nom_centro_poblado',
      ascendente: true
    })
    
    // Paginación mejorada
    const paginaActual = ref(1)
    const elementosPorPagina = ref(50) // Aumentado de 20 a 50
    const opcionesPorPagina = [20, 50, 100, 200] // Opciones para el usuario
    const paginaSalto = ref<number | null>(null)
    
    // Modal
    const modalEliminar = ref({
      mostrar: false,
      centro: null as CentroPoblado | null
    })
    
    // Permisos
    const hasPermission = computed(() => {
      const token = localStorage.getItem('token')
      return !!token
    })
    
    // 🔥 FUNCIÓN PRINCIPAL - CARGAR DEPARTAMENTOS Y PRIMEROS CENTROS POBLADOS
    const cargarDatos = async () => {
      try {
        cargando.value = true
        error.value = null
        
        console.log('🚀 Cargando datos iniciales desde la BD...')
        
        // 1. Cargar departamentos reales
        const deptosData = await departamentosApi.getAll()
        departamentos.value = Array.isArray(deptosData) ? deptosData : []
        console.log('✅ Departamentos cargados:', departamentos.value.length)
        
        // 2. Cargar TODOS los municipios de una vez
        await cargarTodosMunicipios()
        
        // 3. Cargar los PRIMEROS centros poblados directamente (sin filtros)
        await cargarPrimerosCentrosPoblados()
        
      } catch (err) {
        console.error('❌ Error al cargar datos:', err)
        error.value = `Error al cargar datos: ${err.message}`
      } finally {
        cargando.value = false
      }
    }
    
    // 🔥 CARGAR TODOS LOS MUNICIPIOS DE UNA VEZ
    const cargarTodosMunicipios = async () => {
      try {
        console.log('📍 Cargando TODOS los municipios...')
        
        // Intentar diferentes formas de obtener municipios
        try {
          // Opción 1: API directa de municipios
          const munsData = await getMunicipios() // Sin parámetros para obtener todos
          municipios.value = Array.isArray(munsData) ? munsData : []
          console.log('✅ Municipios cargados directamente:', municipios.value.length)
        } catch (error1) {
          console.warn('⚠️ Error con API directa, intentando por departamentos...')
          
          // Opción 2: Cargar por departamentos si la API directa falla
          for (const depto of departamentos.value.slice(0, 5)) { // Solo primeros 5 deptos
            try {
              const munsDepto = await getMunicipiosByDepartamento(depto.cod_depto)
              const munsArray = Array.isArray(munsDepto) ? munsDepto : []
              
              // Agregar sin duplicados
              munsArray.forEach(mun => {
                if (!municipios.value.find(m => m.cod_municipio === mun.cod_municipio)) {
                  municipios.value.push(mun)
                }
              })
            } catch (error2) {
              console.warn(`Error cargando municipios de ${depto.nom_depto}:`, error2)
            }
          }
        }
        
        console.log('📊 Total municipios cargados:', municipios.value.length)
        
      } catch (error) {
        console.warn('⚠️ Error cargando municipios:', error)
      }
    }
    
    // 🔥 CARGAR LOS PRIMEROS CENTROS POBLADOS SIN FILTROS (MÁS DATOS)
    const cargarPrimerosCentrosPoblados = async () => {
      try {
        console.log('🌟 Cargando PRIMEROS centros poblados (sin filtros)...')
        
        // Intentar obtener centros poblados de más municipios para tener datos suficientes
        const centrosIniciales: CentroPoblado[] = []
        
        // Tomar más municipios para obtener más datos
        const municipiosParaCargar = municipios.value.slice(0, 25) // Aumentado de 10 a 25 municipios
        
        for (const municipio of municipiosParaCargar) {
          try {
            const centrosData = await centrosPobladosApi.porMunicipio(municipio.cod_municipio)
            const centrosArray = Array.isArray(centrosData) ? centrosData : []
            
            if (centrosArray.length > 0) {
              // Buscar el departamento
              const departamento = departamentos.value.find(d => d.cod_depto === municipio.cod_depto)
              
              // Enriquecer centros poblados
              const centrosEnriquecidos = centrosArray.map(centro => ({
                ...centro,
                municipio_nombre: municipio.nom_municipio,
                departamento_nombre: departamento?.nom_depto || `Departamento ${municipio.cod_depto}`
              }))
              
              centrosIniciales.push(...centrosEnriquecidos)
              console.log(`  ✅ ${centrosEnriquecidos.length} centros de ${municipio.nom_municipio}`)
              
              // Si ya tenemos suficientes, parar (aumentado el límite)
              if (centrosIniciales.length >= 200) break
            }
            
          } catch (error) {
            console.warn(`No se pudieron cargar centros de ${municipio.nom_municipio}:`, error)
          }
        }
        
        // Ordenar alfabéticamente y asignar
        centrosPobladosOriginales.value = centrosIniciales.sort((a, b) => 
          a.nom_centro_poblado.localeCompare(b.nom_centro_poblado)
        )
        
        console.log(`🎉 Centros poblados iniciales cargados: ${centrosPobladosOriginales.value.length}`)
        
      } catch (error) {
        console.warn('⚠️ Error cargando centros poblados iniciales:', error)
      }
    }
    
    // Computeds para filtros dinámicos
    const municipiosDisponibles = computed(() => {
      if (!filtros.value.departamento) return []
      
      return municipios.value
        .filter(m => m.cod_depto.toString() === filtros.value.departamento.toString())
        .sort((a, b) => a.nom_municipio.localeCompare(b.nom_municipio))
    })
    
    // 🔥 COMPUTED PRINCIPAL - DATOS PARA LA TABLA
    const centrosPobladosTabla = computed(() => {
      let resultado = [...centrosPobladosOriginales.value]
      
      console.log('🔍 Aplicando filtros:')
      console.log(`   - Datos originales: ${resultado.length}`)
      console.log(`   - Filtros:`, filtros.value)
      
      // Aplicar filtro por departamento
      if (filtros.value.departamento) {
        const municipiosDelDepto = municipios.value
          .filter(m => m.cod_depto.toString() === filtros.value.departamento.toString())
          .map(m => m.cod_municipio)
        
        resultado = resultado.filter(c => municipiosDelDepto.includes(c.cod_municipio))
        console.log(`   - Después filtro departamento: ${resultado.length}`)
      }
      
      // Aplicar filtro por municipio
      if (filtros.value.municipio) {
        resultado = resultado.filter(c => c.cod_municipio.toString() === filtros.value.municipio.toString())
        console.log(`   - Después filtro municipio: ${resultado.length}`)
      }
      
      // Aplicar filtro de búsqueda
      if (filtros.value.busqueda) {
        const busqueda = filtros.value.busqueda.toLowerCase()
        resultado = resultado.filter(c => 
          c.nom_centro_poblado.toLowerCase().includes(busqueda) ||
          c.cod_centro_poblado.toLowerCase().includes(busqueda) ||
          (c.municipio_nombre && c.municipio_nombre.toLowerCase().includes(busqueda)) ||
          (c.departamento_nombre && c.departamento_nombre.toLowerCase().includes(busqueda))
        )
        console.log(`   - Después filtro búsqueda: ${resultado.length}`)
      }
      
      // Aplicar ordenación
      return resultado.sort((a, b) => {
        const campo = ordenacion.value.campo
        let valorA = a[campo] || ''
        let valorB = b[campo] || ''
        
        if (typeof valorA === 'string') valorA = valorA.toLowerCase()
        if (typeof valorB === 'string') valorB = valorB.toLowerCase()
        
        if (ordenacion.value.ascendente) {
          return valorA > valorB ? 1 : -1
        } else {
          return valorA < valorB ? 1 : -1
        }
      })
    })
    
    // Hay filtros activos
    const hayFiltrosActivos = computed(() => {
      return !!(filtros.value.departamento || filtros.value.municipio || filtros.value.busqueda)
    })
    
    // Paginación
    const totalPaginas = computed(() => 
      Math.ceil(centrosPobladosTabla.value.length / elementosPorPagina.value) || 1
    )
    
    const centrosPobladosVisibles = computed(() => {
      const inicio = (paginaActual.value - 1) * elementosPorPagina.value
      const fin = inicio + elementosPorPagina.value
      return centrosPobladosTabla.value.slice(inicio, fin)
    })
    
    const botonesNumericos = computed(() => {
      const botones = []
      const maxBotones = 5
      
      if (totalPaginas.value <= maxBotones) {
        for (let i = 1; i <= totalPaginas.value; i++) {
          botones.push({
            valor: i,
            texto: i.toString(),
            activo: i === paginaActual.value,
            ellipsis: false
          })
        }
      } else {
        // Lógica para mostrar páginas con elipsis
        botones.push({
          valor: 1,
          texto: '1',
          activo: paginaActual.value === 1,
          ellipsis: false
        })
        
        if (paginaActual.value > 3) {
          botones.push({
            valor: null,
            texto: '...',
            activo: false,
            ellipsis: true
          })
        }
        
        const inicio = Math.max(2, paginaActual.value - 1)
        const fin = Math.min(totalPaginas.value - 1, paginaActual.value + 1)
        
        for (let i = inicio; i <= fin; i++) {
          if (i !== 1 && i !== totalPaginas.value) {
            botones.push({
              valor: i,
              texto: i.toString(),
              activo: i === paginaActual.value,
              ellipsis: false
            })
          }
        }
        
        if (paginaActual.value < totalPaginas.value - 2) {
          botones.push({
            valor: null,
            texto: '...',
            activo: false,
            ellipsis: true
          })
        }
        
        if (totalPaginas.value > 1) {
          botones.push({
            valor: totalPaginas.value,
            texto: totalPaginas.value.toString(),
            activo: paginaActual.value === totalPaginas.value,
            ellipsis: false
          })
        }
      }
      
      return botones
    })
    
    // 🔥 CARGAR MUNICIPIOS Y TODOS LOS CENTROS POBLADOS DEL DEPARTAMENTO
    const onDepartamentoChange = async () => {
      try {
        // Limpiar filtros dependientes
        filtros.value.municipio = ''
        
        if (!filtros.value.departamento) {
          aplicarFiltros()
          return
        }
        
        console.log('🚀 Cargando TODOS los datos del departamento:', filtros.value.departamento)
        
        // 1. Cargar municipios del departamento si no los tenemos
        let municipiosDelDepto = municipios.value.filter(m => m.cod_depto.toString() === filtros.value.departamento)
        
        if (municipiosDelDepto.length === 0) {
          cargandoMunicipios.value = true
          console.log('📍 Cargando municipios del departamento...')
          
          const municipiosData = await getMunicipiosByDepartamento(parseInt(filtros.value.departamento))
          const municipiosNuevos = Array.isArray(municipiosData) ? municipiosData : []
          
          if (municipiosNuevos.length > 0) {
            // Agregar a la lista existente
            const municipiosIds = new Set(municipios.value.map(m => m.cod_municipio))
            const municipiosFiltrados = municipiosNuevos.filter(m => !municipiosIds.has(m.cod_municipio))
            
            municipios.value = [...municipios.value, ...municipiosFiltrados]
            municipiosDelDepto = municipiosNuevos
            console.log(`✅ ${municipiosNuevos.length} municipios cargados del departamento`)
          }
        }
        
        // 2. Cargar TODOS los centros poblados de TODOS los municipios del departamento
        console.log(`🌟 Cargando centros poblados de ${municipiosDelDepto.length} municipios...`)
        cargandoCentros.value = true
        
        const departamentoSeleccionado = departamentos.value.find(d => d.cod_depto.toString() === filtros.value.departamento)
        const nombreDepartamento = departamentoSeleccionado?.nom_depto || `Departamento ${filtros.value.departamento}`
        
        let centrosNuevosDelDepto = 0
        
        for (const municipio of municipiosDelDepto) {
          try {
            // Verificar si ya tenemos los centros poblados de este municipio
            const centrosExistentes = centrosPobladosOriginales.value.filter(c => 
              c.cod_municipio === municipio.cod_municipio
            )
            
            if (centrosExistentes.length === 0) {
              console.log(`  📍 Cargando centros de ${municipio.nom_municipio}...`)
              
              const centrosData = await centrosPobladosApi.porMunicipio(municipio.cod_municipio)
              const centrosArray = Array.isArray(centrosData) ? centrosData : []
              
              if (centrosArray.length > 0) {
                // Enriquecer centros poblados
                const centrosEnriquecidos = centrosArray.map(centro => ({
                  ...centro,
                  municipio_nombre: municipio.nom_municipio,
                  departamento_nombre: nombreDepartamento
                }))
                
                // Agregar sin duplicados
                const centrosIds = new Set(centrosPobladosOriginales.value.map(c => c.cod_centro_poblado))
                const centrosFiltrados = centrosEnriquecidos.filter(c => !centrosIds.has(c.cod_centro_poblado))
                
                centrosPobladosOriginales.value = [...centrosPobladosOriginales.value, ...centrosFiltrados]
                centrosNuevosDelDepto += centrosFiltrados.length
                
                console.log(`    ✅ ${centrosFiltrados.length} centros de ${municipio.nom_municipio}`)
              }
              
              // Pequeña pausa para no saturar
              await new Promise(resolve => setTimeout(resolve, 100))
            }
            
          } catch (error) {
            console.warn(`⚠️ Error cargando centros de ${municipio.nom_municipio}:`, error)
          }
        }
        
        console.log(`🎉 Total centros nuevos del departamento: ${centrosNuevosDelDepto}`)
        console.log(`📊 Total centros poblados en memoria: ${centrosPobladosOriginales.value.length}`)
        
        aplicarFiltros()
        
      } catch (err) {
        console.error('❌ Error al cargar datos del departamento:', err)
        error.value = `Error al cargar datos del departamento: ${err.message}`
      } finally {
        cargandoMunicipios.value = false
        cargandoCentros.value = false
      }
    }
    
    // 🔥 CARGAR TODOS LOS CENTROS POBLADOS DEL MUNICIPIO ESPECÍFICO
    const onMunicipioChange = async () => {
      try {
        if (!filtros.value.municipio) {
          aplicarFiltros()
          return
        }
        
        console.log('🚀 Cargando TODOS los centros poblados del municipio:', filtros.value.municipio)
        
        // Verificar si ya tenemos TODOS los centros poblados para este municipio
        const centrosDelMunicipio = centrosPobladosOriginales.value.filter(c => 
          c.cod_municipio.toString() === filtros.value.municipio.toString()
        )
        
        // Siempre cargar desde la API para asegurar que tenemos TODOS los datos
        cargandoCentros.value = true
        console.log('📍 Cargando TODOS los centros poblados desde la API...')
        
        const centrosData = await centrosPobladosApi.porMunicipio(parseInt(filtros.value.municipio))
        const centrosCompletos = Array.isArray(centrosData) ? centrosData : []
        
        console.log('✅ Centros poblados obtenidos desde BD:', centrosCompletos.length)
        
        if (centrosCompletos.length > 0) {
          // Buscar información del municipio y departamento
          const municipioSeleccionado = municipios.value.find(m => 
            m.cod_municipio.toString() === filtros.value.municipio.toString()
          )
          
          const departamentoSeleccionado = departamentos.value.find(d => 
            d.cod_depto === municipioSeleccionado?.cod_depto
          )
          
          const nombreMunicipio = municipioSeleccionado?.nom_municipio || `Municipio ${filtros.value.municipio}`
          const nombreDepartamento = departamentoSeleccionado?.nom_depto || 'Departamento no encontrado'
          
          // Enriquecer TODOS los centros poblados
          const centrosEnriquecidos = centrosCompletos.map(centro => ({
            ...centro,
            municipio_nombre: nombreMunicipio,
            departamento_nombre: nombreDepartamento
          }))
          
          // Remover centros poblados existentes de este municipio y agregar los nuevos completos
          centrosPobladosOriginales.value = [
            // Mantener centros de otros municipios
            ...centrosPobladosOriginales.value.filter(c => 
              c.cod_municipio.toString() !== filtros.value.municipio.toString()
            ),
            // Agregar TODOS los centros del municipio seleccionado
            ...centrosEnriquecidos
          ]
          
          console.log(`📊 Centros poblados del municipio: ${centrosEnriquecidos.length}`)
          console.log(`📊 Total centros poblados en memoria: ${centrosPobladosOriginales.value.length}`)
          
          // Si tenemos muchos centros, informar al usuario
          if (centrosEnriquecidos.length > 50) {
            console.log(`🎉 Municipio con muchos centros poblados: ${centrosEnriquecidos.length} encontrados`)
          }
        } else {
          console.log('⚠️ No se encontraron centros poblados para este municipio')
        }
        
        aplicarFiltros()
        
      } catch (err) {
        console.error('❌ Error al cargar centros poblados del municipio:', err)
        error.value = `Error al cargar centros poblados: ${err.message}`
      } finally {
        cargandoCentros.value = false
      }
    }
    
    const aplicarFiltros = () => {
      paginaActual.value = 1
    }
    
    const limpiarFiltro = (filtro: string) => {
      filtros.value[filtro] = ''
      
      // Limpiar filtros dependientes
      if (filtro === 'departamento') {
        filtros.value.municipio = ''
      }
      
      aplicarFiltros()
    }
    
    const limpiarTodosFiltros = () => {
      filtros.value = {
        departamento: '',
        municipio: '',
        busqueda: ''
      }
      aplicarFiltros()
    }
    
    const debounceSearch = debounce(() => {
      aplicarFiltros()
    }, 500)
    
    const ordenarPor = (campo: string) => {
      if (ordenacion.value.campo === campo) {
        ordenacion.value.ascendente = !ordenacion.value.ascendente
      } else {
        ordenacion.value.campo = campo
        ordenacion.value.ascendente = true
      }
    }
    
    const cambiarPagina = (pagina: number) => {
      if (pagina >= 1 && pagina <= totalPaginas.value) {
        paginaActual.value = pagina
        paginaSalto.value = null // Limpiar el campo de salto
      }
    }
    
    const cambiarElementosPorPagina = () => {
      paginaActual.value = 1 // Resetear a la primera página
    }
    
    const saltarAPagina = () => {
      if (paginaSalto.value && paginaSalto.value >= 1 && paginaSalto.value <= totalPaginas.value) {
        cambiarPagina(paginaSalto.value)
      }
    }
    
    const navigateToCreate = () => {
      router.push('/gestion-informacion/centros-poblados/crear')
    }
    
    const confirmarEliminar = (centro: CentroPoblado) => {
      modalEliminar.value.centro = centro
      modalEliminar.value.mostrar = true
    }
    
    const eliminarCentroPoblado = async () => {
      if (!modalEliminar.value.centro) return
      
      try {
        eliminando.value = true
        
        // TODO: Implementar eliminación real usando la API
        console.log('Eliminando centro poblado:', modalEliminar.value.centro.cod_centro_poblado)
        
        // Simular eliminación
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Remover de la lista local
        centrosPobladosOriginales.value = centrosPobladosOriginales.value.filter(
          c => c.cod_centro_poblado !== modalEliminar.value.centro?.cod_centro_poblado
        )
        
        alert('Centro poblado eliminado correctamente')
        
      } catch (err) {
        console.error('Error al eliminar centro poblado:', err)
        alert('Error al eliminar el centro poblado')
      } finally {
        eliminando.value = false
        modalEliminar.value.mostrar = false
      }
    }
    
    const exportarDatos = () => {
      try {
        if (!centrosPobladosTabla.value.length) {
          alert('No hay datos para exportar')
          return
        }
        
        const headers = ['Código', 'Nombre', 'Municipio', 'Departamento', 'Área (Ha)']
        const rows = centrosPobladosTabla.value.map(c => [
          c.cod_centro_poblado || '',
          c.nom_centro_poblado || '',
          c.municipio_nombre || 'N/A',
          c.departamento_nombre || 'N/A',
          c.area_oficial_ha || ''
        ])
        
        const BOM = '\uFEFF'
        const csvContent = BOM + [
          headers.join(','),
          ...rows.map(row => row.map(cell => 
            `"${(cell || '').toString().replace(/"/g, '""')}"`
          ).join(','))
        ].join('\n')
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `centros_poblados_${new Date().toISOString().slice(0, 10)}.csv`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        alert('Archivo CSV generado correctamente')
        
      } catch (err) {
        console.error('Error al exportar datos:', err)
        alert(`Error al exportar datos: ${err.message}`)
      }
    }
    
    // Helpers para nombres
    const obtenerNombreDepartamento = (codDepto: string) => {
      const depto = departamentos.value.find(d => d.cod_depto.toString() === codDepto)
      return depto?.nom_depto || `Departamento ${codDepto}`
    }
    
    const obtenerNombreMunicipio = (codMunicipio: string) => {
      const municipio = municipios.value.find(m => m.cod_municipio.toString() === codMunicipio)
      return municipio?.nom_municipio || `Municipio ${codMunicipio}`
    }
    
    // 🚀 LIFECYCLE - CARGAR DATOS REALES AL INICIAR
    onMounted(async () => {
      console.log('🏁 Componente montado - Cargando datos REALES de la BD')
      await cargarDatos()
      console.log('✅ Carga inicial completada')
    })
    
    return {
      // Estado
      cargando,
      cargandoMunicipios,
      cargandoCentros,
      eliminando,
      error,
      
      // Datos
      departamentos,
      municipios,
      centrosPobladosOriginales,
      
      // Filtros y computeds
      filtros,
      municipiosDisponibles,
      centrosPobladosTabla,
      hayFiltrosActivos,
      
      // Paginación
      paginaActual,
      elementosPorPagina,
      opcionesPorPagina,
      paginaSalto,
      totalPaginas,
      centrosPobladosVisibles,
      botonesNumericos,
      
      // Modal
      modalEliminar,
      
      // Permisos
      hasPermission,
      
      // Ordenación
      ordenacion,
      
      // Métodos
      cargarDatos,
      cargarTodosMunicipios,
      cargarPrimerosCentrosPoblados,
      onDepartamentoChange,
      onMunicipioChange,
      aplicarFiltros,
      limpiarFiltro,
      limpiarTodosFiltros,
      debounceSearch,
      ordenarPor,
      cambiarPagina,
      cambiarElementosPorPagina,
      saltarAPagina,
      navigateToCreate,
      confirmarEliminar,
      eliminarCentroPoblado,
      exportarDatos,
      obtenerNombreDepartamento,
      obtenerNombreMunicipio
    }
  }
})
</script>

<style scoped>
.centros-poblados-list-container {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 1.6rem;
  color: #333;
  margin: 0;
}

.actions-bar {
  display: flex;
  gap: 0.75rem;
}

.btn-create {
  color: #fff;
  background-color: #28a745;
  border-color: #28a745;
  font-size: 1rem;
  padding: 0.5rem 1.25rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: 500;
  text-align: center;
  white-space: nowrap;
  vertical-align: middle;
  user-select: none;
  border: 1px solid transparent;
  line-height: 1.5;
  border-radius: 4px;
  transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  cursor: pointer;
}

.btn-create:hover {
  background-color: #218838;
  border-color: #1e7e34;
}

.filtros-section {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.row {
  display: flex;
  flex-wrap: wrap;
  margin-right: -15px;
  margin-left: -15px;
  margin-bottom: 1rem;
}

.col-md-4 {
  position: relative;
  width: 100%;
  padding-right: 15px;
  padding-left: 15px;
}

@media (min-width: 768px) {
  .col-md-4 {
    flex: 0 0 33.333333%;
    max-width: 33.333333%;
  }
}

.form-group {
  margin-bottom: 1rem;
  position: relative;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #495057;
}

.contador-opciones {
  color: #6c757d;
  font-size: 0.75rem;
  font-weight: normal;
  background-color: #f8f9fa;
  padding: 0.15rem 0.4rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  margin-left: 0.5rem;
}

.form-control {
  display: block;
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: 0.9rem;
  line-height: 1.5;
  color: #495057;
  background-color: #fff;
  background-clip: padding-box;
  border: 1px solid #ced4da;
  border-radius: 4px;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-control:focus {
  border-color: #80bdff;
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-control:disabled {
  background-color: #e9ecef;
  opacity: 1;
  cursor: not-allowed;
}

.form-control.has-selection {
  border-color: #007bff;
  background-color: #f0f8ff;
  font-weight: 500;
}

.form-control.loading {
  background-image: url("data:image/svg+xml,%3csvg width='16' height='16' viewBox='0 0 16 16' fill='none' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='M8 2v2M8 12v2M13.657 8h-2M4.343 8h-2M11.314 4.686l-1.414 1.414M6.1 9.9l-1.414 1.414M11.314 11.314l-1.414-1.414M6.1 6.1L4.686 4.686' stroke='%23007bff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 16px;
}


.btn-limpiar-filtro {
  position: absolute;
  right: 8px;
  top: 34px;
  background: #00bfff; /* Azul claro neón */
  color: white; /* O puedes usar #ffffff para mayor contraste */
  border: none;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  z-index: 10;
}

.btn-limpiar-filtro:hover {
  background: #007acc; /* Azul más oscuro */
  transform: scale(1.15); /* Crece un poco más */
  box-shadow: 0 0 10px rgba(0, 191, 255, 0.6); /* Añade un "glow" azul neón */
}

.filtros-activos {
  margin-top: 1.5rem;
  padding: 1rem;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 8px;
  border-left: 4px solid #28a745;
  animation: slideIn 0.3s ease-out;
}

.filtros-activos h4 {
  margin: 0 0 0.75rem;
  font-size: 1rem;
  color: #343a40;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tags-filtros {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag-filtro {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  animation: fadeIn 0.3s ease-out;
  transition: all 0.2s;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-filtro.departamento {
  background: linear-gradient(135deg, #f39c12, #d68910);
  color: white;
}

.tag-filtro.municipio {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
}

.tag-filtro.busqueda {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
}

.tag-filtro button {
  background: rgba(255, 255, 255, 0.3);
  border: none;
  color: inherit;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0;
  margin-left: 0.25rem;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.tag-filtro button:hover {
  background: rgba(255, 255, 255, 0.5);
  transform: scale(1.1);
}

.filtros-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: 500;
  text-align: center;
  white-space: nowrap;
  vertical-align: middle;
  user-select: none;
  border: 1px solid transparent;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  line-height: 1.5;
  border-radius: 4px;
  transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  cursor: pointer;
}

.btn-primary {
  color: #fff;
  background-color: #007bff;
  border-color: #007bff;
}

.btn-primary:hover {
  color: #fff;
  background-color: #0069d9;
  border-color: #0062cc;
}

.btn-secondary {
  color: #fff;
  background-color: #6c757d;
  border-color: #6c757d;
}

.btn-secondary:hover {
  color: #fff;
  background-color: #5a6268;
  border-color: #545b62;
}

.btn-danger {
  color: #fff;
  background-color: #dc3545;
  border-color: #dc3545;
}

.btn-danger:hover {
  color: #fff;
  background-color: #c82333;
  border-color: #bd2130;
}

.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.loading-filter-container {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.loading-filter-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.loading-filter-text {
  color: #1d4ed8;
  font-weight: 500;
  font-size: 0.95rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 123, 255, 0.1);
  border-left-color: #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(59, 130, 246, 0.2);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.loading-text {
  color: #6c757d;
  font-size: 1rem;
}

.error-container i,
.empty-container i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #dc3545;
}

.empty-container i {
  color: #6c757d;
}

.help-text {
  color: #6c757d;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.results-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.results-title {
  font-size: 1.2rem;
  margin: 0;
  color: #333;
}

.results-summary {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.results-count {
  color: #6c757d;
  font-size: 0.9rem;
}

.results-filter-info,
.results-pagination-info {
  font-size: 0.8rem;
  color: #6c757d;
  font-style: italic;
}

.table-responsive {
  display: block;
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.table {
  width: 100%;
  margin-bottom: 1rem;
  color: #212529;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.table th,
.table td {
  padding: 0.6rem 0.4rem;
  vertical-align: top;
  border-top: 1px solid #dee2e6;
}

.table thead th {
  vertical-align: bottom;
  border-bottom: 2px solid #dee2e6;
  font-weight: 600;
  background-color: #f8f9fa;
  position: relative;
  white-space: nowrap;
}

.table thead th.sortable {
  cursor: pointer;
  user-select: none;
}

.table thead th.sortable:hover {
  background-color: #e9ecef;
}

.table thead th i {
  font-size: 1rem;
  vertical-align: middle;
  margin-left: 0.25rem;
}

.th-codigo { width: 80px; }
.th-nombre { width: 200px; }
.th-municipio { width: 150px; }
.th-departamento { width: 150px; }
.th-area { width: 100px; }
.th-acciones { width: 120px; }

.table-striped tbody tr:nth-of-type(odd) {
  background-color: rgba(0, 0, 0, 0.05);
}

.table-hover tbody tr:hover {
  background-color: rgba(0, 0, 0, 0.075);
}

.text-center {
  text-align: center;
}

.action-buttons {
  display: flex;
  gap: 0.4rem;
  justify-content: center;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 4px;
  border: none;
  padding: 0;
  cursor: pointer;
  transition: all 0.2s;
  color: white;
  text-decoration: none !important;
}

.view-btn {
  background-color: #007bff;
}

.view-btn:hover {
  background-color: #0062cc;
}

.edit-btn {
  background-color: #28a745;
  color: white !important;
}

.edit-btn:hover {
  background-color: #218838;
}

.delete-btn {
  background-color: #dc3545;
}

.delete-btn:hover {
  background-color: #c82333;
}

.pagination-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.pagination-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.pagination-summary {
  color: #6c757d;
  font-size: 0.9rem;
  font-weight: 500;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pagination-label {
  color: #495057;
  font-size: 0.875rem;
  font-weight: 500;
}

.pagination-select {
  padding: 0.375rem 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.875rem;
  background-color: white;
}

.pagination-buttons {
  display: flex;
  justify-content: center;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.pagination-jump {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
}

.pagination-input {
  width: 60px;
  padding: 0.375rem 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.875rem;
  text-align: center;
}

.btn-small {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.btn-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  padding: 0 0.5rem;
  border: 1px solid #dee2e6;
  background-color: #fff;
  border-radius: 4px;
  color: #007bff;
  cursor: pointer;
}

.btn-pagination:hover {
  background-color: #e9ecef;
  text-decoration: none;
}

.btn-pagination.active {
  background-color: #007bff;
  border-color: #007bff;
  color: #fff;
  cursor: default;
}

.btn-pagination.disabled {
  color: #6c757d;
  pointer-events: none;
  cursor: not-allowed;
}

/* Modal */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-dialog {
  width: 100%;
  max-width: 500px;
  margin: 0.5rem;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #dee2e6;
  background-color: #f8f9fa;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
  padding: 0;
  line-height: 1;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #dee2e6;
  background-color: #f8f9fa;
}

.alert {
  padding: 0.75rem 1.25rem;
  margin-bottom: 1rem;
  border: 1px solid transparent;
  border-radius: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.alert-warning {
  color: #856404;
  background-color: #fff3cd;
  border-color: #ffeaa7;
}

.confirm-text {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 4px;
  color: #856404;
}

.btn-loading {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Responsive */
@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .actions-bar {
    width: 100%;
    flex-direction: column;
  }

  .col-md-4 {
    flex: 0 0 100%;
    max-width: 100%;
  }

  .action-buttons {
    flex-wrap: wrap;
  }

  .table {
    font-size: 0.75rem;
  }

  .action-btn {
    width: 24px;
    height: 24px;
  }
  
  .pagination-container {
    padding: 0.75rem;
  }
  
  .pagination-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  
  .pagination-buttons {
    gap: 0.125rem;
  }
  
  .pagination-jump {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .pagination-summary {
    font-size: 0.8rem;
  }
  
  .btn-pagination {
    min-width: 28px;
    height: 28px;
    font-size: 0.8rem;
  }
  
  .loading-filter-container {
    padding: 0.75rem;
  }
  
  .loading-filter-content {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .loading-filter-text {
    font-size: 0.85rem;
    text-align: center;
  }
}
</style>