<template>
  <div class="municipios-list-container">
    <div class="header-section">
      <h2 class="page-title">Consulta de Municipios</h2>
      <div class="actions-bar">
        <button class="btn btn-create" @click="navigateToCreate" v-if="hasPermission">
          <i class="material-icons">add_circle</i>
          Crear Nuevo Municipio
        </button>
        <button 
          class="btn btn-secondary" 
          @click="exportarDatos" 
          :disabled="!municipiosTabla.length"
        >
          <i class="material-icons">file_download</i>
          Exportar Resultados
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
              <option 
                v-for="depto in departamentosDisponibles" 
                :key="depto.cod_depto" 
                :value="depto.cod_depto"
              >
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
              <option 
                v-for="mun in municipiosDisponibles" 
                :key="mun.cod_municipio" 
                :value="mun.cod_municipio"
              >
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
              <span class="contador-opciones">({{ territorialesDisponibles.length }} disponibles)</span>
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
              <option 
                v-for="territorial in territorialesDisponibles" 
                :key="territorial.nom_territorial" 
                :value="territorial.nom_territorial"
              >
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

      <!-- Segunda fila de filtros - Profesionales DINÁMICOS -->
      <div class="row">
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
            >
              <option value="">Todos los roles</option>
              <option 
                v-for="rol in rolesProfesionalesFiltradosDinamicos" 
                :key="rol.codigo" 
                :value="rol.codigo"
              >
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
              <option 
                v-for="prof in profesionalesFiltradosDinamicos" 
                :key="prof.cod_profesional" 
                :value="prof.cod_profesional"
              >
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
              <span class="contador-opciones">({{ mecanismosDisponibles.length }} disponibles)</span>
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
              <option 
                v-for="mecanismo in mecanismosDisponibles" 
                :key="mecanismo.cod_mecanismo" 
                :value="mecanismo.cod_mecanismo"
              >
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
              <span class="contador-opciones">({{ detallesMecanismoDisponibles.length }} disponibles)</span>
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
              <option 
                v-for="detalle in detallesMecanismoDisponibles" 
                :key="detalle.cod_mecanismo_detalle" 
                :value="detalle.cod_mecanismo_detalle"
              >
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
            <label for="mecanismoOperacion">
              Mecanismo Operación:
              <span class="contador-opciones">({{ mecanismosOperacionDisponibles.length }} disponibles)</span>
            </label>
            <select 
              id="mecanismoOperacion" 
              v-model="filtros.mecanismoOperacion" 
              @change="actualizarFiltrosMecanismoOperacion"
              class="form-control"
              :class="{ 'has-selection': filtros.mecanismoOperacion }"
              :disabled="cargandoFiltros"
            >
              <option value="">Todos</option>
              <option 
                v-for="operacion in mecanismosOperacionDisponibles" 
                :key="operacion.cod_operacion" 
                :value="operacion.cod_operacion"
              >
                {{ operacion.cod_operacion }}
              </option>
            </select>
            <button 
              v-if="filtros.mecanismoOperacion" 
              @click="limpiarFiltroEspecifico('mecanismoOperacion')"
              class="btn-limpiar-filtro"
              title="Limpiar filtro de operación"
            >
              ✓
            </button>
          </div>
        </div>
      </div>

      <!-- Cuarta fila de filtros - Grupo, Estado, Búsqueda -->
      <div class="row">
        <div class="col-md-6 col-lg-4">
          <div class="form-group">
            <label for="grupo">
              Grupo:
              <span class="contador-opciones">({{ gruposDisponibles.length }} disponibles)</span>
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
              <option 
                v-for="grupo in gruposDisponibles" 
                :key="grupo.cod_grupo" 
                :value="grupo.cod_grupo"
              >
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

        <div class="col-md-6 col-lg-4">
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

        <div class="col-md-6 col-lg-4">
          <div class="form-group">
            <label for="busqueda">Búsqueda:</label>
            <input 
              type="text" 
              id="busqueda" 
              v-model="filtros.busqueda" 
              @input="debounceSearch"
              placeholder="Buscar municipio..."
              class="form-control"
            />
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
          <span v-if="filtros.mecanismoOperacion" class="tag-filtro operacion">
            Operación: {{ obtenerNombreFiltro('mecanismoOperacion', filtros.mecanismoOperacion) }}
            <button @click="limpiarFiltroEspecifico('mecanismoOperacion')">×</button>
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
    </div>

    <!-- Tabla de resultados -->
    <div v-else class="results-container">
      <div class="results-header">
        <h3 class="results-title">Resultados</h3>
        <div class="results-summary">
          <span class="results-count">{{ municipiosTabla.length }} municipios encontrados</span>
          <span v-if="hayFiltrosActivos" class="results-filter-info">
            (filtrados de {{ municipios.length }} totales)
          </span>
        </div>
      </div>

      <div class="table-responsive">
        <table class="table table-striped table-hover">
          <thead>
            <tr>
              <th @click="ordenarPor('cod_municipio')" class="th-codigo">
                Código
                <i v-if="ordenacion.campo === 'cod_municipio'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('nom_municipio')" class="th-municipio">
                Municipio
                <i v-if="ordenacion.campo === 'nom_municipio'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('cod_depto.nom_depto')" class="th-depto">
                Departamento
                <i v-if="ordenacion.campo === 'cod_depto.nom_depto'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('nom_territorial')" class="th-territorial">
                Territorial
                <i v-if="ordenacion.campo === 'nom_territorial'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('area')" class="th-area">
                Área [ha]
                <i v-if="ordenacion.campo === 'area'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('mecanismo_general')" class="th-mecanismo">
                Mecanismo
                <i v-if="ordenacion.campo === 'mecanismo_general'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('mecanismo_detalle')" class="th-mecdetalle">
                Mec. Detalle
                <i v-if="ordenacion.campo === 'mecanismo_detalle'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('mecanismo_operacion')" class="th-mecoper">
                Mec. Oper.
                <i v-if="ordenacion.campo === 'mecanismo_operacion'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('grupo')" class="th-grupo">
                Grupo
                <i v-if="ordenacion.campo === 'grupo'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('fecha_inicio')" class="th-fecha">
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
              <td>{{ municipio.mecanismo_detalle || 'N/A' }}</td>
              <td>{{ municipio.mecanismo_operacion || 'N/A' }}</td>
              <td>{{ municipio.grupo || 'N/A' }}</td>
              <td>{{ formatFecha(municipio.fecha_inicio) }}</td>
              <!-- NUEVAS COLUMNAS -->
              <td class="text-center">{{ obtenerVigenciaRural(municipio.cod_municipio) }}</td>
              <td class="text-center">{{ obtenerVigenciaUrbana(municipio.cod_municipio) }}</td>
              <td>
                <div class="action-buttons">
                  <router-link 
                    :to="`/gestion-informacion/municipios/${municipio.cod_municipio}`" 
                    class="action-btn view-btn"
                    title="Ver detalles"
                  >
                    <i class="material-icons">visibility</i>
                  </router-link>
                  
                  <router-link 
                    v-if="hasPermission"
                    :to="`/gestion-informacion/municipios/${municipio.cod_municipio}/editar`" 
                    class="action-btn edit-btn"
                    title="Editar municipio"
                  >
                    <i class="material-icons">edit</i>
                  </router-link>
                  
                  <button 
                    v-if="hasPermission"
                    class="action-btn delete-btn" 
                    @click="confirmarEliminar(municipio)"
                    title="Eliminar municipio"
                  >
                    <i class="material-icons">delete</i>
                  </button>
                  
                  <router-link 
                    :to="`/gestion-informacion/insumos?municipio=${municipio.cod_municipio}`" 
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

    <!-- Modal de confirmación para eliminar -->
    <div class="modal" v-if="modalEliminar.mostrar">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">Confirmar eliminación</h4>
            <button class="close-button" @click="modalEliminar.mostrar = false" :disabled="eliminando">
              <i class="material-icons">close</i>
            </button>
          </div>
          <div class="modal-body">
            <div class="alert alert-danger">
              <i class="material-icons">warning</i>
              <strong>ADVERTENCIA: Esta es una operación irreversible</strong>
            </div>
            
            <p>¿Está seguro de que desea eliminar el municipio <strong>{{ modalEliminar.municipio?.nom_municipio }}</strong> ({{ modalEliminar.municipio?.cod_municipio }})?</p>
            
            <div class="cascada-info">
              <p><strong>Esta operación eliminará en cascada:</strong></p>
              <ul class="dependencias-list">
                <li><strong>Insumos:</strong> Todos los insumos del municipio</li>
                <li><strong>Clasificaciones:</strong> Todas las clasificaciones de insumos</li>
                <li><strong>Detalles:</strong> Todos los detalles de insumos</li>
                <li><strong>Archivos:</strong> Todos los archivos vinculados</li>
                <li><strong>Notificaciones:</strong> Todas las notificaciones asociadas</li>
                <li><strong>Rutas de directorios:</strong> Todas las rutas asociadas</li>
                <li><strong>Disposiciones:</strong> Todas las disposiciones de post-operación</li>
                <li><strong>Asignaciones:</strong> Todas las asignaciones de profesionales</li>
              </ul>
            </div>
            
            <div class="confirm-text">
              <p>Esta acción <strong>NO PUEDE DESHACERSE</strong>. Por favor, confirme que desea proceder.</p>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="modalEliminar.mostrar = false" :disabled="eliminando">Cancelar</button>
            <button class="btn btn-danger" @click="eliminarMunicipio" :disabled="eliminando">
              <div v-if="eliminando" class="btn-loading">
                <div class="spinner-small"></div>
                <span>Eliminando...</span>
              </div>
              <div v-else class="btn-content">
                <i class="material-icons">delete_forever</i>
                <span>Eliminar</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de detalles para municipio -->
    <div class="modal" v-if="modalDetalle.mostrar">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">Detalles del Municipio - {{ modalDetalle.municipio?.nom_municipio }}</h4>
            <button class="close-button" @click="modalDetalle.mostrar = false">
              <i class="material-icons">close</i>
            </button>
          </div>
          <div class="modal-body">
            <div v-if="modalDetalle.municipio" class="municipio-info">
              <div class="row">
                <div class="col-md-6">
                  <p><strong>Código:</strong> {{ modalDetalle.municipio.cod_municipio }}</p>
                  <p><strong>Nombre:</strong> {{ modalDetalle.municipio.nom_municipio }}</p>
                  <p><strong>Departamento:</strong> {{ obtenerNombreDepartamento(modalDetalle.municipio) }}</p>
                  <p><strong>Territorial:</strong> {{ modalDetalle.municipio.nom_territorial || 'No asignada' }}</p>
                  <p><strong>Área:</strong> {{ modalDetalle.municipio.area || 'No disponible' }}</p>
                </div>
                <div class="col-md-6">
                  <p><strong>Mecanismo General:</strong> {{ modalDetalle.municipio.mecanismo_general || 'No asignado' }}</p>
                  <p><strong>Mecanismo Detalle:</strong> {{ modalDetalle.municipio.mecanismo_detalle || 'No asignado' }}</p>
                  <p><strong>Mecanismo Operación:</strong> {{ modalDetalle.municipio.mecanismo_operacion || 'No asignado' }}</p>
                  <p><strong>Grupo:</strong> {{ modalDetalle.municipio.grupo || 'No asignado' }}</p>
                  <p><strong>Fecha Inicio:</strong> {{ formatFecha(modalDetalle.municipio.fecha_inicio) }}</p>
                  <p><strong>Vigencia Rural:</strong> {{ obtenerVigenciaRural(modalDetalle.municipio.cod_municipio) }}</p>
                  <p><strong>Vigencia Urbana:</strong> {{ obtenerVigenciaUrbana(modalDetalle.municipio.cod_municipio) }}</p>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button 
              v-if="hasPermission"
              class="btn btn-primary" 
              @click="editMunicipio(modalDetalle.municipio)"
            >
              Editar
            </button>
            <button class="btn btn-info" @click="verInsumos(modalDetalle.municipio)">
              Ver Insumos
            </button>
            <button class="btn btn-secondary" @click="modalDetalle.mostrar = false">Cerrar</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import axios from 'axios'
