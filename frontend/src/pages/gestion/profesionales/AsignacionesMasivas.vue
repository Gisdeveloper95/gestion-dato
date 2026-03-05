<template>
  <div class="asignaciones-masivas-page">
    <!-- Cabecera -->
    <div class="page-header">
      <div class="header-content">
        <h1>Asignaciones Masivas</h1>
        <button @click="goBack" class="btn-outline">
          <i class="material-icons">arrow_back</i>
          Volver
        </button>
      </div>
      <p class="header-subtitle">Asigne múltiples municipios a múltiples profesionales de manera eficiente</p>
    </div>

    <!-- Contenido principal -->
    <div class="main-content">
      <!-- PASO 1: Selección de Profesionales -->
      <div class="step-card">
        <div class="step-header">
          <span class="step-number">1</span>
          <h2>Seleccionar Profesionales</h2>
          <span class="selected-count" v-if="profesionalesSeleccionados.length > 0">
            {{ profesionalesSeleccionados.length }} seleccionados
          </span>
        </div>

        <div class="step-content">
          <!-- Filtros -->
          <div class="filters-row">
            <div class="filter-group">
              <label>Filtrar por Rol</label>
              <select v-model="filtroRol">
                <option value="">Todos los roles</option>
                <option v-for="rol in rolesDisponibles" :key="rol" :value="rol">
                  {{ rol }}
                </option>
              </select>
            </div>
            <div class="filter-group">
              <label>Filtrar por Territorial</label>
              <select v-model="filtroTerritorial">
                <option value="">Todas las territoriales</option>
                <option v-for="t in territorialesDisponibles" :key="t" :value="t">
                  {{ t }}
                </option>
              </select>
            </div>
            <div class="filter-group search">
              <label>Buscar</label>
              <input type="text" v-model="busqueda" placeholder="Nombre o código...">
            </div>
          </div>

          <!-- Acciones rápidas -->
          <div class="quick-actions">
            <button @click="seleccionarTodos" class="btn-link">
              <i class="material-icons">select_all</i> Seleccionar todos
            </button>
            <button @click="deseleccionarTodos" class="btn-link">
              <i class="material-icons">deselect</i> Deseleccionar todos
            </button>
          </div>

          <!-- Lista de profesionales -->
          <div class="profesionales-list">
            <div
              v-for="profesional in profesionalesFiltrados"
              :key="profesional.cod_profesional"
              :class="['profesional-item', { selected: isSelected(profesional) }]"
              @click="toggleProfesional(profesional)"
            >
              <input
                type="checkbox"
                :checked="isSelected(profesional)"
                @click.stop
                @change="toggleProfesional(profesional)"
              >
              <div class="profesional-info">
                <span class="profesional-nombre">{{ profesional.nombre_profesional }}</span>
                <span class="profesional-meta">
                  {{ profesional.cod_profesional }}
                  <span class="separator">|</span>
                  {{ profesional.rol_profesional }}
                </span>
              </div>
            </div>
            <div v-if="profesionalesFiltrados.length === 0" class="empty-state">
              <i class="material-icons">search_off</i>
              <p>No se encontraron profesionales con los filtros aplicados</p>
            </div>
          </div>
        </div>
      </div>

      <!-- PASO 2: Método de Asignación -->
      <div class="step-card">
        <div class="step-header">
          <span class="step-number">2</span>
          <h2>Seleccionar Municipios</h2>
          <span class="selected-count" v-if="municipiosParaAsignar.length > 0">
            {{ municipiosParaAsignar.length }} municipios
          </span>
        </div>

        <div class="step-content">
          <!-- Opciones de método -->
          <div class="method-options">
            <!-- Opción: Por Territorial -->
            <div
              :class="['method-option', { active: metodoAsignacion === 'territorial' }]"
              @click="metodoAsignacion = 'territorial'"
            >
              <div class="method-radio">
                <input type="radio" v-model="metodoAsignacion" value="territorial">
              </div>
              <div class="method-content">
                <h3>Por Territorial</h3>
                <p>Asignar todos los municipios de una territorial</p>

                <div v-if="metodoAsignacion === 'territorial'" class="method-form">
                  <select v-model="territorialSeleccionada">
                    <option value="">Seleccione una territorial</option>
                    <option v-for="t in territoriales" :key="t.nom_territorial" :value="t.nom_territorial">
                      {{ t.nom_territorial }}
                    </option>
                  </select>
                  <div v-if="territorialSeleccionada" class="method-preview">
                    <i class="material-icons">info</i>
                    <span>{{ municipiosPorTerritorial.length }} municipios serán asignados</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Opción: Por Códigos DIVIPOLA -->
            <div
              :class="['method-option', { active: metodoAsignacion === 'divipola' }]"
              @click="metodoAsignacion = 'divipola'"
            >
              <div class="method-radio">
                <input type="radio" v-model="metodoAsignacion" value="divipola">
              </div>
              <div class="method-content">
                <h3>Por Códigos DIVIPOLA</h3>
                <p>Ingrese códigos de 5 dígitos separados por coma, tabulación o salto de línea</p>

                <div v-if="metodoAsignacion === 'divipola'" class="method-form">
                  <textarea
                    v-model="codigosDivipola"
                    placeholder="Ej: 05001, 05002, 08001&#10;11001&#10;15001"
                    rows="4"
                  ></textarea>
                  <div class="divipola-stats">
                    <span class="stat valid">
                      <i class="material-icons">check_circle</i>
                      {{ codigosValidos.length }} válidos
                    </span>
                    <span class="stat invalid" v-if="codigosInvalidos.length > 0">
                      <i class="material-icons">error</i>
                      {{ codigosInvalidos.length }} inválidos
                    </span>
                  </div>
                  <div v-if="codigosInvalidos.length > 0" class="invalid-codes">
                    <small>Códigos no encontrados: {{ codigosInvalidos.join(', ') }}</small>
                  </div>
                </div>
              </div>
            </div>

            <!-- Opción: Selección Manual -->
            <div
              :class="['method-option', { active: metodoAsignacion === 'manual' }]"
              @click="metodoAsignacion = 'manual'"
            >
              <div class="method-radio">
                <input type="radio" v-model="metodoAsignacion" value="manual">
              </div>
              <div class="method-content">
                <h3>Selección Manual</h3>
                <p>Seleccione municipios individualmente por departamento</p>

                <div v-if="metodoAsignacion === 'manual'" class="method-form">
                  <select v-model="deptoSeleccionado">
                    <option value="">Seleccione departamento</option>
                    <option v-for="d in departamentos" :key="d.cod_depto" :value="d.cod_depto">
                      {{ d.nom_depto }}
                    </option>
                  </select>

                  <div v-if="deptoSeleccionado" class="municipios-multiselect">
                    <div class="multiselect-actions">
                      <button @click="seleccionarTodosMunicipios" class="btn-link">
                        Seleccionar todos
                      </button>
                      <button @click="municipiosSeleccionados = []" class="btn-link">
                        Limpiar
                      </button>
                    </div>
                    <div class="municipios-grid">
                      <label
                        v-for="m in municipiosPorDepto"
                        :key="m.cod_municipio"
                        class="municipio-checkbox"
                      >
                        <input
                          type="checkbox"
                          :value="m.cod_municipio"
                          v-model="municipiosSeleccionados"
                        >
                        <span>{{ m.nom_municipio }} ({{ m.cod_municipio }})</span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- PASO 3: Confirmación -->
      <div class="step-card confirmation">
        <div class="step-header">
          <span class="step-number">3</span>
          <h2>Confirmar Asignación</h2>
        </div>

        <div class="step-content">
          <div class="confirmation-summary">
            <div class="summary-item">
              <i class="material-icons">people</i>
              <div>
                <strong>{{ profesionalesSeleccionados.length }}</strong>
                <span>Profesionales</span>
              </div>
            </div>
            <div class="summary-operator">×</div>
            <div class="summary-item">
              <i class="material-icons">location_on</i>
              <div>
                <strong>{{ municipiosParaAsignar.length }}</strong>
                <span>Municipios</span>
              </div>
            </div>
            <div class="summary-operator">=</div>
            <div class="summary-item total">
              <i class="material-icons">assignment</i>
              <div>
                <strong>{{ totalAsignaciones }}</strong>
                <span>Asignaciones</span>
              </div>
            </div>
          </div>

          <div class="confirmation-note">
            <i class="material-icons">info</i>
            <span>Los municipios que ya estén asignados serán ignorados automáticamente.</span>
          </div>

          <div class="confirmation-actions">
            <button @click="goBack" class="btn-outline">
              Cancelar
            </button>
            <button
              @click="ejecutarAsignacion"
              class="btn-primary"
              :disabled="!puedeEjecutar || loading"
            >
              <i class="material-icons" v-if="loading">hourglass_empty</i>
              <i class="material-icons" v-else>rocket_launch</i>
              {{ loading ? 'Procesando...' : 'Ejecutar Asignación' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Notificación -->
    <div v-if="notification.show" :class="['notification', notification.type]">
      <i class="material-icons">{{ notification.icon }}</i>
      <span>{{ notification.message }}</span>
    </div>

    <!-- Modal de resultados -->
    <div v-if="showResults" class="modal-overlay" @click.self="closeResults">
      <div class="modal-content results-modal">
        <div class="modal-header">
          <h3>Resultado de la Asignación</h3>
          <button @click="closeResults" class="btn-icon">
            <i class="material-icons">close</i>
          </button>
        </div>
        <div class="modal-body">
          <div class="results-grid">
            <div class="result-item success">
              <i class="material-icons">check_circle</i>
              <strong>{{ resultados.creados }}</strong>
              <span>Asignaciones creadas</span>
            </div>
            <div class="result-item info">
              <i class="material-icons">info</i>
              <strong>{{ resultados.duplicados }}</strong>
              <span>Ya existían (ignorados)</span>
            </div>
            <div class="result-item" v-if="resultados.errores && resultados.errores.length > 0">
              <i class="material-icons">error</i>
              <strong>{{ resultados.errores.length }}</strong>
              <span>Errores</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeResults" class="btn-outline">Cerrar</button>
          <button @click="nuevaAsignacion" class="btn-primary">Nueva Asignación</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/config'

export default defineComponent({
  name: 'AsignacionesMasivas',

  setup() {
    const router = useRouter()

    // Estado general
    const loading = ref(false)

    // Datos
    const profesionales = ref<any[]>([])
    const territoriales = ref<any[]>([])
    const departamentos = ref<any[]>([])
    const municipios = ref<any[]>([])
    const profesionalTerritorial = ref<any[]>([])

    // Selección de profesionales
    const profesionalesSeleccionados = ref<any[]>([])
    const filtroRol = ref('')
    const filtroTerritorial = ref('')
    const busqueda = ref('')

    // Método de asignación
    const metodoAsignacion = ref<'territorial' | 'divipola' | 'manual'>('territorial')
    const territorialSeleccionada = ref('')
    const codigosDivipola = ref('')
    const deptoSeleccionado = ref('')
    const municipiosSeleccionados = ref<number[]>([])

    // Resultados
    const showResults = ref(false)
    const resultados = ref({
      creados: 0,
      duplicados: 0,
      errores: [] as string[],
      total_intentos: 0
    })

    // Notificación
    const notification = ref({
      show: false,
      message: '',
      type: 'success',
      icon: 'check_circle'
    })

    // Cargar datos iniciales
    onMounted(async () => {
      await loadInitialData()
    })

    const loadInitialData = async () => {
      try {
        loading.value = true

        const [
          profesionalesData,
          territorialesData,
          departamentosData,
          municipiosData,
          profTerritorialData
        ] = await Promise.all([
          api.get('/preoperacion/profesionales-seguimiento/'),
          api.get('/preoperacion/territoriales/'),
          api.get('/preoperacion/departamentos/'),
          api.get('/preoperacion/municipios/'),
          api.get('/preoperacion/profesional-territorial/')
        ])

        profesionales.value = procesarDatos(profesionalesData)
        territoriales.value = procesarDatos(territorialesData)
        departamentos.value = procesarDatos(departamentosData)
        municipios.value = procesarDatos(municipiosData)
        profesionalTerritorial.value = procesarDatos(profTerritorialData)

      } catch (err) {
        console.error('Error cargando datos:', err)
        showNotification('Error cargando datos', 'error')
      } finally {
        loading.value = false
      }
    }

    const procesarDatos = (response: any) => {
      if (response && response.results && Array.isArray(response.results)) {
        return response.results
      }
      return Array.isArray(response) ? response : []
    }

    // Computed: Roles disponibles
    const rolesDisponibles = computed(() => {
      const roles = new Set(profesionales.value.map(p => p.rol_profesional))
      return Array.from(roles).filter(r => r)
    })

    // Computed: Territoriales de los profesionales
    const territorialesDisponibles = computed(() => {
      const terrs = new Set<string>()
      profesionalTerritorial.value.forEach(pt => {
        if (pt.territorial_seguimiento) {
          terrs.add(pt.territorial_seguimiento)
        }
      })
      return Array.from(terrs)
    })

    // Computed: Profesionales filtrados
    const profesionalesFiltrados = computed(() => {
      let filtered = [...profesionales.value]

      if (filtroRol.value) {
        filtered = filtered.filter(p => p.rol_profesional === filtroRol.value)
      }

      if (filtroTerritorial.value) {
        const profsEnTerritorial = profesionalTerritorial.value
          .filter(pt => pt.territorial_seguimiento === filtroTerritorial.value)
          .map(pt => pt.cod_profesional)
        filtered = filtered.filter(p => profsEnTerritorial.includes(p.cod_profesional))
      }

      if (busqueda.value) {
        const search = busqueda.value.toLowerCase()
        filtered = filtered.filter(p =>
          p.nombre_profesional?.toLowerCase().includes(search) ||
          p.cod_profesional?.toLowerCase().includes(search)
        )
      }

      return filtered
    })

    // Computed: Municipios por territorial
    const municipiosPorTerritorial = computed(() => {
      if (!territorialSeleccionada.value) return []
      return municipios.value.filter(m => m.nom_territorial === territorialSeleccionada.value)
    })

    // Computed: Municipios por departamento
    const municipiosPorDepto = computed(() => {
      if (!deptoSeleccionado.value) return []
      return municipios.value.filter(m =>
        m.cod_depto?.toString() === deptoSeleccionado.value?.toString()
      )
    })

    // Computed: Códigos DIVIPOLA parseados
    const codigosParsed = computed(() => {
      if (!codigosDivipola.value) return []
      return codigosDivipola.value
        .split(/[,\t\n\s]+/)
        .map(c => parseInt(c.trim()))
        .filter(c => !isNaN(c) && c >= 10000 && c <= 99999)
    })

    const codigosValidos = computed(() => {
      const codsMunicipios = municipios.value.map(m => m.cod_municipio)
      return codigosParsed.value.filter(c => codsMunicipios.includes(c))
    })

    const codigosInvalidos = computed(() => {
      const codsMunicipios = municipios.value.map(m => m.cod_municipio)
      return codigosParsed.value.filter(c => !codsMunicipios.includes(c))
    })

    // Computed: Municipios para asignar según método
    const municipiosParaAsignar = computed(() => {
      if (metodoAsignacion.value === 'territorial') {
        return municipiosPorTerritorial.value
      } else if (metodoAsignacion.value === 'divipola') {
        return municipios.value.filter(m => codigosValidos.value.includes(m.cod_municipio))
      } else {
        return municipios.value.filter(m => municipiosSeleccionados.value.includes(m.cod_municipio))
      }
    })

    // Computed: Total de asignaciones
    const totalAsignaciones = computed(() => {
      return profesionalesSeleccionados.value.length * municipiosParaAsignar.value.length
    })

    // Computed: Puede ejecutar
    const puedeEjecutar = computed(() => {
      return profesionalesSeleccionados.value.length > 0 && municipiosParaAsignar.value.length > 0
    })

    // Métodos de selección de profesionales
    const isSelected = (profesional: any) => {
      return profesionalesSeleccionados.value.some(p => p.cod_profesional === profesional.cod_profesional)
    }

    const toggleProfesional = (profesional: any) => {
      const index = profesionalesSeleccionados.value.findIndex(p => p.cod_profesional === profesional.cod_profesional)
      if (index >= 0) {
        profesionalesSeleccionados.value.splice(index, 1)
      } else {
        profesionalesSeleccionados.value.push(profesional)
      }
    }

    const seleccionarTodos = () => {
      profesionalesSeleccionados.value = [...profesionalesFiltrados.value]
    }

    const deseleccionarTodos = () => {
      profesionalesSeleccionados.value = []
    }

    const seleccionarTodosMunicipios = () => {
      municipiosSeleccionados.value = municipiosPorDepto.value.map(m => m.cod_municipio)
    }

    // Ejecutar asignación
    const ejecutarAsignacion = async () => {
      if (!puedeEjecutar.value) return

      try {
        loading.value = true

        // Preparar payload
        const payload: any = {
          profesionales: profesionalesSeleccionados.value.map(p => p.cod_profesional),
          municipios: municipiosParaAsignar.value.map(m => m.cod_municipio)
        }

        // Si el método es por territorial, incluir la territorial para asignarla también
        if (metodoAsignacion.value === 'territorial' && territorialSeleccionada.value) {
          payload.territorial = territorialSeleccionada.value
        }

        const response = await api.post('/preoperacion/profesional-municipio/bulk/', payload)

        resultados.value = response
        showResults.value = true

      } catch (err: any) {
        console.error('Error ejecutando asignación:', err)
        showNotification('Error al ejecutar la asignación', 'error')
      } finally {
        loading.value = false
      }
    }

    // Notificación
    const showNotification = (message: string, type: 'success' | 'error' = 'success') => {
      notification.value = {
        show: true,
        message,
        type,
        icon: type === 'success' ? 'check_circle' : 'error'
      }
      setTimeout(() => {
        notification.value.show = false
      }, 3000)
    }

    // Navegación
    const goBack = () => {
      router.back()
    }

    const closeResults = () => {
      showResults.value = false
    }

    const nuevaAsignacion = () => {
      showResults.value = false
      profesionalesSeleccionados.value = []
      territorialSeleccionada.value = ''
      codigosDivipola.value = ''
      municipiosSeleccionados.value = []
    }

    return {
      loading,
      profesionales,
      territoriales,
      departamentos,
      municipios,
      profesionalesSeleccionados,
      filtroRol,
      filtroTerritorial,
      busqueda,
      metodoAsignacion,
      territorialSeleccionada,
      codigosDivipola,
      deptoSeleccionado,
      municipiosSeleccionados,
      showResults,
      resultados,
      notification,
      rolesDisponibles,
      territorialesDisponibles,
      profesionalesFiltrados,
      municipiosPorTerritorial,
      municipiosPorDepto,
      codigosValidos,
      codigosInvalidos,
      municipiosParaAsignar,
      totalAsignaciones,
      puedeEjecutar,
      isSelected,
      toggleProfesional,
      seleccionarTodos,
      deseleccionarTodos,
      seleccionarTodosMunicipios,
      ejecutarAsignacion,
      goBack,
      closeResults,
      nuevaAsignacion
    }
  }
})
</script>

<style scoped>
.asignaciones-masivas-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  margin: 0;
  font-size: 1.8rem;
  color: #333;
}

.header-subtitle {
  margin: 8px 0 0 0;
  color: #666;
}

.btn-outline {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-outline:hover {
  background: #f5f5f5;
  border-color: #ccc;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #1976D2;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-link {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: #2196F3;
  cursor: pointer;
  font-size: 0.85rem;
  padding: 4px 8px;
}

.btn-link:hover {
  text-decoration: underline;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.btn-icon:hover {
  color: #333;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.step-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  overflow: hidden;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
}

.step-number {
  width: 28px;
  height: 28px;
  background: #2196F3;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
}

.step-header h2 {
  margin: 0;
  font-size: 1.1rem;
  color: #333;
  flex: 1;
}

.selected-count {
  background: #e3f2fd;
  color: #1976D2;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.step-content {
  padding: 20px;
}

/* Filtros */
.filters-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 180px;
}

.filter-group.search {
  flex: 1;
  min-width: 200px;
}

.filter-group label {
  font-size: 0.8rem;
  color: #666;
  font-weight: 500;
}

.filter-group select,
.filter-group input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
}

.filter-group select:focus,
.filter-group input:focus {
  outline: none;
  border-color: #2196F3;
}

.quick-actions {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

/* Lista de profesionales */
.profesionales-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 8px;
}

.profesional-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background 0.2s;
}

