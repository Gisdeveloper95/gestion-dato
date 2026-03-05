<template>
  <div class="productos-list-page">
    <!-- Cabecera con título y acciones principales -->
    <div class="page-header">
      <div class="header-content">
        <h1>Gestión de Productos</h1>
        <div class="header-actions">
          <button @click="exportarDatos" class="btn-outline">
            <i class="material-icons">file_download</i>
            Exportar
          </button>
        </div>
      </div>
    </div>

    <!-- Panel de búsqueda y filtros -->
    <div class="filters-panel">
      <div class="search-filters-container">
        <!-- Búsqueda global -->
        <div class="global-search">
          <i class="material-icons">search</i>
          <input 
            type="text"
            v-model="searchTerm"
            placeholder="Buscar municipio..."
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
              <option 
                v-for="dpto in departamentos" 
                :key="dpto.cod_depto" 
                :value="dpto.cod_depto"
              >
                {{ dpto.nom_depto }}
              </option>
            </select>
          </div>

          <div class="filter-item">
            <label>Municipio:</label>
            <select v-model="filters.municipio" @change="handleMunicipioChange">
              <option value="">Todos los municipios</option>
              <option 
                v-for="municipio in municipiosFiltrados" 
                :key="municipio.cod_municipio" 
                :value="municipio.cod_municipio"
              >
                {{ municipio.nom_municipio }}
              </option>
            </select>
          </div>

          <div class="filter-item">
            <label>Territorial:</label>
            <select v-model="filters.territorial" @change="handleFilter">
              <option value="">Todas las territoriales</option>
              <option 
                v-for="territorial in territoriales" 
                :key="territorial.nom_territorial" 
                :value="territorial.nom_territorial"
              >
                {{ territorial.nom_territorial }}
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

    <!-- Lista de municipios con productos -->
    <div v-else class="municipios-container">
      <div v-if="municipiosConProductos.length === 0" class="empty-state">
        <i class="material-icons">inventory_2</i>
        <p>No se encontraron productos con los criterios seleccionados.</p>
        <button @click="clearAllFilters" class="btn-secondary">Limpiar filtros</button>
      </div>

      <div v-else class="table-container">
        <div class="table-header">
          <h3>Municipios con Productos</h3>
          <span class="results-count">{{ filteredMunicipios.length }} municipios encontrados</span>
        </div>
        
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th @click="sortBy('cod_municipio')" class="sortable">
                  Código
                  <i class="material-icons sort-icon" v-if="sortField === 'cod_municipio'">
                    {{ sortAsc ? 'arrow_upward' : 'arrow_downward' }}
                  </i>
                </th>
                <th @click="sortBy('nom_municipio')" class="sortable">
                  Municipio
                  <i class="material-icons sort-icon" v-if="sortField === 'nom_municipio'">
                    {{ sortAsc ? 'arrow_upward' : 'arrow_downward' }}
                  </i>
                </th>
                <th @click="sortBy('cod_depto')" class="sortable">
                  Departamento
                  <i class="material-icons sort-icon" v-if="sortField === 'cod_depto'">
                    {{ sortAsc ? 'arrow_upward' : 'arrow_downward' }}
                  </i>
                </th>
                <th @click="sortBy('nom_territorial')" class="sortable">
                  Territorial
                  <i class="material-icons sort-icon" v-if="sortField === 'nom_territorial'">
                    {{ sortAsc ? 'arrow_upward' : 'arrow_downward' }}
                  </i>
                </th>
                <th @click="sortBy('total_productos')" class="sortable text-center">
                  Total Productos
                  <i class="material-icons sort-icon" v-if="sortField === 'total_productos'">
                    {{ sortAsc ? 'arrow_upward' : 'arrow_downward' }}
                  </i>
                </th>
                <th @click="sortBy('aprobados')" class="sortable text-center">
                  Aprobados
                  <i class="material-icons sort-icon" v-if="sortField === 'aprobados'">
                    {{ sortAsc ? 'arrow_upward' : 'arrow_downward' }}
                  </i>
                </th>
                <th @click="sortBy('pendientes')" class="sortable text-center">
                  Pendientes
                  <i class="material-icons sort-icon" v-if="sortField === 'pendientes'">
                    {{ sortAsc ? 'arrow_upward' : 'arrow_downward' }}
                  </i>
                </th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="municipio in paginatedMunicipios" :key="municipio.cod_municipio">
                <td class="text-center">{{ municipio.cod_municipio }}</td>
                <td>{{ municipio.nom_municipio }}</td>
                <td>{{ getNombreDepartamento(municipio.cod_depto) }}</td>
                <td>{{ municipio.nom_territorial || 'N/A' }}</td>
                <td class="text-center">
                  <span class="badge badge-info">{{ municipio.total_productos || 0 }}</span>
                </td>
                <td class="text-center">
                  <span class="badge badge-success">{{ municipio.aprobados || 0 }}</span>
                </td>
                <td class="text-center">
                  <span class="badge badge-warning">{{ municipio.pendientes || 0 }}</span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button 
                      @click="verDetalle(municipio)" 
                      class="btn-action btn-primary"
                      title="Ver detalles"
                    >
                      <i class="material-icons">visibility</i>
                    </button>
                    <button 
                      @click="exportarMunicipio(municipio)" 
                      class="btn-action btn-secondary"
                      title="Exportar datos"
                    >
                      <i class="material-icons">download</i>
                    </button>
                        <button 
                      @click="descargarProductos(municipio)" 
                      class="btn-action btn-success"
                      title="Descargar productos"
                      :disabled="descargandoProductos[municipio.cod_municipio]"
                    >
                      <i class="material-icons">
                        {{ descargandoProductos[municipio.cod_municipio] ? 'hourglass_empty' : 'inventory' }}
                      </i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Paginación -->
        <div class="pagination" v-if="totalPages > 1">
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
            <i class="material-icons">navigate_next</i>
          </button>
        </div>
      </div>
    </div>

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
import { defineComponent, ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { format, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';
import api, { API_URL } from '@/api/config';

export default defineComponent({
  name: 'ProductosList',
  
  setup() {
    const router = useRouter();
    
    // Estado de carga y error
    const loading = ref(false);
    const error = ref<string | null>(null);
    
    // Datos maestros
    const departamentos = ref<any[]>([]);
    const territoriales = ref<any[]>([]);
    const municipiosList = ref<any[]>([]);
    const municipiosConProductos = ref<any[]>([]);
    const descargandoProductos = ref<{[key: string]: boolean}>({});

    // Filtros
    const searchTerm = ref('');
    const filters = ref({
      departamento: '',
      municipio: '',
      territorial: ''
    });
    
    // Paginación
    const currentPage = ref(1);
    const pageSize = ref(9);
    // Añade este computed property dentro del bloque "setup()" de tu componente
    const municipiosFiltrados = computed(() => {
      if (!filters.value.departamento) {
        return municipiosList.value; // Si no hay departamento seleccionado, muestra todos
      }
      
      // Filtra los municipios que pertenecen al departamento seleccionado
      return municipiosList.value.filter(municipio => 
        municipio.cod_depto?.toString() === filters.value.departamento.toString()
      );
    });
    // Notificación
    const notification = ref({
      show: false,
      message: '',
      type: 'success',
      icon: 'check_circle',
      timeout: null as number | null
    });
    
    // Función para cargar todos los datos paginados
    const cargarTodosLosDatos = async (url: string, params = {}) => {
      let todosLosResultados = [];
      let urlActual = url;
      
      try {
        // Añadir parámetros a la URL
        if (Object.keys(params).length > 0) {
          const queryParams = new URLSearchParams(params as any).toString();
          urlActual = `${url}?${queryParams}`;
        }
        
        // Obtener token
        const token = localStorage.getItem('token');
        const config = token ? {
          headers: {
            'Authorization': `Token ${token}`
          }
        } : {};
        
        // Primera llamada
        const response = await fetch(urlActual, config);
        const data = await response.json();
        
        // Si es un array directo
        if (Array.isArray(data)) {
          return data;
        }
        
        // Si tiene resultados paginados
        if (data.results) {
          todosLosResultados = [...data.results];
          
          // Si hay más páginas
          let nextUrl = data.next;
          while (nextUrl) {
            const nextResponse = await fetch(nextUrl, config);
            const nextData = await nextResponse.json();
            
            if (nextData.results) {
              todosLosResultados = [...todosLosResultados, ...nextData.results];
            }
            
            nextUrl = nextData.next;
          }
        }
        
        return todosLosResultados;
      } catch (error) {
        console.error(`Error cargando datos de ${url}:`, error);
        throw error;
      }
    };
    
    // Cargar datos iniciales
    onMounted(async () => {
      await loadInitialData();
    });
    
    const loadInitialData = async () => {
      try {
        loading.value = true;
        error.value = null;
        
        // Cargar departamentos
        try {
          const deptosData = await cargarTodosLosDatos(`${API_URL}/preoperacion/departamentos/`);
          departamentos.value = deptosData || [];
        } catch (err) {
          console.error('Error cargando departamentos:', err);
          departamentos.value = [];
        }
        
        // Cargar territoriales
        try {
          const territorialesData = await cargarTodosLosDatos(`${API_URL}/preoperacion/territoriales/`);
          territoriales.value = territorialesData || [];
        } catch (err) {
          console.error('Error cargando territoriales:', err);
          territoriales.value = [];
        }
        
        // Cargar municipios para el combo
        try {
          const municipiosData = await cargarTodosLosDatos(`${API_URL}/preoperacion/municipios/`);
          municipiosList.value = municipiosData || [];
        } catch (err) {
          console.error('Error cargando municipios:', err);
          municipiosList.value = [];
        }
        
        // Cargar municipios con productos
        await loadMunicipiosConProductos();
      } catch (err: any) {
        console.error('Error cargando datos:', err);
        error.value = 'Error cargando datos. Por favor, intente nuevamente.';
      } finally {
        loading.value = false;
      }
    };
    
    const loadMunicipiosConProductos = async () => {
      try {
        const params: any = {};
        
        if (filters.value.departamento) {
          params.departamento = filters.value.departamento;
        }
        
        if (filters.value.municipio) {
          params.municipio = filters.value.municipio;
        }
        
        if (filters.value.territorial) {
          params.territorial = filters.value.territorial;
        }
        
        const data = await cargarTodosLosDatos(`${API_URL}/postoperacion/municipios-con-productos/`, params);
        municipiosConProductos.value = data || [];
      } catch (err) {
        console.error('Error cargando municipios con productos:', err);
        showNotification('Error al cargar municipios con productos', 'error');
        municipiosConProductos.value = [];
      }
    };
    
    // Filtros computados
    const filteredMunicipios = computed(() => {
      let result = [...municipiosConProductos.value];
      
      // Filtrar por búsqueda
      if (searchTerm.value.trim()) {
        const search = searchTerm.value.toLowerCase();
        result = result.filter(m => 
          m.nom_municipio.toLowerCase().includes(search) ||
          m.cod_municipio.toString().includes(search)
        );
      }
      
      return result;
    });
    
    // Ordenamiento
    const sortField = ref('nom_municipio');
    const sortAsc = ref(true);
    
    const sortBy = (field: string) => {
      if (sortField.value === field) {
        sortAsc.value = !sortAsc.value;
      } else {
        sortField.value = field;
        sortAsc.value = true;
      }
      currentPage.value = 1;
    };
    
    const sortedMunicipios = computed(() => {
      const sorted = [...filteredMunicipios.value];
      
      sorted.sort((a, b) => {
        let aVal = a[sortField.value];
        let bVal = b[sortField.value];
        
        // Handle null/undefined values
        if (aVal === null || aVal === undefined) aVal = '';
        if (bVal === null || bVal === undefined) bVal = '';
        
        // Convert to string for comparison
        aVal = String(aVal).toLowerCase();
        bVal = String(bVal).toLowerCase();
        
        // Numeric comparison for numeric fields
        if (['cod_municipio', 'total_productos', 'aprobados', 'pendientes'].includes(sortField.value)) {
          aVal = Number(aVal) || 0;
          bVal = Number(bVal) || 0;
        }
        
        let result = 0;
        if (aVal < bVal) result = -1;
        else if (aVal > bVal) result = 1;
        
        return sortAsc.value ? result : -result;
      });
      
      return sorted;
    });
    
    // Paginación
    const totalPages = computed(() => {
      return Math.ceil(sortedMunicipios.value.length / pageSize.value);
    });
    
    const paginatedMunicipios = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value;
      const end = start + pageSize.value;
      return sortedMunicipios.value.slice(start, end);
    });
    
    // Exportar municipio individual
    const exportarMunicipio = (municipio: any) => {
      try {
        const headers = ['Código', 'Municipio', 'Departamento', 'Territorial', 'Total Productos', 'Aprobados', 'Pendientes'];
        
        const data = [[
          municipio.cod_municipio,
          municipio.nom_municipio,
          getNombreDepartamento(municipio.cod_depto),
          municipio.nom_territorial || 'No asignada',
          municipio.total_productos || 0,
          municipio.aprobados || 0,
          municipio.pendientes || 0
        ]];
        
        let csvContent = "data:text/csv;charset=utf-8,\uFEFF";
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
        link.setAttribute('download', `productos_${municipio.nom_municipio}_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`);
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showNotification(`Datos exportados para ${municipio.nom_municipio}`, 'success');
      } catch (error) {
        console.error('Error al exportar municipio:', error);
        showNotification('Error al exportar datos del municipio', 'error');
      }
    };
    
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
    
    // Métodos de filtrado
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
      loadMunicipiosConProductos();
    };
    
    const handleMunicipioChange = () => {
      currentPage.value = 1;
      loadMunicipiosConProductos();
    };
    
    const handleFilter = () => {
      currentPage.value = 1;
      loadMunicipiosConProductos();
    };
    
    const clearAllFilters = () => {
      searchTerm.value = '';
      filters.value = {
        departamento: '',
        municipio: '',
        territorial: ''
      };
      currentPage.value = 1;
      loadMunicipiosConProductos();
    };
    
    // Paginación
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
    
    // Navegación
    const verDetalle = (municipio: any) => {
      router.push(`/gestion-informacion/productos/${municipio.cod_municipio}`);
    };
    
    // Exportar datos
    const exportarDatos = () => {
      try {
        const headers = ['Código', 'Municipio', 'Departamento', 'Territorial', 'Total Productos', 'Aprobados', 'Pendientes'];
        
        const data = filteredMunicipios.value.map(m => [
          m.cod_municipio,
          m.nom_municipio,
          getNombreDepartamento(m.cod_depto),
          m.nom_territorial || 'No asignada',
          m.total_productos || 0,
          m.aprobados || 0,
          m.pendientes || 0
        ]);
        
        let csvContent = "data:text/csv;charset=utf-8,\uFEFF";
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
        link.setAttribute('download', `productos_municipios_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`);
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showNotification('Datos exportados correctamente', 'success');
      } catch (error) {
        console.error('Error al exportar datos:', error);
        showNotification('Error al exportar datos', 'error');
      }
    };
    
    // Refrescar datos
    const refreshData = () => {
      loadMunicipiosConProductos();
    };
    
    // Utilidades
    const getNombreDepartamento = (codDepto: number | string): string => {
      if (!codDepto) return 'N/A';
      const depto = departamentos.value.find(d => d.cod_depto?.toString() === codDepto?.toString());
      return depto ? depto.nom_depto : 'N/A';
    };
    
    // Notificaciones
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

    // Nueva función para descargar productos específicos del municipio
  // ✅ FUNCIÓN CORREGIDA - usar la API de generar reportes
  const descargarProductos = async (municipio: any) => {
    try {
      descargandoProductos.value[municipio.cod_municipio] = true;
      
      showNotification(`Generando reporte de productos para ${municipio.nom_municipio}...`, 'info');
      
      const token = localStorage.getItem('token');
      
      // ✅ USAR LA MISMA API QUE EN REPORTES - pero para un solo municipio
      const response = await fetch(`${API_URL}/postoperacion/generar-reportes/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          municipios: [municipio.cod_municipio], // ← Solo este municipio
          generar_individuales: true
        })
      });
      
      if (!response.ok) {
        throw new Error(`Error HTTP: ${response.status}`);
      }
      
      // ✅ DESCARGAR EL ARCHIVO ZIP directamente (como en ReportesPostoperacion.vue)
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `productos_${municipio.nom_municipio.replace(/\s+/g, '_')}_${format(new Date(), 'yyyyMMdd_HHmmss')}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      showNotification(
        `Reporte de productos de ${municipio.nom_municipio} descargado exitosamente`, 
        'success'
      );
      
    } catch (error) {
      console.error('Error generando reporte de productos:', error);
      showNotification(
        `Error al generar reporte de productos de ${municipio.nom_municipio}`, 
        'error'
      );
    } finally {
      descargandoProductos.value[municipio.cod_municipio] = false;
    }
  };
    
    return {
      loading,
      error,
      departamentos,
      territoriales,
      municipiosList,
      municipiosConProductos,
      searchTerm,
      filters,
      currentPage,
      pageSize,
      totalPages,
      paginatedMunicipios,
      displayedPages,
      notification,
      filteredMunicipios,
      sortField,
      sortAsc,
      sortBy,
      handleSearchInput,
      clearSearch,
      handleDepartamentoChange,
      handleMunicipioChange,
      handleFilter,
      clearAllFilters,
      prevPage,
      nextPage,
      goToPage,
      verDetalle,
      exportarDatos,
      exportarMunicipio,
      refreshData,
      getNombreDepartamento,
      showNotification,
      closeNotification,
      municipiosFiltrados,
      descargandoProductos,
      descargarProductos,
    };
  }
});
</script>

