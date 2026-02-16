import { createServerClient } from "../../supabase";
import { SiteTripRequest, SiteTripRequestStatus } from "@/types/site-request";

/**
 * Récupère la liste des demandes provenant du site vitrine
 */
export async function getSiteTripRequests(options: {
  limit?: number;
  offset?: number;
  status?: SiteTripRequestStatus | 'ALL';
  hidePast?: boolean;
} = {}): Promise<SiteTripRequest[]> {
  const { limit = 50, offset = 0, status = 'ALL', hidePast = true } = options;
  const supabase = createServerClient();

  let query = supabase
    .from("site_trip_requests")
    .select("*, matches:site_trip_request_matches(trip_id, proximity_score)")
    .order("created_at", { ascending: false })
    .range(offset, offset + limit - 1);

  if (status && status !== 'ALL') {
    query = query.eq("status", status);
  }

  if (hidePast) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    // On inclut les dates >= aujourd'hui OU les dates non spécifiées (Dès que possible)
    query = query.or(`desired_date.gte.${today.toISOString()},desired_date.is.null`);
  }

  const { data, error } = await query;

  if (error) {
    console.error("getSiteTripRequests error:", error);
    return [];
  }

  return data as SiteTripRequest[];
}
