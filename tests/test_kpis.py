import pytest
from fastapi.testclient import TestClient
from app.db.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def _seed_full():
    """Crea período, formulario, asigna empleado y crea goals con progreso."""
    client.post("/periods/", json={
        "nombre": "Q2", "periodo": "Q2",
        "fecha_inicio": "2025-04-01", "fecha_fin": "2025-06-30",
    })
    client.post("/evaluations/", json={
        "period_id": 1, "nombre": "Form KPI Test",
        "sections": [{"nombre": "OKRs", "peso": 100.0, "orden": 1}],
    })
    client.put("/evaluations/1/assign", json={"employee_ids": ["emp1"]})
    client.post("/goals/", json={
        "employee_id": "emp1", "period_id": 1,
        "descripcion": "A", "objetivo_okr": "OKR A",
        "peso": 70.0, "fecha_limite": "2025-06-30",
    })
    client.post("/goals/", json={
        "employee_id": "emp1", "period_id": 1,
        "descripcion": "B", "objetivo_okr": "OKR B",
        "peso": 30.0, "fecha_limite": "2025-06-30",
    })
    client.patch("/goals/1/progress", json={"progreso": 90.0})
    client.patch("/goals/2/progress", json={"progreso": 60.0})


# --- Test 9: Cálculo automático de KPIs ---

def test_calculate_kpis():
    _seed_full()
    resp = client.post("/kpis/calculate?form_id=1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["kpis_calculados"] == 1
    # (90*70 + 60*30) / 100 = 81.0
    assert data["resultados"][0]["porcentaje"] == 81.0


# --- Test 10: KPI manual con porcentaje calculado ---

def test_create_kpi_manual():
    _seed_full()
    resp = client.post("/kpis/", json={
        "employee_id": "emp1",
        "form_id": 1,
        "kpi_nombre": "Satisfacción cliente",
        "valor_actual": 4.2,
        "valor_meta": 5.0,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["porcentaje"] == pytest.approx(84.0, abs=0.1)


# --- Test 11: Reporte PDF se genera correctamente ---

def test_pdf_report():
    _seed_full()
    client.post("/kpis/calculate?form_id=1")
    resp = client.get("/reports/1/pdf")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert len(resp.content) > 500


# --- Test 12: Reporte Excel se genera correctamente ---

def test_excel_report():
    _seed_full()
    client.post("/kpis/calculate?form_id=1")
    resp = client.get("/reports/1/excel")
    assert resp.status_code == 200
    assert "spreadsheetml" in resp.headers["content-type"]
    assert len(resp.content) > 500
