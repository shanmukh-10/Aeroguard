# AeroGuard REST API Reference

Base URL: `http://localhost:8000/api`

---

### 1. System Health
`GET /health`
- **Response**: `200 OK`
```json
{
  "status": "healthy",
  "service": "AeroGuard",
  "version": "1.0.0",
  "environment": "development",
  "database": "connected"
}
```

---

### 2. Current Air Quality
`GET /api/current?station_id=site_118`
- **Parameters**: `station_id` (optional), `sensor_id` (optional)
- **Response**: `200 OK`
```json
{
  "station_id": "site_118",
  "location": "DTU, Delhi - CPCB",
  "latitude": 28.750075,
  "longitude": 77.111261,
  "timestamp": "2026-08-22T21:45:00Z",
  "aqi": 215,
  "category": "Poor",
  "color": "#F97316",
  "dominant_pollutant": "PM2.5",
  "pm25": 94.2,
  "pm10": 168.4,
  "no2": 48.2,
  "so2": 14.5,
  "co": 1.35,
  "ozone": 32.1,
  "temperature": 26.4,
  "humidity": 58.0,
  "wind_speed": 2.2,
  "advisory": "Breathing discomfort to most people on prolonged exposure.",
  "sensitive_advisory": "People with respiratory or cardiovascular diseases should reduce strenuous outdoor activities."
}
```

---

### 3. AI Multi-Step Forecast
`GET /api/forecast?hours=12`
- **Parameters**: `hours` (1 to 48, default 12)
- **Response**: `200 OK`
```json
{
  "location": "DTU, Delhi - CPCB",
  "current_pm25": 94.2,
  "trend": "Decreasing",
  "model_name": "Random Forest Regressor",
  "forecast": [
    {
      "forecast_time": "2026-08-22T22:00:00Z",
      "hours_from_now": 0.25,
      "predicted_pm25": 92.8,
      "predicted_aqi": 210,
      "category": "Poor",
      "color": "#F97316",
      "advisory": "Breathing discomfort on prolonged exposure."
    }
  ]
}
```

---

### 4. Historical Trends
`GET /api/history?timeframe=24h`
- **Parameters**: `timeframe` (`24h`, `7d`, `30d`)
- **Response**: `200 OK`

---

### 5. Hotspots
`GET /api/hotspots`
- **Response**: `200 OK`

---

### 6. Automated Alerts
`GET /api/alerts?active_only=true`
- **Response**: `200 OK`

---

### 7. Likely Source Pattern
`GET /api/source-pattern?location=DTU`
- **Response**: `200 OK`
```json
{
  "location": "DTU, Delhi - CPCB",
  "likely_source_pattern": "Likely Traffic-Associated Pattern",
  "confidence_score": 0.88,
  "dominant_factors": [
    "Elevated NO2/SO2 ratio indicative of internal combustion exhaust",
    "Coincides with peak diurnal urban transit hours"
  ],
  "disclaimer": "Likely pollution-source pattern analysis based on stoichiometric ratios and meteorological context. Not a regulatory source attribution."
}
```

---

### 8. IoT Sensor Ingestion
`POST /api/sensors/data`
- **Request Body**:
```json
{
  "sensor_id": "ESP32-AERO-01",
  "location": "Shahbad Daulatpur, Rohini",
  "pm25": 88.5,
  "pm10": 152.0,
  "no2": 42.5,
  "so2": 12.0,
  "co": 1.35,
  "ozone": 28.0,
  "temperature": 27.8,
  "humidity": 58.2,
  "battery_level": 98.0
}
```
- **Response**: `201 Created`
```json
{
  "status": "SUCCESS",
  "message": "Sensor packet ingested and AQI calculated successfully.",
  "sensor_id": "ESP32-AERO-01",
  "calculated_aqi": 195,
  "category": "Moderate",
  "alert_triggered": false
}
```

---

### 9. Nearest Monitoring Station Calculation
`GET /api/nearest-station?lat=28.6315&lon=77.2167&max_radius_km=25.0`
- **Parameters**: `lat` (float, -90 to 90), `lon` (float, -180 to 180), `max_radius_km` (float, default 25.0), `location_name` (optional)
- **Response**: `200 OK`
```json
{
  "selected_location": {
    "name": "Connaught Place",
    "latitude": 28.6315,
    "longitude": 77.2167
  },
  "has_nearby_station": true,
  "coverage_type": "DIRECT",
  "coverage_label": "Direct Sensor Data (Co-located <100m)",
  "distance_km": 0.0,
  "nearest_station": {
    "station_id": "ESP32-AERO-02",
    "name": "Connaught Place Transit Node",
    "type": "Hyperlocal IoT Sensor Node",
    "is_station": false,
    "latitude": 28.6315,
    "longitude": 77.2167,
    "distance_km": 0.0
  },
  "air_quality": {
    "timestamp": "2026-08-23T15:30:00Z",
    "aqi": 215,
    "category": "Poor",
    "color": "#F97316",
    "dominant_pollutant": "PM2.5",
    "pm25": 94.2,
    "pm10": 168.4,
    "no2": 48.2,
    "so2": 14.5,
    "co": 1.35,
    "ozone": 32.1,
    "advisory": "Breathing discomfort to most people on prolonged exposure."
  },
  "forecast_pm25_2h": 98.0,
  "forecast_aqi_2h": 221,
  "disclaimer": "Direct on-site measurements from Connaught Place Transit Node."
}
```

---

### 10. Landmark Geocoding & Search
`GET /api/geocode?q=Connaught%20Place`
- **Parameters**: `q` (string, place name or sector)
- **Response**: `200 OK`
```json
[
  {
    "name": "Connaught Place",
    "display_name": "Connaught Place (CP), Rajiv Chowk, New Delhi",
    "latitude": 28.6315,
    "longitude": 77.2167,
    "type": "Commercial / Central Delhi"
  }
]
```
