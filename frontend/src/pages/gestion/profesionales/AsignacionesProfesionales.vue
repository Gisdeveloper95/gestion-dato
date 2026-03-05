<template>
  <div class="asignaciones-page">
    <!-- Cabecera con título -->
    <div class="page-header">
      <div class="header-content">
        <h1>Gestión de Asignaciones</h1>
        <div class="header-actions">
          <button @click="irAsignacionesMasivas" class="btn-primary-outline">
            <i class="material-icons">library_add</i>
            Asignaciones Masivas
          </button>
          <button @click="goBack" class="btn-outline">
            <i class="material-icons">arrow_back</i>
            Volver a Profesionales
          </button>
        </div>
      </div>
    </div>

    <!-- Selector de profesional si no viene por query -->
    <div class="profesional-selector" v-if="!selectedProfesional">
      <div class="selector-content">
        <h2>Seleccione un profesional para gestionar sus asignaciones</h2>
        <select v-model="profesionalSeleccionado" @change="seleccionarProfesional">
          <option value="">Seleccione un profesional</option>
          <option 
            v-for="profesional in profesionales" 
            :key="profesional.cod_profesional" 
            :value="profesional.cod_profesional"
          >
            {{ profesional.nombre_profesional }} - {{ profesional.rol_profesional }}
          </option>
        </select>
      </div>
    </div>

    <!-- Contenido principal cuando hay profesional seleccionado -->
    <div v-else class="main-content">
      <!-- Información del profesional -->
      <div class="profesional-info-card">
        <div class="profesional-header">
          <div class="profesional-avatar">
            <i class="material-icons">person</i>
          </div>
          <div class="profesional-details">
            <h2>{{ selectedProfesional.nombre_profesional }}</h2>
            <p class="profesional-meta">
              <span>{{ selectedProfesional.cod_profesional }}</span>
              <span class="separator">•</span>
              <span>{{ selectedProfesional.correo_profesional || 'Sin correo' }}</span>
              <span class="separator">•</span>
              <span :class="['rol-badge', getRolClass(selectedProfesional.rol_profesional)]">
                {{ selectedProfesional.rol_profesional }}
              </span>
            </p>
          </div>
          <button @click="cambiarProfesional" class="btn-outline">
            Cambiar Profesional
          </button>
        </div>
      </div>

      <!-- Pestañas de asignaciones -->
      <div class="tabs-container">
        <div class="tabs-header">
          <div 
            :class="['tab', { active: activeTab === 'territoriales' }]"
            @click="activeTab = 'territoriales'"
          >
            <i class="material-icons">location_city</i>
            Territoriales
            <span class="badge">{{ asignacionesTerritoriales.length }}</span>
          </div>
          <div 
            :class="['tab', { active: activeTab === 'municipios' }]"
            @click="activeTab = 'municipios'"
          >
            <i class="material-icons">location_on</i>
            Municipios
            <span class="badge">{{ asignacionesMunicipios.length }}</span>
          </div>
        </div>

        <div class="tab-content">
          <!-- Pestaña de Territoriales -->
          <div v-if="activeTab === 'territoriales'" class="territoriales-tab">
            <div class="tab-actions">
              <button @click="showAddTerritorial = true" class="btn-primary">
                <i class="material-icons">add</i>
                Asignar Territorial
              </button>
            </div>

            <div v-if="asignacionesTerritoriales.length === 0" class="empty-state">
              <i class="material-icons">location_city</i>
              <p>No hay territoriales asignadas a este profesional.</p>
            </div>

            <div v-else class="asignaciones-list">
              <div 
                v-for="asignacion in asignacionesTerritoriales" 
                :key="asignacion.id" 
                class="asignacion-card"
              >
                <div class="asignacion-info">
                  <i class="material-icons">location_city</i>
                  <span>{{ asignacion.territorial_seguimiento }}</span>
                </div>
                <button @click="removeAsignacionTerritorial(asignacion)" class="btn-icon danger">
                  <i class="material-icons">delete</i>
                </button>
              </div>
            </div>
          </div>

          <!-- Pestaña de Municipios -->
          <div v-if="activeTab === 'municipios'" class="municipios-tab">
            <div class="tab-actions">
              <div class="filter-row">
                <div class="filter-item">
                  <label>Filtrar por departamento:</label>
                  <select v-model="filtroDepto" @change="handleDeptoChange">
                    <option value="">Todos los departamentos</option>
                    <option 
                      v-for="depto in departamentos" 
                      :key="depto.cod_depto" 
                      :value="depto.cod_depto"
                    >
                      {{ depto.nom_depto }}
                    </option>
                  </select>
                </div>
                <button @click="showAddMunicipio = true" class="btn-primary">
                  <i class="material-icons">add</i>
                  Asignar Municipio
                </button>
              </div>
            </div>

            <div v-if="filteredAsignacionesMunicipios.length === 0" class="empty-state">
              <i class="material-icons">location_on</i>
              <p>No hay municipios asignados {{ filtroDepto ? 'en este departamento.' : 'a este profesional.' }}</p>
            </div>

            <div v-else class="municipios-grid">
              <div 
                v-for="asignacion in filteredAsignacionesMunicipios" 
                :key="asignacion.id" 
                class="municipio-card"
              >
                <div class="municipio-info">
                  <i class="material-icons">location_on</i>
                  <div class="municipio-details">
                    <span class="municipio-nombre">{{ getMunicipioNombre(asignacion.cod_municipio) }}</span>
                    <span class="municipio-depto">{{ getDepartamentoNombre(asignacion.cod_municipio) }}</span>
                    <span class="municipio-territorial">
                      <i class="material-icons">business</i>
                      {{ getTerritorialesDelProfesional() }}
                    </span>
                  </div>
                </div>
                <button @click="removeAsignacionMunicipio(asignacion)" class="btn-icon danger">
                  <i class="material-icons">delete</i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal para asignar territorial -->
    <div v-if="showAddTerritorial" class="modal-backdrop" @click="closeModalTerritorial">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h2>Asignar Territorial</h2>
          <button class="close-btn" @click="closeModalTerritorial">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="addTerritorial" class="form">
            <div class="form-group">
              <label for="territorial">Territorial <span class="required">*</span></label>
              <select 
                id="territorial" 
                v-model="territorialToAdd" 
                required
              >
                <option value="">Seleccione una territorial</option>
                <option 
                  v-for="territorial in territorialesDisponibles" 
                  :key="territorial.nom_territorial" 
                  :value="territorial.nom_territorial"
                >
                  {{ territorial.nom_territorial }}
                </option>
              </select>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn-secondary" @click="closeModalTerritorial">Cancelar</button>
              <button type="submit" class="btn-primary">Asignar</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Modal para asignar municipio -->
    <div v-if="showAddMunicipio" class="modal-backdrop" @click="closeModalMunicipio">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h2>Asignar Municipio</h2>
          <button class="close-btn" @click="closeModalMunicipio">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="addMunicipio" class="form">
            <div class="form-row">
              <div class="form-group">
                <label for="depto">Departamento</label>
                <select 
                  id="depto" 
                  v-model="deptoSeleccionado" 
                  @change="handleModalDeptoChange"
                >
                  <option value="">Todos los departamentos</option>
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
                <label for="municipio">Municipio <span class="required">*</span></label>
                <select 
                  id="municipio" 
                  v-model="municipioToAdd" 
                  required
                >
                  <option value="">Seleccione un municipio</option>
                  <option 
                    v-for="municipio in municipiosDisponiblesModal" 
                    :key="municipio.cod_municipio" 
                    :value="municipio.cod_municipio"
                  >
                    {{ municipio.nom_municipio }}
                  </option>
                </select>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn-secondary" @click="closeModalMunicipio">Cancelar</button>
              <button type="submit" class="btn-primary">Asignar</button>
            </div>
          </form>
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
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/api/config'

