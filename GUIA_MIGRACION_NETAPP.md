# 📦 Guía de Migración NetApp a Nuevo Servidor

## 🎯 Archivos Necesarios para la Migración

### Archivos a copiar al nuevo servidor:
1. `setup_netapp_mount.sh` - Script de configuración automatizada
2. `NETAPP_MOUNT.env` - Archivo de configuración (EDITAR con nuevos valores)
3. `NETAPP_MOUNT.env.example` - Archivo de referencia

---

## 🔧 Pasos para Migrar

### 1️⃣ En el Servidor Actual (Documentar)
```bash
# Obtener información del usuario Linux actual
id sonia.eraso

# Ver configuración actual del montaje
mount | grep cifs

# Verificar permisos de archivos
ls -la /mnt/repositorio
```

### 2️⃣ En el Nuevo Servidor (Configurar)

#### A. Copiar archivos necesarios
```bash
# Copiar los archivos al nuevo servidor en /ruta/del/proyecto/
scp setup_netapp_mount.sh usuario@nuevo_servidor:/ruta/proyecto/
scp NETAPP_MOUNT.env usuario@nuevo_servidor:/ruta/proyecto/
scp NETAPP_MOUNT.env.example usuario@nuevo_servidor:/ruta/proyecto/
```

#### B. Obtener el UID y GID del nuevo usuario
```bash
# En el nuevo servidor
id nombre_usuario_nuevo
# Ejemplo de salida: uid=1005(usuario) gid=1003(grupo)
```

#### C. Editar el archivo NETAPP_MOUNT.env
```bash
cd /ruta/proyecto/
nano NETAPP_MOUNT.env
```

**Variables a cambiar:**
```bash
# === CREDENCIALES WINDOWS (CAMBIAR) ===
NETAPP_USERNAME=nuevo.usuario@igac.gov.co    # ← Usuario Windows nuevo
NETAPP_PASSWORD=password_del_nuevo_usuario    # ← Password Windows nuevo
NETAPP_DOMAIN=IGAC                            # ← Probablemente igual

# === USUARIO LINUX (CAMBIAR) ===
NETAPP_UID=1005    # ← Del comando 'id' (nuevo servidor)
NETAPP_GID=1003    # ← Del comando 'id' (nuevo servidor)

# === RUTAS (VERIFICAR) ===
NETAPP_SERVER_IP=172.21.54.13      # ← Verificar si cambia
NETAPP_SHARE_PATH=DirGesCat        # ← Probablemente igual
NETAPP_MOUNT_POINT=/mnt/repositorio # ← Verificar si cambia
```

#### D. Ejecutar el script de montaje
```bash
# Dar permisos de ejecución si es necesario
chmod +x setup_netapp_mount.sh

# Ejecutar el script (pedirá sudo)
./setup_netapp_mount.sh
```

#### E. Verificar el montaje
```bash
# Ver que esté montado
mount | grep cifs

# Verificar contenido
ls -la /mnt/repositorio

# Verificar entrada en fstab (para que persista)
grep netapp /etc/fstab
```

---

## 📋 Checklist de Migración

- [ ] Documentar UID y GID del usuario actual
- [ ] Documentar credenciales Windows actuales
- [ ] Copiar archivos al nuevo servidor
- [ ] Obtener UID y GID del nuevo usuario Linux
- [ ] Obtener credenciales Windows del nuevo usuario
- [ ] Editar `NETAPP_MOUNT.env` con nuevos valores
- [ ] Ejecutar `./setup_netapp_mount.sh`
- [ ] Verificar montaje con `mount | grep cifs`
- [ ] Verificar acceso a archivos `ls -la /mnt/repositorio`
- [ ] Verificar entrada en `/etc/fstab`
- [ ] Probar reinicio del servidor
- [ ] Verificar que el montaje persiste después del reinicio

---

## 🆘 Solución de Problemas

### Error: "Permission denied"
```bash
# Verificar que el UID/GID sean correctos
id nombre_usuario
# Actualizar en NETAPP_MOUNT.env
```

### Error: "mount error(13): Permission denied"
```bash
# Verificar credenciales Windows
# Probar manualmente:
smbclient //172.21.54.13/DirGesCat -U usuario@igac.gov.co
```

### Montaje no persiste después de reinicio
```bash
# Verificar entrada en fstab
cat /etc/fstab | grep netapp
# Si no existe, ejecutar de nuevo el script
./setup_netapp_mount.sh
```

---

## 📝 Valores Actuales (Servidor Original)

```bash
NETAPP_SERVER_IP=172.21.54.13
NETAPP_SHARE_PATH=DirGesCat
NETAPP_MOUNT_POINT=/mnt/repositorio
NETAPP_USERNAME=andres.osorio@igac.gov.co
NETAPP_DOMAIN=IGAC
NETAPP_UID=1004
NETAPP_GID=1002
```

---

## ⚠️ IMPORTANTE

1. **NO subir `NETAPP_MOUNT.env` a Git** - Contiene credenciales
2. **Mantener permisos seguros**: `chmod 600 NETAPP_MOUNT.env`
3. **Las credenciales se guardan en**: `/root/.netapp_credentials` (permisos 600)
4. **Probar siempre después de un reinicio** para verificar persistencia
