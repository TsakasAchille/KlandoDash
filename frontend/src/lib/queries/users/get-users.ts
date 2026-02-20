import { createServerClient } from "../../supabase";
import { UserListItem } from "@/types/user";

/**
 * Liste des utilisateurs avec pagination et filtres avancés
 */
export async function getUsers(
  page = 1, 
  pageSize = 20, 
  filters: {
    role?: string;
    verified?: string;
    gender?: string;
    minRating?: number;
    search?: string;
    isNew?: boolean;
  } = {}
): Promise<{ users: UserListItem[], totalCount: number }> {
  const supabase = createServerClient();
  const from = (page - 1) * pageSize;
  const to = from + pageSize - 1;

  let query = supabase
    .from("users")
    .select(`
      uid,
      display_name,
      email,
      phone_number,
      photo_url,
      rating,
      rating_count,
      role,
      gender,
      is_driver_doc_validated,
      created_at
    `, { count: "exact" });

  // Filtre par Rôle (colonne 'role')
  if (filters.role && filters.role !== "all") {
    query = query.eq("role", filters.role);
  }

  // Filtre par Vérification (colonne 'is_driver_doc_validated')
  if (filters.verified === "true") {
    query = query.eq("is_driver_doc_validated", true);
  } else if (filters.verified === "false") {
    query = query.eq("is_driver_doc_validated", false);
  } else if (filters.verified === "pending") {
    // Membres non validés possédant au moins un document
    query = query
      .eq("is_driver_doc_validated", false)
      .or("id_card_url.not.is.null,driver_license_url.not.is.null");
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

  const { data, error, count } = await query
    .order("created_at", { ascending: false })
    .range(from, to);

  if (error) {
    console.error("getUsers error:", error);
    return { users: [], totalCount: 0 };
  }

  return { 
    users: data as UserListItem[], 
    totalCount: count || 0 
  };
}
