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

  @keyframes pulse {
    0% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.2); opacity: 0.8; }
    100% { transform: scale(1); opacity: 1; }
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

// Icône pour les demandes clients (Départ)
const createRequestStartIcon = (isSelected: boolean) =>
  L.divIcon({
    className: "custom-request-start",
    html: `<div style="
      background-color: #22C55E;
      width: ${isSelected ? '18px' : '14px'};
      height: ${isSelected ? '18px' : '14px'};
      border-radius: 50%;
      border: 3px solid white;
      box-shadow: 0 0 15px rgba(34, 197, 94, 0.6);
      display: flex;
      align-items: center;
      justify-content: center;
      ${isSelected ? 'animation: pulse 2s infinite;' : ''}
    ">
      <div style="width: 4px; height: 4px; background: white; border-radius: 50%;"></div>
    </div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });

// Icône pour les demandes clients (Arrivée)
const createRequestEndIcon = (isSelected: boolean) =>
  L.divIcon({
    className: "custom-request-end",
    html: `<div style="
      background-color: #EF4444;
      width: ${isSelected ? '18px' : '14px'};
      height: ${isSelected ? '18px' : '14px'};
      border-radius: 3px;
      border: 3px solid white;
      box-shadow: 0 0 15px rgba(239, 68, 68, 0.6);
      transform: rotate(45deg);
      display: flex;
      align-items: center;
      justify-content: center;
      ${isSelected ? 'animation: pulse 2s infinite;' : ''}
    ">
      <div style="width: 4px; height: 4px; background: white; transform: rotate(-45deg);"></div>
    </div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });

// On garde l'icône générique pour le survol ou les états simples
const createRequestIcon = () =>
  L.divIcon({
    className: "custom-request-marker",
    html: `<div style="
      background-color: #A855F7;
      width: 12px;
      height: 12px;
      border-radius: 3px;
      border: 2px solid white;
      box-shadow: 0 2px 10px rgba(168, 85, 247, 0.4);
      transform: rotate(45deg);
    "></div>`,
    iconSize: [12, 12],
    iconAnchor: [6, 6],
  });

interface TripMapProps {
  trips: TripMapItem[];
  siteRequests?: SiteTripRequest[];
  selectedTrip: TripMapItem | null;
  selectedRequest: SiteTripRequest | null;
  hoveredTripId: string | null;
  hoveredRequestId: string | null;
  hiddenTripIds: Set<string>;
  hiddenRequestIds: Set<string>;
  initialSelectedId?: string | null;
  onSelectTrip: (trip: TripMapItem) => void;
  onSelectRequest: (request: SiteTripRequest) => void;
  onHoverTrip: (tripId: string | null) => void;
  onHoverRequest: (requestId: string | null) => void;
}

