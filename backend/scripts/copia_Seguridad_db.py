import subprocess
import os
import datetime
import sys
import platform
import shutil

def find_pg_dump_executable():
    """
    Encuentra la ruta al ejecutable pg_dump en sistemas Windows y Linux.
    
    Returns:
        str: Ruta al ejecutable pg_dump o simplemente "pg_dump" si no se encuentra una ruta específica
    """
    # Primero intentar encontrar pg_dump en el PATH
    pg_dump_command = "pg_dump"
    if shutil.which(pg_dump_command):
        return pg_dump_command
        
    # Si no se encuentra, buscar en ubicaciones comunes según el sistema operativo
    system = platform.system()
    if system == "Windows":
        # Ubicaciones comunes en Windows
        possible_paths = [
            # PostgreSQL instalado desde el instalador oficial
            r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\14\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\13\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\12\bin\pg_dump.exe",
            # PostgreSQL instalado desde EnterpriseDB
            r"C:\Program Files\edb\as16\bin\pg_dump.exe",
            r"C:\Program Files\edb\as15\bin\pg_dump.exe",
            # PostgreSQL instalado en la carpeta Program Files (x86)
            r"C:\Program Files (x86)\PostgreSQL\16\bin\pg_dump.exe",
            r"C:\Program Files (x86)\PostgreSQL\15\bin\pg_dump.exe",
            r"C:\Program Files (x86)\PostgreSQL\14\bin\pg_dump.exe",
            r"C:\Program Files (x86)\PostgreSQL\13\bin\pg_dump.exe",
            r"C:\Program Files (x86)\PostgreSQL\12\bin\pg_dump.exe",
        ]
    else:
        # Ubicaciones comunes en Linux/Mac
        possible_paths = [
            "/usr/bin/pg_dump",
            "/usr/local/bin/pg_dump",
            "/opt/postgresql/bin/pg_dump",
            "/usr/lib/postgresql/16/bin/pg_dump",
            "/usr/lib/postgresql/15/bin/pg_dump",
            "/usr/lib/postgresql/14/bin/pg_dump",
            "/usr/lib/postgresql/13/bin/pg_dump",
            "/usr/lib/postgresql/12/bin/pg_dump",
        ]
    
    # Verificar cada ruta
    for path in possible_paths:
        if os.path.isfile(path):
            return path
    
    # Si no se encuentra, regresamos el comando original y dejamos que
    # el sistema operativo intente encontrarlo en el PATH
    return pg_dump_command

