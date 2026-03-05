import api from './config';

export interface InfoAdministrativa {
  cod_info_admin: number;
  cod_municipio: number;
  id_gestor_catas?: string;
  gestor_prestador_servicio?: string;
  publicacion_year?: string;
  vigencia_rural?: string;
  vigencia_urbana?: string;
  estado_rural?: string;
  estado_urbano?: string;
  predios_rurales?: string;
  area_terreno_rural_m2?: string;
  area_terreno_rural_ha?: string;
  area_construida_rural_m2?: string;
  avaluo_rural?: string;
  predios_urbanos?: string;
  area_terreno_urbana_m2?: string;
  area_terreno_urbana_ha?: string;
  area_construida_urbana_m2?: string;
  avaluo_urbano_1?: string;
  avaluo_urbano_2?: string;
  total_predios?: string;
  total_area_terreno_m2?: string;
  total_area_terreno_ha?: string;
  total_area_construida_m2?: string;
  total_avaluos?: string;
  area_geografica_rural_ha?: string;
  area_geografica_urbana_ha?: string;
  area_rural_estados_catastrales_ha?: string;
  area_urbana_estados_catastrales_ha?: string;
  observacion?: string;
}

// Interface para crear/actualizar (campos principales del formulario)
export interface InfoAdministrativaForm {
  cod_municipio: string | number; // Puede venir como string del formulario
  id_gestor_catas?: string;
  gestor_prestador_servicio?: string;
  publicacion_year?: string;
  vigencia_rural?: string;
  vigencia_urbana?: string;
  estado_rural?: string;
  estado_urbano?: string;
  predios_rurales?: string;
  area_terreno_rural_m2?: string;
  area_terreno_rural_ha?: string;
  area_construida_rural_m2?: string;
  avaluo_rural?: string;
  predios_urbanos?: string;
  area_terreno_urbana_m2?: string;
  area_terreno_urbana_ha?: string;
  area_construida_urbana_m2?: string;
  avaluo_urbano_1?: string;
  avaluo_urbano_2?: string;
  total_predios?: string;
  total_area_terreno_m2?: string;
  total_area_terreno_ha?: string;
  total_area_construida_m2?: string;
  total_avaluos?: string;
  area_geografica_rural_ha?: string;
  area_geografica_urbana_ha?: string;
  area_rural_estados_catastrales_ha?: string;
  area_urbana_estados_catastrales_ha?: string;
  observacion?: string;
}

