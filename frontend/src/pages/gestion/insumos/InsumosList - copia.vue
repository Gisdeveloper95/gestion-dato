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

              <!-- Estadísticas de insumos mejoradas -->
              <div class="info-card">
                <h3>Estadísticas de Insumos</h3>
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
                  <div v-else class="category-bars">
                    <div v-for="(info, categoria) in insumosPorCategoria" :key="categoria" class="category-bar">
                      <div class="bar-label">
                        <a href="#" @click.prevent="irAInsumosPorCategoria(info.id)">{{ categoria }}</a>
                      </div>
                      <div class="bar-container">
                        <div class="bar-value" :style="{ width: `${(info.count/municipioInsumos.length)*100}%` }"></div>
                      </div>
                      <div class="bar-count">{{ info.count }}</div>
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
                  
                  <div class="clasificaciones-list" v-if="getClasificaciones(insumo.cod_insumo).length > 0">
                    <h5>Clasificaciones:</h5>
                    <div v-for="clasif in getClasificaciones(insumo.cod_insumo)" :key="clasif.cod_clasificacion" class="clasificacion-item">
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
                      <span class="detail-value path-value">{{ clasificacion.ruta }}</span>
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
          
          <!-- Pestaña de Detalles -->
          <div v-else-if="activeTab === 'detalles'" class="detalles-tab">
            <div class="tab-actions">
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
              
              <button 
                v-if="authStore.isAnyAdmin"
                @click="createDetalle" 
                class="btn-primary"
              >
                <i class="material-icons">add</i>
                Nuevo Detalle
              </button>
            </div>
            
            <div v-if="municipioDetalles.length === 0" class="empty-message">
              No hay detalles de insumo registrados para este municipio.
            </div>
            
            <div v-else class="detalles-table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Clasificación</th>
                    <th>Escala</th>
                    <th>Estado</th>
                    <th>Entidad</th>
                    <th>Formato</th>
                    <th>Usuario</th>
                    <th>Fecha Entrega</th>
                    <th v-if="authStore.isAnyAdmin">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="detalle in filteredDetalles" :key="detalle.cod_detalle">
                    <td>{{ detalle.cod_detalle }}</td>
                    <td>{{ getNombreClasificacion(detalle.cod_clasificacion) }}</td>
                    <td>{{ detalle.escala || '-' }}</td>
                    <td>{{ detalle.estado || '-' }}</td>
                    <td>{{ getNombreEntidad(detalle.cod_entidad) }}</td>
                    <td>{{ detalle.formato_tipo }}</td>
                    <td>{{ getNombreUsuario(detalle.cod_usuario) }}</td>
                    <td>{{ formatDate(detalle.fecha_entrega) }}</td>
                    <td v-if="authStore.isAnyAdmin">
                      <div class="row-actions">
                        <!-- 🔥 BOTÓN CORREGIDO -->
                        <button @click="showDetalleModal(detalle)" class="btn-icon small primary" title="Ver detalle">
                          <i class="material-icons">visibility</i>
                        </button>
                        <button @click="editDetalle(detalle)" class="btn-icon small warning" title="Editar">
                          <i class="material-icons">edit</i>
                        </button>
                        <button @click="showDeleteDetalleModal(detalle)" class="btn-icon small danger" title="Eliminar">
                          <i class="material-icons">delete</i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
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
          
          <!-- Pestaña de Archivos mejorada con filtros y vista tabla -->
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
            
            <!-- Contenido de archivos de preoperación -->
            <div v-if="activeArchivosTab === 'preoperacion'" class="archivos-content">
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
                <i class="material-icons">insert_drive_file</i>
                <p>No hay archivos de preoperación registrados para este municipio.</p>
              </div>
              
              <div v-else>
                <!-- Filtros específicos para preoperación -->
                <div class="archivos-filters">
                  <div class="filters-row">
                    <!-- Filtro por clasificación -->
                    <div class="filter-item">
                      <label>Filtrar por clasificación:</label>
                      <select v-model="filtroClasificacionPre">
                        <option value="">Todas las clasificaciones</option>
                        <option 
                          v-for="clasificacion in clasificacionesUnicasPre" 
                          :key="clasificacion" 
                          :value="clasificacion"
                        >
                          {{ clasificacion }}
                        </option>
                      </select>
                    </div>
                    
                    <!-- Filtro por nombre de archivo -->
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
                </div>
                
                <!-- Vista de tabla para archivos de preoperación -->
                <div class="table-responsive">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th>Nombre</th>
                        <th>Clasificación</th>
                        <th>Fecha</th>
                        <th>Observación</th>
                        <th>Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="archivo in filteredArchivosPre" :key="archivo.id_lista_archivo">
                        <td>
                          <div class="file-info">
                            <i class="material-icons file-icon">{{ getFileIcon(archivo.nombre_insumo) }}</i>
                            <span>{{ archivo.nombre_insumo }}</span>
                          </div>
                        </td>
                        <td>{{ getNombreClasificacion(archivo.cod_insumo) }}</td>
                        <td>{{ formatDate(archivo.fecha_disposicion) }}</td>
                        <td>{{ archivo.observacion || 'Sin observaciones' }}</td>
                        <td>
                          <div class="row-actions">
                            <button @click="viewArchivo(archivo)" class="btn-icon small primary" 
                              :title="['gdb', 'zip', 'rar', '7z'].includes(getFileExtension(archivo.nombre_insumo)) ? 'Descargar archivo' :
                                    getFileExtension(archivo.nombre_insumo) === 'pdf' ? 'Ver PDF en nueva ventana' : 
                                    ['jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff', 'xlsx', 'xls', 'docx', 'doc'].includes(getFileExtension(archivo.nombre_insumo)) ? 'Abrir archivo' : 'Descargar archivo'">
                              <i class="material-icons">{{ ['gdb', 'zip', 'rar', '7z'].includes(getFileExtension(archivo.nombre_insumo)) ? 'download' :
                                getFileExtension(archivo.nombre_insumo) === 'pdf' ? 'open_in_new' : 
                                ['jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff', 'xlsx', 'xls', 'docx', 'doc'].includes(getFileExtension(archivo.nombre_insumo)) ? 'visibility' : 'download' }}</i>
                            </button>
                            <!-- Botón de ver detalles añadido -->
                            <button @click="showArchivoDetails(archivo, 'pre')" class="btn-icon small info" title="Ver detalles">
                              <i class="material-icons">info</i>
                            </button>
                            <button @click="downloadArchivo(archivo)" class="btn-icon small success" title="Descargar">
                              <i class="material-icons">download</i>
                            </button>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
            
            <!-- Contenido de archivos de postoperación -->
            <div v-if="activeArchivosTab === 'postoperacion'" class="archivos-content">
              <div v-if="archivosPostLoading" class="loading-state">
                <div class="spinner"></div>
                <p>Cargando archivos de postoperación...</p>
              </div>
              
              <div v-else-if="archivosPostError" class="error-state">
                <i class="material-icons">error</i>
                <p>{{ archivosPostError }}</p>
                <button @click="cargarArchivosPost" class="btn-primary">Reintentar</button>
              </div>
              
              <div v-else-if="municipioArchivosPost.length === 0" class="empty-message">
                <i class="material-icons">insert_drive_file</i>
                <p>No hay archivos de postoperación registrados para este municipio.</p>
              </div>
              
              <div v-else>
                <!-- Filtros específicos para postoperación -->
                <div class="archivos-filters">
                  <div class="filters-row">
                    <!-- Filtro por componente -->
                    <div class="filter-item">
                      <label>Filtrar por componente:</label>
                      <select v-model="filtroComponentePost">
                        <option value="">Todos los componentes</option>
                        <option 
                          v-for="componente in componentesUnicosPost" 
                          :key="componente" 
                          :value="componente"
                        >
                          {{ componente }}
                        </option>
                      </select>
                    </div>
                    
                    <!-- Filtro por nombre de archivo -->
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
                  </div>
                </div>
                
                <!-- Vista de tabla para archivos de postoperación -->
                <div class="table-responsive">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th>Nombre</th>
                        <th>Componente</th>
                        <th>Fecha</th>
                        <th>Observación</th>
                        <th>Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="archivo in filteredArchivosPost" :key="archivo.id_archivo">
                        <td>
                          <div class="file-info">
                            <i class="material-icons file-icon">{{ getFileIcon(archivo.nombre_archivo) }}</i>
                            <span>{{ archivo.nombre_archivo }}</span>
                          </div>
                        </td>
                        <td>{{ archivo.disposicion_info?.componente || 'No especificado' }}</td>
                        <td>{{ formatDate(archivo.fecha_disposicion) }}</td>
                        <td>{{ archivo.observacion || 'Sin observaciones' }}</td>
                        <td>
                          <div class="row-actions">
                            <button @click="viewArchivoPost(archivo)" class="btn-icon small primary" 
                              :title="['gdb', 'zip', 'rar', '7z'].includes(getFileExtension(archivo.nombre_archivo)) ? 'Descargar archivo' :
                                    getFileExtension(archivo.nombre_archivo) === 'pdf' ? 'Ver PDF en nueva ventana' : 
                                    ['jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff', 'xlsx', 'xls', 'docx', 'doc'].includes(getFileExtension(archivo.nombre_archivo)) ? 'Abrir archivo' : 'Descargar archivo'">
                              <i class="material-icons">{{ ['gdb', 'zip', 'rar', '7z'].includes(getFileExtension(archivo.nombre_archivo)) ? 'download' :
                                getFileExtension(archivo.nombre_archivo) === 'pdf' ? 'open_in_new' : 
                                ['jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff', 'xlsx', 'xls', 'docx', 'doc'].includes(getFileExtension(archivo.nombre_archivo)) ? 'visibility' : 'download' }}</i>
                            </button>
                            <!-- Botón de ver detalles añadido -->
                            <button @click="showArchivoDetails(archivo, 'post')" class="btn-icon small info" title="Ver detalles">
                              <i class="material-icons">info</i>
                            </button>
                            <button @click="downloadArchivoPost(archivo)" class="btn-icon small success" title="Descargar">
                              <i class="material-icons">download</i>
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
                <div class="detail-item">
                  <span class="detail-label">Extensión:</span>
                  <span class="detail-value">
                    .{{ getFileExtension(archivoDetailsType === 'pre' ? selectedArchivoDetails.nombre_insumo : selectedArchivoDetails.nombre_archivo).toUpperCase() }}
                  </span>
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
                  <span class="detail-value">{{ getArchivoExtraInfo(selectedArchivoDetails, archivoDetailsType).departamento }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Municipio:</span>
                  <span class="detail-value">{{ getArchivoExtraInfo(selectedArchivoDetails, archivoDetailsType).municipio }}</span>
                </div>
                <div class="detail-item full-width">
                  <span class="detail-label">Ruta completa:</span>
                  <div class="ruta-completa">
                    {{ getArchivoExtraInfo(selectedArchivoDetails, archivoDetailsType).ruta }}
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

    <!-- 🔥 MODAL DE DETALLES SIMPLIFICADO QUE SÍ FUNCIONA -->
    <div v-if="detalleModalVisible" 
         style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                background: rgba(0,0,0,0.8); z-index: 999999; 
                display: flex; justify-content: center; align-items: center;"
         @click="detalleModalVisible = false">
      
      <div style="background: white; padding: 2rem; border-radius: 8px; 
                  max-width: 800px; width: 90%; max-height: 80vh; overflow-y: auto;" 
           @click.stop>
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
          <h2 style="margin: 0; color: #343a40;">
            <i class="material-icons" style="vertical-align: middle; margin-right: 0.5rem;">description</i>
            Detalle #{{ detalleSeleccionado?.cod_detalle }}
          </h2>
          <button @click="detalleModalVisible = false" 
                  style="background: #dc3545; color: white; border: none; 
                         width: 40px; height: 40px; border-radius: 50%; 
                         display: flex; align-items: center; justify-content: center; cursor: pointer;">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div v-if="detalleSeleccionado" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 2rem;">
          <div style="padding: 0.75rem; background: #f8f9fa; border-radius: 4px;">
            <strong style="color: #6c757d; font-size: 0.875rem;">Código:</strong>
            <div style="font-size: 1rem; color: #212529; margin-top: 0.25rem;">{{ detalleSeleccionado.cod_detalle }}</div>
          </div>
          
          <div style="padding: 0.75rem; background: #f8f9fa; border-radius: 4px;">
            <strong style="color: #6c757d; font-size: 0.875rem;">Municipio:</strong>
            <div style="font-size: 1rem; color: #212529; margin-top: 0.25rem;">{{ selectedMunicipio?.nom_municipio || 'N/A' }}</div>
          </div>
          
          <div style="padding: 0.75rem; background: #f8f9fa; border-radius: 4px;">
            <strong style="color: #6c757d; font-size: 0.875rem;">Clasificación:</strong>
            <div style="font-size: 1rem; color: #212529; margin-top: 0.25rem;">{{ getNombreClasificacion(detalleSeleccionado.cod_clasificacion) || 'N/A' }}</div>
          </div>
          
          <div style="padding: 0.75rem; background: #f8f9fa; border-radius: 4px;">
            <strong style="color: #6c757d; font-size: 0.875rem;">Estado:</strong>
            <div style="font-size: 1rem; margin-top: 0.25rem;">
              <span :class="['estado-badge', getEstadoClass(detalleSeleccionado.estado)]">
                {{ detalleSeleccionado.estado || 'N/A' }}
              </span>
            </div>
          </div>
          
          <div style="padding: 0.75rem; background: #f8f9fa; border-radius: 4px;">
            <strong style="color: #6c757d; font-size: 0.875rem;">Escala:</strong>
            <div style="font-size: 1rem; color: #212529; margin-top: 0.25rem;">{{ detalleSeleccionado.escala || 'N/A' }}</div>
          </div>
          
          <div style="padding: 0.75rem; background: #f8f9fa; border-radius: 4px;">
            <strong style="color: #6c757d; font-size: 0.875rem;">Cubrimiento:</strong>
            <div style="font-size: 1rem; color: #212529; margin-top: 0.25rem;">{{ detalleSeleccionado.cubrimiento || 'N/A' }}</div>
          </div>
          
          <div style="padding: 0.75rem; background: #f8f9fa; border-radius: 4px;">
            <strong style="color: #6c757d; font-size: 0.875rem;">Entidad:</strong>
            <div style="font-size: 1rem; color: #212529; margin-top: 0.25rem;">{{ getNombreEntidad(detalleSeleccionado.cod_entidad) }}</div>
          </div>
          
          <div style="padding: 0.75rem; background: #f8f9fa; border-radius: 4px;">
            <strong style="color: #6c757d; font-size: 0.875rem;">Formato:</strong>
            <div style="font-size: 1rem; color: #212529; margin-top: 0.25rem;">{{ detalleSeleccionado.formato_tipo || 'N/A' }}</div>
          </div>
          
          <div style="padding: 0.75rem; background: #f8f9fa; border-radius: 4px;">
            <strong style="color: #6c757d; font-size: 0.875rem;">Usuario:</strong>
            <div style="font-size: 1rem; color: #212529; margin-top: 0.25rem;">{{ getNombreUsuario(detalleSeleccionado.cod_usuario) }}</div>
          </div>
          
          <div style="padding: 0.75rem; background: #f8f9fa; border-radius: 4px;">
            <strong style="color: #6c757d; font-size: 0.875rem;">Fecha Entrega:</strong>
            <div style="font-size: 1rem; color: #212529; margin-top: 0.25rem;">{{ formatDate(detalleSeleccionado.fecha_entrega) }}</div>
          </div>
        </div>
        
        <div v-if="detalleSeleccionado?.observacion" style="padding: 1rem; background: #e3f2fd; border-radius: 4px; margin-bottom: 1.5rem;">
          <strong style="color: #1565c0; font-size: 0.875rem; display: block; margin-bottom: 0.5rem;">Observación:</strong>
          <div style="color: #1976d2;">{{ detalleSeleccionado.observacion }}</div>
        </div>
        
        <div style="display: flex; justify-content: flex-end; gap: 1rem;">
          <button @click="detalleModalVisible = false" 
                  style="background: #6c757d; color: white; border: none; 
                         padding: 0.75rem 1.5rem; border-radius: 4px; cursor: pointer;">
            Cerrar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de detalles de insumo MEJORADO -->
    <div v-if="modalDetalleInsumo.mostrar" class="modal-overlay" style="z-index: 99999 !important;" @click="modalDetalleInsumo.mostrar = false">
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
                v-for="clasificacion in getClasificaciones(modalDetalleInsumo.insumo.cod_insumo)" 
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
                    <span class="ruta-text">{{ clasificacion.ruta }}</span>
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
                <div class="clasificacion-actions">
                  <button 
                    @click="verDetallesDeClasificacion(clasificacion)"
                    class="btn btn-primary btn-sm"
                  >
                    <i class="material-icons">visibility</i>
                    Ver detalles ({{ getDetallesCount(clasificacion.cod_clasificacion) }})
                  </button>
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
    
    <!-- Mensajes de notificación -->
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
import { defineComponent, ref, computed, watch, onMounted, nextTick  } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { format, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';
// ✅ IMPORTAR EL STORE DE AUTH PARA PERMISOS
import { useAuthStore } from '@/store/auth';
// Importar servicios API
import { 
  getClasificacionesByMunicipio, getDetallesByMunicipio 
} from '@/api/municipios';
import axios from 'axios'
import { 
  createInsumo, updateInsumo, deleteInsumo, 
  createClasificacion, updateClasificacion, deleteClasificacion,
  createDetalle, updateDetalle, deleteDetalle,
  getClasificaciones,
  getProfesionalesSeguimiento, getArchivosByClasificacion,getMecanismosGenerales,
  getMecanismosDetalle, getMecanismosOperacion,getAlcancesOperacion,getGrupos,
  getTerritoriales,
} from '@/api/insumos';


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

export default defineComponent({
  name: 'InsumosList',
  
  setup() {
    const detalleModalVisible = ref(false);
    const detalleSeleccionado = ref(null);

    const route = useRoute();
    const router = useRouter();
    // ✅ USAR EL STORE DE AUTH PARA PERMISOS
    const authStore = useAuthStore();
    
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
    
    // Municipio seleccionado
    const selectedMunicipioId = ref<number | null>(null);
    const selectedMunicipio = ref<any | null>(null);
    const municipioInsumos = ref<any[]>([]);
    const municipioClasificaciones = ref<any[]>([]);
    const municipioDetalles = ref<any[]>([]);
    const municipioArchivos = ref<any[]>([]);
    const municipioProfesionales = ref<any[]>([]);
    
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


    // Implementa la función cargarTodosLosDatos
const cargarTodosLosDatos = async (endpoint: string, params = {}) => {
  let allResults = [];
  let nextUrl = endpoint;
  
  // Convertir URL completa a endpoint relativo si es necesario
  if (nextUrl.startsWith('http') || nextUrl.includes(API_URL)) {
    try {
      const urlObj = new URL(nextUrl);
      nextUrl = urlObj.pathname;
    } catch (e) {
      nextUrl = endpoint.replace(API_URL || '', '');
    }
  }
  
  while (nextUrl) {
    try {
      // ✅ USAR API EN LUGAR DE FETCH MANUAL
      const response = await api.get(nextUrl, { params });
      
      let data;
      if (response && typeof response === 'object') {
        data = response;
      } else {
        console.warn('Respuesta inesperada:', response);
        break;
      }
      
      if (data.results && Array.isArray(data.results)) {
        allResults = [...allResults, ...data.results];
        nextUrl = data.next;
        
        // Convertir próxima URL a endpoint relativo si es necesario
        if (nextUrl && nextUrl.startsWith('http')) {
          try {
            const urlObj = new URL(nextUrl);
            nextUrl = urlObj.pathname + urlObj.search;
          } catch (e) {
            nextUrl = null;
          }
        }
      } else if (Array.isArray(data)) {
        allResults = [...allResults, ...data];
        nextUrl = null;
      } else {
        allResults = Array.isArray(data) ? data : [];
        nextUrl = null;
      }
      
      params = {};
      
    } catch (error) {
      console.error('Error cargando datos desde:', nextUrl, error);
      throw error;
    }
  }
  
  return allResults;
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















    // ========================================================================================
// 4. FUNCIÓN CORREGIDA: loadInitialData
// ========================================================================================
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
      // ✅ USAR ENDPOINTS RELATIVOS EN LUGAR DE URLs COMPLETAS
      cargarTodosLosDatos('/preoperacion/departamentos/'),
      cargarTodosLosDatos('/preoperacion/municipios/'),
      cargarTodosLosDatos('/preoperacion/categorias/'),
      cargarTodosLosDatos('/preoperacion/tipos-insumo/'),
      cargarTodosLosDatos('/preoperacion/mecanismos-general/'),
      cargarTodosLosDatos('/preoperacion/mecanismos-detalle/'),
      cargarTodosLosDatos('/preoperacion/grupos/'),
      cargarTodosLosDatos('/preoperacion/territoriales/'),
      cargarTodosLosDatos('/preoperacion/entidades/'),
      cargarTodosLosDatos('/preoperacion/usuarios/')
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
    
    console.log(`✅ Datos iniciales cargados: ${municipiosList.value.length} municipios`);
    
  } catch (err: any) {
    console.error('❌ Error cargando datos iniciales:', err);
    error.value = 'Error cargando datos. Por favor, intente nuevamente.';
  } finally {
    loading.value = false;
  }
};

// ========================================================================================
// 5. FUNCIÓN CORREGIDA: loadProfesionalesForMunicipio
// ========================================================================================
const loadProfesionalesForMunicipio = async (municipioId: number) => {
  try {
    console.log(`Cargando profesionales para municipio ${municipioId}...`);
    
    // ✅ USAR API EN LUGAR DE FETCH MANUAL
    const response = await api.get(`/preoperacion/municipios/${municipioId}/profesionales/`);
    
    let profesionales = [];
    if (response && Array.isArray(response)) {
      profesionales = response;
    } else if (response.results && Array.isArray(response.results)) {
      profesionales = response.results;
    }
    
    municipioProfesionales.value = profesionales;
    console.log(`✅ Cargados ${municipioProfesionales.value.length} profesionales`);
    
  } catch (error) {
    console.error('❌ Error cargando profesionales para el municipio:', error);
    municipioProfesionales.value = [];
  }
};

// ========================================================================================
// 6. FUNCIÓN CORREGIDA: loadArchivosPostForMunicipio
// ========================================================================================
const loadArchivosPostForMunicipio = async (municipioId: number) => {
  try {
    archivosPostLoading.value = true;
    archivosPostError.value = null;
    
    console.log(`Cargando archivos de postoperación para municipio ${municipioId}`);
    
    // ✅ USAR API EN LUGAR DE FETCH MANUAL
    const response = await api.get('/postoperacion/archivos/por_municipio/', {
      params: { municipio_id: municipioId }
    });
    
    let archivos = [];
    if (response && Array.isArray(response)) {
      archivos = response;
    } else if (response.results && Array.isArray(response.results)) {
      archivos = response.results;
    }
    
    municipioArchivosPost.value = archivos;
    console.log(`✅ Cargados ${municipioArchivosPost.value.length} archivos de postoperación`);
    
  } catch (error) {
    if (error.response?.status === 404) {
      municipioArchivosPost.value = [];
    } else {
      console.error('❌ Error cargando archivos de postoperación:', error);
      archivosPostError.value = error.message || 'Error al cargar archivos de postoperación. Intente nuevamente.';
      municipioArchivosPost.value = [];
    }
  } finally {
    archivosPostLoading.value = false;
  }
};

// ========================================================================================
// 7. FUNCIÓN CORREGIDA: cargarConceptos
// ========================================================================================
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

// ========================================================================================
// 8. FUNCIÓN CORREGIDA: descargarInsumos
// ========================================================================================
const descargarInsumos = async (municipio: any) => {
  try {
    descargandoInsumos.value[municipio.cod_municipio] = true;
    
    showNotification(`Generando reporte de insumos para ${municipio.nom_municipio}...`, 'info');
    
    // ✅ USAR API EN LUGAR DE FETCH MANUAL
    const response = await api.post('/preoperacion/generar-reportes/', {
      municipios: [municipio.cod_municipio],
      generar_individuales: true
    }, {
      responseType: 'blob'
    });
    
    // Crear enlace de descarga
    const blob = new Blob([response]);
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
    console.error('❌ Error generando reporte de insumos:', error);
    showNotification(
      `Error al generar reporte de insumos de ${municipio.nom_municipio}`, 
      'error'
    );
  } finally {
    descargandoInsumos.value[municipio.cod_municipio] = false;
  }
};


// Función para ver detalle completo de un insumo (REEMPLAZA LA EXISTENTE viewInsumoDetails)
const viewInsumoDetails = (insumo) => {
  console.log('🔍 ViewInsumoDetails llamada con:', insumo);
  
  if (!insumo) {
    console.error('❌ No se proporcionó insumo');
    showNotification('Error: No se pudo cargar el detalle del insumo', 'error');
    return;
  }
  
  console.log('✅ Mostrando modal para insumo:', insumo.cod_insumo);
  
  // Asegurar que se actualice correctamente
  modalDetalleInsumo.value.insumo = insumo;
  modalDetalleInsumo.value.mostrar = true;
  
  // Forzar actualización del DOM
  nextTick(() => {
    console.log('📱 Modal estado después de nextTick:', modalDetalleInsumo.value.mostrar);
  });
};

// Función para ver detalle completo de un detalle específico


// Función para obtener detalles de un insumo específico para el modal


// Función para obtener conceptos de un detalle específico
const getConceptosDelDetalle = (codDetalle) => {
  return municipioConceptos.value.filter(c => c.cod_detalle === codDetalle);
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



// ========================================================================================
// 9. FUNCIÓN CORREGIDA: verDocumentoPDF
// ========================================================================================
// Función para ver PDF de concepto (igual que en EstadoProducto.vue)
const verDocumentoPDF = async (rutaPdf) => {
  if (!rutaPdf) {
    showNotification('No hay ruta PDF disponible', 'warning');
    return;
  }
  
  try {
    console.log('🔍 Abriendo PDF:', rutaPdf);
    
    // Usar la API de visualización de PDF con token automático
    const response = await api.get('/preoperacion/ver_pdf/', {
      params: { ruta: rutaPdf },
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
      showNotification('El archivo PDF no se encontró en el servidor.', 'error');
    } else if (error.response?.status === 403) {
      showNotification('No tiene permisos para acceder a este archivo.', 'error');
    } else {
      showNotification('Error al abrir el archivo PDF. Por favor, inténtelo de nuevo.', 'error');
    }
  }
};

// ========================================================================================
// 10. FUNCIÓN CORREGIDA PARA PDFs: verDocumentoPDFMejorado (alternativa)
// ========================================================================================
const verDocumentoPDFMejorado = async (rutaPDF: string) => {
  if (!rutaPDF) {
    showNotification('No hay ruta PDF disponible', 'warning');
    return;
  }
  
  try {
    // ✅ USAR API PARA MEJOR MANEJO DE AUTENTICACIÓN
    const response = await api.get('/preoperacion/ver_pdf/', {
      params: { ruta: rutaPDF },
      responseType: 'blob'
    });
    
    const blob = new Blob([response], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    
    window.open(url, '_blank');
    
    // Limpiar después de un tiempo
    setTimeout(() => {
      window.URL.revokeObjectURL(url);
    }, 1000);
    
  } catch (error) {
    console.error('❌ Error al abrir PDF:', error);
    showNotification('Error al abrir el documento PDF', 'error');
  }
};

// ========================================================================================
// 11. FUNCIÓN CORREGIDA: loadArchivosPreForMunicipio (si existe)
// ========================================================================================
const loadArchivosPreForMunicipio = async (municipioId: number) => {
  try {
    archivosPreLoading.value = true;
    archivosPreError.value = null;
    
    console.log(`Cargando archivos de preoperación para municipio ${municipioId}`);
    
    // ✅ USAR API EN LUGAR DE FETCH MANUAL
    const response = await api.get('/preoperacion/archivos/por_municipio/', {
      params: { municipio_id: municipioId }
    });
    
    let archivos = [];
    if (response && Array.isArray(response)) {
      archivos = response;
    } else if (response.results && Array.isArray(response.results)) {
      archivos = response.results;
    }
    
    municipioArchivos.value = archivos;
    console.log(`✅ Cargados ${municipioArchivos.value.length} archivos de preoperación`);
    
  } catch (error) {
    if (error.response?.status === 404) {
      municipioArchivos.value = [];
    } else {
      console.error('❌ Error cargando archivos de preoperación:', error);
      archivosPreError.value = error.message || 'Error al cargar archivos de preoperación. Intente nuevamente.';
      municipioArchivos.value = [];
    }
  } finally {
    archivosPreLoading.value = false;
  }
};






    // **COMPUTED PROPERTIES CORREGIDAS**
    
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
    const filteredDetalles = computed(() => {
      let result = [...municipioDetalles.value];
      
      if (detalleSearch.value.trim()) {
        const search = detalleSearch.value.toLowerCase();
        result = result.filter(d => 
          d.cod_detalle.toString().includes(search) ||
          (d.escala?.toLowerCase().includes(search) || '') ||
          (d.estado?.toLowerCase().includes(search) || '') ||
          (d.observacion?.toLowerCase().includes(search) || '')
        );
      }
      
      return result;
    });
    
    // ✅ FILTROS PARA ARCHIVOS DE PREOPERACIÓN
    const filteredArchivosPre = computed(() => {
      let result = [...municipioArchivos.value];
      
      if (filtroClasificacionPre.value) {
        result = result.filter(a => {
          const nombreClasificacion = getNombreClasificacion(a.cod_insumo);
          return nombreClasificacion === filtroClasificacionPre.value;
        });
      }
      
      if (filtroNombreArchivoPre.value.trim()) {
        const search = filtroNombreArchivoPre.value.toLowerCase();
        result = result.filter(a => 
          a.nombre_insumo?.toLowerCase().includes(search)
        );
      }
      
      return result;
    });

    // ✅ FILTROS PARA ARCHIVOS DE POSTOPERACIÓN
    const filteredArchivosPost = computed(() => {
      let result = [...municipioArchivosPost.value];
      
      if (filtroComponentePost.value) {
        result = result.filter(a => 
          a.disposicion_info?.componente === filtroComponentePost.value
        );
      }
      
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
      if (!conceptoSearch.value.trim()) {
        return municipioConceptos.value;
      }
      
      const search = conceptoSearch.value.toLowerCase();
      return municipioConceptos.value.filter(c => 
        (c.concepto && c.concepto.toLowerCase().includes(search)) ||
        (c.detalle_concepto && c.detalle_concepto.toLowerCase().includes(search)) ||
        (c.observacion && c.observacion.toLowerCase().includes(search)) ||
        (c.evaluacion && c.evaluacion.toLowerCase().includes(search))
      );
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
    
    const handleFilter = () => {
      currentPage.value = 1;
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
    
    const getClasificaciones = (insumoId: number): any[] => {
      return municipioClasificaciones.value.filter(c => c.cod_insumo === insumoId);
    };
    
    const getClasificacionesCount = (insumoId: number): number => {
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

    // **FUNCIONES DE SELECCIÓN**

    // ✅ FUNCIÓN PARA VERIFICAR ACCESO ANTES DE SELECCIONAR MUNICIPIO
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
    
    const clearSelectedMunicipio = () => {
      selectedMunicipioId.value = null;
      selectedMunicipio.value = null;
      
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




// 🔧 CORRECCIÓN ESPECÍFICA PARA downloadArchivoPost EN InsumosList.vue

// ========================================================================================
// REEMPLAZAR LA FUNCIÓN downloadArchivoPost COMPLETAMENTE:
// ========================================================================================

const downloadArchivoPost = async (archivo: any) => {
  if (!archivo.ruta_completa) {
    showNotification('No hay ruta disponible para descargar este archivo', 'warning');
    return;
  }
  
  try {
    const nombreArchivo = obtenerNombreArchivo(archivo.ruta_completa);
    const extension = getFileExtension(nombreArchivo);
    
    console.log('⬇️ Descargando archivo POST:', {
      archivo: nombreArchivo,
      extension: extension,
      ruta: archivo.ruta_completa
    });
    
    // ✅ LÓGICA CORREGIDA: Usar endpoint específico según tipo de archivo
    let endpoint;
    let params = { ruta: archivo.ruta_completa };
    
    if (extension === 'pdf') {
      // 🔧 PARA PDFs: usar ver_pdf con download=true
      endpoint = '/preoperacion/ver_pdf/';
      params.download = 'true'; // ← Parámetro clave para forzar descarga
    } else {
      // 🔧 PARA OTROS ARCHIVOS: usar descargar_archivo
      endpoint = '/preoperacion/descargar_archivo/';
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
    showNotification(`Descargando: ${nombreArchivo}`, 'success');
    
  } catch (error) {
    console.error('❌ Error al descargar archivo POST:', error);
    showNotification(`Error al descargar archivo: ${error.message}`, 'error');
  }
};

// ========================================================================================
// TAMBIÉN CORREGIR downloadArchivo (para preoperación) SI NO ESTÁ YA CORREGIDO:
// ========================================================================================

const downloadArchivo = async (archivo: any) => {
  if (!archivo.path_file) {
    showNotification('No hay ruta disponible para descargar este archivo', 'warning');
    return;
  }
  
  try {
    const nombreArchivo = obtenerNombreArchivo(archivo.path_file);
    const extension = getFileExtension(nombreArchivo);
    
    console.log('⬇️ Descargando archivo PRE:', {
      archivo: nombreArchivo,
      extension: extension,
      ruta: archivo.path_file
    });
    
    // ✅ LÓGICA CORREGIDA: Usar endpoint específico según tipo de archivo
    let endpoint;
    let params = { ruta: archivo.path_file };
    
    if (extension === 'pdf') {
      // 🔧 PARA PDFs: usar ver_pdf con download=true
      endpoint = '/preoperacion/ver_pdf/';
      params.download = 'true'; // ← Parámetro clave para forzar descarga
    } else {
      // 🔧 PARA OTROS ARCHIVOS: usar descargar_archivo
      endpoint = '/preoperacion/descargar_archivo/';
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
    showNotification(`Descargando: ${nombreArchivo}`, 'success');
    
  } catch (error) {
    console.error('❌ Error al descargar archivo PRE:', error);
    showNotification(`Error al descargar archivo: ${error.message}`, 'error');
  }
};

// ========================================================================================
// ASEGURARSE DE QUE EXISTAN LAS FUNCIONES AUXILIARES:
// ========================================================================================

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

    const getArchivoExtraInfo = (archivo: any, type: 'pre' | 'post') => {
      const info: any = {
        municipio: selectedMunicipio.value?.nom_municipio || 'No disponible',
        departamento: getNombreDepartamento(selectedMunicipio.value?.cod_depto) || 'No disponible',
        fecha_disposicion: archivo.fecha_disposicion ? formatDate(archivo.fecha_disposicion) : 'No disponible',
        observacion: archivo.observacion || 'Sin observaciones'
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



    // **FUNCIONES ADICIONALES**

    const editMunicipio = (municipio: any) => {
      showNotification(`Editar municipio ${municipio.nom_municipio}`, 'info');
    };

    const showCreateInsumoForMunicipio = (municipioId: number) => {
      showNotification(`Crear nuevo insumo para municipio ${municipioId}`, 'info');
    };

    const createDetalle = () => {
      if (!selectedMunicipioId.value) {
        showNotification('Debe seleccionar un municipio primero', 'error');
        return;
      }
      
      if (!selectedMunicipio.value) {
        showNotification('Error: No se pudo obtener la información del municipio', 'error');
        return;
      }
      
      // Redirigir al formulario de crear detalle con municipio y departamento preseleccionados
      router.push({
        name: 'CrearDetalle',
        query: {
          municipio: selectedMunicipio.value.cod_municipio,
          departamento: selectedMunicipio.value.cod_depto
        }
      });
    };


    const editDetalle = (detalle: any) => {
      showNotification(`Editar detalle ${detalle.cod_detalle}`, 'info');
    };

    const viewDetalleDetails = (detalle) => {
      modalDetalleDetalle.value.detalle = detalle;
      modalDetalleDetalle.value.mostrar = true;
    };

    const showDeleteDetalleModal = (detalle: any) => {
      showNotification(`Eliminar detalle ${detalle.cod_detalle}`, 'warning');
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

    // **INICIALIZACIÓN**

    onMounted(async () => {
      await loadInitialData();
      
      const municipioIdFromRoute = route.query.municipio?.toString();
      if (municipioIdFromRoute) {
        selectMunicipio(parseInt(municipioIdFromRoute));
      }
    });


 








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



const showDetalleModal = (detalle) => {
  console.log('Mostrando detalle:', detalle);
  detalleSeleccionado.value = detalle;
  detalleModalVisible.value = true;
};

// 🔥 AGREGAR ESTAS FUNCIONES AUXILIARES SI NO EXISTEN
const getEstadoClass = (estado) => {
  if (!estado) return '';
  
  const estadoLower = estado.toLowerCase();
  if (estadoLower.includes('oficializado') || estadoLower.includes('aprobado')) return 'estado-oficializado';
  if (estadoLower.includes('produccion') || estadoLower.includes('proceso')) return 'estado-produccion';
  if (estadoLower.includes('pendiente')) return 'estado-pendiente';
  if (estadoLower.includes('rechazado')) return 'estado-rechazado';
  return 'estado-default';
};

// Función para obtener detalles de un insumo específico para el modal
const getDetallesForInsumoModal = (insumoId) => {
  const clasificacionesIds = getClasificaciones(insumoId).map(c => c.cod_clasificacion);
  return municipioDetalles.value.filter(d => clasificacionesIds.includes(d.cod_clasificacion));
};

// Función para contar conceptos de un insumo
const getConceptosCountForInsumo = (insumoId) => {
  // Esta es una implementación básica - ajusta según tu lógica
  return 0; // O la lógica que tengas para contar conceptos
};

// Función para contar archivos de un insumo
const getArchivosCountForInsumo = (insumoId) => {
  // Esta es una implementación básica - ajusta según tu lógica
  const clasificaciones = getClasificaciones(insumoId);
  return clasificaciones.length * 2; // Estimación: 2 archivos por clasificación
};

// Funciones para el modal de insumo
const verDetalleCompleto = (detalle) => {
  // Cerrar modal de insumo y abrir modal de detalle
  modalDetalleInsumo.value.mostrar = false;
  showDetalleModal(detalle);
};

const verDetallesDeClasificacion = (clasificacion) => {
  // Cambiar a la pestaña de detalles
  activeTab.value = 'detalles';
  modalDetalleInsumo.value.mostrar = false;
};

const verTodosLosDetalles = (insumo) => {
  modalDetalleInsumo.value.mostrar = false;
  activeTab.value = 'detalles';
};

const irAVistaCompleta = (insumo) => {
  // Redirigir a página específica del insumo si existe
  console.log('Ir a vista completa de insumo:', insumo);
  modalDetalleInsumo.value.mostrar = false;
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
      filteredArchivosPre,
      
      // ✅ FILTROS ESPECÍFICOS PARA ARCHIVOS
      filtroClasificacionPre,
      filtroNombreArchivoPre,
      filtroComponentePost,
      filtroNombreArchivoPost,
      clasificacionesUnicasPre,
      componentesUnicosPost,
      
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
      createDetalle,
      editDetalle,
      showDeleteDetalleModal,
      
      // Métodos adicionales
      descargarInsumos,
      exportarDatos,
      refreshData,
      showNotification,
      closeNotification,
      
      // Control de permisos
      tieneAccesoAMunicipio,
      obtenerNombreArchivo,
      verDocumentoPDFMejorado,
      loadArchivosPreForMunicipio,

      modalDetalleInsumo,
      modalDetalleDetalle,
      verDetalleCompleto,
      verDetallesDeClasificacion,
      getDetallesForInsumoModal,
      getConceptosDelDetalle,
      getConceptosCountForInsumo,
      getArchivosCountForInsumo,
      getEstadoClass,
      verTodosLosDetalles,
      irAVistaCompleta,


        detalleModalVisible,
        detalleSeleccionado, 
        showDetalleModal,
        

    }
  }
});
</script>

<style scoped>

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999; /* ← ASEGURAR QUE SEA MUY ALTO */
  backdrop-filter: blur(8px);
  animation: modalBackdropFadeIn 0.3s ease;
}

.modal-content {
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 24px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(10px);
  animation: modalSlideIn 0.3s ease;
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

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
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

.data-table th,
.data-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #dee2e6;
  font-size: 0.9rem; /* Esto equivale aproximadamente a 14px */
}

/* Si quieres que los encabezados sean un poco más grandes que el contenido */
.data-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
  white-space: nowrap;
  font-size: 1.0rem; /* Encabezados ligeramente más grandes */
}

/* Alternativa: Si solo quieres reducir el contenido de las celdas, mantén los encabezados */
.data-table td {
  font-size: 0.9rem; /* Solo las celdas de datos, no los encabezados */
}

.btn-action.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-action.btn-success:hover:not(:disabled) {
  background-color: #218838;
}

.btn-action:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.archivos-inner-tabs .inner-tab {
  position: relative;
  padding-right: 2.5rem;
}

.archivos-inner-tabs .inner-tab::after {
  content: attr(data-count);

}

.archivos-inner-tabs .inner-tab.active::after {
  background-color: #0d6efd;
  color: white;
}


/* Estilos generales */
.insumos-list-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Cabecera de página */
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

/* Paneles y filtros */
.filters-panel {
  background-color: white;
  border-radius: 8px;
  padding: 1.25rem 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.search-filters-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.global-search {
  position: relative;
}

.global-search i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

.global-search input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
}

.global-search input:focus {
  border-color: #4dabf7;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
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
  display: flex;
  align-items: center;
  justify-content: center;
}

.filters-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 200px;
  flex: 1;
}

.filter-item label {
  font-size: 0.875rem;
  color: #495057;
  font-weight: 500;
}

.filter-item select {
  padding: 0.5rem 1rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background-color: white;
  font-size: 0.95rem;
}

.filter-actions {
  display: flex;
  gap: 0.75rem;
  margin-left: auto;
}

.clear-filters-btn,
.refresh-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.clear-filters-btn {
  background-color: #f8f9fa;
  color: #6c757d;
  border: 1px solid #ced4da;
}

.clear-filters-btn:hover {
  background-color: #e9ecef;
}

.refresh-btn {
  background-color: #6c757d;
  color: white;
}

.refresh-btn:hover {
  background-color: #5a6268;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Estilos para archivos */
.archivos-inner-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #dee2e6;
  background-color: #f8f9fa;
  border-radius: 8px 8px 0 0;
  overflow: hidden;
}

.inner-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  background-color: transparent;
  color: #495057;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  position: relative;
  font-weight: 500;
}

.inner-tab:hover {
  background-color: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
}

.inner-tab.active {
  color: #0d6efd;
  background-color: white;
  border-bottom: 3px solid #0d6efd;
}

.inner-tab.active:after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 3px;
  background-color: #0d6efd;
}

.inner-tab i {
  font-size: 1.2rem;
}

.archivos-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.25rem;
  padding: 0.5rem;
}

.archivo-card {
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s, box-shadow 0.2s;
  background-color: white;
  height: 100%;
}

.archivo-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.12);
}

.archivo-header {
  display: flex;
  padding: 1.25rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  align-items: center;
}

.archivo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 8px;
  margin-right: 1rem;
  background-color: rgba(13, 110, 253, 0.1);
}

.archivo-icon i {
  font-size: 1.75rem;
  color: #0d6efd;
}

.archivo-title {
  flex: 1;
  overflow: hidden;
}

.archivo-title h4 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #212529;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.archivo-fecha {
  font-size: 0.85rem;
  color: #6c757d;
}

.archivo-body {
  flex: 1;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.detail-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #6c757d;
  min-width: 100px;
}

.detail-value {
  flex: 1;
  font-size: 0.9rem;
  color: #212529;
  word-break: break-word;
}

.path-value {
  font-family: 'Consolas', monospace;
  font-size: 0.85rem;
  background-color: #f8f9fa;
  padding: 0.5rem;
  border-radius: 4px;
  max-height: 80px;
  overflow-y: auto;
}

.archivo-footer {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 1rem 1.25rem;
  background-color: #f8f9fa;
  border-top: 1px solid #dee2e6;
}

.btn-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  color: #0d6efd;
  font-size: 0.9rem;
  font-weight: 500;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-text:hover {
  background-color: rgba(13, 110, 253, 0.1);
}

.btn-text i {
  font-size: 1.1rem;
}

/* Estilos para el estado vacío */
.empty-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 3rem 1rem;
  color: #6c757d;
}

.empty-message i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #adb5bd;
}

/* Estilos para estados de carga y error */
.loading-state, 
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
}

.loading-state .spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(13, 110, 253, 0.2);
  border-top: 3px solid #0d6efd;
  border-radius: 50%;
  margin-bottom: 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state i {
  font-size: 3rem;
  color: #dc3545;
  margin-bottom: 1rem;
}

/* Estilos específicos para cada tipo de archivo */
.archivo-icon i.material-icons-pdf {
  color: #dc3545;
}

.archivo-icon i.material-icons-doc {
  color: #0d6efd;
}

.archivo-icon i.material-icons-xls {
  color: #198754;
}

.archivo-icon i.material-icons-img {
  color: #fd7e14;
}

.archivo-icon i.material-icons-zip {
  color: #6f42c1;
}

.archivo-icon i.material-icons-shp {
  color: #20c997;
}

/* Botones */
.btn-primary,
.btn-secondary,
.btn-outline,
.btn-danger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.1s;
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
  background-color: #5a6268;
}

