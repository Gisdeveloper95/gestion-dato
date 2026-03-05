import api from './config';
import type { ArchivoPre } from '@/models/archivos';

// Obtener archivos preoperación por municipio
export const getArchivosByMunicipio = async (municipioId: number): Promise<ArchivoPre[]> => {
  try {
    // Obtener todas las clasificaciones del municipio
    const clasificacionesResponse = await api.get(`/preoperacion/municipios/${municipioId}/clasificaciones/`);
    const clasificaciones = Array.isArray(clasificacionesResponse) ? clasificacionesResponse : [];
    
    // Array para almacenar todos los archivos
    const archivos: ArchivoPre[] = [];
    
    // Para cada clasificación, obtener sus archivos
    for (const clasificacion of clasificaciones) {
      try {
        const archivosResponse = await api.get(`/preoperacion/clasificaciones/${clasificacion.cod_clasificacion}/archivos-pre/`);
        
        if (Array.isArray(archivosResponse)) {
          archivos.push(...archivosResponse);
        }
      } catch (error) {
        console.error(`Error al obtener archivos para clasificación ${clasificacion.cod_clasificacion}:`, error);
      }
    }
    
    return archivos;
  } catch (error) {
    console.error('Error al obtener archivos de preoperación:', error);
    throw error;
  }
};

// Ver archivo
export const verArchivoPre = async (rutaArchivo: string): Promise<Blob> => {
  try {
    const response = await api.get(`/preoperacion/ver_archivo/?ruta=${encodeURIComponent(rutaArchivo)}`, {
      responseType: 'blob'
    });
    return response;
  } catch (error) {
    console.error('Error al ver archivo:', error);
    throw error;
  }
};

// Descargar archivo
export const descargarArchivoPre = async (rutaArchivo: string): Promise<Blob> => {
  try {
    const response = await api.get(`/preoperacion/descargar_archivo/?ruta=${encodeURIComponent(rutaArchivo)}`, {
      responseType: 'blob'
    });
    return response;
  } catch (error) {
    console.error('Error al descargar archivo:', error);
    throw error;
  }
};