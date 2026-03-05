
<template>
  <div class="insumo-detail-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>Detalle de Insumo</h1>
        <div class="header-actions">
          <button @click="goBack" class="btn btn-outline">
            <i class="material-icons">arrow_back</i>
            Volver
          </button>
        </div>
      </div>
    </div>
    
    <!-- Estados de carga y error del insumo -->
    <div v-if="loading" class="loading-indicator">
      <div class="spinner"></div>
      <p>Cargando información del insumo...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      <i class="material-icons">error_outline</i>
      <p>{{ error }}</p>
    </div>
    
    <!-- Contenido principal -->
    <div v-else-if="insumo" class="content-wrapper">
      <div class="detail-card">
        <div class="card-header">
          <div class="header-info">
            <div class="icon-container">
              <i class="material-icons">
                {{ insumo.cod_categoria === 2 ? 'folder_special' : 'folder_shared' }}
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
                <div class="clasificaciones-counter">
                  <div class="counter-info">
                    <i class="material-icons">category</i>
                    <span class="counter-text">
                      {{ clasificaciones.length }} {{ clasificaciones.length === 1 ? 'Clasificación' : 'Clasificaciones' }} encontradas
                    </span>
                  </div>
                </div>
              </div>
              
              <div v-if="clasificaciones.length === 0" class="empty-state">
                <i class="material-icons">folder_open</i>
                <p>No hay clasificaciones asociadas a este insumo</p>
              </div>
              
              <div v-else class="clasificaciones-grid">
                <div v-for="clasificacion in clasificaciones" :key="clasificacion.cod_clasificacion" class="clasificacion-card">
                  <div class="clasificacion-header">
                    <div class="clasificacion-info">
                      <h4>{{ clasificacion.nombre || 'Sin nombre' }}</h4>
                      <span class="clasificacion-codigo">Código: {{ clasificacion.cod_clasificacion }}</span>
                    </div>
                  </div>
                  <div class="clasificacion-details">
                    <div class="detail-row" v-if="clasificacion.ruta">
                      <span class="detail-label">Ruta:</span>
                      <span class="detail-value path-value" :title="clasificacion.ruta">
                        {{ linuxToWindowsPath(clasificacion.ruta) }}
                      </span>
                    </div>
                    <div class="detail-row" v-if="clasificacion.descripcion">
                      <span class="detail-label">Descripción:</span>
                      <span class="detail-value">{{ clasificacion.descripcion }}</span>
                    </div>
                    <div class="detail-row" v-if="clasificacion.observacion">
                      <span class="detail-label">Observación:</span>
                      <span class="detail-value">{{ clasificacion.observacion }}</span>
                    </div>
                  </div>
                  <div class="clasificacion-footer">
                    <span class="detalles-count">
                      <i class="material-icons">description</i>
                      {{ getDetallesCount(clasificacion.cod_clasificacion) }} detalles
                    </span>
                    <span class="archivos-count">
                      <i class="material-icons">insert_drive_file</i>
                      {{ getArchivosCount(clasificacion.cod_clasificacion) }} archivos
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Pestaña de Detalles -->
            <div v-if="activeTab === 'detalles'" class="detalles-tab">
              <div class="tab-header">
                <div class="tab-filters">
                  <div class="search-box">
                    <i class="material-icons">search</i>
                    <input 
                      v-model="detalleSearch" 
                      type="text" 
                      placeholder="Buscar detalles..."
                    />
                  </div>
                  <select v-model="detalleFilter" class="filter-select">
                    <option value="">Todos los detalles</option>
                    <option value="con_observacion">Con observación</option>
                    <option value="sin_observacion">Sin observación</option>
                  </select>
                  <button @click="limpiarFiltrosDetalles" class="btn btn-outline btn-sm">
                    <i class="material-icons">clear</i>
                    Limpiar
                  </button>
                </div>
              </div>
              
              <div v-if="filteredDetalles.length === 0" class="empty-state">
                <i class="material-icons">description</i>
                <p>No se encontraron detalles</p>
              </div>
              
              <div v-else class="detalles-list">
                <div v-for="detalle in filteredDetalles" :key="detalle.cod_detalle" class="detalle-card">
                  <div class="detalle-header">
                    <h4>Detalle {{ detalle.cod_detalle }}</h4>
                    <span class="detalle-fecha">{{ formatDate(detalle.fecha_disposicion) }}</span>
                  </div>
                  <div class="detalle-info">
                    <div class="info-row">
                      <span class="info-label">Clasificación:</span>
                      <span class="info-value">{{ getNombreClasificacion(detalle.cod_insumo) }}</span>
                    </div>
                    <div class="info-row">
                      <span class="info-label">Estado:</span>
                      <span class="info-value">{{ detalle.estado || 'No especificado' }}</span>
                    </div>
                    <div v-if="detalle.observacion" class="info-row">
                      <span class="info-label">Observación:</span>
                      <span class="info-value">{{ detalle.observacion }}</span>
                    </div>
                  </div>
                  <!-- NUEVO: Botón Ver Detalles -->
                  <div class="detalle-actions">
                    <button @click="verDetalleCompleto(detalle)" class="btn btn-primary btn-sm">
                      <i class="material-icons">visibility</i>
                      Ver detalles
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Pestaña de Archivos -->
            <div v-if="activeTab === 'archivos'" class="archivos-tab">
              <div class="tab-header">
                <div class="tab-filters">
                  <div class="search-box">
                    <i class="material-icons">search</i>
                    <input 
                      v-model="archivoSearch" 
                      type="text" 
                      placeholder="Buscar archivos..."
                    />
                  </div>
                  
                  <!-- ✅ NUEVO: Filtros adicionales para Cartografía Básica -->
                  <template v-if="mostrarFiltrosCartografiaBasica">
                    <!-- Filtro por centro poblado -->
                    <select 
                      v-model="filtroCentroPoblado" 
                      @change="aplicarFiltrosArchivos"
                      class="filter-select"
                      :disabled="cargandoCentrosPoblados"
                    >
                      <option value="">Todos los centros poblados</option>
                      <option 
                        v-for="centro in centrosPobladosConArchivos" 
                        :key="centro.cod_centro_poblado" 
                        :value="extraerCodigoCentroPoblado(centro.cod_centro_poblado)"
                      >
                        {{ centro.cod_centro_poblado }} - {{ centro.nom_centro_poblado }}
                      </option>
                    </select>
                    
                    <!-- Filtro por tipo de cartografía -->
                    <select v-model="filtroTipoCartografia" @change="aplicarFiltrosArchivos" class="filter-select">
                      <option value="">Todos los tipos</option>
                      <option value="Vectorial">Vectorial ✅</option>
                      <option value="Ortofoto">Ortofoto 🏔️</option>
                      <option value="Modelo Digital">Modelo Digital del Terreno 🗺️</option>
                    </select>
                  </template>
                  
                  <button @click="limpiarFiltrosArchivos" class="btn btn-outline btn-sm">
                    <i class="material-icons">clear</i>
                    Limpiar
                  </button>
                </div>
              </div>
              
              <!-- ✅ NUEVO: Indicador de carga para centros poblados -->
              <div v-if="cargandoCentrosPoblados" class="loading-indicator-small">
                <div class="spinner-small"></div>
                <span>Cargando centros poblados...</span>
              </div>
              
              <!-- ✅ NUEVO: Información de filtros activos -->
              <div v-if="hayFiltrosActivosArchivos" class="filtros-activos-info">
                <div class="filtros-activos-content">
                  <i class="material-icons">filter_list</i>
                  <span>Filtros activos:</span>
                  <div class="filtros-tags">
                    <span v-if="filtroCentroPoblado && mostrarFiltrosCartografiaBasica" class="filtro-tag">
                      Centro: {{ getNombreCentroPobladoSeleccionado() }}
                      <button @click="filtroCentroPoblado = ''; aplicarFiltrosArchivos()" class="tag-close">×</button>
                    </span>
                    <span v-if="filtroTipoCartografia && mostrarFiltrosCartografiaBasica" class="filtro-tag">
                      Tipo: {{ filtroTipoCartografia }}
                      <button @click="filtroTipoCartografia = ''; aplicarFiltrosArchivos()" class="tag-close">×</button>
                    </span>
                    <span v-if="archivoSearch" class="filtro-tag">
                      Búsqueda: "{{ archivoSearch }}"
                      <button @click="archivoSearch = ''" class="tag-close">×</button>
                    </span>
                  </div>
                </div>
              </div>
              
              <div v-if="filteredArchivos.length === 0" class="empty-state">
                <i class="material-icons">insert_drive_file</i>
                <p>No se encontraron archivos</p>
              </div>
              
              <div v-else class="archivos-grid">
                <div v-for="archivo in filteredArchivos" :key="archivo.id_lista_archivo" class="archivo-card">
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
                    
                    <!-- ✅ NUEVO: Mostrar centro poblado para Cartografía Básica -->
                    <div v-if="mostrarFiltrosCartografiaBasica" class="detail-row">
                      <span class="detail-label">Centro Poblado:</span>
                      <span class="detail-value">{{ getCentroPobladoFromPath(archivo.path_file) }}</span>
                    </div>
                    
                    <!-- ✅ NUEVO: Mostrar tipo de cartografía -->
                    <div v-if="mostrarFiltrosCartografiaBasica" class="detail-row">
                      <span class="detail-label">Tipo:</span>
                      <span class="detail-value">{{ getTipoCartografiaFromPath(archivo.path_file) }}</span>
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
                    <div class="archivo-info">
                      <span v-if="getArchivoDescargaInfo(archivo.nombre_insumo)" class="descarga-badge">
                        {{ getArchivoDescargaInfo(archivo.nombre_insumo) }}
                      </span>
                    </div>
                    
                    <div class="archivo-actions">
                      <button 
                        @click="verArchivoDetalles(archivo)" 
                        class="btn-icon info" 
                        title="Ver detalles completos"
                      >
                        <i class="material-icons">info</i>
                      </button>
                      <button 
                        @click="testearDescarga(archivo)" 
                        class="btn-icon warning" 
                        title="Probar descarga"
                        :disabled="descargandoArchivos.has(archivo.id_lista_archivo)"
                      >
                        <i class="material-icons">bug_report</i>
                      </button>
                      <button 
                        @click="viewArchivo(archivo)" 
                        class="btn-icon primary" 
                        :title="getDownloadTitle(archivo)"
                      >
                        <i class="material-icons">visibility</i>
                      </button>
                      <button 
                        @click="downloadArchivo(archivo)" 
                        class="btn-icon success"
                        :title="`Descargar ${archivo.nombre_insumo}`"
                        :disabled="descargandoArchivos.has(archivo.id_lista_archivo)"
                      >
                        <i class="material-icons">download</i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Pestaña de Conceptos -->
            <div v-if="activeTab === 'conceptos'" class="conceptos-tab">
              <div class="tab-header">
                <div class="tab-filters">
                  <div class="search-box">
                    <i class="material-icons">search</i>
                    <input 
                      v-model="conceptoSearch" 
                      type="text" 
                      placeholder="Buscar conceptos..."
                    />
                  </div>
                  <button @click="limpiarFiltrosConceptos" class="btn btn-outline btn-sm">
                    <i class="material-icons">clear</i>
                    Limpiar
                  </button>
                </div>
                <button @click="cargarConceptosConFiltros" class="btn btn-primary btn-sm">
                  <i class="material-icons">refresh</i>
                  Recargar
                </button>
              </div>
              
              <div v-if="cargandoConceptos" class="loading-indicator">
                <div class="spinner"></div>
                <p>Cargando conceptos...</p>
              </div>
              
              <div v-else-if="errorConceptos" class="error-message">
                <i class="material-icons">error_outline</i>
                <p>{{ errorConceptos }}</p>
              </div>
              
              <div v-else-if="filteredConceptos.length === 0" class="empty-state">
                <i class="material-icons">lightbulb_outline</i>
                <p>No se encontraron conceptos</p>
              </div>
              
              <div v-else class="conceptos-list">
                <div v-for="concepto in filteredConceptos" :key="concepto.cod_concepto" class="concepto-card">
                  <div class="concepto-header">
                    <h4>{{ concepto.concepto }}</h4>
                    <div class="concepto-meta">
                      <span class="concepto-fecha">{{ formatDate(concepto.fecha) }}</span>
                      <span :class="['evaluacion-badge', getEvaluacionClass(concepto.evaluacion)]">
                        {{ concepto.evaluacion || 'Sin evaluar' }}
                      </span>
                    </div>
                  </div>
                  
                  <div class="concepto-body">
                    <div class="concepto-table">
                      <div class="concepto-row">
                        <div class="concepto-cell header">Código Concepto:</div>
                        <div class="concepto-cell">{{ concepto.cod_concepto }}</div>
                      </div>
                      <div class="concepto-row">
                        <div class="concepto-cell header">Código Detalle:</div>
                        <div class="concepto-cell">{{ concepto.cod_detalle }}</div>
                      </div>
                      <div class="concepto-row">
                        <div class="concepto-cell header">Municipio:</div>
                        <div class="concepto-cell">{{ municipioName }}</div>
                      </div>
                    </div>
                    
                    <div v-if="concepto.detalle_concepto" class="concepto-detail-section">
                      <div class="concepto-detail-header">Detalle del Concepto:</div>
                      <div class="concepto-detail-content">{{ concepto.detalle_concepto }}</div>
                    </div>
                    
                    <div v-if="concepto.observacion" class="concepto-observation-section">
                      <div class="concepto-observation-header">Observaciones:</div>
                      <div class="concepto-observation-content">{{ concepto.observacion }}</div>
                    </div>
                  </div>
                  
                  <div class="concepto-footer">
                    <div class="concepto-actions">
                      <!-- NUEVO: Botón Ver Concepto -->
                      <button @click="verConceptoCompleto(concepto)" class="btn btn-primary">
                        <i class="material-icons">visibility</i>
                        Ver concepto
                      </button>
                      <button v-if="concepto.path_file || concepto.pdf" @click="verPDF(concepto)" class="btn btn-secondary">
                        <i class="material-icons">picture_as_pdf</i>
                        Ver PDF
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
    
    <!-- Modal para ver detalle completo -->
    <div class="modal" v-if="modalDetalle.mostrar">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">Detalle de Insumo - Código {{ modalDetalle.detalle?.cod_detalle }}</h4>
            <button class="close-button" @click="modalDetalle.mostrar = false">
              <i class="material-icons">close</i>
            </button>
          </div>
          <div class="modal-body">
            <div v-if="modalDetalle.detalle" class="detalle-info">
              <div class="row">
                <div class="col-md-6">
                  <p><strong>Municipio:</strong> {{ municipioName }}</p>
                  <p><strong>Clasificación:</strong> {{ getNombreClasificacion(modalDetalle.detalle.cod_insumo) }}</p>
                  <p><strong>Estado:</strong> {{ modalDetalle.detalle.estado || 'No disponible' }}</p>
                  <p><strong>Escala:</strong> {{ modalDetalle.detalle.escala || 'No disponible' }}</p>
                  <p><strong>Cubrimiento:</strong> {{ modalDetalle.detalle.cubrimiento || 'No disponible' }}</p>
                  <p><strong>Área:</strong> {{ modalDetalle.detalle.area || 'No disponible' }}</p>
                </div>
                <div class="col-md-6">
                  <p><strong>Entidad:</strong> {{ getNombreEntidad(modalDetalle.detalle.cod_entidad) || 'No disponible' }}</p>
                  <p><strong>Formato:</strong> {{ modalDetalle.detalle.formato_tipo || 'No disponible' }}</p>
                  <p><strong>Vigencia:</strong> {{ modalDetalle.detalle.vigencia || 'No disponible' }}</p>
                  <p><strong>Zona:</strong> {{ modalDetalle.detalle.zona || 'No disponible' }}</p>
                  <p><strong>Fecha Entrega:</strong> {{ formatDate(modalDetalle.detalle.fecha_entrega) }}</p>
                  <p><strong>Fecha Disposición:</strong> {{ formatDate(modalDetalle.detalle.fecha_disposicion) }}</p>
                </div>
              </div>
              <div class="row mt-3">
                <div class="col-12">
                  <p><strong>Observaciones:</strong></p>
                  <p class="observacion-text">{{ modalDetalle.detalle.observacion || 'Sin observaciones' }}</p>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="modalDetalle.mostrar = false">Cerrar</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Modal para ver concepto completo -->
    <div class="modal" v-if="modalConcepto.mostrar">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">Concepto {{ modalConcepto.concepto?.cod_concepto }}</h4>
            <button class="close-button" @click="modalConcepto.mostrar = false">
              <i class="material-icons">close</i>
            </button>
          </div>
          <div class="modal-body">
            <div v-if="modalConcepto.concepto" class="concepto-info">
              <div class="concepto-form">
                <div class="form-row">
                  <div class="form-field">
                    <label>Concepto:</label>
                    <div class="field-value">{{ modalConcepto.concepto.concepto }}</div>
                  </div>
                  <div class="form-field">
                    <label>Fecha:</label>
                    <div class="field-value">{{ formatDate(modalConcepto.concepto.fecha) }}</div>
                  </div>
                </div>
                
                <div class="form-row">
                  <div class="form-field">
                    <label>Municipio:</label>
                    <div class="field-value">{{ municipioName }}</div>
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
                
                <div class="form-row">
                  <div class="form-field">
                    <label>Detalle asociado:</label>
                    <div class="field-value">{{ getDetalleNombre(modalConcepto.concepto.cod_detalle) || 'N/A' }}</div>
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
                      <div class="field-value">{{ modalConcepto.concepto.cod_insumo || 'N/A' }}</div>
                    </div>
                    <div class="form-field">
                      <label>Código municipio:</label>
                      <div class="field-value">{{ modalConcepto.concepto.cod_municipio }}</div>
                    </div>
                  </div>
                </div>
                
                <!-- PDF adjunto si existe -->
                <div v-if="modalConcepto.concepto.path_file || modalConcepto.concepto.pdf" class="pdf-container mt-3">
                  <div class="pdf-info">
                    <i class="material-icons">picture_as_pdf</i>
                    <span>Documento PDF adjunto</span>
                  </div>
                  <div class="pdf-actions">
                    <button @click="verPDF(modalConcepto.concepto)" class="btn btn-sm btn-primary">
                      <i class="material-icons">visibility</i>
                      Ver PDF
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="modalConcepto.mostrar = false">Cerrar</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Modal para ver detalle completo de archivo -->
    <div class="modal" v-if="modalArchivo.mostrar">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">
              <i class="material-icons">insert_drive_file</i>
              Detalles del Archivo
            </h4>
            <button class="close-button" @click="modalArchivo.mostrar = false">
              <i class="material-icons">close</i>
            </button>
          </div>
          <div class="modal-body" v-if="modalArchivo.archivo">
            <div class="archivo-details-content">
              <!-- Información básica -->
              <div class="details-section">
                <h3>
                  <i class="material-icons">info</i>
                  Información Básica
                </h3>
                <div class="details-grid">
                  <div class="detail-item">
                    <span class="detail-label">Nombre del archivo:</span>
                    <span class="detail-value">{{ modalArchivo.archivo.nombre_insumo }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Tipo:</span>
                    <span class="detail-value archivo-type-badge">Preoperación</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Extensión:</span>
                    <span class="detail-value">
                      .{{ getFileExtension(modalArchivo.archivo.nombre_insumo).toUpperCase() }}
                    </span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Fecha de disposición:</span>
                    <span class="detail-value">{{ formatDate(modalArchivo.archivo.fecha_disposicion) }}</span>
                  </div>
                </div>
              </div>

              <!-- Información de ubicación -->
              <div class="details-section">
                <h3>
                  <i class="material-icons">place</i>
                  Ubicación
                </h3>
                <div class="details-grid">
                  <div class="detail-item">
                    <span class="detail-label">Departamento:</span>
                    <span class="detail-value">{{ departamentoName }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Municipio:</span>
                    <span class="detail-value">{{ municipioName }}</span>
                  </div>
                  <div class="detail-item full-width">
                    <span class="detail-label">Ruta completa:</span>
                    <div class="ruta-completa">{{ linuxToWindowsPath(modalArchivo.archivo.path_file) }}</div>
                  </div>
                </div>
              </div>

              <!-- Información específica para Cartografía Básica -->
              <div class="details-section" v-if="mostrarFiltrosCartografiaBasica">
                <h3>
                  <i class="material-icons">map</i>
                  Información de Cartografía
                </h3>
                <div class="details-grid">
                  <div class="detail-item">
                    <span class="detail-label">Clasificación:</span>
                    <span class="detail-value">{{ getNombreClasificacion(modalArchivo.archivo.cod_insumo) }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Centro Poblado:</span>
                    <span class="detail-value">{{ getCentroPobladoFromPath(modalArchivo.archivo.path_file) }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Tipo de Cartografía:</span>
                    <span class="detail-value">{{ getTipoCartografiaFromPath(modalArchivo.archivo.path_file) }}</span>
                  </div>
                </div>
              </div>

              <!-- Información general -->
              <div class="details-section">
                <h3>
                  <i class="material-icons">description</i>
                  Información Adicional
                </h3>
                <div class="details-grid">
                  <div class="detail-item">
                    <span class="detail-label">Código insumo:</span>
                    <span class="detail-value">{{ modalArchivo.archivo.cod_insumo }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">ID del archivo:</span>
                    <span class="detail-value">{{ modalArchivo.archivo.id_lista_archivo }}</span>
                  </div>
                </div>
              </div>

              <!-- Observaciones -->
              <div class="details-section" v-if="modalArchivo.archivo.observacion">
                <h3>
                  <i class="material-icons">comment</i>
                  Observaciones
                </h3>
                <div class="observaciones-content">
                  {{ modalArchivo.archivo.observacion }}
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="modalArchivo.mostrar = false">Cerrar</button>
            <button class="btn btn-primary" @click="downloadArchivo(modalArchivo.archivo)">
              <i class="material-icons">download</i>
              Descargar archivo
            </button>
          </div>
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
import { useRoute, useRouter } from 'vue-router';
import { format, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';
import { linuxToWindowsPath } from '@/utils/pathUtils';

// Importaciones de servicios API
import { 
  getInsumoById, 
  getClasificacionesByInsumo,
  getArchivosByClasificacion, 
  getCategorias, 
  getTiposInsumo,
  getEntidades,
  getUsuarios,
  getDetallesByClasificacion
} from '@/api/insumos';

import { API_URL } from '@/api/config';
import { getMunicipioById } from '@/api/municipios';
import { getDepartamentoById } from '@/api/departamentos';
import { getConceptos, getConceptosByDetalle } from '@/api/conceptos';
import { 
  getConceptosByMunicipio,
  verDocumentoPDF 
} from '@/api/conceptos';
import { getCentrosPobladosPorMunicipio } from '@/api/centrosPoblados';

export default defineComponent({
  name: 'InsumoDetalle',
  
  setup() {
    const route = useRoute();
    const router = useRouter();
    
    // Obtener el ID desde la ruta
    const insumoId = computed(() => {
      const id = route.params.id;
      return id ? (typeof id === 'string' ? parseInt(id) : id) : null;
    });
    
    // Estado general
    const loading = ref(true); // Iniciar en true para mostrar loading
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
    const activeTab = ref('clasificaciones');
    
    // NUEVO: Estados para filtros de Cartografía Básica
    const filtroCentroPoblado = ref('');
    const filtroTipoCartografia = ref('');
    const centrosPoblados = ref<any[]>([]);
    const cargandoCentrosPoblados = ref(false);


    
    // NUEVO: Estados para modales
    const modalDetalle = ref({
      mostrar: false,
      detalle: null as any
    });
    
    const modalConcepto = ref({
      mostrar: false,
      concepto: null as any
    });
    
    const modalArchivo = ref({
      mostrar: false,
      archivo: null as any
    });
    
    // Estado de notificaciones
    const notification = ref({
      show: false,
      message: '',
      type: '',
      icon: ''
    });
    
    // Estados adicionales para conceptos y archivos
    const cargandoConceptos = ref(false);
    const errorConceptos = ref<string | null>(null);
    const descargandoArchivos = ref(new Set());
    const previewDescarga = ref<{ mostrar: boolean; archivo: any | null }>({
      mostrar: false,
      archivo: null
    });
    
    // Pestañas disponibles
    const tabs = [
      { id: 'clasificaciones', label: 'Clasificaciones', icon: 'category' },
      { id: 'detalles', label: 'Detalles', icon: 'description' },
      { id: 'archivos', label: 'Archivos', icon: 'insert_drive_file' },
      { id: 'conceptos', label: 'Conceptos', icon: 'lightbulb_outline' }
    ];
    
// ✅ NUEVO: Computed para determinar si mostrar los filtros de cartografía básica
const mostrarFiltrosCartografiaBasica = computed(() => {
  return insumo.value && 
         insumo.value.categoria && 
         insumo.value.categoria.nom_categoria === 'Cartografia Basica';
});

// ✅ NUEVO: Computed para verificar si hay filtros activos
const hayFiltrosActivosArchivos = computed(() => {
  return archivoSearch.value !== '' || 
         (mostrarFiltrosCartografiaBasica.value && (filtroCentroPoblado.value !== '' || filtroTipoCartografia.value !== ''));
});

// ✅ NUEVO: Computed para centros poblados con archivos
const centrosPobladosConArchivos = computed(() => {
  if (!mostrarFiltrosCartografiaBasica.value || !insumo.value?.cod_municipio) {
    return [];
  }

  const codigosConArchivos = new Set<string>();
  
  archivos.value.forEach(archivo => {
    if (archivo.path_file) {
      const tresDigitos = extraerCodigoFinal(archivo.path_file);
      if (tresDigitos) {
        const codigoCompleto = `${insumo.value.cod_municipio}${tresDigitos}`;
        codigosConArchivos.add(codigoCompleto);
      }
    }
  });

  return centrosPoblados.value.filter(centro => 
    codigosConArchivos.has(centro.cod_centro_poblado)
  );
});


    
    // NUEVO: Computed para obtener clasificaciones únicas
    const clasificacionesUnicas = computed(() => {
      const clasificacionesSet = new Set(
        archivos.value.map(archivo => getNombreClasificacion(archivo.cod_insumo))
      );
      return Array.from(clasificacionesSet).filter(c => c && c !== '');
    });
    

    
    // Métodos auxiliares
    const formatDate = (date: string | null) => {
      if (!date) return 'No disponible';
      try {
        return format(parseISO(date), 'dd/MM/yyyy', { locale: es });
      } catch {
        return date;
      }
    };
    
    const getNombreCategoria = (codCategoria: number) => {
      const categoria = categorias.value.find(c => c.cod_categoria === codCategoria);
      return categoria ? categoria.nom_categoria : 'Sin categoría';
    };
    
    const getTipoInsumoNombre = (tipoInsumo: number) => {
      const tipo = tiposInsumo.value.find(t => t.tipo_insumo === tipoInsumo);
      return tipo ? tipo.descripcion : 'No especificado';
    };
    
    const getNombreClasificacion = (codInsumo: number) => {
      const clasificacion = clasificaciones.value.find(c => 
        c.cod_insumo === codInsumo || 
        c.cod_clasificacion === codInsumo ||
        c.id === codInsumo
      );
      
      if (clasificacion) {
        return clasificacion.nombre_clasificacion || 
               clasificacion.nombre || 
               clasificacion.descripcion ||
               `Clasificación ${codInsumo}`;
      }
      
      return `Clasificación ${codInsumo}`;
    };
    
    const getNombreEntidad = (codEntidad: number) => {
      const entidad = entidades.value.find(e => e.cod_entidad === codEntidad);
      return entidad ? entidad.nom_entidad : 'No especificada';
    };
    
    const getNombreUsuario = (codUsuario: number) => {
      const usuario = usuarios.value.find(u => u.id === codUsuario);
      return usuario ? usuario.username : 'No especificado';
    };
    
    const getDetalleNombre = (codDetalle: number) => {
      const detalle = detalles.value.find(d => d.cod_detalle === codDetalle);
      return detalle ? `Detalle ${codDetalle}` : 'Detalle no encontrado';
    };
    
    const getDetallesCount = (codClasificacion: number) => {
      return detalles.value.filter(d => d.cod_clasificacion === codClasificacion).length;
    };
    
    const getArchivosCount = (codClasificacion: number) => {
      return archivos.value.filter(a => a.cod_insumo === codClasificacion).length;
    };
    
    const getFileIcon = (fileName: string) => {
      if (!fileName) return 'insert_drive_file';
      
      const extension = fileName.split('.').pop()?.toLowerCase();
      const iconMap: { [key: string]: string } = {
        'pdf': 'picture_as_pdf',
        'doc': 'description',
        'docx': 'description',
        'xls': 'table_chart',
        'xlsx': 'table_chart',
        'dwg': 'architecture',
        'dxf': 'architecture',
        'shp': 'map',
        'gdb': 'storage',
        'tif': 'terrain',
        'tiff': 'terrain',
        'ecw': 'satellite',
        'jpg': 'image',
        'jpeg': 'image',
        'png': 'image',
        'zip': 'folder_zip',
        'rar': 'folder_zip'
      };
      
      return iconMap[extension || ''] || 'insert_drive_file';
    };
    
    const getEvaluacionClass = (evaluacion: string) => {
      const classMap: { [key: string]: string } = {
        'Aprobado': 'success',
        'Rechazado': 'danger',
        'En revisión': 'warning',
        'Pendiente': 'info'
      };
      return classMap[evaluacion] || 'default';
    };
    
    const getCategoriaClass = (codCategoria: number) => {
      return codCategoria === 2 ? 'categoria-especial' : 'categoria-normal';
    };
    
    // NUEVO: Método para verificar si es Cartografía Básica
    const esCartografiaBasica = (archivo: any) => {
      return getNombreClasificacion(archivo.cod_insumo) === 'Cartografía Básica';
    };
    

    

    
    // NUEVO: Método alternativo para extraer código
    const extraerCodigoCentroPobladoDesdeRutaAlternativa = (pathFile: string): string => {
      if (!pathFile) return '';
      
      const partes = pathFile.split('\\');
      
      for (let i = partes.length - 1; i >= 0; i--) {
        const parte = partes[i];
        if (/^\d{3}$/.test(parte)) {
          return parte;
        }
      }
      
      return '';
    };
    

    
    // NUEVO: Método para obtener código completo de centro poblado
    const obtenerCodigoCompletoCentroPoblado = (pathFile: string, municipioId: number): string => {
      const tresDigitos = extraerCodigoFinal(pathFile);
      if (!tresDigitos || !municipioId) return '';
      
      return `${municipioId}${tresDigitos}`;
    };
    


    


    
    // NUEVO: Método para manejar cambio de clasificación
    const handleClasificacionChange = () => {
      if (!mostrarFiltrosCartografiaBasica.value) {
        filtroCentroPoblado.value = '';
        filtroTipoCartografia.value = '';
      } else {
        if (insumo.value?.cod_municipio) {
          cargarCentrosPoblados(insumo.value.cod_municipio);
        }
      }
    };

    
// ✅ NUEVO: Cargar centros poblados para el municipio del insumo
const cargarCentrosPoblados = async (municipioId: number) => {
  if (!municipioId) return;
  
  try {
    cargandoCentrosPoblados.value = true;
    console.log(`Cargando centros poblados para municipio ${municipioId}`);
    
    const data = await getCentrosPobladosPorMunicipio(municipioId);
    centrosPoblados.value = data;
    
    console.log(`Cargados ${data.length} centros poblados:`, data);
  } catch (error) {
    console.error('Error al cargar centros poblados:', error);
    centrosPoblados.value = [];
  } finally {
    cargandoCentrosPoblados.value = false;
  }
};

// ✅ NUEVO: Extraer código de centro poblado desde ruta
const extraerCodigoCentroPobladoDesdeRuta = (pathFile: string): string => {
  if (!pathFile) return '';
  
  const patterns = [
    /\\1_urb\\(\d{3})\\/,  // Para Windows: \\1_urb\\000\\
    /\/1_urb\/(\d{3})\//,  // Para Unix: /1_urb/000/
    /\\01_urb\\(\d{3})\\/,  // Por si acaso: \\01_urb\\000\\
    /\/01_urb\/(\d{3})\//   // Por si acaso: /01_urb/000/
  ];
  
  for (const pattern of patterns) {
    const match = pathFile.match(pattern);
    if (match) {
      return match[1]; // Retorna los 3 dígitos (ej: "000", "001", "013")
    }
  }
  
  return '';
};

// ✅ NUEVO: Función alternativa para extraer código
const extraerCodigoCentroPobladoAlternativa = (pathFile: string): string => {
  if (!pathFile) return '';
  
  const normalizedPath = pathFile.replace(/\\/g, '/');
  const match = normalizedPath.match(/\/0?1_urb\/(\d{3})\//);
  if (match) {
    return match[1];
  }
  
  return '';
};

// ✅ NUEVO: Función final para extraer código
const extraerCodigoFinal = (pathFile: string): string => {
  let resultado = extraerCodigoCentroPobladoDesdeRuta(pathFile);
  
  if (!resultado) {
    resultado = extraerCodigoCentroPobladoAlternativa(pathFile);
  }
  
  return resultado;
};

// ✅ NUEVO: Extraer solo los últimos 3 dígitos del código completo
const extraerCodigoCentroPoblado = (codCentroPoblado: string): string => {
  if (!codCentroPoblado) return '';
  return codCentroPoblado.slice(-3);
};

// ✅ NUEVO: Obtener centro poblado desde path
const getCentroPobladoFromPath = (pathFile: string): string => {
  if (!pathFile || !insumo.value?.cod_municipio) return 'N/A';
  
  const tresDigitos = extraerCodigoFinal(pathFile);
  if (!tresDigitos) return 'N/A';
  
  const codigoCompleto = `${insumo.value.cod_municipio}${tresDigitos}`;
  
  const centro = centrosPoblados.value.find(c => 
    c.cod_centro_poblado === codigoCompleto
  );
  
  return centro ? `${codigoCompleto} - ${centro.nom_centro_poblado}` : `${codigoCompleto} - Centro ${tresDigitos}`;
};

// ✅ NUEVO: Obtener tipo de cartografía desde path
const getTipoCartografiaFromPath = (pathFile: string): string => {
  if (!pathFile) return 'N/A';
  
  if (pathFile.includes('02_vect')) return 'Vectorial';
  if (pathFile.includes('01_rast\\01_orto') || pathFile.includes('01_rast/01_orto')) return 'Ortofoto';
  if (pathFile.includes('01_rast\\02_dtm') || pathFile.includes('01_rast/02_dtm')) return 'Modelo Digital';
  if (pathFile.includes('01_rast\\02_mtd') || pathFile.includes('01_rast/02_mtd')) return 'Modelo Digital';
  
  return 'N/A';
};

// ✅ NUEVO: Obtener nombre del centro poblado seleccionado
const getNombreCentroPobladoSeleccionado = (): string => {
  if (!filtroCentroPoblado.value || !insumo.value?.cod_municipio) return '';
  
  const codigoCompleto = `${insumo.value.cod_municipio}${filtroCentroPoblado.value}`;
  const centro = centrosPoblados.value.find(c => 
    c.cod_centro_poblado === codigoCompleto
  );
  
  return centro ? `${codigoCompleto} - ${centro.nom_centro_poblado}` : `${codigoCompleto} - Centro ${filtroCentroPoblado.value}`;
};

// ✅ NUEVO: Aplicar filtros de archivos
const aplicarFiltrosArchivos = () => {
  // Los filtros se aplican automáticamente por los computed properties
  console.log('Aplicando filtros de archivos...');
};

// ✅ NUEVO: Limpiar filtros específicos de cartografía básica
const limpiarFiltrosCartografiaBasica = () => {
  filtroCentroPoblado.value = '';
  filtroTipoCartografia.value = '';
};



    
    // NUEVO: Método para ver detalle completo
    const verDetalleCompleto = (detalle: any) => {
      modalDetalle.value.detalle = detalle;
      modalDetalle.value.mostrar = true;
    };
    
    // NUEVO: Método para ver concepto completo
    const verConceptoCompleto = (concepto: any) => {
      modalConcepto.value.concepto = concepto;
      modalConcepto.value.mostrar = true;
    };
    
    // NUEVO: Método para ver detalles del archivo
    const verArchivoDetalles = (archivo: any) => {
      modalArchivo.value.archivo = archivo;
      modalArchivo.value.mostrar = true;
    };
    
    // NUEVO: Método para obtener extensión del archivo
    const getFileExtension = (fileName: string): string => {
      if (!fileName) return '';
      return fileName.split('.').pop()?.toLowerCase() || '';
    };
    
    // Filtros computados
    const filteredDetalles = computed(() => {
      let result = [...detalles.value];
      
      if (detalleSearch.value) {
        const search = detalleSearch.value.toLowerCase();
        result = result.filter(detalle => 
          detalle.cod_detalle.toString().includes(search) ||
          (detalle.observacion && detalle.observacion.toLowerCase().includes(search)) ||
          (detalle.estado && detalle.estado.toLowerCase().includes(search))
        );
      }
      
      if (detalleFilter.value) {
        if (detalleFilter.value === 'con_observacion') {
          result = result.filter(d => d.observacion && d.observacion.trim() !== '');
        } else if (detalleFilter.value === 'sin_observacion') {
          result = result.filter(d => !d.observacion || d.observacion.trim() === '');
        }
      }
      
      return result;
    });
    
    const filteredArchivos = computed(() => {
      let result = [...archivos.value];
      
      // Filtro por búsqueda
      if (archivoSearch.value) {
        const search = archivoSearch.value.toLowerCase();
        result = result.filter(archivo => 
          archivo.nombre_insumo.toLowerCase().includes(search)
        );
      }
      
      // Filtro por clasificación
      if (archivoFilter.value) {
        result = result.filter(archivo => {
          const nombreClasificacion = getNombreClasificacion(archivo.cod_insumo);
          return nombreClasificacion === archivoFilter.value;
        });
      }
      
      // Filtros para Cartografía Básica
      if (mostrarFiltrosCartografiaBasica.value) {
        // Filtro por centro poblado
        if (filtroCentroPoblado.value) {
          result = result.filter(archivo => {
            if (!archivo.path_file || !insumo.value?.cod_municipio) return false;
            
            const tresDigitosArchivo = extraerCodigoFinal(archivo.path_file);
            return tresDigitosArchivo === filtroCentroPoblado.value;
          });
        }
        
        // Filtro por tipo de cartografía
        if (filtroTipoCartografia.value) {
          result = result.filter(archivo => {
            if (!archivo.path_file) return false;
            
            const tipoArchivo = getTipoCartografiaFromPath(archivo.path_file);
            return tipoArchivo === filtroTipoCartografia.value;
          });
        }
      }
      
      return result;
    });
    
    const filteredConceptos = computed(() => {
      let result = [...conceptos.value];
      
      if (conceptoSearch.value) {
        const search = conceptoSearch.value.toLowerCase();
        result = result.filter(concepto => 
          concepto.concepto.toLowerCase().includes(search) ||
          (concepto.detalle_concepto && concepto.detalle_concepto.toLowerCase().includes(search)) ||
          (concepto.observacion && concepto.observacion.toLowerCase().includes(search)) ||
          concepto.cod_concepto.toString().includes(search)
        );
      }
      
      return result;
    });
    
    // Métodos para limpiar filtros
    const limpiarFiltrosArchivos = () => {
      archivoSearch.value = '';
      archivoFilter.value = '';
      filtroCentroPoblado.value = '';
      filtroTipoCartografia.value = '';
    };
    
    const limpiarFiltrosDetalles = () => {
      detalleSearch.value = '';
      detalleFilter.value = '';
    };
    
    const limpiarFiltrosConceptos = () => {
      conceptoSearch.value = '';
    };
    
    // Métodos para acciones
    const goBack = () => {
      router.back();
    };
    
    const verDetalles = (clasificacion: any) => {
      router.push({
        name: 'ClasificacionDetalle',
        params: { id: clasificacion.cod_insumo }
      });
    };
    
    const viewArchivo = async (archivo: any) => {
      if (!archivo.path_file) {
        showNotification('No hay ruta disponible para este archivo', 'warning');
        return;
      }
      
      const fileName = archivo.nombre_insumo || 'archivo';
      const fileExtension = fileName.split('.').pop()?.toLowerCase();
      
      console.log('🔍 ViewArchivo - Archivo:', fileName, 'Extensión:', fileExtension);
      
      const token = localStorage.getItem('token');
      if (!token) {
        showNotification('No hay token de autenticación. Por favor, inicie sesión nuevamente.', 'error');
        return;
      }
      
      if (fileExtension === 'pdf') {
        console.log('📋 Abriendo PDF para visualización');
        const fileUrl = `${API_URL}/preoperacion/ver_pdf/?ruta=${encodeURIComponent(archivo.path_file)}&token=${token}`;
        window.open(fileUrl, '_blank');
        showNotification('Abriendo PDF en nueva ventana', 'info');
      } else {
        console.log('📁 Iniciando descarga de archivo no-PDF');
        downloadArchivo(archivo);
      }
    };
    
    const downloadArchivo = async (archivo: any) => {
      if (!archivo.path_file) {
        showNotification('No hay ruta disponible para descargar este archivo', 'warning');
        return;
      }
      
      const archivoId = archivo.id_lista_archivo;
      if (descargandoArchivos.value.has(archivoId)) {
        showNotification('Ya hay una descarga en curso para este archivo', 'warning');
        return;
      }
      
      try {
        descargandoArchivos.value.add(archivoId);
        
        const token = localStorage.getItem('token');
        if (!token) {
          throw new Error('No hay token de autenticación. Por favor, inicie sesión nuevamente.');
        }
        
        const nombreArchivo = archivo.nombre_insumo || 'archivo';
        const fileExtension = nombreArchivo.split('.').pop()?.toLowerCase();
        
        console.log('🚀 DownloadArchivo - Archivo:', nombreArchivo, 'Extensión:', fileExtension);
        
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
        
        showNotification(descripcionDescarga, 'info');
        
        let downloadUrl = '';
        
        if (fileExtension === 'pdf') {
          console.log('📋 Usando endpoint PDF para descarga');
          downloadUrl = `${API_URL}/preoperacion/ver_pdf/?ruta=${encodeURIComponent(archivo.path_file)}&token=${token}&download=true`;
        } else {
          console.log('📦 Usando endpoint de descarga para archivo:', fileExtension);
          downloadUrl = `${API_URL}/preoperacion/descargar_archivo/?ruta=${encodeURIComponent(archivo.path_file)}`;
        }
        
        const response = await fetch(downloadUrl, {
          method: 'GET',
          headers: {
            'Authorization': `Token ${token}`
          }
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          let errorMessage = 'Error al descargar el archivo';
          try {
            const errorData = JSON.parse(errorText);
            errorMessage = errorData.detail || errorData.error || errorMessage;
          } catch {
            errorMessage = errorText || errorMessage;
          }
          throw new Error(errorMessage);
        }
        
        const blob = await response.blob();
        
        let finalFileName = nombreArchivo;
        const contentDisposition = response.headers.get('content-disposition');
        if (contentDisposition) {
          const fileNameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
          if (fileNameMatch && fileNameMatch[1]) {
            finalFileName = fileNameMatch[1].replace(/['"]/g, '');
          }
        }
        
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = finalFileName;
        document.body.appendChild(link);
        link.click();
        
        setTimeout(() => {
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        }, 100);
        
        showNotification('Archivo descargado exitosamente', 'success');
        
      } catch (error: any) {
        console.error('❌ Error al descargar archivo:', error);
        showNotification(error.message || 'Error al descargar el archivo', 'error');
      } finally {
        descargandoArchivos.value.delete(archivoId);
      }
    };
    
    const verPDF = async (concepto: any) => {
      const pdfPath = concepto.path_file || concepto.pdf;
      
      if (!pdfPath) {
        showNotification('Este concepto no tiene un PDF asociado', 'warning');
        return;
      }
      
      try {
        await verDocumentoPDF(pdfPath);
        showNotification('Abriendo documento PDF...', 'info');
      } catch (error: any) {
        console.error('Error al abrir PDF:', error);
        showNotification('Error al abrir el documento PDF', 'error');
      }
    };
    
    const showNotification = (message: string, type: string = 'info') => {
      notification.value = {
        show: true,
        message,
        type,
        icon: type === 'success' ? 'check_circle' : 
              type === 'error' ? 'error' : 
              type === 'warning' ? 'warning' : 'info'
      };
      
      setTimeout(() => {
        closeNotification();
      }, 5000);
    };
    
    const closeNotification = () => {
      notification.value.show = false;
    };
    
    const testearDescarga = async (archivo: any) => {
      console.log('🧪 TEST - Información del archivo:', {
        nombre: archivo.nombre_insumo,
        path: archivo.path_file,
        extension: archivo.nombre_insumo?.split('.').pop()?.toLowerCase()
      });
      showNotification(`Test: ${archivo.nombre_insumo} - Extensión: ${archivo.nombre_insumo?.split('.').pop()}`, 'info');
    };
    
    const esArchivoComplejo = (nombreArchivo: string): boolean => {
      if (!nombreArchivo) return false;
      const extension = nombreArchivo.split('.').pop()?.toLowerCase();
      return ['gdb', 'dwg', 'tif', 'tiff', 'ecw'].includes(extension || '');
    };
    
    const getArchivoDescargaInfo = (nombreArchivo: string): string => {
      if (!nombreArchivo) return '';
      const extension = nombreArchivo.split('.').pop()?.toLowerCase();
      
      if (extension === 'gdb') return '📦 Se descargará como ZIP';
      if (['dwg', 'dxf'].includes(extension || '')) return '📐 Archivo CAD';
      if (['tif', 'tiff', 'ecw'].includes(extension || '')) return '🗺️ Archivo Raster';
      if (extension === 'shp') return '🌍 Shapefile';
      
      return '';
    };
    
    const getDownloadTitle = (archivo: any): string => {
      const extension = archivo.nombre_insumo?.split('.').pop()?.toLowerCase();
      if (extension === 'pdf') return 'Ver PDF';
      return 'Visualizar archivo';
    };
    
    const cargarConceptosConFiltros = async () => {
      console.log('🔄 INICIANDO CARGA DE CONCEPTOS...');
      console.log('📋 Detalles disponibles:', detalles.value.length);
      console.log('🏘️ Municipio:', insumo.value?.cod_municipio);
      
      // Mostrar los detalles que tenemos
      if (detalles.value.length > 0) {
        console.log('📌 Detalles cargados:', detalles.value.map(d => ({
          cod_detalle: d.cod_detalle,
          cod_clasificacion: d.cod_clasificacion,
          observacion: d.observacion
        })));
      }
      
      await cargarConceptos();
      
      console.log('✅ Conceptos cargados:', conceptos.value.length);
      if (conceptos.value.length > 0) {
        console.log('📚 Conceptos:', conceptos.value);
      }
    };
    
    const cargarDetallesPorClasificaciones = async () => {
      try {
        // Usar cod_clasificacion para buscar detalles
        const clasificacionesIds = clasificaciones.value.map(c => c.cod_clasificacion);
        const allDetalles: any[] = [];
        
        for (const codClasificacion of clasificacionesIds) {
          try {
            const detallesData = await getDetallesByClasificacion(codClasificacion);
            
            if (Array.isArray(detallesData)) {
              allDetalles.push(...detallesData);
            }
          } catch (detError) {
            console.error(`Error al cargar detalles para clasificación ${codClasificacion}:`, detError);
          }
        }
        
        detalles.value = allDetalles;
      } catch (error) {
        console.error('Error general al cargar detalles:', error);
        detalles.value = [];
      }
    };
    
    const cargarArchivosPorClasificaciones = async () => {
      try {
        const allArchivos: any[] = [];
        
        for (const clasificacion of clasificaciones.value) {
          try {
            const idClasificacion = clasificacion.cod_clasificacion;
            const archivosData = await getArchivosByClasificacion(idClasificacion);
            
            if (Array.isArray(archivosData)) {
              allArchivos.push(...archivosData);
            }
          } catch (archError) {
            console.error(`Error al cargar archivos para clasificación ${clasificacion.cod_clasificacion}:`, archError);
          }
        }
        
        archivos.value = allArchivos;
      } catch (error) {
        console.error('Error general al cargar archivos:', error);
        archivos.value = [];
      }
    };
    
    // Cargar datos iniciales
    onMounted(async () => {
      if (!insumoId.value) {
        error.value = 'No se proporcionó un ID de insumo válido';
        loading.value = false;
        return;
      }
      
      loading.value = true;
      error.value = null;
      
      try {
        const id = insumoId.value;
        
        // Cargar datos básicos...
        const [
          insumoResponse,
          categoriasResponse,
          tiposInsumoResponse,
          entidadesResponse
        ] = await Promise.all([
          getInsumoById(id),
          getCategorias(),
          getTiposInsumo(),
          getEntidades()
        ]);
        
        insumo.value = insumoResponse.data || insumoResponse;
        categorias.value = categoriasResponse.data || categoriasResponse || [];
        tiposInsumo.value = tiposInsumoResponse.data || tiposInsumoResponse || [];
        entidades.value = entidadesResponse.data || entidadesResponse || [];
        
        // Cargar usuarios por separado
        try {
          const usuariosResponse = await getUsuarios();
          usuarios.value = usuariosResponse.data || usuariosResponse || [];
        } catch (userError) {
          console.warn('⚠️ No se pudieron cargar usuarios, continuando sin ellos');
          usuarios.value = [];
        }
        
        if (!insumo.value) {
          throw new Error(`No se encontró el insumo con ID ${id}`);
        }
        
        // Cargar información del municipio
        if (insumo.value.cod_municipio) {
          try {
            const municipioResponse = await getMunicipioById(insumo.value.cod_municipio);
            const municipio = municipioResponse.data || municipioResponse;
            municipioName.value = municipio?.nom_municipio || 'No disponible';
            
            const codDepartamento = municipio?.cod_departamento || municipio?.cod_depto;
            if (codDepartamento) {
              const departamentoResponse = await getDepartamentoById(codDepartamento);
              const departamento = departamentoResponse.data || departamentoResponse;
              departamentoName.value = departamento?.nom_departamento || 'No disponible';
            }
          } catch (geoError) {
            console.error('Error al cargar información geográfica:', geoError);
            municipioName.value = 'Error al cargar';
            departamentoName.value = 'Error al cargar';
          }
        }
        
        // Cargar clasificaciones
        try {
          const clasificacionesResponse = await getClasificacionesByInsumo(id);
          clasificaciones.value = clasificacionesResponse.data || clasificacionesResponse || [];
        } catch (clasError) {
          console.error('Error al cargar clasificaciones:', clasError);
          clasificaciones.value = [];
        }
        
        // Cargar detalles y archivos si hay clasificaciones
        if (clasificaciones.value.length > 0) {
          await Promise.all([
            cargarDetallesPorClasificaciones(),
            cargarArchivosPorClasificaciones()
          ]);
          
          if (detalles.value.length > 0) {
            await cargarConceptos();
          }
        }
        
        // ✅ NUEVO: Cargar centros poblados si es cartografía básica
        if (insumo.value && 
            insumo.value.categoria && 
            insumo.value.categoria.nom_categoria === 'Cartografia Basica' && 
            insumo.value.cod_municipio) {
          await cargarCentrosPoblados(insumo.value.cod_municipio);
        }
        
      } catch (err: any) {
        console.error('❌ Error al cargar datos del insumo:', err);
        error.value = err.response?.data?.detail || err.message || 'Error al cargar la información del insumo';
        
        if (err.response?.status === 404) {
          error.value = `No se encontró el insumo con ID ${insumoId.value}`;
        }
      } finally {
        loading.value = false;
      }
    });

    
    const cargarConceptos = async () => {
      if (!insumo.value?.cod_municipio || detalles.value.length === 0) {
        return;
      }
      
      cargandoConceptos.value = true;
      errorConceptos.value = null;
      
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          throw new Error('No hay token de autenticación');
        }
        
        const municipioId = insumo.value.cod_municipio;
        const url = `${API_URL}/preoperacion/conceptos/?cod_municipio=${municipioId}`;
        
        const response = await fetch(url, {
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Extraer conceptos del response
        let todosLosConceptos: any[] = [];
        
        if (data.results && Array.isArray(data.results)) {
          todosLosConceptos = data.results;
        } else if (Array.isArray(data)) {
          todosLosConceptos = data;
        }
        
        // Filtrar por los detalles que tenemos
        const detallesIds = detalles.value.map(d => d.cod_detalle);
        
        conceptos.value = todosLosConceptos.filter(c => 
          c.cod_detalle && detallesIds.includes(c.cod_detalle)
        );
        
      } catch (err: any) {
        console.error('Error al cargar conceptos:', err);
        errorConceptos.value = err.message || 'Error al cargar conceptos';
      } finally {
        cargandoConceptos.value = false;
      }
    };
    
    // TEMPORAL: Función para verificar la estructura de datos
    const verificarEstructuraDatos = async () => {
      console.log('🔬 VERIFICANDO ESTRUCTURA DE DATOS...');
      
      if (clasificaciones.value.length > 0) {
        const primeraClasificacion = clasificaciones.value[0];
        console.log('📌 Primera clasificación completa:', primeraClasificacion);
        
        // Listar todas las propiedades
        console.log('🔑 Propiedades de la clasificación:');
        Object.keys(primeraClasificacion).forEach(key => {
          console.log(`  - ${key}: ${primeraClasificacion[key]}`);
        });
      }
    };
    
    // TEMPORAL: Probar carga directa sin pasar por clasificaciones
    const probarCargaDirecta = async () => {
      console.log('🧪 PROBANDO CARGA DIRECTA...');
      
      try {
        // Probar con el ID del insumo directamente
        const testId = insumoId.value;
        console.log(`🔍 Probando con ID del insumo: ${testId}`);
        
        // Intentar cargar detalles directamente
        console.log('📋 Intentando cargar detalles con ID:', testId);
        const detallesTest = await getDetallesByClasificacion(testId);
        console.log('📦 Respuesta detalles:', detallesTest);
        
        // Intentar cargar archivos directamente
        console.log('📁 Intentando cargar archivos con ID:', testId);
        const archivosTest = await getArchivosByClasificacion(testId);
        console.log('📦 Respuesta archivos:', archivosTest);
        
      } catch (error) {
        console.error('❌ Error en prueba directa:', error);
      }
    };
    
    // TEMPORAL: Función para recargar datos manualmente
    const recargarDatos = async () => {
      console.log('🔄 RECARGANDO TODOS LOS DATOS...');
      
      // Primero verificar estructura
      await verificarEstructuraDatos();
      
      if (clasificaciones.value.length > 0) {
        // Primero cargar detalles y archivos
        await Promise.all([
          cargarDetallesPorClasificaciones(),
          cargarArchivosPorClasificaciones()
        ]);
        
        // Luego cargar conceptos si hay detalles
        if (detalles.value.length > 0) {
          console.log('📚 Cargando conceptos ya que hay detalles disponibles...');
          await cargarConceptos();
        } else {
          console.log('⚠️ No hay detalles para cargar conceptos');
        }
      } else {
        console.warn('⚠️ No hay clasificaciones para cargar datos');
      }
    };
    
    return {
      insumoId,
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
      getArchivosCount,
      getFileIcon,
      getEvaluacionClass,
      getCategoriaClass,
      goBack,
      limpiarFiltrosArchivos,
      limpiarFiltrosDetalles,
      limpiarFiltrosConceptos,
      verDetalles,
      viewArchivo,
      downloadArchivo,
      verDocumentoPDF,
      showNotification,
      closeNotification,
      verPDF,
      cargandoConceptos,
      cargarConceptos,
      errorConceptos,
      descargandoArchivos,
      previewDescarga,
      testearDescarga,
      esArchivoComplejo,
      getArchivoDescargaInfo,
      getDownloadTitle,
      cargarConceptosConFiltros,
      cargarDetallesPorClasificaciones,
      cargarArchivosPorClasificaciones,
      // NUEVO: Estados y métodos agregados
      filtroCentroPoblado,
      filtroTipoCartografia,
      centrosPoblados,
      cargandoCentrosPoblados,
      mostrarFiltrosCartografiaBasica,
      hayFiltrosActivosArchivos,
      clasificacionesUnicas,
      centrosPobladosConArchivos,
      esCartografiaBasica,
      extraerCodigoCentroPoblado,
      getCentroPobladoFromPath,
      getTipoCartografiaFromPath,
      getNombreCentroPobladoSeleccionado,
      handleClasificacionChange,
      aplicarFiltrosArchivos,
      cargarCentrosPoblados,
      verDetalleCompleto,
      verConceptoCompleto,
      modalDetalle,
      modalConcepto,
      modalArchivo,
      verArchivoDetalles,
      getFileExtension,
      limpiarFiltrosCartografiaBasica,
      extraerCodigoFinal,
      // Utilidades de rutas
      linuxToWindowsPath,
    };
  }
});
</script>

<style scoped>
/* Estilos existentes... */
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
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #f0f0f0;
  border-top-color: #0d6efd;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner-small {
  width: 24px;
  height: 24px;
  border: 3px solid #f0f0f0;
  border-top-color: #0d6efd;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  color: #dc3545;
}

.error-message i {
  font-size: 48px;
  margin-bottom: 1rem;
}

/* Contenido principal */
.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.card-header {
  background: linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%);
  color: white;
  padding: 1.5rem;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.icon-container {
  width: 48px;
  height: 48px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-container i {
  font-size: 28px;
}

.insumo-title h2 {
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
}

.categoria-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  background-color: rgba(255, 255, 255, 0.2);
}

.categoria-especial {
  background-color: rgba(255, 193, 7, 0.3);
}

.card-body {
  padding: 1.5rem;
}

/* Sección de información básica */
.detail-section {
  margin-bottom: 2rem;
}

.detail-section h3 {
  margin: 0 0 1rem;
  font-size: 1.25rem;
  color: #333;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-weight: 600;
  color: #6c757d;
  font-size: 0.875rem;
}

.info-value {
  color: #333;
  font-size: 1rem;
}

/* Pestañas */
.detail-tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid #e9ecef;
  margin-bottom: 1.5rem;
}

.tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.tab:hover {
  color: #0d6efd;
  background-color: #f8f9fa;
}

.tab.active {
  color: #0d6efd;
  border-bottom-color: #0d6efd;
}

.tab i {
  font-size: 20px;
}

/* Contenido de pestañas */
.tab-content {
  min-height: 400px;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.tab-filters {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex: 1;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 200px;
  max-width: 400px;
}

.search-box i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
  font-size: 20px;
}

.search-box input {
  width: 100%;
  padding: 0.5rem 1rem 0.5rem 2.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.95rem;
  transition: border-color 0.3s ease;
}

.search-box input:focus {
  outline: none;
  border-color: #0d6efd;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.95rem;
  min-width: 200px;
  background-color: white;
}

/* Estado vacío */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #6c757d;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 1rem;
  opacity: 0.5;
}

/* Grids y listas */
.clasificaciones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.detalles-list,
.conceptos-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.archivos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1rem;
}

/* Cards */
.clasificacion-card,
.detalle-card,
.archivo-card,
.concepto-card {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.clasificacion-card:hover,
.detalle-card:hover,
.archivo-card:hover,
.concepto-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

/* Clasificación card */
.clasificacion-header {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.clasificacion-info h4 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  color: #333;
}

.clasificacion-codigo {
  color: #6c757d;
  font-size: 0.875rem;
}

.clasificacion-details {
  padding: 1rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.detail-label {
  font-weight: 600;
  color: #6c757d;
  font-size: 0.875rem;
}

.detail-value {
  color: #333;
  font-size: 0.875rem;
}

/* Modificar el estilo existente para path-value para mostrar la ruta completa */
.path-value {
  max-width: none; /* Cambiar de 200px a none */
  overflow: visible; /* Cambiar de hidden a visible */
  text-overflow: initial; /* Cambiar de ellipsis a initial */
  white-space: normal; /* Cambiar de nowrap a normal */
  cursor: help;
  word-break: break-all; /* Agregar para que rompa palabras largas */
  font-size: 0.8rem; /* Hacer la fuente un poco más pequeña */
  line-height: 1.4; /* Mejorar el espaciado entre líneas */
}

.clasificacion-footer {
  padding: 0.75rem 1rem;
  background-color: #f0f2f5;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detalles-count,
.archivos-count {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6c757d;
  font-size: 0.875rem;
}

/* Detalle card */
.detalle-header {
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e9ecef;
}

.detalle-header h4 {
  margin: 0;
  font-size: 1.1rem;
  color: #333;
}

.detalle-fecha {
  color: #6c757d;
  font-size: 0.875rem;
}

.detalle-info {
  padding: 1rem;
}

.info-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.info-row:last-child {
  margin-bottom: 0;
}

/* NUEVO: Estilos para acciones de detalle */
.detalle-actions {
  padding: 0.75rem 1rem;
  background-color: #f0f2f5;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: flex-end;
}

/* Archivo card */
.archivo-header {
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.archivo-icon {
  width: 40px;
  height: 40px;
  background-color: #e3f2fd;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0d6efd;
}

.archivo-title h4 {
  margin: 0 0 0.25rem;
  font-size: 1rem;
  color: #333;
  word-break: break-word;
}

.archivo-fecha {
  color: #6c757d;
  font-size: 0.875rem;
}

.archivo-body {
  padding: 1rem;
}

.archivo-footer {
  padding: 0.75rem 1rem;
  background-color: #f0f2f5;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.archivo-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.descarga-badge {
  font-size: 0.75rem;
  color: #6c757d;
  background-color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  border: 1px solid #e9ecef;
}

.archivo-actions {
  display: flex;
  gap: 0.5rem;
}

/* Concepto card */
.concepto-header {
  padding: 1rem;
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
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
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
  background-color: #5c636a;
}

.btn-outline {
  background-color: transparent;
  color: #0d6efd;
  border: 1px solid #0d6efd;
}

.btn-outline:hover {
  background-color: #0d6efd;
  color: white;
}

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
}

/* Botones de icono */
.btn-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-icon i {
  font-size: 20px;
}

.btn-icon.primary {
  background-color: #e3f2fd;
  color: #0d6efd;
}

.btn-icon.primary:hover {
  background-color: #0d6efd;
  color: white;
}

.btn-icon.success {
  background-color: #e8f5e9;
  color: #4caf50;
}

.btn-icon.success:hover {
  background-color: #4caf50;
  color: white;
}

.btn-icon.warning {
  background-color: #fff3e0;
  color: #ff9800;
}

.btn-icon.warning:hover {
  background-color: #ff9800;
  color: white;
}

.btn-icon.info {
  background-color: #e3f2fd;
  color: #1976d2;
}

.btn-icon.info:hover {
  background-color: #1976d2;
  color: white;
}

.btn-icon:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Notificación */
.notification {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  min-width: 300px;
  padding: 1rem 1.5rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: space-between;
  animation: slideIn 0.3s ease;
  z-index: 1000;
}

@keyframes slideIn {
  from {
    transform: translateX(400px);
  }
  to {
    transform: translateX(0);
  }
}

.notification.success {
  border-left: 4px solid #28a745;
}

.notification.error {
  border-left: 4px solid #dc3545;
}

.notification.warning {
  border-left: 4px solid #ffc107;
}

.notification.info {
  border-left: 4px solid #17a2b8;
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.notification-close {
  background: none;
  border: none;
  cursor: pointer;
  color: #6c757d;
  padding: 0;
}

.notification-close:hover {
  color: #333;
}

/* NUEVO: Estilos para indicador de carga pequeño */
.loading-indicator-small {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  font-size: 0.875rem;
  color: #6c757d;
}

/* NUEVO: Estilos para información de filtros activos */
.filtros-activos-info {
  background-color: #e3f2fd;
  border: 1px solid #90caf9;
  border-radius: 4px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
}

.filtros-activos-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.filtros-activos-content i {
  color: #1976d2;
}

.filtros-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filtro-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  background-color: white;
  border: 1px solid #90caf9;
  border-radius: 16px;
  font-size: 0.875rem;
  color: #1976d2;
}

.tag-close {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  line-height: 1;
  color: #1976d2;
  margin-left: 0.25rem;
  padding: 0;
}

.tag-close:hover {
  color: #0d47a1;
}

/* NUEVO: Estilos para modales */
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
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
  max-height: 70vh;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #dee2e6;
  background-color: #f8f9fa;
}

.detalle-info p {
  margin-bottom: 0.75rem;
}

.observacion-text {
  padding: 0.75rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #dee2e6;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}

/* NUEVO: Estilos para formulario en modal */
.concepto-form {
  font-size: 0.95rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-row.full-width {
  grid-template-columns: 1fr;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-field label {
  font-weight: 600;
  color: #495057;
  font-size: 0.875rem;
}

.field-value {
  padding: 0.5rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #dee2e6;
  color: #212529;
}

.field-value.text-area {
  min-height: 80px;
  white-space: pre-wrap;
}

.form-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #dee2e6;
}

.form-section h6 {
  margin: 0 0 1rem;
  color: #495057;
  font-size: 1rem;
}

.badge-text {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 600;
}

.badge-text.success {
  background-color: #d4edda;
  color: #155724;
}

.badge-text.danger {
  background-color: #f8d7da;
  color: #721c24;
}

.badge-text.warning {
  background-color: #fff3cd;
  color: #856404;
}

.badge-text.info {
  background-color: #d1ecf1;
  color: #0c5460;
}

.badge-text.default {
  background-color: #e2e3e5;
  color: #383d41;
}

.pdf-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #dee2e6;
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

/* Estilos para el modal de archivo */
.archivo-details-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.details-section {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
}

.details-section h3 {
  margin: 0;
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  color: #495057;
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border-bottom: 1px solid #dee2e6;
}

.details-section h3 i {
  font-size: 1.2rem;
  opacity: 0.8;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  padding: 0;
}

.detail-item {
  display: flex;
  flex-direction: column;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid #f1f5f9;
  border-right: 1px solid #f1f5f9;
}

.detail-item:nth-child(even) {
  border-right: none;
}

.detail-item:last-child,
.detail-item:nth-last-child(2):nth-child(odd) {
  border-bottom: none;
}

.detail-item.full-width {
  grid-column: 1 / -1;
  border-right: none;
}

.ruta-completa {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.85rem;
  background: #f8f9fa;
  padding: 0.75rem;
  border-radius: 4px;
  border: 1px solid #dee2e6;
  max-height: 120px;
  overflow-y: auto;
  word-break: break-all;
  line-height: 1.4;
}

.observaciones-content {
  padding: 1rem 1.25rem;
  font-size: 0.95rem;
  line-height: 1.5;
  color: #495057;
}

.archivo-type-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
  border-radius: 16px;
  font-size: 0.85rem;
  font-weight: 600;
}

.mt-3 {
  margin-top: 1rem;
}

.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.col-12 {
  grid-column: 1 / -1;
}

/* Responsive */
@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .tab-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .tab-filters {
    flex-direction: column;
    width: 100%;
  }
  
  .search-box {
    max-width: none;
  }
  
  .clasificaciones-grid,
  .archivos-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-tabs {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .notification {
    right: 1rem;
    left: 1rem;
    min-width: auto;
  }
  
  .modal-dialog {
    margin: 0.5rem;
    max-width: calc(100% - 1rem);
  }
  
  .modal-dialog.modal-lg {
    max-width: calc(100% - 1rem);
  }
  
  .row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-item {
    border-right: none;
  }
}
</style>