<template>
  <div class="insumos-list-page">
    <!-- Cabecera con título y acciones principales -->
    <div class="page-header">
      <div class="header-content">
        <h1>Gestión de Insumos</h1>
        <div class="header-actions">
          <button @click="exportarDatos" class="btn-outline">
            <i class="material-icons">file_download</i>
            Exportar
          </button>
        </div>
      </div>
    </div>

    <!-- Panel de búsqueda y filtros avanzados -->
    <div class="filters-panel">
      <div class="search-filters-container">
        <!-- Búsqueda global -->
        <div class="global-search">
          <i class="material-icons">search</i>
          <input 
            type="text"
            v-model="searchTerm"
            placeholder="Buscar municipio, insumo, categoría..."
            @input="handleSearchInput"
          />
          <button v-if="searchTerm" @click="clearSearch" class="clear-btn">
            <i class="material-icons">close</i>
          </button>
        </div>

        <!-- Filtros principales -->
        <div class="filters-row">
          <div class="filter-item">
            <label>Departamento:</label>
            <select v-model="filters.departamento" @change="handleDepartamentoChange">
              <option value="">Todos los departamentos</option>
              <option v-for="dpto in departamentosDisponibles" :key="dpto.cod_depto" :value="dpto.cod_depto">
                {{ dpto.nom_depto }}
              </option>
            </select>
          </div>

          <div class="filter-item">
            <label>Municipio:</label>
            <select v-model="filters.municipio" @change="handleMunicipioChange">
              <option value="">Todos los municipios</option>
              <option v-for="municipio in municipiosDisponibles" :key="municipio.cod_municipio" :value="municipio.cod_municipio">
                {{ municipio.nom_municipio }}
              </option>
            </select>
          </div>

          <div class="filter-item">
            <label>Territorial:</label>
            <select v-model="filters.territorial" @change="handleFilter">
              <option value="">Todas las territoriales</option>
              <option v-for="territorial in territorialesDisponibles" :key="territorial.nom_territorial" :value="territorial.nom_territorial">
                {{ territorial.nom_territorial }}
              </option>
            </select>
          </div>
        </div>

        <!-- Filtros adicionales -->
        <div class="filters-row">
          <div class="filter-item">
            <label>Mecanismo General:</label>
            <select v-model="filters.mecanismoGeneral" @change="handleFilter">
              <option value="">Todos</option>
              <option v-for="mecanismo in mecanismosGeneralesDisponibles" :key="mecanismo.cod_mecanismo" :value="mecanismo.cod_mecanismo">
                {{ mecanismo.cod_mecanismo }}
              </option>
            </select>
          </div>

            <div class="filter-item">
            <label>Mecanismo Detalle:</label>
            <select v-model="filters.mecanismoDetalle" @change="handleFilter">
              <option value="">Todos</option>
              <option 
                v-for="mecanismo in mecanismosDetalleDisponibles" 
                :key="mecanismo.cod_mecanismo_detalle" 
                :value="mecanismo.cod_mecanismo_detalle"
              >
                {{ mecanismo.cod_mecanismo_detalle }}
              </option>
            </select>
          </div>

          <div class="filter-item">
            <label>Grupo:</label>
            <select v-model="filters.grupo" @change="handleFilter">
              <option value="">Todos</option>
              <option v-for="grupo in gruposDisponibles" :key="grupo.cod_grupo" :value="grupo.cod_grupo">
                {{ grupo.descripcion || grupo.cod_grupo }}
              </option>
            </select>
          </div>

          <div class="filter-actions">
            <button @click="clearAllFilters" class="clear-filters-btn">
              <i class="material-icons">filter_alt_off</i>
              Limpiar filtros
            </button>
            
            <button @click="refreshData" class="refresh-btn" :disabled="loading">
              <i class="material-icons">refresh</i>
              Actualizar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Estados de carga y errores -->
    <div v-if="loading" class="loading-indicator">
      <div class="spinner"></div>
      <span>Cargando datos...</span>
    </div>

    <div v-else-if="error" class="error-message">
      <i class="material-icons">error</i>
      <p>{{ error }}</p>
      <button @click="refreshData" class="btn-primary">Reintentar</button>
    </div>

    <!-- Vista de datos para municipios filtrados -->
    <div v-else-if="filteredMunicipios.length === 0 && !selectedMunicipioId" class="empty-state">
      <i class="material-icons">search_off</i>
      <p>No se encontraron municipios con los criterios seleccionados.</p>
      <button @click="clearAllFilters" class="btn-secondary">Limpiar filtros</button>
    </div>

    <!-- Contenido principal -->
    <div v-else class="main-content">
      <!-- Vista de lista de municipios si no hay municipio seleccionado -->
      <div v-if="!selectedMunicipioId" class="municipios-table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Código</th>
              <th>Municipio</th>
              <th>Departamento</th>
              <th>Territorial</th>
              <th>Mecanismo</th>
              <th>Grupo</th>
              <th>Área</th>
              <th>Fecha Inicio</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="municipio in paginatedMunicipios" :key="municipio.cod_municipio">
              <td>{{ municipio.cod_municipio }}</td>
              <td>{{ municipio.nom_municipio }}</td>
              <td>{{ getNombreDepartamento(municipio.cod_depto) }}</td>
              <td>{{ municipio.nom_territorial || 'No asignada' }}</td>
              <td>{{ municipio.mecanismo_general || '-' }}</td>
              <td>{{ municipio.grupo || '-' }}</td>
              <td>{{ municipio.area || '-' }}</td>
              <td>{{ formatDate(municipio.fecha_inicio) }}</td>
              <td>
                <div class="row-actions">
                  <button @click="selectMunicipio(municipio.cod_municipio)" class="btn-icon primary" title="Ver detalle">
                    <i class="material-icons">visibility</i>
                  </button>

                  <button 
                    @click="descargarInsumos(municipio)" 
                    class="btn-action btn-success"
                    title="Descargar reporte de insumos"
                    :disabled="descargandoInsumos[municipio.cod_municipio]"
                  >
                    <i class="material-icons">
                      {{ descargandoInsumos[municipio.cod_municipio] ? 'hourglass_empty' : 'inventory_2' }}
                    </i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Paginación para la tabla de municipios -->
        <div class="pagination" v-if="filteredMunicipios.length > pageSize">
          <button 
            @click="prevPage" 
            :disabled="currentPage === 1" 
            class="pagination-button"
          >
            <i class="material-icons">chevron_left</i>
          </button>
          
          <span 
            v-for="page in displayedPages" 
            :key="page" 
            :class="['page-number', { active: currentPage === page }]"
            @click="goToPage(page)"
          >
            {{ page }}
          </span>
          
          <button 
            @click="nextPage" 
            :disabled="currentPage === totalPages" 
            class="pagination-button"
          >
            <i class="material-icons">chevron_right</i>
          </button>
        </div>
      </div>

      <div v-else class="municipio-detail">
        <div class="detail-header">
          <button @click="clearSelectedMunicipio" class="back-button">
            <i class="material-icons">arrow_back</i>
            Volver a la lista
          </button>
          <h2>{{ selectedMunicipio ? selectedMunicipio.nom_municipio : 'Cargando...' }}</h2>
          <div class="detail-actions">
          </div>
        </div>

        <!-- Pestañas para la información detallada -->
        <div class="detail-tabs">
          <div 
            v-for="tab in detailTabs" 
            :key="tab.id"
            :class="['tab', { active: activeTab === tab.id }]"
            @click="activeTab = tab.id">
            <i class="material-icons">{{ tab.icon }}</i>
            {{ tab.label }}
          </div>
        </div>

        <!-- Contenido de las pestañas -->
        <div class="tab-content">
          <!-- Pestaña de Resumen -->
          <div v-if="activeTab === 'resumen'" class="resumen-tab">
            <div class="info-cards">
              <div class="info-card">
                <h3>Información General</h3>
                <div class="info-grid">
                  <div class="info-item">
                    <span class="info-label">Código:</span>
                    <span class="info-value">{{ selectedMunicipio.cod_municipio }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Nombre:</span>
                    <span class="info-value">{{ selectedMunicipio.nom_municipio }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Departamento:</span>
                    <span class="info-value">{{ getNombreDepartamento(selectedMunicipio.cod_depto) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Fecha de Inicio:</span>
                    <span class="info-value">{{ formatDate(selectedMunicipio.fecha_inicio) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Área:</span>
                    <span class="info-value">{{ selectedMunicipio.area || 'No especificada' }}</span>
                  </div>
                </div>
              </div>
              
              <div class="info-card">
                <h3>Información Operativa</h3>
                <div class="info-grid">
                  <div class="info-item">
                    <span class="info-label">Territorial:</span>
                    <span class="info-value">{{ selectedMunicipio.nom_territorial || 'No asignada' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Mecanismo General:</span>
                    <span class="info-value">{{ selectedMunicipio.mecanismo_general || 'No asignado' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Mecanismo Detalle:</span>
                    <span class="info-value">{{ selectedMunicipio.mecanismo_detalle || 'No asignado' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Alcance Operación:</span>
                    <span class="info-value">{{ selectedMunicipio.alcance_operacion || 'No asignado' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Grupo:</span>
                    <span class="info-value">{{ selectedMunicipio.grupo || 'No asignado' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Mecanismo Operación:</span>
                    <span class="info-value">{{ selectedMunicipio.mecanismo_operacion || 'No asignado' }}</span>
                  </div>
                </div>
              </div>

              <!-- Estadísticas de Categorias mejoradas -->
              <div class="info-card">
                <h3>Estadísticas de Categorias</h3>
                <div class="stats-container">
                  <div class="stat-item">
                    <div class="stat-icon">
                      <i class="material-icons">folder</i>
                    </div>
                    <div class="stat-value">{{ municipioInsumos.length }}</div>
                    <div class="stat-label">Total Insumos</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-icon">
                      <i class="material-icons">category</i>
                    </div>
                    <div class="stat-value">{{ municipioClasificaciones.length }}</div>
                    <div class="stat-label">Clasificaciones</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-icon">
                      <i class="material-icons">description</i>
                    </div>
                    <div class="stat-value">{{ municipioDetalles.length }}</div>
                    <div class="stat-label">Detalles</div>
                  </div>
                </div>
              </div>

              <div class="info-card">
                <h3>Insumos por Categoría</h3>
                <div class="category-container">
                  <div v-if="Object.keys(insumosPorCategoria).length === 0" class="empty-message">
                    No hay datos de categorías disponibles
                  </div>
                  <div v-else class="category-links">
                    <div v-for="(info, categoria) in insumosPorCategoria" :key="categoria" class="category-link-item">
                      <a href="#" @click.prevent="irAInsumosPorCategoria(info.id)" class="category-link">
                        <i class="material-icons">folder</i>
                        {{ categoria }}
                      </a>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Profesionales asignados añadidos -->
              <div class="info-card">
                <h3><i class="material-icons">people</i> Profesionales Asignados</h3>
                <div v-if="municipioProfesionales.length === 0" class="empty-message">
                  <i class="material-icons">person_off</i>
                  No hay profesionales asignados a este municipio.
                </div>
                <div v-else class="profesionales-list">
                  <div v-for="prof in municipioProfesionales" :key="prof.cod_profesional" class="profesional-card">
                    <div class="profesional-avatar">
                      <i class="material-icons">person</i>
                    </div>
                    <div class="profesional-info">
                      <div class="profesional-name">{{ prof.nombre_profesional }}</div>
                      <div class="profesional-role">{{ prof.rol_profesional }}</div>
                      <div v-if="prof.correo_profesional" class="profesional-email">
                        <i class="material-icons">email</i>
                        {{ prof.correo_profesional }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Pestaña de Insumos -->
          <div v-else-if="activeTab === 'insumos'" class="insumos-tab">
            <div class="tab-actions">
              <div class="search-box">
                <i class="material-icons">search</i>
                <input 
                  type="text"
                  v-model="insumoSearch"
                  placeholder="Buscar insumo..."
                />
                <button v-if="insumoSearch" @click="insumoSearch = ''" class="clear-btn">
                  <i class="material-icons">close</i>
                </button>
              </div>
              
              <div class="filter-item">
                <label>Filtrar por categoría:</label>
                <select v-model="insumoFilter">
                  <option value="">Todas las categorías</option>
                  <option 
                    v-for="categoria in categorias" 
                    :key="categoria.cod_categoria" 
                    :value="categoria.cod_categoria"
                  >
                    {{ categoria.nom_categoria }}
                  </option>
                </select>
              </div>
              
              <div class="filter-item">
                <label>Filtrar por tipo:</label>
                <select v-model="tipoInsumoFilter">
                  <option value="">Todos los tipos</option>
                  <option 
                    v-for="tipo in tiposInsumo" 
                    :key="tipo.tipo_insumo" 
                    :value="tipo.tipo_insumo"
                  >
                    {{ tipo.tipo_insumo }}
                  </option>
                </select>
              </div>
            </div>
            
            <div v-if="municipioInsumos.length === 0" class="empty-message">
              No hay insumos registrados para este municipio.
              <button 
                v-if="authStore.isAnyAdmin"
                @click="showCreateInsumoForMunicipio(selectedMunicipioId)" 
                class="btn-primary"
              >
                <i class="material-icons">add</i>
                Nuevo Insumo
              </button>
            </div>

            <div class="insumos-grid">
              <div 
                v-for="insumo in filteredInsumos" 
                :key="insumo.cod_insumo" 
                class="insumo-card"
              >
                <div class="insumo-header">
                  <div class="insumo-icon">
                    <i class="material-icons">
                      {{ insumo.tipo_insumo === 'Primario' ? 'folder_special' : 'folder_shared' }}
                    </i>
                  </div>
                  <div class="insumo-title">
                    <h4>Insumo {{ insumo.cod_insumo }}</h4>
                    <span :class="['categoria-badge', getCategoriaClass(insumo.cod_categoria)]">
                      {{ getNombreCategoria(insumo.cod_categoria) }}
                    </span>
                  </div>
                  <div class="insumo-actions">
                  </div>
                </div>
                
                <div class="insumo-body">
                  <div class="insumo-details">
                    <div class="detail-row">
                      <span class="detail-label">Tipo:</span>
                      <span class="detail-value">
                        {{ getTipoInsumoNombre(insumo.tipo_insumo) }}
                      </span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">Clasificaciones:</span>
                      <span class="detail-value">{{ getClasificacionesCount(insumo.cod_insumo) }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">Detalles:</span>
                      <span class="detail-value">{{ getDetallesCountForInsumo(insumo.cod_insumo) }}</span>
                    </div>
                  </div>
                  
                  <div class="clasificaciones-list" v-if="getTodasLasClasificaciones(insumo.cod_insumo).length > 0">
                    <h5>Clasificaciones:</h5>
                    <div v-for="clasif in getTodasLasClasificaciones(insumo.cod_insumo)" 
                        :key="clasif.cod_clasificacion || clasif.nombre" 
                        class="clasificacion-item">
                      <i class="material-icons">label</i>
                      <span class="clasificacion-nombre">{{ clasif.nombre }}</span>
                    </div>
                  </div>
                </div>
                
                <div class="insumo-footer">
                  <button @click="viewInsumoDetails(insumo)" class="btn-text">
                    Ver detalle completo
                    <i class="material-icons">arrow_forward</i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Pestaña de Clasificaciones -->
          <div v-else-if="activeTab === 'clasificaciones'" class="clasificaciones-tab">
            <div v-if="municipioClasificaciones.length === 0" class="empty-message">
              No hay clasificaciones registradas para este municipio.
            </div>
              <div class="clasificaciones-list-detailed">
                <div 
                  v-for="clasificacion in filteredClasificaciones" 
                  :key="clasificacion.cod_clasificacion" 
                  class="clasificacion-card"
                >
                  <div class="clasificacion-header">
                    <div class="clasificacion-title">
                      <h4 class="clasificacion-nombre">{{ clasificacion.nombre }}</h4>
                      <span class="insumo-code">Insumo {{ clasificacion.cod_insumo }}</span>
                    </div>
                  </div>
                  
                  <div class="clasificacion-body">
                    <div class="detail-row">
                      <span class="detail-label">Código:</span>
                      <span class="detail-value">{{ clasificacion.cod_clasificacion }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">Categoría:</span>
                      <span class="detail-value">
                        <span :class="['categoria-badge-small', getCategoriaClass(getInsumoCategoria(clasificacion.cod_insumo))]">
                          {{ getNombreCategoriaByInsumo(clasificacion.cod_insumo) }}
                        </span>
                      </span>
                    </div>
                    <!-- If it's Cartografia Basica, show the subtype -->
                    <div class="detail-row" v-if="isCartografiaBasica(clasificacion.cod_insumo) && clasificacion.ruta">
                      <span class="detail-label">Tipo:</span>
                      <span class="detail-value">{{ getCartografiaSubtipo(clasificacion.ruta) }}</span>
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
                    <button @click="viewClasificacionDetalles(clasificacion)" class="btn-text">
                      Ver detalles asociados ({{ getDetallesCount(clasificacion.cod_clasificacion) }})
                      <i class="material-icons">arrow_forward</i>
                    </button>
                  </div>
                </div>
              </div>
          </div>
          
          <!-- ✅ ✅ ✅ PESTAÑA DE DETALLES MODIFICADA ✅ ✅ ✅ -->
<div v-else-if="activeTab === 'detalles'" class="detalles-tab">
  <div class="tab-actions">
    <!-- Búsqueda general -->
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
    
    <!-- Filtro por Zona -->
    <div class="filter-item">
      <label>Zona:</label>
      <select v-model="filtroZonaDetalle" @change="handleZonaDetalleChange">
        <option value="">Todas las zonas</option>
        <option v-for="zona in zonasUnicasDetalles" :key="zona" :value="zona">
          {{ zona }}
        </option>
      </select>
    </div>
    
    <!-- Filtro por Centro Poblado (solo si zona es CENTROS POBLADOS) -->
    <div class="filter-item" v-if="filtroZonaDetalle === 'CENTROS POBLADOS'">
      <label>Centro Poblado:</label>
      <select v-model="filtroCentroPobladoDetalle">
        <option value="">Todos los centros poblados</option>
        <option 
          v-for="centro in centrosPobladosUnicosDetalles" 
          :key="centro.codigo" 
          :value="centro.codigo"
        >
          {{ centro.nombre }}
        </option>
      </select>
    </div>
    
    <!-- Filtro por Clasificación -->
    <div class="filter-item">
      <label>Clasificación:</label>
      <select v-model="filtroClasificacionDetalle">
        <option value="">Todas las clasificaciones</option>
        <option 
          v-for="clasif in clasificacionesUnicasDetalles" 
          :key="clasif.codigo" 
          :value="clasif.codigo"
        >
          {{ clasif.nombre }}
        </option>
      </select>
    </div>
    
    <!-- Filtro por Formato -->
    <div class="filter-item">
      <label>Formato:</label>
      <select v-model="filtroFormatoDetalle">
        <option value="">Todos los formatos</option>
        <option v-for="formato in formatosUnicosDetalles" :key="formato" :value="formato">
          {{ formato }}
        </option>
      </select>
    </div>
    
    <!-- Botón para limpiar filtros -->
    <button 
      v-if="hayFiltrosActivosDetalles" 
      @click="limpiarFiltrosDetalles" 
      class="clear-filters-btn"
    >
      <i class="material-icons">filter_alt_off</i>
      Limpiar filtros
    </button>
  </div>
  
  <!-- Indicador de filtros activos -->
  <div v-if="hayFiltrosActivosDetalles" class="filtros-activos-info">
    <div class="filtros-activos-content">
      <i class="material-icons">filter_list</i>
      <span>Filtros activos:</span>
      <div class="filtros-tags">
        <span v-if="filtroZonaDetalle" class="filtro-tag">
          Zona: {{ filtroZonaDetalle }}
          <button @click="filtroZonaDetalle = ''" class="tag-close">×</button>
        </span>
        <span v-if="filtroCentroPobladoDetalle" class="filtro-tag">
          Centro: {{ centrosPobladosUnicosDetalles.find(c => c.codigo === filtroCentroPobladoDetalle)?.nombre }}
          <button @click="filtroCentroPobladoDetalle = ''" class="tag-close">×</button>
        </span>
        <span v-if="filtroClasificacionDetalle" class="filtro-tag">
          Clasificación: {{ getNombreClasificacion(filtroClasificacionDetalle) }}
          <button @click="filtroClasificacionDetalle = ''" class="tag-close">×</button>
        </span>
        <span v-if="filtroFormatoDetalle" class="filtro-tag">
          Formato: {{ filtroFormatoDetalle }}
          <button @click="filtroFormatoDetalle = ''" class="tag-close">×</button>
        </span>
      </div>
      <span class="resultados-count">
        Mostrando {{ filteredDetalles.length }} de {{ municipioDetalles.length }} registros
      </span>
    </div>
  </div>
  
  <!-- ✅ AQUÍ ESTÁ LA CORRECCIÓN PRINCIPAL -->
  <div v-if="filteredDetalles.length === 0" class="empty-message">
    <i class="material-icons">search_off</i>
    <p>No se encontraron detalles con los filtros seleccionados.</p>
    <button v-if="hayFiltrosActivosDetalles" @click="limpiarFiltrosDetalles" class="btn-secondary">
      Limpiar filtros
    </button>
  </div>
  
  <!-- ✅ TABLA USANDO filteredDetalles EN LUGAR DE municipioDetalles -->
  <div v-else class="detalles-table-container">
    <table class="data-table">
      <thead>
        <tr>
          <th>Código</th>
          <th>Clasificación</th>
          <th>Escala</th>
          <th>Estado</th>
          <th>Entidad</th>
          <th>Zona / Centro Poblado</th>
          <th>Formato</th>
          <th v-if="authStore.isAnyAdmin">Acciones</th>
        </tr>
      </thead>
      <tbody>
        <!-- ✅ USAR filteredDetalles AQUÍ -->
        <tr v-for="detalle in filteredDetalles" :key="detalle.cod_detalle">
          <td>{{ detalle.cod_detalle }}</td>
          <td>{{ getNombreClasificacion(detalle.cod_clasificacion) }}</td>
          <td>{{ detalle.escala || '-' }}</td>
          <td>{{ detalle.estado || '-' }}</td>
          <td>{{ getNombreEntidad(detalle.cod_entidad) }}</td>
          
          <td>
            <span 
              class="zona-info"
              :class="{
                'zona-urbano': detalle.zona === 'URBANO',
                'zona-rural': detalle.zona === 'RURAL', 
                'zona-centro-poblado': detalle.zona === 'CENTROS POBLADOS'
              }"
              :title="detalle.zona === 'CENTROS POBLADOS' ? `Centro Poblado: ${detalle.centro_poblado_nombre || 'Cargando...'}` : detalle.zona"
            >
              {{ formatZonaConCentroPoblado(detalle) }}
            </span>
          </td>
          
          <td>
            <span class="formato-badge">
              {{ detalle.formato_tipo || '-' }}
            </span>
          </td>
          
          <td v-if="authStore.isAnyAdmin">
            <div class="row-actions">
              <button @click="showDetalleModal(detalle)" class="btn-icon small primary" title="Ver detalle">
                <i class="material-icons">visibility</i>
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    
    <!-- Mensaje cuando la tabla está vacía después de filtrar -->
    <div v-if="filteredDetalles.length === 0 && municipioDetalles.length > 0" class="no-results-message">
      <p>No se encontraron detalles que coincidan con los filtros seleccionados.</p>
    </div>
  </div>
</div>
          
          <!-- Nueva Pestaña de Conceptos -->
          <div v-else-if="activeTab === 'conceptos'" class="conceptos-tab">
            <div class="tab-header">
              <h3>Conceptos Asociados</h3>
            </div>
            
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
            </div>
            
            <div v-if="conceptosLoading" class="loading-state">
              <div class="spinner"></div>
              <p>Cargando conceptos...</p>
            </div>
            
            <div v-else-if="conceptosError" class="error-state">
              <i class="material-icons">error</i>
              <p>{{ conceptosError }}</p>
              <button @click="cargarConceptos" class="btn-primary">Reintentar</button>
            </div>
            
            <div v-else-if="municipioConceptos.length === 0" class="empty-message">
              <i class="material-icons">comment</i>
              <p>No hay conceptos registrados para este municipio.</p>
            </div>
            
            <div v-else>
              <div class="conceptos-list">
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
                    <!-- Información estructurada en forma de tabla -->
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
                    
                    <!-- Detalle del concepto si existe -->
                    <div v-if="concepto.detalle_concepto" class="concepto-detail-section">
                      <div class="concepto-detail-header">Detalle del concepto:</div>
                      <div class="concepto-detail-content">{{ concepto.detalle_concepto }}</div>
                    </div>
                    
                    <!-- Observación si existe -->
                    <div v-if="concepto.observacion" class="concepto-observation-section">
                      <div class="concepto-observation-header">Observación:</div>
                      <div class="concepto-observation-content">{{ concepto.observacion }}</div>
                    </div>

                  </div>
                  
                  <div class="concepto-footer">
                    <button v-if="concepto.pdf" @click="verDocumentoPDF(concepto.pdf)" class="btn-text">
                      Ver documento PDF en nueva ventana
                      <i class="material-icons">open_in_new</i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
<!-- ✅ PESTAÑA DE ARCHIVOS CORREGIDA -->
<div v-else-if="activeTab === 'archivos'" class="archivos-tab">
  <div class="tab-header">
    <h3>Archivos Asociados</h3>
  </div>
  
  <!-- Tabs para seleccionar tipo de archivos -->
  <div class="archivos-inner-tabs">
    <button 
      :class="['inner-tab', { active: activeArchivosTab === 'preoperacion' }]"
      @click="activeArchivosTab = 'preoperacion'"
    >
      <i class="material-icons">folder_open</i>
      Archivos Preoperación ({{ filteredArchivosPre.length }})
    </button>
    <button 
      :class="['inner-tab', { active: activeArchivosTab === 'postoperacion' }]"
      @click="activeArchivosTab = 'postoperacion'"
    >
      <i class="material-icons">folder_shared</i>
      Archivos Postoperación ({{ filteredArchivosPost.length }})
    </button>
  </div>
  
  <!-- CONTENIDO DE PREOPERACIÓN -->
  <div v-if="activeArchivosTab === 'preoperacion'" class="archivos-content">
    <!-- Filtros para preoperación con estilos originales -->
    <div class="tab-actions">
      <div class="filter-item">
        <label>Filtrar por clasificación:</label>
        <select v-model="filtroClasificacionPre" @change="handleClasificacionPreChange">
          <option value="">Todas las clasificaciones</option>
          <option v-for="clasif in clasificacionesUnicasPre" :key="clasif" :value="clasif">
            {{ clasif }}
          </option>
        </select>
      </div>
      
      <!-- Filtros condicionales para Cartografía Básica -->
      <div v-if="mostrarFiltrosCartografiaBasica" class="filter-item">
        <label>Centro Poblado:</label>
        <select v-model="filtroCentroPoblado">
          <option value="">Todos los centros</option>
          <option 
            v-for="centro in centrosPobladosConArchivos" 
            :key="centro.cod_centro_poblado" 
            :value="extraerCodigoCentroPoblado(centro.cod_centro_poblado)"
          >
            {{ centro.nom_centro_poblado }}
          </option>
        </select>
      </div>
      
      <div v-if="mostrarFiltrosCartografiaBasica" class="filter-item">
        <label>Tipo Cartografía:</label>
        <select v-model="filtroTipoCartografia">
          <option value="">Todos los tipos</option>
          <option value="Vectorial">Vectorial</option>
          <option value="Ortofoto">Ortofoto</option>
          <option value="Modelo Digital">Modelo Digital</option>
        </select>
      </div>
      
      <!-- Filtros para Información Catastral -->
      <div v-if="mostrarFiltrosInfoCatastral" class="filter-item">
        <label>Tipo Info Catastral:</label>
        <select v-model="filtroTipoInfoCatastral">
          <option value="">Todos los tipos</option>
          <option v-for="tipo in tiposInfoCatastralUnicos" :key="tipo" :value="tipo">
            {{ tipo }}
          </option>
        </select>
      </div>
      
      <div class="filter-item">
        <label>Filtrar por nombre:</label>
        <div class="search-box">
          <i class="material-icons">search</i>
          <input 
            type="text"
            v-model="filtroNombreArchivoPre"
            placeholder="Buscar por nombre..."
          />
          <button v-if="filtroNombreArchivoPre" @click="filtroNombreArchivoPre = ''" class="clear-btn">
            <i class="material-icons">close</i>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Estados de carga y error -->
    <div v-if="archivosPreLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando archivos de preoperación...</p>
    </div>
    
    <div v-else-if="archivosPreError" class="error-state">
      <i class="material-icons">error</i>
      <p>{{ archivosPreError }}</p>
      <button @click="cargarArchivosPre" class="btn-primary">Reintentar</button>
    </div>
    
    <div v-else-if="municipioArchivos.length === 0" class="empty-message">
      <i class="material-icons">folder_off</i>
      <p>No hay archivos de preoperación para este municipio.</p>
    </div>
    
    <div v-else-if="filteredArchivosPre.length === 0" class="empty-message">
      <i class="material-icons">search_off</i>
      <p>No se encontraron archivos con los filtros seleccionados.</p>
      <button @click="limpiarFiltrosPreoperacion" class="btn-secondary">
        Limpiar filtros
      </button>
    </div>
    
    <!-- ✅ TABLA DE PREOPERACIÓN CON COLUMNAS CORRECTAS -->
    <div v-else class="table-responsive">
      <table class="data-table">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Clasificación</th>
            <th>Fecha</th>
            <th>Peso Memoria</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="archivo in filteredArchivosPre" :key="archivo.cod_archivopre">
            <td>
              <div class="file-info">
                <i class="material-icons file-icon">{{ getFileIcon(archivo.nombre_insumo) }}</i>
                <span :title="archivo.nombre_insumo">{{ getShortFileName(archivo.nombre_insumo, 40) }}</span>
              </div>
            </td>
            <td>{{ getNombreClasificacion(archivo.cod_insumo) || 'N/A' }}</td>
            <td>{{ formatDate(archivo.fecha_disposicion) }}</td>
            <td>
              <span v-if="archivo.peso_memoria" :class="['peso-memoria-badge', getPesoMemoriaClass(archivo.peso_memoria)]">
                {{ formatPesoMemoria(archivo.peso_memoria) }}
              </span>
              <span v-else>-</span>
            </td>
            <td>
              <div class="row-actions">
                <button 
                  @click="viewArchivo(archivo)" 
                  class="btn-icon small primary"
                  title="Ver archivo"
                >
                  <i class="material-icons">visibility</i>
                </button>
                <button 
                  @click="downloadArchivo(archivo)" 
                  class="btn-icon small success"
                  title="Descargar archivo"
                >
                  <i class="material-icons">download</i>
                </button>
                <button 
                  @click="showArchivoDetails(archivo, 'pre')" 
                  class="btn-icon small info"
                  title="Ver detalles"
                >
                  <i class="material-icons">info</i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  
<!-- ✅ SECCIÓN DE POSTOPERACIÓN CON FILTROS POR NIVELES -->
<div v-if="activeArchivosTab === 'postoperacion'" class="archivos-content">
  <!-- Filtros dinámicos por niveles de carpetas -->
  <div class="tab-actions">
    <!-- Filtro Nivel 1 -->
    <div v-if="opcionesNivel1Post.length > 0" class="filter-item">
      <label>Directorio Nivel 1:</label>
      <select v-model="filtrosNivelesPost.nivel1" @change="handleNivelChange(1)">
        <option value="">Todos</option>
        <option v-for="opcion in opcionesNivel1Post" :key="opcion" :value="opcion">
          {{ opcion }}
        </option>
      </select>
    </div>
    
    <!-- Filtro Nivel 2 (aparece solo si hay nivel 1 seleccionado) -->
    <div v-if="filtrosNivelesPost.nivel1 && opcionesNivel2Post.length > 0" class="filter-item">
      <label>Directorio Nivel 2:</label>
      <select v-model="filtrosNivelesPost.nivel2" @change="handleNivelChange(2)">
        <option value="">Todos</option>
        <option v-for="opcion in opcionesNivel2Post" :key="opcion" :value="opcion">
          {{ opcion }}
        </option>
      </select>
    </div>
    
    <!-- Filtro Nivel 3 -->
    <div v-if="filtrosNivelesPost.nivel2 && opcionesNivel3Post.length > 0" class="filter-item">
      <label>Directorio Nivel 3:</label>
      <select v-model="filtrosNivelesPost.nivel3" @change="handleNivelChange(3)">
        <option value="">Todos</option>
        <option v-for="opcion in opcionesNivel3Post" :key="opcion" :value="opcion">
          {{ opcion }}
        </option>
      </select>
    </div>
    
    <!-- Filtro Nivel 4 -->
    <div v-if="filtrosNivelesPost.nivel3 && opcionesNivel4Post.length > 0" class="filter-item">
      <label>Directorio Nivel 4:</label>
      <select v-model="filtrosNivelesPost.nivel4" @change="handleNivelChange(4)">
        <option value="">Todos</option>
        <option v-for="opcion in opcionesNivel4Post" :key="opcion" :value="opcion">
          {{ opcion }}
        </option>
      </select>
    </div>
    
    <!-- Filtro Nivel 5 -->
    <div v-if="filtrosNivelesPost.nivel4 && opcionesNivel5Post.length > 0" class="filter-item">
      <label>Directorio Nivel 5:</label>
      <select v-model="filtrosNivelesPost.nivel5" @change="handleNivelChange(5)">
        <option value="">Todos</option>
        <option v-for="opcion in opcionesNivel5Post" :key="opcion" :value="opcion">
          {{ opcion }}
        </option>
      </select>
    </div>
    
    <!-- Búsqueda por nombre -->
    <div class="filter-item">
      <label>Filtrar por nombre:</label>
      <div class="search-box">
        <i class="material-icons">search</i>
        <input 
          type="text"
          v-model="filtroNombreArchivoPost"
          placeholder="Buscar por nombre..."
        />
        <button v-if="filtroNombreArchivoPost" @click="filtroNombreArchivoPost = ''" class="clear-btn">
          <i class="material-icons">close</i>
        </button>
      </div>
    </div>
    
    <!-- Botón limpiar filtros -->
    <button 
      v-if="hayFiltrosActivosPost" 
      @click="limpiarFiltrosPostoperacion" 
      class="clear-filters-btn"
    >
      <i class="material-icons">filter_alt_off</i>
      Limpiar filtros
    </button>
  </div>
  
  <!-- Indicador de filtros activos -->
  <div v-if="hayFiltrosActivosPost" class="filtros-activos-info">
    <div class="filtros-activos-content">
      <i class="material-icons">folder_open</i>
      <span>Ruta filtrada:</span>
      <span class="ruta-filtrada">
        03_post
        <span v-if="filtrosNivelesPost.nivel1"> / {{ filtrosNivelesPost.nivel1 }}</span>
        <span v-if="filtrosNivelesPost.nivel2"> / {{ filtrosNivelesPost.nivel2 }}</span>
        <span v-if="filtrosNivelesPost.nivel3"> / {{ filtrosNivelesPost.nivel3 }}</span>
        <span v-if="filtrosNivelesPost.nivel4"> / {{ filtrosNivelesPost.nivel4 }}</span>
        <span v-if="filtrosNivelesPost.nivel5"> / {{ filtrosNivelesPost.nivel5 }}</span>
      </span>
      <span class="resultados-count">
        {{ filteredArchivosPost.length }} archivos
      </span>
    </div>
  </div>
  
  <!-- Estados de carga y error -->
  <div v-if="archivosPostLoading" class="loading-state">
    <div class="spinner"></div>
    <p>Cargando archivos de postoperación...</p>
  </div>
  
  <div v-else-if="archivosPostError" class="error-state">
    <i class="material-icons">error</i>
    <p>{{ archivosPostError }}</p>
    <button @click="loadArchivosPostForMunicipio(selectedMunicipioId)" class="btn-primary">Reintentar</button>
  </div>
  
  <div v-else-if="municipioArchivosPost.length === 0" class="empty-message">
    <i class="material-icons">folder_off</i>
    <p>No hay archivos de postoperación para este municipio.</p>
  </div>
  
  <div v-else-if="filteredArchivosPost.length === 0" class="empty-message">
    <i class="material-icons">search_off</i>
    <p>No se encontraron archivos en la ruta seleccionada.</p>
    <button @click="limpiarFiltrosPostoperacion" class="btn-secondary">
      Limpiar filtros
    </button>
  </div>
  
  <!-- ✅ TABLA CON COLUMNA DIRECTORIO EN LUGAR DE COMPONENTE -->
  <div v-else class="table-responsive">
    <table class="data-table">
      <thead>
        <tr>
          <th>Nombre</th>
          <th>Directorio</th> <!-- ✅ CAMBIADO DE COMPONENTE A DIRECTORIO -->
          <th>Fecha</th>
          <th>Peso Memoria</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="archivo in filteredArchivosPost" :key="archivo.cod_archivo">
          <td>
            <div class="file-info">
              <i class="material-icons file-icon">{{ getFileIcon(archivo.nombre_archivo) }}</i>
              <span :title="archivo.nombre_archivo">{{ getShortFileName(archivo.nombre_archivo, 40) }}</span>
            </div>
          </td>
          <td>
            <!-- ✅ MOSTRAR DIRECTORIO (CONVERTIDO A WINDOWS) -->
            <span class="directorio-path" :title="linuxToWindowsPath(archivo.disposicion_info?.directorio)">
              {{ linuxToWindowsPath(archivo.disposicion_info?.directorio) || 'No especificado' }}
            </span>
          </td>
          <td>{{ formatDate(archivo.fecha_disposicion) }}</td>
          <td>
            <span v-if="archivo.peso_memoria" :class="['peso-memoria-badge', getPesoMemoriaClass(archivo.peso_memoria)]">
              {{ formatPesoMemoria(archivo.peso_memoria) }}
            </span>
            <span v-else>-</span>
          </td>
          <td>
            <div class="row-actions">
              <button 
                @click="viewArchivoPost(archivo)" 
                class="btn-icon small primary"
                title="Ver archivo"
              >
                <i class="material-icons">visibility</i>
              </button>
              <button 
                @click="downloadArchivoPost(archivo)" 
                class="btn-icon small success"
                title="Descargar archivo"
              >
                <i class="material-icons">download</i>
              </button>
              <button 
                @click="showArchivoDetails(archivo, 'post')" 
                class="btn-icon small info"
                title="Ver detalles"
              >
                <i class="material-icons">info</i>
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

        <!-- ✅ ✅ ✅ MODAL DE DETALLE - AL FINAL DE TODO ✅ ✅ ✅ -->
<div v-if="detalleModalVisible" class="modal-overlay" @click="cerrarDetalleModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>📋 Detalle Completo - Código {{ detalleSeleccionado?.cod_detalle }}</h3>
        <button @click="cerrarDetalleModal" class="close-btn">
          <i class="material-icons">close</i>
        </button>
      </div>
      
      <div class="modal-body">
        <div v-if="detalleSeleccionado">
          <div class="detalle-info-grid">
            
            <!-- Información Básica -->
            <div class="info-section">
              <h4>🏷️ Información Básica</h4>
              
              <div class="info-item">
                <strong>Código Detalle:</strong>
                <span>{{ detalleSeleccionado.cod_detalle }}</span>
              </div>
              
              <div class="info-item">
                <strong>Clasificación:</strong>
                <span>{{ getNombreClasificacion(detalleSeleccionado.cod_clasificacion) }}</span>
              </div>
              
              <div class="info-item">
                <strong>Estado:</strong>
                <span class="estado-badge" :class="getEstadoClass(detalleSeleccionado.estado)">
                  {{ detalleSeleccionado.estado || 'Sin estado' }}
                </span>
              </div>
              
              <div class="info-item" v-if="detalleSeleccionado.escala">
                <strong>Escala:</strong>
                <span>{{ detalleSeleccionado.escala }}</span>
              </div>
              
              <div class="info-item" v-if="detalleSeleccionado.vigencia">
                <strong>Vigencia:</strong>
                <span>{{ detalleSeleccionado.vigencia }}</span>
              </div>
              
              <div class="info-item" v-if="detalleSeleccionado.formato_tipo">
                <strong>Formato:</strong>
                <span class="formato-badge">{{ detalleSeleccionado.formato_tipo }}</span>
              </div>
            </div>

            <!-- Información Geográfica -->
            <div class="info-section">
              <h4>🗺️ Información Geográfica</h4>
              
              <div class="info-item">
                <strong>Zona:</strong>
                <span class="zona-info" 
                      :class="{
                        'zona-urbano': detalleSeleccionado.zona === 'URBANO',
                        'zona-rural': detalleSeleccionado.zona === 'RURAL', 
                        'zona-centro-poblado': detalleSeleccionado.zona === 'CENTROS POBLADOS'
                      }">
                  {{ formatZonaConCentroPoblado(detalleSeleccionado) }}
                </span>
              </div>
              
              <div class="info-item" v-if="detalleSeleccionado.area">
                <strong>Área (km²):</strong>
                <span class="valor-monetario">{{ formatArea(detalleSeleccionado.area) }}</span>
              </div>
              
              <div class="info-item" v-if="detalleSeleccionado.cubrimiento">
                <strong>Cubrimiento (km²):</strong>
                <span class="valor-monetario">{{ formatArea(detalleSeleccionado.cubrimiento) }}</span>
              </div>
              
              <div class="info-item" v-if="detalleSeleccionado.porcentaje_cubrimiento">
                <strong>% Cubrimiento:</strong>
                <span class="valor-porcentaje">{{ detalleSeleccionado.porcentaje_cubrimiento }}%</span>
              </div>
              
              <div class="info-item" v-if="detalleSeleccionado.ruta_archivo">
                <strong>Ruta Archivo:</strong>
                <span class="valor-archivo">{{ linuxToWindowsPath(detalleSeleccionado.ruta_archivo) }}</span>
              </div>
            </div>

            <!-- Información Institucional -->
            <div class="info-section">
              <h4>🏢 Información Institucional</h4>
              
              <div class="info-item">
                <strong>Entidad:</strong>
                <span>{{ getNombreEntidad(detalleSeleccionado.cod_entidad) }}</span>
              </div>
              
            </div>

            <!-- Cronología -->
            <div class="info-section">
              <h4>📅 Cronología</h4>
              
              <div class="info-item" v-if="detalleSeleccionado.fecha_entrega">
                <strong>Fecha Entrega:</strong>
                <span class="valor-fecha">{{ formatDate(detalleSeleccionado.fecha_entrega) }}</span>
              </div>
              
              <div class="info-item" v-if="detalleSeleccionado.fecha_disposicion">
                <strong>Fecha Disposición:</strong>
                <span class="valor-fecha">{{ formatDate(detalleSeleccionado.fecha_disposicion) }}</span>
              </div>
            </div>

            <!-- Observaciones (si existe) -->
            <div class="info-section" v-if="detalleSeleccionado.observacion">
              <h4>📝 Observaciones</h4>
              
              <div class="info-item">
                <strong>Observación:</strong>
                <span>{{ detalleSeleccionado.observacion }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">

        <button @click="cerrarDetalleModal" class="btn btn-secondary">
          <i class="material-icons">close</i>
          Cerrar
        </button>
      </div>
    </div>
  </div>
      </div>
    </div>

    <!-- Modal para detalles de archivo añadido -->
    <div v-if="showArchivoDetailsModal" class="modal-backdrop" @click="closeArchivoDetailsModal">
      <div class="modal-container archivo-details-modal" @click.stop>
        <div class="modal-header">
          <h2>
            <i class="material-icons">info</i>
            Detalles del Archivo
          </h2>
          <button class="close-btn" @click="closeArchivoDetailsModal">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body" v-if="selectedArchivoDetails">
          <div class="archivo-details-content">
            <!-- Información básica -->
            <div class="details-section">
              <h3>
                <i class="material-icons">insert_drive_file</i>
                Información Básica
              </h3>
              <div class="details-grid">
                <div class="detail-item">
                  <span class="detail-label">Nombre del archivo:</span>
                  <span class="detail-value">
                    {{ archivoDetailsType === 'pre' ? selectedArchivoDetails.nombre_insumo : selectedArchivoDetails.nombre_archivo }}
                  </span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Tipo:</span>
                  <span class="detail-value archivo-type-badge" :class="archivoDetailsType">
                    {{ archivoDetailsType === 'pre' ? 'Preoperación' : 'Postoperación' }}
                  </span>
                </div>
                <!-- ✅ NUEVO: Agregar peso_memoria al modal -->
                <div class="detail-item">
                  <span class="detail-label">Peso en memoria:</span>
                  <span class="detail-value">
                    <span 
                      v-if="selectedArchivoDetails.peso_memoria"
                      :class="['peso-memoria-badge', 'large', getPesoMemoriaClass(selectedArchivoDetails.peso_memoria)]"
                    >
                      {{ formatPesoMemoria(selectedArchivoDetails.peso_memoria) }}
                    </span>
                    <span v-else class="sin-peso-memoria">No registrado</span>
                  </span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Extensión:</span>
                  <span class="detail-value">
                    .{{ getFileExtension(archivoDetailsType === 'pre' ? selectedArchivoDetails.nombre_insumo : selectedArchivoDetails.nombre_archivo).toUpperCase() }}
                  </span>
                </div>
              </div>
            </div>

            <!-- ✅ NUEVO: Agregar sección específica para observaciones (solo si existen) -->
            <div class="details-section" v-if="selectedArchivoDetails.observacion && selectedArchivoDetails.observacion.trim() !== ''">
              <h3>
                <i class="material-icons">comment</i>
                Observaciones Detalladas
              </h3>
              <div class="observaciones-detalladas">
                {{ selectedArchivoDetails.observacion }}
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
                  <span class="detail-value">{{ getArchivoExtraInfo(selectedArchivoDetails, archivoDetailsType).departamento }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Municipio:</span>
                  <span class="detail-value">{{ getArchivoExtraInfo(selectedArchivoDetails, archivoDetailsType).municipio }}</span>
                </div>
                <div class="detail-item full-width">
                  <span class="detail-label">Ruta completa:</span>
                  <div class="ruta-completa">
                    {{ linuxToWindowsPath(getArchivoExtraInfo(selectedArchivoDetails, archivoDetailsType).ruta) }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Información específica según tipo -->
            <div class="details-section" v-if="archivoDetailsType === 'pre'">
              <h3>
                <i class="material-icons">category</i>
                Información de Preoperación
              </h3>
              <div class="details-grid">
                <div class="detail-item">
                  <span class="detail-label">Clasificación:</span>
                  <span class="detail-value">{{ getArchivoExtraInfo(selectedArchivoDetails, archivoDetailsType).clasificacion }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Código insumo:</span>
                  <span class="detail-value">{{ selectedArchivoDetails.cod_insumo }}</span>
                </div>
              </div>
            </div>

            <div class="details-section" v-else>
              <h3>
                <i class="material-icons">assignment_turned_in</i>
                Información de Postoperación
              </h3>
              <div class="details-grid">
                <div class="detail-item">
                  <span class="detail-label">Componente:</span>
                  <span class="detail-value">{{ getArchivoExtraInfo(selectedArchivoDetails, archivoDetailsType).componente }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Aprobado:</span>
                  <span class="detail-value" :class="{ 'status-approved': getArchivoExtraInfo(selectedArchivoDetails, archivoDetailsType).aprobado === 'Sí' }">
                    {{ getArchivoExtraInfo(selectedArchivoDetails, archivoDetailsType).aprobado }}
                  </span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Dispuesto:</span>
                  <span class="detail-value" :class="{ 'status-approved': getArchivoExtraInfo(selectedArchivoDetails, archivoDetailsType).dispuesto === 'Sí' }">
                    {{ getArchivoExtraInfo(selectedArchivoDetails, archivoDetailsType).dispuesto }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Información temporal -->
            <div class="details-section">
              <h3>
                <i class="material-icons">schedule</i>
                Información Temporal
              </h3>
              <div class="details-grid">
                <div class="detail-item">
                  <span class="detail-label">Fecha de disposición:</span>
                  <span class="detail-value">{{ getArchivoExtraInfo(selectedArchivoDetails, archivoDetailsType).fecha_disposicion }}</span>
                </div>
              </div>
            </div>

            <!-- Observaciones -->
            <div class="details-section" v-if="getArchivoExtraInfo(selectedArchivoDetails, archivoDetailsType).observacion !== 'Sin observaciones'">
              <h3>
                <i class="material-icons">comment</i>
                Observaciones
              </h3>
              <div class="observaciones-content">
                {{ getArchivoExtraInfo(selectedArchivoDetails, archivoDetailsType).observacion }}
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeArchivoDetailsModal">Cerrar</button>
          <button class="btn-primary" @click="archivoDetailsType === 'pre' ? downloadArchivo(selectedArchivoDetails) : downloadArchivoPost(selectedArchivoDetails)">
            <i class="material-icons">download</i>
            Descargar archivo
          </button>
        </div>
      </div>
    </div>

    <!-- 🚀 NUEVOS MODALES DE DETALLE - AGREGAR AQUÍ -->
    
    <!-- Modal de detalles de insumo MEJORADO -->
    <div v-if="modalDetalleInsumo.mostrar" class="modal-overlay" @click="modalDetalleInsumo.mostrar = false">
      <div class="modal-content modal-detalle-insumo" @click.stop>
        <div class="modal-header">
          <h3>
            <i class="material-icons">folder_special</i>
            Detalle Completo - Insumo {{ modalDetalleInsumo.insumo?.cod_insumo }}
          </h3>
          <button class="btn-close" @click="modalDetalleInsumo.mostrar = false">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body" v-if="modalDetalleInsumo.insumo">
          <!-- Información básica del insumo -->
          <div class="seccion-info">
            <h4><i class="material-icons">info</i> Información Básica</h4>
            <div class="info-grid">
              <div class="info-item">
                <label>Código de Insumo:</label>
                <span>{{ modalDetalleInsumo.insumo.cod_insumo }}</span>
              </div>
              <div class="info-item">
                <label>Municipio:</label>
                <span>{{ selectedMunicipio?.nom_municipio || 'No disponible' }}</span>
              </div>
              <div class="info-item">
                <label>Departamento:</label>
                <span>{{ getNombreDepartamento(selectedMunicipio?.cod_depto) }}</span>
              </div>
              <div class="info-item">
                <label>Categoría:</label>
                <span :class="['categoria-badge', getCategoriaClass(modalDetalleInsumo.insumo.cod_categoria)]">
                  {{ getNombreCategoria(modalDetalleInsumo.insumo.cod_categoria) }}
                </span>
              </div>
              <div class="info-item">
                <label>Tipo de Insumo:</label>
                <span>{{ getTipoInsumoNombre(modalDetalleInsumo.insumo.tipo_insumo) }}</span>
              </div>
              <div class="info-item">
                <label>Total Clasificaciones:</label>
                <span class="stat-badge">{{ getClasificaciones(modalDetalleInsumo.insumo.cod_insumo).length }}</span>
              </div>
              <div class="info-item">
                <label>Total Detalles:</label>
                <span class="stat-badge">{{ getDetallesCountForInsumo(modalDetalleInsumo.insumo.cod_insumo) }}</span>
              </div>
            </div>
          </div>

          <!-- Clasificaciones del insumo -->
          <div v-if="getClasificaciones(modalDetalleInsumo.insumo.cod_insumo).length > 0" class="seccion-info">
  <h4><i class="material-icons">category</i> Clasificaciones Asociadas</h4>
  <div class="clasificaciones-grid">
    <div 
      v-for="clasificacion in getClasificacionesParaModal(modalDetalleInsumo.insumo.cod_insumo)"
      :key="clasificacion.cod_clasificacion"
      class="clasificacion-card-modal"
    >
      <div class="clasificacion-header-modal">
        <h5>{{ clasificacion.nombre }}</h5>
        <span class="clasificacion-code">{{ clasificacion.cod_clasificacion }}</span>
      </div>
      <div class="clasificacion-details">
        <div v-if="clasificacion.ruta" class="detail-row">
          <strong>Ruta:</strong>
          <span class="ruta-text">{{ linuxToWindowsPath(clasificacion.ruta) }}</span>
        </div>
        <div v-if="clasificacion.observacion" class="detail-row">
          <strong>Observación:</strong>
          <span>{{ clasificacion.observacion }}</span>
        </div>
        <div v-if="clasificacion.descripcion" class="detail-row">
          <strong>Descripción:</strong>
          <span>{{ clasificacion.descripcion }}</span>
        </div>
        <div class="detail-row">
          <strong>Detalles asociados:</strong>
          <span class="stat-badge">{{ getDetallesCount(clasificacion.cod_clasificacion) }}</span>
        </div>
      </div>
    </div>
  </div>
</div>

          <!-- Detalles más recientes -->
          <div v-if="getDetallesForInsumoModal(modalDetalleInsumo.insumo.cod_insumo).length > 0" class="seccion-info">
            <h4><i class="material-icons">description</i> Detalles Recientes</h4>
            <div class="detalles-tabla-modal">
              <table class="tabla-detalles">
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Clasificación</th>
                    <th>Estado</th>
                    <th>Entidad</th>
                    <th>Fecha Entrega</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="detalle in getDetallesForInsumoModal(modalDetalleInsumo.insumo.cod_insumo).slice(0, 5)" :key="detalle.cod_detalle">
                    <td>{{ detalle.cod_detalle }}</td>
                    <td>{{ getNombreClasificacion(detalle.cod_clasificacion) }}</td>
                    <td>
                      <span class="estado-badge" :class="getEstadoClass(detalle.estado)">
                        {{ detalle.estado || 'N/A' }}
                      </span>
                    </td>
                    <td>{{ getNombreEntidad(detalle.cod_entidad) }}</td>
                    <td>{{ formatDate(detalle.fecha_entrega) }}</td>
                    <td>
                      <button 
                        @click="verDetalleCompleto(detalle)"
                        class="btn btn-primary btn-sm"
                        title="Ver detalle completo"
                      >
                        <i class="material-icons">open_in_new</i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-if="getDetallesForInsumoModal(modalDetalleInsumo.insumo.cod_insumo).length > 5" class="mas-detalles">
                <p>Mostrando 5 de {{ getDetallesForInsumoModal(modalDetalleInsumo.insumo.cod_insumo).length }} detalles totales.</p>
                <button @click="verTodosLosDetalles(modalDetalleInsumo.insumo)" class="btn btn-outline">
                  Ver todos los detalles
                </button>
              </div>
            </div>
          </div>

          <!-- Estadísticas del insumo -->
          <div class="seccion-info">
            <h4><i class="material-icons">analytics</i> Estadísticas</h4>
            <div class="stats-grid-modal">
              <div class="stat-card-modal">
                <div class="stat-icon">
                  <i class="material-icons">category</i>
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ getClasificaciones(modalDetalleInsumo.insumo.cod_insumo).length }}</div>
                  <div class="stat-label">Clasificaciones</div>
                </div>
              </div>
              <div class="stat-card-modal">
                <div class="stat-icon">
                  <i class="material-icons">description</i>
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ getDetallesCountForInsumo(modalDetalleInsumo.insumo.cod_insumo) }}</div>
                  <div class="stat-label">Detalles</div>
                </div>
              </div>
              <div class="stat-card-modal">
                <div class="stat-icon">
                  <i class="material-icons">comment</i>
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ getConceptosCountForInsumo(modalDetalleInsumo.insumo.cod_insumo) }}</div>
                  <div class="stat-label">Conceptos</div>
                </div>
              </div>
              <div class="stat-card-modal">
                <div class="stat-icon">
                  <i class="material-icons">insert_drive_file</i>
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ getArchivosCountForInsumo(modalDetalleInsumo.insumo.cod_insumo) }}</div>
                  <div class="stat-label">Archivos</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="modalDetalleInsumo.mostrar = false">
            Cerrar
          </button>
          <button class="btn btn-primary" @click="irAVistaCompleta(modalDetalleInsumo.insumo)">
            <i class="material-icons">open_in_new</i>
            Ver vista completa
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de detalle de detalle (similar a EstadoProducto.vue) -->
    <div v-if="modalDetalleDetalle.mostrar" class="modal-overlay" @click="modalDetalleDetalle.mostrar = false">
      <div class="modal-content modal-detalle-detalle" @click.stop>
        <div class="modal-header">
          <h3>
            <i class="material-icons">description</i>
            Detalle Completo #{{ modalDetalleDetalle.detalle?.cod_detalle }}
          </h3>
          <button class="btn-close" @click="modalDetalleDetalle.mostrar = false">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body" v-if="modalDetalleDetalle.detalle">
          <div class="detalle-info">
            <div class="info-grid">
              <div class="info-item">
                <label>Código:</label>
                <span>{{ modalDetalleDetalle.detalle.cod_detalle }}</span>
              </div>
              <div class="info-item">
                <label>Municipio:</label>
                <span>{{ selectedMunicipio?.nom_municipio || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Clasificación:</label>
                <span>{{ getNombreClasificacion(modalDetalleDetalle.detalle.cod_clasificacion) || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Estado:</label>
                <span class="estado-badge" :class="getEstadoClass(modalDetalleDetalle.detalle.estado)">
                  {{ modalDetalleDetalle.detalle.estado || 'N/A' }}
                </span>
              </div>
              <div class="info-item">
                <label>Escala:</label>
                <span>{{ modalDetalleDetalle.detalle.escala || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Cubrimiento:</label>
                <span>{{ modalDetalleDetalle.detalle.cubrimiento || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Área:</label>
                <span>{{ modalDetalleDetalle.detalle.area || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Zona:</label>
                <span>{{ modalDetalleDetalle.detalle.zona || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Entidad:</label>
                <span>{{ getNombreEntidad(modalDetalleDetalle.detalle.cod_entidad) }}</span>
              </div>
              <div class="info-item">
                <label>Formato:</label>
                <span>{{ modalDetalleDetalle.detalle.formato_tipo || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Vigencia:</label>
                <span>{{ modalDetalleDetalle.detalle.vigencia || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Usuario:</label>
                <span>{{ getNombreUsuario(modalDetalleDetalle.detalle.cod_usuario) }}</span>
              </div>
              <div class="info-item">
                <label>Fecha Entrega:</label>
                <span>{{ formatDate(modalDetalleDetalle.detalle.fecha_entrega) }}</span>
              </div>
              <div class="info-item">
                <label>Fecha Disposición:</label>
                <span>{{ formatDate(modalDetalleDetalle.detalle.fecha_disposicion) }}</span>
              </div>
              <div class="info-item" v-if="modalDetalleDetalle.detalle.observacion">
                <label>Observación:</label>
                <span>{{ modalDetalleDetalle.detalle.observacion }}</span>
              </div>
            </div>
            
            <!-- Sección de Conceptos (igual que en EstadoProducto.vue) -->
            <div v-if="getConceptosDelDetalle(modalDetalleDetalle.detalle.cod_detalle).length > 0" class="conceptos-section">
              <h4><i class="material-icons">description</i> Conceptos Asociados</h4>
              <div class="conceptos-list">
                <div 
                  v-for="concepto in getConceptosDelDetalle(modalDetalleDetalle.detalle.cod_detalle)" 
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
                    <p v-if="concepto.fecha"><strong>Fecha:</strong> {{ formatDate(concepto.fecha) }}</p>
                    <div v-if="concepto.pdf" class="concepto-actions">
                      <button 
                        @click="verDocumentoPDF(concepto.pdf)" 
                        class="btn btn-primary btn-sm"
                        title="Ver PDF del concepto en nueva ventana"
                      >
                        <i class="material-icons">open_in_new</i>
                        Ver PDF
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

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="modalDetalleDetalle.mostrar = false">
            Cerrar
          </button>
        </div>
      </div>
    </div>
    
    <!-- Mensajes de notificación -->
    <div v-if="notification.show" :class="['notification', notification.type]">
      <div class="notification-content">
        <i class="material-icons">{{ notification.icon }}</i>
        <span>{{ notification.message }}</span>
      </div>
      <button @click="closeNotification" class="notification-close">
        <i class="material-icons">close</i>Ɋ>
      </button>
    </div>
  </div>
</template>


<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { format, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';
import { linuxToWindowsPath, windowsToLinuxPath } from '@/utils/pathUtils';
// ✅ IMPORTAR EL STORE DE AUTH PARA PERMISOS
import { useAuthStore } from '@/store/auth';
// Importar servicios API
import { 
  getClasificacionesByMunicipio, getDetallesByMunicipio 
} from '@/api/municipios';

import { 
  createInsumo, updateInsumo, deleteInsumo, 
  createClasificacion, updateClasificacion, deleteClasificacion,
  createDetalle, updateDetalle, deleteDetalle,
  getClasificaciones,
  getProfesionalesSeguimiento, getArchivosByClasificacion,getMecanismosGenerales,
  getMecanismosDetalle, getMecanismosOperacion,getAlcancesOperacion,getGrupos,
  getTerritoriales,
} from '@/api/insumos';

import axios from 'axios'
import { 
getMunicipioById, getInsumosByMunicipio 
} from '@/api/municipios';

import { 
  getCategorias, getTiposInsumo, 
  getEntidades, getFormatos, getZonas, getUsuarios 
} from '@/api/insumos';

import api, { API_URL } from '@/api/config';
import { getDepartamentos } from '@/api/departamentos';
import { getMunicipios } from '@/api/municipios';
import { getConceptosByMunicipio } from '@/api/conceptos';
import { getCentrosPobladosPorMunicipio } from '@/api/centrosPoblados';



export default defineComponent({
  name: 'InsumosList',
  
  setup() {
    const route = useRoute();
    const router = useRouter();
    // ✅ USAR EL STORE DE AUTH PARA PERMISOS
    const authStore = useAuthStore();
    const filtroTipoInfoCatastral = ref('');
    // Estado de carga y error
    const loading = ref(false);
    const error = ref<string | null>(null);
    
    // Estado de notificaciones
    const notification = ref({
      show: false,
      message: '',
      type: 'success',
      icon: 'check_circle',
      timeout: null as number | null
    });
    
    // Estados de datos principales
    const departamentos = ref<any[]>([]);
    const municipiosList = ref<any[]>([]);
    const categorias = ref<any[]>([]);
    const tiposInsumo = ref<any[]>([]);
    const mecanismosGenerales = ref<any[]>([]);
    const mecanismosDetalle = ref<any[]>([]);
    const mecanismosOperacion = ref<any[]>([]);
    const alcancesOperacion = ref<any[]>([]);
    const grupos = ref<any[]>([]);
    const territoriales = ref<any[]>([]);
    const zonas = ref<any[]>([]);
    const entidades = ref<any[]>([]);
    const formatos = ref<any[]>([]);
    const usuarios = ref<any[]>([]);
    const descargandoInsumos = ref<{[key: string]: boolean}>({});

    const filtroZonaDetalle = ref('');
    const filtroCentroPobladoDetalle = ref('');
    const filtroClasificacionDetalle = ref('');
    const filtroFormatoDetalle = ref('');
    
    // Municipio seleccionado
    const selectedMunicipioId = ref<number | null>(null);
    const selectedMunicipio = ref<any | null>(null);
    const municipioInsumos = ref<any[]>([]);
    const municipioClasificaciones = ref<any[]>([]);
    const municipioDetalles = ref<any[]>([]);
    const municipioArchivos = ref<any[]>([]);
    const municipioProfesionales = ref<any[]>([]);
    
    // ✅ NUEVOS ESTADOS PARA FILTROS DE CARTOGRAFÍA BÁSICA
    const filtroCentroPoblado = ref('');
    const filtroTipoCartografia = ref('');
    const centrosPoblados = ref<any[]>([]);
    const cargandoCentrosPoblados = ref(false);

    const detalleSeleccionado = ref(null);
    const detalleModalVisible = ref(false);

    // Filtros y paginación
    const searchTerm = ref('');
    const filters = ref({
      departamento: '',
      municipio: '',
      territorial: '',
      mecanismoGeneral: '',
      mecanismoDetalle: '',
      grupo: ''
    });
    const currentPage = ref(1);
    const pageSize = ref(10);
    
    // Filtros para pestañas
    const insumoSearch = ref('');
    const insumoFilter = ref('');
    const tipoInsumoFilter = ref('');
    const clasificacionSearch = ref('');
    const detalleSearch = ref('');
    const archivoSearch = ref('');
    
    // Pestaña activa en vista detallada
    const activeTab = ref('resumen');
    
    const activeArchivosTab = ref('preoperacion');
    const municipioArchivosPost = ref<any[]>([]);
    const municipioConceptos = ref<any[]>([]);
    const conceptoSearch = ref('');
    const conceptosLoading = ref(false);
    const conceptosError = ref<string | null>(null);
    const archivosPostLoading = ref(false);
    const archivosPostError = ref<string | null>(null);
    const archivosPreLoading = ref(false);
    const archivosPreError = ref<string | null>(null);

    // ✅ FILTROS ESPECÍFICOS PARA ARCHIVOS
    const filtroClasificacionPre = ref('');
    const filtroNombreArchivoPre = ref('');
    const filtroComponentePost = ref('');
    const filtroNombreArchivoPost = ref('');

    // ✅ MODAL DE DETALLES DE ARCHIVO
    const showArchivoDetailsModal = ref(false);
    const selectedArchivoDetails = ref<any>(null);
    const archivoDetailsType = ref<'pre' | 'post'>('pre');


    const modalDetalleInsumo = ref({
      mostrar: false,
      insumo: null
    });

    const modalDetalleDetalle = ref({
      mostrar: false,
      detalle: null
    });


    // Pestañas para la vista detallada
    const detailTabs = [
      { id: 'resumen', label: 'Resumen', icon: 'dashboard' },
      { id: 'insumos', label: 'Insumos', icon: 'folder' },
      { id: 'clasificaciones', label: 'Clasificaciones', icon: 'category' },
      { id: 'detalles', label: 'Detalles', icon: 'description' },
      { id: 'conceptos', label: 'Conceptos', icon: 'comment' },
      { id: 'archivos', label: 'Archivos', icon: 'insert_drive_file' }
    ];

    // **FUNCIONES AUXILIARES**
    // Función para obtener el nombre del archivo de una ruta completa
    const obtenerNombreArchivo = (rutaCompleta: string): string => {
      if (!rutaCompleta) return 'archivo';
      
      // Separar por both tipos de separadores (Windows y Unix)
      const separadores = rutaCompleta.split(/[\\/]/);
      const nombreArchivo = separadores[separadores.length - 1];
      
      return nombreArchivo || 'archivo';
    };

    // Implementa la función cargarTodosLosDatos
    const cargarTodosLosDatos = async (url: string, params = {}) => {
      let allResults = [];
      let nextUrl = url;
      
      while (nextUrl) {
        const response = await fetch(nextUrl, {
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });
        
        if (!response.ok) {
          throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.results && Array.isArray(data.results)) {
          allResults = [...allResults, ...data.results];
          nextUrl = data.next;
        } else if (Array.isArray(data)) {
          allResults = [...allResults, ...data];
          nextUrl = null;
        } else {
          console.warn('Respuesta inesperada:', data);
          allResults = Array.isArray(data) ? data : [];
          nextUrl = null;
        }
      }
      
      return allResults;
    };

    // ✅ NUEVAS FUNCIONES PARA CARTOGRAFÍA BÁSICA

    // Cargar centros poblados para el municipio seleccionado
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



    // Aplicar filtros de archivos
    const aplicarFiltrosArchivos = () => {
      // Esta función se ejecuta automáticamente por los computed properties
      console.log('Aplicando filtros de archivos...');
    };

const filteredArchivosPreConInfoCatastral = computed(() => {
  let result = [...municipioArchivos.value];
  
  // Filtro por clasificación
  if (filtroClasificacionPre.value) {
    result = result.filter(a => {
      const nombreClasificacion = getNombreClasificacion(a.cod_insumo);
      return nombreClasificacion === filtroClasificacionPre.value;
    });
  }
  
  // ✅ FILTROS PARA CARTOGRAFÍA BÁSICA
  if (mostrarFiltrosCartografiaBasica.value) {
    if (filtroCentroPoblado.value) {
      result = result.filter(a => {
        if (!a.path_file || !selectedMunicipioId.value) return false;
        const tresDigitosArchivo = extraerCodigoFinal(a.path_file);
        return tresDigitosArchivo === filtroCentroPoblado.value;
      });
    }
    
    if (filtroTipoCartografia.value) {
      result = result.filter(a => {
        if (!a.path_file) return false;
        const tipoArchivo = getTipoCartografiaFromPath(a.path_file);
        return tipoArchivo === filtroTipoCartografia.value;
      });
    }
  }
  
  // ✅ NUEVO: FILTROS PARA INFORMACIÓN CATASTRAL
  if (mostrarFiltrosInfoCatastral.value && filtroTipoInfoCatastral.value) {
    result = result.filter(a => {
      if (!a.path_file) return false;
      const tipoInfoCatastral = getTipoInfoCatastralFromPath(a.path_file);
      return tipoInfoCatastral === filtroTipoInfoCatastral.value;
    });
  }
  
  // Filtro por nombre de archivo
  if (filtroNombreArchivoPre.value.trim()) {
    const search = filtroNombreArchivoPre.value.toLowerCase();
    result = result.filter(a => 
      a.nombre_insumo?.toLowerCase().includes(search)
    );
  }
  
  console.log(`🔍 Filtros aplicados: clasificación=${filtroClasificacionPre.value}, tipo_catastral=${filtroTipoInfoCatastral.value}`);
  console.log(`📊 Resultados: ${result.length} de ${municipioArchivos.value.length} archivos`);
  
  return result;
});

    // Obtener tipo de cartografía desde la ruta del archivo
    const getTipoCartografiaFromPath = (pathFile: string): string => {
      if (!pathFile) return 'N/A';

      // Normalizar separadores (convertir todo a forward slash)
      const normalizedPath = pathFile.replace(/\\/g, '/');

      // Verificar patrones en orden de especificidad
      // IMPORTANTE: Usar normalizedPath para TODAS las comparaciones
      if (normalizedPath.includes('/02_vect/')) return 'Vectorial';
      if (normalizedPath.includes('/01_rast/01_orto') || normalizedPath.includes('01_rast/01_orto')) return 'Ortofoto';
      if (normalizedPath.includes('/01_rast/02_dtm') || normalizedPath.includes('01_rast/02_dtm')) return 'Modelo Digital';
      if (normalizedPath.includes('/01_rast/02_mtd') || normalizedPath.includes('01_rast/02_mtd')) return 'Modelo Digital';

      return 'N/A';
    };


    // ✅ 2. FUNCIÓN para verificar si un archivo coincide con el tipo seleccionado
const archivoCoincideConTipo = (pathFile: string, tipoSeleccionado: string): boolean => {
  if (!pathFile || !tipoSeleccionado) return true;
  
  const tipoArchivo = getTipoCartografiaFromPath(pathFile);
  return tipoArchivo === tipoSeleccionado;
};

// ✅ 3. COMPUTED CORREGIDO para filtros de archivos de preoperación
const filteredArchivosPreFinal = computed(() => {
  let result = [...municipioArchivos.value];
  
  // Filtro por clasificación
  if (filtroClasificacionPre.value) {
    result = result.filter(a => {
      const nombreClasificacion = getNombreClasificacion(a.cod_insumo);
      return nombreClasificacion === filtroClasificacionPre.value;
    });
  }
  
  // ✅ FILTROS PARA CARTOGRAFÍA BÁSICA
  if (mostrarFiltrosCartografiaBasica.value) {
    // Filtro por centro poblado
    if (filtroCentroPoblado.value) {
      result = result.filter(a => {
        if (!a.path_file || !selectedMunicipioId.value) return false;
        
        const tresDigitosArchivo = extraerCodigoFinal(a.path_file);
        const coincide = tresDigitosArchivo === filtroCentroPoblado.value;
        
        return coincide;
      });
    }
    
    // ✅ FILTRO POR TIPO DE CARTOGRAFÍA CORREGIDO
    if (filtroTipoCartografia.value) {
      result = result.filter(a => {
        if (!a.path_file) return false;
        
        const tipoArchivo = getTipoCartografiaFromPath(a.path_file);
        const coincide = tipoArchivo === filtroTipoCartografia.value;
        
        // Debug para ver qué está pasando
        if (filtroTipoCartografia.value === 'Ortofoto' && tipoArchivo === 'Ortofoto') {
          console.log(`✅ Ortofoto encontrada: ${a.nombre_insumo}`);
        }
        
        return coincide;
      });
    }
  }
  
  // Filtro por nombre de archivo
  if (filtroNombreArchivoPre.value.trim()) {
    const search = filtroNombreArchivoPre.value.toLowerCase();
    result = result.filter(a => 
      a.nombre_insumo?.toLowerCase().includes(search)
    );
  }
  
  console.log(`🔍 Filtros aplicados: clasificación=${filtroClasificacionPre.value}, centro=${filtroCentroPoblado.value}, tipo=${filtroTipoCartografia.value}`);
  console.log(`📊 Resultados: ${result.length} de ${municipioArchivos.value.length} archivos`);
  
  return result;
});


    // Obtener clase CSS para el tipo de cartografía
    const getTipoCartografiaClass = (pathFile: string): string => {
      const tipo = getTipoCartografiaFromPath(pathFile);
      switch (tipo) {
        case 'Vectorial': return 'tipo-vectorial';
        case 'Ortofoto': return 'tipo-ortofoto';
        case 'Modelo Digital': return 'tipo-modelo';
        default: return 'tipo-default';
      }
    };

    // Extraer código de centro poblado (últimos 3 dígitos)


    // Obtener nombre amigable del tipo de cartografía
    const getNombreTipoCartografia = (tipo: string): string => {
      switch (tipo) {
        case '02_vect': return 'Vectorial';
        case '01_rast\\01_orto': return 'Ortofoto';
        case '01_rast\\02_dtm': return 'Modelo Digital del Terreno';
        case '01_rast\\02_mtd': return 'Modelo Digital del Terreno';
        default: return tipo;
      }
    };

    // Limpiar todos los filtros de preoperación
    const limpiarFiltrosPreoperacion = () => {
      filtroClasificacionPre.value = '';
      filtroNombreArchivoPre.value = '';
      filtroCentroPoblado.value = '';
      filtroTipoCartografia.value = '';
      filtroTipoInfoCatastral.value = ''; 
    };

    // ✅ FUNCIÓN PARA VERIFICAR ACCESO A MUNICIPIO (CONTROL DE PERMISOS)
    const tieneAccesoAMunicipio = (municipioId: number): boolean => {
      // Si es admin o super admin, tiene acceso a todo
      if (authStore.isAnyAdmin) return true;
      
      // Si es profesional, verificar municipios asignados
      if (authStore.isProfesional) {
        return authStore.tieneAccesoAMunicipio(municipioId);
      }
      
      // Por defecto, no tiene acceso
      return false;
    };

    // Cargar datos iniciales
    const loadInitialData = async () => {
      try {
        loading.value = true;
        error.value = null;
        
        const [
          deptosResult, 
          municipiosResult, 
          categoriasResult, 
          tiposResult, 
          mecGeneralResult,
          mecDetalleResult,
          gruposResult, 
          territorialesResult, 
          entidadesResult, 
          usuariosResult
        ] = await Promise.allSettled([
          cargarTodosLosDatos(`${API_URL}/preoperacion/departamentos/`),
          cargarTodosLosDatos(`${API_URL}/preoperacion/municipios/`),
          cargarTodosLosDatos(`${API_URL}/preoperacion/categorias/`),
          cargarTodosLosDatos(`${API_URL}/preoperacion/tipos-insumo/`),
          cargarTodosLosDatos(`${API_URL}/preoperacion/mecanismos-general/`),
          cargarTodosLosDatos(`${API_URL}/preoperacion/mecanismos-detalle/`),
          cargarTodosLosDatos(`${API_URL}/preoperacion/grupos/`),
          cargarTodosLosDatos(`${API_URL}/preoperacion/territoriales/`),
          cargarTodosLosDatos(`${API_URL}/preoperacion/entidades/`),
          cargarTodosLosDatos(`${API_URL}/preoperacion/usuarios/`)
        ]);
        
        departamentos.value = deptosResult.status === 'fulfilled' ? deptosResult.value : [];
        municipiosList.value = municipiosResult.status === 'fulfilled' ? municipiosResult.value : [];
        categorias.value = categoriasResult.status === 'fulfilled' ? categoriasResult.value : [];
        tiposInsumo.value = tiposResult.status === 'fulfilled' ? tiposResult.value : [];
        mecanismosGenerales.value = mecGeneralResult.status === 'fulfilled' ? mecGeneralResult.value : [];
        mecanismosDetalle.value = mecDetalleResult.status === 'fulfilled' ? mecDetalleResult.value : [];
        grupos.value = gruposResult.status === 'fulfilled' ? gruposResult.value : [];
        territoriales.value = territorialesResult.status === 'fulfilled' ? territorialesResult.value : [];
        entidades.value = entidadesResult.status === 'fulfilled' ? entidadesResult.value : [];
        usuarios.value = usuariosResult.status === 'fulfilled' ? usuariosResult.value : [];
        
        console.log(`Cargados ${municipiosList.value.length} municipios`);
        
      } catch (err: any) {
        console.error('Error cargando datos iniciales:', err);
        error.value = 'Error cargando datos. Por favor, intente nuevamente.';
      } finally {
        loading.value = false;
      }
    };

    // **COMPUTED PROPERTIES**

    // ✅ NUEVOS COMPUTED PROPERTIES PARA CARTOGRAFÍA BÁSICA
    
    // Computed para determinar si mostrar los filtros de cartografía básica
    const mostrarFiltrosCartografiaBasica = computed(() => {
      return filtroClasificacionPre.value === 'Cartografía Básica' || 
             filtroClasificacionPre.value === 'cartografia_basica' ||
             filtroClasificacionPre.value.toLowerCase().includes('cartograf');
    });

    // Computed para verificar si hay filtros activos
    const hayFiltrosActivosPreoperacion = computed(() => {
      return filtroClasificacionPre.value || 
            filtroNombreArchivoPre.value || 
            (mostrarFiltrosCartografiaBasica.value && (filtroCentroPoblado.value || filtroTipoCartografia.value)) ||
            (mostrarFiltrosInfoCatastral.value && filtroTipoInfoCatastral.value);
    });

    // ✅ FILTRAR MUNICIPIOS SEGÚN PERMISOS
    const filteredMunicipiosForDropdown = computed(() => {
      let municipios = municipiosList.value;
      
      // Aplicar filtro de departamento si existe
      if (filters.value.departamento) {
        municipios = municipios.filter(m => 
          m.cod_depto.toString() === filters.value.departamento.toString()
        );
      }
      
      // ✅ APLICAR FILTRO DE PERMISOS
      if (authStore.isProfesional) {
        municipios = municipios.filter(m => tieneAccesoAMunicipio(m.cod_municipio));
      }
      
      return municipios;
    });
    
    const filteredMunicipios = computed(() => {
      let result = [...municipiosList.value];
      
      // ✅ APLICAR FILTRO DE PERMISOS PRIMERO
      if (authStore.isProfesional) {
        result = result.filter(m => tieneAccesoAMunicipio(m.cod_municipio));
      }
      
      if (searchTerm.value.trim()) {
        const search = searchTerm.value.toLowerCase();
        result = result.filter(m => 
          m.nom_municipio.toLowerCase().includes(search) ||
          m.cod_municipio.toString().includes(search) ||
          getNombreDepartamento(m.cod_depto).toLowerCase().includes(search)
        );
      }
      
      if (filters.value.departamento) {
        result = result.filter(m => 
          m.cod_depto.toString() === filters.value.departamento.toString()
        );
      }
      
      if (filters.value.municipio) {
        result = result.filter(m => 
          m.cod_municipio.toString() === filters.value.municipio.toString()
        );
      }
      
      if (filters.value.territorial) {
        result = result.filter(m => 
          m.nom_territorial === filters.value.territorial
        );
      }
      
      if (filters.value.mecanismoGeneral) {
        result = result.filter(m => 
          m.mecanismo_general === filters.value.mecanismoGeneral
        );
      }
      
      if (filters.value.grupo) {
        result = result.filter(m => 
          m.grupo === filters.value.grupo
        );
      }
      
      return result;
    });
    
    // Paginación
    const totalPages = computed(() => {
      return Math.ceil(filteredMunicipios.value.length / pageSize.value);
    });
    
    const paginatedMunicipios = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value;
      const end = start + pageSize.value;
      return filteredMunicipios.value.slice(start, end);
    });
    
    const displayedPages = computed(() => {
      if (totalPages.value <= 5) {
        return Array.from({ length: totalPages.value }, (_, i) => i + 1);
      }
      
      const pages = [];
      if (currentPage.value <= 3) {
        for (let i = 1; i <= 5; i++) {
          pages.push(i);
        }
      } else if (currentPage.value >= totalPages.value - 2) {
        for (let i = totalPages.value - 4; i <= totalPages.value; i++) {
          pages.push(i);
        }
      } else {
        for (let i = currentPage.value - 2; i <= currentPage.value + 2; i++) {
          pages.push(i);
        }
      }
      
      return pages;
    });
    
    // Filtros para insumos
    const filteredInsumos = computed(() => {
      let result = [...municipioInsumos.value];
      
      if (insumoSearch.value.trim()) {
        const search = insumoSearch.value.toLowerCase();
        result = result.filter(i => 
          i.cod_insumo.toString().includes(search) ||
          (getNombreCategoria(i.cod_categoria).toLowerCase().includes(search)) ||
          (getTipoInsumoNombre(i.tipo_insumo).toLowerCase().includes(search))
        );
      }
      
      if (insumoFilter.value) {
        result = result.filter(i => 
          i.cod_categoria.toString() === insumoFilter.value.toString()
        );
      }
      
      if (tipoInsumoFilter.value) {
        result = result.filter(i => {
          const tipoNormalizado = getTipoInsumoNombre(i.tipo_insumo).toLowerCase();
          return tipoNormalizado === tipoInsumoFilter.value.toLowerCase();
        });
      }
      
      return result;
    });
    
    // Filtros para clasificaciones
    const filteredClasificaciones = computed(() => {
      let result = [...municipioClasificaciones.value];
      
      if (clasificacionSearch.value.trim()) {
        const search = clasificacionSearch.value.toLowerCase();
        result = result.filter(c => 
          c.nombre.toLowerCase().includes(search) ||
          c.cod_clasificacion.toString().includes(search) ||
          (c.observacion?.toLowerCase().includes(search) || '')
        );
      }
      
      return result;
    });
    
    // Filtros para detalles
    // REEMPLAZAR el computed filteredDetalles existente
    const filteredDetalles = computed(() => {
      let result = [...municipioDetalles.value];
      
      // Búsqueda general
      if (detalleSearch.value.trim()) {
        const search = detalleSearch.value.toLowerCase();
        result = result.filter(d => 
          d.cod_detalle.toString().includes(search) ||
          (d.escala?.toLowerCase().includes(search) || '') ||
          (d.estado?.toLowerCase().includes(search) || '') ||
          (d.observacion?.toLowerCase().includes(search) || '') ||
          (getNombreClasificacion(d.cod_clasificacion).toLowerCase().includes(search)) ||
          (getNombreEntidad(d.cod_entidad).toLowerCase().includes(search))
        );
      }
      
      // Filtro por Zona
      if (filtroZonaDetalle.value) {
        result = result.filter(d => d.zona === filtroZonaDetalle.value);
        
        // Filtro por Centro Poblado (solo si zona es CENTROS POBLADOS)
        if (filtroZonaDetalle.value === 'CENTROS POBLADOS' && filtroCentroPobladoDetalle.value) {
          result = result.filter(d => d.cod_centro_poblado === filtroCentroPobladoDetalle.value);
        }
      }
      
      // Filtro por Clasificación
      if (filtroClasificacionDetalle.value) {
        result = result.filter(d => d.cod_clasificacion === parseInt(filtroClasificacionDetalle.value));
      }
      
      // Filtro por Formato
      if (filtroFormatoDetalle.value) {
        result = result.filter(d => d.formato_tipo === filtroFormatoDetalle.value);
      }
      
      return result;
    });
    const handleZonaDetalleChange = () => {
      // Si cambia la zona y no es CENTROS POBLADOS, limpiar filtro de centro poblado
      if (filtroZonaDetalle.value !== 'CENTROS POBLADOS') {
        filtroCentroPobladoDetalle.value = '';
      }
    };

    const limpiarFiltrosDetalles = () => {
      filtroZonaDetalle.value = '';
      filtroCentroPobladoDetalle.value = '';
      filtroClasificacionDetalle.value = '';
      filtroFormatoDetalle.value = '';
      detalleSearch.value = '';
    };


    // ✅ COMPUTED PARA OPCIONES DINÁMICAS DE FILTROS EN DETALLES
    const zonasUnicasDetalles = computed(() => {
      let detalles = [...municipioDetalles.value];
      
      // Aplicar búsqueda si existe
      if (detalleSearch.value.trim()) {
        const search = detalleSearch.value.toLowerCase();
        detalles = detalles.filter(d => 
          d.cod_detalle.toString().includes(search) ||
          (d.escala?.toLowerCase().includes(search) || '') ||
          (d.estado?.toLowerCase().includes(search) || '') ||
          (d.observacion?.toLowerCase().includes(search) || '')
        );
      }
      
      // Aplicar otros filtros para obtener zonas disponibles
      if (filtroClasificacionDetalle.value) {
        detalles = detalles.filter(d => d.cod_clasificacion === parseInt(filtroClasificacionDetalle.value));
      }
      
      if (filtroFormatoDetalle.value) {
        detalles = detalles.filter(d => d.formato_tipo === filtroFormatoDetalle.value);
      }
      
      const zonas = new Set();
      detalles.forEach(d => {
        if (d.zona) zonas.add(d.zona);
      });
      
      return Array.from(zonas).sort();
    });

    const centrosPobladosUnicosDetalles = computed(() => {
      if (filtroZonaDetalle.value !== 'CENTROS POBLADOS') return [];
      
      let detalles = municipioDetalles.value.filter(d => d.zona === 'CENTROS POBLADOS');
      
      // Aplicar otros filtros
      if (detalleSearch.value.trim()) {
        const search = detalleSearch.value.toLowerCase();
        detalles = detalles.filter(d => 
          d.cod_detalle.toString().includes(search) ||
          (d.escala?.toLowerCase().includes(search) || '') ||
          (d.estado?.toLowerCase().includes(search) || '') ||
          (d.observacion?.toLowerCase().includes(search) || '')
        );
      }
      
      if (filtroClasificacionDetalle.value) {
        detalles = detalles.filter(d => d.cod_clasificacion === parseInt(filtroClasificacionDetalle.value));
      }
      
      if (filtroFormatoDetalle.value) {
        detalles = detalles.filter(d => d.formato_tipo === filtroFormatoDetalle.value);
      }
      
      const centros = new Map();
      detalles.forEach(d => {
        if (d.cod_centro_poblado) {
          const nombre = d.centro_poblado_nombre || `Centro ${d.cod_centro_poblado}`;
          centros.set(d.cod_centro_poblado, nombre);
        }
      });
      
      return Array.from(centros.entries()).map(([codigo, nombre]) => ({
        codigo,
        nombre
      })).sort((a, b) => a.nombre.localeCompare(b.nombre));
    });

    const clasificacionesUnicasDetalles = computed(() => {
      let detalles = [...municipioDetalles.value];
      
      // Aplicar otros filtros
      if (detalleSearch.value.trim()) {
        const search = detalleSearch.value.toLowerCase();
        detalles = detalles.filter(d => 
          d.cod_detalle.toString().includes(search) ||
          (d.escala?.toLowerCase().includes(search) || '') ||
          (d.estado?.toLowerCase().includes(search) || '') ||
          (d.observacion?.toLowerCase().includes(search) || '')
        );
      }
      
      if (filtroZonaDetalle.value) {
        detalles = detalles.filter(d => d.zona === filtroZonaDetalle.value);
        
        if (filtroZonaDetalle.value === 'CENTROS POBLADOS' && filtroCentroPobladoDetalle.value) {
          detalles = detalles.filter(d => d.cod_centro_poblado === filtroCentroPobladoDetalle.value);
        }
      }
      
      if (filtroFormatoDetalle.value) {
        detalles = detalles.filter(d => d.formato_tipo === filtroFormatoDetalle.value);
      }
      
      const clasificaciones = new Set();
      detalles.forEach(d => {
        if (d.cod_clasificacion) {
          clasificaciones.add(d.cod_clasificacion);
        }
      });
      
      return Array.from(clasificaciones).map(cod => ({
        codigo: cod,
        nombre: getNombreClasificacion(cod)
      })).sort((a, b) => a.nombre.localeCompare(b.nombre));
    });

    const formatosUnicosDetalles = computed(() => {
      let detalles = [...municipioDetalles.value];
      
      // Aplicar otros filtros
      if (detalleSearch.value.trim()) {
        const search = detalleSearch.value.toLowerCase();
        detalles = detalles.filter(d => 
          d.cod_detalle.toString().includes(search) ||
          (d.escala?.toLowerCase().includes(search) || '') ||
          (d.estado?.toLowerCase().includes(search) || '') ||
          (d.observacion?.toLowerCase().includes(search) || '')
        );
      }
      
      if (filtroZonaDetalle.value) {
        detalles = detalles.filter(d => d.zona === filtroZonaDetalle.value);
        
        if (filtroZonaDetalle.value === 'CENTROS POBLADOS' && filtroCentroPobladoDetalle.value) {
          detalles = detalles.filter(d => d.cod_centro_poblado === filtroCentroPobladoDetalle.value);
        }
      }
      
      if (filtroClasificacionDetalle.value) {
        detalles = detalles.filter(d => d.cod_clasificacion === parseInt(filtroClasificacionDetalle.value));
      }
      
      const formatos = new Set();
      detalles.forEach(d => {
        if (d.formato_tipo) formatos.add(d.formato_tipo);
      });
      
      return Array.from(formatos).sort();
    });

    // Computed para verificar si hay filtros activos
    const hayFiltrosActivosDetalles = computed(() => {
      return filtroZonaDetalle.value || 
            filtroCentroPobladoDetalle.value || 
            filtroClasificacionDetalle.value || 
            filtroFormatoDetalle.value ||
            detalleSearch.value;
    });


    const filteredArchivosPost = computed(() => {
      let result = [...municipioArchivosPost.value];
      
      // Filtro por niveles de carpetas
      if (filtrosNivelesPost.value.nivel1) {
        result = result.filter(a => {
          if (!a.ruta_completa) return false;
          const niveles = extraerNivelesDeRuta(a.ruta_completa);
          return niveles[0] === filtrosNivelesPost.value.nivel1;
        });
        
        if (filtrosNivelesPost.value.nivel2) {
          result = result.filter(a => {
            const niveles = extraerNivelesDeRuta(a.ruta_completa);
            return niveles[1] === filtrosNivelesPost.value.nivel2;
          });
          
          if (filtrosNivelesPost.value.nivel3) {
            result = result.filter(a => {
              const niveles = extraerNivelesDeRuta(a.ruta_completa);
              return niveles[2] === filtrosNivelesPost.value.nivel3;
            });
            
            if (filtrosNivelesPost.value.nivel4) {
              result = result.filter(a => {
                const niveles = extraerNivelesDeRuta(a.ruta_completa);
                return niveles[3] === filtrosNivelesPost.value.nivel4;
              });
              
              if (filtrosNivelesPost.value.nivel5) {
                result = result.filter(a => {
                  const niveles = extraerNivelesDeRuta(a.ruta_completa);
                  return niveles[4] === filtrosNivelesPost.value.nivel5;
                });
              }
            }
          }
        }
      }
      
      // Filtro por nombre de archivo
      if (filtroNombreArchivoPost.value.trim()) {
        const search = filtroNombreArchivoPost.value.toLowerCase();
        result = result.filter(a => 
          a.nombre_archivo?.toLowerCase().includes(search)
        );
      }
      
      return result;
    });


    // ✅ LISTAS ÚNICAS PARA FILTROS
    const clasificacionesUnicasPre = computed(() => {
      const clasificaciones = new Set();
      municipioArchivos.value.forEach(archivo => {
        if (archivo.cod_insumo) {
          const nombreClasificacion = getNombreClasificacion(archivo.cod_insumo);
          if (nombreClasificacion && nombreClasificacion !== 'N/A') {
            clasificaciones.add(nombreClasificacion);
          }
        }
      });
      return Array.from(clasificaciones).sort();
    });

    const componentesUnicosPost = computed(() => {
      const componentes = new Set();
      municipioArchivosPost.value.forEach(archivo => {
        if (archivo.disposicion_info?.componente) {
          componentes.add(archivo.disposicion_info.componente);
        }
      });
      return Array.from(componentes).sort();
    });

    const filteredConceptos = computed(() => {
      // ✅ DEBUG: Mostrar si hay filtro activo
      if (conceptoSearch.value.trim()) {
        console.log(`🔍 FILTRO DE BÚSQUEDA ACTIVO: "${conceptoSearch.value}"`);
        console.log(`📊 Conceptos antes del filtro: ${municipioConceptos.value.length}`);
      }
      
      if (!conceptoSearch.value.trim()) {
        return municipioConceptos.value;
      }
      
      const search = conceptoSearch.value.toLowerCase();
      const filtered = municipioConceptos.value.filter(c => 
        (c.concepto && c.concepto.toLowerCase().includes(search)) ||
        (c.detalle_concepto && c.detalle_concepto.toLowerCase().includes(search)) ||
        (c.observacion && c.observacion.toLowerCase().includes(search)) ||
        (c.evaluacion && c.evaluacion.toLowerCase().includes(search))
      );
      
      console.log(`📊 Conceptos después del filtro: ${filtered.length}`);
      return filtered;
    });
    
    // Cálculo de resumen de insumos por categoría
    const insumosPorCategoria = computed(() => {
      const result = {};
      
      municipioInsumos.value.forEach(insumo => {
        const categoria = categorias.value.find(c => c.cod_categoria.toString() === insumo.cod_categoria.toString());
        if (categoria) {
          const categoriaId = categoria.cod_categoria;
          const categoriaName = categoria.nom_categoria;
          
          if (!result[categoriaName]) {
            result[categoriaName] = {
              id: categoriaId,
              count: 0
            };
          }
          result[categoriaName].count++;
        }
      });
      
      return result;
    });

    // COMPUTED PROPERTIES PARA FILTROS DINÁMICOS
    const departamentosDisponibles = computed(() => {
      let municipiosParaDepartamentos = [...municipiosList.value];
      
      // Solo aplicar búsqueda si existe
      if (searchTerm.value.trim()) {
        const search = searchTerm.value.toLowerCase();
        municipiosParaDepartamentos = municipiosParaDepartamentos.filter(m => 
          m.nom_municipio?.toLowerCase().includes(search) ||
          m.cod_municipio?.toString().includes(search)
        );
      }
      
      const deptosUsados = new Set(municipiosParaDepartamentos.map(m => m.cod_depto));
      return departamentos.value.filter(d => deptosUsados.has(d.cod_depto));
    });

    // 2. Municipios disponibles (filtrados por departamento seleccionado)
    const municipiosDisponibles = computed(() => {
      let municipiosParaMunicipios = [...municipiosList.value];
      
      // Aplicar búsqueda
      if (searchTerm.value.trim()) {
        const search = searchTerm.value.toLowerCase();
        municipiosParaMunicipios = municipiosParaMunicipios.filter(m => 
          m.nom_municipio?.toLowerCase().includes(search) ||
          m.cod_municipio?.toString().includes(search)
        );
      }
      
      // ⭐ FILTRAR POR DEPARTAMENTO SELECCIONADO
      if (filters.value.departamento) {
        municipiosParaMunicipios = municipiosParaMunicipios.filter(m => 
          m.cod_depto?.toString() === filters.value.departamento.toString()
        );
      }
      
      return municipiosParaMunicipios;
    });

    // 3. Territoriales disponibles (filtradas por dept + municipio)
    const territorialesDisponibles = computed(() => {
      let municipiosParaTerritoriales = [...municipiosList.value];
      
      // Aplicar búsqueda
      if (searchTerm.value.trim()) {
        const search = searchTerm.value.toLowerCase();
        municipiosParaTerritoriales = municipiosParaTerritoriales.filter(m => 
          m.nom_municipio?.toLowerCase().includes(search) ||
          m.cod_municipio?.toString().includes(search)
        );
      }
      
      // ⭐ FILTRAR POR DEPARTAMENTO
      if (filters.value.departamento) {
        municipiosParaTerritoriales = municipiosParaTerritoriales.filter(m => 
          m.cod_depto?.toString() === filters.value.departamento.toString()
        );
      }
      
      // ⭐ FILTRAR POR MUNICIPIO
      if (filters.value.municipio) {
        municipiosParaTerritoriales = municipiosParaTerritoriales.filter(m => 
          m.cod_municipio?.toString() === filters.value.municipio.toString()
        );
      }
      
      const territorialesUsadas = new Set(
        municipiosParaTerritoriales
          .map(m => m.nom_territorial)
          .filter(t => t && t.trim() !== '')
      );
      
      return territoriales.value.filter(t => territorialesUsadas.has(t.nom_territorial));
    });

    // 4. Mecanismos Generales (filtrados por dept + municipio + territorial)
    const mecanismosGeneralesDisponibles = computed(() => {
      let municipiosParaMecanismos = [...municipiosList.value];
      
      // Aplicar TODOS los filtros anteriores
      if (searchTerm.value.trim()) {
        const search = searchTerm.value.toLowerCase();
        municipiosParaMecanismos = municipiosParaMecanismos.filter(m => 
          m.nom_municipio?.toLowerCase().includes(search) ||
          m.cod_municipio?.toString().includes(search)
        );
      }
      
      if (filters.value.departamento) {
        municipiosParaMecanismos = municipiosParaMecanismos.filter(m => 
          m.cod_depto?.toString() === filters.value.departamento.toString()
        );
      }
      
      if (filters.value.municipio) {
        municipiosParaMecanismos = municipiosParaMecanismos.filter(m => 
          m.cod_municipio?.toString() === filters.value.municipio.toString()
        );
      }
      
      if (filters.value.territorial) {
        municipiosParaMecanismos = municipiosParaMecanismos.filter(m => 
          m.nom_territorial === filters.value.territorial
        );
      }
      
      const mecanismosUsados = new Set(
        municipiosParaMecanismos
          .map(m => m.mecanismo_general)
          .filter(mg => mg && mg.trim() !== '')
      );
      
      return mecanismosGenerales.value.filter(mg => mecanismosUsados.has(mg.cod_mecanismo));
    });

    // 5. Mecanismos Detalle (filtrados por TODOS los anteriores)
    const mecanismosDetalleDisponibles = computed(() => {
      let municipiosParaMecanismosDetalle = [...municipiosList.value];
      
      // Aplicar TODOS los filtros anteriores
      if (searchTerm.value.trim()) {
        const search = searchTerm.value.toLowerCase();
        municipiosParaMecanismosDetalle = municipiosParaMecanismosDetalle.filter(m => 
          m.nom_municipio?.toLowerCase().includes(search) ||
          m.cod_municipio?.toString().includes(search)
        );
      }
      
      if (filters.value.departamento) {
        municipiosParaMecanismosDetalle = municipiosParaMecanismosDetalle.filter(m => 
          m.cod_depto?.toString() === filters.value.departamento.toString()
        );
      }
      
      if (filters.value.municipio) {
        municipiosParaMecanismosDetalle = municipiosParaMecanismosDetalle.filter(m => 
          m.cod_municipio?.toString() === filters.value.municipio.toString()
        );
      }
      
      if (filters.value.territorial) {
        municipiosParaMecanismosDetalle = municipiosParaMecanismosDetalle.filter(m => 
          m.nom_territorial === filters.value.territorial
        );
      }
      
      if (filters.value.mecanismoGeneral) {
        municipiosParaMecanismosDetalle = municipiosParaMecanismosDetalle.filter(m => 
          m.mecanismo_general === filters.value.mecanismoGeneral
        );
      }
      
      const mecanismosDetalleUsados = new Set(
        municipiosParaMecanismosDetalle
          .map(m => m.mecanismo_detalle)
          .filter(md => md && md.trim() !== '')
      );
      
      return mecanismosDetalle.value.filter(md => mecanismosDetalleUsados.has(md.cod_mecanismo_detalle));
    });

    // 6. Grupos (filtrados por TODOS los anteriores)
    const gruposDisponibles = computed(() => {
      let municipiosParaGrupos = [...municipiosList.value];
      
      // Aplicar TODOS los filtros anteriores
      if (searchTerm.value.trim()) {
        const search = searchTerm.value.toLowerCase();
        municipiosParaGrupos = municipiosParaGrupos.filter(m => 
          m.nom_municipio?.toLowerCase().includes(search) ||
          m.cod_municipio?.toString().includes(search)
        );
      }
      
      if (filters.value.departamento) {
        municipiosParaGrupos = municipiosParaGrupos.filter(m => 
          m.cod_depto?.toString() === filters.value.departamento.toString()
        );
      }
      
      if (filters.value.municipio) {
        municipiosParaGrupos = municipiosParaGrupos.filter(m => 
          m.cod_municipio?.toString() === filters.value.municipio.toString()
        );
      }
      
      if (filters.value.territorial) {
        municipiosParaGrupos = municipiosParaGrupos.filter(m => 
          m.nom_territorial === filters.value.territorial
        );
      }
      
      if (filters.value.mecanismoGeneral) {
        municipiosParaGrupos = municipiosParaGrupos.filter(m => 
          m.mecanismo_general === filters.value.mecanismoGeneral
        );
      }
      
      if (filters.value.mecanismoDetalle) {
        municipiosParaGrupos = municipiosParaGrupos.filter(m => 
          m.mecanismo_detalle === filters.value.mecanismoDetalle
        );
      }
      
      const gruposUsados = new Set(
        municipiosParaGrupos
          .map(m => m.grupo)
          .filter(g => g && g.trim() !== '')
      );
      
      return grupos.value.filter(g => gruposUsados.has(g.cod_grupo));
    });

    // **FUNCIONES DE NAVEGACIÓN Y FILTROS**
    
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
    
    const goToPage = (page: number) => {
      currentPage.value = page;
    };
    
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
      
      if (filters.value.municipio) {
        const municipio = municipiosList.value.find(m => 
          m.cod_municipio.toString() === filters.value.municipio.toString()
        );
        if (municipio && municipio.cod_depto) {
          filters.value.departamento = municipio.cod_depto.toString();
        }
      }
    };
    

    const showDetalleModal = async (detalle) => {
      console.log('🔍 Mostrando modal para detalle:', detalle.cod_detalle);
      
      // Asignar el detalle seleccionado
      detalleSeleccionado.value = detalle;
      detalleModalVisible.value = true;
      
      // ✅ AUTO-SCROLL AL MODAL - ESPERAR A QUE SE RENDERICE
      await nextTick(); // Esperar al siguiente ciclo de renderizado
      
      // ✅ MÉTODO 1: Scroll suave al inicio de la página
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
      
      // ✅ MÉTODO 2: Enfocar el modal para asegurar que es visible
      setTimeout(() => {
        const modalElement = document.querySelector('.modal-overlay');
        if (modalElement) {
          modalElement.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
          });
          
          // ✅ OPCIONAL: Focus para accesibilidad
          const modalContent = modalElement.querySelector('.modal-content');
          if (modalContent) {
            modalContent.focus();
          }
        }
      }, 100); // Pequeño delay para asegurar que el modal está renderizado
      
      // ✅ BLOQUEAR SCROLL DEL BODY MIENTRAS EL MODAL ESTÁ ABIERTO
      document.body.style.overflow = 'hidden';
    };

    // ✅ FUNCIÓN PARA CERRAR MODAL CON RESTAURACIÓN DE SCROLL
    const cerrarDetalleModal = () => {
      detalleModalVisible.value = false;
      detalleSeleccionado.value = null;
      
      // ✅ RESTAURAR SCROLL DEL BODY
      document.body.style.overflow = 'auto';
    };


    const handleFilter = () => {
      currentPage.value = 1;
    };
    
    const formatArea = (area) => {
    if (!area) return 'No disponible';
    
    // Convertir a número
    const numero = parseFloat(area);
    if (isNaN(numero)) return area;
    
    // Formatear con separadores de miles
    return numero.toLocaleString('es-CO', { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 2 
    });
  };

    const clearAllFilters = () => {
      searchTerm.value = '';
      filters.value = {
        departamento: '',
        municipio: '',
        territorial: '',
        mecanismoGeneral: '',
        mecanismoDetalle: '',
        grupo: ''
      };
      currentPage.value = 1;
    };

    // **FUNCIONES DE UTILIDAD**
    
    const formatDate = (dateString: string | null): string => {
      if (!dateString) return 'N/A';
      try {
        return format(parseISO(dateString), 'dd/MM/yyyy', { locale: es });
      } catch (error) {
        return dateString;
      }
    };
    
    const getNombreDepartamento = (codDepto: number | string): string => {
      if (!codDepto) return 'N/A';
      const depto = departamentos.value.find(d => d.cod_depto.toString() === codDepto.toString());
      return depto ? depto.nom_depto : 'N/A';
    };

    const getInsumoCount = (municipioId: number): number => {
      const municipio = municipiosList.value.find(m => m.cod_municipio === municipioId);
      if (municipio && municipio.insumos_count !== undefined) {
        return municipio.insumos_count;
      }
      
      if (selectedMunicipioId.value === municipioId && municipioInsumos.value.length > 0) {
        return municipioInsumos.value.length;
      }
      
      return 0;
    };
    
    const getNombreCategoria = (categoriaId: number | string): string => {
      if (!categoriaId) return 'N/A';
      const categoria = categorias.value.find(c => c.cod_categoria.toString() === categoriaId.toString());
      return categoria ? categoria.nom_categoria : 'N/A';
    };
    
    const getNombreClasificacion = (clasificacionId: number | string): string => {
      if (!clasificacionId) return 'N/A';
      const clasificacion = municipioClasificaciones.value.find(c => c.cod_clasificacion.toString() === clasificacionId.toString());
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

// ========================================
// 🚨 FIX URGENTE: ELIMINAR LOOP INFINITO
// ========================================

// ❌ PROBLEMA: getClasificaciones llama getClasificacionesFiltradas y viceversa
// ✅ SOLUCIÓN: Crear función independiente para el MODAL

// ========================================
// 1. FUNCIÓN ORIGINAL getClasificaciones (NO TOCAR)
// ========================================
// Dejar la función getClasificaciones ORIGINAL como está:
// ✅ 1. AGREGAR NUEVO ESTADO REACTIVO
// En la sección de estados reactivos, agregar:


// ✅ 2. COMPUTED PARA DETECTAR SI MOSTRAR FILTROS DE INFO CATASTRAL
const mostrarFiltrosInfoCatastral = computed(() => {
  return filtroClasificacionPre.value === 'Información Catastral' || 
         filtroClasificacionPre.value === 'Informacion Catastral' ||
         filtroClasificacionPre.value.toLowerCase().includes('catastral');
});

// ✅ 3. FUNCIÓN PARA EXTRAER TIPO DE INFO CATASTRAL DESDE LA RUTA
const getTipoInfoCatastralFromPath = (pathFile: string): string => {
  if (!pathFile) return 'N/A';
  
  // Normalizar separadores
  const normalizedPath = pathFile.replace(/\\/g, '/');
  
  // Buscar el patrón /03_info_catas/XX_TIPO/
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

// ✅ 4. FUNCIÓN PARA OBTENER CLASE CSS DEL TIPO
const getTipoInfoCatastralClass = (pathFile: string): string => {
  const tipo = getTipoInfoCatastralFromPath(pathFile);
  
  switch (tipo) {
    case 'R1 & R2': return 'tipo-r1r2';
    case 'GDB': return 'tipo-gdb';
    case 'Tablas Terreno & Construcción': return 'tipo-tablas';
    case 'Estudio ZHF & ZHG': return 'tipo-estudio';
    default: return 'tipo-default';
  }
};

// ✅ 5. COMPUTED PARA TIPOS ÚNICOS DE INFO CATASTRAL
const tiposInfoCatastralUnicos = computed(() => {
  if (!mostrarFiltrosInfoCatastral.value) return [];
  
  const tipos = new Set<string>();
  
  municipioArchivos.value.forEach(archivo => {
    if (archivo.path_file) {
      const tipo = getTipoInfoCatastralFromPath(archivo.path_file);
      if (tipo !== 'N/A') {
        tipos.add(tipo);
      }
    }
  });
  
  // Ordenar según el orden lógico
  const ordenTipos = ['R1 & R2', 'GDB', 'Tablas Terreno & Construcción', 'Estudio ZHF & ZHG'];
  return ordenTipos.filter(tipo => tipos.has(tipo));
});

// ========================================
// 2. NUEVA FUNCIÓN ESPECÍFICA PARA EL MODAL
// ========================================
const getClasificacionesParaModal = (insumoId: number): any[] => {
  // Obtener clasificaciones originales SIN llamar a getClasificacionesFiltradas
  const clasificacionesOriginales = municipioClasificaciones.value.filter(c => c.cod_insumo === insumoId);
  
  const insumo = municipioInsumos.value.find(i => i.cod_insumo === insumoId);
  if (!insumo) return clasificacionesOriginales;
  
  const categoria = getNombreCategoria(insumo.cod_categoria);
  
  // ✅ PARA INFORMACIÓN CATASTRAL: Generar 4 clasificaciones HIJAS
  if (categoria.toLowerCase().includes('catastral')) {
    // Buscar la clasificación padre para obtener su ruta
    const clasificacionPadre = clasificacionesOriginales.find(c => 
      c.nombre && c.nombre.toLowerCase().includes('catastral')
    );
    
    // Obtener ruta base del padre (debe terminar en \03_info_catas)
    const rutaBase = clasificacionPadre?.ruta || '';
    
    // Generar las 4 clasificaciones hijas con rutas específicas
    return [
      {
        cod_clasificacion: `${insumoId}_R1R2`,
        cod_insumo: insumoId,
        nombre: 'R1 & R2',
        ruta: `${rutaBase}\\01_r1_r2`,
        descripcion: 'Registros R1 y R2 - Información de terrenos y propietarios',
        observacion: 'Archivos de registros catastrales R1 y R2'
      },
      {
        cod_clasificacion: `${insumoId}_GDB`,
        cod_insumo: insumoId,
        nombre: 'GDB',
        ruta: `${rutaBase}\\02_gdb`,
        descripcion: 'Base de Datos Geográfica - Información espacial catastral',
        observacion: 'Geodatabase con información catastral vectorial'
      },
      {
        cod_clasificacion: `${insumoId}_TABLAS`,
        cod_insumo: insumoId,
        nombre: 'Tablas Terreno & Construcción',
        ruta: `${rutaBase}\\03_tab_terr_constr`,
        descripcion: 'Tablas de terreno y construcción - Información alfanumérica',
        observacion: 'Tablas con información detallada de terrenos y construcciones'
      },
      {
        cod_clasificacion: `${insumoId}_ESTUDIO`,
        cod_insumo: insumoId,
        nombre: 'Estudio ZHF & ZHG',
        ruta: `${rutaBase}\\04_estu_zhf_zhg`,
        descripcion: 'Estudio de Zonas Homogéneas Físicas y Geoeconómicas',
        observacion: 'Estudios de zonificación homogénea para avalúos catastrales'
      }
    ];
  }
  
  // ✅ PARA CARTOGRAFÍA BÁSICA: Filtrar duplicado genérico
  if (categoria.toLowerCase().includes('cartograf')) {
    return clasificacionesOriginales.filter(clasif => 
      clasif.nombre.trim().toLowerCase() !== 'cartografia basica'
    );
  }
  
  // Para otras categorías, devolver las originales
  return clasificacionesOriginales;
};

const getClasificaciones = (insumoId: number): any[] => {
  return municipioClasificaciones.value.filter(c => c.cod_insumo === insumoId);
};
    
    const getClasificacionesCount = (insumoId: number): number => {
  const insumo = municipioInsumos.value.find(i => i.cod_insumo === insumoId);
  if (!insumo) return 0;
  
  const categoria = getNombreCategoria(insumo.cod_categoria);
  
  // ✅ INFORMACIÓN CATASTRAL: Siempre 4 (las 4 hijas)
  if (categoria.toLowerCase().includes('catastral')) {
    return 4;
  }
  
  // ✅ CARTOGRAFÍA BÁSICA: Siempre 3
  if (categoria.toLowerCase().includes('cartograf')) {
    return 3;
  }
  
  // Para otras categorías, contar las clasificaciones reales
  return getClasificaciones(insumoId).length;
};
    
    const getDetallesCount = (clasificacionId: number): number => {
      return municipioDetalles.value.filter(d => d.cod_clasificacion === clasificacionId).length;
    };
    
    const getDetallesCountForInsumo = (insumoId: number): number => {
      const clasificacionesIds = getClasificaciones(insumoId).map(c => c.cod_clasificacion);
      return municipioDetalles.value.filter(d => clasificacionesIds.includes(d.cod_clasificacion)).length;
    };

    const getTipoInsumoNombre = (tipo: any) => {
      if (!tipo) return 'Desconocido';
      
      if (typeof tipo === 'object' && tipo !== null && tipo.tipo_insumo) {
        return tipo.tipo_insumo;
      }
      
      if (typeof tipo === 'string') {
        return tipo;
      }
      
      return String(tipo);
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
        case 'jpg':
        case 'jpeg':
        case 'png':
        case 'gif':
          return 'image';
        case 'zip':
        case 'rar':
          return 'folder_zip';
        case 'gdb':
          return 'storage';
        default:
          return 'insert_drive_file';
      }
    };

    const getFileExtension = (fileName: string): string => {
      if (!fileName) return '';
      return fileName.split('.').pop()?.toLowerCase() || '';
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

    const isCartografiaBasica = (insumoId: number): boolean => {
      const insumo = municipioInsumos.value.find(i => i.cod_insumo === insumoId);
      if (!insumo) return false;
      
      const categoria = getNombreCategoria(insumo.cod_categoria);
      return categoria.toLowerCase().includes('cartograf');
    };
    
    const getInsumoCategoria = (insumoId: number): number | string => {
      const insumo = municipioInsumos.value.find(i => i.cod_insumo === insumoId);
      return insumo ? insumo.cod_categoria : '';
    };
    
    const getNombreCategoriaByInsumo = (insumoId: number): string => {
      const insumo = municipioInsumos.value.find(i => i.cod_insumo === insumoId);
      return insumo ? getNombreCategoria(insumo.cod_categoria) : 'No especificado';
    };
    
    const getCartografiaSubtipo = (ruta: string): string => {
      if (!ruta) return 'No especificado';
      
      const CARTO_BASIC_SUBTIPOS = {
        "02_vect": {
          "nombre": "Cartografía Básica (Vectorial)",
          "ruta_sufijo": "\\02_vect"
        },
        "01_rast\\01_orto": {
          "nombre": "Ortoimagen",
          "ruta_sufijo": "\\01_rast\\01_orto"
        },
        "01_rast\\02_dtm": {
          "nombre": "Modelo Digital Terreno",
          "ruta_sufijo": "\\01_rast\\02_dtm"
        }
        ,
        "01_rast\\02_mtd": {
          "nombre": "Modelo Digital Terreno",
          "ruta_sufijo": "\\01_rast\\02_mtd"
        }
      };
      
      for (const [key, value] of Object.entries(CARTO_BASIC_SUBTIPOS)) {
        if (ruta.includes(value.ruta_sufijo)) {
          return value.nombre;
        }
      }
      
      return 'Cartografía Básica';
    };



    const getDetalleNombre = (detalleId: number): string => {
      if (!detalleId) return 'N/A';
      const detalle = municipioDetalles.value.find(d => d.cod_detalle === detalleId);
      return detalle ? `Detalle #${detalle.cod_detalle}` : `Detalle #${detalleId}`;
    };


    const selectMunicipio = async (municipioId: number) => {
      // ✅ VERIFICAR PERMISOS ANTES DE CARGAR
      if (!tieneAccesoAMunicipio(municipioId)) {
        showNotification('No tiene permisos para acceder a este municipio', 'error');
        return;
      }
      
      try {
        loading.value = true;
        selectedMunicipioId.value = municipioId;
        
        console.log(`Seleccionando municipio ${municipioId}`);
        
        const [municipio, insumos, clasificaciones, detalles] = await Promise.allSettled([
          getMunicipioById(municipioId),
          getInsumosByMunicipio(municipioId),
          getClasificacionesByMunicipio(municipioId),
          getDetallesByMunicipio(municipioId)
        ]);
        
        selectedMunicipio.value = municipio.status === 'fulfilled' ? municipio.value : null;
        municipioInsumos.value = insumos.status === 'fulfilled' ? insumos.value : [];
        municipioClasificaciones.value = clasificaciones.status === 'fulfilled' ? clasificaciones.value : [];
        municipioDetalles.value = detalles.status === 'fulfilled' ? detalles.value : [];
        
        // ✅ DEBUG: Ver qué detalles se cargaron
        console.log('📊 Detalles originales cargados:', municipioDetalles.value.length);
        if (municipioDetalles.value.length > 0) {
          console.log('📋 Primer detalle original:', municipioDetalles.value[0]);
        }
        
        // ✅ ENRIQUECIMIENTO CON MANEJO DE ERRORES Y DEBUG
        if (municipioDetalles.value && municipioDetalles.value.length > 0) {
          try {
            console.log('🔄 Iniciando enriquecimiento de detalles...');
            const detallesEnriquecidos = await enriquecerDetallesConCentrosPoblados(municipioDetalles.value);
            municipioDetalles.value = detallesEnriquecidos;
            
            console.log('✅ Detalles enriquecidos asignados');
            if (municipioDetalles.value.length > 0) {
              console.log('📋 Primer detalle enriquecido:', municipioDetalles.value[0]);
            }
            
          } catch (enrichError) {
            console.error('❌ Error en el enriquecimiento de detalles:', enrichError);
          }
        }
        
        // Cargar datos adicionales
        await cargarArchivosPre();
        await loadArchivosPostForMunicipio(municipioId);
        await cargarConceptos();
        await loadProfesionalesForMunicipio(municipioId);
        
        router.push({ 
          query: { 
            ...route.query,
            municipio: municipioId.toString() 
          }
        });
        
        console.log(`Municipio ${municipioId} cargado exitosamente`);
        
      } catch (err: any) {
        console.error('Error loading municipality data:', err);
        showNotification('Error loading municipality data: ' + (err.message || 'Unknown error'), 'error');
      } finally {
        loading.value = false;
      }
    };


    const enriquecerDetallesConCentrosPoblados = async (detalles) => {
      console.log(`🔄 Enriqueciendo ${detalles.length} detalles con información de centros poblados...`);
      
      const detallesEnriquecidos = await Promise.all(detalles.map(async (detalle, index) => {
        let detalleEnriquecido = { ...detalle };
        
        // ✅ LÓGICA EXACTA DE DetallesList.vue
        if (detalle.cod_centro_poblado) {
          try {
            console.log(`🔍 [${index + 1}/${detalles.length}] Buscando centro poblado ${detalle.cod_centro_poblado}...`);
            
            // ✅ USAR AXIOS COMO EN DetallesList.vue (NO api.get)
            const centroPobladoResponse = await axios.get(
              `${API_URL}/preoperacion/centros-poblados/${detalle.cod_centro_poblado}/`
            );
            
            // ✅ ASIGNAR CORRECTAMENTE LOS DATOS (igual que DetallesList.vue)
            detalleEnriquecido.centro_poblado_codigo = detalle.cod_centro_poblado;
            detalleEnriquecido.centro_poblado_nombre = centroPobladoResponse.data.nom_centro_poblado;
            
            console.log(`✅ Centro poblado encontrado: ${centroPobladoResponse.data.nom_centro_poblado}`);
            
          } catch (error) {
            console.error(`❌ Error al obtener centro poblado ${detalle.cod_centro_poblado}:`, error);
            // Si hay error, mantener solo el código
            detalleEnriquecido.centro_poblado_codigo = detalle.cod_centro_poblado;
            detalleEnriquecido.centro_poblado_nombre = `Centro ${detalle.cod_centro_poblado}`;
          }
        }
        
        return detalleEnriquecido;
      }));
      
      console.log(`✅ Enriquecimiento completado: ${detallesEnriquecidos.length} detalles procesados`);
      return detallesEnriquecidos;
    };


    const formatZonaConCentroPoblado = (detalle) => {
      if (!detalle.zona) return 'No disponible';
      if (detalle.zona === 'CENTROS POBLADOS' && detalle.cod_centro_poblado) {
        const nombreCentro = detalle.centro_poblado_nombre || 'Cargando...';
        return `CP: ${nombreCentro}`;
      }
      return detalle.zona;
    };



    const clearSelectedMunicipio = () => {
      selectedMunicipioId.value = null;
      selectedMunicipio.value = null;
      
      // ✅ LIMPIAR FILTROS DE CARTOGRAFÍA BÁSICA
      limpiarFiltrosPreoperacion();
      
      const query = { ...route.query };
      delete query.municipio;
      router.push({ query });
    };

    const irAInsumosPorCategoria = (categoriaId: number) => {
      activeTab.value = 'insumos';
      insumoFilter.value = categoriaId.toString();
      insumoSearch.value = '';
      tipoInsumoFilter.value = '';
    };

    const viewInsumoDetails = (insumo) => {
      modalDetalleInsumo.value.insumo = insumo;
      modalDetalleInsumo.value.mostrar = true;
    };

    const viewClasificacionDetalles = (clasificacion: any) => {
      activeTab.value = 'detalles';
    };

    // **FUNCIONES DE ARCHIVOS**

    const cargarArchivosPre = async () => {
      try {
        archivosPreLoading.value = true;
        archivosPreError.value = null;
        
        if (!selectedMunicipioId.value) {
          municipioArchivos.value = [];
          return;
        }
        
        const response = await fetch(`${API_URL}/preoperacion/archivos-pre/por_municipio/?municipio_id=${selectedMunicipioId.value}`, {
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          if (response.status === 404) {
            municipioArchivos.value = [];
            return;
          } else {
            throw new Error(`Error HTTP: ${response.status} ${response.statusText}`);
          }
        }
        
        const archivos = await response.json();
        municipioArchivos.value = Array.isArray(archivos) ? archivos : [];
        
        console.log(`Cargados ${municipioArchivos.value.length} archivos de preoperación`);
        
      } catch (error) {
        console.error('Error cargando archivos de preoperación:', error);
        archivosPreError.value = error.message || 'Error al cargar archivos de preoperación. Intente nuevamente.';
        municipioArchivos.value = [];
      } finally {
        archivosPreLoading.value = false;
      }
    };

    const loadArchivosPostForMunicipio = async (municipioId: number) => {
      try {
        archivosPostLoading.value = true;
        archivosPostError.value = null;
        
        console.log(`Cargando archivos de postoperación para municipio ${municipioId}`);
        
        const response = await fetch(`${API_URL}/postoperacion/archivos/por_municipio/?municipio_id=${municipioId}`, {
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          if (response.status === 404) {
            municipioArchivosPost.value = [];
            return;
          } else {
            throw new Error(`Error HTTP: ${response.status} ${response.statusText}`);
          }
        }
        
        const archivos = await response.json();
        municipioArchivosPost.value = Array.isArray(archivos) ? archivos : [];
        
        console.log(`Cargados ${municipioArchivosPost.value.length} archivos de postoperación`);
        
      } catch (error) {
        console.error('Error cargando archivos de postoperación:', error);
        archivosPostError.value = error.message || 'Error al cargar archivos de postoperación. Intente nuevamente.';
        municipioArchivosPost.value = [];
      } finally {
        archivosPostLoading.value = false;
      }
    };

const cargarConceptos = async () => {
  try {
    conceptosLoading.value = true;
    conceptosError.value = null;
    municipioConceptos.value = [];
    
    if (!selectedMunicipioId.value) {
      conceptosLoading.value = false;
      return;
    }
    
    console.log(`Cargando conceptos para municipio ${selectedMunicipioId.value}`);
    
    // ✅ USAR FILTRO POR DEPARTAMENTO + MUNICIPIO (así funciona el backend)
    const municipio = selectedMunicipio.value;
    const departamentoId = municipio?.cod_depto;
    
    const url = `${API_URL}/preoperacion/conceptos/buscar/?departamento=${departamentoId}&municipio=${selectedMunicipioId.value}`;
    
    const response = await axios.get(url, {
      headers: {
        'Authorization': `Token ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      }
    });
    
    const conceptos = response.data || [];
    
    municipioConceptos.value = conceptos.map(concepto => ({
      ...concepto,
      municipioId: selectedMunicipioId.value,
      municipio: selectedMunicipio.value?.nom_municipio || 'Municipio no disponible'
    }));
    
    console.log(`✅ Cargados ${municipioConceptos.value.length} conceptos únicos para el municipio ${selectedMunicipioId.value}`);
    
  } catch (error) {
    console.error("Error al cargar conceptos:", error);
    conceptosError.value = "Error al cargar conceptos. Por favor, intente nuevamente.";
    municipioConceptos.value = [];
  } finally {
    conceptosLoading.value = false;
  }
};

const filtrosNivelesPost = ref({
  nivel1: '',
  nivel2: '',
  nivel3: '',
  nivel4: '',
  nivel5: ''
});
const maxNivelesPost = ref(0);

// ✅ FUNCIÓN PARA EXTRAER NIVELES DE CARPETAS DESPUÉS DE 03_post
const extraerNivelesDeRuta = (rutaCompleta: string): string[] => {
  if (!rutaCompleta) return [];
  
  // Normalizar separadores
  const rutaNormalizada = rutaCompleta.replace(/\//g, '\\');
  
  // Buscar la posición de 03_post
  const indicePost = rutaNormalizada.indexOf('03_post\\');
  if (indicePost === -1) return [];
  
  // Obtener todo después de 03_post\
  const despuesDePost = rutaNormalizada.substring(indicePost + 8); // 8 = longitud de "03_post\"
  
  // Dividir por \ para obtener carpetas y archivo
  const partes = despuesDePost.split('\\').filter(p => p);
  
  // Remover el último elemento (que es el archivo)
  if (partes.length > 0) {
    partes.pop();
  }
  
  return partes;
};

// ✅ COMPUTED PARA OPCIONES DE CADA NIVEL
const opcionesNivel1Post = computed(() => {
  const opciones = new Set<string>();
  
  municipioArchivosPost.value.forEach(archivo => {
    if (archivo.ruta_completa) {
      const niveles = extraerNivelesDeRuta(archivo.ruta_completa);
      if (niveles[0]) {
        opciones.add(niveles[0]);
      }
    }
  });
  
  return Array.from(opciones).sort();
});

const opcionesNivel2Post = computed(() => {
  if (!filtrosNivelesPost.value.nivel1) return [];
  
  const opciones = new Set<string>();
  
  municipioArchivosPost.value.forEach(archivo => {
    if (archivo.ruta_completa) {
      const niveles = extraerNivelesDeRuta(archivo.ruta_completa);
      if (niveles[0] === filtrosNivelesPost.value.nivel1 && niveles[1]) {
        opciones.add(niveles[1]);
      }
    }
  });
  
  return Array.from(opciones).sort();
});

const opcionesNivel3Post = computed(() => {
  if (!filtrosNivelesPost.value.nivel1 || !filtrosNivelesPost.value.nivel2) return [];
  
  const opciones = new Set<string>();
  
  municipioArchivosPost.value.forEach(archivo => {
    if (archivo.ruta_completa) {
      const niveles = extraerNivelesDeRuta(archivo.ruta_completa);
      if (niveles[0] === filtrosNivelesPost.value.nivel1 && 
          niveles[1] === filtrosNivelesPost.value.nivel2 && 
          niveles[2]) {
        opciones.add(niveles[2]);
      }
    }
  });
  
  return Array.from(opciones).sort();
});

const opcionesNivel4Post = computed(() => {
  if (!filtrosNivelesPost.value.nivel1 || 
      !filtrosNivelesPost.value.nivel2 || 
      !filtrosNivelesPost.value.nivel3) return [];
  
  const opciones = new Set<string>();
  
  municipioArchivosPost.value.forEach(archivo => {
    if (archivo.ruta_completa) {
      const niveles = extraerNivelesDeRuta(archivo.ruta_completa);
      if (niveles[0] === filtrosNivelesPost.value.nivel1 && 
          niveles[1] === filtrosNivelesPost.value.nivel2 && 
          niveles[2] === filtrosNivelesPost.value.nivel3 && 
          niveles[3]) {
        opciones.add(niveles[3]);
      }
    }
  });
  
  return Array.from(opciones).sort();
});

const opcionesNivel5Post = computed(() => {
  if (!filtrosNivelesPost.value.nivel1 || 
      !filtrosNivelesPost.value.nivel2 || 
      !filtrosNivelesPost.value.nivel3 ||
      !filtrosNivelesPost.value.nivel4) return [];
  
  const opciones = new Set<string>();
  
  municipioArchivosPost.value.forEach(archivo => {
    if (archivo.ruta_completa) {
      const niveles = extraerNivelesDeRuta(archivo.ruta_completa);
      if (niveles[0] === filtrosNivelesPost.value.nivel1 && 
          niveles[1] === filtrosNivelesPost.value.nivel2 && 
          niveles[2] === filtrosNivelesPost.value.nivel3 && 
          niveles[3] === filtrosNivelesPost.value.nivel4 &&
          niveles[4]) {
        opciones.add(niveles[4]);
      }
    }
  });
  
  return Array.from(opciones).sort();
});

// ✅ COMPUTED PARA DETECTAR MÁXIMO NIVEL DE PROFUNDIDAD
const maxNivelProfundidad = computed(() => {
  let maxNivel = 0;
  
  municipioArchivosPost.value.forEach(archivo => {
    if (archivo.ruta_completa) {
      const niveles = extraerNivelesDeRuta(archivo.ruta_completa);
      if (niveles.length > maxNivel) {
        maxNivel = niveles.length;
      }
    }
  });
  
  return maxNivel;
});

// ✅ FUNCIÓN PARA LIMPIAR NIVELES INFERIORES
const handleNivelChange = (nivel: number) => {
  // Limpiar todos los niveles inferiores cuando cambie uno superior
  switch(nivel) {
    case 1:
      filtrosNivelesPost.value.nivel2 = '';
      filtrosNivelesPost.value.nivel3 = '';
      filtrosNivelesPost.value.nivel4 = '';
      filtrosNivelesPost.value.nivel5 = '';
      break;
    case 2:
      filtrosNivelesPost.value.nivel3 = '';
      filtrosNivelesPost.value.nivel4 = '';
      filtrosNivelesPost.value.nivel5 = '';
      break;
    case 3:
      filtrosNivelesPost.value.nivel4 = '';
      filtrosNivelesPost.value.nivel5 = '';
      break;
    case 4:
      filtrosNivelesPost.value.nivel5 = '';
      break;
  }
};

// ✅ FUNCIÓN PARA LIMPIAR TODOS LOS FILTROS DE POSTOPERACIÓN
const limpiarFiltrosPostoperacion = () => {
  filtrosNivelesPost.value = {
    nivel1: '',
    nivel2: '',
    nivel3: '',
    nivel4: '',
    nivel5: ''
  };
  filtroNombreArchivoPost.value = '';
};

// ✅ COMPUTED PARA VERIFICAR SI HAY FILTROS ACTIVOS
const hayFiltrosActivosPost = computed(() => {
  return filtrosNivelesPost.value.nivel1 || 
         filtrosNivelesPost.value.nivel2 || 
         filtrosNivelesPost.value.nivel3 || 
         filtrosNivelesPost.value.nivel4 || 
         filtrosNivelesPost.value.nivel5 ||
         filtroNombreArchivoPost.value;
});

    const loadProfesionalesForMunicipio = async (municipioId: number) => {
      try {
        console.log(`Cargando profesionales para municipio ${municipioId}...`);
        
        const url = `${API_URL}/preoperacion/municipios/${municipioId}/profesionales/`;
        
        const response = await fetch(url, {
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`
          }
        });
        
        if (!response.ok) {
          console.warn(`Error al cargar profesionales: ${response.status} ${response.statusText}`);
          municipioProfesionales.value = [];
          return;
        }
        
        const data = await response.json();
        const profesionales = Array.isArray(data.results) ? data.results : 
                            Array.isArray(data) ? data : [];
        
        municipioProfesionales.value = profesionales;
        console.log(`Cargados ${municipioProfesionales.value.length} profesionales`);
      } catch (error) {
        console.error('Error cargando profesionales para el municipio:', error);
        municipioProfesionales.value = [];
      }
    };

    const viewArchivo = async (archivo: any) => {
      if (!archivo.path_file) {
        showNotification('No hay ruta disponible para este archivo', 'warning');
        return;
      }
      
      try {
        // ✅ USAR API AXIOS (con token automático)
        const response = await api.get('/preoperacion/ver_pdf/', {
          params: { ruta: archivo.path_file },
          responseType: 'blob' // Importante para archivos
        });
        
        // Crear URL del blob para visualización
        const blob = new Blob([response], { type: response.type || 'application/octet-stream' });
        const url = window.URL.createObjectURL(blob);
        
        const fileName = obtenerNombreArchivo(archivo.path_file);
        const fileExtension = getFileExtension(fileName);
        
        if (['gdb', 'zip', 'rar', '7z'].includes(fileExtension)) {
          // Para archivos comprimidos, forzar descarga
          const link = document.createElement('a');
          link.href = url;
          link.download = fileName;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          showNotification(`Descargando: ${fileName}`, 'success');
        } else {
          // Para otros archivos, abrir en nueva ventana
          window.open(url, '_blank');
          showNotification(`Abriendo: ${fileName}`, 'info');
        }
        
        // Limpiar URL después de un tiempo
        setTimeout(() => window.URL.revokeObjectURL(url), 10000);
        
      } catch (error) {
        console.error('Error al visualizar archivo:', error);
        showNotification(`Error al abrir archivo: ${error.message}`, 'error');
      }
    };



    // APLICAR LO MISMO PARA POST-OPERACIÓN:
    const viewArchivoPost = async (archivo: any) => {
      if (!archivo.ruta_completa) {
        showNotification('No hay ruta disponible para este archivo', 'warning');
        return;
      }
      
      try {
        // ✅ USAR API AXIOS (con token automático)
        const response = await api.get('/preoperacion/ver_pdf/', {
          params: { ruta: archivo.ruta_completa },
          responseType: 'blob'
        });
        
        const blob = new Blob([response], { type: response.type || 'application/octet-stream' });
        const url = window.URL.createObjectURL(blob);
        
        const fileName = obtenerNombreArchivo(archivo.ruta_completa);
        const fileExtension = getFileExtension(fileName);
        
        if (['gdb', 'zip', 'rar', '7z'].includes(fileExtension)) {
          const link = document.createElement('a');
          link.href = url;
          link.download = fileName;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          showNotification(`Descargando: ${fileName}`, 'success');
        } else {
          window.open(url, '_blank');
          showNotification(`Abriendo: ${fileName}`, 'info');
        }
        
        setTimeout(() => window.URL.revokeObjectURL(url), 10000);
        
      } catch (error) {
        console.error('Error al visualizar archivo:', error);
        showNotification(`Error al abrir archivo: ${error.message}`, 'error');
      }
    };


    const downloadArchivo = async (archivo: any) => {
      if (!archivo.path_file) {
        showNotification('No hay ruta disponible para descargar este archivo', 'warning');
        return;
      }
      
      try {
        // 🔍 Detectar si puede ser archivo grande
        const rutaArchivo = archivo.path_file;
        const extension = rutaArchivo.toLowerCase().split('.').pop();
        const esTIF = extension === 'tif' || extension === 'tiff';
        const esArchivoGrande = esTIF || extension === 'gdb' || extension === 'zip';
        
        // 📋 Mostrar mensaje apropiado para archivos grandes
        if (esArchivoGrande) {
          showNotification('⏳ Preparando descarga de archivo grande... Esto puede tomar varios minutos.', 'info');
        } else {
          showNotification('📥 Descargando archivo...', 'info');
        }

        // ⚡ CONFIGURACIÓN ESPECIAL PARA ARCHIVOS GRANDES
        const timeoutConfig = esArchivoGrande 
          ? { timeout: 20 * 60 * 1000 } // 🕐 10 minutos para archivos grandes
          : { timeout: 60 * 1000 };     // 🕐 1 minuto para archivos normales

        console.log(`🔧 Configurando timeout: ${timeoutConfig.timeout / 1000} segundos`);

        // 🚀 USAR API AXIOS con timeout extendido
        const response = await api.get('/preoperacion/descargar_archivo/', {
          params: { ruta: rutaArchivo },
          responseType: 'blob',
          ...timeoutConfig,
          
          // 📊 OPCIONAL: Callback de progreso (si axios lo soporta)
          onDownloadProgress: (progressEvent) => {
            if (esArchivoGrande && progressEvent.total) {
              const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              console.log(`📥 Progreso descarga: ${percentCompleted}% (${(progressEvent.loaded / 1024 / 1024).toFixed(1)} MB)`);
              
              // Actualizar notificación cada 10%
              if (percentCompleted % 10 === 0) {
                showNotification(`📥 Descargando... ${percentCompleted}% completado`, 'info');
              }
            }
          }
        });
        
        console.log(`✅ Descarga completada. Tamaño: ${(response.size || 0) / 1024 / 1024} MB`);
        
        // ✅ Crear blob (ya sabemos que funciona con response directamente)
        const blob = new Blob([response]);
        
        // ⚠️ VALIDACIÓN: Verificar que el blob no esté vacío
        if (blob.size === 0) {
          throw new Error('❌ El archivo descargado está vacío. Intente nuevamente.');
        }
        
        // 📁 Procesar nombre del archivo
        let nombreArchivo = obtenerNombreArchivo(rutaArchivo);
        if (esTIF) {
          nombreArchivo = nombreArchivo.replace(/\.(tif|tiff)$/i, '.zip');
        }
        
        // 💾 Crear enlace de descarga
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = nombreArchivo;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // 🗑️ Limpiar URL después de un tiempo
        setTimeout(() => {
          window.URL.revokeObjectURL(url);
          console.log('🗑️ URL de descarga limpiada');
        }, 30000); // 30 segundos para archivos grandes
        
        // ✅ Mensaje de éxito con tamaño
        const tamanoMB = (blob.size / 1024 / 1024).toFixed(1);
        showNotification(
          `✅ Descarga completada: ${nombreArchivo} (${tamanoMB} MB)`, 
          'success'
        );
        
      } catch (error) {
        console.error('❌ Error al descargar archivo:', error);
        
        // 🎯 Mensajes de error específicos para timeouts
        let mensajeError;
        if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
          mensajeError = `⏰ Tiempo de espera agotado. El archivo es muy grande y necesita más tiempo. Intente nuevamente o contacte al administrador.`;
        } else if (error.response?.status === 404) {
          mensajeError = '📁 Archivo no encontrado';
        } else if (error.response?.status === 403) {
          mensajeError = '🔒 No tiene permisos para descargar este archivo';
        } else if (error.response?.status === 500) {
          mensajeError = '⚙️ Error del servidor al procesar la descarga';
        } else {
          mensajeError = error.message || 'Error desconocido';
        }
        
        showNotification(`❌ Error: ${mensajeError}`, 'error');
      }
    };


    const downloadArchivoPost = async (archivo: any) => {
      if (!archivo.ruta_completa) {
        showNotification('No hay ruta disponible para descargar este archivo', 'warning');
        return;
      }
      
      try {
        // 🔍 Detectar si es archivo TIF
        const rutaArchivo = archivo.ruta_completa;
        const extension = rutaArchivo.toLowerCase().split('.').pop();
        const esTIF = extension === 'tif' || extension === 'tiff';
        
        // 📋 Mostrar mensaje apropiado
        if (esTIF) {
          showNotification('Preparando descarga del directorio completo (puede tomar un momento)...', 'info');
        } else {
          showNotification('Preparando descarga...', 'info');
        }

        // ✅ USAR API AXIOS (con token automático)  
        const response = await api.get('/preoperacion/descargar_archivo/', {
          params: { ruta: rutaArchivo },
          responseType: 'blob'
        });
        
        // ✅ FIX: Usar response.data en lugar de response
        const blob = new Blob([response.data]);
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        // 🎯 Determinar nombre de descarga apropiado
        let nombreDescarga;
        if (esTIF) {
          // Para TIF, extraer nombre del directorio padre
          const directorio = rutaArchivo.split(/[\\/]/).slice(-2, -1)[0] || 'ortofoto';
          nombreDescarga = `${directorio}_ortofotos_completo.zip`;
        } else {
          nombreDescarga = obtenerNombreArchivo(rutaArchivo);
        }
        
        link.download = nombreDescarga;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        window.URL.revokeObjectURL(url);
        
        // ✅ Mensaje de éxito diferenciado
        if (esTIF) {
          showNotification(`✅ Directorio descargado: ${nombreDescarga} (incluye archivos auxiliares)`, 'success');
        } else {
          showNotification(`✅ Archivo descargado: ${nombreDescarga}`, 'success');
        }
        
      } catch (error) {
        console.error('Error al descargar archivo:', error);
        
        // 🎯 Mensajes de error más específicos
        let mensajeError = 'Error desconocido';
        if (error.response?.status === 404) {
          mensajeError = 'Archivo no encontrado';
        } else if (error.response?.status === 403) {
          mensajeError = 'No tiene permisos para descargar este archivo';
        } else if (error.response?.status === 500) {
          mensajeError = 'Error del servidor al procesar la descarga';
        } else if (error.message) {
          mensajeError = error.message;
        }
        
        showNotification(`❌ Error al descargar: ${mensajeError}`, 'error');
      }
    };

    // ✅ FUNCIONES DEL MODAL DE DETALLES DE ARCHIVO
    const showArchivoDetails = (archivo: any, type: 'pre' | 'post') => {
      selectedArchivoDetails.value = archivo;
      archivoDetailsType.value = type;
      showArchivoDetailsModal.value = true;
    };

    const closeArchivoDetailsModal = () => {
      showArchivoDetailsModal.value = false;
      selectedArchivoDetails.value = null;
    };




    // Función para ver detalle completo de un detalle específico
const verDetalleCompleto = (detalle) => {
  modalDetalleDetalle.value.detalle = detalle;
  modalDetalleDetalle.value.mostrar = true;
};

// Función para ver detalles de una clasificación específica
const verDetallesDeClasificacion = (clasificacion) => {
  // Cambiar a la pestaña de detalles y filtrar por clasificación
  activeTab.value = 'detalles';
  // Cerrar modal de insumo si está abierto
  modalDetalleInsumo.value.mostrar = false;
  console.log('Ver detalles de clasificación:', clasificacion);
};

// Función para obtener detalles de un insumo específico para el modal
const getDetallesForInsumoModal = (insumoId) => {
  const clasificacionesIds = getClasificaciones(insumoId).map(c => c.cod_clasificacion);
  return municipioDetalles.value.filter(d => clasificacionesIds.includes(d.cod_clasificacion));
};

// Función para obtener conceptos de un detalle específico
const getConceptosDelDetalle = (codDetalle) => {
  return municipioConceptos.value.filter(c => c.cod_detalle === codDetalle);
};

// Función para contar conceptos de un insumo
const getConceptosCountForInsumo = (insumoId: number): number => {
  const categoria = getNombreCategoria(
    municipioInsumos.value.find(i => i.cod_insumo === insumoId)?.cod_categoria
  );
  
  // Para Información Catastral, usar el conteo de items manuales
  if (categoria.toLowerCase().includes('catastral')) {
    const itemsManuales = getItemsManuales(insumoId);
    return itemsManuales.length; // Siempre 4
  }
  
  // Para otras categorías, usar la lógica original
  const detallesIds = getDetallesForInsumoModal(insumoId).map(d => d.cod_detalle);
  let totalConceptos = 0;
  detallesIds.forEach(detalleId => {
    totalConceptos += getConceptosDelDetalle(detalleId).length;
  });
  return totalConceptos;
};

// Función para contar archivos de un insumo (aproximación)
const getArchivosCountForInsumo = (insumoId) => {
  // Esta función depende de si tienes archivos asociados
  // Por ahora retornamos un valor estimado basado en clasificaciones
  const clasificaciones = getClasificaciones(insumoId);
  return clasificaciones.length * 2; // Estimación: 2 archivos por clasificación
};

// Función para obtener clase CSS de estado
const getEstadoClass = (estado) => {
  if (!estado) return '';
  
  const estadoLower = estado.toLowerCase();
  if (estadoLower.includes('oficializado') || estadoLower.includes('aprobado')) return 'estado-oficializado';
  if (estadoLower.includes('produccion') || estadoLower.includes('proceso')) return 'estado-produccion';
  if (estadoLower.includes('pendiente')) return 'estado-pendiente';
  if (estadoLower.includes('rechazado')) return 'estado-rechazado';
  return 'estado-default';
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

// Función para ver todos los detalles de un insumo
const verTodosLosDetalles = (insumo) => {
  // Cerrar modal actual
  modalDetalleInsumo.value.mostrar = false;
  // Cambiar a pestaña de detalles
  activeTab.value = 'detalles';
};

// Función para ir a vista completa (redirigir a página específica)
const irAVistaCompleta = (insumo) => {
  router.push({ 
    name: 'DisposicionInsumoDetalle', 
    params: { id: insumo.cod_insumo } 
  });
};

// Función para ver PDF de concepto (igual que en EstadoProducto.vue)
const verDocumentoPDF = async (rutaPdf: string) => {
  if (!rutaPdf) {
    showNotification('No hay ruta PDF disponible', 'warning');
    return;
  }

  try {
    console.log('🔍 Abriendo PDF (ruta original):', rutaPdf);

    // Convertir ruta de Windows a Linux si es necesario
    // El backend espera rutas Linux, convertimos desde frontend para evitar problemas
    let rutaParaEnviar = rutaPdf;

    // Si la ruta tiene formato Windows (\\repositorio o //repositorio), convertir a Linux
    if (rutaPdf.includes('\\') || rutaPdf.includes('repositorio')) {
      const rutaConvertida = windowsToLinuxPath(rutaPdf);
      if (rutaConvertida && rutaConvertida !== rutaPdf) {
        rutaParaEnviar = rutaConvertida;
        console.log('🔄 Ruta convertida de Windows a Linux:', rutaParaEnviar);
      }
    }

    console.log('📤 Enviando ruta al backend:', rutaParaEnviar);

    // Usar axios directamente para mejor control de la respuesta
    const token = localStorage.getItem('token');
    const response = await axios.get(`${API_URL}/preoperacion/ver_pdf/`, {
      params: { ruta: rutaParaEnviar },
      headers: {
        'Authorization': `Token ${token}`
      },
      responseType: 'blob',
      // Importante: Validar que la respuesta sea exitosa
      validateStatus: (status) => status >= 200 && status < 300
    });

    // Verificar que la respuesta es realmente un PDF
    const contentType = response.headers['content-type'] || '';
    console.log('📥 Content-Type recibido:', contentType);

    if (contentType.includes('text/html') || contentType.includes('application/json')) {
      // Es un error del servidor, leer el mensaje
      const text = await response.data.text();
      console.error('❌ Error del servidor:', text);
      showNotification(`Error del servidor: ${text.substring(0, 100)}`, 'error');
      return;
    }

    // Crear blob con el tipo correcto
    const blob = new Blob([response.data], {
      type: contentType || 'application/pdf'
    });

    // Verificar que el blob tiene contenido
    if (blob.size === 0) {
      showNotification('El archivo PDF está vacío o no se pudo cargar.', 'error');
      return;
    }

    const url = window.URL.createObjectURL(blob);

    // Abrir en nueva ventana
    const newWindow = window.open(url, '_blank');

    if (!newWindow) {
      showNotification('El navegador bloqueó la ventana emergente. Permite ventanas emergentes para ver el PDF.', 'warning');
      // Fallback: descargar el archivo
      const a = document.createElement('a');
      a.href = url;
      a.download = rutaPdf.split(/[\\/]/).pop() || 'documento.pdf';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }

    // Limpiar URL después de un tiempo
    setTimeout(() => {
      window.URL.revokeObjectURL(url);
    }, 30000);

    console.log('✅ PDF abierto en nueva ventana');

  } catch (error: any) {
    console.error('❌ Error al abrir PDF:', error);

    // Intentar leer el mensaje de error del blob
    let errorMessage = 'Error al abrir el archivo PDF.';

    if (error.response?.data instanceof Blob) {
      try {
        const text = await error.response.data.text();
        console.error('Mensaje de error del servidor:', text);
        errorMessage = text.substring(0, 150) || errorMessage;
      } catch (e) {
        console.error('No se pudo leer el mensaje de error');
      }
    }

    if (error.response?.status === 404) {
      showNotification('El archivo PDF no se encontró en el servidor.', 'error');
    } else if (error.response?.status === 403) {
      showNotification('No tiene permisos para acceder a este archivo.', 'error');
    } else if (error.response?.status === 500) {
      showNotification(`Error del servidor: ${errorMessage}`, 'error');
    } else {
      showNotification('Error al abrir el archivo PDF. Por favor, inténtelo de nuevo.', 'error');
    }
  }
};


    // **FUNCIONES ADICIONALES**

    const editMunicipio = (municipio: any) => {
      showNotification(`Editar municipio ${municipio.nom_municipio}`, 'info');
    };

    const showCreateInsumoForMunicipio = (municipioId: number) => {
      showNotification(`Crear nuevo insumo para municipio ${municipioId}`, 'info');
    };





    const viewDetalleDetails = (detalle) => {
      modalDetalleDetalle.value.detalle = detalle;
      modalDetalleDetalle.value.mostrar = true;
    };


    const descargarInsumos = async (municipio: any) => {
      try {
        descargandoInsumos.value[municipio.cod_municipio] = true;
        
        showNotification(`Generando reporte de insumos para ${municipio.nom_municipio}...`, 'info');
        
        const token = localStorage.getItem('token');
        
        const response = await fetch(`${API_URL}/preoperacion/generar-reportes/`, {
          method: 'POST',
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            municipios: [municipio.cod_municipio],
            generar_individuales: true
          })
        });
        
        if (!response.ok) {
          throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `insumos_${municipio.nom_municipio.replace(/\s+/g, '_')}_${format(new Date(), 'yyyyMMdd_HHmmss')}.zip`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        showNotification(
          `Reporte de insumos de ${municipio.nom_municipio} descargado exitosamente`, 
          'success'
        );
        
      } catch (error) {
        console.error('Error generando reporte de insumos:', error);
        showNotification(
          `Error al generar reporte de insumos de ${municipio.nom_municipio}`, 
          'error'
        );
      } finally {
        descargandoInsumos.value[municipio.cod_municipio] = false;
      }
    };

    const exportarDatos = () => {
      try {
        let csvContent = '';
        let headers = [];
        let data = [];
        let filename = '';
        
        if (selectedMunicipioId.value) {
          headers = ['Código Insumo', 'Categoría', 'Tipo Insumo', 'Clasificaciones', 'Detalles'];
          
          data = municipioInsumos.value.map(insumo => {
            return [
              insumo.cod_insumo,
              getNombreCategoria(insumo.cod_categoria),
              insumo.tipo_insumo,
              getClasificacionesCount(insumo.cod_insumo),
              getDetallesCountForInsumo(insumo.cod_insumo)
            ];
          });
          
          filename = `municipio_${selectedMunicipio.value.cod_municipio}_${selectedMunicipio.value.nom_municipio.replace(/[^a-zA-Z0-9]/g, '_')}.csv`;
        } else {
          headers = ['Código', 'Municipio', 'Departamento', 'Territorial', 'Mecanismo', 'Grupo'];
          
          data = filteredMunicipios.value.map(m => {
            return [
              m.cod_municipio,
              m.nom_municipio,
              getNombreDepartamento(m.cod_depto),
              m.nom_territorial || 'No asignada',
              m.mecanismo_general || '-',
              m.grupo || '-'
            ];
          });
          
          filename = 'municipios_exportados.csv';
        }
        
        csvContent = "data:text/csv;charset=utf-8,\uFEFF";
        csvContent += headers.join(';') + '\n';
        
        data.forEach(row => {
          const formattedRow = row.map(field => 
            `"${String(field).replace(/"/g, '""')}"` 
          );
          csvContent += formattedRow.join(';') + '\n';
        });
        
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', filename);
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showNotification('Datos exportados correctamente en formato CSV', 'success');
      } catch (error) {
        console.error('Error exporting data:', error);
        showNotification('Error al exportar datos', 'error');
      }
    };

    const refreshData = async () => {
      if (selectedMunicipioId.value) {
        await selectMunicipio(selectedMunicipioId.value);
      } else {
        await loadInitialData();
      }
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

    // ✅ WATCH PARA DETECTAR CAMBIOS EN EL MUNICIPIO SELECCIONADO
    watch(() => selectedMunicipioId.value, (nuevoMunicipio) => {
      if (nuevoMunicipio) {
        // Cargar centros poblados cuando cambia el municipio
        cargarCentrosPoblados(nuevoMunicipio);
        
        // Resetear filtros cuando cambia el municipio
        limpiarFiltrosPreoperacion();
      }
    });

    // **INICIALIZACIÓN**

    onMounted(async () => {
      await loadInitialData();
      
      const municipioIdFromRoute = route.query.municipio?.toString();
      if (municipioIdFromRoute) {
        selectMunicipio(parseInt(municipioIdFromRoute));
      }
    });



const extraerCodigoCentroPobladoDesdeRuta = (pathFile: string): string => {
  if (!pathFile) return '';
  
  // ✅ REGEX CORREGIDA: Buscar tanto backslashes como forward slashes
  // Patrón: \\1_urb\\XXX\\ o /1_urb/XXX/ donde XXX son los 3 dígitos
  const patterns = [
    /\\1_urb\\(\d{3})\\/,  // Para Windows: \\1_urb\\000\\
    /\/1_urb\/(\d{3})\//,  // Para Unix: /1_urb/000/
    /\\01_urb\\(\d{3})\\/,  // Por si acaso: \\01_urb\\000\\
    /\/01_urb\/(\d{3})\//   // Por si acaso: /01_urb/000/
  ];
  
  for (const pattern of patterns) {
    const match = pathFile.match(pattern);
    if (match) {
      console.log(`✅ Patrón encontrado: ${pattern} -> ${match[1]} en ruta: ${pathFile.substring(pathFile.length - 50)}`);
      return match[1]; // Retorna los 3 dígitos (ej: "000", "001", "013")
    }
  }
  
  console.log(`❌ No se encontró patrón en: ${pathFile.substring(pathFile.length - 50)}`);
  return '';
};
// ✅ 2. FUNCIÓN ALTERNATIVA más robusta (por si la anterior no funciona)
const extraerCodigoCentroPobladoDesdeRutaAlternativa = (pathFile: string): string => {
  if (!pathFile) return '';
  
  // Normalizar separadores a forward slashes
  const normalizedPath = pathFile.replace(/\\/g, '/');
  
  // Buscar el patrón /1_urb/XXX/ donde XXX son 3 dígitos
  const match = normalizedPath.match(/\/0?1_urb\/(\d{3})\//);
  if (match) {
    console.log(`✅ Patrón alternativo encontrado: ${match[1]} en ruta normalizada`);
    return match[1];
  }
  
  console.log(`❌ Patrón alternativo no encontrado en: ${normalizedPath.substring(normalizedPath.length - 50)}`);
  return '';
};





// ✅ 4. FUNCIÓN CORREGIDA para obtener centro poblado desde la ruta del archivo
const getCentroPobladoFromPath = (pathFile: string): string => {
  if (!pathFile || !selectedMunicipioId.value) return 'N/A';
  
  const tresDigitos = extraerCodigoFinal(pathFile); // ✅ USAR FUNCIÓN CORREGIDA
  if (!tresDigitos) return 'N/A';
  
  const codigoCompleto = `${selectedMunicipioId.value}${tresDigitos}`;
  
  const centro = centrosPoblados.value.find(c => 
    c.cod_centro_poblado === codigoCompleto
  );
  
  return centro ? `${codigoCompleto} - ${centro.nom_centro_poblado}` : `${codigoCompleto} - Centro ${tresDigitos}`;
};

// ✅ REEMPLAZAR la función obtenerCodigoCompletoCentroPoblado
const obtenerCodigoCompletoCentroPoblado = (pathFile: string, municipioId: number): string => {
  const tresDigitos = extraerCodigoFinal(pathFile); // ✅ USAR FUNCIÓN CORREGIDA
  if (!tresDigitos || !municipioId) return '';
  
  return `${municipioId}${tresDigitos}`;
};
// ✅ 5. FUNCIÓN para extraer solo los últimos 3 dígitos del código completo
const extraerCodigoCentroPoblado = (codCentroPoblado: string): string => {
  if (!codCentroPoblado) return '';
  return codCentroPoblado.slice(-3); // Obtiene los últimos 3 caracteres
};

// ✅ 6. COMPUTED CORREGIDO para filtros de archivos de preoperación
const filteredArchivosPre = computed(() => {
  let result = [...municipioArchivos.value];
  
  // Filtro por clasificación
  if (filtroClasificacionPre.value) {
    result = result.filter(a => {
      const nombreClasificacion = getNombreClasificacion(a.cod_insumo);
      return nombreClasificacion === filtroClasificacionPre.value;
    });
  }
  
  // Filtros para CARTOGRAFÍA BÁSICA
  if (mostrarFiltrosCartografiaBasica.value) {
    if (filtroCentroPoblado.value) {
      result = result.filter(a => {
        if (!a.path_file || !selectedMunicipioId.value) return false;
        const tresDigitosArchivo = extraerCodigoFinal(a.path_file);
        return tresDigitosArchivo === filtroCentroPoblado.value;
      });
    }
    
    if (filtroTipoCartografia.value) {
      result = result.filter(a => {
        if (!a.path_file) return false;
        const tipoArchivo = getTipoCartografiaFromPath(a.path_file);
        return tipoArchivo === filtroTipoCartografia.value;
      });
    }
  }
  
  // Filtros para INFORMACIÓN CATASTRAL
  if (mostrarFiltrosInfoCatastral.value && filtroTipoInfoCatastral.value) {
    result = result.filter(a => {
      if (!a.path_file) return false;
      const tipoInfoCatastral = getTipoInfoCatastralFromPath(a.path_file);
      return tipoInfoCatastral === filtroTipoInfoCatastral.value;
    });
  }
  
  // Filtro por nombre de archivo
  if (filtroNombreArchivoPre.value.trim()) {
    const search = filtroNombreArchivoPre.value.toLowerCase();
    result = result.filter(a => 
      a.nombre_insumo?.toLowerCase().includes(search)
    );
  }
  
  console.log(`📊 Archivos filtrados: ${result.length} de ${municipioArchivos.value.length}`);
  return result;
});

// ✅ 7. FUNCIÓN CORREGIDA para obtener nombre del centro poblado seleccionado
const getNombreCentroPobladoSeleccionado = (): string => {
  if (!filtroCentroPoblado.value || !selectedMunicipioId.value) return '';
  
  const codigoCompleto = `${selectedMunicipioId.value}${filtroCentroPoblado.value}`;
  const centro = centrosPoblados.value.find(c => 
    c.cod_centro_poblado === codigoCompleto
  );
  
  return centro ? `${codigoCompleto} - ${centro.nom_centro_poblado}` : `${codigoCompleto} - Centro ${filtroCentroPoblado.value}`;
};

// ✅ 8. FUNCIÓN para manejar cambio en el filtro de clasificación (ACTUALIZADA)
const handleClasificacionPreChange = () => {
  // Resetear filtros de cartografía básica cuando cambia la clasificación
  if (!mostrarFiltrosCartografiaBasica.value) {
    filtroCentroPoblado.value = '';
    filtroTipoCartografia.value = '';
  } else {
    // Si se selecciona cartografía básica, cargar centros poblados
    if (selectedMunicipioId.value) {
      cargarCentrosPoblados(selectedMunicipioId.value);
    }
  }
  
  // Limpiar filtros previos cuando cambia la clasificación
  filtroCentroPoblado.value = '';
  filtroTipoCartografia.value = '';
};


// ✅ 3. FUNCIÓN DE PRUEBA para verificar ambos métodos
const probarExtraccionCodigos = (pathFile: string) => {
  console.log('🧪 PROBANDO EXTRACCIÓN:');
  console.log('Ruta original:', pathFile);
  console.log('Método 1:', extraerCodigoCentroPobladoDesdeRuta(pathFile));
  console.log('Método 2:', extraerCodigoCentroPobladoDesdeRutaAlternativa(pathFile));
  console.log('---');
};



// ✅ 5. FUNCIÓN PARA USAR EL MÉTODO QUE FUNCIONE MEJOR
const extraerCodigoFinal = (pathFile: string): string => {
  // Probar primero el método principal
  let resultado = extraerCodigoCentroPobladoDesdeRuta(pathFile);
  
  // Si no funciona, probar el alternativo
  if (!resultado) {
    resultado = extraerCodigoCentroPobladoDesdeRutaAlternativa(pathFile);
  }
  
  return resultado;
};

// ✅ 6. COMPUTED CORREGIDO usando la función final
const centrosPobladosConArchivos = computed(() => {
  if (!selectedMunicipioId.value || municipioArchivos.value.length === 0) {
    return [];
  }

  // Obtener códigos únicos de centros poblados que tienen archivos
  const codigosConArchivos = new Set<string>();
  
  municipioArchivos.value.forEach(archivo => {
    if (archivo.path_file) {
      const tresDigitos = extraerCodigoFinal(archivo.path_file); // ✅ USAR LA FUNCIÓN CORREGIDA
      if (tresDigitos) {
        const codigoCompleto = `${selectedMunicipioId.value}${tresDigitos}`;
        codigosConArchivos.add(codigoCompleto);
        console.log(`✅ Archivo encontrado para centro poblado: ${codigoCompleto} (${tresDigitos})`);
      }
    }
  });

  console.log('🎯 Códigos únicos encontrados:', Array.from(codigosConArchivos));

  // Filtrar centros poblados que tienen archivos
  return centrosPoblados.value.filter(centro => 
    codigosConArchivos.has(centro.cod_centro_poblado)
  );
});

// ✅ 7. ACTUALIZAR filteredArchivosPre para usar la función corregida
const filteredArchivosPreCorregido = computed(() => {
  let result = [...municipioArchivos.value];
  
  // Filtro por clasificación
  if (filtroClasificacionPre.value) {
    result = result.filter(a => {
      const nombreClasificacion = getNombreClasificacion(a.cod_insumo);
      return nombreClasificacion === filtroClasificacionPre.value;
    });
  }
  
  // ✅ FILTROS PARA CARTOGRAFÍA BÁSICA (USANDO FUNCIÓN CORREGIDA)
  if (mostrarFiltrosCartografiaBasica.value) {
    // Filtro por centro poblado
    if (filtroCentroPoblado.value) {
      result = result.filter(a => {
        if (!a.path_file || !selectedMunicipioId.value) return false;
        
        // ✅ USAR LA FUNCIÓN CORREGIDA
        const tresDigitosArchivo = extraerCodigoFinal(a.path_file);
        
        // Comparar con el filtro seleccionado
        const coincide = tresDigitosArchivo === filtroCentroPoblado.value;
        if (coincide) {
          console.log(`✅ Archivo coincide con filtro: ${a.nombre_insumo} (${tresDigitosArchivo})`);
        }
        
        return coincide;
      });
    }
    
    // Filtro por tipo de cartografía
    if (filtroTipoCartografia.value) {
      result = result.filter(a => {
        if (!a.path_file) return false;
        const tipoArchivo = getTipoCartografiaFromPath(a.path_file);
        return tipoArchivo === filtroTipoCartografia.value;
      });
    }
  }

  // Filtro por nombre de archivo
  if (filtroNombreArchivoPre.value.trim()) {
    const search = filtroNombreArchivoPre.value.toLowerCase();
    result = result.filter(a => 
      a.nombre_insumo?.toLowerCase().includes(search)
    );
  }
  
  return result;
});



// Función para filtrar clasificaciones y evitar duplicados de Cartografia Basica
const getClasificacionesFiltradas = (insumoId: number): any[] => {
  // ⭐ OBTENER CLASIFICACIONES DIRECTAMENTE, NO LLAMAR A getClasificaciones
  const clasificaciones = municipioClasificaciones.value.filter(c => c.cod_insumo === insumoId);
  
  const categoria = getNombreCategoria(
    municipioInsumos.value.find(i => i.cod_insumo === insumoId)?.cod_categoria
  );
  
  // Para Cartografia Basica, filtrar el duplicado genérico
  if (categoria.toLowerCase().includes('cartograf')) {
    return clasificaciones.filter(clasif => 
      clasif.nombre.trim().toLowerCase() !== 'cartografia basica'
    );
  }
  
  // Para Información Catastral, excluir la clasificación padre
  if (categoria.toLowerCase().includes('catastral')) {
    return clasificaciones.filter(clasif => {
      const nombre = clasif.nombre?.toLowerCase() || '';
      return !nombre.includes('informacion catastral') && 
             !nombre.includes('información catastral');
    });
  }
  
  return clasificaciones;
};

// Función para obtener items manuales adicionales por categoría
const getItemsManuales = (insumoId: number): any[] => {
  const categoria = getNombreCategoria(
    municipioInsumos.value.find(i => i.cod_insumo === insumoId)?.cod_categoria
  );
  
  // Items manuales para Información Catastral (ahora con rutas específicas)
  if (categoria.toLowerCase().includes('catastral')) {
    return [
      { 
        nombre: 'R1 & R2',
        ruta_sugerida: '\\03_info_catas\\01_r1_r2',
        descripcion: 'Registros R1 y R2'
      },
      { 
        nombre: 'GDB',
        ruta_sugerida: '\\03_info_catas\\02_gdb',
        descripcion: 'Base de datos geográfica'
      },
      { 
        nombre: 'Tablas Terreno & Construcción',
        ruta_sugerida: '\\03_info_catas\\03_tab_terr_constr',
        descripcion: 'Tablas de terreno y construcción'
      },
      { 
        nombre: 'Estudio ZHF & ZHG',
        ruta_sugerida: '\\03_info_catas\\04_estu_zhf_zhg',
        descripción: 'Estudio de zonas homogéneas físicas y geoeconómicas'
      }
    ];
  }
  
  return [];
};



// Función combinada que obtiene todas las clasificaciones (BD + manuales)
const getTodasLasClasificaciones = (insumoId: number): any[] => {
  const clasificacionesBD = getClasificacionesFiltradas(insumoId);
  const itemsManuales = getItemsManuales(insumoId);
  
  return [...clasificacionesBD, ...itemsManuales];
};


const getActionTitle = (fileName: string, action: 'view' | 'download' | 'details'): string => {
  if (!fileName) return '';
  
  const extension = getFileExtension(fileName);
  const shortName = fileName.length > 30 
    ? `${fileName.substring(0, 30)}...` 
    : fileName;
  
  switch (action) {
    case 'view':
      if (['gdb', 'zip', 'rar', '7z'].includes(extension)) {
        return `Descargar archivo comprimido: ${shortName}`;
      } else if (extension === 'pdf') {
        return `Ver PDF en nueva ventana: ${shortName}`;
      } else if (['jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff'].includes(extension)) {
        return `Ver imagen: ${shortName}`;
      } else if (['xlsx', 'xls', 'docx', 'doc'].includes(extension)) {
        return `Abrir documento: ${shortName}`;
      } else {
        return `Abrir archivo: ${shortName}`;
      }
    
    case 'download':
      return `Descargar: ${shortName}`;
    
    case 'details':
      return `Ver detalles completos de: ${shortName}`;
    
    default:
      return shortName;
  }
};

/**
 * Genera iconos dinámicos para los botones de acción
 */
const getActionIcon = (fileName: string, action: 'view' | 'download' | 'details'): string => {
  if (!fileName || action !== 'view') {
    return action === 'download' ? 'download' : 'visibility';
  }
  
  const extension = getFileExtension(fileName);
  
  if (['gdb', 'zip', 'rar', '7z'].includes(extension)) {
    return 'download'; // Archivos comprimidos se descargan directamente
  } else if (extension === 'pdf') {
    return 'open_in_new'; // PDFs se abren en nueva ventana
  } else if (['jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff'].includes(extension)) {
    return 'visibility'; // Imágenes se visualizan
  } else if (['xlsx', 'xls'].includes(extension)) {
    return 'table_chart'; // Archivos de Excel
  } else if (['docx', 'doc'].includes(extension)) {
    return 'description'; // Documentos de Word
  } else {
    return 'visibility'; // Otros archivos
  }
};

/**
 * Trunca texto largo y agrega puntos suspensivos
 */
const truncateText = (text: string, maxLength: number = 30): string => {
  if (!text) return '';
  return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
};

/**
 * Obtiene el nombre corto del archivo para mostrar
 */
const getShortFileName = (fileName: string, maxLength: number = 35): string => {
  if (!fileName) return '';
  
  if (fileName.length <= maxLength) {
    return fileName;
  }
  
  // Separar nombre y extensión
  const lastDotIndex = fileName.lastIndexOf('.');
  if (lastDotIndex === -1) {
    return `${fileName.substring(0, maxLength - 3)}...`;
  }
  
  const name = fileName.substring(0, lastDotIndex);
  const extension = fileName.substring(lastDotIndex);
  
  // Calcular cuánto espacio queda para el nombre
  const availableLength = maxLength - extension.length - 3; // 3 para "..."
  
  if (availableLength <= 0) {
    return `${fileName.substring(0, maxLength - 3)}...`;
  }
  
  return `${name.substring(0, availableLength)}...${extension}`;
};

/**
 * Valida si un nombre de archivo es considerado "largo"
 */
const isLongFileName = (fileName: string, threshold: number = 40): boolean => {
  return fileName && fileName.length > threshold;
};

/**
 * Obtiene información resumida del archivo para tooltips
 */
const getFileInfo = (archivo: any, type: 'pre' | 'post'): string => {
  const fileName = type === 'pre' ? archivo.nombre_insumo : archivo.nombre_archivo;
  const date = archivo.fecha_disposicion ? formatDate(archivo.fecha_disposicion) : 'Sin fecha';
  const size = archivo.tamaño ? `${(archivo.tamaño / 1024 / 1024).toFixed(2)} MB` : 'Tamaño desconocido';
  
  return `Archivo: ${fileName}\nFecha: ${date}\nTamaño: ${size}`;
};



// ✅ FUNCIÓN PRINCIPAL: Formatear peso_memoria según las reglas específicas
const formatPesoMemoria = (pesoMemoria: string | number | null): string => {
  if (!pesoMemoria) return 'N/A';
  
  // Convertir string a número
  const bytes = typeof pesoMemoria === 'string' ? parseInt(pesoMemoria, 10) : pesoMemoria;
  
  if (isNaN(bytes) || bytes < 0) return 'N/A';
  
  const MB = 1024 * 1024;
  const GB = 1024 * MB;
  
  // ✅ REGLA 1: Si es más de 900 MB → mostrar en GB
  if (bytes > 900 * MB) {
    const gb = bytes / GB;
    return `${gb.toFixed(2)} GB`;
  }
  
  // ✅ REGLA 2: Si es menos de 1 MB → mostrar en bytes
  if (bytes < MB) {
    return `${bytes.toLocaleString()} B`;
  }
  
  // ✅ REGLA 3: Entre 1 MB y 900 MB → mostrar en MB
  const mb = bytes / MB;
  return `${mb.toFixed(2)} MB`;
};

// ✅ FUNCIÓN AUXILIAR: Formateo detallado para tooltips
const formatPesoMemoriaDetallado = (pesoMemoria: string | number | null): string => {
  if (!pesoMemoria) return 'No disponible';
  
  const bytes = typeof pesoMemoria === 'string' ? parseInt(pesoMemoria, 10) : pesoMemoria;
  
  if (isNaN(bytes) || bytes < 0) return 'Datos inválidos';
  
  return `${bytes.toLocaleString()} bytes`;
};

// ✅ FUNCIÓN: Obtener clase CSS según el tamaño
const getPesoMemoriaClass = (pesoMemoria: string | number | null): string => {
  if (!pesoMemoria) return 'sin-peso';
  
  const bytes = typeof pesoMemoria === 'string' ? parseInt(pesoMemoria, 10) : pesoMemoria;
  
  if (isNaN(bytes) || bytes < 0) return 'sin-peso';
  
  const MB = 1024 * 1024;
  const GB = 1024 * MB;
  
  // Clasificar por tamaños para colores
  if (bytes >= 2 * GB) {
    return 'peso-muy-alto'; // 2GB+ - rojo intenso
  } else if (bytes >= 500 * MB) {
    return 'peso-alto'; // 500MB+ - rojo
  } else if (bytes >= 100 * MB) {
    return 'peso-medio-alto'; // 100MB+ - naranja
  } else if (bytes >= 10 * MB) {
    return 'peso-medio'; // 10MB+ - amarillo
  } else if (bytes >= MB) {
    return 'peso-bajo-medio'; // 1MB+ - verde claro
  } else {
    return 'peso-bajo'; // < 1MB - verde
  }
};

// ✅ ACTUALIZAR la función getArchivoExtraInfo para incluir peso_memoria
const getArchivoExtraInfo = (archivo: any, type: 'pre' | 'post') => {
  const info: any = {
    municipio: selectedMunicipio.value?.nom_municipio || 'No disponible',
    departamento: getNombreDepartamento(selectedMunicipio.value?.cod_depto) || 'No disponible',
    fecha_disposicion: archivo.fecha_disposicion ? formatDate(archivo.fecha_disposicion) : 'No disponible',
    // ✅ NUEVO: Peso memoria formateado
    peso_memoria: archivo.peso_memoria ? formatPesoMemoria(archivo.peso_memoria) : 'No registrado',
    peso_memoria_bytes: archivo.peso_memoria ? formatPesoMemoriaDetallado(archivo.peso_memoria) : 'No disponible',
    // ✅ CAMBIO: Observaciones pueden estar vacías
    observacion: archivo.observacion && archivo.observacion.trim() !== '' ? archivo.observacion : 'Sin observaciones'
  };

  if (type === 'pre') {
    info.ruta = archivo.path_file || 'No disponible';
    info.clasificacion = getNombreClasificacion(archivo.cod_insumo) || 'No disponible';
  } else {
    info.ruta = archivo.ruta_completa || 'No disponible';
    info.componente = archivo.disposicion_info?.componente || 'No disponible';
    info.aprobado = archivo.disposicion_info?.aprobado ? 'Sí' : 'No';
    info.dispuesto = archivo.disposicion_info?.dispuesto ? 'Sí' : 'No';
  }

  return info;
};



    // **RETURN DEL SETUP**
    return {
      mecanismosDetalleDisponibles,
      // ✅ STORE DE AUTH PARA PERMISO
      departamentosDisponibles,
      municipiosDisponibles,
      territorialesDisponibles,
      mecanismosGeneralesDisponibles,
      gruposDisponibles,
      authStore,
      
      // Estados principales
      loading,
      error,
      notification,
      
      // Datos maestros
      departamentos,
      categorias,
      tiposInsumo,
      mecanismosGenerales,
      mecanismosDetalle,
      mecanismosOperacion,
      alcancesOperacion,
      grupos,
      territoriales,
      descargandoInsumos,
      
      // Filtros y búsqueda
      searchTerm,
      filters,
      handleSearchInput,
      clearSearch,
      handleDepartamentoChange,
      handleMunicipioChange,
      handleFilter,
      clearAllFilters,
      
      // Paginación
      currentPage,
      pageSize,
      totalPages,
      paginatedMunicipios,
      filteredMunicipios,
      filteredMunicipiosForDropdown,
      displayedPages,
      prevPage,
      nextPage,
      goToPage,
      
      // Municipio seleccionado
      selectedMunicipioId,
      selectedMunicipio,
      municipioInsumos,
      municipioClasificaciones,
      municipioDetalles,
      municipioArchivos,
      municipioProfesionales,
      selectMunicipio,
      clearSelectedMunicipio,
      
      // Pestañas para municipio seleccionado
      activeTab,
      detailTabs,
      
      // Búsqueda dentro de pestañas
      insumoSearch,
      insumoFilter,
      tipoInsumoFilter,
      clasificacionSearch,
      detalleSearch,
      archivoSearch,
      
      // Datos filtrados en pestañas
      filteredInsumos,
      filteredClasificaciones,
      filteredDetalles,
      insumosPorCategoria,
      
      // Variables para archivos y conceptos
      activeArchivosTab,
      municipioArchivosPost,
      municipioConceptos,
      conceptoSearch,
      conceptosLoading,
      conceptosError,
      archivosPostLoading,
      archivosPostError,
      archivosPreLoading,
      archivosPreError,
      filteredConceptos,
      filteredArchivosPost,
      //filteredArchivosPre,
      
      // ✅ FILTROS ESPECÍFICOS PARA ARCHIVOS
      filtroClasificacionPre,
      filtroNombreArchivoPre,
      filtroComponentePost,
      filtroNombreArchivoPost,
      clasificacionesUnicasPre,
      componentesUnicosPost,
      
      // ✅ NUEVAS VARIABLES PARA CARTOGRAFÍA BÁSICA
      filtroCentroPoblado,
      filtroTipoCartografia,
      centrosPoblados,
      cargandoCentrosPoblados,
      mostrarFiltrosCartografiaBasica,
      hayFiltrosActivosPreoperacion,
      handleClasificacionPreChange,
      aplicarFiltrosArchivos,
      getCentroPobladoFromPath,
      getTipoCartografiaFromPath,
      getTipoCartografiaClass,
      extraerCodigoCentroPoblado,
      getNombreCentroPobladoSeleccionado,
      getNombreTipoCartografia,
      limpiarFiltrosPreoperacion,
      cargarCentrosPoblados,
      
      // ✅ MODAL DE DETALLES DE ARCHIVO
      showArchivoDetailsModal,
      selectedArchivoDetails,
      archivoDetailsType,
      showArchivoDetails,
      closeArchivoDetailsModal,
      getArchivoExtraInfo,
      
      // Métodos de utilidad
      formatDate,
      getNombreDepartamento,
      getInsumoCount,
      getNombreCategoria,
      getNombreClasificacion,
      getNombreEntidad,
      getNombreUsuario,
      getClasificaciones,
      getClasificacionesCount,
      getDetallesCount,
      getDetallesCountForInsumo,
      getFileIcon,
      getFileExtension,
      
      // Métodos de archivos
      viewArchivo,
      viewArchivoPost,
      downloadArchivo,
      downloadArchivoPost,
      cargarArchivosPre,
      loadArchivosPostForMunicipio,
      
      // Métodos de conceptos
      cargarConceptos,
      getEvaluacionClass,
      verDocumentoPDF,
      getDetalleNombre,
      
      // Métodos de profesionales
      loadProfesionalesForMunicipio,
      
      // Métodos adicionales
      getCategoriaClass,
      isCartografiaBasica,
      getInsumoCategoria,
      getNombreCategoriaByInsumo,
      getCartografiaSubtipo,
      getTipoInsumoNombre,
      
      // Métodos de navegación
      irAInsumosPorCategoria,
      viewInsumoDetails,
      viewClasificacionDetalles,
      viewDetalleDetails,
      
      // Métodos de edición (simplificados)
      editMunicipio,
      showCreateInsumoForMunicipio,
     
      // Métodos adicionales
      descargarInsumos,
      exportarDatos,
      refreshData,
      showNotification,
      closeNotification,
      
      // Control de permisos
      tieneAccesoAMunicipio,
      obtenerNombreArchivo,
      centrosPobladosConArchivos,
      extraerCodigoCentroPobladoDesdeRuta,
      obtenerCodigoCompletoCentroPoblado,
     
      extraerCodigoFinal,
      extraerCodigoCentroPobladoDesdeRutaAlternativa,
      probarExtraccionCodigos,
      filteredArchivosPreCorregido,




            // Nuevos modales
      modalDetalleInsumo,
      modalDetalleDetalle,
      
      // Nuevas funciones
      verDetalleCompleto,
      verDetallesDeClasificacion,
      getDetallesForInsumoModal,
      getConceptosDelDetalle,
      getConceptosCountForInsumo,
      getArchivosCountForInsumo,
      getEstadoClass,
      verTodosLosDetalles,
      irAVistaCompleta,
      getClasificacionesParaModal,



      archivoCoincideConTipo,

      // ✅ REEMPLAZAR O AGREGAR:
      filteredArchivosPre: filteredArchivosPreConInfoCatastral,


        getActionTitle,
        getActionIcon,
        truncateText,
        getShortFileName,
        isLongFileName,
        getFileInfo,

        getClasificacionesFiltradas,
        getItemsManuales,
        getTodasLasClasificaciones,

        filtroTipoInfoCatastral,
        mostrarFiltrosInfoCatastral,
        getTipoInfoCatastralFromPath,
        getTipoInfoCatastralClass,
        tiposInfoCatastralUnicos,
        formatPesoMemoria,
        formatPesoMemoriaDetallado,
        getPesoMemoriaClass,
        formatZonaConCentroPoblado,
        enriquecerDetallesConCentrosPoblados,
        showDetalleModal,

        detalleSeleccionado,
        detalleModalVisible,
        formatArea,
        cerrarDetalleModal,
          filtroZonaDetalle,
      filtroCentroPobladoDetalle,
      filtroClasificacionDetalle,
      filtroFormatoDetalle,
      zonasUnicasDetalles,
      centrosPobladosUnicosDetalles,
      clasificacionesUnicasDetalles,
      formatosUnicosDetalles,
      hayFiltrosActivosDetalles,
      handleZonaDetalleChange,
      limpiarFiltrosDetalles,
      filtrosNivelesPost,
      maxNivelProfundidad,
      opcionesNivel1Post,
      opcionesNivel2Post,
      opcionesNivel3Post,
      opcionesNivel4Post,
      opcionesNivel5Post,
      handleNivelChange,
      limpiarFiltrosPostoperacion,
      hayFiltrosActivosPost,
      extraerNivelesDeRuta,
      // Utilidades de rutas
      linuxToWindowsPath,
    }
  }
});
</script>

<style scoped>
.ruta-filtrada {
  font-family: 'Consolas', 'Monaco', monospace;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  margin: 0 0.5rem;
}

.directorio-path {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.85rem;
  color: #475569;
  background: #f8fafc;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  display: inline-block;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Estilos para los badges de zona */
.zona-info {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.zona-urbano {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(29, 78, 216, 0.1) 100%);
  color: #1d4ed8;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.zona-rural {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(21, 128, 61, 0.1) 100%);
  color: #166534;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.zona-centro-poblado {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(126, 34, 206, 0.1) 100%);
  color: #7e22ce;
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.formato-badge {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%);
  color: #d97706;
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.no-results-message {
  padding: 2rem;
  text-align: center;
  color: #6b7280;
  font-style: italic;
}

/* Agregar en la sección de estilos */
.resultados-count {
  margin-left: auto;
  font-weight: 600;
  color: #6366f1;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.85rem;
}

.detalles-tab .tab-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  border-radius: 16px;
  border: 1px solid rgba(99, 102, 241, 0.1);
}

.detalles-tab .filter-item {
  min-width: 180px;
  flex: 1;
  max-width: 250px;
}

.detalles-tab .search-box {
  min-width: 280px;
  flex: 2;
}

/* ✅✅✅ FORZAR CENTRADO DEL MODAL - MÁXIMA PRIORIDAD ✅✅✅ */
body.modal-open {
  overflow: hidden !important;
}

div[class*="modal-overlay"] {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: 100% !important;
  background-color: rgba(0, 0, 0, 0.6) !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  z-index: 999999 !important;
  margin: 0 !important;
  padding: 0 !important;
  right: auto !important;
  bottom: auto !important;
  transform: none !important;
  overflow: hidden !important;
}

div[class*="modal-overlay"] > div {
  position: relative !important;
  background: white !important;
  border-radius: 12px !important;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3) !important;
  width: 90% !important;
  max-width: 900px !important;
  max-height: 90vh !important;
  margin: 0 !important;
  left: auto !important;
  right: auto !important;
  top: auto !important;
  bottom: auto !important;
  transform: none !important;
  display: flex !important;
  flex-direction: column !important;
  overflow: hidden !important;
}

/* ESPECÍFICO PARA TU MODAL DE DETALLE */
.detalles-tab .modal-overlay {
  position: fixed !important;
  inset: 0 !important;
  display: grid !important;
  place-items: center !important;
  margin: 0 !important;
  padding: 0 !important;
}

.detalles-tab .modal-content,
.modal-overlay .modal-content {
  position: static !important;
  transform: translate(0, 0) !important;
  margin: 0 !important;
  left: unset !important;
  right: unset !important;
  top: unset !important;
  bottom: unset !important;
}

/* ✅ MODAL CENTRADO EN VIEWPORT (PANTALLA COMPLETA) */
.modal-overlay {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  z-index: 99999 !important;
  animation: fadeIn 0.3s ease-out;
  
  /* ✅ CRÍTICO: Reset de márgenes y padding */
  margin: 0 !important;
  padding: 0 !important;
  transform: none !important;
  
  /* ✅ IMPORTANTE: Evitar scroll horizontal */
  overflow-x: hidden;
  overflow-y: auto;
  
  /* ✅ CRUCIAL: Asegurar que use todo el viewport */
  box-sizing: border-box;
  inset: 0; /* Alternativa moderna a top/left/right/bottom */
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 900px;
  width: 90%;
  max-height: 90vh;
  
  /* ✅ SOLUCIÓN: Centrado perfecto */
  position: relative !important;
  margin: 0 auto !important; /* Solo margin horizontal auto */
  left: 0 !important;
  right: 0 !important;
  transform: none !important; /* Evitar transforms que puedan descentrar */
  
  /* ✅ ASEGURAR CENTRADO */
  display: flex;
  flex-direction: column;
  overflow: hidden;
  
  animation: modalSlideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}


/* ✅ BODY CON SCROLL INTERNO */
.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex-grow: 1;
  max-height: calc(90vh - 140px);
}

/* ✅ HEADER Y FOOTER FIJOS */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  flex-shrink: 0;
  border-radius: 12px 12px 0 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e9ecef;
  background-color: #f8f9fa;
  flex-shrink: 0;
  border-radius: 0 0 12px 12px;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

/* ✅ ANIMACIONES MEJORADAS */
@keyframes fadeIn {
  from { 
    opacity: 0; 
    backdrop-filter: blur(0px);
  }
  to { 
    opacity: 1; 
    backdrop-filter: blur(4px);
  }
}

@keyframes modalSlideIn {
  from { 
    opacity: 0;
    transform: translateY(-30px) scale(0.95);
  }
  to { 
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}



/* ✅ ESTILOS PARA EL CONTENIDO DEL MODAL */
.detalle-info-grid {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

.info-section {
  background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 1.25rem;
  border-radius: 8px;
  border-left: 4px solid #007bff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.info-section h4 {
  margin: 0 0 1rem 0;
  color: #007bff;
  font-size: 1.05rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(0,0,0,0.1);
}

.info-item:last-child {
  border-bottom: none;
}

.info-item strong {
  color: #495057;
  font-size: 0.9rem;
  font-weight: 600;
  min-width: 140px;
  flex-shrink: 0;
}

.info-item span {
  color: #212529;
  font-size: 0.95rem;
  text-align: right;
  flex-grow: 1;
  word-break: break-word;
}

.peso-memoria-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.peso-memoria-badge {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  border-radius: 16px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  border: 1px solid;
  transition: all 0.3s ease;
  cursor: help;
  white-space: nowrap;
}

.peso-memoria-badge.large {
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
}

/* ✅ NUEVOS COLORES según tamaños reales */

/* Archivos muy pequeños (< 1MB) - Verde oscuro */
.peso-memoria-badge.peso-bajo {
  background: linear-gradient(135deg, rgba(5, 150, 105, 0.1) 0%, rgba(6, 78, 59, 0.1) 100%);
  color: #064e3b;
  border-color: rgba(5, 150, 105, 0.3);
}

/* Archivos pequeños (1MB - 10MB) - Verde claro */
.peso-memoria-badge.peso-bajo-medio {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(21, 128, 61, 0.1) 100%);
  color: #166534;
  border-color: rgba(34, 197, 94, 0.3);
}

/* Archivos medianos (10MB - 100MB) - Amarillo */
.peso-memoria-badge.peso-medio {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%);
  color: #d97706;
  border-color: rgba(245, 158, 11, 0.3);
}

/* Archivos medio-grandes (100MB - 500MB) - Naranja */
.peso-memoria-badge.peso-medio-alto {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, rgba(194, 65, 12, 0.1) 100%);
  color: #c2410c;
  border-color: rgba(249, 115, 22, 0.3);
}

/* Archivos grandes (500MB - 2GB) - Rojo */
.peso-memoria-badge.peso-alto {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%);
  color: #dc2626;
  border-color: rgba(239, 68, 68, 0.3);
}

/* Archivos muy grandes (2GB+) - Rojo intenso */
.peso-memoria-badge.peso-muy-alto {
  background: linear-gradient(135deg, rgba(185, 28, 28, 0.15) 0%, rgba(127, 29, 29, 0.15) 100%);
  color: #7f1d1d;
  border-color: rgba(185, 28, 28, 0.4);
  font-weight: 800;
  box-shadow: 0 2px 8px rgba(185, 28, 28, 0.2);
}

.sin-peso-memoria {
  color: #9ca3af;
  font-style: italic;
  font-size: 0.85rem;
  text-align: center;
}

/* Sección de observaciones detalladas en el modal */
.observaciones-detalladas {
  padding: 1.25rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  border-radius: 12px;
  border: 1px solid rgba(99, 102, 241, 0.1);
  color: #374151;
  line-height: 1.6;
  white-space: pre-wrap;
  font-size: 0.95rem;
  max-height: 200px;
  overflow-y: auto;
}

/* Hover effects */
.peso-memoria-badge:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}


tipo-info-catastral-badge {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  border: 1px solid;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tipo-info-catastral-badge.tipo-r1r2 {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(21, 128, 61, 0.1) 100%);
  color: #166534;
  border-color: rgba(34, 197, 94, 0.3);
}

.tipo-info-catastral-badge.tipo-gdb {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(29, 78, 216, 0.1) 100%);
  color: #1d4ed8;
  border-color: rgba(59, 130, 246, 0.3);
}

.tipo-info-catastral-badge.tipo-tablas {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(126, 34, 206, 0.1) 100%);
  color: #7e22ce;
  border-color: rgba(168, 85, 247, 0.3);
}

.tipo-info-catastral-badge.tipo-estudio {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%);
  color: #d97706;
  border-color: rgba(245, 158, 11, 0.3);
}

.tipo-info-catastral-badge.tipo-default {
  background: linear-gradient(135deg, rgba(107, 114, 128, 0.1) 0%, rgba(75, 85, 99, 0.1) 100%);
  color: #4b5563;
  border-color: rgba(107, 114, 128, 0.3);
}

.category-links {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem;
}

.category-link-item {
  transition: all 0.3s ease;
}

.category-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  border-radius: 12px;
  text-decoration: none;
  color: #374151;
  font-weight: 600;
  border: 1px solid rgba(99, 102, 241, 0.1);
  transition: all 0.3s ease;
}

.category-link:hover {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  color: #6366f1;
  text-decoration: none;
  transform: translateX(4px);
  border-color: rgba(99, 102, 241, 0.2);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

.category-link i {
  color: #6366f1;
  font-size: 1.2rem;
}



/* Modales específicos */
.modal-detalle-insumo {
  max-width: 1200px;
  max-height: 85vh;
}

.modal-detalle-detalle {
  max-width: 900px;
  max-height: 85vh;
}

/* Animaciones */
@keyframes modalBackdropFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}



/* Header del modal */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem 2.5rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 24px 24px 0 0;
  color: white;
  position: relative;
  overflow: hidden;
}

.modal-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1.5" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="80" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
  pointer-events: none;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  color: white;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  position: relative;
  z-index: 1;
}

.modal-header h3 i {
  font-size: 1.75rem;
  opacity: 0.9;
}

/* Botón cerrar */
.btn-close {
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  cursor: pointer;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 1;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.4);
  transform: scale(1.1);
}

.btn-close i {
  font-size: 1.25rem;
}

/* Body del modal */
.modal-body {
  padding: 2.5rem;
  overflow-y: auto;
  max-height: calc(90vh - 200px);
}

/* Footer del modal */
.modal-footer {
  padding: 1.5rem 2.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 0 0 24px 24px;
}

/* ==========================================================================
   SECCIONES DE INFORMACIÓN
   ========================================================================== */

.seccion-info {
  margin-bottom: 2.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  overflow: hidden;
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
}

.seccion-info h4 {
  margin: 0;
  padding: 1.25rem 1.5rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  font-size: 1.1rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.seccion-info h4 i {
  font-size: 1.3rem;
  opacity: 0.9;
}

/* Grid de información */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 0;
  padding: 0;
}

.info-item {
  display: flex;
  flex-direction: column;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
  border-right: 1px solid #f1f5f9;
  transition: background-color 0.2s ease;
}

.info-item:hover {
  background-color: rgba(99, 102, 241, 0.02);
}

.info-item:nth-child(even) {
  border-right: none;
}

.info-item:last-child,
.info-item:nth-last-child(2):nth-child(odd) {
  border-bottom: none;
}

.info-item label {
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.info-item span {
  font-size: 1rem;
  color: #1e293b;
  font-weight: 500;
  word-break: break-word;
}

/* ==========================================================================
   CLASIFICACIONES EN MODAL
   ========================================================================== */

.clasificaciones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
}

.clasificacion-card-modal {
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
}

.clasificacion-card-modal:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 25px rgba(0, 0, 0, 0.1);
  border-color: rgba(99, 102, 241, 0.2);
}

.clasificacion-header-modal {
  padding: 1.25rem 1.5rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.clasificacion-header-modal h5 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #374151;
}

.clasificacion-code {
  padding: 0.25rem 0.75rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.clasificacion-details {
  padding: 1.25rem 1.5rem;
}

.clasificacion-details .detail-row {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 0.75rem;
}

.clasificacion-details .detail-row strong {
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 700;
}

.clasificacion-details .detail-row span {
  font-size: 0.95rem;
  color: #374151;
}

.ruta-text {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.85rem;
  background: #f8fafc;
  padding: 0.5rem;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  word-break: break-all;
}

.clasificacion-actions {
  padding: 1rem 1.5rem;
  border-top: 1px solid #f1f5f9;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

/* ==========================================================================
   TABLA DE DETALLES EN MODAL
   ========================================================================== */

.detalles-tabla-modal {
  padding: 1.5rem;
}

.tabla-detalles {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

.tabla-detalles th,
.tabla-detalles td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #f1f5f9;
}

.tabla-detalles th {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  font-weight: 700;
  color: #374151;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.tabla-detalles tbody tr:hover {
  background-color: rgba(99, 102, 241, 0.05);
}

.mas-detalles {
  margin-top: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  border-radius: 12px;
  text-align: center;
}

.mas-detalles p {
  margin: 0 0 1rem 0;
  color: #64748b;
  font-size: 0.95rem;
}

/* ==========================================================================
   ESTADÍSTICAS EN MODAL
   ========================================================================== */

.stats-grid-modal {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
}

.stat-card-modal {
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
}

.stat-card-modal:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 25px rgba(0, 0, 0, 0.1);
  border-color: rgba(99, 102, 241, 0.2);
}

.stat-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
}

.stat-icon i {
  font-size: 1.75rem;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 2rem;
  font-weight: 800;
  color: #6366f1;
  margin-bottom: 0.25rem;
  text-shadow: 0 2px 4px rgba(99, 102, 241, 0.1);
}

.stat-label {
  font-size: 0.95rem;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

/* ==========================================================================
   BADGES Y ESTADOS
   ========================================================================== */

.stat-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
  box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
}

.estado-badge {
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.estado-oficializado {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.estado-produccion {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
  border: 1px solid #fde68a;
}

.estado-pendiente {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #991b1b;
  border: 1px solid #fecaca;
}

.estado-rechazado {
  background: linear-gradient(135deg, #fde2e7 0%, #fbb6ce 100%);
  color: #be185d;
  border: 1px solid #fbb6ce;
}

.estado-default {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  color: #374151;
  border: 1px solid #d1d5db;
}

/* ==========================================================================
   CONCEPTOS (IGUAL QUE EN EstadoProducto.vue)
   ========================================================================== */

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
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.evaluacion-aprobado {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.evaluacion-rechazado {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #991b1b;
  border: 1px solid #fecaca;
}

.evaluacion-pendiente {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
  border: 1px solid #fde68a;
}

.evaluacion-revision {
  background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 100%);
  color: #1e40af;
  border: 1px solid #93c5fd;
}

.evaluacion-default {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
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





/* ✅ MEJORA ESPECÍFICA PARA NOMBRES MUY LARGOS */
.archivo-nombre-largo {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
  vertical-align: middle;
}

/* ✅ ESTILO ALTERNATIVO PARA MOSTRAR MÁS INFORMACIÓN EN HOVER */
.data-table tbody tr:hover .file-info span {
  color: #6366f1;
  font-weight: 600;
}

/* Contenedor de tabla responsivo mejorado */
.table-responsive {
  width: 100%;
  overflow-x: auto;
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(10px);
}

/* ✅ TABLA CON LAYOUT FIJO para evitar problemas de ancho */
.data-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed; /* ✅ CLAVE: Layout fijo para controlar anchos */
  min-width: 900px; /* ✅ Ancho mínimo para evitar compresión excesiva */
}

/* ✅ DEFINIR ANCHOS ESPECÍFICOS PARA CADA COLUMNA */

/* Para tablas de archivos de PREOPERACIÓN */
.archivos-content .data-table th:nth-child(1), /* Nombre */
.archivos-content .data-table td:nth-child(1) {
  width: 25%; /* ✅ 25% para nombre - ancho controlado */
  max-width: 250px; /* ✅ Máximo 250px */
  min-width: 180px; /* ✅ Mínimo 180px */
}

.archivos-content .data-table th:nth-child(2), /* Clasificación */
.archivos-content .data-table td:nth-child(2) {
  width: 15%;
  min-width: 120px;
}

.archivos-content .data-table th:nth-child(3), /* Centro Poblado (si existe) */
.archivos-content .data-table td:nth-child(3) {
  width: 15%;
  min-width: 130px;
}

.archivos-content .data-table th:nth-child(4), /* Tipo (si existe) */
.archivos-content .data-table td:nth-child(4) {
  width: 12%;
  min-width: 100px;
}

.archivos-content .data-table th:last-child, /* Acciones - SIEMPRE AL FINAL */
.archivos-content .data-table td:last-child {
  width: 130px; /* ✅ ANCHO FIJO para acciones */
  min-width: 130px; /* ✅ Garantizar que siempre se vean los 3 botones */
  max-width: 130px;
}

/* ✅ INFORMACIÓN DEL ARCHIVO CON TRUNCAMIENTO */
.file-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  max-width: 100%; /* ✅ No exceder el contenedor */
  overflow: hidden; /* ✅ Ocultar overflow */
}

.file-icon {
  font-size: 1.5rem;
  color: #6366f1;
  opacity: 0.8;
  flex-shrink: 0; /* ✅ El icono no se encoge */
  width: 24px; /* ✅ Ancho fijo para el icono */
}

/* ✅ NOMBRE DEL ARCHIVO CON TRUNCAMIENTO ELEGANTE */
.file-info span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  font-size: 0.9rem;
  font-weight: 500;
  color: #374151;
  cursor: help; /* ✅ Indicar que se puede ver más info */
}

/* ✅ TOOLTIP PARA MOSTRAR NOMBRE COMPLETO AL HACER HOVER */
.file-info span:hover {
  position: relative;
}

.file-info span:hover::after {
  content: attr(title);
  position: absolute;
  bottom: 100%;
  left: 0;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  white-space: nowrap;
  z-index: 1000;
  max-width: 400px;
  word-break: break-all;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: tooltipFadeIn 0.2s ease;
}

@keyframes tooltipFadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ✅ BOTONES DE ACCIÓN OPTIMIZADOS */
.row-actions {
  display: flex;
  gap: 0.5rem; /* ✅ Reducir gap para más espacio */
  justify-content: center;
  flex-wrap: nowrap; /* ✅ Evitar que se envuelvan */
  min-width: 120px; /* ✅ Ancho mínimo garantizado */
}

/* ✅ BOTONES MÁS COMPACTOS PERO VISIBLES */
.btn-icon.small {
  width: 32px; /* ✅ Reducir ligeramente el tamaño */
  height: 32px;
  min-width: 32px; /* ✅ Evitar compresión */
  flex-shrink: 0; /* ✅ Los botones no se encogen */
}

.btn-icon.small i {
  font-size: 1rem; /* ✅ Ajustar tamaño del icono */
}

/* ✅ CELDAS DE TABLA CON MEJOR CONTROL */
.data-table td {
  padding: 0.75rem 1rem; /* ✅ Reducir padding para más espacio */
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.9rem; /* ✅ Fuente ligeramente más pequeña */
  vertical-align: middle;
  overflow: hidden; /* ✅ Evitar overflow en todas las celdas */
}

/* ✅ HEADERS DE TABLA */
.data-table th {
  padding: 1rem;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  font-weight: 700;
  color: #374151;
  white-space: nowrap;
  font-size: 0.85rem; /* ✅ Headers más compactos */
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 2px solid #cbd5e1;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ✅ BADGES Y ELEMENTOS ESPECIALES MÁS COMPACTOS */
.centro-poblado-info {
  display: inline-block;
  padding: 0.25rem 0.6rem; /* ✅ Más compacto */
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(21, 128, 61, 0.1) 100%);
  color: #166534;
  border-radius: 16px;
  font-size: 0.75rem; /* ✅ Fuente más pequeña */
  font-weight: 600;
  border: 1px solid rgba(34, 197, 94, 0.2);
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tipo-cartografia-badge {
  display: inline-block;
  padding: 0.25rem 0.6rem; /* ✅ Más compacto */
  border-radius: 16px;
  font-size: 0.7rem; /* ✅ Fuente más pequeña */
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  border: 1px solid;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}



/* Mensaje cuando no hay datos */
.no-data-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%);
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: 8px;
  color: #d97706;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.no-data-message i {
  font-size: 1.1rem;
  opacity: 0.8;
}

/* Botón de debug temporal */
.debug-btn {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  margin-top: 0.5rem;
  transition: all 0.2s ease;
}

.debug-btn:hover {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  transform: translateY(-1px);
}

/* Mejorar el select de centros poblados */
.filter-item select option {
  padding: 0.5rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Estilo para opciones largas en el select */
.filter-item select {
  max-width: 300px;
  font-size: 0.9rem;
}

/* Indicador de carga pequeño para centros poblados */
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

/* Información de filtros activos */
.filtros-activos-info {
  margin-top: 1rem;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%);
  border-radius: 12px;
  border: 1px solid rgba(99, 102, 241, 0.15);
}

.filtros-activos-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.filtros-activos-content i {
  color: #6366f1;
  font-size: 1.2rem;
}

.filtros-activos-content > span {
  font-weight: 600;
  color: #374151;
  font-size: 0.95rem;
}

.filtros-tags {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.filtro-tag {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
}

.tag-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  cursor: pointer;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  transition: all 0.2s ease;
}

.tag-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.limpiar-filtros-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-left: auto;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
}

.limpiar-filtros-btn:hover {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(239, 68, 68, 0.3);
}

.limpiar-filtros-btn i {
  font-size: 1rem;
}





.tipo-cartografia-badge.tipo-vectorial {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(29, 78, 216, 0.1) 100%);
  color: #1d4ed8;
  border-color: rgba(59, 130, 246, 0.3);
}

.tipo-cartografia-badge.tipo-ortofoto {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(126, 34, 206, 0.1) 100%);
  color: #7e22ce;
  border-color: rgba(168, 85, 247, 0.3);
}

.tipo-cartografia-badge.tipo-modelo {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%);
  color: #d97706;
  border-color: rgba(245, 158, 11, 0.3);
}

.tipo-cartografia-badge.tipo-default {
  background: linear-gradient(135deg, rgba(107, 114, 128, 0.1) 0%, rgba(75, 85, 99, 0.1) 100%);
  color: #4b5563;
  border-color: rgba(107, 114, 128, 0.3);
}

/* Contenedor de estadísticas - asegurar que no se recorten */
.stats-container {
  padding: 1.5rem;
  display: flex;
  justify-content: space-around;
  gap: 1rem; /* Reducido de 1.5rem */
  flex-wrap: wrap; /* Permitir que se envuelvan */
  min-width: 0; /* Asegurar que pueda encoger */
}

/* Tarjetas individuales de estadísticas */
.stat-item {
  text-align: center;
  padding: 1.25rem; /* Reducido de 1.5rem */
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  border-radius: 16px;
  transition: all 0.3s ease;
  flex: 1 1 120px; /* flex-grow, flex-shrink, flex-basis */
  min-width: 120px; /* Ancho mínimo para evitar recorte */
  max-width: 200px; /* Ancho máximo */
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem; /* Reducido de 0.75rem */
  border: 2px solid rgba(99, 102, 241, 0.1);
}


/* Estilos generales */
.insumos-list-page {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
  padding: 1.5rem;
}

/* Cabecera de página */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 2rem 2.5rem;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1.5" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="80" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
  pointer-events: none;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
}

.header-content h1 {
  margin: 0;
  font-size: 2.25rem;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  letter-spacing: -0.02em;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

/* Paneles y filtros */
.filters-panel {
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 20px;
  padding: 2rem 2.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(10px);
}

.search-filters-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.global-search {
  position: relative;
}

.global-search i {
  position: absolute;
  left: 1.25rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6366f1;
  font-size: 1.25rem;
}

.global-search input {
  width: 100%;
  padding: 1rem 1.25rem 1rem 3.5rem;
  border: 2px solid #e5e7eb;
  border-radius: 16px;
  font-size: 1.1rem;
  background: white;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.global-search input:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1), 0 8px 25px rgba(0, 0, 0, 0.1);
  outline: none;
  transform: translateY(-2px);
}

.clear-btn {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: #f3f4f6;
  border: none;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  background: #e5e7eb;
  transform: translateY(-50%) scale(1.1);
}

.filters-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  align-items: flex-end;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 220px;
  flex: 1;
}

.filter-item label {
  font-size: 0.8rem;
  color: #374151;
  font-weight: 600;
  letter-spacing: 0.025em;
}

.filter-item select,
.filter-item input {
  padding: 0.875rem 1.25rem;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  background: white;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.filter-item select:focus,
.filter-item input:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  outline: none;
}

.filter-item .search-box {
  position: relative;
}

.filter-item .search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6366f1;
  font-size: 1.1rem;
}

.filter-item .search-box input {
  padding-left: 3rem;
}

.filter-item .search-box .clear-btn {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: #f3f4f6;
  border: none;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.filter-actions {
  display: flex;
  gap: 1rem;
  margin-left: auto;
}

.clear-filters-btn,
.refresh-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.5rem;
  border-radius: 12px;
  border: none;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.clear-filters-btn {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  color: #475569;
  border: 2px solid #e2e8f0;
}

.clear-filters-btn:hover {
  background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}

.refresh-btn {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
}

.refresh-btn:hover {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Botones */
.btn-primary,
.btn-secondary,
.btn-outline,
.btn-danger {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.75rem;
  border-radius: 12px;
  border: none;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 0.025em;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
}

.btn-primary {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
}

.btn-secondary {
  background: linear-gradient(135deg, #64748b 0%, #475569 100%);
  color: white;
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #475569 0%, #334155 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(100, 116, 139, 0.3);
}

.btn-outline {
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  border: 2px solid #e2e8f0;
  color: #475569;
}

.btn-outline:hover {
  background: linear-gradient(145deg, #f1f5f9 0%, #e2e8f0 100%);
  border-color: #cbd5e1;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.btn-danger:hover {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(239, 68, 68, 0.3);
}

.btn-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  color: #6366f1;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  position: relative;
}

.btn-text:hover {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  transform: translateY(-1px);
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.btn-icon:hover {
  background: linear-gradient(145deg, #e2e8f0 0%, #cbd5e1 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
}

.btn-icon.primary {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
  color: #6366f1;
  border: 2px solid rgba(99, 102, 241, 0.2);
}

.btn-icon.primary:hover {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(139, 92, 246, 0.25) 100%);
  border-color: rgba(99, 102, 241, 0.3);
}

.btn-icon.warning {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.15) 100%);
  color: #f59e0b;
  border: 2px solid rgba(245, 158, 11, 0.2);
}

.btn-icon.warning:hover {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.25) 0%, rgba(217, 119, 6, 0.25) 100%);
  border-color: rgba(245, 158, 11, 0.3);
}

.btn-icon.success {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(21, 128, 61, 0.15) 100%);
  color: #22c55e;
  border: 2px solid rgba(34, 197, 94, 0.2);
}

.btn-icon.success:hover {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.25) 0%, rgba(21, 128, 61, 0.25) 100%);
  border-color: rgba(34, 197, 94, 0.3);
}

.btn-icon.danger {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.15) 100%);
  color: #ef4444;
  border: 2px solid rgba(239, 68, 68, 0.2);
}

.btn-icon.danger:hover {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.25) 0%, rgba(220, 38, 38, 0.25) 100%);
  border-color: rgba(239, 68, 68, 0.3);
}

.btn-icon.info {
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.15) 0%, rgba(14, 165, 233, 0.15) 100%);
  color: #06b6d4;
  border: 2px solid rgba(6, 182, 212, 0.2);
}

.btn-icon.info:hover {
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.25) 0%, rgba(14, 165, 233, 0.25) 100%);
  border-color: rgba(6, 182, 212, 0.3);
}





.btn-action.btn-success {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: white;
  border: none;
  padding: 0.75rem;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(34, 197, 94, 0.1);
}

.btn-action.btn-success:hover:not(:disabled) {
  background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(34, 197, 94, 0.3);
}

.btn-action:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Estados de carga y errores */
.loading-indicator,
.error-message,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(10px);
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #f1f5f9;
  border-top: 4px solid #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 8px rgba(99, 102, 241, 0.2);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message i,
.empty-state i {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.7;
}

.error-message i {
  color: #ef4444;
}

.empty-state i {
  color: #6366f1;
}

.error-message p,
.empty-state p {
  margin-bottom: 2rem;
  font-size: 1.2rem;
  color: #64748b;
  font-weight: 500;
}

.loading-state, 
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-state .spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(99, 102, 241, 0.2);
  border-top: 4px solid #6366f1;
  border-radius: 50%;
  margin-bottom: 1.5rem;
  animation: spin 1s linear infinite;
}

.error-state i {
  font-size: 4rem;
  color: #ef4444;
  margin-bottom: 1.5rem;
}

/* Tablas */
.municipios-table-container,
.detalles-table-container {
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(10px);
}








.data-table tbody tr {
  transition: all 0.3s ease;
}

.data-table tbody tr:hover {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.data-table .text-center {
  text-align: center;
}

.data-table .badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  font-size: 0.8rem;
  font-weight: 700;
  line-height: 1;
  color: #fff;
  text-align: center;
  white-space: nowrap;
  vertical-align: baseline;
  border-radius: 20px;
  letter-spacing: 0.025em;
  text-transform: uppercase;
}

.badge-primary {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
}

.badge-secondary {
  background: linear-gradient(135deg, #64748b 0%, #475569 100%);
}

.badge-success {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

.badge-danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.badge-warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.badge-info {
  background: linear-gradient(135deg, #06b6d4 0%, #0e7490 100%);
  color: white;
}





/* Paginación */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  border-top: 1px solid #dee2e6;
  gap: 0.5rem;
}

.pagination-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid #dee2e6;
  background-color: white;
  color: #0d6efd;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.pagination-button:hover:not(:disabled) {
  background-color: #e9ecef;
}

.pagination-button:disabled {
  color: #6c757d;
  cursor: not-allowed;
  opacity: 0.5;
}

.page-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid #dee2e6;
  background-color: white;
  color: #495057;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.page-number:hover {
  background-color: #e9ecef;
}

.page-number.active {
  background-color: #0d6efd;
  color: white;
  border-color: #0d6efd;
  font-weight: 600;
}

/* Vista detallada de municipio */
.municipio-detail {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(10px);
}

.detail-header {
  display: flex;
  align-items: center;
  padding: 2rem 2.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.detail-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1.5" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="80" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
  pointer-events: none;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  cursor: pointer;
  padding: 0.875rem 1.5rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 1;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 255, 255, 0.2);
}

