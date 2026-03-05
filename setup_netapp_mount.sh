#!/bin/bash

# ==============================================
# Script de Configuración de Montaje NetApp
# Configura automáticamente el montaje CIFS/SMB
# ==============================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Configuración de Montaje NetApp ===${NC}"

# Verificar si existe el archivo de configuración
if [ ! -f "NETAPP_MOUNT.env" ]; then
    echo -e "${RED}Error: No se encuentra NETAPP_MOUNT.env${NC}"
    echo "Por favor copia NETAPP_MOUNT.env.example a NETAPP_MOUNT.env y configúralo"
    exit 1
fi

# Cargar variables
source NETAPP_MOUNT.env

echo -e "${YELLOW}Configuración cargada:${NC}"
echo "  Servidor: ${NETAPP_SERVER_IP}"
echo "  Share: ${NETAPP_SHARE_PATH}"
echo "  Punto de montaje: ${NETAPP_MOUNT_POINT}"
echo "  Usuario: ${NETAPP_USERNAME}"

# Verificar que no esté vacío
if [ -z "$NETAPP_SERVER_IP" ] || [ -z "$NETAPP_USERNAME" ] || [ -z "$NETAPP_PASSWORD" ]; then
    echo -e "${RED}Error: Faltan configuraciones en NETAPP_MOUNT.env${NC}"
    exit 1
fi

# Instalar cifs-utils si no está
if ! command -v mount.cifs &> /dev/null; then
    echo -e "${YELLOW}Instalando cifs-utils...${NC}"
    sudo yum install -y cifs-utils || sudo apt install -y cifs-utils
fi

# Crear punto de montaje
if [ ! -d "$NETAPP_MOUNT_POINT" ]; then
    echo -e "${YELLOW}Creando punto de montaje: ${NETAPP_MOUNT_POINT}${NC}"
    sudo mkdir -p "$NETAPP_MOUNT_POINT"
fi

# Crear archivo de credenciales seguro
CREDS_FILE="/root/.netapp_credentials"
echo -e "${YELLOW}Creando archivo de credenciales...${NC}"
sudo bash -c "cat > $CREDS_FILE <<EOF
username=${NETAPP_USERNAME}
password=${NETAPP_PASSWORD}
domain=${NETAPP_DOMAIN}
EOF"
sudo chmod 600 "$CREDS_FILE"

# Probar montaje manual
echo -e "${YELLOW}Probando montaje...${NC}"
if mount | grep -q "$NETAPP_MOUNT_POINT"; then
    echo "Desmontando montaje existente..."
    sudo umount "$NETAPP_MOUNT_POINT" || true
fi

sudo mount -t cifs \
    "//${NETAPP_SERVER_IP}/${NETAPP_SHARE_PATH}" \
    "$NETAPP_MOUNT_POINT" \
    -o "credentials=$CREDS_FILE,uid=${NETAPP_UID},gid=${NETAPP_GID},file_mode=${NETAPP_FILE_MODE},dir_mode=${NETAPP_DIR_MODE},vers=3.0"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Montaje exitoso${NC}"
else
    echo -e "${RED}✗ Error en el montaje${NC}"
    exit 1
fi

# Verificar acceso
if [ -d "$NETAPP_MOUNT_POINT" ] && [ "$(ls -A $NETAPP_MOUNT_POINT 2>/dev/null)" ]; then
    echo -e "${GREEN}✓ Contenido accesible${NC}"
else
    echo -e "${YELLOW}⚠ Advertencia: El punto de montaje está vacío${NC}"
fi

# Agregar a /etc/fstab si no existe
if ! grep -q "$NETAPP_MOUNT_POINT" /etc/fstab; then
    echo -e "${YELLOW}Agregando entrada a /etc/fstab...${NC}"
    echo "# NetApp CIFS Mount - Configurado $(date)" | sudo tee -a /etc/fstab
    echo "//${NETAPP_SERVER_IP}/${NETAPP_SHARE_PATH} ${NETAPP_MOUNT_POINT} cifs credentials=${CREDS_FILE},uid=${NETAPP_UID},gid=${NETAPP_GID},file_mode=${NETAPP_FILE_MODE},dir_mode=${NETAPP_DIR_MODE},vers=3.0,_netdev 0 0" | sudo tee -a /etc/fstab
    echo -e "${GREEN}✓ Entrada agregada a /etc/fstab${NC}"
else
    echo -e "${YELLOW}⚠ Ya existe una entrada en /etc/fstab para ${NETAPP_MOUNT_POINT}${NC}"
fi

echo ""
echo -e "${GREEN}=== Configuración Completa ===${NC}"
echo -e "El montaje NetApp está configurado y persistirá después de reinicios"
echo ""
echo "Para verificar:"
echo "  ls -la ${NETAPP_MOUNT_POINT}"
echo "  mount | grep cifs"
