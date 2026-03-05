<template>
  <div class="notificaciones-page">
    <!-- Toast de notificación profesional -->
    <Transition name="toast">
      <div v-if="toastVisible" :class="['toast-notification', `toast-${toastType}`]">
        <div class="toast-icon">
          <i class="material-icons">{{ toastType === 'error' ? 'error_outline' : toastType === 'success' ? 'check_circle' : 'info' }}</i>
        </div>
        <div class="toast-content">
          <div class="toast-title">{{ toastTitle }}</div>
          <div class="toast-message" v-html="toastMessage"></div>
        </div>
        <button class="toast-close" @click="cerrarToast">
          <i class="material-icons">close</i>
        </button>
      </div>
    </Transition>

    <div class="container">
      <div class="page-header">
        <h1 class="page-title">
          <i class="material-icons">notifications</i>
          Notificaciones
        </h1>
        <p class="page-description">
          Consulta las últimas actualizaciones y cambios en el sistema
        </p>
      </div>
      
      <!-- Filtros de búsqueda -->
      <div class="filters-section">
        <div class="search-bar">
          <i class="material-icons">search</i>
          <input 
            type="text" 
            v-model="searchQuery" 
            @input="handleSearch" 
            placeholder="Buscar en notificaciones..."
          />
          <button v-if="searchQuery" @click="clearSearch">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="filters">
          <div class="filter-group">
            <label for="tipo">Tipo</label>
            <select id="tipo" v-model="filtros.tipo" @change="aplicarFiltros">
              <option value="">Todos los tipos</option>
              <option value="preoperacion">Preoperación</option>
              <option value="postoperacion">Postoperación</option>
            </select>
          </div>
          
          <div class="filter-group">
            <label for="departamento">Departamento</label>
            <select id="departamento" v-model="filtros.departamento" @change="cargarMunicipios">
              <option value="">Todos los departamentos</option>
              <option 
                v-for="(depto, index) in departamentos" 
                :key="depto?.cod_depto || index" 
                :value="depto?.cod_depto || ''"
              >
                {{ depto?.nom_depto || 'Desconocido' }}
              </option>
            </select>
          </div>
          
          <div class="filter-group">
            <label for="municipio">Municipio</label>
            <select id="municipio" v-model="filtros.municipio" @change="aplicarFiltros">
              <option value="">Todos los municipios</option>
              <option 
                v-for="municipio in municipiosFiltrados" 
                :key="municipio.cod_municipio" 
                :value="municipio.cod_municipio"
              >
                {{ municipio.nom_municipio }}
              </option>
            </select>
          </div>
          
          <div class="filter-group">
            <label for="accion">Acción</label>
            <select id="accion" v-model="filtros.accion" @change="aplicarFiltros">
              <option value="">Todas las acciones</option>
              <option v-for="(accion, index) in acciones" :key="accion?.value || index" :value="accion?.value || ''">
                {{ accion?.label || 'Desconocido' }}
              </option>
            </select>
          </div>
          
          <div class="filter-group">
            <label for="tipoEntidad">Tipo Entidad</label>
            <select id="tipoEntidad" v-model="filtros.tipoEntidad" @change="aplicarFiltros">
              <option value="">Todos los tipos de entidad</option>
              <option v-for="(te, index) in tiposEntidad" :key="te.value || index" :value="te.value">
                {{ te.label }}
              </option>
            </select>
          </div>

          <div class="filter-group date-filter">
            <label>Rango de Fechas</label>
            <div class="date-range-inputs">
              <div class="date-field">
                <label for="fecha-desde">Desde:</label>
                <input 
                  type="date" 
                  id="fecha-desde" 
                  v-model="filtros.fechaDesde" 
                  class="date-input"
                  @change="aplicarFiltros"
                />
              </div>
              
              <div class="date-field">
                <label for="fecha-hasta">Hasta:</label>
                <input 
                  type="date" 
                  id="fecha-hasta" 
                  v-model="filtros.fechaHasta" 
                  class="date-input"
                  @change="aplicarFiltros"
                />
              </div>
            </div>
          </div>
          
          <div class="filter-group">
            <label for="usuario">Usuario</label>
            <select id="usuario" v-model="filtros.usuario" @change="aplicarFiltros">
              <option value="">Todos los usuarios</option>
              <option 
                v-for="usuario in usuariosUnicos" 
                :key="usuario" 
                :value="usuario"
              >
                {{ usuario }}
              </option>
            </select>
          </div>
          
          <div class="filter-options">
            <div class="filter-checkbox">
              <input type="checkbox" id="no-leidas" v-model="filtros.soloNoLeidas" @change="aplicarFiltros">
              <label for="no-leidas">Solo no leídas</label>
            </div>
            
            <div class="filter-actions">
              <button class="filter-button" @click="aplicarFiltros" :disabled="cargando">
                <i class="material-icons">filter_list</i>
                Aplicar filtros
              </button>
              
              <button class="clear-button" @click="limpiarFiltros">
                <i class="material-icons">clear_all</i>
                Limpiar filtros
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Información de carga -->
      <div class="load-info" v-if="notificaciones.length > 0">
        <div class="load-summary">
          <div class="load-stats">
            <span class="load-count">{{ notificacionesFiltradas.length }} notificaciones mostradas</span>
            <span v-if="notificaciones.length !== notificacionesFiltradas.length" class="filtered-info">
              de {{ notificaciones.length }} total
            </span>
            <span v-if="puedeCargarMas" class="more-available">| Más disponibles</span>
          </div>
          <button 
            v-if="puedeCargarMas" 
            class="load-more-button" 
            @click="cargarMasDatos" 
            :disabled="cargandoMas"
          >
            <i class="material-icons">expand_more</i>
            {{ cargandoMas ? 'Cargando...' : 'Cargar más (10K)' }}
          </button>
        </div>
      </div>
      
      <!-- Resumen de notificaciones y acciones -->
      <div class="summary-section">
        <div class="summary-stats">
          <div class="stat-chip">
            <span class="stat-label">Total:</span>
            <span class="stat-value">{{ notificaciones.length }}</span>
          </div>
          
          <div class="stat-chip">
            <span class="stat-label">No leídas:</span>
            <span class="stat-value">{{ contadorNoLeidas }}</span>
          </div>
          
          <div class="type-chips">
            <div class="type-chip preop-chip">
              <span class="type-label">Preoperación:</span>
              <span class="type-value">{{ contadorPre }}</span>
            </div>
            
            <div class="type-chip postop-chip">
              <span class="type-label">Postoperación:</span>
              <span class="type-value">{{ contadorPost }}</span>
            </div>
          </div>
        </div>
        
        <div class="summary-actions">
          <button 
            v-if="contadorNoLeidas > 0" 
            class="mark-read-button" 
            @click="marcarTodasLeidas"
          >
            <i class="material-icons">done_all</i>
            Marcar todas como leídas
          </button>
          
          <button class="refresh-button" @click="cargarNotificaciones" :disabled="cargando">
            <i class="material-icons">refresh</i>
            Actualizar
          </button>
          
          <button 
            class="export-button" 
            @click="exportarCSV"
            :disabled="notificaciones.length === 0"
          >
            <i class="material-icons">file_download</i>
            Exportar CSV
          </button>
          
          <!-- ✅ BOTÓN ESPECIAL PARA USUARIOS ESPECÍFICOS -->
          <button 
            v-if="mostrarBotonInformeEspecial"
            class="informe-especial-button" 
            @click="generarInformeUsuariosEspecificos"
            :disabled="cargandoInformeEspecial || !tieneRangoFechasValido"
            :title="!tieneRangoFechasValido ? 
              'Seleccione un rango de fechas válido para generar el informe' : 
              `Generar informe detallado de usuarios específicos (${filtros.fechaDesde || 'Sin fecha'} - ${filtros.fechaHasta || 'Sin fecha'})`"
          >
            <i class="material-icons">{{ cargandoInformeEspecial ? 'hourglass_empty' : 'assessment' }}</i>
            {{ cargandoInformeEspecial ? 'Generando...' : 'Informe Usuarios' }}
            <span v-if="tieneRangoFechasValido" class="button-badge">{{ 
              Math.ceil((new Date(filtros.fechaHasta).getTime() - new Date(filtros.fechaDesde).getTime()) / (1000 * 60 * 60 * 24)) + 1 
            }} días</span>
          </button>
        </div>
      </div>
      
      <!-- Tabla de notificaciones -->
      <div class="notifications-section">
        <!-- Estado de carga -->
        <div v-if="cargando" class="loading-indicator">
          <div class="spinner"></div>
          <span>Cargando notificaciones...</span>
        </div>
        
        <!-- Mensaje de error -->
        <div v-else-if="error" class="error-message">
          <i class="material-icons">error</i>
          <span>{{ error }}</span>
          <button @click="cargarNotificaciones">Reintentar</button>
        </div>
        
        <!-- Mensaje cuando no hay resultados -->
        <div v-else-if="notificaciones.length === 0" class="empty-message">
          <i class="material-icons">info</i>
          <span>No se encontraron notificaciones con los filtros seleccionados</span>
        </div>
        
        <!-- Tabla de notificaciones -->
        <div v-else class="table-container">
          <table class="notificaciones-table">
            <thead>
              <tr>
                <th @click="ordenarPor('id')" class="sortable">
                  ID
                  <i v-if="ordenacion.campo === 'id'" class="material-icons">
                    {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                  </i>
                </th>
                <th @click="ordenarPor('fecha_cambio')" class="sortable column-fecha">
                  Fecha
                  <i v-if="ordenacion.campo === 'fecha_cambio'" class="material-icons">
                    {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                  </i>
                </th>
                <th class="column-tipo">Tipo</th>
                <th class="column-entidad">Entidad</th>
                <th class="column-accion">Acción</th>
                <th class="column-ubicacion">Municipio</th>
                <th class="column-descripcion">Descripción</th>
                <th class="column-usuario">Usuario</th>
                <th class="column-acciones">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="notificacion in notificacionesPaginadas" 
                :key="(esTipoPreoperacion(notificacion) ? 'pre-' : 'post-') + notificacion.id"
                :class="{ 'no-leida': !notificacion.leido }"
              >
                <td>{{ notificacion.id }}</td>
                
                <td class="column-fecha">
                  <div class="fecha-info">
                    <span class="fecha">{{ formatearFecha(notificacion) }}</span>
                    <span class="tiempo">{{ formatearTiempo(notificacion) }}</span>
                  </div>
                </td>
                
                <td class="column-tipo">
                  <span 
                    class="tipo-badge" 
                    :class="{
                      'tipo-pre': notificacion.tipo_sistema === 'preoperacion',
                      'tipo-post': notificacion.tipo_sistema === 'postoperacion'
                    }"
                  >
                    {{ notificacion.tipo_sistema === 'preoperacion' ? 'Preoperación' : 'Postoperación' }}
                  </span>
                </td>
                
                <td class="column-entidad">
                  <div class="entidad-info">
                    <i class="material-icons">{{ getNotificationIcon(notificacion.tipo_entidad) }}</i>
                    <span>{{ formatearTipoEntidad(notificacion.tipo_entidad) }}</span>
                  </div>
                </td>
                
                <td class="column-accion">
                  <span class="accion-badge" :class="getAccionClass(notificacion.accion)">
                    {{ formatearAccion(notificacion.accion) }}
                  </span>
                </td>
                
                <td class="column-ubicacion">
                  <div v-if="getMunicipio(notificacion)" class="municipio-info">
                    <i class="material-icons">location_city</i>
                    <span>{{ getMunicipio(notificacion) }}</span>
                  </div>
                  <div v-else class="no-data">-</div>
                </td>
                
                <td class="column-descripcion">
                  <div class="descripcion-wrapper">
                    <p class="descripcion-texto" :title="getDescripcionCompleta(notificacion)">
                      {{ getDescripcionCompleta(notificacion) }}
                    </p>
                    <div v-if="getDetallesExtra(notificacion)" class="detalles-extra">
                      <span>{{ getDetallesExtra(notificacion) }}</span>
                    </div>
                    <!-- NUEVO: Indicador de archivo disponible -->
                    <div v-if="tieneArchivoDisponible(notificacion)" class="archivo-indicator">
                      <i class="material-icons">{{ getFileIcon(obtenerNombreArchivo(extraerRutaArchivo(notificacion))) }}</i>
                      <span class="archivo-text">Archivo disponible</span>
                    </div>
                  </div>
                </td>
                
                <td class="column-usuario">
                  <div v-if="getUsuario(notificacion)" class="usuario-info">
                    <i class="material-icons">person</i>
                    <span>{{ getUsuario(notificacion) }}</span>
                  </div>
                  <div v-else class="no-data">-</div>
                </td>
                
                <td class="column-acciones">
                  <div class="acciones-container">
                    <button 
                      v-if="!notificacion.leido" 
                      class="action-button mark-read" 
                      @click="marcarLeida(notificacion)"
                      title="Marcar como leída"
                    >
                      <i class="material-icons">done</i>
                    </button>
                    <button 
                      class="action-button view-details" 
                      @click="verDetalles(notificacion)"
                      title="Ver detalles"
                    >
                      <i class="material-icons">visibility</i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Paginación -->
        <div v-if="notificaciones.length > 0" class="pagination">
          <div class="pagination-info">
            Mostrando {{ paginaInicio }} - {{ paginaFin }} de {{ notificaciones.length }} notificaciones
          </div>
          
          <div class="pagination-controls">
            <button 
              class="pagination-button"
              @click="irAPagina(paginaActual - 1)"
              :disabled="paginaActual === 1"
            >
              <i class="material-icons">chevron_left</i>
            </button>
            
            <span 
              v-for="pagina in paginas" 
              :key="pagina.numero"
              :class="{ 
                'page-number': true, 
                'active': pagina.numero === paginaActual,
                'ellipsis': pagina.esEllipsis
              }"
              @click="pagina.esEllipsis ? null : irAPagina(pagina.numero)"
            >
              {{ pagina.esEllipsis ? '...' : pagina.numero }}
            </span>
            
            <button 
              class="pagination-button"
              @click="irAPagina(paginaActual + 1)"
              :disabled="paginaActual === totalPaginas"
            >
              <i class="material-icons">chevron_right</i>
            </button>
          </div>
          
          <div class="pagination-options">
            <label for="elementos-pagina">Elementos por página:</label>
            <select id="elementos-pagina" v-model="elementosPorPagina" @change="cambiarElementosPorPagina">
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Modal para ver detalles de notificación -->
    <div v-if="modalVisible" class="modal-overlay" @click="cerrarModal">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h2>Detalles de Notificación</h2>
          <button class="close-button" @click="cerrarModal">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div v-if="notificacionSeleccionada" class="modal-body">
          <div class="notificacion-detalle">
            <!-- Información básica -->
            <div class="detalle-seccion">
              <h3>Información General</h3>
              <div class="info-basica">
                <div class="detalle-campo">
                  <span class="campo-label">ID:</span>
                  <span class="campo-valor">{{ notificacionSeleccionada.id }}</span>
                </div>
                
                <div class="detalle-campo">
                  <span class="campo-label">Sistema:</span>
                  <span class="campo-valor">
                    {{ notificacionSeleccionada.tipo_sistema === 'preoperacion' ? 'Preoperación' : 'Postoperación' }}
                  </span>
                </div>
                
                <div class="detalle-campo">
                  <span class="campo-label">Tipo de Entidad:</span>
                  <span class="campo-valor">{{ formatearTipoEntidad(notificacionSeleccionada.tipo_entidad) }}</span>
                </div>
                
                <div class="detalle-campo">
                  <span class="campo-label">Acción:</span>
                  <span class="campo-valor">
                    <span class="accion-badge" :class="getAccionClass(notificacionSeleccionada.accion)">
                      {{ formatearAccion(notificacionSeleccionada.accion) }}
                    </span>
                  </span>
                </div>
                
                <div class="detalle-campo">
                  <span class="campo-label">Fecha y Hora:</span>
                  <span class="campo-valor">
                    {{ formatearFecha(notificacionSeleccionada) }} {{ formatearTiempo(notificacionSeleccionada) }}
                  </span>
                </div>
                
                <div class="detalle-campo">
                  <span class="campo-label">Estado:</span>
                  <span class="campo-valor">
                    <span class="estado-badge" :class="notificacionSeleccionada.leido ? 'estado-leido' : 'estado-no-leido'">
                      {{ notificacionSeleccionada.leido ? 'Leída' : 'No leída' }}
                    </span>
                  </span>
                </div>
                
                <div v-if="getMunicipio(notificacionSeleccionada)" class="detalle-campo">
                  <span class="campo-label">Municipio:</span>
                  <span class="campo-valor">{{ getMunicipio(notificacionSeleccionada) }}</span>
                </div>
                
                <div v-if="getUsuario(notificacionSeleccionada)" class="detalle-campo">
                  <span class="campo-label">Usuario:</span>
                  <span class="campo-valor">
                    <div class="usuario-info">
                      <i class="material-icons">person</i>
                      <span>{{ getUsuario(notificacionSeleccionada) }}</span>
                      <!-- NUEVO: Botón para ver historial de propietarios -->
                      <button 
                        class="btn-historial" 
                        @click="verHistorialPropietarios"
                        title="Ver historial de propietarios"
                      >
                        <i class="material-icons">history</i> Historial
                      </button>
                    </div>
                  </span>
                </div>

                <!-- NUEVA SECCIÓN PARA ARCHIVO -->
                <div v-if="extraerRutaArchivo(notificacionSeleccionada) && archivoDisponible(notificacionSeleccionada)" class="detalle-campo archivo-campo">
                  <span class="campo-label">Archivo Asociado:</span>
                  <div class="campo-valor archivo-info">
                    <div class="archivo-details">
                      <i class="material-icons archivo-icon">{{ getFileIcon(obtenerNombreArchivo(extraerRutaArchivo(notificacionSeleccionada))) }}</i>
                      <span class="archivo-nombre">{{ obtenerNombreArchivo(extraerRutaArchivo(notificacionSeleccionada)) }}</span>
                    </div>
                    <div class="archivo-actions">
                      <button 
                        class="btn-archivo ver-archivo" 
                        @click="verArchivoNotificacion(notificacionSeleccionada)"
                        :title="getFileExtension(obtenerNombreArchivo(extraerRutaArchivo(notificacionSeleccionada))) === 'pdf' ? 'Ver PDF en nueva ventana' : 
                              ['jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff', 'xlsx', 'xls', 'docx', 'doc'].includes(getFileExtension(obtenerNombreArchivo(extraerRutaArchivo(notificacionSeleccionada)))) ? 'Abrir archivo' : 'Descargar archivo'"
                      >
                        <i class="material-icons">{{ 
                          getFileExtension(obtenerNombreArchivo(extraerRutaArchivo(notificacionSeleccionada))) === 'pdf' ? 'open_in_new' : 
                          ['jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff', 'xlsx', 'xls', 'docx', 'doc'].includes(getFileExtension(obtenerNombreArchivo(extraerRutaArchivo(notificacionSeleccionada)))) ? 'visibility' : 'download' 
                        }}</i>
                        {{ getFileExtension(obtenerNombreArchivo(extraerRutaArchivo(notificacionSeleccionada))) === 'pdf' ? 'Ver' : 
                          ['jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff', 'xlsx', 'xls', 'docx', 'doc'].includes(getFileExtension(obtenerNombreArchivo(extraerRutaArchivo(notificacionSeleccionada)))) ? 'Abrir' : 'Descargar' }}
                      </button>
                      <button 
                        class="btn-archivo descargar-archivo" 
                        @click="descargarArchivoNotificacion(notificacionSeleccionada)"
                        title="Descargar archivo"
                      >
                        <i class="material-icons">download</i>
                        Descargar
                      </button>
                    </div>
                  </div>
                </div>
                <!-- FIN NUEVA SECCIÓN PARA ARCHIVO -->

              </div>
            </div>
            
            <!-- Descripción -->
            <div v-if="notificacionSeleccionada.descripcion" class="detalle-seccion">
              <h3>Descripción</h3>
              <div class="descripcion-completa">
                <p>{{ notificacionSeleccionada.descripcion }}</p>
              </div>
            </div>
            
            <!-- Datos de contexto -->
            <div v-if="notificacionSeleccionada.datos_contexto && Object.keys(notificacionSeleccionada.datos_contexto).length > 0" 
                class="detalle-seccion">
              <h3>Información Adicional</h3>
              <div class="datos-contexto">
                <template v-for="(valor, clave) in notificacionSeleccionada.datos_contexto" :key="clave">
                  <div class="detalle-campo">
                    <div class="campo-label">{{ formatearCampo(clave) }}:</div>
                    <div class="campo-valor">{{ formatearValor(valor) }}</div>
                  </div>
                </template>
              </div>
            </div>
            
            <!-- Mensaje si no hay datos adicionales -->
            <div v-else class="detalle-seccion">
              <div class="no-data-message">
                <i class="material-icons">info</i>
                <span>No hay información adicional disponible para esta notificación</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button 
            v-if="notificacionSeleccionada && !notificacionSeleccionada.leido" 
            class="btn btn-primary" 
            @click="marcarLeidaYCerrar"
          >
            <i class="material-icons">done</i>
            Marcar como leída y cerrar
          </button>
          <button class="btn btn-secondary" @click="cerrarModal">
            Cerrar
          </button>
        </div>
      </div>
    </div>
    
    <!-- NUEVO: Modal para historial de propietarios -->
    <HistorialPropietariosModal ref="historialModal" />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useNotificacionesStore } from '@/store/notificaciones';
