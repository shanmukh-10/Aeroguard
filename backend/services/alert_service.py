"""
AeroGuard Automated Alert Engine
--------------------------------
Monitors current AQI, predicted multi-hour deterioration, and rate-of-change
to automatically generate and manage actionable alerts.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from database.models import Alert, AirQualityRecord


def evaluate_and_generate_alerts(
    db: Session,
    location: str,
    current_aqi: int,
    current_pm25: float,
    predicted_aqi: Optional[int] = None,
    station_id: Optional[str] = None,
    sensor_id: Optional[str] = None
) -> Optional[Alert]:
    """
    Evaluates real-time sensor / station reading against alert rules:
    - Critical (AQI >= 400 or PM2.5 >= 250)
    - Danger (AQI >= 300 or predicted escalation > 50 points)
    - Warning (AQI >= 200)
    - Rapid Rate of Change (> 35 µg/m³ rise in 1 hour)
    """
    if current_aqi is None:
        return None

    severity = None
    title = None
    message = None
    reason = None

    # Check for rapid deterioration
    recent_rec = db.query(AirQualityRecord).filter(
        AirQualityRecord.station_id == station_id if station_id else AirQualityRecord.sensor_id == sensor_id
    ).order_by(AirQualityRecord.timestamp.desc()).first()

    pm25_jump = 0.0
    if recent_rec and recent_rec.pm25 is not None:
        pm25_jump = current_pm25 - recent_rec.pm25

    if current_aqi >= 400 or current_pm25 >= 250.0:
        severity = "CRITICAL"
        title = f"Severe Air Quality Emergency in {location}"
        message = f"AQI has escalated to {current_aqi} (Severe). PM2.5 concentration is {current_pm25:.1f} µg/m³. Immediate reduction in all outdoor exposure is advised."
        reason = "Extremely elevated particulate concentration crossing emergency threshold."

    elif (predicted_aqi and predicted_aqi >= 350) or current_aqi >= 300:
        severity = "DANGER"
        title = f"High Pollution Alert for {location}"
        message = f"Current AQI is {current_aqi} (Very Poor) and forecasted to reach {predicted_aqi or current_aqi} within the next 2-4 hours."
        reason = "High pollution with sustained escalation forecast."

    elif pm25_jump >= 35.0:
        severity = "WARNING"
        title = f"Rapid Pollution Surge Detected in {location}"
        message = f"PM2.5 concentration spiked by +{pm25_jump:.1f} µg/m³ in recent intervals. AQI is now {current_aqi}."
        reason = "Sudden localized particulate spike."

    elif current_aqi >= 201:
        severity = "WARNING"
        title = f"Poor Air Quality Advisory for {location}"
        message = f"AQI has entered the Poor category at {current_aqi}. Sensitive groups should limit strenuous outdoor activity."
        reason = "Exceeds clean air advisory threshold."

    if severity:
        # Check if an identical active alert was posted in the last 30 minutes to prevent spam
        recent_alert = db.query(Alert).filter(
            Alert.location == location,
            Alert.severity == severity,
            Alert.timestamp >= datetime.utcnow() - timedelta(minutes=30)
        ).first()

        if not recent_alert:
            alert = Alert(
                location=location,
                station_id=station_id,
                sensor_id=sensor_id,
                severity=severity,
                title=title,
                message=message,
                current_aqi=current_aqi,
                predicted_aqi=predicted_aqi,
                reason=reason,
                timestamp=datetime.utcnow(),
                is_active=True
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)
            return alert
        else:
            return recent_alert

    return None
