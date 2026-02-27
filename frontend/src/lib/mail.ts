import nodemailer from 'nodemailer';
import React from 'react';
import { render } from '@react-email/render';

interface SendEmailOptions {
  to: string | string[];
  subject: string;
  react: React.ReactElement;
  from?: string;
}

/**
 * Service d'envoi d'emails via Google SMTP (Gmail/Workspace)
 * Avantages : Gratuit, haute limite quotidienne (500-2000), meilleure délivrabilité avec votre domaine.
 */
export async function sendEmail({ to, subject, react, from }: SendEmailOptions) {
  // On récupère les identifiants Google
  const user = process.env.GOOGLE_EMAIL_USER; // ex: contact@klando-sn.com
  const pass = process.env.GOOGLE_EMAIL_APP_PASSWORD; // Mot de passe d'application 16 caractères

  if (!user || !pass) {
    console.warn("[MAIL] Envoi annulé : Identifiants Google SMTP manquants (GOOGLE_EMAIL_USER, GOOGLE_EMAIL_APP_PASSWORD).");
    return { success: false, error: 'SMTP credentials missing' };
  }

  try {
    // 1. Initialiser le transporteur SMTP Google
    const transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: user,
        pass: pass,
      },
    });

    // 2. Convertir le composant React Email en HTML
    const html = await render(react);

    // 3. Envoyer l'email
    const info = await transporter.sendMail({
      from: from || process.env.EMAIL_FROM || `"Klando" <${user}>`,
      to: Array.isArray(to) ? to.join(', ') : to,
      subject,
      html,
    });

    console.log("[MAIL SENT]", info.messageId);
    return { success: true, id: info.messageId };
  } catch (error) {
    console.error("[MAIL CRASH]", error);
    return { success: false, error };
  }
}
