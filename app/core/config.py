from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Config
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Network Monitor"
    
    # Database
    SQLITE_URL: str = "sqlite:///network_monitor.db"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Monitoring Config
    MONITOR_INTERVAL: int = 300  # 5 minutes
    ALERT_THRESHOLD_LATENCY: float = 100.0  # ms
    ALERT_THRESHOLD_PACKET_LOSS: float = 5.0  # percentage
    MIN_UPLOAD_SPEED: float = 10.0  # Mbps
    MIN_DOWNLOAD_SPEED: float = 20.0  # Mbps
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()