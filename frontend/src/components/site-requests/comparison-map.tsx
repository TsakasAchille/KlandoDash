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

const createCustomIcon = (color: string, label: string) =>
  L.divIcon({
    className: "custom-marker",
    html: `<div style="display: flex; flex-direction: column; items-center; transform: translate(-50%, -100%);">
      <div style="
        background-color: ${color};
        width: 14px;
        height: 14px;
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        margin: 0 auto;
      "></div>
      <div style="
        background: white;
        color: black;
        font-size: 9px;
        font-weight: 900;
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid ${color};
        margin-top: 2px;
        white-space: nowrap;
        text-transform: uppercase;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
      ">${label}</div>
    </div>`,
    iconSize: [0, 0],
    iconAnchor: [0, 0],
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

  // Geocoding and Routing
  useEffect(() => {
    let isMounted = true;

    const initMap = async () => {
      if (!mapContainerRef.current) return;

      try {
        setLoading(true);
        setError(null);

        // Geocode requested cities (Fallback if GPS coords are missing)
        const geocode = async (city: string) => {
          try {
            const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(city + ", Senegal")}&limit=1`);
            const data = await res.json();
            if (data && data[0]) {
              return [parseFloat(data[0].lat), parseFloat(data[0].lon)] as [number, number];
            }
          } catch (e) {
            console.warn(`Geocoding failed for ${city}`, e);
          }
          return null;
        };

        // Strict GPS detection
        const hasOriginGPS = originLat !== null && originLat !== undefined && originLng !== null && originLng !== undefined;
        const hasDestGPS = destLat !== null && destLat !== undefined && destLng !== null && destLng !== undefined;

        const originCoords: [number, number] | null = hasOriginGPS 
          ? [originLat as number, originLng as number] 
          : await geocode(originCity);

        const destCoords: [number, number] | null = hasDestGPS
          ? [destLat as number, destLng as number]
          : await geocode(destination_city);

        if (!isMounted) return;

        if (!originCoords || !destCoords) {
          setError("Localisation impossible.");
          setLoading(false);
          return;
        }

        // Try to get a route for requested trip (OSRM)
        let requestedPolylineCoords: [number, number][] = [originCoords, destCoords];
        try {
          const routeRes = await fetch(`https://router.project-osrm.org/route/v1/driving/${originCoords[1]},${originCoords[0]};${destCoords[1]},${destCoords[0]}?overview=full`);
          const routeData = await routeRes.json();
          if (routeData.routes && routeData.routes[0]) {
            requestedPolylineCoords = polyline.decode(routeData.routes[0].geometry) as [number, number][];
          }
        } catch (e) {
          console.warn("Routing failed, using straight line", e);
        }

        if (!isMounted || !mapContainerRef.current) return;

        // Force cleanup if map already exists
        if (mapRef.current) {
          mapRef.current.remove();
          mapRef.current = null;
        }

        // Re-init Map
        mapRef.current = L.map(mapContainerRef.current).setView(originCoords, 8);
        L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
          attribution: '&copy; CartoDB positron'
        }).addTo(mapRef.current);

        const map = mapRef.current;
        const bounds = L.latLngBounds([]);

        // 1. Draw Requested Trip (Dashed Blue)
        const reqLine = L.polyline(requestedPolylineCoords, {
          color: "#3B82F6",
          weight: 3,
          opacity: 0.5,
          dashArray: "8, 8"
        }).addTo(map);
        bounds.extend(reqLine.getBounds());

        // Markers for requested trip
        L.marker(originCoords, { icon: createCustomIcon("#3B82F6", `CLIENT: ${originCity.split(',')[0]}`) }).addTo(map);
        L.marker(destCoords, { icon: createCustomIcon("#3B82F6", `CLIENT: ${destination_city.split(',')[0]}`) }).addTo(map);

        // 2. Draw Recommended Trip (Solid Gold)
        if (recommendedPolyline) {
          try {
            const recCoords = polyline.decode(recommendedPolyline) as [number, number][];
            if (recCoords.length > 0) {
              const recLine = L.polyline(recCoords, {
                color: "#EBC33F",
                weight: 5,
                opacity: 0.9,
              }).addTo(map);
              bounds.extend(recLine.getBounds());
              
              const startRec = recCoords[0];
              const endRec = recCoords[recCoords.length - 1];

              // Markers for recommended trip
              L.marker(startRec, { icon: createCustomIcon("#22C55E", `CONDUCTEUR: ${recommendedDepartureCity?.split(',')[0] || "Départ"}`) }).addTo(map);
              L.marker(endRec, { icon: createCustomIcon("#EF4444", `CONDUCTEUR: ${recommendedArrivalCity?.split(',')[0] || "Arrivée"}`) }).addTo(map);

              // 3. DRAW JUNCTION LINES
              // Green dashed line for departure gap
              L.polyline([originCoords, startRec], {
                color: "#22C55E",
                weight: 2.5,
                opacity: 0.8,
                dashArray: "5, 5"
              }).addTo(map);

              // Red dashed line for arrival gap
              L.polyline([destCoords, endRec], {
                color: "#EF4444",
                weight: 2.5,
                opacity: 0.8,
                dashArray: "5, 5"
              }).addTo(map);

              // Visual anchor circles at driver points
              L.circleMarker(startRec, { radius: 4, color: "#22C55E", fillColor: "white", fillOpacity: 1, weight: 2 }).addTo(map);
              L.circleMarker(endRec, { radius: 4, color: "#EF4444", fillColor: "white", fillOpacity: 1, weight: 2 }).addTo(map);
            }
          } catch (e) {
            console.error("Failed to decode recommended polyline", e);
          }
        }

        if (isMounted) {
          if (!bounds.isValid()) {
            map.setView(originCoords, 10);
          } else {
            map.fitBounds(bounds, { padding: [50, 50] });
          }
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          console.error("Map error:", err);
          setError("Erreur lors de l'initialisation de la carte.");
          setLoading(false);
        }
      }
    };

    initMap();

    return () => {
      isMounted = false;
    };
  }, [originCity, destination_city, originLat, originLng, destLat, destLng, recommendedPolyline, recommendedDepartureCity, recommendedArrivalCity]);

  // Handle cleanup on unmount
  useEffect(() => {
    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  return (
    <div className="relative w-full h-[300px] rounded-2xl overflow-hidden border border-border bg-muted/20">
      {loading && (
        <div className="absolute inset-0 z-20 bg-white/60 backdrop-blur-sm flex flex-col items-center justify-center space-y-3">
          <Loader2 className="w-8 h-8 text-klando-gold animate-spin" />
          <p className="text-[10px] font-black uppercase tracking-widest text-klando-dark">Calcul de l&apos;itinéraire...</p>
        </div>
      )}
      
      {error && !loading && (
        <div className="absolute inset-0 z-20 flex flex-col items-center justify-center p-6 text-center">
          <MapPin className="w-8 h-8 text-muted-foreground mb-2" />
          <p className="text-xs font-bold text-muted-foreground">{error}</p>
        </div>
      )}

      <div ref={mapContainerRef} className="w-full h-full z-10" />
      
      {!loading && !error && (
        <div className="absolute bottom-3 left-3 z-20 flex flex-col gap-1.5">
          <div className="flex items-center gap-2 bg-white/90 backdrop-blur px-2 py-1 rounded-md border border-border shadow-sm">
            <div className="w-3 h-0.5 bg-blue-500 border-t border-dashed border-blue-500" style={{ borderTopStyle: 'dashed' }}></div>
            <span className="text-[9px] font-bold uppercase">Demande Client</span>
          </div>
          <div className="flex items-center gap-2 bg-white/90 backdrop-blur px-2 py-1 rounded-md border border-border shadow-sm">
            <div className="w-3 h-1 bg-klando-gold rounded-full"></div>
            <span className="text-[9px] font-bold uppercase">Trajet Proposé</span>
          </div>
        </div>
      )}
    </div>
  );
}
