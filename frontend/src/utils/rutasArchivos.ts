// utils/rutasArchivos.ts

export interface InfoRutaArchivo {
  esCartografiaBasica: boolean;
  centroPoblado: string | null;
  codigoCentroPoblado: string | null;
  tipoCartografia: 'vectorial' | 'raster-ortofoto' | 'raster-dtm' | 'otro' | null;
  esUrbano: boolean;
}

/**
 * Analiza una ruta de archivo y extrae información relevante
 * @param ruta - Ruta completa del archivo
 * @param codigoMunicipio - Código del municipio (para construir el código del centro poblado)
 * @returns Objeto con información extraída de la ruta
 */
export function analizarRutaArchivo(ruta: string, codigoMunicipio: string): InfoRutaArchivo {
  const resultado: InfoRutaArchivo = {
    esCartografiaBasica: false,
    centroPoblado: null,
    codigoCentroPoblado: null,
    tipoCartografia: null,
    esUrbano: false
  };

  // Verificar si es cartografía básica
  resultado.esCartografiaBasica = ruta.includes('01_carto_basic');

  // Verificar si es urbano
  resultado.esUrbano = ruta.includes('01_urb') || ruta.includes('1_urb');

  if (resultado.esCartografiaBasica && resultado.esUrbano) {
    // Extraer centro poblado
    const regexCentroPoblado = /(?:01_urb|1_urb)[\\\/](\d{3})/;
    const matchCentroPoblado = ruta.match(regexCentroPoblado);
    
    if (matchCentroPoblado && matchCentroPoblado[1]) {
      resultado.centroPoblado = matchCentroPoblado[1];
      resultado.codigoCentroPoblado = codigoMunicipio + matchCentroPoblado[1];
    }

    // Determinar tipo de cartografía
    if (ruta.includes('02_vect')) {
      resultado.tipoCartografia = 'vectorial';
    } else if (ruta.includes('01_rast')) {
      if (ruta.includes('01_orto')) {
        resultado.tipoCartografia = 'raster-ortofoto';
      } else if (ruta.includes('02_dtm')) {
        resultado.tipoCartografia = 'raster-dtm';
      }
    }
  }

  return resultado;
}

/**
 * Extrae los centros poblados únicos de una lista de archivos
 * @param archivos - Lista de archivos con ruta_completa
 * @param codigoMunicipio - Código del municipio
 * @returns Array de códigos de centros poblados únicos
 */
export function extraerCentrosPobladosDeArchivos(
  archivos: Array<{ ruta_completa: string }>, 
  codigoMunicipio: string
): string[] {
  const centrosPoblados = new Set<string>();
  
  archivos.forEach(archivo => {
    const info = analizarRutaArchivo(archivo.ruta_completa, codigoMunicipio);
    if (info.centroPoblado) {
      centrosPoblados.add(info.centroPoblado);
    }
  });
  
  return Array.from(centrosPoblados).sort();
}