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
import { GeocodingService } from "@/features/site-requests/services/geocoding.service";
import { TripService } from "@/features/site-requests/services/trip.service";
import { AIMatchingService } from "@/features/site-requests/services/ai-matching.service";

export async function updateRequestStatusAction(id: string, status: SiteTripRequestStatus) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const success = await updateRequest(id, { status });
  if (success) {
    revalidatePath("/site-requests");
    revalidatePath("/marketing");
  }
  return { success };
}

export async function calculateAndSaveRequestRouteAction(requestId: string, originCity: string, destCity: string) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  try {
    const [originCoords, destCoords] = await Promise.all([
      GeocodingService.getCoordinates(originCity),
      GeocodingService.getCoordinates(destCity)
    ]);
    if (!originCoords || !destCoords) return { success: false, message: "Coordonnées introuvables." };

    const route = await GeocodingService.getRoute(originCoords, destCoords);
    if (!route) return { success: false, message: "Itinéraire non trouvé." };

    const geometry = {
      polyline: route.polyline,
      origin_lat: originCoords.lat,
      origin_lng: originCoords.lng,
      destination_lat: destCoords.lat,
      destination_lng: destCoords.lng
    };

    const success = await updateRequest(requestId, geometry);
    if (success) revalidatePath("/marketing");
    return { success, data: geometry };
  } catch (error) {
    return { success: false, message: "Erreur serveur." };
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
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  try {
    const { createAdminClient } = await import("@/lib/supabase");
    const supabase = createAdminClient();
    
    const { data: requestData } = await supabase
      .from("site_trip_requests")
      .select("origin_lat, origin_lng, destination_lat, destination_lng, ai_recommendation")
      .eq("id", requestId)
      .single();

    if (!requestData) throw new Error("Demande introuvable");

    let aiRecommendation = requestData.ai_recommendation;
    
    if (!aiRecommendation || forceRefresh) {
      // On utilise la fonction de scan locale (SQL RPC) pour ne donner à l'IA que des trajets pertinents
      const { findMatchingTrips } = await import("@/lib/queries/site-requests");
      const matches = await findMatchingTrips(requestId, 15); // Rayon de 15km max (départ ET arrivée)
      
      const relevantTrips = matches.map(m => ({
        id: m.trip_id,
        departure_city: m.departure_city,
        arrival_city: m.arrival_city,
        departure_time: m.departure_time,
        seats_available: Number(m.seats_available),
        // On injecte les distances déjà calculées par le SQL pour éviter les recalculs lents
        origin_dist: m.origin_distance,
        dest_dist: m.destination_distance
      }));

      aiRecommendation = await AIMatchingService.generateRecommendation(
        origin, destination, date, 
        { 
          lat: requestData.origin_lat!, 
          lng: requestData.origin_lng!, 
          destLat: requestData.destination_lat!, 
          destLng: requestData.destination_lng! 
        },
        relevantTrips
      );

      await updateRequest(requestId, { 
        ai_recommendation: aiRecommendation, 
        ai_updated_at: new Date().toISOString() 
      });
      revalidatePath("/site-requests");
      revalidatePath("/marketing");
    }

    // EXTRACTION ROBUSTE DE L'ID
    let tripId = null;
    const tripIdMatch = aiRecommendation.match(/\[TRIP_ID\][:\s]*([A-Za-z0-9-]+)/i);
    if (tripIdMatch) {
      tripId = tripIdMatch[1].trim();
    } else {
      // Fallback : recherche libre de TRIP-XXXX dans tout le texte
      const globalMatch = aiRecommendation.match(/TRIP-[A-Za-z0-9-]+/);
      if (globalMatch) tripId = globalMatch[0].trim();
    }

    let matchedTripData = null;
    if (tripId && tripId.toUpperCase() !== 'NONE') {
      console.log(`[getAIMatchingAction] Fetching details for: ${tripId}`);
      const trip = await TripService.getById(tripId);
      
      if (trip) {
        matchedTripData = {
          id: trip.trip_id,
          departure_city: trip.departure_name || "",
          arrival_city: trip.destination_name || "",
          departure_time: trip.departure_schedule || "",
          seats_available: trip.seats_available || 0,
          polyline: trip.polyline,
          departure_latitude: trip.departure_latitude,
          departure_longitude: trip.departure_longitude,
          destination_latitude: trip.destination_latitude,
          destination_longitude: trip.destination_longitude,
          origin_dist: GeocodingService.calculateDistance(
            { lat: requestData.origin_lat!, lng: requestData.origin_lng! },
            { lat: trip.departure_latitude!, lng: trip.departure_longitude! }
          ),
          dest_dist: GeocodingService.calculateDistance(
            { lat: requestData.destination_lat!, lng: requestData.destination_lng! },
            { lat: trip.destination_latitude!, lng: trip.destination_longitude! }
          )
        };
      }
    }
    
    return { success: true, text: aiRecommendation, matchedTrip: matchedTripData };
  } catch (error) {
    console.error("AI Matching Error:", error);
    return { success: false, message: "Erreur lors du matching IA." };
  }
}

export async function scanRequestMatchesAction(requestId: string, radiusKm: number = 5) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  try {
    const supabase = (await import("@/lib/supabase")).createAdminClient();
    const { findMatchingTrips } = await import("@/lib/queries/site-requests");

    const { data: req } = await supabase.from("site_trip_requests").select("*").eq("id", requestId).single();
    if (!req) throw new Error("Introuvable");

    let coords = { origin_lat: req.origin_lat, origin_lng: req.origin_lng, destination_lat: req.destination_lat, destination_lng: req.destination_lng };
    if (!coords.origin_lat) {
      const res = await calculateAndSaveRequestRouteAction(requestId, req.origin_city, req.destination_city);
      if (res.success && res.data) coords = res.data;
    }

    const matches = await findMatchingTrips(requestId, radiusKm);
    await supabase.from("site_trip_request_matches").delete().eq("request_id", requestId);
    if (matches.length > 0) {
      await supabase.from("site_trip_request_matches").insert(
        (matches as any[]).map((m) => ({
          request_id: requestId,
          trip_id: m.trip_id,
          proximity_score: m.total_proximity_score,
          origin_distance: m.origin_distance,
          destination_distance: m.destination_distance
        }))
      );
    }
    revalidatePath("/site-requests");
    revalidatePath("/marketing");
    return { success: true, count: matches.length };
  } catch (error) {
    return { success: false };
  }
}

export async function getMarketingSiteRequestsAction(options: { 
  limit?: number; 
  status?: SiteTripRequestStatus | 'ALL' 
} = {}) {
  const session = await auth();
  if (!session) return { success: false, data: [] };
  
  const requests = await getSiteTripRequests({ 
    limit: options.limit || 1000, 
    status: options.status,
    hidePast: false 
  });
  return { success: true, data: requests };
}
