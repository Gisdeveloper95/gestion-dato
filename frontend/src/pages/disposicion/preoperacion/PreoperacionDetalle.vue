<template>
  <div class="preoperacion-detalle-page">
    <!-- Header -->
    <header class="page-header">
      <div class="header-content">
        <button @click="goBack" class="btn-back">
          <i class="material-icons">arrow_back</i>
          Volver
        </button>
        <div class="header-info">
          <h1>Pre-Operación - {{ municipioName }}</h1>
          <div class="header-badges">
            <span class="badge-departamento">{{ departamentoName }}</span>
            <span class="badge-territorial">{{ territorialName }}</span>
          </div>
        </div>
        <div class="header-actions">
          <button @click="expandAll" class="btn-action" title="Expandir todo">
            <i class="material-icons">unfold_more</i>
          </button>
          <button @click="collapseAll" class="btn-action" title="Colapsar todo">
            <i class="material-icons">unfold_less</i>
          </button>
          <button @click="refreshData" class="btn-action" :disabled="loading" title="Actualizar">
            <i class="material-icons">refresh</i>
          </button>
        </div>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <span>Cargando estructura de directorios...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <i class="material-icons">error</i>
      <p>{{ error }}</p>
      <button @click="refreshData" class="btn-retry">Reintentar</button>
    </div>

    <!-- Main Content -->
    <main v-else class="main-content">
      <!-- Stats Bar -->
      <div class="stats-bar">
        <div class="stat-item">
          <i class="material-icons">folder</i>
          <span>{{ totalDirectorios }} directorios</span>
        </div>
        <div class="stat-item">
          <i class="material-icons">description</i>
          <span>{{ totalArchivos }} archivos</span>
        </div>
        <div class="stat-info">
          <i class="material-icons">info</i>
          <span>Click en icono <i class="material-icons" style="font-size: 16px; vertical-align: middle;">download</i> para descargar carpeta</span>
        </div>
      </div>

      <!-- Filtro de mecanismo activo -->
      <div v-if="mecanismoFromUrl" class="mecanismo-filter-banner">
        <i class="material-icons">filter_alt</i>
        <span>Filtrando por fuente: <strong>{{ mecanismoFromUrl }}</strong></span>
        <button @click="clearMecanismoFilter()" class="btn-clear-mecanismo">
          <i class="material-icons">close</i>
          Ver todos
        </button>
      </div>

      <!-- Search Bar -->
      <div class="search-bar">
        <div class="search-box">
          <i class="material-icons">search</i>
          <input
            v-model="searchTerm"
            placeholder="Buscar archivo o directorio..."
            @input="onSearch"
          />
          <button v-if="searchTerm" @click="clearSearch" class="clear-btn">
            <i class="material-icons">close</i>
          </button>
        </div>
        <div v-if="searchTerm && searchResults.length > 0" class="search-results-info">
          {{ searchResults.length }} resultados encontrados
        </div>
      </div>

      <!-- Tree Container -->
      <div class="tree-container">
        <div v-if="displayData.length === 0" class="empty-state">
          <i class="material-icons">folder_off</i>
          <p v-if="mensajeBackend">{{ mensajeBackend }}</p>
          <p v-else>No se encontraron directorios de pre-operación</p>
          <p v-if="rutaBuscada" class="ruta-info">
            <small>Ruta: {{ linuxToWindowsPath(rutaBuscada) }}</small>
          </p>
        </div>

        <div v-else class="tree-view">
          <!-- Nivel 0 -->
          <div v-for="n0 in displayData" :key="n0.id" class="tree-node nivel-0">
            <!-- Archivo nivel 0 -->
            <div v-if="n0.tipo === 'archivo'"
                 class="node-header is-file"
                 :class="{ 'is-highlighted': isHighlighted(n0) }"
                 @click="openFileModal(n0)">
              <span class="expand-placeholder"></span>
              <i class="material-icons file-icon">{{ getFileIcon(n0.extension) }}</i>
              <span class="node-name">{{ n0.nombre }}</span>
              <span v-if="n0.tamano_legible" class="file-size">{{ n0.tamano_legible }}</span>
              <span v-if="n0.extension" class="extension-badge">{{ n0.extension }}</span>
            </div>
            <!-- Directorio nivel 0 -->
            <template v-else>
              <div class="node-header"
                   :class="{ 'is-expanded': expanded[n0.id], 'is-highlighted': isHighlighted(n0) }"
                   @click="toggle(n0.id)">
                <span class="expand-icon">
                  <i class="material-icons">{{ expanded[n0.id] ? 'expand_more' : 'chevron_right' }}</i>
                </span>
                <i class="material-icons folder-icon">{{ expanded[n0.id] ? 'folder_open' : 'folder' }}</i>
                <span class="node-name">{{ n0.nombre }}</span>
                <span v-if="n0.archivos_count" class="file-count">({{ n0.archivos_count }})</span>
                <button @click.stop="downloadDirectory(n0)" class="btn-download-dir" :disabled="downloadingDir === n0.id" title="Descargar directorio como ZIP">
                  <i class="material-icons">{{ downloadingDir === n0.id ? 'hourglass_empty' : 'download' }}</i>
                </button>
              </div>
              <!-- Nivel 1 -->
              <div v-if="expanded[n0.id] && n0.hijos" class="children">
                <div v-for="n1 in n0.hijos" :key="n1.id" class="tree-node nivel-1">
                  <div v-if="n1.tipo === 'archivo'" class="node-header is-file" :class="{ 'is-highlighted': isHighlighted(n1) }" @click="openFileModal(n1)">
                    <span class="expand-placeholder"></span>
                    <i class="material-icons file-icon">{{ getFileIcon(n1.extension) }}</i>
                    <span class="node-name">{{ n1.nombre }}</span>
                    <span v-if="n1.tamano_legible" class="file-size">{{ n1.tamano_legible }}</span>
                    <span v-if="n1.extension" class="extension-badge">{{ n1.extension }}</span>
                  </div>
                  <template v-else>
                    <div class="node-header" :class="{ 'is-expanded': expanded[n1.id], 'is-highlighted': isHighlighted(n1) }" @click="toggle(n1.id)">
                      <span class="expand-icon"><i class="material-icons">{{ expanded[n1.id] ? 'expand_more' : 'chevron_right' }}</i></span>
                      <i class="material-icons folder-icon">{{ expanded[n1.id] ? 'folder_open' : 'folder' }}</i>
                      <span class="node-name">{{ n1.nombre }}</span>
                      <span v-if="n1.archivos_count" class="file-count">({{ n1.archivos_count }})</span>
                      <button @click.stop="downloadDirectory(n1)" class="btn-download-dir" :disabled="downloadingDir === n1.id" title="Descargar directorio como ZIP">
                        <i class="material-icons">{{ downloadingDir === n1.id ? 'hourglass_empty' : 'download' }}</i>
                      </button>
                    </div>
                    <!-- Nivel 2 -->
                    <div v-if="expanded[n1.id] && n1.hijos" class="children">
                      <div v-for="n2 in n1.hijos" :key="n2.id" class="tree-node nivel-2">
                        <div v-if="n2.tipo === 'archivo'" class="node-header is-file" :class="{ 'is-highlighted': isHighlighted(n2) }" @click="openFileModal(n2)">
                          <span class="expand-placeholder"></span>
                          <i class="material-icons file-icon">{{ getFileIcon(n2.extension) }}</i>
                          <span class="node-name">{{ n2.nombre }}</span>
                          <span v-if="n2.tamano_legible" class="file-size">{{ n2.tamano_legible }}</span>
                          <span v-if="n2.extension" class="extension-badge">{{ n2.extension }}</span>
                        </div>
                        <template v-else>
                          <div class="node-header" :class="{ 'is-expanded': expanded[n2.id], 'is-highlighted': isHighlighted(n2) }" @click="toggle(n2.id)">
                            <span class="expand-icon"><i class="material-icons">{{ expanded[n2.id] ? 'expand_more' : 'chevron_right' }}</i></span>
                            <i class="material-icons folder-icon">{{ expanded[n2.id] ? 'folder_open' : 'folder' }}</i>
                            <span class="node-name">{{ n2.nombre }}</span>
                            <span v-if="n2.archivos_count" class="file-count">({{ n2.archivos_count }})</span>
                            <button @click.stop="downloadDirectory(n2)" class="btn-download-dir" :disabled="downloadingDir === n2.id" title="Descargar directorio como ZIP">
                              <i class="material-icons">{{ downloadingDir === n2.id ? 'hourglass_empty' : 'download' }}</i>
                            </button>
                          </div>
                          <!-- Nivel 3 -->
                          <div v-if="expanded[n2.id] && n2.hijos" class="children">
                            <div v-for="n3 in n2.hijos" :key="n3.id" class="tree-node nivel-3">
                              <div v-if="n3.tipo === 'archivo'" class="node-header is-file" :class="{ 'is-highlighted': isHighlighted(n3) }" @click="openFileModal(n3)">
                                <span class="expand-placeholder"></span>
                                <i class="material-icons file-icon">{{ getFileIcon(n3.extension) }}</i>
                                <span class="node-name">{{ n3.nombre }}</span>
                                <span v-if="n3.tamano_legible" class="file-size">{{ n3.tamano_legible }}</span>
                                <span v-if="n3.extension" class="extension-badge">{{ n3.extension }}</span>
                              </div>
                              <template v-else>
                                <div class="node-header" :class="{ 'is-expanded': expanded[n3.id], 'is-highlighted': isHighlighted(n3) }" @click="toggle(n3.id)">
                                  <span class="expand-icon"><i class="material-icons">{{ expanded[n3.id] ? 'expand_more' : 'chevron_right' }}</i></span>
                                  <i class="material-icons folder-icon">{{ expanded[n3.id] ? 'folder_open' : 'folder' }}</i>
                                  <span class="node-name">{{ n3.nombre }}</span>
                                  <span v-if="n3.archivos_count" class="file-count">({{ n3.archivos_count }})</span>
                                  <button @click.stop="downloadDirectory(n3)" class="btn-download-dir" :disabled="downloadingDir === n3.id" title="Descargar directorio como ZIP">
                                    <i class="material-icons">{{ downloadingDir === n3.id ? 'hourglass_empty' : 'download' }}</i>
                                  </button>
                                </div>
                                <!-- Nivel 4 -->
                                <div v-if="expanded[n3.id] && n3.hijos" class="children">
                                  <div v-for="n4 in n3.hijos" :key="n4.id" class="tree-node nivel-4">
                                    <div v-if="n4.tipo === 'archivo'" class="node-header is-file" :class="{ 'is-highlighted': isHighlighted(n4) }" @click="openFileModal(n4)">
                                      <span class="expand-placeholder"></span>
                                      <i class="material-icons file-icon">{{ getFileIcon(n4.extension) }}</i>
                                      <span class="node-name">{{ n4.nombre }}</span>
                                      <span v-if="n4.tamano_legible" class="file-size">{{ n4.tamano_legible }}</span>
                                      <span v-if="n4.extension" class="extension-badge">{{ n4.extension }}</span>
                                    </div>
                                    <template v-else>
                                      <div class="node-header" :class="{ 'is-expanded': expanded[n4.id], 'is-highlighted': isHighlighted(n4) }" @click="toggle(n4.id)">
                                        <span class="expand-icon"><i class="material-icons">{{ expanded[n4.id] ? 'expand_more' : 'chevron_right' }}</i></span>
                                        <i class="material-icons folder-icon">{{ expanded[n4.id] ? 'folder_open' : 'folder' }}</i>
                                        <span class="node-name">{{ n4.nombre }}</span>
                                        <span v-if="n4.archivos_count" class="file-count">({{ n4.archivos_count }})</span>
                                        <button @click.stop="downloadDirectory(n4)" class="btn-download-dir" :disabled="downloadingDir === n4.id" title="Descargar directorio como ZIP">
                                          <i class="material-icons">{{ downloadingDir === n4.id ? 'hourglass_empty' : 'download' }}</i>
                                        </button>
                                      </div>
                                      <!-- Nivel 5 -->
                                      <div v-if="expanded[n4.id] && n4.hijos" class="children">
                                        <div v-for="n5 in n4.hijos" :key="n5.id" class="tree-node nivel-5">
                                          <div v-if="n5.tipo === 'archivo'" class="node-header is-file" :class="{ 'is-highlighted': isHighlighted(n5) }" @click="openFileModal(n5)">
                                            <span class="expand-placeholder"></span>
                                            <i class="material-icons file-icon">{{ getFileIcon(n5.extension) }}</i>
                                            <span class="node-name">{{ n5.nombre }}</span>
                                            <span v-if="n5.tamano_legible" class="file-size">{{ n5.tamano_legible }}</span>
                                            <span v-if="n5.extension" class="extension-badge">{{ n5.extension }}</span>
                                          </div>
                                          <template v-else>
                                            <div class="node-header" :class="{ 'is-expanded': expanded[n5.id], 'is-highlighted': isHighlighted(n5) }" @click="toggle(n5.id)">
                                              <span class="expand-icon"><i class="material-icons">{{ expanded[n5.id] ? 'expand_more' : 'chevron_right' }}</i></span>
                                              <i class="material-icons folder-icon">{{ expanded[n5.id] ? 'folder_open' : 'folder' }}</i>
                                              <span class="node-name">{{ n5.nombre }}</span>
                                              <span v-if="n5.archivos_count" class="file-count">({{ n5.archivos_count }})</span>
                                              <button @click.stop="downloadDirectory(n5)" class="btn-download-dir" :disabled="downloadingDir === n5.id" title="Descargar directorio como ZIP">
                                                <i class="material-icons">{{ downloadingDir === n5.id ? 'hourglass_empty' : 'download' }}</i>
                                              </button>
                                            </div>
                                            <!-- Nivel 6 -->
                                            <div v-if="expanded[n5.id] && n5.hijos" class="children">
                                              <div v-for="n6 in n5.hijos" :key="n6.id" class="tree-node nivel-6">
                                                <div v-if="n6.tipo === 'archivo'" class="node-header is-file" :class="{ 'is-highlighted': isHighlighted(n6) }" @click="openFileModal(n6)">
                                                  <span class="expand-placeholder"></span>
                                                  <i class="material-icons file-icon">{{ getFileIcon(n6.extension) }}</i>
                                                  <span class="node-name">{{ n6.nombre }}</span>
                                                  <span v-if="n6.tamano_legible" class="file-size">{{ n6.tamano_legible }}</span>
                                                  <span v-if="n6.extension" class="extension-badge">{{ n6.extension }}</span>
                                                </div>
                                                <template v-else>
                                                  <div class="node-header" :class="{ 'is-expanded': expanded[n6.id], 'is-highlighted': isHighlighted(n6) }" @click="toggle(n6.id)">
                                                    <span class="expand-icon"><i class="material-icons">{{ expanded[n6.id] ? 'expand_more' : 'chevron_right' }}</i></span>
                                                    <i class="material-icons folder-icon">{{ expanded[n6.id] ? 'folder_open' : 'folder' }}</i>
                                                    <span class="node-name">{{ n6.nombre }}</span>
                                                    <span v-if="n6.archivos_count" class="file-count">({{ n6.archivos_count }})</span>
                                                    <button @click.stop="downloadDirectory(n6)" class="btn-download-dir" :disabled="downloadingDir === n6.id" title="Descargar directorio como ZIP">
                                                      <i class="material-icons">{{ downloadingDir === n6.id ? 'hourglass_empty' : 'download' }}</i>
                                                    </button>
                                                  </div>
                                                  <!-- Nivel 7 -->
                                                  <div v-if="expanded[n6.id] && n6.hijos" class="children">
                                                    <div v-for="n7 in n6.hijos" :key="n7.id" class="tree-node nivel-7">
                                                      <div v-if="n7.tipo === 'archivo'" class="node-header is-file" :class="{ 'is-highlighted': isHighlighted(n7) }" @click="openFileModal(n7)">
                                                        <span class="expand-placeholder"></span>
                                                        <i class="material-icons file-icon">{{ getFileIcon(n7.extension) }}</i>
                                                        <span class="node-name">{{ n7.nombre }}</span>
                                                        <span v-if="n7.tamano_legible" class="file-size">{{ n7.tamano_legible }}</span>
                                                        <span v-if="n7.extension" class="extension-badge">{{ n7.extension }}</span>
                                                      </div>
                                                      <template v-else>
                                                        <div class="node-header" :class="{ 'is-expanded': expanded[n7.id], 'is-highlighted': isHighlighted(n7) }" @click="toggle(n7.id)">
                                                          <span class="expand-icon"><i class="material-icons">{{ expanded[n7.id] ? 'expand_more' : 'chevron_right' }}</i></span>
                                                          <i class="material-icons folder-icon">{{ expanded[n7.id] ? 'folder_open' : 'folder' }}</i>
                                                          <span class="node-name">{{ n7.nombre }}</span>
                                                          <span v-if="n7.archivos_count" class="file-count">({{ n7.archivos_count }})</span>
                                                          <button @click.stop="downloadDirectory(n7)" class="btn-download-dir" :disabled="downloadingDir === n7.id" title="Descargar directorio como ZIP">
                                                            <i class="material-icons">{{ downloadingDir === n7.id ? 'hourglass_empty' : 'download' }}</i>
                                                          </button>
                                                        </div>
                                                        <!-- Nivel 8+ (archivos solamente) -->
                                                        <div v-if="expanded[n7.id] && n7.hijos" class="children">
                                                          <div v-for="n8 in n7.hijos" :key="n8.id" class="tree-node nivel-8">
                                                            <div v-if="n8.tipo === 'archivo'" class="node-header is-file" :class="{ 'is-highlighted': isHighlighted(n8) }" @click="openFileModal(n8)">
                                                              <span class="expand-placeholder"></span>
                                                              <i class="material-icons file-icon">{{ getFileIcon(n8.extension) }}</i>
                                                              <span class="node-name">{{ n8.nombre }}</span>
                                                              <span v-if="n8.tamano_legible" class="file-size">{{ n8.tamano_legible }}</span>
                                                              <span v-if="n8.extension" class="extension-badge">{{ n8.extension }}</span>
                                                            </div>
                                                            <template v-else>
                                                              <div class="node-header" :class="{ 'is-expanded': expanded[n8.id], 'is-highlighted': isHighlighted(n8) }" @click="toggle(n8.id)">
                                                                <span class="expand-icon"><i class="material-icons">{{ expanded[n8.id] ? 'expand_more' : 'chevron_right' }}</i></span>
                                                                <i class="material-icons folder-icon">{{ expanded[n8.id] ? 'folder_open' : 'folder' }}</i>
                                                                <span class="node-name">{{ n8.nombre }}</span>
                                                                <span v-if="n8.archivos_count" class="file-count">({{ n8.archivos_count }})</span>
                                                                <button @click.stop="downloadDirectory(n8)" class="btn-download-dir" :disabled="downloadingDir === n8.id" title="Descargar directorio como ZIP">
                                                                  <i class="material-icons">{{ downloadingDir === n8.id ? 'hourglass_empty' : 'download' }}</i>
                                                                </button>
                                                              </div>
                                                              <!-- Nivel 9+ -->
                                                              <div v-if="expanded[n8.id] && n8.hijos" class="children">
                                                                <div v-for="n9 in n8.hijos" :key="n9.id" class="tree-node nivel-9">
                                                                  <div v-if="n9.tipo === 'archivo'" class="node-header is-file" @click="openFileModal(n9)">
                                                                    <span class="expand-placeholder"></span>
                                                                    <i class="material-icons file-icon">{{ getFileIcon(n9.extension) }}</i>
                                                                    <span class="node-name">{{ n9.nombre }}</span>
                                                                    <span v-if="n9.tamano_legible" class="file-size">{{ n9.tamano_legible }}</span>
                                                                  </div>
                                                                  <div v-else class="node-header" :class="{ 'is-expanded': expanded[n9.id] }" @click="toggle(n9.id)">
                                                                    <span class="expand-icon"><i class="material-icons">{{ expanded[n9.id] ? 'expand_more' : 'chevron_right' }}</i></span>
                                                                    <i class="material-icons folder-icon">{{ expanded[n9.id] ? 'folder_open' : 'folder' }}</i>
                                                                    <span class="node-name">{{ n9.nombre }}</span>
                                                                    <span v-if="n9.archivos_count" class="file-count">({{ n9.archivos_count }})</span>
                                                                    <button @click.stop="downloadDirectory(n9)" class="btn-download-dir" :disabled="downloadingDir === n9.id" title="Descargar directorio como ZIP">
                                                                      <i class="material-icons">{{ downloadingDir === n9.id ? 'hourglass_empty' : 'download' }}</i>
                                                                    </button>
                                                                  </div>
                                                                </div>
                                                              </div>
                                                            </template>
                                                          </div>
                                                        </div>
                                                      </template>
                                                    </div>
                                                  </div>
                                                </template>
                                              </div>
                                            </div>
                                          </template>
                                        </div>
                                      </div>
                                    </template>
                                  </div>
                                </div>
                              </template>
                            </div>
                          </div>
                        </template>
                      </div>
                    </div>
                  </template>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </main>

    <!-- File Modal -->
    <div v-if="showFileModal" class="modal-overlay" @click.self="closeFileModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>
            <i class="material-icons">{{ getFileIcon(selectedFile?.extension) }}</i>
            {{ selectedFile?.nombre }}
          </h3>
          <button @click="closeFileModal" class="close-btn">
            <i class="material-icons">close</i>
          </button>
        </div>

        <div class="modal-body">
          <div class="detail-grid">
            <div class="detail-item">
              <label>Tipo:</label>
              <span>Archivo</span>
            </div>

            <div class="detail-item">
              <label>Extensión:</label>
              <span class="extension-badge large">{{ selectedFile?.extension || 'N/A' }}</span>
            </div>

            <div class="detail-item">
              <label>Tamaño:</label>
              <span>{{ selectedFile?.tamano_legible || 'N/A' }}</span>
            </div>

            <div class="detail-item">
              <label>Fecha modificación:</label>
              <span>{{ formatDate(selectedFile?.fecha_modificacion) }}</span>
            </div>

            <div class="detail-item full-width">
              <label>Ruta:</label>
              <div class="path-container">
                <code>{{ linuxToWindowsPath(selectedFile?.ruta_absoluta || selectedFile?.ruta_relativa) }}</code>
                <button @click="copyPath" class="copy-btn" title="Copiar ruta">
                  <i class="material-icons">{{ copied ? 'check' : 'content_copy' }}</i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="previewFile" class="btn-preview" :disabled="!canPreview">
            <i class="material-icons">visibility</i>
            Vista previa
          </button>
          <button @click="downloadFile" class="btn-download">
            <i class="material-icons">download</i>
            Descargar
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { API_URL } from '@/api/config'

