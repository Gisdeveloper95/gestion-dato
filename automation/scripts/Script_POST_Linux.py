#!/usr/bin/env python3
"""
Script_POST_Linux.py - VERSION LINUX NATIVA
============================================

CAMBIOS VS VERSION WINDOWS:
- ELIMINADO: PowerShell completo
- NUEVO: Funciones nativas Linux (pwd, os.stat)
- NUEVO: Rutas simples /mnt/path
- OPTIMIZADO: 10x mas rapido

FUNCIONALIDADES:
1. Exploracion recursiva de directorios POST
2. Tabla disposicion_post = directorios
3. Tabla archivos_post = archivos
4. Sistema de propietarios nativos
5. Verificacion de existencia
6. Sistema de notificaciones
7. Constraint unico en rutas
8. Sistema de logs exportable
"""

import os
import pwd
import psycopg2
from datetime import datetime
import traceback
import argparse
import json
import multiprocessing
import threading
from pathlib import Path
import time
import logging
import logging.handlers
from propietario_windows import obtener_propietario_windows
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (ubicado en el directorio padre)
ENV_PATH = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(ENV_PATH)

# CONFIGURACION GLOBAL - Desde .env (SIN FALLBACK - debe fallar si no está configurado)
def _get_required_env(var_name):
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"Variable de entorno requerida no definida: {var_name}")
    return value

DB_CONFIG = {
    'host': _get_required_env('DB_HOST'),
    'database': _get_required_env('DB_NAME'),
    'user': _get_required_env('DB_USER'),
    'password': _get_required_env('DB_PASSWORD'),
    'port': os.getenv('DB_PORT', '5432')
}

BATCH_SIZE_DB = 1000
NUM_PROCESSES = min(multiprocessing.cpu_count(), 8)
MODO_SIMULACION = False
MODO_VERBOSE = True
MODO_ELIMINAR = True

DB_LOCK = threading.Lock()
contador_lock = threading.Lock()

cambios_disposiciones = {'creadas': 0, 'actualizadas': 0, 'eliminadas': 0}
cambios_archivos = {'creados': 0, 'actualizados': 0, 'eliminados': 0}
cambios_por_municipio = {}

logger = None
LOGS_HABILITADOS = False
DIRECTORIO_LOGS = "/var/log/script_post"
NIVEL_LOG = logging.INFO

EXTENSIONES_IGNORAR = [
    '.log', '.aux', '.lock', '.lck', '.xml', '.ovr',
    '.idx', '.ind', '.tmp', '.temp', '.pyr', '.rdx', '.dng',
    '.bak', '.dwl', '.dwl2', '.cpg', '.qix', '.fix', '.dbf', '.tfw', '.prj', '.shx',
    '.gdbtable', '.gdbtablx', '.gdbindexes', '.freelist', '.sbn', '.sbx',
    '.horizon', '.spx', '.atx', 'Thumbs.db'
]

EXTENSIONES_ARCHIVO_UNICO = ['.gdb', '.eslpk', '.gz']

def es_extension_ignorada(nombre_archivo):
    """Verifica si la extension debe ser ignorada"""
    nombre_lower = nombre_archivo.lower()

    archivos_ignorar = [
        'thumbs.db', 'desktop.ini', '.ds_store', 'folder.jpg'
    ]

    if nombre_lower in archivos_ignorar:
        return True

    if nombre_lower.startswith('.') and nombre_lower != '.gdb':
        return True

    for ext in EXTENSIONES_IGNORAR:
        if nombre_lower.endswith(ext):
            return True

    return False

def obtener_propietario_linux(ruta):
    """Obtiene el propietario Windows REAL del archivo usando getcifsacl + mapeo de SIDs"""
    try:
        return obtener_propietario_windows(ruta)
    except:
        return 'Sistema'

def obtener_fechas_linux(ruta):
    try:
        stat_info = os.stat(ruta)
        return datetime.fromtimestamp(stat_info.st_mtime)
    except:
        return datetime.now()

def obtener_peso_linux(ruta):
    try:
        if os.path.isdir(ruta):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(ruta):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except:
                        continue
            return total_size
        else:
            return os.path.getsize(ruta)
    except:
        return 0

