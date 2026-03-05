<template>
  <div class="usuario-form-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="breadcrumb">
          <router-link to="/gestion-informacion/usuarios" class="breadcrumb-link">
            <i class="material-icons">group</i>
            Usuarios
          </router-link>
          <i class="material-icons">chevron_right</i>
          <span class="breadcrumb-current">{{ esEdicion ? 'Editar Usuario' : 'Crear Usuario' }}</span>
        </div>
        
        <div class="title-section">
          <h1 class="page-title">
            <i class="material-icons">{{ esEdicion ? 'edit' : 'person_add' }}</i>
            {{ esEdicion ? 'Editar Usuario' : 'Crear Nuevo Usuario' }}
          </h1>
          <p class="page-description">
            {{ esEdicion ? 'Modifica la información y permisos del usuario' : 'Completa la información para crear un nuevo usuario del sistema' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Contenido principal -->
    <div class="page-content">
      <!-- Loading -->
      <div v-if="cargandoUsuario && esEdicion" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Cargando información del usuario...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="error-container">
        <i class="material-icons">error</i>
        <h3>Error al cargar usuario</h3>
        <p>{{ error }}</p>
        <button @click="cargarUsuario" class="btn btn-primary">
          <i class="material-icons">refresh</i>
          Reintentar
        </button>
      </div>

      <!-- Formulario -->
      <div v-else class="form-container">
        <form @submit.prevent="guardarUsuario" class="usuario-form">
          
          <!-- Información básica -->
          <div class="form-section">
            <div class="section-header">
              <h2>
                <i class="material-icons">person</i>
                Información Básica
              </h2>
            </div>
            
            <div class="form-grid">
              <div class="form-group">
                <label for="username" class="form-label required">
                  <i class="material-icons">account_circle</i>
                  Nombre de Usuario
                </label>
                <input
                  id="username"
                  v-model="formulario.username"
                  type="text"
                  class="form-input"
                  :class="{ error: errores.username }"
                  placeholder="usuario.ejemplo"
                  :disabled="esEdicion"
                  autocomplete="username"
                  required
                />
                <small class="form-help">Solo letras, números, puntos y guiones bajos</small>
                <div v-if="errores.username" class="error-message">{{ errores.username }}</div>
              </div>
              
              <div class="form-group">
                <label for="email" class="form-label required">
                  <i class="material-icons">email</i>
                  Correo Electrónico
                </label>
                <input
                  id="email"
                  v-model="formulario.email"
                  type="email"
                  class="form-input"
                  :class="{ error: errores.email }"
                  placeholder="usuario@igac.gov.co"
                  autocomplete="email"
                  required
                />
                <div v-if="errores.email" class="error-message">{{ errores.email }}</div>
              </div>
              
              <div class="form-group">
                <label for="first_name" class="form-label">
                  <i class="material-icons">badge</i>
                  Nombre(s)
                </label>
                <input
                  id="first_name"
                  v-model="formulario.first_name"
                  type="text"
                  class="form-input"
                  placeholder="Nombres del usuario"
                  autocomplete="given-name"
                />
              </div>
              
              <div class="form-group">
                <label for="last_name" class="form-label">
                  <i class="material-icons">badge</i>
                  Apellido(s)
                </label>
                <input
                  id="last_name"
                  v-model="formulario.last_name"
                  type="text"
                  class="form-input"
                  placeholder="Apellidos del usuario"
                  autocomplete="family-name"
                />
              </div>
            </div>
          </div>

          <!-- Contraseña (solo al crear) -->
          <div v-if="!esEdicion" class="form-section">
            <div class="section-header">
              <h2>
                <i class="material-icons">lock</i>
                Contraseña
              </h2>
            </div>
            
            <div class="form-grid">
              <div class="form-group">
                <label for="password" class="form-label required">
                  <i class="material-icons">lock</i>
                  Contraseña
                </label>
                <div class="password-input-container">
                  <input
                    id="password"
                    v-model="formulario.password"
                    :type="mostrarPassword ? 'text' : 'password'"
                    class="form-input"
                    :class="{ error: errores.password }"
                    placeholder="Mínimo 4 caracteres"
                    autocomplete="new-password"
                    required
                    minlength="4"
                  />
                  <button
                    type="button"
                    @click="toggleMostrarPassword"
                    class="password-toggle"
                  >
                    <i class="material-icons">{{ mostrarPassword ? 'visibility_off' : 'visibility' }}</i>
                  </button>
                </div>
                <small class="form-help">Mínimo 4 caracteres (página privada, contraseña simple permitida)</small>
                <div v-if="errores.password" class="error-message">{{ errores.password }}</div>
              </div>
              
              <div class="form-group">
                <label for="confirm_password" class="form-label required">
                  <i class="material-icons">lock_outline</i>
                  Confirmar Contraseña
                </label>
                <div class="password-input-container">
                  <input
                    id="confirm_password"
                    v-model="formulario.confirm_password"
                    :type="mostrarConfirmarPassword ? 'text' : 'password'"
                    class="form-input"
                    :class="{ error: errores.confirm_password }"
                    placeholder="Confirme la contraseña"
                    autocomplete="new-password"
                    required
                    minlength="4"
                  />
                  <button
                    type="button"
                    @click="toggleMostrarConfirmarPassword"
                    class="password-toggle"
                  >
                    <i class="material-icons">{{ mostrarConfirmarPassword ? 'visibility_off' : 'visibility' }}</i>
                  </button>
                </div>
                <div v-if="errores.confirm_password" class="error-message">{{ errores.confirm_password }}</div>
              </div>
            </div>
          </div>

          <!-- Permisos y Estado (solo al editar) -->
          <div v-if="esEdicion" class="form-section">
            <div class="section-header">
              <h2>
                <i class="material-icons">admin_panel_settings</i>
                Permisos y Estado
              </h2>
            </div>
            
            <div class="form-grid">
              <div class="form-group">
                <label for="rol_tipo" class="form-label">
                  <i class="material-icons">verified_user</i>
                  Tipo de Usuario
                </label>
                <select
                  id="rol_tipo"
                  v-model="formulario.rol_tipo"
                  class="form-select"
                  :disabled="!puedeEditarRol || usuarioProtegido"
                >
                  <option value="profesional">Profesional</option>
                  <option value="admin">Administrador</option>
                  <option v-if="authStore.user?.isSuperUser" value="super_admin">Super Administrador</option>
                </select>
                <small class="form-help" v-if="usuarioProtegido">
                  <i class="material-icons" style="font-size: 14px; vertical-align: middle;">lock</i>
                  Usuario protegido - No se puede modificar su rol
                </small>
                <small class="form-help" v-else>
                  {{ puedeEditarRol ? 'Seleccione el nivel de acceso del usuario' : 'No puede modificar este rol' }}
                </small>
              </div>
              
              <div class="form-group">
                <label class="checkbox-label" :class="{ 'disabled': usuarioProtegido }">
                  <input
                    v-model="formulario.is_active"
                    type="checkbox"
                    class="form-checkbox"
                    :disabled="usuarioProtegido"
                  />
                  <span class="checkbox-custom"></span>
                  <span class="checkbox-text">
                    <i class="material-icons">{{ formulario.is_active ? 'check_circle' : 'block' }}</i>
                    Usuario Activo
                  </span>
                </label>
                <small class="form-help" v-if="usuarioProtegido">
                  <i class="material-icons" style="font-size: 14px; vertical-align: middle;">lock</i>
                  Usuario protegido - No se puede desactivar
                </small>
                <small class="form-help" v-else>Los usuarios inactivos no pueden iniciar sesión</small>
              </div>
            </div>
          </div>

          <!-- Errores generales -->
          <div v-if="errorGeneral" class="error-general">
            <i class="material-icons">error</i>
            {{ errorGeneral }}
          </div>

          <!-- Acciones -->
          <div class="form-actions">
            <router-link to="/gestion-informacion/usuarios" class="btn btn-secondary">
              <i class="material-icons">arrow_back</i>
              Cancelar
            </router-link>
            
            <button 
              type="submit" 
              class="btn btn-primary"
              :disabled="guardando || !formularioValido"
            >
              <span v-if="guardando" class="loading-spinner"></span>
              <i v-else class="material-icons">{{ esEdicion ? 'save' : 'person_add' }}</i>
              {{ guardando ? 'Guardando...' : (esEdicion ? 'Actualizar Usuario' : 'Crear Usuario') }}
            </button>
          </div>
        </form>
      </div>
    </div>

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
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { usuariosService, type CrearUsuarioData, type ActualizarUsuarioData, validarDatosUsuario, esUsuarioProtegido } from '@/api/usuarios'
import { useAuthStore } from '@/store/auth'

// =============== SETUP ===============
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// =============== STATE ===============
const cargandoUsuario = ref(false)
const guardando = ref(false)
const error = ref<string | null>(null)
const errorGeneral = ref('')

const formulario = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  confirm_password: '',
  rol_tipo: 'profesional' as 'profesional' | 'admin' | 'super_admin',
  is_active: true
})

