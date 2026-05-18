from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import EvaluationForm, FormAssignment, EmployeeGoal, KPIRecord, EvaluationResult
from app.services.report_gen import generate_pdf_report, generate_excel_report

router = APIRouter()


def _gather_report_data(form_id: int, db: Session) -> tuple[str, str, list[dict]]:
    """Recopila todos los datos necesarios para generar un reporte."""
    form = db.query(EvaluationForm).filter(EvaluationForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Formulario no encontrado")

    period = form.period
    assignments = db.query(FormAssignment).filter(FormAssignment.form_id == form_id).all()

    employees_data = []
    for assignment in assignments:
        emp_id = assignment.employee_id

        goals = db.query(EmployeeGoal).filter(
            EmployeeGoal.employee_id == emp_id,
            EmployeeGoal.period_id == period.id,
        ).all()

        kpis = db.query(KPIRecord).filter(
            KPIRecord.employee_id == emp_id,
            KPIRecord.form_id == form_id,
        ).all()

        result = db.query(EvaluationResult).filter(
            EvaluationResult.employee_id == emp_id,
            EvaluationResult.form_id == form_id,
        ).first()

        # Calcular puntaje si no existe resultado formal
        if result:
            puntaje = result.puntaje_total
            estado = result.estado
            comentarios = result.comentarios or ""
        else:
            total_peso = sum(g.peso for g in goals)
            puntaje = sum(g.progreso * g.peso for g in goals) / total_peso if total_peso else 0.0
            estado = "pendiente"
            comentarios = ""

        employees_data.append({
            "employee_id": emp_id,
            "employee_name": f"Empleado {emp_id}",
            "puntaje_total": puntaje,
            "estado": estado,
            "comentarios": comentarios,
            "goals": [
                {
                    "objetivo_okr": g.objetivo_okr,
                    "peso": g.peso,
                    "progreso": g.progreso,
                }
                for g in goals
            ],
            "kpis": [
                {
                    "kpi_nombre": k.kpi_nombre,
                    "valor_actual": k.valor_actual,
                    "valor_meta": k.valor_meta,
                    "porcentaje": k.porcentaje,
                }
                for k in kpis
            ],
        })

    return form.nombre, period.nombre, employees_data


@router.get("/reports/{form_id}/pdf")
def download_pdf_report(form_id: int, db: Session = Depends(get_db)):
    form_name, period_name, employees_data = _gather_report_data(form_id, db)
    buffer = generate_pdf_report(form_name, period_name, employees_data)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="reporte_{form_id}.pdf"'},
    )


@router.get("/reports/{form_id}/excel")
def download_excel_report(form_id: int, db: Session = Depends(get_db)):
    form_name, period_name, employees_data = _gather_report_data(form_id, db)
    buffer = generate_excel_report(form_name, period_name, employees_data)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="reporte_{form_id}.xlsx"'},
    )
