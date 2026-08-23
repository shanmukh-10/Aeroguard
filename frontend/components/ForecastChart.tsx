"use client";

import React from "react";
import { ForecastData } from "../lib/types";
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from "recharts";
import { Sparkles, TrendingUp, Cpu, Info } from "lucide-react";

interface ForecastChartProps {
  data: ForecastData;
}

export default function ForecastChart({ data }: ForecastChartProps) {
  const chartData = (data.forecast || []).map((pt) => {
    const dt = new Date(pt.forecast_time);
    const timeLabel = `${dt.getHours().toString().padStart(2, "0")}:${dt.getMinutes().toString().padStart(2, "0")}`;
    return {
      time: timeLabel,
      hoursAhead: `+${pt.hours_from_now}h`,
      predictedPM25: pt.predicted_pm25,
      predictedAQI: pt.predicted_aqi,
      category: pt.category,
      color: pt.color,
      cpcbThreshold: 60, // CPCB 24-hr Moderate/Satisfactory limit
    };
  });

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">
              AI Multi-Step Pollution Forecast
            </h3>
            <p className="text-xs text-slate-400">
              Model: <span className="text-emerald-400 font-medium">{data.model_name}</span> (12-Hour Horizon)
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400">Trend Projection:</span>
          <span
            className={`text-xs px-2.5 py-1 rounded-full font-semibold border ${
              data.trend === "Increasing"
                ? "bg-red-500/15 text-red-300 border-red-500/30"
                : data.trend === "Decreasing"
                ? "bg-emerald-500/15 text-emerald-300 border-emerald-500/30"
                : "bg-amber-500/15 text-amber-300 border-amber-500/30"
            }`}
          >
            {data.trend}
          </span>
        </div>
      </div>

      {/* Chart container */}
      <div className="h-72 w-full mt-6">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="forecastGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis dataKey="hoursAhead" stroke="#94A3B8" fontSize={11} tickLine={false} />
            <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const p = payload[0].payload;
                  return (
                    <div className="bg-slate-950 border border-slate-700 p-3 rounded-xl shadow-2xl text-xs space-y-1">
                      <p className="font-semibold text-white">Horizon: {p.hoursAhead} ({p.time})</p>
                      <p className="text-emerald-400 font-medium">Predicted PM2.5: {p.predictedPM25} µg/m³</p>
                      <p className="text-amber-400 font-medium">Predicted AQI: {p.predictedAQI} ({p.category})</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend verticalAlign="top" height={36} iconType="circle" wrapperStyle={{ fontSize: "12px" }} />
            <Area
              type="monotone"
              dataKey="predictedPM25"
              name="Predicted PM2.5 (µg/m³)"
              stroke="#10B981"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#forecastGradient)"
            />
            <Line
              type="monotone"
              dataKey="cpcbThreshold"
              name="CPCB 24h Threshold (60 µg/m³)"
              stroke="#EF4444"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              dot={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 pt-4 border-t border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between text-xs text-slate-400 gap-2">
        <div className="flex items-center space-x-1.5">
          <Info className="w-4 h-4 text-slate-500 shrink-0" />
          <span>Predictions update continuously with incoming 15-minute telemetry streams.</span>
        </div>
      </div>
    </div>
  );
}
