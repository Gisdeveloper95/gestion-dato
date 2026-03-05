#!/bin/bash
# Inicia todos los servicios de automatización

echo "🚀 Iniciando servicios de automatización..."

# Iniciar scheduler
echo "  → Iniciando scheduler..."
sudo systemctl start gestion-scheduler

# Iniciar bot de Telegram
echo "  → Iniciando bot de Telegram..."
sudo systemctl start gestion-telegram-bot

# Iniciar timer de limpieza
echo "  → Habilitando timer de limpieza..."
sudo systemctl start gestion-db-cleanup.timer

sleep 2

# Verificar estado
echo -e "\n📊 Estado de servicios:"
sudo systemctl status gestion-scheduler --no-pager | grep "Active:"
sudo systemctl status gestion-telegram-bot --no-pager | grep "Active:"

echo -e "\n✅ Servicios iniciados. Usa ./status.sh para ver el estado completo."
