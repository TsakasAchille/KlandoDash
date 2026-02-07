import { getTripsForMap, getTripsStats, getDriversList } from "@/lib/queries/trips";
import { MapClient } from "./map-client";
import { RefreshButton } from "@/components/refresh-button";
import { Map as MapIcon } from "lucide-react";

interface MapPageProps {
  searchParams: Promise<{
    selected?: string;
    status?: string;
    driver?: string;
  }>;
}

export default async function MapPage({ searchParams }: MapPageProps) {
  const params = await searchParams;
  const selectedTripId = params.selected || null;
  const statusFilter = params.status || "ALL";
  const driverFilter = params.driver || null;

  const [trips, stats, drivers] = await Promise.all([
    getTripsForMap(50),
    getTripsStats(),
    getDriversList(),
  ]);

  const initialSelectedTrip = selectedTripId
    ? trips.find((t) => t.trip_id === selectedTripId) || null
    : null;

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Header Stylisé */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between p-6 border-b border-border/40 gap-4 bg-card/50 backdrop-blur-sm z-10 relative">
        <div className="space-y-1">
          <h1 className="text-3xl font-black tracking-tight uppercase flex items-center gap-3">
            <MapIcon className="w-8 h-8 text-klando-gold" />
            Carte Live
          </h1>
          <p className="text-sm text-muted-foreground font-medium">
            Visualisation temps réel de la flotte
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex gap-2">
            <div className="px-3 py-1 rounded-lg bg-secondary/80 border border-border/50 text-xs font-bold flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-foreground/20" />
              {stats.total_trips} TOTAL
            </div>
            <div className="px-3 py-1 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-500 text-xs font-bold flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
              {stats.active_trips} ACTIFS
            </div>
          </div>
          <RefreshButton />
        </div>
      </div>

      {/* Client Component - Map prend tout l'espace restant */}
      <div className="flex-1 relative overflow-hidden">
        <MapClient
          trips={trips}
          drivers={drivers}
          initialSelectedTrip={initialSelectedTrip}
          initialStatusFilter={statusFilter}
          initialDriverFilter={driverFilter}
        />
      </div>
    </div>
  );
}