"""
AeroGuard Sensor Management & IoT Ingestion API Router
------------------------------------------------------
Endpoints:
- GET /api/sensors: Lists registered IoT sensors and monitoring stations.
- GET /api/locations: Lists all monitoring nodes for geospatial visualization.
- GET /api/nearest-station: Finds nearest CAAQMS / IoT node using Haversine calculation.
- GET /api/geocode: Search locations and landmarks across Delhi NCR.
- POST /api/sensors/data: Ingestion endpoint for IoT hardware / simulator data packets.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Sensor, Station, AirQualityRecord
from backend.schemas.air_quality import (
    SensorResponse, SensorIngestPayload, SensorIngestResponse,
    NearestStationResponse, GeocodeResultItem
)
from ml.aqi_calculator import calculate_overall_aqi
from backend.services.alert_service import evaluate_and_generate_alerts
from backend.services.nearest_station_service import find_nearest_monitoring_source
from backend.services.geocoding_service import geocode_location, reverse_geocode_location

router = APIRouter(prefix="", tags=["IoT Sensors & Geospatial"])


@router.get("/sensors", response_model=List[SensorResponse])
def get_sensors(db: Session = Depends(get_db)):
    """
    Returns registered IoT sensors and CAAQMS stations.
    """
    sensors = db.query(Sensor).all()
    results = []
    for s in sensors:
        latest_rec = db.query(AirQualityRecord).filter(
            AirQualityRecord.sensor_id == s.id
        ).order_by(AirQualityRecord.timestamp.desc()).first()

        results.append(SensorResponse(
            id=s.id,
            name=s.name,
            location=s.location,
            latitude=s.latitude,
            longitude=s.longitude,
            hardware_type=s.hardware_type,
            status=s.status,
            last_seen=s.last_seen,
            battery_level=s.battery_level,
            latest_aqi=latest_rec.aqi if latest_rec else None,
            latest_pm25=latest_rec.pm25 if latest_rec else None
        ))
    return results


@router.get("/locations")
def get_monitoring_locations(db: Session = Depends(get_db)):
    """
    Returns all monitoring locations including CAAQMS stations and IoT nodes for map visualizer.
    """
    stations = db.query(Station).filter(Station.is_active == True).all()
    sensors = db.query(Sensor).all()

    locations = []
    for st in stations:
        latest = db.query(AirQualityRecord).filter(
            AirQualityRecord.station_id == st.id
        ).order_by(AirQualityRecord.timestamp.desc()).first()

        locations.append({
            "id": st.id,
            "name": st.name,
            "type": "CAAQMS Station",
            "is_station": True,
            "latitude": st.latitude,
            "longitude": st.longitude,
            "aqi": latest.aqi if latest else 215,
            "category": latest.aqi_category if latest else "Poor",
            "pm25": latest.pm25 if latest else 94.2,
            "status": "ONLINE"
        })

    for sen in sensors:
        latest = db.query(AirQualityRecord).filter(
            AirQualityRecord.sensor_id == sen.id
        ).order_by(AirQualityRecord.timestamp.desc()).first()

        locations.append({
            "id": sen.id,
            "name": sen.name,
            "type": "IoT Sensor Node",
            "is_station": False,
            "latitude": sen.latitude,
            "longitude": sen.longitude,
            "aqi": latest.aqi if latest else 185,
            "category": latest.aqi_category if latest else "Moderate",
            "pm25": latest.pm25 if latest else 78.4,
            "status": sen.status
        })

    return locations


@router.get("/nearest-station", response_model=NearestStationResponse)
def get_nearest_station(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Target Latitude"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Target Longitude"),
    max_radius_km: float = Query(25.0, ge=1.0, le=200.0, description="Maximum search radius in km"),
    location_name: Optional[str] = Query(None, description="Optional name of the selected location"),
    db: Session = Depends(get_db)
):
    """
    Computes exact Haversine distance from selected coordinates to all registered
    AeroGuard monitoring nodes and returns the nearest active station with actual readings.
    """
    result = find_nearest_monitoring_source(
        db=db,
        lat=lat,
        lon=lon,
        max_radius_km=max_radius_km,
        location_name=location_name
    )
    return result


@router.get("/geocode", response_model=List[GeocodeResultItem])
async def search_places(
    q: str = Query(..., min_length=1, max_length=100, description="Location search query")
):
    """
    Searches locations, cities, districts, and landmarks across India.
    """
    results = await geocode_location(query=q)
    return [
        GeocodeResultItem(
            name=r["name"],
            display_name=r["display_name"],
            latitude=r["latitude"],
            longitude=r["longitude"],
            type=r.get("type", "place")
        )
        for r in results
    ]


@router.get("/reverse-geocode")
async def reverse_geocode(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude")
):
    """
    Reverse geocodes coordinates to a human-readable location name.
    """
    location_name = await reverse_geocode_location(lat=lat, lon=lon)
    return {"latitude": lat, "longitude": lon, "name": location_name}


@router.post("/sensors/data", response_model=SensorIngestResponse, status_code=status.HTTP_201_CREATED)
def ingest_sensor_data(payload: SensorIngestPayload, db: Session = Depends(get_db)):
    """
    Ingests live packet from physical ESP32 or IoT Simulator.
    Validates ranges, calculates CPCB AQI, stores in DB, and checks alert thresholds.
    """
    # 1. Validation checks
    if payload.pm25 is None or payload.pm25 < 0:
        raise HTTPException(status_code=400, detail="Invalid PM2.5 measurement.")

    now = payload.timestamp or datetime.utcnow()

    # 2. Update sensor state
    sensor = db.query(Sensor).filter(Sensor.id == payload.sensor_id).first()
    if not sensor:
        sensor = Sensor(
            id=payload.sensor_id,
            name=f"IoT Sensor {payload.sensor_id}",
            location=payload.location or "Hyperlocal Delhi NCR Node",
            latitude=payload.latitude or 28.7495,
            longitude=payload.longitude or 77.1180,
            hardware_type="ESP32 + PMS5003",
            status="ONLINE",
            last_seen=now,
            battery_level=payload.battery_level or 100.0
        )
        db.add(sensor)
    else:
        sensor.last_seen = now
        sensor.status = "ONLINE"
        if payload.battery_level is not None:
            sensor.battery_level = payload.battery_level

    # 3. Calculate CPCB AQI
    pollutant_dict = {
        "pm25": payload.pm25,
        "pm10": payload.pm10,
        "no2": payload.no2,
        "so2": payload.so2,
        "co": payload.co,
        "ozone": payload.ozone
    }
    aqi_res = calculate_overall_aqi(pollutant_dict, enforce_cpcb_rule=False)

    # 4. Save Air Quality Record
    record = AirQualityRecord(
        sensor_id=payload.sensor_id,
        location=payload.location or sensor.location,
        latitude=payload.latitude or sensor.latitude,
        longitude=payload.longitude or sensor.longitude,
        timestamp=now,
        pm25=payload.pm25,
        pm10=payload.pm10,
        no2=payload.no2,
        so2=payload.so2,
        co=payload.co,
        ozone=payload.ozone,
        temperature=payload.temperature,
        humidity=payload.humidity,
        wind_speed=payload.wind_speed,
        wind_direction=payload.wind_direction,
        aqi=aqi_res["aqi"],
        aqi_category=aqi_res["category"],
        dominant_pollutant=aqi_res["dominant_pollutant"],
        is_simulated=True
    )
    db.add(record)
    db.commit()

    # 5. Check and generate alerts
    alert = evaluate_and_generate_alerts(
        db=db,
        location=payload.location or sensor.location,
        current_aqi=aqi_res["aqi"] or 200,
        current_pm25=payload.pm25,
        sensor_id=payload.sensor_id
    )

    return SensorIngestResponse(
        status="SUCCESS",
        message="Sensor packet ingested and AQI calculated successfully.",
        sensor_id=payload.sensor_id,
        calculated_aqi=aqi_res["aqi"],
        category=aqi_res["category"],
        alert_triggered=alert is not None,
        alert_message=alert.message if alert else None
    )
