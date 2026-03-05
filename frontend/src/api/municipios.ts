import api from './config'
import type { Municipio, Departamento } from '@/models/municipio'

// Tipo para manejador de respuestas paginadas
type PaginatedResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// =============== FUNCIONES PRINCIPALES PARA MunicipiosList.vue ===============

// Obtener todos los municipios (con opción de filtros)
export const getMunicipios = async (params = {}): Promise<any[]> => {
  try {
    const response = await api.get<PaginatedResponse<any>>('/preoperacion/municipios/', { params });
    return response.results || [];
  } catch (error) {
    console.error('Error al obtener municipios:', error);
    throw error;
  }
}

// Obtener un municipio por ID
export const getMunicipioById = async (id: number): Promise<any> => {
  try {
    const response = await api.get<any>(`/preoperacion/municipios/${id}/`);
    return response;
  } catch (error) {
    console.error('Error al obtener municipio:', error);
    throw error;
  }
}

// Eliminar un municipio en cascada (elimina todas las dependencias)
export const eliminarMunicipioCascada = async (id: number): Promise<any> => {
  try {
    const response = await api.delete(`/preoperacion/municipios/${id}/eliminar_cascada/`);
    return response;
  } catch (error) {
    console.error('Error al eliminar municipio en cascada:', error);
    throw error;
  }
}

// =============== FUNCIONES ESPECÍFICAS PARA InsumosList.vue ===============

// Obtener insumos de un municipio
export const getInsumosByMunicipio = async (municipioId: number): Promise<any[]> => {
  try {
    // Intentar diferentes URLs hasta encontrar la correcta
    let response;
    
    try {
      // Opción 1: URL específica del municipio
      response = await api.get(`/preoperacion/municipios/${municipioId}/insumos/`);
    } catch (error1) {
      try {
        // Opción 2: Filtro con parámetro cod_municipio
        response = await api.get(`/preoperacion/insumos/?cod_municipio=${municipioId}`);
      } catch (error2) {
        // Opción 3: Filtro con parámetro municipio
        response = await api.get(`/preoperacion/insumos/?municipio=${municipioId}`);
      }
    }
    
    return Array.isArray(response.results) ? response.results : Array.isArray(response) ? response : [];
  } catch (error) {
    console.warn(`No se pudieron obtener insumos para el municipio ${municipioId}:`, error);
    return [];
  }
}

// Obtener clasificaciones de insumos de un municipio
export const getClasificacionesByMunicipio = async (municipioId: number): Promise<any[]> => {
  try {
    // Intentar diferentes URLs hasta encontrar la correcta
    let response;
    
    try {
      // Opción 1: URL específica del municipio
      response = await api.get(`/preoperacion/municipios/${municipioId}/clasificaciones/`);
    } catch (error1) {
      try {
        // Opción 2: Filtro con parámetro cod_municipio
        response = await api.get(`/preoperacion/clasificaciones/?cod_municipio=${municipioId}`);
      } catch (error2) {
        // Opción 3: Filtro con parámetro municipio
        response = await api.get(`/preoperacion/clasificaciones/?municipio=${municipioId}`);
      }
    }
    
    return Array.isArray(response.results) ? response.results : Array.isArray(response) ? response : [];
  } catch (error) {
    console.warn(`No se pudieron obtener clasificaciones para el municipio ${municipioId}:`, error);
    return [];
  }
}

// Obtener detalles de un municipio
export const getDetallesByMunicipio = async (municipioId: number): Promise<any[]> => {
  try {
    // Intentar diferentes URLs hasta encontrar la correcta
    let response;
    
    try {
      // Opción 1: URL específica del municipio
      response = await api.get(`/preoperacion/municipios/${municipioId}/detalles/`);
    } catch (error1) {
      try {
        // Opción 2: Filtro con parámetro municipio
        response = await api.get(`/preoperacion/detalles/?municipio=${municipioId}`);
      } catch (error2) {
        try {
          // Opción 3: Filtro con parámetro cod_municipio
          response = await api.get(`/preoperacion/detalles/?cod_municipio=${municipioId}`);
        } catch (error3) {
          // Opción 4: Endpoint de detalles-insumo
          response = await api.get(`/preoperacion/detalles-insumo/?cod_municipio=${municipioId}`);
        }
      }
    }
    
    return Array.isArray(response.results) ? response.results : Array.isArray(response) ? response : [];
  } catch (error) {
    console.warn(`No se pudieron obtener detalles para el municipio ${municipioId}:`, error);
    // Retornar array vacío en lugar de lanzar error para que no rompa la carga
    return [];
  }
}

// =============== FUNCIONES ADICIONALES DEL ARCHIVO ORIGINAL ===============

// Buscar municipios por nombre
export const buscarMunicipios = async (query: string): Promise<any[]> => {
  try {
    const response = await api.get<PaginatedResponse<any>>('/preoperacion/municipios/', { 
      params: { search: query } 
    });
    return response.results || [];
  } catch (error) {
    console.error('Error al buscar municipios:', error);
    throw error;
  }
}

// Obtener municipios por departamento
export const getMunicipiosByDepartamento = async (deptoId: number): Promise<any[]> => {
  try {
    const response = await api.get<any[]>(`/preoperacion/departamentos/${deptoId}/municipios/`);
    return response;
  } catch (error) {
    throw error;
  }
}

