<template>
  <div class="reportes-preoperacion-page">
    <!-- Cabecera -->
    <div class="page-header">
      <div class="header-content">
        <h1>Reportes de Insumos</h1>
        <div class="header-actions">
          <button @click="exportarFiltros" class="btn-outline">
            <i class="material-icons">save_alt</i>
            Exportar Filtros
          </button>
          <button @click="importarFiltros" class="btn-outline">
            <i class="material-icons">file_upload</i>
            Importar Filtros
          </button>
        </div>
      </div>
    </div>

    <!-- Panel de filtros avanzados -->
    <div class="filters-panel">
      <div class="filters-container">
        <div class="filters-header">
          <h2>
            <i class="material-icons">filter_list</i>
            Filtros de Selección
          </h2>
          <!-- Indicador de modo de filtrado -->
          <div class="filters-mode-indicator">
            <div v-if="busquedaMunicipios.trim()" class="mode-search">
              <i class="material-icons">search</i>
              <span>Filtros aplicados sobre {{ municipiosBusqueda.length }} municipios encontrados</span>
            </div>
            <div v-else class="mode-normal">
              <i class="material-icons">tune</i>
              <span>Filtros sobre todos los municipios ({{ municipiosDisponiblesParaFiltros.length }})</span>
            </div>
          </div>
        </div>

        <!-- 🆕 BÚSQUEDA RÁPIDA INTEGRADA -->
        <div class="quick-search-section">
          <div class="quick-search-header">
            <div class="search-title">
              <i class="material-icons">search</i>
              <h4>Búsqueda Rápida de Municipios</h4>
            </div>
            <div class="search-info" v-if="busquedaMunicipios.trim()">
              <span class="search-results-count">{{ municipiosBusqueda.length }} encontrados</span>
            </div>
          </div>
          
          <div class="search-input-container">
            <i class="material-icons search-icon">search</i>
            <input 
              type="text" 
              v-model="busquedaMunicipios" 
              @input="busquedaInmediataMunicipios"
              placeholder="🔍 Buscar por código (ej: 25175) o nombre de municipio (ej: CHIA )..."
              class="search-input"
            />
            <button 
              v-if="busquedaMunicipios" 
              @click="limpiarBusquedaMunicipios" 
              class="clear-search-btn"
              title="Limpiar búsqueda"
            >
              <i class="material-icons">clear</i>
            </button>
          </div>
          
          <!-- Indicador de búsqueda activa -->
          <div v-if="busquedaMunicipios.trim()" class="search-active-indicator">
            <div class="search-mode-badge">
              <i class="material-icons">filter_alt</i>
              <span>Búsqueda activa:</span>
              <span class="search-term">"{{ busquedaMunicipios.trim() }}"</span>
            </div>
            <button @click="limpiarBusquedaMunicipios" class="btn-clear-search">
              <i class="material-icons">clear</i>
              Limpiar
            </button>
          </div>
        </div>
        
        <!-- Filtros principales -->
        <div class="filters-grid">
          <!-- Departamentos -->
          <div class="filter-group">
            <label>Departamentos:</label>
            <div class="multi-select-container" @click.stop>
              <div class="selected-items" @click="toggleDropdown('departamentos')">
                <span v-if="selectedDepartamentos.length === 0" class="placeholder">
                  Seleccionar departamentos...
                </span>
                <span v-else class="selection-summary">
                  {{ selectedDepartamentos.length }} departamento(s) seleccionado(s)
                </span>
                <i class="material-icons">{{ dropdownStates.departamentos ? 'expand_less' : 'expand_more' }}</i>
              </div>
              <div v-if="dropdownStates.departamentos" class="dropdown-menu" @click.stop>
                <div class="dropdown-header">
                  <button @click="selectAllDepartamentos" class="btn-text">Seleccionar todos</button>
                  <button @click="clearDepartamentos" class="btn-text">Limpiar</button>
                </div>
                <div class="dropdown-search">
                  <input 
                    type="text" 
                    v-model="searchDepartamentos"
                    placeholder="Buscar departamento..."
                    @click.stop
                  />
                </div>
                <div class="dropdown-items">
                  <label 
                    v-for="depto in filteredDepartamentos" 
                    :key="depto.cod_depto"
                    class="dropdown-item"
                    @click.stop
                  >
                    <input 
                      type="checkbox"
                      :value="depto.cod_depto"
                      v-model="selectedDepartamentos"
                      @change="onDepartamentosChange"
                      @click.stop
                    />
                    <span>{{ depto.nom_depto }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Municipios -->
          <div class="filter-group">
            <label>Municipios:</label>
            <div class="multi-select-container">
              <div class="selected-items" @click="toggleDropdown('municipios')">
                <span v-if="selectedMunicipios.length === 0" class="placeholder">
                  Seleccionar municipios...
                </span>
                <span v-else class="selection-summary">
                  {{ selectedMunicipios.length }} municipio(s) seleccionado(s)
                </span>
                <i class="material-icons">{{ dropdownStates.municipios ? 'expand_less' : 'expand_more' }}</i>
              </div>
              <div v-if="dropdownStates.municipios" class="dropdown-menu">
                <div class="dropdown-header">
                  <button @click="selectAllMunicipios" class="btn-text">Seleccionar todos</button>
                  <button @click="clearMunicipios" class="btn-text">Limpiar</button>
                </div>
                <div class="dropdown-search">
                  <input 
                    type="text" 
                    v-model="searchMunicipios"
                    placeholder="Buscar municipio..."
                  />
                </div>
                <div class="dropdown-items">
                  <label 
                    v-for="municipio in filteredMunicipios" 
                    :key="municipio.cod_municipio"
                    class="dropdown-item"
                  >
                    <input 
                      type="checkbox"
                      :value="municipio.cod_municipio"
                      v-model="selectedMunicipios"
                    />
                    <span>{{ municipio.nom_municipio }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Territoriales -->
          <div class="filter-group">
            <label>Territoriales:</label>
            <div class="multi-select-container" @click.stop>
              <div class="selected-items" @click="toggleDropdown('territoriales')">
                <span v-if="selectedTerritoriales.length === 0" class="placeholder">
                  Seleccionar territoriales...
                </span>
                <span v-else class="selection-summary">
                  {{ selectedTerritoriales.length }} territorial(es) seleccionado(s)
                </span>
                <i class="material-icons">{{ dropdownStates.territoriales ? 'expand_less' : 'expand_more' }}</i>
              </div>
              <div v-if="dropdownStates.territoriales" class="dropdown-menu" @click.stop>
                <div class="dropdown-header">
                  <button @click="selectAllTerritoriales" class="btn-text">Seleccionar todos</button>
                  <button @click="clearTerritoriales" class="btn-text">Limpiar</button>
                </div>
                <div class="dropdown-search">
                  <input 
                    type="text" 
                    v-model="searchTerritoriales"
                    placeholder="Buscar territorial..."
                    @click.stop
                  />
                </div>
                <div class="dropdown-items">
                  <label 
                    v-for="territorial in filteredTerritoriales" 
                    :key="territorial.nom_territorial"
                    class="dropdown-item"
                    @click.stop
                  >
                    <input 
                      type="checkbox"
                      :value="territorial.nom_territorial"
                      v-model="selectedTerritoriales"
                      @change="onTerritorialesChange"
                      @click.stop
                    />
                    <span>{{ territorial.nom_territorial }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Mecanismos Generales -->
          <div class="filter-group">
            <label>Mecanismos Generales:</label>
            <div class="multi-select-container" @click.stop>
              <div class="selected-items" @click="toggleDropdown('mecanismosGenerales')">
                <span v-if="selectedMecanismosGenerales.length === 0" class="placeholder">
                  Seleccionar mecanismos...
                </span>
                <span v-else class="selection-summary">
                  {{ selectedMecanismosGenerales.length }} mecanismo(s) seleccionado(s)
                </span>
                <i class="material-icons">{{ dropdownStates.mecanismosGenerales ? 'expand_less' : 'expand_more' }}</i>
              </div>
              <div v-if="dropdownStates.mecanismosGenerales" class="dropdown-menu" @click.stop>
                <div class="dropdown-header">
                  <button @click="selectAllMecanismosGenerales" class="btn-text">Seleccionar todos</button>
                  <button @click="clearMecanismosGenerales" class="btn-text">Limpiar</button>
                </div>
                <div class="dropdown-search">
                  <input 
                    type="text" 
                    v-model="searchMecanismosGenerales"
                    placeholder="Buscar mecanismo..."
                    @click.stop
                  />
                </div>
                <div class="dropdown-items">
                  <label 
                    v-for="mecanismo in filteredMecanismosGenerales" 
                    :key="mecanismo.cod_mecanismo"
                    class="dropdown-item"
                    @click.stop
                  >
                    <input 
                      type="checkbox"
                      :value="mecanismo.cod_mecanismo"
                      v-model="selectedMecanismosGenerales"
                      @change="onMecanismosGeneralesChange"
                      @click.stop
                    />
                    <span>{{ mecanismo.descripcion || mecanismo.cod_mecanismo }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Mecanismos Detalle -->
          <div class="filter-group">
            <label>Mecanismos Detalle:</label>
            <div class="multi-select-container" @click.stop>
              <div class="selected-items" @click="toggleDropdown('mecanismosDetalle')">
                <span v-if="selectedMecanismosDetalle.length === 0" class="placeholder">
                  Seleccionar mecanismos detalle...
                </span>
                <span v-else class="selection-summary">
                  {{ selectedMecanismosDetalle.length }} mecanismo(s) detalle seleccionado(s)
                </span>
                <i class="material-icons">{{ dropdownStates.mecanismosDetalle ? 'expand_less' : 'expand_more' }}</i>
              </div>
              <div v-if="dropdownStates.mecanismosDetalle" class="dropdown-menu" @click.stop>
                <div class="dropdown-header">
                  <button @click="selectAllMecanismosDetalle" class="btn-text">Seleccionar todos</button>
                  <button @click="clearMecanismosDetalle" class="btn-text">Limpiar</button>
                </div>
                <div class="dropdown-search">
                  <input 
                    type="text" 
                    v-model="searchMecanismosDetalle"
                    placeholder="Buscar mecanismo detalle..."
                    @click.stop
                  />
                </div>
                <div class="dropdown-items">
                  <label 
                    v-for="mecanismo in filteredMecanismosDetalle" 
                    :key="mecanismo.cod_mecanismo_detalle"
                    class="dropdown-item"
                    @click.stop
                  >
                    <input 
                      type="checkbox"
                      :value="mecanismo.cod_mecanismo_detalle"
                      v-model="selectedMecanismosDetalle"
                      @change="onMecanismosDetalleChange"
                      @click.stop
                    />
                    <span>{{ mecanismo.descripcion || mecanismo.cod_mecanismo_detalle }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Grupos -->
          <div class="filter-group">
            <label>Grupos:</label>
            <div class="multi-select-container" @click.stop>
              <div class="selected-items" @click="toggleDropdown('grupos')">
                <span v-if="selectedGrupos.length === 0" class="placeholder">
                  Seleccionar grupos...
                </span>
                <span v-else class="selection-summary">
                  {{ selectedGrupos.length }} grupo(s) seleccionado(s)
                </span>
                <i class="material-icons">{{ dropdownStates.grupos ? 'expand_less' : 'expand_more' }}</i>
              </div>
              <div v-if="dropdownStates.grupos" class="dropdown-menu" @click.stop>
                <div class="dropdown-header">
                  <button @click="selectAllGrupos" class="btn-text">Seleccionar todos</button>
                  <button @click="clearGrupos" class="btn-text">Limpiar</button>
                </div>
                <div class="dropdown-search">
                  <input 
                    type="text" 
                    v-model="searchGrupos"
                    placeholder="Buscar grupo..."
                    @click.stop
                  />
                </div>
                <div class="dropdown-items">
                  <label 
                    v-for="grupo in filteredGrupos" 
                    :key="grupo.cod_grupo"
                    class="dropdown-item"
                    @click.stop
                  >
                    <input 
                      type="checkbox"
                      :value="grupo.cod_grupo"
                      v-model="selectedGrupos"
                      @click.stop
                    />
                    <span>{{ grupo.descripcion || grupo.cod_grupo }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Filtro especial de códigos de municipio -->
        <div class="special-filter-section">
          <div class="section-toggle">
            <label class="toggle-switch">
              <input 
                type="checkbox" 
                v-model="useCodigosMunicipioFilter"
                @change="onCodigosFilterToggle"
              />
              <span class="toggle-slider"></span>
            </label>
            <span class="toggle-label">Filtro por códigos de municipio específicos</span>
          </div>

          <div v-if="useCodigosMunicipioFilter" class="codigo-filter-content">
            <div class="input-methods">
              <!-- Input manual -->
              <div class="input-method">
                <h4>Ingreso Manual</h4>
                <p class="method-description">
                  Ingrese los códigos de municipio separados por comas (ejemplo: 17174, 17001, 17486)
                </p>
                <textarea 
                  v-model="codigosManuales"
                  placeholder="17174, 17001, 17486, ..."
                  rows="3"
                  @input="onCodigosManualesChange"
                ></textarea>
                <div class="validation-info">
                  <span v-if="codigosValidados.length > 0" class="valid-codes">
                    ✓ {{ codigosValidados.length }} códigos válidos encontrados
                  </span>
                  <span v-if="codigosInvalidos.length > 0" class="invalid-codes">
                    ⚠ {{ codigosInvalidos.length }} códigos inválidos: {{ codigosInvalidos.join(', ') }}
                  </span>
                </div>
              </div>

              <!-- Upload de archivo -->
              <div class="input-method">
                <h4>Cargar desde Archivo</h4>
                <p class="method-description">
                  Suba un archivo Excel (.xlsx), CSV (.csv) o texto (.txt) con los códigos de municipio.
                  <br><strong>Formatos soportados:</strong>
                </p>
                <ul class="format-examples">
                  <li><strong>Excel:</strong> Columna A con códigos (A1: 17174, A2: 17001, ...)</li>
                  <li><strong>CSV:</strong> Una columna con códigos separados por comas o saltos de línea</li>
                  <li><strong>TXT:</strong> Códigos separados por comas, espacios o saltos de línea</li>
                </ul>
                
                <div class="file-upload-area" @dragover.prevent @drop.prevent="handleFileDrop">
                  <input 
                    type="file" 
                    ref="fileInput"
                    @change="handleFileSelect"
                    accept=".xlsx,.xls,.csv,.txt"
                    style="display: none"
                  />
                  <div class="upload-content" @click="$refs.fileInput.click()">
                    <i class="material-icons">cloud_upload</i>
                    <p>Haga clic aquí o arrastre un archivo</p>
                    <p class="file-types">(.xlsx, .csv, .txt)</p>
                  </div>
                </div>

                <div v-if="archivoSeleccionado" class="file-selected">
                  <i class="material-icons">attach_file</i>
                  <span>{{ archivoSeleccionado.name }}</span>
                  <button @click="removeFile" class="btn-remove">
                    <i class="material-icons">close</i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Acciones de filtros -->
        <div class="filter-actions">
          <button @click="clearAllFilters" class="btn-secondary">
            <i class="material-icons">clear_all</i>
            Limpiar Todos los Filtros
          </button>
          <button @click="aplicarFiltros" class="btn-primary" :disabled="loading">
            <i class="material-icons">filter_alt</i>
            Aplicar Filtros ({{ municipiosFiltrados.length }} municipios)
          </button>
        </div>
      </div>
    </div>

    <!-- Resultados -->
    <div v-if="municipiosFiltrados.length > 0" class="results-section">
      <div class="results-header">
        <h2>Municipios Seleccionados ({{ municipiosFiltrados.length }})</h2>
        <div class="generation-options">
          <div class="report-types">
            <label class="checkbox-label">
              <input type="checkbox" v-model="generarReportesIndividuales" />
              <span>Reportes Individuales ({{ municipiosFiltrados.length }} archivos)</span>
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="generarReporteResumen" />
              <span>Reporte Resumen Matriz (1 archivo)</span>
            </label>
          </div>
          <button 
            @click="generarReportes" 
            class="btn-success"
            :disabled="loading || (!generarReportesIndividuales && !generarReporteResumen)"
          >
            <i class="material-icons">{{ loading ? 'hourglass_empty' : 'download' }}</i>
            {{ loading ? 'Generando...' : 'Generar Reportes' }}
          </button>
        </div>
      </div>

      <!-- Vista previa de municipios -->
      <div class="municipalities-preview">
        <div class="preview-table-container">
          <table class="preview-table">
            <thead>
              <tr>
                <th>Código</th>
                <th>Municipio</th>
                <th>Departamento</th>
                <th>Territorial</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="municipio in paginatedMunicipios" :key="municipio.cod_municipio">
                <td>{{ municipio.cod_municipio }}</td>
                <td>{{ municipio.nom_municipio }}</td>
                <td>{{ getNombreDepartamento(municipio.cod_depto) }}</td>
                <td>{{ municipio.nom_territorial || 'No asignada' }}</td>
                <td>
                  <span :class="['status-badge', municipio.en_operacion === 'Sí' ? 'active' : 'inactive']">
                    {{ municipio.en_operacion === 'Sí' ? 'Activo' : 'Inactivo' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Paginación -->
        <div v-if="municipiosFiltrados.length > pageSize" class="pagination">
          <button 
            @click="currentPage--" 
            :disabled="currentPage === 1"
            class="pagination-btn"
          >
            <i class="material-icons">chevron_left</i>
          </button>
          
          <span class="page-info">
            Página {{ currentPage }} de {{ totalPages }}
          </span>
          
          <button 
            @click="currentPage++" 
            :disabled="currentPage === totalPages"
            class="pagination-btn"
          >
            <i class="material-icons">chevron_right</i>
          </button>
        </div>
      </div>
    </div>

    <!-- Estados de carga y mensajes -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <div class="spinner"></div>
        <p>{{ loadingMessage }}</p>
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
import { defineComponent, ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import * as XLSX from 'xlsx';
import { API_URL } from '@/api/config';

export default defineComponent({
  name: 'ReportesPreoperacion',
  
  setup() {
    const router = useRouter();
    
    // Estados principales
    const loading = ref(false);
    const loadingMessage = ref('');
    
    // 🆕 NUEVO: Estado para búsqueda de municipios
    const busquedaMunicipios = ref('');
    const municipiosBusqueda = ref<any[]>([]);
    const buscandoMunicipios = ref(false);
    
    // Datos maestros
    const departamentos = ref<any[]>([]);
    const municipiosList = ref<any[]>([]);
    const territoriales = ref<any[]>([]);
    const mecanismosGenerales = ref<any[]>([]);
    const grupos = ref<any[]>([]);
    const mecanismosDetalle = ref<any[]>([]);
    
    // Estados de filtros
    const selectedDepartamentos = ref<string[]>([]);
    const selectedMunicipios = ref<string[]>([]);
    const selectedTerritoriales = ref<string[]>([]);
    const selectedMecanismosGenerales = ref<string[]>([]);
    const selectedGrupos = ref<string[]>([]);
    const selectedMecanismosDetalle = ref<string[]>([]);
    
    // Estados de dropdown
    const dropdownStates = ref({
      departamentos: false,
      municipios: false,
      territoriales: false,
      mecanismosGenerales: false, 
      mecanismosDetalle: false,  
      grupos: false               
    });
    
    // Búsquedas en dropdowns
    const searchDepartamentos = ref('');
    const searchMunicipios = ref('');
    const searchTerritoriales = ref('');
    const searchMecanismosDetalle = ref('');

    // Filtro especial por códigos
    const useCodigosMunicipioFilter = ref(false);
    const codigosManuales = ref('');
    const codigosValidados = ref<string[]>([]);
    const codigosInvalidos = ref<string[]>([]);
    const archivoSeleccionado = ref<File | null>(null);
    
    // Opciones de generación
    const generarReportesIndividuales = ref(true);
    const generarReporteResumen = ref(true);
    
    // Paginación
    const currentPage = ref(1);
    const pageSize = ref(20);
    
    // Notificación
    const notification = ref({
      show: false,
      message: '',
      type: 'success',
      icon: 'check_circle',
      timeout: null as number | null
    });
    
    // 🆕 NUEVA FUNCIÓN: Búsqueda inmediata de municipios
    const busquedaInmediataMunicipios = () => {
      console.log('🔍 Búsqueda inmediata de municipios:', busquedaMunicipios.value);
      
      if (!busquedaMunicipios.value.trim()) {
        municipiosBusqueda.value = [];
        return;
      }
      
      realizarBusquedaMunicipios();
    };
    
    // 🆕 NUEVA FUNCIÓN: Realizar búsqueda de municipios
    const realizarBusquedaMunicipios = async () => {
      try {
        buscandoMunicipios.value = true;
        const terminoBusqueda = busquedaMunicipios.value.trim();
        console.log('🔍 Término de búsqueda:', terminoBusqueda);
        
        if (!terminoBusqueda) {
          municipiosBusqueda.value = [];
          return;
        }
        
        // Estrategia múltiple de búsqueda (similar a MunicipiosList.vue)
        let municipiosEncontrados: any[] = [];
        
        // 1. Búsqueda por código exacto (si es numérico)
        if (/^\d+$/.test(terminoBusqueda)) {
          console.log('🔍 Búsqueda por código:', terminoBusqueda);
          try {
            const municipioEspecifico = await cargarTodosLosDatos(`${API_URL}/preoperacion/municipios/`, {
              cod_municipio: terminoBusqueda
            });
            if (municipioEspecifico.length > 0) {
              municipiosEncontrados = [...municipiosEncontrados, ...municipioEspecifico];
            }
          } catch (error) {
            console.log('No se encontró por código exacto');
          }
        }
        
        // 2. Búsqueda general con parámetro search
        try {
          console.log('🔍 Búsqueda general con search:', terminoBusqueda);
          const municipiosBusqueda = await cargarTodosLosDatos(`${API_URL}/preoperacion/municipios/`, {
            search: terminoBusqueda
          });
          if (municipiosBusqueda.length > 0) {
            municipiosEncontrados = [...municipiosEncontrados, ...municipiosBusqueda];
          }
        } catch (error) {
          console.log('Error en búsqueda general:', error);
        }
        
        // 3. Si no hay resultados, cargar todos y filtrar en cliente
        if (municipiosEncontrados.length === 0) {
          console.log('🔍 Búsqueda en cliente (fallback)');
          // Si ya tenemos municipios cargados, usarlos
          let todosMunicipios = municipiosList.value;
          if (todosMunicipios.length === 0) {
            todosMunicipios = await cargarTodosLosDatos(`${API_URL}/preoperacion/municipios/`);
          }
          
          municipiosEncontrados = todosMunicipios.filter(m => {
            const codigoCoincide = m.cod_municipio.toString().includes(terminoBusqueda);
            const nombreCoincide = m.nom_municipio.toLowerCase().includes(terminoBusqueda.toLowerCase());
            return codigoCoincide || nombreCoincide;
          });
        }
        
        // Eliminar duplicados por cod_municipio
        const municipiosUnicos = Array.from(
          new Map(municipiosEncontrados.map(m => [m.cod_municipio, m])).values()
        );
        
        municipiosBusqueda.value = municipiosUnicos;
        console.log(`✅ Búsqueda completada: ${municipiosBusqueda.value.length} municipios encontrados`);
        
        if (municipiosBusqueda.value.length === 0) {
          console.log('⚠️ No se encontraron municipios con el término:', terminoBusqueda);
        }
        
      } catch (error) {
        console.error('❌ Error en búsqueda de municipios:', error);
        showNotification('Error al realizar la búsqueda. Inténtelo de nuevo.', 'error');
      } finally {
        buscandoMunicipios.value = false;
      }
    };
    
    // 🆕 NUEVA FUNCIÓN: Limpiar búsqueda de municipios
    const limpiarBusquedaMunicipios = () => {
      console.log('🧹 Limpiando búsqueda de municipios');
      busquedaMunicipios.value = '';
      municipiosBusqueda.value = [];
      currentPage.value = 1;
    };
    
    // 🆕 NUEVO COMPUTED: Municipios disponibles para filtros (base)
    const municipiosDisponiblesParaFiltros = computed(() => {
      // Si hay búsqueda activa, usar resultados de búsqueda como base
      if (busquedaMunicipios.value.trim()) {
        return municipiosBusqueda.value;
      }
      // Si no hay búsqueda, usar todos los municipios
      return municipiosList.value;
    });
    
    // Función para cargar todos los datos con paginación
    const cargarTodosLosDatos = async (url: string, params = {}) => {
      let allResults = [];
      
      try {
        const token = localStorage.getItem('token');
        const config = token ? {
          headers: {
            'Authorization': `Token ${token}`
          }
        } : {};
        
        let currentUrl = url;
        if (Object.keys(params).length > 0) {
          const queryParams = new URLSearchParams(params as any).toString();
          currentUrl = `${url}?${queryParams}`;
        }
        
        // Usar fetch en lugar de axios para mayor compatibilidad
        const response = await fetch(currentUrl, {
          ...config,
          headers: {
            ...config.headers,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });
        
        if (!response.ok) {
          throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Manejar respuestas paginadas y no paginadas
        if (data.results && Array.isArray(data.results)) {
          allResults = [...data.results];
          let nextUrl = data.next;
          
          // Cargar todas las páginas
          while (nextUrl) {
            const nextResponse = await fetch(nextUrl, config);
            if (!nextResponse.ok) break;
            
            const nextData = await nextResponse.json();
            if (nextData.results && Array.isArray(nextData.results)) {
              allResults = [...allResults, ...nextData.results];
            }
            nextUrl = nextData.next;
          }
        } else if (Array.isArray(data)) {
          allResults = data;
        } else {
          allResults = [];
        }
        
      } catch (error) {
        console.error(`Error cargando datos de ${url}:`, error);
        throw error;
      }
      
      return allResults;
    };
    
    // Cargar datos iniciales
    // SOLUCIÓN INTEGRAL PARA TODOS LOS FILTROS EN REPORTES-PREOPERACION.VUE
    const mecanismosGeneralesDisponibles = computed(() => {
      console.log('🔍 Calculando mecanismos generales disponibles...');
      
      // Usar la base de municipios (búsqueda o todos)
      const municipiosBase = municipiosDisponiblesParaFiltros.value;
      
      // Si no hay filtros aplicados, mostrar todos basados en los municipios base
      if (selectedDepartamentos.value.length === 0 && 
          selectedMunicipios.value.length === 0 && 
          selectedTerritoriales.value.length === 0) {
        // Extraer mecanismos únicos de la base actual
        const mecanismosEncontrados = new Set();
        municipiosBase.forEach(municipio => {
          if (municipio.mecanismo_general) {
            mecanismosEncontrados.add(municipio.mecanismo_general);
          }
        });
        
        const resultado = mecanismosGenerales.value.filter(mecanismo => 
          mecanismosEncontrados.has(mecanismo.cod_mecanismo)
        );
        console.log(`- Sin filtros previos, mostrando basados en base actual: ${resultado.length}`);
        return resultado;
      }
      
      // Filtrar municipios según los filtros aplicados
      let municipiosFiltrados = [...municipiosBase];
      
      // Aplicar filtro de departamentos
      if (selectedDepartamentos.value.length > 0) {
        municipiosFiltrados = municipiosFiltrados.filter(m => 
          selectedDepartamentos.value.includes(String(m.cod_depto))
        );
      }
      
      // Aplicar filtro de municipios específicos
      if (selectedMunicipios.value.length > 0) {
        municipiosFiltrados = municipiosFiltrados.filter(m => 
          selectedMunicipios.value.includes(String(m.cod_municipio))
        );
      }
      
      // Aplicar filtro de territoriales
      if (selectedTerritoriales.value.length > 0) {
        municipiosFiltrados = municipiosFiltrados.filter(m => 
          m.nom_territorial && selectedTerritoriales.value.includes(m.nom_territorial)
        );
      }
      
      // Extraer mecanismos generales únicos de los municipios filtrados
      const mecanismosEncontrados = new Set();
      
      municipiosFiltrados.forEach(municipio => {
        if (municipio.mecanismo_general) {
          mecanismosEncontrados.add(municipio.mecanismo_general);
        }
      });
      
      console.log(`- Mecanismos generales encontrados: ${mecanismosEncontrados.size}`);
      
      // Filtrar la lista original para mantener el orden
      const resultado = mecanismosGenerales.value.filter(mecanismo => 
        mecanismosEncontrados.has(mecanismo.cod_mecanismo)
      );
      
      console.log(`- Resultado final: ${resultado.length} mecanismos generales`);
      return resultado;
    });

    // 2. Mecanismos detalle disponibles basado en selecciones anteriores
    const mecanismosDetalleDisponibles = computed(() => {
      console.log('🔍 Calculando mecanismos detalle disponibles...');
      
      const municipiosBase = municipiosDisponiblesParaFiltros.value;
      
      // Si no hay filtros aplicados y no hay mecanismos generales seleccionados, mostrar todos basados en la base
      if (selectedDepartamentos.value.length === 0 && 
          selectedMunicipios.value.length === 0 && 
          selectedTerritoriales.value.length === 0 &&
          selectedMecanismosGenerales.value.length === 0) {
        // Extraer mecanismos detalle únicos de la base actual
        const mecanismosEncontrados = new Set();
        municipiosBase.forEach(municipio => {
          if (municipio.mecanismo_detalle) {
            mecanismosEncontrados.add(municipio.mecanismo_detalle);
          }
        });
        
        const resultado = mecanismosDetalle.value.filter(mecanismo => 
          mecanismosEncontrados.has(mecanismo.cod_mecanismo_detalle)
        );
        console.log(`- Sin filtros previos, mostrando basados en base actual: ${resultado.length}`);
        return resultado;
      }
      
      // Filtrar municipios según los filtros aplicados
      let municipiosFiltrados = [...municipiosBase];
      
      // Aplicar filtro de departamentos
      if (selectedDepartamentos.value.length > 0) {
        municipiosFiltrados = municipiosFiltrados.filter(m => 
          selectedDepartamentos.value.includes(String(m.cod_depto))
        );
      }
      
      // Aplicar filtro de municipios específicos
      if (selectedMunicipios.value.length > 0) {
        municipiosFiltrados = municipiosFiltrados.filter(m => 
          selectedMunicipios.value.includes(String(m.cod_municipio))
        );
      }
      
      // Aplicar filtro de territoriales
      if (selectedTerritoriales.value.length > 0) {
        municipiosFiltrados = municipiosFiltrados.filter(m => 
          m.nom_territorial && selectedTerritoriales.value.includes(m.nom_territorial)
        );
      }
      
      // Aplicar filtro de mecanismos generales
      if (selectedMecanismosGenerales.value.length > 0) {
        municipiosFiltrados = municipiosFiltrados.filter(m => 
          m.mecanismo_general && selectedMecanismosGenerales.value.includes(m.mecanismo_general)
        );
      }
      
      // Extraer mecanismos detalle únicos de los municipios filtrados
      const mecanismosEncontrados = new Set();
      
      municipiosFiltrados.forEach(municipio => {
        if (municipio.mecanismo_detalle) {
          mecanismosEncontrados.add(municipio.mecanismo_detalle);
        }
      });
      
      console.log(`- Mecanismos detalle encontrados: ${mecanismosEncontrados.size}`);
      
      // Filtrar la lista original para mantener el orden
      const resultado = mecanismosDetalle.value.filter(mecanismo => 
        mecanismosEncontrados.has(mecanismo.cod_mecanismo_detalle)
      );
      
      console.log(`- Resultado final: ${resultado.length} mecanismos detalle`);
      return resultado;
    });

    // 3. Grupos disponibles basado en selecciones anteriores
    const gruposDisponibles = computed(() => {
      console.log('🔍 Calculando grupos disponibles...');
      
      const municipiosBase = municipiosDisponiblesParaFiltros.value;
      
      // Si no hay filtros aplicados, mostrar todos basados en la base
      if (selectedDepartamentos.value.length === 0 && 
          selectedMunicipios.value.length === 0 && 
          selectedTerritoriales.value.length === 0 &&
          selectedMecanismosGenerales.value.length === 0 &&
          selectedMecanismosDetalle.value.length === 0) {
        // Extraer grupos únicos de la base actual
        const gruposEncontrados = new Set();
        municipiosBase.forEach(municipio => {
          if (municipio.grupo) {
            gruposEncontrados.add(municipio.grupo);
          }
        });
        
        const resultado = grupos.value.filter(grupo => 
          gruposEncontrados.has(grupo.cod_grupo)
        );
        console.log(`- Sin filtros previos, mostrando basados en base actual: ${resultado.length}`);
        return resultado;
      }
      
      // Filtrar municipios según los filtros aplicados
      let municipiosFiltrados = [...municipiosBase];
      
      // Aplicar filtro de departamentos
      if (selectedDepartamentos.value.length > 0) {
        municipiosFiltrados = municipiosFiltrados.filter(m => 
          selectedDepartamentos.value.includes(String(m.cod_depto))
        );
      }
      
      // Aplicar filtro de municipios específicos
      if (selectedMunicipios.value.length > 0) {
        municipiosFiltrados = municipiosFiltrados.filter(m => 
          selectedMunicipios.value.includes(String(m.cod_municipio))
        );
      }
      
      // Aplicar filtro de territoriales
      if (selectedTerritoriales.value.length > 0) {
        municipiosFiltrados = municipiosFiltrados.filter(m => 
          m.nom_territorial && selectedTerritoriales.value.includes(m.nom_territorial)
        );
      }
      
      // Aplicar filtro de mecanismos generales
      if (selectedMecanismosGenerales.value.length > 0) {
        municipiosFiltrados = municipiosFiltrados.filter(m => 
          m.mecanismo_general && selectedMecanismosGenerales.value.includes(m.mecanismo_general)
        );
      }
      
      // Aplicar filtro de mecanismos detalle
      if (selectedMecanismosDetalle.value.length > 0) {
        municipiosFiltrados = municipiosFiltrados.filter(m => 
          m.mecanismo_detalle && selectedMecanismosDetalle.value.includes(m.mecanismo_detalle)
        );
      }
      
      // Extraer grupos únicos de los municipios filtrados
      const gruposEncontrados = new Set();
      
      municipiosFiltrados.forEach(municipio => {
        if (municipio.grupo) {
          gruposEncontrados.add(municipio.grupo);
        }
      });
      
      console.log(`- Grupos encontrados: ${gruposEncontrados.size}`);
      
      // Filtrar la lista original para mantener el orden
      const resultado = grupos.value.filter(grupo => 
        gruposEncontrados.has(grupo.cod_grupo)
      );
      
      console.log(`- Resultado final: ${resultado.length} grupos`);
      return resultado;
    });

    // 4. Modificar los filtered properties existentes para usar las nuevas propiedades
    const filteredMecanismosGenerales = computed(() => {
      console.log('🔍 Calculando mecanismos generales filtrados...');
      
      if (!searchMecanismosGenerales.value) {
        console.log(`- Sin búsqueda, mostrando disponibles: ${mecanismosGeneralesDisponibles.value.length}`);
        return mecanismosGeneralesDisponibles.value;
      }
      
      const search = searchMecanismosGenerales.value.toLowerCase();
      const result = mecanismosGeneralesDisponibles.value.filter(mecanismo => {
        const codMatch = mecanismo.cod_mecanismo.toLowerCase().includes(search);
        const descMatch = mecanismo.descripcion && mecanismo.descripcion.toLowerCase().includes(search);
        return codMatch || descMatch;
      });
      
      console.log(`- Con búsqueda "${search}": ${result.length} resultados`);
      return result;
    });

    const filteredMecanismosDetalle = computed(() => {
      console.log('🔍 Calculando mecanismos detalle filtrados...');
      
      if (!searchMecanismosDetalle.value) {
        console.log(`- Sin búsqueda, mostrando disponibles: ${mecanismosDetalleDisponibles.value.length}`);
        return mecanismosDetalleDisponibles.value;
      }
      
      const search = searchMecanismosDetalle.value.toLowerCase();
      const result = mecanismosDetalleDisponibles.value.filter(mecanismo => {
        const codMatch = mecanismo.cod_mecanismo_detalle.toLowerCase().includes(search);
        const descMatch = mecanismo.descripcion && mecanismo.descripcion.toLowerCase().includes(search);
        return codMatch || descMatch;
      });
      
      console.log(`- Con búsqueda "${search}": ${result.length} resultados`);
      return result;
    });

    const filteredGrupos = computed(() => {
      console.log('🔍 Calculando grupos filtrados...');
      
      if (!searchGrupos.value) {
        console.log(`- Sin búsqueda, mostrando disponibles: ${gruposDisponibles.value.length}`);
        return gruposDisponibles.value;
      }
      
      const search = searchGrupos.value.toLowerCase();
      const result = gruposDisponibles.value.filter(grupo => {
        const codMatch = grupo.cod_grupo.toLowerCase().includes(search);
        const descMatch = grupo.descripcion && grupo.descripcion.toLowerCase().includes(search);
        return codMatch || descMatch;
      });
      
      console.log(`- Con búsqueda "${search}": ${result.length} resultados`);
      return result;
    });

    // 5. Añadir variables de búsqueda para los nuevos filtros
    const searchMecanismosGenerales = ref('');
    const searchGrupos = ref('');

    // 6. Añadir funciones de cambio para actualizar selecciones
    const onMecanismosGeneralesChange = () => {
      console.log('🔄 onMecanismosGeneralesChange ejecutado');
      console.log('- Mecanismos generales seleccionados:', selectedMecanismosGenerales.value);
      
      if (selectedMecanismosGenerales.value.length > 0) {
        // Limpiar mecanismos detalle que ya no aplican
        const mecanismosDetalleAnteriores = selectedMecanismosDetalle.value.length;
        
        // Usar la base de municipios correcta
        const municipiosBase = municipiosDisponiblesParaFiltros.value;
        
        // Obtener los mecanismos detalle válidos basados en los mecanismos generales seleccionados
        const mecanismosDetalleValidos = new Set();
        municipiosBase.forEach(municipio => {
          if (selectedMecanismosGenerales.value.includes(municipio.mecanismo_general) && 
              municipio.mecanismo_detalle) {
            mecanismosDetalleValidos.add(municipio.mecanismo_detalle);
          }
        });
        
        // Filtrar los mecanismos detalle seleccionados
        selectedMecanismosDetalle.value = selectedMecanismosDetalle.value.filter(mecanismo => 
          mecanismosDetalleValidos.has(mecanismo)
        );
        
        console.log(`- Mecanismos detalle actualizados: ${selectedMecanismosDetalle.value.length} (antes: ${mecanismosDetalleAnteriores})`);
        
        // Limpiar grupos que ya no aplican
        const gruposAnteriores = selectedGrupos.value.length;
        
        // Obtener los grupos válidos basados en los mecanismos generales seleccionados
        const gruposValidos = new Set();
        municipiosBase.forEach(municipio => {
          if (selectedMecanismosGenerales.value.includes(municipio.mecanismo_general) && 
              municipio.grupo) {
            gruposValidos.add(municipio.grupo);
          }
        });
        
        // Filtrar los grupos seleccionados
        selectedGrupos.value = selectedGrupos.value.filter(grupo => 
          gruposValidos.has(grupo)
        );
        
        console.log(`- Grupos actualizados: ${selectedGrupos.value.length} (antes: ${gruposAnteriores})`);
      }
    };

    const onMecanismosDetalleChange = () => {
      console.log('🔄 onMecanismosDetalleChange ejecutado');
      console.log('- Mecanismos detalle seleccionados:', selectedMecanismosDetalle.value);
      
      if (selectedMecanismosDetalle.value.length > 0) {
        // Limpiar grupos que ya no aplican
        const gruposAnteriores = selectedGrupos.value.length;
        
        // Usar la base de municipios correcta
        const municipiosBase = municipiosDisponiblesParaFiltros.value;
        
        // Obtener los grupos válidos basados en los mecanismos detalle seleccionados
        const gruposValidos = new Set();
        municipiosBase.forEach(municipio => {
          if (selectedMecanismosDetalle.value.includes(municipio.mecanismo_detalle) && 
              municipio.grupo) {
            gruposValidos.add(municipio.grupo);
          }
        });
        
        // Filtrar los grupos seleccionados
        selectedGrupos.value = selectedGrupos.value.filter(grupo => 
          gruposValidos.has(grupo)
        );
        
        console.log(`- Grupos actualizados: ${selectedGrupos.value.length} (antes: ${gruposAnteriores})`);
      }
    };

    // 7. Actualizar las funciones existentes para mantener coherencia

    // Actualizar onDepartamentosChange para usar la base correcta y limpiar mecanismos y grupos
    const onDepartamentosChange = () => {
      console.log('🔄 onDepartamentosChange ejecutado');
      console.log('- Departamentos seleccionados:', selectedDepartamentos.value);
      
      if (selectedDepartamentos.value.length > 0) {
        const municipiosBase = municipiosDisponiblesParaFiltros.value;
        
        // Limpiar municipios que ya no aplican
        const municipiosAnteriores = selectedMunicipios.value.length;
        selectedMunicipios.value = selectedMunicipios.value.filter(codMun => {
          const municipio = municipiosBase.find(m => String(m.cod_municipio) === codMun);
          return municipio && selectedDepartamentos.value.includes(String(municipio.cod_depto));
        });
        console.log(`- Municipios actualizados: ${selectedMunicipios.value.length} (antes: ${municipiosAnteriores})`);
        
        // Limpiar territoriales que ya no aplican
        const territorialesAnteriores = selectedTerritoriales.value.length;
        
        // Obtener las territoriales válidas basadas en los departamentos seleccionados
        const territorialesValidas = new Set();
        municipiosBase.forEach(municipio => {
          if (selectedDepartamentos.value.includes(String(municipio.cod_depto)) && municipio.nom_territorial) {
            territorialesValidas.add(municipio.nom_territorial);
          }
        });
        
        // Filtrar las territoriales seleccionadas
        selectedTerritoriales.value = selectedTerritoriales.value.filter(territorial => 
          territorialesValidas.has(territorial)
        );
        
        console.log(`- Territoriales actualizadas: ${selectedTerritoriales.value.length} (antes: ${territorialesAnteriores})`);
        
        // NUEVO: Limpiar mecanismos generales que ya no aplican
        const mecanismosGeneralesAnteriores = selectedMecanismosGenerales.value.length;
        
        // Obtener los mecanismos generales válidos basados en los departamentos seleccionados
        const mecanismosGeneralesValidos = new Set();
        municipiosBase.forEach(municipio => {
          if (selectedDepartamentos.value.includes(String(municipio.cod_depto)) && municipio.mecanismo_general) {
            mecanismosGeneralesValidos.add(municipio.mecanismo_general);
          }
        });
        
        // Filtrar los mecanismos generales seleccionados
        selectedMecanismosGenerales.value = selectedMecanismosGenerales.value.filter(mecanismo => 
          mecanismosGeneralesValidos.has(mecanismo)
        );
        
        console.log(`- Mecanismos generales actualizados: ${selectedMecanismosGenerales.value.length} (antes: ${mecanismosGeneralesAnteriores})`);
        
        // NUEVO: Limpiar mecanismos detalle que ya no aplican
        const mecanismosDetalleAnteriores = selectedMecanismosDetalle.value.length;
        
        // Obtener los mecanismos detalle válidos basados en los departamentos seleccionados
        const mecanismosDetalleValidos = new Set();
        municipiosBase.forEach(municipio => {
          if (selectedDepartamentos.value.includes(String(municipio.cod_depto)) && municipio.mecanismo_detalle) {
            mecanismosDetalleValidos.add(municipio.mecanismo_detalle);
          }
        });
        
        // Filtrar los mecanismos detalle seleccionados
        selectedMecanismosDetalle.value = selectedMecanismosDetalle.value.filter(mecanismo => 
          mecanismosDetalleValidos.has(mecanismo)
        );
        
        console.log(`- Mecanismos detalle actualizados: ${selectedMecanismosDetalle.value.length} (antes: ${mecanismosDetalleAnteriores})`);
        
        // NUEVO: Limpiar grupos que ya no aplican
        const gruposAnteriores = selectedGrupos.value.length;
        
        // Obtener los grupos válidos basados en los departamentos seleccionados
        const gruposValidos = new Set();
        municipiosBase.forEach(municipio => {
          if (selectedDepartamentos.value.includes(String(municipio.cod_depto)) && municipio.grupo) {
            gruposValidos.add(municipio.grupo);
          }
        });
        
        // Filtrar los grupos seleccionados
        selectedGrupos.value = selectedGrupos.value.filter(grupo => 
          gruposValidos.has(grupo)
        );
        
        console.log(`- Grupos actualizados: ${selectedGrupos.value.length} (antes: ${gruposAnteriores})`);
      }
    };

    // Actualizar onTerritorialesChange para usar la base correcta y limpiar mecanismos y grupos
    const onTerritorialesChange = () => {
      console.log('🔄 onTerritorialesChange ejecutado');
      console.log('- Territoriales seleccionadas:', selectedTerritoriales.value);
      
      if (selectedTerritoriales.value.length > 0) {
        const municipiosBase = municipiosDisponiblesParaFiltros.value;
        
        // Limpiar municipios que ya no aplican
        const municipiosAnteriores = selectedMunicipios.value.length;
        selectedMunicipios.value = selectedMunicipios.value.filter(codMun => {
          const municipio = municipiosBase.find(m => String(m.cod_municipio) === codMun);
          return municipio && municipio.nom_territorial && 
                 selectedTerritoriales.value.includes(municipio.nom_territorial);
        });
        console.log(`- Municipios actualizados: ${selectedMunicipios.value.length} (antes: ${municipiosAnteriores})`);
        
        // NUEVO: Limpiar mecanismos generales que ya no aplican
        const mecanismosGeneralesAnteriores = selectedMecanismosGenerales.value.length;
        
        // Obtener los mecanismos generales válidos basados en las territoriales seleccionadas
        const mecanismosGeneralesValidos = new Set();
        municipiosBase.forEach(municipio => {
          if (municipio.nom_territorial && selectedTerritoriales.value.includes(municipio.nom_territorial) && 
              municipio.mecanismo_general) {
            mecanismosGeneralesValidos.add(municipio.mecanismo_general);
          }
        });
        
        // Filtrar los mecanismos generales seleccionados
        selectedMecanismosGenerales.value = selectedMecanismosGenerales.value.filter(mecanismo => 
          mecanismosGeneralesValidos.has(mecanismo)
        );
        
        console.log(`- Mecanismos generales actualizados: ${selectedMecanismosGenerales.value.length} (antes: ${mecanismosGeneralesAnteriores})`);
        
        // NUEVO: Limpiar mecanismos detalle que ya no aplican
        const mecanismosDetalleAnteriores = selectedMecanismosDetalle.value.length;
        
        // Obtener los mecanismos detalle válidos basados en las territoriales seleccionadas
        const mecanismosDetalleValidos = new Set();
        municipiosBase.forEach(municipio => {
          if (municipio.nom_territorial && selectedTerritoriales.value.includes(municipio.nom_territorial) && 
              municipio.mecanismo_detalle) {
            mecanismosDetalleValidos.add(municipio.mecanismo_detalle);
          }
        });
        
        // Filtrar los mecanismos detalle seleccionados
        selectedMecanismosDetalle.value = selectedMecanismosDetalle.value.filter(mecanismo => 
          mecanismosDetalleValidos.has(mecanismo)
        );
        
        console.log(`- Mecanismos detalle actualizados: ${selectedMecanismosDetalle.value.length} (antes: ${mecanismosDetalleAnteriores})`);
        
        // NUEVO: Limpiar grupos que ya no aplican
        const gruposAnteriores = selectedGrupos.value.length;
        
        // Obtener los grupos válidos basados en las territoriales seleccionadas
        const gruposValidos = new Set();
        municipiosBase.forEach(municipio => {
          if (municipio.nom_territorial && selectedTerritoriales.value.includes(municipio.nom_territorial) && 
              municipio.grupo) {
            gruposValidos.add(municipio.grupo);
          }
        });
        
        // Filtrar los grupos seleccionados
        selectedGrupos.value = selectedGrupos.value.filter(grupo => 
          gruposValidos.has(grupo)
        );
        
        console.log(`- Grupos actualizados: ${selectedGrupos.value.length} (antes: ${gruposAnteriores})`);
      }
    };

    // 1. NORMALIZACIÓN DE DATOS EN CARGA INICIAL
    const loadInitialData = async () => {
      try {
        loading.value = true;
        loadingMessage.value = 'Cargando datos maestros...';
        
        console.log('🔄 Iniciando carga de datos...');
        
        // Cargar todos los datos en paralelo
        const [deptosData, municipiosData, territorialesData, mecanismosGeneralesData, mecanismosDetalleData, gruposData] = 
          await Promise.allSettled([
            cargarTodosLosDatos(`${API_URL}/preoperacion/departamentos/`),
            cargarTodosLosDatos(`${API_URL}/preoperacion/municipios/`),
            cargarTodosLosDatos(`${API_URL}/preoperacion/territoriales/`),
            cargarTodosLosDatos(`${API_URL}/preoperacion/mecanismos-general/`),
            cargarTodosLosDatos(`${API_URL}/preoperacion/mecanismos-detalle/`),
            cargarTodosLosDatos(`${API_URL}/preoperacion/grupos/`)
          ]);
        
        // Procesar resultados
        departamentos.value = deptosData.status === 'fulfilled' ? deptosData.value : [];
        municipiosList.value = municipiosData.status === 'fulfilled' ? municipiosData.value : [];
        territoriales.value = territorialesData.status === 'fulfilled' ? territorialesData.value : [];
        mecanismosGenerales.value = mecanismosGeneralesData.status === 'fulfilled' ? mecanismosGeneralesData.value : [];
        mecanismosDetalle.value = mecanismosDetalleData.status === 'fulfilled' ? mecanismosDetalleData.value : [];
        grupos.value = gruposData.status === 'fulfilled' ? gruposData.value : [];
        
        // IMPORTANTE: NORMALIZACIÓN DE DATOS CRÍTICA PARA QUE LOS FILTROS FUNCIONEN
        // Asegurar que todos los campos de ID/código son strings para comparaciones consistentes
        departamentos.value = departamentos.value.map(d => ({
          ...d,
          cod_depto: String(d.cod_depto)
        }));
        
        municipiosList.value = municipiosList.value.map(m => ({
          ...m,
          cod_municipio: String(m.cod_municipio),
          cod_depto: String(m.cod_depto),
          // Asegurar que estos valores existen aunque sea como string vacío
          mecanismo_general: m.mecanismo_general || '',
          mecanismo_detalle: m.mecanismo_detalle || '',
          grupo: m.grupo || '',
          nom_territorial: m.nom_territorial || ''
        }));
        
        // Debugging
        console.log('📊 DATOS CARGADOS:');
        console.log(`- Departamentos: ${departamentos.value.length}`);
        console.log(`- Municipios: ${municipiosList.value.length}`);
        console.log(`- Territoriales: ${territoriales.value.length}`);
        console.log(`- Mecanismos Generales: ${mecanismosGenerales.value.length}`);
        console.log(`- Mecanismos Detalle: ${mecanismosDetalle.value.length}`);
        console.log(`- Grupos: ${grupos.value.length}`);
        
        // Imprimir muestra de cada uno para verificar estructura
        if (departamentos.value.length > 0) {
          console.log('📋 Ejemplo departamento:', departamentos.value[0]);
        }
        
        if (municipiosList.value.length > 0) {
          console.log('📋 Ejemplo municipio:', municipiosList.value[0]);
        }
        
        if (territoriales.value.length > 0) {
          console.log('📋 Ejemplo territorial:', territoriales.value[0]);
        }
        
        if (mecanismosGenerales.value.length > 0) {
          console.log('📋 Ejemplo mecanismo general:', mecanismosGenerales.value[0]);
        }
        
        if (mecanismosDetalle.value.length > 0) {
          console.log('📋 Ejemplo mecanismo detalle:', mecanismosDetalle.value[0]);
        }
        
        // Resetear selecciones
        selectedDepartamentos.value = [];
        selectedMunicipios.value = [];
        selectedTerritoriales.value = [];
        selectedMecanismosGenerales.value = [];
        selectedMecanismosDetalle.value = [];
        selectedGrupos.value = [];
        
      } catch (error) {
        console.error('❌ Error cargando datos:', error);
        showNotification('Error cargando datos maestros', 'error');
      } finally {
        loading.value = false;
      }
    };

    // 2. TERRITORIALES DISPONIBLES CORREGIDO
    const territorialesDisponibles = computed(() => {
      console.log('🔍 Calculando territoriales disponibles...');
      console.log('- Departamentos seleccionados:', selectedDepartamentos.value);
      
      const municipiosBase = municipiosDisponiblesParaFiltros.value;
      
      if (selectedDepartamentos.value.length === 0) {
        console.log('- Sin filtro de departamentos, obteniendo todas las territoriales de la base');
        // Extraer territoriales únicas de la base actual
        const territorialesEnBase = new Set();
        municipiosBase.forEach(municipio => {
          if (municipio.nom_territorial) {
            territorialesEnBase.add(municipio.nom_territorial);
          }
        });
        
        const resultado = territoriales.value.filter(territorial => 
          territorialesEnBase.has(territorial.nom_territorial)
        );
        console.log(`- Territoriales en base: ${resultado.length}`);
        return resultado;
      }
      
      // Crear conjunto de territoriales que tienen municipios en los departamentos seleccionados
      const territorialesEnDepartamentos = new Set();
      
      // Contar para debugging
      let conteoMunicipiosPorTerritorial = {};
      
      municipiosBase.forEach(municipio => {
        const deptoStr = String(municipio.cod_depto);
        
        // Verificar si este municipio está en un departamento seleccionado
        if (selectedDepartamentos.value.includes(deptoStr) && municipio.nom_territorial) {
          territorialesEnDepartamentos.add(municipio.nom_territorial);
          
          // Contar para debugging
          if (!conteoMunicipiosPorTerritorial[municipio.nom_territorial]) {
            conteoMunicipiosPorTerritorial[municipio.nom_territorial] = 0;
          }
          conteoMunicipiosPorTerritorial[municipio.nom_territorial]++;
        }
      });
      
      console.log('- Territoriales encontradas en departamentos seleccionados:', 
        Array.from(territorialesEnDepartamentos));
      console.log('- Conteo por territorial:', conteoMunicipiosPorTerritorial);
      
      // Filtrar las territoriales por las que encontramos
      const resultado = territoriales.value.filter(territorial => 
        territorialesEnDepartamentos.has(territorial.nom_territorial)
      );
      
      console.log(`- Resultado final: ${resultado.length} territoriales`);
      return resultado;
    });

    // 3. FILTERED MUNICIPIOS CORREGIDO
    const filteredMunicipios = computed(() => {
      console.log('🔍 Calculando municipios filtrados...');
      
      const municipiosBase = municipiosDisponiblesParaFiltros.value;
      let result = [...municipiosBase];
      console.log(`- Total inicial: ${result.length} municipios`);
      
      // Filtrar por departamentos seleccionados
      if (selectedDepartamentos.value.length > 0) {
        const antes = result.length;
        result = result.filter(m => {
          const incluido = selectedDepartamentos.value.includes(String(m.cod_depto));
          return incluido;
        });
        console.log(`- Después de filtro por departamentos: ${result.length} (antes: ${antes})`);
      }
      
      // Filtrar por territoriales seleccionadas
      if (selectedTerritoriales.value.length > 0) {
        const antes = result.length;
        result = result.filter(m => {
          const incluido = m.nom_territorial && selectedTerritoriales.value.includes(m.nom_territorial);
          return incluido;
        });
        console.log(`- Después de filtro por territoriales: ${result.length} (antes: ${antes})`);
      }
      
      // Filtrar por búsqueda
      if (searchMunicipios.value) {
        const antes = result.length;
        const search = searchMunicipios.value.toLowerCase();
        result = result.filter(m => {
          const coincideNombre = m.nom_municipio.toLowerCase().includes(search);
          const coincideCodigo = String(m.cod_municipio).includes(search);
          return coincideNombre || coincideCodigo;
        });
        console.log(`- Después de búsqueda: ${result.length} (antes: ${antes})`);
      }
      
      return result;
    });

    // 4. MUNICIPIOS FILTRADOS FINAL CORREGIDO - ACTUALIZADO PARA USAR LA BASE CORRECTA
    const municipiosFiltrados = computed(() => {
      console.log('🔍 Calculando resultado final de municipios filtrados...');
      
      // Usar filtro por códigos específicos si está activado
      if (useCodigosMunicipioFilter.value && codigosValidados.value.length > 0) {
        const municipiosBase = municipiosDisponiblesParaFiltros.value;
        const result = municipiosBase.filter(m => 
          codigosValidados.value.includes(String(m.cod_municipio))
        );
        console.log(`- Resultado por códigos específicos: ${result.length} municipios`);
        return result;
      }
      
      // Iniciar con la base correcta (búsqueda o todos)
      const municipiosBase = municipiosDisponiblesParaFiltros.value;
      let result = [...municipiosBase];
      console.log(`- Total inicial: ${result.length} municipios`);
      
      // Aplicar filtros uno por uno
      if (selectedDepartamentos.value.length > 0) {
        const antes = result.length;
        result = result.filter(m => selectedDepartamentos.value.includes(String(m.cod_depto)));
        console.log(`- Después de filtrar por departamentos: ${result.length} (antes: ${antes})`);
        
        // Si no hay resultados, podría ser un problema de formato
        if (result.length === 0 && municipiosBase.length > 0) {
          console.warn('⚠️ No hay resultados después de filtrar por departamentos. Verificando tipos:');
          console.log('  Tipo de selectedDepartamentos[0]:', typeof selectedDepartamentos.value[0]);
          console.log('  Tipo de municipio.cod_depto:', typeof municipiosBase[0].cod_depto);
        }
      }
      
      if (selectedMunicipios.value.length > 0) {
        const antes = result.length;
        result = result.filter(m => selectedMunicipios.value.includes(String(m.cod_municipio)));
        console.log(`- Después de filtrar por municipios seleccionados: ${result.length} (antes: ${antes})`);
      }
      
      if (selectedTerritoriales.value.length > 0) {
        const antes = result.length;
        result = result.filter(m => 
          m.nom_territorial && selectedTerritoriales.value.includes(m.nom_territorial)
        );
        console.log(`- Después de filtrar por territoriales: ${result.length} (antes: ${antes})`);
      }
      
      if (selectedMecanismosGenerales.value.length > 0) {
        const antes = result.length;
        result = result.filter(m => 
          m.mecanismo_general && selectedMecanismosGenerales.value.includes(m.mecanismo_general)
        );
        console.log(`- Después de filtrar por mecanismos generales: ${result.length} (antes: ${antes})`);
      }
      
      if (selectedMecanismosDetalle.value.length > 0) {
        const antes = result.length;
        result = result.filter(m => 
          m.mecanismo_detalle && selectedMecanismosDetalle.value.includes(m.mecanismo_detalle)
        );
        console.log(`- Después de filtrar por mecanismos detalle: ${result.length} (antes: ${antes})`);
      }
      
      if (selectedGrupos.value.length > 0) {
        const antes = result.length;
        result = result.filter(m => 
          m.grupo && selectedGrupos.value.includes(m.grupo)
        );
        console.log(`- Después de filtrar por grupos: ${result.length} (antes: ${antes})`);
      }
      
      console.log(`- Resultado final: ${result.length} municipios`);
      return result;
    });

    // Computed properties para filtros
    const filteredDepartamentos = computed(() => {
      console.log('🔍 Calculando departamentos filtrados...');
      if (!searchDepartamentos.value) {
        // Mostrar solo departamentos que están en la base actual
        const municipiosBase = municipiosDisponiblesParaFiltros.value;
        const deptosIds = new Set(municipiosBase.map(m => String(m.cod_depto)));
        const resultado = departamentos.value.filter(d => deptosIds.has(String(d.cod_depto)));
        console.log(`- Sin búsqueda, mostrando departamentos de la base: ${resultado.length}`);
        return resultado;
      }
      
      const search = searchDepartamentos.value.toLowerCase();
      const municipiosBase = municipiosDisponiblesParaFiltros.value;
      const deptosIds = new Set(municipiosBase.map(m => String(m.cod_depto)));
      
      const result = departamentos.value
        .filter(d => deptosIds.has(String(d.cod_depto)))
        .filter(depto => depto.nom_depto.toLowerCase().includes(search));
      
      console.log(`- Con búsqueda "${search}": ${result.length} resultados`);
      return result;
    });
    
    const filteredTerritoriales = computed(() => {
      console.log('🔍 Calculando territoriales filtradas...');
      if (!searchTerritoriales.value) {
        console.log(`- Sin búsqueda, mostrando todas disponibles: ${territorialesDisponibles.value.length}`);
        return territorialesDisponibles.value;
      }
      
      const search = searchTerritoriales.value.toLowerCase();
      const result = territorialesDisponibles.value.filter(terr => 
        terr.nom_territorial.toLowerCase().includes(search)
      );
      console.log(`- Con búsqueda "${search}": ${result.length} resultados`);
      return result;
    });
    
    // Paginación
    const totalPages = computed(() => 
      Math.ceil(municipiosFiltrados.value.length / pageSize.value)
    );
    
    const paginatedMunicipios = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value;
      const end = start + pageSize.value;
      return municipiosFiltrados.value.slice(start, end);
    });
    
    // Funciones de toggle para dropdowns
    const toggleDropdown = (dropdown) => {
      console.log(`🔍 Toggling dropdown: ${dropdown}`);
      console.log(`- Estado actual: ${dropdownStates.value[dropdown]}`);
      
      // Importante: Primero verifica si hay datos disponibles para este dropdown
      let itemsCount = 0;
      
      switch (dropdown) {
        case 'departamentos':
          itemsCount = departamentos.value.length;
          break;
        case 'municipios':
          itemsCount = filteredMunicipios.value.length;
          break;
        case 'territoriales':
          itemsCount = territorialesDisponibles.value.length;
          break;
        case 'mecanismosGenerales':
          itemsCount = mecanismosGenerales.value.length;
          break;
        case 'mecanismosDetalle':
          itemsCount = mecanismosDetalle.value.length;
          break;
        case 'grupos':
          itemsCount = grupos.value.length;
          break;
      }
      
      console.log(`- Elementos disponibles: ${itemsCount}`);
      
      if (itemsCount === 0) {
        console.warn(`⚠️ No hay elementos disponibles para el dropdown ${dropdown}`);
        showNotification(`No hay elementos disponibles para seleccionar en ${dropdown}`, 'warning');
        return;
      }
      
      // Cerrar todos los demás dropdowns
      Object.keys(dropdownStates.value).forEach(key => {
        if (key !== dropdown) {
          dropdownStates.value[key] = false;
        }
      });
      
      // Toggle el dropdown actual
      dropdownStates.value[dropdown] = !dropdownStates.value[dropdown];
      console.log(`- Nuevo estado: ${dropdownStates.value[dropdown]}`);
      
      // Forzar re-renderizado si es necesario
      if (dropdownStates.value[dropdown]) {
        nextTick(() => {
          console.log(`✅ DOM actualizado para dropdown ${dropdown}`);
        });
      }
    };
    
    // Funciones de selección masiva
    const selectAllDepartamentos = () => {
      const municipiosBase = municipiosDisponiblesParaFiltros.value;
      const deptosIds = new Set(municipiosBase.map(m => String(m.cod_depto)));
      selectedDepartamentos.value = Array.from(deptosIds);
      onDepartamentosChange();
    };
    
    const clearDepartamentos = () => {
      selectedDepartamentos.value = [];
      onDepartamentosChange();
    };
    
    const selectAllMunicipios = () => {
      selectedMunicipios.value = filteredMunicipios.value.map(m => m.cod_municipio.toString());
    };
    
    const clearMunicipios = () => {
      selectedMunicipios.value = [];
    };
    
    const selectAllTerritoriales = () => {
      selectedTerritoriales.value = territoriales.value.map(t => t.nom_territorial);
      onTerritorialesChange();
    };
    
    const clearTerritoriales = () => {
      selectedTerritoriales.value = [];
      onTerritorialesChange();
    };
        
    // Manejo del filtro especial por códigos
    const onCodigosFilterToggle = () => {
      if (!useCodigosMunicipioFilter.value) {
        // Limpiar datos del filtro especial
        codigosManuales.value = '';
        codigosValidados.value = [];
        codigosInvalidos.value = [];
        archivoSeleccionado.value = null;
      }
    };
    
    const onCodigosManualesChange = () => {
      if (!codigosManuales.value.trim()) {
        codigosValidados.value = [];
        codigosInvalidos.value = [];
        return;
      }
      
      // Extraer códigos del texto
      const codigos = codigosManuales.value
        .split(/[,\s\n]+/)
        .map(c => c.trim())
        .filter(c => c.length > 0);
      
      // Validar códigos contra la lista de municipios (usar la base correcta)
      const municipiosBase = municipiosDisponiblesParaFiltros.value;
      const validos = [];
      const invalidos = [];
      
      codigos.forEach(codigo => {
        const municipio = municipiosBase.find(m => 
          m.cod_municipio.toString() === codigo
        );
        
        if (municipio) {
          validos.push(codigo);
        } else {
          invalidos.push(codigo);
        }
      });
      
      codigosValidados.value = validos;
      codigosInvalidos.value = invalidos;
    };
    
    // Manejo de archivos
    const handleFileSelect = (event: Event) => {
      const target = event.target as HTMLInputElement;
      if (target.files && target.files.length > 0) {
        processFile(target.files[0]);
      }
    };
    
    const handleFileDrop = (event: DragEvent) => {
      if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
        processFile(event.dataTransfer.files[0]);
      }
    };
    
    const processFile = async (file: File) => {
      archivoSeleccionado.value = file;
      
      try {
        loading.value = true;
        loadingMessage.value = 'Procesando archivo...';
        
        const codigos = await extractCodigosFromFile(file);
        
        // Validar códigos extraídos (usar la base correcta)
        const municipiosBase = municipiosDisponiblesParaFiltros.value;
        const validos = [];
        const invalidos = [];
        
        codigos.forEach(codigo => {
          const municipio = municipiosBase.find(m => 
            m.cod_municipio.toString() === codigo
          );
          
          if (municipio) {
            validos.push(codigo);
          } else {
            invalidos.push(codigo);
          }
        });
        
        codigosValidados.value = validos;
        codigosInvalidos.value = invalidos;
        
        showNotification(
          `Archivo procesado: ${validos.length} códigos válidos encontrados`,
          'success'
        );
        
      } catch (error) {
        console.error('Error procesando archivo:', error);
        showNotification('Error procesando el archivo', 'error');
        removeFile();
      } finally {
        loading.value = false;
      }
    };
    
    const extractCodigosFromFile = async (file: File): Promise<string[]> => {
      const extension = file.name.split('.').pop()?.toLowerCase();
      
      switch (extension) {
        case 'xlsx':
        case 'xls':
          return await extractFromExcel(file);
        case 'csv':
          return await extractFromCSV(file);
        case 'txt':
          return await extractFromTXT(file);
        default:
          throw new Error('Formato de archivo no soportado');
      }
    };
    
    const extractFromExcel = async (file: File): Promise<string[]> => {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data);
      const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
      const jsonData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 });
      
      const codigos = [];
      for (const row of jsonData as any[][]) {
        if (row[0] && typeof row[0] === 'number') {
          codigos.push(row[0].toString());
        } else if (row[0] && typeof row[0] === 'string' && /^\d+$/.test(row[0])) {
          codigos.push(row[0]);
        }
      }
      
      return codigos;
    };
    
    const extractFromCSV = async (file: File): Promise<string[]> => {
      const text = await file.text();
      const lines = text.split(/\r?\n/);
      const codigos = [];
      
      for (const line of lines) {
        const values = line.split(/[,;]/);
        for (const value of values) {
          const cleaned = value.trim().replace(/"/g, '');
          if (/^\d+$/.test(cleaned)) {
            codigos.push(cleaned);
          }
        }
      }
      
      return codigos;
    };
    
    const extractFromTXT = async (file: File): Promise<string[]> => {
      const text = await file.text();
      const codigos = text
        .split(/[,\s\n]+/)
        .map(c => c.trim())
        .filter(c => /^\d+$/.test(c));
      
      return codigos;
    };
    
    const removeFile = () => {
      archivoSeleccionado.value = null;
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) {
        fileInput.value = '';
      }
    };
    
    // Funciones de utilidad
    const getNombreDepartamento = (codDepto: number | string): string => {
      const depto = departamentos.value.find(d => d.cod_depto.toString() === codDepto.toString());
      return depto ? depto.nom_depto : 'N/A';
    };
    
    const getInsumoCount = (municipioId: number): number => {
      // Esta función debería hacer una llamada al API para obtener el conteo real
      // Por ahora retornamos un valor placeholder
      return Math.floor(Math.random() * 20) + 1;
    };
    
    // Funciones principales
    const aplicarFiltros = () => {
      currentPage.value = 1;
      showNotification(
        `Filtros aplicados: ${municipiosFiltrados.value.length} municipios encontrados`,
        'success'
      );
    };
    
    const clearAllFilters = () => {
      selectedDepartamentos.value = [];
      selectedMunicipios.value = [];
      selectedTerritoriales.value = [];
      selectedMecanismosGenerales.value = [];
      selectedMecanismosDetalle.value = [];
      selectedGrupos.value = [];
      useCodigosMunicipioFilter.value = false;
      codigosManuales.value = '';
      codigosValidados.value = [];
      codigosInvalidos.value = [];
      archivoSeleccionado.value = null;
      currentPage.value = 1;
      
      // 🆕 IMPORTANTE: También limpiar la búsqueda de municipios
      limpiarBusquedaMunicipios();
      
      // Cerrar todos los dropdowns
      Object.keys(dropdownStates.value).forEach(key => {
        dropdownStates.value[key] = false;
      });
    };
    
    const generarReportes = async () => {
      if (municipiosFiltrados.value.length === 0) {
        showNotification('No hay municipios seleccionados', 'warning');
        return;
      }
      
      try {
        loading.value = true;
        loadingMessage.value = 'Generando reportes...';
        
        const municipioCodes = municipiosFiltrados.value.map(m => m.cod_municipio);
        
        const reportOptions = {
          municipios: municipioCodes,
          generar_individuales: generarReportesIndividuales.value,
          generar_resumen: generarReporteResumen.value
        };
        
          const response = await fetch(`${API_URL}/preoperacion/generar-reportes/`, {
          method: 'POST',
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(reportOptions)
        });
        
        if (!response.ok) {
          throw new Error('Error generando reportes');
        }
        
        // Descargar el archivo ZIP
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `reportes_preoperacion_${new Date().toISOString().split('T')[0]}.zip`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        showNotification('Reportes generados y descargados exitosamente', 'success');
        
      } catch (error) {
        console.error('Error generando reportes:', error);
        showNotification('Error al generar reportes', 'error');
      } finally {
        loading.value = false;
      }
    };
    
    const exportarFiltros = () => {
      const filtros = {
        selectedDepartamentos: selectedDepartamentos.value,
        selectedMunicipios: selectedMunicipios.value,
        selectedTerritoriales: selectedTerritoriales.value,
        selectedMecanismosGenerales: selectedMecanismosGenerales.value,
        selectedMecanismosDetalle: selectedMecanismosDetalle.value,
        selectedGrupos: selectedGrupos.value,
        useCodigosMunicipioFilter: useCodigosMunicipioFilter.value,
        codigosManuales: codigosManuales.value,
        // 🆕 NUEVO: Incluir búsqueda de municipios en la exportación
        busquedaMunicipios: busquedaMunicipios.value
      };
      
      const dataStr = JSON.stringify(filtros, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `filtros_preoperacion_${new Date().toISOString().split('T')[0]}.json`;
      link.click();
      URL.revokeObjectURL(url);
      
      showNotification('Filtros exportados exitosamente', 'success');
    };
    
    const importarFiltros = () => {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = '.json';
      input.onchange = async (e) => {
        const file = (e.target as HTMLInputElement).files?.[0];
        if (file) {
          try {
            const text = await file.text();
            const filtros = JSON.parse(text);
            
            selectedDepartamentos.value = filtros.selectedDepartamentos || [];
            selectedMunicipios.value = filtros.selectedMunicipios || [];
            selectedTerritoriales.value = filtros.selectedTerritoriales || [];
            selectedMecanismosGenerales.value = filtros.selectedMecanismosGenerales || [];
            selectedMecanismosDetalle.value = filtros.selectedMecanismosDetalle || [];
            selectedGrupos.value = filtros.selectedGrupos || [];
            useCodigosMunicipioFilter.value = filtros.useCodigosMunicipioFilter || false;
            codigosManuales.value = filtros.codigosManuales || '';
            
            // 🆕 NUEVO: Importar búsqueda de municipios
            if (filtros.busquedaMunicipios) {
              busquedaMunicipios.value = filtros.busquedaMunicipios;
              await realizarBusquedaMunicipios();
            }
            
            if (codigosManuales.value) {
              onCodigosManualesChange();
            }
            
            showNotification('Filtros importados exitosamente', 'success');
          } catch (error) {
            showNotification('Error al importar filtros', 'error');
          }
        }
      };
      input.click();
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
    
    // Cerrar dropdowns al hacer clic fuera
    const closeDropdowns = (event) => {
      const target = event.target;
      if (!target.closest('.multi-select-container')) {
        console.log('🔍 Cerrando todos los dropdowns (clic fuera)');
        Object.keys(dropdownStates.value).forEach(key => {
          dropdownStates.value[key] = false;
        });
      }
    };

    const selectAllMecanismosGenerales = () => {
      console.log('🔄 Seleccionando todos los mecanismos generales disponibles');
      selectedMecanismosGenerales.value = mecanismosGeneralesDisponibles.value.map(m => m.cod_mecanismo);
      console.log(`- Seleccionados: ${selectedMecanismosGenerales.value.length}`);
      onMecanismosGeneralesChange();
    };

    const clearMecanismosGenerales = () => {
      console.log('🔄 Limpiando selección de mecanismos generales');
      selectedMecanismosGenerales.value = [];
      onMecanismosGeneralesChange();
    };

    // Funciones de selección masiva para mecanismos detalle
    const selectAllMecanismosDetalle = () => {
      console.log('🔄 Seleccionando todos los mecanismos detalle disponibles');
      selectedMecanismosDetalle.value = mecanismosDetalleDisponibles.value.map(m => m.cod_mecanismo_detalle);
      console.log(`- Seleccionados: ${selectedMecanismosDetalle.value.length}`);
      onMecanismosDetalleChange();
    };

    const clearMecanismosDetalle = () => {
      console.log('🔄 Limpiando selección de mecanismos detalle');
      selectedMecanismosDetalle.value = [];
      onMecanismosDetalleChange();
    };

    // Funciones de selección masiva para grupos
    const selectAllGrupos = () => {
      console.log('🔄 Seleccionando todos los grupos disponibles');
      selectedGrupos.value = gruposDisponibles.value.map(g => g.cod_grupo);
      console.log(`- Seleccionados: ${selectedGrupos.value.length}`);
    };

    const clearGrupos = () => {
      console.log('🔄 Limpiando selección de grupos');
      selectedGrupos.value = [];
    };

    // Asegúrate de agregar este event listener en el ciclo de vida del componente
    onMounted(() => {
      loadInitialData();
      document.addEventListener('click', closeDropdowns);
    });

    onBeforeUnmount(() => {
      document.removeEventListener('click', closeDropdowns);
    });
    
    // Watchers
    watch([selectedDepartamentos, selectedTerritoriales], () => {
      currentPage.value = 1;
    });
    
    // 🆕 NUEVO WATCHER: Actualizar filtros cuando cambie la búsqueda
    watch(busquedaMunicipios, (newValue, oldValue) => {
      if (newValue !== oldValue) {
        currentPage.value = 1;
        
        // Si se limpió la búsqueda, reset algunas selecciones que podrían no ser válidas
        if (!newValue.trim() && oldValue && oldValue.trim()) {
          console.log('🧹 Búsqueda limpiada, verificando selecciones...');
          
          // Opcional: Limpiar selecciones que podrían no ser válidas ahora
          // (Esto depende del comportamiento deseado)
        }
      }
    });
    
    return {
      loading,
      loadingMessage,
      departamentos,
      municipiosList,
      territoriales,
      mecanismosGenerales,
      grupos,
      selectedDepartamentos,
      selectedMunicipios,
      selectedTerritoriales,
      selectedMecanismosGenerales,
      selectedGrupos,
      dropdownStates,
      searchDepartamentos,
      searchMunicipios,
      searchTerritoriales,
      useCodigosMunicipioFilter,
      codigosManuales,
      codigosValidados,
      codigosInvalidos,
      archivoSeleccionado,
      generarReportesIndividuales,
      generarReporteResumen,
      currentPage,
      pageSize,
      notification,
      filteredDepartamentos,
      filteredMunicipios,
      filteredTerritoriales,
      municipiosFiltrados,
      totalPages,
      paginatedMunicipios,
      toggleDropdown,
      selectAllDepartamentos,
      clearDepartamentos,
      selectAllMunicipios,
      clearMunicipios,
      selectAllTerritoriales,
      clearTerritoriales,
      selectAllMecanismosGenerales,
      clearMecanismosGenerales,
      selectAllGrupos,
      clearGrupos,
      onDepartamentosChange,
      onTerritorialesChange,
      onCodigosFilterToggle,
      onCodigosManualesChange,
      handleFileSelect,
      handleFileDrop,
      removeFile,
      getNombreDepartamento,
      getInsumoCount,
      aplicarFiltros,
      clearAllFilters,
      generarReportes,
      exportarFiltros,
      importarFiltros,
      showNotification,
      closeNotification,
      mecanismosDetalle,
      selectedMecanismosDetalle,
      searchMecanismosDetalle,
      filteredMecanismosDetalle,
      selectAllMecanismosDetalle,
      clearMecanismosDetalle,
      territorialesDisponibles,
      mecanismosGeneralesDisponibles,
      mecanismosDetalleDisponibles,
      gruposDisponibles,
      searchMecanismosGenerales,
      searchGrupos,
      filteredMecanismosGenerales,
      filteredGrupos,
      onMecanismosGeneralesChange,
      onMecanismosDetalleChange,
      
      // 🆕 NUEVAS PROPIEDADES PARA BÚSQUEDA DE MUNICIPIOS
      busquedaMunicipios,
      municipiosBusqueda,
      buscandoMunicipios,
      busquedaInmediataMunicipios,
      limpiarBusquedaMunicipios,
      realizarBusquedaMunicipios,
      municipiosDisponiblesParaFiltros,
    };
  }
});

</script>



<style scoped>
.reportes-preoperacion-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding-bottom: 2rem;
}

/* Cabecera */
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

/* Panel de filtros */
.filters-panel {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.filters-container {
  padding: 2rem;
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e9ecef;
}

.filters-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #343a40;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filters-mode-indicator {
  font-size: 0.9rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
}

.mode-search {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.mode-normal {
  background: linear-gradient(135deg, #6c757d, #495057);
  color: white;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* 🆕 BÚSQUEDA RÁPIDA INTEGRADA */
.quick-search-section {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border: 2px solid #dee2e6;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}

.quick-search-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea, #764ba2);
}

.quick-search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.search-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.search-title h4 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #495057;
}

.search-title i {
  font-size: 1.25rem;
  color: #667eea;
}

.search-info {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.search-results-count {
  color: white;
}

.search-input-container {
  position: relative;
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.search-icon {
  position: absolute;
  left: 1.25rem;
  color: #667eea;
  z-index: 2;
  font-size: 1.2rem;
}

.search-input {
  width: 100%;
  padding: 1rem 1.25rem 1rem 3.25rem;
  font-size: 0.95rem;
  line-height: 1.5;
  color: #495057;
  background-color: white;
  border: 2px solid #dee2e6;
  border-radius: 25px;
  transition: all 0.3s ease;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.search-input:focus {
  border-color: #667eea;
  outline: 0;
  box-shadow: 0 0 0 0.25rem rgba(102, 126, 234, 0.15), inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.search-input::placeholder {
  color: #6c757d;
  font-style: italic;
}

.clear-search-btn {
  position: absolute;
  right: 0.75rem;
  background: rgba(220, 53, 69, 0.1);
  border: 1px solid rgba(220, 53, 69, 0.3);
  color: #dc3545;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  width: 32px;
  height: 32px;
}

.clear-search-btn:hover {
  background: rgba(220, 53, 69, 0.2);
  border-color: rgba(220, 53, 69, 0.5);
  transform: scale(1.1);
}

.search-active-indicator {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  padding: 0.75rem 1rem;
}

.search-mode-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #495057;
  font-weight: 500;
}

.search-mode-badge i {
  color: #28a745;
  font-size: 1.1rem;
}

.search-term {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-weight: 600;
  font-style: italic;
  margin-left: 0.5rem;
}

.btn-clear-search {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(220, 53, 69, 0.1);
  border: 1px solid rgba(220, 53, 69, 0.3);
  color: #dc3545;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.85rem;
  font-weight: 500;
}

.btn-clear-search:hover {
  background: rgba(220, 53, 69, 0.2);
  border-color: rgba(220, 53, 69, 0.5);
  transform: translateY(-1px);
}

/* Filtros principales */
.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.95rem;
  color: #495057;
  font-weight: 600;
}

/* Multi-select containers */
.multi-select-container {
  position: relative;
}

.selected-items {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
  min-height: 48px;
}

.selected-items:hover {
  border-color: #adb5bd;
}

.selected-items:focus,
.selected-items:focus-within {
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
  outline: none;
}

.placeholder {
  color: #6c757d;
  font-style: italic;
}

.selection-summary {
  color: #0d6efd;
  font-weight: 500;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 2px solid #e9ecef;
  border-top: none;
  border-radius: 0 0 6px 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-height: 300px;
  overflow: hidden;
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.dropdown-search {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e9ecef;
}

.dropdown-search input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.9rem;
}

.dropdown-items {
  max-height: 200px;
  overflow-y: auto;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 0.95rem;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
}

.dropdown-item input[type="checkbox"] {
  margin: 0;
  cursor: pointer;
}

/* Filtro especial */
.special-filter-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid #e9ecef;
}

.section-toggle {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.4s;
  border-radius: 34px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: #0d6efd;
}

input:checked + .toggle-slider:before {
  transform: translateX(26px);
}

.toggle-label {
  font-size: 1.1rem;
  font-weight: 600;
  color: #343a40;
}

.codigo-filter-content {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  border: 2px solid #e9ecef;
}

.input-methods {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.input-method {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.input-method h4 {
  margin: 0 0 0.75rem;
  font-size: 1.1rem;
  color: #343a40;
}

.method-description {
  margin: 0 0 1rem;
  color: #6c757d;
  font-size: 0.9rem;
  line-height: 1.4;
}

.format-examples {
  margin: 0.5rem 0 1rem;
  padding-left: 1.5rem;
  color: #6c757d;
  font-size: 0.85rem;
}

.format-examples li {
  margin-bottom: 0.25rem;
}

.input-method textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  resize: vertical;
  font-family: monospace;
  font-size: 0.9rem;
}

.validation-info {
  margin-top: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.valid-codes {
  color: #28a745;
  font-size: 0.85rem;
  font-weight: 500;
}

.invalid-codes {
  color: #dc3545;
  font-size: 0.85rem;
  font-weight: 500;
}

/* File upload */
.file-upload-area {
  border: 2px dashed #ced4da;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background-color 0.2s;
}

.file-upload-area:hover {
  border-color: #0d6efd;
  background-color: rgba(13, 110, 253, 0.05);
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.upload-content i {
  font-size: 3rem;
  color: #6c757d;
}

.upload-content p {
  margin: 0;
  color: #495057;
}

.file-types {
  font-size: 0.85rem;
  color: #6c757d;
}

.file-selected {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: #e3f2fd;
  border-radius: 4px;
  border: 1px solid #bbdefb;
}

.btn-remove {
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 0.25rem;
  border-radius: 50%;
  margin-left: auto;
}

.btn-remove:hover {
  background-color: rgba(220, 53, 69, 0.1);
}

/* Acciones de filtros */
.filter-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid #e9ecef;
}

/* Sección de resultados */
.results-section {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.results-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #343a40;
}

.generation-options {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.report-types {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  color: #495057;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  margin: 0;
  cursor: pointer;
}

/* Vista previa de municipios */
.municipalities-preview {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  border: 1px solid #e9ecef;
}

.preview-table-container {
  overflow-x: auto;
  margin-bottom: 1rem;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.preview-table th {
  background-color: #343a40;
  color: white;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.9rem;
}

.preview-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e9ecef;
  font-size: 0.9rem;
}

.preview-table tbody tr:hover {
  background-color: #f8f9fa;
}

.text-center {
  text-align: center;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 4px;
  text-transform: uppercase;
}

.status-badge.active {
  background-color: #28a745;
  color: white;
}

.status-badge.inactive {
  background-color: #6c757d;
  color: white;
}

.badge {
  display: inline-block;
  padding: 0.35em 0.65em;
  font-size: 0.75em;
  font-weight: 700;
  line-height: 1;
  text-align: center;
  white-space: nowrap;
  vertical-align: baseline;
  border-radius: 0.375rem;
}

.badge-info {
  background-color: #0dcaf0;
  color: #000;
}

/* Paginación */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
}

.pagination-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 1px solid #dee2e6;
  background-color: white;
  color: #495057;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #e9ecef;
  border-color: #adb5bd;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.95rem;
  color: #495057;
}

/* Botones */
.btn-primary,
.btn-secondary,
.btn-success,
.btn-outline,
.btn-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border: none;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
}

.btn-primary {
  background-color: #0d6efd;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0b5ed7;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
  transform: translateY(-1px);
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #218838;
  transform: translateY(-1px);
}

.btn-success:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
  transform: none;
}

.btn-outline {
  background-color: transparent;
  border: 2px solid #ced4da;
  color: #495057;
}

.btn-outline:hover {
  background-color: #f8f9fa;
  border-color: #adb5bd;
  transform: translateY(-1px);
}

.btn-text {
  background: none;
  color: #0d6efd;
  padding: 0.25rem 0.5rem;
  font-size: 0.85rem;
}

.btn-text:hover {
  background-color: rgba(13, 110, 253, 0.1);
}

/* Loading overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #0d6efd;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Notificación */
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
@media (max-width: 1200px) {
  .filters-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
  
  .input-methods {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .header-actions { 
    width: 100%;
    justify-content: flex-end;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .results-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .generation-options {
    width: 100%;
    justify-content: space-between;
  }
  
  .notification {
    min-width: auto;
    max-width: 90%;
    left: 5%;
    right: 5%;
  }
  
  .preview-table {
    font-size: 0.8rem;
  }
  
  .preview-table th,
  .preview-table td {
    padding: 0.5rem;
  }

  /* Responsive para búsqueda integrada */
  .quick-search-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .search-active-indicator {
    flex-direction: column;
    gap: 1rem;
  }

  .filters-mode-indicator {
    text-align: center;
  }

  .filters-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
}

@media (max-width: 576px) {
  .dropdown-menu {
    position: fixed;
    top: 50%;
    left: 5%;
    right: 5%;
    transform: translateY(-50%);
    max-height: 70vh;
  }
  
  .file-upload-area {
    padding: 1rem;
  }
  
  .upload-content i {
    font-size: 2rem;
  }

  .quick-search-section {
    padding: 1rem;
  }

  .search-title h4 {
    font-size: 1rem;
  }
}
</style>