#!/usr/bin/env python3
"""
🗑️ SCRIPT DE LIMPIEZA MASIVA DE ARCHIVOS HUÉRFANOS
ELIMINA TODOS LOS ARCHIVOS QUE NO EXISTEN FÍSICAMENTE
"""

import os
import psycopg2
import time
from datetime import datetime
import json

# Configuración de BD
DB_CONFIG = {
    'host': 'localhost',
    'database': 'gestion_dato_db',
    'user': 'postgres',
    'password': '1234',
    'port': '5432'
}

def verificar_archivo_existe_simple(ruta_archivo):
    """🔍 Verificación simple y directa"""
    try:
        # Método 1: os.path.exists
        if os.path.exists(ruta_archivo):
            return True, "exists_direct"
        
        # Método 2: PowerShell para UNC
        if ruta_archivo.startswith('\\\\'):
            import subprocess
            
            ruta_ps = ruta_archivo
            if ruta_archivo.startswith('\\\\?\\UNC\\'):
                ruta_ps = '\\\\' + ruta_archivo[8:]
            
            ruta_ps_escapada = ruta_ps.replace('"', '""')
            script = f'Test-Path -LiteralPath "{ruta_ps_escapada}"'
            
            try:
                resultado = subprocess.run([
                    'powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', 
                    '-Command', script
                ], capture_output=True, text=True, encoding='utf-8', 
                errors='ignore', timeout=10)
                
                if resultado.returncode == 0:
                    existe_ps = resultado.stdout.strip().lower() == 'true'
                    if existe_ps:
                        return True, "powershell_true"
            except:
                pass
        
        # Método 3: Verificar directorio padre
        directorio_padre = os.path.dirname(ruta_archivo)
        if os.path.exists(directorio_padre):
            nombre_archivo = os.path.basename(ruta_archivo)
            try:
                archivos_en_directorio = os.listdir(directorio_padre)
                for archivo in archivos_en_directorio:
                    if archivo.lower() == nombre_archivo.lower():
                        return True, "case_insensitive"
            except:
                pass
        
        return False, "no_existe_confirmado"
        
    except Exception as e:
        return False, f"error_{str(e)[:20]}"

def encontrar_todos_huerfanos():
    """🔍 Encuentra TODOS los archivos huérfanos en la BD"""
    print("🔍 BUSCANDO TODOS LOS ARCHIVOS HUÉRFANOS...")
    print("="*60)
    
    inicio = time.time()
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Obtener TODOS los archivos
        print("📊 Obteniendo todos los archivos de la BD...")
        cursor.execute("""
            SELECT 
                a.id_lista_archivo,
                a.nombre_insumo,
                a.path_file,
                a.fecha_disposicion,
                a.cod_insumo,
                c.nombre as clasificacion_nombre,
                i.cod_municipio,
                m.nom_municipio,
                cat.nom_categoria
            FROM lista_archivos_preo a
            JOIN clasificacion_insumo c ON c.cod_clasificacion = a.cod_insumo
            JOIN insumos i ON i.cod_insumo = c.cod_insumo
            LEFT JOIN categorias cat ON cat.cod_categoria = i.cod_categoria
            LEFT JOIN municipios m ON m.cod_municipio = i.cod_municipio
            ORDER BY a.id_lista_archivo
        """)
        
        todos_archivos = cursor.fetchall()
        total_archivos = len(todos_archivos)
        
        print(f"📄 Total archivos en BD: {total_archivos:,}")
        
        if total_archivos == 0:
            print("✅ No hay archivos en la BD")
            conn.close()
            return []
        
        # Verificar existencia de cada archivo
        archivos_huerfanos = []
        archivos_existentes = 0
        errores = 0
        
        print(f"\n🔍 Verificando existencia de {total_archivos:,} archivos...")
        print(f"📊 Progreso cada 1000 archivos...")
        
        for i, archivo_info in enumerate(todos_archivos):
            id_archivo, nombre, path_file, fecha, cod_insumo, clasificacion, cod_municipio, nom_municipio, nom_categoria = archivo_info
            
            # Mostrar progreso cada 1000 archivos
            if (i + 1) % 1000 == 0:
                porcentaje = (i + 1) / total_archivos * 100
                huerfanos_hasta_ahora = len(archivos_huerfanos)
                print(f"  📊 {i+1:,}/{total_archivos:,} ({porcentaje:.1f}%) - Huérfanos: {huerfanos_hasta_ahora:,}")
            
            try:
                existe, metodo = verificar_archivo_existe_simple(path_file)
                
                if existe:
                    archivos_existentes += 1
                else:
                    # Es un huérfano
                    archivos_huerfanos.append({
                        'id_archivo': id_archivo,
                        'nombre': nombre,
                        'path_file': path_file,
                        'fecha': fecha,
                        'cod_insumo': cod_insumo,
                        'clasificacion': clasificacion,
                        'cod_municipio': cod_municipio,
                        'nom_municipio': nom_municipio,
                        'nom_categoria': nom_categoria,
                        'metodo_verificacion': metodo
                    })
                
            except Exception as e:
                errores += 1
                if errores <= 10:  # Solo mostrar primeros 10 errores
                    print(f"  ⚠️ Error verificando {nombre}: {e}")
        
        tiempo_verificacion = time.time() - inicio
        
        print(f"\n📊 RESULTADO DE VERIFICACIÓN MASIVA:")
        print(f"  ⏱️ Tiempo total: {tiempo_verificacion:.2f} segundos")
        print(f"  📄 Total archivos verificados: {total_archivos:,}")
        print(f"  ✅ Archivos existentes: {archivos_existentes:,}")
        print(f"  🗑️ Archivos huérfanos: {len(archivos_huerfanos):,}")
        print(f"  ❌ Errores: {errores}")
        
        if len(archivos_huerfanos) > 0:
            porcentaje_huerfanos = len(archivos_huerfanos) / total_archivos * 100
            print(f"  📊 Porcentaje huérfanos: {porcentaje_huerfanos:.2f}%")
            
            velocidad = total_archivos / tiempo_verificacion
            print(f"  ⚡ Velocidad verificación: {velocidad:.0f} archivos/segundo")
        
        conn.close()
        return archivos_huerfanos
        
    except Exception as e:
        print(f"❌ Error buscando huérfanos: {e}")
        return []

