from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.db.models import EmployeeGoal
from app.models.schemas import GoalCreate, GoalResponse, GoalProgressUpdate

router = APIRouter()


@router.post("/goals/", response_model=GoalResponse)
def create_goal(data: GoalCreate, db: Session = Depends(get_db)):
    goal = EmployeeGoal(**data.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.get("/goals/employee/{employee_id}", response_model=list[GoalResponse])
def get_employee_goals(employee_id: str, period_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(EmployeeGoal).filter(EmployeeGoal.employee_id == employee_id)
    if period_id:
        query = query.filter(EmployeeGoal.period_id == period_id)
    return query.all()


@router.get("/goals/period/{period_id}", response_model=list[GoalResponse])
def get_period_goals(period_id: int, db: Session = Depends(get_db)):
    return db.query(EmployeeGoal).filter(EmployeeGoal.period_id == period_id).all()


@router.patch("/goals/{goal_id}/progress", response_model=GoalResponse)
def update_progress(goal_id: int, data: GoalProgressUpdate, db: Session = Depends(get_db)):
    goal = db.query(EmployeeGoal).filter(EmployeeGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Objetivo no encontrado")
    goal.progreso = data.progreso
    db.commit()
    db.refresh(goal)
    return goal


@router.get("/goals/employee/{employee_id}/summary")
def get_employee_goal_summary(employee_id: str, period_id: int | None = None, db: Session = Depends(get_db)):
    """Resumen OKR de un empleado: total de objetivos, progreso promedio ponderado."""
    query = db.query(EmployeeGoal).filter(EmployeeGoal.employee_id == employee_id)
    if period_id:
        query = query.filter(EmployeeGoal.period_id == period_id)
    goals = query.all()

    if not goals:
        return {"employee_id": employee_id, "total_goals": 0, "progreso_ponderado": 0.0}

    total_peso = sum(g.peso for g in goals)
    if total_peso == 0:
        progreso_ponderado = 0.0
    else:
        progreso_ponderado = sum(g.progreso * g.peso for g in goals) / total_peso

    return {
        "employee_id": employee_id,
        "total_goals": len(goals),
        "progreso_ponderado": round(progreso_ponderado, 2),
        "goals": [
            {"id": g.id, "objetivo_okr": g.objetivo_okr, "peso": g.peso, "progreso": g.progreso}
            for g in goals
        ],
    }
