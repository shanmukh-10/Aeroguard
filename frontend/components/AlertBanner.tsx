"use client";

import React from "react";
import { Alert } from "../lib/types";
import { AlertTriangle, Flame, AlertCircle, Info, X } from "lucide-react";

interface AlertBannerProps {
  alerts: Alert[];
}

export default function AlertBanner({ alerts }: AlertBannerProps) {
  if (!alerts || alerts.length === 0) return null;

  return (
    <div className="space-y-2 mb-6">
      {alerts.slice(0, 2).map((alert) => {
        let bgClass = "bg-amber-500/10 border-amber-500/30 text-amber-200";
        let icon = <AlertCircle className="w-5 h-5 text-amber-400 shrink-0" />;

        if (alert.severity === "CRITICAL") {
          bgClass = "bg-red-500/15 border-red-500/40 text-red-100 animate-pulse";
          icon = <Flame className="w-5 h-5 text-red-400 shrink-0" />;
        } else if (alert.severity === "DANGER") {
          bgClass = "bg-orange-500/15 border-orange-500/30 text-orange-100";
          icon = <AlertTriangle className="w-5 h-5 text-orange-400 shrink-0" />;
        }

        return (
          <div
            key={alert.id}
            className={`p-4 rounded-xl border flex items-start justify-between backdrop-blur shadow-sm ${bgClass}`}
          >
            <div className="flex items-start space-x-3">
              {icon}
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-sm tracking-wide">
                    {alert.title}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 font-mono font-medium">
                    {alert.location}
                  </span>
                </div>
                <p className="text-xs sm:text-sm mt-1 text-slate-300">
                  {alert.message}
                </p>
                {alert.reason && (
                  <p className="text-xs text-slate-400 mt-1 italic">
                    Reason: {alert.reason}
                  </p>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
