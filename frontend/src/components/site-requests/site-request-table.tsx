"use client";

import { useMemo, useEffect, useState } from "react";
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
import { Calendar, Phone, Mail, Sparkles, Loader2, ChevronLeft, ChevronRight, Hash, Radar, CheckCircle, Check, ArrowUpRight, Clock } from "lucide-react";
import { scanRequestMatchesAction } from "@/app/site-requests/actions";
import { toast } from "sonner";
import { ScanResultsDialog } from "@/app/site-requests/components/ScanResultsDialog";

interface SiteRequestTableProps {
  requests: SiteTripRequest[];
  onUpdateStatus: (id: string, status: SiteTripRequestStatus) => void;
  updatingId: string | null;
  currentPage: number;
  setCurrentPage: (p: number) => void;
  statusFilter: string;
  setStatusFilter: (v: string) => void;
  onOpenIA: (id: string) => void;
  onScan: (id: string) => void;
  onSelectOnMap?: (id: string) => void;
  scanningId: string | null;
  selectedId?: string;
}

const ITEMS_PER_PAGE = 10;

const statusConfig: Record<string, { label: string; color: string; background: string; }> = {
  NEW: { label: "Nouveau", color: "text-blue-400", background: "bg-blue-500/10" },
  REVIEWED: { label: "Examiné", color: "text-purple-400", background: "bg-purple-500/10" },
  CONTACTED: { label: "Contacté", color: "text-green-400", background: "bg-green-500/10" },
  IGNORED: { label: "Ignoré", color: "text-gray-400", background: "bg-gray-500/10" },
  VALIDATED: { label: "Validé", color: "text-green-600", background: "bg-green-600/10" },
};

