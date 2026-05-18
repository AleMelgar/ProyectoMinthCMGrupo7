import pytest
from fastapi.testclient import TestClient
from app.db.database import Base, engine, SessionLocal
from app.main import app


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def _create_period():
    return client.post("/periods/", json={
        "nombre": "Eval Q2 2025",
        "periodo": "Q2",
        "fecha_inicio": "2025-04-01",
        "fecha_fin": "2025-06-30",
    })


# --- Test 1: Crear período ---

def test_create_period():
    response = _create_period()
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Eval Q2 2025"
    assert data["estado"] == "borrador"
    assert data["id"] == 1


# --- Test 2: Activar y cerrar período ---

def test_period_lifecycle():
    _create_period()

    resp = client.patch("/periods/1/activate")
    assert resp.status_code == 200
    assert resp.json()["estado"] == "activo"

    resp = client.patch("/periods/1/close")
    assert resp.status_code == 200
    assert resp.json()["estado"] == "cerrado"


# --- Test 3: Crear formulario con secciones ---

def test_create_form_with_sections():
    _create_period()
    response = client.post("/evaluations/", json={
        "period_id": 1,
        "nombre": "Formulario General",
        "escala_min": 1,
        "escala_max": 5,
        "sections": [
            {"nombre": "Competencias", "peso": 30.0, "orden": 1},
            {"nombre": "OKRs", "peso": 50.0, "orden": 2},
            {"nombre": "KPIs", "peso": 20.0, "orden": 3},
        ],
    })
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Formulario General"
    assert len(data["sections"]) == 3
    pesos = [s["peso"] for s in data["sections"]]
    assert sum(pesos) == 100.0


# --- Test 4: Asignar empleados a formulario ---

def test_assign_employees():
    _create_period()
    client.post("/evaluations/", json={
        "period_id": 1, "nombre": "Form Test",
        "sections": [{"nombre": "Sec1", "peso": 100.0, "orden": 1}],
    })

    resp = client.put("/evaluations/1/assign", json={"employee_ids": ["emp1", "emp2"]})
    assert resp.status_code == 200
    assert len(resp.json()) == 2

    # No duplicar si se vuelve a asignar
    resp2 = client.put("/evaluations/1/assign", json={"employee_ids": ["emp1", "emp3"]})
    assert resp2.status_code == 200
    assert len(resp2.json()) == 1  # solo emp3 es nuevo

    assignments = client.get("/evaluations/1/assignments")
    assert len(assignments.json()) == 3


# --- Test 5: Formulario no encontrado devuelve 404 ---

def test_form_not_found():
    resp = client.get("/evaluations/999")
    assert resp.status_code == 404