import { useAuthStore } from '@/store/auth';
import { format, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';
import { getMunicipiosByDepartamento } from '@/api/municipios';
import { getDepartamentos } from '@/api/departamentos';
import type { Notificacion } from '@/models/notificacion';
import type { Departamento, Municipio } from '@/models/municipio';


import archivosService from '@/services/archivos';
import HistorialPropietariosModal from '@/components/notificaciones/HistorialPropietariosModal.vue';
import api, { API_URL } from '@/api/config';
import { linuxToWindowsPath, isPathLike } from '@/utils/pathUtils';


export default defineComponent({
  name: 'NotificacionesPage',
  
  components: {
    HistorialPropietariosModal
  },
  
  setup() {
    const router = useRouter();
    const notificacionesStore = useNotificacionesStore();
    const authStore = useAuthStore();
    const historialModal = ref(null);
    // Estado para notificaciones
    const notificaciones = ref<Notificacion[]>([]);
    const cargando = ref(false);
    const cargandoMas = ref(false);
    const error = ref<string | null>(null);
    const puedeCargarMas = ref(false);
    
    // ✅ ESTADO PARA INFORME ESPECIAL
    const cargandoInformeEspecial = ref(false);
    
    // CAMBIO: Offsets separados para cada tipo
    const offsetsPorTipo = ref({
      preoperacion: 0,
      postoperacion: 0
    });
    
    const ultimosParametros = ref<any>(null);
    
    // Estado para búsqueda y filtros
    const searchQuery = ref('');
    const filtros = ref({
      tipo: '',
      departamento: '',
      municipio: '',
      accion: '',
      tipoEntidad: '',
      fechaDesde: '',
      fechaHasta: '',
      soloNoLeidas: false,
      usuario: ''
    });
    
    // Estado para ordenación y paginación
    const ordenacion = ref({
      campo: 'fecha_cambio',
      ascendente: false
    });
    
    const paginaActual = ref(1);
    const elementosPorPagina = ref(20);
    
    // Estado para modal
    const modalVisible = ref(false);
    const notificacionSeleccionada = ref<Notificacion | null>(null);

    // Estado para toast de notificaciones
    const toastVisible = ref(false);
    const toastType = ref<'error' | 'success' | 'info'>('error');
    const toastTitle = ref('');
    const toastMessage = ref('');
    let toastTimeout: number | null = null;

    const mostrarToast = (tipo: 'error' | 'success' | 'info', titulo: string, mensaje: string, duracion = 8000) => {
      // Limpiar timeout anterior si existe
      if (toastTimeout) {
        clearTimeout(toastTimeout);
      }
      toastType.value = tipo;
      toastTitle.value = titulo;
      toastMessage.value = mensaje;
      toastVisible.value = true;

      // Auto-cerrar después de la duración
      toastTimeout = window.setTimeout(() => {
        cerrarToast();
      }, duracion);
    };

    const cerrarToast = () => {
      toastVisible.value = false;
      if (toastTimeout) {
        clearTimeout(toastTimeout);
        toastTimeout = null;
      }
    };

    // Estado para catálogos
    const departamentos = ref<Departamento[]>([]);
    const municipios = ref<Municipio[]>([]);
    const usuariosUnicos = ref<string[]>([]);
    
    // Acciones disponibles
    const acciones = [
      { value: 'crear', label: 'Crear' },
      { value: 'actualizar', label: 'Actualizar' },
      { value: 'eliminar', label: 'Eliminar' },
      { value: 'aprobar', label: 'Aprobar' },
      { value: 'rechazar', label: 'Rechazar' },
      { value: 'disponer', label: 'Disponer' },
      { value: 'evaluar', label: 'Evaluar' },
    ];

    // Tipos de entidad disponibles
    const tiposEntidad = [
      { value: 'detalle', label: 'Detalle de Insumo' },
      { value: 'archivo', label: 'Archivo' },
      { value: 'archivo_insumo', label: 'Archivo Insumo' },
      { value: 'clasificacion_insumo', label: 'Clasificacion Insumo' },
      { value: 'insumo', label: 'Insumo' },
      { value: 'municipio', label: 'Municipio' },
      { value: 'sistema', label: 'Sistema' },
    ];
    
    // ✅ COMPUTED PROPERTIES PARA INFORME ESPECIAL
    const mostrarBotonInformeEspecial = computed(() => {
      const usuariosAutorizados = ['andres.osorio', 'elizabeth.eraso'];
      
      let username = null;
      if (authStore.user) {
        username = authStore.user.username || 
                  authStore.user.userName || 
                  authStore.user.email?.split('@')[0] ||
                  authStore.user.id;
      }
      
      console.log('🔍 Debug botón especial:', {
        usuario_actual: username,
        usuarios_autorizados: usuariosAutorizados,
        debe_mostrar: username && usuariosAutorizados.includes(username)
      });
      
      return username && usuariosAutorizados.includes(username);
    });
    
    const tieneRangoFechasValido = computed(() => {
      return filtros.value.fechaDesde && filtros.value.fechaHasta && 
             filtros.value.fechaDesde <= filtros.value.fechaHasta;
    });
    
    // Computed properties
    const hayFiltrosActivos = computed(() => {
      return filtros.value.tipo || filtros.value.departamento || filtros.value.municipio || 
             filtros.value.accion || filtros.value.fechaDesde || filtros.value.fechaHasta || 
             filtros.value.soloNoLeidas || filtros.value.usuario || searchQuery.value;
    });
    
    const municipiosFiltrados = computed(() => {
      return municipios.value;
    });
    
    const notificacionesPaginadas = computed(() => {
      const inicio = (paginaActual.value - 1) * elementosPorPagina.value;
      const fin = inicio + elementosPorPagina.value;
      return notificacionesFiltradas.value.slice(inicio, fin);
    });
    
    const totalPaginas = computed(() => {
      return Math.ceil(notificaciones.value.length / elementosPorPagina.value) || 1;
    });
    
    const paginaInicio = computed(() => {
      return notificaciones.value.length === 0 ? 0 : (paginaActual.value - 1) * elementosPorPagina.value + 1;
    });
    
    const paginaFin = computed(() => {
      return Math.min(paginaActual.value * elementosPorPagina.value, notificaciones.value.length);
    });
    
    const paginas = computed(() => {
      const total = totalPaginas.value;
      const actual = paginaActual.value;
      
      if (total <= 7) {
        return Array.from({ length: total }, (_, i) => ({
          numero: i + 1,
          esEllipsis: false
        }));
      }
      
      if (actual <= 3) {
        return [
          { numero: 1, esEllipsis: false },
          { numero: 2, esEllipsis: false },
          { numero: 3, esEllipsis: false },
          { numero: 4, esEllipsis: false },
          { numero: 0, esEllipsis: true },
          { numero: total, esEllipsis: false }
        ];
      }
      
      if (actual >= total - 2) {
        return [
          { numero: 1, esEllipsis: false },
          { numero: 0, esEllipsis: true },
          { numero: total - 3, esEllipsis: false },
          { numero: total - 2, esEllipsis: false },
          { numero: total - 1, esEllipsis: false },
          { numero: total, esEllipsis: false }
        ];
      }
      
      return [
        { numero: 1, esEllipsis: false },
        { numero: 0, esEllipsis: true },
        { numero: actual - 1, esEllipsis: false },
        { numero: actual, esEllipsis: false },
        { numero: actual + 1, esEllipsis: false },
        { numero: 0, esEllipsis: true },
        { numero: total, esEllipsis: false }
      ];
    });
    
    const contadorNoLeidas = computed(() => {
      return notificacionesFiltradas.value.filter(n => !n.leido).length;
    });

    const contadorPre = computed(() => {
      return notificacionesFiltradas.value.filter(n => esTipoPreoperacion(n)).length;
    });

    const contadorPost = computed(() => {
      return notificacionesFiltradas.value.filter(n => !esTipoPreoperacion(n)).length;
    });
    
    // 🔧 FUNCIÓN CORREGIDA: Verificar si tiene archivos disponibles basado en roles correctos
    const tieneArchivoDisponible = (notificacion: Notificacion): boolean => {
      const ruta = extraerRutaArchivo(notificacion);
      if (!ruta) return false;
      
      return archivoDisponible(notificacion);
    };

    const notificacionesFiltradas = computed(() => {
      // Creamos una copia para no afectar el array original
      const notificacionesOrdenadas = [...notificaciones.value];
      
      // Definimos una función de prioridad para las acciones
      const getPrioridad = (accion: string): number => {
        const accionLower = accion?.toLowerCase();
        // Prioridad 1: Acciones de creación (mayor prioridad)
        if (accionLower === 'crear' || accionLower === 'insert') return 1;
        // Prioridad 2: Acciones de actualización o modificación
        if (accionLower === 'actualizar' || accionLower === 'update' || 
            accionLower === 'disponer' || accionLower === 'aprobar' ||
            accionLower === 'evaluar') return 2;
        // Prioridad 3: Otras acciones que no son ni creación ni eliminación
        if (accionLower !== 'eliminar' && accionLower !== 'delete') return 3;
        // Prioridad 4: Acciones de eliminación (menor prioridad)
        return 4;
      };
      
      // Ordenamos por prioridad de acción primero y luego por fecha
      notificacionesOrdenadas.sort((a, b) => {
        // Primero comparamos por prioridad de acción
        const prioridadA = getPrioridad(a.accion);
        const prioridadB = getPrioridad(b.accion);
        
        if (prioridadA !== prioridadB) {
          return prioridadA - prioridadB;
        }
        
        // Si las prioridades son iguales, mantenemos el orden por fecha
        // (respetando la dirección de ordenación seleccionada)
        const fechaA = new Date(a.fecha_cambio || 0).getTime();
        const fechaB = new Date(b.fecha_cambio || 0).getTime();
        
        return ordenacion.value.ascendente ? fechaA - fechaB : fechaB - fechaA;
      });
      
      return notificacionesOrdenadas;
    });
    // **FUNCIÓN PRINCIPAL**: Cargar notificaciones con filtros del backend
    const cargarNotificaciones = async () => {
      try {
        cargando.value = true;
        error.value = null;
        
        notificaciones.value = [];
        offsetsPorTipo.value = {
          preoperacion: 0,
          postoperacion: 0
        };
        puedeCargarMas.value = false;
        
        console.log("🔄 Cargando notificaciones con filtros del backend...");
        
        await cargarDatos(false);
        
        if (departamentos.value.length === 0) {
          await cargarCatalogos();
        }
        
        return true;
      } catch (err: any) {
        console.error("❌ Error general:", err);
        error.value = err.message || 'Error al cargar notificaciones';
        return false;
      } finally {
        cargando.value = false;
      }
    };
    
    const cargarMasDatos = async () => {
      if (cargandoMas.value || !puedeCargarMas.value) return;
      
      try {
        cargandoMas.value = true;
        console.log("📄 Cargando más datos...");
        
        await cargarDatos(true);
        
      } catch (err: any) {
        console.error("❌ Error cargando más datos:", err);
        error.value = err.message || 'Error al cargar más datos';
      } finally {
        cargandoMas.value = false;
      }
    };
    

    
    const actualizarUsuariosUnicos = () => {
      const usuarios = new Set<string>();
      notificaciones.value.forEach(n => {
        const usuario = getUsuario(n);
        if (usuario) usuarios.add(usuario);
      });
      usuariosUnicos.value = Array.from(usuarios).sort();
    };
    

    

    
    const aplicarFiltros = () => {
      paginaActual.value = 1;
      cargarNotificaciones();
    };
    
    const limpiarFiltros = () => {
      filtros.value = {
        tipo: '',
        departamento: '',
        municipio: '',
        accion: '',
        tipoEntidad: '',
        fechaDesde: '',
        fechaHasta: '',
        soloNoLeidas: false,
        usuario: '',
      };
      searchQuery.value = '';
      paginaActual.value = 1;
      municipios.value = [];
      cargarNotificaciones();
    };
    
    let searchTimeout: number;
    const handleSearch = () => {
      clearTimeout(searchTimeout);
      searchTimeout = window.setTimeout(() => {
        paginaActual.value = 1;
        cargarNotificaciones();
      }, 500);
    };
    
    const clearSearch = () => {
      searchQuery.value = '';
      paginaActual.value = 1;
      cargarNotificaciones();
    };
    

    
    // Funciones auxiliares (mantener las mismas)
    const esTipoPreoperacion = (notificacion: Notificacion): boolean => {
      if (notificacion.tipo_sistema) {
        return notificacion.tipo_sistema === 'preoperacion';
      }
      return notificacion.id < 1000000;
    };
    
    const getNotificationIcon = (tipoEntidad: string): string => {
      switch (tipoEntidad?.toLowerCase()) {
        case 'municipio': return 'location_city';
        case 'insumo': return 'folder';
        case 'clasificacion': return 'category';
        case 'detalle': return 'list_alt';
        case 'concepto': return 'comment';
        case 'disposicion': return 'check_circle';
        case 'componente': return 'view_module';
        case 'archivo': return 'insert_drive_file';
        default: return 'notifications';
      }
    };
    
    const formatearTipoEntidad = (tipo: string): string => {
      const mapaTipos: Record<string, string> = {
        'municipio': 'Municipio',
        'insumo': 'Insumo',
        'clasificacion': 'Clasificación',
        'detalle': 'Detalle',
        'componente': 'Componente',
        'disposicion': 'Disposición',
        'archivo': 'Archivo'
      };
      return mapaTipos[tipo?.toLowerCase()] || tipo || 'Desconocido';
    };
    
    const formatearAccion = (accion: string): string => {
      const mapaAcciones: Record<string, string> = {
        'crear': 'Crear',
        'actualizar': 'Actualizar',
        'eliminar': 'Eliminar',
        'aprobar': 'Aprobar',
        'rechazar': 'Rechazar',
        'disponer': 'Disponer',
        'evaluar': 'Evaluar',
        'INSERT': 'Crear',
        'UPDATE': 'Actualizar',
        'DELETE': 'Eliminar'
      };
      return mapaAcciones[accion] || accion || 'Desconocido';
    };
    
    const getAccionClass = (accion: string): string => {
      switch (accion?.toLowerCase()) {
        case 'crear':
        case 'insert':
          return 'accion-crear';
        case 'actualizar':
        case 'update':
          return 'accion-actualizar';
        case 'eliminar':
        case 'delete':
          return 'accion-eliminar';
        case 'aprobar':
          return 'accion-aprobar';
        case 'rechazar':
          return 'accion-rechazar';
        case 'disponer':
          return 'accion-disponer';
        case 'evaluar':
          return 'accion-evaluar';
        default:
          return 'accion-otro';
      }
    };
    
    const getMunicipio = (notificacion: Notificacion): string => {
      if (notificacion.datos_contexto) {
        let contexto = notificacion.datos_contexto;
        if (typeof contexto === 'string') {
          try {
            contexto = JSON.parse(contexto);
          } catch {
            return '';
          }
        }
        
        if (contexto && typeof contexto === 'object') {
          if (contexto.municipio) return contexto.municipio;
          if (contexto.municipio_nombre) return contexto.municipio_nombre;
          if (contexto.nom_municipio) return contexto.nom_municipio;
        }
      }
      
      if (notificacion.descripcion) {
        const matchMunicipio = notificacion.descripcion.match(/[Mm]unicipio[:\s]+([A-Za-zÁÉÍÓÚáéíóúÑñ\s]+?)(?:\s+[,()]|$)/);
        if (matchMunicipio && matchMunicipio[1]) {
          return matchMunicipio[1].trim();
        }
      }
      
      return '';
    };
    
// FUNCIÓN COMPLETA MEJORADA - REEMPLAZAR EN AMBOS ARCHIVOS (Home.vue y Notificaciones.vue)
const getUsuario = (notificacion: Notificacion): string => {
  // DIAGNÓSTICO: Imprimir datos completos de la notificación para depuración
  console.debug('🔍 DATOS NOTIFICACIÓN:', {
    id: notificacion.id,
    tipo: notificacion.tipo_sistema || (notificacion.id < 1000000 ? 'preoperacion' : 'postoperacion'),
    tiene_usuario_directo: !!notificacion.usuario_windows,
    usuario_directo: notificacion.usuario_windows,
    tiene_datos_contexto: !!notificacion.datos_contexto,
    tipo_datos_contexto: typeof notificacion.datos_contexto,
    accion: notificacion.accion,
    datos_contexto_raw: notificacion.datos_contexto
  });
  
  // CASO 1: Usuario directo en la notificación
  if (notificacion.usuario_windows) {
    console.debug(`✅ ENCONTRADO usuario_windows directo: ${notificacion.usuario_windows}`);
    return notificacion.usuario_windows;
  }
  
  // CASO 2: En datos_contexto como objeto o string
  if (notificacion.datos_contexto) {
    // Normalizar: Si datos_contexto es string, intentar parsearlo como JSON
    let contexto = notificacion.datos_contexto;
    if (typeof contexto === 'string') {
      try {
        contexto = JSON.parse(contexto);
        console.debug('📦 datos_contexto parseado de string a objeto');
      } catch (e) {
        console.debug('⚠️ Error parseando datos_contexto como JSON', e);
      }
    }
    
    // Ahora que contexto está normalizado (o sigue siendo string si falló), buscar en posibles propiedades
    if (contexto && typeof contexto === 'object') {
      // Lista de propiedades a buscar, en orden de prioridad
      const propiedadesUsuario = [
        'usuario_windows', 'usuario', 'propietario', 'creador', 
        'modificado_por', 'created_by', 'updated_by', 'usuario_login'
      ];
      
      for (const prop of propiedadesUsuario) {
        if (contexto[prop]) {
          console.debug(`✅ ENCONTRADO usuario en datos_contexto.${prop}: ${contexto[prop]}`);
          return contexto[prop];
        }
      }
      
      // Búsqueda heurística: cualquier propiedad que contenga 'usuario' o 'user'
      for (const key in contexto) {
        const keyLower = key.toLowerCase();
        if ((keyLower.includes('usuario') || keyLower.includes('user')) && contexto[key]) {
          console.debug(`✅ ENCONTRADO usuario en datos_contexto.${key}: ${contexto[key]}`);
          return contexto[key];
        }
      }
      
      // Si hay un objeto anidado que podría contener info de usuario, buscamos ahí también
      for (const key in contexto) {
        if (contexto[key] && typeof contexto[key] === 'object') {
          for (const subKey in contexto[key]) {
            const subKeyLower = subKey.toLowerCase();
            if ((subKeyLower.includes('usuario') || 
                 subKeyLower.includes('user') || 
                 subKeyLower.includes('autor') ||
                 subKeyLower.includes('creado')) && 
                 contexto[key][subKey]) {
              console.debug(`✅ ENCONTRADO usuario en datos_contexto.${key}.${subKey}: ${contexto[key][subKey]}`);
              return contexto[key][subKey];
            }
          }
        }
      }
    }
  }
  
  // CASO 3: Extraer de la descripción
  if (notificacion.descripcion) {
    const patrones = [
      /creado por\s+([a-zA-Z0-9_.]+)/i,
      /actualizado por\s+([a-zA-Z0-9_.]+)/i,
      /modificado por\s+([a-zA-Z0-9_.]+)/i,
      /subido por\s+([a-zA-Z0-9_.]+)/i,
      /usuario\s*:\s*([a-zA-Z0-9_.]+)/i,
      /autor\s*:\s*([a-zA-Z0-9_.]+)/i,
      /por\s+([a-zA-Z0-9_.]+)/i
    ];
    
    for (const patron of patrones) {
      const coincidencia = notificacion.descripcion.match(patron);
      if (coincidencia && coincidencia[1]) {
        console.debug(`✅ ENCONTRADO usuario en descripción: ${coincidencia[1]}`);
        return coincidencia[1];
      }
    }
  }
  
  // CASO ESPECIAL: Búsqueda ampliada en todas las propiedades
  for (const key in notificacion) {
    if (typeof notificacion[key] === 'string' && notificacion[key].length < 100) {
      const value = notificacion[key];
      // Verificar si parece un nombre de usuario
      if (/^[a-zA-Z0-9_.]{3,30}$/.test(value) && 
          !value.includes('http') && !value.includes('/')) {
        console.debug(`✅ POSIBLE usuario encontrado en notificacion.${key}: ${value}`);
        return value;
      }
    }
  }
  
  // Nada encontrado
  console.debug('❌ NO SE ENCONTRÓ USUARIO');
  return '';
};

// AGREGA ESTO EN LA FUNCIÓN QUE CARGA LAS NOTIFICACIONES (JUSTO DESPUÉS DE OBTENER DATOS)
// En Home.vue, probablemente en cargarNotificacionesHoyOptimizado o similar
// En Notificaciones.vue, en cargarNotificaciones
const analizarRespuestaAPI = (respuesta: any) => {
  console.log('🔥 ANÁLISIS RESPUESTA API 🔥');
  
  // Verificar estructura general
  if (!respuesta) {
    console.error('⛔ Respuesta API vacía o nula');
    return;
  }
  
  // Encontrar dónde están las notificaciones en la respuesta
  let notificacionesArray: any[] = [];
  if (Array.isArray(respuesta)) {
    notificacionesArray = respuesta;
    console.log(`✅ Respuesta directamente es un array de ${respuesta.length} notificaciones`);
  } else if (respuesta.results && Array.isArray(respuesta.results)) {
    notificacionesArray = respuesta.results;
    console.log(`✅ Respuesta contiene array 'results' con ${respuesta.results.length} notificaciones`);
  } else {
    console.error('⛔ No se encontró array de notificaciones en respuesta');
    console.log('📦 Estructura respuesta:', Object.keys(respuesta));
    return;
  }
  
  if (notificacionesArray.length === 0) {
    console.log('⚠️ Array de notificaciones está vacío');
    return;
  }
  
  // Analizar primera notificación
  const primera = notificacionesArray[0];
  console.log('📝 CAMPOS PRIMERA NOTIFICACIÓN:', Object.keys(primera));
  console.log('📝 EJEMPLO COMPLETO:', JSON.stringify(primera, null, 2));
  
  // Estadísticas de campo usuario_windows
  const conUsuarioWindows = notificacionesArray.filter(n => n.usuario_windows).length;
  console.log(`📊 Notificaciones CON usuario_windows: ${conUsuarioWindows}/${notificacionesArray.length} (${(conUsuarioWindows/notificacionesArray.length*100).toFixed(1)}%)`);
  
  // Estadísticas de datos_contexto
  const conDatosContexto = notificacionesArray.filter(n => n.datos_contexto).length;
  console.log(`📊 Notificaciones CON datos_contexto: ${conDatosContexto}/${notificacionesArray.length} (${(conDatosContexto/notificacionesArray.length*100).toFixed(1)}%)`);
  
  // Tipos de datos_contexto
  const tiposDatosContexto = notificacionesArray
    .filter(n => n.datos_contexto)
    .reduce((acc, n) => {
      const tipo = typeof n.datos_contexto;
      acc[tipo] = (acc[tipo] || 0) + 1;
      return acc;
    }, {});
  console.log('📊 TIPOS de datos_contexto:', tiposDatosContexto);
  
  // Verificar cuántas tienen usuario según nuestra función
  const usuariosExtraidos = notificacionesArray.map(n => getUsuario(n));
  const conUsuarioExtraido = usuariosExtraidos.filter(u => u).length;
  console.log(`📊 Notificaciones CON usuario extraído: ${conUsuarioExtraido}/${notificacionesArray.length} (${(conUsuarioExtraido/notificacionesArray.length*100).toFixed(1)}%)`);
  
  // Muestreo de datos_contexto
  if (conDatosContexto > 0) {
    const muestras = notificacionesArray
      .filter(n => n.datos_contexto)
      .slice(0, 5)
      .map(n => {
        const contexto = typeof n.datos_contexto === 'string' 
          ? { _original: n.datos_contexto.substring(0, 100) + '...' } 
          : n.datos_contexto;
        return { id: n.id, datos_contexto: contexto };
      });
    console.log('📊 MUESTRAS de datos_contexto:', muestras);
  }
};

// COLOCAR ESTA LLAMADA DESPUÉS DE OBTENER NOTIFICACIONES
// Ejemplo: 
// const response = await api.get('/preoperacion/notificaciones/');
// analizarRespuestaAPI(response);

    
    const getDescripcionCompleta = (notificacion: Notificacion): string => {
      if (!notificacion.descripcion) {
        return formatearAccion(notificacion.accion) + ' de ' + formatearTipoEntidad(notificacion.tipo_entidad);
      }
      return notificacion.descripcion;
    };
    
    const getDetallesExtra = (notificacion: Notificacion): string => {
      if (notificacion.datos_contexto) {
        const detalles = [];
        
        if (notificacion.tipo_entidad === 'clasificacion') {
          if (notificacion.datos_contexto.nombre) {
            detalles.push(`Clasificación: "${notificacion.datos_contexto.nombre}"`);
          }
        } else if (notificacion.tipo_entidad === 'insumo') {
          if (notificacion.datos_contexto.categoria) {
            detalles.push(`Categoría: ${notificacion.datos_contexto.categoria}`);
          }
          if (notificacion.datos_contexto.tipo_insumo) {
            detalles.push(`Tipo: ${notificacion.datos_contexto.tipo_insumo}`);
          }
        }
        
        return detalles.join(' - ');
      }
      
      return '';
    };
    
    const formatearFecha = (notificacion: any) => {
      const fechaStr = notificacion.fecha_cambio;
      if (!fechaStr) return 'Fecha no disponible';
      
      try {
        const fechaObj = new Date(fechaStr);
        return format(fechaObj, 'dd/MM/yyyy', { locale: es });
      } catch (error) {
        return 'Fecha desconocida';
      }
    };
    
    const formatearTiempo = (notificacion: any) => {
      const fechaStr = notificacion.fecha_cambio;
      if (!fechaStr) return '';
      
      try {
        const fechaObj = new Date(fechaStr);
        if (isNaN(fechaObj.getTime())) return '';
        return format(fechaObj, 'HH:mm:ss', { locale: es });
      } catch (error) {
        return '';
      }
    };
    
    // Funciones de paginación y ordenación
    const irAPagina = (pagina: number) => {
      if (pagina < 1 || pagina > totalPaginas.value) return;
      paginaActual.value = pagina;
    };
    
    const cambiarElementosPorPagina = () => {
      paginaActual.value = 1;
    };
    
    const ordenarPor = (campo: string) => {
      if (ordenacion.value.campo === campo) {
        ordenacion.value.ascendente = !ordenacion.value.ascendente;
      } else {
        ordenacion.value.campo = campo;
        ordenacion.value.ascendente = true;
      }
      
      cargarNotificaciones();
    };
    
    // Funciones del modal y acciones
    const verDetalles = (notificacion: Notificacion) => {
      notificacionSeleccionada.value = notificacion;
      modalVisible.value = true;
    };
    
    const cerrarModal = () => {
      modalVisible.value = false;
      notificacionSeleccionada.value = null;
    };
    
    const marcarLeida = async (notificacion: Notificacion) => {
      try {
        const tipo = esTipoPreoperacion(notificacion) ? 'preoperacion' : 'postoperacion';
        await notificacionesStore.marcarLeidas([notificacion.id], tipo);
        
        const index = notificaciones.value.findIndex(n => n.id === notificacion.id && n.tipo_sistema === notificacion.tipo_sistema);
        if (index >= 0) {
          notificaciones.value[index] = { ...notificaciones.value[index], leido: true };
        }
      } catch (error) {
        console.error('Error al marcar como leída:', error);
      }
    };
    
    const marcarLeidaYCerrar = async () => {
      if (notificacionSeleccionada.value) {
        await marcarLeida(notificacionSeleccionada.value);
      }
      cerrarModal();
    };
    

    
    const exportarCSV = () => {
      try {
        if (notificacionesFiltradas.value.length === 0) return;
        
        const headers = ['ID', 'Fecha', 'Tipo Sistema', 'Tipo Entidad', 'Acción', 'Municipio', 'Descripción', 'Usuario', 'Estado Lectura'];
        
        const filas = notificacionesFiltradas.value.map(notificacion => [
          notificacion.id,
          formatearFecha(notificacion),
          esTipoPreoperacion(notificacion) ? 'Preoperación' : 'Postoperación',
          formatearTipoEntidad(notificacion.tipo_entidad),
          formatearAccion(notificacion.accion),
          getMunicipio(notificacion),
          getDescripcionCompleta(notificacion),
          getUsuario(notificacion),
          notificacion.leido ? 'Leída' : 'No leída'
        ]);
        
        const csvContent = [
          headers.join(','),
          ...filas.map(fila => fila.map(campo => `"${String(campo).replace(/"/g, '""')}"`).join(','))
        ].join('\n');
        
        const BOM = '\uFEFF';
        const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
        link.download = `notificaciones_filtradas_${timestamp}.csv`;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        alert(`Se han exportado ${notificacionesFiltradas.value.length} notificaciones exitosamente`);
        
      } catch (error) {
        console.error('Error al exportar CSV:', error);
        alert('Error al generar el archivo CSV.');
      }
    };
    
    // Funciones adicionales para el modal
    const formatearCampo = (campo: string): string => {
      const mapaCampos: Record<string, string> = {
        'municipio_id': 'ID Municipio',
        'cod_municipio': 'Código Municipio',
        'municipio': 'Municipio',
        'municipio_nombre': 'Nombre Municipio',
        'nom_municipio': 'Nombre Municipio',
        'usuario_windows': 'Usuario',
        'usuario': 'Usuario',
        'componente': 'Componente',
        'nombre_componente': 'Nombre Componente',
        'categoria': 'Categoría',
        'tipo_insumo': 'Tipo de Insumo',
        'estado': 'Estado',
        'departamento': 'Departamento',
        'nom_depto': 'Nombre Departamento',
        'nombre': 'Nombre',
        'descripcion': 'Descripción',
        'fecha': 'Fecha',
        'hora': 'Hora',
        'observaciones': 'Observaciones',
        'ruta': 'Ruta',
        'archivo': 'Archivo'
      };
      
      return mapaCampos[campo] || campo.charAt(0).toUpperCase() + campo.slice(1).replace(/_/g, ' ');
    };
    
    const formatearValor = (valor: any): string => {
      if (valor === null || valor === undefined) return 'No especificado';
      if (typeof valor === 'boolean') return valor ? 'Sí' : 'No';
      if (typeof valor === 'object') return JSON.stringify(valor, null, 2);
      // Convertir rutas Linux a Windows si es una ruta
      const strValor = String(valor);
      if (isPathLike(strValor)) {
        return linuxToWindowsPath(strValor) || strValor;
      }
      return strValor;
    };
    
    // Función para extraer la ruta del archivo de los datos de contexto
    const extraerRutaArchivo = (notificacion: Notificacion): string | null => {
      // 🔍 DEBUG: Ver qué datos llegan
      console.log('🔍 extraerRutaArchivo - notificacion:', {
        id: notificacion.id,
        tipo_entidad: notificacion.tipo_entidad,
        tiene_datos_contexto: !!notificacion.datos_contexto,
        datos_contexto_tipo: typeof notificacion.datos_contexto,
        datos_contexto: notificacion.datos_contexto
      });

      if (!notificacion.datos_contexto) {
        console.log('⚠️ No hay datos_contexto para notificación:', notificacion.id);
        return null;
      }

      let contexto = notificacion.datos_contexto;
      if (typeof contexto === 'string') {
        try {
          contexto = JSON.parse(contexto);
          console.log('📦 datos_contexto parseado de string:', contexto);
        } catch (e) {
          console.error('❌ Error parseando datos_contexto:', e);
          return null;
        }
      }

      if (contexto && typeof contexto === 'object') {
        // Buscar en múltiples campos posibles
        const ruta = contexto.ruta || contexto.path_file || contexto.ruta_completa ||
                     contexto.archivo || contexto.path || contexto.file_path || null;
        console.log('🔗 Ruta extraída:', ruta, '| Campos disponibles:', Object.keys(contexto));
        return ruta;
      }

      console.log('⚠️ datos_contexto no es un objeto válido');
      return null;
    };

    // 🔧 FUNCIÓN CORREGIDA: Verificar disponibilidad de archivo basado en roles correctos
    const archivoDisponible = (notificacion: Notificacion): boolean => {
      const accion = notificacion.accion?.toLowerCase();
      const ruta = extraerRutaArchivo(notificacion);
      
      // Si el archivo fue eliminado, no está disponible
      if (accion === 'eliminar' || accion === 'delete') {
        return false;
      }
      
      // Si no hay ruta, no está disponible
      if (!ruta) {
        return false;
      }
      
      // 🔧 CORRECCIÓN PRINCIPAL: Usar isAnyAdmin en lugar de solo isAdmin
      // Los super administradores Y administradores normales tienen acceso completo
      if (authStore.isAnyAdmin || authStore.isSuperAdmin) {
        console.log('🔧 Acceso de administrador concedido:', {
          isSuperAdmin: authStore.isSuperAdmin,
          isAdmin: authStore.isAdmin,
          isAnyAdmin: authStore.isAnyAdmin,
          username: authStore.user?.username
        });
        return true;
      }
      
      // Para profesionales, verificar municipio asignado
      let municipioId: number | undefined;
      if (notificacion.datos_contexto) {
        const ctx = notificacion.datos_contexto;
        municipioId = ctx.municipio_id || ctx.cod_municipio || undefined;
      }
      
      // Si no hay municipio en datos_contexto, intentar extraer de la ruta
      if (!municipioId && archivosService?.extraerCodigoMunicipioDeRuta) {
        const codigoExtraido = archivosService.extraerCodigoMunicipioDeRuta(ruta);
        if (codigoExtraido) municipioId = codigoExtraido;
      }
      
      // Si encontramos municipio, verificar acceso del profesional
      if (municipioId) {
        const tieneAcceso = authStore.tieneAccesoAMunicipio(municipioId);
        console.log('🔍 Verificación profesional:', {
          municipioId,
          tieneAcceso,
          username: authStore.user?.username,
          rol: authStore.user?.rol_tipo
        });
        return tieneAcceso;
      }
      
      // Si no podemos determinar el municipio, denegar acceso por seguridad
      console.log('⚠️ Acceso denegado - no se pudo determinar municipio:', {
        ruta,
        username: authStore.user?.username,
        rol: authStore.user?.rol_tipo
      });
      return false;
    };
    

    
    // Función para obtener el ícono del archivo
    const getFileIcon = (fileName: string): string => {
      if (!fileName) return 'insert_drive_file';
      
      const extension = getFileExtension(fileName);
      
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
        case 'tif':
        case 'tiff':
          return 'image';
        case 'zip':
        case 'rar':
        case '7z':
          return 'folder_zip';
        case 'shp':
        case 'kml':
        case 'kmz':
        case 'gdb':
          return 'map';
        case 'txt':
        case 'md':
          return 'text_snippet';
        case 'mp3':
        case 'wav':
        case 'ogg':
          return 'audio_file';
        case 'mp4':
        case 'mov':
        case 'avi':
          return 'video_file';
        default:
          return 'insert_drive_file';
      }
    };
    

    
    // 🔧 FUNCIÓN CORREGIDA: Ver archivo con permisos de super admin
    const verArchivoNotificacion = async (notificacion: Notificacion) => {
      const rutaArchivo = extraerRutaArchivo(notificacion);
      
      if (!rutaArchivo) {
        alert('No se encontró la ruta del archivo en esta notificación');
        return;
      }
      
      if (!archivoDisponible(notificacion)) {
        alert('Este archivo no está disponible o no tienes permisos para acceder a él');
        return;
      }
      
      const nombreArchivo = obtenerNombreArchivo(rutaArchivo);
      const extension = getFileExtension(nombreArchivo);
      
      try {
        const token = localStorage.getItem('token');
        const baseUrl = import.meta.env.VITE_API_URL || '';
        const esPostOperacion = notificacion.tipo_sistema === 'postoperacion';
        const tipoOperacion = esPostOperacion ? 'postoperacion' : 'preoperacion';
        const endpoint = extension === 'pdf' ? 'ver_pdf' : 'descargar_archivo';
        const url = `${baseUrl}/${tipoOperacion}/${endpoint}/?ruta=${encodeURIComponent(rutaArchivo)}`;
        
        console.log('🔗 Intentando abrir archivo:', {
          url,
          extension,
          username: authStore.user?.username,
          isSuperAdmin: authStore.isSuperAdmin,
          isAdmin: authStore.isAdmin
        });
        
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Authorization': `Token ${token}`,
            'Accept': '*/*'
          },
          credentials: 'include'
        });
        
        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const blob = await response.blob();
        const blobUrl = window.URL.createObjectURL(blob);
        
        // Abrir en nueva ventana
        window.open(blobUrl, '_blank');
        
        // Limpiar después de un tiempo
        setTimeout(() => {
          window.URL.revokeObjectURL(blobUrl);
        }, 1000);
        
        console.log(`✅ Archivo ${extension.toUpperCase()} abierto correctamente`);
      } catch (error) {
        console.error('❌ Error al abrir archivo:', error);
        // Si falla, intentar descargar
        try {
          await descargarArchivoNotificacion(notificacion);
        } catch (downloadError) {
          alert(`Error al procesar archivo: ${error.message}`);
        }
      }
    };



    // NUEVA FUNCIÓN: Ver historial de propietarios

    const verHistorialPropietarios = () => {
      if (!notificacionSeleccionada.value) {
        console.warn("No hay notificación seleccionada");
        return;
      }
      
      // Determinar tipo de archivo y su ID
      let tipoArchivo = 'postoperacion';
      let idArchivo = null;
      let nombreArchivo = '';
      
      // Si la notificación es de preoperación, cambiar el tipo
      if (notificacionSeleccionada.value.tipo_sistema === 'preoperacion' || 
          esTipoPreoperacion(notificacionSeleccionada.value)) {
        tipoArchivo = 'preoperacion';
      }
      
      // Obtener ID del archivo desde datos_contexto si está disponible
      if (notificacionSeleccionada.value.datos_contexto) {
        const datos = notificacionSeleccionada.value.datos_contexto;
        
        // Para preoperación
        if (tipoArchivo === 'preoperacion') {
          idArchivo = datos.id_archivo || datos.id_lista_archivo || notificacionSeleccionada.value.id_entidad;
          nombreArchivo = datos.nombre_archivo || datos.nombre_insumo || 'Archivo';
        } 
        // Para postoperación
        else {
          idArchivo = datos.id_archivo || notificacionSeleccionada.value.id_entidad;
          nombreArchivo = datos.nombre_archivo || 'Archivo';
        }
      } else {
        // Si no hay datos_contexto, usar id_entidad de la notificación
        idArchivo = notificacionSeleccionada.value.id_entidad;
        nombreArchivo = 'Archivo';
      }
      
      // ✅ NUEVO: Obtener usuario de la notificación
      const usuarioNotificacion = getUsuario(notificacionSeleccionada.value);
      
      console.log("Abriendo historial para:", {
        tipoArchivo,
        idArchivo,
        nombreArchivo,
        usuarioNotificacion,  // NUEVO
        refExists: !!historialModal.value
      });
      
      // Verificar que la referencia existe antes de usarla
      if (historialModal.value && idArchivo) {
        // ✅ PASAR EL USUARIO DE LA NOTIFICACIÓN
        historialModal.value.mostrar(tipoArchivo, idArchivo, nombreArchivo, usuarioNotificacion);
      } else {
        console.error("No se puede mostrar el historial: referencia no disponible o ID inválido");
        alert("No se pudo abrir el historial. Por favor intente nuevamente.");
      }
    };
    










    // ========================================================================================
