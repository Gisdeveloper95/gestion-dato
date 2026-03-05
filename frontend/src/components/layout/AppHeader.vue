<template>
  <header class="app-header">
    <div class="container">
      <div class="header-content">
        <!-- Logo y título juntos en la izquierda -->
        <div class="logo-title-container">
          <img src="/assets/logo.ico" alt="Logo" class="logo" />
          <h1 class="site-title">Sistema de Gestión del Dato</h1>
        </div>
        
        <!-- Barra de búsqueda en el centro -->
        <div class="search-container">
          <div class="search-box">
            <input 
              type="text" 
              v-model="searchQuery" 
              @input="handleSearch" 
              @keyup.enter="submitSearch"
              placeholder="Buscar municipio por nombre o código..."
              class="search-input"
            />
            <button class="search-button" @click="submitSearch">
              <i class="material-icons">search</i>
            </button>
          </div>
          
          <!-- Resultados de búsqueda (mostrar solo si hay resultados) -->
          <div v-if="showResults && searchResults.length > 0" class="search-results">
            <ul>
              <li v-for="result in searchResults" :key="result.cod_municipio">
                <a href="#" @click.prevent="searchMunicipio(result)" class="search-result-item">
                  <div class="result-main">
                    <span class="municipio-nombre">{{ result.nom_municipio }}</span>
                    <span class="municipio-codigo">({{ result.cod_municipio }})</span>
                  </div>
                  <div class="result-department">
                    {{ obtenerNombreDepartamento(result) }}
                  </div>
                </a>
              </li>
            </ul>
            
            <!-- Opción para ver todos los resultados -->
            <div v-if="searchResults.length > 0" class="search-all-results">
              <a href="#" @click.prevent="searchAllResults" class="ver-todos-link">
                <i class="material-icons">search</i>
                Ver todos los resultados para "{{ searchQuery }}"
              </a>
            </div>
          </div>
          
          <!-- Mensaje cuando no hay resultados -->
          <div v-if="showResults && searchQuery.trim() && searchResults.length === 0" class="search-no-results">
            <div class="no-results-message">
              <i class="material-icons">search_off</i>
              <span>No se encontraron municipios</span>
            </div>
            <div class="search-suggestion">
              <a href="#" @click.prevent="searchAllResults" class="buscar-anyway-link">
                Buscar de todas formas "{{ searchQuery }}"
              </a>
            </div>
          </div>
        </div>
        
        <!-- Contenido del header -->
        <div class="auth-container">
          <!-- Espacio para futuros elementos de autenticación -->
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { buscarMunicipios, departamentosApi } from '@/api/municipios';

const router = useRouter();
const searchQuery = ref('');
const searchResults = ref([]);
const showResults = ref(false);
const searchTimeout = ref(null);

// ✨ NUEVO: Lista de departamentos para obtener los nombres
const departamentos = ref<any[]>([]);

// ✨ NUEVO: Función para obtener nombre del departamento (copiada de MunicipiosList.vue)
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

// ✨ NUEVO: Cargar departamentos
const cargarDepartamentos = async () => {
  try {
    console.log('📍 Cargando departamentos para búsqueda...');
    const deptosData = await departamentosApi.getAll();
    departamentos.value = deptosData;
    console.log('✅ Departamentos cargados:', deptosData.length);
  } catch (error) {
    console.error('❌ Error al cargar departamentos:', error);
    // No es crítico, simplemente no se mostrarán los nombres de departamentos
  }
};

// Función para manejar la búsqueda con debounce
const handleSearch = () => {
  // Limpiar timeout previo
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value);
  }
  
  // Si la búsqueda está vacía, limpiar resultados
  if (!searchQuery.value.trim()) {
    searchResults.value = [];
    showResults.value = false;
    return;
  }
  
  // Establecer nuevo timeout para ejecutar búsqueda después de 300ms
  searchTimeout.value = setTimeout(async () => {
    try {
      if (searchQuery.value.length >= 2) {
        console.log('🔍 Buscando municipios:', searchQuery.value.trim());
        const results = await buscarMunicipios(searchQuery.value);
        searchResults.value = results.slice(0, 8); // Limitar a 8 resultados para no saturar
        showResults.value = true;
        console.log('✅ Resultados encontrados:', results.length);
      }
    } catch (error) {
      console.error('Error al buscar municipios:', error);
      searchResults.value = [];
      showResults.value = true; // Mostrar mensaje de "no encontrados"
    }
  }, 300);
};

// Función para buscar un municipio específico (desde la lista de resultados)
const searchMunicipio = (municipio: any) => {
  console.log('🎯 Buscando municipio específico:', municipio.nom_municipio);
  
  // Redirigir a la lista de municipios con el nombre como filtro de búsqueda
  router.push({
    path: '/disposicion-informacion/municipios',
    query: { 
      busqueda: municipio.nom_municipio,
      autoSearch: 'true' // Flag para indicar que debe aplicar la búsqueda automáticamente
    }
  });
  
  clearSearch();
};

