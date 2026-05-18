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


def _seed():
    client.post("/periods/", json={
        "nombre": "Q2", "periodo": "Q2",
        "fecha_inicio": "2025-04-01", "fecha_fin": "2025-06-30",
    })


# --- Test 6: Crear objetivo OKR ---

def test_create_goal():
    _seed()
    resp = client.post("/goals/", json={
        "employee_id": "emp1",
        "period_id": 1,
        "descripcion": "Mejorar ventas",
        "objetivo_okr": "Aumentar ventas 20%",
        "peso": 60.0,
        "fecha_limite": "2025-06-30",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["objetivo_okr"] == "Aumentar ventas 20%"
    assert data["progreso"] == 0.0


# --- Test 7: Actualizar progreso ---

def test_update_progress():
    _seed()
    client.post("/goals/", json={
        "employee_id": "emp1", "period_id": 1,
        "descripcion": "Test", "objetivo_okr": "OKR test",
        "peso": 100.0, "fecha_limite": "2025-06-30",
    })

    resp = client.patch("/goals/1/progress", json={"progreso": 75.5})
    assert resp.status_code == 200
    assert resp.json()["progreso"] == 75.5


# --- Test 8: Resumen OKR ponderado ---

def test_goal_summary():
    _seed()
    client.post("/goals/", json={
        "employee_id": "emp1", "period_id": 1,
        "descripcion": "A", "objetivo_okr": "OKR A",
        "peso": 60.0, "fecha_limite": "2025-06-30",
    })
    client.post("/goals/", json={
        "employee_id": "emp1", "period_id": 1,
        "descripcion": "B", "objetivo_okr": "OKR B",
        "peso": 40.0, "fecha_limite": "2025-06-30",
    })
    client.patch("/goals/1/progress", json={"progreso": 80.0})
    client.patch("/goals/2/progress", json={"progreso": 50.0})

    resp = client.get("/goals/employee/emp1/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_goals"] == 2
    # (80*60 + 50*40) / 100 = 68.0
    assert data["progreso_ponderado"] == 68.0
