import axios, { AxiosResponse } from 'axios'
import { API_BASE_URL } from './config'

// =============== INTERFACES ===============
export interface Categoria {
  id_categoria: number
  nom_categoria: string
  descripcion?: string
  estado: 'activo' | 'inactivo'
  fecha_creacion: string
  fecha_actualizacion: string
  // Campos adicionales si existen en el backend
  created_by?: number
  updated_by?: number
  insumos_count?: number // Cantidad de insumos en esta categoría
}

export interface CategoriaCreate {
  nom_categoria: string
  descripcion?: string
  estado?: 'activo' | 'inactivo'
}

export interface CategoriaUpdate extends Partial<CategoriaCreate> {
  id_categoria?: number
}

export interface CategoriaFilter {
  estado?: 'activo' | 'inactivo'
  search?: string
  fecha_creacion_desde?: string
  fecha_creacion_hasta?: string
  ordering?: string
  page?: number
  page_size?: number
}

export interface CategoriaResponse {
  count: number
  next: string | null
  previous: string | null
  results: Categoria[]
}

export interface CategoriaStats {
  total: number
  activas: number
  inactivas: number
  recientes: number // Creadas en los últimos 30 días
  con_insumos: number
  sin_insumos: number
}

export interface BulkUpdateResponse {
  updated: number
  errors: string[]
  success_ids: number[]
  error_ids: number[]
}

// =============== CONFIGURACIÓN BASE ===============
const API_ENDPOINT = `${API_BASE_URL}/categorias/`

// Token de autenticación
const getAuthConfig = () => {
  const token = localStorage.getItem('token')
  return token ? {
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    }
  } : {}
}

// =============== SERVICIOS CRUD BÁSICOS ===============

/**
 * Obtener todas las categorías con filtros opcionales
 */
export const getCategorias = async (filters: CategoriaFilter = {}): Promise<CategoriaResponse> => {
  try {
    const params = new URLSearchParams()
    
    if (filters.estado) params.append('estado', filters.estado)
    if (filters.search) params.append('search', filters.search)
    if (filters.fecha_creacion_desde) params.append('fecha_creacion__gte', filters.fecha_creacion_desde)
    if (filters.fecha_creacion_hasta) params.append('fecha_creacion__lte', filters.fecha_creacion_hasta)
    if (filters.ordering) params.append('ordering', filters.ordering)
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.page_size) params.append('page_size', filters.page_size.toString())
    
    const url = params.toString() ? `${API_ENDPOINT}?${params}` : API_ENDPOINT
    const response: AxiosResponse<CategoriaResponse> = await axios.get(url, getAuthConfig())
    
    return response.data
  } catch (error: any) {
    console.error('Error obteniendo categorías:', error)
    throw new Error(error.response?.data?.message || 'Error al obtener las categorías')
  }
}

/**
 * Obtener todas las categorías sin paginación (para selects y filtros)
 */
export const getAllCategorias = async (activas_solo: boolean = false): Promise<Categoria[]> => {
  try {
    let todasLasCategorias: Categoria[] = []
    let url = API_ENDPOINT
    
    if (activas_solo) {
      url += '?estado=activo'
    }
    
    // Obtener todas las páginas
    while (url) {
      const response: AxiosResponse<CategoriaResponse> = await axios.get(url, getAuthConfig())
      todasLasCategorias = [...todasLasCategorias, ...response.data.results]
      url = response.data.next || ''
    }
    
    return todasLasCategorias
  } catch (error: any) {
    console.error('Error obteniendo todas las categorías:', error)
    throw new Error(error.response?.data?.message || 'Error al obtener todas las categorías')
  }
}

/**
 * Obtener una categoría por ID
 */
export const getCategoria = async (id: number): Promise<Categoria> => {
  try {
    const response: AxiosResponse<Categoria> = await axios.get(`${API_ENDPOINT}${id}/`, getAuthConfig())
    return response.data
  } catch (error: any) {
    console.error(`Error obteniendo categoría ${id}:`, error)
    throw new Error(error.response?.data?.message || 'Error al obtener la categoría')
  }
}

/**
 * Crear una nueva categoría
 */
export const createCategoria = async (data: CategoriaCreate): Promise<Categoria> => {
  try {
    // Valores por defecto
    const categoriaData = {
      estado: 'activo',
      ...data
    }
    
    const response: AxiosResponse<Categoria> = await axios.post(API_ENDPOINT, categoriaData, getAuthConfig())
    return response.data
  } catch (error: any) {
    console.error('Error creando categoría:', error)
    
    if (error.response?.data) {
      const errorData = error.response.data
      
      // Manejar errores de validación específicos
      if (errorData.nom_categoria) {
        throw new Error(`Nombre de categoría: ${errorData.nom_categoria[0]}`)
      }
      
      if (errorData.non_field_errors) {
        throw new Error(errorData.non_field_errors[0])
      }
      
      throw new Error(errorData.message || errorData.detail || 'Error al crear la categoría')
    }
    
    throw new Error('Error al crear la categoría')
  }
}

