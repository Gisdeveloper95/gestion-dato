<template>
  <div class="insumo-detail-page">
    <!-- Cabecera con título y acciones -->
    <div class="page-header">
      <div class="header-content">
        <h1>Detalle de Insumo</h1>
        <div class="header-actions">
          <button @click="goBack" class="btn-outline">
            <i class="material-icons">arrow_back</i>
            Volver
          </button>
          <button @click="editInsumo" class="btn-primary">
            <i class="material-icons">edit</i>
            Editar Insumo
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
    <div v-else-if="insumo" class="main-content">
      <div class="detail-card">
        <div class="card-header">
          <div class="insumo-info">
            <div class="insumo-icon">
              <i class="material-icons">
                {{ insumo.tipo_insumo === 'Primario' ? 'folder_special' : 'folder_shared' }}
              </i>
            </div>
            <div class="insumo-title">
              <h2>Insumo {{ insumo.cod_insumo }}</h2>
              <span :class="['categoria-badge', getCategoriaClass(insumo.cod_categoria)]">
                {{ getNombreCategoria(insumo.cod_categoria) }}
              </span>
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
                <span class="info-value">{{ insumo.cod_insumo }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Municipio:</span>
                <span class="info-value">{{ municipioName }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Departamento:</span>
                <span class="info-value">{{ departamentoName }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Categoría:</span>
                <span class="info-value">{{ getNombreCategoria(insumo.cod_categoria) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Tipo de Insumo:</span>
                <span class="info-value">{{ getTipoInsumoNombre(insumo.tipo_insumo) }}</span>
              </div>
            </div>
          </div>
          
          <!-- Pestañas de contenido -->
          <div class="detail-tabs">
            <div 
              v-for="tab in tabs" 
              :key="tab.id"
              :class="['tab', { active: activeTab === tab.id }]"
              @click="activeTab = tab.id">
              <i class="material-icons">{{ tab.icon }}</i>
              {{ tab.label }}
            </div>
          </div>
          
          <div class="tab-content">
            <!-- Pestaña de Clasificaciones -->
            <div v-if="activeTab === 'clasificaciones'" class="clasificaciones-tab">
              <div class="tab-actions">
                <!-- Contador de clasificaciones -->
                <div class="clasificaciones-counter">
                  <div class="counter-info">
                    <i class="material-icons">category</i>
                    <span class="counter-text">
                      {{ clasificaciones.length }} {{ clasificaciones.length === 1 ? 'clasificación' : 'clasificaciones' }}
                    </span>
                  </div>
                </div>
              </div>
              
              <div v-if="clasificaciones.length === 0" class="empty-state">
                <i class="material-icons">category</i>
                <p>No hay clasificaciones registradas para este insumo.</p>
                <button @click="crearClasificacion" class="btn-primary">
                  <i class="material-icons">add</i>
                  Crear Clasificación
                </button>
              </div>
              
              <div v-else class="clasificaciones-list">
                <div 
                  v-for="clasificacion in clasificaciones" 
                  :key="clasificacion.cod_clasificacion" 
                  class="clasificacion-card"
                >
                  <div class="clasificacion-header">
                    <div class="clasificacion-title">
                      <h4>{{ clasificacion.nombre }}</h4>
                    </div>
                  </div>
                  
                  <div class="clasificacion-body">
                    <div class="detail-row">
                      <span class="detail-label">Código:</span>
                      <span class="detail-value">{{ clasificacion.cod_clasificacion }}</span>
                    </div>
                    <div class="detail-row" v-if="clasificacion.ruta">
                      <span class="detail-label">Ruta:</span>
                      <span class="detail-value path-value">{{ linuxToWindowsPath(clasificacion.ruta) }}</span>
                    </div>
                    <div class="detail-row" v-if="clasificacion.observacion">
                      <span class="detail-label">Observación:</span>
                      <span class="detail-value">{{ clasificacion.observacion }}</span>
                    </div>
                    <div class="detail-row" v-if="clasificacion.descripcion">
                      <span class="detail-label">Descripción:</span>
                      <span class="detail-value">{{ clasificacion.descripcion }}</span>
                    </div>
                  </div>
                  
                  <div class="clasificacion-footer">
                    <div class="detalles-badge">
                      <i class="material-icons">description</i>
                      {{ getDetallesCount(clasificacion.cod_clasificacion) }} detalles asociados
                    </div>
                    <button @click="verDetalles(clasificacion)" class="btn-text">
                      Ver detalles
                      <i class="material-icons">arrow_forward</i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Pestaña de Detalles -->
            <div v-else-if="activeTab === 'detalles'" class="detalles-tab">
              <div class="tab-actions">
                <div class="search-box">
                  <i class="material-icons">search</i>
                  <input 
                    type="text"
                    v-model="detalleSearch"
                    placeholder="Buscar detalle..."
                  />
                  <button v-if="detalleSearch" @click="detalleSearch = ''" class="clear-btn">
                    <i class="material-icons">close</i>
                  </button>
                </div>
                
                <div class="filter-item">
                  <label>Filtrar por clasificación:</label>
                  <select v-model="detalleFilter">
                    <option value="">Todas las clasificaciones</option>
                    <option 
                      v-for="clasificacion in clasificaciones" 
                      :key="clasificacion.cod_clasificacion" 
                      :value="clasificacion.cod_clasificacion"
                    >
                      {{ clasificacion.nombre }}
                    </option>
                  </select>
                </div>
                
                <!-- Contador de detalles dinámico -->
                <div class="detalles-counter">
                  <div class="counter-info">
                    <i class="material-icons">description</i>
                    <span v-if="!detalleSearch && !detalleFilter" class="counter-text">
                      {{ detalles.length }} {{ detalles.length === 1 ? 'detalle' : 'detalles' }}
                    </span>
                    <span v-else class="counter-text">
                      {{ filteredDetalles.length }} de {{ detalles.length }} {{ detalles.length === 1 ? 'detalle' : 'detalles' }}
                    </span>
                  </div>
                  
                  <!-- Indicador de filtros activos -->
                  <div v-if="detalleSearch || detalleFilter" class="filtros-activos">
                    <span v-if="detalleSearch" class="filtro-badge">
                      <i class="material-icons">search</i>
                      "{{ detalleSearch }}"
                      <button @click="detalleSearch = ''" class="remove-filter">
                        <i class="material-icons">close</i>
                      </button>
                    </span>
                    <span v-if="detalleFilter" class="filtro-badge">
                      <i class="material-icons">category</i>
                      {{ getNombreClasificacion(detalleFilter) }}
                      <button @click="detalleFilter = ''" class="remove-filter">
                        <i class="material-icons">close</i>
                      </button>
                    </span>
                    <button @click="limpiarFiltrosDetalles" class="btn-clear-all">
                      <i class="material-icons">clear_all</i>
                      Limpiar filtros
                    </button>
                  </div>
                </div>
                
                <button @click="crearDetalle" class="btn-primary">
                  <i class="material-icons">add</i>
                  Nuevo Detalle
                </button>
              </div>
              
              <div v-if="detalles.length === 0" class="empty-state">
                <i class="material-icons">description</i>
                <p>No hay detalles registrados para este insumo.</p>
                <button @click="crearDetalle" class="btn-primary">
                  <i class="material-icons">add</i>
                  Crear Detalle
                </button>
              </div>
              
              <div v-else class="detalles-table-container">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>Código</th>
                      <th>Clasificación</th>
                      <th>Escala</th>
                      <th>Estado</th>
                      <th>Entidad</th>
                      <th>Formato</th>
                      <th>Usuario</th>
                      <th>Fecha Entrega</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="detalle in filteredDetalles" :key="detalle.cod_detalle">
                      <td>{{ detalle.cod_detalle }}</td>
                      <td>{{ getNombreClasificacion(detalle.cod_clasificacion) }}</td>
                      <td>{{ detalle.escala || '-' }}</td>
                      <td>{{ detalle.estado || '-' }}</td>
                      <td>{{ getNombreEntidad(detalle.cod_entidad) }}</td>
                      <td>{{ detalle.formato_tipo }}</td>
                      <td>{{ getNombreUsuario(detalle.cod_usuario) }}</td>
                      <td>{{ formatDate(detalle.fecha_entrega) }}</td>
                      <td>
                        <div class="row-actions">
                          <button @click="editarDetalle(detalle)" class="btn-icon small warning" title="Editar">
                            <i class="material-icons">edit</i>
                          </button>
                          <button @click="showDeleteDetalleModal(detalle)" class="btn-icon small danger" title="Eliminar">
                            <i class="material-icons">delete</i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            <!-- Pestaña de Conceptos -->
            <div v-else-if="activeTab === 'conceptos'" class="conceptos-tab">
              <div class="tab-actions">
                <div class="search-box">
                  <i class="material-icons">search</i>
                  <input 
                    type="text"
                    v-model="conceptoSearch"
                    placeholder="Buscar concepto..."
                  />
                  <button v-if="conceptoSearch" @click="conceptoSearch = ''" class="clear-btn">
                    <i class="material-icons">close</i>
                  </button>
                </div>
                
                <!-- Contador de conceptos dinámico -->
                <div class="conceptos-counter">
                  <div class="counter-info">
                    <i class="material-icons">comment</i>
                    <span v-if="!conceptoSearch" class="counter-text">
                      {{ conceptos.length }} {{ conceptos.length === 1 ? 'concepto' : 'conceptos' }}
                    </span>
                    <span v-else class="counter-text">
                      {{ filteredConceptos.length }} de {{ conceptos.length }} {{ conceptos.length === 1 ? 'concepto' : 'conceptos' }}
                    </span>
                  </div>
                  
                  <!-- Indicador de filtro activo -->
                  <div v-if="conceptoSearch" class="filtros-activos">
                    <span class="filtro-badge">
                      <i class="material-icons">search</i>
                      "{{ conceptoSearch }}"
                      <button @click="conceptoSearch = ''" class="remove-filter">
                        <i class="material-icons">close</i>
                      </button>
                    </span>
                    <button @click="limpiarFiltrosConceptos" class="btn-clear-all">
                      <i class="material-icons">clear_all</i>
                      Limpiar filtro
                    </button>
                  </div>
                </div>
                
                <button @click="cargarConceptos" class="btn-outline" title="Recargar conceptos">
                  <i class="material-icons">refresh</i>
                  Actualizar
                </button>
              </div>
              
              <div v-if="cargandoConceptos" class="loading-indicator small">
                <div class="spinner"></div>
                <span>Cargando conceptos...</span>
              </div>
              
              <div v-else-if="errorConceptos" class="error-message small">
                <i class="material-icons">error</i>
                <p>{{ errorConceptos }}</p>
                <button @click="cargarConceptos" class="btn-primary">Reintentar</button>
              </div>
              
              <div v-else-if="conceptos.length === 0" class="empty-state">
                <i class="material-icons">comment</i>
                <p>No hay conceptos registrados para los detalles de este insumo.</p>
              </div>
              
              <div v-else class="conceptos-list">
                <div 
                  v-for="concepto in filteredConceptos" 
                  :key="concepto.cod_concepto" 
                  class="concepto-card"
                >
                  <div class="concepto-header">
                    <h4>{{ concepto.concepto }}</h4>
                    <div class="concepto-meta">
                      <span class="concepto-fecha">{{ formatDate(concepto.fecha) }}</span>
                      <span 
                        v-if="concepto.evaluacion" 
                        :class="['evaluacion-badge', getEvaluacionClass(concepto.evaluacion)]"
                      >
                        {{ concepto.evaluacion }}
                      </span>
                    </div>
                  </div>
                  
                  <div class="concepto-body">
                    <div class="concepto-table">
                      <div class="concepto-row">
                        <div class="concepto-cell header">Código</div>
                        <div class="concepto-cell">{{ concepto.cod_concepto }}</div>
                      </div>
                      
                      <div class="concepto-row">
                        <div class="concepto-cell header">Fecha</div>
                        <div class="concepto-cell">{{ formatDate(concepto.fecha) || 'No disponible' }}</div>
                      </div>
                      
                      <div class="concepto-row">
                        <div class="concepto-cell header">Evaluación</div>
                        <div class="concepto-cell">
                          <span :class="['evaluacion-badge', getEvaluacionClass(concepto.evaluacion)]">
                            {{ concepto.evaluacion || 'Sin evaluar' }}
                          </span>
                        </div>
                      </div>
                      
                      <div class="concepto-row">
                        <div class="concepto-cell header">Detalle asociado</div>
                        <div class="concepto-cell">{{ getDetalleNombre(concepto.cod_detalle) }}</div>
                      </div>
                    </div>
                    
                    <div v-if="concepto.detalle_concepto" class="concepto-detail-section">
                      <div class="concepto-detail-header">Detalle del concepto:</div>
                      <div class="concepto-detail-content">{{ concepto.detalle_concepto }}</div>
                    </div>
                    
                    <div v-if="concepto.observacion" class="concepto-observation-section">
                      <div class="concepto-observation-header">Observación:</div>
                      <div class="concepto-observation-content">{{ concepto.observacion }}</div>
                    </div>
                  </div>
                  
                  <div class="concepto-footer">
                    <div class="concepto-actions">
                      <button v-if="concepto.pdf" @click="verPDF(concepto.pdf)" class="btn-icon primary" title="Ver PDF">
                        <i class="material-icons">picture_as_pdf</i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Pestaña de Archivos -->
            <div v-else-if="activeTab === 'archivos'" class="archivos-tab">
              <div class="tab-actions">
                <div class="search-box">
                  <i class="material-icons">search</i>
                  <input 
                    type="text"
                    v-model="archivoSearch"
                    placeholder="Buscar archivo..."
                  />
                  <button v-if="archivoSearch" @click="archivoSearch = ''" class="clear-btn">
                    <i class="material-icons">close</i>
                  </button>
                </div>
                
                <div class="filter-item">
                  <label>Filtrar por clasificación:</label>
                  <select v-model="archivoFilter">
                    <option value="">Todas las clasificaciones</option>
                    <option 
                      v-for="clasificacion in clasificaciones" 
                      :key="clasificacion.cod_clasificacion" 
                      :value="clasificacion.cod_clasificacion"
                    >
                      {{ clasificacion.nombre }}
                    </option>
                  </select>
                </div>
                
                <!-- Contador de archivos dinámico -->
                <div class="archivos-counter">
                  <div class="counter-info">
                    <i class="material-icons">folder_open</i>
                    <span v-if="!archivoSearch && !archivoFilter" class="counter-text">
                      {{ archivos.length }} {{ archivos.length === 1 ? 'archivo' : 'archivos' }}
                    </span>
                    <span v-else class="counter-text">
                      {{ filteredArchivos.length }} de {{ archivos.length }} {{ archivos.length === 1 ? 'archivo' : 'archivos' }}
                    </span>
                  </div>
                  
                  <!-- Indicador de filtros activos -->
                  <div v-if="archivoSearch || archivoFilter" class="filtros-activos">
                    <span v-if="archivoSearch" class="filtro-badge">
                      <i class="material-icons">search</i>
                      "{{ archivoSearch }}"
                      <button @click="archivoSearch = ''" class="remove-filter">
                        <i class="material-icons">close</i>
                      </button>
                    </span>
                    <span v-if="archivoFilter" class="filtro-badge">
                      <i class="material-icons">category</i>
                      {{ getNombreClasificacion(archivoFilter) }}
                      <button @click="archivoFilter = ''" class="remove-filter">
                        <i class="material-icons">close</i>
                      </button>
                    </span>
                    <button @click="limpiarFiltrosArchivos" class="btn-clear-all">
                      <i class="material-icons">clear_all</i>
                      Limpiar filtros
                    </button>
                  </div>
                </div>
              </div>
              
              <div v-if="archivos.length === 0" class="empty-state">
                <i class="material-icons">insert_drive_file</i>
                <p>No hay archivos cargados para este insumo.</p>
                <button @click="cargarArchivo" class="btn-primary">
                  <i class="material-icons">upload_file</i>
                  Cargar Archivo
                </button>
              </div>
              
              <div v-else class="archivos-grid">
                <div 
                  v-for="archivo in filteredArchivos" 
                  :key="archivo.id_lista_archivo" 
                  class="archivo-card"
                >
                  <div class="archivo-header">
                    <div class="archivo-icon">
                      <i class="material-icons">{{ getFileIcon(archivo.nombre_insumo) }}</i>
                    </div>
                    <div class="archivo-title">
                      <h4>{{ archivo.nombre_insumo }}</h4>
                      <span class="archivo-fecha">{{ formatDate(archivo.fecha_disposicion) }}</span>
                    </div>
                  </div>
                  
                  <div class="archivo-body">
                    <div class="detail-row">
                      <span class="detail-label">Clasificación:</span>
                      <span class="detail-value">{{ getNombreClasificacion(archivo.cod_insumo) }}</span>
                    </div>
                    <div class="detail-row" v-if="archivo.path_file">
                      <span class="detail-label">Ruta:</span>
                      <span class="detail-value path-value">{{ linuxToWindowsPath(archivo.path_file) }}</span>
                    </div>
                    <div class="detail-row" v-if="archivo.observacion">
                      <span class="detail-label">Observación:</span>
                      <span class="detail-value">{{ archivo.observacion }}</span>
                    </div>
                  </div>
                  
                  <div class="archivo-footer">
                    <!-- Indicador de tipo de descarga -->
                    <div class="archivo-info">
                      <span v-if="getArchivoDescargaInfo(archivo.nombre_insumo)" class="descarga-badge">
                        {{ getArchivoDescargaInfo(archivo.nombre_insumo) }}
                      </span>
                    </div>
                    
                    <div class="archivo-actions">
                      <button 
                        @click="testearDescarga(archivo)" 
                        class="btn-icon warning" 
                        title="Probar descarga (Debug)"
                      >
                        <i class="material-icons">bug_report</i>
                      </button>
                      
                      <button 
                        @click="previewDescarga(archivo)" 
                        class="btn-icon info" 
                        title="Vista previa de descarga"
                        v-if="esArchivoComplejo(archivo.nombre_insumo)"
                      >
                        <i class="material-icons">info</i>
                      </button>
                      
                      <button @click="viewArchivo(archivo)" class="btn-icon primary" title="Ver archivo">
                        <i class="material-icons">visibility</i>
                      </button>
                      
                      <button 
                        @click="downloadArchivo(archivo)" 
                        class="btn-icon success" 
                        :title="getDownloadTitle(archivo.nombre_insumo)"
                        :disabled="descargandoArchivos.has(archivo.id_lista_archivo)"
                      >
                        <i class="material-icons" v-if="!descargandoArchivos.has(archivo.id_lista_archivo)">
                          download
                        </i>
                        <i class="material-icons spinning" v-else>
                          hourglass_top
                        </i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>          
          </div>
        </div>
      </div>
    </div>

    <!-- Modal para confirmación de eliminación -->
    <div v-if="showDeleteModal" class="modal-backdrop" @click="closeModals">
      <div class="modal-container delete-modal" @click.stop>
        <div class="modal-header">
          <h2>Confirmar Eliminación</h2>
          <button class="close-btn" @click="closeModals">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="delete-warning">
            <i class="material-icons">warning</i>
            <p>¿Está seguro que desea eliminar {{ deleteConfirmationText }}?</p>
            <p>Esta acción no se puede deshacer.</p>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeModals">Cancelar</button>
          <button class="btn-danger" @click="confirmDelete">Eliminar</button>
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
import { defineComponent, ref, computed, onMounted } from 'vue';
import { linuxToWindowsPath } from '@/utils/pathUtils';
import { useRoute, useRouter } from 'vue-router';
import { format, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';

// Importaciones de servicios API
import { 
  getInsumoById, 
  getClasificacionesByInsumo,
  getArchivosByClasificacion, 
  getCategorias, 
  getTiposInsumo,
  getEntidades,
  getUsuarios,
  getDetalles
} from '@/api/insumos';

import { API_URL } from '@/api/config';
import { getMunicipioById } from '@/api/municipios';
import { getDepartamentoById } from '@/api/departamentos';
import { getConceptos, getConceptosByDetalle } from '@/api/conceptos';
import { 
  getConceptosByMunicipio,
  verDocumentoPDF 
} from '@/api/conceptos';

export default defineComponent({
  name: 'InsumoDetalle',
  
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
    const insumo = ref<any | null>(null);
    const clasificaciones = ref<any[]>([]);
    const detalles = ref<any[]>([]);
    const archivos = ref<any[]>([]);
    const conceptos = ref<any[]>([]);
    const categorias = ref<any[]>([]);
    const tiposInsumo = ref<any[]>([]);
    const entidades = ref<any[]>([]);
    const usuarios = ref<any[]>([]);
    
    // Información adicional
    const municipioName = ref('');
    const departamentoName = ref('');
    
    // Estado de búsqueda y filtrado
    const detalleSearch = ref('');
    const detalleFilter = ref('');
    const archivoSearch = ref('');
    const archivoFilter = ref('');
    const conceptoSearch = ref('');
    
    // Pestaña activa
    const activeTab = ref('clasificaciones');
    
    // Tabs disponibles
    const tabs = [
      { id: 'clasificaciones', label: 'Clasificaciones', icon: 'category' },
      { id: 'detalles', label: 'Detalles', icon: 'description' },
      { id: 'archivos', label: 'Archivos', icon: 'insert_drive_file' },
      { id: 'conceptos', label: 'Conceptos', icon: 'comment' }
    ];
    
    // Estado del modal de eliminación
    const showDeleteModal = ref(false);
    const deleteType = ref('');
    const deleteItemId = ref<number | null>(null);
    const deleteConfirmationText = ref('');
    
    // Estado de notificación
    const notification = ref({
      show: false,
      message: '',
      type: 'success',
      icon: 'check_circle',
      timeout: null as number | null
    });
    
    // Estado para manejar descargas
    const descargandoArchivos = ref(new Set());
    const cargandoConceptos = ref(false);
    const errorConceptos = ref(null);
    
    // Cargar datos iniciales
    onMounted(async () => {
      await loadInsumoData();
    });
    
    const cargarConceptosDirectamente = async () => {
      try {
        if (!detalles.value || detalles.value.length === 0) {
          console.log("No hay detalles para buscar conceptos");
          conceptos.value = [];
          return;
        }
        
        const token = localStorage.getItem('token');
        if (!token) {
          console.error("No hay token disponible");
          return;
        }
        
        const response = await fetch(`${API_URL}/preoperacion/conceptos/`, {
          headers: {
            'Authorization': `Token ${token}`
          }
        });
        
        if (!response.ok) {
          throw new Error(`Error al cargar conceptos: ${response.status}`);
        }
        
        const data = await response.json();
        const allConceptos = data.results || data;
        const detallesIds = detalles.value.map(d => d.cod_detalle);
        
        conceptos.value = allConceptos.filter(concepto => 
          concepto.cod_detalle && detallesIds.includes(concepto.cod_detalle)
        );
        
        console.log(`Cargados ${conceptos.value.length} conceptos relacionados con este insumo`);
      } catch (error) {
        console.error("Error al cargar conceptos:", error);
        conceptos.value = [];
      }
    };
    
    // Método para cargar los datos del insumo y relacionados
    const loadInsumoData = async () => {
      try {
        loading.value = true;
        error.value = null;
        
        const insumoId = Number(props.id);
        
        // Cargar datos maestros primero
        const [categoriasData, tiposData, entidadesData, usuariosData] = await Promise.all([
          getCategorias(),
          getTiposInsumo(),
          getEntidades(),
          getUsuarios()
        ]);
        
        categorias.value = categoriasData;
        tiposInsumo.value = tiposData;
        entidades.value = entidadesData;
        usuarios.value = usuariosData;
        
        // Cargar datos del insumo
        const insumoData = await getInsumoById(insumoId);
        insumo.value = insumoData;
        
        // Cargar datos del municipio y departamento
        if (insumoData.cod_municipio) {
          const municipio = await getMunicipioById(insumoData.cod_municipio);
          municipioName.value = municipio.nom_municipio;
          
          const deptoId = typeof municipio.cod_depto === 'object' 
            ? municipio.cod_depto.cod_depto 
            : municipio.cod_depto;
          
          try {
            const departamento = await getDepartamentoById(deptoId);
            departamentoName.value = departamento.nom_depto;
          } catch (err) {
            console.warn(`No se pudo cargar el departamento con ID ${deptoId}`, err);
            departamentoName.value = 'No disponible';
          }
        }
        
        // Cargar clasificaciones
        const clasificacionesData = await getClasificacionesByInsumo(insumoId);
        clasificaciones.value = clasificacionesData;
        
        // Cargar detalles asociados al insumo
        try {
          const todosDetalles = await getDetalles();
          const clasificacionesIds = clasificacionesData.map(c => c.cod_clasificacion);
          const allDetalles = todosDetalles.filter(d => 
            clasificacionesIds.includes(d.cod_clasificacion)
          );
          detalles.value = allDetalles;
        } catch (err) {
          console.warn(`Error al cargar detalles para el insumo:`, err);
          detalles.value = [];
        }

        try {
          await cargarConceptosDirectamente();
        } catch (err) {
          console.warn('Error al cargar conceptos:', err);
          conceptos.value = [];
        }
        
        // Cargar archivos para todas las clasificaciones
        const allArchivos = [];
        for (const clasificacion of clasificacionesData) {
          try {
            const archivosClasificacion = await getArchivosByClasificacion(clasificacion.cod_clasificacion);
            allArchivos.push(...archivosClasificacion);
          } catch (err) {
            console.warn(`Error al cargar archivos para clasificación ${clasificacion.cod_clasificacion}:`, err);
          }
        }
        archivos.value = allArchivos;
        
      } catch (err: any) {
        console.error('Error cargando datos del insumo:', err);
        error.value = 'Error cargando datos del insumo. Por favor, intente nuevamente.';
      } finally {
        loading.value = false;
      }
    };
    
    // Métodos para filtrado de datos
    const filteredDetalles = computed(() => {
      let result = [...detalles.value];
      
      if (detalleSearch.value.trim()) {
        const search = detalleSearch.value.toLowerCase();
        result = result.filter(d => 
          d.cod_detalle.toString().includes(search) ||
          (d.escala?.toLowerCase().includes(search) || '') ||
          (d.estado?.toLowerCase().includes(search) || '') ||
          (d.observacion?.toLowerCase().includes(search) || '')
        );
      }
      
      if (detalleFilter.value) {
        result = result.filter(d => 
          d.cod_clasificacion.toString() === detalleFilter.value.toString()
        );
      }
      
      return result;
    });
    
    const filteredArchivos = computed(() => {
      let result = [...archivos.value];
      
      if (archivoSearch.value.trim()) {
        const search = archivoSearch.value.toLowerCase();
        result = result.filter(a => 
          (a.nombre_insumo?.toLowerCase().includes(search) || '') ||
          (a.observacion?.toLowerCase().includes(search) || '')
        );
      }
      
      if (archivoFilter.value) {
        result = result.filter(a => 
          a.cod_insumo.toString() === archivoFilter.value.toString()
        );
      }
      
      return result;
    });
    
    const filteredConceptos = computed(() => {
      if (!conceptoSearch.value.trim()) {
        return conceptos.value;
      }
      
      const search = conceptoSearch.value.toLowerCase();
      return conceptos.value.filter(c => 
        (c.concepto && c.concepto.toLowerCase().includes(search)) ||
        (c.detalle_concepto && c.detalle_concepto.toLowerCase().includes(search)) ||
        (c.observacion && c.observacion.toLowerCase().includes(search)) ||
        (c.evaluacion && c.evaluacion.toLowerCase().includes(search))
      );
    });
    
    // Métodos de utilidad
    const formatDate = (dateString: string | null): string => {
      if (!dateString) return 'N/A';
      try {
        return format(parseISO(dateString), 'dd/MM/yyyy', { locale: es });
      } catch (error) {
        return dateString || 'N/A';
      }
    };
    
    const getNombreCategoria = (categoriaId: number | string): string => {
      if (!categoriaId) return 'N/A';
      const categoria = categorias.value.find(c => c.cod_categoria.toString() === categoriaId.toString());
      return categoria ? categoria.nom_categoria : 'N/A';
    };
    
    const getTipoInsumoNombre = (tipo: string | any): string => {
      if (!tipo) return 'Desconocido';
      
      if (typeof tipo === 'object' && tipo !== null && tipo.tipo_insumo) {
        return tipo.tipo_insumo;
      }
      
      if (typeof tipo === 'string') {
        return tipo;
      }
      
      return String(tipo);
    };
    
    const getNombreClasificacion = (clasificacionId: number | string): string => {
      if (!clasificacionId) return 'N/A';
      const clasificacion = clasificaciones.value.find(c => c.cod_clasificacion.toString() === clasificacionId.toString());
      return clasificacion ? clasificacion.nombre : 'N/A';
    };
    
    const getNombreEntidad = (entidadId: string): string => {
      if (!entidadId) return 'N/A';
      const entidad = entidades.value.find(e => e.cod_entidad === entidadId);
      return entidad ? entidad.nom_entidad : 'N/A';
    };
    
    const getNombreUsuario = (usuarioId: number): string => {
      if (!usuarioId) return 'N/A';
      const usuario = usuarios.value.find(u => u.cod_usuario === usuarioId);
      return usuario ? usuario.nombre : 'N/A';
    };
    
    const getDetalleNombre = (detalleId: number): string => {
      if (!detalleId) return 'N/A';
      const detalle = detalles.value.find(d => d.cod_detalle === detalleId);
      return detalle ? `Detalle #${detalle.cod_detalle}` : `Detalle #${detalleId}`;
    };
    
    const getDetallesCount = (clasificacionId: number): number => {
      return detalles.value.filter(d => d.cod_clasificacion === clasificacionId).length;
    };
    
    const getFileIcon = (fileName: string): string => {
      if (!fileName) return 'insert_drive_file';
      
      const extension = fileName.split('.').pop()?.toLowerCase();
      
      switch (extension) {
        case 'pdf':
          return 'picture_as_pdf';
        case 'doc':
        case 'docx':
          return 'description';
        case 'xls':
        case 'xlsx':
        case 'csv':
          return 'table_chart';
        case 'ppt':
        case 'pptx':
          return 'slideshow';
        case 'jpg':
        case 'jpeg':
        case 'png':
        case 'gif':
          return 'image';
        case 'zip':
        case 'rar':
          return 'folder_zip';
        case 'shp':
        case 'kml':
        case 'kmz':
          return 'map';
        case 'gdb':
          return 'storage'; // Icono específico para geodatabases
        case 'tif':
        case 'tiff':
          return 'terrain'; // Icono específico para imágenes TIF
        default:
          return 'insert_drive_file';
      }
    };
    
    const getEvaluacionClass = (evaluacion: string): string => {
      if (!evaluacion) return 'default';
      
      const ev = evaluacion.toLowerCase();
      if (ev.includes('aprob')) return 'success';
      if (ev.includes('rechaz')) return 'danger';
      if (ev.includes('pend')) return 'warning';
      if (ev.includes('revis')) return 'info';
      
      return 'default';
    };
    
    const getCategoriaClass = (categoriaId: number | string): string => {
      if (!categoriaId) return '';
      
      const categoria = categorias.value.find(c => c.cod_categoria.toString() === categoriaId.toString());
      if (!categoria) return '';
      
      const nombreCategoria = categoria.nom_categoria.toLowerCase();
      
      if (nombreCategoria.includes('cartograf')) return 'cartografia';
      if (nombreCategoria.includes('agrolog')) return 'agrologico';
      if (nombreCategoria.includes('planea')) return 'planeacion';
      if (nombreCategoria.includes('predial')) return 'predial';
      if (nombreCategoria.includes('catastral')) return 'catastral';
      
      return 'default';
    };
    
    // Funciones auxiliares para archivos
    const esArchivoComplejo = (fileName: string): boolean => {
      if (!fileName) return false;
      
      const extension = fileName.split('.').pop()?.toLowerCase();
      const extensionesComplejas = ['tif', 'tiff', 'gdb', 'shp', 'dwg', 'dxf'];
      
      return extensionesComplejas.includes(extension || '');
    };
    
    const getArchivoDescargaInfo = (fileName: string): string => {
      if (!fileName) return '';
      
      const extension = fileName.split('.').pop()?.toLowerCase();
      
      switch (extension) {
        case 'tif':
        case 'tiff':
          return 'Directorio completo';
        case 'gdb':
          return 'Geodatabase';
        case 'shp':
          return 'Shapefile completo';
        case 'dwg':
        case 'dxf':
          return 'CAD + auxiliares';
        default:
          return '';
      }
    };
    
    const getDownloadTitle = (fileName: string): string => {
      const info = getArchivoDescargaInfo(fileName);
      return info ? `Descargar ${info} como ZIP` : 'Descargar archivo';
    };
    
    // Métodos de navegación
    const goBack = () => {
      router.go(-1);
    };
    
    const editInsumo = () => {
      router.push(`/gestion-informacion/insumos/editar/${props.id}`);
    };
    
    // Métodos para crear/editar elementos
    const crearClasificacion = () => {
      router.push({
        path: '/gestion-informacion/clasificaciones/crear',
        query: { insumo: props.id }
      });
    };
    
    const editarClasificacion = (clasificacion: any) => {
      router.push(`/gestion-informacion/clasificaciones/${clasificacion.cod_clasificacion}`);
    };
    
    const crearDetalle = () => {
      router.push({
        path: '/gestion-informacion/detalles/crear',
        query: { insumo: props.id }
      });
    };
    
    const editarDetalle = (detalle: any) => {
      router.push(`/gestion-informacion/detalles/${detalle.cod_detalle}`);
    };
    
    const cargarArchivo = () => {
      showNotification('Funcionalidad de carga de archivos en desarrollo', 'info');
    };
    
    const crearConcepto = () => {
      router.push({
        path: '/gestion-informacion/conceptos/crear',
        query: { insumo: props.id }
      });
    };
    
    const editarConcepto = (concepto: any) => {
      router.push(`/gestion-informacion/conceptos/${concepto.cod_concepto}`);
    };
    
    // Funciones para limpiar filtros
    const limpiarFiltrosArchivos = () => {
      archivoSearch.value = '';
      archivoFilter.value = '';
      showNotification('Filtros de archivos eliminados', 'info');
    };
    
    const limpiarFiltrosDetalles = () => {
      detalleSearch.value = '';
      detalleFilter.value = '';
      showNotification('Filtros de detalles eliminados', 'info');
    };
    
    const limpiarFiltrosConceptos = () => {
      conceptoSearch.value = '';
      showNotification('Filtro de conceptos eliminado', 'info');
    };
    
    const verDetalles = (clasificacion: any) => {
      activeTab.value = 'detalles';
      detalleFilter.value = clasificacion.cod_clasificacion.toString();
    };
    
    // Métodos para visualizar/descargar archivos COMPLETAMENTE CORREGIDOS
    const viewArchivo = (archivo: any) => {
      if (!archivo.path_file) {
        showNotification('No hay ruta disponible para este archivo', 'warning');
        return;
      }
      
      const fileName = archivo.nombre_insumo || 'archivo';
      const fileExtension = fileName.split('.').pop()?.toLowerCase();
      
      console.log('🔍 ViewArchivo - Archivo:', fileName, 'Extensión:', fileExtension);
      
      // Obtener token de autenticación
      const token = localStorage.getItem('token');
      if (!token) {
        showNotification('No hay token de autenticación. Por favor, inicie sesión nuevamente.', 'error');
        return;
      }
      
      // SOLO visualizar PDFs en el navegador, TODO LO DEMÁS se descarga
      if (fileExtension === 'pdf') {
        console.log('📋 Abriendo PDF para visualización');
        const fileUrl = `${API_URL}/preoperacion/ver_pdf/?ruta=${encodeURIComponent(archivo.path_file)}&token=${token}`;
        window.open(fileUrl, '_blank');
        showNotification('Abriendo PDF en nueva ventana', 'info');
      } else {
        console.log('📁 Iniciando descarga de archivo no-PDF');
        // Para CUALQUIER archivo que NO sea PDF, usar downloadArchivo
        downloadArchivo(archivo);
      }
    };
    
    const downloadArchivo = async (archivo: any) => {
      if (!archivo.path_file) {
        showNotification('No hay ruta disponible para descargar este archivo', 'warning');
        return;
      }
      
      // Evitar descargas duplicadas
      const archivoId = archivo.id_lista_archivo;
      if (descargandoArchivos.value.has(archivoId)) {
        showNotification('Ya hay una descarga en curso para este archivo', 'warning');
        return;
      }
      
      try {
        // Marcar como descargando
        descargandoArchivos.value.add(archivoId);
        
        // Obtener token de autenticación
        const token = localStorage.getItem('token');
        if (!token) {
          throw new Error('No hay token de autenticación. Por favor, inicie sesión nuevamente.');
        }
        
        const nombreArchivo = archivo.nombre_insumo || 'archivo';
        const fileExtension = nombreArchivo.split('.').pop()?.toLowerCase();
        
        console.log('🚀 DownloadArchivo - Archivo:', nombreArchivo, 'Extensión:', fileExtension);
        
        // Verificar información del archivo primero
        const verifyUrl = `${API_URL}/preoperacion/verificar_archivo/?ruta=${encodeURIComponent(archivo.path_file)}`;
        const verifyResponse = await fetch(verifyUrl, {
          headers: {
            'Authorization': `Token ${token}`
          }
        });
        
        let tipoDescarga = 'individual';
        let descripcionDescarga = `Descargando archivo: ${nombreArchivo}`;
        
        if (verifyResponse.ok) {
          const verifyData = await verifyResponse.json();
          console.log('✅ Verificación exitosa:', verifyData);
          if (verifyData.requiere_zip) {
            tipoDescarga = verifyData.metodo_descarga || 'agrupado';
            descripcionDescarga = verifyData.descripcion || `Descargando como ZIP: ${nombreArchivo}`;
          }
        } else {
          console.warn('⚠️ Error en verificación:', verifyResponse.status);
        }
        
        // Mostrar notificación inicial
        showNotification(descripcionDescarga, 'info');
        
        // LÓGICA CORREGIDA: Determinar URL del endpoint
        let downloadUrl = '';
        
        // REGLA SIMPLE: Solo PDFs van a ver_pdf, TODO LO DEMÁS va a descargar_archivo
        if (fileExtension === 'pdf') {
          console.log('📋 Usando endpoint PDF para descarga');
          downloadUrl = `${API_URL}/preoperacion/ver_pdf/?ruta=${encodeURIComponent(archivo.path_file)}&token=${token}&download=true`;
        } else {
          console.log('📦 Usando endpoint de descarga para archivo:', fileExtension);
          // TODOS los demás archivos (.gdb, .tif, .dwg, .shp, etc.) van aquí
          downloadUrl = `${API_URL}/preoperacion/descargar_archivo/?ruta=${encodeURIComponent(archivo.path_file)}&token=${token}`;
        }
        
        console.log('🌐 URL de descarga:', downloadUrl);
        
        // Iniciar descarga inmediata usando window.open
        window.open(downloadUrl, '_blank');
        
        // Mensaje de confirmación inmediato
        setTimeout(() => {
          let mensajeExito = '';
          
          switch (tipoDescarga) {
            case 'directorio_completo':
              mensajeExito = `✅ Descarga iniciada: Directorio completo de ${nombreArchivo}`;
              break;
            case 'geodatabase_completa':
              mensajeExito = `✅ Descarga iniciada: Geodatabase ${nombreArchivo}`;
              break;
            case 'archivos_relacionados':
              mensajeExito = `✅ Descarga iniciada: Archivos relacionados con ${nombreArchivo}`;
              break;
            default:
              mensajeExito = `✅ Descarga iniciada: ${nombreArchivo}`;
          }
          
          showNotification(mensajeExito, 'success');
        }, 500);
        
      } catch (error: any) {
        console.error('❌ Error al descargar archivo:', error);
        showNotification(`Error al descargar archivo: ${error.message}`, 'error');
      } finally {
        // Quitar del conjunto de descargas después de un tiempo
        setTimeout(() => {
          descargandoArchivos.value.delete(archivoId);
        }, 3000);
      }
    };
    
    // Función de prueba/debug para verificar que los endpoints funcionan
    const testearDescarga = async (archivo: any) => {
      console.log('🧪 INICIANDO TEST DE DESCARGA');
      console.log('📄 Archivo a probar:', archivo);
      
      if (!archivo.path_file) {
        console.error('❌ No hay ruta de archivo');
        return;
      }
      
      const nombreArchivo = archivo.nombre_insumo || 'archivo';
      const fileExtension = nombreArchivo.split('.').pop()?.toLowerCase();
      
      console.log('🔍 Nombre del archivo:', nombreArchivo);
      console.log('🔍 Extensión detectada:', fileExtension);
      
      const token = localStorage.getItem('token');
      if (!token) {
        console.error('❌ No hay token');
        return;
      }
      
      // Paso 1: Verificar archivo
      console.log('📋 Paso 1: Verificando archivo...');
      const verifyUrl = `${API_URL}/preoperacion/verificar_archivo/?ruta=${encodeURIComponent(archivo.path_file)}`;
      console.log('🌐 URL de verificación:', verifyUrl);
      
      try {
        const verifyResponse = await fetch(verifyUrl, {
          headers: {
            'Authorization': `Token ${token}`
          }
        });
        
        console.log('📊 Status verificación:', verifyResponse.status);
        
        if (verifyResponse.ok) {
          const verifyData = await verifyResponse.json();
          console.log('✅ Datos de verificación:', verifyData);
        } else {
          console.error('❌ Error en verificación:', await verifyResponse.text());
        }
      } catch (error) {
        console.error('❌ Error de red en verificación:', error);
      }
      
      // Paso 2: Determinar URL de descarga
      console.log('📋 Paso 2: Determinando URL de descarga...');
      
      let downloadUrl = '';
      
      if (fileExtension === 'pdf') {
        downloadUrl = `${API_URL}/preoperacion/ver_pdf/?ruta=${encodeURIComponent(archivo.path_file)}&token=${token}&download=true`;
        console.log('📋 Usando endpoint PDF');
      } else {
        downloadUrl = `${API_URL}/preoperacion/descargar_archivo/?ruta=${encodeURIComponent(archivo.path_file)}&token=${token}`;
        console.log('📦 Usando endpoint de descarga general');
      }
      
      console.log('🌐 URL final de descarga:', downloadUrl);
      
      // Paso 3: Probar descarga
      console.log('📋 Paso 3: Probando descarga...');
      
      try {
        const downloadResponse = await fetch(downloadUrl, {
          method: 'GET',
          headers: {
            'Authorization': `Token ${token}`
          }
        });
        
        console.log('📊 Status descarga:', downloadResponse.status);
        console.log('📊 Headers respuesta:', Object.fromEntries(downloadResponse.headers.entries()));
        
        if (!downloadResponse.ok) {
          const errorText = await downloadResponse.text();
          console.error('❌ Error en descarga:', errorText);
          showNotification(`Error de descarga: ${errorText}`, 'error');
        } else {
          console.log('✅ Descarga exitosa');
          showNotification('✅ Test de descarga exitoso! Ver consola para detalles.', 'success');
        }
      } catch (error) {
        console.error('❌ Error de red en descarga:', error);
        showNotification(`Error de red: ${error.message}`, 'error');
      }
      
      console.log('🧪 FIN DEL TEST DE DESCARGA');
    };
    
    const previewDescarga = async (archivo: any) => {
      if (!archivo.path_file) {
        showNotification('No hay ruta disponible para este archivo', 'warning');
        return;
      }
      
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          showNotification('No hay token de autenticación', 'error');
          return;
        }
        
        const previewUrl = `${API_URL}/preoperacion/preview_descarga/?ruta=${encodeURIComponent(archivo.path_file)}`;
        const response = await fetch(previewUrl, {
          headers: {
            'Authorization': `Token ${token}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          
          // Mostrar información detallada
          let mensaje = `📋 Vista previa de descarga:\n`;
          mensaje += `• Total de archivos: ${data.total_archivos}\n`;
          mensaje += `• Tamaño total: ${data.tamaño_total_mb} MB\n\n`;
          
          if (data.archivos.length > 1) {
            mensaje += `Se incluirán múltiples archivos/directorios.`;
          }
          
          showNotification(mensaje, 'info');
        }
        
      } catch (error) {
        console.error('Error al obtener preview:', error);
      }
    };
    
    const verDocumentoPDF = (rutaPDF: string) => {
      if (!rutaPDF) {
        showNotification('No hay ruta PDF disponible', 'warning');
        return;
      }
      
      const token = localStorage.getItem('token');
      if (!token) {
        showNotification('No hay token de autenticación. Por favor, inicie sesión nuevamente.', 'error');
        return;
      }
      
      window.open(`${API_URL}/preoperacion/ver_pdf/?ruta=${encodeURIComponent(rutaPDF)}&token=${token}`, '_blank');
    };
    
    const verPDF = (rutaPDF: string) => {
      if (!rutaPDF) {
        showNotification('No hay documento PDF disponible', 'warning');
        return;
      }
      
      const token = localStorage.getItem('token');
      if (!token) {
        showNotification('No hay token de autenticación. Por favor, inicie sesión nuevamente.', 'error');
        return;
      }
      
      const url = `${API_URL}/preoperacion/ver_pdf/?ruta=${encodeURIComponent(rutaPDF)}&token=${token}`;
      window.open(url, '_blank');
      showNotification('Abriendo PDF en nueva ventana', 'info');
    };
    
    // Métodos para eliminación
    const showDeleteClasificacionModal = (clasificacion: any) => {
      deleteType.value = 'clasificacion';
      deleteItemId.value = clasificacion.cod_clasificacion;
      deleteConfirmationText.value = `la clasificación "${clasificacion.nombre}"`;
      showDeleteModal.value = true;
    };
    
    const showDeleteDetalleModal = (detalle: any) => {
      deleteType.value = 'detalle';
      deleteItemId.value = detalle.cod_detalle;
      deleteConfirmationText.value = `el detalle #${detalle.cod_detalle}`;
      showDeleteModal.value = true;
    };
    
    const showDeleteArchivoModal = (archivo: any) => {
      deleteType.value = 'archivo';
      deleteItemId.value = archivo.id_lista_archivo;
      deleteConfirmationText.value = `el archivo "${archivo.nombre_insumo}"`;
      showDeleteModal.value = true;
    };
    
    const showDeleteConceptoModal = (concepto: any) => {
      deleteType.value = 'concepto';
      deleteItemId.value = concepto.cod_concepto;
      deleteConfirmationText.value = `el concepto "${concepto.concepto}"`;
      showDeleteModal.value = true;
    };
    
    const confirmDelete = async () => {
      if (!deleteItemId.value || !deleteType.value) {
        closeModals();
        return;
      }
      
      try {
        loading.value = true;
        
        switch (deleteType.value) {
          case 'clasificacion':
            showNotification('Clasificación eliminada correctamente', 'success');
            const updatedClasificaciones = clasificaciones.value.filter(c => c.cod_clasificacion !== deleteItemId.value);
            clasificaciones.value = updatedClasificaciones;
            break;
            
          case 'detalle':
            showNotification('Detalle eliminado correctamente', 'success');
            const updatedDetalles = detalles.value.filter(d => d.cod_detalle !== deleteItemId.value);
            detalles.value = updatedDetalles;
            break;
            
          case 'archivo':
            showNotification('Archivo eliminado correctamente', 'success');
            const updatedArchivos = archivos.value.filter(a => a.id_lista_archivo !== deleteItemId.value);
            archivos.value = updatedArchivos;
            break;
            
          case 'concepto':
            showNotification('Concepto eliminado correctamente', 'success');
            const updatedConceptos = conceptos.value.filter(c => c.cod_concepto !== deleteItemId.value);
            conceptos.value = updatedConceptos;
            break;
        }
      } catch (error: any) {
        console.error(`Error eliminando ${deleteType.value}:`, error);
        showNotification(`Error al eliminar ${deleteType.value}: ${error.message}`, 'error');
      } finally {
        loading.value = false;
        closeModals();
      }
    };
    
    // Métodos de gestión de modales y notificaciones
    const closeModals = () => {
      showDeleteModal.value = false;
      deleteType.value = '';
      deleteItemId.value = null;
    };
    
    const showNotification = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
      if (notification.value.timeout) {
        clearTimeout(notification.value.timeout);
      }
      
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
    
    const closeNotification = () => {
      if (notification.value.timeout) {
        clearTimeout(notification.value.timeout);
      }
      notification.value.show = false;
    };
    
    const cargarConceptos = async () => {
      try {
        cargandoConceptos.value = true;
        errorConceptos.value = null;
        conceptos.value = [];
        
        if (!insumo.value || !insumo.value.cod_municipio) {
          console.log("No hay insumo o municipio seleccionado");
          return;
        }
        
        console.log(`Intentando cargar conceptos para el municipio ${insumo.value.cod_municipio}`);
        
        const token = localStorage.getItem('token');
        if (!token) {
          throw new Error('No hay token de autenticación disponible');
        }
        
        const detallesIds = detalles.value.map(d => d.cod_detalle).join(',');
        
        if (!detallesIds) {
          console.log("No hay detalles asociados a este insumo");
          return;
        }
        
        const response = await fetch(`${API_URL}/preoperacion/conceptos/?cod_detalle__in=${detallesIds}`, {
          headers: {
            'Authorization': `Token ${token}`
          }
        });
        
        if (!response.ok) {
          console.log("Intentando buscar conceptos sin filtros específicos...");
          
          const backupResponse = await fetch(`${API_URL}/preoperacion/conceptos/`, {
            headers: {
              'Authorization': `Token ${token}`
            }
          });
          
          if (!backupResponse.ok) {
            throw new Error(`Error al cargar conceptos: ${backupResponse.status} ${backupResponse.statusText}`);
          }
          
          const allConceptosData = await backupResponse.json();
          const allConceptos = Array.isArray(allConceptosData.results) 
            ? allConceptosData.results 
            : (Array.isArray(allConceptosData) ? allConceptosData : []);
          
          const detallesIdsArray = detalles.value.map(d => d.cod_detalle);
          conceptos.value = allConceptos.filter(c => 
            c.cod_detalle && detallesIdsArray.includes(c.cod_detalle)
          );
        } else {
          const data = await response.json();
          conceptos.value = Array.isArray(data.results) 
            ? data.results 
            : (Array.isArray(data) ? data : []);
        }
        
        console.log(`Cargados ${conceptos.value.length} conceptos relacionados con este insumo`);
      } catch (err) {
        console.error('Error al cargar conceptos:', err);
        errorConceptos.value = err.message || 'Error al cargar conceptos';
      } finally {
        cargandoConceptos.value = false;
      }
    };
    
    return {
      loading,
      error,
      insumo,
      clasificaciones,
      detalles,
      archivos,
      conceptos,
      municipioName,
      departamentoName,
      detalleSearch,
      detalleFilter,
      archivoSearch,
      archivoFilter,
      conceptoSearch,
      activeTab,
      tabs,
      showDeleteModal,
      deleteConfirmationText,
      notification,
      filteredDetalles,
      filteredArchivos,
      filteredConceptos,
      formatDate,
      getNombreCategoria,
      getTipoInsumoNombre,
      getNombreClasificacion,
      getNombreEntidad,
      getNombreUsuario,
      getDetalleNombre,
      getDetallesCount,
      getFileIcon,
      getEvaluacionClass,
      getCategoriaClass,
      goBack,
      editInsumo,
      crearClasificacion,
      editarClasificacion,
      crearDetalle,
      editarDetalle,
      cargarArchivo,
      crearConcepto,
      editarConcepto,
      verDetalles,
      // Funciones para limpiar filtros
      limpiarFiltrosArchivos,
      limpiarFiltrosDetalles,
      limpiarFiltrosConceptos,
      viewArchivo,
      downloadArchivo,
      verDocumentoPDF,
      showDeleteClasificacionModal,
      showDeleteDetalleModal,
      showDeleteArchivoModal,
      showDeleteConceptoModal,
      confirmDelete,
      closeModals,
      showNotification,
      closeNotification,
      verPDF,
      cargandoConceptos,
      cargarConceptos,
      errorConceptos,
      // Nuevas funciones para archivos
      descargandoArchivos,
      previewDescarga,
      testearDescarga,
      esArchivoComplejo,
      getArchivoDescargaInfo,
      getDownloadTitle,
      // Utilidades de rutas
      linuxToWindowsPath,
    };
  }
});
</script>

<style scoped>
.insumo-detail-page {
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

/* Estados de carga y error */
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

/* Contenido principal */
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

.insumo-info {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.insumo-icon {
  width: 56px;
  height: 56px;
  background-color: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.insumo-icon i {
  font-size: 2rem;
}

.insumo-title h2 {
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
  color: #343a40;
}

.categoria-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  border-radius: 4px;
  font-weight: 500;
}

.categoria-badge.cartografia {
  background-color: #e3f2fd;
  color: #0d47a1;
}

.categoria-badge.agrologico {
  background-color: #e8f5e9;
  color: #1b5e20;
}

.categoria-badge.planeacion {
  background-color: #fff3e0;
  color: #e65100;
}

.categoria-badge.predial {
  background-color: #e1f5fe;
  color: #01579b;
}

.categoria-badge.catastral {
  background-color: #f3e5f5;
  color: #6a1b9a;
}

.categoria-badge.default {
  background-color: #eceff1;
  color: #546e7a;
}

.card-body {
  padding: 0;
}

.detail-section {
  padding: 1.5rem;
}

.detail-section h3 {
  margin: 0 0 1rem;
  font-size: 1.25rem;
  color: #343a40;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #dee2e6;
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
}

/* Pestañas */
.detail-tabs {
  display: flex;
  border-bottom: 1px solid #dee2e6;
  background-color: #f8f9fa;
}

.tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;
  border-bottom: 3px solid transparent;
  font-weight: 500;
  color: #6c757d;
}

.tab:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.tab.active {
  color: #0d6efd;
  border-bottom-color: #0d6efd;
}

.tab i {
  font-size: 1.2rem;
}

.tab-content {
  padding: 1.5rem;
}

/* Acciones de pestaña */
.tab-actions {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

/* Contadores para todas las pestañas */
.archivos-counter,
.detalles-counter,
.conceptos-counter,
.clasificaciones-counter {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
  min-width: 200px;
}

.counter-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #e3f2fd;
  border: 1px solid #bbdefb;
  border-radius: 6px;
  color: #1565c0;
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.counter-info:hover {
  background-color: #bbdefb;
  transform: translateY(-1px);
}

/* Variaciones de color para diferentes contadores */
.detalles-counter .counter-info {
  background-color: #e8f5e9;
  border-color: #c8e6c9;
  color: #2e7d32;
}

.detalles-counter .counter-info:hover {
  background-color: #c8e6c9;
}

.conceptos-counter .counter-info {
  background-color: #fff3e0;
  border-color: #ffcc02;
  color: #e65100;
}

.conceptos-counter .counter-info:hover {
  background-color: #ffcc02;
}

.clasificaciones-counter .counter-info {
  background-color: #f3e5f5;
  border-color: #ce93d8;
  color: #6a1b9a;
}

.clasificaciones-counter .counter-info:hover {
  background-color: #ce93d8;
}

.counter-info i {
  font-size: 1.1rem;
}

.counter-text {
  white-space: nowrap;
  font-weight: 600;
}

/* Indicadores de filtros activos */
.filtros-activos {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  justify-content: flex-end;
  max-width: 300px;
}

.filtro-badge {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background-color: #fff3e0;
  border: 1px solid #ffcc02;
  border-radius: 4px;
  color: #e65100;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.2s ease;
  max-width: 200px;
  overflow: hidden;
}

.filtro-badge:hover {
  background-color: #ffe0b2;
  transform: translateY(-1px);
}

.filtro-badge i {
  font-size: 0.9rem;
  flex-shrink: 0;
}

.remove-filter {
  background: none;
  border: none;
  color: #e65100;
  cursor: pointer;
  padding: 0;
  margin-left: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 2px;
  transition: background-color 0.2s;
  flex-shrink: 0;
}

.remove-filter:hover {
  color: #bf360c;
  background-color: rgba(191, 54, 12, 0.1);
}

.remove-filter i {
  font-size: 0.8rem;
}

.btn-clear-all {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background-color: #f3e5f5;
  border: 1px solid #ce93d8;
  border-radius: 4px;
  color: #6a1b9a;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-clear-all:hover {
  background-color: #e1bee7;
  transform: translateY(-1px);
}

.btn-clear-all i {
  font-size: 0.9rem;
}

/* Responsive para contadores */
@media (max-width: 768px) {
  .archivos-counter,
  .detalles-counter,
  .conceptos-counter,
  .clasificaciones-counter {
    min-width: auto;
    align-items: stretch;
  }
  
  .filtros-activos {
    justify-content: center;
    max-width: none;
  }
  
  .tab-actions {
    align-items: stretch;
  }
}

.search-box {
  position: relative;
  min-width: 250px;
}

.search-box i {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

.search-box input {
  width: 100%;
  padding: 0.5rem 0.5rem 0.5rem 2.25rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
}

.clear-btn {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.filter-item label {
  font-size: 0.875rem;
  color: #495057;
  font-weight: 500;
}

.filter-item select {
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  min-width: 200px;
}

/* Estado vacío */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
}

.empty-state i {
  font-size: 3rem;
  color: #adb5bd;
  margin-bottom: 1rem;
}

.empty-state p {
  margin-bottom: 1.5rem;
  color: #6c757d;
}

/* Clasificaciones */
.clasificaciones-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.clasificacion-card {
  background-color: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.clasificacion-card:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}

.clasificacion-header {
  padding: 1rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.clasificacion-title h4 {
  margin: 0;
  font-size: 1.1rem;
  color: #343a40;
}

.clasificacion-body {
  padding: 1rem;
}

.detail-row {
  display: flex;
  margin-bottom: 0.75rem;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.detail-label {
  width: 120px;
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 500;
}

.detail-value {
  flex: 1;
  font-size: 0.95rem;
  color: #212529;
}

.path-value {
  font-family: monospace;
  font-size: 0.85rem;
  color: #495057;
  overflow-wrap: break-word;
  word-break: break-all;
}

.clasificacion-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-top: 1px solid #dee2e6;
  background-color: #f8f9fa;
}

.detalles-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #6c757d;
}

.detalles-badge i {
  font-size: 1.1rem;
}

/* Detalles */
.detalles-table-container {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #dee2e6;
}

.data-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
  white-space: nowrap;
}

.data-table tbody tr:hover {
  background-color: #f8f9fa;
}

.row-actions {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

/* Archivos */
.archivos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.archivo-card {
  background-color: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.archivo-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.12);
}

.archivo-header {
  display: flex;
  padding: 1rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  align-items: center;
}

.archivo-icon {
  width: 40px;
  height: 40px;
  background-color: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
}

.archivo-title {
  flex: 1;
}

.archivo-title h4 {
  margin: 0 0 0.25rem;
  font-size: 1rem;
  color: #343a40;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.archivo-fecha {
  font-size: 0.85rem;
  color: #6c757d;
}

.archivo-body {
  padding: 1rem;
}

.archivo-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid #dee2e6;
  background-color: #f8f9fa;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.archivo-info {
  flex: 1;
}

.descarga-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  background-color: #e3f2fd;
  color: #1565c0;
  border-radius: 4px;
  font-weight: 500;
  border: 1px solid #bbdefb;
}

.archivo-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

/* Conceptos */
.conceptos-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.concepto-card {
  background-color: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.concepto-card:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}

.concepto-header {
  padding: 1rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.concepto-header h4 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  color: #343a40;
}

.concepto-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.concepto-fecha {
  font-size: 0.85rem;
  color: #6c757d;
}

.evaluacion-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  border-radius: 4px;
  font-weight: 600;
  color: white;
}

.evaluacion-badge.success {
  background-color: #28a745;
}

.evaluacion-badge.danger {
  background-color: #dc3545;
}

.evaluacion-badge.warning {
  background-color: #ffc107;
  color: #212529;
}

.evaluacion-badge.info {
  background-color: #17a2b8;
}

.evaluacion-badge.default {
  background-color: #6c757d;
}

.concepto-body {
  padding: 1rem;
}

.concepto-table {
  width: 100%;
  margin-bottom: 1rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  overflow: hidden;
}

.concepto-row {
  display: flex;
  border-bottom: 1px solid #dee2e6;
}

.concepto-row:last-child {
  border-bottom: none;
}

.concepto-cell {
  padding: 0.75rem 1rem;
  flex: 1;
}

.concepto-cell.header {
  background-color: #f8f9fa;
  font-weight: 600;
  width: 180px;
  flex: 0 0 180px;
  color: #495057;
}

.concepto-detail-section,
.concepto-observation-section {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}

.concepto-detail-header,
.concepto-observation-header {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #495057;
}

.concepto-detail-content,
.concepto-observation-content {
  white-space: pre-wrap;
  color: #212529;
  line-height: 1.5;
}

.concepto-footer {
  display: flex;
  justify-content: flex-end;
  padding: 0.75rem 1rem;
  border-top: 1px solid #dee2e6;
  background-color: #f8f9fa;
}

.concepto-actions {
  display: flex;
  gap: 0.5rem;
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

.btn-danger {
  background-color: #dc3545;
  color: white;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-danger:hover {
  background-color: #c82333;
}

.btn-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  color: #0d6efd;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
}

.btn-text:hover {
  background-color: rgba(13, 110, 253, 0.1);
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

.btn-icon.primary {
  background-color: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
}

.btn-icon.primary:hover {
  background-color: rgba(13, 110, 253, 0.2);
}

.btn-icon.warning {
  background-color: rgba(255, 193, 7, 0.1);
  color: #ffc107;
}

.btn-icon.warning:hover {
  background-color: rgba(255, 193, 7, 0.2);
}

.btn-icon.success {
  background-color: rgba(25, 135, 84, 0.1);
  color: #198754;
}

.btn-icon.success:hover {
  background-color: rgba(25, 135, 84, 0.2);
}

.btn-icon.danger {
  background-color: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

.btn-icon.danger:hover {
  background-color: rgba(220, 53, 69, 0.2);
}

.btn-icon.info {
  background-color: rgba(13, 202, 240, 0.1);
  color: #0dcaf0;
}

.btn-icon.info:hover {
  background-color: rgba(13, 202, 240, 0.2);
}

.btn-icon.small {
  width: 32px;
  height: 32px;
}

.btn-icon.small i {
  font-size: 1.1rem;
}

/* Estados de botones deshabilitados y animaciones */
.btn-icon:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}

.spinning {
  animation: spin 1s linear infinite;
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
  max-width: 500px;
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

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #dee2e6;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.delete-warning {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.delete-warning i {
  font-size: 3rem;
  color: #ffc107;
  margin-bottom: 1rem;
}

.delete-warning p {
  margin-bottom: 0.5rem;
  color: #495057;
}

/* Notificación mejorada */
.notification {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  min-width: 350px;
  max-width: 500px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
  z-index: 1100;
  overflow: hidden;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  animation: slide-up 0.3s ease;
  white-space: pre-line;
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
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  flex: 1;
}

.notification-content i {
  font-size: 1.5rem;
  margin-top: 0.1rem;
}

.notification-content span {
  line-height: 1.4;
  max-height: 200px;
  overflow-y: auto;
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

/* Estados de carga pequeños */
.loading-indicator.small {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.loading-indicator.small .spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(13, 110, 253, 0.2);
  border-top: 3px solid #0d6efd;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.error-message.small {
  padding: 1rem;
  border: 1px solid #f5c6cb;
  background-color: #f8d7da;
  color: #721c24;
  border-radius: 4px;
}

/* Responsive */
@media (max-width: 1200px) {
  .clasificaciones-list,
  .conceptos-list {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 992px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .archivos-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
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
}

@media (max-width: 768px) {
  .tab-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-item {
    width: 100%;
  }
  
  .archivos-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-tabs {
    overflow-x: auto;
  }
  
  .tab {
    white-space: nowrap;
    padding: 0.75rem 0.75rem;
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