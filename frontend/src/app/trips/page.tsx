import { getTripsWithDriver, getTripById, getTripsStats } from "@/lib/queries/trips";
import { toTrip } from "@/types/trip";
import { TripsPageClient } from "./trips-client";
import { Car } from "lucide-react";

export const dynamic = "force-dynamic";

interface Props {
  searchParams: Promise<{ selected?: string }>;
}

export default async function TripsPage({ searchParams }: Props) {
  const { selected } = await searchParams;

  // Pre-fetch selected trip if ID in URL
  const [tripsData, stats, selectedTripData] = await Promise.all([
    getTripsWithDriver(100),
    getTripsStats(),
    selected ? getTripById(selected) : null,
  ]);

  // Convert to legacy Trip format for compatibility with existing components
  const trips = tripsData.map(toTrip);
  const initialSelectedTrip = selectedTripData ? toTrip(selectedTripData) : null;

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header responsive */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <Car className="w-6 h-6 sm:w-8 sm:h-8 text-klando-gold" />
          <h1 className="text-2xl sm:text-3xl font-bold">Trajets</h1>
        </div>
      </div>

      {/* Stats responsive */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
        <div className="flex flex-wrap gap-2">
          <div className="px-3 py-1 rounded-full bg-secondary">
            <span className="text-muted-foreground text-xs sm:text-sm">Total:</span>{" "}
            <span className="font-semibold text-xs sm:text-sm">{stats.total_trips}</span>
          </div>
          <div className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-400 text-xs sm:text-sm">
            Actifs: {stats.active_trips}
          </div>
          <div className="px-3 py-1 rounded-full bg-green-500/20 text-green-400 text-xs sm:text-sm">
            Complétés: {stats.completed_trips}
          </div>
        </div>
      </div>

      <TripsPageClient
        trips={trips}
        initialSelectedId={selected || null}
        initialSelectedTrip={initialSelectedTrip}
      />
    </div>
  );
}
