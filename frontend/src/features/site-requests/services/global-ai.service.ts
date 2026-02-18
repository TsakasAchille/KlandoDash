import { createAdminClient } from "@/lib/supabase";

export const GlobalAIService = {
  /**
   * Scan stratégique analytique (SANS IA systématique)
   * Identifie les opportunités de matching réelles via SQL.
   */
  async runGlobalIntelligenceScan() {
    const supabase = createAdminClient();
    console.log("[Marketing Scan] Starting analytical opportunity scan...");

    // 1. Récupérer les demandes en attente (Prospects)
    const { data: requests } = await supabase
      .from('site_trip_requests')
      .select('id, origin_city, destination_city, desired_date, ai_recommendation, ai_updated_at')
      .eq('status', 'NEW');

    if (!requests || requests.length === 0) return 0;

    // 2. Nettoyer les anciennes recommandations PENDING pour repartir sur du propre
    await supabase.from('dash_ai_recommendations').delete().eq('status', 'PENDING');

    const recommendations = [];

    // 3. Analyser chaque demande via SQL
    for (const req of requests) {
      try {
        // Appeler la fonction de matching SQL (Rayon par défaut 15km pour le scan large)
        const { data: matches, error: matchError } = await supabase.rpc('find_matching_trips', {
          p_request_id: req.id,
          p_radius_km: 15.0
        });

        if (matchError) throw matchError;

        // Si on a au moins un match, on crée une Action Card
        if (matches && matches.length > 0) {
          const topMatches = matches
            .sort((a: any, b: any) => a.total_proximity_score - b.total_proximity_score)
            .slice(0, 3); // On garde les 3 meilleurs

          recommendations.push({
            type: 'TRACTION',
            priority: matches.length >= 3 ? 3 : 2, // Priorité haute si beaucoup de choix
            title: `Opportunité : ${req.origin_city}`,
            target_id: req.id,
            content: {
              request: {
                id: req.id,
                origin: req.origin_city,
                destination: req.destination_city,
                date: req.desired_date,
                has_ai_scan: !!req.ai_recommendation,
                last_ai_date: req.ai_updated_at
              },
              matches_count: matches.length,
              top_trips: topMatches.map((m: any) => ({
                id: m.trip_id,
                departure: m.departure_city,
                arrival: m.arrival_city,
                time: m.departure_time,
                score: m.total_proximity_score,
                dist: m.origin_distance
              }))
            }
          });
        }
      } catch (err) {
        console.error(`[Marketing Scan] Failed to analyze request ${req.id}:`, err);
      }
    }

    // 4. Sauvegarder les cartes d'opportunités
    if (recommendations.length > 0) {
      const { error } = await supabase.from('dash_ai_recommendations').insert(recommendations);
      if (error) console.error("[Marketing Scan] Error inserting action cards:", error);
    }

    return recommendations.length;
  }
};
