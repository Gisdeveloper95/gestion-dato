<template>
  <div class="municipio-detalle-page">
    <div class="page-header">
      <div class="header-content">
        <h1>Detalle del Municipio</h1>
        <div class="header-actions">
          <button @click="goBack" class="btn-outline">
            <i class="material-icons">arrow_back</i>
            Volver
          </button>
          <button @click="editMunicipio" class="btn-primary">
            <i class="material-icons">edit</i>
            Editar Municipio
          </button>
        </div>
      </div>
    </div>

    <!-- Estados de carga y errores -->
    <div v-if="loading" class="loading-indicator">
      <div class="spinner"></div>
      <p>Cargando datos...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <i class="material-icons">error</i>
      <p>{{ error }}</p>
      <button @click="goBack" class="btn-primary">Volver</button>
    </div>

    <!-- Contenido principal -->
    <div v-else-if="municipio" class="main-content">
      <div class="detail-card">
        <div class="card-header">
          <div class="municipio-info">
            <div class="municipio-icon">
              <i class="material-icons">location_city</i>
            </div>
            <div class="municipio-title">
              <h2>{{ municipio.nom_municipio }}</h2>
              <span class="codigo-badge">Código: {{ municipio.cod_municipio }}</span>
            </div>
          </div>
        </div>
        
        <div class="card-body">
          <!-- Información básica -->
          <div class="detail-section">
            <h3>Información Básica</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Código:</span>
                <span class="info-value">{{ municipio.cod_municipio }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Nombre:</span>
                <span class="info-value">{{ municipio.nom_municipio }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Departamento:</span>
                <span class="info-value">{{ getDepartamentoNombre(municipio) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Fecha de inicio:</span>
                <span class="info-value">{{ formatDate(municipio.fecha_inicio) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Área:</span>
                <span class="info-value">{{ municipio.area || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Territorial:</span>
                <span class="info-value">{{ municipio.nom_territorial || 'N/A' }}</span>
              </div>
            </div>
          </div>

          <!-- Información de mecanismos -->
          <div class="detail-section">
            <h3>Información de Mecanismos</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Mecanismo General:</span>
                <span class="info-value">{{ municipio.mecanismo_general || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Mecanismo Detalle:</span>
                <span class="info-value">{{ municipio.mecanismo_detalle || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Mecanismo Operación:</span>
                <span class="info-value">{{ municipio.mecanismo_operacion || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Alcance Operación:</span>
                <span class="info-value">{{ municipio.alcance_operacion || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Grupo:</span>
                <span class="info-value">{{ getGrupoDescripcion(municipio.grupo) }}</span>
              </div>
            </div>
          </div>

          <!-- Profesionales de Seguimiento -->
          <div class="detail-section">
            <h3>Profesionales de Seguimiento</h3>
            <div v-if="!profesionalesValidos || profesionalesValidos.length === 0" class="empty-message">
              <p>No hay profesionales asignados a este municipio</p>
            </div>
            <div v-else class="profesionales-list">
              <div 
                v-for="prof in profesionalesValidos" 
                :key="prof.cod_profesional"
                class="profesional-item"
              >
                <div class="profesional-icon">
                  <i class="material-icons">person</i>
                </div>
                <div class="profesional-info">
                  <div class="profesional-name">{{ prof.nombre_profesional || 'Sin nombre' }}</div>
                  <div class="profesional-rol">{{ prof.rol_profesional || 'Sin rol' }}</div>
                  <div class="profesional-email" v-if="prof.correo_profesional">
                    <i class="material-icons">email</i>
                    {{ prof.correo_profesional }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- ============= REEMPLAZAR TODA LA SECCIÓN "Información Administrativa" CON ESTO ============= -->

          <!-- Información Administrativa CON PESTAÑAS -->
          <div class="detail-section">
            <h3>
              Información Administrativa Catastral
              <span v-if="todosInfoAdministrativa.length > 0" class="registro-counter-detalle">
                ({{ todosInfoAdministrativa.length }} registro{{ todosInfoAdministrativa.length > 1 ? 's' : '' }})
              </span>
            </h3>
            
            <div v-if="todosInfoAdministrativa.length > 0">
              <!-- 🆕 PESTAÑAS (solo mostrar si hay más de 1 registro) -->
              <div v-if="todosInfoAdministrativa.length > 1" class="tabs-container-detalle">
                <div class="tabs-header-detalle">
                  <button 
                    v-for="(registro, index) in todosInfoAdministrativa" 
                    :key="`tab-info-${index}`"
                    class="tab-button-detalle"
                    :class="{ 'active': tabActivaInfoAdmin === index }"
                    @click="cambiarTabInfoAdmin(index)"
                  >
                    <div class="tab-main-content">
                      <i class="material-icons">assessment</i>
                      <span class="tab-title">Registro {{ index + 1 }}</span>
                    </div>
                    <div v-if="registro.vigencia_rural || registro.vigencia_urbana" class="tab-vigencias-detalle">
                      <span v-if="registro.vigencia_rural" class="vigencia-rural-detalle">
                        <i class="material-icons">landscape</i>
                        {{ registro.vigencia_rural }}
                      </span>
                      <span v-if="registro.vigencia_urbana" class="vigencia-urbana-detalle">
                        <i class="material-icons">location_city</i>
                        {{ registro.vigencia_urbana }}
                      </span>
                    </div>
                  </button>
                </div>
              </div>
              
              <!-- 🆕 CONTENIDO DEL REGISTRO ACTIVO -->
              <div v-if="infoAdministrativa" class="tab-content-detalle">
                <!-- Información General -->
                <div class="subsection">
                  <h4>Información General</h4>
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">ID Gestor Catastral:</span>
                      <span class="info-value">{{ infoAdministrativa.id_gestor_catas || 'N/A' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Gestor/Prestador de Servicio:</span>
                      <span class="info-value">{{ infoAdministrativa.gestor_prestador_servicio || 'N/A' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Año de Publicación:</span>
                      <span class="info-value">{{ infoAdministrativa.publicacion_year || 'N/A' }}</span>
                    </div>
                  </div>
                </div>

                <!-- Información Rural -->
                <div class="subsection">
                  <h4>Información Rural</h4>
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">Vigencia Rural:</span>
                      <span class="info-value">{{ infoAdministrativa.vigencia_rural || 'N/A' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Estado Rural:</span>
                      <span class="info-value">{{ infoAdministrativa.estado_rural || 'N/A' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Predios Rurales:</span>
                      <span class="info-value">{{ formatNumber(infoAdministrativa.predios_rurales) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Área Terreno Rural:</span>
                      <span class="info-value">{{ formatArea(infoAdministrativa.area_terreno_rural_m2) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Área Terreno Rural (ha):</span>
                      <span class="info-value">{{ formatArea(infoAdministrativa.area_terreno_rural_ha, 'ha') }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Área Construida Rural:</span>
                      <span class="info-value">{{ formatArea(infoAdministrativa.area_construida_rural_m2) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Avalúo Rural:</span>
                      <span class="info-value">{{ formatCurrency(infoAdministrativa.avaluo_rural) }}</span>
                    </div>
                  </div>
                </div>

                <!-- Información Urbana -->
                <div class="subsection">
                  <h4>Información Urbana</h4>
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">Vigencia Urbana:</span>
                      <span class="info-value">{{ infoAdministrativa.vigencia_urbana || 'N/A' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Estado Urbano:</span>
                      <span class="info-value">{{ infoAdministrativa.estado_urbano || 'N/A' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Predios Urbanos:</span>
                      <span class="info-value">{{ formatNumber(infoAdministrativa.predios_urbanos) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Área Terreno Urbana:</span>
                      <span class="info-value">{{ formatArea(infoAdministrativa.area_terreno_urbana_m2) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Área Terreno Urbana (ha):</span>
                      <span class="info-value">{{ formatArea(infoAdministrativa.area_terreno_urbana_ha, 'ha') }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Área Construida Urbana:</span>
                      <span class="info-value">{{ formatArea(infoAdministrativa.area_construida_urbana_m2) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Avalúo Urbano 1:</span>
                      <span class="info-value">{{ formatCurrency(infoAdministrativa.avaluo_urbano_1) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Avalúo Urbano 2:</span>
                      <span class="info-value">{{ formatCurrency(infoAdministrativa.avaluo_urbano_2) }}</span>
                    </div>
                  </div>
                </div>

                <!-- Totales -->
                <div class="subsection">
                  <h4>Totales</h4>
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">Total Predios:</span>
                      <span class="info-value">{{ formatNumber(infoAdministrativa.total_predios) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Total Área Terreno:</span>
                      <span class="info-value">{{ formatArea(infoAdministrativa.total_area_terreno_m2) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Total Área Terreno (ha):</span>
                      <span class="info-value">{{ formatArea(infoAdministrativa.total_area_terreno_ha, 'ha') }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Total Área Construida:</span>
                      <span class="info-value">{{ formatArea(infoAdministrativa.total_area_construida_m2) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Total Avalúos:</span>
                      <span class="info-value">{{ formatCurrency(infoAdministrativa.total_avaluos) }}</span>
                    </div>
                  </div>
                </div>

                <!-- Áreas Geográficas -->
                <div class="subsection">
                  <h4>Áreas Geográficas y Estados Catastrales</h4>
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">Área Geográfica Rural:</span>
                      <span class="info-value">{{ formatArea(infoAdministrativa.area_geografica_rural_ha, 'ha') }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Área Geográfica Urbana:</span>
                      <span class="info-value">{{ formatArea(infoAdministrativa.area_geografica_urbana_ha, 'ha') }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Área Rural Estados Catastrales:</span>
                      <span class="info-value">{{ formatArea(infoAdministrativa.area_rural_estados_catastrales_ha, 'ha') }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">Área Urbana Estados Catastrales:</span>
                      <span class="info-value">{{ formatArea(infoAdministrativa.area_urbana_estados_catastrales_ha, 'ha') }}</span>
                    </div>
                  </div>
                </div>

                <!-- Observaciones -->
                <div v-if="infoAdministrativa.observacion" class="subsection">
                  <h4>Observaciones</h4>
                  <div class="observation-box">
                    {{ infoAdministrativa.observacion }}
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else class="empty-message">
              <i class="material-icons">info</i>
              <p>No hay información administrativa disponible para este municipio</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getMunicipioById } from '@/api/municipios';
import { getInfoAdministrativaByMunicipio, getTodosInfoAdministrativaPorMunicipio } from '@/api/infoAdministrativa';
import { getGrupos } from '@/api/insumos';
import { format, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';
import api from '@/api/config';
import type { InfoAdministrativa } from '@/models/infoAdministrativa';

export default defineComponent({
  name: 'MunicipioDetalle',
  
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  
  setup(props) {
    const route = useRoute();
    const router = useRouter();
    
    // Estado general
    const loading = ref(false);
    const error = ref<string | null>(null);
    const municipio = ref<any | null>(null);
    const profesionales = ref<any[]>([]);
    const infoAdministrativa = ref<InfoAdministrativa | null>(null);
    const todosInfoAdministrativa = ref<InfoAdministrativa[]>([])
    const tabActivaInfoAdmin = ref(0)
    // Datos maestros
    const grupos = ref<any[]>([]);
    
    // Computed para profesionales válidos (filtrar nulls y objetos incompletos)
    const profesionalesValidos = computed(() => {
      return profesionales.value.filter(prof => 
        prof && 
        prof.cod_profesional !== null && 
        prof.cod_profesional !== undefined
      );
    });
    
    // Cargar datos del municipio
    onMounted(async () => {
      await loadMunicipioData();
    });
    
    const loadMunicipioData = async () => {
      try {
        loading.value = true;
        error.value = null;
        
        const municipioId = Number(props.id);
        
        // Cargar datos maestros primero
        try {
          const gruposData = await getGrupos();
          grupos.value = gruposData || [];
        } catch (err) {
          console.warn('Error cargando grupos:', err);
          grupos.value = [];
        }
        
        // Cargar datos del municipio
        const municipioData = await getMunicipioById(municipioId);
        municipio.value = municipioData;
        
        // Cargar información administrativa
      try {
        console.log('🔍 Intentando cargar info administrativa para municipio:', municipioId);
        
        // 🆕 NUEVO: Cargar TODOS los registros de información administrativa
        const todosInfoAdminData = await getTodosInfoAdministrativaPorMunicipio(municipioId);
        console.log('📊 Respuesta de TODOS los registros de info administrativa:', todosInfoAdminData);
        todosInfoAdministrativa.value = todosInfoAdminData;
        
        // Mantener compatibilidad: usar el primer registro como principal
        if (todosInfoAdminData && todosInfoAdminData.length > 0) {
          infoAdministrativa.value = todosInfoAdminData[0];
          console.log('✅ Info administrativa cargada correctamente:', {
            total_registros: todosInfoAdminData.length,
            cod_municipio: todosInfoAdminData[0].cod_municipio,
            vigencia_rural: todosInfoAdminData[0].vigencia_rural,
            vigencia_urbana: todosInfoAdminData[0].vigencia_urbana
          });
        } else {
          console.warn('⚠️ No se recibieron registros de información administrativa');
          infoAdministrativa.value = null;
        }
        
        // Resetear tab activa
        tabActivaInfoAdmin.value = 0;
        
      } catch (err) {
        console.error('❌ Error al cargar información administrativa:', err);
        infoAdministrativa.value = null;
        todosInfoAdministrativa.value = [];
      }
        
        // Cargar profesionales asignados
        try {
          const response = await api.get(`/preoperacion/municipios/${municipioId}/profesionales/`);
          
          // Validar que la respuesta sea un array
          if (Array.isArray(response)) {
            profesionales.value = response;
          } else if (response && response.results && Array.isArray(response.results)) {
            profesionales.value = response.results;
          } else {
            profesionales.value = [];
          }
          
          console.log('Profesionales cargados:', profesionales.value);
        } catch (err) {
          console.warn('No se pudieron cargar los profesionales:', err);
          profesionales.value = [];
        }
        
      } catch (err: any) {
        console.error('Error cargando datos del municipio:', err);
        error.value = 'Error cargando datos del municipio. Por favor, intente nuevamente.';
      } finally {
        loading.value = false;
      }
    };
    
    const cambiarTabInfoAdmin = (index: number) => {
      tabActivaInfoAdmin.value = index
      // Actualizar infoAdministrativa para compatibilidad con el resto del código
      if (todosInfoAdministrativa.value[index]) {
        infoAdministrativa.value = todosInfoAdministrativa.value[index]
      }
    }

    // Métodos de utilidad
    const formatDate = (dateString: string | null): string => {
      if (!dateString) return 'No definida';
      try {
        return format(parseISO(dateString), 'dd/MM/yyyy', { locale: es });
      } catch (error) {
        return 'No definida';
      }
    };
    
    const formatNumber = (value: string | number | undefined): string => {
      if (!value) return 'N/A';
      const num = typeof value === 'string' ? parseFloat(value) : value;
      if (isNaN(num)) return 'N/A';
      return new Intl.NumberFormat('es-CO').format(num);
    };
    
    const formatCurrency = (value: string | number | undefined): string => {
      if (!value) return 'N/A';
      const num = typeof value === 'string' ? parseFloat(value) : value;
      if (isNaN(num)) return 'N/A';
      return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(num);
    };
    
    const formatArea = (value: string | number | undefined, unit: string = 'm²'): string => {
      if (!value) return 'N/A';
      const num = typeof value === 'string' ? parseFloat(value) : value;
      if (isNaN(num)) return 'N/A';
      return `${new Intl.NumberFormat('es-CO').format(num)} ${unit}`;
    };
    
    const getDepartamentoNombre = (municipio: any): string => {
      if (!municipio) return 'N/A';
      
      // Si el departamento está anidado
      if (municipio.departamento && municipio.departamento.nom_depto) {
        return municipio.departamento.nom_depto;
      }
      
      // Si cod_depto es un objeto
      if (municipio.cod_depto && typeof municipio.cod_depto === 'object' && municipio.cod_depto.nom_depto) {
        return municipio.cod_depto.nom_depto;
      }
      
      return 'N/A';
    };
    
    const getGrupoDescripcion = (grupoId: string): string => {
      if (!grupoId) return 'N/A';
      const grupo = grupos.value.find(g => g.cod_grupo === grupoId);
      return grupo ? (grupo.descripcion || grupo.cod_grupo) : grupoId;
    };
    
    // Métodos de navegación
    const goBack = () => {
      router.back();
    };
    
    const editMunicipio = () => {
      router.push(`/gestion-informacion/municipios/${props.id}/editar`);
    };
    
    return {
      loading,
      error,
      municipio,
      profesionales,
      profesionalesValidos,
      infoAdministrativa,
      formatDate,
      formatNumber,
      formatCurrency,
      formatArea,
      getDepartamentoNombre,
      getGrupoDescripcion,
      goBack,
      editMunicipio,
      todosInfoAdministrativa,
      tabActivaInfoAdmin,
      cambiarTabInfoAdmin
    };
  }
});
</script>

<style scoped>
.registro-counter-detalle {
  color: #6c757d;
  font-size: 0.9rem;
  font-weight: normal;
  background-color: #e3f2fd;
  color: #0d47a1;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  border: 1px solid #bbdefb;
  margin-left: 1rem;
  display: inline-flex;
  align-items: center;
  vertical-align: middle;
}

/* Contenedor de pestañas para página de detalle */
.tabs-container-detalle {
  margin: 1.5rem 0;
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border: 1px solid #dee2e6;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.tabs-header-detalle {
  display: flex;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-bottom: 2px solid #dee2e6;
  overflow-x: auto;
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

.tabs-header-detalle::-webkit-scrollbar {
  height: 6px;
}

.tabs-header-detalle::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.tabs-header-detalle::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.tabs-header-detalle::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* Botones de pestañas para página de detalle */
.tab-button-detalle {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 200px;
  padding: 1.25rem 1rem;
  background: none;
  border: none;
  border-right: 1px solid #dee2e6;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 0.9rem;
  font-weight: 500;
  color: #6c757d;
  text-align: center;
  gap: 0.5rem;
  position: relative;
  overflow: hidden;
}

.tab-button-detalle:last-child {
  border-right: none;
}

.tab-button-detalle::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transition: left 0.5s;
}

.tab-button-detalle:hover::before {
  left: 100%;
}

.tab-button-detalle:hover {
  background: linear-gradient(135deg, #e9ecef, #f8f9fa);
  color: #495057;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.tab-button-detalle.active {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 123, 255, 0.3);
  position: relative;
  z-index: 1;
}

.tab-button-detalle.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 12px solid transparent;
  border-right: 12px solid transparent;
  border-bottom: 10px solid white;
}

/* Contenido principal de cada pestaña */
.tab-main-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.tab-main-content i {
  font-size: 1.5rem;
  margin-bottom: 0.25rem;
}

.tab-title {
  font-weight: 600;
  font-size: 0.95rem;
}

/* Vigencias en las pestañas de detalle */
.tab-vigencias-detalle {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.vigencia-rural-detalle,
.vigencia-urbana-detalle {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-weight: 600;
  line-height: 1;
  transition: all 0.2s;
}

.vigencia-rural-detalle {
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.2), rgba(40, 167, 69, 0.1));
  color: #155724;
  border: 1px solid rgba(40, 167, 69, 0.3);
}

.tab-button-detalle.active .vigencia-rural-detalle {
  background: rgba(255, 255, 255, 0.25);
  color: white;
  border-color: rgba(255, 255, 255, 0.4);
}

.vigencia-urbana-detalle {
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.2), rgba(255, 193, 7, 0.1));
  color: #856404;
  border: 1px solid rgba(255, 193, 7, 0.3);
}

.tab-button-detalle.active .vigencia-urbana-detalle {
  background: rgba(255, 255, 255, 0.25);
  color: white;
  border-color: rgba(255, 255, 255, 0.4);
}

.vigencia-rural-detalle i,
.vigencia-urbana-detalle i {
  font-size: 0.85rem;
}

/* Contenido de las pestañas para página de detalle */
.tab-content-detalle {
  background-color: white;
  padding: 2rem;
  border-radius: 0 0 12px 12px;
  animation: fadeInDetalle 0.4s ease-out;
  box-shadow: inset 0 4px 8px rgba(0, 0, 0, 0.05);
}

@keyframes fadeInDetalle {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Mejorar el mensaje de vacío */
.detail-section .empty-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
  color: #6c757d;
  margin-top: 1.5rem;
  border: 2px dashed #dee2e6;
  text-align: center;
}

.detail-section .empty-message i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #adb5bd;
  opacity: 0.7;
}

.detail-section .empty-message p {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 500;
}

/* Efectos hover para las subsecciones cuando hay pestañas activas */
.tab-content-detalle .subsection {
  transition: all 0.2s ease;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  background: linear-gradient(135deg, #ffffff, #fafafa);
  border: 1px solid #f0f0f0;
}

.tab-content-detalle .subsection:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.tab-content-detalle .subsection h4 {
  color: #495057;
  margin-bottom: 1.25rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e9ecef;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tab-content-detalle .subsection h4::before {
  content: '📊';
  font-size: 1.1rem;
}


.municipio-detalle-page {
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

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.loading-indicator,
.error-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
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

.main-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-card {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.card-header {
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.municipio-info {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.municipio-icon {
  width: 56px;
  height: 56px;
  background-color: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.municipio-icon i {
  font-size: 2rem;
}

.municipio-title h2 {
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
  color: #343a40;
}

.codigo-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  border-radius: 4px;
  font-weight: 500;
  background-color: #e3f2fd;
  color: #0d47a1;
}

.card-body {
  padding: 0;
}

.detail-section {
  padding: 1.5rem;
  border-bottom: 1px solid #dee2e6;
}

.detail-section:last-child {
  border-bottom: none;
}

.detail-section h3 {
  margin: 0 0 1rem;
  font-size: 1.25rem;
  color: #343a40;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.875rem;
  color: #6c757d;
  font-weight: 500;
}

.info-value {
  font-size: 1rem;
  color: #212529;
  font-weight: 500;
  word-break: break-word;
}

.empty-message {
  color: #6c757d;
  padding: 1rem 0;
}

.profesionales-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.profesional-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.profesional-icon {
  width: 48px;
  height: 48px;
  background-color: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.profesional-info {
  flex: 1;
}

.profesional-name {
  font-weight: 500;
  color: #212529;
  font-size: 1.05rem;
}

.profesional-rol {
  color: #6c757d;
  font-size: 0.9rem;
  margin-top: 0.25rem;
}

.profesional-email {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #495057;
  font-size: 0.85rem;
  margin-top: 0.5rem;
}

.profesional-email i {
  font-size: 1rem;
  color: #6c757d;
}

/* Subsecciones para información administrativa */
.subsection {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e9ecef;
}

.subsection:first-child {
  margin-top: 0;
  padding-top: 0;
  border-top: none;
}

.subsection h4 {
  margin: 0 0 1rem;
  font-size: 1.1rem;
  color: #495057;
  font-weight: 600;
}

.observation-box {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 1rem;
  color: #6c757d;
  line-height: 1.6;
  white-space: pre-wrap;
}

/* Mejorar el grid para información administrativa */
.detail-section .info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
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

.btn-outline {
  background-color: transparent;
  border: 1px solid #ced4da;
  color: #495057;
}

.btn-outline:hover {
  background-color: #f8f9fa;
}

/* Responsive */
@media (max-width: 992px) {
  .tab-button-detalle {
    min-width: 160px;
    padding: 1rem 0.75rem;
    font-size: 0.85rem;
  }
  
  .tab-main-content i {
    font-size: 1.3rem;
  }
  
  .tab-title {
    font-size: 0.9rem;
  }
  
  .registro-counter-detalle {
    font-size: 0.8rem;
    padding: 0.2rem 0.6rem;
    margin-left: 0.75rem;
  }
}
@media (max-width: 768px) {
    .tab-button-detalle {
    min-width: 140px;
    padding: 0.875rem 0.5rem;
    font-size: 0.8rem;
  }
  
  .tab-vigencias-detalle {
    gap: 0.5rem;
    margin-top: 0.25rem;
  }
  
  .vigencia-rural-detalle,
  .vigencia-urbana-detalle {
    font-size: 0.7rem;
    padding: 0.2rem 0.4rem;
  }
  
  .tabs-header-detalle {
    justify-content: flex-start;
  }
  
  .tab-content-detalle {
    padding: 1.5rem;
  }
  
  .registro-counter-detalle {
    display: block;
    margin-left: 0;
    margin-top: 0.5rem;
    width: fit-content;
  }
  
  /* Hacer el título más compacto en móvil */
  .detail-section h3 {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 480px) {
  .tab-button-detalle {
    min-width: 120px;
    padding: 0.75rem 0.25rem;
    font-size: 0.75rem;
  }
  
  .tab-vigencias-detalle {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .tab-main-content i {
    font-size: 1.1rem;
  }
  
  .tab-title {
    font-size: 0.8rem;
  }
  
  .tab-content-detalle {
    padding: 1rem;
  }
  
  .tab-content-detalle .subsection {
    padding: 1rem;
    margin-bottom: 1rem;
  }
}
</style>