// Obtener estadísticas de un municipio
export const getEstadisticasMunicipio = async (id: number): Promise<any> => {
  try {
    const response = await api.get<any>(`/preoperacion/municipios/${id}/estadisticas/`);
    return response;
  } catch (error) {
    console.error('Error al obtener estadísticas del municipio:', error);
    throw error;
  }
}

// Crear un municipio
export const crearMunicipio = async (municipio: Partial<any>): Promise<any> => {
  try {
    const response = await api.post<any>('/preoperacion/municipios/', municipio);
    return response;
  } catch (error) {
    console.error('Error al crear municipio:', error);
    throw error;
  }
}

// Actualizar un municipio
export const actualizarMunicipio = async (id: number, municipio: Partial<any>): Promise<any> => {
  try {
    const response = await api.put<any>(`/preoperacion/municipios/${id}/`, municipio);
    return response;
  } catch (error) {
    console.error('Error al actualizar municipio:', error);
    throw error;
  }
}

// Eliminar un municipio (estándar - puede fallar por dependencias)
export const eliminarMunicipio = async (id: number): Promise<any> => {
  try {
    const response = await api.delete(`/preoperacion/municipios/${id}/`);
    return response;
  } catch (error) {
    console.error('Error al eliminar municipio:', error);
    throw error;
  }
}

// Obtener profesionales de un municipio
export const getProfesionalesByMunicipio = async (municipioId: number): Promise<any[]> => {
  try {
    const response = await api.get(`/preoperacion/municipios/${municipioId}/profesionales/`);
    return response;
  } catch (error) {
    console.error('Error al obtener profesionales del municipio:', error);
    throw error;
  }
}

// =============== API PARA DEPARTAMENTOS ===============
export const departamentosApi = {
  // Obtener todos los departamentos
  async getAll(): Promise<any[]> {
    try {
      const response = await api.get('/preoperacion/departamentos/')
      return Array.isArray(response.results) ? response.results : Array.isArray(response) ? response : []
    } catch (error) {
      console.error('Error obteniendo departamentos:', error)
      throw error
    }
  },

  // Obtener departamento por ID
  async getById(id: number): Promise<any> {
    try {
      const response = await api.get(`/preoperacion/departamentos/${id}/`)
      return response
    } catch (error) {
      console.error(`Error obteniendo departamento ${id}:`, error)
      throw error
    }
  },

  // Buscar departamentos
  async search(query: string): Promise<any[]> {
    try {
      const response = await api.get(`/preoperacion/departamentos/?search=${encodeURIComponent(query)}`)
      return Array.isArray(response.results) ? response.results : Array.isArray(response) ? response : []
    } catch (error) {
      console.error('Error buscando departamentos:', error)
      throw error
    }
  }
}

// =============== FUNCIONES AUXILIARES ===============

// Obtener municipios con información del departamento
export const getMunicipiosConDepartamento = async (): Promise<any[]> => {
  try {
    const [municipios, departamentos] = await Promise.all([
      getMunicipios(),
      departamentosApi.getAll()
    ])

    // Mapear municipios con información del departamento
    return municipios.map(municipio => ({
      ...municipio,
      departamento: departamentos.find(dept => dept.cod_depto === municipio.cod_depto)
    }))
  } catch (error) {
    console.error('Error obteniendo municipios con departamentos:', error)
    throw error
  }
}

// Obtener departamentos con sus municipios
export const getDepartamentosConMunicipios = async (): Promise<any[]> => {
  try {
    const [departamentos, municipios] = await Promise.all([
      departamentosApi.getAll(),
      getMunicipios()
    ])

    return departamentos.map(departamento => ({
      ...departamento,
      municipios: municipios.filter(mun => mun.cod_depto === departamento.cod_depto)
    }))
  } catch (error) {
    console.error('Error obteniendo departamentos con municipios:', error)
    throw error
  }
}

// Obtener municipios por página
export const getMunicipiosPaginados = async (page: number = 1, pageSize: number = 20): Promise<{
  results: any[]
  count: number
  next: string | null
  previous: string | null
}> => {
  try {
    const response = await api.get(`/preoperacion/municipios/?page=${page}&page_size=${pageSize}`)
    return {
      results: Array.isArray(response.results) ? response.results : [],
      count: response.count || 0,
      next: response.next || null,
      previous: response.previous || null
    }
  } catch (error) {
    console.error('Error obteniendo municipios paginados:', error)
    throw error
  }
}

// Validar si un municipio existe
export const existeMunicipio = async (id: number): Promise<boolean> => {
  try {
    await getMunicipioById(id)
    return true
  } catch (error) {
    return false
  }
}

// =============== ALIAS PARA COMPATIBILIDAD ===============
export const obtenerMunicipios = getMunicipios
export const obtenerDepartamentos = departamentosApi.getAll
export const buscarDepartamentos = departamentosApi.search

// =============== EXPORTACIONES POR DEFECTO ===============
export default {
  getMunicipios,
  getMunicipioById,
  eliminarMunicipioCascada,
  getInsumosByMunicipio,
  getClasificacionesByMunicipio,
  getDetallesByMunicipio,
  buscarMunicipios,
  getMunicipiosByDepartamento,
  getEstadisticasMunicipio,
  crearMunicipio,
  actualizarMunicipio,
  eliminarMunicipio,
  getProfesionalesByMunicipio,
  departamentosApi,
  getMunicipiosConDepartamento,
  getDepartamentosConMunicipios,
  getMunicipiosPaginados,
  existeMunicipio,
  obtenerMunicipios,
  obtenerDepartamentos,
  buscarDepartamentos
}