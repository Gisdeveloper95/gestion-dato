<template>
  <Teleport to="body">
    <div v-if="isOpen" class="upload-modal-overlay" @click.self="handleClose">
      <div class="upload-modal">
        <!-- Header -->
        <div class="upload-modal-header">
          <div class="header-info">
            <h2>
              <i class="material-icons">cloud_upload</i>
              Subir Archivos
            </h2>
          </div>
          <button @click="handleClose" class="btn-close" :disabled="isUploading">
            <i class="material-icons">close</i>
          </button>
        </div>

        <!-- Destination Info - SIEMPRE VISIBLE -->
        <div class="destination-section">
          <div class="destination-header">
            <i class="material-icons">folder</i>
            <span class="destination-label">Carpeta destino:</span>
          </div>
          <div class="destination-path">
            <code>{{ fullWindowsDestinationPath }}</code>
          </div>
          <div class="destination-chars" :class="destinationPathStatus">
            <i class="material-icons">{{ destinationPathStatus === 'danger' ? 'error' : 'info' }}</i>
            <span>Ruta base: {{ fullWindowsDestinationPath.length }} caracteres</span>
          </div>
        </div>

        <!-- Content -->
        <div class="upload-modal-content">
          <!-- Step 1: Select Files -->
          <div v-if="currentStep === 'select'" class="step-content">
            <!-- Drop Zone -->
            <div
              class="drop-zone"
              :class="{ 'is-dragging': isDragging }"
              @dragover.prevent="handleDragOver"
              @dragleave="handleDragLeave"
              @drop.prevent="handleDrop"
              @click="triggerFileInput"
            >
              <i class="material-icons drop-icon">cloud_upload</i>
              <p class="drop-text">Arrastra archivos aquí o haz clic para seleccionar</p>
              <p class="drop-warning">
                <i class="material-icons">warning</i>
                Solo archivos individuales - NO directorios
              </p>
              <input
                ref="fileInput"
                type="file"
                multiple
                @change="handleFileSelect"
                class="hidden-input"
              />
            </div>

            <!-- Files List -->
            <div v-if="files.length > 0" class="files-section">
              <div class="files-header">
                <h3>
                  <i class="material-icons">list</i>
                  Archivos seleccionados ({{ files.length }})
                </h3>
                <button @click="clearAllFiles" class="btn-clear-all" :disabled="isUploading">
                  <i class="material-icons">delete_sweep</i>
                  Limpiar todo
                </button>
              </div>

              <div class="files-list">
                <div
                  v-for="fileData in files"
                  :key="fileData.id"
                  class="file-item"
                  :class="getFileStatusClass(fileData)"
                >
                  <div class="file-main">
                    <i class="material-icons file-icon">{{ getFileIcon(fileData.file) }}</i>
                    <div class="file-details">
                      <p class="file-name">{{ fileData.file.name }}</p>
                      <p class="file-meta">
                        <span class="file-size">{{ formatFileSize(fileData.file.size) }}</span>
                      </p>
                      <!-- Barra de caracteres -->
                      <div class="chars-bar-container">
                        <div class="chars-bar">
                          <div
                            class="chars-bar-fill"
                            :class="getPathLengthClass(fileData)"
                            :style="{ width: Math.min((getFullWindowsPath(fileData).length / 260) * 100, 100) + '%' }"
                          ></div>
                        </div>
                        <span class="chars-text" :class="getPathLengthClass(fileData)">
                          {{ getFullWindowsPath(fileData).length }}/260 caracteres
                        </span>
                      </div>
                    </div>
                    <div class="file-status">
                      <span class="status-badge" :class="fileData.status">
                        <i class="material-icons">{{ getStatusIcon(fileData.status) }}</i>
                        {{ getStatusText(fileData.status) }}
                      </span>
                      <button
                        v-if="fileData.status !== 'uploading' && fileData.status !== 'uploaded'"
                        @click="removeFile(fileData.id)"
                        class="btn-remove"
                        :disabled="isUploading"
                      >
                        <i class="material-icons">close</i>
                      </button>
                    </div>
                  </div>

                  <!-- Validation Errors -->
                  <div v-if="fileData.validationErrors.length > 0" class="validation-errors">
                    <div v-for="(error, idx) in fileData.validationErrors" :key="idx" class="error-item">
                      <i class="material-icons">error</i>
                      <span>{{ error }}</span>
                    </div>
                  </div>

                  <!-- Full path preview -->
                  <div class="path-preview-container">
                    <span class="path-label">Ruta final:</span>
                    <code class="path-preview" :class="getPathLengthClass(fileData)">{{ getFullWindowsPath(fileData) }}</code>
                  </div>

                  <!-- Progress Bar (when uploading) -->
                  <div v-if="fileData.status === 'uploading'" class="progress-container">
                    <div class="progress-bar">
                      <div class="progress-fill" :style="{ width: fileData.progress + '%' }"></div>
                    </div>
                    <span class="progress-text">{{ fileData.progress }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-else class="empty-state">
              <i class="material-icons">inbox</i>
              <p>No hay archivos seleccionados</p>
              <p class="empty-hint">Arrastra archivos o haz clic en la zona superior</p>
            </div>
          </div>

          <!-- Step 2: Confirmation -->
          <div v-else-if="currentStep === 'confirm'" class="step-content">
            <div class="confirmation-box">
              <div class="confirmation-icon">
                <i class="material-icons">help_outline</i>
              </div>
              <h3>Confirmar subida de archivos</h3>
              <p class="confirmation-text">
                Vas a subir <strong>{{ validFilesCount }} archivo(s)</strong> a:
              </p>
              <div class="confirmation-destination">
                <i class="material-icons">folder</i>
                <code>{{ fullWindowsDestinationPath }}</code>
              </div>

              <div class="confirmation-files-list">
                <div v-for="fileData in validFiles" :key="fileData.id" class="confirmation-file">
                  <i class="material-icons">description</i>
                  <div class="confirmation-file-info">
                    <span class="confirmation-file-name">{{ fileData.file.name }}</span>
                    <span class="confirmation-file-size">{{ formatFileSize(fileData.file.size) }}</span>
                  </div>
                </div>
              </div>

              <div class="confirmation-warning">
                <i class="material-icons">info</i>
                <span>Esta acción quedará registrada en el historial de auditoría</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="upload-modal-footer">
          <div class="footer-info">
            <p v-if="validFilesCount > 0 && currentStep === 'select'" class="valid-count">
              <i class="material-icons">check_circle</i>
              {{ validFilesCount }} archivo(s) válido(s)
            </p>
            <p v-if="invalidFilesCount > 0 && currentStep === 'select'" class="invalid-count">
              <i class="material-icons">error</i>
              {{ invalidFilesCount }} archivo(s) inválido(s)
            </p>
          </div>
          <div class="footer-actions">
            <!-- Step 1 buttons -->
            <template v-if="currentStep === 'select'">
              <button @click="handleClose" class="btn-cancel" :disabled="isUploading">
                Cancelar
              </button>
              <button
                @click="goToConfirmation"
                class="btn-next"
                :disabled="validFilesCount === 0 || isUploading"
              >
                <i class="material-icons">arrow_forward</i>
                Continuar
              </button>
            </template>

            <!-- Step 2 buttons -->
            <template v-else-if="currentStep === 'confirm'">
              <button @click="goBackToSelect" class="btn-back" :disabled="isUploading">
                <i class="material-icons">arrow_back</i>
                Volver
              </button>
              <button
                @click="handleUploadAll"
                class="btn-upload"
                :disabled="isUploading"
              >
                <template v-if="isUploading">
                  <i class="material-icons spinning">sync</i>
                  Subiendo...
                </template>
                <template v-else>
                  <i class="material-icons">cloud_upload</i>
                  Confirmar y Subir
                </template>
              </button>
            </template>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch } from 'vue'

