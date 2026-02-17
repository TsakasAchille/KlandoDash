import { createAdminClient } from "@/lib/supabase";
import { TripDetail } from "@/types/trip";

export const TripService = {
  /**
   * Récupère un trajet par son ID (complet ou partiel)
   * Utilise le client ADMIN pour bypasser les restrictions RLS lors du matching technique.
   */
  async getById(tripId: string): Promise<TripDetail | null> {
    const supabase = createAdminClient();
    
    // On garde l'ID tel quel car les hashes en suffixe sont sensibles à la casse !
    let cleanId = tripId.trim();
    
    // On prépare les variantes sans forcer la casse
    const idsToTry = [cleanId];
    
    // Si l'ID est en majuscules (venant de l'extraction regex), 
    // on essaiera aussi une recherche ILIKE (insensible à la casse) si nécessaire.
    
    console.log(`[TripService] Searching for ID: "${cleanId}"`);

    // Tentative 1: Recherche exacte (Rapide)
    let { data: foundData, error } = await supabase
      .from("trips")
      .select(`
        *,
        driver:users!fk_driver (uid, display_name, photo_url, phone_number, rating, rating_count, is_driver_doc_validated),
        bookings (status, user:users (uid, display_name, photo_url))
      `)
      .eq("trip_id", cleanId)
      .maybeSingle();

    // Tentative 2: Recherche insensible à la casse (si l'IA a crié en MAJUSCULES)
    if (!foundData) {
      console.log(`[TripService] Exact match failed for ${cleanId}, trying ILIKE...`);
      const { data: ilikeData } = await supabase
        .from("trips")
        .select(`
          *,
          driver:users!fk_driver (uid, display_name, photo_url, phone_number, rating, rating_count, is_driver_doc_validated),
          bookings (status, user:users (uid, display_name, photo_url))
        `)
        .ilike("trip_id", cleanId)
        .maybeSingle();
      foundData = ilikeData;
    }

    if (!foundData) {
      console.warn(`[TripService] No trip found even with ILIKE for: ${cleanId}`);
      return null;
    }

    const data = foundData;
    const driver = Array.isArray(data.driver) ? data.driver[0] : data.driver;
    
    const bookings = (data.bookings || [])
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .filter((b: any) => ["CONFIRMED", "COMPLETED"].includes(b.status))
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .map((b: any) => {
            const u = Array.isArray(b.user) ? b.user[0] : b.user;
            return u ? { uid: u.uid, display_name: u.display_name, photo_url: u.photo_url } : null;
        })
        .filter(Boolean);

    return {
      trip_id: data.trip_id,
      departure_name: data.departure_name,
      departure_description: data.departure_description,
      departure_latitude: data.departure_latitude,
      departure_longitude: data.departure_longitude,
      destination_name: data.destination_name,
      destination_description: data.destination_description,
      destination_latitude: data.destination_latitude,
      destination_longitude: data.destination_longitude,
      departure_schedule: data.departure_schedule,
      distance: data.distance,
      polyline: data.polyline,
      seats_available: data.seats_available,
      seats_published: data.seats_published,
      seats_booked: data.seats_booked,
      passenger_price: data.passenger_price,
      driver_price: data.driver_price,
      status: data.status,
      auto_confirmation: data.auto_confirmation,
      created_at: data.created_at,
      driver_id: data.driver_id,
      driver_name: driver?.display_name,
      driver_photo: driver?.photo_url,
      driver_phone: driver?.phone_number,
      driver_rating: driver?.rating,
      driver_rating_count: driver?.rating_count,
      driver_verified: driver?.is_driver_doc_validated,
      passengers: bookings,
    } as TripDetail;
  }
};
