<template>
  <div class="archivos-pre-operacion-page">
    <!-- Header -->
    <div class="page-header">
      <div class="breadcrumb">
        <router-link to="/gestion-informacion/database" class="breadcrumb-link">
          <i class="material-icons">dashboard</i>
          Gestión Base de Datos
        </router-link>
        <i class="material-icons breadcrumb-separator">chevron_right</i>
        <router-link to="/gestion-informacion/database/preoperacion" class="breadcrumb-link">
          Pre-operación
        </router-link>
        <i class="material-icons breadcrumb-separator">chevron_right</i>
        <span class="breadcrumb-current">Archivos Pre-operación</span>
      </div>
      
      <div class="page-title-section">
        <h1 class="page-title">
          <i class="material-icons page-icon">upload_file</i>
          Archivos Pre-operación
        </h1>
        <p class="page-description">
          Gestión completa de archivos preoperacionales con filtros avanzados para miles de registros
        </p>
      </div>
      
      <div class="header-actions">
        <router-link to="/gestion-informacion/database/preoperacion" class="btn-back">
          <i class="material-icons">arrow_back</i>
          Volver a Pre-operación
        </router-link>
      </div>
    </div>

    <!-- Filtros Avanzados Complejos -->
    <div class="filtros-container">
      <div class="filtros-header">
        <h3><i class="material-icons">filter_list</i> Filtros Avanzados</h3>
        <div class="filtros-actions">
          <button @click="toggleFiltrosAvanzados" class="btn-toggle-filtros">
            <i class="material-icons">{{ mostrarFiltrosAvanzados ? 'expand_less' : 'expand_more' }}</i>
            {{ mostrarFiltrosAvanzados ? 'Ocultar' : 'Mostrar' }} Filtros
          </button>
          <button @click="limpiarTodosFiltros" class="btn-limpiar-todo" :disabled="!hayFiltrosActivos">
            <i class="material-icons">clear_all</i>
            Limpiar Todo
          </button>

          <button @click="toggleFiltrosAvanzados" class="btn-toggle-filtros">
    <i class="material-icons">{{ mostrarFiltrosAvanzados ? 'expand_less' : 'expand_more' }}</i>
    {{ mostrarFiltrosAvanzados ? 'Ocultar' : 'Mostrar' }} Filtros
  </button>
  <button @click="limpiarTodosFiltros" class="btn-limpiar-todo" :disabled="!hayFiltrosActivos">
    <i class="material-icons">clear_all</i>
    Limpiar Todo
  </button>
  
  <!-- 🆕 AGREGAR ESTE BOTÓN NUEVO -->
  <button 
    @click="descargarCSVMunicipioFiltrado" 
    class="btn-csv-municipio"
    :disabled="!filtros.municipio || cargandoCSV"
    :title="filtros.municipio ? `Descargar CSV del municipio seleccionado` : 'Seleccione un municipio para descargar su CSV'"
  >
    <i class="material-icons">{{ cargandoCSV ? 'hourglass_empty' : 'download' }}</i>
    {{ cargandoCSV ? 'Generando...' : 'CSV Municipio' }}
  </button>
  
  <span class="contador-registros">
    <i class="material-icons">visibility</i>
    {{ registrosFiltrados.length }} de {{ totalRegistros }} archivos
  </span>


          
        </div>
      </div>

      <!-- Filtros Básicos (siempre visibles) -->
      <div class="filtros-basicos">
        <div class="filtros-grid-basicos">
          <!-- Búsqueda Global -->
          <div class="filtro-item col-span-2">
            <label for="busqueda">
              <i class="material-icons">search</i>
              Búsqueda Global:
            </label>
            <div class="input-with-clear">
              <input 
                id="busqueda"
                v-model="filtros.busqueda"
                @input="aplicarFiltros"
                type="text"
                placeholder="Buscar por nombre, archivo, usuario, observación..."
                class="form-control"
              >
              <button 
                v-if="filtros.busqueda" 
                @click="limpiarFiltro('busqueda')"
                class="btn-clear-input"
              >
                ×
              </button>
            </div>
          </div>

          <!-- Filtro Rápido por Fecha -->
          <div class="filtro-item">
            <label for="rangoFecha">
              <i class="material-icons">date_range</i>
              Rango de Fecha:
            </label>
            <div class="select-with-clear">
              <select 
                id="rangoFecha"
                v-model="filtros.rangoFecha"
                @change="aplicarRangoFecha"
                class="form-control"
                :class="{ 'has-selection': filtros.rangoFecha }"
              >
                <option value="">Todas las fechas</option>
                <option value="hoy">Hoy</option>
                <option value="semana">Esta semana</option>
                <option value="mes">Este mes</option>
                <option value="trimestre">Este trimestre</option>
                <option value="año">Este año</option>
                <option value="personalizado">Rango personalizado</option>
              </select>
              <button 
                v-if="filtros.rangoFecha" 
                @click="limpiarRangoFecha"
                class="btn-clear-select"
              >
                ×
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Filtros Avanzados (colapsables) -->
      <div v-show="mostrarFiltrosAvanzados" class="filtros-avanzados">
        <div class="filtros-grid">
          <!-- Filtro Departamento -->
          <div class="filtro-item">
            <label for="departamento">
              <i class="material-icons">location_city</i>
              Departamento:
              <span class="contador">({{ departamentosDisponibles.length }})</span>
            </label>
            <div class="select-with-clear">
              <select 
                id="departamento"
                v-model="filtros.departamento"
                @change="handleDepartamentoChange"
                class="form-control"
                :class="{ 'has-selection': filtros.departamento }"
              >
                <option value="">Todos los departamentos</option>
                <option 
                  v-for="depto in departamentosDisponibles" 
                  :key="depto.cod_depto" 
                  :value="depto.cod_depto"
                >
                  {{ depto.nom_depto }}
                </option>
              </select>
              <button 
                v-if="filtros.departamento" 
                @click="limpiarFiltro('departamento')"
                class="btn-clear-select"
              >
                ×
              </button>
            </div>
          </div>

          <!-- Filtro Municipio -->
          <div class="filtro-item">
            <label for="municipio">
              <i class="material-icons">location_on</i>
              Municipio:
              <span class="contador">({{ municipiosDisponibles.length }})</span>
            </label>
            <div class="select-with-clear">
              <select 
                id="municipio"
                v-model="filtros.municipio"
                @change="aplicarFiltros"
                class="form-control"
                :class="{ 'has-selection': filtros.municipio }"
                :disabled="!municipiosDisponibles.length"
              >
                <option value="">Todos los municipios</option>
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
                class="btn-clear-select"
              >
                ×
              </button>
            </div>
          </div>

          <!-- Filtro Categoría de Insumo -->
          <div class="filtro-item">
            <label for="categoria">
              <i class="material-icons">category</i>
              Categoría:
              <span class="contador">({{ categoriasDisponibles.length }})</span>
            </label>
            <div class="select-with-clear">
              <select 
                id="categoria"
                v-model="filtros.categoria"
                @change="handleCategoriaChange"
                class="form-control"
                :class="{ 'has-selection': filtros.categoria }"
              >
                <option value="">Todas las categorías</option>
                <option 
                  v-for="cat in categoriasDisponibles" 
                  :key="cat.cod_categoria" 
                  :value="cat.cod_categoria"
                >
                  {{ cat.nom_categoria }}
                </option>
              </select>
              <button 
                v-if="filtros.categoria" 
                @click="limpiarFiltro('categoria')"
                class="btn-clear-select"
              >
                ×
              </button>
            </div>
          </div>

          <!-- Filtro Insumo -->
          <div class="filtro-item">
            <label for="insumo">
              <i class="material-icons">inventory</i>
              Insumo:
              <span class="contador">({{ insumosDisponibles.length }})</span>
            </label>
            <div class="select-with-clear">
              <select 
                id="insumo"
                v-model="filtros.insumo"
                @change="aplicarFiltros"
                class="form-control"
                :class="{ 'has-selection': filtros.insumo }"
                :disabled="!insumosDisponibles.length"
              >
                <option value="">Todos los insumos</option>
                <option 
                  v-for="ins in insumosDisponibles" 
                  :key="ins.cod_insumo" 
                  :value="ins.cod_insumo"
                >
                  {{ ins.nom_insumo }}
                </option>
              </select>
              <button 
                v-if="filtros.insumo" 
                @click="limpiarFiltro('insumo')"
                class="btn-clear-select"
              >
                ×
              </button>
            </div>
          </div>

          <!-- Filtro Usuario -->
          <div class="filtro-item">
            <label for="usuario">
              <i class="material-icons">person</i>
              Usuario:
              <span class="contador">({{ usuariosDisponibles.length }})</span>
            </label>
            <div class="select-with-clear">
              <select 
                id="usuario"
                v-model="filtros.usuario"
                @change="aplicarFiltros"
                class="form-control"
                :class="{ 'has-selection': filtros.usuario }"
              >
                <option value="">Todos los usuarios</option>
                <option 
                  v-for="usuario in usuariosDisponibles" 
                  :key="usuario" 
                  :value="usuario"
                >
                  {{ usuario }}
                </option>
              </select>
              <button 
                v-if="filtros.usuario" 
                @click="limpiarFiltro('usuario')"
                class="btn-clear-select"
              >
                ×
              </button>
            </div>
          </div>

          <!-- Filtro Estado de Archivo -->
          <div class="filtro-item">
            <label for="estadoArchivo">
              <i class="material-icons">file_present</i>
              Estado Archivo:
            </label>
            <div class="select-with-clear">
              <select 
                id="estadoArchivo"
                v-model="filtros.estadoArchivo"
                @change="aplicarFiltros"
                class="form-control"
                :class="{ 'has-selection': filtros.estadoArchivo }"
              >
                <option value="">Todos los estados</option>
                <option value="con_archivo">Con archivo (path definido)</option>
                <option value="sin_archivo">Sin archivo (sin path)</option>
                <option value="con_hash">Con hash de contenido</option>
                <option value="sin_hash">Sin hash de contenido</option>
                <option value="con_observacion">Con observaciones</option>
                <option value="sin_observacion">Sin observaciones</option>
              </select>
              <button 
                v-if="filtros.estadoArchivo" 
                @click="limpiarFiltro('estadoArchivo')"
                class="btn-clear-select"
              >
                ×
              </button>
            </div>
          </div>

          <!-- Filtros de Fecha Personalizada -->
          <div v-if="filtros.rangoFecha === 'personalizado'" class="filtro-item col-span-2">
            <div class="fecha-personalizada">
              <div class="fecha-item">
                <label for="fechaDesde">
                  <i class="material-icons">date_range</i>
                  Desde:
                </label>
                <div class="input-with-clear">
                  <input 
                    id="fechaDesde"
                    v-model="filtros.fechaDesde"
                    @change="aplicarFiltros"
                    type="date"
                    class="form-control"
                    :class="{ 'has-selection': filtros.fechaDesde }"
                  >
                  <button 
                    v-if="filtros.fechaDesde" 
                    @click="limpiarFiltro('fechaDesde')"
                    class="btn-clear-input"
                  >
                    ×
                  </button>
                </div>
              </div>
              
              <div class="fecha-item">
                <label for="fechaHasta">
                  <i class="material-icons">event</i>
                  Hasta:
                </label>
                <div class="input-with-clear">
                  <input 
                    id="fechaHasta"
                    v-model="filtros.fechaHasta"
                    @change="aplicarFiltros"
                    type="date"
                    class="form-control"
                    :class="{ 'has-selection': filtros.fechaHasta }"
                  >
                  <button 
                    v-if="filtros.fechaHasta" 
                    @click="limpiarFiltro('fechaHasta')"
                    class="btn-clear-input"
                  >
                    ×
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tags Filtros Activos -->
      <div v-if="hayFiltrosActivos" class="filtros-activos">
        <h4><i class="material-icons">local_offer</i> Filtros Activos:</h4>
        <div class="tags-filtros">
          <span v-if="filtros.busqueda" class="tag-filtro busqueda">
            <i class="material-icons">search</i>
            "{{ filtros.busqueda }}"
            <button @click="limpiarFiltro('busqueda')">×</button>
          </span>
          <span v-if="filtros.departamento" class="tag-filtro departamento">
            <i class="material-icons">location_city</i>
            {{ getNombreDepartamento(filtros.departamento) }}
            <button @click="limpiarFiltro('departamento')">×</button>
          </span>
          <span v-if="filtros.municipio" class="tag-filtro municipio">
            <i class="material-icons">location_on</i>
            {{ getNombreMunicipio(filtros.municipio) }}
            <button @click="limpiarFiltro('municipio')">×</button>
          </span>
          <span v-if="filtros.categoria" class="tag-filtro categoria">
            <i class="material-icons">category</i>
            {{ getNombreCategoria(filtros.categoria) }}
            <button @click="limpiarFiltro('categoria')">×</button>
          </span>
          <span v-if="filtros.insumo" class="tag-filtro insumo">
            <i class="material-icons">inventory</i>
            {{ getNombreInsumo(filtros.insumo) }}
            <button @click="limpiarFiltro('insumo')">×</button>
          </span>
          <span v-if="filtros.usuario" class="tag-filtro usuario">
            <i class="material-icons">person</i>
            {{ filtros.usuario }}
            <button @click="limpiarFiltro('usuario')">×</button>
          </span>
          <span v-if="filtros.estadoArchivo" class="tag-filtro estado">
            <i class="material-icons">file_present</i>
            {{ getEstadoArchivoLabel(filtros.estadoArchivo) }}
            <button @click="limpiarFiltro('estadoArchivo')">×</button>
          </span>
          <span v-if="filtros.rangoFecha && filtros.rangoFecha !== 'personalizado'" class="tag-filtro fecha">
            <i class="material-icons">date_range</i>
            {{ getRangoFechaLabel(filtros.rangoFecha) }}
            <button @click="limpiarRangoFecha">×</button>
          </span>
          <span v-if="filtros.fechaDesde || filtros.fechaHasta" class="tag-filtro fecha">
            <i class="material-icons">date_range</i>
            {{ formatearRangoPersonalizado() }}
            <button @click="limpiarFechasPersonalizadas">×</button>
          </span>
        </div>
      </div>
    </div>

    <!-- Contenido principal -->
    <div class="page-content">
      <div class="table-container">
        <TableManager
          :table-config="tableConfig"
          :permissions="permissions"
          :data-override="registrosFiltrados"
          :loading-override="cargando"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import TableManager from '@/pages/gestion/database/components/TableManager.vue'
