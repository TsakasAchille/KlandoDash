"use server";

import { getTripById } from "@/lib/queries/trips";

/**
 * Action serveur pour récupérer les détails complets d'un trajet
 */
export async function getTripDetailsAction(tripId: string) {
  try {
    const trip = await getTripById(tripId);
    if (!trip) return { success: false, error: "Trajet non trouvé" };
    return { success: true, data: trip };
  } catch (error) {
    console.error("Error in getTripDetailsAction:", error);
    return { success: false, error: "Erreur lors de la récupération du trajet" };
  }
}
