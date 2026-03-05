<template>
  <div class="municipio-form-page">
    <div class="page-header">
      <div class="header-content">
        <h1>{{ isEditing ? 'Editar Municipio' : 'Nuevo Municipio' }}</h1>
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

      <form v-else @submit.prevent="saveMunicipio" class="municipio-form">
        <!-- Información básica del municipio -->
        <div class="form-section">
          <h2>Información Básica</h2>
          
          <div class="form-row">
            <div class="form-group">
              <label for="cod_municipio">Código Municipio <span class="required">*</span></label>
              <input 
                type="text" 
                id="cod_municipio" 
                v-model="form.cod_municipio" 
                :disabled="isEditing"
                required
                pattern="[0-9]{5}"
                maxlength="5"
                placeholder="Código de 5 dígitos"
              />
              <small class="form-hint">Código único de 5 dígitos del municipio</small>
            </div>
            
            <div class="form-group">
              <label for="nom_municipio">Nombre del Municipio <span class="required">*</span></label>
              <input 
                type="text" 
                id="nom_municipio" 
                v-model="form.nom_municipio" 
                required
                placeholder="Nombre completo del municipio"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="cod_depto">Departamento <span class="required">*</span></label>
              <select 
                id="cod_depto" 
                v-model="form.cod_depto" 
                required
              >
                <option value="">Seleccione un departamento</option>
                <option 
                  v-for="depto in departamentos" 
                  :key="depto.cod_depto" 
                  :value="depto.cod_depto"
                >
                  {{ depto.nom_depto }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="fecha_inicio">Fecha de Inicio</label>
              <input 
                type="date" 
                id="fecha_inicio" 
                v-model="form.fecha_inicio"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="area">Área (km²)</label>
              <input 
                type="text" 
                id="area" 
                v-model="form.area"
                placeholder="Área del municipio en km²"
              />
            </div>
            
            <div class="form-group">
              <label for="nom_territorial">Territorial</label>
              <select 
                id="nom_territorial" 
                v-model="form.nom_territorial"
              >
                <option value="">Seleccione una territorial</option>
                <option 
                  v-for="territorial in territoriales" 
                  :key="territorial.nom_territorial" 
                  :value="territorial.nom_territorial"
                >
                  {{ territorial.nom_territorial }}
                </option>
              </select>
            </div>
          </div>
        </div>
        
        <!-- Información de mecanismos -->
        <div class="form-section">
          <h2>Información de Mecanismos</h2>
          
          <div class="form-row">
            <div class="form-group">
              <label for="mecanismo_general">Mecanismo General</label>
              <select 
                id="mecanismo_general" 
                v-model="form.mecanismo_general"
              >
                <option value="">Seleccione un mecanismo</option>
                <option 
                  v-for="mecanismo in mecanismosGenerales" 
                  :key="mecanismo.cod_mecanismo" 
                  :value="mecanismo.cod_mecanismo"
                >
                  {{ mecanismo.cod_mecanismo }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="mecanismo_detalle">Mecanismo Detalle</label>
              <select 
                id="mecanismo_detalle" 
                v-model="form.mecanismo_detalle"
              >
                <option value="">Seleccione un mecanismo detalle</option>
                <option 
                  v-for="detalle in mecanismosDetalle" 
                  :key="detalle.cod_mecanismo_detalle" 
                  :value="detalle.cod_mecanismo_detalle"
                >
                  {{ detalle.cod_mecanismo_detalle }}
                </option>
              </select>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="mecanismo_operacion">Mecanismo Operación</label>
              <select 
                id="mecanismo_operacion" 
                v-model="form.mecanismo_operacion"
              >
                <option value="">Seleccione un mecanismo de operación</option>
                <option 
                  v-for="operacion in mecanismosOperacion" 
                  :key="operacion.cod_operacion" 
                  :value="operacion.cod_operacion"
                >
                  {{ operacion.cod_operacion }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="alcance_operacion">Alcance Operación</label>
              <select 
                id="alcance_operacion" 
                v-model="form.alcance_operacion"
              >
                <option value="">Seleccione un alcance</option>
                <option 
                  v-for="alcance in alcancesOperacion" 
                  :key="alcance.cod_alcance" 
                  :value="alcance.cod_alcance"
                >
                  {{ alcance.cod_alcance }}
                </option>
              </select>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="grupo">Grupo</label>
              <select 
                id="grupo" 
                v-model="form.grupo"
              >
                <option value="">Seleccione un grupo</option>
                <option 
                  v-for="grupo in grupos" 
                  :key="grupo.cod_grupo" 
                  :value="grupo.cod_grupo"
                >
                  {{ grupo.descripcion || grupo.cod_grupo }}
                </option>
              </select>
            </div>
          </div>
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
  getMunicipioById, 
  crearMunicipio, 
  actualizarMunicipio
} from '@/api/municipios';
import { 
  getCategorias, 
  getTiposInsumo, 
  getEntidades, 
  getFormatos, 
  getZonas, 
  getUsuarios,
  getTerritoriales,
  getMecanismosGenerales,
  getMecanismosDetalle,
  getMecanismosOperacion,
  getAlcancesOperacion,
  getGrupos,
  getDepartamentos
} from '@/api/insumos';
import api from '@/api/config';
import type { Municipio } from '@/models/municipio';

export default defineComponent({
  name: 'MunicipioForm',
  
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
    const departamentos = ref<any[]>([]);
    const territoriales = ref<any[]>([]);
    const mecanismosGenerales = ref<any[]>([]);
    const mecanismosDetalle = ref<any[]>([]);
    const mecanismosOperacion = ref<any[]>([]);
    const alcancesOperacion = ref<any[]>([]);
    const grupos = ref<any[]>([]);
    
    // Datos del formulario
    const form = ref({
      cod_municipio: '',
      nom_municipio: '',
      cod_depto: '',
      fecha_inicio: '',
      area: '',
      nom_territorial: '',
      mecanismo_general: '',
      mecanismo_detalle: '',
      mecanismo_operacion: '',
      alcance_operacion: '',
      grupo: ''
    });
    
    // Verificar si estamos editando o creando
    const isEditing = computed(() => !!props.id);
    
    // Estado de notificación
    const notification = ref({
      show: false,
      message: '',
      type: 'success',
      icon: 'check_circle',
      timeout: null as number | null
    });
    
    // Función auxiliar para cargar todos los datos paginados
    const cargarTodosDatos = async (url: string) => {
      let allResults = [];
      let nextUrl = url;
      
      try {
        while (nextUrl) {
          const response = await api.get(nextUrl);
          
          // Si la respuesta no es paginada
          if (Array.isArray(response)) {
            return response;
          }
          
          // Si es paginada
          if (response.results) {
            allResults = [...allResults, ...response.results];
            nextUrl = response.next;
          } else {
            // Si no tiene results, probablemente sea un array directo
            return response;
          }
        }
      } catch (error) {
        console.error(`Error cargando datos de ${url}:`, error);
        return [];
      }
      
      return allResults;
    };
    
    // Cargar datos iniciales
    onMounted(async () => {
      try {
        loading.value = true;
        error.value = null;
        
        console.log('Iniciando carga de datos maestros...');
        
        // Cargar datos maestros en paralelo
        try {
          const [
            deptosData,
            territorialesData,
            mecanismosData,
            detallesData,
            operacionData,
            alcancesData,
            gruposData
          ] = await Promise.all([
            getDepartamentos(),
            getTerritoriales(),
            getMecanismosGenerales(),
            getMecanismosDetalle(),
            getMecanismosOperacion(),
            getAlcancesOperacion(),
            getGrupos()
          ]);
          
          departamentos.value = deptosData || [];
          territoriales.value = territorialesData || [];
          mecanismosGenerales.value = mecanismosData || [];
          mecanismosDetalle.value = detallesData || [];
          mecanismosOperacion.value = operacionData || [];
          alcancesOperacion.value = alcancesData || [];
          grupos.value = gruposData || [];
          
          console.log('Datos maestros cargados:', {
            departamentos: departamentos.value.length,
            territoriales: territoriales.value.length,
            mecanismos: mecanismosGenerales.value.length
          });
        } catch (err) {
          console.error('Error cargando datos maestros:', err);
          // Si falla cargar los datos maestros, intentar cargarlos individualmente
          departamentos.value = await cargarTodosDatos('/preoperacion/departamentos/') || [];
          territoriales.value = await cargarTodosDatos('/preoperacion/territoriales/') || [];
          mecanismosGenerales.value = await cargarTodosDatos('/preoperacion/mecanismos-general/') || [];
          mecanismosDetalle.value = await cargarTodosDatos('/preoperacion/mecanismos-detalle/') || [];
          mecanismosOperacion.value = await cargarTodosDatos('/preoperacion/mecanismos-operacion/') || [];
          alcancesOperacion.value = await cargarTodosDatos('/preoperacion/alcances-operacion/') || [];
          grupos.value = await cargarTodosDatos('/preoperacion/grupos/') || [];
        }
        
        // Si estamos editando, cargar los datos del municipio
        if (isEditing.value) {
          console.log('Cargando datos del municipio para editar...');
          const municipioId = Number(props.id);
          const municipioData = await getMunicipioById(municipioId);
          
          console.log('Datos del municipio cargados:', municipioData);
          
          // Verificar que tenemos los datos necesarios
          if (municipioData) {
            form.value = {
              cod_municipio: municipioData.cod_municipio?.toString() || '',
              nom_municipio: municipioData.nom_municipio || '',
              cod_depto: (typeof municipioData.cod_depto === 'object' && municipioData.cod_depto?.cod_depto) 
                         ? municipioData.cod_depto.cod_depto.toString()
                         : (municipioData.cod_depto?.toString() || ''),
              fecha_inicio: municipioData.fecha_inicio || '',
              area: municipioData.area || '',
              nom_territorial: municipioData.nom_territorial || '',
              mecanismo_general: municipioData.mecanismo_general || '',
              mecanismo_detalle: municipioData.mecanismo_detalle || '',
              mecanismo_operacion: municipioData.mecanismo_operacion || '',
              alcance_operacion: municipioData.alcance_operacion || '',
              grupo: municipioData.grupo || ''
            };
          }
        }
      } catch (err: any) {
        console.error('Error cargando datos:', err);
        error.value = 'Error cargando datos. Por favor, intente nuevamente.';
      } finally {
        loading.value = false;
      }
    });
    
    // Método para guardar el municipio
    const saveMunicipio = async () => {
      try {
        // Validar formulario
        if (!form.value.cod_municipio || !form.value.nom_municipio || !form.value.cod_depto) {
          showNotification('Por favor, complete todos los campos requeridos', 'error');
          return;
        }
        
        loading.value = true;
        
        // Preparar datos a enviar
        const municipioData: Partial<Municipio> = {
          cod_municipio: Number(form.value.cod_municipio),
          nom_municipio: form.value.nom_municipio,
          cod_depto: Number(form.value.cod_depto),
          fecha_inicio: form.value.fecha_inicio || null,
          area: form.value.area || null,
          nom_territorial: form.value.nom_territorial || null,
          mecanismo_general: form.value.mecanismo_general || null,
          mecanismo_detalle: form.value.mecanismo_detalle || null,
          mecanismo_operacion: form.value.mecanismo_operacion || null,
          alcance_operacion: form.value.alcance_operacion || null,
          grupo: form.value.grupo || null
        };
        
        if (isEditing.value) {
          // Actualizar municipio existente
          await actualizarMunicipio(Number(props.id), municipioData);
          showNotification('Municipio actualizado correctamente', 'success');
        } else {
          // Crear nuevo municipio
          await crearMunicipio(municipioData);
          showNotification('Municipio creado correctamente', 'success');
        }
        
        // Redireccionar después de un segundo
        setTimeout(() => {
          router.push('/gestion-informacion/municipios');
        }, 1000);
      } catch (err: any) {
        console.error('Error guardando municipio:', err);
        showNotification(
          `Error al ${isEditing.value ? 'actualizar' : 'crear'} el municipio. ${err.message || ''}`, 
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
      departamentos,
      territoriales,
      mecanismosGenerales,
      mecanismosDetalle,
      mecanismosOperacion,
      alcancesOperacion,
      grupos,
      isEditing,
      notification,
      saveMunicipio,
      showNotification,
      closeNotification,
      goBack
    };
  }
});
</script>

<style scoped>
/* Estilos idénticos a los que ya tienes, no necesitas cambiarlos */
.municipio-form-page {
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

.municipio-form {
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

.form-group input:disabled {
  background-color: #e9ecef;
  cursor: not-allowed;
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