import { getSiteTripRequests, getSiteTripRequestsStats, getPublicPendingTrips, getPublicCompletedTrips } from "@/lib/queries/site-requests";
import { SiteRequestsClient } from "./site-requests-client";
import { LayoutGrid, CircleDot, Clock, CheckCircle, Globe } from "lucide-react";
import { RefreshButton } from "@/components/refresh-button";
import { MiniStatCard } from "@/components/mini-stat-card";
import { SiteRequestsInfo } from "@/components/site-requests/site-requests-info";

export const dynamic = "force-dynamic";

export default async function SiteRequestsPage() {
  const [requests, stats, publicPending, publicCompleted] = await Promise.all([
    getSiteTripRequests({ limit: 100 }),
    getSiteTripRequestsStats(),
    getPublicPendingTrips(),
    getPublicCompletedTrips(),
  ]);

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 pb-10 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-border/40 pb-6">
        <div className="space-y-1">
          <h1 className="text-3xl font-black tracking-tight uppercase flex items-center gap-3">
            <Globe className="w-8 h-8 text-klando-gold" />
            Demandes Site
            <SiteRequestsInfo />
          </h1>
          <p className="text-sm text-muted-foreground font-medium">
            Intentions de voyage (Aujourd&apos;hui & Futur) collectées sur le site vitrine
          </p>
        </div>
        <RefreshButton />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
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
          color="green" 
        />
      </div>

      <SiteRequestsClient 
        initialRequests={requests} 
        publicPending={publicPending}
        publicCompleted={publicCompleted}
      />
    </div>
  );
}