def configurar_sistema_logs(exportar_logs=False, directorio_logs="/var/log/script_post", nivel_detalle="INFO"):
    global logger, LOGS_HABILITADOS, DIRECTORIO_LOGS
    
    LOGS_HABILITADOS = exportar_logs
    DIRECTORIO_LOGS = directorio_logs
    
    if not exportar_logs:
        print("Sistema de logs: DESHABILITADO")
        return
    
    try:
        os.makedirs(directorio_logs, exist_ok=True)
        
        logger = logging.getLogger('ScriptPostLinux')
        logger.setLevel(logging.INFO)
        
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"script_post_linux_{timestamp}.log"
        ruta_archivo = os.path.join(directorio_logs, nombre_archivo)
        
        file_handler = logging.handlers.RotatingFileHandler(
            ruta_archivo, maxBytes=50*1024*1024, backupCount=5, encoding='utf-8'
        )
        
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        print(f"Sistema de logs HABILITADO: {ruta_archivo}")
        logger.info("SCRIPT_POST_LINUX.py - INICIO")
        
    except Exception as e:
        print(f"Error configurando logs: {e}")

def log(mensaje, nivel=1):
    if nivel <= 1 or MODO_VERBOSE:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {mensaje}")
    
    if LOGS_HABILITADOS and logger:
        try:
            logger.info(mensaje)
        except:
            pass

def incrementar_contador(tipo_cambio, cod_municipio=None, categoria='archivos'):
    with contador_lock:
        if categoria == 'archivos':
            cambios_archivos[tipo_cambio] += 1
        elif categoria == 'disposiciones':
            cambios_disposiciones[tipo_cambio] += 1
        
        if cod_municipio:
            if cod_municipio not in cambios_por_municipio:
                cambios_por_municipio[cod_municipio] = {
                    'disposiciones': {'creadas': 0, 'actualizadas': 0, 'eliminadas': 0},
                    'archivos': {'creados': 0, 'actualizados': 0, 'eliminados': 0}
                }
            cambios_por_municipio[cod_municipio][categoria][tipo_cambio] += 1

