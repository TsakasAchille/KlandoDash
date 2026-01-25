"use client";

import { useState, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import type {
  SupportTicketWithUser,
  TicketDetail,
  TicketStatus,
} from "@/types/support";
import { TicketTable } from "@/components/support/ticket-table";
import { TicketDetails } from "@/components/support/ticket-details";

interface SupportPageClientProps {
  tickets: SupportTicketWithUser[];
  initialSelectedId: string | null;
  initialSelectedTicket: TicketDetail | null;
}

export function SupportPageClient({
  tickets,
  initialSelectedId,
  initialSelectedTicket,
}: SupportPageClientProps) {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [selectedTicketId, setSelectedTicketId] = useState<string | null>(
    initialSelectedId
  );
  const [selectedTicket, setSelectedTicket] = useState<TicketDetail | null>(
    initialSelectedTicket
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Mettre a jour l'URL quand on selectionne un ticket
  const updateUrl = useCallback(
    (ticketId: string | null) => {
      const params = new URLSearchParams(searchParams.toString());
      if (ticketId) {
        params.set("selected", ticketId);
      } else {
        params.delete("selected");
      }
      router.push(`/support?${params.toString()}`, { scroll: false });
    },
    [router, searchParams]
  );

  // Selectionner un ticket
  const handleSelectTicket = async (ticket: SupportTicketWithUser) => {
    if (ticket.ticket_id === selectedTicketId) {
      // Deselectionner
      setSelectedTicketId(null);
      setSelectedTicket(null);
      updateUrl(null);
      return;
    }

    setSelectedTicketId(ticket.ticket_id);
    updateUrl(ticket.ticket_id);
    setIsLoading(true);
    setError(null);

    try {
      // Fetch les details du ticket via API
      const response = await fetch(`/api/support/tickets/${ticket.ticket_id}`);
      if (!response.ok) {
        throw new Error("Erreur lors du chargement du ticket");
      }
      const data = await response.json();
      setSelectedTicket(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue");
      setSelectedTicket(null);
    } finally {
      setIsLoading(false);
    }
  };

  // Changer le status du ticket
  const handleStatusChange = async (newStatus: TicketStatus) => {
    if (!selectedTicketId || !selectedTicket) return;

    try {
      const response = await fetch(`/api/support/tickets/${selectedTicketId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || "Erreur lors de la mise a jour");
      }

      // Optimistic update
      setSelectedTicket((prev) =>
        prev ? { ...prev, status: newStatus } : null
      );

      // Refresh la page pour mettre a jour la liste
      router.refresh();
    } catch (err) {
      throw err;
    }
  };

  // Ajouter un commentaire
  const handleAddComment = async (text: string) => {
    if (!selectedTicketId) return;

    try {
      const response = await fetch(
        `/api/support/tickets/${selectedTicketId}/comments`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || "Erreur lors de l'ajout du commentaire");
      }

      const newComment = await response.json();

      // Optimistic update - ajouter le commentaire a la liste
      setSelectedTicket((prev) =>
        prev
          ? {
              ...prev,
              comments: [...(prev.comments || []), newComment],
            }
          : null
      );
    } catch (err) {
      throw err;
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Liste des tickets */}
      <div className="space-y-4">
        <TicketTable
          tickets={tickets}
          selectedTicketId={selectedTicketId}
          onSelectTicket={handleSelectTicket}
        />
      </div>

      {/* Details du ticket */}
      <div className="lg:sticky lg:top-6 lg:h-fit">
        <div className="rounded-lg border bg-card p-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-klando-gold"></div>
            </div>
          ) : error ? (
            <div className="text-center py-12 text-red-500">{error}</div>
          ) : selectedTicket ? (
            <TicketDetails
              ticket={selectedTicket}
              onStatusChange={handleStatusChange}
              onAddComment={handleAddComment}
            />
          ) : (
            <div className="text-center py-12 text-muted-foreground">
              Selectionnez un ticket pour voir les details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
