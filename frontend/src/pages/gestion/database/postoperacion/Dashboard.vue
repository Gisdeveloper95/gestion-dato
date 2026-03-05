<template>
  <div class="postoperacion-dashboard">
    <!-- Header -->
    <header class="page-header">
      <div class="header-content">
        <h1>Dashboard Post-operación</h1>
        <div class="header-stats">
          <div class="stat-badge">
            <i class="material-icons">location_city</i>
            <span>{{ contadorResultados.filtrados }} de {{ contadorResultados.total }} municipios</span>
          </div>
          <div v-if="hayFiltrosActivos" class="stat-badge">
            <i class="material-icons">filter_list</i>
            <span>{{ filtrosActivos.length }} filtros activos</span>
          </div>
        </div>
        <div class="header-actions">
          <button @click="refreshData" class="btn-export" :disabled="loading">
            <i class="material-icons">refresh</i>
            Actualizar
          </button>
          
          <!-- 🆕 NUEVOS BOTONES CSV POST-OPERACIÓN -->
          <button @click="descargarCSVRutas" class="btn-csv-rutas" :disabled="loading || municipiosList.length === 0">
            <i class="material-icons">download</i>
            CSV Rutas
          </button>
          
          <button @click="descargarCSVArchivos" class="btn-csv-archivos" :disabled="loading || municipiosList.length === 0">
            <i class="material-icons">file_download</i>
            CSV Archivos
          </button>
        </div>
      </div>
    </header>

    <!-- Filtros -->
    <section class="filters-section">
      <div class="search-container">
        <div class="search-box">
          <i class="material-icons">search</i>
          <input 
            v-model="searchTerm"
            placeholder="Buscar municipio, código, departamento..."
            @input="handleSearchInput"
          />
          <button v-if="searchTerm" @click="clearSearch" class="clear-btn">
            <i class="material-icons">close</i>
          </button>
        </div>
      </div>

      <div class="filters-grid">
        <!-- Filtro Departamento -->
        <div class="filter-container">
          <label class="filter-label">Departamento</label>
          <select v-model="filters.departamento" @change="handleDepartamentoChange">
            <option value="">Todos los departamentos ({{ departamentosDisponibles.length }})</option>
            <option 
              v-for="dpto in departamentosDisponibles" 
              :key="dpto.cod_depto" 
              :value="dpto.cod_depto"
            >
              {{ dpto.nom_depto }} ({{ contarMunicipiosPorDepto(dpto.cod_depto) }})
            </option>
          </select>
        </div>

        <!-- Filtro Municipio -->
        <div class="filter-container">
          <label class="filter-label">Municipio</label>
          <select v-model="filters.municipio" @change="handleMunicipioChange" :disabled="!filters.departamento">
            <option value="">
              {{ filters.departamento ? `Todos del departamento (${municipiosDisponibles.length})` : 'Selecciona departamento primero' }}
            </option>
            <option 
              v-for="municipio in municipiosDisponibles" 
              :key="municipio.cod_municipio" 
              :value="municipio.cod_municipio"
            >
              {{ municipio.nom_municipio }}
            </option>
          </select>
        </div>

        <!-- Acciones de filtros -->
        <div class="filter-actions">
          <button @click="clearAllFilters" class="btn-clear" :disabled="!hayFiltrosActivos">
            <i class="material-icons">clear_all</i>
            Limpiar Filtros
          </button>
        </div>
      </div>

      <!-- Tags de filtros activos -->
      <div v-if="hayFiltrosActivos" class="active-filters">
        <h4><i class="material-icons">filter_list</i> Filtros activos:</h4>
        <div class="filter-tags">
          <div v-if="searchTerm" class="filter-tag search">
            <span class="filter-type">Búsqueda:</span>
            <span class="filter-value">"{{ searchTerm }}"</span>
            <button @click="clearSearch" class="filter-remove">
              <i class="material-icons">close</i>
            </button>
          </div>
          <div v-if="filters.departamento" class="filter-tag department">
            <span class="filter-type">Departamento:</span>
            <span class="filter-value">{{ obtenerNombreFiltro('departamento', filters.departamento) }}</span>
            <button @click="limpiarFiltroEspecifico('departamento')" class="filter-remove">
              <i class="material-icons">close</i>
            </button>
          </div>
          <div v-if="filters.municipio" class="filter-tag municipio">
            <span class="filter-type">Municipio:</span>
            <span class="filter-value">{{ obtenerNombreFiltro('municipio', filters.municipio) }}</span>
            <button @click="limpiarFiltroEspecifico('municipio')" class="filter-remove">
              <i class="material-icons">close</i>
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Tabla de Municipios -->
    <section class="table-section">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando municipios...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <i class="material-icons">error</i>
        <h3>Error al cargar los datos</h3>
        <p>{{ error }}</p>
        <button @click="loadInitialData" class="btn-retry">
          <i class="material-icons">refresh</i>
          Reintentar
        </button>
      </div>

      <div v-else-if="paginatedMunicipios.length === 0" class="empty-state">
        <i class="material-icons">location_off</i>
        <h3>No se encontraron municipios</h3>
        <p v-if="hayFiltrosActivos">No hay municipios con los filtros aplicados.</p>
        <p v-else>No hay municipios disponibles.</p>
      </div>

      <div v-else class="table-container">
        <table class="municipios-table">
          <thead>
            <tr>
              <th>Código</th>
              <th>Municipio</th>
              <th>Departamento</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="municipio in paginatedMunicipios" :key="municipio.cod_municipio" class="municipio-row">
              <td class="codigo-col">
                <span class="codigo-badge">{{ municipio.cod_municipio }}</span>
              </td>
              <td class="municipio-col">
                <div class="municipio-info">
                  <span class="municipio-nombre">{{ municipio.nom_municipio }}</span>
                </div>
              </td>
              <td class="departamento-col">
                {{ getNombreDepartamento(municipio.cod_depto) }}
              </td>
              <td class="acciones-col">
                <div class="btn-group">
                  <button 
                    @click="verRutas(municipio)" 
                    class="btn-action btn-rutas"
                    title="Ver/Editar Rutas Post-operativas"
                  >
                    <i class="material-icons">folder_open</i>
                    Rutas
                  </button>
                  <button 
                    @click="verArchivos(municipio)" 
                    class="btn-action btn-archivos"
                    title="Ver/Gestionar Archivos Post-operación"
                  >
                    <i class="material-icons">description</i>
                    Archivos
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Paginación -->
        <div v-if="totalPages > 1" class="pagination">
          <button @click="prevPage" :disabled="currentPage <= 1" class="page-btn">
            <i class="material-icons">chevron_left</i>
          </button>
          <span class="page-info">
            Página {{ currentPage }} de {{ totalPages }}
          </span>
          <button @click="nextPage" :disabled="currentPage >= totalPages" class="page-btn">
            <i class="material-icons">chevron_right</i>
          </button>
        </div>
      </div>
    </section>

    <!-- Modal para gestionar Rutas Post-operación -->
    <div v-if="showRutasModal" class="modal-overlay" @click="closeRutasModal">
      <div class="modal-content modal-fullscreen" @click.stop>
        <div class="modal-header">
          <h3>Rutas Post-operación - {{ selectedMunicipio?.nom_municipio }}</h3>
          <button @click="closeRutasModal" class="modal-close">
            <i class="material-icons">close</i>
          </button>
        </div>
        <div class="modal-body-fullscreen">
          <!-- Botón para agregar nueva ruta -->
          <div class="section-header">
            <h4>Rutas Post-operativas del Municipio</h4>
            <button @click="agregarRuta" class="btn-primary">
              <i class="material-icons">add</i>
              Nueva Ruta
            </button>
          </div>

          <div v-if="loadingRutas" class="loading-simple">
            <div class="spinner-small"></div>
            <span>Cargando rutas del municipio {{ selectedMunicipio?.nom_municipio }}...</span>
          </div>
          
          <div v-else-if="rutasMunicipio.length === 0" class="empty-simple">
            <i class="material-icons" style="font-size: 3rem; color: #6c757d;">folder_off</i>
            <h4>No hay rutas registradas</h4>
            <p>Este municipio no tiene rutas post-operativas registradas.</p>
            <button @click="agregarRuta" class="btn-primary">
              <i class="material-icons">add</i>
              Agregar Primera Ruta
            </button>
          </div>
          
          <div v-else class="rutas-table-container-full">
            <table class="rutas-table-full">
              <thead>
                <tr>
                  <th class="id-col">ID</th>
                  <th class="ruta-col">Ruta del Directorio</th>
                  <th class="fecha-col">Fecha Creación</th>
                  <th class="acciones-col">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="ruta in rutasMunicipio" :key="ruta.id" class="ruta-row">
                  <td class="id-cell">
                    <span class="id-badge">{{ ruta.id }}</span>
                  </td>
                  <td class="path-cell-full">
                    <div class="path-display">
                      <div class="path-content" :title="ruta.path">
                        <pre class="path-text-full">{{ linuxToWindowsPath(ruta.path) || 'Sin ruta definida' }}</pre>
                      </div>
                      <div class="path-actions">
                        <button @click="copyToClipboard(ruta.path)" class="btn-copy" title="Copiar ruta">
                          <i class="material-icons">content_copy</i>
                        </button>
                      </div>
                    </div>
                  </td>
                  <td class="fecha-cell">
                    <div class="fecha-info">
                      <span class="fecha-principal">{{ formatDate(ruta.fecha_creacion) }}</span>
                      <span class="fecha-hora">{{ formatTime(ruta.fecha_creacion) }}</span>
                    </div>
                  </td>
                  <td class="acciones-cell">
                    <div class="btn-group-actions">
                      <button @click="editarRuta(ruta)" class="btn-action-table btn-edit" title="Editar ruta">
                        <i class="material-icons">edit</i>
                        <span>Editar</span>
                      </button>
                      <button @click="eliminarRuta(ruta)" class="btn-action-table btn-delete" title="Eliminar ruta">
                        <i class="material-icons">delete</i>
                        <span>Eliminar</span>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Formulario para agregar/editar ruta -->
          <div v-if="showRutaForm" class="ruta-form-fullscreen">
            <div class="form-header">
              <h4>{{ editingRuta ? 'Editar Ruta Post-operativa' : 'Nueva Ruta Post-operativa' }}</h4>
              <p class="form-subtitle">Municipio: <strong>{{ selectedMunicipio?.nom_municipio }}</strong></p>
            </div>
            <div class="form-content">
              <div class="form-group-full">
                <label for="path-input">Ruta del Directorio Post-operativo:</label>
                <textarea 
                  id="path-input"
                  v-model="rutaForm.path" 
                  class="form-control-fullscreen"
                  placeholder="Ejemplo: C:\Users\usuario\Documents\Proyectos\IGAC\Municipios\{{ selectedMunicipio?.nom_municipio }}\Postoperacion\2024\Resultados"
                  rows="4"
                  required
                ></textarea>
                <div class="form-help-full">
                  <i class="material-icons">info</i>
                  <span>Ingrese la ruta completa del directorio donde se almacenan los archivos post-operativos de este municipio. La ruta debe ser accesible desde el servidor.</span>
                </div>
              </div>
            </div>
            <div class="form-actions-full">
              <button @click="cancelarRutaForm" class="btn-cancel">
                <i class="material-icons">close</i>
                Cancelar
              </button>
              <button @click="guardarRuta" class="btn-save" :disabled="savingRuta || !rutaForm.path.trim()">
                <i v-if="savingRuta" class="material-icons spinning">refresh</i>
                <i v-else class="material-icons">{{ editingRuta ? 'update' : 'save' }}</i>
                {{ editingRuta ? 'Actualizar Ruta' : 'Guardar Ruta' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal para gestionar Archivos Post-operación -->
    <div v-if="showArchivosModal" class="modal-overlay" @click="closeArchivosModal">
      <div class="modal-content modal-fullscreen" @click.stop>
        <div class="modal-header">
          <h3>Archivos Post-operación - {{ selectedMunicipio?.nom_municipio }}</h3>
          <button @click="closeArchivosModal" class="modal-close">
            <i class="material-icons">close</i>
          </button>
        </div>
        <div class="modal-body-fullscreen">
          <!-- Filtros de archivos por COMPONENTES -->
          <div class="archivos-filters-full">
            <div class="filter-group">
              <label>Filtrar por Componente:</label>
              <select v-model="filtroComponentePost" @change="filtrarArchivos">
                <option value="">Todos los componentes</option>
                <option v-for="componente in componentesUnicosPost" :key="componente" :value="componente">
                  {{ componente }}
                </option>
              </select>
            </div>
            <div class="filter-group">
              <label>Buscar archivo:</label>
              <input 
                v-model="filtroNombreArchivoPost" 
                type="text" 
                placeholder="Nombre del archivo..."
                @input="filtrarArchivos"
              >
            </div>
            <div class="filter-stats">
              <span class="stats-badge">
                <i class="material-icons">description</i>
                {{ archivosFiltrados.length }} archivo(s) encontrado(s)
              </span>
              <button 
                @click="descargarCSVMunicipioModal" 
                class="btn-csv-modal"
                :disabled="archivosFiltrados.length === 0"
              >
                <i class="material-icons">download</i>
                CSV Municipio
              </button>
            </div>
          </div>

          <div v-if="loadingArchivos" class="loading-simple">
            <div class="spinner-small"></div>
            <span>Cargando archivos del municipio {{ selectedMunicipio?.nom_municipio }}...</span>
          </div>
          
          <div v-else-if="archivosFiltrados.length === 0" class="empty-simple">
            <i class="material-icons" style="font-size: 3rem; color: #6c757d;">description_off</i>
            <h4>No hay archivos registrados</h4>
            <p v-if="archivosMunicipio.length === 0">Este municipio no tiene archivos post-operativos registrados.</p>
            <p v-else>No se encontraron archivos con los filtros aplicados.</p>
          </div>
          
          <div v-else class="archivos-table-container-full">
            <table class="archivos-table-full">
              <thead>
                <tr>
                  <th class="nombre-col">Nombre</th>
                  <th class="componente-col">Componente</th>
                  <th class="fecha-col">Fecha</th>
                  <th class="ruta-archivo-col">Ruta del Archivo</th>
                  <th class="acciones-col">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="archivo in archivosFiltrados" :key="archivo.id_archivo" class="archivo-row">
                  <td class="nombre-cell">
                    <div class="archivo-nombre">
                      <i class="material-icons archivo-icon">description</i>
                      <span>{{ archivo.nombre_archivo || 'Sin nombre' }}</span>
                    </div>
                  </td>
                  <td class="componente-cell">
                    <span class="componente-badge">
                      {{ getComponenteNombre(archivo) }}
                    </span>
                  </td>
                  <td class="fecha-cell">
                    <div class="fecha-info">
                      <span class="fecha-principal">{{ formatDate(archivo.fecha_disposicion) }}</span>
                    </div>
                  </td>
                  <td class="ruta-archivo-cell">
                    <div class="path-display">
                      <div class="path-content">
                        <pre class="path-text-archivo">{{ linuxToWindowsPath(archivo.ruta_completa) || 'Sin ruta definida' }}</pre>
                      </div>
                      <div class="path-actions">
                        <button v-if="archivo.ruta_completa" @click="copyToClipboard(archivo.ruta_completa)" class="btn-copy" title="Copiar ruta">
                          <i class="material-icons">content_copy</i>
                        </button>
                      </div>
                    </div>
                  </td>
                  <td class="acciones-cell">
                    <div class="btn-group-actions">
                      <button @click="editarArchivo(archivo)" class="btn-action-table btn-edit" title="Editar archivo">
                        <i class="material-icons">edit</i>
                        <span>Editar</span>
                      </button>
                      <button @click="eliminarArchivo(archivo)" class="btn-action-table btn-delete" title="Eliminar archivo">
                        <i class="material-icons">delete</i>
                        <span>Eliminar</span>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Notificaciones -->
    <div v-if="notification.show" class="notification" :class="notification.type">
      <div class="notification-content">
        <i class="material-icons">{{ notification.icon }}</i>
        <span>{{ notification.message }}</span>
        <button @click="closeNotification" class="notification-close">
          <i class="material-icons">close</i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { format, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';
import { useAuthStore } from '@/store/auth';
import api from '@/api/config';
import { linuxToWindowsPath } from '@/utils/pathUtils';

const authStore = useAuthStore();

// ✅ Estados reactivos principales
const loading = ref(false);
const error = ref<string | null>(null);

// Notificaciones
const notification = ref({
  show: false,
  message: '',
  type: 'success',
  icon: 'check_circle',
  timeout: null as number | null
});

// Datos principales
const departamentos = ref<any[]>([]);
const municipiosList = ref<any[]>([]);
const componentes = ref<any[]>([]);
const cargandoCSVModal = ref(false); // ✅ Variable para estado del CSV modal

// Filtros
const searchTerm = ref('');
const filters = ref({
  departamento: '',
  municipio: ''
});

// Paginación
const currentPage = ref(1);
const pageSize = ref(20);

// Estados para modales
const showRutasModal = ref(false);
const showArchivosModal = ref(false);
const selectedMunicipio = ref<any | null>(null);

// Estados para Rutas
const rutasMunicipio = ref<any[]>([]);
const loadingRutas = ref(false);
const showRutaForm = ref(false);
const editingRuta = ref<any | null>(null);
const savingRuta = ref(false);
const rutaForm = ref({
  path: ''
});

// Estados para Archivos POST-OPERACIÓN con filtro por COMPONENTES
const archivosMunicipio = ref<any[]>([]);
const loadingArchivos = ref(false);
const filtroComponentePost = ref(''); // ✅ Filtro por COMPONENTE (no clasificación)
const filtroNombreArchivoPost = ref(''); // ✅ Filtro por nombre de archivo

// ✅ FUNCIÓN PARA OBTENER NOMBRE DEL COMPONENTE (CORREGIDA)
const getComponenteNombre = (archivo: any): string => {
  if (!archivo) return 'N/A';
  
  // Para post-operación, el endpoint ya enriquece con disposicion_info.componente
  if (archivo.disposicion_info?.componente) {
    return archivo.disposicion_info.componente;
  }
  
  // Fallback si hay relación directa con componente
  if (archivo.componente) {
    return archivo.componente;
  }
  
  return 'Sin componente';
};

// 🆕 FUNCIÓN DEBUG PARA VER ESTRUCTURA EXACTA DE ARCHIVOS POST
const debugEstructuraArchivosPost = async () => {
  try {
    console.log('🔍 === DEBUG: ESTRUCTURA DE ARCHIVOS POST ===');
    
    const response = await api.get('/postoperacion/archivos/?page=1');
    console.log('📄 ARCHIVOS POST - Respuesta completa:', response);
    
    const archivos = Array.isArray(response) ? response : (response.results || []);
    console.log('📄 ARCHIVOS POST - Total en primera página:', archivos.length);
    
    if (archivos.length > 0) {
      const primerArchivo = archivos[0];
      console.log('📄 ARCHIVOS POST - Primer archivo completo:', primerArchivo);
      console.log('📄 ARCHIVOS POST - Campos disponibles:', Object.keys(primerArchivo));
      
      // Debug específico de campos de municipio
      console.log('🏛️ CAMPOS DE MUNICIPIO:');
      console.log('- cod_municipio:', primerArchivo.cod_municipio);
      console.log('- municipio_id:', primerArchivo.municipio_id);
      console.log('- id_municipio:', primerArchivo.id_municipio);
      console.log('- municipio:', primerArchivo.municipio);
      console.log('- disposicion_info:', primerArchivo.disposicion_info);
      
      // Debug de extracción desde nombre
      if (primerArchivo.nombre_archivo) {
        const nombreMatch = primerArchivo.nombre_archivo.match(/^\d{8}_(\d{5})_/);
        console.log('📝 Extracción desde nombre:', nombreMatch);
      }
      
      // Debug de extracción desde ruta
      if (primerArchivo.ruta_completa) {
        const rutaMatch = primerArchivo.ruta_completa.match(/actualiz_catas[\\\/](\d{2})[\\\/](\d{3})[\\\/]/);
        console.log('📂 Extracción desde ruta:', rutaMatch);
      }
    }
    
    console.log('🔍 === FIN DEBUG ARCHIVOS POST ===');
    showNotification('Debug de archivos POST completado - Ver consola', 'info');
    
  } catch (error) {
    console.error('❌ Error en debug archivos POST:', error);
    showNotification('Error en debug de archivos POST', 'error');
  }
};

// ✅ COMPONENTES ÚNICOS PARA EL FILTRO (copiado de InsumosList)
const componentesUnicosPost = computed(() => {
  const componentesSet = new Set();
  archivosMunicipio.value.forEach(archivo => {
    const nombreComponente = getComponenteNombre(archivo);
    if (nombreComponente && nombreComponente !== 'N/A') {
      componentesSet.add(nombreComponente);
    }
  });
  return Array.from(componentesSet).sort();
});

// ✅ SISTEMA DE FILTROS DINÁMICOS (misma lógica que preoperación)

const municipiosBase = computed(() => {
  let result = [...municipiosList.value];
  
  // Filtrar por permisos si es profesional
  if (authStore.isProfesional) {
    result = result.filter(m => tieneAccesoAMunicipio(m.cod_municipio));
  }
  
  return result;
});

// Departamentos disponibles
const departamentosDisponibles = computed(() => {
  let municipiosParaDeptos = [...municipiosBase.value];
  
  // Aplicar filtros EXCEPTO departamento
  if (searchTerm.value.trim()) {
    const search = searchTerm.value.toLowerCase();
    municipiosParaDeptos = municipiosParaDeptos.filter(m => 
      m.nom_municipio?.toLowerCase().includes(search) ||
      m.cod_municipio?.toString().includes(search) ||
      getNombreDepartamento(m.cod_depto)?.toLowerCase().includes(search)
    );
  }
  
  if (filters.value.municipio) {
    municipiosParaDeptos = municipiosParaDeptos.filter(m => 
      m.cod_municipio?.toString() === filters.value.municipio.toString()
    );
  }
  
  // Obtener IDs de departamentos que tienen municipios disponibles
  const deptosIds = new Set(municipiosParaDeptos.map(m => m.cod_depto).filter(id => id));
  
  return departamentos.value
    .filter(d => deptosIds.has(d.cod_depto))
    .sort((a, b) => a.nom_depto.localeCompare(b.nom_depto));
});

// Municipios disponibles
const municipiosDisponibles = computed(() => {
  let municipiosParaMunicipios = [...municipiosBase.value];
  
  // Aplicar filtros EXCEPTO municipio
  if (searchTerm.value.trim()) {
    const search = searchTerm.value.toLowerCase();
    municipiosParaMunicipios = municipiosParaMunicipios.filter(m => 
      m.nom_municipio?.toLowerCase().includes(search) ||
      m.cod_municipio?.toString().includes(search) ||
      getNombreDepartamento(m.cod_depto)?.toLowerCase().includes(search)
    );
  }
  
  // AUTO-FILTRAR POR DEPARTAMENTO SELECCIONADO
  if (filters.value.departamento) {
    municipiosParaMunicipios = municipiosParaMunicipios.filter(m => 
      m.cod_depto?.toString() === filters.value.departamento.toString()
    );
  }
  
  return municipiosParaMunicipios.sort((a, b) => a.nom_municipio.localeCompare(b.nom_municipio));
});

// Resultado final filtrado
const filteredMunicipios = computed(() => {
  let resultado = [...municipiosBase.value];
  
  // Filtro por búsqueda
  if (searchTerm.value.trim()) {
    const search = searchTerm.value.toLowerCase();
    resultado = resultado.filter(m => 
      m.nom_municipio?.toLowerCase().includes(search) ||
      m.cod_municipio?.toString().includes(search) ||
      getNombreDepartamento(m.cod_depto).toLowerCase().includes(search)
    );
  }
  
  // Filtro por departamento
  if (filters.value.departamento) {
    resultado = resultado.filter(m => 
      m.cod_depto?.toString() === filters.value.departamento.toString()
    );
  }
  
  // Filtro por municipio específico
  if (filters.value.municipio) {
    resultado = resultado.filter(m => 
      m.cod_municipio?.toString() === filters.value.municipio.toString()
    );
  }
  
  return resultado.sort((a, b) => a.nom_municipio.localeCompare(b.nom_municipio));
});

// Paginación
const totalPages = computed(() => 
  Math.ceil(filteredMunicipios.value.length / pageSize.value)
);

const paginatedMunicipios = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredMunicipios.value.slice(start, end);
});

// Contadores
const contadorResultados = computed(() => {
  const total = municipiosList.value.length;
  const filtrados = filteredMunicipios.value.length;
  return {
    total,
    filtrados,
    porcentaje: total > 0 ? Math.round((filtrados / total) * 100) : 0
  };
});

const hayFiltrosActivos = computed(() => {
  return searchTerm.value || 
         Object.values(filters.value).some(f => f !== '');
});

const filtrosActivos = computed(() => {
  const activos = [];
  if (searchTerm.value) activos.push('búsqueda');
  if (filters.value.departamento) activos.push('departamento');
  if (filters.value.municipio) activos.push('municipio');
  return activos;
});

// ✅ ARCHIVOS FILTRADOS POR COMPONENTES (copiado de InsumosList.vue)
const archivosFiltrados = computed(() => {
  let result = [...archivosMunicipio.value];
  
  if (filtroComponentePost.value) {
    result = result.filter(a => {
      const nombreComponente = getComponenteNombre(a);
      return nombreComponente === filtroComponentePost.value;
    });
  }
  
  if (filtroNombreArchivoPost.value.trim()) {
    const search = filtroNombreArchivoPost.value.toLowerCase();
    result = result.filter(a => 
      a.nombre_archivo?.toLowerCase().includes(search) ||
      a.path_file?.toLowerCase().includes(search)
    );
  }
  
  return result;
});

// ✅ FUNCIONES DE UTILIDAD
const getNombreDepartamento = (codDepto: any): string => {
  if (!codDepto || !Array.isArray(departamentos.value)) return 'N/A';
  
  try {
    const depto = departamentos.value.find(d => 
      d && d.cod_depto && d.cod_depto.toString() === codDepto.toString()
    );
    return depto?.nom_depto || 'N/A';
  } catch (error) {
    console.error('Error en getNombreDepartamento:', error);
    return 'N/A';
  }
};

const contarMunicipiosPorDepto = (codDepto: any) => {
  if (!Array.isArray(municipiosList.value)) return 0;
  
  return municipiosList.value.filter(m => {
    return m.cod_depto?.toString() === codDepto.toString();
  }).length;
};

const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A';
  try {
    return format(parseISO(dateString), 'dd/MM/yyyy', { locale: es });
  } catch {
    return dateString;
  }
};

