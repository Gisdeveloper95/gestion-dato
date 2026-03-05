<template>
  <div class="home-page">
 <!-- Carrusel principal -->
    <section class="hero-carousel-section">
      <div class="container">
        <div class="hero-carousel-container">
          <button class="carousel-control prev" @click="prevHeroImage">
            <i class="material-icons">chevron_left</i>
          </button>
          
          <div class="carousel-images">
            <div 
              v-for="(imagen, index) in imagenesHero" 
              :key="index"
              class="carousel-item"
              :class="{ active: index === imagenHeroActiva }"
            >
              <img :src="imagen.url" :alt="imagen.titulo" />
              <div class="carousel-caption">
                <h3>{{ imagen.titulo }}</h3>
                <p>{{ imagen.descripcion }}</p>
              </div>
            </div>
          </div>
          
          <button class="carousel-control next" @click="nextHeroImage">
            <i class="material-icons">chevron_right</i>
          </button>
        </div>
        
        <div class="carousel-indicators">
          <button 
            v-for="(imagen, index) in imagenesHero" 
            :key="index"
            class="indicator"
            :class="{ active: index === imagenHeroActiva }"
            @click="setActiveHeroImage(index)"
          ></button>
        </div>
      </div>
    </section>
    
    <!-- Sección principal con estadísticas y notificaciones -->
    <section class="main-section">
      <div class="container">
        <div class="dashboard-grid">
          <!-- Estadísticas resumidas -->
          <div class="stats-card">
            <div class="stats-header">
              <h2>Estadísticas Generales</h2>
              <button @click="cargarEstadisticas" :disabled="cargandoEstadisticas">
                <i class="material-icons">refresh</i>
              </button>
            </div>
            
            <div v-if="cargandoEstadisticas" class="loading-stats">
              <div class="spinner"></div>
              <span>Cargando estadísticas...</span>
            </div>
            
            <div v-else-if="errorEstadisticas" class="error-stats">
              <i class="material-icons">error</i>
              <span>{{ errorEstadisticas }}</span>
              <button @click="cargarEstadisticas">Reintentar</button>
            </div>
            
            <div class="stats-grid">
              <!-- Municipios Pre -->
              <router-link to="/disposicion-informacion/municipios" class="stat-item clickable">
                <div class="stat-value">{{ estadisticas.total_municipios || 0 }}</div>
                <div class="stat-label">Municipios Pre</div>
                <i class="material-icons stat-icon">location_city</i>
              </router-link>
              
              <!-- Municipios Post -->
              <router-link to="/disposicion-informacion/productos" class="stat-item clickable">
                <div class="stat-value">{{ estadisticas.total_municipios_post || 0 }}</div>
                <div class="stat-label">Municipios Post</div>
                <i class="material-icons stat-icon">inventory_2</i>
              </router-link>
              
              <!-- Archivos Pre -->
              <router-link to="/disposicion-informacion/insumos" class="stat-item clickable">
                <div class="stat-value">{{ estadisticas.total_archivos_pre || 0 }}</div>
                <div class="stat-label">Archivos Pre</div>
                <i class="material-icons stat-icon">folder</i>
              </router-link>
              
              <!-- Archivos Post -->
              <router-link to="/disposicion-informacion/productos" class="stat-item clickable">
                <div class="stat-value">{{ estadisticas.total_archivos_post || 0 }}</div>
                <div class="stat-label">Archivos Post</div>
                <i class="material-icons stat-icon">inventory_2</i>
              </router-link>
              
              <!-- Territoriales -->
              <router-link to="/disposicion-informacion/profesionales" class="stat-item clickable">
                <div class="stat-value">{{ estadisticas.total_territoriales || 0 }}</div>
                <div class="stat-label">Territoriales</div>
                <i class="material-icons stat-icon">engineering</i>
              </router-link>
              
              <!-- Enlaces -->
              <router-link to="/disposicion-informacion/profesionales" class="stat-item clickable">
                <div class="stat-value">{{ estadisticas.total_enlaces || 0 }}</div>
                <div class="stat-label">Enlaces</div>
                <i class="material-icons stat-icon">people</i>
              </router-link>
              
              <!-- Municipios Sin Insumos -->
              <router-link to="/disposicion-informacion/municipios" class="stat-item clickable">
                <div class="stat-value">{{ estadisticas.total_municipios_sin_insumos || 0 }}</div>
                <div class="stat-label">Municipios Sin Insumos</div>
                <i class="material-icons stat-icon">warning</i>
              </router-link>
            </div>
            
            <div class="stats-footer">
              <router-link to="/Indicadores" class="link-more">
                Ver más en Indicadores
                <i class="material-icons">pie_chart</i>
              </router-link>
            </div>
          </div>
          
          <!-- Notificaciones recientes -->
          <div class="notificaciones-card">
            <div class="header">
              <h2 class="title">
                <i class="material-icons">notifications</i>
                Notificaciones Recientes
              </h2>
              <div class="actions">
                <!-- Indicador de permisos -->
                <div class="permisos-indicador" :class="{ 
                  'permisos-super-admin': permisoUsuario.esSuperAdmin,
                  'permisos-completos': permisoUsuario.puedeVerArchivos,
                  'permisos-limitados': permisoUsuario.puedeVerArchivosMunicipio,
                  'sin-permisos': !authStore.isAuthenticated
                }">
                  <i class="material-icons">{{ 
                    permisoUsuario.esSuperAdmin ? 'admin_panel_settings' :
                    permisoUsuario.puedeVerArchivos ? 'verified' :
                    permisoUsuario.puedeVerArchivosMunicipio ? 'badge' :
                    'person'
                  }}</i>
                  <span class="tooltip">{{ permisoUsuario.mensajeAcceso }}</span>
                </div>
                
                <button class="refresh-button" @click="cargarNotificacionesManual" :disabled="cargandoNotificaciones">
                  <i class="material-icons">refresh</i>
                </button>
              </div>
            </div>
            
            <div v-if="cargandoNotificaciones && notificacionesPre.length === 0" class="loading">
              <div class="spinner"></div>
              <span>Cargando notificaciones...</span>
            </div>
            
            <div v-else-if="errorNotificaciones" class="error-message">
              <i class="material-icons">error</i>
              <span>{{ errorNotificaciones }}</span>
              <button @click="cargarNotificacionesManual">Reintentar</button>
            </div>
            
            <div v-else-if="notificacionesPre.length === 0 && notificacionesPost.length === 0" class="empty-message">
              <i class="material-icons">notifications_none</i>
              <span>No hay notificaciones en las últimas 24 horas</span>
            </div>
            
            <!-- Mostrar notificaciones de hoy con scroll completo y colores diferenciados -->
            <div v-else-if="notificacionesHoy.length > 0" class="notificaciones-hoy-container">
              <h3>Notificaciones de las últimas 24 horas ({{ notificacionesHoy.length }})</h3>
              <div class="notificaciones-scroll">
                <ul class="notificaciones-lista">
                  <li
                    v-for="(notificacion, index) in notificacionesFiltradas" :key="`hoy-${index}`"
                    :class="{ 
                      'no-leida': !notificacion.leido,
                      'notificacion-pre': esTipoPreoperacion(notificacion),
                      'notificacion-post': esTipoPostoperacion(notificacion)
                    }"
                    @click="verDetalleNotificacion(notificacion)"
                    class="clickable-notification"
                  >
                    <div class="notificacion-icon" :class="{ 
                      'icon-pre': esTipoPreoperacion(notificacion),
                      'icon-post': esTipoPostoperacion(notificacion)
                    }">
                      <i class="material-icons">{{ getNotificationIcon(notificacion.tipo_entidad) }}</i>
                    </div>
                    <div class="notificacion-content">
                      <div class="notificacion-title">
                        {{ getTipoNotificacion(notificacion) }}
                        <span v-if="!notificacion.leido" class="badge">Nueva</span>
                      </div>
                      <div class="notificacion-meta">
                        <span class="municipio" v-if="getMunicipio(notificacion)">
                          <i class="material-icons">location_city</i>
                          {{ getMunicipio(notificacion) }}
                        </span>
                        <span class="tiempo">{{ formatearTiempo(notificacion.fecha_cambio) }}</span>
                        <span class="usuario" v-if="getUsuario(notificacion)">
                          <i class="material-icons">person</i>
                          {{ getUsuario(notificacion) }}
                        </span>
                        <span class="tipo" :class="{ 
                          'tag-pre': esTipoPreoperacion(notificacion),
                          'tag-post': esTipoPostoperacion(notificacion)
                        }">
                          {{ esTipoPreoperacion(notificacion) ? 'Preoperación' : 'Postoperación' }}
                        </span>
                      </div>
                      <div class="notificacion-details" v-if="getDetallesNotificacion(notificacion)">
                        {{ getDetallesNotificacion(notificacion) }}
                      </div>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
            
            <!-- Mostrar notificaciones recientes si no hay de hoy -->
            <div v-else class="notificaciones-scroll">
              <ul class="notificaciones-lista">
                <li
                  v-for="(notificacion, index) in [...notificacionesPre, ...notificacionesPost].sort((a, b) => 
                    new Date(b.fecha_cambio).getTime() - new Date(a.fecha_cambio).getTime()
                  )"
                  :key="`reciente-${index}`"
                  :class="{ 
                    'no-leida': !notificacion.leido,
                    'notificacion-pre': esTipoPreoperacion(notificacion),
                    'notificacion-post': esTipoPostoperacion(notificacion)
                  }"
                  @click="verDetalleNotificacion(notificacion)"
                  class="clickable-notification"
                >
                  <div class="notificacion-icon" :class="{ 
                    'icon-pre': esTipoPreoperacion(notificacion),
                    'icon-post': esTipoPostoperacion(notificacion)
                  }">
                    <i class="material-icons">{{ getNotificationIcon(notificacion.tipo_entidad) }}</i>
                  </div>
                  <div class="notificacion-content">
                    <div class="notificacion-title">
                      {{ getTipoNotificacion(notificacion) }}
                      <span v-if="!notificacion.leido" class="badge">Nueva</span>
                    </div>
                    <div class="notificacion-meta">
                      <span class="municipio" v-if="getMunicipio(notificacion)">
                        <i class="material-icons">location_city</i>
                        {{ getMunicipio(notificacion) }}
                      </span>
                      <span class="tiempo">{{ formatearTiempo(notificacion.fecha_cambio) }}</span>
                      <span class="usuario" v-if="getUsuario(notificacion)">
                        <i class="material-icons">person</i>
                        {{ getUsuario(notificacion) }}
                      </span>
                      <span class="tipo" :class="{ 
                        'tag-pre': esTipoPreoperacion(notificacion),
                        'tag-post': esTipoPostoperacion(notificacion)
                      }">
                        {{ esTipoPreoperacion(notificacion) ? 'Preoperación' : 'Postoperación' }}
                      </span>
                    </div>
                    <div class="notificacion-details" v-if="getDetallesNotificacion(notificacion)">
                      {{ getDetallesNotificacion(notificacion) }}
                    </div>
                  </div>
                </li>
              </ul>
            </div>
            
            <div class="ver-mas">
              <router-link to="/notificaciones" class="link-more">
                Ver todas las notificaciones 
                <i class="material-icons">arrow_forward</i>
              </router-link>
            </div>
          </div>
          
          <!-- Sistemas de Calendarios Duales -->
          <div class="calendars-section">
            <div class="calendars-header">
              <h2 class="section-subtitle">Calendarios de Eventos y Notificaciones</h2>
              <div class="calendars-info">
                <i class="material-icons">info</i>
                <span>Los datos se cargan bajo demanda por mes para mejor rendimiento</span>
              </div>
            </div>
            
            <div class="calendars-container">
              <!-- Calendario Preoperación -->
              <div class="calendar-card pre-calendar" v-if="!mostrandoDetallesPre">
                <div class="calendar-header">
                  <h2>
                    <i class="material-icons pre-icon">event_note</i>
                    Calendario Preoperación
                    <!-- Indicador de carga -->
                    <div v-if="cargandoMesPre" class="loading-indicator-small">
                      <div class="spinner-small"></div>
                    </div>
                  </h2>
                  <div class="calendar-nav">
                    <button 
                      @click="mesAnteriorPre" 
                      :disabled="cargandoMesPre"
                      :class="{ 'loading': cargandoMesPre }"
                      title="Mes anterior"
                    >
                      <i class="material-icons">chevron_left</i>
                    </button>
                    <span class="month-year-display">{{ nombreMesPre }} {{ yearActualPre }}</span>
                    <button 
                      @click="mesSiguientePre"
                      :disabled="cargandoMesPre" 
                      :class="{ 'loading': cargandoMesPre }"
                      title="Mes siguiente"
                    >
                      <i class="material-icons">chevron_right</i>
                    </button>
                    <!-- Botón para ir a hoy -->
                    <button 
                      @click="irAMesActual" 
                      class="today-button"
                      :disabled="cargandoMesPre || cargandoMesPost"
                      title="Ir al mes actual"
                    >
                      <i class="material-icons">today</i>
                      Hoy
                    </button>
                    <div class="month-year-selector">
                      <div class="dropdown-container">
                        <button class="dropdown-trigger" @click="toggleMonthPicker('pre')">
                          {{ nombreMesPre }} {{ yearActualPre }}
                          <i class="material-icons">arrow_drop_down</i>
                        </button>
                        <div v-if="showMonthPicker === 'pre'" class="month-picker-popup pre-operacion">
                          <div class="year-selector">
                            <button @click="changeYear('pre', -1)">&laquo;</button>
                            <span>{{ yearActualPre }}</span>
                            <button @click="changeYear('pre', 1)">&raquo;</button>
                          </div>
                          <div class="month-grid">
                            <button 
                              v-for="(mes, index) in meses" 
                              :key="index"
                              @click="selectMonth('pre', index)"
                              :class="{ active: index === fechaActualPre.getMonth() }"
                            >
                              {{ mes }}
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Overlay de carga para el calendario -->
                <div v-if="cargandoMesPre" class="calendar-loading-overlay">
                  <div class="loading-content">
                    <div class="spinner"></div>
                    <span>Cargando {{ nombreMesPre }}...</span>
                  </div>
                </div>
                
                <div class="calendar-grid" :class="{ 'loading': cargandoMesPre }">
                  <div class="calendar-day-header" v-for="dia in diasSemana" :key="dia">{{ dia }}</div>
                  <div 
                    v-for="dia in diasCalendarioPre" 
                    :key="`pre-${formatDate(dia.fecha)}`" 
                    class="calendar-day" 
                    :class="{ 
                      'other-month': dia.otroMes, 
                      'today': dia.esHoy,
                      'has-events': dia.notificaciones && dia.notificaciones.length > 0,
                      'loading': cargandoMesPre
                    }"
                    @click="!cargandoMesPre && verDetallesDia(dia, 'pre')"
                    :style="{ 'pointer-events': cargandoMesPre ? 'none' : 'auto' }"
                  >
                    <span class="day-number">{{ dia.numero }}</span>
                    
                    <div v-if="dia.notificaciones && dia.notificaciones.length > 0" class="day-events">
                      <span class="notification-count">{{ dia.notificaciones.length }}</span>
                    </div>
                  </div>
                </div>
                
                <div class="calendar-footer">
                  <span class="events-tip">
                    <i class="material-icons">info</i>
                    Haga clic en un día para ver las notificaciones
                  </span>
                  <!-- Mostrar información de carga -->
                  <span v-if="cargandoMesPre" class="loading-info">
                    <i class="material-icons">hourglass_empty</i>
                    Cargando datos del mes...
                  </span>
                </div>
              </div>
              
              <!-- Vista detallada de notificaciones para Preoperación -->
              <div class="day-details pre-details" v-if="mostrandoDetallesPre">
                <div class="day-details-header">
                  <button class="back-button" @click="volverACalendarioPre">
                    <i class="material-icons">arrow_back</i>
                    Volver a Calendario
                  </button>
                  <h2>
                    <i class="material-icons pre-icon">event_note</i>
                    {{ formatearFecha(fechaSeleccionadaPre) }}
                  </h2>
                </div>
                
                <div class="day-details-content">
                  <div v-if="!notificacionesDiaPre.length" class="no-events">
                    <i class="material-icons">info</i>
                    <p>No hay notificaciones para este día en preoperación</p>
                  </div>
                  
                  <div v-else class="notifications-list">
                    <div 
                      v-for="(notificacion, index) in notificacionesDiaPre" 
                      :key="`notif-pre-${index}`" 
                      class="notification-item clickable-notification"
                      @click="verDetalleNotificacion(notificacion)"
                    >
                      <div class="notification-icon">
                        <i class="material-icons">{{ getNotificationIcon(notificacion.tipo_entidad) }}</i>
                      </div>
                      <div class="notification-content">
                        <div class="notification-title">
                          {{ getTipoNotificacion(notificacion) }}
                          <span class="notification-badge" v-if="!notificacion.leido">Nueva</span>
                        </div>
                        <div class="notification-time">{{ formatearTiempo(notificacion.fecha_cambio) }}</div>
                        <div class="notification-details">
                          <div v-if="getMunicipio(notificacion)">
                            <i class="material-icons">location_city</i>
                            {{ getMunicipio(notificacion) }}
                          </div>
                          <div v-if="getUsuario(notificacion)">
                            <i class="material-icons">person</i>
                            {{ getUsuario(notificacion) }}
                          </div>
                          <div v-if="getDetallesNotificacion(notificacion)">
                            <i class="material-icons">info</i>
                            {{ getDetallesNotificacion(notificacion) }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Calendario Postoperación -->
              <div class="calendar-card post-calendar" v-if="!mostrandoDetallesPost">
                <div class="calendar-header">
                  <h2>
                    <i class="material-icons post-icon">event_available</i>
                    Calendario Postoperación
                    <!-- Indicador de carga -->
                    <div v-if="cargandoMesPost" class="loading-indicator-small">
                      <div class="spinner-small"></div>
                    </div>
                  </h2>
                  <div class="calendar-nav">
                    <button 
                      @click="mesAnteriorPost"
                      :disabled="cargandoMesPost"
                      :class="{ 'loading': cargandoMesPost }"
                      title="Mes anterior"
                    >
                      <i class="material-icons">chevron_left</i>
                    </button>
                    <span class="month-year-display">{{ nombreMesPost }} {{ yearActualPost }}</span>
                    <button 
                      @click="mesSiguientePost"
                      :disabled="cargandoMesPost"
                      :class="{ 'loading': cargandoMesPost }"
                      title="Mes siguiente"
                    >
                      <i class="material-icons">chevron_right</i>
                    </button>
                    <!-- Botón para ir a hoy -->
                    <button 
                      @click="irAMesActual" 
                      class="today-button"
                      :disabled="cargandoMesPre || cargandoMesPost"
                      title="Ir al mes actual"
                    >
                      <i class="material-icons">today</i>
                      Hoy
                    </button>
                    <div class="month-year-selector">
                      <div class="dropdown-container">
                        <button class="dropdown-trigger" @click="toggleMonthPicker('post')">
                          {{ nombreMesPost }} {{ yearActualPost }}
                          <i class="material-icons">arrow_drop_down</i>
                        </button>
                        <div v-if="showMonthPicker === 'post'" class="month-picker-popup post-operacion">
                          <div class="year-selector">
                            <button @click="changeYear('post', -1)">&laquo;</button>
                            <span>{{ yearActualPost }}</span>
                            <button @click="changeYear('post', 1)">&raquo;</button>
                          </div>
                          <div class="month-grid">
                            <button 
                              v-for="(mes, index) in meses" 
                              :key="index"
                              @click="selectMonth('post', index)"
                              :class="{ active: index === fechaActualPost.getMonth() }"
                            >
                              {{ mes }}
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Overlay de carga para el calendario -->
                <div v-if="cargandoMesPost" class="calendar-loading-overlay">
                  <div class="loading-content">
                    <div class="spinner"></div>
                    <span>Cargando {{ nombreMesPost }}...</span>
                  </div>
                </div>
                
                <div class="calendar-grid" :class="{ 'loading': cargandoMesPost }">
                  <div class="calendar-day-header" v-for="dia in diasSemana" :key="dia">{{ dia }}</div>
                  <div 
                    v-for="dia in diasCalendarioPost" 
                    :key="`post-${formatDate(dia.fecha)}`" 
                    class="calendar-day" 
                    :class="{ 
                      'other-month': dia.otroMes, 
                      'today': dia.esHoy,
                      'has-events': dia.notificaciones && dia.notificaciones.length > 0,
                      'loading': cargandoMesPost
                    }"
                    @click="!cargandoMesPost && verDetallesDia(dia, 'post')"
                    :style="{ 'pointer-events': cargandoMesPost ? 'none' : 'auto' }"
                  >
                    <span class="day-number">{{ dia.numero }}</span>
                    
                    <div v-if="dia.notificaciones && dia.notificaciones.length > 0" class="day-events">
                      <span class="notification-count">{{ dia.notificaciones.length }}</span>
                    </div>
                  </div>
                </div>
                
                <div class="calendar-footer">
                  <span class="events-tip">
                    <i class="material-icons">info</i>
                    Haga clic en un día para ver las notificaciones
                  </span>
                  <!-- Mostrar información de carga -->
                  <span v-if="cargandoMesPost" class="loading-info">
                    <i class="material-icons">hourglass_empty</i>
                    Cargando datos del mes...
                  </span>
                </div>
              </div>
              
              <div class="day-details post-details" v-if="mostrandoDetallesPost">
                <div class="day-details-header">
                  <button class="back-button" @click="volverACalendarioPost">
                    <i class="material-icons">arrow_back</i>
                    Volver a Calendario
                  </button>
                  <h2>
                    <i class="material-icons post-icon">event_available</i>
                    {{ formatearFecha(fechaSeleccionadaPost) }}
                  </h2>
                </div>
                
                <div class="day-details-content">
                  <div v-if="!notificacionesDiaPost.length" class="no-events">
                    <i class="material-icons">info</i>
                    <p>No hay notificaciones para este día en postoperación</p>
                  </div>
                  
                  <div v-else class="notifications-list">
                    <div 
                      v-for="(notificacion, index) in notificacionesDiaPost" 
                      :key="`notif-post-${index}`" 
                      class="notification-item clickable-notification"
                      @click="verDetalleNotificacion(notificacion)"
                    >
                      <div class="notification-icon">
                        <i class="material-icons">{{ getNotificationIcon(notificacion.tipo_entidad) }}</i>
                      </div>
                      <div class="notification-content">
                        <div class="notification-title">
                          {{ getTipoNotificacion(notificacion) }}
                          <span class="notification-badge" v-if="!notificacion.leido">Nueva</span>
                        </div>
                        <div class="notification-time">{{ formatearTiempo(notificacion.fecha_cambio) }}</div>
                        <div class="notification-details">
                          <div v-if="getMunicipio(notificacion)">
                            <i class="material-icons">location_city</i>
                            {{ getMunicipio(notificacion) }}
                          </div>
                          <div v-if="getUsuario(notificacion)">
                            <i class="material-icons">person</i>
                            {{ getUsuario(notificacion) }}
                          </div>
                          <div v-if="getDetallesNotificacion(notificacion)">
                            <i class="material-icons">info</i>
                            {{ getDetallesNotificacion(notificacion) }}
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
      </div>
    </section>
    
    <!-- Visor de imágenes destacadas -->
    <section class="image-showcase">
      <div class="container">
        <h2 class="section-title">Imágenes Destacadas</h2>
        
        <div class="carousel-container">
          <button class="carousel-control prev" @click="prevImage">
            <i class="material-icons">chevron_left</i>
          </button>
          
          <div class="carousel-images">
            <div 
              v-for="(imagen, index) in imagenes" 
              :key="index"
              class="carousel-item"
              :class="{ active: index === imagenActiva }"
            >
              <img :src="imagen.url" :alt="imagen.titulo" />
              <div class="carousel-caption">
                <h3>{{ imagen.titulo }}</h3>
                <p>{{ imagen.descripcion }}</p>
              </div>
            </div>
          </div>
          
          <button class="carousel-control next" @click="nextImage">
            <i class="material-icons">chevron_right</i>
          </button>
        </div>
        
        <div class="carousel-indicators">
          <button 
            v-for="(imagen, index) in imagenes" 
            :key="index"
            class="indicator"
            :class="{ active: index === imagenActiva }"
            @click="setActiveImage(index)"
          ></button>
        </div>
      </div>
    </section>
    
    <!-- Enlaces rápidos -->
    <section class="quick-links">
      <div class="container">
        <h2 class="section-title">Enlaces Rápidos</h2>
        
        <div class="links-grid">
          <router-link to="/disposicion-informacion" class="link-card">
            <i class="material-icons">description</i>
            <h3>Disposición de Información</h3>
            <p>Gestiona la disposición de información por municipio y componente</p>
          </router-link>

          
          <router-link to="/indicadores" class="link-card">
            <i class="material-icons">pie_chart</i>
            <h3>Indicadores</h3>
            <p>Consulta indicadores de gestión y estadísticas del sistema</p>
          </router-link>
          
          <router-link to="/geoportal" class="link-card">
            <i class="material-icons">map</i>
            <h3>Geoportal</h3>
            <p>Visualiza información geográfica de los municipios</p>
          </router-link>
        </div>
      </div>
    </section>
    
    <!-- Modal para ver detalles de notificación -->
    <div v-if="modalNotificacionVisible" class="modal-overlay" @click="cerrarModalNotificacion">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h2>Detalles de la Notificación</h2>
          <button class="close-button" @click="cerrarModalNotificacion">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body">
          <div v-if="notificacionSeleccionada" class="notificacion-detalle">
            <!-- Información básica -->
            <div class="detalle-seccion info-basica">
              <div class="detalle-campo">
                <span class="campo-label">ID:</span>
                <span class="campo-valor">{{ notificacionSeleccionada.id }}</span>
              </div>
              
              <div class="detalle-campo">
                <span class="campo-label">Tipo:</span>
                <span 
                  class="campo-valor tipo-badge" 
                  :class="esTipoPreoperacion(notificacionSeleccionada) ? 'tipo-pre' : 'tipo-post'"
                >
                  {{ esTipoPreoperacion(notificacionSeleccionada) ? 'Preoperación' : 'Postoperación' }}
                </span>
              </div>
              
              <div class="detalle-campo">
                <span class="campo-label">Fecha:</span>
                <span class="campo-valor">{{ formatearFechaDetallada(notificacionSeleccionada.fecha_cambio) }}</span>
              </div>
              
              <div class="detalle-campo">
                <span class="campo-label">Estado:</span>
                <span 
                  class="campo-valor estado-badge"
                  :class="notificacionSeleccionada.leido ? 'estado-leido' : 'estado-no-leido'"
                >
                  {{ notificacionSeleccionada.leido ? 'Leída' : 'No leída' }}
                </span>
              </div>
            </div>
            
            <!-- Información de la entidad -->
            <div class="detalle-seccion">
              <h3>Información de la Entidad</h3>
              
              <div class="detalle-campo">
                <span class="campo-label">Tipo de Entidad:</span>
                <div class="campo-valor entidad-info">
                  <i class="material-icons">{{ getNotificationIcon(notificacionSeleccionada.tipo_entidad) }}</i>
                  <span>{{ formatearTipoEntidad(notificacionSeleccionada.tipo_entidad) }}</span>
                </div>
              </div>
              
              <div class="detalle-campo">
                <span class="campo-label">ID de Entidad:</span>
                <span class="campo-valor">{{ notificacionSeleccionada.id_entidad }}</span>
              </div>
              
              <div class="detalle-campo">
                <span class="campo-label">Acción:</span>
                <span 
                  class="campo-valor accion-badge" 
                  :class="getAccionClass(notificacionSeleccionada.accion)"
                >
                  {{ formatearAccion(notificacionSeleccionada.accion) }}
                </span>
              </div>
            </div>
            
            <div class="detalle-seccion">
              <h3>Información de Usuario</h3>
              
              <div class="detalle-campo">
                <span class="campo-label">Usuario:</span>
                <div v-if="getUsuario(notificacionSeleccionada)" class="campo-valor usuario-info">
                  <i class="material-icons">person</i>
                  <span>{{ getUsuario(notificacionSeleccionada) }}</span>
                </div>
                <div v-else class="campo-valor no-data">No hay información de usuario disponible</div>
              </div>
              
              <div v-if="notificacionSeleccionada.fecha_cambio" class="detalle-campo">
                <span class="campo-label">Fecha de modificación:</span>
                <span class="campo-valor">{{ formatearFechaDetallada(notificacionSeleccionada.fecha_cambio) }}</span>
              </div>
            </div>
            
            <!-- ARCHIVO ASOCIADO -->
            <div v-if="extraerRutaArchivo(notificacionSeleccionada)" class="detalle-seccion">
              <h3>Archivo Asociado</h3>
              
              <div class="detalle-campo archivo-campo">
                <div class="campo-valor archivo-info">
                  <div class="archivo-details">
                    <i class="material-icons archivo-icon">{{ getFileIcon(obtenerNombreArchivo(extraerRutaArchivo(notificacionSeleccionada))) }}</i>
                    <span class="archivo-nombre">{{ obtenerNombreArchivo(extraerRutaArchivo(notificacionSeleccionada)) }}</span>
                  </div>
                  
                  <!-- MOSTRAR BOTONES SOLO SI TIENE PERMISOS -->
                  <div v-if="mostrarBotonesArchivo(notificacionSeleccionada)" class="archivo-actions">
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
                  
                  <!-- MOSTRAR MENSAJE DE RESTRICCIÓN SI NO TIENE PERMISOS -->
                  <div v-else class="archivo-restriccion">
                    <i class="material-icons">lock</i>
                    <span class="restriccion-mensaje">{{ permisoUsuario.mensajeAcceso }}</span>
                    
                    <!-- Mensaje para profesionales sin acceso al municipio -->
                    <div v-if="permisoUsuario.esProfesional && !archivoDisponible(notificacionSeleccionada)" class="restriccion-detalle">
                      <small>Este archivo pertenece a un municipio que no está asignado a su perfil.</small>
                    </div>
                    
                    <!-- Mensaje para usuarios no autenticados -->
                    <div v-else-if="!authStore.isAuthenticated" class="restriccion-detalle">
                      <router-link to="/login" class="link-login">
                        <i class="material-icons">login</i>
                        Iniciar sesión para acceder
                      </router-link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Ubicación -->
            <div class="detalle-seccion">
              <h3>Ubicación</h3>
              
              <div v-if="getMunicipio(notificacionSeleccionada)" class="detalle-campo">
                <span class="campo-label">Municipio:</span>
                <div class="campo-valor municipio-info">
                  <i class="material-icons">location_city</i>
                  <span>{{ getMunicipio(notificacionSeleccionada) }}</span>
                </div>
              </div>
              
              <div v-if="getDepartamento(notificacionSeleccionada)" class="detalle-campo">
                <span class="campo-label">Departamento:</span>
                <div class="campo-valor">
                  <i class="material-icons">map</i>
                  <span>{{ getDepartamento(notificacionSeleccionada) }}</span>
                </div>
              </div>
              
              <div v-if="!getMunicipio(notificacionSeleccionada) && !getDepartamento(notificacionSeleccionada)" class="no-data-message">
                <i class="material-icons">info</i>
                <span>No hay información de ubicación disponible</span>
              </div>
            </div>
            
            <!-- Descripción completa -->
            <div class="detalle-seccion">
              <h3>Descripción</h3>
              
              <div class="detalle-campo descripcion-completa">
                <p>{{ getDescripcionCompleta(notificacionSeleccionada) }}</p>
              </div>
              
              <div v-if="getDetallesExtra(notificacionSeleccionada)" class="detalle-campo">
                <span class="campo-label">Detalles adicionales:</span>
                <div class="campo-valor detalles-extra">
                  <p>{{ getDetallesExtra(notificacionSeleccionada) }}</p>
                </div>
              </div>
            </div>
            
            <!-- Datos de contexto -->
            <div v-if="notificacionSeleccionada.datos_contexto" class="detalle-seccion">
              <h3>Datos de contexto</h3>
              
              <div v-html="formatearDatosContexto(notificacionSeleccionada.datos_contexto)"></div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button 
            v-if="notificacionSeleccionada && !notificacionSeleccionada.leido && authStore.isAuthenticated" 
            class="btn btn-primary"
            @click="marcarLeidaYCerrar"
          >
            <i class="material-icons">done</i>
            Marcar como leída
          </button>
          
          <div v-else-if="notificacionSeleccionada && !notificacionSeleccionada.leido && !authStore.isAuthenticated" class="auth-note">
            <i class="material-icons">info</i>
            <router-link to="/login">Inicia sesión</router-link> para marcar como leída
          </div>
          
          <button class="btn btn-secondary" @click="navegarAEntidadDesdeModal">
            <i class="material-icons">open_in_new</i>
            Ver entidad relacionada
          </button>
          
          <button class="btn btn-tertiary" @click="cerrarModalNotificacion">
            <i class="material-icons">close</i>
            Cerrar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { 
  format, addMonths, subMonths, startOfMonth, endOfMonth, 
  addDays, startOfWeek, endOfWeek, isSameMonth, 
  isSameDay, formatISO, parseISO, isToday, isYesterday,
  isWithinInterval
} from 'date-fns';
import { es } from 'date-fns/locale';
import { useNotificacionesStore } from '@/store/notificaciones';
import { getNotificacionesPorMes, getNotificacionesHoy } from '@/api/notificaciones';
import type { Notificacion } from '@/models/notificacion';
import { useAuthStore } from '@/store/auth';
import archivosService from '@/services/archivos';
import api, { API_URL } from '@/api/config';
import { linuxToWindowsPath, isPathLike } from '@/utils/pathUtils';
// Stores
const authStore = useAuthStore();
const notificacionesStore = useNotificacionesStore();
const router = useRouter();

