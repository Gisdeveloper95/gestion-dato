# 🔒 GUÍA COMPLETA: CONFIGURACIÓN HTTPS CON DUCKDNS Y LET'S ENCRYPT

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Paso 1: Obtener Dominio DuckDNS](#paso-1-obtener-dominio-duckdns)
3. [Paso 2: Configurar Firewall](#paso-2-configurar-firewall)
4. [Paso 3: Obtener Certificados SSL](#paso-3-obtener-certificados-ssl)
5. [Paso 4: Configurar Variables de Entorno](#paso-4-configurar-variables-de-entorno)
6. [Paso 5: Reconstruir y Desplegar](#paso-5-reconstruir-y-desplegar)
7. [Verificación](#verificación)
8. [Cambiar de Dominio](#cambiar-de-dominio)
9. [Renovación Automática de Certificados](#renovación-automática-de-certificados)
10. [Solución de Problemas](#solución-de-problemas)

---

## 🚀 Scripts de Gestión Rápida

La aplicación incluye 3 scripts para gestión simplificada:

| Script | Uso | Descripción |
|--------|-----|-------------|
| `install.sh` | `sudo bash install.sh` | Instalación completa desde cero |
| `start.sh` | `sudo bash start.sh` | Iniciar todos los servicios |
| `stop.sh` | `sudo bash stop.sh` | Detener todos los servicios |

**Ubicación**: `/home/sonia.eraso/server/`

---

## Requisitos Previos

- ✅ Servidor Linux (Rocky Linux, CentOS, Ubuntu, etc.)
- ✅ Docker y Docker Compose instalados
- ✅ Aplicación funcionando en HTTP
- ✅ Acceso root o sudo
- ✅ IP pública del servidor

---

## Paso 1: Obtener Dominio DuckDNS

### 1.1 Crear Cuenta en DuckDNS

1. Ve a: https://www.duckdns.org/
2. Inicia sesión con una de las opciones (GitHub, Google, etc.)
3. Anota tu **Token** (lo necesitarás después)

### 1.2 Crear Subdominio

1. En el campo "sub domain", escribe el nombre que quieras (ej: `gestiondato`)
2. En "current ip", ingresa la **IP pública** de tu servidor
3. Haz clic en "add domain"
4. Tu dominio será: `tusubdominio.duckdns.org`

### 1.3 Verificar IP Pública

```bash
# Obtener tu IP pública
curl ifconfig.me
```

**IMPORTANTE**: Si tu servidor está detrás de NAT corporativo, necesitas:
- Configurar port forwarding en el firewall: `IP_PUBLICA:80` → `IP_SERVIDOR:80` y `IP_PUBLICA:443` → `IP_SERVIDOR:443`
- Actualizar DuckDNS con la IP pública (no la interna)

---

## Paso 2: Configurar Firewall

### 2.1 Abrir Puertos en el Firewall del Servidor

```bash
# Para firewalld (Rocky Linux, CentOS)
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload

# Verificar
sudo firewall-cmd --list-ports
```

```bash
# Para ufw (Ubuntu)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload

# Verificar
sudo ufw status
```

### 2.2 Verificar Acceso Externo

Desde otra computadora fuera de tu red:
```bash
curl http://tusubdominio.duckdns.org
```

Si no funciona, verifica el port forwarding en tu router/firewall corporativo.

---

## Paso 3: Obtener Certificados SSL

### 3.1 Instalar acme.sh

```bash
cd ~
curl https://get.acme.sh | sh
source ~/.bashrc
```

### 3.2 Obtener Certificados con DNS Verification

```bash
# Establecer token de DuckDNS
export DuckDNS_Token="TU_TOKEN_AQUI"

# Obtener certificado
~/.acme.sh/acme.sh --issue --dns dns_duckdns -d tusubdominio.duckdns.org
```

**Espera 2-3 minutos** para que DNS se propague.

### 3.3 Copiar Certificados a /etc/letsencrypt

```bash
# Crear directorios
sudo mkdir -p /etc/letsencrypt/live/tusubdominio.duckdns.org

# Copiar certificados
sudo cp ~/.acme.sh/tusubdominio.duckdns.org/fullchain.cer \
  /etc/letsencrypt/live/tusubdominio.duckdns.org/fullchain.pem

sudo cp ~/.acme.sh/tusubdominio.duckdns.org/tusubdominio.duckdns.org.key \
  /etc/letsencrypt/live/tusubdominio.duckdns.org/privkey.pem

sudo cp ~/.acme.sh/tusubdominio.duckdns.org/tusubdominio.duckdns.org.cer \
  /etc/letsencrypt/live/tusubdominio.duckdns.org/cert.pem

# Permisos correctos
sudo chmod 600 /etc/letsencrypt/live/tusubdominio.duckdns.org/privkey.pem
sudo chmod 644 /etc/letsencrypt/live/tusubdominio.duckdns.org/*.pem

# Verificar
sudo ls -la /etc/letsencrypt/live/tusubdominio.duckdns.org/
```

---

## Paso 4: Configurar Variables de Entorno

### 4.1 Editar el archivo `.env`

```bash
cd /home/sonia.eraso/server
nano .env
```

### 4.2 Configurar las siguientes variables:

```bash
# === DJANGO BACKEND ===
DEBUG=False
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
ALLOWED_HOSTS=*,tusubdominio.duckdns.org,localhost,127.0.0.1,IP_SERVIDOR,backend

# === CORS Y CSRF ===
CORS_ALLOWED_ORIGINS=https://tusubdominio.duckdns.org,http://tusubdominio.duckdns.org
CSRF_TRUSTED_ORIGINS=https://tusubdominio.duckdns.org,http://tusubdominio.duckdns.org

# === FRONTEND ===
# URL vacía = usa paths relativos (funciona con HTTP y HTTPS)
VITE_API_URL=
```

**IMPORTANTE**:
- `VITE_API_URL=` debe estar **vacío** (sin valor)
- Reemplaza `tusubdominio` con tu dominio real
- Reemplaza `IP_SERVIDOR` con la IP interna de tu servidor

---

## Paso 5: Reconstruir y Desplegar

### 5.1 Actualizar nginx/ssl.conf

Edita `/home/sonia.eraso/server/nginx/ssl.conf` y reemplaza **todas las ocurrencias** de `gestiondato.duckdns.org` con tu dominio:

```bash
cd /home/sonia.eraso/server
sed -i 's/gestiondato.duckdns.org/tusubdominio.duckdns.org/g' nginx/ssl.conf
```

### 5.2 Instalación Completa

Usa el script de instalación automática:

```bash
cd /home/sonia.eraso/server
sudo bash install.sh
```

Este script realiza:
- Detención de servicios existentes
- Limpieza completa del sistema Docker
- Build de todas las imágenes sin caché
- Inicio de servicios
- Verificación automática

**Alternativa manual:**

```bash
cd /home/sonia.eraso/server

# Detener todo
sudo docker compose down

# Limpiar imágenes antiguas
sudo docker system prune -a -f

# Rebuild sin caché
sudo docker compose build --no-cache

# Levantar servicios
sudo docker compose up -d

# Esperar que inicien
sleep 20

# Verificar estado
sudo docker compose ps
```

---

## Verificación

### 6.1 Verificar Servicios

```bash
# Ver estado de contenedores
sudo docker compose ps

# Ver logs del backend
sudo docker compose logs backend --tail 30

# Ver logs de nginx
sudo docker compose logs nginx-proxy --tail 30
```

### 6.2 Probar Acceso

#### Desde el servidor:
```bash
# HTTP
curl -k http://localhost/

# HTTPS
curl -k https://localhost/
```

#### Desde tu navegador:

1. **HTTP por IP**: `http://IP_SERVIDOR`
   - ✅ Debe funcionar sin redirección

2. **HTTPS por dominio**: `https://tusubdominio.duckdns.org`
   - ✅ Debe mostrar candado verde
   - ✅ Certificado válido de Let's Encrypt

### 6.3 Verificar Login

Prueba hacer login desde:
- ✅ Tu PC local
- ✅ Otra PC en la red
- ✅ PC externa (otra ciudad/red)

---

## Cambiar de Dominio

Si necesitas cambiar de dominio (por ejemplo, compras un dominio propio), es muy simple:

### Opción A: Nuevo Dominio DuckDNS

1. Crea nuevo subdominio en DuckDNS
2. Obtén nuevos certificados:
   ```bash
   ~/.acme.sh/acme.sh --issue --dns dns_duckdns -d nuevodominio.duckdns.org
   ```
3. Copia certificados a `/etc/letsencrypt/live/nuevodominio.duckdns.org/`
4. Actualiza `.env`:
   ```bash
   ALLOWED_HOSTS=*,nuevodominio.duckdns.org,...
   CORS_ALLOWED_ORIGINS=https://nuevodominio.duckdns.org,...
   CSRF_TRUSTED_ORIGINS=https://nuevodominio.duckdns.org,...
   ```
5. Actualiza `nginx/ssl.conf`:
   ```bash
   sed -i 's/viejodominio.duckdns.org/nuevodominio.duckdns.org/g' nginx/ssl.conf
   ```
6. Rebuild frontend y reinicia nginx:
   ```bash
   sudo docker compose build frontend --no-cache
   sudo docker compose restart nginx-proxy frontend
   ```

### Opción B: Dominio Propio (ej: miempresa.com)

1. Configura DNS de tu dominio para apuntar a tu IP pública
2. Obtén certificados usando otro método de verificación:
   ```bash
   ~/.acme.sh/acme.sh --issue -d miempresa.com --webroot /var/www/html
   ```
   O usa Certbot:
   ```bash
   sudo certbot certonly --standalone -d miempresa.com
   ```
3. Sigue los mismos pasos de "Opción A" pero con tu dominio

---

## Renovación Automática de Certificados

### 9.1 Configurar Cron Job

Los certificados de Let's Encrypt expiran cada 90 días. Configura renovación automática:

```bash
# Editar crontab
crontab -e

# Agregar esta línea (renueva cada día a las 2 AM)
0 2 * * * ~/.acme.sh/acme.sh --cron --home ~/.acme.sh && \
  sudo cp ~/.acme.sh/tusubdominio.duckdns.org/fullchain.cer /etc/letsencrypt/live/tusubdominio.duckdns.org/fullchain.pem && \
  sudo cp ~/.acme.sh/tusubdominio.duckdns.org/tusubdominio.duckdns.org.key /etc/letsencrypt/live/tusubdominio.duckdns.org/privkey.pem && \
  sudo docker compose -f /home/sonia.eraso/server/docker-compose.yml restart nginx-proxy
```

### 9.2 Verificar Renovación Manual

```bash
# Probar renovación
~/.acme.sh/acme.sh --cron --force --home ~/.acme.sh

# Copiar certificados renovados
sudo cp ~/.acme.sh/tusubdominio.duckdns.org/fullchain.cer \
  /etc/letsencrypt/live/tusubdominio.duckdns.org/fullchain.pem

sudo cp ~/.acme.sh/tusubdominio.duckdns.org/tusubdominio.duckdns.org.key \
  /etc/letsencrypt/live/tusubdominio.duckdns.org/privkey.pem

# Reiniciar nginx
sudo docker compose restart nginx-proxy
```

---

## Solución de Problemas

### Problema 1: "Mixed Content" Error

**Error**: `Mixed Content: The page at 'https://...' was loaded over HTTPS, but requested an insecure XMLHttpRequest endpoint 'http://...'`

**Solución**:
- Verifica que `VITE_API_URL=` esté **vacío** en `.env`
- Rebuild frontend: `sudo docker compose build frontend --no-cache`
- Limpia caché del navegador o usa ventana de incógnito

### Problema 2: 404 en /api-token-auth/

**Solución**:
- Verifica que `nginx/ssl.conf` tenga las rutas:
  ```nginx
  location /api-token-auth/ { ... }
  location /preoperacion/ { ... }
  location /postoperacion/ { ... }
  ```
- Reinicia nginx: `sudo docker compose restart nginx-proxy`

### Problema 3: Connection Timeout Externo

**Diagnóstico**:
```bash
# Verificar IP pública
curl ifconfig.me

# Verificar DNS
nslookup tusubdominio.duckdns.org
```

**Solución**:
- Verifica que DuckDNS tenga la IP pública correcta
- Verifica port forwarding en firewall/router
- Verifica puertos abiertos: `sudo firewall-cmd --list-ports`

### Problema 4: "ERR_CERT_AUTHORITY_INVALID"

**Solución**:
- Verifica que los certificados se copiaron correctamente:
  ```bash
  sudo ls -la /etc/letsencrypt/live/tusubdominio.duckdns.org/
  ```
- Verifica permisos: `sudo chmod 600 /etc/letsencrypt/live/*/privkey.pem`
- Reinicia nginx: `sudo docker compose restart nginx-proxy`

### Problema 5: CORS Error desde Otra PC

**Solución**:
- Verifica que `CORS_ALLOW_ALL_ORIGINS = True` en `backend/backend/settings.py`
- Verifica que CSRF esté desactivado (comentado en MIDDLEWARE)
- Rebuild backend: `sudo docker compose build backend --no-cache`

---

## 📝 Resumen de Archivos Importantes

### Archivos de Configuración

| Archivo | Propósito |
|---------|----------|
| `.env` | Variables de entorno (dominios, URLs, etc.) |
| `nginx/ssl.conf` | Configuración de nginx con SSL |
| `backend/backend/settings.py` | CORS, CSRF, ALLOWED_HOSTS |
| `frontend/Dockerfile` | Build del frontend con variables de entorno |
| `docker-compose.yml` | Orquestación de servicios |

### Scripts de Gestión

La aplicación incluye 3 scripts esenciales en `/home/sonia.eraso/server/`:

#### 1. **install.sh** - Instalación completa desde cero
```bash
cd /home/sonia.eraso/server
sudo bash install.sh
```
Realiza:
- Detención de servicios
- Limpieza completa de Docker
- Build sin caché
- Inicio y verificación

#### 2. **start.sh** - Iniciar servicios
```bash
cd /home/sonia.eraso/server
sudo bash start.sh
```
Inicia todos los servicios con verificación de estado.

#### 3. **stop.sh** - Detener servicios
```bash
cd /home/sonia.eraso/server
sudo bash stop.sh
```
Detiene servicios de forma ordenada y segura.

### Comandos Útiles Adicionales

```bash
# Ver logs en tiempo real
sudo docker compose logs -f backend
sudo docker compose logs -f nginx-proxy

# Reiniciar servicios individuales
sudo docker compose restart nginx-proxy
sudo docker compose restart backend
sudo docker compose restart frontend

# Rebuild específico
sudo docker compose build backend --no-cache
sudo docker compose build frontend --no-cache

# Ver estado
sudo docker compose ps

# Verificar certificados
sudo openssl x509 -in /etc/letsencrypt/live/tusubdominio.duckdns.org/cert.pem -text -noout

# Verificar HTTPS
curl -vI https://tusubdominio.duckdns.org 2>&1 | grep -i ssl
```

---

## ✅ Checklist Final

Antes de considerar la configuración completa, verifica:

- [ ] DuckDNS configurado con IP correcta
- [ ] Puertos 80 y 443 abiertos en firewall
- [ ] Certificados SSL obtenidos y copiados
- [ ] `.env` actualizado con dominio correcto
- [ ] `nginx/ssl.conf` actualizado con dominio
- [ ] Frontend y backend reconstruidos
- [ ] HTTPS funciona desde navegador externo
- [ ] Login funciona desde múltiples PCs
- [ ] No hay errores de "Mixed Content"
- [ ] Renovación automática de certificados configurada

---

## 🎉 ¡Felicitaciones!

Tu aplicación ahora está:
- ✅ Accesible por HTTPS con certificado válido
- ✅ Funcionando desde cualquier PC (local o remota)
- ✅ Protegida con SSL/TLS
- ✅ Lista para producción

**Dominio actual**: https://gestiondato.duckdns.org

---

## 📞 Soporte

Si tienes problemas:
1. Revisa la sección "Solución de Problemas"
2. Verifica los logs: `sudo docker compose logs`
3. Consulta la documentación de Docker/nginx

---

**Última actualización**: 2025-11-10
**Versión**: 1.0
