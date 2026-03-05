import type { DominioKey } from '@/api/dominios'

// =============== INTERFACE PARA CONFIGURACIÓN ===============
export interface DominioConfig {
  key: DominioKey
  title: string
  description: string
  singularName: string
  pluralName: string
  idField: string
  columns: Array<{
    key: string
    label: string
    type?: 'text' | 'number' | 'select' | 'textarea'
    editable?: boolean
    required?: boolean
    sortable?: boolean
    placeholder?: string
    maxLength?: number
  }>
  searchFields: string[]
}

// =============== CONFIGURACIONES DE DOMINIOS ===============
export const DOMINIOS_CONFIG: Record<string, DominioConfig> = {
  // ========== ALCANCE OPERACIÓN ==========
  alcance_operacion: {
    key: 'alcance_operacion',
    title: 'Alcance de Operación',
    description: 'Gestión de alcances operacionales del sistema',
    singularName: 'Alcance',
    pluralName: 'Alcances',
    idField: 'cod_alcance',
    columns: [
      {
        key: 'cod_alcance',
        label: 'Código',
        type: 'text',
        required: true,
        sortable: true,
        placeholder: 'Ej: ALC001',
        maxLength: 10
      }
    ],
    searchFields: ['cod_alcance']
  },

  // ========== CATEGORÍAS ==========
  categorias: {
    key: 'categorias',
    title: 'Categorías de Insumos',
    description: 'Clasificación de categorías para organizar insumos',
    singularName: 'Categoría',
    pluralName: 'Categorías',
    idField: 'cod_categoria',
    columns: [
      {
        key: 'cod_categoria',
        label: 'Código',
        type: 'number',
        required: true,
        sortable: true,
        editable: false
      },
      {
        key: 'nom_categoria',
        label: 'Nombre',
        type: 'text',
        required: true,
        sortable: true,
        placeholder: 'Nombre de la categoría',
        maxLength: 100
      }
    ],
    searchFields: ['nom_categoria', 'cod_categoria']
  },

  // ========== COMPONENTES POST ==========
  componentes_post: {
    key: 'componentes_post',
    title: 'Componentes Post-operación',
    description: 'Gestión de componentes para procesos post-operativos',
    singularName: 'Componente',
    pluralName: 'Componentes',
    idField: 'id_componente',
    columns: [
      {
        key: 'id_componente',
        label: 'ID',
        type: 'number',
        required: true,
        sortable: true,
        editable: false
      },
      {
        key: 'nombre_componente',
        label: 'Nombre',
        type: 'text',
        required: true,
        sortable: true,
        placeholder: 'Nombre del componente',
        maxLength: 150
      }
    ],
    searchFields: ['nombre_componente', 'id_componente']
  },

  // ========== ENTIDADES ==========
  entidades: {
    key: 'entidades',
    title: 'Entidades de Operación',
    description: 'Gestión de entidades operacionales',
    singularName: 'Entidad',
    pluralName: 'Entidades',
    idField: 'cod_entidad',
    columns: [
      {
        key: 'cod_entidad',
        label: 'Código',
        type: 'text',
        required: true,
        sortable: true,
        placeholder: 'Código de entidad',
        maxLength: 20
      },
      {
        key: 'nom_entidad',
        label: 'Nombre',
        type: 'text',
        required: true,
        sortable: true,
        placeholder: 'Nombre de la entidad',
        maxLength: 100
      }
    ],
    searchFields: ['nom_entidad', 'cod_entidad']
  },

  // ========== ESTADO INSUMOS ==========
  estados_insumo: {
    key: 'estados_insumo',
    title: 'Estado de Insumos',
    description: 'Estados posibles para la gestión de insumos',
    singularName: 'Estado',
    pluralName: 'Estados',
    idField: 'estado',
    columns: [
      {
        key: 'estado',
        label: 'Estado',
        type: 'text',
        required: true,
        sortable: true,
        placeholder: 'Ej: Activo, Inactivo, Pendiente',
        maxLength: 50
      }
    ],
    searchFields: ['estado']
  },

  // ========== GRUPOS ==========
  grupos: {
    key: 'grupos',
    title: 'Grupos de Operación',
    description: 'Gestión de grupos operacionales',
    singularName: 'Grupo',
    pluralName: 'Grupos',
    idField: 'cod_grupo',
    columns: [
      {
        key: 'cod_grupo',
        label: 'Código',
        type: 'text',
        required: true,
        sortable: true,
        placeholder: 'Código del grupo',
        maxLength: 20
      },
      {
        key: 'descripcion',
        label: 'Descripción',
        type: 'textarea',
        required: false,
        sortable: false,
        placeholder: 'Descripción del grupo',
        maxLength: 255
      }
    ],
    searchFields: ['cod_grupo', 'descripcion']
  },

  // ========== MECANISMO DETALLE ==========
  mecanismo_detalle: {
    key: 'mecanismo_detalle',
    title: 'Mecanismo Detalle',
    description: 'Detalles específicos de mecanismos operativos',
    singularName: 'Mecanismo Detalle',
    pluralName: 'Mecanismos Detalle',
    idField: 'cod_mecanismo_detalle',
    columns: [
      {
        key: 'cod_mecanismo_detalle',
        label: 'Código',
        type: 'text',
        required: true,
        sortable: true,
        placeholder: 'Código del mecanismo',
        maxLength: 20
      },
      {
        key: 'descripcion',
        label: 'Descripción',
        type: 'textarea',
        required: false,
        sortable: false,
        placeholder: 'Descripción del mecanismo',
        maxLength: 255
      }
    ],
    searchFields: ['cod_mecanismo_detalle', 'descripcion']
  },

  // ========== MECANISMO GENERAL ==========
  mecanismo_general: {
    key: 'mecanismo_general',
    title: 'Mecanismo General',
    description: 'Mecanismos generales del sistema operativo',
    singularName: 'Mecanismo General',
    pluralName: 'Mecanismos Generales',
    idField: 'cod_mecanismo',
    columns: [
      {
        key: 'cod_mecanismo',
        label: 'Código',
        type: 'text',
        required: true,
        sortable: true,
        placeholder: 'Código del mecanismo',
        maxLength: 20
      },
      {
        key: 'descripcion',
        label: 'Descripción',
        type: 'textarea',
        required: false,
        sortable: false,
        placeholder: 'Descripción del mecanismo',
        maxLength: 255
      }
    ],
    searchFields: ['cod_mecanismo', 'descripcion']
  },

  // ========== MECANISMO OPERACIÓN ==========
  mecanismo_operacion: {
    key: 'mecanismo_operacion',
    title: 'Mecanismo de Operación',
    description: 'Mecanismos específicos de operación',
    singularName: 'Mecanismo de Operación',
    pluralName: 'Mecanismos de Operación',
    idField: 'cod_operacion',
    columns: [
      {
        key: 'cod_operacion',
        label: 'Código',
        type: 'text',
        required: true,
        sortable: true,
        placeholder: 'Código de operación',
        maxLength: 20
      },
      {
        key: 'descripcion',
        label: 'Descripción',
        type: 'textarea',
        required: false,
        sortable: false,
        placeholder: 'Descripción de la operación',
        maxLength: 255
      }
    ],
    searchFields: ['cod_operacion', 'descripcion']
  },

  // ========== ROLES SEGUIMIENTO ==========
  roles_seguimiento: {
    key: 'roles_seguimiento',
    title: 'Roles de Seguimiento',
    description: 'Roles para el seguimiento de profesionales',
    singularName: 'Rol',
    pluralName: 'Roles',
    idField: 'rol_profesional',
    columns: [
      {
        key: 'rol_profesional',
        label: 'Rol',
        type: 'text',
        required: true,
        sortable: true,
        placeholder: 'Nombre del rol',
        maxLength: 100
      }
    ],
    searchFields: ['rol_profesional']
  },

  // ========== TERRITORIALES IGAC ==========
  territoriales_igac: {
    key: 'territoriales_igac',
    title: 'Territoriales IGAC',
    description: 'Gestión de entidades territoriales IGAC',
    singularName: 'Territorial',
    pluralName: 'Territoriales',
    idField: 'nom_territorial',
    columns: [
      {
        key: 'nom_territorial',
        label: 'Nombre',
        type: 'text',
        required: true,
        sortable: true,
        placeholder: 'Nombre de la territorial',
        maxLength: 100
      }
    ],
    searchFields: ['nom_territorial']
  },

  // ========== TIPOS FORMATO ==========
  tipos_formato: {
    key: 'tipos_formato',
    title: 'Tipos de Formato',
    description: 'Gestión de tipos de formato de archivos',
    singularName: 'Tipo de Formato',
    pluralName: 'Tipos de Formato',
    idField: 'cod_formato_tipo',
    columns: [
      {
        key: 'cod_formato_tipo',
        label: 'Código',
        type: 'text',
        required: true,
        sortable: true,
        placeholder: 'Ej: PDF, DOCX, XLS',
        maxLength: 20
      }
    ],
    searchFields: ['cod_formato_tipo']
  },

  // ========== TIPOS INSUMOS ==========
  tipos_insumos: {
    key: 'tipos_insumos',
    title: 'Tipos de Insumos',
    description: 'Clasificación de tipos de insumos',
    singularName: 'Tipo de Insumo',
    pluralName: 'Tipos de Insumos',
    idField: 'tipo_insumo',
    columns: [
      {
        key: 'tipo_insumo',
        label: 'Tipo',
        type: 'text',
        required: true,
        sortable: true,
        placeholder: 'Tipo de insumo',
        maxLength: 100
      }
    ],
    searchFields: ['tipo_insumo']
  },

  // ========== ZONAS ==========
  zonas: {
    key: 'zonas',
    title: 'Zonas de Operación',
    description: 'Gestión de zonas operacionales',
    singularName: 'Zona',
    pluralName: 'Zonas',
    idField: 'zona',
    columns: [
      {
        key: 'zona',
        label: 'Zona',
        type: 'text',
        required: true,
        sortable: true,
        placeholder: 'Nombre de la zona',
        maxLength: 100
      }
    ],
    searchFields: ['zona']
  }
}

