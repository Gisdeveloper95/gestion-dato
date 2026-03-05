<template>
  <div class="gestion-inicio">
    <!-- Resumen de estadísticas -->
    <EstadisticasGestion />
    
    <!-- Accesos rápidos (modificado) -->
    <div class="panel-section">
      <h2 class="section-title">Accesos Rápidos</h2>
      
      <!-- Primera fila: Nuevo Detalle y Consultar Detalles -->
      <div class="quick-actions first-row">
        <router-link to="/gestion-informacion/detalles/crear" class="action-card blue-card">
          <div class="action-icon">
            <i class="material-icons">post_add</i>
          </div>
          <h3 class="action-title">Nuevo Detalle</h3>
          <p class="action-description">Añadir detalle a una clasificación</p>
        </router-link>
        
        <router-link to="/gestion-informacion/detalles" class="action-card green-card">
          <div class="action-icon">
            <i class="material-icons">search</i>
          </div>
          <h3 class="action-title">Consultar Detalles</h3>
          <p class="action-description">Ver y gestionar detalles registrados</p>
        </router-link>
      </div>
      
      <!-- Segunda fila: Nuevo Concepto y Consultar Conceptos -->
      <div class="quick-actions second-row">
        <router-link to="/gestion-informacion/conceptos/crear" class="action-card purple-card">
          <div class="action-icon">
            <i class="material-icons">note_add</i>
          </div>
          <h3 class="action-title">Nuevo Concepto</h3>
          <p class="action-description">Registrar un nuevo concepto para un detalle</p>
        </router-link>
        
        <router-link to="/gestion-informacion/conceptos" class="action-card orange-card">
          <div class="action-icon">
            <i class="material-icons">description</i>
          </div>
          <h3 class="action-title">Consultar Conceptos</h3>
          <p class="action-description">Ver y gestionar conceptos registrados</p>
        </router-link>
      </div>
    </div>
    
    <!-- Actividad reciente -->
    <ActividadRecenteGestion />
    
    <!-- Flujo de trabajo recomendado (modificado) -->
    <div class="panel-section">
      <h2 class="section-title">Flujo de Trabajo Recomendado</h2>
      
      <div class="workflow-steps">
        <div class="workflow-step">
          <div class="step-number">1</div>
          <div class="step-content">
            <h3>Seleccionar Municipio</h3>
            <p>Elija el municipio en el que desea trabajar desde la sección de Municipios.</p>
            <router-link to="/gestion-informacion/municipios" class="step-link">
              Ir a Municipios
              <i class="material-icons">arrow_forward</i>
            </router-link>
          </div>
        </div>
        
        <div class="workflow-step">
          <div class="step-number">2</div>
          <div class="step-content">
            <h3>Seleccionar Insumo y Clasificación</h3>
            <p>Busque y seleccione un insumo y clasificación ya existentes para trabajar.</p>
            <router-link to="/gestion-informacion/clasificaciones" class="step-link">
              Ver Clasificaciones
              <i class="material-icons">arrow_forward</i>
            </router-link>
          </div>
        </div>
        
        <div class="workflow-step">
          <div class="step-number">3</div>
          <div class="step-content">
            <h3>Agregar Detalle</h3>
            <p>Registre los detalles específicos de la clasificación, como escalas, estado, etc.</p>
            <router-link to="/gestion-informacion/detalles/crear" class="step-link">
              Agregar Detalle
              <i class="material-icons">arrow_forward</i>
            </router-link>
          </div>
        </div>
        
        <div class="workflow-step">
          <div class="step-number">4</div>
          <div class="step-content">
            <h3>Crear Concepto</h3>
            <p>Finalmente, registre el concepto asociado al detalle del insumo.</p>
            <router-link to="/gestion-informacion/conceptos/crear" class="step-link">
              Crear Concepto
              <i class="material-icons">arrow_forward</i>
            </router-link>
          </div>
        </div>
      </div>
      
      <!-- Nota informativa nueva -->
      <div class="info-note">
        <i class="material-icons">info</i>
        <p>Los insumos y clasificaciones se generan automáticamente por el sistema. Solo se requiere la creación manual de detalles y conceptos.</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import EstadisticasGestion from '@/pages/gestion/auditoria/components/EstadisticasGestion.vue'