def create_postgres_backup(db_config, output_dir="backups"):
    """
    Crea un backup de una base de datos PostgreSQL usando pg_dump.

    Genera un backup limpio y portable que puede restaurarse en cualquier servidor PostgreSQL.

    Args:
        db_config (dict): Configuración de la base de datos
        output_dir (str): Directorio donde se guardará el backup

    Returns:
        str: Ruta al archivo de backup creado
    """
    # Asegurarse de que el directorio de backup existe
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generar nombre de archivo con timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{db_config['database']}_{timestamp}.sql"
    backup_path = os.path.join(output_dir, backup_filename)

    # Encontrar el ejecutable pg_dump
    pg_dump_executable = find_pg_dump_executable()
    print(f"Usando pg_dump desde: {pg_dump_executable}")

    # Configurar comando pg_dump con flags mejorados para restauración limpia
    pg_dump_command = [
        pg_dump_executable,
        f"--host={db_config['host']}",
        f"--port={db_config['port']}",
        f"--username={db_config['user']}",
        f"--dbname={db_config['database']}",
        "--format=plain",           # Formato de texto plano SQL
        "--no-owner",               # No incluir comandos de propietario (evita errores de permisos)
        "--no-privileges",          # No incluir GRANT/REVOKE (evita errores de roles)
        "--no-acl",                 # Equivalente a --no-privileges
        "--if-exists",              # Usar IF EXISTS en DROP (evita errores si no existe)
        "--clean",                  # Incluir comandos DROP antes de los CREATE
        "--encoding=UTF8",          # Forzar encoding UTF8
        "--no-comments",            # No incluir comentarios de extensiones (evita errores)
        f"--file={backup_path}"
    ]

    # Configurar variable de entorno PGPASSWORD
    env = os.environ.copy()
    env["PGPASSWORD"] = db_config['password']

    try:
        # Ejecutar pg_dump
        print(f"Ejecutando comando: {' '.join(pg_dump_command)}")
        process = subprocess.run(
            pg_dump_command,
            env=env,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Post-procesar el archivo para limpiar comandos problemáticos
        if os.path.exists(backup_path):
            clean_backup_file(backup_path)

        print(f"Backup creado exitosamente: {backup_path}")
        return backup_path

    except subprocess.CalledProcessError as e:
        print(f"Error al crear el backup: {e}")
        print(f"Salida de error: {e.stderr}")
        return None
    except FileNotFoundError as e:
        print(f"Error: No se pudo encontrar el ejecutable pg_dump. {e}")
        print("Por favor, asegúrate de que PostgreSQL está instalado y su directorio bin está en el PATH.")
        return None


def clean_backup_file(backup_path):
    """
    Limpia el archivo de backup eliminando comandos problemáticos.

    Remueve:
    - Comandos \\connect que pueden causar problemas
    - Comandos SELECT pg_catalog.set_config('search_path', '', false)
    - Líneas con \\restrict (psql internal command)

    Args:
        backup_path (str): Ruta al archivo de backup a limpiar
    """
    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_size = len(content)
        lines = content.split('\n')
        cleaned_lines = []

        skip_patterns = [
            '\\connect',                    # Comandos de conexión psql
            "SELECT pg_catalog.set_config('search_path'",  # Configuración de search_path
            '\\restrict',                   # Comando interno de psql
        ]

        for line in lines:
            skip = False
            for pattern in skip_patterns:
                if pattern in line:
                    skip = True
                    print(f"  Removiendo línea problemática: {line[:80]}...")
                    break
            if not skip:
                cleaned_lines.append(line)

        cleaned_content = '\n'.join(cleaned_lines)

        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)

        new_size = len(cleaned_content)
        if original_size != new_size:
            print(f"  Archivo limpiado: {original_size} -> {new_size} bytes")

    except Exception as e:
        print(f"Advertencia: No se pudo limpiar el archivo de backup: {e}")

