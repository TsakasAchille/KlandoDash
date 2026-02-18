"use server";

import { revalidatePath } from "next/cache";
import { createAdminClient } from "@/lib/supabase";
import { GlobalAIService } from "@/features/site-requests/services/global-ai.service";
import { auth } from "@/lib/auth";

/**
 * Lance le scan global d'intelligence
 */
export async function runGlobalScanAction() {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  try {
    const count = await GlobalAIService.runGlobalIntelligenceScan();
    revalidatePath("/marketing");
    return { success: true, count };
  } catch (error) {
    console.error("[AI Action] Global scan failed:", error);
    return { success: false, message: "Erreur lors du scan global." };
  }
}

/**
 * Met à jour le statut d'une recommandation
 */
export async function updateRecommendationStatusAction(id: string, status: 'APPLIED' | 'DISMISSED') {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  const { error } = await supabase
    .from('dash_ai_recommendations')
    .update({ status, updated_at: new Date().toISOString() })
    .eq('id', id);

  if (error) return { success: false };
  revalidatePath("/marketing");
  return { success: true };
}

/**
 * Récupère les recommandations depuis la DB
 */
export async function getStoredRecommendationsAction() {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  const { data, error } = await supabase
    .from('dash_ai_recommendations')
    .select('*')
    .order('priority', { ascending: false })
    .order('created_at', { ascending: false });

  if (error) return { success: false, data: [] };
  return { success: true, data };
}
