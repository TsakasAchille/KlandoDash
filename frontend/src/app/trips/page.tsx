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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Car className="w-8 h-8 text-klando-gold" />
          <h1 className="text-3xl font-bold">Trajets</h1>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <div className="px-3 py-1 rounded-full bg-secondary">
            <span className="text-muted-foreground">Total:</span>{" "}
            <span className="font-semibold">{stats.total_trips}</span>
          </div>
          <div className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-400">
            Actifs: {stats.active_trips}
          </div>
          <div className="px-3 py-1 rounded-full bg-green-500/20 text-green-400">
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