// 3. FUNCIÓN cargarDatos - CORRECCIÓN COMPLETA:
// ========================================================================================
const cargarDatos = async (esCargarMas: boolean) => {
  const params: any = {
    page_size: '10000',
    ordering: ordenacion.value.ascendente ? ordenacion.value.campo : `-${ordenacion.value.campo}`
  };
  
  if (filtros.value.departamento) {
    params.departamento_id = filtros.value.departamento;
  }
  
  if (filtros.value.municipio) {
    params.municipio_id = filtros.value.municipio;
  }
  
  if (filtros.value.accion) {
    params.accion = filtros.value.accion;
  }
  
  if (filtros.value.fechaDesde) {
    params.fecha_desde = filtros.value.fechaDesde;
  }
  
  if (filtros.value.fechaHasta) {
    params.fecha_hasta = filtros.value.fechaHasta;
  }
  
  if (filtros.value.soloNoLeidas) {
    params.leido = 'false';
  }
  
  if (filtros.value.usuario) {
    params.usuario_windows = filtros.value.usuario;
  }
  
  if (searchQuery.value.trim()) {
    params.search = searchQuery.value.trim();
  }

  if (filtros.value.tipoEntidad) {
    params.tipo_entidad = filtros.value.tipoEntidad;
  }

  const tipos = [];
  if (!filtros.value.tipo || filtros.value.tipo === 'preoperacion') {
    tipos.push('preoperacion');
  }
  if (!filtros.value.tipo || filtros.value.tipo === 'postoperacion') {
    tipos.push('postoperacion');
  }
  
  const promesas = tipos.map(async tipo => {
    const paramsConOffset = { ...params };
    
    if (esCargarMas) {
      paramsConOffset.offset = offsetsPorTipo.value[tipo as keyof typeof offsetsPorTipo.value];
    }
    
    // ✅ USAR API EN LUGAR DE AXIOS DIRECTO
    const endpoint = `/${tipo}/notificaciones/`;
    console.log(`📡 ${tipo} Endpoint:`, endpoint);
    console.log(`📡 ${tipo} Params:`, paramsConOffset);
    
    const response = await api.get(endpoint, { params: paramsConOffset });
    
    let notificacionesTipo = [];
    if (response && Array.isArray(response)) {
      notificacionesTipo = response;
    } else if (response.results && Array.isArray(response.results)) {
      notificacionesTipo = response.results;
    }
    
    if (esCargarMas) {
      offsetsPorTipo.value[tipo as keyof typeof offsetsPorTipo.value] += notificacionesTipo.length;
    } else {
      offsetsPorTipo.value[tipo as keyof typeof offsetsPorTipo.value] = notificacionesTipo.length;
    }
    
    console.log(`📊 ${tipo}: ${notificacionesTipo.length} notificaciones obtenidas`);
    
    return {
      tipo,
      notificaciones: notificacionesTipo.map(n => ({
        ...n,
        tipo_sistema: tipo
      }))
    };
  });
  
  const resultados = await Promise.all(promesas);
  let nuevasNotificaciones = resultados.flatMap(r => r.notificaciones);
  
  if (esCargarMas) {
    const idsExistentes = new Set(notificaciones.value.map(n => `${n.tipo_sistema}-${n.id}`));
    const notificacionesUnicas = nuevasNotificaciones.filter(n => 
      !idsExistentes.has(`${n.tipo_sistema}-${n.id}`)
    );
    notificaciones.value = [...notificaciones.value, ...notificacionesUnicas];
  } else {
    notificaciones.value = nuevasNotificaciones;
  }
  
  const puedeCargarMasPre = resultados.find(r => r.tipo === 'preoperacion')?.notificaciones.length >= 10000;
  const puedeCargarMasPost = resultados.find(r => r.tipo === 'postoperacion')?.notificaciones.length >= 10000;
  
  puedeCargarMas.value = (tipos.includes('preoperacion') && puedeCargarMasPre) || 
                        (tipos.includes('postoperacion') && puedeCargarMasPost);
  
  ultimosParametros.value = { params, tipos };
  
  actualizarUsuariosUnicos();
};

