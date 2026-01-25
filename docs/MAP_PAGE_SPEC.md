# Spécification - Page Map (Carte des Trajets)

## Vue d'ensemble

Nouvelle page `/map` affichant une carte interactive des trajets Klando avec :
- Visualisation des polylines de tous les trajets
- Filtrage par statut, date, conducteur
- Tableau des 10 derniers trajets
- Détails au clic sur une polyline
- Navigation vers profils conducteur/passagers et page trajet

---

## Architecture

### Structure des fichiers

```
frontend/src/
├── app/
│   └── map/
│       ├── page.tsx              # Server Component (données initiales)
│       └── map-client.tsx        # Client Component (état UI)
├── components/
│   └── map/
│       ├── trip-map.tsx          # Carte Leaflet avec polylines
│       ├── trip-map-popup.tsx    # Popup détails trajet
│       ├── map-filters.tsx       # Filtres (statut, date, conducteur)
│       └── recent-trips-table.tsx # Tableau 10 derniers trajets
└── lib/
    └── queries/
        └── trips.ts              # + getTripsForMap()
```

---

## Flux de données

```
┌─────────────────────────────────────────────────────────────────┐
│  Server Component: /app/map/page.tsx                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  await Promise.all([                                     │    │
│  │    getTripsForMap(50),       // Trajets avec polyline   │    │
│  │    getTripsStats(),          // Stats header            │    │
│  │    getDriversList()          // Pour filtre conducteur  │    │
│  │  ])                                                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼ props                             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Client Component: map-client.tsx                        │    │
│  │                                                          │    │
│  │  State:                                                  │    │
│  │  - selectedTrip: TripMapItem | null                      │    │
│  │  - filters: { status, dateRange, driverId }             │    │
│  │  - hoveredTrip: string | null                           │    │
│  │                                                          │    │
│  │  URL State:                                              │    │
│  │  - ?selectedTrip=xxx (sync avec router.replace)         │    │
│  │  - ?status=ACTIVE&driver=uid (filtres persistés)        │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
    ┌──────────┐       ┌──────────┐       ┌──────────────┐
    │ TripMap  │       │ Filters  │       │ RecentTrips  │
    │          │       │          │       │ Table        │
    │ Leaflet  │◄─────►│ Status   │       │              │
    │ Polylines│       │ Date     │       │ 10 derniers  │
    │ Popups   │       │ Driver   │       │ Cliquables   │
    └──────────┘       └──────────┘       └──────────────┘
```

---

## Types TypeScript

### Nouveau type pour la carte

```typescript
// types/trip.ts

export interface TripMapItem {
  trip_id: string;
  departure_name: string;
  destination_name: string;
  departure_lat: number;
  departure_lng: number;
  destination_lat: number;
  destination_lng: number;
  polyline: string;              // Encoded polyline
  status: TripStatus;
  departure_schedule: string;
  price_per_seat: number;
  available_seats: number;
  total_seats: number;
  distance: number;
  driver: {
    uid: string;
    display_name: string;
    photo_url: string | null;
    rating: number;
  };
  passengers: Array<{
    uid: string;
    display_name: string;
    photo_url: string | null;
  }>;
}

export interface MapFilters {
  status: TripStatus | "ALL";
  dateFrom: string | null;
  dateTo: string | null;
  driverId: string | null;
}
```

---

## Requêtes Supabase

### Nouvelle query: `getTripsForMap()`

```typescript
// lib/queries/trips.ts

export async function getTripsForMap(limit = 100): Promise<TripMapItem[]> {
  const { data, error } = await supabase
    .from("trips")
    .select(`
      trip_id,
      departure_name,
      destination_name,
      departure_lat,
      departure_lng,
      destination_lat,
      destination_lng,
      polyline,
      status,
      departure_schedule,
      price_per_seat,
      available_seats,
      total_seats,
      distance,
      driver:users!fk_driver (
        uid,
        display_name,
        photo_url,
        rating
      )
    `)
    .not("polyline", "is", null)        // Seulement trajets avec polyline
    .order("departure_schedule", { ascending: false })
    .limit(limit);

  if (error) throw error;

  // Flatten driver + ajouter passengers (query séparée ou join bookings)
  return data.map(trip => ({
    ...trip,
    driver: Array.isArray(trip.driver) ? trip.driver[0] : trip.driver,
    passengers: []  // Enrichi via getPassengersForTrip si sélectionné
  }));
}

// Query passagers pour le popup détail
export async function getPassengersForTrip(tripId: string) {
  const { data, error } = await supabase
    .from("bookings")
    .select(`
      user:users (
        uid,
        display_name,
        photo_url
      )
    `)
    .eq("trip_id", tripId)
    .eq("status", "CONFIRMED");

  if (error) throw error;
  return data?.map(b => b.user).filter(Boolean) || [];
}

// Liste conducteurs pour filtre
export async function getDriversList() {
  const { data, error } = await supabase
    .from("users")
    .select("uid, display_name")
    .eq("role", "driver")
    .order("display_name");

  if (error) throw error;
  return data || [];
}
```

