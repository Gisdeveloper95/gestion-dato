#!/usr/bin/env python3
"""
resolver_sids.py
Script para resolver manualmente SIDs a nombres de usuario
"""

import psycopg2
import sys

DB_CONFIG = {
    'host': 'localhost',
    'database': 'gestion_dato_db',
    'user': 'postgres',
    'password': '1234',
    'port': '5432'
}


def listar_sids_sin_resolver():
    """Muestra todos los SIDs que no han sido resueltos"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sid, usuario_windows, fecha_registro, notas
        FROM sids_sin_resolver
        ORDER BY fecha_registro DESC
    """)

    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        print("✅ No hay SIDs pendientes de resolver")
        return []

    print(f"\n📋 SIDs SIN RESOLVER: {len(resultados)}")
    print("="*80)

    for i, (sid, usuario_temp, fecha, notas) in enumerate(resultados, 1):
        print(f"\n{i}. SID: {sid}")
        print(f"   Usuario temporal: {usuario_temp}")
        print(f"   Fecha registro: {fecha}")
        if notas:
            print(f"   Notas: {notas}")

    return resultados


def resolver_sid(sid, usuario_windows, nombre_completo=None, notas=None):
    """Resuelve un SID a un nombre de usuario"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE mapeo_sids
        SET usuario_windows = %s,
            nombre_completo = %s,
            resuelto = TRUE,
            notas = %s
        WHERE sid = %s
    """, (usuario_windows, nombre_completo, notas, sid))

    filas_actualizadas = cursor.rowcount
    conn.commit()
    conn.close()

    return filas_actualizadas > 0


def resolver_interactivo():
    """Modo interactivo para resolver SIDs"""
    print("="*80)
    print("RESOLVER SIDS - MODO INTERACTIVO")
    print("="*80)

    sids = listar_sids_sin_resolver()

    if not sids:
        return

    print("\n" + "="*80)
    print("\nOpciones:")
    print("  1. Resolver SID individual")
    print("  2. Resolver todos de una vez (desde CSV)")
    print("  3. Salir")

    opcion = input("\nSelecciona opción (1-3): ").strip()

    if opcion == "1":
        # Resolver uno por uno
        numero = input(f"\n¿Cuál SID quieres resolver? (1-{len(sids)}): ").strip()

        try:
            idx = int(numero) - 1
            sid, usuario_temp, fecha, _ = sids[idx]

            print(f"\nResolviendo: {sid}")
            print(f"Usuario temporal: {usuario_temp}")

            usuario = input("\nNombre de usuario Windows (ej. laura.rodriguez): ").strip()
            nombre = input("Nombre completo (opcional, Enter para omitir): ").strip() or None
            notas = input("Notas (opcional, Enter para omitir): ").strip() or "Resuelto manualmente"

            if resolver_sid(sid, usuario, nombre, notas):
                print(f"\n✅ SID resuelto exitosamente: {sid} → {usuario}")
            else:
                print(f"\n❌ Error resolviendo SID")

        except (ValueError, IndexError):
            print("\n❌ Número inválido")

    elif opcion == "2":
        # Importar desde CSV
        print("\n📄 Importar desde CSV")
        print("\nFormato del CSV: sid,usuario_windows,nombre_completo")
        print("Ejemplo:")
        print("  S-1-5-21-...-43400,laura.rodriguez,Laura Rodríguez")
        print("  S-1-5-21-...-52134,brayan.lara,Brayan Lara")

        archivo_csv = input("\nRuta del archivo CSV: ").strip()

        try:
            with open(archivo_csv, 'r', encoding='utf-8') as f:
                lineas = f.readlines()

            resueltos = 0
            for linea in lineas[1:]:  # Saltar header
                if not linea.strip():
                    continue

                partes = [p.strip() for p in linea.split(',')]
                if len(partes) >= 2:
                    sid = partes[0]
                    usuario = partes[1]
                    nombre = partes[2] if len(partes) > 2 else None

                    if resolver_sid(sid, usuario, nombre, "Importado desde CSV"):
                        resueltos += 1
                        print(f"  ✅ {sid} → {usuario}")

            print(f"\n✅ Total resueltos: {resueltos}")

        except FileNotFoundError:
            print(f"\n❌ Archivo no encontrado: {archivo_csv}")
        except Exception as e:
            print(f"\n❌ Error: {e}")

    print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Modo CLI
        if sys.argv[1] == "listar":
            listar_sids_sin_resolver()
        elif sys.argv[1] == "resolver" and len(sys.argv) >= 4:
            sid = sys.argv[2]
            usuario = sys.argv[3]
            nombre = sys.argv[4] if len(sys.argv) > 4 else None

            if resolver_sid(sid, usuario, nombre):
                print(f"✅ SID resuelto: {sid} → {usuario}")
            else:
                print(f"❌ Error resolviendo SID")
        else:
            print("Uso:")
            print("  python3 resolver_sids.py                           # Modo interactivo")
            print("  python3 resolver_sids.py listar                    # Listar SIDs sin resolver")
            print('  python3 resolver_sids.py resolver SID USUARIO [NOMBRE]  # Resolver uno')
    else:
        # Modo interactivo
        resolver_interactivo()
