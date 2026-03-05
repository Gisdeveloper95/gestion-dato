import api,{ API_URL } from './config'
import type { LoginCredentials, LoginResponse, User } from '@/models/auth'

// Iniciar sesión
export const login = async (credentials: LoginCredentials): Promise<LoginResponse> => {
  try {
    // Usar la ruta correcta para obtener token de autenticación
    const response = await api.post('/api-token-auth/', credentials)
    
    // Verificar la estructura de la respuesta
    if (typeof response === 'object' && response !== null) {
      // Si la respuesta es un objeto, verificar si tiene token
      if ('token' in response) {
        return {
          token: response.token,
          user: response.user || { username: credentials.username }
        }
      } else {
        throw new Error('Respuesta de servidor inválida: no contiene token')
      }
    } else {
      throw new Error('Respuesta de servidor inválida')
    }
  } catch (error) {
    console.error('Error en login:', error)
    throw error
  }
}

// Cerrar sesión
export const logout = async (): Promise<boolean> => {
  try {
    // Limpiar todas las posibles fuentes de datos de sesión
    localStorage.removeItem('token');
    localStorage.removeItem('userProfile');
    sessionStorage.clear();
    
    // Si el backend tiene un endpoint para logout, llamarlo aquí
    // await api.post('/logout/');
    
    return true;
  } catch (error) {
    console.error('Error en logout:', error)
    // Intentar limpiar datos de sesión incluso si hay error
    localStorage.removeItem('token');
    localStorage.removeItem('userProfile');
    sessionStorage.clear();
    return false;
  }
}

// 🆕 GETPROFILE ACTUALIZADO PARA MANEJAR TODOS LOS CAMPOS
// auth.ts (ejemplo de implementación)
const getProfile = async (token: string) => {
  try {
    const response = await axios.get('/preoperacion/usuarios/me/', {
      headers: { Authorization: `Token ${token}` }
    });

    // Normalizar respuesta
    const userData = response.data;
    
    if (!userData.id && !userData.cod_usuario) {
      throw new Error('Formato de respuesta inválido: falta identificador');
    }

    return {
      id: userData.id || userData.cod_usuario,
      username: userData.username,
      firstName: userData.firstName || userData.nombre?.split(' ')[0] || '',
      lastName: userData.lastName || userData.nombre?.split(' ')[1] || '',
      email: userData.email,
      role: userData.rol_tipo
    };
    
  } catch (error) {
    console.error('❌ Error obteniendo perfil:', error);
    throw new Error('Error al obtener perfil: ' + error.message);
  }
};

// Verificar validez del token
export const verifyToken = async (): Promise<boolean> => {
  try {
    const token = localStorage.getItem('token');
    if (!token) return false;
    
    // Usa la nueva ruta para verificar el token
    const response = await api.get('/preoperacion/verify-token/');
    
    // Si la respuesta es exitosa, el token es válido
    return response && response.valid === true;
  } catch (error) {
    console.warn('Token inválido o expirado');
    // Limpiar token inválido
    localStorage.removeItem('token');
    localStorage.removeItem('userProfile');
    return false;
  }
}

// Registrar nuevo usuario (si se permite)
export const register = async (userData: Partial<User>): Promise<User> => {
  try {
    const response = await api.post('/preoperacion/register/', userData)
    return response
  } catch (error) {
    console.error('Error en registro:', error)
    throw error
  }
}

// Actualizar información del perfil
export const updateProfile = async (profileData: Partial<User>): Promise<User> => {
  try {
    const response = await api.post('/preoperacion/actualizar-perfil/', {
      firstName: profileData.firstName,
      lastName: profileData.lastName,
      email: profileData.email
    });
    
    if (response) {
      // Actualizar localStorage
      localStorage.setItem('userProfile', JSON.stringify(response));
      return response;
    }
    throw new Error('Error actualizando perfil: respuesta vacía');
  } catch (error) {
    console.error('Error actualizando perfil:', error);
    throw error;
  }
}

export const changePassword = async (passwordData: {
  old_password: string
  new_password: string
}): Promise<boolean> => {
  try {
    await api.post('/preoperacion/cambiar-password/', passwordData);
    return true;
  } catch (error) {
    console.error('Error cambiando contraseña:', error);
    throw error;
  }
}