---

## Composants

### 1. Server Page: `/app/map/page.tsx`

```typescript
import { Suspense } from "react";
import { getTripsForMap, getTripsStats, getDriversList } from "@/lib/queries/trips";
import { MapClient } from "./map-client";

interface MapPageProps {
  searchParams: Promise<{
    selectedTrip?: string;
    status?: string;
    driver?: string;
  }>;
}

export default async function MapPage({ searchParams }: MapPageProps) {
  const params = await searchParams;
  const selectedTripId = params.selectedTrip || null;
  const statusFilter = params.status || "ALL";
  const driverFilter = params.driver || null;

  const [trips, stats, drivers] = await Promise.all([
    getTripsForMap(50),  // Limite 50 par défaut (voir section Volumétrie)
    getTripsStats(),
    getDriversList(),
  ]);

  const initialSelectedTrip = selectedTripId
    ? trips.find((t) => t.trip_id === selectedTripId) || null
    : null;

  return (
    <div className="flex flex-col h-full">
      {/* Header avec stats */}
      <div className="flex items-center justify-between p-4 border-b border-gray-800">
        <h1 className="text-2xl font-bold text-klando-gold">
          Carte des Trajets
        </h1>
        <div className="flex gap-4">
          <Badge>{stats.total_trips} trajets</Badge>
          <Badge variant="success">{stats.active_trips} actifs</Badge>
        </div>
      </div>

      {/* Client Component */}
      <MapClient
        trips={trips}
        drivers={drivers}
        initialSelectedTrip={initialSelectedTrip}
        initialStatusFilter={statusFilter}
        initialDriverFilter={driverFilter}
      />
    </div>
  );
}
```

### 2. Client Component: `map-client.tsx`

```typescript
"use client";

import { useState, useCallback, useMemo, useEffect } from "react";
import { useRouter } from "next/navigation";
import { TripMap } from "@/components/map/trip-map";
import { MapFilters } from "@/components/map/map-filters";
import { RecentTripsTable } from "@/components/map/recent-trips-table";
import { TripMapPopup } from "@/components/map/trip-map-popup";
import { getPassengersForTrip } from "@/lib/queries/trips";

interface MapClientProps {
  trips: TripMapItem[];
  drivers: Array<{ uid: string; display_name: string }>;
  initialSelectedTrip: TripMapItem | null;
  initialStatusFilter: string;
  initialDriverFilter: string | null;
}

export function MapClient({
  trips,
  drivers,
  initialSelectedTrip,
  initialStatusFilter,
  initialDriverFilter,
}: MapClientProps) {
  const router = useRouter();

  // State
  const [selectedTrip, setSelectedTrip] = useState(initialSelectedTrip);
  const [filters, setFilters] = useState<MapFilters>({
    status: initialStatusFilter as TripStatus | "ALL",
    dateFrom: null,
    dateTo: null,
    driverId: initialDriverFilter,
  });
  const [hoveredTripId, setHoveredTripId] = useState<string | null>(null);

  // Fetch passagers uniquement pour le trajet sélectionné (évite N+1)
  useEffect(() => {
    if (selectedTrip && selectedTrip.passengers.length === 0) {
      fetch(`/api/trips/${selectedTrip.trip_id}/passengers`)
        .then(res => res.json())
        .then(passengers => {
          setSelectedTrip(prev => prev ? { ...prev, passengers } : null);
        })
        .catch(console.error);
    }
  }, [selectedTrip?.trip_id]);

  // Pre-fetch pages liées (UX premium)
  useEffect(() => {
    if (selectedTrip) {
      router.prefetch(`/users?selectedUser=${selectedTrip.driver.uid}`);
      router.prefetch(`/trips?selectedTrip=${selectedTrip.trip_id}`);
    }
  }, [selectedTrip, router]);

  // Filtrage des trajets (client-side MVP)
  const filteredTrips = useMemo(() => {
    return trips.filter((trip) => {
      if (filters.status !== "ALL" && trip.status !== filters.status) return false;
      if (filters.driverId && trip.driver.uid !== filters.driverId) return false;
      if (filters.dateFrom) {
        const tripDate = new Date(trip.departure_schedule);
        if (tripDate < new Date(filters.dateFrom)) return false;
      }
      if (filters.dateTo) {
        const tripDate = new Date(trip.departure_schedule);
        if (tripDate > new Date(filters.dateTo)) return false;
      }
      return true;
    });
  }, [trips, filters]);

  // 10 derniers trajets filtrés
  const recentTrips = useMemo(() => {
    return filteredTrips.slice(0, 10);
  }, [filteredTrips]);

  // Sélection avec sync URL (convention: selectedTrip)
  const handleSelectTrip = useCallback((trip: TripMapItem) => {
    setSelectedTrip(trip);
    const url = new URL(window.location.href);
    url.searchParams.set("selectedTrip", trip.trip_id);
    router.replace(url.pathname + url.search, { scroll: false });
  }, [router]);

  // Mise à jour filtres avec sync URL
  const handleFilterChange = useCallback((newFilters: Partial<MapFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    const url = new URL(window.location.href);
    if (newFilters.status !== undefined) {
      newFilters.status === "ALL"
        ? url.searchParams.delete("status")
        : url.searchParams.set("status", newFilters.status);
    }
    if (newFilters.driverId !== undefined) {
      newFilters.driverId === null
        ? url.searchParams.delete("driver")
        : url.searchParams.set("driver", newFilters.driverId);
    }
    router.replace(url.pathname + url.search, { scroll: false });
  }, [router]);

  return (
    <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-4 p-4">
      {/* Colonne gauche: Filtres + Tableau */}
      <div className="lg:col-span-1 flex flex-col gap-4">
        <MapFilters
          filters={filters}
          drivers={drivers}
          onFilterChange={handleFilterChange}
        />
        <RecentTripsTable
          trips={recentTrips}
          selectedTripId={selectedTrip?.trip_id}
          hoveredTripId={hoveredTripId}
          onSelectTrip={handleSelectTrip}
          onHoverTrip={setHoveredTripId}
        />
      </div>

      {/* Colonne droite: Carte */}
      <div className="lg:col-span-3 relative min-h-[500px]">
        <TripMap
          trips={filteredTrips}
          selectedTrip={selectedTrip}
          hoveredTripId={hoveredTripId}
          onSelectTrip={handleSelectTrip}
          onHoverTrip={setHoveredTripId}
        />

        {/* Popup détails (overlay sur la carte) */}
        {selectedTrip && (
          <TripMapPopup
            trip={selectedTrip}
            onClose={() => {
              setSelectedTrip(null);
              const url = new URL(window.location.href);
              url.searchParams.delete("selectedTrip");
              router.replace(url.pathname + url.search, { scroll: false });
            }}
          />
        )}
      </div>
    </div>
  );
}
```

