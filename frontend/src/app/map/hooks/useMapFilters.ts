import { useState, useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";
import { TripMapItem, MapFilters as MapFiltersType } from "@/types/trip";
import { SiteTripRequest } from "@/types/site-request";

interface UseMapFiltersProps {
  trips: TripMapItem[];
  siteRequests: SiteTripRequest[];
  initialStatusFilter: string;
  initialDriverFilter: string | null;
  initialShowRequests: boolean;
  selectedRequest: SiteTripRequest | null;
}

export function useMapFilters({
  trips,
  siteRequests,
  initialStatusFilter,
  initialDriverFilter,
  initialShowRequests,
  selectedRequest
}: UseMapFiltersProps) {
  const router = useRouter();

  const [filters, setFilters] = useState<MapFiltersType & { showRequests: boolean; showMatchesOnly: boolean }>({
    status: (initialStatusFilter as MapFiltersType["status"]) || "ALL",
    dateFrom: null,
    dateTo: null,
    driverId: initialDriverFilter,
    showRequests: initialShowRequests,
    showMatchesOnly: false,
  });

  const handleFilterChange = useCallback(
    (newFilters: Partial<MapFiltersType & { showRequests: boolean; showMatchesOnly: boolean }>) => {
      setFilters((prev) => ({ ...prev, ...newFilters }));
      const url = new URL(window.location.href);
      
      if (newFilters.status !== undefined) {
        if (newFilters.status === "PENDING") url.searchParams.delete("status");
        else url.searchParams.set("status", newFilters.status);
      }
      
      if (newFilters.driverId !== undefined) {
        if (newFilters.driverId === null) url.searchParams.delete("driver");
        else url.searchParams.set("driver", newFilters.driverId);
      }

      if (newFilters.showRequests !== undefined) {
        if (!newFilters.showRequests) url.searchParams.delete("showRequests");
        else url.searchParams.set("showRequests", "true");
      }

      router.replace(url.pathname + url.search, { scroll: false });
    },
    [router]
  );

  const filteredTrips = useMemo(() => {
    // Si le filtre "Matches Only" est actif et qu'on a une demande sélectionnée
    const matchedTripIds = selectedRequest?.matches?.map(m => m.trip_id) || [];
    
    if (filters.showMatchesOnly && selectedRequest && matchedTripIds.length > 0) {
      return trips.filter(t => matchedTripIds.includes(t.trip_id));
    }

    return trips.filter((trip) => {
      // Mode normal (filtres classiques)
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
  }, [trips, filters, selectedRequest]);

  const filteredRequests = useMemo(() => {
    if (!filters.showRequests) return [];

    return siteRequests.map(r => {
      if (r.origin_lat && r.origin_lng) return r;

      // Fallback position for demo/incomplete data
      const dakarLat = 14.7167;
      const dakarLng = -17.4677;
      const randomOffset = () => (Math.random() - 0.5) * 0.1;

      return {
        ...r,
        origin_lat: dakarLat + randomOffset(),
        origin_lng: dakarLng + randomOffset(),
        is_estimated: true
      };
    });
  }, [siteRequests, filters.showRequests]);

  return {
    filters,
    handleFilterChange,
    filteredTrips,
    filteredRequests
  };
}