/**
 * Actualizar una categoría existente
 */
export const updateCategoria = async (id: number, data: CategoriaUpdate): Promise<Categoria> => {
  try {
    const response: AxiosResponse<Categoria> = await axios.patch(`${API_ENDPOINT}${id}/`, data, getAuthConfig())
    return response.data
  } catch (error: any) {
    console.error(`Error actualizando categoría ${id}:`, error)
    
    if (error.response?.data) {
      const errorData = error.response.data
      
      if (errorData.nom_categoria) {
        throw new Error(`Nombre de categoría: ${errorData.nom_categoria[0]}`)
      }
      
      if (errorData.non_field_errors) {
        throw new Error(errorData.non_field_errors[0])
      }
      
      throw new Error(errorData.message || errorData.detail || 'Error al actualizar la categoría')
    }
    
    throw new Error('Error al actualizar la categoría')
  }
}

/**
 * Eliminar una categoría
 */
export const deleteCategoria = async (id: number): Promise<void> => {
  try {
    await axios.delete(`${API_ENDPOINT}${id}/`, getAuthConfig())
  } catch (error: any) {
    console.error(`Error eliminando categoría ${id}:`, error)
    
    if (error.response?.status === 400) {
      throw new Error('No se puede eliminar esta categoría porque tiene insumos asociados')
    }
    
    throw new Error(error.response?.data?.message || 'Error al eliminar la categoría')
  }
}

// =============== SERVICIOS AVANZADOS ===============

/**
 * Obtener estadísticas de categorías
 */
export const getCategoriasStats = async (): Promise<CategoriaStats> => {
  try {
    const response: AxiosResponse<CategoriaStats> = await axios.get(`${API_ENDPOINT}stats/`, getAuthConfig())
    return response.data
  } catch (error: any) {
    console.error('Error obteniendo estadísticas de categorías:', error)
    throw new Error(error.response?.data?.message || 'Error al obtener estadísticas')
  }
}

/**
 * Búsqueda inteligente de categorías
 */
export const searchCategorias = async (query: string, limit: number = 10): Promise<Categoria[]> => {
  try {
    const response: AxiosResponse<CategoriaResponse> = await axios.get(
      `${API_ENDPOINT}?search=${encodeURIComponent(query)}&page_size=${limit}`,
      getAuthConfig()
    )
    return response.data.results
  } catch (error: any) {
    console.error('Error en búsqueda de categorías:', error)
    throw new Error(error.response?.data?.message || 'Error en la búsqueda')
  }
}

/**
 * Cambiar estado de una categoría
 */
export const toggleCategoriaStatus = async (id: number): Promise<Categoria> => {
  try {
    const response: AxiosResponse<Categoria> = await axios.patch(
      `${API_ENDPOINT}${id}/toggle_status/`,
      {},
      getAuthConfig()
    )
    return response.data
  } catch (error: any) {
    console.error(`Error cambiando estado de categoría ${id}:`, error)
    throw new Error(error.response?.data?.message || 'Error al cambiar el estado')
  }
}

/**
 * Duplicar una categoría
 */
export const duplicateCategoria = async (id: number, newName?: string): Promise<Categoria> => {
  try {
    const original = await getCategoria(id)
    const duplicateData: CategoriaCreate = {
      nom_categoria: newName || `${original.nom_categoria} (Copia)`,
      descripcion: original.descripcion,
      estado: 'inactivo' // Las copias empiezan inactivas por seguridad
    }
    
    return await createCategoria(duplicateData)
  } catch (error: any) {
    console.error(`Error duplicando categoría ${id}:`, error)
    throw new Error('Error al duplicar la categoría')
  }
}

// =============== OPERACIONES MASIVAS ===============

/**
 * Actualización masiva de estado
 */
export const bulkUpdateCategoriaStatus = async (
  ids: number[], 
  estado: 'activo' | 'inactivo'
): Promise<BulkUpdateResponse> => {
  try {
    const response: AxiosResponse<BulkUpdateResponse> = await axios.patch(
      `${API_ENDPOINT}bulk_update_status/`,
      { ids, estado },
      getAuthConfig()
    )
    return response.data
  } catch (error: any) {
    console.error('Error en actualización masiva:', error)
    throw new Error(error.response?.data?.message || 'Error en la actualización masiva')
  }
}

/**
 * Eliminación masiva
 */
export const bulkDeleteCategorias = async (ids: number[]): Promise<BulkUpdateResponse> => {
  try {
    const response: AxiosResponse<BulkUpdateResponse> = await axios.delete(
      `${API_ENDPOINT}bulk_delete/`,
      {
        ...getAuthConfig(),
        data: { ids }
      }
    )
    return response.data
  } catch (error: any) {
    console.error('Error en eliminación masiva:', error)
    throw new Error(error.response?.data?.message || 'Error en la eliminación masiva')
  }
}

