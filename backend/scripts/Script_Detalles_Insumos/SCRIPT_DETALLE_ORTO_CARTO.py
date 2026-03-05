import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import datetime, date
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("=== PROCESADOR EXCEL DETALLE_ORTO_CARTO ===")
print("Dependencias requeridas:")
print("- pandas: pip install pandas")
print("- psycopg2: pip install psycopg2-binary") 
print("- openpyxl: pip install openpyxl")
print("- tkinter: incluido con Python")
print("")
print("CARACTERÍSTICAS:")
print("✅ Procesamiento por subgrupos (ORTO_R, CARTO_R, MDT_R, ORTO_CAB, CARTO_CAB, MDT_CAB)")
print("✅ Validación de estados (OFICIALIZADO, OFICIALIZADO PARCIAL)")
print("✅ Formateo automático de porcentajes (máximo 3 caracteres)")
print("✅ Conversión automática de decimales Excel (1 → 100%, 0.58 → 58%)")
print("✅ Manejo de valores con símbolo % (ej: '100%' → '100')")
print("✅ Límite máximo de cubrimiento: 100% (valores superiores → 100)")
print("✅ Detección y selección de valores múltiples (ej: '34%, 100%')")
print("✅ Omisión automática de registros con valores de texto")
print("✅ Detección de duplicados (evita insertar el mismo registro múltiples veces)")
print("✅ Reporte de errores por pestañas separadas")
print("✅ Sentencias SQL completas en errores")
print("=" * 50)

