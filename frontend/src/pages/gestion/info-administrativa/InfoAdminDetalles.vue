<template>
  <div class="info-admin-detalles">
    <!-- Header con navegación -->
    <div class="page-header">
      <div class="header-content">
        <nav class="breadcrumb">
          <router-link to="/gestion-informacion/info-administrativa" class="breadcrumb-link">
            <i class="material-icons">admin_panel_settings</i>
            Información Administrativa
          </router-link>
          <i class="material-icons breadcrumb-separator">chevron_right</i>
          <span class="breadcrumb-current">Detalles</span>
        </nav>
        
        <div v-if="loading" class="title-skeleton">
          <div class="skeleton-line long"></div>
          <div class="skeleton-line short"></div>
        </div>
        
        <div v-else-if="infoAdministrativa" class="title-section">
          <h1 class="page-title">
            <i class="material-icons">description</i>
            Información Administrativa
          </h1>
          <div class="subtitle-info">
            <span class="codigo-badge">ID: {{ infoAdministrativa.cod_info_admin }}</span>
            <span class="ubicacion">
              {{ infoAdministrativa.municipio_nombre }} - {{ infoAdministrativa.departamento_nombre }}
            </span>
          </div>
        </div>
      </div>
      
      <div v-if="!loading && infoAdministrativa" class="header-actions">
        <button 
          @click="descargarExcel"
          class="btn btn-success"
          :disabled="descargando"
        >
          <i v-if="descargando" class="material-icons spinning">sync</i>
          <i v-else class="material-icons">file_download</i>
          {{ descargando ? 'Generando...' : 'Descargar Excel' }}
        </button>
        
        <router-link 
          :to="`/gestion-informacion/info-administrativa/${infoAdministrativa.cod_info_admin}/editar`"
          class="btn btn-primary"
        >
          <i class="material-icons">edit</i>
          Editar
        </router-link>
        
        <router-link 
          to="/gestion-informacion/info-administrativa"
          class="btn btn-outline"
        >
          <i class="material-icons">arrow_back</i>
          Volver
        </router-link>
      </div>
    </div>

    <!-- Estados de carga -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Cargando información administrativa...</p>
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

    <!-- Contenido principal -->
    <div v-else-if="infoAdministrativa" class="details-container">
      
      <!-- Información de Ubicación -->
      <div class="info-card">
        <div class="card-header">
          <h2 class="card-title">
            <i class="material-icons">location_on</i>
            Información de Ubicación
          </h2>
        </div>
        
        <div class="card-content">
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">ID Registro</span>
              <span class="info-value code-value">{{ infoAdministrativa.cod_info_admin }}</span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Código Municipio</span>
              <span class="info-value code-value">{{ infoAdministrativa.cod_municipio }}</span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Municipio</span>
              <router-link 
                v-if="infoAdministrativa.cod_municipio"
                :to="`/gestion-informacion/municipios/${infoAdministrativa.cod_municipio}`"
                class="info-link"
              >
                {{ infoAdministrativa.municipio_nombre }}
                <i class="material-icons">open_in_new</i>
              </router-link>
              <span v-else class="info-value">{{ infoAdministrativa.municipio_nombre }}</span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Departamento</span>
              <span class="info-value">{{ infoAdministrativa.departamento_nombre }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Información General del Catastro -->
      <div class="info-card">
        <div class="card-header">
          <h2 class="card-title">
            <i class="material-icons">business</i>
            Información General del Catastro
          </h2>
        </div>
        
        <div class="card-content">
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">ID Gestor Catastral</span>
              <span class="info-value">{{ infoAdministrativa.id_gestor_catas || 'No especificado' }}</span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Gestor Prestador Servicio</span>
              <span class="info-value">{{ infoAdministrativa.gestor_prestador_servicio || 'No especificado' }}</span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Año de Publicación</span>
              <span class="info-value">
                {{ infoAdministrativa.publicacion_year || 'No especificado' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Vigencias y Estados -->
      <div class="info-card">
        <div class="card-header">
          <h2 class="card-title">
            <i class="material-icons">schedule</i>
            Vigencias y Estados
          </h2>
        </div>
        
        <div class="card-content">
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Vigencia Rural</span>
              <span :class="['vigencia-badge', getVigenciaClass(infoAdministrativa.vigencia_rural)]">
                {{ infoAdministrativa.vigencia_rural || 'No especificada' }}
              </span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Vigencia Urbana</span>
              <span :class="['vigencia-badge', getVigenciaClass(infoAdministrativa.vigencia_urbana)]">
                {{ infoAdministrativa.vigencia_urbana || 'No especificada' }}
              </span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Estado Rural</span>
              <span :class="['estado-badge', getEstadoClass(infoAdministrativa.estado_rural)]">
                {{ infoAdministrativa.estado_rural || 'No especificado' }}
              </span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Estado Urbano</span>
              <span :class="['estado-badge', getEstadoClass(infoAdministrativa.estado_urbano)]">
                {{ infoAdministrativa.estado_urbano || 'No especificado' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Información Rural -->
      <div class="info-card">
        <div class="card-header">
          <h2 class="card-title">
            <i class="material-icons">agriculture</i>
            Información Rural
          </h2>
        </div>
        
        <div class="card-content">
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Predios Rurales</span>
              <span class="info-value metric-value">
                {{ formatNumber(infoAdministrativa.predios_rurales) || 'No especificado' }}
                <span v-if="infoAdministrativa.predios_rurales" class="unit">predios</span>
              </span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Área Terreno Rural (m²)</span>
              <span class="info-value metric-value">
                {{ formatNumber(infoAdministrativa.area_terreno_rural_m2) || 'No especificado' }}
                <span v-if="infoAdministrativa.area_terreno_rural_m2" class="unit">m²</span>
              </span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Área Terreno Rural (Ha)</span>
              <span class="info-value metric-value">
                {{ formatNumber(infoAdministrativa.area_terreno_rural_ha) || 'No especificado' }}
                <span v-if="infoAdministrativa.area_terreno_rural_ha" class="unit">Ha</span>
              </span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Área Construida Rural (m²)</span>
              <span class="info-value metric-value">
                {{ formatNumber(infoAdministrativa.area_construida_rural_m2) || 'No especificado' }}
                <span v-if="infoAdministrativa.area_construida_rural_m2" class="unit">m²</span>
              </span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Avalúo Rural</span>
              <span class="info-value currency-value">
                {{ formatCurrency(infoAdministrativa.avaluo_rural) || 'No especificado' }}
              </span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Área Geográfica Rural (Ha)</span>
              <span class="info-value metric-value">
                {{ formatNumber(infoAdministrativa.area_geografica_rural_ha) || 'No especificado' }}
                <span v-if="infoAdministrativa.area_geografica_rural_ha" class="unit">Ha</span>
              </span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Área Rural Estados Catastrales (Ha)</span>
              <span class="info-value metric-value">
                {{ formatNumber(infoAdministrativa.area_rural_estados_catastrales_ha) || 'No especificado' }}
                <span v-if="infoAdministrativa.area_rural_estados_catastrales_ha" class="unit">Ha</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Información Urbana -->
      <div class="info-card">
        <div class="card-header">
          <h2 class="card-title">
            <i class="material-icons">location_city</i>
            Información Urbana
          </h2>
        </div>
        
        <div class="card-content">
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Predios Urbanos</span>
              <span class="info-value metric-value">
                {{ formatNumber(infoAdministrativa.predios_urbanos) || 'No especificado' }}
                <span v-if="infoAdministrativa.predios_urbanos" class="unit">predios</span>
              </span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Área Terreno Urbana (m²)</span>
              <span class="info-value metric-value">
                {{ formatNumber(infoAdministrativa.area_terreno_urbana_m2) || 'No especificado' }}
                <span v-if="infoAdministrativa.area_terreno_urbana_m2" class="unit">m²</span>
              </span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Área Terreno Urbana (Ha)</span>
              <span class="info-value metric-value">
                {{ formatNumber(infoAdministrativa.area_terreno_urbana_ha) || 'No especificado' }}
                <span v-if="infoAdministrativa.area_terreno_urbana_ha" class="unit">Ha</span>
              </span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Área Construida Urbana (m²)</span>
              <span class="info-value metric-value">
                {{ formatNumber(infoAdministrativa.area_construida_urbana_m2) || 'No especificado' }}
                <span v-if="infoAdministrativa.area_construida_urbana_m2" class="unit">m²</span>
              </span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Avalúo Urbano 1</span>
              <span class="info-value currency-value">
                {{ formatCurrency(infoAdministrativa.avaluo_urbano_1) || 'No especificado' }}
              </span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Avalúo Urbano 2</span>
              <span class="info-value currency-value">
                {{ formatCurrency(infoAdministrativa.avaluo_urbano_2) || 'No especificado' }}
              </span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Área Geográfica Urbana (Ha)</span>
              <span class="info-value metric-value">
                {{ formatNumber(infoAdministrativa.area_geografica_urbana_ha) || 'No especificado' }}
                <span v-if="infoAdministrativa.area_geografica_urbana_ha" class="unit">Ha</span>
              </span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Área Urbana Estados Catastrales (Ha)</span>
              <span class="info-value metric-value">
                {{ formatNumber(infoAdministrativa.area_urbana_estados_catastrales_ha) || 'No especificado' }}
                <span v-if="infoAdministrativa.area_urbana_estados_catastrales_ha" class="unit">Ha</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Totales Consolidados -->
      <div class="info-card totales-card">
        <div class="card-header">
          <h2 class="card-title">
            <i class="material-icons">calculate</i>
            Totales Consolidados
          </h2>
        </div>
        
        <div class="card-content">
          <div class="info-grid">
            <div class="info-item highlight">
              <span class="info-label">Total Predios</span>
              <span class="info-value total-value">
                {{ formatNumber(infoAdministrativa.total_predios) || 'No especificado' }}
                <span v-if="infoAdministrativa.total_predios" class="unit">predios</span>
              </span>
            </div>
            
            <div class="info-item highlight">
              <span class="info-label">Total Área Terreno (m²)</span>
              <span class="info-value total-value">
                {{ formatNumber(infoAdministrativa.total_area_terreno_m2) || 'No especificado' }}
                <span v-if="infoAdministrativa.total_area_terreno_m2" class="unit">m²</span>
              </span>
            </div>
            
            <div class="info-item highlight">
              <span class="info-label">Total Área Terreno (Ha)</span>
              <span class="info-value total-value">
                {{ formatNumber(infoAdministrativa.total_area_terreno_ha) || 'No especificado' }}
                <span v-if="infoAdministrativa.total_area_terreno_ha" class="unit">Ha</span>
              </span>
            </div>
            
            <div class="info-item highlight">
              <span class="info-label">Total Área Construida (m²)</span>
              <span class="info-value total-value">
                {{ formatNumber(infoAdministrativa.total_area_construida_m2) || 'No especificado' }}
                <span v-if="infoAdministrativa.total_area_construida_m2" class="unit">m²</span>
              </span>
            </div>
            
            <div class="info-item highlight">
              <span class="info-label">Total Avalúos</span>
              <span class="info-value total-currency-value">
                {{ formatCurrency(infoAdministrativa.total_avaluos) || 'No especificado' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Observaciones -->
      <div v-if="infoAdministrativa.observacion" class="info-card">
        <div class="card-header">
          <h2 class="card-title">
            <i class="material-icons">note</i>
            Observaciones
          </h2>
        </div>
        
        <div class="card-content">
          <div class="observacion-content">
            <p>{{ infoAdministrativa.observacion }}</p>
          </div>
        </div>
      </div>

      <!-- Enlaces Relacionados -->
      <div class="info-card">
        <div class="card-header">
          <h2 class="card-title">
            <i class="material-icons">link</i>
            Enlaces Relacionados
          </h2>
        </div>
        
        <div class="card-content">
          <div class="related-links">
            <router-link 
              v-if="infoAdministrativa.cod_municipio"
              :to="`/gestion-informacion/municipios/${infoAdministrativa.cod_municipio}`"
              class="related-link"
            >
              <i class="material-icons">location_city</i>
              <div class="link-content">
                <span class="link-title">Ver Municipio</span>
                <span class="link-description">{{ infoAdministrativa.municipio_nombre }}</span>
              </div>
              <i class="material-icons">chevron_right</i>
            </router-link>
            
            <router-link 
              to="/gestion-informacion/info-administrativa"
              class="related-link"
            >
              <i class="material-icons">list</i>
              <div class="link-content">
                <span class="link-title">Toda la Información Administrativa</span>
                <span class="link-description">Volver a la lista completa</span>
              </div>
              <i class="material-icons">chevron_right</i>
            </router-link>
            
            <router-link 
              :to="`/gestion-informacion/info-administrativa/${infoAdministrativa.cod_info_admin}/editar`"
              class="related-link edit-link"
            >
              <i class="material-icons">edit</i>
              <div class="link-content">
                <span class="link-title">Editar Información</span>
                <span class="link-description">Modificar los datos administrativos</span>
              </div>
              <i class="material-icons">chevron_right</i>
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Estado sin datos -->
    <div v-else class="empty-container">
      <i class="material-icons">description</i>
      <h3>Información administrativa no encontrada</h3>
      <p>No se pudo encontrar la información administrativa solicitada.</p>
      <router-link to="/gestion-informacion/info-administrativa" class="btn btn-primary">
        <i class="material-icons">arrow_back</i>
        Volver a la Lista
      </router-link>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

// Importar APIs REALES
import { getInfoAdministrativaByMunicipio } from '@/api/infoAdministrativa'
import { departamentosApi, getMunicipioById } from '@/api/municipios'

// Interface para la información administrativa completa
interface InfoAdministrativaDetalle {
  cod_info_admin: number
  cod_municipio: number
  id_gestor_catas?: string
  gestor_prestador_servicio?: string
  publicacion_year?: string
  vigencia_rural?: string
  vigencia_urbana?: string
  estado_rural?: string
  estado_urbano?: string
  predios_rurales?: string
  area_terreno_rural_m2?: string
  area_terreno_rural_ha?: string
  area_construida_rural_m2?: string
  avaluo_rural?: string
  predios_urbanos?: string
  area_terreno_urbana_m2?: string
  area_terreno_urbana_ha?: string
  area_construida_urbana_m2?: string
  avaluo_urbano_1?: string
  avaluo_urbano_2?: string
  total_predios?: string
  total_area_terreno_m2?: string
  total_area_terreno_ha?: string
  total_area_construida_m2?: string
  total_avaluos?: string
  area_geografica_rural_ha?: string
  area_geografica_urbana_ha?: string
  area_rural_estados_catastrales_ha?: string
  area_urbana_estados_catastrales_ha?: string
  observacion?: string
  municipio_nombre?: string
  departamento_nombre?: string
}

export default defineComponent({
  name: 'InfoAdministrativaDetalles',
  
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    // Estado reactivo
    const loading = ref(true)
    const descargando = ref(false)
    const error = ref<string | null>(null)
    
    // Datos
    const infoAdministrativa = ref<InfoAdministrativaDetalle | null>(null)
    const infoId = route.params.id as string
    
    // Método principal para cargar datos
    const cargarDatos = async () => {
      try {
        loading.value = true
        error.value = null
        
        console.log('🔍 Cargando información administrativa:', infoId)
        
        // TODO: Implementar API específica para obtener por ID
        // Por ahora, simular con datos de ejemplo basados en el ID
        
        // Simular carga de datos
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Datos de ejemplo (reemplazar con API real)
        const infoData: InfoAdministrativaDetalle = {
          cod_info_admin: parseInt(infoId),
          cod_municipio: 13006,
          id_gestor_catas: 'GC001',
          gestor_prestador_servicio: 'IGAC - Instituto Geográfico Agustín Codazzi',
          publicacion_year: '2023',
          vigencia_rural: '2023',
          vigencia_urbana: '2024',
          estado_rural: 'Vigente',
          estado_urbano: 'Actualizado',
          predios_rurales: '15420',
          area_terreno_rural_m2: '1256789000',
          area_terreno_rural_ha: '125678.9',
          area_construida_rural_m2: '456789',
          avaluo_rural: '125000000000',
          predios_urbanos: '8750',
          area_terreno_urbana_m2: '34567800',
          area_terreno_urbana_ha: '3456.78',
          area_construida_urbana_m2: '987654',
          avaluo_urbano_1: '89000000000',
          avaluo_urbano_2: '92000000000',
          total_predios: '24170',
          total_area_terreno_m2: '1291356800',
          total_area_terreno_ha: '129135.68',
          total_area_construida_m2: '1444443',
          total_avaluos: '306000000000',
          area_geografica_rural_ha: '128000.5',
          area_geografica_urbana_ha: '3500.2',
          area_rural_estados_catastrales_ha: '125600.0',
          area_urbana_estados_catastrales_ha: '3450.0',
          observacion: 'Información actualizada según censo catastral 2023. Pendiente validación de algunas áreas rurales en la zona montañosa del municipio.',
          municipio_nombre: 'Cartagena',
          departamento_nombre: 'Bolívar'
        }
        
        // Enriquecer con información de municipio y departamento
        try {
          const municipioData = await getMunicipioById(infoData.cod_municipio)
          if (municipioData) {
            infoData.municipio_nombre = municipioData.nom_municipio
            
            // Buscar departamento
            const departamentosData = await departamentosApi.getAll()
            const departamento = departamentosData.find(d => d.cod_depto === municipioData.cod_depto)
            if (departamento) {
              infoData.departamento_nombre = departamento.nom_depto
            }
          }
        } catch (err) {
          console.warn('⚠️ Error cargando datos de ubicación:', err)
        }
        
        infoAdministrativa.value = infoData
        
        console.log('✅ Información administrativa completa cargada:', infoAdministrativa.value)
        
      } catch (err) {
        console.error('❌ Error al cargar datos:', err)
        error.value = err.message || 'Error al cargar la información administrativa'
      } finally {
        loading.value = false
      }
    }
    
    // Método para descargar Excel
    const descargarExcel = async () => {
      if (!infoAdministrativa.value) return
      
      try {
        descargando.value = true
        
        console.log('📊 Generando archivo Excel...')
        
        // Simular generación de Excel
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Crear datos para Excel
        const datosExcel = [
          ['INFORMACIÓN ADMINISTRATIVA COMPLETA'],
          [''],
          ['Información de Ubicación'],
          ['ID Registro', infoAdministrativa.value.cod_info_admin],
          ['Código Municipio', infoAdministrativa.value.cod_municipio],
          ['Municipio', infoAdministrativa.value.municipio_nombre],
          ['Departamento', infoAdministrativa.value.departamento_nombre],
          [''],
          ['Información General'],
          ['ID Gestor Catastral', infoAdministrativa.value.id_gestor_catas || ''],
          ['Gestor Prestador Servicio', infoAdministrativa.value.gestor_prestador_servicio || ''],
          ['Año Publicación', infoAdministrativa.value.publicacion_year || ''],
          [''],
          ['Vigencias y Estados'],
          ['Vigencia Rural', infoAdministrativa.value.vigencia_rural || ''],
          ['Vigencia Urbana', infoAdministrativa.value.vigencia_urbana || ''],
          ['Estado Rural', infoAdministrativa.value.estado_rural || ''],
          ['Estado Urbano', infoAdministrativa.value.estado_urbano || ''],
          [''],
          ['Información Rural'],
          ['Predios Rurales', infoAdministrativa.value.predios_rurales || ''],
          ['Área Terreno Rural (m²)', infoAdministrativa.value.area_terreno_rural_m2 || ''],
          ['Área Terreno Rural (Ha)', infoAdministrativa.value.area_terreno_rural_ha || ''],
          ['Área Construida Rural (m²)', infoAdministrativa.value.area_construida_rural_m2 || ''],
          ['Avalúo Rural', infoAdministrativa.value.avaluo_rural || ''],
          ['Área Geográfica Rural (Ha)', infoAdministrativa.value.area_geografica_rural_ha || ''],
          ['Área Rural Estados Catastrales (Ha)', infoAdministrativa.value.area_rural_estados_catastrales_ha || ''],
          [''],
          ['Información Urbana'],
          ['Predios Urbanos', infoAdministrativa.value.predios_urbanos || ''],
          ['Área Terreno Urbana (m²)', infoAdministrativa.value.area_terreno_urbana_m2 || ''],
          ['Área Terreno Urbana (Ha)', infoAdministrativa.value.area_terreno_urbana_ha || ''],
          ['Área Construida Urbana (m²)', infoAdministrativa.value.area_construida_urbana_m2 || ''],
          ['Avalúo Urbano 1', infoAdministrativa.value.avaluo_urbano_1 || ''],
          ['Avalúo Urbano 2', infoAdministrativa.value.avaluo_urbano_2 || ''],
          ['Área Geográfica Urbana (Ha)', infoAdministrativa.value.area_geografica_urbana_ha || ''],
          ['Área Urbana Estados Catastrales (Ha)', infoAdministrativa.value.area_urbana_estados_catastrales_ha || ''],
          [''],
          ['Totales Consolidados'],
          ['Total Predios', infoAdministrativa.value.total_predios || ''],
          ['Total Área Terreno (m²)', infoAdministrativa.value.total_area_terreno_m2 || ''],
          ['Total Área Terreno (Ha)', infoAdministrativa.value.total_area_terreno_ha || ''],
          ['Total Área Construida (m²)', infoAdministrativa.value.total_area_construida_m2 || ''],
          ['Total Avalúos', infoAdministrativa.value.total_avaluos || ''],
          [''],
          ['Observaciones'],
          [infoAdministrativa.value.observacion || 'Sin observaciones']
        ]
        
        // Crear CSV como simulación de Excel
        const BOM = '\uFEFF'
        const csvContent = BOM + datosExcel.map(row => 
          row.map(cell => `"${(cell || '').toString().replace(/"/g, '""')}"`).join(',')
        ).join('\n')
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `info_administrativa_${infoAdministrativa.value.cod_info_admin}_${infoAdministrativa.value.municipio_nombre}_${new Date().toISOString().slice(0, 10)}.csv`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        console.log('✅ Archivo Excel generado exitosamente')
        
      } catch (err) {
        console.error('❌ Error al generar Excel:', err)
        alert('Error al generar el archivo Excel')
      } finally {
        descargando.value = false
      }
    }
    
    // Helpers para formateo
    const formatNumber = (value: string | null | undefined): string => {
      if (!value || value === 'N/A' || value === '') return ''
      
      const num = parseFloat(value.replace(/,/g, ''))
      if (isNaN(num)) return value
      
      return new Intl.NumberFormat('es-CO').format(num)
    }
    
    const formatCurrency = (value: string | null | undefined): string => {
      if (!value || value === 'N/A' || value === '') return ''
      
      const num = parseFloat(value.replace(/,/g, ''))
      if (isNaN(num)) return value
      
      return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(num)
    }
    
    // Helpers para clases CSS de estados (reutilizados de la lista)
    const getVigenciaClass = (vigencia: string | undefined): string => {
      if (!vigencia || vigencia === 'N/A') return 'vigencia-na'
      
      const year = parseInt(vigencia)
      const currentYear = new Date().getFullYear()
      
      if (year >= currentYear - 1) return 'vigencia-actual'
      if (year >= currentYear - 3) return 'vigencia-reciente'
      return 'vigencia-antigua'
    }
    
    const getEstadoClass = (estado: string | undefined): string => {
      if (!estado || estado === 'N/A') return 'estado-na'
      
      const estadoLower = estado.toLowerCase()
      if (estadoLower.includes('vigente') || estadoLower.includes('activo')) return 'estado-vigente'
      if (estadoLower.includes('actualizado')) return 'estado-actualizado'
      if (estadoLower.includes('pendiente')) return 'estado-pendiente'
      if (estadoLower.includes('vencido') || estadoLower.includes('expirado')) return 'estado-vencido'
      
      return 'estado-otro'
    }
    
    // Lifecycle
    onMounted(() => {
      if (infoId) {
        cargarDatos()
      } else {
        error.value = 'ID de información administrativa no proporcionado'
        loading.value = false
      }
    })
    
    return {
      // Estado
      loading,
      descargando,
      error,
      
      // Datos
      infoAdministrativa,
      
      // Métodos
      cargarDatos,
      descargarExcel,
      formatNumber,
      formatCurrency,
      getVigenciaClass,
      getEstadoClass
    }
  }
})
</script>

<style scoped>
.info-admin-detalles {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  gap: 2rem;
}

.header-content {
  flex: 1;
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

.title-skeleton {
  animation: pulse 2s infinite;
}

.skeleton-line {
  height: 1rem;
  background: #e5e7eb;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.skeleton-line.long {
  width: 400px;
  height: 2rem;
}

.skeleton-line.short {
  width: 250px;
}

.title-section {
  margin-bottom: 0;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.75rem 0;
  font-size: 1.875rem;
  font-weight: 600;
  color: #1f2937;
}

.subtitle-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.codigo-badge {
  background: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
  font-family: 'Courier New', monospace;
}

.ubicacion {
  color: #6b7280;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

/* Estados */
.loading-container, .error-container, .empty-container {
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

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.spinning {
  animation: spin 1s linear infinite;
}

.error-container i,
.empty-container i {
  font-size: 3rem;
  color: #ef4444;
  margin-bottom: 1rem;
}

.empty-container i {
  color: #6b7280;
}

/* Contenido */
.details-container {
  display: grid;
  gap: 1.5rem;
}

.info-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.totales-card {
  border: 2px solid #f59e0b;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.1);
}

.card-header {
  padding: 1.5rem 1.5rem 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f8f9fa;
}

.totales-card .card-header {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.card-content {
  padding: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-item.highlight {
  background: #fffbeb;
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid #f59e0b;
}

.info-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  font-size: 1.125rem;
  color: #1f2937;
  font-weight: 500;
  word-break: break-word;
}

.code-value {
  font-family: 'Courier New', monospace;
  background: #f9fafb;
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
  display: inline-block;
}

.metric-value {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-weight: 600;
  color: #0f172a;
}

.currency-value {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-weight: 600;
  color: #059669;
  background: #ecfdf5;
  padding: 0.5rem;
  border-radius: 6px;
  display: inline-block;
}

.total-value {
  font-size: 1.375rem;
  font-weight: 700;
  color: #f59e0b;
}

.total-currency-value {
  font-size: 1.375rem;
  font-weight: 700;
  color: #059669;
  background: #d1fae5;
  padding: 0.75rem;
  border-radius: 8px;
  display: inline-block;
}

.unit {
  color: #6b7280;
  font-size: 0.875rem;
  margin-left: 0.25rem;
  font-weight: 400;
}

.info-link {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  color: #3b82f6;
  text-decoration: none;
  font-size: 1.125rem;
  font-weight: 500;
}

.info-link:hover {
  text-decoration: underline;
}

/* Badges para vigencias y estados (reutilizados) */
.vigencia-badge, .estado-badge {
  padding: 0.375rem 0.875rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
  text-align: center;
  display: inline-block;
  min-width: 80px;
}

.vigencia-badge.vigencia-actual, .estado-badge.estado-vigente {
  background: #dcfce7;
  color: #166534;
}

.vigencia-badge.vigencia-reciente, .estado-badge.estado-actualizado {
  background: #dbeafe;
  color: #1d4ed8;
}

.vigencia-badge.vigencia-antigua, .estado-badge.estado-vencido {
  background: #fee2e2;
  color: #991b1b;
}

.estado-badge.estado-pendiente {
  background: #fef3c7;
  color: #92400e;
}

.estado-badge.estado-otro {
  background: #e0e7ff;
  color: #3730a3;
}

.vigencia-badge.vigencia-na, .estado-badge.estado-na {
  background: #f3f4f6;
  color: #6b7280;
}

/* Observaciones */
.observacion-content {
  background: #f8fafc;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
}

.observacion-content p {
  margin: 0;
  color: #475569;
  line-height: 1.6;
  font-size: 1rem;
}

/* Enlaces relacionados */
.related-links {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.related-link {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  text-decoration: none;
  color: #374151;
  transition: all 0.2s;
  border: 1px solid #e5e7eb;
}

.related-link:hover {
  background: #f3f4f6;
  transform: translateX(4px);
  border-color: #d1d5db;
}

.related-link.edit-link {
  background: #fef3c7;
  border-color: #fbbf24;
}

.related-link.edit-link:hover {
  background: #fde68a;
}

.link-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.link-title {
  font-weight: 600;
  color: #1f2937;
  font-size: 1rem;
}

.link-description {
  font-size: 0.875rem;
  color: #6b7280;
}

/* Botones */
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

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
}

.btn-outline {
  background: white;
  color: #374151;
  border-color: #d1d5db;
}

.btn-outline:hover:not(:disabled) {
  background: #f3f4f6;
}

/* Responsive */
@media (max-width: 768px) {
  .info-admin-detalles {
    padding: 1rem;
  }
  
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .subtitle-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .header-actions {
    justify-content: stretch;
  }
  
  .header-actions .btn {
    flex: 1;
    justify-content: center;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>