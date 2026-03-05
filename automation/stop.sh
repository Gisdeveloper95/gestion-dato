#!/bin/bash
# Detiene todos los servicios de automatización

echo "🛑 Deteniendo servicios de automatización..."

# Detener scheduler
echo "  → Deteniendo scheduler..."
sudo systemctl stop gestion-scheduler

# Detener bot de Telegram
echo "  → Deteniendo bot de Telegram..."
sudo systemctl stop gestion-telegram-bot

# Detener timer de limpieza
echo "  → Deteniendo timer de limpieza..."
sudo systemctl stop gestion-db-cleanup.timer

sleep 1

# Verificar que se detuvieron
echo -e "\n📊 Estado de servicios:"
sudo systemctl status gestion-scheduler --no-pager | grep "Active:" || echo "  ✓ Scheduler detenido"
sudo systemctl status gestion-telegram-bot --no-pager | grep "Active:" || echo "  ✓ Bot detenido"

echo -e "\n✅ Servicios detenidos."
