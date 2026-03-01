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
  const { selected, page, status, search, driverId, minPrice, maxPrice, onlyPaid } = await searchParams;
  const currentPage = parseInt(page || "1", 10);
  const isOnlyPaid = onlyPaid === "true";
  const pageSize = 20;

  // Pre-fetch data with filters and pagination
  const [{ trips: tripsData, totalCount }, stats, selectedTripData, publicPending] = await Promise.all([
    getTripsWithDriver({
      page: currentPage,
      pageSize,
      status,
      search,
      driverId,
      minPrice: minPrice ? parseInt(minPrice, 10) : undefined,
      maxPrice: maxPrice ? parseInt(maxPrice, 10) : undefined,
      onlyPaid: isOnlyPaid,
    }),
    getTripsStats(),
    selected ? getTripById(selected) : null,
    getPublicPendingTrips(),
  ]);

  // Convert to legacy Trip format for compatibility with table component
  const trips = tripsData.map(toTrip);

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 pb-10 px-4 sm:px-6 lg:px-8 pt-4 relative">
      {/* Action Bar Floating */}
      <div className="absolute top-4 right-8 z-10">
        <RefreshButton />
      </div>

      {/* Stats */}
      <StatCards stats={stats} publicPendingCount={publicPending.length} />

      <TripsPageClient
        trips={trips}
        totalCount={totalCount}
        currentPage={currentPage}
        pageSize={pageSize}
        initialSelectedId={selected || null}
        initialSelectedTripDetail={selectedTripData}
      />
    </div>
  );
}