import api from './config'

// =============== TIPOS PARA DOMINIOS ===============
export interface DominioBase {
  [key: string]: any
}

export interface AlcanceOperacion {
  cod_alcance: string
}

export interface Categoria {
  cod_categoria: number
  nom_categoria: string
}

export interface ComponentePost {
  id_componente: number
  nombre_componente: string
}

export interface Entidad {
  cod_entidad: string
  nom_entidad: string
}

export interface EstadoInsumo {
  estado: string
}

export interface Grupo {
  cod_grupo: string
  descripcion?: string
}

export interface MecanismoDetalle {
  cod_mecanismo_detalle: string
  descripcion?: string
}

export interface MecanismoGeneral {
  cod_mecanismo: string
  descripcion?: string
}

export interface MecanismoOperacion {
  cod_operacion: string
  descripcion?: string
}

export interface RolSeguimiento {
  rol_profesional: string
}

export interface TerritorialIgac {
  nom_territorial: string
}

export interface TipoFormato {
  cod_formato_tipo: string
}

export interface TipoInsumo {
  tipo_insumo: string
}

export interface Zona {
  zona: string
}

// =============== CONFIGURACIÓN DE ENDPOINTS ===============
export const ENDPOINTS_DOMINIOS = {
  alcance_operacion: '/preoperacion/alcances-operacion/',
  categorias: '/preoperacion/categorias/',
  componentes_post: '/postoperacion/componentes/',
  entidades: '/preoperacion/entidades/',
  estados_insumo: '/preoperacion/estados-insumo/',
  grupos: '/preoperacion/grupos/',
  mecanismo_detalle: '/preoperacion/mecanismos-detalle/',
  mecanismo_general: '/preoperacion/mecanismos-general/',
  mecanismo_operacion: '/preoperacion/mecanismos-operacion/',
  roles_seguimiento: '/preoperacion/roles-seguimiento/',
  territoriales_igac: '/preoperacion/territoriales/',
  tipos_formato: '/preoperacion/tipos-formato/',
  tipos_insumos: '/preoperacion/tipos-insumo/',
  zonas: '/preoperacion/zonas/'
} as const

export type DominioKey = keyof typeof ENDPOINTS_DOMINIOS

// =============== CLASE GENÉRICA PARA DOMINIOS ===============
export class DominiosService {
  private endpoint: string

  constructor(dominioKey: DominioKey) {
    this.endpoint = ENDPOINTS_DOMINIOS[dominioKey]
  }

  // Obtener todos los registros
  async getAll(): Promise<any[]> {
    try {
      const response = await api.get(this.endpoint)
      return Array.isArray(response) ? response : response.results || []
    } catch (error) {
      console.error(`Error obteniendo registros de ${this.endpoint}:`, error)
      throw error
    }
  }

  // Obtener un registro por ID
  async getById(id: string | number): Promise<any> {
    try {
      const response = await api.get(`${this.endpoint}${id}/`)
      return response
    } catch (error) {
      console.error(`Error obteniendo registro ${id} de ${this.endpoint}:`, error)
      throw error
    }
  }

  // Crear nuevo registro
  async create(data: any): Promise<any> {
    try {
      const response = await api.post(this.endpoint, data)
      return response
    } catch (error) {
      console.error(`Error creando registro en ${this.endpoint}:`, error)
      throw error
    }
  }

  // Actualizar registro
  async update(id: string | number, data: any): Promise<any> {
    try {
      const response = await api.put(`${this.endpoint}${id}/`, data)
      return response
    } catch (error) {
      console.error(`Error actualizando registro ${id} en ${this.endpoint}:`, error)
      throw error
    }
  }

  // Eliminar registro
  async delete(id: string | number): Promise<void> {
    try {
      await api.delete(`${this.endpoint}${id}/`)
    } catch (error) {
      console.error(`Error eliminando registro ${id} de ${this.endpoint}:`, error)
      throw error
    }
  }

  // Buscar registros con filtros
  async search(params: Record<string, any>): Promise<any[]> {
    try {
      const response = await api.get(this.endpoint, { params })
      return Array.isArray(response) ? response : response.results || []
    } catch (error) {
      console.error(`Error buscando en ${this.endpoint}:`, error)
      throw error
    }
  }
}

// =============== SERVICIOS ESPECÍFICOS ===============
export const alcanceOperacionService = new DominiosService('alcance_operacion')
export const categoriasService = new DominiosService('categorias')
export const componentesPostService = new DominiosService('componentes_post')
export const entidadesService = new DominiosService('entidades')
export const estadosInsumoService = new DominiosService('estados_insumo')
export const gruposService = new DominiosService('grupos')
export const mecanismoDetalleService = new DominiosService('mecanismo_detalle')
export const mecanismoGeneralService = new DominiosService('mecanismo_general')
export const mecanismoOperacionService = new DominiosService('mecanismo_operacion')
export const rolesSeguimientoService = new DominiosService('roles_seguimiento')
export const territorialesIgacService = new DominiosService('territoriales_igac')
export const tiposFormatoService = new DominiosService('tipos_formato')
export const tiposInsumosService = new DominiosService('tipos_insumos')
export const zonasService = new DominiosService('zonas')

// =============== HELPER PARA OBTENER SERVICIO POR CLAVE ===============
export const getDominioService = (dominio: DominioKey): DominiosService => {
  const services = {
    alcance_operacion: alcanceOperacionService,
    categorias: categoriasService,
    componentes_post: componentesPostService,
    entidades: entidadesService,
    estados_insumo: estadosInsumoService,
    grupos: gruposService,
    mecanismo_detalle: mecanismoDetalleService,
    mecanismo_general: mecanismoGeneralService,
    mecanismo_operacion: mecanismoOperacionService,
    roles_seguimiento: rolesSeguimientoService,
    territoriales_igac: territorialesIgacService,
    tipos_formato: tiposFormatoService,
    tipos_insumos: tiposInsumosService,
    zonas: zonasService
  }
  
  return services[dominio]
}

// =============== EXPORTACIÓN POR DEFECTO ===============
export default {
  DominiosService,
  getDominioService,
  ENDPOINTS_DOMINIOS,
  // Servicios específicos
  alcanceOperacionService,
  categoriasService,
  componentesPostService,
  entidadesService,
  estadosInsumoService,
  gruposService,
  mecanismoDetalleService,
  mecanismoGeneralService,
  mecanismoOperacionService,
  rolesSeguimientoService,
  territorialesIgacService,
  tiposFormatoService,
  tiposInsumosService,
  zonasService
}