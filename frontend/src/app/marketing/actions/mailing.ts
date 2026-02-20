"use server";

import { revalidatePath } from "next/cache";
import { createAdminClient } from "@/lib/supabase";
import { auth } from "@/lib/auth";
import { askKlandoAI } from "@/lib/gemini";
import { sendEmail } from "@/lib/mail";
import React from "react";
import { EmailCategory, EmailStatus, MarketingEmail } from "../types";
import fs from "fs/promises";
import path from "path";

/**
 * Sauvegarde le feedback de l'utilisateur (Like/Commentaire) et met à jour les mémoires IA
 */
export async function saveMailingFeedbackAction(id: string, isLiked: boolean, feedback?: string) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  
  // 1. Mise à jour en base
  const { data: email, error } = await supabase
    .from('dash_marketing_emails')
    .update({ 
      is_liked: isLiked, 
      admin_feedback: feedback 
    })
    .eq('id', id)
    .select()
    .single();

  if (error) return { success: false };

  // 2. Si un feedback est donné ou si c'est liké, on met à jour le fichier mémoire
  try {
    const memoryPath = path.join(process.cwd(), "docs/MARKETING_MEMORIES.md");
    let content = await fs.readFile(memoryPath, "utf-8");

    if (feedback) {
      const feedbackEntry = `\n*   **Feedback (${new Date().toLocaleDateString()})** : "${feedback}" (Sur le mail: "${email.subject}")`;
      content = content.replace("## 2. Historique des Retours Admin (Apprentissage)", `## 2. Historique des Retours Admin (Apprentissage)${feedbackEntry}`);
    }

    if (isLiked) {
      const likeEntry = `\n*   **Exemple Liké** : Objet "${email.subject}" - Contenu: "${email.content.substring(0, 50)}..."`;
      content = content.replace("## 3. Exemples de Succès (Liked)", `## 3. Exemples de Succès (Liked)${likeEntry}`);
    }

    await fs.writeFile(memoryPath, content, "utf-8");
  } catch (err) {
    console.error("[MEMORY UPDATE ERROR]", err);
  }

  revalidatePath("/marketing");
  return { success: true };
}

/**
 * Télécharge un fichier (image ou doc) vers Supabase Storage
 */
export async function uploadMarketingImageAction(base64DataWithHeader: string) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  
  // Extraire le type mime et les données
  const matches = base64DataWithHeader.match(/^data:([a-zA-Z0-9]+\/[a-zA-Z0-9-.+]+);base64,(.*)$/);
  if (!matches || matches.length !== 3) return { success: false, error: "Format invalide" };

  const contentType = matches[1];
  const base64Data = matches[2];
  const buffer = Buffer.from(base64Data, 'base64');
  
  // Déterminer l'extension
  let extension = 'bin';
  if (contentType.includes('image/png')) extension = 'png';
  else if (contentType.includes('image/jpeg')) extension = 'jpg';
  else if (contentType.includes('image/webp')) extension = 'webp';
  else if (contentType.includes('application/pdf')) extension = 'pdf';

  const fileName = `${Date.now()}.${extension}`;
  const filePath = `uploads/${fileName}`;

  const { error } = await supabase.storage
    .from('marketing')
    .upload(filePath, buffer, {
      contentType,
      upsert: true
    });

  if (error) {
    console.error("[STORAGE ERROR]", error);
    return { success: false };
  }

  const { data: { publicUrl } } = supabase.storage
    .from('marketing')
    .getPublicUrl(filePath);

  return { success: true, url: publicUrl };
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

  // Construction du corps HTML avec image si présente
  const htmlContent = `
    <div style="font-family: sans-serif; padding: 20px; color: #333; line-height: 1.6;">
      <div style="margin-bottom: 30px; white-space: pre-wrap;">${email.content}</div>
      ${email.image_url ? `
        <div style="margin-top: 20px; border: 1px solid #eee; border-radius: 12px; overflow: hidden; max-width: 600px;">
          <img src="${email.image_url}" alt="Carte de votre trajet" style="width: 100%; display: block;" />
        </div>
      ` : ''}
      <div style="margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px; font-size: 12px; color: #999;">
        L'équipe Klando
      </div>
    </div>
  `;

  const res = await sendEmail({
    to: email.recipient_email,
    subject: email.subject,
    react: React.createElement("div", { dangerouslySetInnerHTML: { __html: htmlContent } })
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
 * Déplace un email vers la corbeille
 */
export async function moveEmailToTrashAction(id: string) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  const { error } = await supabase
    .from('dash_marketing_emails')
    .update({ status: 'TRASH' })
    .eq('id', id);

  if (error) return { success: false };
  revalidatePath("/marketing");
  return { success: true };
}

/**
 * Met à jour un email (contenu, sujet ou flag AI)
 */
export async function updateMarketingEmailAction(id: string, updates: Partial<MarketingEmail>) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  const { error } = await supabase
    .from('dash_marketing_emails')
    .update(updates)
    .eq('id', id);

  if (error) return { success: false };
  revalidatePath("/marketing");
  return { success: true };
}

