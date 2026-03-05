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
        'base_path': r"/mnt/repositorio/2510SP/H_Informacion_Consulta/Sub_Proy/01_actualiz_catas"
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
        # Patrón para rutas Linux
        pattern = r'/mnt/repositorio/2510SP/H_Informacion_Consulta/Sub_Proy/01_actualiz_catas/(\d+)/(\d+)'
        
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

def procesar_archivo_rutas():
    """Procesa el archivo de rutas de ejemplo"""
    try:
        file_path = 'paste.txt'
        if not os.path.exists(file_path):
            print(f"No se encuentra el archivo: {file_path}")
            return []
        
        with open(file_path, 'r') as f:
            rutas = f.readlines()
        
        results = []
        # Patrón para rutas Linux
        pattern = r'/mnt/repositorio/2510SP/H_Informacion_Consulta/Sub_Proy/01_actualiz_catas/(\d+)/(\d+)'
        
        for ruta in rutas:
            ruta = ruta.strip()
            if ruta and '_insu' in ruta:
                match = re.search(pattern, ruta)
                if match:
                    depto_codigo = match.group(1)
                    mpio_codigo = match.group(2)
                    codigo_municipio = int(f"{depto_codigo}{mpio_codigo}")
                    
                    results.append({
                        'codigo_mpio': codigo_municipio,
                        'ruta_completa': ruta
                    })
        
        print(f"Se procesaron {len(results)} rutas desde el archivo de ejemplo")
        return results
    except Exception as e:
        print(f"Error al procesar archivo: {str(e)}")
        return []

def buscar_rutas_en_sistema(base_path):
    """Busca las rutas de municipios en el sistema de archivos"""
    results = []
    
    # Verificar si la ruta base existe
    if not os.path.exists(base_path):
        print(f"La ruta base {base_path} no existe")
        return []
    
    # Recorrer directorios con manejo de errores
    try:
        depto_dirs = os.listdir(base_path)
    except Exception as e:
        print(f"Error al listar directorios: {str(e)}")
        return []
    
    for depto_dir in depto_dirs:
        depto_path = os.path.join(base_path, depto_dir)
        
        # Verificar si es un directorio y tiene nombre numérico
        if not (os.path.isdir(depto_path) and depto_dir.isdigit()):
            continue
            
        try:
            # Listar municipios dentro del departamento
            mpio_dirs = os.listdir(depto_path)
        except Exception as e:
            print(f"Error al listar municipios en departamento {depto_dir}: {str(e)}")
            continue
        
        # Procesar cada municipio
        for mpio_dir in mpio_dirs:
            mpio_path = os.path.join(depto_path, mpio_dir)
            
            if not (os.path.isdir(mpio_path) and mpio_dir.isdigit()):
                continue
                
            try:
                project_dirs = os.listdir(mpio_path)
            except Exception as e:
                print(f"Error en municipio {depto_dir}/{mpio_dir}: {str(e)}")
                continue
            
            # Buscar directorios de proyectos (PGN, FCP, etc)
            for project_dir in project_dirs:
                project_path = os.path.join(mpio_path, project_dir)
                
                if not os.path.isdir(project_path):
                    continue
                
                # Buscar directorio 01_preo
                preo_path = os.path.join(project_path, "01_preo")
                if not os.path.isdir(preo_path):
                    continue
                
                try:
                    preo_contents = os.listdir(preo_path)
                except Exception as e:
                    continue
                
                # CAMBIO MEJORADO: Buscar directorios que CONTENGAN "_insu" (case-insensitive)
                for insu_dir in preo_contents:
                    # Cambio principal aquí - búsqueda case-insensitive
                    if "_insu" not in insu_dir.lower():
                        continue
                        
                    insu_path = os.path.join(preo_path, insu_dir)
                    if not os.path.isdir(insu_path):
                        continue
                        
                    # Construir la ruta completa en formato Windows
                    full_path = os.path.join(base_path, depto_dir, mpio_dir, project_dir, "01_preo", insu_dir)
                    windows_path = full_path.replace('/', '\\')
                    
                    # Convertir código a entero
                    codigo_municipio = int(f"{depto_dir}{mpio_dir}")
                    
                    results.append({
                        'codigo_mpio': codigo_municipio,
                        'ruta_completa': windows_path,
                        'nombre_directorio': insu_dir  # Agregar nombre del directorio para debug
                    })
    
    print(f"Se encontraron {len(results)} rutas en el sistema de archivos")
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
        # Patrón para rutas Linux
        pattern = r'/mnt/repositorio/2510SP/H_Informacion_Consulta/Sub_Proy/01_actualiz_catas/(\d+)/(\d+)'
        
        for ruta in rutas:
            ruta = ruta.strip()
            # CAMBIO MEJORADO: Buscar que contenga "_insu" (case-insensitive)
            if ruta and '_insu' in ruta.lower():  # Búsqueda case-insensitive
                match = re.search(pattern, ruta)
                if match:
                    depto_codigo = match.group(1)
                    mpio_codigo = match.group(2)
                    codigo_municipio = int(f"{depto_codigo}{mpio_codigo}")
                    
                    # Extraer el nombre del directorio para debug
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

