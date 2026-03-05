import os
import re
import pandas as pd
import psycopg2
import sys
from pathlib import Path
import datetime

# Configuración - Puedes ajustar estos parámetros según tu entorno
CONFIG = {
    # Parámetros de conexión a PostgreSQL
    'db': {
        'host': 'localhost',
        'database': 'gestion_dato_db',
        'user': 'postgres',
        'password': '1234',
        'port': '5432'
    },
    # Configuración de generación de Excel (puedes comentar esta sección si no deseas generar el Excel)
    'excel': {
        'generate': True,  # Cambiar a False para no generar el Excel
        'filename_prefix': 'municipios_rutas'
    },
    # Rutas principales
    'paths': {
        'base_path': r"\\repositorio\DirGesCat\2510SP\H_Informacion_Consulta\Sub_Proy\01_actualiz_catas"
    }
}

def obtener_conexion_db():
    """Obtiene una conexión a la base de datos PostgreSQL"""
    try:
        return psycopg2.connect(**CONFIG['db'])
    except Exception as e:
        print(f"Error al conectar con PostgreSQL: {str(e)}")
        return None

def obtener_codigos_municipios():
    """Obtiene los códigos de municipio desde la base de datos PostgreSQL"""
    try:
        conn = obtener_conexion_db()
        if not conn:
            return extraer_codigos_desde_archivo()
            
        cursor = conn.cursor()
        cursor.execute("SELECT cod_municipio FROM municipios")
        municipios = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        print(f"Se encontraron {len(municipios)} códigos de municipio en PostgreSQL")
        return municipios
    
    except Exception as e:
        print(f"Error al consultar municipios: {str(e)}")
        print("Extrayendo códigos del archivo de ejemplo...")
        return extraer_codigos_desde_archivo()

def extraer_codigos_desde_archivo():
    """Extrae códigos de municipio desde el archivo de rutas de ejemplo"""
    try:
        file_path = 'paste.txt'
        if not os.path.exists(file_path):
            print(f"No se encuentra el archivo: {file_path}")
            return []
        
        with open(file_path, 'r') as f:
            rutas = f.readlines()
        
        # Extraer códigos de municipio de las rutas
        codigos = set()
        pattern = r'\\\\repositorio\\\\DirGesCat\\\\2510SP\\\\H_Informacion_Consulta\\\\Sub_Proy\\\\01_actualiz_catas\\\\(\d+)\\\\(\d+)'
        
        for ruta in rutas:
            match = re.search(pattern, ruta)
            if match:
                depto_codigo = match.group(1)
                mpio_codigo = match.group(2)
                codigo_completo = int(f"{depto_codigo}{mpio_codigo}")
                codigos.add(codigo_completo)
        
        print(f"Se extrajeron {len(codigos)} códigos de municipio del archivo")
        return list(codigos)
    except Exception as e:
        print(f"Error al leer el archivo: {str(e)}")
        return []

def buscar_rutas_en_sistema(base_path):
    """Busca las rutas de municipios en el sistema de archivos para 01_preo"""
    results = []
    
    if not os.path.exists(base_path):
        print(f"La ruta base {base_path} no existe")
        return []
    
    try:
        depto_dirs = os.listdir(base_path)
    except Exception as e:
        print(f"Error al listar directorios: {str(e)}")
        return []
    
    for depto_dir in depto_dirs:
        depto_path = os.path.join(base_path, depto_dir)
        
        if not (os.path.isdir(depto_path) and depto_dir.isdigit()):
            continue
            
        try:
            mpio_dirs = os.listdir(depto_path)
        except Exception as e:
            print(f"Error al listar municipios en departamento {depto_dir}: {str(e)}")
            continue
        
        for mpio_dir in mpio_dirs:
            mpio_path = os.path.join(depto_path, mpio_dir)
            
            if not (os.path.isdir(mpio_path) and mpio_dir.isdigit()):
                continue
                
            try:
                project_dirs = os.listdir(mpio_path)
            except Exception as e:
                print(f"Error en municipio {depto_dir}/{mpio_dir}: {str(e)}")
                continue
            
            for project_dir in project_dirs:
                project_path = os.path.join(mpio_path, project_dir)
                
                if not os.path.isdir(project_path):
                    continue
                
                preo_path = os.path.join(project_path, "01_preo")
                if not os.path.isdir(preo_path):
                    continue
                
                try:
                    preo_contents = os.listdir(preo_path)
                except Exception as e:
                    continue
                
                for insu_dir in preo_contents:
                    if "_insu" not in insu_dir.lower():
                        continue
                        
                    insu_path = os.path.join(preo_path, insu_dir)
                    if not os.path.isdir(insu_path):
                        continue
                        
                    full_path = os.path.join(base_path, depto_dir, mpio_dir, project_dir, "01_preo", insu_dir)
                    windows_path = full_path.replace('/', '\\')
                    
                    codigo_municipio = int(f"{depto_dir}{mpio_dir}")
                    
                    results.append({
                        'codigo_mpio': codigo_municipio,
                        'ruta_completa': windows_path,
                        'nombre_directorio': insu_dir
                    })
    
    print(f"Se encontraron {len(results)} rutas en 01_preo")
    return results

