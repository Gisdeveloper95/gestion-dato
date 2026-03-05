<template>
  <div class="rutas-pre-operacion-page">
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
        <span class="breadcrumb-current">Rutas Preoperativas</span>
      </div>
      
      <div class="page-title-section">
        <h1 class="page-title">
          <i class="material-icons page-icon">folder</i>
          Rutas Preoperativas
        </h1>
        <p class="page-description">
          Gestión de rutas de directorios para archivos preoperacionales por municipio
        </p>
      </div>
      
      <div class="header-actions">
        <router-link to="/gestion-informacion/database/preoperacion" class="btn-back">
          <i class="material-icons">arrow_back</i>
          Volver a Pre-operación
        </router-link>
      </div>
    </div>

    <!-- Filtros Avanzados -->
    <div class="filtros-container">
      <div class="filtros-header">
        <h3><i class="material-icons">filter_list</i> Filtros Avanzados</h3>
        <div class="filtros-actions">
          <button @click="limpiarTodosFiltros" class="btn-limpiar-todo" :disabled="!hayFiltrosActivos">
            <i class="material-icons">clear_all</i>
            Limpiar Filtros
          </button>
          <span class="contador-registros">
            <i class="material-icons">visibility</i>
            {{ registrosFiltrados.length }} de {{ totalRegistros }} registros
          </span>
        </div>
      </div>

      <div class="filtros-grid">
        <!-- Filtro Búsqueda Global -->
        <div class="filtro-item col-span-full">
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
              placeholder="Buscar por municipio, ruta, ID..."
              class="form-control"
            >
            <button 
              v-if="filtros.busqueda" 
              @click="limpiarFiltro('busqueda')"
              class="btn-clear-input"
              title="Limpiar búsqueda"
            >
              ×
            </button>
          </div>
        </div>

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
              title="Limpiar departamento"
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
              title="Limpiar municipio"
            >
              ×
            </button>
          </div>
        </div>

        <!-- Filtro Fecha Desde -->
        <div class="filtro-item">
          <label for="fechaDesde">
            <i class="material-icons">date_range</i>
            Fecha Desde:
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
              title="Limpiar fecha desde"
            >
              ×
            </button>
          </div>
        </div>

        <!-- Filtro Fecha Hasta -->
        <div class="filtro-item">
          <label for="fechaHasta">
            <i class="material-icons">event</i>
            Fecha Hasta:
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
              title="Limpiar fecha hasta"
            >
              ×
            </button>
          </div>
        </div>

        <!-- Filtro por Existencia de Ruta -->
        <div class="filtro-item">
          <label for="tipoRuta">
            <i class="material-icons">rule</i>
            Tipo de Ruta:
          </label>
          <div class="select-with-clear">
            <select 
              id="tipoRuta"
              v-model="filtros.tipoRuta"
              @change="aplicarFiltros"
              class="form-control"
              :class="{ 'has-selection': filtros.tipoRuta }"
            >
              <option value="">Todas las rutas</option>
              <option value="con_ruta">Con ruta definida</option>
              <option value="ruta_vacia">Ruta vacía/indefinida</option>
            </select>
            <button 
              v-if="filtros.tipoRuta" 
              @click="limpiarFiltro('tipoRuta')"
              class="btn-clear-select"
              title="Limpiar tipo de ruta"
            >
              ×
            </button>
          </div>
        </div>
      </div>

      <!-- Tags Filtros Activos -->
      <div v-if="hayFiltrosActivos" class="filtros-activos">
        <h4><i class="material-icons">local_offer</i> Filtros Activos:</h4>
        <div class="tags-filtros">
          <span v-if="filtros.busqueda" class="tag-filtro busqueda">
            <i class="material-icons">search</i>
            Búsqueda: "{{ filtros.busqueda }}"
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
          <span v-if="filtros.fechaDesde" class="tag-filtro fecha">
            <i class="material-icons">date_range</i>
            Desde: {{ formatearFecha(filtros.fechaDesde) }}
            <button @click="limpiarFiltro('fechaDesde')">×</button>
          </span>
          <span v-if="filtros.fechaHasta" class="tag-filtro fecha">
            <i class="material-icons">event</i>
            Hasta: {{ formatearFecha(filtros.fechaHasta) }}
            <button @click="limpiarFiltro('fechaHasta')">×</button>
          </span>
          <span v-if="filtros.tipoRuta" class="tag-filtro tipo">
            <i class="material-icons">rule</i>
            {{ getTipoRutaLabel(filtros.tipoRuta) }}
            <button @click="limpiarFiltro('tipoRuta')">×</button>
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

// Filtros
const filtros = ref({
  busqueda: '',
  departamento: '',
  municipio: '',
  fechaDesde: '',
  fechaHasta: '',
  tipoRuta: ''
})

