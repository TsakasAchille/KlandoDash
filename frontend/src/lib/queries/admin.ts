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
 * Récupère les journaux d'audit avec filtres et pagination
 */
export async function getAuditLogs(options: { 
  limit?: number, 
  offset?: number,
  adminEmail?: string, 
  actionType?: string 
} = {}): Promise<{ logs: AuditLog[], totalCount: number }> {
  noStore();

  const { limit = 100, offset = 0, adminEmail, actionType } = options;
  const supabase = createServerClient();
  
  let query = supabase
    .from("dash_audit_logs")
    .select("*", { count: "exact" })
    .order("created_at", { ascending: false });

  if (adminEmail && adminEmail !== 'ALL') {
    query = query.eq('admin_email', adminEmail);
  }

  if (actionType && actionType !== 'ALL') {
    query = query.eq('action_type', actionType);
  }

  const { data, error, count } = await query
    .range(offset, offset + limit - 1);

  if (error) {
    console.error("Erreur getAuditLogs:", error);
    return { logs: [], totalCount: 0 };
  }

  return { 
    logs: (data || []) as AuditLog[], 
    totalCount: count || 0 
  };
}

/**
 * Récupère la liste des administrateurs ayant effectué des actions (pour les filtres)
 */
export async function getAuditAdmins(): Promise<string[]> {
  noStore();
  const supabase = createServerClient();
  
  const { data, error } = await supabase
    .from("dash_audit_logs")
    .select("admin_email")
    .order("admin_email");

  if (error) return [];
  
  // Extraire les emails uniques
  const uniqueEmails = Array.from(new Set(data.map(d => d.admin_email)));
  return uniqueEmails;
}