.profesional-item:last-child {
  border-bottom: none;
}

.profesional-item:hover {
  background: #f8f9fa;
}

.profesional-item.selected {
  background: #e3f2fd;
}

.profesional-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.profesional-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.profesional-nombre {
  font-weight: 500;
  color: #333;
}

.profesional-meta {
  font-size: 0.8rem;
  color: #888;
}

.separator {
  margin: 0 6px;
  color: #ccc;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #999;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 12px;
}

/* Métodos de asignación */
.method-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.method-option {
  display: flex;
  gap: 16px;
  padding: 16px;
  border: 2px solid #eee;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.method-option:hover {
  border-color: #ccc;
}

.method-option.active {
  border-color: #2196F3;
  background: #f8fbff;
}

.method-radio {
  padding-top: 2px;
}

.method-radio input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.method-content {
  flex: 1;
}

.method-content h3 {
  margin: 0 0 4px 0;
  font-size: 1rem;
  color: #333;
}

.method-content p {
  margin: 0;
  font-size: 0.85rem;
  color: #666;
}

.method-form {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.method-form select,
.method-form textarea {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
  font-family: inherit;
}

.method-form textarea {
  resize: vertical;
  min-height: 80px;
}

.method-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #e8f5e9;
  border-radius: 6px;
  color: #2e7d32;
  font-size: 0.9rem;
}

