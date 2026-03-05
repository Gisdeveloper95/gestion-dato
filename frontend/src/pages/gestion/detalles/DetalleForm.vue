<template>
  <div class="detalle-form-container">
    <h2 class="form-title">{{ isEditing ? 'Editar Detalle Insumo' : 'Crear Detalle Insumo' }}</h2>
    
    <!-- Filtros jerárquicos -->
    <div class="filtros-section">
      <div class="row">
        <div class="col-md-6">
          <div class="form-group">
            <label for="departamento" class="required">Departamento:</label>
            <select 
              id="departamento" 
              v-model="filtros.departamento" 
              @change="cargarMunicipios"
              class="form-control"
              required
            >
              <option value="">Seleccione un departamento</option>
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
        <div class="col-md-6">
          <div class="form-group">
            <label for="municipio" class="required">Municipio:</label>
            <select 
              id="municipio" 
              v-model="filtros.municipio" 
              @change="cargarInsumos"
              class="form-control"
              :disabled="!filtros.departamento || municipios.length === 0"
              required
            >
              <option value="">Seleccione un municipio</option>
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
      </div>
      
      <div class="row">
        <div class="col-md-6">
          <div class="form-group">
            <label for="insumo" class="required">Insumo:</label>
            <select 
              id="insumo" 
              v-model="filtros.insumo" 
              @change="cargarClasificaciones"
              class="form-control"
              :disabled="!filtros.municipio || insumos.length === 0"
              required
            >
              <option value="">Seleccione un insumo</option>
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

        <!-- ✅ ZONA: Solo mostrar si no es tipo específico -->
        <div class="col-md-6" v-if="mostrarZona">
          <div class="form-group">
            <label for="zona_filtro" class="required">Zona:</label>
            <select 
              id="zona_filtro" 
              v-model="filtros.zona" 
              @change="onZonaChange"
              class="form-control"
              :key="`zona-${filtros.zona}-${zonas.length}`"
              required
            >
              <option value="">Seleccione una zona</option>
              <option 
                v-for="zona in zonas" 
                :key="zona.zona" 
                :value="zona.zona"
                :selected="zona.zona === filtros.zona"
              >
                {{ zona.zona }}
              </option>
            </select>
            <!-- ✅ DEBUG INFO -->
            <small v-if="isEditing" class="text-muted debug-info">
              Debug: Zona actual = "{{ filtros.zona }}" | Zonas cargadas = {{ zonas.length }}
            </small>
          </div>
        </div>
      </div>
      
      <div class="row">
        <div class="col-md-6">
          <div class="form-group">
            <label for="clasificacion" class="required">Clasificación:</label>
            <select 
              id="clasificacion" 
              v-model="formData.cod_clasificacion"
              class="form-control"
              :disabled="!filtros.insumo || clasificaciones.length === 0"
              required
            >
              <option value="">Seleccione una clasificación</option>
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

      <!-- Sub-Dominio (solo para Insumos Fuentes Secundarias) -->
      <div v-if="mostrarSubClasificacion" class="row">
        <div class="col-md-6">
          <div class="form-group">
            <label for="sub_clasificacion" class="required">Sub-Dominio:</label>
            <select
              id="sub_clasificacion"
              v-model="formData.cod_sub_clasificacion"
              class="form-control"
              :disabled="cargandoSubClasificaciones || subClasificaciones.length === 0"
              required
            >
              <option value="">Seleccione un sub-dominio</option>
              <option
                v-for="sub in subClasificaciones"
                :key="sub.cod_sub_clasificacion"
                :value="sub.cod_sub_clasificacion"
              >
                {{ sub.nombre }}
              </option>
            </select>
            <small v-if="cargandoSubClasificaciones" class="text-info loading-info">
              <i class="fas fa-spinner fa-spin"></i> Cargando sub-dominios...
            </small>
            <small v-if="subClasificaciones.length === 1 && formData.cod_sub_clasificacion" class="text-muted">
              Sub-dominio auto-seleccionado (unico disponible)
            </small>
          </div>
        </div>
      </div>

      <!-- ✅ Centro Poblado (condicional) - MEJORADO -->
      <div v-if="mostrarCentroPoblado" class="row">
        <div class="col-md-6">
          <div class="form-group">
            <label for="centro_poblado" class="required">Centro Poblado:</label>
            <select 
              id="centro_poblado" 
              v-model="formData.cod_centro_poblado"
              class="form-control"
              :disabled="cargandoCentrosPoblados || centrosPoblados.length === 0"
              :key="`centro-${formData.cod_centro_poblado}-${centrosPoblados.length}`"
              required
            >
              <option value="">Seleccione un centro poblado</option>
              <option 
                v-for="centro in centrosPoblados" 
                :key="centro.cod_centro_poblado" 
                :value="centro.cod_centro_poblado"
                :selected="centro.cod_centro_poblado === formData.cod_centro_poblado"
              >
                {{ centro.cod_centro_poblado }} - {{ centro.nom_centro_poblado }}
              </option>
            </select>
            <!-- ✅ DEBUG INFO MEJORADO -->
            <small v-if="isEditing" class="text-muted debug-info">
              Debug: Centro = "{{ formData.cod_centro_poblado }}" | Centros cargados = {{ centrosPoblados.length }}
            </small>
            <small v-if="cargandoCentrosPoblados" class="text-info loading-info">
              <i class="fas fa-spinner fa-spin"></i> Cargando centros poblados...
            </small>
            <small v-if="!cargandoCentrosPoblados && centrosPoblados.length === 0 && filtros.municipio" class="text-warning">
              <i class="material-icons">warning</i> No hay centros poblados disponibles para este municipio
            </small>
          </div>
        </div>
      </div>
    </div>

    <!-- ✅ MOSTRAR CONFIGURACIÓN ACTIVA -->
    <div v-if="tipoInsumoSeleccionado" class="configuracion-activa">
      <div class="config-header">
        <i class="material-icons">settings</i>
        <span>Configuración para: {{ tipoInsumoSeleccionado.categoria_nombre }}</span>
      </div>
      <div class="config-content">
        <div class="config-item" v-if="esCartografiaBasica">
          <span class="config-label">Estado:</span>
          <span class="config-value">OFICIALIZADO (por defecto)</span>
        </div>
        <div class="config-item" v-if="esEstudioAgrologico">
          <span class="config-label">Estado:</span>
          <span class="config-value">OFICIALIZADO (por defecto)</span>
        </div>
        <div class="config-item" v-if="esDeslinde || esCartografiaBasica || esEstudioAgrologico">
          <span class="config-label">Cubrimiento:</span>
          <span class="config-value">100% automático</span>
        </div>
        <div class="config-item" v-if="esInformacionCatastral || esInsumosFuentesSecundarias || esSaldoConservacion">
          <span class="config-label">Campos ocultos:</span>
          <span class="config-value">
            {{ esInformacionCatastral ? 'Cubrimiento, Escala, Área' : '' }}
            {{ esInsumosFuentesSecundarias ? 'Escala, Cubrimiento, Área' : '' }}
            {{ esSaldoConservacion ? 'Área, Cubrimiento, Escala' : '' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Formulario principal -->
    <form @submit.prevent="guardarDetalle" class="form-main">
      <!-- Campos ocultos -->
      <input type="hidden" v-model="formData.cod_detalle" />
      <input type="hidden" v-model="formData.ruta_archivo" />
      
      <div class="row">
        <!-- COLUMNA IZQUIERDA -->
        <div class="col-md-6">
          <div class="form-group">
            <label for="usuario" class="required">Usuario:</label>
            <input 
              type="text" 
              id="usuario" 
              v-model="usuarioNombre" 
              class="form-control" 
              readonly 
              required
            />
            <input type="hidden" v-model="formData.cod_usuario" />
          </div>
          
          <!-- ✅ ESCALA: Solo mostrar si aplica -->
          <div class="form-group" v-if="mostrarEscala">
            <label for="escala">Escala:</label>
            <input 
              type="text" 
              id="escala" 
              v-model="formData.escala" 
              class="form-control" 
              placeholder="Ej: 1:25000"
            />
          </div>
          
          <div class="form-group">
            <label for="formato" class="required">Formato:</label>
            <div class="search-input-container">
              <input 
                type="text" 
                id="formato_search" 
                v-model="formatoSearch" 
                @input="filtrarFormatos"
                class="form-control" 
                placeholder="Buscar formato..."
                :class="{ 'campo-auto': campoEsAutomatico('formato') }"
              />
              <select 
                id="formato" 
                v-model="formData.formato_tipo" 
                class="form-control formato-select"
                :class="{ 'campo-auto': campoEsAutomatico('formato') }"
                required
              >
                <option value="">Seleccione un formato</option>
                <option 
                  v-for="formato in formatosFiltrados" 
                  :key="formato.cod_formato_tipo" 
                  :value="formato.cod_formato_tipo"
                >
                  {{ formato.cod_formato_tipo }}
                </option>
              </select>
            </div>
            <small v-if="campoEsAutomatico('formato')" class="form-hint">
              <i class="material-icons">auto_fix_high</i>
              Valor establecido automáticamente
            </small>
          </div>
          
          <!-- ✅ ÁREA: Solo mostrar si aplica -->
          <div class="form-group" v-if="mostrarCubrimiento">
            <label for="area_municipio">Área del Municipio:</label>
            <div class="area-input-container">
              <input 
                type="text" 
                id="area_municipio" 
                v-model="areaMunicipioFormatted" 
                class="form-control area-input area-readonly" 
                readonly
                placeholder="Se carga automáticamente"
              />
              <span class="area-unit-fixed">Ha</span>
            </div>
            <small class="form-hint">
              <i class="material-icons">info</i>
              Área obtenida automáticamente del municipio seleccionado
            </small>
          </div>
          
          <div class="form-group">
            <label for="fechaEntrega">Fecha de Entrega (Cartografia):</label>
            <input 
              type="date" 
              id="fechaEntrega" 
              v-model="formData.fecha_entrega" 
              class="form-control"
            />
          </div>
        </div>
        
        <!-- COLUMNA DERECHA -->
        <div class="col-md-6">
          <div class="form-group">
            <label for="entidad" class="required">Entidad:</label>
            <div class="search-input-container">
              <input
                type="text"
                id="entidad_search"
                v-model="entidadSearch"
                @input="filtrarEntidades"
                class="form-control"
                placeholder="Buscar entidad..."
                :class="{ 'campo-auto': campoEsAutomatico('entidad') || esInsumosFuentesSecundarias }"
                :disabled="esInsumosFuentesSecundarias"
              />
              <select
                id="entidad"
                v-model="formData.cod_entidad"
                class="form-control entidad-select"
                :class="{ 'campo-auto': campoEsAutomatico('entidad') || esInsumosFuentesSecundarias }"
                :disabled="esInsumosFuentesSecundarias"
                required
              >
                <option value="">Seleccione una entidad</option>
                <option
                  v-for="entidad in entidadesFiltradas"
                  :key="entidad.cod_entidad"
                  :value="entidad.cod_entidad"
                >
                  {{ entidad.nom_entidad }}
                </option>
              </select>
            </div>
            <small v-if="esInsumosFuentesSecundarias && formData.cod_entidad" class="form-hint">
              <i class="material-icons">lock</i>
              Entidad asignada según clasificación
            </small>
            <small v-else-if="campoEsAutomatico('entidad')" class="form-hint">
              <i class="material-icons">auto_fix_high</i>
              IGAC establecido automáticamente
            </small>
          </div>
          
          <div class="form-group">
            <label for="estado" class="required">Estado:</label>
            <select 
              id="estado" 
              v-model="formData.estado" 
              class="form-control"
              :class="{ 'campo-auto': campoEsAutomatico('estado') }"
              required
            >
              <option value="">Seleccione un estado</option>
              <option 
                v-for="estado in opcionesEstado" 
                :key="estado" 
                :value="estado"
              >
                {{ estado }}
              </option>
            </select>
            <small v-if="campoEsAutomatico('estado')" class="form-hint">
              <i class="material-icons">auto_fix_high</i>
              Valor establecido automáticamente
            </small>
          </div>
          
          <!-- ✅ CUBRIMIENTO: Solo mostrar si aplica -->
          <div class="form-group" v-if="mostrarCubrimiento">
            <label for="cubrimiento">Cubrimiento:</label>
            <div class="area-input-container">
              <input 
                type="text" 
                id="cubrimiento_valor" 
                v-model="formData.cubrimiento_valor" 
                @input="onCubrimientoChange"
                class="form-control area-input" 
                :class="{ 'campo-auto': campoEsAutomatico('cubrimiento') }"
                placeholder="Ej: 100"
              />
              <span class="area-unit-fixed">Ha</span>
            </div>
            <small v-if="campoEsAutomatico('cubrimiento')" class="form-hint">
              <i class="material-icons">auto_fix_high</i>
              Establecido automáticamente al 100%
            </small>
          </div>
          
          <!-- ✅ PORCENTAJE: Solo mostrar si aplica -->
          <div class="form-group" v-if="mostrarCubrimiento">
            <label for="porcentaje_cubrimiento">Porcentaje de Cubrimiento:</label>
            <div class="porcentaje-container">
              <input 
                type="text" 
                id="porcentaje_cubrimiento" 
                v-model="porcentajeCubrimientoCalculado" 
                class="form-control porcentaje-input" 
                readonly
                placeholder="Se calcula automáticamente"
              />
              <span class="porcentaje-symbol">%</span>
            </div>
            <small class="form-hint">
              <i class="material-icons">calculate</i>
              Calculado: (Cubrimiento ÷ Área Municipio) × 100
            </small>
          </div>
          
          <div class="form-group">
            <label for="vigencia">Vigencia (Año):</label>
            <input 
              type="number" 
              id="vigencia" 
              v-model="formData.vigencia" 
              class="form-control"
              min="1900"
              max="2100"
              step="1"
              placeholder="Ej: 2025"
            />
          </div>
        </div>
      </div>
      
      <div class="row">
        <div class="col-md-6">
          <div class="form-group">
            <label for="fechaDisposicion">Fecha de Disposición (Sub. Proyectos):</label>
            <input 
              type="date" 
              id="fechaDisposicion" 
              v-model="formData.fecha_disposicion" 
              class="form-control"
              :class="{ 'campo-auto': campoEsAutomatico('fechaDisposicion') }"
            />
            <small v-if="campoEsAutomatico('fechaDisposicion')" class="form-hint">
              <i class="material-icons">auto_fix_high</i>
              Fecha actual establecida automáticamente
            </small>
          </div>
        </div>
      </div>
      
      <div class="row">
        <div class="col-md-12">
          <div class="form-group">
            <label for="observacion">Observaciones:</label>
            <textarea 
              id="observacion" 
              v-model="formData.observacion" 
              class="form-control" 
              rows="4"
              placeholder="Observaciones adicionales sobre el detalle..."
            ></textarea>
          </div>
        </div>
      </div>
    </form>
    
    <!-- ✅ SECCIÓN MOVIDA AL FINAL: Selección de Archivo -->
    <div class="archivo-selection-section">
      <h3 class="section-title">
        <i class="material-icons">attach_file</i>
        Asociar Archivo (Opcional)
      </h3>
      
      <div class="archivo-selection-container">
        <!-- Toggle entre selección automática y manual -->
        <div class="selection-mode-toggle">
          <label class="radio-option">
            <input 
              type="radio" 
              v-model="archivoSelectionMode" 
              value="automatico"
              @change="onSelectionModeChange"
            />
            <span>Seleccionar de archivos disponibles</span>
          </label>
          <label class="radio-option">
            <input 
              type="radio" 
              v-model="archivoSelectionMode" 
              value="manual"
              @change="onSelectionModeChange"
            />
            <span>Ingresar ruta manualmente</span>
          </label>
        </div>

        <!-- Selección automática de archivos -->
        <div v-if="archivoSelectionMode === 'automatico'" class="archivo-automatico">
          <!-- Estado de carga -->
          <div v-if="archivosLoading" class="loading-state">
            <i class="fas fa-spinner fa-spin"></i>
            <span>Cargando archivos disponibles...</span>
          </div>

          <!-- Error al cargar archivos -->
          <div v-else-if="archivosError" class="error-state">
            <i class="material-icons">error</i>
            <span>{{ archivosError }}</span>
            <button @click="cargarArchivosDisponibles" class="btn-retry">Reintentar</button>
          </div>

          <!-- Sin archivos disponibles -->
          <div v-else-if="archivosDisponibles.length === 0" class="empty-state">
            <i class="material-icons">folder_open</i>
            <p>No hay archivos disponibles para este municipio.</p>
            <small>Seleccione un municipio válido o use la opción manual.</small>
          </div>

          <!-- Lista de archivos disponibles -->
          <div v-else class="archivos-disponibles">
            <div class="form-group">
              <label for="archivo_select">
                <span class="contador-dinamico">Archivos Disponibles: {{ contadorArchivos }}</span>
                <span v-if="filtros.insumo && getCategoriaInsumoSeleccionado() && !mostrarTodos" class="filter-info">
                  - Filtrados por categoría: {{ getCategoriaInsumoSeleccionado() }}
                </span>
                <span v-if="mostrarTodos" class="filter-info">
                  - Mostrando todos
                </span>
              </label>
              
              <!-- Información de categorías disponibles -->
              <div v-if="patronesDisponibles.length > 0" class="info-categorias">
                <small class="text-info">
                  <i class="material-icons">info</i>
                  Categorías en archivos: {{ patronesDisponibles.join(', ') }}
                </small>
                <small v-if="contadorArchivos === 0 && filtros.insumo && getCategoriaInsumoSeleccionado()" class="text-warning">
                  <i class="material-icons">warning</i>
                  No hay archivos para la categoría "{{ getCategoriaInsumoSeleccionado() }}". 
                  <button @click="mostrarTodosLosArchivos" class="btn-link">Ver todos los archivos</button>
                </small>
              </div>
              
              <div class="archivo-search">
                <i class="material-icons">search</i>
                <input 
                  type="text"
                  v-model="archivoSearchTerm"
                  placeholder="Buscar archivo por nombre..."
                  class="form-control search-input"
                />
              </div>
              
              <select 
                id="archivo_select"
                v-model="selectedArchivoId"
                @change="onArchivoSelect"
                class="form-control archivo-select"
              >
                <option value="">-- Seleccione un archivo --</option>
                <option 
                  v-for="archivo in archivosFiltrados" 
                  :key="archivo.id_lista_archivo" 
                  :value="archivo.id_lista_archivo"
                >
                  {{ archivo.nombre_insumo }}
                </option>
              </select>
            </div>

            <!-- SOLO SUBFILTROS INFORMACIÓN CATASTRAL -->
            <template v-if="mostrarFiltrosInfoCatastral">
              <div class="subfiltros-section">
                <h5 class="subfiltros-title">
                  <i class="material-icons">filter_list</i>
                  Filtros adicionales para Información Catastral
                </h5>
                
                <div class="subfiltros-grid">
                  <div class="filter-item">
                    <label for="tipo_info_catastral_filtro">Tipo de información:</label>
                    <select 
                      id="tipo_info_catastral_filtro"
                      v-model="filtroTipoInfoCatastral" 
                      class="form-control filter-select"
                    >
                      <option value="">Todos los tipos</option>
                      <option 
                        v-for="tipo in tiposInfoCatastralUnicos" 
                        :key="tipo" 
                        :value="tipo"
                      >
                        {{ tipo }}
                      </option>
                    </select>
                  </div>
                </div>
              </div>
            </template>

            <!-- INFORMACIÓN DE FILTROS ACTIVOS -->
            <div v-if="hayFiltrosActivosArchivos" class="filtros-activos-info">
              <div class="filtros-activos-content">
                <i class="material-icons">filter_list</i>
                <span>Filtros activos:</span>
                <div class="filtros-tags">
                  <!-- Mostrar clasificación seleccionada -->
                  <span v-if="getClasificacionSeleccionada()" class="filtro-tag clasificacion-tag">
                    📋 {{ getClasificacionSeleccionada().nombre }}
                    <small>(seleccionado arriba)</small>
                  </span>
                  
                  <!-- Mostrar centro poblado seleccionado -->
                  <span v-if="getCentroPobladoSeleccionado() && mostrarCentroPoblado" class="filtro-tag centro-tag">
                    🏘️ Centro: {{ getCentroPobladoFromCod(getCentroPobladoSeleccionado()) }}
                    <small>(seleccionado arriba)</small>
                  </span>
                  
                  <!-- Filtro de información catastral -->
                  <span v-if="filtroTipoInfoCatastral" class="filtro-tag">
                    📊 Info: {{ filtroTipoInfoCatastral }}
                    <button @click="filtroTipoInfoCatastral = ''" class="tag-close">
                      <i class="material-icons">close</i>
                    </button>
                  </span>
                  
                  <!-- Filtro de búsqueda -->
                  <span v-if="archivoSearchTerm" class="filtro-tag">
                    🔍 Búsqueda: "{{ archivoSearchTerm }}"
                    <button @click="archivoSearchTerm = ''" class="tag-close">
                      <i class="material-icons">close</i>
                    </button>
                  </span>
                </div>
                <button @click="limpiarFiltrosArchivos" class="btn-limpiar-filtros">
                  <i class="material-icons">clear_all</i> Limpiar filtros adicionales
                </button>
              </div>
            </div>

            <!-- Vista previa del archivo seleccionado -->
            <div v-if="archivoSeleccionado" class="archivo-preview">
              <div class="preview-header">
                <i class="material-icons">description</i>
                <span>Archivo Seleccionado</span>
              </div>
              <div class="preview-content">
                <div class="preview-row">
                  <strong>Nombre:</strong>
                  <span>{{ archivoSeleccionado.nombre_insumo }}</span>
                </div>
                <div class="preview-row">
                  <strong>Categoría:</strong>
                  <span class="categoria-detectada">
                    {{ getCategoriaDelArchivo(archivoSeleccionado) || 'No detectada' }}
                  </span>
                </div>
                <div class="preview-row">
                  <strong>Ruta:</strong>
                  <span class="path-text">{{ mostrarRutaWindows(archivoSeleccionado.path_file) }}</span>
                </div>
                <div class="preview-row" v-if="archivoSeleccionado.fecha_disposicion">
                  <strong>Fecha:</strong>
                  <span>{{ formatDate(archivoSeleccionado.fecha_disposicion) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Entrada manual de ruta -->
        <div v-else class="archivo-manual">
          <div class="form-group">
            <label for="ruta_manual">Ruta del Archivo:</label>
            <textarea 
              id="ruta_manual"
              v-model="formData.ruta_archivo"
              class="form-control"
              rows="3"
              placeholder="Ejemplo: \\repositorio\DirGesCat\2510SP\H_Informacion_Consulta\Sub_Proy\01_actualiz_catas\54\810\FCP\01_preo\07_insu\01_carto_basic\01_rast\01_orto\1_urb\006\Orto10_54810006_20221209\Orto10_Metadato_54810006_20221209.pdf"
            ></textarea>
            <small class="form-hint">
              Ingrese la ruta completa del archivo. Puede usar barras normales (/) o invertidas (\).
            </small>
            <!-- ✅ DEBUG INFO PARA ARCHIVO -->
            <small v-if="isEditing" class="text-info debug-info">
              Debug: Modo = "{{ archivoSelectionMode }}" | Archivo ID = "{{ selectedArchivoId }}" | Ruta = "{{ formData.ruta_archivo?.substring(0, 50) }}..."
            </small>
          </div>
        </div>

        <!-- Botón para limpiar selección -->
        <div v-if="formData.ruta_archivo" class="archivo-actions">
          <button 
            type="button" 
            @click="limpiarSeleccionArchivo" 
            class="btn-clear-archivo"
          >
            <i class="material-icons">clear</i>
            Limpiar selección
          </button>
        </div>
      </div>
    </div>
    

    
    <!-- Formulario principal - BOTONES -->
    <form @submit.prevent="guardarDetalle" class="form-buttons-section">
      <div class="form-buttons">
        <button type="button" class="btn btn-secondary" @click="cancelar">Cancelar</button>
        <button type="submit" class="btn btn-primary" :disabled="!isFormValid">Guardar Detalle</button>
      </div>
    </form>
    
    <!-- Mensajes de error/éxito -->
    <div v-if="mensaje.texto" class="alert" :class="{ 'alert-success': mensaje.tipo === 'success', 'alert-danger': mensaje.tipo === 'error' }">
      {{ mensaje.texto }}
    </div>
    
    <!-- Leyenda para campos requeridos -->
    <div class="required-fields-legend">
      <span class="required-indicator">*</span> Campos obligatorios
    </div>


  </div>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/store/auth';
import axios from 'axios';

// URL base para las API
import api, { API_URL } from '@/api/config';
// Utilidad para convertir rutas Linux a Windows para visualización
import { linuxToWindowsPath } from '@/utils/pathUtils';
// ✅ IMPORT CORRECTO USANDO EL API ACTUALIZADO
import { getCentrosPobladosPorMunicipio, centrosPobladosApi } from '@/api/centrosPoblados';
import { getMunicipioById } from '@/api/municipios';
import { subClasificacionesApi } from '@/api/subClasificaciones';

export default {
  name: 'DetalleForm',
  
  setup() {
    console.log('🚀 Iniciando setup del componente DetalleForm');
    const router = useRouter();
    const route = useRoute();
    const authStore = useAuthStore();
    
    // Estado de carga y error
    const cargando = ref(false);
    const error = ref(null);
    
    // Filtros jerárquicos con zona añadida
    const filtros = ref({
      departamento: '',
      zona: '',
      municipio: '',
      insumo: ''
    });
    
    // Catálogos y dominios
    const departamentos = ref([]);
    const municipios = ref([]);
    const insumos = ref([]);
    const clasificaciones = ref([]);
    const zonas = ref([]);
    const formatos = ref([]);
    const entidades = ref([]);
    
    // Variables para el filtro de formatos y entidades
    const formatoSearch = ref('');
    const entidadSearch = ref('');
    
    // Variables para centros poblados
    const centrosPoblados = ref([]);
    const cargandoCentrosPoblados = ref(false);

    // Variables para sub-clasificaciones de fuentes secundarias
    const subClasificaciones = ref([]);
    const cargandoSubClasificaciones = ref(false);

    // Variables para manejo de archivos
    const archivosDisponibles = ref([]);
    const archivosLoading = ref(false);
    const archivosError = ref(null);
    const archivoSelectionMode = ref('automatico');
    const selectedArchivoId = ref('');
    const archivoSeleccionado = ref(null);
    const archivoSearchTerm = ref('');

    // Variable para rutas de archivos ya usadas en otros detalles
    const rutasEnUso = ref([]);
    const rutaActualEditando = ref(''); // Para guardar la ruta del detalle que estamos editando

    // Variable para filtro de Información Catastral
    const filtroTipoInfoCatastral = ref('');

    // Variables para área del municipio
    const areaMunicipio = ref('');
    const cargandoAreaMunicipio = ref(false);

    // Datos del formulario
    const formData = ref({
      cod_detalle: '', 
      cod_clasificacion: '',
      cod_usuario: '',
      escala: '',
      estado: '',
      cubrimiento_valor: '',
      fecha_entrega: '',
      fecha_disposicion: '',
      area_municipio: '',
      porcentaje_cubrimiento: '',
      cod_entidad: '',
      observacion: '',
      vigencia: '',
      formato_tipo: '',
      zona: '',
      cod_centro_poblado: '',
      ruta_archivo: '',
      cod_sub_clasificacion: ''
    });
    
    // Mensajes de error/éxito
    const mensaje = ref({
      texto: '',
      tipo: ''
    });
    
    // Usuario actual
    const usuarioNombre = ref('');
    
    // Computed para isEditing
    const isEditing = computed(() => {
      return !!route.params.id;
    });

    // ✅ NUEVOS COMPUTED PARA MANEJO DE TIPOS DE INSUMO
    
    // Detectar el tipo de insumo seleccionado (CORREGIDO PARA MANEJAR PROXY)
    const tipoInsumoSeleccionado = computed(() => {
      if (!filtros.value.insumo) return null;
      
      const insumoSeleccionado = insumos.value.find(i => i.cod_insumo == filtros.value.insumo);
      if (!insumoSeleccionado) return null;
      
      // Extraer el valor correcto del tipo_insumo (que puede ser un Proxy)
      let tipoInsumoValor = insumoSeleccionado.tipo_insumo;
      if (typeof tipoInsumoValor === 'object' && tipoInsumoValor !== null) {
        // Si es un objeto/proxy, buscar la propiedad que contiene el valor
        tipoInsumoValor = tipoInsumoValor.tipo_insumo || 
                         tipoInsumoValor.nom_tipo_insumo || 
                         tipoInsumoValor.nombre || 
                         String(tipoInsumoValor);
      }
      
      return {
        tipo_insumo: tipoInsumoValor,
        categoria_nombre: insumoSeleccionado.categoria_nombre
      };
    });

    // Determinar si es Cartografía Básica (CORREGIDO)
    const esCartografiaBasica = computed(() => {
      const tipo = tipoInsumoSeleccionado.value;
      const esInsumo = tipo?.tipo_insumo === 'Insumo Primario';
      const esCategoria = tipo?.categoria_nombre === 'Cartografia Basica';
      console.log(`🔍 Cartografía Básica: ${esInsumo} && ${esCategoria} = ${esInsumo && esCategoria}`);
      return esInsumo && esCategoria;
    });

    // Determinar si es Estudio Agrológ ico (CORREGIDO)
    const esEstudioAgrologico = computed(() => {
      const tipo = tipoInsumoSeleccionado.value;
      const esInsumo = tipo?.tipo_insumo === 'Insumo Primario';
      const esCategoria = tipo?.categoria_nombre === 'Estudio Agrologico';
      console.log(`🔍 Estudio Agrológ ico: ${esInsumo} && ${esCategoria} = ${esInsumo && esCategoria}`);
      return esInsumo && esCategoria;
    });

    // Determinar si es Información Catastral (CORREGIDO)
    const esInformacionCatastral = computed(() => {
      const tipo = tipoInsumoSeleccionado.value;
      const esInsumo = tipo?.tipo_insumo === 'Insumo Primario';
      const esCategoria = tipo?.categoria_nombre === 'Informacion Catastral';
      console.log(`🔍 Información Catastral: ${esInsumo} && ${esCategoria} = ${esInsumo && esCategoria}`);
      return esInsumo && esCategoria;
    });

    // Determinar si es Deslinde (CORREGIDO)
    const esDeslinde = computed(() => {
      const tipo = tipoInsumoSeleccionado.value;
      const esInsumo = tipo?.tipo_insumo === 'Insumo Primario';
      const esCategoria = tipo?.categoria_nombre === 'Deslinde';
      console.log(`🔍 Deslinde: ${esInsumo} && ${esCategoria} = ${esInsumo && esCategoria}`);
      return esInsumo && esCategoria;
    });

    // Determinar si es Insumos Fuentes Secundarias (CORREGIDO)
    const esInsumosFuentesSecundarias = computed(() => {
      const tipo = tipoInsumoSeleccionado.value;
      const esInsumo = tipo?.tipo_insumo === 'Insumo Secundario';
      const esCategoria = tipo?.categoria_nombre === 'Insumos Fuentes Secundarias';
      console.log(`🔍 Insumos Fuentes Secundarias: ${esInsumo} && ${esCategoria} = ${esInsumo && esCategoria}`);
      return esInsumo && esCategoria;
    });

    // Helper: extraer código de dominio del nombre de clasificación
    function extraerDominio(nombreClasificacion) {
      if (!nombreClasificacion) return '';
      const parts = nombreClasificacion.split(' - ');
      return parts[0].trim();
    }

    // Mapeo dominio de clasificación → cod_entidad (para auto-selección en insumos secundarios)
    const DOMINIO_A_ENTIDAD = {
      'ANT': 'ANT',
      'ART': 'ART',
      'DAPRE': 'DAPRE',
      'MADS': 'MADS',
      'PNN': 'PNNC',
      'SICHI': 'SINCHI',
      'URT': 'URT',
      'ICANH': 'ICANH',
      'ANLA': 'ANLA',
      'MIN. CULTURA': 'MIN_CULTURA',
      'IGAC': 'IGAC',
      'DANE': 'DANE',
      'ANM': 'ANM',
      'INVIAS': 'INVIAS',
      'DETERMINANTE AMBIENTAL': 'CAR',
    };

    // Computed: mostrar dropdown de sub-clasificación
    const mostrarSubClasificacion = computed(() => {
      if (!esInsumosFuentesSecundarias.value) return false;
      if (!formData.value.cod_clasificacion) return false;
      const clasifSeleccionada = clasificaciones.value.find(
        c => c.cod_clasificacion == formData.value.cod_clasificacion
      );
      if (!clasifSeleccionada) return false;
      const dominio = extraerDominio(clasifSeleccionada.nombre);
      return dominio !== 'General';
    });

    // Cargar sub-clasificaciones según dominio seleccionado
    async function cargarSubClasificaciones(dominio) {
      subClasificaciones.value = [];
      formData.value.cod_sub_clasificacion = '';

      if (!dominio || dominio === 'General') return;

      cargandoSubClasificaciones.value = true;
      try {
        const resultado = await subClasificacionesApi.porDominio(dominio);
        subClasificaciones.value = resultado;

        // Auto-seleccionar si solo hay 1 sub-dominio (ART, SICHI, MIN. CULTURA)
        if (resultado.length === 1) {
          formData.value.cod_sub_clasificacion = resultado[0].cod_sub_clasificacion;
        }
      } catch (error) {
        console.error('Error al cargar sub-clasificaciones:', error);
      } finally {
        cargandoSubClasificaciones.value = false;
      }
    }

    // Determinar si es Saldo Conservación (CORREGIDO)
    const esSaldoConservacion = computed(() => {
      const tipo = tipoInsumoSeleccionado.value;
      const esInsumo = tipo?.tipo_insumo === 'Insumo Primario';
      const esCategoria = tipo?.categoria_nombre === 'Saldo Conservacion';
      console.log(`🔍 Saldo Conservación: ${esInsumo} && ${esCategoria} = ${esInsumo && esCategoria}`);
      return esInsumo && esCategoria;
    });

    // ✅ COMPUTED PARA MOSTRAR/OCULTAR CAMPOS (CORREGIDOS)

    // Mostrar campo Escala
    const mostrarEscala = computed(() => {
      const noMostrar = esInformacionCatastral.value || 
                       esInsumosFuentesSecundarias.value || 
                       esSaldoConservacion.value;
      console.log(`🔍 Mostrar Escala: !${noMostrar} = ${!noMostrar}`);
      return !noMostrar;
    });

    // Mostrar campos de Cubrimiento y Área
    const mostrarCubrimiento = computed(() => {
      const noMostrar = esInformacionCatastral.value || 
                       esInsumosFuentesSecundarias.value || 
                       esSaldoConservacion.value;
      console.log(`🔍 Mostrar Cubrimiento: !${noMostrar} = ${!noMostrar}`);
      return !noMostrar;
    });

    // Mostrar zona normalmente
    const mostrarZona = computed(() => {
      return true; // Siempre mostrar zona
    });

    // ✅ COMPUTED PARA OPCIONES DE ESTADO (CORREGIDO)
    const opcionesEstado = computed(() => {
      if (esCartografiaBasica.value) {
        console.log('🔍 Opciones de estado para Cartografía Básica');
        // Para Cartografía Básica: quitar "NO SE PRODUCIRA" y "EN PRODUCCION", agregar "NO APLICA"
        return [
          "OFICIALIZADO",
          "OFICIALIZADO PARCIAL", 
          "POR PRODUCIR",
          "SIN FECHA DEFINIDA",
          "NO APLICA"
        ];
      }
      
      console.log('🔍 Opciones de estado normales');
      // Para todos los demás casos, opciones normales (basado en estados.csv)
      return [
        "EN PRODUCCION",
        "NO SE PRODUCIRA", 
        "OFICIALIZADO",
        "OFICIALIZADO PARCIAL",
        "POR PRODUCIR",
        "SIN FECHA DEFINIDA"
      ];
    });

    // ✅ FUNCIÓN PARA DETERMINAR SI UN CAMPO ES AUTOMÁTICO (CORREGIDA)
    const campoEsAutomatico = (campo) => {
      switch (campo) {
        case 'entidad':
          const esEntidadAuto = esCartografiaBasica.value || esEstudioAgrologico.value || 
                               esInformacionCatastral.value || esDeslinde.value || esSaldoConservacion.value;
          console.log(`🔍 Campo entidad es automático: ${esEntidadAuto}`);
          return esEntidadAuto;
        case 'estado':
          const esEstadoAuto = esCartografiaBasica.value || esEstudioAgrologico.value || esInsumosFuentesSecundarias.value;
          console.log(`🔍 Campo estado es automático: ${esEstadoAuto}`);
          return esEstadoAuto;
        case 'formato':
          const esFormatoAuto = esCartografiaBasica.value || esEstudioAgrologico.value || 
                               esInformacionCatastral.value || esDeslinde.value || esInsumosFuentesSecundarias.value;
          console.log(`🔍 Campo formato es automático: ${esFormatoAuto}`);
          return esFormatoAuto;
        case 'cubrimiento':
          const esCubrimientoAuto = esCartografiaBasica.value || esEstudioAgrologico.value || esDeslinde.value;
          console.log(`🔍 Campo cubrimiento es automático: ${esCubrimientoAuto}`);
          return esCubrimientoAuto;
        case 'fechaDisposicion':
          const esFechaAuto = esCartografiaBasica.value;
          console.log(`🔍 Campo fechaDisposicion es automático: ${esFechaAuto}`);
          return esFechaAuto;
        default:
          return false;
      }
    };

    // ✅ Computed para mostrar centro poblado (MEJORADO)
    const mostrarCentroPoblado = computed(() => {
      if (!filtros.value.insumo || !filtros.value.zona) {
        console.log(`🔍 Mostrar Centro Poblado: false (sin insumo o zona)`);
        console.log(`   - Insumo: ${filtros.value.insumo}`);
        console.log(`   - Zona: "${filtros.value.zona}"`);
        return false;
      }
      
      const esCartografia = esCartografiaBasica.value;
      const esCentrosPoblados = filtros.value.zona === 'CENTROS POBLADOS';
      
      console.log(`🔍 Mostrar Centro Poblado: ${esCartografia} && ${esCentrosPoblados} = ${esCartografia && esCentrosPoblados}`);
      console.log(`   - Es Cartografía Básica: ${esCartografia}`);
      console.log(`   - Zona es CENTROS POBLADOS: ${esCentrosPoblados}`);
      console.log(`   - Zona actual: "${filtros.value.zona}"`);
      
      return esCartografia && esCentrosPoblados;
    });

    // COMPUTED PROPERTIES CORREGIDOS
    const mostrarFiltrosInfoCatastral = computed(() => {
      const resultado = esInformacionCatastral.value;
      console.log(`🔍 Mostrar filtros Info Catastral: ${resultado}`);
      return resultado;
    });

    const tiposInfoCatastralUnicos = computed(() => {
      if (!mostrarFiltrosInfoCatastral.value) return [];
      
      const tipos = new Set();
      archivosDisponibles.value.forEach(archivo => {
        if (archivo.path_file) {
          const tipo = getTipoInfoCatastralFromPath(archivo.path_file);
          if (tipo !== 'N/A') tipos.add(tipo);
        }
      });
      
      const ordenTipos = ['R1 & R2', 'GDB', 'Tablas Terreno & Construcción', 'Estudio ZHF & ZHG'];
      return ordenTipos.filter(tipo => tipos.has(tipo));
    });

    const hayFiltrosActivosArchivos = computed(() => {
      return filtroTipoInfoCatastral.value || 
             archivoSearchTerm.value ||
             getClasificacionSeleccionada() ||
             (getCentroPobladoSeleccionado() && mostrarCentroPoblado.value);
    });

    // Área del municipio formateada para mostrar
    const areaMunicipioFormatted = computed(() => {
      if (!areaMunicipio.value) return '';
      return areaMunicipio.value.replace(',', '.');
    });

    // Porcentaje de cubrimiento calculado automáticamente
    const porcentajeCubrimientoCalculado = computed(() => {
      // Si no se debe mostrar cubrimiento, retornar vacío
      if (!mostrarCubrimiento.value) {
        return '';
      }
      
      const cubrimiento = parseFloat(formData.value.cubrimiento_valor?.replace(',', '.') || '0');
      const area = parseFloat(areaMunicipio.value?.replace(',', '.') || '0');
      
      // Si no hay datos, retornar 0
      if (!cubrimiento || !area || area === 0) {
        return '0';
      }
      
      // Calcular porcentaje: (cubrimiento / área) * 100
      const porcentaje = (cubrimiento / area) * 100;
      
      // Redondear a 2 decimales y retornar solo el número (sin %)
      return Math.round(porcentaje * 100) / 100;
    });

    // Mapeo de categorías con nombres exactos de la BD
    const categoriasToPathPatterns = {
      'Cartografia Basica': ['01_carto_basic', 'carto_basic', 'cartografia_basica', '01_carto_basica'], 
      'Estudio Agrologico': ['02_estu_agro', 'estu_agro', 'estudios_agrologicos', 'agrologico'],
      'Informacion Catastral': ['03_info_catas', 'info_catas', 'informacion_catastral', 'catastral'],
      'Deslinde': ['04_deslin', 'deslinde'],
      'Perimetro': ['05_perim', 'perimetro'],
      'Insumos Registro': ['06_insu_regis', 'insumos_registro'],
      'Insumos Fuente Secundaria': ['07_insu_fte_secun', 'fuente_secundaria'],
      'Inst Ordenamiento Territorial': ['08_inst_ord_terri', 'ordenamiento_territorial'],
      'Saldos Conservacion': ['09_sald_conserva', 'saldos_conservacion'],
      'Ortofoto': ['orto', 'ortofoto'],
      'MDT': ['mdt', 'modelo_digital'],
      'Topografia': ['topog', 'topografia']
    };

    // FUNCIÓN PARA OBTENER LA CATEGORÍA DEL INSUMO SELECCIONADO
    const getCategoriaInsumoSeleccionado = () => {
      if (!filtros.value.insumo) return null;
      
      const insumoSeleccionado = insumos.value.find(i => i.cod_insumo == filtros.value.insumo);
      if (!insumoSeleccionado) return null;
      
      return insumoSeleccionado.categoria_nombre;
    };

    // FUNCIÓN PARA VERIFICAR SI UN ARCHIVO COINCIDE CON LA CATEGORÍA
    const archivoCoincideConCategoria = (archivo, categoria) => {
      if (!categoria || !archivo.path_file) return false;
      
      const rutaLower = archivo.path_file.toLowerCase();
      const patrones = categoriasToPathPatterns[categoria] || [];
      
      return patrones.some(patron => {
        return rutaLower.includes(patron.toLowerCase());
      });
    };

    // Variable reactiva específica para el contador (FORZAR REACTIVIDAD)
    const contadorArchivos = ref(0);

    // Variable para controlar si mostrar todos los archivos
    const mostrarTodos = ref(false);

    // FUNCIONES PARA INFORMACIÓN CATASTRAL
    const getTipoInfoCatastralFromPath = (pathFile) => {
      if (!pathFile) return 'N/A';
      
      const normalizedPath = pathFile.replace(/\\/g, '/');
      
      const patterns = [
        { pattern: /\/03_info_catas\/01_r1_r2\//i, tipo: 'R1 & R2' },
        { pattern: /\/03_info_catas\/02_gdb\//i, tipo: 'GDB' },
        { pattern: /\/03_info_catas\/03_tab_terr_constr\//i, tipo: 'Tablas Terreno & Construcción' },
        { pattern: /\/03_info_catas\/04_estu_zhf_zhg\//i, tipo: 'Estudio ZHF & ZHG' }
      ];
      
      for (const { pattern, tipo } of patterns) {
        if (pattern.test(normalizedPath)) {
          return tipo;
        }
      }
      
      return 'N/A';
    };

    // FUNCIÓN PARA OBTENER EL CENTRO POBLADO YA SELECCIONADO
    const getCentroPobladoSeleccionado = () => {
      if (!formData.value.cod_centro_poblado) return null;
      return formData.value.cod_centro_poblado;
    };

    // FUNCIÓN PARA OBTENER NOMBRE DEL CENTRO POBLADO
    const getCentroPobladoFromCod = (cod) => {
      if (!cod) return '';
      const centro = centrosPoblados.value.find(c => c.cod_centro_poblado === cod);
      return centro ? centro.nom_centro_poblado : cod;
    };

    // FUNCIÓN PARA OBTENER LA CLASIFICACIÓN SELECCIONADA
    const getClasificacionSeleccionada = () => {
      if (!formData.value.cod_clasificacion) return null;
      
      const clasificacion = clasificaciones.value.find(c => 
        c.cod_clasificacion == formData.value.cod_clasificacion
      );
      
      return clasificacion;
    };

    // LIMPIAR SOLO FILTROS NUEVOS (no tocar los existentes)
    const limpiarFiltrosArchivos = () => {
      filtroTipoInfoCatastral.value = '';
      archivoSearchTerm.value = '';
    };

    // Computed para patrones de categoría disponibles en archivos
    const patronesDisponibles = computed(() => {
      const patrones = new Set();
      
      archivosDisponibles.value.forEach(archivo => {
        if (archivo.path_file) {
          const rutaLower = archivo.path_file.toLowerCase();
          
          Object.entries(categoriasToPathPatterns).forEach(([categoria, patronesCategoria]) => {
            patronesCategoria.forEach(patron => {
              if (rutaLower.includes(patron.toLowerCase())) {
                patrones.add(categoria);
              }
            });
          });
        }
      });
      
      return Array.from(patrones).sort();
    });

    // COMPUTED archivosFiltrados CORREGIDO - USAR FILTROS EXISTENTES
    const archivosFiltrados = computed(() => {
      let result = [...archivosDisponibles.value];
      
      console.log(`🔄 Filtrando archivos...`);
      console.log(`📦 Archivos disponibles: ${result.length}`);
      
      // 1. FILTRO POR CATEGORÍA DEL INSUMO (filtro existente)
      if (filtros.value.insumo && !mostrarTodos.value) {
        const categoria = getCategoriaInsumoSeleccionado();
        console.log(`🏷️ Categoría detectada: ${categoria}`);
        
        if (categoria) {
          const archivosFiltradosTemp = result.filter(archivo => 
            archivoCoincideConCategoria(archivo, categoria)
          );
          
          console.log(`📊 Archivos filtrados por categoría: ${archivosFiltradosTemp.length}`);
          result = archivosFiltradosTemp;
        }
      }
      
      // 2. FILTRO POR CLASIFICACIÓN SELECCIONADA (para Cartografía Básica)
      const clasificacionSeleccionada = getClasificacionSeleccionada();
      if (clasificacionSeleccionada) {
        console.log(`🎯 Clasificación seleccionada: ${clasificacionSeleccionada.nombre}`);
        
        // Para cartografía básica, filtrar por el tipo específico en la ruta
        if (clasificacionSeleccionada.nombre.toLowerCase().includes('vectorial')) {
          const antesCount = result.length;
          result = result.filter(a => {
            if (!a.path_file) return false;
            const ruta = a.path_file.toLowerCase();
            return ruta.includes('/02_vect/') || 
                   ruta.includes('\\02_vect\\') || 
                   ruta.includes('02_vect') ||
                   ruta.includes('vect') ||
                   ruta.includes('vector');
          });
          console.log(`🔍 Filtrado por Vectorial: ${antesCount} → ${result.length} archivos`);
        } 
        else if (clasificacionSeleccionada.nombre.toLowerCase().includes('ortoimagen') || 
                 clasificacionSeleccionada.nombre.toLowerCase().includes('ortofoto')) {
          result = result.filter(a => {
            if (!a.path_file) return false;
            const ruta = a.path_file.toLowerCase();
            return ruta.includes('01_rast\\01_orto') || 
                   ruta.includes('01_rast/01_orto') ||
                   ruta.includes('orto') ||
                   ruta.includes('ortofoto');
          });
          console.log(`🔍 Filtrado por Ortoimagen: ${result.length} archivos`);
        }
        else if (clasificacionSeleccionada.nombre.toLowerCase().includes('modelo') || 
                 clasificacionSeleccionada.nombre.toLowerCase().includes('terreno')) {
          result = result.filter(a => {
            if (!a.path_file) return false;
            const ruta = a.path_file.toLowerCase();
            return ruta.includes('01_rast\\02_dtm') || 
                   ruta.includes('01_rast\\02_mtd') ||
                   ruta.includes('01_rast/02_dtm') || 
                   ruta.includes('01_rast/02_mtd') ||
                   ruta.includes('dtm') ||
                   ruta.includes('mtd') ||
                   ruta.includes('modelo');
          });
          console.log(`🔍 Filtrado por Modelo Digital: ${result.length} archivos`);
        }
      }
      
      // 3. FILTRO POR CENTRO POBLADO YA SELECCIONADO (si aplica)
      const centroPobladoSeleccionado = getCentroPobladoSeleccionado();
      if (centroPobladoSeleccionado && mostrarCentroPoblado.value) {
        console.log(`🏘️ Centro poblado seleccionado: ${centroPobladoSeleccionado}`);
        
        // Extraer últimos 3 dígitos del código del centro poblado
        const codigoCorto = centroPobladoSeleccionado.slice(-3);
        
        result = result.filter(a => {
          if (!a.path_file) return false;
          return a.path_file.includes(codigoCorto);
        });
        
        console.log(`🔍 Filtrado por centro poblado: ${result.length} archivos`);
      }
      
      // 4. FILTRO POR TIPO DE INFORMACIÓN CATASTRAL (solo para Info Catastral)
      if (mostrarFiltrosInfoCatastral.value && filtroTipoInfoCatastral.value) {
        result = result.filter(a => {
          if (!a.path_file) return false;
          const tipo = getTipoInfoCatastralFromPath(a.path_file);
          return tipo === filtroTipoInfoCatastral.value;
        });
        
        console.log(`🔍 Filtrado por tipo catastral ${filtroTipoInfoCatastral.value}: ${result.length} archivos`);
      }
      
      // 5. FILTRO POR TÉRMINO DE BÚSQUEDA (existente)
      if (archivoSearchTerm.value.trim()) {
        const searchTerm = archivoSearchTerm.value.toLowerCase();
        result = result.filter(archivo =>
          archivo.nombre_insumo?.toLowerCase().includes(searchTerm)
        );
        console.log(`🔎 Filtrado por búsqueda "${searchTerm}": ${result.length} archivos`);
      }

      // 6. ✅ FILTRO PARA EXCLUIR ARCHIVOS YA USADOS EN OTROS DETALLES
      if (rutasEnUso.value.length > 0) {
        const antesDelFiltro = result.length;

        // Obtener el ID del detalle que estamos editando (si aplica)
        const detalleEditandoId = isEditing.value ? parseInt(route.params.id) : null;

        result = result.filter(archivo => {
          if (!archivo.path_file) return true;

          // Normalizar la ruta del archivo para comparación
          const rutaArchivoNormalizada = archivo.path_file.replace(/\\/g, '/').toLowerCase().trim();

          // Verificar si esta ruta ya está en uso
          const rutaEnUso = rutasEnUso.value.find(r => r.ruta === rutaArchivoNormalizada);

          if (!rutaEnUso) {
            // La ruta NO está en uso, incluir el archivo
            return true;
          }

          // La ruta está en uso, pero verificar si es del detalle que estamos editando
          if (detalleEditandoId && rutaEnUso.cod_detalle === detalleEditandoId) {
            // Es el archivo del detalle que estamos editando, incluirlo
            console.log(`📝 Archivo permitido (es el del detalle en edición): ${archivo.nombre_insumo}`);
            return true;
          }

          // También verificar si la ruta coincide con la ruta actual del formulario (modo edición)
          if (isEditing.value && formData.value.ruta_archivo) {
            const rutaFormNormalizada = formData.value.ruta_archivo.replace(/\\/g, '/').toLowerCase().trim();
            if (rutaArchivoNormalizada === rutaFormNormalizada) {
              console.log(`📝 Archivo permitido (es la ruta actual en edición): ${archivo.nombre_insumo}`);
              return true;
            }
          }

          // La ruta está en uso por otro detalle, excluir
          console.log(`🚫 Archivo excluido (ya usado en detalle ${rutaEnUso.cod_detalle}): ${archivo.nombre_insumo}`);
          return false;
        });

        const excluidos = antesDelFiltro - result.length;
        if (excluidos > 0) {
          console.log(`🚫 Filtrado por rutas en uso: ${antesDelFiltro} → ${result.length} archivos (${excluidos} excluidos)`);
        }
      }

      console.log(`✅ Total archivos finales: ${result.length}`);
      
      // Actualizar contador
      const nuevoContador = result.length;
      if (contadorArchivos.value !== nuevoContador) {
        contadorArchivos.value = nuevoContador;
      }
      
      return result;
    });

    // FUNCIÓN PARA MOSTRAR TODOS LOS ARCHIVOS
    const mostrarTodosLosArchivos = () => {
      mostrarTodos.value = true;
      contadorArchivos.value = archivosDisponibles.value.length;
      console.log('🔍 Mostrando todos los archivos disponibles (sin filtrar por categoría)');
    };

    // ✅ NUEVAS FUNCIONES HELPER

    // Obtener fecha actual en formato YYYY-MM-DD
    const obtenerFechaActual = () => {
      const hoy = new Date();
      return hoy.toISOString().split('T')[0];
    };

    // Buscar entidad "Instituto Geográfico Agustín Codazzi" (CORREGIDO CON DATOS REALES)
    const obtenerCodigoIGAC = () => {
      console.log('🔍 Buscando entidad IGAC...');
      console.log('📋 Entidades disponibles:', entidades.value.length);
      
      if (entidades.value.length === 0) {
        console.log('❌ No hay entidades cargadas');
        return '';
      }
      
      // Buscar por código IGAC directamente (según la BD)
      const igacPorCodigo = entidades.value.find(e => e.cod_entidad === 'IGAC');
      if (igacPorCodigo) {
        console.log('✅ IGAC encontrado por código:', igacPorCodigo.nom_entidad, 'Código:', igacPorCodigo.cod_entidad);
        return igacPorCodigo.cod_entidad;
      }
      
      // Buscar por nombre como respaldo
      const igacPorNombre = entidades.value.find(e => {
        const nombre = e.nom_entidad.toLowerCase();
        console.log('🔎 Revisando entidad:', nombre);
        return nombre.includes('instituto geográfico') && nombre.includes('agustín codazzi');
      });
      
      if (igacPorNombre) {
        console.log('✅ IGAC encontrado por nombre:', igacPorNombre.nom_entidad, 'Código:', igacPorNombre.cod_entidad);
        return igacPorNombre.cod_entidad;
      } else {
        console.log('❌ IGAC NO encontrado. Entidades disponibles:');
        entidades.value.forEach(e => console.log(`   - ${e.cod_entidad}: ${e.nom_entidad}`));
        return '';
      }
    };

    // Buscar formato específico (CORREGIDO CON DATOS REALES)
    const obtenerCodigoFormato = (nombreFormato) => {
      console.log(`🔍 Buscando formato: ${nombreFormato}`);
      console.log('📋 Formatos disponibles:', formatos.value.length);
      
      if (formatos.value.length === 0) {
        console.log('❌ No hay formatos cargados');
        return '';
      }
      
      // Buscar exactamente por cod_formato_tipo (según la BD)
      const formato = formatos.value.find(f => {
        const codigo = f.cod_formato_tipo;
        console.log('🔎 Revisando formato:', codigo);
        return codigo === nombreFormato; // Comparación exacta
      });
      
      if (formato) {
        console.log('✅ Formato encontrado:', formato.cod_formato_tipo);
        return formato.cod_formato_tipo;
      } else {
        console.log(`❌ Formato ${nombreFormato} NO encontrado. Formatos disponibles:`);
        formatos.value.slice(0, 10).forEach(f => console.log(`   - ${f.cod_formato_tipo}`));
        if (formatos.value.length > 10) {
          console.log(`   ... y ${formatos.value.length - 10} más`);
        }
        return '';
      }
    };

    // ✅ FUNCIÓN PRINCIPAL PARA APLICAR VALORES POR DEFECTO (CORREGIDA PARA DEBUG)
    const aplicarValoresPorDefecto = async () => {
      if (!tipoInsumoSeleccionado.value) {
        console.log('❌ No hay tipo de insumo seleccionado');
        return;
      }

      console.log(`🔧 APLICANDO VALORES POR DEFECTO para: ${tipoInsumoSeleccionado.value.categoria_nombre}`);
      console.log('🔍 Tipo de insumo detectado:', tipoInsumoSeleccionado.value.tipo_insumo);
      console.log('🔍 Verificando tipos detectados:', {
        esCartografiaBasica: esCartografiaBasica.value,
        esEstudioAgrologico: esEstudioAgrologico.value,
        esInformacionCatastral: esInformacionCatastral.value,
        esDeslinde: esDeslinde.value,
        esInsumosFuentesSecundarias: esInsumosFuentesSecundarias.value,
        esSaldoConservacion: esSaldoConservacion.value
      });
      
      console.log('📊 Estado ANTES de aplicar valores:', {
        entidad: formData.value.cod_entidad,
        estado: formData.value.estado,
        formato: formData.value.formato_tipo,
        zona: formData.value.zona,
        cubrimiento: formData.value.cubrimiento_valor
      });

      // ✅ ESPERAR A QUE ÁREA ESTÉ CARGADA SI ES NECESARIA
      if (mostrarCubrimiento.value && filtros.value.municipio && !areaMunicipio.value) {
        console.log('🔄 Cargando área del municipio antes de aplicar valores...');
        await cargarAreaMunicipio(filtros.value.municipio);
      }

      // 1. CARTOGRAFÍA BÁSICA
      if (esCartografiaBasica.value) {
        console.log('🎯 Aplicando valores para Cartografía Básica');
        
        const codigoIGAC = obtenerCodigoIGAC();
        const codigoGDB = obtenerCodigoFormato('GDB');
        
        formData.value.cod_entidad = codigoIGAC;
        formData.value.estado = 'OFICIALIZADO';
        formData.value.formato_tipo = codigoGDB;
        
        console.log('✅ Valores establecidos para Cartografía Básica:', {
          entidad: codigoIGAC,
          estado: 'OFICIALIZADO',
          formato: codigoGDB
        });
        
        // Cubrimiento al 100% del área del municipio
        if (areaMunicipio.value) {
          const areaNumerico = parseFloat(areaMunicipio.value.replace(',', '.') || '0');
          formData.value.cubrimiento_valor = areaNumerico.toString();
          console.log(`📊 Cubrimiento establecido: ${areaNumerico} Ha`);
        }
        
        // Fecha de disposición actual
        formData.value.fecha_disposicion = obtenerFechaActual();
      }

      // 2. ESTUDIO AGROLÓG ICO ✅ CON ZONA RURAL
      else if (esEstudioAgrologico.value) {
        console.log('🎯 Aplicando valores para Estudio Agrológ ico');
        
        // ✅ ZONA RURAL POR DEFECTO
        console.log('🌾 Estableciendo zona RURAL...');
        filtros.value.zona = 'RURAL';
        formData.value.zona = 'RURAL';
        console.log('✅ Zona establecida:', filtros.value.zona, formData.value.zona);
        
        const codigoIGAC = obtenerCodigoIGAC();
        const codigoGDB = obtenerCodigoFormato('GDB');
        
        console.log('🔧 Estableciendo valores principales...');
        formData.value.cod_entidad = codigoIGAC;
        formData.value.estado = 'OFICIALIZADO';
        formData.value.formato_tipo = codigoGDB;
        
        console.log('✅ Valores establecidos para Estudio Agrológ ico:', {
          zona: formData.value.zona,
          entidad: codigoIGAC,
          estado: 'OFICIALIZADO',
          formato: codigoGDB
        });
        
        // Cubrimiento al 100% del área del municipio
        if (areaMunicipio.value) {
          const areaNumerico = parseFloat(areaMunicipio.value.replace(',', '.') || '0');
          formData.value.cubrimiento_valor = areaNumerico.toString();
          console.log(`📊 Cubrimiento establecido: ${areaNumerico} Ha`);
        } else {
          console.log('⚠️ No hay área del municipio disponible');
        }
      }

      // 3. INFORMACIÓN CATASTRAL
      else if (esInformacionCatastral.value) {
        console.log('🎯 Aplicando valores para Información Catastral');
        
        const codigoIGAC = obtenerCodigoIGAC();
        const codigoGDB = obtenerCodigoFormato('GDB');
        
        formData.value.cod_entidad = codigoIGAC;
        formData.value.formato_tipo = codigoGDB;
        
        console.log('✅ Valores establecidos para Información Catastral:', {
          entidad: codigoIGAC,
          formato: codigoGDB
        });
        
        // Limpiar campos que no se usan
        formData.value.cubrimiento_valor = '';
        formData.value.escala = '';
        formData.value.area_municipio = '';
        formData.value.porcentaje_cubrimiento = '';
      }

      // 4. DESLINDE
      else if (esDeslinde.value) {
        console.log('🎯 Aplicando valores para Deslinde');
        
        const codigoIGAC = obtenerCodigoIGAC();
        const codigoSHP = obtenerCodigoFormato('SHP');
        
        formData.value.cod_entidad = codigoIGAC;
        formData.value.formato_tipo = codigoSHP;
        
        console.log('✅ Valores establecidos para Deslinde:', {
          entidad: codigoIGAC,
          formato: codigoSHP
        });
        
        // Cubrimiento al 100% del área del municipio
        if (areaMunicipio.value) {
          const areaNumerico = parseFloat(areaMunicipio.value.replace(',', '.') || '0');
          formData.value.cubrimiento_valor = areaNumerico.toString();
          console.log(`📊 Cubrimiento establecido: ${areaNumerico} Ha`);
        }
      }

      // 5. INSUMOS FUENTES SECUNDARIAS
      else if (esInsumosFuentesSecundarias.value) {
        console.log('🎯 Aplicando valores para Insumos Fuentes Secundarias');
        
        const codigoGDB = obtenerCodigoFormato('GDB');
        
        formData.value.estado = 'OFICIALIZADO';
        formData.value.formato_tipo = codigoGDB;
        
        console.log('✅ Valores establecidos para Insumos Fuentes Secundarias:', {
          estado: 'OFICIALIZADO',
          formato: codigoGDB
        });
        
        // Limpiar campos que no se usan
        formData.value.escala = '';
        formData.value.cubrimiento_valor = '';
        formData.value.area_municipio = '';
        formData.value.porcentaje_cubrimiento = '';
      }

      // 6. SALDO CONSERVACIÓN ✅ CORREGIDO
      else if (esSaldoConservacion.value) {
        console.log('🎯 Aplicando valores para Saldo Conservación');
        
        const codigoIGAC = obtenerCodigoIGAC();
        
        formData.value.cod_entidad = codigoIGAC;
        
        console.log('✅ Valores establecidos para Saldo Conservación:', {
          entidad: codigoIGAC
        });
        
        // Limpiar campos que no se usan
        formData.value.area_municipio = '';
        formData.value.cubrimiento_valor = '';
        formData.value.escala = '';
        formData.value.porcentaje_cubrimiento = '';
      }

      // ❌ SI NINGUNO COINCIDE
      else {
        console.log('❌ NINGÚN TIPO COINCIDE - NO SE APLICARÁN VALORES');
        console.log('🔍 Tipo actual:', tipoInsumoSeleccionado.value);
        return;
      }

      // ✅ FORZAR ACTUALIZACIÓN DE CAMPOS DE BÚSQUEDA PARA LA UI
      console.log('🔄 Actualizando campos de búsqueda para la UI...');
      
      if (formData.value.cod_entidad) {
        const entidadEncontrada = entidades.value.find(e => e.cod_entidad === formData.value.cod_entidad);
        if (entidadEncontrada) {
          entidadSearch.value = entidadEncontrada.nom_entidad;
          console.log(`🏢 Campo de búsqueda entidad actualizado: ${entidadEncontrada.nom_entidad}`);
        } else {
          console.log(`❌ No se encontró entidad con código: ${formData.value.cod_entidad}`);
        }
      }

      if (formData.value.formato_tipo) {
        formatoSearch.value = formData.value.formato_tipo;
        console.log(`📄 Campo de búsqueda formato actualizado: ${formData.value.formato_tipo}`);
      }

      // ✅ RECALCULAR PORCENTAJE SI HAY CUBRIMIENTO
      if (formData.value.cubrimiento_valor) {
        formData.value.porcentaje_cubrimiento = porcentajeCubrimientoCalculado.value.toString();
        console.log(`📈 Porcentaje calculado: ${porcentajeCubrimientoCalculado.value}%`);
      }

      console.log('📊 Estado DESPUÉS de aplicar valores:', {
        zona: formData.value.zona,
        entidad: formData.value.cod_entidad,
        entidadSearch: entidadSearch.value,
        estado: formData.value.estado,
        formato: formData.value.formato_tipo,
        formatoSearch: formatoSearch.value,
        cubrimiento: formData.value.cubrimiento_valor,
        porcentaje: formData.value.porcentaje_cubrimiento
      });

      console.log('✅ VALORES POR DEFECTO APLICADOS EXITOSAMENTE');
    };

    // ✅ WATCHER PRINCIPAL PARA EL INSUMO - EJECUTA INMEDIATAMENTE
    watch(() => filtros.value.insumo, async (newInsumoId, oldInsumoId) => {
      console.log(`🔄 WATCHER INSUMO EJECUTÁNDOSE: ${oldInsumoId} → ${newInsumoId}`);
      
      if (!newInsumoId) {
        console.log('❌ Sin insumo seleccionado, limpiando formulario');
        // Limpiar formulario
        formData.value.cod_entidad = '';
        formData.value.estado = '';
        formData.value.formato_tipo = '';
        formData.value.cubrimiento_valor = '';
        formData.value.zona = '';
        filtros.value.zona = '';
        entidadSearch.value = '';
        formatoSearch.value = '';
        return;
      }

      console.log(`🎯 INSUMO SELECCIONADO: ${newInsumoId}`);
      
      // ✅ ESPERAR A QUE SE ACTUALICEN LOS COMPUTED
      await nextTick();
      
      if (!tipoInsumoSeleccionado.value) {
        console.log('⏳ Esperando a que se detecte el tipo de insumo...');
        return;
      }
      
      console.log(`📋 TIPO DETECTADO: ${tipoInsumoSeleccionado.value.categoria_nombre}`);
      
      // ✅ APLICAR VALORES INMEDIATAMENTE
      try {
        await aplicarValoresPorDefecto();
        console.log('✅ VALORES APLICADOS DESDE WATCHER PRINCIPAL');
      } catch (error) {
        console.error('❌ Error aplicando valores desde watcher:', error);
      }
    }, { immediate: false });

    // ✅ WATCHER DE RESPALDO PARA CUANDO SE CARGAN ENTIDADES/FORMATOS
    watch([() => entidades.value.length, () => formatos.value.length], async ([entidadesLength, formatosLength]) => {
      console.log(`🔄 WATCHER RESPALDO: Entidades=${entidadesLength}, Formatos=${formatosLength}`);
      
      if (entidadesLength > 0 && formatosLength > 0 && filtros.value.insumo && tipoInsumoSeleccionado.value) {
        console.log('🔄 Intentando reaplicar valores (entidades/formatos listos)');
        await nextTick();
        try {
          await aplicarValoresPorDefecto();
          console.log('✅ VALORES REAPLICADOS DESDE WATCHER RESPALDO');
        } catch (error) {
          console.error('❌ Error reaplicando valores:', error);
        }
      }
    });

    // FUNCIÓN PARA CARGAR ARCHIVOS CON ACTUALIZACIÓN DE CONTADOR
const cargarArchivosDisponibles = async () => {
  console.log(`🚀 INICIANDO cargarArchivosDisponibles()`);
  
  if (!filtros.value.municipio) {
    console.log('❌ No hay municipio, saliendo');
    archivosDisponibles.value = [];
    contadorArchivos.value = 0;
    return;
  }

  try {
    archivosLoading.value = true;
    archivosError.value = null;
    mostrarTodos.value = false;
    
    console.log(`🔍 CARGANDO ARCHIVOS PARA MUNICIPIO: ${filtros.value.municipio}`);
    
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_URL}/preoperacion/archivos-pre/por_municipio/?municipio_id=${filtros.value.municipio}`, {
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      if (response.status === 404) {
        console.log('📂 No se encontraron archivos (404)');
        archivosDisponibles.value = [];
        contadorArchivos.value = 0;
        return;
      } else {
        throw new Error(`Error HTTP: ${response.status}`);
      }
    }
    
    const archivos = await response.json();
    const archivosArray = Array.isArray(archivos) ? archivos : [];
    
    console.log(`✅ ARCHIVOS CARGADOS: ${archivosArray.length}`);
    
    archivosDisponibles.value = archivosArray;
    contadorArchivos.value = archivosArray.length;

    // ✅ CARGAR RUTAS YA USADAS EN OTROS DETALLES DEL MISMO MUNICIPIO
    await cargarRutasEnUso();

    // ✅ SI ESTAMOS EDITANDO Y HAY ARCHIVO GUARDADO, BUSCARLO
    if (isEditing.value && formData.value.ruta_archivo) {
      buscarArchivoEnLista(formData.value.ruta_archivo);
    }

  } catch (error) {
    console.error('❌ Error cargando archivos:', error);
    archivosError.value = `Error: ${error.message}`;
    archivosDisponibles.value = [];
    contadorArchivos.value = 0;
  } finally {
    archivosLoading.value = false;
  }
};

// ✅ FUNCIÓN PARA CARGAR RUTAS DE ARCHIVOS YA USADAS EN OTROS DETALLES
const cargarRutasEnUso = async () => {
  try {
    if (!filtros.value.municipio) {
      rutasEnUso.value = [];
      return;
    }

    console.log('🔍 Cargando rutas ya usadas en detalles existentes...');

    const token = localStorage.getItem('token');

    // Obtener todos los detalles que tienen ruta_archivo
    // Usamos el endpoint de detalles filtrado por los insumos del municipio
    const insumosResponse = await fetch(
      `${API_URL}/preoperacion/municipios/${filtros.value.municipio}/insumos/`,
      {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (!insumosResponse.ok) {
      console.log('⚠️ No se pudieron cargar insumos para verificar rutas');
      rutasEnUso.value = [];
      return;
    }

    const insumos = await insumosResponse.json();
    const insumosArray = Array.isArray(insumos) ? insumos : [];

    if (insumosArray.length === 0) {
      rutasEnUso.value = [];
      return;
    }

    // Obtener todas las clasificaciones de estos insumos
    const clasificacionesPromises = insumosArray.map(insumo =>
      fetch(`${API_URL}/preoperacion/insumos/${insumo.cod_insumo}/clasificaciones/`, {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        }
      }).then(res => res.ok ? res.json() : [])
    );

    const clasificacionesResponses = await Promise.all(clasificacionesPromises);
    const todasClasificaciones = clasificacionesResponses.flat();

    if (todasClasificaciones.length === 0) {
      rutasEnUso.value = [];
      return;
    }

    // Obtener todos los detalles de estas clasificaciones
    const detallesPromises = todasClasificaciones.map(clasificacion =>
      fetch(`${API_URL}/preoperacion/detalles-insumo/?cod_clasificacion=${clasificacion.cod_clasificacion}`, {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        }
      }).then(res => res.ok ? res.json() : { results: [] })
    );

    const detallesResponses = await Promise.all(detallesPromises);

    // Extraer rutas de archivos usadas
    const rutas = [];
    detallesResponses.forEach(response => {
      const detalles = response.results || response || [];
      const detallesArray = Array.isArray(detalles) ? detalles : [];

      detallesArray.forEach(detalle => {
        if (detalle.ruta_archivo && detalle.ruta_archivo.trim() !== '') {
          // Normalizar la ruta para comparación
          const rutaNormalizada = detalle.ruta_archivo.replace(/\\/g, '/').toLowerCase().trim();
          rutas.push({
            ruta: rutaNormalizada,
            rutaOriginal: detalle.ruta_archivo,
            cod_detalle: detalle.cod_detalle
          });
        }
      });
    });

    rutasEnUso.value = rutas;
    console.log(`✅ Rutas en uso cargadas: ${rutas.length}`);
    console.log('📋 Rutas en uso:', rutas.map(r => r.rutaOriginal.substring(0, 50) + '...'));

  } catch (error) {
    console.error('❌ Error al cargar rutas en uso:', error);
    rutasEnUso.value = [];
  }
};

// ✅ FUNCIÓN SIMPLE PARA BUSCAR ARCHIVO
// ✅ FUNCIÓN MEJORADA PARA BUSCAR ARCHIVO
const buscarArchivoEnLista = (rutaBuscada) => {
  if (!rutaBuscada) {
    console.log('❌ No hay ruta a buscar');
    return false;
  }
  
  if (archivosDisponibles.value.length === 0) {
    console.log('❌ No hay archivos disponibles aún');
    return false;
  }
  
  console.log(`🔍 BUSCANDO: "${rutaBuscada}" en ${archivosDisponibles.value.length} archivos`);
  
  // Buscar por nombre de archivo
  const nombreBuscado = rutaBuscada.split(/[/\\]/).pop()?.toLowerCase();
  console.log(`🔍 Nombre buscado: "${nombreBuscado}"`);
  
  const encontrado = archivosDisponibles.value.find(archivo => {
    if (!archivo.path_file) return false;
    const nombreArchivo = archivo.path_file.split(/[/\\]/).pop()?.toLowerCase();
    return nombreArchivo === nombreBuscado;
  });
  
  if (encontrado) {
    console.log(`✅ ARCHIVO ENCONTRADO: ${encontrado.nombre_insumo}`);
    console.log(`📂 Cambiando a modo automático...`);
    
    archivoSelectionMode.value = 'automatico';
    selectedArchivoId.value = encontrado.id_lista_archivo.toString();
    archivoSeleccionado.value = encontrado;
    formData.value.ruta_archivo = encontrado.path_file;
    
    console.log(`🎯 Archivo seleccionado: ID=${selectedArchivoId.value}`);
    return true;
  } else {
    console.log(`❌ NO ENCONTRADO en automático - mantener manual`);
    console.log(`🔍 Primeros 3 archivos disponibles:`);
    archivosDisponibles.value.slice(0, 3).forEach((archivo, i) => {
      const nombre = archivo.path_file?.split(/[/\\]/).pop() || 'Sin nombre';
      console.log(`   ${i + 1}: "${nombre}"`);
    });
    return false;
  }
};


    // FUNCIÓN PARA MANEJAR SELECCIÓN DE ARCHIVO
    const onArchivoSelect = () => {
      if (!selectedArchivoId.value) {
        archivoSeleccionado.value = null;
        formData.value.ruta_archivo = '';
        return;
      }
      
      const archivo = archivosDisponibles.value.find(a => a.id_lista_archivo == selectedArchivoId.value);
      if (archivo) {
        archivoSeleccionado.value = archivo;
        formData.value.ruta_archivo = archivo.path_file;
        console.log('🔍 Archivo seleccionado:', archivo.nombre_insumo);
      }
    };

    // FUNCIÓN PARA CAMBIAR MODO DE SELECCIÓN
    const onSelectionModeChange = () => {
      selectedArchivoId.value = '';
      archivoSeleccionado.value = null;
      
      if (archivoSelectionMode.value === 'automatico') {
        formData.value.ruta_archivo = '';
      }
    };

    // FUNCIÓN PARA LIMPIAR SELECCIÓN DE ARCHIVO
    const limpiarSeleccionArchivo = () => {
      selectedArchivoId.value = '';
      archivoSeleccionado.value = null;
      formData.value.ruta_archivo = '';
      archivoSearchTerm.value = '';
    };

    // FUNCIÓN PARA OBTENER CATEGORÍA DE UN ARCHIVO ESPECÍFICO
    const getCategoriaDelArchivo = (archivo) => {
      if (!archivo || !archivo.path_file) return null;
      
      const rutaLower = archivo.path_file.toLowerCase();
      
      for (const [categoria, patrones] of Object.entries(categoriasToPathPatterns)) {
        for (const patron of patrones) {
          if (rutaLower.includes(patron.toLowerCase())) {
            return categoria;
          }
        }
      }
      
      return null;
    };

    // ✅ CARGAR ÁREA DEL MUNICIPIO
    const cargarAreaMunicipio = async (municipioId) => {
      if (!municipioId) {
        areaMunicipio.value = '';
        formData.value.area_municipio = '';
        return;
      }

      try {
        cargandoAreaMunicipio.value = true;
        console.log(`🗺️ Cargando área del municipio ${municipioId}...`);
        
        const municipio = await getMunicipioById(municipioId);
        
        if (municipio && municipio.area) {
          areaMunicipio.value = municipio.area;
          formData.value.area_municipio = municipio.area;
          console.log(`✅ Área del municipio cargada: ${municipio.area} Ha`);
        } else {
          console.log(`⚠️ No se encontró área para el municipio ${municipioId}`);
          areaMunicipio.value = '';
          formData.value.area_municipio = '';
        }
      } catch (error) {
        console.error('❌ Error al cargar área del municipio:', error);
        areaMunicipio.value = '';
        formData.value.area_municipio = '';
        mensaje.value = {
          texto: 'Error al cargar el área del municipio. El cálculo de porcentaje no estará disponible.',
          tipo: 'error'
        };
      } finally {
        cargandoAreaMunicipio.value = false;
      }
    };

    // Manejar cambio en cubrimiento para recalcular porcentaje
    const onCubrimientoChange = () => {
      console.log(`📊 Cubrimiento cambiado a: ${formData.value.cubrimiento_valor}`);
      console.log(`📊 Porcentaje calculado: ${porcentajeCubrimientoCalculado.value}%`);
      
      // Actualizar el campo en formData para guardarlo en BD
      formData.value.porcentaje_cubrimiento = porcentajeCubrimientoCalculado.value.toString();
    };

    // Watcher explícito para forzar reactividad del filtrado CON CONTADOR
    watch([() => filtros.value.insumo, () => mostrarTodos.value, () => archivoSearchTerm.value], 
      ([nuevoInsumo, nuevoMostrarTodos, nuevaBusqueda]) => {
        console.log(`🔄 WATCHER: Cambio detectado en filtros`);
        console.log(`   Insumo: ${nuevoInsumo}`);
        console.log(`   Mostrar todos: ${nuevoMostrarTodos}`);
        console.log(`   Búsqueda: "${nuevaBusqueda}"`);
        
        const archivosFiltradosLength = archivosFiltrados.value.length;
        contadorArchivos.value = archivosFiltradosLength;
        console.log(`   Archivos resultantes: ${archivosFiltradosLength}`);
      }
    );

    // Limpiar solo filtros nuevos al cambiar insumo
    watch(() => filtros.value.insumo, () => {
      filtroTipoInfoCatastral.value = '';
      archivoSearchTerm.value = '';
      mostrarTodos.value = false;
      limpiarSeleccionArchivo();
    });

    // ✅ WATCHER PARA MUNICIPIO
    watch(() => filtros.value.municipio, async (newMunicipioId) => {
      console.log(`🔄 WATCHER MUNICIPIO: ${newMunicipioId}`);
      
      // Limpiar selecciones
      limpiarSeleccionArchivo();
      mostrarTodos.value = false;
      contadorArchivos.value = 0;
      filtroTipoInfoCatastral.value = '';
      archivoSearchTerm.value = '';
      
      if (!newMunicipioId) {
        areaMunicipio.value = '';
        formData.value.area_municipio = '';
        formData.value.porcentaje_cubrimiento = '';
        return;
      }
      
      // Cargar área del municipio
      await cargarAreaMunicipio(newMunicipioId);
      
      // Si ya hay insumo seleccionado, reaplicar valores
      if (filtros.value.insumo && tipoInsumoSeleccionado.value) {
        console.log('🔄 Reaplicando valores tras cambio de municipio');
        await nextTick();
        try {
          await aplicarValoresPorDefecto();
        } catch (error) {
          console.error('❌ Error reaplicando valores:', error);
        }
      }
      
      // Cargar archivos
      if (archivoSelectionMode.value === 'automatico') {
        cargarArchivosDisponibles();
      }
    });

    // Actualizar porcentaje cuando cambie cubrimiento o área
    watch([() => formData.value.cubrimiento_valor, () => areaMunicipio.value], () => {
      formData.value.porcentaje_cubrimiento = porcentajeCubrimientoCalculado.value.toString();
    });

    // ✅ Función para manejar cambios en zona (MEJORADA PARA DEBUG)
    function onZonaChange() {
      const zonaAnterior = formData.value.zona;
      formData.value.cod_centro_poblado = '';
      formData.value.zona = filtros.value.zona;
      
      console.log(`🔄 CAMBIO DE ZONA: "${zonaAnterior}" → "${filtros.value.zona}"`);
      console.log(`🔍 DEBUG onZonaChange - Estado actual:`);
      console.log(`   - Zona en filtros: "${filtros.value.zona}"`);
      console.log(`   - Zona en formData: "${formData.value.zona}"`);
      console.log(`   - Es Cartografía Básica: ${esCartografiaBasica.value}`);
      console.log(`   - Municipio: ${filtros.value.municipio}`);
      console.log(`   - Mostrar Centro Poblado: ${mostrarCentroPoblado.value}`);
      
      if (filtros.value.zona !== 'CENTROS POBLADOS') {
        console.log(`❌ Zona no es CENTROS POBLADOS, limpiando centros poblados`);
        centrosPoblados.value = [];
      } else {
        // Solo cargar centros poblados si es Cartografía Básica y zona es CENTROS POBLADOS
        const esCartografia = tipoInsumoSeleccionado.value?.categoria_nombre === 'Cartografia Basica';
        console.log(`🔍 DEBUG CAMBIO ZONA a CENTROS POBLADOS:`);
        console.log(`   - ¿Es Cartografía Básica?: ${esCartografia}`);
        console.log(`   - Municipio: ${filtros.value.municipio}`);
        console.log(`   - Valor computed mostrarCentroPoblado: ${mostrarCentroPoblado.value}`);
        
        if (esCartografia && filtros.value.municipio) {
          console.log('🏘️ ✅ EJECUTANDO cargarCentrosPoblados() por cambio de zona');
          cargarCentrosPoblados();
        } else {
          console.log('🏘️ ❌ NO se ejecuta cargarCentrosPoblados()');
          console.log(`   - Es cartografía: ${esCartografia}`);
          console.log(`   - Tiene municipio: ${!!filtros.value.municipio}`);
        }
      }
    }

    // ✅ Cargar centros poblados MEJORADA CON MÁS DEBUG
    async function cargarCentrosPoblados() {
      console.log(`🚀 INICIANDO cargarCentrosPoblados()`);
      console.log(`🔍 DEBUG - Estado completo:`);
      console.log(`   - Municipio: ${filtros.value.municipio}`);
      console.log(`   - Zona actual: "${filtros.value.zona}"`);
      console.log(`   - Es edición: ${isEditing.value}`);
      console.log(`   - Centro poblado en form: "${formData.value.cod_centro_poblado}"`);
      console.log(`   - API disponible: ${typeof getCentrosPobladosPorMunicipio}`);
      
      if (!filtros.value.municipio) {
        console.log(`❌ No hay municipio, saliendo de cargarCentrosPoblados`);
        centrosPoblados.value = [];
        return;
      }
      
      try {
        cargandoCentrosPoblados.value = true;
        console.log(`🔍 Cargando centros poblados para municipio ${filtros.value.municipio}...`);
        
        // ✅ USAR LA FUNCIÓN CORRECTA DEL API
        const data = await getCentrosPobladosPorMunicipio(parseInt(filtros.value.municipio));
        console.log(`📡 Respuesta del API:`, data);
        
        centrosPoblados.value = Array.isArray(data) ? data : [];
        
        console.log(`✅ Cargados ${centrosPoblados.value.length} centros poblados exitosamente`);
        if (centrosPoblados.value.length > 0) {
          console.log(`📋 Primeros centros poblados:`, centrosPoblados.value.slice(0, 3).map(c => ({
            codigo: c.cod_centro_poblado,
            nombre: c.nom_centro_poblado
          })));
        } else {
          console.warn(`⚠️ No se encontraron centros poblados para el municipio ${filtros.value.municipio}`);
        }

        // ✅ SI ESTAMOS EDITANDO Y HAY UN CENTRO POBLADO GUARDADO, VERIFICAR SU EXISTENCIA
        if (isEditing.value && formData.value.cod_centro_poblado && centrosPoblados.value.length > 0) {
          const centroExiste = centrosPoblados.value.find(c => c.cod_centro_poblado === formData.value.cod_centro_poblado);
          if (centroExiste) {
            console.log(`🎯 CENTRO POBLADO CONFIRMADO EN LISTA: ${centroExiste.cod_centro_poblado} - ${centroExiste.nom_centro_poblado}`);
          } else {
            console.warn(`⚠️ El centro poblado ${formData.value.cod_centro_poblado} NO está en la lista cargada`);
            console.log(`📋 Centros disponibles:`, centrosPoblados.value.map(c => c.cod_centro_poblado));
          }
        }
        
      } catch (error) {
        console.error('❌ Error al cargar centros poblados:', error);
        console.error('❌ Error completo:', {
          message: error.message,
          stack: error.stack,
          response: error.response?.data
        });
        centrosPoblados.value = [];
        mensaje.value = {
          texto: 'Error al cargar centros poblados: ' + error.message,
          tipo: 'error'
        };
      } finally {
        cargandoCentrosPoblados.value = false;
        console.log(`🏁 Finalizando cargarCentrosPoblados(), cargando: ${cargandoCentrosPoblados.value}`);
      }
    }

// Función para cargar TODOS los datos sin importar la paginación
    function cargarTodosLosDatos(url, params = {}) {
      return new Promise(async (resolve, reject) => {
        try {
          let todosLosResultados = [];
          let urlActual = url;
          
          if (Object.keys(params).length > 0) {
            const queryParams = new URLSearchParams(params).toString();
            urlActual = `${url}?${queryParams}`;
          }
          
          const primeraRespuesta = await axios.get(urlActual);
          
          if (Array.isArray(primeraRespuesta.data)) {
            console.log(`Recibidos ${primeraRespuesta.data.length} elementos (sin paginación)`);
            resolve(primeraRespuesta.data);
            return;
          }
          
          if (primeraRespuesta.data.results) {
            todosLosResultados = [...primeraRespuesta.data.results];
            
            const count = primeraRespuesta.data.count || 0;
            console.log(`Total de elementos a cargar: ${count}`);
            
            if (todosLosResultados.length >= count) {
              resolve(todosLosResultados);
              return;
            }
            
            const pageSize = primeraRespuesta.data.results.length;
            const totalPages = Math.ceil(count / pageSize);
            
            const promesas = [];
            for (let pagina = 2; pagina <= totalPages; pagina++) {
              let urlPagina = `${url}?page=${pagina}`;
              
              if (Object.keys(params).length > 0) {
                const otrosParams = new URLSearchParams(params).toString();
                urlPagina = `${url}?${otrosParams}&page=${pagina}`;
              }
              
              promesas.push(axios.get(urlPagina));
            }
            
            const respuestas = await Promise.all(promesas);
            
            respuestas.forEach(respuesta => {
              if (respuesta.data && respuesta.data.results) {
                todosLosResultados = [...todosLosResultados, ...respuesta.data.results];
              }
            });
            
            resolve(todosLosResultados);
          } else {
            resolve([]);
          }
        } catch (error) {
          console.error(`Error cargando datos desde ${url}:`, error);
          reject(error);
        }
      });
    }

    // Función para formatear fechas
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES');
      } catch (error) {
        return dateString;
      }
    };
    
    // Filtrar formatos y entidades
    function filtrarFormatos() {
      if (formatosFiltrados.value.length === 1) {
        formData.value.formato_tipo = formatosFiltrados.value[0].cod_formato_tipo;
      }
      
      const formatoExacto = formatos.value.find(f => 
        f.cod_formato_tipo.toLowerCase() === formatoSearch.value.toLowerCase()
      );
      
      if (formatoExacto) {
        formData.value.formato_tipo = formatoExacto.cod_formato_tipo;
      }
    }
    
    function filtrarEntidades() {
      if (entidadesFiltradas.value.length === 1) {
        formData.value.cod_entidad = entidadesFiltradas.value[0].cod_entidad;
      }
      
      const entidadExacta = entidades.value.find(e => 
        e.nom_entidad.toLowerCase() === entidadSearch.value.toLowerCase() ||
        e.cod_entidad.toLowerCase() === entidadSearch.value.toLowerCase()
      );
      
      if (entidadExacta) {
        formData.value.cod_entidad = entidadExacta.cod_entidad;
      }
    }

    // Computados existentes
    const formatosFiltrados = computed(() => {
      if (!formatoSearch.value) {
        return formatos.value;
      }
      return formatos.value.filter(formato => 
        formato.cod_formato_tipo.toLowerCase().includes(formatoSearch.value.toLowerCase())
      );
    });
    
    const entidadesFiltradas = computed(() => {
      if (!entidadSearch.value) {
        return entidades.value;
      }
      return entidades.value.filter(entidad => 
        entidad.nom_entidad.toLowerCase().includes(entidadSearch.value.toLowerCase()) ||
        entidad.cod_entidad.toLowerCase().includes(entidadSearch.value.toLowerCase())
      );
    });
    
    const insumosConCategoria = computed(() => {
      return insumos.value.map(insumo => {
        if (insumo.categoria_nombre) {
          return insumo;
        }
        
        if (insumo.categoria && insumo.categoria.nom_categoria) {
          return {
            ...insumo,
            categoria_nombre: insumo.categoria.nom_categoria
          };
        }
        
        return {
          ...insumo,
          categoria_nombre: 'Categoría no disponible'
        };
      });
    });
    
    const isFormValid = computed(() => {
      const basico = (
        formData.value.cod_clasificacion &&
        formData.value.cod_usuario &&
        formData.value.estado &&
        formData.value.cod_entidad &&
        formData.value.formato_tipo
      );
      // Si se muestra sub-clasificación, debe estar seleccionada
      if (mostrarSubClasificacion.value) {
        return basico && formData.value.cod_sub_clasificacion;
      }
      return basico;
    });
    
    // 🚀 OPTIMIZADO: Obtener siguiente código usando endpoint del backend
    async function obtenerUltimosCodigos() {
      try {
        // Usar el nuevo endpoint optimizado que ejecuta MAX() en la BD
        const response = await axios.get(`${API_URL}/preoperacion/detalles-insumo/siguiente_codigo/`);

        if (response.data && response.data.siguiente_codigo) {
          formData.value.cod_detalle = response.data.siguiente_codigo;
          console.log(`✅ Siguiente código obtenido del backend: ${response.data.siguiente_codigo}`);
        } else {
          // Fallback si la respuesta no tiene el formato esperado
          formData.value.cod_detalle = 1;
        }
      } catch (error) {
        console.error('Error al obtener siguiente código:', error);
        // Fallback: usar timestamp
        formData.value.cod_detalle = Math.floor(Date.now() / 1000) % 100000;
      }
    }
    
    // Obtener información del usuario actual
    async function setUsuarioActual() {
      if (authStore.user) {
        usuarioNombre.value = authStore.user.username || authStore.user.email || '';
        
        if (usuarioNombre.value) {
          await obtenerCodigoUsuario(usuarioNombre.value);
          return;
        }
      }
      
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const config = {
            headers: {
              'Authorization': `Token ${token}`
            }
          };
          
          const perfilResponse = await axios.get(`${API_URL}/api/profile/`, config);
          if (perfilResponse.data) {
            const usuario = perfilResponse.data;
            usuarioNombre.value = usuario.username || usuario.email || '';
            await obtenerCodigoUsuario(usuarioNombre.value);
          }
        } catch (error) {
          console.error('Error al obtener perfil de usuario:', error);
          usuarioNombre.value = 'Usuario no identificado';
          formData.value.cod_usuario = 1;
        }
      } else {
        console.warn('No hay token de autenticación');
        usuarioNombre.value = 'Usuario no autenticado';
        formData.value.cod_usuario = 1;
      }
    }
    
    // Obtener código de usuario
    async function obtenerCodigoUsuario(username) {
      if (!username) {
        formData.value.cod_usuario = 1;
        return;
      }
      
      try {
        const response = await axios.get(`${API_URL}/preoperacion/usuarios-legacy/?search=${username}`);
        
        if (response.data && response.data.results && response.data.results.length > 0) {
          const usuario = response.data.results[0];
          formData.value.cod_usuario = usuario.cod_usuario;
        } else {
          const todosUsuarios = await cargarTodosLosDatos(`${API_URL}/preoperacion/usuarios/`);
          
          const usuarioEncontrado = todosUsuarios.find(u => 
            u.nombre.toLowerCase().includes(username.toLowerCase()) || 
            (u.correo && u.correo.toLowerCase().includes(username.toLowerCase()))
          );
          
          if (usuarioEncontrado) {
            formData.value.cod_usuario = usuarioEncontrado.cod_usuario;
          } else {
            formData.value.cod_usuario = 1;
          }
        }
      } catch (error) {
        console.error('Error al obtener código de usuario:', error);
        mensaje.value = {
          texto: 'Error al obtener información del usuario',
          tipo: 'error'
        };
        formData.value.cod_usuario = 1;
      }
    }
    
    // Cargar departamentos
    async function cargarDepartamentos() {
      try {
        console.log('Cargando TODOS los departamentos...');
        const resultado = await cargarTodosLosDatos(`${API_URL}/preoperacion/departamentos/`);
        departamentos.value = resultado;
        console.log(`Cargados ${departamentos.value.length} departamentos COMPLETOS`);
      } catch (error) {
        console.error('Error al cargar departamentos:', error);
        mensaje.value = {
          texto: 'Error al cargar departamentos',
          tipo: 'error'
        };
      }
    }
    
    // Cargar municipios ordenados alfabéticamente
    async function cargarMunicipios() {
      municipios.value = [];
      filtros.value.municipio = '';
      filtros.value.insumo = '';
      formData.value.cod_clasificacion = '';
      
      // Limpiar área al cambiar departamento
      areaMunicipio.value = '';
      formData.value.area_municipio = '';
      formData.value.porcentaje_cubrimiento = '';
      
      limpiarSeleccionArchivo();
      
      if (!filtros.value.departamento) return;
      
      try {
        console.log(`Cargando TODOS los municipios del departamento ${filtros.value.departamento}...`);
        const params = { cod_depto: filtros.value.departamento };
        const resultado = await cargarTodosLosDatos(`${API_URL}/preoperacion/municipios/`, params);
        
        municipios.value = resultado.sort((a, b) => {
          return a.nom_municipio.localeCompare(b.nom_municipio, 'es', { sensitivity: 'base' });
        });
        
        console.log(`Cargados ${municipios.value.length} municipios COMPLETOS y ordenados alfabéticamente`);
      } catch (error) {
        console.error('Error al cargar municipios:', error);
        mensaje.value = {
          texto: 'Error al cargar municipios',
          tipo: 'error'
        };
      }
    }
    
    // Cargar insumos
    async function cargarInsumos() {
      insumos.value = [];
      filtros.value.insumo = '';
      formData.value.cod_clasificacion = '';
      formData.value.cod_centro_poblado = '';

      limpiarSeleccionArchivo();

      if (!filtros.value.municipio) return;

      try {
        console.log(`Cargando insumos del municipio ${filtros.value.municipio}...`);

        // 🚀 OPTIMIZACIÓN: Cargar insumos y categorías en paralelo
        const [insumosData, categoriasData] = await Promise.all([
          cargarTodosLosDatos(`${API_URL}/preoperacion/municipios/${filtros.value.municipio}/insumos/`),
          cargarTodosLosDatos(`${API_URL}/preoperacion/categorias/`)
        ]);

        // Crear mapa de categorías para lookup O(1)
        const categoriasMap = new Map();
        categoriasData.forEach(cat => {
          categoriasMap.set(cat.cod_categoria, cat.nom_categoria);
        });

        // Asignar categorías sin hacer peticiones adicionales
        const insumosConCategorias = insumosData.map(insumo => {
          // Primero intentar obtener del objeto anidado
          if (insumo.categoria && insumo.categoria.nom_categoria) {
            return {
              ...insumo,
              categoria_nombre: insumo.categoria.nom_categoria
            };
          }
          // Si no, usar el mapa de categorías
          return {
            ...insumo,
            categoria_nombre: categoriasMap.get(insumo.cod_categoria) || 'Categoría no disponible'
          };
        });

        insumos.value = insumosConCategorias;
        console.log(`✅ Cargados ${insumos.value.length} insumos (optimizado, sin N+1)`);
        
        const hayCartografiaBasica = insumos.value.some(i => i.categoria_nombre === 'Cartografia Basica');
        console.log(`🔍 DEBUG CENTROS POBLADOS:`);
        console.log(`   - ¿Hay Cartografía Básica?: ${hayCartografiaBasica}`);
        console.log(`   - Zona actual: "${filtros.value.zona}"`);
        console.log(`   - Municipio: ${filtros.value.municipio}`);
        
        // ✅ NO CARGAR CENTROS POBLADOS AQUÍ - Solo cuando se seleccione la zona
        
      } catch (error) {
        console.error('Error al cargar insumos:', error);
        mensaje.value = {
          texto: 'Error al cargar insumos',
          tipo: 'error'
        };
      }
    }

    // Watcher para manejar cambios en el insumo
    watch(() => filtros.value.insumo, (newValue) => {
      formData.value.cod_centro_poblado = '';
      
      if (newValue && !mostrarCentroPoblado.value) {
        centrosPoblados.value = [];
      }
    });

    // Función para filtrar duplicados en clasificaciones
    function filtrarClasificacionesDuplicadas(clasificaciones) {
      const clasificacionesFiltradas = [];
      const nombresVistos = new Set();
      
      const clasificacionesOrdenadas = clasificaciones.sort((a, b) => {
        const aEspecifica = a.nombre.includes('(') && a.nombre.includes(')');
        const bEspecifica = b.nombre.includes('(') && b.nombre.includes(')');
        
        if (aEspecifica && !bEspecifica) return -1;
        if (!aEspecifica && bEspecifica) return 1;
        
        return a.nombre.localeCompare(b.nombre);
      });
      
      for (const clasificacion of clasificacionesOrdenadas) {
        const nombreBase = clasificacion.nombre.replace(/\s*\([^)]*\)\s*/g, '').trim();
        
        if (nombresVistos.has(nombreBase)) {
          console.log(`⚠️ Clasificación duplicada filtrada: "${clasificacion.nombre}" (mantuvimos la más específica)`);
          continue;
        }
        
        nombresVistos.add(nombreBase);
        clasificacionesFiltradas.push(clasificacion);
      }
      
      return clasificacionesFiltradas;
    }

    // Cargar clasificaciones con filtro de duplicados
    async function cargarClasificaciones() {
      clasificaciones.value = [];
      formData.value.cod_clasificacion = '';
      
      if (!filtros.value.insumo) return;
      
      try {
        console.log(`Cargando TODAS las clasificaciones del insumo ${filtros.value.insumo}...`);
        const resultado = await cargarTodosLosDatos(
          `${API_URL}/preoperacion/insumos/${filtros.value.insumo}/clasificaciones/`
        );
        
        const clasificacionesSinDuplicados = filtrarClasificacionesDuplicadas(resultado);
        clasificaciones.value = clasificacionesSinDuplicados;
        
        console.log(`Cargadas ${resultado.length} clasificaciones, filtradas a ${clasificaciones.value.length} (sin duplicados)`);
      } catch (error) {
        console.error('Error al cargar clasificaciones:', error);
        mensaje.value = {
          texto: 'Error al cargar clasificaciones',
          tipo: 'error'
        };
      }
    }
    
    // Cargar dominios
    async function cargarDominios() {
      try {
        console.log('Cargando TODOS los dominios...');
        
        console.log('Cargando zonas...');
        zonas.value = await cargarTodosLosDatos(`${API_URL}/preoperacion/zonas/`);
        console.log(`Cargadas ${zonas.value.length} zonas COMPLETAS`);
        
        console.log('Cargando formatos...');
        formatos.value = await cargarTodosLosDatos(`${API_URL}/preoperacion/tipos-formato/`);
        console.log(`Cargados ${formatos.value.length} formatos COMPLETOS`);
        
        console.log('Cargando entidades...');
        entidades.value = await cargarTodosLosDatos(`${API_URL}/preoperacion/entidades/`);
        console.log(`Cargadas ${entidades.value.length} entidades COMPLETAS`);
        
      } catch (error) {
        console.error('Error al cargar dominios:', error);
        mensaje.value = {
          texto: 'Error al cargar datos de referencia',
          tipo: 'error'
        };
      }
    }
    
    // Función guardarDetalle modificada para CORREGIR PROBLEMAS DE GUARDADO
// ✅ FUNCIÓN GUARDAR DETALLE CORREGIDA
    async function guardarDetalle() {
      if (!isFormValid.value) {
        mensaje.value = {
          texto: 'Por favor complete todos los campos requeridos',
          tipo: 'error'
        };
        return;
      }
      
      // ✅ DEFINIR datosAEnviar FUERA DEL TRY-CATCH
      let datosAEnviar = null;
      
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          mensaje.value = {
            texto: 'No se encontró token de autenticación. Por favor, inicie sesión nuevamente.',
            tipo: 'error'
          };
          setTimeout(() => {
            router.push('/login');
          }, 2000);
          return;
        }
        
        const config = {
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
          }
        };
        
        const isEdit = !!route.params.id;
        let detalleId = null;
        
        if (isEdit) {
          detalleId = parseInt(route.params.id);
          if (isNaN(detalleId)) {
            mensaje.value = {
              texto: 'ID de detalle inválido',
              tipo: 'error'
            };
            return;
          }
        }
        
        // Solo cubrimiento se combina, área viene del municipio
        let cubrimientoCombinado = '';
        if (formData.value.cubrimiento_valor && mostrarCubrimiento.value) {
          cubrimientoCombinado = `${formData.value.cubrimiento_valor} Ha`;
        }
        
        // ✅ PREPARAR DATOS CON LOGGING DETALLADO
        console.log('📊 PREPARANDO DATOS PARA ENVIAR...');
        console.log('📋 formData.value completo:', formData.value);
        console.log('📄 ruta_archivo antes de procesar:', formData.value.ruta_archivo);
        console.log('📈 porcentaje_cubrimiento antes de procesar:', formData.value.porcentaje_cubrimiento);
        
        // ✅ PREPARAR DATOS AQUÍ (DENTRO DEL TRY PERO ANTES DE USARLOS)
datosAEnviar = {
          ...formData.value,
          // cod_detalle: Solo enviar en edición. En creación el backend lo genera automáticamente
          ...(isEdit ? { cod_detalle: detalleId } : {}),
          cod_clasificacion: parseInt(formData.value.cod_clasificacion),
          cod_usuario: parseInt(formData.value.cod_usuario),
          cubrimiento: cubrimientoCombinado,
          // Campo área: Ahora viene del municipio, solo si se muestra
          area: mostrarCubrimiento.value ? (formData.value.area_municipio || '') : '',
          // ✅ CAMPO PORCENTAJE: SIEMPRE INCLUIR
          porcentaje_cubrimiento: formData.value.porcentaje_cubrimiento || '0',
          // Campo escala: Solo si se muestra
          escala: mostrarEscala.value ? (formData.value.escala || '') : '',
          cod_centro_poblado: formData.value.cod_centro_poblado || null,
          // Sub-clasificación: solo para fuentes secundarias
          cod_sub_clasificacion: esInsumosFuentesSecundarias.value ? (formData.value.cod_sub_clasificacion || null) : null,
          // ✅ CAMPO RUTA_ARCHIVO: SIEMPRE INCLUIR
          ruta_archivo: formData.value.ruta_archivo || '',
          cod_concepto: 1,  // Usamos un valor por defecto
          
          // ✅ CAMPOS DE FECHA: CONVERTIR STRINGS VACÍOS A NULL
          fecha_entrega: formData.value.fecha_entrega && formData.value.fecha_entrega.trim() !== '' 
            ? formData.value.fecha_entrega 
            : null,
          fecha_disposicion: formData.value.fecha_disposicion && formData.value.fecha_disposicion.trim() !== '' 
            ? formData.value.fecha_disposicion 
            : null
        };

        console.log('📊 Datos después del spread inicial:', {
          ruta_archivo: datosAEnviar.ruta_archivo,
          porcentaje_cubrimiento: datosAEnviar.porcentaje_cubrimiento,
          area: datosAEnviar.area,
          cubrimiento: datosAEnviar.cubrimiento,
          fecha_entrega: datosAEnviar.fecha_entrega,
          fecha_disposicion: datosAEnviar.fecha_disposicion
        });

        // ✅ VALIDAR FORMATO DE FECHAS ANTES DE ENVIAR
        const validarFecha = (fecha, nombreCampo) => {
          if (!fecha) return true; // null/undefined son válidos
          
          // Validar formato YYYY-MM-DD
          const formatoFecha = /^\d{4}-\d{2}-\d{2}$/;
          if (!formatoFecha.test(fecha)) {
            throw new Error(`${nombreCampo} debe tener formato YYYY-MM-DD. Valor recibido: "${fecha}"`);
          }
          
          // Validar que sea una fecha válida
          const fechaObj = new Date(fecha);
          if (isNaN(fechaObj.getTime())) {
            throw new Error(`${nombreCampo} no es una fecha válida. Valor recibido: "${fecha}"`);
          }
          
          return true;
        };

        // Validar fechas
        validarFecha(datosAEnviar.fecha_entrega, 'fecha_entrega');
        validarFecha(datosAEnviar.fecha_disposicion, 'fecha_disposicion');

        console.log('✅ Fechas validadas correctamente:', {
          fecha_entrega: datosAEnviar.fecha_entrega,
          fecha_disposicion: datosAEnviar.fecha_disposicion
        });
        
        console.log('📊 Datos después del spread inicial:', {
          ruta_archivo: datosAEnviar.ruta_archivo,
          porcentaje_cubrimiento: datosAEnviar.porcentaje_cubrimiento,
          area: datosAEnviar.area,
          cubrimiento: datosAEnviar.cubrimiento
        });
        
        // ✅ REMOVER CAMPOS TEMPORALES PERO CONSERVAR IMPORTANTES
        if (!mostrarCubrimiento.value) {
          delete datosAEnviar.cubrimiento_valor; // Solo quitar el temporal
          delete datosAEnviar.area_municipio; // Solo quitar el temporal
          console.log('🔧 Tipo sin cubrimiento - eliminando campos temporales pero conservando porcentaje');
        } else {
          delete datosAEnviar.cubrimiento_valor; // Quitar temporal (ya está en 'cubrimiento')
          console.log('🔧 Tipo con cubrimiento - eliminando solo campo temporal');
        }
        
        // Remover escala si no se usa
        if (!mostrarEscala.value) {
          delete datosAEnviar.escala;
          console.log('🔧 Eliminando escala (no se usa para este tipo)');
        }
        
        // ✅ SIEMPRE LIMPIAR CAMPOS TEMPORALES DE UI
        delete datosAEnviar.area_municipio; // Siempre eliminar (es temporal de UI)

        // ✅ EN CREACIÓN: Eliminar cod_detalle para que el backend lo genere automáticamente
        if (!isEdit) {
          delete datosAEnviar.cod_detalle;
          console.log('🔧 Creación: cod_detalle eliminado (el backend lo generará automáticamente)');
        }

        // ✅ LOGGING FINAL ANTES DE ENVIAR
        console.log('📤 DATOS FINALES A ENVIAR:');
        console.log('🔍 Operación:', isEdit ? 'Actualización' : 'Creación');
        console.log('🔍 ID del detalle:', isEdit ? detalleId : '(generado por backend)');
        console.log('🔍 Datos completos:', datosAEnviar);
        console.log('📄 ruta_archivo final:', datosAEnviar.ruta_archivo);
        console.log('📈 porcentaje_cubrimiento final:', datosAEnviar.porcentaje_cubrimiento);
        console.log('📊 Cubrimiento final:', datosAEnviar.cubrimiento);
        console.log('🔍 Área final:', datosAEnviar.area);
        
        let response;
        
        if (isEdit) {
          console.log(`🔄 ENVIANDO PUT a: ${API_URL}/preoperacion/detalles-insumo/${detalleId}/`);
          response = await axios.put(
            `${API_URL}/preoperacion/detalles-insumo/${detalleId}/`, 
            datosAEnviar, 
            config
          );
          mensaje.value = {
            texto: 'Detalle de insumo actualizado exitosamente',
            tipo: 'success'
          };
        } else {
          console.log(`🔄 ENVIANDO POST a: ${API_URL}/preoperacion/detalles-insumo/`);
          response = await axios.post(
            `${API_URL}/preoperacion/detalles-insumo/`, 
            datosAEnviar, 
            config
          );
          mensaje.value = {
            texto: 'Detalle de insumo guardado exitosamente',
            tipo: 'success'
          };
        }
        
        console.log('✅ Respuesta exitosa del servidor:', response.data);
        console.log('📄 ruta_archivo en respuesta:', response.data.ruta_archivo);
        console.log('📈 porcentaje_cubrimiento en respuesta:', response.data.porcentaje_cubrimiento);
        
        setTimeout(() => {
          router.push('/gestion-informacion/detalles');
        }, 1500);
        
      } catch (error) {
        console.error('❌ Error al guardar detalle:', error);
        
        // ✅ AHORA datosAEnviar ESTÁ DISPONIBLE AQUÍ
        if (error.response) {
          console.error('📤 Datos que se intentaron enviar:', datosAEnviar);
          console.error('📥 Respuesta del servidor:', error.response.data);
          console.error('📢 Status code:', error.response.status);
          
          // ✅ MANEJO DETALLADO DE ERROR 400
          if (error.response.status === 400) {
            console.error('🔍 DETALLES DEL ERROR 400:');
            console.error('🔍 Headers enviados:', error.config?.headers);
            console.error('🔍 URL:', error.config?.url);
            console.error('🔍 Método:', error.config?.method);
            console.error('🔍 Datos enviados (string):', JSON.stringify(datosAEnviar, null, 2));
            
            // Mostrar errores específicos del servidor
            if (error.response.data && typeof error.response.data === 'object') {
              console.error('🔍 Errores por campo:');
              Object.entries(error.response.data).forEach(([campo, errores]) => {
                console.error(`   ${campo}: ${Array.isArray(errores) ? errores.join(', ') : errores}`);
              });
            }
          }
        }
        
        let mensajeError = (route.params.id) ? 
          'Error al actualizar el detalle de insumo' :
          'Error al guardar el detalle de insumo';
        
        if (error.response) {
          if (error.response.status === 500) {
            mensajeError = 'Error en el servidor: Hay un problema con la configuración del backend.';
          } else if (error.response.status === 404) {
            mensajeError = 'Error: No se encontró el recurso solicitado. Verifique que el ID del detalle sea válido.';
          } else if (error.response.status === 400) {
            // ✅ MANEJO ESPECÍFICO PARA ERROR 400
            if (error.response.data && typeof error.response.data === 'object') {
              const errores = [];
              Object.entries(error.response.data).forEach(([campo, mensajes]) => {
                const mensajesArray = Array.isArray(mensajes) ? mensajes : [mensajes];
                errores.push(`${campo}: ${mensajesArray.join(', ')}`);
              });
              
              if (errores.length > 0) {
                mensajeError = `Errores de validación:\n${errores.join('\n')}`;
              } else {
                mensajeError = 'Error de validación: Los datos enviados no son válidos.';
              }
            } else if (error.response.data && typeof error.response.data === 'string') {
              mensajeError = `Error de validación: ${error.response.data}`;
            } else {
              mensajeError = 'Error de validación: Verifique que todos los campos estén correctamente completados.';
            }
          } else {
            mensajeError = `Error ${error.response.status}: ${error.response.data?.detail || error.response.data?.message || 'Error desconocido'}`;
          }
        } else if (error.request) {
          mensajeError = 'Error de conexión: No se pudo conectar con el servidor.';
        } else {
          mensajeError = `Error: ${error.message}`;
        }
        
        mensaje.value = {
          texto: mensajeError,
          tipo: 'error'
        };
        
        // ✅ MOSTRAR DATOS EN CONSOLA PARA DEBUG
        if (datosAEnviar) {
          console.log('🔍 DATOS COMPLETOS QUE SE INTENTARON ENVIAR:');
          console.table(datosAEnviar);
        }
      }
    }

    
    // Cancelar edición
    function cancelar() {
      router.push('/gestion-informacion/detalles');
    }
    
    // ✅ FUNCIÓN PRINCIPAL - CARGAR DETALLE EXISTENTE CON PARCHE INTEGRADO
    async function cargarDetalleExistente(id) {
      try {
        cargando.value = true;
        mensaje.value = {
          texto: 'Cargando datos del detalle...',
          tipo: 'info'
        };
        
        const detalleId = parseInt(id);
        if (isNaN(detalleId)) {
          throw new Error('ID del detalle inválido');
        }
        
        console.log(`🔍 ID RECIBIDO: "${id}" (tipo: ${typeof id})`);
        console.log(`🔍 ID PARSEADO: ${detalleId} (tipo: ${typeof detalleId})`);
        console.log(`🔍 URL que se va a llamar: ${API_URL}/preoperacion/detalles-insumo/${detalleId}/`);

        const response = await axios.get(`${API_URL}/preoperacion/detalles-insumo/${detalleId}/`, {
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        });

console.log('📦 RESPUESTA DEL SERVIDOR:', response.data);
        
        if (!response.data) {
          throw new Error('No se encontraron datos para el detalle solicitado');
        }
        
        const detalle = response.data;
        console.log('Datos del detalle obtenidos:', detalle);
        
        // Procesar cubrimiento para separar valor
        let cubrimientoValor = '';
        
        if (detalle.cubrimiento) {
          const cubrimientoMatch = detalle.cubrimiento.match(/^([\d.,]+)\s*Ha$/);
          if (cubrimientoMatch) {
            cubrimientoValor = cubrimientoMatch[1];
          } else {
            cubrimientoValor = detalle.cubrimiento;
          }
        }
        
        // Cargar datos en el formulario con nuevos campos
        formData.value = {
          cod_detalle: detalle.cod_detalle,
          cod_clasificacion: detalle.cod_clasificacion,
          cod_usuario: detalle.cod_usuario,
          escala: detalle.escala || '',
          estado: detalle.estado || '',
          cubrimiento_valor: cubrimientoValor,
          fecha_entrega: detalle.fecha_entrega || '',
          fecha_disposicion: detalle.fecha_disposicion || '',
          // Nuevos campos
          area_municipio: detalle.area || '', // Área viene de la BD
          porcentaje_cubrimiento: detalle.porcentaje_cubrimiento || '0',
          cod_entidad: detalle.cod_entidad || '',
          observacion: detalle.observacion || '',
          // Vigencia: Extraer solo el año si es una fecha completa
          vigencia: detalle.vigencia ? (detalle.vigencia.includes('-') ? new Date(detalle.vigencia).getFullYear().toString() : detalle.vigencia) : '',
          formato_tipo: detalle.formato_tipo || '',
          zona: detalle.zona || '',
          cod_centro_poblado: detalle.cod_centro_poblado || '',
          ruta_archivo: detalle.ruta_archivo || '',
          cod_sub_clasificacion: detalle.cod_sub_clasificacion || ''
        };
        // ✅ FORZAR CARGA DE ARCHIVO - BRUTAL Y DIRECTO
          console.log(`🔧 FORZANDO CARGA DE ARCHIVO: "${detalle.ruta_archivo}"`);

          // Modo manual por defecto si hay archivo
          if (detalle.ruta_archivo) {
            archivoSelectionMode.value = 'manual';
            formData.value.ruta_archivo = detalle.ruta_archivo;
            console.log(`📝 ARCHIVO FORZADO EN MANUAL: ${detalle.ruta_archivo}`);
          }

          // FORZAR CARGA DE ARCHIVOS DISPONIBLES
          if (filtros.value.municipio) {
            console.log(`📂 FORZANDO CARGA DE ARCHIVOS PARA MUNICIPIO: ${filtros.value.municipio}`);
            cargarArchivosDisponibles();
          }
        
        // Establecer el área del municipio en la variable reactiva
        areaMunicipio.value = detalle.area || '';
        
        // Configurar modo de selección de archivo
        if (formData.value.ruta_archivo) {
          archivoSelectionMode.value = 'manual';
        }
        
        // Establecer zona en filtros también
        filtros.value.zona = detalle.zona || '';
        
        // Cargar datos relacionados jerárquicos
        if (detalle.cod_clasificacion) {
          try {
            console.log(`Cargando clasificación ${detalle.cod_clasificacion}...`);
            
            const clasificacionResponse = await axios.get(
              `${API_URL}/preoperacion/clasificaciones/${detalle.cod_clasificacion}/`
            );
            
            const clasificacion = clasificacionResponse.data;
            console.log('Clasificación cargada:', clasificacion);
            
            clasificaciones.value = [clasificacion];
            
            if (clasificacion.cod_insumo) {
              console.log(`Cargando insumo ${clasificacion.cod_insumo}...`);
              
              const insumoResponse = await axios.get(
                `${API_URL}/preoperacion/insumos/${clasificacion.cod_insumo}/`
              );
              
              const insumo = insumoResponse.data;
              console.log('Insumo cargado:', insumo);
              
              insumos.value = [insumo];
              filtros.value.insumo = insumo.cod_insumo;
              
              if (insumo.cod_municipio) {
                console.log(`Cargando municipio ${insumo.cod_municipio}...`);
                
                const municipioResponse = await axios.get(
                  `${API_URL}/preoperacion/municipios/${insumo.cod_municipio}/`
                );
                
                const municipio = municipioResponse.data;
                console.log('Municipio cargado:', municipio);
                
                municipios.value = [municipio];
                filtros.value.municipio = municipio.cod_municipio;
                
                // Establecer área del municipio al cargar
                if (municipio.area) {
                  areaMunicipio.value = municipio.area;
                  formData.value.area_municipio = municipio.area;
                  console.log(`✅ Área del municipio establecida: ${municipio.area} Ha`);
                }
                
                if (municipio.cod_depto) {
                  console.log(`Cargando departamento ${municipio.cod_depto}...`);
                  
                  if (departamentos.value.length === 0) {
                    await cargarDepartamentos();
                  }
                  
                  const codDepto = typeof municipio.cod_depto === 'object' 
                    ? municipio.cod_depto.cod_depto 
                    : municipio.cod_depto;
                  
                  console.log('Estableciendo departamento:', codDepto);
                  
                  filtros.value.departamento = codDepto;
                  
                  await cargarMunicipios();
                  filtros.value.municipio = municipio.cod_municipio;
                  
                  await cargarInsumos();
                  filtros.value.insumo = insumo.cod_insumo;
                  
                  await cargarClasificaciones();
                  formData.value.cod_clasificacion = detalle.cod_clasificacion;

                  // Cargar sub-clasificaciones si es fuente secundaria con sub-clasificación
                  if (detalle.cod_sub_clasificacion) {
                    await nextTick();
                    const clasif = clasificaciones.value.find(
                      c => c.cod_clasificacion == detalle.cod_clasificacion
                    );
                    if (clasif) {
                      const dominio = extraerDominio(clasif.nombre);
                      await cargarSubClasificaciones(dominio);
                      formData.value.cod_sub_clasificacion = detalle.cod_sub_clasificacion;
                    }
                  }

                  // Cargar archivos disponibles después de configurar filtros
                  if (archivoSelectionMode.value === 'automatico') {
                    console.log('🔍 Cargando archivos para buscar el archivo guardado...');
                    await cargarArchivosDisponibles();
                    
                    // Buscar el archivo en la lista después de cargar
                    if (detalle.ruta_archivo) {
                      await buscarYSeleccionarArchivo(detalle.ruta_archivo);
                    }
                  }
                }
              }
            }
          } catch (err) {
            console.error('Error al cargar datos relacionados:', err);
            mensaje.value = {
              texto: 'Error al cargar datos relacionados. Algunos campos podrían no estar disponibles.',
              tipo: 'error'
            };
          }
        }
        
        // Cargar usuario
        if (detalle.cod_usuario) {
          try {
            console.log(`Cargando usuario ${detalle.cod_usuario}...`);
            
            const usuarioResponse = await axios.get(
              `${API_URL}/preoperacion/usuarios/${detalle.cod_usuario}/`
            );
            
            usuarioNombre.value = usuarioResponse.data.nombre || 'Usuario no disponible';
            console.log('Usuario cargado:', usuarioNombre.value);
          } catch (err) {
            console.error('Error al cargar usuario:', err);
            usuarioNombre.value = 'Usuario no disponible';
          }
        }
        
        // Actualizar los campos de búsqueda para entidad y formato
        if (detalle.cod_entidad) {
          if (entidades.value.length === 0) {
            await cargarDominios();
          }
          
          const entidadEncontrada = entidades.value.find(e => e.cod_entidad === detalle.cod_entidad);
          if (entidadEncontrada) {
            entidadSearch.value = entidadEncontrada.nom_entidad;
            console.log('Entidad encontrada:', entidadEncontrada.nom_entidad);
          }
        }
        
        if (detalle.formato_tipo) {
          formatoSearch.value = detalle.formato_tipo;
          console.log('Formato establecido:', detalle.formato_tipo);
        }
        
        console.log('Detalle cargado correctamente:', formData.value);
        
        mensaje.value = {
          texto: 'Datos del detalle cargados correctamente',
          tipo: 'success'
        };

        // 🎯 PARCHE QUIRÚRGICO - SOLO ZONA Y ARCHIVO
        setTimeout(() => {
          console.log('🔧 PARCHE QUIRÚRGICO - SOLO ZONA Y ARCHIVO...');
          
          // ✅ 1. VERIFICAR QUE MUNICIPIO ESTÉ EN FILTROS
          console.log(`📍 Estado de filtros antes del parche:`);
          console.log(`   Departamento: ${filtros.value.departamento}`);
          console.log(`   Municipio: ${filtros.value.municipio}`);
          console.log(`   Insumo: ${filtros.value.insumo}`);
          console.log(`   Zona: "${filtros.value.zona}"`);
          
          // ✅ 2. FORZAR SOLO LA ZONA (sin tocar otros filtros)
          if (detalle.zona && filtros.value.zona !== detalle.zona) {
            console.log(`🎯 FORZANDO ZONA: "${detalle.zona}"`);
            filtros.value.zona = detalle.zona;
            formData.value.zona = detalle.zona;
          }
          
          // ✅ 3. CARGAR CENTROS POBLADOS SOLO SI HAY MUNICIPIO
          if (detalle.zona === 'CENTROS POBLADOS' && detalle.cod_centro_poblado && filtros.value.municipio) {
            console.log(`🏘️ Cargando centros poblados para municipio: ${filtros.value.municipio}`);
            
            cargarCentrosPoblados().then(() => {
              console.log(`✅ Centros poblados cargados: ${centrosPoblados.value.length}`);
              
              // Esperar un poco más y establecer centro poblado
              setTimeout(() => {
                formData.value.cod_centro_poblado = detalle.cod_centro_poblado;
                console.log(`✅ Centro poblado establecido: ${detalle.cod_centro_poblado}`);
              }, 500);
            }).catch(error => {
              console.error('❌ Error cargando centros poblados:', error);
            });
          } else if (detalle.zona === 'CENTROS POBLADOS' && !filtros.value.municipio) {
            console.log(`❌ No se puede cargar centros poblados: falta municipio en filtros`);
            // Intentar restaurar municipio del detalle si es posible
            if (municipios.value.length > 0) {
              const municipioDetalle = municipios.value[0];
              filtros.value.municipio = municipioDetalle.cod_municipio;
              console.log(`🔄 Restaurando municipio: ${municipioDetalle.cod_municipio}`);
              
              // Reintentar cargar centros poblados
              setTimeout(() => {
                cargarCentrosPoblados().then(() => {
                  formData.value.cod_centro_poblado = detalle.cod_centro_poblado;
                  console.log(`✅ Centro poblado establecido (reintento): ${detalle.cod_centro_poblado}`);
                });
              }, 300);
            }
          }
          
        }, 1500); // Primer timer para zona y centros poblados

        // ✅ TIMER SEPARADO PARA ARCHIVO (más tiempo)
        setTimeout(() => {
          if (detalle.ruta_archivo && archivosDisponibles.value.length > 0) {
            console.log(`🔧 BUSCANDO ARCHIVO: "${detalle.ruta_archivo}"`);
            
            // Normalizar la ruta del detalle
            const rutaBuscada = detalle.ruta_archivo.replace(/\\/g, '/').toLowerCase().trim();
            
            const archivoEncontrado = archivosDisponibles.value.find(archivo => {
              if (!archivo.path_file) return false;
              
              // Normalizar la ruta del archivo
              const rutaArchivo = archivo.path_file.replace(/\\/g, '/').toLowerCase().trim();
              
              return rutaArchivo === rutaBuscada;
            });
            
            if (archivoEncontrado) {
              console.log(`✅ ARCHIVO ENCONTRADO: ${archivoEncontrado.nombre_insumo}`);
              archivoSelectionMode.value = 'automatico';
              selectedArchivoId.value = archivoEncontrado.id_lista_archivo.toString();
              archivoSeleccionado.value = archivoEncontrado;
              
              // Forzar actualización del formData
              formData.value.ruta_archivo = archivoEncontrado.path_file;
              
            } else {
              console.log('⚠️ ARCHIVO NO ENCONTRADO EN LISTA AUTOMÁTICA');
              console.log(`📋 Total archivos disponibles: ${archivosDisponibles.value.length}`);
              console.log(`📋 Ruta buscada: "${rutaBuscada}"`);
              console.log('📋 Primeras 5 rutas disponibles:');
              archivosDisponibles.value.slice(0, 5).forEach((a, i) => {
                const rutaNormalizada = a.path_file ? a.path_file.replace(/\\/g, '/').toLowerCase() : 'Sin ruta';
                console.log(`   ${i + 1}: "${rutaNormalizada}"`);
              });
              
              // Mantener modo manual con la ruta original
              archivoSelectionMode.value = 'manual';
              formData.value.ruta_archivo = detalle.ruta_archivo;
            }
          }
          
          console.log('🎉 PARCHE COMPLETADO');
          console.log(`   Zona final: "${filtros.value.zona}"`);
          console.log(`   Centro final: "${formData.value.cod_centro_poblado}"`);
          console.log(`   Archivo final: ${archivoSeleccionado.value?.nombre_insumo || 'Manual'}`);
          console.log(`   Modo archivo: ${archivoSelectionMode.value}`);
          
        }, 3000); // Más tiempo para archivos
        
      } catch (err) {
        console.error('Error al cargar detalle:', err);
        
        mensaje.value = {
          texto: 'Error al cargar los datos del detalle: ' + (err.message || 'Error desconocido'),
          tipo: 'error'
        };
      } finally {
        cargando.value = false;
      }
    }
    
    // Observadores para formato y entidad
    watch(() => formData.value.cod_entidad, (newValue) => {
      if (newValue) {
        const entidadSeleccionada = entidades.value.find(e => e.cod_entidad === newValue);
        if (entidadSeleccionada) {
          entidadSearch.value = entidadSeleccionada.nom_entidad;
        }
      }
    });
    
    watch(() => formData.value.formato_tipo, (newValue) => {
      if (newValue) {
        formatoSearch.value = newValue;
      }
    });


    // ✅ NUEVA FUNCIÓN PARA BUSCAR Y SELECCIONAR ARCHIVO
const buscarYSeleccionarArchivo = async (rutaBuscada) => {
  if (!rutaBuscada || archivosDisponibles.value.length === 0) {
    console.log('❌ No hay ruta o archivos disponibles');
    return false;
  }
  
  console.log(`🔍 Buscando archivo con ruta: "${rutaBuscada}"`);
  console.log(`📂 Total archivos disponibles: ${archivosDisponibles.value.length}`);
  
  // Normalizar la ruta buscada (quitar barras y convertir a minúsculas)
  const rutaNormalizada = rutaBuscada.replace(/\\/g, '/').toLowerCase().trim();
  
  // Buscar por ruta exacta
  let archivoEncontrado = archivosDisponibles.value.find(archivo => {
    if (!archivo.path_file) return false;
    const rutaArchivo = archivo.path_file.replace(/\\/g, '/').toLowerCase().trim();
    return rutaArchivo === rutaNormalizada;
  });
  
  // Si no encontramos por ruta exacta, buscar por nombre de archivo
  if (!archivoEncontrado) {
    const nombreArchivoBuscado = rutaBuscada.split(/[/\\]/).pop()?.toLowerCase();
    if (nombreArchivoBuscado) {
      console.log(`🔍 Buscando por nombre de archivo: "${nombreArchivoBuscado}"`);
      
      archivoEncontrado = archivosDisponibles.value.find(archivo => {
        if (!archivo.path_file) return false;
        const nombreArchivoActual = archivo.path_file.split(/[/\\]/).pop()?.toLowerCase();
        return nombreArchivoActual === nombreArchivoBuscado;
      });
    }
  }
  
  if (archivoEncontrado) {
    console.log(`✅ ARCHIVO ENCONTRADO: ${archivoEncontrado.nombre_insumo}`);
    
    // Establecer selección automática
    archivoSelectionMode.value = 'automatico';
    selectedArchivoId.value = archivoEncontrado.id_lista_archivo.toString();
    archivoSeleccionado.value = archivoEncontrado;
    formData.value.ruta_archivo = archivoEncontrado.path_file;
    
    console.log(`📁 Archivo seleccionado automáticamente en modo automático`);
    return true;
  } else {
    console.log('⚠️ Archivo NO encontrado en lista, usando modo manual');
    
    // Fallback a modo manual
    archivoSelectionMode.value = 'manual';
    selectedArchivoId.value = '';
    archivoSeleccionado.value = null;
    formData.value.ruta_archivo = rutaBuscada; // Mantener ruta original
    
    console.log(`📝 Establecido en modo manual con ruta original`);
    return false;
  }
};



    // ✅ WATCHER ADICIONAL PARA DEBUG (agregar en el setup)
    watch(() => filtros.value.zona, (newZona, oldZona) => {
      console.log(`🔍 WATCHER ZONA: "${oldZona}" → "${newZona}"`);
      console.log(`🔍 FormData zona: "${formData.value.zona}"`);
      console.log(`🔍 Zonas disponibles:`, zonas.value.map(z => z.zona));
    });

    watch(() => formData.value.cod_centro_poblado, (newCentro, oldCentro) => {
      console.log(`🔍 WATCHER CENTRO POBLADO: "${oldCentro}" → "${newCentro}"`);
      console.log(`🔍 Centros disponibles:`, centrosPoblados.value.length);
    });

    // Watcher: cuando cambia la clasificación, cargar sub-clasificaciones y auto-seleccionar entidad si es fuente secundaria
    watch(() => formData.value.cod_clasificacion, async (newValue) => {
      if (!esInsumosFuentesSecundarias.value || !newValue) {
        subClasificaciones.value = [];
        formData.value.cod_sub_clasificacion = '';
        return;
      }
      const clasifSeleccionada = clasificaciones.value.find(
        c => c.cod_clasificacion == newValue
      );
      if (!clasifSeleccionada) return;
      const dominio = extraerDominio(clasifSeleccionada.nombre);
      await cargarSubClasificaciones(dominio);

      // Auto-seleccionar entidad según el dominio
      const codEntidad = DOMINIO_A_ENTIDAD[dominio];
      if (codEntidad) {
        formData.value.cod_entidad = codEntidad;
        // Actualizar el campo de búsqueda de entidad para reflejar la selección
        const entidadEncontrada = entidades.value.find(e => e.cod_entidad === codEntidad);
        if (entidadEncontrada) {
          entidadSearch.value = entidadEncontrada.nom_entidad;
          console.log(`🏢 Entidad auto-seleccionada: ${codEntidad} - ${entidadEncontrada.nom_entidad}`);
        }
      }
    });

    watch(() => archivoSeleccionado.value, (newArchivo, oldArchivo) => {
      console.log(`🔍 WATCHER ARCHIVO:`, {
        anterior: oldArchivo?.nombre_insumo || 'Ninguno',
        nuevo: newArchivo?.nombre_insumo || 'Ninguno',
        modo: archivoSelectionMode.value
      });
    });
    
    // Inicialización al montar el componente
    onMounted(async () => {
      console.log('Modo del formulario:', route.params.id ? 'Edición' : 'Creación');
      if (route.params.id) {
        console.log('ID del detalle a editar:', route.params.id);
      }
      
      if (!authStore.isAuthenticated) {
        console.warn('Usuario no autenticado, redirigiendo a login...');
        router.push('/login?redirect=' + encodeURIComponent(route.fullPath));
        return;
      }
      
      try {
        await Promise.all([
          cargarDepartamentos(),
          cargarDominios()
        ]);
        
        await setUsuarioActual();
        
        if (route.params.id) {
          await cargarDetalleExistente(route.params.id);
        } else {
          await obtenerUltimosCodigos();
          
          if (route.query.departamento && route.query.municipio) {
            console.log('Preseleccionando departamento y municipio desde query params...');
            
            filtros.value.departamento = route.query.departamento.toString();
            await cargarMunicipios();
            
            filtros.value.municipio = route.query.municipio.toString();
            await cargarInsumos();
            
            // Cargar área al preseleccionar municipio
            await cargarAreaMunicipio(filtros.value.municipio);
            
            console.log('Departamento y municipio preseleccionados correctamente');
          }
        }
      } catch (err) {
        console.error('Error al inicializar formulario:', err);
        mensaje.value = {
          texto: 'Error al cargar los datos iniciales: ' + (err.message || 'Error desconocido'),
          tipo: 'error'
        };
      }
    });


    // ✅ WATCHER PARA BUSCAR ARCHIVO CUANDO LOS ARCHIVOS ESTÉN LISTOS
watch(
  () => archivosDisponibles.value.length,
  (newLength) => {
    console.log(`📂 WATCHER ARCHIVOS: ${newLength} archivos disponibles`);
    
    // Si estamos editando Y hay archivo guardado Y ahora hay archivos disponibles
    if (isEditing.value && formData.value.ruta_archivo && newLength > 0) {
      console.log('🔍 EJECUTANDO BÚSQUEDA AUTOMÁTICA DE ARCHIVO...');
      buscarArchivoEnLista(formData.value.ruta_archivo);
    }
  }
);

// ✅ WATCHER ADICIONAL PARA CUANDO CAMBIE EL MUNICIPIO EN FILTROS
watch(
  () => filtros.value.municipio,
  async (newMunicipio) => {
    if (newMunicipio && isEditing.value) {
      console.log(`🏙️ MUNICIPIO LISTO EN EDICIÓN: ${newMunicipio}`);
      
      // Esperar un poco y cargar archivos
      setTimeout(async () => {
        await cargarArchivosDisponibles();
        
        // Si hay archivo guardado, buscarlo
        if (formData.value.ruta_archivo) {
          setTimeout(() => {
            buscarArchivoEnLista(formData.value.ruta_archivo);
          }, 1000);
        }
      }, 2000);
    }
  }
);

    // Función para mostrar rutas en formato Windows (para visualización)
    const mostrarRutaWindows = (ruta) => {
      return linuxToWindowsPath(ruta);
    };

    // Retornar todas las variables y funciones
    return {
      // Estado
      cargando,
      error,
      isEditing,
      
      // Filtros
      filtros,
      
      // Catálogos
      departamentos,
      municipios,
      insumos,
      insumosConCategoria,
      clasificaciones,
      zonas,
      formatos,
      entidades,
      
      // Variables de búsqueda
      formatoSearch,
      formatosFiltrados,
      entidadSearch,
      entidadesFiltradas,
      
      // Datos del formulario
      formData,
      mensaje,
      usuarioNombre,
      isFormValid,
      
      // Variables para área y porcentaje
      areaMunicipio,
      areaMunicipioFormatted,
      porcentajeCubrimientoCalculado,
      cargandoAreaMunicipio,
      onCubrimientoChange,
      
      // Centros poblados
      centrosPoblados,
      cargandoCentrosPoblados,
      mostrarCentroPoblado,
      cargarCentrosPoblados,

      // Sub-clasificaciones fuentes secundarias
      subClasificaciones,
      cargandoSubClasificaciones,
      mostrarSubClasificacion,
      
      // Variables para archivos
      archivosDisponibles,
      archivosLoading,
      archivosError,
      archivoSelectionMode,
      selectedArchivoId,
      archivoSeleccionado,
      archivoSearchTerm,
      archivosFiltrados,
      patronesDisponibles,
      mostrarTodos,
      contadorArchivos,
      rutasEnUso, // Rutas de archivos ya usadas en otros detalles

      // Variables para filtros
      filtroTipoInfoCatastral,
      mostrarFiltrosInfoCatastral,
      tiposInfoCatastralUnicos,
      hayFiltrosActivosArchivos,
      getTipoInfoCatastralFromPath,
      getCentroPobladoSeleccionado,
      getCentroPobladoFromCod,
      getClasificacionSeleccionada,
      limpiarFiltrosArchivos,
      
      // Variables para tipos de insumo
      tipoInsumoSeleccionado,
      esCartografiaBasica,
      esEstudioAgrologico,
      esInformacionCatastral,
      esDeslinde,
      esInsumosFuentesSecundarias,
      esSaldoConservacion,
      mostrarEscala,
      mostrarCubrimiento,
      mostrarZona,
      opcionesEstado,
      campoEsAutomatico,
      aplicarValoresPorDefecto,
      obtenerFechaActual,
      obtenerCodigoIGAC,
      obtenerCodigoFormato,
      
      // Métodos existentes
      cargarDepartamentos,
      cargarMunicipios,
      cargarInsumos,
      cargarClasificaciones,
      filtrarFormatos,
      filtrarEntidades,
      guardarDetalle,
      cancelar,
      onZonaChange,
      cargarAreaMunicipio,
      
      // Métodos para archivos
      cargarArchivosDisponibles,
      onArchivoSelect,
      onSelectionModeChange,
      limpiarSeleccionArchivo,
      mostrarTodosLosArchivos,
      getCategoriaInsumoSeleccionado,
      getCategoriaDelArchivo,
      formatDate,
      buscarYSeleccionarArchivo,
      buscarArchivoEnLista,

      // Función para mostrar rutas en formato Windows
      mostrarRutaWindows,
    };
  }
};
</script>

<style scoped>
/* ✅ ESTILOS ESPECÍFICOS PARA LOS NUEVOS CAMPOS */
.area-readonly {
  background-color: #f8f9fa !important;
  color: #6c757d;
  font-weight: 500;
  border: 1px solid #e9ecef !important;
}

.area-unit-fixed {
  background-color: #e9ecef;
  color: #495057;
  padding: 0.5rem 0.75rem;
  border: 1px solid #ced4da;
  border-left: none;
  border-radius: 0 4px 4px 0;
  font-weight: 500;
  display: flex;
  align-items: center;
  min-width: 50px;
  justify-content: center;
}

.porcentaje-container {
  display: flex;
  gap: 0;
}

.porcentaje-input {
  flex: 1;
  background-color: #f8f9fa !important;
  color: #6c757d;
  font-weight: 500;
  border: 1px solid #e9ecef !important;
  border-right: none;
  border-radius: 4px 0 0 4px;
}

.porcentaje-symbol {
  background-color: #e9ecef;
  color: #495057;
  padding: 0.5rem 0.75rem;
  border: 1px solid #ced4da;
  border-left: none;
  border-radius: 0 4px 4px 0;
  font-weight: 600;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  min-width: 50px;
  justify-content: center;
}

.form-hint {
  color: #6c757d;
  font-size: 0.8rem;
  margin-top: 0.25rem;
  font-style: italic;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.form-hint i {
  font-size: 14px;
  color: #007bff;
}

/* ✅ ESTILOS PARA CAMPOS AUTOMÁTICOS */
.campo-auto {
  background-color: #e8f5e8 !important;
  border-color: #28a745 !important;
  font-weight: 500;
}

.campo-auto:focus {
  box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25) !important;
  border-color: #1e7e34 !important;
}

/* Estilo para resaltar campos calculados automáticamente */
.area-readonly:focus,
.porcentaje-input:focus {
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.15) !important;
  border-color: #80bdff !important;
}

/* ✅ ESTILOS PARA DEBUG INFO */
.debug-info {
  color: #6c757d;
  font-size: 0.75rem;
  font-style: italic;
  margin-top: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.loading-info {
  color: #17a2b8;
  font-size: 0.8rem;
  margin-top: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.loading-info i {
  color: #17a2b8;
}

/* ✅ ESTILOS PARA CONFIGURACIÓN ACTIVA */
.configuracion-activa {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border: 1px solid #90caf9;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  margin: 1rem 0;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.15);
}

.config-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: #1976d2;
  font-size: 1rem;
}

.config-header i {
  color: #1976d2;
  font-size: 1.2rem;
}

.config-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  padding: 0.25rem 0;
}

.config-label {
  font-weight: 500;
  color: #495057;
}

.config-value {
  font-weight: 600;
  color: #28a745;
  background: rgba(40, 167, 69, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}



.debug-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.debug-item {
  background: white;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  border-left: 3px solid #ff8f00;
}

.debug-item strong {
  color: #e65100;
}

/* ✅ ESTILOS PARA SUBFILTROS */
.subfiltros-section {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 1px solid #dee2e6;
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1rem 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.subfiltros-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 1rem 0;
  color: #495057;
  font-size: 1rem;
  font-weight: 600;
}

.subfiltros-title i {
  color: #007bff;
  font-size: 1.2rem;
}

.subfiltros-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-item label {
  font-weight: 500;
  color: #495057;
  font-size: 0.9rem;
}

.filter-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  background-color: white;
  font-size: 0.95rem;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.filter-select:focus {
  border-color: #80bdff;
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.filter-select:disabled {
  background-color: #e9ecef;
  opacity: 0.6;
}

/* ✅ ESTILOS PARA FILTROS ACTIVOS */
.filtros-activos-info {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border: 1px solid #90caf9;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  margin: 1rem 0;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.15);
}

.filtros-activos-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  font-size: 0.9rem;
}

.filtros-activos-content > i {
  color: #1976d2;
  font-size: 1.1rem;
}

.filtros-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.filtro-tag {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 16px;
  font-size: 0.8rem;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(25, 118, 210, 0.3);
}

.clasificacion-tag {
  background: linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%);
}

.centro-tag {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
}

.tag-close {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.tag-close:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.tag-close i {
  font-size: 14px;
}

.btn-limpiar-filtros {
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(220, 53, 69, 0.3);
}

.btn-limpiar-filtros:hover {
  background: linear-gradient(135deg, #c82333 0%, #bd2130 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(220, 53, 69, 0.4);
}

.btn-limpiar-filtros i {
  font-size: 16px;
}

/* ✅ ESTILOS PARA SELECCIÓN DE ARCHIVOS */
.archivo-selection-section {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid #e9ecef;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #343a40;
  margin-bottom: 1.5rem;
  font-size: 1.2rem;
  font-weight: 600;
}

.section-title i {
  color: #007bff;
}

.archivo-selection-container {
  background-color: white;
  border-radius: 6px;
  padding: 1.5rem;
  border: 1px solid #dee2e6;
}

.selection-mode-toggle {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  cursor: pointer;
}

.radio-option input[type="radio"] {
  width: 1.2rem;
  height: 1.2rem;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  color: #6c757d;
  background-color: #f8f9fa;
  border-radius: 6px;
  margin: 1rem 0;
}

.loading-state i,
.error-state i,
.empty-state i {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.error-state {
  color: #dc3545;
}

.error-state i {
  color: #dc3545;
}

.btn-retry {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-retry:hover {
  background-color: #0056b3;
}

.archivos-disponibles {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.filter-info {
  color: #007bff;
  font-size: 0.9rem;
  font-weight: normal;
}

.contador-dinamico {
  font-weight: 600;
}

.archivo-search {
  position: relative;
  margin-bottom: 0.5rem;
}

.archivo-search i {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
  z-index: 2;
}

.search-input {
  padding-left: 2.5rem !important;
}

.archivo-select {
  max-height: 300px;
  overflow-y: auto;
}

.archivo-preview {
  background-color: #e7f3ff;
  border: 1px solid #b3d9ff;
  border-radius: 6px;
  overflow: hidden;
  margin-top: 1rem;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: #007bff;
  color: white;
  font-weight: 600;
}

.preview-content {
  padding: 1rem;
}

.preview-row {
  display: flex;
  margin-bottom: 0.5rem;
  gap: 1rem;
}

.preview-row strong {
  min-width: 80px;
  color: #495057;
}

.categoria-detectada {
  background-color: #28a745;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  font-weight: 600;
  font-size: 0.875rem;
}

.path-text {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.85rem;
  background-color: #f8f9fa;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  word-break: break-all;
  border: 1px solid #dee2e6;
}

.archivo-manual textarea {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.9rem;
  resize: vertical;
}

.archivo-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #dee2e6;
}

.btn-clear-archivo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.btn-clear-archivo:hover {
  background-color: #c82333;
}

/* ✅ ESTILOS PRINCIPALES DEL FORMULARIO */
.detalle-form-container {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  margin-bottom: 2rem;
}

.form-title {
  color: #343a40;
  margin-bottom: 1.5rem;
  font-size: 1.6rem;
  font-weight: 600;
}

.filtros-section {
  background-color: #f8f9fa;
  border-radius: 6px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid #e9ecef;
}

.row {
  display: flex;
  flex-wrap: wrap;
  margin-right: -15px;
  margin-left: -15px;
  margin-bottom: 1rem;
}

.col-md-6 {
  position: relative;
  width: 100%;
  padding-right: 15px;
  padding-left: 15px;
  flex: 0 0 50%;
  max-width: 50%;
}

.col-md-12 {
  position: relative;
  width: 100%;
  padding-right: 15px;
  padding-left: 15px;
  flex: 0 0 100%;
  max-width: 100%;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #495057;
}

.form-control {
  display: block;
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: 1rem;
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

.search-input-container {
  position: relative;
}

.search-input-container input {
  margin-bottom: 0.5rem;
}

.formato-select,
.entidad-select {
  max-height: 200px;
  overflow-y: auto;
}

.area-input-container {
  display: flex;
  gap: 0;
}

.area-input {
  flex: 1;
  border-right: none;
  border-radius: 4px 0 0 4px;
}

.form-buttons-section {
  background: none;
  border: none;
  padding: 0;
  margin-top: 2rem;
}

.form-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.btn {
  display: inline-block;
  font-weight: 500;
  text-align: center;
  white-space: nowrap;
  vertical-align: middle;
  user-select: none;
  border: 1px solid transparent;
  padding: 0.5rem 1rem;
  font-size: 1rem;
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

.btn-warning {
  color: #212529;
  background-color: #ffc107;
  border-color: #ffc107;
}

.btn-warning:hover {
  color: #212529;
  background-color: #e0a800;
  border-color: #d39e00;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  line-height: 1.5;
  border-radius: 0.2rem;
}

.alert {
  position: relative;
  padding: 1rem;
  margin-top: 1.5rem;
  border: 1px solid transparent;
  border-radius: 4px;
}

.alert-success {
  color: #155724;
  background-color: #d4edda;
  border-color: #c3e6cb;
}

.alert-danger {
  color: #721c24;
  background-color: #f8d7da;
  border-color: #f5c6cb;
}

/* ✅ ESTILOS PARA CAMPOS REQUERIDOS */
label.required:after {
  content: " *";
  color: #dc3545;
  font-weight: bold;
}

.required-fields-legend {
  margin-top: 20px;
  font-size: 0.9rem;
  color: #6c757d;
}

.required-indicator {
  color: #dc3545;
  font-weight: bold;
}

/* ✅ VALIDACIÓN */
.form-control:invalid {
  border-color: #dc3545;
}

/* ✅ ANIMACIONES */
.subfiltros-section,
.filtros-activos-info,
.configuracion-activa {
  transition: all 0.3s ease;
}

.filtro-tag {
  transition: all 0.2s ease;
}

.filtro-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(25, 118, 210, 0.4);
}

.filter-select {
  transition: all 0.2s ease;
}

.filter-select:hover:not(:disabled) {
  border-color: #80bdff;
}

/* ✅ ANIMACIÓN PARA SPINNER */
@keyframes spin {
  to { 
    transform: rotate(360deg); 
  }
}

.fa-spinner {
  animation: spin 1s linear infinite;
}

/* ✅ RESPONSIVE DESIGN */
@media (max-width: 768px) {
  .col-md-6 {
    flex: 0 0 100%;
    max-width: 100%;
  }
  
  .area-input-container,
  .porcentaje-container {
    flex-direction: column;
  }
  
  .area-unit-fixed,
  .porcentaje-symbol {
    border-radius: 0 0 4px 4px;
    border-left: 1px solid #ced4da;
    border-top: none;
  }
  
  .area-input,
  .porcentaje-input {
    border-radius: 4px 4px 0 0;
  }
  
  .form-buttons {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .btn {
    width: 100%;
  }
  
  .selection-mode-toggle {
    flex-direction: column;
    gap: 1rem;
  }

  .subfiltros-section,
  .filtros-activos-info,
  .configuracion-activa {
    padding: 0.75rem 1rem;
    margin: 0.75rem 0;
  }
  
  .subfiltros-title {
    font-size: 0.9rem;
  }
  
  .filter-item label {
    font-size: 0.85rem;
  }
  
  .filter-select {
    font-size: 0.9rem;
    padding: 0.4rem 0.6rem;
  }
  
  .filtro-tag {
    font-size: 0.75rem;
    padding: 0.2rem 0.6rem;
  }
  
  .btn-limpiar-filtros {
    font-size: 0.75rem;
    padding: 0.35rem 0.7rem;
  }

  .subfiltros-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .filtros-activos-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .filtros-tags {
    width: 100%;
  }
  
  .debug-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 576px) {
  .detalle-form-container {
    padding: 1rem;
  }
  
  .form-title {
    font-size: 1.4rem;
  }
  
  .filtros-section,
  .archivo-selection-section {
    padding: 1rem;
  }
  
  .selection-mode-toggle {
    padding: 0.75rem;
  }
  
  .archivo-selection-container {
    padding: 1rem;
  }
}

/* ✅ ANIMACIÓN SUTIL PARA CUANDO SE ACTUALIZA EL PORCENTAJE */
.porcentaje-input {
  transition: all 0.3s ease;
}

.porcentaje-input:not(:placeholder-shown) {
  background-color: #e8f5e8 !important;
  border-color: #28a745 !important;
}

/* ✅ PLACEHOLDER STYLES */
.area-readonly::placeholder,
.porcentaje-input::placeholder {
  color: #adb5bd;
  font-style: italic;
}
</style>