### 3. Composant Carte: `trip-map.tsx`

```typescript
"use client";

import { useEffect, useRef, useMemo, useState } from "react";
import L from "leaflet";
import polyline from "polyline";
import "leaflet/dist/leaflet.css";

// Couleurs par statut
// Couleurs par statut
const STATUS_COLORS: Record<TripStatus, string> = {
  ACTIVE: "#3B82F6",      // Bleu
  COMPLETED: "#22C55E",   // Vert
  PENDING: "#EAB308",     // Jaune
  CANCELLED: "#EF4444",   // Rouge
  ARCHIVED: "#6B7280",    // Gris
};

// Fix Leaflet default icon path (requis avec bundlers)
import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";

const DefaultIcon = L.icon({
  iconUrl: icon.src,
  shadowUrl: iconShadow.src,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

// Icônes personnalisées (style Streamlit)
const createCustomIcon = (color: string) => L.divIcon({
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
  initialSelectedId?: string;  // Pour highlight à l'arrivée
  onSelectTrip: (trip: TripMapItem) => void;
  onHoverTrip: (tripId: string | null) => void;
}

export function TripMap({
  trips,
  selectedTrip,
  hoveredTripId,
  initialSelectedId,
  onSelectTrip,
  onHoverTrip,
}: TripMapProps) {
  const mapRef = useRef<L.Map | null>(null);
  const polylinesRef = useRef<Map<string, L.Polyline>>(new Map());
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
      .map(trip => {
        try {
          const coordinates = polyline.decode(trip.polyline) as [number, number][];

          // Validation minimale
          if (!coordinates || coordinates.length < 2) {
            console.warn(`Polyline invalide pour trip ${trip.trip_id}`);
            return null;
          }

          return { ...trip, coordinates };
        } catch (error) {
          console.error(`Erreur decode polyline trip ${trip.trip_id}:`, error);
          return null; // Fallback silencieux
        }
      })
      .filter((t): t is NonNullable<typeof t> => t !== null);
  }, [trips]);

  // Init map
  useEffect(() => {
    if (!mapRef.current) {
      // Centre sur le Sénégal
      mapRef.current = L.map("trip-map", {
        center: [14.6937, -17.4441], // Dakar
        zoom: 7,
      });

      // CartoDB positron (même style que Streamlit legacy)
      L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
        attribution: '© <a href="https://carto.com/">CartoDB</a> © <a href="https://openstreetmap.org">OpenStreetMap</a>',
        subdomains: "abcd",
        maxZoom: 19,
      }).addTo(mapRef.current);
    }

    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []);

  // Dessiner les polylines
  useEffect(() => {
    if (!mapRef.current) return;

    // Clear existing
    polylinesRef.current.forEach(p => p.remove());
    polylinesRef.current.clear();

    decodedTrips.forEach(trip => {
      const isSelected = selectedTrip?.trip_id === trip.trip_id;
      const isHovered = hoveredTripId === trip.trip_id;

      const line = L.polyline(trip.coordinates, {
        color: STATUS_COLORS[trip.status],
        weight: isSelected ? 6 : isHovered ? 5 : 3,
        opacity: isSelected || isHovered ? 1 : 0.7,
        // Animation pulse pour highlight temporaire
        className: isSelected && isHighlighting ? "polyline-pulse" : "",
      });

      line.on("click", () => onSelectTrip(trip));
      line.on("mouseover", () => onHoverTrip(trip.trip_id));
      line.on("mouseout", () => onHoverTrip(null));

      line.addTo(mapRef.current!);
      polylinesRef.current.set(trip.trip_id, line);

      // Markers départ/arrivée (style Streamlit)
      if (isSelected) {
        const coords = trip.coordinates;

        // Marker départ (vert)
        L.marker(coords[0], { icon: createCustomIcon("#22C55E") })
          .bindPopup(`<b>Départ:</b> ${trip.departure_name}`)
          .addTo(mapRef.current!);

        // Marker arrivée (rouge)
        L.marker(coords[coords.length - 1], { icon: createCustomIcon("#EF4444") })
          .bindPopup(`<b>Arrivée:</b> ${trip.destination_name}`)
          .addTo(mapRef.current!);
      }
    });
  }, [decodedTrips, selectedTrip, hoveredTripId, isHighlighting, onSelectTrip, onHoverTrip]);

  // Zoom sur trajet sélectionné
  useEffect(() => {
    if (selectedTrip && mapRef.current) {
      const line = polylinesRef.current.get(selectedTrip.trip_id);
      if (line) {
        mapRef.current.fitBounds(line.getBounds(), { padding: [50, 50] });
      }
    }
  }, [selectedTrip]);

  return <div id="trip-map" className="w-full h-full rounded-lg" />;
}
```