// Computed para verificar si el usuario está autenticado
const usuarioAutenticado = computed(() => {
  return authStore.isAuthenticated || authStore.user != null;
});

// ESTADO PARA ESTADÍSTICAS
const estadisticas = ref({
  total_municipios: 0,
  total_municipios_post: 0,
  total_archivos_pre: 0,
  total_archivos_post: 0,
  total_territoriales: 0,
  total_profesionales_las: 0,
  total_profesionales_pas: 0,
  total_enlaces: 0,
  total_municipios_sin_insumos: 0
});
const cargandoEstadisticas = ref(false);
const errorEstadisticas = ref<string | null>(null);

// ESTADO PARA NOTIFICACIONES
const notificacionesPre = ref<Notificacion[]>([]);
const notificacionesPost = ref<Notificacion[]>([]);
const cargandoNotificaciones = ref(false);
const errorNotificaciones = ref<string | null>(null);

// ESTADO PARA CACHÉ POR MES (OPTIMIZACIÓN PRINCIPAL)
const cacheNotificacionesPorMes = ref<Map<string, {
  preoperacion: Notificacion[],
  postoperacion: Notificacion[],
  timestamp: number
}>>(new Map());

const CACHE_DURATION = 10 * 60 * 1000; // 10 minutos de caché

// Estados de carga específicos para navegación de calendarios
const cargandoMesPre = ref(false);
const cargandoMesPost = ref(false);

