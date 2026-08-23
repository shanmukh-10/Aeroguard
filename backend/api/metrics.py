"""
AeroGuard Model Metrics API Router
----------------------------------
Endpoint: GET /api/model-metrics
Returns measured benchmark comparison between Persistence Baseline, Random Forest, and LSTM.
"""

import os
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import ModelMetric
from backend.schemas.air_quality import ModelMetricsResponse

router = APIRouter(prefix="", tags=["Model Benchmarks"])


@router.get("/model-metrics")
def get_model_metrics(db: Session = Depends(get_db)):
    """
    Returns empirical validation metrics (MAE, RMSE, R2, Latency, Error Reduction %).
    """
    json_path = 'models/model_metrics.json'
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading metrics JSON: {e}")

    # Fallback to database or default benchmark structure
    metrics = db.query(ModelMetric).all()
    models_dict = {}
    for m in metrics:
        models_dict[m.model_name.lower().replace(" ", "_")] = {
            "model_name": m.model_name,
            "mae": m.mae,
            "rmse": m.rmse,
            "r2": m.r2,
            "mae_improvement_pct": m.mae_improvement_pct,
            "rmse_improvement_pct": m.rmse_improvement_pct,
            "training_time_seconds": m.training_time_seconds,
            "inference_latency_ms": m.inference_latency_ms
        }

    return {
        "target": "Future PM2.5 (2-hour forecast horizon)",
        "frequency": "15 minutes",
        "dataset": "Delhi DTU-CPCB (2024-2025)",
        "train_samples": 56000,
        "test_samples": 14000,
        "best_model": "Random Forest Regressor",
        "models": models_dict
    }
