<template>
  <div class="detalles-list-container">
    <div class="header-section">
      <h2 class="page-title">Estado del Producto</h2>
      <p class="page-description">Vista informativa de detalles de insumos y sus conceptos asociados</p>
    </div>

    <!-- Filtros jerárquicos DINÁMICOS -->
    <div class="filtros-section">
      <div class="row">
        <div class="col-md-6 col-lg-3">
          <div class="form-group">
            <label for="departamento">Departamento:</label>
            <select 
              id="departamento" 
              v-model="filtros.departamento" 
              @change="limpiarFiltrosInferiores(['municipio', 'insumo', 'clasificacion', 'centroPoblado'])"
              class="form-control"
            >
              <option value="">Todos los departamentos</option>
              <option 
                v-for="depto in departamentosDisponibles" 
                :key="depto.cod_depto" 
                :value="depto.cod_depto"
              >
                {{ depto.nom_depto }}
              </option>
            </select>
          </div>
        </div>
        
        <div class="col-md-6 col-lg-3">
          <div class="form-group">
            <label for="municipio">Municipio:</label>
            <select 
              id="municipio" 
              v-model="filtros.municipio" 
              @change="limpiarFiltrosInferiores(['insumo', 'clasificacion', 'centroPoblado'])"
              class="form-control"
              :disabled="!filtros.departamento"
            >
              <option value="">Todos los municipios</option>
              <option 
                v-for="municipio in municipiosDisponibles" 
                :key="municipio.cod_municipio" 
                :value="municipio.cod_municipio"
              >
                {{ municipio.nom_municipio }}
              </option>
            </select>
          </div>
        </div>
        
        <div class="col-md-6 col-lg-3">
          <div class="form-group">
            <label for="insumo">Insumo:</label>
            <select 
              id="insumo" 
              v-model="filtros.insumo" 
              @change="limpiarFiltrosInferiores(['clasificacion', 'centroPoblado'])"
              class="form-control"
              :disabled="!filtros.municipio"
            >
              <option value="">Todos los insumos</option>
              <option 
                v-for="insumo in insumosDisponibles" 
                :key="insumo.cod_insumo" 
                :value="insumo.cod_insumo"
              >
                {{ insumo.categoria_nombre }}
              </option>
            </select>
          </div>
        </div>
        
        <div class="col-md-6 col-lg-3">
          <div class="form-group">
            <label for="clasificacion">Clasificación:</label>
            <select 
              id="clasificacion" 
              v-model="filtros.clasificacion"
              @change="limpiarFiltrosInferiores(['centroPoblado'])"
              class="form-control"
              :disabled="!filtros.insumo"
            >
              <option value="">Todas las clasificaciones</option>
              <option 
                v-for="clasificacion in clasificacionesDisponibles" 
                :key="clasificacion.cod_clasificacion" 
                :value="clasificacion.cod_clasificacion"
              >
                {{ clasificacion.nombre }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- Filtro adicional para centros poblados (solo para cartografía básica) -->
      <div v-if="mostrarFiltroCentrosPoblados" class="row">
        <div class="col-md-6 col-lg-3">
          <div class="form-group">
            <label for="centroPoblado">Centro Poblado:</label>
            <select 
              id="centroPoblado" 
              v-model="filtros.centroPoblado"
              class="form-control"
              :disabled="cargandoCentrosPoblados"
            >
              <option value="">Todos los centros poblados</option>
              <option 
                v-for="centro in centrosPobladosDisponibles" 
                :key="centro.cod_centro_poblado" 
                :value="centro.cod_centro_poblado"
              >
                {{ centro.cod_centro_poblado }} - {{ centro.nom_centro_poblado }}
              </option>
            </select>
            <div v-if="cargandoCentrosPoblados" class="loading-indicator-small">
              <div class="spinner-small"></div>
              <span>Cargando centros poblados...</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Filtros adicionales -->
      <div class="row">
        <div class="col-md-6 col-lg-3">
          <div class="form-group">
            <label for="estado">Estado:</label>
            <select 
              id="estado" 
              v-model="filtros.estado"
              class="form-control"
            >
              <option value="">Todos los estados</option>
              <option 
                v-for="estado in estadosDisponibles" 
                :key="estado" 
                :value="estado"
              >
                {{ estado }}
              </option>
            </select>
          </div>
        </div>

        <div class="col-md-6 col-lg-3">
          <div class="form-group">
            <label for="zona">Zona:</label>
            <select 
              id="zona" 
              v-model="filtros.zona"
              class="form-control"
            >
              <option value="">Todas las zonas</option>
              <option 
                v-for="zona in zonasDisponibles" 
                :key="zona" 
                :value="zona"
              >
                {{ zona }}
              </option>
            </select>
          </div>
        </div>

        <div class="col-md-6 col-lg-3">
          <div class="form-group">
            <label for="entidad">Entidad:</label>
            <select 
              id="entidad" 
              v-model="filtros.entidad"
              class="form-control"
            >
              <option value="">Todas las entidades</option>
              <option 
                v-for="entidad in entidadesDisponibles" 
                :key="entidad" 
                :value="entidad"
              >
                {{ entidad }}
              </option>
            </select>
          </div>
        </div>

        <div class="col-md-6 col-lg-3">
          <div class="form-group">
            <label for="busqueda">Búsqueda:</label>
            <input 
              id="busqueda"
              type="text" 
              v-model="filtros.busqueda" 
              placeholder="Buscar en observaciones..."
              class="form-control"
            >
          </div>
        </div>
      </div>

      <!-- Indicadores de filtros activos -->
      <div v-if="hayFiltrosActivos" class="filtros-activos">
        <h4><i class="material-icons">filter_list</i> Filtros activos:</h4>
        <div class="tags-filtros">
          <span v-if="filtros.departamento" class="tag-filtro">
            Departamento: {{ getNombreDepartamento(filtros.departamento) }}
            <button @click="limpiarFiltroEspecifico('departamento')">×</button>
          </span>
          <span v-if="filtros.municipio" class="tag-filtro">
            Municipio: {{ getNombreMunicipio(filtros.municipio) }}
            <button @click="limpiarFiltroEspecifico('municipio')">×</button>
          </span>
          <span v-if="filtros.insumo" class="tag-filtro">
            Insumo: {{ getNombreInsumo(filtros.insumo) }}
            <button @click="limpiarFiltroEspecifico('insumo')">×</button>
          </span>
          <span v-if="filtros.clasificacion" class="tag-filtro">
            Clasificación: {{ getNombreClasificacion(filtros.clasificacion) }}
            <button @click="limpiarFiltroEspecifico('clasificacion')">×</button>
          </span>
          <span v-if="filtros.centroPoblado" class="tag-filtro">
            Centro Poblado: {{ getNombreCentroPoblado(filtros.centroPoblado) }}
            <button @click="limpiarFiltroEspecifico('centroPoblado')">×</button>
          </span>
          <span v-if="filtros.estado" class="tag-filtro">
            Estado: {{ filtros.estado }}
            <button @click="limpiarFiltroEspecifico('estado')">×</button>
          </span>
          <span v-if="filtros.zona" class="tag-filtro">
            Zona: {{ filtros.zona }}
            <button @click="limpiarFiltroEspecifico('zona')">×</button>
          </span>
          <span v-if="filtros.entidad" class="tag-filtro">
            Entidad: {{ filtros.entidad }}
            <button @click="limpiarFiltroEspecifico('entidad')">×</button>
          </span>
          <span v-if="filtros.busqueda" class="tag-filtro">
            Búsqueda: "{{ filtros.busqueda }}"
            <button @click="limpiarFiltroEspecifico('busqueda')">×</button>
          </span>
        </div>
      </div>

      <div class="filtros-buttons">
        <button class="btn btn-secondary" @click="limpiarFiltros" :disabled="cargando">
          <i class="material-icons">clear</i> Limpiar Filtros
        </button>
      </div>
    </div>

    <!-- Loading indicator -->
    <div v-if="cargando" class="loading-section">
      <div class="loading-content">
        <div class="spinner"></div>
        <p>Cargando información...</p>
        <small class="loading-details">
          Conectando con: {{ API_URL }}<br>
          Consultando APIs de preoperación...
        </small>
      </div>
    </div>

    <!-- Error message -->
    <div v-if="error && !cargando" class="error-section">
      <div class="error-message">
        <i class="material-icons">error</i>
        <div class="error-details">
          <strong>{{ error }}</strong>
          <br>
          <small>URL de API: {{ API_URL }}</small>
          <br>
          <small>Endpoints verificados:</small>
          <ul>
            <li>/preoperacion/departamentos/</li>
            <li>/preoperacion/municipios/</li>
            <li>/preoperacion/insumos/</li>
            <li>/preoperacion/categorias/</li>
            <li>/preoperacion/clasificaciones/</li>
            <li>/preoperacion/detalles-insumo/</li>
            <li>/preoperacion/conceptos/</li>
            <li>/preoperacion/centros-poblados/</li>
            <li>/preoperacion/ver_pdf/ (para PDFs)</li>
          </ul>
          <button class="btn btn-primary btn-sm" @click="reintentar" style="margin-top: 1rem;">
            <i class="material-icons">refresh</i>
            Reintentar
          </button>
        </div>
      </div>
    </div>

    <!-- Estadísticas -->
    <div v-if="!cargando && !error" class="stats-section">
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-number">{{ detallesFiltrados.length }}</div>
          <div class="stat-label">Detalles encontrados</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ municipiosUnicos.length }}</div>
          <div class="stat-label">Municipios únicos</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ entidadesUnicas.length }}</div>
          <div class="stat-label">Entidades únicas</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ totalConceptos }}</div>
          <div class="stat-label">Conceptos asociados</div>
        </div>
      </div>
    </div>

    <!-- Tabla de resultados -->
    <div v-if="!cargando && !error" class="table-section">
      <div class="table-header">
        <div class="table-info">
          <span>{{ detallesFiltrados.length }} registros encontrados</span>
        </div>
        <div class="table-controls">
          <select v-model="elementosPorPagina" class="form-control">
            <option value="10">10 por página</option>
            <option value="25">25 por página</option>
            <option value="50">50 por página</option>
            <option value="100">100 por página</option>
          </select>
        </div>
      </div>

      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th @click="ordenarPor('cod_detalle')" class="sortable">
                <span>Código</span>
                <i class="material-icons sort-icon" :class="getSortClass('cod_detalle')">arrow_upward</i>
              </th>
              <th @click="ordenarPor('nom_municipio')" class="sortable">
                <span>Municipio</span>
                <i class="material-icons sort-icon" :class="getSortClass('nom_municipio')">arrow_upward</i>
              </th>
              <th @click="ordenarPor('tipo_insumo')" class="sortable">
                <span>Insumo</span>
                <i class="material-icons sort-icon" :class="getSortClass('tipo_insumo')">arrow_upward</i>
              </th>
              <th @click="ordenarPor('nombre_clasificacion')" class="sortable">
                <span>Clasificación</span>
                <i class="material-icons sort-icon" :class="getSortClass('nombre_clasificacion')">arrow_upward</i>
              </th>
              <th @click="ordenarPor('estado')" class="sortable">
                <span>Estado</span>
                <i class="material-icons sort-icon" :class="getSortClass('estado')">arrow_upward</i>
              </th>
              <th @click="ordenarPor('zona')" class="sortable">
                <span>Zona</span>
                <i class="material-icons sort-icon" :class="getSortClass('zona')">arrow_upward</i>
              </th>
              <th @click="ordenarPor('cod_entidad')" class="sortable">
                <span>Entidad</span>
                <i class="material-icons sort-icon" :class="getSortClass('cod_entidad')">arrow_upward</i>
              </th>
              <th @click="ordenarPor('fecha_entrega')" class="sortable">
                <span>Fecha Entrega</span>
                <i class="material-icons sort-icon" :class="getSortClass('fecha_entrega')">arrow_upward</i>
              </th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="detalle in detallesVisibles" :key="detalle.cod_detalle">
              <td>{{ detalle.cod_detalle }}</td>
              <td>{{ detalle.nom_municipio || 'N/A' }}</td>
              <td>{{ detalle.tipo_insumo || 'N/A' }}</td>
              <td>{{ detalle.nombre_clasificacion || 'N/A' }}</td>
              <td>
                <span class="estado-badge" :class="getEstadoClass(detalle.estado)">
                  {{ detalle.estado }}
                </span>
              </td>
              <td>{{ detalle.zona || 'N/A' }}</td>
              <td>{{ detalle.cod_entidad }}</td>
              <td>{{ formatFecha(detalle.fecha_entrega) }}</td>
              <td>
                <button 
                  class="btn btn-primary btn-sm" 
                  @click="verDetalle(detalle)"
                  title="Ver detalles"
                >
                  <i class="material-icons">visibility</i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Paginación -->
      <div v-if="totalPaginas > 1" class="pagination-section">
        <div class="pagination-info">
          Página {{ paginaActual }} de {{ totalPaginas }}
        </div>
        <div class="pagination-controls">
          <button 
            class="btn btn-secondary" 
            @click="cambiarPagina(paginaActual - 1)"
            :disabled="paginaActual === 1"
          >
            <i class="material-icons">chevron_left</i>
          </button>
          
          <button 
            v-for="numero in botonesNumericos" 
            :key="numero"
            class="btn" 
            :class="numero === paginaActual ? 'btn-primary' : 'btn-secondary'"
            @click="cambiarPagina(numero)"
          >
            {{ numero }}
          </button>
          
          <button 
            class="btn btn-secondary" 
            @click="cambiarPagina(paginaActual + 1)"
            :disabled="paginaActual === totalPaginas"
          >
            <i class="material-icons">chevron_right</i>
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de detalles -->
    <div v-if="modalDetalle.mostrar" class="modal-overlay" @click="modalDetalle.mostrar = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Detalle {{ modalDetalle.detalle?.cod_detalle }}</h3>
          <button class="btn-close" @click="modalDetalle.mostrar = false">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="detalle-info" v-if="modalDetalle.detalle">
            <div class="info-grid">
              <div class="info-item">
                <label>Código:</label>
                <span>{{ modalDetalle.detalle.cod_detalle }}</span>
              </div>
              <div class="info-item">
                <label>Municipio:</label>
                <span>{{ modalDetalle.detalle.nom_municipio || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Insumo:</label>
                <span>{{ modalDetalle.detalle.tipo_insumo || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Clasificación:</label>
                <span>{{ modalDetalle.detalle.nombre_clasificacion || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Estado:</label>
                <span class="estado-badge" :class="getEstadoClass(modalDetalle.detalle.estado)">
                  {{ modalDetalle.detalle.estado }}
                </span>
              </div>
              <div class="info-item">
                <label>Escala:</label>
                <span>{{ modalDetalle.detalle.escala || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Cubrimiento:</label>
                <span>{{ modalDetalle.detalle.cubrimiento || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Área:</label>
                <span>{{ modalDetalle.detalle.area || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Zona:</label>
                <span>{{ modalDetalle.detalle.zona || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Entidad:</label>
                <span>{{ modalDetalle.detalle.cod_entidad }}</span>
              </div>
              <div class="info-item">
                <label>Formato:</label>
                <span>{{ modalDetalle.detalle.formato_tipo || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Vigencia:</label>
                <span>{{ modalDetalle.detalle.vigencia || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Fecha Entrega:</label>
                <span>{{ formatFecha(modalDetalle.detalle.fecha_entrega) }}</span>
              </div>
              <div class="info-item">
                <label>Fecha Disposición:</label>
                <span>{{ formatFecha(modalDetalle.detalle.fecha_disposicion) }}</span>
              </div>
              <div class="info-item" v-if="modalDetalle.detalle.observacion">
                <label>Observación:</label>
                <span>{{ modalDetalle.detalle.observacion }}</span>
              </div>
            </div>
            
            <!-- Sección de Conceptos -->
            <div v-if="getConceptosDelDetalle(modalDetalle.detalle.cod_detalle).length > 0" class="conceptos-section">
              <h4><i class="material-icons">description</i> Conceptos Asociados</h4>
              <div class="conceptos-list">
                <div 
                  v-for="concepto in getConceptosDelDetalle(modalDetalle.detalle.cod_detalle)" 
                  :key="concepto.cod_concepto"
                  class="concepto-card"
                >
                  <div class="concepto-header">
                    <span class="concepto-title">Concepto #{{ concepto.cod_concepto }}</span>
                    <span 
                      v-if="concepto.evaluacion" 
                      class="evaluacion-badge" 
                      :class="getEvaluacionClass(concepto.evaluacion)"
                    >
                      {{ concepto.evaluacion }}
                    </span>
                  </div>
                  <div class="concepto-content">
                    <p v-if="concepto.concepto"><strong>Concepto:</strong> {{ concepto.concepto }}</p>
                    <p v-if="concepto.detalle_concepto"><strong>Detalle:</strong> {{ concepto.detalle_concepto }}</p>
                    <p v-if="concepto.observacion"><strong>Observación:</strong> {{ concepto.observacion }}</p>
                    <p v-if="concepto.fecha"><strong>Fecha:</strong> {{ formatFecha(concepto.fecha) }}</p>
                    <div v-if="concepto.pdf" class="concepto-actions">
                      <button 
                        @click="verDocumentoPDF(concepto.pdf)" 
                        class="btn btn-primary btn-sm"
                        title="Ver PDF del concepto en nueva ventana"
                      >
                        <i class="material-icons">open_in_new</i>
                        Ver PDF en nueva ventana
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="no-conceptos">
              <p><i class="material-icons">info</i> No hay conceptos asociados a este detalle.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth';
import axios from 'axios';
import api, { API_URL } from '@/api/config';

export default {
  name: 'EstadoProducto',

  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    
    // Estado de carga y errores
    const cargando = ref(false);
    const error = ref(null);
    
    // Datos principales
    const detallesOriginales = ref([]);
    const centrosPoblados = ref([]);
    const cargandoCentrosPoblados = ref(false);
    const conceptos = ref([]);
    const conceptosPorDetalle = ref({});
    
    // Catálogos y listas de referencia
    const departamentos = ref([]);
    const municipios = ref([]);
    const insumos = ref([]);
    const clasificaciones = ref([]);
    
    // Filtros de búsqueda
    const filtros = ref({
      departamento: '',
      municipio: '',
      insumo: '',
      clasificacion: '',
      centroPoblado: '',
      estado: '',
      zona: '',
      entidad: '',
      busqueda: ''
    });
    
    // Ordenación
    const ordenacion = ref({
      campo: 'cod_detalle',
      ascendente: true
    });
    
    // Paginación
    const paginaActual = ref(1);
    const elementosPorPagina = ref(10);
    
    // Modal
    const modalDetalle = ref({
      mostrar: false,
      detalle: null
    });
    
    // FUNCIÓN AUXILIAR PARA CARGAR TODOS LOS DATOS PAGINADOS - MEJORADA
    const cargarTodosLosDatos = async (url, params = {}) => {
      try {
        const todosLosResultados = [];
        let paginaSiguiente = url;
        let intentos = 0;
        const maxIntentos = 20;
        
        console.log('🔄 Iniciando carga de datos desde:', url);
        console.log('📋 Parámetros:', params);
        
        while (paginaSiguiente && intentos < maxIntentos) {
          intentos++;
          console.log(`📄 Cargando página ${intentos}...`);
          
          try {
            const response = await axios.get(paginaSiguiente, { 
              params: intentos === 1 ? params : {},
              timeout: 10000 // 10 segundos timeout
            });
            
            console.log(`✅ Página ${intentos} cargada:`, response.data);
            
            if (response.data && response.data.results) {
              todosLosResultados.push(...response.data.results);
              paginaSiguiente = response.data.next;
              console.log(`📊 Total acumulado: ${todosLosResultados.length}, Siguiente: ${paginaSiguiente ? 'Sí' : 'No'}`);
            } else if (Array.isArray(response.data)) {
              todosLosResultados.push(...response.data);
              paginaSiguiente = null;
              console.log(`📊 Datos directos cargados: ${todosLosResultados.length}`);
            } else {
              console.warn('⚠️ Estructura de respuesta inesperada:', response.data);
              break;
            }
          } catch (pageError) {
            console.error(`❌ Error en página ${intentos}:`, pageError);
            if (intentos === 1) {
              // Si es el primer intento, lanzar el error
              throw pageError;
            } else {
              // Si no es el primer intento, detener la paginación
              break;
            }
          }
        }
        
        console.log(`🎉 Carga completada. Total resultados: ${todosLosResultados.length}`);
        return todosLosResultados;
      } catch (error) {
        console.error('💥 Error en cargarTodosLosDatos:', error);
        console.error('🔍 URL que falló:', url);
        console.error('🔍 Parámetros:', params);
        
        // Información detallada del error
        if (error.response) {
          console.error('📊 Status:', error.response.status);
          console.error('📊 Data:', error.response.data);
          console.error('📊 Headers:', error.response.headers);
        } else if (error.request) {
          console.error('📡 Request sin respuesta:', error.request);
        } else {
          console.error('⚙️ Error de configuración:', error.message);
        }
        
        throw error;
      }
    };

    // Cargar catálogos iniciales - MEJORADO
    const cargarCatalogos = async () => {
      try {
        console.log('🚀 Iniciando carga de catálogos...');
        
        // Cargar departamentos - RUTA CORREGIDA
        try {
          const deptosData = await cargarTodosLosDatos(`${API_URL}/preoperacion/departamentos/`);
          departamentos.value = deptosData;
          console.log(`✅ Cargados ${deptosData.length} departamentos`);
        } catch (err) {
          console.error('❌ Error cargando departamentos:', err);
          departamentos.value = [];
        }
        
        // Cargar insumos completos con categoría - MEJORADO
        try {
          const insumosData = await cargarTodosLosDatos(`${API_URL}/preoperacion/insumos/`);
          
          // También cargar categorías por separado para enriquecer
          let categoriasData = [];
          try {
            categoriasData = await cargarTodosLosDatos(`${API_URL}/preoperacion/categorias/`);
            console.log(`✅ Cargadas ${categoriasData.length} categorías`);
          } catch (err) {
            console.warn('⚠️ No se pudieron cargar categorías:', err);
          }
          
          // Enriquecer insumos con categorías
          insumos.value = insumosData.map(insumo => {
            let categoria_nombre = 'Sin categoría';
            
            // Intentar obtener categoría de varias formas
            if (insumo.categoria?.nom_categoria) {
              categoria_nombre = insumo.categoria.nom_categoria;
            } else if (insumo.categoria_nombre) {
              categoria_nombre = insumo.categoria_nombre;
            } else if (insumo.categoria && typeof insumo.categoria === 'string') {
              categoria_nombre = insumo.categoria;
            } else if (insumo.cod_categoria && categoriasData.length > 0) {
              // Buscar en el catálogo de categorías
              const categoriaEncontrada = categoriasData.find(cat => cat.cod_categoria === insumo.cod_categoria);
              if (categoriaEncontrada) {
                categoria_nombre = categoriaEncontrada.nom_categoria;
              }
            }
            
            return {
              ...insumo,
              categoria_nombre
            };
          });
          
          console.log(`✅ Cargados ${insumosData.length} insumos con categorías enriquecidas`);
          console.log('📋 Muestra de insumos:', insumos.value.slice(0, 3));
        } catch (err) {
          console.error('❌ Error cargando insumos:', err);
          insumos.value = [];
        }
        
        // Cargar clasificaciones
        try {
          const clasificacionesData = await cargarTodosLosDatos(`${API_URL}/preoperacion/clasificaciones/`);
          clasificaciones.value = clasificacionesData;
          console.log(`✅ Cargadas ${clasificacionesData.length} clasificaciones`);
        } catch (err) {
          console.error('❌ Error cargando clasificaciones:', err);
          clasificaciones.value = [];
        }
        
        console.log('🎉 Carga de catálogos completada');
        
      } catch (err) {
        console.error('💥 Error general al cargar catálogos:', err);
        error.value = 'Error al cargar catálogos base. Verifique la conexión con el servidor.';
      }
    };

    // Cargar detalles de la API - MEJORADO
    const cargarDetalles = async () => {
      try {
        cargando.value = true;
        error.value = null;
        console.log('🚀 Iniciando carga de detalles de insumos...');
        
        const detallesData = await cargarTodosLosDatos(`${API_URL}/preoperacion/detalles-insumo/`);
        console.log(`✅ Cargados ${detallesData.length} detalles de insumos`);
        console.log('📋 Estructura del primer detalle:', detallesData[0]);
        
        // Enriquecer detalles con información adicional
        console.log('🔄 Iniciando enriquecimiento de detalles...');
        const detallesEnriquecidos = await Promise.all(detallesData.map(async (detalle, index) => {
          try {
            console.log(`📝 Enriqueciendo detalle ${index + 1}/${detallesData.length} (ID: ${detalle.cod_detalle})`);
            
            // Enriquecer con clasificación
            if (detalle.cod_clasificacion) {
              try {
                console.log(`🔍 Buscando clasificación ${detalle.cod_clasificacion}...`);
                const clasificacionResponse = await axios.get(
                  `${API_URL}/preoperacion/clasificaciones/${detalle.cod_clasificacion}/`
                );
                detalle.nombre_clasificacion = clasificacionResponse.data.nombre;
                console.log(`✅ Clasificación encontrada: ${detalle.nombre_clasificacion}`);
                
                // Enriquecer con insumo
                if (clasificacionResponse.data.cod_insumo) {
                  try {
                    console.log(`🔍 Buscando insumo ${clasificacionResponse.data.cod_insumo}...`);
                    const insumoResponse = await axios.get(
                      `${API_URL}/preoperacion/insumos/${clasificacionResponse.data.cod_insumo}/`
                    );
                    detalle.tipo_insumo = insumoResponse.data.tipo_insumo;
                    detalle.cod_insumo = insumoResponse.data.cod_insumo;
                    console.log(`✅ Insumo encontrado: ${detalle.tipo_insumo}`);
                    
                    // Enriquecer con municipio
                    if (insumoResponse.data.cod_municipio) {
                      try {
                        console.log(`🔍 Buscando municipio ${insumoResponse.data.cod_municipio}...`);
                        const municipioResponse = await axios.get(
                          `${API_URL}/preoperacion/municipios/${insumoResponse.data.cod_municipio}/`
                        );
                        detalle.nom_municipio = municipioResponse.data.nom_municipio;
                        detalle.cod_municipio = municipioResponse.data.cod_municipio;
                        detalle.cod_depto = municipioResponse.data.cod_depto;
                        console.log(`✅ Municipio encontrado: ${detalle.nom_municipio}`);
                      } catch (err) {
                        console.warn(`⚠️ Error al cargar municipio ${insumoResponse.data.cod_municipio}:`, err);
                      }
                    }
                  } catch (err) {
                    console.warn(`⚠️ Error al cargar insumo ${clasificacionResponse.data.cod_insumo}:`, err);
                  }
                }
              } catch (err) {
                console.warn(`⚠️ Error al cargar clasificación ${detalle.cod_clasificacion}:`, err);
              }
            }
            
            console.log(`✅ Detalle ${index + 1} enriquecido completamente`);
            return detalle;
          } catch (err) {
            console.warn(`⚠️ Error al enriquecer detalle ${index + 1}:`, err);
            return detalle;
          }
        }));
        
        detallesOriginales.value = detallesEnriquecidos;
        console.log(`🎉 Enriquecimiento completado. ${detallesEnriquecidos.length} detalles listos.`);
        
      } catch (err) {
        console.error('💥 Error al cargar detalles:', err);
        error.value = 'Error al cargar los detalles. Verifique la conexión con el servidor.';
      } finally {
        cargando.value = false;
      }
    };

    // Cargar conceptos y crear mapa por detalle
    const cargarConceptos = async () => {
      try {
        console.log('🚀 Cargando conceptos...');
        const conceptosData = await cargarTodosLosDatos(`${API_URL}/preoperacion/conceptos/`);
        conceptos.value = conceptosData;
        console.log(`✅ Cargados ${conceptosData.length} conceptos`);
        
        // Crear mapa de conceptos por detalle
        conceptosPorDetalle.value = {};
        conceptosData.forEach(concepto => {
          if (concepto.cod_detalle) {
            if (!conceptosPorDetalle.value[concepto.cod_detalle]) {
              conceptosPorDetalle.value[concepto.cod_detalle] = [];
            }
            conceptosPorDetalle.value[concepto.cod_detalle].push(concepto);
          }
        });
        
        console.log(`✅ Mapa de conceptos creado para ${Object.keys(conceptosPorDetalle.value).length} detalles`);
      } catch (err) {
        console.error('❌ Error al cargar conceptos:', err);
        conceptos.value = [];
        conceptosPorDetalle.value = {};
      }
    };

    // Cargar centros poblados específicos por sus códigos
    const cargarCentrosPobladosPorCodigos = async (codigos) => {
      if (!codigos || codigos.length === 0) {
        centrosPoblados.value = [];
        return;
      }
      
      try {
        cargandoCentrosPoblados.value = true;
        console.log(`🔍 Buscando centros poblados por códigos:`, codigos);
        
        // Obtener todos los centros poblados y filtrar por los códigos que necesitamos
        const response = await axios.get(`${API_URL}/preoperacion/centros-poblados/`);
        const todosCentrosPoblados = response.data.results || response.data || [];
        
        // Filtrar solo los que coinciden con nuestros códigos
        const centrosFiltrados = todosCentrosPoblados.filter(centro => 
          codigos.includes(centro.cod_centro_poblado)
        );
        
        centrosPoblados.value = centrosFiltrados;
        console.log(`✅ Encontrados ${centrosFiltrados.length} centros poblados:`, centrosFiltrados);
        
      } catch (error) {
        console.error('❌ Error al cargar centros poblados por códigos:', error);
        centrosPoblados.value = [];
      } finally {
        cargandoCentrosPoblados.value = false;
      }
    };

    // COMPUTADAS PARA FILTROS DINÁMICOS

    // 1. Filtrar detalles progresivamente
    const detallesFiltradosPorJerarquia = computed(() => {
      let resultado = [...detallesOriginales.value];
      
      // Filtrar por departamento
      if (filtros.value.departamento) {
        resultado = resultado.filter(d => 
          d.cod_depto && d.cod_depto.toString() === filtros.value.departamento.toString()
        );
      }
      
      // Filtrar por municipio
      if (filtros.value.municipio) {
        resultado = resultado.filter(d => 
          d.cod_municipio && d.cod_municipio.toString() === filtros.value.municipio.toString()
        );
      }
      
      // Filtrar por insumo
      if (filtros.value.insumo) {
        resultado = resultado.filter(d => 
          d.cod_insumo && d.cod_insumo.toString() === filtros.value.insumo.toString()
        );
      }
      
      // Filtrar por clasificación
      if (filtros.value.clasificacion) {
        resultado = resultado.filter(d => 
          d.cod_clasificacion && d.cod_clasificacion.toString() === filtros.value.clasificacion.toString()
        );
      }
      
      return resultado;
    });

    // 2. Opciones disponibles para cada filtro basadas en los datos filtrados
    const departamentosDisponibles = computed(() => {
      const deptosUsados = new Set();
      detallesOriginales.value.forEach(detalle => {
        if (detalle.cod_depto) {
          deptosUsados.add(detalle.cod_depto.toString());
        }
      });
      
      return departamentos.value.filter(d => deptosUsados.has(d.cod_depto.toString()));
    });

    const municipiosDisponibles = computed(() => {
      if (!filtros.value.departamento) return [];
      
      const municipiosUsados = new Set();
      detallesOriginales.value
        .filter(d => d.cod_depto && d.cod_depto.toString() === filtros.value.departamento.toString())
        .forEach(detalle => {
          if (detalle.cod_municipio && detalle.nom_municipio) {
            municipiosUsados.add(JSON.stringify({
              cod_municipio: detalle.cod_municipio,
              nom_municipio: detalle.nom_municipio
            }));
          }
        });
      
      return Array.from(municipiosUsados).map(m => JSON.parse(m));
    });

    const insumosDisponibles = computed(() => {
      if (!filtros.value.municipio) return [];
      
      const insumosUsados = new Map();
      detallesFiltradosPorJerarquia.value.forEach(detalle => {
        if (detalle.cod_insumo && detalle.tipo_insumo) {
          // Si ya existe, no lo agregamos de nuevo
          if (insumosUsados.has(detalle.cod_insumo)) return;
          
          // Buscar la categoría real del insumo en el catálogo cargado
          const insumoCompleto = insumos.value.find(ins => ins.cod_insumo === detalle.cod_insumo);
          let categoria = 'Sin categoría';
          
          if (insumoCompleto) {
            // Probar diferentes formas de obtener la categoría
            if (insumoCompleto.categoria_nombre) {
              categoria = insumoCompleto.categoria_nombre;
            } else if (insumoCompleto.categoria?.nom_categoria) {
              categoria = insumoCompleto.categoria.nom_categoria;
            } else if (insumoCompleto.categoria && typeof insumoCompleto.categoria === 'string') {
              categoria = insumoCompleto.categoria;
            }
          }
          
          insumosUsados.set(detalle.cod_insumo, {
            cod_insumo: detalle.cod_insumo,
            tipo_insumo: detalle.tipo_insumo,
            categoria_nombre: categoria
          });
        }
      });
      
      console.log('🔍 Insumos disponibles detectados:', Array.from(insumosUsados.values()));
      return Array.from(insumosUsados.values());
    });

    const clasificacionesDisponibles = computed(() => {
      if (!filtros.value.insumo) return [];
      
      const clasificacionesUsadas = new Set();
      detallesFiltradosPorJerarquia.value.forEach(detalle => {
        if (detalle.cod_clasificacion && detalle.nombre_clasificacion) {
          clasificacionesUsadas.add(JSON.stringify({
            cod_clasificacion: detalle.cod_clasificacion,
            nombre: detalle.nombre_clasificacion
          }));
        }
      });
      
      return Array.from(clasificacionesUsadas).map(c => JSON.parse(c));
    });

    // 3. Determinar si mostrar filtro de centros poblados - CORREGIDO
    const mostrarFiltroCentrosPoblados = computed(() => {
      if (!filtros.value.insumo) return false;
      
      // Buscar el insumo seleccionado
      const insumoSeleccionado = insumosDisponibles.value.find(
        i => i.cod_insumo.toString() === filtros.value.insumo.toString()
      );
      
      if (!insumoSeleccionado) return false;
      
      // Verificar si es cartografía básica - PROTEGIDO CONTRA ERRORES
      const tipoInsumo = insumoSeleccionado.tipo_insumo;
      const categoria = insumoSeleccionado.categoria_nombre;
      
      // Verificar en tipo_insumo
      const esCartografiaBasicaPorTipo = tipoInsumo && 
                                        typeof tipoInsumo === 'string' &&
                                        tipoInsumo.toLowerCase().includes('cartografia') &&
                                        tipoInsumo.toLowerCase().includes('basica');
      
      // Verificar en categoría
      const esCartografiaBasicaPorCategoria = categoria && 
                                             typeof categoria === 'string' &&
                                             categoria.toLowerCase().includes('cartografia') &&
                                             categoria.toLowerCase().includes('basica');
      
      console.log('🔍 Verificando filtro centros poblados:', {
        insumoSeleccionado,
        tipoInsumo,
        categoria,
        esCartografiaBasicaPorTipo,
        esCartografiaBasicaPorCategoria,
        resultado: esCartografiaBasicaPorTipo || esCartografiaBasicaPorCategoria
      });
      
      return esCartografiaBasicaPorTipo || esCartografiaBasicaPorCategoria;
    });

    // 4. Centros poblados disponibles - BASADO EN DATOS REALES
    const centrosPobladosDisponibles = computed(() => {
      // Solo mostrar si es cartografía básica
      if (!mostrarFiltroCentrosPoblados.value) return [];
      
      // Extraer códigos únicos de centros poblados de los detalles filtrados
      const codigosUnicos = new Set();
      detallesFiltradosPorJerarquia.value.forEach(detalle => {
        if (detalle.cod_centro_poblado && detalle.cod_centro_poblado !== null) {
          codigosUnicos.add(detalle.cod_centro_poblado);
        }
      });
      
      console.log('🏘️ Códigos de centros poblados encontrados en datos:', Array.from(codigosUnicos));
      
      // Filtrar centros poblados cargados que coinciden con los códigos de los datos
      const centrosConDatos = centrosPoblados.value.filter(centro => 
        codigosUnicos.has(centro.cod_centro_poblado)
      );
      
      console.log('🏘️ Centros poblados con datos disponibles:', centrosConDatos);
      return centrosConDatos;
    });

    // 5. Opciones para filtros adicionales
    const estadosDisponibles = computed(() => {
      const estados = new Set();
      detallesFiltradosPorJerarquia.value.forEach(d => {
        if (d.estado) estados.add(d.estado);
      });
      return Array.from(estados).sort();
    });

    const zonasDisponibles = computed(() => {
      const zonas = new Set();
      detallesFiltradosPorJerarquia.value.forEach(d => {
        if (d.zona) zonas.add(d.zona);
      });
      return Array.from(zonas).sort();
    });

    const entidadesDisponibles = computed(() => {
      const entidades = new Set();
      detallesFiltradosPorJerarquia.value.forEach(d => {
        if (d.cod_entidad) entidades.add(d.cod_entidad);
      });
      return Array.from(entidades).sort();
    });

    // APLICAR TODOS LOS FILTROS (incluidos los adicionales)
    const detallesFiltrados = computed(() => {
      let resultado = [...detallesFiltradosPorJerarquia.value];
      
      // Filtrar por centro poblado
      if (filtros.value.centroPoblado) {
        resultado = resultado.filter(d => 
          d.cod_centro_poblado && d.cod_centro_poblado.toString() === filtros.value.centroPoblado.toString()
        );
      }
      
      // Filtrar por estado
      if (filtros.value.estado) {
        resultado = resultado.filter(d => d.estado === filtros.value.estado);
      }
      
      // Filtrar por zona
      if (filtros.value.zona) {
        resultado = resultado.filter(d => d.zona === filtros.value.zona);
      }
      
      // Filtrar por entidad
      if (filtros.value.entidad) {
        resultado = resultado.filter(d => d.cod_entidad === filtros.value.entidad);
      }
      
      // Filtrar por búsqueda en observaciones
      if (filtros.value.busqueda) {
        const busqueda = filtros.value.busqueda.toLowerCase();
        resultado = resultado.filter(d => 
          (d.observacion && d.observacion.toLowerCase().includes(busqueda)) ||
          (d.cubrimiento && d.cubrimiento.toLowerCase().includes(busqueda))
        );
      }
      
      // Aplicar ordenación
      resultado.sort((a, b) => {
        const valorA = a[ordenacion.value.campo] || '';
        const valorB = b[ordenacion.value.campo] || '';
        
        if (valorA < valorB) return ordenacion.value.ascendente ? -1 : 1;
        if (valorA > valorB) return ordenacion.value.ascendente ? 1 : -1;
        return 0;
      });
      
      return resultado;
    });

    // Elementos visibles en la página actual
    const detallesVisibles = computed(() => {
      const inicio = (paginaActual.value - 1) * elementosPorPagina.value;
      const fin = inicio + elementosPorPagina.value;
      return detallesFiltrados.value.slice(inicio, fin);
    });

    // Total de páginas
    const totalPaginas = computed(() => {
      return Math.ceil(detallesFiltrados.value.length / elementosPorPagina.value) || 1;
    });

    // Botones numéricos para paginación
    const botonesNumericos = computed(() => {
      const botones = [];
      const maxBotones = 5;
      
      if (totalPaginas.value <= maxBotones) {
        for (let i = 1; i <= totalPaginas.value; i++) {
          botones.push(i);
        }
      } else {
        const mitad = Math.floor(maxBotones / 2);
        let inicio = paginaActual.value - mitad;
        let fin = paginaActual.value + mitad;
        
        if (inicio < 1) {
          inicio = 1;
          fin = maxBotones;
        } else if (fin > totalPaginas.value) {
          fin = totalPaginas.value;
          inicio = totalPaginas.value - maxBotones + 1;
        }
        
        for (let i = inicio; i <= fin; i++) {
          botones.push(i);
        }
      }
      
      return botones;
    });

    // Estadísticas
    const municipiosUnicos = computed(() => {
      const municipios = new Set();
      detallesFiltrados.value.forEach(d => {
        if (d.nom_municipio) municipios.add(d.nom_municipio);
      });
      return Array.from(municipios);
    });

    const entidadesUnicas = computed(() => {
      const entidades = new Set();
      detallesFiltrados.value.forEach(d => {
        if (d.cod_entidad) entidades.add(d.cod_entidad);
      });
      return Array.from(entidades);
    });

    const totalConceptos = computed(() => {
      let total = 0;
      detallesFiltrados.value.forEach(d => {
        const conceptosDetalle = conceptosPorDetalle.value[d.cod_detalle];
        if (conceptosDetalle) {
          total += conceptosDetalle.length;
        }
      });
      return total;
    });

    // Verificar si hay filtros activos
    const hayFiltrosActivos = computed(() => {
      return Object.values(filtros.value).some(valor => valor !== '');
    });

    // MÉTODOS

    // Limpiar filtros inferiores cuando cambia un filtro superior
    const limpiarFiltrosInferiores = (filtrosALimpiar) => {
      filtrosALimpiar.forEach(filtro => {
        filtros.value[filtro] = '';
      });
      
      // Si limpiamos filtros que afectan centros poblados, limpiarlos también
      if (filtrosALimpiar.includes('municipio') || 
          filtrosALimpiar.includes('insumo') || 
          filtrosALimpiar.includes('clasificacion')) {
        centrosPoblados.value = [];
      }
    };

    // Limpiar filtro específico
    const limpiarFiltroEspecifico = (filtro) => {
      filtros.value[filtro] = '';
      
      // Limpiar filtros dependientes
      const jerarquia = ['departamento', 'municipio', 'insumo', 'clasificacion', 'centroPoblado'];
      const indice = jerarquia.indexOf(filtro);
      
      if (indice >= 0) {
        for (let i = indice + 1; i < jerarquia.length; i++) {
          filtros.value[jerarquia[i]] = '';
        }
      }
      
      // Limpiar centros poblados si es necesario
      if (['municipio', 'insumo', 'clasificacion'].includes(filtro)) {
        centrosPoblados.value = [];
      }
    };

    // Limpiar todos los filtros
    const limpiarFiltros = () => {
      Object.keys(filtros.value).forEach(key => {
        filtros.value[key] = '';
      });
      centrosPoblados.value = [];
      paginaActual.value = 1;
    };

    // Funciones para obtener nombres
    const getNombreDepartamento = (cod) => {
      const depto = departamentos.value.find(d => d.cod_depto.toString() === cod.toString());
      return depto ? depto.nom_depto : cod;
    };

    const getNombreMunicipio = (cod) => {
      const municipio = municipiosDisponibles.value.find(m => m.cod_municipio.toString() === cod.toString());
      return municipio ? municipio.nom_municipio : cod;
    };

    const getNombreInsumo = (cod) => {
      const insumo = insumosDisponibles.value.find(i => i.cod_insumo.toString() === cod.toString());
      return insumo ? insumo.categoria_nombre : cod; // CAMBIADO: mostrar categoría
    };

    const getNombreClasificacion = (cod) => {
      const clasificacion = clasificacionesDisponibles.value.find(c => c.cod_clasificacion.toString() === cod.toString());
      return clasificacion ? clasificacion.nombre : cod;
    };

    const getNombreCentroPoblado = (cod) => {
      const centro = centrosPoblados.value.find(c => c.cod_centro_poblado.toString() === cod.toString());
      return centro ? `${centro.cod_centro_poblado} - ${centro.nom_centro_poblado}` : cod;
    };

    // Función para ver PDF de concepto de forma segura - COMO EN InsumosList.vue
    const verDocumentoPDF = async (rutaPdf) => {
      if (!rutaPdf) {
        console.warn('No hay ruta PDF disponible');
        return;
      }
      
      try {
        console.log('🔍 Abriendo PDF:', rutaPdf);
        
        // Usar la API de visualización de PDF con token automático
        const response = await api.get('/preoperacion/ver_pdf/', {
          params: { ruta: rutaPdf },
          responseType: 'blob' // Importante para archivos
        });
        
        // Crear URL del blob para visualización segura
        const blob = new Blob([response], { 
          type: response.type || 'application/pdf' 
        });
        const url = window.URL.createObjectURL(blob);
        
        // Abrir en nueva ventana (seguro)
        window.open(url, '_blank');
        
        // Limpiar URL después de un tiempo
        setTimeout(() => {
          window.URL.revokeObjectURL(url);
        }, 10000);
        
        console.log('✅ PDF abierto en nueva ventana');
        
      } catch (error) {
        console.error('❌ Error al abrir PDF:', error);
        
        // Mostrar error amigable al usuario
        if (error.response?.status === 404) {
          alert('El archivo PDF no se encontró en el servidor.');
        } else if (error.response?.status === 403) {
          alert('No tiene permisos para acceder a este archivo.');
        } else {
          alert('Error al abrir el archivo PDF. Por favor, inténtelo de nuevo.');
        }
      }
    };

    // Función para obtener conceptos de un detalle específico
    const getConceptosDelDetalle = (codDetalle) => {
      return conceptosPorDetalle.value[codDetalle] || [];
    };

    // Función para obtener clase CSS de evaluación
    const getEvaluacionClass = (evaluacion) => {
      if (!evaluacion) return '';
      
      const evaluacionLower = evaluacion.toLowerCase();
      if (evaluacionLower.includes('aprobado') || evaluacionLower.includes('favorable')) return 'evaluacion-aprobado';
      if (evaluacionLower.includes('rechazado') || evaluacionLower.includes('desfavorable')) return 'evaluacion-rechazado';
      if (evaluacionLower.includes('pendiente')) return 'evaluacion-pendiente';
      if (evaluacionLower.includes('revision')) return 'evaluacion-revision';
      return 'evaluacion-default';
    };

    // Ordenación
    const ordenarPor = (campo) => {
      if (ordenacion.value.campo === campo) {
        ordenacion.value.ascendente = !ordenacion.value.ascendente;
      } else {
        ordenacion.value.campo = campo;
        ordenacion.value.ascendente = true;
      }
    };

    const getSortClass = (campo) => {
      if (ordenacion.value.campo !== campo) return '';
      return ordenacion.value.ascendente ? 'asc' : 'desc';
    };

    // Paginación
    const cambiarPagina = (pagina) => {
      if (pagina >= 1 && pagina <= totalPaginas.value) {
        paginaActual.value = pagina;
      }
    };

    // Utilidades
    const formatFecha = (fecha) => {
      if (!fecha) return 'N/A';
      try {
        return new Date(fecha).toLocaleDateString();
      } catch {
        return fecha;
      }
    };

    const getEstadoClass = (estado) => {
      if (!estado) return '';
      
      const estadoLower = estado.toLowerCase();
      if (estadoLower.includes('oficializado')) return 'estado-oficializado';
      if (estadoLower.includes('produccion')) return 'estado-produccion';
      if (estadoLower.includes('pendiente')) return 'estado-pendiente';
      return 'estado-default';
    };

    // Ver detalle
    const verDetalle = (detalle) => {
      modalDetalle.value.detalle = detalle;
      modalDetalle.value.mostrar = true;
    };

    // Watchers
    watch(() => mostrarFiltroCentrosPoblados.value, async (mostrar) => {
      if (mostrar) {
        // Extraer códigos de centros poblados de los datos filtrados
        const codigosUnicos = new Set();
        detallesFiltradosPorJerarquia.value.forEach(detalle => {
          if (detalle.cod_centro_poblado && detalle.cod_centro_poblado !== null) {
            codigosUnicos.add(detalle.cod_centro_poblado);
          }
        });
        
        if (codigosUnicos.size > 0) {
          console.log('🔄 Cargando centros poblados para códigos:', Array.from(codigosUnicos));
          await cargarCentrosPobladosPorCodigos(Array.from(codigosUnicos));
        }
      } else {
        centrosPoblados.value = [];
      }
    });
    
    // Watch para recargar centros poblados cuando cambien los datos
    watch(() => detallesFiltradosPorJerarquia.value.length, async () => {
      if (mostrarFiltroCentrosPoblados.value) {
        const codigosUnicos = new Set();
        detallesFiltradosPorJerarquia.value.forEach(detalle => {
          if (detalle.cod_centro_poblado && detalle.cod_centro_poblado !== null) {
            codigosUnicos.add(detalle.cod_centro_poblado);
          }
        });
        
        if (codigosUnicos.size > 0) {
          await cargarCentrosPobladosPorCodigos(Array.from(codigosUnicos));
        }
      }
    });

    watch(() => elementosPorPagina.value, () => {
      paginaActual.value = 1;
    });

    // Reintentar carga
    const reintentar = async () => {
      console.log('🔄 Reintentando carga de datos...');
      await cargarCatalogos();
      await cargarDetalles();
      await cargarConceptos();
    };

    // Inicialización
    onMounted(async () => {
      await cargarCatalogos();
      await cargarDetalles();
      await cargarConceptos();
    });

    return {
      // Configuración
      API_URL,
      
      // Estado y datos
      cargando,
      error,
      cargandoCentrosPoblados,
      conceptos,
      conceptosPorDetalle,
      
      // Filtros y opciones
      filtros,
      departamentosDisponibles,
      municipiosDisponibles,
      insumosDisponibles,
      clasificacionesDisponibles,
      centrosPobladosDisponibles,
      estadosDisponibles,
      zonasDisponibles,
      entidadesDisponibles,
      mostrarFiltroCentrosPoblados,
      hayFiltrosActivos,
      
      // Datos filtrados y paginación
      detallesFiltrados,
      detallesVisibles,
      paginaActual,
      elementosPorPagina,
      totalPaginas,
      botonesNumericos,
      
      // Estadísticas
      municipiosUnicos,
      entidadesUnicas,
      totalConceptos,
      
      // Ordenación
      ordenacion,
      
      // Modal
      modalDetalle,
      
      // Métodos
      reintentar,
      cargarCentrosPobladosPorCodigos,
      limpiarFiltrosInferiores,
      limpiarFiltroEspecifico,
      limpiarFiltros,
      getNombreDepartamento,
      getNombreMunicipio,
      getNombreInsumo,
      getNombreClasificacion,
      getNombreCentroPoblado,
      getConceptosDelDetalle,
      getEvaluacionClass,
      verDocumentoPDF,
      ordenarPor,
      getSortClass,
      cambiarPagina,
      formatFecha,
      getEstadoClass,
      verDetalle
    };
  }
};
</script>

<style scoped>
/* ESTILOS BASE */
.detalles-list-container {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
}

.header-section {
  margin-bottom: 1.5rem;
  text-align: center;
}

.page-title {
  font-size: 1.6rem;
  color: #333;
  margin: 0 0 0.5rem 0;
}

.page-description {
  color: #6c757d;
  font-size: 1rem;
  margin: 0;
}

/* FILTROS */
.filtros-section {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.row {
  display: flex;
  flex-wrap: wrap;
  margin-right: -15px;
  margin-left: -15px;
  margin-bottom: 1rem;
}

.col-md-6, .col-lg-3 {
  position: relative;
  width: 100%;
  padding-right: 15px;
  padding-left: 15px;
}

@media (min-width: 768px) {
  .col-md-6 {
    flex: 0 0 50%;
    max-width: 50%;
  }
}

@media (min-width: 992px) {
  .col-lg-3 {
    flex: 0 0 25%;
    max-width: 25%;
  }
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #495057;
}

.form-control {
  display: block;
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: 0.9rem;
  line-height: 1.5;
  color: #495057;
  background-color: #fff;
  background-clip: padding-box;
  border: 1px solid #ced4da;
  border-radius: 4px;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-control:focus {
  border-color: #80bdff;
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-control:disabled {
  background-color: #e9ecef;
  opacity: 1;
}

/* FILTROS ACTIVOS */
.filtros-activos {
  margin-top: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%);
  border-radius: 8px;
  border: 1px solid rgba(99, 102, 241, 0.15);
}

.filtros-activos h4 {
  margin: 0 0 0.75rem 0;
  font-size: 0.95rem;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tags-filtros {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tag-filtro {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.75rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border-radius: 16px;
  font-size: 0.85rem;
  font-weight: 500;
}

.tag-filtro button {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tag-filtro button:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* BOTONES */
.filtros-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: 500;
  text-align: center;
  white-space: nowrap;
  vertical-align: middle;
  user-select: none;
  border: 1px solid transparent;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  line-height: 1.5;
  border-radius: 4px;
  transition: all 0.15s ease-in-out;
  cursor: pointer;
  text-decoration: none;
}

.btn-primary {
  color: #fff;
  background-color: #007bff;
  border-color: #007bff;
}

.btn-primary:hover {
  color: #fff;
  background-color: #0069d9;
  border-color: #0062cc;
}

.btn-secondary {
  color: #fff;
  background-color: #6c757d;
  border-color: #6c757d;
}

.btn-secondary:hover {
  color: #fff;
  background-color: #5a6268;
  border-color: #545b62;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
}

.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

/* CARGA Y ERRORES */
.loading-section {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 3rem;
  background-color: white;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  text-align: center;
}

.loading-details {
  color: #6c757d;
  font-size: 0.85rem;
  line-height: 1.4;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f1f5f9;
  border-top: 4px solid #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-indicator-small {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  color: #6366f1;
  font-size: 0.9rem;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid #f1f5f9;
  border-top: 2px solid #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.error-section {
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.error-message {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  color: #c53030;
}

.error-message i {
  font-size: 1.5rem;
  margin-top: 0.25rem;
}

.error-details {
  flex: 1;
}

.error-details ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.error-details li {
  margin-bottom: 0.25rem;
  font-family: monospace;
  font-size: 0.85rem;
}

/* ESTADÍSTICAS */
.stats-section {
  margin-bottom: 1.5rem;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: #6c757d;
  font-size: 0.9rem;
}

/* TABLA */
.table-section {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
  background-color: #f8f9fa;
}

.table-info {
  font-weight: 500;
  color: #495057;
}

.table-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.table-responsive {
  overflow-x: auto;
}

.table {
  width: 100%;
  margin-bottom: 0;
  color: #212529;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 0.75rem;
  vertical-align: top;
  border-top: 1px solid #dee2e6;
  text-align: left;
}

.table thead th {
  vertical-align: bottom;
  border-bottom: 2px solid #dee2e6;
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
}

.table tbody tr:hover {
  background-color: #f5f5f5;
}

.sortable {
  cursor: pointer;
  user-select: none;
  position: relative;
}

.sortable:hover {
  background-color: #e9ecef;
}

.sort-icon {
  margin-left: 0.5rem;
  font-size: 1rem;
  opacity: 0.5;
  transition: all 0.2s;
}

.sort-icon.asc {
  opacity: 1;
  transform: rotate(0deg);
}

.sort-icon.desc {
  opacity: 1;
  transform: rotate(180deg);
}

/* ESTADOS */
.estado-badge {
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.estado-oficializado {
  background-color: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.estado-produccion {
  background-color: #fef3c7;
  color: #92400e;
  border: 1px solid #fde68a;
}

.estado-pendiente {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.estado-default {
  background-color: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

/* PAGINACIÓN */
.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-top: 1px solid #dee2e6;
  background-color: #f8f9fa;
}

.pagination-info {
  color: #6c757d;
  font-size: 0.9rem;
}

.pagination-controls {
  display: flex;
  gap: 0.5rem;
}

/* MODAL */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 900px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #dee2e6;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.btn-close:hover {
  background-color: #f8f9fa;
  color: #495057;
}

.modal-body {
  padding: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item label {
  font-weight: 600;
  color: #495057;
  font-size: 0.9rem;
}

.info-item span {
  color: #212529;
  font-size: 0.95rem;
}

/* CONCEPTOS EN MODAL */
.conceptos-section {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 2px solid #e9ecef;
}

.conceptos-section h4 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 1rem 0;
  color: #495057;
  font-size: 1.1rem;
}

.conceptos-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.concepto-card {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem;
}

.concepto-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.concepto-title {
  font-weight: 600;
  color: #495057;
  font-size: 0.95rem;
}

.evaluacion-badge {
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.evaluacion-aprobado {
  background-color: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.evaluacion-rechazado {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.evaluacion-pendiente {
  background-color: #fef3c7;
  color: #92400e;
  border: 1px solid #fde68a;
}

.evaluacion-revision {
  background-color: #dbeafe;
  color: #1e40af;
  border: 1px solid #93c5fd;
}

.evaluacion-default {
  background-color: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.concepto-content {
  color: #374151;
  font-size: 0.9rem;
  line-height: 1.5;
}

.concepto-content p {
  margin: 0 0 0.5rem 0;
}

.concepto-content strong {
  color: #111827;
}

.concepto-actions {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #dee2e6;
}

.no-conceptos {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
  background: #f8f9fa;
  border-radius: 8px;
  margin-top: 1.5rem;
}

.no-conceptos p {
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .col-md-6, .col-lg-3 {
    flex: 0 0 100%;
    max-width: 100%;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .table-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .pagination-section {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .pagination-controls {
    justify-content: center;
  }
  
  .filtros-buttons {
    justify-content: center;
  }
  
  .tags-filtros {
    justify-content: center;
  }
}
</style>