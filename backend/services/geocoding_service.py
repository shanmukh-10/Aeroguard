"""
AeroGuard Geocoding & Landmark Search Service
---------------------------------------------
Provides fast, resilient geocoding for all Indian cities, districts, localities,
and landmarks with instant in-memory matching and OpenStreetMap Nominatim fallback.
Includes reverse-geocoding for coordinate clicks.
"""

import re
import math
import httpx
from typing import List, Dict, Any, Optional

# Comprehensive All-India and Delhi NCR Gazetteer
INDIAN_GAZETTEER = [
    # --- Major National Metros & State Capitals ---
    {"name": "Hyderabad", "display_name": "Hyderabad, Telangana, India", "lat": 17.385044, "lon": 78.486671, "type": "Metropolitan Capital / IT Hub"},
    {"name": "Bengaluru (Bangalore)", "display_name": "Bengaluru (Bangalore), Karnataka, India", "lat": 12.971599, "lon": 77.594566, "type": "Metropolitan Capital / Tech Capital"},
    {"name": "Mumbai", "display_name": "Mumbai, Maharashtra, India", "lat": 19.076090, "lon": 72.877426, "type": "Financial Capital / Coastal Metro"},
    {"name": "Chennai", "display_name": "Chennai, Tamil Nadu, India", "lat": 13.082680, "lon": 80.270721, "type": "Metropolitan Capital / Southern Metro"},
    {"name": "Kolkata", "display_name": "Kolkata, West Bengal, India", "lat": 22.572645, "lon": 88.363892, "type": "Metropolitan Capital / Eastern Metro"},
    {"name": "Pune", "display_name": "Pune, Maharashtra, India", "lat": 18.520430, "lon": 73.856743, "type": "Urban City / IT & Industrial Hub"},
    {"name": "Ahmedabad", "display_name": "Ahmedabad, Gujarat, India", "lat": 23.022505, "lon": 72.571365, "type": "Major Commercial City"},
    {"name": "Jaipur", "display_name": "Jaipur, Rajasthan, India", "lat": 26.912434, "lon": 75.787270, "type": "State Capital / Historic City"},
    {"name": "Lucknow", "display_name": "Lucknow, Uttar Pradesh, India", "lat": 26.846708, "lon": 80.946159, "type": "State Capital / Northern Urban"},
    {"name": "Chandigarh", "display_name": "Chandigarh, Union Territory, India", "lat": 30.733315, "lon": 76.779419, "type": "Union Territory Capital"},
    {"name": "Visakhapatnam (Vizag)", "display_name": "Visakhapatnam, Andhra Pradesh, India", "lat": 17.686816, "lon": 83.218483, "type": "Coastal City / Port"},
    {"name": "Kochi (Cochin)", "display_name": "Kochi, Kerala, India", "lat": 9.931233, "lon": 76.267303, "type": "Commercial Port City"},
    {"name": "Indore", "display_name": "Indore, Madhya Pradesh, India", "lat": 22.719568, "lon": 75.857727, "type": "Commercial & Clean City Hub"},
    {"name": "Bhopal", "display_name": "Bhopal, Madhya Pradesh, India", "lat": 23.259933, "lon": 77.412613, "type": "State Capital"},
    {"name": "Patna", "display_name": "Patna, Bihar, India", "lat": 25.594095, "lon": 85.137566, "type": "State Capital"},
    {"name": "Surat", "display_name": "Surat, Gujarat, India", "lat": 21.170240, "lon": 72.831062, "type": "Commercial Hub"},
    {"name": "Nagpur", "display_name": "Nagpur, Maharashtra, India", "lat": 21.145800, "lon": 79.088158, "type": "Central Urban City"},
    {"name": "Coimbatore", "display_name": "Coimbatore, Tamil Nadu, India", "lat": 11.016844, "lon": 76.955833, "type": "Industrial & Tech Hub"},
    {"name": "Varanasi", "display_name": "Varanasi, Uttar Pradesh, India", "lat": 25.317645, "lon": 82.973915, "type": "Cultural Heritage City"},
    {"name": "Kanpur", "display_name": "Kanpur, Uttar Pradesh, India", "lat": 26.449923, "lon": 80.331871, "type": "Industrial City"},
    {"name": "Agra", "display_name": "Agra, Uttar Pradesh, India", "lat": 27.176670, "lon": 78.008072, "type": "Heritage City"},
    {"name": "Dehradun", "display_name": "Dehradun, Uttarakhand, India", "lat": 30.316496, "lon": 78.032188, "type": "State Capital"},
    {"name": "Shimla", "display_name": "Shimla, Himachal Pradesh, India", "lat": 31.104830, "lon": 77.173401, "type": "State Capital"},
    {"name": "Amritsar", "display_name": "Amritsar, Punjab, India", "lat": 31.633980, "lon": 74.872261, "type": "Historic City"},
    {"name": "Bhubaneswar", "display_name": "Bhubaneswar, Odisha, India", "lat": 20.296059, "lon": 85.824539, "type": "State Capital"},
    {"name": "Thiruvananthapuram", "display_name": "Thiruvananthapuram, Kerala, India", "lat": 8.524139, "lon": 76.936638, "type": "State Capital"},
    {"name": "Guwahati", "display_name": "Guwahati, Assam, India", "lat": 26.144518, "lon": 91.736237, "type": "Northeastern Hub"},
    {"name": "Srinagar", "display_name": "Srinagar, Jammu and Kashmir, India", "lat": 34.083656, "lon": 74.797287, "type": "Summer Capital"},

    # --- Delhi NCR Hyperlocal Core & Stations ---
    {"name": "Delhi Technological University (DTU)", "display_name": "DTU, Shahbad Daulatpur, Bawana Road, North Delhi, Delhi", "lat": 28.750075, "lon": 77.111261, "type": "Academic / CAAQMS Reference Station"},
    {"name": "Connaught Place", "display_name": "Connaught Place (CP), Rajiv Chowk, Central Delhi, Delhi", "lat": 28.6315, "lon": 77.2167, "type": "Commercial / Central Delhi"},
    {"name": "Anand Vihar", "display_name": "Anand Vihar ISBT, East Delhi, Delhi", "lat": 28.6469, "lon": 77.3160, "type": "Transit Hub / CAAQMS Reference Station"},
    {"name": "Punjabi Bagh", "display_name": "Punjabi Bagh West, West Delhi, Delhi", "lat": 28.6683, "lon": 77.1264, "type": "Residential / CAAQMS Reference Station"},
    {"name": "R K Puram", "display_name": "R K Puram Sector 1, South West Delhi, Delhi", "lat": 28.5630, "lon": 77.1860, "type": "Residential / CAAQMS Reference Station"},
    {"name": "Mandir Marg", "display_name": "Mandir Marg, Gole Market, New Delhi", "lat": 28.6340, "lon": 77.2000, "type": "Institutional / CAAQMS Reference Station"},
    {"name": "Bawana Industrial Area", "display_name": "Bawana Industrial Area, North West Delhi, Delhi", "lat": 28.7950, "lon": 77.0500, "type": "Industrial Hotspot"},
    {"name": "Rohini Sector 16", "display_name": "Rohini Sector 16, North West Delhi, Delhi", "lat": 28.7350, "lon": 77.1200, "type": "Residential"},
    {"name": "Rohini Sector 22", "display_name": "Rohini Sector 22, North West Delhi, Delhi", "lat": 28.7180, "lon": 77.0880, "type": "Residential"},
    {"name": "Pitampura", "display_name": "Pitampura TV Tower, North West Delhi, Delhi", "lat": 28.6989, "lon": 77.1408, "type": "Commercial"},
    {"name": "Netaji Subhash Place (NSP)", "display_name": "Netaji Subhash Place, Pitampura, Delhi", "lat": 28.6917, "lon": 77.1517, "type": "Commercial Hub"},
    {"name": "Karol Bagh", "display_name": "Karol Bagh Market, Central Delhi, Delhi", "lat": 28.6514, "lon": 77.1907, "type": "Commercial"},
    {"name": "Chandni Chowk", "display_name": "Chandni Chowk, Old Delhi, Delhi", "lat": 28.6560, "lon": 77.2300, "type": "Heritage / Dense Urban"},
    {"name": "India Gate", "display_name": "India Gate, Rajpath, New Delhi", "lat": 28.6129, "lon": 77.2295, "type": "National Landmark"},
    {"name": "Hauz Khas", "display_name": "Hauz Khas Village & IIT Delhi, South Delhi", "lat": 28.5494, "lon": 77.2001, "type": "Urban / Academic"},
    {"name": "Dwarka Sector 10", "display_name": "Dwarka Sector 10, South West Delhi, Delhi", "lat": 28.5823, "lon": 77.0500, "type": "Sub-City / Transit"},
    {"name": "Saket", "display_name": "Saket District Centre, South Delhi, Delhi", "lat": 28.5244, "lon": 77.2183, "type": "Commercial"},
    {"name": "Janakpuri", "display_name": "Janakpuri District Centre, West Delhi, Delhi", "lat": 28.6219, "lon": 77.0878, "type": "Residential / Commercial"},
    {"name": "Lajpat Nagar", "display_name": "Lajpat Nagar Central Market, South East Delhi", "lat": 28.5677, "lon": 77.2433, "type": "Commercial"},
    {"name": "Mayur Vihar Phase 1", "display_name": "Mayur Vihar Phase 1, East Delhi, Delhi", "lat": 28.6080, "lon": 77.2970, "type": "Residential"},
    {"name": "Okhla Phase 3", "display_name": "Okhla Industrial Area Phase 3, South Delhi", "lat": 28.5300, "lon": 77.2700, "type": "Industrial Hotspot"},
    {"name": "Noida Sector 18", "display_name": "Noida Sector 18 (Atta Market), Gautam Buddha Nagar, UP", "lat": 28.5700, "lon": 77.3200, "type": "Commercial NCR"},
    {"name": "Noida Sector 62", "display_name": "Noida Sector 62 IT Hub, Gautam Buddha Nagar, UP", "lat": 28.6280, "lon": 77.3640, "type": "Institutional NCR"},
    {"name": "Cyber Hub Gurgaon", "display_name": "DLF Cyber City / Cyber Hub, Gurugram, Haryana", "lat": 28.4950, "lon": 77.0890, "type": "Corporate NCR"},
    {"name": "Indirapuram Ghaziabad", "display_name": "Indirapuram, Ghaziabad, Uttar Pradesh", "lat": 28.6410, "lon": 77.3730, "type": "Residential NCR"},
    {"name": "Mukarba Chowk", "display_name": "Mukarba Chowk, GT Karnal Road, North Delhi", "lat": 28.7370, "lon": 77.1580, "type": "High Traffic Corridor"},
    {"name": "Jahangirpuri", "display_name": "Jahangirpuri, North Delhi, Delhi", "lat": 28.7260, "lon": 77.1650, "type": "High Density Urban"}
]


