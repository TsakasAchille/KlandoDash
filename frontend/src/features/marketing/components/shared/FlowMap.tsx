"use client";

import { useEffect, useRef, useMemo, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { MarketingFlowStat } from "@/lib/queries/site-requests";
import { Loader2 } from "lucide-react";

interface FlowMapProps {
  stats: MarketingFlowStat[];
}

export default function FlowMap({ stats }: FlowMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const [isMounted, setIsMounted] = useState(false);

  // Fix Leaflet icons issues in Next.js
  useEffect(() => {
    setIsMounted(true);
    // @ts-ignore
    delete L.Icon.Default.prototype._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
      iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    });
  }, []);

  // Initialize Map
  useEffect(() => {
    if (!isMounted || !mapContainerRef.current || mapRef.current) return;

    // Check if container already has a map
    // @ts-ignore
    if (mapContainerRef.current._leaflet_id) return;

    const map = L.map(mapContainerRef.current, {
      center: [14.7167, -17.4677], // Dakar
      zoom: 9,
      scrollWheelZoom: false,
      zoomControl: true,
    });

    L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
      attribution: '&copy; <a href="https://carto.com/">CartoDB</a> contributors',
    }).addTo(map);

    mapRef.current = map;

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [isMounted]);

  // Calculer les hotspots et dessiner les éléments
  const hotspots = useMemo(() => {
    const points: Record<string, { lat: number, lng: number, count: number, city: string }> = {};
    stats.forEach(s => {
      const key = `${s.avg_origin_lat.toFixed(3)},${s.avg_origin_lng.toFixed(3)}`;
      if (!points[key]) {
        points[key] = { lat: s.avg_origin_lat, lng: s.avg_origin_lng, count: 0, city: s.origin_city };
      }
      points[key].count += Number(s.request_count);
    });
    return Object.values(points);
  }, [stats]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    // Nettoyer les couches existantes (hors tuiles)
    map.eachLayer((layer) => {
      if (layer instanceof L.Polyline || layer instanceof L.CircleMarker) {
        map.removeLayer(layer);
      }
    });

    const maxCount = Math.max(...hotspots.map(h => h.count), 1);

    // 1. Dessiner les FLUX
    stats.forEach((flow) => {
      const weight = Math.max(1, (Number(flow.request_count) / maxCount) * 10);
      L.polyline([
        [flow.avg_origin_lat, flow.avg_origin_lng],
        [flow.avg_dest_lat, flow.avg_dest_lng]
      ], {
        color: '#7B1F2F',
        weight: weight,
        opacity: 0.3,
        lineCap: 'round',
        dashArray: '5, 10'
      }).addTo(map).bindPopup(`
        <div style="text-align: left; font-family: sans-serif;">
          <strong style="text-transform: uppercase; font-size: 10px;">${flow.origin_city} ➜ ${flow.destination_city}</strong>
          <div style="color: #7B1F2F; font-size: 10px; font-weight: bold; margin-top: 4px;">${flow.request_count} demandes</div>
        </div>
      `);
    });

    // 2. Dessiner la HEATMAP
    hotspots.forEach((spot) => {
      const intensity = spot.count / maxCount;
      const radius = 10 + (intensity * 30);
      L.circleMarker([spot.lat, spot.lng], {
        fillColor: '#EBC33F',
        fillOpacity: 0.3 + (intensity * 0.4),
        color: 'transparent',
        stroke: false,
        radius: radius
      }).addTo(map).bindPopup(`
        <div style="text-align: left; font-family: sans-serif;">
          <strong style="text-transform: uppercase; font-size: 10px;">${spot.city}</strong>
          <div style="color: #7B1F2F; font-size: 10px; font-weight: bold; margin-top: 4px;">${spot.count} intentions au total</div>
        </div>
      `);
    });

    // Forcer le redimensionnement après un court délai
    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 300);

    return () => clearTimeout(timer);
  }, [stats, hotspots]);

  if (!isMounted) return (
    <div className="w-full h-[500px] rounded-[2rem] bg-slate-900 flex items-center justify-center">
      <Loader2 className="w-8 h-8 text-white/20 animate-spin" />
    </div>
  );

  return (
    <div className="w-full h-[500px] rounded-[2rem] overflow-hidden border border-white/10 shadow-2xl relative bg-slate-900">
      <div ref={mapContainerRef} className="w-full h-full z-0" />
      
      {/* Overlay Legend */}
      <div className="absolute bottom-6 left-6 z-[400] bg-white/90 backdrop-blur-md border border-slate-200 p-4 rounded-2xl shadow-2xl pointer-events-none">
        <h4 className="text-[10px] font-black uppercase text-slate-900 tracking-widest mb-3">Légende des Flux</h4>
        <div className="space-y-2 text-left">
          <div className="flex items-center gap-3">
            <div className="w-6 h-1 bg-klando-burgundy opacity-40 border-t border-dashed border-slate-400"></div>
            <span className="text-[9px] font-bold text-slate-600 uppercase">Volume de demandes</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-4 h-4 rounded-full bg-klando-gold/40"></div>
            <span className="text-[9px] font-bold text-slate-600 uppercase">Zones de chaleur (Hotspots)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
