from fastapi import APIRouter, HTTPException
from app.services.minthcm import mint_client

router = APIRouter()


@router.get("/minthcm/employees")
async def list_employees(page: int = 1, items: int = 20):
    try:
        data = await mint_client.get_employees(page=page, items=items)
        employees = []
        for record in data.get("results", []):
            attrs = record.get("attributes", {})
            employees.append({
                "id": attrs.get("id"),
                "first_name": attrs.get("first_name", ""),
                "last_name": attrs.get("last_name", ""),
                "full_name": attrs.get("full_name", ""),
                "title": attrs.get("title", ""),
                "department": attrs.get("department", ""),
                "position_name": attrs.get("position_name", ""),
                "employee_status": attrs.get("employee_status", ""),
            })
        return {"total": data.get("total", 0), "employees": employees}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al conectar con MintHCM: {e}")


@router.get("/minthcm/employees/{employee_id}")
async def get_employee(employee_id: str):
    try:
        data = await mint_client.get_employee(employee_id)
        attrs = data.get("attributes", {})
        return {
            "id": attrs.get("id"),
            "first_name": attrs.get("first_name", ""),
            "last_name": attrs.get("last_name", ""),
            "full_name": attrs.get("full_name", ""),
            "title": attrs.get("title", ""),
            "department": attrs.get("department", ""),
            "position_name": attrs.get("position_name", ""),
            "email": attrs.get("email1", ""),
            "phone_work": attrs.get("phone_work", ""),
            "employee_status": attrs.get("employee_status", ""),
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al conectar con MintHCM: {e}")
