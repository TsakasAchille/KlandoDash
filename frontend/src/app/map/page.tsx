import { getTripsForMap, getTripsStats, getDriversList } from "@/lib/queries/trips";
import { MapClient } from "./map-client";

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
    <div className="flex flex-col h-full">
      {/* Header responsive avec stats */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-4 border-b border-gray-800 gap-4">
        <h1 className="text-xl sm:text-2xl font-bold text-klando-gold">Carte des Trajets</h1>
        <div className="flex flex-wrap gap-2 sm:gap-4">
          <span className="px-3 py-1 text-xs sm:text-sm bg-gray-800 rounded-full">
            {stats.total_trips} trajets
          </span>
          <span className="px-3 py-1 text-xs sm:text-sm bg-blue-500/20 text-blue-400 rounded-full">
            {stats.active_trips} actifs
          </span>
        </div>
      </div>

      {/* Client Component */}
      <MapClient
        trips={trips}
        drivers={drivers}
        initialSelectedTrip={initialSelectedTrip}
        initialStatusFilter={statusFilter}
        initialDriverFilter={driverFilter}
      />
    </div>
  );
}
