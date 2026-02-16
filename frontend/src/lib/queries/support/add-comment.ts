import { createServerClient } from "../../supabase";

/**
 * Ajouter un commentaire a un ticket
 * Utilise la fonction RPC add_support_comment
 */
export async function addComment(
  ticketId: string,
  userId: string,
  commentText: string,
  source: "admin" | "system" = "admin"
): Promise<{ success: boolean; commentId?: string; error?: string }> {
  const supabase = createServerClient();

  const { data, error } = await supabase.rpc("add_support_comment", {
    p_ticket_id: ticketId,
    p_user_id: userId,
    p_comment_text: commentText,
    p_comment_source: source,
  });

  if (error) {
    console.error("addComment error:", error);
    return { success: false, error: error.message };
  }

  return { success: true, commentId: data as string };
}
