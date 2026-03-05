<template>
    <form @submit.prevent="handleSubmit" class="clasificacion-form">
      <div class="form-group required">
        <label for="insumo">Insumo:</label>
        <div class="select-container">
          <select 
            id="insumo" 
            v-model="formData.cod_insumo"
            required
            :disabled="modoEdicion"
          >
            <option value="" disabled selected>Seleccione un insumo</option>
            <option 
              v-for="insumo in insumos" 
              :key="insumo.cod_insumo" 
              :value="insumo.cod_insumo"
            >
              {{ insumo.municipio?.nom_municipio }} - 
              {{ insumo.categoria?.nom_categoria }} 
              ({{ insumo.tipo_insumo }})
            </option>
          </select>
        </div>
        <span v-if="errors.cod_insumo" class="error-message">{{ errors.cod_insumo }}</span>
      </div>
      
      <div class="form-group required">
        <label for="nombre">Nombre de la clasificación:</label>
        <input 
          type="text" 
          id="nombre" 
          v-model="formData.nombre"
          placeholder="Ingrese el nombre de la clasificación"
          required
        />
        <span v-if="errors.nombre" class="error-message">{{ errors.nombre }}</span>
      </div>
      
      <div class="form-group">
        <label for="ruta">Ruta de almacenamiento:</label>
        <input 
          type="text" 
          id="ruta" 
          v-model="formData.ruta"
          placeholder="Ingrese la ruta donde se almacenarán los archivos"
        />
        <span v-if="errors.ruta" class="error-message">{{ errors.ruta }}</span>
      </div>
      
      <div class="form-group">
        <label for="observacion">Observaciones:</label>
        <textarea 
          id="observacion" 
          v-model="formData.observacion"
          placeholder="Agregue observaciones relevantes"
          rows="3"
        ></textarea>
        <span v-if="errors.observacion" class="error-message">{{ errors.observacion }}</span>
      </div>
      
      <div class="form-group">
        <label for="descripcion">Descripción:</label>
        <textarea 
          id="descripcion" 
          v-model="formData.descripcion"
          placeholder="Agregue una descripción detallada"
          rows="4"
        ></textarea>
        <span v-if="errors.descripcion" class="error-message">{{ errors.descripcion }}</span>
      </div>
      
      <div class="form-actions">
        <button type="button" class="btn-cancel" @click="cancelar">
          Cancelar
        </button>
        <button type="submit" class="btn-submit" :disabled="enviando">
          <span v-if="!enviando">{{ modoEdicion ? 'Actualizar' : 'Guardar' }}</span>
          <div v-else class="button-spinner"></div>
        </button>
      </div>
    </form>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, computed, watch } from 'vue'
  import type { PropType } from 'vue'
  import type { ClasificacionInsumo, Insumo } from '@/models/municipio'
  
  export default defineComponent({
    name: 'ClasificacionForm',
    
    props: {
      clasificacion: {
        type: Object as PropType<Partial<ClasificacionInsumo> | null>,
        default: null
      },
      insumos: {
        type: Array as PropType<Insumo[]>,
        default: () => []
      },
      modoEdicion: {
        type: Boolean,
        default: false
      }
    },
    
    emits: ['guardar', 'cancelar'],
    
    setup(props, { emit }) {
      // Estado del formulario
      const formData = ref({
        cod_insumo: props.clasificacion?.cod_insumo || '',
        nombre: props.clasificacion?.nombre || '',
        ruta: props.clasificacion?.ruta || '',
        observacion: props.clasificacion?.observacion || '',
        descripcion: props.clasificacion?.descripcion || ''
      })
      
      // Estado de validación
      const errors = ref({
        cod_insumo: '',
        nombre: '',
        ruta: '',
        observacion: '',
        descripcion: ''
      })
      
      // Estado de envío
      const enviando = ref(false)
      
      // Actualizar formulario cuando cambian las props
      watch(() => props.clasificacion, (newVal) => {
        if (newVal) {
          formData.value = {
            cod_insumo: newVal.cod_insumo || '',
            nombre: newVal.nombre || '',
            ruta: newVal.ruta || '',
            observacion: newVal.observacion || '',
            descripcion: newVal.descripcion || ''
          }
        }
      }, { deep: true })
      
      // Validar formulario
      const validarFormulario = (): boolean => {
        let esValido = true
        
        // Reiniciar errores
        errors.value = {
          cod_insumo: '',
          nombre: '',
          ruta: '',
          observacion: '',
          descripcion: ''
        }
        
        // Validar insumo
        if (!formData.value.cod_insumo) {
          errors.value.cod_insumo = 'Debe seleccionar un insumo'
          esValido = false
        }
        
        // Validar nombre
        if (!formData.value.nombre.trim()) {
          errors.value.nombre = 'El nombre de la clasificación es requerido'
          esValido = false
        } else if (formData.value.nombre.trim().length < 3) {
          errors.value.nombre = 'El nombre debe tener al menos 3 caracteres'
          esValido = false
        }
        
        // Validar ruta (opcional)
        if (formData.value.ruta && !formData.value.ruta.startsWith('/')) {
          errors.value.ruta = 'La ruta debe comenzar con /'
          esValido = false
        }
        
        // Validar descripción (opcional)
        if (formData.value.descripcion && formData.value.descripcion.trim().length < 10) {
          errors.value.descripcion = 'La descripción debe tener al menos 10 caracteres'
          esValido = false
        }
        
        return esValido
      }
      
      // Manejar envío del formulario
      const handleSubmit = async () => {
        if (!validarFormulario()) {
          return
        }
        
        try {
          enviando.value = true
          
          // Crear objeto de datos
          const clasificacionData: Partial<ClasificacionInsumo> = {
            cod_insumo: formData.value.cod_insumo ? Number(formData.value.cod_insumo) : undefined,
            nombre: formData.value.nombre.trim(),
            ruta: formData.value.ruta.trim() || null,
            observacion: formData.value.observacion.trim() || null,
            descripcion: formData.value.descripcion.trim() || null
          }
          
          // Si es edición, incluir el código
          if (props.modoEdicion && props.clasificacion?.cod_clasificacion) {
            clasificacionData.cod_clasificacion = props.clasificacion.cod_clasificacion
          }
          
          // Emitir evento
          emit('guardar', clasificacionData)
        } catch (error) {
          console.error('Error al guardar clasificación:', error)
        } finally {
          enviando.value = false
        }
      }
      
      // Cancelar formulario
      const cancelar = () => {
        emit('cancelar')
      }
      
      return {
        formData,
        errors,
        enviando,
        handleSubmit,
        cancelar
      }
    }
  })
  </script>
  
  <style scoped>
  .clasificacion-form {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
  }
  
  .form-group label {
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #495057;
  }
  
  .form-group.required label::after {
    content: "*";
    color: #dc3545;
    margin-left: 4px;
  }
  
  .form-group input,
  .form-group textarea,
  .select-container select {
    padding: 0.75rem;
    border: 1px solid #ced4da;
    border-radius: 4px;
    font-size: 1rem;
    transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  }
  
  .form-group input:focus,
  .form-group textarea:focus,
  .select-container select:focus {
    border-color: #80bdff;
    outline: 0;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  }
  
  .select-container {
    position: relative;
  }
  
  .select-container select {
    width: 100%;
    appearance: none;
    padding-right: 2.5rem;
  }
  
  .select-container::after {
    content: "↓";
    position: absolute;
    right: 1rem;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    color: #6c757d;
  }
  
  .error-message {
    color: #dc3545;
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }
  
  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 1rem;
  }
  
  .btn-cancel {
    padding: 0.75rem 1.5rem;
    border: 1px solid #6c757d;
    background-color: transparent;
    color: #6c757d;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.15s ease-in-out;
  }
  
  .btn-cancel:hover {
    background-color: #6c757d;
    color: white;
  }
  
  .btn-submit {
    padding: 0.75rem 1.5rem;
    border: none;
    background-color: #007bff;
    color: white;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    transition: background-color 0.15s ease-in-out;
    min-width: 120px;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .btn-submit:hover {
    background-color: #0069d9;
  }
  
  .btn-submit:disabled {
    background-color: #6c757d;
    cursor: not-allowed;
  }
  
  .button-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top: 2px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  @media (max-width: 768px) {
    .form-actions {
      flex-direction: column-reverse;
    }
    
    .btn-cancel, 
    .btn-submit {
      width: 100%;
      text-align: center;
    }
  }
  </style>