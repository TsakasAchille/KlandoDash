"use server";

import { askKlandoAI } from "@/lib/gemini";
import { getHomeSummary } from "@/lib/queries/stats";
import { getSiteTripRequests } from "@/lib/queries/site-requests";
import { getTrips } from "@/lib/queries/trips";
import { auth } from "@/lib/auth";

// Fonction utilitaire pour masquer les infos sensibles
function maskContact(contact: string) {
  if (!contact) return "N/A";
  if (contact.includes('@')) {
    const [part1, part2] = contact.split('@');
    return `${part1.substring(0, 3)}***@${part2}`;
  }
  return `${contact.substring(0, 4)}******`;
}

async function getDataContext() {
  const summary = await getHomeSummary();
  const siteRequests = await getSiteTripRequests({ limit: 20 });
  // Récupérer les 50 derniers trajets (incluant PENDING, ACTIVE, etc.)
  const allTrips = await getTrips({ limit: 50 });
  
  return {
    global_stats: {
      total_users: summary.users.total,
      new_users_month: summary.users.newThisMonth,
      active_trips: summary.trips.byStatus.find(s => s.status === 'ACTIVE')?.count || 0,
      pending_trips: summary.trips.byStatus.find(s => s.status === 'PENDING')?.count || 0,
      revenue_margin: summary.revenue.klandoMargin,
    },
    activity: {
      // Liste détaillée pour le matching
      trips: allTrips.map(t => ({
        id: t.trip_id,
        from: t.departure_name,
        to: t.destination_name,
        schedule: t.departure_schedule,
        status: t.status,
        seats: t.seats_available
      })),
      site_requests: siteRequests.map(r => ({
        from: r.origin_city,
        to: r.destination_city,
        contact: maskContact(r.contact_info),
        date: r.desired_date,
        status: r.status
      }))
    }
  };
}

export async function askGeminiAction(prompt: string) {
  const session = await auth();
  if (!session || session.user.role !== "admin") {
    throw new Error("Non autorisé");
  }

  try {
    const context = await getDataContext();
    const response = await askKlandoAI(prompt, context);
    return { success: true, text: response };
  } catch (error: any) {
    console.error("AI Action Error:", error);
    return { success: false, message: error.message || "Erreur lors de l'appel à l'IA" };
  }
}

export async function getAIInsightsAction() {
  const session = await auth();
  if (!session || session.user.role !== "admin") {
    throw new Error("Non autorisé");
  }

  try {
    const context = await getDataContext();
    const prompt = `
      En tant qu'expert business Klando, analyse ces données (trajets PENDING/ACTIVE et demandes site) et donne-moi EXACTEMENT 3 recommandations prioritaires pour augmenter la traction.
      
      FORMAT DE RÉPONSE (JSON UNIQUEMENT) :
      [
        { "title": "Titre court", "description": "Explication courte", "impact": "High/Medium", "type": "matching/growth/security" },
        ...
      ]
    `;

    const response = await askKlandoAI(prompt, context);
    const jsonStr = response.replace(/```json|```/g, "").trim();
    return { success: true, insights: JSON.parse(jsonStr) };
  } catch (error) {
    console.error("AI Insights Error:", error);
    return { success: false, insights: [] };
  }
}
