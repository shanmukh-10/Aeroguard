"""
AeroGuard Deep Learning Forecaster (LSTM)
------------------------------------------
Implements a multi-layer Long Short-Term Memory (LSTM) neural network using PyTorch
for temporal sequence forecasting of future PM2.5 concentrations.
"""

import os
import time
import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from typing import Dict, Any, Tuple, List
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class TimeSeriesDataset(Dataset):
    """Sliding window sequence dataset for PyTorch."""
    def __init__(self, X: np.ndarray, y: np.ndarray, seq_len: int = 16):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)
        self.seq_len = seq_len

    def __len__(self):
        return len(self.X) - self.seq_len

    def __getitem__(self, idx):
        return (
            self.X[idx : idx + self.seq_len],
            self.y[idx + self.seq_len]
        )


class AeroGuardLSTM(nn.Module):
    """
    2-Layer LSTM with Dropout and Dense output head for regression.
    """
    def __init__(self, input_dim: int, hidden_dim: int = 64, num_layers: int = 2, dropout: float = 0.2):
        super(AeroGuardLSTM, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        # x: (batch_size, seq_len, input_dim)
        lstm_out, _ = self.lstm(x)
        # Take the output of the last time step
        last_step = lstm_out[:, -1, :]
        out = self.fc(last_step)
        return out.squeeze(-1)


def train_lstm_model(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_cols: List[str],
    target_col: str = 'target_pm25_2h',
    seq_len: int = 16,
    epochs: int = 15,
    batch_size: int = 128,
    learning_rate: float = 0.001,
    model_save_path: str = 'models/lstm_pm25.pt',
    scaler_save_path: str = 'models/scaler.joblib'
) -> Tuple[Dict[str, Any], np.ndarray, nn.Module]:
    """
    Normalizes features, trains PyTorch LSTM model with early stopping, evaluates on test set.
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Training PyTorch LSTM on device: {device}")

    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(train_df[feature_cols].values)
    y_train = train_df[target_col].values

    X_test_scaled = scaler.transform(test_df[feature_cols].values)
    y_test = test_df[target_col].values

    # Build datasets and dataloaders
    train_dataset = TimeSeriesDataset(X_train_scaled, y_train, seq_len=seq_len)
    test_dataset = TimeSeriesDataset(X_test_scaled, y_test, seq_len=seq_len)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    model = AeroGuardLSTM(input_dim=len(feature_cols), hidden_dim=64, num_layers=2, dropout=0.2).to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-5)

    start_train = time.time()
    best_loss = float('inf')
    best_weights = None

    print(f"Starting LSTM training for {epochs} epochs...")
    for epoch in range(1, epochs + 1):
        model.train()
        total_train_loss = 0.0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            preds = model(batch_x)
            loss = criterion(preds, batch_y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            total_train_loss += loss.item() * len(batch_y)

        avg_train_loss = total_train_loss / len(train_dataset)

        # Validation on test loader
        model.eval()
        total_val_loss = 0.0
        with torch.no_grad():
            for val_x, val_y in test_loader:
                val_x, val_y = val_x.to(device), val_y.to(device)
                val_preds = model(val_x)
                val_loss = criterion(val_preds, val_y)
                total_val_loss += val_loss.item() * len(val_y)
        avg_val_loss = total_val_loss / len(test_dataset)

        if avg_val_loss < best_loss:
            best_loss = avg_val_loss
            best_weights = model.state_dict().copy()

        if epoch % 3 == 0 or epoch == epochs:
            print(f"Epoch [{epoch}/{epochs}] - Train Loss (MSE): {avg_train_loss:.2f} | Val Loss: {avg_val_loss:.2f}")

    training_time = time.time() - start_train
    if best_weights is not None:
        model.load_state_dict(best_weights)

    # Final Inference Evaluation
    model.eval()
    all_preds = []
    all_targets = []
    start_infer = time.time()
    with torch.no_grad():
        for test_x, test_y in test_loader:
            test_x = test_x.to(device)
            preds = model(test_x)
            all_preds.extend(preds.cpu().numpy().tolist())
            all_targets.extend(test_y.numpy().tolist())

    y_pred_arr = np.clip(np.array(all_preds), a_min=0.0, a_max=None)
    y_test_arr = np.array(all_targets)
    inference_time = (time.time() - start_infer) / len(y_test_arr)

    mae = float(mean_absolute_error(y_test_arr, y_pred_arr))
    rmse = float(np.sqrt(mean_squared_error(y_test_arr, y_pred_arr)))
    r2 = float(r2_score(y_test_arr, y_pred_arr))

    metrics = {
        "model_name": "LSTM Neural Network",
        "mae": round(mae, 3),
        "rmse": round(rmse, 3),
        "r2": round(r2, 4),
        "training_time_seconds": round(training_time, 2),
        "inference_latency_ms": round(inference_time * 1000, 4),
        "sample_count": int(len(y_test_arr)),
        "epochs": epochs
    }
    print(f"[LSTM] MAE: {mae:.3f} | RMSE: {rmse:.3f} | R²: {r2:.4f}")

    # Save artifacts
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    torch.save({
        'state_dict': model.state_dict(),
        'input_dim': len(feature_cols),
        'hidden_dim': 64,
        'num_layers': 2,
        'seq_len': seq_len,
        'feature_cols': feature_cols,
        'target_col': target_col,
        'metrics': metrics
    }, model_save_path)

    joblib.dump(scaler, scaler_save_path)
    print(f"Saved LSTM weights to {model_save_path} and Scaler to {scaler_save_path}")

    return metrics, y_pred_arr, model
