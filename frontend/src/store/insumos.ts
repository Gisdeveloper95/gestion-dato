import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as insumosAPI from '@/api/insumos'
import type { 
  Insumo, ClasificacionInsumo, DetalleInsumo, Concepto,
  Municipio, Categoria, Entidad, Formato, TipoInsumo, Zona, Usuario
} from '@/models/insumo'

export const useInsumosStore = defineStore('insumos', () => {
  // Estado
  const insumos = ref<Insumo[]>([])
  const clasificaciones = ref<ClasificacionInsumo[]>([])
  const detalles = ref<DetalleInsumo[]>([])
  const conceptos = ref<Concepto[]>([])
  
  // Catálogos
  const municipios = ref<Municipio[]>([])
  const categorias = ref<Categoria[]>([])
  const entidades = ref<Entidad[]>([])
  const formatos = ref<Formato[]>([])
  const tiposInsumo = ref<TipoInsumo[]>([])
  const zonas = ref<Zona[]>([])
  const usuarios = ref<Usuario[]>([])
  
  // Estado de carga
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // Insumo seleccionado actual
  const selectedInsumoId = ref<number | null>(null)
  const selectedClasificacionId = ref<number | null>(null)
  const selectedDetalleId = ref<number | null>(null)
  
  // Getters
  const selectedInsumo = computed(() => {
    if (!selectedInsumoId.value) return null
    return insumos.value.find(i => i.cod_insumo === selectedInsumoId.value) || null
  })
  
  const selectedClasificacion = computed(() => {
    if (!selectedClasificacionId.value) return null
    return clasificaciones.value.find(c => c.cod_clasificacion === selectedClasificacionId.value) || null
  })
  
  const selectedDetalle = computed(() => {
    if (!selectedDetalleId.value) return null
    return detalles.value.find(d => d.cod_detalle === selectedDetalleId.value) || null
  })
  
  const insumosByMunicipio = computed(() => {
    // Agrupar insumos por municipio
    const result: Record<number, Insumo[]> = {}
    
    insumos.value.forEach(insumo => {
      if (!result[insumo.cod_municipio]) {
        result[insumo.cod_municipio] = []
      }
      result[insumo.cod_municipio].push(insumo)
    })
    
    return result
  })
  
  const clasificacionesByInsumo = computed(() => {
    // Agrupar clasificaciones por insumo
    const result: Record<number, ClasificacionInsumo[]> = {}
    
    clasificaciones.value.forEach(clasificacion => {
      if (!result[clasificacion.cod_insumo]) {
        result[clasificacion.cod_insumo] = []
      }
      result[clasificacion.cod_insumo].push(clasificacion)
    })
    
    return result
  })
  
  const detallesByClasificacion = computed(() => {
    // Agrupar detalles por clasificación
    const result: Record<number, DetalleInsumo[]> = {}
    
    detalles.value.forEach(detalle => {
      if (!result[detalle.cod_clasificacion]) {
        result[detalle.cod_clasificacion] = []
      }
      result[detalle.cod_clasificacion].push(detalle)
    })
    
    return result
  })
  
  // Acciones
  
  // Cargar catálogos
  const loadCatalogos = async () => {
    try {
      loading.value = true
      error.value = null
      
      const [
        municipiosData,
        categoriasData,
        entidadesData,
        formatosData,
        tiposData,
        zonasData,
        usuariosData
      ] = await Promise.all([
        insumosAPI.getMunicipios(),
        insumosAPI.getCategorias(),
        insumosAPI.getEntidades(),
        insumosAPI.getFormatos(),
        insumosAPI.getTiposInsumo(),
        insumosAPI.getZonas(),
        insumosAPI.getUsuarios()
      ])
      
      municipios.value = municipiosData
      categorias.value = categoriasData
      entidades.value = entidadesData
      formatos.value = formatosData
      tiposInsumo.value = tiposData
      zonas.value = zonasData
      usuarios.value = usuariosData
      
      return true
    } catch (err: any) {
      console.error('Error al cargar catálogos:', err)
      error.value = 'Error al cargar catálogos: ' + (err.message || 'Error desconocido')
      return false
    } finally {
      loading.value = false
    }
  }
  
  // Cargar todos los insumos
  const loadInsumos = async (params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const data = await insumosAPI.getInsumos(params)
      insumos.value = data
      
      return true
    } catch (err: any) {
      console.error('Error al cargar insumos:', err)
      error.value = 'Error al cargar insumos: ' + (err.message || 'Error desconocido')
      return false
    } finally {
      loading.value = false
    }
  }
  
  // Cargar insumos por municipio
  const loadInsumosByMunicipio = async (municipioId: number) => {
    try {
      loading.value = true
      error.value = null
      
      const data = await insumosAPI.getInsumosByMunicipio(municipioId)
      
      // Si solo queremos insumos de este municipio
      insumos.value = data
      
      // Si queremos mantener todos los insumos y añadir/actualizar los de este municipio
      // const existingIds = new Set(insumos.value.map(i => i.cod_insumo))
      // const toUpdate = data.filter(i => existingIds.has(i.cod_insumo))
      // const toAdd = data.filter(i => !existingIds.has(i.cod_insumo))
      
      // // Actualizar existentes
      // toUpdate.forEach(newInsumo => {
      //   const index = insumos.value.findIndex(i => i.cod_insumo === newInsumo.cod_insumo)
      //   if (index !== -1) {
      //     insumos.value[index] = newInsumo
      //   }
      // })
      
      // // Añadir nuevos
      // insumos.value = [...insumos.value, ...toAdd]
      
      return true
    } catch (err: any) {
      console.error('Error al cargar insumos por municipio:', err)
      error.value = 'Error al cargar insumos: ' + (err.message || 'Error desconocido')
      return false
    } finally {
      loading.value = false
    }
  }
  
  // Cargar un insumo específico
  const loadInsumo = async (insumoId: number) => {
    try {
      loading.value = true
      error.value = null
      
      const data = await insumosAPI.getInsumoById(insumoId)
      
      // Actualizar en la lista si ya existe
      const index = insumos.value.findIndex(i => i.cod_insumo === insumoId)
      if (index !== -1) {
        insumos.value[index] = data
      } else {
        insumos.value.push(data)
      }
      
      selectedInsumoId.value = insumoId
      
      return data
    } catch (err: any) {
      console.error('Error al cargar insumo:', err)
      error.value = 'Error al cargar insumo: ' + (err.message || 'Error desconocido')
      return null
    } finally {
      loading.value = false
    }
  }
  
  // Crear un insumo
  const createInsumo = async (data: Partial<Insumo>) => {
    try {
      loading.value = true
      error.value = null
      
      const newInsumo = await insumosAPI.createInsumo(data)
      insumos.value.push(newInsumo)
      
      return newInsumo
    } catch (err: any) {
      console.error('Error al crear insumo:', err)
      error.value = 'Error al crear insumo: ' + (err.message || 'Error desconocido')
      return null
    } finally {
      loading.value = false
    }
  }
  
  // Actualizar un insumo
  const updateInsumo = async (id: number, data: Partial<Insumo>) => {
    try {
      loading.value = true
      error.value = null
      
      const updatedInsumo = await insumosAPI.updateInsumo(id, data)
      
      const index = insumos.value.findIndex(i => i.cod_insumo === id)
      if (index !== -1) {
        insumos.value[index] = updatedInsumo
      }
      
      return updatedInsumo
    } catch (err: any) {
      console.error('Error al actualizar insumo:', err)
      error.value = 'Error al actualizar insumo: ' + (err.message || 'Error desconocido')
      return null
    } finally {
      loading.value = false
    }
  }
  
  // Eliminar un insumo
  const deleteInsumo = async (id: number) => {
    try {
      loading.value = true
      error.value = null
      
      await insumosAPI.deleteInsumo(id)
      
      insumos.value = insumos.value.filter(i => i.cod_insumo !== id)
      
      if (selectedInsumoId.value === id) {
        selectedInsumoId.value = null
      }
      
      return true
    } catch (err: any) {
      console.error('Error al eliminar insumo:', err)
      error.value = 'Error al eliminar insumo: ' + (err.message || 'Error desconocido')
      return false
    } finally {
      loading.value = false
    }
  }
  
  // -------------- CLASIFICACIONES --------------
  
  // Cargar todas las clasificaciones
  const loadClasificaciones = async (params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const data = await insumosAPI.getClasificaciones(params)
      clasificaciones.value = data
      
      return true
    } catch (err: any) {
      console.error('Error al cargar clasificaciones:', err)
      error.value = 'Error al cargar clasificaciones: ' + (err.message || 'Error desconocido')
      return false
    } finally {
      loading.value = false
    }
  }
  
  // Cargar clasificaciones de un insumo específico
  const loadClasificacionesByInsumo = async (insumoId: number) => {
    try {
      loading.value = true
      error.value = null
      
      const data = await insumosAPI.getClasificacionesByInsumo(insumoId)
      
      // Si solo queremos clasificaciones de este insumo
      clasificaciones.value = data
      
      // Si queremos mantener todas las clasificaciones y añadir/actualizar las de este insumo
      // const existingIds = new Set(clasificaciones.value.map(c => c.cod_clasificacion))
      // const toUpdate = data.filter(c => existingIds.has(c.cod_clasificacion))
      // const toAdd = data.filter(c => !existingIds.has(c.cod_clasificacion))
      
      // // Actualizar existentes
      // toUpdate.forEach(newClasificacion => {
      //   const index = clasificaciones.value.findIndex(c => c.cod_clasificacion === newClasificacion.cod_clasificacion)
      //   if (index !== -1) {
      //     clasificaciones.value[index] = newClasificacion
      //   }
      // })
      
      // // Añadir nuevas
      // clasificaciones.value = [...clasificaciones.value, ...toAdd]
      
      return true
    } catch (err: any) {
      console.error('Error al cargar clasificaciones por insumo:', err)
      error.value = 'Error al cargar clasificaciones: ' + (err.message || 'Error desconocido')
      return false
    } finally {
      loading.value = false
    }
  }
  
  // Cargar una clasificación específica
  const loadClasificacion = async (clasificacionId: number) => {
    try {
      loading.value = true
      error.value = null
      
      const data = await insumosAPI.getClasificacionById(clasificacionId)
      
      // Actualizar en la lista si ya existe
      const index = clasificaciones.value.findIndex(c => c.cod_clasificacion === clasificacionId)
      if (index !== -1) {
        clasificaciones.value[index] = data
      } else {
        clasificaciones.value.push(data)
      }
      
      selectedClasificacionId.value = clasificacionId
      
      return data
    } catch (err: any) {
      console.error('Error al cargar clasificación:', err)
      error.value = 'Error al cargar clasificación: ' + (err.message || 'Error desconocido')
      return null
    } finally {
      loading.value = false
    }
  }
  
  // Crear una clasificación
  const createClasificacion = async (data: Partial<ClasificacionInsumo>) => {
    try {
      loading.value = true
      error.value = null
      
      const newClasificacion = await insumosAPI.createClasificacion(data)
      clasificaciones.value.push(newClasificacion)
      
      // Actualizar contador en el insumo correspondiente
      const insumo = insumos.value.find(i => i.cod_insumo === newClasificacion.cod_insumo)
      if (insumo && insumo.clasificaciones_count !== undefined) {
        insumo.clasificaciones_count++
      }
      
      return newClasificacion
    } catch (err: any) {
      console.error('Error al crear clasificación:', err)
      error.value = 'Error al crear clasificación: ' + (err.message || 'Error desconocido')
      return null
    } finally {
      loading.value = false
    }
  }
  
  // Actualizar una clasificación
  const updateClasificacion = async (id: number, data: Partial<ClasificacionInsumo>) => {
    try {
      loading.value = true
      error.value = null
      
      const updatedClasificacion = await insumosAPI.updateClasificacion(id, data)
      
      const index = clasificaciones.value.findIndex(c => c.cod_clasificacion === id)
      if (index !== -1) {
        clasificaciones.value[index] = updatedClasificacion
      }
      
      return updatedClasificacion
    } catch (err: any) {
      console.error('Error al actualizar clasificación:', err)
      error.value = 'Error al actualizar clasificación: ' + (err.message || 'Error desconocido')
      return null
    } finally {
      loading.value = false
    }
  }
  
  // Eliminar una clasificación
  const deleteClasificacion = async (id: number) => {
    try {
      loading.value = true
      error.value = null
      
      const clasificacion = clasificaciones.value.find(c => c.cod_clasificacion === id)
      
      await insumosAPI.deleteClasificacion(id)
      
      clasificaciones.value = clasificaciones.value.filter(c => c.cod_clasificacion !== id)
      
      // Actualizar contador en el insumo correspondiente
      if (clasificacion) {
        const insumo = insumos.value.find(i => i.cod_insumo === clasificacion.cod_insumo)
        if (insumo && insumo.clasificaciones_count !== undefined && insumo.clasificaciones_count > 0) {
          insumo.clasificaciones_count--
        }
      }
      
      if (selectedClasificacionId.value === id) {
        selectedClasificacionId.value = null
      }
      
      return true
    } catch (err: any) {
      console.error('Error al eliminar clasificación:', err)
      error.value = 'Error al eliminar clasificación: ' + (err.message || 'Error desconocido')
      return false
    } finally {
      loading.value = false
    }
  }
  
  // -------------- DETALLES --------------
  
  // Cargar todos los detalles
  const loadDetalles = async (params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const data = await insumosAPI.getDetalles(params)
      detalles.value = data
      
      return true
    } catch (err: any) {
      console.error('Error al cargar detalles:', err)
      error.value = 'Error al cargar detalles: ' + (err.message || 'Error desconocido')
      return false
    } finally {
      loading.value = false
    }
  }
  
  // Cargar detalles de una clasificación específica
  const loadDetallesByClasificacion = async (clasificacionId: number) => {
    try {
      loading.value = true
      error.value = null
      
      const data = await insumosAPI.getDetallesByClasificacion(clasificacionId)
      
      // Si solo queremos detalles de esta clasificación
      detalles.value = data
      
      // Si queremos mantener todos los detalles y añadir/actualizar los de esta clasificación
      // const existingIds = new Set(detalles.value.map(d => d.cod_detalle))
      // const toUpdate = data.filter(d => existingIds.has(d.cod_detalle))
      // const toAdd = data.filter(d => !existingIds.has(d.cod_detalle))
      
      // // Actualizar existentes
      // toUpdate.forEach(newDetalle => {
      //   const index = detalles.value.findIndex(d => d.cod_detalle === newDetalle.cod_detalle)
      //   if (index !== -1) {
      //     detalles.value[index] = newDetalle
      //   }
      // })
      
      // // Añadir nuevos
      // detalles.value = [...detalles.value, ...toAdd]
      
      return true
    } catch (err: any) {
      console.error('Error al cargar detalles por clasificación:', err)
      error.value = 'Error al cargar detalles: ' + (err.message || 'Error desconocido')
      return false
    } finally {
      loading.value = false
    }
  }
  
  // Cargar un detalle específico
  const loadDetalle = async (detalleId: number) => {
    try {
      loading.value = true
      error.value = null
      
      const data = await insumosAPI.getDetalleById(detalleId)
      
      // Actualizar en la lista si ya existe
      const index = detalles.value.findIndex(d => d.cod_detalle === detalleId)
      if (index !== -1) {
        detalles.value[index] = data
      } else {
        detalles.value.push(data)
      }
      
      selectedDetalleId.value = detalleId
      
      return data
    } catch (err: any) {
      console.error('Error al cargar detalle:', err)
      error.value = 'Error al cargar detalle: ' + (err.message || 'Error desconocido')
      return null
    } finally {
      loading.value = false
    }
  }
  
  // Crear un detalle
  const createDetalle = async (data: Partial<DetalleInsumo>) => {
    try {
      loading.value = true
      error.value = null
      
      const newDetalle = await insumosAPI.createDetalle(data)
      detalles.value.push(newDetalle)
      
      // Actualizar contador en la clasificación correspondiente
      const clasificacion = clasificaciones.value.find(c => c.cod_clasificacion === newDetalle.cod_clasificacion)
      if (clasificacion && clasificacion.detalles_count !== undefined) {
        clasificacion.detalles_count++
      }
      
      return newDetalle
    } catch (err: any) {
      console.error('Error al crear detalle:', err)
      error.value = 'Error al crear detalle: ' + (err.message || 'Error desconocido')
      return null
    } finally {
      loading.value = false
    }
  }
  
  // Actualizar un detalle
  const updateDetalle = async (id: number, data: Partial<DetalleInsumo>) => {
    try {
      loading.value = true
      error.value = null
      
      const updatedDetalle = await insumosAPI.updateDetalle(id, data)
      
      const index = detalles.value.findIndex(d => d.cod_detalle === id)
      if (index !== -1) {
        detalles.value[index] = updatedDetalle
      }
      
      return updatedDetalle
    } catch (err: any) {
      console.error('Error al actualizar detalle:', err)
      error.value = 'Error al actualizar detalle: ' + (err.message || 'Error desconocido')
      return null
    } finally {
      loading.value = false
    }
  }
  
  // Eliminar un detalle
  const deleteDetalle = async (id: number) => {
    try {
      loading.value = true
      error.value = null
      
      const detalle = detalles.value.find(d => d.cod_detalle === id)
      
      await insumosAPI.deleteDetalle(id)
      
      detalles.value = detalles.value.filter(d => d.cod_detalle !== id)
      
      // Actualizar contador en la clasificación correspondiente
      if (detalle) {
        const clasificacion = clasificaciones.value.find(c => c.cod_clasificacion === detalle.cod_clasificacion)
        if (clasificacion && clasificacion.detalles_count !== undefined && clasificacion.detalles_count > 0) {
          clasificacion.detalles_count--
        }
      }
      
      if (selectedDetalleId.value === id) {
        selectedDetalleId.value = null
      }
      
      return true
    } catch (err: any) {
      console.error('Error al eliminar detalle:', err)
      error.value = 'Error al eliminar detalle: ' + (err.message || 'Error desconocido')
      return false
    } finally {
      loading.value = false
    }
  }
  
  // -------------- CONCEPTOS --------------
  
  // Cargar todos los conceptos
  const loadConceptos = async (params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const data = await insumosAPI.getConceptos(params)
      conceptos.value = data
      
      return true
    } catch (err: any) {
      console.error('Error al cargar conceptos:', err)
      error.value = 'Error al cargar conceptos: ' + (err.message || 'Error desconocido')
      return false
    } finally {
      loading.value = false
    }
  }
  
  // Cargar un concepto específico
  const loadConcepto = async (conceptoId: number) => {
    try {
      loading.value = true
      error.value = null
      
      const data = await insumosAPI.getConceptoById(conceptoId)
      
      // Actualizar en la lista si ya existe
      const index = conceptos.value.findIndex(c => c.cod_concepto === conceptoId)
      if (index !== -1) {
        conceptos.value[index] = data
      } else {
        conceptos.value.push(data)
      }
      
      return data
    } catch (err: any) {
      console.error('Error al cargar concepto:', err)
      error.value = 'Error al cargar concepto: ' + (err.message || 'Error desconocido')
      return null
    } finally {
      loading.value = false
    }
  }
  
  // Crear un concepto
  const createConcepto = async (data: Partial<Concepto>) => {
    try {
      loading.value = true
      error.value = null
      
      const newConcepto = await insumosAPI.createConcepto(data)
      conceptos.value.push(newConcepto)
      
      return newConcepto
    } catch (err: any) {
      console.error('Error al crear concepto:', err)
      error.value = 'Error al crear concepto: ' + (err.message || 'Error desconocido')
      return null
    } finally {
      loading.value = false
    }
  }
  
  // Actualizar un concepto
  const updateConcepto = async (id: number, data: Partial<Concepto>) => {
    try {
      loading.value = true
      error.value = null
      
      const updatedConcepto = await insumosAPI.updateConcepto(id, data)
      
      const index = conceptos.value.findIndex(c => c.cod_concepto === id)
      if (index !== -1) {
        conceptos.value[index] = updatedConcepto
      }
      
      return updatedConcepto
    } catch (err: any) {
      console.error('Error al actualizar concepto:', err)
      error.value = 'Error al actualizar concepto: ' + (err.message || 'Error desconocido')
      return null
    } finally {
      loading.value = false
    }
  }
  
  // Eliminar un concepto
  const deleteConcepto = async (id: number) => {
    try {
      loading.value = true
      error.value = null
      
      await insumosAPI.deleteConcepto(id)
      
      conceptos.value = conceptos.value.filter(c => c.cod_concepto !== id)
      
      return true
    } catch (err: any) {
      console.error('Error al eliminar concepto:', err)
      error.value = 'Error al eliminar concepto: ' + (err.message || 'Error desconocido')
      return false
    } finally {
      loading.value = false
    }
  }
  
  return {
    // Estado
    insumos,
    clasificaciones,
    detalles,
    conceptos,
    municipios,
    categorias,
    entidades,
    formatos,
    tiposInsumo,
    zonas,
    usuarios,
    loading,
    error,
    selectedInsumoId,
    selectedClasificacionId,
    selectedDetalleId,
    
    // Getters
    selectedInsumo,
    selectedClasificacion,
    selectedDetalle,
    insumosByMunicipio,
    clasificacionesByInsumo,
    detallesByClasificacion,
    
    // Acciones - Catálogos
    loadCatalogos,
    
    // Acciones - Insumos
    loadInsumos,
    loadInsumosByMunicipio,
    loadInsumo,
    createInsumo,
    updateInsumo,
    deleteInsumo,
    
    // Acciones - Clasificaciones
    loadClasificaciones,
    loadClasificacionesByInsumo,
    loadClasificacion,
    createClasificacion,
    updateClasificacion,
    deleteClasificacion,
    
    // Acciones - Detalles
    loadDetalles,
    loadDetallesByClasificacion,
    loadDetalle,
    createDetalle,
    updateDetalle,
    deleteDetalle,
    
    // Acciones - Conceptos
    loadConceptos,
    loadConcepto,
    createConcepto,
    updateConcepto,
    deleteConcepto
  }
})