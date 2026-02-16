"use client";

"use client";

import { useEffect, useRef, useMemo, useState } from "react";
import L from "leaflet";
import * as polyline from "@mapbox/polyline";
import "leaflet/dist/leaflet.css";
import { TripMapItem } from "@/types/trip";
import { SiteTripRequest } from "@/types/site-request";

// CSS personnalisé pour les popups Leaflet et z-index
const popupStyles = `
  .leaflet-popup-content-wrapper {
    background-color: rgba(8, 28, 54, 0.95) !important;
    backdrop-filter: blur(8px);
    color: white !important;
    border-radius: 16px !important;
    border: 1px solid rgba(235, 195, 63, 0.2) !important;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3) !important;
  }
  .leaflet-popup-content {
    color: white !important;
    margin: 12px !important;
    font-family: system-ui, -apple-system, sans-serif !important;
  }
  .leaflet-popup-tip {
    background-color: rgba(8, 28, 54, 0.95) !important;
  }
  .leaflet-popup-close-button {
    color: white !important;
    opacity: 0.8 !important;
    padding: 8px !important;
  }
  
  .leaflet-container {
    z-index: 10 !important;
    background: #f8fafc !important;
  }
  .leaflet-control-container {
    z-index: 11 !important;
  }
  .leaflet-control-zoom {
    border: none !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    border-radius: 12px !important;
    overflow: hidden;
  }
  .leaflet-control-zoom-in, .leaflet-control-zoom-out {
    background-color: white !important;
    color: #081C36 !important;
    border: none !important;
  }
  .leaflet-control-zoom-in:hover, .leaflet-control-zoom-out:hover {
    background-color: #f1f5f9 !important;
    color: #EBC33F !important;
  }
`;

// Palette de couleurs variées pour distinguer les trajets
const POLYLINE_COLORS = [
  "#EBC33F", // Klando Gold
  "#3B82F6", // Bleu
  "#22C55E", // Vert
  "#EF4444", // Rouge
  "#A855F7", // Violet
  "#F97316", // Orange
  "#06B6D4", // Cyan
  "#EC4899", // Rose
  "#84CC16", // Lime
  "#6366F1", // Indigo
  "#14B8A6", // Teal
  "#F59E0B", // Ambre
];

// Icône personnalisée pour markers de trajet
const createTripIcon = (color: string, isSelected: boolean) =>
  L.divIcon({
    className: "custom-trip-marker",
    html: `<div style="
      background-color: ${color};
      width: ${isSelected ? '16px' : '12px'};
      height: ${isSelected ? '16px' : '12px'};
      border-radius: 50%;
      border: 2px solid white;
      box-shadow: 0 2px 10px rgba(0,0,0,0.3);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      ${isSelected ? 'transform: scale(1.2); box-shadow: 0 0 0 4px rgba(235, 195, 63, 0.3);' : ''}
    "></div>`,
    iconSize: isSelected ? [16, 16] : [12, 12],
    iconAnchor: isSelected ? [8, 8] : [6, 6],
  });