### 4. Popup Détails: `trip-map-popup.tsx`

```typescript
"use client";

import Link from "next/link";
import { X, User, Users, MapPin, Calendar, Car, ExternalLink } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { formatDate, formatPrice } from "@/lib/utils";

interface TripMapPopupProps {
  trip: TripMapItem;
  onClose: () => void;
}

export function TripMapPopup({ trip, onClose }: TripMapPopupProps) {
  return (
    <Card className="absolute top-4 right-4 w-80 z-[1000] bg-klando-dark border-gray-700">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg text-klando-gold">
            Détails du trajet
          </CardTitle>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Itinéraire */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-green-500" />
            <span className="text-sm">{trip.departure_name}</span>
          </div>
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-red-500" />
            <span className="text-sm">{trip.destination_name}</span>
          </div>
        </div>

        {/* Infos */}
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-gray-400" />
            <span>{formatDate(trip.departure_schedule)}</span>
          </div>
          <div className="flex items-center gap-2">
            <Car className="w-4 h-4 text-gray-400" />
            <span>{trip.available_seats}/{trip.total_seats} places</span>
          </div>
        </div>

        {/* Prix + Status */}
        <div className="flex items-center justify-between">
          <span className="text-lg font-bold text-klando-gold">
            {formatPrice(trip.price_per_seat)}
          </span>
          <Badge variant={trip.status.toLowerCase()}>
            {trip.status}
          </Badge>
        </div>

        {/* Conducteur */}
        <div className="border-t border-gray-700 pt-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Avatar className="w-8 h-8">
                <AvatarImage src={trip.driver.photo_url || ""} />
                <AvatarFallback>
                  {trip.driver.display_name?.charAt(0)}
                </AvatarFallback>
              </Avatar>
              <div>
                <p className="text-sm font-medium">{trip.driver.display_name}</p>
                <p className="text-xs text-gray-400">
                  ⭐ {trip.driver.rating?.toFixed(1) || "N/A"}
                </p>
              </div>
            </div>
            <Link href={`/users?selectedUser=${trip.driver.uid}`}>
              <Button variant="outline" size="sm">
                <User className="w-4 h-4 mr-1" />
                Profil
              </Button>
            </Link>
          </div>
        </div>

        {/* Passagers */}
        {trip.passengers.length > 0 && (
          <div className="border-t border-gray-700 pt-3">
            <p className="text-sm text-gray-400 mb-2">
              <Users className="w-4 h-4 inline mr-1" />
              {trip.passengers.length} passager(s)
            </p>
            <div className="flex flex-wrap gap-2">
              {trip.passengers.map((p) => (
                <Link key={p.uid} href={`/users?selectedUser=${p.uid}`}>
                  <Avatar className="w-6 h-6 cursor-pointer hover:ring-2 ring-klando-gold">
                    <AvatarImage src={p.photo_url || ""} />
                    <AvatarFallback className="text-xs">
                      {p.display_name?.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="border-t border-gray-700 pt-3">
          <Link href={`/trips?selectedTrip=${trip.trip_id}`}>
            <Button className="w-full bg-klando-burgundy hover:bg-klando-burgundy/80">
              <ExternalLink className="w-4 h-4 mr-2" />
              Voir page trajet
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
```