def analizar_patrones_insu(data):
    """Nueva función para analizar los diferentes patrones de nombres _insu* (case-insensitive)"""
    patrones = {}
    
    for item in data:
        nombre = item.get('nombre_directorio', '')
        if '_insu' in nombre.lower():  # Búsqueda case-insensitive
            # Extraer el patrón después de _insu (manteniendo el caso original)
            nombre_lower = nombre.lower()
            insu_index = nombre_lower.find('_insu')
            # Obtener el sufijo desde el nombre original (para preservar mayúsculas/minúsculas)
            sufijo_original = nombre[insu_index:]
            
            if sufijo_original in patrones:
                patrones[sufijo_original] += 1
            else:
                patrones[sufijo_original] = 1
    
    if patrones:
        print("\n=== Análisis de Patrones de Directorios ===")
        for patron, count in sorted(patrones.items(), key=lambda x: x[1], reverse=True):
            print(f"  {patron}: {count} directorios")
    
    return patrones

def generar_excel(data):
    """Genera un archivo Excel con los datos de municipios y rutas"""
    if not CONFIG['excel']['generate']:
        print("Generación de Excel desactivada en la configuración")
        return None
    
    try:
        # Crear DataFrame
        df = pd.DataFrame(data)
        
        # Crear nombre de archivo con fecha actual
        current_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{CONFIG['excel']['filename_prefix']}_{current_date}.xlsx"
        
        # Guardar el DataFrame en un archivo Excel
        df.to_excel(output_file, index=False)
        
        print(f"Archivo Excel generado: {output_file}")
        return output_file
    except Exception as e:
        print(f"Error al generar Excel: {str(e)}")
        return None

