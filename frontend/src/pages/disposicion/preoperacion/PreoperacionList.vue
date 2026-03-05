<template>
  <div class="productos-page">
    <!-- Header -->
    <header class="page-header">
      <div class="header-content">
        <h1>Pre-Operación</h1>
        <div class="header-actions">
          <div class="access-badge" :class="accessLevelClass">
            <i class="material-icons">{{ accessLevelIcon }}</i>
            <span>{{ accessLevelText }}</span>
          </div>
          <button v-if="canExport" @click="exportarDatos" class="btn-export" :disabled="loading">
            <i class="material-icons">file_download</i>
            Exportar
          </button>
        </div>
      </div>
    </header>

    <!-- Filtros ACUMULATIVOS -->
    <section class="filters-section">
      <div class="search-container">
        <div class="search-box">
          <i class="material-icons">search</i>
          <input
            v-model="searchTerm"
            placeholder="Buscar municipio..."
            @input="debouncedSearch"
          />
          <button v-if="searchTerm" @click="clearSearch" class="clear-btn">
            <i class="material-icons">close</i>
          </button>
        </div>
      </div>

      <div class="filters-grid">
        <!-- FILTRO DEPARTAMENTO CON CONTADOR -->
        <div class="filter-container">
          <label class="filter-label">Departamento</label>
          <select v-model="filters.departamento" @change="onFilterChange">
            <option value="">Todos los departamentos ({{ departamentosDisponibles.length }})</option>
            <option
              v-for="dpto in departamentosDisponibles"
              :key="dpto.cod_depto"
              :value="dpto.cod_depto"
            >
              {{ dpto.nom_depto }} ({{ dpto.count_municipios }})
            </option>
          </select>
        </div>

        <!-- FILTRO TERRITORIAL CON CONTADOR -->
        <div class="filter-container">
          <label class="filter-label">Territorial</label>
          <select v-model="filters.territorial" @change="onFilterChange">
            <option value="">Todas las territoriales ({{ territorialesDisponibles.length }})</option>
            <option
              v-for="terr in territorialesDisponibles"
              :key="terr.nom_territorial"
              :value="terr.nom_territorial"
            >
              {{ terr.nom_territorial }} ({{ terr.count_municipios }})
            </option>
          </select>
        </div>

        <!-- FILTRO MUNICIPIO CON CONTADOR -->
        <div class="filter-container">
          <label class="filter-label">Municipio Específico</label>
          <select v-model="filters.municipio" @change="onFilterChange">
            <option value="">Todos los municipios ({{ municipiosParaSelector.length }})</option>
            <option
              v-for="mun in municipiosParaSelector"
              :key="mun.cod_municipio"
              :value="mun.cod_municipio"
            >
              {{ mun.nom_municipio }}
            </option>
          </select>
        </div>

        <!-- ACCIONES DE FILTROS -->
        <div class="filter-actions">
          <button @click="clearFilters" class="btn-clear" :disabled="!hasActiveFilters">
            <i class="material-icons">clear_all</i>
            Limpiar ({{ filtrosActivos.length }})
          </button>
          <button @click="refreshData" class="btn-refresh" :disabled="loading">
            <i class="material-icons">refresh</i>
          </button>
        </div>
      </div>

      <!-- RESUMEN DE FILTROS ACTIVOS -->
      <div v-if="hasActiveFilters" class="active-filters">
        <h4><i class="material-icons">filter_list</i> Filtros activos:</h4>
        <div class="filter-tags">
          <div v-for="filtro in filtrosActivos" :key="filtro.tipo" class="filter-tag">
            <span class="filter-type">{{ filtro.tipo }}:</span>
            <span class="filter-value">{{ filtro.valor }}</span>
            <button @click="removeFilter(filtro.tipo)" class="filter-remove">
              <i class="material-icons">close</i>
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Contenido -->
    <main class="content-section">
      <!-- Loading -->
      <div v-if="loading" class="loading-container">
        <div class="spinner"></div>
        <span>Cargando municipios con pre-operación...</span>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="error-container">
        <i class="material-icons">error</i>
        <p>{{ error }}</p>
        <button @click="refreshData" class="btn-retry">Reintentar</button>
      </div>

      <!-- Empty -->
      <div v-else-if="!municipiosFiltered.length" class="empty-container">
        <i class="material-icons">account_tree</i>
        <p>No se encontraron municipios con pre-operación con los filtros aplicados</p>
        <button @click="clearFilters" class="btn-clear">Limpiar filtros</button>
      </div>

      <!-- Table -->
      <div v-else class="table-container">
        <div class="table-header">
          <h3>
            {{ municipiosFiltered.length }} municipios encontrados
            <span v-if="hasActiveFilters" class="filter-result">
              (filtrados de {{ totalMunicipiosBase }})
            </span>
          </h3>
        </div>

        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th @click="sortBy('cod_municipio')" class="sortable">
                  Código <i v-if="sortField === 'cod_municipio'" class="material-icons">{{ sortIcon }}</i>
                </th>
                <th @click="sortBy('nom_municipio')" class="sortable">
                  Municipio <i v-if="sortField === 'nom_municipio'" class="material-icons">{{ sortIcon }}</i>
                </th>
                <th>Departamento</th>
                <th>Territorial</th>
                <th class="text-center">Directorios</th>
                <th class="text-center">Archivos</th>
                <th class="text-center">Tamaño</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="municipio in paginatedMunicipios" :key="municipio.cod_municipio">
                <td class="text-center">{{ municipio.cod_municipio }}</td>
                <td class="municipio-name">{{ municipio.nom_municipio }}</td>
                <td>{{ getDepartamentoName(municipio.cod_depto) }}</td>
                <td>{{ municipio.nom_territorial || 'N/A' }}</td>
                <td class="text-center">
                  <span class="badge badge-info">{{ municipio.total_directorios || 0 }}</span>
                </td>
                <td class="text-center">
                  <span class="badge badge-primary">{{ municipio.total_archivos || 0 }}</span>
                </td>
                <td class="text-center">
                  <span class="badge badge-success">{{ municipio.tamano_total || '0 B' }}</span>
                </td>
                <td>
                  <div class="actions">
                    <button @click="verDetalle(municipio)" class="action-btn view" title="Ver estructura">
                      <i class="material-icons">account_tree</i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Paginación -->
        <nav v-if="totalPages > 1" class="pagination">
          <button @click="prevPage" :disabled="currentPage === 1" class="page-btn">
            <i class="material-icons">chevron_left</i>
          </button>

          <span v-for="page in visiblePages" :key="page"
                :class="['page-num', { active: currentPage === page }]"
                @click="goToPage(page)">
            {{ page }}
          </span>

          <button @click="nextPage" :disabled="currentPage === totalPages" class="page-btn">
            <i class="material-icons">chevron_right</i>
          </button>
        </nav>
      </div>
    </main>

    <!-- Modal de árbol de directorios -->
    <div v-if="showTreeModal" class="modal-overlay" @click.self="closeTreeModal">
      <div class="modal-content modal-large">
        <div class="modal-header">
          <h3>
            <i class="material-icons">account_tree</i>
            Pre-Operación: {{ selectedMunicipio?.nom_municipio }}
          </h3>
          <button @click="closeTreeModal" class="close-btn">
            <i class="material-icons">close</i>
          </button>
        </div>

        <div class="modal-body">
          <!-- Loading árbol -->
          <div v-if="loadingTree" class="loading-container">
            <div class="spinner"></div>
            <span>Cargando estructura de directorios...</span>
          </div>

          <!-- Error árbol -->
          <div v-else-if="treeError" class="error-container">
            <i class="material-icons">error</i>
            <p>{{ treeError }}</p>
          </div>

          <!-- Empty árbol -->
          <div v-else-if="arbolData.length === 0" class="empty-container">
            <i class="material-icons">folder_off</i>
            <p>No se encontraron directorios de pre-operación para este municipio.</p>
          </div>

          <!-- Árbol de directorios -->
          <div v-else class="tree-wrapper">
            <div class="tree-stats">
              <span><i class="material-icons">folder</i> {{ totalNodos }} elementos</span>
            </div>
            <div class="tree-content">
              <TreeNode
                v-for="node in arbolData"
                :key="node.id"
                :node="node"
                :level="0"
                @show-details="showFileDetails"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de detalles de archivo -->
    <div v-if="showFileModal" class="modal-overlay" @click.self="closeFileModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>
            <i class="material-icons">{{ selectedFile?.tipo === 'archivo' ? 'description' : 'folder' }}</i>
            {{ selectedFile?.nombre }}
          </h3>
          <button @click="closeFileModal" class="close-btn">
            <i class="material-icons">close</i>
          </button>
        </div>

        <div class="modal-body">
          <div class="detail-row">
            <label>Tipo:</label>
            <span>{{ selectedFile?.tipo === 'archivo' ? 'Archivo' : 'Directorio' }}</span>
          </div>

          <div class="detail-row">
            <label>Fuente:</label>
            <span class="source-badge" :class="selectedFile?.fuente">
              {{ selectedFile?.fuente === 'insumos' ? 'Insumos (07_insu)' : 'Pre-Operación' }}
            </span>
          </div>

          <div v-if="selectedFile?.ruta_windows" class="detail-row">
            <label>Ruta Windows:</label>
            <div class="path-container">
              <code class="path-text">{{ selectedFile.ruta_windows }}</code>
              <button @click="copyPath" class="copy-btn" title="Copiar ruta">
                <i class="material-icons">{{ copied ? 'check' : 'content_copy' }}</i>
              </button>
            </div>
          </div>

          <div v-if="selectedFile?.extension" class="detail-row">
            <label>Extensión:</label>
            <span class="extension-badge">{{ selectedFile.extension }}</span>
          </div>

          <div v-if="selectedFile?.tamano_legible" class="detail-row">
            <label>Tamaño:</label>
            <span>{{ selectedFile.tamano_legible }}</span>
          </div>

          <div v-if="selectedFile?.propietario" class="detail-row">
            <label>Propietario:</label>
            <span>{{ selectedFile.propietario }}</span>
          </div>

          <div v-if="selectedFile?.fecha_modificacion" class="detail-row">
            <label>Última modificación:</label>
            <span>{{ formatDate(selectedFile.fecha_modificacion) }}</span>
          </div>
        </div>

        <div v-if="selectedFile?.tipo === 'archivo'" class="modal-footer">
          <button
            v-if="isViewable(selectedFile?.extension)"
            @click="viewFile"
            class="btn-primary"
          >
            <i class="material-icons">visibility</i>
            Ver archivo
          </button>
          <button @click="downloadFile" class="btn-secondary">
            <i class="material-icons">download</i>
            Descargar
          </button>
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

    <!-- Modal de Selección de Mecanismo de Financiación -->
    <div v-if="showMecanismoModal" class="modal-overlay" @click.self="closeMecanismoModal">
      <div class="modal-mecanismo">
        <div class="modal-header-mec">
          <h3>
            <i class="material-icons">account_balance</i>
            Seleccionar Fuente de Financiación
          </h3>
          <button @click="closeMecanismoModal" class="modal-close-mec">
            <i class="material-icons">close</i>
          </button>
        </div>
        <div class="modal-body-mec">
          <p class="modal-subtitle-mec">
            El municipio <strong>{{ municipioSeleccionado?.nom_municipio }}</strong> tiene múltiples fuentes de financiación.
            Seleccione la que desea consultar:
          </p>
          <div v-if="loadingMecanismos" class="loading-mecanismos">
            <div class="spinner-small-mec"></div>
            <span>Cargando mecanismos...</span>
          </div>
          <div v-else class="mecanismos-list">
            <button
              v-for="mecanismo in mecanismosDisponibles"
              :key="mecanismo.codigo"
              @click="seleccionarMecanismo(mecanismo)"
              class="mecanismo-option"
            >
              <div class="mecanismo-info">
                <span class="mecanismo-codigo">{{ mecanismo.codigo }}</span>
                <span class="mecanismo-stats">
                  {{ mecanismo.total_directorios }} directorio(s) · {{ mecanismo.total_archivos }} archivo(s)
                </span>
              </div>
              <i class="material-icons">arrow_forward</i>
            </button>
          </div>
        </div>
        <div class="modal-footer-mec">
          <button @click="closeMecanismoModal" class="btn-cancel-mec">Cancelar</button>
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
import { format } from 'date-fns'
import api, { API_URL } from '@/api/config'