.detail-header h2 {
  margin: 0 0 0 1.5rem;
  font-size: 2rem;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
}

.detail-actions {
  margin-left: auto;
  display: flex;
  gap: 1rem;
  position: relative;
  z-index: 1;
}

.detail-tabs {
  display: flex;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-bottom: 1px solid #cbd5e1;
  padding: 0 1rem;
}

.tab {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 3px solid transparent;
  font-weight: 600;
  color: #64748b;
  border-radius: 16px 16px 0 0;
  margin: 0 0.25rem;
  position: relative;
  overflow: hidden;
}

.tab::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.tab:hover::before {
  opacity: 1;
}

.tab:hover {
  color: #6366f1;
  transform: translateY(-2px);
}

.tab.active {
  color: #6366f1;
  background: white;
  border-bottom-color: #6366f1;
  box-shadow: 0 -4px 20px rgba(99, 102, 241, 0.15);
}

.tab.active::before {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  opacity: 1;
}

.tab i {
  font-size: 1.25rem;
  position: relative;
  z-index: 1;
}

.tab-content {
  padding: 2.5rem;
}

/* Contenido de pestaña Resumen */
.info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
  gap: 2rem;
}

.info-card {
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  position: relative;
}

.info-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.info-card h3 {
  margin: 0;
  padding: 1.25rem 1.5rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  font-size: 1.1rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.info-card h3 i {
  font-size: 1.3rem;
  opacity: 0.9;
}

.info-grid {
  display: table;
  width: 100%;
  table-layout: fixed;
  padding: 0;
  margin: 0;
}

.info-item {
  display: table-row;
  border-bottom: 1px solid #f1f5f9;
  transition: background-color 0.2s ease;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item:hover {
  background-color: rgba(99, 102, 241, 0.02);
}

.info-label, .info-value {
  display: table-cell;
  padding: 0.875rem 1.5rem;
  vertical-align: middle;
  line-height: 1.4;
}

.info-label {
  width: 45%;
  font-size: 0.95rem;
  color: #64748b;
  font-weight: 600;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-right: 1px solid #e2e8f0;
}

.info-value {
  width: 55%;
  font-size: 1rem;
  color: #1e293b;
  font-weight: 500;
}





.stat-item:hover {
  transform: translateY(-6px);
  box-shadow: 0 15px 35px rgba(99, 102, 241, 0.2);
  border-color: rgba(99, 102, 241, 0.2);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
}

.stat-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
}

.stat-icon i {
  font-size: 1.75rem;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 800;
  color: #6366f1;
  margin-bottom: 0.25rem;
  text-shadow: 0 2px 4px rgba(99, 102, 241, 0.1);
}

.stat-label {
  font-size: 1rem;
  color: #64748b;
  font-weight: 600;
  letter-spacing: 0.025em;
}

.category-container {
  padding: 1.5rem;
}
















.profesionales-list {
  padding: 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.profesional-card {
  display: flex;
  gap: 1rem;
  padding: 1.25rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  border-radius: 16px;
  align-items: center;
  border: 2px solid rgba(99, 102, 241, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.profesional-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.profesional-card:hover::before {
  opacity: 1;
}

.profesional-card:hover {
  transform: translateY(-4px);
  border-color: rgba(99, 102, 241, 0.2);
  box-shadow: 0 12px 30px rgba(99, 102, 241, 0.15);
}

.profesional-avatar {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.3);
  position: relative;
  z-index: 1;
}

.profesional-avatar i {
  font-size: 1.25rem;
}

.profesional-info {
  flex: 1;
  position: relative;
  z-index: 1;
}

.profesional-name {
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.25rem;
  font-size: 1rem;
}

.profesional-role {
  color: #64748b;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.profesional-email {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #6366f1;
  font-weight: 500;
}

.profesional-email i {
  font-size: 1rem;
}

.empty-message {
  padding: 2rem;
  text-align: center;
  color: #64748b;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  border-radius: 16px;
  margin: 1rem;
  border: 2px dashed rgba(99, 102, 241, 0.2);
}

.empty-message i {
  font-size: 3rem;
  color: #6366f1;
  opacity: 0.7;
}

/* Contenido de pestaña Insumos */
.tab-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1.5rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  border-radius: 16px;
  border: 1px solid rgba(99, 102, 241, 0.1);
}

.search-box {
  position: relative;
  min-width: 280px;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6366f1;
  font-size: 1.2rem;
}

.search-box input {
  width: 100%;
  padding: 0.875rem 1rem 0.875rem 3rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  background: white;
  transition: all 0.3s ease;
}

.search-box input:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  outline: none;
}

.insumos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
}

