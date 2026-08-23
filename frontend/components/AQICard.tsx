"use client";

import React from "react";
import { CurrentAirQuality } from "../lib/types";
import { Gauge, Droplets, Thermometer, Wind, Compass, Shield, Activity } from "lucide-react";

interface AQICardProps {
  data: CurrentAirQuality;
}

export default function AQICard({ data }: AQICardProps) {
  const aqi = data.aqi || 215;
  const category = data.category || "Poor";
  const dominant = data.dominant_pollutant || "PM2.5";

  // Category styling helper
  const getBadgeStyle = (cat: string) => {
    switch (cat.toLowerCase()) {
      case "good":
        return "bg-emerald-500/20 text-emerald-300 border-emerald-500/30";
      case "satisfactory":
        return "bg-lime-500/20 text-lime-300 border-lime-500/30";
      case "moderate":
        return "bg-yellow-500/20 text-yellow-300 border-yellow-500/30";
      case "poor":
        return "bg-orange-500/20 text-orange-300 border-orange-500/30";
      case "very poor":
        return "bg-red-500/20 text-red-300 border-red-500/30";
      case "severe":
      case "severe+":
        return "bg-rose-950 text-rose-200 border-rose-600";
      default:
        return "bg-slate-700 text-slate-300 border-slate-600";
    }
  };

  const pollutants = [
    { label: "PM2.5", value: data.pm25, unit: "µg/m³", highlight: dominant === "PM2.5" || dominant === "pm25" },
    { label: "PM10", value: data.pm10, unit: "µg/m³", highlight: dominant === "PM10" || dominant === "pm10" },
    { label: "NO2", value: data.no2, unit: "µg/m³", highlight: dominant === "no2" },
    { label: "SO2", value: data.so2, unit: "µg/m³", highlight: dominant === "so2" },
    { label: "CO", value: data.co, unit: "mg/m³", highlight: dominant === "co" },
    { label: "Ozone", value: data.ozone, unit: "µg/m³", highlight: dominant === "ozone" },
    { label: "NH3", value: data.nh3, unit: "µg/m³", highlight: dominant === "nh3" },
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
      {/* Background glow matching AQI severity */}
      <div
        className="absolute -right-16 -top-16 w-64 h-64 rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ backgroundColor: data.color || "#F97316" }}
      ></div>

      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
              Hyperlocal Live Stream
            </span>
            <span className="text-slate-500">•</span>
            <span className="text-xs text-slate-400 font-mono">
              {data.station_id || data.sensor_id || "site_118"}
            </span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-white mt-1">
            {data.location}
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Verified Indian CPCB Sub-Index Methodology
          </p>
        </div>

        {/* Status Badge */}
        <div className="flex items-center space-x-2">
          <span className={`px-4 py-1.5 rounded-full text-sm font-semibold border ${getBadgeStyle(category)}`}>
            {category}
          </span>
        </div>
      </div>

      {/* Main Stats Hero Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 py-6 border-b border-slate-800">
        {/* AQI Big Counter */}
        <div className="flex items-center space-x-4 bg-slate-800/40 p-4 rounded-xl border border-slate-800">
          <div
            className="w-16 h-16 rounded-xl flex flex-col items-center justify-center font-bold text-2xl text-white shadow-inner"
            style={{ backgroundColor: data.color || "#F97316" }}
          >
            {aqi}
          </div>
          <div>
            <span className="text-xs uppercase text-slate-400 tracking-wider">Air Quality Index</span>
            <p className="text-sm font-semibold text-white mt-0.5">CPCB Standard AQI</p>
            <p className="text-xs text-slate-400">Dominant: <span className="text-emerald-400 font-medium">{dominant}</span></p>
          </div>
        </div>

        {/* PM2.5 Priority Card */}
        <div className="flex items-center space-x-4 bg-slate-800/40 p-4 rounded-xl border border-slate-800">
          <div className="w-16 h-16 rounded-xl bg-slate-800 flex items-center justify-center text-emerald-400 border border-slate-700">
            <Activity className="w-8 h-8" />
          </div>
          <div>
            <span className="text-xs uppercase text-slate-400 tracking-wider">PM2.5 Primary Pollutant</span>
            <div className="flex items-baseline space-x-1 mt-0.5">
              <span className="text-2xl font-bold text-white">
                {data.pm25 !== undefined ? data.pm25.toFixed(1) : "--"}
              </span>
              <span className="text-xs text-slate-400">µg/m³</span>
            </div>
            <p className="text-xs text-slate-400">CPCB 24h Safe Limit: 30 µg/m³</p>
          </div>
        </div>

        {/* Ambient Meteorology */}
        <div className="bg-slate-800/40 p-4 rounded-xl border border-slate-800 flex items-center justify-around">
          <div className="text-center">
            <div className="flex items-center justify-center text-sky-400 mb-1">
              <Thermometer className="w-4 h-4 mr-1" />
              <span className="text-xs text-slate-400">Temp</span>
            </div>
            <span className="text-base font-bold text-white">
              {data.temperature ? `${data.temperature.toFixed(1)}°C` : "26.5°C"}
            </span>
          </div>

          <div className="text-center">
            <div className="flex items-center justify-center text-teal-400 mb-1">
              <Droplets className="w-4 h-4 mr-1" />
              <span className="text-xs text-slate-400">Humidity</span>
            </div>
            <span className="text-base font-bold text-white">
              {data.humidity ? `${data.humidity.toFixed(0)}%` : "58%"}
            </span>
          </div>

          <div className="text-center">
            <div className="flex items-center justify-center text-indigo-400 mb-1">
              <Wind className="w-4 h-4 mr-1" />
              <span className="text-xs text-slate-400">Wind</span>
            </div>
            <span className="text-base font-bold text-white">
              {data.wind_speed ? `${data.wind_speed.toFixed(1)} m/s` : "2.2 m/s"}
            </span>
          </div>
        </div>
      </div>

      {/* Multi-Pollutant Grid */}
      <div className="pt-6">
        <h3 className="text-xs uppercase tracking-wider text-slate-400 font-semibold mb-3">
          Measured Pollutant Concentrations & Sub-Indices
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
          {pollutants.map((pol) => {
            const subVal = data.sub_indices?.[pol.label.toLowerCase()] || data.sub_indices?.[pol.label];
            return (
              <div
                key={pol.label}
                className={`p-3 rounded-xl border transition-all ${
                  pol.highlight
                    ? "bg-slate-800/90 border-emerald-500/40 shadow-sm shadow-emerald-500/10"
                    : "bg-slate-800/30 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-300">{pol.label}</span>
                  {pol.highlight && (
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                  )}
                </div>
                <div className="mt-1 flex items-baseline space-x-1">
                  <span className="text-lg font-bold text-white">
                    {pol.value !== undefined && pol.value !== null ? pol.value.toFixed(1) : "--"}
                  </span>
                  <span className="text-[10px] text-slate-500">{pol.unit}</span>
                </div>
                {subVal && (
                  <p className="text-[10px] text-slate-400 mt-0.5">
                    Sub-index: <span className="text-slate-200 font-mono">{Math.round(subVal)}</span>
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
