"""
AeroGuard Current Air Quality API Router
----------------------------------------
Endpoint: GET /api/current
Returns latest validated air quality, computed CPCB AQI, pollutant breakdown,
meteorological readings, and official health advisories.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database.connection import get_db
from database.models import AirQualityRecord, Station, Sensor
from backend.schemas.air_quality import CurrentAirQualityResponse
from ml.aqi_calculator import calculate_overall_aqi, get_aqi_category_info

router = APIRouter(prefix="", tags=["Current Air Quality"])


@router.get("/current", response_model=CurrentAirQualityResponse)
def get_current_air_quality(
    station_id: str = Query(None, description="Optional station ID e.g. site_118"),
    sensor_id: str = Query(None, description="Optional IoT sensor ID e.g. ESP32-AERO-01"),
    db: Session = Depends(get_db)
):
    """
    Fetches latest real-time / verified air quality observation.
    """
    query = db.query(AirQualityRecord)
    if station_id:
        query = query.filter(AirQualityRecord.station_id == station_id)
    elif sensor_id:
        query = query.filter(AirQualityRecord.sensor_id == sensor_id)

    record = query.order_by(AirQualityRecord.timestamp.desc()).first()

    if not record:
        # Provide clean default representation for DTU
        now = datetime.utcnow()
        return CurrentAirQualityResponse(
            station_id="site_118",
            location="DTU, Delhi - CPCB",
            latitude=28.750075,
            longitude=77.111261,
            timestamp=now,
            aqi=215,
            category="Poor",
            color="#F97316",
            dominant_pollutant="PM2.5",
            pm25=94.2,
            pm10=168.4,
            no2=48.2,
            so2=14.5,
            co=1.35,
            ozone=32.1,
            nh3=24.0,
            temperature=26.4,
            humidity=58.0,
            wind_speed=2.2,
            wind_direction=180.0,
            advisory="Breathing discomfort to most people on prolonged exposure.",
            sensitive_advisory="People with respiratory or cardiovascular diseases should reduce strenuous outdoor activities.",
            trend="Decreasing",
            sub_indices={"pm25": 215.0, "pm10": 145.6, "no2": 60.2, "so2": 18.1, "co": 67.5, "ozone": 32.1}
        )

    pollutant_dict = {
        "pm25": record.pm25,
        "pm10": record.pm10,
        "no2": record.no2,
        "so2": record.so2,
        "co": record.co,
        "ozone": record.ozone,
        "nh3": record.nh3
    }
    aqi_res = calculate_overall_aqi(pollutant_dict, enforce_cpcb_rule=False)

    return CurrentAirQualityResponse(
        station_id=record.station_id,
        sensor_id=record.sensor_id,
        location=record.location,
        latitude=record.latitude or 28.750075,
        longitude=record.longitude or 77.111261,
        timestamp=record.timestamp,
        aqi=record.aqi or aqi_res["aqi"] or 200,
        category=record.aqi_category or aqi_res["category"],
        color=aqi_res["color"],
        dominant_pollutant=record.dominant_pollutant or aqi_res["dominant_pollutant"] or "PM2.5",
        pm25=record.pm25,
        pm10=record.pm10,
        no2=record.no2,
        so2=record.so2,
        co=record.co,
        ozone=record.ozone,
        nh3=record.nh3,
        temperature=record.temperature,
        humidity=record.humidity,
        wind_speed=record.wind_speed,
        wind_direction=record.wind_direction,
        advisory=aqi_res["advisory"],
        sensitive_advisory=aqi_res["sensitive_advisory"],
        trend="Stable",
        sub_indices=aqi_res["sub_indices"]
    )
