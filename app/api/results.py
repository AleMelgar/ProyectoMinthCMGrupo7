from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import EvaluationResult
from app.models.schemas import ResultCreate, ResultResponse

router = APIRouter()


@router.post("/results/", response_model=ResultResponse)
def create_result(data: ResultCreate, db: Session = Depends(get_db)):
    result = EvaluationResult(**data.model_dump())
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@router.get("/results/employee/{employee_id}", response_model=list[ResultResponse])
def get_employee_results(employee_id: str, db: Session = Depends(get_db)):
    return db.query(EvaluationResult).filter(EvaluationResult.employee_id == employee_id).all()
