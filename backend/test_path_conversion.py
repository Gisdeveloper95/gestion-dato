#!/usr/bin/env python3
"""
Script de prueba para verificar la conversión de rutas Linux a Windows
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, '/home/sonia.eraso/server/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.path_utils import linux_to_windows_path, windows_to_linux_path

def test_conversiones():
    """Prueba las conversiones de rutas"""

    print("=" * 80)
    print("PRUEBAS DE CONVERSIÓN DE RUTAS LINUX -> WINDOWS")
    print("=" * 80)
    print()

    # Casos de prueba
    test_cases = [
        # (input_linux, expected_windows)
        ('/mnt/repositorio/2510SP/H_Informacion_Consulta',
         r'\\repositorio\DirGesCat\2510SP\H_Informacion_Consulta'),

        ('/mnt/repositorio/2510SP/H_Informacion_Consulta/Sub_Proy/01_actualiz_catas/17/174/PGN/03_post/05_prod_catas/02_memo_tecn_actualiz/documento.pdf',
         r'\\repositorio\DirGesCat\2510SP\H_Informacion_Consulta\Sub_Proy\01_actualiz_catas\17\174\PGN\03_post\05_prod_catas\02_memo_tecn_actualiz\documento.pdf'),

        ('Sin ruta', 'Sin ruta'),
        ('Sin directorio', 'Sin directorio'),
        (None, None),
        ('', ''),

        # Ruta que ya está en formato Windows (no debería cambiar)
        (r'\\repositorio\DirGesCat\2510SP\test', r'\\repositorio\DirGesCat\2510SP\test'),
    ]

    print("Pruebas de conversión Linux -> Windows:")
    print("-" * 80)

    todos_ok = True
    for i, (linux_path, expected) in enumerate(test_cases, 1):
        resultado = linux_to_windows_path(linux_path)
        status = "✅ OK" if resultado == expected else "❌ FAIL"

        if resultado != expected:
            todos_ok = False

        print(f"\nTest {i}: {status}")
        print(f"  Input:    {repr(linux_path)}")
        print(f"  Expected: {repr(expected)}")
        print(f"  Got:      {repr(resultado)}")

    print()
    print("=" * 80)

    if todos_ok:
        print("✅ TODAS LAS PRUEBAS PASARON CORRECTAMENTE")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")

    print("=" * 80)
    print()

    # Prueba inversa
    print("=" * 80)
    print("PRUEBA INVERSA: WINDOWS -> LINUX")
    print("=" * 80)
    print()

    win_to_linux_tests = [
        (r'\\repositorio\DirGesCat\2510SP\H_Informacion_Consulta',
         '/mnt/repositorio/2510SP/H_Informacion_Consulta'),
    ]

    for win_path, expected_linux in win_to_linux_tests:
        resultado = windows_to_linux_path(win_path)
        status = "✅ OK" if resultado == expected_linux else "❌ FAIL"

        print(f"Test: {status}")
        print(f"  Input:    {repr(win_path)}")
        print(f"  Expected: {repr(expected_linux)}")
        print(f"  Got:      {repr(resultado)}")

    print()
    print("=" * 80)

    return todos_ok

if __name__ == '__main__':
    try:
        success = test_conversiones()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
