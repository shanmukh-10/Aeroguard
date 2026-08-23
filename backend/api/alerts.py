"""
AeroGuard Alerts API Router
---------------------------
Endpoint: GET /api/alerts
Returns active real-time air quality warnings and health advisories.
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Alert
from backend.schemas.air_quality import AlertResponse

router = APIRouter(prefix="", tags=["Alerts"])


@router.get("/alerts", response_model=List[AlertResponse])
def get_active_alerts(
    active_only: bool = Query(True, description="Filter for active alerts"),
    db: Session = Depends(get_db)
):
    """
    Returns active real-time automated alerts.
    """
    query = db.query(Alert)
    if active_only:
        query = query.filter(Alert.is_active == True)
    
    alerts = query.order_by(Alert.timestamp.desc()).limit(20).all()
    return [
        AlertResponse(
            id=a.id,
            location=a.location,
            severity=a.severity,
            title=a.title,
            message=a.message,
            current_aqi=a.current_aqi,
            predicted_aqi=a.predicted_aqi,
            reason=a.reason,
            timestamp=a.timestamp,
            is_active=a.is_active
        )
        for a in alerts
    ]
