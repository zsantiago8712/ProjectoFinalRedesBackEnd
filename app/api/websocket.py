from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import asyncio
import json
from app.monitoring.network import NetworkMonitor
from app.db.redis import get_redis
import redis

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.monitoring_tasks: Dict[int, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, network_id: int):
        await websocket.accept()
        if network_id not in self.active_connections:
            self.active_connections[network_id] = set()
        self.active_connections[network_id].add(websocket)

    def disconnect(self, websocket: WebSocket, network_id: int):
        self.active_connections[network_id].remove(websocket)
        if not self.active_connections[network_id]:
            if network_id in self.monitoring_tasks:
                self.monitoring_tasks[network_id].cancel()
                del self.monitoring_tasks[network_id]
            del self.active_connections[network_id]

    async def broadcast(self, message: str, network_id: int):
        if network_id in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[network_id]:
                try:
                    await connection.send_text(message)
                except WebSocketDisconnect:
                    dead_connections.add(connection)
            
            # Limpiar conexiones muertas
            for dead in dead_connections:
                self.active_connections[network_id].remove(dead)

    async def monitor_network(self, network_id: int, redis_client: redis.Redis):
        monitor = NetworkMonitor(network_id)
        
        while True:
            try:
                # Obtener y almacenar métricas en Redis
                metrics = monitor.get_realtime_data(redis_client)
                
                # Enviar a través de WebSocket
                await self.broadcast(json.dumps(metrics), network_id)
                
                # Esperar intervalo
                await asyncio.sleep(5)
                
            except Exception as e:
                await self.broadcast(
                    json.dumps({"error": str(e)}),
                    network_id
                )
                await asyncio.sleep(5)

manager = ConnectionManager()

async def get_websocket_manager():
    return manager