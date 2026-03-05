import api from './config'
import type { ComponentePost, DisposicionPost, ArchivoPost } from '@/models/municipio'

// Tipo para manejador de respuestas paginadas
type PaginatedResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Obtener todos los componentes post
export const getComponentesPost = async (): Promise<ComponentePost[]> => {
  try {
    const response = await api.get<PaginatedResponse<ComponentePost>>('/postoperacion/componentes/');
    return response.results || [];
  } catch (error) {
    throw error;
  }
}

// Obtener un componente post por ID
export const getComponentePostById = async (id: number): Promise<ComponentePost> => {
  try {
    const response = await api.get<ComponentePost>(`/postoperacion/componentes/${id}/`);
    return response;
  } catch (error) {
    throw error;
  }
}

// Crear un nuevo componente post (requiere autenticación)
export const createComponentePost = async (data: Partial<ComponentePost>): Promise<ComponentePost> => {
  try {
    const response = await api.post<ComponentePost>('/postoperacion/componentes/', data);
    return response;
  } catch (error) {
    throw error;
  }
}

// Actualizar un componente post (requiere autenticación)
export const updateComponentePost = async (id: number, data: Partial<ComponentePost>): Promise<ComponentePost> => {
  try {
    const response = await api.put<ComponentePost>(`/postoperacion/componentes/${id}/`, data);
    return response;
  } catch (error) {
    throw error;
  }
}

// Eliminar un componente post (requiere autenticación)
export const deleteComponentePost = async (id: number): Promise<void> => {
  try {
    await api.delete(`/postoperacion/componentes/${id}/`);
  } catch (error) {
    throw error;
  }
}

// Obtener todas las disposiciones post
export const getDisposicionesPost = async (params = {}): Promise<DisposicionPost[]> => {
  try {
    const response = await api.get<PaginatedResponse<DisposicionPost>>('/postoperacion/disposiciones/', { params });
    return response.results || [];
  } catch (error) {
    throw error;
  }
}

// Obtener disposiciones por municipio
export const getDisposicionesByMunicipio = async (municipioId: number): Promise<DisposicionPost[]> => {
  try {
    const response = await api.get<DisposicionPost[]>(`/postoperacion/disposiciones/por_municipio/?municipio_id=${municipioId}`);
    return response;
  } catch (error) {
    throw error;
  }
}

// Obtener una disposición post por ID
export const getDisposicionPostById = async (id: number): Promise<DisposicionPost> => {
  try {
    const response = await api.get<DisposicionPost>(`/postoperacion/disposiciones/${id}/`);
    return response;
  } catch (error) {
    throw error;
  }
}

// Crear una nueva disposición post (requiere autenticación)
export const createDisposicionPost = async (data: Partial<DisposicionPost>): Promise<DisposicionPost> => {
  try {
    const response = await api.post<DisposicionPost>('/postoperacion/disposiciones/', data);
    return response;
  } catch (error) {
    throw error;
  }
}

// Actualizar una disposición post (requiere autenticación)
export const updateDisposicionPost = async (id: number, data: Partial<DisposicionPost>): Promise<DisposicionPost> => {
  try {
    const response = await api.put<DisposicionPost>(`/postoperacion/disposiciones/${id}/`, data);
    return response;
  } catch (error) {
    throw error;
  }
}

// Eliminar una disposición post (requiere autenticación)
export const deleteDisposicionPost = async (id: number): Promise<void> => {
  try {
    await api.delete(`/postoperacion/disposiciones/${id}/`);
  } catch (error) {
    throw error;
  }
}

// Obtener resumen de estados de disposiciones
export const getResumenEstadoDisposiciones = async (): Promise<any> => {
  try {
    const response = await api.get<any>('/postoperacion/disposiciones/resumen_estado/');
    return response;
  } catch (error) {
    throw error;
  }
}

// Obtener estadísticas detalladas
export const getEstadisticasDisposiciones = async (): Promise<any> => {
  try {
    const response = await api.get<any>('/postoperacion/disposiciones/estadisticas/');
    return response;
  } catch (error) {
    throw error;
  }
}

// Obtener archivos por disposición
export const getArchivosByDisposicion = async (disposicionId: number): Promise<ArchivoPost[]> => {
  try {
    const response = await api.get<ArchivoPost[]>(`/postoperacion/archivos/por_disposicion/?disposicion_id=${disposicionId}`);
    return response;
  } catch (error) {
    throw error;
  }
}

// Crear un nuevo archivo (requiere autenticación)
export const createArchivoPost = async (data: Partial<ArchivoPost>): Promise<ArchivoPost> => {
  try {
    const response = await api.post<ArchivoPost>('/postoperacion/archivos/', data);
    return response;
  } catch (error) {
    throw error;
  }
}

// Eliminar un archivo (requiere autenticación)
export const deleteArchivoPost = async (id: number): Promise<void> => {
  try {
    await api.delete(`/postoperacion/archivos/${id}/`);
  } catch (error) {
    throw error;
  }
}