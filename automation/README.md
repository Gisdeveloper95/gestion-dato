# Automation System

Sistema de automatizacion para indexacion de archivos y bot de Telegram.

## Estructura

```
automation/
├── .env                    # Configuracion (UNICO archivo de config)
├── .env.example            # Template de configuracion
├── install.sh              # Instalador (genera venv, systemd)
├── diagnose.sh             # Diagnostico del sistema
├── control.sh              # Control de servicios
├── scheduler.py            # Ejecuta scripts segun horarios
├── telegram_bot.py         # Bot de Telegram
├── db_cleaner.py           # Limpieza de BD
├── requirements.txt        # Dependencias Python
├── config/
│   ├── config.example.json # Config de horarios (sin credenciales)
│   └── roles.json          # Roles de usuarios Telegram
├── scripts/                # Scripts de indexacion
│   ├── Script_INSUMOS_Linux.py
│   ├── Script_POST_Linux.py
│   ├── Script_TRANSVERSAL_Linux.py
│   ├── Script_OPERACION_Linux.py
│   └── Script_INDEXAR_VECTORIAL.py
├── systemd/                # Templates systemd (generados por install.sh)
├── utils/
│   └── common.py           # Utilidades compartidas
├── logs/                   # Logs de ejecucion
└── venv/                   # Ambiente Python (generado por install.sh)
```

## Instalacion

### 1. Configurar .env

```bash
cp .env.example .env
nano .env
```

Variables requeridas:
```bash
# Rutas (ajustar al servidor)
AUTOMATION_DIR=/ruta/a/automation
SCRIPTS_DIR=/ruta/a/automation/scripts
LOGS_DIR=/ruta/a/automation/logs
CONFIG_DIR=/ruta/a/automation/config
PYTHON_VENV=/ruta/a/automation/venv
PYTHON_BASE=/usr/bin/python3

# Usuario del sistema
SERVICE_USER=usuario
SERVICE_GROUP=grupo

# Base de datos
DB_HOST=localhost
DB_NAME=base_datos
DB_USER=usuario
DB_PASSWORD=password
DB_PORT=5432

# Telegram
TELEGRAM_TOKEN=token_del_bot
TELEGRAM_CHAT_ID=id_del_chat
```

### 2. Ejecutar instalador

```bash
chmod +x install.sh
./install.sh
```

El instalador:
- Crea venv con dependencias
- Genera archivos systemd con rutas del .env
- Opcionalmente instala servicios en systemd

### 3. Verificar instalacion

```bash
./diagnose.sh
```

## Uso

### Control de servicios

```bash
./control.sh start      # Iniciar scheduler y bot
./control.sh stop       # Detener todo
./control.sh restart    # Reiniciar
./control.sh status     # Ver estado
./control.sh logs       # Ver logs en tiempo real
./control.sh test       # Testear componentes
```

### Ejecutar script manualmente

```bash
./control.sh run Script_INSUMOS_Linux.py
```

### Con systemd (produccion)

```bash
# Instalar servicios
sudo cp systemd/*.service /etc/systemd/system/
sudo cp systemd/*.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gestion-scheduler gestion-telegram-bot

# Controlar
sudo systemctl start gestion-scheduler
sudo systemctl start gestion-telegram-bot
sudo journalctl -u gestion-scheduler -f
```

## Componentes

### scheduler.py
Ejecuta los scripts de indexacion segun horarios:
- POST e INSUMOS: cada 6 horas
- TRANSVERSAL y OPERACION: cada 72 horas (Lunes 02:00)

### telegram_bot.py
Bot para monitoreo y control via Telegram:
- `/status` - Estado del sistema
- `/scripts` - Scripts en ejecucion
- `/logs` - Ver logs
- `/iniciar <script>` - Ejecutar script

### db_cleaner.py
Limpieza automatica de registros antiguos (>4 meses).

## Archivos de configuracion

### .env
Configuracion principal. Contiene:
- Rutas del sistema
- Credenciales de BD
- Token de Telegram
- Configuracion de logging

### config/config.example.json
Horarios de ejecucion de scripts (sin credenciales).

### config/roles.json
Roles y permisos de usuarios de Telegram.

## Logs

Los logs se guardan en `logs/`:
- `scheduler.log` - Ejecucion de scripts
- `telegram_bot.log` - Actividad del bot

Con systemd, tambien disponibles via journalctl.

## Troubleshooting

### El venv no tiene dependencias
```bash
./install.sh  # Regenera venv
```

### Los scripts no se ejecutan
```bash
./diagnose.sh           # Ver errores
./control.sh test       # Testear componentes
./control.sh logs       # Ver logs
```

### Error de conexion a BD
Verificar en .env: DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT

### Bot no responde
Verificar TELEGRAM_TOKEN y TELEGRAM_CHAT_ID en .env
