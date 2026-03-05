import api from './config';

// Interface para estadísticas del dashboard
export interface EstadisticasDashboard {
  total_municipios_pre: number;
  total_municipios_post: number;
  total_archivos_pre: number;
  total_archivos_post: number;
  total_territoriales: number;
  total_profesionales_las: number;
  total_profesionales_pas: number;
  total_municipios_sin_insumos: number;
}

// Obtener estadísticas para el dashboard
export const getEstadisticasDashboard = async (): Promise<EstadisticasDashboard> => {
  try {
    const response = await api.get<EstadisticasDashboard>('/preoperacion/estadisticas/dashboard/');
    return response;
  } catch (error) {
    console.error('Error al obtener estadísticas del dashboard:', error);
    // Lanzar error para que se maneje en la capa superior
    throw error;
  }
};

// Interface para estadísticas generales
export interface Estadisticas {
  total_municipios: number;
  total_insumos: number;
  total_clasificaciones: number;
  total_detalles: number;
  total_conceptos: number;
  [key: string]: any;
}

// Obtener estadísticas generales del sistema
export const getEstadisticasGenerales = async (): Promise<Estadisticas> => {
  try {
    const response = await api.get<Estadisticas>('/preoperacion/estadisticas/');
    return response;
  } catch (error) {
    console.error('Error al obtener estadísticas generales:', error);
    throw error;
  }
};

// Obtener estadísticas específicas de insumos
export const getEstadisticasInsumos = async (): Promise<any> => {
  try {
    const response = await api.get<any>('/preoperacion/estadisticas/insumos/');
    return response;
  } catch (error) {
    console.error('Error al obtener estadísticas de insumos:', error);
    // Retornar valores predeterminados en caso de error
    return {
      totalDetalles: 0,
      detallesPendientes: 0,
      totalConceptos: 0,
      conceptosPendientes: 0
    };
  }
};

// Obtener estadísticas por municipio
export const getEstadisticasPorMunicipio = async (municipioId: number): Promise<any> => {
  try {
    const response = await api.get<any>(`/preoperacion/estadisticas/municipios/${municipioId}/`);
    return response;
  } catch (error) {
    console.error('Error al obtener estadísticas por municipio:', error);
    throw error;
  }
};