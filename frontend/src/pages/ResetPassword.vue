<template>
  <div class="reset-password-page">
    <div class="reset-password-container">
      <div class="reset-password-card">
        <!-- Estado: Validando token -->
        <div v-if="validating" class="validating-state">
          <div class="spinner-large"></div>
          <p>Validando enlace...</p>
        </div>

        <!-- Estado: Token inválido o expirado -->
        <div v-else-if="tokenInvalid" class="invalid-state">
          <div class="reset-password-header error-header">
            <h1 class="reset-password-title">Enlace no válido</h1>
            <p class="reset-password-subtitle">El enlace ha expirado o no es válido</p>
          </div>
          <div class="invalid-content">
            <div class="invalid-icon">
              <i class="material-icons">link_off</i>
            </div>
            <p>
              Este enlace de recuperación ya no es válido. Los enlaces expiran después de 1 hora
              o después de ser utilizados.
            </p>
            <router-link to="/recuperar-contrasena" class="btn-primary">
              Solicitar nuevo enlace
            </router-link>
          </div>
        </div>

        <!-- Estado: Contraseña restablecida con éxito -->
        <div v-else-if="passwordReset" class="success-state">
          <div class="reset-password-header success-header">
            <h1 class="reset-password-title">Contraseña actualizada</h1>
            <p class="reset-password-subtitle">Su contraseña ha sido restablecida exitosamente</p>
          </div>
          <div class="success-content">
            <div class="success-icon">
              <i class="material-icons">check_circle</i>
            </div>
            <p>
              Ahora puede iniciar sesión con su nueva contraseña.
            </p>
            <router-link to="/login" class="btn-primary">
              Ir a Iniciar Sesión
            </router-link>
          </div>
        </div>

        <!-- Estado: Formulario para nueva contraseña -->
        <template v-else>
          <div class="reset-password-header">
            <h1 class="reset-password-title">Nueva Contraseña</h1>
            <p class="reset-password-subtitle">Ingrese su nueva contraseña</p>
          </div>

          <form @submit.prevent="handleSubmit" class="reset-password-form">
            <div class="form-group">
              <label for="password">Nueva contraseña</label>
              <div class="input-with-icon">
                <i class="material-icons">lock</i>
                <input
                  :type="showPassword ? 'text' : 'password'"
                  id="password"
                  v-model="password"
                  placeholder="Ingrese su nueva contraseña"
                  required
                  autocomplete="new-password"
                />
                <button
                  type="button"
                  class="toggle-password"
                  @click="showPassword = !showPassword"
                >
                  <i class="material-icons">{{ showPassword ? 'visibility_off' : 'visibility' }}</i>
                </button>
              </div>
              <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
            </div>

            <div class="form-group">
              <label for="confirmPassword">Confirmar contraseña</label>
              <div class="input-with-icon">
                <i class="material-icons">lock_outline</i>
                <input
                  :type="showConfirmPassword ? 'text' : 'password'"
                  id="confirmPassword"
                  v-model="confirmPassword"
                  placeholder="Confirme su nueva contraseña"
                  required
                  autocomplete="new-password"
                />
                <button
                  type="button"
                  class="toggle-password"
                  @click="showConfirmPassword = !showConfirmPassword"
                >
                  <i class="material-icons">{{ showConfirmPassword ? 'visibility_off' : 'visibility' }}</i>
                </button>
              </div>
              <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</span>
            </div>

            <!-- Requisitos de contraseña -->
            <div class="password-requirements">
              <p class="requirements-title">La contraseña debe tener:</p>
              <ul>
                <li :class="{ valid: password.length >= 8 }">
                  <i class="material-icons">{{ password.length >= 8 ? 'check_circle' : 'radio_button_unchecked' }}</i>
                  Al menos 8 caracteres
                </li>
                <li :class="{ valid: /[A-Z]/.test(password) }">
                  <i class="material-icons">{{ /[A-Z]/.test(password) ? 'check_circle' : 'radio_button_unchecked' }}</i>
                  Una letra mayúscula
                </li>
                <li :class="{ valid: /[a-z]/.test(password) }">
                  <i class="material-icons">{{ /[a-z]/.test(password) ? 'check_circle' : 'radio_button_unchecked' }}</i>
                  Una letra minúscula
                </li>
                <li :class="{ valid: /[0-9]/.test(password) }">
                  <i class="material-icons">{{ /[0-9]/.test(password) ? 'check_circle' : 'radio_button_unchecked' }}</i>
                  Un número
                </li>
              </ul>
            </div>

            <div v-if="error" class="alert-error">
              <i class="material-icons">error</i>
              <span>{{ error }}</span>
            </div>

            <button
              type="submit"
              class="submit-button"
              :disabled="loading"
            >
              <span v-if="!loading">Restablecer Contraseña</span>
              <div v-else class="button-spinner"></div>
            </button>
          </form>
        </template>

        <div v-if="!validating && !tokenInvalid && !passwordReset" class="reset-password-footer">
          <router-link to="/login" class="back-link">
            <i class="material-icons">arrow_back</i>
            Volver a Iniciar Sesión
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

