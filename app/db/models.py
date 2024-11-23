from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from .database import Base

class Network(Base):
    __tablename__ = "networks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    alias = Column(String, nullable=False)
    location = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class NetworkMetric(Base):
    __tablename__ = "network_metrics"

    id = Column(Integer, primary_key=True, index=True)
    network_id = Column(Integer, ForeignKey("networks.id"))
    upload_speed = Column(Float)
    download_speed = Column(Float)
    latency = Column(Float)
    packet_loss = Column(Float)
    connection_type = Column(Integer)  # 0: Ethernet, 1: WiFi
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class RouteChange(Base):
    __tablename__ = "route_changes"

    id = Column(Integer, primary_key=True, index=True)
    network_id = Column(Integer, ForeignKey("networks.id"))
    old_route = Column(String)
    new_route = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())