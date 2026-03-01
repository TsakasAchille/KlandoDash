"use client";

import { useState, useMemo, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2 } from "lucide-react";
import { Trip, TripDetail } from "@/types/trip";
import { TripTable } from "@/components/trips/trip-table";
import { TripDetails } from "@/components/trips/trip-details";
import { StatCards } from "./stat-cards";
import { TripStats } from "@/types/trip";

interface TripsPageClientProps {
  initialTrips: Trip[];
  stats: TripStats;
  publicPendingCount: number;
  initialSelectedId: string | null;
  initialSelectedTripDetail: TripDetail | null;
}

function TripsPageClientContent({ 
  initialTrips,
  stats,
  publicPendingCount,
  initialSelectedId,
  initialSelectedTripDetail 
}: TripsPageClientProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  // États locaux
  const [selectedTrip, setSelectedTrip] = useState<TripDetail | null>(initialSelectedTripDetail);
  const [selectedId, setSelectedId] = useState<string | null>(initialSelectedId);
  const [currentPage, setCurrentPage] = useState(1);
  const ITEMS_PER_PAGE = 5;

  // Filtres
  const statusFilter = searchParams.get("status") || "all";
  const onlyPaidFilter = searchParams.get("onlyPaid") === "true";
  const searchFilter = searchParams.get("search")?.toLowerCase() || "";

  // 1. FILTRAGE LOCAL
  const filteredTrips = useMemo(() => {
    const filtered = initialTrips.filter(trip => {
      const matchesStatus = statusFilter === "all" || trip.status === statusFilter;
      const matchesPaid = !onlyPaidFilter || trip.has_successful_transaction === true;
      const matchesSearch = !searchFilter || 
        trip.departure_city.toLowerCase().includes(searchFilter) ||
        trip.destination_city.toLowerCase().includes(searchFilter) ||
        trip.trip_id.toLowerCase().includes(searchFilter);
      
      return matchesStatus && matchesPaid && matchesSearch;
    });
    return filtered;
  }, [initialTrips, statusFilter, onlyPaidFilter, searchFilter]);

  // Reset pagination when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [statusFilter, onlyPaidFilter, searchFilter]);

  // 2. PAGINATION LOCALE (5 éléments)
  const paginatedTrips = useMemo(() => {
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    return filteredTrips.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  }, [filteredTrips, currentPage]);

  // Sync URL
  useEffect(() => {
    setSelectedId(initialSelectedId);
    if (!initialSelectedId) setSelectedTrip(null);
  }, [initialSelectedId]);

  const handleSelectTrip = (trip: Trip) => {
    setSelectedId(trip.trip_id);
    const params = new URLSearchParams(searchParams.toString());
    params.set("selected", trip.trip_id);
    router.push(`?${params.toString()}`, { scroll: false });
    setSelectedTrip(trip as unknown as TripDetail);
  };

  return (
    <div className="space-y-8 pb-20">
      {/* Stats cliquables */}
      <StatCards stats={stats} publicPendingCount={publicPendingCount} />

      {/* Tableau (Full width, max 5 éléments) */}
      <div className="space-y-6">
        <TripTable 
          trips={paginatedTrips} 
          totalCount={filteredTrips.length}
          currentPage={currentPage}
          pageSize={ITEMS_PER_PAGE}
          selectedTripId={selectedId}
          onSelectTrip={handleSelectTrip}
          // On passe une fonction de mise à jour pour la pagination locale
          onPageChange={setCurrentPage}
        />
      </div>

      {/* Détails (Sous le tableau) */}
      <div className="pt-4 border-t border-border/40">
        {selectedId && selectedTrip ? (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <TripDetails trip={selectedTrip} />
          </div>
        ) : (
          <div className="h-[200px] flex items-center justify-center rounded-[2.5rem] border border-dashed border-border/40 bg-card/5 backdrop-blur-sm">
            <div className="text-center space-y-2 opacity-40">
              <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Sélectionnez un trajet ci-dessus pour voir les détails financiers et passagers</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export function TripsPageClient(props: TripsPageClientProps) {
  return (
    <Suspense fallback={
      <div className="flex flex-col items-center justify-center py-20 space-y-4">
        <Loader2 className="w-10 h-10 text-klando-gold animate-spin" />
        <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground animate-pulse">Chargement des trajets...</p>
      </div>
    }>
      <TripsPageClientContent {...props} />
    </Suspense>
  );
}
