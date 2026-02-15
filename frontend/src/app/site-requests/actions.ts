"use server";

import { revalidatePath } from "next/cache";
import { 
  updateSiteTripRequest as updateRequest,
  getSiteTripRequests 
} from "@/lib/queries/site-requests";
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
    if (!forceRefresh) {
      const requests = await getSiteTripRequests({ limit: 100 });
      const current = requests.find(r => r.id === requestId);
      if (current?.ai_recommendation) {
        return { success: true, text: current.ai_recommendation, fromCache: true };
      }
    }

    // 2. Sinon, générer avec Gemini
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
      1. Trouve les 2-3 meilleurs conducteurs qui font un trajet similaire.
      2. Pour le meilleur match, rédige un message WhatsApp de traction ultra-convaincant.
      
      CONSIGNES POUR LE MESSAGE [MESSAGE] :
      - Invite explicitement le client à ouvrir l'application Klando.
      - Dis-lui de taper "${origin}" comme départ et "${destination}" comme destination.
      - Précise-lui de bien sélectionner la date du ${date || "correspondante"}.
      - Le message doit être court, chaleureux et donner envie de réserver immédiatement.
      
      IMPORTANT: Ta réponse DOIT impérativement suivre cette structure exacte pour que je puisse la traiter :
      
      [COMMENTAIRE]
      (Ton analyse, tes conseils et tes explications pour l'admin ici)
      
      [MESSAGE]
      (Uniquement le texte du message WhatsApp prêt à être copié-collé, sans préambule ni guillemets)
    `;

    const response = await askKlandoAI(prompt, { context: "Matching Traction" });

    // 3. Sauvegarder en DB
    await updateRequest(requestId, {
      ai_recommendation: response,
      ai_updated_at: new Date().toISOString()
    });

    // Note: We keep revalidatePath here because it's safer for server-side consistency,
    // but we will ensure the client handles it gracefully with useTransition and stable components.
    revalidatePath("/site-requests");
    
    return { success: true, text: response, fromCache: false };
  } catch (error: unknown) {
    console.error("AI Matching Error:", error);
    return { success: false, message: "Impossible de générer les recommandations." };
  }
}
