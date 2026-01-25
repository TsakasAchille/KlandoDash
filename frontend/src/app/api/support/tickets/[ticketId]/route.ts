import { NextRequest, NextResponse } from "next/server";
import { getTicketDetail, updateTicketStatus } from "@/lib/queries/support";
import type { TicketStatus } from "@/types/support";

interface RouteParams {
  params: Promise<{ ticketId: string }>;
}

// GET /api/support/tickets/[ticketId]
export async function GET(request: NextRequest, { params }: RouteParams) {
  try {
    const { ticketId } = await params;

    const ticket = await getTicketDetail(ticketId);

    if (!ticket) {
      return NextResponse.json(
        { error: "Ticket non trouve" },
        { status: 404 }
      );
    }

    return NextResponse.json(ticket);
  } catch (error) {
    console.error("GET /api/support/tickets/[ticketId] error:", error);
    return NextResponse.json(
      { error: "Erreur serveur" },
      { status: 500 }
    );
  }
}

// PATCH /api/support/tickets/[ticketId]
export async function PATCH(request: NextRequest, { params }: RouteParams) {
  try {
    const { ticketId } = await params;
    const body = await request.json();
    const { status } = body as { status: TicketStatus };

    if (!status) {
      return NextResponse.json(
        { error: "Status requis" },
        { status: 400 }
      );
    }

    const validStatuses: TicketStatus[] = ["OPEN", "CLOSED", "PENDING"];
    if (!validStatuses.includes(status)) {
      return NextResponse.json(
        { error: "Status invalide" },
        { status: 400 }
      );
    }

    const result = await updateTicketStatus(ticketId, status);

    if (!result.success) {
      return NextResponse.json(
        { error: result.error || "Erreur lors de la mise a jour" },
        { status: 500 }
      );
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("PATCH /api/support/tickets/[ticketId] error:", error);
    return NextResponse.json(
      { error: "Erreur serveur" },
      { status: 500 }
    );
  }
}