.btn-outline {
  background-color: transparent;
  border: 1px solid #ced4da;
  color: #495057;
}

.btn-outline:hover {
  background-color: #f8f9fa;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover {
  background-color: #bb2d3b;
}

.btn-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  color: #0d6efd;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
}

.btn-text:hover {
  background-color: rgba(13, 110, 253, 0.1);
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 4px;
  border: none;
  background-color: #f8f9fa;
  color: #495057;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-icon:hover {
  background-color: #e9ecef;
}

.btn-icon.primary {
  background-color: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
}

.btn-icon.primary:hover {
  background-color: rgba(13, 110, 253, 0.2);
}

.btn-icon.warning {
  background-color: rgba(255, 193, 7, 0.1);
  color: #ffc107;
}

.btn-icon.warning:hover {
  background-color: rgba(255, 193, 7, 0.2);
}

.btn-icon.success {
  background-color: rgba(25, 135, 84, 0.1);
  color: #198754;
}

.btn-icon.success:hover {
  background-color: rgba(25, 135, 84, 0.2);
}

.btn-icon.danger {
  background-color: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

.btn-icon.danger:hover {
  background-color: rgba(220, 53, 69, 0.2);
}

.btn-icon.small {
  width: 32px;
  height: 32px;
}

.btn-icon.small i {
  font-size: 1.2rem;
}

/* Estados de carga y errores */
.loading-indicator,
.error-message,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #0d6efd;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message i,
.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-message i {
  color: #dc3545;
}

.empty-state i {
  color: #6c757d;
}

.error-message p,
.empty-state p {
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
  color: #6c757d;
}

/* Tablas */
.municipios-table-container,
.detalles-table-container {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #dee2e6;
}

.data-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
  white-space: nowrap;
}

