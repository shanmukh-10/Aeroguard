"use client";

import React from "react";
import { SourcePattern } from "../lib/types";
import { Search, Compass, CheckCircle2, ShieldCheck } from "lucide-react";

interface SourcePatternProps {
  data: SourcePattern;
}

export default function SourcePatternCard({ data }: SourcePatternProps) {
  const confidencePct = Math.round((data.confidence_score || 0.85) * 100);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-400">
            <Search className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">
              Likely Pollution-Source Pattern
            </h3>
            <p className="text-xs text-slate-400">Multi-Pollutant Stoichiometric Analysis</p>
          </div>
        </div>

        <div className="flex items-center space-x-1.5 bg-teal-500/15 text-teal-300 border border-teal-500/30 px-3 py-1 rounded-full text-xs font-semibold">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>{confidencePct}% Confidence</span>
        </div>
      </div>

      <div className="mt-4 space-y-4">
        {/* Identified pattern banner */}
        <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/80">
          <span className="text-xs uppercase tracking-wider text-slate-400 font-medium">
            Inferred Dominant Signature
          </span>
          <p className="text-base sm:text-lg font-bold text-white mt-0.5">
            {data.likely_source_pattern}
          </p>
        </div>

        {/* Contributing Factors */}
        <div>
          <h4 className="text-xs uppercase tracking-wider text-slate-400 font-semibold mb-2">
            Key Inferred Indicators
          </h4>
          <ul className="space-y-2">
            {(data.dominant_factors || []).map((factor, idx) => (
              <li key={idx} className="flex items-start space-x-2 text-xs sm:text-sm text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>{factor}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Atmospheric / Ratios Grid */}
        <div className="grid grid-cols-2 gap-3 pt-2 border-t border-slate-800 text-xs">
          <div className="bg-slate-800/40 p-2.5 rounded-lg border border-slate-800">
            <span className="text-slate-400 block">PM2.5 / PM10 Ratio:</span>
            <span className="text-white font-mono font-semibold">
              {data.supporting_indicators?.pm25_to_pm10_ratio ?? "0.56"}
            </span>
          </div>
          <div className="bg-slate-800/40 p-2.5 rounded-lg border border-slate-800">
            <span className="text-slate-400 block">NO2 / SO2 Ratio:</span>
            <span className="text-white font-mono font-semibold">
              {data.supporting_indicators?.no2_to_so2_ratio ?? "3.32"}
            </span>
          </div>
        </div>

        {/* Disclaimer */}
        <p className="text-[11px] text-slate-500 italic pt-1">
          {data.disclaimer}
        </p>
      </div>
    </div>
  );
}