<style scoped>
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

.productos-list-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

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

.refresh-btn {
  background-color: #6c757d;
  color: white;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

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

.municipios-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.table-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #dee2e6;
  background-color: #f8f9fa;
}

.table-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #343a40;
}

.results-count {
  color: #6c757d;
  font-size: 0.9rem;
}

.table-responsive {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background-color: #f8f9fa;
}

.data-table th {
  padding: 0.75rem 1rem;
  font-weight: 600;
  color: #495057;
  border-bottom: 2px solid #dee2e6;
  white-space: nowrap;
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
  position: relative;
}

.data-table th.sortable:hover {
  background-color: #e9ecef;
  color: #212529;
}

.sort-icon {
  display: inline-block;
  font-size: 1rem;
  vertical-align: middle;
  margin-left: 0.25rem;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #dee2e6;
}

.data-table tbody tr:hover {
  background-color: #f5f5f5;
}

.data-table .text-center {
  text-align: center;
}

.badge {
  display: inline-block;
  padding: 0.25em 0.6em;
  font-size: 0.875rem;
  font-weight: 600;
  line-height: 1;
  text-align: center;
  white-space: nowrap;
  vertical-align: baseline;
  border-radius: 0.25rem;
}

.badge-info {
  color: #fff;
  background-color: #17a2b8;
}

