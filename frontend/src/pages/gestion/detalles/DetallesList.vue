<template>
  <div class="detalles-list-container">
    <div class="header-section">
      <h2 class="page-title">Consulta de Detalles de Insumos</h2>
      <div class="actions-bar">
        <button class="btn btn-primary" @click="navigateToCreate">
          <i class="material-icons">add</i>
          Crear Nuevo Detalle
        </button>
        <button class="btn btn-secondary" @click="exportarDatos" :disabled="!detalles.length">
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

      <!-- Filtros adicionales -->
      <div class="row">
        <div class="col-md-6 col-lg-3">
          <div class="form-group">
            <label for="estado">Estado:</label>
            <select id="estado" v-model="filtros.estado" class="form-control">
              <option value="">Todos los estados</option>
              <option value="EN PRODUCCION">EN PRODUCCION</option>
              <option value="NO SE PRODUCIRA">NO SE PRODUCIRA</option>
              <option value="OFICIALIZADO">OFICIALIZADO</option>
              <option value="OFICIALIZADO PARCIAL">OFICIALIZADO PARCIAL</option>
              <option value="POR PRODUCIR">POR PRODUCIR</option>
              <option value="SIN FECHA DEFINIDA">SIN FECHA DEFINIDA</option>
            </select>
          </div>
        </div>

        <div class="col-md-6 col-lg-3">
          <div class="form-group">
            <label for="zona">Zona:</label>
            <select id="zona" v-model="filtros.zona" class="form-control">
              <option value="">Todas las zonas</option>
              <option 
                v-for="zona in zonas" 
                :key="zona.zona" 
                :value="zona.zona"
              >
                {{ zona.zona }}
              </option>
            </select>
          </div>
        </div>

        <div class="col-md-6 col-lg-3">
          <div class="form-group">
            <label for="entidad">Entidad:</label>
            <select id="entidad" v-model="filtros.entidad" class="form-control">
              <option value="">Todas las entidades</option>
              <option 
                v-for="entidad in entidades" 
                :key="entidad.cod_entidad" 
                :value="entidad.cod_entidad"
              >
                {{ entidad.nom_entidad }}
              </option>
            </select>
          </div>
        </div>

        <div class="col-md-6 col-lg-3">
          <div class="form-group">
            <label for="busqueda">Búsqueda:</label>
            <input 
              type="text" 
              id="busqueda" 
              v-model="filtros.busqueda" 
              placeholder="Buscar por observación..."
              class="form-control"
            />
          </div>
        </div>
      </div>

      <div class="filtros-buttons">
        <button class="btn btn-primary" @click="aplicarFiltros" :disabled="cargando">
          <i class="material-icons">filter_list</i>
          {{ cargando ? 'Buscando...' : 'Aplicar Filtros' }}
        </button>
        <button class="btn btn-secondary" @click="limpiarFiltros" :disabled="cargando">
          <i class="material-icons">clear_all</i>
          Limpiar Filtros
        </button>
        <div v-if="cargando" class="filtros-loading">
          <i class="material-icons spinning">autorenew</i>
          <span>{{ mensajeCarga }}</span>
        </div>
      </div>
    </div>

    <!-- ⚠️ MENSAJE DE PACIENCIA PARA CONSULTAS AMPLIAS -->
    <div v-if="mostrarMensajePaciencia" class="mensaje-paciencia alert alert-warning">
      <div class="mensaje-header">
        <i class="material-icons">info</i>
        <strong>Consulta amplia detectada</strong>
      </div>
      <p class="mensaje-texto">
        Esta consulta de departamento completo puede tomar <strong>2-4 minutos</strong> debido a la gran cantidad de datos. 
        <strong>Recomendación:</strong> Seleccione un municipio específico para obtener resultados más rápidos y precisos.
      </p>
      <div class="mensaje-sugerencias">
        <small>
          <strong>💡 Sugerencias para acelerar:</strong> Seleccione un municipio específico, una clasificación, 
          un estado particular, o combine múltiples filtros para resultados más dirigidos.
        </small>
      </div>
    </div>

    <!-- ⚠️ ADVERTENCIA PARA CONSULTAS SIN FILTROS -->
    <div v-if="mostrarAdvertencia && !mostrarMensajePaciencia" class="alert alert-warning">
      <div class="mensaje-header">
        <i class="material-icons">warning</i>
        <strong>Vista inicial limitada</strong>
      </div>
      <p>
        Se muestran solo los primeros 10 resultados. Use filtros específicos para obtener datos más precisos.
      </p>
    </div>

    <!-- 📊 BARRA DE PROGRESO DETALLADA -->
    <div v-if="progresoCarga.mostrar" class="progreso-container alert alert-info">
      <div class="progreso-header">
        <i class="material-icons">hourglass_top</i>
        <strong>{{ progresoCarga.titulo }}</strong>
        <div v-if="progresoCarga.etapa" class="progreso-etapa">
          {{ progresoCarga.etapa }}
        </div>
        <div v-if="progresoCarga.tiempoEstimado" class="progreso-tiempo">
          {{ progresoCarga.tiempoEstimado }}
        </div>
      </div>
      
      <div class="progreso-bar">
        <div class="progreso-fill" :style="{ width: progresoCarga.porcentaje + '%' }"></div>
        <div class="progreso-text-overlay">
          {{ Math.round(progresoCarga.porcentaje) }}%
        </div>
      </div>
      
      <div class="progreso-stats">
        <span class="progreso-actual">{{ progresoCarga.actual }}</span>
        <span class="progreso-separador"> de </span>
        <span class="progreso-total">{{ progresoCarga.total }}</span>
      </div>
      
      <div v-if="progresoCarga.detalle" class="progreso-detalle">
        <i class="material-icons small-icon">info_outline</i>
        {{ progresoCarga.detalle }}
      </div>
      
      <div v-if="progresoCarga.mostrarTip" class="progreso-tip">
        <small>
          <i class="material-icons small-icon">lightbulb_outline</i>
          💡 Tip: Para consultas más rápidas, use filtros específicos como municipio o clasificación
        </small>
      </div>
    </div>

    <!-- Estado de carga y mensajes -->
    <div v-if="cargando && !progresoCarga.mostrar" class="loading-container">
      <div class="spinner"></div>
      <span class="loading-text">{{ mensajeCarga }}</span>
    </div>

    <div v-else-if="error" class="error-container">
      <i class="material-icons">error</i>
      <span>{{ error }}</span>
      <button class="btn btn-primary" @click="aplicarFiltros">Reintentar</button>
    </div>

    <div v-else-if="detalles.length === 0 && !cargando" class="empty-container">
      <i class="material-icons">info</i>
      <span>No se encontraron detalles con los filtros seleccionados</span>
    </div>

    <!-- INFORMACIÓN DE RESULTADOS -->
    <div v-else-if="detalles.length > 0" class="results-info alert alert-info">
      <i class="material-icons">info</i>
      <span>
        Mostrando {{ detalles.length }} registros{{ hayMasResultados ? ' (puede haber más disponibles)' : '' }}.
        <span v-if="hayMasResultados">Use filtros más específicos para resultados precisos.</span>
        <span v-if="resultadosLimitados"> Resultados limitados por rendimiento - use filtros más específicos.</span>
      </span>
    </div>

    <!-- Tabla de resultados -->
    <div v-if="detalles.length > 0 && !cargando" class="results-container">
      <div class="results-header">
        <h3 class="results-title">Resultados</h3>
        <span class="results-count">{{ detalles.length }} detalles encontrados</span>
      </div>

      <div class="table-responsive">
        <table class="table table-striped table-hover">
          <thead>
            <tr>
              <th @click="ordenarPor('cod_detalle')">
                Código
                <i v-if="ordenacion.campo === 'cod_detalle'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th>Municipio</th>
              <th>Clasificación</th>
              <th @click="ordenarPor('estado')">
                Estado
                <i v-if="ordenacion.campo === 'estado'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('zona')">
                Zona / Centro Poblado
                <i v-if="ordenacion.campo === 'zona'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th>Entidad</th>
              <th @click="ordenarPor('escala')">
                Escala
                <i v-if="ordenacion.campo === 'escala'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th>Formato</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="detalle in detallesVisibles" :key="detalle.cod_detalle">
              <td>{{ detalle.cod_detalle }}</td>
              <td>{{ detalle.municipio_nombre || 'Cargando...' }}</td>
              <td>{{ detalle.clasificacion_nombre || 'Cargando...' }}</td>
              <td>
                <span class="badge" :class="getEstadoClass(detalle.estado)">
                  {{ detalle.estado || 'Sin estado' }}
                </span>
              </td>
              <td>{{ formatZonaConCentroPoblado(detalle) }}</td>
              <td>{{ detalle.entidad_nombre || 'Cargando...' }}</td>
              <td>{{ detalle.escala || 'N/A' }}</td>
              <td>
                <span class="badge badge-secondary">{{ detalle.formato_tipo || 'N/A' }}</span>
              </td>
              <td class="actions-column">
                <div class="actions-buttons">
                  <button class="btn-icon" @click="verDetalle(detalle)" title="Ver detalle">
                    <i class="material-icons">visibility</i>
                  </button>
                  <button class="btn-icon" @click="editarDetalle(detalle)" title="Editar">
                    <i class="material-icons">edit</i>
                  </button>
                  <button class="btn-icon btn-danger" @click="confirmarEliminar(detalle)" title="Eliminar">
                    <i class="material-icons">delete</i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Paginación REAL -->
      <div class="pagination-container" v-if="totalPaginas > 1">
        <button 
          class="btn-pagination" 
          @click="cambiarPagina(paginaActual - 1)" 
          :disabled="paginaActual === 1 || cargando"
        >
          <i class="material-icons">navigate_before</i>
        </button>
        
        <button 
          v-for="pagina in botonesNumericos" 
          :key="pagina.valor"
          class="btn-pagination" 
          :class="{ active: pagina.activo, disabled: pagina.ellipsis }"
          @click="pagina.ellipsis ? null : cambiarPagina(pagina.valor)"
          :disabled="cargando"
        >
          {{ pagina.texto }}
        </button>
        
        <button 
          class="btn-pagination" 
          @click="cambiarPagina(paginaActual + 1)" 
          :disabled="paginaActual === totalPaginas || cargando"
        >
          <i class="material-icons">navigate_next</i>
        </button>
      </div>
    </div>

    <!-- Modal de Eliminación -->
    <div class="modal" v-if="modalEliminar.mostrar">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">Confirmar eliminación</h4>
            <button class="close-button" @click="modalEliminar.mostrar = false">
              <i class="material-icons">close</i>
            </button>
          </div>
          <div class="modal-body">
            <p>¿Está seguro de que desea eliminar el detalle con código <strong>{{ modalEliminar.detalle?.cod_detalle }}</strong>?</p>
            <p class="text-danger">Esta acción no se puede deshacer.</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="modalEliminar.mostrar = false">Cancelar</button>
            <button class="btn btn-danger" @click="eliminarDetalle">Eliminar</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 🆕 MODAL DE DETALLE MEJORADO CON SCROLL -->
    <div class="modal" v-if="modalDetalle.mostrar">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">
              📋 Detalle Completo - Código {{ modalDetalle.detalle?.cod_detalle }}
            </h4>
            <div class="header-info">
              <span class="scroll-hint">📜 Desplázate para ver toda la información</span>
            </div>
            <button class="close-button" @click="modalDetalle.mostrar = false">
              <i class="material-icons">close</i>
            </button>
          </div>
          <div class="modal-body">
            <div v-if="modalDetalle.detalle" class="detalle-info">
              
              <!-- 📍 INFORMACIÓN GEOGRÁFICA -->
              <div class="info-section">
                <h6 class="seccion-titulo">📍 Información Geográfica</h6>
                <div class="row">
                  <div class="col-md-6">
                    <p><strong>Código Detalle:</strong> <span class="codigo-highlight">{{ modalDetalle.detalle.cod_detalle }}</span></p>
                    <p><strong>Municipio:</strong> {{ modalDetalle.detalle.municipio_nombre || 'No disponible' }}</p>
                    <p><strong>Código Municipio:</strong> {{ modalDetalle.detalle.cod_municipio || 'No disponible' }}</p>
                  </div>
                  <div class="col-md-6">
                    <p><strong>Zona:</strong> 
                      <span class="badge badge-info">{{ modalDetalle.detalle.zona || 'No disponible' }}</span>
                    </p>
                    <p><strong>Área (km²):</strong> {{ formatArea(modalDetalle.detalle.area) }}</p>
                    <p><strong>Cubrimiento:</strong> {{ modalDetalle.detalle.cubrimiento || 'No disponible' }}</p>
                    <p><strong>% Cubrimiento:</strong> {{ formatPorcentaje(modalDetalle.detalle.porcentaje_cubrimiento) }}</p>
                  </div>
                </div>
                
                <!-- ✅ INFORMACIÓN DETALLADA DEL CENTRO POBLADO -->
                <div v-if="modalDetalle.detalle.zona === 'CENTROS POBLADOS'" class="centro-poblado-detalle">
                  <h6 class="centro-titulo">🏘️ Centro Poblado Asociado</h6>
                  <div class="centro-info-box">
                    <div class="row">
                      <div class="col-md-6">
                        <p><strong>Código Centro:</strong> {{ modalDetalle.detalle.cod_centro_poblado || 'No disponible' }}</p>
                      </div>
                      <div class="col-md-6">
                        <p><strong>Nombre Centro:</strong> {{ modalDetalle.detalle.centro_poblado_nombre || 'Cargando...' }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 🏢 INFORMACIÓN INSTITUCIONAL -->
              <div class="info-section">
                <h6 class="seccion-titulo">🏢 Información Institucional</h6>
                <div class="row">
                  <div class="col-md-6">
                    <p><strong>Entidad:</strong> {{ modalDetalle.detalle.entidad_nombre || 'No disponible' }}</p>
                    <p><strong>Código Entidad:</strong> {{ modalDetalle.detalle.cod_entidad || 'No disponible' }}</p>
                    <p><strong>Clasificación:</strong> {{ modalDetalle.detalle.clasificacion_nombre || 'No disponible' }}</p>
                  </div>
                  <div class="col-md-6">
                    <p><strong>Código Clasificación:</strong> {{ modalDetalle.detalle.cod_clasificacion || 'No disponible' }}</p>
                    <p><strong>Usuario Responsable:</strong> {{ modalDetalle.detalle.cod_usuario || 'No disponible' }}</p>
                    <p><strong>Estado:</strong> 
                      <span class="badge" :class="getEstadoClass(modalDetalle.detalle.estado)">
                        {{ modalDetalle.detalle.estado || 'No disponible' }}
                      </span>
                    </p>
                  </div>
                </div>
              </div>

              <!-- 📋 ESPECIFICACIONES TÉCNICAS -->
              <div class="info-section">
                <h6 class="seccion-titulo">📋 Especificaciones Técnicas</h6>
                <div class="row">
                  <div class="col-md-6">
                    <p><strong>Escala:</strong> {{ modalDetalle.detalle.escala || 'No definida' }}</p>
                    <p><strong>Formato:</strong> 
                      <span class="badge badge-secondary">{{ modalDetalle.detalle.formato_tipo || 'No disponible' }}</span>
                    </p>
                    <p><strong>Vigencia:</strong> {{ modalDetalle.detalle.vigencia || 'No disponible' }}</p>
                  </div>
                  <div class="col-md-6">
                    <p><strong>Ruta Archivo:</strong></p>
                    <div v-if="modalDetalle.detalle.ruta_archivo" class="ruta-archivo">
                      📁 {{ modalDetalle.detalle.ruta_archivo }}
                    </div>
                    <div v-else class="text-muted">No especificada</div>
                  </div>
                </div>
              </div>

              <!-- 📅 FECHAS IMPORTANTES -->
              <div class="info-section">
                <h6 class="seccion-titulo">📅 Cronología</h6>
                <div class="row">
                  <div class="col-md-6">
                    <p><strong>Fecha Entrega:</strong> {{ formatFecha(modalDetalle.detalle.fecha_entrega) }}</p>
                    <p><strong>Fecha Disposición:</strong> {{ formatFecha(modalDetalle.detalle.fecha_disposicion) }}</p>
                  </div>
                  <div class="col-md-6">
                    <p><strong>Fecha Creación:</strong> {{ formatFecha(modalDetalle.detalle.fecha_creacion) }}</p>
                    <p><strong>Última Actualización:</strong> {{ formatFecha(modalDetalle.detalle.fecha_actualizacion) }}</p>
                  </div>
                </div>
              </div>

              <!-- 📝 OBSERVACIONES -->
              <div class="info-section">
                <h6 class="seccion-titulo">📝 Observaciones y Notas</h6>
                <div class="observaciones-box">
                  <p>{{ modalDetalle.detalle.observacion || 'Sin observaciones registradas' }}</p>
                </div>
              </div>

            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-primary" @click="editarDetalle(modalDetalle.detalle)">
              <i class="material-icons">edit</i>
              Editar
            </button>
            <button class="btn btn-secondary" @click="modalDetalle.mostrar = false">
              <i class="material-icons">close</i>
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth';
import axios from 'axios';
import api, { API_URL } from '@/api/config';

export default {
  name: 'DetallesList',

  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    
    // 🚫 CONTROLADOR DE CANCELACIÓN
    let abortController = null;
    
    // Estado de carga y errores
    const cargando = ref(false);
    const error = ref(null);
    const mensajeCarga = ref('Cargando detalles...');
    
    // Datos para la tabla
    const detalles = ref([]);
    const hayMasResultados = ref(false);
    const mostrarAdvertencia = ref(false);
    const mostrarMensajePaciencia = ref(false);
    const resultadosLimitados = ref(false);
    
    // 🎯 BARRA DE PROGRESO DETALLADA
    const progresoCarga = ref({
      mostrar: false,
      titulo: '',
      actual: 0,
      total: 0,
      porcentaje: 0,
      detalle: '',
      mostrarTip: false,
      etapa: '',
      tiempoEstimado: '',
      inicioTiempo: 0
    });
    
    // Catálogos y listas de referencia
    const departamentos = ref([]);
    const municipios = ref([]);
    const insumos = ref([]);
    const clasificaciones = ref([]);
    const zonas = ref([]);
    const entidades = ref([]);
    
    // Filtros de búsqueda
    const filtros = ref({
      departamento: '',
      municipio: '',
      insumo: '',
      clasificacion: '',
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
    
    // Paginación REAL
    const paginaActual = ref(1);
    const elementosPorPagina = ref(25);
    const totalRegistros = ref(0);
    
    // Modales
    const modalEliminar = ref({
      mostrar: false,
      detalle: null
    });
    
    const modalDetalle = ref({
      mostrar: false,
      detalle: null
    });
    
    // 🔄 FUNCIÓN PARA CANCELAR PETICIONES ANTERIORES
    const cancelarPeticionesAnteriores = () => {
      if (abortController) {
        abortController.abort();
      }
      abortController = new AbortController();
      return abortController.signal;
    };
    
    // 📊 FUNCIÓN PARA ACTUALIZAR PROGRESO CON DETALLES
    const actualizarProgreso = (actual, total, titulo, detalle = '', mostrarTip = false, etapa = '') => {
      progresoCarga.value.actual = actual;
      progresoCarga.value.total = total;
      progresoCarga.value.porcentaje = total > 0 ? (actual / total) * 100 : 0;
      progresoCarga.value.titulo = titulo;
      progresoCarga.value.detalle = detalle;
      progresoCarga.value.mostrarTip = mostrarTip;
      progresoCarga.value.etapa = etapa;
      
      // Calcular tiempo estimado (aproximado)
      if (total > 0 && actual > 0 && progresoCarga.value.inicioTiempo) {
        const porcentajeCompletado = actual / total;
        const tiempoTranscurrido = (Date.now() - progresoCarga.value.inicioTiempo) / 1000;
        const tiempoEstimadoTotal = tiempoTranscurrido / porcentajeCompletado;
        const tiempoRestante = Math.max(0, tiempoEstimadoTotal - tiempoTranscurrido);
        
        if (tiempoRestante > 60) {
          progresoCarga.value.tiempoEstimado = `~${Math.ceil(tiempoRestante / 60)} min`;
        } else if (tiempoRestante > 10) {
          progresoCarga.value.tiempoEstimado = `~${Math.ceil(tiempoRestante)} seg`;
        } else {
          progresoCarga.value.tiempoEstimado = 'Casi listo...';
        }
      }
    };
    
    // 🚀 INICIAR PROGRESO
    const iniciarProgreso = (titulo, mostrarTip = false) => {
      progresoCarga.value = {
        mostrar: true,
        titulo,
        actual: 0,
        total: 100,
        porcentaje: 0,
        detalle: '',
        mostrarTip,
        etapa: '',
        tiempoEstimado: '',
        inicioTiempo: Date.now()
      };
    };
    
    // 🏁 FINALIZAR PROGRESO
    const finalizarProgreso = () => {
      progresoCarga.value.mostrar = false;
      mostrarMensajePaciencia.value = false;
    };
    
    // 🔥 FUNCIÓN PRINCIPAL DE CARGA - CON PROGRESO DETALLADO
    const cargarDetalles = async (pagina = 1) => {
      // 🚫 CANCELAR peticiones anteriores
      const signal = cancelarPeticionesAnteriores();
      
      error.value = null;
      cargando.value = true;
      
      try {
        // 🎯 DETECTAR TIPO DE FILTROS
        const tieneClasificacionDirecta = filtros.value.clasificacion;
        const tieneFiltrosDirectos = filtros.value.estado || filtros.value.zona || filtros.value.entidad;
        const tieneFiltrosJerarquicos = filtros.value.departamento || filtros.value.municipio || filtros.value.insumo;
        
        // 🚨 MOSTRAR MENSAJE DE PACIENCIA PARA CONSULTAS AMPLIAS
        if (filtros.value.departamento && !filtros.value.municipio) {
          mostrarMensajePaciencia.value = true;
        } else {
          mostrarMensajePaciencia.value = false;
        }
        
        let detallesObtenidos = [];
        
        if (tieneClasificacionDirecta || tieneFiltrosDirectos) {
          // 🎯 FILTROS DIRECTOS - Consulta directa al endpoint
          mensajeCarga.value = 'Aplicando filtros específicos...';
          detallesObtenidos = await cargarConFiltrosDirectos(pagina, signal);
          
        } else if (tieneFiltrosJerarquicos) {
          // 🗃️ FILTROS JERÁRQUICOS - Con progreso detallado
          detallesObtenidos = await cargarConFiltrosJerarquicos(pagina, signal);
          
        } else {
          // 📋 SIN FILTROS - Carga inicial limitada
          mensajeCarga.value = 'Consultando primeros resultados...';
          mostrarAdvertencia.value = true;
          detallesObtenidos = await cargarSinFiltros(pagina, signal);
        }
        
        // Asignar resultados
        if (Array.isArray(detallesObtenidos)) {
          detalles.value = detallesObtenidos;
          totalRegistros.value = detallesObtenidos.length;
          hayMasResultados.value = detallesObtenidos.length >= elementosPorPagina.value;
          resultadosLimitados.value = filtros.value.departamento && !filtros.value.municipio;
        } else if (detallesObtenidos && detallesObtenidos.results) {
          detalles.value = detallesObtenidos.results;
          totalRegistros.value = detallesObtenidos.count || 0;
          hayMasResultados.value = totalRegistros.value > detalles.value.length;
          resultadosLimitados.value = false;
        } else {
          detalles.value = [];
          totalRegistros.value = 0;
          hayMasResultados.value = false;
          resultadosLimitados.value = false;
        }
        
        paginaActual.value = pagina;
        
        console.log(`✅ Cargados ${detalles.value.length} detalles (página ${pagina})`);
        
        // 🏷️ CARGAR NOMBRES CON PROGRESO
        if (detalles.value.length > 0) {
          await cargarNombresConProgreso(signal);
        }
        
      } catch (err) {
        if (err.name === 'AbortError') {
          console.log('🚫 Petición cancelada');
          return;
        }
        
        console.error('❌ Error cargando detalles:', err);
        error.value = 'Error al cargar los detalles.';
      } finally {
        cargando.value = false;
        finalizarProgreso();
      }
    };
    
    // 🎯 CARGAR CON FILTROS DIRECTOS
    const cargarConFiltrosDirectos = async (pagina, signal) => {
      const params = new URLSearchParams();
      params.append('page', pagina.toString());
      params.append('page_size', elementosPorPagina.value.toString());
      
      if (filtros.value.clasificacion) {
        params.append('cod_clasificacion', filtros.value.clasificacion);
      }
      if (filtros.value.estado) {
        params.append('estado', filtros.value.estado);
      }
      if (filtros.value.zona) {
        params.append('zona', filtros.value.zona);
      }
      if (filtros.value.entidad) {
        params.append('cod_entidad', filtros.value.entidad);
      }
      if (filtros.value.busqueda && filtros.value.busqueda.trim()) {
        params.append('search', filtros.value.busqueda.trim());
      }
      
      const url = `${API_URL}/preoperacion/detalles-insumo/?${params.toString()}`;
      console.log('🎯 Consultando filtros directos:', url);
      
      const response = await axios.get(url, { signal });
      return response.data;
    };
    
    // 🚀 CARGAR CON FILTROS JERÁRQUICOS - OPTIMIZADO (usa endpoint del backend)
    const cargarConFiltrosJerarquicos = async (pagina, signal) => {
      /**
       * OPTIMIZACIÓN: En lugar de hacer N+1 peticiones en el frontend,
       * ahora usamos filtros directos en el backend que ejecutan las
       * queries de forma eficiente en la base de datos.
       */

      const params = new URLSearchParams();
      params.append('page', pagina.toString());
      params.append('page_size', '100'); // Aumentamos porque ahora es rápido

      // Determinar el tipo de filtro jerárquico
      let tipoFiltro = '';
      let descripcionFiltro = '';

      if (filtros.value.insumo) {
        // 🎯 FILTRO POR INSUMO - Usar nuevo parámetro del backend
        params.append('cod_insumo', filtros.value.insumo);
        tipoFiltro = 'insumo';
        descripcionFiltro = `Insumo: ${filtros.value.insumo}`;
        iniciarProgreso('Consultando detalles del insumo...', false);

      } else if (filtros.value.municipio) {
        // 🏛️ FILTRO POR MUNICIPIO - Usar nuevo parámetro del backend
        params.append('cod_municipio', filtros.value.municipio);
        tipoFiltro = 'municipio';
        const municipioNombre = municipios.value.find(m => m.cod_municipio == filtros.value.municipio)?.nom_municipio || filtros.value.municipio;
        descripcionFiltro = `Municipio: ${municipioNombre}`;
        iniciarProgreso('Consultando detalles del municipio...', false);

      } else if (filtros.value.departamento) {
        // 🏢 FILTRO POR DEPARTAMENTO - Usar nuevo parámetro del backend
        params.append('cod_departamento', filtros.value.departamento);
        tipoFiltro = 'departamento';
        const deptoNombre = departamentos.value.find(d => d.cod_depto == filtros.value.departamento)?.nom_depto || filtros.value.departamento;
        descripcionFiltro = `Departamento: ${deptoNombre}`;
        iniciarProgreso('Consultando detalles del departamento...', true);
        mostrarMensajePaciencia.value = true;
      }

      // Agregar filtros adicionales si existen
      if (filtros.value.estado) params.append('estado', filtros.value.estado);
      if (filtros.value.zona) params.append('zona', filtros.value.zona);
      if (filtros.value.entidad) params.append('cod_entidad', filtros.value.entidad);
      if (filtros.value.busqueda && filtros.value.busqueda.trim()) {
        params.append('search', filtros.value.busqueda.trim());
      }

      actualizarProgreso(30, 100, 'Ejecutando consulta optimizada...', descripcionFiltro, tipoFiltro === 'departamento', '1/2');

      try {
        const url = `${API_URL}/preoperacion/detalles-insumo/?${params.toString()}`;
        console.log(`🚀 Consulta optimizada (${tipoFiltro}):`, url);

        const response = await axios.get(url, { signal });

        actualizarProgreso(90, 100, 'Procesando resultados...', '', false, '2/2');

        // Procesar respuesta
        let detallesObtenidos = [];
        if (response.data.results) {
          detallesObtenidos = response.data.results;
          totalRegistros.value = response.data.count || detallesObtenidos.length;
          hayMasResultados.value = !!response.data.next;
        } else if (Array.isArray(response.data)) {
          detallesObtenidos = response.data;
          totalRegistros.value = detallesObtenidos.length;
          hayMasResultados.value = false;
        }

        actualizarProgreso(100, 100, 'Completado',
          `${detallesObtenidos.length} detalles encontrados`, false, 'Final');

        console.log(`✅ Filtros jerárquicos optimizados: ${detallesObtenidos.length} detalles (${tipoFiltro})`);

        // Ya no necesitamos marcar como limitado - el backend devuelve TODOS los resultados
        resultadosLimitados.value = false;

        return detallesObtenidos;

      } catch (err) {
        if (err.name === 'AbortError') {
          console.log('🚫 Petición cancelada');
          throw err;
        }
        console.error('❌ Error en consulta optimizada:', err);
        actualizarProgreso(100, 100, 'Error', err.message, false, 'Error');
        throw err;
      }
    };
    
    // 🔧 FUNCIÓN AUXILIAR PARA CARGAR DETALLES POR CLASIFICACIÓN
    const cargarDetallesPorClasificacion = async (clasifId, signal) => {
      try {
        const params = new URLSearchParams();
        params.append('cod_clasificacion', clasifId);
        params.append('page_size', '50');
        
        // Aplicar filtros adicionales
        if (filtros.value.estado) params.append('estado', filtros.value.estado);
        if (filtros.value.zona) params.append('zona', filtros.value.zona);
        if (filtros.value.entidad) params.append('cod_entidad', filtros.value.entidad);
        
        const response = await axios.get(
          `${API_URL}/preoperacion/detalles-insumo/?${params.toString()}`,
          { signal }
        );
        
        return response.data.results || response.data || [];
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.warn(`Error obteniendo detalles para clasificación ${clasifId}`);
        }
        return [];
      }
    };
    
    // 📋 CARGAR SIN FILTROS (inicial)
    const cargarSinFiltros = async (pagina, signal) => {
      const params = new URLSearchParams();
      params.append('page', pagina.toString());
      params.append('page_size', elementosPorPagina.value.toString());
      
      const url = `${API_URL}/preoperacion/detalles-insumo/?${params.toString()}`;
      console.log('📋 Carga inicial:', url);
      
      const response = await axios.get(url, { signal });
      return response.data;
    };
    
    // 🏷️ CARGAR NOMBRES CON PROGRESO
    const cargarNombresConProgreso = async (signal) => {
      if (detalles.value.length === 0) return;
      
      console.log(`Cargando nombres para ${detalles.value.length} detalles...`);
      
      // Solo mostrar progreso si hay muchos elementos
      const mostrarProgresoNombres = detalles.value.length > 15;
      
      if (mostrarProgresoNombres && !progresoCarga.value.mostrar) {
        iniciarProgreso('Cargando información adicional...', false);
      }
      
      try {
        const loteSize = 5; // Procesar de 5 en 5
        
        for (let i = 0; i < detalles.value.length; i += loteSize) {
          const loteDetalles = detalles.value.slice(i, i + loteSize);
          
          // Procesar lote en paralelo
          const promesasLote = loteDetalles.map(detalle => 
            cargarDatosDetalle(detalle, signal).catch(err => {
              if (err.name !== 'AbortError') {
                console.warn(`Error cargando datos del detalle ${detalle.cod_detalle}:`, err);
              }
            })
          );
          
          await Promise.all(promesasLote);
          
          // Actualizar progreso si corresponde
          if (mostrarProgresoNombres) {
            const progreso = ((i + loteSize) / detalles.value.length) * 100;
            actualizarProgreso(
              Math.min(progreso, 100), 
              100, 
              'Cargando información adicional...', 
              `${Math.min(i + loteSize, detalles.value.length)} de ${detalles.value.length} registros procesados`,
              false,
              'Final'
            );
          }
          
          // Forzar reactualización de la UI cada 3 lotes
          if (i % (loteSize * 3) === 0) {
            detalles.value = [...detalles.value];
          }
          
          // Pequeña pausa para no saturar
          if (i + loteSize < detalles.value.length) {
            await new Promise(resolve => setTimeout(resolve, mostrarProgresoNombres ? 100 : 50));
          }
        }
        
        console.log('✅ Carga de nombres completada');
        
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.warn('Error en carga de nombres:', err);
        }
      }
    };
    

    // 📋 CARGAR DATOS DE UN DETALLE ESPECÍFICO
    const cargarDatosDetalle = async (detalle, signal) => {
      try {
        if (detalle.cod_clasificacion) {
          const clasifResponse = await axios.get(
            `${API_URL}/preoperacion/clasificaciones/${detalle.cod_clasificacion}/`,
            { signal }
          );
          
          detalle.clasificacion_nombre = clasifResponse.data.nombre;
          
          if (clasifResponse.data.cod_insumo) {
            const insumoResponse = await axios.get(
              `${API_URL}/preoperacion/insumos/${clasifResponse.data.cod_insumo}/`,
              { signal }
            );
            
            if (insumoResponse.data.cod_municipio) {
              const municipioResponse = await axios.get(
                `${API_URL}/preoperacion/municipios/${insumoResponse.data.cod_municipio}/`,
                { signal }
              );
              detalle.municipio_nombre = municipioResponse.data.nom_municipio;
            }
          }
        }
        
        if (detalle.cod_entidad) {
          const entidadResponse = await axios.get(
            `${API_URL}/preoperacion/entidades/${detalle.cod_entidad}/`,
            { signal }
          );
          detalle.entidad_nombre = entidadResponse.data.nom_entidad;
        }

        // ✅ CARGAR NOMBRE DEL CENTRO POBLADO SI APLICA
        if (detalle.zona === 'CENTROS POBLADOS' && detalle.cod_centro_poblado) {
          try {
            const centroResponse = await axios.get(
              `${API_URL}/preoperacion/centros-poblados/${detalle.cod_centro_poblado}/`,
              { signal }
            );
            detalle.centro_poblado_nombre = centroResponse.data.nom_centro_poblado;
            console.log(`✅ Centro poblado cargado: ${detalle.centro_poblado_nombre}`);
          } catch (err) {
            console.warn(`⚠️ No se pudo cargar centro poblado ${detalle.cod_centro_poblado}:`, err);
            detalle.centro_poblado_nombre = 'No disponible';
          }
        }
      } catch (err) {
        if (err.name !== 'AbortError') {
          throw err;
        }
      }
    };
    
    // Cargar departamentos
    const cargarDepartamentos = async () => {
      try {
        const response = await axios.get(`${API_URL}/preoperacion/departamentos/`);
        departamentos.value = response.data.results || response.data;
      } catch (err) {
        console.error('Error al cargar departamentos:', err);
      }
    };
    
    // 🚀 Cargar municipios CON EJECUCIÓN AUTOMÁTICA
    const cargarMunicipios = async () => {
      // Limpiar dependientes
      municipios.value = [];
      filtros.value.municipio = '';
      filtros.value.insumo = '';
      filtros.value.clasificacion = '';
      
      if (!filtros.value.departamento) {
        // Si no hay departamento, ejecutar consulta (carga inicial)
        aplicarFiltros();
        return;
      }
      
      try {
        const response = await axios.get(
          `${API_URL}/preoperacion/municipios/?cod_depto=${filtros.value.departamento}`
        );
        municipios.value = response.data.results || response.data;
        console.log(`🏛️ Cargados ${municipios.value.length} municipios para departamento ${filtros.value.departamento}`);
        
        // 🚀 EJECUTAR AUTOMÁTICAMENTE la consulta con filtro de departamento
        aplicarFiltros();
        
      } catch (err) {
        console.error('Error al cargar municipios:', err);
      }
    };
    
    // 🚀 Cargar insumos CON EJECUCIÓN AUTOMÁTICA  
    const cargarInsumos = async () => {
      // Limpiar dependientes
      insumos.value = [];
      filtros.value.insumo = '';
      filtros.value.clasificacion = '';
      
      if (!filtros.value.municipio) {
        // Si se limpia municipio, ejecutar con filtro de departamento
        aplicarFiltros();
        return;
      }
      
      try {
        // 🚀 OPTIMIZACIÓN: Cargar insumos y categorías en paralelo (evita N+1)
        const [insumosResponse, categoriasResponse] = await Promise.all([
          axios.get(`${API_URL}/preoperacion/municipios/${filtros.value.municipio}/insumos/`),
          axios.get(`${API_URL}/preoperacion/categorias/`)
        ]);

        const insumosData = insumosResponse.data.results || insumosResponse.data;
        const categoriasData = categoriasResponse.data.results || categoriasResponse.data;

        // Crear mapa de categorías para lookup O(1)
        const categoriasMap = new Map();
        categoriasData.forEach(cat => {
          categoriasMap.set(cat.cod_categoria, cat.nom_categoria);
        });

        // Asignar categorías sin peticiones adicionales
        const insumosConCategorias = insumosData.map(insumo => {
          if (insumo.categoria && insumo.categoria.nom_categoria) {
            return { ...insumo, categoria_nombre: insumo.categoria.nom_categoria };
          }
          return {
            ...insumo,
            categoria_nombre: categoriasMap.get(insumo.cod_categoria) || 'Categoría no disponible'
          };
        });

        insumos.value = insumosConCategorias;
        console.log(`📦 Cargados ${insumos.value.length} insumos (optimizado, sin N+1)`);
        
        // 🚀 EJECUTAR AUTOMÁTICAMENTE la consulta con filtro de municipio
        aplicarFiltros();
        
      } catch (err) {
        console.error('Error al cargar insumos:', err);
        error.value = 'Error al cargar insumos.';
      }
    };
    
    // 🚀 Cargar clasificaciones CON EJECUCIÓN AUTOMÁTICA
    const cargarClasificaciones = async () => {
      clasificaciones.value = [];
      filtros.value.clasificacion = '';
      
      if (!filtros.value.insumo) {
        // Si se limpia insumo, ejecutar con filtro de municipio
        aplicarFiltros();
        return;
      }
      
      try {
        const response = await axios.get(
          `${API_URL}/preoperacion/insumos/${filtros.value.insumo}/clasificaciones/`
        );
        clasificaciones.value = response.data.results || response.data;
        console.log(`🏷️ Cargadas ${clasificaciones.value.length} clasificaciones para insumo ${filtros.value.insumo}`);
        
        // 🚀 EJECUTAR AUTOMÁTICAMENTE la consulta con filtro de insumo
        aplicarFiltros();
        
      } catch (err) {
        console.error('Error al cargar clasificaciones:', err);
        error.value = 'Error al cargar clasificaciones.';
      }
    };
    
    // Cargar dominios
    const cargarDominios = async () => {
      try {
        const [zonasRes, entidadesRes] = await Promise.all([
          axios.get(`${API_URL}/preoperacion/zonas/`),
          axios.get(`${API_URL}/preoperacion/entidades/`)
        ]);
        
        zonas.value = zonasRes.data.results || zonasRes.data;
        entidades.value = entidadesRes.data.results || entidadesRes.data;
      } catch (err) {
        console.error('Error al cargar dominios:', err);
      }
    };
    
    // 🔄 APLICAR FILTROS CON AJUSTE AUTOMÁTICO DE PAGINACIÓN
    const aplicarFiltros = () => {
      // Ajustar tamaño de página según filtros
      const tieneFlitros = filtros.value.departamento || filtros.value.municipio || 
                          filtros.value.insumo || filtros.value.clasificacion || 
                          filtros.value.estado || filtros.value.zona || filtros.value.entidad;
      
      if (tieneFlitros) {
        elementosPorPagina.value = 25; // Más generoso con filtros
        mostrarAdvertencia.value = false;
      } else {
        elementosPorPagina.value = 10; // Restrictivo sin filtros
        mostrarAdvertencia.value = true;
      }
      
      paginaActual.value = 1;
      cargarDetalles(1);
    };
    
    // 🧹 LIMPIAR FILTROS
    const limpiarFiltros = () => {
      filtros.value = {
        departamento: '',
        municipio: '',
        insumo: '',
        clasificacion: '',
        estado: '',
        zona: '',
        entidad: '',
        busqueda: ''
      };
      
      municipios.value = [];
      insumos.value = [];
      clasificaciones.value = [];
      
      paginaActual.value = 1;
      mostrarAdvertencia.value = true;
      mostrarMensajePaciencia.value = false;
      elementosPorPagina.value = 10; // Volver a límite inicial
      
      cargarDetalles(1);
    };
    
    // 🔄 CAMBIAR PÁGINA
    const cambiarPagina = (nuevaPagina) => {
      if (nuevaPagina >= 1 && nuevaPagina <= totalPaginas.value && !cargando.value) {
        cargarDetalles(nuevaPagina);
      }
    };
    
    // 📊 COMPUTADAS
    const totalPaginas = computed(() => {
      return Math.ceil(totalRegistros.value / elementosPorPagina.value) || 1;
    });
    
    const detallesVisibles = computed(() => {
      return detalles.value;
    });
    
    const insumosConCategoria = computed(() => {
      return insumos.value.map(insumo => ({
        ...insumo,
        categoria_nombre: insumo.categoria?.nom_categoria || 'Categoría no disponible'
      }));
    });
    
    // 🔢 BOTONES NUMÉRICOS PARA PAGINACIÓN
    const botonesNumericos = computed(() => {
      const botones = [];
      const maxBotones = 5;
      const total = totalPaginas.value;
      const actual = paginaActual.value;
      
      if (total <= maxBotones) {
        for (let i = 1; i <= total; i++) {
          botones.push({
            valor: i,
            texto: i.toString(),
            activo: i === actual,
            ellipsis: false
          });
        }
      } else {
        // Lógica para páginas con ellipsis
        botones.push({ valor: 1, texto: '1', activo: actual === 1, ellipsis: false });
        
        let inicio = Math.max(2, actual - 1);
        let fin = Math.min(total - 1, actual + 1);
        
        if (actual <= 3) fin = Math.min(4, total - 1);
        if (actual >= total - 2) inicio = Math.max(2, total - 3);
        
        if (inicio > 2) {
          botones.push({ valor: null, texto: '...', activo: false, ellipsis: true });
        }
        
        for (let i = inicio; i <= fin; i++) {
          botones.push({ valor: i, texto: i.toString(), activo: i === actual, ellipsis: false });
        }
        
        if (fin < total - 1) {
          botones.push({ valor: null, texto: '...', activo: false, ellipsis: true });
        }
        
        if (total > 1) {
          botones.push({ valor: total, texto: total.toString(), activo: actual === total, ellipsis: false });
        }
      }
      
      return botones;
    });
    
    // 🎨 FORMATEAR ZONA CON CENTRO POBLADO
    const formatZonaConCentroPoblado = (detalle) => {
      if (!detalle.zona) return 'No disponible';
      
      // Si es centro poblado y tiene el código y nombre, mostrar formato especial
      if (detalle.zona === 'CENTROS POBLADOS' && detalle.cod_centro_poblado) {
        const nombreCentro = detalle.centro_poblado_nombre || 'Cargando...';
        return `CP: ${nombreCentro}`;
      }
      
      // Para otras zonas, mostrar normal
      return detalle.zona;
    };
    
    // 🎨 FORMATEAR ÁREA
    const formatArea = (area) => {
      if (!area) return 'No disponible';
      const numero = parseFloat(area);
      if (isNaN(numero)) return area;
      return `${numero.toLocaleString('es-CO', { maximumFractionDigits: 3 })} km²`;
    };
    
    // 🎨 FORMATEAR PORCENTAJE
    const formatPorcentaje = (porcentaje) => {
      if (!porcentaje) return 'No disponible';
      const numero = parseFloat(porcentaje);
      if (isNaN(numero)) return porcentaje;
      return `${numero.toFixed(1)}%`;
    };
    
    // Funciones de utilidad
    const ordenarPor = (campo) => {
      if (ordenacion.value.campo === campo) {
        ordenacion.value.ascendente = !ordenacion.value.ascendente;
      } else {
        ordenacion.value.campo = campo;
        ordenacion.value.ascendente = true;
      }
    };
    
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
    
    const getEstadoClass = (estado) => {
      if (!estado) return 'badge-secondary';
      
      switch (estado) {
        case 'OFICIALIZADO': return 'badge-success';
        case 'OFICIALIZADO PARCIAL': return 'badge-info';
        case 'EN PRODUCCION': return 'badge-primary';
        case 'POR PRODUCIR': return 'badge-warning';
        case 'NO SE PRODUCIRA': return 'badge-danger';
        case 'SIN FECHA DEFINIDA': return 'badge-secondary';
        default: return 'badge-secondary';
      }
    };
    
    // Funciones de modal
    const verDetalle = (detalle) => {
      modalDetalle.value.detalle = detalle;
      modalDetalle.value.mostrar = true;
    };
    
    const editarDetalle = (detalle) => {
      if (modalDetalle.value.mostrar) {
        modalDetalle.value.mostrar = false;
      }
      router.push(`/gestion-informacion/detalles/${detalle.cod_detalle}`);
    };
    
    const confirmarEliminar = (detalle) => {
      modalEliminar.value.detalle = detalle;
      modalEliminar.value.mostrar = true;
    };
    
    const eliminarDetalle = async () => {
      if (!modalEliminar.value.detalle) return;
      
      try {
        cargando.value = true;
        
        const token = localStorage.getItem('token');
        if (!token) {
          alert('No se encontró token de autenticación. Por favor, inicie sesión.');
          modalEliminar.value.mostrar = false;
          router.push('/login');
          return;
        }
        
        const config = { headers: { 'Authorization': `Token ${token}` } };
        const detalleId = modalEliminar.value.detalle.cod_detalle;
        
        await axios.delete(`${API_URL}/preoperacion/detalles-insumo/${detalleId}/`, config);
        
        modalEliminar.value.mostrar = false;
        await cargarDetalles(paginaActual.value);
        alert('Detalle eliminado con éxito');
      } catch (err) {
        console.error('Error al eliminar detalle:', err);
        alert(`Error: ${err.response?.data || 'Error desconocido'}`);
      } finally {
        cargando.value = false;
      }
    };
    
    const exportarDatos = () => {
      if (!detalles.value.length) {
        alert('No hay datos para exportar');
        return;
      }
      
      try {
        const headers = [
          'Código', 'Municipio', 'Clasificación', 'Estado', 'Zona/Centro Poblado', 'Entidad', 
          'Escala', 'Formato', 'Área (km²)', 'Cubrimiento', '% Cubrimiento', 'Vigencia',
          'Fecha Entrega', 'Fecha Disposición', 'Ruta Archivo', 'Usuario', 'Observaciones'
        ];
        
        const rows = detalles.value.map(detalle => [
          detalle.cod_detalle,
          detalle.municipio_nombre || 'Sin municipio',
          detalle.clasificacion_nombre || 'Sin clasificación',
          detalle.estado || '',
          formatZonaConCentroPoblado(detalle),
          detalle.entidad_nombre || 'Sin entidad',
          detalle.escala || '',
          detalle.formato_tipo || '',
          detalle.area || '',
          detalle.cubrimiento || '',
          detalle.porcentaje_cubrimiento || '',
          detalle.vigencia || '',
          formatFecha(detalle.fecha_entrega),
          formatFecha(detalle.fecha_disposicion),
          detalle.ruta_archivo || '',
          detalle.cod_usuario || '',
          detalle.observacion || ''
        ]);
        
        const BOM = '\uFEFF';
        const csvContent = BOM + [
          headers.join(','),
          ...rows.map(row => row.map(cell => 
            `"${String(cell).replace(/"/g, '""')}"`
          ).join(','))
        ].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', `detalles_insumos_${new Date().toISOString().slice(0, 10)}.csv`);
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } catch (err) {
        console.error('Error al exportar datos:', err);
        alert('Error al exportar datos');
      }
    };
    
    const navigateToCreate = () => {
      router.push('/gestion-informacion/detalles/crear');
    };
    
    // 🗃️ MONTAR COMPONENTE CON WATCHERS AUTOMÁTICOS
    onMounted(async () => {
      if (!authStore.isAuthenticated) {
        router.push('/login');
        return;
      }
      
      try {
        await Promise.all([
          cargarDepartamentos(),
          cargarDominios()
        ]);
        
        // Carga inicial: solo 10 registros
        elementosPorPagina.value = 10;
        await cargarDetalles(1);
        
        // 🚀 CONFIGURAR WATCHERS PARA EJECUCIÓN AUTOMÁTICA
        
        // Watch para filtros no jerárquicos - EJECUCIÓN INMEDIATA
        const watchOptions = { immediate: false };
        
        // Estado
        watch(() => filtros.value.estado, (newVal, oldVal) => {
          if (newVal !== oldVal) {
            console.log(`🔄 Cambió estado: ${oldVal} → ${newVal}`);
            aplicarFiltros();
          }
        }, watchOptions);
        
        // Zona  
        watch(() => filtros.value.zona, (newVal, oldVal) => {
          if (newVal !== oldVal) {
            console.log(`🔄 Cambió zona: ${oldVal} → ${newVal}`);
            aplicarFiltros();
          }
        }, watchOptions);
        
        // Entidad
        watch(() => filtros.value.entidad, (newVal, oldVal) => {
          if (newVal !== oldVal) {
            console.log(`🔄 Cambió entidad: ${oldVal} → ${newVal}`);
            aplicarFiltros();
          }
        }, watchOptions);
        
        // Clasificación (filtro directo más específico)
        watch(() => filtros.value.clasificacion, (newVal, oldVal) => {
          if (newVal !== oldVal) {
            console.log(`🔄 Cambió clasificación: ${oldVal} → ${newVal}`);
            aplicarFiltros();
          }
        }, watchOptions);
        
        // Búsqueda con debounce
        let searchTimeout;
        watch(() => filtros.value.busqueda, (newVal, oldVal) => {
          if (newVal !== oldVal) {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
              console.log(`🔄 Cambió búsqueda: "${oldVal}" → "${newVal}"`);
              aplicarFiltros();
            }, 500); // Esperar 500ms después de que pare de escribir
          }
        }, watchOptions);
        
      } catch (err) {
        console.error('Error al cargar datos iniciales:', err);
        error.value = 'Error al cargar datos iniciales. Por favor, actualice la página.';
      }
    });
    
    // 🧹 LIMPIAR AL DESMONTAR
    onUnmounted(() => {
      if (abortController) {
        abortController.abort();
      }
    });
    
    return {
      // Estado y datos
      cargando,
      error,
      mensajeCarga,
      detalles,
      detallesVisibles,
      hayMasResultados,
      mostrarAdvertencia,
      mostrarMensajePaciencia,
      resultadosLimitados,
      progresoCarga,
      
      // Catálogos
      departamentos,
      municipios,
      insumos,
      insumosConCategoria,
      clasificaciones,
      zonas,
      entidades,
      
      // Filtros y ordenación
      filtros,
      ordenacion,
      
      // Paginación
      paginaActual,
      totalPaginas,
      botonesNumericos,
      totalRegistros,
      
      // Modales
      modalEliminar,
      modalDetalle,
      
      // Métodos
      cargarMunicipios,
      cargarInsumos,
      cargarClasificaciones,
      aplicarFiltros,
      limpiarFiltros,
      ordenarPor,
      cambiarPagina,
      formatFecha,
      formatZonaConCentroPoblado,
      formatArea,
      formatPorcentaje,
      getEstadoClass,
      navigateToCreate,
      verDetalle,
      editarDetalle,
      confirmarEliminar,
      eliminarDetalle,
      exportarDatos
    };
  }
};
</script>

