import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { addComment, getTicketDetail } from "@/lib/queries/support";
import { createClient } from "@supabase/supabase-js";
import { Resend } from "resend";
import { MentionNotificationEmail } from "@/components/emails/mention-notification";
import { render } from "@react-email/render";

// Initialize services
const supabaseAdmin = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

interface RouteParams {
  params: { ticketId: string };
}

/**
 * Parses mentions, fetches mentioned user data, and triggers email notifications.
 * This function runs without blocking the main API response.
 */
async function sendMentionNotifications(
  commentText: string,
  ticketId: string,
  commenterName: string
) {
  try {
    // Gracefully handle missing Resend API key
    if (!process.env.RESEND_API_KEY) {
      console.warn("RESEND_API_KEY is not set. Skipping email notifications.");
      return;
    }

    const resend = new Resend(process.env.RESEND_API_KEY); // Revert to simple initialization
    
    const mentionRegex = /@(\w+)/g;
    const mentionedIds = Array.from(commentText.matchAll(mentionRegex), match => match[1]);
    console.log("Mentioned IDs:", mentionedIds);

    if (mentionedIds.length === 0) {
      return;
    }

    // 1. Get user data for the mentioned IDs
    const { data: users, error: userError } = await supabaseAdmin
      .from("dash_authorized_users")
      .select("email, display_name")
      .in("role", ["admin", "support"]);
    console.log("Fetched dash_authorized_users:", users);
    if (userError) throw userError;

    const usersToNotify = users.filter(user => 
      mentionedIds.includes(user.display_name?.replace(/\s+/g, '') || '')
    );
    console.log("Users to notify:", usersToNotify);
    
    if (usersToNotify.length === 0) return;

    // 2. Get ticket details for the email subject
    const ticket = await getTicketDetail(ticketId);
    console.log("Fetched ticket details:", ticket);
    if (!ticket) {
        console.error(`Could not find ticket ${ticketId} for notification.`);
        return;
    }

    // 3. Send an email to each mentioned user
    for (const user of usersToNotify) {
      // Manually render React component to HTML using @react-email/render
      const emailHtml = await render(
        <MentionNotificationEmail
          mentionedBy={commenterName}
          ticketId={ticket.ticket_id}
          ticketSubject={ticket.subject || "Sans sujet"}
          commentText={commentText}
          dashboardUrl={process.env.NEXTAUTH_URL || "http://localhost:3000"}
        />,
        { pretty: true }
      );
      console.log(`Rendering email for ${user.email}. HTML length: ${emailHtml.length}`);

      const { data, error: sendError } = await resend.emails.send({
        from: process.env.RESEND_FROM_EMAIL || "KlandoDash <onboarding@resend.dev>",
        to: user.email,
        subject: `Nouvelle mention de ${commenterName} sur le ticket #${ticket.ticket_id}`,
        html: emailHtml,
      });

      if (sendError) {
        console.error(`Resend error for ${user.email}:`, sendError);
      } else {
        console.log(`Email sent to ${user.email} for ticket ${ticket.ticket_id}. Resend ID: ${data?.id}`);
      }
    }
  } catch (error) {
    console.error("Failed to send mention notifications:", error);
  }
}

// POST /api/support/tickets/[ticketId]/comments
export async function POST(request: NextRequest, { params }: RouteParams) {
  try {
    const session = await auth();
    if (!session?.user?.email) {
      return NextResponse.json({ error: "Non autorisé" }, { status: 401 });
    }

    const { ticketId } = params;
    const body = await request.json();
    const { text } = body as { text: string };

    if (!text || text.trim().length < 3) {
      return NextResponse.json(
        { error: "Le commentaire doit faire au moins 3 caracteres." },
        { status: 400 }
      );
    }

    const trimmedText = text.trim();
    const result = await addComment(ticketId, session.user.email, trimmedText, "admin");

    if (!result.success || !result.commentId) {
      return NextResponse.json(
        { error: result.error || "Erreur lors de l'ajout du commentaire." },
        { status: 500 }
      );
    }
    
    // --- New Mention Logic (Fire-and-Forget) ---
    // We don't await this so the API can respond quickly.
    sendMentionNotifications(
      trimmedText, 
      ticketId, 
      session.user.name || session.user.email
    );
    // --- End New Mention Logic ---

    return NextResponse.json({
      comment_id: result.commentId,
      ticket_id: ticketId,
      user_id: session.user.email,
      comment_text: trimmedText,
      created_at: new Date().toISOString(),
      comment_source: "admin",
      admin_name: session.user.name || session.user.email, // Pass admin name for display
    });
  } catch (error) {
    console.error("POST /api/support/tickets/[ticketId]/comments error:", error);
    return NextResponse.json({ error: "Erreur serveur." }, { status: 500 });
  }
}