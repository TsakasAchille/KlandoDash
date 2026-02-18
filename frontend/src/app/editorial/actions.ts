"use server";

import { createServerClient } from "@/lib/supabase";
import { MarketingComment } from "../marketing/types";
import { revalidatePath } from "next/cache";

/**
 * Récupère les commentaires d'une communication ou d'un email
 */
export async function getMarketingComments(params: { commId?: string, emailId?: string }) {
  const supabase = createServerClient();
  
  let query = supabase
    .from('dash_marketing_comments')
    .select(`
      *,
      author:dash_authorized_users(display_name, avatar_url)
    `)
    .order('created_at', { ascending: true });

  if (params.commId) {
    query = query.eq('comm_id', params.commId);
  } else if (params.emailId) {
    query = query.eq('email_id', params.emailId);
  } else {
    return [];
  }

  const { data, error } = await query;

  if (error) {
    console.error("Erreur getMarketingComments:", error);
    return [];
  }

  return data as MarketingComment[];
}

/**
 * Ajoute un commentaire
 */
export async function addMarketingComment(params: { 
  commId?: string, 
  emailId?: string, 
  userEmail: string, 
  content: string 
}) {
  const supabase = createServerClient();

  const { error } = await supabase
    .from('dash_marketing_comments')
    .insert([{
      comm_id: params.commId || null,
      email_id: params.emailId || null,
      user_email: params.userEmail,
      content: params.content
    }]);

  if (error) {
    console.error("Erreur addMarketingComment:", error);
    return { success: false, error: error.message };
  }

  return { success: true };
}

/**
 * Met à jour l'image d'une communication ou d'un email
 */
export async function updateMarketingVisual(params: {
    commId?: string,
    emailId?: string,
    imageUrl: string
}) {
    const supabase = createServerClient();

    if (params.commId) {
        const { error } = await supabase
            .from('dash_marketing_communications')
            .update({ image_url: params.imageUrl })
            .eq('id', params.commId);
        
        if (error) return { success: false, error: error.message };
    } else if (params.emailId) {
        const { error } = await supabase
            .from('dash_marketing_emails')
            .update({ image_url: params.imageUrl })
            .eq('id', params.emailId);
        
        if (error) return { success: false, error: error.message };
    }

    revalidatePath('/editorial');
    return { success: true };
}
