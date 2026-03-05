<template>
  <div class="conceptos-list-container">
    <div class="header-section">
      <h2 class="page-title">Consulta de Conceptos</h2>
      <div class="actions-bar">
        <button class="btn btn-primary" @click="navigateToCreate">
          <i class="material-icons">add</i>
          Crear Nuevo Concepto
        </button>
        <button class="btn btn-secondary" @click="exportarDatos" :disabled="!conceptosFiltrados.length">
          <i class="material-icons">file_download</i>
          Exportar Resultados
        </button>
      </div>
    </div>
  
    <!-- Filtros jerárquicos -->
    <div class="filtros-section">
      <div class="row">
        <div class="col-md-6 col-lg-3">
          <div class="form-group">
            <label for="departamento">Departamento:</label>
            <select 
              id="departamento" 
              v-model="filtros.departamento" 
              @change="cargarMunicipios"
              class="form-control"
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
        </div>
        
        <div class="col-md-6 col-lg-3">
          <div class="form-group">
            <label for="municipio">Municipio:</label>
            <select 
              id="municipio" 
              v-model="filtros.municipio" 
              @change="cargarInsumos"
              class="form-control"
              :disabled="!filtros.departamento || municipios.length === 0"
            >
              <option value="">Todos los municipios</option>
              <option 
                v-for="municipio in municipios" 
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
              @change="cargarClasificaciones"
              class="form-control"
              :disabled="!filtros.municipio || insumos.length === 0"
            >
              <option value="">Todos los insumos</option>
              <option 
                v-for="insumo in insumosConCategoria" 
                :key="insumo.cod_insumo" 
                :value="insumo.cod_insumo"
              >
                {{ insumo.cod_insumo }} - {{ insumo.tipo_insumo }} ({{ insumo.categoria_nombre }})
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
              @change="cargarDetalles"
              class="form-control"
              :disabled="!filtros.insumo || clasificaciones.length === 0"
            >
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
        </div>
      </div>

      <!-- ÚNICO FILTRO PARA DETALLE_INSUMO QUE SOLO MUESTRA LOS REGISTROS EXISTENTES -->
      <div class="row">
        <div class="col-12">
          <div class="form-group">
            <label for="detalle">Detalle Insumo:</label>
            <select 
              id="detalle" 
              v-model="filtros.detalle" 
              class="form-control"
              :disabled="!filtros.clasificacion || detalles.length === 0"
            >
              <option value="">Seleccionar detalle...</option>
              <option 
                v-for="detalle in detalles" 
                :key="detalle.cod_detalle" 
                :value="detalle.cod_detalle"
              >
                {{ detalle.cod_detalle }} - Escala: {{ detalle.escala || 'N/A' }} - Estado: {{ detalle.estado || 'N/A' }} - Entidad: {{ detalle.cod_entidad || 'N/A' }} - Formato: {{ detalle.formato_tipo || 'N/A' }}
              </option>
            </select>
          </div>
        </div>
      </div>
  
      <div class="filtros-buttons">
        <button class="btn btn-primary" @click="aplicarFiltros">
          <i class="material-icons">filter_list</i>
          Aplicar Filtros
        </button>
        <button class="btn btn-secondary" @click="limpiarFiltros">
          <i class="material-icons">clear_all</i>
          Limpiar Filtros
        </button>
      </div>
    </div>

    <!-- Estado de carga y mensajes -->
    <div v-if="cargando" class="loading-container">
      <div class="spinner"></div>
      <span class="loading-text">Cargando conceptos...</span>
    </div>
  
    <div v-else-if="error" class="error-container">
      <i class="material-icons">error</i>
      <span>{{ error }}</span>
      <button class="btn btn-primary" @click="cargarConceptos">Reintentar</button>
    </div>
  
    <div v-else-if="conceptosFiltrados.length === 0" class="empty-container">
      <i class="material-icons">info</i>
      <span>No se encontraron conceptos con los filtros seleccionados</span>
    </div>
  
    <!-- Tabla de resultados -->
    <div v-else class="results-container">
      <div class="results-header">
        <h3 class="results-title">Resultados</h3>
        <span class="results-count">{{ conceptosFiltrados.length }} conceptos encontrados</span>
      </div>
  
      <div class="table-responsive">
        <table class="table table-striped table-hover">
          <thead>
            <tr>
              <th @click="ordenarPor('cod_concepto')">
                Código
                <i v-if="ordenacion.campo === 'cod_concepto'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('concepto')">
                Concepto
                <i v-if="ordenacion.campo === 'concepto'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('fecha')">
                Fecha
                <i v-if="ordenacion.campo === 'fecha'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('evaluacion')">
                Evaluación
                <i v-if="ordenacion.campo === 'evaluacion'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              
              <th @click="ordenarPor('municipio')">
                Municipio
                <i v-if="ordenacion.campo === 'municipio'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="concepto in conceptosVisibles" :key="concepto.cod_concepto">
              <td>{{ concepto.cod_concepto }}</td>
              <td>
                <span class="concepto-texto">{{ limitarTexto(concepto.concepto, 50) }}</span>
              </td>
              <td>{{ formatFecha(concepto.fecha) }}</td>
              <td>
                <span class="badge-text" :class="getEvaluacionClass(concepto.evaluacion)">
                  {{ concepto.evaluacion || 'Sin evaluar' }}
                </span>
              </td>
              <td>
                <span v-if="concepto.municipio">{{ concepto.municipio }}</span>
                <span v-else class="text-muted">No disponible</span>
              </td>
              <td class="actions-column">
                <div class="actions-buttons">
                  <button class="btn-icon" @click="verConcepto(concepto)" title="Ver detalle">
                    <i class="material-icons">visibility</i>
                  </button>
                  <button class="btn-icon" @click="editarConcepto(concepto)" title="Editar">
                    <i class="material-icons">edit</i>
                  </button>
                  <button class="btn-icon btn-danger" @click="confirmarEliminar(concepto)" title="Eliminar">
                    <i class="material-icons">delete</i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
  
      <!-- Paginación -->
      <div class="pagination-container" v-if="totalPaginas > 1">
        <button 
          class="btn-pagination" 
          @click="cambiarPagina(paginaActual - 1)" 
          :disabled="paginaActual === 1"
        >
          <i class="material-icons">navigate_before</i>
        </button>
        
        <button 
          v-for="pagina in botonesNumericos" 
          :key="pagina.valor"
          class="btn-pagination" 
          :class="{ active: pagina.activo, disabled: pagina.ellipsis }"
          @click="pagina.ellipsis ? null : cambiarPagina(pagina.valor)"
        >
          {{ pagina.texto }}
        </button>
        
        <button 
          class="btn-pagination" 
          @click="cambiarPagina(paginaActual + 1)" 
          :disabled="paginaActual === totalPaginas"
        >
          <i class="material-icons">navigate_next</i>
        </button>
      </div>
    </div>
  
    <!-- Modal de conceptos mejorado -->
    <div class="modal fixed-modal" v-if="modalConcepto.mostrar">
      <div class="modal-dialog modal-compact">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">Concepto {{ modalConcepto.concepto?.cod_concepto }}</h4>
            <button class="close-button" @click="cerrarModalConcepto">
              <i class="material-icons">close</i>
            </button>
          </div>
          <div class="modal-body">
            <div v-if="modalConcepto.concepto" class="concepto-info">
              <!-- Título e información principal -->
              <div class="concepto-form">
                <div class="form-row">
                  <div class="form-field">
                    <label>Concepto:</label>
                    <div class="field-value">{{ modalConcepto.concepto.concepto }}</div>
                  </div>
                  <div class="form-field">
                    <label>Fecha:</label>
                    <div class="field-value">{{ formatFecha(modalConcepto.concepto.fecha) }}</div>
                  </div>
                </div>
                
              <div class="form-row">
                <div class="form-field">
                  <label>Municipio:</label>
                  <div class="field-value">{{ modalConcepto.concepto.municipio || 'N/A' }}</div>
                </div>
                <div class="form-field">
                  <label>Evaluación:</label>
                  <div class="field-value">
                    <span class="badge-text" :class="getEvaluacionClass(modalConcepto.concepto.evaluacion)">
                      {{ modalConcepto.concepto.evaluacion || 'Sin evaluar' }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Nueva fila para centro poblado (solo se muestra si existe) -->
              <div class="form-row" v-if="modalConcepto.concepto.centro_poblado_nombre">
                <div class="form-field">
                  <label>Centro Poblado:</label>
                  <div class="field-value">
                    {{ modalConcepto.concepto.centro_poblado_nombre }}
                    <span class="text-muted">({{ modalConcepto.concepto.centro_poblado_codigo }})</span>
                  </div>
                </div>
                <div class="form-field">
                  <!-- Espacio vacío para mantener la alineación -->
                </div>
              </div>
                
                <div class="form-row">
                  <div class="form-field">
                    <label>Detalle asociado:</label>
                    <div class="field-value">{{ modalConcepto.concepto.detalle_id || 'N/A' }}</div>
                  </div>
                </div>
                
                <div class="form-row full-width">
                  <div class="form-field">
                    <label>Detalle del concepto:</label>
                    <div class="field-value text-area">{{ modalConcepto.concepto.detalle_concepto || 'Sin detalle' }}</div>
                  </div>
                </div>
                
                <div class="form-row full-width">
                  <div class="form-field">
                    <label>Observaciones:</label>
                    <div class="field-value text-area">{{ modalConcepto.concepto.observacion || 'Sin observaciones' }}</div>
                  </div>
                </div>
                
                <!-- Información técnica -->
                <div class="form-section">
                  <h6>Información técnica:</h6>
                  
                  <div class="form-row">
                    <div class="form-field">
                      <label>Código concepto:</label>
                      <div class="field-value">{{ modalConcepto.concepto.cod_concepto }}</div>
                    </div>
                    <div class="form-field">
                      <label>Código detalle:</label>
                      <div class="field-value">{{ modalConcepto.concepto.cod_detalle }}</div>
                    </div>
                  </div>
                  
                  <div class="form-row">
                    <div class="form-field">
                      <label>Código insumo:</label>
                      <div class="field-value">{{ modalConcepto.concepto.cod_insumo }}</div>
                    </div>
                    <div class="form-field">
                      <label>Código clasificación:</label>
                      <div class="field-value">{{ modalConcepto.concepto.cod_clasificacion }}</div>
                    </div>
                  </div>
                  
                  <div class="form-row">
                    <div class="form-field">
                      <label>Código municipio:</label>
                      <div class="field-value">{{ modalConcepto.concepto.cod_municipio }}</div>
                    </div>
                  </div>
                </div>
                
                <!-- Sección de documento PDF -->
                <div class="form-section" v-if="modalConcepto.concepto.pdf">
                  <h6>Documento PDF:</h6>
                  
                  <!-- Agregamos la ruta completa -->
                  <div class="form-row full-width">
                    <div class="form-field">
                      <label>Ruta completa:</label>
                      <div class="field-value text-area">{{ modalConcepto.concepto.pdf }}</div>
                    </div>
                  </div>
                  
                  <div class="form-row">
                    <div class="form-field full-width">
                      <div class="pdf-container">
                        <div class="pdf-info">
                          <i class="material-icons">description</i>
                          <span>{{ obtenerNombreArchivo(modalConcepto.concepto.pdf) }}</span>
                        </div>
                        <div class="pdf-actions">
                          <button class="btn btn-sm btn-primary" @click="descargarPdf(modalConcepto.concepto)">
                            <i class="material-icons">download</i> Descargar PDF
                          </button>
                          <button class="btn btn-sm btn-secondary" @click="verPdfEnNuevaPestana(modalConcepto.concepto)">
                            <i class="material-icons">visibility</i> Ver en nueva pestaña
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="modal-footer">
            <button class="btn btn-primary" @click="editarConcepto(modalConcepto.concepto)">
              <i class="material-icons">edit</i> Editar
            </button>
            <button class="btn btn-secondary" @click="cerrarModalConcepto">
              <i class="material-icons">close</i> Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/store/auth';
import axios from 'axios';


// URL base para las API
import api, { API_URL } from '@/api/config';

export default {
  name: 'ConceptosList',
  
  setup() {
    const router = useRouter();
    const route = useRoute();
    const authStore = useAuthStore();
    
    // Estado para visualización de PDF
    const mostrandoPdf = ref(false);
    const pdfUrl = ref(null);
    const pdfCargando = ref(false);
    const pdfError = ref(null);
    
    // Estado de carga y errores
    const cargando = ref(false);
    const error = ref(null);
    
    // Datos para la tabla
    const conceptos = ref([]);
    const conceptosFiltradosManual = ref([]);
    
    // Catálogos y listas de referencia
    const departamentos = ref([]);
    const municipios = ref([]);
    const insumos = ref([]);
    const clasificaciones = ref([]);
    const detalles = ref([]);
    
    // Filtros de búsqueda
    const filtros = ref({
      departamento: '',
      municipio: '',
      insumo: '',
      clasificacion: '',
      detalle: ''
    });
    
    // Estado para indicar si algún filtro jerárquico está activo
    const filtrosJerarquicosActivos = ref(false);
    
    // Ordenación
    const ordenacion = ref({
      campo: 'cod_concepto',
      ascendente: true
    });
    
    // Paginación
    const paginaActual = ref(1);
    const elementosPorPagina = ref(10);
    
    // Modales
    const modalEliminar = ref({
      mostrar: false,
      concepto: null
    });
    
    const modalConcepto = ref({
      mostrar: false,
      concepto: null
    });
    // Función para cerrar el modal del concepto

    // Función recursiva para cargar TODOS los datos sin importar la paginación
    const cargarTodosLosDatos = async (url, params = {}) => {
      try {
        // Array para almacenar todos los resultados
        let todosLosResultados = [];
        // URL inicial
        let urlActual = url;
        
        // Añadir parámetros iniciales a la URL
        if (Object.keys(params).length > 0) {
          const queryParams = new URLSearchParams(params).toString();
          urlActual = `${url}?${queryParams}`;
        }
        
        // Primera llamada para obtener el total de elementos
        const primeraRespuesta = await axios.get(urlActual);
        
        // Verificar si la respuesta ya es un array simple (sin paginación)
        if (Array.isArray(primeraRespuesta.data)) {
          console.log(`Recibidos ${primeraRespuesta.data.length} elementos (sin paginación)`);
          return primeraRespuesta.data;
        }
        
        // Si hay resultados paginados, obtener la primera página
        if (primeraRespuesta.data.results) {
          todosLosResultados = [...primeraRespuesta.data.results];
          
          // Calcular el número total de elementos
          const count = primeraRespuesta.data.count || 0;
          console.log(`Total de elementos a cargar: ${count}`);
          
          // Si ya tenemos todos los elementos, terminar
          if (todosLosResultados.length >= count) {
            return todosLosResultados;
          }
          
          // Calcular cuántas páginas necesitamos cargar
          const pageSize = primeraRespuesta.data.results.length;
          const totalPages = Math.ceil(count / pageSize);
          
          // Preparar todas las peticiones para las páginas restantes
          const promesas = [];
          for (let pagina = 2; pagina <= totalPages; pagina++) {
            // Construir URL con parámetro de página
            let urlPagina = `${url}?page=${pagina}`;
            
            // Añadir otros parámetros si existen
            if (Object.keys(params).length > 0) {
              const otrosParams = new URLSearchParams(params).toString();
              urlPagina = `${url}?${otrosParams}&page=${pagina}`;
            }
            
            promesas.push(axios.get(urlPagina));
          }
          
          // Ejecutar todas las peticiones en paralelo
          const respuestas = await Promise.all(promesas);
          
          // Procesar todas las respuestas y añadir los resultados
          respuestas.forEach(respuesta => {
            if (respuesta.data && respuesta.data.results) {
              todosLosResultados = [...todosLosResultados, ...respuesta.data.results];
            }
          });
          
          return todosLosResultados;
        } else {
          return [];
        }
      } catch (error) {
        console.error(`Error cargando datos de ${url}:`, error);
        throw error;
      }
    };

    // Función para manejar el evento de teclado Escape
    const handleEscKeypress = (event) => {
      if (event.key === 'Escape') {
        if (mostrandoPdf.value) {
          cerrarPdf();
        } else if (modalConcepto.value.mostrar) {
          cerrarModalConcepto();
        }
      }
    };
    
    // Función para cerrar el modal del concepto
    // Función para cerrar el modal del concepto
    const cerrarModalConcepto = () => {
      document.removeEventListener('keydown', handleEscKeypress);
      modalConcepto.value.mostrar = false;
    };
    
    // Función para visualizar el PDF
    const verPdf = async (concepto) => {
      if (!concepto.pdf) {
        alert('No hay archivo PDF asociado a este concepto.');
        return;
      }
      
      try {
        pdfCargando.value = true;
        pdfError.value = null;
        mostrandoPdf.value = true;
        
        // Agregar event listener para la tecla Escape
        document.addEventListener('keydown', handleEscKeypress);
        
        // Obtener token de autenticación
        const token = localStorage.getItem('token');
        if (!token) {
          throw new Error('No hay token de autenticación. Por favor, inicie sesión nuevamente.');
        }
        
        // Construir la URL para el endpoint del backend
        const rutaCompleta = concepto.pdf;
        
        // Usar el endpoint existente en el backend
        // Intentamos primero una llamada de prueba para verificar que el PDF es accesible
        try {
          await axios.get(`${API_URL}/verificar_pdf/`, {
            method: 'POST',
            headers: {
              'Authorization': `Token ${token}`,
              'Content-Type': 'application/json'
            },
            data: JSON.stringify({
              ruta_pdf: rutaCompleta
            })
          });
          
          // Si llegamos aquí, el PDF existe y podemos mostrarlo
          // Generamos la URL completa para el endpoint ver_pdf
          pdfUrl.value = `${API_URL}/ver_pdf/?ruta=${encodeURIComponent(rutaCompleta)}&token=${token}`;
          
        } catch (error) {
          console.error('Error verificando PDF:', error);
          
          // Si hay un error específico de la verificación
          if (error.response && error.response.data) {
            pdfError.value = `Error verificando PDF: ${error.response.data.error || JSON.stringify(error.response.data)}`;
          } else {
            pdfError.value = `Error verificando PDF: ${error.message}`;
          }
          
          // Intentamos directamente con el endpoint ver_pdf como fallback
          pdfUrl.value = `${API_URL}/ver_pdf/?ruta=${encodeURIComponent(rutaCompleta)}&token=${token}`;
        }
        
      } catch (error) {
        console.error('Error general al mostrar PDF:', error);
        pdfError.value = `Error al preparar la visualización del PDF: ${error.message}`;
      } finally {
        pdfCargando.value = false;
      }
    };
    
    // Función para cerrar el visor de PDF
    const cerrarPdf = () => {
      document.removeEventListener('keydown', handleEscKeypress);
      mostrandoPdf.value = false;
      pdfUrl.value = null;
      pdfError.value = null;
    };
    
    // Obtener nombre del archivo desde una ruta completa

    
    // Cargar departamentos
    const cargarDepartamentos = async () => {
      try {
        console.log('Cargando departamentos...');
        const resultado = await cargarTodosLosDatos(`${API_URL}/preoperacion/departamentos/`);
        departamentos.value = resultado;
        console.log(`Cargados ${departamentos.value.length} departamentos`);
      } catch (err) {
        console.error('Error al cargar departamentos:', err);
        error.value = 'Error al cargar departamentos.';
      }
    };
    
    // Ver concepto completo
const verConcepto = async (concepto) => {
  try {
    // Crear una copia del concepto para enriquecerlo
    let conceptoEnriquecido = { ...concepto };
    
    // Si el concepto tiene un cod_detalle, buscar información adicional
    if (concepto.cod_detalle) {
      try {
        // Obtener el detalle completo
        const detalleResponse = await axios.get(
          `${API_URL}/preoperacion/detalles-insumo/${concepto.cod_detalle}/`
        );
        
        const detalle = detalleResponse.data;
        
        // Si el detalle tiene un centro poblado, obtener su nombre
        if (detalle.cod_centro_poblado) {
          try {
            const centroPobladoResponse = await axios.get(
              `${API_URL}/preoperacion/centros-poblados/${detalle.cod_centro_poblado}/`
            );
            
            // Agregar la información del centro poblado al concepto
            conceptoEnriquecido.centro_poblado_codigo = detalle.cod_centro_poblado;
            conceptoEnriquecido.centro_poblado_nombre = centroPobladoResponse.data.nom_centro_poblado;
          } catch (error) {
            console.error('Error al obtener centro poblado:', error);
          }
        }
      } catch (error) {
        console.error('Error al obtener detalle:', error);
      }
    }
    
    // Asignar el concepto enriquecido al modal
    modalConcepto.value.concepto = conceptoEnriquecido;
    modalConcepto.value.mostrar = true;
    
    // Agregar event listener para la tecla Escape
    document.addEventListener('keydown', handleEscKeypress);
  } catch (error) {
    console.error('Error al procesar concepto:', error);
    // En caso de error, mostrar el concepto original
    modalConcepto.value.concepto = concepto;
    modalConcepto.value.mostrar = true;
    document.addEventListener('keydown', handleEscKeypress);
  }
};

    // Cargar municipios
    const cargarMunicipios = async () => {
      municipios.value = [];
      filtros.value.municipio = '';
      filtros.value.insumo = '';
      filtros.value.clasificacion = '';
      filtros.value.detalle = '';
      
      if (!filtros.value.departamento) {
        // Si no hay departamento seleccionado, mostrar todos los conceptos
        conceptosFiltradosManual.value = conceptos.value;
        filtrosJerarquicosActivos.value = false;
        return;
      }
      
      try {
        console.log(`Cargando municipios del departamento ${filtros.value.departamento}...`);
        const params = { cod_depto: filtros.value.departamento };
        const resultado = await cargarTodosLosDatos(`${API_URL}/preoperacion/municipios/`, params);
        municipios.value = resultado;
        console.log(`Cargados ${municipios.value.length} municipios`);
        
        // Aplicar filtrado por departamento
        filtrosJerarquicosActivos.value = true;
        await aplicarFiltrosJerarquicos();
        
      } catch (err) {
        console.error('Error al cargar municipios:', err);
        error.value = 'Error al cargar municipios.';
      }
    };
    
    // Cargar insumos
    const cargarInsumos = async () => {
      insumos.value = [];
      filtros.value.insumo = '';
      filtros.value.clasificacion = '';
      filtros.value.detalle = '';
      
      if (!filtros.value.municipio) {
        // Si no hay municipio seleccionado, filtrar solo por departamento
        await aplicarFiltrosJerarquicos();
        return;
      }
      
      try {
        console.log(`Cargando insumos del municipio ${filtros.value.municipio}...`);
        const insumosData = await cargarTodosLosDatos(
          `${API_URL}/preoperacion/municipios/${filtros.value.municipio}/insumos/`
        );
        
        // Obtener categoría para cada insumo
        const insumosConCategorias = await Promise.all(insumosData.map(async (insumo) => {
          try {
            // Si ya tiene la información de categoría, usarla
            if (insumo.categoria && insumo.categoria.nom_categoria) {
              return {
                ...insumo,
                categoria_nombre: insumo.categoria.nom_categoria
              };
            }
            
            // Si no, intentar obtenerla
            const categoriaResponse = await axios.get(
              `${API_URL}/preoperacion/categorias/${insumo.cod_categoria}/`
            );
            return {
              ...insumo,
              categoria_nombre: categoriaResponse.data.nom_categoria
            };
          } catch (error) {
            console.error(`Error al obtener categoría para insumo ${insumo.cod_insumo}:`, error);
            return {
              ...insumo,
              categoria_nombre: 'Categoría no disponible'
            };
          }
        }));
        
        insumos.value = insumosConCategorias;
        console.log(`Cargados ${insumos.value.length} insumos`);
        
        // Aplicar filtrado por municipio
        await aplicarFiltrosJerarquicos();
        
      } catch (err) {
        console.error('Error al cargar insumos:', err);
        error.value = 'Error al cargar insumos.';
      }
    };
    
    // ✅ FUNCIÓN PARA VER PDF EN NUEVA PESTAÑA (CORREGIDA)
const verPdfEnNuevaPestana = async (concepto) => {
  if (!concepto.pdf) {
    alert('No hay archivo PDF asociado a este concepto.');
    return;
  }
  
  try {
    console.log('🔍 Abriendo PDF en nueva pestaña:', concepto.pdf);
    
    // ✅ USAR API CONFIGURADA CON TOKEN AUTOMÁTICO (igual que en InsumosList.vue)
    const response = await api.get('/preoperacion/ver_pdf/', {
      params: { ruta: concepto.pdf },
      responseType: 'blob'
    });
    
    // Crear URL del blob para visualización segura
    const blob = new Blob([response], { 
      type: response.type || 'application/pdf' 
    });
    const url = window.URL.createObjectURL(blob);
    
    // Abrir en nueva ventana
    window.open(url, '_blank');
    
    // Limpiar URL después de un tiempo
    setTimeout(() => {
      window.URL.revokeObjectURL(url);
    }, 10000);
    
    console.log('✅ PDF abierto en nueva ventana');
    
  } catch (error) {
    console.error('❌ Error al abrir PDF:', error);
    
    if (error.response?.status === 404) {
      alert('El archivo PDF no se encontró en el servidor.');
    } else if (error.response?.status === 403) {
      alert('No tiene permisos para acceder a este archivo.');
    } else {
      alert('Error al abrir el archivo PDF. Por favor, inténtelo de nuevo.');
    }
  }
};

    // Cargar clasificaciones
    const cargarClasificaciones = async () => {
      clasificaciones.value = [];
      filtros.value.clasificacion = '';
      filtros.value.detalle = '';
      
      if (!filtros.value.insumo) {
        // Si no hay insumo seleccionado, filtrar por municipio
        await aplicarFiltrosJerarquicos();
        return;
      }
      
      try {
        console.log(`Cargando clasificaciones del insumo ${filtros.value.insumo}...`);
        const resultado = await cargarTodosLosDatos(
          `${API_URL}/preoperacion/insumos/${filtros.value.insumo}/clasificaciones/`
        );
        clasificaciones.value = resultado;
        console.log(`Cargadas ${clasificaciones.value.length} clasificaciones`);
        
        // Aplicar filtrado por insumo
        await aplicarFiltrosJerarquicos();
        
      } catch (err) {
        console.error('Error al cargar clasificaciones:', err);
        error.value = 'Error al cargar clasificaciones.';
      }
    };
    
    // Cargar detalles
    const cargarDetalles = async () => {
      detalles.value = [];
      filtros.value.detalle = '';
      
      if (!filtros.value.clasificacion) {
        // Si no hay clasificación seleccionada, filtrar por insumo
        await aplicarFiltrosJerarquicos();
        return;
      }
      
      try {
        console.log(`Cargando detalles de la clasificación ${filtros.value.clasificacion}...`);
        const resultado = await cargarTodosLosDatos(
          `${API_URL}/preoperacion/detalles-insumo/`,
          { cod_clasificacion: filtros.value.clasificacion }
        );
        
        detalles.value = resultado;
        console.log(`Cargados ${detalles.value.length} detalles`);
        
        // Aplicar filtrado por clasificación
        await aplicarFiltrosJerarquicos();
        
      } catch (err) {
        console.error('Error al cargar detalles:', err);
        error.value = 'Error al cargar detalles.';
      }
    };
    
    // Aplicar filtros jerárquicos manualmente
    // Improved version of aplicarFiltrosJerarquicos function:
    const aplicarFiltrosJerarquicos = async () => {
      try {
        cargando.value = true;
        error.value = null;
        
        console.log("Applying hierarchical filters with:", filtros.value);
        
        // Special approach for detail - if we have a selected detail, ignore other filters
        // and search directly by that detail
        if (filtros.value.detalle) {
          try {
            // Directly search for the concept associated with this detail
            const response = await axios.get(`${API_URL}/preoperacion/conceptos/buscar/?detalle=${filtros.value.detalle}`);
            conceptosFiltradosManual.value = await enrichConceptsWithInfo(response.data);
            console.log(`Found ${conceptosFiltradosManual.value.length} concepts for detail ${filtros.value.detalle}`);
          } catch (error) {
            console.error("Error getting concepts by detail:", error);
            conceptosFiltradosManual.value = [];
          }
        } else {
          // If no detail is selected, use the normal hierarchical approach
          try {
            // Build URL with applied filters
            let url = `${API_URL}/preoperacion/conceptos/buscar/?`;
            let params = [];
            
            if (filtros.value.departamento) {
              params.push(`departamento=${filtros.value.departamento}`);
            }
            
            if (filtros.value.municipio) {
              params.push(`municipio=${filtros.value.municipio}`);
            }
            
            if (filtros.value.insumo) {
              params.push(`insumo=${filtros.value.insumo}`);
            }
            
            if (filtros.value.clasificacion) {
              params.push(`clasificacion=${filtros.value.clasificacion}`);
            }
            
            url += params.join('&');
            console.log("Search URL:", url);
            
            const response = await axios.get(url);
            // Enrich the data with municipality names and other information
            conceptosFiltradosManual.value = await enrichConceptsWithInfo(response.data);
            console.log(`Found ${conceptosFiltradosManual.value.length} concepts with selected filters`);
          } catch (error) {
            console.error("Error in hierarchical search:", error);
            conceptosFiltradosManual.value = [];
          }
        }
      } catch (err) {
        console.error("General error applying filters:", err);
        error.value = "Error applying filters";
        conceptosFiltradosManual.value = [];
      } finally {
        cargando.value = false;
      }
    };

    // New helper function to enrich concepts with additional info
    const enrichConceptsWithInfo = async (concepts) => {
      if (!concepts || concepts.length === 0) return [];
      
      const enrichedConcepts = await Promise.all(concepts.map(async (concept) => {
        try {
          // If municipality info is missing, try to fetch it
          if (!concept.municipio) {
            // First check if we have cod_municipio directly
            if (concept.cod_municipio) {
              try {
                const municipioResponse = await axios.get(
                  `${API_URL}/preoperacion/municipios/${concept.cod_municipio}/`
                );
                concept.municipio = municipioResponse.data.nom_municipio;
              } catch (err) {
                console.warn(`Could not fetch municipality info for cod_municipio ${concept.cod_municipio}:`, err);
              }
            } 
            // If not, try to find through detalle -> clasificacion -> insumo -> municipio
            else if (concept.cod_detalle) {
              try {
                const detalleResponse = await axios.get(
                  `${API_URL}/preoperacion/detalles-insumo/${concept.cod_detalle}/`
                );
                
                const detalle = detalleResponse.data;
                if (detalle.cod_clasificacion) {
                  const clasificacionResponse = await axios.get(
                    `${API_URL}/preoperacion/clasificaciones/${detalle.cod_clasificacion}/`
                  );
                  
                  const clasificacion = clasificacionResponse.data;
                  if (clasificacion.cod_insumo) {
                    const insumoResponse = await axios.get(
                      `${API_URL}/preoperacion/insumos/${clasificacion.cod_insumo}/`
                    );
                    
                    const insumo = insumoResponse.data;
                    if (insumo.cod_municipio) {
                      const municipioResponse = await axios.get(
                        `${API_URL}/preoperacion/municipios/${insumo.cod_municipio}/`
                      );
                      
                      concept.municipio = municipioResponse.data.nom_municipio;
                      concept.cod_municipio = insumo.cod_municipio;
                      concept.cod_insumo = insumo.cod_insumo;
                      concept.cod_clasificacion = clasificacion.cod_clasificacion;
                      concept.cod_departamento = municipioResponse.data.cod_depto.cod_depto;
                    }
                  }
                }
              } catch (err) {
                console.warn(`Could not fetch related info for concept ${concept.cod_concepto}:`, err);
              }
            }
          }
          
          return concept;
        } catch (err) {
          console.warn(`Error enriching concept ${concept.cod_concepto}:`, err);
          return concept;
        }
      }));
      
      return enrichedConcepts;
    };
    
    // Cargar conceptos
    // Improved cargarConceptos function
    const cargarConceptos = async () => {
      error.value = null;
      
      try {
        cargando.value = true;
        console.log('Loading concepts...');
        
        // Reset hierarchical filters
        filtrosJerarquicosActivos.value = false;
        
        // Use a more robust approach to get ALL concepts without pagination issues
        const conceptosData = await cargarTodosLosDatos(`${API_URL}/preoperacion/conceptos/`);
        
        console.log(`Loaded ${conceptosData.length} concepts`);
        
        // Update the concepts
        conceptos.value = conceptosData;
        
        // Initially, enrich and show all concepts
        conceptos.value = await enrichConceptsWithInfo(conceptosData);
        conceptosFiltradosManual.value = conceptos.value;
        
        // Reset pagination
        paginaActual.value = 1;
        
      } catch (err) {
        console.error('Error loading concepts:', err);
        error.value = 'Error loading concepts. Please try again.';
      } finally {
        cargando.value = false;
      }
    };
    // Insumos con categoría nombre
    const insumosConCategoria = computed(() => {
      return insumos.value.map(insumo => {
        // Si el insumo ya tiene la categoría nombre, utilizarlo
        if (insumo.categoria_nombre) {
          return insumo;
        }
        
        // Si no, intentar obtenerlo de la propiedad categoria
        if (insumo.categoria && insumo.categoria.nom_categoria) {
          return {
            ...insumo,
            categoria_nombre: insumo.categoria.nom_categoria
          };
        }
        
        // Si no encontramos la categoría, usar un valor por defecto
        return {
          ...insumo,
          categoria_nombre: 'Categoría no disponible'
        };
      });
    });
    
    // Aplicar filtros a los conceptos - usar conceptosFiltradosManual en lugar de conceptos
    const conceptosFiltrados = computed(() => {
      return conceptosFiltradosManual.value;
    });
    
    // Elementos visibles en la página actual
    const conceptosVisibles = computed(() => {
      const inicio = (paginaActual.value - 1) * elementosPorPagina.value;
      const fin = inicio + elementosPorPagina.value;
      return conceptosFiltrados.value.slice(inicio, fin);
    });
    
    // Total de páginas
    const totalPaginas = computed(() => {
      return Math.ceil(conceptosFiltrados.value.length / elementosPorPagina.value) || 1;
    });
    
    // Botones numéricos para paginación
    const botonesNumericos = computed(() => {
      const botones = [];
      const maxBotones = 5; // Número máximo de botones a mostrar
      
      if (totalPaginas.value <= maxBotones) {
        // Si hay pocas páginas, mostrarlas todas
        for (let i = 1; i <= totalPaginas.value; i++) {
          botones.push({
            valor: i,
            texto: i.toString(),
            activo: i === paginaActual.value,
            ellipsis: false
          });
        }
      } else {
        // Siempre mostrar la primera página
        botones.push({
          valor: 1,
          texto: '1',
          activo: paginaActual.value === 1,
          ellipsis: false
        });
        
        // Calcular el rango de páginas a mostrar alrededor de la página actual
        let inicio = Math.max(2, paginaActual.value - 1);
        let fin = Math.min(totalPaginas.value - 1, paginaActual.value + 1);
        
        // Ajustar si estamos cerca del principio
        if (paginaActual.value <= 3) {
          fin = Math.min(4, totalPaginas.value - 1);
        }
        
        // Ajustar si estamos cerca del final
        if (paginaActual.value >= totalPaginas.value - 2) {
          inicio = Math.max(2, totalPaginas.value - 3);
        }
        
        // Mostrar elipsis si hay salto al principio
        if (inicio > 2) {
          botones.push({
            valor: null,
            texto: '...',
            activo: false,
            ellipsis: true
          });
        }
        
        // Mostrar páginas centrales
        for (let i = inicio; i <= fin; i++) {
          botones.push({
            valor: i,
            texto: i.toString(),
            activo: i === paginaActual.value,
            ellipsis: false
          });
        }
        
        // Mostrar elipsis si hay salto al final
        if (fin < totalPaginas.value - 1) {
          botones.push({
            valor: null,
            texto: '...',
            activo: false,
            ellipsis: true
          });
        }
        
        // Siempre mostrar la última página
        if (totalPaginas.value > 1) {
          botones.push({
            valor: totalPaginas.value,
            texto: totalPaginas.value.toString(),
            activo: paginaActual.value === totalPaginas.value,
            ellipsis: false
          });
        }
      }
      
      return botones;
    });
    
    // Cambiar página
    const cambiarPagina = (pagina) => {
      if (pagina >= 1 && pagina <= totalPaginas.value) {
        paginaActual.value = pagina;
      }
    };
    
    // Ordenar por campo
    const ordenarPor = (campo) => {
      if (ordenacion.value.campo === campo) {
        // Si ya estamos ordenando por este campo, invertir dirección
        ordenacion.value.ascendente = !ordenacion.value.ascendente;
      } else {
        // Si es un nuevo campo, ordenar ascendente por defecto
        ordenacion.value.campo = campo;
        ordenacion.value.ascendente = true;
      }
    };
    
    // Formatear fecha para mostrar
    const formatFecha = (fecha) => {
      if (!fecha) return 'No disponible';
      
      try {
        const fechaObj = new Date(fecha);
        return fechaObj.toLocaleDateString('es-CO', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric'
        });
      } catch (error) {
        return fecha;
      }
    };
    
    // Limitar texto para mostrar
    const limitarTexto = (texto, maxLength) => {
      if (!texto) return 'Sin descripción';
      if (texto.length <= maxLength) return texto;
      return texto.substring(0, maxLength) + '...';
    };
    
    // Obtener clase CSS para la evaluación
    const getEvaluacionClass = (evaluacion) => {
      if (!evaluacion) return 'badge-secondary';
      
      switch(evaluacion) {
        case 'APROBADO':
          return 'badge-success';
        case 'RECHAZADO':
          return 'badge-danger';
        case 'PENDIENTE':
          return 'badge-warning';
        case 'EN REVISIÓN':
          return 'badge-info';
        default:
          return 'badge-secondary';
      }
    };
    
    // Aplicar filtros
    const aplicarFiltros = () => {
      // Aplicar filtros jerárquicos si hay algún filtro activo
      if (filtros.value.departamento || filtros.value.municipio || 
          filtros.value.insumo || filtros.value.clasificacion || 
          filtros.value.detalle) {
        filtrosJerarquicosActivos.value = true;
        aplicarFiltrosJerarquicos();
      } else {
        // Si no hay filtros, mostrar todos los conceptos
        filtrosJerarquicosActivos.value = false;
        conceptosFiltradosManual.value = conceptos.value;
      }
    };
    
    // Limpiar filtros
    const limpiarFiltros = () => {
      filtros.value = {
        departamento: '',
        municipio: '',
        insumo: '',
        clasificacion: '',
        detalle: ''
      };
      
      // Limpiar listas dependientes
      municipios.value = [];
      insumos.value = [];
      clasificaciones.value = [];
      detalles.value = [];
      
      // Desactivar filtros jerárquicos
      filtrosJerarquicosActivos.value = false;
      
      // Mostrar todos los conceptos
      conceptosFiltradosManual.value = conceptos.value;
      
      // Reiniciar paginación
      paginaActual.value = 1;
    };
    
    // Navegar a la página de creación
    const navigateToCreate = () => {
      router.push('/gestion-informacion/conceptos/crear');
    };
    
    // Ver concepto completo

    
    // Editar concepto
    const editarConcepto = (concepto) => {
      // Cerrar modal si está abierto
      if (modalConcepto.value.mostrar) {
        modalConcepto.value.mostrar = false;
      }
      
      // Navegar a la página de edición con el ID
      router.push(`/gestion-informacion/conceptos/${concepto.cod_concepto}`);
    };
    
    // Confirmar eliminación
    const confirmarEliminar = (concepto) => {
      modalEliminar.value.concepto = concepto;
      modalEliminar.value.mostrar = true;
    };
    
    // Eliminar concepto
    const eliminarConcepto = async () => {
      if (!modalEliminar.value.concepto) return;
      
      try {
        cargando.value = true;
        
        // Obtener el token de autenticación
        const token = localStorage.getItem('token');
        if (!token) {
          alert('No se encontró token de autenticación. Por favor, inicie sesión.');
          modalEliminar.value.mostrar = false;
          router.push('/login');
          return;
        }
        
        // Configurar headers con el token
        const config = {
          headers: {
            'Authorization': `Token ${token}`
          }
        };
        
        // Enviar la petición DELETE
        await axios.delete(
          `${API_URL}/preoperacion/conceptos/${modalEliminar.value.concepto.cod_concepto}/`,
          config
        );
        
        // También necesitamos actualizar los detalles que tenían este concepto
        try {
          // Buscar los detalles asociados a este concepto
          const detallesResponse = await axios.get(`${API_URL}/preoperacion/detalles-insumo/`, {
            params: { cod_concepto: modalEliminar.value.concepto.cod_concepto }
          });
          
          if (detallesResponse.data && detallesResponse.data.results && detallesResponse.data.results.length > 0) {
            // Para cada detalle, quitar la referencia al concepto
            for (const detalle of detallesResponse.data.results) {
              try {
                // Obtener el detalle completo
                const detalleCompleto = await axios.get(
                  `${API_URL}/preoperacion/detalles-insumo/${detalle.cod_detalle}/`
                );
                
                // Actualizar la referencia al concepto
                const detalleActualizado = {
                  ...detalleCompleto.data,
                  cod_concepto: null
                };
                
                // Guardar el detalle actualizado
                await axios.put(
                  `${API_URL}/preoperacion/detalles-insumo/${detalle.cod_detalle}/`,
                  detalleActualizado,
                  config
                );
              } catch (err) {
                console.warn(`Error al actualizar detalle ${detalle.cod_detalle}:`, err);
                // No bloqueamos el proceso por este error
              }
            }
          }
        } catch (err) {
          console.warn('Error al buscar detalles asociados:', err);
          // No bloqueamos el proceso por este error
        }
        
        // Cerrar modal
        modalEliminar.value.mostrar = false;
        
        // Actualizar lista
        await cargarConceptos();
        
        // Mostrar mensaje de éxito
        alert('Concepto eliminado con éxito');
      } catch (err) {
        console.error('Error al eliminar concepto:', err);
        
        let mensajeError = 'Error al eliminar el concepto.';
        if (err.response && err.response.data) {
          if (typeof err.response.data === 'string') {
            mensajeError = err.response.data;
          } else if (typeof err.response.data === 'object') {
            mensajeError = JSON.stringify(err.response.data);
          }
        }
        
        alert(`Error: ${mensajeError}`);
      } finally {
        cargando.value = false;
      }
    };
    
    // Exportar datos a CSV
    // Updated exportarDatos function with proper character encoding
    const exportarDatos = () => {
      if (!conceptosFiltrados.value.length) {
        alert('No hay datos para exportar');
        return;
      }
      
      try {
        // Define headers
        const headers = [
          'Código',
          'Concepto',
          'Fecha',
          'Evaluación',
          'Municipio',
          'Detalle Concepto',
          'Observaciones'
        ];
        
        // Prepare data rows
        const rows = conceptosFiltrados.value.map(concepto => [
          concepto.cod_concepto,
          concepto.concepto || '',
          formatFecha(concepto.fecha),
          concepto.evaluacion || '',
          concepto.municipio || '',
          concepto.detalle_concepto || '',
          concepto.observacion || ''
        ]);
        
        // Add BOM (Byte Order Mark) for UTF-8 encoding
        const BOM = '\uFEFF';
        
        // Combine headers and rows with proper escaping
        const csvContent = BOM + [
          headers.join(','),
          ...rows.map(row => row.map(cell => {
            // Convert to string and handle null/undefined
            const value = cell === null || cell === undefined ? '' : String(cell);
            
            // Check if we need to quote the cell (contains commas, quotes or newlines)
            if (value.includes(',') || value.includes('"') || value.includes('\n') || value.includes('\r')) {
              // Escape quotes by doubling them and wrap in quotes
              return `"${value.replace(/"/g, '""')}"`;
            }
            return value;
          }).join(','))
        ].join('\n');
        
        // Create blob with UTF-8 encoding
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        
        // Create and trigger download link
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', `conceptos_${new Date().toISOString().slice(0, 10)}.csv`);
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Clean up
        setTimeout(() => {
          URL.revokeObjectURL(url);
        }, 100);
      } catch (err) {
        console.error('Error al exportar datos:', err);
        alert('Error al exportar datos: ' + err.message);
      }
    };
    
    // Cargar datos al montar el componente
    onMounted(async () => {
      // Verificar autenticación
      if (!authStore.isAuthenticated) {
        console.log('Usuario no autenticado, redirigiendo a login...');
        router.push('/login');
        return;
      }
      
      // Inicializar variables de estado
      conceptosFiltradosManual.value = [];
      filtrosJerarquicosActivos.value = false;
      
      // Cargar datos iniciales en paralelo
      try {
        await Promise.all([
          cargarDepartamentos(),
          cargarConceptos()
        ]);
        
        // Verificar si hay filtros de URL al iniciar
        const componenteId = route.query.componente?.toString();
        if (componenteId) {
          filtros.value.componente = componenteId;
          aplicarFiltros();
        }
      } catch (err) {
        console.error('Error al cargar datos iniciales:', err);
        error.value = 'Error al cargar datos iniciales. Por favor, actualice la página.';
      }
    });
    
    // Limpiar event listeners al desmontar el componente
    onBeforeUnmount(() => {
      document.removeEventListener('keydown', handleEscKeypress);
    });
    
    // Añadir logs para depuración
    watch(() => conceptos.value.length, (newLength) => {
      console.log(`Número de conceptos actualizados: ${newLength}`);
    });
    
    watch(() => conceptosFiltradosManual.value.length, (newLength) => {
      console.log(`Número de conceptos filtrados: ${newLength}`);
      // Reiniciar paginación cuando cambian los resultados
      paginaActual.value = 1;
    });
    
    // Observar cambios en los filtros para actualizar inmediatamente
    watch([
      () => filtros.value.departamento,
      () => filtros.value.municipio,
      () => filtros.value.insumo,
      () => filtros.value.clasificacion,
      () => filtros.value.detalle
    ], () => {
      console.log('Filtros cambiados, aplicando automáticamente...');
      // No es necesario llamar a aplicarFiltros() aquí, ya que
      // cada cambio en los selectores llama a sus respectivas funciones
      // que actualizan automáticamente los resultados
    });
    // Descargar el PDF desde el backend

// ✅ FUNCIÓN PARA DESCARGAR PDF (CORREGIDA)
const descargarPdf = async (concepto) => {
  if (!concepto.pdf) {
    alert('No hay archivo PDF asociado a este concepto.');
    return;
  }
  
  try {
    const nombreArchivo = obtenerNombreArchivo(concepto.pdf);
    console.log('⬇️ Descargando PDF:', nombreArchivo);
    
    // ✅ USAR API CONFIGURADA CON PARÁMETRO download=true (igual que en InsumosList.vue)
    const response = await api.get('/preoperacion/ver_pdf/', {
      params: { 
        ruta: concepto.pdf,
        download: 'true' // ← Parámetro clave para forzar descarga
      },
      responseType: 'blob'
    });
    
    // Crear enlace de descarga
    const blob = new Blob([response]);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = nombreArchivo;
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    window.URL.revokeObjectURL(url);
    console.log('✅ PDF descargado exitosamente');
    
  } catch (error) {
    console.error('❌ Error al descargar PDF:', error);
    
    if (error.response?.status === 404) {
      alert('El archivo PDF no se encontró en el servidor.');
    } else if (error.response?.status === 403) {
      alert('No tiene permisos para acceder a este archivo.');
    } else {
      alert('Error al descargar el PDF: ' + (error.message || 'Error desconocido'));
    }
  }
};

// ✅ FUNCIÓN AUXILIAR MEJORADA PARA OBTENER NOMBRE DE ARCHIVO
const obtenerNombreArchivo = (ruta) => {
  if (!ruta) return 'archivo_sin_nombre.pdf';
  
  // Extraer nombre del archivo de la ruta
  const partes = ruta.replace(/\\/g, '/').split('/');
  let nombre = partes[partes.length - 1];
  
  // Si no tiene extensión, añadir .pdf
  if (!nombre.includes('.')) {
    nombre = `${nombre}.pdf`;
  }
  
  // Si el nombre está vacío, usar un nombre por defecto
  if (!nombre || nombre === '.pdf') {
    nombre = `concepto_${Date.now()}.pdf`;
  }
  
  return nombre;
};


    return {
      // Estado de PDF
      mostrandoPdf,
      pdfUrl,
      pdfCargando,
      pdfError,
      
      // Estado y datos
      cargando,
      error,
      conceptos,
      conceptosFiltrados,
      conceptosVisibles,
      
      // Catálogos
      departamentos,
      municipios,
      insumos,
      insumosConCategoria,
      clasificaciones,
      detalles,
      
      // Filtros y ordenación
      filtros,
      ordenacion,
      
      // Paginación
      paginaActual,
      totalPaginas,
      botonesNumericos,
      

      
      // Modales
      modalEliminar,
      modalConcepto,
      
      // Métodos y funciones útiles
      obtenerNombreArchivo,
      verPdf,
      cargarMunicipios,
      cargarInsumos,
      cargarClasificaciones,
      cargarDetalles,
      cargarConceptos,
      aplicarFiltros,
      limpiarFiltros,
      ordenarPor,
      cambiarPagina,
      formatFecha,
      limitarTexto,
      getEvaluacionClass,
      navigateToCreate,
      verConcepto,
      editarConcepto,
      confirmarEliminar,
      eliminarConcepto,
      exportarDatos,
      descargarPdf,
      verPdfEnNuevaPestana,
      modalConcepto,
      cerrarModalConcepto,
    };
  }
};
</script>