const formatTime = (dateString: string) => {
  if (!dateString) return '';
  try {
    return format(parseISO(dateString), 'HH:mm', { locale: es });
  } catch {
    return '';
  }
};

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text);
    showNotification('Ruta copiada al portapapeles', 'success');
  } catch (error) {
    console.error('Error copiando al portapapeles:', error);
    showNotification('Error al copiar la ruta', 'error');
  }
};

const tieneAccesoAMunicipio = (municipioId: number): boolean => {
  // Implementar lógica de permisos específica
  return true;
};

const obtenerNombreFiltro = (tipo: string, valor: any): string => {
  switch (tipo) {
    case 'departamento':
      const depto = departamentos.value.find(d => d.cod_depto?.toString() === valor?.toString());
      return depto ? depto.nom_depto : valor;
    case 'municipio':
      const municipio = municipiosList.value.find(m => m.cod_municipio?.toString() === valor?.toString());
      return municipio ? municipio.nom_municipio : valor;
    default:
      return valor;
  }
};

// ✅ FUNCIONES DE CARGA DE DATOS PARA POST-OPERACIÓN (ENDPOINTS CORREGIDOS)
const loadInitialData = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    departamentos.value = [];
    municipiosList.value = [];
    componentes.value = [];
    
    console.log('🔄 Cargando datos iniciales POST-OPERACIÓN (municipios/departamentos desde preoperación)...');
    
    const [
      municipiosResult,
      departamentosResult,
      componentesResult
    ] = await Promise.allSettled([
      // ✅ USAR API PRE-OPERACIÓN PARA DATOS MAESTROS (municipios y departamentos)
      api.get('/preoperacion/municipios/'),
      // ✅ USAR API PRE-OPERACIÓN PARA DATOS MAESTROS (municipios y departamentos)
      api.get('/preoperacion/departamentos/'),
      // ✅ CARGAR COMPONENTES PARA EL FILTRO DESDE POST-OPERACIÓN
      api.get('/postoperacion/componentes/')
    ]);
    
    if (municipiosResult.status === 'fulfilled') {
      const data = municipiosResult.value;
      municipiosList.value = Array.isArray(data) ? data : (Array.isArray(data.results) ? data.results : []);
      console.log(`✅ Municipios cargados: ${municipiosList.value.length}`);
    } else {
      console.error('❌ Error cargando municipios:', municipiosResult.reason);
      municipiosList.value = [];
    }
    
    if (departamentosResult.status === 'fulfilled') {
      const data = departamentosResult.value;
      departamentos.value = Array.isArray(data) ? data : (Array.isArray(data.results) ? data.results : []);
      console.log(`✅ Departamentos cargados: ${departamentos.value.length}`);
    } else {
      console.error('❌ Error cargando departamentos:', departamentosResult.reason);
      departamentos.value = [];
    }
    
    if (componentesResult.status === 'fulfilled') {
      const data = componentesResult.value;
      componentes.value = Array.isArray(data) ? data : (Array.isArray(data.results) ? data.results : []);
      console.log(`✅ Componentes cargados: ${componentes.value.length}`);
    } else {
      console.error('❌ Error cargando componentes:', componentesResult.reason);
      componentes.value = [];
    }
    
    console.log('✅ Datos POST-OPERACIÓN cargados exitosamente');
    
  } catch (err: any) {
    console.error('❌ Error loading initial data:', err);
    error.value = 'Error al cargar datos iniciales: ' + (err.message || 'Error desconocido');
  } finally {
    loading.value = false;
  }
};

