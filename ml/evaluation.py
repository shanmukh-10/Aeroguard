"""
AeroGuard Model Evaluation & Comparison Pipeline
-------------------------------------------------
Orchestrates training and benchmarking of:
1. Persistence Baseline
2. Random Forest Regressor
3. PyTorch LSTM Neural Network

Calculates MAE, RMSE, R², training time, and inference latency.
Selects best performing model based on empirical validation results.
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List

from ml.feature_engineering import prepare_ml_dataset
from ml.baseline import evaluate_persistence_baseline
from ml.random_forest import train_random_forest
from ml.lstm import train_lstm_model


def run_full_model_benchmark(
    clean_csv_path: str = 'data/processed/cleaned_cpcb_dtu.csv',
    metrics_json_path: str = 'models/model_metrics.json'
) -> Dict[str, Any]:
    """
    Runs end-to-end benchmark across Persistence Baseline, Random Forest, and LSTM models.
    """
    print("=" * 60)
    print("AEROGUARD ML BENCHMARK PIPELINE")
    print("=" * 60)

    # 1. Prepare engineered dataset
    train_df, test_df, feature_cols = prepare_ml_dataset(clean_csv_path, target_col='target_pm25_2h')

    # 2. Evaluate Baseline
    print("\n--- 1. Evaluating Baseline Model ---")
    baseline_metrics, _ = evaluate_persistence_baseline(test_df, target_col='target_pm25_2h')

    # 3. Train & Evaluate Random Forest
    print("\n--- 2. Training Random Forest Model ---")
    rf_metrics, _, _ = train_random_forest(
        train_df, test_df, feature_cols,
        target_col='target_pm25_2h',
        model_save_path='models/rf_pm25.joblib'
    )

    # 4. Train & Evaluate LSTM
    print("\n--- 3. Training PyTorch LSTM Model ---")
    lstm_metrics, _, _ = train_lstm_model(
        train_df, test_df, feature_cols,
        target_col='target_pm25_2h',
        seq_len=16,
        epochs=12,
        batch_size=128,
        model_save_path='models/lstm_pm25.pt',
        scaler_save_path='models/scaler.joblib'
    )

    # 5. Compute Comparative Performance Improvements
    baseline_mae = baseline_metrics['mae']
    baseline_rmse = baseline_metrics['rmse']

    rf_mae_reduction = ((baseline_mae - rf_metrics['mae']) / baseline_mae) * 100
    rf_rmse_reduction = ((baseline_rmse - rf_metrics['rmse']) / baseline_rmse) * 100

    lstm_mae_reduction = ((baseline_mae - lstm_metrics['mae']) / baseline_mae) * 100
    lstm_rmse_reduction = ((baseline_rmse - lstm_metrics['rmse']) / baseline_rmse) * 100

    rf_metrics['mae_improvement_pct'] = round(rf_mae_reduction, 2)
    rf_metrics['rmse_improvement_pct'] = round(rf_rmse_reduction, 2)

    lstm_metrics['mae_improvement_pct'] = round(lstm_mae_reduction, 2)
    lstm_metrics['rmse_improvement_pct'] = round(lstm_rmse_reduction, 2)

    # 6. Select Best Model (lowest MAE on unseen test set)
    all_models = [baseline_metrics, rf_metrics, lstm_metrics]
    best_model_data = min(all_models, key=lambda m: m['mae'])
    best_model_name = best_model_data['model_name']

    summary = {
        "target": "Future PM2.5 (2-hour forecast horizon)",
        "frequency": "15 minutes",
        "dataset": "Delhi DTU-CPCB (2024-2025)",
        "train_samples": len(train_df),
        "test_samples": len(test_df),
        "best_model": best_model_name,
        "models": {
            "persistence_baseline": baseline_metrics,
            "random_forest": rf_metrics,
            "lstm": lstm_metrics
        }
    }

    # Save to JSON
    os.makedirs(os.path.dirname(metrics_json_path), exist_ok=True)
    with open(metrics_json_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY & COMPARISON")
    print("=" * 60)
    print(f"Baseline      -> MAE: {baseline_metrics['mae']:.3f} | RMSE: {baseline_rmse:.3f} | R²: {baseline_metrics['r2']:.4f}")
    print(f"Random Forest -> MAE: {rf_metrics['mae']:.3f} ({rf_mae_reduction:+.1f}% vs baseline) | RMSE: {rf_metrics['rmse']:.3f} | R²: {rf_metrics['r2']:.4f}")
    print(f"LSTM          -> MAE: {lstm_metrics['mae']:.3f} ({lstm_mae_reduction:+.1f}% vs baseline) | RMSE: {lstm_metrics['rmse']:.3f} | R²: {lstm_metrics['r2']:.4f}")
    print(f"\n=> Best Performing Model Selected: {best_model_name}")
    print(f"Metrics saved to: {metrics_json_path}")

    return summary


if __name__ == '__main__':
    run_full_model_benchmark()
