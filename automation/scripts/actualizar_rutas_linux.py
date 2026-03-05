#!/usr/bin/env python3
"""
actualizar_rutas_linux.py - Actualiza rutas Windows -> Linux en BD
===================================================================

Convierte rutas como:
- \\\\servidor\\PREOPERACION\\... -> /mnt/repositorio/PREOPERACION/...
- C:\\Users\\... -> /home/users/...

TABLAS AFECTADAS:
1. notificaciones.datos_contexto (JSONB)
2. notificaciones_post.datos_contexto (JSONB)
3. path_dir_pre.path
4. path_dir_post.path
5. lista_archivos_preo.path_file
6. archivos_post.ruta_completa (si existe)
"""

import psycopg2
import json
import re
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'database': 'gestion_dato_db',
    'user': 'postgres',
    'password': '1234',
    'port': '5432'
}

def convertir_ruta_windows_a_linux(ruta_windows):
    """Convierte ruta Windows a ruta Linux"""
    if not ruta_windows or not isinstance(ruta_windows, str):
        return ruta_windows

    ruta = ruta_windows

    # Eliminar prefijos UNC largos
    ruta = ruta.replace('\\\\?\\UNC\\', '\\\\')
    ruta = ruta.replace('\\\\?\\', '')

    # Convertir rutas UNC: \\servidor\share\path -> /mnt/repositorio/path
    if ruta.startswith('\\\\'):
        # Eliminar \\servidor\share y reemplazar con /mnt/repositorio
        partes = ruta.split('\\')
        partes = [p for p in partes if p]  # Eliminar strings vacíos

        if len(partes) >= 2:
            # Saltar servidor y share, mantener el resto
            ruta_relativa = '/'.join(partes[2:])
            ruta = f'/mnt/repositorio/{ruta_relativa}'
        else:
            ruta = f'/mnt/repositorio/{"/".join(partes)}'

    # Convertir rutas locales: C:\Users\... -> /home/users/...
    elif len(ruta) > 1 and ruta[1] == ':':
        ruta = ruta[2:]  # Quitar C:
        ruta = f'/home{ruta}'

    # Reemplazar todas las \ por /
    ruta = ruta.replace('\\', '/')

    # Limpiar múltiples slashes
    while '//' in ruta:
        ruta = ruta.replace('//', '/')

    return ruta

def actualizar_notificaciones_tabla(conn, tabla_nombre):
    """Actualiza rutas en tabla de notificaciones (genérica para notificaciones y notificaciones_post)"""
    print(f"\n=== ACTUALIZANDO {tabla_nombre.upper()} ===")

    try:
        cursor = conn.cursor()

        # Buscar registros con rutas Windows (\\repositorio o C:)
        cursor.execute(f"""
            SELECT id, datos_contexto
            FROM {tabla_nombre}
            WHERE datos_contexto IS NOT NULL
              AND (
                  datos_contexto::text LIKE '%\\\\repositorio%'
                  OR datos_contexto::text LIKE '%:\\\\%'
              )
        """)

        notificaciones = cursor.fetchall()
        print(f"Encontradas {len(notificaciones)} notificaciones con rutas Windows")

        actualizadas = 0
        sin_cambios = 0

        for id_notif, datos_contexto in notificaciones:
            try:
                # Convertir JSONB a dict
                contexto_dict = dict(datos_contexto) if isinstance(datos_contexto, dict) else datos_contexto

                # Actualizar rutas en el dict
                contexto_actualizado = {}
                hubo_cambios = False

                for key, value in contexto_dict.items():
                    if isinstance(value, str) and ('\\' in value or (len(value) > 1 and value[1:3] == ':/')):
                        nueva_ruta = convertir_ruta_windows_a_linux(value)
                        contexto_actualizado[key] = nueva_ruta
                        if nueva_ruta != value:
                            hubo_cambios = True
                            if actualizadas < 5:  # Mostrar primeros 5 ejemplos
                                print(f"  Ejemplo: {value[:60]}... -> {nueva_ruta[:60]}...")
                    else:
                        contexto_actualizado[key] = value

                if not hubo_cambios:
                    sin_cambios += 1
                    continue

                # Actualizar en BD
                cursor.execute(f"""
                    UPDATE {tabla_nombre}
                    SET datos_contexto = %s
                    WHERE id = %s
                """, (json.dumps(contexto_actualizado), id_notif))

                actualizadas += 1

                if actualizadas % 100 == 0:
                    conn.commit()
                    print(f"  Progreso: {actualizadas}/{len(notificaciones)}")

            except Exception as e:
                print(f"  Error actualizando registro {id_notif}: {e}")
                continue

        conn.commit()
        print(f"✓ {actualizadas} registros actualizados")
        if sin_cambios > 0:
            print(f"  ({sin_cambios} registros sin cambios)")

    except Exception as e:
        conn.rollback()
        print(f"✗ Error actualizando {tabla_nombre}: {e}")

