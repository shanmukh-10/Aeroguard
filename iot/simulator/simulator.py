"""
AeroGuard IoT Multi-Sensor Network Simulator
--------------------------------------------
Simulates distributed hyperlocal IoT air-quality sensing nodes streaming
real-time telemetry packets to the AeroGuard backend ingestion endpoint
(POST /api/sensors/data) using standard JSON payloads.

Usage:
  python -m iot.simulator.simulator --interval 5 --cycles 10
  python -m iot.simulator.simulator --inject-spike
"""

import time
import math
import random
import argparse
import httpx
from datetime import datetime


SIMULATED_NODES = [
    {
        "sensor_id": "ESP32-AERO-01",
        "location": "Shahbad Daulatpur, Rohini Sec 16",
        "latitude": 28.749500,
        "longitude": 77.118000,
        "base_pm25": 85.0,
        "base_pm10": 145.0,
        "base_no2": 42.0,
        "base_so2": 12.0,
        "base_co": 1.20,
        "base_temp": 27.5,
        "base_humidity": 56.0
    },
    {
        "sensor_id": "ESP32-AERO-02",
        "location": "Mukarba Chowk Intersection Node",
        "latitude": 28.736000,
        "longitude": 77.148000,
        "base_pm25": 115.0,
        "base_pm10": 210.0,
        "base_no2": 68.0,
        "base_so2": 16.0,
        "base_co": 2.10,
        "base_temp": 28.0,
        "base_humidity": 52.0
    },
    {
        "sensor_id": "ESP32-AERO-03",
        "location": "Pitampura Residential Node",
        "latitude": 28.698000,
        "longitude": 77.138000,
        "base_pm25": 65.0,
        "base_pm10": 110.0,
        "base_no2": 32.0,
        "base_so2": 9.0,
        "base_co": 0.85,
        "base_temp": 26.8,
        "base_humidity": 60.0
    },
    {
        "sensor_id": "ESP32-AERO-04",
        "location": "Bawana Industrial Perimeter Node",
        "latitude": 28.781000,
        "longitude": 77.042000,
        "base_pm25": 165.0,
        "base_pm10": 290.0,
        "base_no2": 58.0,
        "base_so2": 38.0,
        "base_co": 1.95,
        "base_temp": 29.2,
        "base_humidity": 48.0
    },
    {
        "sensor_id": "ESP32-AERO-05",
        "location": "Connaught Place Urban Node",
        "latitude": 28.631500,
        "longitude": 77.216700,
        "base_pm25": 92.0,
        "base_pm10": 160.0,
        "base_no2": 54.0,
        "base_so2": 14.0,
        "base_co": 1.65,
        "base_temp": 28.5,
        "base_humidity": 54.0
    }
]


def generate_sensor_payload(node: dict, inject_spike: bool = False) -> dict:
    """Generates a physically consistent sensor observation payload."""
    hour = datetime.utcnow().hour
    # Diurnal cycle factor (morning/evening rush peaks)
    diurnal = 1.0 + 0.25 * math.sin(2 * math.pi * (hour - 6) / 24.0)
    noise = random.uniform(0.92, 1.08)

    pm25 = max(5.0, node["base_pm25"] * diurnal * noise)
    pm10 = max(pm25 * 1.3, node["base_pm10"] * diurnal * noise)
    no2 = max(5.0, node["base_no2"] * diurnal * random.uniform(0.95, 1.05))
    so2 = max(2.0, node["base_so2"] * random.uniform(0.9, 1.1))
    co = max(0.2, node["base_co"] * diurnal * random.uniform(0.95, 1.05))
    ozone = max(5.0, 35.0 * (1.0 - 0.3 * math.sin(2 * math.pi * hour / 24.0)))

    if inject_spike and node["sensor_id"] == "ESP32-AERO-02":
        print(f"[Simulator] Injecting deliberate severe pollution surge on {node['sensor_id']}...")
        pm25 += 140.0
        pm10 += 220.0
        no2 += 45.0

    payload = {
        "sensor_id": node["sensor_id"],
        "timestamp": datetime.utcnow().isoformat(),
        "location": node["location"],
        "latitude": node["latitude"],
        "longitude": node["longitude"],
        "pm25": round(pm25, 1),
        "pm10": round(pm10, 1),
        "no2": round(no2, 1),
        "so2": round(so2, 1),
        "co": round(co, 2),
        "ozone": round(ozone, 1),
        "temperature": round(node["base_temp"] + random.uniform(-0.8, 0.8), 1),
        "humidity": round(node["base_humidity"] + random.uniform(-2.0, 2.0), 1),
        "wind_speed": round(random.uniform(1.2, 3.8), 1),
        "wind_direction": round(random.uniform(160, 220), 0),
        "battery_level": round(random.uniform(92.0, 99.5), 1)
    }
    return payload


def run_simulation(
    target_url: str = "http://localhost:8000/api/sensors/data",
    interval: float = 3.0,
    cycles: int = 5,
    inject_spike: bool = False
):
    """Streams simulated packets to backend."""
    print("=" * 65)
    print("AEROGUARD IOT NETWORK SIMULATOR")
    print(f"Target Ingestion URL: {target_url}")
    print(f"Active Nodes: {len(SIMULATED_NODES)}")
    print(f"Cycles: {'Infinite' if cycles <= 0 else cycles} | Interval: {interval}s")
    print("=" * 65)

    cycle_count = 0
    try:
        while True:
            cycle_count += 1
            print(f"\n--- Simulation Cycle #{cycle_count} ({datetime.now().strftime('%H:%M:%S')}) ---")
            
            for node in SIMULATED_NODES:
                payload = generate_sensor_payload(node, inject_spike=(inject_spike and cycle_count == 2))
                try:
                    resp = httpx.post(target_url, json=payload, timeout=5)
                    if resp.status_code == 201:
                        data = resp.json()
                        alert_flag = " [ALERT TRIGGERED]" if data.get("alert_triggered") else ""
                        print(f"[{payload['sensor_id']}] -> PM2.5: {payload['pm25']:>5.1f} µg/m³ | AQI: {data.get('calculated_aqi'):>3} ({data.get('category')}){alert_flag}")
                    else:
                        print(f"[{payload['sensor_id']}] -> Ingestion failed (HTTP {resp.status_code}): {resp.text}")
                except Exception as e:
                    print(f"[{payload['sensor_id']}] -> Connection error: {e}")

            if 0 < cycles <= cycle_count:
                print(f"\nCompleted {cycle_count} simulation cycles.")
                break

            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AeroGuard IoT Multi-Node Simulator")
    parser.add_argument("--url", default="http://localhost:8000/api/sensors/data", help="Backend ingestion URL")
    parser.add_argument("--interval", type=float, default=4.0, help="Interval in seconds between cycles")
    parser.add_argument("--cycles", type=int, default=3, help="Number of cycles (0 for infinite)")
    parser.add_argument("--inject-spike", action="store_true", help="Inject artificial high pollution spike")
    args = parser.parse_args()

    run_simulation(
        target_url=args.url,
        interval=args.interval,
        cycles=args.cycles,
        inject_spike=args.inject_spike
    )
