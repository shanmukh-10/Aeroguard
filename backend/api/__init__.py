from backend.api.current import router as current_router
from backend.api.forecast import router as forecast_router
from backend.api.history import router as history_router
from backend.api.hotspots import router as hotspots_router
from backend.api.alerts import router as alerts_router
from backend.api.sensors import router as sensors_router
from backend.api.source_pattern import router as source_pattern_router
from backend.api.metrics import router as metrics_router

__all__ = [
    "current_router",
    "forecast_router",
    "history_router",
    "hotspots_router",
    "alerts_router",
    "sensors_router",
    "source_pattern_router",
    "metrics_router"
]
