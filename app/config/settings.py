from pydantic_settings import BaseSettings
from dataclasses import dataclass

@dataclass
class Settings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_EXPIRY: int = 60 * 60 * 24  # 24 horas
    METRICS_RETENTION: int = 60 * 30   # 30 minutos
    
    DATABASE_URL: str = "sqlite:///network_monitor.db"
    
    class Config:
        env_file = ".env"

settings = Settings()