export interface Departamento {
    cod_depto: number;
    nom_depto: string;
  }
  
  export interface Municipio {
    cod_municipio: number;
    nom_municipio: string;
    cod_depto: number;
    fecha_inicio: string | null;
    nom_territorial: string | null;
    mecanismo_general: string | null;
    mecanismo_detalle: string | null;
    alcance_operacion: string | null;
    grupo: string | null;
    mecanismo_operacion: string | null;
    // Relaciones
    departamento?: Departamento;
    territorial_info?: any;
    mecanismo_detalle_info?: any;
    alcance_operacion_info?: any;
    grupo_info?: any;
    mecanismo_operacion_info?: any;
  }
  
  export interface Insumo {
    cod_insumo: number;
    cod_municipio: number;
    cod_categoria: number;
    tipo_insumo: string;
    // Relaciones
    municipio?: Municipio;
    categoria?: Categoria;
  }
  
  export interface Categoria {
    cod_categoria: number;
    nom_categoria: string;
  }
  
  export interface ClasificacionInsumo {
    cod_clasificacion: number;
    cod_insumo: number;
    nombre: string;
    observacion: string | null;
    ruta: string | null;
    descripcion: string | null;
    // Relación
    insumo?: Insumo;
  }
  
  export interface ComponentePost {
    id_componente: number;
    nombre_componente: string;
  }
  
  export interface DisposicionPost {
    id_disposicion: number;
    cod_municipio: number;
    id_componente: number;
    dispuesto: boolean;
    fecha_disposicion: string | null;
    ruta_acceso: string | null;
    evaluado: boolean;
    aprobado: boolean;
    observaciones: string | null;
    // Relaciones
    municipio?: Municipio;
    componente?: ComponentePost;
  }
  
  export interface ArchivoPost {
    id_archivo: number;
    id_disposicion: number;
    nombre_archivo: string;
    ruta_completa: string;
    fecha_disposicion: string | null;
    observacion: string | null;
    // Relación
    disposicion?: DisposicionPost;
  }
  
  export interface MunicipioState {
    municipios: Municipio[];
    municipioSeleccionado: Municipio | null;
    cargando: boolean;
    error: string | null;
  }