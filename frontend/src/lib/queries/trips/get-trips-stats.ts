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
  const activeCount = byStatus.find((s) => s.status === 'ACTIVE')?.count || 0;
  const completedCount = byStatus.find((s) => s.status === 'COMPLETED')?.count || 0;
  const pendingCount = byStatus.find((s) => s.status === 'PENDING')?.count || 0;
  const cancelledCount = byStatus.find((s) => s.status === 'CANCELLED')?.count || 0;

  // Récupération manuelle du nombre de trajets ayant au moins un paiement validé
  const { count: paidTripsCount } = await supabase
    .from('trips')
    .select('trip_id, bookings!inner(transaction!inner(status))', { count: 'exact', head: true })
    .eq('bookings.transaction.status', 'SUCCESS');

  return {
    total_trips: data.trips.total,
    active_trips: activeCount,
    completed_trips: completedCount,
    pending_trips: pendingCount,
    cancelled_trips: cancelledCount,
    paid_trips: paidTripsCount || 0,
    total_distance: data.trips.totalDistance,
    total_seats_booked: data.trips.totalSeatsBooked,
  };
}
