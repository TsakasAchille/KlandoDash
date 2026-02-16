import { createServerClient } from "../../supabase";
import { SupportStats } from "@/types/support";

/**
 * Statistiques du support
 * NOTE: Approche simple pour v1 (comptage JS cote client)
 * A terme: RPC dediee avec COUNT(*) GROUP BY cote DB
 */
export async function getSupportStats(): Promise<SupportStats> {
  const supabase = createServerClient();

  const { data, error } = await supabase
    .from("support_tickets")
    .select("status");

  if (error) {
    console.error("getSupportStats error:", error);
    return { total: 0, open: 0, closed: 0, pending: 0 };
  }

  type StatusRow = { status: string | null };
  const tickets = (data || []) as StatusRow[];

  return {
    total: tickets.length,
    open: tickets.filter((t) => t.status === "OPEN").length,
    closed: tickets.filter((t) => t.status === "CLOSED").length,
    pending: tickets.filter((t) => t.status === "PENDING").length,
  };
}
