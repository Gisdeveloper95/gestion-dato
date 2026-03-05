<template>
  <div class="usuarios-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">
            <i class="material-icons">group</i>
            Gestión de Usuarios
          </h1>
          <p class="page-description">
            Administración completa de usuarios del sistema organizados por roles
          </p>
        </div>
        
        <div class="header-actions">
          <router-link 
            to="/gestion-informacion/usuarios-admin/nuevo" 
            class="btn btn-primary"
            v-if="puedeCrearUsuarios"
          >
            <i class="material-icons">person_add</i>
            Crear Usuario
          </router-link>
          
          <button @click="cargarUsuarios" class="btn btn-secondary" :disabled="cargando">
            <i class="material-icons">refresh</i>
            Actualizar
          </button>
        </div>
      </div>
    </div>

    <!-- Barra de filtros -->
    <div class="filtros-section">
      <div class="filtros-container">
        <h3 class="filtros-title">
          <i class="material-icons">filter_list</i>
          Filtros de Búsqueda
        </h3>
        
        <div class="filtros-grid">
          <!-- Búsqueda por nombre -->
          <div class="form-group">
            <label for="filtro-nombre">
              Buscar por Nombre:
              <span class="contador-opciones">({{ usuariosFiltrados.length }} usuarios encontrados)</span>
            </label>
            <div class="search-input-container">
              <i class="material-icons search-icon">search</i>
              <input
                id="filtro-nombre"
                v-model="filtros.busqueda"
                type="text"
                class="form-control"
                :class="{ 'has-selection': filtros.busqueda }"
                placeholder="Buscar por nombre o usuario..."
              />
              <button 
                v-if="filtros.busqueda" 
                @click="limpiarFiltroEspecifico('busqueda')"
                class="btn-limpiar-filtro"
                title="Limpiar búsqueda"
              >
                ✓
              </button>
            </div>
          </div>

          <!-- Filtro por correo -->
          <div class="form-group">
            <label for="filtro-email">
              Buscar por Email:
              <span class="contador-opciones">({{ emailsDisponibles.length }} emails disponibles)</span>
            </label>
            <div class="search-input-container">
              <i class="material-icons search-icon">email</i>
              <input
                id="filtro-email"
                v-model="filtros.email"
                type="text"
                class="form-control"
                :class="{ 'has-selection': filtros.email }"
                placeholder="Buscar por correo electrónico..."
              />
              <button 
                v-if="filtros.email" 
                @click="limpiarFiltroEspecifico('email')"
                class="btn-limpiar-filtro"
                title="Limpiar búsqueda de email"
              >
                ✓
              </button>
            </div>
          </div>

          <!-- Filtro por rol -->
          <div class="form-group">
            <label for="filtro-rol">
              Rol de Usuario:
              <span class="contador-opciones">({{ rolesDisponibles.length }} roles disponibles)</span>
            </label>
            <select 
              id="filtro-rol" 
              v-model="filtros.rol"
              class="form-control"
              :class="{ 'has-selection': filtros.rol }"
            >
              <option value="">Todos los roles</option>
              <option v-for="rol in rolesDisponibles" :key="rol.codigo" :value="rol.codigo">
                {{ rol.nombre }} ({{ rol.cantidad }})
              </option>
            </select>
            <button 
              v-if="filtros.rol" 
              @click="limpiarFiltroEspecifico('rol')"
              class="btn-limpiar-filtro"
              title="Limpiar filtro de rol"
            >
              ✓
            </button>
          </div>

          <!-- Filtro por estado -->
          <div class="form-group">
            <label for="filtro-estado">
              Estado del Usuario:
              <span class="contador-opciones">(2 opciones)</span>
            </label>
            <select 
              id="filtro-estado" 
              v-model="filtros.estado"
              class="form-control"
              :class="{ 'has-selection': filtros.estado }"
            >
              <option value="">Todos los estados</option>
              <option value="activo">Solo Activos ({{ usuariosActivosCount }})</option>
              <option value="inactivo">Solo Inactivos ({{ usuariosInactivosCount }})</option>
            </select>
            <button 
              v-if="filtros.estado" 
              @click="limpiarFiltroEspecifico('estado')"
              class="btn-limpiar-filtro"
              title="Limpiar filtro de estado"
            >
              ✓
            </button>
          </div>
        </div>

        <!-- Indicadores de filtros activos -->
        <div class="filtros-activos" v-if="hayFiltrosActivos">
          <h4>🔍 Filtros activos:</h4>
          <div class="tags-filtros">
            <span v-if="filtros.busqueda" class="tag-filtro busqueda">
              Nombre: "{{ filtros.busqueda }}"
              <button @click="limpiarFiltroEspecifico('busqueda')">×</button>
            </span>
            <span v-if="filtros.email" class="tag-filtro email">
              Email: "{{ filtros.email }}"
              <button @click="limpiarFiltroEspecifico('email')">×</button>
            </span>
            <span v-if="filtros.rol" class="tag-filtro rol">
              Rol: {{ obtenerNombreRol(filtros.rol) }}
              <button @click="limpiarFiltroEspecifico('rol')">×</button>
            </span>
            <span v-if="filtros.estado" class="tag-filtro estado">
              Estado: {{ filtros.estado === 'activo' ? 'Activos' : 'Inactivos' }}
              <button @click="limpiarFiltroEspecifico('estado')">×</button>
            </span>
          </div>
        </div>

        <!-- Botones de filtros -->
        <div class="filtros-buttons">
          <button class="btn btn-secondary" @click="limpiarTodosFiltros">
            <i class="material-icons">clear_all</i>
            Limpiar Filtros
          </button>
          <div class="resultados-info">
            <i class="material-icons">info</i>
            Mostrando {{ usuariosFiltrados.length }} de {{ todoLosUsuarios.length }} usuarios
          </div>
        </div>
      </div>
    </div>

    <!-- Estadísticas filtradas -->
    <div class="stats-grid" v-if="estadisticas">
      <div class="stat-card super-admin">
        <div class="stat-icon">
          <i class="material-icons">admin_panel_settings</i>
        </div>
        <div class="stat-content">
          <h3>{{ usuariosFiltradosPorRol.super_admins.length }}</h3>
          <p>Super Administradores</p>
          <small v-if="hayFiltrosActivos" class="filtro-info">
            de {{ estadisticas.total_super_admins }} totales
          </small>
        </div>
      </div>
      
      <div class="stat-card admin">
        <div class="stat-icon">
          <i class="material-icons">manage_accounts</i>
        </div>
        <div class="stat-content">
          <h3>{{ usuariosFiltradosPorRol.admins.length }}</h3>
          <p>Administradores</p>
          <small v-if="hayFiltrosActivos" class="filtro-info">
            de {{ estadisticas.total_admins }} totales
          </small>
        </div>
      </div>
      
      <div class="stat-card profesional">
        <div class="stat-icon">
          <i class="material-icons">person</i>
        </div>
        <div class="stat-content">
          <h3>{{ usuariosFiltradosPorRol.profesionales.length }}</h3>
          <p>Profesionales</p>
          <small v-if="hayFiltrosActivos" class="filtro-info">
            de {{ estadisticas.total_profesionales }} totales
          </small>
        </div>
      </div>
      
      <div class="stat-card total">
        <div class="stat-icon">
          <i class="material-icons">groups</i>
        </div>
        <div class="stat-content">
          <h3>{{ usuariosFiltrados.length }}</h3>
          <p>Total Filtrado</p>
          <small v-if="hayFiltrosActivos" class="filtro-info">
            de {{ todoLosUsuarios.length }} totales
          </small>
        </div>
      </div>
    </div>

    <!-- Contenido principal -->
    <div class="page-content">
      <!-- Loading -->
      <div v-if="cargando" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Cargando usuarios...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="error-container">
        <i class="material-icons">error</i>
        <h3>Error al cargar usuarios</h3>
        <p>{{ error }}</p>
        <button @click="cargarUsuarios" class="btn btn-primary">
          <i class="material-icons">refresh</i>
          Reintentar
        </button>
      </div>

      <!-- No hay resultados -->
      <div v-else-if="usuariosFiltrados.length === 0 && hayFiltrosActivos" class="empty-filter-state">
        <i class="material-icons">search_off</i>
        <h3>No se encontraron usuarios</h3>
        <p>No hay usuarios que coincidan con los filtros seleccionados</p>
        <button @click="limpiarTodosFiltros" class="btn btn-primary">
          <i class="material-icons">clear_all</i>
          Limpiar Filtros
        </button>
      </div>

      <!-- Usuarios por rol (filtrados) -->
      <div v-else class="usuarios-sections">
        
        <!-- Super Administradores -->
        <div class="usuarios-section" v-if="usuariosFiltradosPorRol.super_admins?.length > 0">
          <div class="section-header super-admin">
            <h2>
              <i class="material-icons">admin_panel_settings</i>
              Super Administradores
              <span class="count">({{ usuariosFiltradosPorRol.super_admins.length }})</span>
            </h2>
          </div>
          
          <div class="usuarios-grid">
            <!-- Super Administradores Cards -->
            <div 
              v-for="usuario in usuariosFiltradosPorRol.super_admins"
              :key="usuario.id"
              class="usuario-card"
            >
              <!-- Header con estado y rol -->
              <div class="card-header">
                <div class="user-avatar super-admin">
                  <i class="material-icons">admin_panel_settings</i>
                </div>

                <div class="user-basic-info">
                  <h3 class="user-name">
                    {{ getNombreCompleto(usuario) }}
                    <span v-if="esUsuarioProtegido(usuario.username)" class="protected-badge" title="Usuario protegido del sistema">
                      <i class="material-icons">verified_user</i>
                    </span>
                  </h3>
                  <p class="user-username">@{{ usuario.username }}</p>
                </div>

                <div class="user-status">
                  <span :class="['status-badge', { active: usuario.is_active }]">
                    <i class="material-icons">{{ usuario.is_active ? 'check_circle' : 'block' }}</i>
                    {{ usuario.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                </div>
              </div>

              <!-- Información principal -->
              <div class="card-body">
                <div class="info-section">
                  <div class="info-item">
                    <i class="material-icons">email</i>
                    <span>{{ usuario.email }}</span>
                  </div>

                  <div class="info-item">
                    <i class="material-icons">badge</i>
                    <span class="rol-badge super-admin">
                      Super Administrador
                    </span>
                  </div>

                  <!-- Indicador de usuario protegido -->
                  <div class="info-item protected-info" v-if="esUsuarioProtegido(usuario.username)">
                    <i class="material-icons">security</i>
                    <span class="protected-text">Usuario protegido del sistema</span>
                  </div>
                  
                  <div class="info-item">
                    <i class="material-icons">schedule</i>
                    <span>Registrado: {{ formatearFecha(usuario.fecha_registro) }}</span>
                  </div>
                  
                  <div class="info-item" v-if="usuario.ultimo_login">
                    <i class="material-icons">login</i>
                    <span>Último acceso: {{ formatearFecha(usuario.ultimo_login) }}</span>
                  </div>
                  
                  <div class="info-item" v-else>
                    <i class="material-icons">login</i>
                    <span class="never-logged">Nunca ha iniciado sesión</span>
                  </div>
                </div>
              </div>

              <!-- Acciones -->
              <div class="card-actions">
                <button
                  @click="editarUsuario(usuario)"
                  class="action-btn edit"
                  :disabled="!puedeEditarUsuarioLocal(usuario)"
                  :title="puedeEditarUsuarioLocal(usuario) ? 'Editar usuario' : 'No tiene permisos para editar'"
                >
                  <i class="material-icons">edit</i>
                  Editar
                </button>

                <button
                  @click="cambiarPassword(usuario)"
                  class="action-btn password"
                  :disabled="!puedeEditarPassword(usuario)"
                  :title="puedeEditarPassword(usuario) ? 'Cambiar contraseña' : (esUsuarioProtegido(usuario.username) ? 'Usuario protegido' : 'No tiene permisos')"
                >
                  <i class="material-icons">lock_reset</i>
                  Contraseña
                </button>

                <button
                  @click="confirmarEliminacion(usuario)"
                  class="action-btn delete"
                  :disabled="!puedeEliminarUsuarioLocal(usuario)"
                  :title="puedeEliminarUsuarioLocal(usuario) ? 'Eliminar usuario' : (esUsuarioProtegido(usuario.username) ? 'Usuario protegido - No se puede eliminar' : 'No tiene permisos')"
                  v-if="usuarioActual?.isSuperUser"
                >
                  <i class="material-icons">delete</i>
                  Eliminar
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Administradores -->
        <div class="usuarios-section" v-if="usuariosFiltradosPorRol.admins?.length > 0">
          <div class="section-header admin">
            <h2>
              <i class="material-icons">manage_accounts</i>
              Administradores
              <span class="count">({{ usuariosFiltradosPorRol.admins.length }})</span>
            </h2>
          </div>
          
          <div class="usuarios-grid">
            <!-- Administradores Cards -->
            <div 
              v-for="usuario in usuariosFiltradosPorRol.admins"
              :key="usuario.id"
              class="usuario-card"
            >
              <!-- Header con estado y rol -->
              <div class="card-header">
                <div class="user-avatar admin">
                  <i class="material-icons">manage_accounts</i>
                </div>
                
                <div class="user-basic-info">
                  <h3 class="user-name">{{ getNombreCompleto(usuario) }}</h3>
                  <p class="user-username">@{{ usuario.username }}</p>
                </div>
                
                <div class="user-status">
                  <span :class="['status-badge', { active: usuario.is_active }]">
                    <i class="material-icons">{{ usuario.is_active ? 'check_circle' : 'block' }}</i>
                    {{ usuario.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                </div>
              </div>

              <!-- Información principal -->
              <div class="card-body">
                <div class="info-section">
                  <div class="info-item">
                    <i class="material-icons">email</i>
                    <span>{{ usuario.email }}</span>
                  </div>
                  
                  <div class="info-item">
                    <i class="material-icons">badge</i>
                    <span class="rol-badge admin">
                      Administrador
                    </span>
                  </div>
                  
                  <div class="info-item">
                    <i class="material-icons">schedule</i>
                    <span>Registrado: {{ formatearFecha(usuario.fecha_registro) }}</span>
                  </div>
                  
                  <div class="info-item" v-if="usuario.ultimo_login">
                    <i class="material-icons">login</i>
                    <span>Último acceso: {{ formatearFecha(usuario.ultimo_login) }}</span>
                  </div>
                  
                  <div class="info-item" v-else>
                    <i class="material-icons">login</i>
                    <span class="never-logged">Nunca ha iniciado sesión</span>
                  </div>
                </div>
              </div>

              <!-- Acciones -->
              <div class="card-actions">
                <button 
                  @click="editarUsuario(usuario)"
                  class="action-btn edit"
                  :disabled="!puedeEditarUsuarioLocal(usuario)"
                  :title="puedeEditarUsuarioLocal(usuario) ? 'Editar usuario' : 'No tiene permisos para editar'"
                >
                  <i class="material-icons">edit</i>
                  Editar
                </button>
                
                <button 
                  @click="cambiarPassword(usuario)"
                  class="action-btn password"
                  :disabled="!puedeEditarPassword(usuario)"
                  :title="puedeEditarPassword(usuario) ? 'Cambiar contraseña' : 'No tiene permisos para cambiar contraseña'"
                >
                  <i class="material-icons">lock_reset</i>
                  Contraseña
                </button>
                
                <button 
                  @click="confirmarEliminacion(usuario)"
                  class="action-btn delete"
                  :disabled="!puedeEliminarUsuarioLocal(usuario)"
                  :title="puedeEliminarUsuarioLocal(usuario) ? 'Eliminar usuario' : 'No tiene permisos para eliminar'"
                  v-if="usuarioActual?.isSuperUser && puedeEliminarUsuarioLocal(usuario)"
                >
                  <i class="material-icons">delete</i>
                  Eliminar
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Profesionales -->
        <div class="usuarios-section" v-if="usuariosFiltradosPorRol.profesionales?.length > 0">
          <div class="section-header profesional">
            <h2>
              <i class="material-icons">person</i>
              Profesionales
              <span class="count">({{ usuariosFiltradosPorRol.profesionales.length }})</span>
            </h2>
          </div>
          
          <div class="usuarios-grid">
            <!-- Profesionales Cards -->
            <div 
              v-for="usuario in usuariosFiltradosPorRol.profesionales"
              :key="usuario.id"
              class="usuario-card"
            >
              <!-- Header con estado y rol -->
              <div class="card-header">
                <div class="user-avatar profesional">
                  <i class="material-icons">person</i>
                </div>
                
                <div class="user-basic-info">
                  <h3 class="user-name">{{ getNombreCompleto(usuario) }}</h3>
                  <p class="user-username">@{{ usuario.username }}</p>
                </div>
                
                <div class="user-status">
                  <span :class="['status-badge', { active: usuario.is_active }]">
                    <i class="material-icons">{{ usuario.is_active ? 'check_circle' : 'block' }}</i>
                    {{ usuario.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                </div>
              </div>

              <!-- Información principal -->
              <div class="card-body">
                <div class="info-section">
                  <div class="info-item">
                    <i class="material-icons">email</i>
                    <span>{{ usuario.email }}</span>
                  </div>
                  
                  <div class="info-item">
                    <i class="material-icons">badge</i>
                    <span class="rol-badge profesional">
                      Profesional
                    </span>
                  </div>
                  
                  <div class="info-item">
                    <i class="material-icons">schedule</i>
                    <span>Registrado: {{ formatearFecha(usuario.fecha_registro) }}</span>
                  </div>
                  
                  <div class="info-item" v-if="usuario.ultimo_login">
                    <i class="material-icons">login</i>
                    <span>Último acceso: {{ formatearFecha(usuario.ultimo_login) }}</span>
                  </div>
                  
                  <div class="info-item" v-else>
                    <i class="material-icons">login</i>
                    <span class="never-logged">Nunca ha iniciado sesión</span>
                  </div>
                </div>
              </div>

              <!-- Acciones -->
              <div class="card-actions">
                <button 
                  @click="editarUsuario(usuario)"
                  class="action-btn edit"
                  :disabled="!puedeEditarUsuarioLocal(usuario)"
                  :title="puedeEditarUsuarioLocal(usuario) ? 'Editar usuario' : 'No tiene permisos para editar'"
                >
                  <i class="material-icons">edit</i>
                  Editar
                </button>
                
                <button 
                  @click="cambiarPassword(usuario)"
                  class="action-btn password"
                  :disabled="!puedeEditarPassword(usuario)"
                  :title="puedeEditarPassword(usuario) ? 'Cambiar contraseña' : 'No tiene permisos para cambiar contraseña'"
                >
                  <i class="material-icons">lock_reset</i>
                  Contraseña
                </button>
                
                <button 
                  @click="confirmarEliminacion(usuario)"
                  class="action-btn delete"
                  :disabled="!puedeEliminarUsuarioLocal(usuario)"
                  :title="puedeEliminarUsuarioLocal(usuario) ? 'Eliminar usuario' : 'No tiene permisos para eliminar'"
                  v-if="usuarioActual?.isSuperUser && puedeEliminarUsuarioLocal(usuario)"
                >
                  <i class="material-icons">delete</i>
                  Eliminar
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Estado vacío -->
        <div v-if="todoLosUsuarios.length === 0" class="empty-state">
          <i class="material-icons">group_off</i>
          <h3>No hay usuarios registrados</h3>
          <p>Comienza creando el primer usuario del sistema</p>
          <router-link to="/gestion-informacion/usuarios-admin/nuevo" class="btn btn-primary">
            <i class="material-icons">person_add</i>
            Crear Usuario
          </router-link>
        </div>
      </div>
    </div>

    <!-- Modal de confirmación de eliminación -->
    <ConfirmModal
      v-if="mostrarModalEliminar"
      :show="mostrarModalEliminar"
      :title="'Eliminar Usuario'"
      :message="`¿Está seguro de que desea eliminar al usuario '${usuarioAEliminar?.username}'? Esta acción eliminará TODOS los datos asociados y no se puede deshacer.`"
      :confirm-text="'Eliminar'"
      :cancel-text="'Cancelar'"
      :loading="eliminando"
      danger
      @confirm="eliminarUsuario"
      @cancel="cancelarEliminacion"
    />

    <!-- Modal de cambio de contraseña -->
    <PasswordModal
      v-if="mostrarModalPassword"
      :show="mostrarModalPassword"
      :usuario="usuarioAEditarPassword"
      @confirm="confirmarCambioPassword"
      @cancel="cancelarCambioPassword"
    />

    <!-- Notificaciones -->
    <div v-if="notificacion.show" :class="['notification', notificacion.type]">
      <i class="material-icons">{{ notificacion.icon }}</i>
      <span>{{ notificacion.message }}</span>
      <button @click="cerrarNotificacion" class="close-btn">
        <i class="material-icons">close</i>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { usuariosService, type Usuario, type UsuariosPorRol, getRolDisplayName, getRolColor, puedeEliminarUsuario, puedeEditarUsuario, esUsuarioProtegido } from '@/api/usuarios'
import { useAuthStore } from '@/store/auth'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import PasswordModal from './components/PasswordModal.vue'

// =============== STATE ===============
const router = useRouter()
const authStore = useAuthStore()

const cargando = ref(false)
const error = ref<string | null>(null)
const usuarios = ref<UsuariosPorRol>({
  super_admins: [],
  admins: [],
  profesionales: [],
  total: 0,
  estadisticas: {
    total_super_admins: 0,
    total_admins: 0,
    total_profesionales: 0
  }
})

const estadisticas = ref<any>(null)

// ========== SISTEMA DE FILTROS ==========
const filtros = ref({
  busqueda: '',
  email: '',
  rol: '',
  estado: ''
})

// Estados de modales
const mostrarModalEliminar = ref(false)
const mostrarModalPassword = ref(false)
const usuarioAEliminar = ref<Usuario | null>(null)
const usuarioAEditarPassword = ref<Usuario | null>(null)
const eliminando = ref(false)

// Notificaciones
const notificacion = ref({
  show: false,
  type: 'success',
  message: '',
  icon: 'check_circle'
})

// =============== COMPUTED PARA FILTROS DINÁMICOS ===============

// Array con todos los usuarios combinados
const todoLosUsuarios = computed(() => {
  return [
    ...usuarios.value.super_admins,
    ...usuarios.value.admins, 
    ...usuarios.value.profesionales
  ]
})

// Usuarios filtrados dinámicamente
const usuariosFiltrados = computed(() => {
  let resultado = [...todoLosUsuarios.value]
  
  // Filtro por búsqueda (nombre, usuario, email)
  if (filtros.value.busqueda.trim()) {
    const termino = filtros.value.busqueda.toLowerCase().trim()
    resultado = resultado.filter(usuario => {
      const nombreCompleto = `${usuario.first_name} ${usuario.last_name}`.toLowerCase()
      const username = usuario.username.toLowerCase()
      const email = usuario.email.toLowerCase()
      
      return nombreCompleto.includes(termino) || 
             username.includes(termino) || 
             email.includes(termino)
    })
  }
  
  // Filtro por email específico
  if (filtros.value.email.trim()) {
    const emailTermino = filtros.value.email.toLowerCase().trim()
    resultado = resultado.filter(usuario => 
      usuario.email.toLowerCase().includes(emailTermino)
    )
  }
  
  // Filtro por rol
  if (filtros.value.rol) {
    resultado = resultado.filter(usuario => usuario.rol_tipo === filtros.value.rol)
  }
  
  // Filtro por estado
  if (filtros.value.estado) {
    const esActivo = filtros.value.estado === 'activo'
    resultado = resultado.filter(usuario => usuario.is_active === esActivo)
  }
  
  return resultado
})

// Usuarios filtrados organizados por rol
const usuariosFiltradosPorRol = computed(() => {
  const filtrados = usuariosFiltrados.value
  
  return {
    super_admins: filtrados.filter(u => u.rol_tipo === 'super_admin'),
    admins: filtrados.filter(u => u.rol_tipo === 'admin'),
    profesionales: filtrados.filter(u => u.rol_tipo === 'profesional')
  }
})

// Opciones disponibles para cada filtro (dinámicas)
const emailsDisponibles = computed(() => {
  // Obtener emails únicos del conjunto filtrado actual (excluyendo el filtro de email)
  let usuariosParaEmails = [...todoLosUsuarios.value]
  
  // Aplicar otros filtros excepto email
  if (filtros.value.busqueda.trim()) {
    const termino = filtros.value.busqueda.toLowerCase().trim()
    usuariosParaEmails = usuariosParaEmails.filter(usuario => {
      const nombreCompleto = `${usuario.first_name} ${usuario.last_name}`.toLowerCase()
      const username = usuario.username.toLowerCase()
      const email = usuario.email.toLowerCase()
      
      return nombreCompleto.includes(termino) || 
             username.includes(termino) || 
             email.includes(termino)
    })
  }
  
  if (filtros.value.rol) {
    usuariosParaEmails = usuariosParaEmails.filter(usuario => usuario.rol_tipo === filtros.value.rol)
  }
  
  if (filtros.value.estado) {
    const esActivo = filtros.value.estado === 'activo'
    usuariosParaEmails = usuariosParaEmails.filter(usuario => usuario.is_active === esActivo)
  }
  
  return Array.from(new Set(usuariosParaEmails.map(u => u.email))).sort()
})

const rolesDisponibles = computed(() => {
  // Obtener roles del conjunto filtrado actual (excluyendo el filtro de rol)
  let usuariosParaRoles = [...todoLosUsuarios.value]
  
  // Aplicar otros filtros excepto rol
  if (filtros.value.busqueda.trim()) {
    const termino = filtros.value.busqueda.toLowerCase().trim()
    usuariosParaRoles = usuariosParaRoles.filter(usuario => {
      const nombreCompleto = `${usuario.first_name} ${usuario.last_name}`.toLowerCase()
      const username = usuario.username.toLowerCase()
      const email = usuario.email.toLowerCase()
      
      return nombreCompleto.includes(termino) || 
             username.includes(termino) || 
             email.includes(termino)
    })
  }
  
  if (filtros.value.email.trim()) {
    const emailTermino = filtros.value.email.toLowerCase().trim()
    usuariosParaRoles = usuariosParaRoles.filter(usuario => 
      usuario.email.toLowerCase().includes(emailTermino)
    )
  }
  
  if (filtros.value.estado) {
    const esActivo = filtros.value.estado === 'activo'
    usuariosParaRoles = usuariosParaRoles.filter(usuario => usuario.is_active === esActivo)
  }
  
  // Contar usuarios por rol
  const rolesCounts = usuariosParaRoles.reduce((acc, usuario) => {
    acc[usuario.rol_tipo] = (acc[usuario.rol_tipo] || 0) + 1
    return acc
  }, {} as Record<string, number>)
  
  const roles = [
    { codigo: 'super_admin', nombre: 'Super Administrador', cantidad: rolesCounts.super_admin || 0 },
    { codigo: 'admin', nombre: 'Administrador', cantidad: rolesCounts.admin || 0 },
    { codigo: 'profesional', nombre: 'Profesional', cantidad: rolesCounts.profesional || 0 }
  ]
  
  // Solo devolver roles que tengan usuarios
  return roles.filter(rol => rol.cantidad > 0)
})

// Contadores para estados
const usuariosActivosCount = computed(() => {
  return usuariosFiltrados.value.filter(u => u.is_active).length
})

const usuariosInactivosCount = computed(() => {
  return usuariosFiltrados.value.filter(u => !u.is_active).length
})

// Verificar si hay filtros activos
const hayFiltrosActivos = computed(() => {
  return !!(
    filtros.value.busqueda.trim() ||
    filtros.value.email.trim() ||
    filtros.value.rol ||
    filtros.value.estado
  )
})

// =============== COMPUTED ORIGINALES ===============
const usuarioActual = computed(() => authStore.user)

const puedeCrearUsuarios = computed(() => {
  return usuarioActual.value?.isStaff || usuarioActual.value?.isSuperUser
})

// =============== METHODS PARA FILTROS ===============
const limpiarFiltroEspecifico = (filtro: string) => {
  console.log(`🧹 Limpiando filtro específico: ${filtro}`)
  filtros.value[filtro] = ''
}

const limpiarTodosFiltros = () => {
  console.log('🧹 Limpiando todos los filtros')
  filtros.value = {
    busqueda: '',
    email: '',
    rol: '',
    estado: ''
  }
}

const obtenerNombreRol = (codigo: string): string => {
  const roles = {
    'super_admin': 'Super Administrador',
    'admin': 'Administrador',
    'profesional': 'Profesional'
  }
  return roles[codigo as keyof typeof roles] || codigo
}

// =============== METHODS ORIGINALES ===============
const cargarUsuarios = async () => {
  try {
    cargando.value = true
    error.value = null

    const [usuariosData, estadisticasData] = await Promise.all([
      usuariosService.listarUsuarios(),
      usuariosService.obtenerEstadisticas()
    ])

    usuarios.value = usuariosData
    estadisticas.value = estadisticasData

  } catch (err: any) {
    error.value = err.message
    console.error('Error cargando usuarios:', err)
  } finally {
    cargando.value = false
  }
}

const editarUsuario = (usuario: Usuario) => {
  router.push(`/gestion-informacion/usuarios-admin/${usuario.id}/editar`)
}

const confirmarEliminacion = (usuario: Usuario) => {
  if (!puedeEliminarUsuarioLocal(usuario)) {
    mostrarNotificacion('error', 'No tiene permisos para eliminar este usuario', 'error')
    return
  }

  usuarioAEliminar.value = usuario
  mostrarModalEliminar.value = true
}

const eliminarUsuario = async () => {
  if (!usuarioAEliminar.value) return

  try {
    eliminando.value = true
    
    const response = await usuariosService.eliminarUsuario(usuarioAEliminar.value.id)
    
    mostrarNotificacion('success', response.message, 'delete')
    cancelarEliminacion()
    
    // Recargar lista
    await cargarUsuarios()

  } catch (err: any) {
    mostrarNotificacion('error', err.message, 'error')
  } finally {
    eliminando.value = false
  }
}

const cancelarEliminacion = () => {
  mostrarModalEliminar.value = false
  usuarioAEliminar.value = null
  eliminando.value = false
}

const cambiarPassword = (usuario: Usuario) => {
  usuarioAEditarPassword.value = usuario
  mostrarModalPassword.value = true
}

const confirmarCambioPassword = async (nuevaPassword: string) => {
  if (!usuarioAEditarPassword.value) return

  try {
    const response = await usuariosService.cambiarPassword(
      usuarioAEditarPassword.value.id, 
      nuevaPassword
    )
    
    mostrarNotificacion('success', response.message, 'lock_reset')
    cancelarCambioPassword()

  } catch (err: any) {
    mostrarNotificacion('error', err.message, 'error')
  }
}

const cancelarCambioPassword = () => {
  mostrarModalPassword.value = false
  usuarioAEditarPassword.value = null
}

const mostrarNotificacion = (tipo: string, mensaje: string, icono: string) => {
  notificacion.value = {
    show: true,
    type: tipo,
    message: mensaje,
    icon: icono
  }
  
  setTimeout(() => {
    cerrarNotificacion()
  }, 5000)
}

const cerrarNotificacion = () => {
  notificacion.value.show = false
}

// =============== MÉTODOS PARA TARJETAS ===============
const getNombreCompleto = (usuario: Usuario): string => {
  const nombre = `${usuario.first_name} ${usuario.last_name}`.trim()
  return nombre || usuario.username
}

const formatearFecha = (fecha: string): string => {
  if (!fecha) return 'No disponible'
  
  try {
    const date = new Date(fecha)
    return date.toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return 'Fecha inválida'
  }
}

const puedeEditarUsuarioLocal = (usuario: Usuario): boolean => {
  if (!usuarioActual.value) return false

  // Super admin puede editar a TODOS (incluyendo otros super admins)
  // Los usuarios protegidos se manejan en el backend y en el formulario de edición
  if (usuarioActual.value.isSuperUser) {
    return true
  }

  // Admin puede editar profesionales y a sí mismo
  if (usuarioActual.value.isStaff) {
    return usuario.rol_tipo === 'profesional' || usuario.id === usuarioActual.value.id
  }

  // Profesionales solo pueden editarse a sí mismos
  return usuario.id === usuarioActual.value.id
}

const puedeEliminarUsuarioLocal = (usuario: Usuario): boolean => {
  if (!usuarioActual.value) return false

  // Solo super admins pueden eliminar usuarios
  if (!usuarioActual.value.isSuperUser) return false

  // No puede eliminarse a sí mismo
  if (usuario.id === usuarioActual.value.id) return false

  // No puede eliminar usuarios protegidos
  if (esUsuarioProtegido(usuario.username)) return false

  // Super admin PUEDE eliminar a otros super admins (excepto los protegidos, ya validado arriba)
  return true
}

const puedeEditarPassword = (usuario: Usuario): boolean => {
  if (!usuarioActual.value) return false

  // No puede cambiar password a usuarios protegidos
  if (esUsuarioProtegido(usuario.username)) return false

  // Super admin puede cambiar password a TODOS (excepto usuarios protegidos, ya validado arriba)
  if (usuarioActual.value.isSuperUser) {
    return true
  }

  // Admin puede cambiar password a profesionales
  if (usuarioActual.value.isStaff) {
    return usuario.rol_tipo === 'profesional'
  }

  return false
}

// =============== LIFECYCLE ===============
onMounted(() => {
  cargarUsuarios()
})
</script>

<style scoped>
.usuarios-page {
  min-height: 100vh;
  background: #f8f9fa;
}

/* ========== ESTILOS PARA FILTROS ========== */
.filtros-section {
  max-width: 1200px;
  margin: 0 auto 2rem;
  padding: 0 2rem;
}

.filtros-container {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.filtros-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 1.5rem 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #1f2937;
}

.filtros-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  position: relative;
}

.form-group label {
  font-weight: 500;
  color: #374151;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
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

.search-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  color: #6b7280;
  z-index: 1;
  font-size: 1.2rem;
}

.form-control {
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.2s;
  background: white;
  width: 100%;
}

.search-input-container .form-control {
  padding-left: 3rem;
  padding-right: 3rem;
}

.form-control:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-control.has-selection {
  border-color: #007bff;
  background-color: #f0f8ff;
  font-weight: 500;
}

.btn-limpiar-filtro {
  position: absolute;
  right: 8px;
  background: #00bfff;
  color: white;
  border: none;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  z-index: 10;
}

.btn-limpiar-filtro:hover {
  background: #007acc;
  transform: scale(1.15);
  box-shadow: 0 0 10px rgba(0, 191, 255, 0.6);
}

.filtros-activos {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 8px;
  border-left: 4px solid #28a745;
}

.filtros-activos h4 {
  margin: 0 0 0.75rem;
  font-size: 1rem;
  color: #343a40;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tags-filtros {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag-filtro {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-filtro.busqueda {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
}

.tag-filtro.email {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
}

.tag-filtro.rol {
  background: linear-gradient(135deg, #9b59b6, #8e44ad);
  color: white;
}

.tag-filtro.estado {
  background: linear-gradient(135deg, #f39c12, #d68910);
  color: white;
}

.tag-filtro button {
  background: rgba(255, 255, 255, 0.3);
  border: none;
  color: inherit;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.tag-filtro button:hover {
  background: rgba(255, 255, 255, 0.5);
  transform: scale(1.1);
}

.filtros-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.resultados-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.9rem;
}

.empty-filter-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.empty-filter-state i {
  font-size: 4rem;
  margin-bottom: 1rem;
  color: #d1d5db;
}

/* ========== ESTILOS ORIGINALES (HEREDADOS) ========== */
/* Header */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  margin-bottom: 2rem;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 700;
}

.page-description {
  margin: 0;
  opacity: 0.9;
  font-size: 1.1rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

/* Estadísticas */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  max-width: 1200px;
  margin: 0 auto 2rem;
  padding: 0 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  border-left: 4px solid;
}

.stat-card.super-admin {
  border-left-color: #dc2626;
}

.stat-card.admin {
  border-left-color: #ea580c;
}

.stat-card.profesional {
  border-left-color: #16a34a;
}

.stat-card.total {
  border-left-color: #3b82f6;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
}

.super-admin .stat-icon {
  background: #fef2f2;
  color: #dc2626;
}

.admin .stat-icon {
  background: #fff7ed;
  color: #ea580c;
}

.profesional .stat-icon {
  background: #f0fdf4;
  color: #16a34a;
}

.total .stat-icon {
  background: #eff6ff;
  color: #3b82f6;
}

.stat-content h3 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
}

.stat-content p {
  margin: 0;
  color: #6b7280;
  font-size: 0.9rem;
}

.filtro-info {
  color: #9ca3af;
  font-size: 0.8rem;
  font-style: italic;
}

/* Contenido principal */
.page-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* Secciones de usuarios */
.usuarios-sections {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.usuarios-section {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.section-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e5e7eb;
}

.section-header.super-admin {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-bottom-color: #fecaca;
}

.section-header.admin {
  background: linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%);
  border-bottom-color: #fdba74;
}

.section-header.profesional {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border-bottom-color: #bbf7d0;
}

.section-header h2 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
}

.count {
  font-size: 1rem;
  font-weight: 400;
  color: #6b7280;
}

.usuarios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  padding: 2rem;
}

/* Estados */
.loading-container,
.error-container,
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-left-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-container i,
.empty-state i {
  font-size: 4rem;
  margin-bottom: 1rem;
  color: #d1d5db;
}

/* Botones */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  text-decoration: none;
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

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #4b5563;
}

/* Notificaciones */
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  background: white;
  border-radius: 8px;
  padding: 1rem 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 1000;
  min-width: 300px;
  border-left: 4px solid;
}

.notification.success {
  border-left-color: #10b981;
  color: #047857;
}

.notification.error {
  border-left-color: #ef4444;
  color: #dc2626;
}

.close-btn {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0;
  margin-left: auto;
}

/* =============== ESTILOS PARA TARJETAS DE USUARIO =============== */
.usuario-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid #e5e7eb;
}

