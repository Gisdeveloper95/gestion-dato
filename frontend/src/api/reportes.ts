import api, { API_URL } from './config';
import * as XLSX from 'xlsx';
// Interfaces para opciones de reportes
export interface OpcionesReportePreoperacion {
  municipios: number[];
  generar_individuales: boolean;
  generar_resumen: boolean;
  formato?: 'excel' | 'pdf';
  incluir_archivos?: boolean;
  incluir_estadisticas?: boolean;
}

export interface OpcionesReportePostoperacion {
  municipios: number[];
  generar_individuales: boolean;
  formato?: 'excel' | 'pdf';
  incluir_archivos?: boolean;
  incluir_estadisticas?: boolean;
  incluir_componentes?: string[];
}

export interface RespuestaGeneracionReporte {
  success: boolean;
  message: string;
  archivo_url?: string;
  archivo_nombre?: string;
  total_municipios?: number;
  tiempo_procesamiento?: string;
}

// Interfaz para el progreso de generación
export interface ProgresoReporte {
  municipio_actual: string;
  municipios_completados: number;
  total_municipios: number;
  porcentaje: number;
  estado: 'iniciando' | 'procesando' | 'finalizando' | 'completado' | 'error';
  mensaje?: string;
}

/**
 * Servicios para Reportes de Preoperación
 */
export class ReportesPreoperacionService {
  
  /**
   * Genera reportes de preoperación según las opciones especificadas
   */
  static async generarReportes(opciones: OpcionesReportePreoperacion): Promise<Blob> {
    try {
      console.log('🔄 Generando reportes de preoperación:', opciones);
      
      const response = await fetch(`${API_URL}/preoperacion/generar-reportes/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(opciones)
      });
      
      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`Error ${response.status}: ${errorData}`);
      }
      
      const blob = await response.blob();
      console.log('✅ Reportes de preoperación generados exitosamente');
      
      return blob;
    } catch (error) {
      console.error('❌ Error generando reportes de preoperación:', error);
      throw error;
    }
  }
  
  /**
   * Obtiene el progreso de la generación de reportes
   */
  static async obtenerProgreso(tareaId: string): Promise<ProgresoReporte> {
    try {
      const response = await api.get(`/preoperacion/reportes/progreso/${tareaId}/`);
      return response;
    } catch (error) {
      console.error('Error obteniendo progreso de preoperación:', error);
      throw error;
    }
  }
  
  /**
   * Obtiene la lista de plantillas disponibles para preoperación
   */
  static async obtenerPlantillas(): Promise<any[]> {
    try {
      const response = await api.get('/preoperacion/reportes/plantillas/');
      return Array.isArray(response) ? response : response.results || [];
    } catch (error) {
      console.error('Error obteniendo plantillas de preoperación:', error);
      return [];
    }
  }
  
  /**
   * Valida los códigos de municipio para preoperación
   */
  static async validarMunicipios(codigos: string[]): Promise<{
    validos: number[];
    invalidos: string[];
    detalles: any[];
  }> {
    try {
      const response = await api.post('/preoperacion/validar-municipios/', {
        codigos: codigos
      });
      
      return response;
    } catch (error) {
      console.error('Error validando municipios de preoperación:', error);
      throw error;
    }
  }
  
  /**
   * Obtiene estadísticas de insumos por municipio
   */
  static async obtenerEstadisticasInsumos(municipioIds: number[]): Promise<any[]> {
    try {
      const response = await api.post('/preoperacion/estadisticas-insumos/', {
        municipios: municipioIds
      });
      
      return Array.isArray(response) ? response : response.results || [];
    } catch (error) {
      console.error('Error obteniendo estadísticas de insumos:', error);
      return [];
    }
  }
  
  /**
   * Descarga un reporte individual por municipio
   */
  static async descargarReporteIndividual(
    municipioId: number, 
    formato: 'excel' | 'pdf' = 'excel'
  ): Promise<Blob> {
    try {
      const response = await fetch(
        `${API_URL}/preoperacion/reporte-individual/${municipioId}/?formato=${formato}`,
        {
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`
          }
        }
      );
      
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      
      return await response.blob();
    } catch (error) {
      console.error('Error descargando reporte individual:', error);
      throw error;
    }
  }
}

/**
 * Servicios para Reportes de Post-operación
 */
