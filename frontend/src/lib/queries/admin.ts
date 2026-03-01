import { createServerClient } from "@/lib/supabase";
import { unstable_noStore as noStore } from "next/cache";

export interface DashUser {
  email: string;
  role: string;
  active: boolean;
  added_at: string;
  added_by: string | null;
}

export interface AuditLog {
  id: string;
  created_at: string;
  admin_email: string;
  action_type: string;
  entity_type: string;
  entity_id: string | null;
  details: any;
  ip_address: string | null;
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

/**
 * Récupère tous les journaux d'audit
 */
export async function getAuditLogs(limit = 100): Promise<AuditLog[]> {
  noStore();

  const supabase = createServerClient();
  const { data, error } = await supabase
    .from("dash_audit_logs")
    .select("*")
    .order("created_at", { ascending: false })
    .limit(limit);

  if (error) {
    console.error("Erreur getAuditLogs:", error);
    return [];
  }

  return data || [];
}
