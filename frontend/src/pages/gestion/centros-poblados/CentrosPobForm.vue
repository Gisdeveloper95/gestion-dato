<template>
  <div class="centros-poblados-form">
    <!-- Header con navegación -->
    <div class="page-header">
      <div class="header-content">
        <nav class="breadcrumb">
          <router-link to="/gestion-informacion/centros-poblados" class="breadcrumb-link">
            <i class="material-icons">location_city</i>
            Centros Poblados
          </router-link>
          <i class="material-icons breadcrumb-separator">chevron_right</i>
          <span class="breadcrumb-current">
            {{ modoEdicion ? 'Editar Centro Poblado' : 'Nuevo Centro Poblado' }}
          </span>
        </nav>
        
        <h1 class="page-title">
          <i class="material-icons">{{ modoEdicion ? 'edit' : 'add_location' }}</i>
          {{ modoEdicion ? 'Editar Centro Poblado' : 'Crear Nuevo Centro Poblado' }}
        </h1>
        
        <p class="page-description">
          {{ modoEdicion 
            ? 'Modifique la información del centro poblado. Los cambios se guardarán al hacer clic en "Actualizar".' 
            : 'Complete la información del nuevo centro poblado. Los campos marcados con * son obligatorios.'
          }}
        </p>
      </div>
    </div>

    <!-- Estados de carga -->
    <div v-if="cargandoDatos" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Cargando información...</p>
    </div>

    <div v-else-if="error" class="error-container">
      <i class="material-icons">error</i>
      <h3>Error al cargar los datos</h3>
      <p>{{ error }}</p>
      <button @click="cargarDatos" class="btn btn-outline">
        <i class="material-icons">refresh</i>
        Reintentar
      </button>
    </div>

    <!-- Formulario -->
    <div v-else class="form-container">
      <form @submit.prevent="guardarCentro" class="centro-form">
        
        <!-- Filtros de Ubicación -->
        <div class="form-section">
          <div class="section-header">
            <h2 class="section-title">
              <i class="material-icons">place</i>
              Ubicación Geográfica
            </h2>
            <p class="section-description">
              Seleccione primero el departamento y luego el municipio
            </p>
          </div>
          
          <div class="form-grid">
            <!-- Filtro Departamento -->
            <div class="form-group">
              <label for="departamento" class="form-label required">
                Departamento
                <span class="contador-opciones">({{ departamentos.length }} disponibles)</span>
              </label>
              <select
                id="departamento"
                v-model="filtros.departamento"
                @change="onDepartamentoChange"
                class="form-select"
                :class="{ 'error': errores.departamento, 'has-selection': filtros.departamento }"
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
              <span v-if="errores.departamento" class="error-message">
                {{ errores.departamento }}
              </span>
            </div>

            <!-- Filtro Municipio -->
            <div class="form-group">
              <label for="municipio" class="form-label required">
                Municipio
                <span class="contador-opciones">({{ municipiosDisponibles.length }} disponibles)</span>
              </label>
              <select
                id="municipio"
                v-model="formulario.cod_municipio"
                @change="onMunicipioChange"
                class="form-select"
                :class="{ 
                  'error': errores.cod_municipio, 
                  'has-selection': formulario.cod_municipio,
                  'loading': cargandoMunicipios 
                }"
                :disabled="!filtros.departamento || cargandoMunicipios"
                required
              >
                <option value="">
                  {{ cargandoMunicipios ? 'Cargando municipios...' : 
                     !filtros.departamento ? 'Primero seleccione un departamento' : 'Seleccione un municipio' }}
                </option>
                <option 
                  v-for="mun in municipiosDisponibles" 
                  :key="mun.cod_municipio" 
                  :value="mun.cod_municipio"
                >
                  {{ mun.nom_municipio }} ({{ mun.cod_municipio }})
                </option>
              </select>
              <span v-if="errores.cod_municipio" class="error-message">
                {{ errores.cod_municipio }}
              </span>
              <span v-if="!filtros.departamento" class="help-text">
                Primero debe seleccionar un departamento
              </span>
            </div>
          </div>
        </div>

        <!-- Información del Centro Poblado -->
        <div class="form-section">
          <div class="section-header">
            <h2 class="section-title">
              <i class="material-icons">info</i>
              Datos del Centro Poblado
            </h2>
            <p class="section-description">
              Información específica del centro poblado
            </p>
          </div>
          
          <div class="form-grid">
            <!-- Código del Centro Poblado -->
            <div class="form-group">
              <label for="codigo" class="form-label required">
                Código del Centro Poblado
              </label>
              <input
                id="codigo"
                v-model="formulario.cod_centro_poblado"
                type="text"
                class="form-input"
                :class="{ 'error': errores.cod_centro_poblado }"
                placeholder="Ej: 13006015"
                :disabled="modoEdicion"
                maxlength="8"
                pattern="[0-9]{8}"
                @input="onCodigoInput"
                required
              />
              <span v-if="errores.cod_centro_poblado" class="error-message">
                {{ errores.cod_centro_poblado }}
              </span>
              <span class="help-text">
                {{ modoEdicion 
                  ? 'El código no puede modificarse una vez creado' 
                  : 'Código de 8 dígitos único (ej: 13006015)' 
                }}
              </span>
            </div>

            <!-- Nombre del Centro Poblado -->
            <div class="form-group">
              <label for="nombre" class="form-label required">
                Nombre del Centro Poblado
              </label>
              <input
                id="nombre"
                v-model="formulario.nom_centro_poblado"
                type="text"
                class="form-input"
                :class="{ 'error': errores.nom_centro_poblado }"
                placeholder="Ingrese el nombre del centro poblado"
                required
              />
              <span v-if="errores.nom_centro_poblado" class="error-message">
                {{ errores.nom_centro_poblado }}
              </span>
            </div>

            <!-- Área Oficial -->
            <div class="form-group">
              <label for="area" class="form-label">
                Área Oficial (Hectáreas)
              </label>
              <input
                id="area"
                v-model="formulario.area_oficial_ha"
                type="text"
                class="form-input"
                :class="{ 'error': errores.area_oficial_ha }"
                placeholder="Ej: 150.5 Ha"
              />
              <span v-if="errores.area_oficial_ha" class="error-message">
                {{ errores.area_oficial_ha }}
              </span>
              <span class="help-text">
                Área oficial en hectáreas (opcional)
              </span>
            </div>
          </div>
        </div>

        <!-- Información de Referencia (Solo vista) -->
        <div v-if="municipioSeleccionado" class="form-section info-section">
          <div class="section-header">
            <h2 class="section-title">
              <i class="material-icons">location_on</i>
              Información de Ubicación
            </h2>
          </div>
          
          <div class="info-display">
            <div class="info-item">
              <span class="info-label">Departamento:</span>
              <span class="info-value">{{ departamentoSeleccionado?.nom_depto }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Municipio:</span>
              <span class="info-value">{{ municipioSeleccionado.nom_municipio }} ({{ municipioSeleccionado.cod_municipio }})</span>
            </div>
          </div>
        </div>

        <!-- Botones de acción -->
        <div class="form-actions">
          <div class="actions-left">
            <router-link 
              to="/gestion-informacion/centros-poblados" 
              class="btn btn-outline"
            >
              <i class="material-icons">arrow_back</i>
              Cancelar
            </router-link>
          </div>
          
          <div class="actions-right">
            <button 
              v-if="modoEdicion"
              type="button" 
              @click="resetearFormulario"
              class="btn btn-outline"
              :disabled="guardando"
            >
              <i class="material-icons">refresh</i>
              Resetear
            </button>
            
            <button 
              type="submit" 
              class="btn btn-primary"
              :disabled="guardando || !formularioValido"
            >
              <i v-if="guardando" class="material-icons spinning">sync</i>
              <i v-else class="material-icons">{{ modoEdicion ? 'save' : 'add' }}</i>
              {{ guardando ? 'Guardando...' : (modoEdicion ? 'Actualizar' : 'Crear') }}
            </button>
          </div>
        </div>
      </form>
    </div>

    <!-- Modal de confirmación -->
    <div v-if="mostrarModalConfirmacion" class="modal-overlay" @click="cancelarConfirmacion">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Confirmar Acción</h3>
          <button @click="cancelarConfirmacion" class="modal-close">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="confirmation-icon">
            <i class="material-icons">{{ modoEdicion ? 'edit' : 'add_location' }}</i>
          </div>
          <p>
            ¿Está seguro de que desea {{ modoEdicion ? 'actualizar' : 'crear' }} 
            este centro poblado?
          </p>
          <div class="centro-preview">
            <div class="preview-item">
              <strong>Código:</strong> {{ formulario.cod_centro_poblado }}
            </div>
            <div class="preview-item">
              <strong>Nombre:</strong> {{ formulario.nom_centro_poblado }}
            </div>
            <div class="preview-item">
              <strong>Municipio:</strong> {{ municipioSeleccionado?.nom_municipio }}
            </div>
            <div class="preview-item">
              <strong>Área:</strong> {{ formulario.area_oficial_ha || 'No especificada' }}
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="cancelarConfirmacion" class="btn btn-outline">
            Cancelar
          </button>
          <button @click="confirmarGuardado" class="btn btn-primary">
            <i class="material-icons">{{ modoEdicion ? 'save' : 'add' }}</i>
            {{ modoEdicion ? 'Actualizar' : 'Crear' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

// Importar APIs REALES
import { departamentosApi, getMunicipiosByDepartamento } from '@/api/municipios'
import { centrosPobladosApi } from '@/api/centrosPoblados'
import type { CentroPoblado } from '@/models/centroPoblado'

// Interfaces simplificadas para el formulario
interface CentroPobladoForm {
  cod_centro_poblado: string
  cod_municipio: string
  nom_centro_poblado: string
  area_oficial_ha: string
}

interface Departamento {
  cod_depto: number
  nom_depto: string
}

interface Municipio {
  cod_municipio: number
  nom_municipio: string
  cod_depto: number
}

export default defineComponent({
  name: 'CentrosPobladosForm',
  
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    // Estado reactivo
    const cargandoDatos = ref(false)
    const cargandoMunicipios = ref(false)
    const guardando = ref(false)
    const mostrarModalConfirmacion = ref(false)
    const error = ref<string | null>(null)
    
    // Datos
    const departamentos = ref<Departamento[]>([])
    const municipios = ref<Municipio[]>([])
    const errores = ref<Record<string, string>>({})
    
    // Filtros para selección
    const filtros = ref({
      departamento: ''
    })
    
    // Modo de edición
    const modoEdicion = computed(() => !!route.params.id)
    const centroId = computed(() => route.params.id as string)
    
    // Formulario simplificado con solo 4 campos
    const formulario = ref<CentroPobladoForm>({
      cod_centro_poblado: '',
      cod_municipio: '',
      nom_centro_poblado: '',
      area_oficial_ha: ''
    })
    
    // Computed properties
    const municipiosDisponibles = computed(() => {
      if (!filtros.value.departamento) return []
      
      return municipios.value
        .filter(m => m.cod_depto.toString() === filtros.value.departamento.toString())
        .sort((a, b) => a.nom_municipio.localeCompare(b.nom_municipio))
    })
    
    const municipioSeleccionado = computed(() => 
      municipios.value.find(m => m.cod_municipio.toString() === formulario.value.cod_municipio.toString())
    )
    
    const departamentoSeleccionado = computed(() => 
      departamentos.value.find(d => d.cod_depto.toString() === filtros.value.departamento.toString())
    )
    
    const formularioValido = computed(() => {
      return (formulario.value.cod_centro_poblado?.toString().trim() || '') !== '' &&
             formulario.value.cod_municipio !== '' &&
             (formulario.value.nom_centro_poblado?.trim() || '') !== '' &&
             Object.keys(errores.value).length === 0
    })
    
    // Métodos principales
    const cargarDatos = async () => {
      try {
        cargandoDatos.value = true
        error.value = null
        
        console.log('🚀 Cargando datos iniciales...')
        
        // 1. Cargar departamentos
        const deptosData = await departamentosApi.getAll()
        departamentos.value = Array.isArray(deptosData) ? deptosData : []
        console.log('✅ Departamentos cargados:', departamentos.value.length)
        
        // 2. Si estamos en modo edición, cargar datos del centro poblado
        if (modoEdicion.value) {
          await cargarCentroPoblado()
        }
        
      } catch (err) {
        console.error('❌ Error al cargar datos:', err)
        error.value = `Error al cargar datos: ${err.message}`
      } finally {
        cargandoDatos.value = false
      }
    }
    
    const cargarCentroPoblado = async () => {
      try {
        console.log('🔍 Cargando centro poblado para edición:', centroId.value)
        
        // ✅ CARGA REAL desde la API
        const centroData = await centrosPobladosApi.getById(centroId.value)
        
        // Asignar datos del centro poblado
        formulario.value = {
          cod_centro_poblado: centroData.cod_centro_poblado || '',
          cod_municipio: centroData.cod_municipio?.toString() || '',
          nom_centro_poblado: centroData.nom_centro_poblado || '',
          area_oficial_ha: centroData.area_oficial_ha || ''
        }
        
        console.log('📋 Datos del centro cargados:', formulario.value)
        
        // Buscar el municipio correspondiente para configurar filtros
        let municipioData = municipios.value.find(m => 
          m.cod_municipio.toString() === formulario.value.cod_municipio
        )
        
        // Si no se encuentra el municipio, intentar cargarlo
        if (!municipioData && formulario.value.cod_municipio) {
          console.log('🔍 Municipio no encontrado, determinando departamento...')
          
          // Intentar determinar el departamento por el código del municipio
          // Los primeros 2 dígitos del código de municipio suelen indicar el departamento
          const codigoMunicipio = parseInt(formulario.value.cod_municipio)
          const codigoDepartamento = Math.floor(codigoMunicipio / 1000)
          
          // Buscar el departamento
          const departamento = departamentos.value.find(d => d.cod_depto === codigoDepartamento)
          
          if (departamento) {
            console.log(`📍 Departamento encontrado: ${departamento.nom_depto}`)
            filtros.value.departamento = departamento.cod_depto.toString()
            
            // Cargar municipios de ese departamento
            await cargarMunicipiosDelDepartamento()
            
            // Buscar de nuevo el municipio
            municipioData = municipios.value.find(m => 
              m.cod_municipio.toString() === formulario.value.cod_municipio
            )
          }
        }
        
        // Si encontramos el municipio, configurar el filtro de departamento
        if (municipioData) {
          filtros.value.departamento = municipioData.cod_depto.toString()
          if (municipios.value.filter(m => m.cod_depto === municipioData.cod_depto).length === 0) {
            await cargarMunicipiosDelDepartamento()
          }
          console.log('✅ Filtros configurados correctamente')
        } else {
          console.warn('⚠️ No se pudo encontrar información del municipio')
        }
        
        console.log('✅ Centro poblado cargado para edición exitosamente')
        
      } catch (error) {
        console.error('❌ Error cargando centro poblado:', error)
        error.value = `Error al cargar el centro poblado: ${error.message}`
        throw error
      }
    }
    
    const cargarMunicipiosDelDepartamento = async () => {
      if (!filtros.value.departamento) return
      
      try {
        cargandoMunicipios.value = true
        console.log('📍 Cargando municipios del departamento:', filtros.value.departamento)
        
        const municipiosData = await getMunicipiosByDepartamento(parseInt(filtros.value.departamento))
        const municipiosNuevos = Array.isArray(municipiosData) ? municipiosData : []
        
        if (municipiosNuevos.length > 0) {
          // Agregar municipios sin duplicados
          const municipiosIds = new Set(municipios.value.map(m => m.cod_municipio))
          const municipiosFiltrados = municipiosNuevos.filter(m => !municipiosIds.has(m.cod_municipio))
          
          municipios.value = [...municipios.value, ...municipiosFiltrados]
          console.log(`✅ ${municipiosNuevos.length} municipios cargados del departamento`)
        }
        
      } catch (err) {
        console.error('❌ Error al cargar municipios del departamento:', err)
        error.value = `Error al cargar municipios: ${err.message}`
      } finally {
        cargandoMunicipios.value = false
      }
    }
    
    const validarFormulario = () => {
      const nuevosErrores: Record<string, string> = {}
      
      // Validar código del centro poblado (VARCHAR de 8 dígitos)
      const codigo = (formulario.value.cod_centro_poblado?.toString().trim() || '')
      if (!codigo) {
        nuevosErrores.cod_centro_poblado = 'El código es obligatorio'
      } else if (!/^\d{8}$/.test(codigo)) {
        nuevosErrores.cod_centro_poblado = 'El código debe tener exactamente 8 dígitos'
      }
      
      // Validar municipio (debe ser un número válido)
      const municipioId = formulario.value.cod_municipio?.toString().trim()
      if (!municipioId) {
        nuevosErrores.cod_municipio = 'Debe seleccionar un municipio'
      } else {
        const municipioNum = parseInt(municipioId)
        if (isNaN(municipioNum) || municipioNum <= 0) {
          nuevosErrores.cod_municipio = 'Código de municipio inválido'
        }
      }
      
      // Validar nombre
      const nombre = (formulario.value.nom_centro_poblado?.trim() || '')
      if (!nombre) {
        nuevosErrores.nom_centro_poblado = 'El nombre es obligatorio'
      } else if (nombre.length < 3) {
        nuevosErrores.nom_centro_poblado = 'El nombre debe tener al menos 3 caracteres'
      } else if (nombre.length > 200) {
        nuevosErrores.nom_centro_poblado = 'El nombre no puede exceder 200 caracteres'
      }
      
      // Validar área (opcional, pero si se proporciona debe ser válida)
      const area = formulario.value.area_oficial_ha?.trim()
      if (area && area.length > 100) {
        nuevosErrores.area_oficial_ha = 'El área no puede exceder 100 caracteres'
      }
      
      // Validar departamento (filtro)
      if (!filtros.value.departamento) {
        nuevosErrores.departamento = 'Debe seleccionar un departamento'
      }
      
      errores.value = nuevosErrores
      return Object.keys(nuevosErrores).length === 0
    }
    
    // Event handlers
    const onDepartamentoChange = async () => {
      // Limpiar municipio seleccionado
      formulario.value.cod_municipio = ''
      
      // Limpiar error de departamento
      if (errores.value.departamento) {
        delete errores.value.departamento
      }
      
      if (filtros.value.departamento) {
        await cargarMunicipiosDelDepartamento()
      }
    }
    
    const onMunicipioChange = () => {
      // Limpiar error de municipio
      if (errores.value.cod_municipio) {
        delete errores.value.cod_municipio
      }
    }
    
    const onCodigoInput = (event: Event) => {
      const target = event.target as HTMLInputElement
      // Permitir solo números
      const valor = target.value.replace(/[^0-9]/g, '')
      formulario.value.cod_centro_poblado = valor
    }
    
    const guardarCentro = () => {
      if (validarFormulario()) {
        mostrarModalConfirmacion.value = true
      }
    }
    
    const confirmarGuardado = async () => {
      try {
        guardando.value = true
        mostrarModalConfirmacion.value = false
        
        console.log('💾 Guardando centro poblado:', formulario.value)
        
        // ✅ IMPLEMENTAR GUARDADO REAL
        try {
          if (modoEdicion.value) {
            // Actualizar centro poblado existente
            await centrosPobladosApi.update(centroId.value, formulario.value)
            console.log('✅ Centro poblado actualizado en la BD')
          } else {
            // Crear nuevo centro poblado
            await centrosPobladosApi.create(formulario.value)
            console.log('✅ Centro poblado creado en la BD')
          }
          
          // Mensaje de éxito
          alert(`Centro poblado ${modoEdicion.value ? 'actualizado' : 'creado'} exitosamente`)
          
          // Redirigir a la lista
          router.push('/gestion-informacion/centros-poblados')
          
        } catch (apiError) {
          console.error('❌ Error en la API:', apiError)
          
          // Si la API falla, mostrar error específico
          if (apiError.response?.status === 400) {
            alert('Error de validación: Verifique que todos los datos sean correctos')
          } else if (apiError.response?.status === 409) {
            alert('Error: Ya existe un centro poblado con ese código')
          } else {
            alert(`Error al guardar en la base de datos: ${apiError.message}`)
          }
        }
        
      } catch (error) {
        console.error('❌ Error general:', error)
        alert(`Error inesperado: ${error.message}`)
      } finally {
        guardando.value = false
      }
    }
    
    const cancelarConfirmacion = () => {
      mostrarModalConfirmacion.value = false
    }
    
    const resetearFormulario = () => {
      if (modoEdicion.value) {
        cargarCentroPoblado()
      } else {
        formulario.value = {
          cod_centro_poblado: '',
          cod_municipio: '',
          nom_centro_poblado: '',
          area_oficial_ha: ''
        }
        filtros.value.departamento = ''
      }
      errores.value = {}
    }
    
    // Watchers para limpiar errores
    watch(() => formulario.value.cod_centro_poblado, () => {
      if (errores.value.cod_centro_poblado) {
        delete errores.value.cod_centro_poblado
      }
    })
    
    watch(() => formulario.value.nom_centro_poblado, () => {
      if (errores.value.nom_centro_poblado) {
        delete errores.value.nom_centro_poblado
      }
    })
    
    // Lifecycle
    onMounted(() => {
      cargarDatos()
    })
    
    return {
      // Estado
      cargandoDatos,
      cargandoMunicipios,
      guardando,
      mostrarModalConfirmacion,
      error,
      modoEdicion,
      
      // Datos
      departamentos,
      municipios,
      errores,
      filtros,
      formulario,
      
      // Computed
      municipiosDisponibles,
      municipioSeleccionado,
      departamentoSeleccionado,
      formularioValido,
      
      // Métodos
      cargarDatos,
      onDepartamentoChange,
      onMunicipioChange,
      onCodigoInput,
      guardarCentro,
      confirmarGuardado,
      cancelarConfirmacion,
      resetearFormulario
    }
  }
})
</script>

<style scoped>
.centros-poblados-form {
  padding: 1.5rem;
  max-width: 1000px;
  margin: 0 auto;
}

/* Header */
.page-header {
  margin-bottom: 2rem;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.breadcrumb-link {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #3b82f6;
  text-decoration: none;
}

.breadcrumb-link:hover {
  text-decoration: underline;
}

.breadcrumb-separator {
  color: #9ca3af;
  font-size: 1rem;
}

.breadcrumb-current {
  color: #6b7280;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.5rem 0;
  font-size: 1.75rem;
  font-weight: 600;
  color: #1f2937;
}

.page-description {
  color: #6b7280;
  margin: 0;
  font-size: 1rem;
}

/* Estados */
.loading-container, .error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-container i {
  font-size: 3rem;
  color: #ef4444;
  margin-bottom: 1rem;
}

/* Formulario */
.form-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.centro-form {
  padding: 2rem;
}

.form-section {
  margin-bottom: 2.5rem;
}

.form-section:last-of-type {
  margin-bottom: 0;
}

.section-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.section-description {
  color: #6b7280;
  margin: 0;
  font-size: 0.875rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-label.required::after {
  content: ' *';
  color: #ef4444;
}

.contador-opciones {
  color: #6c757d;
  font-size: 0.75rem;
  font-weight: normal;
  background-color: #f8f9fa;
  padding: 0.15rem 0.4rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.form-input,
.form-select {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input.error,
.form-select.error {
  border-color: #ef4444;
}

.form-input:disabled,
.form-select:disabled {
  background: #f9fafb;
  color: #6b7280;
  cursor: not-allowed;
}

.form-select.has-selection {
  border-color: #3b82f6;
  background-color: #f0f8ff;
  font-weight: 500;
}

.form-select.loading {
  background-image: url("data:image/svg+xml,%3csvg width='16' height='16' viewBox='0 0 16 16' fill='none' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='M8 2v2M8 12v2M13.657 8h-2M4.343 8h-2M11.314 4.686l-1.414 1.414M6.1 9.9l-1.414 1.414M11.314 11.314l-1.414-1.414M6.1 6.1L4.686 4.686' stroke='%23007bff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 16px;
}

.error-message {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.help-text {
  color: #6b7280;
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

/* Sección de información */
.info-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  margin-top: 1rem;
}

.info-display {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.info-value {
  font-size: 1rem;
  color: #1f2937;
  font-weight: 500;
}

/* Botones de acción */
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.actions-left,
.actions-right {
  display: flex;
  gap: 1rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  text-decoration: none;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 120px;
  justify-content: center;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-outline {
  background: white;
  color: #374151;
  border-color: #d1d5db;
}

.btn-outline:hover:not(:disabled) {
  background: #f3f4f6;
}

.spinning {
  animation: spin 1s linear infinite;
}

/* Modal */
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
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  color: #6b7280;
}

.modal-body {
  padding: 1.5rem;
  text-align: center;
}

.confirmation-icon {
  margin-bottom: 1rem;
}

.confirmation-icon i {
  font-size: 3rem;
  color: #3b82f6;
}

.centro-preview {
  background: #f3f4f6;
  padding: 1rem;
  border-radius: 6px;
  margin: 1rem 0;
  text-align: left;
}

.preview-item {
  margin-bottom: 0.5rem;
}

.preview-item:last-child {
  margin-bottom: 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

/* Responsive */
@media (max-width: 768px) {
  .centros-poblados-form {
    padding: 1rem;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .actions-left,
  .actions-right {
    width: 100%;
    justify-content: center;
  }
  
  .info-display {
    grid-template-columns: 1fr;
  }
}
</style>