from fastapi import APIRouter, HTTPException
from app.models.schemas import Host, HostInDB
from app.core.database import add_host, get_host
from app.services.metrics_service import metrics_service
import sqlite3

router = APIRouter()

@router.post("/hosts")
async def add_host(host: Host) -> dict[str, int]:
    # Probar el host antes de agregarlo
    test_result = metrics_service.ping_host(host.address)
    if not test_result["success"]:
        raise HTTPException(status_code=400, detail="No se pudo conectar al host")

    host_id = add_host(host.address)
    return {"id": host_id}
    

@router.get("/hosts")
async def get_hosts() -> list[HostInDB]:
    result = get_host()
    return [
            HostInDB(id=row[0], address=row[1], dns=row[2])
            for row in result
        ]