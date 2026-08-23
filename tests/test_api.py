"""
Integration Tests for AeroGuard FastAPI REST Endpoints
------------------------------------------------------
Validates health, current AQI, forecast, history, hotspots, alerts, sensors,
source pattern analysis, model metrics, nearest-station resolution,
all-India geocoding, and reverse-geocoding API routes.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "AeroGuard" in data["service"]


def test_current_aqi_endpoint():
    response = client.get("/api/current")
    assert response.status_code == 200
    data = response.json()
    assert "aqi" in data
    assert "category" in data
    assert "pm25" in data
    assert "sub_indices" in data


def test_forecast_endpoint():
    response = client.get("/api/forecast?hours=12")
    assert response.status_code == 200
    data = response.json()
    assert "forecast" in data
    assert "current_pm25" in data
    assert len(data["forecast"]) > 0


def test_history_endpoint():
    response = client.get("/api/history?timeframe=24h")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "record_count" in data


def test_hotspots_endpoint():
    response = client.get("/api/hotspots")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_alerts_endpoint():
    response = client.get("/api/alerts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_sensors_endpoint():
    response = client.get("/api/sensors")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_source_pattern_endpoint():
    response = client.get("/api/source-pattern")
    assert response.status_code == 200
    data = response.json()
    assert "likely_source_pattern" in data
    assert "confidence_score" in data
    assert "dominant_factors" in data


def test_model_metrics_endpoint():
    response = client.get("/api/model-metrics")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data


# ==================================================
# Nearest Station & Geocoding Integration Tests
# ==================================================

def test_nearest_station_known_coords():
    # Test near DTU coordinates (28.7500, 77.1112)
    response = client.get("/api/nearest-station?lat=28.750075&lon=77.111261")
    assert response.status_code == 200
    data = response.json()
    assert data["has_nearby_station"] is True
    assert data["nearest_station"] is not None
    assert data["distance_km"] <= 0.2
    assert data["coverage_type"] in ["DIRECT", "NEARBY"]
    assert "DTU" in data["nearest_station"]["name"]
    assert data["air_quality"] is not None
    assert "aqi" in data["air_quality"]


def test_nearest_station_connaught_place():
    # Test near Connaught Place (28.6315, 77.2167)
    response = client.get("/api/nearest-station?lat=28.6315&lon=77.2167&location_name=Connaught%20Place")
    assert response.status_code == 200
    data = response.json()
    assert data["has_nearby_station"] is True
    assert data["nearest_station"] is not None
    assert data["distance_km"] < 5.0
    assert data["coverage_type"] in ["DIRECT", "NEARBY"]
    assert "Connaught Place" in data["nearest_station"]["name"] or "Mandir Marg" in data["nearest_station"]["name"]


def test_nearest_station_hyderabad_no_sensor():
    # Hyderabad coordinates (17.3850, 78.4867) -> Should find no nearby AeroGuard station
    response = client.get("/api/nearest-station?lat=17.385044&lon=78.486671&max_radius_km=25.0&location_name=Hyderabad")
    assert response.status_code == 200
    data = response.json()
    assert data["has_nearby_station"] is False
    assert data["coverage_type"] == "OUT_OF_RANGE"
    assert data["air_quality"] is None
    assert data["distance_km"] > 1000.0  # >1200 km from Delhi stations
    assert "exceeding preferred" in data["disclaimer"]


def test_nearest_station_out_of_range():
    # Coordinates far from Delhi NCR (e.g. Mumbai: 19.0760, 72.8777)
    response = client.get("/api/nearest-station?lat=19.0760&lon=72.8777&max_radius_km=25.0")
    assert response.status_code == 200
    data = response.json()
    assert data["has_nearby_station"] is False
    assert data["coverage_type"] == "OUT_OF_RANGE"
    assert data["air_quality"] is None
    assert "exceeding preferred" in data["disclaimer"]


def test_nearest_station_invalid_coordinates():
    # Invalid latitude > 90
    response = client.get("/api/nearest-station?lat=95.0&lon=77.0")
    assert response.status_code == 422


def test_geocode_search_delhi_landmark():
    response = client.get("/api/geocode?q=Connaught%20Place")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any("Connaught Place" in item["name"] for item in data)
    assert 28.5 <= data[0]["latitude"] <= 28.8
    assert 77.0 <= data[0]["longitude"] <= 77.4


def test_geocode_search_hyderabad():
    response = client.get("/api/geocode?q=Hyderabad")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any("Hyderabad" in item["name"] for item in data)
    hyd = next(item for item in data if "Hyderabad" in item["name"])
    assert 17.2 <= hyd["latitude"] <= 17.6
    assert 78.2 <= hyd["longitude"] <= 78.7


def test_geocode_search_bengaluru():
    response = client.get("/api/geocode?q=Bengaluru")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any("Bengaluru" in item["name"] or "Bangalore" in item["name"] for item in data)
    blr = next(item for item in data if "Bengaluru" in item["name"] or "Bangalore" in item["name"])
    assert 12.8 <= blr["latitude"] <= 13.2
    assert 77.4 <= blr["longitude"] <= 77.8


def test_geocode_search_mumbai():
    response = client.get("/api/geocode?q=Mumbai")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any("Mumbai" in item["name"] for item in data)
    mum = next(item for item in data if "Mumbai" in item["name"])
    assert 18.8 <= mum["latitude"] <= 19.3
    assert 72.7 <= mum["longitude"] <= 73.1


def test_reverse_geocode_endpoint():
    response = client.get("/api/reverse-geocode?lat=28.6315&lon=77.2167")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "Connaught Place" in data["name"]
