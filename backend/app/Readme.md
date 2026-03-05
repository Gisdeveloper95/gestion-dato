# App de Ejecución de Scripts

Esta aplicación Django permite ejecutar scripts de manera controlada a través de endpoints API, con funcionalidades específicas para crear backups de base de datos y descargarlos como archivos ZIP.

## 🚀 Características Principales

- **Ejecución Asíncrona**: Los scripts se ejecutan en hilos separados para no bloquear la API
- **Tracking Completo**: Registro de todas las ejecuciones con estados, tiempos y resultados
- **Descargas ZIP**: Empaquetado automático de backups para descarga
- **API REST**: Endpoints completos para gestión y monitoreo
- **Autenticación**: Control de acceso basado en tokens
- **Limpieza Automática**: Posibilidad de limpiar directorios antes de ejecutar scripts

## 📁 Estructura de Archivos

```
backend/
├── Scripts/                    # Directorio con los scripts (al nivel de backend)
│   ├── copia_Seguridad_db.py
│   └── llenar_datos_dir_pre_&_post.py
├── app/                        # Nueva aplicación Django
│   ├── models.py              # Modelos para tracking
│   ├── views.py               # Views de la API
│   ├── serializers.py         # Serializers REST
│   ├── utils.py               # Utilidades para ejecutar scripts
│   ├── urls.py                # URLs de la aplicación
│   ├── admin.py               # Configuración del admin
│   └── management/            # Comandos de Django
│       └── commands/
│           └── run_script.py
└── backups/                   # Directorio donde se guardan los backups
```

## ⚙️ Instalación y Configuración

### 1. Agregar la app a INSTALLED_APPS

```python
# En backend/settings.py
INSTALLED_APPS = [
    # ... otras apps
    'app',  # Agregar esta línea
    # ... resto de apps
]
```

### 2. Incluir las URLs

```python
# En backend/urls.py
urlpatterns = [
    # ... otras URLs
    path('scripts/', include('app.urls')),  # Agregar esta línea
    # ... resto de URLs
]
```

### 3. Ejecutar migraciones

```bash
# Crear migraciones
python manage.py makemigrations app

# Aplicar migraciones
python manage.py migrate
```

### 4. Crear superusuario (si no existe)

```bash
python manage.py createsuperuser
```

## 🔌 Endpoints API

### Autenticación
- `POST /api-token-auth/` - Obtener token de autenticación

### Ejecuciones de Scripts
- `GET /scripts/api/executions/` - Listar todas las ejecuciones
- `POST /scripts/api/executions/` - Crear nueva ejecución (asíncrona)
- `GET /scripts/api/executions/{id}/` - Detalle de ejecución específica
- `POST /scripts/api/executions/{id}/retry/` - Reintentar ejecución
- `GET /scripts/api/executions/status_summary/` - Resumen de estado de scripts

### Backups Específicos
- `GET /scripts/api/backup/status/` - Estado general de backups
- `POST /scripts/api/backup/execute/` - Ejecutar backup (síncrono)
- `GET /scripts/api/backup/download-zip/` - Descargar último backup como ZIP
- `GET /scripts/api/backup/files/` - Listar archivos de backup
- `GET /scripts/api/backup/files/{id}/download/` - Descargar archivo específico
- `DELETE /scripts/api/backup/clean/` - Limpiar directorio de backups

## 💻 Uso desde la Línea de Comandos

```bash
# Ejecutar backup con limpieza previa
python manage.py run_script backup_db --clean-backup-dir --user admin

# Ejecutar script de datos
python manage.py run_script llenar_datos --user admin
```

## 🌐 Ejemplos de Uso con curl

### 1. Autenticarse y obtener token

```bash
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "tu_usuario", "password": "tu_password"}'
```

### 2. Ejecutar backup de forma asíncrona

```bash
curl -X POST http://localhost:8000/scripts/api/executions/ \
  -H "Authorization: Token tu_token_aqui" \
  -H "Content-Type: application/json" \
  -d '{"script_name": "backup_db"}'
```

### 3. Descargar backup como ZIP

```bash
curl -X GET http://localhost:8000/scripts/api/backup/download-zip/ \
  -H "Authorization: Token tu_token_aqui" \
  -o backup.zip
```

## 🔧 Scripts Soportados

### 1. backup_db - Copia de Seguridad de Base de Datos
- **Descripción**: Crea una copia de seguridad de la base de datos PostgreSQL
- **Funcionalidad**: 
  - Limpia el directorio de backups antes de ejecutar
  - Intenta múltiples métodos de backup (pg_dump, psycopg2, etc.)
  - Registra los archivos creados en la base de datos
- **Archivos generados**: `.sql` o `.sql.gz`

### 2. llenar_datos - Llenar Datos de Directorios
- **Descripción**: Procesa rutas de municipios y actualiza las tablas correspondientes
- **Funcionalidad**:
  - Busca rutas en el sistema de archivos
  - Actualiza tablas `path_dir_pre` y `path_dir_post`
  - Maneja errores de acceso a red y archivos

## 📊 Monitoreo y Estados

### Estados de Ejecución
- `pending`: Pendiente de ejecución
- `running`: Ejecutándose actualmente
- `completed`: Completado exitosamente
- `failed`: Falló durante la ejecución

### Información Tracked
- Usuario que ejecutó el script
- Tiempos de inicio y finalización
- Archivos generados
- Logs de salida y errores
- Duración de ejecución

## 🛡️ Seguridad

- **Autenticación requerida**: Todos los endpoints requieren token de autenticación
- **Timeouts**: Scripts tienen límites de tiempo para evitar ejecuciones infinitas
- **Logging**: Todas las operaciones se registran para auditoría
- **Validación**: Validación estricta de nombres de scripts permitidos

## 🚨 Troubleshooting

### Error: "Script no encontrado"
- Verificar que el directorio `Scripts` existe al nivel del directorio `backend`
- Confirmar que los archivos de script tienen los nombres exactos esperados

### Error: "Error de permisos al acceder a archivos"
- Verificar permisos del directorio `backups`
- En Windows, verificar acceso a recursos de red compartidos

### Error: "pg_dump no encontrado"
- El script intentará múltiples métodos de backup automáticamente
- Verificar instalación de PostgreSQL o instalar `psycopg2-binary`

### Timeout en ejecución
- Los scripts tienen timeouts configurados (5-10 minutos)
- Para scripts que requieren más tiempo, ajustar en `utils.py`

## 📈 Futuras Mejoras

- [ ] Interfaz web para gestión visual
- [ ] Programación de ejecuciones automáticas
- [ ] Notificaciones por email/webhook
- [ ] Compresión automática de backups antiguos
- [ ] Integración con sistemas de almacenamiento en la nube
- [ ] Métricas y dashboards de performance

## 🤝 Contribución

Para agregar nuevos scripts:

1. Agregar el script al directorio `Scripts/`
2. Incluir el nombre en `SCRIPT_CHOICES` en `models.py`
3. Implementar la lógica de ejecución en `utils.py`
4. Actualizar la documentación

## 📝 Logs

Los logs se almacenan en:
- **Django logs**: Configuración estándar de logging de Django
- **Base de datos**: Campo `output_log` en el modelo `ScriptExecution`
- **Archivos de sistema**: Según configuración del script individual