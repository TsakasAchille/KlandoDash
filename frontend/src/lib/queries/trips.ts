import { createServerClient } from "../supabase";
import { TripListItem, TripDetail, TripStats, TripMapItem } from "@/types/trip";

// =====================================================
// Requêtes optimisées - colonnes spécifiques seulement
// =====================================================

/**
 * Liste des trajets pour le tableau (colonnes minimales)
 */
export async function getTrips(options: {
  limit?: number;
  offset?: number;
  status?: string;
} = {}): Promise<TripListItem[]> {
  const { limit = 50, offset = 0, status } = options;
  const supabase = createServerClient();

  let query = supabase
    .from("trips")
    .select(`
      trip_id,
      departure_name,
      destination_name,
      departure_schedule,
      distance,
      seats_available,
      seats_published,
      passenger_price,
      status,
      driver_id
    `)
    .order("departure_schedule", { ascending: false })
    .range(offset, offset + limit - 1);

  if (status) {
    query = query.eq("status", status);
  }

  const { data, error } = await query;

  if (error) {
    console.error("getTrips error:", error);
    return [];
  }

  return data as TripListItem[];
}

/**
 * Détail d'un trajet avec jointure conducteur
 */
export async function getTripById(tripId: string): Promise<TripDetail | null> {
  const supabase = createServerClient();

  const { data, error } = await supabase
    .from("trips")
    .select(`
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
      )
    `)
    .eq("trip_id", tripId)
    .single();

  if (error) {
    console.error("getTripById error:", error);
    return null;
  }

  // Flatten driver data (Supabase may return as array or object)
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
  } as TripDetail;
}

/**
 * Statistiques globales des trajets
 */
export async function getTripsStats(): Promise<TripStats> {
  const supabase = createServerClient();

  const { data, error } = await supabase
    .from("trips")
    .select("status, distance, seats_booked");

  if (error) {
    console.error("getTripsStats error:", error);
    return {
      total_trips: 0,
      active_trips: 0,
      completed_trips: 0,
      total_distance: 0,
      total_seats_booked: 0,
    };
  }

  type TripRow = { status: string | null; distance: number | null; seats_booked: number | null };
  const trips = (data || []) as TripRow[];
  const total = trips.length;
  return {
    total_trips: total,
    active_trips: trips.filter((t: TripRow) => t.status === "ACTIVE").length,
    completed_trips: trips.filter((t: TripRow) => t.status === "COMPLETED").length,
    total_distance: trips.reduce((sum: number, t: TripRow) => sum + (t.distance || 0), 0),
    total_seats_booked: trips.reduce((sum: number, t: TripRow) => sum + (t.seats_booked || 0), 0),
  };
}

/**
 * Trajets d'un conducteur (pour profil utilisateur)
 * Optimisation: count + data en une seule requête
 */
export async function getTripsByDriver(
  driverId: string,
  options: { limit?: number; offset?: number } = {}
): Promise<{ trips: TripListItem[]; total: number }> {
  const { limit = 5, offset = 0 } = options;
  const supabase = createServerClient();

  const { data, count, error } = await supabase
    .from("trips")
    .select(`
      trip_id,
      departure_name,
      destination_name,
      departure_schedule,
      distance,
      seats_available,
      seats_published,
      passenger_price,
      status
    `, { count: "exact" })
    .eq("driver_id", driverId)
    .order("departure_schedule", { ascending: false })
    .range(offset, offset + limit - 1);

  if (error) {
    console.error("getTripsByDriver error:", error);
    return { trips: [], total: 0 };
  }

  return {
    trips: data as TripListItem[],
    total: count || 0,
  };
}

/**
 * Liste des trajets avec infos conducteur (pour le tableau enrichi)
 */
export async function getTripsWithDriver(limit = 50): Promise<TripDetail[]> {
  const supabase = createServerClient();

  const { data, error } = await supabase
    .from("trips")
    .select(`
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
        display_name,
        photo_url,
        phone_number,
        rating,
        rating_count,
        is_driver_doc_validated
      )
    `)
    .order("departure_schedule", { ascending: false })
    .limit(limit);

  if (error) {
    console.error("getTripsWithDriver error:", error);
    return [];
  }

  type TripWithDriverRow = {
    trip_id: string;
    departure_name: string | null;
    departure_description: string | null;
    departure_latitude: number | null;
    departure_longitude: number | null;
    destination_name: string | null;
    destination_description: string | null;
    destination_latitude: number | null;
    destination_longitude: number | null;
    departure_schedule: string | null;
    distance: number | null;
    polyline: string | null;
    seats_available: number | null;
    seats_published: number | null;
    seats_booked: number | null;
    passenger_price: number | null;
    driver_price: number | null;
    status: string | null;
    auto_confirmation: boolean | null;
    created_at: string | null;
    driver_id: string | null;
    driver: unknown; // Supabase returns array or object
  };

  type DriverData = {
    display_name: string | null;
    photo_url: string | null;
    phone_number: string | null;
    rating: number | null;
    rating_count: number | null;
    is_driver_doc_validated: boolean | null;
  };

  return (data as unknown as TripWithDriverRow[]).map((t: TripWithDriverRow) => {
    const rawDriver = t.driver;
    const driver: DriverData | null = Array.isArray(rawDriver)
      ? (rawDriver[0] as DriverData | undefined) || null
      : (rawDriver as DriverData | null);

    return {
      trip_id: t.trip_id,
      departure_name: t.departure_name,
      departure_description: t.departure_description,
      departure_latitude: t.departure_latitude,
      departure_longitude: t.departure_longitude,
      destination_name: t.destination_name,
      destination_description: t.destination_description,
      destination_latitude: t.destination_latitude,
      destination_longitude: t.destination_longitude,
      departure_schedule: t.departure_schedule,
      distance: t.distance,
      polyline: t.polyline,
      seats_available: t.seats_available,
      seats_published: t.seats_published,
      seats_booked: t.seats_booked,
      passenger_price: t.passenger_price,
      driver_price: t.driver_price,
      status: t.status,
      auto_confirmation: t.auto_confirmation,
      created_at: t.created_at,
      driver_id: t.driver_id,
      driver_name: driver?.display_name || null,
      driver_photo: driver?.photo_url || null,
      driver_phone: driver?.phone_number || null,
      driver_rating: driver?.rating || null,
      driver_rating_count: driver?.rating_count || null,
      driver_verified: driver?.is_driver_doc_validated || null,
    } as TripDetail;
  });
}

// =====================================================
// Requêtes pour la page Map
// =====================================================

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
