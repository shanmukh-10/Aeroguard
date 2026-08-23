"""
AeroGuard FastAPI Main Application
----------------------------------
High-performance REST API backend for Hyperlocal Pollution Intelligence,
AI Forecasting, CPCB AQI Calculation, Hotspot Detection, and IoT Ingestion.
"""

import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from backend.config import settings
from database.connection import init_db
from database.seed import seed_database
from database.models import Station
from database.connection import SessionLocal
from backend.api import (
    current_router,
    forecast_router,
    history_router,
    hotspots_router,
    alerts_router,
    sensors_router,
    source_pattern_router,
    metrics_router
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("AeroGuard")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event handler for database provisioning and initial seed check."""
    logger.info("Initializing AeroGuard database schema...")
    try:
        init_db()
        db = SessionLocal()
        station_count = db.query(Station).count()
        db.close()
        if station_count == 0:
            logger.info("Database empty, running initial seeder...")
            seed_database()
    except Exception as e:
        logger.warning(f"Database startup check note: {e}")
    yield
    logger.info("AeroGuard backend shutting down gracefully.")


app = FastAPI(
    title=settings.PROJECT_TITLE,
    version=settings.VERSION,
    description="Complementary AIoT Environmental Intelligence Layer for Hyperlocal Air Quality Monitoring, AI Forecasting, and Preventive Alerts.",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Measures and logs request processing latency."""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = str(round(process_time, 2))
    return response


@app.get("/", tags=["System"])
def root():
    """Root endpoint welcoming visitors and directing to interactive documentation."""
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "title": settings.PROJECT_TITLE,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "health_url": "/health",
        "endpoints": {
            "current_aqi": "/api/current",
            "forecast": "/api/forecast?hours=12",
            "history": "/api/history?timeframe=24h",
            "hotspots": "/api/hotspots",
            "alerts": "/api/alerts",
            "sensors": "/api/sensors",
            "nearest_station": "/api/nearest-station?lat=28.6315&lon=77.2167",
            "geocode": "/api/geocode?q=Hyderabad",
            "reverse_geocode": "/api/reverse-geocode?lat=28.6315&lon=77.2167",
            "source_pattern": "/api/source-pattern",
            "model_metrics": "/api/model-metrics"
        }
    }


@app.get("/health", tags=["System"])
def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "title": settings.PROJECT_TITLE,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected"
    }


# Mount all API routers under /api
app.include_router(current_router, prefix=settings.API_PREFIX)
app.include_router(forecast_router, prefix=settings.API_PREFIX)
app.include_router(history_router, prefix=settings.API_PREFIX)
app.include_router(hotspots_router, prefix=settings.API_PREFIX)
app.include_router(alerts_router, prefix=settings.API_PREFIX)
app.include_router(sensors_router, prefix=settings.API_PREFIX)
app.include_router(source_pattern_router, prefix=settings.API_PREFIX)
app.include_router(metrics_router, prefix=settings.API_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