// Funciones de filtros
const handleSearchInput = () => {
  currentPage.value = 1;
};

const clearSearch = () => {
  searchTerm.value = '';
  currentPage.value = 1;
};

const handleDepartamentoChange = () => {
  filters.value.municipio = '';
  currentPage.value = 1;
};

const handleMunicipioChange = () => {
  currentPage.value = 1;
};

const limpiarFiltroEspecifico = (filtro: string) => {
  (filters.value as any)[filtro] = '';
  if (filtro === 'departamento') {
    filters.value.municipio = '';
  }
  currentPage.value = 1;
};

const clearAllFilters = () => {
  searchTerm.value = '';
  filters.value = {
    departamento: '',
    municipio: ''
  };
  currentPage.value = 1;
};

// Paginación
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
  }
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
  }
};

const refreshData = () => {
  loadInitialData();
};

// ✅ FUNCIONES PARA RUTAS POST-OPERACIÓN - Mostrar tabla path_dir_post
const verRutas = async (municipio: any) => {
  selectedMunicipio.value = municipio;
  showRutasModal.value = true;
  await cargarRutasMunicipio(municipio.cod_municipio);
};

const cargarRutasMunicipio = async (codMunicipio: number) => {
  try {
    loadingRutas.value = true;
    console.log(`Cargando rutas POST para municipio: ${codMunicipio}`);
    
    // ✅ USAR ENDPOINT CORRECTO POST-OPERACIÓN para rutas
    const response = await api.get(`/postoperacion/rutas/por_municipio/?municipio_id=${codMunicipio}`);
    rutasMunicipio.value = Array.isArray(response) ? response : (Array.isArray(response.results) ? response.results : []);
    
    console.log(`✅ Rutas POST cargadas para municipio ${codMunicipio}: ${rutasMunicipio.value.length}`);
    
  } catch (error) {
    console.error('Error cargando rutas POST:', error);
    showNotification('Error al cargar rutas del municipio', 'error');
    rutasMunicipio.value = [];
  } finally {
    loadingRutas.value = false;
  }
};

