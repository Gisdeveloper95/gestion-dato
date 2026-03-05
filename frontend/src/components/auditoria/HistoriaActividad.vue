<template>
  <div class="auditoria-page">
    <div class="panel-header">
      <h1 class="panel-title">Historial de Actividad</h1>
      <p class="panel-description">Consulta el registro completo de actividades del sistema</p>
    </div>
    
    <!-- Filtros -->
    <div class="filters-panel">
      <div class="filters-form">
        <div class="form-row">
          <div class="form-group">
            <label for="tipo-entidad">Tipo de Entidad</label>
            <select id="tipo-entidad" v-model="filtros.tipo_entidad">
              <option value="">Todos</option>
              <option value="municipio">Municipio</option>
              <option value="insumo">Insumo</option>
              <option value="clasificacion">Clasificación</option>
              <option value="detalle">Detalle</option>
              <option value="concepto">Concepto</option>
              <option value="usuario">Usuario</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="accion">Acción</label>
            <select id="accion" v-model="filtros.accion">
              <option value="">Todas</option>
              <option value="crear">Crear</option>
              <option value="actualizar">Actualizar</option>
              <option value="eliminar">Eliminar</option>
              <option value="consultar">Consultar</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="usuario">Usuario</label>
            <select id="usuario" v-model="filtros.usuario">
              <option value="">Todos</option>
              <option v-for="user in usuarios" :key="user.cod_usuario" :value="user.cod_usuario">
                {{ user.nombre }}
              </option>
            </select>
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="fecha-desde">Fecha Desde</label>
            <input 
              type="date" 
              id="fecha-desde" 
              v-model="filtros.fecha_desde"
            />
          </div>
          
          <div class="form-group">
            <label for="fecha-hasta">Fecha Hasta</label>
            <input 
              type="date" 
              id="fecha-hasta" 
              v-model="filtros.fecha_hasta"
            />
          </div>
          
          <div class="form-group">
            <label for="busqueda">Búsqueda</label>
            <div class="search-input">
              <input 
                type="text" 
                id="busqueda" 
                v-model="filtros.search"
                placeholder="Buscar..."
              />
              <i class="material-icons">search</i>
            </div>
          </div>
        </div>
        
        <div class="filters-actions">
          <button class="btn-primary" @click="aplicarFiltros">
            <i class="material-icons">filter_list</i>
            Aplicar Filtros
          </button>
          
          <button class="btn-secondary" @click="limpiarFiltros">
            <i class="material-icons">clear_all</i>
            Limpiar Filtros
          </button>
        </div>
      </div>
    </div>
    
    <!-- Resultados -->
    <div class="results-panel">
      <div class="results-header">
        <div class="results-count">
          {{ registrosFiltrados.length }} registros encontrados
        </div>
        
        <div class="results-actions">
          <button class="btn-outline" @click="exportarCSV">
            <i class="material-icons">file_download</i>
            Exportar CSV
          </button>
        </div>
      </div>
      
      <!-- Estado de carga -->
      <div v-if="cargando" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando registros de actividad...</p>
      </div>
      
      <!-- Mensaje de error -->
      <div v-else-if="error" class="error-state">
        <i class="material-icons">error</i>
        <p>{{ error }}</p>
        <button @click="cargarRegistros">Reintentar</button>
      </div>
      
      <!-- Tabla de resultados -->
      <div v-else-if="registrosFiltrados.length > 0" class="results-table-container">
        <table class="results-table">
          <thead>
            <tr>
              <th @click="ordenarPor('fecha_hora')">
                Fecha y Hora
                <i v-if="ordenacion.campo === 'fecha_hora'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('usuario')">
                Usuario
                <i v-if="ordenacion.campo === 'usuario'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('tipo_entidad')">
                Tipo
                <i v-if="ordenacion.campo === 'tipo_entidad'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th @click="ordenarPor('accion')">
                Acción
                <i v-if="ordenacion.campo === 'accion'" class="material-icons">
                  {{ ordenacion.ascendente ? 'arrow_upward' : 'arrow_downward' }}
                </i>
              </th>
              <th>Descripción</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="registro in registrosPaginados" :key="registro.id">
              <td>{{ formatearFechaHora(registro.fecha_hora) }}</td>
              <td>
                <span v-if="registro.usuario_nombre">{{ registro.usuario_nombre }}</span>
                <span v-else class="text-muted">No identificado</span>
              </td>
              <td>
                <span class="badge" :class="`badge-${getTipoEntidadClass(registro.tipo_entidad)}`">
                  {{ formatearTipoEntidad(registro.tipo_entidad) }}
                </span>
              </td>
              <td>
                <span class="badge" :class="`badge-${getAccionClass(registro.accion)}`">
                  {{ formatearAccion(registro.accion) }}
                </span>
              </td>
              <td>{{ getDescripcionFormateada(registro) }}</td>
              <td>
                <button class="action-btn" @click="verDetalles(registro)">
                  <i class="material-icons">info</i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Mensaje de no resultados -->
      <div v-else class="empty-state">
        <i class="material-icons">search</i>
        <p>No se encontraron registros con los filtros aplicados</p>
      </div>
      
      <!-- Paginación -->
      <div v-if="registrosFiltrados.length > 0" class="pagination">
        <button 
          class="pagination-btn" 
          :disabled="paginaActual === 1"
          @click="cambiarPagina(1)"
        >
          <i class="material-icons">first_page</i>
        </button>
        
        <button 
          class="pagination-btn" 
          :disabled="paginaActual === 1"
          @click="cambiarPagina(paginaActual - 1)"
        >
          <i class="material-icons">chevron_left</i>
        </button>
        
        <div class="pagination-info">
          Página {{ paginaActual }} de {{ totalPaginas }}
        </div>
        
        <button 
          class="pagination-btn" 
          :disabled="paginaActual === totalPaginas"
          @click="cambiarPagina(paginaActual + 1)"
        >
          <i class="material-icons">chevron_right</i>
        </button>
        
        <button 
          class="pagination-btn" 
          :disabled="paginaActual === totalPaginas"
          @click="cambiarPagina(totalPaginas)"
        >
          <i class="material-icons">last_page</i>
        </button>
      </div>
    </div>
    
    <!-- Modal de Detalles -->
    <div v-if="mostrarModal" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-container">
        <div class="modal-header">
          <h2>Detalles de Actividad</h2>
          <button class="close-btn" @click="cerrarModal">
            <i class="material-icons">close</i>
          </button>
        </div>
        
        <div class="modal-body">
          <div v-if="registroSeleccionado" class="detail-grid">
            <div class="detail-item">
              <div class="detail-label">Fecha y Hora</div>
              <div class="detail-value">{{ formatearFechaHora(registroSeleccionado.fecha_hora) }}</div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">Usuario</div>
              <div class="detail-value">{{ registroSeleccionado.usuario_nombre || 'No identificado' }}</div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">Tipo de Entidad</div>
              <div class="detail-value">{{ formatearTipoEntidad(registroSeleccionado.tipo_entidad) }}</div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">ID de Entidad</div>
              <div class="detail-value">{{ registroSeleccionado.id_entidad }}</div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">Acción</div>
              <div class="detail-value">{{ formatearAccion(registroSeleccionado.accion) }}</div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">Descripción</div>
              <div class="detail-value">{{ getDescripcionFormateada(registroSeleccionado) }}</div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">Dirección IP</div>
              <div class="detail-value">{{ registroSeleccionado.ip_origen || 'No disponible' }}</div>
            </div>
            
            <div class="detail-item full-width" v-if="registroSeleccionado.detalles">
              <div class="detail-label">Detalles Técnicos</div>
              <div class="detail-value json-viewer">
                <pre>{{ JSON.stringify(registroSeleccionado.detalles, null, 2) }}</pre>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn-primary" @click="cerrarModal">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { getRegistrosAuditoria } from '@/api/auditoria'
