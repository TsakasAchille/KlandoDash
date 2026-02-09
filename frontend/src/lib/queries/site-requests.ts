import { createServerClient } from "../supabase";
import { SiteTripRequest, SiteTripRequestStatus, SiteTripRequestsStats } from "@/types/site-request";

/**
 * Récupère la liste des demandes provenant du site vitrine
 */
export async function getSiteTripRequests(options: {
  limit?: number;
  offset?: number;
  status?: SiteTripRequestStatus | 'ALL';
} = {}): Promise<SiteTripRequest[]> {
  const { limit = 50, offset = 0, status = 'ALL' } = options;
  const supabase = createServerClient();

  let query = supabase
    .from("site_trip_requests")
    .select("*")
    .order("created_at", { ascending: false })
    .range(offset, offset + limit - 1);

  if (status && status !== 'ALL') {
    query = query.eq("status", status);
  }

  const { data, error } = await query;

  if (error) {
    console.error("getSiteTripRequests error:", error);
    return [];
  }

  return data as SiteTripRequest[];
}

/**
 * Récupère les statistiques des demandes du site
 */
export async function getSiteTripRequestsStats(): Promise<SiteTripRequestsStats> {
  const supabase = createServerClient();

  const { data, error } = await supabase
    .from("site_trip_requests")
    .select("status");

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

/**
 * Met à jour le statut ou les notes d'une demande
 */
export async function updateSiteTripRequest(
  id: string,
  updates: { status?: SiteTripRequestStatus; notes?: string }
): Promise<boolean> {
  const supabase = createServerClient();

  const { error } = await supabase
    .from("site_trip_requests")
    .update(updates)
    .eq("id", id);

  if (error) {
    console.error("updateSiteTripRequest error:", error);
    return false;
  }

  return true;
}
