# PerformTrack

Modulo de evaluacion de desempeno para [MintHCM](https://minthcm.org/).

**Materia:** Aplicaciones de Codigo Abierto — Grupo 7, UCA Ciclo 09

## Que es PerformTrack?

MintHCM es un sistema de gestion de recursos humanos de codigo abierto (GPL). PerformTrack agrega funcionalidad que no tiene nativamente:

- Formularios de evaluacion configurables por periodo
- Asignacion de objetivos OKR por empleado
- Calculo automatico de KPIs
- Generacion de reportes exportables en PDF y Excel

El modulo se conecta a MintHCM mediante su API REST para leer datos de empleados, departamentos y cargos.

## Arquitectura

```
┌──────────────┐     API REST      ┌──────────────┐
│   MintHCM    │◄──────────────────│ PerformTrack │
│  (Docker)    │  OAuth2 + JSON    │  (FastAPI)   │
│  :80         │                   │  :8000       │
└──────────────┘                   └──────┬───────┘
                                          │
                                   ┌──────┴───────┐
                                   │   SQLite DB  │
                                   └──────────────┘
```

## Stack tecnologico

| Capa | Tecnologia |
|---|---|
| Software base | MintHCM (PHP/GPL) |
| Backend modulo | Python 3.12 + FastAPI |
| Base de datos | SQLite (dev) |
| ORM | SQLAlchemy |
| Reportes PDF | ReportLab |
| Reportes Excel | openpyxl |
| Frontend | HTML + Bootstrap 5 + vanilla JS |
| CI/CD | GitHub Actions |
| Contenedores | Docker (MintHCM) |

## Requisitos previos

- Python 3.12+
- MintHCM corriendo en Docker (`http://localhost`)
- Git

## Instalacion

```bash
# 1. Clonar el repositorio
git clone https://github.com/AleMelgar/ProyectoMinthCMGrupo7.git
cd ProyectoMinthCMGrupo7

# 2. Crear entorno virtual e instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env si las credenciales de MintHCM son diferentes

# 4. Ejecutar el servidor
uvicorn app.main:app --port 8000
```

Abrir `http://localhost:8000` para acceder al frontend.

La documentacion de la API (Swagger) esta en `http://localhost:8000/docs`.

## Configuracion

Variables de entorno en `.env`:

| Variable | Descripcion | Default |
|---|---|---|
| `MINTHCM_URL` | URL base de MintHCM | `http://localhost` |
| `MINTHCM_CLIENT_ID` | OAuth2 client ID | `mobile` |
| `MINTHCM_CLIENT_SECRET` | OAuth2 client secret | (ver .env.example) |
| `MINTHCM_USERNAME` | Usuario de MintHCM | `admin` |
| `MINTHCM_PASSWORD` | Contrasena de MintHCM | `minthcm` |
| `DATABASE_URL` | URL de la base de datos | `sqlite:///./performtrack.db` |

## Ejecutar tests

```bash
source venv/bin/activate
pytest tests/ -v
```

12 tests unitarios que cubren: periodos, formularios, asignacion de empleados, OKRs, calculo de KPIs, y generacion de reportes PDF/Excel.

## Estructura del proyecto

```
ProyectoMinthCMGrupo7/
├── app/
│   ├── main.py                 # Entry point FastAPI
│   ├── api/
│   │   ├── evaluations.py      # CRUD periodos + formularios + asignacion
│   │   ├── goals.py            # OKRs por empleado
│   │   ├── kpis.py             # KPIs + calculo automatico
│   │   ├── results.py          # Resultados de evaluacion
│   │   ├── reports.py          # Descarga PDF / Excel
│   │   └── minthcm_proxy.py    # Proxy a empleados de MintHCM
│   ├── models/
│   │   └── schemas.py          # Validacion Pydantic
│   ├── services/
│   │   ├── minthcm.py          # Cliente OAuth2 de MintHCM
│   │   └── report_gen.py       # Generacion PDF y Excel
│   ├── db/
│   │   ├── database.py         # Conexion SQLAlchemy
│   │   └── models.py           # 7 tablas del modulo
│   └── static/
│       └── index.html          # Frontend (Bootstrap 5)
├── tests/                      # 12 tests con pytest
├── docs/
│   └── fase2-diseno.md         # Diseno del modelo de datos
├── .github/workflows/
│   └── ci.yml                  # GitHub Actions CI/CD
├── requirements.txt
├── .env.example
└── README.md
```

## Endpoints principales

### Periodos
- `POST /periods/` — Crear periodo
- `GET /periods/` — Listar periodos
- `PATCH /periods/{id}/activate` — Activar periodo
- `PATCH /periods/{id}/close` — Cerrar periodo

### Formularios
- `POST /evaluations/` — Crear formulario con secciones
- `GET /evaluations/` — Listar formularios
- `PUT /evaluations/{id}/assign` — Asignar empleados

### OKRs
- `POST /goals/` — Crear objetivo OKR
- `GET /goals/employee/{id}` — Ver objetivos de un empleado
- `GET /goals/employee/{id}/summary` — Resumen ponderado
- `PATCH /goals/{id}/progress` — Actualizar progreso

### KPIs
- `POST /kpis/calculate?form_id=` — Calcular KPIs automaticamente
- `GET /kpis/employee/{id}` — Ver KPIs de un empleado

### Reportes
- `GET /reports/{form_id}/pdf` — Descargar PDF
- `GET /reports/{form_id}/excel` — Descargar Excel

### MintHCM
- `GET /minthcm/employees` — Lista de empleados desde MintHCM

## Flujo de uso

1. Crear un periodo de evaluacion (ej: "Q2 2025")
2. Crear un formulario con secciones ponderadas (Competencias 30%, OKRs 50%, KPIs 20%)
3. Asignar empleados al formulario (IDs desde MintHCM)
4. Crear objetivos OKR para cada empleado
5. Actualizar progreso de los OKRs conforme avanzan
6. Calcular KPIs automaticamente
7. Descargar reporte en PDF o Excel

## CI/CD

GitHub Actions ejecuta `pytest` automaticamente en cada push o PR a `main` y `develop`.

## Licencia

Este proyecto es parte de un trabajo academico. MintHCM esta bajo licencia [AGPL v3](https://www.gnu.org/licenses/agpl-3.0.html).

## Equipo

Grupo 7 — Aplicaciones de Codigo Abierto, UCA Ciclo 09
