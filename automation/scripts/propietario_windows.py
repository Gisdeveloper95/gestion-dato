#!/usr/bin/env python3
"""
propietario_windows.py
Módulo compartido para obtener propietarios y metadatos Windows REALES usando SMB directo
"""

import subprocess
import re
import psycopg2
from datetime import datetime
import os


DB_CONFIG = {
    'host': 'localhost',
    'database': 'gestion_dato_db',
    'user': 'postgres',
    'password': '1234',
    'port': '5432'
}

# Configuración SMB
SMB_SERVER = '172.21.54.13'
SMB_SHARE = 'DirGesCat'
SMB_USERNAME = 'andres.osorio@igac.gov.co'
SMB_PASSWORD = os.getenv('SMB_PASSWORD', '')  # Configurable por variable de entorno

# Cache de conexión SMB (para evitar reconectar en cada archivo)
_smb_connection = None
_smb_tid = None


def obtener_conexion_smb():
    """
    Obtiene o crea una conexión SMB persistente

    Returns:
        tuple: (SMBConnection, tree_id) o (None, None) si falla
    """
    global _smb_connection, _smb_tid

    if _smb_connection is not None:
        try:
            # Verificar que la conexión sigue activa
            _smb_connection.getSMBServer()
            return _smb_connection, _smb_tid
        except:
            _smb_connection = None
            _smb_tid = None

    try:
        from impacket.smbconnection import SMBConnection

        smb = SMBConnection(SMB_SERVER, SMB_SERVER, timeout=10)
        smb.login(SMB_USERNAME, SMB_PASSWORD, domain='')
        tid = smb.connectTree(SMB_SHARE)

        _smb_connection = smb
        _smb_tid = tid

        return smb, tid
    except Exception:
        return None, None


def obtener_metadatos_windows_smb(ruta_archivo):
    """
    Obtiene metadatos REALES de Windows usando SMB directo con impacket

    Args:
        ruta_archivo (str): Ruta completa del archivo en Linux (ej: /mnt/repositorio/2510SP/...)

    Returns:
        dict: {'sid': str, 'fecha_modificacion': datetime, 'fecha_creacion': datetime} o None
    """
    try:
        # Convertir ruta Linux a ruta SMB
        if not ruta_archivo.startswith('/mnt/repositorio/'):
            return None

        ruta_smb = ruta_archivo.replace('/mnt/repositorio/', '').replace('/', '\\')

        smb, tid = obtener_conexion_smb()
        if not smb or not tid:
            return None

        from impacket import smb3structs

        # Abrir el archivo para obtener sus atributos
        fid = smb.openFile(tid, ruta_smb, desiredAccess=smb3structs.FILE_READ_ATTRIBUTES)

        # Obtener información del archivo
        file_info = smb.queryInfo(tid, fid)

        # Obtener descriptor de seguridad (SID del propietario)
        OWNER_SECURITY_INFORMATION = 0x00000001
        sec_desc = smb.querySecurityInfo(tid, fid, OWNER_SECURITY_INFORMATION)

        # Extraer SID del propietario
        owner_sid = sec_desc['OwnerSid'].formatCanonical()

        # Extraer fechas
        # file_info contiene las fechas en formato FILETIME de Windows
        fecha_modificacion = datetime.fromtimestamp(file_info['LastWriteTime'])
        fecha_creacion = datetime.fromtimestamp(file_info['CreationTime'])

        smb.closeFile(tid, fid)

        return {
            'sid': owner_sid,
            'fecha_modificacion': fecha_modificacion,
            'fecha_creacion': fecha_creacion
        }

    except Exception as e:
        # Si falla SMB, intentar con getcifsacl como fallback
        return None


def obtener_sid_propietario_fallback(ruta_archivo):
    """
    Fallback: Usa getcifsacl para obtener el SID del propietario Windows

    Args:
        ruta_archivo (str): Ruta completa del archivo en Linux

    Returns:
        str: SID del propietario (ej: S-1-5-21-...-43400) o None si falla
    """
    try:
        cmd = ['getcifsacl', ruta_archivo]
        resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if resultado.returncode == 0:
            # Buscar la línea OWNER:S-1-5-21-...
            match = re.search(r'OWNER:(S-1-5-21-[\d-]+)', resultado.stdout)
            if match:
                return match.group(1)

        return None

    except subprocess.TimeoutExpired:
        return None
    except FileNotFoundError:
        # getcifsacl no está instalado
        return None
    except Exception:
        return None


