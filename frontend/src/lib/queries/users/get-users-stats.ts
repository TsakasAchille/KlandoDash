import { createServerClient } from "../../supabase";
import { UserStats } from "@/types/user";

/**
 * Statistiques globales des utilisateurs (Version Allégée et Rapide)
 */
export async function getUsersStats(): Promise<UserStats> {
  const supabase = createServerClient();

  // On lance les comptages en parallèle pour aller plus vite
  const [totalRes, verifiedRes, avgRes, newRes] = await Promise.all([
    supabase.from("users").select("*", { count: "exact", head: true }),
    supabase.from("users").select("*", { count: "exact", head: true }).eq("is_driver_doc_validated", true),
    supabase.from("users").select("rating").gt("rating", 0),
    supabase.from("users").select("*", { count: "exact", head: true }).gte("created_at", new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString())
  ]);

  const total = totalRes.count || 0;
  const verified = verifiedRes.count || 0;
  const newThisMonth = newRes.count || 0;
  
  // Calcul manuel de la moyenne pour éviter un RPC
  const ratings = avgRes.data || [];
  const avg = ratings.length > 0 
    ? ratings.reduce((acc, curr) => acc + (Number(curr.rating) || 0), 0) / ratings.length 
    : 0;

  return {
    total_users: total,
    verified_drivers: verified,
    avg_rating: avg,
    new_this_month: newThisMonth,
  };
}
