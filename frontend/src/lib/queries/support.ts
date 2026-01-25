import { createServerClient } from "../supabase";
import type {
  SupportTicketWithUser,
  TicketDetail,
  SupportStats,
  TicketStatus,
} from "@/types/support";

// =====================================================
// Requetes de lecture (Read)
// =====================================================

/**
 * Liste des tickets avec infos utilisateur
 * Utilise la fonction RPC get_tickets_with_user
 */
export async function getTicketsWithUser(options: {
  status?: TicketStatus | null;
  limit?: number;
  offset?: number;
} = {}): Promise<SupportTicketWithUser[]> {
  const { status = null, limit = 50, offset = 0 } = options;
  const supabase = createServerClient();

  const { data, error } = await supabase.rpc("get_tickets_with_user", {
    p_status: status,
    p_limit: limit,
    p_offset: offset,
  });

  if (error) {
    console.error("getTicketsWithUser error:", error);
    return [];
  }

  return (data || []) as SupportTicketWithUser[];
}

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

/**
 * Compte total des tickets (pour pagination)
 */
export async function getTicketsCount(
  status?: TicketStatus | null
): Promise<number> {
  const supabase = createServerClient();

  let query = supabase
    .from("support_tickets")
    .select("ticket_id", { count: "exact", head: true });

  if (status) {
    query = query.eq("status", status);
  }

  const { count, error } = await query;

  if (error) {
    console.error("getTicketsCount error:", error);
    return 0;
  }

  return count || 0;
}

// =====================================================
// Requetes d'ecriture (Write) - via RPC
// =====================================================

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

// =====================================================
// Requetes directes (fallback si RPC non disponible)
// =====================================================

/**
 * Liste des tickets (requete directe sans RPC)
 * Utilisee si les fonctions RPC ne sont pas encore deployees
 */
export async function getTicketsDirect(options: {
  status?: TicketStatus | null;
  limit?: number;
  offset?: number;
} = {}): Promise<SupportTicketWithUser[]> {
  const { status = null, limit = 50, offset = 0 } = options;
  const supabase = createServerClient();

  let query = supabase
    .from("support_tickets")
    .select(`
      ticket_id,
      subject,
      message,
      status,
      contact_preference,
      phone,
      mail,
      created_at,
      updated_at,
      user_id,
      user:users!support_tickets_user_id_fkey (
        uid,
        display_name,
        phone_number,
        email
      )
    `)
    .order("created_at", { ascending: false })
    .range(offset, offset + limit - 1);

  if (status) {
    query = query.eq("status", status);
  }

  const { data, error } = await query;

  if (error) {
    console.error("getTicketsDirect error:", error);
    return [];
  }

  type UserData = {
    uid: string;
    display_name: string | null;
    phone_number: string | null;
    email: string | null;
  };

  type TicketRow = {
    ticket_id: string;
    subject: string | null;
    message: string;
    status: string;
    contact_preference: string;
    phone: string | null;
    mail: string | null;
    created_at: string;
    updated_at: string;
    user_id: string;
    user: unknown;
  };

  return (data as unknown as TicketRow[]).map((t) => {
    const rawUser = t.user;
    const user: UserData | null = Array.isArray(rawUser)
      ? (rawUser[0] as UserData | undefined) || null
      : (rawUser as UserData | null);

    return {
      ticket_id: t.ticket_id,
      subject: t.subject,
      message: t.message,
      status: t.status as TicketStatus,
      contact_preference: t.contact_preference,
      created_at: t.created_at,
      updated_at: t.updated_at,
      user_uid: user?.uid || null,
      user_display_name: user?.display_name || null,
      user_phone: t.phone || user?.phone_number || null,
      user_email: t.mail || user?.email || null,
      comment_count: 0, // Non disponible en requete directe
    } as SupportTicketWithUser;
  });
}
