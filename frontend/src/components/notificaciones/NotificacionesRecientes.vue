<template>
  <div class="notificaciones-recientes">
    <div class="header">
      <h2 class="title">
        <i class="material-icons">notifications</i>
        Notificaciones Recientes
      </h2>
      <div class="actions">
        <button class="refresh-button" @click="cargarNotificaciones" :disabled="cargando">
          <i class="material-icons">refresh</i>
        </button>
        <button v-if="notificacionesNoLeidas > 0" class="mark-read-button" @click="marcarTodasLeidas">
          <i class="material-icons">done_all</i>
        </button>
      </div>
    </div>
    
    <div v-if="cargando" class="loading">
      <div class="spinner"></div>
      <span>Cargando notificaciones...</span>
    </div>
    
    <div v-else-if="error" class="error-message">
      <i class="material-icons">error</i>
      <span>{{ error }}</span>
      <button @click="cargarNotificaciones">Reintentar</button>
    </div>
    
    <div v-else-if="notificaciones.length === 0" class="empty-message">
      <i class="material-icons">notifications_none</i>
      <span>No hay notificaciones recientes</span>
    </div>
    
    <ul v-else class="notificaciones-lista">
      <li 
        v-for="notificacion in notificacionesLimitadas" 
        :key="notificacion.id"
        :class="{ 'no-leida': !notificacion.leido }"
        @click="verDetalle(notificacion)"
      >
        <div class="notificacion-icon">
          <i class="material-icons">{{ getIconoTipo(notificacion.accion) }}</i>
        </div>
        <div class="notificacion-content">
          <div class="notificacion-title">
            {{ getTitulo(notificacion) }}
            <span v-if="!notificacion.leido" class="badge">Nueva</span>
          </div>
          <div class="notificacion-description">{{ notificacion.descripcion }}</div>
          <div class="notificacion-meta">
            <span class="tiempo">{{ formatearTiempo(notificacion.fecha_cambio) }}</span>
            <span class="tipo">{{ formatearTipo(notificacion.tipo_entidad) }}</span>
          </div>
        </div>
        <button class="mark-read" @click.stop="marcarLeida(notificacion)" v-if="!notificacion.leido">
          <i class="material-icons">done</i>
        </button>
      </li>
    </ul>
    
    <div v-if="notificaciones.length > limiteNotificaciones" class="ver-mas">
      <button @click="verTodasNotificaciones">
        Ver todas las notificaciones 
        <i class="material-icons">arrow_forward</i>
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificacionesStore } from '@/store/notificaciones'
import type { Notificacion } from '@/models/notificacion'
import { format, parseISO, formatDistance } from 'date-fns'
import { es } from 'date-fns/locale'

