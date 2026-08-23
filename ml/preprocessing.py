"""
AeroGuard Data Preprocessing & Validation Pipeline
---------------------------------------------------
Cleans raw Delhi DTU-CPCB 2024-25 dataset:
- Removes corrupted rows and 100% empty / unusable columns (e.g. VWS, O-Xylene, AT, Toluene, Xylene, BP).
- Performs time-aware interpolation strictly for short gaps (<= 4 x 15-min intervals = 1 hr).
- Retains legitimate missing values across long sensor outages without fabricating measurements.
- Applies physical bounds checks.
- Calculates official CPCB rolling concentrations and AQI.
- Saves clean, defensible processed dataset.
"""

import os
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List
from ml.aqi_calculator import calculate_overall_aqi, calculate_sub_index


COLUMN_MAPPING = {
    'Station ID': 'station_id',
    'State': 'state',
    'City': 'city',
    'Station Name': 'station_name',
    'Timestamp': 'timestamp',
    'PM2.5 (g/m)': 'pm25',
    'PM2.5 (µg/m³)': 'pm25',
    'PM10 (g/m)': 'pm10',
    'PM10 (µg/m³)': 'pm10',
    'NO (g/m)': 'no',
    'NO (µg/m³)': 'no',
    'NO2 (g/m)': 'no2',
    'NO2 (µg/m³)': 'no2',
    'NOx (ppb)': 'nox',
    'NH3 (g/m)': 'nh3',
    'NH3 (µg/m³)': 'nh3',
    'SO2 (g/m)': 'so2',
    'SO2 (µg/m³)': 'so2',
    'CO (mg/m)': 'co',
    'CO (mg/m³)': 'co',
    'Ozone (g/m)': 'ozone',
    'Ozone (µg/m³)': 'ozone',
    'Benzene (g/m)': 'benzene',
    'Benzene (µg/m³)': 'benzene',
    'Eth-Benzene (g/m)': 'eth_benzene',
    'Eth-Benzene (µg/m³)': 'eth_benzene',
    'MP-Xylene (g/m)': 'mp_xylene',
    'MP-Xylene (µg/m³)': 'mp_xylene',
    'RH (%)': 'rh',
    'WS (m/s)': 'ws',
    'WD (deg)': 'wd',
    'RF (mm)': 'rf',
    'TOT-RF (mm)': 'tot_rf',
    'SR (W/mt2)': 'sr',
    'BP (mmHg)': 'bp',
}

# 100% empty / unviable columns to drop
DROP_COLUMNS = [
    'VWS (m/s)', 'O Xylene (g/m)', 'AT (C)', 'Toluene (g/m)', 'Xylene (g/m)', 'BP (mmHg)',
    'vws', 'o_xylene', 'at', 'toluene', 'xylene', 'bp'
]

# Physical range bounds for scientific validation
PHYSICAL_BOUNDS = {
    'pm25': (0.0, 1000.0),
    'pm10': (0.0, 1500.0),
    'no': (0.0, 1000.0),
    'no2': (0.0, 800.0),
    'nox': (0.0, 1000.0),
    'nh3': (0.0, 2000.0),
    'so2': (0.0, 1500.0),
    'co': (0.0, 100.0),
    'ozone': (0.0, 1000.0),
    'benzene': (0.0, 500.0),
    'eth_benzene': (0.0, 500.0),
    'mp_xylene': (0.0, 500.0),
    'rh': (0.0, 100.0),
    'ws': (0.0, 60.0),
    'wd': (0.0, 360.0),
    'rf': (0.0, 500.0),
    'tot_rf': (0.0, 5000.0),
    'sr': (0.0, 1500.0),
}


def load_and_standardize(raw_csv_path: str) -> pd.DataFrame:
    """Loads raw CSV, cleans column names, and drops 100% empty / unviable columns."""
    df = pd.read_csv(raw_csv_path)
    
    # Rename columns to standard identifiers
    new_cols = {}
    for col in df.columns:
        clean_col = col.strip()
        if clean_col in COLUMN_MAPPING:
            new_cols[col] = COLUMN_MAPPING[clean_col]
        else:
            normalized = clean_col.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')
            new_cols[col] = normalized
            
    df = df.rename(columns=new_cols)

    # Drop explicitly identified empty/unusable columns and any fully null columns
    cols_to_drop = [c for c in df.columns if c in DROP_COLUMNS or df[c].isnull().all()]
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)

    return df


