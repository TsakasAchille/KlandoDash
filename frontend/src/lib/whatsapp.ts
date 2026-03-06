/**
 * WhatsApp Business Cloud API Service
 */

const WHATSAPP_TOKEN = process.env.WHATSAPP_ACCESS_TOKEN;
const PHONE_NUMBER_ID = process.env.WHATSAPP_PHONE_NUMBER_ID;
const API_VERSION = "v17.0";

interface SendMessageOptions {
  to: string;
  message: string;
}

/**
 * Envoie un message texte simple via WhatsApp Cloud API
 */
export async function sendWhatsAppMessage({ to, message }: SendMessageOptions) {
  if (!WHATSAPP_TOKEN || !PHONE_NUMBER_ID) {
    console.error("WhatsApp credentials missing in environment");
    return { success: false, error: "Configuration manquante" };
  }

  const url = `https://graph.facebook.com/${API_VERSION}/${PHONE_NUMBER_ID}/messages`;

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${WHATSAPP_TOKEN}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        messaging_product: "whatsapp",
        recipient_type: "individual",
        to: to.replace(/\D/g, ""), // Nettoyage du numéro
        type: "text",
        text: { body: message },
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      console.error("WhatsApp API Error:", data);
      return { success: false, error: data.error?.message || "Erreur API" };
    }

    return { success: true, messageId: data.messages?.[0]?.id };
  } catch (error) {
    console.error("WhatsApp Service Exception:", error);
    return { success: false, error: "Erreur réseau" };
  }
}

/**
 * Envoie un Template pré-approuvé (pour initier une conversation)
 */
export async function sendWhatsAppTemplate({ to, templateName, languageCode = "fr", components = [] }: any) {
  if (!WHATSAPP_TOKEN || !PHONE_NUMBER_ID) return { success: false, error: "Config missing" };

  const url = `https://graph.facebook.com/${API_VERSION}/${PHONE_NUMBER_ID}/messages`;

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${WHATSAPP_TOKEN}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        messaging_product: "whatsapp",
        to: to.replace(/\D/g, ""),
        type: "template",
        template: {
          name: templateName,
          language: { code: languageCode },
          components: components
        },
      }),
    });

    const data = await response.json();
    return response.ok ? { success: true, messageId: data.messages?.[0]?.id } : { success: false, error: data };
  } catch (error) {
    return { success: false, error };
  }
}