// ESTADO PARA CALENDARIOS
const hoy = new Date();
const fechaActualPre = ref(new Date(hoy.getFullYear(), hoy.getMonth(), 1));
const fechaActualPost = ref(new Date(hoy.getFullYear(), hoy.getMonth(), 1));
const mostrandoDetallesPre = ref(false);
const mostrandoDetallesPost = ref(false);
const fechaSeleccionadaPre = ref<Date | null>(null);
const fechaSeleccionadaPost = ref<Date | null>(null);
const notificacionesDiaPre = ref<Notificacion[]>([]);
const notificacionesDiaPost = ref<Notificacion[]>([]);

// ESTADO PARA MODAL DE NOTIFICACIONES
const modalNotificacionVisible = ref(false);
const notificacionSeleccionada = ref<Notificacion | null>(null);

// FUNCIONES UTILITARIAS
const generarClaveMes = (fecha: Date): string => {
  return `${fecha.getFullYear()}-${(fecha.getMonth() + 1).toString().padStart(2, '0')}`;
};

const tieneCacheValido = (claveMes: string): boolean => {
  const cache = cacheNotificacionesPorMes.value.get(claveMes);
  if (!cache) return false;
  
  const ahora = Date.now();
  return (ahora - cache.timestamp) < CACHE_DURATION;
};

// FUNCIÓN OPTIMIZADA: Cargar notificaciones de un mes específico
const cargarNotificacionesMesEspecifico = async (fecha: Date): Promise<{
  preoperacion: Notificacion[],
  postoperacion: Notificacion[]
}> => {
  const claveMes = generarClaveMes(fecha);
  const año = fecha.getFullYear();
  const mes = fecha.getMonth() + 1;
  
  // Verificar caché primero
  if (tieneCacheValido(claveMes)) {
    console.log(`💾 Usando caché para ${claveMes}`);
    const cache = cacheNotificacionesPorMes.value.get(claveMes)!;
    return {
      preoperacion: cache.preoperacion,
      postoperacion: cache.postoperacion
    };
  }
  
  try {
    console.log(`🔄 Cargando datos frescos para ${claveMes}`);
    
    // Cargar ambos tipos con Promise.allSettled para manejo independiente de errores
    const [resultadoPre, resultadoPost] = await Promise.allSettled([
      getNotificacionesPorMes('preoperacion', año, mes, 1000),
      getNotificacionesPorMes('postoperacion', año, mes, 1000)
    ]);
    
    const notifPre = resultadoPre.status === 'fulfilled' ? resultadoPre.value : [];
    const notifPost = resultadoPost.status === 'fulfilled' ? resultadoPost.value : [];
    
    // Registrar errores pero no fallar completamente
    if (resultadoPre.status === 'rejected') {
      console.warn(`⚠️ Error cargando preoperación ${claveMes}:`, resultadoPre.reason);
    }
    if (resultadoPost.status === 'rejected') {
      console.warn(`⚠️ Error cargando postoperación ${claveMes}:`, resultadoPost.reason);
    }
    
    // Guardar en caché
    cacheNotificacionesPorMes.value.set(claveMes, {
      preoperacion: notifPre,
      postoperacion: notifPost,
      timestamp: Date.now()
    });
    
    console.log(`✅ ${claveMes}: ${notifPre.length} pre + ${notifPost.length} post`);
    
    return {
      preoperacion: notifPre,
      postoperacion: notifPost
    };
    
  } catch (error) {
    console.error(`❌ Error general cargando datos para ${claveMes}:`, error);
    
    // Retornar arrays vacíos en lugar de fallar
    return { preoperacion: [], postoperacion: [] };
  }
};