.divipola-stats {
  display: flex;
  gap: 16px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
}

.stat.valid {
  color: #4caf50;
}

.stat.invalid {
  color: #f44336;
}

.stat i {
  font-size: 18px;
}

.invalid-codes {
  color: #f44336;
  font-size: 0.8rem;
}

/* Multi-select municipios */
.municipios-multiselect {
  margin-top: 12px;
}

.multiselect-actions {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.municipios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.municipio-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  cursor: pointer;
}

.municipio-checkbox input {
  cursor: pointer;
}

/* Confirmación */
.step-card.confirmation {
  border: 2px solid #e3f2fd;
}

.confirmation-summary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 24px;
  background: #f8f9fa;
  border-radius: 10px;
  margin-bottom: 16px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.summary-item i {
  font-size: 32px;
  color: #2196F3;
}

.summary-item div {
  display: flex;
  flex-direction: column;
}

.summary-item strong {
  font-size: 1.5rem;
  color: #333;
}

.summary-item span {
  font-size: 0.8rem;
  color: #666;
}

.summary-item.total i {
  color: #4caf50;
}

.summary-operator {
  font-size: 1.5rem;
  color: #999;
  font-weight: 300;
}

.confirmation-note {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fff3e0;
  border-radius: 6px;
  color: #e65100;
  font-size: 0.9rem;
  margin-bottom: 20px;
}

.confirmation-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Notificación */
.notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 1000;
  animation: slideIn 0.3s ease;
}

.notification.success {
  background: #4caf50;
}

.notification.error {
  background: #f44336;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.1rem;
}

.modal-body {
  padding: 24px 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #eee;
  background: #f8f9fa;
}

/* Resultados */
.results-grid {
  display: flex;
  gap: 24px;
  justify-content: center;
}

.result-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 30px;
  border-radius: 10px;
  background: #f8f9fa;
}

.result-item i {
  font-size: 36px;
}

.result-item.success i {
  color: #4caf50;
}

.result-item.info i {
  color: #2196F3;
}

.result-item strong {
  font-size: 1.8rem;
  color: #333;
}

.result-item span {
  font-size: 0.85rem;
  color: #666;
}

/* Responsive */
@media (max-width: 768px) {
  .filters-row {
    flex-direction: column;
  }

  .filter-group {
    width: 100%;
  }

  .confirmation-summary {
    flex-direction: column;
    gap: 16px;
  }

  .summary-operator {
    display: none;
  }

  .results-grid {
    flex-direction: column;
    gap: 12px;
  }

  .result-item {
    padding: 16px;
  }
}
</style>
