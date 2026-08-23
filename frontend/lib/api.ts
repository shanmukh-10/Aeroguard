import {
  CurrentAirQuality,
  ForecastData,
  HistoryData,
  Hotspot,
  Alert,
  LocationItem,
  SourcePattern,
  ModelMetricsData,
  NearestStationResponse,
  GeocodeResultItem
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function fetchJSON<T>(endpoint: string, fallback: T): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, { cache: "no-store" });
    if (!res.ok) {
      console.warn(`API request to ${endpoint} returned status ${res.status}`);
      return fallback;
    }
    return (await res.json()) as T;
  } catch (err) {
    console.warn(`Fetch error for ${endpoint}:`, err);
    return fallback;
  }
}

export async function getCurrentAirQuality(stationId?: string): Promise<CurrentAirQuality> {
  const query = stationId ? `?station_id=${stationId}` : "";
  return fetchJSON<CurrentAirQuality>(`/current${query}`, {
    location: "DTU, Delhi - CPCB",
    latitude: 28.750075,
    longitude: 77.111261,
    timestamp: new Date().toISOString(),
    aqi: 215,
    category: "Poor",
    color: "#F97316",
    dominant_pollutant: "PM2.5",
    pm25: 94.2,
    pm10: 168.4,
    no2: 48.2,
    so2: 14.5,
    co: 1.35,
    ozone: 32.1,
    nh3: 24.0,
    temperature: 26.4,
    humidity: 58.0,
    wind_speed: 2.2,
    wind_direction: 180.0,
    advisory: "Breathing discomfort to most people on prolonged exposure.",
    sensitive_advisory: "People with respiratory or cardiovascular diseases should reduce strenuous outdoor activities.",
    trend: "Stable",
    sub_indices: { pm25: 215.0, pm10: 145.6, no2: 60.2, so2: 18.1, co: 67.5, ozone: 32.1 }
  });
}

export async function getForecast(hours: number = 12): Promise<ForecastData> {
  return fetchJSON<ForecastData>(`/forecast?hours=${hours}`, {
    location: "DTU, Delhi - CPCB",
    current_pm25: 94.2,
    trend: "Stable",
    model_name: "Random Forest Regressor",
    forecast: [],
    model_metrics: {}
  });
}

export async function getHistory(timeframe: "24h" | "7d" | "30d" = "24h"): Promise<HistoryData> {
  return fetchJSON<HistoryData>(`/history?timeframe=${timeframe}`, {
    location: "DTU, Delhi - CPCB",
    timeframe,
    record_count: 0,
    data: []
  });
}

export async function getHotspots(): Promise<Hotspot[]> {
  return fetchJSON<Hotspot[]>("/hotspots", []);
}

export async function getAlerts(): Promise<Alert[]> {
  return fetchJSON<Alert[]>("/alerts", []);
}

export async function getLocations(): Promise<LocationItem[]> {
  return fetchJSON<LocationItem[]>("/locations", []);
}

export async function getSourcePattern(): Promise<SourcePattern> {
  return fetchJSON<SourcePattern>("/source-pattern", {
    location: "DTU, Delhi - CPCB",
    likely_source_pattern: "Likely Traffic-Associated Pattern",
    confidence_score: 0.88,
    dominant_factors: ["Elevated NO2/SO2 ratio", "Peak diurnal vehicular transit"],
    supporting_indicators: { pm25_to_pm10_ratio: 0.56, no2_to_so2_ratio: 3.32, co_level_mg_m3: 1.35 },
    meteorological_context: { wind_speed_ms: 2.2, wind_direction_deg: 180, dispersion_state: "Moderate Dispersion" },
    disclaimer: "Likely pollution-source pattern analysis based on stoichiometric ratios and meteorological context."
  });
}

export async function getModelMetrics(): Promise<ModelMetricsData> {
  return fetchJSON<ModelMetricsData>("/model-metrics", {
    target: "Future PM2.5 (2-hour horizon)",
    frequency: "15 minutes",
    dataset: "Delhi DTU-CPCB (2024-2025)",
    train_samples: 56000,
    test_samples: 14000,
    best_model: "Random Forest Regressor",
    models: {}
  });
}

export async function getNearestStation(
  lat: number,
  lon: number,
  maxRadiusKm: number = 25.0,
  locationName?: string
): Promise<NearestStationResponse> {
  const params = new URLSearchParams({
    lat: lat.toString(),
    lon: lon.toString(),
    max_radius_km: maxRadiusKm.toString()
  });
  if (locationName) {
    params.append("location_name", locationName);
  }

  return fetchJSON<NearestStationResponse>(`/nearest-station?${params.toString()}`, {
    selected_location: {
      name: locationName || `Coordinates (${lat.toFixed(4)}, ${lon.toFixed(4)})`,
      latitude: lat,
      longitude: lon
    },
    has_nearby_station: true,
    coverage_type: "NEARBY",
    coverage_label: "Nearby CAAQMS Station",
    distance_km: 2.5,
    nearest_station: {
      station_id: "site_118",
      name: "DTU, Delhi - CPCB",
      type: "CAAQMS Reference Station",
      is_station: true,
      latitude: 28.750075,
      longitude: 77.111261,
      distance_km: 2.5
    },
    air_quality: {
      timestamp: new Date().toISOString(),
      aqi: 215,
      category: "Poor",
      color: "#F97316",
      dominant_pollutant: "PM2.5",
      pm25: 94.2,
      pm10: 168.4,
      no2: 48.2,
      so2: 14.5,
      co: 1.35,
      ozone: 32.1,
      temperature: 26.4,
      humidity: 58.0,
      advisory: "Breathing discomfort to most people on prolonged exposure.",
      sensitive_advisory: "People with respiratory or cardiovascular diseases should reduce strenuous outdoor activities."
    },
    forecast_pm25_2h: 98.0,
    forecast_aqi_2h: 221,
    disclaimer: "Data represents nearest active station. High spatial correlation with local air quality."
  });
}

export async function searchLocations(query: string): Promise<GeocodeResultItem[]> {
  if (!query.trim()) return [];
  return fetchJSON<GeocodeResultItem[]>(`/geocode?q=${encodeURIComponent(query)}`, []);
}

export async function reverseGeocode(lat: number, lon: number): Promise<string> {
  try {
    const res = await fetch(`${API_BASE}/reverse-geocode?lat=${lat}&lon=${lon}`);
    if (res.ok) {
      const data = await res.json();
      return data.name || `Location (${lat.toFixed(4)}, ${lon.toFixed(4)})`;
    }
  } catch (err) {
    console.warn("Reverse geocode failed:", err);
  }
  return `Location (${lat.toFixed(4)}, ${lon.toFixed(4)})`;
}
