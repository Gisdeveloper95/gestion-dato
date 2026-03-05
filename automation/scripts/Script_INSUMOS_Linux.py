#!/usr/bin/env python3
"""
Script_INSUMOS_Linux.py - VERSION LINUX NATIVA
============================================

CAMBIOS VS VERSION WINDOWS:
- ELIMINADO: PowerShell completo
- NUEVO: Funciones nativas Linux (pwd, os.stat)
- NUEVO: Rutas simples /mnt/path
- OPTIMIZADO: 10x mas rapido

FUNCIONALIDADES:
1. Exploracion recursiva de directorios INSUMOS por categoria
2. 13 categorias predefinidas (01_carto_basic ... 13_insu_colsmart)
3. Tabla insumos = agrupacion por municipio/categoria
4. Tabla clasificacion_insumo = clasificaciones
5. Tabla lista_archivos_preo = archivos
6. Sistema de propietarios nativos (Windows via getcifsacl)
7. Verificacion de existencia
8. Constraint unico en rutas
9. Sistema de notificaciones
10. Sistema de logs exportable

NUEVO (v2.0): Indexacion COMPLETA de Pre-Operacion
11. Indexa resto de 01_preo (excluyendo 07_insu)
12. Tablas: directorios_preoperacion, archivos_preoperacion
13. Permite vista arbol completa en frontend
"""

import os
import pwd
import psycopg2
from datetime import datetime
import traceback
import argparse
from propietario_windows import obtener_propietario_windows
import json
import multiprocessing
import threading
from pathlib import Path
import time
import logging
import logging.handlers
from dotenv import load_dotenv
import unicodedata

# Cargar variables de entorno desde .env (ubicado en el directorio padre)
ENV_PATH = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(ENV_PATH, override=False)

# CONFIGURACION GLOBAL - Desde .env (SIN FALLBACK - debe fallar si no esta configurado)
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
MODO_NO_NOTIFICACIONES = False

DB_LOCK = threading.Lock()
contador_lock = threading.Lock()

cambios_insumos = {'creados': 0, 'actualizados': 0, 'eliminados': 0}
cambios_clasificaciones = {'creadas': 0, 'actualizadas': 0, 'eliminadas': 0}
cambios_archivos = {'creados': 0, 'actualizados': 0, 'eliminados': 0}
cambios_por_municipio = {}

# NUEVO: Contadores para indexación de resto de pre-operación
cambios_directorios_preo = {'creados': 0, 'actualizados': 0, 'eliminados': 0}
cambios_archivos_preo = {'creados': 0, 'actualizados': 0, 'eliminados': 0}

# Directorios a EXCLUIR de la indexación de "resto" (ya indexados por INSUMOS)
DIRECTORIOS_EXCLUIR_PREO = ['07_insu']

logger = None
LOGS_HABILITADOS = False
DIRECTORIO_LOGS = "/var/log/script_insumos"
NIVEL_LOG = logging.INFO

# Mapeo de categorias
CATEGORIAS_MAPPING = {
    '01_carto_basic': {'cod_categoria': 1, 'nom_categoria': 'Cartografia Basica'},
    '02_estu_agro': {'cod_categoria': 2, 'nom_categoria': 'Estudio Agrologico'},
    '03_info_catas': {'cod_categoria': 3, 'nom_categoria': 'Informacion Catastral'},
    '04_deslin': {'cod_categoria': 4, 'nom_categoria': 'Deslinde'},
    '05_perim': {'cod_categoria': 5, 'nom_categoria': 'Perimetro'},
    '06_insu_regis': {'cod_categoria': 6, 'nom_categoria': 'Insumo Registral'},
    '07_insu_fuente_secun': {'cod_categoria': 7, 'nom_categoria': 'Insumos Fuentes Secundarias'},
    '08_inst_ord_terri': {'cod_categoria': 8, 'nom_categoria': 'Instrumento Ordenamiento Territorial'},
    '09_sald_conserva': {'cod_categoria': 9, 'nom_categoria': 'Saldo Conservacion'},
    '10_cica_app': {'cod_categoria': 10, 'nom_categoria': 'CICA app'},
    '11_comp_soci': {'cod_categoria': 11, 'nom_categoria': 'Componente Social'},
    '12_comp_amb': {'cod_categoria': 12, 'nom_categoria': 'Componente Ambiental'},
    '13_insu_colsmart': {'cod_categoria': 13, 'nom_categoria': 'Insumos Colsmart'}
}

CATEGORIA_PATTERNS = list(CATEGORIAS_MAPPING.keys())

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

def configurar_sistema_logs(exportar_logs=False, directorio_logs="/var/log/script_insumos", nivel_detalle="INFO"):
    global logger, LOGS_HABILITADOS, DIRECTORIO_LOGS

    LOGS_HABILITADOS = exportar_logs
    DIRECTORIO_LOGS = directorio_logs

    if not exportar_logs:
        print("Sistema de logs: DESHABILITADO")
        return

    try:
        os.makedirs(directorio_logs, exist_ok=True)

        logger = logging.getLogger('ScriptInsumosLinux')
        logger.setLevel(logging.INFO)

        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"script_insumos_linux_{timestamp}.log"
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
        logger.info("SCRIPT_INSUMOS_LINUX.py - INICIO")

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
        elif categoria == 'insumos':
            cambios_insumos[tipo_cambio] += 1
        elif categoria == 'clasificaciones':
            cambios_clasificaciones[tipo_cambio] += 1

        if cod_municipio:
            if cod_municipio not in cambios_por_municipio:
                cambios_por_municipio[cod_municipio] = {
                    'insumos': {'creados': 0, 'actualizados': 0, 'eliminados': 0},
                    'clasificaciones': {'creadas': 0, 'actualizadas': 0, 'eliminadas': 0},
                    'archivos': {'creados': 0, 'actualizados': 0, 'eliminados': 0}
                }
            cambios_por_municipio[cod_municipio][categoria][tipo_cambio] += 1

