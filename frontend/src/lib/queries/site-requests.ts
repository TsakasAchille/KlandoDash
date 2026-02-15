import { createServerClient } from "../supabase";
import { SiteTripRequest, SiteTripRequestStatus, SiteTripRequestsStats } from "@/types/site-request";

export interface PublicTrip {
  id: string;
  departure_city: string;
  arrival_city: string;
  departure_time: string;
  seats_available?: number;
  polyline?: string | null;
  destination_latitude?: number | null;
  destination_longitude?: number | null;
}

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
  updates: { 
    status?: SiteTripRequestStatus; 
    notes?: string;
    ai_recommendation?: string;
    ai_updated_at?: string;
  }
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
