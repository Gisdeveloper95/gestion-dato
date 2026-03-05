#!/bin/bash

# ==============================================
# Script de Preparación para Migración
# Prepara el servidor actual para transferencia
# ==============================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   PREPARACIÓN PARA MIGRACIÓN - IGAC       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Directorio de trabajo
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$HOME/server_migration_backup"

echo -e "${YELLOW}Directorio actual:${NC} $SCRIPT_DIR"
echo -e "${YELLOW}Backups se guardarán en:${NC} $BACKUP_DIR"
echo ""

# Crear directorio de backup
mkdir -p "$BACKUP_DIR"

# ==============================================
# 1. RECOPILAR INFORMACIÓN DEL SISTEMA
# ==============================================

echo -e "${GREEN}[1/5] Recopilando información del sistema...${NC}"

cat > "$BACKUP_DIR/SERVIDOR_ACTUAL_INFO.txt" <<EOF
=== INFORMACIÓN DEL SERVIDOR ACTUAL ===
Generado: $(date)

SISTEMA:
  Usuario Linux: $(whoami)
  Home Directory: $HOME
  IP del Servidor: $(hostname -I | awk '{print $1}')
  Hostname: $(hostname)
  OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)

DOCKER:
  Docker Version: $(docker --version 2>/dev/null || echo "No disponible")
  Docker Compose: $(docker-compose --version 2>/dev/null || echo "No disponible")

POSTGRES:
  PostgreSQL Version: $(psql --version 2>/dev/null || echo "No disponible")

PYTHON:
  Python3 Version: $(python3 --version 2>/dev/null || echo "No disponible")

NETAPP:
  Mount Actual: $(mount | grep cifs | awk '{print $1, "->", $3}' || echo "No montado")
  Usuario CIFS: $(mount | grep cifs | grep -oP 'username=\K[^,]+' || echo "N/A")

WEB:
  Dominio Nginx: $(grep 'server_name' nginx/ssl.conf 2>/dev/null | grep -v '_' | grep -v '#' | head -1 | awk '{print $2}' | tr -d ';' || echo "N/A")

SERVICIOS SYSTEMD:
$(systemctl list-units --type=service --state=running 2>/dev/null | grep -E 'gestion|telegram' | awk '{print "  - " $1}' || echo "  Ninguno")

CONTAINERS DOCKER:
$(docker ps --format "  - {{.Names}} ({{.Status}})" 2>/dev/null || echo "  No hay containers corriendo")

CRONTAB:
$(crontab -l 2>/dev/null | grep -v '^#' | sed 's/^/  /' || echo "  No hay crontab configurado")

EOF

cat "$BACKUP_DIR/SERVIDOR_ACTUAL_INFO.txt"
echo ""
echo -e "${GREEN}✓ Información guardada en: ${BACKUP_DIR}/SERVIDOR_ACTUAL_INFO.txt${NC}"
echo ""

# ==============================================
# 2. BACKUP DE BASE DE DATOS
# ==============================================

echo -e "${GREEN}[2/5] Creando backup de PostgreSQL...${NC}"

DB_NAME=$(grep DB_NAME backend/.env 2>/dev/null | cut -d= -f2 || echo "gestion_dato_db")
DB_USER=$(grep DB_USER backend/.env 2>/dev/null | cut -d= -f2 || echo "postgres")
DB_HOST=$(grep DB_HOST backend/.env 2>/dev/null | cut -d= -f2 || echo "localhost")

BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_$(date +%Y%m%d_%H%M%S).sql"

echo "  Base de datos: $DB_NAME"
echo "  Usuario: $DB_USER"
echo "  Host: $DB_HOST"

if command -v pg_dump &> /dev/null; then
    if pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE" 2>/dev/null; then
        gzip "$BACKUP_FILE"
        echo -e "${GREEN}✓ Backup creado: ${BACKUP_FILE}.gz${NC}"
        echo -e "  Tamaño: $(du -h ${BACKUP_FILE}.gz | cut -f1)"
    else
        echo -e "${YELLOW}⚠ No se pudo crear el backup automáticamente${NC}"
        echo "  Crea el backup manualmente:"
        echo "    pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME | gzip > ${BACKUP_FILE}.gz"
    fi
else
    echo -e "${YELLOW}⚠ pg_dump no está disponible${NC}"
fi
echo ""

# ==============================================
# 3. GUARDAR CONFIGURACIONES SENSIBLES
# ==============================================

echo -e "${GREEN}[3/5] Extrayendo configuraciones sensibles...${NC}"

CONFIG_FILE="$BACKUP_DIR/configuraciones_sensibles.txt"

cat > "$CONFIG_FILE" <<EOF
=== CONFIGURACIONES SENSIBLES ===
Generado: $(date)

IMPORTANTE: Este archivo contiene información sensible.
            Protégelo con contraseña y elimínalo después de la migración.

