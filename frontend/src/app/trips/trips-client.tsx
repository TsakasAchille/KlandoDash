"use client";

import { useState, useMemo, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2, Search, X, Map as MapIcon } from "lucide-react";
import { Trip, TripDetail } from "@/types/trip";
import { TripTable } from "@/components/trips/trip-table";
import { TripDetails } from "@/components/trips/trip-details";
import { StatCards } from "./stat-cards";
import { TripStats } from "@/types/trip";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { getTripDetailsAction } from "./actions";
import { toast } from "sonner";

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
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
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
    if (initialSelectedId && !selectedTrip && initialSelectedTripDetail) {
        setSelectedTrip(initialSelectedTripDetail);
    }
    if (!initialSelectedId) setSelectedTrip(null);
  }, [initialSelectedId, initialSelectedTripDetail]);

  const handleSelectTrip = async (trip: Trip) => {
    setSelectedId(trip.trip_id);
    setIsLoadingDetails(true);
    
    // Mettre à jour l'URL sans rechargement complet
    const params = new URLSearchParams(window.location.search);
    params.set("selected", trip.trip_id);
    router.push(`?${params.toString()}`, { scroll: false });
    
    try {
      const res = await getTripDetailsAction(trip.trip_id);
      if (res.success && res.data) {
        setSelectedTrip(res.data);
      } else {
        toast.error("Impossible de charger les détails complets");
        setSelectedTrip(trip as unknown as TripDetail);
      }
    } catch (e) {
      console.error(e);
      setSelectedTrip(trip as unknown as TripDetail);
    } finally {
      setIsLoadingDetails(false);
    }
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
      <div className="pt-8 min-h-[600px]">
        {!selectedId ? (
          <div className="h-[300px] flex items-center justify-center rounded-[3rem] border-2 border-dashed border-slate-200 bg-slate-50/50 backdrop-blur-sm animate-in fade-in duration-700">
            <div className="text-center space-y-4 opacity-40">
              <div className="w-20 h-20 bg-white rounded-[2rem] flex items-center justify-center mx-auto shadow-sm">
                <MapIcon className="w-8 h-8 text-slate-400" />
              </div>
              <p className="text-xs font-black uppercase tracking-[0.3em] text-slate-500">Sélectionnez un trajet pour une analyse complète</p>
            </div>
          </div>
        ) : isLoadingDetails ? (
          <div className="h-[500px] flex flex-col items-center justify-center space-y-6 bg-white rounded-[3rem] border border-slate-100 shadow-xl animate-in fade-in duration-300">
              <div className="w-12 h-12 border-4 border-klando-gold border-t-transparent rounded-full animate-spin" />
              <div className="text-center space-y-1">
                <p className="text-[10px] font-black uppercase tracking-[0.2em] text-klando-gold animate-pulse">Extraction des données temps-réel...</p>
                <p className="text-[9px] text-slate-400 font-bold uppercase tracking-widest">Calcul des finances et tracé GPS</p>
              </div>
          </div>
        ) : selectedTrip ? (
          <div className="animate-in fade-in slide-in-from-bottom-10 duration-1000 ease-out">
            <TripDetails trip={selectedTrip} />
          </div>
        ) : null}
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
