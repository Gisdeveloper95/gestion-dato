// src/services/archivos.ts
import { useAuthStore } from '@/store/auth';

export const archivosService = {
  /**
   * Extrae el código de municipio de una ruta de archivo
   */
  extraerCodigoMunicipioDeRuta(ruta: string): number | null {
    // Buscar el patrón después de 01_actualiz_catas\
    const regex = /01_actualiz_catas[\/\\](\d+)[\/\\](\d+)[\/\\]/i;
    const match = ruta.match(regex);
    
    if (match && match[1] && match[2]) {
      const codigoDepartamento = match[1];
      const codigoMunicipio = match[2];
      return parseInt(`${codigoDepartamento}${codigoMunicipio}`);
    }
    
    return null;
  },
  
  /**
   * Verifica si el usuario actual puede acceder a un archivo
   */
  puedeAccederArchivo(ruta: string, municipioId?: number): boolean {
    const authStore = useAuthStore();
    
    // Administradores tienen acceso a todo - USANDO LA MISMA LÓGICA DE TU NAVBAR
    if (authStore.isAdmin) {
      console.log("Usuario es admin, acceso permitido");
      return true;
    }
    
    // Si se proporciona directamente el ID del municipio
    if (municipioId) {
      const tieneAcceso = authStore.tieneAccesoAMunicipio(municipioId);
      console.log(`Verificando acceso a municipio ${municipioId}: ${tieneAcceso}`);
      return tieneAcceso;
    }
    
    // Intentar extraer el código del municipio de la ruta
    const codigoMunicipio = this.extraerCodigoMunicipioDeRuta(ruta);
    if (codigoMunicipio) {
      const tieneAcceso = authStore.tieneAccesoAMunicipio(codigoMunicipio);
      console.log(`Municipio extraído de ruta ${codigoMunicipio}, acceso: ${tieneAcceso}`);
      return tieneAcceso;
    }
    
    console.log("No se pudo determinar el municipio, acceso denegado");
    return false;
  },

   archivoDisponible(notificacion: any): boolean {
    const ruta = this.extraerRutaArchivo(notificacion);
    if (!ruta) return false;
    
    // Si la acción es eliminar, el archivo no está disponible
    const accion = notificacion.accion?.toLowerCase();
    if (accion === 'eliminar' || accion === 'delete') {
      return false;
    }
    
    // Verificar permisos de acceso
    return this.puedeAccederArchivo(ruta);
  },

  /**
   * Extraer ruta de archivo de los datos de contexto de una notificación
   */
  extraerRutaArchivo(notificacion: any): string | null {
    if (!notificacion.datos_contexto) return null;
    
    let contexto = notificacion.datos_contexto;
    if (typeof contexto === 'string') {
      try {
        contexto = JSON.parse(contexto);
      } catch {
        return null;
      }
    }
    
    if (contexto && typeof contexto === 'object') {
      return contexto.ruta || contexto.path_file || contexto.ruta_completa || contexto.archivo || null;
    }
    
    return null;
  },
  
  /**
   * Descargar archivo - Usa window.open con token para mostrar barra de progreso del navegador
   */
  descargarArchivo(ruta: string, _nombreArchivo?: string): void {
    if (!ruta) {
      console.error('Ruta de archivo no proporcionada');
      return;
    }

    const token = localStorage.getItem('token');
    const baseUrl = import.meta.env.VITE_API_URL || '';
    const downloadUrl = `${baseUrl}/preoperacion/descargar_archivo/?ruta=${encodeURIComponent(ruta)}&token=${token}`;

    console.log("Descargando archivo:", ruta);
    window.open(downloadUrl, '_blank');
  },

  /**
   * Descargar archivo de postoperación - Usa window.open con token
   */
  descargarArchivoPost(ruta: string, _nombreArchivo?: string): void {
    if (!ruta) {
      console.error('Ruta de archivo no proporcionada');
      return;
    }

    const token = localStorage.getItem('token');
    const baseUrl = import.meta.env.VITE_API_URL || '';
    const downloadUrl = `${baseUrl}/postoperacion/descargar_archivo/?ruta=${encodeURIComponent(ruta)}&token=${token}`;

    console.log("Descargando archivo post:", ruta);
    window.open(downloadUrl, '_blank');
  },

  /**
   * Descargar directorio como ZIP - Usa window.open con token
   */
  descargarDirectorio(ruta: string, municipioId?: number): void {
    if (!ruta) {
      console.error('Ruta de directorio no proporcionada');
      return;
    }

    const token = localStorage.getItem('token');
    const baseUrl = import.meta.env.VITE_API_URL || '';
    let downloadUrl = `${baseUrl}/preoperacion/descargar_directorio/?ruta=${encodeURIComponent(ruta)}&token=${token}`;

    if (municipioId) {
      downloadUrl += `&municipio_id=${municipioId}`;
    }

    console.log("Descargando directorio:", ruta);
    window.open(downloadUrl, '_blank');
  },
  
  /**
   * Obtener nombre de archivo de una ruta
   */
  obtenerNombreArchivo(ruta: string): string {
    if (!ruta) return 'archivo';
    
    // Manejar separadores de rutas para Windows y Unix
    const partes = ruta.split(/[\/\\]/);
    return partes[partes.length - 1];
  },

  /**
   * Obtener extensión de archivo
   */
  getFileExtension(fileName: string): string {
    if (!fileName) return '';
    return fileName.split('.').pop()?.toLowerCase() || '';
  },

  /**
   * Obtener ícono de archivo basado en extensión
   */
  getFileIcon(fileName: string): string {
    if (!fileName) return 'insert_drive_file';
    
    const extension = this.getFileExtension(fileName);
    
    switch (extension) {
      case 'pdf':
        return 'picture_as_pdf';
      case 'doc':
      case 'docx':
        return 'description';
      case 'xls':
      case 'xlsx':
      case 'csv':
        return 'table_chart';
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
      case 'tif':
      case 'tiff':
        return 'image';
      case 'zip':
      case 'rar':
        return 'folder_zip';
      case 'shp':
      case 'kml':
      case 'kmz':
        return 'map';
      default:
        return 'insert_drive_file';
    }
  },
    /**
   * Ver archivo en nueva ventana
   */
  verArchivo(ruta: string): void {
    const baseUrl = import.meta.env.VITE_API_URL || '';
    const url = `${baseUrl}/preoperacion/ver_pdf/?ruta=${encodeURIComponent(ruta)}`;
    window.open(url, '_blank');
  },

  /**
   * Validar si una ruta es válida
   */
  validarRuta(ruta: string): boolean {
    return !!(ruta && ruta.trim() !== '');
  },

  /**
   * Normalizar ruta de archivo
   */
  normalizarRuta(ruta: string): string {
    if (!ruta) return '';
    return ruta.replace(/\\/g, '/').replace(/\/+/g, '/').trim();
  }
};

export default archivosService;