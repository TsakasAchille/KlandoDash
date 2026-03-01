"use server";

import { createAdminClient } from "@/lib/supabase";
import { auth } from "@/lib/auth";
import { revalidatePath } from "next/cache";

/**
 * Envoie un message dans le chat interne
 */
export async function sendInternalMessageAction(content: string, channelId: string = 'general') {
  const session = await auth();
  if (!session?.user?.email) throw new Error("Unauthorized");

  const supabase = createAdminClient();
  
  const { data, error } = await supabase
    .from("dash_internal_messages")
    .insert([{
      sender_email: session.user.email,
      content: content,
      channel_id: channelId
    }])
    .select()
    .single();

  if (error) {
    console.error("Erreur sendInternalMessageAction:", error.message);
    return { success: false, error: error.message };
  }

  revalidatePath("/chats");
  return { success: true, message: data };
}
