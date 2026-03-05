<template>
  <div class="profesionales-list-page">
    <!-- Cabecera con título y acciones principales -->
    <div class="page-header">
      <div class="header-content">
        <h1>Gestión de Profesionales de Seguimiento</h1>
        <div class="header-actions">
          <button @click="showCreateModal" class="btn-primary">
            <i class="material-icons">person_add</i>
            Nuevo Profesional
          </button>
          <button @click="goToAsignaciones" class="btn-outline">
            <i class="material-icons">assignment</i>
            Gestionar Asignaciones
          </button>
          <button @click="goToAsignacionesMasivas" class="btn-accent">
            <i class="material-icons">library_add</i>
            Asignaciones Masivas
          </button>
        </div>
      </div>
    </div>

    <!-- Panel de búsqueda y filtros avanzados -->
    <div class="filters-panel">
      <div class="search-filters-container">
        <!-- Búsqueda global -->
        <div class="global-search">
          <i class="material-icons">search</i>
          <input 
            type="text"
            v-model="searchTerm"
            placeholder="Buscar por nombre, correo o código..."
            @input="handleSearchInput"
          />
          <button v-if="searchTerm" @click="clearSearch" class="clear-btn">
            <i class="material-icons">close</i>
          </button>
        </div>

        <!-- Filtros principales -->
        <div class="filters-row">
          <div class="filter-item">
            <label>Rol:
              <span class="contador-opciones">({{ rolesDisponibles.length }} disponibles)</span>
            </label>
            <select v-model="filters.rol" @change="handleFilter">
              <option value="">Todos los roles</option>
              <option 
                v-for="rol in rolesDisponibles" 
                :key="rol.rol_profesional" 
                :value="rol.rol_profesional"
              >
                {{ rol.rol_profesional }}
              </option>
            </select>
          </div>

          <div class="filter-item">
            <label>Territorial:
              <span class="contador-opciones">({{ territorialesDisponibles.length }} disponibles)</span>
            </label>
            <select v-model="filters.territorial" @change="handleTerritorialChange">
              <option value="">Todas las territoriales</option>
              <option 
                v-for="territorial in territorialesDisponibles" 
                :key="territorial.nom_territorial" 
                :value="territorial.nom_territorial"
              >
                {{ territorial.nom_territorial }}
              </option>
            </select>
          </div>

          <div class="filter-item">
            <label>Departamento:
              <span class="contador-opciones">({{ departamentosDisponibles.length }} disponibles)</span>
            </label>
            <select v-model="filters.departamento" @change="handleDepartamentoChange">
              <option value="">Todos los departamentos</option>
              <option 
                v-for="depto in departamentosDisponibles" 
                :key="depto.cod_depto" 
                :value="depto.cod_depto"
              >
                {{ depto.nom_depto }}
              </option>
            </select>
          </div>
        </div>

        <div class="filters-row">
          <div class="filter-item">
            <label>Municipio:
              <span class="contador-opciones">({{ municipiosDisponibles.length }} disponibles)</span>
            </label>
            <select v-model="filters.municipio" @change="handleFilter">
              <option value="">Todos los municipios</option>
              <option 
                v-for="municipio in municipiosDisponibles" 
                :key="municipio.cod_municipio" 
                :value="municipio.cod_municipio"
              >
                {{ municipio.nom_municipio }}
              </option>
            </select>
          </div>

          <div class="filter-actions">
            <button @click="clearAllFilters" class="clear-filters-btn">
              <i class="material-icons">filter_alt_off</i>
              Limpiar filtros
            </button>
            
            <button @click="refreshData" class="refresh-btn" :disabled="loading">
              <i class="material-icons">refresh</i>
              Actualizar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Estados de carga y errores -->
    <div v-if="loading" class="loading-indicator">
      <div class="spinner"></div>
      <span>Cargando datos...</span>
    </div>

    <div v-else-if="error" class="error-message">
      <i class="material-icons">error</i>
      <p>{{ error }}</p>
      <button @click="refreshData" class="btn-primary">Reintentar</button>
    </div>

    <!-- Barra de selección flotante -->
    <div v-if="selectedProfesionales.length > 0" class="selection-bar">
      <div class="selection-info">
        <i class="material-icons">check_circle</i>
        <span>{{ selectedProfesionales.length }} seleccionado(s)</span>
      </div>
      <div class="selection-actions">
        <button @click="clearSelection" class="btn-selection-clear">
          <i class="material-icons">clear_all</i>
          Deseleccionar
        </button>
        <button @click="selectAllVisible" class="btn-selection-all">
          <i class="material-icons">select_all</i>
          Seleccionar página
        </button>
        <button @click="generarReporteExcel" class="btn-selection-report" :disabled="generandoReporte">
          <i class="material-icons">{{ generandoReporte ? 'hourglass_empty' : 'file_download' }}</i>
          {{ generandoReporte ? 'Generando...' : 'Generar Reporte Excel' }}
        </button>
      </div>
    </div>

    <!-- Vista de profesionales filtrados -->
    <div v-if="!loading && !error" class="main-content">
      <div v-if="filteredProfesionales.length === 0" class="empty-state">
        <i class="material-icons">person_search</i>
        <p>No se encontraron profesionales con los criterios seleccionados.</p>
        <button @click="clearAllFilters" class="btn-secondary">Limpiar filtros</button>
      </div>

      <div v-else class="profesionales-grid">
        <div
          v-for="profesional in paginatedProfesionales"
          :key="profesional.cod_profesional"
          :class="['profesional-card', { 'selected': isSelected(profesional.cod_profesional) }]"
        >
          <div class="profesional-header">
            <label class="checkbox-container" @click.stop>
              <input
                type="checkbox"
                :checked="isSelected(profesional.cod_profesional)"
                @change="toggleSelection(profesional)"
              />
              <span class="checkmark"></span>
            </label>
            <div class="profesional-avatar">
              <i class="material-icons">person</i>
            </div>
            <div class="profesional-info">
              <h3>{{ profesional.nombre_profesional }}</h3>
              <span class="profesional-codigo">{{ profesional.cod_profesional }}</span>
            </div>
          </div>

          <div class="profesional-body">
            <div class="info-row">
              <span class="info-label">Email:</span>
              <span class="info-value">{{ profesional.correo_profesional || 'No registrado' }}</span>
            </div>
            
            <div class="info-row">
              <span class="info-label">Rol:</span>
              <span class="info-value">
                <span :class="['rol-badge', getRolClass(profesional.rol_profesional)]">
                  {{ profesional.rol_profesional }}
                </span>
              </span>
            </div>

            <div class="asignaciones-summary">
              <div class="asignacion-item">
                <i class="material-icons">location_city</i>
                <span>{{ getTerritoriales(profesional.cod_profesional).length }} Territoriales</span>
              </div>
              <div class="asignacion-item">
                <i class="material-icons">location_on</i>
                <span>{{ getMunicipios(profesional.cod_profesional).length }} Municipios</span>
              </div>
            </div>
          </div>

          <div class="profesional-footer">
            <button @click="editProfesional(profesional)" class="btn-icon primary">
              <i class="material-icons">edit</i>
            </button>
            <button @click="viewAsignaciones(profesional)" class="btn-icon info">
              <i class="material-icons">assignment</i>
            </button>
            <button @click="showDeleteModal(profesional)" class="btn-icon danger">
              <i class="material-icons">delete</i>
            </button>
          </div>
        </div>
      </div>

      <!-- Paginación -->
      <div class="pagination" v-if="filteredProfesionales.length > pageSize">
        <button 
          @click="prevPage" 
          :disabled="currentPage === 1" 
          class="pagination-button"
        >
          <i class="material-icons">chevron_left</i>
        </button>
        
        <span 
          v-for="page in displayedPages" 
          :key="page" 
          :class="['page-number', { active: currentPage === page }]"
          @click="goToPage(page)"
        >
          {{ page }}
        </span>
        
        <button 
          @click="nextPage" 
          :disabled="currentPage === totalPages" 
          class="pagination-button"
        >
          <i class="material-icons">chevron_right</i>
        </button>
      </div>
    </div>

    <!-- Modal para crear/editar profesional -->
    <div v-if="showModal" class="modal-backdrop" @click="closeModal">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h2>{{ modalMode === 'create' ? 'Nuevo Profesional' : 'Editar Profesional' }}</h2>
          <button class="close-btn" @click="closeModal">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveProfesional" class="form">
            <div class="form-row">
              <div class="form-group">
                <label for="cod_profesional">Código <span class="required">*</span></label>
                <input 
                  type="text" 
                  id="cod_profesional" 
                  v-model="form.cod_profesional" 
                  required
                  :readonly="modalMode === 'edit'"
                  placeholder="Código único del profesional"
                />
              </div>
              
              <div class="form-group">
                <label for="nombre_profesional">Nombre <span class="required">*</span></label>
                <input 
                  type="text" 
                  id="nombre_profesional" 
                  v-model="form.nombre_profesional" 
                  required
                  placeholder="Nombre completo"
                />
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="correo_profesional">Correo Electrónico</label>
                <input 
                  type="email" 
                  id="correo_profesional" 
                  v-model="form.correo_profesional"
                  placeholder="correo@ejemplo.com"
                />
              </div>
              
              <div class="form-group">
                <label for="rol_profesional">Rol <span class="required">*</span></label>
                <select 
                  id="rol_profesional" 
                  v-model="form.rol_profesional" 
                  required
                >
                  <option value="">Seleccione un rol</option>
                  <option 
                    v-for="rol in roles" 
                    :key="rol.rol_profesional" 
                    :value="rol.rol_profesional"
                  >
                    {{ rol.rol_profesional }}
                  </option>
                </select>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn-secondary" @click="closeModal">Cancelar</button>
              <button type="submit" class="btn-primary">
                {{ modalMode === 'create' ? 'Crear' : 'Actualizar' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Modal de confirmación de eliminación -->
    <div v-if="showDeleteConfirm" class="modal-backdrop" @click="closeDeleteModal">
      <div class="modal-container delete-modal" @click.stop>
        <div class="modal-header">
          <h2>Confirmar Eliminación</h2>
          <button class="close-btn" @click="closeDeleteModal">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="delete-warning">
            <i class="material-icons">warning</i>
            <p>¿Está seguro que desea eliminar a {{ profesionalToDelete?.nombre_profesional }}?</p>
            <p>Esta acción eliminará también todas las asignaciones a territoriales y municipios.</p>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeDeleteModal">Cancelar</button>
          <button class="btn-danger" @click="confirmDelete">Eliminar</button>
        </div>
      </div>
    </div>

    <!-- Notificación -->
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
import { defineComponent, ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/config'
import { API_URL } from '@/api/config'

export default defineComponent({
  name: 'ProfesionalesList',
  
  setup() {
    const router = useRouter()
    
    // Estado general
    const loading = ref(false)
    const error = ref<string | null>(null)
    
    // Datos
    const profesionales = ref<any[]>([])
    const roles = ref<any[]>([])
    const territoriales = ref<any[]>([])
    const departamentos = ref<any[]>([])
    const municipios = ref<any[]>([])
    const profesionalTerritorial = ref<any[]>([])
    const profesionalMunicipio = ref<any[]>([])
    
    // Filtros
    const searchTerm = ref('')
    const filters = ref({
      rol: '',
      territorial: '',
      departamento: '',
      municipio: ''
    })
    
    // Paginación
    const currentPage = ref(1)
    const pageSize = ref(12)
    
    // Modal
    const showModal = ref(false)
    const modalMode = ref<'create' | 'edit'>('create')
    const form = ref({
      cod_profesional: '',
      nombre_profesional: '',
      correo_profesional: '',
      rol_profesional: ''
    })
    
    // Delete modal
    const showDeleteConfirm = ref(false)
    const profesionalToDelete = ref<any>(null)

    // Selección múltiple para reportes
    const selectedProfesionales = ref<any[]>([])
    const generandoReporte = ref(false)

    // Notificación
    const notification = ref({
      show: false,
      message: '',
      type: 'success',
      icon: 'check_circle',
      timeout: null as number | null
    })
    
    // ========== SISTEMA DE FILTROS DINÁMICOS ACUMULATIVOS ==========
    
    /**
     * PROFESIONALES FILTRADOS ACUMULATIVAMENTE
     */
    const profesionalesFiltradosAcumulativos = computed(() => {
      let resultado = [...profesionales.value]
      
      // Aplicar búsqueda por texto
      if (searchTerm.value.trim()) {
        const search = searchTerm.value.toLowerCase()
        resultado = resultado.filter(p => 
          p.nombre_profesional.toLowerCase().includes(search) ||
          p.cod_profesional.toLowerCase().includes(search) ||
          (p.correo_profesional && p.correo_profesional.toLowerCase().includes(search))
        )
      }
      
      // Aplicar filtro por rol
      if (filters.value.rol) {
        resultado = resultado.filter(p => p.rol_profesional === filters.value.rol)
      }
      
      // Aplicar filtro por territorial
      if (filters.value.territorial) {
        const profesionalesIds = profesionalTerritorial.value
          .filter(pt => pt.territorial_seguimiento === filters.value.territorial)
          .map(pt => pt.cod_profesional)
        resultado = resultado.filter(p => profesionalesIds.includes(p.cod_profesional))
      }
      
      // Aplicar filtro por departamento
      if (filters.value.departamento) {
        // Obtener municipios del departamento
        const municipiosDelDepto = municipios.value
          .filter(m => m.cod_depto.toString() === filters.value.departamento.toString())
          .map(m => m.cod_municipio)
        
        // Obtener profesionales asignados a esos municipios
        const profesionalesIds = profesionalMunicipio.value
          .filter(pm => municipiosDelDepto.includes(pm.cod_municipio))
          .map(pm => pm.cod_profesional)
        
        resultado = resultado.filter(p => profesionalesIds.includes(p.cod_profesional))
      }
      
      // Aplicar filtro por municipio específico
      if (filters.value.municipio) {
        const profesionalesIds = profesionalMunicipio.value
          .filter(pm => pm.cod_municipio.toString() === filters.value.municipio.toString())
          .map(pm => pm.cod_profesional)
        resultado = resultado.filter(p => profesionalesIds.includes(p.cod_profesional))
      }
      
      return resultado
    })

    /**
     * OPCIONES DISPONIBLES PARA CADA FILTRO BASADAS EN PROFESIONALES FILTRADOS ACTUALES
     */
    const rolesDisponibles = computed(() => {
      const rolesUsados = new Set(
        profesionalesFiltradosAcumulativos.value
          .map(p => p.rol_profesional)
          .filter(r => r && r.trim() !== '')
      )
      
      return roles.value
        .filter(r => rolesUsados.has(r.rol_profesional))
        .sort((a, b) => a.rol_profesional.localeCompare(b.rol_profesional))
    })

    const territorialesDisponibles = computed(() => {
      // Obtener IDs de profesionales filtrados
      const profesionalesIds = profesionalesFiltradosAcumulativos.value.map(p => p.cod_profesional)
      
      // Obtener territoriales asignadas a estos profesionales
      const territorialesUsadas = new Set(
        profesionalTerritorial.value
          .filter(pt => profesionalesIds.includes(pt.cod_profesional))
          .map(pt => pt.territorial_seguimiento)
          .filter(t => t && t.trim() !== '')
      )
      
      return territoriales.value
        .filter(t => territorialesUsadas.has(t.nom_territorial))
        .sort((a, b) => a.nom_territorial.localeCompare(b.nom_territorial))
    })

    const departamentosDisponibles = computed(() => {
      // Obtener IDs de profesionales filtrados
      const profesionalesIds = profesionalesFiltradosAcumulativos.value.map(p => p.cod_profesional)
      
      // Obtener municipios asignados a estos profesionales
      const municipiosAsignados = profesionalMunicipio.value
        .filter(pm => profesionalesIds.includes(pm.cod_profesional))
        .map(pm => pm.cod_municipio)
      
      // Obtener departamentos de esos municipios
      const deptosUsados = new Set(
        municipios.value
          .filter(m => municipiosAsignados.includes(m.cod_municipio))
          .map(m => {
            if (typeof m.cod_depto === 'object' && m.cod_depto !== null) {
              return m.cod_depto.cod_depto || m.cod_depto
            }
            return m.cod_depto
          })
          .filter(d => d)
      )
      
      return departamentos.value
        .filter(d => deptosUsados.has(d.cod_depto))
        .sort((a, b) => a.nom_depto.localeCompare(b.nom_depto))
    })

    const municipiosDisponibles = computed(() => {
      // Obtener IDs de profesionales filtrados
      const profesionalesIds = profesionalesFiltradosAcumulativos.value.map(p => p.cod_profesional)
      
      // Obtener municipios asignados a estos profesionales
      const municipiosAsignados = profesionalMunicipio.value
        .filter(pm => profesionalesIds.includes(pm.cod_profesional))
        .map(pm => pm.cod_municipio)
      
      let municipiosDisponiblesArray = municipios.value
        .filter(m => municipiosAsignados.includes(m.cod_municipio))
      
      // Si hay filtro de departamento, aplicarlo también
      if (filters.value.departamento) {
        municipiosDisponiblesArray = municipiosDisponiblesArray.filter(m => {
          const codDepto = typeof m.cod_depto === 'object' && m.cod_depto !== null 
            ? (m.cod_depto.cod_depto || m.cod_depto)
            : m.cod_depto
          return codDepto.toString() === filters.value.departamento.toString()
        })
      }
      
      return municipiosDisponiblesArray.sort((a, b) => a.nom_municipio.localeCompare(b.nom_municipio))
    })
    
    // ========== COMPUTED FINALES ==========
    
    const filteredProfesionales = computed(() => {
      return profesionalesFiltradosAcumulativos.value
    })
    
    // Cargar datos iniciales
    onMounted(async () => {
      await loadInitialData()
    })
    
    // Métodos de carga de datos
    const loadInitialData = async () => {
      try {
        loading.value = true
        error.value = null
        
        // Cargar todos los datos necesarios
        const [
          profesionalesData,
          rolesData,
          territorialesData,
          departamentosData,
          municipiosData,
          profesionalTerritorialData,
          profesionalMunicipioData
        ] = await Promise.all([
          api.get('/preoperacion/profesionales-seguimiento/'),
          api.get('/preoperacion/roles-seguimiento/'),
          api.get('/preoperacion/territoriales/'),
          api.get('/preoperacion/departamentos/'),
          api.get('/preoperacion/municipios/'),
          api.get('/preoperacion/profesional-territorial/'),
          api.get('/preoperacion/profesional-municipio/')
        ])
        
        // Asignar datos
        profesionales.value = procesarDatos(profesionalesData)
        roles.value = procesarDatos(rolesData)
        territoriales.value = procesarDatos(territorialesData)
        departamentos.value = procesarDatos(departamentosData)
        municipios.value = procesarDatos(municipiosData)
        profesionalTerritorial.value = procesarDatos(profesionalTerritorialData)
        profesionalMunicipio.value = procesarDatos(profesionalMunicipioData)
        
        console.log('✅ Datos cargados:', {
          profesionales: profesionales.value.length,
          roles: roles.value.length,
          territoriales: territoriales.value.length,
          departamentos: departamentos.value.length,
          municipios: municipios.value.length,
          profesionalTerritorial: profesionalTerritorial.value.length,
          profesionalMunicipio: profesionalMunicipio.value.length
        })
        
      } catch (err: any) {
        console.error('Error cargando datos:', err)
        error.value = 'Error cargando datos. Por favor, intente nuevamente.'
      } finally {
        loading.value = false
      }
    }
    
    // Proceso de datos para manejar respuestas paginadas y no paginadas
    const procesarDatos = (response: any) => {
      if (response && response.results && Array.isArray(response.results)) {
        return response.results
      }
      return Array.isArray(response) ? response : []
    }
    
    // Paginación
    const totalPages = computed(() => {
      return Math.ceil(filteredProfesionales.value.length / pageSize.value)
    })
    
    const paginatedProfesionales = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredProfesionales.value.slice(start, end)
    })
    
    const displayedPages = computed(() => {
      if (totalPages.value <= 5) {
        return Array.from({ length: totalPages.value }, (_, i) => i + 1)
      }
      
      const pages = []
      if (currentPage.value <= 3) {
        for (let i = 1; i <= 5; i++) {
          pages.push(i)
        }
      } else if (currentPage.value >= totalPages.value - 2) {
        for (let i = totalPages.value - 4; i <= totalPages.value; i++) {
          pages.push(i)
        }
      } else {
        for (let i = currentPage.value - 2; i <= currentPage.value + 2; i++) {
          pages.push(i)
        }
      }
      
      return pages
    })
    
    // Métodos de navegación
    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
      }
    }
    
    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
      }
    }
    
    const goToPage = (page: number) => {
      currentPage.value = page
    }
    
    // Métodos de filtrado SIMPLIFICADOS (ahora solo reinician página)
    const handleSearchInput = () => {
      currentPage.value = 1
    }
    
    const clearSearch = () => {
      searchTerm.value = ''
      currentPage.value = 1
    }
    
    const handleFilter = () => {
      currentPage.value = 1
    }
    
    const handleDepartamentoChange = () => {
      // Ya no necesitamos limpiar municipio manualmente, el sistema dinámico se encarga
      currentPage.value = 1
    }
    
    const handleTerritorialChange = () => {
      currentPage.value = 1
    }
    
    const clearAllFilters = () => {
      searchTerm.value = ''
      filters.value = {
        rol: '',
        territorial: '',
        departamento: '',
        municipio: ''
      }
      currentPage.value = 1
    }
    
    // Métodos de modal
    const showCreateModal = () => {
      modalMode.value = 'create'
      form.value = {
        cod_profesional: '',
        nombre_profesional: '',
        correo_profesional: '',
        rol_profesional: ''
      }
      showModal.value = true
    }
    
    const editProfesional = (profesional: any) => {
      modalMode.value = 'edit'
      form.value = {
        cod_profesional: profesional.cod_profesional,
        nombre_profesional: profesional.nombre_profesional,
        correo_profesional: profesional.correo_profesional || '',
        rol_profesional: profesional.rol_profesional
      }
      showModal.value = true
    }
    
    const closeModal = () => {
      showModal.value = false
    }
    
    const saveProfesional = async () => {
      try {
        loading.value = true
        
        if (modalMode.value === 'create') {
          await api.post('/preoperacion/profesionales-seguimiento/', form.value)
          showNotification('Profesional creado correctamente', 'success')
        } else {
          await api.put(`/preoperacion/profesionales-seguimiento/${form.value.cod_profesional}/`, form.value)
          showNotification('Profesional actualizado correctamente', 'success')
        }
        
        await loadInitialData()
        closeModal()
      } catch (err: any) {
        console.error('Error guardando profesional:', err)
        showNotification('Error al guardar profesional', 'error')
      } finally {
        loading.value = false
      }
    }
    
    // Métodos de eliminación
    const showDeleteModal = (profesional: any) => {
      profesionalToDelete.value = profesional
      showDeleteConfirm.value = true
    }
    
    const closeDeleteModal = () => {
      showDeleteConfirm.value = false
      profesionalToDelete.value = null
    }
    
    const confirmDelete = async () => {
      if (!profesionalToDelete.value) return
      
      try {
        loading.value = true
        await api.delete(`/preoperacion/profesionales-seguimiento/${profesionalToDelete.value.cod_profesional}/`)
        showNotification('Profesional eliminado correctamente', 'success')
        await loadInitialData()
        closeDeleteModal()
      } catch (err: any) {
        console.error('Error eliminando profesional:', err)
        showNotification('Error al eliminar profesional', 'error')
      } finally {
        loading.value = false
      }
    }
    
    // Métodos auxiliares
    const getTerritoriales = (codProfesional: string) => {
      return profesionalTerritorial.value.filter(pt => pt.cod_profesional === codProfesional)
    }
    
    const getMunicipios = (codProfesional: string) => {
      return profesionalMunicipio.value.filter(pm => pm.cod_profesional === codProfesional)
    }
    
    const getRolClass = (rol: string) => {
      const rolUpper = rol.toUpperCase()
      if (rolUpper.includes('L.A.S')) return 'las'
      if (rolUpper.includes('P.A.S')) return 'pas'
      return 'default'
    }
    
    const viewAsignaciones = (profesional: any) => {
      router.push({
        path: '/gestion-informacion/profesionales/asignaciones',
        query: { profesional: profesional.cod_profesional }
      })
    }
    
    const goToAsignaciones = () => {
      router.push('/gestion-informacion/profesionales/asignaciones')
    }

    const goToAsignacionesMasivas = () => {
      router.push('/gestion-informacion/profesionales/asignaciones-masivas')
    }
    
    // Notificaciones
    const showNotification = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
      if (notification.value.timeout) {
        clearTimeout(notification.value.timeout)
      }
      
      let icon = 'info'
      switch (type) {
        case 'success':
          icon = 'check_circle'
          break
        case 'error':
          icon = 'error'
          break
        case 'warning':
          icon = 'warning'
          break
      }
      
      notification.value = {
        show: true,
        message,
        type,
        icon,
        timeout: setTimeout(() => {
          notification.value.show = false
        }, 5000) as unknown as number
      }
    }
    
    const closeNotification = () => {
      if (notification.value.timeout) {
        clearTimeout(notification.value.timeout)
      }
      notification.value.show = false
    }
    
    const refreshData = () => {
      loadInitialData()
    }

    // ========== FUNCIONES DE SELECCIÓN MÚLTIPLE ==========

    const isSelected = (codProfesional: string) => {
      return selectedProfesionales.value.some(p => p.cod_profesional === codProfesional)
    }

    const toggleSelection = (profesional: any) => {
      const index = selectedProfesionales.value.findIndex(p => p.cod_profesional === profesional.cod_profesional)
      if (index === -1) {
        selectedProfesionales.value.push(profesional)
      } else {
        selectedProfesionales.value.splice(index, 1)
      }
    }

    const clearSelection = () => {
      selectedProfesionales.value = []
    }

    const selectAllVisible = () => {
      // Agregar todos los de la página actual que no estén ya seleccionados
      paginatedProfesionales.value.forEach((profesional: any) => {
        if (!isSelected(profesional.cod_profesional)) {
          selectedProfesionales.value.push(profesional)
        }
      })
    }

    const generarReporteExcel = async () => {
      if (selectedProfesionales.value.length === 0) {
        showNotification('Seleccione al menos un registro para generar el reporte', 'warning')
        return
      }

      try {
        generandoReporte.value = true

        const codigos = selectedProfesionales.value.map(p => p.cod_profesional)

        // Obtener token para la petición
        const token = localStorage.getItem('token')

        const response = await fetch(`${API_URL}/preoperacion/reportes/asignaciones-profesionales/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${token}`
          },
          body: JSON.stringify({ profesionales: codigos })
        })

        if (!response.ok) {
          throw new Error('Error al generar el reporte')
        }

        // Obtener el blob del archivo
        const blob = await response.blob()

        // Obtener nombre del archivo desde headers o usar uno por defecto
        const contentDisposition = response.headers.get('Content-Disposition')
        let filename = 'Reporte_Asignaciones.xlsx'
        if (contentDisposition) {
          const match = contentDisposition.match(/filename="?([^"]+)"?/)
          if (match) {
            filename = match[1]
          }
        }

        // Crear link de descarga
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

        showNotification(`Reporte generado: ${selectedProfesionales.value.length} registro(s)`, 'success')

      } catch (err: any) {
        console.error('Error generando reporte:', err)
        showNotification('Error al generar el reporte', 'error')
      } finally {
        generandoReporte.value = false
      }
    }

    return {
      // Estado
      loading,
      error,
      searchTerm,
      filters,
      currentPage,
      pageSize,
      showModal,
      modalMode,
      form,
      showDeleteConfirm,
      profesionalToDelete,
      notification,
      selectedProfesionales,
      generandoReporte,

      // Datos originales
      profesionales,
      roles,
      territoriales,
      departamentos,
      municipios,
      
      // Datos dinámicos
      rolesDisponibles,
      territorialesDisponibles,
      departamentosDisponibles,
      municipiosDisponibles,
      filteredProfesionales,
      paginatedProfesionales,
      
      // Paginación
      totalPages,
      displayedPages,
      prevPage,
      nextPage,
      goToPage,
      
      // Métodos
      handleSearchInput,
      clearSearch,
      handleFilter,
      handleDepartamentoChange,
      handleTerritorialChange,
      clearAllFilters,
      showCreateModal,
      editProfesional,
      closeModal,
      saveProfesional,
      showDeleteModal,
      closeDeleteModal,
      confirmDelete,
      getTerritoriales,
      getMunicipios,
      getRolClass,
      viewAsignaciones,
      goToAsignaciones,
      goToAsignacionesMasivas,
      showNotification,
      closeNotification,
      refreshData,
      isSelected,
      toggleSelection,
      clearSelection,
      selectAllVisible,
      generarReporteExcel,
    }
  }
})
</script>

