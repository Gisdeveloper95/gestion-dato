#!/bin/bash
# ============================================================================
# SCRIPT PARA DETENER SERVICIOS
# ============================================================================
# Detiene todos los servicios de la aplicación de forma segura
# Uso: sudo bash stop.sh
# ============================================================================

set -e  # Detener en caso de error

echo "======================================"
echo "🛑 DETENIENDO SERVICIOS"
echo "======================================"
echo ""

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ ERROR: Este script debe ejecutarse como root (sudo)"
    exit 1
fi

# Verificar que existe docker-compose.yml
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ ERROR: No se encontró docker-compose.yml"
    echo "   Asegúrate de ejecutar este script desde /home/sonia.eraso/server"
    exit 1
fi

# Verificar si hay servicios corriendo
echo "📋 Verificando servicios actuales..."
if ! docker compose ps | grep -q "Up"; then
    echo "⚠️  No hay servicios en ejecución"
    docker compose ps
    echo ""
    echo "✅ Nada que detener"
    exit 0
fi

# Mostrar servicios que se van a detener
echo ""
echo "📋 Servicios que se van a detener:"
docker compose ps
echo ""

# Opción para detener con confirmación
read -p "¿Continuar con la detención? (s/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "❌ Operación cancelada"
    exit 0
fi

# Detener servicios
echo ""
echo "🛑 Deteniendo servicios de forma ordenada..."
echo "   1. Deteniendo frontend..."
docker compose stop frontend 2>/dev/null || true

echo "   2. Deteniendo nginx..."
docker compose stop nginx-proxy 2>/dev/null || true

echo "   3. Deteniendo backend..."
docker compose stop backend 2>/dev/null || true

echo "   4. Deteniendo base de datos..."
docker compose stop postgres 2>/dev/null || true

# Detener cualquier otro servicio
echo "   5. Verificando otros servicios..."
docker compose down

echo ""
echo "======================================"
echo "✅ SERVICIOS DETENIDOS CORRECTAMENTE"
echo "======================================"
echo ""

# Verificar que todo está detenido
if docker compose ps | grep -q "Up"; then
    echo "⚠️  Algunos servicios aún están corriendo:"
    docker compose ps
    echo ""
    echo "Para forzar la detención:"
    echo "   sudo docker compose down --remove-orphans"
else
    echo "✅ Todos los servicios están detenidos"
fi

echo ""
echo "🔧 Para volver a iniciar:"
echo "   sudo bash start.sh"
echo ""
echo "🔧 Para reinstalar desde cero:"
echo "   sudo bash install.sh"
echo ""
