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

// Styles premium pour la carte
const mapStyles = `
  .leaflet-container {
    z-index: 10 !important;
    background: #f8fafc !important;
  }
  .leaflet-control-container {
    z-index: 11 !important;
  }
  .leaflet-bar {
    border: none !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
  }
  .leaflet-bar a {
    background-color: white !important;
    color: #0f172a !important;
    border-bottom: 1px solid #f1f5f9 !important;
  }
  .leaflet-bar a:hover {
    background-color: #f8fafc !important;
    color: #EBC33F !important;
  }
  .custom-marker-shadow {
    filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));
  }
`;

// Icône personnalisée pour markers
const createMarkerIcon = (color: string, label: string) =>
  L.divIcon({
    className: "custom-marker-shadow",
    html: `<div style="
      background-color: ${color};
      width: 18px;
      height: 18px;
      border-radius: 50%;
      border: 4px solid white;
      display: flex;
      align-items: center;
      justify-content: center;
    "></div>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  });

export function TripRouteMap({
  polylineString,
  departureName,
  destinationName,
}: TripRouteMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const routeLayerRef = useRef<L.Polyline | null>(null);
  const markersRef = useRef<L.Marker[]>([]);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Injecter les styles CSS
    const styleElement = document.createElement('style');
    styleElement.textContent = mapStyles;
    document.head.appendChild(styleElement);

    // Initialisation de la carte si elle n'existe pas
    if (!mapRef.current) {
        mapRef.current = L.map(mapContainerRef.current, {
            zoomControl: true,
            scrollWheelZoom: false,
            attributionControl: false
        });

        L.tileLayer(
            "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
            {
                subdomains: "abcd",
                maxZoom: 19,
            }
        ).addTo(mapRef.current);
    }

    // Nettoyage des couches existantes
    if (routeLayerRef.current) {
        mapRef.current.removeLayer(routeLayerRef.current);
    }
    markersRef.current.forEach(marker => mapRef.current?.removeLayer(marker));
    markersRef.current = [];

    // Décoder et tracer
    try {
        const coordinates = polyline.decode(polylineString) as [number, number][];
        if (coordinates.length >= 2) {
            // Ligne du trajet
            routeLayerRef.current = L.polyline(coordinates, {
                color: "#EBC33F",
                weight: 6,
                opacity: 0.8,
                lineJoin: 'round'
            }).addTo(mapRef.current);

            // Markers
            const startMarker = L.marker(coordinates[0], { 
                icon: createMarkerIcon("#22C55E", "Départ") 
            }).addTo(mapRef.current);
            
            const endMarker = L.marker(coordinates[coordinates.length - 1], {
                icon: createMarkerIcon("#EF4444", "Arrivée")
            }).addTo(mapRef.current);

            markersRef.current = [startMarker, endMarker];

            // Ajuster la vue
            mapRef.current.fitBounds(routeLayerRef.current.getBounds(), { 
                padding: [50, 50],
                animate: true
            });
        }
    } catch (e) {
        console.error("Erreur carte:", e);
    }

    return () => {
      styleElement.remove();
    };
  }, [polylineString]); // On re-trace quand le polyline change

  // Nettoyage final au démontage du composant
  useEffect(() => {
    return () => {
        if (mapRef.current) {
            mapRef.current.remove();
            mapRef.current = null;
        }
    };
  }, []);

  return (
    <div
      ref={mapContainerRef}
      className="w-full h-[600px]"
    />
  );
}