/**
 * Crée un brouillon d'email manuellement (ou via Aide IA)
 */
export async function createEmailDraftAction(data: {
  recipient_email: string;
  recipient_name?: string;
  subject: string;
  content: string;
  category: EmailCategory;
  is_ai_generated?: boolean;
  image_url?: string;
}) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  const { data: draft, error } = await supabase
    .from('dash_marketing_emails')
    .insert([{
      ...data,
      status: 'DRAFT',
      is_ai_generated: data.is_ai_generated || false,
      image_url: data.image_url || null,
      created_at: new Date().toISOString()
    }])
    .select()
    .single();

  if (error) return { success: false, message: "Échec de sauvegarde" };
  
  revalidatePath("/marketing");
  return { success: true, id: draft.id };
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
    .limit(50);

  if (error) return { success: false, data: [] };
  return { success: true, data: data as MarketingEmail[] };
}

/**
 * Génère des suggestions de mailing ciblées via IA
 */
export async function generateMailingSuggestionsAction() {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();

  // 1. Charger les mémoires marketing
  let marketingMemories = "";
  try {
    const memoryPath = path.join(process.cwd(), "docs/MARKETING_MEMORIES.md");
    marketingMemories = await fs.readFile(memoryPath, "utf-8");
  } catch (e) {
    console.warn("No memories found yet.");
  }

  // 2. Récupérer les données cibles pour l'IA
  const { data: prospects } = await supabase.from('site_trip_requests').select('*').eq('status', 'NEW').limit(10);
  const { data: inactiveUsers } = await supabase.from('users').select('*').limit(10);

  const dataContext = {
    prospects: prospects?.map(p => ({ email: p.contact_info, from: p.origin_city, to: p.destination_city })),
    inactive_users: inactiveUsers?.map(u => ({ name: u.display_name, email: u.email })),
    preferences: marketingMemories
  };

  // 3. Demander à l'IA de suggérer des opportunités avec raisonnement
  const prompt = `
    En te basant sur nos préférences marketing et sur les données fournies, identifie 3 opportunités de mailing.
    IMPORTANT : Pour chaque mail, explique précisément POURQUOI tu suggères cette approche dans le champ "ai_reasoning".
    
    Structure JSON attendue :
    {
      "opportunities": [
        {
          "category": "MATCH_FOUND" | "RETENTION" | "WELCOME" | "PROMO",
          "recipient_email": "email",
          "recipient_name": "nom",
          "subject": "sujet",
          "content": "contenu Markdown",
          "ai_reasoning": "Explication de la stratégie choisie"
        }
      ]
    }
  `;

  try {
    const aiResponse = await askKlandoAI(prompt, { context: dataContext });
    
    const jsonMatch = aiResponse.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error("IA n'a pas renvoyé de JSON valide");
    
    const { opportunities } = JSON.parse(jsonMatch[0]);

    if (opportunities && opportunities.length > 0) {
      const { error } = await supabase.from('dash_marketing_emails').insert(
        opportunities.map((o: any) => ({
          ...o,
          status: 'DRAFT',
          is_ai_generated: true
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
