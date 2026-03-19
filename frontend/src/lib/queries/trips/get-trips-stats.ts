import { createServerClient } from "../../supabase";
import { TripStats } from "@/types/trip";

interface StatusCount {
  status: string;
  count: number;
}

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
      pending_trips: 0,
      cancelled_trips: 0,
      paid_trips: 0,
      total_distance: 0,
      total_seats_booked: 0,
    };
  }

  const byStatus: StatusCount[] = data.trips.byStatus || [];
  
  // Agrégation des statuts pour correspondre aux catégories du dashboard
  const activeCount = byStatus
    .filter(s => s.status === 'ACTIVE' || s.status === 'STARTED')
    .reduce((acc, s) => acc + s.count, 0);
    
  const completedCount = byStatus
    .filter(s => s.status === 'COMPLETED' || s.status === 'CLOSED')
    .reduce((acc, s) => acc + s.count, 0);
    
  const pendingCount = byStatus
    .filter(s => s.status === 'PENDING')
    .reduce((acc, s) => acc + s.count, 0);
    
  const cancelledCount = byStatus
    .filter(s => s.status === 'CANCELLED')
    .reduce((acc, s) => acc + s.count, 0);

  return {
    total_trips: data.trips.total,
    active_trips: activeCount,
    completed_trips: completedCount,
    pending_trips: pendingCount,
    cancelled_trips: cancelledCount,
    paid_trips: data.trips.paid_count || 0,
    total_distance: data.trips.totalDistance,
    total_seats_booked: data.trips.totalSeatsBooked,
  };
}
