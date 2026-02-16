import { createServerClient } from "../../supabase";

/**
 * Recherche des trajets correspondant par proximité géographique (RPC)
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function findMatchingTrips(requestId: string, radiusKm: number = 5): Promise<any[]> {
  const supabase = createServerClient();

  const { data, error } = await supabase.rpc("find_matching_trips", {
    p_request_id: requestId,
    p_radius_km: radiusKm
  });

  if (error) {
    console.error("findMatchingTrips error:", error);
    return [];
  }

  return data || [];
}
