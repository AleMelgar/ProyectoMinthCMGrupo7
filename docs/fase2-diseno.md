# Fase 2 — Diseño del Módulo PerformTrack

## 2.1 — Modelo de Datos

### Contexto: módulos que MintHCM ya tiene

Antes de crear tablas propias, se exploró la API de MintHCM y se encontró que los siguientes módulos ya existen y pueden consumirse directamente:

| Módulo MintHCM | Uso en PerformTrack |
|---|---|
| `Employees` | Fuente de empleados (no duplicar) |
| `Positions` | Cargos de los empleados |
| `Goals` | Se reutiliza como base para OKRs |
| `Appraisals` | Referencia para evaluaciones existentes |
| `Competencies` / `CompetencyRatings` | Competencias evaluables |

PerformTrack **no replica** estos datos; los consulta en tiempo real vía API.

---

### Entidades propias de PerformTrack

PerformTrack mantiene su propia base de datos (SQLite en desarrollo, PostgreSQL en producción) con las entidades que MintHCM no cubre:

#### `EvaluationPeriod` — Período de evaluación
```
id            INTEGER  PK autoincrement
nombre        TEXT     "Evaluación Q2 2025"
periodo       TEXT     "Q1" | "Q2" | "Q3" | "Q4" | "Anual"
fecha_inicio  DATE
fecha_fin     DATE
estado        TEXT     "borrador" | "activo" | "cerrado"
creado_en     DATETIME
```

#### `EvaluationForm` — Formulario de evaluación
```
id               INTEGER  PK autoincrement
period_id        INTEGER  FK → EvaluationPeriod
nombre           TEXT
descripcion      TEXT
escala_min       INTEGER  (ej: 1)
escala_max       INTEGER  (ej: 5)
creado_en        DATETIME
```

#### `FormSection` — Secciones del formulario
```
id          INTEGER  PK autoincrement
form_id     INTEGER  FK → EvaluationForm
nombre      TEXT     "Competencias" | "Resultados" | "OKRs"
peso        FLOAT    porcentaje (suma de secciones = 100%)
orden       INTEGER
```

#### `EmployeeGoal` — Objetivo OKR asignado a un empleado
```
id              INTEGER  PK autoincrement
employee_id     TEXT     ID del empleado en MintHCM
period_id       INTEGER  FK → EvaluationPeriod
descripcion     TEXT
objetivo_okr    TEXT     enunciado del objetivo
peso            FLOAT    % de peso en la evaluación
progreso        FLOAT    0.0 – 100.0
fecha_limite    DATE
creado_en       DATETIME
```

#### `KPIRecord` — KPI calculado por empleado y formulario
```
id              INTEGER  PK autoincrement
employee_id     TEXT     ID del empleado en MintHCM
form_id         INTEGER  FK → EvaluationForm
kpi_nombre      TEXT
valor_actual    FLOAT
valor_meta      FLOAT
porcentaje      FLOAT    (valor_actual / valor_meta) * 100
calculado_en    DATETIME
```

#### `EvaluationResult` — Resultado final de evaluación
```
id                INTEGER  PK autoincrement
employee_id       TEXT     ID del empleado en MintHCM
form_id           INTEGER  FK → EvaluationForm
puntaje_total     FLOAT    calculado automáticamente
comentarios       TEXT
evaluador_id      TEXT     ID del evaluador en MintHCM
fecha_evaluacion  DATE
estado            TEXT     "pendiente" | "completado" | "aprobado"
creado_en         DATETIME
```

---

### Diagrama de relaciones

```
EvaluationPeriod
    │
    ├──< EvaluationForm >──< FormSection
    │        │
    │        ├──< KPIRecord (employee_id → MintHCM)
    │        └──< EvaluationResult (employee_id → MintHCM)
    │
    └──< EmployeeGoal (employee_id → MintHCM)
```

---

## 2.2 — Diseño de los Formularios de Evaluación

Cada `EvaluationForm` contiene secciones configurables. Ejemplo de un formulario tipo:

```
Evaluación Q2 2025
├── Sección: Competencias          (peso: 30%)
│   ├── Comunicación               (escala 1-5)
│   ├── Trabajo en equipo          (escala 1-5)
│   └── Orientación a resultados   (escala 1-5)
│
├── Sección: OKRs / Objetivos      (peso: 50%)
│   ├── Objetivo 1 (de EmployeeGoal)
│   ├── Objetivo 2
│   └── Objetivo 3
│
└── Sección: KPIs                  (peso: 20%)
    ├── KPI: Ventas vs Meta
    └── KPI: Satisfacción cliente
```

**Cálculo del puntaje total:**
```
puntaje_total = Σ (promedio_seccion * peso_seccion)
```

---

## 2.3 — Flujo de Trabajo

```
[Admin]
  │
  ├─ 1. Crea EvaluationPeriod (ej: "Q2 2025")
  │
  ├─ 2. Crea EvaluationForm con sus secciones y pesos
  │
  ├─ 3. Asigna EmployeeGoals a empleados (lee empleados de MintHCM)
  │
  └─ 4. Activa el período → estado = "activo"

[Empleado / Jefe]
  │
  ├─ 5. Llena EvaluationResult (autoevaluación o evaluación por jefe)
  │
  └─ 6. Confirma evaluación → estado = "completado"

[Sistema]
  │
  ├─ 7. Calcula KPIRecords automáticamente
  │
  └─ 8. Genera reporte PDF / Excel con resultados

[Admin]
  └─ 9. Cierra el período → estado = "cerrado"
```

---

## Endpoints REST que expone PerformTrack

### Períodos
- `POST   /periods/`              — Crear período
- `GET    /periods/`              — Listar períodos
- `GET    /periods/{id}`          — Ver período
- `PATCH  /periods/{id}/activate` — Activar período

### Formularios
- `POST   /evaluations/`          — Crear formulario
- `GET    /evaluations/{id}`      — Ver formulario
- `PUT    /evaluations/{id}`      — Editar formulario

### OKRs / Objetivos
- `POST   /goals/`                         — Crear objetivo para empleado
- `GET    /goals/employee/{employee_id}`   — Ver objetivos de un empleado
- `PATCH  /goals/{id}/progress`            — Actualizar progreso

### KPIs
- `POST   /kpis/calculate`                 — Calcular KPIs (trigger manual)
- `GET    /kpis/employee/{employee_id}`    — Ver KPIs de un empleado

### Resultados
- `POST   /results/`                       — Registrar resultado de evaluación
- `GET    /results/employee/{employee_id}` — Ver resultados de un empleado

### Reportes
- `GET    /reports/{form_id}/pdf`          — Descargar PDF
- `GET    /reports/{form_id}/excel`        — Descargar Excel

### MintHCM (proxy de datos)
- `GET    /minthcm/employees`              — Lista de empleados desde MintHCM
- `GET    /minthcm/employees/{id}`         — Detalle de empleado

---

## Notas de integración con la API de MintHCM

La API correcta a usar es la **moderna (OAuth2 + Slim)**, no la legacy `SugarRestServlet`.

```
Base URL:      http://localhost/api
Auth endpoint: POST /api/access_token
Grant type:    mobile
Client ID:     mobile
```

Módulos HR que PerformTrack consulta vía API:
- `POST /api/Employees` — lista de empleados
- `POST /api/Employees/Get/{id}` — detalle de un empleado
- `POST /api/Positions` — cargos