export default defineComponent({
  name: 'AsignacionesProfesionales',
  
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    // Estado general
    const loading = ref(false)
    const error = ref<string | null>(null)
    
    // Datos
    const profesionales = ref<any[]>([])
    const territoriales = ref<any[]>([])
    const departamentos = ref<any[]>([])
    const municipios = ref<any[]>([])
    const asignacionesTerritoriales = ref<any[]>([])
    const asignacionesMunicipios = ref<any[]>([])
    
    // Selección
    const profesionalSeleccionado = ref('')
    const selectedProfesional = ref<any>(null)
    const activeTab = ref('territoriales')
    
    // Filtros
    const filtroDepto = ref('')
    const deptoSeleccionado = ref('')
    
    // Modales
    const showAddTerritorial = ref(false)
    const showAddMunicipio = ref(false)
    const territorialToAdd = ref('')
    const municipioToAdd = ref('')
    
    // Notificación
    const notification = ref({
      show: false,
      message: '',
      type: 'success',
      icon: 'check_circle',
      timeout: null as number | null
    })
    
    // Cargar datos iniciales
    onMounted(async () => {
      await loadInitialData()
      
      // Si viene un profesional por query, seleccionarlo
      const profesionalId = route.query.profesional?.toString()
      if (profesionalId) {
        profesionalSeleccionado.value = profesionalId
        await seleccionarProfesional()
      }
    })
    
    // Métodos de carga
    const loadInitialData = async () => {
      try {
       error.value = null
       
       const [
         profesionalesData,
         territorialesData,
         departamentosData,
         municipiosData
       ] = await Promise.all([
         api.get('/preoperacion/profesionales-seguimiento/'),
         api.get('/preoperacion/territoriales/'),
         api.get('/preoperacion/departamentos/'),
         api.get('/preoperacion/municipios/')
       ])
       
       profesionales.value = procesarDatos(profesionalesData)
       territoriales.value = procesarDatos(territorialesData)
       departamentos.value = procesarDatos(departamentosData)
       municipios.value = procesarDatos(municipiosData)
       
     } catch (err: any) {
       console.error('Error cargando datos:', err)
       error.value = 'Error cargando datos. Por favor, intente nuevamente.'
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
   
   const loadAsignaciones = async () => {
     if (!selectedProfesional.value) return
     
     try {
       const [territorialesData, municipiosData] = await Promise.all([
         api.get(`/preoperacion/profesional-territorial/?cod_profesional=${selectedProfesional.value.cod_profesional}`),
         api.get(`/preoperacion/profesional-municipio/?cod_profesional=${selectedProfesional.value.cod_profesional}`)
       ])
       
       asignacionesTerritoriales.value = procesarDatos(territorialesData)
       asignacionesMunicipios.value = procesarDatos(municipiosData)
     } catch (err: any) {
       console.error('Error cargando asignaciones:', err)
       showNotification('Error al cargar asignaciones', 'error')
     }
   }
   
   // Métodos de selección
   const seleccionarProfesional = async () => {
     const profesional = profesionales.value.find(p => p.cod_profesional === profesionalSeleccionado.value)
     if (profesional) {
       selectedProfesional.value = profesional
       await loadAsignaciones()
     }
   }
   
   const cambiarProfesional = () => {
     selectedProfesional.value = null
     profesionalSeleccionado.value = ''
     asignacionesTerritoriales.value = []
     asignacionesMunicipios.value = []
   }
   
   // Filtros computados
   const filteredAsignacionesMunicipios = computed(() => {
     if (!filtroDepto.value) return asignacionesMunicipios.value
     
     return asignacionesMunicipios.value.filter(asignacion => {
       const municipio = municipios.value.find(m => m.cod_municipio === asignacion.cod_municipio)
       return municipio && municipio.cod_depto.toString() === filtroDepto.value.toString()
     })
   })
   
   const territorialesDisponibles = computed(() => {
     const asignadas = asignacionesTerritoriales.value.map(a => a.territorial_seguimiento)
     return territoriales.value.filter(t => !asignadas.includes(t.nom_territorial))
   })
   
   const municipiosDisponiblesModal = computed(() => {
     const asignados = asignacionesMunicipios.value.map(a => a.cod_municipio)
     let disponibles = municipios.value.filter(m => !asignados.includes(m.cod_municipio))
     
     if (deptoSeleccionado.value) {
       disponibles = disponibles.filter(m => m.cod_depto.toString() === deptoSeleccionado.value.toString())
     }
     
     return disponibles
   })
   
   // Métodos de asignación
   const addTerritorial = async () => {
     if (!territorialToAdd.value || !selectedProfesional.value) return
     
     try {
       loading.value = true
       await api.post('/preoperacion/profesional-territorial/', {
         cod_profesional: selectedProfesional.value.cod_profesional,
         territorial_seguimiento: territorialToAdd.value
       })
       
       showNotification('Territorial asignada correctamente', 'success')
       await loadAsignaciones()
       closeModalTerritorial()
     } catch (err: any) {
       console.error('Error asignando territorial:', err)
       showNotification('Error al asignar territorial', 'error')
     } finally {
       loading.value = false
     }
   }
   
   const addMunicipio = async () => {
     if (!municipioToAdd.value || !selectedProfesional.value) return
     
     try {
       loading.value = true
       await api.post('/preoperacion/profesional-municipio/', {
         cod_profesional: selectedProfesional.value.cod_profesional,
         cod_municipio: parseInt(municipioToAdd.value)
       })
       
       showNotification('Municipio asignado correctamente', 'success')
       await loadAsignaciones()
       closeModalMunicipio()
     } catch (err: any) {
       console.error('Error asignando municipio:', err)
       showNotification('Error al asignar municipio', 'error')
     } finally {
       loading.value = false
     }
   }
   
   const removeAsignacionTerritorial = async (asignacion: any) => {
     if (!confirm(`¿Está seguro de quitar la asignación de ${asignacion.territorial_seguimiento}?`)) return
     
     try {
       loading.value = true
       await api.delete(`/preoperacion/profesional-territorial/${asignacion.id}/`)
       showNotification('Asignación eliminada correctamente', 'success')
       await loadAsignaciones()
     } catch (err: any) {
       console.error('Error eliminando asignación:', err)
       showNotification('Error al eliminar asignación', 'error')
     } finally {
       loading.value = false
     }
   }
   
   const removeAsignacionMunicipio = async (asignacion: any) => {
     const municipioNombre = getMunicipioNombre(asignacion.cod_municipio)
     if (!confirm(`¿Está seguro de quitar la asignación de ${municipioNombre}?`)) return
     
     try {
       loading.value = true
       await api.delete(`/preoperacion/profesional-municipio/${asignacion.id}/`)
       showNotification('Asignación eliminada correctamente', 'success')
       await loadAsignaciones()
     } catch (err: any) {
       console.error('Error eliminando asignación:', err)
       showNotification('Error al eliminar asignación', 'error')
     } finally {
       loading.value = false
     }
   }
   
   // Métodos auxiliares
   const getMunicipioNombre = (codMunicipio: number) => {
     const municipio = municipios.value.find(m => m.cod_municipio === codMunicipio)
     return municipio ? municipio.nom_municipio : 'Desconocido'
   }
   
   const getDepartamentoNombre = (codMunicipio: number) => {
     const municipio = municipios.value.find(m => m.cod_municipio === codMunicipio)
     if (!municipio) return 'Desconocido'
     
     const depto = departamentos.value.find(d => d.cod_depto === municipio.cod_depto)
     return depto ? depto.nom_depto : 'Desconocido'
   }
   
   const getTerritorialesDelProfesional = (): string => {
     if (!asignacionesTerritoriales.value || asignacionesTerritoriales.value.length === 0) {
       return 'Sin asignación territorial'
     }
     
     const territoriales = asignacionesTerritoriales.value
       .map(t => t.territorial_seguimiento)
       .filter(t => t && t.trim() !== '')
       .join(', ')
     
     return territoriales || 'Sin asignación territorial'
   }
   
   const getRolClass = (rol: string) => {
     const rolUpper = rol.toUpperCase()
     if (rolUpper.includes('L.A.S')) return 'las'
     if (rolUpper.includes('P.A.S')) return 'pas'
     return 'default'
   }
   
   // Métodos de modal
   const closeModalTerritorial = () => {
     showAddTerritorial.value = false
     territorialToAdd.value = ''
   }
   
   const closeModalMunicipio = () => {
     showAddMunicipio.value = false
     municipioToAdd.value = ''
     deptoSeleccionado.value = ''
   }
   
   const handleDeptoChange = () => {
     // No hacer nada, el filtro computado se actualiza automáticamente
   }
   
   const handleModalDeptoChange = () => {
     municipioToAdd.value = ''
   }
   
   // Notificaciones
   const showNotification = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
     if (notification.value.timeout) {
       clearTimeout(notification.value.timeout)
     }
     
     let icon = 'info'
     switch (type) {
       case 'success':
         icon = 'check_circle'
         break
       case 'error':
         icon = 'error'
         break
       case 'warning':
         icon = 'warning'
         break
     }
     
     notification.value = {
       show: true,
       message,
       type,
       icon,
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
   
   const goBack = () => {
     router.push('/gestion-informacion/profesionales')
   }

   const irAsignacionesMasivas = () => {
     router.push('/gestion-informacion/profesionales/asignaciones-masivas')
   }

   return {
     // Estado
     loading,
     error,
     profesionalSeleccionado,
     selectedProfesional,
     activeTab,
     filtroDepto,
     deptoSeleccionado,
     showAddTerritorial,
     showAddMunicipio,
     territorialToAdd,
     municipioToAdd,
     notification,
     
     // Datos
     profesionales,
     territoriales,
     departamentos,
     municipios,
     asignacionesTerritoriales,
     asignacionesMunicipios,
     filteredAsignacionesMunicipios,
     territorialesDisponibles,
     municipiosDisponiblesModal,
     
     // Métodos
     seleccionarProfesional,
     cambiarProfesional,
     addTerritorial,
     addMunicipio,
     removeAsignacionTerritorial,
     removeAsignacionMunicipio,
     getMunicipioNombre,
     getDepartamentoNombre,
     getTerritorialesDelProfesional,
     getRolClass,
     closeModalTerritorial,
     closeModalMunicipio,
     handleDeptoChange,
     handleModalDeptoChange,
     showNotification,
     closeNotification,
     goBack,
     irAsignacionesMasivas
   }
 }
})
</script>

<style scoped>
.asignaciones-page {
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

.profesional-selector {
 background-color: white;
 border-radius: 8px;
 padding: 2rem;
 box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.selector-content {
 max-width: 600px;
 margin: 0 auto;
 text-align: center;
}

.selector-content h2 {
 margin-bottom: 1.5rem;
 color: #343a40;
}

.selector-content select {
 width: 100%;
 padding: 0.75rem 1rem;
 border: 1px solid #ced4da;
 border-radius: 4px;
 font-size: 1rem;
}

.main-content {
 display: flex;
 flex-direction: column;
 gap: 1.5rem;
}

.profesional-info-card {
 background-color: white;
 border-radius: 8px;
 padding: 1.5rem;
 box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.profesional-header {
 display: flex;
 align-items: center;
 gap: 1.5rem;
}

.profesional-avatar {
 width: 80px;
 height: 80px;
 background-color: #0d6efd;
 color: white;
 border-radius: 50%;
 display: flex;
 align-items: center;
 justify-content: center;
 font-size: 2.5rem;
}

.profesional-details {
 flex: 1;
}

.profesional-details h2 {
 margin: 0 0 0.5rem;
 font-size: 1.5rem;
 color: #343a40;
}

.profesional-meta {
 display: flex;
 align-items: center;
 gap: 0.75rem;
 color: #6c757d;
}

.separator {
 font-size: 0.8rem;
}

.rol-badge {
 display: inline-block;
 padding: 0.25rem 0.5rem;
 font-size: 0.75rem;
 border-radius: 4px;
 font-weight: 600;
}

.rol-badge.las {
 background-color: #e3f2fd;
 color: #0d47a1;
}

.rol-badge.pas {
 background-color: #e8f5e9;
 color: #1b5e20;
}

.rol-badge.default {
 background-color: #f0f0f0;
 color: #495057;
}

.tabs-container {
 background-color: white;
 border-radius: 8px;
 overflow: hidden;
 box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.tabs-header {
 display: flex;
 background-color: #f8f9fa;
 border-bottom: 1px solid #dee2e6;
}

.tab {
 flex: 1;
 display: flex;
 align-items: center;
 justify-content: center;
 gap: 0.5rem;
 padding: 1rem;
 cursor: pointer;
 transition: background-color 0.2s;
 border-bottom: 3px solid transparent;
 color: #6c757d;
 font-weight: 500;
}

.tab:hover {
 background-color: rgba(0, 0, 0, 0.05);
}

.tab.active {
 color: #0d6efd;
 border-bottom-color: #0d6efd;
 background-color: white;
}

.tab i {
 font-size: 1.2rem;
}

.badge {
 display: inline-block;
 padding: 0.25em 0.5em;
 font-size: 0.75rem;
 font-weight: 700;
 background-color: #6c757d;
 color: white;
 border-radius: 10rem;
 min-width: 1.5rem;
 text-align: center;
}

.tab.active .badge {
 background-color: #0d6efd;
}

.tab-content {
 padding: 1.5rem;
}

.tab-actions {
 display: flex;
 justify-content: space-between;
 align-items: center;
 margin-bottom: 1.5rem;
}

.filter-row {
 display: flex;
 gap: 1rem;
 align-items: flex-end;
 width: 100%;
}

.filter-item {
 flex: 1;
 display: flex;
 flex-direction: column;
 gap: 0.25rem;
}

.filter-item label {
 font-size: 0.875rem;
 color: #6c757d;
 font-weight: 500;
}

.filter-item select {
 padding: 0.5rem;
 border: 1px solid #ced4da;
 border-radius: 4px;
}

.empty-state {
 display: flex;
 flex-direction: column;
 align-items: center;
 justify-content: center;
 padding: 3rem;
 text-align: center;
}

.empty-state i {
 font-size: 3rem;
 color: #6c757d;
 margin-bottom: 1rem;
}

.empty-state p {
 color: #6c757d;
}

.asignaciones-list {
 display: flex;
 flex-direction: column;
 gap: 0.75rem;
}

.asignacion-card {
 display: flex;
 justify-content: space-between;
 align-items: center;
 padding: 1rem;
 background-color: #f8f9fa;
 border-radius: 4px;
 border: 1px solid #dee2e6;
}

.asignacion-info {
 display: flex;
 align-items: center;
 gap: 0.75rem;
 font-size: 1rem;
 color: #343a40;
}

.asignacion-info i {
 color: #6c757d;
 font-size: 1.2rem;
}

.municipios-grid {
 display: grid;
 grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
 gap: 1rem;
}

.municipio-card {
 display: flex;
 justify-content: space-between;
 align-items: center;
 padding: 1rem;
 background-color: #f8f9fa;
 border-radius: 8px;
 border: 1px solid #dee2e6;
 transition: transform 0.2s, box-shadow 0.2s;
}

.municipio-card:hover {
 transform: translateY(-2px);
 box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.municipio-info {
 display: flex;
 align-items: center;
 gap: 0.75rem;
}

.municipio-info i {
 color: #6c757d;
 font-size: 1.2rem;
}

.municipio-details {
 display: flex;
 flex-direction: column;
 gap: 0.25rem;
}

.municipio-nombre {
 font-weight: 500;
 color: #343a40;
}

.municipio-depto {
 font-size: 0.875rem;
 color: #6c757d;
}

.municipio-territorial {
 font-size: 0.75rem;
 color: #17a2b8;
 display: flex;
 align-items: center;
 gap: 0.25rem;
 margin-top: 0.25rem;
 font-style: italic;
}

.municipio-territorial i {
 font-size: 0.9rem;
}

/* Modal */
.modal-backdrop {
 position: fixed;
 top: 0;
 left: 0;
 right: 0;
 bottom: 0;
 background-color: rgba(0, 0, 0, 0.5);
 display: flex;
 align-items: center;
 justify-content: center;
 z-index: 1000;
}

.modal-container {
 background-color: white;
 border-radius: 8px;
 box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
 width: 100%;
 max-width: 600px;
 max-height: 90vh;
 display: flex;
 flex-direction: column;
}

.modal-header {
 display: flex;
 justify-content: space-between;
 align-items: center;
 padding: 1rem 1.5rem;
 border-bottom: 1px solid #dee2e6;
}

.modal-header h2 {
 margin: 0;
 font-size: 1.25rem;
 color: #343a40;
}

.close-btn {
 background: none;
 border: none;
 color: #6c757d;
 cursor: pointer;
 font-size: 1.5rem;
 display: flex;
 align-items: center;
 justify-content: center;
}

.modal-body {
 padding: 1.5rem;
 overflow-y: auto;
}

.form {
 display: flex;
 flex-direction: column;
 gap: 1.5rem;
}

.form-row {
 display: flex;
 gap: 1rem;
 flex-wrap: wrap;
}

.form-group {
 flex: 1;
 min-width: 250px;
 display: flex;
 flex-direction: column;
 gap: 0.25rem;
}

.form-group label {
 font-size: 0.95rem;
 color: #495057;
 font-weight: 500;
}

.form-group .required {
 color: #dc3545;
}

.form-group select {
 padding: 0.5rem 0.75rem;
 border: 1px solid #ced4da;
 border-radius: 4px;
 font-size: 0.95rem;
}

.form-group select:focus {
 border-color: #4dabf7;
 box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
 outline: none;
}

.form-actions {
 display: flex;
 justify-content: flex-end;
 gap: 1rem;
 margin-top: 1rem;
}

/* Botones */
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

.btn-primary-outline {
 background-color: transparent;
 border: 1px solid #0d6efd;
 color: #0d6efd;
}

.btn-primary-outline:hover {
 background-color: #0d6efd;
 color: white;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
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

.btn-icon {
 display: flex;
 align-items: center;
 justify-content: center;
 width: 36px;
 height: 36px;
 border-radius: 4px;
 border: none;
 background-color: #f8f9fa;
 color: #495057;
 cursor: pointer;
 transition: background-color 0.2s;
}

.btn-icon:hover {
 background-color: #e9ecef;
}

.btn-icon.danger {
 background-color: rgba(220, 53, 69, 0.1);
 color: #dc3545;
}

.btn-icon.danger:hover {
 background-color: rgba(220, 53, 69, 0.2);
}

/* Notificaciones */
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
@media (max-width: 992px) {
 .header-content {
   flex-direction: column;
   align-items: flex-start;
   gap: 1rem;
 }
 
 .profesional-header {
   flex-direction: column;
   text-align: center;
 }
 
 .profesional-avatar {
   width: 60px;
   height: 60px;
   font-size: 2rem;
 }
 
 .profesional-meta {
   flex-direction: column;
   gap: 0.25rem;
 }
 
 .separator {
   display: none;
 }
 
 .municipios-grid {
   grid-template-columns: 1fr;
 }
}

@media (max-width: 768px) {
 .filter-row {
   flex-direction: column;
 }
 
 .tabs-header {
   flex-direction: column;
 }
 
 .tab {
   border-left: 3px solid transparent;
   border-bottom: none;
 }
 
 .tab.active {
   border-left-color: #0d6efd;
   border-bottom-color: transparent;
 }
 
 .form-row {
   flex-direction: column;
 }
 
 .form-group {
   min-width: 100%;
 }
 
 .notification {
   min-width: auto;
   max-width: 90%;
   left: 5%;
   right: 5%;
 }
}

@media (max-width: 576px) {
 .btn-primary,
 .btn-secondary,
 .btn-outline {
   padding: 0.5rem 0.75rem;
   font-size: 0.9rem;
 }
 
 .modal-container {
   max-width: 95%;
   margin: 0 2.5%;
 }
}
</style>