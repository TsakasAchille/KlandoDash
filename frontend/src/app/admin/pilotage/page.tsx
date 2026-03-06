import { getPilotageMetrics } from "@/lib/queries/stats/get-pilotage-metrics";
import { getCRMOpportunities } from "@/lib/queries/stats/get-crm-opportunities";
import { getTripsForMap } from "@/lib/queries/trips/get-trips-for-map";
import { PilotageClient } from "./pilotage-client";

export const dynamic = "force-dynamic";

export default async function PilotagePage() {
  const [metrics, crmData, tripsForMap] = await Promise.all([
    getPilotageMetrics(),
    getCRMOpportunities(),
    getTripsForMap(200) // On prend un peu plus de trajets pour la vue corridors
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
    />
  );
}
