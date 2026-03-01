import { getSiteTripRequests, getSiteTripRequestsStats, getPublicPendingTrips, getPublicCompletedTrips } from "@/lib/queries/site-requests";
import { getTripsForMap } from "@/lib/queries/trips";
import { SiteRequestsClient } from "./site-requests-client";
import { LayoutGrid, CircleDot, Clock, CheckCircle, Globe, ShieldCheck } from "lucide-react";
import { RefreshButton } from "@/components/refresh-button";
import { MiniStatCard } from "@/components/mini-stat-card";
import { SiteRequestsInfo } from "@/components/site-requests/site-requests-info";

export const dynamic = "force-dynamic";

export default async function SiteRequestsPage() {
  const [requests, stats, publicPending, publicCompleted, tripsForMap] = await Promise.all([
    getSiteTripRequests({ limit: 100 }),
    getSiteTripRequestsStats(),
    getPublicPendingTrips(),
    getPublicCompletedTrips(),
    getTripsForMap(100),
  ]);

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 pb-10 px-4 sm:px-6 lg:px-8 pt-4 relative">
      {/* Action Bar Floating */}
      <div className="absolute top-4 right-8 z-10">
        <RefreshButton />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <MiniStatCard 
          title="Total" 
          value={stats.total} 
          icon={LayoutGrid} 
          color="purple" 
        />
        <MiniStatCard 
          title="Nouveaux" 
          value={stats.new} 
          icon={CircleDot} 
          color="red" 
        />
        <MiniStatCard 
          title="Examinés" 
          value={stats.reviewed} 
          icon={Clock} 
          color="gold" 
        />
        <MiniStatCard 
          title="Contactés" 
          value={stats.contacted} 
          icon={CheckCircle} 
          color="blue" 
        />
        <MiniStatCard 
          title="Validés" 
          value={stats.validated} 
          icon={ShieldCheck} 
          color="green" 
        />
      </div>

      <SiteRequestsClient 
        initialRequests={requests} 
        publicPending={publicPending}
        publicCompleted={publicCompleted}
        tripsForMap={tripsForMap}
      />
    </div>
  );
}