<style scoped>
.centro-poblado-info {
  display: block;
  margin-top: 4px;
  color: #6c757d;
}

.centro-poblado-info i {
  color: #007bff;
  margin-right: 4px;
}

.text-muted {
  color: #6c757d;
  font-size: 0.85em;
}

/* Estilos para el visor de PDF integrado */
.pdf-viewer-container {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.pdf-viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background-color: #e9ecef;
  border-bottom: 1px solid #dee2e6;
}

.pdf-viewer-header h6 {
  margin: 0;
  font-size: 1rem;
}

.pdf-iframe-container {
  height: 500px;
  overflow: hidden;
}

.pdf-iframe {
  border: none;
  width: 100%;
  height: 100%;
}
.conceptos-list-container {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 1.6rem;
  color: #333;
  margin: 0;
}

.actions-bar {
  display: flex;
  gap: 0.75rem;
}

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

.col-12 {
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
  transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  cursor: pointer;
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

.btn-primary:disabled {
  color: #fff;
  background-color: #007bff;
  border-color: #007bff;
  opacity: 0.65;
  cursor: not-allowed;
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

.btn-danger {
  color: #fff;
  background-color: #dc3545;
  border-color: #dc3545;
}

.btn-danger:hover {
  color: #fff;
  background-color: #c82333;
  border-color: #bd2130;
}

.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 123, 255, 0.1);
  border-left-color: #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: #6c757d;
  font-size: 1rem;
}