// Router
const route = useRoute()
const router = useRouter()

// Estado
const loading = ref(true)
const error = ref<string | null>(null)
const municipioData = ref<any>(null)
const arbolData = ref<any[]>([])
const mensajeBackend = ref<string | null>(null)  // Mensaje informativo del backend
const rutaBuscada = ref<string | null>(null)     // Ruta que se intentó buscar
const expanded = ref<Record<string, boolean>>({})
const searchTerm = ref('')
const searchResults = ref<any[]>([])

// Filtro de mecanismo desde URL
const mecanismoFromUrl = ref('')

// Modal de archivo
const showFileModal = ref(false)
const selectedFile = ref<any>(null)
const copied = ref(false)

// Descarga de directorio
const downloadingDir = ref<string | null>(null)

// Computed
const municipioName = computed(() => municipioData.value?.nom_municipio || 'Cargando...')
const departamentoName = computed(() => municipioData.value?.nom_depto || '')
const territorialName = computed(() => municipioData.value?.nom_territorial || '')

const displayData = computed(() => {
  return arbolData.value
})

const totalDirectorios = computed(() => {
  let count = 0
  const countDirs = (nodes: any[]) => {
    for (const node of nodes) {
      if (node.tipo !== 'archivo') count++
      if (node.hijos) countDirs(node.hijos)
    }
  }
  countDirs(displayData.value)
  return count
})

