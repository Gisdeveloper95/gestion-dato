<template>
  <div class="table-manager-container">
    <!-- Header Section -->
    <div class="header-section">
      <h2 class="page-title">{{ tableConfig.title }}</h2>
      <div class="info-section">
        <div class="access-info-header">
          <div class="access-badge" :class="accessLevelClass">
            <i class="material-icons">{{ accessLevelIcon }}</i>
            <span>{{ accessLevelText }}</span>
          </div>
          <div v-if="totalRecords > 0" class="scope-info">
            {{ totalRecords }} registros disponibles
          </div>
        </div>
        <div class="actions-bar">
          <button 
            v-if="permissions.canCreate"
            class="btn btn-success" 
            @click="abrirModalCrear"
          >
            <i class="material-icons">add</i>
            Nuevo {{ tableConfig.singularName }}
          </button>
          <button 
            class="btn btn-export" 
            @click="exportarDatos" 
            :disabled="!datosTabla.length"
          >
            <i class="material-icons">file_download</i>
            Exportar Resultados
          </button>
        </div>
      </div>
    </div>

    <!-- Barra de búsqueda principal -->
    <div class="search-section">
      <div class="search-input-container">
        <i class="material-icons search-icon">search</i>
        <input 
          type="text" 
          v-model="filtros.busqueda" 
          @input="busquedaInmediata"
          :placeholder="`Buscar ${tableConfig.singularName.toLowerCase()}...`"
          class="search-input"
        />
        <button 
          v-if="filtros.busqueda" 
          @click="limpiarBusqueda" 
          class="clear-search-btn"
        >
          <i class="material-icons">clear</i>
        </button>
      </div>
    </div>

    <!-- Filtros dinámicos -->
    <div class="filtros-section" v-if="tableConfig.filters && tableConfig.filters.length > 0">
      <div class="row">
        <div 
          v-for="filter in tableConfig.filters" 
          :key="filter.key"
          class="col-md-6 col-lg-4"
        >
          <div class="form-group">
            <label :for="filter.key">
              {{ filter.label }}:
              <span class="contador-opciones">({{ getFilterOptions(filter.key).length }} opciones)</span>
            </label>
            <select 
              :id="filter.key" 
              v-model="filtros[filter.key]"
              @change="actualizarFiltros"
              class="form-control"
              :class="{ 'has-selection': filtros[filter.key] }"
            >
              <option value="">Todos</option>
              <option 
                v-for="option in getFilterOptions(filter.key)" 
                :key="option.value" 
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
            <button 
              v-if="filtros[filter.key]" 
              @click="limpiarFiltroEspecifico(filter.key)"
              class="btn-limpiar-filtro"
              :title="`Limpiar filtro de ${filter.label.toLowerCase()}`"
            >
              ×
            </button>
          </div>
        </div>
      </div>
      
      <!-- Tags de filtros activos -->
      <div class="filtros-activos" v-if="hayFiltrosActivos">
        <h4>🔍 Filtros activos:</h4>
        <div class="tags-filtros">
          <span 
            v-for="(value, key) in filtrosActivos" 
            :key="key"
            class="tag-filtro"
            :class="getFilterClass(key)"
          >
            {{ getFilterLabel(key) }}: {{ obtenerNombreFiltro(key, value) }}
            <button @click="limpiarFiltroEspecifico(key)">×</button>
          </span>
        </div>
      </div>

      <div class="filtros-buttons">
        <button class="btn btn-primary" @click="aplicarFiltros" :disabled="cargandoFiltros">
          <i class="material-icons">filter_list</i>
          Aplicar Filtros
        </button>
        <button class="btn btn-secondary" @click="limpiarFiltros" :disabled="cargandoFiltros">
          <i class="material-icons">clear_all</i>
          Limpiar Filtros
        </button>
      </div>
    </div>

    <!-- Estados de carga y mensajes -->
    <div v-if="cargando" class="loading-container">
      <div class="spinner"></div>
      <span class="loading-text">Cargando {{ tableConfig.singularName.toLowerCase() }}...</span>
    </div>

    <div v-else-if="error" class="error-container">
      <i class="material-icons">error</i>
      <span>{{ error }}</span>
      <button class="btn btn-primary" @click="cargarDatos">Reintentar</button>
    </div>

    <div v-else-if="datosTabla.length === 0" class="empty-container">
      <i class="material-icons">info</i>
      <span>No se encontraron {{ tableConfig.pluralName.toLowerCase() }} con los filtros seleccionados</span>
    </div>

    <!-- Tabla de datos -->
    <div v-else class="table-section">
      <div class="results-info">
        <span class="results-count">
          Mostrando {{ datosTabla.length }} de {{ totalRecords }} {{ tableConfig.pluralName.toLowerCase() }}
        </span>
        <div class="pagination-info" v-if="paginacion.totalPaginas > 1">
          Página {{ paginacion.paginaActual }} de {{ paginacion.totalPaginas }}
        </div>
      </div>

      <div class="table-responsive">
        <table class="table table-striped table-hover">
          <thead>
            <tr>
              <th 
                v-for="column in tableConfig.columns" 
                :key="column.key"
                :class="{ 'sortable': column.sortable }"
                @click="column.sortable ? ordenarPor(column.key) : null"
              >
                {{ column.label }}
                <i v-if="column.sortable && ordenActual.campo === column.key" 
                   class="material-icons sort-icon">
                  {{ ordenActual.direccion === 'asc' ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th v-if="permissions.canEdit || permissions.canDelete" class="actions-column">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in datosPaginados" :key="getItemId(item)">
              <td v-for="column in tableConfig.columns" :key="column.key">
                <component 
                  v-if="column.component"
                  :is="column.component"
                  :value="getNestedValue(item, column.key)"
                  :item="item"
                />
                <span v-else>{{ formatValue(getNestedValue(item, column.key), column) }}</span>
              </td>
              <td v-if="permissions.canEdit || permissions.canDelete" class="actions-cell">
                <button 
                  v-if="permissions.canEdit"
                  class="btn btn-sm btn-outline-primary"
                  @click="editarItem(item)"
                  title="Editar"
                >
                  <i class="material-icons">edit</i>
                </button>
                <button 
                  v-if="permissions.canDelete"
                  class="btn btn-sm btn-outline-danger"
                  @click="confirmarEliminar(item)"
                  title="Eliminar"
                >
                  <i class="material-icons">delete</i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Paginación -->
      <div class="pagination-container" v-if="paginacion.totalPaginas > 1">
        <nav>
          <ul class="pagination">
            <li class="page-item" :class="{ disabled: paginacion.paginaActual === 1 }">
              <button class="page-link" @click="cambiarPagina(1)">
                <i class="material-icons">first_page</i>
              </button>
            </li>
            <li class="page-item" :class="{ disabled: paginacion.paginaActual === 1 }">
              <button class="page-link" @click="cambiarPagina(paginacion.paginaActual - 1)">
                <i class="material-icons">chevron_left</i>
              </button>
            </li>
            
            <li 
              v-for="pagina in paginasVisibles" 
              :key="pagina"
              class="page-item" 
              :class="{ active: pagina === paginacion.paginaActual }"
            >
              <button class="page-link" @click="cambiarPagina(pagina)">
                {{ pagina }}
              </button>
            </li>
            
            <li class="page-item" :class="{ disabled: paginacion.paginaActual === paginacion.totalPaginas }">
              <button class="page-link" @click="cambiarPagina(paginacion.paginaActual + 1)">
                <i class="material-icons">chevron_right</i>
              </button>
            </li>
            <li class="page-item" :class="{ disabled: paginacion.paginaActual === paginacion.totalPaginas }">
              <button class="page-link" @click="cambiarPagina(paginacion.totalPaginas)">
                <i class="material-icons">last_page</i>
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <!-- Modal para crear/editar -->
    <div v-if="mostrarModal" class="modal-overlay" @click="cerrarModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ modoEdicion ? 'Editar' : 'Nuevo' }} {{ tableConfig.singularName }}</h3>
          <button class="btn-close" @click="cerrarModal">
            <i class="material-icons">close</i>
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="guardarItem">
            <div 
              v-for="column in tableConfig.columns" 
              :key="column.key"
              class="form-group"
              v-if="column.editable !== false"
            >
              <label :for="`form-${column.key}`">{{ column.label }}:</label>
              <input 
                v-if="column.type === 'text' || !column.type"
                :id="`form-${column.key}`"
                v-model="formulario[column.key]"
                type="text"
                class="form-control"
                :required="column.required"
                :placeholder="column.placeholder"
              />
              <input 
                v-else-if="column.type === 'number'"
                :id="`form-${column.key}`"
                v-model.number="formulario[column.key]"
                type="number"
                class="form-control"
                :required="column.required"
                :placeholder="column.placeholder"
              />
              <input 
                v-else-if="column.type === 'date'"
                :id="`form-${column.key}`"
                v-model="formulario[column.key]"
                type="date"
                class="form-control"
                :required="column.required"
              />
              <select 
                v-else-if="column.type === 'select'"
                :id="`form-${column.key}`"
                v-model="formulario[column.key]"
                class="form-control"
                :required="column.required"
              >
                <option value="">Seleccionar...</option>
                <option 
                  v-for="option in column.options" 
                  :key="option.value" 
                  :value="option.value"
                >
                  {{ option.label }}
                </option>
              </select>
              <textarea 
                v-else-if="column.type === 'textarea'"
                :id="`form-${column.key}`"
                v-model="formulario[column.key]"
                class="form-control"
                :required="column.required"
                :placeholder="column.placeholder"
                rows="3"
              ></textarea>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="cerrarModal">
            Cancelar
          </button>
          <button 
            type="button" 
            class="btn btn-primary" 
            @click="guardarItem"
            :disabled="guardando"
          >
            <i v-if="guardando" class="material-icons spin">refresh</i>
            <i v-else class="material-icons">save</i>
            {{ guardando ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de confirmación para eliminar -->
    <div v-if="mostrarModalEliminar" class="modal-overlay" @click="cerrarModalEliminar">
      <div class="modal-content modal-small" @click.stop>
        <div class="modal-header">
          <h3>Confirmar eliminación</h3>
          <button class="btn-close" @click="cerrarModalEliminar">
            <i class="material-icons">close</i>
          </button>
        </div>
        <div class="modal-body">
          <p>¿Estás seguro de que deseas eliminar este {{ tableConfig.singularName.toLowerCase() }}?</p>
          <p class="text-danger">Esta acción no se puede deshacer.</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="cerrarModalEliminar">
            Cancelar
          </button>
          <button 
            type="button" 
            class="btn btn-danger" 
            @click="eliminarItem"
            :disabled="eliminando"
          >
            <i v-if="eliminando" class="material-icons spin">refresh</i>
            <i v-else class="material-icons">delete</i>
            {{ eliminando ? 'Eliminando...' : 'Eliminar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch } from 'vue'
import axios from 'axios'

// =============== INTERFACES (COPIADAS LOCALMENTE PARA EVITAR DEPENDENCIAS) ===============
interface TableColumn {
  key: string
  label: string
  type?: 'text' | 'number' | 'date' | 'select' | 'textarea' | 'boolean'
  sortable?: boolean
  editable?: boolean
  required?: boolean
  component?: any
  options?: { value: any, label: string }[]
  format?: (value: any) => string
  placeholder?: string
}

interface TableFilter {
  key: string
  label: string
  type: 'select' | 'multiselect'
  options?: { value: any, label: string }[]
  endpoint?: string
}

interface TableConfig {
  title: string
  singularName: string
  pluralName: string
  apiEndpoint: string
  idField: string
  columns: TableColumn[]
  filters?: TableFilter[]
  searchFields: string[]
}

interface Permissions {
  canCreate: boolean
  canEdit: boolean
  canDelete: boolean
  canExport: boolean
}

// =============== PROPS ===============
const props = withDefaults(defineProps<{
  tableConfig: TableConfig
  permissions?: Permissions
  municipioFilter?: boolean
}>(), {
  permissions: () => ({
    canCreate: true,
    canEdit: true,
    canDelete: true,
    canExport: true
  })
})

// =============== EMITS ===============
const emit = defineEmits<{
  'item-created': [item: any]
  'item-updated': [item: any]
  'item-deleted': [item: any]
  'error': [error: string, context?: string]
}>()

// =============== ESTADO REACTIVO ===============
const datosOriginales = ref<any[]>([])
const datosTabla = ref<any[]>([])
const cargando = ref(false)
const error = ref('')
const totalRecords = ref(0)
const cargandoFiltros = ref(false)

// Filtros
const filtros = reactive<Record<string, any>>({
  busqueda: ''
})

// Formulario para crear/editar
const formulario = reactive<Record<string, any>>({})
const mostrarModal = ref(false)
const modoEdicion = ref(false)
const itemEditando = ref<any>(null)
const guardando = ref(false)

// Modal de eliminación
const mostrarModalEliminar = ref(false)
const itemEliminar = ref<any>(null)
const eliminando = ref(false)

// Ordenamiento
const ordenActual = reactive({
  campo: '',
  direccion: 'asc' as 'asc' | 'desc'
})

// Paginación
const paginacion = reactive({
  paginaActual: 1,
  itemsPorPagina: 20,
  totalPaginas: 1
})

// Inicializar filtros basados en la configuración
if (props.tableConfig.filters) {
  props.tableConfig.filters.forEach(filter => {
    filtros[filter.key] = ''
  })
}

// =============== COMPUTED ===============
const filtrosActivos = computed(() => {
  const activos: Record<string, any> = {}
  for (const [key, value] of Object.entries(filtros)) {
    if (value && key !== 'busqueda') {
      activos[key] = value
    }
  }
  return activos
})

const hayFiltrosActivos = computed(() => {
  return Object.keys(filtrosActivos.value).length > 0
})

const datosFiltrados = computed(() => {
  let resultado = [...datosOriginales.value]

  // Filtro de búsqueda
  if (filtros.busqueda) {
    const termino = filtros.busqueda.toLowerCase()
    resultado = resultado.filter(item => {
      return props.tableConfig.searchFields.some(field => {
        const value = getNestedValue(item, field)
        return value && value.toString().toLowerCase().includes(termino)
      })
    })
  }

  // Aplicar filtros específicos
  for (const [key, value] of Object.entries(filtrosActivos.value)) {
    if (value) {
      resultado = resultado.filter(item => {
        const itemValue = getNestedValue(item, key)
        return itemValue && itemValue.toString() === value.toString()
      })
    }
  }

  return resultado
})

const datosOrdenados = computed(() => {
  if (!ordenActual.campo) return datosFiltrados.value

  return [...datosFiltrados.value].sort((a, b) => {
    const aValue = getNestedValue(a, ordenActual.campo)
    const bValue = getNestedValue(b, ordenActual.campo)
    
    let comparison = 0
    if (aValue < bValue) comparison = -1
    if (aValue > bValue) comparison = 1
    
    return ordenActual.direccion === 'desc' ? -comparison : comparison
  })
})

const datosPaginados = computed(() => {
  const inicio = (paginacion.paginaActual - 1) * paginacion.itemsPorPagina
  const fin = inicio + paginacion.itemsPorPagina
  return datosOrdenados.value.slice(inicio, fin)
})

const paginasVisibles = computed(() => {
  const paginas = []
  const actual = paginacion.paginaActual
  const total = paginacion.totalPaginas
  
  let inicio = Math.max(1, actual - 2)
  let fin = Math.min(total, inicio + 4)
  
  if (fin - inicio < 4) {
    inicio = Math.max(1, fin - 4)
  }
  
  for (let i = inicio; i <= fin; i++) {
    paginas.push(i)
  }
  
  return paginas
})

const permissions = computed(() => props.permissions)
const accessLevelClass = computed(() => 'access-admin')
const accessLevelIcon = computed(() => 'admin_panel_settings')
const accessLevelText = computed(() => 'Administrador')

// =============== MÉTODOS ===============
const cargarDatos = async () => {
  cargando.value = true
  error.value = ''
  
  try {
    const token = localStorage.getItem('token')
    const config = token ? {
      headers: { 'Authorization': `Token ${token}` }
    } : {}
    
    const response = await axios.get(props.tableConfig.apiEndpoint, config)
    
    if (Array.isArray(response.data)) {
      datosOriginales.value = response.data
      totalRecords.value = response.data.length
    } else if (response.data.results) {
      datosOriginales.value = response.data.results
      totalRecords.value = response.data.count || response.data.results.length
    } else {
      datosOriginales.value = []
      totalRecords.value = 0
    }
    
    datosTabla.value = datosOriginales.value
    actualizarPaginacion()
    
  } catch (err: any) {
    error.value = err.response?.data?.message || 'Error al cargar los datos'
    console.error('Error cargando datos:', err)
  } finally {
    cargando.value = false
  }
}

const busquedaInmediata = () => {
  clearTimeout((busquedaInmediata as any).timeout)
  ;(busquedaInmediata as any).timeout = setTimeout(() => {
    actualizarDatosTabla()
  }, 300)
}

const actualizarDatosTabla = () => {
  datosTabla.value = datosFiltrados.value
  paginacion.paginaActual = 1
  actualizarPaginacion()
}

const actualizarPaginacion = () => {
  paginacion.totalPaginas = Math.ceil(datosOrdenados.value.length / paginacion.itemsPorPagina)
  if (paginacion.paginaActual > paginacion.totalPaginas) {
    paginacion.paginaActual = 1
  }
}

const actualizarFiltros = () => {
  actualizarDatosTabla()
}

const aplicarFiltros = () => {
  cargandoFiltros.value = true
  setTimeout(() => {
    actualizarDatosTabla()
    cargandoFiltros.value = false
  }, 500)
}

const limpiarFiltros = () => {
  for (const key in filtros) {
    if (key !== 'busqueda') {
      filtros[key] = ''
    }
  }
  actualizarDatosTabla()
}

const limpiarBusqueda = () => {
  filtros.busqueda = ''
  actualizarDatosTabla()
}

const limpiarFiltroEspecifico = (filtro: string) => {
  filtros[filtro] = ''
  actualizarDatosTabla()
}

const ordenarPor = (campo: string) => {
  if (ordenActual.campo === campo) {
    ordenActual.direccion = ordenActual.direccion === 'asc' ? 'desc' : 'asc'
  } else {
    ordenActual.campo = campo
    ordenActual.direccion = 'asc'
  }
  actualizarPaginacion()
}

const cambiarPagina = (pagina: number) => {
  if (pagina >= 1 && pagina <= paginacion.totalPaginas) {
    paginacion.paginaActual = pagina
  }
}

// CRUD Operations
const abrirModalCrear = () => {
  modoEdicion.value = false
  itemEditando.value = null
  resetFormulario()
  mostrarModal.value = true
}

const editarItem = (item: any) => {
  modoEdicion.value = true
  itemEditando.value = item
  
  for (const column of props.tableConfig.columns) {
    if (column.editable !== false) {
      formulario[column.key] = getNestedValue(item, column.key)
    }
  }
  
  mostrarModal.value = true
}

const resetFormulario = () => {
  for (const column of props.tableConfig.columns) {
    formulario[column.key] = ''
  }
}

const cerrarModal = () => {
  mostrarModal.value = false
  resetFormulario()
}

const guardarItem = async () => {
  guardando.value = true
  
  try {
    const token = localStorage.getItem('token')
    const config = token ? {
      headers: { 'Authorization': `Token ${token}` }
    } : {}
    
    let item: any
    
    if (modoEdicion.value && itemEditando.value) {
      const id = getItemId(itemEditando.value)
      const response = await axios.put(`${props.tableConfig.apiEndpoint}${id}/`, formulario, config)
      item = response.data
      emit('item-updated', item)
    } else {
      const response = await axios.post(props.tableConfig.apiEndpoint, formulario, config)
      item = response.data
      emit('item-created', item)
    }
    
    await cargarDatos()
    cerrarModal()
    
  } catch (err: any) {
    const errorMessage = err.response?.data?.message || 'Error al guardar'
    emit('error', errorMessage)
  } finally {
    guardando.value = false
  }
}

const confirmarEliminar = (item: any) => {
  itemEliminar.value = item
  mostrarModalEliminar.value = true
}

const cerrarModalEliminar = () => {
  mostrarModalEliminar.value = false
  itemEliminar.value = null
}

const eliminarItem = async () => {
  if (!itemEliminar.value) return
  
  eliminando.value = true
  
  try {
    const token = localStorage.getItem('token')
    const config = token ? {
      headers: { 'Authorization': `Token ${token}` }
    } : {}
    
    const id = getItemId(itemEliminar.value)
    await axios.delete(`${props.tableConfig.apiEndpoint}${id}/`, config)
    
    emit('item-deleted', itemEliminar.value)
    await cargarDatos()
    cerrarModalEliminar()
    
  } catch (err: any) {
    const errorMessage = err.response?.data?.message || 'Error al eliminar'
    emit('error', errorMessage)
  } finally {
    eliminando.value = false
  }
}

const exportarDatos = () => {
  const csvContent = convertToCSV(datosOrdenados.value)
  downloadCSV(csvContent, `${props.tableConfig.singularName}_export.csv`)
}

// =============== MÉTODOS AUXILIARES ===============
const getNestedValue = (obj: any, path: string): any => {
  return path.split('.').reduce((current, key) => current?.[key], obj)
}

const getItemId = (item: any): any => {
  return getNestedValue(item, props.tableConfig.idField)
}

const formatValue = (value: any, column: TableColumn): string => {
  if (value == null) return ''
  
  if (column.format) {
    return column.format(value)
  }
  
  if (column.type === 'date' && value) {
    return new Date(value).toLocaleDateString()
  }
  
  if (column.type === 'boolean') {
    return value ? 'Sí' : 'No'
  }
  
  return value.toString()
}

const getFilterOptions = (filterKey: string): { value: any, label: string }[] => {
  const filter = props.tableConfig.filters?.find(f => f.key === filterKey)
  if (!filter) return []
  
  if (filter.options) {
    return filter.options
  }
  
  const uniqueValues = new Set(
    datosOriginales.value.map(item => getNestedValue(item, filterKey))
  )
  
  return Array.from(uniqueValues)
    .filter(value => value != null)
    .map(value => ({ value, label: value.toString() }))
    .sort((a, b) => a.label.localeCompare(b.label))
}

const getFilterLabel = (filterKey: string): string => {
  const filter = props.tableConfig.filters?.find(f => f.key === filterKey)
  return filter?.label || filterKey
}

const obtenerNombreFiltro = (filterKey: string, value: any): string => {
  const options = getFilterOptions(filterKey)
  const option = options.find(opt => opt.value === value)
  return option?.label || value.toString()
}

const getFilterClass = (filterKey: string): string => {
  const classMap: Record<string, string> = {
    departamento: 'departamento',
    municipio: 'municipio',
    categoria: 'categoria',
    tipo: 'tipo',
    estado: 'estado'
  }
  
  return classMap[filterKey] || 'default'
}

const convertToCSV = (data: any[]): string => {
  if (!data.length) return ''
  
  const headers = props.tableConfig.columns.map(col => col.label).join(',')
  const rows = data.map(item => 
    props.tableConfig.columns.map(col => {
      const value = getNestedValue(item, col.key)
      return `"${formatValue(value, col)}"`
    }).join(',')
  )
  
  return [headers, ...rows].join('\n')
}

const downloadCSV = (csvContent: string, filename: string) => {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

// =============== WATCHERS ===============
watch(datosOrdenados, () => {
  actualizarPaginacion()
})

// =============== LIFECYCLE ===============
onMounted(() => {
  cargarDatos()
})
</script>

<style scoped>
/* Todos los estilos del componente anterior... */
.table-manager-container {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-size: 1.6rem;
  color: #333;
  margin: 0;
}

.info-section {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.access-info-header {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.access-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
}

.access-admin {
  background: linear-gradient(135deg, #f39c12, #d68910);
  color: white;
}

.scope-info {
  font-size: 0.8rem;
  color: #6c757d;
}

.actions-bar {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.search-section {
  margin-bottom: 1.5rem;
}

.search-input-container {
  position: relative;
  display: flex;
  align-items: center;
  max-width: 500px;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: #6c757d;
  z-index: 5;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
  border: 2px solid #e9ecef;
  border-radius: 25px;
  font-size: 1rem;
  transition: all 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.clear-search-btn {
  position: absolute;
  right: 8px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.clear-search-btn:hover {
  background: #c82333;
  transform: scale(1.1);
}

.filtros-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.row {
  display: flex;
  flex-wrap: wrap;
  margin: -0.5rem;
}

.col-md-6, .col-lg-4 {
  flex: 0 0 100%;
  padding: 0.5rem;
}

@media (min-width: 768px) {
  .col-md-6 { flex: 0 0 50%; }
}

@media (min-width: 992px) {
  .col-lg-4 { flex: 0 0 33.333333%; }
}

.form-group {
  position: relative;
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.5rem;
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
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
  transition: all 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-control.has-selection {
  border-color: #007bff;
  background-color: #f0f8ff;
  font-weight: 500;
}

.btn-limpiar-filtro {
  position: absolute;
  right: 8px;
  top: 34px;
  background: #dc3545;
  color: white;
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
  background: #c82333;
  transform: scale(1.1);
}

.filtros-activos {
  margin-top: 1.5rem;
  padding: 1rem;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 8px;
  border-left: 4px solid #28a745;
  animation: slideIn 0.3s ease-out;
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

.tag-filtro:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.tag-filtro.departamento {
  background: linear-gradient(135deg, #f39c12, #d68910);
  color: white;
}

.tag-filtro.municipio {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
}

.tag-filtro.categoria {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
}

.tag-filtro.tipo {
  background: linear-gradient(135deg, #9b59b6, #8e44ad);
  color: white;
}

.tag-filtro.estado {
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
}

.tag-filtro.default {
  background: linear-gradient(135deg, #6c757d, #5a6268);
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
  margin-top: 1.5rem;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.loading-container, .error-container, .empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
  background: white;
  border-radius: 8px;
  margin: 2rem 0;
}

.loading-container {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
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

.loading-text {
  color: #6c757d;
  font-size: 1.1rem;
}

.error-container {
  background: linear-gradient(135deg, #fff5f5, #fed7d7);
  color: #e53e3e;
}

.empty-container {
  background: linear-gradient(135deg, #f7fafc, #edf2f7);
  color: #4a5568;
}

.table-section {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.results-info {
  padding: 1rem 1.5rem;
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.results-count {
  font-weight: 600;
  color: #495057;
}

.pagination-info {
  color: #6c757d;
  font-size: 0.9rem;
}

.table-responsive {
  overflow-x: auto;
}

.table {
  width: 100%;
  margin-bottom: 0;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 0.75rem;
  vertical-align: middle;
  border-bottom: 1px solid #dee2e6;
}

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
  border-bottom: 2px solid #dee2e6;
}

.table th.sortable {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s;
}

.table th.sortable:hover {
  background-color: #e9ecef;
}

.sort-icon {
  font-size: 1rem;
  margin-left: 0.5rem;
  color: #007bff;
}

.table-striped tbody tr:nth-of-type(odd) {
  background-color: rgba(0, 0, 0, 0.02);
}

.table-hover tbody tr:hover {
  background-color: rgba(0, 123, 255, 0.05);
}

.actions-column {
  width: 120px;
  text-align: center;
}

.actions-cell {
  text-align: center;
}

.actions-cell .btn {
  margin: 0 0.25rem;
}

.pagination-container {
  padding: 1.5rem;
  background: #f8f9fa;
  border-top: 1px solid #dee2e6;
  display: flex;
  justify-content: center;
}

.pagination {
  display: flex;
  list-style: none;
  padding: 0;
  margin: 0;
  border-radius: 4px;
}

.page-item {
  margin: 0 0.125rem;
}

.page-link {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 0.75rem;
  margin: 0;
  text-decoration: none;
  color: #007bff;
  background-color: #fff;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  transition: all 0.2s;
  min-width: 40px;
  height: 40px;
}

.page-link:hover {
  color: #0056b3;
  background-color: #e9ecef;
  border-color: #adb5bd;
}

.page-item.active .page-link {
  color: #fff;
  background-color: #007bff;
  border-color: #007bff;
}

.page-item.disabled .page-link {
  color: #6c757d;
  pointer-events: none;
  background-color: #fff;
  border-color: #dee2e6;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  border: 1px solid transparent;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  color: #fff;
  background-color: #007bff;
  border-color: #007bff;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
  border-color: #004085;
}

.btn-success {
  color: #fff;
  background-color: #28a745;
  border-color: #28a745;
}

.btn-success:hover:not(:disabled) {
  background-color: #218838;
  border-color: #1e7e34;
}

.btn-secondary {
  color: #fff;
  background-color: #6c757d;
  border-color: #6c757d;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #5a6268;
  border-color: #545b62;
}

.btn-danger {
  color: #fff;
  background-color: #dc3545;
  border-color: #dc3545;
}

.btn-danger:hover:not(:disabled) {
  background-color: #c82333;
  border-color: #bd2130;
}

.btn-export {
  color: #fff;
  background: linear-gradient(135deg, #17a2b8, #138496);
  border-color: #17a2b8;
}

.btn-export:hover:not(:disabled) {
  background: linear-gradient(135deg, #138496, #117a8b);
  border-color: #138496;
}

.btn-outline-primary {
  color: #007bff;
  background-color: transparent;
  border-color: #007bff;
}

.btn-outline-primary:hover:not(:disabled) {
  color: #fff;
  background-color: #007bff;
  border-color: #007bff;
}

.btn-outline-danger {
  color: #dc3545;
  background-color: transparent;
  border-color: #dc3545;
}

.btn-outline-danger:hover:not(:disabled) {
  color: #fff;
  background-color: #dc3545;
  border-color: #dc3545;
}

.btn-sm {
  padding: 0.375rem 0.5rem;
  font-size: 0.8rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  animation: modalSlideIn 0.3s ease-out;
}

.modal-small {
  max-width: 400px;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.2s;
}

.btn-close:hover {
  background-color: #f8f9fa;
  color: #495057;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #dee2e6;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.spin {
  animation: spin 1s linear infinite;
}

.text-danger {
  color: #dc3545;
}

@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .info-section {
    align-items: stretch;
  }
  
  .access-info-header {
    align-items: center;
  }
  
  .actions-bar {
    justify-content: center;
  }
  
  .table-responsive {
    font-size: 0.85rem;
  }
  
  .modal-content {
    margin: 0.5rem;
    max-width: calc(100% - 1rem);
  }
}
</style>