def verificar_tablas_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name IN ('disposicion_post', 'archivos_post')
        """)
        
        tablas = [row[0] for row in cursor.fetchall()]
        
        if 'disposicion_post' not in tablas:
            log("Creando tabla disposicion_post")
            cursor.execute("""
                CREATE TABLE disposicion_post (
                    id_disposicion SERIAL PRIMARY KEY,
                    cod_municipio INTEGER,
                    ruta_acceso TEXT UNIQUE,
                    nombre_directorio VARCHAR(255),
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP,
                    fecha_actualizacion TIMESTAMP
                )
            """)
        
        if 'archivos_post' not in tablas:
            log("Creando tabla archivos_post")
            cursor.execute("""
                CREATE TABLE archivos_post (
                    id_archivo SERIAL PRIMARY KEY,
                    id_disposicion INTEGER,
                    nombre_archivo VARCHAR(500),
                    ruta_completa TEXT UNIQUE,
                    extension VARCHAR(50),
                    peso_bytes BIGINT,
                    usuario_windows VARCHAR(100),
                    fecha_modificacion TIMESTAMP,
                    activo BOOLEAN DEFAULT TRUE
                )
            """)
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        log(f"Error verificando tablas: {e}")
        return False

def obtener_rutas_post(municipio_especifico=None):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        if municipio_especifico:
            cursor.execute("""
                SELECT id, cod_municipio, path
                FROM path_dir_post
                WHERE cod_municipio = %s
                ORDER BY cod_municipio
            """, (municipio_especifico,))
        else:
            cursor.execute("""
                SELECT id, cod_municipio, path
                FROM path_dir_post
                ORDER BY cod_municipio
            """)

        rutas = cursor.fetchall()
        log(f"Rutas POST encontradas: {len(rutas)}")
        return rutas

    except Exception as e:
        log(f"Error obteniendo rutas: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

def crear_notificacion_post(conn, tipo_entidad, id_entidad, accion, descripcion, datos_contexto):
    """Crear notificacion para POST"""
    if MODO_SIMULACION:
        return True

    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO notificaciones_post(
                tipo_entidad, id_entidad, accion, descripcion,
                datos_contexto, fecha_cambio, usuario_windows, leido
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            tipo_entidad, id_entidad, accion, descripcion,
            json.dumps(datos_contexto, ensure_ascii=False),
            datetime.now(), 'Sistema', False
        ))

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        log(f"Error creando notificacion: {e}", 3)
        return False

# CLASE SCANNER POST
class ScannerArchivosPost:
    """Scanner optimizado para POST Linux - explora directorios recursivamente"""

    def __init__(self):
        self.archivos_procesados = set()

    def explorar_directorio_completo(self, ruta_base, cod_municipio):
        """Explora TODA la estructura de directorios recursivamente"""
        estructura = {
            'directorios': {},
            'archivos_por_directorio': {}
        }

        try:
            log(f"Explorando estructura POST en: {ruta_base}", 1)

            if not os.path.exists(ruta_base):
                log(f"ADVERTENCIA: Ruta no existe: {ruta_base}", 1)
                return estructura

            for root, dirs, files in os.walk(ruta_base):
                # Manejo de directorios especiales como .gdb
                for dirname in dirs[:]:
                    if any(dirname.lower().endswith(ext) for ext in EXTENSIONES_ARCHIVO_UNICO):
                        ruta_dir = os.path.join(root, dirname)
                        estructura['archivos_por_directorio'].setdefault(root, []).append(ruta_dir)
                        dirs.remove(dirname)  # No entrar recursivamente

                # Registrar directorio actual
                if root not in estructura['directorios']:
                    estructura['directorios'][root] = {
                        'nombre': os.path.basename(root),
                        'ruta_completa': root,
                        'archivos_directos': []
                    }

                # Registrar archivos del directorio actual
                for filename in files:
                    if es_extension_ignorada(filename):
                        continue

                    ruta_archivo = os.path.join(root, filename)
                    estructura['directorios'][root]['archivos_directos'].append(ruta_archivo)

            log(f"Exploración completada: {len(estructura['directorios'])} directorios", 1)
            return estructura

        except Exception as e:
            log(f"Error explorando directorio: {e}", 1)
            return estructura

    def obtener_crear_disposicion(self, conn, ruta_dir, cod_municipio):
        """Obtiene o crea una disposición (directorio) en BD"""
        try:
            cursor = conn.cursor()

            # Buscar por ruta_acceso
            cursor.execute("""
                SELECT id_disposicion FROM disposicion_post
                WHERE ruta_acceso = %s
            """, (ruta_dir,))

            resultado = cursor.fetchone()

            if resultado:
                return resultado[0]

            # Crear nueva disposición
            if MODO_SIMULACION:
                log(f"[SIMULACION] Crearia disposicion: {ruta_dir}", 3)
                return -1

            nombre_dir = os.path.basename(ruta_dir)

            cursor.execute("""
                INSERT INTO disposicion_post (
                    cod_municipio, ruta_acceso, nombre_directorio,
                    activo, fecha_creacion, fecha_actualizacion
                ) VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id_disposicion
            """, (cod_municipio, ruta_dir, nombre_dir, True, datetime.now(), datetime.now()))

            id_disposicion = cursor.fetchone()[0]
            conn.commit()

            incrementar_contador('creadas', cod_municipio, 'disposiciones')
            log(f"Nueva disposicion creada: {nombre_dir}", 2)

            datos_contexto = {
                'municipio': cod_municipio,
                'ruta': ruta_dir,
                'nombre': nombre_dir
            }

            crear_notificacion_post(conn, 'disposicion', id_disposicion, 'crear',
                                   f"Nueva disposicion: {nombre_dir}", datos_contexto)

            return id_disposicion

        except Exception as e:
            conn.rollback()
            log(f"Error obteniendo/creando disposicion: {e}", 1)
            return None

    def procesar_archivos_post_batch(self, conn, archivos, id_disposicion, cod_municipio):
        """Procesa archivos de una disposición en batch"""
        if not archivos:
            return

        try:
            cursor = conn.cursor()

            log(f"Procesando {len(archivos)} archivos para disposicion {id_disposicion}", 2)

            for archivo_path in archivos:
                try:
                    nombre_archivo = os.path.basename(archivo_path)
                    extension = os.path.splitext(nombre_archivo)[1]
                    propietario = obtener_propietario_linux(archivo_path)
                    fecha_mod = obtener_fechas_linux(archivo_path)
                    peso_bytes = obtener_peso_linux(archivo_path)

                    # Verificar si existe por ruta_completa
                    cursor.execute("""
                        SELECT id_archivo, usuario_windows FROM archivos_post
                        WHERE ruta_completa = %s
                        LIMIT 1
                    """, (archivo_path,))

                    archivo_existente = cursor.fetchone()

                    if archivo_existente:
                        id_existente, usuario_existente = archivo_existente

                        # Actualizar si cambió propietario
                        if usuario_existente != propietario and propietario != 'Sistema':
                            if not MODO_SIMULACION:
                                cursor.execute("""
                                    UPDATE archivos_post
                                    SET usuario_windows = %s, fecha_modificacion = %s, peso_bytes = %s,
                                        fecha_disposicion = %s, peso_memoria = %s
                                    WHERE id_archivo = %s
                                """, (propietario, fecha_mod, peso_bytes,
                                      fecha_mod.date() if fecha_mod else None, str(peso_bytes) if peso_bytes else None,
                                      id_existente))

                                conn.commit()
                                incrementar_contador('actualizados', cod_municipio, 'archivos')
                                log(f"Archivo actualizado: {nombre_archivo}", 3)
                    else:
                        # Insertar nuevo archivo
                        if not MODO_SIMULACION:
                            cursor.execute("""
                                INSERT INTO archivos_post (
                                    id_disposicion, nombre_archivo, ruta_completa,
                                    extension, peso_bytes, usuario_windows,
                                    fecha_modificacion, activo,
                                    fecha_disposicion, peso_memoria
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                RETURNING id_archivo
                            """, (id_disposicion, nombre_archivo, archivo_path,
                                  extension, peso_bytes, propietario, fecha_mod, True,
                                  fecha_mod.date() if fecha_mod else None, str(peso_bytes) if peso_bytes else None))

                            id_nuevo = cursor.fetchone()[0]
                            conn.commit()

                            incrementar_contador('creados', cod_municipio, 'archivos')
                            log(f"Archivo nuevo insertado: {nombre_archivo}", 3)

                except Exception as e:
                    log(f"Error procesando archivo {archivo_path}: {e}", 3)
                    conn.rollback()
                    continue

        except Exception as e:
            conn.rollback()
            log(f"Error en procesar_archivos_post_batch: {e}", 1)

    def eliminar_archivos_no_existentes(self, conn, id_disposicion, rutas_fisicas, cod_municipio):
        """Elimina archivos de BD que ya no existen fisicamente"""
        if not MODO_ELIMINAR:
            return

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id_archivo, nombre_archivo, ruta_completa
                FROM archivos_post
                WHERE id_disposicion = %s AND activo = TRUE
            """, (id_disposicion,))

            archivos_bd = cursor.fetchall()

            if not archivos_bd:
                return

            archivos_eliminados = 0

            for id_archivo, nombre, path_bd in archivos_bd:
                existe = os.path.exists(path_bd) or Path(path_bd).exists()

                if not existe:
                    if not MODO_SIMULACION:
                        cursor.execute("""
                            UPDATE archivos_post
                            SET activo = FALSE
                            WHERE id_archivo = %s
                        """, (id_archivo,))

                        conn.commit()
                        incrementar_contador('eliminados', cod_municipio, 'archivos')
                        archivos_eliminados += 1
                        log(f"Archivo marcado inactivo: {nombre}", 3)

            if archivos_eliminados > 0:
                log(f"Total archivos eliminados: {archivos_eliminados}", 2)

        except Exception as e:
            conn.rollback()
            log(f"Error eliminando archivos: {e}", 1)

    def procesar_municipio_post_completo(self, ruta_base, cod_municipio):
        """Procesa un municipio POST completo"""
        try:
            log(f"\n{'='*60}", 1)
            log(f"PROCESANDO MUNICIPIO POST: {cod_municipio}", 1)
            log(f"Ruta: {ruta_base}", 1)
            log(f"{'='*60}\n", 1)

            inicio_municipio = time.time()

            # 1. Explorar estructura completa
            estructura = self.explorar_directorio_completo(ruta_base, cod_municipio)

            if not estructura['directorios']:
                log(f"No se encontraron directorios en {ruta_base}", 1)
                return

            # 2. Conectar a BD
            conn = psycopg2.connect(**DB_CONFIG)

            # 3. Procesar cada directorio
            for ruta_dir, info_dir in estructura['directorios'].items():
                # Crear/obtener disposición
                id_disposicion = self.obtener_crear_disposicion(conn, ruta_dir, cod_municipio)

                if not id_disposicion:
                    continue

                # Procesar archivos del directorio
                archivos_directos = info_dir.get('archivos_directos', [])

                if archivos_directos:
                    self.procesar_archivos_post_batch(
                        conn, archivos_directos, id_disposicion, cod_municipio
                    )

                # Eliminar archivos que ya no existen
                rutas_fisicas = set(archivos_directos)
                self.eliminar_archivos_no_existentes(
                    conn, id_disposicion, rutas_fisicas, cod_municipio
                )

            conn.close()

            tiempo_municipio = time.time() - inicio_municipio
            log(f"\nMunicipio POST {cod_municipio} completado en {tiempo_municipio:.2f}s", 1)

        except Exception as e:
            log(f"Error procesando municipio POST {cod_municipio}: {e}", 1)
            traceback.print_exc()

