// src/store/auth.ts - VERSIÓN CORREGIDA
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/config'
import type { User, LoginCredentials } from '@/models/auth'

export const useAuthStore = defineStore('auth', () => {
  // Estado
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const loading = ref<boolean>(false)
  const error = ref<string | null>(null)

  // ==================== GETTERS ====================
  
const isAuthenticated = computed(() => !!token.value)

// 🆕 SUPER ADMIN - Nuevo
const isSuperAdmin = computed(() => {
  if (!user.value) return false;
  return user.value.isSuperAdmin === true || user.value.rol_tipo === 'super_admin';
});

// 🔧 ADMIN NORMAL - Cambiado
  const isAdmin = computed(() => {
    if (!user.value) return false;
    return user.value.isAdmin === true || user.value.rol_tipo === 'admin';
  });

  // PROFESIONAL - Sin cambios
  const isProfesional = computed(() => {
    return user.value?.rol_tipo === 'profesional';
  });

  // 🆕 CUALQUIER ADMIN - Para retrocompatibilidad
  const isAnyAdmin = computed(() => {
    return isSuperAdmin.value || isAdmin.value;
  });

  const userRole = computed(() => {
    return user.value?.rol_tipo || 'publico';
  });

  // ==================== ACCIONES ====================
  
  // 🔧 LOGIN CORREGIDO - MANEJO MEJORADO DE RESPUESTA
  async function login(credentials: LoginCredentials) {
    try {
      loading.value = true;
      error.value = null;
      console.log("🔑 Iniciando login para:", credentials.username);

      // Hacer petición de login
      const response = await api.post('/api-token-auth/', credentials);
      
      console.log("📋 Respuesta completa del servidor:", response);
      
      // 🔧 MANEJO MEJORADO DE LA RESPUESTA
      let tokenValue = null;
      
      // Verificar diferentes posibles estructuras de respuesta
      if (response?.data?.token) {
        tokenValue = response.data.token;
      } else if (response?.token) {
        tokenValue = response.token;
      } else if (typeof response === 'string') {
        // Algunas APIs devuelven solo el token como string
        tokenValue = response;
      } else if (response?.data && typeof response.data === 'string') {
        tokenValue = response.data;
      }
      
      console.log("🔍 Token extraído:", tokenValue ? "✅ Encontrado" : "❌ No encontrado");
      console.log("🔍 Estructura de respuesta:", {
        hasData: !!response?.data,
        dataType: typeof response?.data,
        hasToken: !!response?.data?.token,
        directToken: !!response?.token,
        responseKeys: response ? Object.keys(response) : 'No response',
        dataKeys: response?.data ? Object.keys(response.data) : 'No data'
      });

      if (!tokenValue) {
        console.error("❌ No se encontró token en la respuesta");
        throw new Error('Respuesta de login inválida - no se recibió token');
      }

      console.log("✅ Token recibido correctamente");
      
      // Guardar token
      localStorage.setItem('token', tokenValue);
      token.value = tokenValue;

      // Obtener perfil del usuario
      const userData = await getProfile();
      
      if (userData) {
        user.value = userData;
        localStorage.setItem('userProfile', JSON.stringify(userData));
        console.log("✅ Login exitoso para:", userData.username, "- Admin:", !!(userData.isStaff || userData.isAdmin));
        return true;
      } else {
        throw new Error("No se pudo obtener el perfil del usuario");
      }
      
    } catch (err: any) {
      console.error("❌ Error en login:", err);
      console.error("❌ Respuesta de error:", err.response);
      
      // Determinar el mensaje de error
      let errorMessage = 'Error de conexión';
      
      if (err.response) {
        console.log("📋 Status de error:", err.response.status);
        console.log("📋 Data de error:", err.response.data);
        
        if (err.response.status === 400) {
          errorMessage = 'Usuario o contraseña incorrectos';
        } else if (err.response.status === 401) {
          errorMessage = 'Credenciales inválidas';
        } else if (err.response.data?.non_field_errors) {
          errorMessage = err.response.data.non_field_errors[0];
        } else if (err.response.data?.detail) {
          errorMessage = err.response.data.detail;
        } else if (err.response.data?.error) {
          errorMessage = err.response.data.error;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      error.value = errorMessage;
      
      // Limpiar estado en caso de error
      localStorage.removeItem('token');
      localStorage.removeItem('userProfile');
      token.value = null;
      user.value = null;
      
      return false;
    } finally {
      loading.value = false;
    }
  }

  // 🔧 LOGOUT SIMPLE (sin llamadas a APIs inexistentes)
  async function logout() {
    try {
      console.log("🚪 Cerrando sesión...");
      clearSession();
      console.log("✅ Sesión cerrada");
      return true;
    } catch (err: any) {
      console.error("❌ Error en logout:", err);
      return false;
    }
  }

  // 🆕 Función auxiliar para limpiar sesión
  function clearSession() {
    console.log("🧹 Limpiando datos de sesión...");
    localStorage.removeItem('token');
    localStorage.removeItem('userProfile');
    localStorage.removeItem('userId');
    token.value = null;
    user.value = null;
    error.value = null;
  }

  // 🔧 CHECK AUTH - SIEMPRE VALIDA CON EL SERVIDOR
  async function checkAuth() {
    const storedToken = localStorage.getItem('token');

    if (!storedToken) {
      console.log("⚠️ No hay token guardado");
      user.value = null;
      token.value = null;
      return false;
    }

    token.value = storedToken;

    // SIEMPRE verificar con el servidor si el token es válido
    // Esto detecta tokens expirados aunque estén en localStorage
    try {
      console.log("🔍 Verificando validez del token con el servidor...");
      const userData = await getProfile();

      if (userData) {
        user.value = userData;
        localStorage.setItem('userProfile', JSON.stringify(userData));
        console.log("✅ Token válido - Sesión activa para:", userData.username);
        return true;
      }
    } catch (err: any) {
      console.error("❌ Token inválido o expirado:", err.response?.status);

      // Limpiar sesión - el interceptor ya habrá redirigido si es 401
      clearSession();
      return false;
    }

    return false;
  }

  // 🔧 GET PROFILE CORREGIDO - MANEJO FLEXIBLE DE RESPUESTA
  async function getProfile() {
    if (!token.value) {
      throw new Error('No hay token disponible');
    }
    
    try {
      console.log("🔍 Obteniendo perfil del usuario...");
      
      const response = await api.get('/preoperacion/usuario-actual/', {
        headers: { 'Authorization': `Token ${token.value}` }
      });
      
      console.log("📋 Respuesta de perfil completa:", response);
      console.log("📋 Tipo de respuesta:", typeof response);
      console.log("📋 Keys de respuesta:", response ? Object.keys(response) : 'No response');
      
      // 🔧 MANEJO FLEXIBLE DE LA RESPUESTA
      let profileData = null;
      
      // Verificar diferentes estructuras posibles
      if (response?.data) {
        profileData = response.data;
        console.log("✅ Datos encontrados en response.data");
      } else if (response?.id || response?.username) {
        profileData = response;
        console.log("✅ Datos encontrados directamente en response");
      } else if (typeof response === 'object' && response !== null) {
        profileData = response;
        console.log("✅ Usando response directamente como objeto");
      }
      
      console.log("📋 Profile data extraída:", profileData);
      
      if (!profileData) {
        console.error("❌ No se encontraron datos de perfil en ninguna estructura");
        throw new Error("Respuesta vacía del servidor - no se encontraron datos de perfil");
      }
      
      // Verificar que tenga al menos un identificador
      if (!profileData.id && !profileData.username && !profileData.cod_usuario) {
        console.error("❌ Datos de perfil sin identificador válido:", profileData);
        throw new Error("Datos de perfil inválidos - falta identificador");
      }
      
      // 🔧 MAPEO SIMPLE Y DIRECTO
    const userData: User = {
      id: profileData.id || profileData.cod_usuario,
      username: profileData.username || profileData.user || '',
      email: profileData.email || '',
      firstName: profileData.firstName || profileData.first_name || profileData.nombre?.split(' ')[0] || '',
      lastName: profileData.lastName || profileData.last_name || profileData.nombre?.split(' ')[1] || '',
      isActive: profileData.isActive !== false,
      isStaff: profileData.isStaff === true,
      
      // 🆕 AGREGAR ESTOS CAMPOS NUEVOS:
      isSuperUser: profileData.isSuperUser === true,
      isAdmin: profileData.isAdmin === true,         // Admin normal del backend
      isSuperAdmin: profileData.isSuperAdmin === true, // Super admin del backend
      
      rol_tipo: profileData.rol_tipo || 'publico',
      municipios_asignados: profileData.municipios_asignados || [],
      groups: profileData.groups || [],
      cod_usuario: profileData.cod_usuario,
      nombre: profileData.nombre || profileData.full_name || ''
    };
      
      console.log("👤 Perfil mapeado:", {
        username: userData.username,
        isStaff: userData.isStaff,
        isAdmin: userData.isAdmin,
        rol_tipo: userData.rol_tipo,
        municipios_asignados: userData.municipios_asignados,
        municipios_count: Array.isArray(userData.municipios_asignados) ? userData.municipios_asignados.length : 0,
        hasId: !!userData.id
      });
      
      return userData;
    } catch (err: any) {
      console.error("❌ Error obteniendo perfil:", err);
      console.error("❌ Respuesta del error:", err.response);
      console.error("❌ Status del error:", err.response?.status);
      console.error("❌ Data del error:", err.response?.data);
      throw err;
    }
  }

  // 🔧 REFRESH USER PROFILE
  async function refreshUserProfile() {
    if (!token.value) return false;
    
    try {
      const userData = await getProfile();
      if (userData) {
        user.value = userData;
        localStorage.setItem('userProfile', JSON.stringify(userData));
        console.log("✅ Perfil actualizado");
        return true;
      }
      return false;
    } catch (err) {
      console.error("❌ Error actualizando perfil:", err);
      return false;
    }
  }

  // Verificar acceso a municipio
  function tieneAccesoAMunicipio(municipioId: number): boolean {
    if (isAdmin.value) return true;
    
    if (!user.value?.municipios_asignados) return false;
    
    let municipios: number[] = [];
    
    if (typeof user.value.municipios_asignados === 'string') {
      municipios = user.value.municipios_asignados.split(',')
        .map(m => parseInt(m.trim()))
        .filter(m => !isNaN(m));
    } else if (Array.isArray(user.value.municipios_asignados)) {
      municipios = user.value.municipios_asignados;
    }
    
    return municipios.includes(municipioId);
  }

  // Otras funciones
  async function verifyAuthentication() {
    return checkAuth();
  }

  async function updateProfile(profileData: Partial<User>) {
    try {
      loading.value = true;
      const response = await api.post('/preoperacion/actualizar-perfil/', profileData, {
        headers: { 'Authorization': `Token ${token.value}` }
      });
      
      // Manejo flexible de respuesta
      let updatedData = null;
      if (response?.data) {
        updatedData = response.data;
      } else if (response && typeof response === 'object') {
        updatedData = response;
      }
      
      if (updatedData) {
        user.value = { ...user.value, ...updatedData };
        localStorage.setItem('userProfile', JSON.stringify(user.value));
        return true;
      }
      return false;
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Error actualizando perfil';
      return false;
    } finally {
      loading.value = false;
    }
  }

  return {
    // Estado
    user,
    token,
    loading,
    error,
    
    // Getters
  isAuthenticated,
    isSuperAdmin,    
    isAdmin,         
    isAnyAdmin,      
    isProfesional,
    userRole,
    
    // Acciones
    login,
    logout,
    checkAuth,
    refreshUserProfile,
    verifyAuthentication,
    updateProfile,
    tieneAccesoAMunicipio,
    getProfile
  }
})