.error-container i,
.empty-container i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #dc3545;
}

.empty-container i {
  color: #6c757d;
}

.results-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.results-title {
  font-size: 1.2rem;
  margin: 0;
  color: #333;
}

.results-count {
  color: #6c757d;
font-size: 0.9rem;
}

.table-responsive {
display: block;
width: 100%;
overflow-x: auto;
-webkit-overflow-scrolling: touch;
}

.table {
width: 100%;
margin-bottom: 1rem;
color: #212529;
border-collapse: collapse;
}

.table th,
.table td {
padding: 0.75rem;
vertical-align: top;
border-top: 1px solid #dee2e6;
}

.table thead th {
vertical-align: bottom;
border-bottom: 2px solid #dee2e6;
font-weight: 600;
background-color: #f8f9fa;
position: relative;
cursor: pointer;
}

.table thead th i {
font-size: 1rem;
vertical-align: middle;
margin-left: 0.25rem;
}

.table-striped tbody tr:nth-of-type(odd) {
background-color: rgba(0, 0, 0, 0.05);
}

.table-hover tbody tr:hover {
background-color: rgba(0, 0, 0, 0.075);
}

.concepto-texto {
display: block;
max-width: 300px;
}

.badge {
display: inline-block;
padding: 0.25em 0.6em;
font-size: 75%;
font-weight: 700;
line-height: 1;
text-align: center;
white-space: nowrap;
vertical-align: baseline;
border-radius: 0.25rem;
}