def main():
    global MODO_VERBOSE, MODO_SIMULACION
    
    parser = argparse.ArgumentParser(description='Scanner POST Linux')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--simulacion', action='store_true')
    parser.add_argument('--municipio', type=int)
    parser.add_argument('--exportar-logs', action='store_true')
    parser.add_argument('--directorio-logs', default='/var/log/script_post')
    
    args = parser.parse_args()
    
    MODO_VERBOSE = args.verbose or True
    MODO_SIMULACION = args.simulacion
    
    if args.exportar_logs:
        configurar_sistema_logs(True, args.directorio_logs)
    
    print("="*60)
    print("SCRIPT_POST_LINUX.py - VERSION NATIVA")
    print("="*60)
    
    inicio_total = time.time()
    
    try:
        log("Verificando base de datos...")
        if not verificar_tablas_db():
            print("Error verificando tablas")
            return
        
        log("Obteniendo rutas POST...")
        rutas = obtener_rutas_post(args.municipio)
        
        if not rutas:
            print("No hay rutas configuradas")
            return
        
        print(f"\nProcesando {len(rutas)} municipios POST")

        # Crear instancia del scanner POST
        scanner = ScannerArchivosPost()

        # Procesar cada municipio
        for id_path, cod_municipio, path_municipio in rutas:
            try:
                scanner.procesar_municipio_post_completo(path_municipio, cod_municipio)
            except Exception as e:
                log(f"Error procesando municipio {cod_municipio}: {e}", 1)
                continue

        tiempo_total = time.time() - inicio_total

        print("\n" + "="*60)
        print("SCRIPT_POST_LINUX.py COMPLETADO")
        print("="*60)
        print(f"\nESTADISTICAS FINALES:")
        print(f"  Disposiciones creadas: {cambios_disposiciones['creadas']}")
        print(f"  Archivos creados: {cambios_archivos['creados']}")
        print(f"  Archivos actualizados: {cambios_archivos['actualizados']}")
        print(f"  Archivos eliminados: {cambios_archivos['eliminados']}")
        print(f"  Municipios procesados: {len(rutas)}")
        print(f"\nTiempo total: {tiempo_total:.2f} segundos")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\nInterrumpido por usuario")
    except Exception as e:
        print(f"\nError critico: {str(e)}")
        traceback.print_exc()
    finally:
        if args.exportar_logs and logger:
            logger.info("SCRIPT_POST_LINUX.py - FIN")

if __name__ == "__main__":
    main()