def actualizar_notificaciones(conn):
    """Actualiza rutas en notificaciones.datos_contexto"""
    actualizar_notificaciones_tabla(conn, 'notificaciones')

def actualizar_notificaciones_post(conn):
    """Actualiza rutas en notificaciones_post.datos_contexto"""
    actualizar_notificaciones_tabla(conn, 'notificaciones_post')

def actualizar_path_dir_pre(conn):
    """Actualiza rutas en path_dir_pre.path"""
    print("\n=== ACTUALIZANDO PATH_DIR_PRE ===")

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, path
            FROM path_dir_pre
            WHERE path LIKE '%\\%'
        """)

        rutas = cursor.fetchall()
        print(f"Encontradas {len(rutas)} rutas Windows")

        actualizadas = 0

        for id_path, path_windows in rutas:
            path_linux = convertir_ruta_windows_a_linux(path_windows)

            cursor.execute("""
                UPDATE path_dir_pre
                SET path = %s
                WHERE id = %s
            """, (path_linux, id_path))

            actualizadas += 1
            print(f"  {path_windows} -> {path_linux}")

        conn.commit()
        print(f"✓ {actualizadas} rutas actualizadas en path_dir_pre")

    except Exception as e:
        conn.rollback()
        print(f"✗ Error actualizando path_dir_pre: {e}")

def actualizar_path_dir_post(conn):
    """Actualiza rutas en path_dir_post.path"""
    print("\n=== ACTUALIZANDO PATH_DIR_POST ===")

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, path
            FROM path_dir_post
            WHERE path LIKE '%\\%'
        """)

        rutas = cursor.fetchall()
        print(f"Encontradas {len(rutas)} rutas Windows")

        actualizadas = 0

        for id_path, path_windows in rutas:
            path_linux = convertir_ruta_windows_a_linux(path_windows)

            cursor.execute("""
                UPDATE path_dir_post
                SET path = %s
                WHERE id = %s
            """, (path_linux, id_path))

            actualizadas += 1
            print(f"  {path_windows} -> {path_linux}")

        conn.commit()
        print(f"✓ {actualizadas} rutas actualizadas en path_dir_post")

    except Exception as e:
        conn.rollback()
        print(f"✗ Error actualizando path_dir_post: {e}")

def actualizar_lista_archivos_preo(conn):
    """Actualiza rutas en lista_archivos_preo.path_file"""
    print("\n=== ACTUALIZANDO LISTA_ARCHIVOS_PREO ===")

    try:
        cursor = conn.cursor()

        # Contar primero
        cursor.execute("""
            SELECT COUNT(*)
            FROM lista_archivos_preo
            WHERE path_file LIKE '%\\%'
        """)

        total = cursor.fetchone()[0]
        print(f"Encontrados {total} archivos con rutas Windows")

        if total == 0:
            print("✓ No hay archivos para actualizar")
            return

        # Actualizar por lotes
        batch_size = 1000
        actualizadas = 0

        cursor.execute("""
            SELECT id_lista_archivo, path_file
            FROM lista_archivos_preo
            WHERE path_file LIKE '%\\%'
        """)

        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break

            for id_archivo, path_windows in batch:
                path_linux = convertir_ruta_windows_a_linux(path_windows)

                cursor.execute("""
                    UPDATE lista_archivos_preo
                    SET path_file = %s
                    WHERE id_lista_archivo = %s
                """, (path_linux, id_archivo))

                actualizadas += 1

            conn.commit()
            print(f"  Progreso: {actualizadas}/{total}")

        print(f"✓ {actualizadas} archivos actualizados en lista_archivos_preo")

    except Exception as e:
        conn.rollback()
        print(f"✗ Error actualizando lista_archivos_preo: {e}")

def main():
    print("="*60)
    print("ACTUALIZADOR DE RUTAS WINDOWS -> LINUX")
    print("="*60)
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✓ Conectado a la base de datos")

        # Actualizar cada tabla
        actualizar_path_dir_pre(conn)
        actualizar_path_dir_post(conn)
        actualizar_lista_archivos_preo(conn)
        actualizar_notificaciones(conn)
        actualizar_notificaciones_post(conn)

        conn.close()

        print("\n" + "="*60)
        print("ACTUALIZACION COMPLETADA")
        print(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

    except Exception as e:
        print(f"\n✗ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
