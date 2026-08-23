"""
Unit Tests for Machine Learning Pipeline
----------------------------------------
Validates feature engineering, cyclical encoding, model loading,
and multi-step prediction outputs.
"""

import os
import pytest
import pandas as pd
import numpy as np
from ml.feature_engineering import create_cyclical_features, create_lag_and_rolling_features, create_targets
from ml.prediction import AeroGuardPredictor


def test_cyclical_features():
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01 00:00', periods=96, freq='15min'),
        'pm25': np.random.uniform(30, 150, 96)
    })
    feat_df = create_cyclical_features(df)
    assert 'hour_sin' in feat_df.columns
    assert 'hour_cos' in feat_df.columns
    assert 'month_sin' in feat_df.columns
    assert feat_df['hour_sin'].min() >= -1.0
    assert feat_df['hour_sin'].max() <= 1.0


def test_lag_and_rolling_features():
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01 00:00', periods=120, freq='15min'),
        'pm25': np.linspace(20, 140, 120)
    })
    lag_df = create_lag_and_rolling_features(df)
    assert 'pm25_lag_1' in lag_df.columns
    assert 'pm25_lag_4' in lag_df.columns
    assert 'pm25_roll_mean_1h' in lag_df.columns


def test_predictor_multi_step():
    predictor = AeroGuardPredictor(model_dir='models')
    records = [
        {"timestamp": "2024-01-01 10:00:00", "pm25": 80.0, "pm10": 140.0, "no2": 45.0, "so2": 12.0, "co": 1.2, "ozone": 30.0},
        {"timestamp": "2024-01-01 10:15:00", "pm25": 85.0, "pm10": 148.0, "no2": 46.0, "so2": 13.0, "co": 1.3, "ozone": 31.0},
        {"timestamp": "2024-01-01 10:30:00", "pm25": 90.0, "pm10": 155.0, "no2": 48.0, "so2": 14.0, "co": 1.4, "ozone": 32.0},
    ]
    res = predictor.predict_multi_step(records, hours_ahead=4)
    assert "forecast" in res
    assert len(res["forecast"]) >= 2
    assert res["forecast"][0]["predicted_pm25"] > 0
    assert "trend" in res
