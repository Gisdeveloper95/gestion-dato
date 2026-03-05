import api from './config'
import type { Insumo, ClasificacionInsumo, DetalleInsumo, Concepto } from '@/models/insumo'

// Tipo para respuestas paginadas
type PaginatedResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// --------------------- INSUMOS ---------------------

/**
 * Obtiene todos los insumos con opción de filtrado
 */
export const getInsumos = async (params = {}): Promise<Insumo[]> => {
  try {
    const response = await api.get<PaginatedResponse<Insumo>>('/preoperacion/insumos/', { params });
    return response.results || [];
  } catch (error) {
    console.error('Error al obtener insumos:', error);
    throw error;
  }
}

/**
 * Obtiene un insumo específico por su ID
 */
export const getInsumoById = async (id: number): Promise<Insumo> => {
  try {
    const response = await api.get<Insumo>(`/preoperacion/insumos/${id}/`);
    return response;
  } catch (error) {
    console.error(`Error al obtener insumo ${id}:`, error);
    throw error;
  }
}

/**
 * Obtiene todos los insumos de un municipio específico
 */
export const getInsumosByMunicipio = async (municipioId: number): Promise<Insumo[]> => {
  try {
    const response = await api.get<Insumo[]>(`/preoperacion/municipios/${municipioId}/insumos/`);
    return response;
  } catch (error) {
    console.error(`Error al obtener insumos del municipio ${municipioId}:`, error);
    throw error;
  }
}

/**
 * Crea un nuevo insumo
 */
export const createInsumo = async (data: Partial<Insumo>): Promise<Insumo> => {
  try {
    const response = await api.post<Insumo>('/preoperacion/insumos/', data);
    return response;
  } catch (error) {
    console.error('Error al crear insumo:', error);
    throw error;
  }
}

/**
 * Actualiza un insumo existente
 */
export const updateInsumo = async (id: number, data: Partial<Insumo>): Promise<Insumo> => {
  try {
    const response = await api.put<Insumo>(`/preoperacion/insumos/${id}/`, data);
    return response;
  } catch (error) {
    console.error(`Error al actualizar insumo ${id}:`, error);
    throw error;
  }
}

/**
 * Elimina un insumo
 */
export const deleteInsumo = async (id: number): Promise<void> => {
  try {
    await api.delete(`/preoperacion/insumos/${id}/`);
  } catch (error) {
    console.error(`Error al eliminar insumo ${id}:`, error);
    throw error;
  }
}

// --------------------- CLASIFICACIONES ---------------------

/**
 * Obtiene todas las clasificaciones con opción de filtrado
 */
export const getClasificaciones = async (params = {}): Promise<ClasificacionInsumo[]> => {
  try {
    const response = await api.get<PaginatedResponse<ClasificacionInsumo>>('/preoperacion/clasificaciones/', { params });
    return response.results || [];
  } catch (error) {
    console.error('Error al obtener clasificaciones:', error);
    throw error;
  }
}

/**
 * Obtiene una clasificación específica por su ID
 */
export const getClasificacionById = async (id: number): Promise<ClasificacionInsumo> => {
  try {
    const response = await api.get<ClasificacionInsumo>(`/preoperacion/clasificaciones/${id}/`);
    return response;
  } catch (error) {
    console.error(`Error al obtener clasificación ${id}:`, error);
    throw error;
  }
}

/**
 * Obtiene todas las clasificaciones de un insumo específico
 */

/**
 * Crea una nueva clasificación
 */
export const createClasificacion = async (data: Partial<ClasificacionInsumo>): Promise<ClasificacionInsumo> => {
  try {
    const response = await api.post<ClasificacionInsumo>('/preoperacion/clasificaciones/', data);
    return response;
  } catch (error) {
    console.error('Error al crear clasificación:', error);
    throw error;
  }
}

/**
 * Actualiza una clasificación existente
 */
export const updateClasificacion = async (id: number, data: Partial<ClasificacionInsumo>): Promise<ClasificacionInsumo> => {
  try {
    const response = await api.put<ClasificacionInsumo>(`/preoperacion/clasificaciones/${id}/`, data);
    return response;
  } catch (error) {
    console.error(`Error al actualizar clasificación ${id}:`, error);
    throw error;
  }
}

/**
 * Elimina una clasificación
 */
export const deleteClasificacion = async (id: number): Promise<void> => {
  try {
    await api.delete(`/preoperacion/clasificaciones/${id}/`);
  } catch (error) {
    console.error(`Error al eliminar clasificación ${id}:`, error);
    throw error;
  }
}

// --------------------- DETALLES DE INSUMO ---------------------

/**
 * Obtiene todos los detalles de insumo con opción de filtrado
 */