=== DJANGO ===
SECRET_KEY=$(grep '^SECRET_KEY=' .env 2>/dev/null | cut -d= -f2 || grep '^SECRET_KEY=' backend/.env 2>/dev/null | cut -d= -f2 || echo "NO_ENCONTRADO")

=== POSTGRESQL ===
DB_NAME=$(grep '^DB_NAME=' backend/.env 2>/dev/null | cut -d= -f2 || echo "gestion_dato_db")
DB_USER=$(grep '^DB_USER=' backend/.env 2>/dev/null | cut -d= -f2 || echo "postgres")
DB_PASSWORD=$(grep '^DB_PASSWORD=' backend/.env 2>/dev/null | cut -d= -f2 || echo "NO_ENCONTRADO")
DB_HOST=$(grep '^DB_HOST=' backend/.env 2>/dev/null | cut -d= -f2 || echo "localhost")

=== TELEGRAM BOT ===
TELEGRAM_TOKEN=$(grep -A3 '"telegram"' automation/config/config.json 2>/dev/null | grep '"token"' | cut -d'"' -f4 || echo "NO_ENCONTRADO")
TELEGRAM_CHAT_ID=$(grep -A4 '"telegram"' automation/config/config.json 2>/dev/null | grep '"chat_id"' | cut -d'"' -f4 || echo "NO_ENCONTRADO")

=== GROQ AI ===
GROQ_API_KEY=$(grep -A4 '"ai"' automation/config/config.json 2>/dev/null | grep '"groq_api_key"' | cut -d'"' -f4 || echo "NO_ENCONTRADO")
GROQ_MODEL=$(grep -A4 '"ai"' automation/config/config.json 2>/dev/null | grep '"model"' | cut -d'"' -f4 || echo "llama-3.3-70b-versatile")

=== NETAPP ===
NETAPP_SERVER_IP=$(mount | grep cifs | awk -F'//' '{print $2}' | cut -d'/' -f1 || echo "NO_MONTADO")
NETAPP_SHARE=$(mount | grep cifs | awk -F'//' '{print $2}' | cut -d'/' -f2 | awk '{print $1}' || echo "NO_MONTADO")
NETAPP_MOUNT_POINT=$(mount | grep cifs | awk '{print $3}' || echo "/mnt/repositorio")
NETAPP_USER=$(mount | grep cifs | grep -oP 'username=\K[^,]+' || echo "NO_ENCONTRADO")
NETAPP_UID=$(mount | grep cifs | grep -oP 'uid=\K[0-9]+' || echo "1004")
NETAPP_GID=$(mount | grep cifs | grep -oP 'gid=\K[0-9]+' || echo "1002")
NETAPP_PASSWORD=AGREGAR_MANUALMENTE

=== WEB/DOMINIO ===
DOMINIO_ACTUAL=$(grep 'server_name' nginx/ssl.conf 2>/dev/null | grep -v '_' | grep -v '#' | head -1 | awk '{print $2}' | tr -d ';' || echo "NO_CONFIGURADO")
ALLOWED_HOSTS=$(grep '^ALLOWED_HOSTS=' .env 2>/dev/null | cut -d= -f2 || echo "NO_ENCONTRADO")
CORS_ORIGINS=$(grep '^CORS_ALLOWED_ORIGINS=' .env 2>/dev/null | cut -d= -f2 || echo "NO_ENCONTRADO")

