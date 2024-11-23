from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.core.enums import ConnectionType

class NetworkBase(BaseModel):
    name: str
    alias: str
    location: Optional[str] = None

class NetworkCreate(NetworkBase):
    pass

class Network(NetworkBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class NetworkMetricBase(BaseModel):
    network_id: int
    upload_speed: float
    download_speed: float
    latency: float
    packet_loss: float
    connection_type: ConnectionType  # Usando el enum aquí

class NetworkMetricCreate(NetworkMetricBase):
    pass

class NetworkMetric(NetworkMetricBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class RouteChangeBase(BaseModel):
    network_id: int
    old_route: str
    new_route: str

class RouteChange(RouteChangeBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True