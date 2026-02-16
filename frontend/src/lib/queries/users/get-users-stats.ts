import { createServerClient } from "../../supabase";
import { UserStats } from "@/types/user";

/**
 * Statistiques globales des utilisateurs
 */
export async function getUsersStats(): Promise<UserStats> {
  const supabase = createServerClient();

  const { data, error } = await supabase
    .from("users")
    .select("uid, rating, is_driver_doc_validated, created_at");

  if (error) {
    console.error("getUsersStats error:", error);
    return {
      total_users: 0,
      verified_drivers: 0,
      avg_rating: 0,
      new_this_month: 0,
    };
  }

  type UserRow = {
    uid: string;
    rating: number | null;
    is_driver_doc_validated: boolean | null;
    created_at: string | null;
  };

  const users = (data || []) as UserRow[];
  const total = users.length;

  // Count verified drivers
  const verifiedDrivers = users.filter((u: UserRow) => u.is_driver_doc_validated === true).length;

  // Average rating (only users with rating)
  const usersWithRating = users.filter((u: UserRow) => u.rating !== null && u.rating > 0);
  const avgRating = usersWithRating.length > 0
    ? usersWithRating.reduce((sum: number, u: UserRow) => sum + (u.rating || 0), 0) / usersWithRating.length
    : 0;

  // New users this month
  const now = new Date();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
  const newThisMonth = users.filter((u: UserRow) => {
    if (!u.created_at) return false;
    return new Date(u.created_at) >= monthStart;
  }).length;

  return {
    total_users: total,
    verified_drivers: verifiedDrivers,
    avg_rating: Math.round(avgRating * 100) / 100,
    new_this_month: newThisMonth,
  };
}
