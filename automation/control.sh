#!/bin/bash
# ==============================================
# AUTOMATION SYSTEM - CONTROL (DOCKER)
# ==============================================

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Cargar .env
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

# Determinar comando de docker-compose
if docker compose version &>/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# ==============================================
# Funciones
# ==============================================

show_help() {
    echo -e "${BLUE}AUTOMATION SYSTEM - CONTROL DOCKER${NC}"
    echo ""
    echo "Uso: $0 <comando> [opciones]"
    echo ""
    echo "Comandos:"
    echo "  start       - Iniciar contenedores"
    echo "  stop        - Detener contenedores"
    echo "  restart     - Reiniciar contenedores"
    echo "  status      - Ver estado de contenedores"
    echo "  logs        - Ver logs (usa -f para seguir)"
    echo "  build       - Reconstruir imagenes"
    echo "  test        - Probar acceso al NAS desde Docker"
    echo "  run <script> - Ejecutar script manualmente"
    echo "  cleanup     - Ejecutar limpieza de BD"
    echo "  shell       - Abrir shell en contenedor"
    echo ""
    echo "Ejemplos:"
    echo "  $0 start"
    echo "  $0 logs -f"
    echo "  $0 run Script_INSUMOS_Linux.py"
    echo "  $0 shell"
}

cmd_start() {
    echo -e "${BLUE}Iniciando contenedores...${NC}"
    $COMPOSE_CMD up -d
    echo -e "${GREEN}OK${NC} Contenedores iniciados"
    sleep 2
    cmd_status
}

cmd_stop() {
    echo -e "${BLUE}Deteniendo contenedores...${NC}"
    $COMPOSE_CMD down
    echo -e "${GREEN}OK${NC} Contenedores detenidos"
}

cmd_restart() {
    echo -e "${BLUE}Reiniciando contenedores...${NC}"
    $COMPOSE_CMD restart
    echo -e "${GREEN}OK${NC} Contenedores reiniciados"
    sleep 2
    cmd_status
}

cmd_status() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  ESTADO DE CONTENEDORES${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""

    $COMPOSE_CMD ps

    echo ""
    echo -e "${YELLOW}Ultimos logs scheduler:${NC}"
    $COMPOSE_CMD logs --tail=5 scheduler 2>/dev/null || echo "  (sin logs)"

    echo ""
    echo -e "${YELLOW}Ultimos logs telegram_bot:${NC}"
    $COMPOSE_CMD logs --tail=5 telegram_bot 2>/dev/null || echo "  (sin logs)"
}

cmd_logs() {
    # Quitar 'logs' de los argumentos
    shift
    if [ $# -eq 0 ]; then
        $COMPOSE_CMD logs --tail=50
    else
        $COMPOSE_CMD logs "$@"
    fi
}

cmd_build() {
    echo -e "${BLUE}Reconstruyendo imagenes...${NC}"
    $COMPOSE_CMD build --no-cache
    echo -e "${GREEN}OK${NC} Imagenes reconstruidas"
}

cmd_test() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  PRUEBAS DEL SISTEMA${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""

    # Test 1: Acceso NAS
    echo -e "${YELLOW}[1] Acceso al NAS desde Docker:${NC}"
    if $COMPOSE_CMD run --rm scheduler ls -la /netapp/2510SP/H_Informacion_Consulta/Sub_Proy 2>/dev/null | head -5; then
        echo -e "  ${GREEN}OK${NC}"
    else
        echo -e "  ${RED}ERROR - No se puede acceder al NAS${NC}"
    fi

    echo ""

    # Test 2: Base de datos
    echo -e "${YELLOW}[2] Conexion a PostgreSQL:${NC}"
    $COMPOSE_CMD run --rm scheduler python -c "
import os
import psycopg2
try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT', 5432)
    )
    cur = conn.cursor()
    cur.execute('SELECT version()')
    print(f'  PostgreSQL: {cur.fetchone()[0][:60]}...')
    conn.close()
    print('  OK')
except Exception as e:
    print(f'  ERROR: {e}')
    exit(1)
" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}OK${NC}"
    else
        echo -e "  ${RED}ERROR${NC}"
    fi

    echo ""

    # Test 3: Telegram API
    echo -e "${YELLOW}[3] Telegram API:${NC}"
    RESPONSE=$(curl -s "https://api.telegram.org/bot$TELEGRAM_TOKEN/getMe")
    if echo "$RESPONSE" | grep -q '"ok":true'; then
        BOT_NAME=$(echo "$RESPONSE" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
        echo -e "  Bot: @$BOT_NAME"
        echo -e "  ${GREEN}OK${NC}"
    else
        echo -e "  ${RED}ERROR${NC}"
    fi

    echo ""

    # Test 4: Imports Python
    echo -e "${YELLOW}[4] Modulos Python:${NC}"
    $COMPOSE_CMD run --rm scheduler python -c "
modules = ['psycopg2', 'telegram', 'schedule', 'psutil', 'dotenv', 'requests']
for mod in modules:
    try:
        __import__(mod)
        print(f'  {mod}: OK')
    except ImportError as e:
        print(f'  {mod}: FAIL - {e}')
" 2>/dev/null

    echo ""
}

cmd_run() {
    SCRIPT_NAME="$1"

    if [ -z "$SCRIPT_NAME" ]; then
        echo -e "${RED}ERROR: Especifica el script a ejecutar${NC}"
        echo ""
        echo "Uso: $0 run <script.py>"
        echo ""
        echo "Scripts disponibles:"
        ls -1 scripts/*.py 2>/dev/null | sed 's|scripts/||' | sed 's|^|  |'
        exit 1
    fi

    # Verificar que existe localmente
    if [ ! -f "scripts/$SCRIPT_NAME" ]; then
        echo -e "${RED}ERROR: Script no encontrado: scripts/$SCRIPT_NAME${NC}"
        exit 1
    fi

    echo -e "${BLUE}Ejecutando $SCRIPT_NAME en Docker...${NC}"
    echo ""

    # Ejecutar en contenedor temporal
    $COMPOSE_CMD run --rm scheduler python /app/scripts/"$SCRIPT_NAME"
}

cmd_cleanup() {
    echo -e "${BLUE}Ejecutando limpieza de BD...${NC}"
    $COMPOSE_CMD --profile cleanup run --rm db_cleaner
}

cmd_shell() {
    CONTAINER="${1:-scheduler}"
    echo -e "${BLUE}Abriendo shell en automation_$CONTAINER...${NC}"

    if docker ps -q -f name=automation_$CONTAINER 2>/dev/null | grep -q .; then
        docker exec -it automation_$CONTAINER /bin/bash
    else
        echo -e "${YELLOW}Contenedor no esta corriendo, iniciando temporal...${NC}"
        $COMPOSE_CMD run --rm $CONTAINER /bin/bash
    fi
}

# ==============================================
# Main
# ==============================================

case "${1:-help}" in
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    restart)
        cmd_restart
        ;;
    status)
        cmd_status
        ;;
    logs)
        cmd_logs "$@"
        ;;
    build)
        cmd_build
        ;;
    test)
        cmd_test
        ;;
    run)
        cmd_run "$2"
        ;;
    cleanup)
        cmd_cleanup
        ;;
    shell)
        cmd_shell "$2"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Comando desconocido: $1${NC}"
        show_help
        exit 1
        ;;
esac
