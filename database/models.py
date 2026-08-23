"""
AeroGuard SQLAlchemy Database ORM Models
----------------------------------------
Declares database entities for stations, IoT sensors, historical & real-time
air quality records, AI predictions, active alerts, hotspots, and model metrics.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Station(Base):
    __tablename__ = "stations"

    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False, default="Delhi")
    state = Column(String(100), nullable=False, default="Delhi")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    station_type = Column(String(100), default="CAAQMS")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    records = relationship("AirQualityRecord", back_populates="station")


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    hardware_type = Column(String(100), default="ESP32 + PMS5003 + DHT22")
    status = Column(String(50), default="ONLINE")  # ONLINE, MAINTENANCE, OFFLINE
    last_seen = Column(DateTime, default=datetime.utcnow)
    battery_level = Column(Float, default=100.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    records = relationship("AirQualityRecord", back_populates="sensor")


class AirQualityRecord(Base):
    __tablename__ = "air_quality_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String(64), ForeignKey("stations.id", ondelete="SET NULL"), nullable=True)
    sensor_id = Column(String(64), ForeignKey("sensors.id", ondelete="SET NULL"), nullable=True)
    location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Pollutants
    pm25 = Column(Float, nullable=True)
    pm10 = Column(Float, nullable=True)
    no = Column(Float, nullable=True)
    no2 = Column(Float, nullable=True)
    nox = Column(Float, nullable=True)
    nh3 = Column(Float, nullable=True)
    so2 = Column(Float, nullable=True)
    co = Column(Float, nullable=True)
    ozone = Column(Float, nullable=True)

    # Meteorological / Contextual
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    wind_direction = Column(Float, nullable=True)

    # AQI Metrics
    aqi = Column(Integer, nullable=True, index=True)
    aqi_category = Column(String(50), nullable=True)
    dominant_pollutant = Column(String(50), nullable=True)
    is_simulated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    station = relationship("Station", back_populates="records")
    sensor = relationship("Sensor", back_populates="records")

    __table_args__ = (
        Index("idx_records_station_time", "station_id", "timestamp"),
        Index("idx_records_sensor_time", "sensor_id", "timestamp"),
    )


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(255), nullable=False)
    station_id = Column(String(64), nullable=True)
    forecast_time = Column(DateTime, nullable=False, index=True)
    hours_ahead = Column(Float, nullable=False)
    predicted_pm25 = Column(Float, nullable=False)
    predicted_pm10 = Column(Float, nullable=True)
    predicted_aqi = Column(Integer, nullable=False)
    predicted_category = Column(String(50), nullable=True)
    model_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(255), nullable=False)
    station_id = Column(String(64), nullable=True)
    sensor_id = Column(String(64), nullable=True)
    severity = Column(String(50), nullable=False)  # INFO, WARNING, DANGER, CRITICAL
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    current_aqi = Column(Integer, nullable=False)
    predicted_aqi = Column(Integer, nullable=True)
    reason = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class Hotspot(Base):
    __tablename__ = "hotspots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    current_aqi = Column(Integer, nullable=False)
    current_pm25 = Column(Float, nullable=False)
    trend = Column(String(50), nullable=False)  # Increasing, Stable, Decreasing
    severity_level = Column(String(50), nullable=False)  # Moderate, High, Severe, Critical
    likely_source = Column(String(255), nullable=True)
    confidence_score = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(100), nullable=False)
    mae = Column(Float, nullable=False)
    rmse = Column(Float, nullable=False)
    r2 = Column(Float, nullable=False)
    mae_improvement_pct = Column(Float, nullable=True)
    rmse_improvement_pct = Column(Float, nullable=True)
    training_time_seconds = Column(Float, nullable=True)
    inference_latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
