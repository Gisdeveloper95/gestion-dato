<template>
  <div class="dominios-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="dashboard-title">
            <i class="material-icons">category</i>
            Gestión de Dominios
          </h1>
          <p class="dashboard-description">
            Administre las 14 tablas de dominio del sistema. 
            Estas tablas contienen los datos maestros y de configuración.
          </p>
        </div>
        <div class="stats-section">
          <div class="stat-card">
            <div class="stat-number">14</div>
            <div class="stat-label">Tablas</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ totalRegistros }}</div>
            <div class="stat-label">Registros</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Navegación por categorías -->
    <div class="dashboard-content">
      <!-- Filtro y búsqueda -->
      <div class="controls-section">
        <div class="search-box">
          <i class="material-icons">search</i>
          <input 
            v-model="filtro" 
            type="text" 
            placeholder="Buscar dominio..."
            class="search-input"
          >
        </div>
        <div class="view-toggle">
          <button 
            @click="vistaCategoria = true" 
            :class="{ active: vistaCategoria }"
            class="toggle-btn"
          >
            <i class="material-icons">category</i>
            Por Categoría
          </button>
          <button 
            @click="vistaCategoria = false" 
            :class="{ active: !vistaCategoria }"
            class="toggle-btn"
          >
            <i class="material-icons">view_list</i>
            Lista
          </button>
        </div>
      </div>

      <!-- Vista por categorías -->
      <div v-if="vistaCategoria" class="categories-view">
        <div 
          v-for="(categoria, nombreCategoria) in dominiosFiltrados" 
          :key="nombreCategoria"
          class="category-section"
        >
          <h2 class="category-title">
            <i class="material-icons">{{ getCategoryIcon(nombreCategoria) }}</i>
            {{ nombreCategoria }}
            <span class="category-count">({{ categoria.length }})</span>
          </h2>
          <div class="dominios-grid">
            <router-link
              v-for="dominio in categoria"
              :key="dominio.key"
              :to="getDominioRoute(dominio.key)"
              class="dominio-card"
            >
              <div class="card-icon">
                <i class="material-icons">{{ getDominioIcon(dominio.key) }}</i>
              </div>
              <div class="card-content">
                <h3 class="card-title">{{ dominio.title }}</h3>
                <p class="card-description">{{ dominio.description }}</p>
                <div class="card-meta">
                  <span class="meta-item">
                    <i class="material-icons">storage</i>
                    {{ dominio.pluralName }}
                  </span>
                </div>
              </div>
              <div class="card-arrow">
                <i class="material-icons">arrow_forward_ios</i>
              </div>
            </router-link>
          </div>
        </div>
      </div>

      <!-- Vista de lista -->
      <div v-else class="list-view">
        <div class="dominios-table">
          <div class="table-header">
            <div class="header-cell">Dominio</div>
            <div class="header-cell">Descripción</div>
            <div class="header-cell">Tipo</div>
            <div class="header-cell">Acciones</div>
          </div>
          <router-link
            v-for="dominio in listaFiltrada"
            :key="dominio.key"
            :to="getDominioRoute(dominio.key)"
            class="table-row"
          >
            <div class="table-cell">
              <div class="cell-content">
                <i class="material-icons">{{ getDominioIcon(dominio.key) }}</i>
                <div>
                  <div class="cell-title">{{ dominio.title }}</div>
                  <div class="cell-subtitle">{{ dominio.pluralName }}</div>
                </div>
              </div>
            </div>
            <div class="table-cell">{{ dominio.description }}</div>
            <div class="table-cell">
              <span class="type-badge">{{ getCategoryForDominio(dominio.key) }}</span>
            </div>
            <div class="table-cell">
              <i class="material-icons">arrow_forward_ios</i>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Estado vacío cuando no hay resultados -->
      <div v-if="Object.keys(dominiosFiltrados).length === 0" class="empty-state">
        <i class="material-icons">search_off</i>
        <h3>No se encontraron dominios</h3>
        <p>Intenta con otros términos de búsqueda</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getDominiosByCategory, getAllDominiosConfig } from './configs/dominiosConfig'

// =============== STATE ===============
const filtro = ref('')
const vistaCategoria = ref(true)
const totalRegistros = ref(0) // Se puede cargar desde la API

// =============== COMPUTED ===============
const todasCategorias = computed(() => getDominiosByCategory())

const dominiosFiltrados = computed(() => {
  if (!filtro.value) return todasCategorias.value
  
  const filtroLower = filtro.value.toLowerCase()
  const resultado: Record<string, any[]> = {}
  
  for (const [categoria, dominios] of Object.entries(todasCategorias.value)) {
    const dominiosFiltradosCategoria = dominios.filter(dominio =>
      dominio.title.toLowerCase().includes(filtroLower) ||
      dominio.description.toLowerCase().includes(filtroLower) ||
      dominio.key.toLowerCase().includes(filtroLower)
    )
    
    if (dominiosFiltradosCategoria.length > 0) {
      resultado[categoria] = dominiosFiltradosCategoria
    }
  }
  
  return resultado
})

const listaFiltrada = computed(() => {
  const todosDominios = getAllDominiosConfig()
  if (!filtro.value) return todosDominios
  
  const filtroLower = filtro.value.toLowerCase()
  return todosDominios.filter(dominio =>
    dominio.title.toLowerCase().includes(filtroLower) ||
    dominio.description.toLowerCase().includes(filtroLower) ||
    dominio.key.toLowerCase().includes(filtroLower)
  )
})

