"use client";

import { useState, useMemo, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2, Search, X } from "lucide-react";
import { Trip, TripDetail } from "@/types/trip";
import { TripTable } from "@/components/trips/trip-table";
import { TripDetails } from "@/components/trips/trip-details";
import { StatCards } from "./stat-cards";
import { TripStats } from "@/types/trip";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

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
  const [localSearch, setLocalSearch] = useState(searchParams.get("search") || "");
  const ITEMS_PER_PAGE = 5;

  // Filtres issus de l'URL
  const statusFilter = searchParams.get("status") || "all";
  const onlyPaidFilter = searchParams.get("onlyPaid") === "true";

  // FILTRAGE LOCAL (Instantané)
  const filteredTrips = useMemo(() => {
    return initialTrips.filter(trip => {
      const matchesStatus = statusFilter === "all" || trip.status === statusFilter;
      const matchesPaid = !onlyPaidFilter || trip.has_successful_transaction === true;
      const matchesSearch = !localSearch || 
        trip.departure_city.toLowerCase().includes(localSearch.toLowerCase()) ||
        trip.destination_city.toLowerCase().includes(localSearch.toLowerCase()) ||
        trip.trip_id.toLowerCase().includes(localSearch.toLowerCase());
      
      return matchesStatus && matchesPaid && matchesSearch;
    });
  }, [initialTrips, statusFilter, onlyPaidFilter, localSearch]);

  // Reset pagination when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [statusFilter, onlyPaidFilter, localSearch]);

  // PAGINATION LOCALE
  const paginatedTrips = useMemo(() => {
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    return filteredTrips.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  }, [filteredTrips, currentPage]);

  // Sync URL selection
  useEffect(() => {
    setSelectedId(initialSelectedId);
    if (!initialSelectedId) setSelectedTrip(null);
  }, [initialSelectedId]);

  const handleSelectTrip = (trip: Trip) => {
    setSelectedId(trip.trip_id);
    const params = new URLSearchParams(window.location.search);
    params.set("selected", trip.trip_id);
    router.push(`?${params.toString()}`, { scroll: false });
    setSelectedTrip(trip as unknown as TripDetail);
  };

  return (
    <div className="space-y-8 pb-20">
      {/* Stats cliquables */}
      <StatCards stats={stats} publicPendingCount={publicPendingCount} />

      {/* Barre de recherche locale */}
      <div className="relative max-w-xl mx-auto w-full">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Filtrer par ville ou ID..."
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          className="pl-11 h-12 text-sm rounded-2xl bg-card/40 border-border/60 focus:border-klando-gold/50 backdrop-blur-md shadow-sm"
        />
        {localSearch && (
            <Button 
                variant="ghost" 
                size="icon" 
                className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 hover:bg-transparent"
                onClick={() => setLocalSearch("")}
            >
                <X className="h-4 w-4 text-muted-foreground" />
            </Button>
        )}
      </div>

      {/* Tableau (Full width, max 5 éléments) */}
      <div className="space-y-6">
        <TripTable 
          trips={paginatedTrips} 
          totalCount={filteredTrips.length}
          currentPage={currentPage}
          pageSize={ITEMS_PER_PAGE}
          selectedTripId={selectedId}
          onSelectTrip={handleSelectTrip}
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
              <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Sélectionnez un trajet pour voir les détails financiers</p>
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
