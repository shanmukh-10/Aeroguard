"""
Unit Tests for AeroGuard Geospatial Calculations & Nearest Station Resolution
-----------------------------------------------------------------------------
Tests Haversine great-circle distance formulas, tier classification,
and local gazetteer resolution.
"""

import pytest
import math
from backend.services.nearest_station_service import haversine_distance
from backend.services.geocoding_service import search_local_gazetteer


def test_haversine_same_point():
    # Distance from a point to itself should be exactly 0.0
    dist = haversine_distance(28.750075, 77.111261, 28.750075, 77.111261)
    assert dist == 0.0


def test_haversine_known_delhi_distance():
    # DTU (28.750075, 77.111261) to Anand Vihar (28.6469, 77.3160)
    # Expected approximate distance is ~23 to 24 km
    dist = haversine_distance(28.750075, 77.111261, 28.6469, 77.3160)
    assert 22.0 <= dist <= 25.0


def test_haversine_short_distance():
    # DTU Main Campus to Shahbad Daulatpur Village (~0.5 - 1.2 km)
    dist = haversine_distance(28.750075, 77.111261, 28.755000, 77.118000)
    assert 0.4 <= dist <= 1.5


def test_local_gazetteer_token_search():
    results = search_local_gazetteer("Connaught Place")
    assert len(results) > 0
    assert any("Connaught Place" in r["name"] for r in results)

    results_rohini = search_local_gazetteer("Rohini")
    assert len(results_rohini) > 0
    assert any("Rohini" in r["name"] for r in results_rohini)

    results_dtu = search_local_gazetteer("DTU")
    assert len(results_dtu) > 0
    assert any("DTU" in r["name"] for r in results_dtu)
