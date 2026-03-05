"use server";

import { revalidatePath } from "next/cache";
import { createAdminClient } from "@/lib/supabase";
import { auth } from "@/lib/auth";
import { askKlandoAI } from "@/lib/gemini";
import { sendEmail } from "@/lib/mail";
import React from "react";
import { MessageCategory, MessageStatus, MarketingMessage, MessageChannel } from "../types";
import { recordAuditLog } from "@/lib/audit";
import fs from "fs/promises";
import path from "path";

/**
 * Sauvegarde le feedback de l'utilisateur (Like/Commentaire) et met à jour les mémoires IA
 */
export async function saveMessagingFeedbackAction(id: string, isLiked: boolean, feedback?: string) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  
  // 1. Mise à jour en base
  const { data: message, error } = await supabase
    .from('dash_marketing_messages')
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
      const feedbackEntry = `\n*   **Feedback (${new Date().toLocaleDateString()})** : "${feedback}" (Sur le message: "${message.subject || message.content.substring(0, 20)}")`;
      content = content.replace("## 2. Historique des Retours Admin (Apprentissage)", `## 2. Historique des Retours Admin (Apprentissage)${feedbackEntry}`);
    }

    if (isLiked) {
      const likeEntry = `\n*   **Exemple Liké** : Canal "${message.channel}" - Contenu: "${message.content.substring(0, 50)}..."`;
      content = content.replace("## 3. Exemples de Succès (Liked)", `## 3. Exemples de Succès (Liked)${likeEntry}`);
    }

    await fs.writeFile(memoryPath, content, "utf-8");
  } catch (err) {
    console.error("[MEMORY UPDATE ERROR]", err);
  }

  await recordAuditLog({
    action: 'USER_UPDATE',
    entityType: 'MARKETING_MESSAGE',
    entityId: id,
    details: { isLiked, hasFeedback: !!feedback }
  });

  revalidatePath("/marketing");
  return { success: true };
}

/**
 * Envoie un message (Email ou WhatsApp)
 */
export async function sendMessageAction(id: string) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  const { data: message, error: fetchError } = await supabase
    .from('dash_marketing_messages')
    .select('*')
    .eq('id', id)
    .single();

  if (fetchError || !message) return { success: false, message: "Message introuvable" };

  if (message.channel === 'EMAIL') {
    return sendEmailInternalAction(id);
  } else {
    // Pour WhatsApp, on marque juste comme envoyé pour l'instant (en attendant l'API Meta)
    // L'envoi se fait via wa.me coté client
    await supabase.from('dash_marketing_messages').update({
      status: 'SENT',
      sent_at: new Date().toISOString()
    }).eq('id', id);
    
    return { success: true, via: 'WHATSAPP_LINK' };
  }
}

/**
 * Logique interne d'envoi d'email
 */
async function sendEmailInternalAction(id: string) {
  const supabase = createAdminClient();
  const { data: email } = await supabase
    .from('dash_marketing_messages')
    .select('*')
    .eq('id', id)
    .single();

  if (!email) return { success: false };

  // Construction du corps HTML avec images
  const imagesHtml = email.images && email.images.length > 0 
    ? email.images.map((img: { url: string; description: string }) => `
        <div style="margin-top: 20px; border: 1px solid #eee; border-radius: 12px; overflow: hidden; max-width: 600px; background: #f9f9f9;">
          <img src="${img.url}" alt="${img.description}" style="width: 100%; display: block;" />
          <div style="padding: 10px; font-size: 11px; color: #666; text-align: center; border-top: 1px solid #eee;">${img.description}</div>
        </div>
      `).join('')
    : (email.image_url ? `
        <div style="margin-top: 20px; border: 1px solid #eee; border-radius: 12px; overflow: hidden; max-width: 600px;">
          <img src="${email.image_url}" alt="Carte de votre trajet" style="width: 100%; display: block;" />
        </div>
      ` : '');

  const htmlContent = `
    <div style="font-family: sans-serif; padding: 20px; color: #333; line-height: 1.6;">
      <div style="margin-bottom: 30px; white-space: pre-wrap;">${email.content}</div>
      ${imagesHtml}
      <div style="margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px; font-size: 12px; color: #999;">
        L'équipe Klando
      </div>
    </div>
  `;

  const res = await sendEmail({
    to: email.recipient_contact,
    subject: email.subject || "Message de Klando",
    react: React.createElement("div", { dangerouslySetInnerHTML: { __html: htmlContent } })
  });

  if (res.success) {
    await supabase.from('dash_marketing_messages').update({
      status: 'SENT',
      sent_at: new Date().toISOString(),
      message_id: res.id
    }).eq('id', id);

    await recordAuditLog({
      action: 'EMAIL_SENT',
      entityType: 'MARKETING_MESSAGE',
      entityId: id,
      details: { recipient: email.recipient_contact, subject: email.subject }
    });

    revalidatePath("/marketing");
    return { success: true };
  } else {
    await supabase.from('dash_marketing_messages').update({
      status: 'FAILED',
      error_message: JSON.stringify(res.error)
    }).eq('id', id);
    return { success: false, message: "Échec de l'envoi" };
  }
}

