import { createAdminClient } from "@/lib/supabase";

export const GlobalAIService = {
  /**
   * Scan stratégique analytique ultra-robuste
   */
  async runGlobalIntelligenceScan() {
    const supabase = createAdminClient();
    console.log("[Marketing Scan] Starting deep analytical scan...");

    // 1. Nettoyage immédiat et total des anciennes opportunités pour éviter les doublons/fantômes
    await supabase.from('dash_ai_recommendations').delete().eq('status', 'PENDING');

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // 2. Récupérer toutes les demandes NEW
    const { data: allRequests, error: reqError } = await supabase
      .from('site_trip_requests')
      .select('id, origin_city, destination_city, desired_date, ai_recommendation, ai_updated_at, origin_lat')
      .eq('status', 'NEW');

    if (reqError || !allRequests) return 0;

    // 3. Filtrer en JS pour garantir la correspondance exacte avec le tableau des Prospects
    const activeRequests = allRequests.filter(req => {
      // Garder uniquement si : a des coordonnées GPS ET (pas de date OU date >= aujourd'hui)
      const hasCoords = req.origin_lat !== null;
      const isFutureOrNull = !req.desired_date || new Date(req.desired_date) >= today;
      return hasCoords && isFutureOrNull;
    });

    console.log(`[Marketing Scan] Found ${activeRequests.length} active requests to analyze out of ${allRequests.length}.`);

    if (activeRequests.length === 0) return 0;

    const recommendations = [];

    // 4. Analyser chaque demande active
    for (const req of activeRequests) {
      try {
        const { data: matches, error: matchError } = await supabase.rpc('find_matching_trips', {
          p_request_id: req.id,
          p_radius_km: 15.0
        });

        if (matchError) continue;

        if (matches && matches.length > 0) {
          const topMatches = matches
            .sort((a: any, b: any) => a.total_proximity_score - b.total_proximity_score)
            .slice(0, 3);

          recommendations.push({
            type: 'TRACTION',
            priority: matches.length >= 3 ? 3 : 2,
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
        console.error(`[Marketing Scan] Error analyzing ${req.id}:`, err);
      }
    }

    // 5. Sauvegarder les nouvelles cartes
    if (recommendations.length > 0) {
      const { error: insertError } = await supabase.from('dash_ai_recommendations').insert(recommendations);
      if (insertError) console.error("[Marketing Scan] Insert error:", insertError);
    }

    return recommendations.length;
  }
};