// ========================================================================================
// 4. FUNCIÓN cargarCatalogos - CORRECCIÓN COMPLETA:
// ========================================================================================
const cargarCatalogos = async () => {
  try {
    console.log("🔄 Cargando catálogos...");
    
    // ✅ USAR API EN LUGAR DE AXIOS DIRECTO
    const respuesta = await api.get('/preoperacion/departamentos/');
    
    if (respuesta && Array.isArray(respuesta)) {
      departamentos.value = respuesta;
    } else if (respuesta.results && Array.isArray(respuesta.results)) {
      departamentos.value = respuesta.results;
    }
    
    console.log(`✅ Departamentos: ${departamentos.value.length} cargados`);
  } catch (err) {
    console.error("❌ Error al cargar departamentos:", err);
  }
};

// ========================================================================================
// 5. FUNCIÓN cargarMunicipios - CORRECCIÓN COMPLETA:
// ========================================================================================
const cargarMunicipios = async () => {
  municipios.value = [];
  filtros.value.municipio = '';
  
  if (!filtros.value.departamento) {
    aplicarFiltros();
    return;
  }
  
  try {
    console.log(`Loading municipalities for department ${filtros.value.departamento}...`);
    
    // ✅ USAR API EN LUGAR DE AXIOS DIRECTO
    const response = await api.get(`/preoperacion/departamentos/${filtros.value.departamento}/municipios/`);
    
    if (Array.isArray(response)) {
      municipios.value = response;
    } else if (response && Array.isArray(response.results)) {
      municipios.value = response.results;
    }
    
    console.log(`✅ Loaded ${municipios.value.length} municipalities`);
    
    aplicarFiltros();
  } catch (error) {
    console.error('Error loading municipalities:', error);
  }
};