export const getDetalles = async (params = {}): Promise<DetalleInsumo[]> => {
  try {
    const response = await api.get<PaginatedResponse<DetalleInsumo>>('/preoperacion/detalles-insumo/', { params });
    return response.results || [];
  } catch (error) {
    console.error('Error al obtener detalles:', error);
    throw error;
  }
}

/**
 * Obtiene un detalle específico por su ID
 */
export const getDetalleById = async (id: number): Promise<DetalleInsumo> => {
  try {
    const response = await api.get<DetalleInsumo>(`/preoperacion/detalles-insumo/${id}/`);
    return response;
  } catch (error) {
    console.error(`Error al obtener detalle ${id}:`, error);
    throw error;
  }
}

/**
 * Obtiene todos los detalles de una clasificación específica
 */
export const getDetallesByClasificacion = async (clasificacionId: number): Promise<DetalleInsumo[]> => {
  try {
    const response = await api.get<DetalleInsumo[]>(`/preoperacion/clasificaciones/${clasificacionId}/detalles/`);
    return response;
  } catch (error) {
    console.error(`Error al obtener detalles de clasificación ${clasificacionId}:`, error);
    throw error;
  }
}

/**
 * Crea un nuevo detalle de insumo
 */
export const createDetalle = async (data: Partial<DetalleInsumo>): Promise<DetalleInsumo> => {
  try {
    const response = await api.post<DetalleInsumo>('/preoperacion/detalles-insumo/', data);
    return response;
  } catch (error) {
    console.error('Error al crear detalle:', error);
    throw error;
  }
}

/**
 * Actualiza un detalle existente
 */
export const updateDetalle = async (id: number, data: Partial<DetalleInsumo>): Promise<DetalleInsumo> => {
  try {
    const response = await api.put<DetalleInsumo>(`/preoperacion/detalles-insumo/${id}/`, data);
    return response;
  } catch (error) {
    console.error(`Error al actualizar detalle ${id}:`, error);
    throw error;
  }
}

/**
 * Elimina un detalle
 */
export const deleteDetalle = async (id: number): Promise<void> => {
  try {
    await api.delete(`/preoperacion/detalles-insumo/${id}/`);
  } catch (error) {
    console.error(`Error al eliminar detalle ${id}:`, error);
    throw error;
  }
}

// --------------------- ARCHIVOS PRE-OPERACIÓN ---------------------

/**
 * Obtiene todos los archivos de una clasificación específica
 */
// Busca esta función en tu archivo insumos.ts y reemplázala por esta versión
export const getArchivosByClasificacion = async (clasificacionId: number): Promise<any[]> => {
  try {
    const response = await api.get<any>(`/preoperacion/clasificaciones/${clasificacionId}/archivos-pre/`);
    
    // Asegurarnos de que siempre devolvemos un array
    if (Array.isArray(response)) {
      return response;
    } else if (response && typeof response === 'object') {
      // Verificar si tiene una propiedad results o data
      if (Array.isArray(response.results)) {
        return response.results;
      } 
      if (Array.isArray(response.data)) {
        return response.data;
      }
      // Si es un objeto único, devolverlo en un array
      return [response];
    }
    
    // Si la respuesta no es un objeto iterable, devolvemos un array vacío
    return [];
  } catch (error) {
    console.error(`Error al obtener archivos para clasificación ${clasificacionId}:`, error);
    // En caso de error, devolvemos un array vacío
    return [];
  }
};

/**
 * Obtiene un archivo específico por su ID
 */
export const getArchivoById = async (id: number): Promise<any> => {
  try {
    const response = await api.get<any>(`/preoperacion/archivos-pre/${id}/`);
    return response;
  } catch (error) {
    console.error(`Error al obtener archivo ${id}:`, error);
    throw error;
  }
}

/**
 * Crea un nuevo archivo para una clasificación
 */
export const createArchivo = async (data: any): Promise<any> => {
  try {
    const response = await api.post<any>('/preoperacion/archivos-pre/', data);
    return response;
  } catch (error) {
    console.error('Error al crear archivo:', error);
    throw error;
  }
}

/**
 * Actualiza un archivo existente
 */
export const updateArchivo = async (id: number, data: any): Promise<any> => {
  try {
    const response = await api.put<any>(`/preoperacion/archivos-pre/${id}/`, data);
    return response;
  } catch (error) {
    console.error(`Error al actualizar archivo ${id}:`, error);
    throw error;
  }
}

/**
 * Elimina un archivo
 */
export const deleteArchivo = async (id: number): Promise<void> => {
  try {
    await api.delete(`/preoperacion/archivos-pre/${id}/`);
  } catch (error) {
    console.error(`Error al eliminar archivo ${id}:`, error);
    throw error;
  }
}

