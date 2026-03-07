"use client";

import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { TripMapItem } from "@/types/trip";
import { SiteTripRequest } from "@/types/site-request";
import { 
  popupStyles, POLYLINE_COLORS, createTripIcon, createRequestStartIcon, createRequestEndIcon 
} from "./map-icons";
import { useTripMapLogic } from "./use-trip-map-logic";

interface TripMapProps {
  trips: TripMapItem[];
  siteRequests?: SiteTripRequest[];
  selectedTrip: TripMapItem | null;
  selectedRequest: SiteTripRequest | null;
  hoveredTripId: string | null;
  hoveredRequestId: string | null;
  hiddenTripIds: Set<string>;
  hiddenRequestIds: Set<string>;
  onSelectTrip: (trip: TripMapItem) => void;
  onSelectRequest: (request: SiteTripRequest) => void;
  onHoverTrip: (tripId: string | null) => void;
  onHoverRequest: (requestId: string | null) => void;
  flowMode?: boolean;
  initialSelectedId?: string | null;
}

export function TripMap({
  trips, siteRequests = [], selectedTrip, selectedRequest,
  hoveredTripId, hoveredRequestId, hiddenTripIds, hiddenRequestIds,
  onSelectTrip, onSelectRequest, onHoverTrip, onHoverRequest, flowMode = false,
  initialSelectedId = null
}: TripMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const layersRef = useRef<{
    trips: Map<string, L.Polyline>,
    requests: Map<string, L.Polyline>,
    markers: L.Layer[],
    flows: L.Layer[]
  }>({ trips: new Map(), requests: new Map(), markers: [], flows: [] });

  const { flows, decodedTrips, decodedRequests } = useTripMapLogic(trips, siteRequests, flowMode);

  // 1. Initialisation Carte
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;
    const styleElement = document.createElement('style');
    styleElement.textContent = popupStyles;
    document.head.appendChild(styleElement);

    mapRef.current = L.map(mapContainerRef.current, { center: [14.6937, -17.4441], zoom: 7 });
    L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
      attribution: '&copy; CartoDB', subdomains: "abcd", maxZoom: 19,
    }).addTo(mapRef.current);

    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
      document.head.removeChild(styleElement);
    };
  }, []);

  // 2. Rendu des Couches
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    // Nettoyage complet
    layersRef.current.trips.forEach(p => p.remove()); layersRef.current.trips.clear();
    layersRef.current.requests.forEach(p => p.remove()); layersRef.current.requests.clear();
    layersRef.current.markers.forEach(m => m.remove()); layersRef.current.markers = [];
    layersRef.current.flows.forEach(l => l.remove()); layersRef.current.flows = [];

    if (flowMode) {
      flows.forEach(f => {
        const line = L.polyline([f.origin, f.dest], { color: "#4f46e5", weight: Math.min(4 + f.count * 2, 15), opacity: 0.7, lineCap: 'round' }).addTo(map);
        line.bindTooltip(`<div class="font-black uppercase text-[10px]">${f.originName} ↔ ${f.destName}<br/>${f.count} Trajets</div>`);
        layersRef.current.flows.push(line);
      });
    } else {
      // Trajets Conducteurs
      decodedTrips.forEach((t, i) => {
        if (hiddenTripIds.has(t.trip_id)) return;
        const isSel = selectedTrip?.trip_id === t.trip_id;
        const isHov = hoveredTripId === t.trip_id;
        const color = isSel ? "#EBC33F" : POLYLINE_COLORS[i % POLYLINE_COLORS.length];
        
        const line = L.polyline(t.coordinates, { color, weight: isSel ? 6 : isHov ? 5 : 3, opacity: isSel || isHov ? 1 : 0.6 })
          .on("click", (e) => { L.DomEvent.stopPropagation(e); onSelectTrip(t); })
          .on("mouseover", () => onHoverTrip(t.trip_id))
          .on("mouseout", () => onHoverTrip(null))
          .addTo(map);
        
        layersRef.current.trips.set(t.trip_id, line);
        if (isSel || isHov) {
          const m = L.marker(t.coordinates[0], { icon: createTripIcon(color, isSel) }).addTo(map);
          layersRef.current.markers.push(m);
        }
      });

      // Demandes Prospects
      decodedRequests.forEach(r => {
        if (hiddenRequestIds.has(r.id)) return;
        const isSel = selectedRequest?.id === r.id;
        const isHov = hoveredRequestId === r.id;
        const line = L.polyline(r.coordinates, { color: "#A855F7", weight: isSel ? 5 : isHov ? 4 : 2, opacity: isSel || isHov ? 0.9 : 0.4, dashArray: isSel ? undefined : "5, 10" })
          .on("click", (e) => { L.DomEvent.stopPropagation(e); onSelectRequest(r); })
          .on("mouseover", () => onHoverRequest(r.id))
          .on("mouseout", () => onHoverRequest(null))
          .addTo(map);
        layersRef.current.requests.set(r.id, line);

        if (r.origin_lat && r.origin_lng) {
          const mStart = L.marker([r.origin_lat, r.origin_lng], { icon: createRequestStartIcon(isSel) }).addTo(map);
          layersRef.current.markers.push(mStart);
        }
      });
    }
  }, [decodedTrips, decodedRequests, flows, flowMode, selectedTrip, selectedRequest, hoveredTripId, hoveredRequestId, hiddenTripIds, hiddenRequestIds]);

  // 3. Gestion Visibilité & Zoom (ResizeObserver)
  useEffect(() => {
    if (!mapRef.current || !mapContainerRef.current) return;
    mapRef.current.invalidateSize();
    const observer = new ResizeObserver(() => mapRef.current?.invalidateSize());
    observer.observe(mapContainerRef.current);

    // Auto-zoom logic
    const allLayers = [...Array.from(layersRef.current.trips.values()), ...Array.from(layersRef.current.requests.values()), ...layersRef.current.flows];
    if (allLayers.length > 0) {
      const group = new L.FeatureGroup(allLayers);
      const bounds = group.getBounds();
      if (bounds.isValid()) mapRef.current.fitBounds(bounds, { padding: [50, 50], animate: false });
    }

    return () => observer.disconnect();
  }, [selectedTrip, selectedRequest, flowMode, decodedTrips.length, decodedRequests.length]);

  return <div ref={mapContainerRef} className="w-full h-full" />;
}