// Configuración de la tabla con validaciones para municipios
const tableConfig = computed(() => ({
  title: 'Rutas Preoperativas',
  singularName: 'Ruta Preoperativa',
  pluralName: 'Rutas Preoperativas',
  apiEndpoint: '/preoperacion/path-dir-pre/',
  idField: 'id',
  itemsPerPage: 50,
  columns: [
    {
      key: 'id',
      label: 'ID',
      type: 'number',
      editable: false,
      required: true,
      sortable: true,
      isPrimaryKey: true,
      width: '80px'
    },
    {
      key: 'cod_municipio',
      label: 'Municipio',
      type: 'select',
      editable: true,
      required: true,
      sortable: true,
      options: municipios.value.map(m => ({ 
        value: m.cod_municipio, 
        label: `${m.nom_municipio} (${m.cod_depto?.nom_depto || 'Sin Dpto'})` 
      })),
      placeholder: 'Seleccione un municipio',
      width: '250px',
      validation: {
        required: 'El municipio es obligatorio',
        custom: (value: any) => {
          const municipioExiste = municipios.value.find(m => m.cod_municipio === value)
          return municipioExiste ? null : 'Municipio no válido'
        }
      }
    },
    {
      key: 'path',
      label: 'Ruta del Directorio',
      type: 'textarea',
      editable: true,
      required: true,
      sortable: true,
      placeholder: 'Ingrese la ruta completa del directorio preoperativo',
      maxLength: 1000,
      width: 'calc(100% - 400px)',
      validation: {
        required: 'La ruta es obligatoria',
        minLength: 3,
        pattern: {
          regex: /^[a-zA-Z]:\\|^\/|^\\\\/,
          message: 'La ruta debe ser válida (ej: C:\\ruta, /mnt/ruta o \\\\servidor\\ruta)'
        }
      }
    },
    {
      key: 'fecha_creacion',
      label: 'Fecha Creación',
      type: 'datetime',
      editable: false,
      required: false,
      sortable: true,
      width: '170px'
    }
  ],
  searchFields: ['path', 'cod_municipio__nom_municipio', 'id'],
  orderBy: '-fecha_creacion',
  emptyMessage: 'No hay rutas preoperativas registradas',
  createButtonText: 'Nueva Ruta Preoperativa',
  confirmDeleteMessage: '¿Está seguro que desea eliminar esta ruta preoperativa?',
  // Configuración especial para creación
  beforeCreate: (data: any) => {
    // Validar que el municipio no tenga ya una ruta registrada
    const rutaExistente = registros.value.find(r => r.cod_municipio?.cod_municipio === data.cod_municipio)
    if (rutaExistente) {
      throw new Error(`El municipio ya tiene una ruta registrada (ID: ${rutaExistente.id})`)
    }
    return data
  }
}))

// Permisos
const permissions = computed(() => ({
  canCreate: true,
  canEdit: true,
  canDelete: true,
  canExport: true,
  canImport: false // Deshabilitado por seguridad de rutas
}))

// Computed properties para filtros dinámicos
const registrosFiltrados = computed(() => {
  let resultado = [...registros.value]

  // Filtro por búsqueda global (busca en formato Linux Y Windows)
  if (filtros.value.busqueda.trim()) {
    const busqueda = filtros.value.busqueda.toLowerCase()
    resultado = resultado.filter(r => {
      // Buscar en ruta Linux original
      const pathLinux = r.path?.toLowerCase() || ''
      // Buscar en ruta Windows convertida
      const pathWindows = linuxToWindowsPath(r.path)?.toLowerCase() || ''

      return pathLinux.includes(busqueda) ||
        pathWindows.includes(busqueda) ||
        r.cod_municipio?.nom_municipio?.toLowerCase().includes(busqueda) ||
        r.id?.toString().includes(busqueda)
    })
  }

  // Filtro por departamento
  if (filtros.value.departamento) {
    resultado = resultado.filter(r => {
      const municipio = r.cod_municipio
      if (!municipio) return false
      const codDepto = municipio.cod_depto?.cod_depto || municipio.cod_depto
      return codDepto?.toString() === filtros.value.departamento.toString()
    })
  }

  // Filtro por municipio
  if (filtros.value.municipio) {
    resultado = resultado.filter(r => 
      r.cod_municipio?.cod_municipio?.toString() === filtros.value.municipio.toString()
    )
  }

  // Filtro por fecha desde
  if (filtros.value.fechaDesde) {
    resultado = resultado.filter(r => {
      if (!r.fecha_creacion) return false
      const fechaRegistro = new Date(r.fecha_creacion).toISOString().split('T')[0]
      return fechaRegistro >= filtros.value.fechaDesde
    })
  }

  // Filtro por fecha hasta
  if (filtros.value.fechaHasta) {
    resultado = resultado.filter(r => {
      if (!r.fecha_creacion) return false
      const fechaRegistro = new Date(r.fecha_creacion).toISOString().split('T')[0]
      return fechaRegistro <= filtros.value.fechaHasta
    })
  }

  // Filtro por tipo de ruta
  if (filtros.value.tipoRuta) {
    if (filtros.value.tipoRuta === 'con_ruta') {
      resultado = resultado.filter(r => r.path && r.path.trim().length > 0)
    } else if (filtros.value.tipoRuta === 'ruta_vacia') {
      resultado = resultado.filter(r => !r.path || r.path.trim().length === 0)
    }
  }

  return resultado
})

