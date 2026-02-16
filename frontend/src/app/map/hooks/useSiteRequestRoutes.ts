import { useState, useEffect } from "react";
import { SiteTripRequest } from "@/types/site-request";
import { saveRequestGeometryAction } from "@/app/site-requests/actions";

export function useSiteRequestRoutes(requests: SiteTripRequest[]) {
  const [enrichedRequests, setRequests] = useState<SiteTripRequest[]>(requests);

  useEffect(() => {
    // Initial sync
    setRequests(requests);

    const calculateMissingRoutes = async () => {
      const needsCalculation = requests.filter(r => !r.polyline && r.origin_city && r.destination_city);
      if (needsCalculation.length === 0) return;

      const geocode = async (city: string) => {
        try {
          const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(city + ", Senegal")}&limit=1`);
          const data = await res.json();
          if (data && data[0]) {
            return [parseFloat(data[0].lat), parseFloat(data[0].lon)] as [number, number];
          }
        } catch (e) {
          console.warn(`Geocoding failed for ${city}`, e);
        }
        return null;
      };

      const results = await Promise.all(
        needsCalculation.map(async (req) => {
          try {
            const [originCoords, destCoords] = await Promise.all([
              geocode(req.origin_city),
              geocode(req.destination_city)
            ]);

            if (!originCoords || !destCoords) return null;

            const routeRes = await fetch(`https://router.project-osrm.org/route/v1/driving/${originCoords[1]},${originCoords[0]};${destCoords[1]},${destCoords[0]}?overview=full`);
            const routeData = await routeRes.json();
            
            if (routeData.routes && routeData.routes[0]) {
              const geometry = {
                id: req.id,
                polyline: routeData.routes[0].geometry,
                origin_lat: originCoords[0],
                origin_lng: originCoords[1],
                destination_lat: destCoords[0],
                destination_lng: destCoords[1]
              };

              // PERSISTANCE : Sauvegarder en base de données pour les prochains utilisateurs
              saveRequestGeometryAction(req.id, {
                polyline: geometry.polyline,
                origin_lat: geometry.origin_lat,
                origin_lng: geometry.origin_lng,
                destination_lat: geometry.destination_lat,
                destination_lng: geometry.destination_lng
              });

              return geometry;
            }
          } catch (e) {
            console.error(`Route calculation failed for request ${req.id}`, e);
          }
          return null;
        })
      );

      const updates = results.filter((r): r is NonNullable<typeof r> => r !== null);
      if (updates.length > 0) {
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