import { DominiosService } from '@/api/dominios'
import type { Municipio, Departamento } from '@/models/municipio'
import { linuxToWindowsPath, copyPathToClipboard } from '@/utils/pathUtils'

// Estado para copiar rutas
const rutaCopiada = ref<string | null>(null)

// Estados reactivos
const cargando = ref(false)
const error = ref('')
const registros = ref<any[]>([])
const municipios = ref<Municipio[]>([])
const departamentos = ref<Departamento[]>([])
const categorias = ref<any[]>([])
const insumos = ref<any[]>([])
const mostrarFiltrosAvanzados = ref(false)

const cargandoCSV = ref(false)

// Filtros
const filtros = ref({
  busqueda: '',
  departamento: '',
  municipio: '',
  categoria: '',
  insumo: '',
  usuario: '',
  estadoArchivo: '',
  rangoFecha: '',
  fechaDesde: '',
  fechaHasta: ''
})

// Configuración de la tabla con validaciones para insumos
const tableConfig = computed(() => ({
  title: 'Archivos Pre-operación',
  singularName: 'Archivo Pre-operación',
  pluralName: 'Archivos Pre-operación',
  apiEndpoint: '/preoperacion/lista-archivos-pre/',
  idField: 'id_lista_archivo',
  itemsPerPage: 50,
  columns: [
    {
      key: 'id_lista_archivo',
      label: 'ID',
      type: 'number',
      editable: false,
      required: true,
      sortable: true,
      isPrimaryKey: true,
      width: '80px'
    },
    {
      key: 'cod_insumo',
      label: 'Insumo',
      type: 'select',
      editable: true,
      required: true,
      sortable: true,
      options: insumos.value.map(i => ({ 
        value: i.cod_insumo, 
        label: `${i.nom_insumo} (${i.cod_categoria?.nom_categoria || 'Sin Cat'})` 
      })),
      placeholder: 'Seleccione un insumo',
      width: '200px'
    },
    {
      key: 'nombre_insumo',
      label: 'Nombre del Archivo',
      type: 'text',
      editable: true,
      required: false,
      sortable: true,
      placeholder: 'Nombre descriptivo del archivo',
      maxLength: 500,
      width: '250px'
    },
    {
      key: 'fecha_disposicion',
      label: 'Fecha Disposición',
      type: 'date',
      editable: true,
      required: false,
      sortable: true,
      width: '140px'
    },
    {
      key: 'observacion',
      label: 'Observación',
      type: 'textarea',
      editable: true,
      required: false,
      sortable: true,
      placeholder: 'Observaciones sobre el archivo',
      maxLength: 1000,
      width: '200px'
    },
    {
      key: 'path_file',
      label: 'Ruta del Archivo',
      type: 'text',
      editable: true,
      required: false,
      sortable: true,
      placeholder: 'Ruta completa del archivo',
      maxLength: 500,
      width: 'calc(100% - 870px)'
    },
    {
      key: 'usuario_windows',
      label: 'Usuario',
      type: 'text',
      editable: true,
      required: false,
      sortable: true,
      placeholder: 'Usuario de Windows',
      maxLength: 100,
      width: '120px'
    }
  ],
  searchFields: ['nombre_insumo', 'path_file', 'observacion', 'usuario_windows'],
  orderBy: '-fecha_disposicion',
  emptyMessage: 'No hay archivos pre-operación registrados',
  createButtonText: 'Nuevo Archivo',
  confirmDeleteMessage: '¿Está seguro que desea eliminar este archivo pre-operación?'
}))