### 5. Filtres: `map-filters.tsx`

```typescript
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface MapFiltersProps {
  filters: MapFilters;
  drivers: Array<{ uid: string; display_name: string }>;
  onFilterChange: (filters: Partial<MapFilters>) => void;
}

export function MapFilters({ filters, drivers, onFilterChange }: MapFiltersProps) {
  return (
    <Card className="bg-klando-dark border-gray-700">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm text-klando-gold">Filtres</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Statut */}
        <div className="space-y-1">
          <Label className="text-xs">Statut</Label>
          <Select
            value={filters.status}
            onValueChange={(value) => onFilterChange({ status: value as any })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">Tous</SelectItem>
              <SelectItem value="ACTIVE">Actifs</SelectItem>
              <SelectItem value="COMPLETED">Terminés</SelectItem>
              <SelectItem value="PENDING">En attente</SelectItem>
              <SelectItem value="CANCELLED">Annulés</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Conducteur */}
        <div className="space-y-1">
          <Label className="text-xs">Conducteur</Label>
          <Select
            value={filters.driverId || "ALL"}
            onValueChange={(value) =>
              onFilterChange({ driverId: value === "ALL" ? null : value })
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="Tous les conducteurs" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">Tous</SelectItem>
              {drivers.map((d) => (
                <SelectItem key={d.uid} value={d.uid}>
                  {d.display_name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Date de début */}
        <div className="space-y-1">
          <Label className="text-xs">Date début</Label>
          <Input
            type="date"
            value={filters.dateFrom || ""}
            onChange={(e) => onFilterChange({ dateFrom: e.target.value || null })}
          />
        </div>

        {/* Date de fin */}
        <div className="space-y-1">
          <Label className="text-xs">Date fin</Label>
          <Input
            type="date"
            value={filters.dateTo || ""}
            onChange={(e) => onFilterChange({ dateTo: e.target.value || null })}
          />
        </div>
      </CardContent>
    </Card>
  );
}
```

### 6. Tableau Récents: `recent-trips-table.tsx`

```typescript
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import { cn } from "@/lib/utils";

interface RecentTripsTableProps {
  trips: TripMapItem[];
  selectedTripId: string | undefined;
  hoveredTripId: string | null;
  onSelectTrip: (trip: TripMapItem) => void;
  onHoverTrip: (tripId: string | null) => void;
}

export function RecentTripsTable({
  trips,
  selectedTripId,
  hoveredTripId,
  onSelectTrip,
  onHoverTrip,
}: RecentTripsTableProps) {
  return (
    <Card className="bg-klando-dark border-gray-700 flex-1 overflow-hidden">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm text-klando-gold">
          10 Derniers Trajets
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="max-h-[400px] overflow-y-auto">
          <Table>
            <TableBody>
              {trips.map((trip) => (
                <TableRow
                  key={trip.trip_id}
                  className={cn(
                    "cursor-pointer transition-colors",
                    selectedTripId === trip.trip_id && "bg-klando-burgundy/30",
                    hoveredTripId === trip.trip_id && "bg-gray-800"
                  )}
                  onClick={() => onSelectTrip(trip)}
                  onMouseEnter={() => onHoverTrip(trip.trip_id)}
                  onMouseLeave={() => onHoverTrip(null)}
                >
                  <TableCell className="py-2">
                    <div className="space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-medium truncate max-w-[120px]">
                          {trip.departure_name}
                        </span>
                        <Badge variant={trip.status.toLowerCase()} className="text-[10px]">
                          {trip.status}
                        </Badge>
                      </div>
                      <div className="text-xs text-gray-400">
                        → {trip.destination_name}
                      </div>
                      <div className="text-[10px] text-gray-500">
                        {formatDate(trip.departure_schedule)}
                      </div>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
```

---

## Navigation inter-pages

### Convention URL normalisée

```
/map?selectedTrip=xxx&status=ACTIVE&driver=uid
/trips?selectedTrip=xxx
/users?selectedUser=xxx
```

