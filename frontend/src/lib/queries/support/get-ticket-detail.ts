import { createServerClient } from "../../supabase";
import { TicketDetail } from "@/types/support";

/**
 * Detail d'un ticket avec ses commentaires
 * Utilise la fonction RPC get_ticket_detail
 */
export async function getTicketDetail(
  ticketId: string
): Promise<TicketDetail | null> {
  const supabase = createServerClient();

  const { data, error } = await supabase.rpc("get_ticket_detail", {
    p_ticket_id: ticketId,
  });

  if (error) {
    console.error("getTicketDetail error:", error);
    return null;
  }

  if (!data || data.length === 0) {
    return null;
  }

  return data[0] as TicketDetail;
}
