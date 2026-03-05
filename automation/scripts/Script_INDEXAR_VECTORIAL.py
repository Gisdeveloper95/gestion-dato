#!/usr/bin/env python3
"""
Script de Indexación Vectorial
Indexa todos los archivos de la BD en el sistema de búsqueda semántica
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import time

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.vector_index import VectorIndex
from utils.common import Config, DatabaseManager


def indexar_preoperacion(vector_idx: VectorIndex, db: DatabaseManager, limit: int = None):
    """Indexa archivos de preoperación"""
    print("\n" + "="*60)
    print("INDEXANDO PREOPERACIÓN")
    print("="*60)

    # Consulta para obtener archivos
    query = """
        SELECT
            id,
            path_file as path,
            nombre_archivo as nombre,
            COALESCE(SUBSTRING(path_file, 30, 5), '') as cod_mpio,
            extension,
            CASE
                WHEN peso_memoria LIKE '%GB%' THEN CAST(SPLIT_PART(peso_memoria, ' ', 1) AS FLOAT) * 1024
                WHEN peso_memoria LIKE '%MB%' THEN CAST(SPLIT_PART(peso_memoria, ' ', 1) AS FLOAT)
                ELSE 0
            END as size_mb,
            fecha_disposicion as fecha,
            nombre_insumo as categoria
        FROM lista_archivos_preo
        WHERE path_file IS NOT NULL AND nombre_archivo IS NOT NULL
    """

    if limit:
        query += f" LIMIT {limit}"

    print(f"📊 Consultando base de datos...")
    start = time.time()

    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(query)

    # Convertir a lista de diccionarios
    columns = [desc[0] for desc in cursor.description]
    archivos = []

    for row in cursor.fetchall():
        archivo = dict(zip(columns, row))
        # Convertir fecha a string si es datetime
        if archivo['fecha'] and hasattr(archivo['fecha'], 'strftime'):
            archivo['fecha'] = archivo['fecha'].strftime('%Y-%m-%d')
        archivos.append(archivo)

    conn.close()

    elapsed = time.time() - start
    print(f"✅ Consultados {len(archivos):,} archivos en {elapsed:.2f}s")

    # Indexar
    if archivos:
        vector_idx.indexar_lote(archivos, fase='preo', batch_size=100)
    else:
        print("⚠️ No hay archivos para indexar")


def indexar_postoperacion(vector_idx: VectorIndex, db: DatabaseManager, limit: int = None):
    """Indexa archivos de postoperación"""
    print("\n" + "="*60)
    print("INDEXANDO POSTOPERACIÓN")
    print("="*60)

    query = """
        SELECT
            ap.id,
            CONCAT(dp.ruta_acceso, '/', ap.nombre) as path,
            ap.nombre as nombre,
            SUBSTRING(dp.cod_municipio::text, 1, 5) as cod_mpio,
            ap.extension,
            COALESCE(ap.peso_memoria / (1024.0 * 1024.0), 0) as size_mb,
            ap.fecha_disposicion as fecha,
            'postoperacion' as categoria
        FROM archivos_post ap
        JOIN disposicion_post dp ON ap.id_disposicion = dp.id_disposicion
        WHERE ap.nombre IS NOT NULL
    """

    if limit:
        query += f" LIMIT {limit}"

    print(f"📊 Consultando base de datos...")
    start = time.time()

    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(query)

    columns = [desc[0] for desc in cursor.description]
    archivos = []

    for row in cursor.fetchall():
        archivo = dict(zip(columns, row))
        if archivo['fecha'] and hasattr(archivo['fecha'], 'strftime'):
            archivo['fecha'] = archivo['fecha'].strftime('%Y-%m-%d')
        archivos.append(archivo)

    conn.close()

    elapsed = time.time() - start
    print(f"✅ Consultados {len(archivos):,} archivos en {elapsed:.2f}s")

    if archivos:
        vector_idx.indexar_lote(archivos, fase='post', batch_size=100)
    else:
        print("⚠️ No hay archivos para indexar")


def indexar_operacion(vector_idx: VectorIndex, db: DatabaseManager, limit: int = None):
    """Indexa archivos de operación"""
    print("\n" + "="*60)
    print("INDEXANDO OPERACIÓN")
    print("="*60)

    query = """
        SELECT
            id,
            path as path,
            nombre as nombre,
            COALESCE(cod_mpio, '') as cod_mpio,
            extension,
            COALESCE(size / (1024.0 * 1024.0), 0) as size_mb,
            fecha_modificacion as fecha,
            'operacion' as categoria
        FROM archivos_operacion
        WHERE nombre IS NOT NULL
    """

    if limit:
        query += f" LIMIT {limit}"

    print(f"📊 Consultando base de datos...")
    start = time.time()

    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(query)

    columns = [desc[0] for desc in cursor.description]
    archivos = []

    for row in cursor.fetchall():
        archivo = dict(zip(columns, row))
        if archivo['fecha'] and hasattr(archivo['fecha'], 'strftime'):
            archivo['fecha'] = archivo['fecha'].strftime('%Y-%m-%d')
        archivos.append(archivo)

    conn.close()

    elapsed = time.time() - start
    print(f"✅ Consultados {len(archivos):,} archivos en {elapsed:.2f}s")

    if archivos:
        vector_idx.indexar_lote(archivos, fase='opera', batch_size=100)
    else:
        print("⚠️ No hay archivos para indexar")


def indexar_transversal(vector_idx: VectorIndex, db: DatabaseManager, limit: int = None):
    """Indexa archivos transversales"""
    print("\n" + "="*60)
    print("INDEXANDO TRANSVERSAL")
    print("="*60)

    query = """
        SELECT
            id,
            path as path,
            nombre as nombre,
            '' as cod_mpio,
            extension,
            COALESCE(size / (1024.0 * 1024.0), 0) as size_mb,
            fecha_modificacion as fecha,
            'transversal' as categoria
        FROM archivos_transv
        WHERE nombre IS NOT NULL
    """

    if limit:
        query += f" LIMIT {limit}"

    print(f"📊 Consultando base de datos...")
    start = time.time()

    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(query)

    columns = [desc[0] for desc in cursor.description]
    archivos = []

    for row in cursor.fetchall():
        archivo = dict(zip(columns, row))
        if archivo['fecha'] and hasattr(archivo['fecha'], 'strftime'):
            archivo['fecha'] = archivo['fecha'].strftime('%Y-%m-%d')
        archivos.append(archivo)

    conn.close()

    elapsed = time.time() - start
    print(f"✅ Consultados {len(archivos):,} archivos en {elapsed:.2f}s")

    if archivos:
        vector_idx.indexar_lote(archivos, fase='transv', batch_size=100)
    else:
        print("⚠️ No hay archivos para indexar")


def main():
    """Función principal"""
    print("\n" + "="*80)
    print("🚀 SCRIPT DE INDEXACIÓN VECTORIAL - VEGA IA")
    print("="*80)
    print(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Parsear argumentos
    import argparse
    parser = argparse.ArgumentParser(description='Indexar archivos para búsqueda semántica')
    parser.add_argument('--fase', choices=['preo', 'post', 'opera', 'transv', 'all'],
                       default='all', help='Fase a indexar')
    parser.add_argument('--limit', type=int, help='Límite de archivos (para testing)')
    parser.add_argument('--limpiar', action='store_true', help='Limpiar índice antes de indexar')

    args = parser.parse_args()

    try:
        # Inicializar
        print("📦 Inicializando sistema...")
        vector_idx = VectorIndex()
        db = DatabaseManager(Config())

        # Limpiar si se solicita
        if args.limpiar:
            print("\n🗑️ Limpiando índice...")
            if args.fase == 'all':
                vector_idx.limpiar_indice()
            else:
                vector_idx.limpiar_indice(args.fase)

        # Indexar según fase
        start_total = time.time()

        if args.fase == 'all' or args.fase == 'preo':
            indexar_preoperacion(vector_idx, db, args.limit)

        if args.fase == 'all' or args.fase == 'post':
            indexar_postoperacion(vector_idx, db, args.limit)

        if args.fase == 'all' or args.fase == 'opera':
            indexar_operacion(vector_idx, db, args.limit)

        if args.fase == 'all' or args.fase == 'transv':
            indexar_transversal(vector_idx, db, args.limit)

        # Resumen final
        elapsed_total = time.time() - start_total

        print("\n" + "="*80)
        print("✅ INDEXACIÓN COMPLETADA")
        print("="*80)
        print(f"⏱️ Tiempo total: {elapsed_total/60:.2f} minutos")
        print()

        # Mostrar estadísticas
        stats = vector_idx.exportar_estadisticas()
        print("📊 Estadísticas finales:")
        for fase, info in stats['fases'].items():
            print(f"   {fase.upper()}: {info['total_archivos']:,} archivos")

        print(f"\n⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

    except KeyboardInterrupt:
        print("\n\n⚠️ Indexación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
