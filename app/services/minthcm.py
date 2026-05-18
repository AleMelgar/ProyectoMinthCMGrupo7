import os
import httpx


class MintHCMClient:
    """Cliente para la API REST moderna de MintHCM (OAuth2 + Slim)."""

    def __init__(self):
        self.base_url = os.getenv("MINTHCM_URL", "http://localhost")
        self.client_id = os.getenv("MINTHCM_CLIENT_ID", "mobile")
        self.client_secret = os.getenv("MINTHCM_CLIENT_SECRET", "")
        self.username = os.getenv("MINTHCM_USERNAME", "admin")
        self.password = os.getenv("MINTHCM_PASSWORD", "minthcm")
        self._token: str | None = None

    async def _get_token(self) -> str:
        """Obtiene un access token via OAuth2 mobile grant."""
        if self._token:
            return self._token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/access_token",
                json={
                    "grant_type": "mobile",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "username": self.username,
                    "password": self.password,
                },
            )
            response.raise_for_status()
            data = response.json()
            self._token = data["access_token"]
            return self._token

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """Hace una petición autenticada a la API de MintHCM."""
        token = await self._get_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method, f"{self.base_url}/api{path}", headers=headers, **kwargs
            )
            if response.status_code == 401:
                self._token = None
                token = await self._get_token()
                headers["Authorization"] = f"Bearer {token}"
                response = await client.request(
                    method, f"{self.base_url}/api{path}", headers=headers, **kwargs
                )
            response.raise_for_status()
            return response.json()

    async def get_employees(self, page: int = 1, items: int = 20) -> dict:
        """Lista empleados desde MintHCM."""
        return await self._request("POST", "/Employees", json={"page": page, "items": items})

    async def get_employee(self, employee_id: str) -> dict:
        """Obtiene detalle de un empleado."""
        return await self._request("POST", f"/Employees/Get/{employee_id}")

    async def get_positions(self, page: int = 1, items: int = 50) -> dict:
        """Lista cargos/posiciones."""
        return await self._request("POST", "/Positions", json={"page": page, "items": items})

    async def get_departments(self, page: int = 1, items: int = 50) -> dict:
        """Lista departamentos (via SecurityGroups que actúan como departments)."""
        return await self._request("POST", "/SecurityGroups", json={"page": page, "items": items})


mint_client = MintHCMClient()
