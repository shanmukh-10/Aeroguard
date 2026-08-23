"use client";

import React, { useEffect, useState } from "react";
import { getLocations, getHotspots } from "../../lib/api";
import { LocationItem, Hotspot } from "../../lib/types";
import MapView from "../../components/MapView";
import HotspotList from "../../components/HotspotList";

export default function MapPage() {
  const [locations, setLocations] = useState<LocationItem[]>([]);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getLocations(), getHotspots()]).then(([locs, hs]) => {
      setLocations(locs);
      setHotspots(hs);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl">
        <h1 className="text-2xl font-bold text-white">Hyperlocal Geospatial Intelligence</h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Explore Continuous Ambient Air Quality Monitoring Stations (CAAQMS) and Hyperlocal IoT nodes across Delhi NCR.
        </p>
      </div>

      <MapView locations={locations} hotspots={hotspots} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <HotspotList hotspots={hotspots} />
        
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-3">
          <h3 className="text-base font-bold text-white">Geospatial AQI Breakpoints (CPCB)</h3>
          <p className="text-xs text-slate-400">
            Standard color spectrum for spatial severity classification:
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 pt-2">
            <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs">
              <span className="font-bold block">Good (0 - 50)</span>
              Minimal health impact.
            </div>
            <div className="p-3 rounded-lg bg-lime-500/10 border border-lime-500/30 text-lime-300 text-xs">
              <span className="font-bold block">Satisfactory (51 - 100)</span>
              Minor discomfort to sensitive.
            </div>
            <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/30 text-yellow-300 text-xs">
              <span className="font-bold block">Moderate (101 - 200)</span>
              Discomfort in lung/heart disease.
            </div>
            <div className="p-3 rounded-lg bg-orange-500/10 border border-orange-500/30 text-orange-300 text-xs">
              <span className="font-bold block">Poor (201 - 300)</span>
              Discomfort on prolonged exposure.
            </div>
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-xs">
              <span className="font-bold block">Very Poor (301 - 400)</span>
              Respiratory illness risk.
            </div>
            <div className="p-3 rounded-lg bg-rose-950/80 border border-rose-600 text-rose-200 text-xs">
              <span className="font-bold block">Severe (401 - 500)</span>
              Emergency impact on all groups.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
