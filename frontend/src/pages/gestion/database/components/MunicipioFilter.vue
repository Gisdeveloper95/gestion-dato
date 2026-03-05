<template>
  <div class="municipio-filter">
    <div class="filter-group">
      <!-- Filtro de Departamento -->
      <div class="form-group">
        <label for="departamento-select">Departamento</label>
        <select 
          id="departamento-select"
          v-model="selectedDepartamento"
          @change="onDepartamentoChange"
          class="filter-select"
          :disabled="loadingDepartamentos"
        >
          <option value="">
            {{ loadingDepartamentos ? 'Cargando...' : 'Todos los departamentos' }}
          </option>
          <option 
            v-for="depto in departamentos" 
            :key="depto.id_departamento"
            :value="depto.id_departamento"
          >
            {{ depto.nombre_departamento }}
          </option>
        </select>
      </div>

      <!-- Filtro de Municipio -->
      <div class="form-group">
        <label for="municipio-select">Municipio</label>
        <div class="municipio-select-container">
          <select 
            id="municipio-select"
            v-model="selectedMunicipio"
            @change="onMunicipioChange"
            class="filter-select"
            :disabled="!selectedDepartamento || loadingMunicipios"
          >
            <option value="">
              {{ getMunicipioPlaceholder() }}
            </option>
            <option 
              v-for="municipio in municipiosFiltrados" 
              :key="municipio.cod_municipio"
              :value="municipio.cod_municipio"
            >
              {{ municipio.nombre_municipio }}
            </option>
          </select>
          
          <!-- Indicador de carga -->
          <div v-if="loadingMunicipios" class="loading-indicator">
            <span class="material-icons rotating">refresh</span>
          </div>
        </div>
      </div>

      <!-- Búsqueda rápida de municipio -->
      <div class="form-group" v-if="showSearch">
        <label for="municipio-search">Búsqueda rápida</label>
        <div class="search-container">
          <span class="material-icons search-icon">search</span>
          <input
            id="municipio-search"
            v-model="searchQuery"
            type="text"
            placeholder="Buscar municipio..."
            class="search-input"
            @input="onSearchInput"
          />
          <button 
            v-if="searchQuery"
            @click="clearSearch"
            class="clear-search"
          >
            <span class="material-icons">clear</span>
          </button>
        </div>
      </div>

      <!-- Acciones rápidas -->
      <div class="filter-actions" v-if="showActions">
        <button 
          @click="clearFilters"
          class="btn-clear"
          :disabled="!selectedDepartamento && !selectedMunicipio"
        >
          <span class="material-icons">clear_all</span>
          Limpiar
        </button>
        
        <button 
          v-if="canSelectMultiple"
          @click="toggleMultiSelect"
          class="btn-multi"
          :class="{ active: multiSelectMode }"
        >
          <span class="material-icons">
            {{ multiSelectMode ? 'radio_button_checked' : 'check_box_outline_blank' }}
          </span>
          Múltiple
        </button>
      </div>
    </div>

    <!-- Selección múltiple -->
    <div v-if="multiSelectMode && canSelectMultiple" class="multi-select-section">
      <h4>Municipios seleccionados</h4>
      <div class="selected-municipios">
        <div 
          v-for="municipio in selectedMunicipios"
          :key="municipio.cod_municipio"
          class="selected-municipio-chip"
        >
          <span>{{ municipio.nombre_municipio }}</span>
          <button 
            @click="removeMunicipio(municipio.cod_municipio)"
            class="remove-chip"
          >
            <span class="material-icons">close</span>
          </button>
        </div>
        
        <div v-if="selectedMunicipios.length === 0" class="no-selection">
          No hay municipios seleccionados
        </div>
      </div>
    </div>

    <!-- Estadísticas rápidas -->
    <div v-if="showStats" class="filter-stats">
      <div class="stat-item">
        <span class="stat-label">Departamentos:</span>
        <span class="stat-value">{{ departamentos.length }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Municipios disponibles:</span>
        <span class="stat-value">{{ municipiosFiltrados.length }}</span>
      </div>
      <div v-if="selectedMunicipio" class="stat-item">
        <span class="stat-label">Seleccionado:</span>
        <span class="stat-value highlighted">{{ getMunicipioNombre(selectedMunicipio) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { municipiosApi, departamentosApi } from '@/api/municipios'

// =============== INTERFACES ===============
interface Departamento {
  id_departamento: string
  nombre_departamento: string
}

interface Municipio {
  cod_municipio: string
  nombre_municipio: string
  id_departamento: string
  departamento?: Departamento
}

// =============== PROPS ===============
interface Props {
  modelValue?: string | string[]
  placeholder?: string
  showSearch?: boolean
  showActions?: boolean
  showStats?: boolean
  canSelectMultiple?: boolean
  departamentoInicial?: string
  municipioInicial?: string
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: 'Selecciona un municipio',
  showSearch: true,
  showActions: true,
  showStats: false,
  canSelectMultiple: false,
  disabled: false
})

// =============== EMITS ===============
const emit = defineEmits<{
  'update:modelValue': [value: string | string[]]
  'municipio-selected': [municipioId: string, municipio?: Municipio]
  'departamento-selected': [departamentoId: string, departamento?: Departamento]
  'selection-cleared': []
  'multiple-selected': [municipios: Municipio[]]
}>()

// =============== ESTADO REACTIVO ===============
const loadingDepartamentos = ref(false)
const loadingMunicipios = ref(false)
const departamentos = ref<Departamento[]>([])
const municipios = ref<Municipio[]>([])
const searchQuery = ref('')
const multiSelectMode = ref(false)

// Selecciones actuales
const selectedDepartamento = ref('')
const selectedMunicipio = ref('')
const selectedMunicipios = ref<Municipio[]>([])

// =============== COMPUTED ===============
const municipiosFiltrados = computed(() => {
  let result = municipios.value

  // Filtrar por departamento seleccionado
  if (selectedDepartamento.value) {
    result = result.filter(m => m.id_departamento === selectedDepartamento.value)
  }

  // Filtrar por búsqueda
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    result = result.filter(m => 
      m.nombre_municipio.toLowerCase().includes(query) ||
      m.cod_municipio.toLowerCase().includes(query)
    )
  }

  // Ordenar alfabéticamente
  return result.sort((a, b) => a.nombre_municipio.localeCompare(b.nombre_municipio))
})

// =============== MÉTODOS ===============
const cargarDepartamentos = async () => {
  loadingDepartamentos.value = true
  try {
    const response = await departamentosApi.getAll()
    departamentos.value = response.data.results || response.data
  } catch (error) {
    console.error('Error cargando departamentos:', error)
  } finally {
    loadingDepartamentos.value = false
  }
}

const cargarMunicipios = async () => {
  loadingMunicipios.value = true
  try {
    const response = await municipiosApi.getAll()
    municipios.value = response.data.results || response.data
  } catch (error) {
    console.error('Error cargando municipios:', error)
  } finally {
    loadingMunicipios.value = false
  }
}

const onDepartamentoChange = () => {
  // Limpiar municipio seleccionado cuando cambia el departamento
  selectedMunicipio.value = ''
  searchQuery.value = ''
  
  // Limpiar selección múltiple
  if (multiSelectMode.value) {
    selectedMunicipios.value = []
  }
  
  // Emitir evento de departamento seleccionado
  const departamento = departamentos.value.find(d => d.id_departamento === selectedDepartamento.value)
  emit('departamento-selected', selectedDepartamento.value, departamento)
  
  // Actualizar valor del modelo
  updateModelValue()
}

const onMunicipioChange = () => {
  if (multiSelectMode.value && props.canSelectMultiple) {
    // Modo selección múltiple
    if (selectedMunicipio.value && !selectedMunicipios.value.find(m => m.cod_municipio === selectedMunicipio.value)) {
      const municipio = municipiosFiltrados.value.find(m => m.cod_municipio === selectedMunicipio.value)
      if (municipio) {
        selectedMunicipios.value.push(municipio)
        emit('multiple-selected', selectedMunicipios.value)
      }
    }
    selectedMunicipio.value = '' // Resetear select
  } else {
    // Modo selección simple
    const municipio = municipiosFiltrados.value.find(m => m.cod_municipio === selectedMunicipio.value)
    emit('municipio-selected', selectedMunicipio.value, municipio)
  }
  
  updateModelValue()
}

const onSearchInput = () => {
  // Si hay solo un resultado de búsqueda, sugerir selección automática
  if (municipiosFiltrados.value.length === 1) {
    const municipio = municipiosFiltrados.value[0]
    // Auto-select si presiona Enter
    // selectedMunicipio.value = municipio.cod_municipio
  }
}

const clearSearch = () => {
  searchQuery.value = ''
}

const clearFilters = () => {
  selectedDepartamento.value = ''
  selectedMunicipio.value = ''
  selectedMunicipios.value = []
  searchQuery.value = ''
  multiSelectMode.value = false
  
  emit('selection-cleared')
  updateModelValue()
}

const toggleMultiSelect = () => {
  multiSelectMode.value = !multiSelectMode.value
  
  if (!multiSelectMode.value) {
    // Si se desactiva multi-select, mantener solo el último seleccionado
    if (selectedMunicipios.value.length > 0) {
      const ultimo = selectedMunicipios.value[selectedMunicipios.value.length - 1]
      selectedMunicipio.value = ultimo.cod_municipio
      selectedMunicipios.value = []
    }
  } else {
    // Si se activa multi-select, agregar el municipio actual a la lista
    if (selectedMunicipio.value) {
      const municipio = municipiosFiltrados.value.find(m => m.cod_municipio === selectedMunicipio.value)
      if (municipio && !selectedMunicipios.value.find(m => m.cod_municipio === municipio.cod_municipio)) {
        selectedMunicipios.value.push(municipio)
      }
      selectedMunicipio.value = ''
    }
  }
  
  updateModelValue()
}

const removeMunicipio = (municipioId: string) => {
  selectedMunicipios.value = selectedMunicipios.value.filter(m => m.cod_municipio !== municipioId)
  emit('multiple-selected', selectedMunicipios.value)
  updateModelValue()
}

const updateModelValue = () => {
  if (props.canSelectMultiple && multiSelectMode.value) {
    const valores = selectedMunicipios.value.map(m => m.cod_municipio)
    emit('update:modelValue', valores)
  } else {
    emit('update:modelValue', selectedMunicipio.value)
  }
}

// =============== HELPERS ===============
const getMunicipioPlaceholder = () => {
  if (loadingMunicipios.value) return 'Cargando municipios...'
  if (!selectedDepartamento.value) return 'Selecciona un departamento primero'
  if (municipiosFiltrados.value.length === 0) return 'No hay municipios disponibles'
  return multiSelectMode.value ? 'Agregar municipio...' : 'Selecciona un municipio'
}

const getMunicipioNombre = (municipioId: string) => {
  const municipio = municipios.value.find(m => m.cod_municipio === municipioId)
  return municipio?.nombre_municipio || municipioId
}

// =============== WATCHERS ===============
watch(() => props.modelValue, (newValue) => {
  if (Array.isArray(newValue)) {
    // Modo múltiple
    multiSelectMode.value = true
    selectedMunicipios.value = municipios.value.filter(m => newValue.includes(m.cod_municipio))
  } else {
    // Modo simple
    selectedMunicipio.value = newValue || ''
    if (selectedMunicipio.value) {
      // Autoseleccionar departamento
      const municipio = municipios.value.find(m => m.cod_municipio === selectedMunicipio.value)
      if (municipio && municipio.id_departamento !== selectedDepartamento.value) {
        selectedDepartamento.value = municipio.id_departamento
      }
    }
  }
})

// =============== LIFECYCLE ===============
onMounted(async () => {
  await Promise.all([
    cargarDepartamentos(),
    cargarMunicipios()
  ])
  
  // Inicializar con valores por defecto
  if (props.departamentoInicial) {
    selectedDepartamento.value = props.departamentoInicial
  }
  
  if (props.municipioInicial) {
    selectedMunicipio.value = props.municipioInicial
    // Auto-seleccionar departamento
    const municipio = municipios.value.find(m => m.cod_municipio === props.municipioInicial)
    if (municipio && !selectedDepartamento.value) {
      selectedDepartamento.value = municipio.id_departamento
    }
  }
})
</script>

<style scoped>
.municipio-filter {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Layout del filtro */
.filter-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  align-items: end;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 500;
  color: #495057;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

/* Selects */
.filter-select {
  padding: 0.75rem 1rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  background: white;
  font-size: 0.9rem;
  transition: all 0.2s;
  width: 100%;
}

.filter-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.filter-select:disabled {
  background: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

/* Contenedor de municipio con indicador */
.municipio-select-container {
  position: relative;
}

.loading-indicator {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

/* Búsqueda */
.search-container {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  color: #6c757d;
  z-index: 1;
}

.search-input {
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  width: 100%;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.clear-search {
  position: absolute;
  right: 0.5rem;
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 3px;
  display: flex;
  align-items: center;
}

.clear-search:hover {
  background: #f8f9fa;
}

/* Acciones */
.filter-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-clear, .btn-multi {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: 1px solid #ced4da;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-clear:hover:not(:disabled) {
  background: #f8f9fa;
  border-color: #adb5bd;
}

.btn-clear:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-multi:hover {
  background: #e3f2fd;
  border-color: #2196f3;
}

.btn-multi.active {
  background: #2196f3;
  color: white;
  border-color: #2196f3;
}

/* Selección múltiple */
.multi-select-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e9ecef;
}

.multi-select-section h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  color: #495057;
}

.selected-municipios {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  min-height: 2.5rem;
  align-items: flex-start;
}

.selected-municipio-chip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.5rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  border: 1px solid #bbdefb;
}

.remove-chip {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0.125rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
}

.remove-chip:hover {
  background: rgba(25, 118, 210, 0.1);
}

.no-selection {
  color: #6c757d;
  font-style: italic;
  padding: 0.75rem;
  text-align: center;
  width: 100%;
}

/* Estadísticas */
.filter-stats {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.stat-label {
  color: #6c757d;
}

.stat-value {
  font-weight: 500;
  color: #495057;
}

.stat-value.highlighted {
  color: #667eea;
  font-weight: 600;
}

/* Animaciones */
.rotating {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .filter-group {
    grid-template-columns: 1fr;
  }
  
  .filter-actions {
    justify-content: center;
  }
  
  .filter-stats {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .selected-municipios {
    justify-content: center;
  }
}

/* Estados hover y focus mejorados */
.filter-select:hover:not(:disabled) {
  border-color: #adb5bd;
}

.search-input:hover {
  border-color: #adb5bd;
}

/* Mejoras de accesibilidad */
.filter-select:focus-visible,
.search-input:focus-visible {
  outline: 2px solid #667eea;
  outline-offset: 2px;
}

button:focus-visible {
  outline: 2px solid #667eea;
  outline-offset: 2px;
}
</style>