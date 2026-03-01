import { createServerClient } from "@/lib/supabase";
import { unstable_noStore as noStore } from "next/cache";
import { ChatMessage, Conversation } from "@/types/chat";

/**
 * Récupère les messages d'un trajet spécifique
 */
export async function getChatMessages(tripId: string): Promise<ChatMessage[]> {
  noStore();
  const supabase = createServerClient();

  // On récupère d'abord les messages
  const { data: messages, error } = await supabase
    .from("chats")
    .select("*")
    .eq("trip_id", tripId)
    .order("timestamp", { ascending: true });

  if (error) {
    console.error("Erreur getChatMessages:", error.message);
    return [];
  }

  if (!messages || messages.length === 0) return [];

  // On récupère les profils des expéditeurs manuellement pour éviter les erreurs de jointure
  const senderIds = Array.from(new Set(messages.map(m => m.sender_id).filter(Boolean)));
  
  if (senderIds.length > 0) {
    const { data: profiles } = await supabase
      .from("users")
      .select("uid, display_name, photo_url")
      .in("uid", senderIds);

    if (profiles) {
      return messages.map(m => ({
        ...m,
        sender: profiles.find(p => p.uid === m.sender_id)
      })) as ChatMessage[];
    }
  }

  return messages as ChatMessage[];
}

/**
 * Récupère la liste des conversations (groupées par trip_id)
 */
export async function getRecentConversations(): Promise<Conversation[]> {
  noStore();
  const supabase = createServerClient();

  // 1. Récupérer les messages bruts (sans jointure trips pour éviter l'erreur de cache)
  const { data: messages, error } = await supabase
    .from("chats")
    .select("trip_id, message, timestamp, sender_id")
    .order("timestamp", { ascending: false })
    .limit(1000);

  if (error) {
    console.error("Erreur getRecentConversations (Fetch):", error.message);
    return [];
  }

  if (!messages || messages.length === 0) return [];

  // 2. Grouper par trip_id et collecter les IDs uniques
  const conversationsMap = new Map<string, Conversation>();
  const allTripIds = new Set<string>();
  const allUserIds = new Set<string>();

  for (const row of messages) {
    if (!row.trip_id) continue;
    allTripIds.add(row.trip_id);
    if (row.sender_id) allUserIds.add(row.sender_id);

    if (!conversationsMap.has(row.trip_id)) {
      conversationsMap.set(row.trip_id, {
        trip_id: row.trip_id,
        last_message: row.message,
        last_timestamp: row.timestamp,
        participant_ids: [],
        participants: [],
      });
    }

    const conv = conversationsMap.get(row.trip_id)!;
    if (row.sender_id && !conv.participant_ids.includes(row.sender_id)) {
      conv.participant_ids.push(row.sender_id);
    }
  }

  // 3. Récupérer les détails des trajets manuellement
  if (allTripIds.size > 0) {
    const { data: trips } = await supabase
      .from("trips")
      .select("trip_id, departure_name, destination_name, driver_id")
      .in("trip_id", Array.from(allTripIds));

    if (trips) {
      trips.forEach(t => {
        const conv = conversationsMap.get(t.trip_id);
        if (conv) {
          conv.departure_name = t.departure_name;
          conv.destination_name = t.destination_name;
          if (t.driver_id) allUserIds.add(t.driver_id);
        }
      });
    }
  }

  // 4. Récupérer les profils utilisateurs manuellement
  if (allUserIds.size > 0) {
    const { data: profiles } = await supabase
      .from("users")
      .select("uid, display_name, photo_url")
      .in("uid", Array.from(allUserIds));

    if (profiles) {
      conversationsMap.forEach(conv => {
        conv.participants = profiles.filter(p => conv.participant_ids.includes(p.uid));
      });
    }
  }

  return Array.from(conversationsMap.values());
}
