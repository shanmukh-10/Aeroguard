export interface CurrentAirQuality {
  station_id?: string;
  sensor_id?: string;
  location: string;
  latitude: number;
  longitude: number;
  timestamp: string;
  aqi: number;
  category: string;
  color: string;
  dominant_pollutant: string;
  pm25: number;
  pm10: number;
  no2: number;
  so2: number;
  co: number;
  ozone: number;
  nh3: number;
  temperature: number;
  humidity: number;
  wind_speed: number;
  wind_direction: number;
  advisory: string;
  sensitive_advisory: string;
  trend: string;
  sub_indices: Record<string, number>;
}

export interface ForecastPoint {
  forecast_time: string;
  hours_from_now: number;
  predicted_pm25: number;
  predicted_pm10?: number;
  predicted_aqi: number;
  category: string;
  color: string;
  advisory: string;
}

export interface ForecastData {
  location: string;
  current_pm25: number;
  trend: string;
  model_name: string;
  forecast: ForecastPoint[];
  model_metrics: Record<string, any>;
}

export interface HistoryPoint {
  timestamp: string;
  pm25?: number;
  pm10?: number;
  no2?: number;
  so2?: number;
  co?: number;
  ozone?: number;
  aqi?: number;
  category?: string;
}

export interface HistoryData {
  location: string;
  timeframe: string;
  record_count: number;
  avg_aqi?: number;
  max_aqi?: number;
  min_aqi?: number;
  avg_pm25?: number;
  max_pm25?: number;
  data: HistoryPoint[];
}

export interface Hotspot {
  id: number;
  location: string;
  latitude: number;
  longitude: number;
  current_aqi: number;
  current_pm25: number;
  trend: "Increasing" | "Stable" | "Decreasing";
  severity_level: "Moderate" | "High" | "Severe" | "Critical";
  likely_source?: string;
  confidence_score?: number;
  last_updated: string;
}

export interface Alert {
  id: number;
  location: string;
  severity: "INFO" | "WARNING" | "DANGER" | "CRITICAL";
  title: string;
  message: string;
  current_aqi: number;
  predicted_aqi?: number;
  reason?: string;
  timestamp: string;
  is_active: boolean;
}

export interface LocationItem {
  id: string;
  name: string;
  type: string;
  is_station: boolean;
  latitude: number;
  longitude: number;
  aqi: number;
  category: string;
  pm25: number;
  status: string;
}

export interface SourcePattern {
  location: string;
  likely_source_pattern: string;
  confidence_score: number;
  dominant_factors: string[];
  supporting_indicators: Record<string, any>;
  meteorological_context: Record<string, any>;
  disclaimer: string;
}

export interface ModelMetricsData {
  target: string;
  frequency: string;
  dataset: string;
  train_samples: number;
  test_samples: number;
  best_model: string;
  models: Record<string, {
    model_name: string;
    mae: number;
    rmse: number;
    r2: number;
    mae_improvement_pct?: number;
    rmse_improvement_pct?: number;
    training_time_seconds?: number;
    inference_latency_ms?: number;
  }>;
}

// ==========================================
// Location Search & Nearest Station Types
// ==========================================

export interface SelectedLocationInfo {
  name: string;
  latitude: number;
  longitude: number;
}

export interface NearestStationDetail {
  station_id: string;
  name: string;
  type: string;
  is_station: boolean;
  latitude: number;
  longitude: number;
  distance_km: number;
}

export interface NearestAirQualityData {
  timestamp: string;
  aqi?: number;
  category: string;
  color: string;
  dominant_pollutant?: string;
  pm25?: number;
  pm10?: number;
  no2?: number;
  so2?: number;
  co?: number;
  ozone?: number;
  temperature?: number;
  humidity?: number;
  advisory: string;
  sensitive_advisory: string;
}

export interface NearestStationResponse {
  selected_location: SelectedLocationInfo;
  has_nearby_station: boolean;
  coverage_type: "DIRECT" | "NEARBY" | "EXTENDED" | "OUT_OF_RANGE";
  coverage_label: string;
  distance_km?: number;
  nearest_station?: NearestStationDetail;
  air_quality?: NearestAirQualityData;
  forecast_pm25_2h?: number;
  forecast_aqi_2h?: number;
  disclaimer: string;
}

export interface GeocodeResultItem {
  name: string;
  display_name: string;
  latitude: number;
  longitude: number;
  type: string;
}
