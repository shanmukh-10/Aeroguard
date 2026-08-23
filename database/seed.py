"""
AeroGuard Database Seeder
-------------------------
Populates PostgreSQL / SQLite database with:
1. Official CPCB / DPCC CAAQMS monitoring stations across Delhi NCR.
2. Hyperlocal IoT sensor nodes.
3. Cleaned historical & real-time air quality observations.
4. Active pollution hotspots with source attribution.
5. Automated alerts.
6. Model benchmark metrics.
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from database.connection import init_db, SessionLocal
from database.models import Station, Sensor, AirQualityRecord, Hotspot, Alert, ModelMetric, Prediction
from ml.aqi_calculator import calculate_overall_aqi, get_aqi_category_info


STATIONS = [
    {
        "id": "site_118",
        "name": "DTU, Delhi - CPCB",
        "city": "Delhi",
        "state": "Delhi",
        "latitude": 28.750075,
        "longitude": 77.111261,
        "station_type": "Continuous Ambient Air Quality Monitoring Station (CAAQMS)"
    },
    {
        "id": "site_142",
        "name": "Anand Vihar, Delhi - DPCC",
        "city": "Delhi",
        "state": "Delhi",
        "latitude": 28.647260,
        "longitude": 77.316040,
        "station_type": "CAAQMS"
    },
    {
        "id": "site_256",
        "name": "Punjabi Bagh, Delhi - DPCC",
        "city": "Delhi",
        "state": "Delhi",
        "latitude": 28.674045,
        "longitude": 77.131023,
        "station_type": "CAAQMS"
    },
    {
        "id": "site_301",
        "name": "R K Puram, Delhi - DPCC",
        "city": "Delhi",
        "state": "Delhi",
        "latitude": 28.563262,
        "longitude": 77.186937,
        "station_type": "CAAQMS"
    },
    {
        "id": "site_103",
        "name": "Mandir Marg, Delhi - DPCC",
        "city": "Delhi",
        "state": "Delhi",
        "latitude": 28.636429,
        "longitude": 77.201067,
        "station_type": "CAAQMS"
    },
    {
        "id": "site_502",
        "name": "Bawana Industrial Area - DPCC",
        "city": "Delhi",
        "state": "Delhi",
        "latitude": 28.776200,
        "longitude": 77.051070,
        "station_type": "CAAQMS"
    }
]

SENSORS = [
    {
        "id": "ESP32-AERO-01",
        "name": "DTU Innovation Lab Node",
        "location": "Shahbad Daulatpur, Rohini Sec 16",
        "latitude": 28.749500,
        "longitude": 77.118000,
        "hardware_type": "ESP32 + PMS5003 + DHT22 + MQ135",
        "status": "ONLINE",
        "battery_level": 98.5
    },
    {
        "id": "ESP32-AERO-02",
        "name": "Outer Ring Road Junction Node",
        "location": "Mukarba Chowk, North Delhi",
        "latitude": 28.736000,
        "longitude": 77.148000,
        "hardware_type": "ESP32 + PMS5003 + DHT22",
        "status": "ONLINE",
        "battery_level": 94.0
    },
    {
        "id": "ESP32-AERO-03",
        "name": "Pitampura Residential Node",
        "location": "Pitampura Block CP",
        "latitude": 28.698000,
        "longitude": 77.138000,
        "hardware_type": "ESP32 + PMS5003 + DHT22",
        "status": "ONLINE",
        "battery_level": 89.0
    },
    {
        "id": "ESP32-AERO-04",
        "name": "Bawana Industrial Perimeter Node",
        "location": "Bawana Sector 4",
        "latitude": 28.781000,
        "longitude": 77.042000,
        "hardware_type": "ESP32 + PMS5003 + MQ135 + DHT22",
        "status": "ONLINE",
        "battery_level": 100.0
    },
    {
        "id": "ESP32-AERO-05",
        "name": "Connaught Place Urban Node",
        "location": "Inner Circle, Connaught Place",
        "latitude": 28.631500,
        "longitude": 77.216700,
        "hardware_type": "ESP32 + PMS5003 + DHT22",
        "status": "ONLINE",
        "battery_level": 92.0
    }
]


def seed_database(clean_csv_path: str = 'data/processed/cleaned_cpcb_dtu.csv'):
    """Executes full database seeding."""
    print("[Seed] Initializing database tables...")
    init_db()
    db = SessionLocal()

    try:
        # 1. Seed Stations
        print("[Seed] Seeding CAAQMS monitoring stations...")
        for s_data in STATIONS:
            existing = db.query(Station).filter(Station.id == s_data["id"]).first()
            if not existing:
                st = Station(**s_data)
                db.add(st)
        db.commit()

        # 2. Seed IoT Sensors
        print("[Seed] Seeding IoT sensor network...")
        for sen_data in SENSORS:
            existing = db.query(Sensor).filter(Sensor.id == sen_data["id"]).first()
            if not existing:
                sen = Sensor(**sen_data)
                db.add(sen)
        db.commit()

        # 3. Seed Air Quality Records from cleaned CPCB dataset
        if os.path.exists(clean_csv_path):
            print(f"[Seed] Loading processed records from {clean_csv_path}...")
            df = pd.read_csv(clean_csv_path)
            # Use most recent 2,000 records for fast local startup, or sample if large
            record_count = db.query(AirQualityRecord).count()
            if record_count < 100:
                print(f"[Seed] Inserting recent 3,000 records into database...")
                sample_df = df.tail(3000).copy()
                records_to_insert = []
                for _, row in sample_df.iterrows():
                    ts = pd.to_datetime(row['timestamp'])
                    rec = AirQualityRecord(
                        station_id='site_118',
                        location='DTU, Delhi - CPCB',
                        latitude=28.750075,
                        longitude=77.111261,
                        timestamp=ts,
                        pm25=float(row['pm25']) if pd.notnull(row.get('pm25')) else None,
                        pm10=float(row['pm10']) if pd.notnull(row.get('pm10')) else None,
                        no=float(row['no']) if pd.notnull(row.get('no')) else None,
                        no2=float(row['no2']) if pd.notnull(row.get('no2')) else None,
                        nox=float(row['nox']) if pd.notnull(row.get('nox')) else None,
                        nh3=float(row['nh3']) if pd.notnull(row.get('nh3')) else None,
                        so2=float(row['so2']) if pd.notnull(row.get('so2')) else None,
                        co=float(row['co']) if pd.notnull(row.get('co')) else None,
                        ozone=float(row['ozone']) if pd.notnull(row.get('ozone')) else None,
                        temperature=float(row['temperature']) if pd.notnull(row.get('temperature')) else 26.5,
                        humidity=float(row['rh']) if pd.notnull(row.get('rh')) else 55.0,
                        wind_speed=float(row['ws']) if pd.notnull(row.get('ws')) else 2.1,
                        wind_direction=float(row['wd']) if pd.notnull(row.get('wd')) else 180.0,
                        aqi=int(row['aqi']) if pd.notnull(row.get('aqi')) else None,
                        aqi_category=str(row['aqi_category']) if pd.notnull(row.get('aqi_category')) else None,
                        dominant_pollutant=str(row['dominant_pollutant']) if pd.notnull(row.get('dominant_pollutant')) else 'PM2.5',
                        is_simulated=False
                    )
                    records_to_insert.append(rec)
                db.add_all(records_to_insert)
                db.commit()
                print(f"[Seed] Inserted {len(records_to_insert)} CPCB air quality records.")

        # 4. Seed Hotspots
        print("[Seed] Seeding active pollution hotspots...")
        db.query(Hotspot).delete()
        hotspots_data = [
            {
                "location": "Bawana Industrial Perimeter",
                "latitude": 28.776200,
                "longitude": 77.051070,
                "current_aqi": 342,
                "current_pm25": 192.4,
                "trend": "Increasing",
                "severity_level": "Severe",
                "likely_source": "Likely Industrial & Local Fuel Combustion Pattern",
                "confidence_score": 0.88
            },
            {
                "location": "Anand Vihar ISBT Corridor",
                "latitude": 28.647260,
                "longitude": 77.316040,
                "current_aqi": 388,
                "current_pm25": 235.1,
                "trend": "Increasing",
                "severity_level": "Severe",
                "likely_source": "Likely Heavy Vehicular & Inter-state Transit Pattern",
                "confidence_score": 0.93
            },
            {
                "location": "Mukarba Chowk Intersection",
                "latitude": 28.736000,
                "longitude": 77.148000,
                "current_aqi": 278,
                "current_pm25": 114.6,
                "trend": "Stable",
                "severity_level": "Poor",
                "likely_source": "Likely Traffic-Associated Pattern",
                "confidence_score": 0.82
            },
            {
                "location": "DTU Campus / Shahbad Daulatpur",
                "latitude": 28.750075,
                "longitude": 77.111261,
                "current_aqi": 215,
                "current_pm25": 94.2,
                "trend": "Decreasing",
                "severity_level": "Poor",
                "likely_source": "Likely Regional / Secondary Background Aerosol Pattern",
                "confidence_score": 0.76
            }
        ]
        for h in hotspots_data:
            db.add(Hotspot(**h))
        db.commit()

        # 5. Seed Alerts
        print("[Seed] Seeding system alerts...")
        db.query(Alert).delete()
        alerts_data = [
            {
                "location": "Anand Vihar ISBT Corridor",
                "station_id": "site_142",
                "severity": "CRITICAL",
                "title": "Severe Air Quality Deterioration",
                "message": "AQI has escalated to 388 (Severe). High PM2.5 concentrations exceeding 235 µg/m³. Sensitive groups must avoid all outdoor physical exertion.",
                "current_aqi": 388,
                "predicted_aqi": 412,
                "reason": "Sustained high traffic density and low atmospheric boundary layer mixing.",
                "timestamp": datetime.utcnow() - timedelta(minutes=25),
                "is_active": True
            },
            {
                "location": "Bawana Industrial Perimeter",
                "station_id": "site_502",
                "severity": "DANGER",
                "title": "Industrial Zone Hotspot Alert",
                "message": "AQI reached 342 (Very Poor). Model forecasts sustained high pollutant levels over the next 4 hours.",
                "current_aqi": 342,
                "predicted_aqi": 360,
                "reason": "Elevated PM10 and SO2 ratios indicating localized emission concentration.",
                "timestamp": datetime.utcnow() - timedelta(minutes=50),
                "is_active": True
            },
            {
                "location": "DTU Campus / North Delhi",
                "station_id": "site_118",
                "severity": "WARNING",
                "title": "Air Quality Advisory - Poor Category",
                "message": "Current AQI is 215 (Poor). Forecast indicates moderate reduction as wind dispersion increases.",
                "current_aqi": 215,
                "predicted_aqi": 185,
                "reason": "Diurnal evening traffic accumulation.",
                "timestamp": datetime.utcnow() - timedelta(minutes=15),
                "is_active": True
            }
        ]
        for a in alerts_data:
            db.add(Alert(**a))
        db.commit()

        # 6. Seed Model Metrics if JSON exists
        metrics_json_path = 'models/model_metrics.json'
        if os.path.exists(metrics_json_path):
            print("[Seed] Seeding model evaluation metrics...")
            with open(metrics_json_path, 'r', encoding='utf-8') as f:
                metrics_data = json.load(f)
            db.query(ModelMetric).delete()
            for m_key, m_val in metrics_data.get('models', {}).items():
                rec = ModelMetric(
                    model_name=m_val.get('model_name', m_key),
                    mae=float(m_val.get('mae', 0.0)),
                    rmse=float(m_val.get('rmse', 0.0)),
                    r2=float(m_val.get('r2', 0.0)),
                    mae_improvement_pct=float(m_val.get('mae_improvement_pct', 0.0)) if 'mae_improvement_pct' in m_val else None,
                    rmse_improvement_pct=float(m_val.get('rmse_improvement_pct', 0.0)) if 'rmse_improvement_pct' in m_val else None,
                    training_time_seconds=float(m_val.get('training_time_seconds', 0.0)) if 'training_time_seconds' in m_val else None,
                    inference_latency_ms=float(m_val.get('inference_latency_ms', 0.0)) if 'inference_latency_ms' in m_val else None
                )
                db.add(rec)
            db.commit()

        print("[Seed] Database seeding completed successfully.")

    except Exception as e:
        db.rollback()
        print(f"[Seed] Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    seed_database()
