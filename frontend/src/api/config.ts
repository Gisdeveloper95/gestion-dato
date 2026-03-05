import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'

// =============== COMPATIBILIDAD: MANTENER EXPORTACIONES ORIGINALES ===============
// Exportar la URL base ORIGINAL para que funcionen las importaciones existentes
// NOTA: Ahora todo se configura desde el archivo .env

// Si VITE_API_URL no está definido o es vacío, usar cadena vacía (paths relativos)
export const API_URL = import.meta.env.VITE_API_URL !== undefined ? import.meta.env.VITE_API_URL : ''

// =============== NUEVAS EXPORTACIONES PARA TABLEMANAGER ===============
/**
 * URL base de la API (alias del original para nuevos componentes)
 */
export const API_BASE_URL = API_URL

/**
 * URL base del servidor (sin /api)
 * Para archivos estáticos, uploads, etc.
 */

export const SERVER_BASE_URL = import.meta.env.VITE_SERVER_BASE_URL || API_URL

/**
 * Configuración de timeouts
 */
export const API_TIMEOUT = 30000 // 30 segundos

/**
 * Configuración de paginación por defecto
 */
export const DEFAULT_PAGE_SIZE = 20
export const MAX_PAGE_SIZE = 100

/**
 * Configuración de caché
 */
export const CACHE_DURATION = {
  SHORT: 5 * 60 * 1000,     // 5 minutos
  MEDIUM: 15 * 60 * 1000,   // 15 minutos
  LONG: 60 * 60 * 1000      // 1 hora
}

/**
 * Headers por defecto para todas las peticiones
 */
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}

/**
 * Endpoints específicos de la API
 */
export const API_ENDPOINTS = {
  // Autenticación
  AUTH: {
    LOGIN: '/auth/login/',
    LOGOUT: '/auth/logout/',
    REFRESH: '/auth/refresh/',
    USER_PROFILE: '/auth/user/',
    CHANGE_PASSWORD: '/auth/change-password/'
  },
  
  // Gestión de usuarios
  USERS: '/usuarios/',
  
  // Datos geográficos
  DEPARTAMENTOS: '/departamentos/',
  MUNICIPIOS: '/municipios/',
  TERRITORIALES: '/territoriales/',
  
  // Dominios
  CATEGORIAS: '/categorias/',
  TIPOS_INSUMOS: '/tipos-insumos/',
  ESTADO_INSUMOS: '/estado-insumos/',
  ENTIDADES: '/entidades/',
  GRUPOS: '/grupos/',
  ZONAS: '/zonas/',
  ALCANCE_OPERACION: '/alcance-operacion/',
  ROLES_SEGUIMIENTO: '/roles-seguimiento/',
  MECANISMO_GENERAL: '/mecanismo-general/',
  MECANISMO_DETALLE: '/mecanismo-detalle/',
  MECANISMO_OPERACION: '/mecanismo-operacion/',
  TIPOS_FORMATO: '/tipos-formato/',
  COMPONENTES_POST: '/componentes-post/',
  
  // Gestión de archivos
  ARCHIVOS_POST: '/archivos-post/',
  ARCHIVOS_PRE: '/archivos-pre/',
  PATH_DIR_POST: '/path-dir-post/',
  PATH_DIR_PRE: '/path-dir-pre/',
  
  // Insumos y productos
  INSUMOS: '/insumos/',
  PRODUCTOS: '/productos/',
  
  // Profesionales
  PROFESIONALES: '/profesionales/',
  PROFESIONAL_MUNICIPIO: '/profesional-municipio/',
  
  // Reportes y auditoría
  REPORTES: '/reportes/',
  AUDITORIA: '/auditoria/',
  ESTADISTICAS: '/estadisticas/',
  
  // Notificaciones
  NOTIFICACIONES: '/notificaciones/'
}

// =============== CONFIGURACIÓN ORIGINAL DE AXIOS ===============
// Crear configuración base para axios
const apiConfig: AxiosRequestConfig = {
  baseURL: API_URL,
  timeout: 15000, // Aumentado a 15 segundos
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
}

// Crear instancia de axios
const api: AxiosInstance = axios.create(apiConfig)

// Variable global para controlar si estamos redirigiendo
let isRedirecting = false

// Interceptor para agregar token a las peticiones
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token && config.headers) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Interceptor para manejar respuestas
// ✅ INTERCEPTOR DE RESPUESTA MEJORADO - Cierre automático de sesión en token expirado
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // Si la respuesta es exitosa, retornar los datos
    return response.data
  },
  (error: AxiosError) => {
    console.log('🔍 Interceptor detectó error:', {
      status: error.response?.status,
      url: error.config?.url,
      method: error.config?.method,
      data: error.response?.data
    })

    // ✅ ERROR 401 = Token inválido/expirado - SIEMPRE cerrar sesión
    if (error.response?.status === 401) {
      console.warn('🔑 Error 401 detectado - Sesión expirada o token inválido')

      // Evitar redirecciones múltiples
      if (!isRedirecting) {
        isRedirecting = true

        // Limpiar datos de sesión
        localStorage.removeItem('token')
        localStorage.removeItem('userProfile')
        localStorage.removeItem('userId')

        // Redirigir a login si no estamos ya ahí
        const currentPath = window.location.pathname
        if (currentPath !== '/login' && currentPath !== '/') {
          console.log('🔄 Redirigiendo a login por token expirado...')
          window.location.href = '/login?expired=1'
        }

        // Reset del flag después de un tiempo
        setTimeout(() => {
          isRedirecting = false
        }, 3000)
      }

    } else if (error.response?.status === 403) {
      // 403 = Sin permisos suficientes (NO redirigir a login, mantener sesión)
      console.warn('🚫 Error 403 - Sin permisos suficientes (sesión activa)')
    }

    // ✅ OTROS ERRORES COMUNES
    if (error.code === 'ECONNABORTED' || error.message === 'Network Error') {
      console.error('🌐 Error de conexión:', error.message)
    }

    if (error.response && error.response.status >= 500) {
      console.error('🔥 Error del servidor:', error.response.status, error.response.data)
    }

    if (error.response && error.response.status === 400) {
      console.warn('⚠️ Error de validación:', error.response.data)
    }

    return Promise.reject(error)
  }
)

