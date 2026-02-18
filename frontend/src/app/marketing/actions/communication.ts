"use server";

import { revalidatePath } from "next/cache";
import { createAdminClient } from "@/lib/supabase";
import { auth } from "@/lib/auth";
import { askKlandoAI } from "@/lib/gemini";
import { getDashboardStats } from "@/lib/queries/stats";
import { CommPlatform, MarketingComm, CommStatus } from "../types";

/**
 * Génère des idées de communication stratégiques via IA
 */
export async function generateCommIdeasAction() {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const stats = await getDashboardStats();
  const supabase = createAdminClient();

  const prompt = `
    En tant qu'expert marketing pour Klando au Sénégal, propose 3 angles de communication percutants basés sur ces chiffres : ${JSON.stringify(stats)}.
    Chaque angle doit avoir un titre, un texte d'explication et une suggestion de visuel.
    Réponds en JSON STRICT : {"ideas": [{"title": "...", "content": "...", "visual": "..."}] }
  `;

  try {
    const aiResponse = await askKlandoAI(prompt, { context: stats });
    const jsonMatch = aiResponse.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error("IA JSON Error");
    
    const { ideas } = JSON.parse(jsonMatch[0]);

    if (ideas && ideas.length > 0) {
      await supabase.from('dash_marketing_communications').insert(
        ideas.map((i: any) => ({
          type: 'IDEA',
          title: i.title,
          content: i.content,
          visual_suggestion: i.visual,
          platform: 'GENERAL',
          status: 'NEW'
        }))
      );
    }

    revalidatePath("/marketing");
    return { success: true, count: ideas.length };
  } catch (err) {
    console.error(err);
    return { success: false };
  }
}

/**
 * Génère un post pour un réseau social spécifique
 */
export async function generateSocialPostAction(platform: CommPlatform, topic: string) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();

  const prompt = `
    Rédige une publication pour ${platform} sur le thème : "${topic}".
    Adapte le ton :
    - TIKTOK : Très court, punchy, mentionne une idée de musique tendance, beaucoup d'emojis.
    - INSTAGRAM : Inspirant, esthétique, texte aéré.
    - X (Twitter) : Court, informatif, engageant.
    
    Réponds en JSON STRICT : { "title": "...", "content": "...", "hashtags": ["...", "..."], "visual": "..." }
  `;

  try {
    const aiResponse = await askKlandoAI(prompt, { platform, topic });
    const jsonMatch = aiResponse.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error("IA JSON Error");
    
    const data = JSON.parse(jsonMatch[0]);

    const { data: post, error } = await supabase.from('dash_marketing_communications').insert([{
      type: 'POST',
      platform,
      title: data.title,
      content: data.content,
      hashtags: data.hashtags,
      visual_suggestion: data.visual,
      status: 'NEW'
    }]).select().single();

    if (error) throw error;

    revalidatePath("/marketing");
    return { success: true, post };
  } catch (err) {
    return { success: false };
  }
}

/**
 * Génère une publication pour promouvoir les trajets en attente (Site Requests)
 */
export async function generatePendingRequestsPostAction(platform: CommPlatform) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();

  // 1. Récupérer les trajets en attente les plus récents (intentions clients)
  const { data: requests, error: reqError } = await supabase
    .from('site_trip_requests')
    .select('origin_city, destination_city, desired_date')
    .eq('status', 'NEW')
    .order('created_at', { ascending: false })
    .limit(5);

  if (reqError || !requests || requests.length === 0) {
    return { success: false, message: "Aucun trajet en attente trouvé." };
  }

  const tripsContext = requests.map(r => 
    `${r.origin_city} -> ${r.destination_city} (${r.desired_date || 'ASAP'})`
  ).join(', ');

  const prompt = `
    En tant que Community Manager de Klando Sénégal, crée une publication ${platform} pour inviter les conducteurs à répondre à ces demandes de trajets en attente :
    Demandes : ${tripsContext}
    
    L'objectif est de trouver des chauffeurs pour ces passagers. 
    Utilise un ton communautaire, solidaire et efficace.
    
    Réponds en JSON STRICT : { "title": "...", "content": "...", "hashtags": ["...", "..."], "visual": "..." }
  `;

  try {
    const aiResponse = await askKlandoAI(prompt, { platform, requests });
    const jsonMatch = aiResponse.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error("IA JSON Error");
    
    const data = JSON.parse(jsonMatch[0]);

    const { data: post, error } = await supabase.from('dash_marketing_communications').insert([{
      type: 'POST',
      platform,
      title: data.title,
      content: data.content,
      hashtags: data.hashtags,
      visual_suggestion: data.visual,
      status: 'NEW'
    }]).select().single();

    if (error) throw error;

    revalidatePath("/marketing");
    return { success: true, post };
  } catch (err) {
    console.error(err);
    return { success: false };
  }
}

/**
 * Crée manuellement une communication
 */
export async function createMarketingCommAction(data: Partial<MarketingComm>) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  const { data: post, error } = await supabase
    .from('dash_marketing_communications')
    .insert([{
      type: 'POST',
      platform: data.platform || 'GENERAL',
      title: data.title,
      content: data.content,
      hashtags: data.hashtags || [],
      visual_suggestion: data.visual_suggestion || '',
      image_url: data.image_url || null,
      status: 'DRAFT'
    }])
    .select()
    .single();

  if (error) {
    console.error("[COMM CREATE ERROR]", error);
    return { success: false };
  }
  
  revalidatePath("/marketing");
  return { success: true, post };
}

/**
 * Utilise l'IA pour corriger et améliorer un texte de post
 */
export async function refineMarketingContentAction(content: string, platform: CommPlatform) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const prompt = `
    En tant qu'expert en communication pour Klando au Sénégal, corrige les fautes d'orthographe et améliore le style de ce brouillon pour ${platform}.
    Conserve les informations essentielles mais rends le texte plus engageant et punchy.
    Brouillon : "${content}"
    
    Réponds uniquement avec le texte corrigé et amélioré (pas de JSON, pas de blabla).
  `;

  try {
    const aiResponse = await askKlandoAI(prompt, { content, platform });
    return { success: true, refinedContent: aiResponse.trim() };
  } catch (err) {
    console.error("[REFINE ERROR]", err);
    return { success: false };
  }
}

/**
 * Met à jour une communication (Titre, contenu, plateforme, statut)
 */
export async function updateMarketingCommAction(id: string, updates: Partial<MarketingComm>) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  const { error } = await supabase
    .from('dash_marketing_communications')
    .update(updates)
    .eq('id', id);

  if (error) {
    console.error("[COMM UPDATE ERROR]", error);
    return { success: false };
  }
  
  revalidatePath("/marketing");
  return { success: true };
}

/**
 * Déplace une communication vers la corbeille
 */
export async function trashMarketingCommAction(id: string) {
  return updateMarketingCommAction(id, { status: 'TRASH' });
}

/**
 * Restaure une communication depuis la corbeille (repasse en DRAFT)
 */
export async function restoreMarketingCommAction(id: string) {
  return updateMarketingCommAction(id, { status: 'DRAFT' });
}

/**
 * Supprime définitivement une communication
 */
export async function deleteMarketingCommAction(id: string) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  const { error } = await supabase
    .from('dash_marketing_communications')
    .delete()
    .eq('id', id);

  if (error) return { success: false };
  
  revalidatePath("/marketing");
  return { success: true };
}

/**
 * Récupère l'historique de communication
 */
export async function getMarketingCommAction() {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  const { data, error } = await supabase
    .from('dash_marketing_communications')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) return { success: false, data: [] };
  return { success: true, data: data as MarketingComm[] };
}
