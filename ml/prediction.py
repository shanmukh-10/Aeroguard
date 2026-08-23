"""
AeroGuard Prediction Service
----------------------------
Loads saved model weights (Random Forest / LSTM) and performs multi-step
future PM2.5 forecasting, AQI derivation, trend analysis, and confidence scoring.
"""

import os
import joblib
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from ml.aqi_calculator import calculate_overall_aqi, calculate_sub_index, get_aqi_category_info


class AeroGuardPredictor:
    def __init__(self, model_dir: Optional[str] = None):
        if model_dir is None:
            # Anchor to repository root directory
            repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            candidate = os.path.join(repo_root, 'models')
            self.model_dir = candidate if os.path.exists(candidate) else 'models'
        else:
            self.model_dir = model_dir
        self.rf_model = None
        self.feature_cols = None
        self.metrics = None
        self.load_models()

    def load_models(self):
        """Loads trained model weights and metadata."""
        rf_path = os.path.join(self.model_dir, 'rf_pm25.joblib')
        metrics_path = os.path.join(self.model_dir, 'model_metrics.json')

        if os.path.exists(rf_path):
            try:
                payload = joblib.load(rf_path)
                self.rf_model = payload['model']
                self.feature_cols = payload['feature_cols']
                print(f"[Predictor] Loaded Random Forest model with {len(self.feature_cols)} features.")
            except Exception as e:
                print(f"[Predictor] Warning loading RF model: {e}")

        if os.path.exists(metrics_path):
            try:
                with open(metrics_path, 'r', encoding='utf-8') as f:
                    self.metrics = json.load(f)
            except Exception as e:
                print(f"[Predictor] Warning loading metrics: {e}")

    def predict_multi_step(self, recent_records: List[Dict[str, Any]], hours_ahead: int = 12) -> Dict[str, Any]:
        """
        Generates multi-step predictions for the next `hours_ahead` hours (at 1-hour or 15-min intervals).
        Returns a list of forecasted points with timestamp, predicted PM2.5, predicted AQI, category, and trend.
        """
        if not recent_records:
            return {"forecast": [], "trend": "Unknown", "model_used": "Fallback Persistence"}

        # Convert records to DataFrame
        df = pd.DataFrame(recent_records)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').reset_index(drop=True)

        current_record = recent_records[-1]
        current_pm25 = float(current_record.get('pm25', 100.0) or 100.0)
        current_pm10 = float(current_record.get('pm10', current_pm25 * 1.6) or current_pm25 * 1.6)
        current_no2 = float(current_record.get('no2', 45.0) or 45.0)
        current_so2 = float(current_record.get('so2', 15.0) or 15.0)
        current_co = float(current_record.get('co', 1.2) or 1.2)
        current_o3 = float(current_record.get('ozone', 30.0) or 30.0)
        base_time = pd.to_datetime(current_record.get('timestamp', datetime.utcnow()))

        forecast_points = []
        step_pm25 = current_pm25

        # Perform auto-regressive / multi-horizon forecast
        steps = max(4, hours_ahead * 4)  # 15-minute intervals
        for step in range(1, steps + 1):
            future_dt = base_time + timedelta(minutes=step * 15)
            
            # Predict using RF if available, else smooth diurnal autoregressive model
            if self.rf_model is not None and self.feature_cols is not None:
                # Build feature row
                hour = future_dt.hour + future_dt.minute / 60.0
                month = future_dt.month
                day_of_week = future_dt.dayofweek
                
                feat_dict = {col: 0.0 for col in self.feature_cols}
                feat_dict['pm25_lag_1'] = step_pm25
                feat_dict['pm25_lag_2'] = step_pm25 * 0.98
                feat_dict['pm25_lag_4'] = current_pm25
                feat_dict['pm25_lag_8'] = current_pm25
                feat_dict['pm25_lag_16'] = current_pm25
                feat_dict['pm25_lag_32'] = current_pm25
                feat_dict['pm25_lag_96'] = current_pm25
                feat_dict['pm25_roll_mean_1h'] = step_pm25
                feat_dict['pm25_roll_mean_4h'] = (step_pm25 + current_pm25) / 2
                feat_dict['pm25_roll_mean_24h'] = current_pm25
                feat_dict['pm10_lag_1'] = current_pm10
                feat_dict['no2_lag_1'] = current_no2
                feat_dict['so2_lag_1'] = current_so2
                feat_dict['co_lag_1'] = current_co
                feat_dict['ozone_lag_1'] = current_o3
                feat_dict['rh'] = float(current_record.get('rh', 60.0) or 60.0)
                feat_dict['ws'] = float(current_record.get('ws', 2.0) or 2.0)
                feat_dict['hour_sin'] = np.sin(2 * np.pi * hour / 24.0)
                feat_dict['hour_cos'] = np.cos(2 * np.pi * hour / 24.0)
                feat_dict['month_sin'] = np.sin(2 * np.pi * month / 12.0)
                feat_dict['month_cos'] = np.cos(2 * np.pi * month / 12.0)
                feat_dict['day_of_week'] = day_of_week
                feat_dict['is_weekend'] = 1 if day_of_week >= 5 else 0

                feat_vector = np.array([[feat_dict[c] for c in self.feature_cols]])
                predicted_val = float(self.rf_model.predict(feat_vector)[0])
                # Blend with step propagation
                predicted_val = max(0.0, 0.7 * predicted_val + 0.3 * step_pm25)
            else:
                # Diurnal curve persistence estimation
                diurnal_factor = 1.0 + 0.15 * np.sin(2 * np.pi * (future_dt.hour - 6) / 24.0)
                predicted_val = max(0.0, current_pm25 * (1.0 + (step * 0.005)) * diurnal_factor)

            step_pm25 = predicted_val

            # Only output points at 1-hour intervals or select steps to keep response lightweight
            if step % 4 == 0 or step in [1, 2, 4, 8]:
                pred_pollutants = {
                    'pm25': round(predicted_val, 1),
                    'pm10': round(predicted_val * 1.55, 1),
                    'no2': round(current_no2, 1),
                    'so2': round(current_so2, 1),
                    'co': round(current_co, 2),
                    'ozone': round(current_o3, 1)
                }
                aqi_res = calculate_overall_aqi(pred_pollutants, enforce_cpcb_rule=False)
                forecast_points.append({
                    "forecast_time": future_dt.isoformat(),
                    "hours_from_now": round(step * 0.25, 2),
                    "predicted_pm25": round(predicted_val, 1),
                    "predicted_pm10": round(predicted_val * 1.55, 1),
                    "predicted_aqi": aqi_res["aqi"],
                    "category": aqi_res["category"],
                    "color": aqi_res["color"],
                    "advisory": aqi_res["advisory"]
                })

        # Determine overall trend
        if forecast_points:
            first_pred = forecast_points[0]["predicted_pm25"]
            last_pred = forecast_points[-1]["predicted_pm25"]
            diff = last_pred - first_pred
            if diff > 10.0:
                trend = "Increasing"
            elif diff < -10.0:
                trend = "Decreasing"
            else:
                trend = "Stable"
        else:
            trend = "Stable"

        return {
            "current_pm25": current_pm25,
            "forecast": forecast_points,
            "trend": trend,
            "model_name": "Random Forest (Tuned Regressor)" if self.rf_model is not None else "Persistence Diurnal Forecaster",
            "model_metrics": self.metrics.get("models", {}).get("random_forest", {}) if self.metrics else {}
        }
