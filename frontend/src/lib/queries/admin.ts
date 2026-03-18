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

export interface RoadmapItem {
  id: string;
  phase_name: string;
  timeline: string;
  title: string;
  description: string;
  status: 'todo' | 'in-progress' | 'done';
  progress: number;
  icon_name: string;
  order_index: number;
  is_planning: boolean;
  planning_stage: 'now' | 'next' | 'later' | 'backlog';
  start_date: string | null;
  target_date: string | null;
  custom_color: string | null;
  assigned_to: string[];
  planning_board_id: string | null;
  updated_at: string;
}

/**
 * Récupère les items de la roadmap
 */
export interface DashMember {
  email: string;
  display_name: string | null;
  avatar_url: string | null;
  role: string;
}

export async function getDashMembers(): Promise<DashMember[]> {
  noStore();
  const supabase = createServerClient();

  const { data, error } = await supabase
    .from("dash_authorized_users")
    .select("email, display_name, avatar_url, role")
    .eq("active", true)
    .order("display_name", { ascending: true });

  if (error) {
    console.error("Erreur getDashMembers:", error);
    return [];
  }

  return data || [];
}

export interface PlanningBoard {
  id: string;
  name: string;
  description: string | null;
  color: string | null;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

export async function getPlanningBoards(): Promise<PlanningBoard[]> {
  noStore();
  const supabase = createServerClient();
  const { data, error } = await supabase
    .from("planning_boards")
    .select("*")
    .order("created_at", { ascending: true });

  if (error) {
    console.error("Erreur getPlanningBoards:", error);
    return [];
  }
  return data || [];
}

export async function getRoadmapItems(): Promise<RoadmapItem[]> {
  noStore();
  const supabase = createServerClient();
  
  const { data, error } = await supabase
    .from("roadmap_items")
    .select("*")
    .order("order_index", { ascending: true });

  if (error) {
    console.error("Erreur getRoadmapItems:", error);
    return [];
  }

  return data || [];
}
