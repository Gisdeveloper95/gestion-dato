<template>
  <div class="productos-page operacion-page">
    <!-- Header -->
    <header class="page-header operacion-header">
      <div class="header-content">
        <div class="header-left">
          <button @click="goBack" class="btn-back">
            <i class="material-icons">arrow_back</i>
          </button>
          <div class="header-info">
            <h1>{{ municipioName }}</h1>
            <span class="header-subtitle">Operacion - Municipio {{ route.params.id }}</span>
          </div>
        </div>
        <div class="header-right">
          <div class="access-badge" :class="accessLevelClass">
            <i class="material-icons">{{ accessLevelIcon }}</i>
            <span>{{ accessLevelText }}</span>
          </div>
          <button @click="refreshData" class="btn-refresh" :disabled="loading">
            <i class="material-icons">refresh</i>
          </button>
        </div>
      </div>
    </header>

    <!-- Loading -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <span>Cargando datos de operacion...</span>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-container">
      <i class="material-icons">error</i>
      <p>{{ error }}</p>
      <button @click="refreshData" class="btn-retry">Reintentar</button>
    </div>

    <!-- Acceso Denegado para Profesionales -->
    <div v-else-if="isProfesionalSinAcceso" class="access-denied-container">
      <i class="material-icons">lock</i>
      <h3>Acceso Restringido</h3>
      <p>No tienes permisos para ver los datos de operacion de este municipio.</p>
      <button @click="goBack" class="btn-back-large">
        <i class="material-icons">arrow_back</i>
        Volver
      </button>
    </div>

    <!-- Contenido Principal -->
    <main v-else-if="tieneAccesoADatos" class="content-main">
      <!-- Panel de Calificacion Masiva (Solo Super Admin) -->
      <section v-if="canUseMassQualification" class="mass-qualification-panel" :class="{ expanded: modoCalificacionMasiva }">
        <div class="panel-header" @click="toggleModoCalificacionMasiva">
          <div class="panel-title">
            <i class="material-icons">grading</i>
            <span>Calificacion Masiva</span>
            <span v-if="modoCalificacionMasiva" class="badge-active">ACTIVO</span>
          </div>
          <i class="material-icons expand-icon">{{ modoCalificacionMasiva ? 'expand_less' : 'expand_more' }}</i>
        </div>

        <div v-if="modoCalificacionMasiva" class="panel-content">
          <div class="mass-qual-controls">
            <div class="control-group">
              <label>Filtro de archivos:</label>
              <select v-model="filtroMasivo" class="select-filtro">
                <option value="todos">Todos los archivos</option>
                <option value="no_calificados">Solo sin calificar (evaluacion=1)</option>
                <option value="excepto_aprobados">Todos excepto aprobados</option>
              </select>
            </div>

            <div class="control-group">
              <label>Calificacion a aplicar:</label>
              <select v-model="calificacionMasivaSeleccionada" class="select-calificacion">
                <option :value="null">-- Seleccionar --</option>
                <option v-for="cal in calificaciones" :key="cal.id" :value="cal.id">
                  {{ cal.concepto }} ({{ cal.valor }})
                </option>
              </select>
            </div>

            <div class="selection-info">
              <span class="count">{{ archivosSeleccionadosCount }} archivos seleccionados</span>
              <span class="filter-count">({{ archivosFiltradosPorMasivo.length }} cumplen filtro)</span>
            </div>

            <div class="mass-actions">
              <button @click="seleccionarTodos" class="btn-select-all">
                <i class="material-icons">select_all</i>
                Seleccionar todos
              </button>
              <button @click="deseleccionarTodos" class="btn-deselect-all">
                <i class="material-icons">deselect</i>
                Limpiar seleccion
              </button>
              <button
                @click="mostrarConfirmacionMasiva"
                class="btn-apply-mass"
                :disabled="archivosSeleccionadosCount === 0 || !calificacionMasivaSeleccionada || aplicandoCalificacion"
              >
                <i class="material-icons">{{ aplicandoCalificacion ? 'hourglass_empty' : 'done_all' }}</i>
                {{ aplicandoCalificacion ? 'Aplicando...' : 'Aplicar calificacion' }}
              </button>
            </div>

            <!-- Info ultimo lote -->
            <div v-if="ultimoLoteMasivo?.tiene_lote" class="ultimo-lote-info">
              <div class="lote-header">
                <i class="material-icons">history</i>
                <span>Ultima calificacion masiva</span>
              </div>
              <div class="lote-details">
                <span>Lote: {{ ultimoLoteMasivo.lote_id }}</span>
                <span>Archivos: {{ ultimoLoteMasivo.archivos_en_lote }}</span>
                <span>Usuario: {{ ultimoLoteMasivo.usuario }}</span>
              </div>
              <button @click="restaurarCalificacionAnterior" class="btn-restore" :disabled="aplicandoCalificacion">
                <i class="material-icons">restore</i>
                Restaurar anterior
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Estadisticas -->
      <section class="stats-section">
        <div class="stat-card">
          <i class="material-icons">folder</i>
          <div class="stat-content">
            <span class="stat-value">{{ estadisticasFiltradas.total_directorios }}</span>
            <span class="stat-label">Directorios</span>
          </div>
        </div>
        <div class="stat-card">
          <i class="material-icons">insert_drive_file</i>
          <div class="stat-content">
            <span class="stat-value">{{ estadisticasFiltradas.total_archivos }}</span>
            <span class="stat-label">Archivos</span>
          </div>
        </div>
        <div class="stat-card pending">
          <i class="material-icons">pending</i>
          <div class="stat-content">
            <span class="stat-value">{{ estadisticasFiltradas.pendientes }}</span>
            <span class="stat-label">Pendientes</span>
          </div>
        </div>
        <div class="stat-card evaluated">
          <i class="material-icons">fact_check</i>
          <div class="stat-content">
            <span class="stat-value">{{ estadisticasFiltradas.evaluados }}</span>
            <span class="stat-label">Evaluados</span>
          </div>
        </div>
        <div class="stat-card approved">
          <i class="material-icons">verified</i>
          <div class="stat-content">
            <span class="stat-value">{{ estadisticasFiltradas.aprobados }}</span>
            <span class="stat-label">Aprobados</span>
          </div>
        </div>
      </section>

      <!-- Filtros -->
      <section class="filters-section">
        <div class="search-box">
          <i class="material-icons">search</i>
          <input v-model="searchTerm" placeholder="Buscar archivo..." />
          <button v-if="searchTerm" @click="clearSearch" class="clear-btn">
            <i class="material-icons">close</i>
          </button>
        </div>

        <div class="filters-row">
          <select v-model="filtroEstado" class="filter-select">
            <option value="">Todos los estados</option>
            <option value="PENDIENTE">Pendientes</option>
            <option value="EVALUADO">Evaluados</option>
            <option value="APROBADO">Aprobados</option>
          </select>

          <select v-if="mecanismosDisponibles.length > 0" v-model="filtroMecanismo" class="filter-select">
            <option value="">Todos los mecanismos</option>
            <option v-for="mec in mecanismosDisponibles" :key="mec" :value="mec">
              {{ mec }} ({{ getCountMecanismo(mec) }})
            </option>
          </select>

          <button v-if="tienesFiltrosActivos" @click="limpiarFiltros" class="btn-clear-filters">
            <i class="material-icons">clear_all</i>
            Limpiar filtros
          </button>
        </div>
      </section>

      <!-- Arbol de Directorios -->
      <section class="tree-section">
        <div class="tree-header">
          <h3>
            <i class="material-icons">account_tree</i>
            Estructura de Directorios
          </h3>
        </div>

        <div class="tree-content">
          <!-- Directorios Padre (Nivel 0) -->
          <div v-for="directorio in directoriosFiltrados" :key="directorio.id_disposicion" class="directorio-padre">
            <div class="directorio-header nivel-0" @click="toggleDirectorio(directorio.id_disposicion)">
              <!-- Checkbox masivo para directorio -->
              <div v-if="modoCalificacionMasiva" class="checkbox-directorio" @click.stop>
                <input
                  type="checkbox"
                  :checked="isDirectorioSeleccionado(directorio)"
                  :indeterminate="isDirectorioParcialmenteSeleccionado(directorio)"
                  @change="toggleDirectorioSeleccion(directorio, $event.target.checked)"
                />
              </div>
              <i class="material-icons folder-icon">
                {{ directoriosExpandidos[directorio.id_disposicion] ? 'folder_open' : 'folder' }}
              </i>
              <span class="directorio-nombre">{{ directorio.nombre_directorio }}</span>
              <div class="directorio-stats">
                <span class="stat-badge files">{{ directorio.total_archivos }} archivos</span>
                <span class="stat-badge subdirs">{{ directorio.subdirectorios_count }} subdirs</span>
              </div>
              <div class="directorio-actions" @click.stop>
                <button v-if="canDownload" @click="descargarDirectorio(directorio)" class="btn-download-dir" title="Descargar directorio">
                  <i class="material-icons">download</i>
                </button>
                <button v-if="canDelete" @click="eliminarDirectorio(directorio)" class="btn-delete-dir" title="Eliminar directorio">
                  <i class="material-icons">delete</i>
                </button>
              </div>
              <i class="material-icons expand-icon">
                {{ directoriosExpandidos[directorio.id_disposicion] ? 'expand_less' : 'expand_more' }}
              </i>
            </div>

            <!-- Contenido expandido del directorio -->
            <div v-if="directoriosExpandidos[directorio.id_disposicion]" class="directorio-content nivel-0">
              <!-- Subdirectorios Nivel 1 -->
              <div v-for="subdirectorio in directorio.subdirectorios" :key="subdirectorio.id_disposicion" class="subdirectorio nivel-1">
                <div class="directorio-header nivel-1" @click="toggleDirectorio(subdirectorio.id_disposicion)">
                  <div v-if="modoCalificacionMasiva" class="checkbox-directorio" @click.stop>
                    <input
                      type="checkbox"
                      :checked="isDirectorioSeleccionado(subdirectorio)"
                      :indeterminate="isDirectorioParcialmenteSeleccionado(subdirectorio)"
                      @change="toggleDirectorioSeleccion(subdirectorio, $event.target.checked)"
                    />
                  </div>
                  <i class="material-icons folder-icon">
                    {{ directoriosExpandidos[subdirectorio.id_disposicion] ? 'folder_open' : 'folder' }}
                  </i>
                  <span class="directorio-nombre">{{ subdirectorio.nombre_directorio }}</span>
                  <div class="directorio-stats">
                    <span class="stat-badge files">{{ subdirectorio.total_archivos }}</span>
                  </div>
                  <div class="directorio-actions" @click.stop>
                    <button v-if="canDownload" @click="descargarDirectorio(subdirectorio)" class="btn-download-dir" title="Descargar">
                      <i class="material-icons">download</i>
                    </button>
                  </div>
                  <i class="material-icons expand-icon">
                    {{ directoriosExpandidos[subdirectorio.id_disposicion] ? 'expand_less' : 'expand_more' }}
                  </i>
                </div>

                <div v-if="directoriosExpandidos[subdirectorio.id_disposicion]" class="directorio-content nivel-1">
                  <!-- Archivos del subdirectorio nivel 1 -->
                  <div v-if="subdirectorio.archivos && subdirectorio.archivos.length > 0" class="archivos-seccion">
                    <div class="archivos-header">
                      <button @click="toggleArchivos(subdirectorio.id_disposicion)" class="btn-toggle-archivos">
                        <i class="material-icons">
                          {{ archivosExpandidos[subdirectorio.id_disposicion] ? 'visibility_off' : 'visibility' }}
                        </i>
                        <span>{{ archivosExpandidos[subdirectorio.id_disposicion] ? 'Ocultar' : 'Ver' }} {{ filtrarArchivos(subdirectorio.archivos).length }} archivos</span>
                      </button>
                    </div>
                    <div v-if="archivosExpandidos[subdirectorio.id_disposicion]" class="archivos-lista">
                      <div
                        v-for="archivo in filtrarArchivos(subdirectorio.archivos)"
                        :key="archivo.id_evaluacion"
                        :class="['archivo-item', { 'seleccionado-masivo': modoCalificacionMasiva && isArchivoSeleccionado(archivo.id_evaluacion) }]"
                      >
                        <div v-if="modoCalificacionMasiva" class="checkbox-archivo" @click.stop>
                          <input
                            type="checkbox"
                            :checked="isArchivoSeleccionado(archivo.id_evaluacion)"
                            @change="toggleArchivoSeleccion(archivo.id_evaluacion)"
                          />
                        </div>
                        <div class="archivo-icon">
                          <i class="material-icons">{{ getFileIcon(archivo.nombre_archivo) }}</i>
                        </div>
                        <div class="archivo-info">
                          <span class="archivo-nombre" :title="archivo.nombre_archivo">{{ archivo.nombre_archivo }}</span>
                          <span class="archivo-fecha">{{ formatDate(archivo.fecha_disposicion) }}</span>
                        </div>
                        <div :class="['estado-badge', getEstadoClass(archivo.estado_archivo)]">
                          {{ archivo.estado_archivo }}
                        </div>
                        <div class="archivo-status">
                          <span :class="['status-icon', archivo.evaluado ? 'ok' : 'no']">{{ archivo.evaluado ? 'E' : 'E' }}</span>
                          <span :class="['status-icon', archivo.aprobado ? 'ok' : 'no']">{{ archivo.aprobado ? 'A' : 'A' }}</span>
                        </div>
                        <div class="archivo-calificacion">
                          <select
                            v-if="canEdit"
                            :value="archivo.evaluacion_archivo"
                            @change="actualizarEvaluacion({ ...archivo, evaluacion_archivo: parseInt($event.target.value) })"
                            class="select-calificacion-mini"
                          >
                            <option v-for="cal in calificaciones" :key="cal.id" :value="cal.id">
                              {{ cal.concepto }}
                            </option>
                          </select>
                          <span v-else class="cal-readonly">{{ getCalificacionText(archivo.evaluacion_archivo) }}</span>
                        </div>
                        <div class="archivo-acciones">
                          <button @click="showFileInfo(archivo)" class="btn-accion info" title="Info">
                            <i class="material-icons">info</i>
                          </button>
                          <button v-if="canDownload" @click="viewFile(archivo)" class="btn-accion view" title="Ver">
                            <i class="material-icons">visibility</i>
                          </button>
                          <button v-if="canDownload" @click="downloadFile(archivo)" class="btn-accion download" title="Descargar">
                            <i class="material-icons">download</i>
                          </button>
                          <button v-if="canEdit" @click="editObservaciones(archivo)" class="btn-accion edit" title="Notas">
                            <i class="material-icons">edit_note</i>
                          </button>
                          <button v-if="canDelete" @click="deleteFile(archivo)" class="btn-accion delete" title="Eliminar">
                            <i class="material-icons">delete</i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Subdirectorios Nivel 2 -->
                  <div v-for="subsubdir in subdirectorio.subdirectorios" :key="subsubdir.id_disposicion" class="subdirectorio nivel-2">
                    <div class="directorio-header nivel-2" @click="toggleDirectorio(subsubdir.id_disposicion)">
                      <div v-if="modoCalificacionMasiva" class="checkbox-directorio" @click.stop>
                        <input
                          type="checkbox"
                          :checked="isDirectorioSeleccionado(subsubdir)"
                          @change="toggleDirectorioSeleccion(subsubdir, $event.target.checked)"
                        />
                      </div>
                      <i class="material-icons folder-icon">{{ directoriosExpandidos[subsubdir.id_disposicion] ? 'folder_open' : 'folder' }}</i>
                      <span class="directorio-nombre">{{ subsubdir.nombre_directorio }}</span>
                      <span class="stat-badge files">{{ subsubdir.total_archivos }}</span>
                      <div class="directorio-actions" @click.stop>
                        <button v-if="canDownload" @click="descargarDirectorio(subsubdir)" class="btn-download-dir" title="Descargar">
                          <i class="material-icons">download</i>
                        </button>
                      </div>
                      <i class="material-icons expand-icon">{{ directoriosExpandidos[subsubdir.id_disposicion] ? 'expand_less' : 'expand_more' }}</i>
                    </div>

                    <div v-if="directoriosExpandidos[subsubdir.id_disposicion]" class="directorio-content nivel-2">
                      <!-- Archivos nivel 2 -->
                      <div v-if="subsubdir.archivos && subsubdir.archivos.length > 0" class="archivos-seccion">
                        <div class="archivos-header">
                          <button @click="toggleArchivos(subsubdir.id_disposicion)" class="btn-toggle-archivos">
                            <i class="material-icons">{{ archivosExpandidos[subsubdir.id_disposicion] ? 'visibility_off' : 'visibility' }}</i>
                            <span>{{ archivosExpandidos[subsubdir.id_disposicion] ? 'Ocultar' : 'Ver' }} {{ filtrarArchivos(subsubdir.archivos).length }} archivos</span>
                          </button>
                        </div>
                        <div v-if="archivosExpandidos[subsubdir.id_disposicion]" class="archivos-lista">
                          <div
                            v-for="archivo in filtrarArchivos(subsubdir.archivos)"
                            :key="archivo.id_evaluacion"
                            :class="['archivo-item', { 'seleccionado-masivo': modoCalificacionMasiva && isArchivoSeleccionado(archivo.id_evaluacion) }]"
                          >
                            <div v-if="modoCalificacionMasiva" class="checkbox-archivo" @click.stop>
                              <input type="checkbox" :checked="isArchivoSeleccionado(archivo.id_evaluacion)" @change="toggleArchivoSeleccion(archivo.id_evaluacion)" />
                            </div>
                            <div class="archivo-icon"><i class="material-icons">{{ getFileIcon(archivo.nombre_archivo) }}</i></div>
                            <div class="archivo-info">
                              <span class="archivo-nombre" :title="archivo.nombre_archivo">{{ archivo.nombre_archivo }}</span>
                              <span class="archivo-fecha">{{ formatDate(archivo.fecha_disposicion) }}</span>
                            </div>
                            <div :class="['estado-badge', getEstadoClass(archivo.estado_archivo)]">{{ archivo.estado_archivo }}</div>
                            <div class="archivo-status">
                              <span :class="['status-icon', archivo.evaluado ? 'ok' : 'no']">E</span>
                              <span :class="['status-icon', archivo.aprobado ? 'ok' : 'no']">A</span>
                            </div>
                            <div class="archivo-calificacion">
                              <select v-if="canEdit" :value="archivo.evaluacion_archivo" @change="actualizarEvaluacion({ ...archivo, evaluacion_archivo: parseInt($event.target.value) })" class="select-calificacion-mini">
                                <option v-for="cal in calificaciones" :key="cal.id" :value="cal.id">{{ cal.concepto }}</option>
                              </select>
                              <span v-else class="cal-readonly">{{ getCalificacionText(archivo.evaluacion_archivo) }}</span>
                            </div>
                            <div class="archivo-acciones">
                              <button @click="showFileInfo(archivo)" class="btn-accion info" title="Info"><i class="material-icons">info</i></button>
                              <button v-if="canDownload" @click="viewFile(archivo)" class="btn-accion view" title="Ver"><i class="material-icons">visibility</i></button>
                              <button v-if="canDownload" @click="downloadFile(archivo)" class="btn-accion download" title="Descargar"><i class="material-icons">download</i></button>
                              <button v-if="canEdit" @click="editObservaciones(archivo)" class="btn-accion edit" title="Notas"><i class="material-icons">edit_note</i></button>
                              <button v-if="canDelete" @click="deleteFile(archivo)" class="btn-accion delete" title="Eliminar"><i class="material-icons">delete</i></button>
                            </div>
                          </div>
                        </div>
                      </div>

                      <!-- Subdirectorios Nivel 3+ (recursivo simplificado) -->
                      <div v-for="nivel3 in subsubdir.subdirectorios" :key="nivel3.id_disposicion" class="subdirectorio nivel-3">
                        <div class="directorio-header nivel-3" @click="toggleDirectorio(nivel3.id_disposicion)">
                          <i class="material-icons folder-icon">{{ directoriosExpandidos[nivel3.id_disposicion] ? 'folder_open' : 'folder' }}</i>
                          <span class="directorio-nombre">{{ nivel3.nombre_directorio }}</span>
                          <span class="stat-badge files">{{ nivel3.total_archivos }}</span>
                          <div class="directorio-actions" @click.stop>
                            <button v-if="canDownload" @click="descargarDirectorio(nivel3)" class="btn-download-dir" title="Descargar">
                              <i class="material-icons">download</i>
                            </button>
                          </div>
                          <i class="material-icons expand-icon">{{ directoriosExpandidos[nivel3.id_disposicion] ? 'expand_less' : 'expand_more' }}</i>
                        </div>
                        <div v-if="directoriosExpandidos[nivel3.id_disposicion]" class="directorio-content nivel-3">
                          <div v-if="nivel3.archivos && nivel3.archivos.length > 0" class="archivos-seccion">
                            <div class="archivos-header">
                              <button @click="toggleArchivos(nivel3.id_disposicion)" class="btn-toggle-archivos">
                                <i class="material-icons">{{ archivosExpandidos[nivel3.id_disposicion] ? 'visibility_off' : 'visibility' }}</i>
                                <span>{{ archivosExpandidos[nivel3.id_disposicion] ? 'Ocultar' : 'Ver' }} {{ filtrarArchivos(nivel3.archivos).length }} archivos</span>
                              </button>
                            </div>
                            <div v-if="archivosExpandidos[nivel3.id_disposicion]" class="archivos-lista">
                              <div v-for="archivo in filtrarArchivos(nivel3.archivos)" :key="archivo.id_evaluacion" :class="['archivo-item', { 'seleccionado-masivo': modoCalificacionMasiva && isArchivoSeleccionado(archivo.id_evaluacion) }]">
                                <div v-if="modoCalificacionMasiva" class="checkbox-archivo" @click.stop>
                                  <input type="checkbox" :checked="isArchivoSeleccionado(archivo.id_evaluacion)" @change="toggleArchivoSeleccion(archivo.id_evaluacion)" />
                                </div>
                                <div class="archivo-icon"><i class="material-icons">{{ getFileIcon(archivo.nombre_archivo) }}</i></div>
                                <div class="archivo-info">
                                  <span class="archivo-nombre" :title="archivo.nombre_archivo">{{ archivo.nombre_archivo }}</span>
                                </div>
                                <div :class="['estado-badge', getEstadoClass(archivo.estado_archivo)]">{{ archivo.estado_archivo }}</div>
                                <div class="archivo-calificacion">
                                  <select v-if="canEdit" :value="archivo.evaluacion_archivo" @change="actualizarEvaluacion({ ...archivo, evaluacion_archivo: parseInt($event.target.value) })" class="select-calificacion-mini">
                                    <option v-for="cal in calificaciones" :key="cal.id" :value="cal.id">{{ cal.concepto }}</option>
                                  </select>
                                </div>
                                <div class="archivo-acciones">
                                  <button @click="showFileInfo(archivo)" class="btn-accion info"><i class="material-icons">info</i></button>
                                  <button v-if="canDownload" @click="downloadFile(archivo)" class="btn-accion download"><i class="material-icons">download</i></button>
                                  <button v-if="canDelete" @click="deleteFile(archivo)" class="btn-accion delete"><i class="material-icons">delete</i></button>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Archivos directos del directorio padre -->
              <div v-if="directorio.archivos && directorio.archivos.length > 0" class="archivos-seccion nivel-0">
                <div class="archivos-header">
                  <button @click="toggleArchivos(directorio.id_disposicion)" class="btn-toggle-archivos">
                    <i class="material-icons">{{ archivosExpandidos[directorio.id_disposicion] ? 'visibility_off' : 'visibility' }}</i>
                    <span>{{ archivosExpandidos[directorio.id_disposicion] ? 'Ocultar' : 'Ver' }} {{ filtrarArchivos(directorio.archivos).length }} archivos directos</span>
                  </button>
                </div>
                <div v-if="archivosExpandidos[directorio.id_disposicion]" class="archivos-lista">
                  <div
                    v-for="archivo in filtrarArchivos(directorio.archivos)"
                    :key="archivo.id_evaluacion"
                    :class="['archivo-item', { 'seleccionado-masivo': modoCalificacionMasiva && isArchivoSeleccionado(archivo.id_evaluacion) }]"
                  >
                    <div v-if="modoCalificacionMasiva" class="checkbox-archivo" @click.stop>
                      <input type="checkbox" :checked="isArchivoSeleccionado(archivo.id_evaluacion)" @change="toggleArchivoSeleccion(archivo.id_evaluacion)" />
                    </div>
                    <div class="archivo-icon"><i class="material-icons">{{ getFileIcon(archivo.nombre_archivo) }}</i></div>
                    <div class="archivo-info">
                      <span class="archivo-nombre" :title="archivo.nombre_archivo">{{ archivo.nombre_archivo }}</span>
                      <span class="archivo-fecha">{{ formatDate(archivo.fecha_disposicion) }}</span>
                    </div>
                    <div :class="['estado-badge', getEstadoClass(archivo.estado_archivo)]">{{ archivo.estado_archivo }}</div>
                    <div class="archivo-status">
                      <span :class="['status-icon', archivo.evaluado ? 'ok' : 'no']">E</span>
                      <span :class="['status-icon', archivo.aprobado ? 'ok' : 'no']">A</span>
                    </div>
                    <div class="archivo-calificacion">
                      <select v-if="canEdit" :value="archivo.evaluacion_archivo" @change="actualizarEvaluacion({ ...archivo, evaluacion_archivo: parseInt($event.target.value) })" class="select-calificacion-mini">
                        <option v-for="cal in calificaciones" :key="cal.id" :value="cal.id">{{ cal.concepto }}</option>
                      </select>
                      <span v-else class="cal-readonly">{{ getCalificacionText(archivo.evaluacion_archivo) }}</span>
                    </div>
                    <div class="archivo-acciones">
                      <button @click="showFileInfo(archivo)" class="btn-accion info" title="Info"><i class="material-icons">info</i></button>
                      <button v-if="canDownload" @click="viewFile(archivo)" class="btn-accion view" title="Ver"><i class="material-icons">visibility</i></button>
                      <button v-if="canDownload" @click="downloadFile(archivo)" class="btn-accion download" title="Descargar"><i class="material-icons">download</i></button>
                      <button v-if="canEdit" @click="editObservaciones(archivo)" class="btn-accion edit" title="Notas"><i class="material-icons">edit_note</i></button>
                      <button v-if="canDelete" @click="deleteFile(archivo)" class="btn-accion delete" title="Eliminar"><i class="material-icons">delete</i></button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Estado vacio -->
          <div v-if="directoriosFiltrados.length === 0" class="empty-state">
            <i class="material-icons">inbox</i>
            <h3>No se encontraron directorios</h3>
            <p>No hay directorios para mostrar con los filtros aplicados.</p>
          </div>
        </div>
      </section>
    </main>

    <!-- Modal de Informacion del Archivo -->
    <div v-if="showFileInfoModal" class="modal-overlay" @click="closeFileInfoModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3><i class="material-icons">info</i> Informacion del Archivo</h3>
          <button @click="closeFileInfoModal" class="modal-close"><i class="material-icons">close</i></button>
        </div>
        <div class="modal-body">
          <div v-if="selectedFileInfo" class="file-info-content">
            <div class="info-row"><label>Nombre:</label><span>{{ selectedFileInfo.nombre_archivo }}</span></div>
            <div class="info-row"><label>Estado:</label><span :class="['estado-badge', getEstadoClass(selectedFileInfo.estado_archivo)]">{{ selectedFileInfo.estado_archivo }}</span></div>
            <div class="info-row"><label>Ruta:</label><span class="ruta-text">{{ linuxToWindowsPath(selectedFileInfo.ruta_completa) }}</span></div>
            <div class="info-row"><label>Fecha:</label><span>{{ formatDate(selectedFileInfo.fecha_disposicion) }}</span></div>
            <div class="info-row"><label>Evaluado:</label><span>{{ selectedFileInfo.evaluado ? 'Si' : 'No' }}</span></div>
            <div class="info-row"><label>Aprobado:</label><span>{{ selectedFileInfo.aprobado ? 'Si' : 'No' }}</span></div>
            <div v-if="selectedFileInfo.observaciones_evaluacion" class="info-row observaciones">
              <label>Observaciones:</label>
              <span>{{ selectedFileInfo.observaciones_evaluacion }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button v-if="canEdit" @click="editObservaciones(selectedFileInfo)" class="btn-primary">Editar Notas</button>
          <button v-if="canDelete" @click="deleteFile(selectedFileInfo)" class="btn-danger">Eliminar</button>
          <button @click="closeFileInfoModal" class="btn-secondary">Cerrar</button>
        </div>
      </div>
    </div>

    <!-- Modal de Observaciones -->
    <div v-if="showObservacionesModal" class="modal-overlay" @click="closeObservacionesModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3><i class="material-icons">edit_note</i> Observaciones</h3>
          <button @click="closeObservacionesModal" class="modal-close"><i class="material-icons">close</i></button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Observaciones de Evaluacion:</label>
            <textarea v-model="observacionesForm" placeholder="Ingrese observaciones..." rows="5"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeObservacionesModal" class="btn-secondary">Cancelar</button>
          <button @click="saveObservaciones" class="btn-primary">Guardar</button>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmacion de Eliminacion -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header warning">
          <h3><i class="material-icons">warning</i> Confirmar Eliminacion</h3>
          <button @click="closeDeleteModal" class="modal-close"><i class="material-icons">close</i></button>
        </div>
        <div class="modal-body">
          <p><strong>Esta seguro de eliminar este directorio?</strong></p>
          <p>Directorio: <code>{{ directorioAEliminar?.nombre_directorio }}</code></p>
          <div v-if="directorioAEliminar?.total_archivos > 0" class="warning-box">
            <i class="material-icons">warning</i>
            <p>Este directorio contiene <strong>{{ directorioAEliminar.total_archivos }} archivos</strong> que tambien seran eliminados.</p>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeDeleteModal" class="btn-secondary">Cancelar</button>
          <button @click="confirmarEliminacion" class="btn-danger">Eliminar</button>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmacion Masiva -->
    <div v-if="showConfirmacionMasiva" class="modal-overlay" @click="showConfirmacionMasiva = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3><i class="material-icons">grading</i> Confirmar Calificacion Masiva</h3>
          <button @click="showConfirmacionMasiva = false" class="modal-close"><i class="material-icons">close</i></button>
        </div>
        <div class="modal-body">
          <p>Se aplicara la calificacion a <strong>{{ archivosSeleccionadosCount }}</strong> archivos.</p>
          <p>Calificacion: <strong>{{ getCalificacionText(calificacionMasivaSeleccionada) }}</strong></p>
          <p>Filtro: <strong>{{ filtroMasivo }}</strong></p>
        </div>
        <div class="modal-footer">
          <button @click="showConfirmacionMasiva = false" class="btn-secondary">Cancelar</button>
          <button @click="aplicarCalificacionMasiva" class="btn-primary">Aplicar</button>
        </div>
      </div>
    </div>

    <!-- Notificacion -->
    <div v-if="notification.show" :class="['notification', notification.type]">
      <div class="notification-content">
        <i class="material-icons">{{ notification.icon }}</i>
        <span>{{ notification.message }}</span>
      </div>
      <button @click="closeNotification" class="notification-close"><i class="material-icons">close</i></button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { format, parseISO } from 'date-fns'
import { es } from 'date-fns/locale'
import { getMunicipioById } from '@/api/municipios'
import api, { API_URL } from '@/api/config'
import { linuxToWindowsPath } from '@/utils/pathUtils'

interface EvaluacionArchivo {
  id_evaluacion: number
  id_archivo: number
  cod_dir_operacion: number
  nombre_archivo: string
  ruta_completa: string
  fecha_disposicion: string | null
  evaluacion_archivo: number | null
  estado_archivo: string
  observaciones_evaluacion: string | null
  evaluado: boolean
  aprobado: boolean
}

interface Calificacion {
  id: number
  concepto: string
  valor: number
}

interface DirectorioOptimizado {
  id_disposicion: number
  nombre_directorio: string
  jerarquia_completa: string
  nivel: number
  es_padre: boolean
  archivos: EvaluacionArchivo[]
  subdirectorios: DirectorioOptimizado[]
  total_archivos: number
  subdirectorios_count: number
  pendientes: number
  evaluados: number
  aprobados: number
}

export default defineComponent({
  name: 'OperacionDetalle',

  setup() {
    const route = useRoute()
    const router = useRouter()
    const authStore = useAuthStore()

    // Estado
    const loading = ref(false)
    const error = ref<string | null>(null)
    const municipioName = ref('')
    const accessDenied = ref(false)

    // Datos
    const evaluacionesArchivos = ref<EvaluacionArchivo[]>([])
    const calificaciones = ref<Calificacion[]>([])
    const directoriosPadre = ref<DirectorioOptimizado[]>([])
    const directoriosData = ref<any[]>([])

    // UI
    const directoriosExpandidos = ref<Record<number, boolean>>({})
    const archivosExpandidos = ref<Record<number, boolean>>({})

    // Filtros
    const searchTerm = ref('')
    const filtroEstado = ref('')
    const filtroMecanismo = ref('')

    // Modales
    const showFileInfoModal = ref(false)
    const selectedFileInfo = ref<EvaluacionArchivo | null>(null)
    const showObservacionesModal = ref(false)
    const editingFile = ref<EvaluacionArchivo | null>(null)
    const observacionesForm = ref('')
    const showDeleteModal = ref(false)
    const directorioAEliminar = ref<DirectorioOptimizado | null>(null)

    // Calificacion masiva
    const modoCalificacionMasiva = ref(false)
    const archivosSeleccionados = ref<Set<number>>(new Set())
    const filtroMasivo = ref<'todos' | 'no_calificados' | 'excepto_aprobados'>('no_calificados')
    const calificacionMasivaSeleccionada = ref<number | null>(null)
    const aplicandoCalificacion = ref(false)
    const showConfirmacionMasiva = ref(false)
    const ultimoLoteMasivo = ref<any>(null)

    // Notificaciones
    const notification = ref({
      show: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning' | 'info',
      icon: 'check_circle',
      timeout: null as number | null
    })

    // Computed
    const userPermissions = computed(() => ({
      isSuperAdmin: authStore.isSuperAdmin,
      isAdmin: authStore.isAdmin,
      isProfesional: authStore.isProfesional,
      isAnyAdmin: authStore.isAnyAdmin
    }))

    const isProfesionalSinAcceso = computed(() => {
      return userPermissions.value.isProfesional && !userPermissions.value.isAnyAdmin && accessDenied.value
    })

    const tieneAccesoADatos = computed(() => {
      if (userPermissions.value.isAnyAdmin) return true
      if (userPermissions.value.isProfesional) return !accessDenied.value && !loading.value && !error.value
      return !error.value && !loading.value
    })

    const canEdit = computed(() => userPermissions.value.isSuperAdmin || userPermissions.value.isAdmin)
    const canDelete = computed(() => userPermissions.value.isSuperAdmin || userPermissions.value.isAdmin)
    const canDownload = computed(() => userPermissions.value.isSuperAdmin || userPermissions.value.isAdmin || userPermissions.value.isProfesional)
    const canUseMassQualification = computed(() => userPermissions.value.isSuperAdmin)

    const accessLevelText = computed(() => {
      if (userPermissions.value.isSuperAdmin) return 'Super Admin'
      if (userPermissions.value.isAdmin) return 'Admin'
      if (userPermissions.value.isProfesional) return 'Profesional'
      return 'Lectura'
    })

    const accessLevelIcon = computed(() => {
      if (userPermissions.value.isSuperAdmin) return 'admin_panel_settings'
      if (userPermissions.value.isAdmin) return 'settings'
      if (userPermissions.value.isProfesional) return 'work'
      return 'visibility'
    })

    const accessLevelClass = computed(() => {
      if (userPermissions.value.isSuperAdmin) return 'super-admin'
      if (userPermissions.value.isAdmin) return 'admin'
      if (userPermissions.value.isProfesional) return 'profesional'
      return 'readonly'
    })

    const estadisticas = computed(() => {
      const total_archivos = evaluacionesArchivos.value.length
      const pendientes = evaluacionesArchivos.value.filter(a => a.estado_archivo === 'PENDIENTE').length
      const evaluados = evaluacionesArchivos.value.filter(a => a.evaluado).length
      const aprobados = evaluacionesArchivos.value.filter(a => a.aprobado).length
      return { total_directorios: directoriosPadre.value.length, total_archivos, pendientes, evaluados, aprobados }
    })

    const estadisticasFiltradas = computed(() => {
      if (!filtroMecanismo.value) return estadisticas.value
      const archivosDelMecanismo = evaluacionesArchivos.value.filter(a => extraerMecanismoDesdeRuta(a.ruta_completa) === filtroMecanismo.value)
      return {
        total_directorios: directoriosFiltrados.value.length,
        total_archivos: archivosDelMecanismo.length,
        pendientes: archivosDelMecanismo.filter(a => a.estado_archivo === 'PENDIENTE').length,
        evaluados: archivosDelMecanismo.filter(a => a.evaluado).length,
        aprobados: archivosDelMecanismo.filter(a => a.aprobado).length
      }
    })

    const directoriosFiltrados = computed(() => {
      if (!filtroMecanismo.value) return directoriosPadre.value
      return directoriosPadre.value
    })

    const mecanismosDisponibles = computed(() => {
      const mecanismos = new Set<string>()
      evaluacionesArchivos.value.forEach(archivo => {
        const mec = extraerMecanismoDesdeRuta(archivo.ruta_completa)
        if (mec && !['SIN_MECANISMO', 'ERROR_MECANISMO'].includes(mec)) mecanismos.add(mec)
      })
      return Array.from(mecanismos).sort()
    })

    const tienesFiltrosActivos = computed(() => searchTerm.value !== '' || filtroEstado.value !== '' || filtroMecanismo.value !== '')

    const archivosSeleccionadosCount = computed(() => archivosSeleccionados.value.size)
    const archivosParaCalificar = computed(() => evaluacionesArchivos.value)
    const archivosFiltradosPorMasivo = computed(() => {
      let archivos = evaluacionesArchivos.value
      if (filtroMasivo.value === 'no_calificados') archivos = archivos.filter(a => a.evaluacion_archivo === 1 || a.evaluacion_archivo === null)
      else if (filtroMasivo.value === 'excepto_aprobados') archivos = archivos.filter(a => !a.aprobado)
      return archivos
    })

    // Funciones
    const extraerMecanismoDesdeRuta = (ruta: string): string => {
      if (!ruta) return 'SIN_MECANISMO'
      try {
        const rutaStr = ruta.replace(/\\/g, '/')
        const match = rutaStr.match(/\/(\d{2})\/(\d{3})\/([^\/]+)\/02_oper/)
        if (match) return match[3].trim() || 'SIN_MECANISMO'
        return 'SIN_MECANISMO'
      } catch { return 'ERROR_MECANISMO' }
    }

    const getCountMecanismo = (mecanismo: string): number => {
      return evaluacionesArchivos.value.filter(a => extraerMecanismoDesdeRuta(a.ruta_completa) === mecanismo).length
    }

    const getCalificaciones = async () => {
      try {
        const response = await api.get('/app/api/operacion-arbol/calificaciones/')
        let data = response
        if (response && typeof response === 'object' && 'data' in response) data = response.data
        if (Array.isArray(data)) return data
        if (data && typeof data === 'object' && Array.isArray(data.results)) return data.results
        return []
      } catch { return [] }
    }

    const ordenarPorNombreNumerico = (directorios: DirectorioOptimizado[]): DirectorioOptimizado[] => {
      return directorios.sort((a, b) => {
        const numA = parseInt(a.nombre_directorio.match(/^(\d+)/)?.[1] || '999')
        const numB = parseInt(b.nombre_directorio.match(/^(\d+)/)?.[1] || '999')
        if (!isNaN(numA) && !isNaN(numB)) return numA - numB
        if (!isNaN(numA)) return -1
        if (!isNaN(numB)) return 1
        return a.nombre_directorio.localeCompare(b.nombre_directorio, 'es', { numeric: true })
      })
    }

    const construirArbolOptimizado = (directoriosDataArr: any[], archivosData: EvaluacionArchivo[]): DirectorioOptimizado[] => {
      const archivosPorDisposicion = new Map<number, EvaluacionArchivo[]>()
      archivosData.forEach(archivo => {
        const key = archivo.cod_dir_operacion
        if (!archivosPorDisposicion.has(key)) archivosPorDisposicion.set(key, [])
        archivosPorDisposicion.get(key)!.push(archivo)
      })

      const directoriosRaizMap = new Map<string, any[]>()
      directoriosDataArr.forEach(dir => {
        if (!dir.jerarquia_completa) return
        const partes = dir.jerarquia_completa.split('/').filter((p: string) => p.trim() !== '')
        const directorioRaiz = (partes[0] || dir.jerarquia_completa).toLowerCase()
        if (!directoriosRaizMap.has(directorioRaiz)) directoriosRaizMap.set(directorioRaiz, [])
        directoriosRaizMap.get(directorioRaiz)!.push(dir)
      })

      const resultado: DirectorioOptimizado[] = []

      directoriosRaizMap.forEach((directoriosDelGrupo, nombreRaiz) => {
        const directorioPadre = directoriosDelGrupo.find((d: any) => {
          const partes = d.jerarquia_completa.split('/').filter((p: string) => p.trim() !== '')
          return partes.length === 1
        }) || directoriosDelGrupo[0]

        const subdirectoriosData = directoriosDelGrupo.filter((d: any) => {
          const partes = d.jerarquia_completa.split('/').filter((p: string) => p.trim() !== '')
          return partes.length > 1 && d !== directorioPadre
        })

        // Construir subdirectorios nivel 1
        const subdirectoriosNivel1Map = new Map<string, any[]>()
        subdirectoriosData.forEach((sub: any) => {
          const partes = sub.jerarquia_completa.split('/').filter((p: string) => p.trim() !== '')
          if (partes.length >= 2) {
            const nivel1 = partes[1].toLowerCase()
            if (!subdirectoriosNivel1Map.has(nivel1)) subdirectoriosNivel1Map.set(nivel1, [])
            subdirectoriosNivel1Map.get(nivel1)!.push(sub)
          }
        })

        const subdirectoriosOptimizados: DirectorioOptimizado[] = []

        subdirectoriosNivel1Map.forEach((subdirs, nombreSub) => {
          const subPrincipal = subdirs.find((s: any) => {
            const partes = s.jerarquia_completa.split('/').filter((p: string) => p.trim() !== '')
            return partes.length === 2
          }) || subdirs[0]

          // Construir nivel 2
          const subdirectoriosNivel2 = subdirs.filter((s: any) => {
            const partes = s.jerarquia_completa.split('/').filter((p: string) => p.trim() !== '')
            return partes.length >= 3
          })

          const nivel2Map = new Map<string, any[]>()
          subdirectoriosNivel2.forEach((sub2: any) => {
            const partes = sub2.jerarquia_completa.split('/').filter((p: string) => p.trim() !== '')
            if (partes.length >= 3) {
              const nivel2Nombre = partes[2].toLowerCase()
              if (!nivel2Map.has(nivel2Nombre)) nivel2Map.set(nivel2Nombre, [])
              nivel2Map.get(nivel2Nombre)!.push(sub2)
            }
          })

          const subdirectoriosNivel2Optimizados: DirectorioOptimizado[] = []

          nivel2Map.forEach((subdirs2, nombreSub2) => {
            const sub2Principal = subdirs2[0]

            // Construir nivel 3
            const subdirectoriosNivel3 = subdirs2.filter((s: any) => {
              const partes = s.jerarquia_completa.split('/').filter((p: string) => p.trim() !== '')
              return partes.length >= 4
            })

            const nivel3Map = new Map<string, any[]>()
            subdirectoriosNivel3.forEach((sub3: any) => {
              const partes = sub3.jerarquia_completa.split('/').filter((p: string) => p.trim() !== '')
              if (partes.length >= 4) {
                const nivel3Nombre = partes[3].toLowerCase()
                if (!nivel3Map.has(nivel3Nombre)) nivel3Map.set(nivel3Nombre, [])
                nivel3Map.get(nivel3Nombre)!.push(sub3)
              }
            })

            const subdirectoriosNivel3Optimizados: DirectorioOptimizado[] = []
            nivel3Map.forEach((subdirs3, nombreSub3) => {
              const sub3Principal = subdirs3[0]
              const archivosSub3: EvaluacionArchivo[] = []
              subdirs3.forEach((subReg: any) => {
                const archivos = archivosPorDisposicion.get(subReg.id_disposicion) || []
                archivos.forEach(a => archivosSub3.push(a))
              })

              subdirectoriosNivel3Optimizados.push({
                id_disposicion: sub3Principal.id_disposicion,
                nombre_directorio: nombreSub3,
                jerarquia_completa: `02_oper/${sub3Principal.jerarquia_completa}`,
                nivel: 3,
                es_padre: false,
                archivos: archivosSub3,
                subdirectorios: [],
                total_archivos: archivosSub3.length,
                subdirectorios_count: 0,
                pendientes: archivosSub3.filter(a => a.estado_archivo === 'PENDIENTE').length,
                evaluados: archivosSub3.filter(a => a.evaluado).length,
                aprobados: archivosSub3.filter(a => a.aprobado).length
              })
            })

            ordenarPorNombreNumerico(subdirectoriosNivel3Optimizados)

            // Archivos nivel 2
            const archivosSub2: EvaluacionArchivo[] = []
            subdirs2.forEach((subReg: any) => {
              const archivos = archivosPorDisposicion.get(subReg.id_disposicion) || []
              archivos.forEach(a => {
                const yaEsta = subdirectoriosNivel3Optimizados.some(sub3 => sub3.archivos.some(arch => arch.id_evaluacion === a.id_evaluacion))
                if (!yaEsta) archivosSub2.push(a)
              })
            })

            let totalArchivosNivel2 = archivosSub2.length
            subdirectoriosNivel3Optimizados.forEach(sub3 => totalArchivosNivel2 += sub3.total_archivos)

            subdirectoriosNivel2Optimizados.push({
              id_disposicion: sub2Principal.id_disposicion,
              nombre_directorio: nombreSub2,
              jerarquia_completa: `02_oper/${sub2Principal.jerarquia_completa}`,
              nivel: 2,
              es_padre: false,
              archivos: archivosSub2,
              subdirectorios: subdirectoriosNivel3Optimizados,
              total_archivos: totalArchivosNivel2,
              subdirectorios_count: subdirectoriosNivel3Optimizados.length,
              pendientes: archivosSub2.filter(a => a.estado_archivo === 'PENDIENTE').length,
              evaluados: archivosSub2.filter(a => a.evaluado).length,
              aprobados: archivosSub2.filter(a => a.aprobado).length
            })
          })

          ordenarPorNombreNumerico(subdirectoriosNivel2Optimizados)

          // Archivos nivel 1
          const archivosNivel1: EvaluacionArchivo[] = []
          subdirs.forEach((subReg: any) => {
            const archivos = archivosPorDisposicion.get(subReg.id_disposicion) || []
            archivos.forEach(a => {
              const yaEsta = subdirectoriosNivel2Optimizados.some(sub2 =>
                sub2.archivos.some(arch => arch.id_evaluacion === a.id_evaluacion) ||
                sub2.subdirectorios.some(sub3 => sub3.archivos.some(arch => arch.id_evaluacion === a.id_evaluacion))
              )
              if (!yaEsta) archivosNivel1.push(a)
            })
          })

          let totalArchivosNivel1 = archivosNivel1.length
          subdirectoriosNivel2Optimizados.forEach(sub2 => totalArchivosNivel1 += sub2.total_archivos)

          subdirectoriosOptimizados.push({
            id_disposicion: subPrincipal.id_disposicion,
            nombre_directorio: nombreSub,
            jerarquia_completa: `02_oper/${subPrincipal.jerarquia_completa}`,
            nivel: 1,
            es_padre: false,
            archivos: archivosNivel1,
            subdirectorios: subdirectoriosNivel2Optimizados,
            total_archivos: totalArchivosNivel1,
            subdirectorios_count: subdirectoriosNivel2Optimizados.length,
            pendientes: archivosNivel1.filter(a => a.estado_archivo === 'PENDIENTE').length,
            evaluados: archivosNivel1.filter(a => a.evaluado).length,
            aprobados: archivosNivel1.filter(a => a.aprobado).length
          })
        })

        ordenarPorNombreNumerico(subdirectoriosOptimizados)

        // Archivos del padre
        const archivosEnSubdirectorios = new Set<number>()
        subdirectoriosOptimizados.forEach(sub => {
          sub.archivos.forEach(arch => archivosEnSubdirectorios.add(arch.id_evaluacion))
          sub.subdirectorios.forEach(sub2 => {
            sub2.archivos.forEach(arch => archivosEnSubdirectorios.add(arch.id_evaluacion))
            sub2.subdirectorios.forEach(sub3 => {
              sub3.archivos.forEach(arch => archivosEnSubdirectorios.add(arch.id_evaluacion))
            })
          })
        })

        const archivosDelPadre: EvaluacionArchivo[] = []
        directoriosDelGrupo.forEach((dirReg: any) => {
          const archivos = archivosPorDisposicion.get(dirReg.id_disposicion) || []
          archivos.forEach(a => {
            if (!archivosEnSubdirectorios.has(a.id_evaluacion)) archivosDelPadre.push(a)
          })
        })

        let totalArchivos = archivosDelPadre.length
        subdirectoriosOptimizados.forEach(sub => totalArchivos += sub.total_archivos)

        resultado.push({
          id_disposicion: directorioPadre.id_disposicion,
          nombre_directorio: nombreRaiz,
          jerarquia_completa: `02_oper/${nombreRaiz}`,
          nivel: 0,
          es_padre: true,
          archivos: archivosDelPadre,
          subdirectorios: subdirectoriosOptimizados,
          total_archivos: totalArchivos,
          subdirectorios_count: subdirectoriosOptimizados.length,
          pendientes: archivosDelPadre.filter(a => a.estado_archivo === 'PENDIENTE').length,
          evaluados: archivosDelPadre.filter(a => a.evaluado).length,
          aprobados: archivosDelPadre.filter(a => a.aprobado).length
        })
      })

      return ordenarPorNombreNumerico(resultado)
    }

    const loadData = async () => {
      try {
        loading.value = true
        error.value = null
        accessDenied.value = false

        const municipioId = Number(route.params.id)
        if (!municipioId || isNaN(municipioId)) {
          error.value = 'ID de municipio invalido'
          return
        }

        try {
          const municipio = await getMunicipioById(municipioId)
          municipioName.value = municipio?.nom_municipio || `Municipio ${municipioId}`
        } catch { municipioName.value = `Municipio ${municipioId}` }

        const calificacionesData = await getCalificaciones()
        calificaciones.value = calificacionesData

        // Cargar directorios
        const dirsResponse = await api.get(`/app/api/operacion-arbol/arbol_directorios/?municipio_id=${municipioId}`)
        const directoriosDataFromAPI = dirsResponse.directorios || dirsResponse || []

        // Cargar evaluaciones
        const evalResponse = await api.get(`/app/api/operacion-arbol/evaluaciones/?municipio_id=${municipioId}`)
        const archivosData = evalResponse.evaluaciones || evalResponse || []

        evaluacionesArchivos.value = archivosData
        directoriosData.value = directoriosDataFromAPI

        const arbolOptimizado = construirArbolOptimizado(directoriosDataFromAPI, archivosData)
        directoriosPadre.value = arbolOptimizado

        // Pre-seleccionar mecanismo desde URL
        const mecanismoFromUrl = route.query.mecanismo as string | undefined
        if (mecanismoFromUrl) {
          filtroMecanismo.value = mecanismoFromUrl
        }

      } catch (err: any) {
        console.error('Error cargando datos:', err)
        if (err.response?.status === 403 && userPermissions.value.isProfesional) {
          accessDenied.value = true
        } else {
          error.value = 'Error al cargar los datos de operacion'
        }
      } finally {
        loading.value = false
      }
    }

    // UI Handlers
    const toggleDirectorio = (id: number) => { directoriosExpandidos.value[id] = !directoriosExpandidos.value[id] }
    const toggleArchivos = (id: number) => { archivosExpandidos.value[id] = !archivosExpandidos.value[id] }

    const filtrarArchivos = (archivos: EvaluacionArchivo[]): EvaluacionArchivo[] => {
      if (!archivos || archivos.length === 0) return []
      let resultado = [...archivos]
      if (searchTerm.value.trim()) {
        const search = searchTerm.value.toLowerCase()
        resultado = resultado.filter(a => a.nombre_archivo.toLowerCase().includes(search))
      }
      if (filtroEstado.value) {
        if (filtroEstado.value === 'EVALUADO') resultado = resultado.filter(a => a.evaluado)
        else if (filtroEstado.value === 'APROBADO') resultado = resultado.filter(a => a.aprobado)
        else resultado = resultado.filter(a => a.estado_archivo === filtroEstado.value)
      }
      if (filtroMecanismo.value) {
        resultado = resultado.filter(a => extraerMecanismoDesdeRuta(a.ruta_completa) === filtroMecanismo.value)
      }
      return resultado
    }

    // Utilidades
    const getFileIcon = (fileName: string): string => {
      const ext = fileName.split('.').pop()?.toLowerCase() || ''
      const icons: Record<string, string> = {
        pdf: 'picture_as_pdf', zip: 'archive', rar: 'archive', '7z': 'archive', gdb: 'storage',
        jpg: 'image', jpeg: 'image', png: 'image', gif: 'image',
        doc: 'description', docx: 'description', xls: 'table_chart', xlsx: 'table_chart'
      }
      return icons[ext] || 'insert_drive_file'
    }

    const getEstadoClass = (estado: string): string => {
      const classes: Record<string, string> = { 'PENDIENTE': 'pendiente', 'EVALUADO': 'evaluado', 'APROBADO': 'aprobado' }
      return classes[estado] || 'pendiente'
    }

    const getCalificacionText = (evaluacionId: number | null): string => {
      if (!evaluacionId) return 'Sin calificar'
      const cal = calificaciones.value.find(c => c.id === evaluacionId)
      return cal ? `${cal.concepto} (${cal.valor})` : 'No encontrada'
    }

    const formatDate = (dateStr: string | null): string => {
      if (!dateStr) return 'Sin fecha'
      try { return format(parseISO(dateStr), 'dd/MM/yyyy', { locale: es }) }
      catch { return 'Fecha invalida' }
    }

    // Acciones de archivo
    const downloadFile = async (archivo: EvaluacionArchivo) => {
      if (!archivo.ruta_completa) { showNotification('No hay ruta disponible', 'warning'); return }
      try {
        showNotification('Descargando...', 'info')
        const response = await api.get('/preoperacion/ver_pdf/', { params: { ruta: archivo.ruta_completa }, responseType: 'blob' })
        let blobData = response
        if (response && typeof response === 'object' && 'data' in response) blobData = response.data
        const blob = new Blob([blobData])
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = archivo.nombre_archivo
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        showNotification(`Descargando: ${archivo.nombre_archivo}`, 'success')
      } catch (err: any) {
        showNotification(`Error: ${err.message}`, 'error')
      }
    }

    const viewFile = async (archivo: EvaluacionArchivo) => {
      if (!archivo.ruta_completa) { showNotification('No hay ruta disponible', 'warning'); return }
      try {
        const ext = archivo.nombre_archivo.split('.').pop()?.toLowerCase() || ''
        if (['gdb', 'zip', 'rar', '7z'].includes(ext)) { await downloadFile(archivo); return }
        showNotification('Abriendo...', 'info')
        const response = await api.get('/preoperacion/ver_pdf/', { params: { ruta: archivo.ruta_completa }, responseType: 'blob' })
        let blobData = response
        if (response && typeof response === 'object' && 'data' in response) blobData = response.data
        const blob = new Blob([blobData], { type: blobData.type || 'application/octet-stream' })
        const url = window.URL.createObjectURL(blob)
        window.open(url, '_blank')
        setTimeout(() => window.URL.revokeObjectURL(url), 10000)
      } catch (err: any) {
        showNotification(`Error: ${err.message}`, 'error')
      }
    }

    const deleteFile = async (archivo: EvaluacionArchivo | null) => {
      if (!archivo) return
      if (!userPermissions.value.isSuperAdmin && !userPermissions.value.isAdmin) {
        showNotification('Solo administradores pueden eliminar', 'error'); return
      }
      if (!confirm(`Eliminar "${archivo.nombre_archivo}"?`)) return
      try {
        showNotification('Eliminando...', 'info')
        await api.delete(`/app/api/operacion-arbol/${archivo.id_evaluacion}/eliminar/`)
        evaluacionesArchivos.value = evaluacionesArchivos.value.filter(a => a.id_evaluacion !== archivo.id_evaluacion)
        await loadData()
        showNotification('Eliminado', 'success')
        closeFileInfoModal()
      } catch (err: any) {
        showNotification(`Error: ${err.message}`, 'error')
      }
    }

    const actualizarEvaluacion = async (archivo: EvaluacionArchivo) => {
      try {
        showNotification('Actualizando...', 'info')
        const response = await api.patch(`/app/api/operacion-arbol/${archivo.id_evaluacion}/actualizar/`, {
          evaluacion_archivo: archivo.evaluacion_archivo
        })
        const data = response.data || response
        // El backend devuelve el objeto serializado directamente
        const evaluacionData = data.evaluacion || data
        const index = evaluacionesArchivos.value.findIndex(a => a.id_evaluacion === archivo.id_evaluacion)
        if (index !== -1) {
          evaluacionesArchivos.value[index] = { ...evaluacionesArchivos.value[index], ...evaluacionData }
        }
        const arbolOptimizado = construirArbolOptimizado(directoriosData.value, evaluacionesArchivos.value)
        directoriosPadre.value = arbolOptimizado
        showNotification('Actualizado', 'success')
      } catch (err: any) {
        showNotification(`Error: ${err.message}`, 'error')
      }
    }

    // Descargar directorio
    const descargarDirectorio = async (directorio: DirectorioOptimizado) => {
      try {
        showNotification(`Descargando ${directorio.nombre_directorio}...`, 'info')
        const municipioId = route.params.id
        const response = await api.get('/preoperacion/descargar_directorio/', {
          params: { ruta: directorio.jerarquia_completa, municipio_id: municipioId },
          responseType: 'blob'
        })
        let blobData = response
        if (response && typeof response === 'object' && 'data' in response) blobData = response.data
        const blob = new Blob([blobData], { type: 'application/zip' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${directorio.nombre_directorio}.zip`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        showNotification('Descarga iniciada', 'success')
      } catch (err: any) {
        showNotification(`Error: ${err.message}`, 'error')
      }
    }

    // Eliminar directorio
    const eliminarDirectorio = (directorio: DirectorioOptimizado) => {
      if (!userPermissions.value.isSuperAdmin && !userPermissions.value.isAdmin) {
        showNotification('Solo administradores pueden eliminar', 'error'); return
      }
      directorioAEliminar.value = directorio
      showDeleteModal.value = true
    }

    const confirmarEliminacion = async () => {
      if (!directorioAEliminar.value) return
      try {
        showNotification('Eliminando directorio...', 'info')
        await api.delete('/app/api/operacion-arbol/eliminar-directorio/', {
          data: { directorio_id: directorioAEliminar.value.id_disposicion }
        })
        showNotification('Directorio eliminado', 'success')
        await loadData()
        closeDeleteModal()
      } catch (err: any) {
        showNotification(`Error: ${err.message}`, 'error')
      }
    }

    const closeDeleteModal = () => { showDeleteModal.value = false; directorioAEliminar.value = null }

    // Observaciones
    const editObservaciones = (archivo: EvaluacionArchivo | null) => {
      if (!archivo) return
      editingFile.value = archivo
      observacionesForm.value = archivo.observaciones_evaluacion || ''
      showObservacionesModal.value = true
    }

    const saveObservaciones = async () => {
      if (!editingFile.value) return
      try {
        showNotification('Guardando...', 'info')
        await api.patch(`/app/api/operacion-arbol/${editingFile.value.id_evaluacion}/actualizar/`, {
          observaciones_evaluacion: observacionesForm.value
        })
        const index = evaluacionesArchivos.value.findIndex(a => a.id_evaluacion === editingFile.value!.id_evaluacion)
        if (index !== -1) evaluacionesArchivos.value[index].observaciones_evaluacion = observacionesForm.value
        if (selectedFileInfo.value?.id_evaluacion === editingFile.value.id_evaluacion) {
          selectedFileInfo.value.observaciones_evaluacion = observacionesForm.value
        }
        showNotification('Guardado', 'success')
        closeObservacionesModal()
      } catch (err: any) {
        showNotification(`Error: ${err.message}`, 'error')
      }
    }

    const closeObservacionesModal = () => { showObservacionesModal.value = false; editingFile.value = null; observacionesForm.value = '' }

    // Modal de info
    const showFileInfo = (archivo: EvaluacionArchivo) => { selectedFileInfo.value = archivo; showFileInfoModal.value = true }
    const closeFileInfoModal = () => { showFileInfoModal.value = false; selectedFileInfo.value = null }

    // Calificacion masiva
    const toggleModoCalificacionMasiva = () => {
      if (!canUseMassQualification.value) {
        showNotification('Solo Super Admin puede usar calificacion masiva', 'error'); return
      }
      modoCalificacionMasiva.value = !modoCalificacionMasiva.value
      if (!modoCalificacionMasiva.value) {
        archivosSeleccionados.value.clear()
        calificacionMasivaSeleccionada.value = null
      } else {
        cargarUltimoLoteMasivo()
      }
    }

    const toggleArchivoSeleccion = (archivoId: number) => {
      if (archivosSeleccionados.value.has(archivoId)) archivosSeleccionados.value.delete(archivoId)
      else archivosSeleccionados.value.add(archivoId)
      archivosSeleccionados.value = new Set(archivosSeleccionados.value)
    }

    const isArchivoSeleccionado = (archivoId: number): boolean => archivosSeleccionados.value.has(archivoId)

    const toggleDirectorioSeleccion = (directorio: DirectorioOptimizado, seleccionar: boolean) => {
      const obtenerArchivosRecursivo = (dir: DirectorioOptimizado): number[] => {
        let ids: number[] = []
        if (dir.archivos) dir.archivos.forEach(a => ids.push(a.id_evaluacion))
        if (dir.subdirectorios) dir.subdirectorios.forEach(sub => ids = [...ids, ...obtenerArchivosRecursivo(sub)])
        return ids
      }
      const archivosIds = obtenerArchivosRecursivo(directorio)
      if (seleccionar) archivosIds.forEach(id => archivosSeleccionados.value.add(id))
      else archivosIds.forEach(id => archivosSeleccionados.value.delete(id))
      archivosSeleccionados.value = new Set(archivosSeleccionados.value)
    }

    const isDirectorioSeleccionado = (directorio: DirectorioOptimizado): boolean => {
      const obtenerArchivosRecursivo = (dir: DirectorioOptimizado): number[] => {
        let ids: number[] = []
        if (dir.archivos) dir.archivos.forEach(a => ids.push(a.id_evaluacion))
        if (dir.subdirectorios) dir.subdirectorios.forEach(sub => ids = [...ids, ...obtenerArchivosRecursivo(sub)])
        return ids
      }
      const archivosIds = obtenerArchivosRecursivo(directorio)
      if (archivosIds.length === 0) return false
      return archivosIds.every(id => archivosSeleccionados.value.has(id))
    }

    const isDirectorioParcialmenteSeleccionado = (directorio: DirectorioOptimizado): boolean => {
      const obtenerArchivosRecursivo = (dir: DirectorioOptimizado): number[] => {
        let ids: number[] = []
        if (dir.archivos) dir.archivos.forEach(a => ids.push(a.id_evaluacion))
        if (dir.subdirectorios) dir.subdirectorios.forEach(sub => ids = [...ids, ...obtenerArchivosRecursivo(sub)])
        return ids
      }
      const archivosIds = obtenerArchivosRecursivo(directorio)
      if (archivosIds.length === 0) return false
      const seleccionados = archivosIds.filter(id => archivosSeleccionados.value.has(id))
      return seleccionados.length > 0 && seleccionados.length < archivosIds.length
    }

    const seleccionarTodos = () => {
      archivosParaCalificar.value.forEach(a => archivosSeleccionados.value.add(a.id_evaluacion))
      archivosSeleccionados.value = new Set(archivosSeleccionados.value)
    }

    const deseleccionarTodos = () => {
      archivosSeleccionados.value.clear()
      archivosSeleccionados.value = new Set(archivosSeleccionados.value)
    }

    const cargarUltimoLoteMasivo = async () => {
      try {
        const municipioId = route.params.id
        const response = await api.get(`/app/api/operacion-arbol/ultimo_lote_masivo/?municipio_id=${municipioId}`)
        ultimoLoteMasivo.value = response.data || response
      } catch { ultimoLoteMasivo.value = null }
    }

    const mostrarConfirmacionMasiva = () => {
      if (archivosSeleccionadosCount.value === 0) { showNotification('Seleccione archivos', 'warning'); return }
      if (!calificacionMasivaSeleccionada.value) { showNotification('Seleccione calificacion', 'warning'); return }
      showConfirmacionMasiva.value = true
    }

    const aplicarCalificacionMasiva = async () => {
      if (!canUseMassQualification.value) return
      aplicandoCalificacion.value = true
      showConfirmacionMasiva.value = false
      try {
        const response = await api.post('/app/api/operacion-arbol/calificacion_masiva/', {
          archivos_ids: Array.from(archivosSeleccionados.value),
          calificacion_id: calificacionMasivaSeleccionada.value,
          filtro: filtroMasivo.value,
          municipio_id: route.params.id
        })
        const data = response.data || response
        showNotification(data.message || `${data.archivos_calificados || 0} archivos calificados`, 'success')
        archivosSeleccionados.value.clear()
        calificacionMasivaSeleccionada.value = null
        await loadData()
        await cargarUltimoLoteMasivo()
      } catch (err: any) {
        showNotification(`Error: ${err.message}`, 'error')
      } finally {
        aplicandoCalificacion.value = false
      }
    }

    const restaurarCalificacionAnterior = async () => {
      if (!ultimoLoteMasivo.value?.lote_id) { showNotification('No hay lote para restaurar', 'warning'); return }
      if (!confirm(`Restaurar lote ${ultimoLoteMasivo.value.lote_id}?`)) return
      aplicandoCalificacion.value = true
      try {
        const response = await api.post('/app/api/operacion-arbol/restaurar_calificacion/', { lote_id: ultimoLoteMasivo.value.lote_id })
        const data = response.data || response
        showNotification(`${data.archivos_restaurados} archivos restaurados`, 'success')
        await loadData()
        await cargarUltimoLoteMasivo()
      } catch (err: any) {
        showNotification(`Error: ${err.message}`, 'error')
      } finally {
        aplicandoCalificacion.value = false
      }
    }

    // Filtros
    const limpiarFiltros = () => { searchTerm.value = ''; filtroEstado.value = ''; filtroMecanismo.value = '' }
    const clearSearch = () => { searchTerm.value = '' }

    // Navegacion
    const goBack = () => { router.back() }
    const refreshData = async () => { await loadData(); showNotification('Datos actualizados', 'success') }

    // Notificaciones
    const showNotification = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
      if (notification.value.timeout) clearTimeout(notification.value.timeout)
      const icons = { success: 'check_circle', error: 'error', warning: 'warning', info: 'info' }
      notification.value = { show: true, message, type, icon: icons[type], timeout: null }
      notification.value.timeout = window.setTimeout(() => closeNotification(), 5000)
    }

    const closeNotification = () => {
      if (notification.value.timeout) clearTimeout(notification.value.timeout)
      notification.value.show = false
    }

    onMounted(() => { loadData() })

    return {
      // Estado
      route, loading, error, municipioName, accessDenied,
      evaluacionesArchivos, calificaciones, directoriosPadre,
      directoriosExpandidos, archivosExpandidos,
      searchTerm, filtroEstado, filtroMecanismo,
      showFileInfoModal, selectedFileInfo, showObservacionesModal, editingFile, observacionesForm,
      showDeleteModal, directorioAEliminar,
      modoCalificacionMasiva, archivosSeleccionados, filtroMasivo, calificacionMasivaSeleccionada,
      aplicandoCalificacion, showConfirmacionMasiva, ultimoLoteMasivo,
      notification,

      // Computed
      userPermissions, isProfesionalSinAcceso, tieneAccesoADatos,
      canEdit, canDelete, canDownload, canUseMassQualification,
      accessLevelText, accessLevelIcon, accessLevelClass,
      estadisticas, estadisticasFiltradas, directoriosFiltrados,
      mecanismosDisponibles, tienesFiltrosActivos,
      archivosSeleccionadosCount, archivosParaCalificar, archivosFiltradosPorMasivo,

      // Metodos
      loadData, toggleDirectorio, toggleArchivos, filtrarArchivos,
      getFileIcon, getEstadoClass, getCalificacionText, formatDate, linuxToWindowsPath,
      getCountMecanismo,
      downloadFile, viewFile, deleteFile, actualizarEvaluacion,
      descargarDirectorio, eliminarDirectorio, confirmarEliminacion, closeDeleteModal,
      editObservaciones, saveObservaciones, closeObservacionesModal,
      showFileInfo, closeFileInfoModal,
      toggleModoCalificacionMasiva, toggleArchivoSeleccion, isArchivoSeleccionado,
      toggleDirectorioSeleccion, isDirectorioSeleccionado, isDirectorioParcialmenteSeleccionado,
      seleccionarTodos, deseleccionarTodos, mostrarConfirmacionMasiva,
      aplicarCalificacionMasiva, restaurarCalificacionAnterior,
      limpiarFiltros, clearSearch, goBack, refreshData, closeNotification
    }
  }
})
</script>

<style scoped>
.productos-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  padding: 1.5rem;
}

.operacion-page .page-header.operacion-header {
  background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
}

.page-header {
  border-radius: 12px;
  padding: 1.5rem 2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-back {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 8px;
  padding: 0.5rem;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background 0.2s;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.3);
}

.header-info h1 {
  color: white;
  margin: 0;
  font-size: 1.75rem;
  font-weight: 600;
}

.header-subtitle {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.access-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 0.875rem;
}

.btn-refresh {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 8px;
  padding: 0.5rem;
  color: white;
  cursor: pointer;
  display: flex;
  transition: background 0.2s;
}

.btn-refresh:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
}

.loading-container, .error-container, .access-denied-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  text-align: center;
  gap: 1rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #A0522D;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container i, .access-denied-container i {
  font-size: 4rem;
  color: #6c757d;
}

.btn-retry, .btn-back-large {
  padding: 0.75rem 1.5rem;
  background: #A0522D;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Panel de calificacion masiva */
.mass-qualification-panel {
  background: white;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.mass-qualification-panel.expanded {
  border: 2px solid #A0522D;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  cursor: pointer;
  background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
  color: white;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 600;
}

.badge-active {
  background: white;
  color: #A0522D;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.panel-content {
  padding: 1.5rem;
  background: #fafafa;
}

.mass-qual-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.control-group label {
  font-weight: 500;
  min-width: 150px;
}

.select-filtro, .select-calificacion {
  padding: 0.5rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  min-width: 200px;
}

.selection-info {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  color: #6c757d;
}

.selection-info .count {
  font-weight: 600;
  color: #A0522D;
}

.mass-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-select-all, .btn-deselect-all, .btn-apply-mass, .btn-restore {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-select-all {
  background: #17a2b8;
  color: white;
}

.btn-deselect-all {
  background: #6c757d;
  color: white;
}

.btn-apply-mass {
  background: #28a745;
  color: white;
}

.btn-apply-mass:disabled {
  background: #94d3a2;
  cursor: not-allowed;
}

.btn-restore {
  background: #ffc107;
  color: #212529;
}

.ultimo-lote-info {
  margin-top: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.lote-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.lote-details {
  display: flex;
  gap: 1rem;
  color: #6c757d;
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
}

/* Estadisticas */
.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.stat-card i {
  font-size: 2rem;
  color: #A0522D;
}

.stat-card.pending i { color: #ffc107; }
.stat-card.evaluated i { color: #17a2b8; }
.stat-card.approved i { color: #28a745; }

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #212529;
}

.stat-label {
  font-size: 0.875rem;
  color: #6c757d;
}

/* Filtros */
.filters-section {
  background: white;
  border-radius: 12px;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.search-box {
  display: flex;
  align-items: center;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.search-box input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 1rem;
  outline: none;
}

.clear-btn {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
}

.filters-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  min-width: 180px;
}

.btn-clear-filters {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
}

/* Arbol de directorios */
.tree-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.tree-header {
  padding: 1.25rem;
  border-bottom: 1px solid #dee2e6;
}

.tree-header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #212529;
}

.tree-content {
  padding: 1rem;
}

.directorio-padre {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  margin-bottom: 0.75rem;
  overflow: hidden;
}

.directorio-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

/* Colores por nivel de profundidad - tonos suaves como Productos */
.directorio-header.nivel-0 {
  background: linear-gradient(135deg, #fdf6f0, #faf0e6);
  border-left: 3px solid #CD853F;
}
.directorio-header.nivel-0:hover {
  background: linear-gradient(135deg, #f5e6d8, #ecdcc8);
}
.directorio-header.nivel-0 .folder-icon { color: #CD853F !important; }

.directorio-header.nivel-1 {
  background: linear-gradient(135deg, #fff8f0, #fff5eb);
  padding-left: 2rem;
  border-left: 3px solid #DEB887;
}
.directorio-header.nivel-1:hover {
  background: linear-gradient(135deg, #ffeddb, #ffe4cc);
}
.directorio-header.nivel-1 .folder-icon { color: #D2691E !important; }

.directorio-header.nivel-2 {
  background: linear-gradient(135deg, #fffaf5, #fff7f0);
  padding-left: 3rem;
  border-left: 3px solid #F5DEB3;
}
.directorio-header.nivel-2:hover {
  background: linear-gradient(135deg, #fff0e0, #ffe8d5);
}
.directorio-header.nivel-2 .folder-icon { color: #DEB887 !important; }

.directorio-header.nivel-3 {
  background: linear-gradient(135deg, #fffcfa, #fff9f5);
  padding-left: 4rem;
  border-left: 3px solid #FAEBD7;
}
.directorio-header.nivel-3:hover {
  background: linear-gradient(135deg, #fff5eb, #ffefe0);
}
.directorio-header.nivel-3 .folder-icon { color: #E6C9A8 !important; }

.directorio-header:hover {
  box-shadow: 0 2px 8px rgba(205,133,63,0.15);
}

.checkbox-directorio, .checkbox-archivo {
  display: flex;
  align-items: center;
}

.checkbox-directorio input, .checkbox-archivo input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.folder-icon {
  color: #A0522D;
}

.directorio-nombre {
  flex: 1;
  font-weight: 500;
}

.directorio-stats {
  display: flex;
  gap: 0.5rem;
}

.stat-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.stat-badge.files { background: #e3f2fd; color: #1976d2; }
.stat-badge.subdirs { background: #fff3e0; color: #f57c00; }

.directorio-actions {
  display: flex;
  gap: 0.25rem;
}

.btn-download-dir, .btn-delete-dir {
  background: none;
  border: none;
  padding: 0.25rem;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  transition: background 0.2s;
}

.btn-download-dir { color: #17a2b8; }
.btn-download-dir:hover { background: #17a2b820; }

.btn-delete-dir { color: #dc3545; }
.btn-delete-dir:hover { background: #dc354520; }

.expand-icon { color: #6c757d; }

.directorio-content {
  border-top: 1px solid #e9ecef;
}

.directorio-content.nivel-0 { padding: 0.5rem; }
.directorio-content.nivel-1 { padding-left: 1rem; }
.directorio-content.nivel-2 { padding-left: 1.5rem; }
.directorio-content.nivel-3 { padding-left: 2rem; }

.subdirectorio {
  border: 1px solid #e9ecef;
  border-radius: 6px;
  margin: 0.5rem 0;
  overflow: hidden;
}

/* Archivos */
.archivos-seccion {
  margin: 0.5rem 0;
  padding: 0.5rem;
  background: #fafafa;
  border-radius: 6px;
}

.archivos-header {
  margin-bottom: 0.5rem;
}

.btn-toggle-archivos {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: 1px solid #dee2e6;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  color: #495057;
  transition: all 0.2s;
}

.btn-toggle-archivos:hover {
  background: #e9ecef;
}

.archivos-lista {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.archivo-item {
  display: grid;
  grid-template-columns: auto auto 1fr auto auto auto auto;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  transition: all 0.2s;
  font-size: 0.85rem;
}

.archivo-item:hover {
  border-color: #A0522D;
}

.archivo-item.seleccionado-masivo {
  background: #fff3e0;
  border-color: #A0522D;
}

.archivo-icon {
  color: #6c757d;
}

.archivo-info {
  min-width: 0;
  overflow: hidden;
}

.archivo-nombre {
  display: block;
  font-weight: 500;
  font-size: 0.85rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 250px;
}

.archivo-fecha {
  font-size: 0.75rem;
  color: #6c757d;
}

.estado-badge {
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  white-space: nowrap;
}

.estado-badge.pendiente { background: #fff3cd; color: #856404; }
.estado-badge.evaluado { background: #cce5ff; color: #004085; }
.estado-badge.aprobado { background: #d4edda; color: #155724; }

.archivo-status {
  display: flex;
  gap: 0.25rem;
}

.status-icon {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6rem;
  font-weight: 700;
}

.status-icon.ok { background: #28a745; color: white; }
.status-icon.no { background: #dee2e6; color: #6c757d; }

.archivo-calificacion {
  min-width: 180px;
  max-width: 220px;
}

.select-calificacion-mini {
  padding: 0.2rem 0.4rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 0.75rem;
  width: 100%;
  background: #f8f9fa;
}

.cal-readonly {
  font-size: 0.8rem;
  color: #6c757d;
}

.archivo-acciones {
  display: flex;
  gap: 0.25rem;
}

.btn-accion {
  background: none;
  border: none;
  padding: 0.25rem;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  transition: all 0.2s;
}

.btn-accion i { font-size: 1rem; }

.btn-accion.info { color: #17a2b8; }
.btn-accion.info:hover { background: #17a2b820; }

.btn-accion.view { color: #6c757d; }
.btn-accion.view:hover { background: #6c757d20; }

.btn-accion.download { color: #28a745; }
.btn-accion.download:hover { background: #28a74520; }

.btn-accion.edit { color: #ffc107; }
.btn-accion.edit:hover { background: #ffc10720; }

.btn-accion.delete { color: #dc3545; }
.btn-accion.delete:hover { background: #dc354520; }

/* Empty state */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
}

.empty-state i {
  font-size: 4rem;
  margin-bottom: 1rem;
}

/* Modales */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem;
  border-bottom: 1px solid #dee2e6;
}

.modal-header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-header.warning h3 { color: #dc3545; }

.modal-close {
  background: none;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  color: #6c757d;
}

.modal-body {
  padding: 1.5rem;
}

.file-info-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-row {
  display: flex;
  gap: 0.75rem;
}

.info-row label {
  font-weight: 600;
  min-width: 100px;
  color: #495057;
}

.info-row.observaciones {
  flex-direction: column;
}

.ruta-text {
  word-break: break-all;
  font-family: monospace;
  font-size: 0.85rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
}

.form-group textarea {
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  resize: vertical;
}

.warning-box {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background: #fff3cd;
  border-radius: 6px;
  margin: 1rem 0;
}

.warning-box i {
  color: #856404;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid #dee2e6;
}

.btn-primary, .btn-secondary, .btn-danger {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-primary { background: #A0522D; color: white; }
.btn-secondary { background: #6c757d; color: white; }
.btn-danger { background: #dc3545; color: white; }

/* Notificacion */
.notification {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  color: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1001;
}

.notification.success { background: #28a745; }
.notification.error { background: #dc3545; }
.notification.warning { background: #ffc107; color: #212529; }
.notification.info { background: #17a2b8; }

.notification-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.notification-close {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
}

@media (max-width: 768px) {
  .productos-page { padding: 1rem; }
  .header-content { flex-direction: column; gap: 1rem; }
  .stats-section { grid-template-columns: repeat(2, 1fr); }
  .archivo-item {
    grid-template-columns: auto 1fr auto;
    gap: 0.25rem;
  }
  .archivo-icon { display: none; }
  .estado-badge { display: none; }
  .archivo-status { display: none; }
  .archivo-acciones { grid-column: span 3; justify-content: flex-end; }
}
</style>
