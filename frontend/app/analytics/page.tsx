"use client";

import React, { useEffect, useState } from "react";
import { getHistory } from "../../lib/api";
import { HistoryData } from "../../lib/types";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from "recharts";
import { Calendar, BarChart3, TrendingUp, Filter } from "lucide-react";

export default function AnalyticsPage() {
  const [timeframe, setTimeframe] = useState<"24h" | "7d" | "30d">("24h");
  const [history, setHistory] = useState<HistoryData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getHistory(timeframe).then((data) => {
      setHistory(data);
      setLoading(false);
    });
  }, [timeframe]);

  const chartData = (history?.data || []).map((pt) => {
    const dt = new Date(pt.timestamp);
    const dateLabel =
      timeframe === "24h"
        ? `${dt.getHours().toString().padStart(2, "0")}:${dt.getMinutes().toString().padStart(2, "0")}`
        : `${dt.getMonth() + 1}/${dt.getDate()} ${dt.getHours()}:00`;

    return {
      time: dateLabel,
      pm25: pt.pm25,
      pm10: pt.pm10,
      no2: pt.no2,
      so2: pt.so2,
      aqi: pt.aqi,
    };
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Historical Pollution Analytics</h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            24-Hour, 7-Day, and 30-Day Multi-Pollutant Time-Series Analysis for DTU Delhi CAAQMS Station.
          </p>
        </div>

        {/* Timeframe Selector */}
        <div className="flex items-center space-x-2 bg-slate-800/80 p-1.5 rounded-xl border border-slate-700">
          {(["24h", "7d", "30d"] as const).map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                timeframe === tf
                  ? "bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              {tf.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <span className="text-xs text-slate-400 uppercase tracking-wider block">Average AQI</span>
          <span className="text-2xl font-bold text-white mt-1 block">
            {history?.avg_aqi !== undefined ? history.avg_aqi : "--"}
          </span>
          <span className="text-[11px] text-slate-500">Over selected period</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <span className="text-xs text-slate-400 uppercase tracking-wider block">Peak AQI</span>
          <span className="text-2xl font-bold text-red-400 mt-1 block">
            {history?.max_aqi !== undefined ? history.max_aqi : "--"}
          </span>
          <span className="text-[11px] text-slate-500">Max observed index</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <span className="text-xs text-slate-400 uppercase tracking-wider block">Average PM2.5</span>
          <span className="text-2xl font-bold text-emerald-400 mt-1 block">
            {history?.avg_pm25 !== undefined ? `${history.avg_pm25.toFixed(1)}` : "--"}
          </span>
          <span className="text-[11px] text-slate-500">µg/m³ concentration</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <span className="text-xs text-slate-400 uppercase tracking-wider block">Peak PM2.5 Spike</span>
          <span className="text-2xl font-bold text-orange-400 mt-1 block">
            {history?.max_pm25 !== undefined ? `${history.max_pm25.toFixed(1)}` : "--"}
          </span>
          <span className="text-[11px] text-slate-500">µg/m³ maximum spike</span>
        </div>
      </div>

      {/* Historical Area Chart */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <h3 className="text-base font-bold text-white mb-4">
          Multi-Pollutant Trajectory ({timeframe.toUpperCase()})
        </h3>
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="pm25Grad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="pm10Grad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#38BDF8" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#38BDF8" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
              <XAxis dataKey="time" stroke="#94A3B8" fontSize={11} tickLine={false} />
              <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const p = payload[0].payload;
                    return (
                      <div className="bg-slate-950 border border-slate-700 p-3 rounded-xl shadow-2xl text-xs space-y-1">
                        <p className="font-semibold text-white">Time: {p.time}</p>
                        <p className="text-emerald-400 font-medium">PM2.5: {p.pm25?.toFixed(1)} µg/m³</p>
                        <p className="text-sky-400 font-medium">PM10: {p.pm10?.toFixed(1)} µg/m³</p>
                        <p className="text-amber-400 font-medium">AQI: {p.aqi}</p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend verticalAlign="top" height={36} iconType="circle" wrapperStyle={{ fontSize: "12px" }} />
              <Area
                type="monotone"
                dataKey="pm25"
                name="PM2.5 (µg/m³)"
                stroke="#10B981"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#pm25Grad)"
              />
              <Area
                type="monotone"
                dataKey="pm10"
                name="PM10 (µg/m³)"
                stroke="#38BDF8"
                strokeWidth={1.5}
                fillOpacity={1}
                fill="url(#pm10Grad)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
