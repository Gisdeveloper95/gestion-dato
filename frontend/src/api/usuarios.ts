import api from './config'

// =============== INTERFACES ===============
export interface Usuario {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  is_staff: boolean
  is_superuser: boolean
  rol_tipo: 'super_admin' | 'admin' | 'profesional'
  fecha_registro: string
  ultimo_login: string | null
}

export interface CrearUsuarioData {
  username: string
  email: string
  first_name: string
  last_name: string
  password: string
  confirm_password: string
}

export interface ActualizarUsuarioData {
  first_name?: string
  last_name?: string
  email?: string
  is_active?: boolean
  rol_tipo?: 'profesional' | 'admin' | 'super_admin'
}

// =============== USUARIOS PROTEGIDOS ===============
// Estos usuarios NO pueden ser eliminados, desactivados ni cambiar su rol/contraseña
export const USUARIOS_PROTEGIDOS = ['andres.osorio', 'elizabeth.eraso']

/**
 * Verificar si un usuario está protegido
 */
export const esUsuarioProtegido = (username: string): boolean => {
  return USUARIOS_PROTEGIDOS.includes(username)
}

export interface UsuariosPorRol {
  super_admins: Usuario[]
  admins: Usuario[]
  profesionales: Usuario[]
  total: number
  estadisticas: {
    total_super_admins: number
    total_admins: number
    total_profesionales: number
  }
}

export interface EstadisticasUsuarios {
  total_usuarios: number
  usuarios_activos: number
  usuarios_inactivos: number
  super_admins: number
  admins: number
  profesionales: number
  usuarios_recientes: number
  porcentaje_activos: number
}

// =============== SERVICIO DE USUARIOS ===============
export const usuariosService = {
  
  /**
   * Crear un nuevo usuario
   */
  async crearUsuario(data: CrearUsuarioData): Promise<{ message: string; usuario: Usuario }> {
    try {
      // Verificar que tenemos token de autenticación
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No hay token de autenticación. Inicie sesión como administrador.');
      }

      const response = await api.post('/preoperacion/usuarios/crear/', data);
      
      // El interceptor ya devuelve response.data, por eso usamos response directamente
      if (!response) {
        throw new Error('El servidor no devolvió datos');
      }
      
      // Verificar estructura de respuesta y adaptarla si es necesario
      if (response.message && response.usuario) {
        return response;
      } else if (response.message) {
        return {
          message: response.message,
          usuario: response.usuario || {
            id: 0,
            username: data.username,
            email: data.email,
            first_name: data.first_name,
            last_name: data.last_name,
            is_active: true,
            is_staff: false,
            is_superuser: false,
            rol_tipo: 'profesional' as const,
            fecha_registro: new Date().toISOString(),
            ultimo_login: null
          }
        };
      } else {
        return {
          message: 'Usuario creado exitosamente',
          usuario: response as Usuario
        };
      }
      
    } catch (error: any) {
      if (error.response?.status === 401) {
        throw new Error('No tiene permisos para crear usuarios. Verifique que esté autenticado como administrador.');
      }
      
      if (error.response?.status === 403) {
        throw new Error('No tiene permisos de administrador para crear usuarios.');
      }

      if (error.response?.status === 405) {
        throw new Error('Error de configuración del servidor. El endpoint no acepta el método POST.');
      }
      
      // Manejo de errores del servidor
      let errorMessage = 'Error desconocido al crear usuario';

      if (error.response?.data) {
        const data = error.response.data;

        if (typeof data === 'string') {
          errorMessage = data;
        } else if (data.error) {
          errorMessage = data.error;
        } else if (data.message) {
          errorMessage = data.message;
        } else if (data.detail) {
          errorMessage = data.detail;
        } else if (data.non_field_errors) {
          // Errores generales de validacion
          errorMessage = Array.isArray(data.non_field_errors)
            ? data.non_field_errors.join('. ')
            : data.non_field_errors;
        } else {
          // Errores de campos especificos (formato DRF serializer)
          // Ejemplo: { "username": ["Este nombre de usuario ya existe."] }
          const fieldErrors: string[] = [];
          for (const [field, messages] of Object.entries(data)) {
            if (Array.isArray(messages)) {
              const fieldName = field === 'username' ? 'Nombre de usuario'
                             : field === 'email' ? 'Correo electrónico'
                             : field === 'password' ? 'Contraseña'
                             : field;
              fieldErrors.push(`${fieldName}: ${messages.join(', ')}`);
            } else if (typeof messages === 'string') {
              fieldErrors.push(messages);
            }
          }
          if (fieldErrors.length > 0) {
            errorMessage = fieldErrors.join('\n');
          }
        }
      } else if (error.message) {
        errorMessage = error.message;
      }

      throw new Error(errorMessage);
    }
  },

  /**
   * Listar usuarios agrupados por rol
   */
  async listarUsuarios(): Promise<UsuariosPorRol> {
    try {
      const response = await api.get('/preoperacion/usuarios/listar/');
      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.message || 
                          error.message || 
                          'Error al listar usuarios';
      throw new Error(errorMessage);
    }
  },

  /**
   * Obtener un usuario específico
   */
  async obtenerUsuario(userId: number): Promise<Usuario> {
    try {
      const response = await api.get(`/preoperacion/usuarios/${userId}/`);
      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.message || 
                          error.message || 
                          'Error al obtener usuario';
      throw new Error(errorMessage);
    }
  },

  /**
   * Actualizar un usuario
   */
  async actualizarUsuario(userId: number, data: ActualizarUsuarioData): Promise<{ message: string; usuario: Usuario }> {
    try {
      const response = await api.put(`/preoperacion/usuarios/${userId}/actualizar/`, data);
      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.message || 
                          error.message || 
                          'Error al actualizar usuario';
      throw new Error(errorMessage);
    }
  },

  /**
   * Eliminar un usuario
   */
  async eliminarUsuario(userId: number): Promise<{ message: string; username: string }> {
    try {
      const response = await api.delete(`/preoperacion/usuarios/${userId}/eliminar/`);
      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.message || 
                          error.message || 
                          'Error al eliminar usuario';
      throw new Error(errorMessage);
    }
  },

  /**
   * Cambiar contraseña de un usuario
   */
  async cambiarPassword(userId: number, nuevaPassword: string): Promise<{ message: string }> {
    try {
      const response = await api.post(`/preoperacion/usuarios/${userId}/cambiar-password/`, {
        nueva_password: nuevaPassword
      });
      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.message || 
                          error.message || 
                          'Error al cambiar contraseña';
      throw new Error(errorMessage);
    }
  },

  /**
   * Obtener estadísticas de usuarios
   */
  async obtenerEstadisticas(): Promise<EstadisticasUsuarios> {
    try {
      const response = await api.get('/preoperacion/usuarios/estadisticas/');
      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.message || 
                          error.message || 
                          'Error al obtener estadísticas';
      throw new Error(errorMessage);
    }
  }
}

