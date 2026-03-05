import api from './config';

export interface CentroPoblado {
  cod_centro_poblado: string;
  cod_municipio: number;
  nom_centro_poblado: string;
  area_oficial_ha?: string;
}

// Interface para crear/actualizar
export interface CentroPobladoForm {
  cod_centro_poblado: string;
  cod_municipio: string | number; // Puede venir como string del formulario
  nom_centro_poblado: string;
  area_oficial_ha?: string;
}

export const centrosPobladosApi = {
  // Obtener centros poblados por municipio (método existente)
  porMunicipio: async (municipioId: number): Promise<CentroPoblado[]> => {
    try {
      // Validar que sea un número
      if (!municipioId || isNaN(municipioId)) {
        console.error('ID de municipio inválido para centros poblados:', municipioId);
        return [];
      }
      
      const response = await api.get(`/preoperacion/centros-poblados/municipio/${municipioId}/`);
      
      // Asegurar que devolvemos un array
      return Array.isArray(response) ? response : [];
    } catch (error) {
      console.error('Error al obtener centros poblados:', error);
      return [];
    }
  },

  // 🆕 CREAR nuevo centro poblado
  create: async (data: CentroPobladoForm): Promise<CentroPoblado> => {
    try {
      console.log('📝 Creando centro poblado:', data);
      
      // Preparar datos asegurando tipos correctos
      const payload = {
        cod_centro_poblado: data.cod_centro_poblado.toString().trim(),
        cod_municipio: parseInt(data.cod_municipio.toString()),
        nom_centro_poblado: data.nom_centro_poblado.trim(),
        area_oficial_ha: data.area_oficial_ha?.trim() || null
      };
      
      // Validar datos antes de enviar
      if (!payload.cod_centro_poblado || !/^\d{8}$/.test(payload.cod_centro_poblado)) {
        throw new Error('Código de centro poblado debe tener 8 dígitos');
      }
      
      if (!payload.cod_municipio || isNaN(payload.cod_municipio)) {
        throw new Error('Código de municipio inválido');
      }
      
      if (!payload.nom_centro_poblado || payload.nom_centro_poblado.length < 3) {
        throw new Error('Nombre del centro poblado es requerido (mín. 3 caracteres)');
      }
      
      console.log('📤 Enviando payload:', payload);
      
      // Intentar diferentes endpoints hasta encontrar el correcto
      let response;
      try {
        // Opción 1: Endpoint directo
        response = await api.post('/preoperacion/centros-poblados/', payload);
      } catch (error1) {
        try {
          // Opción 2: Endpoint sin slash final
          response = await api.post('/preoperacion/centros-poblados', payload);
        } catch (error2) {
          try {
            // Opción 3: Endpoint alternativo
            response = await api.post('/centros-poblados/', payload);
          } catch (error3) {
            // Opción 4: Endpoint sin preoperacion
            response = await api.post('/centros-poblados', payload);
          }
        }
      }
      
      console.log('✅ Centro poblado creado exitosamente:', response);
      return response;
      
    } catch (error) {
      console.error('❌ Error al crear centro poblado:', error);
      
      // Manejo de errores específicos
      if (error.response?.status === 400) {
        const errorMsg = error.response.data?.detail || error.response.data?.message || 'Datos inválidos';
        throw new Error(`Error de validación: ${errorMsg}`);
      } else if (error.response?.status === 409) {
        throw new Error('Ya existe un centro poblado con ese código');
      } else if (error.response?.status === 500) {
        throw new Error('Error interno del servidor');
      } else {
        throw new Error(error.message || 'Error desconocido al crear centro poblado');
      }
    }
  },

  // 🆕 ACTUALIZAR centro poblado existente
  update: async (id: string, data: CentroPobladoForm): Promise<CentroPoblado> => {
    try {
      console.log('✏️ Actualizando centro poblado:', id, data);
      
      // Preparar datos asegurando tipos correctos
      const payload = {
        cod_centro_poblado: data.cod_centro_poblado.toString().trim(),
        cod_municipio: parseInt(data.cod_municipio.toString()),
        nom_centro_poblado: data.nom_centro_poblado.trim(),
        area_oficial_ha: data.area_oficial_ha?.trim() || null
      };
      
      console.log('📤 Enviando payload de actualización:', payload);
      
      // Intentar diferentes endpoints
      let response;
      try {
        // Opción 1: PUT con ID
        response = await api.put(`/preoperacion/centros-poblados/${id}/`, payload);
      } catch (error1) {
        try {
          // Opción 2: PATCH con ID
          response = await api.patch(`/preoperacion/centros-poblados/${id}/`, payload);
        } catch (error2) {
          try {
            // Opción 3: PUT sin slash
            response = await api.put(`/preoperacion/centros-poblados/${id}`, payload);
          } catch (error3) {
            // Opción 4: Endpoint alternativo
            response = await api.put(`/centros-poblados/${id}/`, payload);
          }
        }
      }
      
      console.log('✅ Centro poblado actualizado exitosamente:', response);
      return response;
      
    } catch (error) {
      console.error('❌ Error al actualizar centro poblado:', error);
      
      if (error.response?.status === 404) {
        throw new Error('Centro poblado no encontrado');
      } else if (error.response?.status === 400) {
        const errorMsg = error.response.data?.detail || error.response.data?.message || 'Datos inválidos';
        throw new Error(`Error de validación: ${errorMsg}`);
      } else {
        throw new Error(error.message || 'Error desconocido al actualizar centro poblado');
      }
    }
  },

  // 🆕 OBTENER centro poblado por ID (para modo edición)
  getById: async (id: string): Promise<CentroPoblado> => {
    try {
      console.log('🔍 Obteniendo centro poblado por ID:', id);
      
      // Intentar diferentes endpoints
      let response;
      try {
        response = await api.get(`/preoperacion/centros-poblados/${id}/`);
      } catch (error1) {
        try {
          response = await api.get(`/preoperacion/centros-poblados/${id}`);
        } catch (error2) {
          response = await api.get(`/centros-poblados/${id}/`);
        }
      }
      
      console.log('✅ Centro poblado encontrado:', response);
      return response;
      
    } catch (error) {
      console.error('❌ Error al obtener centro poblado:', error);
      
      if (error.response?.status === 404) {
        throw new Error('Centro poblado no encontrado');
      } else {
        throw new Error(error.message || 'Error al obtener centro poblado');
      }
    }
  },

  // 🆕 ELIMINAR centro poblado
  delete: async (id: string): Promise<void> => {
    try {
      console.log('🗑️ Eliminando centro poblado:', id);
      
      // Intentar diferentes endpoints
      try {
        await api.delete(`/preoperacion/centros-poblados/${id}/`);
      } catch (error1) {
        try {
          await api.delete(`/preoperacion/centros-poblados/${id}`);
        } catch (error2) {
          await api.delete(`/centros-poblados/${id}/`);
        }
      }
      
      console.log('✅ Centro poblado eliminado exitosamente');
      
    } catch (error) {
      console.error('❌ Error al eliminar centro poblado:', error);
      
      if (error.response?.status === 404) {
        throw new Error('Centro poblado no encontrado');
      } else if (error.response?.status === 409) {
        throw new Error('No se puede eliminar: el centro poblado tiene dependencias');
      } else {
        throw new Error(error.message || 'Error al eliminar centro poblado');
      }
    }
  },

  // 🆕 OBTENER TODOS los centros poblados (para lista completa)
  getAll: async (params = {}): Promise<CentroPoblado[]> => {
    try {
      console.log('📋 Obteniendo todos los centros poblados:', params);
      
      const response = await api.get('/preoperacion/centros-poblados/', { params });
      
      // Manejar respuesta paginada o array directo
      const data = response.results || response;
      return Array.isArray(data) ? data : [];
      
    } catch (error) {
      console.error('❌ Error al obtener centros poblados:', error);
      return [];
    }
  }
};

// ✅ FUNCIÓN AUXILIAR PARA COMPATIBILIDAD (mantener la existente)
export const getCentrosPobladosPorMunicipio = centrosPobladosApi.porMunicipio;

// ✅ EXPORTACIÓN POR DEFECTO
export default centrosPobladosApi;