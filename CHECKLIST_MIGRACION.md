# ✅ CHECKLIST DE MIGRACIÓN RÁPIDA

## 📦 ANTES DE MIGRAR (Servidor Actual)

```bash
# 1. Backup de Base de Datos
[ ] pg_dump gestion_dato_db → archivo .sql.gz

# 2. Guardar Configuraciones Secretas
[ ] TELEGRAM_TOKEN guardado
[ ] GROQ_API_KEY guardado
[ ] DB_PASSWORD guardado
[ ] SECRET_KEY guardado
[ ] NETAPP credenciales guardadas
[ ] DUCKDNS_TOKEN guardado (si aplica)

# 3. Documentar Configuración Actual
[ ] IP actual anotada
[ ] Dominio actual anotado
[ ] Usuario Linux actual anotado
[ ] NetApp IP y share anotados
```

## 🆕 EN SERVIDOR NUEVO

### Fase 1: Instalación Base (15 min)
```bash
[ ] 1. Instalar: git, docker, postgresql, cifs-utils
[ ] 2. Iniciar y habilitar Docker
[ ] 3. Iniciar y habilitar PostgreSQL
[ ] 4. Agregar usuario a grupo docker
[ ] 5. Configurar firewall (80, 443, 8000)
```

### Fase 2: Transferencia de Código (10 min)
```bash
[ ] 6. Clonar repositorio o copiar código con scp
[ ] 7. Extraer archivos en /home/NUEVO_USUARIO/server
```

### Fase 3: Configuración de Variables (20 min)
```bash
[ ] 8. Copiar EJEMPLO.env → .env
[ ] 9. Editar .env (NUEVO dominio, IP, hosts)
[ ] 10. Copiar y editar backend/.env
[ ] 11. Copiar automation/.env.example → automation/.env
[ ] 12. Editar automation/.env (usuario, tokens, paths)
[ ] 13. Copiar NETAPP_MOUNT.env.example → NETAPP_MOUNT.env
[ ] 14. Editar NETAPP_MOUNT.env (IP, usuario, password)
```

### Fase 4: Base de Datos (10 min)
```bash
[ ] 15. Crear usuario PostgreSQL
[ ] 16. Crear base de datos gestion_dato_db
[ ] 17. Restaurar backup .sql
[ ] 18. Verificar: psql -h localhost -U postgres -d gestion_dato_db -c "\dt"
```

### Fase 5: NetApp (10 min)
```bash
[ ] 19. Ejecutar: bash setup_netapp_mount.sh
[ ] 20. Verificar montaje: ls /mnt/repositorio
[ ] 21. Probar escritura (si aplica)
[ ] 22. Verificar entrada en /etc/fstab
```

### Fase 6: SSL/HTTPS (15 min) - Si aplica
```bash
[ ] 23. Obtener nuevo dominio DuckDNS
[ ] 24. Apuntar dominio a nueva IP
[ ] 25. Instalar acme.sh
[ ] 26. Obtener certificado SSL con acme.sh
[ ] 27. Copiar certificados a /etc/letsencrypt/live/
[ ] 28. Actualizar nginx/ssl.conf con nuevo dominio
```

### Fase 7: Servicios Systemd (5 min)
```bash
[ ] 29. Actualizar usuario en archivos .service
[ ] 30. Copiar .service a /etc/systemd/system/
[ ] 31. systemctl daemon-reload
[ ] 32. Habilitar servicios (telegram-bot, scheduler, cleanup)
```

### Fase 8: Despliegue Docker (10 min)
```bash
[ ] 33. bash install.sh
[ ] 34. Verificar containers: docker ps
[ ] 35. Ver logs: docker logs igac_backend
[ ] 36. Ver logs: docker logs igac_frontend
```

### Fase 9: Verificación (15 min)
```bash
# Web
[ ] 37. Abrir http://NUEVA_IP en navegador
[ ] 38. Abrir https://nuevo-dominio.com
[ ] 39. Hacer login
[ ] 40. Verificar que dashboard carga
[ ] 41. Probar ver un PDF

# API
[ ] 42. curl http://NUEVA_IP/api/
[ ] 43. curl http://NUEVA_IP/api/municipios/

# Base de Datos
[ ] 44. psql -h localhost -U postgres -d gestion_dato_db
[ ] 45. SELECT COUNT(*) FROM app_municipio;

# NetApp
[ ] 46. ls -la /mnt/repositorio/2510SP/

# Bot Telegram
[ ] 47. systemctl status gestion-telegram-bot
[ ] 48. Enviar comando al bot
[ ] 49. Verificar respuesta del bot

# Scheduler
[ ] 50. systemctl status gestion-scheduler
[ ] 51. ls /home/NUEVO_USUARIO/server/automation/logs/
```

## 🔒 LIMPIEZA Y SEGURIDAD

```bash
[ ] 52. Eliminar config_secreto.txt (si existe)
[ ] 53. chmod 600 .env
[ ] 54. chmod 600 backend/.env
[ ] 55. chmod 600 automation/.env
[ ] 56. chmod 600 NETAPP_MOUNT.env
[ ] 57. sudo chmod 600 /root/.netapp_credentials
[ ] 58. Eliminar backups transferidos de /tmp/
[ ] 59. Verificar que .gitignore excluye archivos sensibles
```

## ⏱️ TIEMPO ESTIMADO TOTAL

- **Instalación rápida (sin SSL)**: ~1.5 horas
- **Instalación completa (con SSL)**: ~2 horas
- **Troubleshooting adicional**: +30 min buffer

## 🚨 VALIDACIÓN FINAL

Todo debe estar ✅:
- [ ] Frontend accesible (HTTP y HTTPS)
- [ ] Login funciona
- [ ] API responde
- [ ] PDFs se pueden ver
- [ ] Bot de Telegram responde
- [ ] Scheduler está activo
- [ ] NetApp montado
- [ ] Base de datos con datos

## 📞 EN CASO DE PROBLEMAS

Ver: [GUIA_MIGRACION_PASO_A_PASO.md](GUIA_MIGRACION_PASO_A_PASO.md) sección Troubleshooting

Logs importantes:
```bash
# Docker
docker logs igac_backend -f
docker logs igac_frontend -f
docker logs igac_nginx_proxy -f

# Systemd
journalctl -u gestion-telegram-bot -f
journalctl -u gestion-scheduler -f

# PostgreSQL
sudo tail -f /var/lib/pgsql/data/log/postgresql-*.log
```

---

**Tip**: Imprime este checklist y marca cada item a medida que lo completas.