.insumo-card {
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.insumo-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border-color: rgba(99, 102, 241, 0.2);
}

.insumo-header {
  display: flex;
  padding: 1.5rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  align-items: center;
  color: white;
}

.insumo-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  backdrop-filter: blur(10px);
}

.insumo-icon i {
  font-size: 1.5rem;
}

.insumo-title {
  flex: 1;
}

.insumo-title h4 {
  margin: 0 0 0.5rem;
  font-size: 1.2rem;
  color: white;
  font-weight: 700;
}

.categoria-badge {
  display: inline-block;
  padding: 0.375rem 0.875rem;
  font-size: 0.8rem;
  border-radius: 20px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  backdrop-filter: blur(10px);
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
  background-color: #f3e5f5;
  color: #6a1b9a;
}

.categoria-badge.catastral {
  background-color: #e8eaf6;
  color: #303f9f;
}

.categoria-badge.default {
  background-color: #eceff1;
  color: #455a64;
}

.categoria-badge-small {
  font-size: 0.7rem;
  padding: 0.15rem 0.35rem;
}

.insumo-actions {
  display: flex;
  gap: 0.5rem;
}

.insumo-body {
  padding: 1rem;
  flex: 1;
}

.insumo-details {
  margin-bottom: 1rem;
}

.detail-row {
  display: flex;
  margin-bottom: 0.5rem;
}

