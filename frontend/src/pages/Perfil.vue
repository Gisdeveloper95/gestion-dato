<template>
  <div class="perfil-page">
    <div class="container">
      <div class="page-header">
        <h1>Mi Perfil</h1>
        <p>Gestiona tu información personal y seguridad de cuenta</p>
      </div>
      
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando datos del usuario...</p>
      </div>
      
      <div v-else-if="error" class="error-state">
        <i class="material-icons">error</i>
        <p>{{ error }}</p>
        <button @click="loadUserData" class="btn-primary">Reintentar</button>
      </div>
      
      <div v-else class="profile-content">
        <!-- Pestañas para navegación interna -->
        <div class="profile-tabs">
          <button 
            @click="activeTab = 'info'"
            :class="{ active: activeTab === 'info' }"
          >
            <i class="material-icons">person</i>
            Información Personal
          </button>
          
          <button 
            @click="activeTab = 'security'"
            :class="{ active: activeTab === 'security' }"
          >
            <i class="material-icons">lock</i>
            Seguridad
          </button>
        </div>
        
        <!-- Contenido de las pestañas -->
        <div class="tab-content">
          <!-- Información personal -->
          <div v-if="activeTab === 'info'" class="panel info-panel">
            <h2>Información Personal</h2>
            
            <!-- Sección de datos actuales -->
            <div class="user-info-section">
              <h3>Datos Actuales</h3>
              <div class="info-item">
                <span class="info-label">Usuario:</span>
                <span class="info-value">{{ userData.username || 'No disponible' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Nombre:</span>
                <span class="info-value">{{ userData.firstName || userData.first_name || userData.nombre || 'No especificado' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Apellido:</span>
                <span class="info-value">{{ userData.lastName || userData.last_name || 'No especificado' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Correo electrónico:</span>
                <span class="info-value">{{ userData.email || userData.correo || 'No especificado' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Tipo de cuenta:</span>
                <span class="info-value">{{ 
                  userData.isAdmin || userData.is_superuser 
                  ? 'Administrador' 
                  : (userData.isStaff || userData.is_staff ? 'Personal' : 'Usuario') 
                }}</span>
              </div>
            </div>
            
            <form @submit.prevent="updateProfile" class="profile-form">
              <div class="profile-avatar">
                <div class="avatar-preview">
                  <span>{{ userInitials }}</span>
                </div>
                <div class="avatar-info">
                  <h3>{{ userData.username }}</h3>
                  <p>Actualizar información</p>
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label for="firstName">Nombre</label>
                  <input 
                    type="text" 
                    id="firstName" 
                    v-model="formData.firstName" 
                    placeholder="Nombre"
                  />
                </div>
                
                <div class="form-group">
                  <label for="lastName">Apellido</label>
                  <input 
                    type="text" 
                    id="lastName" 
                    v-model="formData.lastName" 
                    placeholder="Apellido"
                  />
                </div>
              </div>
              
              <div class="form-group">
                <label for="email">Correo Electrónico</label>
                <input 
                  type="email" 
                  id="email" 
                  v-model="formData.email" 
                  placeholder="correo@ejemplo.com"
                />
              </div>
              
              <div v-if="updateMessage" class="message-box" :class="updateSuccess ? 'info' : 'error'">
                <i class="material-icons">{{ updateSuccess ? 'info' : 'error' }}</i>
                <span>{{ updateMessage }}</span>
              </div>
              
              <div class="form-actions">
                <button 
                  type="submit" 
                  class="btn-primary"
                  :disabled="updating || !formDataChanged"
                >
                  <span v-if="!updating">Guardar Cambios</span>
                  <div v-else class="button-spinner"></div>
                </button>
                
                <button 
                  type="button" 
                  class="btn-secondary"
                  @click="resetForm"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
          
          <!-- Seguridad -->
          <div v-if="activeTab === 'security'" class="panel security-panel">
            <h2>Cambiar Contraseña</h2>
            
            <form @submit.prevent="changePassword" class="profile-form">
              <div class="form-group">
                <label for="currentPassword">Contraseña Actual</label>
                <input 
                  type="password" 
                  id="currentPassword" 
                  v-model="passwordData.currentPassword" 
                  placeholder="Contraseña actual"
                  required
                />
              </div>
              
              <div class="form-group">
                <label for="newPassword">Nueva Contraseña</label>
                <input 
                  type="password" 
                  id="newPassword" 
                  v-model="passwordData.newPassword" 
                  placeholder="Nueva contraseña"
                  required
                />
                <div class="password-strength" v-if="passwordData.newPassword">
                  <div :class="passwordStrengthClass"></div>
                  <span>{{ passwordStrengthText }}</span>
                </div>
              </div>
              
              <div class="form-group">
                <label for="confirmPassword">Confirmar Contraseña</label>
                <input 
                  type="password" 
                  id="confirmPassword" 
                  v-model="passwordData.confirmPassword" 
                  placeholder="Confirmar nueva contraseña"
                  required
                />
                <span v-if="passwordMismatch" class="validation-error">
                  Las contraseñas no coinciden
                </span>
              </div>
              
              <div class="password-guidelines">
                <h4>Requisitos de seguridad:</h4>
                <ul>
                  <li :class="{ 'requirement-met': passwordData.newPassword.length >= 8 }">
                    <i class="material-icons">{{ passwordData.newPassword.length >= 8 ? 'check_circle' : 'cancel' }}</i>
                    Mínimo 8 caracteres
                  </li>
                  <li :class="{ 'requirement-met': /[A-Z]/.test(passwordData.newPassword) }">
                    <i class="material-icons">{{ /[A-Z]/.test(passwordData.newPassword) ? 'check_circle' : 'cancel' }}</i>
                    Al menos una letra mayúscula
                  </li>
                  <li :class="{ 'requirement-met': /[a-z]/.test(passwordData.newPassword) }">
                    <i class="material-icons">{{ /[a-z]/.test(passwordData.newPassword) ? 'check_circle' : 'cancel' }}</i>
                    Al menos una letra minúscula
                  </li>
                  <li :class="{ 'requirement-met': /[0-9]/.test(passwordData.newPassword) }">
                    <i class="material-icons">{{ /[0-9]/.test(passwordData.newPassword) ? 'check_circle' : 'cancel' }}</i>
                    Al menos un número
                  </li>
                  <li :class="{ 'requirement-met': /[^A-Za-z0-9]/.test(passwordData.newPassword) }">
                    <i class="material-icons">{{ /[^A-Za-z0-9]/.test(passwordData.newPassword) ? 'check_circle' : 'cancel' }}</i>
                    Al menos un caracter especial
                  </li>
                </ul>
              </div>
              
              <div v-if="passwordMessage" class="message-box" :class="passwordSuccess ? 'info' : 'error'">
                <i class="material-icons">{{ passwordSuccess ? 'info' : 'error' }}</i>
                <span>{{ passwordMessage }}</span>
              </div>
              
              <div class="form-actions">
                <button 
                  type="submit" 
                  class="btn-primary"
                  :disabled="passwordChanging || passwordMismatch || !passwordValid"
                >
                  <span v-if="!passwordChanging">Cambiar Contraseña</span>
                  <div v-else class="button-spinner"></div>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import axios from 'axios';
import api from '@/api/config';

export default defineComponent({
  name: 'PerfilPage',
  
  setup() {
    // Estado
    const activeTab = ref('info');
    const userData = ref({});
    const loading = ref(true);
    const error = ref(null);
    const formData = ref({
      firstName: '',
      lastName: '',
      email: ''
    });
    const updating = ref(false);
    const updateMessage = ref('');
    const updateSuccess = ref(false);
    const passwordData = ref({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
    const passwordChanging = ref(false);
    const passwordMessage = ref('');
    const passwordSuccess = ref(false);
    
    // Métodos
    const getAuthHeaders = () => {
      const token = localStorage.getItem('token');
      return token ? {
        headers: { 'Authorization': `Token ${token}` }
      } : {};
    };
    
    const loadUserData = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        // Obtener datos del usuario actual desde el nuevo endpoint
        const response = await api.get('/preoperacion/usuario-actual/', getAuthHeaders());
        
        if (response) {
          userData.value = response;
          formData.value = {
            firstName: response.firstName || response.first_name || '',
            lastName: response.lastName || response.last_name || '',
            email: response.email || response.correo || ''
          };
          
          // Actualizar localStorage por si acaso
          localStorage.setItem('userProfile', JSON.stringify(response));
        } else {
          throw new Error('No se recibieron datos del usuario');
        }
      } catch (err) {
        console.error('Error al cargar datos del usuario:', err);
        error.value = 'No se pudieron cargar los datos del usuario. Por favor, intente de nuevo.';
        
        // Intentar usar datos almacenados localmente si hay error
        const savedProfile = localStorage.getItem('userProfile');
        if (savedProfile) {
          try {
            const parsedProfile = JSON.parse(savedProfile);
            userData.value = parsedProfile;
            formData.value = {
              firstName: parsedProfile.firstName || parsedProfile.first_name || '',
              lastName: parsedProfile.lastName || parsedProfile.last_name || '',
              email: parsedProfile.email || parsedProfile.correo || ''
            };
          } catch (e) {
            console.warn('Error al parsear perfil guardado:', e);
          }
        }
      } finally {
        loading.value = false;
      }
    };
    
    const resetForm = () => {
      formData.value = {
        firstName: userData.value.firstName || userData.value.first_name || '',
        lastName: userData.value.lastName || userData.value.last_name || '',
        email: userData.value.email || userData.value.correo || ''
      };
      updateMessage.value = '';
    };
    
    const updateProfile = async () => {
      updating.value = true;
      updateMessage.value = '';
      updateSuccess.value = false;
      
      try {
        // Enviar actualización al servidor usando el nuevo endpoint
        const response = await api.post('/preoperacion/actualizar-perfil/', {
          firstName: formData.value.firstName,
          lastName: formData.value.lastName,
          email: formData.value.email
        }, getAuthHeaders());
        
        if (response) {
          // Actualizar datos locales
          userData.value = response;
          
          // Actualizar localStorage
          localStorage.setItem('userProfile', JSON.stringify(response));
          
          updateSuccess.value = true;
          updateMessage.value = 'Perfil actualizado con éxito.';
        } else {
          throw new Error('No se recibió respuesta del servidor');
        }
      } catch (err) {
        console.error('Error al actualizar perfil:', err);
        updateSuccess.value = false;
        updateMessage.value = err.response?.data?.error || 'Error al actualizar el perfil. Intente nuevamente.';
      } finally {
        updating.value = false;
      }
    };
    
    const changePassword = async () => {
      if (passwordMismatch.value) {
        passwordMessage.value = 'Las contraseñas no coinciden';
        passwordSuccess.value = false;
        return;
      }
      
      if (!passwordValid.value) {
        passwordMessage.value = 'La contraseña no cumple con los requisitos mínimos';
        passwordSuccess.value = false;
        return;
      }
      
      passwordChanging.value = true;
      passwordMessage.value = '';
      passwordSuccess.value = false;
      
      try {
        // Usar el nuevo endpoint para cambiar contraseña
        await api.post('/preoperacion/cambiar-password/', {
          old_password: passwordData.value.currentPassword,
          new_password: passwordData.value.newPassword
        }, getAuthHeaders());
        
        passwordSuccess.value = true;
        passwordMessage.value = 'Contraseña actualizada con éxito';
        
        // Limpiar formulario
        passwordData.value = {
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        };
      } catch (err) {
        console.error('Error al cambiar contraseña:', err);
        passwordSuccess.value = false;
        passwordMessage.value = err.response?.data?.error || 'Error al cambiar la contraseña. Por favor, verifique los datos ingresados.';
      } finally {
        passwordChanging.value = false;
      }
    };
    
    // Propiedades computadas
    const userInitials = computed(() => {
      // Intentar obtener iniciales del nombre o apellido
      if (userData.value.firstName && userData.value.lastName) {
        return `${userData.value.firstName.charAt(0)}${userData.value.lastName.charAt(0)}`.toUpperCase();
      } else if (userData.value.first_name && userData.value.last_name) {
        return `${userData.value.first_name.charAt(0)}${userData.value.last_name.charAt(0)}`.toUpperCase();
      } else if (userData.value.nombre) {
        // Intentar con nombre completo
        const nameParts = userData.value.nombre.split(' ');
        if (nameParts.length >= 2) {
          return `${nameParts[0].charAt(0)}${nameParts[1].charAt(0)}`.toUpperCase();
        }
        return nameParts[0].charAt(0).toUpperCase();
      } else if (userData.value.username) {
        // Usar la primera letra del nombre de usuario
        return userData.value.username.charAt(0).toUpperCase();
      }
      return 'U';
    });
    
    const formDataChanged = computed(() => {
      return formData.value.firstName !== (userData.value.firstName || userData.value.first_name || '') ||
             formData.value.lastName !== (userData.value.lastName || userData.value.last_name || '') ||
             formData.value.email !== (userData.value.email || userData.value.correo || '');
    });
    
    const passwordMismatch = computed(() => {
      return passwordData.value.newPassword !== passwordData.value.confirmPassword && 
             passwordData.value.confirmPassword !== '';
    });
    
    const passwordStrength = computed(() => {
      const pw = passwordData.value.newPassword;
      if (!pw) return 0;
      
      let score = 0;
      
      // Longitud
      if (pw.length >= 8) score += 1;
      if (pw.length >= 12) score += 1;
      
      // Complejidad
      if (/[A-Z]/.test(pw)) score += 1;
      if (/[a-z]/.test(pw)) score += 1;
      if (/[0-9]/.test(pw)) score += 1;
      if (/[^A-Za-z0-9]/.test(pw)) score += 1;
      
      return Math.min(score, 5);
    });
    
    const passwordStrengthClass = computed(() => {
      const strength = passwordStrength.value;
      if (strength === 0) return 'strength-none';
      if (strength <= 2) return 'strength-weak';
      if (strength <= 3) return 'strength-medium';
      return 'strength-strong';
    });
    
    const passwordStrengthText = computed(() => {
      const strength = passwordStrength.value;
      if (strength === 0) return 'Ingrese una contraseña';
      if (strength <= 2) return 'Débil';
      if (strength <= 3) return 'Media';
      return 'Fuerte';
    });
    
    const passwordValid = computed(() => {
      return passwordStrength.value >= 3 &&
             !passwordMismatch.value &&
             passwordData.value.newPassword !== '';
    });
    
    // Ciclo de vida
    onMounted(() => {
      loadUserData();
    });
    
    return {
      activeTab,
      userData,
      loading,
      error,
      formData,
      updating,
      updateMessage,
      updateSuccess,
      passwordData,
      passwordChanging,
      passwordMessage,
      passwordSuccess,
      userInitials,
      formDataChanged,
      passwordMismatch,
      passwordStrengthClass,
      passwordStrengthText,
      passwordValid,
      loadUserData,
      resetForm,
      updateProfile,
      changePassword
    };
  }
});
</script>

<style scoped>
.perfil-page {
  padding: 2rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  color: #343a40;
}

.page-header p {
  color: #6c757d;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state i {
  font-size: 3rem;
  color: #dc3545;
  margin-bottom: 1rem;
}

.profile-content {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Tabs */
.profile-tabs {
  display: flex;
  border-bottom: 1px solid #dee2e6;
}

.profile-tabs button {
  padding: 1rem 1.5rem;
  background: none;
  border: none;
  color: #495057;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s;
  position: relative;
}

.profile-tabs button:after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background-color: transparent;
  transition: background-color 0.2s;
}

.profile-tabs button.active {
  color: #007bff;
}

.profile-tabs button.active:after {
  background-color: #007bff;
}

.profile-tabs button:hover {
  color: #007bff;
}

.profile-tabs button i {
  font-size: 1.25rem;
}

/* Tab content */
.tab-content {
  padding: 2rem;
}

.panel h2 {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: #343a40;
}

/* Profile avatar section */
.profile-avatar {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.avatar-preview {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: #007bff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.75rem;
  font-weight: bold;
}

.avatar-info h3 {
  margin: 0 0 0.25rem;
  font-size: 1.25rem;
}

.avatar-info p {
  margin: 0;
  color: #6c757d;
}

/* User data section */
.user-info-section {
  margin: 1.5rem 0;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #007bff;
}

.user-info-section h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.1rem;
  color: #343a40;
}

.info-item {
  display: flex;
  margin-bottom: 0.75rem;
}

.info-label {
  min-width: 150px;
  font-weight: 500;
  color: #6c757d;
}

.info-value {
  color: #212529;
}

/* Form styles */
.profile-form {
  width: 100%;
}

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #495057;
}

.form-group input[type="text"],
.form-group input[type="email"],
.form-group input[type="password"] {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus {
  border-color: #80bdff;
  outline: none;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.validation-error {
  display: block;
  margin-top: 0.5rem;
  color: #dc3545;
  font-size: 0.85rem;
}

/* Password strength indicator */
.password-strength {
  margin-top: 0.5rem;
}

.password-strength div {
  height: 5px;
  border-radius: 2.5px;
  margin-bottom: 0.25rem;
}

.password-strength span {
  font-size: 0.85rem;
}

.strength-none {
  background-color: #dee2e6;
  width: 0;
}

.strength-weak {
  background-color: #dc3545;
  width: 30%;
}

.strength-medium {
  background-color: #ffc107;
  width: 60%;
}

.strength-strong {
  background-color: #28a745;
  width: 100%;
}

/* Password guidelines */
.password-guidelines {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.password-guidelines h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1rem;
}

.password-guidelines ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.password-guidelines li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  color: #6c757d;
}

.password-guidelines li i {
  font-size: 1.2rem;
  color: #dc3545;
}

.password-guidelines .requirement-met {
  color: #212529;
}

.password-guidelines .requirement-met i {
  color: #28a745;
}

/* Form actions */
.form-actions {
  margin-top: 2rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: background-color 0.2s;
  border: none;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0069d9;
}

.btn-primary:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

/* Message box */
.message-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.message-box.info {
  background-color: #cff4fc;
  color: #055160;
}

.message-box.error {
  background-color: #f8d7da;
  color: #721c24;
}

.button-spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Responsive */
@media (max-width: 768px) {
  .profile-tabs {
    overflow-x: auto;
  }
  
  .profile-tabs button {
    padding: 1rem;
    white-space: nowrap;
  }
  
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  
  .tab-content {
    padding: 1.5rem;
  }
}
</style>