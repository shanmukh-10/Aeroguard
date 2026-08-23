"""
AeroGuard Historical Analytics API Router
-----------------------------------------
Endpoint: GET /api/history
Provides aggregated 24h, 7d, and 30d air-quality trends, statistics, and pollutant levels.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pandas as pd
from database.connection import get_db
from database.models import AirQualityRecord
from backend.schemas.air_quality import HistoryResponse, HistoryPoint

router = APIRouter(prefix="", tags=["Historical Analytics"])


@router.get("/history", response_model=HistoryResponse)
def get_historical_trends(
    timeframe: str = Query("24h", pattern="^(24h|7d|30d)$", description="Historical duration"),
    location: str = Query("DTU, Delhi - CPCB", description="Location name"),
    db: Session = Depends(get_db)
):
    """
    Returns time-series history with summary statistics.
    """
    limit_map = {
        "24h": 96,    # 96 x 15m = 24 hours
        "7d": 672,   # 7 days
        "30d": 2880  # 30 days
    }
    sample_step_map = {
        "24h": 1,   # Every 15 mins
        "7d": 4,    # Every 1 hour
        "30d": 16   # Every 4 hours
    }

    limit = limit_map.get(timeframe, 96)
    step = sample_step_map.get(timeframe, 1)

    records = db.query(AirQualityRecord).filter(
        AirQualityRecord.location.ilike(f"%{location.split(',')[0]}%")
    ).order_by(AirQualityRecord.timestamp.desc()).limit(limit).all()

    if not records:
        records = db.query(AirQualityRecord).order_by(AirQualityRecord.timestamp.desc()).limit(limit).all()

    records = list(reversed(records))
    sampled_records = records[::step]

    data_points = []
    aqi_list = []
    pm25_list = []

    for r in sampled_records:
        data_points.append(HistoryPoint(
            timestamp=r.timestamp,
            pm25=r.pm25,
            pm10=r.pm10,
            no2=r.no2,
            so2=r.so2,
            co=r.co,
            ozone=r.ozone,
            aqi=r.aqi,
            category=r.aqi_category
        ))
        if r.aqi is not None:
            aqi_list.append(r.aqi)
        if r.pm25 is not None:
            pm25_list.append(r.pm25)

    avg_aqi = round(sum(aqi_list) / len(aqi_list), 1) if aqi_list else None
    max_aqi = max(aqi_list) if aqi_list else None
    min_aqi = min(aqi_list) if aqi_list else None
    avg_pm25 = round(sum(pm25_list) / len(pm25_list), 1) if pm25_list else None
    max_pm25 = round(max(pm25_list), 1) if pm25_list else None

    return HistoryResponse(
        location=location,
        timeframe=timeframe,
        record_count=len(data_points),
        avg_aqi=avg_aqi,
        max_aqi=max_aqi,
        min_aqi=min_aqi,
        avg_pm25=avg_pm25,
        max_pm25=max_pm25,
        data=data_points
    )
