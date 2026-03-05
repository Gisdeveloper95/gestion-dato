#!/bin/bash
# ==============================================
# AUTOMATION SYSTEM - DIAGNOSTICO (DOCKER)
# ==============================================

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  AUTOMATION SYSTEM - DIAGNOSTICO DOCKER${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

ERRORS=0
WARNINGS=0

check_ok() {
    echo -e "  ${GREEN}[OK]${NC} $1"
}

check_fail() {
    echo -e "  ${RED}[FAIL]${NC} $1"
    ((ERRORS++))
}

check_warn() {
    echo -e "  ${YELLOW}[WARN]${NC} $1"
    ((WARNINGS++))
}

# Determinar comando de docker-compose
if docker compose version &>/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# ==============================================
# 1. DOCKER
# ==============================================
echo -e "${YELLOW}[1] DOCKER${NC}"

if command -v docker &>/dev/null; then
    DOCKER_VER=$(docker --version | cut -d' ' -f3 | tr -d ',')
    check_ok "Docker instalado: $DOCKER_VER"
else
    check_fail "Docker NO instalado"
fi

if docker info &>/dev/null 2>&1; then
    check_ok "Docker daemon corriendo"
else
    check_fail "Docker daemon NO disponible"
fi

if $COMPOSE_CMD version &>/dev/null 2>&1; then
    check_ok "Docker Compose disponible"
else
    check_fail "Docker Compose NO disponible"
fi

echo ""

# ==============================================
# 2. CONFIGURACION
# ==============================================
echo -e "${YELLOW}[2] CONFIGURACION${NC}"

if [ -f ".env" ]; then
    check_ok ".env existe"
    set -a
    source .env
    set +a
else
    check_fail ".env NO existe"
    echo -e "     Ejecuta: cp .env.example .env"
fi

if [ -n "$AUTOMATION_DIR" ]; then
    check_ok "AUTOMATION_DIR=$AUTOMATION_DIR"
else
    check_fail "AUTOMATION_DIR no definido"
fi

if [ -n "$REPOSITORY_PATH" ]; then
    check_ok "REPOSITORY_PATH=$REPOSITORY_PATH"
else
    check_fail "REPOSITORY_PATH no definido"
fi

if [ -n "$DB_HOST" ]; then
    check_ok "DB_HOST=$DB_HOST"
else
    check_fail "DB_HOST no definido"
fi

if [ -n "$TELEGRAM_TOKEN" ]; then
    TOKEN_MASKED="${TELEGRAM_TOKEN:0:10}...${TELEGRAM_TOKEN: -5}"
    check_ok "TELEGRAM_TOKEN=$TOKEN_MASKED"
else
    check_fail "TELEGRAM_TOKEN no definido"
fi

echo ""

# ==============================================
# 3. MONTAJE NAS (HOST)
# ==============================================
echo -e "${YELLOW}[3] MONTAJE NAS (HOST)${NC}"

if [ -d "$REPOSITORY_PATH" ]; then
    check_ok "Directorio existe: $REPOSITORY_PATH"

    # Verificar si esta montado
    if mount | grep -q "$REPOSITORY_PATH"; then
        MOUNT_INFO=$(mount | grep "$REPOSITORY_PATH" | head -1)
        check_ok "Montaje activo"
    else
        check_warn "No parece estar montado (puede ser bind mount)"
    fi

    # Verificar acceso (desde host, puede fallar)
    if ls "$REPOSITORY_PATH" &>/dev/null 2>&1; then
        check_ok "Acceso desde host: OK"
    else
        check_warn "Sin acceso desde host (Docker puede tener acceso)"
    fi
else
    check_fail "Directorio NO existe: $REPOSITORY_PATH"
fi

echo ""

# ==============================================
# 4. IMAGENES DOCKER
# ==============================================
echo -e "${YELLOW}[4] IMAGENES DOCKER${NC}"

if [ -f "Dockerfile" ]; then
    check_ok "Dockerfile existe"
else
    check_fail "Dockerfile NO existe"
fi

if [ -f "docker-compose.yml" ]; then
    check_ok "docker-compose.yml existe"
else
    check_fail "docker-compose.yml NO existe"
fi

# Verificar si imagen existe
IMAGE_NAME=$(basename "$SCRIPT_DIR")
if docker images | grep -q "$IMAGE_NAME"; then
    check_ok "Imagen Docker construida"
else
    check_warn "Imagen Docker no construida"
    echo -e "     Ejecuta: ./install.sh"
fi

echo ""

# ==============================================
# 5. CONTENEDORES
# ==============================================
echo -e "${YELLOW}[5] CONTENEDORES${NC}"

CONTAINERS=("automation_scheduler" "automation_telegram_bot")
for container in "${CONTAINERS[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        STATUS=$(docker inspect -f '{{.State.Status}}' "$container" 2>/dev/null)
        UPTIME=$(docker inspect -f '{{.State.StartedAt}}' "$container" 2>/dev/null | cut -d'T' -f1)
        check_ok "$container: $STATUS (desde $UPTIME)"
    elif docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
        STATUS=$(docker inspect -f '{{.State.Status}}' "$container" 2>/dev/null)
        check_warn "$container: $STATUS (detenido)"
    else
        check_warn "$container: no existe"
    fi
done

echo ""

# ==============================================
# 6. ACCESO NAS DESDE DOCKER
# ==============================================
echo -e "${YELLOW}[6] ACCESO NAS DESDE DOCKER${NC}"

# Probar acceso al NAS desde contenedor
if docker ps --format '{{.Names}}' | grep -q "automation_scheduler"; then
    if docker exec automation_scheduler ls /netapp/2510SP/H_Informacion_Consulta/Sub_Proy &>/dev/null 2>&1; then
        check_ok "Acceso al NAS desde contenedor: OK"
        # Contar directorios
        DIR_COUNT=$(docker exec automation_scheduler ls /netapp/2510SP/H_Informacion_Consulta/Sub_Proy 2>/dev/null | wc -l)
        check_ok "Directorios en Sub_Proy: $DIR_COUNT"
    else
        check_fail "NO hay acceso al NAS desde contenedor"
    fi
else
    check_warn "Contenedor no corriendo - no se puede verificar acceso NAS"
    echo -e "     Ejecuta: ./control.sh start"
fi

echo ""

# ==============================================
# 7. BASE DE DATOS
# ==============================================
echo -e "${YELLOW}[7] BASE DE DATOS${NC}"

if command -v psql &>/dev/null; then
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" &>/dev/null 2>&1
    if [ $? -eq 0 ]; then
        check_ok "Conexion PostgreSQL desde host: OK"
        TABLE_COUNT=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'" 2>/dev/null | tr -d ' ')
        check_ok "Tablas en BD: $TABLE_COUNT"
    else
        check_warn "No se puede conectar desde host (verificar desde contenedor)"
    fi
else
    check_warn "psql no instalado en host"
fi

# Verificar desde contenedor si esta corriendo
if docker ps --format '{{.Names}}' | grep -q "automation_scheduler"; then
    docker exec automation_scheduler python -c "
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
    conn.close()
    print('OK')
except Exception as e:
    print(f'FAIL: {e}')
    exit(1)
" 2>/dev/null
    if [ $? -eq 0 ]; then
        check_ok "Conexion PostgreSQL desde contenedor: OK"
    else
        check_fail "Conexion PostgreSQL desde contenedor: FALLO"
    fi
fi

echo ""

# ==============================================
# 8. TELEGRAM API
# ==============================================
echo -e "${YELLOW}[8] TELEGRAM API${NC}"

if [ -n "$TELEGRAM_TOKEN" ]; then
    RESPONSE=$(curl -s "https://api.telegram.org/bot$TELEGRAM_TOKEN/getMe" 2>/dev/null)
    if echo "$RESPONSE" | grep -q '"ok":true'; then
        BOT_NAME=$(echo "$RESPONSE" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
        check_ok "Telegram API OK - Bot: @$BOT_NAME"
    else
        check_fail "Telegram API fallo"
    fi
else
    check_warn "TELEGRAM_TOKEN no definido"
fi

echo ""

# ==============================================
# 9. ARCHIVOS
# ==============================================
echo -e "${YELLOW}[9] ARCHIVOS${NC}"

FILES=("scheduler.py" "telegram_bot.py" "db_cleaner.py" "requirements.txt")
for f in "${FILES[@]}"; do
    if [ -f "$f" ]; then
        check_ok "$f existe"
    else
        check_fail "$f NO existe"
    fi
done

echo -e "  ${BLUE}Scripts indexadores:${NC}"
SCRIPTS=("Script_INSUMOS_Linux.py" "Script_POST_Linux.py" "Script_TRANSVERSAL_Linux.py" "Script_OPERACION_Linux.py")
for s in "${SCRIPTS[@]}"; do
    if [ -f "scripts/$s" ]; then
        echo -e "    $s: ${GREEN}OK${NC}"
    else
        echo -e "    $s: ${RED}FALTA${NC}"
        ((WARNINGS++))
    fi
done

echo ""

# ==============================================
# 10. LOGS RECIENTES
# ==============================================
echo -e "${YELLOW}[10] LOGS RECIENTES${NC}"

if docker ps --format '{{.Names}}' | grep -q "automation_scheduler"; then
    echo -e "  ${BLUE}Scheduler (ultimas 3 lineas):${NC}"
    $COMPOSE_CMD logs --tail=3 scheduler 2>/dev/null | sed 's/^/    /'
    echo ""
    echo -e "  ${BLUE}Telegram Bot (ultimas 3 lineas):${NC}"
    $COMPOSE_CMD logs --tail=3 telegram_bot 2>/dev/null | sed 's/^/    /'
else
    check_warn "Contenedores no corriendo - sin logs"
fi

echo ""

# ==============================================
# RESUMEN
# ==============================================
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  RESUMEN${NC}"
echo -e "${BLUE}================================================${NC}"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}Todo OK - Sistema listo${NC}"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}$WARNINGS advertencias - Revisar antes de continuar${NC}"
else
    echo -e "${RED}$ERRORS errores, $WARNINGS advertencias${NC}"
    echo -e "${RED}Corrige los errores antes de iniciar${NC}"
fi

echo ""
echo -e "Comandos utiles:"
echo -e "  ${BLUE}./install.sh${NC}        - Instalar/reconstruir"
echo -e "  ${BLUE}./control.sh start${NC}  - Iniciar contenedores"
echo -e "  ${BLUE}./control.sh test${NC}   - Probar componentes"
echo -e "  ${BLUE}./control.sh logs -f${NC} - Ver logs en vivo"
echo ""

exit $ERRORS
