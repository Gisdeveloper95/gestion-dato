<template>
  <div class="roles-seguimiento-page">
    <!-- Header mejorado -->
    <div class="page-header">
      <div class="breadcrumb">
        <router-link to="/gestion-informacion/database" class="breadcrumb-link">
          <i class="material-icons">dashboard</i>
          Gestión Base de Datos
        </router-link>
        <i class="material-icons breadcrumb-separator">chevron_right</i>
        <span class="breadcrumb-current">Roles de Seguimiento</span>
      </div>
      
      <div class="page-title-section">
        <h1 class="page-title">
          <i class="material-icons page-icon">supervised_user_circle</i>
          Roles de Seguimiento
        </h1>
        <p class="page-description">
          Gestión de roles profesionales para el seguimiento de operaciones cartográficas
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
      <!-- TableManager con configuración específica -->
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

// Configuración específica para roles de seguimiento
const tableConfig = computed(() => ({
  title: 'Roles de Seguimiento',
  singularName: 'Rol de Seguimiento',
  pluralName: 'Roles de Seguimiento',
  apiEndpoint: '/preoperacion/roles-seguimiento/',
  idField: 'rol_profesional',
  itemsPerPage: 25,
  columns: [
    {
      key: 'rol_profesional',
      label: 'Rol Profesional',
      type: 'text',
      editable: true,
      required: true,
      sortable: true,
      placeholder: 'Ej: Coordinador Técnico',
      maxLength: 100,
      isPrimaryKey: true,
      width: 'auto'
    }
  ],
  searchFields: ['rol_profesional'],
  orderBy: 'rol_profesional',
  emptyMessage: 'No hay roles de seguimiento registrados',
  createButtonText: 'Nuevo Rol de Seguimiento',
  confirmDeleteMessage: '¿Está seguro que desea eliminar este rol de seguimiento?'
}))

// Permisos para la gestión de roles de seguimiento
const permissions = computed(() => ({
  canCreate: true,
  canEdit: true,
  canDelete: true,
  canExport: true,
  canImport: true
}))
</script>

<style scoped>
.roles-seguimiento-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem 0;
  margin-bottom: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.breadcrumb {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.breadcrumb-link {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: color 0.3s ease;
}

.breadcrumb-link:hover {
  color: white;
  text-decoration: none;
}

.breadcrumb-separator {
  margin: 0 0.5rem;
  opacity: 0.7;
  font-size: 1.2rem;
}

.breadcrumb-current {
  opacity: 0.9;
  font-weight: 500;
}

.page-title-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.page-icon {
  font-size: 2.5rem;
  opacity: 0.9;
}

.page-description {
  font-size: 1.1rem;
  opacity: 0.9;
  line-height: 1.5;
  margin: 0;
  max-width: 600px;
}

.header-actions {
  max-width: 1200px;
  margin: 2rem auto 0;
  padding: 0 2rem;
  display: flex;
  justify-content: flex-end;
}

.btn-back {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  color: white;
  text-decoration: none;
}

.page-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem 3rem;
}

.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

/* Responsive Design */
@media (max-width: 768px) {
  .page-header {
    padding: 1.5rem 0;
  }
  
  .breadcrumb,
  .page-title-section,
  .header-actions,
  .page-content {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .page-icon {
    font-size: 2rem;
  }
  
  .page-description {
    font-size: 1rem;
  }
  
  .header-actions {
    margin-top: 1.5rem;
  }
  
  .btn-back {
    padding: 0.625rem 1.25rem;
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.75rem;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .breadcrumb {
    flex-wrap: wrap;
    gap: 0.25rem;
  }
  
  .btn-back {
    width: 100%;
    justify-content: center;
  }
}
</style>