// Permisos
const permissions = computed(() => ({
  canCreate: true,
  canEdit: true,
  canDelete: true,
  canExport: true,
  canImport: true
}))

// Computed properties para filtros dinámicos
const registrosFiltrados = computed(() => {
  let resultado = [...registros.value]

  // Filtro por búsqueda global (busca en formato Linux Y Windows)
  if (filtros.value.busqueda.trim()) {
    const busqueda = filtros.value.busqueda.toLowerCase()
    resultado = resultado.filter(r => {
      // Buscar en ruta Linux original
      const pathLinux = r.path_file?.toLowerCase() || ''
      // Buscar en ruta Windows convertida
      const pathWindows = linuxToWindowsPath(r.path_file)?.toLowerCase() || ''

      return r.nombre_insumo?.toLowerCase().includes(busqueda) ||
        pathLinux.includes(busqueda) ||
        pathWindows.includes(busqueda) ||
        r.observacion?.toLowerCase().includes(busqueda) ||
        r.usuario_windows?.toLowerCase().includes(busqueda) ||
        r.cod_insumo?.nom_insumo?.toLowerCase().includes(busqueda)
    })
  }

  // Filtro por departamento (a través del municipio del insumo)
  if (filtros.value.departamento) {
    resultado = resultado.filter(r => {
      const insumo = r.cod_insumo
      if (!insumo?.cod_municipio) return false
      const municipio = insumo.cod_municipio
      const codDepto = municipio.cod_depto?.cod_depto || municipio.cod_depto
      return codDepto?.toString() === filtros.value.departamento.toString()
    })
  }

  // Filtro por municipio
  if (filtros.value.municipio) {
    resultado = resultado.filter(r => {
      const insumo = r.cod_insumo
      return insumo?.cod_municipio?.cod_municipio?.toString() === filtros.value.municipio.toString()
    })
  }

  // Filtro por categoría
  if (filtros.value.categoria) {
    resultado = resultado.filter(r => {
      const insumo = r.cod_insumo
      return insumo?.cod_categoria?.cod_categoria?.toString() === filtros.value.categoria.toString()
    })
  }

  // Filtro por insumo
  if (filtros.value.insumo) {
    resultado = resultado.filter(r => 
      r.cod_insumo?.cod_insumo?.toString() === filtros.value.insumo.toString()
    )
  }

  // Filtro por usuario
  if (filtros.value.usuario) {
    resultado = resultado.filter(r => 
      r.usuario_windows?.toLowerCase().includes(filtros.value.usuario.toLowerCase())
    )
  }

  // Filtro por estado de archivo
  if (filtros.value.estadoArchivo) {
    switch (filtros.value.estadoArchivo) {
      case 'con_archivo':
        resultado = resultado.filter(r => r.path_file && r.path_file.trim())
        break
      case 'sin_archivo':
        resultado = resultado.filter(r => !r.path_file || !r.path_file.trim())
        break
      case 'con_hash':
        resultado = resultado.filter(r => r.hash_contenido && r.hash_contenido.trim())
        break
      case 'sin_hash':
        resultado = resultado.filter(r => !r.hash_contenido || !r.hash_contenido.trim())
        break
      case 'con_observacion':
        resultado = resultado.filter(r => r.observacion && r.observacion.trim())
        break
      case 'sin_observacion':
        resultado = resultado.filter(r => !r.observacion || !r.observacion.trim())
        break
    }
  }

  // Filtros de fecha
  const ahora = new Date()
  const fechaDesde = filtros.value.fechaDesde ? new Date(filtros.value.fechaDesde) : null
  const fechaHasta = filtros.value.fechaHasta ? new Date(filtros.value.fechaHasta) : null

  if (fechaDesde || fechaHasta) {
    resultado = resultado.filter(r => {
      if (!r.fecha_disposicion) return false
      const fechaRegistro = new Date(r.fecha_disposicion)
      
      if (fechaDesde && fechaRegistro < fechaDesde) return false
      if (fechaHasta && fechaRegistro > fechaHasta) return false
      
      return true
    })
  }

  return resultado
})