// Variable para almacenar si el usuario que se edita es protegido
const usuarioProtegido = ref(false)

const errores = ref({
  username: '',
  email: '',
  password: '',
  confirm_password: ''
})

const mostrarPassword = ref(false)
const mostrarConfirmarPassword = ref(false)

// Notificaciones
const notificacion = ref({
  show: false,
  type: 'success',
  message: '',
  icon: 'check_circle'
})

// =============== COMPUTED ===============
const esEdicion = computed(() => Boolean(route.params.id))
const usuarioId = computed(() => Number(route.params.id))

const puedeEditarRol = computed(() => {
  const user = authStore.user
  // Solo super admins pueden cambiar roles
  return user?.isSuperUser
})

const formularioValido = computed(() => {
  if (esEdicion.value) {
    return formulario.value.email &&
           !Object.values(errores.value).some(error => error)
  } else {
    return formulario.value.username &&
           formulario.value.email &&
           formulario.value.password &&
           formulario.value.confirm_password &&
           formulario.value.password === formulario.value.confirm_password &&
           !Object.values(errores.value).some(error => error)
  }
})

// =============== WATCHERS ===============
watch(() => formulario.value.username, (newValue) => {
  errores.value.username = ''
  if (newValue && !/^[a-zA-Z0-9._]+$/.test(newValue)) {
    errores.value.username = 'Solo se permiten letras, números, puntos y guiones bajos'
  }
})

