"use server";

import { revalidatePath } from "next/cache";
import { 
  updateSiteTripRequest as updateRequest,
  getSiteTripRequests,
  getPublicPendingTrips
} from "@/lib/queries/site-requests";
import { SiteTripRequestStatus } from "@/types/site-request";
import { askKlandoAI } from "@/lib/gemini";
import { auth } from "@/lib/auth";

export async function updateRequestStatusAction(id: string, status: SiteTripRequestStatus) {
  const success = await updateRequest(id, { status });

  if (success) {
    revalidatePath("/site-requests");
    return { success: true, message: "Statut mis à jour." };
  }

  return { success: false, message: "Erreur lors de la mise à jour." };
}

export async function saveRequestGeometryAction(
  id: string, 
  data: { 
    polyline: string; 
    origin_lat: number; 
    origin_lng: number;
    destination_lat: number;
    destination_lng: number;
  }
) {
  const success = await updateRequest(id, data);
  if (success) {
    // On ne revalide pas forcément tout de suite pour éviter les flashs UI pendant le calcul en arrière-plan
    return { success: true };
  }
  return { success: false };
}

export async function getAIMatchingAction(
  requestId: string, 
  origin: string, 
  destination: string, 
  date: string | null,
  forceRefresh = false
) {
  const session = await auth();
  if (!session || session.user.role !== "admin") {
    throw new Error("Non autorisé");
  }

  try {
    // 1. Vérifier si on a déjà une recommandation (si pas forceRefresh)
    let aiRecommendation = null;
    if (!forceRefresh) {
      const requests = await getSiteTripRequests({ limit: 100 });
      const current = requests.find(r => r.id === requestId);
      if (current?.ai_recommendation) {
        aiRecommendation = current.ai_recommendation;
      }
    }

    // 2. Sinon, générer avec Gemini en utilisant la vue PUBLIC_PENDING_TRIPS et le matching géo
    if (!aiRecommendation) {
      // On utilise la vue spécifique au site public comme demandé
      const relevantTrips = await getPublicPendingTrips();
      
      // Nouvelle logique: Matching géo multi-rayons (2km, 5km, 10km, 15km)
      const { findMatchingTrips } = await import("@/lib/queries/site-requests");
      const [match2km, match5km, match10km, match15km] = await Promise.all([
        findMatchingTrips(requestId, 2),
        findMatchingTrips(requestId, 5),
        findMatchingTrips(requestId, 10),
        findMatchingTrips(requestId, 15),
      ]);

      const prompt = `
        Analyse cette demande client :
        De : ${origin}
        Vers : ${destination}
        Date souhaitée : ${date || "Dès que possible"}
        
        RÉSULTATS DU MATCHING GÉOGRAPHIQUE :
        - À moins de 2km : ${match2km.length > 0 ? JSON.stringify(match2km) : "Aucun"}
        - À moins de 5km : ${match5km.length > 0 ? JSON.stringify(match5km) : "Aucun"}
        - À moins de 10km : ${match10km.length > 0 ? JSON.stringify(match10km) : "Aucun"}
        - À moins de 15km : ${match15km.length > 0 ? JSON.stringify(match15km) : "Aucun"}

        Voici également TOUS les trajets actuellement visibles sur le SITE PUBLIC :
        ${JSON.stringify(relevantTrips.map(t => ({
          id: t.id,
          from: t.departure_city,
          to: t.arrival_city,
          time: t.departure_time,
          seats: t.seats_available
        })))}
        
        TA MISSION :
        1. Trouve le MEILLEUR trajet qui correspond à la demande (priorise les résultats du MATCHING GÉOGRAPHIQUE s'ils existent).
        2. Rédige un message WhatsApp de traction convaincant.
        
        CONSIGNES POUR LE MESSAGE [MESSAGE] :
        - Si match géo proche (2-5km) : "Bonne nouvelle ! Nous avons un départ juste à côté de chez vous..."
        - Si match géo moyen (10-15km) : "Bonne nouvelle ! Nous avons un départ à proximité de ${origin}..."
        - Si match ville uniquement : "Bonne nouvelle ! Nous avons un départ de ${origin} vers ${destination}..."
        - Si pas de match : "Nous n'avons pas encore de départ confirmé pour ce trajet précis..."
        
        IMPORTANT: Ta réponse DOIT impérativement suivre cette structure exacte :
        
        [COMMENTAIRE]
        (Ton analyse : pourquoi ce trajet est un bon match ? Mentionne la distance si c'est un match géo)
        
        [TRIP_ID]
        (L'ID du trajet choisi parmi la liste fournie ci-dessus. Si aucun match, écris NONE)
        
        [MESSAGE]
        (Le texte du message WhatsApp prêt à être envoyé)
      `;

      aiRecommendation = await askKlandoAI(prompt, { context: "Matching Traction Site" });

      // Sauvegarder en DB
      await updateRequest(requestId, {
        ai_recommendation: aiRecommendation,
        ai_updated_at: new Date().toISOString()
      });
      
      revalidatePath("/site-requests");
    }

    // 3. Extraire le TRIP_ID pour renvoyer les détails complets (notamment la polyline)
    let matchedTripData = null;
    
    const tripIdMatch = aiRecommendation.match(/\[TRIP_ID\][:\s]*([A-Z0-9-]+)/i);
    let tripId = tripIdMatch?.[1]?.trim()?.toUpperCase();
    
    if (!tripId || tripId === 'NONE') {
      const fallbackMatch = aiRecommendation.match(/TRIP-[A-Z0-9]+/i);
      if (fallbackMatch) {
        tripId = fallbackMatch[0].toUpperCase().trim();
      }
    }

    const finalTripId = tripId && tripId !== 'NONE' && tripId !== '' ? tripId : null;

    if (finalTripId) {
      console.log(`[AI Matching] Searching details for ID: ${finalTripId}`);
      const { getTripById } = await import("@/lib/queries/trips");
      
      let trip = await getTripById(finalTripId);
      if (!trip && finalTripId.startsWith('TRIP-')) {
        trip = await getTripById(finalTripId.replace('TRIP-', ''));
      }

      if (trip) {
        matchedTripData = {
          id: trip.trip_id,
          departure_city: trip.departure_name,
          arrival_city: trip.destination_name,
          departure_time: trip.departure_schedule,
          seats_available: trip.seats_available,
          polyline: trip.polyline
        };
      }
    }
    
    return { 
      success: true, 
      text: aiRecommendation, 
      matchedTrip: matchedTripData,
      fromCache: !forceRefresh 
    };
  } catch (error: unknown) {
    console.error("AI Matching Error:", error);
    return { success: false, message: "Impossible de générer les recommandations." };
  }
}
