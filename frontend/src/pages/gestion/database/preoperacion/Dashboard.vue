<template>
  <div class="preoperacion-dashboard">
    <!-- Header -->
    <header class="page-header">
      <div class="header-content">
        <h1>Dashboard Pre-operación</h1>
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
          
          <!-- 🆕 NUEVOS BOTONES CSV -->
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
                    title="Ver/Editar Rutas Preoperativas"
                  >
                    <i class="material-icons">folder_open</i>
                    Rutas
                  </button>
                  <button 
                    @click="verArchivos(municipio)" 
                    class="btn-action btn-archivos"
                    title="Ver/Gestionar Archivos Pre-operación"
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

    <!-- Modal para gestionar Rutas Pre-operación -->
    <div v-if="showRutasModal" class="modal-overlay" @click="closeRutasModal">
      <div class="modal-content modal-fullscreen" @click.stop>
        <div class="modal-header">
          <h3>Rutas Pre-operación - {{ selectedMunicipio?.nom_municipio }}</h3>
          <button @click="closeRutasModal" class="modal-close">
            <i class="material-icons">close</i>
          </button>
        </div>
        <div class="modal-body-fullscreen">
          <!-- Botón para agregar nueva ruta -->
          <div class="section-header">
            <h4>Rutas Preoperativas del Municipio</h4>
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
            <p>Este municipio no tiene rutas preoperativas registradas.</p>
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
              <h4>{{ editingRuta ? 'Editar Ruta Preoperativa' : 'Nueva Ruta Preoperativa' }}</h4>
              <p class="form-subtitle">Municipio: <strong>{{ selectedMunicipio?.nom_municipio }}</strong></p>
            </div>
            <div class="form-content">
              <div class="form-group-full">
                <label for="path-input">Ruta del Directorio Preoperativo:</label>
                <textarea 
                  id="path-input"
                  v-model="rutaForm.path" 
                  class="form-control-fullscreen"
                  placeholder="Ejemplo: C:\Users\usuario\Documents\Proyectos\IGAC\Municipios\{{ selectedMunicipio?.nom_municipio }}\Preoperacion\2024\Datos"
                  rows="4"
                  required
                ></textarea>
                <div class="form-help-full">
                  <i class="material-icons">info</i>
                  <span>Ingrese la ruta completa del directorio donde se almacenan los archivos preoperativos de este municipio. La ruta debe ser accesible desde el servidor.</span>
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

    <!-- Modal para gestionar Archivos Pre-operación -->
    <div v-if="showArchivosModal" class="modal-overlay" @click="closeArchivosModal">
      <div class="modal-content modal-fullscreen" @click.stop>
        <div class="modal-header">
          <h3>Archivos Pre-operación - {{ selectedMunicipio?.nom_municipio }}</h3>
          <button @click="closeArchivosModal" class="modal-close">
            <i class="material-icons">close</i>
          </button>
        </div>
        <div class="modal-body-fullscreen">
          <!-- Filtros de archivos -->
          <div class="archivos-filters-full">
            <div class="filter-group">
              <label>Filtrar por Clasificación:</label>
              <select v-model="filtroClasificacionPre" @change="filtrarArchivos">
                <option value="">Todas las clasificaciones</option>
                <option v-for="clasificacion in clasificacionesUnicasPre" :key="clasificacion" :value="clasificacion">
                  {{ clasificacion }}
                </option>
              </select>
            </div>
            <div class="filter-group">
              <label>Buscar archivo:</label>
              <input 
                v-model="filtroNombreArchivo" 
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
            <p v-if="archivosMunicipio.length === 0">Este municipio no tiene archivos preoperativos registrados.</p>
            <p v-else>No se encontraron archivos con los filtros aplicados.</p>
          </div>
          
          <div v-else class="archivos-table-container-full">
            <table class="archivos-table-full">
              <thead>
                <tr>
                  <th class="nombre-col">Nombre</th>
                  <th class="clasificacion-col">Clasificación</th>
                  <th class="fecha-col">Fecha</th>
                  <th class="ruta-archivo-col">Ruta del Archivo</th>
                  <th class="acciones-col">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="archivo in archivosFiltrados" :key="archivo.id_lista_archivo" class="archivo-row">
                  <td class="nombre-cell">
                    <div class="archivo-nombre">
                      <i class="material-icons archivo-icon">description</i>
                      <span>{{ archivo.nombre_insumo || 'Sin nombre' }}</span>
                    </div>
                  </td>
                  <td class="clasificacion-cell">
                    <span class="clasificacion-badge">
                      {{ getNombreClasificacion(archivo.cod_insumo) }}
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
                        <pre class="path-text-archivo">{{ linuxToWindowsPath(archivo.path_file) || 'Sin ruta definida' }}</pre>
                      </div>
                      <div class="path-actions">
                        <button v-if="archivo.path_file" @click="copyToClipboard(archivo.path_file)" class="btn-copy" title="Copiar ruta">
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
const categorias = ref<any[]>([]);
const cargandoCSVModal = ref(false)
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

// Estados para Archivos
const archivosMunicipio = ref<any[]>([]);
const loadingArchivos = ref(false);
const filtroClasificacionPre = ref(''); // ✅ Cambio de nombre para coincidir con InsumosList
const filtroNombreArchivo = ref('');
const categoriasArchivos = ref<any[]>([]);
const clasificaciones = ref<any[]>([]); // ✅ Agregar para el filtro

