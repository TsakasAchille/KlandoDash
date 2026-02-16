"use client";

import { useState, useTransition, useEffect, useMemo, useCallback } from "react";
import { SiteTripRequest, SiteTripRequestStatus } from "@/types/site-request";
import { SiteRequestTable } from "@/components/site-requests/site-request-table";
import { updateRequestStatusAction, getAIMatchingAction } from "./actions";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { MapPin, Calendar, CheckCircle2, Globe, Sparkles, Loader2, RefreshCw, Phone, MessageSquare, Copy, Info } from "lucide-react";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import dynamic from "next/dynamic";

const ComparisonMap = dynamic(() => import("@/components/site-requests/comparison-map").then(mod => mod.ComparisonMap), { 
  ssr: false,
  loading: () => <div className="w-full h-[300px] rounded-2xl bg-muted/20 animate-pulse flex flex-col items-center justify-center space-y-3">
    <Loader2 className="w-8 h-8 text-klando-gold animate-spin" />
    <p className="text-[10px] font-black uppercase tracking-widest text-klando-dark">Chargement de la carte...</p>
  </div>
});

interface PublicTrip {
  id: string;
  departure_city: string;
  arrival_city: string;
  departure_time: string;
  seats_available?: number;
  polyline?: string | null;
}

interface SiteRequestsClientProps {
  initialRequests: SiteTripRequest[];
  publicPending: PublicTrip[];
  publicCompleted: PublicTrip[];
}

