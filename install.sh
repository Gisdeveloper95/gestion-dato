#!/bin/bash
# ============================================================================
# SCRIPT DE INSTALACIÓN COMPLETA DESDE CERO
# ============================================================================
# Este script realiza una instalación limpia y completa de la aplicación
# Uso: sudo bash install.sh
# ============================================================================

set -e  # Detener en caso de error

echo "======================================"
echo "🚀 INSTALACIÓN COMPLETA DESDE CERO"
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

# Verificar que existe .env
if [ ! -f ".env" ]; then
    echo "❌ ERROR: No se encontró el archivo .env"
    echo "   Crea el archivo .env con las configuraciones necesarias"
    exit 1
fi

# Paso 1: Detener todos los contenedores
echo "📦 Paso 1/6: Deteniendo contenedores existentes..."
docker compose down 2>/dev/null || true
echo "✅ Contenedores detenidos"
echo ""

# Paso 2: Limpiar sistema Docker completo
echo "🧹 Paso 2/6: Limpiando sistema Docker..."
echo "   - Eliminando contenedores antiguos"
echo "   - Eliminando imágenes sin usar"
echo "   - Eliminando volúmenes huérfanos"
echo "   - Eliminando redes sin usar"
docker system prune -a -f --volumes
echo "✅ Sistema Docker limpiado"
echo ""

# Paso 3: Verificar puertos libres
echo "🔍 Paso 3/6: Verificando puertos necesarios..."
PORTS_IN_USE=""
for PORT in 80 443 5432 5173 8000; do
    if netstat -tuln 2>/dev/null | grep -q ":$PORT " || ss -tuln 2>/dev/null | grep -q ":$PORT "; then
        PORTS_IN_USE="$PORTS_IN_USE $PORT"
    fi
done

if [ -n "$PORTS_IN_USE" ]; then
    echo "⚠️  ADVERTENCIA: Los siguientes puertos están en uso:$PORTS_IN_USE"
    echo "   Si hay problemas, detén los servicios que usan estos puertos"
    echo ""
else
    echo "✅ Todos los puertos necesarios están disponibles"
    echo ""
fi

# Paso 4: Build completo sin caché
echo "🔨 Paso 4/6: Construyendo imágenes desde cero..."
echo "   Esto puede tardar varios minutos..."
docker compose build --no-cache --pull
echo "✅ Imágenes construidas exitosamente"
echo ""

# Paso 5: Iniciar servicios
echo "🚀 Paso 5/6: Iniciando servicios..."
docker compose up -d
echo "✅ Servicios iniciados"
echo ""

# Paso 6: Esperar y verificar
echo "⏳ Paso 6/6: Esperando que los servicios inicien..."
sleep 10

echo ""
echo "🔍 Verificando estado de los servicios..."
docker compose ps
echo ""

# Verificar logs de errores críticos
echo "📋 Verificando logs por errores..."
if docker compose logs backend 2>&1 | grep -i "error\|exception\|failed" | tail -5 | grep -q .; then
    echo "⚠️  Se detectaron algunos errores en backend. Revisa los logs:"
    echo "   sudo docker compose logs backend"
else
    echo "✅ Backend sin errores críticos"
fi

if docker compose logs frontend 2>&1 | grep -i "error\|failed" | tail -5 | grep -q .; then
    echo "⚠️  Se detectaron algunos errores en frontend. Revisa los logs:"
    echo "   sudo docker compose logs frontend"
else
    echo "✅ Frontend sin errores críticos"
fi

echo ""
echo "======================================"
echo "✅ INSTALACIÓN COMPLETADA"
echo "======================================"
echo ""
echo "📍 Acceso a la aplicación:"
echo "   • Por IP (HTTP):     http://172.19.3.196"
echo "   • Por dominio (HTTPS): https://gestiondato.duckdns.org"
echo ""
echo "🔧 Comandos útiles:"
echo "   • Ver logs:          sudo docker compose logs -f [servicio]"
echo "   • Ver estado:        sudo docker compose ps"
echo "   • Detener:           sudo bash stop.sh"
echo "   • Reiniciar:         sudo bash start.sh"
echo ""
echo "📚 Servicios disponibles:"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
echo ""
