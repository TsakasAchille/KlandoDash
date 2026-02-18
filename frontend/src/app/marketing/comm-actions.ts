"use server";

import { revalidatePath } from "next/cache";
import { createAdminClient } from "@/lib/supabase";
import { auth } from "@/lib/auth";
import { askKlandoAI } from "@/lib/gemini";
import { getDashboardStats } from "@/lib/queries/stats";

export type CommType = 'IDEA' | 'POST';
export type CommPlatform = 'TIKTOK' | 'INSTAGRAM' | 'X' | 'WHATSAPP' | 'GENERAL';

export interface MarketingComm {
  id: string;
  type: CommType;
  platform: CommPlatform;
  title: string;
  content: string;
  hashtags?: string[];
  visual_suggestion?: string;
  created_at: string;
}

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
          platform: 'GENERAL'
        }))
      );
    }

    revalidatePath("/marketing");
    return { success: true, count: ideas.length };
  } catch (err) {
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
      visual_suggestion: data.visual
    }]).select().single();

    if (error) throw error;

    revalidatePath("/marketing");
    return { success: true, post };
  } catch (err) {
    return { success: false };
  }
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
