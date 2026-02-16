import { createServerClient } from "../../supabase";
import { SupportTicketWithUser, TicketStatus } from "@/types/support";

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
