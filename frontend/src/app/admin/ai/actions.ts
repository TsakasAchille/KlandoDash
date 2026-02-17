"use server";

import { revalidatePath } from "next/cache";
import { createAdminClient } from "@/lib/supabase";
import { GlobalAIService } from "@/features/site-requests/services/global-ai.service";

/**
 * Lance le scan global d'intelligence
 */
export async function runGlobalScanAction() {
  try {
    const count = await GlobalAIService.runGlobalIntelligenceScan();
    revalidatePath("/admin/ai");
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
  const supabase = createAdminClient();
  const { error } = await supabase
    .from('dash_ai_recommendations')
    .update({ status, updated_at: new Date().toISOString() })
    .eq('id', id);

  if (error) return { success: false };
  revalidatePath("/admin/ai");
  return { success: true };
}

/**
 * Récupère les recommandations depuis la DB
 */
export async function getStoredRecommendationsAction() {
  const supabase = createAdminClient();
  const { data, error } = await supabase
    .from('dash_ai_recommendations')
    .select('*')
    .eq('status', 'PENDING')
    .order('priority', { ascending: false })
    .order('created_at', { ascending: false });

  if (error) return { success: false, data: [] };
  return { success: true, data };
}
