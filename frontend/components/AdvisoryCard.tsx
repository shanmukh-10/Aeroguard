"use client";

import React from "react";
import { Shield, HeartHandshake, AlertCircle } from "lucide-react";

interface AdvisoryCardProps {
  advisory: string;
  sensitiveAdvisory: string;
  category: string;
}

export default function AdvisoryCard({ advisory, sensitiveAdvisory, category }: AdvisoryCardProps) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
      <div className="flex items-center space-x-2 pb-3 border-b border-slate-800">
        <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
          <Shield className="w-4 h-4" />
        </div>
        <div>
          <h3 className="text-base font-bold text-white">CPCB Health & Environmental Advisory</h3>
          <p className="text-xs text-slate-400">Evidence-Based Guidance for Category: <span className="text-emerald-400 font-semibold">{category}</span></p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* General Population */}
        <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-800 space-y-1">
          <div className="flex items-center space-x-2 text-slate-300 font-semibold text-xs uppercase tracking-wider">
            <Shield className="w-4 h-4 text-emerald-400" />
            <span>General Public</span>
          </div>
          <p className="text-xs sm:text-sm text-slate-300 pt-1">
            {advisory || "Maintain standard outdoor physical activity. Follow local advisories."}
          </p>
        </div>

        {/* Sensitive Groups */}
        <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-800 space-y-1">
          <div className="flex items-center space-x-2 text-amber-300 font-semibold text-xs uppercase tracking-wider">
            <HeartHandshake className="w-4 h-4 text-amber-400" />
            <span>Vulnerable & Sensitive Groups</span>
          </div>
          <p className="text-xs sm:text-sm text-slate-300 pt-1">
            {sensitiveAdvisory || "Children, elderly, and individuals with respiratory conditions should consider precautions."}
          </p>
        </div>
      </div>

      <p className="text-[11px] text-slate-500 italic">
        Note: AeroGuard provides environmental intelligence and public health advisories based on official CPCB standards. It does not provide medical diagnoses or prescriptions.
      </p>
    </div>
  );
}
