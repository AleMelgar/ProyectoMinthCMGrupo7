from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import EvaluationPeriod, EvaluationForm, FormSection, FormAssignment
from app.models.schemas import (
    PeriodCreate, PeriodResponse,
    FormCreate, FormResponse,
    AssignEmployeesRequest, AssignmentResponse,
)

router = APIRouter()


# --- Períodos ---

@router.post("/periods/", response_model=PeriodResponse)
def create_period(data: PeriodCreate, db: Session = Depends(get_db)):
    period = EvaluationPeriod(**data.model_dump())
    db.add(period)
    db.commit()
    db.refresh(period)
    return period


@router.get("/periods/", response_model=list[PeriodResponse])
def list_periods(db: Session = Depends(get_db)):
    return db.query(EvaluationPeriod).all()


@router.get("/periods/{period_id}", response_model=PeriodResponse)
def get_period(period_id: int, db: Session = Depends(get_db)):
    period = db.query(EvaluationPeriod).filter(EvaluationPeriod.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Período no encontrado")
    return period


@router.patch("/periods/{period_id}/activate", response_model=PeriodResponse)
def activate_period(period_id: int, db: Session = Depends(get_db)):
    period = db.query(EvaluationPeriod).filter(EvaluationPeriod.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Período no encontrado")
    period.estado = "activo"
    db.commit()
    db.refresh(period)
    return period


@router.patch("/periods/{period_id}/close", response_model=PeriodResponse)
def close_period(period_id: int, db: Session = Depends(get_db)):
    period = db.query(EvaluationPeriod).filter(EvaluationPeriod.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Período no encontrado")
    period.estado = "cerrado"
    db.commit()
    db.refresh(period)
    return period


# --- Formularios ---

@router.post("/evaluations/", response_model=FormResponse)
def create_form(data: FormCreate, db: Session = Depends(get_db)):
    period = db.query(EvaluationPeriod).filter(EvaluationPeriod.id == data.period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Período no encontrado")

    sections_data = data.sections
    form_data = data.model_dump(exclude={"sections"})
    form = EvaluationForm(**form_data)
    db.add(form)
    db.flush()

    for s in sections_data:
        section = FormSection(form_id=form.id, **s.model_dump())
        db.add(section)

    db.commit()
    db.refresh(form)
    return form


@router.put("/evaluations/{form_id}/assign", response_model=list[AssignmentResponse])
def assign_employees(form_id: int, data: AssignEmployeesRequest, db: Session = Depends(get_db)):
    form = db.query(EvaluationForm).filter(EvaluationForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Formulario no encontrado")

    created = []
    for emp_id in data.employee_ids:
        exists = db.query(FormAssignment).filter(
            FormAssignment.form_id == form_id,
            FormAssignment.employee_id == emp_id,
        ).first()
        if not exists:
            assignment = FormAssignment(form_id=form_id, employee_id=emp_id)
            db.add(assignment)
            created.append(assignment)

    db.commit()
    for a in created:
        db.refresh(a)
    return created


@router.get("/evaluations/{form_id}/assignments", response_model=list[AssignmentResponse])
def get_assignments(form_id: int, db: Session = Depends(get_db)):
    return db.query(FormAssignment).filter(FormAssignment.form_id == form_id).all()


@router.get("/evaluations/{form_id}", response_model=FormResponse)
def get_form(form_id: int, db: Session = Depends(get_db)):
    form = db.query(EvaluationForm).filter(EvaluationForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Formulario no encontrado")
    return form


@router.get("/evaluations/", response_model=list[FormResponse])
def list_forms(db: Session = Depends(get_db)):
    return db.query(EvaluationForm).all()