// Opciones dinámicas para filtros
const departamentosDisponibles = computed(() => {
  const deptosIds = new Set()
  registros.value.forEach(r => {
    const insumo = r.cod_insumo
    if (insumo?.cod_municipio) {
      const municipio = insumo.cod_municipio
      const codDepto = municipio.cod_depto?.cod_depto || municipio.cod_depto
      if (codDepto) deptosIds.add(codDepto)
    }
  })
  
  return departamentos.value
    .filter(d => deptosIds.has(d.cod_depto))
    .sort((a, b) => a.nom_depto.localeCompare(b.nom_depto))
})

const municipiosDisponibles = computed(() => {
  const municipiosIds = new Set()
  
  // Filtrar por departamento si está seleccionado
  registros.value.forEach(r => {
    const insumo = r.cod_insumo
    if (insumo?.cod_municipio) {
      const municipio = insumo.cod_municipio
      
      if (filtros.value.departamento) {
        const codDepto = municipio.cod_depto?.cod_depto || municipio.cod_depto
        if (codDepto?.toString() === filtros.value.departamento.toString()) {
          municipiosIds.add(municipio.cod_municipio)
        }
      } else {
        municipiosIds.add(municipio.cod_municipio)
      }
    }
  })
  
  return municipios.value
    .filter(m => municipiosIds.has(m.cod_municipio))
    .sort((a, b) => a.nom_municipio.localeCompare(b.nom_municipio))
})