// Componente recursivo para el árbol
const TreeNode = {
  name: 'TreeNode',
  props: {
    node: { type: Object, required: true },
    level: { type: Number, default: 0 }
  },
  emits: ['show-details'],
  data() {
    return {
      expanded: this.level < 2
    }
  },
  computed: {
    hasChildren() {
      return this.node.hijos && this.node.hijos.length > 0
    },
    nodeIcon() {
      if (this.node.tipo === 'archivo') {
        const ext = this.node.extension?.toLowerCase()
        if (['.pdf'].includes(ext)) return 'picture_as_pdf'
        if (['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'].includes(ext)) return 'image'
        if (['.doc', '.docx'].includes(ext)) return 'article'
        if (['.xls', '.xlsx'].includes(ext)) return 'table_chart'
        if (['.zip', '.rar', '.7z'].includes(ext)) return 'folder_zip'
        return 'description'
      }
      if (this.node.tipo === 'categoria') return 'category'
      return this.expanded ? 'folder_open' : 'folder'
    },
    nodeClass() {
      return {
        'tree-node': true,
        'is-file': this.node.tipo === 'archivo',
        'is-directory': this.node.tipo === 'directorio',
        'is-category': this.node.tipo === 'categoria',
        'from-insumos': this.node.fuente === 'insumos',
        'from-preoperacion': this.node.fuente === 'preoperacion'
      }
    }
  },
  methods: {
    toggle() {
      if (this.hasChildren) {
        this.expanded = !this.expanded
      }
    },
    showDetails() {
      this.$emit('show-details', this.node)
    }
  },
  template: `
    <div :class="nodeClass" :style="{ paddingLeft: level * 20 + 'px' }">
      <div class="node-content" @click="node.tipo === 'archivo' ? showDetails() : toggle()">
        <span v-if="hasChildren" class="expand-icon" @click.stop="toggle">
          <i class="material-icons">{{ expanded ? 'expand_more' : 'chevron_right' }}</i>
        </span>
        <span v-else class="expand-placeholder"></span>

        <i class="material-icons node-icon">{{ nodeIcon }}</i>
        <span class="node-name">{{ node.nombre }}</span>

        <span v-if="node.archivos_count > 0" class="file-count">
          ({{ node.archivos_count }} archivos)
        </span>

        <span v-if="node.fuente" class="source-tag" :class="node.fuente">
          {{ node.fuente === 'insumos' ? 'INS' : 'PRE' }}
        </span>

        <button
          v-if="node.tipo === 'archivo'"
          @click.stop="showDetails"
          class="details-btn"
          title="Ver detalles"
        >
          <i class="material-icons">info</i>
        </button>
      </div>

      <div v-if="expanded && hasChildren" class="children">
        <TreeNode
          v-for="child in node.hijos"
          :key="child.id"
          :node="child"
          :level="level + 1"
          @show-details="$emit('show-details', $event)"
        />
      </div>
    </div>
  `
}

