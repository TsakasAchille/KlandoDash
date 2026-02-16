import { createServerClient } from "../../supabase";
import { TripStats } from "@/types/trip";

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
