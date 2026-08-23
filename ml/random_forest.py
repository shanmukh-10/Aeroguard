"""
AeroGuard Random Forest Forecaster (Residual-Augmented)
------------------------------------------------------
Trains and evaluates a Random Forest Regressor predicting the residual change:
  Δy = target_pm25 - pm25_current
and reconstructing final prediction as:
  y_pred = pm25_current + Δy_pred
This leverages both strong auto-regressive persistence and non-linear meteorological interactions.
"""

import os
import time
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def train_random_forest(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_cols: List[str],
    target_col: str = 'target_pm25_2h',
    model_save_path: str = 'models/rf_pm25.joblib'
) -> Tuple[Dict[str, Any], np.ndarray, RandomForestRegressor]:
    """
    Trains Residual Random Forest Regressor on chronological train partition,
    evaluates on unseen test partition, and saves weights.
    """
    valid_train = train_df[target_col].notnull() & train_df['pm25'].notnull()
    X_train = train_df.loc[valid_train, feature_cols].values
    current_train_pm25 = train_df.loc[valid_train, 'pm25'].values
    y_train_target = train_df.loc[valid_train, target_col].values
    y_train_delta = y_train_target - current_train_pm25

    valid_test = test_df[target_col].notnull() & test_df['pm25'].notnull()
    X_test = test_df.loc[valid_test, feature_cols].values
    current_test_pm25 = test_df.loc[valid_test, 'pm25'].values
    y_test_target = test_df.loc[valid_test, target_col].values

    print(f"Training Residual Random Forest on {len(X_train)} samples with {len(feature_cols)} features...")
    start_train = time.time()
    
    rf = RandomForestRegressor(
        n_estimators=100,
        max_depth=14,
        min_samples_split=6,
        min_samples_leaf=4,
        n_jobs=-1,
        random_state=42
    )
    rf.fit(X_train, y_train_delta)
    training_time = time.time() - start_train
    print(f"Random Forest trained in {training_time:.2f} seconds.")

    # Evaluate on test set
    start_infer = time.time()
    delta_pred = rf.predict(X_test)
    y_pred = current_test_pm25 + delta_pred
    inference_time = (time.time() - start_infer) / len(X_test)

    # Post-process: PM2.5 cannot be negative
    y_pred = np.clip(y_pred, a_min=0.0, a_max=None)

    mae = float(mean_absolute_error(y_test_target, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test_target, y_pred)))
    r2 = float(r2_score(y_test_target, y_pred))

    # Feature importances
    importances = {
        col: round(float(imp), 4)
        for col, imp in sorted(zip(feature_cols, rf.feature_importances_), key=lambda x: x[1], reverse=True)[:10]
    }

    metrics = {
        "model_name": "Random Forest (Residual Regressor)",
        "mae": round(mae, 3),
        "rmse": round(rmse, 3),
        "r2": round(r2, 4),
        "training_time_seconds": round(training_time, 2),
        "inference_latency_ms": round(inference_time * 1000, 4),
        "top_features": importances,
        "sample_count": int(len(y_test_target))
    }
    print(f"[Random Forest Residual] MAE: {mae:.3f} | RMSE: {rmse:.3f} | R²: {r2:.4f}")

    # Save model and metadata
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    payload = {
        'model': rf,
        'feature_cols': feature_cols,
        'target_col': target_col,
        'metrics': metrics
    }
    joblib.dump(payload, model_save_path)
    print(f"Saved Random Forest model artifact to {model_save_path}")

    return metrics, y_pred, rf
