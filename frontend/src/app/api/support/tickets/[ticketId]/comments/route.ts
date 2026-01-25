import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { addComment } from "@/lib/queries/support";

interface RouteParams {
  params: Promise<{ ticketId: string }>;
}

// POST /api/support/tickets/[ticketId]/comments
export async function POST(request: NextRequest, { params }: RouteParams) {
  try {
    // Vérifier l'authentification
    const session = await auth();
    if (!session?.user?.email) {
      return NextResponse.json(
        { error: "Non autorisé" },
        { status: 401 }
      );
    }

    const userEmail = session.user.email;
    const userName = session.user.name || userEmail;

    const { ticketId } = await params;
    const body = await request.json();
    const { text } = body as { text: string };

    if (!text || text.trim().length < 3) {
      return NextResponse.json(
        { error: "Le commentaire doit faire au moins 3 caracteres" },
        { status: 400 }
      );
    }

    const result = await addComment(ticketId, userEmail, text.trim(), "admin");

    if (!result.success) {
      return NextResponse.json(
        { error: result.error || "Erreur lors de l'ajout du commentaire" },
        { status: 500 }
      );
    }

    // Retourner le commentaire créé avec les infos de l'admin
    return NextResponse.json({
      comment_id: result.commentId,
      ticket_id: ticketId,
      user_id: userEmail,
      comment_text: text.trim(),
      created_at: new Date().toISOString(),
      comment_source: "admin",
      admin_name: userName,
    });
  } catch (error) {
    console.error("POST /api/support/tickets/[ticketId]/comments error:", error);
    return NextResponse.json(
      { error: "Erreur serveur" },
      { status: 500 }
    );
  }
}
