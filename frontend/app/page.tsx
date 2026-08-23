"use client";

import React, { useEffect, useState } from "react";
import {
  getCurrentAirQuality,
  getForecast,
  getHotspots,
  getAlerts,
  getLocations,
  getSourcePattern,
  getModelMetrics
} from "../lib/api";
import {
  CurrentAirQuality,
  ForecastData,
  Hotspot,
  Alert,
  LocationItem,
  SourcePattern as SourcePatternType,
  ModelMetricsData
} from "../lib/types";

import AlertBanner from "../components/AlertBanner";
import AQICard from "../components/AQICard";
import ForecastChart from "../components/ForecastChart";
import MapView from "../components/MapView";
import HotspotList from "../components/HotspotList";
import SourcePatternCard from "../components/SourcePattern";
import AdvisoryCard from "../components/AdvisoryCard";
import ModelMetrics from "../components/ModelMetrics";
import { RefreshCw, Radio, Sparkles } from "lucide-react";

export default function Dashboard() {
  const [currentAQ, setCurrentAQ] = useState<CurrentAirQuality | null>(null);
  const [forecast, setForecast] = useState<ForecastData | null>(null);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [locations, setLocations] = useState<LocationItem[]>([]);
  const [sourcePattern, setSourcePattern] = useState<SourcePatternType | null>(null);
  const [metrics, setMetrics] = useState<ModelMetricsData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const loadAllData = async () => {
    try {
      const [aqData, fcData, hsData, alData, locData, spData, mmData] = await Promise.all([
        getCurrentAirQuality(),
        getForecast(12),
        getHotspots(),
        getAlerts(),
        getLocations(),
        getSourcePattern(),
        getModelMetrics()
      ]);
      setCurrentAQ(aqData);
      setForecast(fcData);
      setHotspots(hsData);
      setAlerts(alData);
      setLocations(locData);
      setSourcePattern(spData);
      setMetrics(mmData);
    } catch (err) {
      console.error("Error loading dashboard data:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadAllData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadAllData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    loadAllData();
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <div className="w-12 h-12 border-4 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin"></div>
        <p className="text-sm font-medium text-slate-400">
          Loading AeroGuard Environmental Intelligence...
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Banner / Hero Title Bar */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/60 border border-slate-800 p-6 rounded-2xl">
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-xs uppercase font-mono font-semibold tracking-wider text-emerald-400">
              Live Environmental Telemetry Engine
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            AeroGuard
          </h1>
          <p className="text-sm text-slate-300 max-w-2xl mt-1">
            AI + IoT Platform for Predicting and Preventing Pollution Risks. Hyperlocal monitoring, multi-hour neural forecasting, and evidence-based preventive intelligence.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs sm:text-sm font-medium border border-slate-700 transition-colors shadow-sm"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin text-emerald-400" : ""}`} />
            <span>{refreshing ? "Syncing..." : "Refresh Feed"}</span>
          </button>
        </div>
      </div>

      {/* Real-time Alerts Banner */}
      {alerts && alerts.length > 0 && <AlertBanner alerts={alerts} />}

      {/* Live AQI Hero Card */}
      {currentAQ && <AQICard data={currentAQ} />}

      {/* Grid: Forecast Chart & Hotspots */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          {forecast && <ForecastChart data={forecast} />}
        </div>
        <div className="lg:col-span-1">
          <HotspotList hotspots={hotspots} />
        </div>
      </div>

      {/* Interactive Map */}
      <MapView locations={locations} hotspots={hotspots} />

      {/* Grid: Likely Source Pattern & Health Advisories */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {sourcePattern && <SourcePatternCard data={sourcePattern} />}
        {currentAQ && (
          <AdvisoryCard
            advisory={currentAQ.advisory}
            sensitiveAdvisory={currentAQ.sensitive_advisory}
            category={currentAQ.category}
          />
        )}
      </div>

      {/* AI / ML Model Benchmarks */}
      {metrics && <ModelMetrics data={metrics} />}
    </div>
  );
}
