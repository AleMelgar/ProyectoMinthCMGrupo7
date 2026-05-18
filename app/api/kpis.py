from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import KPIRecord
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
def get_employee_kpis(employee_id: str, db: Session = Depends(get_db)):
    return db.query(KPIRecord).filter(KPIRecord.employee_id == employee_id).all()
