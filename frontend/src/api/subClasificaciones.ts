import api from './config';

export interface SubClasificacionFuenteSecundaria {
  cod_sub_clasificacion: number;
  dominio: string;
  nombre: string;
  orden: number;
}

export const subClasificacionesApi = {
  /**
   * Obtener sub-clasificaciones filtradas por dominio
   * @param dominio Código del dominio (ej: "ANT", "IGAC", "DETERMINANTE AMBIENTAL")
   */
  porDominio: async (dominio: string): Promise<SubClasificacionFuenteSecundaria[]> => {
    try {
      if (!dominio || dominio.trim() === '') {
        return [];
      }
      const response = await api.get('/preoperacion/sub-clasificaciones-secundarias/', {
        params: { dominio }
      });
      const data = response.results || response;
      return Array.isArray(data) ? data : [];
    } catch (error) {
      console.error('Error al obtener sub-clasificaciones:', error);
      return [];
    }
  },

  getAll: async (): Promise<SubClasificacionFuenteSecundaria[]> => {
    try {
      const response = await api.get('/preoperacion/sub-clasificaciones-secundarias/');
      const data = response.results || response;
      return Array.isArray(data) ? data : [];
    } catch (error) {
      console.error('Error al obtener sub-clasificaciones:', error);
      return [];
    }
  }
};

export default subClasificacionesApi;