const cargarNotificacionesHoyOptimizado = async () => {
  try {
    cargandoNotificaciones.value = true;
    errorNotificaciones.value = null;

    // Obtener datos del mes actual desde la caché
    const mesActual = new Date();
    const datosMes = await cargarNotificacionesMesEspecifico(mesActual);

    // Filtrar notificaciones de las últimas 24 horas
    const hace24Horas = new Date(Date.now() - 24 * 60 * 60 * 1000);
    
    const filtrar24Horas = (notificaciones: Notificacion[]) => 
      notificaciones.filter(n => 
        parseISO(n.fecha_cambio) >= hace24Horas
      );

    notificacionesPre.value = filtrar24Horas(datosMes.preoperacion);
    notificacionesPost.value = filtrar24Horas(datosMes.postoperacion);

  } catch (err: any) {
    errorNotificaciones.value = err.message || 'Error al cargar notificaciones';
    notificacionesPre.value = [];
    notificacionesPost.value = [];
  } finally {
    cargandoNotificaciones.value = false;
  }
};
const imagenesHero = ref([
  {
    url: '/img/banner2.png',
    titulo: 'GESTION DE INFORMACIÓN PARA PROCESOS CATASTRALES CON ENFOQUE MULTIPROPÓSITO',
    descripcion: 'Plataforma integral para la administración y seguimiento de información territorial'
  },
    {
    url: '/img/banner1.png',
    titulo: 'GESTION DE INFORMACIÓN PARA PROCESOS CATASTRALES CON ENFOQUE MULTIPROPÓSITO',
    descripcion: 'Plataforma integral para la administración y seguimiento de información territorial'
  },
]);
const imagenHeroActiva = ref(0);
const intervaloCarruselHero = ref<number | null>(null);

const prevHeroImage = () => {
  imagenHeroActiva.value = (imagenHeroActiva.value - 1 + imagenesHero.value.length) % imagenesHero.value.length;
  resetIntervaloCarruselHero();
};

const nextHeroImage = () => {
  imagenHeroActiva.value = (imagenHeroActiva.value + 1) % imagenesHero.value.length;
  resetIntervaloCarruselHero();
};

const setActiveHeroImage = (index: number) => {
  imagenHeroActiva.value = index;
  resetIntervaloCarruselHero();
};

const resetIntervaloCarruselHero = () => {
  if (intervaloCarruselHero.value) {
    clearInterval(intervaloCarruselHero.value);
  }
  
  intervaloCarruselHero.value = window.setInterval(() => {
    nextHeroImage();
  }, 5000);
};
// También actualizar cargarMesActualParaCalendarios para mayor resilencia
const cargarMesActualParaCalendarios = async () => {
  try {
    const mesActual = new Date();
    console.log(`📅 Cargando mes actual para calendarios: ${generarClaveMes(mesActual)}`);
    
    const datos = await cargarNotificacionesMesEspecifico(mesActual);
    
    // Asegurar que los calendarios estén en el mes actual
    fechaActualPre.value = new Date(mesActual.getFullYear(), mesActual.getMonth(), 1);
    fechaActualPost.value = new Date(mesActual.getFullYear(), mesActual.getMonth(), 1);
    
    console.log(`✅ Mes actual cargado: ${datos.preoperacion.length} pre + ${datos.postoperacion.length} post`);
    
  } catch (error) {
    console.warn('⚠️ Error en cargarMesActualParaCalendarios:', error);
    
    // Configurar fechas sin datos
    const mesActual = new Date();
    fechaActualPre.value = new Date(mesActual.getFullYear(), mesActual.getMonth(), 1);
    fechaActualPost.value = new Date(mesActual.getFullYear(), mesActual.getMonth(), 1);
    
    // No lanzar error, solo registrar
  }
};

// FUNCIONES DE NAVEGACIÓN OPTIMIZADAS CON CARGA BAJO DEMANDA
const mesAnteriorPre = async () => {
  cargandoMesPre.value = true;
  
  try {
    const nuevoMes = subMonths(fechaActualPre.value, 1);
    fechaActualPre.value = nuevoMes;
    
    console.log(`🔄 Navegando a mes anterior PRE: ${generarClaveMes(nuevoMes)}`);
    await cargarNotificacionesMesEspecifico(nuevoMes);
    
  } catch (error) {
    console.error('❌ Error navegando a mes anterior PRE:', error);
  } finally {
    cargandoMesPre.value = false;
  }
};

const mesSiguientePre = async () => {
  cargandoMesPre.value = true;
  
  try {
    const nuevoMes = addMonths(fechaActualPre.value, 1);
    fechaActualPre.value = nuevoMes;
    
    console.log(`🔄 Navegando a mes siguiente PRE: ${generarClaveMes(nuevoMes)}`);
    await cargarNotificacionesMesEspecifico(nuevoMes);
    
  } catch (error) {
    console.error('❌ Error navegando a mes siguiente PRE:', error);
  } finally {
    cargandoMesPre.value = false;
  }
};

const mesAnteriorPost = async () => {
  cargandoMesPost.value = true;
  
  try {
    const nuevoMes = subMonths(fechaActualPost.value, 1);
    fechaActualPost.value = nuevoMes;
    
    console.log(`🔄 Navegando a mes anterior POST: ${generarClaveMes(nuevoMes)}`);
    await cargarNotificacionesMesEspecifico(nuevoMes);
    
  } catch (error) {
    console.error('❌ Error navegando a mes anterior POST:', error);
  } finally {
    cargandoMesPost.value = false;
  }
};

const mesSiguientePost = async () => {
  cargandoMesPost.value = true;
  
  try {
    const nuevoMes = addMonths(fechaActualPost.value, 1);
    fechaActualPost.value = nuevoMes;
    
    console.log(`🔄 Navegando a mes siguiente POST: ${generarClaveMes(nuevoMes)}`);
    await cargarNotificacionesMesEspecifico(nuevoMes);
    
  } catch (error) {
    console.error('❌ Error navegando a mes siguiente POST:', error);
  } finally {
    cargandoMesPost.value = false;
  }
};

const irAMesActual = async () => {
  try {
    const mesActual = new Date();
    fechaActualPre.value = new Date(mesActual.getFullYear(), mesActual.getMonth(), 1);
    fechaActualPost.value = new Date(mesActual.getFullYear(), mesActual.getMonth(), 1);
    
    await cargarNotificacionesMesEspecifico(mesActual);
  } catch (error) {
    console.error('❌ Error navegando al mes actual:', error);
  }
};

// COMPUTED PARA CALENDARIOS
const nombreMesPre = computed(() => {
  return format(fechaActualPre.value, 'MMMM', { locale: es })
    .replace(/^\w/, c => c.toUpperCase());
});

const nombreMesPost = computed(() => {
  return format(fechaActualPost.value, 'MMMM', { locale: es })
    .replace(/^\w/, c => c.toUpperCase());
});

const yearActualPre = computed(() => {
  return format(fechaActualPre.value, 'yyyy');
});

const yearActualPost = computed(() => {
  return format(fechaActualPost.value, 'yyyy');
});

const diasSemana = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa', 'Do'];

const formatDate = (date: Date): string => {
  return formatISO(date, { representation: 'date' });
};

// NOTIFICACIONES DE HOY
const notificacionesHoy = computed(() => {
  return [...notificacionesPre.value, ...notificacionesPost.value]
    .sort((a, b) => parseISO(b.fecha_cambio).getTime() - parseISO(a.fecha_cambio).getTime());
});

const parseISO = (fecha: string) => {
  try {
    return new Date(fecha.includes('T') ? fecha : `${fecha}T00:00:00`);
  } catch {
    return new Date();
  }
};

const startOfDay = (date: Date) => new Date(date.setHours(0, 0, 0, 0));
const endOfDay = (date: Date) => new Date(date.setHours(23, 59, 59, 999));

// FUNCIÓN AUXILIAR: Ajustar zona horaria
const ajustarZonaHoraria = (fechaStr: string): Date => {
  const fechaObj = new Date(fechaStr);
  
  if (fechaStr.includes('Z') || fechaStr.includes('+')) {
    return fechaObj;
  }
  
  return new Date(
    fechaObj.getFullYear(),
    fechaObj.getMonth(),
    fechaObj.getDate(),
    fechaObj.getHours(),
    fechaObj.getMinutes(),
    fechaObj.getSeconds()
  );
};

// COMPUTED OPTIMIZADOS PARA GENERAR DÍAS DEL CALENDARIO
const diasCalendarioPre = computed(() => {
  const firstDay = startOfMonth(fechaActualPre.value);
  const lastDay = endOfMonth(fechaActualPre.value);
  const startDate = startOfWeek(firstDay, { weekStartsOn: 1 });
  const endDate = endOfWeek(lastDay, { weekStartsOn: 1 });
  
  let date = startDate;
  const calendarDays = [];
  
  // Obtener notificaciones del mes desde caché
  const claveMes = generarClaveMes(fechaActualPre.value);
  const cacheData = cacheNotificacionesPorMes.value.get(claveMes);
  const notificacionesMes = cacheData?.preoperacion || [];
  
  while (date <= endDate) {
    const notificacionesDelDia = notificacionesMes.filter(n => {
      if (!n.fecha_cambio) return false;
      
      try {
        const fechaNotificacion = ajustarZonaHoraria(n.fecha_cambio);
        
        return fechaNotificacion.getFullYear() === date.getFullYear() &&
               fechaNotificacion.getMonth() === date.getMonth() &&
               fechaNotificacion.getDate() === date.getDate();
      } catch (error) {
        console.error('Error comparando fechas:', error, n.fecha_cambio);
        return false;
      }
    });
    
    calendarDays.push({
      fecha: new Date(date),
      numero: date.getDate(),
      otroMes: !isSameMonth(date, fechaActualPre.value),
      esHoy: isSameDay(date, new Date()),
      notificaciones: notificacionesDelDia
    });
    
    date = addDays(date, 1);
  }
  
  return calendarDays;
});

const diasCalendarioPost = computed(() => {
  const firstDay = startOfMonth(fechaActualPost.value);
  const lastDay = endOfMonth(fechaActualPost.value);
  const startDate = startOfWeek(firstDay, { weekStartsOn: 1 });
  const endDate = endOfWeek(lastDay, { weekStartsOn: 1 });
  
  let date = startDate;
  const calendarDays = [];
  
  // Obtener notificaciones del mes desde caché
  const claveMes = generarClaveMes(fechaActualPost.value);
  const cacheData = cacheNotificacionesPorMes.value.get(claveMes);
  const notificacionesMes = cacheData?.postoperacion || [];
  
  while (date <= endDate) {
    const notificacionesDelDia = notificacionesMes.filter(n => {
      if (!n.fecha_cambio) return false;
      
      try {
        const fechaNotificacion = ajustarZonaHoraria(n.fecha_cambio);
        
        return fechaNotificacion.getFullYear() === date.getFullYear() &&
               fechaNotificacion.getMonth() === date.getMonth() &&
               fechaNotificacion.getDate() === date.getDate();
      } catch (error) {
        console.error('Error comparando fechas:', error, n.fecha_cambio);
        return false;
      }
    });
    
    calendarDays.push({
      fecha: new Date(date),
      numero: date.getDate(),
      otroMes: !isSameMonth(date, fechaActualPost.value),
      esHoy: isSameDay(date, new Date()),
      notificaciones: notificacionesDelDia
    });
    
    date = addDays(date, 1);
  }
  
  return calendarDays;
});


// FUNCIÓN DE ACTUALIZACIÓN MANUAL
const cargarNotificacionesManual = async () => {
  cargandoNotificaciones.value = true;
  
  try {
    await cargarNotificacionesHoyOptimizado();
    
    // Invalidar caché del mes actual para forzar recarga
    const mesActual = new Date();
    const claveActual = generarClaveMes(mesActual);
    cacheNotificacionesPorMes.value.delete(claveActual);
    
    await cargarNotificacionesMesEspecifico(mesActual);
    
    console.log('🔄 Notificaciones actualizadas manualmente');
    return true;
  } catch (err: any) {
    console.error('❌ Error actualizando notificaciones:', err);
    errorNotificaciones.value = err.message || 'Error al actualizar notificaciones';
    return false;
  } finally {
    cargandoNotificaciones.value = false;
  }
};

// FUNCIONES DE IDENTIFICACIÓN Y FORMATO
const esTipoPreoperacion = (notificacion: Notificacion): boolean => {
  if (notificacion.tipo_sistema) {
    return notificacion.tipo_sistema === 'preoperacion';
  }
  
  if (notificacion.id < 1000000) {
    return true;
  }
  
  return false;
};

const esTipoPostoperacion = (notificacion: Notificacion): boolean => {
  return !esTipoPreoperacion(notificacion);
};