// Icône pour les demandes clients
const createRequestIcon = () =>
  L.divIcon({
    className: "custom-request-marker",
    html: `<div style="
      background-color: #A855F7;
      width: 14px;
      height: 14px;
      border-radius: 4px;
      border: 2px solid white;
      box-shadow: 0 2px 10px rgba(168, 85, 247, 0.4);
      transform: rotate(45deg);
    "></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
  });

interface TripMapProps {
  trips: TripMapItem[];
  siteRequests?: SiteTripRequest[];
  selectedTrip: TripMapItem | null;
  hoveredTripId: string | null;
  hiddenTripIds: Set<string>;
  initialSelectedId?: string | null;
  onSelectTrip: (trip: TripMapItem) => void;
  onHoverTrip: (tripId: string | null) => void;
}

export function TripMap({
  trips,
  siteRequests = [],
  selectedTrip,
  hoveredTripId,
  hiddenTripIds,
  initialSelectedId,
  onSelectTrip,
  onHoverTrip,
}: TripMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const polylinesRef = useRef<Map<string, L.Polyline>>(new Map());
  const markersRef = useRef<L.Layer[]>([]);
  const hasHighlighted = useRef(false);
  const [isHighlighting, setIsHighlighting] = useState(false);

  // Highlight temporaire à l'arrivée avec URL param
  useEffect(() => {
    if (initialSelectedId && !hasHighlighted.current) {
      setIsHighlighting(true);
      hasHighlighted.current = true;
      setTimeout(() => setIsHighlighting(false), 2500);
    }
  }, [initialSelectedId]);

  // Décoder les polylines avec gestion d'erreurs
  const decodedTrips = useMemo(() => {
    return trips
      .map((trip) => {
        try {
          if (!trip.polyline) return null;
          const coordinates = polyline.decode(trip.polyline) as [number, number][];
          if (!coordinates || coordinates.length < 2) return null;
          return { ...trip, coordinates };
        } catch {
          return null;
        }
      })
      .filter((t): t is TripMapItem & { coordinates: [number, number][] } => t !== null);
  }, [trips]);

  // Init map
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    const styleElement = document.createElement('style');
    styleElement.textContent = popupStyles;
    document.head.appendChild(styleElement);

    mapRef.current = L.map(mapContainerRef.current, {
      center: [14.6937, -17.4441], // Dakar
      zoom: 7,
      zoomControl: true,
    });

    // Style de carte premium (CartoDB Voyagers)
    L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
      attribution: '&copy; <a href="https://carto.com/">CartoDB</a>',
      subdomains: "abcd",
      maxZoom: 19,
    }).addTo(mapRef.current);

    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
      document.head.removeChild(styleElement);
    };
  }, []);

  // Dessiner les polylines et markers
  useEffect(() => {
    if (!mapRef.current) return;

    polylinesRef.current.forEach((p) => p.remove());
    polylinesRef.current.clear();

    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    // 1. Dessiner les trajets
    decodedTrips.forEach((trip, index) => {
      if (hiddenTripIds.has(trip.trip_id)) return;

      const isSelected = selectedTrip?.trip_id === trip.trip_id;
      const isHovered = hoveredTripId === trip.trip_id;
      const polylineColor = isSelected ? "#EBC33F" : POLYLINE_COLORS[index % POLYLINE_COLORS.length];

      const line = L.polyline(trip.coordinates, {
        color: polylineColor,
        weight: isSelected ? 6 : isHovered ? 5 : 3,
        opacity: isSelected || isHovered ? 1 : 0.6,
        lineCap: 'round',
        lineJoin: 'round',
      });

      line.on("click", () => onSelectTrip(trip));
      line.on("mouseover", () => onHoverTrip(trip.trip_id));
      line.on("mouseout", () => onHoverTrip(null));

      line.addTo(mapRef.current!);
      polylinesRef.current.set(trip.trip_id, line);

      if (isSelected || isHovered) {
        const startMarker = L.marker(trip.coordinates[0], { 
          icon: createTripIcon(polylineColor, isSelected) 
        }).addTo(mapRef.current!);
        markersRef.current.push(startMarker);
      }
    });

    // 2. Dessiner les demandes clients
    siteRequests.forEach((req) => {
      if (!req.origin_lat || !req.origin_lng) return;

      const marker = L.marker([req.origin_lat, req.origin_lng], {
        icon: createRequestIcon()
      }).bindPopup(`
        <div class="space-y-2">
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 rounded-full bg-purple-500 animate-pulse"></div>
            <span class="text-[10px] font-black uppercase tracking-widest text-purple-400">Demande Client</span>
          </div>
          <div class="font-black text-sm uppercase leading-tight">${req.origin_city} ➜ ${req.destination_city}</div>
          <div class="text-[10px] font-bold text-slate-400 uppercase">${req.contact_info}</div>
          ${(req as any).is_estimated ? `
            <div class="mt-2 p-1.5 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
              <p class="text-[8px] font-black text-yellow-500 uppercase tracking-tighter italic">Position approximative (Ville)</p>
            </div>
          ` : ''}
        </div>
      `).addTo(mapRef.current!);
      
      markersRef.current.push(marker);
    });

  }, [decodedTrips, siteRequests, selectedTrip, hoveredTripId, hiddenTripIds, isHighlighting, onSelectTrip, onHoverTrip]);

  // Zoom management
  useEffect(() => {
    if (!mapRef.current) return;

    if (selectedTrip) {
      const line = polylinesRef.current.get(selectedTrip.trip_id);
      if (line) mapRef.current.fitBounds(line.getBounds(), { padding: [100, 100] });
    } else if (polylinesRef.current.size > 0 || markersRef.current.length > 0) {
      const group = new L.FeatureGroup([
        ...Array.from(polylinesRef.current.values()),
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        ...markersRef.current as any[]
      ]);
      if (group.getBounds().isValid()) {
        mapRef.current.fitBounds(group.getBounds(), { padding: [50, 50] });
      }
    }
  }, [selectedTrip, hiddenTripIds, siteRequests.length]);

  return (
    <div
      ref={mapContainerRef}
      className="w-full h-full"
    />
  );
}
