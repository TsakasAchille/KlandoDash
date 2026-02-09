"use client";

import { useState, useMemo } from "react";
import type { SiteTripRequest, SiteTripRequestStatus } from "@/types/site-request";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { MapPin, Calendar, Phone } from "lucide-react";

interface SiteRequestTableProps {
  requests: SiteTripRequest[];
  onUpdateStatus: (id: string, status: SiteTripRequestStatus) => void;
}

const ITEMS_PER_PAGE = 10;

const statusConfig: Record<SiteTripRequestStatus, { label: string; color: string }> = {
  NEW: { label: "Nouveau", color: "bg-blue-500/20 text-blue-400 border-blue-500/30" },
  REVIEWED: { label: "Examiné", color: "bg-purple-500/20 text-purple-400 border-purple-500/30" },
  CONTACTED: { label: "Contacté", color: "bg-green-500/20 text-green-400 border-green-500/30" },
  IGNORED: { label: "Ignoré", color: "bg-gray-500/20 text-gray-400 border-gray-500/30" },
};

export function SiteRequestTable({
  requests,
  onUpdateStatus,
}: SiteRequestTableProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const filteredRequests = useMemo(() => {
    if (statusFilter === "all") return requests;
    return requests.filter((r) => r.status === statusFilter);
  }, [requests, statusFilter]);

  const totalPages = Math.ceil(filteredRequests.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const paginatedRequests = filteredRequests.slice(
    startIndex,
    startIndex + ITEMS_PER_PAGE
  );

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

  const formatDate = (date: string | null) => {
    if (!date) return "Non précisé";
    try {
      return new Date(date).toLocaleDateString("fr-FR", {
        day: "numeric",
        month: "long",
        year: "numeric",
      });
    } catch {
      return date;
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setCurrentPage(1); }}>
            <SelectTrigger className="w-48 bg-klando-dark-s border-white/10">
              <SelectValue placeholder="Filtrer par statut" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous les statuts</SelectItem>
              <SelectItem value="NEW">Nouveaux</SelectItem>
              <SelectItem value="REVIEWED">Examinés</SelectItem>
              <SelectItem value="CONTACTED">Contactés</SelectItem>
              <SelectItem value="IGNORED">Ignorés</SelectItem>
            </SelectContent>
          </Select>
          <span className="text-sm text-klando-grizzly">
            {filteredRequests.length} demande{filteredRequests.length > 1 ? "s" : ""}
          </span>
        </div>
      </div>

      <div className="rounded-md border border-white/10 bg-klando-dark-s/30 overflow-hidden">
        <Table>
          <TableHeader className="bg-white/5">
            <TableRow className="hover:bg-transparent border-white/10">
              <TableHead className="text-klando-gold">Origine / Destination</TableHead>
              <TableHead className="text-klando-gold">Contact</TableHead>
              <TableHead className="text-klando-gold">Date souhaitée</TableHead>
              <TableHead className="text-klando-gold">Soumis le</TableHead>
              <TableHead className="text-klando-gold">Statut</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedRequests.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="h-32 text-center text-klando-grizzly">
                  Aucune demande trouvée.
                </TableCell>
              </TableRow>
            ) : (
              paginatedRequests.map((request) => (
                <TableRow key={request.id} className="border-white/5 hover:bg-white/5 transition-colors">
                  <TableCell>
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center gap-2 text-white font-medium">
                        <MapPin className="w-3 h-3 text-klando-gold" />
                        {request.origin_city}
                      </div>
                      <div className="flex items-center gap-2 text-klando-grizzly text-sm">
                        <span className="w-3" />
                        ➜ {request.destination_city}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2 text-white">
                      <Phone className="w-3 h-3 text-klando-gold" />
                      {request.contact_info}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2 text-klando-grizzly">
                      <Calendar className="w-3 h-3" />
                      {formatDate(request.desired_date)}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-col">
                      <span className="text-white text-sm">{formatRelativeDate(request.created_at)}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Select
                      value={request.status}
                      onValueChange={(value) => onUpdateStatus(request.id, value as SiteTripRequestStatus)}
                    >
                      <SelectTrigger className={cn(
                        "w-32 h-8 text-xs font-semibold border",
                        statusConfig[request.status].color
                      )}>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.entries(statusConfig).map(([status, { label }]) => (
                          <SelectItem key={status} value={status}>
                            {label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-end space-x-2">
          <button
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="p-2 rounded-md border border-white/10 disabled:opacity-50 hover:bg-white/5"
          >
            Précédent
          </button>
          <span className="text-sm text-klando-grizzly">
            Page {currentPage} sur {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className="p-2 rounded-md border border-white/10 disabled:opacity-50 hover:bg-white/5"
          >
            Suivant
          </button>
        </div>
      )}
    </div>
  );
}