.badge-success {
color: #fff;
background-color: #28a745;
}

.badge-info {
color: #fff;
background-color: #17a2b8;
}

.badge-warning {
color: #212529;
background-color: #ffc107;
}

.badge-danger {
color: #fff;
background-color: #dc3545;
}

.badge-secondary {
color: #fff;
background-color: #6c757d;
}

.actions-column {
width: 120px;
}

.actions-buttons {
display: flex;
gap: 0.5rem;
}

.btn-icon {
display: flex;
align-items: center;
justify-content: center;
width: 32px;
height: 32px;
border-radius: 4px;
border: none;
background-color: #f8f9fa;
color: #495057;
cursor: pointer;
transition: all 0.2s;
}

.btn-icon:hover {
background-color: #e9ecef;
}

.btn-icon.btn-danger {
background-color: #f8d7da;
color: #dc3545;
}

.btn-icon.btn-danger:hover {
background-color: #f5c6cb;
}

.pagination-container {
display: flex;
justify-content: center;
margin-top: 1.5rem;
gap: 0.25rem;
}

.btn-pagination {
display: flex;
align-items: center;
justify-content: center;
min-width: 32px;
height: 32px;
padding: 0 0.5rem;
border: 1px solid #dee2e6;
background-color: #fff;
border-radius: 4px;
color: #007bff;
cursor: pointer;
}

