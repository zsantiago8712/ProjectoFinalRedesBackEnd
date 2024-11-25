from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes
from app.api.websocket_routes import router as websocket_router
from app.core.config import settings
from app.db.database import engine, Base
from app.db.redis import init_redis

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Verificar conexión con Redis
if not init_redis():
    raise Exception("No se pudo conectar con Redis")

# Incluir rutas
app.include_router(routes.router, prefix=settings.API_V1_STR)
app.include_router(websocket_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "Network Monitor API",
        "docs": "/docs",
        "redoc": "/redoc"
    }