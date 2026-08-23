"""
Unit Tests for Data Preprocessing Pipeline
------------------------------------------
Tests column sanitization, timestamp validation, time-aware interpolation limits,
elimination of 100% empty columns (e.g. bp, vws, at), and physical bounds verification.
"""

import os
import pandas as pd
import numpy as np
import pytest
from ml.preprocessing import (
    load_and_standardize,
    validate_and_clean_timestamps,
    clean_sensor_measurements,
    PHYSICAL_BOUNDS
)


def test_clean_sensor_measurements_bounds():
    df = pd.DataFrame({
        'pm25': [50.0, -10.0, 1500.0, np.nan, 60.0],
        'rh': [55.0, 120.0, np.nan, 45.0, -5.0]
    })
    cleaned = clean_sensor_measurements(df, max_interpolation_gap=2)

    # -10 and 1500 should be filtered and interpolated/handled
    assert cleaned['pm25'].min() >= 0.0
    assert cleaned['pm25'].max() <= 1000.0
    assert cleaned['rh'].min() >= 0.0
    assert cleaned['rh'].max() <= 100.0


def test_interpolation_gap_limits():
    # Gap of 2 (should be interpolated) vs Gap of 8 (should retain NaNs beyond limit 4)
    df = pd.DataFrame({
        'pm25': [10.0, np.nan, np.nan, 40.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 100.0]
    })
    cleaned = clean_sensor_measurements(df, max_interpolation_gap=4)
    # The first short gap is fully interpolated
    assert not cleaned['pm25'].iloc[1:3].isnull().any()
    # The second long gap retains NaNs past the 4-step limit
    assert cleaned['pm25'].iloc[8:10].isnull().any()


def test_validate_and_clean_timestamps():
    df = pd.DataFrame({
        'station_id': ['site_118', 'site_118', 'site_118'],
        'timestamp': ['01-01-2024 00:00', np.nan, '01-01-2024 00:15'],
        'pm25': [50.0, 55.0, 60.0]
    })
    cleaned = validate_and_clean_timestamps(df)
    assert len(cleaned) == 2
    assert pd.to_datetime(cleaned['timestamp'].iloc[0]) < pd.to_datetime(cleaned['timestamp'].iloc[1])


def test_processed_dataset_quality():
    processed_path = 'data/processed/cleaned_cpcb_dtu.csv'
    if os.path.exists(processed_path):
        df = pd.read_csv(processed_path)
        assert len(df) >= 70000
        assert 'pm25' in df.columns
        assert 'aqi' in df.columns
        # bp column and other 100% empty columns must be completely removed
        assert 'bp' not in df.columns
        assert 'vws' not in df.columns
        assert 'at' not in df.columns
        assert 'toluene' not in df.columns
        assert 'xylene' not in df.columns
        assert 'o_xylene' not in df.columns

        # Ensure NO column in the processed dataset is 100% missing
        for col in df.columns:
            assert not df[col].isnull().all(), f"Column {col} is 100% missing in processed dataset!"