const agregarRuta = () => {
  editingRuta.value = null;
  rutaForm.value = { path: '' };
  showRutaForm.value = true;
};

const editarRuta = (ruta: any) => {
  editingRuta.value = ruta;
  rutaForm.value = { path: ruta.path || '' };
  showRutaForm.value = true;
};

const cancelarRutaForm = () => {
  showRutaForm.value = false;
  editingRuta.value = null;
  rutaForm.value = { path: '' };
};

const guardarRuta = async () => {
  if (!rutaForm.value.path.trim()) {
    showNotification('La ruta es obligatoria', 'error');
    return;
  }

  try {
    savingRuta.value = true;
    
    const datos = {
      cod_municipio: selectedMunicipio.value.cod_municipio,
      path: rutaForm.value.path.trim()
    };

    if (editingRuta.value) {
      // Actualizar ruta existente
      await api.put(`/postoperacion/rutas/${editingRuta.value.id}/`, datos);
      showNotification('Ruta actualizada exitosamente', 'success');
    } else {
      // Crear nueva ruta
      await api.post('/postoperacion/rutas/', datos);
      showNotification('Ruta creada exitosamente', 'success');
    }
    
    cancelarRutaForm();
    await cargarRutasMunicipio(selectedMunicipio.value.cod_municipio);
    
  } catch (error) {
    console.error('Error guardando ruta POST:', error);
    showNotification('Error al guardar la ruta', 'error');
  } finally {
    savingRuta.value = false;
  }
};

const eliminarRuta = async (ruta: any) => {
  if (!confirm('¿Está seguro que desea eliminar esta ruta?')) return;
  
  try {
    await api.delete(`/postoperacion/rutas/${ruta.id}/`);
    showNotification('Ruta eliminada exitosamente', 'success');
    await cargarRutasMunicipio(selectedMunicipio.value.cod_municipio);
  } catch (error) {
    console.error('Error eliminando ruta POST:', error);
    showNotification('Error al eliminar la ruta', 'error');
  }
};

const closeRutasModal = () => {
  showRutasModal.value = false;
  selectedMunicipio.value = null;
  rutasMunicipio.value = [];
  cancelarRutaForm();
};

// ✅ FUNCIONES PARA ARCHIVOS POST-OPERACIÓN
const verArchivos = async (municipio: any) => {
  selectedMunicipio.value = municipio;
  showArchivosModal.value = true;
  await cargarArchivosMunicipio(municipio.cod_municipio);
};

const cargarArchivosMunicipio = async (codMunicipio: number) => {
  try {
    loadingArchivos.value = true;
    console.log(`Cargando archivos POST para municipio: ${codMunicipio}`);
    
    // ✅ USAR ENDPOINT CORRECTO POST-OPERACIÓN para archivos (ya enriquecidos con disposicion_info)
    const response = await api.get(`/postoperacion/archivos/por_municipio/?municipio_id=${codMunicipio}`);
    archivosMunicipio.value = Array.isArray(response) ? response : (Array.isArray(response.results) ? response.results : []);
    
    console.log(`✅ Archivos POST cargados para municipio ${codMunicipio}: ${archivosMunicipio.value.length}`);
    console.log('📋 Muestra de archivos:', archivosMunicipio.value.slice(0, 2)); // Debug
    
    // Debug de componentes únicos
    if (archivosMunicipio.value.length > 0) {
      const componentesDebug = archivosMunicipio.value.map(arch => ({
        archivo: arch.nombre_archivo,
        componente: getComponenteNombre(arch)
      }));
      console.log('🎯 Componentes extraídos:', componentesDebug);
    }
    
  } catch (error) {
    console.error('Error cargando archivos POST:', error);
    showNotification('Error al cargar archivos del municipio', 'error');
    archivosMunicipio.value = [];
  } finally {
    loadingArchivos.value = false;
  }
};

const filtrarArchivos = () => {
  // Los archivos se filtran automáticamente mediante computed
};

const editarArchivo = (archivo: any) => {
  console.log('Editar archivo POST:', archivo);
  showNotification('Funcionalidad de edición en desarrollo', 'info');
};

const eliminarArchivo = async (archivo: any) => {
  if (!confirm('¿Está seguro que desea eliminar este archivo?')) return;
  
  try {
    await api.delete(`/postoperacion/archivos/${archivo.id_archivo}/`);
    showNotification('Archivo eliminado exitosamente', 'success');
    await cargarArchivosMunicipio(selectedMunicipio.value.cod_municipio);
  } catch (error) {
    console.error('Error eliminando archivo POST:', error);
    showNotification('Error al eliminar el archivo', 'error');
  }
};

const closeArchivosModal = () => {
  showArchivosModal.value = false;
  selectedMunicipio.value = null;
  archivosMunicipio.value = [];
  filtroComponentePost.value = '';
  filtroNombreArchivoPost.value = '';
  console.log('🔄 Modal de archivos cerrado y filtros limpiados');
};

// Notificaciones
const showNotification = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'success') => {
  notification.value = {
    show: true,
    message,
    type,
    icon: type === 'success' ? 'check_circle' : 
          type === 'error' ? 'error' : 
          type === 'warning' ? 'warning' : 'info_outline',
    timeout: null
  };
  
  setTimeout(() => {
    notification.value.show = false;
  }, 4000);
};

const closeNotification = () => {
  notification.value.show = false;
};

