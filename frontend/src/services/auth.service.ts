import axios, { AxiosError } from 'axios';
import api, { API_URL } from '@/api/config';

// Tipos de datos
interface LoginCredentials {
  username: string;
  password: string;
}

interface LoginResponse {
  token: string;
  user?: UserProfile;
}

interface UserProfile {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

export const authService = {
  // ==================== Utilidades ====================
  getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
      headers: { 
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      }
    };
  },

  // ==================== Autenticación ====================
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      const response = await api.post<LoginResponse>('/api/token/', credentials);
      
      if (!response.data.token) {
        throw new Error('Respuesta de login inválida');
      }

      localStorage.setItem('token', response.data.token);

      if (response.data.user) {
        this.saveUserData(response.data.user);
      } else {
        await this.refreshUserProfile();
      }

      return response.data;

    } catch (error) {
      const err = error as AxiosError;
      throw new Error(
        err.response?.data?.detail || 
        'Error de autenticación. Verifique sus credenciales'
      );
    }
  },

  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('userProfile');
    localStorage.removeItem('userId');
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  },

  // ==================== Gestión de perfil ====================
  async getProfile(): Promise<UserProfile> {
    try {
      const response = await api.get<UserProfile>(
      '/preoperacion/usuarios/me/', 
      this.getAuthHeaders()
    );
      
      if (!response.data) {
        throw new Error('Perfil no encontrado');
      }

      this.saveUserData(response.data);
      return response.data;

    } catch (error) {
      const savedProfile = localStorage.getItem('userProfile');
      if (savedProfile) {
        console.warn('Usando perfil almacenado localmente');
        return JSON.parse(savedProfile);
      }
      throw new Error('No se pudo obtener el perfil del usuario');
    }
  },

  // Actualizaciones en auth.service.ts

  // Actualizar el método updateProfile
  async updateProfile(profileData: Partial<UserProfile>): Promise<UserProfile> {
    try {
      // Usar el nuevo endpoint para actualizar perfil
      const response = await api.post(
        '/preoperacion/actualizar-perfil/',
        profileData
      );
      
      if (response) {
        // Actualizar perfil en localStorage
        const currentProfile = JSON.parse(localStorage.getItem('userProfile') || '{}');
        const updatedProfile = { ...currentProfile, ...response };
        localStorage.setItem('userProfile', JSON.stringify(updatedProfile));
        
        return updatedProfile;
      } else {
        throw new Error('Respuesta vacía al actualizar perfil');
      }
    } catch (error) {
      console.error('Error al actualizar perfil:', error);
      throw error;
    }
  },

  // Actualizar el método changePassword
  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    try {
      const passwordData = {
        old_password: oldPassword,
        new_password: newPassword
      };
      
      // Usar el nuevo endpoint para cambiar contraseña
      await api.post('/preoperacion/cambiar-password/', passwordData);
    } catch (error) {
      console.error('Error al cambiar contraseña:', error);
      throw error;
    }
  },


   // ==================== Funciones auxiliares ====================
  saveUserData(userData: UserProfile): void { // <-- Quitar "private"
    localStorage.setItem('userProfile', JSON.stringify(userData));
    if (userData.id) {
      localStorage.setItem('userId', userData.id);
    }
  },

  async refreshUserProfile(): Promise<UserProfile> {
    return this.getProfile();
  },

  async checkAuth(): Promise<boolean> {
    if (!this.isAuthenticated()) return false;
    
    try {
      await this.getProfile();
      return true;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        this.logout();
      }
      return false;
    }
  }
};

export default authService;