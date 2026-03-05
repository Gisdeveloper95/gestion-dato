#!/bin/bash
# Muestra el estado completo del sistema de automatización

echo "📊 Estado del Sistema de Automatización"
echo "========================================"

# Estado de servicios systemd
echo -e "\n🔧 Servicios Systemd:"
echo "-------------------"

services=("gestion-scheduler" "gestion-telegram-bot" "gestion-db-cleanup.timer")

for service in "${services[@]}"; do
    status=$(sudo systemctl is-active "$service" 2>/dev/null || echo "inactive")
    if [ "$status" = "active" ]; then
        echo "  ✅ $service: ACTIVO"
    else
        echo "  ❌ $service: INACTIVO"
    fi
done

# Scripts en ejecución
echo -e "\n🐍 Scripts Python Activos:"
echo "-------------------------"
ps aux | grep -E "(Script_.*Linux\.py|scheduler\.py|telegram_bot\.py)" | grep -v grep | while read line; do
    script=$(echo $line | grep -oP "Script_\w+_Linux\.py|scheduler\.py|telegram_bot\.py")
    pid=$(echo $line | awk '{print $2}')
    echo "  • $script (PID: $pid)"
done

count=$(ps aux | grep -E "(Script_.*Linux\.py|scheduler\.py|telegram_bot\.py)" | grep -v grep | wc -l)
if [ "$count" -eq 0 ]; then
    echo "  (Ninguno en ejecución)"
fi

# Uso de recursos
echo -e "\n💻 Recursos del Sistema:"
echo "----------------------"
echo "  CPU: $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}')"
echo "  RAM: $(free -h | awk '/^Mem:/ {print $3 "/" $2 " (" $3/$2*100 "%)"}')"
echo "  Disco /: $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 ")"}')"

# NFS
if mountpoint -q /mnt/repositorio; then
    echo "  NFS /mnt/repositorio: $(df -h /mnt/repositorio | awk 'NR==2 {print $3 "/" $2 " (" $5 ")"}')"
else
    echo "  NFS /mnt/repositorio: ❌ NO MONTADO"
fi

# Últimos logs
echo -e "\n📝 Últimos Logs (5 líneas):"
echo "--------------------------"
if [ -f logs/scheduler.log ]; then
    echo "  [Scheduler]"
    tail -n 5 logs/scheduler.log | sed 's/^/    /'
fi

# Próxima ejecución programada
echo -e "\n⏰ Próximas Ejecuciones:"
echo "----------------------"
sudo systemctl list-timers gestion-* --no-pager | grep -v "^$" | tail -n +2

echo -e "\n========================================"
echo "Usa 'sudo journalctl -u gestion-scheduler -f' para logs en tiempo real"