def validate_and_clean_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Drops corrupted timestamp rows and parses datetime strictly."""
    # Drop rows where timestamp is null
    df = df.dropna(subset=['timestamp']).copy()
    
    # Parse timestamps with mixed dayfirst format
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', dayfirst=True, errors='coerce')
    df = df.dropna(subset=['timestamp'])
    
    # Sort chronologically
    df = df.sort_values(by=['station_id', 'timestamp'] if 'station_id' in df.columns else ['timestamp'])
    df = df.drop_duplicates(subset=['timestamp'])
    df = df.reset_index(drop=True)
    return df


def clean_sensor_measurements(df: pd.DataFrame, max_interpolation_gap: int = 4) -> pd.DataFrame:
    """
    Applies physical bounds and time-aware interpolation strictly for short continuous gaps.
    max_interpolation_gap=4 corresponds to 1 hour (4 x 15-min intervals).
    Long sensor outages remain missing (NaN) rather than being fabricated.
    """
    df = df.copy()
    numeric_cols = [c for c in df.columns if c in PHYSICAL_BOUNDS]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        min_val, max_val = PHYSICAL_BOUNDS[col]
        # Set physically impossible values to NaN
        df.loc[(df[col] < min_val) | (df[col] > max_val), col] = np.nan

        # Time-aware linear interpolation strictly for short gaps (limit=4)
        df[col] = df[col].interpolate(method='linear', limit=max_interpolation_gap, limit_direction='forward')

    # Remove any columns that ended up 100% missing after bounds check
    empty_cols = [c for c in df.columns if df[c].isnull().all()]
    if empty_cols:
        df = df.drop(columns=empty_cols)

    return df


def compute_dataset_aqi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes standard 24-hr and 8-hr rolling averages and overall CPCB AQI per record.
    Initial rows will naturally have NaNs for rolling averages when insufficient historical steps exist.
    """
    df = df.copy()
    
    # 24-hr rolling averages (96 periods of 15m) for PM2.5, PM10, NO2, SO2, NH3
    # 8-hr rolling averages (32 periods of 15m) for CO, Ozone
    rolling_24h_cols = ['pm25', 'pm10', 'no2', 'so2', 'nh3']
    rolling_8h_cols = ['co', 'ozone']

    for col in rolling_24h_cols:
        if col in df.columns:
            df[f'{col}_24h_avg'] = df[col].rolling(window=96, min_periods=12).mean()

    for col in rolling_8h_cols:
        if col in df.columns:
            df[f'{col}_8h_avg'] = df[col].rolling(window=32, min_periods=4).mean()

    # Calculate overall AQI row by row using official CPCB sub-index logic
    aqi_values = []
    aqi_categories = []
    dominant_pollutants = []

    for _, row in df.iterrows():
        pollutant_dict = {}
        for p in ['pm25', 'pm10', 'no2', 'so2', 'nh3']:
            avg_col = f'{p}_24h_avg'
            val = row.get(avg_col) if pd.notnull(row.get(avg_col)) else row.get(p)
            if pd.notnull(val):
                pollutant_dict[p] = float(val)

        for p in ['co', 'ozone']:
            avg_col = f'{p}_8h_avg'
            val = row.get(avg_col) if pd.notnull(row.get(avg_col)) else row.get(p)
            if pd.notnull(val):
                pollutant_dict[p] = float(val)

        result = calculate_overall_aqi(pollutant_dict, enforce_cpcb_rule=False)
        aqi_values.append(result['aqi'])
        aqi_categories.append(result['category'])
        dominant_pollutants.append(result['dominant_pollutant'])

    df['aqi'] = aqi_values
    df['aqi_category'] = aqi_categories
    df['dominant_pollutant'] = dominant_pollutants

    return df


def run_preprocessing_pipeline(raw_path: str, processed_path: str) -> pd.DataFrame:
    """Runs complete end-to-end preprocessing."""
    print(f"Loading raw dataset from {raw_path}...")
    df = load_and_standardize(raw_path)
    print(f"Standardized shape: {df.shape}")

    print("Cleaning timestamps...")
    df = validate_and_clean_timestamps(df)
    print(f"Timestamp validated shape: {df.shape}")

    print("Cleaning sensor measurements and interpolating short gaps...")
    df = clean_sensor_measurements(df, max_interpolation_gap=4)

    print("Computing CPCB rolling concentrations and AQI...")
    df = compute_dataset_aqi(df)

    # Final check: drop any column that is 100% missing
    all_null_cols = [c for c in df.columns if df[c].isnull().all()]
    if all_null_cols:
        print(f"Dropping 100% empty columns from final dataset: {all_null_cols}")
        df = df.drop(columns=all_null_cols)

    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    df.to_csv(processed_path, index=False)
    print(f"Successfully saved clean dataset to {processed_path} (Shape: {df.shape})")
    return df


if __name__ == '__main__':
    raw_file = r'C:\prasunethon\data\raw\del-dtu-cpcb-2024-25.csv'
    clean_file = r'C:\prasunethon\data\processed\cleaned_cpcb_dtu.csv'
    run_preprocessing_pipeline(raw_file, clean_file)