// Función para buscar con el término actual (Enter o botón de búsqueda)
const submitSearch = () => {
  if (!searchQuery.value.trim()) {
    return;
  }
  
  console.log('🔍 Ejecutando búsqueda general:', searchQuery.value.trim());
  
  // Redirigir a la lista de municipios con el término de búsqueda
  router.push({
    path: '/disposicion-informacion/municipios',
    query: { 
      busqueda: searchQuery.value.trim(),
      autoSearch: 'true'
    }
  });
  
  clearSearch();
};

// Función para ver todos los resultados (cuando hay muchos o cuando no hay resultados pero se quiere buscar anyway)
const searchAllResults = () => {
  console.log('📋 Ver todos los resultados para:', searchQuery.value.trim());
  
  router.push({
    path: '/disposicion-informacion/municipios',
    query: { 
      busqueda: searchQuery.value.trim(),
      autoSearch: 'true'
    }
  });
  
  clearSearch();
};

// Limpiar búsqueda
const clearSearch = () => {
  searchQuery.value = '';
  searchResults.value = [];
  showResults.value = false;
};

// Cerrar resultados al hacer clic fuera
const handleClickOutside = (event) => {
  const searchContainer = document.querySelector('.search-container');
  if (searchContainer && !searchContainer.contains(event.target)) {
    showResults.value = false;
  }
};

// Añadir/remover listener para clicks fuera de la búsqueda
onMounted(async () => {
  document.addEventListener('click', handleClickOutside);
  
  // ✨ NUEVO: Cargar departamentos al montar el componente
  await cargarDepartamentos();
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value);
  }
});
</script>

<style scoped>
.app-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  padding: 0.5rem 0;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.logo-title-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 250px;
}

.logo {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.site-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
  margin: 0;
  white-space: nowrap;
}

.search-container {
  flex: 1;
  max-width: 500px;
  position: relative;
}

.search-box {
  display: flex;
  align-items: center;
  border: 2px solid #ddd;
  border-radius: 25px;
  overflow: hidden;
  transition: border-color 0.2s;
}

.search-box:focus-within {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  outline: none;
  font-size: 0.95rem;
  background: transparent;
}

.search-input::placeholder {
  color: #6c757d;
}

.search-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.search-button:hover {
  background-color: #0069d9;
}

.search-results,
.search-no-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-height: 400px;
  overflow-y: auto;
  z-index: 1010;
}

.search-results ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.search-results li {
  padding: 0;
  border-bottom: 1px solid #f1f1f1;
}

.search-results li:last-child {
  border-bottom: none;
}

.search-result-item {
  display: block;
  padding: 0.875rem 1rem;
  color: #333;
  text-decoration: none;
  transition: background-color 0.2s;
  cursor: pointer;
}

.search-result-item:hover {
  background-color: #f8f9fa;
}

.result-main {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.municipio-nombre {
  font-weight: 600;
  color: #2c3e50;
}

.municipio-codigo {
  font-size: 0.85rem;
  color: #007bff;
  font-family: 'Courier New', monospace;
  background-color: #e3f2fd;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

.result-department {
  font-size: 0.8rem;
  color: #6c757d;
  font-style: italic;
}

/* Sección para ver todos los resultados */
.search-all-results {
  border-top: 1px solid #e9ecef;
  background-color: #f8f9fa;
}

.ver-todos-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  color: #007bff;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s;
}

.ver-todos-link:hover {
  background-color: #e9ecef;
  text-decoration: none;
}

/* Mensaje cuando no hay resultados */
.search-no-results {
  padding: 1.5rem;
  text-align: center;
}

.no-results-message {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: #6c757d;
  margin-bottom: 0.75rem;
}

.no-results-message i {
  font-size: 1.5rem;
}

.search-suggestion {
  margin-top: 0.75rem;
}

.buscar-anyway-link {
  color: #007bff;
  text-decoration: none;
  font-size: 0.9rem;
}

.buscar-anyway-link:hover {
  text-decoration: underline;
}

.auth-container {
  display: flex;
  align-items: center;
  margin-left: auto;
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    flex-wrap: wrap;
  }
  
  .logo-title-container {
    min-width: auto;
    margin-right: auto;
  }
  
  .site-title {
    font-size: 1rem;
  }
  
  .search-container {
    order: 3;
    max-width: 100%;
    width: 100%;
    margin-top: 0.5rem;
  }
  
  .search-input {
    font-size: 0.9rem;
    padding: 0.6rem 0.8rem;
  }
  
  .search-button {
    padding: 0.6rem 0.8rem;
  }
}

@media (max-width: 480px) {
  .municipio-codigo {
    display: none;
  }
  
  .result-main {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>