# AeroGuard Installation & Quickstart Guide

## Prerequisites
- Python 3.10+ (or Python 3.14)
- Node.js 18+ & npm
- PostgreSQL 14+ (or SQLite fallback)

## 1. Environment Setup

```bash
# Clone or navigate to the project directory
cd c:\data

# Configure environment variables
cp .env.example .env

# Install Python dependencies
pip install -r requirements.txt
```

## 2. Preprocess Dataset & Train Models

```bash
# 1. Run Data Preprocessing on Delhi CPCB Dataset
python -m ml.preprocessing

# 2. Train and Benchmark AI Models (Baseline, Random Forest, PyTorch LSTM)
python -m ml.evaluation

# 3. Seed Database
python -m database.seed
```

## 3. Run FastAPI Backend

```bash
# Start backend server on port 8000
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive Swagger API documentation is available at `http://localhost:8000/docs`.

## 4. Run Next.js Frontend Dashboard

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```
Open `http://localhost:3000` in your web browser.

## 5. Run IoT Simulator (Optional)

```bash
# Stream live multi-node telemetry to backend
python -m iot.simulator.simulator --interval 4 --cycles 10
```
