// src/models/historialPropietarios.ts
export interface HistorialPropietario {
  id: number;
  tipo_archivo: 'preoperacion' | 'postoperacion';
  id_archivo: number;
  id_notificacion: number | null;
  propietario_anterior: string | null;
  propietario_nuevo: string;
  fecha_inicio: string;
  fecha_fin: string | null;
  detalles: Record<string, any>;
  estado?: string;
  duracion?: string;
  nombre_archivo?: string;
}

export interface HistorialPropietarioFiltros {
  tipo?: string;
  id_archivo?: number;
  usuario?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
  solo_actuales?: boolean;
}