watch(() => formulario.value.email, (newValue) => {
  errores.value.email = ''
  if (newValue && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newValue)) {
    errores.value.email = 'Formato de correo inválido'
  }
})

watch(() => formulario.value.password, () => {
  validarPasswords()
})

watch(() => formulario.value.confirm_password, () => {
  validarPasswords()
})

// =============== METHODS ===============
const validarPasswords = () => {
  errores.value.password = ''
  errores.value.confirm_password = ''
  
  if (formulario.value.password && formulario.value.password.length < 4) {
    errores.value.password = 'La contraseña debe tener al menos 4 caracteres'
  }
  
  if (formulario.value.password && formulario.value.confirm_password && 
      formulario.value.password !== formulario.value.confirm_password) {
    errores.value.confirm_password = 'Las contraseñas no coinciden'
  }
}

const cargarUsuario = async () => {
  if (!esEdicion.value) return

  try {
    cargandoUsuario.value = true
    error.value = null

    const usuario = await usuariosService.obtenerUsuario(usuarioId.value)

    // Verificar si es un usuario protegido
    usuarioProtegido.value = esUsuarioProtegido(usuario.username)

    formulario.value = {
      username: usuario.username,
      email: usuario.email,
      first_name: usuario.first_name,
      last_name: usuario.last_name,
      password: '',
      confirm_password: '',
      // Ahora incluimos super_admin como opción válida
      rol_tipo: usuario.rol_tipo as 'profesional' | 'admin' | 'super_admin',
      is_active: usuario.is_active
    }

  } catch (err: any) {
    error.value = err.message
  } finally {
    cargandoUsuario.value = false
  }
}