import ActividadRecenteGestion from '@/pages/gestion/auditoria/components/ActividadRecenteGestion.vue'

export default defineComponent({
  name: 'GestionInicio',
  
  components: {
    EstadisticasGestion,
    ActividadRecenteGestion
  },
  
  setup() {
    // Estado para ayudar con botones de refresh
    const cargandoEstadisticas = ref(false)
    
    // Método para refrescar estadísticas (puede ser usado por algún botón)
    const actualizarEstadisticas = async () => {
      if (cargandoEstadisticas.value) return
      
      try {
        cargandoEstadisticas.value = true
        // Usando ref para acceder al componente
        const estadisticasComp = ref<any>(null)
        if (estadisticasComp.value && typeof estadisticasComp.value.cargarEstadisticas === 'function') {
          await estadisticasComp.value.cargarEstadisticas()
        }
      } catch (error) {
        console.error("Error al actualizar estadísticas:", error)
      } finally {
        cargandoEstadisticas.value = false
      }
    }
    
    // Inicializar
    onMounted(() => {
      // Nada que hacer aquí, los componentes se encargan de su propia inicialización
    })
    
    return {
      cargandoEstadisticas,
      actualizarEstadisticas
    }
  }
})
</script>

<style scoped>
.gestion-inicio {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Secciones de panel */
.panel-section {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.section-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0 0 1.5rem;
  color: #343a40;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.section-title::after {
  content: '';
  flex: 1;
  height: 1px;
  background-color: #e9ecef;
  margin-left: 0.5rem;
}

/* Acciones rápidas */
.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.second-row {
  margin-top: 0.5rem;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
  text-decoration: none;
  color: #343a40;
  transition: transform 0.2s, box-shadow 0.2s;
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

/* Colores para las tarjetas */
.blue-card {
  background-color: #e8f4ff;
  border: 1px solid #c9e2ff;
}

.blue-card .action-icon {
  background-color: rgba(0, 123, 255, 0.1);
}

.blue-card .action-icon i {
  color: #007bff;
}

.green-card {
  background-color: #e8f8ed;
  border: 1px solid #c3e6d1;
}

.green-card .action-icon {
  background-color: rgba(40, 167, 69, 0.1);
}

.green-card .action-icon i {
  color: #28a745;
}

.purple-card {
  background-color: #f0e7f7;
  border: 1px solid #dbc7e9;
}

.purple-card .action-icon {
  background-color: rgba(111, 66, 193, 0.1);
}

.purple-card .action-icon i {
  color: #6f42c1;
}

.orange-card {
  background-color: #fff3e6;
  border: 1px solid #ffddb3;
}

.orange-card .action-icon {
  background-color: rgba(253, 126, 20, 0.1);
}

.orange-card .action-icon i {
  color: #fd7e14;
}

.action-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.action-icon i {
  font-size: 2rem;
}

.action-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 0.5rem;
}

.action-description {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}

/* Flujo de trabajo */
.workflow-steps {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.workflow-step {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #007bff;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #007bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-content h3 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: #343a40;
}

.step-content p {
  margin: 0 0 0.75rem;
  color: #6c757d;
}

.step-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #007bff;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.step-link:hover {
  color: #0056b3;
  text-decoration: underline;
}

/* Nota informativa nueva */
.info-note {
  margin-top: 1.5rem;
  padding: 1rem;
  background-color: #e8f4ff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.info-note i {
  font-size: 1.5rem;
  color: #007bff;
  flex-shrink: 0;
}

.info-note p {
  margin: 0;
  color: #495057;
}

/* Responsive */
@media (max-width: 768px) {
  .quick-actions {
    grid-template-columns: 1fr;
  }
  
  .workflow-step {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}
</style>