export function SiteRequestsClient({ initialRequests, publicPending, publicCompleted }: SiteRequestsClientProps) {
  const [requests, setRequests] = useState<SiteTripRequest[]>(initialRequests);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  
  // AI Matching States
  const [selectedRequestId, setSelectedRequestId] = useState<string | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [localAiResult, setLocalAiResult] = useState<string | null>(null);
  const [actionMatchedTrip, setActionMatchedTrip] = useState<PublicTrip | null>(null);
  const [lastFetchedTripId, setLastFetchedTripId] = useState<string | null>(null);
  const [isAiPending, startAiTransition] = useTransition();
  const [, startTransition] = useTransition();

  // Sync state with props when server re-renders
  useEffect(() => {
    setRequests(initialRequests);
  }, [initialRequests]);

  const selectedRequest = useMemo(() => 
    selectedRequestId ? requests.find(r => r.id === selectedRequestId) : null
  , [requests, selectedRequestId]);

  // Reset matched trip when changing selection
  useEffect(() => {
    setActionMatchedTrip(null);
    setLastFetchedTripId(null);
  }, [selectedRequestId]);

  // Sync local AI result when data updates from server
  useEffect(() => {
    if (selectedRequest?.ai_recommendation) {
      setLocalAiResult(selectedRequest.ai_recommendation);
    }
  }, [selectedRequest?.ai_recommendation]);

  const handleUpdateStatus = (id: string, status: SiteTripRequestStatus) => {
    setUpdatingId(id);
    startTransition(async () => {
      setRequests(prev => prev.map(r => (r.id === id ? { ...r, status } : r)));
      const result = await updateRequestStatusAction(id, status);
      if (!result.success) {
        toast.error(result.message || "Erreur lors de la mise à jour.");
        setRequests(initialRequests); 
      }
      setUpdatingId(null);
    });
  };

  const handleMatchIA = useCallback(async (force = false) => {
    if (!selectedRequest) return;
    
    setAiLoading(true);
    setLastFetchedTripId(selectedRequest.id);
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
          console.log("Server Matched Trip Data:", res.matchedTrip);
          if (res.matchedTrip) {
            setActionMatchedTrip(res.matchedTrip as PublicTrip);
          }
        } else {
          toast.error(res.message || "Erreur IA");
        }
      } catch {
        toast.error("Erreur de connexion IA");
      } finally {
        setAiLoading(false);
      }
    });
  }, [selectedRequest]);

  // Auto-trigger AI if opening a request with no analysis
  useEffect(() => {
    if (selectedRequestId && selectedRequest && !selectedRequest.ai_recommendation && !aiLoading && !localAiResult) {
      handleMatchIA(false);
    }
  }, [selectedRequestId, selectedRequest, aiLoading, localAiResult, handleMatchIA]);

  // Also trigger fetch if we have an AI recommendation but haven't fetched details yet
  useEffect(() => {
    if (selectedRequestId && selectedRequest?.ai_recommendation && !aiLoading && lastFetchedTripId !== selectedRequestId) {
      handleMatchIA(false); // This will use cache but fetch the trip details
    }
  }, [selectedRequestId, selectedRequest?.ai_recommendation, aiLoading, lastFetchedTripId, handleMatchIA]);

      // Parsing AI result
    const { aiComment, aiMessage, matchedTripId } = useMemo(() => {
      const raw = localAiResult || selectedRequest?.ai_recommendation;
      if (!raw) return { aiComment: null, aiMessage: null, matchedTripId: null };
      
      let comment = raw;
      let message = null;
      let tripId = null;
  
      if (raw.includes('[MESSAGE]')) {
        const parts = raw.split('[MESSAGE]');
        comment = parts[0].replace('[COMMENTAIRE]', '').trim();
        message = parts[1]?.trim() || '';
      }
  
      if (comment.includes('[TRIP_ID]')) {
        const parts = comment.split('[TRIP_ID]');
        comment = parts[0].trim();
        const tripIdPart = parts[1]?.split('\n')[0]?.trim();
        tripId = tripIdPart && tripIdPart !== 'NONE' ? tripIdPart : null;
      } else if (raw.includes('[TRIP_ID]')) {
        const tripIdMatch = raw.match(/\[TRIP_ID\]\s*([A-Z0-9-]+)/);
        tripId = tripIdMatch?.[1] && tripIdMatch[1] !== 'NONE' ? tripIdMatch[1] : null;
      }
  
      console.log("AI Raw Analysis:", raw.substring(0, 100) + "...");
      console.log("Structured TripID Found:", tripId);
  
      // Fallback: If still no tripId, try to find a pattern like TRIP-XXXX in the comment
      if (!tripId || tripId === 'NONE') {
        const fallbackMatch = comment.match(/TRIP-[A-Z0-9]+/i);
        if (fallbackMatch) {
          tripId = fallbackMatch[0].toUpperCase().trim();
          console.log("Fallback TripID Found in Text:", tripId);
        }
      }
  
      return { 
        aiComment: comment.replace('[COMMENTAIRE]', '').trim(), 
        aiMessage: message,
        matchedTripId: tripId
      };
    }, [localAiResult, selectedRequest?.ai_recommendation]);
  
    const matchedTrip = useMemo(() => {
      if (actionMatchedTrip) {
        console.log("Using trip from ActionMatchedTrip:", actionMatchedTrip.id);
        return actionMatchedTrip;
      }
      if (!matchedTripId) return null;
      
      const found = publicPending.find(t => t.id === matchedTripId) || 
                    publicCompleted.find(t => t.id === matchedTripId);
      
      console.log("Search for TripID", matchedTripId, "in public lists:", found ? "FOUND" : "NOT FOUND");
      return found;
    }, [matchedTripId, publicPending, publicCompleted, actionMatchedTrip]);
  const processedComment = useMemo(() => 
    aiComment ? aiComment.replace(/([^ \n])\n([^ \n])/g, '$1  \n$2') : "_Analyse en attente..._"
  , [aiComment]);

  return (
    <>
      <Tabs defaultValue="requests" className="space-y-6">
        <TabsList className="bg-muted/50 p-1">
          <TabsTrigger value="requests">Demandes Clients</TabsTrigger>
          <TabsTrigger value="preview">Aperçu Public (Site)</TabsTrigger>
        </TabsList>

        <TabsContent value="requests" className="space-y-6 outline-none">
          <SiteRequestTable 
            requests={requests} 
            onUpdateStatus={handleUpdateStatus}
            updatingId={updatingId}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            onOpenIA={(id) => setSelectedRequestId(id)}
          />
        </TabsContent>
        
        <TabsContent value="preview" className="space-y-8 outline-none">
          {/* Section preview reste inchangée */}
          <div className="grid md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <div className="flex items-center gap-2 px-1">
                <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
                <h3 className="font-bold uppercase tracking-wider text-sm">Trajets en Direct sur le site</h3>
              </div>
              <div className="space-y-3">
                {publicPending.map((trip) => (
                  <Card key={trip.id} className="border-l-4 border-l-klando-gold overflow-hidden">
                    <CardContent className="p-4">
                      <div className="flex justify-between items-start">
                        <div className="space-y-2">
                          <div className="flex items-center gap-2 font-bold text-sm">
                            <MapPin className="w-4 h-4 text-klando-gold" />
                            {trip.departure_city} → {trip.arrival_city}
                          </div>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground font-bold">
                            <Calendar className="w-3.5 h-3.5" />
                            {format(new Date(trip.departure_time), "EEE d MMM 'à' HH:mm", { locale: fr })}
                          </div>
                        </div>
                        <Badge variant="outline" className="bg-klando-gold/10 text-klando-gold border-klando-gold/20">LIVE</Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
            <div className="space-y-4">
              <div className="flex items-center gap-2 px-1">
                <CheckCircle2 className="w-4 h-4 text-green-500" />
                <h3 className="font-bold uppercase tracking-wider text-sm text-muted-foreground">Preuve Sociale (Terminés)</h3>
              </div>
              <div className="space-y-3">
                {publicCompleted.map((trip) => (
                  <Card key={trip.id} className="bg-muted/30 border-dashed opacity-80">
                    <CardContent className="p-4">
                      <div className="flex justify-between items-center">
                        <div className="text-sm font-semibold text-muted-foreground italic">
                          {trip.departure_city} → {trip.arrival_city}
                        </div>
                        <Badge variant="secondary" className="bg-green-500/10 text-green-600 text-[10px]">TERMINÉ</Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </TabsContent>
      </Tabs>

      {/* STABLE DIALOG (Centralized) */}
      <Dialog open={!!selectedRequestId} onOpenChange={(o) => { if(!o) setSelectedRequestId(null); setLocalAiResult(null); }}>
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
                  <div className="text-xl text-klando-dark font-black uppercase tracking-tight">{selectedRequest?.origin_city} ➜ {selectedRequest?.destination_city}</div>
                  <div className="flex gap-5 mt-4 text-xs font-black text-slate-600">
                    <span className="flex items-center gap-2"><Phone className="w-4 h-4 text-klando-gold" /> {selectedRequest?.contact_info}</span>
                    <span className="flex items-center gap-2"><Calendar className="w-4 h-4 text-klando-gold" /> {selectedRequest?.desired_date ? format(new Date(selectedRequest.desired_date), "dd MMM yyyy", { locale: fr }) : "Dès que possible"}</span>
                  </div>
                </div>
              </div>

              {/* MAP COMPARISON */}
              {selectedRequest && (
                <ComparisonMap 
                  originCity={selectedRequest.origin_city}
                  destination_city={selectedRequest.destination_city}
                  recommendedPolyline={matchedTrip?.polyline}
                />
              )}

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
    </>
  );
}
