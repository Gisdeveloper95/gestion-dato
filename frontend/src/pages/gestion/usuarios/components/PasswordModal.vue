<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h3 class="modal-title">
          <i class="material-icons">lock_reset</i>
          Cambiar Contraseña
        </h3>
      </div>
      
      <div class="modal-body">
        <div class="user-info">
          <div class="user-avatar">
            <i class="material-icons">{{ getAvatarIcon(usuario?.rol_tipo) }}</i>
          </div>
          <div class="user-details">
            <h4>{{ getNombreCompleto(usuario) }}</h4>
            <p>@{{ usuario?.username }}</p>
          </div>
        </div>
        
        <form @submit.prevent="confirmarCambio" class="password-form">
          <div class="form-group">
            <label for="nueva-password" class="form-label">
              <i class="material-icons">lock</i>
              Nueva Contraseña
            </label>
            <div class="password-input-container">
              <input
                id="nueva-password"
                v-model="nuevaPassword"
                :type="mostrarPassword ? 'text' : 'password'"
                class="form-input"
                placeholder="Ingrese la nueva contraseña"
                :class="{ error: error }"
                autocomplete="new-password"
                required
                minlength="4"
              />
              <button
                type="button"
                @click="toggleMostrarPassword"
                class="password-toggle"
                :title="mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
              >
                <i class="material-icons">{{ mostrarPassword ? 'visibility_off' : 'visibility' }}</i>
              </button>
            </div>
            <div class="password-help">
              <small>
                <i class="material-icons">info</i>
                Mínimo 4 caracteres (página privada, contraseña simple permitida)
              </small>
            </div>
          </div>
          
          <div class="form-group">
            <label for="confirmar-password" class="form-label">
              <i class="material-icons">lock_outline</i>
              Confirmar Contraseña
            </label>
            <div class="password-input-container">
              <input
                id="confirmar-password"
                v-model="confirmarPassword"
                :type="mostrarConfirmarPassword ? 'text' : 'password'"
                class="form-input"
                placeholder="Confirme la nueva contraseña"
                :class="{ error: error }"
                autocomplete="new-password"
                required
                minlength="4"
              />
              <button
                type="button"
                @click="toggleMostrarConfirmarPassword"
                class="password-toggle"
                :title="mostrarConfirmarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
              >
                <i class="material-icons">{{ mostrarConfirmarPassword ? 'visibility_off' : 'visibility' }}</i>
              </button>
            </div>
          </div>
          
          <div v-if="error" class="error-message">
            <i class="material-icons">error</i>
            {{ error }}
          </div>
        </form>
      </div>
      
      <div class="modal-footer">
        <button 
          @click="$emit('cancel')" 
          class="btn btn-secondary"
          :disabled="loading"
        >
          Cancelar
        </button>
        
        <button 
          @click="confirmarCambio" 
          class="btn btn-primary"
          :disabled="loading || !puedeConfirmar"
        >
          <span v-if="loading" class="loading-spinner"></span>
          <i v-else class="material-icons">lock_reset</i>
          Cambiar Contraseña
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { Usuario } from '@/api/usuarios'

interface Props {
  show: boolean
  usuario: Usuario | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  confirm: [password: string]
  cancel: []
}>()

// =============== STATE ===============
const nuevaPassword = ref('')
const confirmarPassword = ref('')
const mostrarPassword = ref(false)
const mostrarConfirmarPassword = ref(false)
const loading = ref(false)
const error = ref('')

// =============== COMPUTED ===============
const puedeConfirmar = computed(() => {
  return nuevaPassword.value.length >= 4 && 
         confirmarPassword.value.length >= 4 && 
         nuevaPassword.value === confirmarPassword.value &&
         !error.value
})

// =============== WATCHERS ===============
watch([nuevaPassword, confirmarPassword], () => {
  error.value = ''
  
  if (nuevaPassword.value && confirmarPassword.value) {
    if (nuevaPassword.value !== confirmarPassword.value) {
      error.value = 'Las contraseñas no coinciden'
    } else if (nuevaPassword.value.length < 4) {
      error.value = 'La contraseña debe tener al menos 4 caracteres'
    }
  }
})

watch(() => props.show, (newShow) => {
  if (newShow) {
    resetForm()
  }
})

// =============== METHODS ===============
const resetForm = () => {
  nuevaPassword.value = ''
  confirmarPassword.value = ''
  mostrarPassword.value = false
  mostrarConfirmarPassword.value = false
  loading.value = false
  error.value = ''
}

const confirmarCambio = async () => {
  if (!puedeConfirmar.value) return
  
  try {
    loading.value = true
    emit('confirm', nuevaPassword.value)
  } catch (err) {
    console.error('Error en modal:', err)
  } finally {
    loading.value = false
  }
}

const toggleMostrarPassword = () => {
  mostrarPassword.value = !mostrarPassword.value
}

const toggleMostrarConfirmarPassword = () => {
  mostrarConfirmarPassword.value = !mostrarConfirmarPassword.value
}

const handleOverlayClick = () => {
  if (!loading.value) {
    emit('cancel')
  }
}

const getNombreCompleto = (usuario: Usuario | null): string => {
  if (!usuario) return ''
  const nombre = `${usuario.first_name} ${usuario.last_name}`.trim()
  return nombre || usuario.username
}

const getAvatarIcon = (rolTipo?: string): string => {
  const icons = {
    'super_admin': 'admin_panel_settings',
    'admin': 'manage_accounts',
    'profesional': 'person'
  }
  return icons[rolTipo as keyof typeof icons] || 'person'
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.2s ease-out;
}

.modal-container {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.2s ease-out;
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  background: linear-gradient(135deg, #fef3c7 0%, #fbbf24 100%);
}

.modal-title {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.2rem;
  font-weight: 600;
  color: #92400e;
}

.modal-body {
  padding: 1.5rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.user-details h4 {
  margin: 0 0 0.25rem 0;
  color: #1f2937;
  font-weight: 600;
}

.user-details p {
  margin: 0;
  color: #6b7280;
  font-size: 0.9rem;
}

.password-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

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

.form-label i {
  font-size: 1.1rem;
  color: #6b7280;
}

.password-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.form-input {
  width: 100%;
  padding: 0.75rem 3rem 0.75rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.2s;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input.error {
  border-color: #ef4444;
}

.form-input.error:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.password-toggle {
  position: absolute;
  right: 0.75rem;
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

.password-help {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.8rem;
}

.password-help i {
  font-size: 1rem;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #ef4444;
  font-size: 0.9rem;
  background: #fef2f2;
  padding: 0.75rem;
  border-radius: 6px;
  border: 1px solid #fecaca;
}

.modal-footer {
  padding: 1rem 1.5rem;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
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

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 640px) {
  .modal-container {
    width: 95%;
    margin: 1rem;
  }
  
  .modal-footer {
    flex-direction: column-reverse;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
  
  .user-info {
    flex-direction: column;
    text-align: center;
  }
}
</style>