const totalArchivos = computed(() => {
  let count = 0
  const countFiles = (nodes: any[]) => {
    for (const node of nodes) {
      if (node.tipo === 'archivo') count++
      if (node.hijos) countFiles(node.hijos)
    }
  }
  countFiles(displayData.value)
  return count
})

const canPreview = computed(() => {
  const ext = selectedFile.value?.extension?.toLowerCase()
  return ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'].includes(ext || '')
})

// ============================================
// UTILIDAD: Convertir ruta Linux a Windows
// ============================================
const linuxToWindowsPath = (linuxPath: string | null | undefined): string => {
  if (!linuxPath) return 'N/A'

  // Si ya es ruta Windows, devolverla
  if (linuxPath.startsWith('\\\\') || linuxPath.includes(':\\')) {
    return linuxPath
  }

  // Convertir /mnt/repositorio/... a \\repositorio\DirGesCat\...
  let windowsPath = linuxPath

  // Patrón: /mnt/repositorio/ -> \\repositorio\DirGesCat\
  if (windowsPath.startsWith('/mnt/repositorio/')) {
    windowsPath = '\\\\repositorio\\DirGesCat\\' + windowsPath.substring('/mnt/repositorio/'.length)
  } else if (windowsPath.startsWith('/mnt/repositorio')) {
    windowsPath = '\\\\repositorio\\DirGesCat' + windowsPath.substring('/mnt/repositorio'.length)
  }

  // Convertir / a \
  windowsPath = windowsPath.replace(/\//g, '\\')

  return windowsPath
}

// Methods
const goBack = () => {
  // Usar historial del navegador para regresar
  if (window.history.length > 1) {
    router.back()
  } else {
    // Fallback si no hay historial
    router.push('/disposicion/preoperacion')
  }
}

const loadData = async () => {
  const codMpio = route.params.id
  if (!codMpio) {
    error.value = 'Código de municipio no proporcionado'
    loading.value = false
    return
  }

  try {
    loading.value = true
    error.value = null
    mensajeBackend.value = null
    rutaBuscada.value = null

    // Leer mecanismo desde URL query param ANTES de la llamada API
    const mecanismoQuery = route.query.mecanismo as string | undefined
    if (mecanismoQuery) {
      mecanismoFromUrl.value = mecanismoQuery
    }

    const params: Record<string, any> = { cod_mpio: codMpio }
    if (mecanismoFromUrl.value) {
      params.mecanismo = mecanismoFromUrl.value
    }

    const response = await api.get('/preoperacion/preoperacion-arbol/arbol_realtime/', {
      params
    })

    municipioData.value = {
      cod_municipio: response.cod_mpio,
      nom_municipio: response.nom_municipio || route.query.nombre || `Municipio ${codMpio}`,
      nom_depto: response.nom_depto || route.query.depto || '',
      nom_territorial: route.query.territorial || '',
      ruta_base: response.ruta_base || ''
    }

    arbolData.value = response.estructura || []

    // Guardar mensaje informativo del backend (si lo hay)
    if (response.mensaje) {
      mensajeBackend.value = response.mensaje
    }
    if (response.ruta_buscada) {
      rutaBuscada.value = response.ruta_buscada
    }

    // Expandir primer nivel por defecto
    arbolData.value.forEach((node: any) => {
      expanded.value[node.id] = true
    })

  } catch (err: any) {
    console.error('Error cargando datos:', err)
    error.value = err.response?.data?.error || err.message || 'Error al cargar datos'
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadData()
}

const clearMecanismoFilter = () => {
  mecanismoFromUrl.value = ''
  loadData()
}

const toggle = (id: string) => {
  expanded.value[id] = !expanded.value[id]
}

const expandAll = () => {
  const expandNodes = (nodes: any[]) => {
    for (const node of nodes) {
      if (node.tipo !== 'archivo') {
        expanded.value[node.id] = true
      }
      if (node.hijos) expandNodes(node.hijos)
    }
  }
  expandNodes(arbolData.value)
}

const collapseAll = () => {
  expanded.value = {}
}

const onSearch = () => {
  if (!searchTerm.value.trim()) {
    searchResults.value = []
    return
  }

  const term = searchTerm.value.toLowerCase()
  const results: any[] = []

  const searchNodes = (nodes: any[], path: string[] = []) => {
    for (const node of nodes) {
      if (node.nombre.toLowerCase().includes(term)) {
        results.push({ ...node, path })
        path.forEach((id) => {
          expanded.value[id] = true
        })
      }
      if (node.hijos) {
        searchNodes(node.hijos, [...path, node.id])
      }
    }
  }

  searchNodes(arbolData.value)
  searchResults.value = results
}

const clearSearch = () => {
  searchTerm.value = ''
  searchResults.value = []
}

const isHighlighted = (node: any) => {
  if (!searchTerm.value) return false
  return node.nombre.toLowerCase().includes(searchTerm.value.toLowerCase())
}

const getFileIcon = (extension?: string) => {
  const ext = extension?.toLowerCase()
  if (['.pdf'].includes(ext || '')) return 'picture_as_pdf'
  if (['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tif', '.tiff'].includes(ext || '')) return 'image'
  if (['.doc', '.docx'].includes(ext || '')) return 'article'
  if (['.xls', '.xlsx'].includes(ext || '')) return 'table_chart'
  if (['.zip', '.rar', '.7z'].includes(ext || '')) return 'folder_zip'
  if (['.shp', '.dbf', '.shx', '.prj', '.cpg', '.sbn', '.sbx'].includes(ext || '')) return 'map'
  if (['.dwg', '.dxf'].includes(ext || '')) return 'architecture'
  if (['.gdb', '.mdb', '.geodatabase'].includes(ext || '')) return 'storage'
  if (['.txt', '.csv', '.log'].includes(ext || '')) return 'text_snippet'
  if (['.xml', '.json', '.html', '.htm'].includes(ext || '')) return 'code'
  return 'description'
}

const openFileModal = (file: any) => {
  selectedFile.value = file
  showFileModal.value = true
  copied.value = false
}

const closeFileModal = () => {
  showFileModal.value = false
  selectedFile.value = null
}

const copyPath = async () => {
  const rutaOriginal = selectedFile.value?.ruta_absoluta || selectedFile.value?.ruta_relativa
  if (rutaOriginal) {
    try {
      const rutaWindows = linuxToWindowsPath(rutaOriginal)
      await navigator.clipboard.writeText(rutaWindows)
      copied.value = true
      setTimeout(() => { copied.value = false }, 2000)
    } catch (err) {
      console.error('Error copiando:', err)
    }
  }
}

const formatDate = (date?: string) => {
  if (!date) return 'N/A'
  try {
    return new Date(date).toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return date
  }
}

const previewFile = () => {
  const rutaAbsoluta = selectedFile.value?.ruta_absoluta
  if (!rutaAbsoluta) return

  const ext = selectedFile.value?.extension?.toLowerCase()
  const token = localStorage.getItem('token')

  // Para PDFs e imágenes, abrir en nueva pestaña usando fetch + blob
  if (['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.webp'].includes(ext || '')) {
    openFileInNewTab(rutaAbsoluta, token)
  } else {
    // Para otros archivos, descargar directamente
    downloadFile()
  }
  showFileModal.value = false
}

const openFileInNewTab = async (ruta: string, token: string | null) => {
  try {
    const url = `${API_URL}/preoperacion/ver_pdf/?ruta=${encodeURIComponent(ruta)}`
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Token ${token}`
      }
    })

    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`)
    }

    const blob = await response.blob()
    const blobUrl = window.URL.createObjectURL(blob)
    window.open(blobUrl, '_blank')

    // Limpiar URL después de un tiempo
    setTimeout(() => window.URL.revokeObjectURL(blobUrl), 60000)
  } catch (error: any) {
    console.error('Error abriendo archivo:', error)
    alert(`Error al abrir archivo: ${error.message}`)
  }
}

