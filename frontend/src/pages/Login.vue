<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <h1 class="login-title">Iniciar Sesión</h1>
          <p class="login-subtitle">Accede al Sistema de Gestión de Datos</p>
        </div>
        
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="username">Usuario</label>
            <div class="input-with-icon">
              <i class="material-icons">person</i>
              <input 
                type="text" 
                id="username" 
                v-model="username" 
                placeholder="Ingrese su nombre de usuario"
                required
                autocomplete="username"
              />
            </div>
            <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
          </div>
          
          <div class="form-group">
            <label for="password">Contraseña</label>
            <div class="input-with-icon">
              <i class="material-icons">lock</i>
              <input 
                :type="showPassword ? 'text' : 'password'" 
                id="password" 
                v-model="password" 
                placeholder="Ingrese su contraseña"
                required
                autocomplete="current-password"
              />
              <button 
                type="button"
                class="toggle-password"
                @click="togglePasswordVisibility"
              >
                <i class="material-icons">{{ showPassword ? 'visibility_off' : 'visibility' }}</i>
              </button>
            </div>
            <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
          </div>
          
          <div class="form-group options">
            <div class="remember-me">
              <input type="checkbox" id="remember" v-model="rememberMe" />
              <label for="remember">Recordarme</label>
            </div>
            
            <a href="#" @click.prevent="forgotPassword" class="forgot-password">
              ¿Olvidó su contraseña?
            </a>
          </div>
          
          <!-- Mensaje de sesión expirada -->
          <div v-if="sessionExpired" class="alert-warning">
            <i class="material-icons">schedule</i>
            <span>Tu sesión ha expirado. Por favor, inicia sesión nuevamente.</span>
          </div>

          <div v-if="error" class="alert-error">
            <i class="material-icons">error</i>
            <span>{{ error }}</span>
          </div>
          
          <button 
            type="submit" 
            class="login-button"
            :disabled="loading"
          >
            <span v-if="!loading">Iniciar Sesión</span>
            <div v-else class="button-spinner"></div>
          </button>
        </form>
        
        <div class="login-footer">
          <p>¿No tiene una cuenta? Contacte los administradores del sistema.</p>
          
          <div class="help-links">
            <a href="#" @click.prevent="showHelp">Ayuda</a>
            <a href="#" @click.prevent="goBack">Volver al inicio</a>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Modal de confirmación de login exitoso -->
    <div v-if="showSuccessModal" class="modal-overlay">
      <div class="modal-container">
        <div class="modal-content success-modal">
          <div class="modal-icon">
            <i class="material-icons">check_circle</i>
          </div>
          <h2>¡Inicio de sesión exitoso!</h2>
          <p>Bienvenido/a, {{ getUserName() }}</p>
          <button @click="redirectAfterLogin" class="btn btn-primary">
            Continuar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'