.btn-pagination:hover {
background-color: #e9ecef;
text-decoration: none;
}

.btn-pagination.active {
background-color: #007bff;
border-color: #007bff;
color: #fff;
cursor: default;
}

.btn-pagination.disabled {
color: #6c757d;
pointer-events: none;
cursor: not-allowed;
}

.text-muted {
color: #6c757d;
}

.modal {
position: fixed;
top: 0;
left: 0;
width: 100%;
height: 100%;
background-color: rgba(0, 0, 0, 0.5);
display: flex;
align-items: center;
justify-content: center;
z-index: 1000;
}

.modal-dialog {
width: 100%;
max-width: 500px;
background-color: white;
border-radius: 8px;
box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-dialog.modal-lg {
max-width: 800px;
}

.modal-content {
border: none;
border-radius: 8px;
overflow: hidden;
}

.modal-header {
display: flex;
align-items: center;
justify-content: space-between;
padding: 1rem 1.5rem;
border-bottom: 1px solid #dee2e6;
background-color: #f8f9fa;
}

.modal-title {
margin: 0;
font-size: 1.2rem;
color: #333;
}

.close-button {
background: none;
border: none;
font-size: 1.5rem;
cursor: pointer;
color: #6c757d;
padding: 0;
line-height: 1;
}

.modal-body {
padding: 1.5rem;
}

.modal-footer {
display: flex;
justify-content: flex-end;
gap: 0.75rem;
padding: 1rem 1.5rem;
border-top: 1px solid #dee2e6;
background-color: #f8f9fa;
}

.concepto-info {
font-size: 0.95rem;
}

.concepto-header {
margin-bottom: 1rem;
}

.concepto-header h5 {
font-size: 1.1rem;
margin-bottom: 0.5rem;
color: #343a40;
}

.concepto-meta {
display: flex;
align-items: center;
gap: 1rem;
color: #6c757d;
}

.fecha {
display: flex;
align-items: center;
gap: 0.25rem;
}

.fecha i {
font-size: 1rem;
}

.detalle-text,
.observacion-text {
padding: 0.75rem;
background-color: #f8f9fa;
border-radius: 4px;
border: 1px solid #dee2e6;
white-space: pre-wrap;
max-height: 200px;
overflow-y: auto;
margin-bottom: 1rem;
}

.text-danger {
color: #dc3545;
}

.mt-3 {
margin-top: 1rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
.header-section {
  flex-direction: column;
  align-items: flex-start;
  gap: 1rem;
}

.actions-bar {
  width: 100%;
}

.btn-pagination {
  min-width: 28px;
  height: 28px;
  font-size: 0.8rem;
}

.modal-dialog {
  margin: 0.5rem;
  max-width: calc(100% - 1rem);
}

.modal-dialog.modal-lg {
  max-width: calc(100% - 1rem);
}
}
.pdf-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #dee2e6;
  margin-bottom: 1rem;
}

