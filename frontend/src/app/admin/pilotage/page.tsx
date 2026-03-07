import { getPilotageMetrics } from "@/lib/queries/stats/get-pilotage-metrics";
import { getCRMOpportunities } from "@/lib/queries/stats/get-crm-opportunities";
import { getTripsForMap } from "@/lib/queries/trips/get-trips-for-map";
import { getMarketingSiteRequestsAction } from "@/app/site-requests/actions";
import { getPublicPendingTrips, getPublicCompletedTrips, getSiteTripRequestsStats } from "@/lib/queries/site-requests";
import { PilotageClient } from "./pilotage-client";

export const dynamic = "force-dynamic";

export default async function PilotagePage() {
  const [
    metrics, 
    crmData, 
    tripsForMap, 
    requestsRes, 
    publicPending,
    publicCompleted,
    leadStats
  ] = await Promise.all([
    getPilotageMetrics(),
    getCRMOpportunities(),
    getTripsForMap(200),
    getMarketingSiteRequestsAction({ limit: 1000 }),
    getPublicPendingTrips(),
    getPublicCompletedTrips(),
    getSiteTripRequestsStats()
  ]);

  if (!metrics) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-muted-foreground">Erreur lors du chargement des données de pilotage.</p>
      </div>
    );
  }

  return (
    <PilotageClient 
      metrics={metrics} 
      crmData={crmData} 
      tripsForMap={tripsForMap}
      initialRequests={requestsRes.success ? requestsRes.data : []}
      leadStats={leadStats}
      publicPending={publicPending}
      publicCompleted={publicCompleted}
    />
  );
}
