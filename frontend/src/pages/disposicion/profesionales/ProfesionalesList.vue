<template>
  <div class="profesionales-disposicion-container">
    <div class="header-section">
      <h2 class="page-title">Consulta de Profesionales</h2>
      <div class="info-section">
        <div class="access-info-header">
          <div class="access-badge" :class="accessLevelClass">
            <i class="material-icons">{{ accessLevelIcon }}</i>
            <span>{{ accessLevelText }}</span>
          </div>
        </div>
        <div class="actions-bar">
          <button 
            class="btn btn-export" 
            @click="exportarDatos" 
            :disabled="!profesionalesFiltrados.length"
          >
            <i class="material-icons">file_download</i>
            Exportar Resultados
          </button>
          <button 
            class="btn btn-refresh" 
            @click="cargarProfesionales"
            :disabled="cargando"
          >
            <i class="material-icons">refresh</i>
            Actualizar
          </button>
        </div>
      </div>
    </div>

    <!-- Filtros DINÁMICOS mejorados -->
    <div class="filtros-section">
      <!-- Búsqueda global -->
      <div class="search-row">
        <div class="global-search">
          <i class="material-icons">search</i>
          <input 
            type="text"
            v-model="filtros.busqueda"
            placeholder="Buscar por nombre, código o correo..."
            @input="debounceSearch"
          />
          <button v-if="filtros.busqueda" @click="limpiarBusqueda" class="clear-btn">
            <i class="material-icons">close</i>
          </button>
        </div>
      </div>

      <!-- Filtros principales DINÁMICOS -->
      <div class="row">
        <div class="col-md-6 col-lg-3">
          <div class="form-group">
            <label for="rol">
              Rol del Profesional:
              <span class="contador-opciones">({{ rolesDisponibles.length }} disponibles)</span>
            </label>
            <select 
              id="rol" 
              v-model="filtros.rol" 
              @change="aplicarFiltros"
              class="form-control"
              :class="{ 'has-selection': filtros.rol }"
            >
              <option value="">Todos los roles</option>
              <option 
                v-for="rol in rolesDisponibles" 
                :key="rol" 
                :value="rol"
              >
                {{ rol }}
              </option>
            </select>
            <button 
              v-if="filtros.rol" 
              @click="limpiarFiltroEspecifico('rol')"
              class="btn-limpiar-filtro"
              title="Limpiar filtro de rol"
            >
              ✓
            </button>
          </div>
        </div>
        
        <div class="col-md-6 col-lg-3">
          <div class="form-group">
            <label for="territorial">
              Territorial:
              <span class="contador-opciones">({{ territorialesDisponibles.length }} disponibles)</span>
            </label>
            <select 
              id="territorial" 
              v-model="filtros.territorial" 
              @change="aplicarFiltros"
              class="form-control"
              :class="{ 'has-selection': filtros.territorial }"
            >
              <option value="">Todas las territoriales</option>
              <option 
                v-for="territorial in territorialesDisponibles" 
                :key="territorial" 
                :value="territorial"
              >
                {{ territorial }}
              </option>
            </select>
            <button 
              v-if="filtros.territorial" 
              @click="limpiarFiltroEspecifico('territorial')"
              class="btn-limpiar-filtro"
              title="Limpiar filtro de territorial"
            >
              ✓
            </button>
          </div>
        </div>

        <div class="col-md-6 col-lg-3">
          <div class="form-group">
            <label for="departamento">
              Departamento:
              <span class="contador-opciones">({{ departamentosDisponibles.length }} disponibles)</span>
            </label>
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
              @click="limpiarFiltroEspecifico('departamento')"
              class="btn-limpiar-filtro"
              title="Limpiar filtro de departamento"
            >
              ✓
            </button>
          </div>
        </div>

        <div class="col-md-6 col-lg-3">
          <div class="form-group">
            <label for="municipio">
              Municipio:
              <span class="contador-opciones">({{ municipiosDisponibles.length }} disponibles)</span>
            </label>
            <select 
              id="municipio" 
              v-model="filtros.municipio" 
              @change="aplicarFiltros"
              class="form-control"
              :class="{ 'has-selection': filtros.municipio }"
            >
              <option value="">Todos los municipios</option>
              <option 
                v-for="municipio in municipiosDisponibles" 
                :key="municipio.cod_municipio" 
                :value="municipio.cod_municipio"
              >
                {{ municipio.nom_municipio }}
              </option>
            </select>
            <button 
              v-if="filtros.municipio" 
              @click="limpiarFiltroEspecifico('municipio')"
              class="btn-limpiar-filtro"
              title="Limpiar filtro de municipio"
            >
              ✓
            </button>
          </div>
        </div>
      </div>

      <!-- Indicadores de filtros activos -->
      <div class="filtros-activos" v-if="hayFiltrosActivos">
        <h4>🔍 Filtros activos:</h4>
        <div class="tags-filtros">
          <span v-if="filtros.rol" class="tag-filtro rol">
            Rol: {{ filtros.rol }}
            <button @click="limpiarFiltroEspecifico('rol')">×</button>
          </span>
          <span v-if="filtros.territorial" class="tag-filtro territorial">
            Territorial: {{ filtros.territorial }}
            <button @click="limpiarFiltroEspecifico('territorial')">×</button>
          </span>
          <span v-if="filtros.departamento" class="tag-filtro departamento">
            Departamento: {{ getNombreDepartamento(filtros.departamento) }}
            <button @click="limpiarFiltroEspecifico('departamento')">×</button>
          </span>
          <span v-if="filtros.municipio" class="tag-filtro municipio">
            Municipio: {{ getNombreMunicipio(filtros.municipio) }}
            <button @click="limpiarFiltroEspecifico('municipio')">×</button>
          </span>
        </div>
      </div>

      <div class="filtros-buttons">
        <button class="btn btn-primary" @click="aplicarFiltros" :disabled="cargando">
          <i class="material-icons">filter_list</i>
          Aplicar Filtros
        </button>
        <button class="btn btn-secondary" @click="limpiarFiltros" :disabled="cargando">
          <i class="material-icons">clear_all</i>
          Limpiar Todo
        </button>
      </div>
    </div>

    <!-- Estados de carga -->
    <div v-if="cargando" class="loading-container">
      <div class="spinner"></div>
      <span class="loading-text">Cargando profesionales...</span>
    </div>

    <div v-else-if="error" class="error-container">
      <i class="material-icons">error</i>
      <span>{{ error }}</span>
      <button class="btn btn-primary" @click="cargarProfesionales">Reintentar</button>
    </div>

    <div v-else-if="profesionalesFiltrados.length === 0" class="empty-container">
      <i class="material-icons">info</i>
      <span>No se encontraron profesionales con los filtros seleccionados</span>
      <button class="btn btn-secondary" @click="limpiarFiltros">Limpiar filtros</button>
    </div>

    <!-- Grid de profesionales -->
    <div v-else class="results-container">
      <div class="results-header">
        <h3 class="results-title">Resultados</h3>
        <div class="results-summary">
          <span class="results-count">{{ profesionalesFiltrados.length }} profesionales encontrados</span>
          <span class="results-filter-info" v-if="hayFiltrosActivos">
            (filtrados de {{ profesionales.length }} totales)
          </span>
        </div>
      </div>

      <!-- Grid de tarjetas de profesionales -->
      <div class="profesionales-grid">
        <div 
          v-for="profesional in profesionalesVisibles" 
          :key="profesional.cod_profesional"
          class="profesional-card"
        >
          <!-- Header de la tarjeta -->
          <div class="profesional-header">
            <div class="profesional-avatar">
              <i class="material-icons">person</i>
            </div>
            <div class="profesional-info">
              <h3 class="profesional-nombre">{{ profesional.nombre_profesional }}</h3>
              <span class="profesional-codigo">{{ profesional.cod_profesional }}</span>
            </div>
          </div>

          <!-- Contenido de la tarjeta -->
          <div class="profesional-body">
            <div class="info-row">
              <span class="info-label">
                <i class="material-icons">email</i>
                Email:
              </span>
              <span class="info-value">{{ profesional.correo_profesional || 'No registrado' }}</span>
            </div>
            
            <div class="info-row">
              <span class="info-label">
                <i class="material-icons">work</i>
                Rol:
              </span>
              <span class="info-value">
                <span class="role-badge" :class="getRoleClass(profesional.rol_profesional)">
                  {{ profesional.rol_profesional }}
                </span>
              </span>
            </div>

            <!-- Asignaciones resumen -->
            <div class="asignaciones-summary">
              <div class="asignacion-item">
                <i class="material-icons">location_city</i>
                <span>{{ contarTerritoriales(profesional.cod_profesional) }} Territoriales</span>
              </div>
              <div class="asignacion-item">
                <i class="material-icons">location_on</i>
                <span>{{ contarMunicipios(profesional.cod_profesional) }} Municipios</span>
              </div>
            </div>
          </div>

          <!-- Footer con acciones -->
          <div class="profesional-footer">
            <button 
              @click="verDetalleProfesional(profesional)"
              class="action-btn view-btn"
              title="Ver detalles completos"
            >
              <i class="material-icons">visibility</i>
              Ver Detalles
            </button>
          </div>
        </div>
      </div>

      <!-- Paginación -->
      <div class="pagination-container" v-if="totalPaginas > 1">
        <button 
          class="btn-pagination" 
          @click="cambiarPagina(paginaActual - 1)" 
          :disabled="paginaActual === 1"
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
        >
          <i class="material-icons">navigate_next</i>
        </button>
      </div>
    </div>

    <!-- Modal de detalles -->
    <div class="modal" v-if="modalDetalle.mostrar">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">
              <i class="material-icons">person</i>
              Detalles del Profesional - {{ modalDetalle.profesional?.nombre_profesional }}
            </h4>
            <button class="close-button" @click="modalDetalle.mostrar = false">
              <i class="material-icons">close</i>
            </button>
          </div>
          <div class="modal-body">
            <div v-if="modalDetalle.profesional" class="profesional-detail-info">
              <!-- Información general -->
              <div class="detail-section">
                <h5><i class="material-icons">person</i> Información General</h5>
                <div class="detail-grid">
                  <div class="detail-item">
                    <span class="detail-label">Código:</span>
                    <span class="detail-value">{{ modalDetalle.profesional.cod_profesional }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Nombre:</span>
                    <span class="detail-value">{{ modalDetalle.profesional.nombre_profesional }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Correo:</span>
                    <span class="detail-value">{{ modalDetalle.profesional.correo_profesional || 'No registrado' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Rol:</span>
                    <span class="detail-value">
                      <span class="role-badge" :class="getRoleClass(modalDetalle.profesional.rol_profesional)">
                        {{ modalDetalle.profesional.rol_profesional }}
                      </span>
                    </span>
                  </div>
                </div>
              </div>

              <!-- Territoriales asignadas -->
              <div class="detail-section" v-if="modalDetalle.territoriales.length > 0">
                <h5><i class="material-icons">location_city</i> Territoriales Asignadas ({{ modalDetalle.territoriales.length }})</h5>
                <div class="asignaciones-chips">
                  <span 
                    v-for="territorial in modalDetalle.territoriales" 
                    :key="territorial.id"
                    class="territorial-chip"
                  >
                    {{ territorial.territorial_seguimiento }}
                  </span>
                </div>
              </div>

              <!-- Municipios asignados -->
<!-- Municipios asignados -->
              <div class="detail-section" v-if="modalDetalle.municipios.length > 0">
                <h5><i class="material-icons">location_on</i> Municipios Asignados ({{ modalDetalle.municipios.length }})</h5>
                <div class="municipios-list-detail">
                  <div 
                    v-for="asignacion in modalDetalle.municipios" 
                    :key="asignacion.id"
                    class="municipio-item-detail"
                  >
                    <i class="material-icons">location_on</i>
                    <div class="municipio-info-detail">
                      <span class="municipio-nombre">{{ getMunicipioNombre(asignacion.cod_municipio) }}</span>
                      <span class="municipio-depto">{{ getDepartamentoNombre(asignacion.cod_municipio) }}</span>
                      <span class="municipio-territorial">
                        <i class="material-icons">business</i>
                        {{ getTerritorialesDelProfesional() }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Si no tiene asignaciones -->
              <div v-if="modalDetalle.territoriales.length === 0 && modalDetalle.municipios.length === 0" class="no-asignaciones">
                <i class="material-icons">info</i>
                <p>Este profesional no tiene territoriales ni municipios asignados.</p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="modalDetalle.mostrar = false">
              <i class="material-icons">close</i>
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/store/auth'
import { debounce } from 'lodash'
import api from '@/api/config'

export default defineComponent({
  name: 'ProfesionalesDisposicionList',

  setup() {
    const authStore = useAuthStore()
    
    // ============= ESTADO =============
    const cargando = ref(false)
    const error = ref<string | null>(null)
    
    // Datos principales
    const profesionales = ref<any[]>([])
    const departamentos = ref<any[]>([])
    const municipios = ref<any[]>([])
    const profesionalTerritorial = ref<any[]>([])
    const profesionalMunicipio = ref<any[]>([])
    
    // Filtros
    const filtros = ref({
      rol: '',
      territorial: '',
      departamento: '',
      municipio: '',
      busqueda: ''
    })
    
    // Paginación
    const paginaActual = ref(1)
    const elementosPorPagina = ref(20)
    
    // Modal
    const modalDetalle = ref({
      mostrar: false,
      profesional: null as any,
      territoriales: [] as any[],
      municipios: [] as any[]
    })
    
    // ============= PERMISOS =============
    const isSuperAdmin = computed(() => 
      authStore.user?.isAdmin === true || authStore.user?.is_superuser === true
    )
    
    const isAdmin = computed(() => 
      (authStore.user?.isStaff === true || authStore.isAdmin) && !isSuperAdmin.value
    )
    
    const isProfesional = computed(() => 
      authStore.user?.rol_tipo === 'profesional'
    )
    
    const accessLevelText = computed(() => {
      if (isSuperAdmin.value) return 'Acceso Total';
      if (isAdmin.value) return 'Solo Lectura + Descarga';
      if (isProfesional.value) return 'Información Limitada';
      return 'Solo Lectura';
    })
    
    const accessLevelIcon = computed(() => {
      if (isSuperAdmin.value) return 'all_inclusive';
      if (isAdmin.value) return 'download';
      if (isProfesional.value) return 'info';
      return 'visibility';
    })
    
    const accessLevelClass = computed(() => {
      if (isSuperAdmin.value) return 'access-total';
      if (isAdmin.value) return 'access-admin';
      if (isProfesional.value) return 'access-profesional';
      return 'access-publico';
    })
    const getTerritorialesDelProfesional = (): string => {
      if (!modalDetalle.value.territoriales || modalDetalle.value.territoriales.length === 0) {
        return 'Sin asignación territorial'
      }
      
      const territoriales = modalDetalle.value.territoriales
        .map(t => t.territorial_seguimiento)
        .filter(t => t && t.trim() !== '')
        .join(', ')
      
      return territoriales || 'Sin asignación territorial'
    }
    // ============= COMPUTED PROPERTIES DINÁMICOS =============
    
    /**
     * ROLES DISPONIBLES - Se filtra según otros filtros activos
     */
    const rolesDisponibles = computed(() => {
      let profesionalesFiltrados = [...profesionales.value]
      
      // Filtrar por territorial si está seleccionada
      if (filtros.value.territorial) {
        const profesionalesIds = profesionalTerritorial.value
          .filter(pt => pt.territorial_seguimiento === filtros.value.territorial)
          .map(pt => pt.cod_profesional)
        profesionalesFiltrados = profesionalesFiltrados.filter(p => 
          profesionalesIds.includes(p.cod_profesional)
        )
      }
      
      // Filtrar por municipio si está seleccionado
      if (filtros.value.municipio) {
        const profesionalesIds = profesionalMunicipio.value
          .filter(pm => pm.cod_municipio.toString() === filtros.value.municipio.toString())
          .map(pm => pm.cod_profesional)
        profesionalesFiltrados = profesionalesFiltrados.filter(p => 
          profesionalesIds.includes(p.cod_profesional)
        )
      } 
      // Si no hay municipio específico pero sí departamento, filtrar por departamento
      else if (filtros.value.departamento) {
        const municipiosDelDepto = municipios.value
          .filter(m => m.cod_depto.toString() === filtros.value.departamento.toString())
          .map(m => m.cod_municipio)
        
        const profesionalesIds = profesionalMunicipio.value
          .filter(pm => municipiosDelDepto.includes(pm.cod_municipio))
          .map(pm => pm.cod_profesional)
        
        profesionalesFiltrados = profesionalesFiltrados.filter(p => 
          profesionalesIds.includes(p.cod_profesional)
        )
      }
      
      // Extraer roles únicos y ordenar
      const rolesUnicos = Array.from(new Set(
        profesionalesFiltrados
          .map(p => p.rol_profesional)
          .filter(r => r && r.trim() !== '')
      )).sort()
      
      return rolesUnicos
    })
    
    /**
     * TERRITORIALES DISPONIBLES - Se filtra según otros filtros activos  
     */
    const territorialesDisponibles = computed(() => {
      let territorialesValidas = new Set<string>()
      
      // Obtener todas las territoriales de profesionales activos
      let profesionalesFiltrados = [...profesionales.value]
      
      // Filtrar profesionales por rol si está seleccionado
      if (filtros.value.rol) {
        profesionalesFiltrados = profesionalesFiltrados.filter(p => 
          p.rol_profesional === filtros.value.rol
        )
      }
      
      // Filtrar profesionales por departamento/municipio si está seleccionado
      if (filtros.value.municipio) {
        const profesionalesIds = profesionalMunicipio.value
          .filter(pm => pm.cod_municipio.toString() === filtros.value.municipio.toString())
          .map(pm => pm.cod_profesional)
        profesionalesFiltrados = profesionalesFiltrados.filter(p => 
          profesionalesIds.includes(p.cod_profesional)
        )
      } else if (filtros.value.departamento) {
        const municipiosDelDepto = municipios.value
          .filter(m => m.cod_depto.toString() === filtros.value.departamento.toString())
          .map(m => m.cod_municipio)
        
        const profesionalesIds = profesionalMunicipio.value
          .filter(pm => municipiosDelDepto.includes(pm.cod_municipio))
          .map(pm => pm.cod_profesional)
        
        profesionalesFiltrados = profesionalesFiltrados.filter(p => 
          profesionalesIds.includes(p.cod_profesional)
        )
      }
      
      // Obtener territoriales de los profesionales filtrados
      const profesionalesIdsValidos = profesionalesFiltrados.map(p => p.cod_profesional)
      
      profesionalTerritorial.value
        .filter(pt => profesionalesIdsValidos.includes(pt.cod_profesional))
        .forEach(pt => {
          if (pt.territorial_seguimiento && pt.territorial_seguimiento.trim() !== '') {
            territorialesValidas.add(pt.territorial_seguimiento)
          }
        })
      
      return Array.from(territorialesValidas).sort()
    })
    
    /**
     * DEPARTAMENTOS DISPONIBLES - Se filtra según otros filtros activos
     */
    const departamentosDisponibles = computed(() => {
      let departamentosIds = new Set<number>()
      
      // Obtener profesionales filtrados
      let profesionalesFiltrados = [...profesionales.value]
      
      if (filtros.value.rol) {
        profesionalesFiltrados = profesionalesFiltrados.filter(p => 
          p.rol_profesional === filtros.value.rol
        )
      }
      
      if (filtros.value.territorial) {
        const profesionalesIds = profesionalTerritorial.value
          .filter(pt => pt.territorial_seguimiento === filtros.value.territorial)
          .map(pt => pt.cod_profesional)
        profesionalesFiltrados = profesionalesFiltrados.filter(p => 
          profesionalesIds.includes(p.cod_profesional)
        )
      }
      
      // Si hay municipio específico, solo ese departamento
      if (filtros.value.municipio) {
        const municipio = municipios.value.find(m => 
          m.cod_municipio.toString() === filtros.value.municipio.toString()
        )
        if (municipio) {
          departamentosIds.add(municipio.cod_depto)
        }
      } else {
        // Obtener departamentos de municipios que tienen profesionales asignados
        const profesionalesIdsValidos = profesionalesFiltrados.map(p => p.cod_profesional)
        const municipiosConProfesionales = profesionalMunicipio.value
          .filter(pm => profesionalesIdsValidos.includes(pm.cod_profesional))
          .map(pm => pm.cod_municipio)
        
        municipios.value
          .filter(m => municipiosConProfesionales.includes(m.cod_municipio))
          .forEach(m => departamentosIds.add(m.cod_depto))
      }
      
      return departamentos.value
        .filter(d => departamentosIds.has(d.cod_depto))
        .sort((a, b) => a.nom_depto.localeCompare(b.nom_depto))
    })
    
    /**
     * MUNICIPIOS DISPONIBLES - Se filtra según otros filtros activos
     */
    const municipiosDisponibles = computed(() => {
      let municipiosValidos = [...municipios.value]
      
      // Filtrar por departamento si está seleccionado
      if (filtros.value.departamento) {
        municipiosValidos = municipiosValidos.filter(m => 
          m.cod_depto.toString() === filtros.value.departamento.toString()
        )
      }
      
      // Obtener profesionales filtrados por rol y territorial
      let profesionalesFiltrados = [...profesionales.value]
      
      if (filtros.value.rol) {
        profesionalesFiltrados = profesionalesFiltrados.filter(p => 
          p.rol_profesional === filtros.value.rol
        )
      }
      
      if (filtros.value.territorial) {
        const profesionalesIds = profesionalTerritorial.value
          .filter(pt => pt.territorial_seguimiento === filtros.value.territorial)
          .map(pt => pt.cod_profesional)
        profesionalesFiltrados = profesionalesFiltrados.filter(p => 
          profesionalesIds.includes(p.cod_profesional)
        )
      }
      
      // Filtrar municipios que tienen profesionales asignados
      const profesionalesIdsValidos = profesionalesFiltrados.map(p => p.cod_profesional)
      const municipiosConProfesionales = new Set(
        profesionalMunicipio.value
          .filter(pm => profesionalesIdsValidos.includes(pm.cod_profesional))
          .map(pm => pm.cod_municipio)
      )
      
      return municipiosValidos
        .filter(m => municipiosConProfesionales.has(m.cod_municipio))
        .sort((a, b) => a.nom_municipio.localeCompare(b.nom_municipio))
    })

    // ============= COMPUTED PROPERTIES AUXILIARES =============
    
    const hayFiltrosActivos = computed(() => {
      return !!(filtros.value.rol || filtros.value.territorial || filtros.value.departamento || filtros.value.municipio)
    })
    
    const profesionalesFiltrados = computed(() => {
      let resultado = [...profesionales.value]
      
      // Filtro por búsqueda
      if (filtros.value.busqueda.trim()) {
        const busqueda = filtros.value.busqueda.toLowerCase().trim()
        resultado = resultado.filter(p => 
          p.nombre_profesional?.toLowerCase().includes(busqueda) ||
          p.cod_profesional?.toLowerCase().includes(busqueda) ||
          (p.correo_profesional && p.correo_profesional.toLowerCase().includes(busqueda))
        )
      }
      
      // Filtro por rol
      if (filtros.value.rol) {
        resultado = resultado.filter(p => p.rol_profesional === filtros.value.rol)
      }
      
      // Filtro por territorial
      if (filtros.value.territorial) {
        const profesionalesIds = profesionalTerritorial.value
          .filter(pt => pt.territorial_seguimiento === filtros.value.territorial)
          .map(pt => pt.cod_profesional)
        resultado = resultado.filter(p => profesionalesIds.includes(p.cod_profesional))
      }
      
      // Filtro por municipio específico
      if (filtros.value.municipio) {
        const profesionalesIds = profesionalMunicipio.value
          .filter(pm => pm.cod_municipio.toString() === filtros.value.municipio.toString())
          .map(pm => pm.cod_profesional)
        resultado = resultado.filter(p => profesionalesIds.includes(p.cod_profesional))
      } else if (filtros.value.departamento) {
        // Filtro por departamento (todos los municipios del departamento)
        const municipiosDelDepto = municipios.value
          .filter(m => m.cod_depto.toString() === filtros.value.departamento.toString())
          .map(m => m.cod_municipio)
        
        const profesionalesIds = profesionalMunicipio.value
          .filter(pm => municipiosDelDepto.includes(pm.cod_municipio))
          .map(pm => pm.cod_profesional)
        
        resultado = resultado.filter(p => profesionalesIds.includes(p.cod_profesional))
      }
      
      return resultado
    })
    
    const profesionalesVisibles = computed(() => {
      const inicio = (paginaActual.value - 1) * elementosPorPagina.value
      const fin = inicio + elementosPorPagina.value
      return profesionalesFiltrados.value.slice(inicio, fin)
    })
    
    const totalPaginas = computed(() => {
      return Math.ceil(profesionalesFiltrados.value.length / elementosPorPagina.value) || 1
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
        // Lógica para mostrar páginas con puntos suspensivos
        if (paginaActual.value <= 3) {
          for (let i = 1; i <= 5; i++) {
            botones.push({
              valor: i,
              texto: i.toString(),
              activo: i === paginaActual.value,
              ellipsis: false
            })
          }
        } else if (paginaActual.value >= totalPaginas.value - 2) {
          for (let i = totalPaginas.value - 4; i <= totalPaginas.value; i++) {
            botones.push({
              valor: i,
              texto: i.toString(),
              activo: i === paginaActual.value,
              ellipsis: false
            })
          }
        } else {
          for (let i = paginaActual.value - 2; i <= paginaActual.value + 2; i++) {
            botones.push({
              valor: i,
              texto: i.toString(),
              activo: i === paginaActual.value,
              ellipsis: false
            })
          }
        }
      }
      
      return botones
    })

    // ============= WATCHERS PARA AUTO-LIMPIEZA =============
    
    /**
     * Cuando cambia el rol, verificar y limpiar filtros incompatibles
     */
    watch(() => filtros.value.rol, (nuevoRol) => {
      if (nuevoRol) {
        // Verificar si la territorial actual sigue siendo válida
        if (filtros.value.territorial && !territorialesDisponibles.value.includes(filtros.value.territorial)) {
          console.log('🧹 Limpiando territorial incompatible')
          filtros.value.territorial = ''
        }
        
        // Verificar si el departamento actual sigue siendo válido
        const deptosValidos = departamentosDisponibles.value.map(d => d.cod_depto.toString())
        if (filtros.value.departamento && !deptosValidos.includes(filtros.value.departamento)) {
          console.log('🧹 Limpiando departamento incompatible')
          filtros.value.departamento = ''
        }
        
        // Verificar si el municipio actual sigue siendo válido
        const municipiosValidos = municipiosDisponibles.value.map(m => m.cod_municipio.toString())
        if (filtros.value.municipio && !municipiosValidos.includes(filtros.value.municipio)) {
          console.log('🧹 Limpiando municipio incompatible')
          filtros.value.municipio = ''
        }
      }
    })
    
    /**
     * Cuando cambia la territorial, verificar y limpiar filtros incompatibles
     */
    watch(() => filtros.value.territorial, (nuevaTerritorial) => {
      if (nuevaTerritorial) {
        // Verificar si el rol actual sigue siendo válido
        if (filtros.value.rol && !rolesDisponibles.value.includes(filtros.value.rol)) {
          console.log('🧹 Limpiando rol incompatible')
          filtros.value.rol = ''
        }
        
        // Verificar departamento y municipio
        const deptosValidos = departamentosDisponibles.value.map(d => d.cod_depto.toString())
        if (filtros.value.departamento && !deptosValidos.includes(filtros.value.departamento)) {
          console.log('🧹 Limpiando departamento incompatible')
          filtros.value.departamento = ''
        }
        
        const municipiosValidos = municipiosDisponibles.value.map(m => m.cod_municipio.toString())
        if (filtros.value.municipio && !municipiosValidos.includes(filtros.value.municipio)) {
          console.log('🧹 Limpiando municipio incompatible')
          filtros.value.municipio = ''
        }
      }
    })
    
    /**
     * Cuando cambia el departamento, verificar y limpiar filtros incompatibles
     */
    watch(() => filtros.value.departamento, (nuevoDepartamento) => {
      if (nuevoDepartamento) {
        // Verificar municipio
        const municipiosValidos = municipiosDisponibles.value.map(m => m.cod_municipio.toString())
        if (filtros.value.municipio && !municipiosValidos.includes(filtros.value.municipio)) {
          console.log('🧹 Limpiando municipio incompatible')
          filtros.value.municipio = ''
        }
        
        // Verificar otros filtros
        if (filtros.value.rol && !rolesDisponibles.value.includes(filtros.value.rol)) {
          console.log('🧹 Limpiando rol incompatible')
          filtros.value.rol = ''
        }
        
        if (filtros.value.territorial && !territorialesDisponibles.value.includes(filtros.value.territorial)) {
          console.log('🧹 Limpiando territorial incompatible')
          filtros.value.territorial = ''
        }
      }
    })
    
    /**
     * Cuando cambia el municipio, verificar y limpiar filtros incompatibles
     */
    watch(() => filtros.value.municipio, (nuevoMunicipio) => {
      if (nuevoMunicipio) {
        // Auto-seleccionar departamento si no está seleccionado
        const municipio = municipios.value.find(m => 
          m.cod_municipio.toString() === nuevoMunicipio.toString()
        )
        if (municipio && !filtros.value.departamento) {
          console.log('🔄 Auto-seleccionando departamento')
          filtros.value.departamento = municipio.cod_depto.toString()
        }
        
        // Verificar otros filtros
        if (filtros.value.rol && !rolesDisponibles.value.includes(filtros.value.rol)) {
          console.log('🧹 Limpiando rol incompatible')
          filtros.value.rol = ''
        }
        
        if (filtros.value.territorial && !territorialesDisponibles.value.includes(filtros.value.territorial)) {
          console.log('🧹 Limpiando territorial incompatible')
          filtros.value.territorial = ''
        }
      }
    })

    // ============= FUNCIONES PRINCIPALES =============
    
    const procesarDatos = (response: any) => {
      if (response && response.results && Array.isArray(response.results)) {
        return response.results
      }
      return Array.isArray(response) ? response : []
    }
    
    const cargarProfesionales = async () => {
      try {
        cargando.value = true
        error.value = null
        
        console.log('🔄 Cargando datos de profesionales...')
        
        const [
          profesionalesData,
          departamentosData,
          municipiosData,
          profesionalTerritorialData,
          profesionalMunicipioData
        ] = await Promise.all([
          api.get('/preoperacion/profesionales-seguimiento/'),
          api.get('/preoperacion/departamentos/'),
          api.get('/preoperacion/municipios/'),
          api.get('/preoperacion/profesional-territorial/'),
          api.get('/preoperacion/profesional-municipio/')
        ])
        
        profesionales.value = procesarDatos(profesionalesData)
        departamentos.value = procesarDatos(departamentosData)
        municipios.value = procesarDatos(municipiosData)
        profesionalTerritorial.value = procesarDatos(profesionalTerritorialData)
        profesionalMunicipio.value = procesarDatos(profesionalMunicipioData)
        
        console.log('✅ Datos cargados:', {
          profesionales: profesionales.value.length,
          departamentos: departamentos.value.length,
          municipios: municipios.value.length,
          relaciones_territorial: profesionalTerritorial.value.length,
          relaciones_municipio: profesionalMunicipio.value.length
        })
        
      } catch (err: any) {
        console.error('❌ Error al cargar profesionales:', err)
        error.value = 'Error al cargar los profesionales. Por favor, inténtelo de nuevo.'
      } finally {
        cargando.value = false
      }
    }
    
    const aplicarFiltros = () => {
      console.log('🔄 Aplicando filtros:', filtros.value)
      paginaActual.value = 1
    }
    
    const limpiarFiltros = () => {
      console.log('🧹 Limpiando todos los filtros')
      filtros.value = {
        rol: '',
        territorial: '',
        departamento: '',
        municipio: '',
        busqueda: ''
      }
      paginaActual.value = 1
    }
    
    const limpiarFiltroEspecifico = (filtro: string) => {
      console.log(`🧹 Limpiando filtro específico: ${filtro}`)
      filtros.value[filtro] = ''
      aplicarFiltros()
    }
    
    const limpiarBusqueda = () => {
      filtros.value.busqueda = ''
      aplicarFiltros()
    }
    
    const handleDepartamentoChange = () => {
      // Al cambiar departamento, limpiar municipio para que se actualice la lista
      if (filtros.value.municipio) {
        const municipiosValidos = municipiosDisponibles.value.map(m => m.cod_municipio.toString())
        if (!municipiosValidos.includes(filtros.value.municipio)) {
          filtros.value.municipio = ''
        }
      }
      aplicarFiltros()
    }
    
    const debounceSearch = debounce(() => {
      aplicarFiltros()
    }, 500)
    
    const cambiarPagina = (pagina: number) => {
      if (pagina >= 1 && pagina <= totalPaginas.value) {
        paginaActual.value = pagina
      }
    }
    
    // ============= FUNCIONES AUXILIARES =============
    
    const getRoleClass = (tipo: string): string => {
      switch (tipo) {
        case 'L.A.S': return 'role-las'
        case 'P.A.S': return 'role-pas'
        default: return 'role-other'
      }
    }
    
    const contarTerritoriales = (codProfesional: string): number => {
      return profesionalTerritorial.value.filter(pt => pt.cod_profesional === codProfesional).length
    }
    
    const contarMunicipios = (codProfesional: string): number => {
      return profesionalMunicipio.value.filter(pm => pm.cod_profesional === codProfesional).length
    }
    
    const getMunicipioNombre = (codMunicipio: number): string => {
      const municipio = municipios.value.find(m => m.cod_municipio === codMunicipio)
      return municipio ? municipio.nom_municipio : 'Desconocido'
    }
    
    const getDepartamentoNombre = (codMunicipio: number): string => {
      const municipio = municipios.value.find(m => m.cod_municipio === codMunicipio)
      if (!municipio) return 'Desconocido'
      
      const depto = departamentos.value.find(d => d.cod_depto === municipio.cod_depto)
      return depto ? depto.nom_depto : 'Desconocido'
    }
    
    const getNombreDepartamento = (codDepto: string): string => {
      const depto = departamentos.value.find(d => d.cod_depto.toString() === codDepto)
      return depto ? depto.nom_depto : 'Desconocido'
    }
    
    const getNombreMunicipio = (codMunicipio: string): string => {
      const municipio = municipios.value.find(m => m.cod_municipio.toString() === codMunicipio)
      return municipio ? municipio.nom_municipio : 'Desconocido'
    }
    
    const verDetalleProfesional = async (profesional: any) => {
      modalDetalle.value.profesional = profesional
      modalDetalle.value.territoriales = profesionalTerritorial.value.filter(
        pt => pt.cod_profesional === profesional.cod_profesional
      )
      modalDetalle.value.municipios = profesionalMunicipio.value.filter(
        pm => pm.cod_profesional === profesional.cod_profesional
      )
      modalDetalle.value.mostrar = true
    }
    

    // Función auxiliar para obtener nombres de territoriales
    const getNombresTerritoriales = (codProfesional: string): string => {
      const territoriales = profesionalTerritorial.value
        .filter(pt => pt.cod_profesional === codProfesional)
        .map(pt => pt.territorial_seguimiento)
        .filter(t => t && t.trim() !== '')
      
      return territoriales.length > 0 ? territoriales.join(' | ') : 'Sin asignación'
    }
    
    // Función auxiliar para obtener nombres de municipios
    const getNombresMunicipios = (codProfesional: string): string => {
      const municipiosAsignados = profesionalMunicipio.value
        .filter(pm => pm.cod_profesional === codProfesional)
        .map(pm => {
          const municipio = municipios.value.find(m => m.cod_municipio === pm.cod_municipio)
          return municipio ? municipio.nom_municipio : 'Desconocido'
        })
        .filter(m => m !== 'Desconocido')
      
      return municipiosAsignados.length > 0 ? municipiosAsignados.join(' | ') : 'Sin asignación'
    }

    const exportarDatos = () => {
      try {
        if (!profesionalesFiltrados.value || profesionalesFiltrados.value.length === 0) {
          alert('No hay datos para exportar');
          return;
        }
        
        const headers = [
          'Código',
          'Nombre',
          'Correo',
          'Rol',
          'Territoriales Asignadas (Nombres)',
          'Cantidad de Municipios',
          'Municipios Asignados (Nombres)'
        ];
        
        const rows = profesionalesFiltrados.value.map(p => [
          p.cod_profesional,
          p.nombre_profesional,
          p.correo_profesional || '',
          p.rol_profesional,
          getNombresTerritoriales(p.cod_profesional),
          contarMunicipios(p.cod_profesional),
          getNombresMunicipios(p.cod_profesional)
        ]);
        
        const BOM = '\uFEFF';
        const csvContent = BOM + [
          headers.join(','),
          ...rows.map(row => row.map(cell => 
            `"${(cell !== null && cell !== undefined ? String(cell) : '').replace(/"/g, '""')}"`
          ).join(','))
        ].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `profesionales_consulta_${new Date().toISOString().slice(0, 10)}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        alert('Archivo CSV generado correctamente con nombres de territoriales y municipios');
        
      } catch (err) {
        console.error('Error al exportar datos:', err);
        alert(`Error al exportar datos: ${err.message}`);
      }
    }
    
    // ============= INICIALIZACIÓN =============
    onMounted(async () => {
      await cargarProfesionales()
    })
    
    return {
      // Estado
      cargando,
      error,
      profesionales,
      profesionalesFiltrados,
      profesionalesVisibles,
      departamentos,
      municipios,
      
      // Filtros dinámicos
      rolesDisponibles,
      territorialesDisponibles, 
      departamentosDisponibles,
      municipiosDisponibles,
      
      // Permisos
      isSuperAdmin,
      isAdmin,
      isProfesional,
      accessLevelText,
      accessLevelIcon,
      accessLevelClass,
      
      // Filtros y paginación
      filtros,
      hayFiltrosActivos,
      paginaActual,
      totalPaginas,
      botonesNumericos,
      
      // Modal
      modalDetalle,
      
      // Métodos
      cargarProfesionales,
      aplicarFiltros,
      limpiarFiltros,
      limpiarFiltroEspecifico,
      limpiarBusqueda,
      handleDepartamentoChange,
      debounceSearch,
      cambiarPagina,
      getRoleClass,
      contarTerritoriales,
      contarMunicipios,
      getMunicipioNombre,
      getDepartamentoNombre,
      getNombreDepartamento,
      getNombreMunicipio,
      verDetalleProfesional,
      exportarDatos,
      getTerritorialesDelProfesional
    }
  }
})
</script>

<style scoped>
/* ============= ESTILOS BASE ============= */
.profesionales-disposicion-container {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
}

/* ============= HEADER SECTION ============= */
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

.access-total {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
}

.access-admin {
  background: linear-gradient(135deg, #f39c12, #d68910);
  color: white;
}

.access-profesional {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  color: white;
}

.access-publico {
  background: linear-gradient(135deg, #95a5a6, #7f8c8d);
  color: white;
}

.actions-bar {
  display: flex;
  gap: 0.75rem;
}

/* ============= SECCIÓN DE FILTROS MEJORADOS ============= */
.filtros-section {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border-left: 4px solid #007bff;
}

.search-row {
  margin-bottom: 1.5rem;
}

.global-search {
  position: relative;
  max-width: 500px;
}

.global-search i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
  z-index: 2;
}

.global-search input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
  border: 2px solid #e9ecef;
  border-radius: 25px;
  font-size: 1rem;
  transition: all 0.2s;
}

.global-search input:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.25rem rgba(0, 123, 255, 0.25);
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
  padding: 0.25rem;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.clear-btn:hover {
  background-color: #e9ecef;
}

.row {
  display: flex;
  flex-wrap: wrap;
  margin: -0.5rem;
}

.col-md-6, .col-lg-3 {
  flex: 0 0 auto;
  padding: 0.5rem;
}

.col-lg-3 {
  width: 25%;
}

.col-md-6 {
  width: 50%;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  position: relative;
}

.form-group label {
  font-weight: 600;
  color: #495057;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.contador-opciones {
  color: #6c757d;
  font-size: 0.75rem;
  font-weight: normal;
  background-color: #f8f9fa;
  padding: 0.2rem 0.5rem;
  border-radius: 10px;
  border: 1px solid #e9ecef;
}

.form-control {
  padding: 0.5rem 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.95rem;
  transition: all 0.2s;
  background-color: white;
}

.form-control:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.25rem rgba(0, 123, 255, 0.25);
  outline: none;
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
  background: #00bfff; 
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
  background: #007acc; /* Azul más oscuro */
  transform: scale(1.15); /* Crece un poco más */
  box-shadow: 0 0 10px rgba(0, 191, 255, 0.6); /* Añade un "glow" azul neón */
}

/* ============= FILTROS ACTIVOS ============= */
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

.tag-filtro.rol {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
}

.tag-filtro.territorial {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  color: white;
}

.tag-filtro.departamento {
  background: linear-gradient(135deg, #f39c12, #d68910);
  color: white;
}

.tag-filtro.municipio {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
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
  gap: 1rem;
  justify-content: flex-start;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

/* ============= ESTADOS DE CARGA ============= */
.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
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

.loading-text {
  color: #6c757d;
  font-size: 1.1rem;
}

.error-container i,
.empty-container i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #6c757d;
}

/* ============= RESULTADOS ============= */
.results-container {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.results-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #343a40;
  margin: 0;
}

.results-summary {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.results-count {
  color: #007bff;
  font-size: 1rem;
  font-weight: 600;
}

.results-filter-info {
  color: #6c757d;
  font-size: 0.85rem;
  font-style: italic;
}

/* ============= GRID DE PROFESIONALES ============= */
.profesionales-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.profesional-card {
  background-color: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.profesional-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: #007bff;
}

.profesional-header {
  display: flex;
  align-items: center;
  padding: 1.25rem;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-bottom: 1px solid #e9ecef;
  gap: 1rem;
}

.profesional-avatar {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  flex-shrink: 0;
}

.profesional-info {
  flex: 1;
  min-width: 0;
}

.profesional-nombre {
  font-size: 1.1rem;
  font-weight: 600;
  color: #343a40;
  margin: 0 0 0.25rem;
  word-wrap: break-word;
}

.profesional-codigo {
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 500;
}

.profesional-body {
  padding: 1.25rem;
}

.info-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 1rem;
  gap: 0.5rem;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #495057;
  font-size: 0.9rem;
  min-width: 80px;
  flex-shrink: 0;
}

.info-label i {
  font-size: 1.1rem;
  color: #6c757d;
}

.info-value {
  flex: 1;
  color: #212529;
  font-size: 0.9rem;
  word-wrap: break-word;
}

.role-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.role-las {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
}

.role-pas {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  color: white;
}

.role-other {
  background: linear-gradient(135deg, #95a5a6, #7f8c8d);
  color: white;
}

.asignaciones-summary {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.asignacion-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6c757d;
  font-size: 0.85rem;
  font-weight: 500;
}

.asignacion-item i {
  font-size: 1.1rem;
  color: #007bff;
}

.profesional-footer {
  padding: 1rem 1.25rem;
  background-color: #f8f9fa;
  border-top: 1px solid #e9ecef;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
  justify-content: center;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

.view-btn {
  background: linear-gradient(135deg, #17a2b8, #138496);
}

/* ============= PAGINACIÓN ============= */
.pagination-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e9ecef;
}

.btn-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 40px;
  height: 40px;
  padding: 0.5rem;
  border: 1px solid #dee2e6;
  background-color: white;
  color: #007bff;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.btn-pagination:hover:not(:disabled):not(.disabled) {
  background-color: #e9ecef;
  border-color: #adb5bd;
}

.btn-pagination.active {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border-color: #007bff;
  font-weight: 600;
}

.btn-pagination:disabled {
  color: #6c757d;
  cursor: not-allowed;
  opacity: 0.5;
}

/* ============= MODAL ============= */
.modal {
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

.modal-dialog {
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e9ecef;
  background-color: #f8f9fa;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #343a40;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.close-button {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.close-button:hover {
  background-color: #e9ecef;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e9ecef;
  background-color: #f8f9fa;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

/* ============= DETALLES DEL PROFESIONAL EN MODAL ============= */
.profesional-detail-info {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-section {
  background-color: #f8f9fa;
  padding: 1.25rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.detail-section h5 {
  margin: 0 0 1rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: #343a40;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #dee2e6;
}

.detail-section h5 i {
  color: #007bff;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-weight: 600;
  color: #6c757d;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  color: #212529;
  font-size: 0.95rem;
}

.asignaciones-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.territorial-chip {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
  border-radius: 15px;
  font-size: 0.85rem;
  font-weight: 500;
}

.municipios-list-detail {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.75rem;
}

.municipio-item-detail {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background-color: white;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  transition: all 0.2s;
}

.municipio-item-detail:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #007bff;
}

.municipio-item-detail i {
  color: #007bff;
  font-size: 1.25rem;
}

.municipio-info-detail {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.municipio-nombre {
  font-weight: 600;
  color: #343a40;
  font-size: 0.9rem;
}

.municipio-depto {
  font-size: 0.8rem;
  color: #6c757d;
}

.no-asignaciones {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  text-align: center;
  color: #6c757d;
}

.no-asignaciones i {
  font-size: 3rem;
  color: #dee2e6;
}

/* ============= BOTONES ============= */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border: none;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
}

.btn-primary {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

.btn-secondary {
  background: linear-gradient(135deg, #6c757d, #545b62);
  color: white;
}

.btn-secondary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(108, 117, 125, 0.3);
}

.btn-export {
  background: linear-gradient(135deg, #28a745, #1e7e34);
  color: white;
}

.btn-export:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

.btn-refresh {
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
}

.btn-refresh:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(23, 162, 184, 0.3);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

/* ============= RESPONSIVE ============= */
@media (max-width: 992px) {
  .col-lg-3 {
    width: 50%;
  }
  
  .profesionales-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
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
    align-items: stretch;
  }
  
  .col-md-6, .col-lg-3 {
    width: 100%;
  }
  
  .profesionales-grid {
    grid-template-columns: 1fr;
  }
  
  .asignaciones-summary {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .municipios-list-detail {
    grid-template-columns: 1fr;
  }
  
  .modal-dialog {
    width: 95%;
  }
  
  .filtros-buttons {
    flex-direction: column;
  }
  
  .tags-filtros {
    flex-direction: column;
    align-items: stretch;
  }
  
  .tag-filtro {
    justify-content: space-between;
  }
}

@media (max-width: 480px) {
  .profesionales-disposicion-container {
    padding: 1rem;
  }
  
  .filtros-section {
    padding: 1rem;
  }
  
  .results-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .results-summary {
    align-items: flex-start;
  }
}
</style>