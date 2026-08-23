# AeroGuard — AI + IoT Platform for Predicting and Preventing Pollution Risks

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.2+-EE4C2C.svg)](https://pytorch.org/)
[![CPCB Standard](https://img.shields.io/badge/AQI-CPCB%20National%20Standard-emerald.svg)](https://cpcb.nic.in/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Team Name**: Victory Vanguard  
> **Team Member**: Shanmukha Reddy  
> **Domain**: Air Pollution + Artificial Intelligence + IoT + Machine Learning + Public Health + Smart Cities + Environmental Intelligence

---

## 1. Problem Statement & Core Value Proposition

Air pollution causes millions of premature deaths globally each year and exacerbates cardiovascular and respiratory illnesses. While traditional regulatory-grade Continuous Ambient Air Quality Monitoring Stations (CAAQMS) provide high accuracy, their sparse geographical deployment and high capital cost leave vast urban and peri-urban areas without hyperlocal visibility or predictive foresight.

Citizens and civic authorities face critical unanswered questions:
- *What is the actual air quality in my micro-neighborhood right now?*
- *Is pollution increasing or decreasing over the next few hours?*
- *Is an acute pollution hotspot forming upstream?*
- *What actionable, preventive steps should vulnerable individuals take before air quality deteriorates?*

### AeroGuard Solution:
**AeroGuard** is a **Complementary AIoT Intelligence Layer** that bridges this gap. By fusing high-accuracy reference CAAQMS stations, low-cost distributed IoT sensors (ESP32 + PMS5003 + DHT22), time-series machine learning models, stoichiometric source-pattern analysis, and automated alerting, AeroGuard transforms fragmented sensor data into proactive, actionable environmental intelligence.

```
RAW SENSOR TELEMETRY 
  ↓ 
VALIDATION & BOUNDS FILTERING 
  ↓ 
TIME-AWARE INTERPOLATION & ROLLING AVERAGES 
  ↓ 
OFFICIAL CPCB AQI SUB-INDEX CALCULATION 
  ↓ 
AI MULTI-STEP FORECASTING (Random Forest / PyTorch LSTM) 
  ↓ 
HOTSPOT DETECTION & STOICHIOMETRIC SOURCE PATTERN ANALYSIS 
  ↓ 
AUTOMATED PREVENTIVE ALERTS & HEALTH ADVISORIES 
  ↓ 
INTERACTIVE NEXT.JS DASHBOARD & GEOSPATIAL MAP
```

> [!IMPORTANT]
> **Regulatory Positioning**: AeroGuard is designed as a *complementary intelligence and forecasting layer* to expand spatial coverage and accessibility. It does not replace regulatory government monitoring stations.

---

## 2. Key Features

1. **Hyperlocal Live Monitoring**: Real-time continuous stream of $\text{PM}_{2.5}$, $\text{PM}_{10}$, $\text{NO}_2$, $\text{SO}_2$, $\text{CO}$, $\text{O}_3$, $\text{NH}_3$, ambient temperature, relative humidity, wind speed, and wind direction.
2. **Official Indian CPCB AQI Engine**: Strict adherence to the Central Pollution Control Board 8-pollutant sub-index formulas and averaging periods (24-hr for particulate/gases, 8-hr for CO/Ozone).
3. **AI Multi-Step Forecasting**: Neural sequence and ensemble forecasters predicting future $\text{PM}_{2.5}$ and AQI up to 24 hours ahead.
4. **Geospatial Hotspot Detection**: Real-time identification of acute localized pollution pockets with trend projection (Increasing / Stable / Decreasing).
5. **Likely Source-Pattern Analysis**: Inferred emission signatures (Traffic, Industrial, Construction Dust, Regional Background) based on stoichiometric pollutant ratios ($\text{PM}_{2.5}/\text{PM}_{10}$, $\text{NO}_2/\text{SO}_2$, $\text{CO}$) and boundary-layer meteorological dispersion.
6. **Automated Alert Engine**: Real-time early-warning alerts triggered by threshold breaches and rapid rate-of-change surges ($>35\ \mu\text{g/m}^3\text{/hr}$).
7. **Evidence-Based Health Advisories**: Official CPCB precautions tailored for both the general public and sensitive high-risk groups (children, asthmatics, elderly).
8. **Historical Analytics Explorer**: Interactive 24-hour, 7-day, and 30-day multi-pollutant trajectory visualizations with summary statistics.
9. **IoT Sensor Ingestion & Simulator**: High-throughput REST API (`POST /api/sensors/data`) supporting physical ESP32 nodes and multi-node Python simulation.

---

## 3. Dataset Profile & Data Engineering (Delhi DTU-CPCB 2024–2025)

The platform is trained and validated on the official Delhi Technological University (DTU) CPCB air-quality dataset:
- **Station**: `site_118` — DTU, Shahbad Daulatpur, Bawana Road, North Delhi (28.750075°N, 77.111261°E).
- **Timeframe**: January 1, 2024 to December 31, 2025 (2 Full Calendar Years).
- **Temporal Resolution**: 15-minute continuous observations (70,176 valid rows after dropping 1 corrupted timestamp row).

### Cleaning & Validation Policies
- **100% Empty Columns Dropped**: `VWS`, `O Xylene`, `AT`, `Toluene`, `Xylene`.
- **Physical Bounds Verification**: Out-of-bounds readings ($\text{PM}_{2.5} < 0$ or $> 1000\ \mu\text{g/m}^3$, $\text{RH} < 0\%$ or $> 100\%$) marked invalid.
- **Time-Aware Interpolation**: Short continuous gaps ($\le 4$ intervals / 1 hour) interpolated via time-aware linear interpolation; long sensor outages preserved as missing.
- **Zero Future Leakage**: Chronological split (80% Train: Jan 2024 – Aug 2025; 20% Test: Aug 2025 – Dec 2025).

---

## 4. CPCB AQI Calculation Methodology

Pollutant sub-index $I_p$ is calculated via standard linear interpolation:

$$I_p = I_{low} + \frac{I_{high} - I_{low}}{B_{high} - B_{low}} \times (C_p - B_{low})$$

$$\text{Overall AQI} = \max\left(I_{\text{PM2.5}}, I_{\text{PM10}}, I_{\text{NO2}}, I_{\text{SO2}}, I_{\text{CO}}, I_{\text{O3}}, I_{\text{NH3}}\right)$$

### Official Breakpoint Table
| Category | AQI Range | Color | PM2.5 (24h) | PM10 (24h) | NO2 (24h) | SO2 (24h) | CO (8h) | O3 (8h) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Good** | 0 - 50 | `#10B981` | 0 - 30 | 0 - 50 | 0 - 40 | 0 - 40 | 0 - 1.0 | 0 - 50 |
| **Satisfactory** | 51 - 100 | `#84CC16` | 31 - 60 | 51 - 100 | 41 - 80 | 41 - 80 | 1.1 - 2.0 | 51 - 100 |
| **Moderate** | 101 - 200 | `#EAB308` | 61 - 90 | 101 - 250 | 81 - 180 | 81 - 380 | 2.1 - 10 | 101 - 168 |
| **Poor** | 201 - 300 | `#F97316` | 91 - 120 | 251 - 350 | 181 - 280 | 381 - 800 | 10.1 - 17 | 169 - 208 |
| **Very Poor** | 301 - 400 | `#EF4444` | 121 - 250 | 351 - 430 | 281 - 400 | 801 - 1600 | 17.1 - 34 | 209 - 748 |
| **Severe** | 401 - 500 | `#881337` | 250+ | 430+ | 400+ | 1600+ | 34+ | 748+ |

---

## 5. Machine Learning Benchmarks & Validation Results

Evaluated on **12,776 unseen continuous test observations** (August – December 2025):

| Model Architecture | Target Horizon | MAE ($\mu\text{g/m}^3$) | RMSE ($\mu\text{g/m}^3$) | $R^2$ Score | Inference Latency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Persistence Baseline** | 2 Hours Ahead | 30.468 | 60.895 | 0.7629 | < 0.01 ms |
| **Random Forest Regressor** | 2 Hours Ahead | **38.009** | 74.020 | 0.6496 | 0.006 ms |
| **PyTorch Deep LSTM** | 2 Hours Ahead | 49.330 | 94.284 | 0.4318 | 0.046 ms |

*Empirical finding: In 15-minute discrete time-series, persistence baseline provides a strong short-term benchmark, with Random Forest capturing diurnal cyclical patterns across multi-hour projections.*

---

## 6. System Architecture & Tech Stack

```
[ IoT Nodes ESP32 ] ──(HTTP POST)──> [ FastAPI REST Engine ] ──> [ PostgreSQL / SQLite ]
                                              │                         │
                                     [ AI/ML Forecast Hub ] <───────────┘
                                              │
                                     [ Next.js Dashboard ]
                                       ├── Live AQI Cards
                                       ├── Recharts Forecast
                                       ├── Leaflet Map
                                       ├── Hotspot Matrix
                                       └── Source Analysis
```

- **Backend**: Python 3.14, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.0.
- **Database**: PostgreSQL 14+/18 (with SQLite auto-fallback).
- **AI/ML**: PyTorch 2.2+, Scikit-Learn, Pandas, NumPy, Joblib.
- **Frontend**: Next.js 14 (App Router), React 18, Tailwind CSS, Lucide Icons, Recharts, Leaflet.
- **IoT Layer**: Arduino / ESP32 C++ firmware (`PMS5003` laser PM sensor, `DHT22`, `MQ135`), Python multi-node telemetry simulator.

---

## 7. Quickstart & Installation Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- PostgreSQL (or local SQLite)

### Step 1: Clone and Configure Environment
```bash
cd c:\data
cp .env.example .env
pip install -r requirements.txt
```

### Step 2: Run Data Preprocessing & Model Training
```bash
# 1. Clean raw CPCB dataset
python -m ml.preprocessing

# 2. Train and benchmark AI models
python -m ml.evaluation

# 3. Initialize and seed database
python -m database.seed
```

### Step 3: Launch FastAPI Backend
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation: `http://localhost:8000/docs`

### Step 4: Launch Next.js Frontend
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```
Open `http://localhost:3000` in your web browser.

### Step 5: Run IoT Telemetry Simulator (Optional)
```bash
# In a separate terminal
python -m iot.simulator.simulator --interval 4 --cycles 10
```

---

## 8. Presentation Slides Outline (Hackathon Ready)

- **Slide 1 — Title & Problem**: AeroGuard AIoT Environmental Intelligence; tackling hyperlocal air pollution blindspots across Delhi NCR.
- **Slide 2 — Solution & Innovation**: Complete pipeline from ESP32 edge telemetry to CPCB sub-indices, AI multi-step forecasting, and automated alerts.
- **Slide 3 — Technical Architecture**: Robust FastAPI backend, PostgreSQL database, PyTorch/Scikit-Learn models, Next.js frontend.
- **Slide 4 — Feasibility & Scalability**: Low-cost modular IoT expansion, zero future-leakage ML validation, complementary CPCB positioning.
- **Slide 5 — Actual Measured Results**: 70,176 validated records, empirical MAE/RMSE comparisons, real-time alert triggering.
- **Slide 6 — Research & Roadmap**: Edge AI quantization, city-scale dispersion modelling, integration with municipal smart-city dashboards.

---

## 9. 2–3 Minute Demonstration Script

- **0:00–0:30 (Problem & Intro)**: Introduce AeroGuard by Team Victory Vanguard. Explain why regulatory CAAQMS stations need a complementary hyperlocal AIoT layer.
- **0:30–1:00 (Live Dashboard & AQI)**: Show the AeroGuard hero screen with real-time CPCB AQI (215 Poor), dominant pollutant breakdown ($\text{PM}_{2.5}$ 94.2 $\mu\text{g/m}^3$), and evidence-based health advisories.
- **1:00–1:40 (AI Forecast & Map)**: Demonstrate the multi-step 12-hour forecast chart, empirical benchmark table, and interactive Leaflet map featuring Delhi CAAQMS stations and IoT nodes.
- **1:40–2:15 (Hotspots & Source Analysis)**: Highlight active hotspots (Bawana Industrial, Anand Vihar) and stoichiometric source-pattern analysis (Traffic vs Industrial).
- **2:15–2:45 (Live IoT Telemetry Stream)**: Run `python -m iot.simulator.simulator --inject-spike` to stream live packets, showing immediate AQI re-calculation and automated critical alert triggering on the dashboard.
- **2:45–3:00 (Conclusion)**: Reiterate scalable public health impact and smart-city readiness.

---

## 10. License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