// ========================================================================================
// 6. FUNCIÓN generarInformeUsuariosEspecificos - CORRECCIÓN COMPLETA:
// ========================================================================================
const generarInformeUsuariosEspecificos = async () => {
  if (!tieneRangoFechasValido.value) {
    alert('Seleccione un rango de fechas válido para generar el informe');
    return;
  }
  
  try {
    cargandoInformeEspecial.value = true;
    
    // ✅ USAR API AXIOS CON TOKEN AUTOMÁTICO
    const response = await api.post('/preoperacion/generar-informe-usuarios/', {
      fecha_desde: filtros.value.fechaDesde,
      fecha_hasta: filtros.value.fechaHasta,
      usuarios_especificos: ['Usuario1', 'Usuario2'] // Ajustar según necesidad
    }, {
      responseType: 'blob'
    });
    
    // Crear enlace de descarga
    const blob = new Blob([response]);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `informe_usuarios_especificos_${filtros.value.fechaDesde}_${filtros.value.fechaHasta}.xlsx`;
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    window.URL.revokeObjectURL(url);
    alert('Informe generado y descargado exitosamente');
    
  } catch (error) {
    console.error('❌ Error al generar informe:', error);
    let mensajeError = 'Error al generar el informe de usuarios específicos.';
    
    if (error.response?.status === 401) {
      mensajeError += '\n\n⚠️ Error de autenticación. Por favor, inicie sesión nuevamente.';
    } else if (error.response?.status === 403) {
      mensajeError += '\n\n🔒 No tiene permisos para generar este informe.';
    } else if (error.message.includes('400') || error.message.includes('fechas')) {
      mensajeError += '\n\n💡 Sugerencia: Verifique que el rango de fechas sea correcto.';
    } else if (error.message.includes('500')) {
      mensajeError += '\n\n💡 Sugerencia: Contacte al administrador del sistema.';
    }
    
    alert(mensajeError);
  } finally {
    cargandoInformeEspecial.value = false;
  }
};

