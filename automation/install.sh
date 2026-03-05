#!/bin/bash
# ==============================================
# AUTOMATION SYSTEM - INSTALADOR DOCKER
# ==============================================
set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  AUTOMATION SYSTEM - INSTALADOR DOCKER${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# ==============================================
# PASO 1: Verificar Docker
# ==============================================
echo -e "${YELLOW}[1/5]${NC} Verificando Docker..."

if ! command -v docker &>/dev/null; then
    echo -e "${RED}ERROR: Docker no esta instalado${NC}"
    exit 1
fi

if ! command -v docker-compose &>/dev/null && ! docker compose version &>/dev/null; then
    echo -e "${RED}ERROR: docker-compose no esta instalado${NC}"
    exit 1
fi

# Determinar comando de docker-compose
if docker compose version &>/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
echo -e "  Docker: ${GREEN}$DOCKER_VERSION${NC}"
echo -e "  Compose: ${GREEN}$COMPOSE_CMD${NC}"
echo -e "${GREEN}OK${NC} Docker disponible"

# ==============================================
# PASO 2: Cargar configuracion
# ==============================================
echo -e "\n${YELLOW}[2/5]${NC} Cargando configuracion..."

if [ ! -f ".env" ]; then
    echo -e "${RED}ERROR: No existe .env${NC}"
    echo "Copia .env.example a .env y configura las variables"
    exit 1
fi

# Cargar variables
set -a
source .env
set +a

echo -e "  AUTOMATION_DIR: ${GREEN}$AUTOMATION_DIR${NC}"
echo -e "  REPOSITORY_PATH: ${GREEN}$REPOSITORY_PATH${NC}"
echo -e "  DB_HOST: ${GREEN}$DB_HOST${NC}"
echo -e "${GREEN}OK${NC} Configuracion cargada"

# ==============================================
# PASO 3: Verificar montaje NAS
# ==============================================
echo -e "\n${YELLOW}[3/5]${NC} Verificando montaje NAS..."

if [ ! -d "$REPOSITORY_PATH" ]; then
    echo -e "${RED}ERROR: Montaje no existe: $REPOSITORY_PATH${NC}"
    echo "El NAS debe estar montado antes de continuar"
    exit 1
fi

# Verificar acceso (puede fallar por permisos, Docker lo manejara)
if ls "$REPOSITORY_PATH" &>/dev/null; then
    echo -e "  Acceso directo: ${GREEN}OK${NC}"
else
    echo -e "  Acceso directo: ${YELLOW}Denegado (Docker puede tener acceso)${NC}"
fi

echo -e "${GREEN}OK${NC} Montaje verificado"

# ==============================================
# PASO 4: Construir imagenes Docker
# ==============================================
echo -e "\n${YELLOW}[4/5]${NC} Construyendo imagenes Docker..."

$COMPOSE_CMD build --no-cache

echo -e "${GREEN}OK${NC} Imagenes construidas"

# ==============================================
# PASO 5: Generar servicio systemd
# ==============================================
echo -e "\n${YELLOW}[5/5]${NC} Generando servicio systemd..."

mkdir -p systemd

# Servicio unico para docker-compose
cat > systemd/automation-docker.service << EOF
[Unit]
Description=Automation System (Docker)
After=docker.service network-online.target
Requires=docker.service
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$AUTOMATION_DIR
ExecStart=$COMPOSE_CMD up -d
ExecStop=$COMPOSE_CMD down
ExecReload=$COMPOSE_CMD restart
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}OK${NC} Servicio generado: systemd/automation-docker.service"

# ==============================================
# Instalar systemd (opcional)
# ==============================================
echo ""
read -p "Deseas instalar el servicio en systemd? [y/N]: " INSTALL_SYSTEMD
INSTALL_SYSTEMD=${INSTALL_SYSTEMD:-n}

if [[ "$INSTALL_SYSTEMD" =~ ^[Yy]$ ]]; then
    echo -e "  Copiando servicio..."
    sudo cp systemd/automation-docker.service /etc/systemd/system/

    echo -e "  Recargando systemd..."
    sudo systemctl daemon-reload

    echo -e "  Habilitando servicio..."
    sudo systemctl enable automation-docker.service

    echo -e "${GREEN}OK${NC} Servicio instalado"
else
    echo -e "${YELLOW}Servicio NO instalado${NC}"
    echo "Para instalar manualmente:"
    echo "  sudo cp systemd/automation-docker.service /etc/systemd/system/"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable automation-docker.service"
fi

# ==============================================
# RESUMEN
# ==============================================
echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  INSTALACION COMPLETADA${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "Comandos:"
echo -e "  ${BLUE}./diagnose.sh${NC}        - Verificar estado"
echo -e "  ${BLUE}./control.sh start${NC}   - Iniciar contenedores"
echo -e "  ${BLUE}./control.sh status${NC}  - Ver estado"
echo -e "  ${BLUE}./control.sh logs${NC}    - Ver logs"
echo -e "  ${BLUE}./control.sh test${NC}    - Probar script manualmente"
echo ""
echo -e "Docker Compose:"
echo -e "  ${BLUE}$COMPOSE_CMD up -d${NC}     - Iniciar"
echo -e "  ${BLUE}$COMPOSE_CMD down${NC}      - Detener"
echo -e "  ${BLUE}$COMPOSE_CMD logs -f${NC}   - Ver logs en vivo"
echo ""