// --------------------- CONCEPTOS ---------------------

/**
 * Obtiene todos los conceptos
 */
export const getConceptos = async (params = {}): Promise<Concepto[]> => {
  try {
    const response = await api.get<PaginatedResponse<Concepto>>('/preoperacion/conceptos/', { params });
    return response.results || [];
  } catch (error) {
    throw error;
  }
}

// --------------------- OTROS CATÁLOGOS ---------------------

/**
 * Obtiene todas las categorías
 */
export const getCategorias = async (): Promise<any[]> => {
  try {
    const response = await api.get<PaginatedResponse<any>>('/preoperacion/categorias/');
    return response.results || [];
  } catch (error) {
    console.error('Error al obtener categorías:', error);
    throw error;
  }
}

/**
 * Obtiene todos los tipos de insumos
 */
export const getTiposInsumo = async (): Promise<any[]> => {
  try {
    const response = await api.get<PaginatedResponse<any>>('/preoperacion/tipos-insumo/');
    return response.results || [];
  } catch (error) {
    console.error('Error al obtener tipos de insumo:', error);
    throw error;
  }
}

/**
 * Obtiene todas las entidades
 */
export const getEntidades = async (): Promise<any[]> => {
  try {
    const response = await api.get<PaginatedResponse<any>>('/preoperacion/entidades/');
    return response.results || [];
  } catch (error) {
    console.error('Error al obtener entidades:', error);
    throw error;
  }
}

/**
 * Obtiene todos los formatos
 */
export const getFormatos = async (): Promise<any[]> => {
  try {
    const response = await api.get<PaginatedResponse<any>>('/preoperacion/tipos-formato/');
    return response.results || [];
  } catch (error) {
    console.error('Error al obtener formatos:', error);
    throw error;
  }
}

/**
 * Obtiene todas las zonas
 */
export const getZonas = async (): Promise<any[]> => {
  try {
    const response = await api.get<PaginatedResponse<any>>('/preoperacion/zonas/');
    return response.results || [];
  } catch (error) {
    console.error('Error al obtener zonas:', error);
    throw error;
  }
}

/**
 * Obtiene todos los usuarios
 */
export const getUsuarios = async (): Promise<any[]> => {
  // Lista de endpoints posibles en orden de prioridad
  const endpoints = [
    '/preoperacion/usuarios/',
    '/usuarios/',
    '/preoperacion/profesionales-seguimiento/',
    '/auth/users/',
    '/api/users/'
  ];
  
  for (const endpoint of endpoints) {
    try {
      console.log(`Intentando cargar usuarios desde: ${endpoint}`);
      const response = await api.get<PaginatedResponse<any>>(endpoint);
      
      const usuarios = response.results || response || [];
      
      if (Array.isArray(usuarios) && usuarios.length > 0) {
        console.log(`✅ Usuarios cargados exitosamente desde ${endpoint}: ${usuarios.length} usuarios`);
        return usuarios;
      }
    } catch (error: any) {
      console.warn(`❌ Endpoint ${endpoint} falló:`, error.response?.status, error.message);
      // Continuar con el siguiente endpoint
    }
  }
  
  // Si ningún endpoint funciona, retornar array vacío
  console.warn('⚠️ Ningún endpoint de usuarios disponible, retornando array vacío');
  return [];
};

/**
 * Función auxiliar para obtener usuarios de manera segura (sin lanzar errores)
 */


/**
 * Función mejorada para obtener detalles por insumo
 */
export const getDetallesByInsumo = async (insumoId: number): Promise<any[]> => {
  try {
    // Intentar primera opción: endpoint directo por insumo
    const response = await api.get<PaginatedResponse<any>>(`/preoperacion/insumos/${insumoId}/detalles/`);
    return response.results || response || [];
  } catch (error) {
    console.warn('Endpoint directo de detalles no disponible, usando filtro...');
    
    try {
      // Fallback: usar filtro en endpoint general
      const response = await api.get<PaginatedResponse<any>>('/preoperacion/detalles-insumo/', {
        params: { cod_insumo: insumoId }
      });
      return response.results || response || [];
    } catch (fallbackError) {
      console.error('Error obteniendo detalles:', fallbackError);
      return [];
    }
  }
};

/**
 * Función mejorada para obtener clasificaciones por insumo
 */
