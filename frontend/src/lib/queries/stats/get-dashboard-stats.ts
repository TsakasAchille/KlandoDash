import { createServerClient } from "../../supabase";
import { DashboardStats } from "./types";

/**
 * Récupère les statistiques globales du tableau de bord.
 * Version optimisée utilisant une fonction RPC pour éviter de charger toutes les lignes en mémoire.
 */
export async function getDashboardStats(): Promise<DashboardStats> {
  const supabase = createServerClient();

  const { data, error } = await supabase.rpc("get_klando_stats_final");

  if (error) {
    console.error("getDashboardStats error:", error);
    // Fallback minimaliste en cas d'erreur RPC (si la fonction n'est pas encore déployée)
    return {
      trips: { total: 0, byStatus: [], totalDistance: 0, totalSeatsBooked: 0 },
      users: { total: 0, verifiedDrivers: 0, newThisMonth: 0, demographics: { gender: [], age: [] }, typicalProfile: { gender: "Inconnu", ageGroup: "Inconnu" } },
      bookings: { total: 0 },
      transactions: { total: 0, totalAmount: 0, byStatus: [], byType: [] },
      revenue: { totalPassengerPaid: 0, totalDriverPrice: 0, klandoMargin: 0, transactionCount: 0 },
      cashFlow: { totalIn: 0, totalOut: 0, solde: 0, countIn: 0, countOut: 0 }
    };
  }

  return data as DashboardStats;
}