const getMunicipio = (notificacion: Notificacion): string => {
  if (notificacion.datos_contexto) {
    if (notificacion.datos_contexto.municipio) {
      return notificacion.datos_contexto.municipio;
    }
    if (notificacion.datos_contexto.municipio_nombre) {
      return notificacion.datos_contexto.municipio_nombre;
    }
    if (notificacion.datos_contexto.nom_municipio) {
      return notificacion.datos_contexto.nom_municipio;
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

const getDepartamento = (notificacion: Notificacion): string => {
  if (notificacion.datos_contexto) {
    let contexto = notificacion.datos_contexto;
    if (typeof contexto === 'string') {
      try {
        contexto = JSON.parse(contexto);
      } catch {
        // Continuar con el siguiente método
      }
    }
    
    if (contexto && typeof contexto === 'object') {
      if (contexto.departamento) return contexto.departamento;
      if (contexto.nom_depto) return contexto.nom_depto;
    }
  }
  
  return '';
};

const getDetallesNotificacion = (notificacion: Notificacion): string => {
  if (notificacion.datos_contexto) {
    if (notificacion.tipo_entidad === 'clasificacion') {
      if (notificacion.datos_contexto.nombre) {
        return `Se ${notificacion.accion === 'crear' ? 'creó' : 'modificó'} la clasificación "${notificacion.datos_contexto.nombre}"`;
      }
    } else if (notificacion.tipo_entidad === 'insumo') {
      if (notificacion.datos_contexto.categoria) {
        return `Categoría: ${notificacion.datos_contexto.categoria}`;
      }
    } else if (notificacion.tipo_entidad === 'componente') {
      if (notificacion.datos_contexto.nombre_componente) {
        return `Componente: ${notificacion.datos_contexto.nombre_componente}`;
      }
    } else if (notificacion.tipo_entidad === 'disposicion') {
      let detalles = [];
      
      if (notificacion.datos_contexto.componente) {
        detalles.push(`Componente: ${notificacion.datos_contexto.componente}`);
      }
      
      if (notificacion.datos_contexto.estado) {
        detalles.push(`Estado: ${notificacion.datos_contexto.estado}`);
      }
      
      return detalles.join(' - ');
    }
  }
  
  if (notificacion.descripcion) {
    if (notificacion.descripcion === getTipoNotificacion(notificacion)) {
      return '';
    }
    
    const tipoNotif = getTipoNotificacion(notificacion);
    
    if (notificacion.descripcion.includes(tipoNotif)) {
      const extraInfo = notificacion.descripcion.replace(tipoNotif, '').trim();
      if (extraInfo && extraInfo.length > 5) {
        return extraInfo.replace(/^[:\s]+/, '');
      }
    }
    
    const matchDescripcion = notificacion.descripcion.match(/Nueva clasificación ["'](.+?)["'] añadida al insumo/);
    if (matchDescripcion && matchDescripcion[1]) {
      return `Clasificación añadida: "${matchDescripcion[1]}"`;
    }
    
    return notificacion.descripcion;
  }
  
  const usuario = getUsuario(notificacion);
  if (!usuario && notificacion.datos_contexto?.usuario_windows) {
    return `Modificado por: ${notificacion.datos_contexto.usuario_windows}`;
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



const formatearTiempo = (fechaStr: string | null): string => {
  if (!fechaStr) return '';
  
  try {
    const fechaObj = new Date(fechaStr);
    const ahora = new Date();
    
    if (isNaN(fechaObj.getTime())) {
      return "fecha desconocida";
    }
    
    const diffMs = ahora.getTime() - fechaObj.getTime();
    const diffMinutos = Math.floor(diffMs / (1000 * 60));
    const diffHoras = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDias = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffMinutos < 1) {
      return "justo ahora";
    } else if (diffMinutos < 60) {
      return `hace ${diffMinutos} ${diffMinutos === 1 ? 'minuto' : 'minutos'}`;
    } else if (diffHoras < 24) {
      return `hace ${diffHoras} ${diffHoras === 1 ? 'hora' : 'horas'}`;
    } else if (diffDias < 30) {
      return `hace ${diffDias} ${diffDias === 1 ? 'día' : 'días'}`;
    } else {
      return fechaObj.toLocaleDateString('es-ES', {
        day: 'numeric', 
        month: 'long', 
        year: 'numeric'
      });
    }
  } catch (error) {
    console.error('Error al formatear tiempo:', error, fechaStr);
    return fechaStr || "fecha desconocida";
  }
};

const getNotificationIcon = (tipoEntidad: string): string => {
  switch (tipoEntidad?.toLowerCase()) {
    case 'municipio':
      return 'location_city';
    case 'insumo':
      return 'folder';
    case 'clasificacion':
      return 'category';
    case 'detalle':
      return 'list_alt';
    case 'concepto':
      return 'comment';
    case 'disposicion':
      return 'check_circle';
    case 'componente':
      return 'view_module';
    case 'archivo':
      return 'insert_drive_file';
    default:
      return 'notifications';
  }
};

const getTipoNotificacion = (notificacion: any): string => {
  const entidad = notificacion.tipo_entidad
    ? notificacion.tipo_entidad.charAt(0).toUpperCase() + notificacion.tipo_entidad.slice(1)
    : 'Elemento';
  
  switch (notificacion.accion) {
    case 'crear':
    case 'INSERT':
      return `Nuevo ${entidad} creado`;
    case 'actualizar':
    case 'UPDATE':
      return `${entidad} actualizado`;
    case 'eliminar':
    case 'DELETE':
      return `${entidad} eliminado`;
    case 'disponer':
      return `${entidad} dispuesto`;
    case 'evaluar':
      return `${entidad} evaluado`;
    case 'aprobar':
      return `${entidad} aprobado`;
    case 'rechazar':
      return `${entidad} rechazado`;
    default:
      return `Notificación de ${entidad}`;
  }
};

const formatearFecha = (fecha: Date | null): string => {
  if (!fecha) return '';
  return format(fecha, 'd MMMM yyyy', { locale: es })
    .replace(/^\w/, c => c.toUpperCase());
};

const formatearFechaDetallada = (fechaStr: string): string => {
  if (!fechaStr) return '';
  
  try {
    const fechaObj = new Date(fechaStr);
    
    return format(fechaObj, "d 'de' MMMM 'de' yyyy 'a las' HH:mm:ss", { locale: es })
      .replace(/^\w/, c => c.toUpperCase());
  } catch (error) {
    console.error('Error al formatear fecha detallada:', error, fechaStr);
    return fechaStr;
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
    } else if (notificacion.tipo_entidad === 'componente') {
      if (notificacion.datos_contexto.nombre_componente) {
        detalles.push(`Componente: ${notificacion.datos_contexto.nombre_componente}`);
      }
    } else if (notificacion.tipo_entidad === 'disposicion') {
      if (notificacion.datos_contexto.componente) {
        detalles.push(`Componente: ${notificacion.datos_contexto.componente}`);
      }
      if (notificacion.datos_contexto.estado) {
        detalles.push(`Estado: ${notificacion.datos_contexto.estado}`);
      }
    }
    
    return detalles.join(' - ');
  }
  
  return '';
};

const formatearDatosContexto = (datosContexto: any): string => {
  if (!datosContexto) return 'No hay datos de contexto disponibles';
  
  try {
    let datos = datosContexto;
    if (typeof datos === 'string') {
      try {
        datos = JSON.parse(datos);
      } catch (e) {
        return datosContexto
          .replace(/[{}"]/g, '')
          .replace(/,/g, ', ')
          .replace(/:/g, ': ');
      }
    }
    
    if (typeof datos !== 'object' || datos === null) {
      return String(datos);
    }
    
    let html = '<div class="datos-contexto-formateado">';
    
    for (const [key, value] of Object.entries(datos)) {
      html += `<div class="detalle-campo"><span class="campo-label">${key.replace(/_/g, ' ')}:</span>`;
      if (typeof value === 'object' && value !== null) {
        html += `<span class="campo-valor">${JSON.stringify(value)}</span>`;
      } else {
        // Convertir rutas Linux a Windows si es una ruta
        const displayValue = isPathLike(String(value)) ? linuxToWindowsPath(String(value)) : value;
        html += `<span class="campo-valor">${displayValue}</span>`;
      }
      html += '</div>';
    }
    
    html += '</div>';
    return html;
  } catch (error) {
    console.error("Error formateando datos de contexto:", error);
    return `Error al formatear datos: ${error.message}`;
  }
};

// FUNCIONES DEL CALENDARIO
const verDetallesDia = (dia: any, tipo: 'pre' | 'post') => {
  if (tipo === 'pre') {
    fechaSeleccionadaPre.value = dia.fecha;
    notificacionesDiaPre.value = dia.notificaciones;
    mostrandoDetallesPre.value = true;
  } else {
    fechaSeleccionadaPost.value = dia.fecha;
    notificacionesDiaPost.value = dia.notificaciones;
    mostrandoDetallesPost.value = true;
  }
};

const volverACalendarioPre = () => {
  mostrandoDetallesPre.value = false;
};

const volverACalendarioPost = () => {
  mostrandoDetallesPost.value = false;
};

// FUNCIONES DEL MODAL
const verDetalleNotificacion = (notificacion: Notificacion) => {
  try {
    console.log("Mostrando detalles para notificación:", notificacion.id);
    notificacionSeleccionada.value = JSON.parse(JSON.stringify(notificacion));
    modalNotificacionVisible.value = true;
    
    nextTick(() => {
      console.log("Modal visible:", modalNotificacionVisible.value);
    });
  } catch (error) {
    console.error("Error al mostrar detalles de notificación:", error);
    alert("Hubo un problema al mostrar los detalles. Por favor, intente nuevamente.");
  }
};

const showMonthPicker = ref<'pre' | 'post' | null>(null);
const meses = [
  'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
  'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
];

// Métodos nuevos
const toggleMonthPicker = (type: 'pre' | 'post') => {
  showMonthPicker.value = showMonthPicker.value === type ? null : type;
};

const changeYear = (type: 'pre' | 'post', delta: number) => {
  if (type === 'pre') {
    fechaActualPre.value = addYears(fechaActualPre.value, delta);
  } else {
    fechaActualPost.value = addYears(fechaActualPost.value, delta);
  }
};

const selectMonth = async (type: 'pre' | 'post', monthIndex: number) => {
  const currentDate = type === 'pre' ? fechaActualPre.value : fechaActualPost.value;
  const newDate = new Date(currentDate.getFullYear(), monthIndex, 1);
  
  if (type === 'pre') {
    fechaActualPre.value = newDate;
    cargandoMesPre.value = true;
  } else {
    fechaActualPost.value = newDate;
    cargandoMesPost.value = true;
  }

  try {
    await cargarNotificacionesMesEspecifico(newDate);
  } catch (error) {
    console.error(`Error cambiando mes ${type}:`, error);
  } finally {
    showMonthPicker.value = null;
    if (type === 'pre') cargandoMesPre.value = false;
    else cargandoMesPost.value = false;
  }
};

// Agregar esta función de utilidad
const addYears = (date: Date, years: number) => {
  const result = new Date(date);
  result.setFullYear(result.getFullYear() + years);
  return result;
};

const cerrarModalNotificacion = () => {
  modalNotificacionVisible.value = false;
  notificacionSeleccionada.value = null;
};

// ✅ FUNCIONES CORREGIDAS DE ARCHIVOS


// ✅ FUNCIÓN CORREGIDA: archivoDisponible
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
  
  // ✅ SUPER ADMIN: ACCESO COMPLETO A TODO
  if (authStore.isSuperAdmin) {
    return true;
  }
  
  // ✅ ADMIN NORMAL: ACCESO COMPLETO
  if (authStore.isAdmin) {
    return true;
  }
  
  // ✅ PROFESIONAL: ACCESO LIMITADO A MUNICIPIOS ASIGNADOS
  if (authStore.isProfesional) {
    let municipioId: number | undefined;
    if (notificacion.datos_contexto) {
      const ctx = notificacion.datos_contexto;
      municipioId = ctx.municipio_id || ctx.cod_municipio || undefined;
    }
    
    // Si no hay municipio en datos_contexto, intentar extraer de la ruta
    if (!municipioId) {
      const codigoExtraido = archivosService.extraerCodigoMunicipioDeRuta(ruta);
      if (codigoExtraido) municipioId = codigoExtraido;
    }
    
    // Si encontramos municipio, verificar acceso
    if (municipioId) {
      return authStore.tieneAccesoAMunicipio(municipioId);
    }
  }
  
  // ✅ USUARIOS NO AUTENTICADOS: SIN ACCESO
  return false;
};




const verArchivoNotificacion = async (notificacion: Notificacion) => {
  const rutaArchivo = extraerRutaArchivo(notificacion);
  
  if (!rutaArchivo) {
    alert('No se encontró la ruta del archivo en esta notificación');
    return;
  }
  
  // ✅ VERIFICACIÓN MEJORADA DE PERMISOS
  if (!archivoDisponible(notificacion)) {
    let mensaje = 'Este archivo no está disponible o no tienes permisos para acceder a él';
    
    if (!authStore.isAuthenticated) {
      mensaje = 'Debe iniciar sesión para ver archivos.';
    } else if (authStore.isProfesional) {
      mensaje = 'No tiene permisos para acceder a archivos de este municipio.';
    }
    
    alert(mensaje);
    return;
  }
  
  const nombreArchivo = obtenerNombreArchivo(rutaArchivo);
  const extension = getFileExtension(nombreArchivo);
  
  try {
    console.log('👀 Abriendo archivo:', {
      archivo: nombreArchivo,
      extension,
      username: authStore.user?.username
    });
    
    // ✅ USAR API EN LUGAR DE FETCH MANUAL
    const endpoint = '/preoperacion/ver_pdf/';
    const params = { ruta: rutaArchivo };
    
    const response = await api.get(endpoint, {
      params: params,
      responseType: 'blob'
    });
    
    const blob = new Blob([response], { 
      type: response.type || 'application/octet-stream' 
    });
    const blobUrl = window.URL.createObjectURL(blob);
    
    // Abrir en nueva ventana
    window.open(blobUrl, '_blank');
    
    // Limpiar después de un tiempo
    setTimeout(() => {
      window.URL.revokeObjectURL(blobUrl);
    }, 1000);
    
    mostrarNotificacion(`Abriendo archivo ${extension.toUpperCase()}`, 'info');
    
  } catch (error) {
    console.error('❌ Error al abrir archivo:', error);
    // Si falla, intentar descargar solo si tiene permisos
    try {
      await descargarArchivoNotificacion(notificacion);
    } catch (downloadError) {
      alert(`Error al procesar archivo: ${error.message}`);
    }
  }
};

// ========================================================================================
// 4. FUNCIÓN CORREGIDA: descargarArchivoNotificacion
// ========================================================================================
const descargarArchivoNotificacion = async (notificacion: Notificacion) => {
  const rutaArchivo = extraerRutaArchivo(notificacion);
  
  if (!rutaArchivo) {
    alert('No se encontró la ruta del archivo en esta notificación');
    return;
  }
  
  // ✅ VERIFICACIÓN MEJORADA DE PERMISOS
  if (!archivoDisponible(notificacion)) {
    let mensaje = 'Este archivo no está disponible o no tienes permisos para acceder a él';
    
    if (!authStore.isAuthenticated) {
      mensaje = 'Debe iniciar sesión para descargar archivos.';
    } else if (authStore.isProfesional) {
      mensaje = 'No tiene permisos para acceder a archivos de este municipio.';
    }
    
    alert(mensaje);
    return;
  }
  
  try {
    const nombreArchivo = obtenerNombreArchivo(rutaArchivo);
    const extension = getFileExtension(nombreArchivo);
    
    console.log('⬇️ Descargando archivo:', {
      archivo: nombreArchivo,
      extension: extension,
      username: authStore.user?.username
    });
    
    // ✅ LÓGICA CORREGIDA: Usar endpoint específico según tipo de archivo
    let endpoint;
    let params = { ruta: rutaArchivo };
    
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
    mostrarNotificacion(`Archivo descargado correctamente: ${nombreArchivo}`, 'success');
    
  } catch (error) {
    console.error('❌ Error al descargar archivo:', error);
    alert(`Error al descargar archivo: ${error.message}`);
  }
};

// ========================================================================================
// 5. FUNCIÓN CORREGIDA: cargarTodosLosDatos (si existe)
// ========================================================================================
const cargarTodosLosDatos = async (endpoint: string, params = {}) => {
  let allResults = [];
  let nextUrl = endpoint;
  
  // Convertir URL completa a endpoint relativo si es necesario
  if (nextUrl.startsWith('http')) {
    try {
      const urlObj = new URL(nextUrl);
      nextUrl = urlObj.pathname;
    } catch (e) {
      console.warn('Error parsing URL, using as is:', nextUrl);
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
            console.warn('Error parsing next URL:', nextUrl);
            nextUrl = null;
          }
        }
      } else if (Array.isArray(data)) {
        allResults = [...allResults, ...data];
        nextUrl = null;
      } else {
        console.warn('Estructura de datos inesperada:', data);
        nextUrl = null;
      }
      
      // Limpiar parámetros para próximas iteraciones
      params = {};
      
    } catch (error) {
      console.error('Error cargando datos desde:', nextUrl, error);
      throw error;
    }
  }
  
  return allResults;
};

// ========================================================================================
// 6. FUNCIÓN CORREGIDA: cargarEstadisticas (si existe)
// ========================================================================================
const cargarEstadisticas = async () => {
  try {
    cargandoEstadisticas.value = true;
    errorEstadisticas.value = null;
    
    const response = await api.get('/preoperacion/estadisticas/dashboard/');
    
    if (response && typeof response === 'object') {
      // ✅ CALCULAR EL TOTAL DE ENLACES (L.A.S. + P.A.S.)
      const totalLas = response.total_profesionales_las || 0;
      const totalPas = response.total_profesionales_pas || 0;
      const totalEnlaces = response.total_enlaces || (totalLas + totalPas);
      
      estadisticas.value = {
        total_municipios: response.total_municipios || 0,
        total_municipios_post: response.total_municipios_post || 0,
        total_archivos_pre: response.total_archivos_pre || 0,
        total_archivos_post: response.total_archivos_post || 0,
        total_territoriales: response.total_territoriales || 0,
        total_profesionales_las: totalLas,           // ⚠️ Mantener para compatibilidad
        total_profesionales_pas: totalPas,          // ⚠️ Mantener para compatibilidad
        total_enlaces: totalEnlaces,                 // ✅ NUEVO: Total unificado
        total_municipios_sin_insumos: response.total_municipios_sin_insumos || 0
      };
    }
    
    console.log('✅ Estadísticas cargadas:', estadisticas.value);
    
  } catch (error) {
    console.error('❌ Error cargando estadísticas:', error);
    errorEstadisticas.value = 'Error al cargar estadísticas';
  } finally {
    cargandoEstadisticas.value = false;
  }
};

// ========================================================================================
// 7. FUNCIÓN CORREGIDA: cargarNotificacionesRecientes (si existe)
// ========================================================================================
const cargarNotificacionesRecientes = async () => {
  try {
    console.log('🔄 Cargando notificaciones recientes...');
    
    // ✅ USAR API EN LUGAR DE FETCH/AXIOS DIRECTO
    const [preResponse, postResponse] = await Promise.allSettled([
      api.get('/preoperacion/notificaciones/', { 
        params: { 
          page_size: 10, 
          ordering: '-fecha_creacion' 
        } 
      }),
      api.get('/postoperacion/notificaciones/', { 
        params: { 
          page_size: 10, 
          ordering: '-fecha_creacion' 
        } 
      })
    ]);
    
    // Procesar respuesta de preoperación
    if (preResponse.status === 'fulfilled' && preResponse.value) {
      const preData = preResponse.value;
      notificacionesPre.value = Array.isArray(preData) ? preData : 
                               (preData.results && Array.isArray(preData.results)) ? preData.results : [];
    } else {
      console.warn('Error cargando notificaciones de preoperación:', preResponse.reason);
      notificacionesPre.value = [];
    }
    
    // Procesar respuesta de postoperación
    if (postResponse.status === 'fulfilled' && postResponse.value) {
      const postData = postResponse.value;
      notificacionesPost.value = Array.isArray(postData) ? postData : 
                                (postData.results && Array.isArray(postData.results)) ? postData.results : [];
    } else {
      console.warn('Error cargando notificaciones de postoperación:', postResponse.reason);
      notificacionesPost.value = [];
    }
    
    console.log(`✅ Notificaciones cargadas: ${notificacionesPre.value.length} pre, ${notificacionesPost.value.length} post`);
    
  } catch (error) {
    console.error('❌ Error cargando notificaciones recientes:', error);
  }
};

// ========================================================================================
// 8. FUNCIONES AUXILIARES (asegúrate de que existan)
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

const extraerRutaArchivo = (notificacion: Notificacion): string | null => {
  if (!notificacion.datos_contexto) return null;
  
  let contexto = notificacion.datos_contexto;
  if (typeof contexto === 'string') {
    try {
      contexto = JSON.parse(contexto);
    } catch {
      return null;
    }
  }
  
  if (contexto && typeof contexto === 'object') {
    return contexto.ruta || contexto.path_file || contexto.ruta_completa || contexto.archivo || null;
  }
  
  return null;
};

// ========================================================================================
// 9. FUNCIÓN PARA MOSTRAR NOTIFICACIONES (si no existe)
// ========================================================================================
const mostrarNotificacion = (mensaje: string, tipo: string = 'info') => {
  // Si ya tienes un sistema de notificaciones, usarlo
  // Si no, esta es una implementación básica:
  console.log(`${tipo.toUpperCase()}: ${mensaje}`);
  
  // O si tienes algún componente de notificación:
  // notificationStore.show(mensaje, tipo);
};








// ✅ COMPUTED CORREGIDO: notificacionesFiltradas
const notificacionesFiltradas = computed(() => {
  // 🔧 FILTRADO MEJORADO SEGÚN ROLES
  
  // Para usuarios no autenticados: mostrar todas las notificaciones pero sin acceso a archivos
  if (!authStore.isAuthenticated) {
    return notificacionesHoy.value;
  }
  
  // Para superadmins: mostrar todas las notificaciones pero sin acceso a archivos
  if (authStore.isSuperAdmin) {
    return notificacionesHoy.value;
  }
  
  // Para admins normales: acceso completo
  if (authStore.isAdmin) {
    return notificacionesHoy.value;
  }
  
  // Para profesionales: filtrar por municipios asignados
  if (authStore.isProfesional && authStore.user?.municipios_asignados) {
    const municipiosAsignados = Array.isArray(authStore.user.municipios_asignados) 
      ? authStore.user.municipios_asignados 
      : authStore.user.municipios_asignados.split(',').map(m => parseInt(m.trim()));
    
    return notificacionesHoy.value.filter(notificacion => {
      // Si no hay datos de contexto, mostrar la notificación
      if (!notificacion.datos_contexto) return true;
      
      // Verificar si la notificación pertenece a algún municipio asignado
      const ctx = notificacion.datos_contexto;
      const municipioId = ctx.municipio_id || ctx.cod_municipio;
      
      if (municipioId) {
        return municipiosAsignados.includes(municipioId);
      }
      
      // Si no se puede determinar el municipio, mostrar la notificación
      return true;
    });
  }
  
  // Para usuarios genéricos: mostrar todas las notificaciones sin acceso a archivos
  return notificacionesHoy.value;
});

// ✅ FUNCIÓN AUXILIAR: Verificar si se debe mostrar botones de archivo
const mostrarBotonesArchivo = (notificacion: Notificacion): boolean => {
  // Solo mostrar botones si hay archivo y tiene permisos
  return extraerRutaArchivo(notificacion) !== null && archivoDisponible(notificacion);
};

// ✅ FUNCIÓN AUXILIAR: Obtener mensaje de estado de acceso a archivos
const getMensajeAccesoArchivo = (): string => {
  if (!authStore.isAuthenticated) {
    return 'Inicie sesión para acceder a archivos';
  }
  
  if (authStore.isSuperAdmin) {
    return 'Acceso completo a archivos';
  }
  
  if (authStore.isAdmin) {
    return 'Acceso completo a archivos';
  }
  
  if (authStore.isProfesional) {
    return 'Acceso a archivos de municipios asignados';
  }
  
  return 'Sin acceso a archivos';
};

// ✅ COMPUTED: Información de permisos para mostrar en UI
const permisoUsuario = computed(() => {
  return {
    puedeVerArchivos: authStore.isAdmin && !authStore.isSuperAdmin,
    puedeVerArchivosMunicipio: authStore.isProfesional,
    esSuperAdmin: authStore.isSuperAdmin,
    esAdmin: authStore.isAdmin,
    esProfesional: authStore.isProfesional,
    mensajeAcceso: getMensajeAccesoArchivo()
  };
});






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








// **FIN DE NUEVAS FUNCIONES PARA ARCHIVOS**
// CARRUSEL DE IMÁGENES
const imagenes = ref([
  {
    url: '/img/imagen1.png',
    titulo: 'Integración de Datos',
    descripcion: 'Visualización geoespacial de inventarios, servicios y ciudadanía'
  },
  {
    url: '/img/imagen2.png',
    titulo:  'Análisis Territorial',
    descripcion:'Procesamiento y análisis de información catastral en oficina'
  },
  {
    url: '/img/imagen3.png',
    titulo: 'Levantamiento en Campo',
    descripcion:  'Uso de GPS y cartografía para la actualización catastral en terreno'
  },
  {
    url: '/img/imagen4.png',
    titulo: 'Tecnología en Campo',
    descripcion:  'Captura y gestión de datos catastrales con CICA Movil'
  }
]);

const imagenActiva = ref(0);
const intervaloCarrusel = ref<number | null>(null);

const prevImage = () => {
  imagenActiva.value = (imagenActiva.value - 1 + imagenes.value.length) % imagenes.value.length;
  resetIntervaloCarrusel();
};

const nextImage = () => {
  imagenActiva.value = (imagenActiva.value + 1) % imagenes.value.length;
  resetIntervaloCarrusel();
};

const setActiveImage = (index: number) => {
  imagenActiva.value = index;
  resetIntervaloCarrusel();

};

const resetIntervaloCarrusel = () => {
  if (intervaloCarrusel.value) {
    clearInterval(intervaloCarrusel.value);
  }
  
  intervaloCarrusel.value = window.setInterval(() => {
    nextImage();
  }, 5000);
};

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement;
  if (!target.closest('.month-year-selector')) {
    showMonthPicker.value = null;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
});

// INICIALIZACIÓN OPTIMIZADA
onMounted(async () => {
  await cargarEstadisticas();
  await cargarNotificacionesHoyOptimizado();
  resetIntervaloCarrusel();
  resetIntervaloCarruselHero(); // ← AGREGAR ESTA LÍNEA
  
  await notificacionesStore.cargarNotificacionesPorMes(
    new Date().getFullYear(), 
    new Date().getMonth() + 1
  );
});

// MODIFICACIÓN EN onBeforeUnmount (agregar la línea del hero)
onBeforeUnmount(() => {
  if (intervaloCarrusel.value) {
    clearInterval(intervaloCarrusel.value);
  }
  if (intervaloCarruselHero.value) { // ← AGREGAR ESTAS LÍNEAS
    clearInterval(intervaloCarruselHero.value);
  }
});
</script>

<style scoped>
.hero-carousel-section {
  background-color: #f8f9fa;
  padding: 3rem 0;
  margin-bottom: 3rem;
  width: 100%;
}

.hero-carousel-container {
  position: relative;
  height: 500px;
  overflow: hidden;
  width: 100%;
}

.hero-carousel-container .carousel-control {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  background-color: rgba(255, 255, 255, 0.7);
  color: #343a40;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.hero-carousel-container .carousel-control:hover {
  background-color: rgba(255, 255, 255, 0.9);
}

.hero-carousel-container .prev {
  left: 1rem;
}

.hero-carousel-container .next {
  right: 1rem;
}

.hero-carousel-container .carousel-images {
  height: 100%;
  position: relative;
  width: 100%;
}

.hero-carousel-container .carousel-item {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  transition: opacity 0.5s;
}

.hero-carousel-container .carousel-item.active {
  opacity: 1;
}

.hero-carousel-container .carousel-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.hero-carousel-container .carousel-caption {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  color: white;
  padding: 1.5rem;
}

.hero-carousel-container .carousel-caption h3 {
  margin: 0 0 0.5rem;
  font-size: 1.8rem;
  font-weight: bold;
}

.hero-carousel-container .carousel-caption p {
  margin: 0;
  opacity: 0.9;
  font-size: 1.1rem;
}

.archivo-restriccion {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border: 2px dashed #dee2e6;
  border-radius: 8px;
  text-align: center;
}

.archivo-restriccion i {
  font-size: 2rem;
  color: #6c757d;
}

.restriccion-mensaje {
  font-weight: 500;
  color: #495057;
}

.restriccion-detalle {
  margin-top: 0.5rem;
}

.restriccion-detalle small {
  color: #6c757d;
  font-style: italic;
}

.link-login {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  color: #007bff;
  text-decoration: none;
  font-weight: 500;
}

.link-login:hover {
  text-decoration: underline;
}

/* Estilos para indicador de permisos */
.permisos-indicador {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  margin-right: 0.5rem;
}

.permisos-completos {
  background-color: rgba(40, 167, 69, 0.1);
  color: #28a745;
}

.permisos-limitados {
  background-color: rgba(255, 193, 7, 0.1);
  color: #ffc107;
}

.permisos-solo-lectura {
  background-color: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
}

.sin-permisos {
  background-color: rgba(108, 117, 125, 0.1);
  color: #6c757d;
}

.permisos-indicador:hover .tooltip {
  opacity: 1;
  visibility: visible;
}

.tooltip {
  position: absolute;
  bottom: -35px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #343a40;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s;
  z-index: 1000;
}

.tooltip::before {
  content: '';
  position: absolute;
  top: -4px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-bottom: 4px solid #343a40;
}

/* Mejoras para el auth-note */
.auth-note a {
  color: #007bff;
  text-decoration: none;
  font-weight: 500;
}

.auth-note a:hover {
  text-decoration: underline;
}





.archivo-campo {
  grid-column: 1 / -1; /* Ocupa todo el ancho disponible */
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


/* ========================================= */
/* ESTILOS GENERALES */
/* ========================================= */

.container {
  width: 100%;
  max-width: 1500px;
  margin: 0 auto;
  padding: 0 1rem;
}

.section-title {
  text-align: center;
  font-size: 1.8rem;
  margin-bottom: 2rem;
  color: #343a40;
}

.section-subtitle {
  text-align: center;
  font-size: 1.4rem;
  margin-bottom: 1.5rem;
  color: #495057;
}

/* ========================================= */
/* HERO BANNER */
/* ========================================= */

.hero-banner {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  padding: 4rem 0;
  margin-bottom: 3rem;
  width: 100%;
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.hero-title {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.hero-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  margin-bottom: 2rem;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
  border: none;
  cursor: pointer;
  font-size: 0.95rem;
}

.btn-primary {
  background-color: white;
  color: #007bff;
}

.btn-primary:hover {
  background-color: #f8f9fa;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.btn-secondary {
  background-color: transparent;
  border: 1px solid white;
  color: white;
}

.btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.btn-tertiary {
  background-color: #f8f9fa;
  color: #495057;
  border: 1px solid #dee2e6;
}

.btn-tertiary:hover {
  background-color: #e9ecef;
}

.btn i {
  font-size: 1.1rem;
}

/* ========================================= */
/* DASHBOARD GRID */
/* ========================================= */

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 3rem;
  width: 100%;
}

.stats-card {
  grid-column: 1 / 2;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  width: 100%;
}

.notificaciones-card {
  grid-column: 2 / 3;
  grid-row: 1 / 2;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  width: 100%;
}

.stats-header, .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  width: 100%;
}

.stats-header h2, .header h2 {
  margin: 0;
  font-size: 1.2rem;
  color: #343a40;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stats-header button, .header button {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.stats-header button:hover, .header button:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: #007bff;
}

.stats-header button:disabled, .header button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

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

/* ========================================= */
/* ESTADÍSTICAS */
/* ========================================= */

.loading-stats, .loading, .error-message, .empty-message, .no-events {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  color: #6c757d;
}

.spinner {
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

.error-message i, .empty-message i, .no-events i {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.error-message i {
  color: #dc3545;
}

.error-message button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  padding: 1.5rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
}
.month-year-selector {
  position: relative;
  margin-left: 1rem;
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.dropdown-trigger:hover {
  border-color: #007bff;
  background-color: #f8f9fa;
}

.dropdown-trigger i {
  font-size: 1.2rem;
  margin-left: auto;
}



.year-selector {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  padding: 0 0.5rem;
}

.year-selector button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.year-selector button:hover {
  background-color: #f8f9fa;
}

.month-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.month-grid button {
  padding: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.month-grid button:hover {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

.month-grid button.active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}
.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: #6c757d;
  font-size: 0.9rem;
}

.stats-footer, .ver-mas {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e9ecef;
  text-align: center;
}

.link-more {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #007bff;
  text-decoration: none;
  font-weight: 500;
}

.link-more:hover {
  text-decoration: underline;
}

/* ========================================= */
/* NOTIFICACIONES SECCIÓN */
/* ========================================= */

.notificaciones-hoy-container {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  max-height: 500px;
  overflow: hidden;
}

.notificaciones-hoy-container h3 {
  position: sticky;
  top: 0;
  z-index: 10;
  padding: 0.75rem 1.5rem;
  margin: 0;
  font-size: 1rem;
  background-color: #f1f8ff;
  border-bottom: 1px solid #e9ecef;
}

.notificaciones-scroll {
  flex: 1;
  overflow-y: auto;
  max-height: 450px;
  scrollbar-width: thin;
  scrollbar-color: #007bff #f1f8ff;
}

.notificaciones-scroll::-webkit-scrollbar {
  width: 8px;
}

.notificaciones-scroll::-webkit-scrollbar-track {
  background: #f1f8ff;
  border-radius: 4px;
}

.notificaciones-scroll::-webkit-scrollbar-thumb {
  background-color: #007bff;
  border-radius: 4px;
  border: 2px solid #f1f8ff;
}

.notificaciones-lista {
  list-style: none;
  padding: 0;
  margin: 0;
  width: 100%;
}

.notificaciones-lista li {
  display: flex;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e9ecef;
  transition: background-color 0.2s;
  cursor: pointer;
  position: relative;
  width: 100%;
}

.notificaciones-lista li:hover {
  background-color: #f8f9fa;
}

.notificaciones-lista li.notificacion-pre {
  border-left: 4px solid #007bff;
  background-color: #f5fff9;
}

.notificaciones-lista li.notificacion-pre:hover {
  background-color: #e9f3ff;
}

.notificaciones-lista li.notificacion-pre.no-leida {
  background-color: #e8f4ff;
}

.notificaciones-lista li.notificacion-pre .notificacion-icon {
  color: #007bff;
}

.notificaciones-lista li.notificacion-post {
  border-left: 4px solid #28a745;
  background-color: #f5fff9;
}

.notificaciones-lista li.notificacion-post:hover {
  background-color: #e9ffef;
}

.notificaciones-lista li.notificacion-post.no-leida {
  background-color: #e8f7ee;
}

.notificaciones-lista li.notificacion-post .notificacion-icon {
  color: #28a745;
}

.notificacion-icon {
  display: flex;
  align-items: flex-start;
  padding-top: 0.25rem;
  margin-right: 1rem;
}

.notificacion-icon.icon-pre i {
  color: #007bff;
}

.notificacion-icon.icon-post i {
  color: #28a745;
}

.notificacion-icon i {
  font-size: 1.5rem;
}

.notificacion-content {
  flex: 1;
}

.notificacion-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: bold;
  color: #343a40;
  margin-bottom: 0.25rem;
}

.badge {
  font-size: 0.7rem;
  font-weight: normal;
  background-color: #dc3545;
  color: white;
  padding: 0.1rem 0.4rem;
  border-radius: 10px;
}

.notificacion-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  color: #6c757d;
  font-size: 0.8rem;
  margin-bottom: 0.5rem;
}

.notificacion-meta .municipio {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-weight: 500;
}

.notificacion-meta .municipio i {
  font-size: 1rem;
}

.notificacion-meta .tiempo {
  color: #6c757d;
}

.notificacion-meta .usuario {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #6c757d;
}

.notificacion-meta .usuario i {
  font-size: 1rem;
  color: #17a2b8;
}

.notificacion-meta .tipo {
  padding: 0.1rem 0.5rem;
  border-radius: 10px;
  font-size: 0.7rem;
}

.notificacion-meta .tipo.tag-pre {
  background-color: rgba(0, 123, 255, 0.1);
  color: #007bff;
}

.notificacion-meta .tipo.tag-post {
  background-color: rgba(40, 167, 69, 0.1);
  color: #28a745;
}

.notificacion-details {
  background-color: #f8f9fa;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
  color: #495057;
  margin-top: 0.5rem;
}

.notificacion-pre .notificacion-details {
  background-color: rgba(0, 123, 255, 0.05);
  border-left: 2px solid rgba(0, 123, 255, 0.2);
}

.notificacion-post .notificacion-details {
  background-color: rgba(40, 167, 69, 0.05);
  border-left: 2px solid rgba(40, 167, 69, 0.2);
}

.clickable-notification {
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
}

.clickable-notification:hover {
  background-color: #f0f7ff !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.clickable-notification::after {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  border-radius: inherit;
  pointer-events: none;
  transition: all 0.2s ease;
}

.clickable-notification:hover::after {
  box-shadow: 0 0 0 2px #007bff;
}

/* ========================================= */
/* CALENDARIOS OPTIMIZADOS */
/* ========================================= */

.calendars-section {
  grid-column: 1 / 3;
  grid-row: 2 / 3;
  width: 100%;
}

.calendars-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.calendars-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6c757d;
  font-size: 0.9rem;
  background-color: #f8f9fa;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border-left: 3px solid #17a2b8;
}

.calendars-info i {
  color: #17a2b8;
  font-size: 1.1rem;
}

.calendars-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  width: 100%;
}

