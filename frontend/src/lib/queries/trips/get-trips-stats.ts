import { createServerClient } from "../../supabase";
import { TripStats } from "@/types/trip";

/**
 * Statistiques globales des trajets (Optimisé via RPC)
 */
export async function getTripsStats(): Promise<TripStats> {
  const supabase = createServerClient();

  const { data, error } = await supabase.rpc("get_klando_stats_final");

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

  const byStatus = data.trips.byStatus || [];
  const activeCount = byStatus.find((s: any) => s.status === 'ACTIVE')?.count || 0;
  const completedCount = byStatus.find((s: any) => s.status === 'COMPLETED')?.count || 0;

  return {
    total_trips: data.trips.total,
    active_trips: activeCount,
    completed_trips: completedCount,
    total_distance: data.trips.totalDistance,
    total_seats_booked: data.trips.totalSeatsBooked,
  };
}
