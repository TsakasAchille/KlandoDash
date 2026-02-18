"use client";

import { useState, useTransition, useEffect, useMemo } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { SiteTripRequest, SiteTripRequestStatus } from "@/types/site-request";
import { PublicTrip } from "@/app/site-requests/hooks/useSiteRequestAI";
import { TripMapItem } from "@/types/trip";
import { AIRecommendation } from "@/features/site-requests/components/ai/RecommendationCard";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";

// Actions
import { 
  updateRequestStatusAction, 
  scanRequestMatchesAction,
  calculateAndSaveRequestRouteAction
} from "@/app/site-requests/actions";
import { 
  runGlobalScanAction, 
  updateRecommendationStatusAction 
} from "@/app/admin/ai/actions";
import { 
  runMarketingAIScanAction, 
  MarketingInsight 
} from "./actions";

// Components
import { SiteRequestTable } from "@/components/site-requests/site-request-table";
import { SiteRequestsMap } from "@/app/site-requests/components/SiteRequestsMap";
import { RecommendationCard } from "@/features/site-requests/components/ai/RecommendationCard";
import { MatchingDialog } from "@/app/site-requests/components/MatchingDialog";
import { useSiteRequestAI } from "@/app/site-requests/hooks/useSiteRequestAI";
import { 
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow 
} from "@/components/ui/table";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription 
} from "@/components/ui/dialog";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { 
  Zap, Users, Map as MapIcon, History, Sparkles, Loader2, 
  RefreshCw, Target, CheckCircle2, Search, TrendingUp, BarChart3, 
  FileText, ArrowRightCircle, Calendar, Clock
} from "lucide-react";
import { cn } from "@/lib/utils";

interface MarketingClientProps {
  initialRequests: SiteTripRequest[];
  initialRecommendations: AIRecommendation[];
  initialInsights: MarketingInsight[];
  publicPending: PublicTrip[];
  publicCompleted: PublicTrip[];
  tripsForMap: TripMapItem[];
}

