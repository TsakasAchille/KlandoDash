import { createAdminClient } from "@/lib/supabase";
import { TripDetail } from "@/types/trip";

interface RawTripData {
  trip_id: string;
  departure_name: string;
  departure_description: string;
  departure_latitude: number;
  departure_longitude: number;
  destination_name: string;
  destination_description: string;
  destination_latitude: number;
  destination_longitude: number;
  departure_schedule: string;
  distance: number;
  polyline: string;
  seats_available: number;
  seats_published: number;
  seats_booked: number;
  passenger_price: number;
  driver_price: number;
  status: string;
  auto_confirmation: boolean;
  created_at: string;
  driver_id: string;
  driver?: any; // Sub-query result
  bookings?: any[]; // Sub-query result
}

export const TripService = {
  /**
   * Récupère un trajet par son ID avec une robustesse maximale (gestion des préfixes)
   */
  async getById(tripId: string): Promise<TripDetail | null> {
    const supabase = createAdminClient();
    const cleanId = tripId.trim();
    
    console.log(`[TripService] Searching for: "${cleanId}"`);

    // 1. Tentative de recherche exacte
    const { data: exactData } = await supabase
      .from("trips")
      .select(`
        *,
        driver:users!fk_driver (uid, display_name, photo_url, phone_number, rating, rating_count, is_driver_doc_validated),
        bookings (status, user:users (uid, display_name, photo_url))
      `)
      .eq("trip_id", cleanId)
      .maybeSingle();

    if (exactData) return this.mapToTripDetail(exactData as unknown as RawTripData);

    // 2. Tentative de recherche par préfixe (si l'IA a tronqué le hash)
    // On cherche tout ce qui commence par l'ID fourni
    console.log(`[TripService] Exact match failed, trying prefix search (${cleanId}%)...`);
    const { data: prefixData } = await supabase
      .from("trips")
      .select(`
        *,
        driver:users!fk_driver (uid, display_name, photo_url, phone_number, rating, rating_count, is_driver_doc_validated),
        bookings (status, user:users (uid, display_name, photo_url))
      `)
      .ilike("trip_id", `${cleanId}%`)
      .limit(1)
      .maybeSingle();

    if (prefixData) {
      console.log(`[TripService] Trip found via prefix: ${prefixData.trip_id}`);
      return this.mapToTripDetail(prefixData as unknown as RawTripData);
    }

    console.warn(`[TripService] Trip NOT FOUND: ${cleanId}`);
    return null;
  },

  /**
   * Helper pour mapper les données brute vers le type TripDetail
   */
  mapToTripDetail(data: RawTripData): TripDetail {
    const driver = Array.isArray(data.driver) ? data.driver[0] : data.driver;
    const bookings = (data.bookings || [])
        .filter((b: any) => ["CONFIRMED", "COMPLETED"].includes(b.status))
        .map((b: any) => {
            const u = Array.isArray(b.user) ? b.user[0] : b.user;
            if (!u) return null;
            return { 
              uid: u.uid as string, 
              display_name: (u.display_name as string) || null, 
              photo_url: (u.photo_url as string) || null 
            };
        })
        .filter((u: any): u is { uid: string; display_name: string | null; photo_url: string | null } => u !== null);

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
      driver_name: driver?.display_name || "Chauffeur Klando",
      driver_photo: driver?.photo_url,
      driver_phone: driver?.phone_number,
      driver_rating: driver?.rating,
      driver_rating_count: driver?.rating_count,
      driver_verified: driver?.is_driver_doc_validated,
      passengers: bookings,
    };
  }
};
