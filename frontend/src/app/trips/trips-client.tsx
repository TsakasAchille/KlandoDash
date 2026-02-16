"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Trip, TripDetail } from "@/types/trip";
import { TripTable } from "@/components/trips/trip-table";
import { TripDetails } from "@/components/trips/trip-details";

interface TripsPageClientProps {
  trips: Trip[];
  totalCount: number;
  currentPage: number;
  pageSize: number;
  initialSelectedId: string | null;
  initialSelectedTripDetail: TripDetail | null;
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
  totalCount,
  currentPage,
  pageSize,
  initialSelectedId,
  initialSelectedTripDetail,
}: TripsPageClientProps) {
  const router = useRouter();
  const [detailedTrip, setDetailedTrip] = useState<TripDetail | null>(initialSelectedTripDetail);

  // Sync URL on selection change (replace pour éviter pollution historique)
  const handleSelectTrip = useCallback(
    (trip: Trip) => {
      const url = new URL(window.location.href);
      url.searchParams.set("selected", trip.trip_id);
      router.replace(url.pathname + url.search, { scroll: false });
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
  
  useEffect(() => {
    setDetailedTrip(initialSelectedTripDetail);
  }, [initialSelectedTripDetail]);

  return (
    <div className="flex flex-col gap-10">
      {/* Table - Full width */}
      <div className="min-w-0"> {/* min-w-0 pour permettre le scroll */}
        <TripTable
          trips={trips}
          totalCount={totalCount}
          currentPage={currentPage}
          pageSize={pageSize}
          selectedTripId={detailedTrip?.trip_id || null}
          initialSelectedId={initialSelectedId}
          onSelectTrip={handleSelectTrip}
        />
      </div>

      {/* Details - Below the table, full width */}
      <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
        {detailedTrip ? (
          <TripDetails trip={detailedTrip} />
        ) : (
          <div className="flex items-center justify-center py-20 rounded-[2rem] border border-dashed border-border bg-card/30">
            <p className="text-muted-foreground font-medium">
              Sélectionnez un trajet pour voir les détails
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