// ========================================================================================
// 7. FUNCIÓN marcarLeidaNotificacion - CORRECCIÓN SI EXISTE:
// ========================================================================================
const marcarLeidaNotificacion = async (notificacion: Notificacion) => {
  try {
    const endpoint = notificacion.tipo_sistema === 'preoperacion' 
      ? `/preoperacion/notificaciones/${notificacion.id}/marcar-leida/`
      : `/postoperacion/notificaciones/${notificacion.id}/marcar-leida/`;
    
    // ✅ USAR API EN LUGAR DE AXIOS DIRECTO
    await api.patch(endpoint);
    
    // Actualizar localmente
    notificacion.leido = true;
    console.log(`✅ Notificación ${notificacion.id} marcada como leída`);
  } catch (error) {
    console.error('Error al marcar notificación como leída:', error);
  }
};

// ========================================================================================
// 8. FUNCIÓN marcarTodasLeidas - CORRECCIÓN SI EXISTE:
// ========================================================================================
const marcarTodasLeidas = async () => {
  try {
    const notificacionesNoLeidas = notificaciones.value.filter(n => !n.leido);
    
    for (const notificacion of notificacionesNoLeidas) {
      await marcarLeidaNotificacion(notificacion);
    }
    
    console.log(`✅ ${notificacionesNoLeidas.length} notificaciones marcadas como leídas`);
  } catch (error) {
    console.error('Error al marcar todas las notificaciones como leídas:', error);
  }
};





// ✅ FUNCIÓN CORREGIDA: descargarArchivoNotificacion
const descargarArchivoNotificacion = async (notificacion: Notificacion) => {
  const rutaArchivo = extraerRutaArchivo(notificacion);

  if (!rutaArchivo) {
    mostrarToast('error', 'Error', 'No se encontró la ruta del archivo en esta notificación');
    return;
  }

  if (!archivoDisponible(notificacion)) {
    mostrarToast('error', 'Acceso denegado', 'Este archivo no está disponible o no tienes permisos para acceder a él');
    return;
  }
  
  try {
    const nombreArchivo = obtenerNombreArchivo(rutaArchivo);
    const extension = getFileExtension(nombreArchivo);
    
    console.log('⬇️ Descargando archivo:', {
      archivo: nombreArchivo,
      extension: extension,
      username: authStore.user?.username,
      isSuperAdmin: authStore.isSuperAdmin,
      isAdmin: authStore.isAdmin
    });
    
    // ✅ LÓGICA CORREGIDA: Usar endpoint específico según tipo de archivo Y tipo de sistema
    const esPostOperacion = notificacion.tipo_sistema === 'postoperacion';
    const baseEndpoint = esPostOperacion ? '/postoperacion' : '/preoperacion';

    let endpoint;
    let params = { ruta: rutaArchivo };

    if (extension === 'pdf') {
      // 🔧 PARA PDFs: usar ver_pdf con download=true
      endpoint = `${baseEndpoint}/ver_pdf/`;
      params.download = 'true'; // ← Parámetro clave para forzar descarga
    } else {
      // 🔧 PARA OTROS ARCHIVOS: usar descargar_archivo
      endpoint = `${baseEndpoint}/descargar_archivo/`;
    }
    
    console.log(`📡 Usando endpoint: ${endpoint} con params:`, params);
    
    // ✅ USAR API AXIOS CON TOKEN AUTOMÁTICO
    const response = await api.get(endpoint, {
      params: params,
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
    console.log(`✅ Descarga completada: ${nombreArchivo}`);
    
  } catch (error: any) {
    console.error('❌ Error al descargar archivo:', error);
    // Intentar extraer mensaje de error del blob si es respuesta del servidor
    let mensajeError = 'Error desconocido';

    // Axios guarda la respuesta del servidor en error.response.data
    if (error.response?.data instanceof Blob) {
      try {
        const textoError = await error.response.data.text();
        if (textoError) mensajeError = textoError;
      } catch (e) {
        console.error('No se pudo leer el blob de error:', e);
      }
    } else if (typeof error.response?.data === 'string') {
      mensajeError = error.response.data;
    } else if (error.message) {
      mensajeError = error.message;
    }

    // Formatear mensaje para mostrar ruta en línea separada
    const mensajeFormateado = mensajeError.replace('El archivo no existe:', '<br><strong>Ruta:</strong>');
    mostrarToast('error', 'Archivo no encontrado', mensajeFormateado, 12000);
  }
};

// ✅ FUNCIÓN CORREGIDA: abrirArchivoNotificacion (para visualización)
const abrirArchivoNotificacion = async (notificacion: Notificacion) => {
  const rutaArchivo = extraerRutaArchivo(notificacion);

  if (!rutaArchivo) {
    mostrarToast('error', 'Error', 'No se encontró la ruta del archivo en esta notificación');
    return;
  }

  if (!archivoDisponible(notificacion)) {
    mostrarToast('error', 'Acceso denegado', 'Este archivo no está disponible o no tienes permisos para acceder a él');
    return;
  }
  
  try {
    const nombreArchivo = obtenerNombreArchivo(rutaArchivo);
    const extension = getFileExtension(nombreArchivo);
    
    console.log('👀 Abriendo archivo:', {
      archivo: nombreArchivo,
      extension,
      username: authStore.user?.username
    });
    
    // ✅ PARA VISUALIZACIÓN: usar ver_pdf según tipo de sistema (sin download=true)
    const esPostOperacion = notificacion.tipo_sistema === 'postoperacion';
    const baseEndpoint = esPostOperacion ? '/postoperacion' : '/preoperacion';
    const endpoint = `${baseEndpoint}/ver_pdf/`;
    const params = { ruta: rutaArchivo };
    // NO incluir download=true para visualización
    
    const response = await api.get(endpoint, {
      params: params,
      responseType: 'blob'
    });
    
    const blob = new Blob([response], { 
      type: response.type || 'application/octet-stream' 
    });
    const blobUrl = window.URL.createObjectURL(blob);
    
    // Siempre abrir en nueva ventana para visualización
    window.open(blobUrl, '_blank');
    
    // Limpiar después de un tiempo
    setTimeout(() => {
      window.URL.revokeObjectURL(blobUrl);
    }, 1000);
    
    console.log(`✅ Archivo ${extension.toUpperCase()} abierto correctamente`);
    
  } catch (error: any) {
    console.error('❌ Error al procesar archivo:', error);
    // Intentar extraer mensaje de error del blob si es respuesta del servidor
    let mensajeError = 'Error desconocido';

    // Axios guarda la respuesta del servidor en error.response.data
    if (error.response?.data instanceof Blob) {
      try {
        const textoError = await error.response.data.text();
        if (textoError) mensajeError = textoError;
      } catch (e) {
        console.error('No se pudo leer el blob de error:', e);
      }
    } else if (typeof error.response?.data === 'string') {
      mensajeError = error.response.data;
    } else if (error.message) {
      mensajeError = error.message;
    }

    // Formatear mensaje para mostrar ruta en línea separada
    const mensajeFormateado = mensajeError.replace('El archivo no existe:', '<br><strong>Ruta:</strong>');
    mostrarToast('error', 'Archivo no encontrado', mensajeFormateado, 12000);
  }
};

// ✅ FUNCIONES AUXILIARES (asegúrate de que existan)
const obtenerNombreArchivo = (ruta: string): string => {
  if (!ruta) return 'archivo_sin_nombre';
  
  // Extraer nombre del archivo de la ruta
  const partes = ruta.replace(/\\/g, '/').split('/');
  let nombre = partes[partes.length - 1];
  
  // Si no tiene extensión, usar un nombre por defecto
  if (!nombre.includes('.')) {
    nombre = `archivo_${Date.now()}`;
  }
  
  return nombre;
};

const getFileExtension = (fileName: string): string => {
  if (!fileName) return '';
  const parts = fileName.toLowerCase().split('.');
  return parts.length > 1 ? parts[parts.length - 1] : '';
};












    // Cargar datos iniciales
    onMounted(() => {
      cargarNotificaciones();
    });

    return {
      // Estado
      notificaciones,
      cargando,
      cargandoMas,
      error,
      puedeCargarMas,
      searchQuery,
      filtros,
      ordenacion,
      paginaActual,
      elementosPorPagina,
      modalVisible,
      notificacionSeleccionada,
      departamentos,
      municipios,
      usuariosUnicos,
      acciones,
      tiposEntidad,
      // Toast
      toastVisible,
      toastType,
      toastTitle,
      toastMessage,
      cerrarToast,
      
      // Computed
      hayFiltrosActivos,
      municipiosFiltrados,
      notificacionesPaginadas,
      totalPaginas,
      paginaInicio,
      paginaFin,
      paginas,
      contadorNoLeidas,
      contadorPre,
      contadorPost,
      mostrarBotonInformeEspecial,
      tieneRangoFechasValido,
      notificacionesFiltradas,
      
      // Métodos
      cargarNotificaciones,
      cargarMasDatos,
      aplicarFiltros,
      limpiarFiltros,
      handleSearch,
      clearSearch,
      cargarMunicipios,
      esTipoPreoperacion,
      getNotificationIcon,
      formatearTipoEntidad,
      formatearAccion,
      getAccionClass,
      getMunicipio,
      getUsuario,
      getDescripcionCompleta,
      getDetallesExtra,
      formatearFecha,
      formatearTiempo,
      irAPagina,
      cambiarElementosPorPagina,
      ordenarPor,
      verDetalles,
      cerrarModal,
      marcarLeida,
      marcarLeidaYCerrar,
      marcarTodasLeidas,
      exportarCSV,
      formatearCampo,
      formatearValor,
      generarInformeUsuariosEspecificos,
      cargandoInformeEspecial,
      
      // MÉTODOS PARA ARCHIVOS
      extraerRutaArchivo,
      archivoDisponible,
      getFileIcon,
      getFileExtension,
      obtenerNombreArchivo,
      verArchivoNotificacion,
      descargarArchivoNotificacion,
      tieneArchivoDisponible,
      
      // NUEVO MÉTODO PARA HISTORIAL
      verHistorialPropietarios,
        historialModal,
        abrirArchivoNotificacion

    };
  }
});
</script>

