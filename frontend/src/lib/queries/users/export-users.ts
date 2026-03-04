import { createServerClient } from "../../supabase";
import { UserListItem } from "@/types/user";

/**
 * Fetch a limited number of users for export with filters
 */
export async function getExportUsers(
  limit: number = 100, 
  filters: {
    role?: string;
    verified?: string;
    gender?: string;
    minRating?: number;
    search?: string;
    isNew?: boolean;
  } = {}
): Promise<UserListItem[]> {
  const supabase = createServerClient();

  let query = supabase
    .from("users")
    .select(`
      uid,
      display_name,
      first_name,
      name,
      email,
      phone_number,
      rating,
      role,
      gender,
      is_driver_doc_validated,
      created_at,
      id_card_number,
      driver_license_number
    `)
    .limit(limit);

  // Filtre par Rôle (colonne 'role')
  if (filters.role && filters.role !== "all") {
    query = query.eq("role", filters.role);
  }

  // Filtre par Vérification
  if (filters.verified === "true") {
    query = query.eq("is_driver_doc_validated", true);
  } else if (filters.verified === "false") {
    query = query.eq("is_driver_doc_validated", false);
  }

  // Filter: Gender
  if (filters.gender && filters.gender !== "all") {
    query = query.eq("gender", filters.gender);
  }

  // Filter: Min Rating
  if (filters.minRating && filters.minRating > 0) {
    query = query.gte("rating", filters.minRating);
  }

  // Filter: New Members (last 30 days)
  if (filters.isNew) {
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    query = query.gte("created_at", thirtyDaysAgo.toISOString());
  }

  // Search
  if (filters.search) {
    query = query.or(`display_name.ilike.%${filters.search}%,email.ilike.%${filters.search}%,phone_number.ilike.%${filters.search}%`);
  }

  const { data, error } = await query.order("created_at", { ascending: false });

  if (error) {
    console.error("getExportUsers error:", error);
    return [];
  }

  return data as UserListItem[];
}
