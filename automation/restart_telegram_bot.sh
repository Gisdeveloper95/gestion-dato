#!/bin/bash
# Script para reiniciar el bot de Telegram
# Uso: ./restart_telegram_bot.sh

echo "🔄 Reiniciando bot de Telegram..."
sudo systemctl restart gestion-telegram-bot.service

if [ $? -eq 0 ]; then
    sleep 2
    echo "✅ Bot reiniciado correctamente"
    echo ""
    echo "📊 Estado del servicio:"
    sudo systemctl status gestion-telegram-bot.service --no-pager -l
else
    echo "❌ Error al reiniciar el bot"
    exit 1
fi