// ✅ FUNCIÓN PARA VERIFICAR SI EL TOKEN ES VÁLIDO
export const verifyTokenValidity = async (): Promise<boolean> => {
  try {
    const token = localStorage.getItem('token')
    if (!token) return false
    
    // Hacer una petición ligera para verificar el token
    const response = await api.get('/preoperacion/verify-token/')
    return response && response.valid === true
  } catch (error: any) {
    console.warn('❌ Token inválido:', error)
    return false
  }
}

// ✅ FUNCIÓN PARA MANEJAR ERRORES DE PERMISOS
export const handlePermissionError = (error: any, operation: string) => {
  if (error.response?.status === 403) {
    console.warn(`🔒 Sin permisos para: ${operation}`)
    return {
      isPermissionError: true,
      message: 'No tienes permisos suficientes para realizar esta operación. Se requieren permisos de administrador.'
    }
  }
  
  if (error.response?.status === 401) {
    console.warn(`🔑 Error de autenticación para: ${operation}`)
    return {
      isAuthError: true,
      message: 'Error de autenticación. Verifica tu sesión.'
    }
  }
  
  return {
    isOtherError: true,
    message: error.response?.data?.detail || error.response?.data?.message || error.message || 'Error desconocido'
  }
}

// =============== NUEVAS FUNCIONES AUXILIARES ===============

/**
 * Función para obtener la configuración de autenticación
 */
export const getAuthConfig = () => {
  const token = localStorage.getItem('token')
  return token ? {
    headers: {
      ...DEFAULT_HEADERS,
      'Authorization': `Token ${token}`
    }
  } : { headers: DEFAULT_HEADERS }
}

/**
 * Función para obtener la URL completa de un endpoint
 */
export const getFullApiUrl = (endpoint: string): string => {
  // Remover slash inicial si existe
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint
  return `${API_URL}/${cleanEndpoint}`
}

/**
 * Función para construir URL con parámetros
 */
export const buildUrlWithParams = (baseUrl: string, params: Record<string, any>): string => {
  const url = new URL(baseUrl, API_URL)
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      if (Array.isArray(value)) {
        value.forEach(v => url.searchParams.append(key, String(v)))
      } else {
        url.searchParams.append(key, String(value))
      }
    }
  })
  
  return url.toString()
}

/**
 * Función para validar que la API esté disponible
 */
export const validateApiConnection = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_URL}/health/`, { 
      method: 'GET'
    })
    return response.ok
  } catch (error) {
    console.error('API no disponible:', error)
    return false
  }
}

// =============== CONFIGURACIONES ADICIONALES ===============

/**
 * Configuración de entornos
 */
export const ENVIRONMENT = {
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
  appVersion: import.meta.env.VITE_APP_VERSION || '1.0.0'
}

/**
 * Configuración de logging
 */
export const LOGGING = {
  enabled: ENVIRONMENT.isDevelopment,
  level: import.meta.env.VITE_LOG_LEVEL || 'info', // error, warn, info, debug
  logToConsole: true,
  logToServer: ENVIRONMENT.isProduction
}

/**
 * Configuración de validación
 */
export const VALIDATION = {
  PASSWORD_MIN_LENGTH: 8,
  USERNAME_MIN_LENGTH: 3,
  NAME_MIN_LENGTH: 2,
  NAME_MAX_LENGTH: 100,
  DESCRIPTION_MAX_LENGTH: 500,
  EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE_REGEX: /^[\+]?[1-9][\d]{0,15}$/
}

/**
 * Estados comunes del sistema
 */
export const ESTADOS = {
  ACTIVO: 'activo',
  INACTIVO: 'inactivo',
  PENDIENTE: 'pendiente',
  COMPLETADO: 'completado',
  CANCELADO: 'cancelado'
} as const

/**
 * Configuración de colores para estados
 */
export const STATUS_COLORS = {
  [ESTADOS.ACTIVO]: '#28a745',
  [ESTADOS.INACTIVO]: '#dc3545',
  [ESTADOS.PENDIENTE]: '#ffc107',
  [ESTADOS.COMPLETADO]: '#17a2b8',
  [ESTADOS.CANCELADO]: '#6c757d'
}

/**
 * Configuración de formato de fechas
 */
export const DATE_FORMATS = {
  SHORT: 'DD/MM/YYYY',
  LONG: 'DD de MMMM de YYYY',
  WITH_TIME: 'DD/MM/YYYY HH:mm',
  ISO: 'YYYY-MM-DD',
  TIME_ONLY: 'HH:mm'
}

// =============== EXPORTACIÓN POR DEFECTO (MANTENER ORIGINAL) ===============
export default api