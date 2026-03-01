import { createServerClient } from "@/lib/supabase";
import { unstable_noStore as noStore } from "next/cache";
import { ChatMessage, Conversation } from "@/types/chat";

/**
 * Récupère les messages d'un trajet spécifique
 */
export async function getChatMessages(tripId: string): Promise<ChatMessage[]> {
  noStore();
  const supabase = createServerClient();

  const { data, error } = await supabase
    .from("chats")
    .select(`
      id,
      trip_id,
      sender_id,
      message,
      timestamp,
      updated_at,
      sender:users (
        display_name,
        photo_url
      )
    `)
    .eq("trip_id", tripId)
    .order("timestamp", { ascending: true });

  if (error) {
    console.error("Erreur getChatMessages:", error);
    return [];
  }

  return (data || []) as any as ChatMessage[];
}

/**
 * Récupère la liste des conversations (groupées par trip_id)
 */
export async function getRecentConversations(): Promise<Conversation[]> {
  noStore();
  const supabase = createServerClient();

  const { data, error } = await supabase
    .from("chats")
    .select(`
      trip_id,
      message,
      timestamp,
      sender_id,
      trip:trips (
        departure_name,
        destination_name
      )
    `)
    .order("timestamp", { ascending: false })
    .limit(500);

  if (error) {
    console.error("Erreur getRecentConversations:", error);
    return [];
  }

  const conversationsMap = new Map<string, Conversation>();

  for (const row of (data || [])) {
    if (!row.trip_id) continue;

    if (!conversationsMap.has(row.trip_id)) {
      conversationsMap.set(row.trip_id, {
        trip_id: row.trip_id,
        last_message: row.message,
        last_timestamp: row.timestamp,
        participant_ids: [],
        participants: [],
        departure_name: (row.trip as any)?.departure_name,
        destination_name: (row.trip as any)?.destination_name,
      });
    }

    const conv = conversationsMap.get(row.trip_id)!;
    if (row.sender_id && !conv.participant_ids.includes(row.sender_id)) {
      conv.participant_ids.push(row.sender_id);
    }
  }

  return Array.from(conversationsMap.values());
}