/**
 * Déplace un message vers la corbeille
 */
export async function moveMessageToTrashAction(id: string) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  const { error } = await supabase
    .from('dash_marketing_messages')
    .update({ status: 'TRASH' })
    .eq('id', id);

  if (error) return { success: false };

  await recordAuditLog({
    action: 'MESSAGE_TRASHED',
    entityType: 'MARKETING_MESSAGE',
    entityId: id
  });

  revalidatePath("/marketing");
  return { success: true };
}

/**
 * Met à jour un message
 */
export async function updateMarketingMessageAction(id: string, updates: Partial<MarketingMessage>) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  const { error } = await supabase
    .from('dash_marketing_messages')
    .update(updates)
    .eq('id', id);

  if (error) return { success: false };

  await recordAuditLog({
    action: 'USER_UPDATE',
    entityType: 'MARKETING_MESSAGE',
    entityId: id,
    details: { updates }
  });

  revalidatePath("/marketing");
  return { success: true };
}

/**
 * Crée un brouillon de message
 */
export async function createMessageDraftAction(data: {
  recipient_contact: string;
  recipient_name?: string;
  subject?: string;
  content: string;
  category: MessageCategory;
  channel: MessageChannel;
  is_ai_generated?: boolean;
  image_url?: string;
}) {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  const { data: draft, error } = await supabase
    .from('dash_marketing_messages')
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
  
  await recordAuditLog({
    action: 'MESSAGE_DRAFT_CREATED',
    entityType: 'MARKETING_MESSAGE',
    entityId: draft.id,
    details: { recipient: data.recipient_contact, channel: data.channel }
  });

  revalidatePath("/marketing");
  return { success: true, id: draft.id };
}

/**
 * Récupère l'historique de messagerie
 */
export async function getMarketingMessagesAction() {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) throw new Error("Non autorisé");

  const supabase = createAdminClient();
  const { data, error } = await supabase
    .from('dash_marketing_messages')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(50);

  if (error) return { success: false, data: [] };
  return { success: true, data: data as MarketingMessage[] };
}

/**
 * Génère des suggestions de messagerie (Email + WhatsApp) via IA
 */
export async function generateMessagingSuggestionsAction() {
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
    prospects: prospects?.map(p => ({ contact: p.contact_info, from: p.origin_city, to: p.destination_city })),
    inactive_users: inactiveUsers?.map(u => ({ name: u.display_name, email: u.email, phone: u.phone_number })),
    preferences: marketingMemories
  };

  // 3. Demander à l'IA de suggérer des opportunités avec raisonnement
  const prompt = `
    En te basant sur nos préférences marketing et sur les données fournies, identifie 4 opportunités de messagerie directe.
    Mixe intelligemment entre EMAIL et WHATSAPP selon le type de prospect.
    
    IMPORTANT : 
    - Pour WhatsApp, pas de sujet, sois plus direct et utilise des emojis.
    - Pour Email, utilise un sujet accrocheur.
    - Explique ton choix de canal dans "ai_reasoning".
    
    Structure JSON attendue :
    {
      "opportunities": [
        {
          "channel": "EMAIL" | "WHATSAPP",
          "category": "MATCH_FOUND" | "RETENTION" | "WELCOME" | "PROMO",
          "recipient_contact": "email ou téléphone",
          "recipient_name": "nom",
          "subject": "sujet (null si whatsapp)",
          "content": "contenu Markdown",
          "ai_reasoning": "Explication de la stratégie et du choix du canal"
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
      const { error } = await supabase.from('dash_marketing_messages').insert(
        opportunities.map((o: any) => ({
          ...o,
          status: 'DRAFT',
          is_ai_generated: true
        }))
      );
      if (error) throw error;

      await recordAuditLog({
        action: 'MESSAGE_DRAFT_CREATED',
        entityType: 'MARKETING_MESSAGE',
        details: { type: 'AI_SUGGESTIONS', count: opportunities.length }
      });
    }

    revalidatePath("/marketing");
    return { success: true, count: opportunities.length };
  } catch (err) {
    console.error("[Messaging AI] Failed:", err);
    return { success: false, message: "Échec de la génération." };
  }
}

/**
 * Télécharge un fichier (image ou doc) vers Supabase Storage
 */
export async function uploadMarketingImageAction(base64DataWithHeader: string) {
  // Re-exportée ou gardée ici si besoin, c'est identique à avant
  const session = await auth();
  if (!session) return { success: false };
  const supabase = createAdminClient();
  
  const matches = base64DataWithHeader.match(/^data:([a-zA-Z0-9]+\/[a-zA-Z0-9-.+]+);base64,(.*)$/);
  if (!matches || matches.length !== 3) return { success: false };

  const contentType = matches[1];
  const buffer = Buffer.from(matches[2], 'base64');
  const extension = contentType.split('/')[1];
  const fileName = `${Date.now()}.${extension}`;
  const filePath = `uploads/${fileName}`;

  const { error } = await supabase.storage.from('marketing').upload(filePath, buffer, { contentType });
  if (error) return { success: false, error: error.message };

  const { data: { publicUrl } } = supabase.storage.from('marketing').getPublicUrl(filePath);
  return { success: true, url: publicUrl };
}
