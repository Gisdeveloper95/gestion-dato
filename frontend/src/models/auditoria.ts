export interface AuditoriaItem {
    id: number;
    usuario: number | null;
    usuario_nombre: string | null;
    fecha_hora: string;
    tipo_entidad: string;
    id_entidad: number;
    accion: string;
    detalles: Record<string, any> | null;
    ip_origen: string | null;
    entidad_info: Record<string, any> | null;
  }