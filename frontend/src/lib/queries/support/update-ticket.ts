import { createServerClient } from "../../supabase";
import { TicketStatus } from "@/types/support";

/**
 * Mettre a jour le status d'un ticket
 * Utilise la fonction RPC update_ticket_status
 */
export async function updateTicketStatus(
  ticketId: string,
  status: TicketStatus
): Promise<{ success: boolean; error?: string }> {
  const supabase = createServerClient();

  const { error } = await supabase.rpc("update_ticket_status", {
    p_ticket_id: ticketId,
    p_status: status,
  });

  if (error) {
    console.error("updateTicketStatus error:", error);
    return { success: false, error: error.message };
  }

  return { success: true };
}
