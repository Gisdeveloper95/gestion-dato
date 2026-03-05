<template>
  <div class="productos-detalle-page">
    <!-- Header Simplificado -->
    <header class="page-header">
      <div class="header-content">
        <button @click="goBack" class="btn-back">
          <i class="material-icons">arrow_back</i>
          Volver
        </button>
        <div class="header-info">
          <h1>Productos - {{ municipioName }}</h1>
          <div class="access-badge" :class="accessLevelClass">
            <i class="material-icons">{{ accessLevelIcon }}</i>
            <span>{{ accessLevelText }}</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Mensaje para Profesionales sin Acceso -->
    <div v-if="!loading && isProfesionalSinAcceso" class="access-denied-container">
      <div class="access-denied-card">
        <i class="material-icons">lock</i>
        <h2>Acceso Restringido</h2>
        <p>No tienes permisos para acceder a los productos de este municipio.</p>
        <button @click="goBack" class="btn-back-denied">
          <i class="material-icons">arrow_back</i>
          Volver a productos
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-else-if="loading" class="loading-container">
      <div class="spinner"></div>
      <span>Cargando productos...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error && !isProfesionalSinAcceso" class="error-container">
      <i class="material-icons">error</i>
      <p>{{ error }}</p>
      <button @click="reloadData" class="btn-retry">Reintentar</button>
    </div>

    <!-- Main Content -->
    <main v-else-if="tieneAccesoADatos" class="main-content">
      <!-- Filtros Mejorados con Mecanismo -->
      <section class="filters-section">
        <div class="filters-container">
          <div class="search-box">
            <i class="material-icons">search</i>
            <input 
              v-model="searchTerm"
              placeholder="Buscar archivo..."
              @input="aplicarFiltros"
            />
            <button v-if="searchTerm" @click="clearSearch" class="clear-btn">
              <i class="material-icons">close</i>
            </button>
          </div>
          
          <!-- Filtro de Mecanismo -->
          <select v-model="filtroMecanismo" @change="aplicarFiltros" class="filtro-mecanismo">
            <option value="">Todos los mecanismos</option>
            <option v-for="mecanismo in mecanismosDisponibles" :key="mecanismo" :value="mecanismo">
              {{ mecanismo }} ({{ getCountMecanismo(mecanismo) }})
            </option>
          </select>
          
          <select v-model="filtroEstado" @change="aplicarFiltros">
            <option value="">Todos los estados</option>
            <option value="PENDIENTE">Pendientes</option>
            <option value="EVALUADO">Evaluados</option>
            <option value="APROBADO">Aprobados</option>
          </select>
          
          <button @click="refreshData" class="btn-refresh" :disabled="loading">
            <i class="material-icons">refresh</i>
            Actualizar
          </button>

          <!-- Botón limpiar filtros -->
          <button v-if="tienesFiltrosActivos" @click="limpiarFiltros" class="btn-clear-filters">
            <i class="material-icons">clear_all</i>
            Limpiar
          </button>
        </div>

        <!-- Información del filtro activo -->
        <div v-if="filtroMecanismo" class="filtro-activo-info">
          <i class="material-icons">filter_alt</i>
          <span>Filtrando por mecanismo: <strong>{{ filtroMecanismo }}</strong></span>
        </div>
      </section>

      <!-- ============ PANEL SUPER ADMIN (Calificación Masiva + Depuración) ============ -->
      <section v-if="canUseMassQualification" class="calificacion-masiva-section">
        <!-- Botones de acciones de Super Admin -->
        <div class="super-admin-actions">
          <!-- Botón Calificación Masiva -->
          <button
            @click="toggleModoCalificacionMasiva"
            :class="['btn-toggle-masivo', { activo: modoCalificacionMasiva }]"
            :disabled="aplicandoCalificacion || verificandoInexistentes"
          >
            <i class="material-icons">{{ modoCalificacionMasiva ? 'close' : 'playlist_add_check' }}</i>
            {{ modoCalificacionMasiva ? 'Desactivar Modo Masivo' : 'Calificación Masiva' }}
          </button>

          <!-- Botón Depuración de Archivos y Directorios Inexistentes -->
          <button
            @click="verificarInexistentes"
            class="btn-depuracion"
            :disabled="verificandoInexistentes || aplicandoCalificacion || modoCalificacionMasiva"
            title="Verificar y eliminar registros de archivos y directorios que ya no existen físicamente"
          >
            <i class="material-icons">{{ verificandoInexistentes ? 'hourglass_empty' : 'cleaning_services' }}</i>
            {{ verificandoInexistentes ? 'Verificando...' : 'Depurar Inexistentes' }}
          </button>
        </div>

        <!-- Panel de control cuando está activo -->
        <div v-if="modoCalificacionMasiva" class="panel-calificacion-masiva">
          <div class="panel-header">
            <i class="material-icons">admin_panel_settings</i>
            <h3>Modo Calificación Masiva</h3>
          </div>

          <div class="panel-body">
            <!-- Filtro de archivos a afectar -->
            <div class="filtro-masivo-group">
              <label>Afectar archivos:</label>
              <div class="radio-options">
                <label class="radio-option">
                  <input type="radio" v-model="filtroMasivo" value="no_calificados" />
                  <span>Solo NO calificados</span>
                </label>
                <label class="radio-option">
                  <input type="radio" v-model="filtroMasivo" value="excepto_aprobados" />
                  <span>Excepto aprobados</span>
                </label>
                <label class="radio-option">
                  <input type="radio" v-model="filtroMasivo" value="todos" />
                  <span>Todos los archivos</span>
                </label>
              </div>
            </div>

            <!-- Selector de calificación -->
            <div class="calificacion-select-group">
              <label>Calificación a aplicar:</label>
              <select v-model="calificacionMasivaSeleccionada" class="select-calificacion-masiva">
                <option :value="null">-- Seleccionar calificación --</option>
                <option v-for="cal in calificaciones" :key="cal.id" :value="cal.id">
                  {{ cal.concepto }} ({{ cal.valor }})
                </option>
              </select>
            </div>

            <!-- Contador de seleccionados -->
            <div class="contador-seleccionados">
              <i class="material-icons">check_box</i>
              <span><strong>{{ archivosSeleccionadosCount }}</strong> archivos seleccionados</span>
              <span class="de-total">de {{ archivosParaCalificar.length }} totales</span>
            </div>

            <!-- Info de archivos que serán afectados -->
            <div class="info-filtro-masivo">
              <i class="material-icons">filter_list</i>
              <span>
                Con el filtro actual, <strong>{{ archivosFiltradosPorMasivo.length }}</strong> archivos serán afectados
              </span>
            </div>

            <!-- Botones de selección rápida -->
            <div class="botones-seleccion">
              <button @click="seleccionarTodos" class="btn-seleccion" :disabled="todosSeleccionados">
                <i class="material-icons">select_all</i>
                Seleccionar Todos
              </button>
              <button @click="deseleccionarTodos" class="btn-seleccion" :disabled="archivosSeleccionadosCount === 0">
                <i class="material-icons">deselect</i>
                Deseleccionar Todos
              </button>
            </div>

            <!-- Botones de acción -->
            <div class="botones-accion-masiva">
              <button
                @click="mostrarConfirmacionMasiva"
                class="btn-aplicar-masivo"
                :disabled="aplicandoCalificacion || archivosSeleccionadosCount === 0 || !calificacionMasivaSeleccionada"
              >
                <i class="material-icons">{{ aplicandoCalificacion ? 'hourglass_empty' : 'check_circle' }}</i>
                {{ aplicandoCalificacion ? 'Aplicando...' : 'Aplicar Calificación' }}
              </button>

              <button
                v-if="ultimoLoteMasivo?.tiene_lote"
                @click="restaurarCalificacionAnterior"
                class="btn-restaurar"
                :disabled="aplicandoCalificacion"
                :title="`Restaurar lote ${ultimoLoteMasivo.lote_id} (${ultimoLoteMasivo.archivos_en_lote} archivos)`"
              >
                <i class="material-icons">undo</i>
                Restaurar Anterior
              </button>
            </div>

            <!-- Info del último lote -->
            <div v-if="ultimoLoteMasivo?.tiene_lote" class="info-ultimo-lote">
              <i class="material-icons">info</i>
              <span>
                Último lote: <strong>{{ ultimoLoteMasivo.lote_id }}</strong>
                ({{ ultimoLoteMasivo.archivos_en_lote }} archivos)
                por {{ ultimoLoteMasivo.usuario }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Modal de confirmación masiva -->
      <div v-if="showConfirmacionMasiva" class="modal-overlay" @click.self="showConfirmacionMasiva = false">
        <div class="modal-content confirmacion-masiva-modal">
          <div class="modal-header warning">
            <i class="material-icons">warning</i>
            <h2>Confirmar Calificación Masiva</h2>
            <button @click="showConfirmacionMasiva = false" class="btn-close-modal">
              <i class="material-icons">close</i>
            </button>
          </div>
          <div class="modal-body">
            <p class="confirmacion-mensaje">
              ¿Está seguro de aplicar la calificación a <strong>{{ archivosSeleccionadosCount }}</strong> archivos?
            </p>
            <div class="confirmacion-detalles">
              <p><strong>Calificación:</strong>
                {{ calificaciones.find(c => c.id === calificacionMasivaSeleccionada)?.concepto || 'No seleccionada' }}
              </p>
              <p><strong>Filtro:</strong>
                {{ filtroMasivo === 'todos' ? 'Todos los archivos' :
                   filtroMasivo === 'no_calificados' ? 'Solo NO calificados' :
                   'Excepto aprobados' }}
              </p>
            </div>
            <p class="confirmacion-advertencia">
              <i class="material-icons">info</i>
              Esta acción guardará las calificaciones anteriores para poder restaurarlas.
            </p>
          </div>
          <div class="modal-footer">
            <button @click="showConfirmacionMasiva = false" class="btn-cancelar">
              Cancelar
            </button>
            <button @click="aplicarCalificacionMasiva" class="btn-confirmar" :disabled="aplicandoCalificacion">
              <i class="material-icons">{{ aplicandoCalificacion ? 'hourglass_empty' : 'check' }}</i>
              {{ aplicandoCalificacion ? 'Aplicando...' : 'Confirmar y Aplicar' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Modal UNIFICADO de Depuración de Archivos y Directorios Inexistentes -->
      <div v-if="showModalDepuracion" class="modal-overlay" @click.self="cerrarModalDepuracion">
        <div class="modal-content depuracion-modal depuracion-unificada">
          <div class="modal-header" :class="hayInexistentes ? 'warning' : 'success'">
            <i class="material-icons">{{ hayInexistentes ? 'warning' : 'check_circle' }}</i>
            <h2>Verificación de Elementos Inexistentes</h2>
            <button @click="cerrarModalDepuracion" class="btn-close-modal">
              <i class="material-icons">close</i>
            </button>
          </div>
          <div class="modal-body">
            <!-- Resumen general -->
            <div class="verificacion-resumen">
              <div class="resumen-stats resumen-stats-unificado">
                <div class="resumen-stat directorios-stat">
                  <span class="stat-number">{{ resultadoVerificacionDirs?.directorios_inexistentes || 0 }}</span>
                  <span class="stat-label">Directorios Inexistentes</span>
                </div>
                <div class="resumen-stat archivos-stat">
                  <span class="stat-number">{{ resultadoVerificacion?.archivos_inexistentes || 0 }}</span>
                  <span class="stat-label">Archivos Inexistentes</span>
                </div>
                <div class="resumen-stat seleccionados">
                  <span class="stat-number">{{ totalSeleccionadosDepuracion }}</span>
                  <span class="stat-label">Total Seleccionados</span>
                </div>
              </div>

              <!-- Mensaje si todo está bien -->
              <div v-if="!hayInexistentes" class="mensaje-exito">
                <i class="material-icons">check_circle</i>
                <p>¡Todos los directorios y archivos registrados existen físicamente! No hay nada que depurar.</p>
              </div>

              <!-- SECCIÓN: Directorios Inexistentes -->
              <div v-if="resultadoVerificacionDirs?.directorios_inexistentes > 0" class="seccion-depuracion seccion-directorios">
                <div class="lista-header">
                  <h4>
                    <i class="material-icons">folder_off</i>
                    Directorios inexistentes ({{ resultadoVerificacionDirs.lista_inexistentes.length }})
                  </h4>
                  <div class="lista-acciones">
                    <button @click="seleccionarTodosDepuracionDirs" class="btn-seleccion-depuracion">
                      <i class="material-icons">select_all</i>
                      Todos
                    </button>
                    <button @click="deseleccionarTodosDepuracionDirs" class="btn-seleccion-depuracion">
                      <i class="material-icons">deselect</i>
                      Ninguno
                    </button>
                  </div>
                </div>
                <div class="lista-inexistentes lista-dirs-inexistentes">
                  <div
                    v-for="directorio in resultadoVerificacionDirs.lista_inexistentes"
                    :key="'dir-' + directorio.id"
                    :class="['directorio-inexistente', { seleccionado: directoriosADepurarSeleccionados.has(directorio.id) }]"
                    @click="toggleDirectorioDepuracion(directorio.id)"
                  >
                    <div class="archivo-checkbox">
                      <input
                        type="checkbox"
                        :checked="directoriosADepurarSeleccionados.has(directorio.id)"
                        @click.stop="toggleDirectorioDepuracion(directorio.id)"
                      />
                    </div>
                    <div class="directorio-info-depuracion">
                      <span class="directorio-nombre-depuracion">
                        <i class="material-icons">folder</i>
                        {{ directorio.nombre }}
                      </span>
                      <span class="directorio-ruta-depuracion" :title="directorio.ruta_windows">
                        {{ directorio.ruta_windows }}
                      </span>
                      <div class="directorio-meta-depuracion">
                        <span class="meta-item" :class="{ 'meta-warning': directorio.total_archivos > 0 }">
                          <i class="material-icons">description</i>
                          {{ directorio.total_archivos }} archivos
                        </span>
                        <span class="meta-item" :class="directorio.evaluado ? 'meta-ok' : ''">
                          <i class="material-icons">{{ directorio.evaluado ? 'check_circle' : 'pending' }}</i>
                          {{ directorio.evaluado ? 'Evaluado' : 'Pendiente' }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                <!-- Advertencia de archivos en cascada -->
                <div v-if="totalArchivosEnDirSeleccionados > 0" class="advertencia-cascada">
                  <i class="material-icons">warning_amber</i>
                  <p>
                    Los directorios seleccionados contienen <strong>{{ totalArchivosEnDirSeleccionados }}</strong> archivos que también serán eliminados.
                  </p>
                </div>
              </div>

              <!-- SECCIÓN: Archivos Inexistentes -->
              <div v-if="resultadoVerificacion?.archivos_inexistentes > 0" class="seccion-depuracion seccion-archivos">
                <div class="lista-header">
                  <h4>
                    <i class="material-icons">description</i>
                    Archivos inexistentes ({{ resultadoVerificacion.lista_inexistentes.length }})
                  </h4>
                  <div class="lista-acciones">
                    <button @click="seleccionarTodosDepuracion" class="btn-seleccion-depuracion">
                      <i class="material-icons">select_all</i>
                      Todos
                    </button>
                    <button @click="deseleccionarTodosDepuracion" class="btn-seleccion-depuracion">
                      <i class="material-icons">deselect</i>
                      Ninguno
                    </button>
                  </div>
                </div>
                <div class="lista-inexistentes">
                  <div
                    v-for="archivo in resultadoVerificacion.lista_inexistentes"
                    :key="'arch-' + archivo.id"
                    :class="['archivo-inexistente', { seleccionado: archivosADepurarSeleccionados.has(archivo.id) }]"
                    @click="toggleArchivoDepuracion(archivo.id)"
                  >
                    <div class="archivo-checkbox">
                      <input
                        type="checkbox"
                        :checked="archivosADepurarSeleccionados.has(archivo.id)"
                        @click.stop="toggleArchivoDepuracion(archivo.id)"
                      />
                    </div>
                    <div class="archivo-info-depuracion">
                      <span class="archivo-nombre-depuracion">{{ archivo.nombre }}</span>
                      <span class="archivo-ruta-depuracion" :title="archivo.ruta_windows">
                        <i class="material-icons ruta-icon">folder</i>
                        {{ archivo.ruta_windows }}
                      </span>
                    </div>
                    <span class="archivo-fecha-depuracion">
                      {{ archivo.fecha_creacion ? new Date(archivo.fecha_creacion).toLocaleDateString('es-CO') : 'Sin fecha' }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Advertencia final -->
              <div v-if="totalSeleccionadosDepuracion > 0" class="advertencia-final">
                <i class="material-icons">error_outline</i>
                <p>
                  <strong>¡Atención!</strong> Se eliminarán
                  <span v-if="directoriosADepurarSeleccionados.size > 0"><strong>{{ directoriosADepurarSeleccionados.size }}</strong> directorios</span>
                  <span v-if="directoriosADepurarSeleccionados.size > 0 && archivosADepurarSeleccionados.size > 0"> y </span>
                  <span v-if="archivosADepurarSeleccionados.size > 0"><strong>{{ archivosADepurarSeleccionados.size }}</strong> archivos</span>
                  <span v-if="totalArchivosEnDirSeleccionados > 0"> (+ {{ totalArchivosEnDirSeleccionados }} archivos en cascada)</span>.
                  Esta acción NO se puede deshacer.
                </p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="cerrarModalDepuracion" class="btn-cancelar">
              {{ hayInexistentes ? 'Cancelar' : 'Cerrar' }}
            </button>
            <button
              v-if="totalSeleccionadosDepuracion > 0"
              @click="mostrarConfirmacionDepuracion"
              class="btn-depurar-confirmar"
              :disabled="depurandoInexistentes"
            >
              <i class="material-icons">delete_sweep</i>
              Eliminar {{ totalSeleccionadosDepuracion }} Elementos
            </button>
          </div>
        </div>
      </div>

      <!-- Modal de Confirmación de Depuración UNIFICADO -->
      <div v-if="showConfirmacionDepuracion" class="modal-overlay" @click.self="showConfirmacionDepuracion = false">
        <div class="modal-content confirmacion-depuracion-modal">
          <div class="modal-header danger">
            <i class="material-icons">warning</i>
            <h2>Confirmar Eliminación</h2>
            <button @click="showConfirmacionDepuracion = false" class="btn-close-modal">
              <i class="material-icons">close</i>
            </button>
          </div>
          <div class="modal-body">
            <div class="confirmacion-icono">
              <i class="material-icons">delete_forever</i>
            </div>
            <p class="confirmacion-titulo">¿Está seguro de eliminar estos registros?</p>
            <p class="confirmacion-detalle">
              Se eliminarán permanentemente:
              <br v-if="directoriosADepurarSeleccionados.size > 0" />
              <span v-if="directoriosADepurarSeleccionados.size > 0">• <strong>{{ directoriosADepurarSeleccionados.size }}</strong> directorios</span>
              <span v-if="totalArchivosEnDirSeleccionados > 0"> (con {{ totalArchivosEnDirSeleccionados }} archivos en cascada)</span>
              <br v-if="archivosADepurarSeleccionados.size > 0" />
              <span v-if="archivosADepurarSeleccionados.size > 0">• <strong>{{ archivosADepurarSeleccionados.size }}</strong> archivos individuales</span>
            </p>
            <div class="confirmacion-warning">
              <i class="material-icons">info</i>
              <span>Esta acción <strong>NO</strong> se puede deshacer. Los elementos físicos (si existieran en otra ubicación) no serán afectados.</span>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="showConfirmacionDepuracion = false" class="btn-cancelar">
              <i class="material-icons">close</i>
              No, Cancelar
            </button>
            <button
              @click="ejecutarDepuracionUnificada"
              class="btn-eliminar-definitivo"
              :disabled="depurandoInexistentes"
            >
              <i class="material-icons">{{ depurandoInexistentes ? 'hourglass_empty' : 'delete_forever' }}</i>
              {{ depurandoInexistentes ? 'Eliminando...' : 'Sí, Eliminar' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Estadísticas -->
      <section class="stats-section">
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="material-icons">folder</i>
            </div>
            <div class="stat-content">
              <span class="stat-number">{{ estadisticasFiltradas.total_directorios }}</span>
              <span class="stat-label">Directorios</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              <i class="material-icons">description</i>
            </div>
            <div class="stat-content">
              <span class="stat-number">{{ estadisticasFiltradas.total_archivos }}</span>
              <span class="stat-label">Archivos</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon pending">
              <i class="material-icons">pending</i>
            </div>
            <div class="stat-content">
              <span class="stat-number">{{ estadisticasFiltradas.pendientes }}</span>
              <span class="stat-label">Pendientes</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon approved">
              <i class="material-icons">check_circle</i>
            </div>
            <div class="stat-content">
              <span class="stat-number">{{ estadisticasFiltradas.aprobados }}</span>
              <span class="stat-label">Aprobados</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Estructura de Directorios -->
      <section class="directorios-section">
        <div class="section-header">
          <h2>🌳 Estructura de Directorios</h2>
          <span class="count-badge">{{ directoriosFiltrados.length }} directorios principales</span>
        </div>
        
        <div class="tree-container">
          <!-- Directorio Padre (NIVEL 0) -->
          <div 
            v-for="directorio in directoriosFiltrados" 
            :key="`dir-${directorio.id_disposicion}`"
            class="tree-root"
          >
            <!-- Header del Directorio Padre -->
            <div
              :class="['directorio-header', 'nivel-0', { 'drop-target': isDropTarget(directorio.id_disposicion) }]"
              @click="toggleDirectorio(directorio.id_disposicion)"
              @dragenter="handleDirectorioDragEnter($event, directorio)"
              @dragover="handleDirectorioDragOver($event, directorio)"
              @dragleave="handleDirectorioDragLeave($event, directorio)"
              @drop="handleDirectorioDrop($event, directorio)"
            >
              <div class="directorio-content">
                <!-- Checkbox para selección masiva -->
                <div v-if="modoCalificacionMasiva" class="checkbox-masivo" @click.stop>
                  <input
                    type="checkbox"
                    :checked="isDirectorioSeleccionado(directorio)"
                    :indeterminate="isDirectorioParcialmenteSeleccionado(directorio)"
                    @change="toggleDirectorioSeleccion(directorio, ($event.target as HTMLInputElement).checked)"
                    class="checkbox-directorio"
                  />
                </div>
                <div class="toggle-icon">
                  <i class="material-icons">
                    {{ directoriosExpandidos[directorio.id_disposicion] ? 'expand_more' : 'chevron_right' }}
                  </i>
                </div>
                <div class="folder-icon nivel-0">
                  <i class="material-icons">
                    {{ directoriosExpandidos[directorio.id_disposicion] ? 'folder_open' : 'folder' }}
                  </i>
                </div>
                <div class="directorio-info">
                  <h3>📁 {{ directorio.nombre_directorio }}
                    <span v-if="mecanismosDisponibles.length > 1" class="badge-mecanismo">{{ directorio.mecanismo }}</span>
                  </h3>
                  <p class="directorio-stats">
                    {{ directorio.total_archivos }} archivos • {{ directorio.subdirectorios_count }} subdirectorios
                  </p>
                  <span class="directorio-path">{{ linuxToWindowsPath(directorio.jerarquia_completa) }}</span>
                </div>
              </div>
              <div class="directorio-actions">
                <div class="estado-badges">
                  <span v-if="directorio.pendientes > 0" class="badge warning">
                    {{ directorio.pendientes }}P
                  </span>
                  <span v-if="directorio.evaluados > 0" class="badge info">
                    {{ directorio.evaluados }}E
                  </span>
                  <span v-if="directorio.aprobados > 0" class="badge success">
                    {{ directorio.aprobados }}A
                  </span>
                </div>
                <!-- Botón Subir Archivos a ESTE directorio -->
                <button
                  v-if="canUpload"
                  @click.stop="openUploadModal(directorio)"
                  class="btn-subir-directorio"
                  :title="'Subir archivos a: ' + directorio.nombre_directorio"
                >
                  <i class="material-icons">cloud_upload</i>
                </button>
                <button
                  v-if="canDelete"
                  @click.stop="eliminarDirectorio(directorio)"
                  class="btn-eliminar-directorio"
                  title="Eliminar directorio (Administradores)"
                >
                  <i class="material-icons">delete</i>
                </button>
                <button
                  v-else-if="userPermissions.isProfesional"
                  disabled
                  title="Solo los Administradores pueden eliminar directorios"
                  class="btn-eliminar-directorio disabled"
                >
                  <i class="material-icons">delete</i>
                </button>
              </div>
            </div>

            <!-- Contenido Expandible NIVEL 0 -->
            <div v-if="directoriosExpandidos[directorio.id_disposicion]" class="directorio-children">
              
              <!-- Subdirectorios NIVEL 1 -->
              <div 
                v-for="subdirectorio in directorio.subdirectorios" 
                :key="`sub-${subdirectorio.id_disposicion}`"
                class="subdirectorio nivel-1"
              >
                <!-- Header del Subdirectorio NIVEL 1 -->
                <div
                  :class="['subdirectorio-header', 'nivel-1', { 'drop-target': isDropTarget(subdirectorio.id_disposicion) }]"
                  @click="toggleDirectorio(subdirectorio.id_disposicion)"
                  @dragenter="handleDirectorioDragEnter($event, subdirectorio)"
                  @dragover="handleDirectorioDragOver($event, subdirectorio)"
                  @dragleave="handleDirectorioDragLeave($event, subdirectorio)"
                  @drop="handleDirectorioDrop($event, subdirectorio)"
                >
                  <div class="subdirectorio-content">
                    <!-- Checkbox para selección masiva -->
                    <div v-if="modoCalificacionMasiva" class="checkbox-masivo" @click.stop>
                      <input
                        type="checkbox"
                        :checked="isDirectorioSeleccionado(subdirectorio)"
                        :indeterminate="isDirectorioParcialmenteSeleccionado(subdirectorio)"
                        @change="toggleDirectorioSeleccion(subdirectorio, ($event.target as HTMLInputElement).checked)"
                        class="checkbox-directorio"
                      />
                    </div>
                    <div class="toggle-icon">
                      <i class="material-icons">
                        {{ directoriosExpandidos[subdirectorio.id_disposicion] ? 'expand_more' : 'chevron_right' }}
                      </i>
                    </div>
                    <div class="folder-icon nivel-1">
                      <i class="material-icons">
                        {{ directoriosExpandidos[subdirectorio.id_disposicion] ? 'folder_open' : 'folder' }}
                      </i>
                    </div>
                    <div class="subdirectorio-info">
                      <h4>📂 {{ subdirectorio.nombre_directorio }}</h4>
                      <p class="subdirectorio-stats">
                        {{ subdirectorio.total_archivos }} archivos • {{ subdirectorio.subdirectorios_count }} subdirs
                      </p>
                      <span class="subdirectorio-path">{{ linuxToWindowsPath(subdirectorio.jerarquia_completa) }}</span>
                    </div>
                  </div>
                  <div class="subdirectorio-actions">
                    <div class="estado-badges">
                      <span v-if="subdirectorio.pendientes > 0" class="badge warning mini">{{ subdirectorio.pendientes }}P</span>
                      <span v-if="subdirectorio.evaluados > 0" class="badge info mini">{{ subdirectorio.evaluados }}E</span>
                      <span v-if="subdirectorio.aprobados > 0" class="badge success mini">{{ subdirectorio.aprobados }}A</span>
                    </div>
                    <button
                      v-if="canUpload"
                      @click.stop="openUploadModal(subdirectorio)"
                      class="btn-subir-subdirectorio"
                      :title="'Subir archivos a: ' + subdirectorio.nombre_directorio"
                    >
                      <i class="material-icons">cloud_upload</i>
                    </button>
                    <button
                      v-if="canDelete"
                      @click.stop="eliminarDirectorio(subdirectorio)"
                      class="btn-eliminar-subdirectorio"
                      title="Eliminar subdirectorio (Administradores)"
                    >
                      <i class="material-icons">delete</i>
                    </button>
                  </div>
                </div>

                <!-- Contenido del Subdirectorio NIVEL 1 -->
                <div v-if="directoriosExpandidos[subdirectorio.id_disposicion]" class="subdirectorio-children nivel-1">
                  
                  <!-- Subdirectorios NIVEL 2 (Tercer Nivel Total) -->
                  <div 
                    v-for="subsubdirectorio in subdirectorio.subdirectorios" 
                    :key="`subsub-${subsubdirectorio.id_disposicion}`"
                    class="subdirectorio nivel-2"
                    v-show="subdirectorio.subdirectorios && subdirectorio.subdirectorios.length > 0"
                  >
                    <!-- Header del Sub-subdirectorio NIVEL 2 -->
                    <div
                      :class="['subdirectorio-header', 'nivel-2', { 'drop-target': isDropTarget(subsubdirectorio.id_disposicion) }]"
                      @click="toggleDirectorio(subsubdirectorio.id_disposicion)"
                      @dragenter="handleDirectorioDragEnter($event, subsubdirectorio)"
                      @dragover="handleDirectorioDragOver($event, subsubdirectorio)"
                      @dragleave="handleDirectorioDragLeave($event, subsubdirectorio)"
                      @drop="handleDirectorioDrop($event, subsubdirectorio)"
                    >
                      <div class="subdirectorio-content">
                        <!-- Checkbox para selección masiva -->
                        <div v-if="modoCalificacionMasiva" class="checkbox-masivo" @click.stop>
                          <input
                            type="checkbox"
                            :checked="isDirectorioSeleccionado(subsubdirectorio)"
                            :indeterminate="isDirectorioParcialmenteSeleccionado(subsubdirectorio)"
                            @change="toggleDirectorioSeleccion(subsubdirectorio, ($event.target as HTMLInputElement).checked)"
                            class="checkbox-directorio"
                          />
                        </div>
                        <div class="toggle-icon">
                          <i class="material-icons">
                            {{ directoriosExpandidos[subsubdirectorio.id_disposicion] ? 'expand_more' : 'chevron_right' }}
                          </i>
                        </div>
                        <div class="folder-icon nivel-2">
                          <i class="material-icons">
                            {{ directoriosExpandidos[subsubdirectorio.id_disposicion] ? 'folder_open' : 'folder' }}
                          </i>
                        </div>
                        <div class="subdirectorio-info">
                          <h5>📁 {{ subsubdirectorio.nombre_directorio }}</h5>
                          <p class="subdirectorio-stats nivel-2">
                            {{ subsubdirectorio.total_archivos }} archivos • {{ subsubdirectorio.subdirectorios_count }} subdirs
                          </p>
                          <span class="subdirectorio-path nivel-2">{{ linuxToWindowsPath(subsubdirectorio.jerarquia_completa) }}</span>
                        </div>
                      </div>
                      <div class="subdirectorio-actions">
                        <div class="estado-badges">
                          <span v-if="subsubdirectorio.pendientes > 0" class="badge warning mini">{{ subsubdirectorio.pendientes }}P</span>
                          <span v-if="subsubdirectorio.evaluados > 0" class="badge info mini">{{ subsubdirectorio.evaluados }}E</span>
                          <span v-if="subsubdirectorio.aprobados > 0" class="badge success mini">{{ subsubdirectorio.aprobados }}A</span>
                        </div>
                        <button
                          v-if="canUpload"
                          @click.stop="openUploadModal(subsubdirectorio)"
                          class="btn-subir-subdirectorio nivel-2"
                          :title="'Subir archivos a: ' + subsubdirectorio.nombre_directorio"
                        >
                          <i class="material-icons">cloud_upload</i>
                        </button>
                        <button
                          v-if="canDelete"
                          @click.stop="eliminarDirectorio(subsubdirectorio)"
                          class="btn-eliminar-subdirectorio nivel-2"
                          title="Eliminar subdirectorio (Administradores)"
                        >
                          <i class="material-icons">delete</i>
                        </button>
                      </div>
                    </div>

                    <!-- Contenido del Sub-subdirectorio NIVEL 2 -->
                    <div v-if="directoriosExpandidos[subsubdirectorio.id_disposicion]" class="subdirectorio-children nivel-2">
                      
                      <!-- ========== SUBDIRECTORIOS NIVEL 3 (CUARTO NIVEL VISUAL - AZUL AGUAMARINA) ========== -->
                      <div 
                        v-for="subsubsubdirectorio in subsubdirectorio.subdirectorios" 
                        :key="`subsubsub-${subsubsubdirectorio.id_disposicion}`"
                        class="subdirectorio nivel-3"
                        v-show="subsubdirectorio.subdirectorios && subsubdirectorio.subdirectorios.length > 0"
                      >
                        <!-- Header del Sub-sub-subdirectorio NIVEL 3 (4to nivel visual - AZUL AGUAMARINA) -->
                        <div
                          :class="['subdirectorio-header', 'nivel-3', { 'drop-target': isDropTarget(subsubsubdirectorio.id_disposicion) }]"
                          @click="toggleDirectorio(subsubsubdirectorio.id_disposicion)"
                          @dragenter="handleDirectorioDragEnter($event, subsubsubdirectorio)"
                          @dragover="handleDirectorioDragOver($event, subsubsubdirectorio)"
                          @dragleave="handleDirectorioDragLeave($event, subsubsubdirectorio)"
                          @drop="handleDirectorioDrop($event, subsubsubdirectorio)"
                        >
                          <div class="subdirectorio-content">
                            <!-- Checkbox para selección masiva -->
                            <div v-if="modoCalificacionMasiva" class="checkbox-masivo" @click.stop>
                              <input
                                type="checkbox"
                                :checked="isDirectorioSeleccionado(subsubsubdirectorio)"
                                :indeterminate="isDirectorioParcialmenteSeleccionado(subsubsubdirectorio)"
                                @change="toggleDirectorioSeleccion(subsubsubdirectorio, ($event.target as HTMLInputElement).checked)"
                                class="checkbox-directorio"
                              />
                            </div>
                            <div class="toggle-icon">
                              <i class="material-icons">
                                {{ directoriosExpandidos[subsubsubdirectorio.id_disposicion] ? 'expand_more' : 'chevron_right' }}
                              </i>
                            </div>
                            <div class="folder-icon nivel-3">
                              <i class="material-icons">
                                {{ directoriosExpandidos[subsubsubdirectorio.id_disposicion] ? 'folder_open' : 'folder' }}
                              </i>
                            </div>
                            <div class="subdirectorio-info">
                              <h6>📷 {{ subsubsubdirectorio.nombre_directorio }}</h6>
                              <p class="subdirectorio-stats nivel-3">
                                {{ subsubsubdirectorio.total_archivos }} archivos (nivel 4+)
                              </p>
                              <span class="subdirectorio-path nivel-3">{{ linuxToWindowsPath(subsubsubdirectorio.jerarquia_completa) }}</span>
                            </div>
                          </div>
                          <div class="subdirectorio-actions">
                            <div class="estado-badges">
                              <span v-if="subsubsubdirectorio.pendientes > 0" class="badge warning nano">{{ subsubsubdirectorio.pendientes }}P</span>
                              <span v-if="subsubsubdirectorio.evaluados > 0" class="badge info nano">{{ subsubsubdirectorio.evaluados }}E</span>
                              <span v-if="subsubsubdirectorio.aprobados > 0" class="badge success nano">{{ subsubsubdirectorio.aprobados }}A</span>
                            </div>
                            <button
                              v-if="canUpload"
                              @click.stop="openUploadModal(subsubsubdirectorio)"
                              class="btn-subir-subdirectorio nivel-3"
                              :title="'Subir archivos a: ' + subsubsubdirectorio.nombre_directorio"
                            >
                              <i class="material-icons">cloud_upload</i>
                            </button>
                            <button
                              v-if="canDelete"
                              @click.stop="eliminarDirectorio(subsubsubdirectorio)"
                              class="btn-eliminar-subdirectorio nivel-3"
                              title="Eliminar subdirectorio nivel 4 (Solo Administradores)"
                            >
                              <i class="material-icons">delete</i>
                            </button>
                          </div>
                        </div>

                        <!-- Contenido del Sub-sub-subdirectorio NIVEL 3 -->
                        <div v-if="directoriosExpandidos[subsubsubdirectorio.id_disposicion]" class="subdirectorio-children nivel-3">

                          <!-- ========== SUBDIRECTORIOS NIVEL 4 (QUINTO NIVEL VISUAL - CORAL/SALMON) ========== -->
                          <div
                            v-for="subsubsubsubdirectorio in subsubsubdirectorio.subdirectorios"
                            :key="`subsubsubsub-${subsubsubsubdirectorio.id_disposicion}`"
                            class="subdirectorio nivel-4"
                            v-show="subsubsubdirectorio.subdirectorios && subsubsubdirectorio.subdirectorios.length > 0"
                          >
                            <!-- Header del Sub-sub-sub-subdirectorio NIVEL 4 (5to nivel visual - CORAL) -->
                            <div
                              :class="['subdirectorio-header', 'nivel-4', { 'drop-target': isDropTarget(subsubsubsubdirectorio.id_disposicion) }]"
                              @click="toggleDirectorio(subsubsubsubdirectorio.id_disposicion)"
                              @dragenter="handleDirectorioDragEnter($event, subsubsubsubdirectorio)"
                              @dragover="handleDirectorioDragOver($event, subsubsubsubdirectorio)"
                              @dragleave="handleDirectorioDragLeave($event, subsubsubsubdirectorio)"
                              @drop="handleDirectorioDrop($event, subsubsubsubdirectorio)"
                            >
                              <div class="subdirectorio-content">
                                <!-- Checkbox para selección masiva -->
                                <div v-if="modoCalificacionMasiva" class="checkbox-masivo" @click.stop>
                                  <input
                                    type="checkbox"
                                    :checked="isDirectorioSeleccionado(subsubsubsubdirectorio)"
                                    :indeterminate="isDirectorioParcialmenteSeleccionado(subsubsubsubdirectorio)"
                                    @change="toggleDirectorioSeleccion(subsubsubsubdirectorio, ($event.target as HTMLInputElement).checked)"
                                    class="checkbox-directorio"
                                  />
                                </div>
                                <div class="toggle-icon">
                                  <i class="material-icons">
                                    {{ directoriosExpandidos[subsubsubsubdirectorio.id_disposicion] ? 'expand_more' : 'chevron_right' }}
                                  </i>
                                </div>
                                <div class="folder-icon nivel-4">
                                  <i class="material-icons">
                                    {{ directoriosExpandidos[subsubsubsubdirectorio.id_disposicion] ? 'folder_open' : 'folder' }}
                                  </i>
                                </div>
                                <div class="subdirectorio-info">
                                  <h6>🔸 {{ subsubsubsubdirectorio.nombre_directorio }}</h6>
                                  <p class="subdirectorio-stats nivel-4">
                                    {{ subsubsubsubdirectorio.total_archivos }} archivos (nivel 5+)
                                  </p>
                                  <span class="subdirectorio-path nivel-4">{{ linuxToWindowsPath(subsubsubsubdirectorio.jerarquia_completa) }}</span>
                                </div>
                              </div>
                              <div class="subdirectorio-actions">
                                <div class="estado-badges">
                                  <span v-if="subsubsubsubdirectorio.pendientes > 0" class="badge warning pico">{{ subsubsubsubdirectorio.pendientes }}P</span>
                                  <span v-if="subsubsubsubdirectorio.evaluados > 0" class="badge info pico">{{ subsubsubsubdirectorio.evaluados }}E</span>
                                  <span v-if="subsubsubsubdirectorio.aprobados > 0" class="badge success pico">{{ subsubsubsubdirectorio.aprobados }}A</span>
                                </div>
                                <button
                                  v-if="canUpload"
                                  @click.stop="openUploadModal(subsubsubsubdirectorio)"
                                  class="btn-subir-subdirectorio nivel-4"
                                  :title="'Subir archivos a: ' + subsubsubsubdirectorio.nombre_directorio"
                                >
                                  <i class="material-icons">cloud_upload</i>
                                </button>
                                <button
                                  v-if="canDelete"
                                  @click.stop="eliminarDirectorio(subsubsubsubdirectorio)"
                                  class="btn-eliminar-subdirectorio nivel-4"
                                  title="Eliminar subdirectorio nivel 5 (Solo Administradores)"
                                >
                                  <i class="material-icons">delete</i>
                                </button>
                              </div>
                            </div>

                            <!-- Contenido del Sub-sub-sub-subdirectorio NIVEL 4 (5to nivel - CORAL) -->
                            <div v-if="directoriosExpandidos[subsubsubsubdirectorio.id_disposicion]" class="subdirectorio-children nivel-4">

                              <!-- ========== SUBDIRECTORIOS NIVEL 5 (SEXTO NIVEL VISUAL - ROSA/FUCSIA) ========== -->
                              <div
                                v-for="nivel5dir in subsubsubsubdirectorio.subdirectorios"
                                :key="`nivel5-${nivel5dir.id_disposicion}`"
                                class="subdirectorio nivel-5"
                                v-show="subsubsubsubdirectorio.subdirectorios && subsubsubsubdirectorio.subdirectorios.length > 0"
                              >
                                <!-- Header del subdirectorio NIVEL 5 (6to nivel visual - ROSA) -->
                                <div
                                  :class="['subdirectorio-header', 'nivel-5', { 'drop-target': isDropTarget(nivel5dir.id_disposicion) }]"
                                  @click="toggleDirectorio(nivel5dir.id_disposicion)"
                                  @dragenter="handleDirectorioDragEnter($event, nivel5dir)"
                                  @dragover="handleDirectorioDragOver($event, nivel5dir)"
                                  @dragleave="handleDirectorioDragLeave($event, nivel5dir)"
                                  @drop="handleDirectorioDrop($event, nivel5dir)"
                                >
                                  <div class="subdirectorio-content">
                                    <!-- Checkbox para selección masiva -->
                                    <div v-if="modoCalificacionMasiva" class="checkbox-masivo" @click.stop>
                                      <input
                                        type="checkbox"
                                        :checked="isDirectorioSeleccionado(nivel5dir)"
                                        :indeterminate="isDirectorioParcialmenteSeleccionado(nivel5dir)"
                                        @change="toggleDirectorioSeleccion(nivel5dir, ($event.target as HTMLInputElement).checked)"
                                        class="checkbox-directorio"
                                      />
                                    </div>
                                    <div class="toggle-icon">
                                      <i class="material-icons">
                                        {{ directoriosExpandidos[nivel5dir.id_disposicion] ? 'expand_more' : 'chevron_right' }}
                                      </i>
                                    </div>
                                    <div class="folder-icon nivel-5">
                                      <i class="material-icons">
                                        {{ directoriosExpandidos[nivel5dir.id_disposicion] ? 'folder_open' : 'folder' }}
                                      </i>
                                    </div>
                                    <div class="subdirectorio-info">
                                      <h6>🔹 {{ nivel5dir.nombre_directorio }}</h6>
                                      <p class="subdirectorio-stats nivel-5">
                                        {{ nivel5dir.total_archivos }} archivos (nivel 6+)
                                      </p>
                                    </div>
                                  </div>
                                  <div class="subdirectorio-actions">
                                    <div class="estado-badges">
                                      <span v-if="nivel5dir.pendientes > 0" class="badge warning micro">{{ nivel5dir.pendientes }}P</span>
                                      <span v-if="nivel5dir.evaluados > 0" class="badge info micro">{{ nivel5dir.evaluados }}E</span>
                                      <span v-if="nivel5dir.aprobados > 0" class="badge success micro">{{ nivel5dir.aprobados }}A</span>
                                    </div>
                                    <button
                                      v-if="canUpload"
                                      @click.stop="openUploadModal(nivel5dir)"
                                      class="btn-subir-subdirectorio nivel-5"
                                      :title="'Subir archivos a: ' + nivel5dir.nombre_directorio"
                                    >
                                      <i class="material-icons">cloud_upload</i>
                                    </button>
                                    <button
                                      v-if="canDelete"
                                      @click.stop="eliminarDirectorio(nivel5dir)"
                                      class="btn-eliminar-subdirectorio nivel-5"
                                      title="Eliminar subdirectorio nivel 6"
                                    >
                                      <i class="material-icons">delete</i>
                                    </button>
                                  </div>
                                </div>

                                <!-- Archivos del subdirectorio NIVEL 5 (6to nivel - ROSA) -->
                                <div v-if="directoriosExpandidos[nivel5dir.id_disposicion]" class="subdirectorio-children nivel-5">
                                  <div v-if="nivel5dir.archivos && nivel5dir.archivos.length > 0" class="archivos-subdirectorio nivel-5">
                                    <div class="archivos-header nivel-5">
                                      <button
                                        @click="toggleArchivos(nivel5dir.id_disposicion)"
                                        class="btn-toggle-archivos nivel-5"
                                      >
                                        <i class="material-icons">
                                          {{ archivosExpandidos[nivel5dir.id_disposicion] ? 'visibility_off' : 'visibility' }}
                                        </i>
                                        <span>{{ archivosExpandidos[nivel5dir.id_disposicion] ? 'Ocultar' : 'Ver' }} {{ filtrarArchivos(nivel5dir.archivos).length }} archivos nivel 6+</span>
                                      </button>
                                    </div>

                                    <div v-if="archivosExpandidos[nivel5dir.id_disposicion]" class="archivos-lista nivel-5">
                                      <div
                                        v-for="archivo in filtrarArchivos(nivel5dir.archivos)"
                                        :key="`archivo-nivel5-${archivo.id_evaluacion}`"
                                        :class="['archivo-item-compacto', 'nivel-5', { 'seleccionado-masivo': modoCalificacionMasiva && isArchivoSeleccionado(archivo.id_evaluacion) }]"
                                      >
                                        <!-- Checkbox para selección masiva -->
                                        <div v-if="modoCalificacionMasiva" class="checkbox-archivo-masivo">
                                          <input
                                            type="checkbox"
                                            :checked="isArchivoSeleccionado(archivo.id_evaluacion)"
                                            @change="toggleArchivoSeleccion(archivo.id_evaluacion)"
                                            class="checkbox-archivo"
                                          />
                                        </div>
                                        <!-- Fila 1: Icono + Nombre + Estado + Acciones -->
                                        <div class="archivo-row-1">
                                          <div class="archivo-icon-mini nivel-5">
                                            <i class="material-icons">{{ getFileIcon(archivo.nombre_archivo) }}</i>
                                          </div>
                                          <div class="archivo-nombre-compacto" :title="archivo.nombre_archivo">
                                            {{ archivo.nombre_archivo }}
                                          </div>
                                          <div :class="['estado-badge-mini', getEstadoClass(archivo.estado_archivo)]">
                                            {{ archivo.estado_archivo }}
                                          </div>
                                          <div class="acciones-compactas">
                                            <button @click="showFileInfo(archivo)" class="btn-mini info" title="Info">
                                              <i class="material-icons">info</i>
                                            </button>
                                            <button v-if="canDownload" @click="viewFile(archivo)" class="btn-mini view" title="Ver">
                                              <i class="material-icons">visibility</i>
                                            </button>
                                            <button v-if="canDownload" @click="downloadFile(archivo)" class="btn-mini download" title="Descargar">
                                              <i class="material-icons">download</i>
                                            </button>
                                            <button v-if="canEdit" @click="editObservaciones(archivo)" class="btn-mini edit" title="Editar">
                                              <i class="material-icons">edit_note</i>
                                            </button>
                                            <button v-if="canDeleteFile(archivo)" @click="deleteFile(archivo)" class="btn-mini delete" title="Eliminar">
                                              <i class="material-icons">delete</i>
                                            </button>
                                          </div>
                                        </div>
                                        <!-- Fila 2: Fecha + Status + Calificación -->
                                        <div class="archivo-row-2">
                                          <span class="fecha-mini">{{ formatDate(archivo.fecha_disposicion) }}</span>
                                          <div class="status-icons">
                                            <span :class="['icon-status', archivo.evaluado ? 'ok' : 'no']" :title="archivo.evaluado ? 'Evaluado' : 'Sin evaluar'">
                                              {{ archivo.evaluado ? '✓E' : '✗E' }}
                                            </span>
                                            <span :class="['icon-status', archivo.aprobado ? 'ok' : 'no']" :title="archivo.aprobado ? 'Aprobado' : 'No aprobado'">
                                              {{ archivo.aprobado ? '✓A' : '✗A' }}
                                            </span>
                                          </div>
                                          <select
                                            v-if="canEdit"
                                            :value="archivo.evaluacion_archivo"
                                            @change="actualizarEvaluacion({ ...archivo, evaluacion_archivo: parseInt($event.target.value) })"
                                            class="select-mini nivel-5"
                                          >
                                            <option v-for="cal in calificaciones" :key="cal.id" :value="cal.id">
                                              {{ cal.concepto }}
                                            </option>
                                          </select>
                                          <span v-else class="cal-mini">{{ getCalificacionText(archivo.evaluacion_archivo) }}</span>
                                          <span v-if="archivo.usuario_evaluacion" class="usuario-calificador-mini">
                                            <i class="material-icons">person</i>
                                            {{ getUsuarioCalificador(archivo.usuario_evaluacion) }}
                                          </span>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                  <div v-else class="empty-level nivel-5">
                                    <i class="material-icons">folder_open</i>
                                    <span>No hay archivos en nivel 6</span>
                                  </div>
                                </div>
                              </div>
                              <!-- ========== FIN NIVEL 5 (SEXTO NIVEL VISUAL) ========== -->

                              <!-- Archivos del subdirectorio NIVEL 4 -->
                              <div v-if="subsubsubsubdirectorio.archivos && subsubsubsubdirectorio.archivos.length > 0" class="archivos-subdirectorio nivel-4">
                                <div class="archivos-header nivel-4">
                                  <button
                                    @click="toggleArchivos(subsubsubsubdirectorio.id_disposicion)"
                                    class="btn-toggle-archivos nivel-4"
                                  >
                                    <i class="material-icons">
                                      {{ archivosExpandidos[subsubsubsubdirectorio.id_disposicion] ? 'visibility_off' : 'visibility' }}
                                    </i>
                                    <span>{{ archivosExpandidos[subsubsubsubdirectorio.id_disposicion] ? 'Ocultar' : 'Ver' }} {{ filtrarArchivos(subsubsubsubdirectorio.archivos).length }} archivos nivel 5</span>
                                  </button>
                                </div>

                                <div v-if="archivosExpandidos[subsubsubsubdirectorio.id_disposicion]" class="archivos-lista nivel-4">
                                  <div
                                    v-for="archivo in filtrarArchivos(subsubsubsubdirectorio.archivos)"
                                    :key="`archivo-nivel4-${archivo.id_evaluacion}`"
                                    :class="['archivo-item-compacto', 'nivel-4', { 'seleccionado-masivo': modoCalificacionMasiva && isArchivoSeleccionado(archivo.id_evaluacion) }]"
                                  >
                                    <!-- Checkbox para selección masiva -->
                                    <div v-if="modoCalificacionMasiva" class="checkbox-archivo-masivo">
                                      <input
                                        type="checkbox"
                                        :checked="isArchivoSeleccionado(archivo.id_evaluacion)"
                                        @change="toggleArchivoSeleccion(archivo.id_evaluacion)"
                                        class="checkbox-archivo"
                                      />
                                    </div>
                                    <!-- Fila 1: Icono + Nombre + Estado + Acciones -->
                                    <div class="archivo-row-1">
                                      <div class="archivo-icon-mini">
                                        <i class="material-icons">{{ getFileIcon(archivo.nombre_archivo) }}</i>
                                      </div>
                                      <div class="archivo-nombre-compacto" :title="archivo.nombre_archivo">
                                        {{ archivo.nombre_archivo }}
                                      </div>
                                      <div :class="['estado-badge-mini', getEstadoClass(archivo.estado_archivo)]">
                                        {{ archivo.estado_archivo }}
                                      </div>
                                      <div class="acciones-compactas">
                                        <button @click="showFileInfo(archivo)" class="btn-mini info" title="Info">
                                          <i class="material-icons">info</i>
                                        </button>
                                        <button v-if="canDownload" @click="viewFile(archivo)" class="btn-mini view" title="Ver">
                                          <i class="material-icons">visibility</i>
                                        </button>
                                        <button v-if="canDownload" @click="downloadFile(archivo)" class="btn-mini download" title="Descargar">
                                          <i class="material-icons">download</i>
                                        </button>
                                        <button v-if="canEdit" @click="editObservaciones(archivo)" class="btn-mini edit" title="Editar">
                                          <i class="material-icons">edit_note</i>
                                        </button>
                                        <button v-if="canDeleteFile(archivo)" @click="deleteFile(archivo)" class="btn-mini delete" title="Eliminar">
                                          <i class="material-icons">delete</i>
                                        </button>
                                      </div>
                                    </div>
                                    <!-- Fila 2: Fecha + Status + Calificación -->
                                    <div class="archivo-row-2">
                                      <span class="fecha-mini">{{ formatDate(archivo.fecha_disposicion) }}</span>
                                      <div class="status-icons">
                                        <span :class="['icon-status', archivo.evaluado ? 'ok' : 'no']" :title="archivo.evaluado ? 'Evaluado' : 'Sin evaluar'">
                                          {{ archivo.evaluado ? '✓E' : '✗E' }}
                                        </span>
                                        <span :class="['icon-status', archivo.aprobado ? 'ok' : 'no']" :title="archivo.aprobado ? 'Aprobado' : 'No aprobado'">
                                          {{ archivo.aprobado ? '✓A' : '✗A' }}
                                        </span>
                                      </div>
                                      <select
                                        v-if="canEdit"
                                        :value="archivo.evaluacion_archivo"
                                        @change="actualizarEvaluacion({ ...archivo, evaluacion_archivo: parseInt($event.target.value) })"
                                        class="select-mini"
                                      >
                                        <option v-for="cal in calificaciones" :key="cal.id" :value="cal.id">
                                          {{ cal.concepto }}
                                        </option>
                                      </select>
                                      <span v-else class="cal-mini">{{ getCalificacionText(archivo.evaluacion_archivo) }}</span>
                                      <span v-if="archivo.usuario_evaluacion" class="usuario-calificador-mini">
                                        <i class="material-icons">person</i>
                                        {{ getUsuarioCalificador(archivo.usuario_evaluacion) }}
                                      </span>
                                    </div>
                                  </div>
                                </div>
                              </div>

                              <div v-else-if="!subsubsubsubdirectorio.subdirectorios || subsubsubsubdirectorio.subdirectorios.length === 0" class="empty-level nivel-4">
                                <i class="material-icons">folder_open</i>
                                <span>No hay archivos en este subdirectorio nivel 5</span>
                              </div>
                            </div>
                          </div>
                          <!-- ========== FIN NIVEL 4 (QUINTO NIVEL VISUAL) ========== -->

                          <!-- Archivos del Sub-sub-subdirectorio NIVEL 3 -->
                          <div v-if="subsubsubdirectorio.archivos && subsubsubdirectorio.archivos.length > 0" class="archivos-subdirectorio nivel-3">
                            <div class="archivos-header nivel-3">
                              <button
                                @click="toggleArchivos(subsubsubdirectorio.id_disposicion)"
                                class="btn-toggle-archivos nivel-3"
                              >
                                <i class="material-icons">
                                  {{ archivosExpandidos[subsubsubdirectorio.id_disposicion] ? 'visibility_off' : 'visibility' }}
                                </i>
                                <span>{{ archivosExpandidos[subsubsubdirectorio.id_disposicion] ? 'Ocultar' : 'Ver' }} {{ filtrarArchivos(subsubsubdirectorio.archivos).length }} archivos nivel 4</span>
                              </button>
                            </div>

                            <div v-if="archivosExpandidos[subsubsubdirectorio.id_disposicion]" class="archivos-lista nivel-3">
                              <div
                                v-for="archivo in filtrarArchivos(subsubsubdirectorio.archivos)"
                                :key="`archivo-nivel3-${archivo.id_evaluacion}`"
                                :class="['archivo-item', 'nivel-3', { 'seleccionado-masivo': modoCalificacionMasiva && isArchivoSeleccionado(archivo.id_evaluacion) }]"
                              >
                                <!-- Checkbox para selección masiva -->
                                <div v-if="modoCalificacionMasiva" class="checkbox-archivo-masivo">
                                  <input
                                    type="checkbox"
                                    :checked="isArchivoSeleccionado(archivo.id_evaluacion)"
                                    @change="toggleArchivoSeleccion(archivo.id_evaluacion)"
                                    class="checkbox-archivo"
                                  />
                                </div>
                                <div class="archivo-info">
                                  <div class="archivo-icon nivel-3">
                                    <i class="material-icons">{{ getFileIcon(archivo.nombre_archivo) }}</i>
                                    <span class="depth-indicator">4</span>
                                  </div>
                                  <div class="archivo-detalles">
                                    <h6 class="archivo-nombre" :title="archivo.nombre_archivo">{{ archivo.nombre_archivo }}</h6>
                                    <p class="archivo-fecha">{{ formatDate(archivo.fecha_disposicion) }}</p>
                                    <p class="archivo-profundidad">Profundidad: 4 niveles</p>
                                  </div>
                                  <div :class="['archivo-estado', getEstadoClass(archivo.estado_archivo)]">
                                    {{ archivo.estado_archivo }}
                                  </div>
                                </div>

                                <div class="archivo-status">
                                  <div :class="['status-indicator', archivo.evaluado ? 'success' : 'pending']">
                                    {{ archivo.evaluado ? '✓ Evaluado' : '✗ Sin evaluar' }}
                                  </div>
                                  <div :class="['status-indicator', archivo.aprobado ? 'success' : 'pending']">
                                    {{ archivo.aprobado ? '✓ Aprobado' : '✗ No aprobado' }}
                                  </div>
                                </div>

                                <div class="archivo-calificacion-wrapper">
                                  <div class="archivo-calificacion">
                                    <select
                                      v-if="canEdit"
                                      :value="archivo.evaluacion_archivo"
                                      @change="actualizarEvaluacion({ ...archivo, evaluacion_archivo: parseInt($event.target.value) })"
                                      class="calificacion-select"
                                    >
                                      <option
                                        v-for="cal in calificaciones"
                                        :key="cal.id"
                                        :value="cal.id"
                                      >
                                        {{ cal.concepto }} ({{ cal.valor }})
                                      </option>
                                    </select>
                                    <span v-else class="calificacion-readonly">
                                      {{ getCalificacionText(archivo.evaluacion_archivo) }}
                                    </span>
                                  </div>
                                  <div v-if="archivo.usuario_evaluacion" class="usuario-calificador">
                                    <i class="material-icons">person</i>
                                    {{ getUsuarioCalificador(archivo.usuario_evaluacion) }}
                                  </div>
                                </div>

                                <div class="archivo-acciones">
                                  <button @click="showFileInfo(archivo)" class="btn-accion info" title="Ver información">
                                    <i class="material-icons">info</i>
                                  </button>
                                  <button
                                    v-if="canDownload"
                                    @click="viewFile(archivo)"
                                    class="btn-accion view"
                                    title="Ver archivo"
                                  >
                                    <i class="material-icons">visibility</i>
                                  </button>
                                  <button
                                    v-if="canDownload"
                                    @click="downloadFile(archivo)"
                                    class="btn-accion download"
                                    title="Descargar archivo"
                                  >
                                    <i class="material-icons">download</i>
                                  </button>
                                  <button
                                    v-if="canEdit"
                                    @click="editObservaciones(archivo)"
                                    class="btn-accion edit"
                                    title="Editar observaciones"
                                  >
                                    <i class="material-icons">edit_note</i>
                                  </button>
                                  <button
                                    v-if="canDeleteFile(archivo)"
                                    @click="deleteFile(archivo)"
                                    class="btn-accion delete"
                                    title="Eliminar archivo (Solo Administradores)"
                                  >
                                    <i class="material-icons">delete</i>
                                  </button>
                                </div>
                              </div>
                            </div>
                          </div>

                          <div v-else-if="!subsubsubdirectorio.subdirectorios || subsubsubdirectorio.subdirectorios.length === 0" class="empty-level nivel-3">
                            <i class="material-icons">folder_open</i>
                            <span>No hay archivos en este subdirectorio nivel 4</span>
                          </div>
                        </div>
                      </div>
                      <!-- ========== FIN NIVEL 3 (CUARTO NIVEL VISUAL) ========== -->

                      <!-- Archivos del Sub-subdirectorio NIVEL 2 -->
                      <div v-if="subsubdirectorio.archivos && subsubdirectorio.archivos.length > 0" class="archivos-subdirectorio nivel-2">
                        <div class="archivos-header nivel-2">
                          <button 
                            @click="toggleArchivos(subsubdirectorio.id_disposicion)"
                            class="btn-toggle-archivos nivel-2"
                          >
                            <i class="material-icons">
                              {{ archivosExpandidos[subsubdirectorio.id_disposicion] ? 'visibility_off' : 'visibility' }}
                            </i>
                            <span>{{ archivosExpandidos[subsubdirectorio.id_disposicion] ? 'Ocultar' : 'Ver' }} {{ filtrarArchivos(subsubdirectorio.archivos).length }} archivos únicos</span>
                          </button>
                        </div>
                        
                        <div v-if="archivosExpandidos[subsubdirectorio.id_disposicion]" class="archivos-lista nivel-2">
                          <div
                            v-for="archivo in filtrarArchivos(subsubdirectorio.archivos)"
                            :key="`archivo-nivel2-${archivo.id_evaluacion}`"
                            :class="['archivo-item', 'nivel-2', { 'seleccionado-masivo': modoCalificacionMasiva && isArchivoSeleccionado(archivo.id_evaluacion) }]"
                          >
                            <!-- Checkbox para selección masiva -->
                            <div v-if="modoCalificacionMasiva" class="checkbox-archivo-masivo">
                              <input
                                type="checkbox"
                                :checked="isArchivoSeleccionado(archivo.id_evaluacion)"
                                @change="toggleArchivoSeleccion(archivo.id_evaluacion)"
                                class="checkbox-archivo"
                              />
                            </div>
                            <div class="archivo-info">
                              <div class="archivo-icon">
                                <i class="material-icons">{{ getFileIcon(archivo.nombre_archivo) }}</i>
                              </div>
                              <div class="archivo-detalles">
                                <h5 class="archivo-nombre" :title="archivo.nombre_archivo">{{ archivo.nombre_archivo }}</h5>
                                <p class="archivo-fecha">{{ formatDate(archivo.fecha_disposicion) }}</p>
                              </div>
                              <div :class="['archivo-estado', getEstadoClass(archivo.estado_archivo)]">
                                {{ archivo.estado_archivo }}
                              </div>
                            </div>
                            
                            <div class="archivo-status">
                              <div :class="['status-indicator', archivo.evaluado ? 'success' : 'pending']">
                                {{ archivo.evaluado ? '✓ Evaluado' : '✗ Sin evaluar' }}
                              </div>
                              <div :class="['status-indicator', archivo.aprobado ? 'success' : 'pending']">
                                {{ archivo.aprobado ? '✓ Aprobado' : '✗ No aprobado' }}
                              </div>
                            </div>
                            
                            <div class="archivo-calificacion-wrapper">
                              <div class="archivo-calificacion">
                                <select
                                  v-if="canEdit"
                                  :value="archivo.evaluacion_archivo"
                                  @change="actualizarEvaluacion({ ...archivo, evaluacion_archivo: parseInt($event.target.value) })"
                                  class="calificacion-select"
                                >
                                  <option
                                    v-for="cal in calificaciones"
                                    :key="cal.id"
                                    :value="cal.id"
                                  >
                                    {{ cal.concepto }} ({{ cal.valor }})
                                  </option>
                                </select>
                                <span v-else class="calificacion-readonly">
                                  {{ getCalificacionText(archivo.evaluacion_archivo) }}
                                </span>
                              </div>
                              <div v-if="archivo.usuario_evaluacion" class="usuario-calificador">
                                <i class="material-icons">person</i>
                                {{ getUsuarioCalificador(archivo.usuario_evaluacion) }}
                              </div>
                            </div>

                            <div class="archivo-acciones">
                              <button @click="showFileInfo(archivo)" class="btn-accion info" title="Ver información">
                                <i class="material-icons">info</i>
                              </button>
                              <button
                                v-if="canDownload"
                                @click="viewFile(archivo)"
                                class="btn-accion view"
                                title="Ver archivo"
                              >
                                <i class="material-icons">visibility</i>
                              </button>
                              <button 
                                v-if="canDownload" 
                                @click="downloadFile(archivo)" 
                                class="btn-accion download" 
                                title="Descargar archivo"
                              >
                                <i class="material-icons">download</i>
                              </button>
                              <button 
                                v-if="canEdit" 
                                @click="editObservaciones(archivo)" 
                                class="btn-accion edit" 
                                title="Editar observaciones"
                              >
                                <i class="material-icons">edit_note</i>
                              </button>
                              <button
                                v-if="canDeleteFile(archivo)"
                                @click="deleteFile(archivo)"
                                class="btn-accion delete" 
                                title="Eliminar archivo (Solo Administradores)"
                              >
                                <i class="material-icons">delete</i>
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div v-else-if="!subsubdirectorio.subdirectorios || subsubdirectorio.subdirectorios.length === 0" class="empty-level">
                        <i class="material-icons">folder_open</i>
                        <span>No hay archivos en este subdirectorio</span>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Archivos del Subdirectorio NIVEL 1 -->
                  <div v-if="subdirectorio.archivos && subdirectorio.archivos.length > 0" class="archivos-subdirectorio nivel-1">
                    <div class="archivos-header nivel-1">
                      <button 
                        @click="toggleArchivos(subdirectorio.id_disposicion)"
                        class="btn-toggle-archivos nivel-1"
                      >
                        <i class="material-icons">
                          {{ archivosExpandidos[subdirectorio.id_disposicion] ? 'visibility_off' : 'visibility' }}
                        </i>
                        <span>{{ archivosExpandidos[subdirectorio.id_disposicion] ? 'Ocultar' : 'Ver' }} {{ filtrarArchivos(subdirectorio.archivos).length }} archivos únicos</span>
                      </button>
                    </div>
                    
                    <div v-if="archivosExpandidos[subdirectorio.id_disposicion]" class="archivos-lista nivel-1">
                      <div
                        v-for="archivo in filtrarArchivos(subdirectorio.archivos)"
                        :key="`archivo-nivel1-${archivo.id_evaluacion}`"
                        :class="['archivo-item', 'nivel-1', { 'seleccionado-masivo': modoCalificacionMasiva && isArchivoSeleccionado(archivo.id_evaluacion) }]"
                      >
                        <!-- Checkbox para selección masiva -->
                        <div v-if="modoCalificacionMasiva" class="checkbox-archivo-masivo">
                          <input
                            type="checkbox"
                            :checked="isArchivoSeleccionado(archivo.id_evaluacion)"
                            @change="toggleArchivoSeleccion(archivo.id_evaluacion)"
                            class="checkbox-archivo"
                          />
                        </div>
                        <div class="archivo-info">
                          <div class="archivo-icon">
                            <i class="material-icons">{{ getFileIcon(archivo.nombre_archivo) }}</i>
                          </div>
                          <div class="archivo-detalles">
                            <h5 class="archivo-nombre" :title="archivo.nombre_archivo">{{ archivo.nombre_archivo }}</h5>
                            <p class="archivo-fecha">{{ formatDate(archivo.fecha_disposicion) }}</p>
                          </div>
                          <div :class="['archivo-estado', getEstadoClass(archivo.estado_archivo)]">
                            {{ archivo.estado_archivo }}
                          </div>
                        </div>
                        
                        <div class="archivo-status">
                          <div :class="['status-indicator', archivo.evaluado ? 'success' : 'pending']">
                            {{ archivo.evaluado ? '✓ Evaluado' : '✗ Sin evaluar' }}
                          </div>
                          <div :class="['status-indicator', archivo.aprobado ? 'success' : 'pending']">
                            {{ archivo.aprobado ? '✓ Aprobado' : '✗ No aprobado' }}
                          </div>
                        </div>
                        
                        <div class="archivo-calificacion-wrapper">
                          <div class="archivo-calificacion">
                            <select
                              v-if="canEdit"
                              :value="archivo.evaluacion_archivo"
                              @change="actualizarEvaluacion({ ...archivo, evaluacion_archivo: parseInt($event.target.value) })"
                              class="calificacion-select"
                            >
                              <option
                                v-for="cal in calificaciones"
                                :key="cal.id"
                                :value="cal.id"
                              >
                                {{ cal.concepto }} ({{ cal.valor }})
                              </option>
                            </select>
                            <span v-else class="calificacion-readonly">
                              {{ getCalificacionText(archivo.evaluacion_archivo) }}
                            </span>
                          </div>
                          <div v-if="archivo.usuario_evaluacion" class="usuario-calificador">
                            <i class="material-icons">person</i>
                            {{ getUsuarioCalificador(archivo.usuario_evaluacion) }}
                          </div>
                        </div>

                        <div class="archivo-acciones">
                          <button @click="showFileInfo(archivo)" class="btn-accion info" title="Ver información">
                            <i class="material-icons">info</i>
                          </button>
                          <button
                            v-if="canDownload"
                            @click="viewFile(archivo)"
                            class="btn-accion view"
                            title="Ver archivo"
                          >
                            <i class="material-icons">visibility</i>
                          </button>
                          <button
                            v-if="canDownload"
                            @click="downloadFile(archivo)"
                            class="btn-accion download" 
                            title="Descargar archivo"
                          >
                            <i class="material-icons">download</i>
                          </button>
                          <button 
                            v-if="canEdit" 
                            @click="editObservaciones(archivo)" 
                            class="btn-accion edit" 
                            title="Editar observaciones"
                          >
                            <i class="material-icons">edit_note</i>
                          </button>
                          <button
                            v-if="canDeleteFile(archivo)"
                            @click="deleteFile(archivo)"
                            class="btn-accion delete" 
                            title="Eliminar archivo (Solo Administradores)"
                          >
                            <i class="material-icons">delete</i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Archivos del Directorio Padre NIVEL 0 -->
              <div v-if="directorio.archivos && directorio.archivos.length > 0" class="archivos-directos">
                <div class="archivos-header nivel-0">
                  <button 
                    @click="toggleArchivos(directorio.id_disposicion)"
                    class="btn-toggle-archivos nivel-0"
                  >
                    <i class="material-icons">
                      {{ archivosExpandidos[directorio.id_disposicion] ? 'visibility_off' : 'visibility' }}
                    </i>
                    <span>{{ archivosExpandidos[directorio.id_disposicion] ? 'Ocultar' : 'Ver' }} {{ filtrarArchivos(directorio.archivos).length }} archivos únicos</span>
                  </button>
                </div>
                
                <div v-if="archivosExpandidos[directorio.id_disposicion]" class="archivos-lista nivel-0">
                  <div
                    v-for="archivo in filtrarArchivos(directorio.archivos)"
                    :key="`archivo-nivel0-${archivo.id_evaluacion}`"
                    :class="['archivo-item', 'nivel-0', { 'seleccionado-masivo': modoCalificacionMasiva && isArchivoSeleccionado(archivo.id_evaluacion) }]"
                  >
                    <!-- Checkbox para selección masiva -->
                    <div v-if="modoCalificacionMasiva" class="checkbox-archivo-masivo">
                      <input
                        type="checkbox"
                        :checked="isArchivoSeleccionado(archivo.id_evaluacion)"
                        @change="toggleArchivoSeleccion(archivo.id_evaluacion)"
                        class="checkbox-archivo"
                      />
                    </div>
                    <div class="archivo-info">
                      <div class="archivo-icon">
                        <i class="material-icons">{{ getFileIcon(archivo.nombre_archivo) }}</i>
                      </div>
                      <div class="archivo-detalles">
                        <h5 class="archivo-nombre" :title="archivo.nombre_archivo">{{ archivo.nombre_archivo }}</h5>
                        <p class="archivo-fecha">{{ formatDate(archivo.fecha_disposicion) }}</p>
                      </div>
                      <div :class="['archivo-estado', getEstadoClass(archivo.estado_archivo)]">
                        {{ archivo.estado_archivo }}
                      </div>
                    </div>
                    
                    <div class="archivo-status">
                      <div :class="['status-indicator', archivo.evaluado ? 'success' : 'pending']">
                        {{ archivo.evaluado ? '✓ Evaluado' : '✗ Sin evaluar' }}
                      </div>
                      <div :class="['status-indicator', archivo.aprobado ? 'success' : 'pending']">
                        {{ archivo.aprobado ? '✓ Aprobado' : '✗ No aprobado' }}
                      </div>
                    </div>
                    
                    <div class="archivo-calificacion-wrapper">
                      <div class="archivo-calificacion">
                        <select
                          v-if="canEdit"
                          :value="archivo.evaluacion_archivo"
                          @change="actualizarEvaluacion({ ...archivo, evaluacion_archivo: parseInt($event.target.value) })"
                          class="calificacion-select"
                        >
                          <option
                            v-for="cal in calificaciones"
                            :key="cal.id"
                            :value="cal.id"
                          >
                            {{ cal.concepto }} ({{ cal.valor }})
                          </option>
                        </select>
                        <span v-else class="calificacion-readonly">
                          {{ getCalificacionText(archivo.evaluacion_archivo) }}
                        </span>
                      </div>
                      <div v-if="archivo.usuario_evaluacion" class="usuario-calificador">
                        <i class="material-icons">person</i>
                        {{ getUsuarioCalificador(archivo.usuario_evaluacion) }}
                      </div>
                    </div>

                    <div class="archivo-acciones">
                      <button @click="showFileInfo(archivo)" class="btn-accion info" title="Ver información">
                        <i class="material-icons">info</i>
                      </button>
                      <button
                        v-if="canDownload"
                        @click="viewFile(archivo)"
                        class="btn-accion view"
                        title="Ver archivo"
                      >
                        <i class="material-icons">visibility</i>
                      </button>
                      <button
                        v-if="canDownload"
                        @click="downloadFile(archivo)"
                        class="btn-accion download"
                        title="Descargar archivo"
                      >
                        <i class="material-icons">download</i>
                      </button>
                      <button 
                        v-if="canEdit" 
                        @click="editObservaciones(archivo)" 
                        class="btn-accion edit" 
                        title="Editar observaciones"
                      >
                        <i class="material-icons">edit_note</i>
                      </button>
                      <button
                        v-if="canDeleteFile(archivo)"
                        @click="deleteFile(archivo)"
                        class="btn-accion delete" 
                        title="Eliminar archivo (Solo Administradores)"
                      >
                        <i class="material-icons">delete</i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Estado Vacío -->
          <div v-if="directoriosFiltrados.length === 0" class="empty-state">
            <i class="material-icons">inbox</i>
            <h3>No se encontraron directorios</h3>
            <p>No hay directorios para mostrar con los filtros aplicados.</p>
          </div>
        </div>
      </section>
    </main>

<!-- Modal de Información del Archivo -->
    <div v-if="showFileInfoModal" class="modal-overlay" @click="closeFileInfoModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>
            <i class="material-icons">info</i>
            Información del Archivo
          </h3>
          <button @click="closeFileInfoModal" class="modal-close">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body">
          <div v-if="selectedFileInfo" class="file-info">
            <div class="info-group">
              <label>Nombre del archivo:</label>
              <span>{{ selectedFileInfo.nombre_archivo }}</span>
            </div>
            <div class="info-group">
              <label>Estado:</label>
              <span :class="['estado-badge', getEstadoClass(selectedFileInfo.estado_archivo)]">
                {{ selectedFileInfo.estado_archivo }}
              </span>
            </div>
            <div class="info-group">
              <label>Ruta completa:</label>
              <div v-if="editandoRuta && canEdit" class="ruta-editable">
                <textarea 
                  v-model="rutaEditForm"
                  class="ruta-textarea"
                  rows="3"
                  placeholder="Ingrese la nueva ruta del archivo..."
                ></textarea>
                <div class="ruta-actions">
                  <button @click="guardarRuta" class="btn-guardar-ruta">
                    <i class="material-icons">save</i>
                    Guardar
                  </button>
                  <button @click="cancelarEdicionRuta" class="btn-cancelar-ruta">
                    <i class="material-icons">cancel</i>
                    Cancelar
                  </button>
                </div>
              </div>
              <div v-else class="ruta-container">
                <span class="ruta-texto">{{ linuxToWindowsPath(selectedFileInfo.ruta_completa) }}</span>
                <button 
                  v-if="canEdit" 
                  @click="iniciarEdicionRuta" 
                  class="btn-editar-ruta"
                  title="Editar ruta del archivo"
                >
                  <i class="material-icons">edit</i>
                </button>
              </div>
            </div>
            <div class="info-group">
              <label>Fecha disposición:</label>
              <span>{{ formatDate(selectedFileInfo.fecha_disposicion) }}</span>
            </div>
            <div v-if="selectedFileInfo.usuario_evaluacion" class="info-group usuario-evaluacion-info">
              <label>Calificado por:</label>
              <span class="usuario-badge">
                <i class="material-icons">person</i>
                {{ getUsuarioCalificador(selectedFileInfo.usuario_evaluacion) }}
              </span>
            </div>
            <div v-if="selectedFileInfo.observaciones_evaluacion" class="info-group">
              <label>Observaciones:</label>
              <span>{{ selectedFileInfo.observaciones_evaluacion }}</span>
            </div>

            <!-- Sección de Auditoría -->
            <div class="audit-section">
              <div class="audit-header">
                <i class="material-icons">history</i>
                <span>Historial de Auditoría</span>
              </div>

              <!-- Info de subida por plataforma web -->
              <div v-if="fileAuditInfo?.subido_por_plataforma" class="audit-upload-info">
                <div class="upload-badge">
                  <i class="material-icons">cloud_upload</i>
                  <span>Subido desde la plataforma web</span>
                </div>
                <div class="upload-details">
                  <div><strong>Usuario:</strong> {{ fileAuditInfo.info_subida?.usuario }}</div>
                  <div><strong>Fecha:</strong> {{ formatDateTime(fileAuditInfo.info_subida?.fecha) }}</div>
                  <div v-if="fileAuditInfo.info_subida?.ip"><strong>IP:</strong> {{ fileAuditInfo.info_subida.ip }}</div>
                </div>
              </div>

              <!-- Loading -->
              <div v-if="fileAuditLoading" class="audit-loading">
                <i class="material-icons spinning">sync</i>
                <span>Cargando historial...</span>
              </div>

              <!-- Sin historial -->
              <div v-else-if="fileAuditHistory.length === 0" class="audit-empty">
                <i class="material-icons">info_outline</i>
                <span>No hay registros de auditoría para este archivo</span>
              </div>

              <!-- Lista de historial -->
              <div v-else class="audit-list">
                <div v-for="registro in fileAuditHistory" :key="registro.id" class="audit-item">
                  <div class="audit-icon" :class="registro.accion.toLowerCase()">
                    <i class="material-icons">{{ getAuditIcon(registro.accion) }}</i>
                  </div>
                  <div class="audit-content">
                    <div class="audit-action">{{ registro.accion_display }}</div>
                    <div class="audit-meta">
                      <span class="audit-user">{{ registro.usuario }}</span>
                      <span class="audit-date">{{ formatDateTime(registro.fecha_accion) }}</span>
                    </div>
                    <div v-if="registro.plataforma" class="audit-platform">
                      <i class="material-icons">{{ registro.plataforma === 'WEB' ? 'language' : 'desktop_windows' }}</i>
                      {{ registro.plataforma_display }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button v-if="canEdit" @click="editObservaciones(selectedFileInfo)" class="btn-primary">
            <i class="material-icons">edit_note</i> Editar Observaciones
          </button>
          <button v-if="selectedFileInfo && canDeleteFile(selectedFileInfo)" @click="deleteFileRecordOnly(selectedFileInfo)" class="btn-warning" title="Elimina solo el registro de la BD, el archivo físico permanece en la NAS">
            <i class="material-icons">delete_outline</i> Solo Registro
          </button>
          <button v-if="selectedFileInfo && canDeleteFile(selectedFileInfo)" @click="deleteFileComplete(selectedFileInfo)" class="btn-danger" title="Elimina el registro Y el archivo físico de la NAS">
            <i class="material-icons">delete_forever</i> Eliminar Todo
          </button>
          <button @click="closeFileInfoModal" class="btn-secondary">Cerrar</button>
        </div>
      </div>
    </div>

    <!-- Modal de Observaciones -->
    <div v-if="showObservacionesModal" class="modal-overlay" @click="closeObservacionesModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>
            <i class="material-icons">note_add</i>
            Observaciones - {{ editingFile?.nombre_archivo }}
          </h3>
          <button @click="closeObservacionesModal" class="modal-close">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label>Observaciones de Evaluación:</label>
            <textarea 
              v-model="observacionesForm"
              placeholder="Ingrese observaciones sobre la evaluación del archivo..."
              rows="5"
            ></textarea>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeObservacionesModal" class="btn-secondary">Cancelar</button>
          <button @click="saveObservaciones" class="btn-primary">Guardar</button>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmación de Eliminación -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>
            <i class="material-icons">warning</i>
            Confirmar Eliminación
          </h3>
          <button @click="closeDeleteModal" class="modal-close">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body">
          <p><strong>¿Estás seguro de que deseas eliminar este directorio?</strong></p>
          <p>Directorio: <code>{{ directorioAEliminar?.nombre_directorio }}</code></p>
          <p>Ruta: <code>{{ linuxToWindowsPath(directorioAEliminar?.jerarquia_completa) }}</code></p>
          <div v-if="directorioAEliminar?.total_archivos > 0" class="warning-box">
            <i class="material-icons">warning</i>
            <p>Este directorio contiene <strong>{{ directorioAEliminar.total_archivos }} archivos</strong> que también serán eliminados.</p>
          </div>
          <p><strong>Esta acción no se puede deshacer.</strong></p>
        </div>
        
        <div class="modal-footer">
          <button @click="closeDeleteModal" class="btn-secondary">Cancelar</button>
          <button @click="confirmarEliminacion" class="btn-danger">
            <i class="material-icons">delete</i>
            Eliminar Directorio
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de Eliminación de Archivos -->
    <div v-if="showDeleteFileModal" class="modal-overlay" @click="closeDeleteFileModal">
      <div class="modal-content delete-file-modal" @click.stop>
        <div class="modal-header danger">
          <h3>
            <i class="material-icons">delete_forever</i>
            Eliminar Archivo
          </h3>
          <button @click="closeDeleteFileModal" class="modal-close">
            <i class="material-icons">close</i>
          </button>
        </div>

        <div class="modal-body">
          <div class="file-delete-info">
            <div class="file-icon-large">
              <i class="material-icons">description</i>
            </div>
            <div class="file-details">
              <p class="file-name">{{ archivoAEliminar?.nombre_archivo }}</p>
              <p class="file-path">{{ archivoAEliminar?.ruta_completa }}</p>
            </div>
          </div>

          <div class="delete-options">
            <h4>Selecciona el tipo de eliminación:</h4>

            <div class="delete-option" @click="executeDeleteFile(false)">
              <div class="option-icon warning">
                <i class="material-icons">delete_outline</i>
              </div>
              <div class="option-content">
                <p class="option-title">Solo Eliminar Registro</p>
                <p class="option-description">Elimina el registro de la base de datos. El archivo físico permanecerá en la NAS.</p>
              </div>
              <button class="btn-warning" :disabled="eliminandoArchivo">
                <i class="material-icons">delete_outline</i>
                Solo Registro
              </button>
            </div>

            <div class="delete-option danger" @click="executeDeleteFile(true)">
              <div class="option-icon danger">
                <i class="material-icons">delete_forever</i>
              </div>
              <div class="option-content">
                <p class="option-title">Eliminar Completamente</p>
                <p class="option-description">Elimina el registro Y el archivo físico de la NAS. Esta acción es PERMANENTE e IRREVERSIBLE.</p>
              </div>
              <button class="btn-danger" :disabled="eliminandoArchivo">
                <i class="material-icons">delete_forever</i>
                Eliminar Todo
              </button>
            </div>
          </div>

          <div v-if="eliminandoArchivo" class="delete-loading">
            <div class="spinner"></div>
            <p>Eliminando archivo...</p>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeDeleteFileModal" class="btn-secondary" :disabled="eliminandoArchivo">
            Cancelar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de Subida de Archivos -->
    <UploadModal
      :is-open="showUploadModal"
      :current-path="currentUploadPath"
      :initial-files="pendingUploadFiles"
      :municipio-nombre="municipioName"
      :existing-file-names="existingFileNames"
      @close="closeUploadModal"
      @upload-complete="handleUploadComplete"
    />

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
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { format, parseISO } from 'date-fns'
import { es } from 'date-fns/locale'
import { getMunicipioById } from '@/api/municipios'
import api from '@/api/config'
import { linuxToWindowsPath } from '@/utils/pathUtils'
import UploadModal from '@/components/common/UploadModal.vue'

// ============ INTERFACES ============
interface EvaluacionArchivo {
  id_evaluacion: number
  id_archivo: number
  id_disposicion: number
  nombre_archivo: string
  ruta_completa: string
  fecha_disposicion: string | null
  observacion_original: string | null
  hash_contenido: string | null
  usuario_windows: string | null
  peso_memoria: string | null
  evaluacion_archivo: number | null
  estado_archivo: string
  observaciones_evaluacion: string | null
  fecha_creacion: string
  fecha_actualizacion: string
  usuario_evaluacion: string | null
  evaluado: boolean
  aprobado: boolean
  directorio_padre: string
  jerarquia_completa: string
  concepto_calificacion: string
  subido_por_plataforma: string | null  // Usuario que subió el archivo desde la plataforma web
}

interface Calificacion {
  id: number
  concepto: string
  valor: number
}

interface DirectorioData {
  id_disposicion: number
  nombre_directorio: string
  jerarquia_completa: string
  ruta_acceso: string
  dispuesto: boolean
  evaluado: boolean
  aprobado: boolean
  fecha_disposicion: string | null
  observaciones: string | null
  estadisticas: {
    total_archivos: number
    pendientes: number
    evaluados: number
    aprobados: number
  }
}

interface DirectorioOptimizado {
  id_disposicion: number
  nombre_directorio: string
  jerarquia_completa: string
  ruta_acceso: string  // Ruta INDEXADA del backend - NO construir manualmente
  nivel: number
  es_padre: boolean
  archivos: EvaluacionArchivo[]
  subdirectorios: DirectorioOptimizado[]
  total_archivos: number
  subdirectorios_count: number
  pendientes: number
  evaluados: number
  aprobados: number
  fecha_disposicion: string | null
  observaciones: string | null
  mecanismo: string  // Mecanismo de financiación (FCP, PGN, ANT, IGAC, etc.)
}

export default defineComponent({
  name: 'ProductosDetalle',

  components: {
    UploadModal
  },

  setup() {
    const route = useRoute()
    const router = useRouter()
    const authStore = useAuthStore()
    
    // ============ ESTADO REACTIVO ============
    const loading = ref(false)
    const error = ref<string | null>(null)
    const municipioName = ref('')
    const accessDenied = ref(false)
    
    // Datos principales
    const evaluacionesArchivos = ref<EvaluacionArchivo[]>([])
    const calificaciones = ref<Calificacion[]>([])
    const directoriosPadre = ref<DirectorioOptimizado[]>([])
    const directoriosData = ref<DirectorioData[]>([])
    
    // Estados de UI
    const directoriosExpandidos = ref<Record<number, boolean>>({})
    const archivosExpandidos = ref<Record<number, boolean>>({})
    
    // Filtros
    const searchTerm = ref('')
    const filtroEstado = ref('')
    const filtroMecanismo = ref('')
    
    // Modales
    const showFileInfoModal = ref(false)
    const selectedFileInfo = ref<EvaluacionArchivo | null>(null)
    const fileAuditHistory = ref<any[]>([])
    const fileAuditLoading = ref(false)
    const fileAuditInfo = ref<{ subido_por_plataforma: boolean; info_subida: any } | null>(null)
    const showObservacionesModal = ref(false)
    const editingFile = ref<EvaluacionArchivo | null>(null)
    const observacionesForm = ref('')

    // Modal de eliminación de directorios
    const showDeleteModal = ref(false)
    const directorioAEliminar = ref<DirectorioOptimizado | null>(null)

    // Modal de eliminación de archivos (con opciones)
    const showDeleteFileModal = ref(false)
    const archivoAEliminar = ref<EvaluacionArchivo | null>(null)
    const eliminandoArchivo = ref(false)

    // Modal de subida de archivos
    const showUploadModal = ref(false)
    const currentUploadPath = ref('')
    const pendingUploadFiles = ref<File[]>([]) // Archivos pendientes del drag & drop
    const existingFileNames = ref<string[]>([]) // Nombres de archivos existentes en el directorio destino

    // Drag & Drop a directorios
    const dropTargetDirectorioId = ref<number | null>(null) // ID del directorio sobre el que se arrastra

    const editandoRuta = ref(false)
    const rutaEditForm = ref('')

    // ============ CALIFICACIÓN MASIVA (Solo Super Admin) ============
    const modoCalificacionMasiva = ref(false)
    const archivosSeleccionados = ref<Set<number>>(new Set())
    const filtroMasivo = ref<'todos' | 'no_calificados' | 'excepto_aprobados'>('no_calificados')
    const calificacionMasivaSeleccionada = ref<number | null>(null)
    const aplicandoCalificacion = ref(false)
    const ultimoLoteMasivo = ref<{
      tiene_lote: boolean
      lote_id: string | null
      fecha: string | null
      archivos_en_lote: number
      usuario: string | null
    } | null>(null)
    const showConfirmacionMasiva = ref(false)

    // ============ DEPURACIÓN DE ARCHIVOS INEXISTENTES (Solo Super Admin) ============
    const verificandoInexistentes = ref(false)
    const depurandoInexistentes = ref(false)
    const showModalDepuracion = ref(false)
    const showConfirmacionDepuracion = ref(false)
    const archivosADepurarSeleccionados = ref<Set<number>>(new Set())
    const resultadoVerificacion = ref<{
      municipio_id: string
      total_archivos: number
      archivos_existentes: number
      archivos_inexistentes: number
      porcentaje_inexistentes: number
      lista_inexistentes: Array<{
        id: number
        nombre: string
        ruta_windows: string
        ruta_linux: string
        fecha_creacion: string | null
        evaluacion_archivo: number
      }>
    } | null>(null)

    // ============ DEPURACIÓN DE DIRECTORIOS INEXISTENTES (Solo Super Admin) ============
    const verificandoDirectorios = ref(false)
    const depurandoDirectorios = ref(false)
    const showModalDepuracionDirs = ref(false)
    const showConfirmacionDepuracionDirs = ref(false)
    const directoriosADepurarSeleccionados = ref<Set<number>>(new Set())
    const resultadoVerificacionDirs = ref<{
      municipio_id: string
      total_directorios: number
      directorios_existentes: number
      directorios_inexistentes: number
      lista_inexistentes: Array<{
        id: number
        nombre: string
        ruta_windows: string
        fecha_disposicion: string | null
        dispuesto: boolean
        evaluado: boolean
        aprobado: boolean
        total_archivos: number
      }>
    } | null>(null)


    // ============ FUNCIONES DE EDICIÓN DE RUTA ============

    const iniciarEdicionRuta = () => {
      if (!selectedFileInfo.value) return
      rutaEditForm.value = selectedFileInfo.value.ruta_completa || ''
      editandoRuta.value = true
    }

    const cancelarEdicionRuta = () => {
      editandoRuta.value = false
      rutaEditForm.value = ''
    }

    const guardarRuta = async () => {
      if (!selectedFileInfo.value || !rutaEditForm.value.trim()) {
        showNotification('La ruta no puede estar vacía', 'warning')
        return
      }
      
      try {
        showNotification('Guardando nueva ruta...', 'info')
        
        const response = await api.patch(`/postoperacion/evaluacion-actualizar/${selectedFileInfo.value.id_evaluacion}/`, {
          ruta_completa: rutaEditForm.value.trim()
        })
        
        // Actualizar archivo en la lista
        const index = evaluacionesArchivos.value.findIndex(a => a.id_evaluacion === selectedFileInfo.value!.id_evaluacion)
        if (index !== -1) {
          evaluacionesArchivos.value[index].ruta_completa = rutaEditForm.value.trim()
        }
        
        // Actualizar archivo seleccionado
        selectedFileInfo.value.ruta_completa = rutaEditForm.value.trim()
        
        showNotification('Ruta actualizada exitosamente', 'success')
        editandoRuta.value = false
        rutaEditForm.value = ''
        
        // Recargar datos para asegurar consistencia
        await loadData()
        
      } catch (error: any) {
        console.error('Error guardando ruta:', error)
        showNotification(`Error al actualizar ruta: ${error.response?.data?.error || error.message}`, 'error')
      }
    }




    // Notificaciones
    const notification = ref({
      show: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning' | 'info',
      icon: 'check_circle',
      timeout: null as number | null
    })

    // ============ COMPUTED PROPERTIES ============
    
    const userPermissions = computed(() => ({
      isSuperAdmin: authStore.isSuperAdmin,
      isAdmin: authStore.isAdmin,
      isProfesional: authStore.isProfesional,
      isAnyAdmin: authStore.isAnyAdmin
    }))
    
    const isProfesionalSinAcceso = computed(() => {
      return userPermissions.value.isProfesional &&
             !userPermissions.value.isAnyAdmin &&
             accessDenied.value
    })
    
    const tieneAccesoADatos = computed(() => {
      if (userPermissions.value.isAnyAdmin) return true
      if (userPermissions.value.isProfesional) {
        // Profesionales pueden ver si tienen acceso, aunque no haya archivos (directorios vacíos)
        return !accessDenied.value && !loading.value && !error.value
      }
      return !error.value && !loading.value
    })
    
    const canEdit = computed(() => userPermissions.value.isSuperAdmin || userPermissions.value.isAdmin)
    const canDelete = computed(() => userPermissions.value.isSuperAdmin || userPermissions.value.isAdmin)
    const canDownload = computed(() => userPermissions.value.isSuperAdmin || userPermissions.value.isAdmin || userPermissions.value.isProfesional)
    // Profesionales pueden subir archivos a sus municipios asignados
    const canUpload = computed(() => {
      // Admins siempre pueden subir
      if (userPermissions.value.isSuperAdmin || userPermissions.value.isAdmin) {
        return true
      }
      // Profesionales pueden subir si tienen acceso al municipio actual
      if (userPermissions.value.isProfesional) {
        const municipioId = Number(route.params.id)
        if (municipioId && !isNaN(municipioId)) {
          return authStore.tieneAccesoAMunicipio(municipioId)
        }
      }
      return false
    })

    // Función para verificar si el usuario puede eliminar un archivo específico
    // Admins pueden eliminar cualquier archivo, profesionales solo los que subieron ellos
    const canDeleteFile = (archivo: EvaluacionArchivo): boolean => {
      // Admin/SuperAdmin pueden eliminar cualquier archivo
      if (userPermissions.value.isSuperAdmin || userPermissions.value.isAdmin) {
        return true
      }
      // Profesional solo puede eliminar archivos que él subió desde la plataforma
      // subido_por_plataforma contiene el username del usuario que subió el archivo desde la web
      if (userPermissions.value.isProfesional && archivo.subido_por_plataforma) {
        return archivo.subido_por_plataforma === authStore.user?.username
      }
      return false
    }

    // ============ COMPUTED CALIFICACIÓN MASIVA ============
    const canUseMassQualification = computed(() => userPermissions.value.isSuperAdmin)

    const archivosSeleccionadosCount = computed(() => archivosSeleccionados.value.size)

    const archivosParaCalificar = computed(() => {
      // Siempre retorna todos los archivos disponibles (el filtro se aplica al momento de enviar)
      return evaluacionesArchivos.value
    })

    const archivosFiltradosPorMasivo = computed(() => {
      // Este computed muestra cuántos serán afectados según el filtro
      let archivos = evaluacionesArchivos.value

      if (filtroMasivo.value === 'no_calificados') {
        archivos = archivos.filter(a => a.evaluacion_archivo === 1 || a.evaluacion_archivo === null)
      } else if (filtroMasivo.value === 'excepto_aprobados') {
        archivos = archivos.filter(a => !a.aprobado)
      }

      return archivos
    })

    const archivosSeleccionadosParaCalificar = computed(() => {
      return archivosParaCalificar.value.filter(a => archivosSeleccionados.value.has(a.id_evaluacion))
    })

    const todosSeleccionados = computed(() => {
      if (archivosParaCalificar.value.length === 0) return false
      return archivosParaCalificar.value.every(a => archivosSeleccionados.value.has(a.id_evaluacion))
    })

    const accessLevelText = computed(() => {
      if (userPermissions.value.isSuperAdmin) return 'Super Administrador'
      if (userPermissions.value.isAdmin) return 'Administrador'  
      if (userPermissions.value.isProfesional) return 'Profesional de Seguimiento'
      return 'Solo Lectura'
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
      const total_directorios = directoriosPadre.value.length
      
      return {
        total_directorios,
        total_archivos,
        pendientes,
        evaluados,
        aprobados
      }
    })

    // ============ FUNCIONES PARA MECANISMO ============
    const extraerMecanismoDesdeRuta = (ruta: string): string => {
      if (!ruta) return 'SIN_MECANISMO'
      
      try {
        // Normaliza la ruta convirtiendo \ a / (por si quedaran rutas Windows)
        const rutaStr = ruta.replace(/\\/g, '/')
        
        // Extrae el mecanismo de la ruta usando el patrón:
        // /[departamento]/[municipio]/[mecanismo]/03_post
        const match = rutaStr.match(/\/(\d{2})\/(\d{3})\/([^\/]+)\/03_post/)
        
        if (match) {
          const mecanismo = match[3].trim()
          return mecanismo || 'SIN_MECANISMO'
        }
        
        return 'SIN_MECANISMO'
      } catch (error) {
        console.warn('Error extrayendo mecanismo:', error)
        return 'ERROR_MECANISMO'
      }
    }

    const mecanismosDisponibles = computed(() => {
      const mecanismos = new Set<string>()

      // Obtener mecanismos de los directorios raíz del árbol
      directoriosPadre.value.forEach(dir => {
        if (dir.mecanismo && !['SIN_MECANISMO', 'ERROR_MECANISMO'].includes(dir.mecanismo)) {
          mecanismos.add(dir.mecanismo)
        }
      })

      return Array.from(mecanismos).sort()
    })

    const getCountMecanismo = (mecanismo: string): number => {
      // Contar total de archivos en directorios de ese mecanismo
      return directoriosPadre.value
        .filter(dir => dir.mecanismo === mecanismo)
        .reduce((sum, dir) => sum + dir.total_archivos, 0)
    }

    const tienesFiltrosActivos = computed(() => {
      return searchTerm.value !== '' || filtroEstado.value !== '' || filtroMecanismo.value !== ''
    })

    // Filtro de directorios por mecanismo - usa el campo mecanismo del nodo
    const directoriosFiltrados = computed(() => {
      // Sin filtro de mecanismo, mostrar todo
      if (!filtroMecanismo.value) {
        return directoriosPadre.value
      }

      // Con filtro de mecanismo, mostrar solo directorios de ese mecanismo
      return directoriosPadre.value.filter(directorio => {
        return directorio.mecanismo === filtroMecanismo.value
      })
    })

    const estadisticasFiltradas = computed(() => {
      if (!filtroMecanismo.value) {
        return estadisticas.value
      }
      
      const archivosDelMecanismo = evaluacionesArchivos.value.filter(archivo => {
        const mecanismo = extraerMecanismoDesdeRuta(archivo.ruta_completa)
        return mecanismo === filtroMecanismo.value
      })
      
      const total_archivos = archivosDelMecanismo.length
      const pendientes = archivosDelMecanismo.filter(a => a.estado_archivo === 'PENDIENTE').length
      const evaluados = archivosDelMecanismo.filter(a => a.evaluado).length
      const aprobados = archivosDelMecanismo.filter(a => a.aprobado).length
      const total_directorios = directoriosFiltrados.value.length
      
      return {
        total_directorios,
        total_archivos,
        pendientes,
        evaluados,
        aprobados
      }
    })

    // ============ FUNCIÓN PARA VERIFICAR ARCHIVOS EN SUBDIRECTORIOS (Utilidad) ============
    const tieneArchivosEnSubdirectoriosProfundos = (directorio: DirectorioOptimizado): boolean => {
      if (directorio.subdirectorios && directorio.subdirectorios.length > 0) {
        for (const sub of directorio.subdirectorios) {
          if (sub.archivos && sub.archivos.length > 0) {
            return true
          }
          if (tieneArchivosEnSubdirectoriosProfundos(sub)) {
            return true
          }
        }
      }
      return false
    }

    // ============ FUNCIONES API ============
    
    const getCalificaciones = async () => {
      try {
        console.log('📄 Obteniendo calificaciones...')
        
        const response = await api.get('/postoperacion/calificaciones-post/')
        
        let data = response
        if (response && typeof response === 'object' && 'data' in response) {
          data = response.data
        }
        
        if (Array.isArray(data)) {
          console.log(`✅ ${data.length} calificaciones obtenidas`)
          return data
        } else if (data && typeof data === 'object' && Array.isArray(data.results)) {
          console.log(`✅ ${data.results.length} calificaciones obtenidas`)
          return data.results
        }
        
        return []
      } catch (error) {
        console.error('Error obteniendo calificaciones:', error)
        return []
      }
    }

    // ============ FUNCIÓN ORDENAMIENTO NUMÉRICO NATURAL ============

    /**
     * Ordena directorios por nombre numérico natural (01_, 02_, 03_, etc.)
     * Ejemplo: ["02_zhf", "04_memor", "01_plano", "03_fto"] -> ["01_plano", "02_zhf", "03_fto", "04_memor"]
     */
    const ordenarPorNombreNumerico = (directorios: DirectorioOptimizado[]): DirectorioOptimizado[] => {
      return directorios.sort((a, b) => {
        // Extraer el número al inicio del nombre (ej: "01_plano" -> 1, "02_zhf" -> 2)
        const numA = parseInt(a.nombre_directorio.match(/^(\d+)/)?.[1] || '999')
        const numB = parseInt(b.nombre_directorio.match(/^(\d+)/)?.[1] || '999')

        // Si ambos tienen números, ordenar numéricamente
        if (!isNaN(numA) && !isNaN(numB)) {
          return numA - numB
        }

        // Si solo uno tiene número, ese va primero
        if (!isNaN(numA)) return -1
        if (!isNaN(numB)) return 1

        // Si ninguno tiene número, ordenar alfabéticamente
        return a.nombre_directorio.localeCompare(b.nombre_directorio, 'es', { numeric: true })
      })
    }

    // ============ FUNCIÓN CONSTRUIR ÁRBOL 6 NIVELES ============

    const construirArbolOptimizado = (directoriosData: DirectorioData[], archivosData: EvaluacionArchivo[]): DirectorioOptimizado[] => {
      console.log('🌳 Construyendo árbol optimizado CASE-INSENSITIVE con 6 niveles...')
      console.log(`📊 Total directorios recibidos: ${directoriosData.length}`)
      console.log(`📊 Total archivos recibidos: ${archivosData.length}`)
      
      // Crear mapa de archivos por disposición
      const archivosPorDisposicion = new Map<number, EvaluacionArchivo[]>()
      archivosData.forEach((archivo) => {
        if (!archivosPorDisposicion.has(archivo.id_disposicion)) {
          archivosPorDisposicion.set(archivo.id_disposicion, [])
        }
        archivosPorDisposicion.get(archivo.id_disposicion)!.push(archivo)
      })
      
      // 1. Identificar directorios raíz únicos (CASE-INSENSITIVE + SEPARADOS POR MECANISMO)
      const directoriosRaizMap = new Map<string, DirectorioData[]>()

      directoriosData.forEach((dir) => {
        const partes = dir.jerarquia_completa.split('/').filter(p => p.trim() !== '')
        const directorioRaiz = partes[0] || dir.jerarquia_completa
        const directorioRaizNormalizado = directorioRaiz.toLowerCase()

        // Extraer mecanismo de la ruta del directorio para evitar mezclar mecanismos
        const mecanismoDir = extraerMecanismoDesdeRuta(dir.ruta_acceso)

        // Omitir entradas que son el directorio raíz 03_post (nodo fantasma)
        if (directorioRaizNormalizado === '03_post') return

        // Clave de agrupación = mecanismo + nombre (así ANT/01_aprob_econo != IGAC/01_aprob_econo)
        const claveAgrupacion = `${mecanismoDir}__${directorioRaizNormalizado}`

        if (!directoriosRaizMap.has(claveAgrupacion)) {
          directoriosRaizMap.set(claveAgrupacion, [])
        }
        directoriosRaizMap.get(claveAgrupacion)!.push(dir)
      })

      console.log(`🔍 Directorios raíz únicos encontrados: ${directoriosRaizMap.size}`)
      
      // 2. Construir estructura de árbol
      const directoriosResultado: DirectorioOptimizado[] = []
      
      directoriosRaizMap.forEach((directoriosDelGrupo, claveAgrupacion) => {
        // Extraer mecanismo y nombre de la clave de agrupación
        const partesKey = claveAgrupacion.split('__')
        const mecanismoGrupo = partesKey[0] || 'SIN_MECANISMO'
        const nombreRaizNormalizado = partesKey[1] || claveAgrupacion
        console.log(`🔨 Construyendo directorio raíz: ${nombreRaizNormalizado} [${mecanismoGrupo}]`)
        
        // Encontrar el directorio padre (nivel 0)
        const directorioPadre = directoriosDelGrupo.find(d => {
          const partes = d.jerarquia_completa.split('/').filter(p => p.trim() !== '')
          return partes.length === 1
        }) || directoriosDelGrupo[0]
        
        const nombreRaizReal = nombreRaizNormalizado
        
        // Filtrar subdirectorios (más de 1 nivel)
        const subdirectoriosData = directoriosDelGrupo.filter(d => {
          const partes = d.jerarquia_completa.split('/').filter(p => p.trim() !== '')
          return partes.length > 1 && d !== directorioPadre
        })
        
        // ============ CONSTRUCCIÓN DE SUBDIRECTORIOS NIVEL 1 ============
        const subdirectoriosNivel1Map = new Map<string, DirectorioData[]>()
        subdirectoriosData.forEach(sub => {
          const partes = sub.jerarquia_completa.split('/').filter(p => p.trim() !== '')
          if (partes.length >= 2) {
            const nivel1 = partes[1]
            const nivel1Normalizado = nivel1.toLowerCase()
            if (!subdirectoriosNivel1Map.has(nivel1Normalizado)) {
              subdirectoriosNivel1Map.set(nivel1Normalizado, [])
            }
            subdirectoriosNivel1Map.get(nivel1Normalizado)!.push(sub)
          }
        })
        
        const subdirectoriosOptimizados: DirectorioOptimizado[] = []
        
        subdirectoriosNivel1Map.forEach((subdirs, nombreSubNormalizado) => {
          console.log(`  🔧 Procesando subdirectorio nivel 1: ${nombreSubNormalizado}`)
          
          const subPrincipal = subdirs.find(s => {
            const partes = s.jerarquia_completa.split('/').filter(p => p.trim() !== '')
            return partes.length === 2
          }) || subdirs[0]
          
          const nombreRealSubdirectorio = nombreSubNormalizado
          
          // ============ CONSTRUCCIÓN DE SUBDIRECTORIOS NIVEL 2 ============
          const subdirectoriosNivel2 = subdirs.filter(s => {
            const partes = s.jerarquia_completa.split('/').filter(p => p.trim() !== '')
            return partes.length >= 3
          })
          
          const subdirectoriosNivel2Optimizados: DirectorioOptimizado[] = []
          const nivel2Map = new Map<string, DirectorioData[]>()
          
          subdirectoriosNivel2.forEach(sub2 => {
            const partes = sub2.jerarquia_completa.split('/').filter(p => p.trim() !== '')
            if (partes.length >= 3) {
              const nivel2Nombre = partes[2]
              const nivel2Normalizado = nivel2Nombre.toLowerCase()
              if (!nivel2Map.has(nivel2Normalizado)) {
                nivel2Map.set(nivel2Normalizado, [])
              }
              nivel2Map.get(nivel2Normalizado)!.push(sub2)
            }
          })
          
          nivel2Map.forEach((subdirs2, nombreSub2Normalizado) => {
            console.log(`      🔸 Procesando subdirectorio nivel 2: ${nombreSub2Normalizado}`)
            
            const sub2Principal = subdirs2.find(s => {
              const partes = s.jerarquia_completa.split('/').filter(p => p.trim() !== '')
              return partes.length === 3
            }) || subdirs2[0]
            
            const nombreRealSub2 = nombreSub2Normalizado
            
            // ============ CONSTRUCCIÓN DE SUBDIRECTORIOS NIVEL 3 ============
            const subdirectoriosNivel3 = subdirs2.filter(s => {
              const partes = s.jerarquia_completa.split('/').filter(p => p.trim() !== '')
              return partes.length >= 4
            })
            
            const subdirectoriosNivel3Optimizados: DirectorioOptimizado[] = []
            const nivel3Map = new Map<string, DirectorioData[]>()
            
            subdirectoriosNivel3.forEach(sub3 => {
              const partes = sub3.jerarquia_completa.split('/').filter(p => p.trim() !== '')
              if (partes.length >= 4) {
                const nivel3Nombre = partes[3]
                const nivel3Normalizado = nivel3Nombre.toLowerCase()
                if (!nivel3Map.has(nivel3Normalizado)) {
                  nivel3Map.set(nivel3Normalizado, [])
                }
                nivel3Map.get(nivel3Normalizado)!.push(sub3)
              }
            })
            
            nivel3Map.forEach((subdirs3, nombreSub3Normalizado) => {
              console.log(`        🔷 Procesando subdirectorio nivel 3: ${nombreSub3Normalizado}`)

              const sub3Principal = subdirs3.find(s => {
                const partes = s.jerarquia_completa.split('/').filter(p => p.trim() !== '')
                return partes.length === 4
              }) || subdirs3[0]
              const nombreRealSub3 = nombreSub3Normalizado

              // ============ CONSTRUCCIÓN DE SUBDIRECTORIOS NIVEL 4 ============
              const subdirectoriosNivel4 = subdirs3.filter(s => {
                const partes = s.jerarquia_completa.split('/').filter(p => p.trim() !== '')
                return partes.length >= 5
              })

              const subdirectoriosNivel4Optimizados: DirectorioOptimizado[] = []
              const nivel4Map = new Map<string, DirectorioData[]>()

              subdirectoriosNivel4.forEach(sub4 => {
                const partes = sub4.jerarquia_completa.split('/').filter(p => p.trim() !== '')
                if (partes.length >= 5) {
                  const nivel4Nombre = partes[4]
                  const nivel4Normalizado = nivel4Nombre.toLowerCase()
                  if (!nivel4Map.has(nivel4Normalizado)) {
                    nivel4Map.set(nivel4Normalizado, [])
                  }
                  nivel4Map.get(nivel4Normalizado)!.push(sub4)
                }
              })

              nivel4Map.forEach((subdirs4, nombreSub4Normalizado) => {
                console.log(`          🔶 Procesando subdirectorio nivel 4: ${nombreSub4Normalizado}`)

                const sub4Principal = subdirs4.find(s => {
                  const partes = s.jerarquia_completa.split('/').filter(p => p.trim() !== '')
                  return partes.length === 5
                }) || subdirs4[0]
                const nombreRealSub4 = nombreSub4Normalizado

                // ============ CONSTRUCCIÓN DE SUBDIRECTORIOS NIVEL 5 ============
                const subdirectoriosNivel5 = subdirs4.filter(s => {
                  const partes = s.jerarquia_completa.split('/').filter(p => p.trim() !== '')
                  return partes.length >= 6
                })

                const subdirectoriosNivel5Optimizados: DirectorioOptimizado[] = []
                const nivel5Map = new Map<string, DirectorioData[]>()

                subdirectoriosNivel5.forEach(sub5 => {
                  const partes = sub5.jerarquia_completa.split('/').filter(p => p.trim() !== '')
                  if (partes.length >= 6) {
                    const nivel5Nombre = partes[5]
                    const nivel5Normalizado = nivel5Nombre.toLowerCase()
                    if (!nivel5Map.has(nivel5Normalizado)) {
                      nivel5Map.set(nivel5Normalizado, [])
                    }
                    nivel5Map.get(nivel5Normalizado)!.push(sub5)
                  }
                })

                nivel5Map.forEach((subdirs5, nombreSub5Normalizado) => {
                  console.log(`            🔷 Procesando subdirectorio nivel 5: ${nombreSub5Normalizado}`)

                  const sub5Principal = subdirs5[0]
                  const nombreRealSub5 = nombreSub5Normalizado

                  // ⭐ COMBINAR archivos de TODOS los registros nivel 5+ con el mismo nombre
                  const archivosSub5 = new Map<number, EvaluacionArchivo>()

                  subdirs5.forEach(subReg5 => {
                    const archivos = archivosPorDisposicion.get(subReg5.id_disposicion) || []
                    console.log(`              📄 Directorio ${subReg5.id_disposicion} tiene ${archivos.length} archivos`)
                    archivos.forEach(archivo => {
                      archivosSub5.set(archivo.id_evaluacion, archivo)
                    })
                  })

                  const archivosFinalesSub5 = Array.from(archivosSub5.values())
                  console.log(`              ✅ Total archivos nivel 5: ${archivosFinalesSub5.length}`)

                  // ⭐⭐⭐ NIVEL 5: Usar forward slashes ⭐⭐⭐
                  subdirectoriosNivel5Optimizados.push({
                    id_disposicion: sub5Principal.id_disposicion,
                    nombre_directorio: nombreRealSub5,
                    jerarquia_completa: `03_post/${sub5Principal.jerarquia_completa}`, // ← LINUX FORMAT
                    ruta_acceso: sub5Principal.ruta_acceso, // ← RUTA INDEXADA DEL BACKEND
                    nivel: 5,
                    es_padre: false,
                    archivos: archivosFinalesSub5,
                    subdirectorios: [],
                    total_archivos: archivosFinalesSub5.length,
                    subdirectorios_count: 0,
                    pendientes: archivosFinalesSub5.filter(a => a.estado_archivo === 'PENDIENTE').length,
                    evaluados: archivosFinalesSub5.filter(a => a.evaluado).length,
                    aprobados: archivosFinalesSub5.filter(a => a.aprobado).length,
                    fecha_disposicion: sub5Principal.fecha_disposicion,
                    observaciones: sub5Principal.observaciones,
                    mecanismo: mecanismoGrupo
                  })
                })

                // 🔢 ORDENAR subdirectorios nivel 5 numéricamente
                ordenarPorNombreNumerico(subdirectoriosNivel5Optimizados)

                // ⭐ COMBINAR archivos del subdirectorio nivel 4 (excluyendo los de nivel 5)
                const archivosSub4 = new Map<number, EvaluacionArchivo>()

                subdirs4.forEach(subReg4 => {
                  const archivos = archivosPorDisposicion.get(subReg4.id_disposicion) || []
                  console.log(`            📄 Directorio ${subReg4.id_disposicion} tiene ${archivos.length} archivos`)
                  archivos.forEach(archivo => {
                    const yaEstaEnNivel5 = subdirectoriosNivel5Optimizados.some(sub5 =>
                      sub5.archivos.some(arch => arch.id_evaluacion === archivo.id_evaluacion)
                    )

                    if (!yaEstaEnNivel5) {
                      archivosSub4.set(archivo.id_evaluacion, archivo)
                    }
                  })
                })

                const archivosFinalesSub4 = Array.from(archivosSub4.values())
                console.log(`            ✅ Total archivos nivel 4: ${archivosFinalesSub4.length}`)

                // Calcular estadísticas totales nivel 4
                let totalArchivosNivel4 = archivosFinalesSub4.length
                let pendientesNivel4 = archivosFinalesSub4.filter(a => a.estado_archivo === 'PENDIENTE').length
                let evaluadosNivel4 = archivosFinalesSub4.filter(a => a.evaluado).length
                let aprobadosNivel4 = archivosFinalesSub4.filter(a => a.aprobado).length

                subdirectoriosNivel5Optimizados.forEach(sub5 => {
                  totalArchivosNivel4 += sub5.total_archivos
                  pendientesNivel4 += sub5.pendientes
                  evaluadosNivel4 += sub5.evaluados
                  aprobadosNivel4 += sub5.aprobados
                })

                // ⭐⭐⭐ NIVEL 4: Usar forward slashes ⭐⭐⭐
                subdirectoriosNivel4Optimizados.push({
                  id_disposicion: sub4Principal.id_disposicion,
                  nombre_directorio: nombreRealSub4,
                  jerarquia_completa: `03_post/${sub4Principal.jerarquia_completa}`, // ← LINUX FORMAT
                  ruta_acceso: sub4Principal.ruta_acceso, // ← RUTA INDEXADA DEL BACKEND
                  nivel: 4,
                  es_padre: false,
                  archivos: archivosFinalesSub4,
                  subdirectorios: subdirectoriosNivel5Optimizados,
                  total_archivos: totalArchivosNivel4,
                  subdirectorios_count: subdirectoriosNivel5Optimizados.length,
                  pendientes: pendientesNivel4,
                  evaluados: evaluadosNivel4,
                  aprobados: aprobadosNivel4,
                  fecha_disposicion: sub4Principal.fecha_disposicion,
                  observaciones: sub4Principal.observaciones,
                  mecanismo: mecanismoGrupo
                })
              })

              // 🔢 ORDENAR subdirectorios nivel 4 numéricamente
              ordenarPorNombreNumerico(subdirectoriosNivel4Optimizados)

              // ⭐ COMBINAR archivos del subdirectorio nivel 3 (excluyendo los de nivel 4)
              const archivosSub3 = new Map<number, EvaluacionArchivo>()

              subdirs3.forEach(subReg3 => {
                const archivos = archivosPorDisposicion.get(subReg3.id_disposicion) || []
                console.log(`          📄 Directorio ${subReg3.id_disposicion} tiene ${archivos.length} archivos`)
                archivos.forEach(archivo => {
                  const yaEstaEnNivel4o5 = subdirectoriosNivel4Optimizados.some(sub4 =>
                    sub4.archivos.some(arch => arch.id_evaluacion === archivo.id_evaluacion) ||
                    sub4.subdirectorios.some(sub5 =>
                      sub5.archivos.some(arch => arch.id_evaluacion === archivo.id_evaluacion)
                    )
                  )

                  if (!yaEstaEnNivel4o5) {
                    archivosSub3.set(archivo.id_evaluacion, archivo)
                  }
                })
              })

              const archivosFinalesSub3 = Array.from(archivosSub3.values())
              console.log(`          ✅ Total archivos nivel 3: ${archivosFinalesSub3.length}`)

              // Calcular estadísticas totales nivel 3
              let totalArchivosNivel3 = archivosFinalesSub3.length
              let pendientesNivel3 = archivosFinalesSub3.filter(a => a.estado_archivo === 'PENDIENTE').length
              let evaluadosNivel3 = archivosFinalesSub3.filter(a => a.evaluado).length
              let aprobadosNivel3 = archivosFinalesSub3.filter(a => a.aprobado).length

              subdirectoriosNivel4Optimizados.forEach(sub4 => {
                totalArchivosNivel3 += sub4.total_archivos
                pendientesNivel3 += sub4.pendientes
                evaluadosNivel3 += sub4.evaluados
                aprobadosNivel3 += sub4.aprobados
              })

              // ⭐⭐⭐ CAMBIO PRINCIPAL NIVEL 3: Usar forward slashes ⭐⭐⭐
              subdirectoriosNivel3Optimizados.push({
                id_disposicion: sub3Principal.id_disposicion,
                nombre_directorio: nombreRealSub3,
                jerarquia_completa: `03_post/${sub3Principal.jerarquia_completa}`, // ← LINUX FORMAT
                ruta_acceso: sub3Principal.ruta_acceso, // ← RUTA INDEXADA DEL BACKEND
                nivel: 3,
                es_padre: false,
                archivos: archivosFinalesSub3,
                subdirectorios: subdirectoriosNivel4Optimizados,
                total_archivos: totalArchivosNivel3,
                subdirectorios_count: subdirectoriosNivel4Optimizados.length,
                pendientes: pendientesNivel3,
                evaluados: evaluadosNivel3,
                aprobados: aprobadosNivel3,
                fecha_disposicion: sub3Principal.fecha_disposicion,
                observaciones: sub3Principal.observaciones,
                mecanismo: mecanismoGrupo
              })
            })

            // 🔢 ORDENAR subdirectorios nivel 3 numéricamente
            ordenarPorNombreNumerico(subdirectoriosNivel3Optimizados)

            // ⭐ COMBINAR archivos del subdirectorio nivel 2
            const archivosSub2 = new Map<number, EvaluacionArchivo>()

            subdirs2.forEach(subReg2 => {
              const archivos = archivosPorDisposicion.get(subReg2.id_disposicion) || []
              console.log(`        📄 Directorio ${subReg2.id_disposicion} tiene ${archivos.length} archivos`)
              archivos.forEach(archivo => {
                const yaEstaEnNivel3o4o5 = subdirectoriosNivel3Optimizados.some(sub3 =>
                  sub3.archivos.some(arch => arch.id_evaluacion === archivo.id_evaluacion) ||
                  sub3.subdirectorios.some(sub4 =>
                    sub4.archivos.some(arch => arch.id_evaluacion === archivo.id_evaluacion) ||
                    sub4.subdirectorios.some(sub5 =>
                      sub5.archivos.some(arch => arch.id_evaluacion === archivo.id_evaluacion)
                    )
                  )
                )

                if (!yaEstaEnNivel3o4o5) {
                  archivosSub2.set(archivo.id_evaluacion, archivo)
                }
              })
            })
            
            const archivosFinalesSub2 = Array.from(archivosSub2.values())
            console.log(`        ✅ Total archivos nivel 2: ${archivosFinalesSub2.length}`)
            
            // Calcular estadísticas totales
            let totalArchivosNivel2 = archivosFinalesSub2.length
            let pendientesNivel2 = archivosFinalesSub2.filter(a => a.estado_archivo === 'PENDIENTE').length
            let evaluadosNivel2 = archivosFinalesSub2.filter(a => a.evaluado).length
            let aprobadosNivel2 = archivosFinalesSub2.filter(a => a.aprobado).length
            
            subdirectoriosNivel3Optimizados.forEach(sub3 => {
              totalArchivosNivel2 += sub3.total_archivos
              pendientesNivel2 += sub3.pendientes
              evaluadosNivel2 += sub3.evaluados
              aprobadosNivel2 += sub3.aprobados
            })
            
            // ⭐⭐⭐ CAMBIO PRINCIPAL NIVEL 2: Usar forward slashes ⭐⭐⭐
            subdirectoriosNivel2Optimizados.push({
              id_disposicion: sub2Principal.id_disposicion,
              nombre_directorio: nombreRealSub2,
              jerarquia_completa: `03_post/${sub2Principal.jerarquia_completa}`, // ← LINUX FORMAT
              ruta_acceso: sub2Principal.ruta_acceso, // ← RUTA INDEXADA DEL BACKEND
              nivel: 2,
              es_padre: false,
              archivos: archivosFinalesSub2,
              subdirectorios: subdirectoriosNivel3Optimizados,
              total_archivos: totalArchivosNivel2,
              subdirectorios_count: subdirectoriosNivel3Optimizados.length,
              pendientes: pendientesNivel2,
              evaluados: evaluadosNivel2,
              aprobados: aprobadosNivel2,
              fecha_disposicion: sub2Principal.fecha_disposicion,
              observaciones: sub2Principal.observaciones,
              mecanismo: mecanismoGrupo
            })
          })

          // 🔢 ORDENAR subdirectorios nivel 2 numéricamente
          ordenarPorNombreNumerico(subdirectoriosNivel2Optimizados)

          // ⭐ COMBINAR archivos del subdirectorio nivel 1
          const todosLosArchivosNivel1 = new Map<number, EvaluacionArchivo>()

          subdirs.forEach(subReg => {
            const archivos = archivosPorDisposicion.get(subReg.id_disposicion) || []
            console.log(`      📄 Directorio ${subReg.id_disposicion} tiene ${archivos.length} archivos`)
            archivos.forEach(archivo => {
              const yaEstaEnNivel2o3o4o5 = subdirectoriosNivel2Optimizados.some(sub2 =>
                sub2.archivos.some(arch => arch.id_evaluacion === archivo.id_evaluacion) ||
                sub2.subdirectorios.some(sub3 =>
                  sub3.archivos.some(arch => arch.id_evaluacion === archivo.id_evaluacion) ||
                  sub3.subdirectorios.some(sub4 =>
                    sub4.archivos.some(arch => arch.id_evaluacion === archivo.id_evaluacion) ||
                    sub4.subdirectorios.some(sub5 =>
                      sub5.archivos.some(arch => arch.id_evaluacion === archivo.id_evaluacion)
                    )
                  )
                )
              )

              if (!yaEstaEnNivel2o3o4o5) {
                todosLosArchivosNivel1.set(archivo.id_evaluacion, archivo)
              }
            })
          })
          
          const archivosFinalesNivel1 = Array.from(todosLosArchivosNivel1.values())
          console.log(`      ✅ Total archivos nivel 1: ${archivosFinalesNivel1.length}`)
          
          // Calcular estadísticas totales
          let totalArchivosNivel1 = archivosFinalesNivel1.length
          let pendientesNivel1 = archivosFinalesNivel1.filter(a => a.estado_archivo === 'PENDIENTE').length
          let evaluadosNivel1 = archivosFinalesNivel1.filter(a => a.evaluado).length
          let aprobadosNivel1 = archivosFinalesNivel1.filter(a => a.aprobado).length
          
          subdirectoriosNivel2Optimizados.forEach(sub2 => {
            totalArchivosNivel1 += sub2.total_archivos
            pendientesNivel1 += sub2.pendientes
            evaluadosNivel1 += sub2.evaluados
            aprobadosNivel1 += sub2.aprobados
          })
          
          // ⭐⭐⭐ CAMBIO PRINCIPAL NIVEL 1: Usar forward slashes ⭐⭐⭐
          subdirectoriosOptimizados.push({
            id_disposicion: subPrincipal.id_disposicion,
            nombre_directorio: nombreRealSubdirectorio,
            jerarquia_completa: `03_post/${subPrincipal.jerarquia_completa}`, // ← LINUX FORMAT
            ruta_acceso: subPrincipal.ruta_acceso, // ← RUTA INDEXADA DEL BACKEND
            nivel: 1,
            es_padre: false,
            archivos: archivosFinalesNivel1,
            subdirectorios: subdirectoriosNivel2Optimizados,
            total_archivos: totalArchivosNivel1,
            subdirectorios_count: subdirectoriosNivel2Optimizados.length,
            pendientes: pendientesNivel1,
            evaluados: evaluadosNivel1,
            aprobados: aprobadosNivel1,
            fecha_disposicion: subPrincipal.fecha_disposicion,
            observaciones: subPrincipal.observaciones,
            mecanismo: mecanismoGrupo
          })
        })

        // 🔢 ORDENAR subdirectorios nivel 1 numéricamente
        ordenarPorNombreNumerico(subdirectoriosOptimizados)

        // ⭐ COMBINAR archivos del directorio padre
        const archivosDelPadre = new Map<number, EvaluacionArchivo>()

        const archivosEnSubdirectorios = new Set<number>()
        subdirectoriosOptimizados.forEach(sub => {
          sub.archivos.forEach(arch => archivosEnSubdirectorios.add(arch.id_evaluacion))
          sub.subdirectorios.forEach(sub2 => {
            sub2.archivos.forEach(arch => archivosEnSubdirectorios.add(arch.id_evaluacion))
            sub2.subdirectorios.forEach(sub3 => {
              sub3.archivos.forEach(arch => archivosEnSubdirectorios.add(arch.id_evaluacion))
              sub3.subdirectorios.forEach(sub4 => {
                sub4.archivos.forEach(arch => archivosEnSubdirectorios.add(arch.id_evaluacion))
                sub4.subdirectorios.forEach(sub5 => {
                  sub5.archivos.forEach(arch => archivosEnSubdirectorios.add(arch.id_evaluacion))
                })
              })
            })
          })
        })
        
        directoriosDelGrupo.forEach(dirReg => {
          const archivos = archivosPorDisposicion.get(dirReg.id_disposicion) || []
          console.log(`    📄 Directorio ${dirReg.id_disposicion} tiene ${archivos.length} archivos`)
          archivos.forEach(archivo => {
            if (!archivosEnSubdirectorios.has(archivo.id_evaluacion)) {
              archivosDelPadre.set(archivo.id_evaluacion, archivo)
            }
          })
        })
        
        const archivosDelPadreFinal = Array.from(archivosDelPadre.values())
        console.log(`    ✅ Total archivos nivel 0: ${archivosDelPadreFinal.length}`)
        
        // Calcular estadísticas totales
        let totalArchivos = archivosDelPadreFinal.length
        let pendientes = archivosDelPadreFinal.filter(a => a.estado_archivo === 'PENDIENTE').length
        let evaluados = archivosDelPadreFinal.filter(a => a.evaluado).length
        let aprobados = archivosDelPadreFinal.filter(a => a.aprobado).length
        
        subdirectoriosOptimizados.forEach(sub => {
          totalArchivos += sub.total_archivos
          pendientes += sub.pendientes
          evaluados += sub.evaluados
          aprobados += sub.aprobados
        })
        
        // ⭐⭐⭐ CAMBIO PRINCIPAL NIVEL 0: Usar forward slashes ⭐⭐⭐
        directoriosResultado.push({
          id_disposicion: directorioPadre.id_disposicion,
          nombre_directorio: nombreRaizReal,
          jerarquia_completa: `03_post/${nombreRaizReal}`, // ← LINUX FORMAT
          ruta_acceso: directorioPadre.ruta_acceso, // ← RUTA INDEXADA DEL BACKEND
          nivel: 0,
          es_padre: true,
          archivos: archivosDelPadreFinal,
          subdirectorios: subdirectoriosOptimizados,
          total_archivos: totalArchivos,
          subdirectorios_count: subdirectoriosOptimizados.length,
          pendientes,
          evaluados,
          aprobados,
          fecha_disposicion: directorioPadre.fecha_disposicion,
          observaciones: directorioPadre.observaciones,
          mecanismo: mecanismoGrupo
        })
        
        console.log(`✅ Directorio raíz completado: ${nombreRaizReal} (${totalArchivos} archivos totales, ${subdirectoriosOptimizados.length} subdirs)`)
      })
      
      console.log(`🎯 Árbol final construido: ${directoriosResultado.length} directorios raíz`)
      console.log(`📊 Total archivos distribuidos: ${directoriosResultado.reduce((sum, dir) => sum + dir.total_archivos, 0)}`)
      
      // 🔢 ORDENAR directorios raíz numéricamente
      return ordenarPorNombreNumerico(directoriosResultado)
    }
    
    // ============ FUNCIÓN PRINCIPAL DE CARGA ============
    
    const loadData = async () => {
      try {
        loading.value = true
        error.value = null
        accessDenied.value = false
        
        const municipioId = Number(route.params.id)
        if (!municipioId || isNaN(municipioId)) {
          error.value = 'ID de municipio inválido'
          return
        }
        
        console.log(`📊 Cargando datos para municipio ${municipioId}...`)
        
        // 1. Cargar información del municipio
        try {
          const municipio = await getMunicipioById(municipioId)
          municipioName.value = municipio?.nom_municipio || `Municipio ${municipioId}`
        } catch (err) {
          municipioName.value = `Municipio ${municipioId}`
        }
        
        // 2. Cargar calificaciones
        const calificacionesData = await getCalificaciones()
        calificaciones.value = calificacionesData
        
        // 3. Cargar datos completos
        const response = await api.get(`/postoperacion/evaluacion-datos/${municipioId}/`)
        
        const archivosData = response.archivos || []
        const directoriosDataFromAPI = response.directorios || []
        
        console.log(`📊 Archivos recibidos: ${archivosData.length}`)
        console.log(`📊 Directorios recibidos: ${directoriosDataFromAPI.length}`)
        
        evaluacionesArchivos.value = archivosData
        directoriosData.value = directoriosDataFromAPI
        
        // 4. Construir árbol optimizado con 6 niveles
        const arbolOptimizado = construirArbolOptimizado(directoriosDataFromAPI, archivosData)
        directoriosPadre.value = arbolOptimizado
        
        console.log('✅ Todos los datos cargados exitosamente')
        
      } catch (err: any) {
        console.error('❌ Error cargando datos:', err)
        
        if (err.response?.status === 403 && userPermissions.value.isProfesional) {
          accessDenied.value = true
        } else {
          error.value = 'Error al cargar los datos del municipio compruebe que tenga los Permisos Suficientes para acceder a la Informacion de este Municipio'
        }
      } finally {
        loading.value = false
      }
    }

    // ============ FUNCIONES DE INTERACCIÓN ============
    
    const toggleDirectorio = (id: number) => {
      directoriosExpandidos.value[id] = !directoriosExpandidos.value[id]
    }
    
    const toggleArchivos = (id: number) => {
      archivosExpandidos.value[id] = !archivosExpandidos.value[id]
    }

    const filtrarArchivos = (archivos: EvaluacionArchivo[]): EvaluacionArchivo[] => {
      if (!archivos || archivos.length === 0) {
        return []
      }

      let resultado = [...archivos]
      
      // Filtro por búsqueda
      if (searchTerm.value.trim()) {
        const search = searchTerm.value.toLowerCase()
        resultado = resultado.filter(archivo => 
          archivo.nombre_archivo.toLowerCase().includes(search)
        )
      }
      
      // Filtro por estado
      if (filtroEstado.value) {
        if (filtroEstado.value === 'EVALUADO') {
          resultado = resultado.filter(archivo => archivo.evaluado)
        } else if (filtroEstado.value === 'APROBADO') {
          resultado = resultado.filter(archivo => archivo.aprobado)
        } else {
          resultado = resultado.filter(archivo => archivo.estado_archivo === filtroEstado.value)
        }
      }
      
      // Filtro por mecanismo
      if (filtroMecanismo.value) {
        resultado = resultado.filter(archivo => {
          const mecanismo = extraerMecanismoDesdeRuta(archivo.ruta_completa)
          return mecanismo === filtroMecanismo.value
        })
      }
      
      return resultado
    }

    // ============ FUNCIONES UTILITARIAS ============
    
    const getFileIcon = (fileName: string): string => {
      const extension = fileName.split('.').pop()?.toLowerCase() || ''
      const icons: Record<string, string> = {
        pdf: 'picture_as_pdf',
        zip: 'archive', rar: 'archive', '7z': 'archive',
        gdb: 'storage',
        jpg: 'image', jpeg: 'image', png: 'image', gif: 'image',
        doc: 'description', docx: 'description',
        xls: 'table_chart', xlsx: 'table_chart'
      }
      return icons[extension] || 'insert_drive_file'
    }
    
    const getEstadoClass = (estado: string): string => {
      const classes: Record<string, string> = {
        'PENDIENTE': 'pendiente',
        'EVALUADO': 'evaluado',
        'APROBADO': 'aprobado'
      }
      return classes[estado] || 'pendiente'
    }
    
    const getCalificacionText = (evaluacionId: number | null): string => {
      if (!evaluacionId) return 'Sin calificar'
      const cal = calificaciones.value.find(c => c.id === evaluacionId)
      return cal ? `${cal.concepto} (${cal.valor})` : 'Calificación no encontrada'
    }

    // Extrae el nombre de usuario del email (ej: andres.osorio@igac.gov.co -> andres.osorio)
    const getUsuarioCalificador = (usuarioEvaluacion: string | null): string | null => {
      if (!usuarioEvaluacion) return null
      // Si contiene @, extraer la parte antes del @
      if (usuarioEvaluacion.includes('@')) {
        return usuarioEvaluacion.split('@')[0]
      }
      // Si no tiene @, devolver tal cual
      return usuarioEvaluacion
    }
    
    const formatDate = (dateStr: string | null): string => {
      if (!dateStr) return 'Sin fecha'
      try {
        return format(parseISO(dateStr), 'dd/MM/yyyy', { locale: es })
      } catch {
        return 'Fecha inválida'
      }
    }

    const formatDateTime = (dateStr: string | null): string => {
      if (!dateStr) return 'Sin fecha'
      try {
        return format(parseISO(dateStr), 'dd/MM/yyyy HH:mm', { locale: es })
      } catch {
        return 'Fecha inválida'
      }
    }

    const getAuditIcon = (accion: string): string => {
      const iconMap: Record<string, string> = {
        'UPLOAD': 'cloud_upload',
        'DOWNLOAD': 'cloud_download',
        'RENAME': 'edit',
        'DELETE': 'delete',
        'MOVE': 'drive_file_move',
        'COPY': 'content_copy',
        'MODIFY': 'create'
      }
      return iconMap[accion] || 'history'
    }

    // ============ FUNCIONES DE EVALUACIÓN ============
    
    const actualizarEvaluacion = async (archivo: EvaluacionArchivo) => {
      try {
        showNotification('Actualizando evaluación...', 'info')
        
        const response = await api.patch(`/postoperacion/evaluacion-actualizar/${archivo.id_evaluacion}/`, {
          evaluacion_archivo: archivo.evaluacion_archivo
        })
        
        if (response.evaluacion) {
          // Encontrar y actualizar el archivo en el array principal
          const index = evaluacionesArchivos.value.findIndex(a => a.id_evaluacion === archivo.id_evaluacion)
          if (index !== -1) {
            evaluacionesArchivos.value[index] = {
              ...evaluacionesArchivos.value[index],
              evaluacion_archivo: archivo.evaluacion_archivo,
              evaluado: response.evaluacion.evaluado,
              aprobado: response.evaluacion.aprobado,
              estado_archivo: response.evaluacion.estado_archivo,
              usuario_evaluacion: response.evaluacion.usuario_evaluacion,
              fecha_actualizacion: response.evaluacion.fecha_actualizacion
            }
          }
          
          // Reconstruir el árbol con los datos actualizados
          const arbolOptimizado = construirArbolOptimizado(directoriosData.value, evaluacionesArchivos.value)
          directoriosPadre.value = arbolOptimizado
          
          showNotification('Evaluación actualizada correctamente', 'success')
        }
        
      } catch (error: any) {
        console.error('Error actualizando evaluación:', error)
        showNotification(`Error al actualizar evaluación: ${error.response?.data?.error || error.message}`, 'error')
      }
    }


    // ============ FUNCIONES DE ARCHIVOS ============
    
    const downloadFile = async (archivo: EvaluacionArchivo) => {
      if (!archivo.ruta_completa) {
        showNotification('No hay ruta disponible para descargar este archivo', 'warning')
        return
      }
      
      try {
        showNotification('Iniciando descarga...', 'info')
        
        const response = await api.get('/preoperacion/ver_pdf/', {
          params: { ruta: archivo.ruta_completa },
          responseType: 'blob'
        })
        
        let blobData = response
        if (response && typeof response === 'object' && 'data' in response) {
          blobData = response.data
        }
        
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
        
      } catch (error: any) {
        console.error('Error al descargar archivo:', error)
        if (error.response?.status === 403) {
          showNotification('No tienes permisos para descargar este archivo', 'error')
        } else if (error.response?.status === 404) {
          showNotification('Archivo no encontrado', 'error')
        } else {
          showNotification(`Error al descargar archivo: ${error.response?.data?.detail || error.message}`, 'error')
        }
      }
    }
    
    const viewFile = async (archivo: EvaluacionArchivo) => {
      if (!archivo.ruta_completa) {
        showNotification('No hay ruta disponible para este archivo', 'warning')
        return
      }
      
      try {
        const fileExtension = archivo.nombre_archivo.split('.').pop()?.toLowerCase() || ''
        
        if (['gdb', 'zip', 'rar', '7z'].includes(fileExtension)) {
          await downloadFile(archivo)
        } else {
          showNotification('Abriendo archivo...', 'info')
          
          const response = await api.get('/preoperacion/ver_pdf/', {
            params: { ruta: archivo.ruta_completa },
            responseType: 'blob'
          })
          
          let blobData = response
          if (response && typeof response === 'object' && 'data' in response) {
            blobData = response.data
          }
          
          const blob = new Blob([blobData], { type: blobData.type || 'application/octet-stream' })
          const url = window.URL.createObjectURL(blob)
          
          window.open(url, '_blank')
          showNotification(`Abriendo: ${archivo.nombre_archivo}`, 'success')
          
          setTimeout(() => window.URL.revokeObjectURL(url), 10000)
        }
        
      } catch (error: any) {
        console.error('Error al visualizar archivo:', error)
        if (error.response?.status === 403) {
          showNotification('No tienes permisos para ver este archivo', 'error')
        } else if (error.response?.status === 404) {
          showNotification('Archivo no encontrado', 'error')
        } else {
          showNotification(`Error al abrir archivo: ${error.response?.data?.detail || error.message}`, 'error')
        }
      }
    }
    
    // Abrir modal de eliminación de archivo
    const deleteFile = (archivo: EvaluacionArchivo) => {
      // Verificar permisos usando canDeleteFile que ya considera:
      // - Admins/SuperAdmins pueden eliminar cualquier archivo
      // - Profesionales solo pueden eliminar archivos que ellos subieron desde la plataforma
      if (!canDeleteFile(archivo)) {
        if (userPermissions.value.isProfesional) {
          showNotification('Solo puedes eliminar archivos que tú hayas subido desde la plataforma', 'error')
        } else {
          showNotification('No tienes permisos para eliminar archivos', 'error')
        }
        return
      }
      archivoAEliminar.value = archivo
      showDeleteFileModal.value = true
    }

    // Cerrar modal de eliminación de archivo
    const closeDeleteFileModal = () => {
      if (!eliminandoArchivo.value) {
        showDeleteFileModal.value = false
        archivoAEliminar.value = null
      }
    }

    // Ejecutar la eliminación del archivo
    const executeDeleteFile = async (eliminarFisico: boolean) => {
      if (!archivoAEliminar.value) return

      eliminandoArchivo.value = true

      try {
        const mensaje = eliminarFisico ? 'Eliminando archivo completamente...' : 'Eliminando solo registro...'
        showNotification(mensaje, 'info')

        // Añadir parámetro eliminar_fisico si corresponde
        const url = eliminarFisico
          ? `/postoperacion/evaluacion-eliminar/${archivoAEliminar.value.id_evaluacion}/?eliminar_fisico=true`
          : `/postoperacion/evaluacion-eliminar/${archivoAEliminar.value.id_evaluacion}/`

        console.log('🗑️ URL de eliminación:', url)
        const response = await api.delete(url)
        console.log('🗑️ Respuesta del servidor:', response)

        // Cerrar el modal de eliminación
        showDeleteFileModal.value = false
        archivoAEliminar.value = null

        // Actualizar la lista de archivos
        evaluacionesArchivos.value = evaluacionesArchivos.value.filter(a => a.id_evaluacion !== archivoAEliminar.value?.id_evaluacion)
        await loadData()

        // Mostrar mensaje de éxito con detalles
        const detalles = response.detalles || {}
        let mensajeExito = response.message || 'Eliminación exitosa'
        if (eliminarFisico && detalles.archivo_fisico_eliminado === false) {
          mensajeExito += ' (archivo físico no encontrado en la NAS)'
        }
        showNotification(mensajeExito, 'success')
        closeFileInfoModal()

      } catch (error: any) {
        console.error('Error eliminando archivo:', error)

        if (error.response?.status === 403) {
          showNotification('No tienes permisos para eliminar este archivo', 'error')
        } else if (error.response?.status === 404) {
          showNotification('El archivo no fue encontrado', 'warning')
        } else {
          showNotification(`Error al eliminar: ${error.response?.data?.error || error.message}`, 'error')
        }
      } finally {
        eliminandoArchivo.value = false
      }
    }

    // Función específica para eliminar solo registro (desde modal de info)
    const deleteFileRecordOnly = (archivo: EvaluacionArchivo) => {
      archivoAEliminar.value = archivo
      executeDeleteFile(false)
    }

    // Función específica para eliminar registro + archivo físico (desde modal de info)
    const deleteFileComplete = (archivo: EvaluacionArchivo) => {
      archivoAEliminar.value = archivo
      executeDeleteFile(true)
    }

    // ============ FUNCIONES DE DIRECTORIOS ============
    
    const eliminarDirectorio = (directorio: DirectorioOptimizado) => {
      if (!userPermissions.value.isSuperAdmin && !userPermissions.value.isAdmin) {
        showNotification('Solo los Administradores pueden eliminar directorios', 'error')
        return
      }
      
      directorioAEliminar.value = directorio
      showDeleteModal.value = true
    }
    
    const confirmarEliminacion = async () => {
      if (!directorioAEliminar.value) return
      
      try {
        showNotification('Eliminando directorio...', 'info')
        
        const response = await api.delete(`/postoperacion/disposiciones/${directorioAEliminar.value.id_disposicion}/`)
        
        if (response === undefined || response === null || response === '') {
          showNotification('Directorio eliminado exitosamente', 'success')
        } else {
          showNotification(response.message || 'Directorio eliminado exitosamente', 'success')
        }
        
        await loadData()
        closeDeleteModal()
        
      } catch (error: any) {
        console.error('Error eliminando directorio:', error)
        
        if (error.response?.status === 403) {
          showNotification('No tienes permisos para eliminar este directorio', 'error')
        } else if (error.response?.status === 404) {
          showNotification('El directorio no fue encontrado', 'warning')
          await loadData()
          closeDeleteModal()
        } else {
          showNotification(`Error al eliminar directorio: ${error.response?.data?.error || error.message}`, 'error')
        }
      }
    }
    
    const closeDeleteModal = () => {
      showDeleteModal.value = false
      directorioAEliminar.value = null
    }

    // ============ FUNCIONES DE OBSERVACIONES ============
    


    // ============ FUNCIONES DE OBSERVACIONES ============
    
    const editObservaciones = (archivo: EvaluacionArchivo) => {
      editingFile.value = archivo
      observacionesForm.value = archivo.observaciones_evaluacion || ''
      showObservacionesModal.value = true
    }
        const saveObservaciones = async () => {
      if (!editingFile.value) return
      
      try {
        showNotification('Guardando observaciones...', 'info')
        
        const response = await api.patch(`/postoperacion/evaluacion-actualizar/${editingFile.value.id_evaluacion}/`, {
          observaciones_evaluacion: observacionesForm.value
        })
        
        // Actualizar archivo en la lista
        const index = evaluacionesArchivos.value.findIndex(a => a.id_evaluacion === editingFile.value!.id_evaluacion)
        if (index !== -1) {
          evaluacionesArchivos.value[index].observaciones_evaluacion = observacionesForm.value
        }
        
        // Actualizar archivo seleccionado si está abierto
        if (selectedFileInfo.value && selectedFileInfo.value.id_evaluacion === editingFile.value.id_evaluacion) {
          selectedFileInfo.value.observaciones_evaluacion = observacionesForm.value
        }
        
        showNotification('Observaciones guardadas exitosamente', 'success')
        closeObservacionesModal()
        
      } catch (error: any) {
        console.error('Error guardando observaciones:', error)
        showNotification(`Error al guardar observaciones: ${error.response?.data?.error || error.message}`, 'error')
      }
    }

    // ============ HANDLERS DE MODALES ============
    
    const showFileInfo = async (archivo: EvaluacionArchivo) => {
      selectedFileInfo.value = archivo
      showFileInfoModal.value = true

      // Cargar historial de auditoría
      fileAuditLoading.value = true
      fileAuditHistory.value = []
      fileAuditInfo.value = null

      try {
        const response = await fetch(`/postoperacion/historial_archivo/?ruta=${encodeURIComponent(archivo.ruta_completa)}`, {
          headers: {
            'Authorization': `Token ${authStore.token}`
          }
        })

        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            fileAuditHistory.value = data.historial || []
            fileAuditInfo.value = {
              subido_por_plataforma: data.subido_por_plataforma,
              info_subida: data.info_subida
            }
          }
        }
      } catch (error) {
        console.error('Error al cargar historial de auditoría:', error)
      } finally {
        fileAuditLoading.value = false
      }
    }

    const closeFileInfoModal = () => {
      showFileInfoModal.value = false
      selectedFileInfo.value = null
      fileAuditHistory.value = []
      fileAuditInfo.value = null
      editandoRuta.value = false
      rutaEditForm.value = ''
    }
    
    const closeObservacionesModal = () => {
      showObservacionesModal.value = false
      editingFile.value = null
      observacionesForm.value = ''
    }

    // ============ FUNCIONES DE NOTIFICACIONES ============
    
    const showNotification = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
      if (notification.value.timeout) {
        clearTimeout(notification.value.timeout)
      }
      
      const icons = {
        success: 'check_circle',
        error: 'error',
        warning: 'warning',
        info: 'info'
      }
      
      notification.value = {
        show: true,
        message,
        type,
        icon: icons[type],
        timeout: null
      }
      
      notification.value.timeout = window.setTimeout(() => {
        closeNotification()
      }, 5000)
    }
    
    const closeNotification = () => {
      if (notification.value.timeout) {
        clearTimeout(notification.value.timeout)
      }
      notification.value.show = false
    }

    // ============ FUNCIONES DE FILTROS ============
    
    const limpiarFiltros = () => {
      searchTerm.value = ''
      filtroEstado.value = ''
      filtroMecanismo.value = ''
    }
    
    const clearSearch = () => {
      searchTerm.value = ''
    }
    
    const aplicarFiltros = () => {
      // Los filtros se aplican automáticamente a través de computed properties
      console.log('🔍 Aplicando filtros:', {
        busqueda: searchTerm.value,
        estado: filtroEstado.value,
        mecanismo: filtroMecanismo.value
      })
    }

    // ============ FUNCIONES DE NAVEGACIÓN ============
    
    const goBack = () => {
      router.back()
    }
    
    const refreshData = async () => {
      await loadData()
      showNotification('Datos actualizados correctamente', 'success')
    }
    
    const reloadData = async () => {
      await loadData()
    }

    // ============ SUBIDA DE ARCHIVOS ============

    // Obtener ruta base del municipio: 01_actualiz_catas/{depto}/{muni}/{mecanismo}/
    const getMunicipioBasePath = (): string => {
      const municipioId = Number(route.params.id)
      if (!municipioId || isNaN(municipioId)) return ''

      // Extraer departamento y municipio del código
      // Ejemplo: 41013 -> depto=41, muni=013
      const municipioStr = municipioId.toString().padStart(5, '0')
      const depto = municipioStr.substring(0, 2)
      const muni = municipioStr.substring(2, 5)

      // Obtener mecanismo: usar el filtro actual, o IGAC por defecto, o extraer de un archivo existente
      let mecanismo = filtroMecanismo.value || ''

      // Si no hay filtro de mecanismo, intentar obtenerlo de los archivos existentes
      if (!mecanismo && evaluacionesArchivos.value.length > 0) {
        const primerArchivo = evaluacionesArchivos.value[0]
        mecanismo = extraerMecanismoDesdeRuta(primerArchivo.ruta_completa)
      }

      // Si aún no tenemos mecanismo, usar IGAC por defecto
      if (!mecanismo || mecanismo === 'SIN_MECANISMO' || mecanismo === 'ERROR_MECANISMO') {
        mecanismo = 'IGAC'
      }

      return `01_actualiz_catas/${depto}/${muni}/${mecanismo}`
    }

    const openUploadModal = (directorio?: DirectorioOptimizado) => {
      if (!canUpload.value) {
        showNotification('No tienes permisos para subir archivos', 'error')
        return
      }

      // ✅ USAR LA RUTA INDEXADA DEL BACKEND - NO CONSTRUIR MANUALMENTE
      // La ruta_acceso viene del DisposicionPost indexado, ejemplo:
      // \\repositorio\DirGesCat\2510SP\H_Informacion_Consulta\Sub_Proy\01_actualiz_catas\17\013\PGN\03_post\01_aprob_econo

      if (directorio && directorio.ruta_acceso) {
        // Extraer la ruta relativa después de Sub_Proy
        const rutaCompleta = directorio.ruta_acceso.replace(/\\/g, '/') // Normalizar a forward slashes
        const subProyIndex = rutaCompleta.toLowerCase().indexOf('sub_proy/')

        if (subProyIndex !== -1) {
          // Extraer solo la parte después de "Sub_Proy/"
          currentUploadPath.value = rutaCompleta.substring(subProyIndex + 9) // 9 = length of "Sub_Proy/"
        } else {
          // Si no encuentra Sub_Proy, usar la ruta como está
          currentUploadPath.value = rutaCompleta
        }

        console.log('📤 Upload path INDEXADO:', currentUploadPath.value)
        console.log('📤 Ruta original del backend:', directorio.ruta_acceso)
      } else {
        // Sin directorio específico, usar getMunicipioBasePath como fallback
        const rutaBaseMunicipio = getMunicipioBasePath()
        currentUploadPath.value = rutaBaseMunicipio ? `${rutaBaseMunicipio}/03_post` : '03_post'
        console.log('📤 Upload path fallback (sin directorio):', currentUploadPath.value)
      }

      // Recolectar nombres de archivos existentes en el directorio destino
      if (directorio && directorio.archivos) {
        existingFileNames.value = directorio.archivos.map(a => a.nombre_archivo)
      } else {
        existingFileNames.value = []
      }

      showUploadModal.value = true
    }

    const closeUploadModal = () => {
      showUploadModal.value = false
      currentUploadPath.value = ''
      pendingUploadFiles.value = [] // Limpiar archivos del drag & drop
      existingFileNames.value = [] // Limpiar lista de archivos existentes
    }

    const handleUploadComplete = async () => {
      showNotification('Archivos subidos correctamente', 'success')
      pendingUploadFiles.value = [] // Limpiar archivos pendientes
      // Recargar datos para ver los nuevos archivos
      await loadData()
    }

    // ============ DRAG & DROP DIRECTO A DIRECTORIOS ============

    const handleDirectorioDragEnter = (event: DragEvent, directorio: DirectorioOptimizado) => {
      event.preventDefault()
      event.stopPropagation()
      if (!canUpload.value) return

      // Verificar que hay archivos siendo arrastrados
      if (event.dataTransfer?.types.includes('Files')) {
        dropTargetDirectorioId.value = directorio.id_disposicion
        console.log('📂 Drag enter en directorio:', directorio.nombre_directorio)
      }
    }

    const handleDirectorioDragOver = (event: DragEvent, directorio: DirectorioOptimizado) => {
      event.preventDefault()
      event.stopPropagation()
      if (!canUpload.value) return

      // Mantener el indicador visual
      if (event.dataTransfer?.types.includes('Files')) {
        dropTargetDirectorioId.value = directorio.id_disposicion
        // Indicar que se puede soltar
        if (event.dataTransfer) {
          event.dataTransfer.dropEffect = 'copy'
        }
      }
    }

    const handleDirectorioDragLeave = (event: DragEvent, directorio: DirectorioOptimizado) => {
      event.preventDefault()
      event.stopPropagation()

      // Solo limpiar si realmente salimos del directorio (no de un hijo)
      const relatedTarget = event.relatedTarget as HTMLElement
      const currentTarget = event.currentTarget as HTMLElement

      if (!currentTarget.contains(relatedTarget)) {
        if (dropTargetDirectorioId.value === directorio.id_disposicion) {
          dropTargetDirectorioId.value = null
          console.log('📂 Drag leave de directorio:', directorio.nombre_directorio)
        }
      }
    }

    const handleDirectorioDrop = (event: DragEvent, directorio: DirectorioOptimizado) => {
      event.preventDefault()
      event.stopPropagation()

      if (!canUpload.value) {
        showNotification('No tienes permisos para subir archivos', 'error')
        dropTargetDirectorioId.value = null
        return
      }

      const files = event.dataTransfer?.files
      if (!files || files.length === 0) {
        dropTargetDirectorioId.value = null
        return
      }

      console.log('📂 Drop en directorio:', directorio.nombre_directorio)
      console.log('📂 Archivos soltados:', files.length)

      // Guardar archivos para pasarlos al modal
      pendingUploadFiles.value = Array.from(files)

      // Abrir modal con la ruta del directorio
      openUploadModal(directorio)

      // Limpiar indicador visual
      dropTargetDirectorioId.value = null
    }

    // Verificar si un directorio es el target de drop actual
    const isDropTarget = (directorioId: number): boolean => {
      return dropTargetDirectorioId.value === directorioId
    }

    // ============ MANEJO DE ERRORES API ============
    
    const handleApiError = (error: any, funcionName: string) => {
      console.error(`Error en ${funcionName}:`, error)
      
      if (error.response?.status === 401 || error.response?.status === 403) {
        const errorMessage = error.response?.data?.detail || error.response?.data?.message || ''
        
        if (userPermissions.value.isProfesional && !userPermissions.value.isAnyAdmin) {
          console.warn(`⚠️ Profesional sin acceso a ${funcionName}`)
          accessDenied.value = true
          return []
        }
        
        if (errorMessage.includes('Invalid token') || 
            errorMessage.includes('Token has expired') ||
            errorMessage.includes('Authentication credentials were not provided')) {
          authStore.logout()
          router.push('/login')
        }
      }
      
      return []
    }

    // ============ VERIFICACIONES DE PERMISOS ============
    
    const verificarPermisosEliminacion = (tipo: 'directorio' | 'archivo'): { allowed: boolean; message: string } => {
      if (!userPermissions.value.isSuperAdmin && !userPermissions.value.isAdmin) {
        return {
          allowed: false,
          message: `Solo los Administradores pueden eliminar ${tipo}s. Tu rol actual es: ${accessLevelText.value}`
        }
      }

      return {
        allowed: true,
        message: 'Permisos verificados correctamente'
      }
    }

    // ============ FUNCIONES DE CALIFICACIÓN MASIVA ============

    const toggleModoCalificacionMasiva = () => {
      if (!canUseMassQualification.value) {
        showNotification('Solo los Super Administradores pueden usar la calificación masiva', 'error')
        return
      }
      modoCalificacionMasiva.value = !modoCalificacionMasiva.value
      if (!modoCalificacionMasiva.value) {
        // Limpiar selecciones al desactivar
        archivosSeleccionados.value.clear()
        calificacionMasivaSeleccionada.value = null
      } else {
        // Cargar información del último lote al activar
        cargarUltimoLoteMasivo()
      }
    }

    const toggleArchivoSeleccion = (archivoId: number) => {
      if (archivosSeleccionados.value.has(archivoId)) {
        archivosSeleccionados.value.delete(archivoId)
      } else {
        archivosSeleccionados.value.add(archivoId)
      }
      // Forzar reactividad
      archivosSeleccionados.value = new Set(archivosSeleccionados.value)
    }

    const isArchivoSeleccionado = (archivoId: number): boolean => {
      return archivosSeleccionados.value.has(archivoId)
    }

    const toggleDirectorioSeleccion = (directorio: DirectorioOptimizado, seleccionar: boolean) => {
      // Función recursiva para obtener todos los IDs de archivos en un directorio y sus subdirectorios
      const obtenerArchivosRecursivo = (dir: DirectorioOptimizado): number[] => {
        let ids: number[] = []

        // Agregar archivos del directorio actual
        if (dir.archivos && dir.archivos.length > 0) {
          dir.archivos.forEach(archivo => {
            ids.push(archivo.id_evaluacion)
          })
        }

        // Agregar archivos de subdirectorios recursivamente
        if (dir.subdirectorios && dir.subdirectorios.length > 0) {
          dir.subdirectorios.forEach(subdir => {
            ids = [...ids, ...obtenerArchivosRecursivo(subdir)]
          })
        }

        return ids
      }

      const archivosIds = obtenerArchivosRecursivo(directorio)
      console.log(`[Masivo] Directorio ${directorio.nombre_directorio}: ${archivosIds.length} archivos encontrados`)

      if (seleccionar) {
        archivosIds.forEach(id => archivosSeleccionados.value.add(id))
      } else {
        archivosIds.forEach(id => archivosSeleccionados.value.delete(id))
      }
      // Forzar reactividad
      archivosSeleccionados.value = new Set(archivosSeleccionados.value)
      console.log(`[Masivo] Total seleccionados: ${archivosSeleccionados.value.size}`)
    }

    const isDirectorioSeleccionado = (directorio: DirectorioOptimizado): boolean => {
      // Verificar si todos los archivos del directorio están seleccionados
      const obtenerArchivosRecursivo = (dir: DirectorioOptimizado): number[] => {
        let ids: number[] = []
        if (dir.archivos && dir.archivos.length > 0) {
          dir.archivos.forEach(archivo => {
            ids.push(archivo.id_evaluacion)
          })
        }
        if (dir.subdirectorios && dir.subdirectorios.length > 0) {
          dir.subdirectorios.forEach(subdir => {
            ids = [...ids, ...obtenerArchivosRecursivo(subdir)]
          })
        }
        return ids
      }

      const archivosIds = obtenerArchivosRecursivo(directorio)
      if (archivosIds.length === 0) return false
      return archivosIds.every(id => archivosSeleccionados.value.has(id))
    }

    const isDirectorioParcialmenteSeleccionado = (directorio: DirectorioOptimizado): boolean => {
      const obtenerArchivosRecursivo = (dir: DirectorioOptimizado): number[] => {
        let ids: number[] = []
        if (dir.archivos && dir.archivos.length > 0) {
          dir.archivos.forEach(archivo => {
            ids.push(archivo.id_evaluacion)
          })
        }
        if (dir.subdirectorios && dir.subdirectorios.length > 0) {
          dir.subdirectorios.forEach(subdir => {
            ids = [...ids, ...obtenerArchivosRecursivo(subdir)]
          })
        }
        return ids
      }

      const archivosIds = obtenerArchivosRecursivo(directorio)
      if (archivosIds.length === 0) return false
      const seleccionados = archivosIds.filter(id => archivosSeleccionados.value.has(id))
      return seleccionados.length > 0 && seleccionados.length < archivosIds.length
    }

    const seleccionarTodos = () => {
      archivosParaCalificar.value.forEach(archivo => {
        archivosSeleccionados.value.add(archivo.id_evaluacion)
      })
      archivosSeleccionados.value = new Set(archivosSeleccionados.value)
    }

    const deseleccionarTodos = () => {
      archivosSeleccionados.value.clear()
      archivosSeleccionados.value = new Set(archivosSeleccionados.value)
    }

    const cargarUltimoLoteMasivo = async () => {
      try {
        const municipioId = route.params.id
        const response = await api.get(`/postoperacion/evaluacion-archivos/ultimo_lote_masivo/?municipio_id=${municipioId}`)
        // El interceptor de axios puede devolver response.data directamente
        const data = response.data || response
        console.log('[UltimoLote] Respuesta:', data)
        ultimoLoteMasivo.value = data
      } catch (error) {
        console.error('Error cargando último lote masivo:', error)
        ultimoLoteMasivo.value = null
      }
    }

    const mostrarConfirmacionMasiva = () => {
      if (archivosSeleccionadosCount.value === 0) {
        showNotification('Debe seleccionar al menos un archivo', 'warning')
        return
      }
      if (!calificacionMasivaSeleccionada.value) {
        showNotification('Debe seleccionar una calificación a aplicar', 'warning')
        return
      }
      showConfirmacionMasiva.value = true
    }

    const aplicarCalificacionMasiva = async () => {
      if (!canUseMassQualification.value) {
        showNotification('Solo los Super Administradores pueden realizar calificaciones masivas', 'error')
        return
      }

      if (archivosSeleccionadosCount.value === 0) {
        showNotification('Debe seleccionar al menos un archivo', 'warning')
        return
      }

      if (!calificacionMasivaSeleccionada.value) {
        showNotification('Debe seleccionar una calificación a aplicar', 'warning')
        return
      }

      aplicandoCalificacion.value = true
      showConfirmacionMasiva.value = false

      try {
        console.log('[Masivo] Enviando:', {
          archivos_ids: Array.from(archivosSeleccionados.value),
          calificacion_id: calificacionMasivaSeleccionada.value,
          filtro: filtroMasivo.value
        })

        const response = await api.post('/postoperacion/evaluacion-archivos/calificacion_masiva/', {
          archivos_ids: Array.from(archivosSeleccionados.value),
          calificacion_id: calificacionMasivaSeleccionada.value,
          filtro: filtroMasivo.value,
          observaciones: 'Calificación masiva desde ProductosDetalle'
        })

        console.log('[Masivo] Respuesta completa:', response)

        // La respuesta puede venir como response.data o directamente como response
        // dependiendo de la configuración del interceptor de axios
        const data = response.data || response
        console.log('[Masivo] Data:', data)

        // Validar que tengamos datos válidos
        if (!data || typeof data !== 'object') {
          throw new Error('Respuesta inválida del servidor')
        }

        // Mostrar mensaje detallado del servidor
        let notificationType: 'success' | 'warning' | 'info' = 'success'

        if (data.archivos_calificados === 0) {
          notificationType = 'warning'
        }

        const mensaje = data.message || `${data.archivos_calificados || 0} archivos calificados`
        showNotification(mensaje, notificationType)

        // Log detallado en consola para debug
        console.log('[Masivo] Resultado:', {
          calificados: data.archivos_calificados,
          ignorados_filtro: data.archivos_ignorados_por_filtro,
          misma_calificacion: data.archivos_ya_tenian_misma_calificacion,
          total: data.total_seleccionados,
          lote: data.lote_id
        })

        // Limpiar selecciones y recargar datos
        archivosSeleccionados.value.clear()
        calificacionMasivaSeleccionada.value = null
        await loadData()
        await cargarUltimoLoteMasivo()

      } catch (error: any) {
        console.error('Error en calificación masiva:', error)
        console.error('Error response:', error.response)
        console.error('Error data:', error.response?.data)
        showNotification(
          error.response?.data?.error || error.message || 'Error al aplicar calificación masiva',
          'error'
        )
      } finally {
        aplicandoCalificacion.value = false
      }
    }

    const restaurarCalificacionAnterior = async () => {
      if (!ultimoLoteMasivo.value?.lote_id) {
        showNotification('No hay un lote de calificación masiva para restaurar', 'warning')
        return
      }

      if (!confirm(`¿Está seguro de restaurar las calificaciones del lote ${ultimoLoteMasivo.value.lote_id}?\n\nEsto afectará ${ultimoLoteMasivo.value.archivos_en_lote} archivos.`)) {
        return
      }

      aplicandoCalificacion.value = true

      try {
        const response = await api.post('/postoperacion/evaluacion-archivos/restaurar_calificacion/', {
          lote_id: ultimoLoteMasivo.value.lote_id
        })

        // El interceptor de axios puede devolver response.data directamente
        const data = response.data || response
        console.log('[Restaurar] Respuesta:', data)

        showNotification(
          `✅ ${data.archivos_restaurados} archivos restaurados`,
          'success'
        )

        // Recargar datos
        await loadData()
        await cargarUltimoLoteMasivo()

      } catch (error: any) {
        console.error('Error restaurando calificaciones:', error)
        showNotification(
          error.response?.data?.error || error.error || 'Error al restaurar calificaciones',
          'error'
        )
      } finally {
        aplicandoCalificacion.value = false
      }
    }

    // ============ DEPURACIÓN UNIFICADA DE ARCHIVOS Y DIRECTORIOS ============

    // Computed: hay elementos inexistentes?
    const hayInexistentes = computed(() => {
      return (resultadoVerificacion.value?.archivos_inexistentes || 0) > 0 ||
             (resultadoVerificacionDirs.value?.directorios_inexistentes || 0) > 0
    })

    // Computed: total de elementos seleccionados para depurar
    const totalSeleccionadosDepuracion = computed(() => {
      return archivosADepurarSeleccionados.value.size + directoriosADepurarSeleccionados.value.size
    })

    // Función UNIFICADA de verificación (llama ambos endpoints en paralelo)
    const verificarInexistentes = async () => {
      if (!canUseMassQualification.value) {
        showNotification('Solo los Super Administradores pueden usar esta función', 'error')
        return
      }

      verificandoInexistentes.value = true
      showNotification('Verificando existencia de archivos y directorios... Esto puede tomar un momento.', 'info')

      try {
        const municipioId = route.params.id

        // Llamar ambos endpoints en paralelo
        const [archivosResponse, directoriosResponse] = await Promise.all([
          api.get(`/postoperacion/evaluacion-archivos/verificar_archivos_inexistentes/?municipio_id=${municipioId}`),
          api.get(`/postoperacion/evaluacion-archivos/verificar_directorios_inexistentes/?municipio_id=${municipioId}`)
        ])

        // Manejar interceptor axios
        const dataArchivos = archivosResponse.data || archivosResponse
        const dataDirs = directoriosResponse.data || directoriosResponse

        console.log('[Verificación Archivos] Respuesta:', dataArchivos)
        console.log('[Verificación Dirs] Respuesta:', dataDirs)

        resultadoVerificacion.value = dataArchivos
        resultadoVerificacionDirs.value = dataDirs
        showModalDepuracion.value = true

        // Seleccionar todos por defecto
        if (dataArchivos.lista_inexistentes?.length > 0) {
          archivosADepurarSeleccionados.value = new Set(dataArchivos.lista_inexistentes.map((a: any) => a.id))
        }
        if (dataDirs.lista_inexistentes?.length > 0) {
          directoriosADepurarSeleccionados.value = new Set(dataDirs.lista_inexistentes.map((d: any) => d.id))
        }

        const totalInexistentes = (dataArchivos.archivos_inexistentes || 0) + (dataDirs.directorios_inexistentes || 0)
        if (totalInexistentes === 0) {
          showNotification('¡Todos los elementos existen! No hay nada que depurar.', 'success')
        } else {
          showNotification(
            `Se encontraron ${dataDirs.directorios_inexistentes || 0} directorios y ${dataArchivos.archivos_inexistentes || 0} archivos inexistentes`,
            'warning'
          )
        }

      } catch (error: any) {
        console.error('Error verificando elementos:', error)
        showNotification(
          error.response?.data?.error || error.error || 'Error al verificar elementos inexistentes',
          'error'
        )
      } finally {
        verificandoInexistentes.value = false
      }
    }

    const cerrarModalDepuracion = () => {
      showModalDepuracion.value = false
      showConfirmacionDepuracion.value = false
      resultadoVerificacion.value = null
      resultadoVerificacionDirs.value = null
      archivosADepurarSeleccionados.value = new Set()
      directoriosADepurarSeleccionados.value = new Set()
    }

    // Funciones para manejo de checkboxes de ARCHIVOS
    const toggleArchivoDepuracion = (id: number) => {
      const newSet = new Set(archivosADepurarSeleccionados.value)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      archivosADepurarSeleccionados.value = newSet
    }

    const seleccionarTodosDepuracion = () => {
      if (!resultadoVerificacion.value?.lista_inexistentes) return
      const allIds = resultadoVerificacion.value.lista_inexistentes.map((a: any) => a.id)
      archivosADepurarSeleccionados.value = new Set(allIds)
    }

    const deseleccionarTodosDepuracion = () => {
      archivosADepurarSeleccionados.value = new Set()
    }

    // Funciones para manejo de checkboxes de DIRECTORIOS
    const toggleDirectorioDepuracion = (id: number) => {
      const newSet = new Set(directoriosADepurarSeleccionados.value)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      directoriosADepurarSeleccionados.value = newSet
    }

    const seleccionarTodosDepuracionDirs = () => {
      if (!resultadoVerificacionDirs.value?.lista_inexistentes) return
      const allIds = resultadoVerificacionDirs.value.lista_inexistentes.map((d: any) => d.id)
      directoriosADepurarSeleccionados.value = new Set(allIds)
    }

    const deseleccionarTodosDepuracionDirs = () => {
      directoriosADepurarSeleccionados.value = new Set()
    }

    const mostrarConfirmacionDepuracion = () => {
      if (totalSeleccionadosDepuracion.value === 0) {
        showNotification('Seleccione al menos un elemento para eliminar', 'warning')
        return
      }
      showConfirmacionDepuracion.value = true
    }

    // Computed para calcular total de archivos en directorios seleccionados
    const totalArchivosEnDirSeleccionados = computed(() => {
      if (!resultadoVerificacionDirs.value?.lista_inexistentes) return 0
      return resultadoVerificacionDirs.value.lista_inexistentes
        .filter(d => directoriosADepurarSeleccionados.value.has(d.id))
        .reduce((total, d) => total + (d.total_archivos || 0), 0)
    })

    // Función UNIFICADA de ejecución (elimina archivos Y directorios en paralelo)
    const ejecutarDepuracionUnificada = async () => {
      if (totalSeleccionadosDepuracion.value === 0) {
        showNotification('No hay elementos seleccionados para depurar', 'warning')
        return
      }

      depurandoInexistentes.value = true
      showConfirmacionDepuracion.value = false

      try {
        const municipioId = route.params.id
        const promises: Promise<any>[] = []
        let archivosEliminados = 0
        let directoriosEliminados = 0
        let archivosEnCascada = 0

        // Eliminar directorios primero (si hay seleccionados)
        if (directoriosADepurarSeleccionados.value.size > 0) {
          const directorioIds = Array.from(directoriosADepurarSeleccionados.value)
          promises.push(
            api.post('/postoperacion/evaluacion-archivos/depurar_directorios_inexistentes/', {
              municipio_id: municipioId,
              directorio_ids: directorioIds,
              confirmar: true
            }).then(response => {
              const data = response.data || response
              directoriosEliminados = data.directorios_eliminados || 0
              archivosEnCascada = data.archivos_eliminados || 0
              return data
            })
          )
        }

        // Eliminar archivos (si hay seleccionados)
        if (archivosADepurarSeleccionados.value.size > 0) {
          const archivoIds = Array.from(archivosADepurarSeleccionados.value)
          promises.push(
            api.post('/postoperacion/evaluacion-archivos/depurar_archivos_inexistentes/', {
              municipio_id: municipioId,
              archivo_ids: archivoIds,
              confirmar: true
            }).then(response => {
              const data = response.data || response
              archivosEliminados = data.archivos_eliminados || 0
              return data
            })
          )
        }

        await Promise.all(promises)

        // Construir mensaje de éxito
        const mensajes: string[] = []
        if (directoriosEliminados > 0) {
          mensajes.push(`${directoriosEliminados} directorios`)
        }
        if (archivosEnCascada > 0) {
          mensajes.push(`${archivosEnCascada} archivos en cascada`)
        }
        if (archivosEliminados > 0) {
          mensajes.push(`${archivosEliminados} archivos`)
        }

        showNotification(`✅ Eliminados: ${mensajes.join(', ')}`, 'success')
        console.log('[Depuración Unificada] Completada:', { directoriosEliminados, archivosEnCascada, archivosEliminados })

        // Cerrar modal y recargar datos
        cerrarModalDepuracion()
        await loadData()

      } catch (error: any) {
        console.error('Error depurando elementos:', error)
        showNotification(
          error.response?.data?.error || error.error || 'Error al depurar elementos',
          'error'
        )
      } finally {
        depurandoInexistentes.value = false
      }
    }

    // ============ WATCHERS Y LIFECYCLE ============
    
    onMounted(async () => {
      console.log('🚀 ProductosDetalle montado - iniciando carga de datos')

      // Leer mecanismo de la URL si viene como query param
      const mecanismoFromUrl = route.query.mecanismo as string | undefined
      if (mecanismoFromUrl) {
        filtroMecanismo.value = mecanismoFromUrl
        console.log(`📂 Mecanismo pre-seleccionado desde URL: ${mecanismoFromUrl}`)
      }

      await loadData()
    })

    // ============ RETURN DEL SETUP ============
    
    return {
      // Estado reactivo
      loading,
      error,
      municipioName,
      accessDenied,
      
      // Datos principales
      evaluacionesArchivos,
      calificaciones,
      directoriosPadre,
      directoriosData,
      
      // Estados de UI
      directoriosExpandidos,
      archivosExpandidos,
      
      // Filtros
      searchTerm,
      filtroEstado,
      filtroMecanismo,
      
      // Modales
      showFileInfoModal,
      selectedFileInfo,
      fileAuditHistory,
      fileAuditLoading,
      fileAuditInfo,
      showObservacionesModal,
      editingFile,
      observacionesForm,
      showDeleteModal,
      directorioAEliminar,

      // Modal de eliminación de archivos
      showDeleteFileModal,
      archivoAEliminar,
      eliminandoArchivo,
      closeDeleteFileModal,
      executeDeleteFile,

      // Notificaciones
      notification,
      
      // Computed properties
      userPermissions,
      isProfesionalSinAcceso,
      tieneAccesoADatos,
      canEdit,
      canDelete,
      canDeleteFile,
      canDownload,
      accessLevelText,
      accessLevelIcon,
      accessLevelClass,
      estadisticas,
      mecanismosDisponibles,
      tienesFiltrosActivos,
      directoriosFiltrados,
      estadisticasFiltradas,
      
      // Funciones principales
      loadData,
      construirArbolOptimizado,
      
      // Funciones de interacción
      toggleDirectorio,
      toggleArchivos,
      
      // Funciones de filtros
      extraerMecanismoDesdeRuta,
      getCountMecanismo,
      limpiarFiltros,
      clearSearch,
      aplicarFiltros,
      filtrarArchivos,
      
      // Función para evitar duplicación
      tieneArchivosEnSubdirectoriosProfundos,
      
      // Funciones utilitarias
      getFileIcon,
      getEstadoClass,
      getCalificacionText,
      getUsuarioCalificador,
      formatDate,
      formatDateTime,
      getAuditIcon,

      // Funciones de evaluación
      actualizarEvaluacion,
      
      // Funciones de archivos
      downloadFile,
      viewFile,
      deleteFile,
      deleteFileRecordOnly,
      deleteFileComplete,

      // Funciones de directorios
      eliminarDirectorio,
      confirmarEliminacion,
      closeDeleteModal,
      
      // Funciones de observaciones
      editObservaciones,
      saveObservaciones,
      
      // Handlers de modales
      showFileInfo,
      closeFileInfoModal,
      closeObservacionesModal,
      
      // Funciones de notificaciones
      showNotification,
      closeNotification,
      
      // Funciones de navegación
      goBack,
      refreshData,
      reloadData,
      
      // Funciones de permisos
      verificarPermisosEliminacion,
      handleApiError,
      iniciarEdicionRuta,
      cancelarEdicionRuta,
      guardarRuta,
      editandoRuta,
      rutaEditForm,

      // Utilidades de rutas
      linuxToWindowsPath,

      // ============ SUBIDA DE ARCHIVOS ============
      canUpload,
      showUploadModal,
      currentUploadPath,
      pendingUploadFiles,
      existingFileNames,
      openUploadModal,
      closeUploadModal,
      handleUploadComplete,

      // ============ DRAG & DROP A DIRECTORIOS ============
      dropTargetDirectorioId,
      handleDirectorioDragEnter,
      handleDirectorioDragOver,
      handleDirectorioDragLeave,
      handleDirectorioDrop,
      isDropTarget,

      // ============ CALIFICACIÓN MASIVA ============
      modoCalificacionMasiva,
      archivosSeleccionados,
      filtroMasivo,
      calificacionMasivaSeleccionada,
      aplicandoCalificacion,
      ultimoLoteMasivo,
      showConfirmacionMasiva,
      canUseMassQualification,
      archivosSeleccionadosCount,
      archivosParaCalificar,
      archivosFiltradosPorMasivo,
      archivosSeleccionadosParaCalificar,
      todosSeleccionados,
      toggleModoCalificacionMasiva,
      toggleArchivoSeleccion,
      isArchivoSeleccionado,
      toggleDirectorioSeleccion,
      isDirectorioSeleccionado,
      isDirectorioParcialmenteSeleccionado,
      seleccionarTodos,
      deseleccionarTodos,
      mostrarConfirmacionMasiva,
      aplicarCalificacionMasiva,
      restaurarCalificacionAnterior,

      // ============ DEPURACIÓN UNIFICADA DE ARCHIVOS Y DIRECTORIOS ============
      verificandoInexistentes,
      depurandoInexistentes,
      showModalDepuracion,
      showConfirmacionDepuracion,
      resultadoVerificacion,
      resultadoVerificacionDirs,
      archivosADepurarSeleccionados,
      directoriosADepurarSeleccionados,

      // Computeds de depuración
      hayInexistentes,
      totalSeleccionadosDepuracion,
      totalArchivosEnDirSeleccionados,

      // Funciones de depuración
      verificarInexistentes,
      cerrarModalDepuracion,
      ejecutarDepuracionUnificada,
      toggleArchivoDepuracion,
      toggleDirectorioDepuracion,
      seleccionarTodosDepuracion,
      deseleccionarTodosDepuracion,
      seleccionarTodosDepuracionDirs,
      deseleccionarTodosDepuracionDirs,
      mostrarConfirmacionDepuracion,
    }
  }
})
</script>


<style scoped>
/* ============ VARIABLES CSS OPTIMIZADAS ============ */
:root {
  --color-primary: #2563eb;
  --color-primary-light: #3b82f6;
  --color-primary-dark: #1d4ed8;
  --color-success: #10b981;
  --color-success-light: #34d399;
  --color-warning: #f59e0b;
  --color-danger: #ef4444;
  --color-info: #06b6d4;
  --color-light: #f1f5f9;
  --color-dark: #1e293b;
  --color-gray: #64748b;
  --color-gray-light: #94a3b8;
  --color-white: #ffffff;
  --color-aquamarine: #20b2aa;
  --color-aquamarine-light: #5eead4;
  --color-aquamarine-bg: #f0fdfa;
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  --border-radius: 8px;
  --transition: all 0.2s ease;
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* ============ BASE STYLES ============ */
* {
  box-sizing: border-box;
}

.productos-detalle-page {
  min-height: 100vh;
  font-family: var(--font-family);
  color: var(--color-dark);
  background-color: var(--color-light);
  line-height: 1.5;
}

/* ============ HEADER ============ */
.page-header {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: var(--color-white);
  padding: 1.5rem 2rem;
  box-shadow: var(--shadow-lg);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1500px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.15);
  color: var(--color-white);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  cursor: pointer;
  font-weight: 600;
  transition: var(--transition);
  backdrop-filter: blur(8px);
  width: fit-content;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}

.header-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-info h1 {
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
}

.access-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  border-radius: 50px;
  font-weight: 600;
  font-size: 0.9rem;
  backdrop-filter: blur(8px);
  background: rgba(255, 255, 255, 0.15);
}

.access-badge.super-admin { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.access-badge.admin { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.access-badge.profesional { background: linear-gradient(135deg, #10b981, #059669); }
.access-badge.readonly { background: linear-gradient(135deg, #64748b, #475569); }

/* ============ ACCESS DENIED ============ */
.access-denied-container {
  max-width: 600px;
  margin: 3rem auto;
  padding: 0 1.5rem;
}

.access-denied-card {
  background: var(--color-white);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  padding: 3rem;
  text-align: center;
  border-left: 4px solid var(--color-danger);
}

.access-denied-card i {
  font-size: 4rem;
  color: var(--color-danger);
  margin-bottom: 1.5rem;
}

.access-denied-card h2 {
  color: var(--color-danger);
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
  font-weight: 700;
}

.access-denied-card p {
  margin-bottom: 1rem;
  color: var(--color-gray);
  font-size: 1.1rem;
}

.btn-back-denied {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: var(--color-white);
  border: none;
  padding: 1rem 2rem;
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
  transition: var(--transition);
}

.btn-back-denied:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* ============ LOADING & ERROR ============ */
.loading-container,
.error-container {
  max-width: 600px;
  margin: 3rem auto;
  background: var(--color-white);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  padding: 3rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid var(--color-light);
  border-top: 4px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.btn-retry {
  background: var(--color-primary);
  color: var(--color-white);
  border: none;
  padding: 1rem 2rem;
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
}

.btn-retry:hover {
  background: var(--color-primary-dark);
  transform: translateY(-2px);
}

/* ============ MAIN CONTENT ============ */
.main-content {
  max-width: 1500px;
  margin: 2rem auto;
  padding: 0 1.5rem;
}

/* ============ FILTERS ============ */
.filters-section {
  margin-bottom: 2rem;
}

.filters-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  background: var(--color-white);
  padding: 1.5rem;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-md);
}

.search-box {
  flex: 1;
  min-width: 250px;
  position: relative;
}

.search-box i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-gray);
  z-index: 2;
}

.search-box input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 2px solid #e2e8f0;
  border-radius: var(--border-radius);
  font-size: 1rem;
  transition: var(--transition);
  font-family: inherit;
}

.search-box input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.clear-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: var(--color-gray);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.clear-btn:hover {
  background: var(--color-light);
  color: var(--color-danger);
}

.filtro-mecanismo {
  min-width: 220px;
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: var(--border-radius);
  font-size: 1rem;
  background: var(--color-white);
  font-family: inherit;
  cursor: pointer;
  transition: var(--transition);
}

.filtro-mecanismo:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.filters-container select {
  min-width: 200px;
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: var(--border-radius);
  font-size: 1rem;
  background: var(--color-white);
  font-family: inherit;
  cursor: pointer;
  transition: var(--transition);
}

.filters-container select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.btn-refresh {
  background: var(--color-white);
  border: 2px solid var(--color-primary);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
}

.btn-refresh:hover {
  background: var(--color-primary);
  color: var(--color-white);
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-clear-filters {
  background: var(--color-warning);
  color: var(--color-white);
  border: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
}

.btn-clear-filters:hover {
  background: #e67e22;
  transform: translateY(-2px);
}

/* Botón Subir Archivos */
.btn-upload-files {
  background: linear-gradient(135deg, #10b981, #059669);
  color: var(--color-white);
  border: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
}

.btn-upload-files:hover {
  background: linear-gradient(135deg, #059669, #047857);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.4);
}

.btn-upload-files i {
  font-size: 1.25rem;
}

.filtro-activo-info {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  border: 1px solid #2196f3;
  border-radius: var(--border-radius);
  padding: 0.75rem 1rem;
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #1565c0;
}

.filtro-activo-info i {
  color: #2196f3;
}

.filtro-activo-info strong {
  color: #0d47a1;
  font-weight: 700;
}

/* ============ STATISTICS ============ */
.stats-section {
  margin-bottom: 2rem;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: var(--color-white);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-md);
  display: flex;
  padding: 1.5rem;
  transition: var(--transition);
  border-top: 4px solid var(--color-primary);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.stat-card:nth-child(2) { border-top-color: var(--color-info); }
.stat-card:nth-child(3) { border-top-color: var(--color-warning); }
.stat-card:nth-child(4) { border-top-color: var(--color-success); }

.stat-icon {
  margin-right: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon i {
  font-size: 2.5rem;
  background: rgba(37, 99, 235, 0.1);
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius);
  color: var(--color-primary);
}

.stat-icon.pending i {
  color: var(--color-warning);
  background: rgba(245, 158, 11, 0.1);
}

.stat-icon.approved i {
  color: var(--color-success);
  background: rgba(16, 185, 129, 0.1);
}

.stat-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: 800;
  line-height: 1;
  color: var(--color-dark);
  margin-bottom: 0.25rem;
}

.stat-label {
  color: var(--color-gray);
  font-size: 1rem;
  font-weight: 600;
}

/* ============ DIRECTORIES SECTION ============ */
.directorios-section {
  background: var(--color-white);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.section-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, var(--color-light), #e2e8f0);
}

.section-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  color: var(--color-dark);
}

.count-badge {
  background: var(--color-primary);
  color: var(--color-white);
  padding: 0.5rem 1rem;
  border-radius: 50px;
  font-size: 0.9rem;
  font-weight: 600;
}

.tree-container {
  padding: 1.5rem;
}

.tree-root {
  margin-bottom: 1.5rem;
  border: 1px solid #e2e8f0;
  border-radius: var(--border-radius);
  overflow: hidden;
  background: var(--color-white);
  box-shadow: var(--shadow-sm);
}

/* ============ NIVEL 0 - DIRECTORIO PADRE ============ */
.directorio-header.nivel-0 {
  background: linear-gradient(135deg, var(--color-light), #f8fafc);
  padding: 1.25rem 1.5rem;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 80px;
}

.directorio-header.nivel-0:hover {
  background: linear-gradient(135deg, #e2e8f0, #cbd5e1);
}

/* ============ DROP TARGET - INDICADOR VISUAL DRAG & DROP ============ */
.drop-target {
  background: linear-gradient(135deg, #c6f6d5, #9ae6b4) !important;
  border: 3px dashed #22c55e !important;
  box-shadow: 0 0 20px rgba(34, 197, 94, 0.4) !important;
  transform: scale(1.02);
  transition: all 0.2s ease;
}

.drop-target::before {
  content: '📂 Soltar archivo aquí';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(34, 197, 94, 0.9);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  z-index: 10;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.directorio-header.drop-target,
.subdirectorio-header.drop-target {
  position: relative;
}

.directorio-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  min-width: 0;
}

.toggle-icon i {
  font-size: 1.5rem;
  color: var(--color-dark);
  transition: var(--transition);
}

.folder-icon.nivel-0 i {
  font-size: 2rem;
  color: var(--color-primary);
  background: rgba(37, 99, 235, 0.1);
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.directorio-info h3 {
  font-size: 1.3rem;
  margin-bottom: 0.25rem;
  font-weight: 700;
  color: var(--color-dark);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.badge-mecanismo {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  background: #e3f2fd;
  color: #1565c0;
  white-space: nowrap;
}

.directorio-stats {
  color: var(--color-gray);
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.directorio-path {
  font-size: 0.8rem;
  color: var(--color-gray-light);
  font-family: 'Courier New', monospace;
  background: rgba(100, 116, 139, 0.1);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
}

.directorio-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-left: auto;
  padding-left: 1rem;
  flex-shrink: 0;
}

.estado-badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.badge {
  font-size: 0.8rem;
  padding: 0.25rem 0.6rem;
  border-radius: 50px;
  font-weight: 600;
}

.badge.mini {
  font-size: 0.7rem;
  padding: 0.2rem 0.5rem;
}

.badge.micro {
  font-size: 0.65rem;
  padding: 0.15rem 0.4rem;
}

.badge.nano {
  font-size: 0.6rem;
  padding: 0.1rem 0.3rem;
  font-weight: 700;
}

.badge.warning {
  background: rgba(245, 158, 11, 0.2);
  color: #d97706;
}

.badge.info {
  background: rgba(37, 99, 235, 0.2);
  color: var(--color-primary-dark);
}

.badge.success {
  background: rgba(16, 185, 129, 0.2);
  color: #059669;
}

/* Botones Subir Archivos por Carpeta */
.btn-subir-directorio,
.btn-subir-subdirectorio {
  background: transparent;
  border: 2px solid #10b981;
  color: #10b981;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: var(--transition);
}

.btn-subir-directorio:hover,
.btn-subir-subdirectorio:hover {
  background: #10b981;
  color: var(--color-white);
  transform: scale(1.05);
}

.btn-subir-subdirectorio.nivel-2,
.btn-subir-subdirectorio.nivel-3 {
  width: 32px;
  height: 32px;
  border-width: 1px;
}

.btn-subir-subdirectorio.nivel-2 i,
.btn-subir-subdirectorio.nivel-3 i {
  font-size: 1rem;
}

.btn-subir-subdirectorio.nivel-4 {
  width: 28px;
  height: 28px;
  border-width: 1px;
  border-color: #059669;
  color: #059669;
}

.btn-subir-subdirectorio.nivel-4:hover {
  background: #059669;
}

.btn-subir-subdirectorio.nivel-4 i {
  font-size: 0.9rem;
}

.btn-subir-subdirectorio.nivel-5 {
  width: 24px;
  height: 24px;
  border-width: 1px;
  border-color: #047857;
  color: #047857;
}

.btn-subir-subdirectorio.nivel-5:hover {
  background: #047857;
}

.btn-subir-subdirectorio.nivel-5 i {
  font-size: 0.8rem;
}

.btn-eliminar-directorio,
.btn-eliminar-subdirectorio {
  background: transparent;
  border: 2px solid var(--color-danger);
  color: var(--color-danger);
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: var(--transition);
}

.btn-eliminar-subdirectorio.nivel-2,
.btn-eliminar-subdirectorio.nivel-3 {
  width: 32px;
  height: 32px;
  border-width: 1px;
}

.btn-eliminar-directorio:hover,
.btn-eliminar-subdirectorio:hover {
  background: var(--color-danger);
  color: var(--color-white);
}

.btn-eliminar-directorio.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.directorio-children {
  padding: 1rem 1.5rem 1rem 3rem;
  background: #fafbfc;
}

/* ============ NIVEL 1 - SUBDIRECTORIOS ============ */
.subdirectorio.nivel-1 {
  margin-bottom: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: var(--border-radius);
  overflow: hidden;
  background: var(--color-white);
  border-left: 4px solid #10b981;
}

.subdirectorio-header.nivel-1 {
  background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
  padding: 1rem 1.25rem;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.subdirectorio-header.nivel-1:hover {
  background: linear-gradient(135deg, #ecfdf5, #d1fae5);
}

.subdirectorio-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.folder-icon.nivel-1 i {
  font-size: 1.8rem;
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.subdirectorio-info h4 {
  font-size: 1.1rem;
  margin-bottom: 0.25rem;
  font-weight: 600;
  color: var(--color-dark);
}

.subdirectorio-stats {
  color: var(--color-gray);
  font-size: 0.85rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.subdirectorio-path {
  font-size: 0.75rem;
  color: var(--color-gray-light);
  font-family: 'Courier New', monospace;
  background: rgba(100, 116, 139, 0.1);
  padding: 0.15rem 0.3rem;
  border-radius: 3px;
}

.subdirectorio-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  margin-left: auto;
  padding-left: 0.75rem;
  flex-shrink: 0;
}

.subdirectorio-children.nivel-1 {
  padding: 1rem 1.25rem 1rem 2.5rem;
  background: #fafbfc;
}

/* ============ NIVEL 2 - SUB-SUBDIRECTORIOS ============ */
.subdirectorio.nivel-2 {
  margin-left: 1.5rem;
  margin-bottom: 0.75rem;
  border-left: 3px solid #8b5cf6;
  background: #faf9ff;
  border-radius: var(--border-radius);
  overflow: hidden;
}

.subdirectorio-header.nivel-2 {
  background: linear-gradient(135deg, #faf9ff, #f3f0ff);
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.subdirectorio-header.nivel-2:hover {
  background: linear-gradient(135deg, #f3f0ff, #ede9fe);
}

.folder-icon.nivel-2 i {
  font-size: 1.6rem;
  color: #8b5cf6;
  background: rgba(139, 92, 246, 0.1);
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.subdirectorio-info h5 {
  font-size: 1rem;
  margin-bottom: 0.2rem;
  font-weight: 600;
  color: var(--color-dark);
}

.subdirectorio-stats.nivel-2 {
  color: var(--color-gray);
  font-size: 0.8rem;
  font-weight: 500;
  margin-bottom: 0.2rem;
}

.subdirectorio-path.nivel-2 {
  font-size: 0.7rem;
  color: var(--color-gray-light);
  font-family: 'Courier New', monospace;
  background: rgba(139, 92, 246, 0.1);
  padding: 0.1rem 0.25rem;
  border-radius: 3px;
}

.subdirectorio-children.nivel-2 {
  padding: 0.75rem 1rem 0.75rem 2rem;
  background: #fefeff;
  border-left: 2px solid #c4b5fd;
}

/* ============ NIVEL 3 - CUARTO NIVEL VISUAL (AZUL AGUAMARINA) ============ */
.subdirectorio.nivel-3 {
  margin-left: 1.5rem;
  margin-bottom: 0.75rem;
  border-left: 3px solid var(--color-aquamarine);
  background: var(--color-aquamarine-bg);
  border-radius: var(--border-radius);
  overflow: hidden;
}

.subdirectorio-header.nivel-3 {
  background: linear-gradient(135deg, var(--color-aquamarine-bg), #ccfbf1);
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.subdirectorio-header.nivel-3:hover {
  background: linear-gradient(135deg, #ccfbf1, #99f6e4);
}

.folder-icon.nivel-3 i {
  font-size: 1.6rem;
  color: var(--color-aquamarine);
  background: rgba(32, 178, 170, 0.15);
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.subdirectorio-info h6 {
  font-size: 1rem;
  margin-bottom: 0.2rem;
  font-weight: 600;
  color: var(--color-dark);
}

.subdirectorio-stats.nivel-3 {
  color: var(--color-gray);
  font-size: 0.8rem;
  font-weight: 500;
  margin-bottom: 0.2rem;
}

.subdirectorio-path.nivel-3 {
  font-size: 0.7rem;
  color: var(--color-gray-light);
  font-family: 'Courier New', monospace;
  background: rgba(32, 178, 170, 0.1);
  padding: 0.1rem 0.25rem;
  border-radius: 3px;
}

.subdirectorio-children.nivel-3 {
  padding: 0.75rem 1rem 0.75rem 2rem;
  background: var(--color-aquamarine-bg);
  border-left: 2px solid var(--color-aquamarine-light);
}

/* ============ NIVEL 4 - QUINTO NIVEL VISUAL (CORAL/SALMON) ============ */
.subdirectorio.nivel-4 {
  margin-left: 1.25rem;
  margin-bottom: 0.5rem;
  border-left: 3px solid #f97316;
  background: #fff7ed;
  border-radius: var(--border-radius);
  overflow: hidden;
}

.subdirectorio-header.nivel-4 {
  background: linear-gradient(135deg, #fff7ed, #ffedd5);
  padding: 0.6rem 0.8rem;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.subdirectorio-header.nivel-4:hover {
  background: linear-gradient(135deg, #ffedd5, #fed7aa);
}

.folder-icon.nivel-4 i {
  font-size: 1.4rem;
  color: #f97316;
  background: rgba(249, 115, 22, 0.15);
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.subdirectorio-stats.nivel-4 {
  color: var(--color-gray);
  font-size: 0.75rem;
  font-weight: 500;
  margin-bottom: 0.15rem;
}

.subdirectorio-path.nivel-4 {
  font-size: 0.65rem;
  color: var(--color-gray-light);
  font-family: 'Courier New', monospace;
  background: rgba(249, 115, 22, 0.1);
  padding: 0.1rem 0.2rem;
  border-radius: 3px;
}

.subdirectorio-children.nivel-4 {
  padding: 0.5rem 0.75rem 0.5rem 1.5rem;
  background: #fff7ed;
  border-left: 2px solid #fdba74;
}

.btn-eliminar-subdirectorio.nivel-4 {
  background: transparent;
  border: 1px solid #f97316;
  color: #f97316;
  padding: 0.25rem;
  border-radius: 4px;
  cursor: pointer;
  transition: var(--transition);
}

.btn-eliminar-subdirectorio.nivel-4:hover {
  background: #f97316;
  color: white;
}

.btn-eliminar-subdirectorio.nivel-4 i {
  font-size: 0.9rem;
}

/* Badge pico para nivel 4 */
.badge.pico {
  font-size: 0.55rem;
  padding: 0.1rem 0.25rem;
  border-radius: 3px;
}

/* ============ FILES SECTION ============ */
.archivos-directos,
.archivos-subdirectorio {
  margin-top: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: var(--border-radius);
  background: var(--color-white);
}

.archivos-subdirectorio.nivel-1 {
  border-left: 3px solid #10b981;
}

.archivos-subdirectorio.nivel-2 {
  border-left: 3px solid #8b5cf6;
  margin-top: 0.75rem;
}

.archivos-subdirectorio.nivel-3 {
  border-left: 3px solid var(--color-aquamarine);
  margin-top: 0.75rem;
  background: var(--color-aquamarine-bg);
}

.archivos-subdirectorio.nivel-4 {
  border-left: 3px solid #f97316;
  margin-top: 0.5rem;
  background: #fff7ed;
}

.archivos-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(135deg, #f8fafc, var(--color-light));
}

.archivos-header.nivel-0 {
  background: linear-gradient(135deg, #f8fafc, var(--color-light));
}

.archivos-header.nivel-1 {
  background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
}

.archivos-header.nivel-2 {
  background: linear-gradient(135deg, #faf9ff, #f3f0ff);
  padding: 0.75rem 1rem;
}

.archivos-header.nivel-3 {
  background: linear-gradient(135deg, var(--color-aquamarine-bg), #ccfbf1);
  padding: 0.75rem 1rem;
}

.archivos-header.nivel-4 {
  background: linear-gradient(135deg, #fff7ed, #ffedd5);
  padding: 0.6rem 0.8rem;
}

.btn-toggle-archivos {
  background: transparent;
  border: 2px solid var(--color-primary);
  color: var(--color-primary);
  padding: 0.6rem 1.2rem;
  border-radius: var(--border-radius);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: var(--transition);
}

.btn-toggle-archivos.nivel-1 {
  border-color: #10b981;
  color: #10b981;
}

.btn-toggle-archivos.nivel-2 {
  border-color: #8b5cf6;
  color: #8b5cf6;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

.btn-toggle-archivos.nivel-3 {
  border-color: var(--color-aquamarine);
  color: var(--color-aquamarine);
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

.btn-toggle-archivos.nivel-4 {
  border-color: #f97316;
  color: #f97316;
  padding: 0.4rem 0.8rem;
  font-size: 0.85rem;
}

.btn-toggle-archivos:hover {
  background: var(--color-primary);
  color: var(--color-white);
}

.btn-toggle-archivos.nivel-1:hover {
  background: #10b981;
  color: var(--color-white);
}

.btn-toggle-archivos.nivel-2:hover {
  background: #8b5cf6;
  color: var(--color-white);
}

.btn-toggle-archivos.nivel-3:hover {
  background: var(--color-aquamarine);
  color: var(--color-white);
}

.btn-toggle-archivos.nivel-4:hover {
  background: #f97316;
  color: var(--color-white);
}

/* ============ ARCHIVOS LISTA OPTIMIZADA ============ */
.archivos-lista {
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.archivos-lista.nivel-1 {
  padding: 0.6rem;
  gap: 0.4rem;
}

.archivos-lista.nivel-2 {
  padding: 0.5rem;
  gap: 0.35rem;
}

.archivos-lista.nivel-3 {
  padding: 0.4rem;
  gap: 0.3rem;
  background: var(--color-aquamarine-bg);
}

.archivos-lista.nivel-4 {
  padding: 0.35rem;
  gap: 0.25rem;
  background: #fff7ed;
}

/* ============ GRID ARCHIVO ITEMS OPTIMIZADO PARA MÁXIMO ESPACIO ============ */
.archivo-item {
  display: grid;
  grid-template-columns: 2.2fr 140px 180px 160px;
  gap: 0.8rem;
  align-items: center;
  padding: 0.8rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: var(--color-white);
  transition: var(--transition);
  font-size: 0.9rem;
  min-height: 70px;
}

.archivo-item.nivel-1 {
  padding: 0.7rem 0.9rem;
  border-left: 3px solid #10b981;
  grid-template-columns: 2.1fr 130px 170px 150px;
  gap: 0.7rem;
  min-height: 65px;
  font-size: 0.85rem;
}

.archivo-item.nivel-2 {
  padding: 0.6rem 0.8rem;
  border-left: 3px solid #8b5cf6;
  grid-template-columns: 2fr 120px 160px 140px;
  gap: 0.6rem;
  font-size: 0.82rem;
  min-height: 60px;
}

.archivo-item.nivel-3 {
  padding: 0.55rem 0.75rem;
  border-left: 3px solid var(--color-aquamarine);
  grid-template-columns: 1.9fr 110px 150px 130px;
  gap: 0.5rem;
  background: var(--color-aquamarine-bg);
  font-size: 0.8rem;
  min-height: 58px;
}

.archivo-item.nivel-4 {
  padding: 0.5rem 0.7rem;
  border-left: 3px solid #f97316;
  grid-template-columns: 1.8fr 100px 140px 120px;
  gap: 0.45rem;
  background: #fff7ed;
  font-size: 0.78rem;
  min-height: 55px;
}

/* ============ DISEÑO COMPACTO NIVEL 4 (5° NIVEL) ============ */
.archivo-item-compacto.nivel-4 {
  background: #fff7ed;
  border-left: 3px solid #f97316;
  border-radius: 4px;
  padding: 0.4rem 0.5rem;
  margin-bottom: 0.3rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.archivo-item-compacto.nivel-4:hover {
  background: #ffedd5;
  border-left-color: #ea580c;
}

/* Fila 1: Icono + Nombre + Estado + Acciones */
.archivo-row-1 {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  width: 100%;
}

.archivo-icon-mini {
  width: 24px;
  height: 24px;
  min-width: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(249, 115, 22, 0.15);
  border-radius: 4px;
}

.archivo-icon-mini i {
  font-size: 0.9rem;
  color: #f97316;
}

.archivo-nombre-compacto {
  flex: 1;
  font-size: 0.75rem;
  font-weight: 500;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

.estado-badge-mini {
  font-size: 0.6rem;
  padding: 0.15rem 0.35rem;
  border-radius: 3px;
  font-weight: 600;
  text-transform: uppercase;
  white-space: nowrap;
}

.estado-badge-mini.pendiente {
  background: #fef3c7;
  color: #d97706;
}

.estado-badge-mini.aprobado {
  background: #d1fae5;
  color: #059669;
}

.estado-badge-mini.rechazado {
  background: #fee2e2;
  color: #dc2626;
}

.acciones-compactas {
  display: flex;
  gap: 0.2rem;
  flex-shrink: 0;
}

.btn-mini {
  width: 22px;
  height: 22px;
  padding: 0;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.btn-mini i {
  font-size: 0.8rem;
}

.btn-mini.info {
  background: #e0f2fe;
  color: #0284c7;
}

.btn-mini.info:hover {
  background: #0284c7;
  color: white;
}

.btn-mini.view {
  background: #f0fdf4;
  color: #16a34a;
}

.btn-mini.view:hover {
  background: #16a34a;
  color: white;
}

.btn-mini.download {
  background: #ede9fe;
  color: #7c3aed;
}

.btn-mini.download:hover {
  background: #7c3aed;
  color: white;
}

.btn-mini.edit {
  background: #fef3c7;
  color: #d97706;
}

.btn-mini.edit:hover {
  background: #d97706;
  color: white;
}

.btn-mini.delete {
  background: #fee2e2;
  color: #dc2626;
}

.btn-mini.delete:hover {
  background: #dc2626;
  color: white;
}

/* Fila 2: Fecha + Status + Calificación */
.archivo-row-2 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-left: 28px;
  font-size: 0.68rem;
}

.fecha-mini {
  color: #64748b;
  white-space: nowrap;
}

.status-icons {
  display: flex;
  gap: 0.3rem;
}

.icon-status {
  font-size: 0.6rem;
  font-weight: 600;
  padding: 0.1rem 0.25rem;
  border-radius: 2px;
}

.icon-status.ok {
  background: #d1fae5;
  color: #059669;
}

.icon-status.no {
  background: #fee2e2;
  color: #dc2626;
}

.select-mini {
  flex: 1;
  max-width: 150px;
  padding: 0.15rem 0.3rem;
  font-size: 0.65rem;
  border: 1px solid #fdba74;
  border-radius: 3px;
  background: white;
  color: #1e293b;
  cursor: pointer;
}

.select-mini:focus {
  outline: none;
  border-color: #f97316;
  box-shadow: 0 0 0 2px rgba(249, 115, 22, 0.2);
}

.cal-mini {
  font-size: 0.65rem;
  color: #64748b;
  font-style: italic;
}

/* ============ NIVEL 5 - SEXTO NIVEL VISUAL (ROSA/FUCSIA) ============ */
.subdirectorio.nivel-5 {
  margin-left: 1rem;
  margin-bottom: 0.4rem;
  border-left: 3px solid #ec4899;
  background: #fdf2f8;
  border-radius: 4px;
  overflow: hidden;
}

.subdirectorio-header.nivel-5 {
  background: linear-gradient(135deg, #fdf2f8, #fce7f3);
  padding: 0.5rem 0.6rem;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.subdirectorio-header.nivel-5:hover {
  background: linear-gradient(135deg, #fce7f3, #fbcfe8);
}

.folder-icon.nivel-5 i {
  font-size: 1.2rem;
  color: #ec4899;
  background: rgba(236, 72, 153, 0.15);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: var(--transition);
}

.subdirectorio-stats.nivel-5 {
  color: var(--color-gray);
  font-size: 0.7rem;
  font-weight: 500;
  margin-bottom: 0.1rem;
}

.subdirectorio-children.nivel-5 {
  padding: 0.4rem 0.5rem 0.4rem 1rem;
  background: #fdf2f8;
  border-left: 2px solid #f9a8d4;
}

.btn-eliminar-subdirectorio.nivel-5 {
  background: transparent;
  border: 1px solid #ec4899;
  color: #ec4899;
  padding: 0.2rem;
  border-radius: 3px;
  cursor: pointer;
  transition: var(--transition);
}

.btn-eliminar-subdirectorio.nivel-5:hover {
  background: #ec4899;
  color: white;
}

.btn-eliminar-subdirectorio.nivel-5 i {
  font-size: 0.8rem;
}

/* Badge micro para nivel 5 */
.badge.micro {
  font-size: 0.5rem;
  padding: 0.08rem 0.2rem;
  border-radius: 2px;
}

.archivos-subdirectorio.nivel-5 {
  border-left: 3px solid #ec4899;
  margin-top: 0.4rem;
  background: #fdf2f8;
}

.archivos-header.nivel-5 {
  background: linear-gradient(135deg, #fdf2f8, #fce7f3);
  padding: 0.5rem 0.6rem;
}

.btn-toggle-archivos.nivel-5 {
  border-color: #ec4899;
  color: #ec4899;
  padding: 0.35rem 0.7rem;
  font-size: 0.8rem;
}

.btn-toggle-archivos.nivel-5:hover {
  background: #ec4899;
  color: var(--color-white);
}

.archivos-lista.nivel-5 {
  padding: 0.3rem;
  gap: 0.2rem;
  background: #fdf2f8;
}

/* Diseño compacto nivel 5 */
.archivo-item-compacto.nivel-5 {
  background: #fdf2f8;
  border-left: 3px solid #ec4899;
  border-radius: 3px;
  padding: 0.35rem 0.45rem;
  margin-bottom: 0.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.archivo-item-compacto.nivel-5:hover {
  background: #fce7f3;
  border-left-color: #db2777;
}

.archivo-icon-mini.nivel-5 {
  background: rgba(236, 72, 153, 0.15);
}

.archivo-icon-mini.nivel-5 i {
  color: #ec4899;
}

.select-mini.nivel-5 {
  border-color: #f9a8d4;
}

.select-mini.nivel-5:focus {
  border-color: #ec4899;
  box-shadow: 0 0 0 2px rgba(236, 72, 153, 0.2);
}

.empty-level.nivel-5 {
  background: #fdf2f8;
  color: #db2777;
  padding: 0.75rem;
  font-size: 0.75rem;
}

.archivo-item:hover {
  background: #f8fafc;
  border-color: var(--color-primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.archivo-item.nivel-1:hover {
  border-left-color: #059669;
}

.archivo-item.nivel-2:hover {
  border-left-color: #7c3aed;
}

.archivo-item.nivel-3:hover {
  border-left-color: #0d9488;
  background: #ccfbf1;
}

.archivo-item.nivel-4:hover {
  border-left-color: #ea580c;
  background: #ffedd5;
}

/* ============ INFORMACIÓN DE ARCHIVO OPTIMIZADA ============ */
.archivo-info {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  min-width: 0;
  flex: 1;
}

.archivo-icon {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(59, 130, 246, 0.08));
  border-radius: 6px;
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid rgba(37, 99, 235, 0.15);
  transition: var(--transition);
}

.archivo-item.nivel-1 .archivo-icon {
  width: 38px;
  height: 38px;
}

.archivo-item.nivel-2 .archivo-icon {
  width: 34px;
  height: 34px;
}

.archivo-item.nivel-3 .archivo-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, rgba(32, 178, 170, 0.12), rgba(94, 234, 212, 0.08));
  border: 1px solid rgba(32, 178, 170, 0.15);
  position: relative;
}

.archivo-item.nivel-4 .archivo-icon {
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.12), rgba(251, 146, 60, 0.08));
  border: 1px solid rgba(249, 115, 22, 0.15);
  position: relative;
}

.archivo-icon i {
  font-size: 1.2rem;
  color: var(--color-primary);
  transition: var(--transition);
}

.archivo-item.nivel-1 .archivo-icon i {
  font-size: 1.1rem;
}

.archivo-item.nivel-2 .archivo-icon i {
  font-size: 1rem;
}

.archivo-item.nivel-3 .archivo-icon i {
  font-size: 0.95rem;
  color: var(--color-aquamarine);
}

.archivo-item.nivel-4 .archivo-icon i {
  font-size: 0.9rem;
  color: #f97316;
}

.depth-indicator {
  position: absolute;
  top: -6px;
  right: -6px;
  background: linear-gradient(135deg, var(--color-aquamarine), #0d9488);
  color: white;
  font-size: 0.6rem;
  font-weight: 700;
  padding: 0.2rem 0.35rem;
  border-radius: 8px;
  line-height: 1;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  min-width: 16px;
  text-align: center;
}

.archivo-detalles {
  min-width: 0;
  flex: 1;
  line-height: 1.4;
}

.archivo-nombre {
  font-weight: 600;
  font-size: 0.88rem;
  margin: 0 0 0.2rem 0;
  color: var(--color-dark);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
  transition: var(--transition);
}

.archivo-item.nivel-2 .archivo-nombre {
  font-size: 0.82rem;
}

.archivo-item.nivel-3 .archivo-nombre {
  font-size: 0.78rem;
}

.archivo-nombre:hover {
  color: var(--color-primary);
}

.archivo-fecha {
  font-size: 0.75rem;
  color: var(--color-gray);
  margin: 0 0 0.15rem 0;
  font-weight: 500;
}

.archivo-item.nivel-2 .archivo-fecha,
.archivo-item.nivel-3 .archivo-fecha {
  font-size: 0.7rem;
}

.archivo-profundidad {
  font-size: 0.7rem;
  color: var(--color-aquamarine);
  margin: 0;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

/* ============ ESTADOS ARCHIVO OPTIMIZADOS ============ */
.archivo-estado {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.3rem 0.6rem;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  white-space: nowrap;
  text-align: center;
  min-width: 80px;
  border: 1px solid transparent;
  transition: var(--transition);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  line-height: 1.2;
}

.archivo-item.nivel-2 .archivo-estado,
.archivo-item.nivel-3 .archivo-estado {
  font-size: 0.65rem;
  padding: 0.25rem 0.5rem;
  min-width: 70px;
}

.archivo-estado.pendiente {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  color: #d97706;
  border-color: rgba(217, 119, 6, 0.2);
}

.archivo-estado.evaluado {
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  color: var(--color-primary-dark);
  border-color: rgba(37, 99, 235, 0.2);
}

.archivo-estado.aprobado {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  color: #059669;
  border-color: rgba(5, 150, 105, 0.2);
}

/* ============ STATUS INDICATORS OPTIMIZADOS ============ */
.archivo-status {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  align-items: flex-start;
  width: 140px;
}

.archivo-item.nivel-1 .archivo-status {
  width: 130px;
}

.archivo-item.nivel-2 .archivo-status {
  width: 120px;
}

.archivo-item.nivel-3 .archivo-status {
  width: 110px;
}

.status-indicator {
  font-size: 0.7rem;
  padding: 0.25rem 0.5rem;
  border-radius: 10px;
  font-weight: 600;
  text-align: center;
  width: 100%;
  white-space: nowrap;
  line-height: 1.2;
  transition: var(--transition);
  border: 1px solid transparent;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.archivo-item.nivel-2 .status-indicator,
.archivo-item.nivel-3 .status-indicator {
  font-size: 0.65rem;
  padding: 0.2rem 0.4rem;
}

.status-indicator.success {
  background: linear-gradient(135deg, #ecfdf5, #d1fae5);
  color: #059669;
  border-color: rgba(16, 185, 129, 0.2);
}

.status-indicator.success:hover {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.15);
}

.status-indicator.pending {
  background: linear-gradient(135deg, #fef2f2, #fecaca);
  color: #dc2626;
  border-color: rgba(239, 68, 68, 0.2);
}

.status-indicator.pending:hover {
  background: linear-gradient(135deg, #fecaca, #fca5a5);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.15);
}

/* ============ CALIFICACIÓN OPTIMIZADA ============ */
.archivo-calificacion {
  width: 180px;
  max-width: 180px;
}

.archivo-item.nivel-1 .archivo-calificacion {
  width: 170px;
  max-width: 170px;
}

.archivo-item.nivel-2 .archivo-calificacion {
  width: 160px;
  max-width: 160px;
}

.archivo-item.nivel-3 .archivo-calificacion {
  width: 150px;
  max-width: 150px;
}

.calificacion-select {
  width: 100%;
  padding: 0.45rem 0.35rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: linear-gradient(135deg, var(--color-white), #f8fafc);
  font-size: 0.75rem;
  cursor: pointer;
  transition: var(--transition);
  line-height: 1.2;
  font-weight: 500;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.archivo-item.nivel-2 .calificacion-select,
.archivo-item.nivel-3 .calificacion-select {
  font-size: 0.7rem;
  padding: 0.35rem 0.3rem;
}

.calificacion-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1), 0 2px 4px rgba(0, 0, 0, 0.05);
  background: var(--color-white);
}

.calificacion-select:hover {
  border-color: var(--color-primary-light);
  background: var(--color-white);
  transform: translateY(-1px);
}

.calificacion-readonly {
  background: linear-gradient(135deg, var(--color-light), #e2e8f0);
  border-radius: 6px;
  padding: 0.45rem 0.35rem;
  font-size: 0.75rem;
  color: var(--color-gray);
  font-weight: 600;
  text-align: center;
  border: 1px solid #e2e8f0;
  line-height: 1.2;
  word-wrap: break-word;
  width: 100%;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  transition: var(--transition);
}

.archivo-item.nivel-2 .calificacion-readonly,
.archivo-item.nivel-3 .calificacion-readonly {
  font-size: 0.7rem;
  padding: 0.35rem 0.3rem;
}

.calificacion-readonly:hover {
  background: linear-gradient(135deg, #e2e8f0, #cbd5e1);
}

/* Wrapper para calificación + usuario */
.archivo-calificacion-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  min-width: 180px;
}

/* Usuario calificador - sutil debajo de la calificación */
.usuario-calificador {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3px;
  font-size: 0.65rem;
  color: #6b7280;
  text-align: center;
  font-weight: 400;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  margin-top: 2px;
}

.usuario-calificador .material-icons {
  font-size: 0.7rem;
  color: #9ca3af;
}

.archivo-item.nivel-2 .usuario-calificador,
.archivo-item.nivel-3 .usuario-calificador {
  font-size: 0.6rem;
}

.archivo-item.nivel-2 .usuario-calificador .material-icons,
.archivo-item.nivel-3 .usuario-calificador .material-icons {
  font-size: 0.65rem;
}

.archivo-item.nivel-2 .archivo-calificacion-wrapper,
.archivo-item.nivel-3 .archivo-calificacion-wrapper {
  min-width: 160px;
}

/* ============ USUARIO CALIFICADOR MINI (vistas compactas nivel 4 y 5) ============ */
.usuario-calificador-mini {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 0.6rem;
  color: #6b7280;
  font-weight: 400;
  white-space: nowrap;
  margin-left: 6px;
}

.usuario-calificador-mini .material-icons {
  font-size: 0.6rem;
  color: #9ca3af;
}

/* ============ BOTONES DE ACCIONES OPTIMIZADOS ============ */
.archivo-acciones {
  display: flex;
  gap: 0.4rem;
  justify-content: flex-end;
  width: 160px;
  flex-wrap: wrap;
  align-items: center;
}

.archivo-item.nivel-1 .archivo-acciones {
  width: 150px;
  gap: 0.35rem;
}

.archivo-item.nivel-2 .archivo-acciones {
  width: 140px;
  gap: 0.3rem;
}

.archivo-item.nivel-3 .archivo-acciones {
  width: 130px;
  gap: 0.25rem;
}

.btn-accion {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.45rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  transform: translateY(0);
}

.archivo-item.nivel-1 .btn-accion {
  width: 30px;
  height: 30px;
  padding: 0.4rem;
}

.archivo-item.nivel-2 .btn-accion {
  width: 28px;
  height: 28px;
  padding: 0.35rem;
}

.archivo-item.nivel-3 .btn-accion {
  width: 26px;
  height: 26px;
  padding: 0.3rem;
}

.btn-accion::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.btn-accion:hover::before {
  left: 100%;
}

.btn-accion i {
  font-size: 0.85rem;
  z-index: 1;
  position: relative;
  transition: var(--transition);
}

.archivo-item.nivel-1 .btn-accion i {
  font-size: 0.8rem;
}

.archivo-item.nivel-2 .btn-accion i {
  font-size: 0.75rem;
}

.archivo-item.nivel-3 .btn-accion i {
  font-size: 0.7rem;
}

.btn-accion:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.btn-accion:active {
  transform: translateY(-1px) scale(0.98);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* ============ COLORES DE BOTONES ============ */
.btn-accion.info {
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  color: var(--color-primary);
  border: 1px solid rgba(37, 99, 235, 0.2);
}

.btn-accion.info:hover {
  background: linear-gradient(135deg, var(--color-primary), #1d4ed8);
  color: var(--color-white);
  box-shadow: 0 4px 8px rgba(37, 99, 235, 0.3);
}

.btn-accion.view {
  background: linear-gradient(135deg, #cffafe, #a7f3d0);
  color: var(--color-info);
  border: 1px solid rgba(6, 182, 212, 0.2);
}

.btn-accion.view:hover {
  background: linear-gradient(135deg, var(--color-info), #0891b2);
  color: var(--color-white);
  box-shadow: 0 4px 8px rgba(6, 182, 212, 0.3);
}

.btn-accion.download {
  background: linear-gradient(135deg, #f3e8ff, #e9d5ff);
  color: #8b5cf6;
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.btn-accion.download:hover {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: var(--color-white);
  box-shadow: 0 4px 8px rgba(139, 92, 246, 0.3);
}

.btn-accion.edit {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  color: var(--color-warning);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.btn-accion.edit:hover {
  background: linear-gradient(135deg, var(--color-warning), #d97706);
  color: var(--color-white);
  box-shadow: 0 4px 8px rgba(245, 158, 11, 0.3);
}

.btn-accion.delete {
  background: linear-gradient(135deg, #fef2f2, #fecaca);
  color: var(--color-danger);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.btn-accion.delete:hover {
  background: linear-gradient(135deg, var(--color-danger), #dc2626);
  color: var(--color-white);
  box-shadow: 0 4px 8px rgba(239, 68, 68, 0.3);
}

/* ============ ANIMACIONES PARA BOTONES ============ */
.btn-accion:hover i {
  transform: scale(1.1);
}

.btn-accion.info:hover i {
  animation: pulse 1s infinite;
}

.btn-accion.view:hover i {
  animation: bounce 0.6s ease-in-out;
}

.btn-accion.download:hover i {
  animation: downloadBounce 0.8s ease-in-out;
}

.btn-accion.edit:hover i {
  animation: wiggle 0.5s ease-in-out;
}

.btn-accion.delete:hover i {
  animation: shake 0.5s ease-in-out;
}

@keyframes pulse {
  0%, 100% { transform: scale(1.1); }
  50% { transform: scale(1.2); }
}

@keyframes bounce {
  0%, 20%, 60%, 100% { transform: translateY(0) scale(1.1); }
  40% { transform: translateY(-4px) scale(1.1); }
  80% { transform: translateY(-2px) scale(1.1); }
}

@keyframes downloadBounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0) scale(1.1); }
  40% { transform: translateY(3px) scale(1.1); }
  60% { transform: translateY(1px) scale(1.1); }
}

@keyframes wiggle {
  0%, 100% { transform: rotate(0deg) scale(1.1); }
  25% { transform: rotate(-3deg) scale(1.1); }
  75% { transform: rotate(3deg) scale(1.1); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0) scale(1.1); }
  25% { transform: translateX(-2px) scale(1.1); }
  75% { transform: translateX(2px) scale(1.1); }
}

/* ============ EMPTY STATES ============ */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--color-gray);
}

.empty-state i {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  color: var(--color-gray-light);
}

.empty-state h3 {
  font-size: 1.4rem;
  margin-bottom: 1rem;
  color: var(--color-dark);
  font-weight: 700;
}

.empty-level {
  text-align: center;
  padding: 1.5rem;
  color: var(--color-gray);
  font-style: italic;
  background: #f8fafc;
  border-radius: var(--border-radius);
  margin: 0.5rem;
}

.empty-level.nivel-3 {
  background: var(--color-aquamarine-bg);
  color: #0d9488;
}

.empty-level.nivel-4 {
  background: #fff7ed;
  color: #ea580c;
}

.empty-level i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  color: var(--color-gray-light);
  display: block;
}

/* ============ MODALS ============ */
.modal-overlay {
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
  backdrop-filter: blur(4px);
  padding: 1rem;
}

.modal-content {
  background: var(--color-white);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, var(--color-light), #f8fafc);
}

.modal-header h3 {
  margin: 0;
  color: var(--color-dark);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.2rem;
  font-weight: 700;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-gray);
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: var(--transition);
}

.modal-close:hover {
  background: var(--color-light);
  color: var(--color-dark);
}

.modal-body {
  padding: 1.5rem;
}

.file-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-group label {
  font-weight: 600;
  color: var(--color-gray);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-group span {
  color: var(--color-dark);
  font-weight: 500;
}

/* Usuario calificador en modal */
.usuario-evaluacion-info .usuario-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #eef2ff, #e0e7ff);
  color: #4f46e5;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
  border: 1px solid #c7d2fe;
}

.usuario-evaluacion-info .usuario-badge .material-icons {
  font-size: 1rem;
  color: #6366f1;
}

.ruta-texto {
  background: var(--color-light);
  padding: 0.75rem;
  border-radius: var(--border-radius);
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  word-break: break-all;
  border: 1px solid #e2e8f0;
}

.estado-badge {
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  width: fit-content;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: var(--color-dark);
}

.form-group textarea {
  width: 100%;
  min-height: 120px;
  padding: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: var(--border-radius);
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: var(--transition);
}

.form-group textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.warning-box {
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: var(--border-radius);
  padding: 1rem;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin: 1rem 0;
}

.warning-box i {
  color: var(--color-warning);
  font-size: 1.5rem;
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.warning-box p {
  margin: 0;
  color: #d97706;
  font-weight: 500;
}

.modal-footer {
  padding: 1.25rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: flex-end;
  align-items: center;
  background: linear-gradient(135deg, var(--color-light), #f8fafc);
}

.btn-primary,
.btn-secondary,
.btn-danger,
.btn-warning {
  padding: 0.6rem 1rem;
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  transition: var(--transition);
  border: none;
  font-size: 0.85rem;
  white-space: nowrap;
}

.btn-primary .material-icons,
.btn-secondary .material-icons,
.btn-danger .material-icons,
.btn-warning .material-icons {
  font-size: 1rem;
}

.btn-primary {
  background: var(--color-primary);
  color: var(--color-white);
}

.btn-primary:hover {
  background: var(--color-primary-dark);
  transform: translateY(-2px);
}

.btn-secondary {
  background: var(--color-gray);
  color: var(--color-white);
}

.btn-secondary:hover {
  background: var(--color-dark);
  transform: translateY(-2px);
}

.btn-danger {
  background: var(--color-danger);
  color: var(--color-white);
}

.btn-danger:hover {
  background: #dc2626;
  transform: translateY(-2px);
}

.btn-warning {
  background: #f59e0b;
  color: var(--color-white);
}

.btn-warning:hover {
  background: #d97706;
  transform: translateY(-2px);
}

/* ============ NOTIFICATIONS ============ */
.notification {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 1rem 1.5rem;
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  gap: 1rem;
  z-index: 2000;
  box-shadow: var(--shadow-lg);
  max-width: 400px;
  animation: slideInNotification 0.4s ease-out;
}

@keyframes slideInNotification {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.notification.success {
  background: var(--color-success);
  color: var(--color-white);
}

.notification.error {
  background: var(--color-danger);
  color: var(--color-white);
}

.notification.warning {
  background: var(--color-warning);
  color: var(--color-white);
}

.notification.info {
  background: var(--color-info);
  color: var(--color-white);
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.notification-content i {
  font-size: 1.5rem;
}

.notification-content span {
  font-weight: 500;
  line-height: 1.4;
}

.notification-close {
  background: transparent;
  border: none;
  color: var(--color-white);
  cursor: pointer;
  font-size: 1.25rem;
  opacity: 0.8;
  transition: var(--transition);
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.notification-close:hover {
  opacity: 1;
  background: rgba(255, 255, 255, 0.1);
}


/* ============ RUTA EDITABLE - ESTILOS CSS ============ */

/* Contenedor principal de la ruta */
.ruta-container {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

/* Texto de la ruta (modo lectura) */
.ruta-texto {
  background: var(--color-light);
  padding: 0.75rem;
  border-radius: var(--border-radius);
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  word-break: break-all;
  border: 1px solid #e2e8f0;
  flex: 1;
}

/* Botón para editar la ruta */
.btn-editar-ruta {
  background: transparent;
  border: 2px solid var(--color-warning);
  color: var(--color-warning);
  padding: 0.5rem;
  border-radius: var(--border-radius);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
  width: 40px;
  height: 40px;
  flex-shrink: 0;
}

.btn-editar-ruta:hover {
  background: var(--color-warning);
  color: var(--color-white);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(245, 158, 11, 0.3);
}

/* Contenedor del modo edición */
.ruta-editable {
  width: 100%;
}

/* Textarea para editar la ruta */
.ruta-textarea {
  width: 100%;
  min-height: 100px;
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: var(--border-radius);
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  resize: vertical;
  transition: var(--transition);
  background: var(--color-white);
  line-height: 1.4;
}

.ruta-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.ruta-textarea::placeholder {
  color: var(--color-gray-light);
  font-style: italic;
}

/* Contenedor de botones de acción */
.ruta-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.75rem;
  justify-content: flex-end;
}

/* Botones de guardar y cancelar */
.btn-guardar-ruta,
.btn-cancelar-ruta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  border: none;
  font-size: 0.9rem;
  font-family: inherit;
}

/* Botón Guardar */
.btn-guardar-ruta {
  background: linear-gradient(135deg, var(--color-success), #059669);
  color: var(--color-white);
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.btn-guardar-ruta:hover {
  background: linear-gradient(135deg, #059669, #047857);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

.btn-guardar-ruta:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

/* Botón Cancelar */
.btn-cancelar-ruta {
  background: linear-gradient(135deg, var(--color-gray), #7da0d1);
  color: var(--color-red);
  box-shadow: 0 2px 4px rgba(111, 137, 173, 0.2);
}

.btn-cancelar-ruta:hover {
  background: linear-gradient(135deg, var(--color-dark), #0f172a);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(100, 116, 139, 0.3);
}

.btn-cancelar-ruta:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(100, 116, 139, 0.2);
}

/* Iconos de los botones */
.btn-guardar-ruta i,
.btn-cancelar-ruta i {
  font-size: 1rem;
}

/* ============ RESPONSIVE PARA RUTA EDITABLE ============ */

/* Tablets */
@media (max-width: 768px) {
  .ruta-container {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }

  .btn-editar-ruta {
    width: 100%;
    height: auto;
    padding: 0.75rem;
    justify-content: center;
    gap: 0.5rem;
  }

  .btn-editar-ruta::after {
    content: "Editar Ruta";
    font-size: 0.9rem;
    font-weight: 600;
  }

  .ruta-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .btn-guardar-ruta,
  .btn-cancelar-ruta {
    justify-content: center;
    padding: 0.75rem 1rem;
    width: 100%;
  }
}

/* Móviles */
@media (max-width: 480px) {
  .ruta-textarea {
    font-size: 0.8rem;
    min-height: 80px;
    padding: 0.5rem;
  }

  .btn-guardar-ruta,
  .btn-cancelar-ruta {
    font-size: 0.8rem;
    padding: 0.6rem 0.8rem;
  }

  .btn-guardar-ruta i,
  .btn-cancelar-ruta i {
    font-size: 0.9rem;
  }

  .ruta-actions {
    gap: 0.4rem;
  }
}

/* ============ ANIMACIONES Y EFECTOS ============ */

/* Animación de entrada del modo edición */
.ruta-editable {
  animation: slideInEdit 0.3s ease-out;
}

@keyframes slideInEdit {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Efecto de loading en botón guardar */
.btn-guardar-ruta.loading {
  position: relative;
  color: transparent;
  pointer-events: none;
}

.btn-guardar-ruta.loading::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid var(--color-white);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: translate(-50%, -50%) rotate(0deg); }
  100% { transform: translate(-50%, -50%) rotate(360deg); }
}

/* Efecto de hover en textarea */
.ruta-textarea:hover {
  border-color: var(--color-primary-light);
}

/* Estados de validación */
.ruta-textarea.error {
  border-color: var(--color-danger);
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.ruta-textarea.success {
  border-color: var(--color-success);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

/* ============ MODO OSCURO (OPCIONAL) ============ */
@media (prefers-color-scheme: dark) {
  .ruta-texto {
    background: #1e293b;
    border-color: #374151;
    color: #e2e8f0;
  }

  .ruta-textarea {
    background: #1e293b;
    border-color: #374151;
    color: #e2e8f0;
  }

  .ruta-textarea:focus {
    border-color: var(--color-primary-light);
    background: #0f172a;
  }
}


/* ============ RESPONSIVE OPTIMIZADO ============ */
@media (max-width: 768px) {
  .archivo-item {
    grid-template-columns: 1fr;
    gap: 0.6rem;
    padding: 0.7rem;
  }

  .archivo-item.nivel-1,
  .archivo-item.nivel-2,
  .archivo-item.nivel-3,
  .archivo-item.nivel-4 {
    grid-template-columns: 1fr;
  }

  .archivo-status {
    width: auto;
    flex-direction: row;
    gap: 0.5rem;
  }

  .archivo-calificacion {
    width: auto;
    max-width: none;
  }

  .archivo-acciones {
    justify-content: center;
    width: auto;
    gap: 0.5rem;
  }

  .header-info {
    flex-direction: column;
    align-items: flex-start;
  }

  .filters-container {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box {
    min-width: auto;
  }

  .stats-cards {
    grid-template-columns: 1fr 1fr;
  }

  .directorio-content,
  .subdirectorio-content {
    flex-wrap: wrap;
  }

  .directorio-actions,
  .subdirectorio-actions {
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-left: 0;
    margin-top: 0.5rem;
    width: 100%;
    justify-content: flex-end;
  }

  .modal-content {
    margin: 1rem;
    max-width: none;
  }

  .modal-footer {
    flex-direction: column;
  }

  .notification {
    bottom: 1rem;
    right: 1rem;
    left: 1rem;
    max-width: none;
  }

  .directorio-children {
    padding: 1rem 1rem 1rem 1.5rem;
  }

  .subdirectorio-children.nivel-1 {
    padding: 1rem 1rem 1rem 1.5rem;
  }

  .subdirectorio-children.nivel-2 {
    padding: 0.75rem 0.75rem 0.75rem 1rem;
  }

  .subdirectorio-children.nivel-3 {
    padding: 0.75rem 0.75rem 0.75rem 1rem;
  }

  .subdirectorio-children.nivel-4 {
    padding: 0.5rem 0.5rem 0.5rem 0.75rem;
  }
}

@media (max-width: 480px) {
  .archivo-item,
  .archivo-item.nivel-1,
  .archivo-item.nivel-2,
  .archivo-item.nivel-3,
  .archivo-item.nivel-4 {
    padding: 0.5rem;
    gap: 0.4rem;
  }

  .archivo-acciones {
    gap: 0.3rem;
  }
  
  .btn-accion {
    width: 28px;
    height: 28px;
    padding: 0.35rem;
  }
  
  .btn-accion i {
    font-size: 0.7rem;
  }

  .stats-cards {
    grid-template-columns: 1fr;
  }

  .page-header {
    padding: 1rem 1.5rem;
  }

  .main-content {
    padding: 0 1rem;
  }

  .tree-container {
    padding: 1rem;
  }

  .directorio-header.nivel-0,
  .subdirectorio-header.nivel-1 {
    padding: 1rem;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .subdirectorio-header.nivel-2,
  .subdirectorio-header.nivel-3 {
    padding: 0.5rem 0.75rem;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .directorio-content,
  .subdirectorio-content {
    width: 100%;
  }

  .directorio-actions,
  .subdirectorio-actions {
    width: 100%;
    justify-content: flex-start;
    margin-left: 0;
    margin-top: 0;
  }

  .directorio-children {
    padding: 1rem 0.5rem 1rem 1rem;
  }

  .subdirectorio-children.nivel-1 {
    padding: 0.75rem 0.5rem 0.75rem 1rem;
  }

  .subdirectorio-children.nivel-2 {
    padding: 0.5rem 0.25rem 0.5rem 0.75rem;
  }

  .subdirectorio-children.nivel-3 {
    padding: 0.5rem 0.25rem 0.5rem 0.75rem;
  }

  .folder-icon.nivel-0 i {
    width: 40px;
    height: 40px;
    font-size: 1.8rem;
  }

  .folder-icon.nivel-1 i {
    width: 36px;
    height: 36px;
    font-size: 1.6rem;
  }

  .folder-icon.nivel-2 i {
    width: 32px;
    height: 32px;
    font-size: 1.4rem;
  }

  .folder-icon.nivel-3 i {
    width: 32px;
    height: 32px;
    font-size: 1.4rem;
  }
}

/* ============ CALIFICACIÓN MASIVA STYLES ============ */
.calificacion-masiva-section {
  padding: 0 1rem;
  margin-bottom: 1rem;
}

/* Contenedor de botones de Super Admin */
.super-admin-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

/* Botón de Depuración */
.btn-depuracion {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

.btn-depuracion:hover:not(:disabled) {
  background: linear-gradient(135deg, #b91c1c, #991b1b);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(220, 38, 38, 0.4);
}

.btn-depuracion:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Botón de depuración de directorios */
.btn-depuracion-dirs {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, #ea580c, #c2410c);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(234, 88, 12, 0.3);
}

.btn-depuracion-dirs:hover:not(:disabled) {
  background: linear-gradient(135deg, #c2410c, #9a3412);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(234, 88, 12, 0.4);
}

.btn-depuracion-dirs:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-toggle-masivo {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, #7c3aed, #6d28d9);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
}

.btn-toggle-masivo:hover {
  background: linear-gradient(135deg, #6d28d9, #5b21b6);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(124, 58, 237, 0.4);
}

.btn-toggle-masivo.activo {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

.btn-toggle-masivo.activo:hover {
  background: linear-gradient(135deg, #b91c1c, #991b1b);
}

.btn-toggle-masivo:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.panel-calificacion-masiva {
  margin-top: 1rem;
  background: linear-gradient(135deg, #faf5ff, #f3e8ff);
  border: 2px solid #7c3aed;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 6px 20px rgba(124, 58, 237, 0.15);
}

.panel-calificacion-masiva .panel-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, #7c3aed, #6d28d9);
  color: white;
}

.panel-calificacion-masiva .panel-header i {
  font-size: 1.5rem;
}

.panel-calificacion-masiva .panel-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.panel-calificacion-masiva .panel-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.filtro-masivo-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filtro-masivo-group > label {
  font-weight: 600;
  color: #5b21b6;
  font-size: 0.9rem;
}

.radio-options {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  cursor: pointer;
  font-size: 0.9rem;
  color: #374151;
}

.radio-option input[type="radio"] {
  accent-color: #7c3aed;
  width: 16px;
  height: 16px;
}

.calificacion-select-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.calificacion-select-group > label {
  font-weight: 600;
  color: #5b21b6;
  font-size: 0.9rem;
}

.select-calificacion-masiva {
  padding: 0.6rem 1rem;
  border: 2px solid #d8b4fe;
  border-radius: 8px;
  font-size: 0.9rem;
  background: white;
  cursor: pointer;
  transition: border-color 0.2s ease;
  max-width: 100%;
}

.select-calificacion-masiva:focus {
  outline: none;
  border-color: #7c3aed;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2);
}

.contador-seleccionados {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #ede9fe;
  border-radius: 8px;
  font-size: 0.95rem;
}

.contador-seleccionados i {
  color: #7c3aed;
  font-size: 1.3rem;
}

.contador-seleccionados .de-total {
  color: #6b7280;
  font-size: 0.85rem;
}

.botones-seleccion {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.btn-seleccion {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  background: white;
  color: #7c3aed;
  border: 2px solid #d8b4fe;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-seleccion:hover:not(:disabled) {
  background: #f3e8ff;
  border-color: #7c3aed;
}

.btn-seleccion:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-seleccion i {
  font-size: 1rem;
}

.botones-accion-masiva {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.btn-aplicar-masivo {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-aplicar-masivo:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669, #047857);
  transform: translateY(-2px);
}

.btn-aplicar-masivo:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-restaurar {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.btn-restaurar:hover:not(:disabled) {
  background: linear-gradient(135deg, #d97706, #b45309);
  transform: translateY(-2px);
}

.btn-restaurar:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.info-ultimo-lote {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1rem;
  background: #fef3c7;
  border-radius: 6px;
  font-size: 0.85rem;
  color: #92400e;
}

.info-ultimo-lote i {
  font-size: 1.1rem;
}

.info-filtro-masivo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1rem;
  background: #dbeafe;
  border-radius: 6px;
  font-size: 0.85rem;
  color: #1e40af;
}

.info-filtro-masivo i {
  font-size: 1.1rem;
  color: #3b82f6;
}

/* Checkboxes en directorios y archivos */
.checkbox-masivo,
.checkbox-archivo-masivo {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.5rem;
}

.checkbox-directorio,
.checkbox-archivo {
  width: 18px;
  height: 18px;
  accent-color: #7c3aed;
  cursor: pointer;
}

.checkbox-directorio:indeterminate {
  accent-color: #a78bfa;
}

/* Archivo seleccionado visualmente */
.archivo-item.seleccionado-masivo {
  background-color: #ede9fe !important;
  border-left: 4px solid #7c3aed !important;
}

/* Modal de confirmación masiva */
.confirmacion-masiva-modal {
  max-width: 500px;
}

.confirmacion-masiva-modal .modal-header.warning {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.confirmacion-mensaje {
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.confirmacion-detalles {
  background: #f3f4f6;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.confirmacion-detalles p {
  margin: 0.5rem 0;
  font-size: 0.95rem;
}

.confirmacion-advertencia {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #dbeafe;
  border-radius: 6px;
  color: #1e40af;
  font-size: 0.9rem;
}

.confirmacion-advertencia i {
  color: #3b82f6;
}

.btn-cancelar {
  padding: 0.75rem 1.5rem;
  background: #e5e7eb;
  color: #374151;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.95rem;
  transition: background 0.2s ease;
}

.btn-cancelar:hover {
  background: #d1d5db;
}

.btn-confirmar {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.btn-confirmar:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669, #047857);
}

.btn-confirmar:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive para calificación masiva */
@media (max-width: 768px) {
  .panel-calificacion-masiva .panel-body {
    padding: 1rem;
  }

  .radio-options {
    flex-direction: column;
    gap: 0.5rem;
  }

  .botones-seleccion,
  .botones-accion-masiva {
    flex-direction: column;
  }

  .btn-aplicar-masivo,
  .btn-restaurar,
  .btn-seleccion {
    width: 100%;
    justify-content: center;
  }
}

/* ============ MODAL DE DEPURACIÓN ============ */
.depuracion-modal {
  max-width: 700px;
  width: 95%;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
}

.depuracion-modal .modal-header.success {
  background: linear-gradient(135deg, #10b981, #059669);
}

.depuracion-modal .modal-header.warning {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.depuracion-modal .modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

/* Resumen de verificación */
.verificacion-resumen {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.resumen-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.resumen-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  border-radius: 10px;
  text-align: center;
}

.resumen-stat.total {
  background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
}

.resumen-stat.existentes {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
}

.resumen-stat.inexistentes {
  background: linear-gradient(135deg, #fee2e2, #fecaca);
}

.resumen-stat.porcentaje {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
}

.resumen-stat .stat-number {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e293b;
}

.resumen-stat .stat-label {
  font-size: 0.8rem;
  color: #64748b;
  font-weight: 500;
  margin-top: 0.25rem;
}

/* Mensajes */
.mensaje-exito,
.mensaje-advertencia {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-radius: 10px;
}

.mensaje-exito {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  border: 1px solid #10b981;
}

.mensaje-exito i {
  color: #059669;
  font-size: 1.5rem;
}

.mensaje-advertencia {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  border: 1px solid #f59e0b;
}

.mensaje-advertencia i {
  color: #d97706;
  font-size: 1.5rem;
}

.mensaje-exito p,
.mensaje-advertencia p {
  margin: 0;
  font-size: 0.95rem;
}

/* Lista de archivos inexistentes */
.lista-inexistentes-container {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
}

.lista-inexistentes-container h4 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  padding: 0.75rem 1rem;
  background: #f1f5f9;
  font-size: 0.9rem;
  font-weight: 600;
  color: #475569;
}

.lista-inexistentes {
  max-height: 250px;
  overflow-y: auto;
}

.archivo-inexistente {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  transition: background-color 0.2s;
}

.archivo-inexistente:hover {
  background: #fef2f2;
}

.archivo-inexistente:last-child {
  border-bottom: none;
}

.archivo-inexistente.seleccionado {
  background: #fef3c7;
  border-left: 3px solid #f59e0b;
}

.archivo-inexistente.seleccionado:hover {
  background: #fde68a;
}

.checkbox-depuracion {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #f59e0b;
  flex-shrink: 0;
  margin-right: 0.75rem;
}

.btn-seleccion-depuracion {
  padding: 0.4rem 0.75rem;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #475569;
}

.btn-seleccion-depuracion:hover {
  background: #e2e8f0;
  border-color: #94a3b8;
}

/* Modal de confirmación de depuración */
.confirmacion-modal {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  max-width: 450px;
  width: 95%;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  animation: modalSlideIn 0.3s ease-out;
}

.confirmacion-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.confirmacion-header h3 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
  color: #dc2626;
  font-size: 1.25rem;
}

.confirmacion-header h3 i {
  font-size: 1.5rem;
}

.confirmacion-body {
  padding: 1.5rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 12px;
  margin-bottom: 1.5rem;
}

.confirmacion-body p {
  margin: 0 0 0.75rem 0;
  color: #7f1d1d;
  line-height: 1.6;
}

.confirmacion-body p:last-child {
  margin-bottom: 0;
  font-weight: 600;
}

.confirmacion-footer {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn-cancelar {
  padding: 0.75rem 1.5rem;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  color: #475569;
}

.btn-cancelar:hover {
  background: #e2e8f0;
  border-color: #94a3b8;
}

.btn-eliminar-definitivo {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-eliminar-definitivo:hover:not(:disabled) {
  background: linear-gradient(135deg, #b91c1c, #991b1b);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(185, 28, 28, 0.4);
}

.btn-eliminar-definitivo:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Contenedor de selección múltiple */
.seleccion-multiple {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  padding: 0.5rem;
  background: #f8fafc;
  border-radius: 6px;
}

.seleccion-multiple span {
  color: #64748b;
  font-size: 0.85rem;
}

/* Estilos específicos para archivos en el modal de depuración */
.lista-inexistentes .archivo-info-depuracion {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
  min-width: 0;
}

.lista-inexistentes .archivo-nombre-depuracion {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.9rem;
}

.lista-inexistentes .archivo-ruta-depuracion {
  display: flex;
  align-items: flex-start;
  gap: 0.35rem;
  font-size: 0.75rem;
  color: #64748b;
  word-break: break-all;
}

.lista-inexistentes .ruta-icon {
  font-size: 0.9rem !important;
  color: #94a3b8;
  flex-shrink: 0;
  line-height: 1;
}

.lista-inexistentes .archivo-fecha-depuracion {
  font-size: 0.75rem;
  color: #94a3b8;
  white-space: nowrap;
}

/* ============ ESTILOS DE DEPURACIÓN DE DIRECTORIOS ============ */

.lista-dirs-inexistentes .directorio-inexistente {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.lista-dirs-inexistentes .directorio-inexistente:hover {
  background: #f8fafc;
  border-color: #ea580c;
}

.lista-dirs-inexistentes .directorio-inexistente.seleccionado {
  background: #fff7ed;
  border-color: #ea580c;
  box-shadow: 0 0 0 2px rgba(234, 88, 12, 0.1);
}

.directorio-info-depuracion {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1;
  min-width: 0;
}

.directorio-nombre-depuracion {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #1e293b;
  font-size: 0.95rem;
  word-break: break-word;
}

.directorio-nombre-depuracion i {
  font-size: 1.1rem;
  color: #ea580c;
}

.directorio-ruta-depuracion {
  font-size: 0.75rem;
  color: #64748b;
  padding-left: 1.6rem;
  word-break: break-all;
  line-height: 1.4;
}

.directorio-meta-depuracion {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding-left: 1.6rem;
  margin-top: 0.25rem;
}

.directorio-meta-depuracion .meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #64748b;
}

.directorio-meta-depuracion .meta-item i {
  font-size: 0.85rem;
}

.directorio-meta-depuracion .meta-item.meta-warning {
  color: #ea580c;
  font-weight: 600;
}

.directorio-meta-depuracion .meta-item.meta-ok {
  color: #16a34a;
}

/* Advertencia de archivos en cascada */
.advertencia-cascada {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background: linear-gradient(135deg, #fff7ed, #ffedd5);
  border: 1px solid #fed7aa;
  border-radius: 8px;
  margin-top: 1rem;
}

.advertencia-cascada i {
  font-size: 1.5rem;
  color: #ea580c;
  flex-shrink: 0;
}

.advertencia-cascada p {
  margin: 0;
  color: #9a3412;
  font-size: 0.9rem;
  line-height: 1.5;
}

/* Estilos para modal unificado */
.depuracion-unificada {
  max-width: 900px;
}

.resumen-stats-unificado {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.resumen-stat.directorios-stat {
  border-color: #ea580c;
}

.resumen-stat.directorios-stat .stat-number {
  color: #ea580c;
}

.resumen-stat.archivos-stat {
  border-color: #dc2626;
}

.resumen-stat.archivos-stat .stat-number {
  color: #dc2626;
}

.seccion-depuracion {
  margin-top: 1.5rem;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fafafa;
}

.seccion-depuracion .lista-header {
  margin-bottom: 1rem;
}

.seccion-depuracion .lista-header h4 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 1rem;
  color: #1e293b;
}

.seccion-directorios {
  border-color: #fed7aa;
  background: linear-gradient(135deg, #fffbeb, #fef3c7);
}

.seccion-directorios .lista-header h4 {
  color: #92400e;
}

.seccion-archivos {
  border-color: #fecaca;
  background: linear-gradient(135deg, #fef2f2, #fee2e2);
}

.seccion-archivos .lista-header h4 {
  color: #991b1b;
}

.lista-truncada {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #f8fafc;
  color: #64748b;
  font-size: 0.85rem;
  font-style: italic;
}

/* Advertencia final */
.advertencia-final {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  background: linear-gradient(135deg, #fee2e2, #fecaca);
  border: 1px solid #ef4444;
  border-radius: 10px;
}

.advertencia-final i {
  color: #dc2626;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.advertencia-final p {
  margin: 0;
  font-size: 0.9rem;
  color: #7f1d1d;
}

/* Botón de depuración en modal */
.btn-depurar-confirmar {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-depurar-confirmar:hover:not(:disabled) {
  background: linear-gradient(135deg, #b91c1c, #991b1b);
  transform: translateY(-1px);
}

.btn-depurar-confirmar:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive modal depuración */
@media (max-width: 600px) {
  .resumen-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .depuracion-modal {
    max-height: 90vh;
  }

  .super-admin-actions {
    flex-direction: column;
  }

  .btn-depuracion,
  .btn-depuracion-dirs {
    width: 100%;
    justify-content: center;
  }
}

/* ============ ESTILOS DE AUDITORÍA ============ */
.audit-section {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.audit-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1rem;
}

.audit-header i {
  color: #1976d2;
  font-size: 1.2rem;
}

.audit-upload-info {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  border-left: 4px solid #1976d2;
}

.upload-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #1565c0;
  margin-bottom: 0.5rem;
}

.upload-badge i {
  font-size: 1.2rem;
}

.upload-details {
  font-size: 0.9rem;
  color: #333;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.upload-details strong {
  color: #1565c0;
}

.audit-loading,
.audit-empty {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #666;
  font-style: italic;
  padding: 0.5rem 0;
}

.audit-loading i,
.audit-empty i {
  font-size: 1rem;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.audit-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 200px;
  overflow-y: auto;
}

.audit-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #ccc;
}

.audit-item:hover {
  background: #f0f0f0;
}

.audit-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e0e0e0;
  flex-shrink: 0;
}

.audit-icon i {
  font-size: 1rem;
  color: #666;
}

.audit-icon.upload {
  background: #e3f2fd;
  border-color: #1976d2;
}

.audit-icon.upload i {
  color: #1976d2;
}

.audit-icon.download {
  background: #e8f5e9;
}

.audit-icon.download i {
  color: #388e3c;
}

.audit-icon.delete {
  background: #ffebee;
}

.audit-icon.delete i {
  color: #d32f2f;
}

.audit-icon.rename,
.audit-icon.modify {
  background: #fff3e0;
}

.audit-icon.rename i,
.audit-icon.modify i {
  color: #f57c00;
}

.audit-content {
  flex: 1;
  min-width: 0;
}

.audit-action {
  font-weight: 600;
  color: #333;
  margin-bottom: 0.25rem;
}

.audit-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
  color: #666;
}

.audit-user {
  font-weight: 500;
}

.audit-date {
  color: #888;
}

.audit-platform {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #888;
  margin-top: 0.25rem;
}

.audit-platform i {
  font-size: 0.9rem;
}

/* Item con upload tiene borde azul */
.audit-item:has(.audit-icon.upload) {
  border-left-color: #1976d2;
}

.audit-item:has(.audit-icon.download) {
  border-left-color: #388e3c;
}

.audit-item:has(.audit-icon.delete) {
  border-left-color: #d32f2f;
}

.audit-item:has(.audit-icon.rename),
.audit-item:has(.audit-icon.modify) {
  border-left-color: #f57c00;
}

/* ================================= */
/* Modal de Eliminación de Archivos  */
/* ================================= */

.delete-file-modal {
  max-width: 550px;
}

.delete-file-modal .modal-header.danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

.delete-file-modal .modal-header.danger h3 {
  color: white;
}

.delete-file-modal .modal-header.danger .modal-close {
  color: white;
}

.file-delete-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.file-icon-large {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.file-icon-large i {
  font-size: 28px;
  color: #4f46e5;
}

.file-details {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.file-details .file-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 1rem;
  margin-bottom: 0.25rem;
  word-break: break-word;
}

.file-details .file-path {
  font-size: 0.75rem;
  color: #64748b;
  font-family: 'Consolas', monospace;
  word-break: break-all;
}

.delete-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.delete-options h4 {
  font-size: 0.95rem;
  color: #475569;
  margin-bottom: 0.5rem;
}

.delete-option {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #fff;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.delete-option:hover {
  border-color: #94a3b8;
  background: #f8fafc;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.delete-option.danger:hover {
  border-color: #ef4444;
  background: #fef2f2;
}

.option-icon {
  width: 45px;
  height: 45px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.option-icon.warning {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
}

.option-icon.warning i {
  color: #d97706;
  font-size: 24px;
}

.option-icon.danger {
  background: linear-gradient(135deg, #fee2e2, #fecaca);
}

.option-icon.danger i {
  color: #dc2626;
  font-size: 24px;
}

.option-content {
  flex: 1;
  min-width: 0;
}

.option-title {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.option-description {
  font-size: 0.8rem;
  color: #64748b;
  line-height: 1.4;
}

.delete-option button {
  flex-shrink: 0;
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.delete-option button i {
  font-size: 18px;
}

.delete-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  background: #f1f5f9;
  border-radius: 10px;
  margin-top: 1rem;
}

.delete-loading .spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e2e8f0;
  border-top-color: #ef4444;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.delete-loading p {
  color: #64748b;
  font-weight: 500;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>