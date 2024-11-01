from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Host(BaseModel):
    address: str

@dataclass
class HostInDB(Host):
    id: int
    dns: Optional[str] = None
    
@dataclass
class Metric(BaseModel):
    timestamp: float
    value: float
@dataclass
class HostMetrics(BaseModel):
    latency: float
    packets_sent: int
    packets_received: int
    packet_loss: float
@dataclass
class NetworkMetrics(BaseModel):
    upload: float
    download: float