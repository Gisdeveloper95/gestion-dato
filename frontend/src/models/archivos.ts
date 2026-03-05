// Modelo para archivo de preoperación
export interface ArchivoPre {
    id_lista_archivo: number;
    cod_insumo: number; // Referencia a clasificación
    nombre_insumo?: string;
    fecha_disposicion?: string;
    observacion?: string;
    path_file?: string;
  }
  
  // Modelo para archivo de postoperación
  export interface ArchivoPost {
    id_archivo: number;
    id_disposicion: number;
    nombre_archivo: string;
    ruta_completa: string;
    fecha_disposicion?: string;
    observacion?: string;
    disposicion_info?: {
      id_disposicion: number;
      componente: string;
      dispuesto: boolean;
      aprobado: boolean;
    };
  }