### Liens sortants (depuis Map)

| Élément | Destination | Paramètre |
|---------|-------------|-----------|
| Popup → Bouton "Profil" conducteur | `/users?selectedUser={driver_id}` | UID conducteur |
| Popup → Avatar passager | `/users?selectedUser={user_id}` | UID passager |
| Popup → Bouton "Voir page trajet" | `/trips?selectedTrip={trip_id}` | ID trajet |

### Liens entrants (vers Map)

| Source | Lien | Effet |
|--------|------|-------|
| Sidebar | `/map` | Page carte vide |
| Trip details | `/map?selectedTrip={trip_id}` | Zoom + popup + highlight |
| User profile | `/map?driver={uid}` | Filtré sur conducteur |

---

## API Route: Passagers

```typescript
// app/api/trips/[tripId]/passengers/route.ts

import { NextRequest } from "next/server";
import { getPassengersForTrip } from "@/lib/queries/trips";

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ tripId: string }> }
) {
  const { tripId } = await params;

  try {
    const passengers = await getPassengersForTrip(tripId);
    return Response.json(passengers);
  } catch (error) {
    console.error("Error fetching passengers:", error);
    return Response.json({ error: "Failed to fetch passengers" }, { status: 500 });
  }
}
```

---

## Dépendances à installer

```bash
cd frontend
npm install leaflet @types/leaflet @mapbox/polyline
```

> Note: Utiliser `@mapbox/polyline` (le package `polyline` est deprecated).

### Cohérence avec Streamlit legacy

La version Streamlit utilise **Folium** (wrapper Python de Leaflet.js). Pour assurer une cohérence visuelle:

| Élément | Streamlit | Next.js |
|---------|-----------|---------|
| Tiles | CartoDB positron | CartoDB positron ✅ |
| Polyline decode | `polyline.decode()` | `polyline.decode()` ✅ |
| Bibliothèque base | Leaflet.js | Leaflet.js ✅ |

---

## CSS Animation (globals.css)

```css
/* Animation pulse pour highlight polyline à l'arrivée */
@keyframes polyline-pulse {
  0%, 100% {
    stroke-opacity: 1;
    stroke-width: 6px;
  }
  50% {
    stroke-opacity: 0.5;
    stroke-width: 10px;
  }
}

.polyline-pulse path {
  animation: polyline-pulse 0.8s ease-in-out 3;
}

/* Fix Leaflet z-index avec Shadcn */
.leaflet-pane {
  z-index: 1;
}
.leaflet-control {
  z-index: 2;
}

/* Custom markers */
.custom-marker {
  background: transparent;
  border: none;
}

/* Leaflet popup style (dark theme) */
.leaflet-popup-content-wrapper {
  background: #081C36;
  color: white;
  border-radius: 8px;
}
.leaflet-popup-tip {
  background: #081C36;
}
```

---

## Ajout au Sidebar

```typescript
// components/sidebar.tsx

const navItems = [
  { href: "/", label: "Accueil", icon: Home },
  { href: "/trips", label: "Trajets", icon: Car },
  { href: "/users", label: "Utilisateurs", icon: Users },
  { href: "/map", label: "Carte", icon: Map },  // ← Ajouter
  { href: "/stats", label: "Statistiques", icon: BarChart },
  { href: "/chats", label: "Messages", icon: MessageSquare },
];
```

---

## Index Supabase recommandé

```sql
-- Pour le filtre sur polyline non-null
CREATE INDEX idx_trips_polyline_not_null
ON trips (departure_schedule DESC)
WHERE polyline IS NOT NULL;

-- Pour le filtre par conducteur
-- Déjà existant: idx_trips_driver_id
```

---

## Résumé des fonctionnalités

| Fonctionnalité | Implémentation |
|----------------|----------------|
| ✅ Carte avec polylines | Leaflet + polyline decode |
| ✅ Filtres (statut, date, conducteur) | `MapFilters` component |
| ✅ Tableau 10 derniers trajets | `RecentTripsTable` component |
| ✅ Clic polyline → détails | `TripMapPopup` overlay |
| ✅ Lien vers profil conducteur | `Link` vers `/users?selected=` |
| ✅ Lien vers profil passagers | `Link` vers `/users?selected=` |
| ✅ Lien vers page trajet | `Link` vers `/trips?selected=` |
| ✅ URL state management | `router.replace` + searchParams |
| ✅ Hover sync table ↔ carte | `hoveredTripId` state |
| ✅ Supabase optimisé | Colonnes spécifiques, index |

---

## Estimation composants

