# Gestion del Dato - Geospatial Data Management Platform

**Full-stack platform for managing the complete lifecycle of cadastral and geospatial data**, from pre-operation data collection through post-operation quality control. Features interactive mapping, automated file indexing, Telegram bot monitoring, and multi-level operational workflows.

> Developed for the Instituto Geografico Agustin Codazzi (IGAC), Colombia's national geographic and cadastral authority.

---

## Key Features

- **Pre-Operation Management** - Organize raw geographic data across 13 categories (cartography, orthophoto, satellite imagery, LiDAR, etc.)
- **Post-Operation QC** - Disposition management, approval workflows, and quality evaluation
- **Interactive Geoportal** - Leaflet-based mapping with municipality boundaries and territory visualization
- **Automated File Indexing** - Scheduled scripts that recursively scan network shares and index files with ownership detection
- **Telegram Bot Control** - Real-time monitoring, manual script triggers, and system health via Telegram commands
- **Municipality Dashboard** - Track operations across 1,100+ Colombian municipalities with KPI indicators
- **Professional Tracking** - Assign and monitor surveyor/professional territory assignments
- **Audit System** - Complete action logging with user tracking
- **Notification Center** - Real-time notifications for workflow events
- **Report Generation** - Excel/PDF export of operational data and statistics

---

## Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **Django 5.0 + DRF** | REST API framework |
| **PostgreSQL 15** | Primary database |
| **Pandas + OpenPyXL** | Data processing & Excel handling |
| **drf-yasg** | Auto-generated Swagger/OpenAPI docs |
| **SimpleJWT** | Token authentication |

### Frontend
| Technology | Purpose |
|---|---|
| **Vue.js 3** | UI framework |
| **TypeScript** | Type safety |
| **Vite 5** | Build tooling |
| **TailwindCSS 3** | Styling |
| **Pinia** | State management |
| **Leaflet** | Interactive mapping |
| **Chart.js** | Data visualization |
| **PDF.js** | Document viewer |

### Automation
| Technology | Purpose |
|---|---|
| **Python Scheduler** | Cron-like job scheduling (6h/72h cycles) |
| **Telegram Bot API** | Remote monitoring & control |
| **getcifsacl** | Windows ACL ownership detection on SMB |

### Infrastructure
| Technology | Purpose |
|---|---|
| **Docker Compose** | Container orchestration |
| **Nginx** | Reverse proxy + SSL |
| **Let's Encrypt + DuckDNS** | SSL certificates + Dynamic DNS |
| **Systemd** | Service management for automation |

---

## Architecture

```
                     +------------------+
                     |     Nginx        |
                     | (SSL + Proxy)    |
                     +--------+---------+
                              |
               +--------------+--------------+
               |                             |
      +--------v--------+          +--------v--------+
      |  Vue.js Frontend |          |  Django Backend  |
      |  (Static Build)  |          |   REST API       |
      +------------------+          +--------+---------+
                                             |
                         +-------------------+-------------------+
                         |                                       |
                   +-----v------+                         +------v------+
                   | PostgreSQL  |                         |   NetApp    |
                   |    15       |                         |  SMB Share  |
                   +-------------+                         +------+------+
                                                                  |
                                                    +-------------v-----------+
                                                    |    Automation Module     |
                                                    |  +-------------------+  |
                                                    |  | Scheduler (6h)    |  |
                                                    |  | Telegram Bot      |  |
                                                    |  | File Indexers     |  |
                                                    |  | DB Cleaner        |  |
                                                    |  +-------------------+  |
                                                    +-------------------------+
```

### Django Apps

| App | Description |
|---|---|
| `preoperacion` | Pre-operation data management (34 models) - municipalities, categories, file indexing |
| `postoperacion` | Post-operation QC and disposition workflows (9 models) |
| `app` | Utility module - script execution tracking, database backups |

### Data Categories (Pre-Operation)

