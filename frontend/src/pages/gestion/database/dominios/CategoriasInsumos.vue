<template>
  <div class="categorias-page">
    <!-- Header mejorado -->
    <div class="page-header">
      <div class="breadcrumb">
        <router-link to="/gestion-informacion/database" class="breadcrumb-link">
          <i class="material-icons">dashboard</i>
          Gestión Base de Datos
        </router-link>
        <i class="material-icons breadcrumb-separator">chevron_right</i>
        <span class="breadcrumb-current">Categorías de Insumos</span>
      </div>
      
      <div class="page-title-section">
        <h1 class="page-title">
          <i class="material-icons page-icon">category</i>
          Categorías de Insumos
        </h1>
        <p class="page-description">
          Gestión completa de categorías para clasificar y organizar insumos cartográficos del sistema
        </p>
      </div>
      
      <div class="header-actions">
        <router-link to="/gestion-informacion/database" class="btn-back">
          <i class="material-icons">arrow_back</i>
          Volver al Dashboard
        </router-link>
      </div>
    </div>

    <!-- Contenido principal -->
    <div class="page-content">
      <!-- TableManager con configuración mejorada -->
      <div class="table-container">
        <TableManager
          :table-config="tableConfig"
          :permissions="permissions"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import TableManager from '@/pages/gestion/database/components/TableManager.vue'

// Configuración específica para categorías de insumos con conexión API real
const tableConfig = computed(() => ({
  title: 'Categorías de Insumos',
  singularName: 'Categoría',
  pluralName: 'Categorías',
  apiEndpoint: '/preoperacion/categorias/',
  idField: 'cod_categoria',
  itemsPerPage: 25,
  columns: [
    {
      key: 'cod_categoria',
      label: 'Código',
      type: 'number' as const,
      sortable: true,
      editable: false,
      minWidth: '120px'
    },
    {
      key: 'nom_categoria',
      label: 'Nombre de la Categoría',
      type: 'text' as const,
      sortable: true,
      editable: true,
      required: true,
      placeholder: 'Ej: Cartografía Básica, Imágenes Satelitales, Componente Ambiental...',
      minWidth: '400px'
    }
  ],
  searchFields: ['nom_categoria', 'cod_categoria'],
  filters: [
    {
      key: 'nom_categoria',
      label: 'Filtrar por nombre',
      type: 'text' as const,
      placeholder: 'Escribir nombre de categoría...'
    }
  ]
}))

const permissions = computed(() => ({
  canCreate: true,
  canEdit: true,
  canDelete: true,
  canExport: true
}))
</script>

<style scoped>
.categorias-page {
  min-height: 100vh;
  background: #f8f9fa;
}

/* Header mejorado - REDUCIDO EN 1/3 */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem 2rem;
  position: relative;
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.page-header > * {
  position: relative;
  z-index: 1;
}

/* Breadcrumb */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.breadcrumb-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: color 0.2s;
}

.breadcrumb-link:hover {
  color: white;
}

.breadcrumb-separator {
  color: rgba(255, 255, 255, 0.6);
  font-size: 18px;
}

.breadcrumb-current {
  color: white;
  font-weight: 500;
}

/* Título de página */
.page-title-section {
  margin-bottom: 1.5rem;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 0 0 0.75rem 0;
  font-size: 2.5rem;
  font-weight: 700;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.page-icon {
  font-size: 3rem;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  padding: 0.5rem;
}

.page-description {
  margin: 0;
  font-size: 1.1rem;
  opacity: 0.9;
  font-weight: 300;
  line-height: 1.5;
  max-width: 600px;
}

/* Actions del header */
.header-actions {
  position: absolute;
  top: 2rem;
  right: 2rem;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.btn-back .material-icons {
  font-size: 20px;
}

/* Contenido principal */
.page-content {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  border: 1px solid #e9ecef;
}

/* Efectos y animaciones */
@keyframes slideInFromTop {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.categorias-page {
  animation: slideInFromTop 0.5s ease-out;
}

/* Responsive */
@media (max-width: 768px) {
  .page-header {
    padding: 2rem 1rem;
  }
  
  .header-actions {
    position: static;
    margin-top: 2rem;
  }
  
  .page-title {
    font-size: 2rem;
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
  }
  
  .page-icon {
    font-size: 2.5rem;
  }
  
  .page-description {
    text-align: center;
    margin: 0 auto;
  }
  
  .breadcrumb {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .page-content {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.5rem;
  }
  
  .page-description {
    font-size: 1rem;
  }
  
  .btn-back {
    width: 100%;
    justify-content: center;
  }
}

/* Estados de hover mejorados */
.table-container:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  transition: box-shadow 0.3s ease;
}

/* Mejoras visuales adicionales */
.page-header {
  background-attachment: fixed;
}
</style>