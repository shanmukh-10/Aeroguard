"""
AeroGuard Pydantic Request & Response Schemas
---------------------------------------------
Standardized schemas for API endpoints, payload validation, and data serialization.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class SubIndexBreakdown(BaseModel):
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    no2: Optional[float] = None
    so2: Optional[float] = None
    co: Optional[float] = None
    ozone: Optional[float] = None
    nh3: Optional[float] = None


class CurrentAirQualityResponse(BaseModel):
    station_id: Optional[str] = None
    sensor_id: Optional[str] = None
    location: str
    latitude: float
    longitude: float
    timestamp: datetime
    aqi: Optional[int]
    category: str
    color: str
    dominant_pollutant: Optional[str] = None
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    no2: Optional[float] = None
    so2: Optional[float] = None
    co: Optional[float] = None
    ozone: Optional[float] = None
    nh3: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None
    advisory: str
    sensitive_advisory: str
    trend: str = "Stable"
    sub_indices: Dict[str, float] = {}


class ForecastPoint(BaseModel):
    forecast_time: datetime
    hours_from_now: float
    predicted_pm25: float
    predicted_pm10: Optional[float] = None
    predicted_aqi: int
    category: str
    color: str
    advisory: str


class ForecastResponse(BaseModel):
    location: str
    current_pm25: float
    trend: str
    model_name: str
    forecast: List[ForecastPoint]
    model_metrics: Dict[str, Any] = {}


class HistoryPoint(BaseModel):
    timestamp: datetime
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    no2: Optional[float] = None
    so2: Optional[float] = None
    co: Optional[float] = None
    ozone: Optional[float] = None
    aqi: Optional[int] = None
    category: Optional[str] = None


class HistoryResponse(BaseModel):
    location: str
    timeframe: str  # 24h, 7d, 30d
    record_count: int
    avg_aqi: Optional[float] = None
    max_aqi: Optional[int] = None
    min_aqi: Optional[int] = None
    avg_pm25: Optional[float] = None
    max_pm25: Optional[float] = None
    data: List[HistoryPoint]


class HotspotResponse(BaseModel):
    id: int
    location: str
    latitude: float
    longitude: float
    current_aqi: int
    current_pm25: float
    trend: str
    severity_level: str
    likely_source: Optional[str] = None
    confidence_score: Optional[float] = None
    last_updated: datetime


class AlertResponse(BaseModel):
    id: int
    location: str
    severity: str  # INFO, WARNING, DANGER, CRITICAL
    title: str
    message: str
    current_aqi: int
    predicted_aqi: Optional[int] = None
    reason: Optional[str] = None
    timestamp: datetime
    is_active: bool


class SensorResponse(BaseModel):
    id: str
    name: str
    location: str
    latitude: float
    longitude: float
    hardware_type: str
    status: str
    last_seen: datetime
    battery_level: float
    latest_aqi: Optional[int] = None
    latest_pm25: Optional[float] = None


class SensorIngestPayload(BaseModel):
    sensor_id: str = Field(..., description="Unique hardware sensor ID e.g. ESP32-AERO-01")
    timestamp: Optional[datetime] = None
    location: Optional[str] = "Shahbad Daulatpur, Rohini"
    latitude: Optional[float] = 28.7495
    longitude: Optional[float] = 77.1180
    pm25: float = Field(..., ge=0, le=1000, description="PM2.5 concentration in µg/m³")
    pm10: Optional[float] = Field(None, ge=0, le=1500, description="PM10 concentration in µg/m³")
    no2: Optional[float] = Field(None, ge=0, le=800)
    so2: Optional[float] = Field(None, ge=0, le=1500)
    co: Optional[float] = Field(None, ge=0, le=100)
    ozone: Optional[float] = Field(None, ge=0, le=1000)
    temperature: Optional[float] = Field(None, ge=-20, le=60)
    humidity: Optional[float] = Field(None, ge=0, le=100)
    wind_speed: Optional[float] = Field(None, ge=0, le=60)
    wind_direction: Optional[float] = Field(None, ge=0, le=360)
    battery_level: Optional[float] = 100.0


class SensorIngestResponse(BaseModel):
    status: str
    message: str
    sensor_id: str
    calculated_aqi: Optional[int]
    category: str
    alert_triggered: bool
    alert_message: Optional[str] = None


class SourcePatternResponse(BaseModel):
    location: str
    likely_source_pattern: str
    confidence_score: float  # 0.0 to 1.0
    dominant_factors: List[str]
    supporting_indicators: Dict[str, Any]
    meteorological_context: Dict[str, Any]
    disclaimer: str = "Likely pollution-source pattern analysis based on stoichiometric pollutant ratios and meteorological context. Not a regulatory source attribution."


class ModelMetricItem(BaseModel):
    model_name: str
    mae: float
    rmse: float
    r2: float
    mae_improvement_pct: Optional[float] = None
    rmse_improvement_pct: Optional[float] = None
    training_time_seconds: Optional[float] = None
    inference_latency_ms: Optional[float] = None


class ModelMetricsResponse(BaseModel):
    target: str
    frequency: str
    dataset: str
    train_samples: int
    test_samples: int
    best_model: str
    models: Dict[str, Any]


# ==========================================
# Location Search & Nearest Station Schemas
# ==========================================

class SelectedLocationInfo(BaseModel):
    name: str = "Selected Location"
    latitude: float
    longitude: float


class NearestStationDetail(BaseModel):
    station_id: str
    name: str
    type: str  # "CAAQMS Reference Station" or "Hyperlocal IoT Sensor Node"
    is_station: bool
    latitude: float
    longitude: float
    distance_km: float


class NearestAirQualityData(BaseModel):
    timestamp: datetime
    aqi: Optional[int] = None
    category: str
    color: str
    dominant_pollutant: Optional[str] = None
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    no2: Optional[float] = None
    so2: Optional[float] = None
    co: Optional[float] = None
    ozone: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    advisory: str
    sensitive_advisory: str


class NearestStationResponse(BaseModel):
    selected_location: SelectedLocationInfo
    has_nearby_station: bool
    coverage_type: str  # DIRECT, NEARBY, EXTENDED, OUT_OF_RANGE
    coverage_label: str
    distance_km: Optional[float] = None
    nearest_station: Optional[NearestStationDetail] = None
    air_quality: Optional[NearestAirQualityData] = None
    forecast_pm25_2h: Optional[float] = None
    forecast_aqi_2h: Optional[int] = None
    disclaimer: str


class GeocodeResultItem(BaseModel):
    name: str
    display_name: str
    latitude: float
    longitude: float
    type: str = "place"
