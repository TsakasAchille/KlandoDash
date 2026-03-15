/**
 * WhatsApp Business Cloud API Service
 */

const WHATSAPP_TOKEN = process.env.WHATSAPP_ACCESS_TOKEN;
const PHONE_NUMBER_ID = process.env.WHATSAPP_PHONE_ID || process.env.WHATSAPP_PHONE_NUMBER_ID;
const WHATSAPP_ACCOUNT_ID = process.env.WHATSAPP_ACCOUNT_ID;
const API_VERSION = "v22.0";

interface SendMessageOptions {
  to: string;
  message: string;
}

/**
 * Envoie un message texte simple via WhatsApp Cloud API
 */
export async function sendWhatsAppMessage({ to, message }: SendMessageOptions) {
  if (!WHATSAPP_TOKEN || !PHONE_NUMBER_ID) {
    console.error("[WA] Credentials missing:", { hasToken: !!WHATSAPP_TOKEN, hasPhoneId: !!PHONE_NUMBER_ID });
    return { success: false, error: "Configuration manquante" };
  }

  const cleanNumber = to.replace(/\D/g, "");
  const url = `https://graph.facebook.com/${API_VERSION}/${PHONE_NUMBER_ID}/messages`;

  console.log("[WA] Sending message to:", cleanNumber, "via", url);

  try {
    const body = {
      messaging_product: "whatsapp",
      recipient_type: "individual",
      to: cleanNumber,
      type: "text",
      text: { body: message },
    };

    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${WHATSAPP_TOKEN}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    if (!response.ok) {
      console.error("[WA] API Error:", JSON.stringify(data, null, 2));
      return { success: false, error: data.error?.message || "Erreur API" };
    }

    console.log("[WA] Message sent successfully:", data.messages?.[0]?.id);
    return { success: true, messageId: data.messages?.[0]?.id };
  } catch (error) {
    console.error("[WA] Network Exception:", error);
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