def buscar_rutas_post_en_sistema(base_path):
    """Busca las rutas de municipios en el sistema de archivos en 03_post"""
    results = []
    
    if not os.path.exists(base_path):
        print(f"La ruta base {base_path} no existe")
        return []
    
    try:
        depto_dirs = os.listdir(base_path)
    except Exception as e:
        print(f"Error al listar directorios: {str(e)}")
        return []
    
    for depto_dir in depto_dirs:
        depto_path = os.path.join(base_path, depto_dir)
        if not (os.path.isdir(depto_path) and depto_dir.isdigit()):
            continue
            
        try:
            mpio_dirs = os.listdir(depto_path)
        except Exception as e:
            print(f"Error al listar municipios en departamento {depto_dir}: {str(e)}")
            continue
        
        for mpio_dir in mpio_dirs:
            mpio_path = os.path.join(depto_path, mpio_dir)
            if not (os.path.isdir(mpio_path) and mpio_dir.isdigit()):
                continue
                
            try:
                project_dirs = os.listdir(mpio_path)
            except Exception as e:
                print(f"Error en municipio {depto_dir}/{mpio_dir}: {str(e)}")
                continue
            
            for project_dir in project_dirs:
                project_path = os.path.join(mpio_path, project_dir)
                if not os.path.isdir(project_path):
                    continue
                
                post_path = os.path.join(project_path, "03_post")
                if not os.path.isdir(post_path):
                    continue
                
                codigo_municipio = int(f"{depto_dir}{mpio_dir}")
                windows_path = post_path.replace('/', '\\')
                
                results.append({
                    'codigo_mpio': codigo_municipio,
                    'ruta_completa': windows_path
                })
    
    print(f"Se encontraron {len(results)} rutas en 03_post")
    return results

def buscar_rutas_opera_en_sistema(base_path):
    """Busca las rutas de municipios en el sistema de archivos en 02_opera"""
    results = []
    
    if not os.path.exists(base_path):
        print(f"La ruta base {base_path} no existe")
        return []
    
    try:
        depto_dirs = os.listdir(base_path)
    except Exception as e:
        print(f"Error al listar directorios: {str(e)}")
        return []
    
    for depto_dir in depto_dirs:
        depto_path = os.path.join(base_path, depto_dir)
        if not (os.path.isdir(depto_path) and depto_dir.isdigit()):
            continue
            
        try:
            mpio_dirs = os.listdir(depto_path)
        except Exception as e:
            print(f"Error al listar municipios en departamento {depto_dir}: {str(e)}")
            continue
        
        for mpio_dir in mpio_dirs:
            mpio_path = os.path.join(depto_path, mpio_dir)
            if not (os.path.isdir(mpio_path) and mpio_dir.isdigit()):
                continue
                
            try:
                project_dirs = os.listdir(mpio_path)
            except Exception as e:
                print(f"Error en municipio {depto_dir}/{mpio_dir}: {str(e)}")
                continue
            
            for project_dir in project_dirs:
                project_path = os.path.join(mpio_path, project_dir)
                if not os.path.isdir(project_path):
                    continue
                
                opera_path = os.path.join(project_path, "02_opera")
                if not os.path.isdir(opera_path):
                    continue
                
                codigo_municipio = int(f"{depto_dir}{mpio_dir}")
                windows_path = opera_path.replace('/', '\\')
                
                results.append({
                    'codigo_mpio': codigo_municipio,
                    'ruta_completa': windows_path
                })
    
    print(f"Se encontraron {len(results)} rutas en 02_opera")
    return results

