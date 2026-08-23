# Delhi DTU–CPCB Air Quality Dataset Profile (2024–2025)

## 1. Dataset Provenance
- **Source**: Central Pollution Control Board (CPCB), Ministry of Environment, Forest and Climate Change, Government of India.
- **Monitoring Station**: `site_118` — Delhi Technological University (DTU), Shahbad Daulatpur, Bawana Road, North Delhi (Latitude: 28.750075°N, Longitude: 77.111261°E).
- **Timeframe**: January 1, 2024, 00:00 UTC to December 31, 2025, 23:45 UTC (2 Full Calendar Years).
- **Sampling Frequency**: Exactly 15 minutes (70,176 valid continuous time intervals).

## 2. Missing Value Analysis & Cleaning Decisions

| Parameter | Raw Column | Initial Missingness | Policy / Cleaning Decision |
| :--- | :--- | :--- | :--- |
| **PM2.5** | `PM2.5 (µg/m³)` | 7.21% | Retained. Time-aware interpolation for gaps $\le 1$ hour. |
| **PM10** | `PM10 (µg/m³)` | 8.31% | Retained. Short-gap linear interpolation. |
| **NO2** | `NO2 (µg/m³)` | 3.82% | Retained. Short-gap linear interpolation. |
| **NH3** | `NH3 (µg/m³)` | 3.37% | Retained. Short-gap linear interpolation. |
| **SO2** | `SO2 (µg/m³)` | 2.25% | Retained. Short-gap linear interpolation. |
| **CO** | `CO (mg/m³)` | 1.69% | Retained. Short-gap linear interpolation. |
| **Ozone** | `Ozone (µg/m³)` | 2.52% | Retained. Short-gap linear interpolation. |
| **RH** | `RH (%)` | 5.18% | Retained. Bounded between 0% and 100%. |
| **WD** | `WD (deg)` | 6.73% | Cyclical sine/cosine transformation. |
| **WS** | `WS (m/s)` | 41.94% | Forward-filled with seasonal medians where missing. |
| **BP** | `BP (mmHg)` | 98.24% | Excluded from regression feature set due to extreme sparsity. |
| **VWS, AT, Toluene, Xylene, O-Xylene** | Multiple | **100.00%** | **Dropped entirely** (contain zero usable information). |

## 3. Chronological Train-Test Split (Zero Future Leakage)
- **Training Set (80%)**: 51,103 observations (January 2, 2024 to August 7, 2025).
- **Test Set (20%)**: 12,776 observations (August 7, 2025 to December 31, 2025).
- **Evaluation Rule**: Models are evaluated strictly on unseen future timestamps without random shuffling.