// 🆕 FUNCIONES PARA GENERAR Y DESCARGAR CSV CON SOPORTE UTF-8
const generarCSVConBOM = (contenidoCSV: string): Blob => {
  // Agregar BOM (Byte Order Mark) para UTF-8 para soporte completo de caracteres latinos
  const BOM = '\uFEFF';
  const contenidoConBOM = BOM + contenidoCSV;
  
  return new Blob([contenidoConBOM], { 
    type: 'text/csv;charset=utf-8;' 
  });
};

const escaparCSV = (valor: any): string => {
  if (valor === null || valor === undefined) return '';
  
  const str = String(valor);
  
  // Si contiene comillas, comas, saltos de línea o caracteres especiales, envolver en comillas
  if (str.includes('"') || str.includes(',') || str.includes('\n') || str.includes('\r')) {
    // Escapar comillas duplicándolas
    return `"${str.replace(/"/g, '""')}"`;
  }
  
  return str;
};

const descargarArchivo = (blob: Blob, nombreArchivo: string) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = nombreArchivo;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

const formatearFechaCSV = (fecha: string): string => {
  if (!fecha) return '';
  try {
    return format(parseISO(fecha), 'dd/MM/yyyy', { locale: es });
  } catch {
    return fecha;
  }
};

// 🆕 FUNCIÓN 1: DESCARGAR CSV DE RUTAS POST-OPERACIÓN (TODAS)
const descargarCSVRutas = async () => {
  try {
    showNotification('Generando CSV de rutas post-operación...', 'info');
    
    // ✅ USAR ENDPOINT DIRECTO para todas las rutas POST
    let todasLasRutas: any[] = [];
    
    try {
      const response = await api.get('/postoperacion/rutas/');
      console.log('📁 Respuesta completa rutas POST:', response);
      
      // Manejar diferentes estructuras de respuesta
      if (Array.isArray(response)) {
        todasLasRutas = response;
      } else if (response && Array.isArray(response.results)) {
        todasLasRutas = response.results;
      } else if (response && Array.isArray(response.data)) {
        todasLasRutas = response.data;
      } else if (response) {
        todasLasRutas = [response];
      }
      
      console.log(`📊 Total rutas POST cargadas: ${todasLasRutas.length}`);
      
      if (todasLasRutas.length === 0) {
        showNotification('No se encontraron rutas para generar CSV', 'warning');
        return;
      }
    } catch (error) {
      console.error('Error cargando rutas POST completas:', error);
      showNotification(`Error al cargar rutas: ${error.message}`, 'error');
      return;
    }
    
    // Crear mapa de municipios para obtener nombres
    const municipiosMap = new Map();
    municipiosList.value.forEach(m => {
      municipiosMap.set(m.cod_municipio, {
        nombre: m.nom_municipio,
        departamento: getNombreDepartamento(m.cod_depto)
      });
    });
    
    // Preparar datos para CSV con estructura POST-OPERACIÓN
    const datosCSV = [];
    
    todasLasRutas.forEach(ruta => {
      console.log('🔍 Procesando ruta POST:', ruta);
      
      let municipioNombre = 'Sin municipio';
      let departamento = 'Sin departamento';
      
      // Estructura de rutas POST: { id, cod_municipio, municipio_nombre, path, fecha_creacion, municipio: {...} }
      if (ruta.municipio_nombre) {
        municipioNombre = ruta.municipio_nombre;
      } else if (ruta.municipio?.nom_municipio) {
        municipioNombre = ruta.municipio.nom_municipio;
      } else if (ruta.cod_municipio) {
        const municipio = municipiosMap.get(ruta.cod_municipio);
        if (municipio) {
          municipioNombre = municipio.nombre;
          departamento = municipio.departamento;
        }
      }
      
      // Obtener departamento
      if (ruta.municipio?.cod_depto) {
        departamento = getNombreDepartamento(ruta.municipio.cod_depto);
      }
      
      datosCSV.push({
        id: ruta.id || 'N/A',
        municipio: municipioNombre,
        departamento: departamento,
        ruta: ruta.path || 'N/A',
        fechaCreacion: formatearFechaCSV(ruta.fecha_creacion || ''),
        observaciones: ruta.observaciones || ''
      });
    });
    
    // Generar contenido CSV
    let contenidoCSV = 'ID,Municipio,Departamento,Ruta,Fecha Creación,Observaciones\n';
    
    datosCSV.forEach(item => {
      const fila = [
        escaparCSV(item.id),
        escaparCSV(item.municipio),
        escaparCSV(item.departamento),
        escaparCSV(item.ruta),
        escaparCSV(item.fechaCreacion),
        escaparCSV(item.observaciones)
      ].join(',');
      
      contenidoCSV += fila + '\n';
    });
    
    // Crear y descargar archivo
    const blob = generarCSVConBOM(contenidoCSV);
    const fecha = new Date().toISOString().split('T')[0];
    const nombreArchivo = `rutas_postoperacion_municipios_${fecha}.csv`;
    
    descargarArchivo(blob, nombreArchivo);
    
    showNotification(`CSV de rutas POST descargado: ${datosCSV.length} registros`, 'success');
    
  } catch (error) {
    console.error('Error generando CSV de rutas POST:', error);
    showNotification('Error al generar CSV de rutas', 'error');
  }
};