const categoriasDisponibles = computed(() => {
  const categoriasIds = new Set()
  
  registros.value.forEach(r => {
    const insumo = r.cod_insumo
    if (insumo?.cod_categoria) {
      categoriasIds.add(insumo.cod_categoria.cod_categoria)
    }
  })
  
  return categorias.value
    .filter(c => categoriasIds.has(c.cod_categoria))
    .sort((a, b) => a.nom_categoria.localeCompare(b.nom_categoria))
})

const insumosDisponibles = computed(() => {
  let insumosBase = [...insumos.value]
  
  // Filtrar por categoría si está seleccionada
  if (filtros.value.categoria) {
    insumosBase = insumosBase.filter(i => 
      i.cod_categoria?.cod_categoria?.toString() === filtros.value.categoria.toString()
    )
  }
  
  // Solo mostrar insumos que tienen archivos
  const insumosIds = new Set(
    registros.value.map(r => r.cod_insumo?.cod_insumo).filter(id => id)
  )
  
  return insumosBase
    .filter(i => insumosIds.has(i.cod_insumo))
    .sort((a, b) => a.nom_insumo.localeCompare(b.nom_insumo))
})

const usuariosDisponibles = computed(() => {
  const usuarios = new Set(
    registros.value
      .map(r => r.usuario_windows)
      .filter(u => u && u.trim())
  )
  
  return Array.from(usuarios).sort()
})

const totalRegistros = computed(() => registros.value.length)

const hayFiltrosActivos = computed(() => 
  filtros.value.busqueda || 
  filtros.value.departamento || 
  filtros.value.municipio || 
  filtros.value.categoria || 
  filtros.value.insumo || 
  filtros.value.usuario || 
  filtros.value.estadoArchivo || 
  filtros.value.rangoFecha || 
  filtros.value.fechaDesde || 
  filtros.value.fechaHasta
)

// Métodos
const cargarDatos = async () => {
  try {
    cargando.value = true
    error.value = ''
    
    // Cargar datos en paralelo
    const [registrosRes, municipiosRes, departamentosRes, categoriasRes, insumosRes] = await Promise.allSettled([
      DominiosService.getAll('/preoperacion/lista-archivos-pre/'),
      DominiosService.getAll('/municipios/'),
      DominiosService.getAll('/departamentos/'),
      DominiosService.getAll('/categorias/'),
      DominiosService.getAll('/insumos/')
    ])
    
    if (registrosRes.status === 'fulfilled') {
      registros.value = registrosRes.value || []
      console.log(`✅ Archivos pre-operación cargados: ${registros.value.length}`)
    }
    
    if (municipiosRes.status === 'fulfilled') {
      municipios.value = municipiosRes.value || []
    }
    
    if (departamentosRes.status === 'fulfilled') {
      departamentos.value = departamentosRes.value || []
    }
    
    if (categoriasRes.status === 'fulfilled') {
      categorias.value = categoriasRes.value || []
    }
    
    if (insumosRes.status === 'fulfilled') {
      insumos.value = insumosRes.value || []
    }
    
  } catch (err) {
    console.error('Error cargando datos:', err)
    error.value = 'Error al cargar los datos'
  } finally {
    cargando.value = false
  }
}

const aplicarFiltros = () => {
  console.log('🔍 Filtros aplicados:', filtros.value)
  console.log(`📊 Resultados: ${registrosFiltrados.value.length}/${totalRegistros.value}`)
}

const limpiarFiltro = (filtro: string) => {
  (filtros.value as any)[filtro] = ''
  aplicarFiltros()
}

const limpiarTodosFiltros = () => {
  filtros.value = {
    busqueda: '',
    departamento: '',
    municipio: '',
    categoria: '',
    insumo: '',
    usuario: '',
    estadoArchivo: '',
    rangoFecha: '',
    fechaDesde: '',
    fechaHasta: ''
  }
  aplicarFiltros()
}

const toggleFiltrosAvanzados = () => {
  mostrarFiltrosAvanzados.value = !mostrarFiltrosAvanzados.value
}

const handleDepartamentoChange = () => {
  filtros.value.municipio = ''
  aplicarFiltros()
}

const handleCategoriaChange = () => {
  filtros.value.insumo = ''
  aplicarFiltros()
}

