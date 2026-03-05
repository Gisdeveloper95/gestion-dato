<template>
  <div class="insumo-form-page">
    <div class="page-header">
      <div class="header-content">
        <h1>{{ isEditing ? 'Editar Insumo' : 'Nuevo Insumo' }}</h1>
        <button @click="goBack" class="btn-outline">
          <i class="material-icons">arrow_back</i>
          Volver
        </button>
      </div>
    </div>

    <div class="form-container">
      <div v-if="loading" class="loading-indicator">
        <div class="spinner"></div>
        <p>Cargando datos...</p>
      </div>

      <div v-else-if="error" class="error-message">
        <i class="material-icons">error</i>
        <p>{{ error }}</p>
        <button @click="goBack" class="btn-primary">Volver</button>
      </div>

      <form v-else @submit.prevent="saveInsumo" class="insumo-form">
        <div class="form-section">
          <h2>Información Básica</h2>
          
          <div class="form-row">
            <div class="form-group">
              <label for="cod_insumo">Código Insumo <span class="required">*</span></label>
              <input 
                type="number" 
                id="cod_insumo" 
                v-model="form.cod_insumo" 
                :readonly="isEditing"
                required
                placeholder="Código numérico"
              />
              <small class="form-hint">Código numérico único del insumo</small>
            </div>
            
            <div class="form-group">
              <label for="tipo_insumo">Tipo de Insumo <span class="required">*</span></label>
              <select 
                id="tipo_insumo" 
                v-model="form.tipo_insumo" 
                required
              >
                <option value="">Seleccione tipo</option>
                <option 
                  v-for="tipo in tiposInsumo" 
                  :key="tipo.tipo_insumo" 
                  :value="tipo.tipo_insumo"
                >
                  {{ tipo.tipo_insumo }}
                </option>
              </select>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="cod_categoria">Categoría <span class="required">*</span></label>
              <select 
                id="cod_categoria" 
                v-model="form.cod_categoria" 
                required
              >
                <option value="">Seleccione categoría</option>
                <option 
                  v-for="categoria in categorias" 
                  :key="categoria.cod_categoria" 
                  :value="categoria.cod_categoria"
                >
                  {{ categoria.nom_categoria }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="cod_municipio">Municipio <span class="required">*</span></label>
              <select 
                id="cod_municipio" 
                v-model="form.cod_municipio" 
                required
                :disabled="municipioIdFromRoute !== null"
              >
                <option value="">Seleccione municipio</option>
                <option 
                  v-for="municipio in municipios" 
                  :key="municipio.cod_municipio" 
                  :value="municipio.cod_municipio"
                >
                  {{ municipio.nom_municipio }} ({{ getNombreDepartamento(municipio.cod_depto) }})
                </option>
              </select>
            </div>
          </div>
        </div>
        
        <div class="form-section">
          <h2>Información Adicional</h2>
          <p class="section-description">
            Una vez creado el insumo, podrá agregar clasificaciones y detalles adicionales.
          </p>
        </div>
        
        <div class="form-actions">
          <button type="button" @click="goBack" class="btn-secondary">Cancelar</button>
          <button type="submit" class="btn-primary">{{ isEditing ? 'Actualizar' : 'Crear' }}</button>
        </div>
      </form>
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
import { defineComponent, ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { 
  getInsumoById, 
  createInsumo, 
  updateInsumo, 
  getCategorias, 
  getTiposInsumo
} from '@/api/insumos';
import { getMunicipios } from '@/api/municipios';
import type { Insumo } from '@/models/insumo';

export default defineComponent({
  name: 'InsumoForm',
  
  props: {
    id: {
      type: [String, Number],
      default: null
    }
  },
  
  setup(props) {
    const route = useRoute();
    const router = useRouter();
    
    // Estado de carga y error
    const loading = ref(false);
    const error = ref<string | null>(null);
    
    // Datos maestros
    const categorias = ref<any[]>([]);
    const tiposInsumo = ref<any[]>([]);
    const municipios = ref<any[]>([]);
    
    // Datos del formulario
    const form = ref({
      cod_insumo: '',
      cod_municipio: '',
      cod_categoria: '',
      tipo_insumo: ''
    });
    
    // Verificar si estamos editando o creando
    const isEditing = computed(() => !!props.id);
    
    // Verificar si tenemos un municipio en la ruta
    const municipioIdFromRoute = computed(() => {
      const municipioId = route.query.municipio?.toString();
      return municipioId ? Number(municipioId) : null;
    });
    
    // Estado de notificación
    const notification = ref({
      show: false,
      message: '',
      type: 'success',
      icon: 'check_circle',
      timeout: null as number | null
    });
    
    // Cargar datos iniciales
    onMounted(async () => {
      try {
        loading.value = true;
        
        // Cargar datos maestros
        const [categoriasData, tiposData, municipiosData] = await Promise.all([
          getCategorias(),
          getTiposInsumo(),
          getMunicipios()
        ]);
        
        categorias.value = categoriasData;
        tiposInsumo.value = tiposData;
        municipios.value = municipiosData;
        
        // Si hay un municipio en la ruta, establecerlo en el formulario
        if (municipioIdFromRoute.value) {
          form.value.cod_municipio = municipioIdFromRoute.value.toString();
        }
        
        // Si estamos editando, cargar los datos del insumo
        if (isEditing.value) {
          const insumoId = Number(props.id);
          const insumoData = await getInsumoById(insumoId);
          
          form.value = {
            cod_insumo: insumoData.cod_insumo.toString(),
            cod_municipio: insumoData.cod_municipio.toString(),
            cod_categoria: insumoData.cod_categoria.toString(),
            tipo_insumo: insumoData.tipo_insumo
          };
        }
      } catch (err: any) {
        console.error('Error cargando datos:', err);
        error.value = 'Error cargando datos. Por favor, intente nuevamente.';
      } finally {
        loading.value = false;
      }
    });
    
    // Método para obtener el nombre del departamento
    const getNombreDepartamento = (deptoId: number | string): string => {
      const municipio = municipios.value.find(m => m.cod_municipio.toString() === form.value.cod_municipio);
      
      if (municipio && municipio.cod_depto) {
        if (typeof municipio.cod_depto === 'object' && municipio.cod_depto.nom_depto) {
          return municipio.cod_depto.nom_depto;
        }
      }
      
      return 'N/A';
    };
    
    // Método para guardar el insumo
    const saveInsumo = async () => {
      try {
        // Validar formulario
        if (!form.value.cod_insumo || !form.value.cod_municipio || 
            !form.value.cod_categoria || !form.value.tipo_insumo) {
          showNotification('Por favor, complete todos los campos requeridos', 'error');
          return;
        }
        
        loading.value = true;
        
        // Preparar datos a enviar
        const insumoData: Partial<Insumo> = {
          cod_insumo: Number(form.value.cod_insumo),
          cod_municipio: Number(form.value.cod_municipio),
          cod_categoria: Number(form.value.cod_categoria),
          tipo_insumo: form.value.tipo_insumo
        };
        
        if (isEditing.value) {
          // Actualizar insumo existente
          await updateInsumo(Number(props.id), insumoData);
          showNotification('Insumo actualizado correctamente', 'success');
        } else {
          // Crear nuevo insumo
          await createInsumo(insumoData);
          showNotification('Insumo creado correctamente', 'success');
        }
        
        // Redireccionar después de un segundo
        setTimeout(() => {
          // Si vino de un municipio, volver a la vista de ese municipio
          if (municipioIdFromRoute.value) {
            router.push({
              path: '/gestion-informacion/insumos',
              query: { municipio: municipioIdFromRoute.value.toString() }
            });
          } else {
            router.push('/gestion-informacion/insumos');
          }
        }, 1000);
      } catch (err: any) {
        console.error('Error guardando insumo:', err);
        showNotification(
          `Error al ${isEditing.value ? 'actualizar' : 'crear'} el insumo. ${err.message || ''}`, 
          'error'
        );
      } finally {
        loading.value = false;
      }
    };
    
    // Mostrar notificación
    const showNotification = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
      // Cerrar notificación anterior si existe
      if (notification.value.timeout) {
        clearTimeout(notification.value.timeout);
      }
      
      // Establecer icono según el tipo
      let icon = 'info';
      switch (type) {
        case 'success':
          icon = 'check_circle';
          break;
        case 'error':
          icon = 'error';
          break;
        case 'warning':
          icon = 'warning';
          break;
      }
      
      // Mostrar nueva notificación
      notification.value = {
        show: true,
        message,
        type,
        icon,
        timeout: setTimeout(() => {
          notification.value.show = false;
        }, 5000) as unknown as number
      };
    };
    
    // Cerrar notificación
    const closeNotification = () => {
      if (notification.value.timeout) {
        clearTimeout(notification.value.timeout);
      }
      notification.value.show = false;
    };
    
    // Volver a la página anterior
    const goBack = () => {
      router.back();
    };
    
    return {
      loading,
      error,
      form,
      categorias,
      tiposInsumo,
      municipios,
      isEditing,
      municipioIdFromRoute,
      notification,
      saveInsumo,
      getNombreDepartamento,
      showNotification,
      closeNotification,
      goBack
    };
  }
});
</script>

<style scoped>
.insumo-form-page {
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

.form-container {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.loading-indicator,
.error-message {
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
  border-top: 4px solid #0d6efd;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #dc3545;
}

.error-message p {
  margin-bottom: 1.5rem;
  color: #6c757d;
}

.insumo-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-section h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #343a40;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #dee2e6;
}

.section-description {
  color: #6c757d;
  margin: 0;
}

.form-row {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 250px;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 1rem;
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
.form-group select,
.form-group textarea {
  padding: 0.5rem 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.95rem;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #4dabf7;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
  outline: none;
}

.form-hint {
  font-size: 0.8rem;
  color: #6c757d;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #dee2e6;
}

.btn-primary,
.btn-secondary,
.btn-outline {
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

/* Notificación */
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
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .form-actions button {
    width: 100%;
    justify-content: center;
  }
  
  .notification {
    min-width: auto;
    max-width: 90%;
    left: 5%;
    right: 5%;
  }
}
</style>