.pdf-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pdf-info i {
  color: #dc3545;
  font-size: 1.5rem;
}

.pdf-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  line-height: 1.5;
  border-radius: 0.2rem;
}
/* ESTILOS PARA EL MODAL MEJORADO */
.fixed-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

/* Modal de tamaño compacto y controlado */
.modal-compact {
  width: 95%;
  max-width: 700px; /* Tamaño fijo más pequeño */
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.4);
  max-height: 90vh; /* Altura máxima */
  display: flex;
  flex-direction: column;
}

.modal-content {
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Importante para contener el scroll */
  height: 100%;
}

.modal-header {
  background-color: #f8f9fa;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #dee2e6;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

/* Botón de cerrar destacado */
.close-button {
  background: rgba(0, 0, 0, 0.1);
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
}

.close-button:hover {
  background: rgba(0, 0, 0, 0.2);
}

.modal-body {
  padding: 20px;
  overflow-y: auto; /* Scroll solo en el cuerpo */
  flex: 1;
}

.modal-footer {
  padding: 15px 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  border-top: 1px solid #dee2e6;
  background-color: #f8f9fa;
}

/* Estilo para formulario estructurado */
.concepto-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: flex;
  gap: 16px;
}
.pdf-viewer-content {
  width: 100%;
  height: 500px;
  overflow: hidden;
  border: 1px solid #dee2e6;
  border-radius: 0 0 4px 4px;
}

