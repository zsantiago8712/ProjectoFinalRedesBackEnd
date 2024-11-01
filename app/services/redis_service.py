import redis
import json
from datetime import datetime
from typing import List, Optional
from app.config.settings import settings
from dataclasses import dataclass

@dataclass
class RedisService:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )

    def get_key(self, host_id: int, metric_type: str) -> str:
        return f"host:{host_id}:{metric_type}"

    def save_metric(self, host_id: int, metric_type: str, data: dict):
        key = self.get_key(host_id, metric_type)
        timestamp = datetime.now().timestamp()
        
        current_data = self.client.get(key)
        metrics_list = json.loads(current_data) if current_data else []
        
        metrics_list.append({"timestamp": timestamp, **data})
        
        # Mantener solo datos recientes
        current_time = datetime.now().timestamp()
        metrics_list = [
            m for m in metrics_list 
            if current_time - m["timestamp"] <= settings.METRICS_RETENTION
        ]
        
        self.client.set(key, json.dumps(metrics_list), ex=settings.REDIS_EXPIRY)

    def get_metrics(self, host_id: int, metric_type: str, minutes: int = 30) -> List[dict]:
        key = self.get_key(host_id, metric_type)
        data = self.client.get(key)
        if not data:
            return []

        metrics_list = json.loads(data)
        current_time = datetime.now().timestamp()
        
        return [
            m for m in metrics_list 
            if current_time - m["timestamp"] <= minutes * 60
        ]

redis_service = RedisService()