const departamentosDisponibles = computed(() => {
  const deptosIds = new Set(
    registros.value
      .map(r => {
        const municipio = r.cod_municipio
        if (!municipio) return null
        return municipio.cod_depto?.cod_depto || municipio.cod_depto
      })
      .filter(id => id)
  )
  
  return departamentos.value
    .filter(d => deptosIds.has(d.cod_depto))
    .sort((a, b) => a.nom_depto.localeCompare(b.nom_depto))
})

const municipiosDisponibles = computed(() => {
  let municipiosBase = [...municipios.value]
  
  // Si hay filtro de departamento, filtrar municipios
  if (filtros.value.departamento) {
    municipiosBase = municipiosBase.filter(m => {
      const codDepto = m.cod_depto?.cod_depto || m.cod_depto
      return codDepto?.toString() === filtros.value.departamento.toString()
    })
  }
  
  // Solo mostrar municipios que tienen registros O todos los municipios para crear nuevos
  const municipiosConRegistros = new Set(
    registros.value.map(r => r.cod_municipio?.cod_municipio).filter(id => id)
  )
  
  return municipiosBase
    .filter(m => municipiosConRegistros.has(m.cod_municipio) || !filtros.value.departamento)
    .sort((a, b) => a.nom_municipio.localeCompare(b.nom_municipio))
})

const totalRegistros = computed(() => registros.value.length)

const hayFiltrosActivos = computed(() => 
  filtros.value.busqueda || 
  filtros.value.departamento || 
  filtros.value.municipio || 
  filtros.value.fechaDesde || 
  filtros.value.fechaHasta || 
  filtros.value.tipoRuta
)

// Métodos
const cargarDatos = async () => {
  try {
    cargando.value = true
    error.value = ''
    
    // Cargar datos en paralelo
    const [registrosRes, municipiosRes, departamentosRes] = await Promise.allSettled([
      DominiosService.getAll('/preoperacion/path-dir-pre/'),
      DominiosService.getAll('/municipios/'),
      DominiosService.getAll('/departamentos/')
    ])
    
    if (registrosRes.status === 'fulfilled') {
      registros.value = registrosRes.value || []
      console.log(`✅ Rutas preoperativas cargadas: ${registros.value.length}`)
    } else {
      console.error('Error cargando rutas:', registrosRes.reason)
    }
    
    if (municipiosRes.status === 'fulfilled') {
      municipios.value = municipiosRes.value || []
      console.log(`✅ Municipios cargados: ${municipios.value.length}`)
    } else {
      console.error('Error cargando municipios:', municipiosRes.reason)
    }
    
    if (departamentosRes.status === 'fulfilled') {
      departamentos.value = departamentosRes.value || []
      console.log(`✅ Departamentos cargados: ${departamentos.value.length}`)
    } else {
      console.error('Error cargando departamentos:', departamentosRes.reason)
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
    fechaDesde: '',
    fechaHasta: '',
    tipoRuta: ''
  }
  aplicarFiltros()
}

const handleDepartamentoChange = () => {
  // Si cambia departamento, limpiar municipio si no corresponde
  if (filtros.value.departamento && filtros.value.municipio) {
    const municipioSeleccionado = municipios.value.find(m => 
      m.cod_municipio.toString() === filtros.value.municipio.toString()
    )
    
    if (municipioSeleccionado) {
      const codDepto = municipioSeleccionado.cod_depto?.cod_depto || municipioSeleccionado.cod_depto
      if (codDepto?.toString() !== filtros.value.departamento.toString()) {
        filtros.value.municipio = ''
      }
    }
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

const formatearFecha = (fecha: string) => {
  if (!fecha) return fecha
  const fechaObj = new Date(fecha)
  return fechaObj.toLocaleDateString('es-CO')
}

const getTipoRutaLabel = (tipo: string) => {
  switch (tipo) {
    case 'con_ruta': return 'Con ruta definida'
    case 'ruta_vacia': return 'Ruta vacía'
    default: return tipo
  }
}

// Ciclo de vida
onMounted(() => {
  cargarDatos()
})
</script>

<style scoped>
.rutas-pre-operacion-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  transform: translateY(-1px);
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

.filtros-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border: 1px solid #e9ecef;
}

.col-span-full {
  grid-column: 1 / -1;
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
.tag-filtro.fecha { background: #fff3e0; color: #f57c00; }
.tag-filtro.tipo { background: #e1f5fe; color: #0277bd; }

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
  .filtros-grid {
    grid-template-columns: 1fr;
    padding: 1.5rem;
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
  
  .filtros-grid {
    padding: 1rem;
  }
  
  .filtros-container,
  .page-content {
    padding-left: 1rem;
    padding-right: 1rem;
  }
}
</style>