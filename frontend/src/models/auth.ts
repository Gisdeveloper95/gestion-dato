export interface User {
  id?: number;
  username: string;
  email?: string;
  firstName?: string;
  lastName?: string;
  isActive?: boolean;
  isStaff?: boolean;
  isAdmin?: boolean;
  
  // 🆕 NUEVOS CAMPOS CRÍTICOS PARA ROLES
  rol_tipo?: 'administrador' | 'profesional' | 'publico';
  municipios_asignados?: number[] | string;
  groups?: string[];
  cod_usuario?: number;
  nombre?: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: User;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}