// =============== UTILIDADES ===============

/**
 * Obtener el nombre completo del rol
 */
export const getRolDisplayName = (rolTipo: string): string => {
  const roles = {
    'super_admin': 'Super Administrador',
    'admin': 'Administrador',
    'profesional': 'Profesional'
  }
  return roles[rolTipo as keyof typeof roles] || 'Desconocido'
}

/**
 * Obtener el color del badge según el rol
 */
export const getRolColor = (rolTipo: string): string => {
  const colors = {
    'super_admin': '#dc2626', // Rojo
    'admin': '#ea580c',       // Naranja
    'profesional': '#16a34a'  // Verde
  }
  return colors[rolTipo as keyof typeof colors] || '#6b7280'
}

/**
 * Verificar si el usuario actual puede editar a otro usuario
 */
export const puedeEditarUsuario = (usuarioActual: any, usuarioObjetivo: Usuario): boolean => {
  // Super admin puede editar a todos (excepto otros super admins)
  if (usuarioActual.isSuperUser) {
    return usuarioObjetivo.rol_tipo !== 'super_admin' || usuarioObjetivo.id === usuarioActual.id
  }
  
  // Admin puede editar profesionales y a sí mismo
  if (usuarioActual.isStaff) {
    return usuarioObjetivo.rol_tipo === 'profesional' || usuarioObjetivo.id === usuarioActual.id
  }
  
  // Profesionales solo pueden editarse a sí mismos
  return usuarioObjetivo.id === usuarioActual.id
}

/**
 * Verificar si el usuario actual puede eliminar a otro usuario
 */
export const puedeEliminarUsuario = (usuarioActual: any, usuarioObjetivo: Usuario): boolean => {
  // Solo super admins pueden eliminar usuarios
  if (!usuarioActual.isSuperUser) return false
  
  // No puede eliminar a otros super admins ni a sí mismo
  return usuarioObjetivo.rol_tipo !== 'super_admin' && usuarioObjetivo.id !== usuarioActual.id
}

/**
 * Validar datos de usuario antes de enviar
 */
export const validarDatosUsuario = (data: CrearUsuarioData | ActualizarUsuarioData): string[] => {
  const errores: string[] = []
  
  if ('username' in data) {
    if (!data.username || data.username.trim().length < 3) {
      errores.push('El nombre de usuario debe tener al menos 3 caracteres')
    }
    
    if (!/^[a-zA-Z0-9._]+$/.test(data.username)) {
      errores.push('El nombre de usuario solo puede contener letras, números, puntos y guiones bajos')
    }
  }
  
  if ('email' in data && data.email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(data.email)) {
      errores.push('El formato del correo electrónico no es válido')
    }
  }
  
  if ('password' in data) {
    if (!data.password || data.password.length < 4) {
      errores.push('La contraseña debe tener al menos 4 caracteres')
    }
    
    if ('confirm_password' in data && data.password !== data.confirm_password) {
      errores.push('Las contraseñas no coinciden')
    }
  }
  
  return errores
}

export default usuariosService