.pdf-iframe {
  width: 100%;
  height: 100%;
  border: none;
}
.form-field {
  flex: 1;
  min-width: 0; /* Evita overflow */
}

.form-field label {
  display: block;
  font-weight: 600;
  margin-bottom: 5px;
  color: #495057;
  font-size: 14px;
}

.field-value {
  padding: 8px 12px;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  min-height: 24px;
  word-break: break-word;
}

.field-value.text-area {
  min-height: 80px;
  max-height: 150px;
  overflow-y: auto;
  white-space: pre-wrap;
}

.form-section {
  border-top: 1px solid #e9ecef;
  padding-top: 16px;
  margin-top: 10px;
}

.form-section h6 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 16px;
}

.full-width {
  width: 100%;
}

/* Estilos para la sección de PDF */
.pdf-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
}

.pdf-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pdf-info i {
  color: #dc3545;
  font-size: 24px;
}

.pdf-actions {
  display: flex;
  gap: 8px;
}

/* Botones mejorados */
.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn i {
  font-size: 16px;
  margin-right: 4px;
}

/* Responsive */
@media (max-width: 600px) {
  .form-row {
    flex-direction: column;
    gap: 10px;
  }
  
  .modal-body {
    padding: 15px;
  }
}
.fixed-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

/* Modal de tamaño compacto y controlado */
.modal-compact {
  width: 95%;
  max-width: 700px; /* Tamaño fijo más pequeño */
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.4);
  max-height: 90vh; /* Altura máxima */
  display: flex;
  flex-direction: column;
}