const descargarCSVMunicipioModal = async () => {
  if (!selectedMunicipio.value || archivosFiltrados.value.length === 0) {
    showNotification('No hay archivos para descargar', 'warning')
    return
  }
  
  try {
    cargandoCSVModal.value = true
    
    showNotification(`Generando CSV de ${selectedMunicipio.value.nom_municipio}...`, 'info')
    
    // Preparar datos para CSV usando los archivos ya filtrados
    const datosCSV = []
    
    archivosFiltrados.value.forEach(archivo => {
      // Buscar nombre de clasificación
      let nombreClasificacion = 'N/A'
      if (archivo.cod_insumo) {
        nombreClasificacion = getNombreClasificacion(archivo.cod_insumo)
      }
      
      // Calcular extensión del archivo
      let extension = 'N/A'
      if (archivo.path_file) {
        const partes = archivo.path_file.split('.')
        if (partes.length > 1) {
          extension = partes[partes.length - 1].toUpperCase()
        }
      }
      
      datosCSV.push({
        id: archivo.id_lista_archivo || 'N/A',
        municipio: selectedMunicipio.value.nom_municipio,
        departamento: getNombreDepartamento(selectedMunicipio.value.cod_depto),
        nombreArchivo: archivo.nombre_insumo || 'Sin nombre',
        clasificacion: nombreClasificacion,
        ruta: archivo.path_file || 'N/A',
        tamano: 'Ver archivo',
        fechaCreacion: formatearFechaCSV(archivo.fecha_disposicion || ''),
        extension: extension,
        observacion: archivo.observacion || '',
        usuario: archivo.usuario_windows || '',
        hashContenido: archivo.hash_contenido || 'N/A'
      })
    })
    
    // Generar contenido CSV
    let contenidoCSV = `ID,Municipio,Departamento,Nombre Archivo,Clasificación,Ruta,Tamaño,Fecha Creación,Extensión,Observación,Usuario,Hash Contenido\n`
    
    datosCSV.forEach(item => {
      const fila = [
        escaparCSV(item.id),
        escaparCSV(item.municipio),
        escaparCSV(item.departamento),
        escaparCSV(item.nombreArchivo),
        escaparCSV(item.clasificacion),
        escaparCSV(item.ruta),
        escaparCSV(item.tamano),
        escaparCSV(item.fechaCreacion),
        escaparCSV(item.extension),
        escaparCSV(item.observacion),
        escaparCSV(item.usuario),
        escaparCSV(item.hashContenido)
      ].join(',')
      
      contenidoCSV += fila + '\n'
    })
    
    // Crear y descargar archivo
    const blob = generarCSVConBOM(contenidoCSV)
    const fecha = new Date().toISOString().split('T')[0]
    const nombreArchivo = `archivos_${selectedMunicipio.value.nom_municipio.replace(/\s+/g, '_')}_${fecha}.csv`
    
    descargarArchivo(blob, nombreArchivo)
    
    showNotification(`CSV descargado: ${datosCSV.length} archivos de ${selectedMunicipio.value.nom_municipio}`, 'success')
    
  } catch (error) {
    console.error('Error generando CSV del municipio:', error)
    showNotification('Error al generar CSV del municipio', 'error')
  } finally {
    cargandoCSVModal.value = false
  }
}
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

// 🔧 FUNCIONES CORREGIDAS PARA DESCARGA CSV EN Dashboard.vue
// Reemplazar las funciones descargarCSVRutas y descargarCSVArchivos existentes
// 🔧 FUNCIONES CSV CORREGIDAS - USANDO ENDPOINTS REALES QUE FUNCIONAN



