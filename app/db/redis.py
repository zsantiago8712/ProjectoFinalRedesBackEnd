import redis
from app.core.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

def get_redis():
    try:
        yield redis_client
    finally:
        pass  # Redis connection is managed by the client pool

def init_redis():
    try:
        redis_client.ping()
        return True
    except redis.ConnectionError:
        return False