// =============== METHODS ===============
const getDominioRoute = (key: string): string => {
  // Mapear las claves a las rutas específicas definidas en el router
  const routeMap: Record<string, string> = {
    'alcance_operacion': '/gestion-informacion/database/dominios/alcance-operacion',
    'categorias': '/gestion-informacion/database/dominios/categorias-insumos',
    'componentes_post': '/gestion-informacion/database/dominios/componentes-postoperacion',
    'entidades': '/gestion-informacion/database/dominios/entidades-operacion',
    'estados_insumo': '/gestion-informacion/database/dominios/estado-insumos',
    'grupos': '/gestion-informacion/database/dominios/grupos-operacion',
    'mecanismo_detalle': '/gestion-informacion/database/dominios/mecanismo-detalle',
    'mecanismo_general': '/gestion-informacion/database/dominios/mecanismo-general',
    'mecanismo_operacion': '/gestion-informacion/database/dominios/mecanismo-operacion',
    'roles_seguimiento': '/gestion-informacion/database/dominios/roles-seguimiento',
    'territoriales_igac': '/gestion-informacion/database/dominios/territoriales-igac',
    'tipos_formato': '/gestion-informacion/database/dominios/tipos-formato',
    'tipos_insumos': '/gestion-informacion/database/dominios/tipos-insumos',
    'zonas': '/gestion-informacion/database/dominios/zonas-operacion'
  }
  
  return routeMap[key] || `/gestion-informacion/database/dominios/${key}`
}

const getCategoryIcon = (categoria: string): string => {
  const iconMap: Record<string, string> = {
    'Operaciones': 'settings',
    'Clasificaciones': 'label',
    'Organizacionales': 'business',
    'Territoriales': 'map',
    'Post-operación': 'upload'
  }
  return iconMap[categoria] || 'folder'
}

const getDominioIcon = (key: string): string => {
  const iconMap: Record<string, string> = {
    'alcance_operacion': 'track_changes',
    'categorias': 'category',
    'componentes_post': 'upload',
    'entidades': 'business',
    'estados_insumo': 'toggle_on',
    'grupos': 'group_work',
    'mecanismo_detalle': 'build',
    'mecanismo_general': 'settings',
    'mecanismo_operacion': 'precision_manufacturing',
    'roles_seguimiento': 'assignment_ind',
    'territoriales_igac': 'map',
    'tipos_formato': 'description',
    'tipos_insumos': 'inventory',
    'zonas': 'place'
  }
  return iconMap[key] || 'storage'
}

const getCategoryForDominio = (key: string): string => {
  for (const [categoria, dominios] of Object.entries(todasCategorias.value)) {
    if (dominios.some(d => d.key === key)) {
      return categoria
    }
  }
  return 'General'
}

// =============== LIFECYCLE ===============
onMounted(() => {
  // Aquí se puede cargar estadísticas desde la API
  totalRegistros.value = 1250 // Ejemplo
})
</script>

<style scoped>
.dominios-dashboard {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
}

.dashboard-header {
  background: white;
  border-bottom: 1px solid #e9ecef;
  padding: 2rem 2rem 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.title-section {
  flex: 1;
}

.dashboard-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 1rem 0;
  font-size: 2rem;
  font-weight: 600;
  color: #343a40;
}

.dashboard-description {
  margin: 0;
  color: #6c757d;
  font-size: 1rem;
  line-height: 1.5;
}

.stats-section {
  display: flex;
  gap: 1rem;
}

.stat-card {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 12px;
  text-align: center;
  min-width: 80px;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  opacity: 0.9;
}

.dashboard-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  overflow-y: auto;
}

.controls-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  gap: 1rem;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.view-toggle {
  display: flex;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 0.25rem;
}

.toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
  color: #6c757d;
}

.toggle-btn.active {
  background: white;
  color: #007bff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.category-section {
  margin-bottom: 3rem;
}

.category-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 1.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #495057;
}

.category-count {
  font-size: 0.875rem;
  color: #6c757d;
  font-weight: 400;
}

.dominios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.dominio-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  transition: all 0.2s;
  text-decoration: none;
  color: inherit;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  border: 1px solid #e9ecef;
}

.dominio-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  border-color: #007bff;
}

.card-icon {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-content {
  flex: 1;
}

.card-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #343a40;
}

.card-description {
  margin: 0 0 1rem 0;
  color: #6c757d;
  font-size: 0.875rem;
  line-height: 1.4;
}

.card-meta {
  display: flex;
  gap: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #868e96;
}

.meta-item i {
  font-size: 1rem;
}

.card-arrow {
  color: #6c757d;
  transition: transform 0.2s;
}

.dominio-card:hover .card-arrow {
  transform: translateX(4px);
  color: #007bff;
}

/* Lista View */
.dominios-table {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 3fr 1fr 80px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.header-cell {
  padding: 1rem 1.5rem;
  font-weight: 600;
  color: #495057;
  font-size: 0.875rem;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 3fr 1fr 80px;
  border-bottom: 1px solid #e9ecef;
  text-decoration: none;
  color: inherit;
  transition: background-color 0.2s;
}

.table-row:hover {
  background-color: #f8f9fa;
}

.table-cell {
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
}

.cell-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.cell-title {
  font-weight: 500;
  color: #343a40;
}

.cell-subtitle {
  font-size: 0.875rem;
  color: #6c757d;
}

.type-badge {
  background: #e9ecef;
  color: #495057;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6c757d;
}

.empty-state i {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
}

.empty-state p {
  margin: 0;
  font-size: 0.95rem;
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .stats-section {
    align-self: stretch;
    justify-content: center;
  }
  
  .controls-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .dominios-grid {
    grid-template-columns: 1fr;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
  }
  
  .header-cell:not(:first-child),
  .table-cell:not(:first-child) {
    display: none;
  }
}
</style>