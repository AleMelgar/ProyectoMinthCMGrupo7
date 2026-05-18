from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
def get_employee_goals(employee_id: str, db: Session = Depends(get_db)):
    return db.query(EmployeeGoal).filter(EmployeeGoal.employee_id == employee_id).all()


@router.patch("/goals/{goal_id}/progress", response_model=GoalResponse)
def update_progress(goal_id: int, data: GoalProgressUpdate, db: Session = Depends(get_db)):
    goal = db.query(EmployeeGoal).filter(EmployeeGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Objetivo no encontrado")
    goal.progreso = data.progreso
    db.commit()
    db.refresh(goal)
    return goal