.detail-label {
  width: 180px;
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 500;
}

.detail-value {
  flex: 5;
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

.clasificaciones-list h5 {
  margin: 0 0 0.75rem;
  font-size: 0.95rem;
  color: #343a40;
}

.clasificacion-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0;
}

.clasificacion-item i {
  color: #6c757d;
  font-size: 1.1rem;
}

.clasificacion-nombre {
  font-size: 0.95rem;
  color: #495057;
}

.insumo-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid #dee2e6;
  text-align: right;
}

/* Clasificaciones */
.clasificaciones-list-detailed {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 2rem;
}

.clasificacion-card {
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.clasificacion-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border-color: rgba(99, 102, 241, 0.2);
}

.clasificacion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
}

.clasificacion-title h4 {
  margin: 0;
  font-size: 1.2rem;
  color: white;
  font-weight: 700;
}

.clasificacion-nombre {
  font-size: 1.2rem;
  font-weight: 700;
  color: rgb(10, 5, 88);
  margin: 0 0 0.5rem;
}

.insumo-code {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  backdrop-filter: blur(10px);
}

.clasificacion-actions {
  display: flex;
  gap: 0.75rem;
}

.clasificacion-body {
  padding: 1.5rem;
}

.clasificacion-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  text-align: right;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

/* Archivos */
.archivos-inner-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 2rem;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 16px 16px 0 0;
  overflow: hidden;
}