import type { AuditoriaItem } from '@/models/auditoria'
import { format, parseISO } from 'date-fns'
import { es } from 'date-fns/locale'
import { getUsuarios } from '@/api/insumos'

export default defineComponent({
  name: 'HistorialAuditoria',
  
  setup() {
    // Estado
    const registros = ref<AuditoriaItem[]>([])
    const cargando = ref(false)
    const error = ref<string | null>(null)
    const usuarios = ref<any[]>([])
    
    // Filtros
    const filtros = ref({
      tipo_entidad: '',
      accion: '',
      usuario: '',
      fecha_desde: '',
      fecha_hasta: '',
      search: ''
    })
    
    // Ordenación
    const ordenacion = ref({
      campo: 'fecha_hora',
      ascendente: false
    })
    
    // Paginación
    const paginaActual = ref(1)
    const porPagina = ref(20)
    
    // Modal
    const mostrarModal = ref(false)
    const registroSeleccionado = ref<AuditoriaItem | null>(null)
    
    // Cargar registros
    const cargarRegistros = async () => {
      try {
        cargando.value = true
        error.value = null
        
        // Construir parámetros basados en filtros
        const params: Record<string, any> = {}
        
        if (filtros.value.tipo_entidad) {
          params.tipo_entidad = filtros.value.tipo_entidad
        }
        
        if (filtros.value.accion) {
          params.accion = filtros.value.accion
        }
        
        if (filtros.value.usuario) {
          params.usuario = filtros.value.usuario
        }
        
        if (filtros.value.fecha_desde) {
          params.fecha_desde = filtros.value.fecha_desde
        }
        
        if (filtros.value.fecha_hasta) {
          params.fecha_hasta = filtros.value.fecha_hasta
        }
        
        if (filtros.value.search) {
          params.search = filtros.value.search
        }
        
        // Ordenación
        params.ordering = (ordenacion.value.ascendente ? '' : '-') + ordenacion.value.campo
        
        // Llamar a la API
        const data = await getRegistrosAuditoria(params)
        registros.value = data
        
        // Reiniciar paginación
        paginaActual.value = 1
        
        return true
      } catch (err: any) {
        console.error('Error al cargar registros de auditoría:', err)
        error.value = err.message || 'Error al cargar el historial de actividad'
        return false
      } finally {
        cargando.value = false
      }
    }
    
    // Cargar usuarios para filtro
    const cargarUsuarios = async () => {
      try {
        const data = await getUsuarios()
        usuarios.value = data
      } catch (err: any) {
        console.error('Error al cargar usuarios:', err)
      }
    }
    
    // Registros filtrados
    const registrosFiltrados = computed(() => {
      let resultado = [...registros.value]
      
      // Aplicar filtros locales si es necesario
      if (filtros.value.search && !cargando.value) {
        const busqueda = filtros.value.search.toLowerCase()
        resultado = resultado.filter(r => 
          (r.usuario_nombre?.toLowerCase().includes(busqueda)) ||
          r.tipo_entidad.toLowerCase().includes(busqueda) ||
          r.accion.toLowerCase().includes(busqueda) ||
          (r.entidad_info && JSON.stringify(r.entidad_info).toLowerCase().includes(busqueda))
        )
      }
      
      return resultado
    })
    
    // Registros paginados
    const registrosPaginados = computed(() => {
      const inicio = (paginaActual.value - 1) * porPagina.value
      const fin = inicio + porPagina.value
      return registrosFiltrados.value.slice(inicio, fin)
    })
    
    // Total de páginas
    const totalPaginas = computed(() => {
      return Math.ceil(registrosFiltrados.value.length / porPagina.value) || 1
    })
    
    // Cambiar página
    const cambiarPagina = (pagina: number) => {
      if (pagina < 1 || pagina > totalPaginas.value) return
      paginaActual.value = pagina
    }
    
    // Ordenar por campo
    const ordenarPor = (campo: string) => {
      if (ordenacion.value.campo === campo) {
        ordenacion.value.ascendente = !ordenacion.value.ascendente
      } else {
        ordenacion.value.campo = campo
        ordenacion.value.ascendente = true
      }
      
      cargarRegistros() // Recargar con nueva ordenación
    }
    
    // Aplicar filtros
    const aplicarFiltros = () => {
      cargarRegistros()
    }
    
    // Limpiar filtros
    const limpiarFiltros = () => {
      filtros.value = {
        tipo_entidad: '',
        accion: '',
        usuario: '',
        fecha_desde: '',
        fecha_hasta: '',
        search: ''
      }
      
      cargarRegistros()
    }
    
    // Ver detalles
    const verDetalles = (registro: AuditoriaItem) => {
      registroSeleccionado.value = registro
      mostrarModal.value = true
    }
    
    // Cerrar modal
    const cerrarModal = () => {
      mostrarModal.value = false
      registroSeleccionado.value = null
    }
    
    // Formatear fecha y hora
    const formatearFechaHora = (fecha: string): string => {
      try {
        return format(parseISO(fecha), 'dd/MM/yyyy HH:mm:ss', { locale: es })
      } catch (error) {
        return fecha
      }
    }
    
    // Formatear tipo de entidad
    const formatearTipoEntidad = (tipo: string): string => {
      const mapaTipos: Record<string, string> = {
        'municipio': 'Municipio',
        'insumo': 'Insumo',
        'clasificacion': 'Clasificación',
        'detalle': 'Detalle',
        'concepto': 'Concepto',
        'usuario': 'Usuario'
      }
      
      return mapaTipos[tipo.toLowerCase()] || tipo
    }
    
    // Obtener clase para tipo de entidad
    const getTipoEntidadClass = (tipo: string): string => {
      const mapaClases: Record<string, string> = {
        'municipio': 'info',
        'insumo': 'primary',
        'clasificacion': 'success',
        'detalle': 'warning',
        'concepto': 'danger',
        'usuario': 'secondary'
      }
      
      return mapaClases[tipo.toLowerCase()] || 'secondary'
    }
    
    // Formatear acción
    const formatearAccion = (accion: string): string => {
      const mapaAcciones: Record<string, string> = {
        'crear': 'Creación',
        'actualizar': 'Actualización',
        'eliminar': 'Eliminación',
        'consultar': 'Consulta'
      }
      
      return mapaAcciones[accion.toLowerCase()] || accion
    }
    
    // Obtener clase para acción
    const getAccionClass = (accion: string): string => {
      const mapaClases: Record<string, string> = {
        'crear': 'success',
        'actualizar': 'warning',
        'eliminar': 'danger',
        'consultar': 'info'
      }
      
      return mapaClases[accion.toLowerCase()] || 'secondary'
    }
    
    // Formatear descripción
    const getDescripcionFormateada = (registro: AuditoriaItem): string => {
      const entidad = formatearTipoEntidad(registro.tipo_entidad)
      const accion = formatearAccion(registro.accion).toLowerCase()
      
      let descripcion = `${accion} de ${entidad.toLowerCase()}`
      
      // Añadir información de la entidad si está disponible
      if (registro.entidad_info) {
        if (registro.entidad_info.nombre) {
          descripcion += ` "${registro.entidad_info.nombre}"`
        } else if (registro.entidad_info.concepto) {
          descripcion += ` "${registro.entidad_info.concepto}"`
        }
        
        if (registro.entidad_info.municipio) {
          descripcion += ` en ${registro.entidad_info.municipio}`
        } else if (registro.tipo_entidad === 'municipio' && registro.entidad_info.departamento) {
          descripcion += ` (${registro.entidad_info.departamento})`
        }
      } else {
        descripcion += ` #${registro.id_entidad}`
      }
      
      return descripcion
    }
    
    // Exportar a CSV
    const exportarCSV = () => {
      try {
        // Preparar los datos
        const datos = registrosFiltrados.value.map(r => ({
          'Fecha y Hora': formatearFechaHora(r.fecha_hora),
          'Usuario': r.usuario_nombre || 'No identificado',
          'Tipo de Entidad': formatearTipoEntidad(r.tipo_entidad),
          'Acción': formatearAccion(r.accion),
          'ID Entidad': r.id_entidad,
          'Descripción': getDescripcionFormateada(r),
          'IP Origen': r.ip_origen || 'No disponible'
        }))
        
        // Convertir a CSV
        const headers = Object.keys(datos[0])
        const csvContent = [
          headers.join(','),
          ...datos.map(row => headers.map(header => {
            const val = row[header as keyof typeof row]
            // Escapar comillas y añadir comillas alrededor de valores que contengan comas
            const escapedVal = typeof val === 'string' && (val.includes(',') || val.includes('"')) 
              ? `"${val.replace(/"/g, '""')}"` 
              : val
            return escapedVal
          }).join(','))
        ].join('\n')
        
        // Crear Blob y descargar
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `auditoria_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
      } catch (err: any) {
        console.error('Error al exportar a CSV:', err)
        alert('Error al exportar a CSV. Por favor, inténtelo de nuevo.')
      }
    }
    
    // Inicializar
    onMounted(() => {
      cargarRegistros()
      cargarUsuarios()
    })
    
    return {
      registros,
      cargando,
      error,
      usuarios,
      filtros,
      ordenacion,
      paginaActual,
      porPagina,
      mostrarModal,
      registroSeleccionado,
      registrosFiltrados,
      registrosPaginados,
      totalPaginas,
      cargarRegistros,
      cambiarPagina,
      ordenarPor,
      aplicarFiltros,
      limpiarFiltros,
      verDetalles,
      cerrarModal,
      formatearFechaHora,
      formatearTipoEntidad,
      getTipoEntidadClass,
      formatearAccion,
      getAccionClass,
      getDescripcionFormateada,
      exportarCSV
    }
  }
})
</script>

<style scoped>
.auditoria-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.panel-header {
  margin-bottom: 1rem;
}

.panel-title {
  font-size: 1.5rem;
  margin: 0 0 0.5rem;
  color: #343a40;
}

.panel-description {
  color: #6c757d;
  margin: 0;
}

/* Filtros */
.filters-panel {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.form-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  flex: 1;
  min-width: 200px;
}

.form-group label {
  display: block;
  font-size: 0.9rem;
  color: #495057;
  margin-bottom: 0.5rem;
}

.form-group select,
.form-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.9rem;
}

.search-input {
  position: relative;
}

.search-input input {
  padding-right: 2.5rem;
}

.search-input i {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

.filters-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.btn-primary,
.btn-secondary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0069d9;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

/* Resultados */
.results-panel {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.results-count {
  font-weight: 500;
  color: #343a40;
}

.btn-outline {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 1px solid #007bff;
  border-radius: 4px;
  background-color: transparent;
  color: #007bff;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-outline:hover {
  background-color: rgba(0, 123, 255, 0.1);
}

/* Estado de carga y errores */
.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
  color: #6c757d;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state i,
.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-state i {
  color: #dc3545;
}

.error-state button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* Tabla de resultados */
.results-table-container {
  overflow-x: auto;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
}

.results-table th,
.results-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.results-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
  cursor: pointer;
  position: relative;
}

.results-table th:hover {
  background-color: #e9ecef;
}

.results-table th i {
  font-size: 1rem;
  vertical-align: middle;
  margin-left: 0.25rem;
}

.results-table tr:hover {
  background-color: #f8f9fa;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-primary {
  background-color: #cfe2ff;
  color: #0d6efd;
}

.badge-secondary {
  background-color: #e2e3e5;
  color: #6c757d;
}

.badge-success {
  background-color: #d1e7dd;
  color: #198754;
}

.badge-danger {
  background-color: #f8d7da;
  color: #dc3545;
}

.badge-warning {
  background-color: #fff3cd;
  color: #ffc107;
}

.badge-info {
background-color: #cff4fc;
color: #0dcaf0;
}

.action-btn {
background: none;
border: none;
color: #007bff;
cursor: pointer;
display: flex;
align-items: center;
justify-content: center;
width: 32px;
height: 32px;
border-radius: 4px;
}

.action-btn:hover {
background-color: rgba(0, 123, 255, 0.1);
}

/* Paginación */
.pagination {
display: flex;
justify-content: center;
align-items: center;
margin-top: 1.5rem;
gap: 0.5rem;
}

.pagination-btn {
width: 36px;
height: 36px;
display: flex;
align-items: center;
justify-content: center;
border: 1px solid #dee2e6;
background-color: white;
border-radius: 4px;
cursor: pointer;
}

.pagination-btn:disabled {
opacity: 0.5;
cursor: not-allowed;
}

.pagination-btn:hover:not(:disabled) {
background-color: #e9ecef;
}

.pagination-info {
padding: 0 1rem;
color: #6c757d;
}

/* Modal */
.modal-overlay {
position: fixed;
top: 0;
left: 0;
right: 0;
bottom: 0;
background-color: rgba(0, 0, 0, 0.5);
display: flex;
justify-content: center;
align-items: center;
z-index: 1000;
}

.modal-container {
background-color: white;
border-radius: 8px;
box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
width: 90%;
max-width: 800px;
max-height: 90vh;
display: flex;
flex-direction: column;
overflow: hidden;
}

.modal-header {
display: flex;
justify-content: space-between;
align-items: center;
padding: 1rem 1.5rem;
border-bottom: 1px solid #e9ecef;
}

.modal-header h2 {
margin: 0;
font-size: 1.3rem;
}

.close-btn {
background: none;
border: none;
color: #6c757d;
cursor: pointer;
font-size: 1.5rem;
display: flex;
align-items: center;
justify-content: center;
}

.modal-body {
padding: 1.5rem;
overflow-y: auto;
}

.modal-footer {
padding: 1rem 1.5rem;
border-top: 1px solid #e9ecef;
display: flex;
justify-content: flex-end;
}

/* Detalles */
.detail-grid {
display: grid;
grid-template-columns: repeat(2, 1fr);
gap: 1rem;
}

.detail-item {
padding: 0.75rem;
background-color: #f8f9fa;
border-radius: 4px;
}

.detail-item.full-width {
grid-column: span 2;
}

.detail-label {
font-weight: 600;
color: #495057;
margin-bottom: 0.5rem;
}

.detail-value {
color: #343a40;
}

.json-viewer {
background-color: #f0f0f0;
border-radius: 4px;
padding: 0.75rem;
max-height: 300px;
overflow-y: auto;
}

.json-viewer pre {
margin: 0;
white-space: pre-wrap;
font-family: monospace;
font-size: 0.85rem;
}

.text-muted {
color: #6c757d;
}

/* Responsive */
@media (max-width: 768px) {
.form-group {
  min-width: 100%;
}

.detail-grid {
  grid-template-columns: 1fr;
}

.detail-item.full-width {
  grid-column: span 1;
}
}
</style>