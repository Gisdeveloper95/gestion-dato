# 🚀 GUÍA: DESPLEGAR EN UN NUEVO SERVIDOR

Esta guía explica las diferentes formas de migrar/desplegar la aplicación en un servidor Linux nuevo.

## 📋 Tabla de Contenidos

1. [Comparación de Métodos](#comparación-de-métodos)
2. [Método 1: Git (Recomendado)](#método-1-git-recomendado)
3. [Método 2: Exportar Imágenes Docker](#método-2-exportar-imágenes-docker)
4. [Método 3: Copiar Directorio Completo](#método-3-copiar-directorio-completo)
5. [Configuración Post-Despliegue](#configuración-post-despliegue)

---

## Comparación de Métodos

| Método | Velocidad | Tamaño | Flexibilidad | Recomendado Para |
|--------|-----------|--------|--------------|------------------|
| **Git** | ⚡⚡ Rápido | 📦 Pequeño (MB) | ✅ Alta | Producción, múltiples servidores |
| **Imágenes Docker** | ⚡ Medio | 📦📦 Grande (GB) | ⚠️ Media | Servidores similares, sin internet |
| **Copiar Todo** | 🐌 Lento | 📦📦📦 Muy grande | ❌ Baja | Pruebas rápidas, desarrollo |

---

## Método 1: Git (Recomendado) ⭐

### En el Servidor Origen

#### 1.1 Preparar el repositorio

```bash
cd /home/sonia.eraso/server

# Crear .gitignore
cat > .gitignore << 'EOF'
# Archivos de configuración sensibles
.env
*.env

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

# IDE
.vscode/
.idea/
*.swp
*.swo

# Postgres data
postgres_data/

# OS
.DS_Store
Thumbs.db
EOF

# Inicializar git
git init

# Agregar archivos
git add .
git commit -m "Initial commit - Django + Vue.js application"

# Conectar con repositorio remoto (GitHub, GitLab, etc.)
# git remote add origin https://github.com/tu-usuario/tu-repo.git
# git push -u origin main
```

#### 1.2 Documentar configuración

Crea un archivo `EJEMPLO.env` con la estructura (sin valores sensibles):

```bash
cat > EJEMPLO.env << 'EOF'
# === DJANGO BACKEND ===
DEBUG=False
SECRET_KEY=CAMBIAR_POR_CLAVE_SEGURA
ALLOWED_HOSTS=*,tu-dominio.com,localhost,127.0.0.1,IP_SERVIDOR,backend

# === DATABASE ===
POSTGRES_DB=nombre_base_datos
POSTGRES_USER=usuario_postgres
POSTGRES_PASSWORD=CAMBIAR_PASSWORD_SEGURO
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# === CORS Y CSRF ===
CORS_ALLOWED_ORIGINS=https://tu-dominio.com,http://tu-dominio.com
CSRF_TRUSTED_ORIGINS=https://tu-dominio.com,http://tu-dominio.com

# === FRONTEND ===
VITE_API_URL=

# === NETWORK SHARES (si aplica) ===
REPOSITORY_BASE_PATH=ruta_a_tu_repositorio
PDF_REPOSITORY_PATH=ruta_a_tu_repositorio_pdf
EOF
```

### En el Servidor Nuevo

#### 1.3 Clonar e instalar

```bash
# Instalar dependencias del sistema
sudo yum install -y git docker docker-compose  # Rocky Linux/CentOS
# O para Ubuntu:
# sudo apt install -y git docker.io docker-compose

# Iniciar Docker
sudo systemctl start docker
sudo systemctl enable docker

# Clonar repositorio
cd /home/tu_usuario/
git clone https://github.com/tu-usuario/tu-repo.git server
cd server

# Crear archivo .env basado en EJEMPLO.env
cp EJEMPLO.env .env
nano .env  # Editar con valores del nuevo servidor

# Si usas HTTPS, obtener certificados
# (Ver GUIA_COMPLETA_HTTPS.md)

# Instalar y ejecutar
sudo bash install.sh
```

**Ventajas:**
- ✅ Control de versiones
- ✅ Fácil actualizar: `git pull && sudo bash install.sh`
- ✅ No copias archivos innecesarios
- ✅ Puedes tener diferentes configuraciones por servidor

---

## Método 2: Exportar Imágenes Docker

Útil cuando:
- El nuevo servidor no tiene internet
- Quieres garantizar exactamente la misma versión
- Los servidores tienen configuración muy similar

### En el Servidor Origen

#### 2.1 Exportar imágenes

```bash
cd /home/sonia.eraso/server

# Exportar imágenes Docker
sudo bash export_images.sh

# Esto crea el directorio docker_images_export/ con:
# - backend.tar (imagen del backend)
# - frontend.tar (imagen del frontend)
# - postgres.tar (imagen de base de datos)
# - nginx.tar (imagen de nginx)

# Comprimir para transferir
tar -czf docker_images.tar.gz docker_images_export/

# Ver tamaño
ls -lh docker_images.tar.gz
```

#### 2.2 Copiar archivos necesarios

Crear un paquete con todo lo necesario:

```bash
# Crear directorio temporal
mkdir -p deployment_package

# Copiar archivos de configuración
cp docker-compose.yml deployment_package/
cp -r nginx/ deployment_package/
cp *.sh deployment_package/
cp *.md deployment_package/
cp EJEMPLO.env deployment_package/

# Copiar imágenes exportadas
mv docker_images.tar.gz deployment_package/

# Comprimir todo
tar -czf deployment_complete.tar.gz deployment_package/

# Ver tamaño final
ls -lh deployment_complete.tar.gz
```

#### 2.3 Transferir al nuevo servidor

```bash
# Opción A: SCP (si tienes acceso SSH)
scp deployment_complete.tar.gz usuario@servidor-nuevo:/tmp/

# Opción B: Usar USB, red compartida, etc.
```

### En el Servidor Nuevo

#### 2.4 Importar e instalar

```bash
# Descomprimir
cd /home/tu_usuario/
tar -xzf /tmp/deployment_complete.tar.gz
mv deployment_package server
cd server

# Descomprimir imágenes
tar -xzf docker_images.tar.gz

# Importar imágenes Docker
sudo bash import_images.sh

# Crear archivo .env
cp EJEMPLO.env .env
nano .env  # Configurar valores del nuevo servidor

# Configurar nginx si usas dominio diferente
nano nginx/ssl.conf  # Cambiar dominio

# Si usas HTTPS, copiar o generar certificados
# sudo mkdir -p /etc/letsencrypt/live/tu-dominio/
# sudo cp certificados/* /etc/letsencrypt/live/tu-dominio/

# Iniciar servicios
sudo bash start.sh
```

**Ventajas:**
- ✅ No necesita rebuild (más rápido)
- ✅ Funciona sin internet
- ✅ Garantiza misma versión exacta

**Desventajas:**
- ❌ Archivos muy grandes (varios GB)
- ❌ Menos flexible para cambios
- ❌ Difícil actualizar

---

## Método 3: Copiar Directorio Completo

El método más simple pero menos eficiente.

### Qué Copiar

```bash
cd /home/sonia.eraso

# Opción A: Copiar todo excepto datos de postgres
tar --exclude='server/postgres_data' \
    --exclude='server/node_modules' \
    --exclude='server/frontend/dist' \
    --exclude='server/backend/__pycache__' \
    -czf server_backup.tar.gz server/

# Opción B: Copiar solo lo esencial
tar -czf server_minimal.tar.gz \
    server/docker-compose.yml \
    server/backend/ \
    server/frontend/ \
    server/nginx/ \
    server/*.sh \
    server/*.md \
    server/EJEMPLO.env
```

### En el Servidor Nuevo

```bash
# Copiar archivo
scp server_backup.tar.gz usuario@servidor-nuevo:/home/tu_usuario/

# Descomprimir
cd /home/tu_usuario/
tar -xzf server_backup.tar.gz

cd server/

# Editar .env con configuración del nuevo servidor
nano .env

# Instalar
sudo bash install.sh
```

**Ventajas:**
- ✅ Muy simple
- ✅ Incluye todo

**Desventajas:**
- ❌ Muy grande (incluye cosas innecesarias)
- ❌ Copia posibles datos sensibles
- ❌ Puede incluir configuraciones del servidor viejo

---

## Configuración Post-Despliegue

Independientemente del método usado, verifica:

### 1. Configurar .env

```bash
cd /home/tu_usuario/server
nano .env
```

Cambiar:
- `ALLOWED_HOSTS` - IP y dominio del nuevo servidor
- `POSTGRES_PASSWORD` - Nueva contraseña segura
- `SECRET_KEY` - Nueva clave secreta
- `CORS_ALLOWED_ORIGINS` - URLs del nuevo servidor
- `CSRF_TRUSTED_ORIGINS` - URLs del nuevo servidor

### 2. Configurar Firewall

```bash
# Rocky Linux/CentOS
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload

# Ubuntu
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```

### 3. Configurar HTTPS (si aplica)

Si el nuevo servidor tiene dominio diferente:

```bash
# 1. Obtener nuevo dominio en DuckDNS (o tu proveedor DNS)
# 2. Apuntar a la IP del nuevo servidor

# 3. Obtener certificados SSL
cd ~
export DuckDNS_Token="TU_TOKEN"
~/.acme.sh/acme.sh --issue --dns dns_duckdns -d nuevo-dominio.duckdns.org

# 4. Copiar certificados
sudo mkdir -p /etc/letsencrypt/live/nuevo-dominio.duckdns.org
sudo cp ~/.acme.sh/nuevo-dominio.duckdns.org/fullchain.cer \
  /etc/letsencrypt/live/nuevo-dominio.duckdns.org/fullchain.pem
sudo cp ~/.acme.sh/nuevo-dominio.duckdns.org/nuevo-dominio.duckdns.org.key \
  /etc/letsencrypt/live/nuevo-dominio.duckdns.org/privkey.pem

# 5. Actualizar nginx/ssl.conf
cd /home/tu_usuario/server
sed -i 's/gestiondato.duckdns.org/nuevo-dominio.duckdns.org/g' nginx/ssl.conf

# 6. Reinstalar
sudo bash install.sh
```

### 4. Verificar Funcionamiento

```bash
# Ver estado
sudo docker compose ps

# Ver logs
sudo docker compose logs -f

# Probar acceso
curl -k https://localhost/
curl -k http://localhost/

# Desde navegador
# http://IP_NUEVO_SERVIDOR
# https://nuevo-dominio.duckdns.org
```

---

## 🎯 Recomendaciones Finales

### Para Producción (Múltiples Servidores)
✅ **Usa Git (Método 1)**
- Crea repositorio privado en GitHub/GitLab
- Usa `.env` diferentes por servidor
- Configura CI/CD para deployments automáticos

### Para Servidor de Respaldo (Sin Internet)
✅ **Usa Imágenes Docker (Método 2)**
- Exporta imágenes periódicamente
- Mantén respaldo de certificados SSL
- Documenta configuraciones específicas

### Para Pruebas Rápidas
✅ **Copiar Directorio (Método 3)**
- Solo en entornos de desarrollo
- No uses para producción
- Limpia datos sensibles antes de copiar

---

## 📝 Checklist de Migración

Antes de dar por completada la migración:

- [ ] Servicios Docker iniciados correctamente
- [ ] Base de datos accesible y con datos (si aplica)
- [ ] Frontend accesible desde navegador
- [ ] Login funcionando
- [ ] API respondiendo correctamente
- [ ] HTTPS configurado (si aplica)
- [ ] Certificados SSL válidos (si aplica)
- [ ] Firewall configurado
- [ ] Backup configurado en nuevo servidor
- [ ] Documentación actualizada con nueva configuración

---

## 🆘 Problemas Comunes

### Error: "Cannot connect to Docker daemon"
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Error: "Port already in use"
```bash
# Ver qué usa el puerto
sudo netstat -tulpn | grep :80
sudo ss -tulpn | grep :80

# Detener proceso
sudo systemctl stop httpd  # Si es Apache
sudo systemctl stop nginx  # Si es Nginx
```

### Error: Base de datos no inicia
```bash
# Verificar permisos
sudo chown -R 999:999 postgres_data/

# Ver logs
sudo docker compose logs postgres

# Reiniciar
sudo docker compose restart postgres
```

### Error: Frontend no carga
```bash
# Verificar que VITE_API_URL esté vacío
grep VITE_API_URL .env

# Rebuild frontend
sudo docker compose build frontend --no-cache
sudo docker compose restart frontend
```

---

**Última actualización**: 2025-11-10
