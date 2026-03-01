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
      first_name,
      name,
      email,
      phone_number,
      photo_url,
      rating,
      rating_count,
      role,
      gender,
      is_driver_doc_validated,
      created_at,
      id_card_url,
      driver_license_url,
      id_card_number,
      id_card_name_ai,
      id_card_first_name_ai,
      id_card_last_name_ai,
      id_card_expiry_ai,
      driver_license_number,
      driver_license_name_ai,
      driver_license_first_name_ai,
      driver_license_last_name_ai,
      driver_license_expiry_ai,
      ai_validation_status,
      ai_validation_report
    `, { count: "exact" });

  // Filtre par Rôle (colonne 'role')
  if (filters.role && filters.role !== "all") {
    query = query.eq("role", filters.role);
  }

  // Filtre par Vérification (Workflow de validation)
  if (filters.verified === "true") {
    query = query.eq("is_driver_doc_validated", true);
  } else if (filters.verified === "false") {
    query = query.eq("is_driver_doc_validated", false);
  } else if (filters.verified === "pending") {
    // 1. En attente : Pas encore validé ET pas encore analysé par l'IA
    query = query
      .eq("is_driver_doc_validated", false)
      .eq("ai_validation_status", "PENDING")
      .or("id_card_url.not.is.null,driver_license_url.not.is.null");
  } else if (filters.verified === "ai_verified") {
    // 2. IA Vérifiés : Pas encore validé humainement MAIS IA a dit SUCCESS
    query = query
      .eq("is_driver_doc_validated", false)
      .eq("ai_validation_status", "SUCCESS");
  } else if (filters.verified === "ai_alert") {
    // 3. Alertes IA : Pas encore validé humainement ET IA a dit WARNING ou FAILED
    query = query
      .eq("is_driver_doc_validated", false)
      .in("ai_validation_status", ["FAILED", "WARNING"]);
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

  // On tente d'abord avec tous les champs (y compris IA)
  let { data, error, count } = await query
    .order("created_at", { ascending: false })
    .range(from, to);

  // Si erreur de colonne manquante (42703), on réessaie avec une sélection de base
  if (error && error.code === '42703') {
    console.warn("Retrying getUsers with basic selection (AI columns missing in DB)");
    const basicQuery = supabase
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
        created_at,
        id_card_url,
        driver_license_url
      `, { count: "exact" });
    
    // Apply same filters to basicQuery
    let filteredBasicQuery = basicQuery;
    if (filters.role && filters.role !== "all") filteredBasicQuery = filteredBasicQuery.eq("role", filters.role);
    if (filters.verified === "true") filteredBasicQuery = filteredBasicQuery.eq("is_driver_doc_validated", true);
    else if (filters.verified === "false") filteredBasicQuery = filteredBasicQuery.eq("is_driver_doc_validated", false);
    else if (filters.verified === "pending") filteredBasicQuery = filteredBasicQuery.eq("is_driver_doc_validated", false).or("id_card_url.not.is.null,driver_license_url.not.is.null");
    // skip filters.verified === "ai_alert" as columns are missing
    if (filters.gender && filters.gender !== "all") filteredBasicQuery = filteredBasicQuery.eq("gender", filters.gender);
    if (filters.minRating && filters.minRating > 0) filteredBasicQuery = filteredBasicQuery.gte("rating", filters.minRating);
    if (filters.isNew) {
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      filteredBasicQuery = filteredBasicQuery.gte("created_at", thirtyDaysAgo.toISOString());
    }
    if (filters.search) filteredBasicQuery = filteredBasicQuery.or(`display_name.ilike.%${filters.search}%,email.ilike.%${filters.search}%,phone_number.ilike.%${filters.search}%`);

    const retryRes = await filteredBasicQuery
      .order("created_at", { ascending: false })
      .range(from, to);
    
    data = retryRes.data as any;
    error = retryRes.error;
    count = retryRes.count;
  }

  if (error) {
    console.error("getUsers error:", error);
    return { users: [], totalCount: 0 };
  }

  return { 
    users: data as UserListItem[], 
    totalCount: count || 0 
  };
}
