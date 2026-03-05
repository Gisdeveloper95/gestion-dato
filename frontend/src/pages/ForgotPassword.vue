<template>
  <div class="forgot-password-page">
    <div class="forgot-password-container">
      <div class="forgot-password-card">
        <div class="forgot-password-header">
          <h1 class="forgot-password-title">Recuperar Contraseña</h1>
          <p class="forgot-password-subtitle">Ingrese su correo electrónico para recibir instrucciones</p>
        </div>

        <!-- Formulario de solicitud -->
        <form v-if="!emailSent" @submit.prevent="handleSubmit" class="forgot-password-form">
          <div class="form-group">
            <label for="email">Correo electrónico</label>
            <div class="input-with-icon">
              <i class="material-icons">email</i>
              <input
                type="email"
                id="email"
                v-model="email"
                placeholder="Ingrese su correo electrónico"
                required
                autocomplete="email"
              />
            </div>
            <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
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
            <span v-if="!loading">Enviar Instrucciones</span>
            <div v-else class="button-spinner"></div>
          </button>
        </form>

        <!-- Mensaje de éxito -->
        <div v-else class="success-message">
          <div class="success-icon">
            <i class="material-icons">mark_email_read</i>
          </div>
          <h2>Solicitud procesada</h2>
          <p>
            Si existe una cuenta asociada a <strong>{{ email }}</strong>,
            recibirás un correo con las instrucciones para restablecer tu contraseña.
          </p>
          <p class="info-text">
            Revisa tu bandeja de entrada y carpeta de spam. El enlace expira en 1 hora.
          </p>
          <button @click="resetForm" class="btn-secondary">
            Intentar con otro correo
          </button>
        </div>

        <div class="forgot-password-footer">
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
import { defineComponent, ref } from 'vue'
import axios from 'axios'

export default defineComponent({
  name: 'ForgotPasswordPage',

  setup() {
    const email = ref('')
    const loading = ref(false)
    const error = ref('')
    const emailSent = ref(false)
    const errors = ref({
      email: ''
    })

    // Obtener la URL base de la API
    const getApiUrl = () => {
      const baseUrl = import.meta.env.VITE_API_URL || 'https://gestiondato.duckdns.org'
      return `${baseUrl}/preoperacion/auth/request-password-reset/`
    }

    // Validar el formulario
    const validateForm = (): boolean => {
      let isValid = true
      errors.value.email = ''

      if (!email.value.trim()) {
        errors.value.email = 'El correo electrónico es requerido'
        isValid = false
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
        errors.value.email = 'Ingrese un correo electrónico válido'
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

        console.log('Solicitando recuperación de contraseña para:', email.value)

        await axios.post(getApiUrl(), {
          email_or_username: email.value.trim()
        })

        // Éxito - mostrar mensaje
        emailSent.value = true
        console.log('Correo de recuperación enviado exitosamente')

      } catch (err: any) {
        console.error('Error al solicitar recuperación:', err)

        // El backend siempre devuelve éxito por seguridad (para no revelar emails existentes)
        // Pero si hay un error real del servidor, lo mostramos
        if (err.response?.status >= 500) {
          error.value = 'Error en el servidor. Intente más tarde.'
        } else if (err.response?.status === 429) {
          error.value = 'Demasiados intentos. Espere unos minutos.'
        } else {
          // Por seguridad, siempre mostramos éxito aunque el email no exista
          emailSent.value = true
        }
      } finally {
        loading.value = false
      }
    }

    // Resetear el formulario para enviar de nuevo
    const resetForm = () => {
      emailSent.value = false
      error.value = ''
    }

    return {
      email,
      loading,
      error,
      errors,
      emailSent,
      handleSubmit,
      resetForm
    }
  }
})
</script>

<style scoped>
.forgot-password-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 200px);
  background-color: #f5f7fa;
  padding: 2rem 1rem;
}

.forgot-password-container {
  width: 100%;
  max-width: 450px;
}

.forgot-password-card {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.forgot-password-header {
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
  padding: 2rem;
  text-align: center;
}

.forgot-password-title {
  font-size: 1.8rem;
  margin: 0 0 0.5rem;
}

.forgot-password-subtitle {
  opacity: 0.9;
  margin: 0;
}

.forgot-password-form {
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
  box-shadow: 0 0 0 0.2rem rgba(23, 162, 184, 0.25);
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
  background-color: #17a2b8;
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
  background-color: #138496;
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

/* Mensaje de éxito */
.success-message {
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

.success-message h2 {
  margin-bottom: 0.5rem;
  color: #343a40;
}

.success-message p {
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.success-message .info-text {
  font-size: 0.9rem;
  color: #868e96;
  margin-bottom: 1.5rem;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  font-size: 0.9rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

/* Footer */
.forgot-password-footer {
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
  .forgot-password-header {
    padding: 1.5rem;
  }

  .forgot-password-form {
    padding: 1.5rem;
  }

  .success-message {
    padding: 1.5rem;
  }
}
</style>
