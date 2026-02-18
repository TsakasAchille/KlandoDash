import { askKlandoAI } from "@/lib/gemini";
import { MATCHING_PROMPTS } from "./prompts";
import { GeocodingService } from "./geocoding.service";
import { TripService } from "./trip.service";
import { PublicTrip } from "@/app/site-requests/hooks/useSiteRequestAI";

export const AIMatchingService = {
  /**
   * Orchestre le matching complet entre une demande et les trajets publics
   */
  async generateRecommendation(
    origin: string,
    destination: string,
    date: string | null,
    clientCoords: { lat: number, lng: number, destLat: number, destLng: number },
    availableTrips: any[] // Reçoit des trajets avec distances pré-calculées (origin_dist, dest_dist)
  ) {
    // 1. On utilise directement les distances fournies par le Scan SQL (plus rapide et précis)
    // On ne garde que ceux qui ont des distances valides (normalement tous via findMatchingTrips)
    const formattedTrips = availableTrips
      .filter(t => t.origin_dist !== undefined)
      .sort((a, b) => a.origin_dist - b.origin_dist)
      .slice(0, 5) // On ne donne que les 5 meilleures options
      .map(t => ({
        id: t.id,
        from: t.departure_city,
        to: t.arrival_city,
        time: t.departure_time,
        seats: t.seats_available,
        client_to_driver_start_km: `${t.origin_dist.toFixed(1)} km`,
        client_to_driver_end_km: `${t.dest_dist.toFixed(1)} km`
      }));

    console.log(`[AIMatchingService] Sending ${formattedTrips.length} SQL-filtered trips to AI.`);

    // 2. Construire le prompt
    const prompt = MATCHING_PROMPTS.getMatchingPrompt(origin, destination, date, formattedTrips);
    const systemContext = MATCHING_PROMPTS.STRATEGY_SYSTEM;

    // 3. Appeler l'IA
    const response = await askKlandoAI(prompt, { context: systemContext });

    return response;
  }
};
