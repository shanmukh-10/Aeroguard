# AeroGuard Production Deployment Guide

This guide details the step-by-step procedure to deploy the complete **AeroGuard** platform:
- **Backend**: FastAPI REST API + Machine Learning Inference on **Render** (or Railway / AWS)
- **Database**: Managed **PostgreSQL** on Render (with automatic schema provisioning & initial seeding)
- **Frontend**: Next.js 14 Web GIS Dashboard on **Vercel**

---

## 1. Backend & PostgreSQL Deployment (Render)

### Step 1: Create a Managed PostgreSQL Database on Render
1. In the [Render Dashboard](https://dashboard.render.com/), click **New +** → **PostgreSQL**.
2. **Name**: `aeroguard-db`
3. **Database**: `aeroguard`
4. **User**: `postgres` (or default generated user)
5. **Region**: Singapore or Frankfurt (choose the region closest to your users)
6. **Plan**: Free (or Starter)
7. Click **Create Database**.
8. Once provisioned, copy the **Internal Database URL** (or External Database URL).

---

### Step 2: Create a Web Service for the FastAPI Backend
1. In Render Dashboard, click **New +** → **Web Service**.
2. Connect your GitHub repository: `https://github.com/shanmukh-10/Aeroguard`.
3. Configure the service settings:
   - **Name**: `aeroguard-backend`
   - **Region**: Same region as your database
   - **Branch**: `main`
   - **Root Directory**: *(leave blank)*
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn backend.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type**: Free (or Starter)

4. **Environment Variables**:
   | Variable Name | Value / Description |
   | :--- | :--- |
   | `DATABASE_URL` | *Paste the Render PostgreSQL connection string* (e.g. `postgresql://user:pass@host/aeroguard`) |
   | `ENVIRONMENT` | `production` |
   | `CORS_ORIGINS` | `*` (or your frontend Vercel domain e.g. `https://aeroguard.vercel.app`) |

5. Click **Deploy Web Service**.
6. On startup, AeroGuard's lifespan manager automatically connects to PostgreSQL, creates all tables (`init_db()`), and seeds initial CAAQMS stations, IoT sensors, baseline historical records, and hotspots (`seed_database()`).
7. Once deployed, note your backend URL:
   `https://aeroguard-backend.onrender.com`

---

## 2. Frontend Deployment (Vercel)

### Step 1: Import Project to Vercel
1. Go to [Vercel Dashboard](https://vercel.com/new).
2. Click **Import** next to your GitHub repository `shanmukh-10/Aeroguard`.
3. Configure Project:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: Click *Edit* and select **`frontend`**
   - **Build Command**: `npm run build` (or Next.js default)
   - **Output Directory**: `.next` (default)
   - **Install Command**: `npm install` (default)

### Step 2: Set Environment Variables
Add the following environment variable:
| Variable Name | Value |
| :--- | :--- |
| `NEXT_PUBLIC_API_URL` | `https://<your-render-backend-name>.onrender.com/api` |

*(Example: `https://aeroguard-backend.onrender.com/api`)*

### Step 3: Deploy
1. Click **Deploy**.
2. Vercel will build the Next.js production bundle and deploy the web dashboard.
3. Access your live application at `https://aeroguard.vercel.app`.

---

## 3. IoT Telemetry Streaming

The IoT simulator (`iot/simulator/simulator.py`) runs locally or as an edge gateway worker:
```bash
python iot/simulator/simulator.py
```
To stream live telemetry from physical ESP32 devices or edge simulators to the production backend:
Set the target endpoint in `iot/sensor_code/esp32_firmware.ino` or `iot/simulator/simulator.py` to:
`https://aeroguard-backend.onrender.com/api/sensors/data`
