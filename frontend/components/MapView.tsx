"use client";

import React, { useEffect, useState, useRef } from "react";
import dynamic from "next/dynamic";
import { LocationItem, Hotspot, NearestStationResponse, GeocodeResultItem } from "../lib/types";
import { getNearestStation, searchLocations, reverseGeocode } from "../lib/api";
import { 
  MapPin, Radio, Activity, Flame, Search, Navigation, 
  AlertTriangle, ShieldCheck, Compass, Info, X, Loader2, Crosshair
} from "lucide-react";

// Dynamically import Leaflet Map to ensure zero SSR / window issues in Next.js
const RealLeafletMap = dynamic(() => import("./RealLeafletMap"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full min-h-[480px] bg-slate-950 rounded-xl border border-slate-800 flex flex-col items-center justify-center space-y-3">
      <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
      <span className="text-xs text-slate-400 font-mono">Loading Real Geographic Map & Satellite Tiles...</span>
    </div>
  ),
});

interface MapViewProps {
  locations: LocationItem[];
  hotspots: Hotspot[];
  selectedLocation?: string;
  onSelectLocation?: (loc: LocationItem) => void;
}

const PRESET_PLACES = [
  { name: "DTU (Shahbad)", lat: 28.750075, lon: 77.111261, zoom: 14 },
  { name: "Connaught Place", lat: 28.6315, lon: 77.2167, zoom: 14 },
  { name: "Anand Vihar", lat: 28.6469, lon: 77.3160, zoom: 14 },
  { name: "Rohini", lat: 28.7350, lon: 77.1200, zoom: 13 },
  { name: "Bawana", lat: 28.7950, lon: 77.0500, zoom: 13 },
  { name: "Punjabi Bagh", lat: 28.6683, lon: 77.1264, zoom: 14 },
  { name: "Dwarka", lat: 28.5823, lon: 77.0500, zoom: 13 },
  { name: "Saket", lat: 28.5244, lon: 77.2183, zoom: 14 },
  { name: "Hyderabad", lat: 17.385044, lon: 78.486671, zoom: 12 },
  { name: "Bengaluru", lat: 12.971599, lon: 77.594566, zoom: 12 },
  { name: "Mumbai", lat: 19.076090, lon: 72.877426, zoom: 12 },
  { name: "Chennai", lat: 13.082680, lon: 80.270721, zoom: 12 },
  { name: "Noida Sec 18", lat: 28.5700, lon: 77.3200, zoom: 14 },
  { name: "Cyber Hub Gurgaon", lat: 28.4950, lon: 77.0890, zoom: 14 },
];

