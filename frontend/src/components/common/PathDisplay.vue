<template>
  <div class="path-display" :class="{ 'path-display--compact': compact }">
    <!-- Ruta mostrada (siempre en formato Windows para usuarios) -->
    <div class="path-content" :title="tooltipText">
      <i v-if="showIcon" class="material-icons path-icon">{{ pathIcon }}</i>
      <span class="path-text" :class="{ 'path-text--truncate': truncate }">
        {{ displayPath }}
      </span>
    </div>

    <!-- Botones de acción -->
    <div class="path-actions" v-if="showActions">
      <!-- Botón copiar -->
      <button
        @click="copiarRuta"
        class="btn-path-action btn-copy"
        :title="copiado ? 'Copiado!' : 'Copiar ruta Windows al portapapeles'"
        :class="{ 'btn-copied': copiado }"
      >
        <i class="material-icons">{{ copiado ? 'check' : 'content_copy' }}</i>
        <span v-if="showLabels">{{ copiado ? 'Copiado' : 'Copiar' }}</span>
      </button>

      <!-- Botón abrir (solo informativo ya que no puede abrir desde web) -->
      <button
        v-if="showOpenButton"
        @click="mostrarInstrucciones"
        class="btn-path-action btn-open"
        title="Ver instrucciones para abrir"
      >
        <i class="material-icons">open_in_new</i>
        <span v-if="showLabels">Abrir</span>
      </button>
    </div>

    <!-- Toast de confirmación -->
    <Transition name="toast">
      <div v-if="mostrarToast" class="path-toast">
        <i class="material-icons">check_circle</i>
        <span>Ruta copiada al portapapeles</span>
      </div>
    </Transition>

    <!-- Modal de instrucciones -->
    <Teleport to="body">
      <div v-if="mostrarModalInstrucciones" class="modal-overlay" @click="cerrarModal">
        <div class="modal-instrucciones" @click.stop>
          <div class="modal-header">
            <h3>
              <i class="material-icons">help_outline</i>
              Cómo acceder a este archivo
            </h3>
            <button @click="cerrarModal" class="btn-close-modal">
              <i class="material-icons">close</i>
            </button>
          </div>
          <div class="modal-body">
            <div class="instruccion-paso">
              <div class="paso-numero">1</div>
              <div class="paso-contenido">
                <strong>Copiar la ruta</strong>
                <p>Haz clic en el botón "Copiar" para copiar la ruta al portapapeles.</p>
              </div>
            </div>

            <div class="instruccion-paso">
              <div class="paso-numero">2</div>
              <div class="paso-contenido">
                <strong>Abrir el Explorador de Windows</strong>
                <p>Presiona <kbd>Win</kbd> + <kbd>E</kbd> o abre cualquier carpeta.</p>
              </div>
            </div>

            <div class="instruccion-paso">
              <div class="paso-numero">3</div>
              <div class="paso-contenido">
                <strong>Pegar la ruta</strong>
                <p>Haz clic en la barra de direcciones y pega la ruta con <kbd>Ctrl</kbd> + <kbd>V</kbd></p>
              </div>
            </div>

            <div class="instruccion-paso">
              <div class="paso-numero">4</div>
              <div class="paso-contenido">
                <strong>Navegar</strong>
                <p>Presiona <kbd>Enter</kbd> para ir a la ubicación del archivo.</p>
              </div>
            </div>

            <div class="ruta-preview">
              <label>Ruta a copiar:</label>
              <div class="ruta-preview-content">
                <code>{{ displayPath }}</code>
                <button @click="copiarRuta" class="btn-copy-small">
                  <i class="material-icons">content_copy</i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { linuxToWindowsPath, isPathLike, copyPathToClipboard } from '@/utils/pathUtils'

// Props
interface Props {
  /** Ruta original (puede ser Linux o Windows) */
  path: string | null | undefined
  /** Mostrar en modo compacto */
  compact?: boolean
  /** Truncar texto largo */
  truncate?: boolean
  /** Mostrar icono de carpeta/archivo */
  showIcon?: boolean
  /** Mostrar botones de acción */
  showActions?: boolean
  /** Mostrar botón de abrir */
  showOpenButton?: boolean
  /** Mostrar etiquetas en botones */
  showLabels?: boolean
  /** Icono personalizado (material-icons) */
  icon?: string
  /** Texto a mostrar si no hay ruta */
  emptyText?: string
}

const props = withDefaults(defineProps<Props>(), {
  path: null,
  compact: false,
  truncate: true,
  showIcon: true,
  showActions: true,
  showOpenButton: false,
  showLabels: false,
  icon: '',
  emptyText: 'Sin ruta definida'
})

// Emits
const emit = defineEmits<{
  (e: 'copied', path: string): void
  (e: 'error', error: Error): void
}>()

