"use client";

import { useEffect, useRef, useMemo, useState } from "react";
import L from "leaflet";
import * as polyline from "@mapbox/polyline";
import "leaflet/dist/leaflet.css";
import { TripMapItem } from "@/types/trip";

// Palette de couleurs variées pour distinguer les trajets
const POLYLINE_COLORS = [
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
  "#8B5CF6", // Violet clair
];

// Icône personnalisée pour markers
const createCustomIcon = (color: string) =>
  L.divIcon({
    className: "custom-marker",
    html: `<div style="
      background-color: ${color};
      width: 12px;
      height: 12px;
      border-radius: 50%;
      border: 2px solid white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    "></div>`,
    iconSize: [12, 12],
    iconAnchor: [6, 6],
  });

interface TripMapProps {
  trips: TripMapItem[];
  selectedTrip: TripMapItem | null;
  hoveredTripId: string | null;
  hiddenTripIds: Set<string>;
  initialSelectedId?: string | null;
  onSelectTrip: (trip: TripMapItem) => void;
  onHoverTrip: (tripId: string | null) => void;
}

export function TripMap({
  trips,
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
  const markersRef = useRef<L.Marker[]>([]);
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
          if (!coordinates || coordinates.length < 2) {
            console.warn(`Polyline invalide pour trip ${trip.trip_id}`);
            return null;
          }
          return { ...trip, coordinates };
        } catch (error) {
          console.error(`Erreur decode polyline trip ${trip.trip_id}:`, error);
          return null;
        }
      })
      .filter((t): t is TripMapItem & { coordinates: [number, number][] } => t !== null);
  }, [trips]);

  // Init map
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    mapRef.current = L.map(mapContainerRef.current, {
      center: [14.6937, -17.4441], // Dakar
      zoom: 7,
    });

    // CartoDB positron (même style que Streamlit)
    L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
      attribution: '&copy; <a href="https://carto.com/">CartoDB</a> &copy; <a href="https://openstreetmap.org">OpenStreetMap</a>',
      subdomains: "abcd",
      maxZoom: 19,
    }).addTo(mapRef.current);

    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []);

  // Dessiner les polylines
  useEffect(() => {
    if (!mapRef.current) return;

    // Clear existing polylines
    polylinesRef.current.forEach((p) => p.remove());
    polylinesRef.current.clear();

    // Clear existing markers
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    decodedTrips.forEach((trip, index) => {
      // Skip hidden trips
      if (hiddenTripIds.has(trip.trip_id)) return;

      const isSelected = selectedTrip?.trip_id === trip.trip_id;
      const isHovered = hoveredTripId === trip.trip_id;
      // Couleur unique par trajet (cycle dans la palette)
      const polylineColor = POLYLINE_COLORS[index % POLYLINE_COLORS.length];

      const line = L.polyline(trip.coordinates, {
        color: polylineColor,
        weight: isSelected ? 6 : isHovered ? 5 : 3,
        opacity: isSelected || isHovered ? 1 : 0.7,
        className: isSelected && isHighlighting ? "polyline-pulse" : "",
      });

      line.on("click", () => onSelectTrip(trip));
      line.on("mouseover", () => onHoverTrip(trip.trip_id));
      line.on("mouseout", () => onHoverTrip(null));

      line.addTo(mapRef.current!);
      polylinesRef.current.set(trip.trip_id, line);

      // Markers départ/arrivée pour le trajet sélectionné
      if (isSelected) {
        const coords = trip.coordinates;

        // Marker départ (vert)
        const startMarker = L.marker(coords[0], { icon: createCustomIcon("#22C55E") })
          .bindPopup(`<b>Départ:</b> ${trip.departure_name || "N/A"}`)
          .addTo(mapRef.current!);
        markersRef.current.push(startMarker);

        // Marker arrivée (rouge)
        const endMarker = L.marker(coords[coords.length - 1], { icon: createCustomIcon("#EF4444") })
          .bindPopup(`<b>Arrivée:</b> ${trip.destination_name || "N/A"}`)
          .addTo(mapRef.current!);
        markersRef.current.push(endMarker);
      }
    });
  }, [decodedTrips, selectedTrip, hoveredTripId, hiddenTripIds, isHighlighting, onSelectTrip, onHoverTrip]);

  // Zoom sur trajet sélectionné
  useEffect(() => {
    if (selectedTrip && mapRef.current) {
      const line = polylinesRef.current.get(selectedTrip.trip_id);
      if (line) {
        mapRef.current.fitBounds(line.getBounds(), { padding: [50, 50] });
      }
    }
  }, [selectedTrip]);

  // Auto-zoom sur les trajets visibles quand hiddenTripIds change
  useEffect(() => {
    if (!mapRef.current || polylinesRef.current.size === 0) return;

    // Collecter les bounds de tous les trajets visibles
    const visibleBounds: L.LatLngBounds[] = [];
    polylinesRef.current.forEach((line, tripId) => {
      if (!hiddenTripIds.has(tripId)) {
        visibleBounds.push(line.getBounds());
      }
    });

    // S'il y a des trajets visibles, ajuster le zoom
    if (visibleBounds.length > 0) {
      const combinedBounds = visibleBounds.reduce((acc, bounds) => {
        return acc.extend(bounds);
      }, L.latLngBounds(visibleBounds[0].getSouthWest(), visibleBounds[0].getNorthEast()));

      mapRef.current.fitBounds(combinedBounds, { padding: [50, 50] });
    }
  }, [hiddenTripIds]);

  return (
    <div
      ref={mapContainerRef}
      className="w-full h-full rounded-lg"
      style={{ minHeight: "400px" }}
    />
  );
}
