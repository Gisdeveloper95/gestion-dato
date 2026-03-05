// models/notificacion.ts - VERSIÓN ACTUALIZADA

export interface Notificacion {
  id: number;
  tipo_entidad: string;
  id_entidad: number;
  accion: string;
  descripcion: string | null;
  datos_contexto: {
    municipio_id?: number;
    cod_municipio?: number;
    municipio?: string;
    municipio_nombre?: string;
    nom_municipio?: string;
    usuario_windows?: string;
    usuario?: string;
    componente?: string;
    nombre_componente?: string;
    categoria?: string;
    tipo_insumo?: string;
    estado?: string;
    departamento?: string;
    nom_depto?: string;
    [key: string]: any;
  } | null;
  fecha_cambio: string;
  leido: boolean;
  
  // Campos opcionales adicionales
  usuario_windows?: string;
  
  // Campo para identificar el tipo de sistema (se añade en el frontend)
  tipo_sistema?: 'preoperacion' | 'postoperacion';
}

export interface NotificacionPreoperacion extends Notificacion {
  // Campos específicos de notificaciones de preoperación, si los hay
  tipo_sistema: 'preoperacion';
}

export interface NotificacionPostoperacion extends Notificacion {
  // Campos específicos de notificaciones de postoperación, si los hay
  tipo_sistema: 'postoperacion';
}

export interface ResumenNotificaciones {
  total_no_leidas: number;
  por_tipo: {
    tipo_entidad: string;
    total: number;
  }[];
  ultimas: Notificacion[];
}

export interface NotificacionState {
  notificaciones: Notificacion[];
  notificacionesHoy: Notificacion[];
  noLeidas: number;
  cargando: boolean;
  cargandoHoy: boolean;
  cargandoMes: boolean;
  error: string | null;
  ultimaActualizacion: number;
  mesActual: string;
}

// Tipos auxiliares para filtros
export interface FiltrosNotificacion {
  tipo_entidad?: string;
  accion?: string;
  leido?: boolean;
  fecha_desde?: string;
  fecha_hasta?: string;
  fecha_especifica?: string;
  municipio?: string;
  periodo?: 'hoy' | 'semana' | 'mes';
  page_size?: number;
  limite?: number;
}

// Tipo para respuesta de API
export interface RespuestaNotificaciones {
  results?: Notificacion[];
  count?: number;
  next?: string | null;
  previous?: string | null;
}

// Tipos para el caché
export interface CacheNotificacion {
  data: Notificacion[];
  timestamp: number;
}

export interface CachePorMes {
  [claveMes: string]: {
    preoperacion: CacheNotificacion;
    postoperacion: CacheNotificacion;
  };
}

// Utilidades para trabajar con notificaciones
export const NotificacionUtils = {
  /**
   * Determina si una notificación es de preoperación
   */
  esPreoperacion(notificacion: Notificacion): boolean {
    if (notificacion.tipo_sistema) {
      return notificacion.tipo_sistema === 'preoperacion';
    }
    // Fallback basado en ID (preoperación tiene IDs menores)
    return notificacion.id < 1000000;
  },

  /**
   * Determina si una notificación es de postoperación
   */
  esPostoperacion(notificacion: Notificacion): boolean {
    return !this.esPreoperacion(notificacion);
  },

  /**
   * Extrae el nombre del municipio de una notificación
   */
  getMunicipio(notificacion: Notificacion): string {
    if (!notificacion.datos_contexto) return '';
    
    const ctx = notificacion.datos_contexto;
    return ctx.municipio || ctx.municipio_nombre || ctx.nom_municipio || '';
  },

  /**
   * Extrae el nombre del usuario de una notificación
   */
  getUsuario(notificacion: Notificacion): string {
    if (notificacion.usuario_windows) return notificacion.usuario_windows;
    if (!notificacion.datos_contexto) return '';
    
    const ctx = notificacion.datos_contexto;
    return ctx.usuario_windows || ctx.usuario || '';
  },

  /**
   * Formatea el tipo de entidad para mostrar
   */
  formatearTipoEntidad(tipo: string): string {
    const mapaTipos: Record<string, string> = {
      'municipio': 'Municipio',
      'insumo': 'Insumo',
      'clasificacion': 'Clasificación',
      'detalle': 'Detalle',
      'componente': 'Componente',
      'disposicion': 'Disposición',
      'archivo': 'Archivo'
    };
    
    return mapaTipos[tipo?.toLowerCase()] || tipo || 'Desconocido';
  },

  /**
   * Formatea la acción para mostrar
   */
  formatearAccion(accion: string): string {
    const mapaAcciones: Record<string, string> = {
      'crear': 'Crear',
      'actualizar': 'Actualizar',
      'eliminar': 'Eliminar',
      'aprobar': 'Aprobar',
      'rechazar': 'Rechazar',
      'disponer': 'Disponer',
      'evaluar': 'Evaluar',
      'INSERT': 'Crear',
      'UPDATE': 'Actualizar',
      'DELETE': 'Eliminar'
    };
    
    return mapaAcciones[accion] || accion || 'Desconocido';
  },

  /**
   * Genera una clave para el caché por mes
   */
  generarClaveMes(fecha: Date): string {
    return `${fecha.getFullYear()}-${(fecha.getMonth() + 1).toString().padStart(2, '0')}`;
  },

  /**
   * Verifica si una notificación es de hoy
   */
  esDeHoy(notificacion: Notificacion): boolean {
    if (!notificacion.fecha_cambio) return false;
    
    const fechaNotif = new Date(notificacion.fecha_cambio);
    const hoy = new Date();
    
    return fechaNotif.toDateString() === hoy.toDateString();
  }
};