def incrementar_contador_preo(tipo_cambio, tabla='directorios'):
    """Incrementa contadores para tablas de pre-operación resto"""
    with contador_lock:
        if tabla == 'directorios':
            cambios_directorios_preo[tipo_cambio] += 1
        elif tabla == 'archivos':
            cambios_archivos_preo[tipo_cambio] += 1

def verificar_tablas_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Verificar tablas principales de INSUMOS
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name IN ('insumos', 'clasificacion_insumo', 'lista_archivos_preo', 'notificaciones')
        """)

        tablas = [row[0] for row in cursor.fetchall()]

        if 'insumos' not in tablas:
            log("ERROR: Tabla insumos no existe")
            return False

        if 'clasificacion_insumo' not in tablas:
            log("ERROR: Tabla clasificacion_insumo no existe")
            return False

        if 'lista_archivos_preo' not in tablas:
            log("ERROR: Tabla lista_archivos_preo no existe")
            return False

        # Crear indice si no existe
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_lista_archivos_path
            ON lista_archivos_preo(path_file)
        """)

        # ================================================================
        # NUEVO: Verificar/crear tablas para resto de pre-operación
        # ================================================================
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name IN ('directorios_preoperacion', 'archivos_preoperacion')
        """)
        tablas_preo = [row[0] for row in cursor.fetchall()]

        if 'directorios_preoperacion' not in tablas_preo:
            log("Creando tabla directorios_preoperacion...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS directorios_preoperacion (
                    cod_directorio SERIAL PRIMARY KEY,
                    nom_directorio VARCHAR(255) NOT NULL,
                    ruta_directorio TEXT NOT NULL UNIQUE,
                    nivel INTEGER NOT NULL DEFAULT 0,
                    parent_id INTEGER REFERENCES directorios_preoperacion(cod_directorio) ON DELETE CASCADE,
                    cod_mpio INTEGER NOT NULL,
                    fecha_creacion TIMESTAMP,
                    fecha_modificacion TIMESTAMP,
                    propietario VARCHAR(255),
                    fecha_indexacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS dir_preo_mpio_idx ON directorios_preoperacion(cod_mpio)")
            cursor.execute("CREATE INDEX IF NOT EXISTS dir_preo_parent_idx ON directorios_preoperacion(parent_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS dir_preo_nivel_idx ON directorios_preoperacion(nivel)")
            log("Tabla directorios_preoperacion creada")

        if 'archivos_preoperacion' not in tablas_preo:
            log("Creando tabla archivos_preoperacion...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS archivos_preoperacion (
                    cod_archivo SERIAL PRIMARY KEY,
                    nom_archivo VARCHAR(500) NOT NULL,
                    ruta_archivo TEXT NOT NULL UNIQUE,
                    extension VARCHAR(50),
                    tamano_bytes BIGINT,
                    propietario VARCHAR(255),
                    hash_contenido VARCHAR(255),
                    cod_directorio INTEGER NOT NULL REFERENCES directorios_preoperacion(cod_directorio) ON DELETE CASCADE,
                    fecha_creacion TIMESTAMP,
                    fecha_modificacion TIMESTAMP,
                    fecha_indexacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS arch_preo_dir_idx ON archivos_preoperacion(cod_directorio)")
            cursor.execute("CREATE INDEX IF NOT EXISTS arch_preo_ext_idx ON archivos_preoperacion(extension)")
            cursor.execute("CREATE INDEX IF NOT EXISTS arch_preo_prop_idx ON archivos_preoperacion(propietario)")
            log("Tabla archivos_preoperacion creada")

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        log(f"Error verificando tablas: {e}")
        return False

def obtener_rutas_preoperacion(municipio_especifico=None):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        if municipio_especifico:
            cursor.execute("""
                SELECT id, cod_municipio, path
                FROM path_dir_pre
                WHERE cod_municipio = %s
                ORDER BY cod_municipio
            """, (municipio_especifico,))
        else:
            cursor.execute("""
                SELECT id, cod_municipio, path
                FROM path_dir_pre
                ORDER BY cod_municipio
            """)

        rutas = cursor.fetchall()
        log(f"Rutas INSUMOS encontradas: {len(rutas)}")
        return rutas

    except Exception as e:
        log(f"Error obteniendo rutas: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

# NOTIFICACIONES
def crear_notificacion_archivo(conn, accion, id_archivo, nombre, datos_contexto, fecha, propietario):
    """Crea notificacion para archivo"""
    if MODO_SIMULACION or MODO_NO_NOTIFICACIONES:
        return True

    try:
        cursor = conn.cursor()

        descripcion = f"Archivo {accion}: {nombre}"
        datos_contexto['propietario'] = propietario

        cursor.execute("""
            INSERT INTO notificaciones(
                tipo_entidad, id_entidad, accion, descripcion,
                datos_contexto, fecha_cambio, leido
            ) VALUES (
                'archivo_insumo', %s, %s, %s, %s, %s, FALSE
            )
        """, (id_archivo, accion, descripcion, json.dumps(datos_contexto), fecha))

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        log(f"Error creando notificacion archivo: {e}", 3)
        return False

def crear_notificacion_insumo(conn, accion, id_insumo, datos_contexto, fecha):
    """Crea notificacion para insumo"""
    if MODO_SIMULACION or MODO_NO_NOTIFICACIONES:
        return True

    try:
        cursor = conn.cursor()

        descripcion = f"Insumo {accion}: {datos_contexto.get('categoria', 'N/A')} - {datos_contexto.get('municipio', 'N/A')}"

        cursor.execute("""
            INSERT INTO notificaciones(
                tipo_entidad, id_entidad, accion, descripcion,
                datos_contexto, fecha_cambio, leido
            ) VALUES (
                'insumo', %s, %s, %s, %s, %s, FALSE
            )
        """, (id_insumo, accion, descripcion, json.dumps(datos_contexto), fecha))

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        return False

def crear_notificacion_clasificacion(conn, accion, id_clasificacion, nombre, datos_contexto, fecha):
    """Crea notificacion para clasificacion"""
    if MODO_SIMULACION or MODO_NO_NOTIFICACIONES:
        return True

    try:
        cursor = conn.cursor()

        descripcion = f"Clasificacion {accion}: {nombre}"

        cursor.execute("""
            INSERT INTO notificaciones(
                tipo_entidad, id_entidad, accion, descripcion,
                datos_contexto, fecha_cambio, leido
            ) VALUES (
                'clasificacion_insumo', %s, %s, %s, %s, %s, FALSE
            )
        """, (id_clasificacion, accion, descripcion, json.dumps(datos_contexto), fecha))

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        return False

def crear_notificacion_resumen(conn):
    """Crea notificacion resumen final"""
    if MODO_SIMULACION or MODO_NO_NOTIFICACIONES:
        return True

    try:
        cursor = conn.cursor()
        fecha_actual = datetime.now()

        descripcion = f"Sincronizacion INSUMOS completada: "
        descripcion += f"{cambios_archivos['creados']} creados, "
        descripcion += f"{cambios_archivos['actualizados']} actualizados, "
        descripcion += f"{cambios_archivos['eliminados']} eliminados"

        datos_contexto = {
            'insumos': cambios_insumos,
            'clasificaciones': cambios_clasificaciones,
            'archivos': cambios_archivos,
            'municipios_afectados': len(cambios_por_municipio),
            'municipios': list(str(k) for k in cambios_por_municipio.keys()),
            'por_municipio': {str(k): v for k, v in cambios_por_municipio.items()},
            'fecha': fecha_actual.strftime('%Y-%m-%d %H:%M:%S'),
            'version': 'linux_nativa_v1'
        }

        cursor.execute("""
            INSERT INTO notificaciones(
                tipo_entidad, id_entidad, accion, descripcion,
                datos_contexto, fecha_cambio, leido
            ) VALUES (
                'sistema', 1, 'sincronizar_insumos', %s, %s, %s, FALSE
            )
        """, (descripcion, json.dumps(datos_contexto), fecha_actual))

        conn.commit()
        log(f"Notificacion resumen creada: {descripcion}")
        return True

    except Exception as e:
        conn.rollback()
        log(f"Error creando notificacion resumen: {e}")
        return False

# CLASE SCANNER INSUMOS
class ScannerArchivosInsumos:
    """Scanner optimizado para INSUMOS Linux - explora categorias recursivamente"""

    def __init__(self):
        self.archivos_procesados = set()

    def _coincide_categoria(self, dir_name, patron_categoria):
        """Compara nombres de directorio con patrones de categoria"""
        try:
            dir_normalizado = unicodedata.normalize('NFKD', dir_name.lower())
            patron_normalizado = unicodedata.normalize('NFKD', patron_categoria.lower())

            # 1. Coincidencia exacta
            if dir_normalizado == patron_normalizado:
                return True

            # 2. Sin acentos
            dir_sin_acentos = ''.join(c for c in dir_normalizado if not unicodedata.combining(c))
            patron_sin_acentos = ''.join(c for c in patron_normalizado if not unicodedata.combining(c))

            if dir_sin_acentos == patron_sin_acentos:
                return True

            # 3. Verificacion por codigo numerico
            patron_num = patron_categoria.split('_')[0]
            dir_num = dir_name.split('_')[0]

            if patron_num == dir_num:
                return True

            return False

        except Exception:
            return dir_name.lower() == patron_categoria.lower()

    def explorar_categorias(self, ruta_base, cod_municipio):
        """Explora y encuentra todas las categorias en un municipio"""
        categorias_encontradas = {}

        try:
            log(f"Explorando categorias en: {ruta_base}", 1)

            if not os.path.exists(ruta_base):
                log(f"ADVERTENCIA: Ruta no existe: {ruta_base}", 1)
                return categorias_encontradas

            for root, dirs, files in os.walk(ruta_base):
                for dir_name in dirs[:]:
                    for patron_categoria in CATEGORIA_PATTERNS:
                        if self._coincide_categoria(dir_name, patron_categoria):
                            ruta_categoria = os.path.join(root, dir_name)

                            categorias_encontradas[ruta_categoria] = {
                                'patron': patron_categoria,
                                'info': CATEGORIAS_MAPPING[patron_categoria],
                                'ruta_base': ruta_base
                            }

                            log(f"  Categoria encontrada: {patron_categoria} en {ruta_categoria}", 2)
                            break

            log(f"Total categorias encontradas: {len(categorias_encontradas)}", 1)
            return categorias_encontradas

        except Exception as e:
            log(f"Error explorando categorias: {e}", 1)
            return categorias_encontradas

    def recopilar_archivos_categoria(self, ruta_categoria):
        """Recopila todos los archivos de una categoria"""
        archivos_encontrados = []

        try:
            log(f"Recopilando archivos en: {ruta_categoria}", 2)

            if not os.path.exists(ruta_categoria):
                log(f"Ruta de categoria no existe: {ruta_categoria}", 2)
                return []

            for root, dirs, files in os.walk(ruta_categoria):
                # Manejar directorios especiales como .gdb
                dirs_originales = dirs[:]
                for dir_name in dirs_originales:
                    dir_lower = dir_name.lower()
                    if any(dir_lower.endswith(ext) for ext in EXTENSIONES_ARCHIVO_UNICO):
                        dir_path = os.path.join(root, dir_name)
                        archivos_encontrados.append(dir_path)
                        dirs.remove(dir_name)

                # Archivos regulares
                for filename in files:
                    if es_extension_ignorada(filename):
                        continue

                    file_path = os.path.join(root, filename)
                    archivos_encontrados.append(file_path)

            log(f"Archivos recopilados: {len(archivos_encontrados)}", 2)
            return archivos_encontrados

        except Exception as e:
            log(f"Error recopilando archivos: {e}", 2)
            return []

    def obtener_crear_insumo(self, conn, cod_municipio, cod_categoria):
        """Obtiene o crea un insumo"""
        try:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT cod_insumo FROM insumos WHERE cod_municipio = %s AND cod_categoria = %s",
                (cod_municipio, cod_categoria)
            )
            resultado = cursor.fetchone()

            if resultado:
                return resultado[0]

            if MODO_SIMULACION:
                log(f"[SIMULACION] Crearia insumo: municipio={cod_municipio}, categoria={cod_categoria}", 3)
                return -1

            # Obtener nombres para notificacion
            cursor.execute("""
                SELECT c.nom_categoria, m.nom_municipio
                FROM categorias c, municipios m
                WHERE c.cod_categoria = %s AND m.cod_municipio = %s
            """, (cod_categoria, cod_municipio))

            info = cursor.fetchone()
            categoria_nombre, municipio_nombre = info if info else (None, None)

            tipo_insumo = "Insumo Secundario" if cod_categoria == 7 else "Insumo Primario"

            cursor.execute("""
                INSERT INTO insumos (cod_municipio, cod_categoria, tipo_insumo)
                VALUES (%s, %s, %s) RETURNING cod_insumo
            """, (cod_municipio, cod_categoria, tipo_insumo))

            nuevo_id = cursor.fetchone()[0]
            conn.commit()

            # Notificacion
            datos_contexto = {
                "municipio_id": cod_municipio,
                "municipio": municipio_nombre,
                "categoria_id": cod_categoria,
                "categoria": categoria_nombre,
                "tipo_insumo": tipo_insumo
            }

            crear_notificacion_insumo(conn, 'crear', nuevo_id, datos_contexto, datetime.now())

            incrementar_contador('creados', cod_municipio, 'insumos')
            log(f"Insumo creado: {nuevo_id}", 2)
            return nuevo_id

        except Exception as e:
            conn.rollback()
            log(f"Error creando insumo: {e}")
            return None

    def obtener_crear_clasificacion(self, conn, cod_insumo, nombre, ruta):
        """Obtiene o crea una clasificacion"""
        try:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT cod_clasificacion FROM clasificacion_insumo WHERE cod_insumo = %s AND nombre = %s",
                (cod_insumo, nombre)
            )
            resultado = cursor.fetchone()

            if resultado:
                return resultado[0]

            if MODO_SIMULACION:
                log(f"[SIMULACION] Crearia clasificacion: {nombre}", 3)
                return -1

            # Obtener info para notificacion
            cursor.execute("""
                SELECT
                    i.cod_categoria,
                    cat.nom_categoria,
                    m.nom_municipio,
                    i.cod_municipio
                FROM insumos i
                LEFT JOIN categorias cat ON cat.cod_categoria = i.cod_categoria
                LEFT JOIN municipios m ON m.cod_municipio = i.cod_municipio
                WHERE i.cod_insumo = %s
            """, (cod_insumo,))

            info = cursor.fetchone()
            categoria_id, categoria_nombre, municipio_nombre, municipio_id = info if info else (None, None, None, None)

            cursor.execute("""
                INSERT INTO clasificacion_insumo (cod_insumo, nombre, ruta, observacion, descripcion)
                VALUES (%s, %s, %s, %s, %s) RETURNING cod_clasificacion
            """, (cod_insumo, nombre, ruta, "", ""))

            nuevo_id = cursor.fetchone()[0]
            conn.commit()

            # Notificacion
            datos_contexto = {
                "municipio_id": municipio_id,
                "municipio": municipio_nombre,
                "insumo_id": cod_insumo,
                "nombre": nombre,
                "categoria_id": categoria_id,
                "categoria": categoria_nombre,
                "ruta": ruta
            }

            crear_notificacion_clasificacion(conn, 'crear', nuevo_id, nombre, datos_contexto, datetime.now())

            incrementar_contador('creadas', None, 'clasificaciones')
            log(f"Clasificacion creada: {nombre}", 2)
            return nuevo_id

        except Exception as e:
            conn.rollback()
            log(f"Error creando clasificacion: {e}")
            return None

    def procesar_archivos_batch(self, conn, archivos_info, cod_clasificacion, cod_municipio):
        """Procesa archivos en batch"""
        if not archivos_info:
            return 0

        try:
            cursor = conn.cursor()

            # Obtener info de contexto
            cursor.execute("""
                SELECT
                    c.nombre as clasificacion_nombre,
                    i.cod_categoria,
                    cat.nom_categoria,
                    m.nom_municipio,
                    i.cod_insumo
                FROM clasificacion_insumo c
                JOIN insumos i ON i.cod_insumo = c.cod_insumo
                LEFT JOIN categorias cat ON cat.cod_categoria = i.cod_categoria
                LEFT JOIN municipios m ON m.cod_municipio = i.cod_municipio
                WHERE c.cod_clasificacion = %s
            """, (cod_clasificacion,))

            info_contexto = cursor.fetchone()
            if not info_contexto:
                log(f"No se encontro info de contexto para clasificacion {cod_clasificacion}")
                return 0

            clasificacion_nombre, categoria_id, categoria_nombre, municipio_nombre, insumo_id = info_contexto

            archivos_insertados = 0
            archivos_actualizados = 0

            for info in archivos_info:
                archivo_path = info['path']
                nombre = info['nombre']
                fecha = info['fecha']
                propietario = info['propietario']
                peso_bytes = info['peso_bytes']

                try:
                    # Verificar si existe
                    cursor.execute("""
                        SELECT id_lista_archivo, cod_insumo, usuario_windows
                        FROM lista_archivos_preo
                        WHERE path_file = %s
                        LIMIT 1
                    """, (archivo_path,))

                    archivo_existente = cursor.fetchone()

                    if archivo_existente:
                        id_existente, cod_insumo_existente, usuario_existente = archivo_existente

                        # Actualizar si cambio propietario
                        if usuario_existente != propietario and propietario != 'Sistema':
                            if not MODO_SIMULACION:
                                cursor.execute("""
                                    UPDATE lista_archivos_preo
                                    SET fecha_disposicion = %s, usuario_windows = %s,
                                        nombre_insumo = %s, peso_memoria = %s
                                    WHERE id_lista_archivo = %s
                                """, (fecha, propietario, nombre, peso_bytes, id_existente))

                                conn.commit()
                                archivos_actualizados += 1
                                incrementar_contador('actualizados', cod_municipio, 'archivos')

                                # Notificacion
                                datos_contexto = {
                                    "municipio_id": cod_municipio,
                                    "municipio": municipio_nombre,
                                    "clasificacion_id": cod_clasificacion,
                                    "clasificacion": clasificacion_nombre,
                                    "categoria_id": categoria_id,
                                    "categoria": categoria_nombre,
                                    "nombre": nombre,
                                    "ruta": archivo_path
                                }
                                crear_notificacion_archivo(conn, 'actualizar', id_existente, nombre,
                                    datos_contexto, fecha, propietario)
                    else:
                        # Insertar nuevo
                        if not MODO_SIMULACION:
                            cursor.execute("""
                                INSERT INTO lista_archivos_preo (
                                    cod_insumo, nombre_insumo, path_file,
                                    fecha_disposicion, usuario_windows, peso_memoria
                                ) VALUES (%s, %s, %s, %s, %s, %s)
                                RETURNING id_lista_archivo
                            """, (cod_clasificacion, nombre, archivo_path, fecha, propietario, peso_bytes))

                            id_nuevo = cursor.fetchone()[0]
                            conn.commit()

                            archivos_insertados += 1
                            incrementar_contador('creados', cod_municipio, 'archivos')

                            # Notificacion
                            datos_contexto = {
                                "municipio_id": cod_municipio,
                                "municipio": municipio_nombre,
                                "clasificacion_id": cod_clasificacion,
                                "clasificacion": clasificacion_nombre,
                                "categoria_id": categoria_id,
                                "categoria": categoria_nombre,
                                "nombre": nombre,
                                "ruta": archivo_path
                            }
                            crear_notificacion_archivo(conn, 'crear', id_nuevo, nombre,
                                datos_contexto, fecha, propietario)

                except Exception as e:
                    conn.rollback()
                    log(f"Error procesando archivo {nombre}: {e}", 3)
                    continue

            log(f"Batch completado: {archivos_insertados} insertados, {archivos_actualizados} actualizados", 2)
            return archivos_insertados + archivos_actualizados

        except Exception as e:
            conn.rollback()
            log(f"Error en procesar_archivos_batch: {e}", 1)
            return 0

    def eliminar_archivos_no_existentes(self, conn, cod_clasificacion, rutas_fisicas, cod_municipio):
        """Elimina archivos de BD que ya no existen fisicamente"""
        if not MODO_ELIMINAR:
            return 0

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id_lista_archivo, nombre_insumo, path_file, usuario_windows
                FROM lista_archivos_preo
                WHERE cod_insumo = %s
            """, (cod_clasificacion,))

            archivos_bd = cursor.fetchall()

            if not archivos_bd:
                return 0

            rutas_set = set(rutas_fisicas)
            archivos_eliminados = 0

            for id_archivo, nombre, path_bd, usuario_bd in archivos_bd:
                if path_bd not in rutas_set and not os.path.exists(path_bd):
                    if not MODO_SIMULACION:
                        cursor.execute("""
                            DELETE FROM lista_archivos_preo
                            WHERE id_lista_archivo = %s
                        """, (id_archivo,))

                        conn.commit()
                        incrementar_contador('eliminados', cod_municipio, 'archivos')
                        archivos_eliminados += 1
                        log(f"Archivo eliminado: {nombre}", 3)

            if archivos_eliminados > 0:
                log(f"Total archivos eliminados: {archivos_eliminados}", 2)

            return archivos_eliminados

        except Exception as e:
            conn.rollback()
            log(f"Error eliminando archivos: {e}", 1)
            return 0

    def procesar_categoria(self, ruta_categoria, info_categoria, cod_municipio):
        """Procesa una categoria completa"""
        patron = info_categoria['patron']
        categoria_info = info_categoria['info']
        cod_categoria = categoria_info['cod_categoria']
        nom_categoria = categoria_info['nom_categoria']

        log(f"\n{'='*50}", 1)
        log(f"Procesando categoria: {patron} ({nom_categoria})", 1)
        log(f"{'='*50}", 1)

        # Recopilar archivos
        archivos_encontrados = self.recopilar_archivos_categoria(ruta_categoria)

        if not archivos_encontrados:
            log(f"Sin archivos en categoria: {patron}", 1)
            return 0

        # Preparar info de archivos
        archivos_info = []
        for archivo_path in archivos_encontrados:
            nombre = os.path.basename(archivo_path)
            fecha = obtener_fechas_linux(archivo_path)
            propietario = obtener_propietario_linux(archivo_path)
            peso_bytes = obtener_peso_linux(archivo_path)

            archivos_info.append({
                'path': archivo_path,
                'nombre': nombre,
                'fecha': fecha,
                'propietario': propietario,
                'peso_bytes': peso_bytes
            })

        # Conectar a BD
        conn = psycopg2.connect(**DB_CONFIG)

        try:
            # Obtener/crear insumo
            cod_insumo = self.obtener_crear_insumo(conn, cod_municipio, cod_categoria)
            if not cod_insumo:
                return 0

            # Obtener/crear clasificacion
            cod_clasificacion = self.obtener_crear_clasificacion(
                conn, cod_insumo, nom_categoria, ruta_categoria
            )
            if not cod_clasificacion:
                return 0

            # Procesar archivos
            archivos_procesados = self.procesar_archivos_batch(
                conn, archivos_info, cod_clasificacion, cod_municipio
            )

            # Eliminar archivos que ya no existen
            self.eliminar_archivos_no_existentes(
                conn, cod_clasificacion, archivos_encontrados, cod_municipio
            )

            log(f"Categoria {patron} completada: {archivos_procesados} archivos", 1)
            return archivos_procesados

        finally:
            conn.close()

    def procesar_municipio_completo(self, ruta_base, cod_municipio):
        """Procesa un municipio INSUMOS completo"""
        try:
            log(f"\n{'='*60}", 1)
            log(f"PROCESANDO MUNICIPIO INSUMOS: {cod_municipio}", 1)
            log(f"Ruta: {ruta_base}", 1)
            log(f"{'='*60}\n", 1)

            inicio_municipio = time.time()

            # 1. Explorar categorias
            categorias_encontradas = self.explorar_categorias(ruta_base, cod_municipio)

            if not categorias_encontradas:
                log(f"No se encontraron categorias en {ruta_base}", 1)
                return (cod_municipio, 0, 0)

            # 2. Procesar cada categoria
            total_archivos = 0
            for ruta_categoria, info_categoria in categorias_encontradas.items():
                archivos_procesados = self.procesar_categoria(
                    ruta_categoria, info_categoria, cod_municipio
                )
                total_archivos += archivos_procesados

            tiempo_municipio = time.time() - inicio_municipio
            log(f"\nMunicipio INSUMOS {cod_municipio} completado: {len(categorias_encontradas)} categorias, {total_archivos} archivos en {tiempo_municipio:.2f}s", 1)

            return (cod_municipio, len(categorias_encontradas), total_archivos)

        except Exception as e:
            log(f"Error procesando municipio INSUMOS {cod_municipio}: {e}", 1)
            traceback.print_exc()
            return (cod_municipio, 0, 0)


