<template>
  <div class="info-admin-form">
    <!-- Header con navegación -->
    <div class="page-header">
      <div class="header-content">
        <nav class="breadcrumb">
          <router-link to="/gestion-informacion/info-administrativa" class="breadcrumb-link">
            <i class="material-icons">admin_panel_settings</i>
            Información Administrativa
          </router-link>
          <i class="material-icons breadcrumb-separator">chevron_right</i>
          <span class="breadcrumb-current">
            {{ modoEdicion ? 'Editar Información' : 'Nueva Información' }}
          </span>
        </nav>
        
        <h1 class="page-title">
          <i class="material-icons">{{ modoEdicion ? 'edit' : 'add_circle' }}</i>
          {{ modoEdicion ? 'Editar Información Administrativa' : 'Crear Nueva Información Administrativa' }}
        </h1>
        
        <p class="page-description">
          {{ modoEdicion 
            ? 'Modifique la información administrativa del municipio. Los cambios se guardarán al hacer clic en "Actualizar".' 
            : 'Complete la información administrativa del municipio. Solo el municipio es obligatorio, los demás campos son opcionales.'
          }}
        </p>
      </div>
    </div>

    <!-- Estados de carga -->
    <div v-if="cargandoDatos" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Cargando información...</p>
    </div>

    <div v-else-if="error" class="error-container">
      <i class="material-icons">error</i>
      <h3>Error al cargar los datos</h3>
      <p>{{ error }}</p>
      <button @click="cargarDatos" class="btn btn-outline">
        <i class="material-icons">refresh</i>
        Reintentar
      </button>
    </div>

    <!-- Formulario -->
    <div v-else class="form-container">
      <form @submit.prevent="guardarInformacion" class="info-admin-form-content">
        
        <!-- Ubicación del Municipio -->
        <div class="form-section">
          <div class="section-header">
            <h2 class="section-title">
              <i class="material-icons">place</i>
              Ubicación del Municipio
            </h2>
            <p class="section-description">
              Seleccione el municipio para el cual registrará la información administrativa
            </p>
          </div>
          
          <div class="form-grid">
            <!-- Filtro Departamento -->
            <div class="form-group">
              <label for="departamento" class="form-label required">
                Departamento
                <span class="contador-opciones">({{ departamentos.length }} disponibles)</span>
              </label>
              <select
                id="departamento"
                v-model="filtros.departamento"
                @change="onDepartamentoChange"
                class="form-select"
                :class="{ 'error': errores.departamento, 'has-selection': filtros.departamento }"
                :disabled="modoEdicion"
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
              <span v-if="errores.departamento" class="error-message">
                {{ errores.departamento }}
              </span>
              <span v-if="modoEdicion" class="help-text">
                No se puede modificar el departamento en modo edición
              </span>
            </div>

            <!-- Filtro Municipio -->
            <div class="form-group">
              <label for="municipio" class="form-label required">
                Municipio
                <span class="contador-opciones">({{ municipiosDisponibles.length }} disponibles)</span>
              </label>
              <select
                id="municipio"
                v-model="formulario.cod_municipio"
                @change="onMunicipioChange"
                class="form-select"
                :class="{ 
                  'error': errores.cod_municipio, 
                  'has-selection': formulario.cod_municipio,
                  'loading': cargandoMunicipios 
                }"
                :disabled="(!filtros.departamento || cargandoMunicipios) || modoEdicion"
                required
              >
                <option value="">
                  {{ cargandoMunicipios ? 'Cargando municipios...' : 
                     !filtros.departamento ? 'Primero seleccione un departamento' : 'Seleccione un municipio' }}
                </option>
                <option 
                  v-for="mun in municipiosDisponibles" 
                  :key="mun.cod_municipio" 
                  :value="mun.cod_municipio"
                >
                  {{ mun.nom_municipio }} ({{ mun.cod_municipio }})
                </option>
              </select>
              <span v-if="errores.cod_municipio" class="error-message">
                {{ errores.cod_municipio }}
              </span>
              <span v-if="!filtros.departamento" class="help-text">
                Primero debe seleccionar un departamento
              </span>
              <span v-if="modoEdicion" class="help-text">
                No se puede modificar el municipio en modo edición
              </span>
            </div>
          </div>
        </div>

        <!-- Información General -->
        <div class="form-section">
          <div class="section-header">
            <h2 class="section-title">
              <i class="material-icons">business</i>
              Información General
            </h2>
            <p class="section-description">
              Datos generales del catastro y gestor
            </p>
          </div>
          
          <div class="form-grid">
            <!-- ID Gestor Catastral -->
            <div class="form-group">
              <label for="id_gestor_catas" class="form-label">
                ID Gestor Catastral
              </label>
              <input
                id="id_gestor_catas"
                v-model="formulario.id_gestor_catas"
                type="text"
                class="form-input"
                :class="{ 'error': errores.id_gestor_catas }"
                placeholder="Ej: GC001"
                maxlength="20"
              />
              <span v-if="errores.id_gestor_catas" class="error-message">
                {{ errores.id_gestor_catas }}
              </span>
            </div>

            <!-- Gestor Prestador Servicio -->
            <div class="form-group">
              <label for="gestor_prestador_servicio" class="form-label">
                Gestor Prestador de Servicio
              </label>
              <input
                id="gestor_prestador_servicio"
                v-model="formulario.gestor_prestador_servicio"
                type="text"
                class="form-input"
                :class="{ 'error': errores.gestor_prestador_servicio }"
                placeholder="Ej: IGAC - Instituto Geográfico Agustín Codazzi"
                maxlength="200"
              />
              <span v-if="errores.gestor_prestador_servicio" class="error-message">
                {{ errores.gestor_prestador_servicio }}
              </span>
            </div>

            <!-- Año de Publicación -->
            <div class="form-group">
              <label for="publicacion_year" class="form-label">
                Año de Publicación
              </label>
              <input
                id="publicacion_year"
                v-model="formulario.publicacion_year"
                type="number"
                class="form-input"
                :class="{ 'error': errores.publicacion_year }"
                placeholder="Ej: 2023"
                :min="1900"
                :max="2100"
              />
              <span v-if="errores.publicacion_year" class="error-message">
                {{ errores.publicacion_year }}
              </span>
            </div>
          </div>
        </div>

        <!-- Vigencias y Estados -->
        <div class="form-section">
          <div class="section-header">
            <h2 class="section-title">
              <i class="material-icons">schedule</i>
              Vigencias y Estados
            </h2>
            <p class="section-description">
              Información sobre vigencias y estados del catastro rural y urbano
            </p>
          </div>
          
          <div class="form-grid">
            <!-- Vigencia Rural -->
            <div class="form-group">
              <label for="vigencia_rural" class="form-label">
                Vigencia Rural
              </label>
              <input
                id="vigencia_rural"
                v-model="formulario.vigencia_rural"
                type="number"
                class="form-input"
                :class="{ 'error': errores.vigencia_rural }"
                placeholder="Ej: 2023"
                :min="1900"
                :max="2100"
              />
              <span v-if="errores.vigencia_rural" class="error-message">
                {{ errores.vigencia_rural }}
              </span>
            </div>
            
            <!-- Vigencia Urbana -->
            <div class="form-group">
              <label for="vigencia_urbana" class="form-label">
                Vigencia Urbana
              </label>
              <input
                id="vigencia_urbana"
                v-model="formulario.vigencia_urbana"
                type="number"
                class="form-input"
                :class="{ 'error': errores.vigencia_urbana }"
                placeholder="Ej: 2024"
                :min="1900"
                :max="2100"
              />
              <span v-if="errores.vigencia_urbana" class="error-message">
                {{ errores.vigencia_urbana }}
              </span>
            </div>
            
            <!-- Estado Rural -->
            <div class="form-group">
              <label for="estado_rural" class="form-label">
                Estado Rural
              </label>
              <select
                id="estado_rural"
                v-model="formulario.estado_rural"
                class="form-select"
                :class="{ 'error': errores.estado_rural, 'has-selection': formulario.estado_rural }"
              >
                <option value="">Seleccione un estado</option>
                <option value="ACTUALIZADO TOTAL">ACTUALIZADO TOTAL</option>
                <option value="ACTUALIZADO PARCIAL">ACTUALIZADO PARCIAL</option>
                <option value="DESACTUALIZADO">DESACTUALIZADO</option>
                <option value="POR FORMAR">POR FORMAR</option>
              </select>
              <span v-if="errores.estado_rural" class="error-message">
                {{ errores.estado_rural }}
              </span>
            </div>
            
            <!-- Estado Urbano -->
            <div class="form-group">
              <label for="estado_urbano" class="form-label">
                Estado Urbano
              </label>
              <select
                id="estado_urbano"
                v-model="formulario.estado_urbano"
                class="form-select"
                :class="{ 'error': errores.estado_urbano, 'has-selection': formulario.estado_urbano }"
              >
                <option value="">Seleccione un estado</option>
                <option value="ACTUALIZADO TOTAL">ACTUALIZADO TOTAL</option>
                <option value="ACTUALIZADO PARCIAL">ACTUALIZADO PARCIAL</option>
                <option value="DESACTUALIZADO">DESACTUALIZADO</option>
                <option value="POR FORMAR">POR FORMAR</option>
              </select>
              <span v-if="errores.estado_urbano" class="error-message">
                {{ errores.estado_urbano }}
              </span>
            </div>
          </div>
        </div>

        <!-- Información Rural Completa -->
        <div class="form-section">
          <div class="section-header">
            <h2 class="section-title">
              <i class="material-icons">agriculture</i>
              Información Rural Completa
            </h2>
            <p class="section-description">
              Todos los datos del catastro rural - opcionales según disponibilidad
            </p>
          </div>
          
          <div class="form-grid">
            <!-- Predios Rurales -->
            <div class="form-group">
              <label for="predios_rurales" class="form-label">
                Predios Rurales
              </label>
              <input
                id="predios_rurales"
                v-model="formulario.predios_rurales"
                type="text"
                class="form-input"
                :class="{ 'error': errores.predios_rurales }"
                placeholder="Ej: 15420"
              />
              <span v-if="errores.predios_rurales" class="error-message">
                {{ errores.predios_rurales }}
              </span>
            </div>
            
            <!-- Área Terreno Rural (m²) -->
            <div class="form-group">
              <label for="area_terreno_rural_m2" class="form-label">
                Área Terreno Rural (m²)
              </label>
              <input
                id="area_terreno_rural_m2"
                v-model="formulario.area_terreno_rural_m2"
                type="text"
                class="form-input"
                :class="{ 'error': errores.area_terreno_rural_m2 }"
                placeholder="Ej: 1256789000"
              />
              <span v-if="errores.area_terreno_rural_m2" class="error-message">
                {{ errores.area_terreno_rural_m2 }}
              </span>
            </div>
            
            <!-- Área Terreno Rural (Ha) -->
            <div class="form-group">
              <label for="area_terreno_rural_ha" class="form-label">
                Área Terreno Rural (Ha)
              </label>
              <input
                id="area_terreno_rural_ha"
                v-model="formulario.area_terreno_rural_ha"
                type="text"
                class="form-input"
                :class="{ 'error': errores.area_terreno_rural_ha }"
                placeholder="Ej: 125678.9"
              />
              <span v-if="errores.area_terreno_rural_ha" class="error-message">
                {{ errores.area_terreno_rural_ha }}
              </span>
            </div>
            
            <!-- Área Construida Rural (m²) -->
            <div class="form-group">
              <label for="area_construida_rural_m2" class="form-label">
                Área Construida Rural (m²)
              </label>
              <input
                id="area_construida_rural_m2"
                v-model="formulario.area_construida_rural_m2"
                type="text"
                class="form-input"
                :class="{ 'error': errores.area_construida_rural_m2 }"
                placeholder="Ej: 456789"
              />
              <span v-if="errores.area_construida_rural_m2" class="error-message">
                {{ errores.area_construida_rural_m2 }}
              </span>
            </div>
            
            <!-- Avalúo Rural -->
            <div class="form-group">
              <label for="avaluo_rural" class="form-label">
                Avalúo Rural
              </label>
              <input
                id="avaluo_rural"
                v-model="formulario.avaluo_rural"
                type="text"
                class="form-input"
                :class="{ 'error': errores.avaluo_rural }"
                placeholder="Ej: 125000000000"
              />
              <span v-if="errores.avaluo_rural" class="error-message">
                {{ errores.avaluo_rural }}
              </span>
              <span class="help-text">Valor en pesos colombianos</span>
            </div>
            
            <!-- Área Geográfica Rural (Ha) -->
            <div class="form-group">
              <label for="area_geografica_rural_ha" class="form-label">
                Área Geográfica Rural (Ha)
              </label>
              <input
                id="area_geografica_rural_ha"
                v-model="formulario.area_geografica_rural_ha"
                type="text"
                class="form-input"
                :class="{ 'error': errores.area_geografica_rural_ha }"
                placeholder="Ej: 128000.5"
              />
              <span v-if="errores.area_geografica_rural_ha" class="error-message">
                {{ errores.area_geografica_rural_ha }}
              </span>
            </div>
            
            <!-- Área Rural Estados Catastrales (Ha) -->
            <div class="form-group">
              <label for="area_rural_estados_catastrales_ha" class="form-label">
                Área Rural Estados Catastrales (Ha)
              </label>
              <input
                id="area_rural_estados_catastrales_ha"
                v-model="formulario.area_rural_estados_catastrales_ha"
                type="text"
                class="form-input"
                :class="{ 'error': errores.area_rural_estados_catastrales_ha }"
                placeholder="Ej: 125600.0"
              />
              <span v-if="errores.area_rural_estados_catastrales_ha" class="error-message">
                {{ errores.area_rural_estados_catastrales_ha }}
              </span>
            </div>
          </div>
        </div>

        <!-- Información Urbana Completa -->
        <div class="form-section">
          <div class="section-header">
            <h2 class="section-title">
              <i class="material-icons">location_city</i>
              Información Urbana Completa
            </h2>
            <p class="section-description">
              Todos los datos del catastro urbano - opcionales según disponibilidad
            </p>
          </div>
          
          <div class="form-grid">
            <!-- Predios Urbanos -->
            <div class="form-group">
              <label for="predios_urbanos" class="form-label">
                Predios Urbanos
              </label>
              <input
                id="predios_urbanos"
                v-model="formulario.predios_urbanos"
                type="text"
                class="form-input"
                :class="{ 'error': errores.predios_urbanos }"
                placeholder="Ej: 8750"
              />
              <span v-if="errores.predios_urbanos" class="error-message">
                {{ errores.predios_urbanos }}
              </span>
            </div>
            
            <!-- Área Terreno Urbana (m²) -->
            <div class="form-group">
              <label for="area_terreno_urbana_m2" class="form-label">
                Área Terreno Urbana (m²)
              </label>
              <input
                id="area_terreno_urbana_m2"
                v-model="formulario.area_terreno_urbana_m2"
                type="text"
                class="form-input"
                :class="{ 'error': errores.area_terreno_urbana_m2 }"
                placeholder="Ej: 34567800"
              />
              <span v-if="errores.area_terreno_urbana_m2" class="error-message">
                {{ errores.area_terreno_urbana_m2 }}
              </span>
            </div>
            
            <!-- Área Terreno Urbana (Ha) -->
            <div class="form-group">
              <label for="area_terreno_urbana_ha" class="form-label">
                Área Terreno Urbana (Ha)
              </label>
              <input
                id="area_terreno_urbana_ha"
                v-model="formulario.area_terreno_urbana_ha"
                type="text"
                class="form-input"
                :class="{ 'error': errores.area_terreno_urbana_ha }"
                placeholder="Ej: 3456.78"
              />
              <span v-if="errores.area_terreno_urbana_ha" class="error-message">
                {{ errores.area_terreno_urbana_ha }}
              </span>
            </div>
            
            <!-- Área Construida Urbana (m²) -->
            <div class="form-group">
              <label for="area_construida_urbana_m2" class="form-label">
                Área Construida Urbana (m²)
              </label>
              <input
                id="area_construida_urbana_m2"
                v-model="formulario.area_construida_urbana_m2"
                type="text"
                class="form-input"
                :class="{ 'error': errores.area_construida_urbana_m2 }"
                placeholder="Ej: 987654"
              />
              <span v-if="errores.area_construida_urbana_m2" class="error-message">
                {{ errores.area_construida_urbana_m2 }}
              </span>
            </div>
            
            <!-- Avalúo Urbano 1 -->
            <div class="form-group">
              <label for="avaluo_urbano_1" class="form-label">
                Avalúo Urbano 1
              </label>
              <input
                id="avaluo_urbano_1"
                v-model="formulario.avaluo_urbano_1"
                type="text"
                class="form-input"
                :class="{ 'error': errores.avaluo_urbano_1 }"
                placeholder="Ej: 89000000000"
              />
              <span v-if="errores.avaluo_urbano_1" class="error-message">
                {{ errores.avaluo_urbano_1 }}
              </span>
              <span class="help-text">Valor en pesos colombianos</span>
            </div>
            
            <!-- Avalúo Urbano 2 -->
            <div class="form-group">
              <label for="avaluo_urbano_2" class="form-label">
                Avalúo Urbano 2
              </label>
              <input
                id="avaluo_urbano_2"
                v-model="formulario.avaluo_urbano_2"
                type="text"
                class="form-input"
                :class="{ 'error': errores.avaluo_urbano_2 }"
                placeholder="Ej: 92000000000"
              />
              <span v-if="errores.avaluo_urbano_2" class="error-message">
                {{ errores.avaluo_urbano_2 }}
              </span>
              <span class="help-text">Valor en pesos colombianos</span>
            </div>
            
            <!-- Área Geográfica Urbana (Ha) -->
            <div class="form-group">
              <label for="area_geografica_urbana_ha" class="form-label">
                Área Geográfica Urbana (Ha)
              </label>
              <input
                id="area_geografica_urbana_ha"
                v-model="formulario.area_geografica_urbana_ha"
                type="text"
                class="form-input"
                :class="{ 'error': errores.area_geografica_urbana_ha }"
                placeholder="Ej: 3500.2"
              />
              <span v-if="errores.area_geografica_urbana_ha" class="error-message">
                {{ errores.area_geografica_urbana_ha }}
              </span>
            </div>
            
            <!-- Área Urbana Estados Catastrales (Ha) -->
            <div class="form-group">
              <label for="area_urbana_estados_catastrales_ha" class="form-label">
                Área Urbana Estados Catastrales (Ha)
              </label>
              <input
                id="area_urbana_estados_catastrales_ha"
                v-model="formulario.area_urbana_estados_catastrales_ha"
                type="text"
                class="form-input"
                :class="{ 'error': errores.area_urbana_estados_catastrales_ha }"
                placeholder="Ej: 3450.0"
              />
              <span v-if="errores.area_urbana_estados_catastrales_ha" class="error-message">
                {{ errores.area_urbana_estados_catastrales_ha }}
              </span>
            </div>
          </div>
        </div>

        <!-- Totales Consolidados -->
        <div class="form-section">
          <div class="section-header">
            <h2 class="section-title">
              <i class="material-icons">calculate</i>
              Totales Consolidados
            </h2>
            <p class="section-description">
              Totales generales del municipio - opcionales según disponibilidad
            </p>
          </div>
          
          <div class="form-grid">
            <!-- Total Predios -->
            <div class="form-group">
              <label for="total_predios" class="form-label">
                Total Predios
              </label>
              <input
                id="total_predios"
                v-model="formulario.total_predios"
                type="text"
                class="form-input"
                :class="{ 'error': errores.total_predios }"
                placeholder="Ej: 24170"
              />
              <span v-if="errores.total_predios" class="error-message">
                {{ errores.total_predios }}
              </span>
            </div>
            
            <!-- Total Área Terreno (m²) -->
            <div class="form-group">
              <label for="total_area_terreno_m2" class="form-label">
                Total Área Terreno (m²)
              </label>
              <input
                id="total_area_terreno_m2"
                v-model="formulario.total_area_terreno_m2"
                type="text"
                class="form-input"
                :class="{ 'error': errores.total_area_terreno_m2 }"
                placeholder="Ej: 1291356800"
              />
              <span v-if="errores.total_area_terreno_m2" class="error-message">
                {{ errores.total_area_terreno_m2 }}
              </span>
            </div>
            
            <!-- Total Área Terreno (Ha) -->
            <div class="form-group">
              <label for="total_area_terreno_ha" class="form-label">
                Total Área Terreno (Ha)
              </label>
              <input
                id="total_area_terreno_ha"
                v-model="formulario.total_area_terreno_ha"
                type="text"
                class="form-input"
                :class="{ 'error': errores.total_area_terreno_ha }"
                placeholder="Ej: 129135.68"
              />
              <span v-if="errores.total_area_terreno_ha" class="error-message">
                {{ errores.total_area_terreno_ha }}
              </span>
            </div>
            
            <!-- Total Área Construida (m²) -->
            <div class="form-group">
              <label for="total_area_construida_m2" class="form-label">
                Total Área Construida (m²)
              </label>
              <input
                id="total_area_construida_m2"
                v-model="formulario.total_area_construida_m2"
                type="text"
                class="form-input"
                :class="{ 'error': errores.total_area_construida_m2 }"
                placeholder="Ej: 1444443"
              />
              <span v-if="errores.total_area_construida_m2" class="error-message">
                {{ errores.total_area_construida_m2 }}
              </span>
            </div>
            
            <!-- Total Avalúos -->
            <div class="form-group">
              <label for="total_avaluos" class="form-label">
                Total Avalúos
              </label>
              <input
                id="total_avaluos"
                v-model="formulario.total_avaluos"
                type="text"
                class="form-input"
                :class="{ 'error': errores.total_avaluos }"
                placeholder="Ej: 306000000000"
              />
              <span v-if="errores.total_avaluos" class="error-message">
                {{ errores.total_avaluos }}
              </span>
              <span class="help-text">Valor total en pesos colombianos</span>
            </div>
          </div>
        </div>

        <!-- Observaciones -->
        <div class="form-section">
          <div class="section-header">
            <h2 class="section-title">
              <i class="material-icons">note</i>
              Observaciones
            </h2>
            <p class="section-description">
              Información adicional o comentarios sobre la información administrativa
            </p>
          </div>
          
          <div class="form-group">
            <label for="observacion" class="form-label">
              Observaciones
            </label>
            <textarea
              id="observacion"
              v-model="formulario.observacion"
              class="form-textarea"
              :class="{ 'error': errores.observacion }"
              placeholder="Escriba cualquier observación adicional sobre la información administrativa..."
              rows="4"
              maxlength="1000"
            ></textarea>
            <span v-if="errores.observacion" class="error-message">
              {{ errores.observacion }}
            </span>
            <span class="help-text">
              Máximo 1000 caracteres ({{ (formulario.observacion || '').length }}/1000)
            </span>
          </div>
        </div>

        <!-- Información de Referencia (Solo vista) -->
        <div v-if="municipioSeleccionado" class="form-section info-section">
          <div class="section-header">
            <h2 class="section-title">
              <i class="material-icons">location_on</i>
              Información de Ubicación
            </h2>
          </div>
          
          <div class="info-display">
            <div class="info-item">
              <span class="info-label">Departamento:</span>
              <span class="info-value">{{ departamentoSeleccionado?.nom_depto }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Municipio:</span>
              <span class="info-value">{{ municipioSeleccionado.nom_municipio }} ({{ municipioSeleccionado.cod_municipio }})</span>
            </div>
          </div>
        </div>

        <!-- Botones de acción -->
        <div class="form-actions">
          <div class="actions-left">
            <router-link 
              to="/gestion-informacion/info-administrativa" 
              class="btn btn-outline"
            >
              <i class="material-icons">arrow_back</i>
              Cancelar
            </router-link>
          </div>
          
          <div class="actions-right">
            <button 
              v-if="modoEdicion"
              type="button" 
              @click="resetearFormulario"
              class="btn btn-outline"
              :disabled="guardando"
            >
              <i class="material-icons">refresh</i>
              Resetear
            </button>
            
            <button 
              type="submit" 
              class="btn btn-primary"
              :disabled="guardando || !formularioValido"
            >
              <i v-if="guardando" class="material-icons spinning">sync</i>
              <i v-else class="material-icons">{{ modoEdicion ? 'save' : 'add' }}</i>
              {{ guardando ? 'Guardando...' : (modoEdicion ? 'Actualizar' : 'Crear') }}
            </button>
          </div>
        </div>
      </form>
    </div>

    <!-- Modal de confirmación -->
    <div v-if="mostrarModalConfirmacion" class="modal-overlay" @click="cancelarConfirmacion">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Confirmar Acción</h3>
          <button @click="cancelarConfirmacion" class="modal-close">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="confirmation-icon">
            <i class="material-icons">{{ modoEdicion ? 'edit' : 'add_circle' }}</i>
          </div>
          <p>
            ¿Está seguro de que desea {{ modoEdicion ? 'actualizar' : 'crear' }} 
            esta información administrativa?
          </p>
          <div class="info-preview">
            <div class="preview-item">
              <strong>Municipio:</strong> {{ municipioSeleccionado?.nom_municipio }}
            </div>
            <div class="preview-item">
              <strong>Departamento:</strong> {{ departamentoSeleccionado?.nom_depto }}
            </div>
            <div class="preview-item" v-if="formulario.gestor_prestador_servicio">
              <strong>Gestor:</strong> {{ formulario.gestor_prestador_servicio }}
            </div>
            <div class="preview-item" v-if="formulario.vigencia_rural || formulario.vigencia_urbana">
              <strong>Vigencias:</strong> Rural {{ formulario.vigencia_rural || 'N/A' }} - Urbana {{ formulario.vigencia_urbana || 'N/A' }}
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="cancelarConfirmacion" class="btn btn-outline">
            Cancelar
          </button>
          <button @click="confirmarGuardado" class="btn btn-primary">
            <i class="material-icons">{{ modoEdicion ? 'save' : 'add' }}</i>
            {{ modoEdicion ? 'Actualizar' : 'Crear' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

// Importar APIs REALES
import { departamentosApi, getMunicipiosByDepartamento, getMunicipios } from '@/api/municipios'
import { infoAdministrativaApi } from '@/api/infoAdministrativa'
import type { InfoAdministrativaForm } from '@/api/infoAdministrativa'

// Interface completa para el formulario con TODAS las 30 columnas
interface InfoAdminFormData {
  cod_municipio: string
  id_gestor_catas: string
  gestor_prestador_servicio: string
  publicacion_year: string
  vigencia_rural: string
  vigencia_urbana: string
  estado_rural: string
  estado_urbano: string
  predios_rurales: string
  area_terreno_rural_m2: string
  area_terreno_rural_ha: string
  area_construida_rural_m2: string
  avaluo_rural: string
  predios_urbanos: string
  area_terreno_urbana_m2: string
  area_terreno_urbana_ha: string
  area_construida_urbana_m2: string
  avaluo_urbano_1: string
  avaluo_urbano_2: string
  total_predios: string
  total_area_terreno_m2: string
  total_area_terreno_ha: string
  total_area_construida_m2: string
  total_avaluos: string
  area_geografica_rural_ha: string
  area_geografica_urbana_ha: string
  area_rural_estados_catastrales_ha: string
  area_urbana_estados_catastrales_ha: string
  observacion: string
}

interface Departamento {
  cod_depto: number
  nom_depto: string
}

interface Municipio {
  cod_municipio: number
  nom_municipio: string
  cod_depto: number
}

export default defineComponent({
  name: 'InfoAdministrativaForm',
  
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    // Estado reactivo
    const cargandoDatos = ref(false)
    const cargandoMunicipios = ref(false)
    const guardando = ref(false)
    const mostrarModalConfirmacion = ref(false)
    const error = ref<string | null>(null)
    
    // Datos
    const departamentos = ref<Departamento[]>([])
    const municipios = ref<Municipio[]>([])
    const errores = ref<Record<string, string>>({})
    
    // Filtros para selección
    const filtros = ref({
      departamento: ''
    })
    
    // Modo de edición
    const modoEdicion = computed(() => !!route.params.id)
    const infoId = computed(() => route.params.id as string)
    
    // Formulario con campos principales
    const formulario = ref<InfoAdminFormData>({
      cod_municipio: '',
      id_gestor_catas: '',
      gestor_prestador_servicio: '',
      publicacion_year: '',
      vigencia_rural: '',
      vigencia_urbana: '',
      estado_rural: '',
      estado_urbano: '',
      predios_rurales: '',
      predios_urbanos: '',
      area_terreno_rural_ha: '',
      area_terreno_urbana_ha: '',
      avaluo_rural: '',
      avaluo_urbano_1: '',
      total_predios: '',
      total_avaluos: '',
      observacion: ''
    })
    
    // Computed properties
    const municipiosDisponibles = computed(() => {
      if (!filtros.value.departamento) return []
      
      return municipios.value
        .filter(m => m.cod_depto.toString() === filtros.value.departamento.toString())
        .sort((a, b) => a.nom_municipio.localeCompare(b.nom_municipio))
    })
    
    const municipioSeleccionado = computed(() => 
      municipios.value.find(m => m.cod_municipio.toString() === formulario.value.cod_municipio.toString())
    )
    
    const departamentoSeleccionado = computed(() => 
      departamentos.value.find(d => d.cod_depto.toString() === filtros.value.departamento.toString())
    )
    
    const formularioValido = computed(() => {
      return formulario.value.cod_municipio !== '' && Object.keys(errores.value).length === 0
    })
    
    // Métodos principales
    const cargarDatos = async () => {
      try {
        cargandoDatos.value = true
        error.value = null
        
        console.log('🚀 Cargando datos iniciales...')
        
        // 1. Cargar departamentos
        const deptosData = await departamentosApi.getAll()
        departamentos.value = Array.isArray(deptosData) ? deptosData : []
        console.log('✅ Departamentos cargados:', departamentos.value.length)
        
        // 2. Cargar algunos municipios iniciales
        await cargarMunicipiosIniciales()
        
        // 3. Si estamos en modo edición, cargar datos de la información administrativa
        if (modoEdicion.value) {
          await cargarInfoAdministrativa()
        }
        
      } catch (err) {
        console.error('❌ Error al cargar datos:', err)
        error.value = `Error al cargar datos: ${err.message}`
      } finally {
        cargandoDatos.value = false
      }
    }
    
    const cargarMunicipiosIniciales = async () => {
      try {
        console.log('📍 Cargando municipios iniciales...')
        
        try {
          const munsData = await getMunicipios()
          municipios.value = Array.isArray(munsData) ? munsData.slice(0, 100) : []
          console.log('✅ Municipios iniciales cargados:', municipios.value.length)
        } catch (error1) {
          console.warn('⚠️ Error con API directa, cargando por departamentos...')
          
          for (const depto of departamentos.value.slice(0, 3)) {
            try {
              const munsDepto = await getMunicipiosByDepartamento(depto.cod_depto)
              const munsArray = Array.isArray(munsDepto) ? munsDepto : []
              
              munsArray.forEach(mun => {
                if (!municipios.value.find(m => m.cod_municipio === mun.cod_municipio)) {
                  municipios.value.push(mun)
                }
              })
            } catch (error2) {
              console.warn(`Error cargando municipios de ${depto.nom_depto}:`, error2)
            }
          }
        }
        
      } catch (error) {
        console.warn('⚠️ Error cargando municipios iniciales:', error)
      }
    }
    
    const cargarInfoAdministrativa = async () => {
      try {
        console.log('🔍 Cargando información administrativa para edición:', infoId.value)
        
        const infoData = await infoAdministrativaApi.getById(infoId.value)
        
        // Asignar datos de la información administrativa
        formulario.value = {
          cod_municipio: infoData.cod_municipio?.toString() || '',
          id_gestor_catas: infoData.id_gestor_catas || '',
          gestor_prestador_servicio: infoData.gestor_prestador_servicio || '',
          publicacion_year: infoData.publicacion_year || '',
          vigencia_rural: infoData.vigencia_rural || '',
          vigencia_urbana: infoData.vigencia_urbana || '',
          estado_rural: infoData.estado_rural || '',
          estado_urbano: infoData.estado_urbano || '',
          predios_rurales: infoData.predios_rurales || '',
          predios_urbanos: infoData.predios_urbanos || '',
          area_terreno_rural_ha: infoData.area_terreno_rural_ha || '',
          area_terreno_urbana_ha: infoData.area_terreno_urbana_ha || '',
          avaluo_rural: infoData.avaluo_rural || '',
          avaluo_urbano_1: infoData.avaluo_urbano_1 || '',
          total_predios: infoData.total_predios || '',
          total_avaluos: infoData.total_avaluos || '',
          observacion: infoData.observacion || ''
        }
        
        console.log('📋 Datos de información administrativa cargados:', formulario.value)
        
        // Buscar el municipio correspondiente para configurar filtros
        let municipioData = municipios.value.find(m => 
          m.cod_municipio.toString() === formulario.value.cod_municipio
        )
        
        // Si no se encuentra el municipio, intentar cargarlo
        if (!municipioData && formulario.value.cod_municipio) {
          console.log('🔍 Municipio no encontrado, determinando departamento...')
          
          const codigoMunicipio = parseInt(formulario.value.cod_municipio)
          const codigoDepartamento = Math.floor(codigoMunicipio / 1000)
          
          const departamento = departamentos.value.find(d => d.cod_depto === codigoDepartamento)
          
          if (departamento) {
            console.log(`📍 Departamento encontrado: ${departamento.nom_depto}`)
            filtros.value.departamento = departamento.cod_depto.toString()
            
            await cargarMunicipiosDelDepartamento()
            
            municipioData = municipios.value.find(m => 
              m.cod_municipio.toString() === formulario.value.cod_municipio
            )
          }
        }
        
        // Si encontramos el municipio, configurar el filtro de departamento
        if (municipioData) {
          filtros.value.departamento = municipioData.cod_depto.toString()
          if (municipios.value.filter(m => m.cod_depto === municipioData.cod_depto).length === 0) {
            await cargarMunicipiosDelDepartamento()
          }
          console.log('✅ Filtros configurados correctamente')
        } else {
          console.warn('⚠️ No se pudo encontrar información del municipio')
        }
        
        console.log('✅ Información administrativa cargada para edición exitosamente')
        
      } catch (error) {
        console.error('❌ Error cargando información administrativa:', error)
        error.value = `Error al cargar la información administrativa: ${error.message}`
        throw error
      }
    }
    
    const cargarMunicipiosDelDepartamento = async () => {
      if (!filtros.value.departamento) return
      
      try {
        cargandoMunicipios.value = true
        console.log('📍 Cargando municipios del departamento:', filtros.value.departamento)
        
        const municipiosData = await getMunicipiosByDepartamento(parseInt(filtros.value.departamento))
        const municipiosNuevos = Array.isArray(municipiosData) ? municipiosData : []
        
        if (municipiosNuevos.length > 0) {
          const municipiosIds = new Set(municipios.value.map(m => m.cod_municipio))
          const municipiosFiltrados = municipiosNuevos.filter(m => !municipiosIds.has(m.cod_municipio))
          
          municipios.value = [...municipios.value, ...municipiosFiltrados]
          console.log(`✅ ${municipiosNuevos.length} municipios cargados del departamento`)
        }
        
      } catch (err) {
        console.error('❌ Error al cargar municipios del departamento:', err)
        error.value = `Error al cargar municipios: ${err.message}`
      } finally {
        cargandoMunicipios.value = false
      }
    }
    
    const validarFormulario = () => {
      const nuevosErrores: Record<string, string> = {}
      
      // Validar municipio (obligatorio)
      const municipioId = formulario.value.cod_municipio?.toString().trim()
      if (!municipioId) {
        nuevosErrores.cod_municipio = 'Debe seleccionar un municipio'
      } else {
        const municipioNum = parseInt(municipioId)
        if (isNaN(municipioNum) || municipioNum <= 0) {
          nuevosErrores.cod_municipio = 'Código de municipio inválido'
        }
      }
      
      // Validar año de publicación (opcional, pero si se proporciona debe ser válido)
      if (formulario.value.publicacion_year) {
        const year = parseInt(formulario.value.publicacion_year)
        if (isNaN(year) || year < 1900 || year > 2100) {
          nuevosErrores.publicacion_year = 'Año de publicación debe estar entre 1900 y 2100'
        }
      }
      
      // Validar vigencias (opcional, pero si se proporciona debe ser válido)
      if (formulario.value.vigencia_rural) {
        const year = parseInt(formulario.value.vigencia_rural)
        if (isNaN(year) || year < 1900 || year > 2100) {
          nuevosErrores.vigencia_rural = 'Vigencia rural debe estar entre 1900 y 2100'
        }
      }
      
      if (formulario.value.vigencia_urbana) {
        const year = parseInt(formulario.value.vigencia_urbana)
        if (isNaN(year) || year < 1900 || year > 2100) {
          nuevosErrores.vigencia_urbana = 'Vigencia urbana debe estar entre 1900 y 2100'
        }
      }
      
      // Validar observación (opcional, pero límite de caracteres)
      if (formulario.value.observacion && formulario.value.observacion.length > 1000) {
        nuevosErrores.observacion = 'Las observaciones no pueden exceder 1000 caracteres'
      }
      
      // Validar departamento (filtro)
      if (!filtros.value.departamento) {
        nuevosErrores.departamento = 'Debe seleccionar un departamento'
      }
      
      errores.value = nuevosErrores
      return Object.keys(nuevosErrores).length === 0
    }
    
    // Event handlers
    const onDepartamentoChange = async () => {
      // Limpiar municipio seleccionado
      if (!modoEdicion.value) {
        formulario.value.cod_municipio = ''
      }
      
      // Limpiar error de departamento
      if (errores.value.departamento) {
        delete errores.value.departamento
      }
      
      if (filtros.value.departamento) {
        await cargarMunicipiosDelDepartamento()
      }
    }
    
    const onMunicipioChange = () => {
      // Limpiar error de municipio
      if (errores.value.cod_municipio) {
        delete errores.value.cod_municipio
      }
    }
    
    const guardarInformacion = () => {
      if (validarFormulario()) {
        mostrarModalConfirmacion.value = true
      }
    }
    
    const confirmarGuardado = async () => {
      try {
        guardando.value = true
        mostrarModalConfirmacion.value = false
        
        console.log('💾 Guardando información administrativa:', formulario.value)
        
        try {
          if (modoEdicion.value) {
            // Actualizar información administrativa existente
            await infoAdministrativaApi.update(infoId.value, formulario.value)
            console.log('✅ Información administrativa actualizada en la BD')
          } else {
            // Crear nueva información administrativa
            await infoAdministrativaApi.create(formulario.value)
            console.log('✅ Información administrativa creada en la BD')
          }
          
          // Mensaje de éxito
          alert(`Información administrativa ${modoEdicion.value ? 'actualizada' : 'creada'} exitosamente`)
          
          // Redirigir a la lista
          router.push('/gestion-informacion/info-administrativa')
          
        } catch (apiError) {
          console.error('❌ Error en la API:', apiError)
          
          if (apiError.response?.status === 400) {
            alert('Error de validación: Verifique que todos los datos sean correctos')
          } else if (apiError.response?.status === 409) {
            alert('Error: Ya existe información administrativa para este municipio')
          } else {
            alert(`Error al guardar en la base de datos: ${apiError.message}`)
          }
        }
        
      } catch (error) {
        console.error('❌ Error general:', error)
        alert(`Error inesperado: ${error.message}`)
      } finally {
        guardando.value = false
      }
    }
    
    const cancelarConfirmacion = () => {
      mostrarModalConfirmacion.value = false
    }
    
    const resetearFormulario = () => {
      if (modoEdicion.value) {
        cargarInfoAdministrativa()
      } else {
        formulario.value = {
          cod_municipio: '',
          id_gestor_catas: '',
          gestor_prestador_servicio: '',
          publicacion_year: '',
          vigencia_rural: '',
          vigencia_urbana: '',
          estado_rural: '',
          estado_urbano: '',
          predios_rurales: '',
          predios_urbanos: '',
          area_terreno_rural_ha: '',
          area_terreno_urbana_ha: '',
          avaluo_rural: '',
          avaluo_urbano_1: '',
          total_predios: '',
          total_avaluos: '',
          observacion: ''
        }
        filtros.value.departamento = ''
      }
      errores.value = {}
    }
    
    // Watchers para limpiar errores
    watch(() => formulario.value.cod_municipio, () => {
      if (errores.value.cod_municipio) {
        delete errores.value.cod_municipio
      }
    })
    
    // Lifecycle
    onMounted(() => {
      cargarDatos()
    })
    
    return {
      // Estado
      cargandoDatos,
      cargandoMunicipios,
      guardando,
      mostrarModalConfirmacion,
      error,
      modoEdicion,
      
      // Datos
      departamentos,
      municipios,
      errores,
      filtros,
      formulario,
      
      // Computed
      municipiosDisponibles,
      municipioSeleccionado,
      departamentoSeleccionado,
      formularioValido,
      
      // Métodos
      cargarDatos,
      onDepartamentoChange,
      onMunicipioChange,
      guardarInformacion,
      confirmarGuardado,
      cancelarConfirmacion,
      resetearFormulario
    }
  }
})
</script>

<style scoped>
.info-admin-form {
  padding: 1.5rem;
  max-width: 1000px;
  margin: 0 auto;
}

/* Header */
.page-header {
  margin-bottom: 2rem;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.breadcrumb-link {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #3b82f6;
  text-decoration: none;
}

.breadcrumb-link:hover {
  text-decoration: underline;
}

.breadcrumb-separator {
  color: #9ca3af;
  font-size: 1rem;
}

.breadcrumb-current {
  color: #6b7280;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.5rem 0;
  font-size: 1.75rem;
  font-weight: 600;
  color: #1f2937;
}

.page-description {
  color: #6b7280;
  margin: 0;
  font-size: 1rem;
}

/* Estados */
.loading-container, .error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-container i {
  font-size: 3rem;
  color: #ef4444;
  margin-bottom: 1rem;
}

/* Formulario */
.form-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.info-admin-form-content {
  padding: 2rem;
}

.form-section {
  margin-bottom: 2.5rem;
}

.form-section:last-of-type {
  margin-bottom: 0;
}

.section-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.section-description {
  color: #6b7280;
  margin: 0;
  font-size: 0.875rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-label.required::after {
  content: ' *';
  color: #ef4444;
}

.contador-opciones {
  color: #6c757d;
  font-size: 0.75rem;
  font-weight: normal;
  background-color: #f8f9fa;
  padding: 0.15rem 0.4rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.form-input,
.form-select,
.form-textarea {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input.error,
.form-select.error,
.form-textarea.error {
  border-color: #ef4444;
}

.form-input:disabled,
.form-select:disabled {
  background: #f9fafb;
  color: #6b7280;
  cursor: not-allowed;
}

.form-select.has-selection {
  border-color: #3b82f6;
  background-color: #f0f8ff;
  font-weight: 500;
}

.form-select.loading {
  background-image: url("data:image/svg+xml,%3csvg width='16' height='16' viewBox='0 0 16 16' fill='none' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='M8 2v2M8 12v2M13.657 8h-2M4.343 8h-2M11.314 4.686l-1.414 1.414M6.1 9.9l-1.414 1.414M11.314 11.314l-1.414-1.414M6.1 6.1L4.686 4.686' stroke='%23007bff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 16px;
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.error-message {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.help-text {
  color: #6b7280;
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

/* Sección de información */
.info-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  margin-top: 1rem;
}

.info-display {
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
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.info-value {
  font-size: 1rem;
  color: #1f2937;
  font-weight: 500;
}

/* Botones de acción */
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.actions-left,
.actions-right {
  display: flex;
  gap: 1rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  text-decoration: none;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 120px;
  justify-content: center;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-outline {
  background: white;
  color: #374151;
  border-color: #d1d5db;
}

.btn-outline:hover:not(:disabled) {
  background: #f3f4f6;
}

.spinning {
  animation: spin 1s linear infinite;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  color: #6b7280;
}

.modal-body {
  padding: 1.5rem;
  text-align: center;
}

.confirmation-icon {
  margin-bottom: 1rem;
}

.confirmation-icon i {
  font-size: 3rem;
  color: #3b82f6;
}

.info-preview {
  background: #f3f4f6;
  padding: 1rem;
  border-radius: 6px;
  margin: 1rem 0;
  text-align: left;
}

.preview-item {
  margin-bottom: 0.5rem;
}

.preview-item:last-child {
  margin-bottom: 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

/* Responsive */
@media (max-width: 768px) {
  .info-admin-form {
    padding: 1rem;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .actions-left,
  .actions-right {
    width: 100%;
    justify-content: center;
  }
  
  .info-display {
    grid-template-columns: 1fr;
  }
}
</style>