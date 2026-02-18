import { createServerClient } from "../../supabase";

export interface MarketingFlowStat {
  origin_city: string;
  destination_city: string;
  request_count: number;
  avg_origin_lat: number;
  avg_origin_lng: number;
  avg_dest_lat: number;
  avg_dest_lng: number;
}

/**
 * Récupère les statistiques de flux pour le marketing
 */
export async function getMarketingFlowStats(): Promise<MarketingFlowStat[]> {
  const supabase = createServerClient();

  const { data, error } = await supabase.rpc("get_marketing_flow_stats");

  if (error) {
    console.error("getMarketingFlowStats error:", error);
    return [];
  }

  return data as MarketingFlowStat[];
}
