#!/bin/bash
# Script para reiniciar el backend después de cambios en el código

echo "🔄 Reiniciando contenedor backend..."
sudo docker restart igac_backend

echo "⏳ Esperando 5 segundos para que el contenedor inicie..."
sleep 5

echo "✅ Verificando estado del contenedor..."
sudo docker ps | grep igac_backend

echo ""
echo "📋 Últimas 20 líneas del log del backend:"
sudo docker logs igac_backend --tail 20

echo ""
echo "✅ Reinicio completado!"
