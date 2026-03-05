import api from './config';

// Interface para Concepto
export interface Concepto {
  cod_concepto: number;
  concepto: string;
  fecha?: string | null;
  evaluacion?: string | null;
  detalle_concepto?: string | null;
  observacion?: string | null;
  pdf?: string;
}

// Obtener todos los conceptos
export const getConceptos = async (): Promise<Concepto[]> => {
  try {
    const response = await api.get<Concepto[]>('/preoperacion/conceptos/');
    return response || [];
  } catch (error) {
    console.error('Error al obtener conceptos:', error);
    throw error;
  }
};

// Obtener un concepto por ID
export const getConceptoById = async (id: number): Promise<Concepto> => {
  try {
    const response = await api.get<Concepto>(`/preoperacion/conceptos/${id}/`);
    return response;
  } catch (error) {
    console.error('Error al obtener concepto:', error);
    throw error;
  }
};

// Crear un nuevo concepto
export const createConcepto = async (data: Partial<Concepto>): Promise<Concepto> => {
  try {
    const response = await api.post<Concepto>('/preoperacion/conceptos/', data);
    return response;
  } catch (error) {
    console.error('Error al crear concepto:', error);
    throw error;
  }
};

// Actualizar un concepto existente
export const updateConcepto = async (id: number, data: Partial<Concepto>): Promise<Concepto> => {
  try {
    const response = await api.put<Concepto>(`/preoperacion/conceptos/${id}/`, data);
    return response;
  } catch (error) {
    console.error('Error al actualizar concepto:', error);
    throw error;
  }
};

// Eliminar un concepto
export const deleteConcepto = async (id: number): Promise<void> => {
  try {
    await api.delete(`/preoperacion/conceptos/${id}/`);
  } catch (error) {
    console.error('Error al eliminar concepto:', error);
    throw error;
  }
};

// Obtener conceptos por detalle
export const getConceptosByDetalle = async (detalleId: number): Promise<Concepto[]> => {
  try {
    const response = await api.get<Concepto[]>(`/preoperacion/detalles/${detalleId}/conceptos/`);
    return response || [];
  } catch (error) {
    console.error('Error al obtener conceptos por detalle:', error);
    throw error;
  }
};

export const getConceptosByMunicipio = async (municipioId: number): Promise<Concepto[]> => {
  try {
    // Primero obtenemos los detalles del municipio que tengan conceptos asociados
    const detallesResponse = await api.get(`/preoperacion/municipios/${municipioId}/detalles/`);
    const detalles = Array.isArray(detallesResponse) ? detallesResponse : [];
    
    // Array para almacenar todos los conceptos
    const conceptos: Concepto[] = [];
    
    // Para cada detalle, obtener sus conceptos
    for (const detalle of detalles) {
      try {
        // Si el detalle tiene un código válido
        if (detalle.cod_detalle) {
          const conceptosResponse = await api.get(`/preoperacion/detalles/${detalle.cod_detalle}/conceptos/`);
          
          if (Array.isArray(conceptosResponse)) {
            conceptos.push(...conceptosResponse);
          }
        }
      } catch (error) {
        console.error(`Error al obtener conceptos para detalle ${detalle.cod_detalle}:`, error);
      }
    }
    
    return conceptos;
  } catch (error) {
    console.error('Error al obtener conceptos:', error);
    throw error;
  }
};



// Ver documento PDF
export const verDocumentoPDF = async (rutaPDF: string): Promise<Blob> => {
  try {
    const response = await api.get(`/preoperacion/ver_pdf/?ruta=${encodeURIComponent(rutaPDF)}`, {
      responseType: 'blob'
    });
    return response;
  } catch (error) {
    console.error('Error al ver documento PDF:', error);
    throw error;
  }
};