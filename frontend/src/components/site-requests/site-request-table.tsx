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
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Calendar, Phone, Mail } from "lucide-react";
import { Loader2 } from "lucide-react";

interface SiteRequestTableProps {
  requests: SiteTripRequest[];
  onUpdateStatus: (id: string, status: SiteTripRequestStatus) => void;
  updatingId: string | null;
}

const ITEMS_PER_PAGE = 10;

const statusConfig: Record<SiteTripRequestStatus, { label: string; color: string; background: string; }> = {
  NEW: { label: "Nouveau", color: "text-blue-400", background: "bg-blue-500/10" },
  REVIEWED: { label: "Examiné", color: "text-purple-400", background: "bg-purple-500/10" },
  CONTACTED: { label: "Contacté", color: "text-green-400", background: "bg-green-500/10" },
  IGNORED: { label: "Ignoré", color: "text-gray-400", background: "bg-gray-500/10" },
};

interface FilterControlsProps {
  statusFilter: string;
  setStatusFilter: (v: string) => void;
  setCurrentPage: (p: number) => void;
  statusCounts: Record<string, number>;
}

const FilterControls = ({ statusFilter, setStatusFilter, setCurrentPage, statusCounts }: FilterControlsProps) => (
  <>
    {/* Tabs for Desktop */}
    <div className="hidden md:block">
      <Tabs value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setCurrentPage(1); }}>
        <TabsList className="bg-muted/50 p-1 h-auto">
          <TabsTrigger value="all" className="flex items-center gap-2">
            Tous <span className="text-xs px-2 py-0.5 rounded-full bg-background">{statusCounts.all}</span>
          </TabsTrigger>
          {Object.entries(statusConfig).map(([status, { label }]) => (
            <TabsTrigger key={status} value={status} className="flex items-center gap-2">
              {label} 
              <span className={cn("text-xs px-2 py-0.5 rounded-full", statusConfig[status as SiteTripRequestStatus].background, statusConfig[status as SiteTripRequestStatus].color)}>
                {statusCounts[status]}
              </span>
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>
    </div>
    {/* Select for Mobile */}
    <div className="block md:hidden">
       <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setCurrentPage(1); }}>
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Filtrer par statut" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">Tous ({statusCounts.all})</SelectItem>
          {Object.entries(statusConfig).map(([status, { label }]) => (
            <SelectItem key={status} value={status}>{label} ({statusCounts[status]})</SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  </>
);

export function SiteRequestTable({
  requests,
  onUpdateStatus,
  updatingId,
}: SiteRequestTableProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const filteredRequests = useMemo(() => {
    const sorted = [...requests].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    if (statusFilter === "all") return sorted;
    return sorted.filter((r) => r.status === statusFilter);
  }, [requests, statusFilter]);

  const totalPages = Math.ceil(filteredRequests.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const paginatedRequests = filteredRequests.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  
  const statusCounts = useMemo(() => {
    const counts: Record<string, number> = { all: requests.length };
    for (const status in statusConfig) {
      counts[status] = requests.filter(r => r.status === status).length;
    }
    return counts;
  }, [requests]);

  const formatRelativeDate = (date: string) => {
    try { return formatDistanceToNow(new Date(date), { addSuffix: true, locale: fr }); } 
    catch { return date; }
  };

  const formatDate = (date: string | null) => {
    if (!date) return "Date non précisée";
    try { return new Date(date).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric" }); } 
    catch { return date; }
  };

  return (
    <div className="space-y-4">
      <FilterControls 
        statusFilter={statusFilter}
        setStatusFilter={setStatusFilter}
        setCurrentPage={setCurrentPage}
        statusCounts={statusCounts}
      />

      <div className="rounded-md border bg-card overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Client</TableHead>
              <TableHead className="hidden sm:table-cell">Trajet</TableHead>
              <TableHead className="hidden lg:table-cell text-right">Soumis il y a</TableHead>
              <TableHead className="w-[150px] text-right">Statut</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedRequests.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="h-32 text-center text-muted-foreground">
                  Aucune demande trouvée pour ce statut.
                </TableCell>
              </TableRow>
            ) : (
              paginatedRequests.map((request) => {
                const isUpdating = updatingId === request.id;
                const origin = request.origin_city || "N/A";
                const destination = request.destination_city || "N/A";
                const contact = request.contact_info || "N/A";
                const isEmail = contact.includes('@');
                const ContactIcon = isEmail ? Mail : Phone;
                
                return (
                  <TableRow key={request.id} className={cn(isUpdating && "opacity-50")}>
                    <TableCell>
                      <div className="flex items-center gap-2.5">
                         <div className={cn("p-1.5 rounded-full border-2", isEmail ? "bg-blue-500/10 border-blue-500/20 text-blue-400" : "bg-green-500/10 border-green-500/20 text-green-400")}>
                          <ContactIcon className="w-3.5 h-3.5" />
                        </div>
                        <div className="flex flex-col">
                          <div className="font-medium text-foreground">{contact}</div>
                           <div className="font-semibold text-foreground uppercase text-xs sm:hidden mt-1">
                            {origin} ➜ {destination}
                          </div>
                        </div>
                      </div>
                    </TableCell>
                     <TableCell className="hidden sm:table-cell">
                      <div className="flex flex-col">
                        <div className="font-semibold text-foreground uppercase text-xs">
                          {origin} ➜ {destination}
                        </div>
                        <div className="text-muted-foreground text-xs flex items-center gap-1.5 mt-1">
                          <Calendar className="w-3 h-3" />
                          {formatDate(request.desired_date)}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="hidden lg:table-cell text-right text-muted-foreground text-sm">
                      {formatRelativeDate(request.created_at)}
                    </TableCell>
                    <TableCell className="text-right">
                      <Select
                        value={request.status}
                        onValueChange={(value) => onUpdateStatus(request.id, value as SiteTripRequestStatus)}
                        disabled={isUpdating}
                      >
                        <SelectTrigger className={cn("w-36 h-8 text-xs font-semibold border-2 transition-all",
                          isUpdating ? "bg-muted text-muted-foreground" : statusConfig[request.status].background,
                          isUpdating ? "border-muted" : statusConfig[request.status].color.replace('text-', 'border-')
                        )}>
                          {isUpdating ? <Loader2 className="w-4 h-4 animate-spin" /> : <SelectValue />}
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
                )
              })
            )}
          </TableBody>
        </Table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-end space-x-2 pt-4">
          <Button variant="outline" size="sm" onClick={() => setCurrentPage((p) => Math.max(1, p - 1))} disabled={currentPage === 1}>
            Précédent
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {currentPage} sur {totalPages}
          </span>
          <Button variant="outline" size="sm" onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages}>
            Suivant
          </Button>
        </div>
      )}
    </div>
  );
}
