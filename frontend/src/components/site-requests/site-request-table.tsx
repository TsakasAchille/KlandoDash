"use client";

import { useState, useMemo, useEffect, useTransition } from "react";
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
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Calendar, Phone, Mail, Sparkles, Loader2, MessageSquare, RefreshCw, ChevronLeft, ChevronRight, Hash, Globe, Copy, Info } from "lucide-react";
import { getAIMatchingAction } from "@/app/site-requests/actions";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { toast } from "sonner";

interface SiteRequestTableProps {
  requests: SiteTripRequest[];
  onUpdateStatus: (id: string, status: SiteTripRequestStatus) => void;
  updatingId: string | null;
  currentPage: number;
  setCurrentPage: (p: number) => void;
  statusFilter: string;
  setStatusFilter: (v: string) => void;
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
}: SiteRequestTableProps) {
  const [selectedRequestId, setSelectedRequestId] = useState<string | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [localAiResult, setLocalAiResult] = useState<string | null>(null);
  const [isAiPending, startAiTransition] = useTransition();

  // 1. Stable Sort and Filter
  const filteredRequests = useMemo(() => {
    const sorted = [...requests].sort((a, b) => {
      const timeA = new Date(a.created_at).getTime();
      const timeB = new Date(b.created_at).getTime();
      if (timeB !== timeA) return timeB - timeA;
      return b.id.localeCompare(a.id);
    });
    
    if (statusFilter === "all") return sorted;
    return sorted.filter((r) => r.status === statusFilter);
  }, [requests, statusFilter]);

  const totalPages = Math.max(1, Math.ceil(filteredRequests.length / ITEMS_PER_PAGE));
  
  // 2. Resilient selected request tracking
  const selectedRequest = useMemo(() => 
    selectedRequestId ? requests.find(r => r.id === selectedRequestId) : null
  , [requests, selectedRequestId]);

  // 3. Pagination safety
  useEffect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(totalPages);
    }
  }, [totalPages, currentPage, setCurrentPage]);

  // 4. Sync local state when selected request changes OR data updates
  useEffect(() => {
    if (selectedRequest?.ai_recommendation) {
      setLocalAiResult(selectedRequest.ai_recommendation);
    }
  }, [selectedRequest?.ai_recommendation, selectedRequestId]);

  const handleMatch = async (force = false) => {
    if (!selectedRequest) return;
    
    setAiLoading(true);
    startAiTransition(async () => {
      try {
        const res = await getAIMatchingAction(
          selectedRequest.id, 
          selectedRequest.origin_city, 
          selectedRequest.destination_city, 
          selectedRequest.desired_date,
          force
        );
        if (res.success) {
          setLocalAiResult(res.text || null);
        } else {
          toast.error(res.message || "Erreur lors de la génération.");
        }
      } catch (err) {
        console.error(err);
        toast.error("Une erreur est survenue lors de l'appel à l'IA.");
      } finally {
        setAiLoading(false);
      }
    });
  };

  // 5. Auto-trigger AI if needed
  useEffect(() => {
    if (selectedRequestId && selectedRequest && !selectedRequest.ai_recommendation && !aiLoading && !localAiResult) {
      handleMatch(false);
    }
  }, [selectedRequestId, selectedRequest?.id]);

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
    catch { return "Date inconnue"; }
  };

  const formatDate = (date: string | null) => {
    if (!date) return "Dès que possible";
    try { return new Date(date).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric" }); } 
    catch { return "Format invalide"; }
  };

  const lastAiUpdate = selectedRequest?.ai_updated_at 
    ? formatDistanceToNow(new Date(selectedRequest.ai_updated_at), { addSuffix: true, locale: fr })
    : null;

  // 6. Split result into Comment and Message
  const { aiComment, aiMessage } = useMemo(() => {
    const raw = localAiResult || selectedRequest?.ai_recommendation;
    if (!raw) return { aiComment: null, aiMessage: null };

    // Support both old format and new tag-based format
    if (raw.includes('[MESSAGE]')) {
      const parts = raw.split('[MESSAGE]');
      const comment = parts[0].replace('[COMMENTAIRE]', '').trim();
      const message = parts[1]?.trim() || '';
      return { aiComment: comment, aiMessage: message };
    }

    // Fallback for old records: put everything in comment if no obvious split
    return { aiComment: raw, aiMessage: null };
  }, [localAiResult, selectedRequest?.ai_recommendation]);

  // Format markdown for internal comments
  const formattedComment = useMemo(() => {
    if (!aiComment) return "_Aucune analyse disponible._";
    return aiComment.replace(/([^ \n])\n([^ \n])/g, '$1  \n$2');
  }, [aiComment]);

  return (
    <div className="space-y-6">
      {/* Filters Header */}
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

      {/* Table Section */}
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
                <TableCell colSpan={4} className="h-60 text-center">
                  <div className="flex flex-col items-center justify-center space-y-2 opacity-40">
                    <Hash className="w-10 h-10" />
                    <p className="font-bold uppercase tracking-widest text-xs">Aucune demande trouvée</p>
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
                      <div className="flex items-center gap-3">
                         <div className={cn("p-2 rounded-xl border shadow-sm transition-transform group-hover:scale-110", isEmail ? "bg-blue-50 text-blue-500 border-blue-100" : "bg-green-50 text-green-600 border-green-100")}>
                          <ContactIcon className="w-4 h-4" />
                        </div>
                        <div className="flex flex-col min-w-0">
                          <div className="font-bold text-foreground truncate max-w-[150px] sm:max-w-none">{contact}</div>
                           <div className="font-bold uppercase text-[10px] sm:hidden mt-1 text-klando-gold truncate font-black">
                            {request.origin_city} ➜ {request.destination_city}
                          </div>
                        </div>
                      </div>
                    </TableCell>
                     <TableCell className="hidden sm:table-cell">
                      <div className="flex flex-col">
                        <div className="font-black text-klando-dark uppercase text-xs tracking-tight">
                          {request.origin_city} ➜ {request.destination_city}
                        </div>
                        <div className="text-muted-foreground text-[10px] flex items-center gap-1.5 mt-1 font-bold">
                          <Calendar className="w-3 h-3" />
                          {formatDate(request.desired_date)}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="hidden lg:table-cell text-right text-muted-foreground text-[10px] font-bold uppercase tracking-tight italic">
                      {formatRelativeDate(request.created_at)}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex flex-col items-end gap-2">
                        <Select
                          value={request.status}
                          onValueChange={(value) => onUpdateStatus(request.id, value as SiteTripRequestStatus)}
                        >
                          <SelectTrigger className={cn("w-36 h-8 text-[10px] font-black uppercase tracking-wider border-2 transition-all shadow-sm",
                            statusConfig[request.status].background,
                            statusConfig[request.status].color.replace('text-', 'border-')
                          )}>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {Object.entries(statusConfig).map(([status, { label }]) => (
                              <SelectItem key={status} value={status} className="text-[10px] font-black uppercase">
                                {label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => setSelectedRequestId(request.id)}
                          className={cn(
                            "gap-2 border-klando-gold/30 hover:border-klando-gold text-[10px] font-black uppercase tracking-widest px-3 h-8 transition-all shadow-sm",
                            request.ai_recommendation ? "bg-green-50 text-green-600 border-green-200" : "bg-klando-gold/5 text-klando-gold"
                          )}
                        >
                          <Sparkles className="w-3 h-3" />
                          {request.ai_recommendation ? "Aide IA ✓" : "Aide IA"}
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                )
              })
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination Controls */}
      {filteredRequests.length > 0 && (
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 py-4">
          <div className="flex items-center gap-2">
            <Button 
              variant="outline" 
              size="icon" 
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))} 
              disabled={currentPage === 1}
              className="h-9 w-9 rounded-xl border-border hover:bg-muted"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            
            <div className="flex items-center gap-1.5 px-4 py-1.5 bg-muted/30 rounded-2xl border border-border/50 shadow-inner">
              <span className="text-[10px] font-black uppercase text-muted-foreground tracking-tighter">Page</span>
              <span className="text-sm font-black text-klando-dark">{currentPage}</span>
              <span className="text-xs font-bold text-muted-foreground/40 mx-0.5">/</span>
              <span className="text-sm font-black text-muted-foreground/60">{totalPages}</span>
            </div>

            <Button 
              variant="outline" 
              size="icon" 
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))} 
              disabled={currentPage === totalPages}
              className="h-9 w-9 rounded-xl border-border hover:bg-muted"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
          
          {totalPages > 1 && (
            <div className="flex gap-1">
              {[...Array(totalPages)].map((_, i) => {
                const pageNum = i + 1;
                if (pageNum === 1 || pageNum === totalPages || Math.abs(pageNum - currentPage) <= 1) {
                  return (
                    <Button
                      key={pageNum}
                      variant={currentPage === pageNum ? "default" : "ghost"}
                      size="sm"
                      onClick={() => setCurrentPage(pageNum)}
                      className={cn("h-8 w-8 text-[10px] font-black rounded-lg transition-all", 
                        currentPage === pageNum ? "bg-klando-dark text-white scale-110 shadow-md" : "text-muted-foreground"
                      )}
                    >
                      {pageNum}
                    </Button>
                  );
                }
                if (Math.abs(pageNum - currentPage) === 2) {
                  return <span key={pageNum} className="text-muted-foreground/40 text-[10px]">.</span>;
                }
                return null;
              })}
            </div>
          )}
        </div>
      )}

      {/* Structured Dialog */}
      <Dialog 
        open={!!selectedRequestId} 
        onOpenChange={(open) => {
          if (!open) {
            setSelectedRequestId(null);
            setLocalAiResult(null);
          }
        }}
      >
        <DialogContent aria-describedby={undefined} className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto bg-slate-50 border-border shadow-2xl p-0 gap-0">
          <div className="p-6 space-y-6">
            <DialogHeader className="flex flex-row items-center justify-between space-y-0 border-b border-border pb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-klando-gold/10 rounded-xl shadow-inner">
                  <Sparkles className="w-5 h-5 text-klando-gold" />
                </div>
                <DialogTitle className="text-xl font-black uppercase tracking-tight text-klando-dark">
                  Matching IA
                </DialogTitle>
              </div>
              
              {(localAiResult || selectedRequest?.ai_recommendation) && (
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => handleMatch(true)} 
                  disabled={aiLoading}
                  className="h-8 text-[10px] font-black uppercase tracking-widest text-muted-foreground hover:text-klando-gold hover:bg-klando-gold/5"
                >
                  <RefreshCw className={cn("w-3 h-3 mr-2", (aiLoading || isAiPending) && "animate-spin")} />
                  Regénérer
                </Button>
              )}
            </DialogHeader>
            
            <div className="space-y-6">
              {/* Client Info Card */}
              <div className="bg-white rounded-3xl p-6 border border-border relative overflow-hidden shadow-sm">
                <div className="absolute top-0 right-0 p-4 opacity-[0.03]">
                  <Globe className="w-32 h-32 text-klando-dark" />
                </div>
                <div className="relative z-10">
                  <div className="flex justify-between items-start mb-4">
                    <div className="text-[10px] font-black uppercase tracking-[0.3em] text-klando-burgundy">Fiche Client</div>
                    {(lastAiUpdate || localAiResult) && !aiLoading && (
                      <div className="text-[9px] font-black text-muted-foreground uppercase tracking-widest bg-muted px-3 py-1 rounded-full border border-border/40">
                        Analyse {lastAiUpdate || "tout juste générée"}
                      </div>
                    )}
                  </div>
                  <div className="text-xl text-klando-dark font-black uppercase tracking-tight">
                    {selectedRequest?.origin_city} ➜ {selectedRequest?.destination_city}
                  </div>
                  <div className="flex flex-wrap gap-5 mt-4">
                    <div className="text-xs text-slate-600 font-black flex items-center gap-2">
                      <Phone className="w-4 h-4 text-klando-gold" /> {selectedRequest?.contact_info}
                    </div>
                    <div className="text-xs text-slate-600 font-black flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-klando-gold" /> {formatDate(selectedRequest?.desired_date || null)}
                    </div>
                  </div>
                </div>
              </div>

              {/* Main Result Area */}
              <div className="space-y-6">
                {aiLoading ? (
                  <div className="flex flex-col items-center justify-center py-20 bg-white rounded-3xl border border-dashed border-border space-y-6 shadow-inner">
                    <div className="relative">
                      <div className="absolute inset-0 bg-klando-gold/20 blur-xl rounded-full animate-pulse" />
                      <Loader2 className="w-14 h-14 text-klando-gold animate-spin relative z-10" />
                      <Sparkles className="w-6 h-6 text-klando-gold absolute -top-2 -right-2 animate-bounce" />
                    </div>
                    <div className="text-center space-y-2">
                      <p className="text-sm font-black uppercase tracking-[0.2em] text-klando-gold animate-pulse">L&apos;IA analyse les trajets...</p>
                      <p className="text-[10px] text-muted-foreground font-black uppercase tracking-widest italic">Optimisation du matching en cours</p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
                    {/* Part 1: internal analysis */}
                    <div className="bg-white rounded-3xl p-6 border border-border shadow-sm">
                      <div className="flex items-center gap-2 mb-4">
                        <div className="p-1.5 bg-blue-50 text-blue-600 rounded-lg">
                          <Info className="w-4 h-4" />
                        </div>
                        <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-blue-600">Analyse Interne</h4>
                      </div>
                      <div className="prose prose-sm max-w-full prose-p:leading-relaxed prose-li:my-2 prose-strong:text-klando-burgundy prose-strong:font-black prose-headings:text-klando-dark prose-headings:font-black text-slate-700 font-medium break-words overflow-x-hidden whitespace-pre-wrap">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {formattedComment}
                        </ReactMarkdown>
                      </div>
                    </div>

                    {/* Part 2: copyable message */}
                    {aiMessage && (
                      <div className="bg-green-50 rounded-3xl p-6 border border-green-100 shadow-sm border-l-4 border-l-green-500">
                        <div className="flex items-center justify-between gap-2 mb-4">
                          <div className="flex items-center gap-2">
                            <div className="p-1.5 bg-green-100 text-green-600 rounded-lg">
                              <MessageSquare className="w-4 h-4" />
                            </div>
                            <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-green-700">Message WhatsApp Prêt</h4>
                          </div>
                          <Button 
                            size="sm" 
                            variant="ghost" 
                            className="h-8 text-green-700 hover:bg-green-100 font-bold gap-2 text-[10px] uppercase"
                            onClick={() => {
                              navigator.clipboard.writeText(aiMessage);
                              toast.success("Message copié !");
                            }}
                          >
                            <Copy className="w-3.5 h-3.5" />
                            Copier
                          </Button>
                        </div>
                        <div className="bg-white/60 p-4 rounded-2xl border border-green-100 text-sm font-medium text-slate-800 leading-relaxed italic whitespace-pre-wrap">
                          {aiMessage}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Actions Footer */}
            {!aiLoading && aiMessage && (
              <div className="flex justify-end pt-6 border-t border-border mt-4">
                <Button 
                  size="lg" 
                  className="bg-klando-burgundy hover:bg-klando-burgundy/90 text-white gap-3 font-black uppercase tracking-widest px-10 h-14 rounded-2xl shadow-xl shadow-klando-burgundy/20 transition-all hover:scale-[1.02] active:scale-95" 
                  onClick={() => {
                    navigator.clipboard.writeText(aiMessage);
                    toast.success("Message copié avec succès !");
                  }}
                >
                  <MessageSquare className="w-5 h-5" />
                  Copier le message WhatsApp
                </Button>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
