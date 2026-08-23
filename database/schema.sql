-- AeroGuard PostgreSQL Database Schema DDL
-- Platform: PostgreSQL 14+ / PostgreSQL 18
-- Database Name: aeroguard

CREATE TABLE IF NOT EXISTS stations (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL DEFAULT 'Delhi',
    state VARCHAR(100) NOT NULL DEFAULT 'Delhi',
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    station_type VARCHAR(100) DEFAULT 'CAAQMS',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sensors (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    hardware_type VARCHAR(100) DEFAULT 'ESP32 + PMS5003 + DHT22',
    status VARCHAR(50) DEFAULT 'ONLINE',
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    battery_level DOUBLE PRECISION DEFAULT 100.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS air_quality_records (
    id BIGSERIAL PRIMARY KEY,
    station_id VARCHAR(64) REFERENCES stations(id) ON DELETE SET NULL,
    sensor_id VARCHAR(64) REFERENCES sensors(id) ON DELETE SET NULL,
    location VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    pm25 DOUBLE PRECISION,
    pm10 DOUBLE PRECISION,
    no DOUBLE PRECISION,
    no2 DOUBLE PRECISION,
    nox DOUBLE PRECISION,
    nh3 DOUBLE PRECISION,
    so2 DOUBLE PRECISION,
    co DOUBLE PRECISION,
    ozone DOUBLE PRECISION,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    wind_speed DOUBLE PRECISION,
    wind_direction DOUBLE PRECISION,
    aqi INTEGER,
    aqi_category VARCHAR(50),
    dominant_pollutant VARCHAR(50),
    is_simulated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_aq_records_timestamp ON air_quality_records(timestamp);
CREATE INDEX IF NOT EXISTS idx_aq_records_station ON air_quality_records(station_id);
CREATE INDEX IF NOT EXISTS idx_aq_records_sensor ON air_quality_records(sensor_id);
CREATE INDEX IF NOT EXISTS idx_aq_records_aqi ON air_quality_records(aqi);

CREATE TABLE IF NOT EXISTS predictions (
    id BIGSERIAL PRIMARY KEY,
    location VARCHAR(255) NOT NULL,
    station_id VARCHAR(64),
    forecast_time TIMESTAMP WITH TIME ZONE NOT NULL,
    hours_ahead DOUBLE PRECISION NOT NULL,
    predicted_pm25 DOUBLE PRECISION NOT NULL,
    predicted_pm10 DOUBLE PRECISION,
    predicted_aqi INTEGER NOT NULL,
    predicted_category VARCHAR(50),
    model_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_predictions_forecast_time ON predictions(forecast_time);

CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    location VARCHAR(255) NOT NULL,
    station_id VARCHAR(64),
    sensor_id VARCHAR(64),
    severity VARCHAR(50) NOT NULL, -- INFO, WARNING, DANGER, CRITICAL
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    current_aqi INTEGER NOT NULL,
    predicted_aqi INTEGER,
    reason VARCHAR(255),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS hotspots (
    id SERIAL PRIMARY KEY,
    location VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    current_aqi INTEGER NOT NULL,
    current_pm25 DOUBLE PRECISION NOT NULL,
    trend VARCHAR(50) NOT NULL, -- Increasing, Stable, Decreasing
    severity_level VARCHAR(50) NOT NULL, -- Moderate, High, Severe, Critical
    likely_source VARCHAR(255),
    confidence_score DOUBLE PRECISION,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_metrics (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    mae DOUBLE PRECISION NOT NULL,
    rmse DOUBLE PRECISION NOT NULL,
    r2 DOUBLE PRECISION NOT NULL,
    mae_improvement_pct DOUBLE PRECISION,
    rmse_improvement_pct DOUBLE PRECISION,
    training_time_seconds DOUBLE PRECISION,
    inference_latency_ms DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
