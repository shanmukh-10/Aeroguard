"""
AeroGuard CPCB AQI Calculator
------------------------------
Implements the official Central Pollution Control Board (CPCB), Ministry of Environment,
Forest and Climate Change, Government of India National Air Quality Index (AQI) methodology.

Breakpoint Reference:
- Good: 0 - 50
- Satisfactory: 51 - 100
- Moderate: 101 - 200
- Poor: 201 - 300
- Very Poor: 301 - 400
- Severe: 401 - 500
"""

from typing import Dict, Optional, Tuple, Any, List
import math


# Official CPCB Breakpoints: (B_low, B_high, I_low, I_high)
CPCB_BREAKPOINTS = {
    "pm25": [  # 24-hr avg (µg/m³)
        (0.0, 30.0, 0, 50),
        (30.1, 60.0, 51, 100),
        (60.1, 90.0, 101, 200),
        (90.1, 120.0, 201, 300),
        (120.1, 250.0, 301, 400),
        (250.1, 500.0, 401, 500),
    ],
    "pm10": [  # 24-hr avg (µg/m³)
        (0.0, 50.0, 0, 50),
        (50.1, 100.0, 51, 100),
        (100.1, 250.0, 101, 200),
        (250.1, 350.0, 201, 300),
        (350.1, 430.0, 301, 400),
        (430.1, 600.0, 401, 500),
    ],
    "no2": [  # 24-hr avg (µg/m³)
        (0.0, 40.0, 0, 50),
        (40.1, 80.0, 51, 100),
        (80.1, 180.0, 101, 200),
        (180.1, 280.0, 201, 300),
        (280.1, 400.0, 301, 400),
        (400.1, 600.0, 401, 500),
    ],
    "nh3": [  # 24-hr avg (µg/m³)
        (0.0, 200.0, 0, 50),
        (200.1, 400.0, 51, 100),
        (401.0, 800.0, 101, 200),
        (801.0, 1200.0, 201, 300),
        (1201.0, 1800.0, 301, 400),
        (1801.0, 2500.0, 401, 500),
    ],
    "so2": [  # 24-hr avg (µg/m³)
        (0.0, 40.0, 0, 50),
        (40.1, 80.0, 51, 100),
        (80.1, 380.0, 101, 200),
        (381.0, 800.0, 201, 300),
        (801.0, 1600.0, 301, 400),
        (1601.0, 2000.0, 401, 500),
    ],
    "co": [  # 8-hr avg (mg/m³)
        (0.0, 1.0, 0, 50),
        (1.01, 2.0, 51, 100),
        (2.01, 10.0, 101, 200),
        (10.01, 17.0, 201, 300),
        (17.01, 34.0, 301, 400),
        (34.01, 50.0, 401, 500),
    ],
    "o3": [  # 8-hr avg (µg/m³)
        (0.0, 50.0, 0, 50),
        (50.1, 100.0, 51, 100),
        (100.1, 168.0, 101, 200),
        (168.1, 208.0, 201, 300),
        (208.1, 748.0, 301, 400),
        (748.1, 1000.0, 401, 500),
    ],
    "pb": [  # 24-hr avg (µg/m³)
        (0.0, 0.5, 0, 50),
        (0.51, 1.0, 51, 100),
        (1.01, 2.0, 101, 200),
        (2.01, 3.0, 201, 300),
        (3.01, 3.5, 301, 400),
        (3.51, 5.0, 401, 500),
    ]
}

AQI_CATEGORIES = [
    (0, 50, "Good", "#10B981", "Minimal health impact. Air quality is considered satisfactory."),
    (51, 100, "Satisfactory", "#84CC16", "Minor breathing discomfort to sensitive people."),
    (101, 200, "Moderate", "#EAB308", "Breathing discomfort to people with lungs, asthma and heart diseases."),
    (201, 300, "Poor", "#F97316", "Breathing discomfort to most people on prolonged exposure."),
    (301, 400, "Very Poor", "#EF4444", "Respiratory illness on prolonged exposure. Effect may be more pronounced in sensitive groups."),
    (401, 500, "Severe", "#881337", "Affects healthy people and seriously impacts those with existing diseases."),
    (501, 9999, "Severe+", "#4C0519", "Emergency conditions. Entire population is more likely to be affected.")
]


