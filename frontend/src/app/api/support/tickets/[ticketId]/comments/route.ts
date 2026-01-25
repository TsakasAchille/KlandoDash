import { NextRequest, NextResponse } from "next/server";
import { addComment } from "@/lib/queries/support";

interface RouteParams {
  params: Promise<{ ticketId: string }>;
}

// POST /api/support/tickets/[ticketId]/comments
export async function POST(request: NextRequest, { params }: RouteParams) {
  try {
    const { ticketId } = await params;
    const body = await request.json();
    const { text, userId = "admin" } = body as { text: string; userId?: string };

    if (!text || text.trim().length < 10) {
      return NextResponse.json(
        { error: "Le commentaire doit faire au moins 10 caracteres" },
        { status: 400 }
      );
    }

    const result = await addComment(ticketId, userId, text.trim(), "admin");

    if (!result.success) {
      return NextResponse.json(
        { error: result.error || "Erreur lors de l'ajout du commentaire" },
        { status: 500 }
      );
    }

    // Retourner le commentaire cree
    return NextResponse.json({
      comment_id: result.commentId,
      ticket_id: ticketId,
      user_id: userId,
      comment_text: text.trim(),
      created_at: new Date().toISOString(),
      comment_source: "admin",
    });
  } catch (error) {
    console.error("POST /api/support/tickets/[ticketId]/comments error:", error);
    return NextResponse.json(
      { error: "Erreur serveur" },
      { status: 500 }
    );
  }
}
