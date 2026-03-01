import { getTripsForMap, getTripsStats, getDriversList } from "@/lib/queries/trips";
import { getSiteTripRequests } from "@/lib/queries/site-requests";
import { MapClient } from "./map-client";
import { RefreshButton } from "@/components/refresh-button";
import { Map as MapIcon, Users, Loader2 } from "lucide-react";
import { Suspense } from "react";

interface MapPageProps {
  searchParams: Promise<{
    selected?: string;
    request?: string;
    status?: string;
    driver?: string;
    showRequests?: string;
  }>;
}

export default async function MapPage({ searchParams }: MapPageProps) {
  const params = await searchParams;
  const selectedTripId = params.selected || null;
  const requestId = params.request || null;
  const statusFilter = params.status || "PENDING";
  const driverFilter = params.driver || null;
  // Activé par défaut pour que l'utilisateur voie les demandes immédiatement
  const showRequestsFilter = params.showRequests !== "false"; 

  const [trips, stats, drivers, siteRequests] = await Promise.all([
    getTripsForMap(100),
    getTripsStats(),
    getDriversList(),
    getSiteTripRequests({ limit: 100, hidePast: true })
  ]);

  const initialSelectedTrip = selectedTripId
    ? trips.find((t) => t.trip_id === selectedTripId) || null
    : null;

  const initialSelectedRequest = requestId
    ? siteRequests.find((r) => r.id === requestId) || null
    : null;

  return (
    <div className="flex flex-col h-full bg-background overflow-hidden">
      {/* Header Compact pour les Stats et Actions */}
      <div className="flex items-center justify-between p-4 border-b border-border/40 bg-card/50 backdrop-blur-sm z-20 relative">
        <div className="flex gap-2">
          <div className="px-3 py-1 rounded-lg bg-secondary/80 border border-border/50 text-[10px] font-bold flex items-center gap-2">
            <MapIcon className="w-3 h-3 text-klando-gold" />
            {stats.total_trips} TRAJETS
          </div>
          <div className="px-3 py-1 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-500 text-[10px] font-bold flex items-center gap-2">
            <Users className="w-3 h-3 text-purple-500" />
            {siteRequests.length} DEMANDES
          </div>
        </div>
        
        {/* Floating Actions */}
        <div className="absolute right-4 top-1/2 -translate-y-1/2">
            <RefreshButton />
        </div>
      </div>

      {/* Client Component - Map prend tout l'espace restant */}
      <div className="flex-1 relative overflow-hidden h-[calc(100vh-80px)]">
        <Suspense fallback={
          <div className="w-full h-full flex flex-col items-center justify-center bg-card/50 backdrop-blur-md">
            <Loader2 className="w-10 h-10 text-klando-gold animate-spin mb-4" />
            <p className="text-[10px] font-black uppercase tracking-widest text-klando-gold animate-pulse">Initialisation des systèmes de géolocalisation...</p>
          </div>
        }>
          <MapClient
            trips={trips}
            drivers={drivers}
            siteRequests={siteRequests}
            initialSelectedTrip={initialSelectedTrip}
            initialSelectedRequest={initialSelectedRequest}
            initialStatusFilter={statusFilter}
            initialDriverFilter={driverFilter}
            initialShowRequests={showRequestsFilter}
          />
        </Suspense>
      </div>
    </div>
  );
}