export default defineComponent({
  name: 'ResetPasswordPage',

  setup() {
    const route = useRoute()
    const router = useRouter()

    const token = ref('')
    const password = ref('')
    const confirmPassword = ref('')
    const showPassword = ref(false)
    const showConfirmPassword = ref(false)
    const loading = ref(false)
    const validating = ref(true)
    const tokenInvalid = ref(false)
    const passwordReset = ref(false)
    const error = ref('')
    const errors = ref({
      password: '',
      confirmPassword: ''
    })

    // Obtener la URL base de la API
    const getApiUrl = (endpoint: string) => {
      const baseUrl = import.meta.env.VITE_API_URL || 'https://gestiondato.duckdns.org'
      return `${baseUrl}/preoperacion/auth/${endpoint}/`
    }

    // Validar el token al cargar la página
    const validateToken = async () => {
      token.value = route.query.token as string || ''

      if (!token.value) {
        tokenInvalid.value = true
        validating.value = false
        return
      }

      try {
        console.log('Validando token:', token.value.substring(0, 10) + '...')

        await axios.get(getApiUrl('validate-reset-token'), {
          params: { token: token.value }
        })

        // Token válido
        validating.value = false
        console.log('Token válido')

      } catch (err: any) {
        console.error('Token inválido:', err)
        tokenInvalid.value = true
        validating.value = false
      }
    }

    // Validar el formulario
    const validateForm = (): boolean => {
      let isValid = true
      errors.value.password = ''
      errors.value.confirmPassword = ''

      // Validar longitud mínima
      if (password.value.length < 8) {
        errors.value.password = 'La contraseña debe tener al menos 8 caracteres'
        isValid = false
      }

      // Validar mayúscula
      if (!/[A-Z]/.test(password.value)) {
        errors.value.password = 'La contraseña debe contener al menos una mayúscula'
        isValid = false
      }

      // Validar minúscula
      if (!/[a-z]/.test(password.value)) {
        errors.value.password = 'La contraseña debe contener al menos una minúscula'
        isValid = false
      }

      // Validar número
      if (!/[0-9]/.test(password.value)) {
        errors.value.password = 'La contraseña debe contener al menos un número'
        isValid = false
      }

      // Validar que las contraseñas coincidan
      if (password.value !== confirmPassword.value) {
        errors.value.confirmPassword = 'Las contraseñas no coinciden'
        isValid = false
      }

      return isValid
    }

    // Manejar el envío del formulario
    const handleSubmit = async () => {
      if (!validateForm()) {
        return
      }

      try {
        loading.value = true
        error.value = ''

        console.log('Restableciendo contraseña...')

        await axios.post(getApiUrl('confirm-password-reset'), {
          token: token.value,
          new_password: password.value
        })

        // Éxito
        passwordReset.value = true
        console.log('Contraseña restablecida exitosamente')

      } catch (err: any) {
        console.error('Error al restablecer contraseña:', err)

        if (err.response?.status === 400) {
          const detail = err.response.data?.detail || err.response.data?.error
          if (detail?.includes('expirado') || detail?.includes('inválido')) {
            tokenInvalid.value = true
          } else {
            error.value = detail || 'Error al restablecer la contraseña'
          }
        } else {
          error.value = 'Error del servidor. Intente más tarde.'
        }
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      validateToken()
    })

    return {
      password,
      confirmPassword,
      showPassword,
      showConfirmPassword,
      loading,
      validating,
      tokenInvalid,
      passwordReset,
      error,
      errors,
      handleSubmit
    }
  }
})
</script>

