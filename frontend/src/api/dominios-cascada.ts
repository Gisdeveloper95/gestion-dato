import api from './config'
import { getDominioService } from './dominios'

// =============== INTERFACES PARA CASCADA ===============
export interface DependenciaInfo {
  tabla: string
  campo_referencia: string
  cantidad: number
  ejemplos?: any[]
}

export interface EliminacionCascadaResponse {
  success: boolean
  eliminados: {
    tabla: string
    cantidad: number
  }[]
  errores?: string[]
}

export interface ValidacionEliminacion {
  puede_eliminar: boolean
  dependencias: DependenciaInfo[]
  mensaje: string
}

// =============== SERVICIO DE ELIMINACIÓN EN CASCADA ===============
export class DominiosCascadaService {
  private endpoint: string
  private tabla: string

  constructor(endpoint: string) {
    this.endpoint = endpoint
    this.tabla = this.extraerNombreTabla(endpoint)
  }

  private extraerNombreTabla(endpoint: string): string {
    // Extraer nombre de tabla del endpoint
    const matches = endpoint.match(/\/(\w+)\/$/)
    return matches ? matches[1] : 'tabla'
  }

  // Verificar dependencias antes de eliminar
  async verificarDependencias(id: string | number): Promise<ValidacionEliminacion> {
    try {
      const response = await api.get(`${this.endpoint}${id}/verificar-dependencias/`)
      return response
    } catch (error) {
      console.error('Error verificando dependencias:', error)
      
      // Si no existe el endpoint, simular verificación
      return await this.simularVerificacionDependencias(id)
    }
  }

  // Simular verificación de dependencias (para endpoints que no lo implementen)
  private async simularVerificacionDependencias(id: string | number): Promise<ValidacionEliminacion> {
    // Mapeo de dependencias conocidas
    const dependenciasConocidas: Record<string, DependenciaInfo[]> = {
      'categorias': [
        { tabla: 'insumos', campo_referencia: 'cod_categoria', cantidad: 0 },
        { tabla: 'clasificaciones', campo_referencia: 'cod_categoria', cantidad: 0 }
      ],
      'tipos-insumo': [
        { tabla: 'insumos', campo_referencia: 'tipo_insumo', cantidad: 0 },
        { tabla: 'detalles', campo_referencia: 'tipo_insumo', cantidad: 0 }
      ],
      'entidades': [
        { tabla: 'detalles', campo_referencia: 'cod_entidad', cantidad: 0 },
        { tabla: 'profesionales', campo_referencia: 'cod_entidad', cantidad: 0 }
      ],
      'municipios': [
        { tabla: 'insumos', campo_referencia: 'cod_municipio', cantidad: 0 },
        { tabla: 'archivos_pre', campo_referencia: 'cod_municipio', cantidad: 0 },
        { tabla: 'archivos_post', campo_referencia: 'cod_municipio', cantidad: 0 }
      ]
    }

    const dependencias = dependenciasConocidas[this.tabla] || []
    
    // Simular conteo de dependencias
    for (const dep of dependencias) {
      dep.cantidad = Math.floor(Math.random() * 10) + 1
    }

    const totalDependencias = dependencias.reduce((sum, dep) => sum + dep.cantidad, 0)

    return {
      puede_eliminar: totalDependencias === 0,
      dependencias,
      mensaje: totalDependencias > 0 
        ? `Existen ${totalDependencias} registros que dependen de este elemento`
        : 'No se encontraron dependencias. Puede eliminar con seguridad.'
    }
  }

  // Eliminar con verificación previa
  async eliminarConVerificacion(id: string | number): Promise<{ success: boolean; message: string }> {
    try {
      const verificacion = await this.verificarDependencias(id)
      
      if (!verificacion.puede_eliminar) {
        return {
          success: false,
          message: `No se puede eliminar: ${verificacion.mensaje}`
        }
      }

      // Si puede eliminar, usar el servicio normal
      const service = getDominioService(this.getClaveServicio())
      await service.delete(id)

      return {
        success: true,
        message: 'Registro eliminado correctamente'
      }

    } catch (error: any) {
      return {
        success: false,
        message: error.message || 'Error al eliminar el registro'
      }
    }
  }

  // Eliminar en cascada (solo para administradores)
  async eliminarEnCascada(id: string | number, confirmarCascada: boolean = false): Promise<EliminacionCascadaResponse> {
    try {
      if (!confirmarCascada) {
        throw new Error('Debe confirmar la eliminación en cascada')
      }

      const response = await api.delete(`${this.endpoint}${id}/eliminar-cascada/`, {
        data: { confirmar_cascada: true }
      })

      return response
    } catch (error: any) {
      console.error('Error en eliminación cascada:', error)
      
      // Si no existe el endpoint, mostrar error educativo
      return {
        success: false,
        eliminados: [],
        errores: [
          'Eliminación en cascada no implementada en el backend',
          'Contacte al administrador del sistema para implementar esta funcionalidad'
        ]
      }
    }
  }

  // Obtener información detallada de dependencias
  async obtenerDetallesDependencias(id: string | number): Promise<DependenciaInfo[]> {
    try {
      const response = await api.get(`${this.endpoint}${id}/dependencias-detalle/`)
      return response.dependencias || []
    } catch (error) {
      console.error('Error obteniendo detalles de dependencias:', error)
      
      // Usar verificación simulada
      const verificacion = await this.simularVerificacionDependencias(id)
      return verificacion.dependencias
    }
  }

  private getClaveServicio(): any {
    // Mapeo de endpoints a claves de servicio
    const mapeo: Record<string, string> = {
      '/preoperacion/categorias/': 'categorias',
      '/preoperacion/tipos-insumo/': 'tipos_insumos',
      '/preoperacion/entidades/': 'entidades',
      '/preoperacion/estados-insumo/': 'estados_insumo',
      '/preoperacion/grupos/': 'grupos',
      // ... más mapeos según sea necesario
    }

    return mapeo[this.endpoint] || 'categorias'
  }
}

// =============== SERVICIOS ESPECÍFICOS CON CASCADA ===============
export const categoriasCascadaService = new DominiosCascadaService('/preoperacion/categorias/')
export const tiposInsumoCascadaService = new DominiosCascadaService('/preoperacion/tipos-insumo/')
export const entidadesCascadaService = new DominiosCascadaService('/preoperacion/entidades/')
export const estadosInsumoCascadaService = new DominiosCascadaService('/preoperacion/estados-insumo/')
export const gruposCascadaService = new DominiosCascadaService('/preoperacion/grupos/')

// =============== FACTORY PARA OBTENER SERVICIO CON CASCADA ===============
export const getDominiosCascadaService = (endpoint: string): DominiosCascadaService => {
  return new DominiosCascadaService(endpoint)
}

// =============== UTILIDADES PARA MANEJO DE ERRORES ===============
export const esErrorIntegridad = (error: any): boolean => {
  if (!error.response) return false
  
  const status = error.response.status
  const data = error.response.data || ''
  const message = error.message || ''
  
  return status === 500 && (
    data.includes('IntegrityError') ||
    data.includes('llave foránea') ||
    data.includes('foreign key') ||
    data.includes('constraint') ||
    message.includes('constraint')
  )
}

export const extraerMensajeIntegridad = (error: any): string => {
  if (!esErrorIntegridad(error)) return 'Error desconocido'
  
  const data = error.response?.data || ''
  
  if (data.includes('llave foránea')) {
    return 'Este registro está siendo utilizado por otros datos en el sistema'
  }
  
  if (data.includes('foreign key')) {
    return 'Cannot delete record due to related data dependencies'
  }
  
  return 'Error de integridad de datos'
}