.data-table tbody tr:hover {
  background-color: #f8f9fa;
}

.data-table .text-center {
  text-align: center;
}

.data-table .badge {
  display: inline-block;
  padding: 0.35em 0.65em;
  font-size: 0.75em;
  font-weight: 700;
  line-height: 1;
  color: #fff;
  text-align: center;
  white-space: nowrap;
  vertical-align: baseline;
  border-radius: 0.375rem;
}

.badge-primary {
  background-color: #0d6efd;
}

.badge-secondary {
  background-color: #6c757d;
}

.badge-success {
  background-color: #198754;
}

.badge-danger {
  background-color: #dc3545;
}

.badge-warning {
  background-color: #ffc107;
  color: #212529;
}

.badge-info {
  background-color: #0dcaf0;
  color: #212529;
}

.row-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
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
  gap: 1.5rem;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.detail-header {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.95rem;
  font-weight: 500;
}

.back-button:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.detail-header h2 {
  margin: 0 0 0 1rem;
  font-size: 1.5rem;
  color: #343a40;
}

.detail-actions {
  margin-left: auto;
  display: flex;
  gap: 0.75rem;
}

.detail-tabs {
  display: flex;
  border-bottom: 1px solid #dee2e6;
  background-color: #f8f9fa;
}

.tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;
  border-bottom: 3px solid transparent;
  font-weight: 500;
  color: #6c757d;
}