// =============== EXPORTACIÓN ===============

/**
 * Exportar categorías
 */
export const exportCategorias = async (
  filters: CategoriaFilter = {},
  format: 'csv' | 'excel' = 'excel'
): Promise<Blob> => {
  try {
    const params = new URLSearchParams()
    params.append('format', format)
    
    if (filters.estado) params.append('estado', filters.estado)
    if (filters.search) params.append('search', filters.search)
    if (filters.fecha_creacion_desde) params.append('fecha_creacion__gte', filters.fecha_creacion_desde)
    if (filters.fecha_creacion_hasta) params.append('fecha_creacion__lte', filters.fecha_creacion_hasta)
    
    const response = await axios.get(
      `${API_ENDPOINT}export/?${params}`,
      {
        ...getAuthConfig(),
        responseType: 'blob'
      }
    )
    
    return response.data
  } catch (error: any) {
    console.error('Error exportando categorías:', error)
    throw new Error('Error al exportar las categorías')
  }
}

/**
 * Exportar categorías seleccionadas
 */
export const exportSelectedCategorias = async (
  ids: number[],
  format: 'csv' | 'excel' = 'excel'
): Promise<Blob> => {
  try {
    const response = await axios.post(
      `${API_ENDPOINT}export_selected/`,
      { ids, format },
      {
        ...getAuthConfig(),
        responseType: 'blob'
      }
    )
    
    return response.data
  } catch (error: any) {
    console.error('Error exportando categorías seleccionadas:', error)
    throw new Error('Error al exportar las categorías seleccionadas')
  }
}

// =============== UTILIDADES ===============

/**
 * Descargar archivo de exportación
 */
export const downloadFile = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.style.display = 'none'
  
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  window.URL.revokeObjectURL(url)
}

/**
 * Validar datos de categoría antes de enviar
 */
export const validateCategoriaData = (data: CategoriaCreate | CategoriaUpdate): string[] => {
  const errors: string[] = []
  
  if (data.nom_categoria !== undefined) {
    if (!data.nom_categoria || data.nom_categoria.trim().length === 0) {
      errors.push('El nombre de la categoría es requerido')
    } else if (data.nom_categoria.length < 3) {
      errors.push('El nombre debe tener al menos 3 caracteres')
    } else if (data.nom_categoria.length > 100) {
      errors.push('El nombre no puede exceder 100 caracteres')
    }
  }
  
  if (data.descripcion && data.descripcion.length > 500) {
    errors.push('La descripción no puede exceder 500 caracteres')
  }
  
  if (data.estado && !['activo', 'inactivo'].includes(data.estado)) {
    errors.push('El estado debe ser "activo" o "inactivo"')
  }
  
  return errors
}

/**
 * Verificar si una categoría puede ser eliminada
 */
export const canDeleteCategoria = async (id: number): Promise<boolean> => {
  try {
    const response = await axios.get(`${API_ENDPOINT}${id}/can_delete/`, getAuthConfig())
    return response.data.can_delete
  } catch (error) {
    return false
  }
}

// =============== CACHÉ LOCAL (OPCIONAL) ===============
let categoriasCache: Categoria[] | null = null
let cacheTimestamp: number = 0
const CACHE_DURATION = 5 * 60 * 1000 // 5 minutos

/**
 * Obtener categorías con caché
 */
export const getCategoriasCached = async (forceRefresh: boolean = false): Promise<Categoria[]> => {
  const now = Date.now()
  
  if (!forceRefresh && categoriasCache && (now - cacheTimestamp) < CACHE_DURATION) {
    return categoriasCache
  }
  
  try {
    const categorias = await getAllCategorias()
    categoriasCache = categorias
    cacheTimestamp = now
    return categorias
  } catch (error) {
    // Si hay error y tenemos caché, devolver caché aunque esté vencido
    if (categoriasCache) {
      return categoriasCache
    }
    throw error
  }
}

/**
 * Limpiar caché
 */
export const clearCategoriasCache = () => {
  categoriasCache = null
  cacheTimestamp = 0
}

// Exportar todo el servicio como default
export default {
  // CRUD básico
  getCategorias,
  getAllCategorias,
  getCategoria,
  createCategoria,
  updateCategoria,
  deleteCategoria,
  
  // Servicios avanzados
  getCategoriasStats,
  searchCategorias,
  toggleCategoriaStatus,
  duplicateCategoria,
  
  // Operaciones masivas
  bulkUpdateCategoriaStatus,
  bulkDeleteCategorias,
  
  // Exportación
  exportCategorias,
  exportSelectedCategorias,
  downloadFile,
  
  // Utilidades
  validateCategoriaData,
  canDeleteCategoria,
  
  // Caché
  getCategoriasCached,
  clearCategoriasCache
}