// 🆕 FUNCIÓN 2: DESCARGAR CSV DE ARCHIVOS POST-OPERACIÓN (TODOS) - CORREGIDA
const descargarCSVArchivos = async () => {
  try {
    showNotification('Generando CSV de archivos post-operación...', 'info');
    
    // ✅ CARGAR COMPONENTES PRIMERO
    let componentesCompletos: any[] = [];
    try {
      showNotification('Cargando componentes POST...', 'info');
      const responseComp = await api.get('/postoperacion/componentes/');
      componentesCompletos = Array.isArray(responseComp) ? responseComp : (Array.isArray(responseComp.results) ? responseComp.results : []);
      console.log(`📋 ${componentesCompletos.length} componentes cargados`);
    } catch (error) {
      console.warn('Error cargando componentes POST:', error);
    }
    
    // ✅ CARGAR TODAS LAS DISPOSICIONES PARA HACER EL CRUCE
    let todasLasDisposiciones: any[] = [];
    try {
      showNotification('Cargando disposiciones POST...', 'info');
      const responseDisp = await api.get('/postoperacion/disposiciones/');
      todasLasDisposiciones = Array.isArray(responseDisp) ? responseDisp : (Array.isArray(responseDisp.results) ? responseDisp.results : []);
      console.log(`📋 ${todasLasDisposiciones.length} disposiciones cargadas`);
    } catch (error) {
      console.warn('Error cargando disposiciones POST:', error);
    }
    
    // ✅ USAR ENDPOINT DIRECTO para todos los archivos POST
    let todosLosArchivos: any[] = [];
    let paginaActual = 1;
    let totalPaginas = 1;
    
    try {
      // Primera llamada para obtener info de paginación
      showNotification('Cargando página 1 de archivos POST...', 'info');
      const primeraRespuesta = await api.get('/postoperacion/archivos/?page=1');
      console.log('📄 Primera respuesta archivos POST:', primeraRespuesta);
      
      // Determinar estructura de paginación
      let archivos = [];
      let total = 0;
      
      if (Array.isArray(primeraRespuesta)) {
        // Sin paginación, todos los datos de una vez
        archivos = primeraRespuesta;
        todosLosArchivos = archivos;
        total = archivos.length;
      } else if (primeraRespuesta.results) {
        // Con paginación estilo DRF
        archivos = primeraRespuesta.results;
        total = primeraRespuesta.count || 0;
        const siguientePagina = primeraRespuesta.next;
        
        if (siguientePagina) {
          // Calcular total de páginas aproximado
          const porPagina = archivos.length;
          totalPaginas = Math.ceil(total / porPagina);
          console.log(`📊 Paginación POST detectada: ${total} registros, ~${totalPaginas} páginas`);
        }
        
        todosLosArchivos.push(...archivos);
        
        // Cargar páginas adicionales si existen
        if (siguientePagina && totalPaginas > 1) {
          for (let pagina = 2; pagina <= totalPaginas; pagina++) {
            try {
              showNotification(`Cargando página ${pagina} de ${totalPaginas}...`, 'info');
              const respuestaPagina = await api.get(`/postoperacion/archivos/?page=${pagina}`);
              
              if (respuestaPagina.results && respuestaPagina.results.length > 0) {
                todosLosArchivos.push(...respuestaPagina.results);
                console.log(`✅ Página ${pagina} POST cargada: ${respuestaPagina.results.length} archivos`);
              } else {
                console.log(`🔚 No hay más páginas POST después de ${pagina - 1}`);
                break;
              }
            } catch (errorPagina) {
              console.warn(`⚠️ Error cargando página POST ${pagina}:`, errorPagina);
              break;
            }
          }
        }
      } else {
        // Estructura desconocida
        console.warn('🤔 Estructura de respuesta POST desconocida:', primeraRespuesta);
        todosLosArchivos = [primeraRespuesta];
      }
      
      console.log(`📊 Total archivos POST cargados: ${todosLosArchivos.length} de ${total}`);
      
      if (todosLosArchivos.length === 0) {
        showNotification('No se encontraron archivos POST para generar CSV', 'warning');
        return;
      }
      
    } catch (error) {
      console.error('Error cargando archivos POST completos:', error);
      showNotification(`Error al cargar archivos POST: ${error.message}`, 'error');
      return;
    }
    
    // ✅ CREAR MAPAS PARA HACER LOS CRUCES CORRECTOS
    
    // Crear mapa de municipios
    const municipiosMap = new Map();
    municipiosList.value.forEach(m => {
      municipiosMap.set(m.cod_municipio, {
        nombre: m.nom_municipio,
        departamento: getNombreDepartamento(m.cod_depto)
      });
    });
    
    // Crear mapa de componentes: id_componente -> nombre_componente
    const componentesMap = new Map();
    componentesCompletos.forEach(c => {
      componentesMap.set(c.id_componente, c.nombre_componente || 'Sin nombre');
    });
    
    // ✅ CREAR MAPA DE DISPOSICIONES: id_disposicion -> { id_componente, cod_municipio }
    const disposicionesMap = new Map();
    todasLasDisposiciones.forEach(d => {
      disposicionesMap.set(d.id_disposicion, {
        id_componente: d.id_componente,
        cod_municipio: d.cod_municipio,
        nombre_componente: componentesMap.get(d.id_componente) || `Componente ${d.id_componente}`
      });
    });
    
    console.log(`🗺️ Mapas creados:
    - ${municipiosMap.size} municipios
    - ${componentesMap.size} componentes  
    - ${disposicionesMap.size} disposiciones`);
    
    // Preparar datos para CSV
    showNotification('Procesando datos POST para CSV...', 'info');
    const datosCSV = [];
    
    todosLosArchivos.forEach(archivo => {
      console.log('🔍 Procesando archivo POST:', {
        id_archivo: archivo.id_archivo,
        id_disposicion: archivo.id_disposicion,
        nombre_archivo: archivo.nombre_archivo
      });
      
      let municipioNombre = 'Sin municipio';
      let departamento = 'Sin departamento';
      let nombreComponente = 'N/A';
      let codigoMunicipio = null;
      
      // ✅ ESTRATEGIA PRINCIPAL: USAR id_disposicion PARA OBTENER COMPONENTE Y MUNICIPIO
      if (archivo.id_disposicion) {
        const disposicionInfo = disposicionesMap.get(archivo.id_disposicion);
        if (disposicionInfo) {
          nombreComponente = disposicionInfo.nombre_componente;
          codigoMunicipio = disposicionInfo.cod_municipio;
          console.log(`✅ Componente encontrado via disposición: ${nombreComponente} (municipio: ${codigoMunicipio})`);
        } else {
          console.warn(`⚠️ Disposición ${archivo.id_disposicion} no encontrada en mapa`);
        }
      }
      
      // ✅ ESTRATEGIAS ALTERNATIVAS PARA EXTRAER MUNICIPIO SI NO SE OBTUVO
      if (!codigoMunicipio) {
        // Método 1: Verificar campos directos del objeto
        if (archivo.cod_municipio) {
          codigoMunicipio = archivo.cod_municipio;
        } else if (archivo.municipio_id) {
          codigoMunicipio = archivo.municipio_id;
        } else if (archivo.id_municipio) {
          codigoMunicipio = archivo.id_municipio;
        }
        
        // Método 2: Extraer del nombre del archivo (patrón: YYYYMMDD_CODIGO_...)
        if (!codigoMunicipio && archivo.nombre_archivo) {
          const nombreMatch = archivo.nombre_archivo.match(/^\d{8}_(\d{5})_/);
          if (nombreMatch) {
            codigoMunicipio = parseInt(nombreMatch[1]);
            console.log(`📁 Código extraído del nombre: ${codigoMunicipio}`);
          }
        }
        
        // Método 3: Extraer de la ruta (patrón: .../XX/XXX/...)
        if (!codigoMunicipio && archivo.ruta_completa) {
          const rutaMatch = archivo.ruta_completa.match(/actualiz_catas[\\\/](\d{2})[\\\/](\d{3})[\\\/]/);
          if (rutaMatch) {
            codigoMunicipio = parseInt(rutaMatch[1] + rutaMatch[2]);
            console.log(`📂 Código extraído de la ruta: ${codigoMunicipio}`);
          }
        }
      }
      
      // Buscar información del municipio en el mapa
      if (codigoMunicipio) {
        const municipio = municipiosMap.get(codigoMunicipio);
        if (municipio) {
          municipioNombre = municipio.nombre;
          departamento = municipio.departamento;
          console.log(`✅ Municipio encontrado: ${municipioNombre} (${codigoMunicipio})`);
        } else {
          console.warn(`⚠️ Código ${codigoMunicipio} no encontrado en mapa de municipios`);
          municipioNombre = `Municipio ${codigoMunicipio}`;
        }
      }
      
      // ✅ ESTRATEGIA ALTERNATIVA PARA COMPONENTE SI NO SE OBTUVO VIA DISPOSICIÓN
      if (nombreComponente === 'N/A') {
        if (archivo.id_componente) {
          nombreComponente = componentesMap.get(archivo.id_componente) || `Componente ${archivo.id_componente}`;
          console.log(`🔄 Componente alternativo: ${nombreComponente}`);
        } else if (archivo.disposicion_info?.componente) {
          nombreComponente = archivo.disposicion_info.componente;
          console.log(`🔄 Componente desde disposicion_info: ${nombreComponente}`);
        }
      }
      
      // Calcular extensión del archivo
      let extension = 'N/A';
      if (archivo.ruta_completa) {
        const partes = archivo.ruta_completa.split('.');
        if (partes.length > 1) {
          extension = partes[partes.length - 1].toUpperCase();
        }
      } else if (archivo.nombre_archivo) {
        const partes = archivo.nombre_archivo.split('.');
        if (partes.length > 1) {
          extension = partes[partes.length - 1].toUpperCase();
        }
      }
      
      datosCSV.push({
        id: archivo.id_archivo || archivo.id || 'N/A',
        municipio: municipioNombre,
        departamento: departamento,
        nombreArchivo: archivo.nombre_archivo || 'Sin nombre',
        componente: nombreComponente,
        ruta: archivo.ruta_completa || 'N/A',
        fechaCreacion: formatearFechaCSV(archivo.fecha_disposicion || ''),
        extension: extension,
        observacion: archivo.observacion || '',
        aprobado: archivo.aprobado ? 'Sí' : 'No',
        dispuesto: archivo.dispuesto ? 'Sí' : 'No'
      });
    });
    
    // Generar contenido CSV - ✅ SIN COLUMNA DE TAMAÑO
    showNotification('Generando archivo CSV POST...', 'info');
    let contenidoCSV = 'ID,Municipio,Departamento,Nombre Archivo,Componente,Ruta,Fecha Creación,Extensión,Observación,Aprobado,Dispuesto\n';
    
    datosCSV.forEach(item => {
      const fila = [
        escaparCSV(item.id),
        escaparCSV(item.municipio),
        escaparCSV(item.departamento),
        escaparCSV(item.nombreArchivo),
        escaparCSV(item.componente),
        escaparCSV(item.ruta),
        escaparCSV(item.fechaCreacion),
        escaparCSV(item.extension),
        escaparCSV(item.observacion),
        escaparCSV(item.aprobado),
        escaparCSV(item.dispuesto)
      ].join(',');
      
      contenidoCSV += fila + '\n';
    });
    
    // Crear y descargar archivo
    const blob = generarCSVConBOM(contenidoCSV);
    const fecha = new Date().toISOString().split('T')[0];
    const nombreArchivo = `archivos_postoperacion_completo_${fecha}.csv`;
    
    descargarArchivo(blob, nombreArchivo);
    
    showNotification(`CSV de archivos POST descargado: ${datosCSV.length} registros`, 'success');
    
  } catch (error) {
    console.error('Error generando CSV de archivos POST:', error);
    showNotification('Error al generar CSV de archivos', 'error');
  }
};