<style scoped>
.reset-password-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 200px);
  background-color: #f5f7fa;
  padding: 2rem 1rem;
}

.reset-password-container {
  width: 100%;
  max-width: 450px;
}

.reset-password-card {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.reset-password-header {
  background: linear-gradient(135deg, #28a745, #218838);
  color: white;
  padding: 2rem;
  text-align: center;
}

.reset-password-header.error-header {
  background: linear-gradient(135deg, #dc3545, #c82333);
}

.reset-password-header.success-header {
  background: linear-gradient(135deg, #28a745, #218838);
}

.reset-password-title {
  font-size: 1.8rem;
  margin: 0 0 0.5rem;
}

.reset-password-subtitle {
  opacity: 0.9;
  margin: 0;
}

/* Validando */
.validating-state {
  padding: 4rem 2rem;
  text-align: center;
}

.spinner-large {
  width: 48px;
  height: 48px;
  border: 4px solid #e9ecef;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

.validating-state p {
  color: #6c757d;
  font-size: 1.1rem;
}

/* Estado inválido */
.invalid-content {
  padding: 2rem;
  text-align: center;
}

.invalid-icon {
  margin-bottom: 1rem;
}

.invalid-icon i {
  font-size: 4rem;
  color: #dc3545;
}

.invalid-content p {
  color: #6c757d;
  margin-bottom: 1.5rem;
}

/* Estado éxito */
.success-content {
  padding: 2rem;
  text-align: center;
}

.success-icon {
  margin-bottom: 1rem;
}

.success-icon i {
  font-size: 4rem;
  color: #28a745;
}

.success-content p {
  color: #6c757d;
  margin-bottom: 1.5rem;
}

/* Botón primario */
.btn-primary {
  display: inline-block;
  background-color: #007bff;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #0069d9;
  color: white;
}

/* Formulario */
.reset-password-form {
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
  padding: 0.75rem 2.5rem 0.75rem 2.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-with-icon input:focus {
  border-color: #80bdff;
  outline: none;
  box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25);
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

/* Requisitos de contraseña */
.password-requirements {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.requirements-title {
  font-size: 0.9rem;
  font-weight: 500;
  color: #495057;
  margin: 0 0 0.5rem;
}

.password-requirements ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.password-requirements li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #6c757d;
  padding: 0.25rem 0;
}

.password-requirements li i {
  font-size: 1rem;
}

.password-requirements li.valid {
  color: #28a745;
}

.password-requirements li.valid i {
  color: #28a745;
}

.error-message {
  color: #dc3545;
  font-size: 0.85rem;
  margin-top: 0.25rem;
  display: block;
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

.submit-button {
  width: 100%;
  background-color: #28a745;
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

.submit-button:hover {
  background-color: #218838;
}

.submit-button:disabled {
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

/* Footer */
.reset-password-footer {
  padding: 1.5rem 2rem;
  border-top: 1px solid #e9ecef;
  text-align: center;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #007bff;
  text-decoration: none;
  font-size: 0.95rem;
}

.back-link:hover {
  text-decoration: underline;
}

.back-link i {
  font-size: 1.2rem;
}

@media (max-width: 576px) {
  .reset-password-header {
    padding: 1.5rem;
  }

  .reset-password-form {
    padding: 1.5rem;
  }

  .invalid-content,
  .success-content {
    padding: 1.5rem;
  }
}
</style>
