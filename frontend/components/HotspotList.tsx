"use client";

import React from "react";
import { Hotspot } from "../lib/types";
import { Flame, ArrowUpRight, ArrowDownRight, Minus, AlertCircle } from "lucide-react";

interface HotspotListProps {
  hotspots: Hotspot[];
}

export default function HotspotList({ hotspots }: HotspotListProps) {
  const getTrendIcon = (trend: string) => {
    if (trend === "Increasing") return <ArrowUpRight className="w-4 h-4 text-red-400" />;
    if (trend === "Decreasing") return <ArrowDownRight className="w-4 h-4 text-emerald-400" />;
    return <Minus className="w-4 h-4 text-amber-400" />;
  };

  const getSeverityBadge = (sev: string) => {
    switch (sev.toLowerCase()) {
      case "critical":
        return "bg-rose-950 text-rose-300 border-rose-600";
      case "severe":
        return "bg-red-500/20 text-red-300 border-red-500/30";
      case "high":
        return "bg-orange-500/20 text-orange-300 border-orange-500/30";
      default:
        return "bg-yellow-500/20 text-yellow-300 border-yellow-500/30";
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400">
            <Flame className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Active Pollution Hotspots</h3>
            <p className="text-xs text-slate-400">Localized High-Risk Areas</p>
          </div>
        </div>
        <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
          {hotspots.length} Detected
        </span>
      </div>

      <div className="divide-y divide-slate-800/80 mt-2">
        {hotspots.map((h) => (
          <div key={h.id} className="py-3.5 flex items-center justify-between hover:bg-slate-800/30 px-2 rounded-xl transition-colors">
            <div className="space-y-0.5">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-semibold text-white">{h.location}</span>
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium border ${getSeverityBadge(h.severity_level)}`}>
                  {h.severity_level}
                </span>
              </div>
              {h.likely_source && (
                <p className="text-xs text-slate-400">
                  {h.likely_source}
                </p>
              )}
            </div>

            <div className="text-right">
              <div className="flex items-center justify-end space-x-1.5">
                <span className="text-base font-bold text-white">{h.current_aqi}</span>
                <span className="text-[10px] text-slate-400">AQI</span>
                {getTrendIcon(h.trend)}
              </div>
              <p className="text-[11px] text-slate-400">PM2.5: {h.current_pm25.toFixed(1)} µg/m³</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
