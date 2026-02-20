"use server";

import { revalidatePath } from "next/cache";
import { createAdminClient } from "@/lib/supabase";
import { auth } from "@/lib/auth";
import { getDashboardStats } from "@/lib/queries/stats";
import { askKlandoAI } from "@/lib/gemini";
import { InsightCategory, MarketingInsight } from "../types";
import fs from "fs/promises";
import path from "path";

/**
 * Sauvegarde le feedback sur une analyse stratégique et met à jour les mémoires IA
 */
export async function saveInsightFeedbackAction(id: string, isLiked: boolean, feedback?: string) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  
  // 1. Mise à jour en base
  const { data: insight, error } = await supabase
    .from('dash_marketing_insights')
    .update({ 
      is_liked: isLiked, 
      admin_feedback: feedback 
    })
    .eq('id', id)
    .select()
    .single();

  if (error) return { success: false };

  // 2. Mise à jour du fichier mémoire
  try {
    const memoryPath = path.join(process.cwd(), "docs/MARKETING_MEMORIES.md");
    let content = await fs.readFile(memoryPath, "utf-8");

    if (feedback) {
      const feedbackEntry = `\n*   **Feedback Stratégique (${new Date().toLocaleDateString()})** : "${feedback}" (Sur l'analyse: "${insight.title}")`;
      content = content.replace("## 2. Historique des Retours Admin (Apprentissage)", `## 2. Historique des Retours Admin (Apprentissage)${feedbackEntry}`);
    }

    if (isLiked) {
      const likeEntry = `\n*   **Analyse Approuvée** : "${insight.title}" - Aperçu: "${insight.content.substring(0, 50)}..."`;
      content = content.replace("## 3. Exemples de Succès (Liked)", `## 3. Exemples de Succès (Liked)${likeEntry}`);
    }

    await fs.writeFile(memoryPath, content, "utf-8");
  } catch (err) {
    console.error("[MEMORY UPDATE ERROR]", err);
  }

  revalidatePath("/stats");
  revalidatePath("/marketing");
  return { success: true };
}

/**
 * Lance l'analyse IA des statistiques marketing
 */
export async function runMarketingAIScanAction() {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  const stats = await getDashboardStats();

  const categories: { cat: InsightCategory; prompt: string; title: string }[] = [
    { 
      cat: 'CONVERSION', 
      title: 'Analyse des Conversions',
      prompt: `Analyse le taux de remplissage des trajets et le succès des réservations. Suggère des actions pour augmenter le nombre de passagers par trajet.` 
    },
    { 
      cat: 'REVENUE', 
      title: 'Performance Financière',
      prompt: `Analyse les revenus passagers vs prix chauffeurs et la marge Klando. Identifie les opportunités de croissance du chiffre d'affaires.` 
    },
    { 
      cat: 'USER_QUALITY', 
      title: 'Qualité & Rétention',
      prompt: `Analyse la base utilisateurs (drivers vérifiés, nouveaux inscrits). Suggère comment améliorer la qualité de service et fidéliser les meilleurs chauffeurs.` 
    }
  ];

  const results = [];

  for (const item of categories) {
    try {
      const aiResponse = await askKlandoAI(`${item.prompt} 
      IMPORTANT: Commence ton message par une seule phrase de résumé très percutante (max 120 caractères) suivie de deux retours à la ligne, puis développe ton analyse complète en Markdown.`, { 
        context: `Statistiques actuelles de Klando: ${JSON.stringify(stats)}`,
        category: item.cat 
      });

      // Extraire la première phrase comme résumé réel
      const parts = aiResponse.split('\n\n');
      const summary = parts[0].substring(0, 150);
      const content = parts.slice(1).join('\n\n') || aiResponse;

      results.push({
        category: item.cat,
        title: item.title,
        content: content,
        summary: summary,
        metadata: { stats_snapshot: stats }
      });
    } catch (err) {
      console.error(`[Marketing AI] Failed to analyze ${item.cat}:`, err);
    }
  }

  if (results.length > 0) {
    // Nettoyer les anciens rapports pour ces catégories pour n'avoir que le dernier "frais"
    const categoriesToClean = results.map(r => r.category);
    await supabase.from('dash_marketing_insights').delete().in('category', categoriesToClean);
    
    const { error } = await supabase.from('dash_marketing_insights').insert(results);
    if (error) throw error;
  }

  revalidatePath("/marketing");
  return { success: true, count: results.length };
}

/**
 * Récupère les derniers rapports IA
 */
export async function getMarketingInsightsAction(): Promise<{ success: boolean; data: MarketingInsight[] }> {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  const { data, error } = await supabase
    .from('dash_marketing_insights')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(10);

  if (error) return { success: false, data: [] };
  return { success: true, data: data as MarketingInsight[] };
}

/**
 * Génère une analyse flash pour la page Stats (Vue d'ensemble) et la sauvegarde
 */
export async function generateGlobalStatsInsightAction() {
  const session = await auth();
  if (!session || session.user.role !== "admin") throw new Error("Non autorisé");

  const stats = await getDashboardStats();
  const supabase = createAdminClient();

  // 1. Charger les mémoires marketing
  let marketingMemories = "";
  try {
    const memoryPath = path.join(process.cwd(), "docs/MARKETING_MEMORIES.md");
    marketingMemories = await fs.readFile(memoryPath, "utf-8");
  } catch (e) {
    console.warn("No memories found yet.");
  }
  
  const prompt = `
    En tant qu'analyste data senior pour Klando (covoiturage au Sénégal), analyse ces chiffres : ${JSON.stringify(stats)}.
    
    PRENDS EN COMPTE NOS PRÉFÉRENCES ET HISTORIQUE :
    ${marketingMemories}

    Donne-moi :
    1. Un commentaire court (2 phrases) sur la performance actuelle.
    2. Trois recommandations PRIORITAIRES et CONCRÈTES pour booster la plateforme cette semaine.
    
    Réponds en Markdown percutant avec des emojis.
  `;

  try {
    const aiResponse = await askKlandoAI(prompt, { context: stats });
    
    // Sauvegarde en base (on supprime l'ancien rapport GLOBAL_STATS d'abord)
    await supabase.from('dash_marketing_insights').delete().eq('category', 'GLOBAL_STATS');
    
    const { error } = await supabase.from('dash_marketing_insights').insert([{
      category: 'GLOBAL_STATS',
      title: 'Analyse Flash Performance',
      content: aiResponse,
      summary: aiResponse.substring(0, 150),
      metadata: { stats_snapshot: stats }
    }]);

    if (error) throw error;

    revalidatePath("/stats");
    return { success: true, analysis: aiResponse };
  } catch (err) {
    console.error(err);
    return { success: false };
  }
}

/**
 * Récupère la dernière analyse globale enregistrée
 */
export async function getLatestGlobalInsightAction() {
  const session = await auth();
  if (!session) return { success: false };

  const supabase = createAdminClient();
  const { data, error } = await supabase
    .from('dash_marketing_insights')
    .select('*')
    .eq('category', 'GLOBAL_STATS')
    .order('created_at', { ascending: false })
    .limit(1)
    .single();

  if (error || !data) return { success: false };
  return { success: true, data: data as MarketingInsight };
}
