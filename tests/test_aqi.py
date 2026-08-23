"""
Unit Tests for CPCB AQI Calculation Engine
------------------------------------------
Validates official Indian Central Pollution Control Board (CPCB)
sub-index linear interpolation, breakpoints, and overall AQI rules.
"""

import pytest
from ml.aqi_calculator import calculate_sub_index, calculate_overall_aqi, get_aqi_category_info


def test_pm25_sub_index_breakpoints():
    # Good (0 - 30 µg/m³ -> 0 - 50)
    assert calculate_sub_index(0.0, "pm25") == 0.0
    assert calculate_sub_index(15.0, "pm25") == 25.0
    assert calculate_sub_index(30.0, "pm25") == 50.0

    # Satisfactory (30.1 - 60.0 µg/m³ -> 51 - 100)
    sub_60 = calculate_sub_index(60.0, "pm25")
    assert sub_60 == 100.0

    # Moderate (60.1 - 90.0 µg/m³ -> 101 - 200)
    sub_75 = calculate_sub_index(75.0, "pm25")
    assert 140.0 <= sub_75 <= 160.0

    # Poor (90.1 - 120.0 µg/m³ -> 201 - 300)
    sub_120 = calculate_sub_index(120.0, "pm25")
    assert sub_120 == 300.0

    # Very Poor (120.1 - 250.0 µg/m³ -> 301 - 400)
    sub_250 = calculate_sub_index(250.0, "pm25")
    assert sub_250 == 400.0

    # Severe (250.1 - 500.0 µg/m³ -> 401 - 500)
    sub_500 = calculate_sub_index(500.0, "pm25")
    assert sub_500 == 500.0


def test_pm10_sub_index_breakpoints():
    # Good (0 - 50 -> 0 - 50)
    assert calculate_sub_index(50.0, "pm10") == 50.0
    # Satisfactory (51 - 100 -> 51 - 100)
    assert calculate_sub_index(100.0, "pm10") == 100.0
    # Moderate (101 - 250 -> 101 - 200)
    assert calculate_sub_index(250.0, "pm10") == 200.0


def test_invalid_and_edge_inputs():
    assert calculate_sub_index(None, "pm25") is None
    assert calculate_sub_index(-10.0, "pm25") is None
    assert calculate_sub_index(float('nan'), "pm25") is None
    assert calculate_sub_index(50.0, "unknown_pollutant") is None


def test_overall_aqi_calculation():
    data = {
        "pm25": 110.0,  # sub-index ~ 267 (Poor)
        "pm10": 80.0,   # sub-index ~ 80 (Satisfactory)
        "no2": 35.0,    # sub-index ~ 44 (Good)
        "so2": 15.0,    # sub-index ~ 19 (Good)
        "co": 1.1,      # sub-index ~ 56 (Satisfactory)
    }
    result = calculate_overall_aqi(data)
    assert result["aqi"] is not None
    assert result["aqi"] >= 201 and result["aqi"] <= 300
    assert result["category"] == "Poor"
    assert result["dominant_pollutant"] == "pm25"
    assert result["valid_cpcb"] is True


def test_category_info():
    info_good = get_aqi_category_info(45)
    assert info_good["category"] == "Good"
    assert info_good["color"] == "#10B981"

    info_severe = get_aqi_category_info(440)
    assert info_severe["category"] == "Severe"
