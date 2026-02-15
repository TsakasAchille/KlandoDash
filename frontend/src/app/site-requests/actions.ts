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
      2. S'il y a des correspondances : rédige un message WhatsApp de traction ultra-convaincant.
      3. S'il n'y a AUCUNE correspondance pertinente : rédige un message poli expliquant qu'aucun trajet n'est disponible pour le moment mais que nous gardons sa demande et reviendrons vers lui dès qu'un chauffeur se manifeste.
      
      CONSIGNES POUR LE MESSAGE [MESSAGE] :
      - Si match : Invite explicitement le client à ouvrir l'application Klando, à taper "${origin}" et "${destination}" pour la date du ${date || "choisie"}.
      - Si pas de match : Dis-lui que nous n'avons pas encore de départ confirmé pour ce trajet précis, mais que nous l'informerons dès qu'une place se libère.
      - Le message doit être court, chaleureux et professionnel.
      
      IMPORTANT: Ta réponse DOIT impérativement suivre cette structure exacte :
      
      [COMMENTAIRE]
      (Ton analyse pour l'admin ici)
      
      [TRIP_ID]
      (L'ID du trajet du MEILLEUR match uniquement, ex: TRIP-12345. Si aucun match, laisse cette section vide ou écris NONE)
      
      [MESSAGE]
      (Le texte du message WhatsApp prêt à être envoyé)
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