def buscar_rutas_transv_en_sistema(base_path):
    """Busca las rutas de municipios en el sistema de archivos en 04_transv"""
    results = []
    
    if not os.path.exists(base_path):
        print(f"La ruta base {base_path} no existe")
        return []
    
    try:
        depto_dirs = os.listdir(base_path)
    except Exception as e:
        print(f"Error al listar directorios: {str(e)}")
        return []
    
    for depto_dir in depto_dirs:
        depto_path = os.path.join(base_path, depto_dir)
        if not (os.path.isdir(depto_path) and depto_dir.isdigit()):
            continue
            
        try:
            mpio_dirs = os.listdir(depto_path)
        except Exception as e:
            print(f"Error al listar municipios en departamento {depto_dir}: {str(e)}")
            continue
        
        for mpio_dir in mpio_dirs:
            mpio_path = os.path.join(depto_path, mpio_dir)
            if not (os.path.isdir(mpio_path) and mpio_dir.isdigit()):
                continue
                
            try:
                project_dirs = os.listdir(mpio_path)
            except Exception as e:
                print(f"Error en municipio {depto_dir}/{mpio_dir}: {str(e)}")
                continue
            
            for project_dir in project_dirs:
                project_path = os.path.join(mpio_path, project_dir)
                if not os.path.isdir(project_path):
                    continue
                
                transv_path = os.path.join(project_path, "04_transv")
                if not os.path.isdir(transv_path):
                    continue
                
                codigo_municipio = int(f"{depto_dir}{mpio_dir}")
                windows_path = transv_path.replace('/', '\\')
                
                results.append({
                    'codigo_mpio': codigo_municipio,
                    'ruta_completa': windows_path
                })
    
    print(f"Se encontraron {len(results)} rutas en 04_transv")
    return results

def procesar_archivo_rutas():
    """Procesa el archivo de rutas de ejemplo - MEJORADO para capturar _insu*"""
    try:
        file_path = 'paste.txt'
        if not os.path.exists(file_path):
            print(f"No se encuentra el archivo: {file_path}")
            return []
        
        with open(file_path, 'r') as f:
            rutas = f.readlines()
        
        results = []
        pattern = r'\\\\repositorio\\\\DirGesCat\\\\2510SP\\\\H_Informacion_Consulta\\\\Sub_Proy\\\\01_actualiz_catas\\\\(\d+)\\\\(\d+)'
        
        for ruta in rutas:
            ruta = ruta.strip()
            if ruta and '_insu' in ruta:
                match = re.search(pattern, ruta)
                if match:
                    depto_codigo = match.group(1)
                    mpio_codigo = match.group(2)
                    codigo_municipio = int(f"{depto_codigo}{mpio_codigo}")
                    
                    nombre_dir = ruta.split('\\')[-1] if '\\' in ruta else ''
                    
                    results.append({
                        'codigo_mpio': codigo_municipio,
                        'ruta_completa': ruta,
                        'nombre_directorio': nombre_dir
                    })
        
        print(f"Se procesaron {len(results)} rutas desde el archivo de ejemplo")
        return results
    except Exception as e:
        print(f"Error al procesar archivo: {str(e)}")
        return []

def guardar_en_path_dir_pre(data):
    """Guarda los datos en la tabla path_dir_pre de PostgreSQL"""
    return _guardar_en_tabla(data, 'path_dir_pre', 'pre-operación')

def guardar_en_path_dir_post(data):
    """Guarda los datos en la tabla path_dir_post de PostgreSQL"""
    return _guardar_en_tabla(data, 'path_dir_post', 'post-operación')

def guardar_en_path_dir_opera(data):
    """Guarda los datos en la tabla path_dir_opera de PostgreSQL"""
    return _guardar_en_tabla(data, 'path_dir_opera', 'operación')

def guardar_en_path_dir_transv(data):
    """Guarda los datos en la tabla path_dir_transv de PostgreSQL"""
    return _guardar_en_tabla(data, 'path_dir_transv', 'transversal')