export class ReportesPostoperacionService {
  
  /**
   * Genera reportes de post-operación según las opciones especificadas
   */
  static async generarReportes(opciones: OpcionesReportePostoperacion): Promise<Blob> {
    try {
      console.log('🔄 Generando reportes de post-operación:', opciones);
      
      const response = await fetch(`${API_URL}/postoperacion/generar-reportes/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(opciones)
      });
      
      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`Error ${response.status}: ${errorData}`);
      }
      
      const blob = await response.blob();
      console.log('✅ Reportes de post-operación generados exitosamente');
      
      return blob;
    } catch (error) {
      console.error('❌ Error generando reportes de post-operación:', error);
      throw error;
    }
  }
  
  /**
   * Obtiene el progreso de la generación de reportes
   */
  static async obtenerProgreso(tareaId: string): Promise<ProgresoReporte> {
    try {
      const response = await api.get(`/postoperacion/reportes/progreso/${tareaId}/`);
      return response;
    } catch (error) {
      console.error('Error obteniendo progreso de post-operación:', error);
      throw error;
    }
  }
  
  /**
   * Obtiene la lista de componentes disponibles para filtrar
   */
  static async obtenerComponentes(): Promise<any[]> {
    try {
      const response = await api.get('/postoperacion/componentes/');
      return Array.isArray(response) ? response : response.results || [];
    } catch (error) {
      console.error('Error obteniendo componentes:', error);
      return [];
    }
  }
  
  /**
   * Valida los códigos de municipio para post-operación
   */
  static async validarMunicipios(codigos: string[]): Promise<{
    validos: number[];
    invalidos: string[];
    detalles: any[];
  }> {
    try {
      const response = await api.post('/postoperacion/validar-municipios/', {
        codigos: codigos
      });
      
      return response;
    } catch (error) {
      console.error('Error validando municipios de post-operación:', error);
      throw error;
    }
  }
  
  /**
   * Obtiene estadísticas de productos por municipio
   */
  static async obtenerEstadisticasProductos(municipioIds: number[]): Promise<any[]> {
    try {
      const response = await api.post('/postoperacion/estadisticas-productos/', {
        municipios: municipioIds
      });
      
      return Array.isArray(response) ? response : response.results || [];
    } catch (error) {
      console.error('Error obteniendo estadísticas de productos:', error);
      return [];
    }
  }
  
  /**
   * Obtiene el estado de las disposiciones por municipio
   */
  static async obtenerEstadoDisposiciones(municipioIds: number[]): Promise<any[]> {
    try {
      const response = await api.post('/postoperacion/estado-disposiciones/', {
        municipios: municipioIds
      });
      
      return Array.isArray(response) ? response : response.results || [];
    } catch (error) {
      console.error('Error obteniendo estado de disposiciones:', error);
      return [];
    }
  }
  
  /**
   * Descarga un reporte individual por municipio
   */
  static async descargarReporteIndividual(
    municipioId: number, 
    formato: 'excel' | 'pdf' = 'excel'
  ): Promise<Blob> {
    try {
      const response = await fetch(
        `${API_URL}/postoperacion/reporte-individual/${municipioId}/?formato=${formato}`,
        {
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`
          }
        }
      );
      
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      
      return await response.blob();
    } catch (error) {
      console.error('Error descargando reporte individual:', error);
      throw error;
    }
  }
}

/**
 * Utilidades compartidas para reportes
 */
export class ReportesUtils {
  
  /**
   * Descarga un blob como archivo
   */
  static descargarBlob(blob: Blob, nombreArchivo: string): void {
    try {
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = nombreArchivo;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log(`✅ Archivo descargado: ${nombreArchivo}`);
    } catch (error) {
      console.error('❌ Error descargando archivo:', error);
      throw error;
    }
  }
  
  /**
   * Genera un nombre de archivo único con timestamp
   */
  static generarNombreArchivo(
    prefijo: string, 
    tipo: 'preoperacion' | 'postoperacion',
    extension: 'xlsx' | 'pdf' | 'zip' = 'zip'
  ): string {
    const fecha = new Date();
    const timestamp = fecha.toISOString().split('T')[0].replace(/-/g, '');
    const hora = fecha.toTimeString().split(' ')[0].replace(/:/g, '');
    
    return `${prefijo}_${tipo}_${timestamp}_${hora}.${extension}`;
  }
  