// =============== HELPER FUNCTIONS ===============
export const getDominioConfig = (key: string): DominioConfig | null => {
  return DOMINIOS_CONFIG[key] || null
}

export const getAllDominiosConfig = (): DominioConfig[] => {
  return Object.values(DOMINIOS_CONFIG)
}

export const getDominiosByCategory = () => {
  return {
    'Operaciones': [
      DOMINIOS_CONFIG.alcance_operacion,
      DOMINIOS_CONFIG.mecanismo_operacion,
      DOMINIOS_CONFIG.mecanismo_general,
      DOMINIOS_CONFIG.mecanismo_detalle
    ],
    'Clasificaciones': [
      DOMINIOS_CONFIG.categorias,
      DOMINIOS_CONFIG.tipos_insumos,
      DOMINIOS_CONFIG.tipos_formato,
      DOMINIOS_CONFIG.estados_insumo
    ],
    'Organizacionales': [
      DOMINIOS_CONFIG.entidades,
      DOMINIOS_CONFIG.grupos,
      DOMINIOS_CONFIG.zonas,
      DOMINIOS_CONFIG.roles_seguimiento
    ],
    'Territoriales': [
      DOMINIOS_CONFIG.territoriales_igac
    ],
    'Post-operación': [
      DOMINIOS_CONFIG.componentes_post
    ]
  }
}