.calendar-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  width: 100%;
  position: relative;
}

.pre-calendar {
  border-top: 4px solid #007bff;
}

.post-calendar {
  border-top: 4px solid #28a745;
}

.pre-icon {
  color: #007bff;
}

.post-icon {
  color: #28a745;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  width: 100%;
}

.calendar-header h2 {
  margin: 0;
  font-size: 1.1rem;
  color: #343a40;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.loading-indicator-small {
  display: inline-flex;
  align-items: center;
  margin-left: 0.5rem;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.calendar-nav {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.calendar-nav button {
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
  transition: opacity 0.2s ease, background-color 0.2s ease;
}

.calendar-nav button:hover:not(:disabled) {
  background-color: rgba(0, 0, 0, 0.05);
  color: #007bff;
}

.calendar-nav button.loading {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}

.calendar-nav button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.calendar-nav button:disabled:hover {
  background-color: transparent;
  color: #6c757d;
}

.month-year-display {
  font-weight: 600;
  color: #495057;
  min-width: 140px;
  text-align: center;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background-color: rgba(0, 0, 0, 0.05);
}

.today-button {
  background-color: #28a745 !important;
  color: white !important;
  border: none !important;
  border-radius: 4px;
  padding: 6px 12px !important;
  margin-left: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  width: auto !important;
  height: auto !important;
  transition: background-color 0.2s;
}

.today-button:hover:not(:disabled) {
  background-color: #218838 !important;
}

.today-button:disabled {
  background-color: #6c757d !important;
  opacity: 0.6;
  cursor: not-allowed;
}

.today-button i {
  font-size: 1.1rem;
}

.calendar-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: 8px;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.loading-content .spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-content span {
  color: #495057;
  font-weight: 500;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.25rem;
  padding: 1rem;
  width: 100%;
  transition: opacity 0.3s ease;
}

.calendar-grid.loading {
  opacity: 0.6;
  pointer-events: none;
}

.calendar-day-header {
  text-align: center;
  font-weight: bold;
  color: #495057;
  padding: 0.5rem;
  font-size: 0.9rem;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.25rem;
  border-radius: 4px;
  position: relative;
  cursor: pointer;
  transition: opacity 0.3s ease, background-color 0.2s ease;
}

.calendar-day:hover {
  background-color: #f8f9fa;
}

.calendar-day.other-month {
  opacity: 0.5;
}

.calendar-day.today {
  background-color: #e8f4ff;
}

.calendar-day.loading {
  opacity: 0.5;
  cursor: not-allowed;
}

.pre-calendar .calendar-day.has-events {
  background-color: rgba(0, 123, 255, 0.1);
}

.post-calendar .calendar-day.has-events {
  background-color: rgba(40, 167, 69, 0.1);
}

.calendar-day.has-events.loading .notification-count {
  opacity: 0.7;
}

.day-number {
  font-size: 0.9rem;
  font-weight: 500;
  color: #343a40;
  margin-bottom: auto;
  padding: 0.25rem 0;
}

.day-events {
  margin-top: auto;
}

.notification-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  padding: 0 4px;
  font-size: 0.75rem;
  font-weight: bold;
  color: white;
}

.pre-calendar .notification-count {
  background-color: #007bff;
}

.post-calendar .notification-count {
  background-color: #28a745;
}

.calendar-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e9ecef;
  background-color: #f8f9fa;
  width: 100%;
}

