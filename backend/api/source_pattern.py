"""
AeroGuard Source Pattern Analysis API Router
--------------------------------------------
Endpoint: GET /api/source-pattern
Returns probabilistic likely pollution-source pattern analysis based on stoichiometric ratios
(PM2.5/PM10, NO2/SO2, CO), diurnal traffic patterns, and atmospheric dispersion state.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from database.connection import get_db
from database.models import AirQualityRecord
from backend.schemas.air_quality import SourcePatternResponse
from backend.services.source_pattern_service import analyze_source_pattern

router = APIRouter(prefix="", tags=["Source Pattern Analysis"])


@router.get("/source-pattern", response_model=SourcePatternResponse)
def get_source_pattern_analysis(
    location: str = Query("DTU, Delhi - CPCB", description="Location name"),
    db: Session = Depends(get_db)
):
    """
    Computes likely source pattern (Traffic, Industrial, Construction Dust, Regional Background).
    """
    record = db.query(AirQualityRecord).filter(
        AirQualityRecord.location.ilike(f"%{location.split(',')[0]}%")
    ).order_by(AirQualityRecord.timestamp.desc()).first()

    pm25 = record.pm25 if record and record.pm25 else 94.2
    pm10 = record.pm10 if record and record.pm10 else 168.4
    no2 = record.no2 if record and record.no2 else 48.2
    so2 = record.so2 if record and record.so2 else 14.5
    co = record.co if record and record.co else 1.35
    ozone = record.ozone if record and record.ozone else 32.1
    ws = record.wind_speed if record and record.wind_speed else 2.2
    wd = record.wind_direction if record and record.wind_direction else 180.0
    hour = record.timestamp.hour if record and record.timestamp else datetime.utcnow().hour

    analysis = analyze_source_pattern(
        pm25=pm25,
        pm10=pm10,
        no2=no2,
        so2=so2,
        co=co,
        ozone=ozone,
        ws=ws,
        wd=wd,
        hour=hour
    )

    return SourcePatternResponse(
        location=location,
        likely_source_pattern=analysis["likely_source_pattern"],
        confidence_score=analysis["confidence_score"],
        dominant_factors=analysis["dominant_factors"],
        supporting_indicators=analysis["supporting_indicators"],
        meteorological_context=analysis["meteorological_context"],
        disclaimer=analysis["disclaimer"]
    )
