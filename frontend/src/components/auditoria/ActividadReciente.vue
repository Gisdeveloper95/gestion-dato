<template>
    <div class="panel-section">
      <div class="section-header">
        <h2 class="section-title">Actividad Reciente</h2>
        <button class="refresh-button" @click="cargarActividad" :disabled="cargando">
          <i class="material-icons">refresh</i>
        </button>
      </div>
      
      <div v-if="cargando" class="loading-indicator">
        <div class="spinner"></div>
        <span>Cargando actividad reciente...</span>
      </div>
      
      <div v-else-if="error" class="error-message">
        <i class="material-icons">error</i>
        <span>{{ error }}</span>
        <button @click="cargarActividad">Reintentar</button>
      </div>
      
      <div v-else class="activity-list">
        <div v-for="(actividad, index) in recentActivity" :key="index" class="activity-item">
          <div class="activity-icon">
            <i class="material-icons">{{ getActivityIcon(actividad.tipo_entidad) }}</i>
          </div>
          <div class="activity-details">
            <p class="activity-description">{{ getDescripcionFormateada(actividad) }}</p>
            <span class="activity-time">{{ formatearTiempo(actividad.fecha_hora) }}</span>
            <div class="activity-meta" v-if="actividad.usuario_nombre">
              <i class="material-icons">person</i>
              <span>{{ actividad.usuario_nombre }}</span>
            </div>
          </div>
        </div>
        
        <div v-if="recentActivity.length === 0" class="empty-activity">
          <i class="material-icons">info</i>
          <p>No hay actividad reciente para mostrar</p>
        </div>
        
        <div v-if="recentActivity.length > 0 && hayMasActividades" class="load-more">
          <button @click="verHistorialCompleto" :disabled="cargandoMas">
            <span>Ver historial completo</span>
            <i class="material-icons">arrow_forward</i>
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { getUltimasActividades } from '@/api/auditoria'
  import type { AuditoriaItem } from '@/models/auditoria'
  import { format, parseISO, isToday, isYesterday, formatDistance } from 'date-fns'
  import { es } from 'date-fns/locale'
  
  export default defineComponent({
    name: 'ActividadRecenteGestion',
    
    props: {
      limite: {
        type: Number,
        default: 5
      }
    },
    
    setup(props) {
      const router = useRouter()
      
      // Estado
      const recentActivity = ref<AuditoriaItem[]>([])
      const cargando = ref(false)
      const cargandoMas = ref(false)
      const error = ref<string | null>(null)
      const hayMasActividades = ref(true)
      
      // Cargar actividad reciente
      const cargarActividad = async () => {
        try {
          cargando.value = true
          error.value = null
          
          // Llamar a la API real
          const data = await getUltimasActividades(props.limite)
          recentActivity.value = data
          
          // Determinar si hay más actividades (solo una heurística, ajustar según API real)
          hayMasActividades.value = data.length >= props.limite
          
          return true
        } catch (err: any) {
          console.error('Error al cargar actividad:', err)
          error.value = err.message || 'Error al cargar la actividad reciente'
          return false
        } finally {
          cargando.value = false
        }
      }
      
      // Ver historial completo
      const verHistorialCompleto = () => {
        router.push('/gestion-informacion/auditoria')
      }
      
      // Obtener icono según tipo de actividad
      const getActivityIcon = (tipo: string): string => {
        switch (tipo.toLowerCase()) {
          case 'insumo':
            return 'folder'
          case 'clasificacion':
            return 'category'
          case 'detalle':
            return 'list_alt'
          case 'concepto':
            return 'comment'
          case 'municipio':
            return 'location_city'
          case 'usuario':
            return 'person'
          default:
            return 'info'
        }
      }
      
      // Formatear descripción
      const getDescripcionFormateada = (actividad: AuditoriaItem): string => {
        const tipoEntidad = formatearTipoEntidad(actividad.tipo_entidad)
        const accion = formatearAccion(actividad.accion)
        
        let descripcion = `Se ${accion} ${tipoEntidad}`
        
        // Añadir información adicional si está disponible
        if (actividad.entidad_info) {
          if (actividad.entidad_info.nombre) {
            descripcion += ` "${actividad.entidad_info.nombre}"`
          } else if (actividad.entidad_info.concepto) {
            descripcion += ` "${actividad.entidad_info.concepto}"`
          }
          
          if (actividad.entidad_info.municipio) {
            descripcion += ` en ${actividad.entidad_info.municipio}`
          }
        } else {
          descripcion += ` #${actividad.id_entidad}`
        }
        
        return descripcion
      }
      
      // Formatear tipo de entidad
      const formatearTipoEntidad = (tipo: string): string => {
        const mapaTipos: Record<string, string> = {
          'municipio': 'municipio',
          'insumo': 'insumo',
          'clasificacion': 'clasificación',
          'detalle': 'detalle',
          'concepto': 'concepto',
          'usuario': 'usuario'
        }
        
        return mapaTipos[tipo.toLowerCase()] || tipo
      }
      
      // Formatear acción
      const formatearAccion = (accion: string): string => {
        const mapaAcciones: Record<string, string> = {
          'crear': 'creó',
          'actualizar': 'actualizó',
          'eliminar': 'eliminó',
          'consultar': 'consultó'
        }
        
        return mapaAcciones[accion.toLowerCase()] || accion
      }
      
      // Formatear tiempo
      const formatearTiempo = (fecha: string): string => {
        try {
          const fechaObj = parseISO(fecha)
          
          if (isToday(fechaObj)) {
            return `Hoy, ${format(fechaObj, 'HH:mm')}`
          }
          
          if (isYesterday(fechaObj)) {
            return `Ayer, ${format(fechaObj, 'HH:mm')}`
          }
          
          // Si es de esta semana, mostrar día y hora
          if (fechaObj > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)) {
            return format(fechaObj, "EEEE 'a las' HH:mm", { locale: es })
          }
          
          // Para fechas más antiguas
          return formatDistance(fechaObj, new Date(), { addSuffix: true, locale: es })
        } catch (error) {
          return fecha
        }
      }
      
      // Cargar datos al montar
      onMounted(async () => {
        await cargarActividad()
      })
      
      return {
        recentActivity,
        cargando,
        cargandoMas,
        error,
        hayMasActividades,
        getActivityIcon,
        getDescripcionFormateada,
        formatearTiempo,
        cargarActividad,
        verHistorialCompleto
      }
    }
  })
  </script>
  
  <style scoped>
  .panel-section {
    background-color: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  }
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }
  
  .section-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin: 0;
    color: #343a40;
  }
  
  .refresh-button {
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
  
  .refresh-button:hover {
    background-color: rgba(0, 0, 0, 0.05);
    color: #007bff;
  }
  
  .refresh-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .loading-indicator {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    color: #6c757d;
  }
  
  .spinner {
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
  
  .activity-list {
    display: flex;
    flex-direction: column;
  }
  
  .activity-item {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1rem;
    border-bottom: 1px solid #e9ecef;
  }
  
  .activity-item:last-child {
    border-bottom: none;
  }
  
  .activity-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: rgba(0, 123, 255, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  
  .activity-icon i {
    font-size: 1.2rem;
    color: #007bff;
  }
  
  .activity-details {
    flex: 1;
  }
  
  .activity-description {
    margin: 0 0 0.25rem;
    color: #343a40;
  }
  
  .activity-time {
    font-size: 0.85rem;
    color: #6c757d;
    display: block;
    margin-bottom: 0.25rem;
  }
  
  .activity-meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    color: #6c757d;
  }
  
  .activity-meta i {
    font-size: 1rem;
  }
  
  .error-message {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    text-align: center;
    color: #6c757d;
  }
  
  .error-message i {
    font-size: 3rem;
    margin-bottom: 1rem;
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
  
  .empty-activity {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
    color: #6c757d;
    text-align: center;
  }
  
  .empty-activity i {
    font-size: 3rem;
    margin-bottom: 1rem;
    color: #adb5bd;
  }
  
  .load-more {
    display: flex;
    justify-content: center;
    margin-top: 1rem;
  }
  
  .load-more button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: none;
    border: none;
    color: #007bff;
    cursor: pointer;
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    transition: background-color 0.2s;
  }
  
  .load-more button:hover {
    background-color: rgba(0, 123, 255, 0.1);
  }
  
  .load-more button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  @media (max-width: 768px) {
    .activity-icon {
      width: 32px;
      height: 32px;
    }
    
    .activity-icon i {
      font-size: 1rem;
    }
  }
  </style>