// Extensiones peligrosas bloqueadas
const BLOCKED_EXTENSIONS = [
  '.exe', '.bat', '.cmd', '.com', '.msi', '.scr',
  '.vbs', '.js', '.ps1', '.dll', '.sh', '.bin',
  '.app', '.jar', '.pif', '.gadget', '.wsf', '.wsh',
  '.hta', '.cpl', '.msc', '.lnk', '.inf', '.reg',
  '.scf', '.msp', '.chm', '.hlp', '.sys', '.drv'
]

interface FileToUpload {
  id: string
  file: File
  validationErrors: string[]
  status: 'pending' | 'valid' | 'invalid' | 'uploading' | 'uploaded' | 'failed'
  progress: number
}

export default defineComponent({
  name: 'UploadModal',

  props: {
    isOpen: {
      type: Boolean,
      required: true
    },
    currentPath: {
      type: String,
      required: true
    },
    municipioNombre: {
      type: String,
      default: ''
    },
    initialFiles: {
      type: Array as () => File[],
      default: () => []
    },
    existingFileNames: {
      type: Array as () => string[],
      default: () => []
    }
  },

  emits: ['close', 'upload-complete'],

  setup(props, { emit }) {
    const fileInput = ref<HTMLInputElement | null>(null)
    const files = ref<FileToUpload[]>([])
    const isDragging = ref(false)
    const isUploading = ref(false)
    const currentStep = ref<'select' | 'confirm'>('select')

    // Computed - Ruta Windows completa de destino
    const fullWindowsDestinationPath = computed(() => {
      // Base path del repositorio
      let basePath = '\\\\repositorio\\DirGesCat\\2510SP\\H_Informacion_Consulta\\Sub_Proy'

      if (props.currentPath) {
        // Limpiar y convertir la ruta
        let cleanPath = props.currentPath
          .replace(/^\/+/, '')  // Quitar / inicial
          .replace(/\//g, '\\') // Convertir / a \

        if (cleanPath) {
          basePath += '\\' + cleanPath
        }
      }

      return basePath
    })

    // Status de la longitud de la ruta destino
    const destinationPathStatus = computed(() => {
      const length = fullWindowsDestinationPath.value.length
      if (length > 240) return 'danger'
      if (length > 200) return 'warning'
      return 'safe'
    })

    // Computed properties
    const validFilesCount = computed(() => files.value.filter(f => f.status === 'valid').length)
    const invalidFilesCount = computed(() => files.value.filter(f => f.status === 'invalid').length)
    const uploadedFilesCount = computed(() => files.value.filter(f => f.status === 'uploaded').length)
    const validFiles = computed(() => files.value.filter(f => f.status === 'valid'))

    // Reset when modal closes, process initial files when opens
    watch(() => props.isOpen, (isOpen) => {
      console.log('🔔 UploadModal isOpen changed:', isOpen)
      console.log('🔔 currentPath prop:', props.currentPath)
      console.log('🔔 fullWindowsDestinationPath:', fullWindowsDestinationPath.value)
      if (!isOpen) {
        files.value = []
        isUploading.value = false
        currentStep.value = 'select'
      } else {
        // Modal abierto - procesar archivos iniciales si existen (drag & drop directo)
        if (props.initialFiles && props.initialFiles.length > 0) {
          console.log('📂 Procesando archivos iniciales del drag & drop:', props.initialFiles.length)
          // Crear FileList simulada
          const dt = new DataTransfer()
          props.initialFiles.forEach(file => dt.items.add(file))
          processFiles(dt.files)
        }
      }
    })

    // Trigger file input click
    const triggerFileInput = () => {
      fileInput.value?.click()
    }

    // Handle file selection from input
    const handleFileSelect = (event: Event) => {
      const input = event.target as HTMLInputElement
      if (input.files) {
        processFiles(input.files)
      }
      input.value = ''
    }

    // Handle drag over
    const handleDragOver = () => {
      isDragging.value = true
    }

    // Handle drag leave
    const handleDragLeave = () => {
      isDragging.value = false
    }

    // Handle drop
    const handleDrop = (event: DragEvent) => {
      isDragging.value = false
      if (event.dataTransfer?.files) {
        processFiles(event.dataTransfer.files)
      }
    }

    // Process files and validate
    const processFiles = (fileList: FileList) => {
      console.log('📂 processFiles CALLED - Total files:', fileList.length)
      console.log('📂 currentPath prop:', props.currentPath)

      for (let i = 0; i < fileList.length; i++) {
        const file = fileList[i]
        console.log(`📂 Processing file ${i}: ${file.name}, size: ${file.size}, type: ${file.type}`)

        // Check if directory (size 0 and empty type usually indicates directory)
        if (file.size === 0 && file.type === '') {
          console.log(`📂 Skipping ${file.name} - appears to be directory`)
          continue
        }

        // Check if already added in this session
        const isDuplicate = files.value.some(f => f.file.name === file.name)
        if (isDuplicate) {
          console.log(`📂 Skipping ${file.name} - duplicate in session`)
          continue
        }

        // Validate file
        const errors = validateFile(file)

        // Check if file already exists in the target directory
        const existsInDirectory = props.existingFileNames.some(
          existing => existing.toLowerCase() === file.name.toLowerCase()
        )
        if (existsInDirectory) {
          errors.push(`Ya existe un archivo con este nombre en la carpeta destino`)
        }

        const status = errors.length > 0 ? 'invalid' : 'valid'
        console.log(`📂 File ${file.name} validation: status=${status}, errors=`, errors)

        files.value.push({
          id: `${Date.now()}-${i}-${Math.random().toString(36).substr(2, 9)}`,
          file,
          validationErrors: errors,
          status: status,
          progress: 0
        })
        console.log(`📂 File ${file.name} added with status: ${status}`)
      }
      console.log('📂 Total files after processing:', files.value.length)
      console.log('📂 Valid files:', files.value.filter(f => f.status === 'valid').length)
    }

    // Validate a single file
    const validateFile = (file: File): string[] => {
      const errors: string[] = []

      // Check extension
      const extension = getFileExtension(file.name).toLowerCase()
      if (BLOCKED_EXTENSIONS.includes(extension)) {
        errors.push(`Extensión "${extension}" bloqueada por seguridad`)
      }

      // Check file size (max 2500MB)
      const maxSize = 2500 * 1024 * 1024
      if (file.size > maxSize) {
        errors.push('Excede el tamaño máximo de 2500 MB')
      }

      // Check path length (Windows limit: 260 chars)
      const fullPath = getFullWindowsPathForFile(file)
      if (fullPath.length > 260) {
        errors.push(`Ruta excede 260 caracteres (${fullPath.length})`)
      }

      return errors
    }

    // Get file extension
    const getFileExtension = (filename: string): string => {
      const lastDot = filename.lastIndexOf('.')
      return lastDot > 0 ? filename.substring(lastDot) : ''
    }

    // Build full Windows path for a file
    const getFullWindowsPathForFile = (file: File): string => {
      return fullWindowsDestinationPath.value + '\\' + file.name
    }

    // Build full Windows path for a FileToUpload
    const getFullWindowsPath = (fileData: FileToUpload): string => {
      return getFullWindowsPathForFile(fileData.file)
    }

    // Get path length class for styling
    const getPathLengthClass = (fileData: FileToUpload): string => {
      const length = getFullWindowsPath(fileData).length
      if (length > 260) return 'danger'
      if (length > 230) return 'warning'
      return 'safe'
    }

    // Remove file from list
    const removeFile = (fileId: string) => {
      files.value = files.value.filter(f => f.id !== fileId)
    }

    // Clear all files
    const clearAllFiles = () => {
      files.value = []
    }

    // Handle close
    const handleClose = () => {
      if (!isUploading.value) {
        emit('close')
      }
    }

    // Go to confirmation step
    const goToConfirmation = () => {
      console.log('➡️ goToConfirmation CALLED')
      console.log('➡️ validFilesCount:', validFilesCount.value)
      console.log('➡️ currentStep before:', currentStep.value)
      if (validFilesCount.value > 0) {
        currentStep.value = 'confirm'
        console.log('➡️ currentStep after:', currentStep.value)
      } else {
        console.log('➡️ No valid files, not changing step')
      }
    }

    // Go back to select step
    const goBackToSelect = () => {
      currentStep.value = 'select'
    }

    // Upload all valid files
    const handleUploadAll = async () => {
      console.log('📤 handleUploadAll CALLED')
      console.log('📤 All files:', files.value.map(f => ({ name: f.file.name, status: f.status })))

      const filesToUpload = files.value.filter(f => f.status === 'valid')
      console.log('📤 Files to upload:', filesToUpload.length)

      if (filesToUpload.length === 0) {
        console.error('📤 NO HAY ARCHIVOS VÁLIDOS PARA SUBIR!')
        return
      }

      isUploading.value = true

      for (const fileData of filesToUpload) {
        // Mark as uploading
        const index = files.value.findIndex(f => f.id === fileData.id)
        if (index !== -1) {
          files.value[index].status = 'uploading'
          files.value[index].progress = 0
        }

        try {
          // Create FormData
          const formData = new FormData()
          formData.append('file', fileData.file)
          formData.append('path', props.currentPath)
          formData.append('filename', fileData.file.name)

          // Get token
          const token = localStorage.getItem('token')
          console.log('📤 UPLOAD DEBUG - Token:', token ? 'EXISTS' : 'NULL')
          console.log('📤 UPLOAD DEBUG - Path:', props.currentPath)
          console.log('📤 UPLOAD DEBUG - File:', fileData.file.name, fileData.file.size)

          if (!token) {
            throw new Error('No hay token de autenticación. Inicia sesión de nuevo.')
          }

          // Upload with progress tracking
          await new Promise<void>((resolve, reject) => {
            const xhr = new XMLHttpRequest()

            xhr.upload.addEventListener('progress', (event) => {
              if (event.lengthComputable) {
                const percentComplete = Math.round((event.loaded / event.total) * 100)
                const idx = files.value.findIndex(f => f.id === fileData.id)
                if (idx !== -1) {
                  files.value[idx].progress = percentComplete
                }
              }
            })

            xhr.addEventListener('load', () => {
              console.log('📤 UPLOAD DEBUG - Response status:', xhr.status)
              console.log('📤 UPLOAD DEBUG - Response:', xhr.responseText)
              if (xhr.status >= 200 && xhr.status < 300) {
                resolve()
              } else {
                let errorMsg = 'Error al subir archivo'
                try {
                  const response = JSON.parse(xhr.responseText)
                  errorMsg = response.error || errorMsg
                } catch (e) {}
                reject(new Error(errorMsg))
              }
            })

            xhr.addEventListener('error', (e) => {
              console.error('📤 UPLOAD DEBUG - XHR Error:', e)
              reject(new Error('Error de conexión'))
            })

            xhr.open('POST', '/postoperacion/subir_archivo/')
            xhr.setRequestHeader('Authorization', `Token ${token}`)
            console.log('📤 UPLOAD DEBUG - Sending request...')
            xhr.send(formData)
          })

          // Mark as uploaded
          const idx = files.value.findIndex(f => f.id === fileData.id)
          if (idx !== -1) {
            files.value[idx].status = 'uploaded'
            files.value[idx].progress = 100
          }

        } catch (error: any) {
          console.error('Error subiendo archivo:', error)
          const idx = files.value.findIndex(f => f.id === fileData.id)
          if (idx !== -1) {
            files.value[idx].status = 'failed'
            files.value[idx].validationErrors = [error.message || 'Error al subir archivo']
          }
        }
      }

      isUploading.value = false
      emit('upload-complete')

      // If all uploaded, close after delay
      const allUploaded = files.value.every(f => f.status === 'uploaded' || f.status === 'invalid')
      if (allUploaded && uploadedFilesCount.value > 0) {
        setTimeout(() => {
          emit('close')
        }, 1500)
      } else {
        // Go back to select to see failed files
        currentStep.value = 'select'
      }
    }

    // Format file size
    const formatFileSize = (bytes: number): string => {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
    }

    // Get file icon based on extension
    const getFileIcon = (file: File): string => {
      const ext = getFileExtension(file.name).toLowerCase()
      if (['.pdf'].includes(ext)) return 'picture_as_pdf'
      if (['.doc', '.docx'].includes(ext)) return 'description'
      if (['.xls', '.xlsx'].includes(ext)) return 'table_chart'
      if (['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff'].includes(ext)) return 'image'
      if (['.zip', '.rar', '.7z'].includes(ext)) return 'folder_zip'
      if (['.shp', '.gdb', '.mdb'].includes(ext)) return 'map'
      if (['.dwg', '.dxf'].includes(ext)) return 'architecture'
      return 'insert_drive_file'
    }

    // Get status icon
    const getStatusIcon = (status: string): string => {
      switch (status) {
        case 'valid': return 'check_circle'
        case 'invalid': return 'error'
        case 'uploading': return 'sync'
        case 'uploaded': return 'cloud_done'
        case 'failed': return 'error_outline'
        default: return 'hourglass_empty'
      }
    }

    // Get status text
    const getStatusText = (status: string): string => {
      switch (status) {
        case 'valid': return 'Listo'
        case 'invalid': return 'Error'
        case 'uploading': return 'Subiendo'
        case 'uploaded': return 'Subido'
        case 'failed': return 'Falló'
        default: return 'Pendiente'
      }
    }

    // Get file status class
    const getFileStatusClass = (fileData: FileToUpload): string => {
      return `status-${fileData.status}`
    }

    return {
      fileInput,
      files,
      isDragging,
      isUploading,
      currentStep,
      fullWindowsDestinationPath,
      destinationPathStatus,
      validFilesCount,
      invalidFilesCount,
      uploadedFilesCount,
      validFiles,
      triggerFileInput,
      handleFileSelect,
      handleDragOver,
      handleDragLeave,
      handleDrop,
      removeFile,
      clearAllFiles,
      handleClose,
      goToConfirmation,
      goBackToSelect,
      handleUploadAll,
      formatFileSize,
      getFileIcon,
      getStatusIcon,
      getStatusText,
      getFileStatusClass,
      getFullWindowsPath,
      getPathLengthClass
    }
  }
})
</script>

<style scoped>
/* Overlay */
.upload-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

/* Modal Container */
.upload-modal {
  background: white;
  border-radius: 12px;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.4);
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header */
.upload-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  background: linear-gradient(135deg, #1e40af, #1d4ed8);
  color: white;
}

.header-info h2 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 1.35rem;
  font-weight: 700;
}

