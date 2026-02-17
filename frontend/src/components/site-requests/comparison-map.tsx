"use client";

import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import * as polyline from "@mapbox/polyline";
import "leaflet/dist/leaflet.css";
import { Loader2, MapPin } from "lucide-react";

interface ComparisonMapProps {
  originCity: string;
  destination_city: string;
  originLat?: number | null;
  originLng?: number | null;
  destLat?: number | null;
  destLng?: number | null;
  recommendedPolyline?: string | null;
  recommendedDepartureCity?: string | null;
  recommendedArrivalCity?: string | null;
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
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
        <path d="M5 12l14 0M13 5l7 7-7 7" />
      </svg>
    </div>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  });

export function ComparisonMap({ 
  originCity, 
  destination_city, 
  originLat,
  originLng,
  destLat,
  destLng,
  recommendedPolyline,
  recommendedDepartureCity,
  recommendedArrivalCity
}: ComparisonMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const initMap = async () => {
      if (!mapContainerRef.current) return;
      try {
        setLoading(true);
        setError(null);
        const geocode = async (city: string) => {
          try {
            const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(city + ", Senegal")}&limit=1`);
            const data = await res.json();
            return (data && data[0]) ? [parseFloat(data[0].lat), parseFloat(data[0].lon)] as [number, number] : null;
          } catch { return null; }
        };
        const originCoords = (originLat && originLng) ? [originLat, originLng] as [number, number] : await geocode(originCity);
        const destCoords = (destLat && destLng) ? [destLat, destLng] as [number, number] : await geocode(destination_city);
        if (!isMounted) return;
        if (!originCoords || !destCoords) { setError("Localisation impossible."); setLoading(false); return; }

        let reqPts: [number, number][] = [originCoords, destCoords];
        try {
          const routeRes = await fetch(`https://router.project-osrm.org/route/v1/driving/${originCoords[1]},${originCoords[0]};${destCoords[1]},${destCoords[0]}?overview=full`);
          const routeData = await routeRes.json();
          if (routeData.routes && routeData.routes[0]) {
            reqPts = polyline.decode(routeData.routes[0].geometry) as [number, number][];
          }
        } catch {}

        if (!isMounted || !mapContainerRef.current) return;
        if (mapRef.current) { mapRef.current.remove(); mapRef.current = null; }
        mapRef.current = L.map(mapContainerRef.current).setView(originCoords, 8);
        L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", { attribution: '&copy; CartoDB positron' }).addTo(mapRef.current);

        const map = mapRef.current;
        const bounds = L.latLngBounds([]);

        // 1. DEMANDE
        L.polyline(reqPts, { color: "#3B82F6", weight: 3, opacity: 0.5, dashArray: "8, 8" }).addTo(map);
        reqPts.forEach(pt => bounds.extend(pt));
        if (reqPts.length >= 2) {
          const p1 = reqPts[reqPts.length - 2], p2 = reqPts[reqPts.length - 1];
          const angle = - Math.atan2(p2[0] - p1[0], p2[1] - p1[1]) * (180 / Math.PI);
          L.marker(p2, { icon: createEndArrowIcon("#3B82F6", angle), interactive: false }).addTo(map);
        }
        L.marker(originCoords, { icon: createLabelIcon("#3B82F6", `DEMANDE: ${originCity.split(',')[0]}`, -15) }).addTo(map);
        L.marker(destCoords, { icon: createLabelIcon("#3B82F6", `DEMANDE: ${destination_city.split(',')[0]}`, 15) }).addTo(map);

        // 2. CHAUFFEUR
        if (recommendedPolyline) {
          try {
            let recPts = polyline.decode(recommendedPolyline) as [number, number][];
            if (recPts.length >= 2) {
              // AUTO-CORRECTION SENS
              const dStart0 = Math.hypot(recPts[0][0] - originCoords[0], recPts[0][1] - originCoords[1]);
              const dStartN = Math.hypot(recPts[recPts.length-1][0] - originCoords[0], recPts[recPts.length-1][1] - originCoords[1]);
              if (dStartN < dStart0) recPts = [...recPts].reverse();

              L.polyline(recPts, { color: "#EBC33F", weight: 5, opacity: 0.9 }).addTo(map);
              recPts.forEach(pt => bounds.extend(pt));
              const p1 = recPts[recPts.length - 2], p2 = recPts[recPts.length - 1];
              const angle = - Math.atan2(p2[0] - p1[0], p2[1] - p1[1]) * (180 / Math.PI);
              L.marker(p2, { icon: createEndArrowIcon("#EBC33F", angle), interactive: false }).addTo(map);

              const startRec = recPts[0], endRec = recPts[recPts.length - 1];
              L.marker(startRec, { icon: createLabelIcon("#22C55E", `CHAUFFEUR: ${recommendedDepartureCity?.split(',')[0] || "Départ"}`, -15) }).addTo(map);
              L.marker(endRec, { icon: createLabelIcon("#EF4444", `CHAUFFEUR: ${recommendedArrivalCity?.split(',')[0] || "Arrivée"}`, 15) }).addTo(map);
              L.polyline([originCoords, startRec], { color: "#22C55E", weight: 2, opacity: 0.6, dashArray: "5, 5" }).addTo(map);
              L.polyline([destCoords, endRec], { color: "#EF4444", weight: 2, opacity: 0.6, dashArray: "5, 5" }).addTo(map);
            }
          } catch {}
        }

        if (isMounted && bounds.isValid()) {
          map.fitBounds(bounds, { padding: [50, 50], animate: false });
          setLoading(false);
        }
      } catch (err) { if (isMounted) setLoading(false); }
    };
    initMap();
    return () => { isMounted = false; };
  }, [originCity, destination_city, originLat, originLng, destLat, destLng, recommendedPolyline, recommendedDepartureCity, recommendedArrivalCity]);

  useEffect(() => { return () => { if (mapRef.current) { mapRef.current.remove(); mapRef.current = null; } }; }, []);

  return (
    <div className="relative w-full h-[300px] rounded-2xl overflow-hidden border border-border bg-muted/20">
      {loading && (
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