const aplicarRangoFecha = () => {
  const ahora = new Date()
  const hoy = new Date(ahora.getFullYear(), ahora.getMonth(), ahora.getDate())
  
  switch (filtros.value.rangoFecha) {
    case 'hoy':
      filtros.value.fechaDesde = hoy.toISOString().split('T')[0]
      filtros.value.fechaHasta = hoy.toISOString().split('T')[0]
      break
    case 'semana':
      const inicioSemana = new Date(hoy)
      inicioSemana.setDate(hoy.getDate() - hoy.getDay())
      filtros.value.fechaDesde = inicioSemana.toISOString().split('T')[0]
      filtros.value.fechaHasta = hoy.toISOString().split('T')[0]
      break
    case 'mes':
      const inicioMes = new Date(ahora.getFullYear(), ahora.getMonth(), 1)
      filtros.value.fechaDesde = inicioMes.toISOString().split('T')[0]
      filtros.value.fechaHasta = hoy.toISOString().split('T')[0]
      break
    case 'trimestre':
      const inicioTrimestre = new Date(ahora.getFullYear(), Math.floor(ahora.getMonth() / 3) * 3, 1)
      filtros.value.fechaDesde = inicioTrimestre.toISOString().split('T')[0]
      filtros.value.fechaHasta = hoy.toISOString().split('T')[0]
      break
    case 'año':
      const inicioAño = new Date(ahora.getFullYear(), 0, 1)
      filtros.value.fechaDesde = inicioAño.toISOString().split('T')[0]
      filtros.value.fechaHasta = hoy.toISOString().split('T')[0]
      break
    case 'personalizado':
      // No hacer nada, el usuario seleccionará las fechas manualmente
      break
    default:
      filtros.value.fechaDesde = ''
      filtros.value.fechaHasta = ''
  }
  
  aplicarFiltros()
}

const limpiarRangoFecha = () => {
  filtros.value.rangoFecha = ''
  filtros.value.fechaDesde = ''
  filtros.value.fechaHasta = ''
  aplicarFiltros()
}

const limpiarFechasPersonalizadas = () => {
  filtros.value.fechaDesde = ''
  filtros.value.fechaHasta = ''
  if (filtros.value.rangoFecha === 'personalizado') {
    filtros.value.rangoFecha = ''
  }
  aplicarFiltros()
}

// Funciones de utilidad
const getNombreDepartamento = (codDepto: string) => {
  const depto = departamentos.value.find(d => d.cod_depto.toString() === codDepto.toString())
  return depto?.nom_depto || codDepto
}

const getNombreMunicipio = (codMunicipio: string) => {
  const municipio = municipios.value.find(m => m.cod_municipio.toString() === codMunicipio.toString())
  return municipio?.nom_municipio || codMunicipio
}

const getNombreCategoria = (codCategoria: string) => {
  const categoria = categorias.value.find(c => c.cod_categoria.toString() === codCategoria.toString())
  return categoria?.nom_categoria || codCategoria
}

const getNombreInsumo = (codInsumo: string) => {
  const insumo = insumos.value.find(i => i.cod_insumo.toString() === codInsumo.toString())
  return insumo?.nom_insumo || codInsumo
}

const getEstadoArchivoLabel = (estado: string) => {
  const labels: Record<string, string> = {
    'con_archivo': 'Con archivo',
    'sin_archivo': 'Sin archivo',
    'con_hash': 'Con hash',
    'sin_hash': 'Sin hash',
    'con_observacion': 'Con observaciones',
    'sin_observacion': 'Sin observaciones'
  }
  return labels[estado] || estado
}

const getRangoFechaLabel = (rango: string) => {
  const labels: Record<string, string> = {
    'hoy': 'Hoy',
    'semana': 'Esta semana',
    'mes': 'Este mes',
    'trimestre': 'Este trimestre',
    'año': 'Este año'
  }
  return labels[rango] || rango
}

const formatearRangoPersonalizado = () => {
  const desde = filtros.value.fechaDesde
  const hasta = filtros.value.fechaHasta
  
  if (desde && hasta) {
    return `${desde} a ${hasta}`
  } else if (desde) {
    return `Desde ${desde}`
  } else if (hasta) {
    return `Hasta ${hasta}`
  }
  
  return 'Rango personalizado'
}







