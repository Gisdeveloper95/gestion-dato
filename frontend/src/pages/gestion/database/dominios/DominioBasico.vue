<template>
  <div class="dominio-container">
    <!-- Header del dominio -->
    <div class="dominio-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="dominio-title">{{ config.title }}</h1>
          <p class="dominio-description">{{ config.description }}</p>
        </div>
        <div class="actions-section">
          <button 
            @click="refrescarDatos" 
            class="btn btn-secondary"
            :disabled="cargando"
          >
            <i class="material-icons">refresh</i>
            Actualizar
          </button>
        </div>
      </div>
    </div>

    <!-- Contenido principal -->
    <div class="dominio-content">
      <div v-if="error" class="alert alert-error">
        <i class="material-icons">error</i>
        {{ error }}
        <button @click="error = null" class="close-btn">&times;</button>
      </div>

      <div v-if="success" class="alert alert-success">
        <i class="material-icons">check_circle</i>
        {{ success }}
        <button @click="success = null" class="close-btn">&times;</button>
      </div>

      <!-- Tabla de gestión -->
      <TableManager
        :table-config="tableConfig"
        :permissions="permissions"
        :auto-load="true"
        @item-created="handleItemCreated"
        @item-updated="handleItemUpdated"
        @item-deleted="handleItemDeleted"
        @error="handleError"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import TableManager from '@/pages/gestion/database/components/TableManager.vue'
import { DominiosService, type DominioKey, ENDPOINTS_DOMINIOS } from '@/api/dominios'

// =============== INTERFACES ===============
interface DominioConfig {
  key: DominioKey
  title: string
  description: string
  singularName: string
  pluralName: string
  idField: string
  columns: Array<{
    key: string
    label: string
    type?: 'text' | 'number' | 'select' | 'textarea'
    editable?: boolean
    required?: boolean
    sortable?: boolean
    placeholder?: string
    maxLength?: number
  }>
  searchFields: string[]
}

// =============== PROPS ===============
interface Props {
  config: DominioConfig
}

const props = defineProps<Props>()

// =============== STATE ===============
const cargando = ref(false)
const error = ref<string | null>(null)
const success = ref<string | null>(null)

// Inicializar servicio específico para este dominio
const dominioService = new DominiosService(props.config.key)

// =============== COMPUTED ===============
const tableConfig = computed(() => ({
  title: props.config.title,
  singularName: props.config.singularName,
  pluralName: props.config.pluralName,
  apiEndpoint: ENDPOINTS_DOMINIOS[props.config.key],
  idField: props.config.idField,
  columns: props.config.columns,
  searchFields: props.config.searchFields
}))

const permissions = computed(() => ({
  canCreate: true,
  canEdit: true,
  canDelete: true,
  canExport: true
}))

// =============== METHODS ===============
const refrescarDatos = async () => {
  if (cargando.value) return
  
  try {
    cargando.value = true
    error.value = null
    
    // El TableManager se encargará de recargar los datos
    window.location.reload()
    
  } catch (err: any) {
    error.value = 'Error al actualizar los datos'
    console.error('Error al refrescar:', err)
  } finally {
    cargando.value = false
  }
}

const handleItemCreated = (item: any) => {
  success.value = `${props.config.singularName} creado exitosamente`
  setTimeout(() => success.value = null, 3000)
}

const handleItemUpdated = (item: any) => {
  success.value = `${props.config.singularName} actualizado exitosamente`
  setTimeout(() => success.value = null, 3000)
}

const handleItemDeleted = (item: any) => {
  success.value = `${props.config.singularName} eliminado exitosamente`
  setTimeout(() => success.value = null, 3000)
}

const handleError = (errorMessage: string) => {
  error.value = errorMessage
  setTimeout(() => error.value = null, 5000)
}

// =============== LIFECYCLE ===============
onMounted(() => {
  // El TableManager se encarga de cargar los datos automáticamente
})
</script>

<style scoped>
.dominio-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #f8f9fa;
}

.dominio-header {
  background: white;
  border-bottom: 1px solid #e9ecef;
  padding: 1.5rem 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  max-width: 1200px;
  margin: 0 auto;
}

.title-section {
  flex: 1;
}

.dominio-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.75rem;
  font-weight: 600;
  color: #343a40;
}

.dominio-description {
  margin: 0;
  color: #6c757d;
  font-size: 0.95rem;
}

.actions-section {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #545b62;
}

.dominio-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  position: relative;
}

.alert-error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.close-btn {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: inherit;
  opacity: 0.7;
}

.close-btn:hover {
  opacity: 1;
}

.material-icons {
  font-size: 1.2rem;
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }
  
  .dominio-content {
    padding: 1rem;
  }
  
  .dominio-title {
    font-size: 1.5rem;
  }
}
</style>