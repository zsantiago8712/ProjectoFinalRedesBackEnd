from fastapi import WebSocket
import asyncio
from app.services.metrics_service import metrics_service
from app.services.redis_service import redis_service
from app.core.database import get_host
from datetime import datetime

async def monitor_host(websocket: WebSocket, host_id: int):
    await websocket.accept()
    
    try:
        
        host = get_host(host_id)

        if host is None:
            await websocket.close()
            return

        address = host[0]
        
        while True:
            # Obtener y guardar métricas
            host_metrics = metrics_service.ping_host(address)
            if host_metrics["success"]:
                redis_service.save_metric(host_id, "host_metrics", host_metrics)
            
            upload_speed, download_speed = metrics_service.get_network_speed()
            network_metrics = {"upload": upload_speed, "download": download_speed}
            redis_service.save_metric(host_id, "network_metrics", network_metrics)
            
            # Enviar datos al cliente
            current_metrics = {
                "host_metrics": host_metrics,
                "network_metrics": network_metrics,
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_json(current_metrics)
            
            # Agregar métricas diarias si es necesario
            if datetime.now().minute == 0:
                metrics_service.aggregate_daily_metrics(host_id)
            
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"Error in websocket: {e}")
    finally:
        await websocket.close()