import { format, parseISO } from 'date-fns'
import { es } from 'date-fns/locale'
import { debounce } from 'lodash'

// Import API functions
import { 
  getMunicipios, 
  getMunicipioById, 
  eliminarMunicipioCascada 
} from '@/api/municipios';

import { getDepartamentos } from '@/api/departamentos'
import { getInfoAdministrativa } from '@/api/infoAdministrativa'
import api, { API_URL } from '@/api/config'

export default defineComponent({
  name: 'MunicipiosList',

  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    // Estado de carga y errores
    const cargando = ref(false)
    const cargandoFiltros = ref(false)
    const error = ref<string | null>(null)
    const eliminando = ref(false)
    
    // Datos
    const municipios = ref<any[]>([])
    const departamentos = ref<any[]>([])
    const territoriales = ref<any[]>([])
    const mecanismos = ref<any[]>([])
    const detallesMecanismo = ref<any[]>([])
    const mecanismosOperacion = ref<any[]>([])
    const grupos = ref<any[]>([])
    
    // Estado para profesionales
    const profesionales = ref<any[]>([])
    const profesionalesFiltrados = ref<any[]>([])
    
    // Datos para profesionales y sus relaciones
    const profesionalMunicipio = ref<any[]>([])
    const profesionalTerritorial = ref<any[]>([])
    
    // Estado para municipios filtrados por departamento (para el selector de municipios)
    const municipiosFiltrados = ref<any[]>([])
    
    // Estado para los catálogos filtrados
    const territorialesFiltradas = ref<any[]>([])
    const mecanismosFiltrados = ref<any[]>([])
    const detallesMecanismoFiltrados = ref<any[]>([])
    const mecanismosOperacionFiltrados = ref<any[]>([])
    const gruposFiltrados = ref<any[]>([])
    
    // NUEVOS ESTADOS PARA INFO ADMINISTRATIVA
    const infoAdministrativa = ref<any[]>([])
    const infoAdminMap = ref<Map<number, any>>(new Map())
    
    // Búsqueda y filtros
    const filtros = ref({
      departamento: '',
      territorial: '',
      municipio: '',
      mecanismo: '',
      mecanismoDetalle: '',
      mecanismoOperacion: '',
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
    
    // Modales
    const modalEliminar = ref({
      mostrar: false,
      municipio: null as any
    })
    
    const modalDetalle = ref({
      mostrar: false,
      municipio: null as any
    })
    
    // Verificar permisos del usuario - Simplificado para no depender de /usuarios/me/
    const hasPermission = computed(() => {
      // Verificar si hay un token, consideramos que quien tenga un token válido tiene permiso
      const token = localStorage.getItem('token')
      return !!token
    })
    
    // Función para filtrar municipios según permisos del usuario
    const filtrarMunicipiosPorPermisos = (municipiosData: any[]) => {
      // Como este código no maneja permisos específicos, retornar todos
      return municipiosData;
    };
    
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
      
      if (filtros.value.mecanismoOperacion) {
        resultado = resultado.filter(m => m.mecanismo_operacion === filtros.value.mecanismoOperacion)
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

    const territorialesDisponibles = computed(() => {
      const territorialesUnicas = new Set(
        municipiosFiltradosAcumulativos.value
          .map(m => m.nom_territorial)
          .filter(t => t && t.trim() !== '')
      )
      
      return territoriales.value
        .filter(t => territorialesUnicas.has(t.nom_territorial))
        .sort((a, b) => a.nom_territorial.localeCompare(b.nom_territorial))
    })

    const municipiosDisponibles = computed(() => {
      return municipiosFiltradosAcumulativos.value
        .sort((a, b) => a.nom_municipio.localeCompare(b.nom_municipio))
    })

    const mecanismosDisponibles = computed(() => {
      const mecanismosUsados = new Set(
        municipiosFiltradosAcumulativos.value
          .map(m => m.mecanismo_general)
          .filter(m => m && m.trim() !== '')
      )
      
      return mecanismos.value
        .filter(m => mecanismosUsados.has(m.cod_mecanismo))
        .sort((a, b) => a.cod_mecanismo.localeCompare(b.cod_mecanismo))
    })

    const detallesMecanismoDisponibles = computed(() => {
      const detallesUsados = new Set(
        municipiosFiltradosAcumulativos.value
          .map(m => m.mecanismo_detalle)
          .filter(d => d && d.trim() !== '')
      )
      
      return detallesMecanismo.value
        .filter(d => detallesUsados.has(d.cod_mecanismo_detalle))
        .sort((a, b) => a.cod_mecanismo_detalle.localeCompare(b.cod_mecanismo_detalle))
    })

    const mecanismosOperacionDisponibles = computed(() => {
      const operacionesUsadas = new Set(
        municipiosFiltradosAcumulativos.value
          .map(m => m.mecanismo_operacion)
          .filter(o => o && o.trim() !== '')
      )
      
      return mecanismosOperacion.value
        .filter(o => operacionesUsadas.has(o.cod_operacion))
        .sort((a, b) => a.cod_operacion.localeCompare(b.cod_operacion))
    })

    const gruposDisponibles = computed(() => {
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
        filtros.value.mecanismoOperacion ||
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
    
    // COMPUTED PARA VIGENCIAS DISPONIBLES (DINÁMICAS)
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
    
    const municipiosFiltradosDinamicos = computed(() => {
      return municipiosFiltradosAcumulativos.value
        .sort((a, b) => a.nom_municipio.localeCompare(b.nom_municipio))
    })
    
    // Función para obtener el nombre del departamento de un municipio
    const obtenerNombreDepartamento = (municipio: any): string => {
      if (!municipio) return 'N/A'
      
      // Si el objeto tiene la estructura anidada completa
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
    
    // Función recursiva para cargar TODOS los datos sin importar la paginación
    const cargarTodosLosDatos = async (url: string, params = {}) => {
      // Array para almacenar todos los resultados
      let todosLosResultados = []
      // URL inicial
      let urlActual = url
      
      try {
        // Añadir parámetros iniciales a la URL
        if (Object.keys(params).length > 0) {
          const queryParams = new URLSearchParams(params as any).toString()
          urlActual = `${url}?${queryParams}`
          console.log('URL con parámetros:', urlActual);
        }
        
        // Obtener token de autenticación
        const token = localStorage.getItem('token')
        const config = token ? {
          headers: {
            'Authorization': `Token ${token}`
          }
        } : {}
        
        // Primera llamada para obtener el total de elementos
        const primeraRespuesta = await axios.get(urlActual, config)
        
        // Verificar si la respuesta ya es un array simple (sin paginación)
        if (Array.isArray(primeraRespuesta.data)) {
          console.log(`Recibidos ${primeraRespuesta.data.length} elementos (sin paginación)`)
          return primeraRespuesta.data
        }
        
        // Si hay resultados paginados, obtener la primera página
        if (primeraRespuesta.data.results) {
          todosLosResultados = [...primeraRespuesta.data.results]
          
          // Calcular el número total de elementos
          const count = primeraRespuesta.data.count || 0
          console.log(`Total de elementos a cargar: ${count}`)
          
          // Si ya tenemos todos los elementos, terminar
          if (todosLosResultados.length >= count) {
            return todosLosResultados
          }
          
          // Calcular cuántas páginas necesitamos cargar
          const pageSize = primeraRespuesta.data.results.length
          const totalPages = Math.ceil(count / pageSize)
          console.log(`Detectados ${totalPages} páginas con ${pageSize} elementos por página`)
          
          // Preparar todas las peticiones para las páginas restantes
          const promesas = []
          for (let pagina = 2; pagina <= totalPages; pagina++) {
            // Construir URL con parámetro de página
            let urlPagina = `${url}?page=${pagina}`
            
            // Añadir otros parámetros si existen
            if (Object.keys(params).length > 0) {
              const otrosParams = new URLSearchParams(params as any).toString()
              urlPagina = `${url}?${otrosParams}&page=${pagina}`
            }
            
            promesas.push(axios.get(urlPagina, config))
          }
          
          // Ejecutar todas las peticiones en paralelo
          console.log(`Cargando ${promesas.length} páginas adicionales...`)
          const respuestas = await Promise.all(promesas)
          
          // Procesar todas las respuestas y añadir los resultados
          respuestas.forEach(respuesta => {
            if (respuesta.data && respuesta.data.results) {
              todosLosResultados = [...todosLosResultados, ...respuesta.data.results]
            }
          })
          
          console.log(`Cargados con éxito ${todosLosResultados.length} elementos`)
        }
        
        return todosLosResultados
      } catch (error) {
        console.error(`Error cargando datos de ${url}:`, error)
        throw error
      }
    }
    
    // Cargar municipios
    const cargarMunicipios = async () => {
      error.value = null
      
      try {
        cargando.value = true
        console.log('Cargando municipios con filtros:', filtros.value)
        
        // Si hay filtro de profesional o rol profesional, necesitamos un enfoque especial
        if (filtros.value.profesional || filtros.value.rolProfesional) {
          await cargarMunicipiosPorProfesional()
          return
        }
        
        // Construir parámetros de filtro para la API
        const params: any = {}
        
        if (filtros.value.departamento) {
          console.log(`Filtro departamento: ${filtros.value.departamento}`)
          params.cod_depto = filtros.value.departamento
        }
        
        if (filtros.value.territorial) {
          console.log(`Filtro territorial: ${filtros.value.territorial}`)
          params.nom_territorial = filtros.value.territorial
        }
        
        if (filtros.value.municipio) {
          console.log(`Filtro municipio: ${filtros.value.municipio}`)
          params.cod_municipio = filtros.value.municipio
        }
        
        if (filtros.value.mecanismo) {
          console.log(`Filtro mecanismo: ${filtros.value.mecanismo}`)
          params.mecanismo_general = filtros.value.mecanismo
        }
        
        if (filtros.value.mecanismoDetalle) {
          console.log(`Filtro mecanismo detalle: ${filtros.value.mecanismoDetalle}`)
          params.mecanismo_detalle = filtros.value.mecanismoDetalle
        }
        
        if (filtros.value.mecanismoOperacion) {
          console.log(`Filtro mecanismo operación: ${filtros.value.mecanismoOperacion}`)
          params.mecanismo_operacion = filtros.value.mecanismoOperacion
        }
        
        if (filtros.value.grupo) {
          console.log(`Filtro grupo: ${filtros.value.grupo}`)
          params.grupo = filtros.value.grupo
        }
        
        if (filtros.value.busqueda && filtros.value.busqueda.trim() !== '') {
          console.log(`Filtro búsqueda: ${filtros.value.busqueda}`)
          params.search = filtros.value.busqueda.trim()
        }
        
        let municipiosData = []
        
        try {
          if (Object.keys(params).length > 0) {
            // Si hay filtros, cargar los datos filtrados
            console.log('Aplicando parámetros a la API:', params)
            municipiosData = await cargarTodosLosDatos(`${API_URL}/preoperacion/municipios/`, params)
            console.log(`Obtenidos ${municipiosData.length} municipios filtrados de la API`)
          } else {
            // Si no hay filtros, cargar todos los municipios
            municipiosData = await cargarTodosLosDatos(`${API_URL}/preoperacion/municipios/`)
            console.log(`Obtenidos ${municipiosData.length} municipios totales de la API`)
          }
          
          // Filtrar por estadoFecha si está seleccionado (este filtrado se hace del lado del cliente)
          if (filtros.value.estadoFecha) {
            if (filtros.value.estadoFecha === 'con_fecha') {
              municipiosData = municipiosData.filter(m => m.fecha_inicio)
              console.log(`Después de filtrar por fecha_inicio, quedan ${municipiosData.length} municipios`)
            } else if (filtros.value.estadoFecha === 'sin_fecha') {
              municipiosData = municipiosData.filter(m => !m.fecha_inicio)
              console.log(`Después de filtrar por sin fecha_inicio, quedan ${municipiosData.length} municipios`)
            }
          }
          
          // Aplicar filtros de vigencia rural
          if (filtros.value.vigenciaRuralDesde || filtros.value.vigenciaRuralHasta) {
            municipiosData = municipiosData.filter(m => {
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
            municipiosData = municipiosData.filter(m => {
              const info = infoAdminMap.value.get(m.cod_municipio)
              if (!info || !info.vigencia_urbana) return false
              
              const vigenciaYear = parseInt(info.vigencia_urbana)
              if (isNaN(vigenciaYear)) return false
              
              const desde = filtros.value.vigenciaUrbanaDesde ? parseInt(filtros.value.vigenciaUrbanaDesde) : 0
              const hasta = filtros.value.vigenciaUrbanaHasta ? parseInt(filtros.value.vigenciaUrbanaHasta) : 9999
              
              return vigenciaYear >= desde && vigenciaYear <= hasta
            })
          }
          
          // Inicializar el conteo de insumos a 0 para todos los municipios
          municipiosData.forEach(municipio => {
            municipio.insumos_count = 0
          })
          
          // Actualizar la variable municipios con los datos filtrados
          municipios.value = municipiosData
          
          // Reiniciar paginación
          paginaActual.value = 1
          
        } catch (err) {
          console.error('Error al cargar municipios desde la API:', err)
          error.value = 'Error al cargar los municipios. Por favor, inténtelo de nuevo.'
          return
        }
      } catch (err) {
        console.error('Error general al cargar municipios:', err)
        error.value = 'Error al cargar los municipios. Por favor, inténtelo de nuevo.'
      } finally {
        cargando.value = false
      }
    }
    
    // Función para cargar municipios filtrados por profesional
    const cargarMunicipiosPorProfesional = async () => {
      try {
        console.log('Cargando municipios por profesional...');
        let profesionalesIds: string[] = [];
        
        // Si hay un profesional específico seleccionado
        if (filtros.value.profesional) {
          profesionalesIds = [filtros.value.profesional];
          console.log(`Filtrando por profesional específico: ${filtros.value.profesional}`);
        }
        // Si solo hay un rol profesional seleccionado SIN profesional específico, no continuar
        else if (filtros.value.rolProfesional && !filtros.value.profesional) {
          console.log('Se ha seleccionado un rol profesional pero no un profesional específico. No se cargarán municipios hasta seleccionar un profesional específico.');
          municipios.value = [];
          return;
        }
        
        console.log(`Buscando municipios para ${profesionalesIds.length} profesionales:`, profesionalesIds);
        
        // Si no hay profesionales que cumplan los criterios, no hay municipios
        if (profesionalesIds.length === 0) {
          console.log('No se encontraron profesionales con los criterios seleccionados');
          municipios.value = [];
          return;
        }
        
        // Obtener todas las asignaciones de profesionales a municipios
        let todasAsignaciones: any[] = [];
        
        for (const profId of profesionalesIds) {
          try {
            console.log(`Buscando asignaciones para profesional: ${profId}`);
            const asignacionesProf = await cargarTodosLosDatos(`${API_URL}/preoperacion/profesional-municipio/`, {
              cod_profesional: profId
            });
            console.log(`Encontradas ${asignacionesProf.length} asignaciones para profesional ${profId}`);
            
            // Imprimir la primera asignación para depuración
            if (asignacionesProf.length > 0) {
              console.log('Ejemplo de asignación:', asignacionesProf[0]);
            }
            
            todasAsignaciones = [...todasAsignaciones, ...asignacionesProf];
          } catch (error) {
            console.error(`Error al cargar asignaciones para profesional ${profId}:`, error);
          }
        }
        
        console.log(`Obtenidas ${todasAsignaciones.length} asignaciones de municipios para los profesionales seleccionados`);
        
        // Si no hay asignaciones, no hay municipios
        if (todasAsignaciones.length === 0) {
          console.log('No se encontraron asignaciones de municipios para los profesionales seleccionados');
          municipios.value = [];
          return;
        }
        
        // Extraer los IDs de municipios únicos con mejor manejo de diferentes formatos
        const municipiosIds = [...new Set(
          todasAsignaciones.map(a => {
            // Verificar la estructura del objeto para extraer el ID de municipio
            if (!a) return null;
            
            try {
              // Caso 1: a.cod_municipio es un número directamente
              if (typeof a.cod_municipio === 'number') {
                return a.cod_municipio;
              }
              
              // Caso 2: a.cod_municipio es un string que representa un número
              if (typeof a.cod_municipio === 'string' && !isNaN(Number(a.cod_municipio))) {
                return Number(a.cod_municipio);
              }
              
              // Caso 3: a.cod_municipio es un objeto con propiedad cod_municipio
              if (a.cod_municipio && typeof a.cod_municipio === 'object' && a.cod_municipio.cod_municipio) {
                return a.cod_municipio.cod_municipio;
              }
              
              // Caso 4: a.municipio es un objeto o número
              if (a.municipio) {
                if (typeof a.municipio === 'number') {
                  return a.municipio;
                }
                
                if (typeof a.municipio === 'object' && a.municipio.cod_municipio) {
                  return a.municipio.cod_municipio;
                }
              }
              
              // Loguear y retornar null si no podemos extraer el ID
              console.log('No se pudo extraer ID de municipio de asignación:', a);
              return null;
            } catch (error) {
              console.error('Error al extraer ID de municipio:', error);
              return null;
            }
          }).filter(Boolean) // Filtrar valores nulos o undefined
        )];
        
        console.log(`Encontrados ${municipiosIds.length} municipios únicos asignados a los profesionales:`, municipiosIds);
        
        // Si no hay municipios asignados, terminamos
        if (municipiosIds.length === 0) {
          municipios.value = [];
          return;
        }
        
        // Cargar detalles de los municipios
        let municipiosData: any[] = [];
        
        for (const munId of municipiosIds) {
          try {
            const municipioData = await getMunicipioById(munId);
            municipiosData.push(municipioData);
          } catch (error) {
            console.error(`Error al cargar detalles del municipio ${munId}:`, error);
          }
        }
        
        console.log(`Cargados detalles de ${municipiosData.length} municipios`);
        
        // Aplicar filtros adicionales si existen
        let municipiosFiltrados = [...municipiosData];
        
        if (filtros.value.departamento) {
          municipiosFiltrados = municipiosFiltrados.filter(m => {
            if (typeof m.cod_depto === 'object' && m.cod_depto !== null) {
              return m.cod_depto.cod_depto.toString() === filtros.value.departamento.toString();
            }
            return m.cod_depto.toString() === filtros.value.departamento.toString();
          });
          console.log(`Después de filtrar por departamento, quedan ${municipiosFiltrados.length} municipios`);
        }
        
        if (filtros.value.territorial && filtros.value.territorial !== '') {
          municipiosFiltrados = municipiosFiltrados.filter(m => 
            m.nom_territorial === filtros.value.territorial
          );
          console.log(`Después de filtrar por territorial, quedan ${municipiosFiltrados.length} municipios`);
        }
        
        if (filtros.value.mecanismo && filtros.value.mecanismo !== '') {
          municipiosFiltrados = municipiosFiltrados.filter(m => 
            m.mecanismo_general === filtros.value.mecanismo
          );
          console.log(`Después de filtrar por mecanismo, quedan ${municipiosFiltrados.length} municipios`);
        }
        
        if (filtros.value.mecanismoDetalle && filtros.value.mecanismoDetalle !== '') {
          municipiosFiltrados = municipiosFiltrados.filter(m => 
            m.mecanismo_detalle === filtros.value.mecanismoDetalle
          );
          console.log(`Después de filtrar por mecanismo detalle, quedan ${municipiosFiltrados.length} municipios`);
        }
        
        if (filtros.value.mecanismoOperacion && filtros.value.mecanismoOperacion !== '') {
          municipiosFiltrados = municipiosFiltrados.filter(m => 
            m.mecanismo_operacion === filtros.value.mecanismoOperacion
          );
          console.log(`Después de filtrar por mecanismo operación, quedan ${municipiosFiltrados.length} municipios`);
        }
        
        if (filtros.value.grupo && filtros.value.grupo !== '') {
          municipiosFiltrados = municipiosFiltrados.filter(m => 
            m.grupo === filtros.value.grupo
          );
          console.log(`Después de filtrar por grupo, quedan ${municipiosFiltrados.length} municipios`);
        }
        
        if (filtros.value.busqueda && filtros.value.busqueda.trim() !== '') {
          const busqueda = filtros.value.busqueda.toLowerCase().trim();
          municipiosFiltrados = municipiosFiltrados.filter(m => 
            (m.nom_municipio && m.nom_municipio.toLowerCase().includes(busqueda)) ||
            (m.cod_municipio && m.cod_municipio.toString().includes(busqueda))
          );
          console.log(`Después de filtrar por texto de búsqueda, quedan ${municipiosFiltrados.length} municipios`);
        }
        
        if (filtros.value.estadoFecha) {
          if (filtros.value.estadoFecha === 'con_fecha') {
            municipiosFiltrados = municipiosFiltrados.filter(m => m.fecha_inicio);
            console.log(`Después de filtrar por fecha_inicio, quedan ${municipiosFiltrados.length} municipios`);
          } else if (filtros.value.estadoFecha === 'sin_fecha') {
            municipiosFiltrados = municipiosFiltrados.filter(m => !m.fecha_inicio);
            console.log(`Después de filtrar por sin fecha_inicio, quedan ${municipiosFiltrados.length} municipios`);
          }
        }
        
        // Aplicar filtros de vigencia rural
        if (filtros.value.vigenciaRuralDesde || filtros.value.vigenciaRuralHasta) {
          municipiosFiltrados = municipiosFiltrados.filter(m => {
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
          municipiosFiltrados = municipiosFiltrados.filter(m => {
            const info = infoAdminMap.value.get(m.cod_municipio)
            if (!info || !info.vigencia_urbana) return false
            
            const vigenciaYear = parseInt(info.vigencia_urbana)
            if (isNaN(vigenciaYear)) return false
            
            const desde = filtros.value.vigenciaUrbanaDesde ? parseInt(filtros.value.vigenciaUrbanaDesde) : 0
            const hasta = filtros.value.vigenciaUrbanaHasta ? parseInt(filtros.value.vigenciaUrbanaHasta) : 9999
            
            return vigenciaYear >= desde && vigenciaYear <= hasta
          })
        }
        
        // Inicializar el conteo de insumos a 0 para todos los municipios
        municipiosFiltrados.forEach(municipio => {
          municipio.insumos_count = 0;
        });
        
        console.log(`Total final: ${municipiosFiltrados.length} municipios`);
        municipios.value = municipiosFiltrados;
        
        // Reiniciar paginación
        paginaActual.value = 1;
        
      } catch (error) {
        console.error('Error al cargar municipios por profesional:', error);
        error.value = 'Error al cargar municipios por profesional';
      }
    };
    
    // Función para cargar los profesionales
    const cargarProfesionales = async () => {
      try {
        console.log('Cargando profesionales...');
        const profesionalesData = await cargarTodosLosDatos(`${API_URL}/preoperacion/profesionales-seguimiento/`);
        
        // Asegurarse de que todos tengan nombre_profesional
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
        console.log(`Cargados ${profesionales.value.length} profesionales`);
        
        // Imprimir los primeros 5 profesionales para verificar estructura
        console.log('Ejemplo de profesionales:', profesionales.value.slice(0, 5));
      } catch (error) {
        console.error('Error al cargar profesionales:', error);
      }
    };
    
    // Función para cargar relaciones profesionales
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
        infoAdminMap.value = new Map()
        infoData.forEach(info => {
          if (info.cod_municipio) {
            infoAdminMap.value.set(info.cod_municipio, info)
          }
        })
        
        console.log('✅ Info administrativa cargada:', infoData.length, 'registros')
      } catch (error) {
        console.error('❌ Error cargando info administrativa:', error)
      }
    }
    
    // Función para filtrar profesionales por rol
    const filtrarProfesionalesPorRol = () => {
      // Usar el computed dinámico en lugar de filtrar manualmente
      profesionalesFiltrados.value = profesionalesFiltradosDinamicos.value
    };
    
    // Cargar datos iniciales para los filtros
    const cargarCatalogos = async () => {
      try {
        console.log('Cargando catálogos para filtros...')
        
        // Cargar departamentos
        const deptosResult = await cargarTodosLosDatos(`${API_URL}/preoperacion/departamentos/`)
        departamentos.value = deptosResult
        console.log(`Cargados ${departamentos.value.length} departamentos`)
        
        // Cargar territoriales
        const territorialesResult = await cargarTodosLosDatos(`${API_URL}/preoperacion/territoriales/`)
        territoriales.value = territorialesResult
        territorialesFiltradas.value = territorialesResult
        console.log(`Cargadas ${territoriales.value.length} territoriales`)
        
        // Cargar mecanismos generales
        const mecanismosResult = await cargarTodosLosDatos(`${API_URL}/preoperacion/mecanismos-general/`)
        mecanismos.value = mecanismosResult
        mecanismosFiltrados.value = mecanismosResult
        console.log(`Cargados ${mecanismos.value.length} mecanismos generales`)
        
        // Cargar detalles de mecanismos
        const detallesResult = await cargarTodosLosDatos(`${API_URL}/preoperacion/mecanismos-detalle/`)
        detallesMecanismo.value = detallesResult
        detallesMecanismoFiltrados.value = detallesResult
        console.log(`Cargados ${detallesMecanismo.value.length} detalles de mecanismos`)
        
        // Cargar mecanismos de operación
        const operacionResult = await cargarTodosLosDatos(`${API_URL}/preoperacion/mecanismos-operacion/`)
        mecanismosOperacion.value = operacionResult
        mecanismosOperacionFiltrados.value = operacionResult
        console.log(`Cargados ${mecanismosOperacion.value.length} mecanismos de operación`)
        
        // Cargar grupos
        const gruposResult = await cargarTodosLosDatos(`${API_URL}/preoperacion/grupos/`)
        grupos.value = gruposResult
        gruposFiltrados.value = gruposResult
        console.log(`Cargados ${grupos.value.length} grupos`)
      } catch (err) {
        console.error('Error al cargar catálogos:', err)
        error.value = 'Error al cargar datos de referencia.'
      }
    }
    
    // Actualizar filtros al seleccionar departamento
    const actualizarFiltrosDepartamento = async () => {
      await cargarMunicipios()
    }
    
    // Actualizar filtros al seleccionar territorial
    const actualizarFiltrosTerritorial = async () => {
      await cargarMunicipios()
    }
    
    // Actualizar filtros al seleccionar un municipio específico
    const actualizarFiltrosMunicipio = async () => {
      await cargarMunicipios()
    }
    
    // Actualizar filtros al seleccionar mecanismo
    const actualizarFiltrosMecanismo = async () => {
      await cargarMunicipios()
    }
    
    // Función para manejar selección de rol profesional
    const actualizarFiltroRolProfesional = async () => {
      console.log('Actualizando filtro de rol profesional:', filtros.value.rolProfesional);
      
      // Si se selecciona o cambia el rol, limpiar filtro de profesional específico
      filtros.value.profesional = '';
      
      // Siempre filtrar la lista de profesionales según el rol seleccionado
      filtrarProfesionalesPorRol();
      
      // Aplicar cambios inmediatamente
      await cargarMunicipios();
    };
    
    // Función para manejar selección de profesional específico
    const actualizarFiltroProfesional = async () => {
      console.log('Profesional específico seleccionado:', filtros.value.profesional);
      
      if (!filtros.value.profesional) {
        // Si se deselecciona el profesional específico, recargar municipios
        await cargarMunicipios();
        return;
      }
      
      // Ahora sí cargar los municipios para el profesional específico
      await cargarMunicipios();
    };
    
    // Función para manejar cambios en mecanismo detalle
    const actualizarFiltrosMecanismoDetalle = async () => {
      console.log('Actualizando filtro de mecanismo detalle:', filtros.value.mecanismoDetalle)
      await cargarMunicipios()
    }
    
    // Función para manejar cambios en mecanismo operación
    const actualizarFiltrosMecanismoOperacion = async () => {
      console.log('Actualizando filtro de mecanismo operación:', filtros.value.mecanismoOperacion)
      await cargarMunicipios()
    }
    
    // Función para manejar cambios en grupo
    const actualizarFiltrosGrupo = async () => {
      console.log('Actualizando filtro de grupo:', filtros.value.grupo)
      await cargarMunicipios()
    }
    
    // Función para búsqueda con debounce
    const debounceSearch = debounce(() => {
      console.log('Aplicando búsqueda debounced:', filtros.value.busqueda)
      cargarMunicipios()
    }, 500)
    
    // Función para actualizar los filtros genéricos
    const actualizarFiltros = async () => {
      await cargarMunicipios()
    }
    
    // Aplicar filtros
    const aplicarFiltros = async () => {
      console.log('Aplicando filtros manualmente:', filtros.value)
      await cargarMunicipios()
    }
    
    // Limpiar filtros
    const limpiarFiltros = async () => {
      // Resetear todos los filtros
      filtros.value = {
        departamento: '',
        territorial: '',
        municipio: '',
        mecanismo: '',
        mecanismoDetalle: '',
        mecanismoOperacion: '',
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
      
      // Restaurar listas de filtros originales
      territorialesFiltradas.value = [...territoriales.value]
      mecanismosFiltrados.value = [...mecanismos.value]
      detallesMecanismoFiltrados.value = [...detallesMecanismo.value]
      mecanismosOperacionFiltrados.value = [...mecanismosOperacion.value]
      gruposFiltrados.value = [...grupos.value]
      municipiosFiltrados.value = []
      profesionalesFiltrados.value = [...profesionales.value]
      
      // Cargar todos los municipios sin filtros
      await cargarMunicipios()
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
        case 'mecanismoOperacion':
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
    
    // Municipios para mostrar en la tabla
    const municipiosTabla = computed(() => {
      return municipiosFiltradosAcumulativos.value
    })
    
    // Elementos visibles en la página actual
    const municipiosVisibles = computed(() => {
      const inicio = (paginaActual.value - 1) * elementosPorPagina.value
      const fin = inicio + elementosPorPagina.value
      return municipiosTabla.value.slice(inicio, fin)
    })
    
    // Total de páginas
    const totalPaginas = computed(() => {
      return Math.ceil(municipiosTabla.value.length / elementosPorPagina.value) || 1
    })
    
    // Botones numéricos para paginación
    const botonesNumericos = computed(() => {
      const botones = []
      const maxBotones = 5 // Número máximo de botones a mostrar
      
      if (totalPaginas.value <= maxBotones) {
        // Si hay pocas páginas, mostrarlas todas
        for (let i = 1; i <= totalPaginas.value; i++) {
          botones.push({
            valor: i,
            texto: i.toString(),
            activo: i === paginaActual.value,
            ellipsis: false
          })
        }
      } else {
        // Siempre mostrar la primera página
        botones.push({
          valor: 1,
          texto: '1',
          activo: paginaActual.value === 1,
          ellipsis: false
        })
        
        // Calcular el rango de páginas a mostrar alrededor de la página actual
        let inicio = Math.max(2, paginaActual.value - 1)
        let fin = Math.min(totalPaginas.value - 1, paginaActual.value + 1)
        
        // Ajustar si estamos cerca del principio
        if (paginaActual.value <= 3) {
          fin = Math.min(4, totalPaginas.value - 1)
        }
        
        // Ajustar si estamos cerca del final
        if (paginaActual.value >= totalPaginas.value - 2) {
          inicio = Math.max(2, totalPaginas.value - 3)
        }
        
        // Mostrar elipsis si hay salto al principio
        if (inicio > 2) {
          botones.push({
            valor: null,
            texto: '...',
            activo: false,
            ellipsis: true
          })
        }
        
        // Mostrar páginas centrales
        for (let i = inicio; i <= fin; i++) {
          botones.push({
            valor: i,
            texto: i.toString(),
            activo: i === paginaActual.value,
            ellipsis: false
          })
        }
        
        // Mostrar elipsis si hay salto al final
        if (fin < totalPaginas.value - 1) {
          botones.push({
            valor: null,
            texto: '...',
            activo: false,
            ellipsis: true
          })
        }
        
        // Siempre mostrar la última página
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
    
    // Cambiar página
    const cambiarPagina = (pagina) => {
      if (pagina >= 1 && pagina <= totalPaginas.value) {
        paginaActual.value = pagina
      }
    }
    
    // Ordenar por campo
    const ordenarPor = (campo) => {
      if (ordenacion.value.campo === campo) {
        // Si ya estamos ordenando por este campo, invertir dirección
        ordenacion.value.ascendente = !ordenacion.value.ascendente
      } else {
        // Si es un nuevo campo, ordenar ascendente por defecto
        ordenacion.value.campo = campo
        ordenacion.value.ascendente = true
      }
      
      // Aplicar ordenación
      municipios.value.sort((a, b) => {
        let valorA, valorB
        
        // Manejar propiedades anidadas (ej: "cod_depto.nom_depto")
        if (campo.includes('.')) {
          const [parentKey, childKey] = campo.split('.')
          valorA = a[parentKey]?.[childKey] || ''
          valorB = b[parentKey]?.[childKey] || ''
        } else {
          valorA = a[campo] || ''
          valorB = b[campo] || ''
        }
        
        // Comparar según el tipo de dato
        if (typeof valorA === 'string' && typeof valorB === 'string') {
          return ordenacion.value.ascendente 
            ? valorA.localeCompare(valorB) 
            : valorB.localeCompare(valorA)
        } else {
          // Para valores numéricos o fechas
          return ordenacion.value.ascendente 
            ? (valorA > valorB ? 1 : -1)
            : (valorB > valorA ? 1 : -1)
        }
      })
    }
    
    // Formatear fecha
    const formatFecha = (fecha) => {
      if (!fecha) return 'No definida'
      
      try {
        const fechaObj = new Date(fecha)
        return format(fechaObj, 'dd/MM/yyyy', { locale: es })
      } catch (error) {
        return fecha
      }
    }
    // Navegar a la página de edicion
    const editMunicipio = (municipio: any) => {
      router.push(`/gestion-informacion/municipios/${municipio.cod_municipio}/editar`);
    };
    // Navegar a la página de creación
    const navigateToCreate = () => {
      router.push('/gestion-informacion/municipios/crear');
    }
    
    // Confirmar eliminación
    const confirmarEliminar = (municipio) => {
      modalEliminar.value.municipio = municipio
      modalEliminar.value.mostrar = true
    }
    
    // Eliminar municipio y sus dependencias
    const eliminarMunicipio = async () => {
      if (!modalEliminar.value.municipio) return;
      
      try {
        eliminando.value = true;
        
        // Obtener el ID del municipio a eliminar
        const municipioId = modalEliminar.value.municipio.cod_municipio;
        const municipioNombre = modalEliminar.value.municipio.nom_municipio;
        
        console.log(`Iniciando eliminación en cascada del municipio ${municipioId} - ${municipioNombre}`);
        
        try {
          // Usamos el método del servicio para eliminación en cascada
          const response = await eliminarMunicipioCascada(municipioId);
          
          console.log('Respuesta de eliminación:', response);
          
          // Mostrar mensaje de éxito
          alert(`Municipio "${municipioNombre}" y todas sus dependencias eliminados con éxito`);
          
          // Actualizar lista
          await cargarMunicipios();
        } catch (apiError) {
          console.error('Error API al eliminar municipio:', apiError);
          
          let mensajeError = 'Error al eliminar el municipio.';
          
          // Extraer mensaje de error de la respuesta
          if (apiError.response) {
            if (apiError.response.data && apiError.response.data.error) {
              mensajeError = apiError.response.data.error;
            } else if (apiError.response.data && typeof apiError.response.data === 'string') {
              mensajeError = apiError.response.data;
            }
            
            // Si es un error 404, el endpoint no existe
            if (apiError.response.status === 404) {
              mensajeError = 'El endpoint de eliminación en cascada no está disponible. Contacte con el administrador.';
            }
          }
          
          alert(`Error: ${mensajeError}`);
        }
      } catch (err) {
        console.error('Error general al eliminar municipio:', err);
        alert(`Error inesperado: ${err.message}`);
      } finally {
        eliminando.value = false;
        modalEliminar.value.mostrar = false;
      }
    };
    
    // Ver detalles del municipio
    const verMunicipio = async (municipio) => {
      try {
        // Mostrar modal con detalles sin hacer peticiones adicionales
        modalDetalle.value.municipio = municipio
        modalDetalle.value.mostrar = true
      } catch (err) {
        console.error('Error al obtener detalles del municipio:', err)
        alert('Error al cargar los detalles del municipio')
      }
    }
    
    // Editar municipio
    const editarMunicipio = (municipio) => {
      // Cerrar modal si está abierto
      if (modalDetalle.value.mostrar) {
        modalDetalle.value.mostrar = false
      }
      
      // Navegar a la página de edición con el ID
      router.push(`/gestion-informacion/municipios/${municipio.cod_municipio}/editar`)
    }
    
    // Ver insumos del municipio
    const verInsumos = (municipio) => {
      // Cerrar modal si está abierto
      if (modalDetalle.value.mostrar) {
        modalDetalle.value.mostrar = false
      }
      
      // Navegar a la página de insumos del municipio
      router.push(`/gestion-informacion/insumos?municipio=${municipio.cod_municipio}`)
    }
    
    // Exportar datos a CSV ACTUALIZADO
    const exportarDatos = () => {
      try {
        console.log('Botón exportar presionado'); // Añade este log para verificar que se llame la función
        
        // Verificar si hay datos para exportar
        if (!municipiosTabla.value || municipiosTabla.value.length === 0) {
          alert('No hay datos para exportar');
          return;
        }
        
        console.log(`Iniciando exportación de ${municipiosTabla.value.length} registros...`);
        
        // Definir encabezados
        const headers = [
          'Código',
          'Municipio',
          'Departamento',
          'Territorial',
          'Área',
          'Mecanismo General',
          'Mecanismo Detalle',
          'Mecanismo Operación',
          'Grupo',
          'Fecha Inicio',
          'Vigencia Rural',  // Nueva columna
          'Vigencia Urbana'  // Nueva columna
        ];
        
        // Preparar filas de datos
        const rows = municipiosTabla.value.map(m => [
          m.cod_municipio,
          m.nom_municipio,
          obtenerNombreDepartamento(m),
          m.nom_territorial || '',
          m.area || '',
          m.mecanismo_general || '',
          m.mecanismo_detalle || '',
          m.mecanismo_operacion || '',
          m.grupo || '',
          formatFecha(m.fecha_inicio),
          obtenerVigenciaRural(m.cod_municipio),    // Nueva columna
          obtenerVigenciaUrbana(m.cod_municipio)    // Nueva columna
        ]);
        
        // BOM (Byte Order Mark) para que Excel maneje correctamente los caracteres especiales
        const BOM = '\uFEFF';
        
        // Combinar encabezados y filas
        const csvContent = BOM + [
          headers.join(','),
          ...rows.map(row => row.map(cell => 
            // Escapar comas y comillas en las celdas y manejar valores nulos
            `"${(cell !== null && cell !== undefined ? String(cell) : '').replace(/"/g, '""')}"`
          ).join(','))
        ].join('\n');
        
        console.log('CSV generado correctamente');
        
        // Intento simple sin try/catch internos para ver dónde falla
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `municipios_${new Date().toISOString().slice(0, 10)}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log('Descarga iniciada');
        alert('Archivo CSV generado correctamente');
        
      } catch (err) {
        console.error('Error al exportar datos:', err);
        alert(`Error al exportar datos: ${err.message}`);
      }
    };
    
    // Cargar datos al montar el componente
    onMounted(async () => {
      // Verificar token de autenticación directamente
      const token = localStorage.getItem('token')
      if (!token && hasPermission.value) {
        console.log('Usuario no autenticado, redirigiendo a login...')
        router.push('/login')
        return
      }
      
      // Cargar datos iniciales en paralelo
      try {
        console.log('Cargando catálogos para filtros...')
        // Primero cargar los catálogos para los filtros
        await Promise.all([
          cargarCatalogos(),
          cargarProfesionales(),
          cargarRelacionesProfesionales(),
          cargarInfoAdministrativa()  // NUEVA LÍNEA
        ])
        
        // Luego cargar municipios sin filtros
        await cargarMunicipios()
      } catch (err) {
        console.error('Error al cargar datos iniciales:', err)
        error.value = 'Error al cargar datos iniciales. Por favor, actualice la página.'
      }
    })
    
    return {
      // Estado y datos
      cargando,
      cargandoFiltros,
      error,
      eliminando,
      municipios,
      municipiosTabla,
      municipiosVisibles,
      municipiosFiltrados,
      
      // Catálogos
      departamentos,
      territoriales,
      territorialesFiltradas,
      mecanismos,
      mecanismosFiltrados,
      detallesMecanismo,
      detallesMecanismoFiltrados,
      mecanismosOperacion,
      mecanismosOperacionFiltrados,
      grupos,
      gruposFiltrados,
      
      // Profesionales
      profesionales,
      profesionalesFiltrados,
      
      // Variables agregadas para el sistema dinámico
      profesionalMunicipio,
      profesionalTerritorial,
      municipiosFiltradosAcumulativos,
      profesionalesFiltradosDinamicos,
      rolesProfesionalesFiltradosDinamicos,
      
      // Computed dinámicos
      departamentosDisponibles,
      municipiosDisponibles,
      territorialesDisponibles,
      mecanismosDisponibles,
      detallesMecanismoDisponibles,
      mecanismosOperacionDisponibles,
      gruposDisponibles,
      municipiosFiltradosDinamicos,
      
      // Info administrativa
      infoAdministrativa,
      infoAdminMap,
      
      // Permisos
      hasPermission,
      
      // Filtros y ordenación
      filtros,
      ordenacion,
      
      // Paginación
      paginaActual,
      totalPaginas,
      botonesNumericos,
      
      // Modales
      modalEliminar,
      modalDetalle,
      
      // Métodos
      cargarMunicipios,
      cargarRelacionesProfesionales,
      cargarInfoAdministrativa,
      filtrarMunicipiosPorPermisos,
      actualizarFiltrosDepartamento,
      actualizarFiltrosTerritorial,
      actualizarFiltrosMunicipio,
      actualizarFiltrosMecanismo,
      actualizarFiltrosMecanismoDetalle,
      actualizarFiltrosMecanismoOperacion,
      actualizarFiltrosGrupo,
      actualizarFiltroRolProfesional,
      actualizarFiltroProfesional,
      aplicarFiltros,
      limpiarFiltros,
      limpiarFiltroEspecifico,
      limpiarFiltroVigencia,
      ordenarPor,
      cambiarPagina,
      formatFecha,
      obtenerNombreDepartamento,
      obtenerVigenciaRural,
      obtenerVigenciaUrbana,
      obtenerInfoAdministrativa,
      obtenerNombreFiltro,
      obtenerRangoVigencia,
      navigateToCreate,
      editMunicipio,
      verMunicipio,
      editarMunicipio,
      confirmarEliminar,
      eliminarMunicipio,
      verInsumos,
      exportarDatos,
      debounceSearch,
      actualizarFiltros,
      hayFiltrosActivos,
      
      // NUEVOS COMPUTED PARA VIGENCIAS
      vigenciasRuralesDisponibles,
      vigenciasUrbanasDisponibles,
      vigenciasRuralesHastaDisponibles,
      vigenciasUrbanasHastaDisponibles,
    }
  }
})
</script>

<style scoped>
/* ESTILOS PARA FILTROS DINÁMICOS */
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


  /* CONTINUACIÓN DE ESTILOS PARA MunicipiosList2.vue */

.tag-filtro.operacion {
  background: linear-gradient(135deg, #6f42c1, #5a2d91);
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

/* ESTILOS PRINCIPALES DEL COMPONENTE */
.municipios-list-container {
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

.btn-create {
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
  transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  cursor: pointer;
}

.btn-create:hover {
  background-color: #218838;
  border-color: #1e7e34;
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

.col-md-6, .col-lg-3, .col-lg-4, .col-lg-6 {
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

.btn-danger:disabled {
  opacity: 0.65;
  cursor: not-allowed;
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

.spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
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

.results-filter-info {
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
  cursor: pointer;
  white-space: nowrap;
}

.table thead th i {
  font-size: 1rem;
  vertical-align: middle;
  margin-left: 0.25rem;
}

/* Ajustar anchos de columnas */
.th-codigo { width: 70px; }
.th-municipio { width: 120px; }
.th-depto { width: 120px; }
.th-territorial { width: 100px; }
.th-area { width: 70px; }
.th-mecanismo { width: 100px; }
.th-mecdetalle { width: 110px; }
.th-mecoper { width: 100px; }
.th-grupo { width: 80px; }
.th-fecha { width: 100px; }
.th-vigencia { width: 80px; }
.th-acciones { width: 140px; }

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

.badge-primary {
  color: #fff;
  background-color: #007bff;
}

.badge-warning {
  color: #212529;
  background-color: #ffc107;
}

.badge-secondary {
  color: #fff;
  background-color: #6c757d;
}

.text-center {
  text-align: center;
}

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

.edit-btn {
  background-color: #28a745;
  color: white !important;
}

.edit-btn:hover {
  background-color: #218838;
  color: white !important;
}

.delete-btn {
  background-color: #dc3545;
}

.delete-btn:hover {
  background-color: #c82333;
}

.insumos-btn {
  background-color: #17a2b8;
  color: white !important;
}

.insumos-btn:hover {
  background-color: #138496;
  color: white !important;
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

/* ESTILOS DE MODALES */
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
  margin: 0.5rem;
}

.modal-dialog.modal-lg {
  max-width: 800px;
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
  background-color: #f8f9fa;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
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

.close-button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
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

.municipio-info p {
  margin-bottom: 0.75rem;
}

/* Estilos para el modal de eliminación */
.alert {
  padding: 0.75rem 1.25rem;
  margin-bottom: 1rem;
  border: 1px solid transparent;
  border-radius: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.alert-danger {
  color: #721c24;
  background-color: #f8d7da;
  border-color: #f5c6cb;
}

.cascada-info {
  margin: 1.5rem 0;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #dc3545;
}

.cascada-info p {
  margin: 0 0 0.75rem 0;
  font-weight: 600;
}

.dependencias-list {
  margin: 0;
  padding-left: 1.5rem;
  list-style-type: disc;
}

.dependencias-list li {
  margin-bottom: 0.5rem;
}

.confirm-text {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 4px;
  color: #856404;
}

.confirm-text p {
  margin: 0;
}

.btn-loading {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.text-danger {
  color: #dc3545;
}

.text-warning {
  color: #f0ad4e;
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
    flex-direction: column;
  }

  .btn-pagination {
    min-width: 28px;
    height: 28px;
    font-size: 0.8rem;
  }

  .action-buttons {
    flex-wrap: wrap;
  }

  .table {
    font-size: 0.75rem;
  }

  .action-btn {
    width: 24px;
    height: 24px;
  }
  
  .modal-dialog {
    margin: 0.25rem;
  }
  
  .modal-body {
    padding: 1rem;
  }
}
</style>