.events-tip,
.loading-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.events-tip {
  color: #6c757d;
}

.events-tip i {
  color: #17a2b8;
  font-size: 1.1rem;
}

.loading-info {
  color: #007bff;
  margin-left: 1rem;
}

.loading-info i {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ========================================= */
/* VISTA DETALLADA DE DÍA */
/* ========================================= */

.day-details {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  width: 100%;
}

.pre-details {
  border-top: 4px solid #007bff;
}

.post-details {
  border-top: 4px solid #28a745;
}

.day-details-header {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  width: 100%;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  margin-right: 1rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.back-button:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: #343a40;
}

.day-details-header h2 {
  margin: 0;
  font-size: 1.1rem;
  color: #343a40;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.day-details-content {
  padding: 1.5rem;
  max-height: 600px;
  overflow-y: auto;
  width: 100%;
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
}

.notification-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  width: 100%;
}

.pre-details .notification-item {
  border-left: 4px solid #007bff;
}

.post-details .notification-item {
  border-left: 4px solid #28a745;
}

.notification-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: rgba(0, 123, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.post-details .notification-icon {
  background-color: rgba(40, 167, 69, 0.1);
}

.notification-icon i {
  font-size: 1.5rem;
  color: #007bff;
}

.post-details .notification-icon i {
  color: #28a745;
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-weight: 500;
  margin-bottom: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.notification-badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
  background-color: #dc3545;
  color: white;
  font-size: 0.7rem;
  font-weight: normal;
}

.notification-time {
  font-size: 0.85rem;
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.notification-details {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 0.5rem;
  width: 100%;
}

.notification-details div {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.85rem;
  color: #6c757d;
  background-color: rgba(0, 0, 0, 0.05);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.notification-details i {
  font-size: 1rem;
}

/* ========================================= */
/* CARRUSEL */
/* ========================================= */

.image-showcase {
  background-color: #f8f9fa;
  padding: 3rem 0;
  margin-bottom: 3rem;
  width: 100%;
}

.carousel-container {
  position: relative;
  height: 400px;
  overflow: hidden;
  width: 100%;
}

.carousel-control {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  background-color: rgba(255, 255, 255, 0.7);
  color: #343a40;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.carousel-control:hover {
  background-color: rgba(255, 255, 255, 0.9);
}

.prev {
  left: 1rem;
}

.next {
  right: 1rem;
}

.carousel-images {
  height: 100%;
  position: relative;
  width: 100%;
}

.carousel-item {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  transition: opacity 0.5s;
}

.carousel-item.active {
  opacity: 1;
}

.carousel-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.carousel-caption {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  color: white;
  padding: 1.5rem;
}

.carousel-caption h3 {
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
}

.carousel-caption p {
  margin: 0;
  opacity: 0.9;
}

.carousel-indicators {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1rem;
}

.indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.2);
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
}

.indicator.active {
  background-color: #007bff;
}

/* ========================================= */
/* ENLACES RÁPIDOS */
/* ========================================= */

.quick-links {
  padding: 3rem 0;
  width: 100%;
}

.links-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  width: 100%;
}

