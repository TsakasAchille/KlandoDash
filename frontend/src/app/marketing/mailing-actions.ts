"use server";

import { revalidatePath } from "next/cache";
import { createAdminClient } from "@/lib/supabase";
import { auth } from "@/lib/auth";
import { askKlandoAI } from "@/lib/gemini";
import { sendEmail } from "@/lib/mail";
import React from "react";

export type EmailStatus = 'DRAFT' | 'SENT' | 'FAILED';
export type EmailCategory = 'WELCOME' | 'MATCH_FOUND' | 'RETENTION' | 'PROMO' | 'GENERAL';

export interface MarketingEmail {
  id: string;
  category: EmailCategory;
  subject: string;
  content: string;
  recipient_email: string;
  recipient_name: string | null;
  status: EmailStatus;
  created_at: string;
  sent_at: string | null;
}

/**
 * Génère des suggestions de mailing ciblées via IA
 */
export async function generateMailingSuggestionsAction() {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();

  // 1. Récupérer les données cibles pour l'IA
  const { data: prospects } = await supabase.from('site_trip_requests').select('*').eq('status', 'NEW').limit(10);
  const { data: inactiveUsers } = await supabase.from('users').select('*').limit(10); // Simplifié pour le test

  const dataContext = {
    prospects: prospects?.map(p => ({ email: p.contact_info, from: p.origin_city, to: p.destination_city })),
    inactive_users: inactiveUsers?.map(u => ({ name: u.display_name, email: u.email }))
  };

  // 2. Demander à l'IA de suggérer des opportunités
  const prompt = `
    Analyse ces prospects et utilisateurs. Identifie 3 opportunités de mailing prioritaires.
    Pour chaque opportunité, fournis un objet JSON STRICT avec cette structure exacte :
    {
      "opportunities": [
        {
          "category": "MATCH_FOUND" ou "RETENTION",
          "recipient_email": "email",
          "recipient_name": "nom",
          "subject": "sujet accrocheur",
          "content": "contenu en Markdown (chaleureux, professionnel, max 100 mots)"
        }
      ]
    }
  `;

  try {
    const aiResponse = await askKlandoAI(prompt, { context: dataContext });
    
    // Nettoyer la réponse pour extraire le JSON
    const jsonMatch = aiResponse.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error("IA n'a pas renvoyé de JSON valide");
    
    const { opportunities } = JSON.parse(jsonMatch[0]);

    if (opportunities && opportunities.length > 0) {
      const { error } = await supabase.from('dash_marketing_emails').insert(
        opportunities.map((o: any) => ({
          ...o,
          status: 'DRAFT'
        }))
      );
      if (error) throw error;
    }

    revalidatePath("/marketing");
    return { success: true, count: opportunities.length };
  } catch (err) {
    console.error("[Mailing AI] Failed:", err);
    return { success: false, message: "Échec de la génération." };
  }
}

/**
 * Envoie un email marketing via Resend
 */
export async function sendMarketingEmailAction(id: string) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  const { data: email, error: fetchError } = await supabase
    .from('dash_marketing_emails')
    .select('*')
    .eq('id', id)
    .single();

  if (fetchError || !email) return { success: false, message: "Email introuvable" };

  // Note: On utilise React.createElement pour passer le texte brut Markdown (simplifié ici)
  // Dans une vraie app, on utiliserait un parser Markdown -> React
  const res = await sendEmail({
    to: email.recipient_email,
    subject: email.subject,
    react: React.createElement("div", { 
      style: { fontFamily: 'sans-serif', padding: '20px', color: '#333' }
    }, email.content)
  });

  if (res.success) {
    await supabase.from('dash_marketing_emails').update({
      status: 'SENT',
      sent_at: new Date().toISOString(),
      resend_id: res.id
    }).eq('id', id);
    revalidatePath("/marketing");
    return { success: true };
  } else {
    await supabase.from('dash_marketing_emails').update({
      status: 'FAILED',
      error_message: JSON.stringify(res.error)
    }).eq('id', id);
    return { success: false, message: "Échec de l'envoi" };
  }
}

/**
 * Récupère l'historique de mailing
 */
export async function getMarketingEmailsAction() {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  const { data, error } = await supabase
    .from('dash_marketing_emails')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(20);

  if (error) return { success: false, data: [] };
  return { success: true, data: data as MarketingEmail[] };
}
