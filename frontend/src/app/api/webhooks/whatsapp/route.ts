import { NextRequest, NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase";

/**
 * GET : Vérification du Webhook par Meta (Setup initial)
 */
export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const mode = searchParams.get("hub.mode");
  const token = searchParams.get("hub.verify_token");
  const challenge = searchParams.get("hub.challenge");

  if (mode === "subscribe" && token === process.env.WHATSAPP_VERIFY_TOKEN) {
    console.log("[WA-WEBHOOK] Webhook verified successfully");
    return new NextResponse(challenge, { status: 200 });
  }

  return new NextResponse("Forbidden", { status: 403 });
}

/**
 * POST : Réception des messages et statuts de Meta
 */
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    console.log("[WA-WEBHOOK] Received payload:", JSON.stringify(body, null, 2));

    const entry = body.entry?.[0];
    const changes = entry?.changes?.[0];
    const value = changes?.value;

    // 1. Gérer les nouveaux messages
    if (value?.messages) {
      const message = value.messages[0];
      const contact = value.contacts?.[0];
      const from = message.from; // Phone number
      const text = message.text?.body;
      const messageId = message.id;

      if (text) {
        const supabase = createAdminClient();

        // Trouver ou créer la conversation
        let { data: conversation } = await supabase
          .from('whatsapp_conversations')
          .select('id')
          .eq('wa_id', from)
          .single();

        if (!conversation) {
          const { data: newConv } = await supabase
            .from('whatsapp_conversations')
            .insert([{
                wa_id: from,
                display_name: contact?.profile?.name || from
            }])
            .select()
            .single();
          conversation = newConv;
        }

        if (!conversation) {
          console.error("[WA-WEBHOOK] Failed to find or create conversation for:", from);
          return NextResponse.json({ error: "Conversation not found" }, { status: 500 });
        }

        // Insérer le message
        await supabase.from('whatsapp_messages').insert([{
          conversation_id: conversation.id,
          wa_message_id: messageId,
          direction: 'INBOUND',
          content: text,
          type: 'text',
          status: 'delivered'
        }]);

        // Incrémenter le compteur de non-lus
        await supabase.rpc('increment_wa_unread', { conv_id: conversation.id });
      }
    }

    // 2. Gérer les confirmations de lecture (statuses)
    if (value?.statuses) {
        const status = value.statuses[0];
        const supabase = createAdminClient();
        await supabase
            .from('whatsapp_messages')
            .update({ status: status.status })
            .eq('wa_message_id', status.id);
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("[WA-WEBHOOK] Error processing webhook:", error);
    return NextResponse.json({ error: "Internal Error" }, { status: 500 });
  }
}