// Estado
const copiado = ref(false)
const mostrarToast = ref(false)
const mostrarModalInstrucciones = ref(false)

// Computed
const displayPath = computed(() => {
  if (!props.path) {
    return props.emptyText
  }

  // Convertir a Windows si es una ruta Linux
  const converted = linuxToWindowsPath(props.path)
  return converted || props.emptyText
})

const pathIcon = computed(() => {
  if (props.icon) {
    return props.icon
  }

  if (!props.path) {
    return 'folder_off'
  }

  // Detectar si es archivo o carpeta por la extensión
  const path = props.path.toLowerCase()
  if (path.match(/\.[a-z0-9]{1,5}$/)) {
    // Tiene extensión, probablemente es archivo
    return 'description'
  }

  return 'folder'
})

const tooltipText = computed(() => {
  if (!props.path) {
    return 'No hay ruta definida'
  }

  return `Ruta Windows: ${displayPath.value}\n\nHaz clic en "Copiar" para copiar al portapapeles.`
})

const hayRutaValida = computed(() => {
  return props.path && isPathLike(props.path)
})

// Métodos
const copiarRuta = async () => {
  if (!displayPath.value || displayPath.value === props.emptyText) {
    return
  }

  try {
    await copyPathToClipboard(displayPath.value)
    copiado.value = true
    mostrarToast.value = true

    emit('copied', displayPath.value)

    // Resetear estados después de un tiempo
    setTimeout(() => {
      copiado.value = false
    }, 2000)

    setTimeout(() => {
      mostrarToast.value = false
    }, 3000)
  } catch (error) {
    console.error('Error copiando ruta:', error)
    emit('error', error as Error)
  }
}

const mostrarInstrucciones = () => {
  mostrarModalInstrucciones.value = true
}

const cerrarModal = () => {
  mostrarModalInstrucciones.value = false
}
</script>

<style scoped>
.path-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
}

.path-display--compact {
  gap: 0.25rem;
}

.path-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  min-width: 0;
  padding: 0.5rem 0.75rem;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.85rem;
  color: #495057;
}

.path-display--compact .path-content {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
}

.path-icon {
  color: #6c757d;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.path-text {
  flex: 1;
  min-width: 0;
  word-break: break-all;
}

.path-text--truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.path-actions {
  display: flex;
  gap: 0.25rem;
  flex-shrink: 0;
}

.btn-path-action {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.4rem 0.6rem;
  border: 1px solid;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-path-action .material-icons {
  font-size: 1rem;
}

.btn-copy {
  background: #e3f2fd;
  border-color: #90caf9;
  color: #1565c0;
}

.btn-copy:hover {
  background: #bbdefb;
  border-color: #64b5f6;
}

.btn-copied {
  background: #e8f5e9;
  border-color: #a5d6a7;
  color: #2e7d32;
}

.btn-open {
  background: #fff3e0;
  border-color: #ffcc80;
  color: #e65100;
}

.btn-open:hover {
  background: #ffe0b2;
  border-color: #ffb74d;
}

/* Toast de confirmación */
.path-toast {
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #2e7d32;
  color: white;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
  white-space: nowrap;
}

.path-toast .material-icons {
  font-size: 1rem;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}

/* Modal de instrucciones */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-instrucciones {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
}

.modal-header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #333;
  font-size: 1.2rem;
}

.modal-header h3 .material-icons {
  color: #1976d2;
}

.btn-close-modal {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.2s;
}

.btn-close-modal:hover {
  background: #e9ecef;
  color: #333;
}

.modal-body {
  padding: 1.5rem;
}

.instruccion-paso {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.paso-numero {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #1976d2, #1565c0);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}

.paso-contenido strong {
  display: block;
  color: #333;
  margin-bottom: 0.25rem;
}

.paso-contenido p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
}

.paso-contenido kbd {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  font-size: 0.8rem;
  font-family: inherit;
  color: #333;
  background-color: #f4f4f4;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-shadow: 0 1px 1px rgba(0, 0, 0, 0.1);
}

.ruta-preview {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
}

.ruta-preview label {
  display: block;
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.ruta-preview-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.ruta-preview-content code {
  flex: 1;
  padding: 0.5rem 0.75rem;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.8rem;
  color: #333;
  word-break: break-all;
}

.btn-copy-small {
  padding: 0.5rem;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.btn-copy-small:hover {
  background: #1565c0;
}

.btn-copy-small .material-icons {
  font-size: 1.1rem;
}

/* Responsive */
@media (max-width: 768px) {
  .path-display {
    flex-direction: column;
    align-items: stretch;
  }

  .path-actions {
    justify-content: flex-end;
  }

  .path-text--truncate {
    white-space: normal;
  }
}
</style>
