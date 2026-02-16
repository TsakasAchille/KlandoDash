import { createAdminClient } from "../../supabase";
import { SiteTripRequestStatus } from "@/types/site-request";

/**
 * Met à jour le statut ou les notes d'une demande
 * Utilise createAdminClient pour garantir la persistance des données calculées (polylines, etc.)
 */
export async function updateSiteTripRequest(
  id: string,
  updates: { 
    status?: SiteTripRequestStatus; 
    notes?: string;
    ai_recommendation?: string;
    ai_updated_at?: string;
    polyline?: string;
    origin_lat?: number;
    origin_lng?: number;
    destination_lat?: number;
    destination_lng?: number;
  }
): Promise<boolean> {
  const supabase = createAdminClient();
  
  console.log(`[DB] Updating site_trip_request ${id} with:`, Object.keys(updates));

  const { error } = await supabase
    .from("site_trip_requests")
    .update(updates)
    .eq("id", id);

  if (error) {
    console.error(`[DB ERROR] Failed to update site_trip_request ${id}:`, error.message, error.details, error.hint);
    return false;
  }

  console.log(`[DB] Successfully updated site_trip_request ${id}`);
  return true;
}