const guardarUsuario = async () => {
  try {
    guardando.value = true
    errorGeneral.value = ''
    
    console.log('🎯 Iniciando guardarUsuario...');
    console.log('🎯 esEdicion:', esEdicion.value);
    console.log('🎯 formulario.value:', formulario.value);
    
    // Validar formulario
    const erroresValidacion = esEdicion.value ? 
      validarDatosUsuario({
        email: formulario.value.email,
        first_name: formulario.value.first_name,
        last_name: formulario.value.last_name,
        rol_tipo: formulario.value.rol_tipo,
        is_active: formulario.value.is_active
      } as ActualizarUsuarioData) :
      validarDatosUsuario(formulario.value as CrearUsuarioData)
    
    if (erroresValidacion.length > 0) {
      errorGeneral.value = erroresValidacion[0]
      return
    }
    
    let response
    if (esEdicion.value) {
      console.log('🔄 Actualizando usuario...');
      response = await usuariosService.actualizarUsuario(usuarioId.value, {
        first_name: formulario.value.first_name,
        last_name: formulario.value.last_name,
        email: formulario.value.email,
        rol_tipo: formulario.value.rol_tipo,
        is_active: formulario.value.is_active
      })
    } else {
      console.log('➕ Creando usuario...');
      console.log('➕ Datos a enviar:', formulario.value);
      
      response = await usuariosService.crearUsuario(formulario.value as CrearUsuarioData)
      
      console.log('✅ RESPUESTA RECIBIDA en el componente:');
      console.log('📦 response:', response);
      console.log('📦 tipo:', typeof response);
      console.log('📦 claves:', Object.keys(response || {}));
      console.log('📦 response.message:', response?.message);
      console.log('📦 response.usuario:', response?.usuario);
    }
    
    // Verificar que response existe y tiene message
    if (!response) {
      console.error('❌ Response es undefined/null');
      throw new Error('No se recibió respuesta del servidor');
    }
    
    console.log('🎉 Verificando message...');
    const message = response.message || response.data?.message || 'Usuario procesado exitosamente';
    console.log('🎉 Message final:', message);
    
    mostrarNotificacion('success', message, 'check_circle')
    
    // Redirigir después de un momento
    setTimeout(() => {
      router.push('/gestion-informacion/usuarios-admin')
    }, 1500)
    
  } catch (err: any) {
    console.error('❌ ERROR CAPTURADO en guardarUsuario:');
    console.error('❌ err:', err);
    console.error('❌ err.message:', err.message);
    console.error('❌ typeof err:', typeof err);
    
    const errorMessage = err?.message || err?.error || 'Error desconocido';
    console.error('❌ Error message final:', errorMessage);
    
    errorGeneral.value = errorMessage;
    mostrarNotificacion('error', errorMessage, 'error');
  } finally {
    guardando.value = false
  }
}

const toggleMostrarPassword = () => {
  mostrarPassword.value = !mostrarPassword.value
}

const toggleMostrarConfirmarPassword = () => {
  mostrarConfirmarPassword.value = !mostrarConfirmarPassword.value
}

// En UsuarioForm.vue, reemplaza la función mostrarNotificacion con esta versión con debug:

const mostrarNotificacion = (tipo: string, mensaje: string, icono: string) => {
  try {
    console.log('🔔 mostrarNotificacion llamada con:');
    console.log('  - tipo:', tipo, typeof tipo);
    console.log('  - mensaje:', mensaje, typeof mensaje);
    console.log('  - icono:', icono, typeof icono);
    
    // Validar parámetros
    if (!tipo) {
      console.error('❌ tipo es undefined/null');
      tipo = 'info';
    }
    
    if (!mensaje) {
      console.error('❌ mensaje es undefined/null');
      mensaje = 'Operación completada';
    }
    
    if (!icono) {
      console.error('❌ icono es undefined/null');
      icono = 'info';
    }
    
    console.log('🔔 Configurando notificación...');
    notificacion.value = {
      show: true,
      type: tipo,
      message: mensaje,
      icon: icono
    }
    
    console.log('🔔 Notificación configurada:', notificacion.value);
    
    setTimeout(() => {
      console.log('🔔 Cerrando notificación automáticamente...');
      cerrarNotificacion()
    }, 5000)
    
    console.log('✅ mostrarNotificacion completada exitosamente');
    
  } catch (error) {
    console.error('❌ ERROR en mostrarNotificacion:', error);
  }
}

const cerrarNotificacion = () => {
  try {
    console.log('🔔 Cerrando notificación...');
    notificacion.value.show = false
    console.log('✅ Notificación cerrada');
  } catch (error) {
    console.error('❌ ERROR cerrando notificación:', error);
  }
}



// =============== LIFECYCLE ===============
onMounted(() => {
  if (esEdicion.value) {
    cargarUsuario()
  }
})
</script>

<style scoped>
.usuario-form-page {
  min-height: 100vh;
  background: #f8f9fa;
}

/* Header */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  margin-bottom: 2rem;
}

.header-content {
  max-width: 1000px;
  margin: 0 auto;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
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

.breadcrumb-current {
  color: white;
  font-weight: 500;
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

/* Contenido principal */
.page-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 2rem;
}

.form-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.usuario-form {
  padding: 2rem;
}

/* Secciones del formulario */
.form-section {
  margin-bottom: 3rem;
}

.form-section:last-of-type {
  margin-bottom: 2rem;
}

.section-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f3f4f6;
}

.section-header h2 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: #1f2937;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

/* Elementos del formulario */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  color: #374151;
  font-size: 0.9rem;
}

.form-label.required::after {
  content: '*';
  color: #ef4444;
  margin-left: 0.25rem;
}

.form-input,
.form-select {
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.2s;
  background: white;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input:disabled {
  background: #f9fafb;
  color: #6b7280;
  cursor: not-allowed;
}

.form-input.error,
.form-select.error {
  border-color: #ef4444;
}

.form-input.error:focus,
.form-select.error:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.password-input-container {
  position: relative;
}

.password-input-container .form-input {
  padding-right: 3rem;
}

.password-toggle {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s;
}

.password-toggle:hover {
  color: #374151;
  background: #f3f4f6;
}

/* Checkbox personalizado */
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s;
  background: white;
}

.checkbox-label:hover {
  border-color: #d1d5db;
}

.form-checkbox {
  position: absolute;
  opacity: 0;
  cursor: pointer;
}

.checkbox-custom {
  width: 20px;
  height: 20px;
  border: 2px solid #d1d5db;
  border-radius: 4px;
  position: relative;
  transition: all 0.2s;
}

.form-checkbox:checked + .checkbox-custom {
  background: #3b82f6;
  border-color: #3b82f6;
}

.form-checkbox:checked + .checkbox-custom::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.checkbox-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  color: #374151;
}

/* Ayuda y errores */
.form-help {
  color: #6b7280;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.error-message {
  color: #ef4444;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.error-general {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

/* Estados */
.loading-container,
.error-container {
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

.error-container i {
  font-size: 4rem;
  margin-bottom: 1rem;
  color: #ef4444;
}

/* Acciones */
.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
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

.btn .loading-spinner {
  width: 16px;
  height: 16px;
  border-width: 2px;
  margin: 0;
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

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .page-header {
    padding: 1.5rem 1rem;
  }
  
  .page-content {
    padding: 0 1rem;
  }
  
  .usuario-form {
    padding: 1.5rem;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column-reverse;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>