def calculate_sub_index(concentration: float, pollutant: str) -> Optional[float]:
    """
    Computes pollutant sub-index Ip using standard linear interpolation:
    Ip = ((I_high - I_low) / (B_high - B_low)) * (Cp - B_low) + I_low
    """
    if concentration is None or math.isnan(concentration) or concentration < 0:
        return None
    
    pollutant_key = pollutant.lower().replace(".", "").replace("-", "").replace(" ", "")
    if pollutant_key == "ozone":
        pollutant_key = "o3"
    elif pollutant_key in ["pm25", "pm2_5"]:
        pollutant_key = "pm25"
        
    breakpoints = CPCB_BREAKPOINTS.get(pollutant_key)
    if not breakpoints:
        return None

    # Handle concentrations beyond the highest defined breakpoint
    max_b_low, max_b_high, max_i_low, max_i_high = breakpoints[-1]
    if concentration > max_b_high:
        slope = (max_i_high - max_i_low) / (max_b_high - max_b_low)
        sub_idx = max_i_high + slope * (concentration - max_b_high)
        return round(sub_idx, 1)

    for b_low, b_high, i_low, i_high in breakpoints:
        if b_low <= concentration <= b_high:
            sub_idx = ((i_high - i_low) / (b_high - b_low)) * (concentration - b_low) + i_low
            return round(sub_idx, 1)

    return None


def get_aqi_category_info(aqi_value: float) -> Dict[str, Any]:
    """Returns category name, hex color, and general advisory for a given AQI."""
    if aqi_value is None or math.isnan(aqi_value) or aqi_value < 0:
        return {
            "category": "Unknown",
            "color": "#94A3B8",
            "advisory": "Insufficient monitoring data to compute reliable AQI.",
            "sensitive_advisory": "Maintain standard precautions."
        }

    for low, high, category, color, advisory in AQI_CATEGORIES:
        if low <= round(aqi_value) <= high:
            sensitive_advisory = _get_sensitive_advisory(category)
            return {
                "category": category,
                "color": color,
                "advisory": advisory,
                "sensitive_advisory": sensitive_advisory
            }

    return {
        "category": "Severe+",
        "color": "#4C0519",
        "advisory": "Emergency health conditions. Entire population is severely impacted.",
        "sensitive_advisory": "Avoid all outdoor activity. Use certified air purifiers indoors."
    }


def _get_sensitive_advisory(category: str) -> str:
    advisories = {
        "Good": "Normal outdoor physical activity is safe for everyone.",
        "Satisfactory": "Sensitive individuals (children, elderly, asthmatics) can engage in outdoor activities as usual.",
        "Moderate": "People with lung diseases, older adults, and children should consider reducing prolonged heavy outdoor exertion.",
        "Poor": "People with respiratory or cardiovascular diseases should reduce strenuous outdoor activities; use masks if outdoors.",
        "Very Poor": "Children, elderly, and individuals with respiratory/heart conditions should avoid outdoor exertion. Consider N95 masks.",
        "Severe": "All individuals must avoid outdoor exertion. High-risk groups should remain indoors with windows closed and air purifiers active.",
        "Severe+": "Complete restriction of outdoor physical activities. Emergency protocol for vulnerable individuals."
    }
    return advisories.get(category, "Take necessary preventive health measures.")


def calculate_overall_aqi(pollutant_data: Dict[str, float], enforce_cpcb_rule: bool = True) -> Dict[str, Any]:
    """
    Calculates overall AQI following CPCB rules:
    - Minimum 3 pollutants required with at least one PM2.5 or PM10 (if enforce_cpcb_rule=True).
    - Overall AQI = max(sub-indices).
    - Returns overall AQI, dominant pollutant, sub-indices breakdown, category, and health advisories.
    """
    sub_indices: Dict[str, float] = {}
    
    for pol, val in pollutant_data.items():
        if val is not None and not math.isnan(val) and val >= 0:
            sub = calculate_sub_index(val, pol)
            if sub is not None:
                sub_indices[pol] = sub

    if not sub_indices:
        return {
            "aqi": None,
            "category": "Unknown",
            "dominant_pollutant": None,
            "sub_indices": {},
            "valid_cpcb": False,
            "color": "#94A3B8",
            "advisory": "No valid pollutant measurements provided.",
            "sensitive_advisory": "N/A"
        }

    has_pm = any(k.lower() in ["pm25", "pm2.5", "pm10"] for k in sub_indices.keys())
    has_min_pollutants = len(sub_indices) >= 3

    valid_cpcb = (has_pm and has_min_pollutants) if enforce_cpcb_rule else True

    # Find dominant pollutant (maximum sub-index)
    dominant_pollutant = max(sub_indices, key=sub_indices.get)
    overall_aqi = sub_indices[dominant_pollutant]

    cat_info = get_aqi_category_info(overall_aqi)

    return {
        "aqi": round(overall_aqi),
        "category": cat_info["category"],
        "dominant_pollutant": dominant_pollutant,
        "sub_indices": sub_indices,
        "valid_cpcb": valid_cpcb,
        "color": cat_info["color"],
        "advisory": cat_info["advisory"],
        "sensitive_advisory": cat_info["sensitive_advisory"],
    }