.modal-content {
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Importante para contener el scroll */
  height: 100%;
}

.modal-header {
  background-color: #f8f9fa;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #dee2e6;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

/* Botón de cerrar destacado */
.close-button {
  background: rgba(0, 0, 0, 0.1);
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
}

.close-button:hover {
  background: rgba(0, 0, 0, 0.2);
}

.modal-body {
  padding: 20px;
  overflow-y: auto; /* Scroll solo en el cuerpo */
  flex: 1;
}

.modal-footer {
  padding: 15px 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  border-top: 1px solid #dee2e6;
  background-color: #f8f9fa;
}

/* Estilo para formulario estructurado */
.concepto-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-field {
  flex: 1;
  min-width: 0; /* Evita overflow */
}

.form-field label {
  display: block;
  font-weight: 600;
  margin-bottom: 5px;
  color: #495057;
  font-size: 14px;
}

.field-value {
  padding: 8px 12px;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  min-height: 24px;
  word-break: break-word;
}

.field-value.text-area {
  min-height: 80px;
  max-height: 150px;
  overflow-y: auto;
  white-space: pre-wrap;
}

.form-section {
  border-top: 1px solid #e9ecef;
  padding-top: 16px;
  margin-top: 10px;
}

.form-section h6 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 16px;
}

.full-width {
  width: 100%;
}

/* Estilos para la sección de PDF */
.pdf-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
}

.pdf-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pdf-info i {
  color: #dc3545;
  font-size: 24px;
}

.pdf-actions {
  display: flex;
  gap: 8px;
}

/* Botones mejorados */
.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn i {
  font-size: 16px;
  margin-right: 4px;
}

/* Responsive */
@media (max-width: 600px) {
  .form-row {
    flex-direction: column;
    gap: 10px;
  }
  
  .modal-body {
    padding: 15px;
  }
}
/* Estilos para arreglar el color de texto en los badges */
.badge-text {
  display: inline-block;
  padding: 0.25em 0.6em;
  font-size: 75%;
  font-weight: 700;
  line-height: 1;
  text-align: center;
  white-space: nowrap;
  vertical-align: baseline;
  border-radius: 0.25rem;
  color: white; /* Asegura que el texto sea blanco */
}

.badge-text.badge-success {
  background-color: #28a745;
}

.badge-text.badge-info {
  background-color: #17a2b8;
}

.badge-text.badge-warning {
  background-color: #ffc107;
  color: #212529; /* Para badge warning, el texto debe ser oscuro */
}

.badge-text.badge-danger {
  background-color: #dc3545;
}

.badge-text.badge-secondary {
  background-color: #6c757d;
}

/* Mejorar visualización de la ruta del PDF */
.field-value.text-area {
  font-family: monospace;
  font-size: 0.85rem;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 100px;
  overflow-y: auto;
}
</style>