<style scoped>
/* ✅ SCROLL Y MODAL MEJORADO */
.modal-xl {
  max-width: 1200px;
  margin: 1rem auto;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-content {
  border: none;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 90vh;
}

.modal-body {
  padding: 1.5rem;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  max-height: calc(90vh - 140px); /* Restar altura del header + footer */
}

/* ✅ SCROLL PERSONALIZADO PARA EL MODAL */
.modal-body::-webkit-scrollbar {
  width: 8px;
}

.modal-body::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.modal-body::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* ✅ INDICADOR VISUAL DE SCROLL */
.modal-body::before {
  content: '';
  position: sticky;
  top: 0;
  height: 3px;
  background: linear-gradient(90deg, rgba(0,123,255,0.8), rgba(0,123,255,0.2));
  z-index: 10;
  display: block;
  margin: -1.5rem -1.5rem 1rem -1.5rem;
}

/* ✅ ESTILOS MEJORADOS PARA EL MODAL DE DETALLE */
.info-section {
  margin-bottom: 1.5rem;
  padding: 1.25rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #007bff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.centro-poblado-detalle {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #e8f4fd;
  border-left: 4px solid #007bff;
  border-radius: 6px;
}

.centro-titulo {
  font-size: 1rem;
  font-weight: 600;
  color: #007bff;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
}

.centro-info-box {
  background-color: #f8f9fa;
  padding: 0.75rem;
  border-radius: 4px;
  margin-top: 0.5rem;
  border: 1px solid #dee2e6;
}

.centro-info-box p {
  margin: 0.25rem 0;
  font-size: 0.9rem;
}

.seccion-titulo {
  font-size: 1rem;
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #dee2e6;
  display: flex;
  align-items: center;
}

.codigo-highlight {
  background-color: #007bff;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-weight: bold;
}

.ruta-archivo {
  font-family: 'Courier New', monospace;
  background-color: #f8f9fa;
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #dee2e6;
  font-size: 0.85rem;
  word-break: break-all;
  margin-top: 0.25rem;
}

.observaciones-box {
  background-color: white;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 0.5rem;
  min-height: 80px;
  max-height: 150px;
  overflow-y: auto;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
}

.observaciones-box p {
  margin: 0;
  line-height: 1.6;
  color: #495057;
  font-size: 0.95rem;
}

/* ✅ PADDING EXTRA AL FINAL DEL CONTENIDO PARA SCROLL CÓMODO */
.detalle-info {
  font-size: 0.95rem;
  padding-bottom: 2rem; /* Espacio extra al final */
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #dee2e6;
  background-color: #f8f9fa;
  flex-shrink: 0;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.header-info {
  flex-grow: 1;
  text-align: center;
}

.scroll-hint {
  color: #6c757d;
  font-size: 0.75rem;
  font-style: italic;
  background-color: rgba(108,117,125,0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  display: inline-block;
}

/* Estilos para mensaje de paciencia */
.mensaje-paciencia {
  margin-bottom: 1rem;
  padding: 1rem;
  border-left: 4px solid #ffc107;
  background-color: #fff3cd;
  border-color: #ffeaa7;
}

.mensaje-header {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #856404;
}

.mensaje-header i {
  margin-right: 0.5rem;
}

.mensaje-texto {
  margin-bottom: 0.75rem;
  color: #856404;
}

.mensaje-sugerencias {
  color: #6c757d;
  font-size: 0.9em;
}

/* Estilos para la barra de progreso MEJORADA */
.progreso-container {
  margin-bottom: 1rem;
  padding: 1rem;
  border-left: 4px solid #007bff;
  background-color: #e7f1ff;
  border-color: #b8daff;
}

.progreso-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  font-weight: bold;
  color: #004085;
}

.progreso-header i {
  margin-right: 0.5rem;
}

.progreso-etapa {
  background: rgba(0, 123, 255, 0.1);
  color: #007bff;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
}

.progreso-tiempo {
  color: #28a745;
  font-size: 0.8rem;
  font-weight: normal;
  font-style: italic;
}

.progreso-bar {
  position: relative;
  width: 100%;
  height: 24px;
  background-color: #e9ecef;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 0.75rem;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
}

.progreso-fill {
  height: 100%;
  background: linear-gradient(90deg, #007bff, #0056b3);
  transition: width 0.5s ease-out;
  border-radius: 12px;
  position: relative;
  box-shadow: 0 1px 3px rgba(0,123,255,0.3);
}

.progreso-text-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #fff;
  font-weight: bold;
  font-size: 0.8rem;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
  z-index: 2;
}

.progreso-stats {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #004085;
}

.progreso-actual {
  color: #007bff;
  font-size: 1.1rem;
}

.progreso-separador {
  margin: 0 0.5rem;
  color: #6c757d;
}

.progreso-total {
  color: #6c757d;
}

.progreso-detalle {
  display: flex;
  align-items: center;
  text-align: center;
  color: #6c757d;
  font-size: 0.9em;
  margin-bottom: 0.5rem;
  background-color: rgba(255, 255, 255, 0.7);
  padding: 0.5rem;
  border-radius: 6px;
}

.progreso-detalle i {
  margin-right: 0.25rem;
}

.progreso-tip {
  text-align: center;
  color: #6c757d;
  font-size: 0.85em;
  background-color: rgba(255, 255, 255, 0.8);
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid rgba(0,123,255,0.1);
}

.small-icon {
  font-size: 14px;
  margin-right: 0.25rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinning {
  animation: spin 1s linear infinite;
}

.filtros-loading {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #007bff;
  font-size: 0.9rem;
  margin-left: 1rem;
}

.filtros-loading .material-icons {
  font-size: 1.1rem;
}

.loading-text {
  color: #6c757d;
  font-size: 1rem;
}

/* RESTO DE ESTILOS CSS... */
.detalles-list-container {
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
  align-items: center;
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

.btn-success {
  color: #fff;
  background-color: #28a745;
  border-color: #28a745;
}

.btn-success:hover {
  color: #fff;
  background-color: #218838;
  border-color: #1e7e34;
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

.results-info {
  padding: 0.75rem 1.25rem;
  margin-bottom: 1rem;
  border: 1px solid #bee5eb;
  border-radius: 0.25rem;
  color: #0c5460;
  background-color: #d1ecf1;
  border-left: 4px solid #17a2b8;
}

.results-info i {
  margin-right: 0.5rem;
  color: #0c5460;
}

.alert {
  padding: 0.75rem 1.25rem;
  margin-bottom: 1rem;
  border: 1px solid transparent;
  border-radius: 0.25rem;
}

.alert-warning {
  color: #856404;
  background-color: #fff3cd;
  border-color: #ffeaa7;
  border-left: 4px solid #ffc107;
}

.alert-info {
  color: #0c5460;
  background-color: #d1ecf1;
  border-color: #bee5eb;
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

.badge-primary {
  color: #fff;
  background-color: #007bff;
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
  transition: all 0.2s;
}

.btn-pagination:hover:not(.disabled) {
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
  opacity: 0.65;
}

.text-muted {
  color: #6c757d;
}

.text-danger {
  color: #dc3545;
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
  animation: modalFadeIn 0.3s ease-out;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.modal-dialog {
  width: 100%;
  max-width: 500px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.modal-dialog.modal-lg {
  max-width: 900px;
  margin: 1rem auto;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
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
  padding: 0.25rem;
  line-height: 1;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-button:hover {
  background-color: #e9ecef;
  color: #495057;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #dee2e6;
  background-color: #f8f9fa;
  flex-shrink: 0;
}

.col-md-6 {
  padding: 0.5rem;
  flex: 0 0 50%;
  min-width: 0;
}

.col-12 {
  padding: 0.5rem;
  flex: 0 0 100%;
}

.material-icons {
  vertical-align: middle;
}

@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .actions-bar {
    width: 100%;
  }

  .actions-bar .btn {
    flex: 1;
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

  .modal-dialog.modal-lg, .modal-dialog.modal-xl {
    max-width: calc(100% - 1rem);
    margin: 0.5rem;
    max-height: calc(100vh - 1rem);
  }

  .modal-body {
    max-height: calc(100vh - 180px);
  }

  /* ✅ SCROLL HINT PARA MÓVIL */
  .modal-body::after {
    content: '⬇️ Desliza para ver más información';
    position: sticky;
    bottom: 0;
    display: block;
    text-align: center;
    background: linear-gradient(transparent, rgba(248,249,250,0.9));
    padding: 1rem 0 0.5rem 0;
    margin: 1rem -1.5rem -1.5rem -1.5rem;
    color: #6c757d;
    font-size: 0.8rem;
    font-style: italic;
  }

  .scroll-hint {
    display: none; /* Ocultar en móvil porque usamos el ::after */
  }

  .modal-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .header-info {
    order: 2;
    width: 100%;
    text-align: left;
  }

  .close-button {
    order: 3;
    align-self: flex-end;
    margin-top: -2rem;
  }

  .modal-title {
    order: 1;
    font-size: 1rem;
  }

  .info-section {
    margin-bottom: 1rem;
    padding: 1rem;
  }

  .col-md-6 {
    flex: 0 0 100%;
    max-width: 100%;
  }
}
</style>