<style scoped>
.profesionales-list-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  background-color: white;
  border-radius: 8px;
  padding: 1.25rem 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  margin: 0;
  font-size: 1.75rem;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

/* Barra de selección flotante */
.selection-bar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #1F4E79, #2E6DA4);
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(31, 78, 121, 0.3);
  color: white;
  margin-bottom: 1rem;
}

.selection-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
  font-size: 1rem;
}

.selection-info i {
  font-size: 1.5rem;
}

.selection-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-selection-clear,
.btn-selection-all,
.btn-selection-report {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-selection-clear {
  background-color: rgba(255, 255, 255, 0.15);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-selection-clear:hover {
  background-color: rgba(255, 255, 255, 0.25);
}

.btn-selection-all {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.btn-selection-all:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.btn-selection-report {
  background-color: #28a745;
  color: white;
}

.btn-selection-report:hover:not(:disabled) {
  background-color: #218838;
}

.btn-selection-report:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Checkbox en tarjetas */
.checkbox-container {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  cursor: pointer;
  user-select: none;
  margin-right: 0.5rem;
}

.checkbox-container input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark {
  height: 22px;
  width: 22px;
  background-color: #f8f9fa;
  border: 2px solid #ced4da;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.checkbox-container:hover input ~ .checkmark {
  border-color: #0d6efd;
}

.checkbox-container input:checked ~ .checkmark {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.checkmark:after {
  content: "";
  position: absolute;
  display: none;
}

.checkbox-container input:checked ~ .checkmark:after {
  display: block;
}

.checkbox-container .checkmark:after {
  left: 8px;
  top: 4px;
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

/* Tarjeta seleccionada */
.profesional-card.selected {
  border: 2px solid #0d6efd;
  box-shadow: 0 4px 15px rgba(13, 110, 253, 0.2);
}

.profesional-card.selected .profesional-header {
  background-color: #e7f1ff;
}

.filters-panel {
  background-color: white;
  border-radius: 8px;
  padding: 1.25rem 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.search-filters-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.global-search {
  position: relative;
}

.global-search i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

.global-search input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
}

.global-search input:focus {
  border-color: #4dabf7;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
  outline: none;
}

.clear-btn {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.filters-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 200px;
  flex: 1;
}

.filter-item label {
  font-size: 0.875rem;
  color: #495057;
  font-weight: 500;
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

.filter-item select {
  padding: 0.5rem 1rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background-color: white;
  font-size: 0.95rem;
}

.filter-actions {
 display: flex;
 gap: 0.75rem;
 margin-left: auto;
}

.clear-filters-btn,
.refresh-btn {
 display: flex;
 align-items: center;
 gap: 0.5rem;
 padding: 0.5rem 1rem;
 border-radius: 4px;
 border: none;
 font-size: 0.95rem;
 cursor: pointer;
 transition: background-color 0.2s;
}

.clear-filters-btn {
 background-color: #f8f9fa;
 color: #6c757d;
 border: 1px solid #ced4da;
}

.clear-filters-btn:hover {
 background-color: #e9ecef;
}

.refresh-btn {
 background-color: #6c757d;
 color: white;
}

.refresh-btn:hover {
 background-color: #5a6268;
}

.refresh-btn:disabled {
 opacity: 0.6;
 cursor: not-allowed;
}

/* Estados de carga y error */
.loading-indicator,
.error-message,
.empty-state {
 display: flex;
 flex-direction: column;
 align-items: center;
 justify-content: center;
 padding: 3rem;
 text-align: center;
 background-color: white;
 border-radius: 8px;
 box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.spinner {
 width: 40px;
 height: 40px;
 border: 4px solid #f3f3f3;
 border-top: 4px solid #0d6efd;
 border-radius: 50%;
 animation: spin 1s linear infinite;
 margin-bottom: 1rem;
}

@keyframes spin {
 0% { transform: rotate(0deg); }
 100% { transform: rotate(360deg); }
}

.error-message i,
.empty-state i {
 font-size: 3rem;
 margin-bottom: 1rem;
}

.error-message i {
 color: #dc3545;
}

.empty-state i {
 color: #6c757d;
}

.error-message p,
.empty-state p {
 margin-bottom: 1.5rem;
 font-size: 1.1rem;
 color: #6c757d;
}

/* Contenido principal */
.main-content {
 display: flex;
 flex-direction: column;
 gap: 1.5rem;
}

.profesionales-grid {
 display: grid;
 grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
 gap: 1.5rem;
}

.profesional-card {
 background-color: white;
 border-radius: 8px;
 overflow: hidden;
 box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
 transition: transform 0.2s, box-shadow 0.2s;
 display: flex;
 flex-direction: column;
}

.profesional-card:hover {
 transform: translateY(-4px);
 box-shadow: 0 6px 15px rgba(0, 0, 0, 0.12);
}

.profesional-header {
 display: flex;
 align-items: center;
 padding: 1.25rem;
 background-color: #f8f9fa;
 border-bottom: 1px solid #dee2e6;
 gap: 1rem;
}

.profesional-avatar {
 width: 56px;
 height: 56px;
 background-color: #0d6efd;
 color: white;
 border-radius: 50%;
 display: flex;
 align-items: center;
 justify-content: center;
 font-size: 1.75rem;
}

.profesional-info {
 flex: 1;
}

.profesional-info h3 {
 margin: 0 0 0.25rem;
 font-size: 1.25rem;
 color: #343a40;
}

.profesional-codigo {
 font-size: 0.875rem;
 color: #6c757d;
}

.profesional-body {
 padding: 1.25rem;
 flex: 1;
 display: flex;
 flex-direction: column;
 gap: 0.75rem;
}

.info-row {
 display: flex;
 align-items: baseline;
 gap: 0.5rem;
}

.info-label {
 font-size: 0.875rem;
 color: #6c757d;
 font-weight: 500;
 min-width: 60px;
}

.info-value {
 flex: 1;
 font-size: 0.95rem;
 color: #212529;
}

.rol-badge {
 display: inline-block;
 padding: 0.25rem 0.5rem;
 font-size: 0.75rem;
 border-radius: 4px;
 font-weight: 600;
}

.rol-badge.las {
 background-color: #e3f2fd;
 color: #0d47a1;
}

.rol-badge.pas {
 background-color: #e8f5e9;
 color: #1b5e20;
}

.rol-badge.default {
 background-color: #f0f0f0;
 color: #495057;
}

.asignaciones-summary {
 display: flex;
 gap: 1rem;
 margin-top: 0.5rem;
 padding-top: 0.75rem;
 border-top: 1px solid #dee2e6;
}

.asignacion-item {
 display: flex;
 align-items: center;
 gap: 0.5rem;
 font-size: 0.875rem;
 color: #6c757d;
}

.asignacion-item i {
 font-size: 1.1rem;
}

.profesional-footer {
 display: flex;
 justify-content: flex-end;
 gap: 0.5rem;
 padding: 0.75rem 1.25rem;
 background-color: #f8f9fa;
 border-top: 1px solid #dee2e6;
}

/* Paginación */
.pagination {
 display: flex;
 justify-content: center;
 align-items: center;
 padding: 1rem;
 background-color: white;
 border-radius: 8px;
 box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
 gap: 0.5rem;
}

.pagination-button {
 display: flex;
 align-items: center;
 justify-content: center;
 width: 36px;
 height: 36px;
 border: 1px solid #dee2e6;
 background-color: white;
 color: #0d6efd;
 border-radius: 4px;
 cursor: pointer;
 transition: background-color 0.2s;
}

.pagination-button:hover:not(:disabled) {
 background-color: #e9ecef;
}

.pagination-button:disabled {
 color: #6c757d;
 cursor: not-allowed;
 opacity: 0.5;
}

.page-number {
 display: flex;
 align-items: center;
 justify-content: center;
 width: 36px;
 height: 36px;
 border: 1px solid #dee2e6;
 background-color: white;
 color: #495057;
 border-radius: 4px;
 cursor: pointer;
 transition: background-color 0.2s;
}

.page-number:hover {
 background-color: #e9ecef;
}

.page-number.active {
 background-color: #0d6efd;
 color: white;
 border-color: #0d6efd;
 font-weight: 600;
}

/* Modal */
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
 box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
 width: 100%;
 max-width: 600px;
 max-height: 90vh;
 display: flex;
 flex-direction: column;
}

.delete-modal {
 max-width: 500px;
}

.modal-header {
 display: flex;
 justify-content: space-between;
 align-items: center;
 padding: 1rem 1.5rem;
 border-bottom: 1px solid #dee2e6;
}

.modal-header h2 {
 margin: 0;
 font-size: 1.25rem;
 color: #343a40;
}

.close-btn {
 background: none;
 border: none;
 color: #6c757d;
 cursor: pointer;
 font-size: 1.5rem;
 display: flex;
 align-items: center;
 justify-content: center;
}

.modal-body {
 padding: 1.5rem;
 overflow-y: auto;
 max-height: calc(90vh - 132px);
}

.form {
 display: flex;
 flex-direction: column;
 gap: 1.5rem;
}

.form-row {
 display: flex;
 gap: 1rem;
 flex-wrap: wrap;
}

.form-group {
 flex: 1;
 min-width: 250px;
 display: flex;
 flex-direction: column;
 gap: 0.25rem;
}

.form-group label {
 font-size: 0.95rem;
 color: #495057;
 font-weight: 500;
}

.form-group .required {
 color: #dc3545;
}

.form-group input,
.form-group select {
 padding: 0.5rem 0.75rem;
 border: 1px solid #ced4da;
 border-radius: 4px;
 font-size: 0.95rem;
}

.form-group input:focus,
.form-group select:focus {
 border-color: #4dabf7;
 box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
 outline: none;
}

.form-actions {
 display: flex;
 justify-content: flex-end;
 gap: 1rem;
 margin-top: 1rem;
}

.modal-footer {
 padding: 1rem 1.5rem;
 border-top: 1px solid #dee2e6;
 display: flex;
 justify-content: flex-end;
 gap: 1rem;
}

.delete-warning {
 display: flex;
 flex-direction: column;
 align-items: center;
 text-align: center;
}

.delete-warning i {
 font-size: 3rem;
 color: #ffc107;
 margin-bottom: 1rem;
}

.delete-warning p {
 margin-bottom: 0.5rem;
 color: #495057;
}

/* Botones */
.btn-primary,
.btn-secondary,
.btn-outline,
.btn-danger,
.btn-accent {
 display: flex;
 align-items: center;
 gap: 0.5rem;
 padding: 0.5rem 1rem;
 border-radius: 4px;
 border: none;
 font-size: 0.95rem;
 font-weight: 500;
 cursor: pointer;
 transition: background-color 0.2s, transform 0.1s;
}

.btn-primary {
 background-color: #0d6efd;
 color: white;
}

.btn-primary:hover {
 background-color: #0b5ed7;
}

.btn-secondary {
 background-color: #6c757d;
 color: white;
}

.btn-secondary:hover {
 background-color: #5a6268;
}

.btn-outline {
 background-color: transparent;
 border: 1px solid #ced4da;
 color: #495057;
}

.btn-outline:hover {
 background-color: #f8f9fa;
}

.btn-danger {
 background-color: #dc3545;
 color: white;
}

.btn-danger:hover {
 background-color: #bb2d3b;
}

.btn-accent {
 background-color: #6f42c1;
 color: white;
}

.btn-accent:hover {
 background-color: #5a32a3;
}

.btn-icon {
 display: flex;
 align-items: center;
 justify-content: center;
 width: 36px;
 height: 36px;
 border-radius: 4px;
 border: none;
 background-color: #f8f9fa;
 color: #495057;
 cursor: pointer;
 transition: background-color 0.2s;
}

.btn-icon:hover {
 background-color: #e9ecef;
}

.btn-icon.primary {
 background-color: rgba(13, 110, 253, 0.1);
 color: #0d6efd;
}

.btn-icon.primary:hover {
 background-color: rgba(13, 110, 253, 0.2);
}

.btn-icon.info {
 background-color: rgba(13, 202, 240, 0.1);
 color: #0dcaf0;
}

.btn-icon.info:hover {
 background-color: rgba(13, 202, 240, 0.2);
}

.btn-icon.danger {
 background-color: rgba(220, 53, 69, 0.1);
 color: #dc3545;
}

.btn-icon.danger:hover {
 background-color: rgba(220, 53, 69, 0.2);
}

/* Notificaciones */
.notification {
 position: fixed;
 bottom: 1.5rem;
 right: 1.5rem;
 min-width: 300px;
 max-width: 400px;
 background-color: white;
 border-radius: 8px;
 box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
 z-index: 1100;
 overflow: hidden;
 display: flex;
 align-items: center;
 justify-content: space-between;
 animation: slide-up 0.3s ease;
}

@keyframes slide-up {
 from {
   transform: translateY(100%);
   opacity: 0;
 }
 to {
   transform: translateY(0);
   opacity: 1;
 }
}

.notification-content {
 display: flex;
 align-items: center;
 gap: 0.75rem;
 padding: 1rem 1.5rem;
 flex: 1;
}

.notification-content i {
 font-size: 1.5rem;
}

.notification-close {
 background: none;
 border: none;
 color: #6c757d;
 cursor: pointer;
 padding: 0.5rem;
 display: flex;
 align-items: center;
 justify-content: center;
}

.notification.success {
 border-left: 4px solid #198754;
}

.notification.success i {
 color: #198754;
}

.notification.error {
 border-left: 4px solid #dc3545;
}

.notification.error i {
 color: #dc3545;
}

.notification.warning {
 border-left: 4px solid #ffc107;
}

.notification.warning i {
 color: #ffc107;
}

.notification.info {
 border-left: 4px solid #0dcaf0;
}

.notification.info i {
 color: #0dcaf0;
}

/* Responsive */
@media (max-width: 992px) {
 .header-content {
   flex-direction: column;
   align-items: flex-start;
   gap: 1rem;
 }
 
 .header-actions {
   width: 100%;
   justify-content: flex-end;
 }
 
 .filters-row {
   flex-direction: column;
 }
 
 .filter-item {
   width: 100%;
 }
 
 .profesionales-grid {
   grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
 }
}

@media (max-width: 768px) {
 .profesionales-grid {
   grid-template-columns: 1fr;
 }
 
 .form-row {
   flex-direction: column;
 }
 
 .form-group {
   min-width: 100%;
 }
 
 .asignaciones-summary {
   flex-direction: column;
   gap: 0.5rem;
 }
 
 .notification {
   min-width: auto;
   max-width: 90%;
   left: 5%;
   right: 5%;
 }
}

@media (max-width: 576px) {
 .btn-primary,
 .btn-secondary,
 .btn-outline {
   padding: 0.5rem 0.75rem;
   font-size: 0.9rem;
 }
 
 .modal-container {
   max-width: 95%;
   margin: 0 2.5%;
 }
}
</style>