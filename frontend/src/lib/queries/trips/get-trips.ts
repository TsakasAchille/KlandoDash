import { createServerClient } from "../../supabase";
import { TripListItem, TripDetail } from "@/types/trip";

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
 * Trajets d'un conducteur (pour profil utilisateur)
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
 * Liste des trajets avec infos conducteur (pour le tableau enrichi) avec pagination et filtres
 */
export async function getTripsWithDriver(options: {
  page?: number;
  pageSize?: number;
  status?: string;
  search?: string;
  minPrice?: number;
  maxPrice?: number;
  minDistance?: number;
  maxDistance?: number;
  driverId?: string;
  onlyPaid?: boolean;
} = {}): Promise<{ trips: TripDetail[], totalCount: number }> {
  const { 
    page = 1, 
    pageSize = 20, 
    status, 
    search, 
    minPrice, 
    maxPrice, 
    minDistance, 
    maxDistance,
    driverId,
    onlyPaid = false
  } = options;
  const supabase = createServerClient();
  const from = (page - 1) * pageSize;
  const to = from + pageSize - 1;

  let query = supabase
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
      ),
      bookings (
        status,
        transaction_id,
        transaction:transactions (
          amount,
          status
        ),
        user:users (
          uid,
          display_name,
          photo_url
        )
      )
    `, { count: "exact" });

  if (status && status !== "all") {
    query = query.eq("status", status);
  }

  // Si on veut seulement les trajets payés, on filtre ceux qui ont au moins une transaction SUCCESS
  if (onlyPaid) {
    // Utilisation de !inner join sur les bookings et les transactions pour forcer le filtrage
    // @ts-ignore
    query = query.select('*, bookings!inner(transaction!inner(status))').eq('bookings.transaction.status', 'SUCCESS');
  }

  if (driverId && driverId !== "all") {
    query = query.eq("driver_id", driverId);
  }

  if (search) {
    query = query.or(`departure_name.ilike.%${search}%,destination_name.ilike.%${search}%,trip_id.ilike.%${search}%`);
  }

  if (minPrice !== undefined) {
    query = query.gte("passenger_price", minPrice);
  }
  if (maxPrice !== undefined) {
    query = query.lte("passenger_price", maxPrice);
  }

  if (minDistance !== undefined) {
    query = query.gte("distance", minDistance);
  }
  if (maxDistance !== undefined) {
    query = query.lte("distance", maxDistance);
  }

  const { data, error, count } = await query
    .order("departure_schedule", { ascending: false })
    .range(from, to);

  if (error) {
    console.error("getTripsWithDriver error:", error);
    return { trips: [], totalCount: 0 };
  }

  type DriverData = {
    display_name: string | null;
    photo_url: string | null;
    phone_number: string | null;
    rating: number | null;
    rating_count: number | null;
    is_driver_doc_validated: boolean | null;
  };

  type PassengerData = {
    uid: string;
    display_name: string | null;
    photo_url: string | null;
  };

  interface BookingRaw {
    status: string;
    transaction_id: string | null;
    transaction: {
      amount: number;
      status: string;
    } | null;
    user: unknown;
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const trips = (data as any[]).map((t) => {
    const rawDriver = t.driver;
    const driver: DriverData | null = Array.isArray(rawDriver)
      ? (rawDriver[0] as DriverData | undefined) || null
      : (rawDriver as DriverData | null);

    const rawBookings = t.bookings as unknown as BookingRaw[] || [];
    
    let hasSuccessfulTransaction = false;
    let totalPaidAmount = 0;

    const passengers = rawBookings
      .map((b: BookingRaw) => {
        const rawUser = b.user;
        if (!rawUser) return null;
        
        const isPaid = b.transaction?.status === 'SUCCESS';
        if (isPaid) {
          hasSuccessfulTransaction = true;
          totalPaidAmount += b.transaction?.amount || 0;
        }

        const userData = Array.isArray(rawUser)
          ? (rawUser[0] as PassengerData | undefined) || null
          : (rawUser as PassengerData | null);
          
        if (!userData) return null;
        
        return {
          ...userData,
          has_paid: isPaid,
          amount_paid: b.transaction?.amount || 0
        };
      })
      .filter((p): p is (PassengerData & { has_paid: boolean, amount_paid: number }) => p !== null);

    // Si on a activé le filtre onlyPaid mais que par miracle PostgREST nous a retourné des trajets non payés (si pas d'inner join possible)
    // on pourrait refiltrer ici, mais ça fausserait la pagination. 
    // L'idéal est de le faire en SQL.

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
      passengers: passengers,
      has_successful_transaction: hasSuccessfulTransaction,
      total_paid_amount: totalPaidAmount,
    } as TripDetail;
  });

  // Si on a le filtre onlyPaid, on s'assure de ne renvoyer que ceux qui ont effectivement des paiements réussis
  // (Utile car le filtre .not('bookings.transaction_id', 'is', null) peut être imprécis selon le schéma)
  const finalTrips = onlyPaid ? trips.filter(t => t.has_successful_transaction) : trips;

  return { trips: finalTrips, totalCount: onlyPaid ? finalTrips.length : (count || 0) };
}