  /**
   * Valida las opciones de reporte antes de enviarlas
   */
  static validarOpciones(opciones: any): { valido: boolean; errores: string[] } {
    const errores: string[] = [];
    
    if (!opciones.municipios || !Array.isArray(opciones.municipios) || opciones.municipios.length === 0) {
      errores.push('Debe seleccionar al menos un municipio');
    }
    
    if (opciones.municipios && opciones.municipios.length > 100) {
      errores.push('No se pueden procesar más de 100 municipios a la vez');
    }
    
    if ('generar_individuales' in opciones && 'generar_resumen' in opciones) {
      if (!opciones.generar_individuales && !opciones.generar_resumen) {
        errores.push('Debe seleccionar al menos un tipo de reporte para generar');
      }
    } else if ('generar_individuales' in opciones && !opciones.generar_individuales) {
      errores.push('Debe seleccionar generar reportes individuales');
    }
    
    return {
      valido: errores.length === 0,
      errores
    };
  }
  
  /**
   * Formatea el tamaño de archivo para mostrar al usuario
   */
  static formatearTamanoArchivo(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
  
  /**
   * Estima el tiempo de procesamiento basado en el número de municipios
   */
  static estimarTiempoProcesamiento(numeroMunicipios: number, tipo: 'preoperacion' | 'postoperacion'): string {
    // Estimaciones basadas en experiencia (segundos por municipio)
    const tiempoPorMunicipio = tipo === 'preoperacion' ? 3 : 2;
    const tiempoTotal = numeroMunicipios * tiempoPorMunicipio;
    
    if (tiempoTotal < 60) {
      return `${tiempoTotal} segundos`;
    } else if (tiempoTotal < 3600) {
      const minutos = Math.ceil(tiempoTotal / 60);
      return `${minutos} minuto${minutos > 1 ? 's' : ''}`;
    } else {
      const horas = Math.ceil(tiempoTotal / 3600);
      return `${horas} hora${horas > 1 ? 's' : ''}`;
    }
  }
  
  /**
   * Procesa archivos subidos para extraer códigos de municipio
   */
  static async procesarArchivoMunicipios(archivo: File): Promise<string[]> {
    const extension = archivo.name.split('.').pop()?.toLowerCase();
    
    switch (extension) {
      case 'xlsx':
      case 'xls':
        return await this.extraerCodigosDeExcel(archivo);
      case 'csv':
        return await this.extraerCodigosDeCSV(archivo);
      case 'txt':
        return await this.extraerCodigosDeTXT(archivo);
      default:
        throw new Error(`Formato de archivo no soportado: ${extension}`);
    }
  }
  
  private static async extraerCodigosDeExcel(archivo: File): Promise<string[]> {
    // Implementación usando SheetJS (ya importado en los componentes)
    const data = await archivo.arrayBuffer();
    const XLSX = await import('xlsx');
    const workbook = XLSX.read(data);
    const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
    const jsonData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 });
    
    const codigos: string[] = [];
    for (const row of jsonData as any[][]) {
      if (row[0] && (typeof row[0] === 'number' || /^\d+$/.test(String(row[0])))) {
        codigos.push(String(row[0]));
      }
    }
    
    return codigos;
  }
  
  private static async extraerCodigosDeCSV(archivo: File): Promise<string[]> {
    const text = await archivo.text();
    const lines = text.split(/\r?\n/);
    const codigos: string[] = [];
    
    for (const line of lines) {
      const values = line.split(/[,;]/);
      for (const value of values) {
        const cleaned = value.trim().replace(/['"]/g, '');
        if (/^\d+$/.test(cleaned)) {
          codigos.push(cleaned);
        }
      }
    }
    
    return codigos;
  }
  
  private static async extraerCodigosDeTXT(archivo: File): Promise<string[]> {
    const text = await archivo.text();
    const codigos = text
      .split(/[,\s\n\r]+/)
      .map(c => c.trim())
      .filter(c => /^\d+$/.test(c));
    
    return codigos;
  }
}

// Exportar servicios principales
export const reportesPreoperacion = ReportesPreoperacionService;
export const reportesPostoperacion = ReportesPostoperacionService;
export const reportesUtils = ReportesUtils;