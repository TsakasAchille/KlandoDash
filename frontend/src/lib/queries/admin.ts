import { createServerClient } from "@/lib/supabase";
import { unstable_noStore as noStore } from "next/cache";

export interface DashUser {
  email: string;
  role: string;
  active: boolean;
  added_at: string;
  added_by: string | null;
}

/**
 * Récupère tous les utilisateurs autorisés du dashboard
 */
export async function getDashUsers(): Promise<DashUser[]> {
  noStore(); // Désactive le cache Next.js

  const supabase = createServerClient();
  const { data, error } = await supabase
    .from("dash_authorized_users")
    .select("email, role, active, added_at, added_by")
    .order("added_at", { ascending: false });

  if (error) {
    console.error("Erreur getDashUsers:", error);
    return [];
  }

  return data || [];
}

