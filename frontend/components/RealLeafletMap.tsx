"use client";

import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { LocationItem, Hotspot, NearestStationResponse } from "../lib/types";

interface RealLeafletMapProps {
  center: [number, number];
  zoom: number;
  selectedCoord: { lat: number; lon: number; name: string };
  locations: LocationItem[];
  hotspots: Hotspot[];
  nearestData: NearestStationResponse | null;
  onMapClick: (lat: number, lon: number) => void;
  onSelectStation: (loc: LocationItem) => void;
}

// Controller component to smoothly fly/pan map when center or zoom changes
function MapFlyController({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, zoom, { duration: 1.2, easeLinearity: 0.25 });
  }, [center, zoom, map]);
  return null;
}

// Click listener component
function MapEventsHandler({ onMapClick }: { onMapClick: (lat: number, lon: number) => void }) {
  useMapEvents({
    click(e) {
      onMapClick(Number(e.latlng.lat.toFixed(5)), Number(e.latlng.lng.toFixed(5)));
    },
  });
  return null;
}

// Helper to create custom HTML DivIcons for Leaflet
function createCustomIcon(type: "selected" | "station" | "sensor" | "hotspot", aqi?: number, label?: string) {
  let innerHtml = "";
  let iconSize: [number, number] = [32, 32];
  let iconAnchor: [number, number] = [16, 32];

  if (type === "selected") {
    iconSize = [36, 36];
    iconAnchor = [18, 36];
    innerHtml = `
      <div style="position: relative; display: flex; align-items: center; justify-content: center; width: 36px; height: 36px;">
        <span style="position: absolute; width: 36px; height: 36px; border-radius: 50%; background: rgba(6, 182, 212, 0.4); animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;"></span>
        <div style="width: 28px; height: 28px; border-radius: 50%; background: #06b6d4; border: 2.5px solid #ffffff; box-shadow: 0 4px 14px rgba(6, 182, 212, 0.7); display: flex; align-items: center; justify-content: center;">
          <svg style="width: 14px; height: 14px; color: #020617;" viewBox="0 0 24 24" fill="currentColor" stroke="none">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
          </svg>
        </div>
      </div>
    `;
  } else if (type === "station") {
    const aqiColor = (aqi ?? 200) <= 100 ? "#10B981" : (aqi ?? 200) <= 200 ? "#EAB308" : (aqi ?? 200) <= 300 ? "#F97316" : "#EF4444";
    innerHtml = `
      <div style="width: 30px; height: 30px; border-radius: 50%; background: ${aqiColor}; border: 2px solid #ffffff; box-shadow: 0 2px 10px rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 10px;">
        🏛️
      </div>
    `;
  } else if (type === "sensor") {
    innerHtml = `
      <div style="width: 26px; height: 26px; border-radius: 50%; background: #0284c7; border: 2px solid #ffffff; box-shadow: 0 2px 8px rgba(2,132,199,0.6); display: flex; align-items: center; justify-content: center; color: white; font-size: 10px;">
        📡
      </div>
    `;
  } else if (type === "hotspot") {
    innerHtml = `
      <div style="width: 32px; height: 32px; border-radius: 50%; background: #dc2626; border: 2px solid #ffffff; box-shadow: 0 0 12px rgba(220,38,38,0.8); display: flex; align-items: center; justify-content: center; color: white; font-size: 13px; animation: pulse 1s infinite;">
        🔥
      </div>
    `;
  }

  return L.divIcon({
    className: "custom-leaflet-marker",
    html: innerHtml,
    iconSize: iconSize,
    iconAnchor: iconAnchor,
  });
}

export default function RealLeafletMap({
  center,
  zoom,
  selectedCoord,
  locations,
  hotspots,
  nearestData,
  onMapClick,
  onSelectStation,
}: RealLeafletMapProps) {
  // Connector line coordinates between selected location and nearest monitoring station
  const connectorCoords = nearestData?.has_nearby_station && nearestData?.nearest_station
    ? [
        [selectedCoord.lat, selectedCoord.lon] as [number, number],
        [nearestData.nearest_station.latitude, nearestData.nearest_station.longitude] as [number, number],
      ]
    : null;

  return (
    <div className="w-full h-full min-h-[480px] rounded-xl overflow-hidden relative z-0">
      <MapContainer
        center={center}
        zoom={zoom}
        scrollWheelZoom={true}
        className="w-full h-full min-h-[480px]"
        style={{ background: "#090d16" }}
      >
        {/* Real Geographic Map Tiles: CartoDB Dark Matter with full road, city, label detail */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions" target="_blank" rel="noreferrer">CARTO</a>'
          subdomains="abcd"
          maxZoom={19}
        />

        {/* Smooth Map Panning Controller */}
        <MapFlyController center={center} zoom={zoom} />

        {/* Map Click Handler */}
        <MapEventsHandler onMapClick={onMapClick} />

        {/* Polyline connector to nearest station if within range */}
        {connectorCoords && (
          <Polyline
            positions={connectorCoords}
            pathOptions={{
              color: "#38bdf8",
              weight: 2.5,
              dashArray: "6, 6",
              opacity: 0.85,
            }}
          />
        )}

        {/* 1. CAAQMS Reference Stations & IoT Nodes */}
        {locations.map((loc) => (
          <Marker
            key={loc.id}
            position={[loc.latitude, loc.longitude]}
            icon={createCustomIcon(loc.is_station ? "station" : "sensor", loc.aqi, loc.name)}
            eventHandlers={{
              click: () => onSelectStation(loc),
            }}
          >
            <Popup className="custom-leaflet-popup">
              <div className="p-1 text-slate-900">
                <span className="text-xs font-bold block">{loc.name}</span>
                <span className="text-[11px] text-slate-600 block">{loc.type}</span>
                <div className="mt-1 flex items-center justify-between text-xs">
                  <span className="font-semibold">AQI: {loc.aqi}</span>
                  <span className="text-slate-500">PM2.5: {loc.pm25.toFixed(1)}</span>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* 2. Pollution Hotspots */}
        {hotspots.map((hs) => (
          <Marker
            key={`hotspot-${hs.id}`}
            position={[hs.latitude, hs.longitude]}
            icon={createCustomIcon("hotspot", hs.current_aqi, hs.location)}
          >
            <Popup className="custom-leaflet-popup">
              <div className="p-1 text-slate-900">
                <span className="text-xs font-bold text-red-600 block">🔥 Hotspot: {hs.location}</span>
                <span className="text-[11px] text-slate-600 block">Severity: {hs.severity_level}</span>
                <span className="text-xs font-semibold block mt-1">AQI: {hs.current_aqi} | PM2.5: {hs.current_pm25.toFixed(1)}</span>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* 3. Selected User Location Marker */}
        <Marker
          position={[selectedCoord.lat, selectedCoord.lon]}
          icon={createCustomIcon("selected", undefined, selectedCoord.name)}
          zIndexOffset={1000}
        >
          <Popup className="custom-leaflet-popup">
            <div className="p-1 text-slate-900">
              <span className="text-xs font-bold text-cyan-700 block">📍 Selected Location</span>
              <span className="text-xs font-semibold block">{selectedCoord.name}</span>
              <span className="text-[10px] text-slate-500 block font-mono">
                {selectedCoord.lat.toFixed(4)}, {selectedCoord.lon.toFixed(4)}
              </span>
            </div>
          </Popup>
        </Marker>
      </MapContainer>
    </div>
  );
}
