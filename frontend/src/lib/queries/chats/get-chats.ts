import { createServerClient } from "@/lib/supabase";
import { unstable_noStore as noStore } from "next/cache";
import { InternalMessage } from "@/types/chat";

/**
 * Récupère les messages d'un salon interne (ex: general)
 */
export async function getInternalMessages(channelId: string = 'general'): Promise<InternalMessage[]> {
  noStore();
  const supabase = createServerClient();

  const { data, error } = await supabase
    .from("dash_internal_messages")
    .select(`
      *,
      sender:dash_authorized_users(role)
    `)
    .eq("channel_id", channelId)
    .order("created_at", { ascending: true })
    .limit(100);

  if (error) {
    console.error("Erreur getInternalMessages:", error.message);
    return [];
  }

  return data as any as InternalMessage[];
}
