// Interfaces para el módulo de insumos

export interface Departamento {
  cod_depto: number;
  nom_depto: string;
}

export interface Municipio {
  cod_municipio: number;
  nom_municipio: string;
  cod_depto: number | Departamento;
  fecha_inicio?: string;
  mecanismo_general?: string;
  mecanismo_detalle?: string;
  alcance_operacion?: string;
  grupo?: string;
  mecanismo_operacion?: string;
  nom_territorial?: string;
  area?: string;
}

export interface Categoria {
  cod_categoria: number;
  nom_categoria: string;
}

export interface TipoInsumo {
  tipo_insumo: string;
}

export interface Insumo {
  cod_insumo: number;
  cod_municipio: number;
  cod_categoria: number;
  tipo_insumo: string;
  
  // Propiedades expandidas (no en la DB directamente)
  municipio?: Municipio;
  categoria?: Categoria;
}

export interface ClasificacionInsumo {
  cod_clasificacion: number;
  cod_insumo: number;
  nombre: string;
  observacion?: string;
  ruta?: string;
  descripcion?: string;
  
  // Propiedades expandidas
  insumo?: Insumo;
}

export interface Entidad {
  cod_entidad: string;
  nom_entidad: string;
}

export interface TipoFormato {
  cod_formato_tipo: string;
}

export interface Usuario {
  cod_usuario: number;
  nombre: string;
  correo?: string;
}

export interface Zona {
  zona: string;
}

export interface EstadoInsumo {
  estado: string;
}

export interface DetalleInsumo {
  cod_detalle: number;
  escala?: string;
  estado?: string; 
  cubrimiento?: string;
  fecha_entrega?: string;
  fecha_disposicion?: string;
  area?: string;
  cod_entidad: string;
  observacion?: string;
  vigencia?: string;
  formato_tipo: string;
  cod_usuario: number;
  cod_clasificacion: number;
  zona?: string;
  
  // Propiedades expandidas
  entidad?: Entidad;
  formato?: TipoFormato;
  usuario?: Usuario;
  clasificacion?: ClasificacionInsumo;
  zona_info?: Zona;
}

export interface Concepto {
  cod_concepto: number;
  concepto: string;
  fecha?: string;
  evaluacion?: string;
  detalle_concepto?: string;
  observacion?: string;
  pdf?: string;
  cod_detalle?: number;
}

export interface ArchivoPreOperacion {
  id_lista_archivo: number;
  cod_insumo: number; // Referencia a ClasificacionInsumo.cod_clasificacion
  nombre_insumo?: string;
  fecha_disposicion?: string;
  observacion?: string;
  path_file?: string;
}

export interface ProfesionalSeguimiento {
  cod_profesional: string;
  nombre_profesional: string;
  correo_profesional?: string;
  rol_profesional: string;
}

export interface MecanismoGeneral {
  cod_mecanismo: string;
  descripcion?: string;
}

export interface MecanismoDetalle {
  cod_mecanismo_detalle: string;
  descripcion?: string;
}

export interface AlcanceOperacion {
  cod_alcance: string;
}

export interface Grupo {
  cod_grupo: string;
  descripcion?: string;
}

export interface MecanismoOperacion {
  cod_operacion: string;
  descripcion?: string;
}

export interface TerritorialIgac {
  nom_territorial: string;
}