class ExcelProcessor:
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
        self.porcentajes_formateados = 0
        self.registros_omitidos_por_texto = 0
        self.registros_duplicados_omitidos = 0
        
        # Definir grupos y su mapeo
        self.groups = {
            'ORTO_R': {
                'zona': 'RURAL',
                'tipo_nombre': 'Ortoimagen',
                'formato_tipo': 'TIFF',
                'estado_col': 'ESTADO_ORTO_R',
                'escala_col': 'ESCALA_ORTO_R',
                'vigencia_col': 'VIGENCIA_ORTO_R',
                'cubrimiento_col': 'CUBRIMIENTO_ORTO_R',
                'area_especial': 'AREA_ORTO_R_(ha)'
            },
            'CARTO_R': {
                'zona': 'RURAL',
                'tipo_nombre': 'Cartografia Basica (Vectorial)',
                'formato_tipo': 'GDB',
                'estado_col': 'ESTADO_CARTO_R',
                'escala_col': 'ESCALA_CARTO_R',
                'vigencia_col': 'VIGENCIA_CARTO_R',
                'cubrimiento_col': 'CUBRIMIENTO_CARTO_R',
                'area_especial': None
            },
            'MDT_R': {
                'zona': 'RURAL',
                'tipo_nombre': 'Modelo Digital Terreno',
                'formato_tipo': 'RASTER',
                'estado_col': 'ESTADO_MDT_R',
                'escala_col': 'ESCALA_MDT_R',
                'vigencia_col': 'VIGENCIA_MDT_R',
                'cubrimiento_col': 'CUBRIMIENTO_MDT_R',
                'area_especial': None
            },
            'ORTO_CAB': {
                'zona': 'URBANO',
                'tipo_nombre': 'Ortoimagen',
                'formato_tipo': 'TIFF',
                'estado_col': 'ESTADO_ORTO_CAB',
                'escala_col': 'ESCALA_ORTO_CAB',
                'vigencia_col': 'VIGENCIA_ORTO_CAB',
                'cubrimiento_col': 'CUBRIMIENTO_ORTO_CAB',
                'area_especial': None
            },
            'CARTO_CAB': {
                'zona': 'URBANO',
                'tipo_nombre': 'Cartografia Basica (Vectorial)',
                'formato_tipo': 'GDB',
                'estado_col': 'ESTADO_CARTO_CAB',
                'escala_col': 'ESCALA_CARTO_CAB',
                'vigencia_col': 'VIGENCIA_CARTO_CAB',
                'cubrimiento_col': 'CUBRIMIENTO_CARTO_CAB',
                'area_especial': None
            },
            'MDT_CAB': {
                'zona': 'URBANO',
                'tipo_nombre': 'Modelo Digital Terreno',
                'formato_tipo': 'RASTER',
                'estado_col': 'ESTADO_MDT_CAB',
                'escala_col': 'ESCALA_MDT_CAB',
                'vigencia_col': 'VIGENCIA_MDT_CAB',
                'cubrimiento_col': 'CUBRIMIENTO_MDT_CAB',
                'area_especial': None
            }
        }

    def connect_db(self):
        """Conectar a la base de datos"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            logger.info("Conexión a base de datos establecida")
            return True
        except Exception as e:
            logger.error(f"Error conectando a la base de datos: {e}")
            messagebox.showerror("Error DB", f"No se pudo conectar a la base de datos: {e}")
            return False

    def get_next_cod_detalle(self):
        """Obtener el siguiente código de detalle disponible"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COALESCE(MAX(cod_detalle), 0) + 1 FROM detalle_insumo")
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error obteniendo siguiente cod_detalle: {e}")
            return None

    def find_cod_clasificacion(self, cod_municipio, tipo_nombre):
        """Encontrar el código de clasificación correcto"""
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            
            # Buscar en la cadena: municipios -> insumos -> clasificacion_insumo
            query = """
            SELECT ci.cod_clasificacion 
            FROM clasificacion_insumo ci
            INNER JOIN insumos i ON ci.cod_insumo = i.cod_insumo
            INNER JOIN municipios m ON i.cod_municipio = m.cod_municipio
            WHERE m.cod_municipio = %s 
            AND i.cod_categoria = 1 
            AND i.tipo_insumo = 'Insumo Primario'
            AND ci.nombre = %s
            """
            
            cursor.execute(query, (cod_municipio, tipo_nombre))
            result = cursor.fetchone()
            
            if result:
                return result['cod_clasificacion']
            else:
                logger.warning(f"No se encontró cod_clasificacion para municipio {cod_municipio} y tipo {tipo_nombre}")
                return None
                
        except Exception as e:
            logger.error(f"Error buscando cod_clasificacion: {e}")
            return None

    def record_already_exists(self, cod_clasificacion, cod_municipio, zona, formato_tipo):
        """Verificar si ya existe un registro similar para evitar duplicados"""
        try:
            cursor = self.conn.cursor()
            
            # Buscar registros existentes con los mismos parámetros clave
            check_query = """
            SELECT COUNT(*) FROM detalle_insumo 
            WHERE cod_clasificacion = %s 
            AND cod_usuario = %s
            AND zona = %s
            AND formato_tipo = %s
            AND fecha_disposicion = %s
            """
            
            cursor.execute(check_query, (
                cod_clasificacion, 
                1053840329,  # cod_usuario fijo
                zona,
                formato_tipo,
                datetime.now().date()
            ))
            
            count = cursor.fetchone()[0]
            return count > 0
            
        except Exception as e:
            logger.error(f"Error verificando duplicados: {e}")
            return False  # En caso de error, permitir inserción

    def validate_estado(self, estado):
        """Validar si el estado permite inserción"""
        valid_estados = ["OFICIALIZADO", "OFICIALIZADO PARCIAL"]
        return estado in valid_estados if pd.notna(estado) else False

    def format_porcentaje_cubrimiento(self, value, municipio_info="", grupo_info=""):
        """Formatear porcentaje de cubrimiento para cumplir límite de 3 caracteres"""
        if pd.isna(value) or value is None:
            return None
        
        try:
            # Convertir a string primero para manejar casos con %
            str_value = str(value).strip()
            original_str = str_value
            
            # Detectar valores de texto que no son porcentajes
            text_indicators = ["NO APLICA", "FALTA", "SIN FECHA", "DEFINIDA", "POR", "DGIG"]
            if any(indicator in str_value.upper() for indicator in text_indicators):
                logger.warning(f"Valor de texto detectado: '{original_str}' - OMITIENDO REGISTRO")
                return "TEXT_SKIP"  # Señal especial para omitir registro
            
            # Detectar valores múltiples (contiene comas)
            if ',' in str_value:
                # Extraer valores individuales
                parts = [p.strip().replace('%', '') for p in str_value.split(',') if p.strip()]
                try:
                    numeric_parts = [float(p) for p in parts if p and p.replace('.', '').replace('-', '').isdigit()]
                    if len(numeric_parts) > 1:
                        # Preguntar al usuario qué valor usar
                        print(f"\n⚠️  VALOR MÚLTIPLE DETECTADO")
                        print(f"   Municipio: {municipio_info}")
                        print(f"   Grupo: {grupo_info}")
                        print(f"   Valor original: '{original_str}'")
                        print(f"   Opciones encontradas:")
                        for i, val in enumerate(numeric_parts):
                            print(f"     {i+1}. {val}%")
                        
                        while True:
                            try:
                                choice = input(f"   Seleccione opción (1-{len(numeric_parts)}): ").strip()
                                choice_idx = int(choice) - 1
                                if 0 <= choice_idx < len(numeric_parts):
                                    selected_value = numeric_parts[choice_idx]
                                    logger.info(f"Valor múltiple '{original_str}' → seleccionado: {selected_value}")
                                    str_value = str(selected_value)  # Continuar procesamiento
                                    break
                                else:
                                    print("   ❌ Opción inválida. Intente nuevamente.")
                            except ValueError:
                                print("   ❌ Ingrese un número válido.")
                except ValueError:
                    logger.error(f"Error procesando valores múltiples: '{original_str}' - OMITIENDO REGISTRO")
                    return "TEXT_SKIP"
            
            # Variable para rastrear si ya tiene símbolo %
            has_percent_symbol = '%' in str_value
            
            # Si contiene %, extraer solo la parte numérica
            if has_percent_symbol:
                str_value = str_value.replace('%', '').strip()
                if original_str != str_value:
                    logger.info(f"Removiendo símbolo %: '{original_str}' → '{str_value}'")
            
            # Ahora convertir a número
            num_value = float(str_value)
            original_value = num_value
            
            # CLAVE: Si NO tiene símbolo %, es probable que venga de Excel como decimal
            # donde 1 = 100%, 0.5 = 50%, etc. - MULTIPLICAR POR 100
            if not has_percent_symbol and num_value <= 10:  # Solo para valores pequeños que probablemente son decimales
                num_value = num_value * 100
                self.porcentajes_formateados += 1
                logger.info(f"Conversión decimal de Excel: {original_value} → {num_value}% (multiplicado por 100)")
            
            # NUEVA REGLA: Si supera 100, limitar a 100 (no 999)
            if num_value > 100:
                self.porcentajes_formateados += 1
                logger.info(f"Porcentaje {num_value} limitado a 100 (era > 100%)")
                return "100"
            
            # Si es un número entero
            if num_value == int(num_value):
                return str(int(num_value))
            
            # Para decimales, redondear para que quepa en 3 caracteres
            if num_value < 10:
                # Formato: X.Y (3 chars)
                formatted = f"{num_value:.1f}"
                if len(formatted) > 3:
                    formatted = str(int(round(num_value)))
                if original_value != float(formatted):
                    self.porcentajes_formateados += 1
                    logger.info(f"Porcentaje {original_value} redondeado a {formatted}")
                return formatted
            else:
                # Para números >= 10, solo entero para evitar superar 3 chars
                formatted = str(int(round(num_value)))
                if original_value != float(formatted):
                    self.porcentajes_formateados += 1
                    logger.info(f"Porcentaje {original_value} redondeado a {formatted}")
                return formatted
                
        except (ValueError, TypeError):
            # Si aún no se puede convertir, es probable que sea texto
            clean_str = str(value).strip().replace('%', '')
            if not clean_str.replace('.', '').replace('-', '').isdigit():
                logger.warning(f"Valor no numérico detectado: '{value}' - OMITIENDO REGISTRO")
                return "TEXT_SKIP"
            
            # Intentar como número una última vez
            try:
                num_val = float(clean_str)
                # Aplicar conversión decimal si es necesario
                if num_val <= 10:
                    num_val = num_val * 100
                if num_val > 100:
                    return "100"
                return str(int(num_val)) if num_val == int(num_val) else f"{num_val:.1f}"[:3]
            except:
                if len(clean_str) <= 3:
                    return clean_str
                else:
                    # Truncar a 3 caracteres
                    self.porcentajes_formateados += 1
                    logger.info(f"Porcentaje '{value}' truncado a '{clean_str[:3]}'")
                    return clean_str[:3]

    def process_excel_file(self, file_path):
        """Procesar el archivo Excel"""
        try:
            # Leer la pestaña DETALLE_ORTO_CARTO
            df = pd.read_excel(file_path, sheet_name='DETALLE_ORTO_CARTO')
            logger.info(f"Excel leído exitosamente. Filas: {len(df)}")
            
            total_insertados = 0
            total_omitidos = 0
            
            # Obtener cod_detalle inicial
            current_cod_detalle = self.get_next_cod_detalle()
            if current_cod_detalle is None:
                raise Exception("No se pudo obtener el siguiente cod_detalle")
            
            # Procesar cada fila del Excel
            for index, row in df.iterrows():
                logger.info(f"Procesando fila {index + 1}")
                
                # Obtener datos básicos de la fila
                codigo_municipio = int(row['CÓDIGO MUNICIPIO']) if pd.notna(row['CÓDIGO MUNICIPIO']) else None
                area_total = row['AREA TOTAL MPIO (ha)'] if pd.notna(row['AREA TOTAL MPIO (ha)']) else None
                
                if not codigo_municipio:
                    logger.warning(f"Fila {index + 1}: Código de municipio vacío, omitiendo")
                    continue
                
                # Procesar cada grupo
                for group_name, group_config in self.groups.items():
                    estado = row.get(group_config['estado_col'])
                    
                    # Validar estado
                    if not self.validate_estado(estado):
                        logger.info(f"Fila {index + 1}, Grupo {group_name}: Estado '{estado}' no válido, omitiendo")
                        total_omitidos += 1
                        continue
                    
                    # Buscar cod_clasificacion
                    cod_clasificacion = self.find_cod_clasificacion(codigo_municipio, group_config['tipo_nombre'])
                    if not cod_clasificacion:
                        # Agregar a registros fallidos
                        failed_record = self.create_failed_record(
                            row, group_name, group_config, 
                            f"No se encontró cod_clasificacion para {group_config['tipo_nombre']}"
                        )
                        self.failed_records.append(failed_record)
                        continue
                    
                    # VERIFICAR SI YA EXISTE EL REGISTRO PARA EVITAR DUPLICADOS
                    if self.record_already_exists(cod_clasificacion, codigo_municipio, group_config['zona'], group_config['formato_tipo']):
                        logger.info(f"Fila {index + 1}, Grupo {group_name}: Registro ya existe, omitiendo para evitar duplicado")
                        total_omitidos += 1
                        self.registros_duplicados_omitidos += 1
                        continue
                    
                    # Preparar datos del registro
                    record_data = self.prepare_record_data(row, group_config, current_cod_detalle, 
                                                         codigo_municipio, area_total, cod_clasificacion)
                    
                    # Si prepare_record_data devuelve None (por valores de texto), omitir registro
                    if record_data is None:
                        logger.info(f"Fila {index + 1}, Grupo {group_name}: Registro omitido por valor de texto en cubrimiento")
                        total_omitidos += 1
                        self.registros_omitidos_por_texto += 1
                        continue
                    
                    # Insertar registro
                    success, sql_query = self.insert_record(record_data)
                    if success:
                        total_insertados += 1
                        current_cod_detalle += 1
                    else:
                        # Agregar a registros fallidos
                        failed_record = self.create_failed_record(
                            row, group_name, group_config, 
                            "Error en inserción SQL", sql_query
                        )
                        self.failed_records.append(failed_record)
            
            return total_insertados, total_omitidos
            
        except Exception as e:
            logger.error(f"Error procesando archivo Excel: {e}")
            messagebox.showerror("Error", f"Error procesando archivo: {e}")
            return 0, 0

    def prepare_record_data(self, row, group_config, cod_detalle, cod_municipio, area_total, cod_clasificacion):
        """Preparar datos del registro para inserción"""
        # Obtener valores específicos del grupo
        escala = row.get(group_config['escala_col'])
        vigencia = row.get(group_config['vigencia_col'])
        porcentaje_cubrimiento_raw = row.get(group_config['cubrimiento_col'])
        
        # Crear info para mostrar en consola si hay valores múltiples
        municipio_info = f"{cod_municipio} - {row.get('NOMBRE MUNICIPIO', 'N/A')}"
        grupo_info = f"{group_config['zona']} - {group_config['tipo_nombre']}"
        
        # Formatear porcentaje de cubrimiento
        porcentaje_cubrimiento = self.format_porcentaje_cubrimiento(
            porcentaje_cubrimiento_raw, municipio_info, grupo_info
        )
        
        # Si devuelve señal especial para omitir, devolver None
        if porcentaje_cubrimiento == "TEXT_SKIP":
            return None
        
        # Cubrimiento especial solo para AREA_ORTO_R_(ha)
        cubrimiento = None
        if group_config['area_especial']:
            cubrimiento = row.get(group_config['area_especial'])
        
        return {
            'cod_detalle': cod_detalle,
            'escala': escala if pd.notna(escala) else None,
            'estado': row.get(group_config['estado_col']),
            'cubrimiento': cubrimiento if pd.notna(cubrimiento) else None,
            'fecha_entrega': None,
            'fecha_disposicion': datetime.now().date(),
            'area': area_total if pd.notna(area_total) else None,
            'cod_entidad': 'IGAC',
            'observacion': None,
            'vigencia': vigencia if pd.notna(vigencia) else None,
            'formato_tipo': group_config['formato_tipo'],
            'cod_usuario': 1053840329,
            'cod_clasificacion': cod_clasificacion,
            'zona': group_config['zona'],
            'cod_centro_poblado': None,
            'ruta_archivo': None,
            'porcentaje_cubrimiento': porcentaje_cubrimiento
        }

    def insert_record(self, record_data):
        """Insertar registro en la base de datos"""
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
            logger.info(f"Registro insertado exitosamente: cod_detalle {record_data['cod_detalle']}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error insertando registro: {e}")
            self.conn.rollback()
            # Crear la sentencia SQL con valores para el reporte
            sql_with_values = self.format_sql_with_values(insert_query, record_data)
            return False, sql_with_values

    def format_sql_with_values(self, query, data):
        """Formatear consulta SQL con valores para el reporte de errores"""
        try:
            # Reemplazar los placeholders con valores reales
            formatted_query = query
            for key, value in data.items():
                placeholder = f"%({key})s"
                if value is None:
                    replacement = "NULL"
                elif isinstance(value, str):
                    replacement = f"'{value}'"
                elif isinstance(value, datetime):
                    replacement = f"'{value.strftime('%Y-%m-%d')}'"
                elif hasattr(value, 'strftime'):  # Para objetos date
                    replacement = f"'{value.strftime('%Y-%m-%d')}'"
                else:
                    replacement = str(value)
                formatted_query = formatted_query.replace(placeholder, replacement)
            
            return formatted_query.strip()
        except Exception as e:
            return f"Error formateando SQL: {e}"

    def create_failed_record(self, original_row, group_name, group_config, error_message, sql_query=None):
        """Crear registro de fallo para el Excel de errores"""
        
        # Columnas base que siempre se incluyen
        base_columns = ['CÓDIGO MUNICIPIO', 'AREA TOTAL MPIO (ha)']
        
        # Columnas específicas del subgrupo
        group_columns = [
            group_config['estado_col'],
            group_config['escala_col'], 
            group_config['vigencia_col'],
            group_config['cubrimiento_col']
        ]
        
        # Si tiene área especial, agregarla
        if group_config['area_especial']:
            group_columns.append(group_config['area_especial'])
        
        # Crear registro con solo las columnas relevantes
        failed_record = {}
        
        # Agregar columnas base
        for col in base_columns:
            failed_record[col] = original_row.get(col, '')
        
        # Agregar columnas del subgrupo
        for col in group_columns:
            failed_record[col] = original_row.get(col, '')
        
        # Información adicional del error
        failed_record['SUBGRUPO'] = group_name
        failed_record['ZONA'] = group_config['zona']
        failed_record['TIPO_INSUMO'] = group_config['tipo_nombre']
        failed_record['FORMATO_ESPERADO'] = group_config['formato_tipo']
        failed_record['ERROR_MESSAGE'] = error_message
        failed_record['TIMESTAMP'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if sql_query:
            failed_record['SQL_QUERY'] = sql_query
            
        return failed_record

    def save_failed_records(self, original_file_path):
        """Guardar registros fallidos en Excel con pestañas por subgrupo"""
        if not self.failed_records:
            return None
        
        try:
            # Generar nombre del archivo de errores
            base_name = os.path.splitext(os.path.basename(original_file_path))[0]
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            failed_file_name = f"{base_name}_ERRORES_{timestamp}.xlsx"
            failed_file_path = os.path.join(os.path.dirname(original_file_path), failed_file_name)
            
            # Agrupar registros fallidos por subgrupo
            grouped_failures = {}
            for record in self.failed_records:
                subgroup = record['SUBGRUPO']
                if subgroup not in grouped_failures:
                    grouped_failures[subgroup] = []
                grouped_failures[subgroup].append(record)
            
            logger.info(f"Creando archivo con {len(grouped_failures)} pestañas de subgrupos")
            
            # Crear Excel con múltiples pestañas
            with pd.ExcelWriter(failed_file_path, engine='openpyxl') as writer:
                
                # 1. CREAR PESTAÑA DE RESUMEN
                summary_data = []
                total_errors = 0
                for subgroup, records in grouped_failures.items():
                    count = len(records)
                    total_errors += count
                    summary_data.append({
                        'SUBGRUPO': subgroup,
                        'CANTIDAD_ERRORES': count,
                        'PORCENTAJE': f"{(count/len(self.failed_records)*100):.1f}%"
                    })
                
                summary_data.append({
                    'SUBGRUPO': '** TOTAL **',
                    'CANTIDAD_ERRORES': total_errors,
                    'PORCENTAJE': '100.0%'
                })
                
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='RESUMEN', index=False)
                logger.info("Pestaña RESUMEN creada")
                
                # 2. CREAR UNA PESTAÑA PARA CADA SUBGRUPO
                for subgroup, records in grouped_failures.items():
                    logger.info(f"Creando pestaña para subgrupo: {subgroup} con {len(records)} registros")
                    
                    # Convertir a DataFrame
                    df_subgroup = pd.DataFrame(records)
                    
                    # Definir orden de columnas específico para cada subgrupo
                    base_columns = ['CÓDIGO MUNICIPIO', 'AREA TOTAL MPIO (ha)']
                    
                    # Columnas específicas según el subgrupo
                    if subgroup == 'ORTO_R':
                        specific_columns = ['ESTADO_ORTO_R', 'ESCALA_ORTO_R', 'VIGENCIA_ORTO_R', 
                                          'AREA_ORTO_R_(ha)', 'CUBRIMIENTO_ORTO_R']
                    elif subgroup == 'CARTO_R':
                        specific_columns = ['ESTADO_CARTO_R', 'ESCALA_CARTO_R', 'VIGENCIA_CARTO_R', 
                                          'CUBRIMIENTO_CARTO_R']
                    elif subgroup == 'MDT_R':
                        specific_columns = ['ESTADO_MDT_R', 'ESCALA_MDT_R', 'VIGENCIA_MDT_R', 
                                          'CUBRIMIENTO_MDT_R']
                    elif subgroup == 'ORTO_CAB':
                        specific_columns = ['ESTADO_ORTO_CAB', 'ESCALA_ORTO_CAB', 'VIGENCIA_ORTO_CAB', 
                                          'CUBRIMIENTO_ORTO_CAB']
                    elif subgroup == 'CARTO_CAB':
                        specific_columns = ['ESTADO_CARTO_CAB', 'ESCALA_CARTO_CAB', 'VIGENCIA_CARTO_CAB', 
                                          'CUBRIMIENTO_CARTO_CAB']
                    elif subgroup == 'MDT_CAB':
                        specific_columns = ['ESTADO_MDT_CAB', 'ESCALA_MDT_CAB', 'VIGENCIA_MDT_CAB', 
                                          'CUBRIMIENTO_MDT_CAB']
                    else:
                        specific_columns = []
                    
                    # Columnas de información del error
                    error_columns = ['ZONA', 'TIPO_INSUMO', 'FORMATO_ESPERADO', 
                                   'ERROR_MESSAGE', 'SQL_QUERY', 'TIMESTAMP']
                    
                    # Construir orden final de columnas
                    final_columns = base_columns + specific_columns + error_columns
                    
                    # Filtrar solo columnas que existen en el DataFrame
                    available_columns = [col for col in final_columns if col in df_subgroup.columns]
                    
                    # Crear DataFrame ordenado
                    df_ordered = df_subgroup[available_columns].copy()
                    
                    # Nombre de pestaña (máximo 31 caracteres para Excel)
                    sheet_name = f"ERROR_{subgroup}"[:31]
                    
                    # Guardar en pestaña
                    df_ordered.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    # Ajustar ancho de columnas
                    worksheet = writer.sheets[sheet_name]
                    for idx, column in enumerate(df_ordered.columns):
                        max_length = max(
                            len(str(column)),  # Longitud del header
                            max([len(str(val)) for val in df_ordered.iloc[:, idx]] + [0])
                        )
                        # Limitar ancho máximo
                        adjusted_width = min(max_length + 3, 80)
                        column_letter = worksheet.cell(row=1, column=idx+1).column_letter
                        worksheet.column_dimensions[column_letter].width = adjusted_width
                    
                    logger.info(f"Pestaña '{sheet_name}' creada con {len(df_ordered)} registros")
            
            logger.info(f"Archivo de errores guardado: {failed_file_path}")
            logger.info(f"Total de pestañas creadas: {len(grouped_failures) + 1} (incluyendo RESUMEN)")
            return failed_file_path
            
        except Exception as e:
            logger.error(f"Error guardando registros fallidos: {e}")
            return None

    def select_file(self):
        """Interfaz para seleccionar archivo"""
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana principal
        
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Excel files", "*.xlsx *.xlsm *.xls"), ("All files", "*.*")]
        )
        
        root.destroy()
        return file_path

    def run(self):
        """Ejecutar el procesamiento completo"""
        logger.info("Iniciando procesamiento de Excel DETALLE_ORTO_CARTO")
        
        # Conectar a BD
        if not self.connect_db():
            return
        
        try:
            # Seleccionar archivo
            file_path = self.select_file()
            if not file_path:
                logger.info("No se seleccionó ningún archivo")
                return
            
            logger.info(f"Archivo seleccionado: {file_path}")
            
            # Procesar archivo
            insertados, omitidos = self.process_excel_file(file_path)
            
            # Guardar registros fallidos si existen
            failed_file = None
            pestañas_info = ""
            if self.failed_records:
                failed_file = self.save_failed_records(file_path)
                
                # Contar pestañas por subgrupo
                subgroups_count = {}
                for record in self.failed_records:
                    subgroup = record['SUBGRUPO']
                    subgroups_count[subgroup] = subgroups_count.get(subgroup, 0) + 1
                
                pestañas_info = f"\n📋 PESTAÑAS CREADAS:"
                pestañas_info += f"\n   • RESUMEN: Vista general"
                for subgroup, count in subgroups_count.items():
                    pestañas_info += f"\n   • ERROR_{subgroup}: {count} registros"
            
            # Mostrar resumen
            message = f"""
PROCESAMIENTO COMPLETADO

✅ Registros insertados: {insertados}
⚠️ Registros omitidos: {omitidos}
   └ Por estado no válido: {omitidos - self.registros_omitidos_por_texto - self.registros_duplicados_omitidos}
   └ Por valores de texto: {self.registros_omitidos_por_texto}
   └ Por duplicados detectados: {self.registros_duplicados_omitidos}
❌ Registros fallidos: {len(self.failed_records)}
🔧 Porcentajes formateados: {self.porcentajes_formateados}

{f'📁 Archivo de errores: {os.path.basename(failed_file)}' if failed_file else '✨ No hay registros fallidos'}
{pestañas_info}
            """
            
            messagebox.showinfo("Resumen", message.strip())
            
            # Log detallado en consola
            logger.info(f"PROCESAMIENTO COMPLETADO:")
            logger.info(f"  - Registros insertados: {insertados}")
            logger.info(f"  - Registros omitidos: {omitidos}")
            logger.info(f"    * Por estado no válido: {omitidos - self.registros_omitidos_por_texto - self.registros_duplicados_omitidos}")
            logger.info(f"    * Por valores de texto: {self.registros_omitidos_por_texto}")
            logger.info(f"    * Por duplicados detectados: {self.registros_duplicados_omitidos}")
            logger.info(f"  - Registros fallidos: {len(self.failed_records)}")
            logger.info(f"  - Porcentajes formateados: {self.porcentajes_formateados}")
            if failed_file:
                logger.info(f"  - Archivo de errores: {failed_file}")
                # Log de pestañas creadas
                subgroups_count = {}
                for record in self.failed_records:
                    subgroup = record['SUBGRUPO']
                    subgroups_count[subgroup] = subgroups_count.get(subgroup, 0) + 1
                logger.info(f"  - Pestañas de errores creadas:")
                logger.info(f"    * RESUMEN")
                for subgroup, count in subgroups_count.items():
                    logger.info(f"    * ERROR_{subgroup}: {count} registros")
            
        except Exception as e:
            logger.error(f"Error en procesamiento principal: {e}")
            messagebox.showerror("Error", f"Error en procesamiento: {e}")
        
        finally:
            if self.conn:
                self.conn.close()
                logger.info("Conexión a BD cerrada")

if __name__ == "__main__":
    processor = ExcelProcessor()
    processor.run()