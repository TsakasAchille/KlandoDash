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
  
  // États locaux pour le filtrage instantané
  const [selectedTrip, setSelectedTrip] = useState<TripDetail | null>(initialSelectedTripDetail);
  const [selectedId, setSelectedId] = useState<string | null>(initialSelectedId);

  // Récupération des filtres depuis l'URL (pour garder le lien partageable)
  const statusFilter = searchParams.get("status") || "all";
  const onlyPaidFilter = searchParams.get("onlyPaid") === "true";
  const searchFilter = searchParams.get("search")?.toLowerCase() || "";

  // FILTRAGE LOCAL (Instantané !)
  const filteredTrips = useMemo(() => {
    return initialTrips.filter(trip => {
      const matchesStatus = statusFilter === "all" || trip.status === statusFilter;
      const matchesPaid = !onlyPaidFilter || trip.has_successful_transaction;
      const matchesSearch = !searchFilter || 
        trip.departure_city.toLowerCase().includes(searchFilter) ||
        trip.destination_city.toLowerCase().includes(searchFilter) ||
        trip.trip_id.toLowerCase().includes(searchFilter);
      
      return matchesStatus && matchesPaid && matchesSearch;
    });
  }, [initialTrips, statusFilter, onlyPaidFilter, searchFilter]);

  // Synchronisation si l'URL change (ex: bouton retour navigateur)
  useEffect(() => {
    setSelectedId(initialSelectedId);
    if (!initialSelectedId) setSelectedTrip(null);
  }, [initialSelectedId]);

  const handleSelectTrip = (trip: Trip) => {
    setSelectedId(trip.trip_id);
    // On met à jour l'URL sans recharger la page
    const params = new URLSearchParams(searchParams.toString());
    params.set("selected", trip.trip_id);
    router.push(`?${params.toString()}`, { scroll: false });
    
    // On pourrait charger le détail complet ici si pas déjà présent
    // Pour l'instant on simule avec les données de la liste
    setSelectedTrip(trip as unknown as TripDetail);
  };

  return (
    <div className="space-y-6">
      {/* Stats cliquables */}
      <StatCards stats={stats} publicPendingCount={publicPendingCount} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* Tableau (2/3 de l'écran) */}
        <div className="lg:col-span-2 space-y-6">
          <TripTable 
            trips={filteredTrips} 
            totalCount={filteredTrips.length}
            currentPage={1}
            pageSize={filteredTrips.length}
            selectedTripId={selectedId}
            onSelectTrip={handleSelectTrip}
          />
        </div>

        {/* Détails (1/3 de l'écran) */}
        <div className="lg:col-span-1">
          {selectedId && selectedTrip ? (
            <TripDetails trip={selectedTrip} />
          ) : (
            <div className="h-[400px] flex items-center justify-center rounded-[2.5rem] border border-dashed border-border/40 bg-card/20 backdrop-blur-sm">
              <div className="text-center space-y-2 opacity-40">
                <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto">
                    <Loader2 className="w-8 h-8 text-muted-foreground" />
                </div>
                <p className="text-[10px] font-black uppercase tracking-widest">Sélectionnez un trajet</p>
              </div>
            </div>
          )}
        </div>
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