export default function MapView({ locations, hotspots, onSelectLocation }: MapViewProps) {
  // Map center and zoom (default centered on Delhi NCR)
  const [mapCenter, setMapCenter] = useState<[number, number]>([28.6448, 77.1800]);
  const [mapZoom, setMapZoom] = useState<number>(11);

  // Selected user coordinates
  const [selectedCoord, setSelectedCoord] = useState<{ lat: number; lon: number; name: string }>({
    lat: 28.750075,
    lon: 77.111261,
    name: "DTU, Delhi - CPCB"
  });

  // Nearest station data state
  const [nearestData, setNearestData] = useState<NearestStationResponse | null>(null);
  const [loadingNearest, setLoadingNearest] = useState<boolean>(false);

  // Search input state
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [searchResults, setSearchResults] = useState<GeocodeResultItem[]>([]);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [showDropdown, setShowDropdown] = useState<boolean>(false);
  const searchContainerRef = useRef<HTMLDivElement>(null);

  // Max radius config (default 25 km)
  const [maxRadius, setMaxRadius] = useState<number>(25.0);

  // Fetch nearest station whenever selected coordinates or maxRadius changes
  useEffect(() => {
    let isMounted = true;
    setLoadingNearest(true);
    getNearestStation(selectedCoord.lat, selectedCoord.lon, maxRadius, selectedCoord.name)
      .then((res) => {
        if (isMounted) {
          setNearestData(res);
          setLoadingNearest(false);
        }
      })
      .catch(() => {
        if (isMounted) setLoadingNearest(false);
      });

    return () => {
      isMounted = false;
    };
  }, [selectedCoord, maxRadius]);

  // Debounced search query handler for all Indian locations
  useEffect(() => {
    if (!searchQuery.trim() || searchQuery.length < 2) {
      setSearchResults([]);
      setShowDropdown(false);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const results = await searchLocations(searchQuery);
        setSearchResults(results);
        setShowDropdown(true);
      } catch (err) {
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 280);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Close search dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (searchContainerRef.current && !searchContainerRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelectSearchResult = (item: GeocodeResultItem) => {
    setSelectedCoord({
      lat: item.latitude,
      lon: item.longitude,
      name: item.name || item.display_name.split(",")[0]
    });
    setMapCenter([item.latitude, item.longitude]);
    setMapZoom(13);
    setSearchQuery(item.name);
    setShowDropdown(false);
  };

  const handleSelectPreset = (preset: { name: string; lat: number; lon: number; zoom: number }) => {
    setSelectedCoord({
      lat: preset.lat,
      lon: preset.lon,
      name: preset.name
    });
    setMapCenter([preset.lat, preset.lon]);
    setMapZoom(preset.zoom);
    setSearchQuery(preset.name);
  };

  // Direct map click handler: captures coordinates and reverse-geocodes
  const handleMapClick = async (lat: number, lon: number) => {
    const defaultName = `Location (${lat.toFixed(4)}, ${lon.toFixed(4)})`;
    setSelectedCoord({
      lat,
      lon,
      name: defaultName
    });

    // Try reverse geocoding in background
    try {
      const resolvedName = await reverseGeocode(lat, lon);
      setSelectedCoord({
        lat,
        lon,
        name: resolvedName
      });
      setSearchQuery(resolvedName);
    } catch {
      setSearchQuery(defaultName);
    }
  };

  const handleSelectStation = (loc: LocationItem) => {
    setSelectedCoord({
      lat: loc.latitude,
      lon: loc.longitude,
      name: loc.name
    });
    setMapCenter([loc.latitude, loc.longitude]);
    setMapZoom(14);
    setSearchQuery(loc.name);
    if (onSelectLocation) onSelectLocation(loc);
  };

  const getAQIColor = (aqi?: number) => {
    if (aqi === undefined || aqi === null) return "#64748B";
    if (aqi <= 50) return "#10B981";
    if (aqi <= 100) return "#84CC16";
    if (aqi <= 200) return "#EAB308";
    if (aqi <= 300) return "#F97316";
    if (aqi <= 400) return "#EF4444";
    return "#881337";
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
      {/* Header & Legends */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
            <Compass className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              AeroGuard Hyperlocal Air Quality Geospatial Intelligence
            </h3>
            <p className="text-xs text-slate-400">
              Interactive OpenStreetMap GIS with CAAQMS reference stations, IoT nodes, and nationwide place search.
            </p>
          </div>
        </div>

        {/* Legend Pills */}
        <div className="flex flex-wrap items-center gap-3 text-xs">
          <div className="flex items-center space-x-1.5 bg-slate-950 px-2.5 py-1 rounded-full border border-slate-800 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 ring-2 ring-cyan-400/30 inline-block"></span>
            <span className="font-semibold">Selected Location</span>
          </div>
          <div className="flex items-center space-x-1.5 bg-slate-950 px-2.5 py-1 rounded-full border border-slate-800 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block"></span>
            <span>CAAQMS Station</span>
          </div>
          <div className="flex items-center space-x-1.5 bg-slate-950 px-2.5 py-1 rounded-full border border-slate-800 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-400 inline-block"></span>
            <span>IoT Node</span>
          </div>
          <div className="flex items-center space-x-1.5 bg-slate-950 px-2.5 py-1 rounded-full border border-slate-800 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping inline-block"></span>
            <span>Hotspot</span>
          </div>
        </div>
      </div>

      {/* Nationwide Location Search Bar */}
      <div className="relative" ref={searchContainerRef}>
        <div className="relative flex items-center">
          <Search className="w-4 h-4 text-slate-400 absolute left-4 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => {
              if (searchResults.length > 0) setShowDropdown(true);
            }}
            placeholder="Search any Indian city, district, or landmark (e.g. Hyderabad, Connaught Place, Bengaluru, Rohini, Mumbai)..."
            className="w-full bg-slate-950/90 border border-slate-700/80 rounded-xl pl-11 pr-24 py-3 text-sm text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all shadow-inner"
          />
          <div className="absolute right-3 flex items-center space-x-2">
            {isSearching && <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />}
            {searchQuery && (
              <button
                onClick={() => {
                  setSearchQuery("");
                  setSearchResults([]);
                  setShowDropdown(false);
                }}
                className="text-slate-400 hover:text-white p-1 rounded-md"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Search Results Autocomplete Dropdown */}
        {showDropdown && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-slate-950 border border-slate-700 rounded-xl shadow-2xl z-50 overflow-hidden divide-y divide-slate-800 max-h-64 overflow-y-auto">
            {searchResults.length > 0 ? (
              searchResults.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSelectSearchResult(item)}
                  className="w-full text-left px-4 py-3 hover:bg-slate-900 flex items-center justify-between transition-colors group"
                >
                  <div className="flex items-center space-x-3">
                    <MapPin className="w-4 h-4 text-cyan-400 group-hover:scale-110 transition-transform" />
                    <div>
                      <span className="text-sm font-semibold text-white block">{item.name}</span>
                      <span className="text-xs text-slate-400 line-clamp-1">{item.display_name}</span>
                    </div>
                  </div>
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                    {item.type}
                  </span>
                </button>
              ))
            ) : !isSearching ? (
              <div className="px-4 py-3 text-xs text-slate-400">
                No location found for &ldquo;{searchQuery}&rdquo;.
              </div>
            ) : null}
          </div>
        )}

        {/* Preset Quick Chips */}
        <div className="flex items-center gap-1.5 overflow-x-auto pt-2.5 pb-1 no-scrollbar text-xs">
          <span className="text-slate-400 font-medium whitespace-nowrap mr-1 flex items-center gap-1">
            <Crosshair className="w-3 h-3 text-cyan-400" /> Popular:
          </span>
          {PRESET_PLACES.map((preset) => {
            const isSelected = selectedCoord.name.toLowerCase().includes(preset.name.toLowerCase().split(" ")[0]);
            return (
              <button
                key={preset.name}
                onClick={() => handleSelectPreset(preset)}
                className={`px-2.5 py-1 rounded-lg font-medium whitespace-nowrap transition-all border ${
                  isSelected
                    ? "bg-cyan-500/20 border-cyan-500/50 text-cyan-300 ring-1 ring-cyan-500/30"
                    : "bg-slate-950/70 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700"
                }`}
              >
                {preset.name}
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Grid: Real Leaflet Map + Selected Location Analysis Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Real Leaflet Map Visual Area (7 cols) */}
        <div className="lg:col-span-7 bg-slate-950 rounded-xl border border-slate-800 p-2 relative min-h-[480px] overflow-hidden shadow-inner flex flex-col justify-between">
          <RealLeafletMap
            center={mapCenter}
            zoom={mapZoom}
            selectedCoord={selectedCoord}
            locations={locations}
            hotspots={hotspots}
            nearestData={nearestData}
            onMapClick={handleMapClick}
            onSelectStation={handleSelectStation}
          />
        </div>

        {/* Selected Location & Nearest Station Analysis Panel (5 cols) */}
        <div className="lg:col-span-5 bg-slate-950/90 rounded-xl border border-slate-800 p-5 flex flex-col justify-between space-y-4 shadow-xl">
          {loadingNearest ? (
            <div className="h-full flex flex-col items-center justify-center py-16 space-y-3">
              <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
              <p className="text-xs text-slate-400 font-mono">Finding nearest monitoring station...</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Selected Location Title & Coordinates */}
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono uppercase tracking-wider font-semibold text-cyan-400 flex items-center gap-1.5">
                    <Navigation className="w-3.5 h-3.5" /> Selected Location
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
                    {selectedCoord.lat.toFixed(4)}, {selectedCoord.lon.toFixed(4)}
                  </span>
                </div>
                <h4 className="text-lg font-bold text-white mt-1 leading-snug">
                  {selectedCoord.name}
                </h4>
              </div>

              {/* Coverage Tier & Distance Card */}
              <div className={`p-3.5 rounded-xl border ${
                nearestData?.coverage_type === "DIRECT"
                  ? "bg-emerald-950/40 border-emerald-500/40 text-emerald-300"
                  : nearestData?.coverage_type === "NEARBY"
                  ? "bg-sky-950/40 border-sky-500/40 text-sky-300"
                  : nearestData?.coverage_type === "EXTENDED"
                  ? "bg-amber-950/40 border-amber-500/40 text-amber-300"
                  : "bg-rose-950/40 border-rose-500/40 text-rose-300"
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {nearestData?.has_nearby_station ? (
                      <ShieldCheck className="w-4 h-4 flex-shrink-0" />
                    ) : (
                      <AlertTriangle className="w-4 h-4 flex-shrink-0 text-rose-400" />
                    )}
                    <span className="text-xs font-bold">{nearestData?.coverage_label}</span>
                  </div>
                  {nearestData?.distance_km !== undefined && (
                    <span className="text-xs font-mono font-bold bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800 text-white">
                      {nearestData.distance_km} km away
                    </span>
                  )}
                </div>

                <div className="mt-2 text-[11px] opacity-90 leading-relaxed">
                  {nearestData?.has_nearby_station && nearestData?.nearest_station ? (
                    <span>
                      Nearest Active Node: <strong className="text-white">{nearestData.nearest_station.name}</strong> ({nearestData.nearest_station.type})
                    </span>
                  ) : (
                    <span>No AeroGuard monitoring source is currently available near this location.</span>
                  )}
                </div>
              </div>

              {/* Actual Available Air Quality Data */}
              {nearestData?.has_nearby_station && nearestData?.air_quality ? (
                <div className="space-y-2.5">
                  <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                    <div>
                      <span className="text-[11px] text-slate-400 block">Reported CPCB AQI</span>
                      <span className="text-xs text-slate-500">
                        Dominant: <strong className="text-slate-300">{nearestData.air_quality.dominant_pollutant}</strong>
                      </span>
                    </div>
                    <div className="text-right">
                      <span
                        className="text-sm font-bold px-2.5 py-1 rounded-lg text-white inline-block shadow-sm"
                        style={{ backgroundColor: getAQIColor(nearestData.air_quality.aqi) }}
                      >
                        {nearestData.air_quality.aqi} — {nearestData.air_quality.category}
                      </span>
                    </div>
                  </div>

                  {/* Pollutant Micro-Grid */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-center">
                      <span className="text-[10px] text-slate-400 block">PM2.5</span>
                      <span className="text-xs font-bold text-white">
                        {nearestData.air_quality.pm25 !== undefined ? `${nearestData.air_quality.pm25.toFixed(1)}` : "—"}
                      </span>
                      <span className="text-[9px] text-slate-500 block">µg/m³</span>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-center">
                      <span className="text-[10px] text-slate-400 block">PM10</span>
                      <span className="text-xs font-bold text-white">
                        {nearestData.air_quality.pm10 !== undefined ? `${nearestData.air_quality.pm10.toFixed(1)}` : "—"}
                      </span>
                      <span className="text-[9px] text-slate-500 block">µg/m³</span>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-center">
                      <span className="text-[10px] text-slate-400 block">NO2</span>
                      <span className="text-xs font-bold text-white">
                        {nearestData.air_quality.no2 !== undefined ? `${nearestData.air_quality.no2.toFixed(1)}` : "—"}
                      </span>
                      <span className="text-[9px] text-slate-500 block">µg/m³</span>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-center">
                      <span className="text-[10px] text-slate-400 block">2h Forecast</span>
                      <span className="text-xs font-bold text-cyan-300">
                        {nearestData.forecast_pm25_2h !== undefined ? `${nearestData.forecast_pm25_2h.toFixed(1)}` : "—"}
                      </span>
                      <span className="text-[9px] text-slate-500 block">µg/m³</span>
                    </div>
                  </div>

                  {/* Public Health Advisory */}
                  <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs space-y-1">
                    <span className="font-semibold text-slate-300 block">CPCB Health Advisory:</span>
                    <p className="text-slate-400 text-[11px] leading-relaxed">
                      {nearestData.air_quality.advisory}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="p-4 rounded-xl bg-slate-900 border border-rose-900/50 text-center space-y-2">
                  <AlertTriangle className="w-6 h-6 text-rose-400 mx-auto" />
                  <h5 className="text-sm font-bold text-white">No Direct Sensor Data</h5>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    AeroGuard does not fabricate sensor readings for unmonitored locations. The nearest registered monitoring node ({nearestData?.nearest_station?.name || "Delhi CAAQMS"}) is {nearestData?.distance_km ?? ">100"} km away, exceeding the configured {maxRadius} km search threshold.
                  </p>
                </div>
              )}

              {/* Scientific Transparency Disclaimer */}
              <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-800/80 flex items-start space-x-2 text-[11px] text-slate-400">
                <Info className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
                <p className="leading-snug">
                  {nearestData?.disclaimer}
                </p>
              </div>
            </div>
          )}

          {/* Search Radius Slider Control */}
          <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span>Search Radius Threshold:</span>
            <div className="flex items-center space-x-2">
              <input
                type="range"
                min="5"
                max="50"
                step="5"
                value={maxRadius}
                onChange={(e) => setMaxRadius(Number(e.target.value))}
                className="w-24 accent-cyan-400 cursor-pointer"
              />
              <span className="font-mono text-white font-bold">{maxRadius} km</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
