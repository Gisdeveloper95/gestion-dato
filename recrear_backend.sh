#!/bin/bash
# Script para recrear el contenedor backend con los nuevos volúmenes

echo "🔄 Recreando contenedor backend con nuevos volúmenes..."
cd /home/sonia.eraso/server

echo "📋 Parando contenedor actual..."
sudo docker-compose stop backend

echo "🗑️ Eliminando contenedor antiguo..."
sudo docker-compose rm -f backend

echo "🚀 Creando nuevo contenedor con volúmenes actualizados..."
sudo docker-compose up -d backend

echo "⏳ Esperando 10 segundos para que el contenedor inicie..."
sleep 10

echo "✅ Verificando estado del contenedor..."
sudo docker ps | grep igac_backend

echo ""
echo "📋 Últimas 30 líneas del log del backend:"
sudo docker logs igac_backend --tail 30

echo ""
echo "🔍 Verificando si /mnt/repositorio está montado:"
sudo docker exec igac_backend ls -la /mnt/repositorio 2>&1 | head -10

echo ""
echo "✅ Recreación completada!"
