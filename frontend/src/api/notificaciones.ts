// src/api/notificaciones.ts - VERSIÓN CORREGIDA Y RESILIENTE

import axios from 'axios'
import api, { API_URL } from './config'
import type { Notificacion, ResumenNotificaciones } from '@/models/notificacion'

/**
 * Función auxiliar para manejar errores de API de forma resiliente
 */
const manejarErrorAPI = (error: any, contexto: string): void => {
  console.error(`❌ Error en ${contexto}:`, {
    message: error.message,
    status: error.response?.status,
    url: error.config?.url
  });
  
  // No relanzar el error para permitir que el código continúe
};

/**
 * Obtiene notificaciones con parámetros seguros
 */
export const getNotificaciones = async (
  tipo = 'preoperacion', 
  params: Record<string, string> = {}
): Promise<Notificacion[]> => {
  try {
    if (!params.nocache) {
      params.nocache = Date.now().toString();
    }
    
    // Limitar page_size para evitar problemas
    if (params.page_size && parseInt(params.page_size) > 1000) {
      params.page_size = '1000';
    }
    
    let endpoint = tipo === 'preoperacion' 
      ? `/preoperacion/notificaciones/` 
      : `/postoperacion/notificaciones/`;
    
    console.log(`📡 Consultando: ${endpoint}`, params);
    
    const response = await api.get(endpoint, { params });
    
    if (response && response.results && Array.isArray(response.results)) {
      console.log(`✅ ${tipo}: ${response.results.length} notificaciones`);
      return response.results.map(n => ({ ...n, tipo_sistema: tipo }));
    } else if (Array.isArray(response)) {
      console.log(`✅ ${tipo}: ${response.length} notificaciones`);
      return response.map(n => ({ ...n, tipo_sistema: tipo }));
    } else {
      console.warn(`⚠️ Formato inesperado en ${tipo}:`, response);
      return [];
    }
  } catch (error) {
    manejarErrorAPI(error, `getNotificaciones(${tipo})`);
    return []; // Retornar array vacío en lugar de lanzar error
  }
}

/**
 * Obtiene notificaciones de un día específico (con fallback)
 */
export const getNotificacionesPorDia = async (
  tipo: 'preoperacion' | 'postoperacion',
  fecha: string // YYYY-MM-DD
): Promise<Notificacion[]> => {
  try {
    // Estrategia 1: Intentar con fecha específica
    const params1 = {
      fecha_cambio__date: fecha,
      page_size: '500', // Reducir tamaño
      ordering: '-fecha_cambio',
      nocache: Date.now().toString()
    };
    
    console.log(`📅 Intentando consulta por día ${tipo}: ${fecha}`);
    
    const response = await api.get(`/${tipo}/notificaciones/`, { params: params1 });
    
    let notificaciones: Notificacion[] = [];
    
    if (response && response.results && Array.isArray(response.results)) {
      notificaciones = response.results;
    } else if (Array.isArray(response)) {
      notificaciones = response;
    }
    
    console.log(`✅ ${tipo} día ${fecha}: ${notificaciones.length} notificaciones`);
    
    return notificaciones.map(n => ({
      ...n,
      tipo_sistema: tipo
    }));
    
  } catch (error) {
    console.warn(`⚠️ Falló consulta por día ${tipo}, intentando fallback...`);
    
    // FALLBACK: Intentar con rango de fechas
    try {
      const params2 = {
        fecha_cambio__gte: fecha,
        fecha_cambio__lte: fecha + ' 23:59:59',
        page_size: '500',
        nocache: Date.now().toString()
      };
      
      const responseFallback = await api.get(`/${tipo}/notificaciones/`, { params: params2 });
      
      let notificaciones: Notificacion[] = [];
      
      if (responseFallback && responseFallback.results) {
        notificaciones = responseFallback.results;
      } else if (Array.isArray(responseFallback)) {
        notificaciones = responseFallback;
      }
      
      // Filtrar en cliente para asegurar que son del día correcto
      const notificacionesFiltradas = notificaciones.filter(n => {
        if (!n.fecha_cambio) return false;
        const fechaNotif = new Date(n.fecha_cambio).toISOString().split('T')[0];
        return fechaNotif === fecha;
      });
      
      console.log(`✅ ${tipo} fallback día ${fecha}: ${notificacionesFiltradas.length} notificaciones`);
      
      return notificacionesFiltradas.map(n => ({
        ...n,
        tipo_sistema: tipo
      }));
      
    } catch (errorFallback) {
      manejarErrorAPI(errorFallback, `getNotificacionesPorDia fallback ${tipo} ${fecha}`);
      return [];
    }
  }
};

