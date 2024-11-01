from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import hosts
from app.api.websocket.monitor import monitor_host
from app.core.database import init_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar base de datos
init_db()

# Incluir routers
app.include_router(hosts.router)

@app.websocket("/ws/{host_id}")
async def websocket_endpoint(websocket: WebSocket, host_id: int):
    await monitor_host(websocket, host_id)