const downloadFile = () => {
  const rutaAbsoluta = selectedFile.value?.ruta_absoluta
  if (!rutaAbsoluta) return

  const token = localStorage.getItem('token')
  const ext = selectedFile.value?.extension?.toLowerCase() || ''

  // Usar endpoint ver_pdf para PDF, descargar_archivo para otros
  let downloadUrl: string
  if (ext === '.pdf') {
    downloadUrl = `${API_URL}/preoperacion/ver_pdf/?ruta=${encodeURIComponent(rutaAbsoluta)}&download=true&token=${token}`
  } else {
    downloadUrl = `${API_URL}/preoperacion/descargar_archivo/?ruta=${encodeURIComponent(rutaAbsoluta)}&token=${token}`
  }

  console.log(`Descargando: ${selectedFile.value?.nombre} desde ${downloadUrl}`)
  window.open(downloadUrl, '_blank')
  showFileModal.value = false
}

// ============================================
// DESCARGA DE DIRECTORIO - Usa window.open para barra de descarga del navegador
// ============================================
const downloadDirectory = (node: any) => {
  if (!node.ruta_absoluta) {
    alert('No se puede descargar este directorio')
    return
  }

  const token = localStorage.getItem('token')
  const downloadUrl = `${API_URL}/preoperacion/descargar_directorio/?ruta=${encodeURIComponent(node.ruta_absoluta)}&token=${token}`

  console.log(`Descargando directorio: ${node.nombre}...`)
  window.open(downloadUrl, '_blank')
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.preoperacion-detalle-page {
  min-height: 100vh;
  background: #f5f7fa;
}

/* Header */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background 0.2s;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.3);
}