| Composant | Complexité | Lignes estimées |
|-----------|------------|-----------------|
| `page.tsx` | Simple | ~40 |
| `map-client.tsx` | Moyenne | ~100 |
| `trip-map.tsx` | Complexe | ~120 |
| `trip-map-popup.tsx` | Moyenne | ~100 |
| `map-filters.tsx` | Simple | ~80 |
| `recent-trips-table.tsx` | Simple | ~70 |
| Queries additions | Simple | ~50 |
| Types additions | Simple | ~30 |
| **Total** | | **~590 lignes** |

---

## ⚠️ Points d'attention et recommandations

### 1. Volumétrie et performance

**Limite par défaut: 30-50 trajets** (pas 100)

```typescript
// lib/queries/trips.ts
export async function getTripsForMap(limit = 50): Promise<TripMapItem[]> {
```

**Stratégie de scaling:**
| Volume | Stratégie |
|--------|-----------|
| < 100 trajets | Chargement initial complet |
| 100-500 | Filtres obligatoires (date ou driver) |
| 500+ | Bounding box dynamique (viewport carte) |

**Future évolution (bounding box):**
```typescript
// Charger uniquement les trajets visibles
async function getTripsInBounds(bounds: L.LatLngBounds, limit = 50) {
  const { data } = await supabase
    .from("trips")
    .select("...")
    .gte("departure_lat", bounds.getSouth())
    .lte("departure_lat", bounds.getNorth())
    .gte("departure_lng", bounds.getWest())
    .lte("departure_lng", bounds.getEast())
    .limit(limit);
}
```

### 2. Filtrage: client → server

**MVP: filtrage côté client** ✅
```typescript
const filteredTrips = useMemo(() => trips.filter(...), [trips, filters]);
```

**Production: switch vers server-side**
```typescript
// Quand les filtres changent → refetch server
const handleFilterChange = useCallback(async (newFilters) => {
  setFilters(newFilters);

  // MVP: client filter
  // Production: server fetch
  if (ENABLE_SERVER_FILTERING) {
    const filtered = await getTripsForMap({
      status: newFilters.status,
      driverId: newFilters.driverId,
      dateFrom: newFilters.dateFrom,
      dateTo: newFilters.dateTo,
    });
    setTrips(filtered);
  }
}, []);
```

### 3. Convention URL stricte

**Format normalisé cross-pages:**

```
/map?selectedTrip=xxx&status=ACTIVE&driver=uid
/trips?selectedTrip=xxx
/users?selectedUser=xxx
```

| Paramètre | Type | Pages | Description |
|-----------|------|-------|-------------|
| `selectedTrip` | UUID | /map, /trips | ID trajet sélectionné |
| `selectedUser` | UUID | /users | ID utilisateur sélectionné |
| `status` | Enum | /map, /trips | Filtre statut |
| `driver` | UUID | /map | Filtre conducteur |

**Migration:** Renommer `selected` → `selectedTrip` / `selectedUser` pour éviter ambiguïtés.

### 4. Passagers: éviter N+1

**❌ JAMAIS faire:**
```typescript
// N+1 catastrophique
const tripsWithPassengers = await Promise.all(
  trips.map(t => getPassengersForTrip(t.trip_id))
);
```

**✅ Pattern correct:**
```typescript
// Fetch passagers uniquement pour le trajet sélectionné
useEffect(() => {
  if (selectedTrip) {
    getPassengersForTrip(selectedTrip.trip_id)
      .then(passengers => {
        setSelectedTrip(prev => prev ? { ...prev, passengers } : null);
      });
  }
}, [selectedTrip?.trip_id]);
```

**API route recommandée:**
```typescript
// /api/trips/[tripId]/passengers
export async function GET(req, { params }) {
  const passengers = await getPassengersForTrip(params.tripId);
  return Response.json(passengers);
}
```

### 5. Pre-fetch intelligent (UX premium)

```typescript
// map-client.tsx
import { useRouter } from "next/navigation";

// Pre-fetch pages liées au trajet sélectionné
useEffect(() => {
  if (selectedTrip) {
    // Pre-fetch profil conducteur
    router.prefetch(`/users?selectedUser=${selectedTrip.driver.uid}`);
    // Pre-fetch page trajet
    router.prefetch(`/trips?selectedTrip=${selectedTrip.trip_id}`);
  }
}, [selectedTrip, router]);
```

**Résultat:** Navigation instantanée vers profil/trajet.

### 6. Highlight temporaire à l'arrivée

**Animation pulse sur polyline sélectionnée:**

```typescript
// trip-map.tsx
const [isHighlighting, setIsHighlighting] = useState(false);

// Trigger highlight à l'arrivée avec URL param
useEffect(() => {
  if (initialSelectedId && !hasHighlighted.current) {
    setIsHighlighting(true);
    hasHighlighted.current = true;

    setTimeout(() => setIsHighlighting(false), 2500);
  }
}, [initialSelectedId]);

// Style polyline avec animation
const line = L.polyline(trip.coordinates, {
  color: STATUS_COLORS[trip.status],
  weight: isSelected ? 6 : isHovered ? 5 : 3,
  opacity: isSelected || isHovered ? 1 : 0.7,
  className: isSelected && isHighlighting ? "polyline-pulse" : "",
});
```