// 🆕 FUNCIÓN PARA DESCARGAR CSV DEL MUNICIPIO FILTRADO
const descargarCSVMunicipioFiltrado = async () => {
  if (!filtros.value.municipio) {
    showNotification('Debe seleccionar un municipio primero', 'warning');
    return;
  }
  
  try {
    cargandoCSV.value = true;
    
    // Obtener información del municipio seleccionado
    const municipioSeleccionado = municipios.value.find(m => 
      m.cod_municipio.toString() === filtros.value.municipio.toString()
    );
    
    if (!municipioSeleccionado) {
      showNotification('Municipio no encontrado', 'error');
      return;
    }
    
    showNotification(`Cargando archivos de ${municipioSeleccionado.nom_municipio}...`, 'info');
    
    // ✅ USAR ENDPOINT ESPECÍFICO POR MUNICIPIO
    const response = await api.get(`/preoperacion/archivos-pre/por_municipio/?municipio_id=${filtros.value.municipio}`);
    const archivosMunicipio = Array.isArray(response) ? response : (Array.isArray(response.results) ? response.results : []);
    
    if (archivosMunicipio.length === 0) {
      showNotification(`No se encontraron archivos para ${municipioSeleccionado.nom_municipio}`, 'warning');
      return;
    }
    
    console.log(`📊 Archivos del municipio ${municipioSeleccionado.nom_municipio}: ${archivosMunicipio.length}`);
    
    // Cargar clasificaciones para nombres (usar las ya cargadas si existen)
    let clasificacionesCompletas = clasificaciones.value || [];
    if (clasificacionesCompletas.length === 0) {
      try {
        const responseClasif = await api.get('/preoperacion/clasificaciones/');
        clasificacionesCompletas = Array.isArray(responseClasif) ? responseClasif : (Array.isArray(responseClasif.results) ? responseClasif.results : []);
      } catch (error) {
        console.warn('Error cargando clasificaciones:', error);
      }
    }
    
    // Crear mapa de clasificaciones
    const clasificacionesMap = new Map();
    clasificacionesCompletas.forEach(c => {
      clasificacionesMap.set(c.cod_clasificacion, c.nombre || c.nom_clasificacion || c.nom_insumo || 'Sin nombre');
    });
    
    // Obtener información del departamento
    const departamento = getNombreDepartamento(municipioSeleccionado.cod_depto);
    
    // Preparar datos para CSV
    const datosCSV = [];
    
    archivosMunicipio.forEach(archivo => {
      // Estructura real: { id_lista_archivo, nombre_insumo, cod_insumo, fecha_disposicion, hash_contenido, observacion, path_file, usuario_windows }
      
      // Buscar nombre de clasificación
      let nombreClasificacion = 'N/A';
      if (archivo.cod_insumo) {
        nombreClasificacion = clasificacionesMap.get(archivo.cod_insumo) || `Insumo ${archivo.cod_insumo}`;
      }
      
      // Calcular extensión del archivo
      let extension = 'N/A';
      if (archivo.path_file) {
        const partes = archivo.path_file.split('.');
        if (partes.length > 1) {
          extension = partes[partes.length - 1].toUpperCase();
        }
      }
      
      // Calcular tamaño del archivo desde la ruta (aproximado)
      let tamanoAproximado = 'N/A';
      if (archivo.path_file) {
        // Intentar extraer info del nombre del archivo
        const nombreArchivo = archivo.path_file.split('\\').pop() || archivo.path_file.split('/').pop();
        tamanoAproximado = 'Ver archivo'; // Placeholder, el tamaño real requeriría consulta al filesystem
      }
      
      datosCSV.push({
        id: archivo.id_lista_archivo || 'N/A',
        municipio: municipioSeleccionado.nom_municipio,
        departamento: departamento,
        nombreArchivo: archivo.nombre_insumo || 'Sin nombre',
        clasificacion: nombreClasificacion,
        ruta: linuxToWindowsPath(archivo.path_file) || 'N/A',
        tamano: tamanoAproximado,
        fechaCreacion: formatearFechaCSV(archivo.fecha_disposicion || ''),
        extension: extension,
        observacion: archivo.observacion || '',
        usuario: archivo.usuario_windows || '',
        hashContenido: archivo.hash_contenido || 'N/A'
      });
    });
    
    // Generar contenido CSV
    let contenidoCSV = `ID,Municipio,Departamento,Nombre Archivo,Clasificación,Ruta,Tamaño,Fecha Creación,Extensión,Observación,Usuario,Hash Contenido\n`;
    
    datosCSV.forEach(item => {
      const fila = [
        escaparCSV(item.id),
        escaparCSV(item.municipio),
        escaparCSV(item.departamento),
        escaparCSV(item.nombreArchivo),
        escaparCSV(item.clasificacion),
        escaparCSV(item.ruta),
        escaparCSV(item.tamano),
        escaparCSV(item.fechaCreacion),
        escaparCSV(item.extension),
        escaparCSV(item.observacion),
        escaparCSV(item.usuario),
        escaparCSV(item.hashContenido)
      ].join(',');
      
      contenidoCSV += fila + '\n';
    });
    
    // Crear y descargar archivo
    const blob = generarCSVConBOM(contenidoCSV);
    const fecha = new Date().toISOString().split('T')[0];
    const nombreArchivo = `archivos_${municipioSeleccionado.nom_municipio.replace(/\s+/g, '_')}_${fecha}.csv`;
    
    descargarArchivo(blob, nombreArchivo);
    
    showNotification(`CSV descargado: ${datosCSV.length} archivos de ${municipioSeleccionado.nom_municipio}`, 'success');
    
  } catch (error) {
    console.error('Error generando CSV del municipio:', error);
    showNotification('Error al generar CSV del municipio', 'error');
  } finally {
    cargandoCSV.value = false;
  }
};

// 🆕 FUNCIONES AUXILIARES PARA CSV (si no existen ya)
const generarCSVConBOM = (contenidoCSV: string): Blob => {
  const BOM = '\uFEFF';
  const contenidoConBOM = BOM + contenidoCSV;
  return new Blob([contenidoConBOM], { type: 'text/csv;charset=utf-8;' });
};

const escaparCSV = (valor: any): string => {
  if (valor === null || valor === undefined) return '';
  const str = String(valor);
  if (str.includes('"') || str.includes(',') || str.includes('\n') || str.includes('\r')) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
};

const descargarArchivo = (blob: Blob, nombreArchivo: string) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = nombreArchivo;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

const formatearFechaCSV = (fecha: string): string => {
  if (!fecha) return '';
  try {
    return format(parseISO(fecha), 'dd/MM/yyyy', { locale: es });
  } catch {
    return fecha;
  }
};

// 🆕 FUNCIÓN PARA MOSTRAR NOTIFICACIONES (si no existe)
const showNotification = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
  // Implementar según tu sistema de notificaciones
  // Ejemplo básico:
  console.log(`${type.toUpperCase()}: ${message}`);
  
  // Si usas alguna librería de notificaciones como vue-toastification:
  // toast[type](message);
  
  // O si tienes un sistema propio de notificaciones:
  // $emit('show-notification', { message, type });
};


// Ciclo de vida
onMounted(() => {
  cargarDatos()
})
</script>

<style scoped>