.btn-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 8px;
  padding: 0.5rem;
  cursor: pointer;
  color: white;
  transition: background 0.2s;
}

.btn-close:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
}

.btn-close:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Destination Section */
.destination-section {
  background: #fef3c7;
  border-bottom: 1px solid #fbbf24;
  padding: 1rem 1.5rem;
}

.destination-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  color: #92400e;
  font-weight: 600;
}

.destination-header .material-icons {
  font-size: 1.25rem;
}

.destination-path {
  background: #fffbeb;
  border: 1px solid #fcd34d;
  border-radius: 6px;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
}

.destination-path code {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.85rem;
  color: #78350f;
  word-break: break-all;
}

.destination-chars {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
}

.destination-chars .material-icons {
  font-size: 1rem;
}

.destination-chars.safe {
  color: #059669;
}

.destination-chars.warning {
  color: #d97706;
}

.destination-chars.danger {
  color: #dc2626;
}

/* Content */
.upload-modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

/* Drop Zone */
.drop-zone {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #f9fafb;
  margin-bottom: 1.5rem;
}

.drop-zone:hover,
.drop-zone.is-dragging {
  border-color: #2563eb;
  background: #eff6ff;
}

.drop-zone.is-dragging {
  transform: scale(1.01);
}

.drop-icon {
  font-size: 3rem;
  color: #9ca3af;
  margin-bottom: 0.75rem;
}

