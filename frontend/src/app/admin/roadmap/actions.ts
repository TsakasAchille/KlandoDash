"use server";

import { createServerClient } from "@/lib/supabase";
import { revalidatePath } from "next/cache";

export async function addRoadmapItem(item: { 
  title: string, 
  description: string, 
  phase_name: string, 
  timeline: string, 
  icon_name: string,
  is_planning: boolean,
  planning_stage?: string,
  target_date?: string | null
}) {
  const supabase = createServerClient();
  
  const { error } = await supabase
    .from("roadmap_items")
    .insert({
      ...item,
      status: 'todo',
      progress: 0,
      order_index: 99
    });

  if (error) {
    console.error("Erreur addRoadmapItem:", error);
    return { success: false, error: error.message };
  }

  revalidatePath("/admin/roadmap");
  return { success: true };
}

export async function updateRoadmapProgress(itemId: string, progress: number, status?: string) {
  const supabase = createServerClient();
  
  let newStatus = status;
  if (!status) {
    if (progress === 100) newStatus = 'done';
    else if (progress > 0) newStatus = 'in-progress';
    else newStatus = 'todo';
  }

  const { error } = await supabase
    .from("roadmap_items")
    .update({ 
      progress, 
      status: newStatus,
      updated_at: new Date().toISOString() 
    })
    .eq("id", itemId);

  if (error) {
    console.error("Erreur updateRoadmapProgress:", error);
    return { success: false, error: error.message };
  }

  revalidatePath("/admin/roadmap");
  return { success: true };
}

export async function updateRoadmapItem(itemId: string, data: any) {
  const supabase = createServerClient();
  
  const { error } = await supabase
    .from("roadmap_items")
    .update({ 
      ...data,
      updated_at: new Date().toISOString() 
    })
    .eq("id", itemId);

  if (error) {
    console.error("Erreur updateRoadmapItem:", error);
    return { success: false, error: error.message };
  }

  revalidatePath("/admin/roadmap");
  return { success: true };
}

export async function toggleRoadmapPlanning(itemId: string, is_planning: boolean) {
  const supabase = createServerClient();
  
  const { error } = await supabase
    .from("roadmap_items")
    .update({ 
      is_planning,
      updated_at: new Date().toISOString() 
    })
    .eq("id", itemId);

  if (error) {
    console.error("Erreur toggleRoadmapPlanning:", error);
    return { success: false, error: error.message };
  }

  revalidatePath("/admin/roadmap");
  return { success: true };
}

export async function deleteRoadmapItem(itemId: string) {
  const supabase = createServerClient();
  
  const { error } = await supabase
    .from("roadmap_items")
    .delete()
    .eq("id", itemId);

  if (error) {
    console.error("Erreur deleteRoadmapItem:", error);
    return { success: false, error: error.message };
  }

  revalidatePath("/admin/roadmap");
  return { success: true };
}
