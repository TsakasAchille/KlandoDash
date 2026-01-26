"use client";

import { useState } from "react";
import type { TicketDetail, TicketStatus } from "@/types/support";
import { CONTACT_PREFERENCE_LABELS } from "@/types/support";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  User,
  Phone,
  Mail,
  Calendar,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
} from "lucide-react";
import { TicketStatusBadge } from "./ticket-status-badge";
import { CommentThread } from "./comment-thread";
import { CommentForm } from "./comment-form";
import { updateTicketStatusAction } from "@/app/support/actions";

interface TicketDetailsProps {
  ticket: TicketDetail;
  onAddComment: (text: string) => Promise<void>;
}

export function TicketDetails({
  ticket,
  onAddComment,
}: TicketDetailsProps) {
  const [changingStatus, setChangingStatus] = useState<TicketStatus | null>(null);

  const formatDate = (date: string) => {
    try {
      return format(new Date(date), "dd/MM/yyyy HH:mm", { locale: fr });
    } catch {
      return date;
    }
  };

  const handleStatusChange = async (newStatus: TicketStatus) => {
    if (changingStatus || ticket.status === newStatus) return;

    setChangingStatus(newStatus);
    try {
      const result = await updateTicketStatusAction(ticket.ticket_id, newStatus);
      if (!result.success) {
        // Optionnel : Gérer l'erreur avec un state ou une notification
        console.error(result.error);
        alert(`Erreur: ${result.error}`);
      }
      // La revalidation se fait côté serveur, pas besoin de router.refresh()
    } finally {
      setChangingStatus(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <TicketStatusBadge status={ticket.status} />
        </div>
        <h2 className="text-xl font-semibold text-klando-gold">
          {ticket.subject || "(Sans sujet)"}
        </h2>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <User className="w-4 h-4" />
          <span>{ticket.user_display_name || "Anonyme"}</span>
          <span className="mx-1">•</span>
          <Calendar className="w-4 h-4" />
          <span>{formatDate(ticket.created_at)}</span>
        </div>
      </div>

      <Separator />

      {/* Message original */}
      <div className="space-y-2">
        <h3 className="text-sm font-medium text-muted-foreground">
          Message original
        </h3>
        <div className="p-4 rounded-lg bg-klando-dark/50 border border-klando-dark">
          <p className="whitespace-pre-wrap text-white">{ticket.message}</p>
        </div>
      </div>

      {/* Contact */}
      <div className="space-y-2">
        <h3 className="text-sm font-medium text-muted-foreground">
          Contact ({CONTACT_PREFERENCE_LABELS[ticket.contact_preference]})
        </h3>
        <div className="flex flex-col gap-2">
          {ticket.phone && (
            <div className="flex items-center gap-2 text-sm">
              <Phone className="w-4 h-4 text-klando-gold" />
              <a
                href={`tel:${ticket.phone}`}
                className="hover:text-klando-gold transition-colors"
              >
                {ticket.phone}
              </a>
            </div>
          )}
          {ticket.mail && (
            <div className="flex items-center gap-2 text-sm">
              <Mail className="w-4 h-4 text-klando-gold" />
              <a
                href={`mailto:${ticket.mail}`}
                className="hover:text-klando-gold transition-colors"
              >
                {ticket.mail}
              </a>
            </div>
          )}
          {!ticket.phone && !ticket.mail && (
            <p className="text-sm text-muted-foreground">
              Aucune information de contact
            </p>
          )}
        </div>
      </div>

      <Separator />

      {/* Actions status */}
      <div className="space-y-2">
        <h3 className="text-sm font-medium text-muted-foreground">Actions</h3>
        <div className="flex flex-wrap gap-2">
          {ticket.status !== "CLOSED" && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleStatusChange("CLOSED")}
              disabled={changingStatus !== null}
              className="border-green-500/30 text-green-400 hover:bg-green-500/10"
            >
              {changingStatus === "CLOSED" ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <CheckCircle className="w-4 h-4 mr-2" />
              )}
              Marquer Ferme
            </Button>
          )}
          {ticket.status !== "PENDING" && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleStatusChange("PENDING")}
              disabled={changingStatus !== null}
              className="border-yellow-500/30 text-yellow-400 hover:bg-yellow-500/10"
            >
              {changingStatus === "PENDING" ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Clock className="w-4 h-4 mr-2" />
              )}
              En attente
            </Button>
          )}
          {ticket.status !== "OPEN" && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleStatusChange("OPEN")}
              disabled={changingStatus !== null}
              className="border-blue-500/30 text-blue-400 hover:bg-blue-500/10"
            >
              {changingStatus === "OPEN" ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <XCircle className="w-4 h-4 mr-2" />
              )}
              Rouvrir
            </Button>
          )}
        </div>
      </div>

      <Separator />

      {/* Commentaires */}
      <div className="space-y-4">
        <h3 className="text-sm font-medium text-muted-foreground">
          Commentaires ({ticket.comments?.length || 0})
        </h3>
        <CommentThread comments={ticket.comments || []} />
        <CommentForm onSubmit={onAddComment} disabled={changingStatus !== null} />
      </div>
    </div>
  );
}