.drop-zone:hover .drop-icon,
.drop-zone.is-dragging .drop-icon {
  color: #2563eb;
}

.drop-text {
  font-size: 1.1rem;
  color: #374151;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.drop-warning {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  color: #dc2626;
  font-size: 0.85rem;
  font-weight: 600;
}

.drop-warning .material-icons {
  font-size: 1rem;
}

.hidden-input {
  display: none;
}

/* Files Section */
.files-section {
  background: #f8fafc;
  border-radius: 10px;
  padding: 1rem;
}

.files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.files-header h3 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 1rem;
  color: #1f2937;
}

.btn-clear-all {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: #fee2e2;
  color: #dc2626;
  border: none;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-clear-all:hover:not(:disabled) {
  background: #fecaca;
}

/* Files List */
.files-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 300px;
  overflow-y: auto;
}

.file-item {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 0.875rem;
  transition: all 0.2s;
}

.file-item.status-valid {
  border-left: 4px solid #10b981;
}

.file-item.status-invalid {
  border-left: 4px solid #ef4444;
  background: #fef2f2;
}

.file-item.status-uploading {
  border-left: 4px solid #3b82f6;
  background: #eff6ff;
}

.file-item.status-uploaded {
  border-left: 4px solid #10b981;
  background: #ecfdf5;
}