/**
 * Obtiene notificaciones por mes con múltiples estrategias
 */
export const getNotificacionesPorMes = async (
  tipo: 'preoperacion' | 'postoperacion' = 'preoperacion',
  año: number,
  mes: number,
  limite: number = 1000 // Reducir límite por defecto
): Promise<Notificacion[]> => {
  try {
    console.log(`🗓️ Cargando ${tipo} para ${año}-${mes.toString().padStart(2, '0')}`);
    
    // Estrategia 1: Filtro por rango de fechas
    const fechaInicio = `${año}-${mes.toString().padStart(2, '0')}-01`;
    const ultimoDiaDelMes = new Date(año, mes, 0).getDate();
    const fechaFin = `${año}-${mes.toString().padStart(2, '0')}-${ultimoDiaDelMes.toString().padStart(2, '0')}`;
    
    const params = {
      fecha_cambio__gte: fechaInicio,
      fecha_cambio__lte: fechaFin + ' 23:59:59',
      page_size: Math.min(limite, 1000).toString(), // Asegurar límite máximo
      nocache: Date.now().toString()
    };
    
    console.log(`📅 Rango: ${fechaInicio} a ${fechaFin}`);
    
    const endpoint = `/${tipo}/notificaciones/`;
    const response = await api.get(endpoint, { params });
    
    let notificaciones: Notificacion[] = [];
    
    if (response && response.results && Array.isArray(response.results)) {
      notificaciones = response.results;
    } else if (Array.isArray(response)) {
      notificaciones = response;
    } else {
      console.warn(`⚠️ Formato inesperado para ${tipo}:`, response);
      return [];
    }
    
    // Filtro adicional en cliente
    const notificacionesFiltradas = notificaciones.filter(n => {
      if (!n.fecha_cambio) return false;
      
      const fechaNotif = new Date(n.fecha_cambio);
      return fechaNotif.getFullYear() === año && (fechaNotif.getMonth() + 1) === mes;
    });
    
    console.log(`✅ ${tipo}: ${notificacionesFiltradas.length} notificaciones para ${año}-${mes}`);
    
    return notificacionesFiltradas.map(n => ({
      ...n,
      tipo_sistema: tipo
    }));
    
  } catch (error) {
    manejarErrorAPI(error, `getNotificacionesPorMes ${tipo} ${año}-${mes}`);
    
    // FALLBACK: Intentar obtener las más recientes sin filtro de fecha
    try {
      console.log(`🔄 Intentando fallback para ${tipo}...`);
      
      const paramsFallback = {
        page_size: '100', // Mucho más pequeño para el fallback
        nocache: Date.now().toString()
      };
      
      const responseFallback = await api.get(`/${tipo}/notificaciones/`, { params: paramsFallback });
      
      let notificacionesFallback: Notificacion[] = [];
      
      if (responseFallback && responseFallback.results) {
        notificacionesFallback = responseFallback.results;
      } else if (Array.isArray(responseFallback)) {
        notificacionesFallback = responseFallback;
      }
      
      // Filtrar por mes en cliente
      const notificacionesDelMes = notificacionesFallback.filter(n => {
        if (!n.fecha_cambio) return false;
        const fechaNotif = new Date(n.fecha_cambio);
        return fechaNotif.getFullYear() === año && (fechaNotif.getMonth() + 1) === mes;
      });
      
      console.log(`✅ ${tipo} fallback: ${notificacionesDelMes.length} notificaciones`);
      
      return notificacionesDelMes.map(n => ({
        ...n,
        tipo_sistema: tipo
      }));
      
    } catch (errorFallback) {
      manejarErrorAPI(errorFallback, `fallback ${tipo}`);
      return [];
    }
  }
};

