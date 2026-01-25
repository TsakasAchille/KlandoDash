"use client";

import { useState, useMemo } from "react";
import type { SupportTicketWithUser, TicketStatus } from "@/types/support";
import { cn } from "@/lib/utils";
import { formatDistanceToNow } from "date-fns";
import { fr } from "date-fns/locale";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ChevronLeft, ChevronRight, MessageSquare, User } from "lucide-react";
import { TicketStatusBadge } from "./ticket-status-badge";

interface TicketTableProps {
  tickets: SupportTicketWithUser[];
  selectedTicketId: string | null;
  onSelectTicket: (ticket: SupportTicketWithUser) => void;
}

const ITEMS_PER_PAGE = 10;

export function TicketTable({
  tickets,
  selectedTicketId,
  onSelectTicket,
}: TicketTableProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>("all");

  // Filtrer par status
  const filteredTickets = useMemo(() => {
    if (statusFilter === "all") return tickets;
    return tickets.filter((ticket) => ticket.status === statusFilter);
  }, [tickets, statusFilter]);

  // Pagination
  const totalPages = Math.ceil(filteredTickets.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const paginatedTickets = filteredTickets.slice(
    startIndex,
    startIndex + ITEMS_PER_PAGE
  );

  // Reset page quand le filtre change
  const handleFilterChange = (value: string) => {
    setStatusFilter(value);
    setCurrentPage(1);
  };

  // Format date relative
  const formatRelativeDate = (date: string) => {
    try {
      return formatDistanceToNow(new Date(date), {
        addSuffix: true,
        locale: fr,
      });
    } catch {
      return date;
    }
  };

  // Tronquer le sujet
  const truncateSubject = (subject: string | null, maxLength = 40) => {
    if (!subject) return "(Sans sujet)";
    if (subject.length <= maxLength) return subject;
    return subject.slice(0, maxLength) + "...";
  };

  return (
    <div className="space-y-4">
      {/* Filtres */}
      <div className="flex items-center gap-4">
        <Select value={statusFilter} onValueChange={handleFilterChange}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Statut" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous les statuts</SelectItem>
            <SelectItem value="OPEN">Ouverts</SelectItem>
            <SelectItem value="PENDING">En attente</SelectItem>
            <SelectItem value="CLOSED">Fermes</SelectItem>
          </SelectContent>
        </Select>
        <span className="text-sm text-muted-foreground">
          {filteredTickets.length} ticket{filteredTickets.length > 1 ? "s" : ""}
        </span>
      </div>

      {/* Table */}
      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow className="bg-klando-dark hover:bg-klando-dark">
              <TableHead className="text-klando-gold">Sujet</TableHead>
              <TableHead className="text-klando-gold">Utilisateur</TableHead>
              <TableHead className="text-klando-gold">Statut</TableHead>
              <TableHead className="text-klando-gold">Date</TableHead>
              <TableHead className="text-klando-gold text-center">
                <MessageSquare className="w-4 h-4 inline" />
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedTickets.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={5}
                  className="text-center text-muted-foreground py-8"
                >
                  Aucun ticket trouve
                </TableCell>
              </TableRow>
            ) : (
              paginatedTickets.map((ticket) => (
                <TableRow
                  key={ticket.ticket_id}
                  data-ticket-id={ticket.ticket_id}
                  data-state={
                    selectedTicketId === ticket.ticket_id
                      ? "selected"
                      : undefined
                  }
                  className={cn(
                    "cursor-pointer transition-all",
                    selectedTicketId === ticket.ticket_id &&
                      "bg-klando-burgundy/20"
                  )}
                  onClick={() => onSelectTicket(ticket)}
                >
                  <TableCell>
                    <span className="font-medium">
                      {truncateSubject(ticket.subject)}
                    </span>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-muted flex items-center justify-center">
                        <User className="w-3 h-3 text-muted-foreground" />
                      </div>
                      <span className="text-sm truncate max-w-[120px]">
                        {ticket.user_display_name || "Anonyme"}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <TicketStatusBadge status={ticket.status as TicketStatus} />
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {formatRelativeDate(ticket.created_at)}
                  </TableCell>
                  <TableCell className="text-center">
                    {ticket.comment_count > 0 && (
                      <span className="inline-flex items-center justify-center w-5 h-5 text-xs bg-klando-gold/20 text-klando-gold rounded-full">
                        {ticket.comment_count}
                      </span>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">
            Page {currentPage} sur {totalPages}
          </span>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
