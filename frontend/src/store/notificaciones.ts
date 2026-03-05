// store/notificaciones.ts - Versión optimizada para carga por mes

import { defineStore } from 'pinia'
import { 
  getNotificaciones, 
  getNotificacionesPorMes, 
  getNotificacionesHoy,
  getNotificacionesNoLeidas, 
  marcarComoLeidas, 
  marcarTodasComoLeidas 
} from '@/api/notificaciones'
import type { Notificacion, ResumenNotificaciones } from '@/models/notificacion'

// Constantes para optimizar el rendimiento
const CACHE_DURATION = 10 * 60 * 1000 // 10 minutos de caché

interface CacheEntry {
  data: Notificacion[];
  timestamp: number;
}

interface CachePorMes {
  [key: string]: {
    preoperacion: CacheEntry;
    postoperacion: CacheEntry;
  };
}

export const useNotificacionesStore = defineStore('notificaciones', {
  state: () => ({
    // Notificaciones generales (para compatibilidad)
    notificaciones: [] as Notificacion[],
    notificacionesHoy: [] as Notificacion[],
    noLeidas: 0,
    cargando: false,
    error: null as string | null,
    ultimaActualizacion: 0,
    
    // Nuevo sistema de caché por mes
    cachePorMes: {} as CachePorMes,
    
    // Estados de carga específicos
    cargandoHoy: false,
    cargandoMes: false,
    mesActual: '',
  }),
  
  getters: {
    // Verificar si hay caché válido para un mes específico
    tieneCacheValidoPorMes: (state) => (año: number, mes: number, tipo: 'preoperacion' | 'postoperacion') => {
      const claveMes = `${año}-${mes.toString().padStart(2, '0')}`;
      const cache = state.cachePorMes[claveMes]?.[tipo];
      
      if (!cache) return false;
      
      const ahora = Date.now();
      return (ahora - cache.timestamp) < CACHE_DURATION;
    },
    
    // Obtener notificaciones de un mes específico desde caché
    notificacionesPorMes: (state) => (año: number, mes: number, tipo: 'preoperacion' | 'postoperacion') => {
      const claveMes = `${año}-${mes.toString().padStart(2, '0')}`;
      return state.cachePorMes[claveMes]?.[tipo]?.data || [];
    },
    
    // Estadísticas de caché (para debugging)
    estadisticasCache: (state) => {
      const mesesEnCache = Object.keys(state.cachePorMes).length;
      const totalNotificaciones = Object.values(state.cachePorMes).reduce((total, mes) => {
        return total + (mes.preoperacion?.data?.length || 0) + (mes.postoperacion?.data?.length || 0);
      }, 0);
      
      return {
        mesesEnCache,
        totalNotificaciones,
        ultimaActualizacion: state.ultimaActualizacion
      };
    }
  },
  
  actions: {
    // NUEVO: Cargar notificaciones de un mes específico
    async cargarNotificacionesPorMes(año: number, mes: number) {
      const claveMes = `${año}-${mes.toString().padStart(2, '0')}`;
      
      try {
        this.cargandoMes = true;
        this.mesActual = claveMes;
        
        // Verificar caché para ambos tipos
        const tieneCachePre = this.tieneCacheValidoPorMes(año, mes, 'preoperacion');
        const tieneCachePost = this.tieneCacheValidoPorMes(año, mes, 'postoperacion');
        
        if (tieneCachePre && tieneCachePost) {
          console.log(`💾 Usando caché completo para ${claveMes}`);
          return {
            preoperacion: this.notificacionesPorMes(año, mes, 'preoperacion'),
            postoperacion: this.notificacionesPorMes(año, mes, 'postoperacion')
          };
        }
        
        console.log(`🔄 Cargando datos frescos para ${claveMes}`);
        
        // Cargar datos frescos en paralelo
        const promesas = [];
        
        if (!tieneCachePre) {
          promesas.push(getNotificacionesPorMes('preoperacion', año, mes));
        }
        
        if (!tieneCachePost) {
          promesas.push(getNotificacionesPorMes('postoperacion', año, mes));
        }
        
        const resultados = await Promise.all(promesas);
        
        // Procesar resultados
        let notifPre = tieneCachePre ? this.notificacionesPorMes(año, mes, 'preoperacion') : resultados[0] || [];
        let notifPost = tieneCachePost ? this.notificacionesPorMes(año, mes, 'postoperacion') : resultados[tieneCachePre ? 0 : 1] || [];
        
        // Guardar en caché
        if (!this.cachePorMes[claveMes]) {
          this.cachePorMes[claveMes] = {
            preoperacion: { data: [], timestamp: 0 },
            postoperacion: { data: [], timestamp: 0 }
          };
        }
        
        if (!tieneCachePre) {
          this.cachePorMes[claveMes].preoperacion = {
            data: notifPre,
            timestamp: Date.now()
          };
        }
        
        if (!tieneCachePost) {
          this.cachePorMes[claveMes].postoperacion = {
            data: notifPost,
            timestamp: Date.now()
          };
        }
        
        console.log(`✅ ${claveMes}: ${notifPre.length} pre + ${notifPost.length} post`);
        
        this.error = null;
        this.ultimaActualizacion = Date.now();
        
        return {
          preoperacion: notifPre,
          postoperacion: notifPost
        };
        
      } catch (err: any) {
        console.error(`❌ Error cargando mes ${claveMes}:`, err);
        this.error = err.message || 'Error cargando notificaciones';
        throw err;
      } finally {
        this.cargandoMes = false;
      }
    },
    
    // NUEVO: Cargar solo notificaciones de hoy (súper optimizado)
    async cargarNotificacionesHoy() {
      try {
        this.cargandoHoy = true;
        console.log('📅 Cargando notificaciones de HOY...');
        
        const datosHoy = await getNotificacionesHoy();
        
        // Actualizar estado
        this.notificacionesHoy = [...datosHoy.preoperacion, ...datosHoy.postoperacion]
          .sort((a, b) => new Date(b.fecha_cambio || '').getTime() - new Date(a.fecha_cambio || '').getTime());
        
        // También actualizar el array general para compatibilidad (solo si está vacío)
        if (this.notificaciones.length === 0) {
          this.notificaciones = this.notificacionesHoy;
        }
        
        console.log(`✅ HOY: ${this.notificacionesHoy.length} notificaciones`);
        
        this.error = null;
        this.ultimaActualizacion = Date.now();
        
        return this.notificacionesHoy;
        
      } catch (err: any) {
        console.error('❌ Error cargando notificaciones de hoy:', err);
        this.error = err.message || 'Error cargando notificaciones';
        throw err;
      } finally {
        this.cargandoHoy = false;
      }
    },
    
    // Método de compatibilidad (usar la nueva estrategia)
    async cargarNotificaciones() {
      // Por defecto, cargar solo notificaciones de hoy
      return this.cargarNotificacionesHoy();
    },
    
    // Cargar notificaciones no leídas (mantener igual)
    async cargarNotificacionesNoLeidas() {
      try {
        const [noLeidasPre, noLeidasPost] = await Promise.all([
          getNotificacionesNoLeidas('preoperacion'),
          getNotificacionesNoLeidas('postoperacion')
        ]);
        
        this.noLeidas = noLeidasPre.length + noLeidasPost.length;
        console.log(`📊 Total no leídas: ${this.noLeidas}`);
      } catch (err: any) {
        console.error('❌ Error cargando notificaciones no leídas:', err);
      }
    },
    
    // NUEVO: Invalidar caché de un mes específico
    invalidarCacheMes(año: number, mes: number) {
      const claveMes = `${año}-${mes.toString().padStart(2, '0')}`;
      if (this.cachePorMes[claveMes]) {
        delete this.cachePorMes[claveMes];
        console.log(`🗑️ Caché invalidado para ${claveMes}`);
      }
    },
    
    // NUEVO: Limpiar caché viejo (más de 30 minutos)
    limpiarCacheViejo() {
      const ahora = Date.now();
      const LIMITE_CACHE_VIEJO = 30 * 60 * 1000; // 30 minutos
      
      Object.keys(this.cachePorMes).forEach(claveMes => {
        const mes = this.cachePorMes[claveMes];
        const esViejoPre = (ahora - mes.preoperacion.timestamp) > LIMITE_CACHE_VIEJO;
        const esViejoPost = (ahora - mes.postoperacion.timestamp) > LIMITE_CACHE_VIEJO;
        
        if (esViejoPre && esViejoPost) {
          delete this.cachePorMes[claveMes];
          console.log(`🧹 Caché viejo limpiado: ${claveMes}`);
        }
      });
    },
    
    // Marcar notificaciones como leídas (mejorado)
    async marcarLeidas(ids: number[], tipo?: string) {
      if (!ids.length) return;
      
      try {
        // Si no se especifica tipo, detectar automáticamente
        if (!tipo) {
          const idsPre: number[] = [];
          const idsPost: number[] = [];
          
          ids.forEach(id => {
            if (id > 1000000) {
              idsPost.push(id);
            } else {
              idsPre.push(id);
            }
          });
          
          if (idsPre.length) {
            await marcarComoLeidas(idsPre, 'preoperacion');
          }
          
          if (idsPost.length) {
            await marcarComoLeidas(idsPost, 'postoperacion');
          }
        } else {
          await marcarComoLeidas(ids, tipo);
        }
        
        // Actualizar estado local
        this.actualizarEstadoLeido(ids, true);
        
        // Reducir contador
        this.noLeidas = Math.max(0, this.noLeidas - ids.length);
        
      } catch (err: any) {
        console.error('❌ Error marcando como leídas:', err);
        throw err;
      }
    },
    
    // Marcar todas como leídas (mantener igual)
    async marcarTodas(tipo?: string) {
      try {
        if (tipo) {
          await marcarTodasComoLeidas(tipo);
        } else {
          await Promise.all([
            marcarTodasComoLeidas('preoperacion'),
            marcarTodasComoLeidas('postoperacion')
          ]);
        }
        
        // Actualizar estado local
        this.actualizarTodasLeidas();
        this.noLeidas = 0;
        
      } catch (err: any) {
        console.error('❌ Error marcando todas como leídas:', err);
        throw err;
      }
    },
    // NUEVO: Actualizar notificaciones de hoy directamente (usado por Home.vue)
    actualizarNotificacionesHoy(notificacionesPre: Notificacion[], notificacionesPost: Notificacion[]) {
      // Combinar y ordenar por fecha
      this.notificacionesHoy = [...notificacionesPre, ...notificacionesPost]
        .sort((a, b) => new Date(b.fecha_cambio || '').getTime() - new Date(a.fecha_cambio || '').getTime());
      
      // También actualizar el array general para compatibilidad
      if (this.notificaciones.length === 0) {
        this.notificaciones = this.notificacionesHoy;
      }
      
      this.ultimaActualizacion = Date.now();
      console.log(`📊 Store actualizado con ${this.notificacionesHoy.length} notificaciones de hoy`);
    },

    // HELPER: Actualizar estado leído localmente
    actualizarEstadoLeido(ids: number[], leido: boolean) {
      // Actualizar notificaciones principales
      this.notificaciones = this.notificaciones.map(n => 
        ids.includes(n.id) ? { ...n, leido } : n
      );
      
      this.notificacionesHoy = this.notificacionesHoy.map(n => 
        ids.includes(n.id) ? { ...n, leido } : n
      );
      
      // Actualizar caché
      Object.keys(this.cachePorMes).forEach(claveMes => {
        const mes = this.cachePorMes[claveMes];
        
        mes.preoperacion.data = mes.preoperacion.data.map(n => 
          ids.includes(n.id) ? { ...n, leido } : n
        );
        
        mes.postoperacion.data = mes.postoperacion.data.map(n => 
          ids.includes(n.id) ? { ...n, leido } : n
        );
      });
    },
    
    // HELPER: Marcar todas como leídas localmente
    actualizarTodasLeidas() {
      this.notificaciones = this.notificaciones.map(n => ({ ...n, leido: true }));
      this.notificacionesHoy = this.notificacionesHoy.map(n => ({ ...n, leido: true }));
      
      // Actualizar caché
      Object.keys(this.cachePorMes).forEach(claveMes => {
        const mes = this.cachePorMes[claveMes];
        
        mes.preoperacion.data = mes.preoperacion.data.map(n => ({ ...n, leido: true }));
        mes.postoperacion.data = mes.postoperacion.data.map(n => ({ ...n, leido: true }));
      });
    },
    
    // Limpiar todo el estado (útil para logout)
    limpiarNotificaciones() {
      this.notificaciones = [];
      this.notificacionesHoy = [];
      this.noLeidas = 0;
      this.error = null;
      this.ultimaActualizacion = 0;
      this.cachePorMes = {};
      this.mesActual = '';
      
      console.log('🧹 Estado de notificaciones limpiado');
    }
  }
});