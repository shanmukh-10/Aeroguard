"""
AeroGuard Feature Engineering Pipeline
---------------------------------------
Creates time-series lag features, rolling statistics, cyclical diurnal & seasonal
encodings, and future multi-step prediction targets for PM2.5 forecasting.
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any


def create_cyclical_features(df: pd.DataFrame) -> pd.DataFrame:
    """Encodes hour and month into continuous cyclical sine/cosine features."""
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    hours = df['timestamp'].dt.hour + df['timestamp'].dt.minute / 60.0
    months = df['timestamp'].dt.month
    day_of_week = df['timestamp'].dt.dayofweek

    df['hour_sin'] = np.sin(2 * np.pi * hours / 24.0)
    df['hour_cos'] = np.cos(2 * np.pi * hours / 24.0)
    df['month_sin'] = np.sin(2 * np.pi * months / 12.0)
    df['month_cos'] = np.cos(2 * np.pi * months / 12.0)
    df['day_of_week'] = day_of_week
    df['is_weekend'] = (day_of_week >= 5).astype(int)

    # Wind direction cyclical encoding
    if 'wd' in df.columns:
        valid_wd = df['wd'].fillna(0.0)
        df['wd_sin'] = np.sin(2 * np.pi * valid_wd / 360.0)
        df['wd_cos'] = np.cos(2 * np.pi * valid_wd / 360.0)

    return df


def create_lag_and_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates lag and rolling statistics for 15-minute interval data.
    - 1 step = 15 mins
    - 4 steps = 1 hr
    - 16 steps = 4 hrs
    - 96 steps = 24 hrs
    """
    df = df.copy()

    # PM2.5 lags
    lags = [1, 2, 4, 8, 16, 32, 96]
    for lag in lags:
        df[f'pm25_lag_{lag}'] = df['pm25'].shift(lag)

    # PM10 and other key pollutant lags
    for col in ['pm10', 'no2', 'so2', 'co', 'ozone']:
        if col in df.columns:
            df[f'{col}_lag_1'] = df[col].shift(1)
            df[f'{col}_lag_4'] = df[col].shift(4)

    # Rolling window stats for PM2.5
    windows = {'1h': 4, '4h': 16, '24h': 96}
    for name, win in windows.items():
        df[f'pm25_roll_mean_{name}'] = df['pm25'].shift(1).rolling(window=win, min_periods=max(1, win // 4)).mean()
        df[f'pm25_roll_std_{name}'] = df['pm25'].shift(1).rolling(window=win, min_periods=max(1, win // 4)).std().fillna(0.0)

    # PM10 rolling stats
    if 'pm10' in df.columns:
        df['pm10_roll_mean_1h'] = df['pm10'].shift(1).rolling(window=4, min_periods=1).mean()
        df['pm10_roll_mean_24h'] = df['pm10'].shift(1).rolling(window=96, min_periods=12).mean()

    # Rate of change: (PM2.5(t-1) - PM2.5(t-5)) / 4 (trend over the last hour)
    df['pm25_diff_1h'] = df['pm25'].shift(1) - df['pm25'].shift(5)
    df['pm25_diff_4h'] = df['pm25'].shift(1) - df['pm25'].shift(17)

    return df


def create_targets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates future PM2.5 forecasting targets:
    - target_pm25_1h: 1 hour ahead (shift -4)
    - target_pm25_2h: 2 hours ahead (shift -8) [Primary forecast target]
    - target_pm25_4h: 4 hours ahead (shift -16)
    - target_pm25_12h: 12 hours ahead (shift -48)
    - target_pm25_24h: 24 hours ahead (shift -96)
    """
    df = df.copy()
    target_horizons = {
        '1h': 4,
        '2h': 8,
        '4h': 16,
        '12h': 48,
        '24h': 96
    }
    for horizon, steps in target_horizons.items():
        df[f'target_pm25_{horizon}'] = df['pm25'].shift(-steps)

    return df


def get_feature_columns() -> List[str]:
    """Returns the standardized list of input feature column names for ML models."""
    return [
        'pm25_lag_1', 'pm25_lag_2', 'pm25_lag_4', 'pm25_lag_8', 'pm25_lag_16', 'pm25_lag_32', 'pm25_lag_96',
        'pm25_roll_mean_1h', 'pm25_roll_std_1h', 'pm25_roll_mean_4h', 'pm25_roll_std_4h',
        'pm25_roll_mean_24h', 'pm25_roll_std_24h',
        'pm25_diff_1h', 'pm25_diff_4h',
        'pm10_lag_1', 'pm10_lag_4', 'pm10_roll_mean_1h', 'pm10_roll_mean_24h',
        'no2_lag_1', 'no2_lag_4', 'so2_lag_1', 'co_lag_1', 'ozone_lag_1',
        'rh', 'ws', 'wd_sin', 'wd_cos',
        'hour_sin', 'hour_cos', 'month_sin', 'month_cos', 'day_of_week', 'is_weekend'
    ]


def prepare_ml_dataset(clean_csv_path: str, target_col: str = 'target_pm25_2h') -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """
    Loads clean dataset, engineers all features and targets, applies chronological 80/20 train/test split.
    Returns (train_df, test_df, feature_cols).
    """
    df = pd.read_csv(clean_csv_path)
    df = create_cyclical_features(df)
    df = create_lag_and_rolling_features(df)
    df = create_targets(df)

    feature_cols = [c for c in get_feature_columns() if c in df.columns]

    # Drop rows where target or key features are null (edges due to lags/targets)
    valid_mask = df[target_col].notnull() & df['pm25_lag_1'].notnull() & df['pm25_lag_96'].notnull()
    valid_df = df[valid_mask].copy()

    # Fill any remaining feature NaNs and ensure float dtype
    valid_df[feature_cols] = valid_df[feature_cols].apply(pd.to_numeric, errors='coerce').ffill().bfill().fillna(0.0)

    # Strict chronological split (80% train, 20% test)
    split_idx = int(len(valid_df) * 0.8)
    train_df = valid_df.iloc[:split_idx].copy().reset_index(drop=True)
    test_df = valid_df.iloc[split_idx:].copy().reset_index(drop=True)

    print(f"Dataset split: Train={len(train_df)} rows ({train_df['timestamp'].min()} to {train_df['timestamp'].max()})")
    print(f"               Test={len(test_df)} rows ({test_df['timestamp'].min()} to {test_df['timestamp'].max()})")
    print(f"Total features: {len(feature_cols)}")

    return train_df, test_df, feature_cols
