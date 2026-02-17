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

const createMarkerIcon = (color: string, label: string) =>
  L.divIcon({
    className: "custom-marker",
    html: `<div style="display: flex; flex-direction: column; items-center; transform: translate(-50%, -100%);">
      <div style="background-color: ${color}; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>
      <div style="background: white; color: black; font-size: 9px; font-weight: 900; padding: 2px 6px; border-radius: 4px; border: 1px solid ${color}; margin-top: 2px; white-space: nowrap; text-transform: uppercase; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">${label}</div>
    </div>`,
    iconSize: [0, 0],
    iconAnchor: [0, 0],
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
  const [internalLoading, setInternalLoading] = useState(false);

  // 1. Initialisation unique de la carte
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    console.log("[ComparisonMap] Initializing Map...");
    const map = L.map(mapContainerRef.current, {
      zoomControl: true,
      scrollWheelZoom: false,
    }).setView([14.6928, -17.4467], 10);

    L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
      attribution: '&copy; CartoDB positron'
    }).addTo(map);

    mapRef.current = map;

    return () => {
      if (mapRef.current) {
        console.log("[ComparisonMap] Cleaning up Map...");
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  // 2. Mise à jour des calques (Layers)
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    console.log("[ComparisonMap] Syncing Layers...", { clientOrigin, driverTrip: !!driverTrip });

    // Nettoyage immédiat des anciens calques
    map.eachLayer((layer) => {
      if (layer instanceof L.Polyline || layer instanceof L.Marker || layer instanceof L.CircleMarker) {
        map.removeLayer(layer);
      }
    });

    const bounds = L.latLngBounds([]);

    // Dessiner la polyline client
    if (clientPolyline) {
      console.log("[ComparisonMap] Decoding client polyline...");
      const clientPoints = GeocodingService.decodePolyline(clientPolyline);
      if (clientPoints.length > 0) {
        const latLngs = clientPoints.map(p => [p.lat, p.lng] as [number, number]);
        L.polyline(latLngs, { color: "#3B82F6", weight: 3, dashArray: "8, 8", opacity: 0.5 }).addTo(map);
        latLngs.forEach(pt => bounds.extend(pt));
      }
    }

    // Marqueurs client
    if (clientOrigin) {
      L.marker([clientOrigin.lat, clientOrigin.lng], { 
        icon: createMarkerIcon("#3B82F6", `CLIENT: ${clientOrigin.label}`) 
      }).addTo(map);
      bounds.extend([clientOrigin.lat, clientOrigin.lng]);
    }

    if (clientDestination) {
      L.marker([clientDestination.lat, clientDestination.lng], { 
        icon: createMarkerIcon("#3B82F6", `CLIENT: ${clientDestination.label}`) 
      }).addTo(map);
      bounds.extend([clientDestination.lat, clientDestination.lng]);
    }

    // Trajet Chauffeur & Jonctions
    if (driverTrip && driverTrip.polyline) {
      console.log("[ComparisonMap] Decoding driver polyline...");
      const pathPoints = GeocodingService.decodePolyline(driverTrip.polyline);
      console.log("[ComparisonMap] Decoded driver points:", pathPoints.length);
      
      if (pathPoints.length > 0) {
        const latLngs = pathPoints.map(p => [p.lat, p.lng] as [number, number]);
        L.polyline(latLngs, { color: "#EBC33F", weight: 5, opacity: 0.9 }).addTo(map);
        latLngs.forEach(pt => bounds.extend(pt));

        const startPt = latLngs[0];
        const endPt = latLngs[latLngs.length - 1];

        L.marker(startPt, { icon: createMarkerIcon("#22C55E", `CHAUFFEUR: ${driverTrip.origin.label}`) }).addTo(map);
        L.marker(endPt, { icon: createMarkerIcon("#EF4444", `CHAUFFEUR: ${driverTrip.destination.label}`) }).addTo(map);

        if (clientOrigin) {
          console.log("[ComparisonMap] Drawing departure junction line");
          L.polyline([[clientOrigin.lat, clientOrigin.lng], startPt], { color: "#22C55E", weight: 2.5, dashArray: "5, 5", opacity: 0.8 }).addTo(map);
          L.circleMarker(startPt, { radius: 4, color: "#22C55E", fillColor: "white", fillOpacity: 1, weight: 2 }).addTo(map);
        }
        if (clientDestination) {
          console.log("[ComparisonMap] Drawing arrival junction line");
          L.polyline([[clientDestination.lat, clientDestination.lng], endPt], { color: "#EF4444", weight: 2.5, dashArray: "5, 5", opacity: 0.8 }).addTo(map);
          L.circleMarker(endPt, { radius: 4, color: "#EF4444", fillColor: "white", fillOpacity: 1, weight: 2 }).addTo(map);
        }
      }
    } else {
      console.log("[ComparisonMap] No driverTrip or polyline to draw", { hasDriverTrip: !!driverTrip, hasPolyline: !!driverTrip?.polyline });
    }

    // Ajustement de la vue
    if (bounds.isValid()) {
      map.invalidateSize();
      map.fitBounds(bounds, { padding: [40, 40], animate: false });
    } else {
      console.log("[ComparisonMap] Bounds invalid, skipping fitBounds");
    }

  }, [clientOrigin, clientDestination, clientPolyline, driverTrip]);

  return (
    <div className="relative w-full h-[300px] rounded-2xl overflow-hidden border border-border bg-muted/20">
      {(isLoading || internalLoading) && (
        <div className="absolute inset-0 z-20 bg-white/60 backdrop-blur-sm flex flex-col items-center justify-center space-y-3">
          <Loader2 className="w-8 h-8 text-klando-gold animate-spin" />
          <p className="text-[10px] font-black uppercase tracking-widest text-klando-dark">Mise à jour de la carte...</p>
        </div>
      )}
      
      {!clientOrigin && !isLoading && (
        <div className="absolute inset-0 z-20 flex flex-col items-center justify-center p-6 text-center">
          <MapPin className="w-8 h-8 text-muted-foreground mb-2" />
          <p className="text-xs font-bold text-muted-foreground">Données GPS manquantes</p>
        </div>
      )}

      <div ref={mapContainerRef} className="w-full h-full z-10" />
      
      <div className="absolute bottom-3 left-3 z-20 flex flex-col gap-1.5 pointer-events-none">
        <div className="flex items-center gap-2 bg-white/90 backdrop-blur px-2 py-1 rounded-md border border-border shadow-sm">
          <div className="w-3 h-3 rounded-full border-2 border-white bg-blue-500 shadow-sm"></div>
          <span className="text-[9px] font-bold uppercase">Client</span>
        </div>
        <div className="flex items-center gap-2 bg-white/90 backdrop-blur px-2 py-1 rounded-md border border-border shadow-sm">
          <div className="w-3 h-1 bg-klando-gold rounded-full"></div>
          <span className="text-[9px] font-bold uppercase">Trajet Chauffeur</span>
        </div>
      </div>
    </div>
  );
}
