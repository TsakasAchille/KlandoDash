import { Resend } from 'resend';
import React from 'react';

const resend = new Resend(process.env.RESEND_API_KEY);

interface SendEmailOptions {
  to: string | string[];
  subject: string;
  react: React.ReactElement;
  from?: string;
}

/**
 * Service universel d'envoi d'emails via Resend
 */
export async function sendEmail({ to, subject, react, from }: SendEmailOptions) {
  if (!process.env.RESEND_API_KEY) {
    console.warn("[MAIL] Envoi annulé : RESEND_API_KEY manquante.");
    return { success: false, error: 'API Key missing' };
  }

  try {
    const { data, error } = await resend.emails.send({
      from: from || process.env.EMAIL_FROM || 'Klando <no-reply@resend.dev>',
      to,
      subject,
      react,
    });

    if (error) {
      console.error("[MAIL ERROR]", error);
      return { success: false, error };
    }

    return { success: true, id: data?.id };
  } catch (error) {
    console.error("[MAIL CRASH]", error);
    return { success: false, error };
  }
}
