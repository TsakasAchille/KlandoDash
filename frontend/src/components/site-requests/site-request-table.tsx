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
import { Calendar, Phone, Mail, Sparkles, Loader2, ChevronLeft, ChevronRight, Hash, Radar } from "lucide-react";
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
}

const ITEMS_PER_PAGE = 10;

const statusConfig: Record<SiteTripRequestStatus, { label: string; color: string; background: string; }> = {
  NEW: { label: "Nouveau", color: "text-blue-400", background: "bg-blue-500/10" },
  REVIEWED: { label: "Examiné", color: "text-purple-400", background: "bg-purple-500/10" },
  CONTACTED: { label: "Contacté", color: "text-green-400", background: "bg-green-500/10" },
  IGNORED: { label: "Ignoré", color: "text-gray-400", background: "bg-gray-500/10" },
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
}: SiteRequestTableProps) {
  const [scanningId, setScanningId] = useState<string | null>(null);
  const [scanResults, setScanResults] = useState<any>(null);
  const [showScanDialog, setShowScanDialog] = useState(false);

  // Stable Filter and Sort
  const filteredRequests = useMemo(() => {
    const sorted = [...requests].sort((a, b) => {
      // Priorité à la date de soumission (created_at) - Plus récent en premier
      const timeA = new Date(a.created_at).getTime();
      const timeB = new Date(b.created_at).getTime();
      if (timeB !== timeA) return timeB - timeA;
      
      return b.id.localeCompare(a.id);
    });
    
    if (statusFilter === "all") return sorted;
    return sorted.filter((r) => r.status === statusFilter);
  }, [requests, statusFilter]);

  const totalPages = Math.max(1, Math.ceil(filteredRequests.length / ITEMS_PER_PAGE));
  
  // Pagination safety
  useEffect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(totalPages);
    }
  }, [totalPages, currentPage, setCurrentPage]);

  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const paginatedRequests = filteredRequests.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  
  const handleScan = async (id: string, radius: number = 5) => {
    setScanningId(id);
    try {
      const result = await scanRequestMatchesAction(id, radius);
      setScanResults(result);
      setShowScanDialog(true);
      if (result.success && result.count > 0) {
        toast.success(result.message);
      }
    } catch (error) {
      toast.error("Erreur lors du scan.");
    } finally {
      setScanningId(null);
    }
  };

  const statusCounts = useMemo(() => {
    const counts: Record<string, number> = { all: requests.length };
    for (const status in statusConfig) {
      counts[status] = requests.filter(r => r.status === status).length;
    }
    return counts;
  }, [requests]);

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
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
        <div className="hidden md:block">
          <Tabs value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setCurrentPage(1); }}>
            <TabsList className="bg-muted/50 p-1 h-auto">
              <TabsTrigger value="all" className="flex items-center gap-2">
                Tous <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-background font-bold">{statusCounts.all}</span>
              </TabsTrigger>
              {Object.entries(statusConfig).map(([status, { label }]) => (
                <TabsTrigger key={status} value={status} className="flex items-center gap-2">
                  {label} 
                  <span className={cn("text-[10px] px-1.5 py-0.5 rounded-full font-bold", statusConfig[status as SiteTripRequestStatus].background, statusConfig[status as SiteTripRequestStatus].color)}>
                    {statusCounts[status]}
                  </span>
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>
        </div>
        <div className="block md:hidden w-full">
           <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setCurrentPage(1); }}>
            <SelectTrigger className="w-full font-bold text-xs uppercase">
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
        <div className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground bg-muted/30 px-3 py-1.5 rounded-full border border-border/50">
          {filteredRequests.length} demande{filteredRequests.length > 1 ? 's' : ''}
        </div>
      </div>

      <div className="rounded-xl border bg-card shadow-sm overflow-hidden relative min-h-[350px]">
        {updatingId && (
          <div className="absolute inset-0 bg-white/40 backdrop-blur-[1px] z-10 flex items-center justify-center">
            <Loader2 className="w-8 h-8 text-klando-gold animate-spin" />
          </div>
        )}
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/30 hover:bg-muted/30">
              <TableHead className="font-bold py-4">Client</TableHead>
              <TableHead className="hidden sm:table-cell font-bold">Trajet</TableHead>
              <TableHead className="hidden lg:table-cell text-right font-bold">Soumis il y a</TableHead>
              <TableHead className="w-[180px] text-right font-bold">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedRequests.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="h-60 text-center text-muted-foreground opacity-40">
                  <div className="flex flex-col items-center justify-center space-y-2">
                    <Hash className="w-10 h-10" /><p className="font-bold uppercase tracking-widest text-xs">Aucune demande</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              paginatedRequests.map((request) => {
                const contact = request.contact_info || "N/A";
                const isEmail = contact.includes('@');
                const ContactIcon = isEmail ? Mail : Phone;
                return (
                  <TableRow key={request.id} className="transition-colors group hover:bg-muted/20">
                    <TableCell className="py-4">
                      <div className="flex items-center gap-3 min-w-0">
                         <div className={cn("p-2 rounded-xl border shadow-sm", isEmail ? "bg-blue-50 text-blue-500 border-blue-100" : "bg-green-50 text-green-600 border-green-100")}>
                          <ContactIcon className="w-4 h-4" />
                        </div>
                        <div className="flex flex-col min-w-0">
                          <div className="font-bold text-foreground truncate">{contact}</div>
                           <div className="font-black uppercase text-[10px] sm:hidden mt-1 text-klando-gold truncate">
                            {request.origin_city} ➜ {request.destination_city}
                          </div>
                        </div>
                      </div>
                    </TableCell>
                     <TableCell className="hidden sm:table-cell">
                      <div className="flex flex-col">
                        <div className="font-black text-klando-dark uppercase text-xs tracking-tight">{request.origin_city} ➜ {request.destination_city}</div>
                        <div className="text-muted-foreground text-[10px] flex items-center gap-1.5 mt-1 font-bold">
                          <Calendar className="w-3 h-3" /> {formatDate(request.desired_date)}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="hidden lg:table-cell text-right text-muted-foreground text-[10px] font-bold uppercase tracking-tight italic">
                      {formatRelativeDate(request.created_at)}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex flex-col items-end gap-2">
                        <Select value={request.status} onValueChange={(v) => onUpdateStatus(request.id, v as SiteTripRequestStatus)}>
                          <SelectTrigger className={cn("w-36 h-8 text-[10px] font-black uppercase tracking-wider border-2 shadow-sm", statusConfig[request.status].background, statusConfig[request.status].color.replace('text-', 'border-'))}>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {Object.entries(statusConfig).map(([status, { label }]) => (
                              <SelectItem key={status} value={status} className="text-[10px] font-black uppercase">{label}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <div className="flex gap-2">
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => handleScan(request.id)} 
                            disabled={scanningId === request.id}
                            className="h-8 w-8 p-0 border-blue-200 bg-blue-50 text-blue-600 hover:bg-blue-100"
                            title="Scanner les trajets proches"
                          >
                            {scanningId === request.id ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Radar className="w-3.5 h-3.5" />}
                          </Button>
                          <Button variant="outline" size="sm" onClick={() => onOpenIA(request.id)} className={cn("gap-2 border-klando-gold/30 text-[10px] font-black uppercase tracking-widest px-3 h-8 shadow-sm", request.ai_recommendation ? "bg-green-50 text-green-600 border-green-200" : "bg-klando-gold/5 text-klando-gold")}>
                            <Sparkles className="w-3 h-3" /> {request.ai_recommendation ? "Aide IA ✓" : "Aide IA"}
                          </Button>
                        </div>
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
          <Button variant="outline" size="icon" onClick={() => setCurrentPage(Math.max(1, currentPage - 1))} disabled={currentPage === 1} className="h-9 w-9 rounded-xl"><ChevronLeft className="h-4 w-4" /></Button>
          <div className="flex items-center gap-1.5 px-4 py-1.5 bg-muted/30 rounded-2xl border text-xs font-black uppercase tracking-tighter">
            Page <span className="text-sm font-black text-klando-dark mx-1">{currentPage}</span> / <span className="text-sm font-black text-muted-foreground/60 mx-1">{totalPages}</span>
          </div>
          <Button variant="outline" size="icon" onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))} disabled={currentPage === totalPages} className="h-9 w-9 rounded-xl"><ChevronRight className="h-4 w-4" /></Button>
        </div>
      </div>

      <ScanResultsDialog 
        isOpen={showScanDialog}
        onClose={() => setShowScanDialog(false)}
        results={scanResults}
        onRetry={() => {
          if (scanResults?.diagnostics?.origin) {
            const req = requests.find(r => r.origin_city === scanResults.diagnostics.origin);
            if (req) handleScan(req.id, 15);
          }
        }}
      />
    </div>
  );
}
