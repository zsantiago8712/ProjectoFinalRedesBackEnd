from sqlalchemy.orm import Session
from app.schemas import models
from app.db import models as db_models

def create_network(db: Session, network: models.NetworkCreate):
    db_network = db_models.Network(**network.dict())
    db.add(db_network)
    db.commit()
    db.refresh(db_network)
    return db_network

def get_network(db: Session, network_id: int):
    return db.query(db_models.Network).filter(db_models.Network.id == network_id).first()

def get_networks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(db_models.Network).offset(skip).limit(limit).all()

def delete_network(db: Session, network_id: int):
    network = db.query(db_models.Network).filter(db_models.Network.id == network_id).first()
    if network:
        db.delete(network)
        db.commit()
        return True
    return False

def create_network_metric(db: Session, metric: models.NetworkMetricCreate):
    db_metric = db_models.NetworkMetric(**metric.dict())
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric

def get_network_metrics(db: Session, network_id: int, skip: int = 0, limit: int = 100):
    return db.query(db_models.NetworkMetric)\
        .filter(db_models.NetworkMetric.network_id == network_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

def create_route_change(db: Session, route_change: models.RouteChangeBase):
    db_route_change = db_models.RouteChange(**route_change.dict())
    db.add(db_route_change)
    db.commit()
    db.refresh(db_route_change)
    return db_route_change