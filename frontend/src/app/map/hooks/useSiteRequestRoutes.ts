import { useState, useEffect } from "react";
import { SiteTripRequest } from "@/types/site-request";
import { calculateAndSaveRequestRouteAction } from "@/app/site-requests/actions";

export function useSiteRequestRoutes(requests: SiteTripRequest[]) {
  const [enrichedRequests, setRequests] = useState<SiteTripRequest[]>(requests);

  useEffect(() => {
    // Initial sync
    setRequests(requests);

    const calculateMissingRoutes = async () => {
      const needsCalculation = requests.filter(r => !r.polyline && r.origin_city && r.destination_city);
      if (needsCalculation.length === 0) return;

      console.log(`[useSiteRequestRoutes] Requesting server-side calculation for ${needsCalculation.length} requests`);

      // On traite les requêtes en parallèle via les Server Actions
      const results = await Promise.all(
        needsCalculation.map(async (req) => {
          const result = await calculateAndSaveRequestRouteAction(req.id, req.origin_city, req.destination_city);
          if (result.success && result.data) {
            return {
              id: req.id,
              ...result.data
            };
          }
          return null;
        })
      );

      const updates = results.filter((r): r is NonNullable<typeof r> => r !== null);
      if (updates.length > 0) {
        console.log(`[useSiteRequestRoutes] Successfully enriched ${updates.length} requests from server`);
        setRequests(prev => prev.map(r => {
          const update = updates.find(u => u.id === r.id);
          return update ? { ...r, ...update } : r;
        }));
      }
    };

    calculateMissingRoutes();
  }, [requests]);

  return enrichedRequests;
}