export function SiteRequestTable({
  requests,
  onUpdateStatus,
  updatingId,
  currentPage,
  setCurrentPage,
  statusFilter,
  setStatusFilter,
  onOpenIA,
  onScan,
  onSelectOnMap,
  scanningId,
}: SiteRequestTableProps) {
  const [showOnlyUpcoming, setShowOnlyUpcoming] = useState(true); // Par défaut uniquement à venir

  // Stable Filter and Sort
  const filteredRequests = useMemo(() => {
    let result = [...requests];

    // 1. Filtrer par statut
    if (statusFilter !== "all") {
      result = result.filter((r) => r.status === statusFilter);
    }

    // 2. Filtrer par date (Si activé)
    if (showOnlyUpcoming) {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      // On garde si pas de date OU si date >= aujourd'hui
      result = result.filter(r => !r.desired_date || new Date(r.desired_date).getTime() >= today.getTime());
    }

    // 3. Trier par date de soumission (Plus récent en premier)
    return result.sort((a, b) => {
      const timeA = new Date(a.created_at).getTime();
      const timeB = new Date(b.created_at).getTime();
      return timeB - timeA;
    });
  }, [requests, statusFilter, showOnlyUpcoming]);

  const totalPages = Math.max(1, Math.ceil(filteredRequests.length / ITEMS_PER_PAGE));
  
  // Pagination safety
  useEffect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(totalPages);
    }
  }, [totalPages, currentPage, setCurrentPage]);

  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const paginatedRequests = filteredRequests.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  
  const statusCounts = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    // On calcule les compteurs en respectant le filtre de date actuel pour être cohérent
    const baseRequests = showOnlyUpcoming 
      ? requests.filter(r => !r.desired_date || new Date(r.desired_date).getTime() >= today.getTime())
      : requests;

    const counts: Record<string, number> = { all: baseRequests.length };
    Object.keys(statusConfig).forEach(status => {
      counts[status] = baseRequests.filter(r => r.status === status).length;
    });
    return counts;
  }, [requests, showOnlyUpcoming]);

  const formatRelativeDate = (date: string) => {
    try { return formatDistanceToNow(new Date(date), { addSuffix: true, locale: fr }); } 
    catch { return "Date inconnue"; }
  };

  const formatDate = (date: string | null) => {
    if (!date) return "Dès que possible";
    try { return new Date(date).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric" }); } 
    catch { return "Format invalide"; }
  };

  return (
    <div className="space-y-6 text-left">
      <div className="flex flex-col lg:flex-row gap-4 justify-between items-start lg:items-center">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 w-full lg:w-auto">
          <div className="hidden md:block">
            <Tabs value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setCurrentPage(1); }}>
              <TabsList className="bg-muted/50 p-1 h-auto">
                <TabsTrigger value="all" className="flex items-center gap-2">
                  Tous <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-background font-bold">{statusCounts.all}</span>
                </TabsTrigger>
                {Object.entries(statusConfig).map(([status, { label }]) => (
                  <TabsTrigger key={status} value={status} className="flex items-center gap-2">
                    {label} 
                    <span className={cn("text-[10px] px-1.5 py-0.5 rounded-full font-bold", statusConfig[status].background, statusConfig[status].color)}>
                      {statusCounts[status]}
                    </span>
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>
          </div>

          <Button
            variant={showOnlyUpcoming ? "default" : "outline"}
            size="sm"
            onClick={() => { setShowOnlyUpcoming(!showOnlyUpcoming); setCurrentPage(1); }}
            className={cn(
              "h-10 rounded-xl px-4 text-[10px] font-black uppercase tracking-widest gap-2 transition-all shadow-sm",
              showOnlyUpcoming ? "bg-klando-gold text-klando-dark hover:bg-klando-gold/90 border-transparent" : "border-slate-200 text-slate-500 hover:bg-slate-50"
            )}
          >
            <Clock className="w-3.5 h-3.5" />
            {showOnlyUpcoming ? "À venir uniquement" : "Tout afficher (Dates)"}
          </Button>
        </div>

        <div className="block md:hidden w-full text-left">
           <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setCurrentPage(1); }}>
            <SelectTrigger className="w-full font-bold text-xs uppercase bg-white border-slate-200">
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
        <div className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 bg-slate-50 px-3 py-1.5 rounded-full border border-slate-200 shadow-sm">
          {filteredRequests.length} prospect{filteredRequests.length > 1 ? 's' : ''}
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden relative min-h-[350px]">
        {updatingId && (
          <div className="absolute inset-0 bg-white/40 backdrop-blur-[1px] z-10 flex items-center justify-center">
            <Loader2 className="w-8 h-8 text-klando-gold animate-spin" />
          </div>
        )}
        <Table>
          <TableHeader>
            <TableRow className="bg-slate-50 hover:bg-slate-50 border-b border-slate-200">
              <TableHead className="font-bold py-4 text-slate-600">Client</TableHead>
              <TableHead className="hidden sm:table-cell font-bold text-slate-600 text-left">Trajet</TableHead>
              <TableHead className="hidden lg:table-cell text-right font-bold text-slate-600">Soumis il y a</TableHead>
              <TableHead className="w-[180px] text-right font-bold text-slate-600">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedRequests.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="h-60 text-center text-slate-300 opacity-40 font-medium">
                  <div className="flex flex-col items-center justify-center space-y-2">
                    <Hash className="w-10 h-10" /><p className="font-bold uppercase tracking-widest text-xs text-center">Aucune demande</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              paginatedRequests.map((request) => {
                const contact = request.contact_info || "N/A";
                const isEmail = contact.includes('@');
                const ContactIcon = isEmail ? Mail : Phone;
                return (
                  <TableRow key={request.id} className="transition-colors group hover:bg-slate-50 border-b border-slate-100 last:border-0">
                    <TableCell className="py-4">
                      <div className="flex items-center gap-3 min-w-0">
                         <div className={cn("p-2 rounded-xl border shadow-sm transition-transform group-hover:scale-110", isEmail ? "bg-blue-50 text-blue-500 border-blue-100" : "bg-green-50 text-green-600 border-green-100")}>
                          <ContactIcon className="w-4 h-4" />
                        </div>
                        <div className="flex flex-col min-w-0 text-left">
                          <div className="font-bold text-slate-900 truncate">{contact}</div>
                           <div className="font-black uppercase text-[10px] sm:hidden mt-1 text-klando-gold truncate text-left">
                            {request.origin_city} ➜ {request.destination_city}
                          </div>
                        </div>
                      </div>
                    </TableCell>
                     <TableCell className="hidden sm:table-cell text-left">
                      <div className="flex flex-col text-left">
                        <div className="flex items-center gap-2">
                          <div className="font-black text-slate-900 uppercase text-xs tracking-tight text-left">{request.origin_city} ➜ {request.destination_city}</div>
                          {request.matches && request.matches.length > 0 && (
                            <div className="flex items-center gap-1 text-[8px] font-black text-green-600 uppercase bg-green-50 px-1.5 py-0.5 rounded-full border border-green-100 shadow-sm">
                              <Sparkles className="w-2 h-2" />
                              {request.matches.length}
                            </div>
                          )}
                        </div>
                        <div className="text-slate-400 text-[10px] flex items-center gap-1.5 mt-1 font-bold text-left">
                          <Calendar className="w-3 h-3 text-klando-gold" /> {formatDate(request.desired_date)}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="hidden lg:table-cell text-right text-slate-400 text-[10px] font-bold uppercase tracking-tight italic text-right">
                      {formatRelativeDate(request.created_at)}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex flex-col items-end gap-2 text-right">
                        <div className={cn("px-2 py-0.5 rounded-full text-[8px] font-black uppercase tracking-widest border shadow-sm", statusConfig[request.status].background, statusConfig[request.status].color, statusConfig[request.status].color.replace('text-', 'border-'))}>
                          {statusConfig[request.status].label}
                        </div>

                        {request.status === 'VALIDATED' ? (
                          <div className="text-green-600 font-black uppercase text-[10px] pr-2 flex items-center gap-1.5 text-right font-black">
                            <CheckCircle className="w-3.5 h-3.5" /> Terminé
                          </div>
                        ) : (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onSelectOnMap?.(request.id)}
                            className="h-9 rounded-xl border-slate-200 hover:border-klando-gold hover:bg-klando-gold/5 text-slate-600 hover:text-klando-gold font-black text-[10px] uppercase tracking-widest group transition-all shadow-sm"
                          >
                            Traiter sur la Carte
                            <ArrowUpRight className="w-3.5 h-3.5 ml-2 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                )
              })
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex flex-col sm:flex-row items-center justify-center gap-4 py-4">
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" onClick={() => setCurrentPage(Math.max(1, currentPage - 1))} disabled={currentPage === 1} className="h-9 w-9 rounded-xl border-slate-200 text-slate-600 shadow-sm"><ChevronLeft className="h-4 w-4" /></Button>
          <div className="flex items-center gap-1.5 px-4 py-1.5 bg-white rounded-2xl border border-slate-200 text-xs font-black uppercase tracking-tighter shadow-sm">
            Page <span className="text-sm font-black text-slate-900 mx-1">{currentPage}</span> / <span className="text-sm font-black text-slate-400 mx-1">{totalPages}</span>
          </div>
          <Button variant="outline" size="icon" onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))} disabled={currentPage === totalPages} className="h-9 w-9 rounded-xl border-slate-200 text-slate-600 shadow-sm"><ChevronRight className="h-4 w-4" /></Button>
        </div>
      </div>
    </div>
  );
}