export default defineComponent({
  name: 'NotificacionesRecientes',
  
  props: {
    limite: {
      type: Number,
      default: 5
    }
  },
  
  setup(props) {
    const router = useRouter()
    const notificacionesStore = useNotificacionesStore()
    
    // Estado local
    const limiteNotificaciones = ref(props.limite)
    
    // Referencias al store
    const notificaciones = computed(() => notificacionesStore.notificaciones)
    const notificacionesNoLeidas = computed(() => notificacionesStore.noLeidas)
    const cargando = computed(() => notificacionesStore.cargando)
    const error = computed(() => notificacionesStore.error)
    
    // Notificaciones limitadas para mostrar
    const notificacionesLimitadas = computed(() => {
      return notificaciones.value.slice(0, limiteNotificaciones.value)
    })
    
    // Cargar notificaciones al montar
    onMounted(() => {
      cargarNotificaciones()
    })
    
    // Método para cargar notificaciones
    const cargarNotificaciones = async () => {
      await notificacionesStore.cargarNotificaciones()
    }
    
    // Obtener icono según tipo de acción
    const getIconoTipo = (accion: string): string => {
      switch(accion) {
        case 'crear':
          return 'add_circle'
        case 'actualizar':
          return 'update'
        case 'eliminar':
          return 'delete'
        case 'aprobar':
          return 'check_circle'
        case 'rechazar':
          return 'cancel'
        default:
          return 'notifications'
      }
    }
    
    // Obtener título de la notificación
    const getTitulo = (notificacion: Notificacion): string => {
      const entidad = formatearTipo(notificacion.tipo_entidad)
      
      switch(notificacion.accion) {
        case 'crear':
          return `Nuevo ${entidad} creado`
        case 'actualizar':
          return `${entidad} actualizado`
        case 'eliminar':
          return `${entidad} eliminado`
        case 'aprobar':
          return `${entidad} aprobado`
        case 'rechazar':
          return `${entidad} rechazado`
        default:
          return `Notificación de ${entidad}`
      }
    }
    
    // Formatear tipo de entidad
    const formatearTipo = (tipo: string): string => {
      const mapaTipos: Record<string, string> = {
        'municipio': 'Municipio',
        'insumo': 'Insumo',
        'clasificacion': 'Clasificación',
        'detalle': 'Detalle',
        'componente': 'Componente',
        'disposicion': 'Disposición',
        'archivo': 'Archivo'
      }
      
      return mapaTipos[tipo.toLowerCase()] || tipo
    }
    
    // En NotificacionesRecientes.vue, dentro del setup()
    const formatearTiempo = (fechaStr: string): string => {
      try {
        // Convertir la cadena de fecha a un objeto Date
        const fechaObj = new Date(fechaStr);
        // Fecha actual
        const ahora = new Date();
        
        // Comprobar validez
        if (isNaN(fechaObj.getTime())) {
          return "fecha desconocida";
        }
        
        // Cálculo de diferencia en días, horas, minutos
        const diffMs = ahora.getTime() - fechaObj.getTime();
        const diffMinutos = Math.floor(diffMs / (1000 * 60));
        const diffHoras = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDias = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        
        // Formateo basado en la diferencia de tiempo
        if (diffMinutos < 1) {
          return "justo ahora";
        } else if (diffMinutos < 60) {
          return `hace ${diffMinutos} ${diffMinutos === 1 ? 'minuto' : 'minutos'}`;
        } else if (diffHoras < 24) {
          return `hace ${diffHoras} ${diffHoras === 1 ? 'hora' : 'horas'}`;
        } else if (diffDias < 30) {
          return `hace ${diffDias} ${diffDias === 1 ? 'día' : 'días'}`;
        } else {
          // Formato de fecha completo para fechas más antiguas
          return fechaObj.toLocaleDateString('es-ES', {
            day: 'numeric', 
            month: 'long', 
            year: 'numeric'
          });
        }
      } catch (error) {
        console.error('Error al formatear tiempo:', error, fechaStr);
        return fechaStr || "fecha desconocida";
      }
    }

    const ajustarZonaHoraria = (fecha: string): Date => {
      const fechaObj = new Date(fecha);
      
      // Si la fecha está en UTC o zona horaria diferente, ajústala
      // a la zona horaria local si es necesario
      if (fecha.includes('Z') || fecha.includes('+')) {
        // La fecha ya tiene información de zona horaria
        return fechaObj;
      }
      
      // Si la fecha no tiene información de zona horaria,
      // asumimos que está en la zona horaria local
      return new Date(
        fechaObj.getFullYear(),
        fechaObj.getMonth(),
        fechaObj.getDate(),
        fechaObj.getHours(),
        fechaObj.getMinutes(),
        fechaObj.getSeconds()
      );
    }

    // Ver detalle de notificación
    const verDetalle = (notificacion: Notificacion) => {
      // Si no está leída, marcarla como leída
      if (!notificacion.leido) {
        marcarLeida(notificacion)
      }
      
      // Navegar a la entidad correspondiente
      if (notificacion.tipo_entidad === 'municipio') {
        router.push(`/municipio/${notificacion.id_entidad}`)
      } else if (notificacion.tipo_entidad === 'componente') {
        router.push(`/disposicion-informacion?componente=${notificacion.id_entidad}`)
      } else if (notificacion.tipo_entidad === 'disposicion') {
        router.push(`/estado-producto?disposicion=${notificacion.id_entidad}`)
      } else {
        // Si no hay navegación específica, mostrar todas las notificaciones
        router.push('/notificaciones')
      }
    }
    
    // Marcar una notificación como leída
    const marcarLeida = async (notificacion: Notificacion) => {
      // Determinar si es notificación de pre o post operación
      const tipo = notificacion.id < 1000000 ? 'preoperacion' : 'postoperacion'
      await notificacionesStore.marcarLeidas([notificacion.id], tipo)
    }
    
    // Marcar todas las notificaciones como leídas
    const marcarTodasLeidas = async () => {
      // Primero marcar todas las de preoperación
      await notificacionesStore.marcarTodas('preoperacion')
      // Luego marcar todas las de postoperación
      await notificacionesStore.marcarTodas('postoperacion')
    }
    
    // Ver todas las notificaciones
    const verTodasNotificaciones = () => {
      router.push('/notificaciones')
    }
    
    return {
      notificaciones,
      notificacionesLimitadas,
      notificacionesNoLeidas,
      cargando,
      error,
      limiteNotificaciones,
      cargarNotificaciones,
      getIconoTipo,
      getTitulo,
      formatearTipo,
      formatearTiempo,
      verDetalle,
      marcarLeida,
      marcarTodasLeidas,
      verTodasNotificaciones,
      formatearTiempo,
      ajustarZonaHoraria
    }
  }
})
</script>

