"""
AeroGuard Hotspot Detection Engine
----------------------------------
Identifies geographic areas exhibiting elevated pollution concentrations,
computes local anomaly scores, and tracks hotspot severity trends.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database.models import Hotspot, AirQualityRecord, Station, Sensor
from ml.aqi_calculator import calculate_overall_aqi


def compute_active_hotspots(db: Session) -> List[Hotspot]:
    """
    Returns current active hotspots ordered by AQI severity.
    """
    hotspots = db.query(Hotspot).order_by(Hotspot.current_aqi.desc()).all()
    return hotspots
