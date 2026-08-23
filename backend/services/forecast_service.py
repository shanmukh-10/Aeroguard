"""
AeroGuard Forecast Service
--------------------------
Integrates trained ML models with database time-series records to generate
future multi-step forecasts and trend projections.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from database.models import AirQualityRecord, Prediction
from ml.prediction import AeroGuardPredictor

# Initialize global predictor instance
predictor = AeroGuardPredictor(model_dir='models')


def get_forecast_for_location(db: Session, location: str = "DTU, Delhi - CPCB", hours_ahead: int = 12) -> Dict[str, Any]:
    """
    Retrieves recent records from database and computes future forecasts.
    """
    # Fetch recent records for location
    records = db.query(AirQualityRecord).filter(
        AirQualityRecord.location.ilike(f"%{location.split(',')[0]}%")
    ).order_by(AirQualityRecord.timestamp.desc()).limit(96).all()

    if not records:
        # Fallback to any recent records in database
        records = db.query(AirQualityRecord).order_by(AirQualityRecord.timestamp.desc()).limit(96).all()

    record_dicts = []
    for r in reversed(records):
        record_dicts.append({
            "timestamp": r.timestamp,
            "pm25": r.pm25,
            "pm10": r.pm10,
            "no2": r.no2,
            "so2": r.so2,
            "co": r.co,
            "ozone": r.ozone,
            "rh": r.humidity,
            "ws": r.wind_speed,
            "wd": r.wind_direction,
            "aqi": r.aqi
        })

    # If predictor model was loaded, predict
    res = predictor.predict_multi_step(record_dicts, hours_ahead=hours_ahead)
    return res
