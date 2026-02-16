import { createServerClient } from "../../supabase";
import { UserStats } from "@/types/user";

/**
 * Statistiques globales des utilisateurs (Optimisé via RPC)
 */
export async function getUsersStats(): Promise<UserStats> {
  const supabase = createServerClient();

  const { data, error } = await supabase.rpc("get_klando_stats_final");

  if (error) {
    console.error("getUsersStats error:", error);
    return {
      total_users: 0,
      verified_drivers: 0,
      avg_rating: 0,
      new_this_month: 0,
    };
  }

  // Note: avg_rating_val doit être ajouté à la fonction SQL si pas déjà présent
  return {
    total_users: data.users.total,
    verified_drivers: data.users.verifiedDrivers,
    avg_rating: data.users.avgRating || 0,
    new_this_month: data.users.newThisMonth,
  };
}
