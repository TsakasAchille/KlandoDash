"use client";

import { MapContainer, TileLayer, Polyline, CircleMarker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { MarketingFlowStat } from "@/lib/queries/site-requests";
import { useMemo, useEffect } from "react";
import L from "leaflet";

interface FlowMapProps {
  stats: MarketingFlowStat[];
}

function MapRefresher() {
  const map = useMap();
  useEffect(() => {
    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 100);
    return () => clearTimeout(timer);
  }, [map]);
  return null;
}

export default function FlowMap({ stats }: FlowMapProps) {
  // Fix Leaflet icons issues in Next.js
  useEffect(() => {
    // @ts-ignore
    delete L.Icon.Default.prototype._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
      iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    });
  }, []);

  // Calculer les points chauds (Heatmap simplifiée par cercles)
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

  const maxCount = Math.max(...hotspots.map(h => h.count), 1);

  return (
    <div className="w-full h-[500px] rounded-[2rem] overflow-hidden border border-white/10 shadow-2xl relative bg-slate-900">
      <MapContainer 
        center={[14.7167, -17.4677]} // Dakar
        zoom={9} 
        style={{ height: "100%", width: "100%" }}
        className="z-0"
      >
        {/* Utilisation du style Voyager (plus clair) au lieu de Dark_All */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://carto.com/">CartoDB</a> contributors'
        />
        
        <MapRefresher />

        {/* 1. FLUX (Top Routes) */}
        {stats.map((flow, i) => {
          const weight = Math.max(1, (Number(flow.request_count) / maxCount) * 10);
          return (
            <Polyline 
              key={`flow-${i}`}
              positions={[
                [flow.avg_origin_lat, flow.avg_origin_lng],
                [flow.avg_dest_lat, flow.avg_dest_lng]
              ]}
              pathOptions={{
                color: '#7B1F2F', // Burgundy pour les flux sur carte claire
                weight: weight,
                opacity: 0.3,
                lineCap: 'round',
                dashArray: '5, 10'
              }}
            >
              <Popup>
                <div className="text-[10px] font-black uppercase text-slate-900">
                  {flow.origin_city} ➜ {flow.destination_city}
                  <div className="text-klando-burgundy mt-1">{flow.request_count} demandes</div>
                </div>
              </Popup>
            </Polyline>
          );
        })}

        {/* 2. HEATMAP (Circle Markers) */}
        {hotspots.map((spot, i) => {
          const intensity = spot.count / maxCount;
          const radius = 10 + (intensity * 30);
          return (
            <CircleMarker 
              key={`spot-${i}`}
              center={[spot.lat, spot.lng]}
              pathOptions={{
                fillColor: '#EBC33F',
                fillOpacity: 0.3 + (intensity * 0.4),
                color: 'transparent',
                stroke: false
              }}
              radius={radius}
            >
              <Popup>
                <div className="text-[10px] font-black uppercase text-slate-900">
                  {spot.city}
                  <div className="text-klando-burgundy mt-1">{spot.count} intentions au total</div>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>

      {/* Overlay Legend */}
      <div className="absolute bottom-6 left-6 z-10 bg-white/90 backdrop-blur-md border border-slate-200 p-4 rounded-2xl shadow-2xl">
        <h4 className="text-[10px] font-black uppercase text-slate-900 tracking-widest mb-3">Légende des Flux</h4>
        <div className="space-y-2">
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
