"use server";

import { revalidatePath } from "next/cache";
import { createAdminClient } from "@/lib/supabase";
import { auth } from "@/lib/auth";
import { getDashboardStats } from "@/lib/queries/stats";
import { askKlandoAI } from "@/lib/gemini";

export type InsightCategory = 'REVENUE' | 'CONVERSION' | 'USER_QUALITY' | 'GROWTH' | 'GENERAL';

export interface MarketingInsight {
  id: string;
  category: InsightCategory;
  title: string;
  content: string;
  summary: string;
  created_at: string;
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