.inner-tab {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem 2rem;
  background-color: transparent;
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  position: relative;
  font-weight: 600;
  border-radius: 16px 16px 0 0;
}

.inner-tab::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.inner-tab:hover::before {
  opacity: 1;
}

.inner-tab:hover {
  color: #6366f1;
}

.inner-tab.active {
  color: #6366f1;
  background: white;
  border-bottom: 3px solid #6366f1;
  box-shadow: 0 -4px 20px rgba(99, 102, 241, 0.15);
}

.inner-tab.active::before {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  opacity: 1;
}

.inner-tab i {
  font-size: 1.3rem;
  position: relative;
  z-index: 1;
}

.archivos-filters {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  border-radius: 16px;
  border: 1px solid rgba(99, 102, 241, 0.1);
}




.concepto-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border-color: rgba(99, 102, 241, 0.2);
}

.concepto-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
}

.concepto-header h4 {
  margin: 0;
  font-size: 1.2rem;
  color: white;
  font-weight: 700;
}

.concepto-meta {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.concepto-fecha {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  backdrop-filter: blur(10px);
}

.concepto-body {
  padding: 1.5rem;
}

.concepto-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
}

.concepto-row {
  display: flex;
  border-bottom: 1px solid #f1f5f9;
}

.concepto-row:last-child {
  border-bottom: none;
}

