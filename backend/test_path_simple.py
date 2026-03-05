#!/usr/bin/env python3
"""
Script de prueba simple para verificar la conversión de rutas (sin Django)
"""

def linux_to_windows_path(linux_path):
    """Copia de la función para pruebas"""
    if not linux_path:
        return linux_path

    if not isinstance(linux_path, str):
        return linux_path

    if not linux_path.startswith('/mnt/repositorio'):
        return linux_path

    windows_path = linux_path.replace('/mnt/repositorio', r'\\repositorio\DirGesCat')
    windows_path = windows_path.replace('/', '\\')

    return windows_path

# Pruebas
print("=" * 80)
print("PRUEBAS DE CONVERSIÓN DE RUTAS")
print("=" * 80)
print()

test_cases = [
    ('/mnt/repositorio/2510SP/H_Informacion_Consulta',
     r'\\repositorio\DirGesCat\2510SP\H_Informacion_Consulta'),

    ('/mnt/repositorio/2510SP/H_Informacion_Consulta/Sub_Proy/documento.pdf',
     r'\\repositorio\DirGesCat\2510SP\H_Informacion_Consulta\Sub_Proy\documento.pdf'),

    ('Sin ruta', 'Sin ruta'),
    ('Sin directorio', 'Sin directorio'),
    (None, None),
]

todos_ok = True
for i, (input_path, expected) in enumerate(test_cases, 1):
    resultado = linux_to_windows_path(input_path)
    ok = resultado == expected
    status = "✅ OK" if ok else "❌ FAIL"

    if not ok:
        todos_ok = False

    print(f"Test {i}: {status}")
    print(f"  Input:    {repr(input_path)}")
    print(f"  Expected: {repr(expected)}")
    print(f"  Got:      {repr(resultado)}")
    print()

print("=" * 80)
if todos_ok:
    print("✅ TODAS LAS PRUEBAS PASARON")
else:
    print("❌ ALGUNAS PRUEBAS FALLARON")
print("=" * 80)
