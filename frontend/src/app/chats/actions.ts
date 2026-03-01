"use server";

import { createAdminClient } from "@/lib/supabase";
import { auth } from "@/lib/auth";
import { revalidatePath } from "next/cache";

/**
 * Envoie un message dans une conversation (trip)
 */
export async function sendMessageAction(tripId: string, message: string) {
  const session = await auth();
  if (!session?.user?.email) throw new Error("Unauthorized");

  const supabase = createAdminClient();
  
  // On récupère l'UID de l'admin (ou on utilise son email si pas d'UID)
  // Note: La table chats utilise sender_id qui est normalement un UID utilisateur.
  // Pour l'admin, on peut soit utiliser son email, soit un UID système.
  
  const { data, error } = await supabase
    .from("chats")
    .insert([{
      id: crypto.randomUUID(),
      trip_id: tripId,
      sender_id: session.user.id || session.user.email,
      message: message,
      timestamp: new Date().toISOString()
    }])
    .select()
    .single();

  if (error) {
    console.error("Erreur sendMessageAction:", error);
    return { success: false, error: error.message };
  }

  revalidatePath("/chats");
  return { success: true, message: data };
}
