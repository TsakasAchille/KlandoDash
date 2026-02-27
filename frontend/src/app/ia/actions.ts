"use server";

import { auth } from "@/lib/auth";
import { createServerClient } from "@/lib/supabase";
import { sendEmail } from "@/lib/mail";
import React from "react";

/**
 * Recherche les conducteurs ayant déjà effectué un trajet spécifique
 */
export async function searchHistoricalDrivers(origin: string, destination: string) {
  const session = await auth();
  if (!session) throw new Error("Unauthorized");

  const supabase = createServerClient();

  // Recherche dans l'historique des trajets
  const { data, error } = await supabase
    .from("trips")
    .select(`
      departure_name,
      destination_name,
      departure_schedule,
      driver_id,
      driver:users!fk_driver (
        uid,
        display_name,
        photo_url,
        phone_number,
        rating
      )
    `)
    .ilike("departure_name", `%${origin}%`)
    .ilike("destination_name", `%${destination}%`)
    .not("driver_id", "is", null)
    .order("departure_schedule", { ascending: false });

  if (error) {
    console.error("searchHistoricalDrivers error:", error);
    return [];
  }

  // On garde le trajet le plus récent pour chaque conducteur unique trouvé
  const uniqueDriversMap = new Map();
  data.forEach((item: any) => {
    if (item.driver && !uniqueDriversMap.has(item.driver_id)) {
      uniqueDriversMap.set(item.driver_id, {
        ...item.driver,
        matched_trip: {
          departure: item.departure_name,
          destination: item.destination_name,
          date: item.departure_schedule
        }
      });
    }
  });

  return Array.from(uniqueDriversMap.values());
}

/**
 * Récupère les informations d'un utilisateur par UID ou Email
 */
export async function getUserInfo(target: string) {
  const session = await auth();
  if (!session) throw new Error("Unauthorized");

  const supabase = createServerClient();
  const cleanTarget = target.trim();
  const isEmail = cleanTarget.includes("@");

  console.log(`[IA-TOOLS] Fetching user info for: ${cleanTarget} (isEmail: ${isEmail})`);

  const query = supabase
    .from("users")
    .select("uid, display_name, email, phone_number, photo_url");

  if (isEmail) {
    query.eq("email", cleanTarget);
  } else {
    query.eq("uid", cleanTarget);
  }

  const { data, error } = await query.single();

  if (error) {
    console.error(`[IA-TOOLS] Error fetching user ${cleanTarget}:`, error.message);
    return null;
  }

  if (!data) {
    console.warn(`[IA-TOOLS] No user found for: ${cleanTarget}`);
    return null;
  }

  return data;
}

/**
 * Crée un brouillon de proposition dans le centre éditorial (mailing)
 */
export async function createPropositionDraft(target: string, subject: string, message: string, imageUrl?: string) {
  const session = await auth();
  if (!session) throw new Error("Unauthorized");

  const cleanTarget = target.trim();
  console.log(`[IA-TOOLS] Creating draft for "${cleanTarget}" by ${session.user?.email}`);

  const supabase = createServerClient();
  
  // 1. Tenter de récupérer les infos utilisateur
  const user = await getUserInfo(cleanTarget);
  
  let recipientEmail = user?.email;
  let recipientName = user?.display_name;

  // 2. Fallbacks si l'utilisateur n'est pas dans la DB "users"
  if (!recipientEmail) {
    if (cleanTarget.includes("@")) {
      recipientEmail = cleanTarget;
      recipientName = "Contact Direct";
    } else if (cleanTarget.toLowerCase() === "global" || !cleanTarget) {
      recipientEmail = "marketing@klando-sn.com";
      recipientName = "Diffusion Globale";
    } else {
      recipientEmail = "pending@klando-sn.com";
      recipientName = `Cible: ${cleanTarget}`;
    }
  }

  // 3. Créer le brouillon dans dash_marketing_emails
  const { data: draft, error } = await supabase
    .from("dash_marketing_emails")
    .insert([{
      category: 'MATCH_FOUND',
      subject: subject,
      content: message,
      recipient_email: recipientEmail,
      recipient_name: recipientName,
      status: 'DRAFT',
      created_at: new Date().toISOString(),
      is_ai_generated: true,
      image_url: imageUrl || null
    }])
    .select()
    .single();

  if (error) {
    console.error("[IA-TOOLS] createPropositionDraft error:", error);
    return { success: false, error: `Erreur DB: ${error.message}` };
  }

  console.log(`[IA-TOOLS] Draft created successfully with ID: ${draft.id} (Image: ${!!imageUrl})`);
  return { success: true, id: draft.id };
}
