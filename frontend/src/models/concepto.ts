// models/concepto.ts
export interface Concepto {
    cod_concepto: number;
    concepto: string;
    fecha?: string;
    evaluacion?: string;
    detalle_concepto?: string;
    observacion?: string;
    cod_detalle?: number; // Referencia a DetalleInsumo
    pdf?: string;
  }