def resolver_sid_con_bd(sid):
    """
    Resuelve un SID consultando la tabla de mapeo en PostgreSQL

    Si el SID no existe en la tabla, lo crea como "SID-XXXXX" para resolución posterior

    Args:
        sid (str): SID completo de Windows

    Returns:
        str: Nombre del usuario Windows o "SID-XXXXX" si no está resuelto
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Usar la función de PostgreSQL para obtener usuario
        cursor.execute("SELECT obtener_usuario_por_sid(%s)", (sid,))
        usuario = cursor.fetchone()[0]

        # COMMIT para guardar el nuevo SID si se creó
        conn.commit()
        conn.close()

        return usuario

    except Exception:
        # Fallback: extraer RID del SID
        rid = sid.split('-')[-1]
        return f"SID-{rid}"


def obtener_propietario_windows(ruta_archivo):
    """
    Obtiene el propietario Windows REAL del archivo usando SMB directo

    Proceso:
    1. Intenta obtener metadatos vía SMB directo (SID + fechas REALES)
    2. Si falla, usa getcifsacl como fallback (solo SID)
    3. Resuelve el SID a nombre de usuario desde BD

    Args:
        ruta_archivo (str): Ruta completa del archivo en Linux

    Returns:
        str: Nombre del usuario Windows (ej: "laura.rodriguez") o "SID-XXXXX" o "Sistema"
    """
    # Paso 1: Intentar obtener metadatos vía SMB directo
    metadatos = obtener_metadatos_windows_smb(ruta_archivo)

    if metadatos:
        sid = metadatos['sid']
    else:
        # Fallback: usar getcifsacl
        sid = obtener_sid_propietario_fallback(ruta_archivo)

    if not sid:
        # No se pudo obtener SID
        return 'Sistema'

    # Paso 2: Resolver SID a nombre de usuario desde BD
    usuario = resolver_sid_con_bd(sid)

    return usuario


def obtener_metadatos_completos_windows(ruta_archivo):
    """
    Obtiene metadatos COMPLETOS de Windows (propietario + fechas)

    Args:
        ruta_archivo (str): Ruta completa del archivo en Linux

    Returns:
        dict: {
            'usuario': str,
            'sid': str,
            'fecha_modificacion': datetime,
            'fecha_creacion': datetime
        } o None si falla
    """
    # Intentar obtener metadatos vía SMB
    metadatos = obtener_metadatos_windows_smb(ruta_archivo)

    if not metadatos:
        # Fallback: usar getcifsacl + fechas del filesystem
        sid = obtener_sid_propietario_fallback(ruta_archivo)
        if not sid:
            return None

        # Usar fechas del filesystem como fallback
        try:
            import os
            stat_info = os.stat(ruta_archivo)
            metadatos = {
                'sid': sid,
                'fecha_modificacion': datetime.fromtimestamp(stat_info.st_mtime),
                'fecha_creacion': datetime.fromtimestamp(stat_info.st_ctime)
            }
        except:
            return None

    # Resolver SID a usuario
    usuario = resolver_sid_con_bd(metadatos['sid'])

    return {
        'usuario': usuario,
        'sid': metadatos['sid'],
        'fecha_modificacion': metadatos['fecha_modificacion'],
        'fecha_creacion': metadatos.get('fecha_creacion')
    }


def verificar_sids_sin_resolver():
    """
    Retorna lista de SIDs que aún no han sido resueltos a nombres de usuario

    Returns:
        list: Lista de tuplas (sid, usuario_temporal, fecha_registro)
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT sid, usuario_windows, fecha_registro
            FROM sids_sin_resolver
            ORDER BY fecha_registro DESC
        """)

        resultados = cursor.fetchall()
        conn.close()

        return resultados

    except Exception:
        return []


def resolver_sid_manual(sid, usuario_windows, nombre_completo=None):
    """
    Resuelve manualmente un SID a un nombre de usuario

    Args:
        sid (str): SID completo de Windows
        usuario_windows (str): Nombre de usuario (ej: "laura.rodriguez")
        nombre_completo (str, optional): Nombre completo del usuario
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE mapeo_sids
            SET usuario_windows = %s,
                nombre_completo = %s,
                resuelto = TRUE,
                notas = 'Resuelto manualmente'
            WHERE sid = %s
        """, (usuario_windows, nombre_completo, sid))

        conn.commit()
        conn.close()

        return True

    except Exception:
        return False


if __name__ == "__main__":
    # Test
    import sys

    if len(sys.argv) < 2:
        print("Uso: python3 propietario_windows.py RUTA_ARCHIVO")
        sys.exit(1)

    ruta = sys.argv[1]
    propietario = obtener_propietario_windows(ruta)

    print(f"Archivo: {ruta}")
    print(f"Propietario: {propietario}")

    # Mostrar SIDs sin resolver
    sids_pendientes = verificar_sids_sin_resolver()
    if sids_pendientes:
        print(f"\nSIDs sin resolver: {len(sids_pendientes)}")
        for sid, usuario_temp, fecha in sids_pendientes[:5]:
            print(f"  - {sid} → {usuario_temp} (desde {fecha})")