export function TripMap({
  trips,
  siteRequests = [],
  selectedTrip,
  selectedRequest,
  hoveredTripId,
  hoveredRequestId,
  hiddenTripIds,
  hiddenRequestIds,
  initialSelectedId,
  onSelectTrip,
  onSelectRequest,
  onHoverTrip,
  onHoverRequest,
}: TripMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const polylinesRef = useRef<Map<string, L.Polyline>>(new Map());
  const requestPolylinesRef = useRef<Map<string, L.Polyline>>(new Map());
  const matchLinesRef = useRef<L.Layer[]>([]);
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

  const decodedRequests = useMemo(() => {
    return siteRequests
      .map((req) => {
        try {
          if (!req.polyline) return null;
          const coordinates = polyline.decode(req.polyline) as [number, number][];
          if (!coordinates || coordinates.length < 2) return null;
          return { ...req, coordinates };
        } catch {
          return null;
        }
      })
      .filter((r): r is SiteTripRequest & { coordinates: [number, number][] } => r !== null);
  }, [siteRequests]);

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
    
    requestPolylinesRef.current.forEach((p) => p.remove());
    requestPolylinesRef.current.clear();

    matchLinesRef.current.forEach((l) => l.remove());
    matchLinesRef.current = [];

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

      line.on("click", (e) => {
        L.DomEvent.stopPropagation(e);
        onSelectTrip(trip);
      });
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

    // 2. Dessiner les polylines des demandes clients
    decodedRequests.forEach((req) => {
      if (hiddenRequestIds.has(req.id)) return;

      const isSelected = selectedRequest?.id === req.id;
      const isHovered = hoveredRequestId === req.id;

      const line = L.polyline(req.coordinates, {
        color: "#A855F7", // Violet
        weight: isSelected ? 5 : isHovered ? 4 : 2,
        opacity: isSelected || isHovered ? 0.9 : 0.4,
        dashArray: isSelected ? undefined : "5, 10", // Pointillés si pas sélectionné
        lineCap: 'round',
        lineJoin: 'round',
      });

      line.on("click", (e) => {
        L.DomEvent.stopPropagation(e);
        onSelectRequest(req);
      });
      line.on("mouseover", () => onHoverRequest(req.id));
      line.on("mouseout", () => onHoverRequest(null));

      line.addTo(mapRef.current!);
      requestPolylinesRef.current.set(req.id, line);
    });

    // 3. Dessiner les marqueurs des demandes clients
    siteRequests.forEach((req) => {
      if (hiddenRequestIds.has(req.id)) return;
      if (!req.origin_lat || !req.origin_lng) return;

      const isSelected = selectedRequest?.id === req.id;
      const isHovered = hoveredRequestId === req.id;

      // Marqueur Départ (Vert)
      const startMarker = L.marker([req.origin_lat, req.origin_lng], {
        icon: createRequestStartIcon(isSelected),
        zIndexOffset: isSelected || isHovered ? 1000 : 0
      }).on("click", (e) => {
        L.DomEvent.stopPropagation(e);
        onSelectRequest(req);
      }).addTo(mapRef.current!);

      if (isSelected) {
        startMarker.bindTooltip("DÉPART CLIENT", { permanent: true, direction: "top", className: "font-black text-[8px] bg-green-600 text-white border-none rounded-md px-2 py-1 shadow-lg" }).openTooltip();
      }
      
      markersRef.current.push(startMarker);

      // Marqueur Arrivée (Rouge) - uniquement si on a les coordonnées
      if (req.destination_lat && req.destination_lng) {
        const endMarker = L.marker([req.destination_lat, req.destination_lng], {
          icon: createRequestEndIcon(isSelected),
          zIndexOffset: isSelected || isHovered ? 1000 : 0
        }).on("click", (e) => {
          L.DomEvent.stopPropagation(e);
          onSelectRequest(req);
        }).addTo(mapRef.current!);

        if (isSelected) {
          endMarker.bindTooltip("ARRIVÉE CLIENT", { permanent: true, direction: "top", className: "font-black text-[8px] bg-red-600 text-white border-none rounded-md px-2 py-1 shadow-lg" }).openTooltip();
        }
        
        markersRef.current.push(endMarker);
      }
    });

    // 4. Dessiner les lignes de liaison pour les matches (si une demande est sélectionnée)
    if (selectedRequest && selectedRequest.origin_lat && selectedRequest.origin_lng) {
      const matchedTripIds = selectedRequest.matches?.map(m => m.trip_id) || [];
      
      decodedTrips.forEach(trip => {
        // On ne dessine la liaison que si le trajet est un match ET n'est pas caché
        if (matchedTripIds.includes(trip.trip_id) && !hiddenTripIds.has(trip.trip_id)) {
          
          // A. Ligne de liaison : Départ Client ➜ Départ Trajet (Coordonnées explicites)
          if (trip.departure_latitude && trip.departure_longitude) {
            const startLine = L.polyline([
              [selectedRequest.origin_lat!, selectedRequest.origin_lng!],
              [trip.departure_latitude, trip.departure_longitude]
            ], {
              color: "#22C55E", // Vert
              weight: 1.5,
              opacity: 0.7,
              dashArray: "4, 6",
              interactive: false
            }).addTo(mapRef.current!);
            
            matchLinesRef.current.push(startLine);

            // Petit ancrage visuel au point de départ du trajet
            const startAnchor = L.circleMarker([trip.departure_latitude, trip.departure_longitude], {
              radius: 3,
              fillColor: "#22C55E",
              color: "white",
              weight: 1,
              fillOpacity: 1
            }).addTo(mapRef.current!);
            matchLinesRef.current.push(startAnchor);
          }

          // B. Ligne de liaison : Arrivée Client ➜ Arrivée Trajet (Coordonnées explicites)
          if (selectedRequest.destination_lat && selectedRequest.destination_lng && trip.destination_latitude && trip.destination_longitude) {
            const endLine = L.polyline([
              [selectedRequest.destination_lat!, selectedRequest.destination_lng!],
              [trip.destination_latitude, trip.destination_longitude]
            ], {
              color: "#EF4444", // Rouge
              weight: 1.5,
              opacity: 0.7,
              dashArray: "4, 6",
              interactive: false
            }).addTo(mapRef.current!);
            
            matchLinesRef.current.push(endLine);

            // Petit ancrage visuel au point d'arrivée du trajet
            const endAnchor = L.circleMarker([trip.destination_latitude, trip.destination_longitude], {
              radius: 3,
              fillColor: "#EF4444",
              color: "white",
              weight: 1,
              fillOpacity: 1
            }).addTo(mapRef.current!);
            matchLinesRef.current.push(endAnchor);
          }
        }
      });
    }

  }, [decodedTrips, decodedRequests, siteRequests, selectedTrip, selectedRequest, hoveredTripId, hoveredRequestId, hiddenTripIds, hiddenRequestIds, isHighlighting, onSelectTrip, onSelectRequest, onHoverTrip, onHoverRequest]);

  // Zoom management
  useEffect(() => {
    if (!mapRef.current) return;

    if (selectedTrip) {
      const line = polylinesRef.current.get(selectedTrip.trip_id);
      if (line) mapRef.current.fitBounds(line.getBounds(), { padding: [100, 100] });
    } else if (selectedRequest) {
      const line = requestPolylinesRef.current.get(selectedRequest.id);
      if (line) {
        mapRef.current.fitBounds(line.getBounds(), { padding: [100, 100] });
      } else if (selectedRequest.origin_lat && selectedRequest.origin_lng) {
        mapRef.current.setView([selectedRequest.origin_lat, selectedRequest.origin_lng], 13);
      }
    } else if (polylinesRef.current.size > 0 || requestPolylinesRef.current.size > 0 || markersRef.current.length > 0) {
      const allLayers = [
        ...Array.from(polylinesRef.current.values()),
        ...Array.from(requestPolylinesRef.current.values()),
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        ...markersRef.current as any[]
      ];
      
      if (allLayers.length > 0) {
        const group = new L.FeatureGroup(allLayers);
        if (group.getBounds().isValid()) {
          mapRef.current.fitBounds(group.getBounds(), { padding: [50, 50] });
        }
      }
    }
  }, [selectedTrip, selectedRequest, hiddenTripIds, hiddenRequestIds, trips.length, siteRequests.length]);

  return (
    <div
      ref={mapContainerRef}
      className="w-full h-full"
    />
  );
}