<style scoped>

/* ========== TOAST NOTIFICATION PROFESIONAL ========== */
.toast-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  min-width: 350px;
  max-width: 500px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: flex-start;
  padding: 16px;
  z-index: 10000;
  border-left: 4px solid #dc3545;
}

.toast-notification.toast-error {
  border-left-color: #dc3545;
}

.toast-notification.toast-success {
  border-left-color: #28a745;
}

.toast-notification.toast-info {
  border-left-color: #17a2b8;
}

.toast-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.toast-error .toast-icon {
  background: #fde8e8;
  color: #dc3545;
}

.toast-success .toast-icon {
  background: #d4edda;
  color: #28a745;
}

.toast-info .toast-icon {
  background: #d1ecf1;
  color: #17a2b8;
}

.toast-icon i {
  font-size: 22px;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-weight: 600;
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
}

.toast-message {
  font-size: 13px;
  color: #666;
  line-height: 1.4;
  word-break: break-word;
}

.toast-message strong {
  color: #333;
}

.toast-close {
  flex-shrink: 0;
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: #999;
  margin-left: 8px;
  border-radius: 4px;
  transition: all 0.2s;
}

.toast-close:hover {
  background: #f0f0f0;
  color: #666;
}

.toast-close i {
  font-size: 18px;
}

/* Animaciones del toast */
.toast-enter-active {
  animation: toast-in 0.3s ease-out;
}

.toast-leave-active {
  animation: toast-out 0.3s ease-in;
}

@keyframes toast-in {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes toast-out {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(100%);
  }
}


/* ========== TABLA DE NOTIFICACIONES - HEADERS FIJOS ========== */
.notifications-section {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  overflow: hidden;
  /* NUEVO: Altura máxima para permitir scroll interno */
  max-height: 70vh;
  display: flex;
  flex-direction: column;
}

.table-container {
  /* MODIFICADO: Configuración mejorada para sticky headers */
  overflow: auto;
  flex: 1;
  position: relative;
  /* NUEVO: Scroll suave */
  scroll-behavior: smooth;
}

.notificaciones-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
  /* NUEVO: Posición relativa para el contexto de sticky */
  position: relative;
}

.notificaciones-table th,
.notificaciones-table td {
  padding: 0.5rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
  font-size: 0.85rem;
}

.notificaciones-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
  /* MODIFICADO: Configuración mejorada para sticky */
  position: sticky;
  top: 0;
  z-index: 100;
  font-size: 0.85rem;
  /* NUEVO: Sombra para mejor visualización */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  /* NUEVO: Borde para separación visual */
  border-bottom: 2px solid #dee2e6;
}

.notificaciones-table th.sortable {
  cursor: pointer;
  user-select: none;
  /* NUEVO: Transición suave */
  transition: background-color 0.2s ease;
}

.notificaciones-table th.sortable:hover {
  background-color: #e9ecef;
}

/* NUEVO: Indicador visual cuando se hace scroll */
.table-container::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.table-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}







/* ARCHIVO COMPLETO DE ESTILOS PARA NOTIFICACIONES.VUE */

/* ========== ESTILOS PARA ARCHIVOS ========== */
.archivo-campo {
  grid-column: 1 / -1;
  background-color: #f8f9fa !important;
  border: 2px solid #e9ecef !important;
}

.archivo-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.archivo-details {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background-color: white;
  border-radius: 6px;
  border: 1px solid #dee2e6;
}

.archivo-icon {
  font-size: 2rem !important;
  color: #6c757d;
}

.archivo-nombre {
  font-weight: 500;
  color: #495057;
  word-break: break-all;
  flex: 1;
}

.archivo-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-archivo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
}

.ver-archivo {
  background-color: #007bff;
  color: white;
}

.ver-archivo:hover {
  background-color: #0056b3;
  transform: translateY(-1px);
}

.descargar-archivo {
  background-color: #28a745;
  color: white;
}

.descargar-archivo:hover {
  background-color: #1e7e34;
  transform: translateY(-1px);
}

.btn-archivo i {
  font-size: 1.1rem;
}

/* ========== INFORMACIÓN DE CARGA ========== */
.load-info {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1rem 1.5rem;
  margin-bottom: 1rem;
}

.load-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.load-stats {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #495057;
}

.load-count {
  font-weight: 600;
  color: #007bff;
}

.more-available {
  color: #28a745;
  font-weight: 500;
}

.load-more-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  background-color: #17a2b8;
  color: white;
  transition: background-color 0.2s;
}

.load-more-button:hover:not(:disabled) {
  background-color: #138496;
}

.load-more-button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
}

.load-more-button i {
  font-size: 1.1rem;
}

/* ========== ESTILOS GENERALES ========== */
.container {
  width: 100%;
  max-width: 1500px;
  margin: 0 auto;
  padding: 0 1rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.8rem;
  color: #343a40;
  margin-bottom: 0.5rem;
}

.page-description {
  color: #6c757d;
  margin: 0;
}

/* ========== FILTROS - SECCIÓN CORREGIDA ========== */
.filters-section {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.search-bar {
  display: flex;
  align-items: center;
  border: 1px solid #ced4da;
  border-radius: 4px;
  padding: 0 0.75rem;
  margin-bottom: 1rem;
}

.search-bar i {
  color: #6c757d;
  margin-right: 0.5rem;
}

.search-bar input {
  flex: 1;
  padding: 0.75rem 0;
  border: none;
  outline: none;
  font-size: 1rem;
}

.search-bar button {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* CORRECCIÓN PRINCIPAL: Mejor distribución de filtros */
.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

/* Hacer que el filtro de fechas ocupe más espacio */
.date-filter {
  grid-column: span 2;
  min-width: 300px;
}

/* Hacer que las opciones de filtro ocupen el ancho completo */
.filter-options {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.filter-group {
  display: flex;
  flex-direction: column;
  min-width: 0; /* Permite que el elemento se encoja */
}

.filter-group label {
  display: block;
  font-size: 0.9rem;
  color: #495057;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.filter-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.9rem;
  background-color: white;
}

/* CORRECCIÓN ESPECÍFICA: Mejores estilos para filtros de fecha */
.date-range-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  align-items: end;
}

.date-field {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.date-field label {
  display: block;
  font-size: 0.8rem;
  color: #495057;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.date-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.9rem;
  background-color: white;
  min-width: 0;
}

/* Estilos para checkbox y botones */
.filter-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.filter-checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
}

.filter-checkbox label {
  margin: 0;
  font-size: 0.9rem;
  cursor: pointer;
}

.filter-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: flex-start;
}

.filter-button,
.clear-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  white-space: nowrap;
}

.filter-button {
  background-color: #007bff;
  color: white;
}

.filter-button:hover:not(:disabled) {
  background-color: #0069d9;
}

.filter-button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
}

.clear-button {
  background-color: #6c757d;
  color: white;
}

.clear-button:hover {
  background-color: #5a6268;
}

/* ========== SECCIÓN DE RESUMEN ========== */
.summary-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.summary-stats {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.stat-chip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #f8f9fa;
  border-radius: 20px;
  font-size: 0.9rem;
}

.stat-label {
  color: #6c757d;
}

.stat-value {
  font-weight: bold;
  color: #343a40;
}

.type-chips {
  display: flex;
  gap: 0.5rem;
}

.type-chip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
}

.preop-chip {
  background-color: rgba(0, 123, 255, 0.1);
}

.preop-chip .type-value {
  color: #007bff;
  font-weight: bold;
}

.postop-chip {
  background-color: rgba(40, 167, 69, 0.1);
}

.postop-chip .type-value {
  color: #28a745;
  font-weight: bold;
}

.summary-actions {
  display: flex;
  gap: 0.5rem;
}

.mark-read-button,
.refresh-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
}

.mark-read-button {
  background-color: #28a745;
  color: white;
}

.mark-read-button:hover {
  background-color: #218838;
}

.refresh-button {
  background-color: #17a2b8;
  color: white;
}

.refresh-button:hover {
  background-color: #138496;
}

.refresh-button:disabled {
  background-color: #97dbe6;
  cursor: not-allowed;
}

/* ========== TABLA DE NOTIFICACIONES ========== */





.notificaciones-table th,
.notificaciones-table td {
  padding: 0.5rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
  font-size: 0.85rem;
}





.notificaciones-table th.sortable:hover {
  background-color: #e9ecef;
}

.notificaciones-table tr:hover {
  background-color: #f8f9fa;
}

.notificaciones-table tr.no-leida {
  background-color: #f1f8ff;
}

.notificaciones-table tr.no-leida:hover {
  background-color: #e1f0ff;
}

/* ========== COLUMNAS ESPECÍFICAS ========== */
.column-fecha {
  min-width: 100px;
  width: 100px;
}

.fecha-info {
  display: flex;
  flex-direction: column;
}

.fecha-info .fecha {
  font-weight: 500;
  font-size: 0.8rem;
}

.fecha-info .tiempo {
  font-size: 0.75rem;
  color: #6c757d;
}

.column-tipo {
  min-width: 90px;
  width: 90px;
}

.tipo-badge {
  display: inline-block;
  padding: 0.15rem 0.35rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
}

.tipo-pre {
  background-color: rgba(0, 123, 255, 0.1);
  color: #007bff;
}

