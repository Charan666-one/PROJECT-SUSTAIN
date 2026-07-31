"""
Homoeo CDSS — FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routers import api_router
from app.core.config import settings

app = FastAPI(
    title="Homoeo CDSS API",
    description="Intelligent Homeopathic Clinical Decision Support System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# Schema is managed by Alembic migrations (`alembic upgrade head`), not create_all,
# so schema changes never drop data. run_local.sh applies migrations on start.

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Homoeo CDSS"}