export const infoAdministrativaApi = {
  // =============== MÉTODOS EXISTENTES (MANTENER) ===============
  
  // Obtener toda la información administrativa
  getAll: async (): Promise<InfoAdministrativa[]> => {
    try {
      const response = await api.get('/preoperacion/info-administrativa/');
      
      // Si la respuesta es paginada
      if (response.results && Array.isArray(response.results)) {
        return response.results;
      }
      
      // Si es un array directo
      if (Array.isArray(response)) {
        return response;
      }
      
      return [];
    } catch (error) {
      console.error('Error al obtener información administrativa:', error);
      throw error;
    }
  },

  // Obtener información administrativa por municipio
  porMunicipio: async (cod_municipio: number): Promise<InfoAdministrativa | null> => {
    try {
      const response = await api.get('/preoperacion/info-administrativa/', {
        params: { cod_municipio }
      });
      
      // Si hay resultados, tomar el primero
      if (response.results && response.results.length > 0) {
        return response.results[0];
      }
      
      if (Array.isArray(response) && response.length > 0) {
        return response[0];
      }
      
      return null;
    } catch (error) {
      console.error('Error al obtener info administrativa del municipio:', error);
      return null;
    }
  },
  // 🆕 NUEVA FUNCIÓN: Obtener TODOS los registros por municipio
  todosPorMunicipio: async (cod_municipio: number): Promise<InfoAdministrativa[]> => {
    try {
      console.log('🔍 Obteniendo TODOS los registros de info administrativa para municipio:', cod_municipio);
      
      const response = await api.get('/preoperacion/info-administrativa/', {
        params: { cod_municipio }
      });
      
      // Si hay resultados, retornar TODOS
      if (response.results && Array.isArray(response.results)) {
        return response.results; // 🔥 RETORNAR TODOS, no solo el primero
      }
      
      if (Array.isArray(response)) {
        return response;
      }
      
      return [];
    } catch (error) {
      console.error('Error al obtener todos los registros de info administrativa del municipio:', error);
      return [];
    }
  },

  // =============== NUEVOS MÉTODOS CRUD ===============
  
  // 🆕 OBTENER información administrativa por ID específico
  getById: async (id: string | number): Promise<InfoAdministrativa> => {
    try {
      console.log('🔍 Obteniendo información administrativa por ID:', id);
      
      // Intentar diferentes endpoints
      let response;
      try {
        response = await api.get(`/preoperacion/info-administrativa/${id}/`);
      } catch (error1) {
        try {
          response = await api.get(`/preoperacion/info-administrativa/${id}`);
        } catch (error2) {
          response = await api.get(`/info-administrativa/${id}/`);
        }
      }
      
      console.log('✅ Información administrativa encontrada:', response);
      return response;
      
    } catch (error) {
      console.error('❌ Error al obtener información administrativa:', error);
      
      if (error.response?.status === 404) {
        throw new Error('Información administrativa no encontrada');
      } else {
        throw new Error(error.message || 'Error al obtener información administrativa');
      }
    }
  },

  // 🆕 CREAR nueva información administrativa
  create: async (data: InfoAdministrativaForm): Promise<InfoAdministrativa> => {
    try {
      console.log('📝 Creando información administrativa:', data);
      
      // Preparar datos asegurando tipos correctos
      const payload = {
        cod_municipio: parseInt(data.cod_municipio.toString()),
        id_gestor_catas: data.id_gestor_catas?.trim() || null,
        gestor_prestador_servicio: data.gestor_prestador_servicio?.trim() || null,
        publicacion_year: data.publicacion_year?.trim() || null,
        vigencia_rural: data.vigencia_rural?.trim() || null,
        vigencia_urbana: data.vigencia_urbana?.trim() || null,
        estado_rural: data.estado_rural?.trim() || null,
        estado_urbano: data.estado_urbano?.trim() || null,
        predios_rurales: data.predios_rurales?.trim() || null,
        area_terreno_rural_m2: data.area_terreno_rural_m2?.trim() || null,
        area_terreno_rural_ha: data.area_terreno_rural_ha?.trim() || null,
        area_construida_rural_m2: data.area_construida_rural_m2?.trim() || null,
        avaluo_rural: data.avaluo_rural?.trim() || null,
        predios_urbanos: data.predios_urbanos?.trim() || null,
        area_terreno_urbana_m2: data.area_terreno_urbana_m2?.trim() || null,
        area_terreno_urbana_ha: data.area_terreno_urbana_ha?.trim() || null,
        area_construida_urbana_m2: data.area_construida_urbana_m2?.trim() || null,
        avaluo_urbano_1: data.avaluo_urbano_1?.trim() || null,
        avaluo_urbano_2: data.avaluo_urbano_2?.trim() || null,
        total_predios: data.total_predios?.trim() || null,
        total_area_terreno_m2: data.total_area_terreno_m2?.trim() || null,
        total_area_terreno_ha: data.total_area_terreno_ha?.trim() || null,
        total_area_construida_m2: data.total_area_construida_m2?.trim() || null,
        total_avaluos: data.total_avaluos?.trim() || null,
        area_geografica_rural_ha: data.area_geografica_rural_ha?.trim() || null,
        area_geografica_urbana_ha: data.area_geografica_urbana_ha?.trim() || null,
        area_rural_estados_catastrales_ha: data.area_rural_estados_catastrales_ha?.trim() || null,
        area_urbana_estados_catastrales_ha: data.area_urbana_estados_catastrales_ha?.trim() || null,
        observacion: data.observacion?.trim() || null
      };
      
      // Validar datos antes de enviar
      if (!payload.cod_municipio || isNaN(payload.cod_municipio)) {
        throw new Error('Código de municipio es requerido y debe ser válido');
      }
      
      console.log('📤 Enviando payload:', payload);
      
      // Intentar diferentes endpoints hasta encontrar el correcto
      let response;
      try {
        // Opción 1: Endpoint directo
        response = await api.post('/preoperacion/info-administrativa/', payload);
      } catch (error1) {
        try {
          // Opción 2: Endpoint sin slash final
          response = await api.post('/preoperacion/info-administrativa', payload);
        } catch (error2) {
          try {
            // Opción 3: Endpoint alternativo
            response = await api.post('/info-administrativa/', payload);
          } catch (error3) {
            // Opción 4: Endpoint sin preoperacion
            response = await api.post('/info-administrativa', payload);
          }
        }
      }
      
      console.log('✅ Información administrativa creada exitosamente:', response);
      return response;
      
    } catch (error) {
      console.error('❌ Error al crear información administrativa:', error);
      
      // Manejo de errores específicos
      if (error.response?.status === 400) {
        const errorMsg = error.response.data?.detail || error.response.data?.message || 'Datos inválidos';
        throw new Error(`Error de validación: ${errorMsg}`);
      } else if (error.response?.status === 409) {
        throw new Error('Ya existe información administrativa para este municipio');
      } else if (error.response?.status === 500) {
        throw new Error('Error interno del servidor');
      } else {
        throw new Error(error.message || 'Error desconocido al crear información administrativa');
      }
    }
  },

  // 🆕 ACTUALIZAR información administrativa existente
  update: async (id: string | number, data: InfoAdministrativaForm): Promise<InfoAdministrativa> => {
    try {
      console.log('✏️ Actualizando información administrativa:', id, data);
      
      // Preparar datos asegurando tipos correctos
      const payload = {
        cod_municipio: parseInt(data.cod_municipio.toString()),
        id_gestor_catas: data.id_gestor_catas?.trim() || null,
        gestor_prestador_servicio: data.gestor_prestador_servicio?.trim() || null,
        publicacion_year: data.publicacion_year?.trim() || null,
        vigencia_rural: data.vigencia_rural?.trim() || null,
        vigencia_urbana: data.vigencia_urbana?.trim() || null,
        estado_rural: data.estado_rural?.trim() || null,
        estado_urbano: data.estado_urbano?.trim() || null,
        predios_rurales: data.predios_rurales?.trim() || null,
        area_terreno_rural_m2: data.area_terreno_rural_m2?.trim() || null,
        area_terreno_rural_ha: data.area_terreno_rural_ha?.trim() || null,
        area_construida_rural_m2: data.area_construida_rural_m2?.trim() || null,
        avaluo_rural: data.avaluo_rural?.trim() || null,
        predios_urbanos: data.predios_urbanos?.trim() || null,
        area_terreno_urbana_m2: data.area_terreno_urbana_m2?.trim() || null,
        area_terreno_urbana_ha: data.area_terreno_urbana_ha?.trim() || null,
        area_construida_urbana_m2: data.area_construida_urbana_m2?.trim() || null,
        avaluo_urbano_1: data.avaluo_urbano_1?.trim() || null,
        avaluo_urbano_2: data.avaluo_urbano_2?.trim() || null,
        total_predios: data.total_predios?.trim() || null,
        total_area_terreno_m2: data.total_area_terreno_m2?.trim() || null,
        total_area_terreno_ha: data.total_area_terreno_ha?.trim() || null,
        total_area_construida_m2: data.total_area_construida_m2?.trim() || null,
        total_avaluos: data.total_avaluos?.trim() || null,
        area_geografica_rural_ha: data.area_geografica_rural_ha?.trim() || null,
        area_geografica_urbana_ha: data.area_geografica_urbana_ha?.trim() || null,
        area_rural_estados_catastrales_ha: data.area_rural_estados_catastrales_ha?.trim() || null,
        area_urbana_estados_catastrales_ha: data.area_urbana_estados_catastrales_ha?.trim() || null,
        observacion: data.observacion?.trim() || null
      };
      
      console.log('📤 Enviando payload de actualización:', payload);
      
      // Intentar diferentes endpoints
      let response;
      try {
        // Opción 1: PUT con ID
        response = await api.put(`/preoperacion/info-administrativa/${id}/`, payload);
      } catch (error1) {
        try {
          // Opción 2: PATCH con ID
          response = await api.patch(`/preoperacion/info-administrativa/${id}/`, payload);
        } catch (error2) {
          try {
            // Opción 3: PUT sin slash
            response = await api.put(`/preoperacion/info-administrativa/${id}`, payload);
          } catch (error3) {
            // Opción 4: Endpoint alternativo
            response = await api.put(`/info-administrativa/${id}/`, payload);
          }
        }
      }
      
      console.log('✅ Información administrativa actualizada exitosamente:', response);
      return response;
      
    } catch (error) {
      console.error('❌ Error al actualizar información administrativa:', error);
      
      if (error.response?.status === 404) {
        throw new Error('Información administrativa no encontrada');
      } else if (error.response?.status === 400) {
        const errorMsg = error.response.data?.detail || error.response.data?.message || 'Datos inválidos';
        throw new Error(`Error de validación: ${errorMsg}`);
      } else {
        throw new Error(error.message || 'Error desconocido al actualizar información administrativa');
      }
    }
  },

  // 🆕 ELIMINAR información administrativa
  delete: async (id: string | number): Promise<void> => {
    try {
      console.log('🗑️ Eliminando información administrativa:', id);
      
      // Intentar diferentes endpoints
      try {
        await api.delete(`/preoperacion/info-administrativa/${id}/`);
      } catch (error1) {
        try {
          await api.delete(`/preoperacion/info-administrativa/${id}`);
        } catch (error2) {
          await api.delete(`/info-administrativa/${id}/`);
        }
      }
      
      console.log('✅ Información administrativa eliminada exitosamente');
      
    } catch (error) {
      console.error('❌ Error al eliminar información administrativa:', error);
      
      if (error.response?.status === 404) {
        throw new Error('Información administrativa no encontrada');
      } else if (error.response?.status === 409) {
        throw new Error('No se puede eliminar: la información administrativa tiene dependencias');
      } else {
        throw new Error(error.message || 'Error al eliminar información administrativa');
      }
    }
  }
};

// =============== EXPORTACIONES PARA COMPATIBILIDAD ===============
export const getTodosInfoAdministrativaPorMunicipio = infoAdministrativaApi.todosPorMunicipio;
// Mantener las funciones existentes para compatibilidad con código actual
export const getInfoAdministrativa = infoAdministrativaApi.getAll;
export const getInfoAdministrativaByMunicipio = infoAdministrativaApi.porMunicipio;

// Nuevas exportaciones
export const getInfoAdministrativaById = infoAdministrativaApi.getById;
export const createInfoAdministrativa = infoAdministrativaApi.create;
export const updateInfoAdministrativa = infoAdministrativaApi.update;
export const deleteInfoAdministrativa = infoAdministrativaApi.delete;

// ✅ EXPORTACIÓN POR DEFECTO
export default infoAdministrativaApi;