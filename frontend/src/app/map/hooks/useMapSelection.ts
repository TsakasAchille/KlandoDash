import { useState, useCallback, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { TripMapItem } from "@/types/trip";
import { SiteTripRequest } from "@/types/site-request";

interface UseMapSelectionProps {
  initialSelectedTrip: TripMapItem | null;
}

export function useMapSelection({
  initialSelectedTrip
}: UseMapSelectionProps) {
  const router = useRouter();
  const [selectedTrip, setSelectedTrip] = useState<TripMapItem | null>(initialSelectedTrip);
  const [selectedRequest, setSelectedRequest] = useState<SiteTripRequest | null>(null);
  const [hasBeenManuallyClosed, setHasBeenManuallyClosed] = useState(false);
  const lastFetchedPassengersId = useRef<string | null>(null);

  const handleSelectTrip = useCallback(
    (trip: TripMapItem) => {
      setSelectedTrip(trip);
      setSelectedRequest(null); // Désélectionner la demande si on choisit un trajet
      const url = new URL(window.location.href);
      url.searchParams.set("selected", trip.trip_id);
      url.searchParams.delete("request");
      router.replace(url.pathname + url.search, { scroll: false });
    },
    [router]
  );

  const handleSelectRequest = useCallback(
    (request: SiteTripRequest) => {
      setSelectedRequest(request);
      setSelectedTrip(null); // Désélectionner le trajet si on choisit une demande
      const url = new URL(window.location.href);
      url.searchParams.set("request", request.id);
      url.searchParams.delete("selected");
      router.replace(url.pathname + url.search, { scroll: false });
    },
    [router]
  );

  const handleClosePopup = useCallback(() => {
    setSelectedTrip(null);
    setSelectedRequest(null);
    setHasBeenManuallyClosed(true);
    const url = new URL(window.location.href);
    url.searchParams.delete("selected");
    url.searchParams.delete("request");
    router.replace(url.pathname + url.search, { scroll: false });
  }, [router]);

  // Fetch passengers for selected trip
  useEffect(() => {
    if (selectedTrip && lastFetchedPassengersId.current !== selectedTrip.trip_id) {
      lastFetchedPassengersId.current = selectedTrip.trip_id;
      
      fetch(`/api/trips/${selectedTrip.trip_id}/passengers`)
        .then((res) => res.json())
        .then((passengers) => {
          if (Array.isArray(passengers)) {
            setSelectedTrip((prev) =>
              prev && prev.trip_id === selectedTrip.trip_id 
                ? { ...prev, passengers } 
                : prev
            );
          }
        })
        .catch(console.error);
    }
  }, [selectedTrip?.trip_id, selectedTrip]);

  return {
    selectedTrip,
    setSelectedTrip,
    handleSelectTrip,
    handleClosePopup,
    hasBeenManuallyClosed
  };
}
