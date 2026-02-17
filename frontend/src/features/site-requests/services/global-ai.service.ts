import { createAdminClient } from "@/lib/supabase";
import { GeocodingService } from "./geocoding.service";
import { AIMatchingService } from "./ai-matching.service";

export const GlobalAIService = {
  /**
   * Scan global ultra-complet : calcule les km ET génère les recommandations IA 
   * pour chaque demande en attente.
   */
  async runGlobalIntelligenceScan() {
    const supabase = createAdminClient();
    console.log("[AI Global] Starting deep intelligence scan...");

    // 1. Récupérer les données
    const { data: requests } = await supabase.from('site_trip_requests').select('*').eq('status', 'NEW');
    const { data: trips } = await supabase.from('public_pending_trips').select('*');
    const { data: allUsers } = await supabase.from('users').select('*').limit(100);

    // 2. Nettoyer les anciennes reco PENDING
    await supabase.from('dash_ai_recommendations').delete().eq('status', 'PENDING');

    const recommendations = [];

    // MODULE 1 : TRACTION (Génération IA pour chaque demande)
    if (requests && requests.length > 0) {
      console.log(`[AI Global] Processing ${requests.length} requests with Gemini...`);
      
      for (const req of requests) {
        try {
          // A. Générer la recommandation IA complète
          const aiResult = await AIMatchingService.generateRecommendation(
            req.origin_city,
            req.destination_city,
            req.desired_date,
            { 
              lat: req.origin_lat!, 
              lng: req.origin_lng!, 
              destLat: req.destination_lat!, 
              destLng: req.destination_lng! 
            },
            trips || []
          );

          // B. Sauvegarder directement dans la demande client
          await supabase.from('site_trip_requests').update({
            ai_recommendation: aiResult,
            ai_updated_at: new Date().toISOString()
          }).eq('id', req.id);

          // C. Extraire le Trip ID pour le dashboard IA
          const tripIdMatch = aiResult.match(/\[TRIP_ID\][:\s]*([A-Za-z0-9-]+)/i);
          let bestTripId = null;
          if (tripIdMatch) bestTripId = tripIdMatch[1].trim();
          
          if (bestTripId && bestTripId.toUpperCase() !== 'NONE') {
            recommendations.push({
              type: 'TRACTION',
              priority: 2,
              title: `Prêt à envoyer : ${req.origin_city}`,
              target_id: req.id,
              content: {
                route: `${req.origin_city} -> ${req.destination_city}`,
                best_trip_id: bestTripId,
                status: "Analyse IA terminée"
              }
            });
          }
        } catch (err) {
          console.error(`[AI Global] Failed to process request ${req.id}:`, err);
        }
      }
    }

    // MODULE 2 : QUALITÉ & VALIDATION
    const pendingValidation = (allUsers || []).filter(u => u.role === 'driver' && !u.is_driver_doc_validated);
    for (const driver of pendingValidation.slice(0, 5)) {
        recommendations.push({
            type: 'QUALITY',
            priority: 1,
            title: `Chauffeur à certifier : ${driver.display_name}`,
            target_id: driver.uid,
            content: {
                name: driver.display_name,
                alert: "Documents en attente de vérification."
            }
        });
    }

    // 3. Sauvegarder les fiches de dashboard
    if (recommendations.length > 0) {
      const { error } = await supabase.from('dash_ai_recommendations').insert(recommendations);
      if (error) console.error("[AI Global] Error inserting dashboard cards:", error);
    }

    return recommendations.length;
  }
};