export function MarketingClient({ 
  initialRequests, 
  initialRecommendations,
  initialInsights,
  publicPending, 
  publicCompleted, 
  tripsForMap 
}: MarketingClientProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [, startTransition] = useTransition();

  // Tabs state from URL
  const tabParam = searchParams.get("tab") || "strategy";
  const selectedRequestId = searchParams.get("id");
  const aiMatchedTripId = searchParams.get("selectedTrip");

  // Data state
  const [requests, setRequests] = useState<SiteTripRequest[]>(initialRequests);
  const [recommendations, setRecommendations] = useState<AIRecommendation[]>(initialRecommendations);
  const [insights, setInsights] = useState<MarketingInsight[]>(initialInsights);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isScanningMarketing, setIsScanningMarketing] = useState(false);
  const [scanningId, setScanningId] = useState<string | null>(null);
  const [selectedInsight, setSelectedInsight] = useState<MarketingInsight | null>(null);
  const [strategyTab, setStrategyTab] = useState<string>("to-treat");

  // Table state
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [aiDialogOpenId, setAiDialogOpenId] = useState<string | null>(null);

  // Sync with props
  useEffect(() => {
    setRequests(initialRequests);
  }, [initialRequests]);

  useEffect(() => {
    setRecommendations(initialRecommendations);
  }, [initialRecommendations]);

  useEffect(() => {
    setInsights(initialInsights);
  }, [initialInsights]);

  const handleTabChange = (value: string) => {
    const url = new URL(window.location.href);
    url.searchParams.set("tab", value);
    router.replace(url.pathname + url.search, { scroll: false });
  };

  // Recommendations Logic
  const pendingRecommendations = useMemo(() => 
    recommendations.filter(r => r.status === 'PENDING')
  , [recommendations]);

  const historyRecommendations = useMemo(() => 
    recommendations.filter(r => r.status === 'APPLIED')
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  , [recommendations]);

  const handleApplyRecommendation = async (id: string) => {
    const res = await updateRecommendationStatusAction(id, 'APPLIED');
    if (res.success) {
      toast.success("Action marketing validée !");
    }
  };

  const handleDismissRecommendation = async (id: string) => {
    const res = await updateRecommendationStatusAction(id, 'DISMISSED');
    if (res.success) {
      setRecommendations(prev => prev.filter(r => r.id !== id));
    }
  };

  const handleGlobalScan = async () => {
    setIsRefreshing(true);
    const res = await runGlobalScanAction();
    if (res.success) {
      toast.success(`${res.count} nouvelles opportunités identifiées.`);
      setStrategyTab("to-treat");
    } else {
      toast.error("Échec du scan stratégique.");
    }
    setIsRefreshing(false);
  };

  const handleMarketingScan = async () => {
    setIsScanningMarketing(true);
    try {
      const res = await runMarketingAIScanAction();
      if (res.success) {
        toast.success(`${res.count} rapports d'analyse IA générés.`);
        router.refresh();
      }
    } catch (error) {
      toast.error("Erreur lors de l'analyse marketing.");
    } finally {
      setIsScanningMarketing(false);
    }
  };

  // Requests Logic
  const handleUpdateStatus = (id: string, status: SiteTripRequestStatus) => {
    setUpdatingId(id);
    startTransition(async () => {
      const result = await updateRequestStatusAction(id, status);
      if (!result.success) {
        toast.error("Erreur lors de la mise à jour.");
      } else {
        toast.success("Statut mis à jour.");
      }
      setUpdatingId(null);
    });
  };

  const handleScan = async (id: string) => {
    setScanningId(id);
    try {
      const result = await scanRequestMatchesAction(id, 30);
      if (result.success) {
        toast.success(`Scan terminé : ${result.count} trajets analysés.`);
      }
    } catch (error) {
      toast.error("Erreur lors du scan.");
    } finally {
      setScanningId(null);
    }
  };

  const handleSelectRequestOnMap = (id: string) => {
    const url = new URL(window.location.href);
    if (id) {
        url.searchParams.set("id", id);
        url.searchParams.set("tab", "radar");
    } else {
        url.searchParams.delete("id");
        url.searchParams.delete("selectedTrip");
    }
    router.replace(url.pathname + url.search, { scroll: false });
  };

  const selectedRequest = useMemo(() => 
    selectedRequestId ? requests.find(r => r.id === selectedRequestId) : null
  , [requests, selectedRequestId]);

  const aiRequest = useMemo(() => 
    aiDialogOpenId ? requests.find(r => r.id === aiDialogOpenId) : null
  , [requests, aiDialogOpenId]);

  const aiMatching = useSiteRequestAI(aiRequest || null, publicPending, publicCompleted);

  return (
    <div className="space-y-8">
      <Tabs value={tabParam} onValueChange={handleTabChange} className="space-y-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-card/30 p-2 rounded-3xl border border-white/5 backdrop-blur-sm">
          <TabsList className="bg-transparent border-none p-0 h-auto gap-1">
            <TabsTrigger value="strategy" className="rounded-2xl px-6 py-2.5 data-[state=active]:bg-klando-gold data-[state=active]:text-klando-dark font-black uppercase text-[10px] tracking-widest gap-2">
              <Zap className="w-3.5 h-3.5" /> Stratégie
            </TabsTrigger>
            <TabsTrigger value="stats" className="rounded-2xl px-6 py-2.5 data-[state=active]:bg-klando-gold data-[state=active]:text-klando-dark font-black uppercase text-[10px] tracking-widest gap-2">
              <BarChart3 className="w-3.5 h-3.5" /> Intelligence
            </TabsTrigger>
            <TabsTrigger value="prospects" className="rounded-2xl px-6 py-2.5 data-[state=active]:bg-klando-gold data-[state=active]:text-klando-dark font-black uppercase text-[10px] tracking-widest gap-2">
              <Users className="w-3.5 h-3.5" /> Prospects
            </TabsTrigger>
            <TabsTrigger value="radar" className="rounded-2xl px-6 py-2.5 data-[state=active]:bg-klando-gold data-[state=active]:text-klando-dark font-black uppercase text-[10px] tracking-widest gap-2">
              <MapIcon className="w-3.5 h-3.5" /> Radar
            </TabsTrigger>
            <TabsTrigger value="history" className="rounded-2xl px-6 py-2.5 data-[state=active]:bg-klando-gold data-[state=active]:text-klando-dark font-black uppercase text-[10px] tracking-widest gap-2">
              <History className="w-3.5 h-3.5" /> Archives
            </TabsTrigger>
          </TabsList>
          
          <div className="flex items-center gap-2">
            {tabParam === "strategy" && (
                <Button 
                onClick={handleGlobalScan}
                disabled={isRefreshing}
                size="sm"
                className="bg-klando-gold hover:bg-klando-gold/90 text-klando-dark font-black rounded-2xl px-6 h-10 shadow-lg shadow-klando-gold/10"
                >
                {isRefreshing ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <RefreshCw className="w-4 h-4 mr-2" />}
                Scan Opportunités
                </Button>
            )}
            {tabParam === "stats" && (
                <Button 
                onClick={handleMarketingScan}
                disabled={isScanningMarketing}
                size="sm"
                className="bg-blue-600 hover:bg-blue-700 text-white font-black rounded-2xl px-6 h-10 shadow-lg shadow-blue-500/20"
                >
                {isScanningMarketing ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Sparkles className="w-4 h-4 mr-2" />}
                Scan IA Stratégique
                </Button>
            )}
          </div>
        </div>

        {/* --- TABS CONTENT --- */}

        <TabsContent value="strategy" className="outline-none space-y-6">
          <Tabs value={strategyTab} onValueChange={setStrategyTab} className="space-y-6">
            <div className="flex items-center justify-between px-2">
              <TabsList className="bg-white/5 border border-white/10 p-1 h-10 rounded-xl">
                <TabsTrigger value="to-treat" className="rounded-lg px-4 py-1.5 data-[state=active]:bg-green-600 data-[state=active]:text-white font-bold text-[10px] uppercase tracking-wider">
                  À Valider ({pendingRecommendations.length})
                </TabsTrigger>
                <TabsTrigger value="treated" className="rounded-lg px-4 py-1.5 data-[state=active]:bg-white/10 data-[state=active]:text-white font-bold text-[10px] uppercase tracking-wider">
                  Déjà Validées ({historyRecommendations.length})
                </TabsTrigger>
              </TabsList>
            </div>

            <TabsContent value="to-treat" className="outline-none">
              <div className="grid md:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
                {pendingRecommendations.length > 0 ? (
                  pendingRecommendations.map((reco) => (
                    <RecommendationCard 
                      key={reco.id} 
                      reco={reco} 
                      onApply={handleApplyRecommendation}
                      onDismiss={handleDismissRecommendation}
                    />
                  ))
                ) : (
                  <div className="col-span-3 flex flex-col items-center justify-center py-20 bg-white/[0.02] rounded-[3rem] border border-dashed border-white/5 text-center space-y-4">
                    <div className="p-4 bg-white/5 rounded-full"><Target className="w-8 h-8 text-muted-foreground/20" /></div>
                    <p className="text-sm font-bold text-white uppercase">Aucune nouvelle opportunité</p>
                    <Button onClick={handleGlobalScan} variant="outline" size="sm" className="rounded-xl border-white/10 text-[10px] font-black uppercase">
                      Relancer un scan
                    </Button>
                  </div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="treated" className="outline-none">
              <div className="grid md:grid-cols-3 gap-6 opacity-60 grayscale-[0.5] hover:grayscale-0 hover:opacity-100 transition-all duration-500 animate-in fade-in slide-in-from-bottom-2">
                {historyRecommendations.length > 0 ? (
                  historyRecommendations.map((reco) => (
                    <RecommendationCard 
                      key={reco.id} 
                      reco={reco} 
                      onApply={() => {}} 
                      onDismiss={handleDismissRecommendation}
                    />
                  ))
                ) : (
                  <div className="col-span-3 flex flex-col items-center justify-center py-20 text-center opacity-20">
                    <History className="w-12 h-12 mb-4" />
                    <p className="text-[10px] font-black uppercase tracking-widest">Aucun historique récent</p>
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </TabsContent>

        <TabsContent value="stats" className="outline-none">
          <div className="grid md:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {insights.length > 0 ? (
              insights.map((insight) => (
                <Card 
                  key={insight.id} 
                  className="bg-card/40 backdrop-blur-md border-white/5 hover:border-blue-500/30 transition-all duration-500 group relative overflow-hidden flex flex-col h-full"
                >
                  <div className="absolute top-0 right-0 p-4 opacity-[0.03] group-hover:scale-110 transition-transform duration-700">
                    <TrendingUp className="w-12 h-12 text-blue-500" />
                  </div>
                  <CardContent className="p-6 space-y-4 flex flex-col h-full">
                    <div className="flex justify-between items-start">
                      <span className={cn(
                        "text-[8px] font-black px-2 py-0.5 rounded-full uppercase tracking-widest border",
                        insight.category === 'REVENUE' ? "bg-green-500/10 text-green-500 border-green-500/20" :
                        insight.category === 'CONVERSION' ? "bg-purple-500/10 text-purple-500 border-purple-500/20" :
                        "bg-blue-500/10 text-blue-500 border-blue-500/20"
                      )}>
                        {insight.category}
                      </span>
                      <span className="text-[9px] font-bold text-muted-foreground/40 uppercase tabular-nums">
                        {new Date(insight.created_at).toLocaleDateString('fr-FR')}
                      </span>
                    </div>
                    <div>
                      <h4 className="font-black text-sm text-white uppercase tracking-tight group-hover:text-blue-400 transition-colors">
                        {insight.title}
                      </h4>
                      <p className="text-[11px] text-muted-foreground mt-2 leading-relaxed line-clamp-3">
                        {insight.summary}
                      </p>
                    </div>
                    <div className="mt-auto pt-4">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={() => setSelectedInsight(insight)}
                        className="w-full rounded-xl border-white/10 hover:bg-blue-600 hover:text-white hover:border-transparent font-black text-[10px] uppercase tracking-widest h-9"
                      >
                        Lire le rapport <ArrowRightCircle className="w-3.5 h-3.5 ml-2" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <div className="col-span-3 flex flex-col items-center justify-center py-24 bg-white/[0.02] rounded-[3rem] border border-dashed border-white/5 text-center space-y-4">
                <div className="p-4 bg-white/5 rounded-full"><BarChart3 className="w-10 h-10 text-muted-foreground/20" /></div>
                <div className="space-y-1">
                  <p className="text-sm font-bold text-white uppercase tracking-widest">Aucune analyse disponible</p>
                  <p className="text-[10px] text-muted-foreground font-medium max-w-xs mx-auto">
                    Lancez un Scan IA Stratégique pour générer des rapports d&apos;aide à la décision.
                  </p>
                </div>
                <Button 
                  onClick={handleMarketingScan} 
                  disabled={isScanningMarketing}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-black rounded-2xl px-8 h-12 shadow-xl shadow-blue-500/20 mt-4"
                >
                  {isScanningMarketing ? <Loader2 className="w-5 h-5 animate-spin mr-3" /> : <Sparkles className="w-5 h-5 mr-3" />}
                  Générer les rapports
                </Button>
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="prospects" className="outline-none">
          <SiteRequestTable 
            requests={requests} 
            onUpdateStatus={handleUpdateStatus}
            updatingId={updatingId}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            onOpenIA={(id) => setAiDialogOpenId(id)}
            onScan={handleScan}
            scanningId={scanningId}
            selectedId={selectedRequestId || undefined}
          />
        </TabsContent>

        <TabsContent value="radar" className="outline-none">
          <SiteRequestsMap 
            requests={requests}
            trips={tripsForMap}
            selectedRequestId={selectedRequestId}
            onSelectRequest={handleSelectRequestOnMap}
            onScan={handleScan}
            onOpenIA={(id) => setAiDialogOpenId(id)}
            onUpdateStatus={handleUpdateStatus}
            scanningId={scanningId}
            aiMatchedTripId={aiMatchedTripId}
          />
        </TabsContent>

        <TabsContent value="history" className="outline-none space-y-8">
          <Card className="bg-card/30 border-white/5 overflow-hidden rounded-[2rem]">
            <Table>
              <TableHeader>
                <TableRow className="border-white/5 hover:bg-transparent">
                  <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground py-5 pl-8">Date</TableHead>
                  <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Type</TableHead>
                  <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Action</TableHead>
                  <TableHead className="text-right text-[10px] font-black uppercase tracking-widest text-muted-foreground pr-8">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {historyRecommendations.length > 0 ? (
                  historyRecommendations.map((reco) => (
                    <TableRow key={reco.id} className="border-white/5 hover:bg-white/[0.02] transition-colors">
                      <TableCell className="text-[11px] font-medium text-muted-foreground py-4 tabular-nums pl-8">
                        {new Date(reco.created_at).toLocaleString('fr-FR')}
                      </TableCell>
                      <TableCell>
                        <span className={cn(
                          "text-[9px] font-black px-2 py-0.5 rounded-full uppercase tracking-tighter border",
                          reco.type === 'TRACTION' ? "bg-green-500/10 text-green-500 border-green-500/20" :
                          reco.type === 'STRATEGIC' ? "bg-blue-500/10 text-blue-500 border-blue-500/20" :
                          reco.type === 'ENGAGEMENT' ? "bg-klando-gold/10 text-klando-gold border-klando-gold/20" :
                          "bg-red-500/10 text-red-500 border-red-500/20"
                        )}>
                          {reco.type}
                        </span>
                      </TableCell>
                      <TableCell className="text-xs font-bold text-white uppercase">{reco.title}</TableCell>
                      <TableCell className="text-right pr-8">
                        <div className="flex items-center justify-end gap-2 text-green-500 font-black text-[10px] uppercase">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Validé
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={4} className="h-40 text-center text-muted-foreground/30 font-black uppercase text-[10px] tracking-widest">
                      Aucun historique
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>
      </Tabs>

      {/* --- MODALS --- */}

      {/* Detail Insight Modal */}
      <Dialog open={!!selectedInsight} onOpenChange={(open) => !open && setSelectedInsight(null)}>
        <DialogContent className="max-w-3xl bg-slate-900 border-white/10 rounded-[2.5rem] p-0 overflow-hidden outline-none shadow-2xl">
          {selectedInsight && (
            <div className="flex flex-col h-[85vh] bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800">
              <div className="absolute top-0 right-0 p-12 opacity-5 pointer-events-none">
                <BarChart3 className="w-64 h-64 text-blue-400" />
              </div>

              <DialogHeader className="p-10 pb-8 border-b border-white/5 relative z-10 bg-white/[0.02]">
                <div className="flex items-center justify-between mb-6">
                    <span className={cn(
                        "text-[9px] font-black px-3 py-1 rounded-full uppercase tracking-[0.2em] border shadow-sm",
                        selectedInsight.category === 'REVENUE' ? "bg-green-500/10 text-green-500 border-green-500/20" :
                        selectedInsight.category === 'CONVERSION' ? "bg-purple-500/10 text-purple-500 border-purple-500/20" :
                        "bg-blue-500/10 text-blue-500 border-blue-500/20"
                    )}>
                        {selectedInsight.category}
                    </span>
                    <div className="flex items-center gap-6 text-[10px] font-bold text-muted-foreground/60 uppercase tracking-widest">
                        <div className="flex items-center gap-2"><Calendar className="w-3.5 h-3.5 text-klando-gold" /> {new Date(selectedInsight.created_at).toLocaleDateString('fr-FR')}</div>
                        <div className="flex items-center gap-2"><Clock className="w-3.5 h-3.5 text-klando-gold" /> {new Date(selectedInsight.created_at).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}</div>
                    </div>
                </div>
                <DialogTitle className="text-3xl font-black text-white uppercase tracking-tight leading-tight mb-2">
                  {selectedInsight.title}
                </DialogTitle>
                <DialogDescription className="text-[12px] font-black text-blue-400 uppercase tracking-[0.3em] flex items-center gap-2">
                  <Sparkles className="w-3 h-3" /> Intelligence Stratégique
                </DialogDescription>
              </DialogHeader>
              
              <div className="flex-1 overflow-y-auto p-10 pt-8 custom-scrollbar relative z-10">
                <div className="max-w-none">
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      h1: ({node, ...props}) => <h1 className="text-xl font-black text-white uppercase tracking-tight mt-8 mb-4 border-l-4 border-klando-gold pl-4" {...props} />,
                      h2: ({node, ...props}) => <h2 className="text-lg font-bold text-white uppercase tracking-tight mt-6 mb-3" {...props} />,
                      h3: ({node, ...props}) => <h3 className="text-md font-bold text-blue-400 uppercase tracking-wide mt-4 mb-2" {...props} />,
                      p: ({node, ...props}) => <p className="text-sm text-muted-foreground leading-relaxed mb-4 font-medium" {...props} />,
                      ul: ({node, ...props}) => <ul className="list-none space-y-2 mb-6" {...props} />,
                      li: ({node, ...props}) => (
                        <li className="flex gap-3 text-sm text-muted-foreground font-medium items-start">
                          <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-klando-gold shrink-0" />
                          <span {...props} />
                        </li>
                      ),
                      strong: ({node, ...props}) => <strong className="font-bold text-white" {...props} />,
                      code: ({node, ...props}) => <code className="bg-white/5 px-1.5 py-0.5 rounded text-blue-300 font-mono text-xs" {...props} />,
                      blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-white/10 pl-4 italic text-muted-foreground/80 my-6 bg-white/[0.02] p-4 rounded-r-xl" {...props} />,
                    }}
                  >
                    {selectedInsight.content}
                  </ReactMarkdown>
                </div>
              </div>

              <div className="p-8 bg-white/[0.03] border-t border-white/5 flex justify-end relative z-10">
                <Button 
                  onClick={() => setSelectedInsight(null)}
                  className="rounded-2xl bg-white/5 hover:bg-white/10 text-white font-black text-[11px] uppercase px-10 h-12 tracking-[0.2em] transition-all border border-white/10"
                >
                  Fermer l&apos;analyse
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      <MatchingDialog 
        isOpen={!!aiDialogOpenId}
        onClose={() => setAiDialogOpenId(null)}
        selectedRequest={aiRequest || null}
        {...aiMatching}
      />
    </div>
  );
}
