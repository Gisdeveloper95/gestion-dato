<template>
  <TableManager
    :table-config="config"
    :permissions="permissions"
    @item-created="handleItemCreated"
    @item-updated="handleItemUpdated"
    @item-deleted="handleItemDeleted"
    @error="handleError"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import TableManager from './TableManager.vue'

// =============== INTERFACES SIMPLIFICADAS ===============
interface TableColumn {
  key: string
  label: string
  type?: 'text' | 'number' | 'date' | 'select' | 'textarea' | 'boolean'
  sortable?: boolean
  editable?: boolean
  required?: boolean
  options?: { value: any, label: string }[]
  format?: (value: any) => string
  placeholder?: string
}

interface TableFilter {
  key: string
  label: string
  type: 'select' | 'multiselect'
  options?: { value: any, label: string }[]
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

interface TablePermissions {
  canCreate: boolean
  canEdit: boolean
  canDelete: boolean
  canExport: boolean
}

interface ActiveFilters {
  [key: string]: any
}

// =============== PROPS ===============
interface Props {
  /** Configuración de la tabla */
  config: TableConfig
  /** Permisos del usuario */
  permissions?: TablePermissions
  /** Servicio específico para CRUD operations */
  service?: {
    getAll?: (filters?: any) => Promise<any>
    create?: (data: any) => Promise<any>
    update?: (id: any, data: any) => Promise<any>
    delete?: (id: any) => Promise<void>
    validateData?: (data: any) => string[]
  }
  /** Filtros iniciales */
  initialFilters?: ActiveFilters
  /** Si debe cargar datos automáticamente al montar */
  autoLoad?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  autoLoad: true,
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
  'filters-changed': [filters: ActiveFilters]
  'error': [error: string, context?: string]
  'data-loaded': [data: any[], total: number]
}>()

// =============== ESTADO REACTIVO ===============
const currentData = ref<any[]>([])
const totalRecords = ref(0)
const currentFilters = ref<ActiveFilters>(props.initialFilters || {})
const error = ref('')

// =============== COMPUTED ===============
const hasService = computed(() => {
  return props.service && typeof props.service.getAll === 'function'
})

// =============== MÉTODOS PRINCIPALES ===============

/**
 * Manejar creación de elementos
 */
const handleItemCreated = (item: any) => {
  console.log('Elemento creado:', item)
  emit('item-created', item)
}

/**
 * Manejar actualización de elementos
 */
const handleItemUpdated = (item: any) => {
  console.log('Elemento actualizado:', item)
  emit('item-updated', item)
}

/**
 * Manejar eliminación de elementos
 */
const handleItemDeleted = (item: any) => {
  console.log('Elemento eliminado:', item)
  emit('item-deleted', item)
}

/**
 * Manejar errores
 */
const handleError = (errorMessage: string, context?: string) => {
  console.error(`Error en TableManagerAdapter${context ? ` (${context})` : ''}:`, errorMessage)
  emit('error', errorMessage, context)
}

// =============== MÉTODOS AUXILIARES ===============

/**
 * Recargar datos manualmente
 */
const reload = async () => {
  // Aquí podrías implementar lógica de recarga si es necesario
  console.log('Recargando datos...')
}

/**
 * Limpiar datos
 */
const clear = () => {
  currentData.value = []
  totalRecords.value = 0
  currentFilters.value = {}
  error.value = ''
}

// =============== WATCHERS ===============
watch(() => props.initialFilters, (newFilters) => {
  if (newFilters) {
    currentFilters.value = { ...newFilters }
  }
}, { immediate: true })

// =============== LIFECYCLE ===============
onMounted(async () => {
  console.log('TableManagerAdapter montado con configuración:', props.config.title)
})

// =============== EXPOSE ===============
defineExpose({
  reload,
  clear,
  currentData: computed(() => currentData.value),
  totalRecords: computed(() => totalRecords.value),
  hasError: computed(() => !!error.value),
  errorMessage: computed(() => error.value)
})
</script>

<style scoped>
/* El adaptador no necesita estilos propios, 
   ya que simplemente pasa todo al TableManager */
</style>