.badge-success {
  color: #fff;
  background-color: #28a745;
}

.badge-warning {
  color: #212529;
  background-color: #ffc107;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.btn-action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-action i {
  font-size: 1.25rem;
}

.btn-action.btn-primary {
  background-color: #0d6efd;
  color: white;
}

.btn-action.btn-primary:hover {
  background-color: #0b5ed7;
}

.btn-action.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-action.btn-secondary:hover {
  background-color: #5a6268;
}

.btn-primary,
.btn-secondary,
.btn-outline {
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
  width: 100%;
  justify-content: center;
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

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  gap: 0.5rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
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

@media (max-width: 992px) {
 .municipios-grid {
   grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
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
}

@media (max-width: 768px) {
 .filters-row {
   flex-direction: column;
   align-items: stretch;
 }
 
 .filter-actions {
   margin-left: 0;
   margin-top: 1rem;
 }
 
 .municipios-grid {
   grid-template-columns: 1fr;
 }
 
 .productos-stats {
   grid-template-columns: 1fr;
 }
}

@media (max-width: 576px) {
 .btn-primary,
 .btn-secondary,
 .btn-outline {
   padding: 0.5rem 0.75rem;
   font-size: 0.9rem;
 }
 
 .notification {
   min-width: auto;
   max-width: 90%;
   left: 5%;
   right: 5%;
 }
}
</style>