.usuario-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

/* Header de tarjeta */
.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.user-avatar.super-admin {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
}

.user-avatar.admin {
  background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
}

.user-avatar.profesional {
  background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
}

.user-basic-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-username {
  margin: 0;
  font-size: 0.9rem;
  color: #6b7280;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-status {
  flex-shrink: 0;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  background: #fee2e2;
  color: #dc2626;
}

.status-badge.active {
  background: #d1fae5;
  color: #047857;
}

/* Body de tarjeta */
.card-body {
  padding: 1.5rem;
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.9rem;
  color: #4b5563;
}

.info-item i {
  color: #9ca3af;
  font-size: 1.1rem;
  width: 20px;
  flex-shrink: 0;
}

.rol-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  color: white;
  font-size: 0.8rem;
  font-weight: 500;
}

.rol-badge.super-admin {
  background: #dc2626;
}

.rol-badge.admin {
  background: #ea580c;
}

.rol-badge.profesional {
  background: #16a34a;
}

.never-logged {
  color: #9ca3af;
  font-style: italic;
}

/* Usuarios protegidos */
.protected-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-left: 0.5rem;
  color: #059669;
  vertical-align: middle;
}

.protected-badge i {
  font-size: 1rem;
}

.protected-info {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  border: 1px solid #6ee7b7;
}

