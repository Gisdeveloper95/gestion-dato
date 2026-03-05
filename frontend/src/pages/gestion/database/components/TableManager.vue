<template>
  <div class="table-manager">
    <!-- Header -->
    <div class="table-header">
      <div class="table-title-section">
        <h2 class="table-title">{{ tableConfig.title }}</h2>
        <p class="table-subtitle">
          Gestión de {{ tableConfig.pluralName.toLowerCase() }}
        </p>
      </div>
      
      <div class="table-actions">
        <button 
          v-if="permissions.canCreate" 
          @click="crearNuevo"
          class="btn btn-primary"
          :disabled="cargando"
        >
          <i class="material-icons">add</i>
          Crear {{ tableConfig.singularName }}
        </button>
        
        <button 
          v-if="permissions.canExport"
          @click="exportarDatos"
          class="btn btn-outline-secondary"
          :disabled="cargando"
        >
          <i class="material-icons">file_download</i>
          Exportar
        </button>
      </div>
    </div>

    <!-- Filtros y búsqueda -->
    <div class="table-controls">
      <div class="search-section">
        <div class="search-input-wrapper">
          <i class="material-icons search-icon">search</i>
          <input
            v-model="busqueda"
            type="text"
            placeholder="Buscar..."
            class="search-input"
            @input="buscarDatos"
            :disabled="cargando"
          >
        </div>
      </div>
      
      <div class="filter-section">
        <button 
          @click="aplicarFiltros"
          class="btn btn-outline-primary"
          :disabled="cargando"
        >
          <i class="material-icons">filter_list</i>
          Filtros ({{ filtrosActivos }})
        </button>
        
        <button 
          @click="limpiarFiltros"
          class="btn btn-outline-secondary"
          v-if="filtrosActivos > 0"
          :disabled="cargando"
        >
          <i class="material-icons">clear</i>
          Limpiar
        </button>
        
        <button 
          @click="cargarDatos"
          class="btn btn-outline-success"
          title="Actualizar datos"
        >
          <i class="material-icons" :class="{ 'rotating': cargando }">refresh</i>
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="cargando" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Cargando {{ tableConfig.pluralName.toLowerCase() }}...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">
        <i class="material-icons">error_outline</i>
      </div>
      <h3>Error al cargar datos</h3>
      <p>{{ error }}</p>
      <button @click="cargarDatos" class="btn btn-primary">
        <i class="material-icons">refresh</i>
        Reintentar
      </button>
    </div>

    <!-- Tabla -->
    <div v-else class="table-container">
      <div class="table-wrapper">
        <table class="data-table">
          <!-- Header -->
          <thead>
            <tr>
              <th 
                v-for="column in tableConfig.columns" 
                :key="column.key"
                :class="{ 'sortable': column.sortable }"
                @click="column.sortable ? ordenarPor(column.key) : null"
                :style="{ minWidth: column.minWidth || 'auto' }"
              >
                <div class="th-content">
                  <span>{{ column.label }}</span>
                  <i 
                    v-if="column.sortable" 
                    class="material-icons sort-icon"
                    :class="getSortIconClass(column.key)"
                  >
                    {{ getSortIcon(column.key) }}
                  </i>
                </div>
              </th>
              <th v-if="permissions.canEdit || permissions.canDelete" class="actions-column">
                Acciones
              </th>
            </tr>
          </thead>
          
          <!-- Body -->
          <tbody>
            <tr v-for="item in datosPaginados" :key="item[tableConfig.idField]" class="table-row">
              <td v-for="column in tableConfig.columns" :key="column.key">
                <div class="cell-content" :class="{ 'cell-path': esColumnaRuta(column.key) && item[column.key] }">
                  <span v-if="column.editable && editingId === item[tableConfig.idField]" class="edit-mode">
                    <input
                      v-model="editingData[column.key]"
                      :type="getInputType(column.type)"
                      :placeholder="column.placeholder"
                      class="edit-input"
                      @keyup.enter="guardarEdicion"
                      @keyup.escape="cancelarEdicion"
                    >
                  </span>
                  <template v-else>
                    <!-- Celda de ruta con botón de copiar -->
                    <template v-if="esColumnaRuta(column.key) && item[column.key] && isPathLike(item[column.key])">
                      <span class="path-value" :title="formatearValor(item[column.key], column)">
                        {{ formatearValor(item[column.key], column) }}
                      </span>
                      <button
                        @click.stop="copiarRutaAlPortapapeles(item[column.key])"
                        class="btn-copy-path"
                        :class="{ 'copied': rutaCopiada === item[column.key] }"
                        :title="rutaCopiada === item[column.key] ? 'Copiado!' : 'Copiar ruta Windows'"
                      >
                        <i class="material-icons">{{ rutaCopiada === item[column.key] ? 'check' : 'content_copy' }}</i>
                      </button>
                    </template>
                    <!-- Celda normal -->
                    <span v-else>
                      {{ formatearValor(item[column.key], column) }}
                    </span>
                  </template>
                </div>
              </td>
              
              <!-- Acciones -->
              <td v-if="permissions.canEdit || permissions.canDelete" class="actions-cell">
                <div class="action-buttons">
                  <!-- Modo edición -->
                  <template v-if="editingId === item[tableConfig.idField]">
                    <button 
                      @click="guardarEdicion"
                      class="btn-icon btn-save"
                      title="Guardar"
                      :disabled="guardando"
                    >
                      <i class="material-icons">{{ guardando ? 'hourglass_empty' : 'save' }}</i>
                    </button>
                    
                    <button 
                      @click="cancelarEdicion"
                      class="btn-icon btn-cancel"
                      title="Cancelar"
                      :disabled="guardando"
                    >
                      <i class="material-icons">close</i>
                    </button>
                  </template>
                  
                  <!-- Modo normal -->
                  <template v-else>
                    <button 
                      v-if="permissions.canEdit"
                      @click="editarItem(item)"
                      class="btn-icon btn-edit"
                      title="Editar"
                      :disabled="editingId !== null"
                    >
                      <i class="material-icons">edit</i>
                    </button>
                    
                    <button 
                      v-if="permissions.canDelete"
                      @click="eliminarItem(item)"
                      class="btn-icon btn-delete"
                      title="Eliminar"
                      :disabled="editingId !== null || eliminando === item[tableConfig.idField]"
                    >
                      <i class="material-icons">
                        {{ eliminando === item[tableConfig.idField] ? 'hourglass_empty' : 'delete' }}
                      </i>
                    </button>
                  </template>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Sin datos -->
      <div v-if="datosFiltrados.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="material-icons">inbox</i>
        </div>
        <h3>No hay {{ tableConfig.pluralName.toLowerCase() }}</h3>
        <p>{{ busqueda ? 'No se encontraron resultados para tu búsqueda' : 'Aún no hay datos registrados' }}</p>
        <button 
          v-if="permissions.canCreate && !busqueda"
          @click="crearNuevo"
          class="btn btn-primary"
        >
          <i class="material-icons">add</i>
          Crear {{ tableConfig.singularName }}
        </button>
      </div>

      <!-- Paginación -->
      <div v-if="datosFiltrados.length > 0" class="pagination-container">
        <div class="pagination-info">
          Mostrando {{ (paginaActual - 1) * elementosPorPagina + 1 }} - 
          {{ Math.min(paginaActual * elementosPorPagina, datosFiltrados.length) }} 
          de {{ datosFiltrados.length }} {{ tableConfig.pluralName.toLowerCase() }}
        </div>
        
        <div class="pagination-controls">
          <button 
            @click="paginaActual--"
            :disabled="paginaActual <= 1"
            class="btn btn-outline-secondary btn-sm"
          >
            <i class="material-icons">chevron_left</i>
          </button>
          
          <span class="pagination-current">
            {{ paginaActual }} de {{ totalPaginas }}
          </span>
          
          <button 
            @click="paginaActual++"
            :disabled="paginaActual >= totalPaginas"
            class="btn btn-outline-secondary btn-sm"
          >
            <i class="material-icons">chevron_right</i>
          </button>
        </div>
      </div>
    </div>

    <!-- Modal para crear/editar -->
    <div v-if="mostrarModal" class="modal-overlay" @click="cerrarModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ modoModal === 'crear' ? 'Crear' : 'Editar' }} {{ tableConfig.singularName }}</h3>
          <button @click="cerrarModal" class="btn-close-modal">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="procesarFormulario">
            <div 
              v-for="column in tableConfig.columns.filter(c => c.editable !== false)"
              :key="column.key" 
              class="form-group"
            >
              <label :for="column.key" class="form-label">
                {{ column.label }}
                <span v-if="column.required" class="required">*</span>
              </label>
              
              <input
                :id="column.key"
                v-model="formularioData[column.key]"
                :type="getInputType(column.type)"
                :placeholder="column.placeholder"
                :required="column.required"
                class="form-input"
                :disabled="column.key === tableConfig.idField && modoModal === 'editar'"
              >
            </div>
            
            <div class="form-actions">
              <button type="button" @click="cerrarModal" class="btn btn-outline-secondary">
                Cancelar
              </button>
              <button type="submit" class="btn btn-primary" :disabled="procesandoFormulario">
                <i class="material-icons">{{ procesandoFormulario ? 'hourglass_empty' : 'save' }}</i>
                {{ modoModal === 'crear' ? 'Crear' : 'Actualizar' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Modal para eliminación en cascada -->
    <div v-if="mostrarModalEliminacion" class="modal-overlay" @click="cerrarModalEliminacion">
      <div class="modal-content modal-warning" @click.stop>
        <div class="modal-header modal-header-warning">
          <div class="warning-icon">
            <i class="material-icons">warning</i>
          </div>
          <div>
            <h3>¡Registro con datos relacionados!</h3>
            <p>No se puede eliminar directamente</p>
          </div>
          <button @click="cerrarModalEliminacion" class="btn-close-modal">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="warning-message">
            <h4>{{ itemAEliminar ? (itemAEliminar[props.tableConfig.searchFields?.[0]] || itemAEliminar[props.tableConfig.idField]) : '' }}</h4>
            <p>Este {{ props.tableConfig.singularName.toLowerCase() }} está siendo utilizado por otros registros en el sistema.</p>
          </div>
          
          <div class="related-data-section">
            <h5>📊 Datos relacionados encontrados:</h5>
            
            <div v-if="cargandoRelacionados" class="loading-related">
              <div class="loading-spinner-small"></div>
              <span>Buscando registros relacionados...</span>
            </div>
            
            <div v-else class="related-tables">
              <div 
                v-for="relacion in datosRelacionados" 
                :key="relacion.tabla"
                class="related-item"
              >
                <div class="related-icon">
                  <i class="material-icons">storage</i>
                </div>
                <div class="related-info">
                  <span class="related-table">{{ relacion.tabla }}</span>
                  <span class="related-count">{{ relacion.cantidad }} registros</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="options-section">
            <h5>🔧 Opciones disponibles:</h5>
            <div class="option-list">
              <div class="option-item">
                <div class="option-icon safe">
                  <i class="material-icons">edit</i>
                </div>
                <div class="option-content">
                  <strong>Modificar registro</strong>
                  <p>Edita la información sin eliminar</p>
                </div>
              </div>
              
              <div class="option-item">
                <div class="option-icon warning">
                  <i class="material-icons">admin_panel_settings</i>
                </div>
                <div class="option-content">
                  <strong>Contactar administrador</strong>
                  <p>Para eliminación en cascada controlada</p>
                </div>
              </div>
              
              <div class="option-item">
                <div class="option-icon info">
                  <i class="material-icons">search</i>
                </div>
                <div class="option-content">
                  <strong>Revisar dependencias</strong>
                  <p>Ver qué registros usan este dato</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="modal-actions">
            <button @click="cerrarModalEliminacion" class="btn btn-outline-secondary">
              <i class="material-icons">close</i>
              Cancelar
            </button>
            
            <button @click="editarItemDesdeModal" class="btn btn-primary">
              <i class="material-icons">edit</i>
              Editar en su lugar
            </button>
            
            <button 
              @click="confirmarEliminacionCascada" 
              class="btn btn-danger"
              :disabled="true"
              title="Función disponible solo para administradores"
            >
              <i class="material-icons">delete_forever</i>
              Eliminar en cascada
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Notificación -->
    <Transition name="notification">
      <div v-if="notificacion.show" :class="notificacionClass" class="notification-toast">
        <i class="material-icons">{{ notificacion.icon }}</i>
        <div class="notification-content">
          <div class="notification-title">{{ notificacion.title }}</div>
          <div class="notification-message">{{ notificacion.message }}</div>
        </div>
        <button @click="cerrarNotificacion" class="btn-close">
          <i class="material-icons">close</i>
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { getDominioService } from '@/api/dominios'
import { getDominiosCascadaService, esErrorIntegridad, extraerMensajeIntegridad } from '@/api/dominios-cascada'
import type { TableConfig, TablePermissions } from '@/models/table-simple'
import { linuxToWindowsPath, isPathLike, copyPathToClipboard, PATH_FIELDS } from '@/utils/pathUtils'

// Estado para copiar rutas
const rutaCopiada = ref<string | null>(null)

// =============== PROPS ===============
interface Props {
  tableConfig: TableConfig
  permissions: TablePermissions
}

const props = withDefaults(defineProps<Props>(), {
  permissions: () => ({
    canCreate: true,
    canEdit: true,
    canDelete: true,
    canExport: true
  })
})

// =============== ESTADO REACTIVO ===============
const datos = ref<any[]>([])
const cargando = ref(false)
const error = ref<string | null>(null)
const busqueda = ref('')
const ordenActual = ref({ campo: '', direccion: 'asc' as 'asc' | 'desc' })
const paginaActual = ref(1)
const elementosPorPagina = ref(props.tableConfig.itemsPerPage || 20)

// Estados de edición
const editingId = ref<number | string | null>(null)
const editingData = ref<any>({})
const guardando = ref(false)
const eliminando = ref<number | string | null>(null)

// Modal
const mostrarModal = ref(false)
const modoModal = ref<'crear' | 'editar'>('crear')
const formularioData = ref<any>({})
const procesandoFormulario = ref(false)

// Modal de eliminación en cascada
const mostrarModalEliminacion = ref(false)
const itemAEliminar = ref<any>(null)
const datosRelacionados = ref<any[]>([])
const cargandoRelacionados = ref(false)

// Sistema de notificaciones
const notificacion = ref({
  show: false,
  type: 'success' as 'success' | 'error' | 'warning' | 'info',
  title: '',
  message: '',
  icon: 'check_circle'
})

// =============== SERVICIO API ===============
const obtenerServicioAPI = () => {
  // Extraer el dominio del endpoint para usar el servicio correcto
  const endpoint = props.tableConfig.apiEndpoint
  
  // Mapeo de endpoints a claves de dominio
  const endpointToDomainMap: Record<string, string> = {
    '/preoperacion/categorias/': 'categorias',
    '/preoperacion/tipos-insumo/': 'tipos_insumos',
    '/preoperacion/entidades/': 'entidades',
    '/preoperacion/estados-insumo/': 'estados_insumo',
    '/preoperacion/grupos/': 'grupos',
    '/preoperacion/mecanismos-detalle/': 'mecanismo_detalle',
    '/preoperacion/mecanismos-general/': 'mecanismo_general',
    '/preoperacion/mecanismos-operacion/': 'mecanismo_operacion',
    '/preoperacion/roles-seguimiento/': 'roles_seguimiento',
    '/preoperacion/territoriales/': 'territoriales_igac',
    '/preoperacion/tipos-formato/': 'tipos_formato',
    '/preoperacion/zonas/': 'zonas',
    '/preoperacion/alcances-operacion/': 'alcance_operacion',
    '/postoperacion/componentes/': 'componentes_post'
  }
  
  const dominioKey = endpointToDomainMap[endpoint]
  
  if (!dominioKey) {
    console.error('No se encontró servicio para endpoint:', endpoint)
    return null
  }
  
  return getDominioService(dominioKey as any)
}

// =============== COMPUTED ===============
const datosFiltrados = computed(() => {
  let resultado = [...datos.value]
  
  // Aplicar búsqueda
  if (busqueda.value.trim()) {
    const termino = busqueda.value.toLowerCase().trim()
    resultado = resultado.filter(item => {
      return props.tableConfig.searchFields?.some(field => {
        const valor = item[field]
        return valor?.toString().toLowerCase().includes(termino)
      }) || false
    })
  }
  
  // Aplicar ordenamiento
  if (ordenActual.value.campo) {
    resultado.sort((a, b) => {
      const valorA = a[ordenActual.value.campo]
      const valorB = b[ordenActual.value.campo]
      
      if (valorA === valorB) return 0
      
      const resultado = valorA < valorB ? -1 : 1
      return ordenActual.value.direccion === 'asc' ? resultado : -resultado
    })
  }
  
  return resultado
})

const datosPaginados = computed(() => {
  const inicio = (paginaActual.value - 1) * elementosPorPagina.value
  const fin = inicio + elementosPorPagina.value
  return datosFiltrados.value.slice(inicio, fin)
})

const totalPaginas = computed(() => {
  return Math.ceil(datosFiltrados.value.length / elementosPorPagina.value)
})

const filtrosActivos = computed(() => {
  return busqueda.value ? 1 : 0
})

const notificacionClass = computed(() => {
  return `notification-toast notification-toast--${notificacion.value.type}`
})

// =============== MÉTODOS PRINCIPALES ===============
const cargarDatos = async () => {
  try {
    cargando.value = true
    error.value = null
    
    const service = obtenerServicioAPI()
    if (!service) {
      throw new Error('Servicio API no disponible')
    }
    
    const response = await service.getAll()
    datos.value = response || []
    
    mostrarNotificacion('success', 'Datos cargados', `Se cargaron ${datos.value.length} registros correctamente`)
    
  } catch (err: any) {
    console.error('Error cargando datos:', err)
    error.value = err.message || 'Error al cargar los datos'
    mostrarNotificacion('error', 'Error', 'No se pudieron cargar los datos')
  } finally {
    cargando.value = false
  }
}

const buscarDatos = () => {
  paginaActual.value = 1 // Resetear paginación al buscar
}

const ordenarPor = (campo: string) => {
  if (ordenActual.value.campo === campo) {
    ordenActual.value.direccion = ordenActual.value.direccion === 'asc' ? 'desc' : 'asc'
  } else {
    ordenActual.value.campo = campo
    ordenActual.value.direccion = 'asc'
  }
}

const getSortIcon = (campo: string) => {
  if (ordenActual.value.campo !== campo) return 'unfold_more'
  return ordenActual.value.direccion === 'asc' ? 'keyboard_arrow_up' : 'keyboard_arrow_down'
}

const getSortIconClass = (campo: string) => {
  return {
    'active': ordenActual.value.campo === campo,
    'asc': ordenActual.value.campo === campo && ordenActual.value.direccion === 'asc',
    'desc': ordenActual.value.campo === campo && ordenActual.value.direccion === 'desc'
  }
}

const formatearValor = (valor: any, column: any) => {
  if (valor === null || valor === undefined) return '-'

  if (column.format && typeof column.format === 'function') {
    return column.format(valor)
  }

  // Detectar si es una columna de ruta y convertir a Windows
  if (esColumnaRuta(column.key) && typeof valor === 'string' && isPathLike(valor)) {
    return linuxToWindowsPath(valor) || valor
  }

  switch (column.type) {
    case 'date':
      return new Date(valor).toLocaleDateString('es-CO')
    case 'boolean':
      return valor ? 'Sí' : 'No'
    case 'number':
      return valor.toLocaleString('es-CO')
    default:
      return valor.toString()
  }
}

/**
 * Detecta si una columna contiene rutas de archivos basándose en su nombre
 */
const esColumnaRuta = (columnKey: string): boolean => {
  if (!columnKey) return false
  const keyLower = columnKey.toLowerCase()
  return PATH_FIELDS.some(field => keyLower.includes(field.toLowerCase()))
}

/**
 * Copia una ruta al portapapeles y muestra feedback
 */
const copiarRutaAlPortapapeles = async (ruta: string) => {
  try {
    const rutaWindows = linuxToWindowsPath(ruta) || ruta
    await copyPathToClipboard(rutaWindows)
    rutaCopiada.value = ruta
    mostrarNotificacion('success', 'Ruta copiada', 'La ruta Windows se copió al portapapeles')

    setTimeout(() => {
      rutaCopiada.value = null
    }, 3000)
  } catch (error) {
    console.error('Error copiando ruta:', error)
    mostrarNotificacion('error', 'Error', 'No se pudo copiar la ruta')
  }
}

const getInputType = (columnType: string) => {
  switch (columnType) {
    case 'number': return 'number'
    case 'date': return 'date'
    case 'email': return 'email'
    default: return 'text'
  }
}

// =============== ACCIONES CRUD ===============
const crearNuevo = () => {
  modoModal.value = 'crear'
  formularioData.value = {}
  
  // Inicializar valores por defecto
  props.tableConfig.columns.forEach(column => {
    if (column.type === 'number') {
      formularioData.value[column.key] = 0
    } else {
      formularioData.value[column.key] = ''
    }
  })
  
  mostrarModal.value = true
}

const editarItem = (item: any) => {
  editingId.value = item[props.tableConfig.idField]
  editingData.value = { ...item }
}

const cancelarEdicion = () => {
  editingId.value = null
  editingData.value = {}
}

const guardarEdicion = async () => {
  try {
    guardando.value = true
    
    const service = obtenerServicioAPI()
    if (!service) {
      throw new Error('Servicio API no disponible')
    }
    
    const id = editingId.value!
    await service.update(id, editingData.value)
    
    // Actualizar datos locales
    const index = datos.value.findIndex(d => d[props.tableConfig.idField] === id)
    if (index !== -1) {
      datos.value[index] = { ...editingData.value }
    }
    
    editingId.value = null
    editingData.value = {}
    
    mostrarNotificacion('success', 'Actualizado', `${props.tableConfig.singularName} actualizado correctamente`)
    
  } catch (error: any) {
    console.error('Error actualizando:', error)
    mostrarNotificacion('error', 'Error', 'No se pudo actualizar el registro')
  } finally {
    guardando.value = false
  }
}

const eliminarItem = async (item: any) => {
  const itemName = item[props.tableConfig.searchFields?.[0] || props.tableConfig.idField] || 'registro'
  
  if (!confirm(`¿Estás seguro de eliminar "${itemName}"?`)) {
    return
  }
  
  try {
    eliminando.value = item[props.tableConfig.idField]
    
    // Usar servicio con verificación de cascada
    const cascadaService = getDominiosCascadaService(props.tableConfig.apiEndpoint)
    const resultado = await cascadaService.eliminarConVerificacion(item[props.tableConfig.idField])
    
    if (resultado.success) {
      // Remover de datos locales
      const index = datos.value.findIndex(d => d[props.tableConfig.idField] === item[props.tableConfig.idField])
      if (index !== -1) {
        datos.value.splice(index, 1)
      }
      
      mostrarNotificacion('success', 'Eliminado', resultado.message)
    } else {
      // Mostrar modal de eliminación en cascada
      mostrarConfirmacionEliminacionCascada(item, itemName)
    }
    
  } catch (error: any) {
    console.error('Error eliminando:', error)
    
    // Detectar error de Foreign Key Constraint con el nuevo servicio
    if (esErrorIntegridad(error)) {
      const mensajeError = extraerMensajeIntegridad(error)
      mostrarNotificacion('warning', 'No se puede eliminar', mensajeError)
      mostrarConfirmacionEliminacionCascada(item, itemName)
    } else {
      mostrarNotificacion('error', 'Error', 'No se pudo eliminar el registro')
    }
  } finally {
    eliminando.value = null
  }
}

// =============== MODAL Y FORMULARIO ===============
const procesarFormulario = async () => {
  try {
    procesandoFormulario.value = true
    
    const service = obtenerServicioAPI()
    if (!service) {
      throw new Error('Servicio API no disponible')
    }
    
    if (modoModal.value === 'crear') {
      const nuevoItem = await service.create(formularioData.value)
      datos.value.push(nuevoItem)
      mostrarNotificacion('success', 'Creado', `${props.tableConfig.singularName} creado correctamente`)
    } else {
      const id = formularioData.value[props.tableConfig.idField]
      const itemActualizado = await service.update(id, formularioData.value)
      
      const index = datos.value.findIndex(d => d[props.tableConfig.idField] === id)
      if (index !== -1) {
        datos.value[index] = itemActualizado
      }
      
      mostrarNotificacion('success', 'Actualizado', `${props.tableConfig.singularName} actualizado correctamente`)
    }
    
    cerrarModal()
    
  } catch (error: any) {
    console.error('Error procesando formulario:', error)
    mostrarNotificacion('error', 'Error', 'No se pudo procesar la solicitud')
  } finally {
    procesandoFormulario.value = false
  }
}

const cerrarModal = () => {
  mostrarModal.value = false
  formularioData.value = {}
  procesandoFormulario.value = false
}

// =============== ELIMINACIÓN EN CASCADA ===============
const mostrarConfirmacionEliminacionCascada = async (item: any, itemName: string) => {
  itemAEliminar.value = item
  mostrarModalEliminacion.value = true
  
  // Buscar registros relacionados
  await buscarRegistrosRelacionados(item)
}

const buscarRegistrosRelacionados = async (item: any) => {
  try {
    cargandoRelacionados.value = true
    datosRelacionados.value = []
    
    const cascadaService = getDominiosCascadaService(props.tableConfig.apiEndpoint)
    const dependencias = await cascadaService.obtenerDetallesDependencias(item[props.tableConfig.idField])
    
    datosRelacionados.value = dependencias.map(dep => ({
      tabla: dep.tabla.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
      cantidad: dep.cantidad
    }))
    
  } catch (error) {
    console.error('Error buscando registros relacionados:', error)
    datosRelacionados.value = [
      { tabla: 'Registros relacionados', cantidad: '?' }
    ]
  } finally {
    cargandoRelacionados.value = false
  }
}

const confirmarEliminacionCascada = async () => {
  try {
    eliminando.value = itemAEliminar.value[props.tableConfig.idField]
    
    const cascadaService = getDominiosCascadaService(props.tableConfig.apiEndpoint)
    const resultado = await cascadaService.eliminarEnCascada(
      itemAEliminar.value[props.tableConfig.idField], 
      true
    )
    
    if (resultado.success) {
      // Remover de datos locales
      const index = datos.value.findIndex(d => d[props.tableConfig.idField] === itemAEliminar.value[props.tableConfig.idField])
      if (index !== -1) {
        datos.value.splice(index, 1)
      }
      
      mostrarNotificacion('success', 'Eliminado en cascada', 
        `${props.tableConfig.singularName} y ${resultado.eliminados.length} registros relacionados eliminados`)
      
      cerrarModalEliminacion()
    } else {
      const errores = resultado.errores?.join('. ') || 'Error desconocido'
      mostrarNotificacion('error', 'Error en eliminación cascada', errores)
    }
    
  } catch (error: any) {
    console.error('Error en eliminación cascada:', error)
    mostrarNotificacion('error', 'Error', 'No se pudo realizar la eliminación en cascada')
  } finally {
    eliminando.value = null
  }
}

const cerrarModalEliminacion = () => {
  mostrarModalEliminacion.value = false
  itemAEliminar.value = null
  datosRelacionados.value = []
  cargandoRelacionados.value = false
}
const exportarDatos = () => {
  try {
    const csvContent = generateCSV(datos.value)
    downloadCSV(csvContent, `${props.tableConfig.pluralName}.csv`)
    mostrarNotificacion('success', 'Exportado', 'Datos exportados correctamente')
  } catch (error) {
    mostrarNotificacion('error', 'Error', 'No se pudo exportar los datos')
  }
}

const generateCSV = (data: any[]) => {
  if (data.length === 0) return ''
  
  const headers = props.tableConfig.columns.map(col => col.label).join(',')
  const rows = data.map(item => 
    props.tableConfig.columns.map(col => 
      `"${(item[col.key] || '').toString().replace(/"/g, '""')}"` 
    ).join(',')
  )
  
  return [headers, ...rows].join('\n')
}

const downloadCSV = (content: string, filename: string) => {
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
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

const aplicarFiltros = () => {
  mostrarNotificacion('info', 'Filtros', 'Abriendo panel de filtros avanzados')
}

const limpiarFiltros = () => {
  busqueda.value = ''
  ordenActual.value = { campo: '', direccion: 'asc' }
  paginaActual.value = 1
  mostrarNotificacion('success', 'Filtros limpiados', 'Se han eliminado todos los filtros')
}

// =============== NOTIFICACIONES ===============
const mostrarNotificacion = (
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
  
  notificacion.value = {
    show: true,
    type,
    title,
    message,
    icon: icons[type]
  }
  
  const duration = type === 'error' ? 6000 : 4000
  setTimeout(() => {
    cerrarNotificacion()
  }, duration)
}

const cerrarNotificacion = () => {
  notificacion.value.show = false
}

// =============== WATCHERS ===============
watch(() => datosFiltrados.value.length, () => {
  // Ajustar página actual si es necesario
  if (paginaActual.value > totalPaginas.value && totalPaginas.value > 0) {
    paginaActual.value = totalPaginas.value
  }
})

// =============== LIFECYCLE ===============
onMounted(() => {
  cargarDatos()
})
</script>

<style scoped>
/* [TODOS LOS ESTILOS ANTERIORES SE MANTIENEN IGUAL] */
.table-manager {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* Rotating animation for refresh icon */
@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.rotating {
  animation: rotate 1s linear infinite;
}

/* Header */
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 2rem;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
}

.table-title-section h2 {
  margin: 0 0 0.5rem;
  color: #343a40;
  font-size: 1.5rem;
  font-weight: 600;
}

.table-subtitle {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.table-actions {
  display: flex;
  gap: 1rem;
}

/* Controls */
.table-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e9ecef;
  background: white;
}

.search-input-wrapper {
  position: relative;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
  font-size: 20px;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
  border: 1px solid #ced4da;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.filter-section {
  display: flex;
  gap: 0.5rem;
}

/* Loading */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e9ecef;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.error-icon {
  font-size: 4rem;
  color: #dc3545;
  margin-bottom: 1rem;
}

.error-container h3 {
  margin: 0 0 0.5rem;
  color: #343a40;
}

.error-container p {
  margin: 0 0 2rem;
  color: #6c757d;
}

/* Table */
.table-container {
  padding: 0;
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #f8f9fa;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #495057;
  border-bottom: 2px solid #dee2e6;
  white-space: nowrap;
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s;
}

.data-table th.sortable:hover {
  background: #e9ecef;
}

.th-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sort-icon {
  font-size: 18px;
  color: #6c757d;
  transition: color 0.2s;
}

.sort-icon.active {
  color: #007bff;
}

.data-table td {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
  vertical-align: middle;
}

.table-row:hover {
  background-color: #f8f9fa;
}

.cell-content {
  max-width: 500px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Estilos para celdas de rutas */
.cell-path {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f8f9fa;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.85rem;
}

.path-value {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #495057;
}

.btn-copy-path {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  background: #e3f2fd;
  border: 1px solid #90caf9;
  border-radius: 4px;
  color: #1565c0;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.btn-copy-path:hover {
  background: #bbdefb;
  border-color: #64b5f6;
}

.btn-copy-path.copied {
  background: #e8f5e9;
  border-color: #a5d6a7;
  color: #2e7d32;
}

.btn-copy-path .material-icons {
  font-size: 16px;
}

.edit-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #007bff;
  border-radius: 4px;
  background: #fff;
}

.actions-column {
  width: 120px;
  text-align: center;
}

.actions-cell {
  text-align: center;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.btn-icon {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit {
  background: #e3f2fd;
  color: #1976d2;
}

.btn-edit:hover {
  background: #bbdefb;
}

.btn-delete {
  background: #ffebee;
  color: #d32f2f;
}

.btn-delete:hover {
  background: #ffcdd2;
}

.btn-save {
  background: #e8f5e8;
  color: #2e7d32;
}

.btn-save:hover {
  background: #c8e6c9;
}

.btn-cancel {
  background: #fff3e0;
  color: #f57c00;
}

.btn-cancel:hover {
  background: #ffe0b2;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  color: #6c757d;
  margin-bottom: 1rem;
}

.empty-state h3 {
  margin: 0 0 0.5rem;
  color: #343a40;
}

.empty-state p {
  margin: 0 0 2rem;
  color: #6c757d;
}

/* Paginación */
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-top: 1px solid #e9ecef;
  background: #f8f9fa;
}

.pagination-info {
  color: #6c757d;
  font-size: 0.9rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.pagination-current {
  color: #495057;
  font-weight: 500;
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
  z-index: 1050;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  color: #343a40;
}

.btn-close-modal {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.2s;
}

.btn-close-modal:hover {
  background: #f8f9fa;
  color: #343a40;
}

.modal-body {
  padding: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  color: #495057;
  font-weight: 500;
}

.required {
  color: #dc3545;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
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
  border: 1px solid;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #007bff;
  border-color: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
  border-color: #0056b3;
}

.btn-outline-primary {
  background: transparent;
  border-color: #007bff;
  color: #007bff;
}

.btn-outline-primary:hover:not(:disabled) {
  background: #007bff;
  color: white;
}

.btn-outline-secondary {
  background: transparent;
  border-color: #6c757d;
  color: #6c757d;
}

.btn-outline-secondary:hover:not(:disabled) {
  background: #6c757d;
  color: white;
}

.btn-outline-success {
  background: transparent;
  border-color: #28a745;
  color: #28a745;
}

.btn-outline-success:hover:not(:disabled) {
  background: #28a745;
  color: white;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.8rem;
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
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.notification-toast--error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.notification-toast--warning {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.notification-toast--info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
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
  background-color: rgba(0, 0, 0, 0.1);
}

.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

/* Responsive */
@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .table-controls {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .search-input-wrapper {
    max-width: none;
  }
  
  .pagination-container {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .table-actions {
    flex-direction: column;
  }
  
  .notification-toast {
    top: 10px;
    right: 10px;
    left: 10px;
    min-width: auto;
    max-width: none;
  }
  
  .modal-content {
    width: 95%;
  }
  
  .form-actions {
    flex-direction: column;
  }
}

/* Modal de eliminación en cascada */
.modal-warning {
  max-width: 600px;
  border-top: 4px solid #ff9800;
}

.modal-header-warning {
  background: linear-gradient(135deg, #fff3e0, #ffecb3);
  border-bottom: 1px solid #ffcc02;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.warning-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #ff9800, #f57c00);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.warning-icon .material-icons {
  color: white;
  font-size: 32px;
}

.modal-header-warning h3 {
  margin: 0 0 0.25rem;
  color: #e65100;
  font-size: 1.3rem;
}

.modal-header-warning p {
  margin: 0;
  color: #bf360c;
  font-size: 0.9rem;
}

.warning-message {
  background: #fff3e0;
  border: 1px solid #ffcc02;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  text-align: center;
}

.warning-message h4 {
  margin: 0 0 0.5rem;
  color: #e65100;
  font-size: 1.2rem;
  font-weight: 600;
}

.warning-message p {
  margin: 0;
  color: #bf360c;
  line-height: 1.5;
}

.related-data-section {
  margin-bottom: 2rem;
}

.related-data-section h5 {
  margin: 0 0 1rem;
  color: #333;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.loading-related {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  color: #6c757d;
}

.loading-spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid #e9ecef;
  border-top: 2px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.related-tables {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.related-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  transition: all 0.2s;
}

.related-item:hover {
  background: #e9ecef;
  border-color: #dee2e6;
}

.related-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #17a2b8, #138496);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.related-icon .material-icons {
  color: white;
  font-size: 20px;
}

.related-info {
  display: flex;
  flex-direction: column;
}

.related-table {
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
}

.related-count {
  color: #6c757d;
  font-size: 0.8rem;
}

.options-section {
  margin-bottom: 2rem;
}

.options-section h5 {
  margin: 0 0 1rem;
  color: #333;
  font-size: 1rem;
}

.option-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.option-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  transition: all 0.2s;
}

.option-item:hover {
  background: #e9ecef;
  border-color: #dee2e6;
}

.option-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.option-icon.safe {
  background: linear-gradient(135deg, #28a745, #20c997);
}

.option-icon.warning {
  background: linear-gradient(135deg, #ffc107, #fd7e14);
}

.option-icon.info {
  background: linear-gradient(135deg, #17a2b8, #6f42c1);
}

.option-icon .material-icons {
  color: white;
  font-size: 20px;
}

.option-content strong {
  display: block;
  color: #333;
  font-size: 0.95rem;
  margin-bottom: 0.25rem;
}

.option-content p {
  margin: 0;
  color: #6c757d;
  font-size: 0.85rem;
  line-height: 1.4;
}

.btn-danger {
  background: #dc3545;
  border-color: #dc3545;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c82333;
  border-color: #bd2130;
}

.btn-danger:disabled {
  background: #f8d7da;
  border-color: #f5c6cb;
  color: #721c24;
  cursor: not-allowed;
}

/* Responsive para modal de eliminación */
@media (max-width: 768px) {
  .modal-warning {
    width: 95%;
    max-width: none;
  }
  
  .modal-header-warning {
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
  }
  
  .related-tables {
    grid-template-columns: 1fr;
  }
  
  .option-item {
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
  }
}
</style>