**CSS animation:**
```css
/* globals.css */
@keyframes polyline-pulse {
  0%, 100% { stroke-opacity: 1; stroke-width: 6px; }
  50% { stroke-opacity: 0.5; stroke-width: 10px; }
}

.polyline-pulse {
  animation: polyline-pulse 0.8s ease-in-out 3;
}
```

### 7. Gestion erreurs polyline

```typescript
// trip-map.tsx
const decodedTrips = useMemo(() => {
  return trips
    .map(trip => {
      try {
        const coordinates = polyline.decode(trip.polyline) as [number, number][];

        // Validation minimale
        if (!coordinates || coordinates.length < 2) {
          console.warn(`Polyline invalide pour trip ${trip.trip_id}`);
          return null;
        }

        return { ...trip, coordinates };
      } catch (error) {
        console.error(`Erreur decode polyline trip ${trip.trip_id}:`, error);
        return null; // Fallback silencieux
      }
    })
    .filter((t): t is NonNullable<typeof t> => t !== null);
}, [trips]);
```

**Fallback visuel (optionnel):**
```typescript
// Si polyline invalide mais coords départ/arrivée disponibles
if (!trip.polyline && trip.departure_lat && trip.destination_lat) {
  // Ligne droite entre les deux points
  const fallbackCoords = [
    [trip.departure_lat, trip.departure_lng],
    [trip.destination_lat, trip.destination_lng],
  ];
  return { ...trip, coordinates: fallbackCoords, isFallback: true };
}
```

### 8. Re-draw polylines (optimisation future)

**MVP: re-draw complet** ✅
```typescript
// Chaque changement hover/select → clear + redraw all
polylinesRef.current.forEach(p => p.remove());
polylinesRef.current.clear();
decodedTrips.forEach(trip => { ... });
```

**50 trajets → OK**
**300+ trajets → à optimiser**

**v2: update styles sans recreate**
```typescript
// Optimisation: update style au lieu de recreate
useEffect(() => {
  polylinesRef.current.forEach((line, tripId) => {
    const isSelected = selectedTrip?.trip_id === tripId;
    const isHovered = hoveredTripId === tripId;

    // Update style sans supprimer/recréer
    line.setStyle({
      weight: isSelected ? 6 : isHovered ? 5 : 3,
      opacity: isSelected || isHovered ? 1 : 0.7,
    });
  });
}, [selectedTrip, hoveredTripId]);
```

### 9. Cache API passagers (optimisation future)

**MVP: fetch à chaque sélection** ✅
```typescript
useEffect(() => {
  if (selectedTrip) {
    fetch(`/api/trips/${selectedTrip.trip_id}/passengers`)
      .then(...)
  }
}, [selectedTrip?.trip_id]);
```

**v2: memoisation avec SWR/React Query**
```typescript
import useSWR from "swr";

function usePassengers(tripId: string | null) {
  const { data, error, isLoading } = useSWR(
    tripId ? `/api/trips/${tripId}/passengers` : null,
    fetcher,
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000, // Cache 1 minute
    }
  );

  return { passengers: data || [], isLoading, error };
}
```

**Alternative simple: cache Map in-memory**
```typescript
const passengersCache = useRef<Map<string, Passenger[]>>(new Map());

useEffect(() => {
  if (selectedTrip && !passengersCache.current.has(selectedTrip.trip_id)) {
    fetch(`/api/trips/${selectedTrip.trip_id}/passengers`)
      .then(res => res.json())
      .then(passengers => {
        passengersCache.current.set(selectedTrip.trip_id, passengers);
        setSelectedTrip(prev => prev ? { ...prev, passengers } : null);
      });
  } else if (selectedTrip) {
    // Utiliser le cache
    const cached = passengersCache.current.get(selectedTrip.trip_id);
    setSelectedTrip(prev => prev ? { ...prev, passengers: cached || [] } : null);
  }
}, [selectedTrip?.trip_id]);
```

---

## 🚀 Roadmap évolution

| Phase | Fonctionnalité | Priorité |
|-------|----------------|----------|
| MVP | Carte + filtres client + popup | P0 |
| v1.1 | Pre-fetch navigation | P1 |
| v1.1 | Highlight animation | P1 |
| v1.2 | Filtrage server-side | P2 |
| v1.3 | Bounding box loading | P2 |
| v1.4 | Cache passagers (SWR) | P2 |
| v1.4 | Update polyline styles (sans recreate) | P2 |
| v2.0 | Clusters pour > 500 trajets | P3 |
