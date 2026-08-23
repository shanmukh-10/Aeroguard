"use client";

import React, { useEffect, useState } from "react";
import { getForecast, getModelMetrics } from "../../lib/api";
import { ForecastData, ModelMetricsData } from "../../lib/types";
import ForecastChart from "../../components/ForecastChart";
import ModelMetrics from "../../components/ModelMetrics";
import { Sparkles, Brain, Clock, ShieldAlert } from "lucide-react";

export default function ForecastPage() {
  const [forecast, setForecast] = useState<ForecastData | null>(null);
  const [metrics, setMetrics] = useState<ModelMetricsData | null>(null);
  const [horizon, setHorizon] = useState<number>(24);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    Promise.all([getForecast(horizon), getModelMetrics()]).then(([fc, mm]) => {
      setForecast(fc);
      setMetrics(mm);
      setLoading(false);
    });
  }, [horizon]);

  return (
    <div className="space-y-6">
      <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">AI Pollution Forecasting & Model Hub</h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Multi-step PM2.5 and AQI projections powered by Random Forest and Deep LSTM Sequence Models.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400">Forecast Horizon:</span>
          {[6, 12, 24].map((h) => (
            <button
              key={h}
              onClick={() => setHorizon(h)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors ${
                horizon === h
                  ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                  : "bg-slate-800 text-slate-400 border-slate-700 hover:text-white"
              }`}
            >
              {h} Hours
            </button>
          ))}
        </div>
      </div>

      {forecast && <ForecastChart data={forecast} />}

      {/* Forecast Details Table */}
      {forecast && forecast.forecast.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <h3 className="text-base font-bold text-white">Tabular Multi-Step Projections</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase text-[11px] tracking-wider">
                  <th className="py-2.5 px-3">Horizon</th>
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3">Predicted PM2.5</th>
                  <th className="py-2.5 px-3">Predicted AQI</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Health Advisory</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {forecast.forecast.map((pt, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30">
                    <td className="py-3 px-3 font-semibold text-emerald-400">+{pt.hours_from_now}h</td>
                    <td className="py-3 px-3 font-mono text-slate-300">
                      {new Date(pt.forecast_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </td>
                    <td className="py-3 px-3 font-bold text-white">{pt.predicted_pm25.toFixed(1)} µg/m³</td>
                    <td className="py-3 px-3">
                      <span className="font-bold text-white px-2 py-0.5 rounded-md" style={{ backgroundColor: pt.color }}>
                        {pt.predicted_aqi}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-semibold text-slate-200">{pt.category}</td>
                    <td className="py-3 px-3 text-slate-400 max-w-xs truncate">{pt.advisory}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {metrics && <ModelMetrics data={metrics} />}
    </div>
  );
}
