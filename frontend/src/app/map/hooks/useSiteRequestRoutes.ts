import { useState, useEffect, useRef } from "react";
import { SiteTripRequest } from "@/types/site-request";
import { calculateAndSaveRequestRouteAction } from "@/app/site-requests/actions";

export function useSiteRequestRoutes(requests: SiteTripRequest[]) {
  const [enrichedRequests, setRequests] = useState<SiteTripRequest[]>(requests);
  const processedIds = useRef<Set<string>>(new Set());

  useEffect(() => {
    // Initial sync
    setRequests(requests);

    const calculateMissingRoutes = async () => {
      // On ne traite que les requêtes qui n'ont pas de polyline ET qui n'ont pas encore été tentées dans ce cycle
      const needsCalculation = requests.filter(r => 
        !r.polyline && 
        r.origin_city && 
        r.destination_city && 
        !processedIds.current.has(r.id)
      );
      
      if (needsCalculation.length === 0) return;

      console.log(`[useSiteRequestRoutes] Requesting server-side calculation for ${needsCalculation.length} requests`);
      
      // On marque immédiatement comme "en cours/traité" pour éviter le trigger du prochain render
      needsCalculation.forEach(r => processedIds.current.add(r.id));

      // On traite les requêtes en parallèle via les Server Actions
      const results = await Promise.all(
        needsCalculation.map(async (req) => {
          try {
            const result = await calculateAndSaveRequestRouteAction(req.id, req.origin_city, req.destination_city);
            if (result.success && result.data) {
              return {
                id: req.id,
                ...result.data
              };
            }
          } catch (e) {
            console.error(`Failed to calculate route for ${req.id}`, e);
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