/**
 * Obtiene notificaciones del día actual con múltiples fallbacks
 */
export const getNotificacionesHoy = async (): Promise<{
  preoperacion: Notificacion[],
  postoperacion: Notificacion[]
}> => {
  const hoy = new Date();
  const año = hoy.getFullYear();
  const mes = hoy.getMonth() + 1;
  const dia = hoy.getDate().toString().padStart(2, '0');
  const fechaHoy = `${año}-${mes.toString().padStart(2, '0')}-${dia}`;
  
  console.log(`📅 Cargando notificaciones de HOY: ${fechaHoy}`);
  
  // Intentar cargar ambos tipos con manejo de errores independiente
  const [notifPre, notifPost] = await Promise.allSettled([
    getNotificacionesPorDia('preoperacion', fechaHoy),
    getNotificacionesPorDia('postoperacion', fechaHoy)
  ]);
  
  const preoperacion = notifPre.status === 'fulfilled' ? notifPre.value : [];
  const postoperacion = notifPost.status === 'fulfilled' ? notifPost.value : [];
  
  console.log(`✅ HOY: ${preoperacion.length} pre + ${postoperacion.length} post`);
  
  return { preoperacion, postoperacion };
};

// Mantener funciones existentes para compatibilidad (con manejo de errores mejorado)

export const getNotificacionesNoLeidas = async (tipo = 'preoperacion'): Promise<Notificacion[]> => {
  try {
    const timestamp = Date.now();
    let endpoint = tipo === 'preoperacion'
      ? `/preoperacion/notificaciones/no_leidas/?nocache=${timestamp}&limit=100`
      : `/postoperacion/notificaciones/no_leidas/?nocache=${timestamp}&limit=100`;
    
    const response = await api.get(endpoint);
    
    if (response && response.results) {
      return response.results;
    } else if (Array.isArray(response)) {
      return response;
    } else {
      console.warn(`⚠️ Formato inesperado para no leídas ${tipo}:`, response);
      return [];
    }
  } catch (error) {
    manejarErrorAPI(error, `getNotificacionesNoLeidas ${tipo}`);
    return [];
  }
}

export const getResumenNotificaciones = async (tipo = 'preoperacion'): Promise<ResumenNotificaciones> => {
  try {
    const timestamp = Date.now();
    let endpoint = tipo === 'preoperacion'
      ? `/preoperacion/notificaciones/resumen/?nocache=${timestamp}`
      : `/postoperacion/notificaciones/resumen/?nocache=${timestamp}`;
    
    const response = await api.get(endpoint);
    return response;
  } catch (error) {
    manejarErrorAPI(error, `getResumenNotificaciones ${tipo}`);
    return {
      total_no_leidas: 0,
      por_tipo: [],
      ultimas: []
    };
  }
}

export const marcarComoLeidas = async (ids: number[], tipo = 'preoperacion'): Promise<void> => {
  if (!ids.length) return;
  
  try {
    let endpoint = tipo === 'preoperacion'
      ? '/preoperacion/notificaciones/marcar_como_leidas/'
      : '/postoperacion/notificaciones/marcar_como_leidas/';
    
    await api.post(endpoint, { ids });
  } catch (error) {
    manejarErrorAPI(error, `marcarComoLeidas ${tipo}`);
    throw error; // Re-lanzar para que el UI pueda manejar el error
  }
}

export const marcarTodasComoLeidas = async (tipo = 'preoperacion'): Promise<void> => {
  try {
    let endpoint = tipo === 'preoperacion'
      ? '/preoperacion/notificaciones/marcar_todas_leidas/'
      : '/postoperacion/notificaciones/marcar_todas_leidas/';
    
    await api.post(endpoint);
  } catch (error) {
    manejarErrorAPI(error, `marcarTodasComoLeidas ${tipo}`);
    throw error; // Re-lanzar para que el UI pueda manejar el error
  }
}