def _guardar_en_tabla(data, tabla_nombre, tipo_operacion):
    """Función genérica para guardar datos en cualquier tabla de paths"""
    try:
        conn = obtener_conexion_db()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Limpiar tabla para evitar duplicados
        cursor.execute(f"TRUNCATE TABLE {tabla_nombre} RESTART IDENTITY;")
        print(f"Tabla {tabla_nombre} limpiada para evitar duplicados")
        
        # Preparar consulta SQL para inserción
        sql = f"INSERT INTO {tabla_nombre} (cod_municipio, path) VALUES (%s, %s);"
        
        # Verificar que todos los códigos de municipio existen
        municipios_validos = set()
        cursor.execute("SELECT cod_municipio FROM municipios;")
        for row in cursor.fetchall():
            municipios_validos.add(row[0])
        
        # Filtrar registros inválidos
        registros_validos = []
        registros_invalidos = []
        
        for item in data:
            if item['codigo_mpio'] in municipios_validos:
                registros_validos.append(item)
            else:
                registros_invalidos.append(item)
        
        if registros_invalidos:
            print(f"ADVERTENCIA: Se encontraron {len(registros_invalidos)} registros con códigos de municipio que no existen en la base de datos")
            print("Primeros 5 registros inválidos:")
            for i, item in enumerate(registros_invalidos[:5]):
                print(f"  - Código {item['codigo_mpio']}: {item['ruta_completa'][:50]}...")
        
        # Insertar registros válidos
        inserted_count = 0
        for item in registros_validos:
            try:
                cursor.execute(sql, (item['codigo_mpio'], item['ruta_completa']))
                inserted_count += 1
            except Exception as e:
                print(f"Error insertando registro para municipio {item['codigo_mpio']}: {str(e)}")
        
        # Confirmar transacción
        conn.commit()
        
        # Obtener número de registros en la tabla
        cursor.execute(f"SELECT COUNT(*) FROM {tabla_nombre};")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"Datos de {tipo_operacion} guardados en PostgreSQL. {inserted_count} registros insertados en la tabla {tabla_nombre}")
        print(f"Total de registros en la tabla: {count}")
        return True
    except Exception as e:
        print(f"Error al guardar en base de datos ({tipo_operacion}): {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def generar_excel(data, suffix=""):
    """Genera un archivo Excel con los datos de municipios y rutas"""
    if not CONFIG['excel']['generate']:
        print("Generación de Excel desactivada en la configuración")
        return None
    
    try:
        # Crear DataFrame
        df = pd.DataFrame(data)
        
        # Crear nombre de archivo con fecha actual
        current_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{CONFIG['excel']['filename_prefix']}{suffix}_{current_date}.xlsx"
        
        # Guardar el DataFrame en un archivo Excel
        df.to_excel(output_file, index=False)
        
        print(f"Archivo Excel generado: {output_file}")
        return output_file
    except Exception as e:
        print(f"Error al generar Excel: {str(e)}")
        return None

def analizar_duplicados(data):
    """Analiza y muestra información sobre duplicados en los datos"""
    mpio_count = {}
    for item in data:
        mpio = item['codigo_mpio']
        if mpio in mpio_count:
            mpio_count[mpio] += 1
        else:
            mpio_count[mpio] = 1
    
    # Encontrar municipios con múltiples rutas
    multiple_paths = {mpio: count for mpio, count in mpio_count.items() if count > 1}
    
    if multiple_paths:
        print(f"\nDetectados {len(multiple_paths)} municipios con múltiples rutas:")
        for mpio, count in sorted(multiple_paths.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - Municipio {mpio}: {count} rutas")
    
    return multiple_paths

def main():
    print("=== Procesamiento de Rutas de Municipios - VERSIÓN COMPLETA ===")
    print("Procesando: 01_preo, 02_opera, 03_post, 04_transv")
    
    try:
        # 1. Obtener códigos de municipios
        municipios_codes = obtener_codigos_municipios()
        base_path = CONFIG['paths']['base_path']
        print(f"Buscando rutas en: {base_path}")
        
        # 2. PROCESAR 01_PREO (Pre-operación)
        print("\n" + "="*50)
        print("PROCESANDO 01_PREO (Pre-operación)")
        print("="*50)
        
        try:
            paths_pre = buscar_rutas_en_sistema(base_path)
        except Exception as e:
            print(f"Error accediendo al sistema de archivos (pre): {str(e)}")
            paths_pre = procesar_archivo_rutas()
        
        if municipios_codes:
            filtered_pre = [item for item in paths_pre if item['codigo_mpio'] in municipios_codes]
            if not filtered_pre and paths_pre:
                print("El filtrado eliminó todas las rutas pre. Usando datos originales...")
                filtered_pre = paths_pre
        else:
            filtered_pre = paths_pre
        
        analizar_duplicados(filtered_pre)
        db_result_pre = guardar_en_path_dir_pre(filtered_pre)
        
        # 3. PROCESAR 02_OPERA (Operación)
        print("\n" + "="*50)
        print("PROCESANDO 02_OPERA (Operación)")
        print("="*50)
        
        try:
            paths_opera = buscar_rutas_opera_en_sistema(base_path)
        except Exception as e:
            print(f"Error buscando rutas opera: {str(e)}")
            paths_opera = []

        if municipios_codes:
            filtered_opera = [item for item in paths_opera if item['codigo_mpio'] in municipios_codes]
            if not filtered_opera and paths_opera:
                print("El filtrado eliminó todas las rutas opera. Usando datos originales...")
                filtered_opera = paths_opera
        else:
            filtered_opera = paths_opera

        db_result_opera = guardar_en_path_dir_opera(filtered_opera)
        
        # 4. PROCESAR 03_POST (Post-operación)
        print("\n" + "="*50)
        print("PROCESANDO 03_POST (Post-operación)")
        print("="*50)
        
        try:
            paths_post = buscar_rutas_post_en_sistema(base_path)
        except Exception as e:
            print(f"Error buscando rutas post: {str(e)}")
            paths_post = []

        if municipios_codes:
            filtered_post = [item for item in paths_post if item['codigo_mpio'] in municipios_codes]
            if not filtered_post and paths_post:
                print("El filtrado eliminó todas las rutas post. Usando datos originales...")
                filtered_post = paths_post
        else:
            filtered_post = paths_post

        db_result_post = guardar_en_path_dir_post(filtered_post)
        
        # 5. PROCESAR 04_TRANSV (Transversal)
        print("\n" + "="*50)
        print("PROCESANDO 04_TRANSV (Transversal)")
        print("="*50)
        
        try:
            paths_transv = buscar_rutas_transv_en_sistema(base_path)
        except Exception as e:
            print(f"Error buscando rutas transv: {str(e)}")
            paths_transv = []

        if municipios_codes:
            filtered_transv = [item for item in paths_transv if item['codigo_mpio'] in municipios_codes]
            if not filtered_transv and paths_transv:
                print("El filtrado eliminó todas las rutas transv. Usando datos originales...")
                filtered_transv = paths_transv
        else:
            filtered_transv = paths_transv

        db_result_transv = guardar_en_path_dir_transv(filtered_transv)
        
        # 6. GENERAR EXCEL CONSOLIDADO (opcional)
        if CONFIG['excel']['generate']:
            # Crear un reporte consolidado
            all_data = []
            for item in filtered_pre:
                all_data.append({**item, 'tipo': '01_preo'})
            for item in filtered_opera:
                all_data.append({**item, 'tipo': '02_opera'})
            for item in filtered_post:
                all_data.append({**item, 'tipo': '03_post'})
            for item in filtered_transv:
                all_data.append({**item, 'tipo': '04_transv'})
            
            if all_data:
                excel_file = generar_excel(all_data, "_consolidado")
        
        # 7. RESUMEN FINAL
        print("\n" + "="*60)
        print("RESUMEN FINAL DEL PROCESAMIENTO")
        print("="*60)
        
        print(f"01_PREO (Pre-operación):")
        print(f"  - Rutas procesadas: {len(filtered_pre)}")
        print(f"  - Guardado en PostgreSQL: {'✓ Exitoso' if db_result_pre else '✗ Fallido'}")
        
        print(f"02_OPERA (Operación):")
        print(f"  - Rutas procesadas: {len(filtered_opera)}")
        print(f"  - Guardado en PostgreSQL: {'✓ Exitoso' if db_result_opera else '✗ Fallido'}")
        
        print(f"03_POST (Post-operación):")
        print(f"  - Rutas procesadas: {len(filtered_post)}")
        print(f"  - Guardado en PostgreSQL: {'✓ Exitoso' if db_result_post else '✗ Fallido'}")
        
        print(f"04_TRANSV (Transversal):")
        print(f"  - Rutas procesadas: {len(filtered_transv)}")
        print(f"  - Guardado en PostgreSQL: {'✓ Exitoso' if db_result_transv else '✗ Fallido'}")
        
        total_rutas = len(filtered_pre) + len(filtered_opera) + len(filtered_post) + len(filtered_transv)
        print(f"\nTOTAL DE RUTAS PROCESADAS: {total_rutas}")
        
        if CONFIG['excel']['generate']:
            print(f"Excel consolidado: {'✓ Generado' if 'excel_file' in locals() else '✗ No generado'}")
    
    except Exception as e:
        print(f"Error en el proceso: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()