# Método alternativo: hacer un backup directo a un archivo sin usar pg_dump
def create_backup_with_psycopg2(db_config, output_dir="backups"):
    """
    Crea un backup de la base de datos usando la biblioteca psycopg2.
    Esto es útil cuando pg_dump no está disponible en el sistema.
    
    Args:
        db_config (dict): Configuración de la base de datos
        output_dir (str): Directorio donde se guardará el backup
    
    Returns:
        str: Ruta al archivo de backup creado
    """
    try:
        import psycopg2
    except ImportError:
        print("Error: Para usar este método, necesitas instalar psycopg2.")
        print("Puedes instalarlo con: pip install psycopg2-binary")
        return None
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{db_config['database']}_{timestamp}_psycopg2.sql"
    backup_path = os.path.join(output_dir, backup_filename)
    
    try:
        # Conectar a la base de datos
        connection = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        connection.autocommit = True
        cursor = connection.cursor()
        
        # Obtener lista de esquemas
        cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('pg_catalog', 'information_schema');")
        schemas = [row[0] for row in cursor.fetchall()]
        
        with open(backup_path, 'w', encoding='utf-8') as backup_file:
            # Escribir comentario de inicio
            backup_file.write(f"-- Backup de la base de datos {db_config['database']} creado el {datetime.datetime.now()}\n\n")
            
            # Para cada esquema
            for schema in schemas:
                print(f"Procesando esquema: {schema}")
                backup_file.write(f"\n-- Esquema: {schema}\n")
                backup_file.write(f"CREATE SCHEMA IF NOT EXISTS {schema};\n")
                
                # Obtener tablas del esquema
                cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = %s AND table_type = 'BASE TABLE';", (schema,))
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    print(f"  Exportando tabla: {schema}.{table}")
                    backup_file.write(f"\n-- Tabla: {schema}.{table}\n")
                    
                    # Obtener definición de columnas
                    cursor.execute(f"""
                        SELECT column_name, data_type, character_maximum_length, column_default, is_nullable
                        FROM information_schema.columns
                        WHERE table_schema = %s AND table_name = %s
                        ORDER BY ordinal_position;
                    """, (schema, table))
                    columns = cursor.fetchall()
                    
                    # Generar comando CREATE TABLE
                    create_table = f"CREATE TABLE IF NOT EXISTS {schema}.{table} (\n"
                    column_defs = []
                    for col in columns:
                        col_name, col_type, col_length, col_default, col_nullable = col
                        col_def = f"    {col_name} {col_type}"
                        if col_length:
                            col_def += f"({col_length})"
                        if col_default:
                            col_def += f" DEFAULT {col_default}"
                        if col_nullable == 'NO':
                            col_def += " NOT NULL"
                        column_defs.append(col_def)
                    
                    create_table += ",\n".join(column_defs) + "\n);\n\n"
                    backup_file.write(create_table)
                    
                    # Extraer datos
                    cursor.execute(f"SELECT * FROM {schema}.{table};")
                    rows = cursor.fetchall()
                    
                    if rows:
                        backup_file.write(f"-- Datos para la tabla {schema}.{table}\n")
                        
                        columns_str = ", ".join([c[0] for c in columns])
                        for row in rows:
                            values = []
                            for val in row:
                                if val is None:
                                    values.append('NULL')
                                elif isinstance(val, (int, float)):
                                    values.append(str(val))
                                else:
                                    # Escapar comillas simples en strings
                                    val_str = str(val).replace("'", "''")
                                    values.append(f"'{val_str}'")
                            
                            values_str = ", ".join(values)
                            backup_file.write(f"INSERT INTO {schema}.{table} ({columns_str}) VALUES ({values_str});\n")
                        
                        backup_file.write("\n")
            
            print(f"Backup creado exitosamente: {backup_path}")
            return backup_path
            
    except Exception as e:
        print(f"Error al crear el backup con psycopg2: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if 'connection' in locals() and connection:
            connection.close()

# También puedes crear un backup comprimido si quieres ahorrar espacio
def create_compressed_postgres_backup(db_config, output_dir="backups"):
    """
    Crea un backup comprimido (gz) de una base de datos PostgreSQL.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{db_config['database']}_{timestamp}.sql.gz"
    backup_path = os.path.join(output_dir, backup_filename)
    
    # Encontrar el ejecutable pg_dump
    pg_dump_executable = find_pg_dump_executable()
    print(f"Usando pg_dump desde: {pg_dump_executable}")
    
    # Configurar comando pg_dump para salida comprimida
    pg_dump_command = [
        pg_dump_executable,
        f"--host={db_config['host']}",
        f"--port={db_config['port']}",
        f"--username={db_config['user']}",
        f"--dbname={db_config['database']}",
        "--format=plain",
        "--create",
        "--clean"
    ]
    
    # Comando para comprimir con gzip
    gzip_command = ["gzip", "-c"]
    
    env = os.environ.copy()
    env["PGPASSWORD"] = db_config['password']
    
    try:
        # Ejecutar pg_dump y canalizar la salida a través de gzip
        with open(backup_path, 'wb') as backup_file:
            pg_dump_process = subprocess.Popen(
                pg_dump_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            
            gzip_process = subprocess.Popen(
                gzip_command,
                stdin=pg_dump_process.stdout,
                stdout=backup_file,
                stderr=subprocess.PIPE
            )
            
            # Permitir que pg_dump_process cierre su salida
            pg_dump_process.stdout.close()
            
            # Esperar a que ambos procesos finalicen
            gzip_process.communicate()
            pg_dump_exit_code = pg_dump_process.wait()
            
            if pg_dump_exit_code != 0:
                stderr = pg_dump_process.stderr.read().decode('utf-8')
                print(f"Error en pg_dump: {stderr}")
                return None
        
        print(f"Backup comprimido creado exitosamente: {backup_path}")
        return backup_path
        
    except Exception as e:
        print(f"Error al crear el backup comprimido: {e}")
        return None

# Función para restaurar un backup
def restore_postgres_backup(db_config, backup_file):
    """
    Restaura un backup SQL a una base de datos PostgreSQL.
    
    Args:
        db_config (dict): Configuración de la base de datos
        backup_file (str): Ruta al archivo de backup
    
    Returns:
        bool: True si la restauración fue exitosa, False en caso contrario
    """
    if not os.path.exists(backup_file):
        print(f"El archivo de backup no existe: {backup_file}")
        return False
    
    # Verificar si el archivo está comprimido
    is_compressed = backup_file.endswith('.gz')
    
    # Configurar comando de restauración
    if is_compressed:
        # Para archivos comprimidos, usamos gzip para descomprimir y psql para restaurar
        gzip_command = ["gzip", "-cd", backup_file]
        psql_command = [
            "psql",
            f"--host={db_config['host']}",
            f"--port={db_config['port']}",
            f"--username={db_config['user']}",
            f"--dbname=postgres"  # Nos conectamos a la base de datos postgres para poder ejecutar DROP/CREATE
        ]
    else:
        # Para archivos no comprimidos, usamos psql directamente
        psql_command = [
            "psql",
            f"--host={db_config['host']}",
            f"--port={db_config['port']}",
            f"--username={db_config['user']}",
            f"--dbname=postgres",
            f"--file={backup_file}"
        ]
    
    env = os.environ.copy()
    env["PGPASSWORD"] = db_config['password']
    
    try:
        if is_compressed:
            # Ejecutar los comandos en pipeline
            gzip_process = subprocess.Popen(
                gzip_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            
            psql_process = subprocess.Popen(
                psql_command,
                stdin=gzip_process.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            
            # Permitir que gzip_process cierre su salida
            gzip_process.stdout.close()
            
            # Esperar a que ambos procesos finalicen
            stdout, stderr = psql_process.communicate()
            gzip_process.wait()
            
            if psql_process.returncode != 0:
                print(f"Error al restaurar el backup: {stderr.decode('utf-8')}")
                return False
        else:
            # Ejecutar psql directamente
            process = subprocess.run(
                psql_command,
                env=env,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        
        print(f"Backup restaurado exitosamente desde: {backup_file}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error al restaurar el backup: {e}")
        print(f"Salida de error: {e.stderr}")
        return False

def backup_using_custom_commands(db_config, output_dir="backups"):
    """
    Intenta hacer un backup usando comandos directos específicos para Windows.
    Esta es una alternativa cuando pg_dump no está disponible.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{db_config['database']}_{timestamp}_direct.sql"
    backup_path = os.path.join(output_dir, backup_filename)
    
    # Intenta buscar en ubicaciones típicas la ruta de bin de PostgreSQL
    postgres_paths = [
        r"C:\Program Files\PostgreSQL\16\bin",
        r"C:\Program Files\PostgreSQL\15\bin",
        r"C:\Program Files\PostgreSQL\14\bin",
        r"C:\Program Files\PostgreSQL\13\bin",
        r"C:\Program Files\PostgreSQL\12\bin",
        r"C:\Program Files (x86)\PostgreSQL\16\bin",
        r"C:\Program Files (x86)\PostgreSQL\15\bin",
        r"C:\Program Files (x86)\PostgreSQL\14\bin",
        r"C:\Program Files (x86)\PostgreSQL\13\bin",
        r"C:\Program Files (x86)\PostgreSQL\12\bin",
    ]
    
    # Buscar la carpeta bin de PostgreSQL
    pg_bin_path = None
    for path in postgres_paths:
        if os.path.exists(path) and os.path.isdir(path):
            pg_bin_path = path
            break
    
    if not pg_bin_path:
        print("No se pudo encontrar la carpeta bin de PostgreSQL.")
        return None
    
    print(f"Usando la carpeta bin de PostgreSQL en: {pg_bin_path}")
    
    # Crear un archivo batch para ejecutar pg_dump con flags mejorados
    batch_file = os.path.join(output_dir, f"temp_pgdump_{timestamp}.bat")
    with open(batch_file, 'w') as f:
        f.write(f'@echo off\n')
        f.write(f'set PGPASSWORD={db_config["password"]}\n')
        f.write(f'cd /d "{pg_bin_path}"\n')
        f.write(f'pg_dump.exe --host={db_config["host"]} --port={db_config["port"]} ')
        f.write(f'--username={db_config["user"]} --dbname={db_config["database"]} ')
        f.write(f'--format=plain --no-owner --no-privileges --no-acl --if-exists --clean --encoding=UTF8 --no-comments > "{backup_path}"\n')
        f.write(f'echo Backup completado en {backup_path}\n')
    
    try:
        # Ejecutar el archivo batch
        print(f"Ejecutando archivo batch para pg_dump: {batch_file}")
        process = subprocess.run(batch_file, shell=True, check=True)
        
        # Eliminar el archivo batch temporal
        os.remove(batch_file)
        
        if os.path.exists(backup_path) and os.path.getsize(backup_path) > 0:
            # Limpiar el archivo de comandos problemáticos
            clean_backup_file(backup_path)
            print(f"Backup creado exitosamente: {backup_path}")
            return backup_path
        else:
            print(f"El archivo de backup no se creó correctamente.")
            return None

    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el archivo batch: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al crear el backup: {e}")
        return None
    finally:
        # Asegurarse de eliminar el archivo batch temporal
        if os.path.exists(batch_file):
            try:
                os.remove(batch_file)
            except:
                pass

if __name__ == "__main__":
    # Configuración de la base de datos desde variables de entorno
    db_config = {
        'host': os.getenv('DB_HOST', 'host.docker.internal'),  # Para Docker usa host.docker.internal
        'database': os.getenv('DB_NAME', 'gestion_dato_db'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', '1234'),
        'port': os.getenv('DB_PORT', '5432')
    }

    print(f"Configuración de base de datos:")
    print(f"  Host: {db_config['host']}")
    print(f"  Database: {db_config['database']}")
    print(f"  User: {db_config['user']}")
    print(f"  Port: {db_config['port']}")
    
    # Directorio para guardar los backups
    backup_dir = "backups"
    
    # Intentar diferentes métodos para realizar el backup
    print("Intentando crear backup con pg_dump...")
    backup_path = create_postgres_backup(db_config, backup_dir)
    
    # Si pg_dump falló, intentar con el método de comandos específicos para Windows
    if not backup_path and platform.system() == "Windows":
        print("\nEl método pg_dump falló, intentando con método de batch de Windows...")
        backup_path = backup_using_custom_commands(db_config, backup_dir)
    
    # Si ambos métodos anteriores fallan, intentar con psycopg2
    if not backup_path:
        print("\nLos métodos anteriores fallaron, intentando con psycopg2...")
        backup_path = create_backup_with_psycopg2(db_config, backup_dir)
    
    if backup_path:
        print(f"\nBackup creado exitosamente: {backup_path}")
    else:
        print("\nTodos los métodos de backup fallaron. Por favor, verifica la instalación de PostgreSQL.")
    
    # Si se proporcionó un archivo de backup para restaurar
    if len(sys.argv) > 1 and sys.argv[1] == "--restore" and len(sys.argv) > 2:
        restore_file = sys.argv[2]
        restore_postgres_backup(db_config, restore_file)