// 🆕 FUNCIÓN 3: DESCARGAR CSV DEL MUNICIPIO EN EL MODAL
const descargarCSVMunicipioModal = async () => {
  if (!selectedMunicipio.value || archivosFiltrados.value.length === 0) {
    showNotification('No hay archivos para descargar', 'warning');
    return;
  }
  
  try {
    cargandoCSVModal.value = true;
    
    showNotification(`Generando CSV de ${selectedMunicipio.value.nom_municipio}...`, 'info');
    
    // Preparar datos para CSV usando los archivos ya filtrados
    const datosCSV = [];
    
    archivosFiltrados.value.forEach(archivo => {
      // 🔧 EXTRAER CÓDIGO DE MUNICIPIO CON MÚLTIPLES ESTRATEGIAS
      let codigoMunicipio = selectedMunicipio.value.cod_municipio;
      
      // Verificar si podemos obtener más información del archivo
      if (!codigoMunicipio && archivo.cod_municipio) {
        codigoMunicipio = archivo.cod_municipio;
      } else if (!codigoMunicipio && archivo.nombre_archivo) {
        // Extraer del nombre del archivo (patrón: YYYYMMDD_CODIGO_...)
        const nombreMatch = archivo.nombre_archivo.match(/^\d{8}_(\d{5})_/);
        if (nombreMatch) {
          codigoMunicipio = parseInt(nombreMatch[1]);
        }
      } else if (!codigoMunicipio && archivo.ruta_completa) {
        // Extraer de la ruta (patrón: .../XX/XXX/...)
        const rutaMatch = archivo.ruta_completa.match(/actualiz_catas[\\\/](\d{2})[\\\/](\d{3})[\\\/]/);
        if (rutaMatch) {
          codigoMunicipio = parseInt(rutaMatch[1] + rutaMatch[2]);
        }
      }
      
      // Buscar nombre de componente
      let nombreComponente = 'N/A';
      if (archivo.disposicion_info?.componente) {
        nombreComponente = archivo.disposicion_info.componente;
      }
      
      // Calcular extensión del archivo
      let extension = 'N/A';
      if (archivo.ruta_completa) {
        const partes = archivo.ruta_completa.split('.');
        if (partes.length > 1) {
          extension = partes[partes.length - 1].toUpperCase();
        }
      }
      
      datosCSV.push({
        id: archivo.id_archivo || 'N/A',
        municipio: selectedMunicipio.value.nom_municipio,
        departamento: getNombreDepartamento(selectedMunicipio.value.cod_depto),
        nombreArchivo: archivo.nombre_archivo || 'Sin nombre',
        componente: nombreComponente,
        ruta: archivo.ruta_completa || 'N/A',
        tamano: 'Ver archivo',
        fechaCreacion: formatearFechaCSV(archivo.fecha_disposicion || ''),
        extension: extension,
        observacion: archivo.observacion || '',
        aprobado: archivo.disposicion_info?.aprobado ? 'Sí' : 'No',
        dispuesto: archivo.disposicion_info?.dispuesto ? 'Sí' : 'No'
      });
    });
    
    // Generar contenido CSV
    let contenidoCSV = `ID,Municipio,Departamento,Nombre Archivo,Componente,Ruta,Tamaño,Fecha Creación,Extensión,Observación,Aprobado,Dispuesto\n`;
    
    datosCSV.forEach(item => {
      const fila = [
        escaparCSV(item.id),
        escaparCSV(item.municipio),
        escaparCSV(item.departamento),
        escaparCSV(item.nombreArchivo),
        escaparCSV(item.componente),
        escaparCSV(item.ruta),
        escaparCSV(item.tamano),
        escaparCSV(item.fechaCreacion),
        escaparCSV(item.extension),
        escaparCSV(item.observacion),
        escaparCSV(item.aprobado),
        escaparCSV(item.dispuesto)
      ].join(',');
      
      contenidoCSV += fila + '\n';
    });
    
    // Crear y descargar archivo
    const blob = generarCSVConBOM(contenidoCSV);
    const fecha = new Date().toISOString().split('T')[0];
    const nombreArchivo = `archivos_${selectedMunicipio.value.nom_municipio.replace(/\s+/g, '_')}_${fecha}.csv`;
    
    descargarArchivo(blob, nombreArchivo);
    
    showNotification(`CSV descargado: ${datosCSV.length} archivos de ${selectedMunicipio.value.nom_municipio}`, 'success');
    
  } catch (error) {
    console.error('Error generando CSV del municipio POST:', error);
    showNotification('Error al generar CSV del municipio', 'error');
  } finally {
    cargandoCSVModal.value = false;
  }
};
    
// Lifecycle
onMounted(() => {
  loadInitialData();
});

// Watchers
watch(filteredMunicipios, () => {
  if (currentPage.value > totalPages.value && totalPages.value > 0) {
    currentPage.value = totalPages.value;
  }
});

// ✅ WATCH PARA DEBUG DE COMPONENTES ÚNICOS
watch(componentesUnicosPost, (newComponents) => {
  console.log('🎯 Componentes únicos actualizados:', newComponents);
}, { immediate: true });
</script>

<style scoped>
/* ============ ESTILOS PRINCIPALES - TEMA VERDE ============ */
.postoperacion-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #48cc48 0%, #2e8b57 100%);
  padding: 1rem;
}

/* ============ HEADER ============ */
.page-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 2rem;
  color: white;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-content h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 600;
}

.header-stats {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 25px;
  font-weight: 500;
  backdrop-filter: blur(10px);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-export {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.btn-export:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.btn-export:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 🆕 ESTILOS PARA BOTONES CSV POST-OPERACIÓN */
.btn-csv-rutas,
.btn-csv-archivos {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  text-decoration: none;
}

.btn-csv-rutas {
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.8), rgba(34, 139, 34, 0.9));
}

.btn-csv-rutas:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.9), rgba(34, 139, 34, 1));
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

.btn-csv-archivos {
  background: linear-gradient(135deg, rgba(23, 162, 184, 0.8), rgba(13, 110, 253, 0.9));
}

.btn-csv-archivos:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(23, 162, 184, 0.9), rgba(13, 110, 253, 1));
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(23, 162, 184, 0.3);
}

.btn-csv-rutas:disabled,
.btn-csv-archivos:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* ============ FILTROS ============ */
.filters-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 2rem;
}

.search-container {
  margin-bottom: 1rem;
}

.search-box {
  position: relative;
  max-width: 400px;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
  font-size: 1.25rem;
}

.search-box input {
  width: 100%;
  padding: 0.875rem 1rem 0.875rem 3rem;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.search-box input:focus {
  border-color: #28a745;
  box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.1);
  outline: none;
}

.clear-btn {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.clear-btn:hover {
  background-color: rgba(108, 117, 125, 0.1);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  align-items: end;
  margin-bottom: 1rem;
}

.filter-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.25rem;
}

.filters-grid select {
  padding: 0.875rem 1rem;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  background: white;
  font-size: 1rem;
  transition: all 0.3s ease;
  color: #495057;
}

.filters-grid select:focus {
  border-color: #28a745;
  box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.1);
  outline: none;
}

