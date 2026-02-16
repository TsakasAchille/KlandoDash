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
    return { success: true };
  }
  return { success: false };
}

/**
 * Calcule l'itinéraire et les coordonnées côté serveur
 * avec une stratégie d'affinage par IA pour les points d'intérêt locaux.
 */
export async function calculateAndSaveRequestRouteAction(requestId: string, originCity: string, destCity: string) {
  try {
    console.log(`[Geocoding] Searching: ${originCity} -> ${destCity}`);

    const geocodeWithRefinement = async (rawAddress: string) => {
      // 1. Tentative brute avec Nominatim
      const fetchCoords = async (query: string) => {
        const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query + ", Senegal")}&limit=1`, {
          headers: { 'User-Agent': 'KlandoDash-Admin' }
        });
        const data = await res.json();
        return (data && data[0]) ? [parseFloat(data[0].lat), parseFloat(data[0].lon)] as [number, number] : null;
      };

      let coords = await fetchCoords(rawAddress);

      // 2. Si échec, on demande à l'IA de nettoyer l'adresse (extraire quartier/ville)
      if (!coords) {
        console.log(`[Geocoding] Nominatim failed for "${rawAddress}", refining with AI...`);
        const prompt = `Quel est le quartier et la ville correspondant à ce lieu au Sénégal : "${rawAddress}" ? Réponds UNIQUEMENT sous la forme "Quartier, Ville".`;
        const refined = await askKlandoAI(prompt, { context: "Geocoding Refinement" });
        
        if (refined && !refined.includes("Error")) {
          console.log(`[Geocoding] AI refined "${rawAddress}" to "${refined}"`);
          coords = await fetchCoords(refined);
        }
      }

      return coords;
    };

    const [originCoords, destCoords] = await Promise.all([
      geocodeWithRefinement(originCity),
      geocodeWithRefinement(destCity)
    ]);

    if (!originCoords || !destCoords) {
      return { success: false, message: "Coordonnées introuvables même après affinage." };
    }

    const routeRes = await fetch(`https://router.project-osrm.org/route/v1/driving/${originCoords[1]},${originCoords[0]};${destCoords[1]},${destCoords[0]}?overview=full`);
    const routeData = await routeRes.json();
    
    if (!routeData.routes || !routeData.routes[0]) {
      return { success: false, message: "Itinéraire non trouvé entre ces points." };
    }

    const geometry = {
      polyline: routeData.routes[0].geometry,
      origin_lat: originCoords[0],
      origin_lng: originCoords[1],
      destination_lat: destCoords[0],
      destination_lng: destCoords[1]
    };

    // Sauvegarde immédiate
    const saveResult = await saveRequestGeometryAction(requestId, geometry);

    if (!saveResult.success) {
      return { success: false, message: "Échec de la sauvegarde GPS." };
    }

    return { success: true, data: geometry };
  } catch (error) {
    console.error(`[Geocoding Error] ${requestId}:`, error);
    return { success: false, message: "Erreur serveur lors du calcul géographique." };
  }
}

/**
 * SCANNER : Calcule les trajets proches et les enregistre de manière persistante
 */