# ================================================================
# CLASE SCANNER PRE-OPERACION RESTO (excluyendo 07_insu)
# ================================================================
class ScannerPreoperacionResto:
    """
    Scanner para indexar el resto de la estructura de pre-operación.
    Indexa: 01_prop, 02_carta_acept, 03_cto_modif, 04_acta_ini,
            05_plan_gest_proy, 06_precono, 08_contr_pers
    EXCLUYE: 07_insu (ya indexado por ScannerArchivosInsumos)
    """

    def __init__(self):
        self.directorios_procesados = set()
        self.archivos_procesados = set()

    def obtener_ruta_preoperacion(self, ruta_insumos):
        """
        Deriva la ruta raíz de pre-operación desde la ruta de INSUMOS.
        Ejemplo:
          Input:  /mnt/repositorio/.../01_preo/07_insu
          Output: /mnt/repositorio/.../01_preo
        """
        try:
            ruta = Path(ruta_insumos)

            # Buscar el directorio 01_preo en la ruta
            partes = ruta.parts
            for i, parte in enumerate(partes):
                if parte == '01_preo':
                    # Reconstruir la ruta hasta 01_preo inclusive
                    ruta_preo = Path(*partes[:i+1])
                    return str(ruta_preo)

            # Si no encontramos 01_preo, ir un nivel arriba de 07_insu
            if ruta.name == '07_insu' or '07_insu' in str(ruta):
                return str(ruta.parent)

            return str(ruta.parent)

        except Exception as e:
            log(f"Error derivando ruta pre-operación: {e}", 1)
            return None

    def explorar_directorios_preo(self, ruta_preo, cod_municipio):
        """
        Explora la estructura de pre-operación excluyendo 07_insu.
        Retorna lista de directorios con su jerarquía.
        """
        directorios = []

        try:
            if not os.path.exists(ruta_preo):
                log(f"Ruta pre-operación no existe: {ruta_preo}", 1)
                return directorios

            log(f"Explorando pre-operación resto en: {ruta_preo}", 1)

            for root, dirs, files in os.walk(ruta_preo):
                # Excluir 07_insu y sus subdirectorios
                dirs_filtrados = []
                for d in dirs:
                    if d not in DIRECTORIOS_EXCLUIR_PREO:
                        dirs_filtrados.append(d)
                    else:
                        log(f"  Excluyendo directorio: {d}", 2)

                dirs[:] = dirs_filtrados  # Modifica in-place para os.walk

                # Calcular nivel relativo
                nivel = len(Path(root).relative_to(ruta_preo).parts)

                # Agregar directorio actual (excepto la raíz que es 01_preo)
                if root != ruta_preo:
                    directorios.append({
                        'ruta': root,
                        'nombre': os.path.basename(root),
                        'nivel': nivel,
                        'parent_ruta': str(Path(root).parent),
                        'archivos': [f for f in files if not es_extension_ignorada(f)]
                    })

            log(f"Directorios encontrados (excluyendo 07_insu): {len(directorios)}", 1)
            return directorios

        except Exception as e:
            log(f"Error explorando pre-operación: {e}", 1)
            traceback.print_exc()
            return directorios

    def obtener_o_crear_directorio(self, conn, ruta, nombre, nivel, parent_id, cod_municipio):
        """Obtiene o crea un directorio en la tabla directorios_preoperacion"""
        try:
            cursor = conn.cursor()

            # Buscar existente
            cursor.execute("""
                SELECT cod_directorio FROM directorios_preoperacion
                WHERE ruta_directorio = %s
            """, (ruta,))

            resultado = cursor.fetchone()

            if resultado:
                # Ya existe, actualizar fecha de indexación
                cursor.execute("""
                    UPDATE directorios_preoperacion
                    SET fecha_indexacion = CURRENT_TIMESTAMP
                    WHERE cod_directorio = %s
                """, (resultado[0],))
                conn.commit()
                return resultado[0]

            if MODO_SIMULACION:
                log(f"[SIMULACION] Crearía directorio: {nombre}", 3)
                return -1

            # Obtener fechas y propietario
            fecha_mod = obtener_fechas_linux(ruta)
            propietario = obtener_propietario_linux(ruta)

            cursor.execute("""
                INSERT INTO directorios_preoperacion (
                    nom_directorio, ruta_directorio, nivel, parent_id,
                    cod_mpio, fecha_creacion, fecha_modificacion, propietario
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING cod_directorio
            """, (nombre, ruta, nivel, parent_id, cod_municipio,
                  fecha_mod, fecha_mod, propietario))

            nuevo_id = cursor.fetchone()[0]
            conn.commit()

            incrementar_contador_preo('creados', 'directorios')
            log(f"Directorio creado: {nombre} (nivel {nivel})", 2)
            return nuevo_id

        except Exception as e:
            conn.rollback()
            log(f"Error creando directorio {nombre}: {e}", 1)
            return None

    def procesar_archivos_directorio(self, conn, cod_directorio, ruta_directorio, archivos):
        """Procesa los archivos de un directorio"""
        if not archivos:
            return 0

        try:
            cursor = conn.cursor()
            archivos_procesados = 0

            for nombre_archivo in archivos:
                ruta_archivo = os.path.join(ruta_directorio, nombre_archivo)

                if not os.path.exists(ruta_archivo):
                    continue

                try:
                    # Verificar si existe
                    cursor.execute("""
                        SELECT cod_archivo FROM archivos_preoperacion
                        WHERE ruta_archivo = %s
                    """, (ruta_archivo,))

                    resultado = cursor.fetchone()

                    if resultado:
                        # Actualizar fecha de indexación
                        cursor.execute("""
                            UPDATE archivos_preoperacion
                            SET fecha_indexacion = CURRENT_TIMESTAMP
                            WHERE cod_archivo = %s
                        """, (resultado[0],))
                        conn.commit()
                        continue

                    if MODO_SIMULACION:
                        log(f"[SIMULACION] Crearía archivo: {nombre_archivo}", 3)
                        archivos_procesados += 1
                        continue

                    # Obtener metadatos
                    extension = os.path.splitext(nombre_archivo)[1].lower() or None
                    tamano = obtener_peso_linux(ruta_archivo)
                    propietario = obtener_propietario_linux(ruta_archivo)
                    fecha_mod = obtener_fechas_linux(ruta_archivo)

                    cursor.execute("""
                        INSERT INTO archivos_preoperacion (
                            nom_archivo, ruta_archivo, extension, tamano_bytes,
                            propietario, cod_directorio, fecha_creacion, fecha_modificacion
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (nombre_archivo, ruta_archivo, extension, tamano,
                          propietario, cod_directorio, fecha_mod, fecha_mod))

                    conn.commit()
                    incrementar_contador_preo('creados', 'archivos')
                    archivos_procesados += 1

                except Exception as e:
                    conn.rollback()
                    log(f"Error procesando archivo {nombre_archivo}: {e}", 3)
                    continue

            return archivos_procesados

        except Exception as e:
            log(f"Error procesando archivos del directorio: {e}", 1)
            return 0

    def eliminar_registros_huerfanos(self, conn, cod_municipio):
        """Elimina directorios y archivos que ya no existen físicamente"""
        if not MODO_ELIMINAR:
            return (0, 0)

        try:
            cursor = conn.cursor()
            dirs_eliminados = 0
            archs_eliminados = 0

            # Obtener archivos del municipio
            cursor.execute("""
                SELECT a.cod_archivo, a.ruta_archivo
                FROM archivos_preoperacion a
                JOIN directorios_preoperacion d ON a.cod_directorio = d.cod_directorio
                WHERE d.cod_mpio = %s
            """, (cod_municipio,))

            archivos = cursor.fetchall()

            for cod_archivo, ruta in archivos:
                if not os.path.exists(ruta):
                    if not MODO_SIMULACION:
                        cursor.execute("DELETE FROM archivos_preoperacion WHERE cod_archivo = %s", (cod_archivo,))
                        conn.commit()
                    incrementar_contador_preo('eliminados', 'archivos')
                    archs_eliminados += 1

            # Obtener directorios del municipio (ordenar por nivel descendente para eliminar hijos primero)
            cursor.execute("""
                SELECT cod_directorio, ruta_directorio
                FROM directorios_preoperacion
                WHERE cod_mpio = %s
                ORDER BY nivel DESC
            """, (cod_municipio,))

            directorios = cursor.fetchall()

            for cod_dir, ruta in directorios:
                if not os.path.exists(ruta):
                    if not MODO_SIMULACION:
                        cursor.execute("DELETE FROM directorios_preoperacion WHERE cod_directorio = %s", (cod_dir,))
                        conn.commit()
                    incrementar_contador_preo('eliminados', 'directorios')
                    dirs_eliminados += 1

            if dirs_eliminados > 0 or archs_eliminados > 0:
                log(f"Limpieza huérfanos: {dirs_eliminados} dirs, {archs_eliminados} archivos", 2)

            return (dirs_eliminados, archs_eliminados)

        except Exception as e:
            conn.rollback()
            log(f"Error eliminando huérfanos: {e}", 1)
            return (0, 0)

    def procesar_municipio_preo(self, ruta_insumos, cod_municipio):
        """Procesa la estructura pre-operación resto para un municipio"""
        try:
            # 1. Derivar ruta de pre-operación
            ruta_preo = self.obtener_ruta_preoperacion(ruta_insumos)

            if not ruta_preo or not os.path.exists(ruta_preo):
                log(f"No se pudo obtener ruta pre-operación para municipio {cod_municipio}", 1)
                return (cod_municipio, 0, 0)

            log(f"\n{'='*60}", 1)
            log(f"PROCESANDO PRE-OPERACIÓN RESTO: Municipio {cod_municipio}", 1)
            log(f"Ruta: {ruta_preo}", 1)
            log(f"{'='*60}\n", 1)

            inicio = time.time()

            # 2. Explorar directorios
            directorios = self.explorar_directorios_preo(ruta_preo, cod_municipio)

            if not directorios:
                log(f"Sin directorios en pre-operación resto para municipio {cod_municipio}", 1)
                return (cod_municipio, 0, 0)

            # 3. Conectar a BD
            conn = psycopg2.connect(**DB_CONFIG)

            try:
                # 4. Crear mapeo de rutas a IDs (para establecer parent_id)
                ruta_a_id = {}

                # Ordenar por nivel para procesar padres primero
                directorios_ordenados = sorted(directorios, key=lambda x: x['nivel'])

                total_archivos = 0

                for dir_info in directorios_ordenados:
                    # Determinar parent_id
                    parent_id = ruta_a_id.get(dir_info['parent_ruta'])

                    # Crear/obtener directorio
                    cod_dir = self.obtener_o_crear_directorio(
                        conn,
                        dir_info['ruta'],
                        dir_info['nombre'],
                        dir_info['nivel'],
                        parent_id,
                        cod_municipio
                    )

                    if cod_dir and cod_dir > 0:
                        ruta_a_id[dir_info['ruta']] = cod_dir

                        # Procesar archivos del directorio
                        archivos_procesados = self.procesar_archivos_directorio(
                            conn, cod_dir, dir_info['ruta'], dir_info['archivos']
                        )
                        total_archivos += archivos_procesados

                # 5. Eliminar registros huérfanos
                self.eliminar_registros_huerfanos(conn, cod_municipio)

                tiempo = time.time() - inicio
                log(f"\nMunicipio {cod_municipio} pre-op resto: {len(directorios)} dirs, {total_archivos} archivos en {tiempo:.2f}s", 1)

                return (cod_municipio, len(directorios), total_archivos)

            finally:
                conn.close()

        except Exception as e:
            log(f"Error procesando pre-operación municipio {cod_municipio}: {e}", 1)
            traceback.print_exc()
            return (cod_municipio, 0, 0)


def main():
    global MODO_VERBOSE, MODO_SIMULACION, MODO_NO_NOTIFICACIONES

    parser = argparse.ArgumentParser(description='Scanner INSUMOS Linux')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--simulacion', action='store_true')
    parser.add_argument('--municipio', type=int)
    parser.add_argument('--exportar-logs', action='store_true')
    parser.add_argument('--directorio-logs', default='/var/log/script_insumos')
    parser.add_argument('--sin-notificaciones', action='store_true')

    args = parser.parse_args()

    MODO_VERBOSE = args.verbose or True
    MODO_SIMULACION = args.simulacion
    MODO_NO_NOTIFICACIONES = args.sin_notificaciones

    if args.exportar_logs:
        configurar_sistema_logs(True, args.directorio_logs)

    print("="*60)
    print("SCRIPT_INSUMOS_LINUX.py v2.0 - INDEXACION COMPLETA")
    print("  - FASE 1: INSUMOS (07_insu)")
    print("  - FASE 2: PRE-OPERACION RESTO (01-06, 08)")
    print("="*60)

    inicio_total = time.time()

    try:
        log("Verificando base de datos...")
        if not verificar_tablas_db():
            print("Error verificando tablas")
            return

        log("Obteniendo rutas INSUMOS...")
        rutas = obtener_rutas_preoperacion(args.municipio)

        if not rutas:
            print("No hay rutas configuradas")
            return

        print(f"\nProcesando {len(rutas)} municipios INSUMOS")

        # ================================================================
        # FASE 1: INDEXAR INSUMOS (07_insu)
        # ================================================================
        log("\n" + "="*60)
        log("FASE 1: INDEXANDO INSUMOS (07_insu)")
        log("="*60 + "\n")

        scanner_insumos = ScannerArchivosInsumos()

        for id_path, cod_municipio, path_municipio in rutas:
            try:
                scanner_insumos.procesar_municipio_completo(path_municipio, cod_municipio)
            except Exception as e:
                log(f"Error procesando INSUMOS municipio {cod_municipio}: {e}", 1)
                continue

        tiempo_insumos = time.time() - inicio_total
        log(f"\nFASE 1 completada en {tiempo_insumos:.2f} segundos")

        # ================================================================
        # FASE 2: INDEXAR RESTO DE PRE-OPERACIÓN (excluyendo 07_insu)
        # ================================================================
        log("\n" + "="*60)
        log("FASE 2: INDEXANDO RESTO PRE-OPERACIÓN (01-06, 08)")
        log("="*60 + "\n")

        inicio_preo = time.time()
        scanner_preo = ScannerPreoperacionResto()

        for id_path, cod_municipio, path_municipio in rutas:
            try:
                scanner_preo.procesar_municipio_preo(path_municipio, cod_municipio)
            except Exception as e:
                log(f"Error procesando PRE-OP RESTO municipio {cod_municipio}: {e}", 1)
                continue

        tiempo_preo = time.time() - inicio_preo
        log(f"\nFASE 2 completada en {tiempo_preo:.2f} segundos")

        tiempo_total = time.time() - inicio_total

        # Crear notificacion resumen
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            crear_notificacion_resumen(conn)
            conn.close()
        except Exception as e:
            log(f"Error creando notificacion resumen: {e}")

        print("\n" + "="*60)
        print("SCRIPT_INSUMOS_LINUX.py v2.0 COMPLETADO")
        print("="*60)

        print(f"\n--- ESTADISTICAS INSUMOS (07_insu) ---")
        print(f"  Insumos creados: {cambios_insumos['creados']}")
        print(f"  Clasificaciones creadas: {cambios_clasificaciones['creadas']}")
        print(f"  Archivos creados: {cambios_archivos['creados']}")
        print(f"  Archivos actualizados: {cambios_archivos['actualizados']}")
        print(f"  Archivos eliminados: {cambios_archivos['eliminados']}")

        print(f"\n--- ESTADISTICAS PRE-OPERACION RESTO ---")
        print(f"  Directorios creados: {cambios_directorios_preo['creados']}")
        print(f"  Directorios actualizados: {cambios_directorios_preo['actualizados']}")
        print(f"  Directorios eliminados: {cambios_directorios_preo['eliminados']}")
        print(f"  Archivos creados: {cambios_archivos_preo['creados']}")
        print(f"  Archivos actualizados: {cambios_archivos_preo['actualizados']}")
        print(f"  Archivos eliminados: {cambios_archivos_preo['eliminados']}")

        print(f"\n--- RESUMEN GENERAL ---")
        print(f"  Municipios procesados: {len(rutas)}")
        print(f"  Tiempo INSUMOS: {tiempo_insumos:.2f}s")
        print(f"  Tiempo PRE-OP RESTO: {tiempo_preo:.2f}s")
        print(f"  Tiempo total: {tiempo_total:.2f} segundos")
        print("="*60)

    except KeyboardInterrupt:
        print("\nInterrumpido por usuario")
    except Exception as e:
        print(f"\nError critico: {str(e)}")
        traceback.print_exc()
    finally:
        if args.exportar_logs and logger:
            logger.info("SCRIPT_INSUMOS_LINUX.py - FIN")

if __name__ == "__main__":
    main()