def buscar_rutas_en_sistema(base_path):
    """Busca las rutas de municipios en el sistema de archivos"""
    results = []
    
    # Verificar si la ruta base existe
    if not os.path.exists(base_path):
        print(f"La ruta base {base_path} no existe")
        return []
    
    # Recorrer directorios con manejo de errores
    try:
        depto_dirs = os.listdir(base_path)
    except Exception as e:
        print(f"Error al listar directorios: {str(e)}")
        return []
    
    for depto_dir in depto_dirs:
        depto_path = os.path.join(base_path, depto_dir)
        
        # Verificar si es un directorio y tiene nombre numérico
        if not (os.path.isdir(depto_path) and depto_dir.isdigit()):
            continue
            
        try:
            # Listar municipios dentro del departamento
            mpio_dirs = os.listdir(depto_path)
        except Exception as e:
            print(f"Error al listar municipios en departamento {depto_dir}: {str(e)}")
            continue
        
        # Procesar cada municipio
        for mpio_dir in mpio_dirs:
            mpio_path = os.path.join(depto_path, mpio_dir)
            
            if not (os.path.isdir(mpio_path) and mpio_dir.isdigit()):
                continue
                
            try:
                project_dirs = os.listdir(mpio_path)
            except Exception as e:
                print(f"Error en municipio {depto_dir}/{mpio_dir}: {str(e)}")
                continue
            
            # Buscar directorios de proyectos (PGN, FCP, etc)
            for project_dir in project_dirs:
                project_path = os.path.join(mpio_path, project_dir)
                
                if not os.path.isdir(project_path):
                    continue
                
                # Buscar directorio 01_preo
                preo_path = os.path.join(project_path, "01_preo")
                if not os.path.isdir(preo_path):
                    continue
                
                try:
                    preo_contents = os.listdir(preo_path)
                except Exception as e:
                    continue
                
                # CAMBIO MEJORADO: Buscar directorios que CONTENGAN "_insu" (no solo que terminen)
                for insu_dir in preo_contents:
                    # Cambio principal aquí
                    if "_insu" not in insu_dir:
                        continue
                        
                    insu_path = os.path.join(preo_path, insu_dir)
                    if not os.path.isdir(insu_path):
                        continue
                        
                    # Construir la ruta completa en formato Windows
                    full_path = os.path.join(base_path, depto_dir, mpio_dir, project_dir, "01_preo", insu_dir)
                    windows_path = full_path.replace('/', '\\')
                    
                    # Convertir código a entero
                    codigo_municipio = int(f"{depto_dir}{mpio_dir}")
                    
                    results.append({
                        'codigo_mpio': codigo_municipio,
                        'ruta_completa': windows_path,
                        'nombre_directorio': insu_dir  # Agregar nombre del directorio para debug
                    })
    
    print(f"Se encontraron {len(results)} rutas en el sistema de archivos")
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
        # Patrón para rutas Linux
        pattern = r'/mnt/repositorio/2510SP/H_Informacion_Consulta/Sub_Proy/01_actualiz_catas/(\d+)/(\d+)'
        
        for ruta in rutas:
            ruta = ruta.strip()
            # CAMBIO MEJORADO: Buscar que contenga "_insu" en lugar de solo "_insu"
            if ruta and '_insu' in ruta:  # Esto ya era correcto en el código original
                match = re.search(pattern, ruta)
                if match:
                    depto_codigo = match.group(1)
                    mpio_codigo = match.group(2)
                    codigo_municipio = int(f"{depto_codigo}{mpio_codigo}")
                    
                    # Extraer el nombre del directorio para debug
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

def analizar_patrones_insu(data):
    """Nueva función para analizar los diferentes patrones de nombres _insu*"""
    patrones = {}
    
    for item in data:
        nombre = item.get('nombre_directorio', '')
        if '_insu' in nombre:
            # Extraer el patrón después de _insu
            insu_index = nombre.find('_insu')
            sufijo = nombre[insu_index:]  # _insu, _insum, _insumo, etc.
            
            if sufijo in patrones:
                patrones[sufijo] += 1
            else:
                patrones[sufijo] = 1
    
    if patrones:
        print("\n=== Análisis de Patrones de Directorios ===")
        for patron, count in sorted(patrones.items(), key=lambda x: x[1], reverse=True):
            print(f"  {patron}: {count} directorios")
    
    return patrones

def guardar_en_path_dir_post(data):
    """Guarda los datos en la tabla path_dir_post de PostgreSQL"""
    try:
        conn = obtener_conexion_db()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        cursor.execute("TRUNCATE TABLE path_dir_post RESTART IDENTITY;")
        print(f"Tabla path_dir_post limpiada para evitar duplicados")
        
        sql = "INSERT INTO path_dir_post (cod_municipio, path) VALUES (%s, %s);"
        
        municipios_validos = set()
        cursor.execute("SELECT cod_municipio FROM municipios;")
        for row in cursor.fetchall():
            municipios_validos.add(row[0])
        
        registros_validos = []
        registros_invalidos = []
        
        for item in data:
            if item['codigo_mpio'] in municipios_validos:
                registros_validos.append(item)
            else:
                registros_invalidos.append(item)
        
        if registros_invalidos:
            print(f"ADVERTENCIA: {len(registros_invalidos)} registros con códigos inválidos")
            for i, item in enumerate(registros_invalidos[:5]):
                print(f"  - Código {item['codigo_mpio']}: {item['ruta_completa'][:50]}...")
        
        inserted_count = 0
        for item in registros_validos:
            try:
                cursor.execute(sql, (item['codigo_mpio'], item['ruta_completa']))
                inserted_count += 1
            except Exception as e:
                print(f"Error insertando registro para municipio {item['codigo_mpio']}: {str(e)}")
        
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM path_dir_post;")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"{inserted_count} registros insertados en path_dir_post")
        print(f"Total de registros en path_dir_post: {count}")
        return True
    except Exception as e:
        print(f"Error al guardar en base de datos (post): {str(e)}")
        import traceback
        traceback.print_exc()
        return False
