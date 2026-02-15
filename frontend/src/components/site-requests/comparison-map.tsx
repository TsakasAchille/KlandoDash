"use client";

import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import * as polyline from "@mapbox/polyline";
import "leaflet/dist/leaflet.css";
import { Loader2, MapPin } from "lucide-react";

interface ComparisonMapProps {
  originCity: string;
  destination_city: string;
  recommendedPolyline?: string | null;
}

const createCustomIcon = (color: string, label: string) =>
  L.divIcon({
    className: "custom-marker",
    html: `<div style="display: flex; flex-col; items-center; transform: translate(-50%, -100%);">
      <div style="
        background-color: ${color};
        width: 14px;
        height: 14px;
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      "></div>
      <div style="
        background: white;
        color: black;
        font-size: 10px;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid ${color};
        margin-left: 4px;
        white-space: nowrap;
      ">${label}</div>
    </div>`,
    iconSize: [0, 0],
    iconAnchor: [0, 0],
  });

export function ComparisonMap({ originCity, destination_city, recommendedPolyline }: ComparisonMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Geocoding and Routing
  useEffect(() => {
    if (!mapContainerRef.current) return;

    const initMap = async () => {
      try {
        setLoading(true);
        setError(null);

        // Geocode requested cities
        const geocode = async (city: string) => {
          const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(city + ", Senegal")}&limit=1`);
          const data = await res.json();
          if (data && data[0]) {
            return [parseFloat(data[0].lat), parseFloat(data[0].lon)] as [number, number];
          }
          return null;
        };

        const [originCoords, destCoords] = await Promise.all([
          geocode(originCity),
          geocode(destination_city)
        ]);

        if (!originCoords || !destCoords) {
          setError("Impossible de localiser les villes sur la carte.");
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

        // Initialize Map if not already done
        if (!mapRef.current) {
          mapRef.current = L.map(mapContainerRef.current).setView(originCoords, 8);
          L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
            attribution: '&copy; CartoDB positron'
          }).addTo(mapRef.current);
        } else {
          // Clear previous layers
          mapRef.current.eachLayer((layer) => {
            if (layer instanceof L.Polyline || layer instanceof L.Marker) {
              mapRef.current?.removeLayer(layer);
            }
          });
        }

        const map = mapRef.current;
        const bounds = L.latLngBounds([]);

        // 1. Draw Requested Trip (Dashed Blue)
        const reqLine = L.polyline(requestedPolylineCoords, {
          color: "#3B82F6",
          weight: 4,
          opacity: 0.6,
          dashArray: "10, 10"
        }).addTo(map);
        bounds.extend(reqLine.getBounds());

        // Markers for requested trip
        L.marker(originCoords, { icon: createCustomIcon("#3B82F6", "Départ voulu") }).addTo(map);
        L.marker(destCoords, { icon: createCustomIcon("#3B82F6", "Arrivée voulue") }).addTo(map);

        // 2. Draw Recommended Trip (Solid Gold)
        if (recommendedPolyline) {
          try {
            const recCoords = polyline.decode(recommendedPolyline) as [number, number][];
            const recLine = L.polyline(recCoords, {
              color: "#EBC33F",
              weight: 6,
              opacity: 0.9,
            }).addTo(map);
            bounds.extend(recLine.getBounds());
            
            // Markers for recommended trip
            L.marker(recCoords[0], { icon: createCustomIcon("#22C55E", "Conducteur départ") }).addTo(map);
            L.marker(recCoords[recCoords.length - 1], { icon: createCustomIcon("#EF4444", "Conducteur arrivée") }).addTo(map);
          } catch (e) {
            console.error("Failed to decode recommended polyline", e);
          }
        }

        if (!bounds.isValid()) {
          map.setView(originCoords, 10);
        } else {
          map.fitBounds(bounds, { padding: [40, 40] });
        }

        setLoading(false);
      } catch (err) {
        console.error("Map error:", err);
        setError("Erreur lors de l'initialisation de la carte.");
        setLoading(false);
      }
    };

    initMap();

    return () => {
      // Don't remove map entirely to avoid flickering if we update results,
      // but initMap handles clearing layers.
    };
  }, [originCity, destination_city, recommendedPolyline]);

  // Handle cleanup on unmount
  useEffect(() => {
    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
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
            <span className="text-[9px] font-bold uppercase">Proposition Chauffeur</span>
          </div>
        </div>
      )}
    </div>
  );
}
