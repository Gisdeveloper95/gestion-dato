import api from './config';

// Interfaces
export interface Departamento {
  cod_depto: number;
  nom_depto: string;
}

// Obtener todos los departamentos
export const getDepartamentos = async (): Promise<Departamento[]> => {
  try {
    const response = await api.get<Departamento[]>('/preoperacion/departamentos/');
    return response || [];
  } catch (error) {
    console.error('Error al obtener departamentos:', error);
    throw error;
  }
};

// Obtener un departamento por ID
export const getDepartamentoById = async (id: number): Promise<Departamento> => {
  try {
    const response = await api.get<Departamento>(`/preoperacion/departamentos/${id}/`);
    return response;
  } catch (error) {
    console.error('Error al obtener departamento:', error);
    throw error;
  }
};