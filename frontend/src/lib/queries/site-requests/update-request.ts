import { createServerClient } from "../../supabase";
import { SiteTripRequestStatus } from "@/types/site-request";

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