.filters-grid select:disabled {
  background-color: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

.filter-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn-clear {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1rem;
  border: none;
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f8f9fa;
  color: #6c757d;
  border: 2px solid #e9ecef;
}

.btn-clear:hover:not(:disabled) {
  background: #e9ecef;
  color: #495057;
}

.btn-clear:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ============ FILTROS ACTIVOS ============ */
.active-filters {
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.active-filters h4 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 1rem 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #495057;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.filter-tag {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.filter-tag.search {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.filter-tag.department {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

.filter-tag.municipio {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.filter-type {
  font-weight: 600;
}

.filter-value {
  font-weight: 400;
}

.filter-remove {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0;
  margin-left: 0.25rem;
  font-size: 1rem;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.filter-remove:hover {
  opacity: 1;
}

/* ============ TABLA ============ */
.table-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  min-height: 400px;
}

.loading-state, .error-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
  height: 400px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-left-color: #28a745;
  border-radius: 50%;
  animation: spin 1s infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state .material-icons, .empty-state .material-icons {
  font-size: 4rem;
  color: #6c757d;
  margin-bottom: 1rem;
}

.btn-retry {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  background: #28a745;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-retry:hover {
  background: #218838;
}

.table-container {
  overflow-x: auto;
}

.municipios-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.municipios-table th {
  background: #f8f9fa;
  color: #495057;
  font-weight: 600;
  padding: 1rem 0.75rem;
  text-align: left;
  border-bottom: 2px solid #dee2e6;
  white-space: nowrap;
}

.municipios-table td {
  padding: 0.875rem 0.75rem;
  border-bottom: 1px solid #e9ecef;
  vertical-align: middle;
}

.municipio-row:hover {
  background-color: #f8f9fa;
}

.codigo-col {
  width: 100px;
}

.codigo-badge {
  display: inline-block;
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.municipio-col {
  min-width: 200px;
}

.municipio-nombre {
  font-weight: 600;
  color: #495057;
}

.departamento-col {
  min-width: 150px;
  color: #6c757d;
}

.acciones-col {
  width: 200px;
}

.btn-group {
  display: flex;
  gap: 0.5rem;
}

.btn-action {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  border: none;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-rutas {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.btn-rutas:hover {
  background: #c3e6cb;
  transform: translateY(-1px);
}

.btn-archivos {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

.btn-archivos:hover {
  background: #bee5eb;
  transform: translateY(-1px);
}

.btn-action .material-icons {
  font-size: 1rem;
}

/* ============ PAGINACIÓN ============ */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e9ecef;
}

.page-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  background: white;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  border-color: #28a745;
  color: #28a745;
  background: rgba(40, 167, 69, 0.1);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-weight: 500;
  color: #495057;
}

/* ============ MODALES ============ */
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
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.modal-fullscreen {
  width: 98vw;
  height: 95vh;
  max-width: none;
  max-height: none;
  margin: 1vh auto;
  display: flex;
  flex-direction: column;
}

.modal-body-fullscreen {
  padding: 1.5rem;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #495057;
}

.modal-close {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  color: #6c757d;
  transition: all 0.3s;
}

.modal-close:hover {
  background: #f8f9fa;
  color: #495057;
}

/* ============ RUTAS ============ */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h4 {
  margin: 0;
  font-size: 1.1rem;
  color: #495057;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary:hover {
  background: #218838;
  transform: translateY(-1px);
}

.loading-simple {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: #6c757d;
  font-style: italic;
}

.empty-simple {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  margin: 1rem 0;
}

.empty-simple i {
  margin-bottom: 1rem;
}

.empty-simple h4 {
  margin: 0 0 0.5rem 0;
  color: #495057;
  font-size: 1.2rem;
}

.empty-simple p {
  margin: 0 0 1.5rem 0;
  color: #6c757d;
  font-size: 0.95rem;
}

.spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid #e9ecef;
  border-left-color: #28a745;
  border-radius: 50%;
  animation: spin 1s infinite;
  margin-right: 0.5rem;
}

/* ============ RUTAS TABLA COMPLETA ============ */
.rutas-table-container-full {
  flex: 1;
  overflow: auto;
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.rutas-table-full {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.rutas-table-full th {
  background: #f8f9fa;
  color: #495057;
  font-weight: 600;
  padding: 1rem;
  text-align: left;
  border-bottom: 2px solid #dee2e6;
  white-space: nowrap;
  position: sticky;
  top: 0;
  z-index: 10;
}

.rutas-table-full .id-col {
  width: 80px;
}

.rutas-table-full .ruta-col {
  width: 60%;
  min-width: 400px;
}

.rutas-table-full .fecha-col {
  width: 150px;
}

.rutas-table-full .acciones-col {
  width: 200px;
}

.ruta-row {
  transition: background-color 0.2s;
}

.ruta-row:hover {
  background-color: #f8f9fa;
}

.id-cell {
  padding: 1rem;
  text-align: center;
}

.id-badge {
  display: inline-block;
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  padding: 0.5rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.path-cell-full {
  padding: 0.75rem 1rem;
  max-width: 0;
}

.path-display {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.path-content {
  flex: 1;
  min-width: 0;
}

.path-text-full {
  font-family: 'Courier New', Consolas, monospace;
  font-size: 0.85rem;
  color: #495057;
  background: #f8f9fa;
  padding: 0.75rem;
  border-radius: 6px;
  border: 1px solid #e9ecef;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  line-height: 1.4;
  max-height: 120px;
  overflow-y: auto;
  min-height: 60px;
}

.path-actions {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.btn-copy {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.8rem;
}

.btn-copy:hover {
  background: #c3e6cb;
  transform: translateY(-1px);
}

.fecha-cell {
  padding: 1rem;
}

.fecha-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.fecha-principal {
  font-weight: 500;
  color: #495057;
}

.fecha-hora {
  font-size: 0.8rem;
  color: #6c757d;
}

.acciones-cell {
  padding: 1rem;
}

.btn-group-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-action-table {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 90px;
  justify-content: center;
}

.btn-action-table.btn-edit {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.btn-action-table.btn-edit:hover {
  background: #c3e6cb;
  transform: translateY(-1px);
}

.btn-action-table.btn-delete {
  background: #ffebee;
  color: #d32f2f;
  border: 1px solid #ffcdd2;
}

.btn-action-table.btn-delete:hover {
  background: #ffcdd2;
  transform: translateY(-1px);
}

/* ============ FORMULARIO PANTALLA COMPLETA ============ */
.ruta-form-fullscreen {
  background: #f8f9fa;
  border-radius: 12px;
  border: 2px solid #e9ecef;
  margin-top: 2rem;
  overflow: hidden;
}

.form-header {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  padding: 1.5rem 2rem;
}

.form-header h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.3rem;
  font-weight: 600;
}

.form-subtitle {
  margin: 0;
  opacity: 0.9;
  font-size: 0.95rem;
}

.form-content {
  padding: 2rem;
}

.form-group-full {
  margin-bottom: 2rem;
}

.form-group-full label {
  display: block;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: #495057;
  font-size: 1.1rem;
}

.form-control-fullscreen {
  width: 100%;
  padding: 1rem 1.25rem;
  border: 2px solid #ced4da;
  border-radius: 8px;
  font-size: 1rem;
  font-family: 'Courier New', Consolas, monospace;
  transition: all 0.3s;
  resize: vertical;
  min-height: 100px;
  background: white;
}

.form-control-fullscreen:focus {
  outline: none;
  border-color: #28a745;
  box-shadow: 0 0 0 4px rgba(40, 167, 69, 0.1);
}

.form-help-full {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding: 1rem;
  background: #d4edda;
  border-radius: 6px;
  border-left: 4px solid #28a745;
}

.form-help-full i {
  color: #155724;
  font-size: 1.2rem;
  margin-top: 0.1rem;
}

.form-help-full span {
  color: #155724;
  font-size: 0.9rem;
  line-height: 1.4;
}

.form-actions-full {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem 2rem;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
}

.btn-cancel {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1.5rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-cancel:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

.btn-save {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1.5rem;
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
  min-width: 150px;
  justify-content: center;
}

.btn-save:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

.btn-save:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.spinning {
  animation: spin 1s infinite;
}

/* ============ ARCHIVOS PANTALLA COMPLETA ============ */
.archivos-filters-full {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 1rem;
  align-items: end;
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #495057;
}

.filter-group select,
.filter-group input {
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: border-color 0.3s;
}

.filter-group select:focus,
.filter-group input:focus {
  outline: none;
  border-color: #28a745;
  box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.1);
}

.filter-stats {
  display: flex;
  align-items: center;
  gap: 1rem; /* 🔧 Agregar gap para separar elementos */
}

/* 🆕 ESTILOS PARA EL BOTÓN CSV EN EL MODAL */
.btn-csv-modal {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn-csv-modal:hover:not(:disabled) {
  background: linear-gradient(135deg, #218838, #1fa187);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

.btn-csv-modal:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
  transform: none;
  box-shadow: none;
}

.btn-csv-modal .material-icons {
  font-size: 1.1rem;
}

/* Animación para el icono de carga */
.btn-csv-modal:disabled .material-icons {
  animation: spin 1s linear infinite;
}

.stats-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
  border-radius: 20px;
  font-weight: 500;
  font-size: 0.9rem;
}

.archivos-table-container-full {
  flex: 1;
  overflow: auto;
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.archivos-table-full {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.archivos-table-full th {
  background: #f8f9fa;
  color: #495057;
  font-weight: 600;
  padding: 1rem;
  text-align: left;
  border-bottom: 2px solid #dee2e6;
  white-space: nowrap;
  position: sticky;
  top: 0;
  z-index: 10;
}

.archivos-table-full .nombre-col {
  width: 25%;
  min-width: 200px;
}

.archivos-table-full .componente-col {
  width: 15%;
  min-width: 150px;
}

.archivos-table-full .fecha-col {
  width: 12%;
  min-width: 120px;
}

.archivos-table-full .ruta-archivo-col {
  width: 35%;
  min-width: 300px;
}

.archivos-table-full .acciones-col {
  width: 13%;
  min-width: 180px;
}

.archivo-row {
  transition: background-color 0.2s;
}

.archivo-row:hover {
  background-color: #f8f9fa;
}

.nombre-cell {
  padding: 1rem;
}

.archivo-nombre {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.archivo-icon {
  color: #28a745;
  font-size: 1.2rem;
}

.componente-cell {
  padding: 1rem;
}

.componente-badge {
  display: inline-block;
  background: #d4edda;
  color: #155724;
  padding: 0.375rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  border: 1px solid #c3e6cb;
}

.ruta-archivo-cell {
  padding: 0.75rem 1rem;
  max-width: 0;
}

.path-text-archivo {
  font-family: 'Courier New', Consolas, monospace;
  font-size: 0.85rem;
  color: #495057;
  background: #f8f9fa;
  padding: 0.75rem;
  border-radius: 6px;
  border: 1px solid #e9ecef;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  line-height: 1.4;
  max-height: 100px;
  overflow-y: auto;
  min-height: 50px;
}

/* ============ NOTIFICACIONES ============ */
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 10000;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideInRight 0.3s ease;
}

.notification.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.notification.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.notification.warning {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.notification.info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
}

.notification-close {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 50%;
  margin-left: 0.5rem;
}

.notification-close:hover {
  background: rgba(0, 0, 0, 0.1);
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* ============ RESPONSIVE ============ */
@media (max-width: 768px) {
  .postoperacion-dashboard {
    padding: 0.5rem;
  }
  
  /* 🆕 Responsive para botones CSV */
  .header-actions {
    flex-direction: column;
    gap: 0.5rem;
    width: 100%;
  }
  
  .btn-export,
  .btn-csv-rutas,
  .btn-csv-archivos {
    width: 100%;
    justify-content: center;
    padding: 0.875rem 1rem;
  }
  
  .filter-stats {
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }
  
  .btn-csv-modal {
    justify-content: center;
    padding: 0.875rem 1rem;
    font-size: 0.85rem;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }
  
  .header-stats {
    justify-content: center;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .btn-group {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .modal-fullscreen {
    width: 100vw;
    height: 100vh;
    margin: 0;
    border-radius: 0;
  }
  
  .modal-body-fullscreen {
    padding: 1rem;
  }
  
  .archivos-filters-full {
    grid-template-columns: 1fr;
    gap: 1rem;
    padding: 1rem;
  }
  
  .archivos-table-container-full {
    overflow-x: auto;
  }
  
  .archivos-table-full .nombre-col {
    min-width: 150px;
  }
  
  .archivos-table-full .componente-col {
    min-width: 120px;
  }
  
  .archivos-table-full .ruta-archivo-col {
    min-width: 200px;
    width: 40%;
  }
  
  .path-text-archivo {
    font-size: 0.8rem;
    padding: 0.5rem;
    max-height: 80px;
  }
  
  .btn-group-actions {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .btn-action-table {
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
    min-width: 70px;
  }
  
  .form-content {
    padding: 1rem;
  }
  
  .form-control-fullscreen {
    font-size: 0.9rem;
    padding: 0.75rem 1rem;
    min-height: 80px;
  }
  
  .form-actions-full {
    padding: 1rem;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .btn-cancel,
  .btn-save {
    padding: 0.75rem 1rem;
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .btn-csv-modal {
    padding: 0.75rem 0.875rem;
    font-size: 0.8rem;
  }
  
  .btn-export,
  .btn-csv-rutas,
  .btn-csv-archivos {
    font-size: 0.9rem;
    padding: 0.75rem 0.875rem;
  }
}
</style>