.tab:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.tab.active {
  color: #0d6efd;
  border-bottom-color: #0d6efd;
}

.tab i {
  font-size: 1.2rem;
}

.tab-content {
  padding: 1.5rem;
}

/* Contenido de pestaña Resumen */
.info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

/* Código específico para arreglar las tarjetas */
.info-card {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
  background-color: white;
  height: auto;
  display: flex;
  flex-direction: column;
}

.info-card h3 {
  margin: 0;
  padding: 0.75rem 1rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  font-size: 1rem;
  color: #343a40;
  font-weight: 600;
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
  border-bottom: 1px solid #f5f5f5;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label, .info-value {
  display: table-cell;
  padding: 0.5rem 1rem;
  vertical-align: middle;
  line-height: 1.3;
}

.info-label {
  width: 40%;
  font-size: 0.875rem;
  color: #6c757d;
  font-weight: 500;
  background-color: #f9f9f9;
  border-right: 1px solid #f0f0f0;
}

.info-value {
  width: 60%;
  font-size: 0.9rem;
  color: #212529;
}

.stats-container {
  padding: 1rem;
  display: flex;
  justify-content: space-around;
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  transition: transform 0.2s;
  flex: 1;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.05);
}

.stat-value {
  font-size: 2rem;
  font-weight: 600;
  color: #0d6efd;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #6c757d;
  font-weight: 500;
}
/* Estilos para la tarjeta de categorías */
.category-container {
  padding: 1rem;
}

