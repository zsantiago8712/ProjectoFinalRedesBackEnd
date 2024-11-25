from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas import models
from app.monitoring import network
from app.db import crud
from app.db.redis import get_redis
from app.monitoring.network import NetworkMonitor
import redis

router = APIRouter()

@router.post("/networks/", response_model=models.Network)
def create_network(network: models.NetworkCreate, db: Session = Depends(get_db)):
    return crud.create_network(db=db, network=network)

@router.get("/networks/", response_model=List[models.Network])
def read_networks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_networks(db, skip=skip, limit=limit)

@router.get("/networks/{network_id}", response_model=models.Network)
def read_network(network_id: int, db: Session = Depends(get_db)):
    db_network = crud.get_network(db, network_id=network_id)
    if db_network is None:
        raise HTTPException(status_code=404, detail="Network not found")
    return db_network

@router.delete("/networks/{network_id}")
def delete_network(network_id: int, db: Session = Depends(get_db), 
                  redis: redis.Redis = Depends(get_redis)):
    result = crud.delete_network(db, network_id=network_id)
    if not result:
        raise HTTPException(status_code=404, detail="Network not found")
    # Limpiar datos de Redis
    redis.delete(f"network:{network_id}:current")
    redis.srem("monitoring:active", str(network_id))
    return {"status": "success"}

@router.get("/networks/{network_id}/metrics", response_model=List[models.NetworkMetric])
def read_network_metrics(
    network_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    return crud.get_network_metrics(db, network_id=network_id, skip=skip, limit=limit)

@router.get("/networks/{network_id}/metrics/current")
def get_current_metrics(
    network_id: int,
    redis_client: redis.Redis = Depends(get_redis)
):
    """Obtiene las métricas actuales de Redis"""
    metrics = redis_client.hgetall(f"network:{network_id}:current")
    if not metrics:
        raise HTTPException(status_code=404, detail="No current metrics available")
    return metrics


@router.get("/networks/{network_id}/metrics/history")
def get_historical_metrics(
    network_id: int,
    limit: int = 100,
    redis_client: redis.Redis = Depends(get_redis)
):
    """Obtiene el historial de métricas de Redis"""
    monitor = NetworkMonitor(network_id)
    metrics = monitor.get_historical_metrics(redis_client, limit)
    if not metrics:
        raise HTTPException(status_code=404, detail="No historical metrics available")
    return metrics





@router.get("/networks/{network_id}/realtime")
def get_realtime_metrics(
    network_id: int, 
    redis: redis.Redis = Depends(get_redis)
):
    metrics = redis.hgetall(f"network:{network_id}:current")
    if not metrics:
        raise HTTPException(status_code=404, detail="No realtime data available")
    return metrics

@router.post("/networks/{network_id}/monitor")
def start_monitoring(
    network_id: int,
    db: Session = Depends(get_db),
    redis: redis.Redis = Depends(get_redis)
):
    if not crud.get_network(db, network_id=network_id):
        raise HTTPException(status_code=404, detail="Network not found")
    redis.sadd("monitoring:active", str(network_id))
    return {"status": "Monitoring started"}

@router.post("/networks/{network_id}/stop")
def stop_monitoring(
    network_id: int,
    redis: redis.Redis = Depends(get_redis)
):
    redis.srem("monitoring:active", str(network_id))
    return {"status": "Monitoring stopped"}