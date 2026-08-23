"""
AeroGuard Hotspots API Router
-----------------------------
Endpoint: GET /api/hotspots
Returns current localized pollution hotspots across Delhi NCR with trend and severity.
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Hotspot
from backend.schemas.air_quality import HotspotResponse

router = APIRouter(prefix="", tags=["Hotspots"])


@router.get("/hotspots", response_model=List[HotspotResponse])
def get_pollution_hotspots(db: Session = Depends(get_db)):
    """
    Returns list of active pollution hotspots ordered by AQI severity.
    """
    hotspots = db.query(Hotspot).order_by(Hotspot.current_aqi.desc()).all()
    return [
        HotspotResponse(
            id=h.id,
            location=h.location,
            latitude=h.latitude,
            longitude=h.longitude,
            current_aqi=h.current_aqi,
            current_pm25=h.current_pm25,
            trend=h.trend,
            severity_level=h.severity_level,
            likely_source=h.likely_source,
            confidence_score=h.confidence_score,
            last_updated=h.last_updated
        )
        for h in hotspots
    ]