.header-info {
  flex: 1;
}

.header-info h1 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.header-badges {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.badge-departamento,
.badge-territorial {
  padding: 0.25rem 0.75rem;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  font-size: 0.75rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-action {
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-action:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Loading & Error */
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  gap: 1rem;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e0e0e0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-container i {
  font-size: 48px;
  color: #dc3545;
}

.btn-retry {
  padding: 0.5rem 1.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

/* Main Content */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem;
}

/* Stats Bar */
.stats-bar {
  display: flex;
  gap: 2rem;
  padding: 1rem 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #666;
  font-size: 0.875rem;
}

.stat-item i {
  color: #667eea;
}

/* Search Bar */
.search-bar {
  margin-bottom: 1rem;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.search-box i {
  color: #999;
}

.search-box input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 0.9375rem;
}

.clear-btn {
  padding: 0.25rem;
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
}

.search-results-info {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #667eea;
  font-weight: 500;
}

/* Tree Container */
.tree-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.tree-view {
  padding: 1rem;
  max-height: calc(100vh - 300px);
  overflow-y: auto;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: #999;
}

.empty-state i {
  font-size: 64px;
  margin-bottom: 1rem;
}

/* Tree Node */
.tree-node {
  margin: 2px 0;
}

.children {
  margin-left: 24px;
  padding-left: 12px;
  border-left: 1px dashed #e0e0e0;
}

.node-header {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.node-header:hover {
  background: #f0f4ff;
}

.node-header.is-expanded {
  background: #f8f9ff;
}

.node-header.is-file:hover {
  background: #fff8f0;
}

.node-header.is-highlighted {
  background: #fff3cd !important;
  border: 1px solid #ffc107;
}

.expand-icon,
.expand-placeholder {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.expand-icon i {
  font-size: 20px;
  color: #666;
}

.folder-icon {
  font-size: 22px;
  color: #ffc107;
}

.file-icon {
  font-size: 20px;
  color: #666;
}

.node-name {
  flex: 1;
  font-size: 0.9rem;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-count {
  font-size: 0.75rem;
  color: #888;
  margin-left: 0.5rem;
}

.file-size {
  font-size: 0.75rem;
  color: #666;
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 4px;
}

.extension-badge {
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  padding: 2px 6px;
  border-radius: 4px;
  background: #e3f2fd;
  color: #1565c0;
}

/* Color por nivel */
.nivel-0 > .node-header .folder-icon { color: #1a73e8; }
.nivel-1 > .node-header .folder-icon { color: #34a853; }
.nivel-2 > .node-header .folder-icon { color: #fbbc04; }
.nivel-3 > .node-header .folder-icon { color: #ea4335; }
.nivel-4 > .node-header .folder-icon { color: #9c27b0; }
.nivel-5 > .node-header .folder-icon { color: #00bcd4; }
.nivel-6 > .node-header .folder-icon { color: #ff5722; }
.nivel-7 > .node-header .folder-icon { color: #607d8b; }
.nivel-8 > .node-header .folder-icon { color: #795548; }
.nivel-9 > .node-header .folder-icon { color: #e91e63; }

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.modal-header h3 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 1.125rem;
}

.close-btn {
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-item label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
}

.detail-item span,
.detail-item code {
  font-size: 0.9375rem;
  color: #333;
}

.path-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f5f5f5;
  padding: 0.75rem;
  border-radius: 8px;
  margin-top: 0.25rem;
}

.path-container code {
  flex: 1;
  font-size: 0.8rem;
  word-break: break-all;
}

.copy-btn {
  padding: 0.5rem;
  background: #667eea;
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
}

.extension-badge.large {
  font-size: 0.875rem;
  padding: 4px 12px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #eee;
}

.btn-preview,
.btn-download {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9375rem;
  transition: all 0.2s;
}

.btn-preview {
  background: #f0f4ff;
  color: #667eea;
}

.btn-preview:hover:not(:disabled) {
  background: #e0e8ff;
}

.btn-preview:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-download {
  background: #667eea;
  color: white;
}

.btn-download:hover {
  background: #5a6fd6;
}

/* Info de descarga */
.stat-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: auto;
  font-size: 0.85rem;
  color: #666;
  background: #f8f9fa;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px dashed #ccc;
}

/* Directory Download Button */
.btn-download-dir {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  background: #667eea;
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
  margin-right: 4px;
}

.btn-download-dir:hover {
  background: #5a6fd6;
  transform: scale(1.1);
}

.btn-download-dir i {
  font-size: 16px;
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    flex-wrap: wrap;
  }

  .header-info h1 {
    font-size: 1.25rem;
  }

  .stats-bar {
    flex-wrap: wrap;
    gap: 1rem;
  }

  .stat-info {
    width: 100%;
    margin-top: 0.5rem;
    justify-content: center;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .modal-footer {
    flex-direction: column;
  }

  .btn-preview,
  .btn-download {
    width: 100%;
    justify-content: center;
  }
}

.mecanismo-filter-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #eef2ff, #e0e7ff);
  border: 1px solid #c7d2fe;
  border-radius: 8px;
  margin-bottom: 1rem;
  color: #4338ca;
  font-size: 0.9rem;
}
.mecanismo-filter-banner strong {
  color: #3730a3;
}
.btn-clear-mecanismo {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-left: auto;
  padding: 0.35rem 0.75rem;
  background: white;
  border: 1px solid #c7d2fe;
  border-radius: 6px;
  color: #4338ca;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-clear-mecanismo:hover {
  background: #4338ca;
  color: white;
}
.btn-clear-mecanismo .material-icons {
  font-size: 16px;
}
</style>