.category-bars {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.category-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0;
}

.bar-label {
  width: 140px;
  font-size: 0.85rem;
  color: #495057;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bar-label a {
  color: #495057;
  text-decoration: none;
  transition: color 0.2s;
}

.bar-label a:hover {
  color: #0d6efd;
  text-decoration: underline;
}

.bar-container {
  flex: 1;
  height: 8px;
  background-color: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.bar-value {
  height: 100%;
  background-color: #0d6efd;
  border-radius: 4px;
}

.bar-count {
  min-width: 24px;
  text-align: right;
  font-size: 0.85rem;
  color: #495057;
  font-weight: 500;
}

.insumos-by-category {
  margin-top: 1rem;
  border-top: 1px solid #dee2e6;
  padding-top: 1rem;
}

.insumos-by-category h4 {
  margin: 0 0 0.75rem;
  font-size: 1rem;
  color: #343a40;
  font-weight: 600;
}

.category-bars {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.category-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.bar-label {
  width: 140px;
  font-size: 0.85rem;
  color: #495057;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bar-container {
  flex: 1;
  height: 8px;
  background-color: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.bar-value {
  height: 100%;
  background-color: #0d6efd;
  border-radius: 4px;
}

.bar-count {
  min-width: 24px;
  text-align: right;
  font-size: 0.85rem;
  color: #495057;
  font-weight: 500;
}

.profesionales-list {
  padding: 0.75rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 0.75rem;
}

.profesional-card {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  align-items: center;
  border: 1px solid #f0f0f0;
}

.profesional-avatar {
  width: 36px;
  height: 36px;
  background-color: #0d6efd;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profesional-info {
  flex: 1;
}

.profesional-name {
  font-weight: 500;
  color: #343a40;
  margin-bottom: 0.15rem;
  font-size: 0.9rem;
}

.profesional-role {
  color: #6c757d;
  font-size: 0.8rem;
  margin-bottom: 0.25rem;
}

.profesional-email {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #6c757d;
}

.profesional-email i {
  font-size: 0.9rem;
}

.empty-message {
  padding: 1.5rem;
  text-align: center;
  color: #6c757d;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin: 0.75rem;
}

/* Contenido de pestaña Insumos */
.tab-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.search-box {
  position: relative;
  min-width: 250px;
}

.search-box i {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

.search-box input {
  width: 100%;
  padding: 0.5rem 0.5rem 0.5rem 2.25rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
}

.insumos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.insumo-card {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.insumo-header {
  display: flex;
  padding: 1rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  align-items: center;
}

.insumo-icon {
  width: 40px;
  height: 40px;
  background-color: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
}

.insumo-title {
  flex: 1;
}

.insumo-title h4 {
  margin: 0 0 0.25rem;
  font-size: 1rem;
  color: #343a40;
}

.categoria-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  background-color: #e9ecef;
  color: #495057;
  border-radius: 4px;
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
  width: 120px;
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 500;
}

.detail-value {
  flex: 1;
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
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.clasificacion-card {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
}

.clasificacion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.clasificacion-header h4 {
  margin: 0;
  font-size: 1.1rem;
  color: #343a40;
}

.clasificacion-actions {
  display: flex;
  gap: 0.5rem;
}

.clasificacion-body {
  padding: 1rem;
}

.clasificacion-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid #dee2e6;
  text-align: right;
}

/* Archivos */
.archivos-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.archivo-card {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
}

.archivo-header {
  display: flex;
  padding: 1rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  align-items: center;
}

.archivo-icon {
  width: 40px;
  height: 40px;
  background-color: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
}

.archivo-title {
  flex: 1;
}

.archivo-title h4 {
  margin: 0 0 0.25rem;
  font-size: 1rem;
  color: #343a40;
  word-break: break-word;
}

.archivo-fecha {
  font-size: 0.85rem;
  color: #6c757d;
}

.archivo-actions {
  display: flex;
  gap: 0.5rem;
  margin-left: 0.5rem;
}

.archivo-body {
  padding: 1rem;
}

.archivo-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid #dee2e6;
  text-align: right;
}

/* Modales */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 700px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.delete-modal {
  max-width: 500px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #dee2e6;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #343a40;
}

.close-btn {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  max-height: calc(90vh - 132px);
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #dee2e6;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.delete-warning {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.delete-warning i {
  font-size: 3rem;
  color: #ffc107;
  margin-bottom: 1rem;
}

.delete-warning p {
  margin-bottom: 0.5rem;
  color: #495057;
}

/* Formularios */
.form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 250px;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-group label {
  font-size: 0.95rem;
  color: #495057;
  font-weight: 500;
}

.form-group .required {
  color: #dc3545;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.5rem 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.95rem;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #4dabf7;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
  outline: none;
}

.form-hint {
  font-size: 0.8rem;
  color: #6c757d;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

/* Notificaciones */
.notification {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  min-width: 300px;
  max-width: 400px;
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

/* Estilos para la tabla de conceptos */
.concepto-table {
  width: 100%;
  border-collapse: collapse;
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

/* Estilos para badges de evaluación */
.evaluacion-badge {
  display: inline-block;
  padding: 0.35em 0.65em;
  font-size: 0.75em;
  font-weight: 700;
  line-height: 1;
  color: #fff;
  text-align: center;
  white-space: nowrap;
  vertical-align: baseline;
  border-radius: 0.375rem;
}

.evaluacion-badge.success {
  background-color: #198754;
}

.evaluacion-badge.danger {
  background-color: #dc3545;
}

.evaluacion-badge.warning {
  background-color: #ffc107;
  color: #212529;
}

.evaluacion-badge.info {
  background-color: #0dcaf0;
  color: #212529;
}

.evaluacion-badge.default {
  background-color: #6c757d;
}

/* Add these styles to enhance category badges */
.categoria-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  border-radius: 4px;
  font-weight: 500;
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

.clasificacion-nombre {
  font-size: 1.1rem;
  font-weight: 600;
  color: #343a40;
  margin: 0 0 0.25rem;
}

.insumo-code {
  font-size: 0.85rem;
  color: #6c757d;
}

.bar-label a {
  color: #495057;
  text-decoration: none;
  transition: color 0.2s;
}

.bar-label a:hover {
  color: #0d6efd;
  text-decoration: underline;
}

.pdf-viewer-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.85);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.pdf-viewer-container {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 1200px;
  height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.2);
}

.pdf-viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #dee2e6;
  background-color: #f8f9fa;
  border-radius: 8px 8px 0 0;
}

.pdf-viewer-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #343a40;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 75%;
}

.pdf-iframe-container {
  flex: 1;
  overflow: hidden;
}

.pdf-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.pdf-loading,
.pdf-error {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.pdf-loading .spinner {
  width: 60px;
  height: 60px;
  margin-bottom: 1.5rem;
}

.pdf-error i {
  font-size: 4rem;
  color: #dc3545;
  margin-bottom: 1.5rem;
}

.pdf-error p {
  margin-bottom: 1.5rem;
  color: #495057;
  max-width: 600px;
}

/* Estilos para los filtros adicionales */
.archivos-filters {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.view-toggle {
  display: flex;
  gap: 0.5rem;
  margin-right: 1rem;
  align-self: flex-start;
  margin-bottom: 0.5rem;
}

.view-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 4px;
  border: 1px solid #ced4da;
  background-color: white;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.2s;
}

.view-toggle-btn:hover {
  background-color: #e9ecef;
}

.view-toggle-btn.active {
  background-color: #0d6efd;
  border-color: #0d6efd;
  color: white;
}

/* Estilos para la vista de tabla */
.file-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.file-icon {
  font-size: 1.25rem;
  color: #6c757d;
}

/* Estilos responsivos para vista móvil */
@media (max-width: 1200px) {
    .modal-detalle-insumo {
    max-width: 95%;
    margin: 0 2.5%;
  }
  .info-cards {
    grid-template-columns: 1fr;
  }
  
  .clasificaciones-list-detailed {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 992px) {
  .insumos-grid, 
  .archivos-list {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .detail-header {
    flex-wrap: wrap;
  }
  
  .detail-actions {
    margin-left: 0;
    width: 100%;
    margin-top: 1rem;
  }
}

@media (max-width: 768px) {
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
  
  .archivo-footer {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .archivo-footer .btn-text {
    justify-content: center;
  }
  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-actions {
    margin-left: 0;
    margin-top: 1rem;
  }
  
  .detail-tabs {
    overflow-x: auto;
  }
  
  .tab {
    white-space: nowrap;
    padding: 0.75rem 0.75rem;
  }
  
  .notification {
    min-width: auto;
    max-width: 90%;
    left: 5%;
    right: 5%;
  }
  
  .pdf-viewer-container {
    width: 95%;
    height: 90vh;
  }
  
  .pdf-viewer-header h3 {
    max-width: 90%;
    font-size: 1rem;
  }
}
/* Ajustes de diseño responsivo */
@media (max-width: 768px) {
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
  .stats-container {
    flex-direction: column;
  }
  
  .stat-item {
    padding: 0.75rem;
  }
  
  .stat-value {
    font-size: 1.75rem;
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
    padding: 0.5rem 0.75rem;
    font-size: 0.9rem;
  }
  
  .modal-container {
    max-width: 95%;
    margin: 0 2.5%;
  }
}

/* Mejoras para los filtros de archivos */
.filter-item {
  flex: 1;
  min-width: 200px;
}

.filter-item label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: #495057;
  font-weight: 500;
}

.filter-item select,
.filter-item input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.95rem;
}

.filter-item .search-box {
  position: relative;
}

.filter-item .search-box i {
  position: absolute;
  left: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
  font-size: 1.1rem;
}

.filter-item .search-box input {
  padding-left: 2.25rem;
}

.filter-item .search-box .clear-btn {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Mejoras para la tabla */
.table-responsive {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

/* Mejoras para las rutas en la tabla */
.path-value {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}

.path-value:hover {
  white-space: normal;
  word-break: break-all;
}

/* Indicador de tipo de archivo en la lista de archivos */
.file-info .file-icon.pdf {
  color: #dc3545;
}

.file-info .file-icon.doc {
  color: #0d6efd;
}

.file-info .file-icon.xls {
  color: #198754;
}

.file-info .file-icon.img {
  color: #fd7e14;
}

.file-info .file-icon.zip {
  color: #6f42c1;
}

.file-info .file-icon.shp {
  color: #20c997;
}

/* Estilos para el modal de detalles de archivo */
.archivo-details-modal {
  max-width: 800px;
  max-height: 85vh;
}

.archivo-details-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.details-section {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
  background-color: white;
}

.details-section h3 {
  margin: 0;
  padding: 0.75rem 1rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  font-size: 1rem;
  color: #343a40;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.details-section h3 i {
  font-size: 1.2rem;
  color: #0d6efd;
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
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f5f5f5;
  border-right: 1px solid #f5f5f5;
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
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.detail-value {
  font-size: 0.95rem;
  color: #212529;
  word-break: break-word;
}

.ruta-completa {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.85rem;
  background-color: #f8f9fa;
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #dee2e6;
  max-height: 120px;
  overflow-y: auto;
  word-break: break-all;
  line-height: 1.4;
}

.observaciones-content {
  padding: 1rem;
  background-color: #f8f9fa;
  margin: 0;
  font-size: 0.95rem;
  color: #495057;
  line-height: 1.5;
  white-space: pre-wrap;
}

.archivo-type-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.archivo-type-badge.pre {
  background-color: #e3f2fd;
  color: #1565c0;
}

.archivo-type-badge.post {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.status-approved {
  color: #198754;
  font-weight: 600;
}

/* Botón de información */
.btn-text.btn-info {
  color: #0dcaf0;
}

.btn-text.btn-info:hover {
  background-color: rgba(13, 202, 240, 0.1);
}

.btn-icon.info {
  background-color: rgba(13, 202, 240, 0.1);
  color: #0dcaf0;
}

.btn-icon.info:hover {
  background-color: rgba(13, 202, 240, 0.2);
}
</style>