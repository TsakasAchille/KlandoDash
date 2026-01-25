"use client";

import { useEffect, useRef } from "react";
import L from "leaflet";
import * as polyline from "@mapbox/polyline";
import "leaflet/dist/leaflet.css";

interface TripRouteMapProps {
  polylineString: string;
  departureName?: string;
  destinationName?: string;
}

// Icône personnalisée pour markers
const createMarkerIcon = (color: string) =>
  L.divIcon({
    className: "custom-marker",
    html: `<div style="
      background-color: ${color};
      width: 14px;
      height: 14px;
      border-radius: 50%;
      border: 3px solid white;
      box-shadow: 0 2px 6px rgba(0,0,0,0.4);
    "></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
  });

export function TripRouteMap({
  polylineString,
  departureName,
  destinationName,
}: TripRouteMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    // Décoder le polyline
    let coordinates: [number, number][] = [];
    try {
      coordinates = polyline.decode(polylineString) as [number, number][];
    } catch (error) {
      console.error("Erreur décodage polyline:", error);
      return;
    }

    if (coordinates.length < 2) {
      console.warn("Polyline invalide");
      return;
    }

    // Init map
    mapRef.current = L.map(mapContainerRef.current, {
      center: coordinates[Math.floor(coordinates.length / 2)],
      zoom: 10,
      scrollWheelZoom: false,
    });

    // CartoDB dark matter (style sombre)
    L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
      {
        attribution:
          '&copy; <a href="https://carto.com/">CartoDB</a> &copy; <a href="https://openstreetmap.org">OpenStreetMap</a>',
        subdomains: "abcd",
        maxZoom: 19,
      }
    ).addTo(mapRef.current);

    // Tracer la route
    const routeLine = L.polyline(coordinates, {
      color: "#EBC33F", // Klando gold
      weight: 4,
      opacity: 0.9,
    }).addTo(mapRef.current);

    // Marker départ (vert)
    L.marker(coordinates[0], { icon: createMarkerIcon("#22C55E") })
      .bindPopup(`<b>Départ</b><br/>${departureName || "N/A"}`)
      .addTo(mapRef.current);

    // Marker arrivée (rouge)
    L.marker(coordinates[coordinates.length - 1], {
      icon: createMarkerIcon("#EF4444"),
    })
      .bindPopup(`<b>Arrivée</b><br/>${destinationName || "N/A"}`)
      .addTo(mapRef.current);

    // Ajuster le zoom pour voir tout le trajet
    mapRef.current.fitBounds(routeLine.getBounds(), { padding: [30, 30] });

    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, [polylineString, departureName, destinationName]);

  return (
    <div
      ref={mapContainerRef}
      className="w-full h-[300px] rounded-lg overflow-hidden"
    />
  );
}
