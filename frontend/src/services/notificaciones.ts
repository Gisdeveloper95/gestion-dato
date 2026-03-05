// src/services/notificaciones.ts - Archivo nuevo para centralizar la lógica

import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useNotificacionesStore } from '@/store/notificaciones';

// Intervalo global para notificaciones (compartido entre componentes)
let pollingInterval: number | null = null;
let pollingSuscribers = 0;

export function useNotificaciones(intervaloMs = 5000) {
  const notificacionesStore = useNotificacionesStore();
  
  onMounted(() => {
    // Incrementar contador de suscriptores
    pollingSuscribers++;
    
    // Si es el primer suscriptor, iniciar polling
    if (pollingSuscribers === 1) {
      // Cargar inmediatamente las notificaciones al montar
      notificacionesStore.cargarNotificaciones();
      
      // Configurar intervalo de polling
      pollingInterval = window.setInterval(() => {
        notificacionesStore.cargarNotificaciones();
      }, intervaloMs);
      
      console.log(`Polling de notificaciones iniciado (cada ${intervaloMs}ms)`);
    }
  });
  
  onBeforeUnmount(() => {
    // Decrementar contador de suscriptores
    pollingSuscribers--;
    
    // Si no quedan suscriptores, detener polling
    if (pollingSuscribers <= 0) {
      pollingSuscribers = 0;
      
      if (pollingInterval !== null) {
        clearInterval(pollingInterval);
        pollingInterval = null;
        console.log('Polling de notificaciones detenido');
      }
    }
  });
  
  return {
    notificaciones: notificacionesStore.notificaciones,
    noLeidas: notificacionesStore.noLeidas,
    cargando: notificacionesStore.cargando,
    error: notificacionesStore.error,
    cargarNotificaciones: notificacionesStore.cargarNotificaciones,
    marcarLeidas: notificacionesStore.marcarLeidas,
    marcarTodas: notificacionesStore.marcarTodas
  };
}