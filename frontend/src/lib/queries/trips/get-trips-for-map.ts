import { createServerClient } from "../../supabase";
import { TripMapItem } from "@/types/trip";

/**
 * Trajets pour la carte (avec polyline obligatoire)
 */
export async function getTripsForMap(limit = 50): Promise<TripMapItem[]> {
  const supabase = createServerClient();

  const { data, error } = await supabase
    .from("trips")
    .select(`
      trip_id,
      departure_name,
      destination_name,
      departure_latitude,
      departure_longitude,
      destination_latitude,
      destination_longitude,
      polyline,
      status,
      departure_schedule,
      passenger_price,
      seats_available,
      seats_published,
      distance,
      driver_id,
      driver:users!fk_driver (
        uid,
        display_name,
        photo_url,
        rating
      )
    `)
    .not("polyline", "is", null)
    .order("departure_schedule", { ascending: false })
    .limit(limit);

  if (error) {
    console.error("getTripsForMap error:", error);
    return [];
  }

  type DriverData = {
    uid: string;
    display_name: string | null;
    photo_url: string | null;
    rating: number | null;
  };

  return (data || []).map((trip) => {
    const rawDriver = trip.driver as unknown;
    const driver: DriverData | null = Array.isArray(rawDriver)
      ? (rawDriver[0] as DriverData | undefined) || null
      : (rawDriver as DriverData | null);

    return {
      trip_id: trip.trip_id,
      departure_name: trip.departure_name,
      destination_name: trip.destination_name,
      departure_latitude: trip.departure_latitude,
      departure_longitude: trip.departure_longitude,
      destination_latitude: trip.destination_latitude,
      destination_longitude: trip.destination_longitude,
      polyline: trip.polyline,
      status: trip.status,
      departure_schedule: trip.departure_schedule,
      passenger_price: trip.passenger_price,
      seats_available: trip.seats_available,
      seats_published: trip.seats_published,
      distance: trip.distance,
      driver: driver,
      passengers: [], // Chargé séparément via API
    } as TripMapItem;
  });
}

/**
 * Passagers d'un trajet (via bookings)
 */
export async function getPassengersForTrip(tripId: string): Promise<Array<{
  uid: string;
  display_name: string | null;
  photo_url: string | null;
}>> {
  const supabase = createServerClient();

  const { data, error } = await supabase
    .from("bookings")
    .select(`
      user:users (
        uid,
        display_name,
        photo_url
      )
    `)
    .eq("trip_id", tripId)
    .eq("status", "CONFIRMED");

  if (error) {
    console.error("getPassengersForTrip error:", error);
    return [];
  }

  type UserData = {
    uid: string;
    display_name: string | null;
    photo_url: string | null;
  };

  return (data || [])
    .map((b) => {
      const rawUser = b.user as unknown;
      return Array.isArray(rawUser)
        ? (rawUser[0] as UserData | undefined)
        : (rawUser as UserData | null);
    })
    .filter((u): u is UserData => u !== null && u !== undefined);
}

/**
 * Liste des conducteurs (pour filtre)
 */
export async function getDriversList(): Promise<Array<{
  uid: string;
  display_name: string | null;
}>> {
  const supabase = createServerClient();

  const { data, error } = await supabase
    .from("users")
    .select("uid, display_name")
    .eq("role", "driver")
    .order("display_name");

  if (error) {
    console.error("getDriversList error:", error);
    return [];
  }

  return data || [];
}
