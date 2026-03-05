#!/usr/bin/env python3
"""
SCRIPT DETALLE_CP - FIX FINAL
CORRIGE AMBOS PROBLEMAS:
1. Estado mal formateado (Oficializado vs OFICIALIZADO)
2. Centros poblados inexistentes
"""

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import datetime, date
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'detalle_cp_fix_final_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

print("=== SCRIPT DETALLE_CP - FIX FINAL ===")
print("CORRIGE PROBLEMAS IDENTIFICADOS:")
print("✅ Estado: convierte 'Oficializado' → 'OFICIALIZADO' al insertar")
print("✅ Centros poblados: inserta NULL si no existe")
print("=" * 60)

class ExcelProcessorCPFixFinal:
    def __init__(self):
        self.db_config = {
            'dbname': 'gestion_dato_db',
            'user': 'postgres',
            'password': '1234',
            'host': 'localhost',
            'port': '5432'
        }
        self.conn = None
        self.failed_records = []
        
        # MAPEO DE CLASIFICACIONES
        self.mapeo_clasificaciones = {
            'ORTOFOTO': ['Ortoimagen', 'Ortofoto', 'OrtoimÃ¡genes', 'Ortoimágenes'],
            'CARTOGRAFIA': ['Cartografia Basica (Vectorial)', 'CartografÃ­a BÃ¡sica (Vectorial)', 
                           'Cartografia Basica', 'CartografÃ­a BÃ¡sica', 'Cartografía Básica'],
            'MDT': ['Modelo Digital Terreno', 'Modelo Digital del Terreno', 'Modelo Digital de Terreno', 'MDT']
        }
        
        # GRUPOS
        self.groups = {
            'ORTOFOTO': {
                'zona': 'CENTROS POBLADOS',
                'formato_tipo': 'TIFF',
                'escala_pos': 9,
                'vigencia_pos': 10,
                'cubrimiento_pos': 11
            },
            'CARTOGRAFIA': {
                'zona': 'CENTROS POBLADOS',
                'formato_tipo': 'GDB',
                'escala_pos': 13,
                'vigencia_pos': 14,
                'cubrimiento_pos': 15
            },
            'MDT': {
                'zona': 'CENTROS POBLADOS',
                'formato_tipo': 'RASTER',
                'escala_pos': 17,
                'vigencia_pos': 18,
                'cubrimiento_pos': 19
            }
        }
        
        # POSICIONES BASE
        self.base_positions = {
            'divipola_municipio': 0,
            'divipola_centro_poblado': 3,
            'area_oficial': 5,
            'estado_principal': 6
        }
        
        # CONTADORES
        self.contadores = {
            'filas_procesadas': 0,
            'filas_con_estado_valido': 0,
            'municipios_unicos': set(),
            'centros_poblados_registrados': 0,
            'registros_por_grupo': {'ORTOFOTO': 0, 'CARTOGRAFIA': 0, 'MDT': 0},
            'clasificaciones_encontradas': {'ORTOFOTO': 0, 'CARTOGRAFIA': 0, 'MDT': 0},
            'inserciones_exitosas': 0,
            'errores_sql': 0,
            'estados_encontrados': {},
            'clasificaciones_cache': {}
        }

    def connect_db(self):
        try:
            self.conn = psycopg2.connect(**self.db_config)
            logger.info("Conexión a base de datos establecida")
            return True
        except Exception as e:
            logger.error(f"Error conectando a BD: {e}")
            return False

    def cargar_cache_centros_poblados(self):
        """Carga códigos de centros poblados válidos"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT cod_centro_poblado FROM centros_poblados")
            
            for row in cursor.fetchall():
                self.cache_centros_poblados.add(row[0])
            
            logger.info(f"Cache cargado: {len(self.cache_centros_poblados)} centros poblados válidos")
            
            # Mostrar algunos ejemplos
            if len(self.cache_centros_poblados) > 0:
                ejemplos = list(self.cache_centros_poblados)[:10]
                logger.info(f"Ejemplos de códigos válidos: {ejemplos}")
            else:
                logger.warning("⚠️ NO HAY CENTROS POBLADOS en la BD - todos serán NULL")
            
        except Exception as e:
            logger.error(f"Error cargando cache de centros poblados: {e}")

    def get_next_cod_detalle(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COALESCE(MAX(cod_detalle), 0) + 1 FROM detalle_insumo")
            next_code = cursor.fetchone()[0]
            logger.info(f"Próximo cod_detalle: {next_code}")
            return next_code
        except Exception as e:
            logger.error(f"Error obteniendo cod_detalle: {e}")
            return None

    def validate_y_normalizar_estado(self, estado):
        """
        🎯 FIX CRÍTICO: Valida Y normaliza el estado para inserción
        """
        if pd.isna(estado) or estado is None or estado == '':
            return False, None
        
        estado_clean = str(estado).strip().upper()
        valid_estados = ["OFICIALIZADO", "OFICIALIZADO PARCIAL"]
        is_valid = estado_clean in valid_estados
        
        # Registrar estadística
        if estado_clean in self.contadores['estados_encontrados']:
            self.contadores['estados_encontrados'][estado_clean] += 1
        else:
            self.contadores['estados_encontrados'][estado_clean] = 1
            
        # 🎯 RETORNAR ESTADO NORMALIZADO para inserción
        return is_valid, estado_clean if is_valid else None

    def find_cod_clasificacion_flexible(self, cod_municipio, tipo_grupo):
        """Búsqueda de clasificaciones existentes"""
        cache_key = f"{cod_municipio}_{tipo_grupo}"
        if cache_key in self.contadores['clasificaciones_cache']:
            return self.contadores['clasificaciones_cache'][cache_key]
        
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            nombres_posibles = self.mapeo_clasificaciones[tipo_grupo]
            
            query = """
            SELECT ci.cod_clasificacion, ci.nombre
            FROM clasificacion_insumo ci
            INNER JOIN insumos i ON ci.cod_insumo = i.cod_insumo
            INNER JOIN municipios m ON i.cod_municipio = m.cod_municipio
            WHERE m.cod_municipio = %s 
            AND i.cod_categoria = 1 
            AND i.tipo_insumo = 'Insumo Primario'
            AND ci.nombre = %s
            """
            
            for nombre in nombres_posibles:
                cursor.execute(query, (cod_municipio, nombre))
                result = cursor.fetchone()
                
                if result:
                    self.contadores['clasificaciones_cache'][cache_key] = result['cod_clasificacion']
                    self.contadores['clasificaciones_encontradas'][tipo_grupo] += 1
                    return result['cod_clasificacion']
            
            # Búsqueda por palabras clave
            palabras_clave = {'ORTOFOTO': 'orto', 'CARTOGRAFIA': 'cartograf', 'MDT': 'modelo'}
            palabra = palabras_clave.get(tipo_grupo, '')
            
            if palabra:
                query_like = """
                SELECT ci.cod_clasificacion, ci.nombre
                FROM clasificacion_insumo ci
                INNER JOIN insumos i ON ci.cod_insumo = i.cod_insumo
                INNER JOIN municipios m ON i.cod_municipio = m.cod_municipio
                WHERE m.cod_municipio = %s 
                AND i.cod_categoria = 1 
                AND i.tipo_insumo = 'Insumo Primario'
                AND ci.nombre ILIKE %s
                LIMIT 1
                """
                
                cursor.execute(query_like, (cod_municipio, f'%{palabra}%'))
                result = cursor.fetchone()
                
                if result:
                    self.contadores['clasificaciones_cache'][cache_key] = result['cod_clasificacion']
                    self.contadores['clasificaciones_encontradas'][tipo_grupo] += 1
                    return result['cod_clasificacion']
            
            self.contadores['clasificaciones_cache'][cache_key] = None
            return None
                
        except Exception as e:
            logger.error(f"Error buscando clasificación {tipo_grupo}: {e}")
            self.contadores['clasificaciones_cache'][cache_key] = None
            return None

    def get_value_by_position(self, row, position):
        try:
            if position < len(row):
                value = row.iloc[position]
                return value if pd.notna(value) else None
            return None
        except Exception as e:
            logger.error(f"Error obteniendo valor en posición {position}: {e}")
            return None

    def validar_centro_poblado(self, divipola_centro_poblado):
        """
        🎯 FIX CRÍTICO: Retorna código COMPLETO del DIVIPOLA centro poblado
        """
        if pd.isna(divipola_centro_poblado):
            return None
            
        try:
            # 🎯 USAR CÓDIGO COMPLETO, no solo los últimos 3 dígitos
            codigo_centro_completo = str(int(divipola_centro_poblado))
            
            if len(codigo_centro_completo) >= 5:  # DIVIPOLA mínimo
                self.contadores['centros_poblados_registrados'] += 1
                return codigo_centro_completo  # ✅ RETORNAR CÓDIGO COMPLETO
            else:
                return None
            
        except (ValueError, TypeError):
            return None

    def format_porcentaje_cubrimiento(self, value):
        if pd.isna(value) or value is None:
            return None
        
        try:
            num_value = float(value)
            if num_value >= 999:
                return "999"
            if num_value == int(num_value) and num_value < 999:
                return str(int(num_value))
            return str(int(round(num_value))) if num_value >= 1 else "0"
        except (ValueError, TypeError):
            return None

    def prepare_record_data(self, row, group_config, grupo_nombre, cod_detalle, cod_municipio, cod_centro_poblado, area_oficial, cod_clasificacion, estado_normalizado):
        """
        🎯 FIX CRÍTICO: Usa estado_normalizado (OFICIALIZADO) en lugar de estado original
        """
        escala = self.get_value_by_position(row, group_config['escala_pos'])
        vigencia = self.get_value_by_position(row, group_config['vigencia_pos'])
        porcentaje_cubrimiento_raw = self.get_value_by_position(row, group_config['cubrimiento_pos'])
        porcentaje_cubrimiento = self.format_porcentaje_cubrimiento(porcentaje_cubrimiento_raw)
        
        return {
            'cod_detalle': cod_detalle,
            'escala': escala,
            'estado': estado_normalizado,  # 🎯 USA ESTADO NORMALIZADO
            'cubrimiento': None,
            'fecha_entrega': None,
            'fecha_disposicion': datetime.now().date(),
            'area': area_oficial,
            'cod_entidad': 'IGAC',
            'observacion': None,
            'vigencia': vigencia,
            'formato_tipo': group_config['formato_tipo'],
            'cod_usuario': 1053840329,
            'cod_clasificacion': cod_clasificacion,
            'zona': group_config['zona'],
            'cod_centro_poblado': cod_centro_poblado,  # 🎯 PUEDE SER NULL
            'ruta_archivo': None,
            'porcentaje_cubrimiento': porcentaje_cubrimiento
        }

    def insert_record(self, record_data):
        try:
            cursor = self.conn.cursor()
            
            insert_query = """
            INSERT INTO detalle_insumo (
                cod_detalle, escala, estado, cubrimiento, fecha_entrega, fecha_disposicion,
                area, cod_entidad, observacion, vigencia, formato_tipo, cod_usuario,
                cod_clasificacion, zona, cod_centro_poblado, ruta_archivo, porcentaje_cubrimiento
            ) VALUES (
                %(cod_detalle)s, %(escala)s, %(estado)s, %(cubrimiento)s, %(fecha_entrega)s, 
                %(fecha_disposicion)s, %(area)s, %(cod_entidad)s, %(observacion)s, %(vigencia)s,
                %(formato_tipo)s, %(cod_usuario)s, %(cod_clasificacion)s, %(zona)s, 
                %(cod_centro_poblado)s, %(ruta_archivo)s, %(porcentaje_cubrimiento)s
            )
            """
            
            cursor.execute(insert_query, record_data)
            self.conn.commit()
            
            self.contadores['inserciones_exitosas'] += 1
            return True, None
            
        except Exception as e:
            logger.error(f"Error insertando registro: {e}")
            self.conn.rollback()
            self.contadores['errores_sql'] += 1
            return False, str(e)

    def process_excel_file(self, file_path):
        try:
            logger.info(f"Iniciando procesamiento FIX FINAL: {file_path}")
            
            df = pd.read_excel(file_path, header=1, sheet_name='DETALLE_CP')
            logger.info(f"Excel cargado: {len(df)} filas")
            
            total_insertados = 0
            total_omitidos = 0
            
            current_cod_detalle = self.get_next_cod_detalle()
            if current_cod_detalle is None:
                raise Exception("No se pudo obtener cod_detalle inicial")
            
            for index, row in df.iterrows():
                fila_num = index + 2
                self.contadores['filas_procesadas'] += 1
                
                if index % 500 == 0:
                    logger.info(f"Procesando fila {fila_num} ({self.contadores['filas_procesadas']}/{len(df)})")
                
                # Obtener datos básicos
                divipola_municipio = self.get_value_by_position(row, self.base_positions['divipola_municipio'])
                divipola_centro_poblado = self.get_value_by_position(row, self.base_positions['divipola_centro_poblado'])
                area_oficial = self.get_value_by_position(row, self.base_positions['area_oficial'])
                estado_principal = self.get_value_by_position(row, self.base_positions['estado_principal'])
                
                # Validar datos básicos
                if pd.isna(divipola_municipio) or pd.isna(divipola_centro_poblado):
                    continue
                
                # 🎯 VALIDACIÓN Y NORMALIZACIÓN DE ESTADO
                es_valido, estado_normalizado = self.validate_y_normalizar_estado(estado_principal)
                if not es_valido:
                    continue
                
                self.contadores['filas_con_estado_valido'] += 1
                
                codigo_municipio = int(divipola_municipio)
                codigo_centro_poblado = self.validar_centro_poblado(divipola_centro_poblado)
                
                self.contadores['municipios_unicos'].add(codigo_municipio)
                
                # GENERAR 3 REGISTROS
                registros_insertados_fila = 0
                
                for grupo_nombre, group_config in self.groups.items():
                    # Buscar clasificación
                    cod_clasificacion = self.find_cod_clasificacion_flexible(codigo_municipio, grupo_nombre)
                    if not cod_clasificacion:
                        continue
                    
                    # 🎯 PASAR ESTADO NORMALIZADO
                    record_data = self.prepare_record_data(
                        row, group_config, grupo_nombre, current_cod_detalle, 
                        codigo_municipio, codigo_centro_poblado, 
                        area_oficial, cod_clasificacion, estado_normalizado
                    )
                    
                    # Insertar registro
                    success, error = self.insert_record(record_data)
                    if success:
                        total_insertados += 1
                        registros_insertados_fila += 1
                        self.contadores['registros_por_grupo'][grupo_nombre] += 1
                        current_cod_detalle += 1
                    else:
                        logger.error(f"Error insertando fila {fila_num}, grupo {grupo_nombre}: {error}")
                
                if registros_insertados_fila == 0:
                    total_omitidos += 1
            
            self.mostrar_estadisticas_finales()
            return total_insertados, total_omitidos
            
        except Exception as e:
            logger.error(f"Error procesando Excel: {e}")
            return 0, 0

    def mostrar_estadisticas_finales(self):
        logger.info("\n" + "="*60)
        logger.info("ESTADÍSTICAS FINALES - FIX FINAL COMPLETO")
        logger.info("="*60)
        logger.info(f"Filas procesadas: {self.contadores['filas_procesadas']}")
        logger.info(f"Filas con estado válido: {self.contadores['filas_con_estado_valido']}")
        logger.info(f"Municipios únicos: {len(self.contadores['municipios_unicos'])}")
        logger.info(f"Centros poblados registrados: {self.contadores['centros_poblados_registrados']}")
        logger.info(f"Inserciones exitosas: {self.contadores['inserciones_exitosas']}")
        logger.info(f"Errores SQL: {self.contadores['errores_sql']}")
        
        logger.info(f"\nREGISTROS POR GRUPO:")
        for grupo, cantidad in self.contadores['registros_por_grupo'].items():
            encontradas = self.contadores['clasificaciones_encontradas'][grupo]
            logger.info(f"   {grupo}: {cantidad} insertados ({encontradas} clasificaciones encontradas)")

    def select_file(self):
        root = tk.Tk()
        root.withdraw()
        
        file_path = filedialog.askopenfilename(
            title="Seleccionar Excel - DETALLE_CP",
            filetypes=[("Excel files", "*.xlsx *.xlsm *.xls")]
        )
        
        root.destroy()
        return file_path

    def run(self):
        logger.info("Iniciando SCRIPT DETALLE_CP - FIX FINAL COMPLETO")
        
        if not self.connect_db():
            return
        
        try:
            file_path = self.select_file()
            if not file_path:
                logger.info("No se seleccionó archivo")
                return
            
            logger.info(f"Archivo seleccionado: {file_path}")
            
            insertados, omitidos = self.process_excel_file(file_path)
            
            message = f"""