<style scoped>
.notificaciones-recientes {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 1.2rem;
  color: #343a40;
}

.title i {
  color: #007bff;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.actions button {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.actions button:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: #007bff;
}

.actions button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading,
.error-message,
.empty-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  color: #6c757d;
}

.loading .spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message i,
.empty-message i {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.error-message i {
  color: #dc3545;
}

.error-message button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.notificaciones-lista {
  list-style: none;
  padding: 0;
  margin: 0;
}

.notificaciones-lista li {
  display: flex;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e9ecef;
  transition: background-color 0.2s;
  cursor: pointer;
  position: relative;
}

.notificaciones-lista li:hover {
  background-color: #f8f9fa;
}

.notificaciones-lista li.no-leida {
  background-color: #e8f4ff;
}

.notificaciones-lista li.no-leida:hover {
  background-color: #d8eeff;
}

.notificacion-icon {
  display: flex;
  align-items: flex-start;
  padding-top: 0.25rem;
  margin-right: 1rem;
}

.notificacion-icon i {
  font-size: 1.5rem;
  color: #007bff;
}

.notificacion-content {
  flex: 1;
}

.notificacion-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: bold;
  color: #343a40;
  margin-bottom: 0.25rem;
}

.badge {
  font-size: 0.7rem;
  font-weight: normal;
  background-color: #dc3545;
  color: white;
  padding: 0.1rem 0.4rem;
  border-radius: 10px;
}

.notificacion-description {
  color: #495057;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.notificacion-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: #6c757d;
  font-size: 0.8rem;
}

.mark-read {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  transition: background-color 0.2s;
  opacity: 0;
}

.notificaciones-lista li:hover .mark-read {
  opacity: 1;
}

.mark-read:hover {
  background-color: rgba(0, 123, 255, 0.1);
}

.ver-mas {
  display: flex;
  justify-content: center;
  padding: 1rem;
  border-top: 1px solid #e9ecef;
}

.ver-mas button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.ver-mas button:hover {
  background-color: rgba(0, 123, 255, 0.05);
}

@media (max-width: 768px) {
  .title {
    font-size: 1.1rem;
  }
  
  .notificacion-icon {
    display: none;
  }
  
  .notificacion-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>