| # | Category |
|---|---|
| 01 | Cartographic basics |
| 02 | Orthophotos |
| 03 | Satellite imagery |
| 04 | LiDAR data |
| 05 | Vertical photos |
| 06 | Digital models |
| 07 | Topographic data |
| 08-13 | Additional specialized categories |

### Automation Scripts

| Script | Schedule | Description |
|---|---|---|
| `Script_INSUMOS_Linux.py` | Every 6 hours | Index input/supply data across 13 categories |
| `Script_POST_Linux.py` | Every 6 hours | Index post-operation data |
| `Script_TRANSVERSAL_Linux.py` | Every 72 hours | Cross-cutting territorial data |
| `Script_OPERACION_Linux.py` | Every 72 hours | Operations workflow indexing |
| `Script_INDEXAR_VECTORIAL.py` | On demand | Vectorial/spatial data indexing |
| `db_cleaner.py` | On demand | Cleanup records older than 4 months |

### Telegram Bot Commands

| Command | Description |
|---|---|
| `/status` | System health overview |
| `/scripts` | Active script monitoring (CPU/RAM/duration) |
| `/proximos` | Upcoming scheduled tasks with countdown |
| `/iniciar` | Manually trigger indexing scripts |
| `/urgente [script] [municipio]` | Run script for specific municipality |
| `/detener [script]` | Stop running script |
| `/logs [script]` | Retrieve execution logs |
| `/docker` | Container status check |

---

## API Overview

| Endpoint Group | Description |
|---|---|
| `GET /api/municipios/` | List municipalities with filtering |
| `GET /api/insumos/` | Query input/supply records |
| `GET /api/detalle-insumo/` | Detailed record management |
| `GET /api/disposicion-post/` | Post-operation dispositions |
| `GET /api/profesionales/` | Professional assignments |
| `GET /api/auditoria/` | Audit trail queries |
| `GET /api/notificaciones/` | Notification management |
| `GET /api/categorias/` | Category catalog |
| `POST /api/file-explorer/` | File operations on network shares |

Swagger documentation available at `/api/docs/`.

---

## Setup & Deployment

### Prerequisites
- Docker & Docker Compose
- Network share mounted at `/mnt/repositorio` (SMB/CIFS)
- Telegram Bot Token (for automation module)

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Gisdeveloper95/gestion-dato.git
cd gestion-dato

# 2. Configure environment
cp .env.example .env
cp backend/.env.example backend/.env
cp automation/.env.example automation/.env
# Edit all .env files with your credentials

# 3. Launch services
docker-compose up -d

# 4. Run migrations
docker-compose exec backend python manage.py migrate

# 5. Create superuser
docker-compose exec backend python manage.py createsuperuser

# 6. (Optional) Setup automation
cd automation
./install.sh
```

The application will be available at `http://localhost` (Nginx).

### Environment Variables

Key configuration via `.env`:

| Variable | Description |
|---|---|
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Database credentials |
| `SECRET_KEY` | Django secret key |
| `RUTA_RED` | Network share mount path |
| `TELEGRAM_TOKEN` | Telegram Bot API token |
| `ALLOWED_HOSTS` | Comma-separated allowed hostnames |

---

## Frontend Pages

| Page | Description |
|---|---|
| **Dashboard** | Analytics overview with charts and KPIs |
| **Geoportal** | Interactive map with municipality boundaries (Leaflet) |
| **Municipios** | Municipality management and detail views |
| **Insumos** | Input data management with filtering |
| **Productos** | Product state tracking through lifecycle |
| **Indicadores** | KPI indicators and statistics |
| **Auditoria** | Audit trail viewer |
| **Profesionales** | Professional staff and territory assignments |
| **Reportes** | Report generation and export |

---

## License

This project was developed for internal use at IGAC. All rights reserved.

---

## Author

**Andres Felipe Osorio Bastidas**
GIS Developer & Full-Stack Engineer
[GitHub](https://github.com/Gisdeveloper95)
