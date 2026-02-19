import { createServerClient } from "../../supabase";
import { getDashboardStats } from "./get-dashboard-stats";
import { HomeSummary, PublicTrip } from "./types";
import { Trip } from "@/types/trip";
import { TransactionWithUser } from "@/types/transaction";
import { SupportTicketWithUser } from "@/types/support";
import { UserListItem } from "@/types/user";

/**
 * Récupère les stats globales et les dernières activités pour la page d'accueil
 */
export async function getHomeSummary(): Promise<HomeSummary> {
  const stats = await getDashboardStats();
  const supabase = createServerClient();

  // Fetch recent activities with individual error handling to prevent failure
  const [
    recentTripsRes,
    recentTxnsRes,
    recentTicketsRes,
    recentUsersRes,
    publicPendingRes,
    publicCompletedRes,
  ] = await Promise.all([
    supabase
      .from("trips")
      .select(`
        trip_id, departure_name, destination_name, departure_schedule,
        status, seats_available, passenger_price, total_seats:seats_published,
        driver:users!driver_id (display_name, photo_url)
      `)
      .order("created_at", { ascending: false })
      .limit(5),

    supabase
      .from("transactions")
      .select(`
        id, amount, status, type, code_service, phone, created_at,
        user:users!user_id (display_name, photo_url)
      `)
      .order("created_at", { ascending: false })
      .limit(5),

    supabase.rpc("get_tickets_with_user", {
      p_status: null,
      p_limit: 5,
      p_offset: 0,
    }),

    supabase
      .from("users")
      .select("uid, display_name, email, photo_url, role, created_at")
      .order("created_at", { ascending: false })
      .limit(5),

    supabase
      .from("public_pending_trips")
      .select("*")
      .order("departure_time", { ascending: true })
      .limit(4),

    supabase
      .from("public_completed_trips")
      .select("*")
      .limit(4),
  ]);

  if (recentUsersRes.error) console.error("Error fetching recent users:", recentUsersRes.error);
  if (recentTripsRes.error) console.error("Error fetching recent trips:", recentTripsRes.error);
  
  const recentUsersData = recentUsersRes.data || [];
  const recentTripsData = recentTripsRes.data || [];
  const recentTxnsData = recentTxnsRes.data || [];
  const recentTicketsData = recentTicketsRes.data || [];
  const publicPendingData = publicPendingRes.data || [];
  const publicCompletedData = publicCompletedRes.data || [];

  console.log("[HomeSummary] Recent Users Count:", recentUsersData.length);

  interface TripRaw {
    trip_id: string;
    departure_name: string | null;
    destination_name: string | null;
    departure_schedule: string | null;
    status: string | null;
    total_seats: number | null;
    driver: {
      display_name: string | null;
      photo_url: string | null;
    } | null;
  }

  // Transformer les trajets pour correspondre au type Trip
  const recentTrips = (recentTripsData as unknown as TripRaw[]).map((trip) => {
    return {
      trip_id: trip.trip_id,
      departure_city: trip.departure_name?.split(",")[0] || "N/A",
      destination_city: trip.destination_name?.split(",")[0] || "N/A",
      departure_schedule: trip.departure_schedule,
      status: trip.status,
      trip_distance: 0,
      passengers: [], 
      total_seats: trip.total_seats || 0,
      driver_name: trip.driver?.display_name || "N/A",
      driver_photo: trip.driver?.photo_url || null,
    };
  }) as unknown as Trip[];

  return {
    ...stats,
    recentTrips,
    recentTransactions: (recentTxnsData || []) as unknown as TransactionWithUser[],
    recentTickets: (recentTicketsData || []) as SupportTicketWithUser[],
    recentUsers: (recentUsersData || []) as UserListItem[],
    publicPending: (publicPendingData || []) as PublicTrip[],
    publicCompleted: (publicCompletedData || []) as PublicTrip[],
  };
}
