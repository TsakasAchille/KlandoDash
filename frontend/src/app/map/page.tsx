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
      {/* Header Stylisé */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between p-4 sm:p-6 border-b border-border/40 gap-4 bg-card/50 backdrop-blur-sm z-20 relative">
        <div className="space-y-1">
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight uppercase flex items-center gap-3">
            <MapIcon className="w-6 h-6 sm:w-8 sm:h-8 text-klando-gold" />
            Carte Live
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground font-medium">
            Visualisation temps réel de la flotte et des intentions
          </p>
        </div>
        
        <div className="flex items-center justify-between sm:justify-end gap-4 w-full sm:w-auto">
          <div className="flex gap-2">
            <div className="px-2 py-1 sm:px-3 sm:py-1 rounded-lg bg-secondary/80 border border-border/50 text-[10px] sm:text-xs font-bold flex items-center gap-2">
              <MapIcon className="w-3 h-3 text-klando-gold" />
              {stats.total_trips} TRAJETS
            </div>
            <div className="px-2 py-1 sm:px-3 sm:py-1 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-500 text-[10px] sm:text-xs font-bold flex items-center gap-2">
              <Users className="w-3 h-3 text-purple-500" />
              {siteRequests.length} DEMANDES
            </div>
          </div>
          <RefreshButton />
        </div>
      </div>

      {/* Client Component - Map prend tout l'espace restant */}
      <div className="flex-1 relative overflow-hidden h-[calc(100vh-140px)]">
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