// 🆕 FUNCIÓN 1 CORREGIDA: DESCARGAR CSV DE RUTAS (TODAS DE UNA VEZ)
const descargarCSVRutas = async () => {
  try {
    showNotification('Generando CSV de rutas...', 'info');
    
    // ✅ USAR ENDPOINT DIRECTO para todas las rutas
    let todasLasRutas: any[] = [];
    
    try {
      const response = await api.get('/preoperacion/path-pre/');
      console.log('📁 Respuesta completa rutas:', response);
      
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
      
      console.log(`📊 Total rutas cargadas: ${todasLasRutas.length}`);
      
      if (todasLasRutas.length === 0) {
        showNotification('No se encontraron rutas para generar CSV', 'warning');
        return;
      }
    } catch (error) {
      console.error('Error cargando rutas completas:', error);
      showNotification(`Error al cargar rutas: ${error.message}`, 'error');
      return;
    }
    
    // Crear mapa de municipios para obtener nombres (si no vienen incluidos)
    const municipiosMap = new Map();
    municipiosList.value.forEach(m => {
      municipiosMap.set(m.cod_municipio, {
        nombre: m.nom_municipio,
        departamento: getNombreDepartamento(m.cod_depto)
      });
    });
    
    // Preparar datos para CSV con estructura REAL
    const datosCSV = [];
    
    todasLasRutas.forEach(ruta => {
      console.log('🔍 Procesando ruta:', ruta);
      
      // Estructura real: { id, cod_municipio, municipio_nombre, path, fecha_creacion, municipio: {...} }
      let municipioNombre = 'Sin municipio';
      let departamento = 'Sin departamento';
      
      // Priorizar municipio_nombre si existe
      if (ruta.municipio_nombre) {
        municipioNombre = ruta.municipio_nombre;
      } else if (ruta.municipio?.nom_municipio) {
        municipioNombre = ruta.municipio.nom_municipio;
      } else if (ruta.cod_municipio) {
        // Buscar en el mapa si no viene la info
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
        observaciones: '' // Este modelo no tiene observaciones
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
    const nombreArchivo = `rutas_preoperativas_municipios_${fecha}.csv`;
    
    descargarArchivo(blob, nombreArchivo);
    
    showNotification(`CSV de rutas descargado: ${datosCSV.length} registros`, 'success');
    
  } catch (error) {
    console.error('Error generando CSV de rutas:', error);
    showNotification('Error al generar CSV de rutas', 'error');
  }
};

// 🆕 FUNCIÓN 2 CORREGIDA: DESCARGAR CSV DE ARCHIVOS (CON PAGINACIÓN)
const descargarCSVArchivos = async () => {
  try {
    showNotification('Generando CSV de archivos...', 'info');
    
    // ✅ USAR ENDPOINT DIRECTO con manejo de paginación
    let todosLosArchivos: any[] = [];
    let paginaActual = 1;
    let totalPaginas = 1;
    
    try {
      // Primera llamada para obtener info de paginación
      showNotification('Cargando página 1 de archivos...', 'info');
      const primeraRespuesta = await api.get('/preoperacion/archivos-pre/?page=1');
      console.log('📄 Primera respuesta archivos:', primeraRespuesta);
      
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
          console.log(`📊 Paginación detectada: ${total} registros, ~${totalPaginas} páginas`);
        }
        
        todosLosArchivos.push(...archivos);
        
        // Cargar páginas adicionales si existen
        if (siguientePagina && totalPaginas > 1) {
          for (let pagina = 2; pagina <= totalPaginas; pagina++) {
            try {
              showNotification(`Cargando página ${pagina} de ${totalPaginas}...`, 'info');
              const respuestaPagina = await api.get(`/preoperacion/archivos-pre/?page=${pagina}`);
              
              if (respuestaPagina.results && respuestaPagina.results.length > 0) {
                todosLosArchivos.push(...respuestaPagina.results);
                console.log(`✅ Página ${pagina} cargada: ${respuestaPagina.results.length} archivos`);
              } else {
                console.log(`🔚 No hay más páginas después de ${pagina - 1}`);
                break;
              }
            } catch (errorPagina) {
              console.warn(`⚠️ Error cargando página ${pagina}:`, errorPagina);
              break;
            }
          }
        }
      } else {
        // Estructura desconocida
        console.warn('🤔 Estructura de respuesta desconocida:', primeraRespuesta);
        todosLosArchivos = [primeraRespuesta];
      }
      
      console.log(`📊 Total archivos cargados: ${todosLosArchivos.length} de ${total}`);
      
      if (todosLosArchivos.length === 0) {
        showNotification('No se encontraron archivos para generar CSV', 'warning');
        return;
      }
      
    } catch (error) {
      console.error('Error cargando archivos completos:', error);
      showNotification(`Error al cargar archivos: ${error.message}`, 'error');
      return;
    }
    
    // Cargar clasificaciones para nombres
    let clasificacionesCompletas: any[] = [];
    try {
      showNotification('Cargando clasificaciones...', 'info');
      const responseClasif = await api.get('/preoperacion/clasificaciones/');
      clasificacionesCompletas = Array.isArray(responseClasif) ? responseClasif : (Array.isArray(responseClasif.results) ? responseClasif.results : []);
    } catch (error) {
      console.warn('Error cargando clasificaciones:', error);
    }
    
    // Crear mapa de municipios
    const municipiosMap = new Map();
    municipiosList.value.forEach(m => {
      municipiosMap.set(m.cod_municipio, {
        nombre: m.nom_municipio,
        departamento: getNombreDepartamento(m.cod_depto)
      });
    });
    
    // Crear mapa de clasificaciones
    const clasificacionesMap = new Map();
    clasificacionesCompletas.forEach(c => {
      clasificacionesMap.set(c.cod_clasificacion, c.nombre || c.nom_clasificacion || c.nom_insumo || 'Sin nombre');
    });
    
    // Preparar datos para CSV
    showNotification('Procesando datos para CSV...', 'info');
    const datosCSV = [];
    
    todosLosArchivos.forEach(archivo => {
      console.log('🔍 Procesando archivo (sample):', Object.keys(archivo));
      
      // Estructura real: { id_lista_archivo, nombre_insumo, cod_insumo, fecha_disposicion, hash_contenido, observacion, path_file, usuario_windows }
      
      let municipioNombre = 'Sin municipio';
      let departamento = 'Sin departamento';
      
      // Intentar extraer municipio desde cod_insumo o directamente
      if (archivo.cod_municipio) {
        const municipio = municipiosMap.get(archivo.cod_municipio);
        if (municipio) {
          municipioNombre = municipio.nombre;
          departamento = municipio.departamento;
        }
      }
      
      // Buscar nombre de clasificación
      let nombreClasificacion = 'N/A';
      if (archivo.cod_insumo) {
        nombreClasificacion = clasificacionesMap.get(archivo.cod_insumo) || `Insumo ${archivo.cod_insumo}`;
      }
      
      // Calcular extensión del archivo
      let extension = 'N/A';
      if (archivo.path_file) {
        const partes = archivo.path_file.split('.');
        if (partes.length > 1) {
          extension = partes[partes.length - 1].toUpperCase();
        }
      }
      
      datosCSV.push({
        id: archivo.id_lista_archivo || archivo.id || 'N/A',
        municipio: municipioNombre,
        departamento: departamento,
        nombreArchivo: archivo.nombre_insumo || 'Sin nombre',
        clasificacion: nombreClasificacion,
        ruta: archivo.path_file || 'N/A',
        tamano: archivo.tamano || archivo.size || 'N/A',
        fechaCreacion: formatearFechaCSV(archivo.fecha_disposicion || ''),
        extension: extension,
        observacion: archivo.observacion || '',
        usuario: archivo.usuario_windows || '',
        hashContenido: archivo.hash_contenido || 'N/A'
      });
    });
    
    // Generar contenido CSV
    showNotification('Generando archivo CSV...', 'info');
    let contenidoCSV = 'ID,Municipio,Departamento,Nombre Archivo,Clasificación,Ruta,Tamaño,Fecha Creación,Extensión,Observación,Usuario,Hash Contenido\n';
    
    datosCSV.forEach(item => {
      const fila = [
        escaparCSV(item.id),
        escaparCSV(item.municipio),
        escaparCSV(item.departamento),
        escaparCSV(item.nombreArchivo),
        escaparCSV(item.clasificacion),
        escaparCSV(item.ruta),
        escaparCSV(item.tamano),
        escaparCSV(item.fechaCreacion),
        escaparCSV(item.extension),
        escaparCSV(item.observacion),
        escaparCSV(item.usuario),
        escaparCSV(item.hashContenido)
      ].join(',');
      
      contenidoCSV += fila + '\n';
    });
    
    // Crear y descargar archivo
    const blob = generarCSVConBOM(contenidoCSV);
    const fecha = new Date().toISOString().split('T')[0];
    const nombreArchivo = `archivos_preoperacion_completo_${fecha}.csv`;
    
    descargarArchivo(blob, nombreArchivo);
    
    showNotification(`CSV de archivos descargado: ${datosCSV.length} registros`, 'success');
    
  } catch (error) {
    console.error('Error generando CSV de archivos:', error);
    showNotification('Error al generar CSV de archivos', 'error');
  }
};

// 🆕 FUNCIÓN DEBUG PARA VER ESTRUCTURA EXACTA DE RESPUESTAS
const debugEstructuraRespuestas = async () => {
  try {
    console.log('🔍 === DEBUG: ESTRUCTURA DE RESPUESTAS ===');
    
    // Debug rutas
    try {
      console.log('📁 Probando endpoint de rutas...');
      const rutasResponse = await api.get('/preoperacion/path-pre/');
      console.log('📁 RUTAS - Tipo de respuesta:', typeof rutasResponse);
      console.log('📁 RUTAS - Es array:', Array.isArray(rutasResponse));
      console.log('📁 RUTAS - Claves del objeto:', Object.keys(rutasResponse));
      
      const rutas = Array.isArray(rutasResponse) ? rutasResponse : (rutasResponse.results || []);
      console.log('📁 RUTAS - Total:', rutas.length);
      
      if (rutas.length > 0) {
        console.log('📁 RUTAS - Primer elemento:', rutas[0]);
        console.log('📁 RUTAS - Campos disponibles:', Object.keys(rutas[0]));
      }
    } catch (error) {
      console.error('❌ Error debugeando rutas:', error);
    }
    
    // Debug archivos (solo primera página)
    try {
      console.log('📄 Probando endpoint de archivos...');
      const archivosResponse = await api.get('/preoperacion/archivos-pre/?page=1');
      console.log('📄 ARCHIVOS - Tipo de respuesta:', typeof archivosResponse);
      console.log('📄 ARCHIVOS - Es array:', Array.isArray(archivosResponse));
      console.log('📄 ARCHIVOS - Claves del objeto:', Object.keys(archivosResponse));
      
      // Verificar paginación
      if (archivosResponse.count) {
        console.log('📄 ARCHIVOS - Total registros:', archivosResponse.count);
        console.log('📄 ARCHIVOS - Tiene siguiente página:', !!archivosResponse.next);
        console.log('📄 ARCHIVOS - URL siguiente:', archivosResponse.next);
      }
      
      const archivos = Array.isArray(archivosResponse) ? archivosResponse : (archivosResponse.results || []);
      console.log('📄 ARCHIVOS - En esta página:', archivos.length);
      
      if (archivos.length > 0) {
        console.log('📄 ARCHIVOS - Primer elemento:', archivos[0]);
        console.log('📄 ARCHIVOS - Campos disponibles:', Object.keys(archivos[0]));
      }
    } catch (error) {
      console.error('❌ Error debugeando archivos:', error);
    }
    
    console.log('🔍 === FIN DEBUG ===');
    showNotification('Debug completado - Ver consola del navegador', 'info');
    
  } catch (error) {
    console.error('❌ Error general en debug:', error);
    showNotification('Error en debug', 'error');
  }
};

// 🆕 FUNCIÓN 3 ADICIONAL: DESCARGAR CSV DE ARCHIVOS POR CLASIFICACIÓN
const descargarCSVArchivosPorClasificacion = async () => {
  try {
    showNotification('Generando CSV de archivos por clasificación...', 'info');
    
    // Cargar todas las clasificaciones
    const clasificacionesResponse = await api.get('/preoperacion/clasificaciones/');
    const clasificaciones = Array.isArray(clasificacionesResponse) ? clasificacionesResponse : (Array.isArray(clasificacionesResponse.results) ? clasificacionesResponse.results : []);
    
    if (clasificaciones.length === 0) {
      showNotification('No se encontraron clasificaciones', 'warning');
      return;
    }
    
    let todosLosArchivos: any[] = [];
    
    // Para cada clasificación, obtener sus archivos usando el endpoint correcto
    for (const clasificacion of clasificaciones) {
      try {
        const archivosResponse = await api.get(`/preoperacion/clasificaciones/${clasificacion.cod_clasificacion}/archivos-pre/`);
        const archivos = Array.isArray(archivosResponse) ? archivosResponse : (Array.isArray(archivosResponse.results) ? archivosResponse.results : []);
        
        // Enriquecer archivos con información de clasificación
        const archivosEnriquecidos = archivos.map(archivo => ({
          ...archivo,
          clasificacion_info: {
            cod_clasificacion: clasificacion.cod_clasificacion,
            nombre_clasificacion: clasificacion.nombre || clasificacion.nom_clasificacion
          }
        }));
        
        todosLosArchivos.push(...archivosEnriquecidos);
      } catch (error) {
        console.warn(`Error cargando archivos para clasificación ${clasificacion.cod_clasificacion}:`, error);
      }
    }
    
    if (todosLosArchivos.length === 0) {
      showNotification('No se encontraron archivos en ninguna clasificación', 'warning');
      return;
    }
    
    // Crear mapa de municipios
    const municipiosMap = new Map();
    municipiosList.value.forEach(m => {
      municipiosMap.set(m.cod_municipio, {
        nombre: m.nom_municipio,
        departamento: getNombreDepartamento(m.cod_depto)
      });
    });
    
    // Preparar datos para CSV
    const datosCSV = [];
    
    todosLosArchivos.forEach(archivo => {
      let municipioInfo = { nombre: 'Sin municipio', departamento: 'Sin departamento' };
      
      // Obtener municipio desde diferentes posibles estructuras
      const codMunicipio = archivo.cod_municipio || 
                          archivo.cod_insumo?.cod_municipio?.cod_municipio || 
                          archivo.cod_insumo?.cod_municipio;
      
      if (codMunicipio) {
        const municipio = municipiosMap.get(codMunicipio);
        if (municipio) {
          municipioInfo = municipio;
        }
      }
      
      datosCSV.push({
        id: archivo.id || archivo.cod_archivo || 'N/A',
        municipio: municipioInfo.nombre,
        departamento: municipioInfo.departamento,
        nombreArchivo: archivo.nom_archivo || archivo.nombre_archivo || archivo.archivo || 'Sin nombre',
        clasificacion: archivo.clasificacion_info?.nombre_clasificacion || 'N/A',
        codClasificacion: archivo.clasificacion_info?.cod_clasificacion || 'N/A',
        ruta: archivo.ruta_archivo || archivo.path || archivo.directorio || 'N/A',
        tamano: archivo.tamano || archivo.size || 'N/A',
        fechaCreacion: formatearFechaCSV(archivo.fecha_creacion || archivo.created_at || ''),
        extension: archivo.extension || 'N/A'
      });
    });
    
    // Generar contenido CSV
    let contenidoCSV = 'ID,Municipio,Departamento,Nombre Archivo,Clasificación,Cód. Clasificación,Ruta,Tamaño,Fecha Creación,Extensión\n';
    
    datosCSV.forEach(item => {
      const fila = [
        escaparCSV(item.id),
        escaparCSV(item.municipio),
        escaparCSV(item.departamento),
        escaparCSV(item.nombreArchivo),
        escaparCSV(item.clasificacion),
        escaparCSV(item.codClasificacion),
        escaparCSV(item.ruta),
        escaparCSV(item.tamano),
        escaparCSV(item.fechaCreacion),
        escaparCSV(item.extension)
      ].join(',');
      
      contenidoCSV += fila + '\n';
    });
    
    // Crear y descargar archivo
    const blob = generarCSVConBOM(contenidoCSV);
    const fecha = new Date().toISOString().split('T')[0];
    const nombreArchivo = `archivos_por_clasificacion_${fecha}.csv`;
    
    descargarArchivo(blob, nombreArchivo);
    
    showNotification(`CSV de archivos por clasificación descargado: ${datosCSV.length} registros`, 'success');
    
  } catch (error) {
    console.error('Error generando CSV de archivos por clasificación:', error);
    showNotification('Error al generar CSV de archivos por clasificación', 'error');
  }
};

// ✅ FUNCIONES DE UTILIDAD COPIADAS DE InsumosList.vue
const getNombreClasificacion = (codInsumo: any): string => {
  if (!codInsumo) return 'N/A';
  
  try {
    const clasificacion = clasificaciones.value.find(c => 
      c.cod_clasificacion?.toString() === codInsumo.toString()
    );
    return clasificacion ? clasificacion.nombre : 'N/A';
  } catch (error) {
    console.error('Error en getNombreClasificacion:', error);
    return 'N/A';
  }
};

// ✅ CLASIFICACIONES ÚNICAS PARA EL FILTRO (copiado de InsumosList)
const clasificacionesUnicasPre = computed(() => {
  const clasificacionesSet = new Set();
  archivosMunicipio.value.forEach(archivo => {
    if (archivo.cod_insumo) {
      const nombreClasificacion = getNombreClasificacion(archivo.cod_insumo);
      if (nombreClasificacion && nombreClasificacion !== 'N/A') {
        clasificacionesSet.add(nombreClasificacion);
      }
    }
  });
  return Array.from(clasificacionesSet).sort();
});

// ✅ SISTEMA DE FILTROS DINÁMICOS CORREGIDO

const municipiosBase = computed(() => {
  let result = [...municipiosList.value];
  
  // Filtrar por permisos si es profesional
  if (authStore.isProfesional) {
    result = result.filter(m => tieneAccesoAMunicipio(m.cod_municipio));
  }
  
  return result;
});

// ✅ DEPARTAMENTOS DISPONIBLES CORREGIDO - auto filtrado según otros filtros activos
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

// ✅ MUNICIPIOS DISPONIBLES CORREGIDO - auto filtrado por departamento seleccionado
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
  
  // ✅ AUTO-FILTRAR POR DEPARTAMENTO SELECCIONADO
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

// ✅ ARCHIVOS FILTRADOS CORREGIDO (copiado de InsumosList.vue)
const archivosFiltrados = computed(() => {
  let result = [...archivosMunicipio.value];
  
  if (filtroClasificacionPre.value) {
    result = result.filter(a => {
      const nombreClasificacion = getNombreClasificacion(a.cod_insumo);
      return nombreClasificacion === filtroClasificacionPre.value;
    });
  }
  
  if (filtroNombreArchivo.value.trim()) {
    const search = filtroNombreArchivo.value.toLowerCase();
    result = result.filter(a => 
      a.nombre_insumo?.toLowerCase().includes(search) ||
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

// ✅ NUEVA FUNCIÓN PARA COPIAR AL PORTAPAPELES
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

// ✅ FUNCIONES DE CARGA DE DATOS CORREGIDAS
const loadInitialData = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    departamentos.value = [];
    municipiosList.value = [];
    categorias.value = [];
    
    console.log('🔄 Cargando datos iniciales...');
    
    const [
      municipiosResult,
      departamentosResult,
      categoriasResult,
      clasificacionesResult
    ] = await Promise.allSettled([
      // ✅ USAR API CORRECTA DE MUNICIPIOS CON PREFIJO
      api.get('/preoperacion/municipios/'),
      // ✅ USAR API CORRECTA DE DEPARTAMENTOS CON PREFIJO
      api.get('/preoperacion/departamentos/'),
      // ✅ USAR API CORRECTA DE CATEGORÍAS CON PREFIJO
      api.get('/preoperacion/categorias/'),
      // ✅ CARGAR CLASIFICACIONES PARA EL FILTRO
      api.get('/preoperacion/clasificaciones/')
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
    
    if (categoriasResult.status === 'fulfilled') {
      const data = categoriasResult.value;
      categorias.value = Array.isArray(data) ? data : (Array.isArray(data.results) ? data.results : []);
      console.log(`✅ Categorías cargadas: ${categorias.value.length}`);
    } else {
      console.error('❌ Error cargando categorías:', categoriasResult.reason);
      categorias.value = [];
    }
    
    if (clasificacionesResult.status === 'fulfilled') {
      const data = clasificacionesResult.value;
      clasificaciones.value = Array.isArray(data) ? data : (Array.isArray(data.results) ? data.results : []);
      console.log(`✅ Clasificaciones cargadas: ${clasificaciones.value.length}`);
    } else {
      console.error('❌ Error cargando clasificaciones:', clasificacionesResult.reason);
      clasificaciones.value = [];
    }
    
    console.log('✅ Datos cargados exitosamente');
    
  } catch (err: any) {
    console.error('❌ Error loading initial data:', err);
    error.value = 'Error al cargar datos iniciales: ' + (err.message || 'Error desconocido');
  } finally {
    loading.value = false;
  }
};

// ✅ FUNCIONES DE FILTROS CORREGIDAS
const handleSearchInput = () => {
  currentPage.value = 1;
};

const clearSearch = () => {
  searchTerm.value = '';
  currentPage.value = 1;
};

// ✅ CUANDO CAMBIA DEPARTAMENTO, AUTO-LIMPIAR MUNICIPIO
const handleDepartamentoChange = () => {
  filters.value.municipio = ''; // ✅ AUTO-LIMPIAR municipio
  currentPage.value = 1;
};

const handleMunicipioChange = () => {
  currentPage.value = 1;
};

const limpiarFiltroEspecifico = (filtro: string) => {
  (filters.value as any)[filtro] = '';
  if (filtro === 'departamento') {
    filters.value.municipio = ''; // ✅ Si limpia departamento, también municipio
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

// ✅ FUNCIONES PARA RUTAS CORREGIDAS - Mostrar tabla path_dir_pre en modal
const verRutas = async (municipio: any) => {
  selectedMunicipio.value = municipio;
  showRutasModal.value = true;
  await cargarRutasMunicipio(municipio.cod_municipio);
};

const cargarRutasMunicipio = async (codMunicipio: number) => {
  try {
    loadingRutas.value = true;
    console.log(`Cargando rutas para municipio: ${codMunicipio}`);
    
    // ✅ USAR ENDPOINT ESPECÍFICO BY_MUNICIPIO para filtrar correctamente
    const response = await api.get(`/preoperacion/path-pre/by_municipio/?cod_municipio=${codMunicipio}`);
    rutasMunicipio.value = Array.isArray(response) ? response : (Array.isArray(response.results) ? response.results : []);
    
    console.log(`✅ Rutas cargadas para municipio ${codMunicipio}: ${rutasMunicipio.value.length}`);
    
  } catch (error) {
    console.error('Error cargando rutas:', error);
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
      await api.put(`/preoperacion/path-pre/${editingRuta.value.id}/`, datos);
      showNotification('Ruta actualizada exitosamente', 'success');
    } else {
      // Crear nueva ruta
      await api.post('/preoperacion/path-pre/', datos);
      showNotification('Ruta creada exitosamente', 'success');
    }
    
    cancelarRutaForm();
    await cargarRutasMunicipio(selectedMunicipio.value.cod_municipio);
    
  } catch (error) {
    console.error('Error guardando ruta:', error);
    showNotification('Error al guardar la ruta', 'error');
  } finally {
    savingRuta.value = false;
  }
};

const eliminarRuta = async (ruta: any) => {
  if (!confirm('¿Está seguro que desea eliminar esta ruta?')) return;
  
  try {
    await api.delete(`/preoperacion/path-pre/${ruta.id}/`);
    showNotification('Ruta eliminada exitosamente', 'success');
    await cargarRutasMunicipio(selectedMunicipio.value.cod_municipio);
  } catch (error) {
    console.error('Error eliminando ruta:', error);
    showNotification('Error al eliminar la ruta', 'error');
  }
};

const closeRutasModal = () => {
  showRutasModal.value = false;
  selectedMunicipio.value = null;
  rutasMunicipio.value = [];
  cancelarRutaForm();
};

// ✅ FUNCIONES PARA ARCHIVOS
const verArchivos = async (municipio: any) => {
  selectedMunicipio.value = municipio;
  showArchivosModal.value = true;
  await cargarArchivosMunicipio(municipio.cod_municipio);
};

const cargarArchivosMunicipio = async (codMunicipio: number) => {
  try {
    loadingArchivos.value = true;
    console.log(`Cargando archivos para municipio: ${codMunicipio}`);
    
    // ✅ USAR ENDPOINT ESPECÍFICO POR MUNICIPIO para archivos también
    try {
      // Intentar endpoint específico por municipio
      const response = await api.get(`/preoperacion/archivos-pre/por_municipio/?municipio_id=${codMunicipio}`);
      archivosMunicipio.value = Array.isArray(response) ? response : (Array.isArray(response.results) ? response.results : []);
    } catch (error) {
      // Si falla, usar filtro general
      console.warn('Endpoint específico falló, usando filtro general');
      const response = await api.get(`/preoperacion/archivos-pre/?municipio=${codMunicipio}`);
      archivosMunicipio.value = Array.isArray(response) ? response : (Array.isArray(response.results) ? response.results : []);
    }
    
    console.log(`✅ Archivos cargados para municipio ${codMunicipio}: ${archivosMunicipio.value.length}`);
    
  } catch (error) {
    console.error('Error cargando archivos:', error);
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
  // Navegar a una página de edición o mostrar un modal simple
  console.log('Editar archivo:', archivo);
  showNotification('Funcionalidad de edición en desarrollo', 'info');
};

const eliminarArchivo = async (archivo: any) => {
  if (!confirm('¿Está seguro que desea eliminar este archivo?')) return;
  
  try {
    await api.delete(`/preoperacion/archivos-pre/${archivo.id_lista_archivo}/`);
    showNotification('Archivo eliminado exitosamente', 'success');
    await cargarArchivosMunicipio(selectedMunicipio.value.cod_municipio);
  } catch (error) {
    console.error('Error eliminando archivo:', error);
    showNotification('Error al eliminar el archivo', 'error');
  }
};

const closeArchivosModal = () => {
  showArchivosModal.value = false;
  selectedMunicipio.value = null;
  archivosMunicipio.value = [];
  filtroClasificacionPre.value = ''; // ✅ Cambio de nombre
  filtroNombreArchivo.value = '';
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
</script>

<style scoped>
/* 🆕 ESTILOS PARA EL BOTÓN CSV EN EL MODAL */
.filter-stats {
  display: flex;
  align-items: center;
  gap: 1rem; /* 🔧 Agregar gap para separar elementos */
}

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
/* ============ ESTILOS PRINCIPALES ============ */
.preoperacion-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  flex-wrap: wrap;
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

/* 🆕 ESTILOS PARA BOTONES CSV */
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
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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
  background: #e7f3ff;
  color: #0066cc;
  border: 1px solid #b3d9ff;
}

.filter-tag.department {
  background: #fff2e7;
  color: #cc6600;
  border: 1px solid #ffb366;
}

.filter-tag.municipio {
  background: #e7ffe7;
  color: #006600;
  border: 1px solid #66ff66;
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
  border-left-color: #667eea;
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
  background: #667eea;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-retry:hover {
  background: #5a6fd8;
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
  background: linear-gradient(135deg, #667eea, #764ba2);
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
  background: #e3f2fd;
  color: #1976d2;
  border: 1px solid #bbdefb;
}

.btn-rutas:hover {
  background: #bbdefb;
  transform: translateY(-1px);
}

.btn-archivos {
  background: #f3e5f5;
  color: #7b1fa2;
  border: 1px solid #ce93d8;
}

.btn-archivos:hover {
  background: #ce93d8;
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
  border-color: #667eea;
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
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

.modal-large {
  max-width: 900px;
}

.modal-extra-large {
  max-width: 1200px;
  width: 95vw;
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

.modal-body {
  padding: 1.5rem;
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
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary:hover {
  background: #5a6fd8;
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
  border-left-color: #667eea;
  border-radius: 50%;
  animation: spin 1s infinite;
  margin-right: 0.5rem;
}

.rutas-table-container {
  overflow-x: auto;
}

.rutas-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.rutas-table th {
  background: #f8f9fa;
  padding: 0.75rem 0.5rem;
  text-align: left;
  font-weight: 600;
  color: #495057;
  border-bottom: 2px solid #dee2e6;
  white-space: nowrap;
}

.rutas-table td {
  padding: 0.75rem 0.5rem;
  border-bottom: 1px solid #e9ecef;
  vertical-align: middle;
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
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 0.5rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.path-cell-full {
  padding: 0.75rem 1rem;
  max-width: 0; /* Permite que el texto se expanda */
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
  background: #e3f2fd;
  color: #1976d2;
  border: 1px solid #bbdefb;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.8rem;
}

.btn-copy:hover {
  background: #bbdefb;
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
  background: #e3f2fd;
  color: #1976d2;
  border: 1px solid #bbdefb;
}

.btn-action-table.btn-edit:hover {
  background: #bbdefb;
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
  background: linear-gradient(135deg, #667eea, #764ba2);
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
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.form-help-full {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding: 1rem;
  background: #e3f2fd;
  border-radius: 6px;
  border-left: 4px solid #1976d2;
}

.form-help-full i {
  color: #1976d2;
  font-size: 1.2rem;
  margin-top: 0.1rem;
}

.form-help-full span {
  color: #0d47a1;
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
  background: linear-gradient(135deg, #667eea, #764ba2);
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
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-save:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-group-small {
  display: flex;
  gap: 0.25rem;
}

.btn-sm {
  padding: 0.375rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-edit {
  background: #e3f2fd;
  color: #1976d2;
}

.btn-edit:hover {
  background: #bbdefb;
}

.btn-delete {
  background: #ffebee;
  color: #d32f2f;
}

.btn-delete:hover {
  background: #ffcdd2;
}

/* ============ FORMULARIOS ============ */
.ruta-form {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  margin-top: 1rem;
}

.ruta-form h4 {
  margin: 0 0 1rem 0;
  color: #495057;
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
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: border-color 0.3s;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

.btn-secondary {
  padding: 0.75rem 1rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: #5a6268;
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
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.filter-stats {
  display: flex;
  align-items: center;
}

.stats-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #e3f2fd;
  color: #1976d2;
  border: 1px solid #bbdefb;
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

.archivos-table-full .clasificacion-col {
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
  color: #1976d2;
  font-size: 1.2rem;
}

.clasificacion-cell {
  padding: 1rem;
}

.clasificacion-badge {
  display: inline-block;
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.375rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  border: 1px solid #bbdefb;
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

/* Responsive para botones CSV */
@media (max-width: 768px) {
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
  
  .modal-content {
    margin: 0.5rem;
    max-width: calc(100vw - 1rem);
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
  
  .filter-tags {
    flex-direction: column;
    align-items: flex-start;
  }
  
  /* Tabla responsive para móviles - RUTAS */
  .rutas-table-container-full {
    overflow-x: auto;
  }
  
  .rutas-table-full .ruta-col {
    min-width: 300px;
    width: 50%;
  }
  
  .path-text-full {
    font-size: 0.8rem;
    padding: 0.5rem;
    max-height: 80px;
  }
  
  /* Responsive para ARCHIVOS móviles */
  .archivos-filters-full {
    grid-template-columns: 1fr;
    gap: 1rem;
    padding: 1rem;
  }
  
  .filter-stats {
    grid-column: 1 / -1;
    justify-content: center;
    margin-top: 1rem;
  }
  
  .archivos-table-container-full {
    overflow-x: auto;
  }
  
  .archivos-table-full .nombre-col {
    min-width: 150px;
  }
  
  .archivos-table-full .clasificacion-col {
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
  
  .archivo-nombre {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  /* Botones y formularios responsive */
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
  
  .form-header {
    padding: 1rem 1.5rem;
  }
  
  .form-header h4 {
    font-size: 1.1rem;
  }
  
  .empty-simple {
    padding: 1.5rem;
    text-align: center;
  }
  
  .empty-simple h4 {
    font-size: 1.1rem;
    margin: 1rem 0 0.5rem 0;
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