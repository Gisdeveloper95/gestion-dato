# 🚀 GUÍA DE MIGRACIÓN PASO A PASO

Esta guía te ayudará a migrar todo el proyecto a un nuevo servidor con diferentes usuarios, IPs, dominios, etc.

## 📋 ÍNDICE

1. [Preparación en Servidor Actual](#1-preparación-en-servidor-actual)
2. [Configuración en Servidor Nuevo](#2-configuración-en-servidor-nuevo)
3. [Checklist de Verificación](#3-checklist-de-verificación)
4. [Troubleshooting](#4-troubleshooting)

---

## 1. PREPARACIÓN EN SERVIDOR ACTUAL

### 1.1 Recopilar Información Actual

Documenta los valores actuales (para referencia):

```bash
cd /home/sonia.eraso/server

# Crear archivo con información del servidor actual
cat > SERVIDOR_ACTUAL_INFO.txt <<EOF
=== INFORMACIÓN DEL SERVIDOR ACTUAL ===

# SISTEMA
Usuario Linux: $(whoami)
Home Directory: $HOME
IP del Servidor: $(hostname -I | awk '{print $1}')
Hostname: $(hostname)

# DOCKER
Docker Version: $(docker --version 2>/dev/null || echo "N/A")
Containers Activos: $(docker ps --format '{{.Names}}' 2>/dev/null | tr '\n' ', ' || echo "N/A")

# POSTGRES
DB Host: $(grep DB_HOST backend/.env | cut -d= -f2)
DB Name: $(grep DB_NAME backend/.env | cut -d= -f2)
DB User: $(grep DB_USER backend/.env | cut -d= -f2)

# NETAPP
NetApp Mount: $(mount | grep cifs | awk '{print $1, "->", $3}')
NetApp User: $(mount | grep cifs | grep -oP 'username=\K[^,]+')

# WEB
Dominio Actual: $(grep server_name nginx/ssl.conf | grep -v '_' | head -1 | awk '{print $2}' | tr -d ';')
Certificados SSL: $(ls -d /etc/letsencrypt/live/*/ 2>/dev/null || echo "N/A")

# TELEGRAM BOT
Bot Token: $(grep -A1 '"telegram"' automation/config/config.json | grep token | cut -d'"' -f4)
Chat ID: $(grep -A2 '"telegram"' automation/config/config.json | grep chat_id | cut -d'"' -f4)

# SERVICIOS SYSTEMD
Servicios Activos: $(systemctl list-units --type=service --state=running | grep -E 'gestion|telegram' | awk '{print $1}' | tr '\n' ', ')

Fecha de generación: $(date)
EOF

cat SERVIDOR_ACTUAL_INFO.txt
```

### 1.2 Hacer Backup de la Base de Datos

```bash
# Crear directorio de backups
mkdir -p ~/server_migration_backup

# Backup de PostgreSQL
pg_dump -h localhost -U postgres -d gestion_dato_db > ~/server_migration_backup/gestion_dato_db_$(date +%Y%m%d).sql

# Comprimir
gzip ~/server_migration_backup/gestion_dato_db_*.sql

echo "✓ Backup de BD creado en ~/server_migration_backup/"
```

### 1.3 Exportar Configuraciones Sensibles (SEGURO)

```bash
cd /home/sonia.eraso/server

# Crear archivo cifrado con configuraciones sensibles
# IMPORTANTE: Usa una contraseña fuerte que recordarás

cat > ~/server_migration_backup/config_secreto.txt <<EOF
=== CONFIGURACIONES SENSIBLES ===

# DJANGO
SECRET_KEY=$(grep SECRET_KEY .env | cut -d= -f2)

# POSTGRES
DB_PASSWORD=$(grep DB_PASSWORD backend/.env | cut -d= -f2)

# TELEGRAM
TELEGRAM_TOKEN=$(grep -A1 '"telegram"' automation/config/config.json | grep token | cut -d'"' -f4)
TELEGRAM_CHAT_ID=$(grep -A2 '"telegram"' automation/config/config.json | grep chat_id | cut -d'"' -f4)

# GROQ AI
GROQ_API_KEY=$(grep -A1 '"ai"' automation/config/config.json | grep groq_api_key | cut -d'"' -f4)

# NETAPP (desde mount actual)
NETAPP_SERVER=$(mount | grep cifs | awk -F'//' '{print $2}' | cut -d'/' -f1)
NETAPP_USER=$(mount | grep cifs | grep -oP 'username=\K[^,]+')
# NETAPP_PASSWORD: [AGREGAR MANUALMENTE]

# DUCKDNS (si aplica)
# DUCKDNS_TOKEN: [AGREGAR MANUALMENTE SI LO TIENES]

EOF

# Cifrar el archivo (requerirá contraseña)
zip -e ~/server_migration_backup/configuraciones_secretas.zip ~/server_migration_backup/config_secreto.txt

# Eliminar archivo sin cifrar
rm ~/server_migration_backup/config_secreto.txt

echo "✓ Configuraciones guardadas cifradas en ~/server_migration_backup/configuraciones_secretas.zip"
```

### 1.4 Preparar el Código para Git

```bash
cd /home/sonia.eraso/server

# Si no existe .gitignore, crearlo
if [ ! -f .gitignore ]; then
    cat > .gitignore <<'EOF'
# Archivos de configuración sensibles
.env
*.env
!.env.example
!*.env.example
NETAPP_MOUNT.env
automation/.env
config_secreto.txt
configuraciones_secretas.zip
SERVIDOR_ACTUAL_INFO.txt

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
fi

# Si no has inicializado git
if [ ! -d .git ]; then
    git init
    git add .
    git commit -m "Initial commit - Sistema de Gestión de Datos IGAC"
fi

echo "✓ Repositorio Git preparado"
```

---

## 2. CONFIGURACIÓN EN SERVIDOR NUEVO

### 2.1 Requisitos Previos en el Servidor Nuevo

```bash
# Como root o con sudo

# Rocky Linux / CentOS / RHEL
sudo yum update -y
sudo yum install -y git docker docker-compose postgresql postgresql-contrib cifs-utils zip

# Ubuntu / Debian
# sudo apt update
# sudo apt install -y git docker.io docker-compose postgresql postgresql-client cifs-utils zip

# Iniciar y habilitar Docker
sudo systemctl start docker
sudo systemctl enable docker

# Agregar usuario al grupo docker (reemplaza NUEVO_USUARIO)
sudo usermod -aG docker NUEVO_USUARIO

# Iniciar PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2.2 Transferir Archivos

**Opción A: Desde Git (Recomendado si tienes repositorio remoto)**

```bash
# En servidor nuevo
cd /home/NUEVO_USUARIO/
git clone https://github.com/TU_USUARIO/TU_REPO.git server
cd server
```

**Opción B: Transferencia directa con SCP**

```bash
# Desde servidor actual
cd /home/sonia.eraso
tar --exclude='server/postgres_data' \
    --exclude='server/node_modules' \
    --exclude='server/__pycache__' \
    --exclude='server/.git' \
    --exclude='server/logs' \
    -czf server_codigo.tar.gz server/

# Transferir
scp server_codigo.tar.gz NUEVO_USUARIO@NUEVO_SERVIDOR:/tmp/
scp ~/server_migration_backup/gestion_dato_db_*.sql.gz NUEVO_USUARIO@NUEVO_SERVIDOR:/tmp/
scp ~/server_migration_backup/configuraciones_secretas.zip NUEVO_USUARIO@NUEVO_SERVIDOR:/tmp/

# En servidor nuevo
cd /home/NUEVO_USUARIO/
tar -xzf /tmp/server_codigo.tar.gz
```

### 2.3 Configurar Variables de Entorno

```bash
cd /home/NUEVO_USUARIO/server

# Descomprimir configuraciones secretas (te pedirá la contraseña)
unzip /tmp/configuraciones_secretas.zip -d /tmp/
cat /tmp/config_secreto.txt  # Copia los valores que necesites

# ====================
# CONFIGURAR .ENV PRINCIPAL
# ====================

cp EJEMPLO.env .env
nano .env

# Actualizar con NUEVOS valores:
# - DB_HOST=localhost  (o IP del servidor Postgres si es externo)
# - DB_PASSWORD=NUEVA_PASSWORD_SEGURA
# - SECRET_KEY=NUEVA_SECRET_KEY  (genera una nueva)
# - ALLOWED_HOSTS=NUEVA_IP,nuevo-dominio.com,localhost
# - CORS_ALLOWED_ORIGINS=https://nuevo-dominio.com,http://NUEVA_IP
# - CSRF_TRUSTED_ORIGINS=https://nuevo-dominio.com,http://NUEVA_IP

# ====================
# CONFIGURAR BACKEND .ENV
# ====================

cp backend/.env backend/.env.backup 2>/dev/null || true
cat > backend/.env <<EOF
SECRET_KEY=NUEVA_SECRET_KEY_AQUI
DEBUG=False
DB_ENGINE=django.db.backends.postgresql
DB_NAME=gestion_dato_db
DB_USER=postgres
DB_PASSWORD=NUEVA_PASSWORD_SEGURA
DB_HOST=localhost
DB_PORT=5432
DB_CLIENT_ENCODING=UTF8
ALLOWED_HOSTS=nuevo-dominio.com,localhost,127.0.0.1,NUEVA_IP
CORS_ALLOWED_ORIGINS=https://nuevo-dominio.com,http://nuevo-dominio.com,http://localhost:5173
CSRF_TRUSTED_ORIGINS=https://nuevo-dominio.com,http://nuevo-dominio.com,http://localhost:5173
REPOSITORY_BASE_PATH=/mnt/repositorio/2510SP/H_Informacion_Consulta/Sub_Proy
PDF_REPOSITORY_PATH=/mnt/repositorio/2510SP/H_Informacion_Consulta/Sub_Proy/05_grup_trab/11_gest_info/2025/01_insu_primr/CONCEPTOS_ORTO_CARTO
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=180
JWT_REFRESH_TOKEN_LIFETIME_DAYS=1
EOF

# ====================
# CONFIGURAR AUTOMATION .ENV
# ====================

cp automation/.env.example automation/.env
nano automation/.env

# Configurar:
# - LINUX_USER=NUEVO_USUARIO
# - DB_PASSWORD=NUEVA_PASSWORD
# - TELEGRAM_TOKEN=TU_TOKEN (del archivo config_secreto.txt)
# - GROQ_API_KEY=TU_API_KEY (del archivo config_secreto.txt)
# - TELEGRAM_CHAT_ID=TU_CHAT_ID

# ====================
# CONFIGURAR NETAPP
# ====================

cp NETAPP_MOUNT.env.example NETAPP_MOUNT.env
nano NETAPP_MOUNT.env

# Configurar:
# - NETAPP_SERVER_IP=IP_DE_TU_NETAPP
# - NETAPP_USERNAME=NUEVO_USUARIO_WINDOWS@dominio.com
# - NETAPP_PASSWORD=PASSWORD_NETAPP
# - NETAPP_UID=$(id -u)  # ID del nuevo usuario Linux
# - NETAPP_GID=$(id -g)  # ID del grupo del nuevo usuario
```

### 2.4 Configurar PostgreSQL

```bash
# Crear usuario y base de datos
sudo -u postgres psql <<EOF
CREATE USER postgres WITH PASSWORD 'NUEVA_PASSWORD_SEGURA';
CREATE DATABASE gestion_dato_db OWNER postgres;
GRANT ALL PRIVILEGES ON DATABASE gestion_dato_db TO postgres;
\q
EOF

# Restaurar backup
gunzip /tmp/gestion_dato_db_*.sql.gz
psql -h localhost -U postgres -d gestion_dato_db < /tmp/gestion_dato_db_*.sql

# Verificar
psql -h localhost -U postgres -d gestion_dato_db -c "\dt"
```

### 2.5 Configurar Montaje NetApp

```bash
cd /home/NUEVO_USUARIO/server

# Ejecutar script de configuración
bash setup_netapp_mount.sh

# Verificar montaje
ls -la /mnt/repositorio
mount | grep cifs
```

### 2.6 Actualizar Nginx para Nuevo Dominio

```bash
cd /home/NUEVO_USUARIO/server

# Actualizar dominio en nginx/ssl.conf
sed -i 's/gestiondato.duckdns.org/nuevo-dominio.duckdns.org/g' nginx/ssl.conf

# Verificar cambios
grep server_name nginx/ssl.conf
```

### 2.7 Obtener Certificados SSL (si usas DuckDNS)

```bash
# Instalar acme.sh
curl https://get.acme.sh | sh
source ~/.bashrc

# Configurar token de DuckDNS
export DuckDNS_Token="TU_TOKEN_DUCKDNS"

# Obtener certificado
~/.acme.sh/acme.sh --issue --dns dns_duckdns -d nuevo-dominio.duckdns.org

# Copiar certificados
sudo mkdir -p /etc/letsencrypt/live/nuevo-dominio.duckdns.org
sudo cp ~/.acme.sh/nuevo-dominio.duckdns.org/fullchain.cer \
  /etc/letsencrypt/live/nuevo-dominio.duckdns.org/fullchain.pem
sudo cp ~/.acme.sh/nuevo-dominio.duckdns.org/nuevo-dominio.duckdns.org.key \
  /etc/letsencrypt/live/nuevo-dominio.duckdns.org/privkey.pem
sudo chmod 644 /etc/letsencrypt/live/nuevo-dominio.duckdns.org/*.pem
```

### 2.8 Actualizar Servicios Systemd

```bash
cd /home/NUEVO_USUARIO/server/automation/systemd

# Actualizar usuario en los archivos .service
sed -i "s/sonia.eraso/NUEVO_USUARIO/g" *.service
sed -i "s|/home/sonia.eraso|/home/NUEVO_USUARIO|g" *.service

# Copiar servicios
sudo cp *.service /etc/systemd/system/

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicios
sudo systemctl enable gestion-telegram-bot.service
sudo systemctl enable gestion-scheduler.service
sudo systemctl enable gestion-db-cleanup.service
```

### 2.9 Configurar Firewall

```bash
# Rocky Linux / CentOS
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# Ubuntu
# sudo ufw allow 80/tcp
# sudo ufw allow 443/tcp
# sudo ufw allow 8000/tcp
# sudo ufw reload
```

### 2.10 Desplegar la Aplicación

```bash
cd /home/NUEVO_USUARIO/server

# Iniciar servicios Docker
bash install.sh

# Verificar que todo esté corriendo
docker ps
sudo systemctl status gestion-telegram-bot
sudo systemctl status gestion-scheduler

# Ver logs
docker logs igac_backend -f
docker logs igac_frontend -f
```

---

## 3. CHECKLIST DE VERIFICACIÓN

Usa este checklist para asegurarte de que todo funciona:

### 3.1 Sistema Base
- [ ] PostgreSQL instalado y corriendo
- [ ] Docker instalado y corriendo
- [ ] Usuario Linux creado con permisos correctos
- [ ] Firewall configurado (puertos 80, 443, 8000)

### 3.2 Configuraciones
- [ ] Archivo `.env` principal configurado
- [ ] Archivo `backend/.env` configurado
- [ ] Archivo `automation/.env` configurado
- [ ] Archivo `NETAPP_MOUNT.env` configurado
- [ ] Nginx `ssl.conf` actualizado con nuevo dominio
- [ ] Servicios systemd actualizados con nuevo usuario

### 3.3 Base de Datos
- [ ] Base de datos creada
- [ ] Usuario PostgreSQL creado
- [ ] Backup restaurado correctamente
- [ ] Conexión desde backend funciona
```bash
psql -h localhost -U postgres -d gestion_dato_db -c "SELECT COUNT(*) FROM app_municipio;"
```

### 3.4 NetApp
- [ ] Montaje CIFS/SMB exitoso
- [ ] Entrada en `/etc/fstab` agregada
- [ ] Permisos de lectura funcionan
- [ ] Permisos de escritura funcionan (si aplica)
```bash
ls -la /mnt/repositorio/2510SP/
touch /mnt/repositorio/test_write.txt && rm /mnt/repositorio/test_write.txt
```

### 3.5 SSL/HTTPS
- [ ] Certificados SSL obtenidos
- [ ] Certificados copiados a `/etc/letsencrypt/live/`
- [ ] Permisos correctos en certificados (644)
- [ ] Renovación automática configurada (crontab acme.sh)

### 3.6 Docker
- [ ] Contenedor `igac_backend` corriendo
- [ ] Contenedor `igac_frontend` corriendo
- [ ] Contenedor `igac_nginx_proxy` corriendo
- [ ] Volúmenes creados correctamente
- [ ] Red Docker `igac_network` creada

### 3.7 Aplicación Web
- [ ] Frontend accesible: `http://NUEVA_IP`
- [ ] Frontend accesible: `https://nuevo-dominio.com`
- [ ] Login funciona
- [ ] API responde: `curl http://NUEVA_IP/api/`
- [ ] Dashboard carga correctamente
- [ ] Ver PDFs funciona

### 3.8 Bot de Telegram
- [ ] Servicio `gestion-telegram-bot` activo
- [ ] Bot responde a comandos
- [ ] Comandos de IA funcionan
- [ ] Logs se envían a Telegram
```bash
sudo systemctl status gestion-telegram-bot
journalctl -u gestion-telegram-bot -f
```

### 3.9 Scheduler/Automation
- [ ] Servicio `gestion-scheduler` activo
- [ ] Scripts programados se ejecutan
- [ ] Logs se generan correctamente
```bash
sudo systemctl status gestion-scheduler
ls -la /home/NUEVO_USUARIO/server/automation/logs/
```

### 3.10 Seguridad
- [ ] Archivo `config_secreto.txt` eliminado
- [ ] Permisos de archivos `.env` son 600
- [ ] Credenciales NetApp en archivo seguro (600)
- [ ] No hay tokens/passwords en código versionado

---

## 4. TROUBLESHOOTING

### Problema: "Cannot connect to database"
```bash
# Verificar que PostgreSQL esté corriendo
sudo systemctl status postgresql

# Verificar conexión
psql -h localhost -U postgres -d gestion_dato_db

# Ver logs de backend
docker logs igac_backend

# Verificar configuración
grep DB_ backend/.env
```

### Problema: "Permission denied" en NetApp
```bash
# Verificar montaje
mount | grep cifs

# Verificar credenciales
sudo cat /root/.netapp_credentials

# Remontar
sudo umount /mnt/repositorio
bash setup_netapp_mount.sh
```

### Problema: "SSL certificate error"
```bash
# Verificar certificados
ls -la /etc/letsencrypt/live/nuevo-dominio.duckdns.org/

# Verificar permisos
sudo chmod 644 /etc/letsencrypt/live/nuevo-dominio.duckdns.org/*.pem

# Reiniciar nginx
docker restart igac_nginx_proxy
```

### Problema: Bot de Telegram no responde
```bash
# Ver logs
journalctl -u gestion-telegram-bot -n 50

# Verificar configuración
cat automation/.env | grep TELEGRAM

# Reiniciar servicio
sudo systemctl restart gestion-telegram-bot
```

### Problema: Docker no inicia
```bash
# Verificar logs
docker logs igac_backend
docker logs igac_frontend

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📞 SOPORTE ADICIONAL

Si encuentras problemas:

1. Revisa los logs:
   - Backend: `docker logs igac_backend -f`
   - Frontend: `docker logs igac_frontend -f`
   - Nginx: `docker logs igac_nginx_proxy -f`
   - Bot: `journalctl -u gestion-telegram-bot -f`
   - Scheduler: `journalctl -u gestion-scheduler -f`

2. Documentación disponible:
   - [GUIA_DESPLIEGUE_NUEVO_SERVIDOR.md](GUIA_DESPLIEGUE_NUEVO_SERVIDOR.md)
   - [GUIA_COMPLETA_HTTPS.md](GUIA_COMPLETA_HTTPS.md)
   - [automation/README.md](automation/README.md)

3. Verifica configuraciones:
   - `.env`
   - `backend/.env`
   - `automation/.env`
   - `NETAPP_MOUNT.env`

---

**Última actualización**: $(date +%Y-%m-%d)
