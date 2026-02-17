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
    availableTrips: PublicTrip[]
  ) {
    // 1. Préparer le contexte enrichi avec les distances calculées
    const tripsWithDistances = await Promise.all(availableTrips.map(async (t) => {
      let dStart = 999;
      let dEnd = 999;

      // On récupère les coordonnées réelles pour un calcul précis
      const fullTrip = await TripService.getById(t.id);
      if (fullTrip && fullTrip.departure_latitude) {
        dStart = GeocodingService.calculateDistance(
          { lat: clientCoords.lat, lng: clientCoords.lng },
          { lat: fullTrip.departure_latitude, lng: fullTrip.departure_longitude! }
        );
        dEnd = GeocodingService.calculateDistance(
          { lat: clientCoords.destLat, lng: clientCoords.destLng },
          { lat: fullTrip.destination_latitude!, lng: fullTrip.destination_longitude! }
        );
      }

      return {
        id: t.id,
        from: t.departure_city,
        to: t.arrival_city,
        time: t.departure_time,
        seats: t.seats_available,
        client_to_driver_start_km: dStart.toFixed(1),
        client_to_driver_end_km: dEnd.toFixed(1)
      };
    }));

    // 2. Construire le prompt
    const prompt = MATCHING_PROMPTS.getMatchingPrompt(origin, destination, date, tripsWithDistances);
    const systemContext = MATCHING_PROMPTS.STRATEGY_SYSTEM;

    // 3. Appeler l'IA avec le contexte complet
    const response = await askKlandoAI(prompt, { context: systemContext });

    return response;
  }
};
