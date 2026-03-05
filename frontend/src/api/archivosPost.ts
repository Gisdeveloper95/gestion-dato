import api from './config';
import type { ArchivoPost } from '@/models/archivos';

// Obtener archivos postoperación por municipio
export const getArchivosPostByMunicipio = async (municipioId: number): Promise<ArchivoPost[]> => {
  try {
    // Primero obtenemos las disposiciones del municipio
    const disposicionesResponse = await api.get(`/postoperacion/disposiciones/por_municipio/?municipio_id=${municipioId}`);
    const disposiciones = Array.isArray(disposicionesResponse) ? disposicionesResponse : [];
    
    // Array para almacenar todos los archivos
    const archivos: ArchivoPost[] = [];
    
    // Para cada disposición, obtener sus archivos
    for (const disposicion of disposiciones) {
      try {
        const archivosResponse = await api.get(`/postoperacion/archivos/por_disposicion/?disposicion_id=${disposicion.id_disposicion}`);
        
        // Enriquecer cada archivo con información de su disposición
        if (Array.isArray(archivosResponse)) {
          const archivosEnriquecidos = archivosResponse.map(archivo => ({
            ...archivo,
            disposicion_info: {
              id_disposicion: disposicion.id_disposicion,
              componente: disposicion.componente?.nombre_componente || 'No especificado',
              dispuesto: disposicion.dispuesto || false,
              aprobado: disposicion.aprobado || false
            }
          }));
          
          archivos.push(...archivosEnriquecidos);
        }
      } catch (error) {
        console.error(`Error al obtener archivos para disposición ${disposicion.id_disposicion}:`, error);
      }
    }
    
    return archivos;
  } catch (error) {
    console.error('Error al obtener archivos de postoperación:', error);
    throw error;
  }
};

// Ver archivo
export const verArchivoPost = async (rutaArchivo: string): Promise<Blob> => {
  try {
    const response = await api.get(`/postoperacion/ver_archivo/?ruta=${encodeURIComponent(rutaArchivo)}`, {
      responseType: 'blob'
    });
    return response;
  } catch (error) {
    console.error('Error al ver archivo:', error);
    throw error;
  }
};

// Descargar archivo
export const descargarArchivoPost = async (rutaArchivo: string): Promise<Blob> => {
  try {
    const response = await api.get(`/postoperacion/descargar_archivo/?ruta=${encodeURIComponent(rutaArchivo)}`, {
      responseType: 'blob'
    });
    return response;
  } catch (error) {
    console.error('Error al descargar archivo:', error);
    throw error;
  }
};