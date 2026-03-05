<template>
  <div class="municipios-disposicion-container">
    <div class="header-section">
      <h2 class="page-title">Consulta de Municipios</h2>
      <div class="info-section">
        <div class="access-info-header">
          <div class="access-badge" :class="accessLevelClass">
            <i class="material-icons">{{ accessLevelIcon }}</i>
            <span>{{ accessLevelText }}</span>
          </div>
          <div v-if="isProfesional && municipiosPermitidos.length > 0" class="scope-info">
            Acceso a {{ municipiosPermitidos.length }} municipios asignados
          </div>
        </div>
        <div class="actions-bar">
          <button 
            class="btn btn-export" 
            @click="exportarDatos" 
            :disabled="!municipiosTabla.length"
          >
            <i class="material-icons">file_download</i>
            Exportar Resultados
          </button>
        </div>
      </div>
    </div>

    <!-- Barra de búsqueda principal -->
    <div class="search-section">
      <div class="search-input-container">
        <i class="material-icons search-icon">search</i>
        <input 
          type="text" 
          v-model="filtros.busqueda" 
          @input="busquedaInmediata"
          placeholder="Buscar por nombre o código de municipio..."
          class="search-input"
        />
        <button 
          v-if="filtros.busqueda" 
          @click="limpiarBusqueda" 
          class="clear-search-btn"
        >
          <i class="material-icons">clear</i>
        </button>
      </div>
    </div>

    <!-- Filtros jerárquicos organizados en filas CON FILTROS DINÁMICOS -->
    <div class="filtros-section">
      <!-- Primera fila de filtros - Ubicación geográfica DINÁMICA -->
      <div class="row">
        <div class="col-md-6 col-lg-4">
          <div class="form-group">
            <label for="departamento">
              Departamento:
              <span class="contador-opciones">({{ departamentosDisponibles.length }} disponibles)</span>
            </label>
            <select 
              id="departamento" 
              v-model="filtros.departamento" 
              @change="actualizarFiltrosDepartamento"
              class="form-control"
              :class="{ 'has-selection': filtros.departamento }"
            >
              <option value="">Todos los departamentos</option>
              <option v-for="depto in departamentosDisponibles" :key="depto.cod_depto" :value="depto.cod_depto">
                {{ depto.nom_depto }}
              </option>
            </select>
            <button 
              v-if="filtros.departamento" 
              @click="limpiarFiltroEspecifico('departamento')"
              class="btn-limpiar-filtro"
              title="Limpiar filtro de departamento"
            >
              ✓
            </button>
          </div>
        </div>
        
        <div class="col-md-6 col-lg-4">
          <div class="form-group">
            <label for="municipio">
              Municipio:
              <span class="contador-opciones">({{ municipiosFiltradosDinamicos.length }} disponibles)</span>
            </label>
            <select 
              id="municipio" 
              v-model="filtros.municipio" 
              @change="actualizarFiltrosMunicipio"
              class="form-control"
              :class="{ 'has-selection': filtros.municipio }"
              :disabled="cargandoFiltros"
            >
              <option value="">Todos los municipios</option>
              <option v-for="mun in municipiosDisponibles" :key="mun.cod_municipio" :value="mun.cod_municipio">
                {{ mun.nom_municipio }}
              </option>
            </select>
            <button 
              v-if="filtros.municipio" 
              @click="limpiarFiltroEspecifico('municipio')"
              class="btn-limpiar-filtro"
              title="Limpiar filtro de municipio"
            >
              ✓
            </button>
          </div>
        </div>
        
        <div class="col-md-6 col-lg-4">
          <div class="form-group">
            <label for="territorial">
              Territorial:
              <span class="contador-opciones">({{ territorialesFitradasDinamicas.length }} disponibles)</span>
            </label>
            <select 
              id="territorial" 
              v-model="filtros.territorial" 
              @change="actualizarFiltrosTerritorial"
              class="form-control"
              :class="{ 'has-selection': filtros.territorial }"
              :disabled="cargandoFiltros"
            >
              <option value="">Todas las territoriales</option>
              <option v-for="territorial in territorialesDisponibles" :key="territorial.nom_territorial" :value="territorial.nom_territorial">
                {{ territorial.nom_territorial }}
              </option>
            </select>
            <button 
              v-if="filtros.territorial" 
              @click="limpiarFiltroEspecifico('territorial')"
              class="btn-limpiar-filtro"
              title="Limpiar filtro de territorial"
            >
              ✓
            </button>
          </div>
        </div>
      </div>

      <!-- Segunda fila de filtros - Profesionales DINÁMICOS (solo para admin/super admin) -->
      <div class="row" v-if="isSuperAdmin || isAdmin">
        <div class="col-md-6 col-lg-6">
          <div class="form-group">
            <label for="rolProfesional">
              Rol del Profesional:
              <span class="contador-opciones">({{ rolesProfesionalesFiltradosDinamicos.length }} disponibles)</span>
            </label>
            <select 
              id="rolProfesional" 
              v-model="filtros.rolProfesional" 
              @change="actualizarFiltroRolProfesional"
              class="form-control"
              :class="{ 'has-selection': filtros.rolProfesional }"
              :disabled="cargandoFiltros"
            >
              <option value="">Todos los roles</option>
              <option v-for="rol in rolesDisponibles" :key="rol.codigo" :value="rol.codigo">
                {{ rol.nombre }}
              </option>
            </select>
            <button 
              v-if="filtros.rolProfesional" 
              @click="limpiarFiltroEspecifico('rolProfesional')"
              class="btn-limpiar-filtro"
              title="Limpiar filtro de rol"
            >
              ✓
            </button>
          </div>
        </div>
        
        <div class="col-md-6 col-lg-6">
          <div class="form-group">
            <label for="profesional">
              Profesional Específico:
              <span class="contador-opciones">({{ profesionalesFiltradosDinamicos.length }} disponibles)</span>
            </label>
            <select 
              id="profesional" 
              v-model="filtros.profesional" 
              @change="actualizarFiltroProfesional"
              class="form-control"
              :class="{ 'has-selection': filtros.profesional }"
            >
              <option value="">Seleccione un profesional</option>
              <option v-for="prof in profesionalesDisponibles" :key="prof.cod_profesional" :value="prof.cod_profesional">
                {{ prof.nombre_profesional }}
              </option>
            </select>
            <button 
              v-if="filtros.profesional" 
              @click="limpiarFiltroEspecifico('profesional')"
              class="btn-limpiar-filtro"
              title="Limpiar filtro de profesional"
            >
              ✓
            </button>
          </div>
        </div>
      </div>

      <!-- Tercera fila de filtros - Mecanismos DINÁMICOS -->
      <div class="row">
        <div class="col-md-6 col-lg-4">
          <div class="form-group">
            <label for="mecanismo">
              Mecanismo General:
              <span class="contador-opciones">({{ mecanismosFiltradosDinamicos.length }} disponibles)</span>
            </label>
            <select 
              id="mecanismo" 
              v-model="filtros.mecanismo"
              @change="actualizarFiltrosMecanismo"
              class="form-control"
              :class="{ 'has-selection': filtros.mecanismo }"
              :disabled="cargandoFiltros"
            >
              <option value="">Todos los mecanismos</option>
              <option v-for="mecanismo in mecanismosDisponibles" :key="mecanismo.cod_mecanismo" :value="mecanismo.cod_mecanismo">
                {{ mecanismo.cod_mecanismo }}
              </option>
            </select>
            <button 
              v-if="filtros.mecanismo" 
              @click="limpiarFiltroEspecifico('mecanismo')"
              class="btn-limpiar-filtro"
              title="Limpiar filtro de mecanismo"
            >
              ✓
            </button>
          </div>
        </div>

        <div class="col-md-6 col-lg-4">
          <div class="form-group">
            <label for="mecanismoDetalle">
              Mecanismo Detalle:
              <span class="contador-opciones">({{ detallesMecanismoFiltradosDinamicos.length }} disponibles)</span>
            </label>
            <select 
              id="mecanismoDetalle" 
              v-model="filtros.mecanismoDetalle" 
              @change="actualizarFiltrosMecanismoDetalle"
              class="form-control"
              :class="{ 'has-selection': filtros.mecanismoDetalle }"
              :disabled="cargandoFiltros"
            >
              <option value="">Todos los detalles</option>
              <option v-for="detalle in detallesMecanismoDisponibles" :key="detalle.cod_mecanismo_detalle" :value="detalle.cod_mecanismo_detalle">
                {{ detalle.cod_mecanismo_detalle }}
              </option>
            </select>
            <button 
              v-if="filtros.mecanismoDetalle" 
              @click="limpiarFiltroEspecifico('mecanismoDetalle')"
              class="btn-limpiar-filtro"
              title="Limpiar filtro de detalle"
            >
              ✓
            </button>
          </div>
        </div>

        <div class="col-md-6 col-lg-4">
          <div class="form-group">
            <label for="grupo">
              Grupo:
              <span class="contador-opciones">({{ gruposFiltradosDinamicos.length }} disponibles)</span>
            </label>
            <select 
              id="grupo" 
              v-model="filtros.grupo"
              @change="actualizarFiltrosGrupo"
              class="form-control"
              :class="{ 'has-selection': filtros.grupo }"
              :disabled="cargandoFiltros"
            >
              <option value="">Todos los grupos</option>
              <option v-for="grupo in gruposDisponibles" :key="grupo.cod_grupo" :value="grupo.cod_grupo">
                {{ grupo.descripcion || grupo.cod_grupo }}
              </option>
            </select>
            <button 
              v-if="filtros.grupo" 
              @click="limpiarFiltroEspecifico('grupo')"
              class="btn-limpiar-filtro"
              title="Limpiar filtro de grupo"
            >
              ✓
            </button>
          </div>
        </div>
      </div>

      <!-- Cuarta fila de filtros - Estado -->
      <div class="row">
        <div class="col-md-6 col-lg-6">
          <div class="form-group">
            <label for="estadoFecha">
              Estado de Fecha:
              <span class="contador-opciones">(3 opciones)</span>
            </label>
            <select 
              id="estadoFecha" 
              v-model="filtros.estadoFecha"
              @change="actualizarFiltros"
              class="form-control"
              :class="{ 'has-selection': filtros.estadoFecha }"
            >
              <option value="">Todos</option>
              <option value="con_fecha">Con fecha de inicio</option>
              <option value="sin_fecha">Sin fecha de inicio</option>
            </select>
            <button 
              v-if="filtros.estadoFecha" 
              @click="limpiarFiltroEspecifico('estadoFecha')"
              class="btn-limpiar-filtro"
              title="Limpiar filtro de estado"
            >
              ✓
            </button>
          </div>
        </div>
      </div>

      <!-- Quinta fila de filtros - Vigencias DINÁMICAS -->
      <div class="row">
        <div class="col-md-6 col-lg-6">
          <div class="form-group">
            <label>
              Vigencia Rural:
              <span class="contador-opciones">({{ vigenciasRuralesDisponibles.length }} años disponibles)</span>
            </label>
            <div class="rango-vigencia">
              <select 
                v-model="filtros.vigenciaRuralDesde"
                @change="actualizarFiltros"
                class="form-control select-year"
                :class="{ 'has-selection': filtros.vigenciaRuralDesde }"
              >
                <option value="">Desde</option>
                <option v-for="year in vigenciasRuralesDisponibles" :key="'desde-' + year" :value="year">
                  {{ year }}
                </option>
              </select>
              <span class="separador-rango">-</span>
              <select 
                v-model="filtros.vigenciaRuralHasta"
                @change="actualizarFiltros"
                class="form-control select-year"
                :class="{ 'has-selection': filtros.vigenciaRuralHasta }"
              >
                <option value="">Hasta</option>
                <option v-for="year in vigenciasRuralesHastaDisponibles" :key="'hasta-' + year" :value="year">
                  {{ year }}
                </option>
              </select>
              <button 
                v-if="filtros.vigenciaRuralDesde || filtros.vigenciaRuralHasta" 
                @click="limpiarFiltroVigencia('rural')"
                class="btn-limpiar-filtro btn-limpiar-rango"
                title="Limpiar filtro de vigencia rural"
              >
                ✓
              </button>
            </div>
          </div>
        </div>
        
        <div class="col-md-6 col-lg-6">
          <div class="form-group">
            <label>
              Vigencia Urbana:
              <span class="contador-opciones">({{ vigenciasUrbanasDisponibles.length }} años disponibles)</span>
            </label>
            <div class="rango-vigencia">
              <select 
                v-model="filtros.vigenciaUrbanaDesde"
                @change="actualizarFiltros"
                class="form-control select-year"
                :class="{ 'has-selection': filtros.vigenciaUrbanaDesde }"
              >
                <option value="">Desde</option>
                <option v-for="year in vigenciasUrbanasDisponibles" :key="'desde-' + year" :value="year">
                  {{ year }}
                </option>
              </select>
              <span class="separador-rango">-</span>
              <select 
                v-model="filtros.vigenciaUrbanaHasta"
                @change="actualizarFiltros"
                class="form-control select-year"
                :class="{ 'has-selection': filtros.vigenciaUrbanaHasta }"
              >
                <option value="">Hasta</option>
                <option v-for="year in vigenciasUrbanasHastaDisponibles" :key="'hasta-' + year" :value="year">
                  {{ year }}
                </option>
              </select>
              <button 
                v-if="filtros.vigenciaUrbanaDesde || filtros.vigenciaUrbanaHasta" 
                @click="limpiarFiltroVigencia('urbana')"
                class="btn-limpiar-filtro btn-limpiar-rango"
                title="Limpiar filtro de vigencia urbana"
              >
                ✓
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- NUEVA SECCIÓN: Indicadores de filtros activos -->
      <div class="filtros-activos" v-if="hayFiltrosActivos">
        <h4>🔍 Filtros activos:</h4>
        <div class="tags-filtros">
          <span v-if="filtros.departamento" class="tag-filtro departamento">
            Departamento: {{ obtenerNombreFiltro('departamento', filtros.departamento) }}
            <button @click="limpiarFiltroEspecifico('departamento')">×</button>
          </span>
          <span v-if="filtros.territorial" class="tag-filtro territorial">
            Territorial: {{ obtenerNombreFiltro('territorial', filtros.territorial) }}
            <button @click="limpiarFiltroEspecifico('territorial')">×</button>
          </span>
          <span v-if="filtros.municipio" class="tag-filtro municipio">
            Municipio: {{ obtenerNombreFiltro('municipio', filtros.municipio) }}
            <button @click="limpiarFiltroEspecifico('municipio')">×</button>
          </span>
          <span v-if="filtros.rolProfesional" class="tag-filtro rol">
            Rol: {{ obtenerNombreFiltro('rolProfesional', filtros.rolProfesional) }}
            <button @click="limpiarFiltroEspecifico('rolProfesional')">×</button>
          </span>
          <span v-if="filtros.profesional" class="tag-filtro profesional">
            Profesional: {{ obtenerNombreFiltro('profesional', filtros.profesional) }}
            <button @click="limpiarFiltroEspecifico('profesional')">×</button>
          </span>
          <span v-if="filtros.mecanismo" class="tag-filtro mecanismo">
            Mecanismo: {{ obtenerNombreFiltro('mecanismo', filtros.mecanismo) }}
            <button @click="limpiarFiltroEspecifico('mecanismo')">×</button>
          </span>
          <span v-if="filtros.mecanismoDetalle" class="tag-filtro detalle">
            Detalle: {{ obtenerNombreFiltro('mecanismoDetalle', filtros.mecanismoDetalle) }}
            <button @click="limpiarFiltroEspecifico('mecanismoDetalle')">×</button>
          </span>
          <span v-if="filtros.grupo" class="tag-filtro grupo">
            Grupo: {{ obtenerNombreFiltro('grupo', filtros.grupo) }}
            <button @click="limpiarFiltroEspecifico('grupo')">×</button>
          </span>
          <span v-if="filtros.estadoFecha" class="tag-filtro estado">
            Estado: {{ obtenerNombreFiltro('estadoFecha', filtros.estadoFecha) }}
            <button @click="limpiarFiltroEspecifico('estadoFecha')">×</button>
          </span>
          <span v-if="filtros.vigenciaRuralDesde || filtros.vigenciaRuralHasta" class="tag-filtro vigencia-rural">
            Vigencia Rural: {{ obtenerRangoVigencia('rural') }}
            <button @click="limpiarFiltroVigencia('rural')">×</button>
          </span>
          <span v-if="filtros.vigenciaUrbanaDesde || filtros.vigenciaUrbanaHasta" class="tag-filtro vigencia-urbana">
            Vigencia Urbana: {{ obtenerRangoVigencia('urbana') }}
            <button @click="limpiarFiltroVigencia('urbana')">×</button>
          </span>
        </div>
      </div>

      <div class="filtros-buttons">
        <button class="btn btn-primary" @click="aplicarFiltros" :disabled="cargandoFiltros">
          <i class="material-icons">filter_list</i>
          Aplicar Filtros
        </button>
        <button class="btn btn-secondary" @click="limpiarFiltros" :disabled="cargandoFiltros">
          <i class="material-icons">clear_all</i>
          Limpiar Filtros
        </button>
      </div>
    </div>

    <!-- Estado de carga y mensajes -->
    <div v-if="cargando" class="loading-container">
      <div class="spinner"></div>
      <span class="loading-text">Cargando municipios...</span>
    </div>

    <div v-else-if="error" class="error-container">
      <i class="material-icons">error</i>
      <span>{{ error }}</span>
      <button class="btn btn-primary" @click="cargarMunicipios">Reintentar</button>
    </div>

    <div v-else-if="municipiosTabla.length === 0" class="empty-container">
      <i class="material-icons">info</i>
      <span>No se encontraron municipios con los filtros seleccionados</span>
      <div v-if="isProfesional && municipiosPermitidos.length === 0" class="no-access-message">
        <i class="material-icons">lock</i>
        <p>No tienes municipios asignados. Contacta con el administrador para obtener acceso.</p>
      </div>
    </div>

    <!-- Tabla de resultados -->
    <div v-else class="results-container">
      <div class="results-header">
        <h3 class="results-title">Resultados</h3>
        <div class="results-summary">
          <span class="results-count">{{ municipiosTabla.length }} municipios encontrados</span>
          <span v-if="isProfesional" class="scope-indicator">
            (Limitado a municipios asignados)
          </span>
          <span v-if="hayFiltrosActivos" class="results-filter-info">
            (filtrados de {{ municipios.length }} totales)
          </span>
        </div>
      </div>

      <div class="table-responsive">
        <table class="table table-striped table-hover">
          <thead>
            <tr>
              <th @click="ordenarPor('cod_municipio')" class="th-codigo sortable">
                Código
                <i v-if="ordenacion.campo === 'cod_municipio'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('nom_municipio')" class="th-municipio sortable">
                Municipio
                <i v-if="ordenacion.campo === 'nom_municipio'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('cod_depto.nom_depto')" class="th-depto sortable">
                Departamento
                <i v-if="ordenacion.campo === 'cod_depto.nom_depto'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('nom_territorial')" class="th-territorial sortable">
                Territorial
                <i v-if="ordenacion.campo === 'nom_territorial'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('area')" class="th-area sortable">
                Área [ha]
                <i v-if="ordenacion.campo === 'area'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('mecanismo_general')" class="th-mecanismo sortable">
                Mecanismo
                <i v-if="ordenacion.campo === 'mecanismo_general'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('grupo')" class="th-grupo sortable">
                Grupo
                <i v-if="ordenacion.campo === 'grupo'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('fecha_inicio')" class="th-fecha sortable">
                Fecha Inicio
                <i v-if="ordenacion.campo === 'fecha_inicio'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <!-- NUEVAS COLUMNAS -->
              <th class="th-vigencia">Vigencia Rural</th>
              <th class="th-vigencia">Vigencia Urbana</th>
              <th class="th-acciones">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="municipio in municipiosVisibles" :key="municipio.cod_municipio">
              <td class="text-center">{{ municipio.cod_municipio }}</td>
              <td>{{ municipio.nom_municipio }}</td>
              <td>{{ obtenerNombreDepartamento(municipio) }}</td>
              <td>{{ municipio.nom_territorial || 'N/A' }}</td>
              <td>{{ municipio.area || 'N/A' }}</td>
              <td>{{ municipio.mecanismo_general || 'N/A' }}</td>
              <td>{{ municipio.grupo || 'N/A' }}</td>
              <td>{{ formatFecha(municipio.fecha_inicio) }}</td>
              <!-- NUEVAS COLUMNAS -->
              <td class="text-center">{{ obtenerVigenciaRural(municipio.cod_municipio) }}</td>
              <td class="text-center">{{ obtenerVigenciaUrbana(municipio.cod_municipio) }}</td>
              <td>
                <div class="action-buttons">
                  <button 
                    class="action-btn view-btn"
                    @click="verDetalleMunicipio(municipio)"
                    title="Ver detalles"
                  >
                    <i class="material-icons">visibility</i>
                  </button>
                  
                  <router-link 
                    :to="`/disposicion-informacion/insumos?municipio=${municipio.cod_municipio}`" 
                    class="action-btn insumos-btn"
                    title="Ver insumos"
                  >
                    <i class="material-icons">folder</i>
                  </router-link>
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

    <!-- Modal de detalles para municipio -->
    <div class="modal" v-if="modalDetalle.mostrar">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">
              <i class="material-icons">location_city</i>
              Detalles del Municipio - {{ modalDetalle.municipio?.nom_municipio }}
            </h4>
            <button class="close-button" @click="modalDetalle.mostrar = false">
              <i class="material-icons">close</i>
            </button>
          </div>
          <div class="modal-body">
            <div v-if="modalDetalle.municipio" class="municipio-info">
              <div class="info-grid">
                <div class="info-section">
                  <h5>Información General</h5>
                  <div class="info-fields">
                    <div class="info-field">
                      <span class="label">Código:</span>
                      <span class="value">{{ modalDetalle.municipio.cod_municipio }}</span>
                    </div>
                    <div class="info-field">
                      <span class="label">Nombre:</span>
                      <span class="value">{{ modalDetalle.municipio.nom_municipio }}</span>
                    </div>
                    <div class="info-field">
                      <span class="label">Departamento:</span>
                      <span class="value">{{ obtenerNombreDepartamento(modalDetalle.municipio) }}</span>
                    </div>
                    <div class="info-field">
                      <span class="label">Territorial:</span>
                      <span class="value">{{ modalDetalle.municipio.nom_territorial || 'No asignada' }}</span>
                    </div>
                    <div class="info-field">
                      <span class="label">Área:</span>
                      <span class="value">{{ modalDetalle.municipio.area || 'No disponible' }}</span>
                    </div>
                    <div class="info-field">
                      <span class="label">Fecha Inicio:</span>
                      <span class="value">{{ formatFecha(modalDetalle.municipio.fecha_inicio) }}</span>
                    </div>
                  </div>
                </div>
                
                <div class="info-section">
                  <h5>Información de Mecanismos</h5>
                  <div class="info-fields">
                    <div class="info-field">
                      <span class="label">Mecanismo General:</span>
                      <span class="value">{{ modalDetalle.municipio.mecanismo_general || 'No asignado' }}</span>
                    </div>
                    <div class="info-field">
                      <span class="label">Mecanismo Detalle:</span>
                      <span class="value">{{ modalDetalle.municipio.mecanismo_detalle || 'No asignado' }}</span>
                    </div>
                    <div class="info-field">
                      <span class="label">Mecanismo Operación:</span>
                      <span class="value">{{ modalDetalle.municipio.mecanismo_operacion || 'No asignado' }}</span>
                    </div>
                    <div class="info-field">
                      <span class="label">Alcance Operación:</span>
                      <span class="value">{{ modalDetalle.municipio.alcance_operacion || 'No asignado' }}</span>
                    </div>
                    <div class="info-field">
                      <span class="label">Grupo:</span>
                      <span class="value">{{ modalDetalle.municipio.grupo || 'No asignado' }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
                <!-- NUEVA SECCIÓN DE INFORMACIÓN CATASTRAL CON PESTAÑAS -->
                <div class="info-section" v-if="modalDetalle.todosInfoAdmin && modalDetalle.todosInfoAdmin.length > 0">
                  <h5>
                    <i class="material-icons">assessment</i>
                    Información Catastral
                    <span class="registro-counter">({{ modalDetalle.todosInfoAdmin.length }} registro{{ modalDetalle.todosInfoAdmin.length > 1 ? 's' : '' }})</span>
                  </h5>
                  
                  <!-- 🆕 PESTAÑAS (solo mostrar si hay más de 1 registro) -->
                  <div v-if="modalDetalle.todosInfoAdmin.length > 1" class="tabs-container">
                    <div class="tabs-header">
                      <button 
                        v-for="(registro, index) in modalDetalle.todosInfoAdmin" 
                        :key="`tab-${index}`"
                        class="tab-button"
                        :class="{ 'active': modalDetalle.tabActiva === index }"
                        @click="cambiarTabInfoAdmin(index)"
                      >
                        <i class="material-icons">folder</i>
                        <!-- Aquí cambiamos el nombre según el índice -->
                        <span v-if="index === 0">Vigente</span>
                        <span v-else-if="index === 1">Desactualizado</span>
                        <span v-else>Registro {{ index + 1 }}</span>

                        <span v-if="registro.vigencia_rural || registro.vigencia_urbana" class="tab-vigencias">
                          <span v-if="registro.vigencia_rural" class="vigencia-rural">R: {{ registro.vigencia_rural }}</span>
                          <span v-if="registro.vigencia_urbana" class="vigencia-urbana">U: {{ registro.vigencia_urbana }}</span>
                        </span>
                      </button>
                    </div>
                  </div>

                  
                  <!-- 🆕 CONTENIDO DE LA PESTAÑA ACTIVA -->
                  <div v-if="modalDetalle.todosInfoAdmin[modalDetalle.tabActiva]" class="tab-content">
                    <div class="info-fields">
                      <!-- Información de Vigencias y Estados -->
                      <div class="info-subsection">
                        <h6>Vigencias y Estados</h6>
                        <div class="info-field">
                          <span class="label">Vigencia Rural:</span>
                          <span class="value" :class="{'vigencia-desactualizada': modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].estado_rural === 'DESACTUALIZADO'}">
                            {{ modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].vigencia_rural || 'No disponible' }}
                          </span>
                        </div>
                        <div class="info-field">
                          <span class="label">Vigencia Urbana:</span>
                          <span class="value" :class="{'vigencia-desactualizada': modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].estado_urbano === 'DESACTUALIZADO'}">
                            {{ modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].vigencia_urbana || 'No disponible' }}
                          </span>
                        </div>
                        <div class="info-field">
                          <span class="label">Estado Rural:</span>
                          <span class="value" :class="{'estado-badge': true, 'estado-desactualizado': modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].estado_rural === 'DESACTUALIZADO'}">
                            {{ modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].estado_rural || 'No disponible' }}
                          </span>
                        </div>
                        <div class="info-field">
                          <span class="label">Estado Urbano:</span>
                          <span class="value" :class="{'estado-badge': true, 'estado-desactualizado': modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].estado_urbano === 'DESACTUALIZADO'}">
                            {{ modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].estado_urbano || 'No disponible' }}
                          </span>
                        </div>
                      </div>
                      
                      <!-- Información del Gestor -->
                      <div class="info-subsection">
                        <h6>Información del Gestor</h6>
                        <div class="info-field">
                          <span class="label">Gestor Catastral:</span>
                          <span class="value">{{ modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].gestor_prestador_servicio || 'No disponible' }}</span>
                        </div>
                        <div class="info-field">
                          <span class="label">ID Gestor:</span>
                          <span class="value">{{ modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].id_gestor_catas || 'No disponible' }}</span>
                        </div>
                        <div class="info-field">
                          <span class="label">Año Publicación:</span>
                          <span class="value">{{ modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].publicacion_year || 'No disponible' }}</span>
                        </div>
                      </div>
                      
                      <!-- Resumen de Predios y Avalúos -->
                      <div class="info-subsection">
                        <h6>Resumen General</h6>
                        <div class="info-field">
                          <span class="label">Total Predios:</span>
                          <span class="value highlight">{{ formatNumber(modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].total_predios) }}</span>
                        </div>
                        <div class="info-field">
                          <span class="label">Área Total (ha):</span>
                          <span class="value">{{ formatNumber(modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].total_area_terreno_ha) }}</span>
                        </div>
                        <div class="info-field">
                          <span class="label">Avalúo Total:</span>
                          <span class="value highlight">{{ formatCurrency(modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].total_avaluos) }}</span>
                        </div>
                      </div>
                      
                      <!-- Botón para ver más detalles (igual que antes) -->
                      <div class="info-actions">
                        <button 
                          class="btn btn-sm btn-info" 
                          @click="mostrarDetalleCompleto = !mostrarDetalleCompleto"
                        >
                          <i class="material-icons">{{ mostrarDetalleCompleto ? 'expand_less' : 'expand_more' }}</i>
                          {{ mostrarDetalleCompleto ? 'Ver menos' : 'Ver detalles completos' }}
                        </button>
                      </div>
                      
                      <!-- Detalles completos (colapsable) - usar el registro activo -->
                      <div v-show="mostrarDetalleCompleto" class="info-detalle-completo">
                        <!-- Información Rural Detallada -->
                        <div class="info-subsection">
                          <h6>Información Rural Detallada</h6>
                          <div class="info-field">
                            <span class="label">Predios Rurales:</span>
                            <span class="value">{{ formatNumber(modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].predios_rurales) }}</span>
                          </div>
                          <div class="info-field">
                            <span class="label">Área Terreno (m²):</span>
                            <span class="value">{{ formatNumber(modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].area_terreno_rural_m2) }}</span>
                          </div>
                          <div class="info-field">
                            <span class="label">Área Terreno (ha):</span>
                            <span class="value">{{ formatNumber(modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].area_terreno_rural_ha) }}</span>
                          </div>
                          <div class="info-field">
                            <span class="label">Área Construida (m²):</span>
                            <span class="value">{{ formatNumber(modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].area_construida_rural_m2) }}</span>
                          </div>
                          <div class="info-field">
                            <span class="label">Avalúo Rural:</span>
                            <span class="value">{{ formatCurrency(modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].avaluo_rural) }}</span>
                          </div>
                        </div>
                        
                        <!-- Información Urbana Detallada -->
                        <div class="info-subsection">
                          <h6>Información Urbana Detallada</h6>
                          <div class="info-field">
                            <span class="label">Predios Urbanos:</span>
                            <span class="value">{{ formatNumber(modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].predios_urbanos) }}</span>
                          </div>
                          <div class="info-field">
                            <span class="label">Área Terreno (m²):</span>
                            <span class="value">{{ formatNumber(modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].area_terreno_urbana_m2) }}</span>
                          </div>
                          <div class="info-field">
                            <span class="label">Área Terreno (ha):</span>
                            <span class="value">{{ formatNumber(modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].area_terreno_urbana_ha) }}</span>
                          </div>
                          <div class="info-field">
                            <span class="label">Área Construida (m²):</span>
                            <span class="value">{{ formatNumber(modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].area_construida_urbana_m2) }}</span>
                          </div>
                          <div class="info-field" v-if="modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].avaluo_urbano_1">
                            <span class="label">Avalúo Urbano 1:</span>
                            <span class="value">{{ formatCurrency(modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].avaluo_urbano_1) }}</span>
                          </div>
                          <div class="info-field" v-if="modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].avaluo_urbano_2">
                            <span class="label">Avalúo Urbano 2:</span>
                            <span class="value">{{ formatCurrency(modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].avaluo_urbano_2) }}</span>
                          </div>
                        </div>
                        
                        <!-- Áreas Geográficas -->
                        <div class="info-subsection">
                          <h6>Áreas Geográficas</h6>
                          <div class="info-field">
                            <span class="label">Área Geográfica Rural (ha):</span>
                            <span class="value">{{ formatNumber(modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].area_geografica_rural_ha) }}</span>
                          </div>
                          <div class="info-field">
                            <span class="label">Área Geográfica Urbana (ha):</span>
                            <span class="value">{{ formatNumber(modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].area_geografica_urbana_ha) }}</span>
                          </div>
                          <div class="info-field">
                            <span class="label">Área Rural Estados Catastrales (ha):</span>
                            <span class="value">{{ formatNumber(modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].area_rural_estados_catastrales_ha) }}</span>
                          </div>
                          <div class="info-field">
                            <span class="label">Área Urbana Estados Catastrales (ha):</span>
                            <span class="value">{{ formatNumber(modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].area_urbana_estados_catastrales_ha) }}</span>
                          </div>
                        </div>
                        
                        <!-- Observaciones -->
                        <div v-if="modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].observacion" class="info-subsection">
                          <h6>Observaciones</h6>
                          <div class="info-field-full">
                            <p class="observacion-text">{{ modalDetalle.todosInfoAdmin[modalDetalle.tabActiva].observacion }}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Mostrar mensaje si no hay información catastral -->
                <div v-else class="info-section">
                  <h5>
                    <i class="material-icons">assessment</i>
                    Información Catastral
                  </h5>
                  <div class="no-info-message">
                    <i class="material-icons">info</i>
                    <p>No se encontró información catastral para este municipio.</p>
                  </div>
                </div>
            </div>

            <div class="info-section">
              <h5>
                <i class="material-icons">location_city</i>
                Centros Poblados ({{ centrosPoblados.length }})
              </h5>
              
              <!-- Loading state -->
              <div v-if="cargandoCentrosPoblados" class="centros-loading">
                <div class="spinner-small"></div>
                <span>Cargando centros poblados...</span>
              </div>
              
              <!-- Error state -->
              <div v-else-if="errorCentrosPoblados" class="centros-error">
                <i class="material-icons">error</i>
                <span>{{ errorCentrosPoblados }}</span>
              </div>
              
              <!-- Empty state -->
              <div v-else-if="centrosPoblados.length === 0" class="centros-empty">
                <i class="material-icons">info</i>
                <span>No se encontraron centros poblados para este municipio</span>
              </div>
              
              <!-- Centros poblados table -->
              <div v-else class="centros-table-container">
                <table class="centros-table">
                  <thead>
                    <tr>
                      <th>Código</th>
                      <th>Nombre del Centro Poblado</th>
                      <th>Área Oficial (ha)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="centro in centrosPoblados" :key="centro.cod_centro_poblado">
                      <td class="codigo-centro">{{ centro.cod_centro_poblado }}</td>
                      <td class="nombre-centro">{{ centro.nom_centro_poblado }}</td>
                      <td class="area-centro">
                        {{ centro.area_oficial_ha ? formatNumber(centro.area_oficial_ha) : 'N/D' }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <router-link 
              :to="`/disposicion-informacion/insumos?municipio=${modalDetalle.municipio?.cod_municipio}`" 
              class="btn btn-info"
              @click="modalDetalle.mostrar = false"
            >
              <i class="material-icons">folder</i>
              Ver Insumos
            </router-link>
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

<script lang="ts">
import { defineComponent, ref, computed, onMounted , watch} from 'vue'
import { useRouter, useRoute} from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import { debounce } from 'lodash'
import axios from 'axios'
import { centrosPobladosApi } from '@/api/centrosPoblados'
// Import API functions
import { getMunicipios } from '@/api/municipios';
import { getDepartamentos } from '@/api/departamentos'
import { getInfoAdministrativa } from '@/api/infoAdministrativa'
import api, { API_URL } from '@/api/config'
import { getTodosInfoAdministrativaPorMunicipio } from '@/api/infoAdministrativa'

export default defineComponent({
  name: 'MunicipiosDisposicionList',

  setup() {
    const router = useRouter()
    const route = useRoute()
    const authStore = useAuthStore()
    
    // Estado de carga y errores
    const cargando = ref(false)
    const cargandoFiltros = ref(false)
    const error = ref<string | null>(null)
    
    // Datos
    const municipios = ref<any[]>([])
    const departamentos = ref<any[]>([])
    const territoriales = ref<any[]>([])
    const mecanismos = ref<any[]>([])
    const detallesMecanismo = ref<any[]>([])
    const grupos = ref<any[]>([])
    
    // Estado para profesionales
    const profesionales = ref<any[]>([])
    const profesionalesFiltrados = ref<any[]>([])
    
    // Estado para municipios filtrados por departamento
    const municipiosFiltrados = ref<any[]>([])
    
    // Estado para los catálogos filtrados
    const territorialesFiltradas = ref<any[]>([])
    const mecanismosFiltrados = ref<any[]>([])
    const detallesMecanismoFiltrados = ref<any[]>([])
    const gruposFiltrados = ref<any[]>([])
    
    // Datos para profesionales y sus relaciones
    const profesionalMunicipio = ref<any[]>([])
    const profesionalTerritorial = ref<any[]>([])
    
    // NUEVOS ESTADOS PARA INFO ADMINISTRATIVA
    const infoAdministrativa = ref<any[]>([])
    const infoAdminMap = ref<Map<number, any>>(new Map())
    const mostrarDetalleCompleto = ref(false)

    //
    const centrosPoblados = ref<any[]>([])
    const cargandoCentrosPoblados = ref(false)
    const errorCentrosPoblados = ref<string | null>(null)
    // Búsqueda y filtros
    const filtros = ref({
      departamento: '',
      territorial: '',
      municipio: '',
      mecanismo: '',
      mecanismoDetalle: '',
      grupo: '',
      estadoFecha: '',
      busqueda: '',
      profesional: '',
      rolProfesional: '',
      vigenciaRuralDesde: '',
      vigenciaRuralHasta: '',
      vigenciaUrbanaDesde: '',
      vigenciaUrbanaHasta: ''
    })
    
    // Ordenación
    const ordenacion = ref({
      campo: 'nom_municipio',
      ascendente: true
    })
    
    // Paginación
    const paginaActual = ref(1)
    const elementosPorPagina = ref(20)
    
    // Modal
    const modalDetalle = ref({
      mostrar: false,
      municipio: null as any,
      infoAdmin: null as any,  
      todosInfoAdmin: [] as any[],  
      tabActiva: 0  
    })
    
    // ========== VERIFICACIÓN DE ROLES Y PERMISOS ==========
    const isSuperAdmin = computed(() => {
      return authStore.user?.isAdmin === true || 
             authStore.user?.is_superuser === true ||
             authStore.user?.is_admin === true;
    });
    
    const isAdmin = computed(() => {
      return (authStore.user?.isStaff === true || authStore.isAdmin) && !isSuperAdmin.value;
    });
    
    const isProfesional = computed(() => 
      authStore.user?.rol_tipo === 'profesional'
    );
    
    // Municipios que el profesional tiene permitido ver
    const municipiosPermitidos = computed(() => {
      if (isSuperAdmin.value || isAdmin.value) {
        return []; // No aplica restricción
      }
      
      if (!isProfesional.value || !authStore.user?.municipios_asignados) return [];
      
      let municipios: number[] = [];
      
      if (typeof authStore.user.municipios_asignados === 'string') {
        municipios = authStore.user.municipios_asignados.split(',')
          .map(m => parseInt(m.trim()))
          .filter(m => !isNaN(m));
      } else if (Array.isArray(authStore.user.municipios_asignados)) {
        municipios = authStore.user.municipios_asignados;
      }
      
      return municipios;
    });
    
    // Información de acceso
    const accessLevelText = computed(() => {
      if (isSuperAdmin.value) return 'Acceso Total';
      if (isAdmin.value) return 'Solo Lectura';
      if (isProfesional.value) return `Municipios Asignados (${municipiosPermitidos.value.length})`;
      return 'Solo Lectura';
    });
    
    const accessLevelIcon = computed(() => {
      if (isSuperAdmin.value) return 'all_inclusive';
      if (isAdmin.value) return 'visibility';
      if (isProfesional.value) return 'location_on';
      return 'visibility';
    });
    
    const accessLevelClass = computed(() => {
      if (isSuperAdmin.value) return 'access-total';
      if (isAdmin.value) return 'access-admin';
      if (isProfesional.value) return 'access-profesional';
      return 'access-publico';
    });


    // NUEVA FUNCIÓN: Cargar centros poblados de un municipio
const cargarCentrosPoblados = async (codMunicipio: number) => {
  try {
    cargandoCentrosPoblados.value = true
    errorCentrosPoblados.value = null
    
    console.log('🏘️ Cargando centros poblados para municipio:', codMunicipio)
    
    const centrosData = await centrosPobladosApi.porMunicipio(codMunicipio)
    centrosPoblados.value = centrosData || []
    
    console.log('✅ Centros poblados cargados:', centrosPoblados.value.length, 'registros')
    
  } catch (error) {
    console.error('❌ Error cargando centros poblados:', error)
    errorCentrosPoblados.value = 'Error al cargar centros poblados'
    centrosPoblados.value = []
  } finally {
    cargandoCentrosPoblados.value = false
  }
}

    // ========== SISTEMA DE FILTROS ACUMULATIVOS ==========
    
    // Conjunto base de municipios disponibles según permisos
    const municipiosBase = computed(() => {
      return filtrarMunicipiosPorPermisos([...municipios.value])
    })

    /**
     * MUNICIPIOS FILTRADOS ACUMULATIVAMENTE
     */
    const municipiosFiltradosAcumulativos = computed(() => {
      let resultado = [...municipiosBase.value]
      
      // Aplicar TODOS los filtros activos de manera acumulativa
      if (filtros.value.departamento) {
        resultado = resultado.filter(m => {
          const codDepto = typeof m.cod_depto === 'object' && m.cod_depto !== null 
            ? (m.cod_depto.cod_depto || m.cod_depto)
            : m.cod_depto
          return codDepto.toString() === filtros.value.departamento.toString()
        })
      }
      
      if (filtros.value.territorial) {
        resultado = resultado.filter(m => m.nom_territorial === filtros.value.territorial)
      }
      
      if (filtros.value.municipio) {
        resultado = resultado.filter(m => 
          m.cod_municipio.toString() === filtros.value.municipio.toString()
        )
      }
      
      if (filtros.value.mecanismo) {
        resultado = resultado.filter(m => m.mecanismo_general === filtros.value.mecanismo)
      }
      
      if (filtros.value.mecanismoDetalle) {
        resultado = resultado.filter(m => m.mecanismo_detalle === filtros.value.mecanismoDetalle)
      }
      
      if (filtros.value.grupo) {
        resultado = resultado.filter(m => m.grupo === filtros.value.grupo)
      }
      
      if (filtros.value.estadoFecha) {
        if (filtros.value.estadoFecha === 'con_fecha') {
          resultado = resultado.filter(m => m.fecha_inicio)
        } else if (filtros.value.estadoFecha === 'sin_fecha') {
          resultado = resultado.filter(m => !m.fecha_inicio)
        }
      }
      
      // Aplicar filtros de profesional
      if (filtros.value.profesional || filtros.value.rolProfesional) {
        let profesionalesIds = []
        
        if (filtros.value.profesional) {
          profesionalesIds = [filtros.value.profesional]
        } else if (filtros.value.rolProfesional) {
          const profesionalesDelRol = profesionales.value.filter(prof => {
            if (!prof) return false
            try {
              let rolText = ''
              if (typeof prof.rol_profesional === 'string') {
                rolText = prof.rol_profesional
              } else if (prof.rol_profesional && typeof prof.rol_profesional === 'object') {
                if (prof.rol_profesional.rol_profesional) {
                  rolText = prof.rol_profesional.rol_profesional
                }
              }
              const rolUpper = rolText.toUpperCase()
              const rolBuscado = filtros.value.rolProfesional.toUpperCase()
              return rolUpper.includes(rolBuscado)
            } catch (error) {
              return false
            }
          })
          profesionalesIds = profesionalesDelRol.map(prof => prof.cod_profesional)
        }
        
        if (profesionalesIds.length > 0) {
          const municipiosAsignados = profesionalMunicipio.value
            .filter(pm => profesionalesIds.includes(pm.cod_profesional))
            .map(pm => pm.cod_municipio)
          
          resultado = resultado.filter(m => municipiosAsignados.includes(m.cod_municipio))
        }
      }
      
      // Aplicar filtros de vigencia rural
      if (filtros.value.vigenciaRuralDesde || filtros.value.vigenciaRuralHasta) {
        resultado = resultado.filter(m => {
          const info = infoAdminMap.value.get(m.cod_municipio)
          if (!info || !info.vigencia_rural) return false
          
          const vigenciaYear = parseInt(info.vigencia_rural)
          if (isNaN(vigenciaYear)) return false
          
          const desde = filtros.value.vigenciaRuralDesde ? parseInt(filtros.value.vigenciaRuralDesde) : 0
          const hasta = filtros.value.vigenciaRuralHasta ? parseInt(filtros.value.vigenciaRuralHasta) : 9999
          
          return vigenciaYear >= desde && vigenciaYear <= hasta
        })
      }
      
      // Aplicar filtros de vigencia urbana
      if (filtros.value.vigenciaUrbanaDesde || filtros.value.vigenciaUrbanaHasta) {
        resultado = resultado.filter(m => {
          const info = infoAdminMap.value.get(m.cod_municipio)
          if (!info || !info.vigencia_urbana) return false
          
          const vigenciaYear = parseInt(info.vigencia_urbana)
          if (isNaN(vigenciaYear)) return false
          
          const desde = filtros.value.vigenciaUrbanaDesde ? parseInt(filtros.value.vigenciaUrbanaDesde) : 0
          const hasta = filtros.value.vigenciaUrbanaHasta ? parseInt(filtros.value.vigenciaUrbanaHasta) : 9999
          
          return vigenciaYear >= desde && vigenciaYear <= hasta
        })
      }
      
      return resultado
    })

    /**
     * OPCIONES DISPONIBLES PARA CADA FILTRO BASADAS EN MUNICIPIOS FILTRADOS ACTUALES
     */
    const departamentosDisponibles = computed(() => {
      const deptosIds = new Set(municipiosFiltradosAcumulativos.value.map(m => {
        if (typeof m.cod_depto === 'object' && m.cod_depto !== null) {
          return m.cod_depto.cod_depto || m.cod_depto
        }
        return m.cod_depto
      }))
      
      return departamentos.value
        .filter(d => deptosIds.has(d.cod_depto))
        .sort((a, b) => a.nom_depto.localeCompare(b.nom_depto))
    })

    const territorialesFitradasDinamicas = computed(() => {
      const territorialesUnicas = new Set(
        municipiosFiltradosAcumulativos.value
          .map(m => m.nom_territorial)
          .filter(t => t && t.trim() !== '')
      )
      
      return territoriales.value
        .filter(t => territorialesUnicas.has(t.nom_territorial))
        .sort((a, b) => a.nom_territorial.localeCompare(b.nom_territorial))
    })

    const municipiosFiltradosDinamicos = computed(() => {
      return municipiosFiltradosAcumulativos.value
        .sort((a, b) => a.nom_municipio.localeCompare(b.nom_municipio))
    })

    const mecanismosFiltradosDinamicos = computed(() => {
      const mecanismosUsados = new Set(
        municipiosFiltradosAcumulativos.value
          .map(m => m.mecanismo_general)
          .filter(m => m && m.trim() !== '')
      )
      
      return mecanismos.value
        .filter(m => mecanismosUsados.has(m.cod_mecanismo))
        .sort((a, b) => a.cod_mecanismo.localeCompare(b.cod_mecanismo))
    })

    const detallesMecanismoFiltradosDinamicos = computed(() => {
      const detallesUsados = new Set(
        municipiosFiltradosAcumulativos.value
          .map(m => m.mecanismo_detalle)
          .filter(d => d && d.trim() !== '')
      )
      
      return detallesMecanismo.value
        .filter(d => detallesUsados.has(d.cod_mecanismo_detalle))
        .sort((a, b) => a.cod_mecanismo_detalle.localeCompare(b.cod_mecanismo_detalle))
    })

    const gruposFiltradosDinamicos = computed(() => {
      const gruposUsados = new Set(
        municipiosFiltradosAcumulativos.value
          .map(m => m.grupo)
          .filter(g => g && g.trim() !== '')
      )
      
      return grupos.value
        .filter(g => gruposUsados.has(g.cod_grupo))
        .sort((a, b) => (a.descripcion || a.cod_grupo).localeCompare(b.descripcion || b.cod_grupo))
    })

    const profesionalesFiltradosDinamicos = computed(() => {
      // Solo mostrar profesionales que tengan municipios en el conjunto filtrado actual
      const municipiosIds = municipiosFiltradosAcumulativos.value.map(m => m.cod_municipio)
      
      let profesionalesBase = [...profesionales.value]
      
      // Filtrar por rol si está seleccionado
      if (filtros.value.rolProfesional) {
        profesionalesBase = profesionalesBase.filter(prof => {
          if (!prof) return false
          try {
            let rolText = ''
            if (typeof prof.rol_profesional === 'string') {
              rolText = prof.rol_profesional
            } else if (prof.rol_profesional && typeof prof.rol_profesional === 'object') {
              if (prof.rol_profesional.rol_profesional) {
                rolText = prof.rol_profesional.rol_profesional
              }
            }
            const rolUpper = rolText.toUpperCase()
            const rolBuscado = filtros.value.rolProfesional.toUpperCase()
            return rolUpper.includes(rolBuscado)
          } catch (error) {
            return false
          }
        })
      }
      
      // Filtrar profesionales que tengan municipios en el conjunto actual
      return profesionalesBase.filter(prof => {
        const tieneAsignacionValida = profesionalMunicipio.value.some(pm => 
          pm.cod_profesional === prof.cod_profesional && 
          municipiosIds.includes(pm.cod_municipio)
        )
        return tieneAsignacionValida
      })
    })

    const rolesProfesionalesFiltradosDinamicos = computed(() => {
      // Obtener profesionales que tienen municipios en el conjunto filtrado actual
      const municipiosIds = municipiosFiltradosAcumulativos.value.map(m => m.cod_municipio)
      
      const profesionalesConAsignaciones = profesionales.value.filter(prof => {
        return profesionalMunicipio.value.some(pm => 
          pm.cod_profesional === prof.cod_profesional && 
          municipiosIds.includes(pm.cod_municipio)
        )
      })
      
      const rolesSet = new Set()
      profesionalesConAsignaciones.forEach(prof => {
        if (!prof) return
        try {
          let rolText = ''
          if (typeof prof.rol_profesional === 'string') {
            rolText = prof.rol_profesional
          } else if (prof.rol_profesional && typeof prof.rol_profesional === 'object') {
            if (prof.rol_profesional.rol_profesional) {
              rolText = prof.rol_profesional.rol_profesional
            }
          }
          const rolUpper = rolText.toUpperCase()
          if (rolUpper.includes('L.A.S')) rolesSet.add('L.A.S')
          if (rolUpper.includes('P.A.S')) rolesSet.add('P.A.S')
        } catch (error) {
          // Ignorar errores
        }
      })
      
      const rolesArray = []
      if (rolesSet.has('L.A.S')) {
        rolesArray.push({ codigo: 'L.A.S', nombre: 'Profesionales L.A.S' })
      }
      if (rolesSet.has('P.A.S')) {
        rolesArray.push({ codigo: 'P.A.S', nombre: 'Profesionales P.A.S' })
      }
      
      return rolesArray
    })

    /**
     * VERIFICAR SI HAY FILTROS ACTIVOS
     */
    const hayFiltrosActivos = computed(() => {
      return !!(
        filtros.value.departamento || 
        filtros.value.territorial || 
        filtros.value.municipio || 
        filtros.value.mecanismo || 
        filtros.value.mecanismoDetalle || 
        filtros.value.grupo || 
        filtros.value.profesional || 
        filtros.value.rolProfesional ||
        filtros.value.estadoFecha ||
        filtros.value.vigenciaRuralDesde ||
        filtros.value.vigenciaRuralHasta ||
        filtros.value.vigenciaUrbanaDesde ||
        filtros.value.vigenciaUrbanaHasta
      )
    })
    
    // 🆕 COMPUTED PARA VIGENCIAS DISPONIBLES (DINÁMICAS)
    const vigenciasRuralesDisponibles = computed(() => {
      const años = new Set<number>()
      
      // Solo considerar municipios en el conjunto filtrado actual
      municipiosFiltradosAcumulativos.value.forEach(m => {
        const info = infoAdminMap.value.get(m.cod_municipio)
        if (info && info.vigencia_rural) {
          const year = parseInt(info.vigencia_rural)
          if (!isNaN(year)) {
            años.add(year)
          }
        }
      })
      
      return Array.from(años).sort((a, b) => a - b)
    })
    
    const vigenciasUrbanasDisponibles = computed(() => {
      const años = new Set<number>()
      
      // Solo considerar municipios en el conjunto filtrado actual
      municipiosFiltradosAcumulativos.value.forEach(m => {
        const info = infoAdminMap.value.get(m.cod_municipio)
        if (info && info.vigencia_urbana) {
          const year = parseInt(info.vigencia_urbana)
          if (!isNaN(year)) {
            años.add(year)
          }
        }
      })
      
      return Array.from(años).sort((a, b) => a - b)
    })
    
    // Computed para los años "hasta" basados en el "desde" seleccionado
    const vigenciasRuralesHastaDisponibles = computed(() => {
      if (!filtros.value.vigenciaRuralDesde) {
        return vigenciasRuralesDisponibles.value
      }
      
      const desde = parseInt(filtros.value.vigenciaRuralDesde)
      return vigenciasRuralesDisponibles.value.filter(year => year >= desde)
    })
    
    const vigenciasUrbanasHastaDisponibles = computed(() => {
      if (!filtros.value.vigenciaUrbanaDesde) {
        return vigenciasUrbanasDisponibles.value
      }
      
      const desde = parseInt(filtros.value.vigenciaUrbanaDesde)
      return vigenciasUrbanasDisponibles.value.filter(year => year >= desde)
    })
    
    // Contadores para vigencias (solo cuentan los que están en el conjunto filtrado actual)
    const contadorVigenciaRural = computed(() => {
      return municipiosFiltradosAcumulativos.value.filter(m => {
        const info = infoAdminMap.value.get(m.cod_municipio)
        return info && info.vigencia_rural && !isNaN(parseInt(info.vigencia_rural))
      }).length
    })
    
    const contadorVigenciaUrbana = computed(() => {
      return municipiosFiltradosAcumulativos.value.filter(m => {
        const info = infoAdminMap.value.get(m.cod_municipio)
        return info && info.vigencia_urbana && !isNaN(parseInt(info.vigencia_urbana))
      }).length
    })
    
    // ========== FUNCIONES DE CARGA DE DATOS ==========
    
    // Función para filtrar municipios según permisos del usuario
    const filtrarMunicipiosPorPermisos = (municipiosData: any[]) => {
      if (isSuperAdmin.value || isAdmin.value) {
        return municipiosData; // Sin restricciones
      }
      
      if (isProfesional.value && municipiosPermitidos.value.length > 0) {
        return municipiosData.filter(m => 
          municipiosPermitidos.value.includes(m.cod_municipio)
        );
      }
      
      // Usuario público - puede ver todos
      return municipiosData;
    };

    // Cargar municipios con sistema acumulativo
    const cargarMunicipios = async () => {
      error.value = null
      
      try {
        cargando.value = true
        console.log('🔍 Cargando municipios con filtros acumulativos:', filtros.value)
        
        // Manejo de búsqueda
        if (filtros.value.busqueda && filtros.value.busqueda.trim() !== '') {
          console.log('🔍 Realizando búsqueda:', filtros.value.busqueda.trim())
          await realizarBusqueda()
          return
        }
        
        // Para filtros acumulativos, cargar todos los municipios si no los hay
        if (municipios.value.length === 0) {
          const municipiosData = await cargarTodosLosDatos(`${API_URL}/preoperacion/municipios/`)
          municipios.value = municipiosData
        }
        
        paginaActual.value = 1
        console.log(`✅ Filtros aplicados: ${municipiosFiltradosAcumulativos.value.length} municipios encontrados`)
        
      } catch (err) {
        console.error('Error al cargar municipios:', err)
        error.value = 'Error al cargar los municipios. Por favor, inténtelo de nuevo.'
      } finally {
        cargando.value = false
      }
    }
    
    // 🔥 NUEVA FUNCIÓN: Realizar búsqueda específica
    const realizarBusqueda = async () => {
      try {
        const terminoBusqueda = filtros.value.busqueda.trim()
        console.log('🔍 Término de búsqueda:', terminoBusqueda)
        
        // Estrategia múltiple de búsqueda
        let municipiosEncontrados: any[] = []
        
        // 1. Búsqueda por código exacto (si es numérico)
        if (/^\d+$/.test(terminoBusqueda)) {
          console.log('🔍 Búsqueda por código:', terminoBusqueda)
          try {
            const municipioEspecifico = await cargarTodosLosDatos(`${API_URL}/preoperacion/municipios/`, {
              cod_municipio: terminoBusqueda
            })
            if (municipioEspecifico.length > 0) {
              municipiosEncontrados = [...municipiosEncontrados, ...municipioEspecifico]
            }
          } catch (error) {
            console.log('No se encontró por código exacto')
          }
        }
        
        // 2. Búsqueda general con parámetro search
        try {
          console.log('🔍 Búsqueda general con search:', terminoBusqueda)
          const municipiosBusqueda = await cargarTodosLosDatos(`${API_URL}/preoperacion/municipios/`, {
            search: terminoBusqueda
          })
          if (municipiosBusqueda.length > 0) {
            municipiosEncontrados = [...municipiosEncontrados, ...municipiosBusqueda]
          }
        } catch (error) {
          console.log('Error en búsqueda general:', error)
        }
        
        // 3. Si no hay resultados, cargar todos y filtrar en cliente
        if (municipiosEncontrados.length === 0) {
          console.log('🔍 Búsqueda en cliente (fallback)')
          const todosMunicipios = await cargarTodosLosDatos(`${API_URL}/preoperacion/municipios/`)
          
          municipiosEncontrados = todosMunicipios.filter(m => {
            const codigoCoincide = m.cod_municipio.toString().includes(terminoBusqueda)
            const nombreCoincide = m.nom_municipio.toLowerCase().includes(terminoBusqueda.toLowerCase())
            return codigoCoincide || nombreCoincide
          })
        }
        
        // Eliminar duplicados por cod_municipio
        const municipiosUnicos = Array.from(
          new Map(municipiosEncontrados.map(m => [m.cod_municipio, m])).values()
        )
        
        // Aplicar filtros de permisos
        const municipiosFiltradosPermisos = filtrarMunicipiosPorPermisos(municipiosUnicos)
        
        municipios.value = municipiosFiltradosPermisos
        paginaActual.value = 1
        
        console.log(`✅ Búsqueda completada: ${municipios.value.length} municipios encontrados`)
        
        if (municipios.value.length === 0) {
          console.log('⚠️ No se encontraron municipios con el término:', terminoBusqueda)
        }
        
      } catch (error) {
        console.error('❌ Error en búsqueda:', error)
        error.value = 'Error al realizar la búsqueda. Inténtelo de nuevo.'
      }
    }
    
    // Función para cargar todos los datos con paginación
    const cargarTodosLosDatos = async (url: string, params = {}) => {
      let todosLosResultados = []
      let urlActual = url
      
      try {
        if (Object.keys(params).length > 0) {
          const queryParams = new URLSearchParams(params as any).toString()
          urlActual = `${url}?${queryParams}`
        }
        
        const token = localStorage.getItem('token')
        const config = token ? {
          headers: {
            'Authorization': `Token ${token}`
          }
        } : {}
        
        const primeraRespuesta = await axios.get(urlActual, config)
        
        if (Array.isArray(primeraRespuesta.data)) {
          return primeraRespuesta.data
        }
        
        if (primeraRespuesta.data.results) {
          todosLosResultados = [...primeraRespuesta.data.results]
          
          const count = primeraRespuesta.data.count || 0
          
          if (todosLosResultados.length >= count) {
            return todosLosResultados
          }
          
          const pageSize = primeraRespuesta.data.results.length
          const totalPages = Math.ceil(count / pageSize)
          
          const promesas = []
          for (let pagina = 2; pagina <= totalPages; pagina++) {
            let urlPagina = `${url}?page=${pagina}`
            
            if (Object.keys(params).length > 0) {
              const otrosParams = new URLSearchParams(params as any).toString()
              urlPagina = `${url}?${otrosParams}&page=${pagina}`
            }
            
            promesas.push(axios.get(urlPagina, config))
          }
          
          const respuestas = await Promise.all(promesas)
          
          respuestas.forEach(respuesta => {
            if (respuesta.data && respuesta.data.results) {
              todosLosResultados = [...todosLosResultados, ...respuesta.data.results]
            }
          })
        }
        
        return todosLosResultados
      } catch (error) {
        console.error(`Error cargando datos de ${url}:`, error)
        throw error
      }
    }
    
    // Cargar catálogos
    const cargarCatalogos = async () => {
      try {
        console.log('Cargando catálogos para filtros...')
        
        const deptosResult = await cargarTodosLosDatos(`${API_URL}/preoperacion/departamentos/`)
        departamentos.value = deptosResult
        
        const territorialesResult = await cargarTodosLosDatos(`${API_URL}/preoperacion/territoriales/`)
        territoriales.value = territorialesResult
        territorialesFiltradas.value = territorialesResult
        
        const mecanismosResult = await cargarTodosLosDatos(`${API_URL}/preoperacion/mecanismos-general/`)
        mecanismos.value = mecanismosResult
        mecanismosFiltrados.value = mecanismosResult
        
        const detallesResult = await cargarTodosLosDatos(`${API_URL}/preoperacion/mecanismos-detalle/`)
        detallesMecanismo.value = detallesResult
        detallesMecanismoFiltrados.value = detallesResult
        
        const gruposResult = await cargarTodosLosDatos(`${API_URL}/preoperacion/grupos/`)
        grupos.value = gruposResult
        gruposFiltrados.value = gruposResult
      } catch (err) {
        console.error('Error al cargar catálogos:', err)
        error.value = 'Error al cargar datos de referencia.'
      }
    }
    
    // Cargar profesionales
    const cargarProfesionales = async () => {
      try {
        const profesionalesData = await cargarTodosLosDatos(`${API_URL}/preoperacion/profesionales-seguimiento/`);
        
        const profesionalesFormateados = profesionalesData.map(prof => {
          const nuevoProf = { ...prof };
          if (!nuevoProf.nombre_profesional) {
            if (nuevoProf.nombre) {
              nuevoProf.nombre_profesional = nuevoProf.nombre;
            } else {
              nuevoProf.nombre_profesional = nuevoProf.cod_profesional || 'Profesional sin nombre';
            }
          }
          return nuevoProf;
        });
        
        profesionales.value = profesionalesFormateados;
        profesionalesFiltrados.value = profesionalesFormateados;
      } catch (error) {
        console.error('Error al cargar profesionales:', error);
      }
    };

    const cargarRelacionesProfesionales = async () => {
      try {
        console.log('🔄 Cargando relaciones de profesionales...')
        
        const [
          profesionalMunicipioData,
          profesionalTerritorialData
        ] = await Promise.all([
          cargarTodosLosDatos(`${API_URL}/preoperacion/profesional-municipio/`),
          cargarTodosLosDatos(`${API_URL}/preoperacion/profesional-territorial/`)
        ])
        
        profesionalMunicipio.value = profesionalMunicipioData
        profesionalTerritorial.value = profesionalTerritorialData
        
        console.log('✅ Relaciones cargadas:', {
          profesional_municipio: profesionalMunicipio.value.length,
          profesional_territorial: profesionalTerritorial.value.length
        })
        
      } catch (error) {
        console.error('❌ Error cargando relaciones de profesionales:', error)
      }
    }
    
    // NUEVA FUNCIÓN: Cargar información administrativa
    const cargarInfoAdministrativa = async () => {
      try {
        console.log('📊 Cargando información administrativa...')
        const infoData = await cargarTodosLosDatos(`${API_URL}/preoperacion/info-administrativa/`)
        infoAdministrativa.value = infoData

        // Crear un mapa para acceso rápido por cod_municipio
        // IMPORTANTE: Cuando hay múltiples registros para un municipio,
        // se guarda el que tenga la vigencia más reciente
        infoAdminMap.value = new Map()
        infoData.forEach(info => {
          if (info.cod_municipio) {
            const existente = infoAdminMap.value.get(info.cod_municipio)

            if (!existente) {
              // Si no existe, simplemente agregar
              infoAdminMap.value.set(info.cod_municipio, info)
            } else {
              // Si ya existe, comparar vigencias y quedarse con la más reciente
              const vigenciaExistenteRural = parseInt(existente.vigencia_rural) || 0
              const vigenciaExistenteUrbana = parseInt(existente.vigencia_urbana) || 0
              const vigenciaNuevaRural = parseInt(info.vigencia_rural) || 0
              const vigenciaNuevaUrbana = parseInt(info.vigencia_urbana) || 0

              // Usar la mayor vigencia entre rural y urbana para comparar
              const maxVigenciaExistente = Math.max(vigenciaExistenteRural, vigenciaExistenteUrbana)
              const maxVigenciaNueva = Math.max(vigenciaNuevaRural, vigenciaNuevaUrbana)

              // Si la nueva vigencia es mayor, reemplazar
              if (maxVigenciaNueva > maxVigenciaExistente) {
                infoAdminMap.value.set(info.cod_municipio, info)
              }
            }
          }
        })

        console.log('✅ Info administrativa cargada:', infoData.length, 'registros')
        console.log('📋 Municipios únicos con info administrativa:', infoAdminMap.value.size)
      } catch (error) {
        console.error('❌ Error cargando info administrativa:', error)
      }
    }
    
    // ========== FUNCIONES DE FILTROS SIMPLIFICADAS PARA SISTEMA ACUMULATIVO ==========
    
    const actualizarFiltrosDepartamento = async () => {
      await cargarMunicipios()
    }
    
    const actualizarFiltrosTerritorial = async () => {
      await cargarMunicipios()
    }
    
    const actualizarFiltrosMunicipio = async () => {
      await cargarMunicipios()
    }
    
    const actualizarFiltrosMecanismo = async () => {
      await cargarMunicipios()
    }
    
    const actualizarFiltrosMecanismoDetalle = async () => {
      await cargarMunicipios()
    }
    
    const actualizarFiltrosGrupo = async () => {
      await cargarMunicipios()
    }
    
    const actualizarFiltroRolProfesional = async () => {
      // Limpiar profesional específico cuando cambia el rol
      filtros.value.profesional = '';
      
      // Si no hay rol seleccionado, recargar municipios normalmente
      if (!filtros.value.rolProfesional) {
        await cargarMunicipios();
        return;
      }
      
      // Si hay rol seleccionado, recargar municipios (que aplicará el filtro automáticamente)
      profesionalesFiltrados.value = profesionales.value.filter(prof => {
        if (!prof) return false;
        
        try {
          let rolText = '';
          
          if (typeof prof.rol_profesional === 'string') {
            rolText = prof.rol_profesional;
          } else if (prof.rol_profesional && typeof prof.rol_profesional === 'object') {
            if (prof.rol_profesional.rol_profesional) {
              rolText = prof.rol_profesional.rol_profesional;
            }
          }
          
          const rolUpper = rolText.toUpperCase();
          const rolBuscado = filtros.value.rolProfesional.toUpperCase();
          
          return rolUpper.includes(rolBuscado);
        } catch (error) {
          return false;
        }
      });
      
      await cargarMunicipios(); // 🔥 CAMBIAR ESTA LÍNEA: era municipios.value = [];
    };
    
    const actualizarFiltroProfesional = async () => {
      if (!filtros.value.profesional) {
        await cargarMunicipios();
        return;
      }
      
      await cargarMunicipios();
    };
    
    const actualizarFiltros = async () => {
      await cargarMunicipios()
    }
    
    // ========== FUNCIONES DE BÚSQUEDA ==========
    
    const busquedaInmediata = () => {
      console.log('🔍 Búsqueda inmediata activada:', filtros.value.busqueda)
      cargarMunicipios()
    }
    
    const limpiarBusqueda = () => {
      console.log('🔍 Limpiando búsqueda')
      filtros.value.busqueda = ''
      cargarMunicipios()
    }
    
    // ========== FUNCIONES DE UTILIDAD ==========
    
    // Función mejorada para obtener nombre del departamento
    const obtenerNombreDepartamento = (municipio: any): string => {
      if (!municipio) return 'N/A'
      
      // Si el departamento está anidado completo
      if (municipio.cod_depto && municipio.cod_depto.nom_depto) {
        return municipio.cod_depto.nom_depto
      }
      
      // Si el departamento está en departamento_info
      if (municipio.departamento_info && municipio.departamento_info.nom_depto) {
        return municipio.departamento_info.nom_depto
      }
      
      // Si hay un cod_depto pero no está el objeto anidado, buscarlo en la lista
      if (municipio.cod_depto) {
        if (typeof municipio.cod_depto === 'object' && municipio.cod_depto !== null) {
          const depto = departamentos.value.find(d => 
            d.cod_depto.toString() === municipio.cod_depto.cod_depto.toString());
          return depto ? depto.nom_depto : 'N/A';
        }
        
        if (typeof municipio.cod_depto === 'number' || (typeof municipio.cod_depto === 'string' && !isNaN(municipio.cod_depto))) {
          const depto = departamentos.value.find(d => 
            d.cod_depto.toString() === municipio.cod_depto.toString());
          return depto ? depto.nom_depto : 'N/A';
        }
      }
      
      return 'N/A'
    }
    
    const formatFecha = (fecha: any) => {
      if (!fecha) return 'No definida'
      
      try {
        const fechaObj = new Date(fecha)
        return format(fechaObj, 'dd/MM/yyyy', { locale: es })
      } catch (error) {
        return fecha
      }
    }
    
    // NUEVAS FUNCIONES HELPER PARA VIGENCIAS
    const obtenerVigenciaRural = (cod_municipio: number): string => {
      const info = infoAdminMap.value.get(cod_municipio)
      return info?.vigencia_rural || 'N/D'
    }
    
    const obtenerVigenciaUrbana = (cod_municipio: number): string => {
      const info = infoAdminMap.value.get(cod_municipio)
      return info?.vigencia_urbana || 'N/D'
    }
    
    const obtenerInfoAdministrativa = (cod_municipio: number) => {
      return infoAdminMap.value.get(cod_municipio) || null
    }
    
    // NUEVAS FUNCIONES DE FORMATEO
    const formatNumber = (value: string | number | undefined): string => {
      if (!value) return '0'
      const num = typeof value === 'string' ? parseFloat(value.replace(/\./g, '').replace(',', '.')) : value
      if (isNaN(num)) return value.toString()
      return new Intl.NumberFormat('es-CO').format(num)
    }
    
    const formatCurrency = (value: string | undefined): string => {
      if (!value) return '$0'
      // Remover puntos y convertir a número
      const num = parseFloat(value.replace(/\./g, '').replace(',', '.'))
      if (isNaN(num)) return value
      return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(num)
    }
    
    // ========== FUNCIONES DE ACCIONES ==========
    
    const verDetalleMunicipio = async (municipio: any) => {
      try {
        console.log('👀 Viendo detalles del municipio:', municipio.cod_municipio);
        
        // Obtener información administrativa (mantener para compatibilidad)
        const infoAdmin = obtenerInfoAdministrativa(municipio.cod_municipio)
        
        // 🆕 NUEVO: Obtener TODOS los registros de información administrativa
        const todosInfoAdmin = await getTodosInfoAdministrativaPorMunicipio(municipio.cod_municipio)
        
        console.log('📊 Registros de info administrativa encontrados:', todosInfoAdmin.length);
        
        modalDetalle.value.municipio = municipio
        modalDetalle.value.infoAdmin = infoAdmin  // Mantener para compatibilidad
        modalDetalle.value.todosInfoAdmin = todosInfoAdmin  // 🆕 NUEVO
        modalDetalle.value.tabActiva = 0  // 🆕 NUEVO: resetear a primera pestaña
        modalDetalle.value.mostrar = true
        mostrarDetalleCompleto.value = false
        
        // Cargar centros poblados del municipio
        await cargarCentrosPoblados(municipio.cod_municipio)
        
      } catch (error) {
        console.error('❌ Error al ver detalles del municipio:', error);
        alert('Error al cargar los detalles del municipio');
      }
    }

    // 🆕 NUEVA FUNCIÓN: Cambiar pestaña activa
    const cambiarTabInfoAdmin = (index: number) => {
      modalDetalle.value.tabActiva = index
      // Actualizar infoAdmin para compatibilidad con el resto del código
      if (modalDetalle.value.todosInfoAdmin[index]) {
        modalDetalle.value.infoAdmin = modalDetalle.value.todosInfoAdmin[index]
      }
    }
    
    // ========== FUNCIONES DE PAGINACIÓN Y ORDENACIÓN ==========
    
    const municipiosTabla = computed(() => {
      return municipiosFiltradosAcumulativos.value
    })
    
    const municipiosVisibles = computed(() => {
      const inicio = (paginaActual.value - 1) * elementosPorPagina.value
      const fin = inicio + elementosPorPagina.value
      return municipiosTabla.value.slice(inicio, fin)
    })
    
    const totalPaginas = computed(() => {
      return Math.ceil(municipiosTabla.value.length / elementosPorPagina.value) || 1
    })
    
    const botonesNumericos = computed(() => {
      const botones = []
      const maxBotones = 5
      
      if (totalPaginas.value <= maxBotones) {
        for (let i = 1; i <= totalPaginas.value; i++) {
          botones.push({
            valor: i,
            texto: i.toString(),
            activo: i === paginaActual.value,
            ellipsis: false
          })
        }
      } else {
        // Lógica simplificada de paginación
        botones.push({
          valor: 1,
          texto: '1',
          activo: paginaActual.value === 1,
          ellipsis: false
        })
        
        let inicio = Math.max(2, paginaActual.value - 1)
        let fin = Math.min(totalPaginas.value - 1, paginaActual.value + 1)
        
        if (paginaActual.value <= 3) {
          fin = Math.min(4, totalPaginas.value - 1)
        }
        
        if (paginaActual.value >= totalPaginas.value - 2) {
          inicio = Math.max(2, totalPaginas.value - 3)
        }
        
        if (inicio > 2) {
          botones.push({
            valor: null,
            texto: '...',
            activo: false,
            ellipsis: true
          })
        }
        
        for (let i = inicio; i <= fin; i++) {
          botones.push({
            valor: i,
            texto: i.toString(),
            activo: i === paginaActual.value,
            ellipsis: false
          })
        }
        
        if (fin < totalPaginas.value - 1) {
          botones.push({
            valor: null,
            texto: '...',
            activo: false,
            ellipsis: true
          })
        }
        
        if (totalPaginas.value > 1) {
          botones.push({
            valor: totalPaginas.value,
            texto: totalPaginas.value.toString(),
            activo: paginaActual.value === totalPaginas.value,
            ellipsis: false
          })
        }
      }
      
      return botones
    })
    
    const cambiarPagina = (pagina: number) => {
      if (pagina >= 1 && pagina <= totalPaginas.value) {
        paginaActual.value = pagina
      }
    }
    
    const ordenarPor = (campo: string) => {
      if (ordenacion.value.campo === campo) {
        ordenacion.value.ascendente = !ordenacion.value.ascendente
      } else {
        ordenacion.value.campo = campo
        ordenacion.value.ascendente = true
      }
      
      municipios.value.sort((a, b) => {
        let valorA, valorB
        
        if (campo.includes('.')) {
          const [parentKey, childKey] = campo.split('.')
          valorA = a[parentKey]?.[childKey] || ''
          valorB = b[parentKey]?.[childKey] || ''
        } else {
          valorA = a[campo] || ''
          valorB = b[campo] || ''
        }
        
        if (typeof valorA === 'string' && typeof valorB === 'string') {
          return ordenacion.value.ascendente 
            ? valorA.localeCompare(valorB) 
            : valorB.localeCompare(valorA)
        } else {
          return ordenacion.value.ascendente 
            ? (valorA > valorB ? 1 : -1)
            : (valorB > valorA ? 1 : -1)
        }
      })
    }
    
    
    // ========== FUNCIONES DE FILTROS FINALES ==========
    
    const aplicarFiltros = () => {
      paginaActual.value = 1
      cargarMunicipios()
    }
    
    const limpiarFiltros = () => {
      console.log('🧹 Limpiando TODOS los filtros incluyendo búsqueda...')
      
      // Limpiar TODOS los filtros
      filtros.value = {
        departamento: '',
        territorial: '',
        municipio: '',
        mecanismo: '',
        mecanismoDetalle: '',
        grupo: '',
        estadoFecha: '',
        busqueda: '',                    
        profesional: '',
        rolProfesional: '',
        vigenciaRuralDesde: '',
        vigenciaRuralHasta: '',
        vigenciaUrbanaDesde: '',
        vigenciaUrbanaHasta: ''
      }
      
      // ✅ CLAVE: Limpiar el array de municipios para forzar recarga completa
      municipios.value = []
      
      // Resetear las listas filtradas
      territorialesFiltradas.value = [...territoriales.value]
      mecanismosFiltrados.value = [...mecanismos.value]
      detallesMecanismoFiltrados.value = [...detallesMecanismo.value]
      gruposFiltrados.value = [...grupos.value]
      municipiosFiltrados.value = []
      profesionalesFiltrados.value = [...profesionales.value]
      
      // Resetear paginación
      paginaActual.value = 1
      
      // Recargar municipios (ahora cargará TODOS porque municipios.value está vacío)
      cargarMunicipios()
    }

    const limpiarFiltroEspecifico = (filtro: string) => {
      console.log(`🧹 Limpiando filtro específico: ${filtro}`)
      filtros.value[filtro] = ''
      cargarMunicipios()
    }
    
    const limpiarFiltroVigencia = (tipo: 'rural' | 'urbana') => {
      console.log(`🧹 Limpiando filtro de vigencia ${tipo}`)
      if (tipo === 'rural') {
        filtros.value.vigenciaRuralDesde = ''
        filtros.value.vigenciaRuralHasta = ''
      } else {
        filtros.value.vigenciaUrbanaDesde = ''
        filtros.value.vigenciaUrbanaHasta = ''
      }
      cargarMunicipios()
    }

    const obtenerNombreFiltro = (tipo: string, valor: string): string => {
      switch (tipo) {
        case 'departamento':
          const depto = departamentos.value.find(d => d.cod_depto.toString() === valor)
          return depto ? depto.nom_depto : valor
        case 'territorial':
          return valor
        case 'municipio':
          const municipio = municipios.value.find(m => m.cod_municipio.toString() === valor)
          return municipio ? municipio.nom_municipio : valor
        case 'mecanismo':
          return valor
        case 'mecanismoDetalle':
          return valor
        case 'grupo':
          const grupo = grupos.value.find(g => g.cod_grupo === valor)
          return grupo ? (grupo.descripcion || grupo.cod_grupo) : valor
        case 'profesional':
          const prof = profesionales.value.find(p => p.cod_profesional === valor)
          return prof ? prof.nombre_profesional : valor
        case 'rolProfesional':
          return valor
        case 'estadoFecha':
          return valor === 'con_fecha' ? 'Con fecha' : 'Sin fecha'
        default:
          return valor
      }
    }
    
    const obtenerRangoVigencia = (tipo: 'rural' | 'urbana'): string => {
      const desde = tipo === 'rural' ? filtros.value.vigenciaRuralDesde : filtros.value.vigenciaUrbanaDesde
      const hasta = tipo === 'rural' ? filtros.value.vigenciaRuralHasta : filtros.value.vigenciaUrbanaHasta
      
      if (desde && hasta) {
        return `${desde} - ${hasta}`
      } else if (desde) {
        return `Desde ${desde}`
      } else if (hasta) {
        return `Hasta ${hasta}`
      }
      return ''
    }
    
    // Exportar datos ACTUALIZADO
    const exportarDatos = () => {
      try {
        if (!municipiosTabla.value || municipiosTabla.value.length === 0) {
          alert('No hay datos para exportar');
          return;
        }
        
        const headers = [
          'Código',
          'Municipio',
          'Departamento',
          'Territorial',
          'Área',
          'Mecanismo General',
          'Grupo',
          'Fecha Inicio',
          'Vigencia Rural',  // Nueva columna
          'Vigencia Urbana'  // Nueva columna
        ];
        
        const rows = municipiosTabla.value.map(m => [
          m.cod_municipio,
          m.nom_municipio,
          obtenerNombreDepartamento(m),
          m.nom_territorial || '',
          m.area || '',
          m.mecanismo_general || '',
          m.grupo || '',
          formatFecha(m.fecha_inicio),
          obtenerVigenciaRural(m.cod_municipio),    // Nueva columna
          obtenerVigenciaUrbana(m.cod_municipio)    // Nueva columna
        ]);
        
        const BOM = '\uFEFF';
        const csvContent = BOM + [
          headers.join(','),
          ...rows.map(row => row.map(cell => 
            `"${(cell !== null && cell !== undefined ? String(cell) : '').replace(/"/g, '""')}"`
          ).join(','))
        ].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `municipios_disposicion_${new Date().toISOString().slice(0, 10)}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        alert('Archivo CSV generado correctamente');
        
      } catch (err) {
        console.error('Error al exportar datos:', err);
        alert(`Error al exportar datos: ${err.message}`);
      }
    }
    
    // Función auxiliar que falta
    const getMunicipioById = async (id: number) => {
      try {
        const response = await api.get(`/preoperacion/municipios/${id}/`);
        return response.data || response;
      } catch (error) {
        console.error(`Error al obtener municipio ${id}:`, error);
        throw error;
      }
    };
    // Watch para aplicar automáticamente búsqueda desde URL
    watch(
      () => route.query,
      (newQuery) => {
        // Si viene un parámetro de búsqueda y el flag autoSearch
        if (newQuery.busqueda && newQuery.autoSearch === 'true') {
          console.log('🔍 Aplicando búsqueda automática desde URL:', newQuery.busqueda)
          
          // Aplicar el término de búsqueda
          filtros.value.busqueda = newQuery.busqueda as string
          
          // Ejecutar la búsqueda
          cargarMunicipios()
          
          // Limpiar el parámetro autoSearch de la URL para evitar que se ejecute nuevamente
          // al navegar back/forward
          router.replace({
            path: route.path,
            query: { 
              ...route.query, 
              autoSearch: undefined 
            }
          })
        }
      },
      { immediate: true } // Ejecutar inmediatamente al montar el componente
    )
    // Inicialización ACTUALIZADA
      onMounted(async () => {
        try {
          await Promise.all([
            cargarCatalogos(),
            cargarProfesionales(),
            cargarRelacionesProfesionales(),
            cargarInfoAdministrativa()
          ])
          
          // Solo cargar municipios si no hay búsqueda pendiente desde la URL
          if (!route.query.busqueda || route.query.autoSearch !== 'true') {
            await cargarMunicipios()
          }
        } catch (err) {
          console.error('Error al cargar datos iniciales:', err)
          error.value = 'Error al cargar datos iniciales. Por favor, actualice la página.'
        }
      })

    // ============= RETURN STATEMENT COMPLETO =============
    
    return {
      // Estado y datos
      cargando,
      cargandoFiltros,
      error,
      municipios,
      municipiosTabla,
      municipiosVisibles,
      municipiosFiltrados,
      departamentos,
      territoriales,
      territorialesFiltradas,
      mecanismos,
      mecanismosFiltrados,
      detallesMecanismo,
      detallesMecanismoFiltrados,
      grupos,
      gruposFiltrados,
      profesionales,
      profesionalesFiltrados,
      infoAdministrativa,
      infoAdminMap,
      mostrarDetalleCompleto,
      
      // Permisos y roles
      isSuperAdmin,
      isAdmin,
      isProfesional,
      municipiosPermitidos,
      accessLevelText,
      accessLevelIcon,
      accessLevelClass,
      
      // Filtros y ordenación
      filtros,
      ordenacion,
      
      // Paginación
      paginaActual,
      totalPaginas,
      botonesNumericos,
      
      // Modal
      modalDetalle,
      
      // Métodos principales
      cargarMunicipios,
      realizarBusqueda,
      actualizarFiltrosDepartamento,
      actualizarFiltrosTerritorial,
      actualizarFiltrosMunicipio,
      actualizarFiltrosMecanismo,
      actualizarFiltrosMecanismoDetalle,
      actualizarFiltrosGrupo,
      actualizarFiltroRolProfesional,
      actualizarFiltroProfesional,
      aplicarFiltros,
      limpiarFiltros,
      ordenarPor,
      cambiarPagina,
      formatFecha,
      obtenerNombreDepartamento,
      verDetalleMunicipio,
      exportarDatos,
      busquedaInmediata,
      limpiarBusqueda,
      actualizarFiltros,
      cargarInfoAdministrativa,
      obtenerVigenciaRural,
      obtenerVigenciaUrbana,
      obtenerInfoAdministrativa,
      formatNumber,
      formatCurrency,

      // NUEVOS COMPUTED DINÁMICOS ACUMULATIVOS
      departamentosDisponibles,
      municipiosFiltradosDinamicos,
      territorialesFitradasDinamicas,
      profesionalesFiltradosDinamicos,
      mecanismosFiltradosDinamicos,
      detallesMecanismoFiltradosDinamicos,
      gruposFiltradosDinamicos,
      rolesProfesionalesFiltradosDinamicos,
      hayFiltrosActivos,
      
      // NUEVOS MÉTODOS
      limpiarFiltroEspecifico,
      limpiarFiltroVigencia,
      obtenerNombreFiltro,
      obtenerRangoVigencia,
      cargarRelacionesProfesionales,
      profesionalesDisponibles: profesionalesFiltradosDinamicos,
      mecanismosDisponibles: mecanismosFiltradosDinamicos,
      detallesMecanismoDisponibles: detallesMecanismoFiltradosDinamicos,
      gruposDisponibles: gruposFiltradosDinamicos,
      rolesDisponibles: rolesProfesionalesFiltradosDinamicos,
      territorialesDisponibles: territorialesFitradasDinamicas,
      municipiosDisponibles: municipiosFiltradosDinamicos,
      
      // Contadores de vigencias
      contadorVigenciaRural,
      contadorVigenciaUrbana,
      
      // NUEVOS COMPUTED PARA VIGENCIAS
      vigenciasRuralesDisponibles,
      vigenciasUrbanasDisponibles,
      vigenciasRuralesHastaDisponibles,
      vigenciasUrbanasHastaDisponibles,

      centrosPoblados,
      cargandoCentrosPoblados,
      errorCentrosPoblados,
      cambiarTabInfoAdmin,
      route, 

    }
  }
})
</script>

<style scoped>

.registro-counter {
  color: #6c757d;
  font-size: 0.85rem;
  font-weight: normal;
  background-color: #f8f9fa;
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
  border: 1px solid #e9ecef;
  margin-left: 0.5rem;
}

/* Contenedor de pestañas */
.tabs-container {
  margin: 1rem 0;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
}

.tabs-header {
  display: flex;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  overflow-x: auto;
  scrollbar-width: thin;
}

.tabs-header::-webkit-scrollbar {
  height: 4px;
}

.tabs-header::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.tabs-header::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

/* Botones de pestañas */
.tab-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 160px;
  padding: 1rem 0.75rem;
  background: none;
  border: none;
  border-right: 1px solid #dee2e6;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.85rem;
  font-weight: 500;
  color: #6c757d;
  text-align: center;
  gap: 0.25rem;
}

.tab-button:last-child {
  border-right: none;
}

.tab-button:hover {
  background-color: #e9ecef;
  color: #495057;
}

.tab-button.active {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  position: relative;
}

.tab-button.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-bottom: 8px solid white;
}

.tab-button i {
  font-size: 1.2rem;
  margin-bottom: 0.25rem;
}

/* Vigencias en las pestañas */
.tab-vigencias {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.25rem;
  flex-wrap: wrap;
  justify-content: center;
}

.vigencia-rural,
.vigencia-urbana {
  font-size: 0.7rem;
  padding: 0.15rem 0.4rem;
  border-radius: 8px;
  font-weight: 600;
  line-height: 1;
}

.vigencia-rural {
  background-color: rgba(40, 167, 69, 0.2);
  color: #155724;
}

.tab-button.active .vigencia-rural {
  background-color: rgba(255, 255, 255, 0.3);
  color: white;
}

.vigencia-urbana {
  background-color: rgba(255, 193, 7, 0.2);
  color: #856404;
}

.tab-button.active .vigencia-urbana {
  background-color: rgba(255, 255, 255, 0.3);
  color: white;
}

/* Contenido de las pestañas */
.tab-content {
  background-color: white;
  padding: 1.5rem;
  border-radius: 0 0 8px 8px;
  animation: fadeInTab 0.3s ease-out;
}

@keyframes fadeInTab {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Mensaje cuando no hay información */
.no-info-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  color: #6c757d;
  margin-top: 1rem;
  border: 1px dashed #dee2e6;
}

.no-info-message i {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: #adb5bd;
}

.no-info-message p {
  margin: 0;
  font-size: 1rem;
  text-align: center;
}

/* =============== ESTILOS PARA CENTROS POBLADOS =============== */
.centros-loading, 
.centros-error, 
.centros-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  color: #6c757d;
  margin-top: 1rem;
}

.centros-error {
  background-color: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(0, 123, 255, 0.1);
  border-left-color: #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.centros-table-container {
  margin-top: 1rem;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #dee2e6;
  background-color: #fff;
}

.centros-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.centros-table th {
  background-color: #f8f9fa;
  color: #495057;
  font-weight: 600;
  padding: 1rem 0.75rem;
  text-align: left;
  border-bottom: 2px solid #dee2e6;
}

.centros-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #dee2e6;
  vertical-align: middle;
}

.centros-table tbody tr:nth-child(even) {
  background-color: rgba(0, 0, 0, 0.02);
}

.centros-table tbody tr:hover {
  background-color: rgba(0, 123, 255, 0.05);
}

.codigo-centro {
  font-family: 'Courier New', monospace;
  font-weight: 600;
  color: #007bff;
  min-width: 120px;
}

.nombre-centro {
  font-weight: 500;
  color: #495057;
}

.area-centro {
  text-align: right;
  font-weight: 500;
  color: #28a745;
  min-width: 100px;
}



/* Agregar estos estilos al final de tu sección <style scoped> */

/* Modal mejorado con scroll */
.modal-dialog {
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-content {
  display: flex;
  flex-direction: column;
  max-height: 85vh;
  overflow: hidden;
}

.modal-header {
  flex-shrink: 0;
  position: relative;
  z-index: 10;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  max-height: calc(85vh - 120px); /* Resta header y footer */
  padding: 1.5rem;
}

.modal-footer {
  flex-shrink: 0;
  border-top: 1px solid #dee2e6;
  background-color: #f8f9fa;
}

/* Info grid responsive */
.info-grid {
  display: block; /* Cambiar de grid a block para mejor scroll */
}

.info-section {
  margin-bottom: 2rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.info-section:last-child {
  margin-bottom: 0;
}

/* Hacer el botón de cerrar más visible */
.close-button {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.9);
  width: 36px;
  height: 36px;
  font-size: 24px;
  z-index: 20;
}

.close-button:hover {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* Ajustar tamaños en móviles */
@media (max-width: 768px) {

}

/* ============= ESTILOS CSS COMPLETOS ============= */
/* Agregar estos estilos adicionales */
.info-subsection {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.info-subsection:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.info-subsection h6 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-actions {
  margin: 1rem 0;
  text-align: center;
}

.info-detalle-completo {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 2px solid #e9ecef;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.info-field .value.highlight {
  font-weight: 600;
  color: #007bff;
  font-size: 1.1rem;
}

.vigencia-desactualizada {
  color: #dc3545 !important;
  font-weight: 600;
}

.estado-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 600;
}

.estado-desactualizado {
  background-color: #f8d7da;
  color: #721c24;
}

.info-field-full {
  margin-top: 0.5rem;
}

.observacion-text {
  background-color: #f8f9fa;
  padding: 0.75rem;
  border-radius: 4px;
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.5;
  color: #495057;
}

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
}
.contador-opciones {
  color: #6c757d;
  font-size: 0.75rem;
  font-weight: normal;
  background-color: #f8f9fa;
  padding: 0.15rem 0.4rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  margin-left: 0.5rem;
}

/* Campos con selección */
.form-control.has-selection {
  border-color: #007bff;
  background-color: #f0f8ff;
  font-weight: 500;
}

/* Botones para limpiar filtros específicos */
.form-group {
  position: relative;
}

.btn-limpiar-filtro {
  position: absolute;
  right: 8px;
  top: 34px;
  background: #00bfff; /* Azul claro neón */
  color: white; /* O puedes usar #ffffff para mayor contraste */
  border: none;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  z-index: 10;
}

.btn-limpiar-filtro:hover {
  background: #007acc; /* Azul más oscuro */
  transform: scale(1.15); /* Crece un poco más */
  box-shadow: 0 0 10px rgba(0, 191, 255, 0.6); /* Añade un "glow" azul neón */
}

/* Sección de filtros activos */
.filtros-activos {
  margin-top: 1.5rem;
  padding: 1rem;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 8px;
  border-left: 4px solid #28a745;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.filtros-activos h4 {
  margin: 0 0 0.75rem;
  font-size: 1rem;
  color: #343a40;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tags-filtros {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag-filtro {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  animation: fadeIn 0.3s ease-out;
  transition: all 0.2s;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.tag-filtro:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

/* Colores específicos para cada tipo de filtro */
.tag-filtro.departamento {
  background: linear-gradient(135deg, #f39c12, #d68910);
  color: white;
}

.tag-filtro.territorial {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  color: white;
}

.tag-filtro.municipio {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
}

.tag-filtro.rol {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
}

.tag-filtro.profesional {
  background: linear-gradient(135deg, #9b59b6, #8e44ad);
  color: white;
}

.tag-filtro.mecanismo {
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
}

.tag-filtro.detalle {
  background: linear-gradient(135deg, #fd7e14, #e85d04);
  color: white;
}

.tag-filtro.grupo {
  background: linear-gradient(135deg, #20c997, #198754);
  color: white;
}

.tag-filtro.estado {
  background: linear-gradient(135deg, #6f42c1, #5a2d91);
  color: white;
}

.tag-filtro.vigencia-rural {
  background: linear-gradient(135deg, #13795b, #0d6e50);
  color: white;
}

.tag-filtro.vigencia-urbana {
  background: linear-gradient(135deg, #ff6b00, #e85d04);
  color: white;
}

.tag-filtro button {
  background: rgba(255, 255, 255, 0.3);
  border: none;
  color: inherit;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0;
  margin-left: 0.25rem;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.tag-filtro button:hover {
  background: rgba(255, 255, 255, 0.5);
  transform: scale(1.1);
}

/* Estilos para el rango de vigencias */
.rango-vigencia {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
}

.select-year {
  width: 120px;
  text-align: center;
}

.separador-rango {
  color: #6c757d;
  font-weight: 600;
}

.btn-limpiar-rango {
  position: static;
  margin-left: 0.5rem;
}

/* Responsive para los rangos de vigencia */
@media (max-width: 768px) {
  .rango-vigencia {
    flex-wrap: wrap;
  }
  
  .select-year {
    width: calc(50% - 1rem);
  }
  
  .separador-rango {
    width: 100%;
    text-align: center;
    margin: 0.25rem 0;
  }
  
  .btn-limpiar-rango {
    position: absolute;
    right: 0;
    top: 0;
  }
}

/* Resto de estilos del componente */
.municipios-disposicion-container {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-size: 1.6rem;
  color: #333;
  margin: 0;
}

.info-section {

  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.access-info-header {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.access-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
}

.access-total {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
}

.access-admin {
  background: linear-gradient(135deg, #f39c12, #d68910);
  color: white;
}

.access-profesional {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  color: white;
}

.access-publico {
  background: linear-gradient(135deg, #95a5a6, #7f8c8d);
  color: white;
}

.scope-info {
  font-size: 0.75rem;
  color: #6c757d;
  text-align: right;
}

.actions-bar {
  display: flex;
  gap: 0.75rem;
}

.btn-export {
  color: #fff;
  background-color: #28a745;
  border-color: #28a745;
  font-size: 1rem;
  padding: 0.5rem 1.25rem;
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
  line-height: 1.5;
  border-radius: 4px;
  transition: all 0.15s ease-in-out;
  cursor: pointer;
}

.btn-export:hover:not(:disabled) {
  background-color: #218838;
  border-color: #1e7e34;
}

.btn-export:disabled {
  background-color: #6c757d;
  border-color: #6c757d;
  opacity: 0.65;
  cursor: not-allowed;
}

/* Estilos para la barra de búsqueda principal */
.search-section {
  background-color: white;
  border-radius: 8px;
  padding: 1rem 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.search-input-container {
  position: relative;
  display: flex;
  align-items: center;
  max-width: 500px;
}

.search-icon {
  position: absolute;
  left: 1rem;
  color: #6c757d;
  z-index: 1;
  font-size: 1.2rem;
}

.search-input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  font-size: 1rem;
  line-height: 1.5;
  color: #495057;
  background-color: #fff;
  border: 2px solid #ced4da;
  border-radius: 25px;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.search-input:focus {
  border-color: #007bff;
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.clear-search-btn {
  position: absolute;
  right: 0.5rem;
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.clear-search-btn:hover {
  background-color: #f8f9fa;
  color: #495057;
}

/* Botones de acción sin descarga */
.action-buttons {
  display: flex;
  gap: 0.4rem;
  justify-content: center;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 4px;
  border: none;
  padding: 0;
  cursor: pointer;
  transition: all 0.2s;
  color: white;
  text-decoration: none !important;
}

.view-btn {
  background-color: #007bff;
}

.view-btn:hover {
  background-color: #0062cc;
}

.insumos-btn {
  background-color: #17a2b8;
  color: white !important;
}

.insumos-btn:hover {
  background-color: #138496;
  color: white !important;
}

/* Resto de estilos copiados del original */
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

.col-md-6, .col-lg-3, .col-lg-4, .col-lg-6, .col-lg-8 {
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
  
  .col-lg-4 {
    flex: 0 0 33.333333%;
    max-width: 33.333333%;
  }
  
  .col-lg-6 {
    flex: 0 0 50%;
    max-width: 50%;
  }
  
  .col-lg-8 {
    flex: 0 0 66.666667%;
    max-width: 66.666667%;
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
  cursor: not-allowed;
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
  text-decoration: none;
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

.btn-info {
  color: #fff;
  background-color: #17a2b8;
  border-color: #17a2b8;
}

.btn-info:hover {
  color: #fff;
  background-color: #138496;
  border-color: #117a8b;
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

.no-access-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  padding: 2rem;
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  color: #856404;
}

.no-access-message i {
  font-size: 3rem;
  color: #f39c12;
}

.no-access-message p {
  margin: 0;
  text-align: center;
  font-weight: 500;
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

.results-summary {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.results-count {
  color: #6c757d;
  font-size: 0.9rem;
}

.scope-indicator {
  font-size: 0.8rem;
  color: #6c757d;
  font-style: italic;
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
  font-size: 0.85rem;
}

.table th,
.table td {
  padding: 0.6rem 0.4rem;
  vertical-align: top;
  border-top: 1px solid #dee2e6;
}

.table thead th {
  vertical-align: bottom;
  border-bottom: 2px solid #dee2e6;
  font-weight: 600;
  background-color: #f8f9fa;
  position: relative;
  white-space: nowrap;
}

.table thead th.sortable {
  cursor: pointer;
  user-select: none;
}

.table thead th.sortable:hover {
  background-color: #e9ecef;
}

.table thead th i {
  font-size: 1rem;
  vertical-align: middle;
  margin-left: 0.25rem;
}

.th-codigo { width: 70px; }
.th-municipio { width: 120px; }
.th-depto { width: 120px; }
.th-territorial { width: 100px; }
.th-area { width: 70px; }
.th-mecanismo { width: 100px; }
.th-grupo { width: 80px; }
.th-fecha { width: 100px; }
.th-acciones { width: 80px; }

.table-striped tbody tr:nth-of-type(odd) {
  background-color: rgba(0, 0, 0, 0.05);
}

.table-hover tbody tr:hover {
  background-color: rgba(0, 0, 0, 0.075);
}

.text-center {
  text-align: center;
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
}

.btn-pagination.active {
  background-color: #007bff;
  border-color: #007bff;
  color: #fff;
}

.btn-pagination.disabled {
  color: #6c757d;
  pointer-events: none;
  cursor: not-allowed;
}

/* Estilos del modal */
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
  max-width: 800px;
  margin: 0.5rem;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #dee2e6;
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.close-button {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-body {
  padding: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.info-section h5 {
  margin: 0 0 1rem;
  color: #2c3e50;
  font-weight: 600;
  border-bottom: 2px solid #3498db;
  padding-bottom: 0.5rem;
}

.info-fields {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-field {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.info-field .label {
  font-weight: 500;
  color: #495057;
  min-width: 120px;
}

.info-field .value {
  color: #6c757d;
  text-align: right;
  font-weight: 400;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #dee2e6;
  background-color: #f8f9fa;
}

/* Responsive */
@media (max-width: 992px) {
  .info-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}
@media (max-width: 480px) {
  .tab-button {
    min-width: 100px;
    padding: 0.5rem 0.25rem;
    font-size: 0.75rem;
  }
  
  .tab-vigencias {
    flex-direction: column;
    gap: 0.15rem;
  }
}
@media (max-width: 768px) {

  .tab-button {
    min-width: 120px;
    padding: 0.75rem 0.5rem;
    font-size: 0.8rem;
  }
  
  .tab-button i {
    font-size: 1rem;
  }
  
  .tab-vigencias {
    gap: 0.25rem;
  }

  .tabs-header {
    justify-content: flex-start;
  }
  


  .header-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .info-section {
    align-items: stretch;
  }
  
  .access-info-header {
    align-items: center;
  }
  
  .info-field {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .info-field .value {
    text-align: left;
  }
  
  .search-input-container {
    max-width: 100%;
  }
}
</style>