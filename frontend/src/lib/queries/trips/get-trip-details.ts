import { createServerClient } from "../../supabase";
import { TripDetail } from "@/types/trip";

/**
 * Détail d'un trajet avec jointure conducteur et passagers
 */
export async function getTripById(tripId: string): Promise<TripDetail | null> {
  const supabase = createServerClient();

  const { data, error } = await supabase
    .from("trips")
    .select(
      `
      trip_id,
      departure_name,
      departure_description,
      departure_latitude,
      departure_longitude,
      destination_name,
      destination_description,
      destination_latitude,
      destination_longitude,
      departure_schedule,
      distance,
      polyline,
      seats_available,
      seats_published,
      seats_booked,
      passenger_price,
      driver_price,
      status,
      auto_confirmation,
      created_at,
      driver_id,
      driver:users!fk_driver (
        uid,
        display_name,
        photo_url,
        phone_number,
        rating,
        rating_count,
        is_driver_doc_validated
      ),
      bookings (
        user:users (
          uid,
          display_name,
          photo_url
        )
      )
    `
    )
    .eq("trip_id", tripId)
    .single();

  if (error) {
    console.error("getTripById error:", error);
    return null;
  }

  // Flatten driver data
  type DriverData = {
    uid: string;
    display_name: string | null;
    photo_url: string | null;
    phone_number: string | null;
    rating: number | null;
    rating_count: number | null;
    is_driver_doc_validated: boolean | null;
  };
  const rawDriver = data.driver as unknown;
  const driver: DriverData | null = Array.isArray(rawDriver)
    ? (rawDriver[0] as DriverData | undefined) || null
    : (rawDriver as DriverData | null);

  // Extract and flatten passenger data
  type PassengerData = {
    uid: string;
    display_name: string | null;
    photo_url: string | null;
  };

  interface BookingRaw {
    user: unknown;
  }

  const passengers = (data.bookings as unknown as BookingRaw[] || [])
    .map((b: BookingRaw) => {
      const rawUser = b.user;
      if (!rawUser) return null;
      return Array.isArray(rawUser)
        ? (rawUser[0] as PassengerData | undefined) || null
        : (rawUser as PassengerData | null);
    })
    .filter((p): p is PassengerData => p !== null);

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
    driver_name: driver?.display_name || null,
    driver_photo: driver?.photo_url || null,
    driver_phone: driver?.phone_number || null,
    driver_rating: driver?.rating || null,
    driver_rating_count: driver?.rating_count || null,
    driver_verified: driver?.is_driver_doc_validated || null,
    passengers: passengers,
  };
}
