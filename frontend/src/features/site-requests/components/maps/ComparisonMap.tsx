"use client";

import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { Loader2, MapPin } from "lucide-react";
import { GeocodingService } from "../../services/geocoding.service";

interface ComparisonMapProps {
  clientOrigin: { lat: number; lng: number; label: string } | null;
  clientDestination: { lat: number; lng: number; label: string } | null;
  clientPolyline?: string | null; 
  driverTrip?: {
    origin: { lat: number; lng: number; label: string };
    destination: { lat: number; lng: number; label: string };
    polyline: string;
  } | null;
  isLoading?: boolean;
}

const createLabelIcon = (color: string, label: string, offsetTop: number = 0) =>
  L.divIcon({
    className: "custom-label",
    html: `<div style="color: ${color}; font-size: 10px; font-weight: 900; white-space: nowrap; text-transform: uppercase; text-shadow: 0 0 3px white, 0 0 3px white, 0 0 3px white; text-align: center; transform: translate(-50%, calc(-50% + ${offsetTop}px));">${label}</div>`,
    iconSize: [0, 0],
    iconAnchor: [0, 0],
  });

const createEndArrowIcon = (color: string, angle: number) =>
  L.divIcon({
    className: "direction-arrow",
    html: `<div style="transform: rotate(${angle}deg); color: ${color}; display: flex; align-items: center; justify-content: center; filter: drop-shadow(0 0 2px white);">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
        <path d="M5 12l14 0M13 5l7 7-7 7" />
      </svg>
    </div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });

export function ComparisonMap({ 
  clientOrigin, 
  clientDestination, 
  clientPolyline,
  driverTrip,
  isLoading = false 
}: ComparisonMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;
    const map = L.map(mapContainerRef.current, { zoomControl: true, scrollWheelZoom: false }).setView([14.6928, -17.4467], 10);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", { attribution: '&copy; CartoDB positron' }).addTo(map);
    mapRef.current = map;
    return () => { if (mapRef.current) { mapRef.current.remove(); mapRef.current = null; } };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    map.eachLayer((layer) => {
      if (layer instanceof L.Polyline || layer instanceof L.Marker || layer instanceof L.CircleMarker) map.removeLayer(layer);
    });

    const bounds = L.latLngBounds([]);

    // 1. CLIENT
    if (clientPolyline) {
      const pts = GeocodingService.decodePolyline(clientPolyline);
      if (pts.length >= 2) {
        const latLngs = pts.map(p => [p.lat, p.lng] as [number, number]);
        L.polyline(latLngs, { color: "#3B82F6", weight: 3, dashArray: "10, 10", opacity: 0.5 }).addTo(map);
        latLngs.forEach(pt => bounds.extend(pt));

        const p1 = pts[pts.length - 2], p2 = pts[pts.length - 1];
        const angle = - Math.atan2(p2.lat - p1.lat, p2.lng - p1.lng) * (180 / Math.PI);
        L.marker([p2.lat, p2.lng], { icon: createEndArrowIcon("#3B82F6", angle), interactive: false }).addTo(map);
      }
    }

    if (clientOrigin) {
      L.marker([clientOrigin.lat, clientOrigin.lng], { icon: createLabelIcon("#3B82F6", `DEMANDE: ${clientOrigin.label}`, -15) }).addTo(map);
      bounds.extend([clientOrigin.lat, clientOrigin.lng]);
    }
    if (clientDestination) {
      L.marker([clientDestination.lat, clientDestination.lng], { icon: createLabelIcon("#3B82F6", `DEMANDE: ${clientDestination.label}`, 15) }).addTo(map);
      bounds.extend([clientDestination.lat, clientDestination.lng]);
    }

    // 2. DRIVER
    if (driverTrip && driverTrip.polyline) {
      let pts = GeocodingService.decodePolyline(driverTrip.polyline);
      if (pts.length >= 2) {
        // AUTO-CORRECTION DU SENS
        // Si le début de la polyline est plus proche de l'arrivée que du départ, on inverse
        if (driverTrip.origin.lat && driverTrip.destination.lat) {
            const dStart0 = Math.hypot(pts[0].lat - driverTrip.origin.lat, pts[0].lng - driverTrip.origin.lng);
            const dStartN = Math.hypot(pts[pts.length-1].lat - driverTrip.origin.lat, pts[pts.length-1].lng - driverTrip.origin.lng);
            if (dStartN < dStart0) {
                pts = [...pts].reverse();
            }
        }

        const latLngs = pts.map(p => [p.lat, p.lng] as [number, number]);
        L.polyline(latLngs, { color: "#EBC33F", weight: 5, opacity: 0.9 }).addTo(map);
        latLngs.forEach(pt => bounds.extend(pt));

        // Flèche de fin (sur le tracé corrigé)
        const p1 = pts[pts.length - 2], p2 = pts[pts.length - 1];
        const angle = - Math.atan2(p2.lat - p1.lat, p2.lng - p1.lng) * (180 / Math.PI);
        L.marker([p2.lat, p2.lng], { icon: createEndArrowIcon("#EBC33F", angle), interactive: false }).addTo(map);

        const startPt: [number, number] = (driverTrip.origin.lat && driverTrip.origin.lng) ? [driverTrip.origin.lat, driverTrip.origin.lng] : latLngs[0];
        const endPt: [number, number] = (driverTrip.destination.lat && driverTrip.destination.lng) ? [driverTrip.destination.lat, driverTrip.destination.lng] : latLngs[latLngs.length - 1];

        L.marker(startPt, { icon: createLabelIcon("#22C55E", `CHAUFFEUR: ${driverTrip.origin.label}`, -15) }).addTo(map);
        L.marker(endPt, { icon: createLabelIcon("#EF4444", `CHAUFFEUR: ${driverTrip.destination.label}`, 15) }).addTo(map);

        if (clientOrigin) L.polyline([[clientOrigin.lat, clientOrigin.lng], startPt], { color: "#22C55E", weight: 2, dashArray: "5, 5", opacity: 0.6 }).addTo(map);
        if (clientDestination) L.polyline([[clientDestination.lat, clientDestination.lng], endPt], { color: "#EF4444", weight: 2, dashArray: "5, 5", opacity: 0.6 }).addTo(map);
      }
    }

    if (bounds.isValid()) {
      map.invalidateSize();
      map.fitBounds(bounds, { padding: [40, 40], animate: false });
    }
  }, [clientOrigin, clientDestination, clientPolyline, driverTrip]);

  return (
    <div className="relative w-full h-[300px] rounded-2xl overflow-hidden border border-border bg-muted/20">
      {isLoading && (
        <div className="absolute inset-0 z-20 bg-white/60 backdrop-blur-sm flex flex-col items-center justify-center space-y-3">
          <Loader2 className="w-8 h-8 text-klando-gold animate-spin" />
          <p className="text-[10px] font-black uppercase tracking-widest text-klando-dark">Mise à jour...</p>
        </div>
      )}
      <div ref={mapContainerRef} className="w-full h-full z-10" />
      <div className="absolute bottom-3 left-3 z-20 flex flex-col gap-1.5 pointer-events-none">
        <div className="flex items-center gap-2 bg-white/90 backdrop-blur px-2 py-1 rounded-md border border-border shadow-sm">
          <div className="w-3 h-3 rounded-full border-2 border-white bg-blue-500 shadow-sm"></div>
          <span className="text-[9px] font-bold uppercase">Demande</span>
        </div>
        <div className="flex items-center gap-2 bg-white/90 backdrop-blur px-2 py-1 rounded-md border border-border shadow-sm">
          <div className="w-3 h-1 bg-klando-gold rounded-full"></div>
          <span className="text-[9px] font-bold uppercase">Trajet Chauffeur</span>
        </div>
      </div>
    </div>
  );
}
