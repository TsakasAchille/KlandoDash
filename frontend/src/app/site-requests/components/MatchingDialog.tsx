"use client";

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MapPin, Calendar, Globe, Sparkles, Loader2, RefreshCw, Phone, MessageSquare, Copy, Info } from "lucide-react";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { SiteTripRequest } from "@/types/site-request";
import { PublicTrip } from "../hooks/useSiteRequestAI";
import dynamic from "next/dynamic";

const ComparisonMap = dynamic(() => import("@/components/site-requests/comparison-map").then(mod => mod.ComparisonMap), { 
  ssr: false,
  loading: () => <div className="w-full h-[300px] rounded-2xl bg-muted/20 animate-pulse flex flex-col items-center justify-center space-y-3">
    <Loader2 className="w-8 h-8 text-klando-gold animate-spin" />
    <p className="text-[10px] font-black uppercase tracking-widest text-klando-dark">Chargement de la carte...</p>
  </div>
});

interface MatchingDialogProps {
  isOpen: boolean;
  onClose: () => void;
  selectedRequest: SiteTripRequest | null;
  aiLoading: boolean;
  isAiPending: boolean;
  aiMessage: string | null;
  matchedTrip: PublicTrip | null;
  processedComment: string;
  handleMatchIA: (force?: boolean) => void;
  localAiResult: string | null;
}

export function MatchingDialog({
  isOpen,
  onClose,
  selectedRequest,
  aiLoading,
  isAiPending,
  aiMessage,
  matchedTrip,
  processedComment,
  handleMatchIA,
  localAiResult
}: MatchingDialogProps) {
  if (!selectedRequest) return null;

  return (
    <Dialog open={isOpen} onOpenChange={(o) => { if(!o) onClose(); }}>
      <DialogContent aria-describedby={undefined} className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto bg-slate-50 border-border shadow-2xl p-0 gap-0">
        <div className="p-6 space-y-6">
          <DialogHeader className="flex flex-row items-center justify-between space-y-0 border-b border-border pb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-klando-gold/10 rounded-xl shadow-inner"><Sparkles className="w-5 h-5 text-klando-gold" /></div>
              <DialogTitle className="text-xl font-black uppercase tracking-tight text-klando-dark">Matching IA</DialogTitle>
            </div>
            {(localAiResult || selectedRequest?.ai_recommendation) && (
              <Button variant="ghost" size="sm" onClick={() => handleMatchIA(true)} disabled={aiLoading} className="h-8 text-[10px] font-black uppercase tracking-widest text-muted-foreground hover:text-klando-gold">
                <RefreshCw className={cn("w-3 h-3 mr-2", (aiLoading || isAiPending) && "animate-spin")} />
                Regénérer
              </Button>
            )}
          </DialogHeader>
          
          <div className="space-y-6">
            <div className="bg-white rounded-3xl p-6 border border-border relative overflow-hidden shadow-sm">
              <div className="absolute top-0 right-0 p-4 opacity-[0.03]"><Globe className="w-32 h-32 text-klando-dark" /></div>
              <div className="relative z-10">
                <div className="text-[10px] font-black uppercase tracking-[0.3em] text-klando-burgundy mb-2">Fiche Client</div>
                <div className="text-xl text-klando-dark font-black uppercase tracking-tight">{selectedRequest.origin_city} ➜ {selectedRequest.destination_city}</div>
                <div className="flex gap-5 mt-4 text-xs font-black text-slate-600">
                  <span className="flex items-center gap-2"><Phone className="w-4 h-4 text-klando-gold" /> {selectedRequest.contact_info}</span>
                  <span className="flex items-center gap-2"><Calendar className="w-4 h-4 text-klando-gold" /> {selectedRequest.desired_date ? format(new Date(selectedRequest.desired_date), "dd MMM yyyy", { locale: fr }) : "Dès que possible"}</span>
                </div>
              </div>
            </div>

            {/* MAP COMPARISON */}
            <ComparisonMap 
              originCity={selectedRequest.origin_city}
              destination_city={selectedRequest.destination_city}
              recommendedPolyline={matchedTrip?.polyline}
            />

            {/* PROPOSED TRIP BOX */}
            {!aiLoading && matchedTrip && (
              <Card className="border-2 border-klando-gold bg-klando-gold/5 overflow-hidden shadow-md animate-in zoom-in-95 duration-300">
                <div className="bg-klando-gold px-4 py-1.5 flex justify-between items-center">
                  <span className="text-[10px] font-black uppercase tracking-widest text-klando-dark">Trajet Proposé par l&apos;IA</span>
                  <Badge variant="outline" className="bg-white/20 border-white/40 text-klando-dark text-[9px] font-bold">MATCH TROUVÉ</Badge>
                </div>
                <CardContent className="p-4">
                  <div className="flex justify-between items-start">
                    <div className="space-y-3">
                      <div className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded-full bg-klando-gold/20 flex items-center justify-center">
                          <MapPin className="w-4 h-4 text-klando-gold" />
                        </div>
                        <div>
                          <div className="text-sm font-black uppercase text-klando-dark">
                            {matchedTrip.departure_city} ➜ {matchedTrip.arrival_city}
                          </div>
                          <div className="text-[10px] font-bold text-muted-foreground uppercase flex items-center gap-1.5 mt-0.5">
                            <Calendar className="w-3 h-3" />
                            {matchedTrip.departure_time ? format(new Date(matchedTrip.departure_time), "EEEE d MMMM 'à' HH:mm", { locale: fr }) : "Date inconnue"}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-[10px] font-black text-muted-foreground uppercase mb-1">Places</div>
                      <div className="text-xl font-black text-klando-gold leading-none">{matchedTrip.seats_available || "?"}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            <div className="space-y-6">
              {aiLoading ? (
                <div className="flex flex-col items-center justify-center py-20 bg-white rounded-3xl border border-dashed border-border space-y-6">
                  <Loader2 className="w-14 h-14 text-klando-gold animate-spin" />
                  <p className="text-sm font-black uppercase tracking-[0.2em] text-klando-gold animate-pulse">L&apos;IA analyse les trajets...</p>
                </div>
              ) : (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
                  <div className="bg-white rounded-3xl p-6 border border-border shadow-sm">
                    <div className="flex items-center gap-2 mb-4 text-blue-600">
                      <Info className="w-4 h-4" /><h4 className="text-[10px] font-black uppercase tracking-[0.2em]">Analyse Interne</h4>
                    </div>
                    <div className="prose prose-sm max-w-full text-slate-700 font-medium whitespace-pre-wrap">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{processedComment}</ReactMarkdown>
                    </div>
                  </div>

                  {aiMessage && (
                    <div className="bg-green-50 rounded-3xl p-6 border border-green-100 shadow-sm border-l-4 border-l-green-500">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2 text-green-700">
                          <MessageSquare className="w-4 h-4" /><h4 className="text-[10px] font-black uppercase tracking-[0.2em]">Message WhatsApp Prêt</h4>
                        </div>
                        <Button size="sm" variant="ghost" className="h-8 text-green-700 font-bold gap-2 text-[10px] uppercase hover:bg-green-100" onClick={() => { navigator.clipboard.writeText(aiMessage); toast.success("Copié !"); }}>
                          <Copy className="w-3.5 h-3.5" /> Copier
                        </Button>
                      </div>
                      <div className="bg-white/60 p-4 rounded-2xl border border-green-100 text-sm font-medium text-slate-800 leading-relaxed italic whitespace-pre-wrap">{aiMessage}</div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
