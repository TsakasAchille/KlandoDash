import { getTripsWithDriver, getTripById, getTripsStats } from "@/lib/queries/trips";
import { toTrip } from "@/types/trip";
import { TripsPageClient } from "./trips-client";
import { Car, CheckCircle2, Play } from "lucide-react";
import { RefreshButton } from "@/components/refresh-button";
import { MiniStatCard } from "@/components/mini-stat-card";

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
  }>;
}

export default async function TripsPage({ searchParams }: Props) {
  const { selected, page, status, search, driverId, minPrice, maxPrice } = await searchParams;
  const currentPage = parseInt(page || "1", 10);
  const pageSize = 10;

  // Pre-fetch data with filters and pagination
  const [{ trips: tripsData, totalCount }, stats, selectedTripData] = await Promise.all([
    getTripsWithDriver({
      page: currentPage,
      pageSize,
      status,
      search,
      driverId,
      minPrice: minPrice ? parseInt(minPrice, 10) : undefined,
      maxPrice: maxPrice ? parseInt(maxPrice, 10) : undefined,
    }),
    getTripsStats(),
    selected ? getTripById(selected) : null,
  ]);

  // Convert to legacy Trip format for compatibility with table component
  const trips = tripsData.map(toTrip);

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 pb-10 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-border/40 pb-6">
        <div className="space-y-1">
          <h1 className="text-3xl font-black tracking-tight uppercase flex items-center gap-3">
            <Car className="w-8 h-8 text-klando-gold" />
            Trajets
          </h1>
          <p className="text-sm text-muted-foreground font-medium">
            Gestion et suivi des trajets en temps réel
          </p>
        </div>
        <RefreshButton />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MiniStatCard 
          title="Total" 
          value={stats.total_trips} 
          icon={Car} 
          color="gold" 
        />
        <MiniStatCard 
          title="Actifs" 
          value={stats.active_trips} 
          icon={Play} 
          color="blue" 
        />
        <MiniStatCard 
          title="Terminés" 
          value={stats.completed_trips} 
          icon={CheckCircle2} 
          color="green" 
        />
      </div>

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