.concepto-cell {
  padding: 1rem 1.25rem;
  flex: 1;
}

.concepto-cell.header {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  font-weight: 700;
  width: 200px;
  flex: 0 0 200px;
  color: #374151;
  border-right: 1px solid #e2e8f0;
}

.concepto-detail-section,
.concepto-observation-section {
  margin-top: 1.5rem;
  padding: 1.25rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  border-radius: 12px;
  border: 1px solid rgba(99, 102, 241, 0.1);
}

.concepto-detail-header,
.concepto-observation-header {
  font-weight: 700;
  margin-bottom: 0.75rem;
  color: #374151;
  font-size: 1rem;
}

.concepto-detail-content,
.concepto-observation-content {
  white-space: pre-wrap;
  color: #1e293b;
  line-height: 1.6;
  font-size: 0.95rem;
}

.concepto-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  text-align: right;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.evaluacion-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  font-size: 0.8rem;
  font-weight: 700;
  line-height: 1;
  color: #1014C5;
  text-align: center;
  white-space: nowrap;
  vertical-align: baseline;
  border-radius: 20px;
  letter-spacing: 0.025em;
  text-transform: uppercase;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.evaluacion-badge.success {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

.evaluacion-badge.danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.evaluacion-badge.warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.evaluacion-badge.info {
  background: linear-gradient(135deg, #06b6d4 0%, #0e7490 100%);
  color: white;
}

.evaluacion-badge.default {
  background: linear-gradient(135deg, #64748b 0%, #475569 100%);
}

/* Modal para detalles de archivo */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(8px);
  animation: modalBackdropFadeIn 0.3s ease;
}

@keyframes modalBackdropFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-container {
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 24px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  width: 100%;
  max-width: 700px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(10px);
  animation: modalSlideIn 0.3s ease;
}



.archivo-details-modal {
  max-width: 900px;
  max-height: 85vh;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem 2.5rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 24px 24px 0 0;
  color: white;
  position: relative;
  overflow: hidden;
}

.modal-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1.5" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="80" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
  pointer-events: none;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: white;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  position: relative;
  z-index: 1;
}

.modal-header h2 i {
  font-size: 1.75rem;
  opacity: 0.9;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  cursor: pointer;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 1;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.4);
  transform: scale(1.1);
}

