"use client";

import { useState, useMemo } from "react";
import { SiteTripRequest } from "@/types/site-request";
import { MarketingFlowStat } from "@/lib/queries/site-requests";
import { 
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow 
} from "@/components/ui/table";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  ChevronLeft, ChevronRight, Map as MapIcon, 
  History, TrendingUp, Calendar, ArrowUpRight, CheckCircle2, Clock
} from "lucide-react";
import dynamic from "next/dynamic";
import { cn } from "@/lib/utils";

const FlowMap = dynamic(() => import("../FlowMap"), { 
  ssr: false,
  loading: () => <div className="w-full h-[500px] rounded-[2rem] bg-slate-100 animate-pulse flex items-center justify-center">
    <MapIcon className="w-8 h-8 text-slate-300 animate-bounce" />
  </div>
});

interface RequestHistoryTabProps {
  requests: SiteTripRequest[];
  flowStats: MarketingFlowStat[];
}

const ITEMS_PER_PAGE = 10;

export function RequestHistoryTab({ requests, flowStats }: RequestHistoryTabProps) {
  const [currentPage, setCurrentPage] = useState(1);

  // Filtrer les demandes "Terminées" ou "Traitées" pour l'historique (Robuste à la casse)
  const historyRequests = useMemo(() => 
    requests.filter(r => ['VALIDATED', 'CONTACTED', 'REVIEWED'].includes(r.status.toUpperCase()))
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  , [requests]);

  const totalPages = Math.max(1, Math.ceil(historyRequests.length / ITEMS_PER_PAGE));
  const paginatedRequests = historyRequests.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      
      {/* 1. VISUALISATION MAP & FLOWS */}
      <div className="grid lg:grid-cols-12 gap-8">
        <div className="lg:col-span-8 space-y-4">
          <div className="flex items-center gap-3 px-2 text-left">
            <div className="p-2 bg-klando-gold/10 rounded-xl">
              <TrendingUp className="w-4 h-4 text-klando-gold" />
            </div>
            <h3 className="text-xs font-black uppercase tracking-[0.2em] text-white">Cartographie des Flux & Chaleur</h3>
          </div>
          <FlowMap stats={flowStats} />
        </div>

        <div className="lg:col-span-4 space-y-6">
          <div className="flex items-center gap-3 px-2 text-left">
            <div className="p-2 bg-blue-500/10 rounded-xl">
              <ArrowUpRight className="w-4 h-4 text-blue-500" />
            </div>
            <h3 className="text-xs font-black uppercase tracking-[0.2em] text-white">Top Trajets Demandés</h3>
          </div>
          
          <div className="space-y-3">
            {flowStats.length > 0 ? flowStats.slice(0, 6).map((stat, i) => (
              <Card key={i} className="bg-white border-slate-200 p-4 hover:border-klando-gold/50 transition-all group shadow-sm">
                <div className="flex justify-between items-center">
                  <div className="space-y-1 text-left">
                    <p className="text-[10px] font-black uppercase text-slate-900 tracking-tight group-hover:text-klando-burgundy transition-colors">
                      {stat.origin_city} ➜ {stat.destination_city}
                    </p>
                    <div className="flex items-center gap-2 text-[9px] font-bold text-slate-500 uppercase">
                      <Calendar className="w-2.5 h-2.5 text-klando-gold" /> Récurrent
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-xl font-black text-slate-900">{stat.request_count}</span>
                    <p className="text-[8px] font-black text-slate-500 uppercase tracking-widest">Demandes</p>
                  </div>
                </div>
              </Card>
            )) : (
                <div className="py-10 text-center text-[10px] font-bold uppercase text-white/20">Aucune donnée de flux</div>
            )}
          </div>
        </div>
      </div>

      {/* 2. TABLEAU D'HISTORIQUE PAGINÉ (MODE CLAIR) */}
      <div className="space-y-6">
        <div className="flex items-center justify-between px-2">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500/10 rounded-xl">
              <History className="w-4 h-4 text-green-500" />
            </div>
            <h3 className="text-xs font-black uppercase tracking-[0.2em] text-white">Journal des Demandes Traitées</h3>
          </div>
          <div className="text-[10px] font-black uppercase text-muted-foreground bg-white/5 px-3 py-1 rounded-full border border-white/10">
            {historyRequests.length} Archives
          </div>
        </div>

        <Card className="bg-white border-slate-200 overflow-hidden rounded-[2rem] shadow-xl">
          <Table>
            <TableHeader className="bg-slate-50">
              <TableRow className="border-slate-100 hover:bg-transparent">
                <TableHead className="text-[10px] font-black uppercase tracking-widest text-slate-500 py-5 pl-8">Date Soumission</TableHead>
                <TableHead className="text-[10px] font-black uppercase tracking-widest text-slate-500">Contact</TableHead>
                <TableHead className="text-[10px] font-black uppercase tracking-widest text-slate-500">Trajet & Date Prévue</TableHead>
                <TableHead className="text-right text-[10px] font-black uppercase tracking-widest text-slate-500 pr-8">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginatedRequests.length > 0 ? (
                paginatedRequests.map((req) => (
                  <TableRow key={req.id} className="border-slate-100 hover:bg-slate-50 transition-colors group">
                    <TableCell className="text-[11px] font-bold text-slate-500 py-4 tabular-nums pl-8">
                      {new Date(req.created_at).toLocaleString('fr-FR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}
                    </TableCell>
                    <TableCell>
                      <span className="text-xs font-black text-slate-900 uppercase">{req.contact_info}</span>
                    </TableCell>
                    <TableCell className="text-left">
                        <div className="flex flex-col">
                            <span className="text-xs font-black text-klando-burgundy uppercase tracking-tighter text-left">
                                {req.origin_city} ➜ {req.destination_city}
                            </span>
                            <span className="text-[9px] font-bold text-slate-400 uppercase flex items-center gap-1 mt-0.5">
                                <Clock className="w-2.5 h-2.5" /> 
                                {req.desired_date ? new Date(req.desired_date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'long' }) : "Dès que possible"}
                            </span>
                        </div>
                    </TableCell>
                    <TableCell className="text-right pr-8">
                      <div className={cn(
                        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full font-black text-[9px] uppercase tracking-widest shadow-sm border",
                        req.status.toUpperCase() === 'VALIDATED' ? "bg-green-50 border-green-100 text-green-600" : "bg-blue-50 border-blue-100 text-blue-600"
                      )}>
                        {req.status.toUpperCase() === 'VALIDATED' ? <CheckCircle2 className="w-3 h-3" /> : <Clock className="w-3 h-3" />}
                        {req.status}
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={4} className="h-40 text-center text-slate-300 font-black uppercase text-[10px] tracking-widest italic">
                    Aucun historique de demande trouvé
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="p-6 bg-slate-50 border-t border-slate-100 flex items-center justify-center gap-4">
              <Button 
                variant="outline" 
                size="icon" 
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="rounded-xl border-slate-200 hover:bg-white text-slate-600 h-9 w-9 shadow-sm"
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <div className="text-[10px] font-black uppercase tracking-widest text-slate-400">
                Page <span className="text-slate-900">{currentPage}</span> / {totalPages}
              </div>
              <Button 
                variant="outline" 
                size="icon" 
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="rounded-xl border-slate-200 hover:bg-white text-slate-600 h-9 w-9 shadow-sm"
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