export async function scanRequestMatchesAction(requestId: string, radiusKm: number = 5) {
  const session = await auth();
  if (!session || session.user.role !== "admin") {
    throw new Error("Non autorisé");
  }

  try {
    const supabase = (await import("@/lib/supabase")).createAdminClient();
    const { findMatchingTrips } = await import("@/lib/queries/site-requests");

    // 0. Récupérer la demande
    const { data: requestData } = await supabase
      .from("site_trip_requests")
      .select("origin_city, destination_city, origin_lat, origin_lng, destination_lat, destination_lng")
      .eq("id", requestId)
      .single();

    if (!requestData) throw new Error("Demande introuvable");

    // 1. AUTO-GÉOCODAGE si nécessaire
    let coords = {
      origin_lat: requestData.origin_lat,
      origin_lng: requestData.origin_lng,
      destination_lat: requestData.destination_lat,
      destination_lng: requestData.destination_lng
    };

    if (!coords.origin_lat || !coords.destination_lat) {
      console.log(`[Scanner] Coords missing for ${requestId}, geocoding...`);
      const routeResult = await calculateAndSaveRequestRouteAction(
        requestId, 
        requestData.origin_city, 
        requestData.destination_city
      );
      
      if (routeResult.success && routeResult.data) {
        coords = {
          origin_lat: routeResult.data.origin_lat,
          origin_lng: routeResult.data.origin_lng,
          destination_lat: routeResult.data.destination_lat,
          destination_lng: routeResult.data.destination_lng
        };
      } else {
        return { 
          success: false, 
          message: "Impossible de géocoder les villes de départ ou d'arrivée." 
        };
      }
    }

    // 2. Rechercher les trajets correspondants (RPC SQL Haversine)
    const matches = await findMatchingTrips(requestId, radiusKm);
    
    // 3. Diagnostic: Nombre de trajets PENDING au total
    const { count: totalPending } = await supabase
      .from("trips")
      .select("*", { count: "exact", head: true })
      .eq("status", "PENDING")
      .gt("departure_schedule", new Date().toISOString());

    // 4. Nettoyer et Insérer les matches
    await supabase.from("site_trip_request_matches").delete().eq("request_id", requestId);

    if (matches.length > 0) {
      await supabase.from("site_trip_request_matches").insert(
        matches.map((m: any) => ({
          request_id: requestId,
          trip_id: m.trip_id,
          proximity_score: m.total_proximity_score,
          origin_distance: m.origin_distance,
          destination_distance: m.destination_distance
        }))
      );
    }

    revalidatePath("/site-requests");
    revalidatePath("/map");

    return { 
      success: true, 
      count: matches.length, 
      diagnostics: {
        id: requestId,
        hasCoords: true,
        origin: requestData.origin_city,
        destination: requestData.destination_city,
        totalPending: totalPending || 0,
        radiusUsed: radiusKm
      },
      message: `${matches.length} trajet(s) trouvé(s) et enregistré(s).` 
    };
  } catch (error) {
    console.error("[Scanner Error] Failed to scan matches:", error);
    return { success: false, message: "Erreur lors du scan des trajets." };
  }
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

    // 2. Sinon, générer avec Gemini en utilisant les matches déjà présents en DB (Scanner) ou le matching géo en direct
    if (!aiRecommendation) {
      const relevantTrips = await getPublicPendingTrips();
      
      // Récupérer les matches persistants du scanner pour cette demande
      const { data: dbMatches } = await supabase
        .from("site_trip_request_matches")
        .select("trip_id, origin_distance, destination_distance")
        .eq("request_id", requestId);

      const hasDbMatches = dbMatches && dbMatches.length > 0;
      let matchingContext = "";

      if (hasDbMatches) {
        // On utilise les résultats précis du scanner (Déjà calculés en SQL Haversine)
        console.log(`[AI Matching] Using ${dbMatches.length} persistent matches from DB`);
        matchingContext = `RÉSULTATS DU SCANNER (PRÉ-CALCULÉS) :\n${JSON.stringify(dbMatches)}`;
      } else {
        // Fallback: Matching géo multi-rayons en direct (plus lent)
        console.log(`[AI Matching] No persistent matches, running live proximity scan`);
        const { findMatchingTrips } = await import("@/lib/queries/site-requests");
        const [match2km, match5km, match10km, match15km] = await Promise.all([
          findMatchingTrips(requestId, 2),
          findMatchingTrips(requestId, 5),
          findMatchingTrips(requestId, 10),
          findMatchingTrips(requestId, 15),
        ]);
        matchingContext = `
          RÉSULTATS DU MATCHING GÉOGRAPHIQUE EN DIRECT :
          - À moins de 2km : ${match2km.length > 0 ? JSON.stringify(match2km) : "Aucun"}
          - À moins de 5km : ${match5km.length > 0 ? JSON.stringify(match5km) : "Aucun"}
          - À moins de 10km : ${match10km.length > 0 ? JSON.stringify(match10km) : "Aucun"}
          - À moins de 15km : ${match15km.length > 0 ? JSON.stringify(match15km) : "Aucun"}
        `;
      }

      const prompt = `
        Analyse cette demande client :
        De : ${origin}
        Vers : ${destination}
        Date souhaitée : ${date || "Dès que possible"}
        
        ${matchingContext}

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
        (Le texte du message WhatsApp court et direct)

        [EMAIL]
        (Un email professionnel et chaleureux proposant la solution au client)
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
