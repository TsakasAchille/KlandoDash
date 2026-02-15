"use server";

import { revalidatePath } from "next/cache";
import { updateSiteTripRequest as updateRequest } from "@/lib/queries/site-requests";
import { SiteTripRequestStatus } from "@/types/site-request";
import { getTrips } from "@/lib/queries/trips";
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

export async function getAIMatchingAction(requestId: string, origin: string, destination: string, date: string | null) {
  const session = await auth();
  if (!session || session.user.role !== "admin") {
    throw new Error("Non autorisé");
  }

  try {
    // Récupérer les trajets futurs (PENDING ou ACTIVE)
    const futureTrips = await getTrips({ limit: 50 });
    const relevantTrips = futureTrips.filter(t => t.status === 'ACTIVE' || t.status === 'PENDING');

    const prompt = `
      Analyse cette demande client :
      De : ${origin}
      Vers : ${destination}
      Date souhaitée : ${date || "Dès que possible"}
      
      Voici les trajets disponibles dans notre base :
      ${JSON.stringify(relevantTrips)}
      
      TA MISSION :
      1. Trouve les 2-3 meilleurs conducteurs qui font un trajet similaire (même villes ou villes proches).
      2. Pour le meilleur match, rédige un message WhatsApp de traction ultra-convaincant en français.
      3. Le message doit être chaleureux, pro et inciter à la réservation immédiate.
      
      Formatte ta réponse en Markdown avec des sections claires.
    `;

    const response = await askKlandoAI(prompt, { context: "Matching Traction" });
    return { success: true, text: response };
  } catch (error: any) {
    console.error("AI Matching Error:", error);
    return { success: false, message: "Impossible de générer les recommandations." };
  }
}