.link-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  text-align: center;
  text-decoration: none;
  color: #343a40;
  transition: transform 0.2s, box-shadow 0.2s;
}

.link-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.link-card i {
  font-size: 2.5rem;
  color: #007bff;
  margin-bottom: 1rem;
}

.link-card h3 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.link-card p {
  color: #6c757d;
  font-size: 0.9rem;
  margin: 0;
}

/* ========================================= */
/* MODAL */
/* ========================================= */

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  padding: 1rem;
}

.modal-container {
  background-color: white;
  border-radius: 8px;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #343a40;
}

.close-button {
  background: none;
  border: none;
  color: #adb5bd;
  cursor: pointer;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
}

.close-button:hover {
  background-color: #f8f9fa;
  color: #495057;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.notificacion-detalle {
  max-width: 100%;
}

.detalle-seccion {
  margin-bottom: 2rem;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 1rem;
}

.detalle-seccion:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.detalle-seccion h3 {
  font-size: 1.1rem;
  color: #343a40;
  margin: 0 0 1rem;
}

.info-basica {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.detalle-campo {
  margin-bottom: 1rem;
}

.campo-label {
  display: block;
  font-size: 0.85rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.campo-valor {
  font-weight: 500;
  color: #212529;
}

.entidad-info, .usuario-info, .municipio-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.entidad-info i, .usuario-info i, .municipio-info i {
  font-size: 1.2rem;
}

.entidad-info i {
  color: #6c757d;
}

.usuario-info i {
  color: #17a2b8;
}

.municipio-info i {
  color: #6c757d;
}

.estado-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
}

.estado-leido {
  background-color: #e9ecef;
  color: #495057;
}

.estado-no-leido {
  background-color: #cce5ff;
  color: #004085;
}

.tipo-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
}

.tipo-pre {
  background-color: rgba(0, 123, 255, 0.1);
  color: #007bff;
}

.tipo-post {
  background-color: rgba(40, 167, 69, 0.1);
  color: #28a745;
}

.accion-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
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

.descripcion-completa {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
}

.descripcion-completa p, .detalles-extra p {
  margin: 0;
  line-height: 1.5;
}

.detalles-extra {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  margin-top: 0.5rem;
}

.no-data {
  color: #adb5bd;
  font-style: italic;
}

.no-data-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6c757d;
  font-style: italic;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.auth-note {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6c757d;
  font-size: 0.9rem;
  padding: 0.5rem 0.75rem;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.auth-note i {
  color: #17a2b8;
  font-size: 1.1rem;
}

.dropdown-container {
  position: relative;
  display: inline-block;
}

.month-picker-popup {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1000;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
  padding: 1.5rem;
  min-width: 280px;
  max-width: 90vw;
  animation: popupFadeIn 0.3s ease;
}

@keyframes popupFadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, -45%);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%);
  }
}

.datos-contexto-formateado {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
}
.pre-operacion {
  border-top: 4px solid #007bff;
}

.post-operacion {
  border-top: 4px solid #28a745;
}

/* ========================================= */
/* RESPONSIVE */
/* ========================================= */

@media (max-width: 1600px) {
  .container {
    max-width: 1500px;
  }
}

@media (max-width: 1400px) {
  .container {
    max-width: 1300px;
  }
}

@media (max-width: 1200px) {
  .container {
    max-width: 1140px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .hero-title {
    font-size: 2rem;
  }
}

@media (max-width: 992px) {
  .container {
    max-width: 960px;
  }
  
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-card,
  .notificaciones-card {
    grid-column: 1;
  }
  
  .calendars-section {
    grid-column: 1;
  }
  
  .calendars-container {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .carousel-container {
    height: 350px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .calendars-info {
    font-size: 0.8rem;
    padding: 0.4rem 0.8rem;
  }
  
  .loading-content {
    padding: 0.75rem;
  }
  
  .loading-content .spinner {
    width: 28px;
    height: 28px;
  }
}

@media (max-width: 768px) {
    .stat-icon {
    display: none;
  }
  
  .stat-item.clickable:hover {
    transform: none;
  }
   .archivo-actions {
    flex-direction: column;
  }
  
  .btn-archivo {
    width: 100%;
    justify-content: center;
  }
  
  .archivo-details {
    flex-direction: column;
    text-align: center;
  }
  
  .archivo-icon {
    font-size: 3rem !important;
  }

  .month-picker-popup {
    width: 90%;
    padding: 1rem;
  }
  
  .month-grid {
    grid-template-columns: repeat(3, 1fr) !important;
  }

  .container {
    max-width: 720px;
  }
  
  .hero-banner {
    padding: 3rem 0;
  }
  
  .hero-title {
    font-size: 1.8rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .hero-actions {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .carousel-container {
    height: 300px;
  }
  
  .calendar-day-header,
  .calendar-day .day-number {
    font-size: 0.8rem;
  }
  
  .notificacion-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .notificacion-meta .usuario {
    width: 100%;
    margin-top: 0.25rem;
  }
  
  .calendars-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .calendars-info {
    width: 100%;
    justify-content: center;
  }
  
  .calendar-footer {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
  
  .month-year-display {
    min-width: 120px;
    font-size: 0.9rem;
  }
  
  .today-button {
    padding: 4px 8px !important;
    font-size: 0.8rem;
  }
}

@media (max-width: 576px) {
    .archivo-campo {
    margin: 0 -1rem;
    border-radius: 0;
    border-left: none;
    border-right: none;
  }
  .container {
    max-width: 100%;
    padding: 0 10px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .carousel-container {
    height: 250px;
  }
  
  .carousel-caption h3 {
    font-size: 1.2rem;
  }
  
  .carousel-caption p {
    font-size: 0.9rem;
  }
  
  .loading-content span {
    font-size: 0.9rem;
  }
  
  .calendar-nav {
    flex-wrap: wrap;
    gap: 0.25rem;
  }
  
  .today-button {
    order: 3;
    margin-left: 0;
    margin-top: 0.5rem;
  }
  
  .notificaciones-hoy-container,
  .notificaciones-scroll {
    max-height: 300px;
  }
}
.stat-item.clickable {
  position: relative;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.stat-item.clickable::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(52, 152, 219, 0.1), transparent);
  transition: left 0.5s;
}

.stat-item.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  background-color: #f8f9fa;
}

.stat-item.clickable:hover::before {
  left: 100%;
}

.stat-item.clickable:hover .stat-value {
  color: #007bff;
  transform: scale(1.05);
}

.stat-item.clickable:hover .stat-icon {
  opacity: 1;
  transform: translateX(0);
}

.stat-icon {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  font-size: 1.2rem;
  color: #007bff;
  opacity: 0;
  transform: translateX(10px);
  transition: all 0.3s ease;
}

.stat-value {
  transition: all 0.3s ease;
}

/* Colores específicos por tipo de estadística */
.stat-item.clickable:nth-child(1):hover .stat-value,
.stat-item.clickable:nth-child(8):hover .stat-value {
  color: #28a745; /* Verde para municipios */
}

.stat-item.clickable:nth-child(2):hover .stat-value,
.stat-item.clickable:nth-child(4):hover .stat-value {
  color: #6f42c1; /* Púrpura para post-operación */
}

.stat-item.clickable:nth-child(3):hover .stat-value {
  color: #17a2b8; /* Cyan para archivos pre */
}

.stat-item.clickable:nth-child(5):hover .stat-value,
.stat-item.clickable:nth-child(6):hover .stat-value,
.stat-item.clickable:nth-child(7):hover .stat-value {
  color: #fd7e14; /* Naranja para profesionales */
}

.stat-item.clickable:nth-child(8):hover .stat-value {
  color: #dc3545; /* Rojo para municipios sin insumos */
}

</style>