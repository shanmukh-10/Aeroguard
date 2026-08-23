"""
AeroGuard Likely Pollution-Source Pattern Analysis Engine
----------------------------------------------------------
Analyzes multi-pollutant stoichiometric ratios (PM2.5/PM10, NO2/SO2, CO),
diurnal traffic timing, and meteorological transport vectors to infer likely
pollution source patterns with calculated confidence scores.

IMPORTANT:
Does not attribute emissions to any specific firm or person.
"""

from typing import Dict, Any, List


def analyze_source_pattern(
    pm25: float,
    pm10: float,
    no2: float,
    so2: float,
    co: float,
    ozone: float,
    ws: float = 2.0,
    wd: float = 180.0,
    hour: int = 12
) -> Dict[str, Any]:
    """
    Evaluates stoichiometric ratios and atmospheric context to determine the likely pollution pattern.
    """
    pm25 = max(0.1, pm25 or 50.0)
    pm10 = max(0.1, pm10 or 100.0)
    no2 = max(0.1, no2 or 30.0)
    so2 = max(0.1, so2 or 10.0)
    co = max(0.01, co or 1.0)
    ozone = max(0.1, ozone or 25.0)

    pm_ratio = pm25 / pm10
    no2_so2_ratio = no2 / so2
    is_rush_hour = (7 <= hour <= 10) or (17 <= hour <= 21)

    factors: List[str] = []
    indicators: Dict[str, Any] = {
        "pm25_to_pm10_ratio": round(pm_ratio, 3),
        "no2_to_so2_ratio": round(no2_so2_ratio, 3),
        "co_level_mg_m3": round(co, 2),
        "is_peak_transit_hour": is_rush_hour
    }

    # Heuristic pattern classification
    if no2_so2_ratio >= 2.5 and co >= 1.5 and pm_ratio >= 0.55:
        pattern = "Likely Traffic-Associated Pattern"
        confidence = 0.88 if is_rush_hour else 0.78
        factors.append("Elevated NO2/SO2 ratio indicative of internal combustion exhaust")
        factors.append("Elevated CO signature consistent with vehicular idling and urban transit")
        if is_rush_hour:
            factors.append("Coincides with peak diurnal urban traffic hours")

    elif so2 >= 30.0 or (no2_so2_ratio < 1.2 and so2 >= 15.0):
        pattern = "Likely Industrial Combustion & Point-Source Pattern"
        confidence = 0.84
        factors.append("Elevated SO2 concentration characteristic of industrial fuel/coal combustion")
        factors.append("Low NO2/SO2 ratio indicating stationary point source emissions")
        if ws < 2.0:
            factors.append("Low boundary-layer wind speed trapping localized industrial plume")

    elif pm_ratio <= 0.45 and pm10 >= 200.0:
        pattern = "Likely Construction / Road Dust Resuspension Pattern"
        confidence = 0.86
        factors.append("Low PM2.5/PM10 ratio indicating heavy dominance of coarse mechanical particles")
        factors.append("High PM10 coarse fraction typical of unpaved road dust or construction activity")

    else:
        pattern = "Likely Regional Background & Secondary Aerosol Pattern"
        confidence = 0.74
        factors.append("Balanced multi-pollutant distribution consistent with regional background aerosol")
        factors.append("Atmospheric dispersion and photochemical secondary formation")

    meteo_context = {
        "wind_speed_ms": round(ws, 1),
        "wind_direction_deg": round(wd, 0),
        "dispersion_state": "Poor Ventilation (Accumulation)" if ws < 1.8 else "Moderate Dispersion"
    }

    return {
        "likely_source_pattern": pattern,
        "confidence_score": round(confidence, 2),
        "dominant_factors": factors,
        "supporting_indicators": indicators,
        "meteorological_context": meteo_context,
        "disclaimer": "Likely pollution-source pattern analysis based on stoichiometric ratios and meteorological context. Not a definitive regulatory attribution."
    }
