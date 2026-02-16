import { createServerClient } from "../../supabase";
import { SiteTripRequestsStats } from "@/types/site-request";

/**
 * Récupère les statistiques des demandes du site
 */
export async function getSiteTripRequestsStats(options: { hidePast?: boolean } = {}): Promise<SiteTripRequestsStats> {
  const { hidePast = true } = options;
  const supabase = createServerClient();

  let query = supabase
    .from("site_trip_requests")
    .select("status, desired_date");

  if (hidePast) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    // On inclut les dates >= aujourd'hui OU les dates non spécifiées (Dès que possible)
    query = query.or(`desired_date.gte.${today.toISOString()},desired_date.is.null`);
  }

  const { data, error } = await query;

  if (error) {
    console.error("getSiteTripRequestsStats error:", error);
    return { total: 0, new: 0, reviewed: 0, contacted: 0 };
  }

  const stats = {
    total: data.length,
    new: data.filter(r => r.status === 'NEW').length,
    reviewed: data.filter(r => r.status === 'REVIEWED').length,
    contacted: data.filter(r => r.status === 'CONTACTED').length,
  };

  return stats;
}
