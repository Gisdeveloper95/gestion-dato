#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para actualizar la tabla municipios con datos de área desde archivo Excel
Actualiza el campo 'area' basado en cod_municipio como clave primaria
"""

import os
import sys
import pandas as pd
import psycopg2
import math
import logging
import tkinter as tk
from tkinter import filedialog, messagebox

# Configuración de logging con encoding UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('update_municipios.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Parámetros de conexión a la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'database': 'gestion_dato_db',
    'user': 'postgres',
    'password': '1234',
    'port': '5432'
}

def convertir_numero_colombiano(valor):
    """
    Convierte números en formato colombiano (punto para miles, coma para decimales) a float
    Ejemplos: "27.368,70" -> 27368.70, "2,7369" -> 2.7369, "1.234.567,89" -> 1234567.89
    """
    if pd.isna(valor) or valor == '':
        return 0.0
    
    # Si ya es un número, devolverlo
    if isinstance(valor, (int, float)):
        return float(valor)
    
    # Convertir a string y limpiar espacios
    valor_str = str(valor).strip()
    
    # Si no contiene coma ni punto, es un entero simple
    if ',' not in valor_str and '.' not in valor_str:
        try:
            return float(valor_str)
        except ValueError:
            logger.warning(f"No se pudo convertir: {valor_str}")
            return 0.0
    
    # FORMATO COLOMBIANO: Si contiene coma, es separador decimal
    if ',' in valor_str:
        try:
            # Separar parte entera y decimal por la última coma
            partes = valor_str.rsplit(',', 1)
            parte_entera = partes[0]
            parte_decimal = partes[1] if len(partes) > 1 else '0'
            
            # Limpiar puntos de la parte entera (separadores de miles)
            parte_entera = parte_entera.replace('.', '')
            
            # Reconstruir como número con punto decimal
            numero_str = f"{parte_entera}.{parte_decimal}"
            return float(numero_str)
        except (ValueError, IndexError):
            logger.warning(f"Error convirtiendo número colombiano: {valor_str}")
            return 0.0
    
    # Solo tiene punto - puede ser separador de miles o decimal
    if '.' in valor_str:
        try:
            # Si tiene más de 3 dígitos después del punto, es decimal estilo US
            partes = valor_str.split('.')
            if len(partes) == 2 and len(partes[1]) <= 3:
                # Probablemente es separador de miles
                return float(valor_str.replace('.', ''))
            else:
                # Es decimal estilo US
                return float(valor_str)
        except ValueError:
            logger.warning(f"Error convirtiendo número con punto: {valor_str}")
            return 0.0
    
    # Fallback
    try:
        return float(valor_str)
    except ValueError:
        logger.warning(f"No se pudo convertir el valor: {valor_str}")
        return 0.0

def redondear_area(valor, decimales=2):
    """
    Redondea el área a un número específico de decimales
    decimales=None para no redondear
    """
    if decimales is None:
        return float(valor)  # Sin redondeo
    
    return round(float(valor), decimales)

def seleccionar_archivo_excel():
    """
    Abre el navegador de archivos de Windows para seleccionar el Excel
    """
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal
    root.attributes('-topmost', True)  # Traer al frente
    
    # Configurar diálogo de archivo
    archivo_excel = filedialog.askopenfilename(
        title="Seleccionar archivo Excel con datos de municipios",
        filetypes=[
            ("Archivos Excel", "*.xlsx *.xlsm *.xls"),
            ("Excel con macros", "*.xlsm"),
            ("Excel sin macros", "*.xlsx"),
            ("Excel 2003", "*.xls"),
            ("Todos los archivos", "*.*")
        ],
        initialdir=os.getcwd()
    )
    
    root.destroy()
    
    if not archivo_excel:
        logger.info("No se seleccionó ningún archivo. Proceso cancelado.")
        return None
    
    logger.info(f"Archivo seleccionado: {archivo_excel}")
    return archivo_excel

def leer_datos_excel(archivo_path):
    """
    Lee los datos del archivo Excel de la hoja DETALLE_ORTO_CARTO
    Retorna un diccionario con cod_municipio como clave y area como valor
    """
    logger.info(f"Leyendo archivo Excel: {archivo_path}")
    
    try:
        # Leer la hoja específica - NO especificar dtype para AREA para que lea como viene
        df = pd.read_excel(
            archivo_path, 
            sheet_name='DETALLE_ORTO_CARTO',
            usecols=['CÓDIGO MUNICIPIO', 'AREA TOTAL MPIO (ha)'],
            dtype={'CÓDIGO MUNICIPIO': str}  # Solo código como string
        )
        
        # Limpiar datos nulos
        df = df.dropna(subset=['CÓDIGO MUNICIPIO', 'AREA TOTAL MPIO (ha)'])
        
        # Crear diccionario de datos procesados
        municipios_data = {}
        errores_conversion = []
        
        for index, row in df.iterrows():
            try:
                # Procesar código de municipio (convertir a entero, eliminando 0 iniciales)
                cod_municipio_str = str(row['CÓDIGO MUNICIPIO']).strip()
                cod_municipio = int(cod_municipio_str)  # Esto automáticamente elimina 0s iniciales
                
                # Procesar área usando la función de conversión colombiana
                area_raw = row['AREA TOTAL MPIO (ha)']
                area_original = convertir_numero_colombiano(area_raw)
                area_redondeada = redondear_area(area_original, decimales=2)  # 2 decimales por defecto
                
                municipios_data[cod_municipio] = {
                    'area_original': area_original,
                    'area_redondeada': area_redondeada,
                    'cod_original': cod_municipio_str,
                    'area_raw': str(area_raw)  # Para debugging
                }
                
            except Exception as e:
                error_msg = f"Error procesando fila {index + 2}: Código={row.get('CÓDIGO MUNICIPIO', 'N/A')}, Área={row.get('AREA TOTAL MPIO (ha)', 'N/A')} - {str(e)}"
                errores_conversion.append(error_msg)
                logger.warning(error_msg)
        
        logger.info(f"Se leyeron {len(municipios_data)} municipios del Excel")
        
        if errores_conversion:
            logger.warning(f"Se encontraron {len(errores_conversion)} errores de conversión:")
            for error in errores_conversion[:5]:  # Mostrar solo los primeros 5
                logger.warning(f"  {error}")
            if len(errores_conversion) > 5:
                logger.warning(f"  ... y {len(errores_conversion) - 5} errores más")
        
        # Mostrar algunos ejemplos de conversión exitosa
        logger.info("Ejemplos de conversión exitosa:")
        for i, (cod, datos) in enumerate(list(municipios_data.items())[:5]):
            logger.info(f"  {datos['cod_original']} -> {cod} | {datos['area_raw']} -> {datos['area_original']} -> {datos['area_redondeada']} ha")
        
        return municipios_data
        
    except Exception as e:
        logger.error(f"Error al leer el archivo Excel: {str(e)}")
        raise

def obtener_municipios_bd():
    """
    Obtiene los códigos de municipios existentes en la base de datos
    """
    logger.info("Consultando municipios existentes en la base de datos")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SELECT cod_municipio, area FROM municipios ORDER BY cod_municipio")
        municipios_bd = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.close()
        conn.close()
        
        logger.info(f"Se encontraron {len(municipios_bd)} municipios en la base de datos")
        return municipios_bd
        
    except Exception as e:
        logger.error(f"Error al consultar la base de datos: {str(e)}")
        raise

def actualizar_municipios(municipios_excel, municipios_bd):
    """
    Actualiza los municipios en la base de datos con los datos del Excel
    """
    logger.info("Iniciando actualización de municipios")
    
    # Contadores para el reporte
    actualizados = 0
    sin_cambios = 0
    no_encontrados = []
    errores = []
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        for cod_municipio, datos_excel in municipios_excel.items():
            try:
                if cod_municipio in municipios_bd:
                    # USAR FUNCIÓN DE CONVERSIÓN TAMBIÉN PARA DATOS DE LA BD
                    area_bd_raw = municipios_bd[cod_municipio]
                    area_bd_actual = convertir_numero_colombiano(area_bd_raw) if area_bd_raw else 0
                    area_nueva = datos_excel['area_redondeada']
                    
                    # Verificar si hay cambio significativo (diferencia mayor a 0.001)
                    if abs(area_bd_actual - area_nueva) > 0.001:
                        cursor.execute(
                            "UPDATE municipios SET area = %s WHERE cod_municipio = %s",
                            (area_nueva, cod_municipio)
                        )
                        actualizados += 1
                        logger.info(
                            f"Actualizado municipio {cod_municipio}: "
                            f"{area_bd_actual} -> {area_nueva} ha"
                        )
                    else:
                        sin_cambios += 1
                else:
                    no_encontrados.append({
                        'cod_municipio': cod_municipio,
                        'cod_original': datos_excel['cod_original'],
                        'area': datos_excel['area_redondeada']
                    })
                    
            except Exception as e:
                errores.append({
                    'cod_municipio': cod_municipio,
                    'error': str(e)
                })
                logger.error(f"Error procesando municipio {cod_municipio}: {str(e)}")
        
        # Confirmar cambios
        conn.commit()
        cursor.close()
        conn.close()
        
        # Generar reporte
        generar_reporte(actualizados, sin_cambios, no_encontrados, errores, municipios_bd)
        
    except Exception as e:
        logger.error(f"Error durante la actualización: {str(e)}")
        raise

def generar_reporte(actualizados, sin_cambios, no_encontrados, errores, municipios_bd):
    """
    Genera un reporte detallado de la actualización
    """
    logger.info("=" * 60)
    logger.info("REPORTE DE ACTUALIZACIÓN DE MUNICIPIOS")
    logger.info("=" * 60)
    logger.info(f"Municipios actualizados: {actualizados}")
    logger.info(f"Municipios sin cambios: {sin_cambios}")
    logger.info(f"Municipios no encontrados en BD: {len(no_encontrados)}")
    logger.info(f"Errores durante actualización: {len(errores)}")
    logger.info(f"Total municipios en BD: {len(municipios_bd)}")
    
    if no_encontrados:
        logger.info("\nMunicipios del Excel NO encontrados en la BD:")
        for mun in no_encontrados[:10]:  # Mostrar solo los primeros 10
            logger.info(f"  - Código: {mun['cod_municipio']} (original: {mun['cod_original']}), Área: {mun['area']} ha")
        if len(no_encontrados) > 10:
            logger.info(f"  ... y {len(no_encontrados) - 10} más")
    
    if errores:
        logger.info("\nErrores encontrados:")
        for error in errores:
            logger.info(f"  - Código: {error['cod_municipio']}, Error: {error['error']}")
    
    logger.info("=" * 60)

def main():
    """
    Función principal del script
    """
    print("ACTUALIZADOR DE ÁREAS DE MUNICIPIOS - VERSIÓN CORREGIDA")
    print("=" * 60)
    print("OPCIONES DE REDONDEO:")
    print("1. Sin redondeo (valores exactos)")
    print("2. 2 decimales (ej: 47555.10)")
    print("3. 1 decimal (ej: 47555.1)")
    print("4. Sin decimales (ej: 47555)")
    print("")
    
    # Seleccionar tipo de redondeo
    while True:
        try:
            opcion = input("Selecciona opción de redondeo (1-4): ").strip()
            if opcion == "1":
                decimales = None
                break
            elif opcion == "2":
                decimales = 2
                break
            elif opcion == "3":
                decimales = 1
                break
            elif opcion == "4":
                decimales = 0
                break
            else:
                print("Opción inválida. Selecciona 1, 2, 3 o 4")
        except:
            print("Opción inválida. Selecciona 1, 2, 3 o 4")
    
    archivo_excel = seleccionar_archivo_excel()
    if not archivo_excel:
        sys.exit(0)
    
    try:
        # Pasar decimales como parámetro global (simplificando)
        global DECIMALES_REDONDEO
        DECIMALES_REDONDEO = decimales
        
        municipios_excel = leer_datos_excel(archivo_excel)
        municipios_bd = obtener_municipios_bd()
        
        logger.info(f"\nTipo de redondeo seleccionado: {'Sin redondeo' if decimales is None else f'{decimales} decimales'}")
        logger.info("\nEjemplos de códigos procesados:")
        for i, (cod, datos) in enumerate(list(municipios_excel.items())[:5]):
            logger.info(f"  {datos['cod_original']} -> {cod} | Área: {datos['area_original']} -> {datos['area_redondeada']} ha")
        
        print(f"\n¿Proceder con la actualización de {len(municipios_excel)} municipios? (s/N): ", end="")
        respuesta = input()
        if respuesta.lower() != 's':
            logger.info("Actualización cancelada por el usuario")
            return
        
        actualizar_municipios(municipios_excel, municipios_bd)
        logger.info("Proceso completado exitosamente")
        
    except Exception as e:
        logger.error(f"Error durante la ejecución: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()