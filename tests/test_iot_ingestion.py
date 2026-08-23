"""
Integration Tests for IoT Sensor Ingestion & Validation
-------------------------------------------------------
Tests POST /api/sensors/data ingestion payload validation,
rejection of out-of-range inputs, and alert triggering.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_sensor_ingestion_valid():
    payload = {
        "sensor_id": "TEST-NODE-01",
        "location": "DTU Innovation Lab Test Node",
        "latitude": 28.7495,
        "longitude": 77.1180,
        "pm25": 84.5,
        "pm10": 142.0,
        "no2": 45.0,
        "so2": 12.0,
        "co": 1.2,
        "ozone": 28.0,
        "temperature": 27.5,
        "humidity": 55.0,
        "wind_speed": 2.1,
        "wind_direction": 180.0,
        "battery_level": 98.0
    }
    response = client.post("/api/sensors/data", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["sensor_id"] == "TEST-NODE-01"
    assert data["calculated_aqi"] is not None


def test_sensor_ingestion_invalid_negative_pm25():
    payload = {
        "sensor_id": "TEST-NODE-02",
        "pm25": -15.0
    }
    response = client.post("/api/sensors/data", json=payload)
    assert response.status_code == 422  # Pydantic validation error ge=0


def test_sensor_ingestion_spike_triggers_alert():
    # Ingest emergency spike (PM2.5 = 320 µg/m³)
    payload = {
        "sensor_id": "TEST-NODE-SPIKE",
        "location": "Bawana Industrial Perimeter",
        "latitude": 28.7810,
        "longitude": 77.0420,
        "pm25": 320.0,
        "pm10": 480.0,
        "no2": 85.0
    }
    response = client.post("/api/sensors/data", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["calculated_aqi"] >= 400
    assert data["category"] in ["Severe", "Severe+"]
    assert data["alert_triggered"] is True
