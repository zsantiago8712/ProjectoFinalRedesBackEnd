from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.db.redis import get_redis
from .websocket import get_websocket_manager
import asyncio
import redis

router = APIRouter()

@router.websocket("/ws/{network_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    network_id: int,
    manager = Depends(get_websocket_manager),
    redis_client: redis.Redis = Depends(get_redis)
):
    await manager.connect(websocket, network_id)
    
    try:
        # Iniciar monitoreo si no existe
        if network_id not in manager.monitoring_tasks:
            task = asyncio.create_task(
                manager.monitor_network(network_id, redis_client)
            )
            manager.monitoring_tasks[network_id] = task
        
        # Mantener conexión abierta
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, network_id)

# Exportamos el router
__all__ = ['router']