export const getClasificacionesByInsumo = async (insumoId: number): Promise<any[]> => {
  try {
    // Intentar primera opción: endpoint directo por insumo
    const response = await api.get<PaginatedResponse<any>>(`/preoperacion/insumos/${insumoId}/clasificaciones/`);
    return response.results || response || [];
  } catch (error) {
    console.warn('Endpoint directo de clasificaciones no disponible, usando filtro...');
    
    try {
      // Fallback: usar filtro en endpoint general
      const response = await api.get<PaginatedResponse<any>>('/preoperacion/clasificaciones/', {
        params: { cod_insumo: insumoId }
      });
      return response.results || response || [];
    } catch (fallbackError) {
      console.error('Error obteniendo clasificaciones:', fallbackError);
      return [];
    }
  }
};
/**
 * Obtiene estados de insumos
 */
export const getEstadosInsumo = async (): Promise<any[]> => {
  try {
    const response = await api.get<PaginatedResponse<any>>('/preoperacion/estados-insumo/');
    return response.results || [];
  } catch (error) {
    console.error('Error al obtener estados de insumo:', error);
    throw error;
  }
}

/**
 * Obtiene profesionales de seguimiento
 */
export const getProfesionalesSeguimiento = async (): Promise<any[]> => {
  try {
    const response = await api.get<PaginatedResponse<any>>('/preoperacion/profesionales-seguimiento/');
    return response.results || [];
  } catch (error) {
    console.error('Error al obtener profesionales de seguimiento:', error);
    throw error;
  }
}

export const getMecanismosGenerales = async (): Promise<any[]> => {
  try {
    const response = await api.get<PaginatedResponse<any>>('/preoperacion/mecanismos-general/');
    return response.results || [];
  } catch (error) {
    console.error('Error al obtener mecanismos generales:', error);
    throw error;
  }
}

export const getMecanismosDetalle = async (): Promise<any[]> => {
  try {
    const response = await api.get<PaginatedResponse<any>>('/preoperacion/mecanismos-detalle/');
    return response.results || [];
  } catch (error) {
    console.error('Error al obtener mecanismos detalle:', error);
    throw error;
  }
}

export const getMecanismosOperacion = async (): Promise<any[]> => {
  try {
    const response = await api.get<PaginatedResponse<any>>('/preoperacion/mecanismos-operacion/');
    return response.results || [];
  } catch (error) {
    console.error('Error al obtener mecanismos operación:', error);
    throw error;
  }
}

export const getAlcancesOperacion = async (): Promise<any[]> => {
  try {
    const response = await api.get<PaginatedResponse<any>>('/preoperacion/alcances-operacion/');
    return response.results || [];
  } catch (error) {
    console.error('Error al obtener alcances operación:', error);
    throw error;
  }
}

export const getGrupos = async (): Promise<any[]> => {
  try {
    const response = await api.get<PaginatedResponse<any>>('/preoperacion/grupos/');
    return response.results || [];
  } catch (error) {
    console.error('Error al obtener grupos:', error);
    throw error;
  }
}

export const getTerritoriales = async (): Promise<any[]> => {
  try {
    const response = await api.get<PaginatedResponse<any>>('/preoperacion/territoriales/');
    return response.results || [];
  } catch (error) {
    console.error('Error al obtener territoriales:', error);
    throw error;
  }
}

// Función para obtener todos los resultados paginados
async function getAllPaginatedResults<T>(endpoint: string, params = {}): Promise<T[]> {
  try {
    let allResults: T[] = [];
    let nextUrl: string | null = null;
    
    // Primera solicitud
    const initialParams = { ...params, page_size: 100 }; // Pedir 100 por página para reducir el número de solicitudes
    const initialResponse = await api.get<PaginatedResponse<T>>(endpoint, { params: initialParams });
    
    allResults = [...(initialResponse.results || [])];
    nextUrl = initialResponse.next;
    
    // Obtener páginas adicionales si existen
    while (nextUrl) {
      // Extraer la URL relativa de la URL completa (si es necesario)
      const relativeUrl = nextUrl.includes(api.defaults.baseURL || '') 
        ? nextUrl.replace(api.defaults.baseURL || '', '') 
        : nextUrl;
      
      const nextResponse = await api.get<PaginatedResponse<T>>(relativeUrl);
      allResults = [...allResults, ...(nextResponse.results || [])];
      nextUrl = nextResponse.next;
    }
    
    return allResults;
  } catch (error) {
    console.error(`Error obteniendo todos los resultados de ${endpoint}:`, error);
    throw error;
  }
}

// Usar esta función para obtener todos los departamentos
export const getDepartamentos = async (): Promise<any[]> => {
  try {
    return await getAllPaginatedResults('/preoperacion/departamentos/');
  } catch (error) {
    console.error('Error al obtener departamentos:', error);
    throw error;
  }
}

// Usar para obtener todos los municipios
export const getMunicipios = async (params = {}): Promise<any[]> => {
  try {
    return await getAllPaginatedResults('/preoperacion/municipios/', params);
  } catch (error) {
    console.error('Error al obtener municipios:', error);
    throw error;
  }
}