export default defineComponent({
  name: 'PreoperacionList',
  components: { TreeNode },

  setup() {
    const authStore = useAuthStore()
    const router = useRouter()

    // Estado
    const loading = ref(false)
    const error = ref<string | null>(null)
    const searchTerm = ref('')

    // Datos base
    const departamentos = ref<any[]>([])
    const territoriales = ref<any[]>([])
    const municipiosList = ref<any[]>([])
    const municipiosConPreoperacion = ref<any[]>([])
    const todosLosMunicipiosConPreoperacion = ref<any[]>([])

    // Filtros
    const filters = ref({
      departamento: '',
      municipio: '',
      territorial: ''
    })

    // Ordenamiento y paginación
    const sortField = ref('nom_municipio')
    const sortAsc = ref(true)
    const currentPage = ref(1)
    const pageSize = ref(10)

    // Modal de árbol
    const showTreeModal = ref(false)
    const selectedMunicipio = ref<any>(null)
    const arbolData = ref<any[]>([])
    const loadingTree = ref(false)
    const treeError = ref<string | null>(null)

    // Modal de archivo
    const showFileModal = ref(false)
    const selectedFile = ref<any>(null)
    const copied = ref(false)

    // Notificación
    const notification = ref({
      show: false,
      message: '',
      type: 'success',
      icon: 'check_circle',
      timeout: null as number | null
    })

    // Modal de selección de mecanismo
    const showMecanismoModal = ref(false)
    const municipioSeleccionado = ref<any>(null)
    const mecanismosDisponibles = ref<any[]>([])
    const loadingMecanismos = ref(false)

    // ============ PERMISOS Y AUTORIZACIONES ============

    const userPermissions = computed(() => ({
      isSuperAdmin: authStore.isSuperAdmin,
      isAdmin: authStore.isAdmin,
      isProfesional: authStore.isProfesional,
      isAnyAdmin: authStore.isAnyAdmin
    }))

    const canExport = computed(() => {
      const { isSuperAdmin, isAdmin } = userPermissions.value
      return isSuperAdmin || isAdmin
    })

    const accessLevelText = computed(() => {
      const { isSuperAdmin, isAdmin, isProfesional } = userPermissions.value
      if (isSuperAdmin) return 'Super Administrador'
      if (isAdmin) return 'Administrador'
      if (isProfesional) return 'Profesional'
      return 'Solo Lectura'
    })

    const accessLevelIcon = computed(() => {
      const { isSuperAdmin, isAdmin, isProfesional } = userPermissions.value
      if (isSuperAdmin) return 'admin_panel_settings'
      if (isAdmin) return 'settings'
      if (isProfesional) return 'work'
      return 'visibility'
    })

    const accessLevelClass = computed(() => {
      const { isSuperAdmin, isAdmin, isProfesional } = userPermissions.value
      if (isSuperAdmin) return 'super-admin'
      if (isAdmin) return 'admin'
      if (isProfesional) return 'profesional'
      return 'readonly'
    })

    // ============ MUNICIPIOS ASIGNADOS PARA PROFESIONALES ============

    const municipiosAsignados = computed(() => {
      if (!userPermissions.value.isProfesional || !authStore.user?.municipios_asignados) return []

      let municipios: string[] = []
      if (typeof authStore.user.municipios_asignados === 'string') {
        municipios = authStore.user.municipios_asignados.split(',')
          .map((m: string) => m.trim())
          .filter((m: string) => m.length > 0)
      } else if (Array.isArray(authStore.user.municipios_asignados)) {
        municipios = authStore.user.municipios_asignados.map((m: any) => String(m).trim())
      }
      return municipios
    })

    // ============ FILTROS ACUMULATIVOS/PROGRESIVOS ============

    // 1. MUNICIPIOS FILTRADOS PROGRESIVAMENTE (SIN BÚSQUEDA)
    const municipiosFiltradosBase = computed(() => {
      let result = [...todosLosMunicipiosConPreoperacion.value]

      // Si es profesional, filtrar solo municipios asignados
      if (userPermissions.value.isProfesional && !userPermissions.value.isAnyAdmin) {
        const asignados = municipiosAsignados.value
        if (asignados.length > 0) {
          result = result.filter(m =>
            asignados.includes(String(m.cod_municipio))
          )
        }
      }

      // Aplicar filtro de departamento
      if (filters.value.departamento) {
        result = result.filter(m =>
          m.cod_depto?.toString() === filters.value.departamento.toString()
        )
      }

      // Aplicar filtro de territorial
      if (filters.value.territorial) {
        result = result.filter(m =>
          m.nom_territorial === filters.value.territorial
        )
      }

      // Aplicar filtro de municipio específico
      if (filters.value.municipio) {
        result = result.filter(m =>
          m.cod_municipio?.toString() === filters.value.municipio.toString()
        )
      }

      return result
    })

    // 2. APLICAR BÚSQUEDA SOBRE MUNICIPIOS YA FILTRADOS
    const municipiosFiltered = computed(() => {
      let result = [...municipiosFiltradosBase.value]

      if (searchTerm.value.trim()) {
        const search = searchTerm.value.toLowerCase()
        result = result.filter(m =>
          m.nom_municipio.toLowerCase().includes(search) ||
          m.cod_municipio.toString().includes(search)
        )
      }

      return result
    })

    // 3. CALCULAR OPCIONES DISPONIBLES PARA DEPARTAMENTOS
    const departamentosDisponibles = computed(() => {
      let municipiosBase = [...todosLosMunicipiosConPreoperacion.value]

      if (filters.value.territorial) {
        municipiosBase = municipiosBase.filter(m =>
          m.nom_territorial === filters.value.territorial
        )
      }
      if (filters.value.municipio) {
        municipiosBase = municipiosBase.filter(m =>
          m.cod_municipio?.toString() === filters.value.municipio.toString()
        )
      }

      const deptoCounts = new Map()
      municipiosBase.forEach(m => {
        const deptoId = m.cod_depto?.toString()
        if (deptoId) {
          deptoCounts.set(deptoId, (deptoCounts.get(deptoId) || 0) + 1)
        }
      })

      return departamentos.value
        .filter(d => deptoCounts.has(d.cod_depto?.toString()))
        .map(d => ({
          ...d,
          count_municipios: deptoCounts.get(d.cod_depto?.toString()) || 0
        }))
        .sort((a, b) => a.nom_depto.localeCompare(b.nom_depto))
    })

    // 4. CALCULAR OPCIONES DISPONIBLES PARA TERRITORIALES
    const territorialesDisponibles = computed(() => {
      let municipiosBase = [...todosLosMunicipiosConPreoperacion.value]

      if (filters.value.departamento) {
        municipiosBase = municipiosBase.filter(m =>
          m.cod_depto?.toString() === filters.value.departamento.toString()
        )
      }
      if (filters.value.municipio) {
        municipiosBase = municipiosBase.filter(m =>
          m.cod_municipio?.toString() === filters.value.municipio.toString()
        )
      }

      const terrCounts = new Map()
      municipiosBase.forEach(m => {
        if (m.nom_territorial) {
          terrCounts.set(m.nom_territorial, (terrCounts.get(m.nom_territorial) || 0) + 1)
        }
      })

      return Array.from(terrCounts.keys())
        .map(nom => ({
          nom_territorial: nom,
          count_municipios: terrCounts.get(nom) || 0
        }))
        .sort((a, b) => a.nom_territorial.localeCompare(b.nom_territorial))
    })

    // 5. CALCULAR OPCIONES DISPONIBLES PARA MUNICIPIOS
    const municipiosParaSelector = computed(() => {
      let municipiosBase = [...todosLosMunicipiosConPreoperacion.value]

      if (filters.value.departamento) {
        municipiosBase = municipiosBase.filter(m =>
          m.cod_depto?.toString() === filters.value.departamento.toString()
        )
      }
      if (filters.value.territorial) {
        municipiosBase = municipiosBase.filter(m =>
          m.nom_territorial === filters.value.territorial
        )
      }

      return municipiosBase.sort((a, b) => a.nom_municipio.localeCompare(b.nom_municipio))
    })

    // 6. DETECTAR FILTROS ACTIVOS
    const hasActiveFilters = computed(() => {
      return !!(filters.value.departamento || filters.value.territorial || filters.value.municipio)
    })

    const filtrosActivos = computed(() => {
      const activos = []

      if (filters.value.departamento) {
        const depto = departamentos.value.find(d =>
          d.cod_depto?.toString() === filters.value.departamento.toString()
        )
        activos.push({
          tipo: 'departamento',
          valor: depto ? depto.nom_depto : filters.value.departamento
        })
      }

      if (filters.value.territorial) {
        activos.push({
          tipo: 'territorial',
          valor: filters.value.territorial
        })
      }

      if (filters.value.municipio) {
        const mun = todosLosMunicipiosConPreoperacion.value.find(m =>
          m.cod_municipio?.toString() === filters.value.municipio.toString()
        )
        activos.push({
          tipo: 'municipio',
          valor: mun ? mun.nom_municipio : filters.value.municipio
        })
      }

      return activos
    })

    const totalMunicipiosBase = computed(() => {
      if (userPermissions.value.isProfesional && !userPermissions.value.isAnyAdmin) {
        const asignados = municipiosAsignados.value
        if (asignados.length > 0) {
          return todosLosMunicipiosConPreoperacion.value.filter(m =>
            asignados.includes(String(m.cod_municipio))
          ).length
        }
      }
      return todosLosMunicipiosConPreoperacion.value.length
    })

    // ============ COMPUTED PROPERTIES RESTANTES ============

    const municipiosSorted = computed(() => {
      const sorted = [...municipiosFiltered.value]

      sorted.sort((a, b) => {
        let aVal = a[sortField.value] || ''
        let bVal = b[sortField.value] || ''

        if (typeof aVal === 'string') {
          aVal = aVal.toLowerCase()
          bVal = bVal.toLowerCase()
        }

        if (['cod_municipio', 'total_directorios', 'total_archivos'].includes(sortField.value)) {
          aVal = Number(aVal) || 0
          bVal = Number(bVal) || 0
        }

        const result = aVal < bVal ? -1 : aVal > bVal ? 1 : 0
        return sortAsc.value ? result : -result
      })

      return sorted
    })

    const totalPages = computed(() => {
      return Math.ceil(municipiosSorted.value.length / pageSize.value)
    })

    const paginatedMunicipios = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      return municipiosSorted.value.slice(start, start + pageSize.value)
    })

    const visiblePages = computed(() => {
      const total = totalPages.value
      const current = currentPage.value
      const delta = 2

      const range = []
      const rangeWithDots = []

      for (let i = Math.max(2, current - delta);
           i <= Math.min(total - 1, current + delta);
           i++) {
        range.push(i)
      }

      if (current - delta > 2) {
        rangeWithDots.push(1, '...')
      } else {
        rangeWithDots.push(1)
      }

      rangeWithDots.push(...range)

      if (current + delta < total - 1) {
        rangeWithDots.push('...', total)
      } else if (total > 1) {
        rangeWithDots.push(total)
      }

      return rangeWithDots
    })

    const sortIcon = computed(() => {
      return sortAsc.value ? 'arrow_upward' : 'arrow_downward'
    })

    // Conteo de nodos del árbol
    const totalNodos = computed(() => {
      const count = (nodes: any[]): number => {
        return nodes.reduce((acc, node) => {
          return acc + 1 + (node.hijos ? count(node.hijos) : 0)
        }, 0)
      }
      return count(arbolData.value)
    })

    // ============ FUNCIONES API ============

    const fetchAllPaginated = async (url: string, params = {}) => {
      const token = localStorage.getItem('token')
      const config = token ? { headers: { 'Authorization': `Token ${token}` } } : {}

      let allResults: any[] = []
      let currentUrl = url

      if (Object.keys(params).length > 0) {
        const queryParams = new URLSearchParams(params as any).toString()
        currentUrl = `${url}?${queryParams}`
      }

      try {
        const response = await fetch(currentUrl, config)
        const data = await response.json()

        if (Array.isArray(data)) return data

        if (data.results) {
          allResults = [...data.results]
          let nextUrl = data.next

          while (nextUrl) {
            const nextResponse = await fetch(nextUrl, config)
            const nextData = await nextResponse.json()
            if (nextData.results) {
              allResults = [...allResults, ...nextData.results]
            }
            nextUrl = nextData.next
          }
        }

        return allResults
      } catch (err) {
        console.error(`Error fetching ${url}:`, err)
        throw err
      }
    }

    const loadInitialData = async () => {
      try {
        loading.value = true
        error.value = null

        const [deptosData, territorialesData, municipiosConPreopData] = await Promise.allSettled([
          fetchAllPaginated(`${API_URL}/preoperacion/departamentos/`),
          fetchAllPaginated(`${API_URL}/preoperacion/territoriales/`),
          fetchAllPaginated(`${API_URL}/preoperacion/preoperacion-arbol/municipios_con_preoperacion/`)
        ])

        departamentos.value = deptosData.status === 'fulfilled' ? deptosData.value : []
        territoriales.value = territorialesData.status === 'fulfilled' ? territorialesData.value : []

        if (municipiosConPreopData.status === 'fulfilled') {
          todosLosMunicipiosConPreoperacion.value = municipiosConPreopData.value
          municipiosConPreoperacion.value = municipiosConPreopData.value
        }

      } catch (err: any) {
        error.value = 'Error cargando datos iniciales'
        console.error('Error:', err)
      } finally {
        loading.value = false
      }
    }

    // ============ HANDLERS ============

    const debouncedSearch = debounce(() => {
      currentPage.value = 1
    }, 300)

    const sortBy = (field: string) => {
      if (sortField.value === field) {
        sortAsc.value = !sortAsc.value
      } else {
        sortField.value = field
        sortAsc.value = true
      }
      currentPage.value = 1
    }

    const onFilterChange = () => {
      currentPage.value = 1
    }

    const clearSearch = () => {
      searchTerm.value = ''
      currentPage.value = 1
    }

    const clearFilters = () => {
      searchTerm.value = ''
      filters.value = { departamento: '', municipio: '', territorial: '' }
      currentPage.value = 1
    }

    const removeFilter = (tipo: string) => {
      if (tipo === 'departamento') filters.value.departamento = ''
      if (tipo === 'territorial') filters.value.territorial = ''
      if (tipo === 'municipio') filters.value.municipio = ''
      currentPage.value = 1
    }

    const refreshData = () => {
      loadInitialData()
    }

    // Paginación
    const prevPage = () => {
      if (currentPage.value > 1) currentPage.value--
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) currentPage.value++
    }

    const goToPage = (page: number | string) => {
      if (typeof page === 'number' && page >= 1 && page <= totalPages.value) {
        currentPage.value = page
      }
    }

    // ============ ACCIONES ============

    const verDetalle = async (municipio: any) => {
      try {
        loadingMecanismos.value = true
        municipioSeleccionado.value = municipio

        const response = await fetch(`${API_URL}/preoperacion/mecanismos-preoperacion/${municipio.cod_municipio}/`, {
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`
          }
        })

        if (!response.ok) {
          router.push({
            name: 'DisposicionPreoperacionDetalle',
            params: { id: municipio.cod_municipio },
            query: { nombre: municipio.nom_municipio, depto: municipio.nom_depto, territorial: municipio.nom_territorial }
          })
          return
        }

        const data = await response.json()

        if (data.success && data.tiene_multiples) {
          mecanismosDisponibles.value = data.mecanismos
          showMecanismoModal.value = true
        } else {
          const mecanismoCode = data.mecanismos?.length === 1 ? data.mecanismos[0].codigo : undefined
          router.push({
            name: 'DisposicionPreoperacionDetalle',
            params: { id: municipio.cod_municipio },
            query: {
              nombre: municipio.nom_municipio,
              depto: municipio.nom_depto,
              territorial: municipio.nom_territorial,
              ...(mecanismoCode ? { mecanismo: mecanismoCode } : {})
            }
          })
        }
      } catch (error) {
        console.error('Error verificando mecanismos:', error)
        router.push({
          name: 'DisposicionPreoperacionDetalle',
          params: { id: municipio.cod_municipio },
          query: { nombre: municipio.nom_municipio, depto: municipio.nom_depto, territorial: municipio.nom_territorial }
        })
      } finally {
        loadingMecanismos.value = false
      }
    }

    const seleccionarMecanismo = (mecanismo: any) => {
      if (municipioSeleccionado.value) {
        router.push({
          name: 'DisposicionPreoperacionDetalle',
          params: { id: municipioSeleccionado.value.cod_municipio },
          query: {
            nombre: municipioSeleccionado.value.nom_municipio,
            depto: municipioSeleccionado.value.nom_depto,
            territorial: municipioSeleccionado.value.nom_territorial,
            mecanismo: mecanismo.codigo
          }
        })
        closeMecanismoModal()
      }
    }

    const closeMecanismoModal = () => {
      showMecanismoModal.value = false
      municipioSeleccionado.value = null
      mecanismosDisponibles.value = []
    }

    const closeTreeModal = () => {
      showTreeModal.value = false
      selectedMunicipio.value = null
      arbolData.value = []
    }

    const showFileDetails = (node: any) => {
      selectedFile.value = node
      showFileModal.value = true
      copied.value = false
    }

    const closeFileModal = () => {
      showFileModal.value = false
      selectedFile.value = null
    }

    const copyPath = async () => {
      if (selectedFile.value?.ruta_windows) {
        try {
          await navigator.clipboard.writeText(selectedFile.value.ruta_windows)
          copied.value = true
          setTimeout(() => { copied.value = false }, 2000)
          showNotification('Ruta copiada al portapapeles', 'success')
        } catch (err) {
          console.error('Error copiando ruta:', err)
          showNotification('Error al copiar la ruta', 'error')
        }
      }
    }

    const isViewable = (extension: string | null): boolean => {
      if (!extension) return false
      const viewable = ['.pdf', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp']
      return viewable.includes(extension.toLowerCase())
    }

    const viewFile = () => {
      if (selectedFile.value?.ruta_windows) {
        const token = localStorage.getItem('token')
        const url = `/api/file-ops/view/?path=${encodeURIComponent(selectedFile.value.ruta_windows)}&token=${token}`
        window.open(url, '_blank')
      }
    }

    const downloadFile = () => {
      if (selectedFile.value?.ruta_windows) {
        const token = localStorage.getItem('token')
        const url = `/api/file-ops/download/?path=${encodeURIComponent(selectedFile.value.ruta_windows)}&token=${token}`
        window.open(url, '_blank')
      }
    }

    const formatDate = (dateStr: string): string => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleDateString('es-CO', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const exportarDatos = () => {
      if (!canExport.value) {
        showNotification('No tienes permisos para exportar datos', 'error')
        return
      }

      try {
        const headers = ['Código', 'Municipio', 'Departamento', 'Territorial', 'Directorios', 'Archivos', 'Tamaño']
        const data = municipiosFiltered.value.map(m => [
          m.cod_municipio,
          m.nom_municipio,
          getDepartamentoName(m.cod_depto),
          m.nom_territorial || 'N/A',
          m.total_directorios || 0,
          m.total_archivos || 0,
          m.tamano_total || '0 B'
        ])

        const BOM = '\uFEFF'
        const csvContent = BOM + [
          headers.join(','),
          ...data.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
        ].join('\n')

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `preoperacion_municipios_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`

        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)

        showNotification('Datos exportados correctamente', 'success')
      } catch (err) {
        console.error('Error exportando datos:', err)
        showNotification('Error al exportar datos', 'error')
      }
    }

    // ============ UTILIDADES ============

    const getDepartamentoName = (codDepto: number | string): string => {
      const depto = departamentos.value.find(d => d.cod_depto?.toString() === codDepto?.toString())
      return depto ? depto.nom_depto : 'N/A'
    }

    const showNotification = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
      if (notification.value.timeout) {
        clearTimeout(notification.value.timeout)
      }

      const icons: Record<string, string> = { success: 'check_circle', error: 'error', warning: 'warning', info: 'info' }

      notification.value = {
        show: true,
        message,
        type,
        icon: icons[type],
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

    // ============ LIFECYCLE ============

    onMounted(() => {
      loadInitialData()
    })

    return {
      loading,
      error,
      searchTerm,
      filters,
      currentPage,
      totalPages,
      notification,

      // Computed
      userPermissions,
      canExport,
      accessLevelText,
      accessLevelIcon,
      accessLevelClass,
      municipiosFiltered,
      paginatedMunicipios,
      visiblePages,
      sortField,
      sortAsc,
      sortIcon,
      departamentosDisponibles,
      territorialesDisponibles,
      municipiosParaSelector,
      hasActiveFilters,
      filtrosActivos,
      totalMunicipiosBase,
      totalNodos,

      // Data
      departamentos,
      territoriales,

      // Modal árbol
      showTreeModal,
      selectedMunicipio,
      arbolData,
      loadingTree,
      treeError,

      // Modal archivo
      showFileModal,
      selectedFile,
      copied,

      // Methods
      debouncedSearch,
      sortBy,
      onFilterChange,
      clearSearch,
      clearFilters,
      removeFilter,
      refreshData,
      prevPage,
      nextPage,
      goToPage,
      verDetalle,
      closeTreeModal,
      showFileDetails,
      closeFileModal,
      copyPath,
      isViewable,
      viewFile,
      downloadFile,
      formatDate,
      exportarDatos,
      getDepartamentoName,
      showNotification,
      closeNotification,
      // Modal mecanismo
      showMecanismoModal,
      municipioSeleccionado,
      mecanismosDisponibles,
      loadingMecanismos,
      seleccionarMecanismo,
      closeMecanismoModal
    }
  }
})
</script>

<style scoped>
.productos-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
  background-color: #f8f9fa;
  min-height: 100vh;
}

/* ============ HEADER ============ */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 2rem;
  color: white;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-content h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.access-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  backdrop-filter: blur(10px);
}

.access-badge.super-admin {
  background: rgba(220, 53, 69, 0.2);
  border: 1px solid rgba(220, 53, 69, 0.3);
}

.access-badge.admin {
  background: rgba(255, 193, 7, 0.2);
  border: 1px solid rgba(255, 193, 7, 0.3);
}

.access-badge.profesional {
  background: rgba(13, 202, 240, 0.2);
  border: 1px solid rgba(13, 202, 240, 0.3);
}

.access-badge.readonly {
  background: rgba(108, 117, 125, 0.2);
  border: 1px solid rgba(108, 117, 125, 0.3);
}

.btn-export {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.btn-export:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.btn-export:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ============ FILTROS ============ */
.filters-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.search-container {
  margin-bottom: 1rem;
}

.search-box {
  position: relative;
  max-width: 400px;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
  font-size: 1.25rem;
}

.search-box input {
  width: 100%;
  padding: 0.875rem 1rem 0.875rem 3rem;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.search-box input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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
  padding: 0.25rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.clear-btn:hover {
  background-color: rgba(108, 117, 125, 0.1);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  align-items: end;
  margin-bottom: 1rem;
}

.filter-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.25rem;
}

.filters-grid select {
  padding: 0.875rem 1rem;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  background: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.filters-grid select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  outline: none;
}

.filter-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn-clear,
.btn-refresh {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1rem;
  border: none;
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-clear {
  background: #f8f9fa;
  color: #6c757d;
}

.btn-refresh {
  background: #667eea;
  color: white;
}

.btn-clear:hover:not(:disabled) {
  background: #e9ecef;
}

.btn-refresh:hover:not(:disabled) {
  background: #5a6fd8;
  transform: translateY(-2px);
}

.btn-clear:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Filtros activos */
.active-filters {
  border-top: 1px solid #e9ecef;
  padding-top: 1rem;
  margin-top: 1rem;
}

.active-filters h4 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  color: #495057;
  font-weight: 600;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.filter-tag {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.filter-type {
  opacity: 0.8;
}

.filter-value {
  font-weight: 600;
}

.filter-remove {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.filter-remove:hover {
  background: rgba(255, 255, 255, 0.3);
}

.filter-remove i {
  font-size: 14px;
}

/* ============ CONTENIDO ============ */
.content-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

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
  border-top: 4px solid #667eea;
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
  color: #6c757d;
}

.btn-retry {
  padding: 0.75rem 1.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  margin-top: 1rem;
}

/* ============ TABLA ============ */
.table-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
}

.table-header h3 {
  margin: 0;
  color: #343a40;
  font-size: 1.25rem;
  font-weight: 600;
}

.filter-result {
  font-size: 0.875rem;
  color: #6c757d;
  font-weight: 400;
}

.table-responsive {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  padding: 1rem;
  background: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
  font-weight: 600;
  color: #495057;
  text-align: left;
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

.data-table th.sortable i {
  margin-left: 0.5rem;
  font-size: 1rem;
}

.data-table td {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
  vertical-align: middle;
}

.data-table tbody tr:hover {
  background: rgba(102, 126, 234, 0.05);
}

.text-center {
  text-align: center;
}

.municipio-name {
  font-weight: 600;
  color: #343a40;
}

.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2rem;
  height: 2rem;
  padding: 0 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 6px;
  color: white;
}

.badge-info {
  background: linear-gradient(135deg, #17a2b8, #138496);
}

.badge-primary {
  background: linear-gradient(135deg, #667eea, #5a6fd8);
}

.badge-success {
  background: linear-gradient(135deg, #28a745, #1e7e34);
}

.actions {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn.view {
  background: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
}

.action-btn.view:hover {
  background: rgba(13, 110, 253, 0.2);
  transform: scale(1.1);
}

/* ============ PAGINACIÓN ============ */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem;
  border-top: 1px solid #e9ecef;
  background: #f8f9fa;
}

.page-btn,
.page-num {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 2.5rem;
  height: 2.5rem;
  border: 1px solid #dee2e6;
  background: white;
  color: #495057;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.page-btn:hover:not(:disabled),
.page-num:hover {
  background: #e9ecef;
  border-color: #adb5bd;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-num.active {
  background: #667eea;
  border-color: #667eea;
  color: white;
}

/* ============ MODAL ============ */
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
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-content.modal-large {
  max-width: 1100px;
  width: 95%;
  max-height: 90vh;
  min-height: 600px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.modal-header h3 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 1.125rem;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
  justify-content: flex-end;
}

/* Detalles archivo */
.detail-row {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 1rem;
}

.detail-row label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #6c757d;
  text-transform: uppercase;
}

.detail-row span {
  font-size: 0.9rem;
  color: #333;
}

.source-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.source-badge.insumos {
  background: #e8f5e9;
  color: #2e7d32;
}

.source-badge.preoperacion {
  background: #e3f2fd;
  color: #1565c0;
}

.path-container {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
}

.path-text {
  flex: 1;
  padding: 0.5rem;
  background: #f5f5f5;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.8rem;
  word-break: break-all;
}

.copy-btn {
  padding: 0.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.copy-btn:hover {
  background: #5a6fd8;
}

.extension-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  background: #e9ecef;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.8rem;
}

.btn-primary,
.btn-secondary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5a6fd8;
}

.btn-secondary {
  background: #e9ecef;
  color: #333;
}

.btn-secondary:hover {
  background: #dee2e6;
}

/* ============ ÁRBOL ============ */
.tree-wrapper {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
}

.tree-stats {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  font-size: 0.875rem;
  color: #666;
}

.tree-stats i {
  font-size: 1rem;
}

.tree-content {
  padding: 1rem;
  max-height: calc(90vh - 200px);
  min-height: 400px;
  overflow-y: auto;
  overflow-x: auto;
  background: #fafbfc;
  border-radius: 8px;
}

/* TreeNode styles */
:deep(.tree-node) {
  margin: 2px 0;
}

:deep(.node-content) {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

:deep(.node-content:hover) {
  background: #f0f4ff;
}

:deep(.expand-icon),
:deep(.expand-placeholder) {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.expand-icon .material-icons) {
  font-size: 20px;
  color: #666;
}

:deep(.node-icon) {
  font-size: 20px;
  color: #667eea;
}

:deep(.is-file .node-icon) {
  color: #666;
}

:deep(.node-name) {
  flex: 1;
  font-size: 0.875rem;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:deep(.file-count) {
  font-size: 0.75rem;
  color: #888;
}

:deep(.source-tag) {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
}

:deep(.source-tag.insumos) {
  background: #e8f5e9;
  color: #2e7d32;
}

:deep(.source-tag.preoperacion) {
  background: #e3f2fd;
  color: #1565c0;
}

:deep(.details-btn) {
  padding: 4px;
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s;
}

:deep(.details-btn:hover) {
  opacity: 1;
}

:deep(.details-btn .material-icons) {
  font-size: 18px;
  color: #667eea;
}

:deep(.children) {
  margin-left: 0;
  border-left: 1px dashed #e0e0e0;
  margin-top: 2px;
}

:deep(.is-directory > .node-content:hover),
:deep(.is-category > .node-content:hover) {
  background: #e8f0fe;
}

:deep(.is-file > .node-content:hover) {
  background: #fff3e0;
}

/* Colores por nivel */
:deep(.tree-node[style*="padding-left: 0px"] > .node-content .node-icon) {
  color: #1a73e8;
}

:deep(.tree-node[style*="padding-left: 20px"] > .node-content .node-icon) {
  color: #34a853;
}

:deep(.tree-node[style*="padding-left: 40px"] > .node-content .node-icon) {
  color: #fbbc04;
}

:deep(.tree-node[style*="padding-left: 60px"] > .node-content .node-icon) {
  color: #ea4335;
}

/* ============ NOTIFICACIÓN ============ */
.notification {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  min-width: 300px;
  max-width: 400px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  z-index: 1100;
  display: flex;
  align-items: center;
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
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
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification.success {
  border-left: 4px solid #28a745;
}

.notification.success i {
  color: #28a745;
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
  border-left: 4px solid #17a2b8;
}

.notification.info i {
  color: #17a2b8;
}

/* ============ RESPONSIVE ============ */
@media (max-width: 768px) {
  .productos-page {
    padding: 1rem;
    gap: 1rem;
  }

  .page-header {
    padding: 1.5rem;
  }

  .header-content {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }

  .header-content h1 {
    font-size: 1.5rem;
  }

  .filters-grid {
    grid-template-columns: 1fr;
  }

  .filter-actions {
    justify-content: center;
  }

  .filter-tags {
    justify-content: center;
  }

  .data-table {
    font-size: 0.875rem;
  }

  .data-table th,
  .data-table td {
    padding: 0.75rem 0.5rem;
  }

  .notification {
    left: 1rem;
    right: 1rem;
    min-width: auto;
  }

  .modal-content.modal-large {
    max-width: 95%;
  }
}

/* Modal Mecanismo de Financiación */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}
.modal-mecanismo {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
  animation: modalSlideIn 0.3s ease;
}
@keyframes modalSlideIn {
  from { opacity: 0; transform: translateY(-20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.modal-header-mec {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  background: linear-gradient(135deg, #667eea, #5a67d8);
  color: white;
}
.modal-header-mec h3 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}
.modal-close-mec {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 32px; height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.modal-close-mec:hover { background: rgba(255, 255, 255, 0.3); }
.modal-body-mec {
  padding: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
}
.modal-subtitle-mec {
  color: #64748b;
  margin-bottom: 1.25rem;
  line-height: 1.5;
}
.modal-subtitle-mec strong { color: #5a67d8; }
.loading-mecanismos {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
  color: #64748b;
}
.spinner-small-mec {
  width: 24px; height: 24px;
  border: 3px solid #e2e8f0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spinMec 0.8s linear infinite;
}
@keyframes spinMec { to { transform: rotate(360deg); } }
.mecanismos-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.mecanismo-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.mecanismo-option:hover {
  border-color: #667eea;
  background: linear-gradient(135deg, #eef2ff, #e0e7ff);
  transform: translateX(4px);
}
.mecanismo-option:hover .material-icons { color: #667eea; }
.mecanismo-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.mecanismo-codigo {
  font-weight: 700;
  font-size: 1.1rem;
  color: #5a67d8;
}
.mecanismo-stats {
  font-size: 0.85rem;
  color: #64748b;
}
.mecanismo-option .material-icons {
  color: #94a3b8;
  transition: all 0.2s;
}
.modal-footer-mec {
  display: flex;
  justify-content: flex-end;
  padding: 1rem 1.5rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}
.btn-cancel-mec {
  padding: 0.5rem 1.25rem;
  background: #e2e8f0;
  border: none;
  border-radius: 6px;
  color: #64748b;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-cancel-mec:hover {
  background: #cbd5e1;
  color: #475569;
}
</style>