def guardar_en_path_dir_pre(data):
    """Guarda los datos en la tabla path_dir_pre de PostgreSQL"""
    try:
        conn = obtener_conexion_db()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Limpiar tabla para evitar duplicados
        cursor.execute("TRUNCATE TABLE path_dir_pre RESTART IDENTITY;")
        print(f"Tabla path_dir_pre limpiada para evitar duplicados")
        
        # Preparar consulta SQL para inserción
        sql = "INSERT INTO path_dir_pre (cod_municipio, path) VALUES (%s, %s);"
        
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
        cursor.execute("SELECT COUNT(*) FROM path_dir_pre;")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"Datos guardados en PostgreSQL. {inserted_count} registros insertados en la tabla path_dir_pre")
        print(f"Total de registros en la tabla: {count}")
        return True
    except Exception as e:
        print(f"Error al guardar en base de datos: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

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
    print("=== Procesamiento de Rutas de Municipios ===")
    
    try:
        # 1. Intentar obtener rutas desde el sistema de archivos
        base_path = CONFIG['paths']['base_path']
        print(f"Buscando rutas en: {base_path}")
        
        try:
            paths_data = buscar_rutas_en_sistema(base_path)
        except Exception as e:
            print(f"Error accediendo al sistema de archivos: {str(e)}")
            paths_data = []
        
        # 2. Si no hay rutas en el sistema, usar archivo de ejemplo
        if not paths_data:
            print("No se encontraron rutas en el sistema. Usando archivo de ejemplo...")
            paths_data = procesar_archivo_rutas()
        
        # 3. Obtener códigos de municipios (de PostgreSQL o del archivo)
        municipios_codes = obtener_codigos_municipios()
        
        # 4. Filtrar rutas que corresponden a municipios en la base de datos
        if municipios_codes:
            filtered_data = [item for item in paths_data if item['codigo_mpio'] in municipios_codes]
            print(f"Filtrado a {len(filtered_data)} rutas de municipios en la base de datos")
            
            # Si el filtro eliminó todas las rutas, usar datos originales
            if not filtered_data and paths_data:
                print("El filtrado eliminó todas las rutas. Usando datos originales...")
                filtered_data = paths_data
        else:
            filtered_data = paths_data
        
        # 5. Analizar duplicados en los datos
        analizar_duplicados(filtered_data)
        
        # 6. Generar el Excel (si está habilitado en la configuración)
        if filtered_data and CONFIG['excel']['generate']:
            excel_file = generar_excel(filtered_data)
        else:
            excel_file = "Excel no generado"
            
        # 7. Guardar en la base de datos PostgreSQL
        print("\nGuardando datos en la tabla path_dir_pre...")
        db_result = guardar_en_path_dir_pre(filtered_data)
        
        # 8. Informar resultado
        print("\nResumen del proceso:")
        if CONFIG['excel']['generate']:
            print(f"- Excel generado: {excel_file}")
        print(f"- Guardado en PostgreSQL: {'Exitoso' if db_result else 'Fallido'}")
        print(f"- Rutas procesadas: {len(filtered_data)}")
                # 9. Buscar rutas en 03_post
        print("\nBuscando rutas en 03_post...")
        try:
            post_paths = buscar_rutas_post_en_sistema(base_path)
        except Exception as e:
            print(f"Error buscando rutas post: {str(e)}")
            post_paths = []

        # 10. Filtrar rutas válidas
        if municipios_codes:
            filtered_post = [item for item in post_paths if item['codigo_mpio'] in municipios_codes]
            if not filtered_post and post_paths:
                print("El filtrado eliminó todas las rutas post. Usando datos originales...")
                filtered_post = post_paths
        else:
            filtered_post = post_paths

        # 11. Guardar en PostgreSQL
        print("Guardando rutas en path_dir_post...")
        db_result_post = guardar_en_path_dir_post(filtered_post)

        # 12. Mostrar resumen adicional
        print(f"- Guardado en path_dir_post: {'Exitoso' if db_result_post else 'Fallido'}")
        print(f"- Rutas post procesadas: {len(filtered_post)}")

    
    except Exception as e:
        print(f"Error en el proceso: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()