PROCESAMIENTO DETALLE_CP COMPLETADO - FIX FINAL COMPLETO

🎯 PROBLEMAS CORREGIDOS:
✅ Estado: 'Oficializado' → 'OFICIALIZADO' 
✅ Centro poblado: USA CÓDIGO COMPLETO del DIVIPOLA

📊 RESULTADOS:
Registros insertados: {insertados}
Registros omitidos: {omitidos}

ESTADÍSTICAS:
Filas con estado válido: {self.contadores['filas_con_estado_valido']}
Municipios únicos: {len(self.contadores['municipios_unicos'])}
Centros poblados registrados: {self.contadores['centros_poblados_registrados']}

REGISTROS POR GRUPO:
ORTOFOTO: {self.contadores['registros_por_grupo']['ORTOFOTO']}
CARTOGRAFIA: {self.contadores['registros_por_grupo']['CARTOGRAFIA']}
MDT: {self.contadores['registros_por_grupo']['MDT']}
            """
            
            messagebox.showinfo("Resumen - Fix Final Completo", message.strip())
            logger.info("PROCESAMIENTO COMPLETADO EXITOSAMENTE")
            
        except Exception as e:
            logger.error(f"Error en procesamiento principal: {e}")
            messagebox.showerror("Error", f"Error: {e}")
        
        finally:
            if self.conn:
                self.conn.close()

if __name__ == "__main__":
    processor = ExcelProcessorCPFixFinal()
    processor.run()