.protected-info i {
  color: #059669 !important;
}

.protected-text {
  color: #047857;
  font-weight: 500;
  font-size: 0.85rem;
}

/* Actions de tarjeta */
.card-actions {
  padding: 1rem 1.5rem;
  background: #f9fafb;
  border-top: 1px solid #f3f4f6;
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn i {
  font-size: 1rem;
}

.action-btn.edit {
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #dbeafe;
}

.action-btn.edit:hover:not(:disabled) {
  background: #dbeafe;
  border-color: #93c5fd;
}

.action-btn.password {
  background: #fef3c7;
  color: #d97706;
  border: 1px solid #fcd34d;
}

.action-btn.password:hover:not(:disabled) {
  background: #fcd34d;
  border-color: #f59e0b;
}

.action-btn.delete {
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.action-btn.delete:hover:not(:disabled) {
  background: #fecaca;
  border-color: #f87171;
}

/* Responsive */
@media (max-width: 768px) {
  .page-header {
    padding: 1.5rem 1rem;
  }
  
  .header-content {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .header-actions {
    align-self: stretch;
  }
  
  .filtros-section {
    padding: 0 1rem;
  }
  
  .filtros-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .filtros-buttons {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    padding: 0 1rem;
  }
  
  .page-content {
    padding: 0 1rem;
  }
  
  .usuarios-grid {
    grid-template-columns: 1fr;
    padding: 1rem;
  }
  
  .section-header {
    padding: 1rem;
  }
  
  .card-header {
    padding: 1rem;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 0.75rem;
  }
  
  .user-basic-info {
    text-align: center;
  }
  
  .card-body {
    padding: 1rem;
  }
  
  .card-actions {
    padding: 1rem;
    justify-content: center;
  }
  
  .action-btn {
    flex: 1;
    justify-content: center;
    min-width: 0;
  }
}
</style>