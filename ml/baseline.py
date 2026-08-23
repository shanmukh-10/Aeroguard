"""
AeroGuard Baseline Forecaster
------------------------------
Implements a Naive Persistence Baseline model:
Forecast PM2.5 at time t+h is assumed to equal the latest observed PM2.5 at time t.
This represents the primary benchmark against which AI models are evaluated.
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def evaluate_persistence_baseline(test_df: pd.DataFrame, target_col: str = 'target_pm25_2h') -> Dict[str, Any]:
    """
    Evaluates the persistence baseline where predicted value is pm25_lag_1 (or current pm25).
    """
    start_time = time.time()
    
    y_true = test_df[target_col].values
    # Persistence: predict current pm25 for future target
    y_pred = test_df['pm25'].values if 'pm25' in test_df.columns else test_df['pm25_lag_1'].values

    # Remove any NaN pairs
    valid_mask = ~np.isnan(y_true) & ~np.isnan(y_pred)
    y_true = y_true[valid_mask]
    y_pred = y_pred[valid_mask]

    inference_time = (time.time() - start_time) / max(1, len(y_true))

    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred))

    metrics = {
        "model_name": "Persistence Baseline",
        "mae": round(mae, 3),
        "rmse": round(rmse, 3),
        "r2": round(r2, 4),
        "training_time_seconds": 0.0,
        "inference_latency_ms": round(inference_time * 1000, 4),
        "sample_count": int(len(y_true))
    }
    print(f"[Persistence Baseline] MAE: {mae:.3f} | RMSE: {rmse:.3f} | R²: {r2:.4f}")
    return metrics, y_pred
