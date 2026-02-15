"use server";

import { askKlandoAI } from "@/lib/gemini";
import { getHomeSummary } from "@/lib/queries/stats";
import { getSiteTripRequests } from "@/lib/queries/site-requests";
import { auth } from "@/lib/auth";

export async function askGeminiAction(prompt: string) {
  const session = await auth();
  if (!session || session.user.role !== "admin") {
    throw new Error("Non autorisé");
  }

  try {
    // Collecter un contexte riche mais optimisé pour Gemini
    const summary = await getHomeSummary();
    const siteRequests = await getSiteTripRequests({ limit: 10 });
    
    const context = {
      global_stats: {
        total_users: summary.users.total,
        new_users_month: summary.users.newThisMonth,
        active_trips: summary.trips.byStatus.find(s => s.status === 'ACTIVE')?.count || 0,
        revenue_margin: summary.revenue.klandoMargin,
      },
      recent_activity: {
        trips: summary.recentTrips.map(t => ({
          from: t.departure_city,
          to: t.destination_city,
          driver: t.driver_name,
          status: t.status
        })),
        site_requests: siteRequests.map(r => ({
          from: r.origin_city,
          to: r.destination_city,
          contact: r.contact_info,
          status: r.status
        }))
      }
    };

    const response = await askKlandoAI(prompt, context);
    return { success: true, text: response };
  } catch (error: any) {
    console.error("AI Action Error:", error);
    return { success: false, message: error.message || "Erreur lors de l'appel à l'IA" };
  }
}
