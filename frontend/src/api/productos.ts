import api from './config';
import { API_URL } from './config';
import { getMunicipios } from './municipios';
import { getDepartamentos } from './departamentos';

// Interface para Componente Post
export interface ComponentePost {
  id_componente: number;
  nombre_componente: string;
}

// Interface para Disposición Post
export interface DisposicionPost {
  id_disposicion: number;
  cod_municipio: number;
  id_componente: number;
  dispuesto: boolean;
  fecha_disposicion?: string;
  ruta_acceso?: string;
  evaluado: boolean;
  aprobado: boolean;
  observaciones?: string;
}

// Interface para Archivo Post
export interface ArchivoPost {
  id_archivo: number;
  id_disposicion: number;
  nombre_archivo: string;
  ruta_completa: string;
  fecha_disposicion?: string;
  observacion?: string;
}

// Interface para Municipio con Productos
export interface MunicipioConProductos {
  cod_municipio: number;
  nom_municipio: string;
  cod_depto: number;
  nom_territorial?: string;
  total_productos: number;
  aprobados: number;
  pendientes: number;
}

// Obtener municipios con productos (disposiciones)
export const getMunicipiosConProductos = async (filtros?: any): Promise<MunicipioConProductos[]> => {
  try {
    const params = new URLSearchParams();
    if (filtros?.departamento) params.append('departamento', filtros.departamento);
    if (filtros?.municipio) params.append('municipio', filtros.municipio);
    if (filtros?.territorial) params.append('territorial', filtros.territorial);
    
    const queryString = params.toString();
    const url = queryString ? `/postoperacion/municipios-con-productos/?${queryString}` : '/postoperacion/municipios-con-productos/';
    
    const response = await api.get<MunicipioConProductos[]>(url);
    return Array.isArray(response) ? response : [];
  } catch (error) {
    console.error('Error al obtener municipios con productos:', error);
    throw error;
  }
};

// Obtener componentes
export const getComponentes = async (): Promise<ComponentePost[]> => {
  try {
    const response = await api.get<any>('/postoperacion/componentes/');
    
    // Manejar diferentes formatos de respuesta
    if (Array.isArray(response)) {
      return response;
    } else if (response && typeof response === 'object') {
      // Si la respuesta tiene una propiedad results (respuesta paginada)
      if (Array.isArray(response.results)) {
        return response.results;
      }
      // Si la respuesta tiene otra propiedad que contiene el array
      if (Array.isArray(response.data)) {
        return response.data;
      }
    }
    
    // Si no podemos obtener un array, devolver array vacío
    console.warn('Formato de respuesta inesperado para componentes:', response);
    return [];
  } catch (error) {
    console.error('Error al obtener componentes:', error);
    return [];
  }
};

// Obtener disposiciones por municipio
export const getDisposicionesByMunicipio = async (municipioId: number): Promise<DisposicionPost[]> => {
  try {
    const response = await api.get<any>(`/postoperacion/disposiciones/por_municipio/?municipio_id=${municipioId}`);
    
    // Asegurar que devolvemos un array
    if (Array.isArray(response)) {
      return response;
    } else if (response && typeof response === 'object') {
      if (Array.isArray(response.results)) {
        return response.results;
      }
      if (Array.isArray(response.data)) {
        return response.data;
      }
    }
    
    console.warn('Formato de respuesta inesperado para disposiciones:', response);
    return [];
  } catch (error) {
    console.error('Error al obtener disposiciones:', error);
    return [];
  }
};

// Obtener archivos por municipio
export const getArchivosByMunicipio = async (municipioId: number): Promise<ArchivoPost[]> => {
  try {
    // Primero obtenemos las disposiciones del municipio
    const disposiciones = await getDisposicionesByMunicipio(municipioId);
    
    // Luego obtenemos todos los archivos de esas disposiciones
    const archivosPromises = disposiciones.map(disp => 
      api.get<any>(`/postoperacion/archivos/por_disposicion/?disposicion_id=${disp.id_disposicion}`)
    );
    
    const archivosArrays = await Promise.all(archivosPromises);
    
    // Aplanar el array de arrays, asegurándose de que cada elemento es un array
    const archivosFlat = archivosArrays.flatMap(response => {
      if (Array.isArray(response)) {
        return response;
      } else if (response && typeof response === 'object') {
        if (Array.isArray(response.results)) {
          return response.results;
        }
        if (Array.isArray(response.data)) {
          return response.data;
        }
      }
      return [];
    });
    
    return archivosFlat;
  } catch (error) {
    console.error('Error al obtener archivos:', error);
    return [];
  }
};

// Actualizar disposición
export const updateDisposicion = async (id: number, data: Partial<DisposicionPost>): Promise<DisposicionPost> => {
  try {
    const response = await api.patch<DisposicionPost>(`/postoperacion/disposiciones/${id}/`, data);
    return response;
  } catch (error) {
    console.error('Error al actualizar disposición:', error);
    throw error;
  }
};

// Actualizar archivo
export const updateArchivo = async (id: number, data: Partial<ArchivoPost>): Promise<ArchivoPost> => {
  try {
    const response = await api.patch<ArchivoPost>(`/postoperacion/archivos/${id}/`, data);
    return response;
  } catch (error) {
    console.error('Error al actualizar archivo:', error);
    throw error;
  }
};

// Obtener estadísticas de productos
export const getEstadisticasProductos = async (): Promise<any> => {
  try {
    const response = await api.get('/postoperacion/disposiciones/resumen_estado/');
    return response;
  } catch (error) {
    console.error('Error al obtener estadísticas:', error);
    throw error;
  }
};

// Exportar funciones de municipios y departamentos que también se usan en productos
export { getMunicipios, getDepartamentos };

// Obtener territoriales (si viene del módulo de preoperación)
export const getTerritoriales = async (): Promise<any[]> => {
  try {
    const response = await api.get<any>('/preoperacion/territoriales/');
    
    if (Array.isArray(response)) {
      return response;
    } else if (response && typeof response === 'object') {
      if (Array.isArray(response.results)) {
        return response.results;
      }
      if (Array.isArray(response.data)) {
        return response.data;
      }
    }
    
    console.warn('Formato de respuesta inesperado para territoriales:', response);
    return [];
  } catch (error) {
    console.error('Error al obtener territoriales:', error);
    return [];
  }
};