.file-item.status-failed {
  border-left: 4px solid #ef4444;
  background: #fee2e2;
}

/* File Main Row */
.file-main {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.file-icon {
  color: #6b7280;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-name {
  margin: 0;
  font-weight: 600;
  color: #1f2937;
  font-size: 0.9rem;
  word-break: break-all;
}

.file-meta {
  display: flex;
  gap: 1rem;
  margin: 0.25rem 0 0;
  font-size: 0.75rem;
}

.file-size {
  color: #6b7280;
}

/* Barra de caracteres */
.chars-bar-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.35rem;
}

.chars-bar {
  flex: 1;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
  max-width: 120px;
}

.chars-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.chars-bar-fill.safe {
  background: linear-gradient(90deg, #10b981, #059669);
}

.chars-bar-fill.warning {
  background: linear-gradient(90deg, #f59e0b, #d97706);
}

.chars-bar-fill.danger {
  background: linear-gradient(90deg, #ef4444, #dc2626);
}

.chars-text {
  font-size: 0.7rem;
  font-weight: 600;
  white-space: nowrap;
}

.chars-text.safe {
  color: #059669;
}

.chars-text.warning {
  color: #d97706;
}

.chars-text.danger {
  color: #dc2626;
}

.file-path-length {
  font-weight: 600;
}

.file-path-length.safe {
  color: #059669;
}

.file-path-length.warning {
  color: #d97706;
}

.file-path-length.danger {
  color: #dc2626;
}

.file-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Status Badge */
.status-badge {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
}

.status-badge .material-icons {
  font-size: 0.85rem;
}

.status-badge.valid {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.invalid {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.uploading {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.uploading .material-icons {
  animation: spin 1s linear infinite;
}

.status-badge.uploaded {
  background: #10b981;
  color: white;
}

.status-badge.failed {
  background: #ef4444;
  color: white;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.btn-remove {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 0.2rem;
  display: flex;
  border-radius: 4px;
  transition: all 0.2s;
}

.btn-remove:hover:not(:disabled) {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

/* Validation Errors */
.validation-errors {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #fef2f2;
  border-radius: 4px;
}

.error-item {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  color: #991b1b;
  font-size: 0.75rem;
}

.error-item .material-icons {
  font-size: 0.9rem;
}

/* Path Preview */
.path-preview-container {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px dashed #e5e7eb;
}

.path-label {
  font-size: 0.7rem;
  color: #6b7280;
  margin-right: 0.5rem;
}

.path-preview {
  font-size: 0.65rem;
  color: #4b5563;
  word-break: break-all;
  font-family: 'Consolas', 'Monaco', monospace;
}

.path-preview.danger {
  color: #dc2626;
}

.path-preview.warning {
  color: #d97706;
}

/* Progress Container */
.progress-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.75rem;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #2563eb);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.8rem;
  font-weight: 700;
  color: #1e40af;
  min-width: 45px;
  text-align: right;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #9ca3af;
}

.empty-state .material-icons {
  font-size: 3.5rem;
  margin-bottom: 0.75rem;
}

.empty-state p {
  margin: 0;
  font-size: 1rem;
}

.empty-hint {
  font-size: 0.85rem !important;
  margin-top: 0.5rem !important;
}

/* Confirmation Box */
.confirmation-box {
  text-align: center;
  padding: 2rem;
}

.confirmation-icon {
  width: 70px;
  height: 70px;
  background: #dbeafe;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
}

.confirmation-icon .material-icons {
  font-size: 2.5rem;
  color: #2563eb;
}

.confirmation-box h3 {
  margin: 0 0 1rem;
  color: #1f2937;
  font-size: 1.35rem;
}

.confirmation-text {
  color: #4b5563;
  margin-bottom: 1rem;
}

.confirmation-destination {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  background: #fef3c7;
  border: 1px solid #fcd34d;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  text-align: left;
}

.confirmation-destination .material-icons {
  color: #92400e;
  flex-shrink: 0;
}

.confirmation-destination code {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.8rem;
  color: #78350f;
  word-break: break-all;
}

.confirmation-files-list {
  background: #f8fafc;
  border-radius: 8px;
  padding: 1rem;
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 1.5rem;
  text-align: left;
}

.confirmation-file {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e5e7eb;
}

.confirmation-file:last-child {
  border-bottom: none;
}

.confirmation-file .material-icons {
  color: #6b7280;
}

.confirmation-file-info {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.confirmation-file-name {
  font-size: 0.85rem;
  color: #1f2937;
  font-weight: 500;
}

.confirmation-file-size {
  font-size: 0.75rem;
  color: #6b7280;
}

.confirmation-warning {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: #eff6ff;
  border-radius: 6px;
  padding: 0.75rem;
  font-size: 0.85rem;
  color: #1e40af;
}

/* Footer */
.upload-modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.footer-info {
  display: flex;
  gap: 1rem;
}

.valid-count,
.invalid-count {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.85rem;
  font-weight: 600;
  margin: 0;
}

.valid-count {
  color: #059669;
}

.invalid-count {
  color: #dc2626;
}

.valid-count .material-icons,
.invalid-count .material-icons {
  font-size: 1rem;
}

.footer-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-cancel,
.btn-next,
.btn-back,
.btn-upload {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  font-size: 0.9rem;
}

.btn-cancel {
  background: #f3f4f6;
  color: #374151;
}

.btn-cancel:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn-back {
  background: #f3f4f6;
  color: #374151;
}

.btn-back:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn-next {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: white;
}

.btn-next:hover:not(:disabled) {
  background: linear-gradient(135deg, #1d4ed8, #1e40af);
}

.btn-upload {
  background: linear-gradient(135deg, #059669, #047857);
  color: white;
}

.btn-upload:hover:not(:disabled) {
  background: linear-gradient(135deg, #047857, #065f46);
}

.btn-cancel:disabled,
.btn-next:disabled,
.btn-back:disabled,
.btn-upload:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

/* Responsive */
@media (max-width: 640px) {
  .upload-modal {
    max-height: 100vh;
    border-radius: 0;
  }

  .upload-modal-footer {
    flex-direction: column;
    gap: 1rem;
  }

  .footer-actions {
    width: 100%;
  }

  .btn-cancel,
  .btn-next,
  .btn-back,
  .btn-upload {
    flex: 1;
    justify-content: center;
  }
}
</style>
