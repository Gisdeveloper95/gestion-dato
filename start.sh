#!/bin/bash
# ============================================================================
# SCRIPT PARA INICIAR SERVICIOS
# ============================================================================
# Inicia todos los servicios de la aplicación
# Uso: sudo bash start.sh
# ============================================================================

set -e  # Detener en caso de error

echo "======================================"
echo "🚀 INICIANDO SERVICIOS"
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

# Verificar estado actual
echo "📋 Verificando estado actual..."
if docker compose ps | grep -q "Up"; then
    echo "⚠️  Algunos servicios ya están ejecutándose:"
    docker compose ps
    echo ""
    read -p "¿Deseas reiniciarlos? (s/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "❌ Operación cancelada"
        exit 0
    fi
    echo "🔄 Deteniendo servicios actuales..."
    docker compose down
    echo ""
fi

# Iniciar servicios
echo "🚀 Iniciando todos los servicios..."
docker compose up -d

# Esperar que inicien
echo ""
echo "⏳ Esperando que los servicios inicien (10 segundos)..."
sleep 10

# Mostrar estado
echo ""
echo "======================================"
echo "✅ SERVICIOS INICIADOS"
echo "======================================"
echo ""
docker compose ps
echo ""

# Verificar servicios críticos
echo "🔍 Verificando servicios críticos..."
ERRORS=0

if ! docker compose ps | grep -q "postgres.*Up"; then
    echo "❌ ERROR: Base de datos (postgres) no está corriendo"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ Base de datos: OK"
fi

if ! docker compose ps | grep -q "backend.*Up"; then
    echo "❌ ERROR: Backend no está corriendo"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ Backend: OK"
fi

if ! docker compose ps | grep -q "frontend.*Up"; then
    echo "❌ ERROR: Frontend no está corriendo"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ Frontend: OK"
fi

if ! docker compose ps | grep -q "nginx-proxy.*Up"; then
    echo "❌ ERROR: Nginx no está corriendo"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ Nginx: OK"
fi

echo ""

if [ $ERRORS -gt 0 ]; then
    echo "⚠️  Se encontraron $ERRORS error(es)"
    echo "   Revisa los logs: sudo docker compose logs [servicio]"
    echo ""
    exit 1
fi

echo "======================================"
echo "✅ TODOS LOS SERVICIOS ESTÁN FUNCIONANDO"
echo "======================================"
echo ""
echo "📍 Acceso a la aplicación:"
echo "   • Por IP (HTTP):       http://172.19.3.196"
echo "   • Por dominio (HTTPS): https://gestiondato.duckdns.org"
echo ""
echo "🔧 Comandos útiles:"
echo "   • Ver logs:            sudo docker compose logs -f [servicio]"
echo "   • Ver estado:          sudo docker compose ps"
echo "   • Detener:             sudo bash stop.sh"
echo ""
