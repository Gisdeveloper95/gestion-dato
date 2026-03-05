// src/api/historialPropietarios.ts
import axios from 'axios';
import { API_URL } from './config';

// Interfaces
export interface HistorialPropietarioItem {
  id: number;
  tipo_archivo: 'preoperacion' | 'postoperacion';
  id_archivo: number;
  id_notificacion: number | null;
  propietario_anterior: string | null;
  propietario_nuevo: string;
  fecha_inicio: string;
  fecha_fin: string | null;
  detalles: {
    nombre_archivo?: string;
    ruta?: string;
    id_disposicion?: number;
    [key: string]: any;
  };
  estado: string;
  duracion: string;
  nombre_archivo?: string;
}

export interface EstadisticasHistorial {
  agrupacion: string;
  resultados: {
    periodo: string;
    periodo_formateado: string;
    total_cambios: number;
    usuarios_distintos: number;
    archivos_afectados: number;
  }[];
}

// ✅ FUNCIÓN AUXILIAR: Intentar múltiples endpoints
const intentarEndpoints = async (endpoints: string[], params: any, headers: any) => {
  for (const endpoint of endpoints) {
    try {
      console.log(`🔄 Intentando endpoint: ${endpoint}`);
      const response = await axios.get(endpoint, { params, headers, timeout: 5000 });
      console.log(`✅ Endpoint funcionó: ${endpoint}`);
      return response.data;
    } catch (error: any) {
      console.log(`❌ Endpoint falló: ${endpoint} - ${error.response?.status || error.message}`);
      continue;
    }
  }
  throw new Error('Todos los endpoints fallaron');
};

// Métodos para acceder a la API
export const historialPropietariosAPI = {
  /**
   * ✅ SOLUCIÓN SEGURA: Intenta múltiples endpoints y maneja errores elegantemente
   */
  async obtenerHistorialPorArchivo(tipo: string, idArchivo: number): Promise<HistorialPropietarioItem[]> {
    console.log(`🔍 Buscando historial para ${tipo}, ID: ${idArchivo}`);
    
    const headers = {
      'Authorization': `Token ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json'
    };
    
    const params = { tipo, id_archivo: idArchivo };
    
    // ✅ USAR SOLO EL ENDPOINT CORRECTO (ya sabemos que funciona)
    const endpoints = [
      `${API_URL}/postoperacion/historial-propietarios/por_archivo/`  // El único que funciona
    ];
    
    try {
      const data = await intentarEndpoints(endpoints, params, headers);
      
      if (Array.isArray(data)) {
        console.log(`✅ Historial obtenido: ${data.length} registros`);
        return data;
      } else {
        console.log('⚠️ Respuesta no es array, devolviendo vacío');
        return [];
      }
      
    } catch (error: any) {
      console.error(`❌ Todos los endpoints fallaron para ${tipo}/${idArchivo}:`, error);
      
      // ✅ NO devolver datos falsos, solo un array vacío
      return [];
    }
  },
  
  /**
   * ✅ MÉTODO ALTERNATIVO: Si el historial no funciona, intentar obtener info del usuario actual
   */
  async obtenerInfoUsuarioActual(tipo: string, idArchivo: number): Promise<HistorialPropietarioItem[]> {
    try {
      console.log(`🔄 Intentando método alternativo para ${tipo}/${idArchivo}`);
      
      const headers = {
        'Authorization': `Token ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      };
      
      // Intentar obtener info del archivo directamente
      const endpointArchivo = tipo === 'postoperacion' 
        ? `${API_URL}/postoperacion/archivos/${idArchivo}/`
        : `${API_URL}/preoperacion/archivos/${idArchivo}/`;
      
      const response = await axios.get(endpointArchivo, { headers, timeout: 5000 });
      
      if (response.data && response.data.usuario_windows) {
        // Crear un registro "actual" basado en la info del archivo
        const registroActual: HistorialPropietarioItem = {
          id: 1,
          tipo_archivo: tipo as 'preoperacion' | 'postoperacion',
          id_archivo: idArchivo,
          id_notificacion: null,
          propietario_anterior: null,
          propietario_nuevo: response.data.usuario_windows,
          fecha_inicio: response.data.fecha_disposicion || new Date().toISOString(),
          fecha_fin: null,
          detalles: {
            nombre_archivo: response.data.nombre_archivo || `Archivo ${idArchivo}`,
            ruta: response.data.ruta_completa || response.data.path_file || '',
            metodo: 'info_archivo_directo'
          },
          estado: 'Propietario Actual',
          duracion: 'N/A',
          nombre_archivo: response.data.nombre_archivo || `Archivo ${idArchivo}`
        };
        
        console.log('✅ Info obtenida del archivo directamente');
        return [registroActual];
      }
      
      return [];
      
    } catch (error) {
      console.log('❌ Método alternativo también falló');
      return [];
    }
  },
  
  /**
   * ✅ MÉTODO PRINCIPAL MEJORADO: Combina historial + info alternativa
   */
  async obtenerHistorialCompleto(tipo: string, idArchivo: number): Promise<HistorialPropietarioItem[]> {
    // 1. Intentar historial normal
    let historial = await this.obtenerHistorialPorArchivo(tipo, idArchivo);
    
    // 2. Si no hay historial, intentar método alternativo
    if (historial.length === 0) {
      console.log('🔄 Historial vacío, intentando método alternativo...');
      historial = await this.obtenerInfoUsuarioActual(tipo, idArchivo);
    }
    
    return historial;
  },
  
  /**
   * ✅ VERIFICAR SI EL SERVICIO ESTÁ DISPONIBLE
   */
  async verificarDisponibilidad(): Promise<{disponible: boolean, mensaje: string}> {
    try {
      const response = await axios.get(`${API_URL}/postoperacion/historial-propietarios/`, {
        params: { page_size: 1 },
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        timeout: 5000
      });
      
      return {
        disponible: true,
        mensaje: 'Servicio de historial disponible'
      };
      
    } catch (error: any) {
      let mensaje = 'Servicio de historial no disponible';
      
      if (error.response?.status === 500) {
        mensaje = 'Error interno del servidor. El historial está temporalmente deshabilitado.';
      } else if (error.response?.status === 404) {
        mensaje = 'Endpoint de historial no encontrado. Funcionalidad no implementada.';
      } else if (error.code === 'ECONNABORTED') {
        mensaje = 'Timeout del servidor. El servicio está lento.';
      }
      
      return {
        disponible: false,
        mensaje
      };
    }
  }
};