export default defineComponent({
  name: 'LoginPage',
  
  setup() {
    const router = useRouter()
    const route = useRoute()
    const authStore = useAuthStore()
    
    // Estado del formulario
    const username = ref('')
    const password = ref('')
    const rememberMe = ref(false)
    const showPassword = ref(false)
    const loading = ref(false)
    const error = ref('')
    const errors = ref({
      username: '',
      password: ''
    })
    
    // Estado para modal de éxito
    const showSuccessModal = ref(false)

    // Detectar si la sesión expiró (viene de redirección por token expirado)
    const sessionExpired = computed(() => route.query.expired === '1')
    
    // URL de redirección después del login
    const redirectTo = computed(() => {
      return route.query.redirect?.toString() || '/'
    })
    
    // Obtener nombre de usuario para el saludo
    const getUserName = () => {
      const userProfile = localStorage.getItem('userProfile')
      if (userProfile) {
        try {
          const profile = JSON.parse(userProfile)
          return profile.firstName || profile.first_name || profile.nombre || profile.username || username.value
        } catch (e) {
          console.warn('Error al parsear perfil para saludo:', e)
        }
      }
      return username.value || 'Usuario'
    }
    
    // Alternar visibilidad de la contraseña
    const togglePasswordVisibility = () => {
      showPassword.value = !showPassword.value
    }
    
    // Validar el formulario
    const validateForm = (): boolean => {
      let isValid = true
      errors.value.username = ''
      errors.value.password = ''
      
      if (!username.value.trim()) {
        errors.value.username = 'El nombre de usuario es requerido'
        isValid = false
      }
      
      if (!password.value) {
        errors.value.password = 'La contraseña es requerida'
        isValid = false
      } else if (password.value.length < 3) { // Reducir requisito mínimo
        errors.value.password = 'La contraseña debe tener al menos 3 caracteres'
        isValid = false
      }
      
      return isValid
    }
    
    // 🔧 HANDLELOGIN SIMPLIFICADO - SIN LÓGICA COMPLEJA
    const handleLogin = async () => {
      // Validación inicial del formulario
      if (!validateForm()) {
        return;
      }

      try {
        loading.value = true;
        error.value = '';
        
        console.log("🔑 Intentando login con:", {
          username: username.value,
          passwordLength: password.value.length
        });

        // 1. Ejecutar el login principal (toda la lógica está en el store)
        const loginSuccess = await authStore.login({
          username: username.value.trim(),
          password: password.value
        });

        if (!loginSuccess) {
          throw new Error('Login falló - revisar credenciales');
        }

        console.log("✅ Login exitoso, verificando estado...");
        
        // 2. Verificar que el login fue exitoso
        if (!authStore.isAuthenticated) {
          throw new Error('Login completado pero usuario no autenticado');
        }

        // 3. Manejar recordar usuario
        if (rememberMe.value) {
          localStorage.setItem('rememberedUser', username.value);
        } else {
          localStorage.removeItem('rememberedUser');
        }

        console.log("✅ Todo OK, mostrando modal de éxito");
        
        // 4. Mostrar modal de éxito
        showSuccessModal.value = true;
        
        // 5. Redirección automática después de 3 segundos como fallback
        setTimeout(() => {
          if (showSuccessModal.value) {
            console.log("⏰ Redirección automática por timeout");
            redirectAfterLogin();
          }
        }, 1000);

      } catch (err: any) {
        console.error('🔥 ERROR EN LOGIN:', {
          error: err,
          message: err.message,
          response: err.response,
          username: username.value,
          timestamp: new Date().toISOString()
        });

        // Usar el error del store si existe, sino usar el error del catch
        error.value = authStore.error || err.message || 'Error al iniciar sesión. Intente nuevamente';
        
        // Limpiar contraseña en caso de error
        password.value = '';
        
      } finally {
        loading.value = false;
      }
    };

    // Función de redirección manual
    const redirectAfterLogin = () => {
      console.log("🚀 Redirigiendo después del login exitoso");
      showSuccessModal.value = false;
      
      // Determinar ruta final
      const finalPath = redirectTo.value;
      console.log("📍 Redirigiendo a:", finalPath);
      
      router.replace(finalPath);
      
      // Forzar actualización de componentes dependientes
      nextTick(() => {
        window.dispatchEvent(new Event('auth-updated'));
        console.log("✅ Eventos de actualización disparados");
      });
    };
    
    // Manejar olvido de contraseña
    const forgotPassword = () => {
      router.push('/recuperar-contrasena')
    }
    
    // Mostrar ayuda
    const showHelp = () => {
      alert('Para obtener ayuda, contacte al administrador del sistema al correo soporte@gesdat.com o al teléfono (57) 1234-5678.')
    }
    
    // Volver a la página de inicio
    const goBack = () => {
      router.push('/')
    }
    
    // Al montar el componente, verificar si hay un usuario recordado
    const checkRememberedUser = () => {
      const rememberedUser = localStorage.getItem('rememberedUser')
      if (rememberedUser) {
        username.value = rememberedUser
        rememberMe.value = true
      }
    }
    
    // Llamar a la función al montar el componente
    onMounted(() => {
      checkRememberedUser()
      
      // Si el usuario ya está autenticado, redirigir al inicio
      if (authStore.isAuthenticated) {
        console.log("⚠️ Usuario ya autenticado, redirigiendo...");
        router.push(redirectTo.value)
      }
    })
    
    return {
      username,
      password,
      rememberMe,
      showPassword,
      loading,
      error,
      errors,
      showSuccessModal,
      sessionExpired,
      authStore,
      togglePasswordVisibility,
      handleLogin,
      redirectAfterLogin,
      forgotPassword,
      showHelp,
      goBack,
      getUserName
    }
  }
})
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 200px);
  background-color: #f5f7fa;
  padding: 2rem 1rem;
}

.login-container {
  width: 100%;
  max-width: 450px;
}

.login-card {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.login-header {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  padding: 2rem;
  text-align: center;
}

.login-title {
  font-size: 1.8rem;
  margin: 0 0 0.5rem;
}

.login-subtitle {
  opacity: 0.9;
  margin: 0;
}

.login-form {
  padding: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #495057;
}

.input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.input-with-icon i {
  position: absolute;
  left: 12px;
  color: #adb5bd;
}

.input-with-icon input {
  width: 100%;
  padding: 0.75rem 0.75rem 0.75rem 2.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-with-icon input:focus {
  border-color: #80bdff;
  outline: none;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.toggle-password {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-password:focus {
  outline: none;
}

.options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.remember-me input[type="checkbox"] {
  width: 16px;
  height: 16px;
}

.forgot-password {
  color: #007bff;
  text-decoration: none;
  font-size: 0.9rem;
}

.forgot-password:hover {
  text-decoration: underline;
}

.error-message {
  color: #dc3545;
  font-size: 0.85rem;
  margin-top: 0.25rem;
  display: block;
}

.alert-warning {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #fff3cd;
  color: #856404;
  padding: 0.75rem 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  border: 1px solid #ffc107;
}

.alert-warning i {
  font-size: 1.25rem;
}

.alert-error {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #f8d7da;
  color: #721c24;
  padding: 0.75rem 1rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.login-button {
  width: 100%;
  background-color: #007bff;
  color: white;
  border: none;
  padding: 0.75rem;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 48px;
}

.login-button:hover {
  background-color: #0069d9;
}

.login-button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.button-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.login-footer {
  padding: 1.5rem 2rem;
  border-top: 1px solid #e9ecef;
  text-align: center;
}

.login-footer p {
  color: #6c757d;
  margin-bottom: 1rem;
}

.help-links {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
}

.help-links a {
  color: #007bff;
  text-decoration: none;
}

.help-links a:hover {
  text-decoration: underline;
}

/* Modal de éxito */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  width: 90%;
  max-width: 400px;
  margin: 0 auto;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.success-modal .modal-icon {
  margin-bottom: 1rem;
}

.success-modal .modal-icon i {
  font-size: 4rem;
  color: #28a745;
}

.success-modal h2 {
  margin-bottom: 0.5rem;
  color: #343a40;
}

.success-modal p {
  margin-bottom: 1.5rem;
  color: #6c757d;
}

.success-modal button {
  padding: 0.75rem 2rem;
  font-size: 1rem;
}

@media (max-width: 576px) {
  .login-header {
    padding: 1.5rem;
  }
  
  .login-form {
    padding: 1.5rem;
  }
  
  .options {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  
  .help-links {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .modal-content {
    padding: 1.5rem;
  }
}
</style>