def search_local_gazetteer(query: str) -> List[Dict[str, Any]]:
    """Searches the in-memory all-India gazetteer with token matching."""
    q_tokens = re.split(r'[\s,.-]+', query.lower().strip())
    q_tokens = [t for t in q_tokens if len(t) > 1 and t not in ["near", "in", "at", "the"]]
    
    if not q_tokens:
        return [
            {"name": item["name"], "display_name": item["display_name"], "latitude": item["lat"], "longitude": item["lon"], "type": item["type"]}
            for item in INDIAN_GAZETTEER[:6]
        ]

    matches = []
    for item in INDIAN_GAZETTEER:
        searchable_text = f"{item['name']} {item['display_name']} {item['type']}".lower()
        score = 0
        for token in q_tokens:
            if token in searchable_text:
                score += 2 if token in item["name"].lower() else 1
        if score > 0:
            matches.append((score, {
                "name": item["name"],
                "display_name": item["display_name"],
                "latitude": item["lat"],
                "longitude": item["lon"],
                "type": item["type"]
            }))

    matches.sort(key=lambda x: x[0], reverse=True)
    return [m[1] for m in matches[:8]]


async def geocode_location(query: str) -> List[Dict[str, Any]]:
    """
    Geocodes any Indian location query.
    1. Checks local fast gazetteer.
    2. Queries OpenStreetMap Nominatim for all Indian cities, districts, localities, and landmarks.
    """
    clean_q = query.strip()
    if not clean_q:
        return []

    local_results = search_local_gazetteer(clean_q)
    
    # If high-confidence local match exists, return immediately for sub-millisecond response
    if len(local_results) >= 1 and any(clean_q.lower() in r["name"].lower() for r in local_results):
        # Still fetch external if needed, but local is priority
        pass

    # Query OpenStreetMap Nominatim for general Indian locations
    try:
        url = "https://nominatim.openstreetmap.org/search"
        # Search query across India
        params = {
            "q": clean_q if "india" in clean_q.lower() else f"{clean_q}, India",
            "format": "json",
            "countrycodes": "in",
            "limit": 6,
            "addressdetails": 1
        }
        headers = {
            "User-Agent": "AeroGuard-Environmental-Intelligence/2.0 (aeroguard-aiot@gmail.com)"
        }
        async with httpx.AsyncClient(timeout=3.5) as client:
            resp = await client.get(url, params=params, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                external_results = []
                for item in data:
                    lat = float(item["lat"])
                    lon = float(item["lon"])
                    display_name = item.get("display_name", clean_q)
                    name = item.get("name") or display_name.split(",")[0]
                    external_results.append({
                        "name": name,
                        "display_name": display_name,
                        "latitude": lat,
                        "longitude": lon,
                        "type": item.get("type", "location")
                    })
                
                if external_results:
                    # Merge local + external (avoid duplicates by approx coordinates)
                    merged = []
                    seen_coords = set()
                    for r in local_results + external_results:
                        key = (round(r["latitude"], 2), round(r["longitude"], 2))
                        if key not in seen_coords:
                            seen_coords.add(key)
                            merged.append(r)
                    return merged[:8]
    except Exception:
        pass

    return local_results


async def reverse_geocode_location(lat: float, lon: float) -> str:
    """
    Reverse geocodes coordinates to a human-readable location name.
    """
    # Check if close to known landmark
    for item in INDIAN_GAZETTEER:
        d_lat = abs(item["lat"] - lat)
        d_lon = abs(item["lon"] - lon)
        if d_lat < 0.02 and d_lon < 0.02:
            return item["display_name"].split(",")[0]

    # Query Nominatim reverse geocode
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": 14,
            "addressdetails": 1
        }
        headers = {
            "User-Agent": "AeroGuard-Environmental-Intelligence/2.0 (aeroguard-aiot@gmail.com)"
        }
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url, params=params, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                address = data.get("address", {})
                city = address.get("city") or address.get("town") or address.get("suburb") or address.get("neighbourhood")
                state = address.get("state")
                if city and state:
                    return f"{city}, {state}"
                return data.get("display_name", f"Location ({lat:.4f}, {lon:.4f})").split(",")[0]
    except Exception:
        pass

    return f"Location ({lat:.4f}, {lon:.4f})"
