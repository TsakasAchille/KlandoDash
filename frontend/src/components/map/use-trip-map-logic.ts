import { useMemo } from "react";
import * as polyline from "@mapbox/polyline";
import { TripMapItem } from "@/types/trip";
import { SiteTripRequest } from "@/types/site-request";

export function useTripMapLogic(trips: TripMapItem[], siteRequests: SiteTripRequest[], flowMode: boolean) {
  
  // 1. Agrégation des flux (Mode Stratégique)
  const flows = useMemo(() => {
    if (!flowMode) return [];
    const flowMap: Record<string, any> = {};

    trips.forEach(trip => {
      if (!trip.departure_latitude || !trip.destination_latitude) return;
      const originName = trip.departure_name?.split(',')[0] || 'Inconnu';
      const destName = trip.destination_name?.split(',')[0] || 'Inconnu';
      const flowKey = [originName, destName].sort().join(' <-> ');
      
      if (!flowMap[flowKey]) {
        flowMap[flowKey] = {
          id: flowKey,
          origin: [trip.departure_latitude, trip.departure_longitude],
          dest: [trip.destination_latitude, trip.destination_longitude],
          count: 0, originName, destName
        };
      }
      flowMap[flowKey].count++;
    });
    return Object.values(flowMap);
  }, [trips, flowMode]);

  // 2. Décodage des polylines (Trajets)
  const decodedTrips = useMemo(() => {
    return trips.map(t => {
      try {
        if (!t.polyline) return null;
        const coords = polyline.decode(t.polyline) as [number, number][];
        return coords.length >= 2 ? { ...t, coordinates: coords } : null;
      } catch { return null; }
    }).filter((t): t is any => t !== null);
  }, [trips]);

  // 3. Décodage des polylines (Demandes)
  const decodedRequests = useMemo(() => {
    return siteRequests.map(r => {
      try {
        if (!r.polyline) return null;
        const coords = polyline.decode(r.polyline) as [number, number][];
        return coords.length >= 2 ? { ...r, coordinates: coords } : null;
      } catch { return null; }
    }).filter((r): r is any => r !== null);
  }, [siteRequests]);

  return { flows, decodedTrips, decodedRequests };
}
