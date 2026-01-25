"use client";

import { useState, useCallback, useMemo, useEffect } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { MapFilters } from "@/components/map/map-filters";
import { RecentTripsTable } from "@/components/map/recent-trips-table";
import { TripMapPopup } from "@/components/map/trip-map-popup";
import { TripMapItem, MapFilters as MapFiltersType } from "@/types/trip";

// Import dynamique pour éviter les erreurs SSR avec Leaflet
const TripMap = dynamic(
  () => import("@/components/map/trip-map").then((mod) => mod.TripMap),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full flex items-center justify-center bg-gray-900 rounded-lg">
        <div className="text-gray-400">Chargement de la carte...</div>
      </div>
    ),
  }
);

interface MapClientProps {
  trips: TripMapItem[];
  drivers: Array<{ uid: string; display_name: string | null }>;
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
  const [selectedTrip, setSelectedTrip] = useState<TripMapItem | null>(
    initialSelectedTrip
  );
  const [filters, setFilters] = useState<MapFiltersType>({
    status: (initialStatusFilter as MapFiltersType["status"]) || "ALL",
    dateFrom: null,
    dateTo: null,
    driverId: initialDriverFilter,
  });
  const [hoveredTripId, setHoveredTripId] = useState<string | null>(null);
  const [hiddenTripIds, setHiddenTripIds] = useState<Set<string>>(new Set());

  // Toggle visibility d'un trajet
  const handleToggleVisibility = useCallback((tripId: string) => {
    setHiddenTripIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(tripId)) {
        newSet.delete(tripId);
      } else {
        newSet.add(tripId);
      }
      return newSet;
    });
  }, []);

  // Fetch passagers uniquement pour le trajet sélectionné
  useEffect(() => {
    if (selectedTrip && selectedTrip.passengers.length === 0) {
      fetch(`/api/trips/${selectedTrip.trip_id}/passengers`)
        .then((res) => res.json())
        .then((passengers) => {
          if (Array.isArray(passengers)) {
            setSelectedTrip((prev) =>
              prev ? { ...prev, passengers } : null
            );
          }
        })
        .catch(console.error);
    }
  }, [selectedTrip?.trip_id]);

  // Pre-fetch pages liées (UX premium)
  useEffect(() => {
    if (selectedTrip) {
      if (selectedTrip.driver?.uid) {
        router.prefetch(`/users?selected=${selectedTrip.driver.uid}`);
      }
      router.prefetch(`/trips?selected=${selectedTrip.trip_id}`);
    }
  }, [selectedTrip, router]);

  // Filtrage des trajets (client-side MVP)
  const filteredTrips = useMemo(() => {
    return trips.filter((trip) => {
      if (filters.status !== "ALL" && trip.status !== filters.status)
        return false;
      if (filters.driverId && trip.driver?.uid !== filters.driverId)
        return false;
      if (filters.dateFrom && trip.departure_schedule) {
        const tripDate = new Date(trip.departure_schedule);
        if (tripDate < new Date(filters.dateFrom)) return false;
      }
      if (filters.dateTo && trip.departure_schedule) {
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

  // Afficher seulement le dernier trajet
  const handleShowOnlyLast = useCallback(() => {
    const allIds = new Set(filteredTrips.map((t) => t.trip_id));
    // Garder seulement le premier (le plus récent)
    if (filteredTrips.length > 0) {
      allIds.delete(filteredTrips[0].trip_id);
    }
    setHiddenTripIds(allIds);
  }, [filteredTrips]);

  // Afficher tous les trajets
  const handleShowAll = useCallback(() => {
    setHiddenTripIds(new Set());
  }, []);

  // Sélection avec sync URL
  const handleSelectTrip = useCallback(
    (trip: TripMapItem) => {
      setSelectedTrip(trip);
      const url = new URL(window.location.href);
      url.searchParams.set("selected", trip.trip_id);
      router.replace(url.pathname + url.search, { scroll: false });
    },
    [router]
  );

  // Fermeture popup
  const handleClosePopup = useCallback(() => {
    setSelectedTrip(null);
    const url = new URL(window.location.href);
    url.searchParams.delete("selected");
    router.replace(url.pathname + url.search, { scroll: false });
  }, [router]);

  // Mise à jour filtres avec sync URL
  const handleFilterChange = useCallback(
    (newFilters: Partial<MapFiltersType>) => {
      setFilters((prev) => ({ ...prev, ...newFilters }));
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
    },
    [router]
  );

  return (
    <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-4 p-4 min-h-0">
      {/* Colonne gauche: Filtres + Tableau */}
      <div className="lg:col-span-1 flex flex-col gap-4 min-h-0">
        <MapFilters
          filters={filters}
          drivers={drivers}
          onFilterChange={handleFilterChange}
        />
        <RecentTripsTable
          trips={recentTrips}
          selectedTripId={selectedTrip?.trip_id}
          hoveredTripId={hoveredTripId}
          hiddenTripIds={hiddenTripIds}
          onSelectTrip={handleSelectTrip}
          onHoverTrip={setHoveredTripId}
          onToggleVisibility={handleToggleVisibility}
          onShowOnlyLast={handleShowOnlyLast}
          onShowAll={handleShowAll}
        />
      </div>

      {/* Colonne droite: Carte */}
      <div className="lg:col-span-3 relative min-h-[500px]">
        <TripMap
          trips={filteredTrips}
          selectedTrip={selectedTrip}
          hoveredTripId={hoveredTripId}
          hiddenTripIds={hiddenTripIds}
          initialSelectedId={initialSelectedTrip?.trip_id}
          onSelectTrip={handleSelectTrip}
          onHoverTrip={setHoveredTripId}
        />

        {/* Popup détails (overlay sur la carte) */}
        {selectedTrip && (
          <TripMapPopup trip={selectedTrip} onClose={handleClosePopup} />
        )}
      </div>
    </div>
  );
}