/* 🎨 AGREGAR ESTOS ESTILOS AL FINAL DEL CSS EXISTENTE */

.btn-csv-municipio {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #28a745;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.9rem;
  font-weight: 500;
}

.btn-csv-municipio:hover:not(:disabled) {
  background: #218838;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3);
}

.btn-csv-municipio:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
  transform: none;
  box-shadow: none;
}

.btn-csv-municipio .material-icons {
  font-size: 1.1rem;
}

/* Animación para el icono de carga */
.btn-csv-municipio:disabled .material-icons {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}


.archivos-pre-operacion-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.page-header {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
  padding: 2rem 0;
  margin-bottom: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.breadcrumb {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.breadcrumb-link {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: color 0.3s ease;
}

.breadcrumb-link:hover {
  color: white;
  text-decoration: none;
}

.breadcrumb-separator {
  margin: 0 0.5rem;
  opacity: 0.7;
  font-size: 1.2rem;
}

.breadcrumb-current {
  opacity: 0.9;
  font-weight: 500;
}

.page-title-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.page-icon {
  font-size: 2.5rem;
  opacity: 0.9;
}

.page-description {
  font-size: 1.1rem;
  opacity: 0.9;
  line-height: 1.5;
  margin: 0;
  max-width: 600px;
}

.header-actions {
  max-width: 1200px;
  margin: 2rem auto 0;
  padding: 0 2rem;
  display: flex;
  justify-content: flex-end;
}

.btn-back {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  color: white;
  text-decoration: none;
}

.filtros-container {
  max-width: 1200px;
  margin: 0 auto 2rem;
  padding: 0 2rem;
}

.filtros-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.filtros-header h3 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  color: #333;
  font-size: 1.3rem;
}

.filtros-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-toggle-filtros {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #007bff;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.9rem;
}

.btn-toggle-filtros:hover {
  background: #0056b3;
}

.btn-limpiar-todo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #dc3545;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.9rem;
}

.btn-limpiar-todo:hover:not(:disabled) {
  background: #c82333;
}

.btn-limpiar-todo:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
}

.contador-registros {
  background: #f8f9fa;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border: 1px solid #dee2e6;
  font-weight: 500;
  color: #495057;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.filtros-basicos {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border: 1px solid #e9ecef;
  margin-bottom: 1rem;
}

.filtros-grid-basicos {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

.filtros-avanzados {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border: 1px solid #e9ecef;
  margin-bottom: 1rem;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.filtros-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.col-span-2 {
  grid-column: span 2;
}

.filtro-item label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.filtro-item .material-icons {
  font-size: 1.2rem;
  color: #6c757d;
}

.contador {
  font-size: 0.8rem;
  color: #6c757d;
  font-weight: normal;
  background: #f8f9fa;
  padding: 0.2rem 0.5rem;
  border-radius: 10px;
}

.input-with-clear,
.select-with-clear {
  position: relative;
}

.form-control {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: all 0.3s;
  background: white;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.form-control.has-selection {
  border-color: #007bff;
  background-color: #f0f8ff;
}

.form-control:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.btn-clear-input,
.btn-clear-select {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.btn-clear-input:hover,
.btn-clear-select:hover {
  background: #c82333;
  transform: translateY(-50%) scale(1.1);
}

.fecha-personalizada {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.fecha-item label {
  font-size: 0.85rem;
  margin-bottom: 0.3rem;
}

.filtros-activos {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  border-left: 4px solid #28a745;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filtros-activos h4 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 1rem;
  color: #333;
  font-size: 1rem;
}

.tags-filtros {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
}

.tag-filtro {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  transition: all 0.3s;
}

.tag-filtro .material-icons {
  font-size: 1rem;
}

.tag-filtro button {
  background: none;
  border: none;
  color: inherit;
  font-size: 1rem;
  cursor: pointer;
  margin-left: 0.3rem;
  padding: 0;
  line-height: 1;
  transition: transform 0.2s;
}

.tag-filtro button:hover {
  transform: scale(1.2);
}

.tag-filtro.busqueda { background: #e3f2fd; color: #1976d2; }
.tag-filtro.departamento { background: #f3e5f5; color: #7b1fa2; }
.tag-filtro.municipio { background: #e8f5e8; color: #388e3c; }
.tag-filtro.categoria { background: #fff3e0; color: #f57c00; }
.tag-filtro.insumo { background: #e1f5fe; color: #0277bd; }
.tag-filtro.usuario { background: #fce4ec; color: #c2185b; }
.tag-filtro.estado { background: #f1f8e9; color: #558b2f; }
.tag-filtro.fecha { background: #fff8e1; color: #ff8f00; }

.page-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem 3rem;
}

.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

/* Responsive */
@media (max-width: 768px) {
  .filtros-actions {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .btn-csv-municipio {
    font-size: 0.8rem;
    padding: 0.4rem 0.8rem;
  }

  
  .filtros-grid,
  .filtros-grid-basicos {
    grid-template-columns: 1fr;
  }
  
  .col-span-2 {
    grid-column: span 1;
  }
  
  .fecha-personalizada {
    grid-template-columns: 1fr;
  }
  
  .filtros-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filtros-actions {
    justify-content: space-between;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .breadcrumb {
    flex-wrap: wrap;
    gap: 0.25rem;
  }
  
  .tags-filtros {
    gap: 0.5rem;
  }
  
  .tag-filtro {
    font-size: 0.75rem;
    padding: 0.3rem 0.6rem;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.75rem;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .filtros-basicos,
  .filtros-avanzados {
    padding: 1rem;
  }
  
  .filtros-container,
  .page-content {
    padding-left: 1rem;
    padding-right: 1rem;
  }
}
</style>