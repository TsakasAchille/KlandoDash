import { getTripsWithDriver, getTripById, getTripsStats } from "@/lib/queries/trips";
import { getPublicPendingTrips } from "@/lib/queries/site-requests";
import { toTrip } from "@/types/trip";
import { TripsPageClient } from "./trips-client";
import { RefreshButton } from "@/components/refresh-button";
import { StatCards } from "./stat-cards";

export const dynamic = "force-dynamic";

interface Props {
  searchParams: Promise<{ 
    selected?: string;
    page?: string;
    status?: string;
    search?: string;
    driverId?: string;
    minPrice?: string;
    maxPrice?: string;
    onlyPaid?: string;
  }>;
}

export default async function TripsPage({ searchParams }: Props) {
  const { selected } = await searchParams;

  // On récupère une grande quantité de trajets récents pour permettre le filtrage client fluide
  const [tripsResult, stats, selectedTripData, publicPending] = await Promise.all([
    getTripsWithDriver({
      page: 1,
      pageSize: 500, // On prend les 500 derniers trajets
    }),
    getTripsStats(),
    selected ? getTripById(selected) : Promise.resolve(null),
    getPublicPendingTrips(),
  ]);

  const { trips: tripsData } = tripsResult;

  // Convert to legacy Trip format
  const trips = tripsData.map(toTrip);

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 pt-4 px-4 sm:px-6 lg:px-8">
      <div className="absolute top-4 right-8 z-10">
        <RefreshButton />
      </div>

      <TripsPageClient
        initialTrips={trips}
        stats={stats}
        publicPendingCount={publicPending.length}
        initialSelectedId={selected || null}
        initialSelectedTripDetail={selectedTripData}
      />
    </div>
  );
}
