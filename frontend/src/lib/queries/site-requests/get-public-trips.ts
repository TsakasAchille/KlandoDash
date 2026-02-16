import { createServerClient } from "../../supabase";
import { PublicTrip } from "./types";

/**
 * Récupère les trajets actuellement affichés en direct sur le site
 */
export async function getPublicPendingTrips(): Promise<PublicTrip[]> {
  const supabase = createServerClient();
  const { data, error } = await supabase
    .from("public_pending_trips")
    .select("*")
    .order("departure_time", { ascending: true });

  if (error) {
    console.error("getPublicPendingTrips error:", error);
    return [];
  }
  return (data || []) as PublicTrip[];
}

/**
 * Récupère les derniers trajets terminés affichés sur le site
 */
export async function getPublicCompletedTrips(): Promise<PublicTrip[]> {
  const supabase = createServerClient();
  const { data, error } = await supabase
    .from("public_completed_trips")
    .select("*")
    .limit(10);

  if (error) {
    console.error("getPublicCompletedTrips error:", error);
    return [];
  }
  return (data || []) as PublicTrip[];
}
