import { createServerClient } from "../supabase";
import { UserListItem, UserDetail, UserStats } from "@/types/user";

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
      bio,
      birth,
      is_driver_doc_validated,
      driver_license_url,
      id_card_url,
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

/**
 * Détail d'un utilisateur avec stats
 */
export async function getUserById(uid: string): Promise<UserDetail | null> {
  const supabase = createServerClient();

  // Fetch user details
  const { data: user, error: userError } = await supabase
    .from("users")
    .select(`
      uid,
      display_name,
      email,
      first_name,
      name,
      phone_number,
      birth,
      photo_url,
      bio,
      gender,
      rating,
      rating_count,
      role,
      driver_license_url,
      id_card_url,
      is_driver_doc_validated,
      created_at,
      updated_at
    `)
    .eq("uid", uid)
    .single();

  if (userError) {
    console.error("getUserById error:", userError);
    return null;
  }

  // Count trips as driver
  const { count: driverCount } = await supabase
    .from("trips")
    .select("*", { count: "exact", head: true })
    .eq("driver_id", uid);

  // Count trips as passenger (via bookings)
  const { count: passengerCount } = await supabase
    .from("bookings")
    .select("*", { count: "exact", head: true })
    .eq("user_id", uid);

  return {
    ...user,
    trips_as_driver: driverCount || 0,
    trips_as_passenger: passengerCount || 0,
  } as UserDetail;
}

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

/**
 * Valide ou invalide les documents d'un conducteur
 */
export async function validateUser(uid: string, isValidated: boolean): Promise<boolean> {
  const supabase = createServerClient();

  const { error } = await supabase
    .from("users")
    .update({ 
      is_driver_doc_validated: isValidated,
      updated_at: new Date().toISOString()
    })
    .eq("uid", uid);

  if (error) {
    console.error("validateUser error:", error);
    return false;
  }

  return true;
}