=== CERTIFICADOS SSL ===
CERT_PATH=$(ls -d /etc/letsencrypt/live/*/ 2>/dev/null | head -1 || echo "NO_ENCONTRADO")
ACME_SH_INSTALLED=$([ -f ~/.acme.sh/acme.sh ] && echo "SI" || echo "NO")

=== DUCKDNS (si aplica) ===
DUCKDNS_TOKEN=AGREGAR_MANUALMENTE_SI_APLICA

=== NOTAS ADICIONALES ===
# Agrega aquí cualquier otra configuración importante:
#
#

EOF

echo -e "${GREEN}✓ Configuraciones extraídas${NC}"
echo ""

# Preguntar si quiere cifrar
read -p "¿Deseas cifrar el archivo de configuraciones con contraseña? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[SsYy]$ ]]; then
    if command -v zip &> /dev/null; then
        cd "$BACKUP_DIR"
        zip -e configuraciones_sensibles.zip configuraciones_sensibles.txt
        rm configuraciones_sensibles.txt
        echo -e "${GREEN}✓ Archivo cifrado: ${BACKUP_DIR}/configuraciones_sensibles.zip${NC}"
    else
        echo -e "${YELLOW}⚠ zip no está instalado. Archivo guardado sin cifrar.${NC}"
        echo -e "${RED}  ¡IMPORTANTE! Protege este archivo: ${CONFIG_FILE}${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Archivo guardado SIN CIFRAR${NC}"
    echo -e "${RED}  ¡IMPORTANTE! Protege este archivo: ${CONFIG_FILE}${NC}"
fi
echo ""

# ==============================================
# 4. VERIFICAR .GITIGNORE
# ==============================================

echo -e "${GREEN}[4/5] Verificando .gitignore...${NC}"

if [ ! -f "$SCRIPT_DIR/.gitignore" ]; then
    echo -e "${YELLOW}⚠ No existe .gitignore, creando...${NC}"
    cat > "$SCRIPT_DIR/.gitignore" <<'EOF'
# Archivos de configuración sensibles
.env
*.env
!.env.example
!*.env.example
NETAPP_MOUNT.env
automation/.env
config_secreto.txt
configuraciones_sensibles*
SERVIDOR_ACTUAL_INFO.txt
server_migration_backup/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
dist/
build/

# Node
node_modules/
npm-debug.log
yarn-error.log
dist/
.cache/

# Docker
docker_images_export/

# Certificados
*.pem
*.key
*.crt

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo
.claude/

# Postgres data
postgres_data/

# Backups
*_backup/
*.sql
*.sql.gz

# OS
.DS_Store
Thumbs.db
EOF
    echo -e "${GREEN}✓ .gitignore creado${NC}"
else
    echo -e "${GREEN}✓ .gitignore existe${NC}"
fi
echo ""

# ==============================================
# 5. RESUMEN Y PRÓXIMOS PASOS
# ==============================================

echo -e "${GREEN}[5/5] Resumen de preparación${NC}"
echo ""

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          PREPARACIÓN COMPLETADA           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}Archivos generados:${NC}"
echo "  1. Información del sistema:"
echo "     → $BACKUP_DIR/SERVIDOR_ACTUAL_INFO.txt"
echo ""
if [ -f "${BACKUP_FILE}.gz" ]; then
    echo "  2. Backup de base de datos:"
    echo "     → ${BACKUP_FILE}.gz"
    echo ""
fi
if [ -f "$BACKUP_DIR/configuraciones_sensibles.zip" ]; then
    echo "  3. Configuraciones sensibles (CIFRADO):"
    echo "     → $BACKUP_DIR/configuraciones_sensibles.zip"
elif [ -f "$CONFIG_FILE" ]; then
    echo "  3. Configuraciones sensibles (SIN CIFRAR):"
    echo -e "     → ${RED}$CONFIG_FILE${NC}"
fi
echo ""

echo -e "${YELLOW}📋 PRÓXIMOS PASOS:${NC}"
echo ""
echo "1. REVISAR Y COMPLETAR:"
echo "   - Abre las configuraciones sensibles y completa:"
echo "     * NETAPP_PASSWORD"
echo "     * DUCKDNS_TOKEN (si aplica)"
echo "   - Verifica que todos los valores sean correctos"
echo ""

echo "2. TRANSFERIR AL SERVIDOR NUEVO:"
echo "   a) Código fuente (usa Git o SCP):"
if [ -d "$SCRIPT_DIR/.git" ]; then
    echo "      → git push origin main  # Si tienes repo remoto"
else
    echo "      → tar --exclude='.env' --exclude='*.env' --exclude='postgres_data' \\"
    echo "            --exclude='node_modules' --exclude='logs' \\"
    echo "            -czf server_codigo.tar.gz $SCRIPT_DIR"
    echo "      → scp server_codigo.tar.gz usuario@nuevo-servidor:/tmp/"
fi
echo ""
echo "   b) Backup de base de datos:"
if [ -f "${BACKUP_FILE}.gz" ]; then
    echo "      → scp ${BACKUP_FILE}.gz usuario@nuevo-servidor:/tmp/"
fi
echo ""
echo "   c) Configuraciones sensibles:"
if [ -f "$BACKUP_DIR/configuraciones_sensibles.zip" ]; then
    echo "      → scp $BACKUP_DIR/configuraciones_sensibles.zip usuario@nuevo-servidor:/tmp/"
elif [ -f "$CONFIG_FILE" ]; then
    echo "      → scp $CONFIG_FILE usuario@nuevo-servidor:/tmp/"
fi
echo ""

echo "3. EN EL SERVIDOR NUEVO:"
echo "   Sigue la guía paso a paso:"
echo "   → cat GUIA_MIGRACION_PASO_A_PASO.md"
echo "   → cat CHECKLIST_MIGRACION.md"
echo ""

echo -e "${RED}⚠️  IMPORTANTE - SEGURIDAD:${NC}"
echo "   • Protege los archivos de configuración sensibles"
echo "   • Elimina los backups de /tmp/ después de usarlos"
echo "   • NO subas archivos .env o configuraciones a Git público"
echo "   • Cambia passwords en el servidor nuevo por seguridad"
echo ""

echo -e "${GREEN}✓ Preparación completada exitosamente${NC}"
echo ""