.tipo-post {
  background-color: rgba(40, 167, 69, 0.1);
  color: #28a745;
}

.column-entidad {
  min-width: 110px;
  width: 110px;
}

.entidad-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.entidad-info i {
  color: #6c757d;
  font-size: 1rem;
}

.column-accion {
  min-width: 80px;
  width: 80px;
}

.accion-badge {
  display: inline-block;
  padding: 0.15rem 0.35rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
}

.accion-crear {
  background-color: #d4edda;
  color: #155724;
}

.accion-actualizar {
  background-color: #cce5ff;
  color: #004085;
}

.accion-eliminar {
  background-color: #f8d7da;
  color: #721c24;
}

.accion-aprobar {
  background-color: #d1e7dd;
  color: #0f5132;
}

.accion-rechazar {
  background-color: #f8d7da;
  color: #842029;
}

.accion-disponer {
  background-color: #e2e3ff;
  color: #3a33a5;
}

.accion-evaluar {
  background-color: #fff3cd;
  color: #664d03;
}

.accion-otro {
  background-color: #e9ecef;
  color: #495057;
}

.column-ubicacion {
  min-width: 140px;
  width: 140px;
}

.municipio-info {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.85rem;
}

.municipio-info i {
  color: #6c757d;
  font-size: 1rem;
}

.no-data {
  color: #adb5bd;
  font-style: italic;
  font-size: 0.85rem;
}

.column-descripcion {
  min-width: 250px;
}

.descripcion-wrapper {
  max-width: 350px;
}

.descripcion-texto {
  margin: 0 0 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 350px;
  font-size: 0.85rem;
}

.detalles-extra {
  font-size: 0.75rem;
  color: #6c757d;
  background-color: #f8f9fa;
  padding: 0.15rem 0.35rem;
  border-radius: 4px;
  border-left: 2px solid #ddd;
}

.column-usuario {
  min-width: 120px;
  width: 120px;
}

.usuario-info {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.85rem;
}

.usuario-info i {
  color: #17a2b8;
  font-size: 1rem;
}

.column-acciones {
  width: 90px;
  min-width: 90px;
}

.acciones-container {
  display: flex;
  gap: 0.15rem;
}

.action-button {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 4px;
  transition: background-color 0.2s, color 0.2s;
}

.action-button:hover {
  background-color: #f1f3f5;
}

.action-button.mark-read:hover {
  color: #28a745;
}

.action-button.view-details:hover {
  color: #007bff;
}

.action-button.navigate:hover {
  color: #6610f2;
}

/* ========== ESTADOS DE CARGA Y ERRORES ========== */
.loading-indicator,
.error-message,
.empty-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
  color: #6c757d;
}

.loading-indicator .spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message i,
.empty-message i {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.error-message i {
  color: #dc3545;
}

.empty-message i {
  color: #6c757d;
}

.error-message button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

/* ========== PAGINACIÓN ========== */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: #f8f9fa;
  border-top: 1px solid #e9ecef;
  flex-wrap: wrap;
  gap: 1rem;
}

.pagination-info {
  color: #6c757d;
  font-size: 0.9rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.pagination-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid #dee2e6;
  background-color: white;
  color: #6c757d;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.pagination-button:hover:not(:disabled) {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

.pagination-button:disabled {
  background-color: #f8f9fa;
  color: #adb5bd;
  cursor: not-allowed;
  border-color: #e9ecef;
}

.page-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid #dee2e6;
  background-color: white;
  color: #6c757d;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
  margin: 0 0.125rem;
  font-size: 0.9rem;
}

.page-number:hover {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

.page-number.active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
  font-weight: bold;
}

.page-number.ellipsis {
  background-color: transparent;
  border: none;
  cursor: default;
  color: #6c757d;
}

.page-number.ellipsis:hover {
  background-color: transparent;
  color: #6c757d;
}

.pagination-options {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pagination-options label {
  font-size: 0.9rem;
  color: #6c757d;
}

.pagination-options select {
  padding: 0.25rem 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.9rem;
}

/* ========== MODAL ========== */
.modal-overlay {
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
  padding: 1rem;
}

.modal-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
  background-color: #f8f9fa;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #343a40;
}

.close-button {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-button:hover {
  background-color: #e9ecef;
  color: #495057;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e9ecef;
  background-color: #f8f9fa;
}

.btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0069d9;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

/* ========== DETALLES DE NOTIFICACIÓN - CORREGIDO ========== */
.notificacion-detalle {
  font-size: 0.9rem;
}

.detalle-seccion {
  margin-bottom: 2rem;
}

.detalle-seccion h3 {
  margin: 0 0 1rem;
  font-size: 1.1rem;
  color: #495057;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 0.5rem;
}

/* INFORMACIÓN BÁSICA - Mantener grid para campos cortos */
.info-basica {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

/* INFORMACIÓN ADICIONAL - CORREGIDO: Una sola columna */
.datos-contexto {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detalle-campo {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #007bff;
  width: 100%;
  box-sizing: border-box;
}

/* ETIQUETAS Y VALORES */
.campo-label {
  font-weight: 600;
  color: #495057;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
  display: block;
}

.campo-valor {
  color: #6c757d;
  font-size: 0.9rem;
  line-height: 1.4;
  word-break: break-all;
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: pre-wrap;
  max-width: 100%;
}

/* ESTILOS ESPECIALES PARA RUTAS LARGAS */
.detalle-campo:has(.campo-label:contains("Ruta")) .campo-valor,
.detalle-campo:has(.campo-label:contains("Path")) .campo-valor,
.detalle-campo:has(.campo-label:contains("archivo")) .campo-valor {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  background-color: #f1f3f4;
  padding: 0.75rem;
  border-radius: 4px;
  border: 1px solid #e1e5e9;
  white-space: pre-wrap;
  word-break: break-all;
  overflow-wrap: anywhere;
  line-height: 1.3;
  max-height: 200px;
  overflow-y: auto;
}

/* BADGES Y ELEMENTOS ESPECIALES */
.estado-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  width: fit-content;
}

.estado-leido {
  background-color: #d4edda;
  color: #155724;
}

.estado-no-leido {
  background-color: #f8d7da;
  color: #721c24;
}

/* DESCRIPCIÓN COMPLETA */
.descripcion-completa {
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #17a2b8;
  margin-top: 0.5rem;
}

.descripcion-completa p {
  margin: 0;
  line-height: 1.5;
  word-wrap: break-word;
}

/* MENSAJE CUANDO NO HAY DATOS */
.no-data-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 6px;
  color: #6c757d;
  font-style: italic;
  border: 1px dashed #dee2e6;
}

.no-data-message i {
  font-size: 1.2rem;
  color: #adb5bd;
}

/* ========== ESTILOS PARA BOTÓN DE INFORME ESPECIAL ========== */
.informe-especial-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  position: relative;
  overflow: hidden;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.informe-especial-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.informe-especial-button:disabled {
  background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
  cursor: not-allowed;
  opacity: 0.7;
  transform: none;
  box-shadow: 0 2px 8px rgba(149, 165, 166, 0.3);
}

.informe-especial-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.6s;
}

.informe-especial-button:hover:not(:disabled)::before {
  left: 100%;
}

.informe-especial-button i {
  font-size: 1.2rem;
  animation: none;
}

.informe-especial-button:disabled i {
  animation: rotate 1.5s linear infinite;
}

.button-badge {
  background: rgba(255, 255, 255, 0.25);
  border-radius: 12px;
  padding: 0.2rem 0.6rem;
  font-size: 0.7rem;
  font-weight: 700;
  margin-left: 0.5rem;
  animation: pulse 2s infinite;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

@keyframes pulse {
  0% { opacity: 0.8; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.05); }
  100% { opacity: 0.8; transform: scale(1); }
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ========== ESTILOS PARA INDICADOR DE ARCHIVO ========== */
.archivo-indicator {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.5rem;
  padding: 0.3rem 0.6rem;
  background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
  border-radius: 4px;
  border-left: 3px solid #28a745;
  font-size: 0.75rem;
}

.archivo-indicator i {
  font-size: 1rem;
  color: #28a745;
}

.archivo-text {
  color: #155724;
  font-weight: 500;
}

/* ========== ESTILOS PARA BOTÓN EXPORTAR ========== */
.export-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  background-color: #28a745;
  color: white;
  transition: background-color 0.2s;
}

.export-button:hover:not(:disabled) {
  background-color: #218838;
}

.export-button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
}

/* ========== MEJORAS ADICIONALES PARA INFORMACIÓN LARGA ========== */
.campo-valor.long-text {
  max-height: 150px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #ccc #f1f1f1;
}

.campo-valor.long-text::-webkit-scrollbar {
  width: 6px;
}

.campo-valor.long-text::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.campo-valor.long-text::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.campo-valor.long-text::-webkit-scrollbar-thumb:hover {
  background: #999;
}

/* NUEVO: Estilos para el botón de historial */
.btn-historial {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.25rem 0.5rem;
  margin-left: 0.75rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-historial:hover {
  background-color: #0056b3;
}

.btn-historial i {
  font-size: 1rem;
}

/* ========== RESPONSIVE DESIGN ========== */
@media (max-width: 1024px) {
  .filters {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }
  
  .date-filter {
    grid-column: span 1;
    min-width: 180px;
  }
  
  .date-range-inputs {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
}

@media (max-width: 768px) {

  .notifications-section {
    /* NUEVO: Altura ajustada para móviles */
    max-height: 60vh;
  }
  
  .notificaciones-table th {
    /* NUEVO: Padding reducido en móviles */
    padding: 0.4rem 0.5rem;
    font-size: 0.8rem;
    /* NUEVO: Altura mínima para mejor touch */
    min-height: 44px;
  }
  
  .notificaciones-table td {
    padding: 0.4rem 0.5rem;
    font-size: 0.8rem;
  }

  .container {
    padding: 0 0.5rem;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .filters {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .date-filter {
    grid-column: span 1;
    min-width: auto;
  }
  
  .filter-options {
    margin-top: 0.5rem;
    padding-top: 0.5rem;
  }
  
  .filter-actions {
    justify-content: stretch;
  }
  
  .filter-button,
  .clear-button {
    flex: 1;
    justify-content: center;
  }
  
  .summary-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .summary-stats {
    justify-content: center;
  }
  
  .summary-actions {
    justify-content: center;
  }
  

  
  .modal-container {
    margin: 0.5rem;
    max-height: calc(100vh - 1rem);
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 1rem;
  }
  
  .info-basica {
    grid-template-columns: 1fr;
  }
  
  .detalle-campo {
    padding: 0.75rem;
  }
  
  .campo-valor {
    font-size: 0.85rem;
  }
  
  /* Rutas en móvil */
  .detalle-campo:has(.campo-label:contains("Ruta")) .campo-valor,
  .detalle-campo:has(.campo-label:contains("Path")) .campo-valor {
    font-size: 0.75rem;
    padding: 0.5rem;
  }
  
  .pagination {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .pagination-controls {
    order: 2;
  }
  
  .pagination-options {
    order: 3;
  }
  
  .informe-especial-button {
    font-size: 0.8rem;
    padding: 0.4rem 0.8rem;
  }
  
  .button-badge {
    font-size: 0.65rem;
    padding: 0.15rem 0.4rem;
  }
}

@media (max-width: 480px) {

  .notifications-section {
    /* NUEVO: Altura más pequeña para pantallas muy pequeñas */
    max-height: 50vh;
  }
  .filters-section {
    padding: 1rem;
  }
  
  .filter-actions {
    flex-direction: column;
  }
  
  .filter-button,
  .clear-button {
    width: 100%;
    justify-content: center;
  }
  
  .date-range-inputs {
    gap: 0.5rem;
  }
  
  .date-field label {
    font-size: 0.75rem;
  }
  
  .date-input {
    padding: 0.4rem;
    font-size: 0.8rem;
  }
  
  .summary-stats {
    flex-direction: column;
    align-items: stretch;
  }
  
  .summary-actions {
    flex-direction: column;
  }
  
  .acciones-container {
    flex-direction: column;
  }
  
  .type-chips {
    flex-direction: column;
  }
  
  .modal-container {
    margin: 0.25rem;
    max-height: calc(100vh - 0.5rem);
  }
  
  .detalle-campo {
    padding: 0.5rem;
  }
  
  .campo-label {
    font-size: 0.85rem;
  }
  
  .campo-valor {
    font-size: 0.8rem;
  }
}


@media print {
  .filters-section,
  .summary-actions,
  .column-acciones,
  .modal-overlay {
    display: none !important;
  }
  
  .notificaciones-table {
    font-size: 0.7rem;
  }
  
  .notificaciones-table th,
  .notificaciones-table td {
    padding: 0.2rem;
  }
}
</style>