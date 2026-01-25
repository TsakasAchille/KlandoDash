"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Trip } from "@/types/trip";
import { TripTable } from "@/components/trips/trip-table";
import { TripDetails } from "@/components/trips/trip-details";

interface TripsPageClientProps {
  trips: Trip[];
  initialSelectedId: string | null;
  initialSelectedTrip: Trip | null;
}

// Abstraction pour scroll (future-proof pour virtualisation)
function scrollToRow(id: string, prefix: string = "trip") {
  const element = document.querySelector(`[data-${prefix}-id="${id}"]`);
  if (element) {
    element.scrollIntoView({ behavior: "smooth", block: "center" });
    // Highlight temporaire
    element.classList.add("ring-2", "ring-klando-gold");
    setTimeout(() => {
      element.classList.remove("ring-2", "ring-klando-gold");
    }, 2000);
  }
}

export function TripsPageClient({
  trips,
  initialSelectedId,
  initialSelectedTrip,
}: TripsPageClientProps) {
  const router = useRouter();
  const [selectedTrip, setSelectedTrip] = useState<Trip | null>(initialSelectedTrip);

  // Sync URL on selection change (replace pour éviter pollution historique)
  const handleSelectTrip = useCallback(
    (trip: Trip) => {
      setSelectedTrip(trip);
      router.replace(`/trips?selected=${trip.trip_id}`, { scroll: false });
    },
    [router]
  );

  // Scroll to selected row on mount
  useEffect(() => {
    if (initialSelectedId) {
      // Petit délai pour laisser le DOM se rendre
      setTimeout(() => scrollToRow(initialSelectedId, "trip"), 100);
    }
  }, [initialSelectedId]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Table - 1/3 width on large screens */}
      <div className="lg:col-span-1">
        <TripTable
          trips={trips}
          selectedTripId={selectedTrip?.trip_id || null}
          onSelectTrip={handleSelectTrip}
        />
      </div>

      {/* Details - 2/3 width on large screens */}
      <div className="lg:col-span-2">
        {selectedTrip ? (
          <TripDetails trip={selectedTrip} />
        ) : (
          <div className="flex items-center justify-center h-64 rounded-lg border border-dashed border-border">
            <p className="text-muted-foreground">
              Sélectionnez un trajet pour voir les détails
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
