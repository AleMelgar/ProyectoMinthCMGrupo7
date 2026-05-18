from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import KPIRecord, EmployeeGoal, EvaluationForm, FormAssignment
from app.models.schemas import KPICreate, KPIResponse

router = APIRouter()


@router.post("/kpis/", response_model=KPIResponse)
def create_kpi(data: KPICreate, db: Session = Depends(get_db)):
    porcentaje = (data.valor_actual / data.valor_meta * 100) if data.valor_meta != 0 else 0.0
    kpi = KPIRecord(**data.model_dump(), porcentaje=porcentaje)
    db.add(kpi)
    db.commit()
    db.refresh(kpi)
    return kpi


@router.get("/kpis/employee/{employee_id}", response_model=list[KPIResponse])
def get_employee_kpis(employee_id: str, form_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(KPIRecord).filter(KPIRecord.employee_id == employee_id)
    if form_id:
        query = query.filter(KPIRecord.form_id == form_id)
    return query.all()


@router.post("/kpis/calculate")
def calculate_kpis(form_id: int, db: Session = Depends(get_db)):
    """Calcula KPIs automáticamente para todos los empleados asignados a un formulario.

    Por cada empleado asignado, calcula un KPI basado en el progreso
    ponderado de sus objetivos OKR del mismo período.
    """
    form = db.query(EvaluationForm).filter(EvaluationForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Formulario no encontrado")

    assignments = db.query(FormAssignment).filter(FormAssignment.form_id == form_id).all()
    if not assignments:
        raise HTTPException(status_code=400, detail="No hay empleados asignados a este formulario")

    created_kpis = []
    for assignment in assignments:
        goals = db.query(EmployeeGoal).filter(
            EmployeeGoal.employee_id == assignment.employee_id,
            EmployeeGoal.period_id == form.period_id,
        ).all()

        if not goals:
            continue

        total_peso = sum(g.peso for g in goals)
        if total_peso == 0:
            progreso_ponderado = 0.0
        else:
            progreso_ponderado = sum(g.progreso * g.peso for g in goals) / total_peso

        existing = db.query(KPIRecord).filter(
            KPIRecord.employee_id == assignment.employee_id,
            KPIRecord.form_id == form_id,
            KPIRecord.kpi_nombre == "Progreso OKR",
        ).first()

        if existing:
            existing.valor_actual = progreso_ponderado
            existing.valor_meta = 100.0
            existing.porcentaje = progreso_ponderado
            existing.calculado_en = datetime.utcnow()
            created_kpis.append(existing)
        else:
            kpi = KPIRecord(
                employee_id=assignment.employee_id,
                form_id=form_id,
                kpi_nombre="Progreso OKR",
                valor_actual=progreso_ponderado,
                valor_meta=100.0,
                porcentaje=progreso_ponderado,
            )
            db.add(kpi)
            created_kpis.append(kpi)

    db.commit()
    for k in created_kpis:
        db.refresh(k)

    return {
        "form_id": form_id,
        "kpis_calculados": len(created_kpis),
        "resultados": [
            {
                "employee_id": k.employee_id,
                "kpi_nombre": k.kpi_nombre,
                "valor_actual": k.valor_actual,
                "valor_meta": k.valor_meta,
                "porcentaje": round(k.porcentaje, 2),
            }
            for k in created_kpis
        ],
    }
