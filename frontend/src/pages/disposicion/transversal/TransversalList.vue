<template>
  <div class="productos-page">
    <!-- Header -->
    <header class="page-header transversal-header">
      <div class="header-content">
        <h1>Transversal</h1>
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

    <!-- Filtros -->
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
        <!-- Filtro Departamento -->
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

        <!-- Filtro Territorial -->
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

        <!-- Filtro Municipio -->
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

        <!-- Acciones -->
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

      <!-- Filtros activos -->
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
        <span>Cargando municipios con transversal...</span>
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
        <p>No se encontraron municipios con transversal con los filtros aplicados</p>
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

    <!-- Notificación -->
    <transition name="notification">
      <div v-if="notification.show" :class="['notification', notification.type]">
        <i class="material-icons">{{ notification.icon }}</i>
        <span>{{ notification.message }}</span>
      </div>
    </transition>

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

export default defineComponent({
  name: 'TransversalList',

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
    const municipiosConTransversal = ref<any[]>([])
    const todosLosMunicipiosConTransversal = ref<any[]>([])

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

    // Permisos
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

    // Municipios asignados para profesionales
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

    // Filtros acumulativos
    const municipiosFiltradosBase = computed(() => {
      let result = [...todosLosMunicipiosConTransversal.value]

      if (userPermissions.value.isProfesional && !userPermissions.value.isAnyAdmin) {
        const asignados = municipiosAsignados.value
        if (asignados.length > 0) {
          result = result.filter(m =>
            asignados.includes(String(m.cod_municipio))
          )
        }
      }

      if (filters.value.departamento) {
        result = result.filter(m =>
          m.cod_depto?.toString() === filters.value.departamento.toString()
        )
      }

      if (filters.value.territorial) {
        result = result.filter(m =>
          m.nom_territorial === filters.value.territorial
        )
      }

      if (filters.value.municipio) {
        result = result.filter(m =>
          m.cod_municipio?.toString() === filters.value.municipio.toString()
        )
      }

      return result
    })

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

    const departamentosDisponibles = computed(() => {
      let municipiosBase = [...todosLosMunicipiosConTransversal.value]

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

    const territorialesDisponibles = computed(() => {
      let municipiosBase = [...todosLosMunicipiosConTransversal.value]

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

    const municipiosParaSelector = computed(() => {
      let municipiosBase = [...todosLosMunicipiosConTransversal.value]

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

    const hasActiveFilters = computed(() => {
      return !!(filters.value.departamento || filters.value.territorial || filters.value.municipio)
    })

    const filtrosActivos = computed(() => {
      const activos = []
      if (filters.value.departamento) {
        const dpto = departamentos.value.find(d => d.cod_depto?.toString() === filters.value.departamento.toString())
        activos.push({ tipo: 'departamento', valor: dpto?.nom_depto || filters.value.departamento })
      }
      if (filters.value.territorial) {
        activos.push({ tipo: 'territorial', valor: filters.value.territorial })
      }
      if (filters.value.municipio) {
        const mun = todosLosMunicipiosConTransversal.value.find(m => m.cod_municipio?.toString() === filters.value.municipio.toString())
        activos.push({ tipo: 'municipio', valor: mun?.nom_municipio || filters.value.municipio })
      }
      return activos
    })

    const totalMunicipiosBase = computed(() => todosLosMunicipiosConTransversal.value.length)

    // Ordenamiento
    const municipiosSorted = computed(() => {
      return [...municipiosFiltered.value].sort((a, b) => {
        const aVal = a[sortField.value] || ''
        const bVal = b[sortField.value] || ''
        const result = String(aVal).localeCompare(String(bVal), 'es', { numeric: true })
        return sortAsc.value ? result : -result
      })
    })

    const sortIcon = computed(() => sortAsc.value ? 'arrow_upward' : 'arrow_downward')

    // Paginación
    const totalPages = computed(() => Math.ceil(municipiosSorted.value.length / pageSize.value))

    const paginatedMunicipios = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      return municipiosSorted.value.slice(start, start + pageSize.value)
    })

    const visiblePages = computed(() => {
      const pages = []
      const total = totalPages.value
      const current = currentPage.value

      if (total <= 7) {
        for (let i = 1; i <= total; i++) pages.push(i)
      } else {
        pages.push(1)
        if (current > 3) pages.push('...')
        for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) {
          pages.push(i)
        }
        if (current < total - 2) pages.push('...')
        pages.push(total)
      }

      return pages
    })

    // Helpers
    const getDepartamentoName = (codDepto: number) => {
      const dpto = departamentos.value.find(d => d.cod_depto === codDepto)
      return dpto?.nom_depto || 'N/A'
    }

    // Fetch de datos
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

        const [deptosData, territorialesData, municipiosConTransvData] = await Promise.allSettled([
          fetchAllPaginated(`${API_URL}/preoperacion/departamentos/`),
          fetchAllPaginated(`${API_URL}/preoperacion/territoriales/`),
          fetchAllPaginated(`${API_URL}/app/api/transversal-arbol/municipios_con_transversal/`)
        ])

        departamentos.value = deptosData.status === 'fulfilled' ? deptosData.value : []
        territoriales.value = territorialesData.status === 'fulfilled' ? territorialesData.value : []

        if (municipiosConTransvData.status === 'fulfilled') {
          todosLosMunicipiosConTransversal.value = municipiosConTransvData.value
          municipiosConTransversal.value = municipiosConTransvData.value
        }

      } catch (err: any) {
        error.value = 'Error cargando datos iniciales'
        console.error('Error:', err)
      } finally {
        loading.value = false
      }
    }

    // Handlers
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

    // Acciones
    const verDetalle = async (municipio: any) => {
      try {
        loadingMecanismos.value = true
        municipioSeleccionado.value = municipio

        const response = await fetch(`${API_URL}/app/api/mecanismos-transversal/${municipio.cod_municipio}/`, {
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`
          }
        })

        if (!response.ok) {
          router.push({
            name: 'DisposicionTransversalDetalle',
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
            name: 'DisposicionTransversalDetalle',
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
          name: 'DisposicionTransversalDetalle',
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
          name: 'DisposicionTransversalDetalle',
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

    const showNotification = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
      if (notification.value.timeout) {
        clearTimeout(notification.value.timeout)
      }

      const icons: Record<string, string> = {
        success: 'check_circle',
        error: 'error',
        warning: 'warning',
        info: 'info'
      }

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

    const exportarDatos = () => {
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
          ...data.map(row => row.map(cell => `"${cell}"`).join(','))
        ].join('\n')

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `transversal_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`
        link.click()
        URL.revokeObjectURL(url)

        showNotification('Datos exportados exitosamente', 'success')
      } catch (err) {
        console.error('Error exportando:', err)
        showNotification('Error al exportar datos', 'error')
      }
    }

    onMounted(() => {
      loadInitialData()
    })

    return {
      // Estado
      loading,
      error,
      searchTerm,
      filters,
      sortField,
      sortAsc,
      currentPage,
      pageSize,
      notification,

      // Datos
      departamentos,
      municipiosFiltered,
      paginatedMunicipios,

      // Computados
      canExport,
      accessLevelText,
      accessLevelIcon,
      accessLevelClass,
      departamentosDisponibles,
      territorialesDisponibles,
      municipiosParaSelector,
      hasActiveFilters,
      filtrosActivos,
      totalMunicipiosBase,
      sortIcon,
      totalPages,
      visiblePages,

      // Métodos
      getDepartamentoName,
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
      exportarDatos,
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
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  padding: 1.5rem;
}

.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.page-header.transversal-header {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-content h1 {
  color: white;
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
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
}

.btn-export {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: white;
  border: none;
  border-radius: 8px;
  color: #11998e;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-export:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-export:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.filters-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.search-container {
  margin-bottom: 1rem;
}

.search-box {
  display: flex;
  align-items: center;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  gap: 0.5rem;
}

.search-box input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 1rem;
  outline: none;
}

.clear-btn {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
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
}

.filter-container select {
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  font-size: 0.9rem;
  background: white;
  cursor: pointer;
}

.filter-actions {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
}

.btn-clear,
.btn-refresh {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-clear {
  background: #f8f9fa;
  color: #495057;
}

.btn-refresh {
  background: #11998e;
  color: white;
}

.btn-clear:hover:not(:disabled),
.btn-refresh:hover:not(:disabled) {
  transform: translateY(-1px);
}

.btn-clear:disabled,
.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.active-filters {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #dee2e6;
}

.active-filters h4 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #495057;
  margin: 0 0 0.75rem 0;
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
  background: linear-gradient(135deg, #11998e, #38ef7d);
  color: white;
  border-radius: 20px;
  font-size: 0.875rem;
}

.filter-remove {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
}

.filter-remove i {
  font-size: 1rem;
}

.content-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
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
  gap: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #11998e;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container i,
.empty-container i {
  font-size: 3rem;
  color: #6c757d;
}

.btn-retry {
  padding: 0.75rem 1.5rem;
  background: #11998e;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

.table-header {
  margin-bottom: 1rem;
}

.table-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #495057;
}

.filter-result {
  font-weight: normal;
  color: #6c757d;
}

.table-responsive {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #dee2e6;
}

.data-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.data-table th.sortable:hover {
  background: #e9ecef;
}

.data-table th i {
  font-size: 0.875rem;
  vertical-align: middle;
  margin-left: 0.25rem;
}

.data-table tbody tr:hover {
  background: #f8f9fa;
}

.text-center {
  text-align: center;
}

.municipio-name {
  font-weight: 500;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
  color: white;
}

.badge-info {
  background: linear-gradient(135deg, #17a2b8, #138496);
}

.badge-primary {
  background: linear-gradient(135deg, #11998e, #0d7d74);
}

.badge-success {
  background: linear-gradient(135deg, #28a745, #1e7e34);
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn.view {
  background: linear-gradient(135deg, #11998e, #38ef7d);
  color: white;
}

.action-btn:hover {
  transform: scale(1.1);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #dee2e6;
}

.page-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled) {
  background: #11998e;
  color: white;
  border-color: #11998e;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-num {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 36px;
  padding: 0 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-num:hover {
  background: #f8f9fa;
}

.page-num.active {
  background: #11998e;
  color: white;
}

.notification {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
}

.notification.success {
  background: #28a745;
}

.notification.error {
  background: #dc3545;
}

.notification.warning {
  background: #ffc107;
  color: #212529;
}

.notification.info {
  background: #17a2b8;
}

.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from,
.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

@media (max-width: 768px) {
  .productos-page {
    padding: 1rem;
  }

  .header-content {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }

  .header-actions {
    justify-content: center;
  }

  .filters-grid {
    grid-template-columns: 1fr;
  }

  .data-table th,
  .data-table td {
    padding: 0.75rem 0.5rem;
    font-size: 0.875rem;
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
  background: linear-gradient(135deg, #11998e, #0d7d74);
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
.modal-subtitle-mec strong { color: #0d7d74; }
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
  border-top-color: #11998e;
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
  border-color: #11998e;
  background: linear-gradient(135deg, #f0fdf4, #dcfce7);
  transform: translateX(4px);
}
.mecanismo-option:hover .material-icons { color: #11998e; }
.mecanismo-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.mecanismo-codigo {
  font-weight: 700;
  font-size: 1.1rem;
  color: #0d7d74;
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
