import api from './config';
import type { ClasificacionInsumo } from '@/models/municipio';

// Obtener clasificaciones por insumo
export const getClasificacionesByInsumo = async (insumoId: number): Promise<ClasificacionInsumo[]> => {
  try {
    const response = await api.get<ClasificacionInsumo[]>(`/preoperacion/insumos/${insumoId}/clasificaciones/`);
    return response || [];
  } catch (error) {
    console.error('Error al obtener clasificaciones por insumo:', error);
    throw error;
  }
};

// Obtener una clasificación por ID
export const getClasificacionById = async (id: number): Promise<ClasificacionInsumo> => {
  try {
    const response = await api.get<ClasificacionInsumo>(`/preoperacion/clasificaciones/${id}/`);
    return response;
  } catch (error) {
    console.error('Error al obtener clasificación:', error);
    throw error;
  }
};

// Crear una nueva clasificación
export const createClasificacion = async (data: Partial<ClasificacionInsumo>): Promise<ClasificacionInsumo> => {
  try {
    const response = await api.post<ClasificacionInsumo>('/preoperacion/clasificaciones/', data);
    return response;
  } catch (error) {
    console.error('Error al crear clasificación:', error);
    throw error;
  }
};

// Actualizar una clasificación existente
export const updateClasificacion = async (id: number, data: Partial<ClasificacionInsumo>): Promise<ClasificacionInsumo> => {
  try {
    const response = await api.put<ClasificacionInsumo>(`/preoperacion/clasificaciones/${id}/`, data);
    return response;
  } catch (error) {
    console.error('Error al actualizar clasificación:', error);
    throw error;
  }
};

// Eliminar una clasificación
export const deleteClasificacion = async (id: number): Promise<void> => {
  try {
    await api.delete(`/preoperacion/clasificaciones/${id}/`);
  } catch (error) {
    console.error('Error al eliminar clasificación:', error);
    throw error;
  }
};