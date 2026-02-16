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

    // 2. Sinon, générer avec Gemini en utilisant la vue PUBLIC_PENDING_TRIPS
    if (!aiRecommendation) {
      // On utilise la vue spécifique au site public comme demandé
      const relevantTrips = await getPublicPendingTrips();

      const prompt = `
        Analyse cette demande client :
        De : ${origin}
        Vers : ${destination}
        Date souhaitée : ${date || "Dès que possible"}
        
        Voici les trajets actuellement disponibles sur le SITE PUBLIC :
        ${JSON.stringify(relevantTrips.map(t => ({
          id: t.id,
          from: t.departure_city,
          to: t.arrival_city,
          time: t.departure_time,
          seats: t.seats_available
        })))}
        
        TA MISSION :
        1. Trouve le MEILLEUR trajet qui correspond à la demande.
        2. Rédige un message WhatsApp de traction convaincant.
        
        CONSIGNES POUR LE MESSAGE [MESSAGE] :
        - Si match : "Bonne nouvelle ! Nous avons un départ de ${origin} vers ${destination}..."
        - Si pas de match : "Nous n'avons pas encore de départ confirmé pour ce trajet précis..."
        
        IMPORTANT: Ta réponse DOIT impérativement suivre cette structure exacte :
        
        [COMMENTAIRE]
        (Ton analyse : pourquoi ce trajet est un bon match ?)
        
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