.close-btn i {
  font-size: 1.25rem;
}

.modal-body {
  padding: 2.5rem;
  overflow-y: auto;
  max-height: calc(90vh - 200px);
}

.modal-footer {
  padding: 1.5rem 2.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 0 0 24px 24px;
}

.archivo-details-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.details-section {
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  overflow: hidden;
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
}

.details-section h3 {
  margin: 0;
  padding: 1.25rem 1.5rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  font-size: 1.1rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.details-section h3 i {
  font-size: 1.3rem;
  opacity: 0.9;
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
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
  border-right: 1px solid #f1f5f9;
  transition: background-color 0.2s ease;
}

.detail-item:hover {
  background-color: rgba(99, 102, 241, 0.02);
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

.detail-label {
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.detail-value {
  font-size: 1rem;
  color: #1e293b;
  font-weight: 500;
  word-break: break-word;
}

.ruta-completa {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.9rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  max-height: 140px;
  overflow-y: auto;
  word-break: break-all;
  line-height: 1.5;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
}

.observaciones-content {
  padding: 1.25rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  margin: 0;
  font-size: 1rem;
  color: #374151;
  line-height: 1.6;
  white-space: pre-wrap;
  border-radius: 12px;
  border: 1px solid rgba(99, 102, 241, 0.1);
}

.archivo-type-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.archivo-type-badge.pre {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
}

.archivo-type-badge.post {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #166534;
}

.status-approved {
  color: #22c55e;
  font-weight: 700;
  text-shadow: 0 1px 2px rgba(34, 197, 94, 0.2);
}

/* Notificaciones */
.notification {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  min-width: 350px;
  max-width: 450px;
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  z-index: 1100;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: space-between;
  animation: notificationSlideIn 0.4s ease;
  border: 1px solid rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(10px);
}

@keyframes notificationSlideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.75rem;
  flex: 1;
}

.notification-content i {
  font-size: 1.75rem;
  flex-shrink: 0;
}

.notification-content span {
  font-size: 1rem;
  font-weight: 500;
  line-height: 1.4;
}

.notification-close {
  background: rgba(107, 114, 128, 0.1);
  border: none;
  color: #6b7280;
  cursor: pointer;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  transition: all 0.2s ease;
}

.notification-close:hover {
  background: rgba(107, 114, 128, 0.2);
  transform: scale(1.1);
}

.notification.success {
  border-left: 5px solid #22c55e;
}

.notification.success i {
  color: #22c55e;
}

.notification.error {
  border-left: 5px solid #ef4444;
}

.notification.error i {
  color: #ef4444;
}

.notification.warning {
  border-left: 5px solid #f59e0b;
}

.notification.warning i {
  color: #f59e0b;
}

.notification.info {
  border-left: 5px solid #06b6d4;
}

.notification.info i {
  color: #06b6d4;
}

/* Responsive */
@media (max-width: 1200px) {
    .modal-detalle-insumo {
    max-width: 95%;
    margin: 0 2.5%;
  }
    .data-table {
    min-width: 800px; /* ✅ Reducir ancho mínimo en pantallas medianas */
  }
  
  .archivos-content .data-table th:nth-child(1),
  .archivos-content .data-table td:nth-child(1) {
    min-width: 150px; /* ✅ Reducir mínimo para nombres */
  }

  .info-cards {
    grid-template-columns: 1fr;
  }
  
  .clasificaciones-list-detailed {
    grid-template-columns: 1fr;
  }
  
  .insumos-list-page {
    padding: 1rem;
    gap: 1.5rem;
  }
}

@media (max-width: 992px) {
  .insumos-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1.5rem;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .detail-header {
    flex-wrap: wrap;
    padding: 1.5rem 2rem;
  }
  
  .detail-actions {
    margin-left: 0;
    width: 100%;
    margin-top: 1.5rem;
  }
  
  .tab-content {
    padding: 2rem;
  }
  .stats-container {
    gap: 0.75rem;
  }
  
  .stat-item {
    padding: 1rem;
    min-width: 100px;
  }
}

@media (max-width: 768px) {
    .modal-content {
    width: 95% !important;
    max-width: 95% !important;
    margin: 0 auto !important;
  }
  .peso-memoria-badge {
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
  }
  
  .peso-memoria-badge.large {
    font-size: 0.8rem;
    padding: 0.4rem 0.75rem;
  }
  
    .modal-content {
    max-width: 95%;
    margin: 0 2.5%;
    max-height: 95vh;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 1.5rem;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .clasificaciones-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
    padding: 1rem;
  }
  
  .stats-grid-modal {
    grid-template-columns: 1fr;
    gap: 1rem;
    padding: 1rem;
  }
  
  .stat-card-modal {
    padding: 1rem;
  }
  
  .stat-number {
    font-size: 1.5rem;
  }
    .data-table {
    min-width: 700px; /* ✅ Más compacto en móviles */
  }
  
  .btn-icon.small {
    width: 28px; /* ✅ Botones aún más pequeños en móvil */
    height: 28px;
    min-width: 28px;
  }
  
  .row-actions {
    gap: 0.25rem; /* ✅ Menos gap en móvil */
    min-width: 100px;
  }
    .filter-item select {
    max-width: 100%;
    font-size: 0.85rem;
  }
  
  .no-data-message {
    font-size: 0.8rem;
    padding: 0.5rem;
  }
  
  .debug-btn {
    font-size: 0.75rem;
    padding: 0.4rem 0.6rem;
  }

      .stats-container {
    flex-direction: column;
    gap: 1rem;
  }
  
  .stat-item {
    padding: 1.25rem;
    min-width: auto;
    max-width: none;
  }
  .archivo-details-modal {
    max-width: 95%;
    margin: 0 2.5%;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-item {
    border-right: none;
  }
  
  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-actions {
    margin-left: 0;
    margin-top: 1.5rem;
  }
  
  .detail-tabs {
    overflow-x: auto;
    padding: 0 0.5rem;
  }
  
  .tab {
    white-space: nowrap;
    padding: 1rem 1.25rem;
    min-width: fit-content;
  }
  
  .notification {
    min-width: auto;
    max-width: 90%;
    left: 5%;
    right: 5%;
    bottom: 1rem;
  }
  
  .stats-container {
    flex-direction: column;
    gap: 1rem;
  }
  
  .stat-item {
    padding: 1.25rem;
  }
  
  .stat-value {
    font-size: 2rem;
  }
  
  .page-header,
  .filters-panel,
  .tab-content {
    padding: 1.5rem;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 1.5rem;
  }
}

@media (max-width: 576px) {
    .modal-header h3 {
    font-size: 1.25rem;
  }
  
  .modal-footer {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .tabla-detalles {
    font-size: 0.85rem;
  }
  
  .tabla-detalles th,
  .tabla-detalles td {
    padding: 0.5rem;
  }
  .btn-primary,
  .btn-secondary,
  .btn-outline {
    padding: 0.75rem 1.25rem;
    font-size: 0.95rem;
  }
  
  .modal-container {
    max-width: 95%;
    margin: 0 2.5%;
  }
  
  .insumos-list-page {
    padding: 0.75rem;
  }
  
  .header-content h1 {
    font-size: 1.75rem;
  }
  
  .detail-header h2 {
    font-size: 1.5rem;
  }
    .stats-container {
    padding: 1rem;
  }
  
  .stat-item {
    padding: 1rem;
  }
}

/* Mejoras adicionales para el efecto glassmorphism */
.filters-panel,
.municipio-detail,
.info-card,
.clasificacion-card,
.concepto-card,
.insumo-card {
  position: relative;
}

.filters-panel::before,
.municipio-detail::before,
.info-card::before,
.clasificacion-card::before,
.concepto-card::before,
.insumo-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  border-radius: inherit;
  pointer-events: none;
  z-index: 0;
}

.filters-panel > *,
.municipio-detail > *,
.info-card > *,
.clasificacion-card > *,
.concepto-card > *,
.insumo-card > * {
  position: relative;
  z-index: 1;
}
</style>