import api from './config';
import type { AuditoriaItem } from '@/models/auditoria';

// Obtener registros de auditoría con filtros opcionales
export const getRegistrosAuditoria = async (params = {}): Promise<AuditoriaItem[]> => {
  try {
    // Asegurarse de que la URL es correcta
    const response = await api.get('/preoperacion/auditoria/', { params });
    
    // Verificar si la respuesta tiene formato paginado o es un array directo
    if (response.results && Array.isArray(response.results)) {
      return response.results;
    } else if (Array.isArray(response)) {
      return response;
    }
    
    console.warn('Formato de respuesta inesperado:', response);
    return [];
  } catch (error) {
    console.error('Error al obtener registros de auditoría:', error);
    throw error;
  }
};

// Obtener un registro específico por ID
export const getRegistroAuditoria = async (id: number): Promise<AuditoriaItem> => {
  try {
    const response = await api.get(`/preoperacion/auditoria/${id}/`);
    return response;
  } catch (error) {
    console.error('Error al obtener registro de auditoría:', error);
    throw error;
  }
};

// Obtener últimas actividades (para el dashboard)
export const getUltimasActividades = async (limit = 5): Promise<AuditoriaItem[]> => {
  try {
    const response = await api.get('/preoperacion/auditoria/', { 
      params: { 
        limit, 
        ordering: '-fecha_hora' 
      } 
    });
    
    // Verificar si la respuesta es paginada
    if (response.results) {
      return response.results;
    }
    
    // Si no es paginada, devolver la respuesta directamente
    return Array.isArray(response) ? response : [];
  } catch (error) {
    console.error('Error al obtener últimas actividades:', error);
    throw error;
  }
};