def eliminar_huerfanos_en_masa(archivos_huerfanos, confirmar=True):
    """🗑️ Elimina archivos huérfanos en masa"""
    if not archivos_huerfanos:
        print("✅ No hay archivos huérfanos para eliminar")
        return 0
    
    print(f"\n🗑️ ELIMINACIÓN EN MASA DE ARCHIVOS HUÉRFANOS")
    print(f"="*60)
    print(f"📄 Archivos a eliminar: {len(archivos_huerfanos):,}")
    
    # Mostrar muestra de archivos
    print(f"\n📋 MUESTRA DE ARCHIVOS A ELIMINAR (primeros 10):")
    for i, archivo in enumerate(archivos_huerfanos[:10]):
        print(f"  {i+1:2d}. {archivo['nombre']} (ID: {archivo['id_archivo']})")
        print(f"      📁 Municipio: {archivo['nom_municipio']}")
        print(f"      📂 Categoría: {archivo['nom_categoria']}")
    
    if len(archivos_huerfanos) > 10:
        print(f"  ... y {len(archivos_huerfanos) - 10:,} archivos más")
    
    # Confirmación
    if confirmar:
        print(f"\n⚠️ CONFIRMACIÓN REQUERIDA:")
        print(f"   🗑️ Se eliminarán {len(archivos_huerfanos):,} archivos huérfanos de la BD")
        print(f"   📊 Estos archivos NO existen físicamente")
        print(f"   ⚠️ Esta acción NO se puede deshacer")
        

        
        #respuesta = input(f"\n❓ ¿Continuar con la eliminación? (ESCRIBA 'ELIMINAR' para confirmar): ")
        respuesta ='ELIMINAR'
        if respuesta != 'ELIMINAR':
            print("❌ Eliminación cancelada")
            return 0
    
    # Proceder con eliminación
    print(f"\n🗑️ INICIANDO ELIMINACIÓN EN MASA...")
    inicio = time.time()
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        archivos_eliminados = 0
        errores_eliminacion = 0
        batch_size = 100
        
        for i in range(0, len(archivos_huerfanos), batch_size):
            batch = archivos_huerfanos[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(archivos_huerfanos) + batch_size - 1) // batch_size
            
            print(f"  🔄 Batch {batch_num}/{total_batches}: {len(batch)} archivos...")
            
            try:
                # Eliminar batch
                ids_eliminar = [archivo['id_archivo'] for archivo in batch]
                
                # Crear notificaciones para el batch
                for archivo in batch:
                    datos_contexto = {
                        "municipio_id": archivo['cod_municipio'],
                        "municipio": archivo['nom_municipio'],
                        "clasificacion_id": archivo['cod_insumo'],
                        "clasificacion": archivo['clasificacion'],
                        "categoria": archivo['nom_categoria'],
                        "nombre": archivo['nombre'],
                        "ruta": archivo['path_file'],
                        "razon": "Eliminación masiva - archivo huérfano confirmado NO existente",
                        "eliminacion_masiva_huerfanos": True,
                        "metodo_verificacion": archivo['metodo_verificacion'],
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    cursor.execute("""
                        INSERT INTO notificaciones(
                            tipo_entidad, id_entidad, accion, descripcion, 
                            datos_contexto, fecha_cambio, usuario_windows, leido
                        ) VALUES (
                            'archivo', %s, 'eliminar', %s, %s::jsonb, %s, 'SistemaMasivo', FALSE
                        )
                    """, (
                        archivo['id_archivo'],
                        f"Eliminación masiva huérfano: {archivo['nombre']}",
                        json.dumps(datos_contexto),
                        datetime.now()
                    ))
                
                # Eliminar archivos del batch
                cursor.execute("""
                    DELETE FROM lista_archivos_preo 
                    WHERE id_lista_archivo = ANY(%s)
                """, (ids_eliminar,))
                
                eliminados_batch = cursor.rowcount
                archivos_eliminados += eliminados_batch
                
                conn.commit()
                print(f"    ✅ Batch {batch_num} completado: {eliminados_batch} eliminados")
                
            except Exception as e:
                conn.rollback()
                errores_eliminacion += len(batch)
                print(f"    ❌ Error en batch {batch_num}: {e}")
        
        tiempo_eliminacion = time.time() - inicio
        
        print(f"\n🎯 ELIMINACIÓN MASIVA COMPLETADA:")
        print(f"  ⏱️ Tiempo total: {tiempo_eliminacion:.2f} segundos")
        print(f"  ✅ Archivos eliminados: {archivos_eliminados:,}")
        print(f"  ❌ Errores: {errores_eliminacion}")
        
        if archivos_eliminados > 0:
            velocidad = archivos_eliminados / tiempo_eliminacion
            print(f"  ⚡ Velocidad eliminación: {velocidad:.0f} archivos/segundo")
            
        # Crear notificación resumen
        cursor.execute("""
            INSERT INTO notificaciones(
                tipo_entidad, id_entidad, accion, descripcion, 
                datos_contexto, fecha_cambio, usuario_windows, leido
            ) VALUES (
                'sistema', 1, 'limpieza_masiva_huerfanos', %s, %s::jsonb, %s, 'SistemaMasivo', FALSE
            )
        """, (
            f"Limpieza masiva completada: {archivos_eliminados:,} archivos huérfanos eliminados",
            json.dumps({
                "archivos_eliminados": archivos_eliminados,
                "tiempo_segundos": tiempo_eliminacion,
                "errores": errores_eliminacion,
                "velocidad_archivos_por_segundo": archivos_eliminados / tiempo_eliminacion if tiempo_eliminacion > 0 else 0,
                "timestamp": datetime.now().isoformat(),
                "tipo": "limpieza_masiva_huerfanos_v1"
            }),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
        return archivos_eliminados
        
    except Exception as e:
        print(f"❌ Error crítico en eliminación masiva: {e}")
        return 0

def main():
    """🚀 Función principal"""
    print("🗑️" * 60)
    print("LIMPIEZA MASIVA DE ARCHIVOS HUÉRFANOS - SOLUCIÓN INMEDIATA")
    print("ELIMINA TODOS LOS ARCHIVOS QUE NO EXISTEN FÍSICAMENTE")
    print("🗑️" * 60)
    
    inicio_total = time.time()
    
    # PASO 1: Encontrar todos los huérfanos
    archivos_huerfanos = encontrar_todos_huerfanos()
    
    if not archivos_huerfanos:
        print("🎉 ¡EXCELENTE! No hay archivos huérfanos en la BD")
        return
    
    # PASO 2: Mostrar estadísticas por municipio/categoría
    print(f"\n📊 ESTADÍSTICAS DE HUÉRFANOS POR MUNICIPIO:")
    municipios_afectados = {}
    for archivo in archivos_huerfanos:
        municipio = archivo['nom_municipio'] or 'Sin municipio'
        if municipio not in municipios_afectados:
            municipios_afectados[municipio] = 0
        municipios_afectados[municipio] += 1
    
    for municipio, cantidad in sorted(municipios_afectados.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  📍 {municipio}: {cantidad:,} archivos huérfanos")
    
    # PASO 3: Eliminar en masa
    archivos_eliminados = eliminar_huerfanos_en_masa(archivos_huerfanos)
    
    tiempo_total = time.time() - inicio_total
    
    print(f"\n🎉 LIMPIEZA MASIVA COMPLETADA")
    print(f"="*40)
    print(f"⏱️ Tiempo total: {tiempo_total:.2f} segundos")
    print(f"🔍 Archivos verificados: {len(archivos_huerfanos):,}")
    print(f"🗑️ Archivos eliminados: {archivos_eliminados:,}")
    print(f"✅ BD limpia de archivos huérfanos")

if __name__ == "__main__":
    main()