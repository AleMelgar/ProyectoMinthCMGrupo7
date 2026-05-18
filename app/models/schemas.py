from datetime import date, datetime
from pydantic import BaseModel


# --- EvaluationPeriod ---

class PeriodCreate(BaseModel):
    nombre: str
    periodo: str  # Q1, Q2, Q3, Q4, Anual
    fecha_inicio: date
    fecha_fin: date

class PeriodResponse(BaseModel):
    id: int
    nombre: str
    periodo: str
    fecha_inicio: date
    fecha_fin: date
    estado: str
    creado_en: datetime

    model_config = {"from_attributes": True}


# --- EvaluationForm ---

class SectionCreate(BaseModel):
    nombre: str
    peso: float
    orden: int = 0

class FormCreate(BaseModel):
    period_id: int
    nombre: str
    descripcion: str | None = None
    escala_min: int = 1
    escala_max: int = 5
    sections: list[SectionCreate] = []

class SectionResponse(BaseModel):
    id: int
    nombre: str
    peso: float
    orden: int

    model_config = {"from_attributes": True}

class FormResponse(BaseModel):
    id: int
    period_id: int
    nombre: str
    descripcion: str | None
    escala_min: int
    escala_max: int
    creado_en: datetime
    sections: list[SectionResponse] = []

    model_config = {"from_attributes": True}


# --- FormAssignment ---

class AssignEmployeesRequest(BaseModel):
    employee_ids: list[str]

class AssignmentResponse(BaseModel):
    id: int
    form_id: int
    employee_id: str
    asignado_en: datetime

    model_config = {"from_attributes": True}


# --- EmployeeGoal ---

class GoalCreate(BaseModel):
    employee_id: str
    period_id: int
    descripcion: str
    objetivo_okr: str
    peso: float
    fecha_limite: date

class GoalProgressUpdate(BaseModel):
    progreso: float  # 0-100

class GoalResponse(BaseModel):
    id: int
    employee_id: str
    period_id: int
    descripcion: str
    objetivo_okr: str
    peso: float
    progreso: float
    fecha_limite: date
    creado_en: datetime

    model_config = {"from_attributes": True}


# --- KPIRecord ---

class KPICreate(BaseModel):
    employee_id: str
    form_id: int
    kpi_nombre: str
    valor_actual: float
    valor_meta: float

class KPIResponse(BaseModel):
    id: int
    employee_id: str
    form_id: int
    kpi_nombre: str
    valor_actual: float
    valor_meta: float
    porcentaje: float
    calculado_en: datetime

    model_config = {"from_attributes": True}


# --- EvaluationResult ---

class ResultCreate(BaseModel):
    employee_id: str
    form_id: int
    puntaje_total: float
    comentarios: str | None = None
    evaluador_id: str | None = None
    fecha_evaluacion: date

class ResultResponse(BaseModel):
    id: int
    employee_id: str
    form_id: int
    puntaje_total: float
    comentarios: str | None
    evaluador_id: str | None
    fecha_evaluacion: date
    estado: str
    creado_en: datetime

    model_config = {"from_attributes": True}
