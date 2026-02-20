"use client";

import { useState, useEffect, useMemo } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { SiteTripRequest, SiteTripRequestStatus } from "@/types/site-request";
import { PublicTrip, useSiteRequestAI } from "@/app/site-requests/hooks/useSiteRequestAI";
import { TripMapItem } from "@/types/trip";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";

// Actions & Types
import { 
  updateRequestStatusAction, 
  scanRequestMatchesAction,
  getMarketingSiteRequestsAction
} from "@/app/site-requests/actions";
import { 
  runGlobalScanAction, 
  updateRecommendationStatusAction 
} from "@/app/admin/ai/actions";
import { 
  runMarketingAIScanAction,
  getMarketingMapTripsAction,
  getMarketingFlowStatsAction
} from "./actions/intelligence";
import { 
  MarketingInsight, 
  MarketingFlowStat,
  AIRecommendation
} from "./types";

// Sub-components (extracted for SOLID)
import { StrategyTab } from "@/features/marketing/components/tabs/StrategyTab";
import { IntelligenceTab } from "@/features/marketing/components/tabs/IntelligenceTab";
import { RequestHistoryTab } from "@/features/marketing/components/tabs/RequestHistoryTab";
import { InsightDetailModal } from "@/features/marketing/components/shared/InsightDetailModal";

// Existing Site Requests Components
import { SiteRequestTable } from "@/components/site-requests/site-request-table";
import { SiteRequestsMap } from "@/app/site-requests/components/SiteRequestsMap";
import { MatchingDialog } from "@/app/site-requests/components/MatchingDialog";

// UI / Icons
import { Button } from "@/components/ui/button";
import { 
  Zap, Users, Map as MapIcon, History, Sparkles, Loader2, 
  RefreshCw, BarChart3, TrendingUp
} from "lucide-react";

interface MarketingClientProps {
  initialRecommendations: AIRecommendation[];
  initialInsights: MarketingInsight[];
}

export function MarketingClient({ 
  initialRecommendations,
  initialInsights,
}: MarketingClientProps) {
  const router = useRouter();
  const searchParams = useSearchParams();

  // --- URL STATE MANAGEMENT ---
  const tabParam = searchParams.get("tab") || "strategy";
  const subTabParam = searchParams.get("sub") || "to-treat";
  const statusParam = searchParams.get("status") || "all";
  const pageParam = parseInt(searchParams.get("page") || "1");
  const selectedRequestId = searchParams.get("id");
  const aiMatchedTripId = searchParams.get("selectedTrip");

  // Helper to update URL params without reload
  const updateParams = (updates: Record<string, string | number | null>) => {
    const url = new URL(window.location.href);
    Object.entries(updates).forEach(([key, value]) => {
      if (value === null) url.searchParams.delete(key);
      else url.searchParams.set(key, String(value));
    });
    router.replace(url.pathname + url.search, { scroll: false });
  };

  // Data state
  const [recommendations, setRecommendations] = useState<AIRecommendation[]>(initialRecommendations);
  const [insights, setInsights] = useState<MarketingInsight[]>(initialInsights);
  
  // DEFERRED DATA (Smart Loading)
  const [requests, setRequests] = useState<SiteTripRequest[]>([]);
  const [tripsForMap, setTripsForMap] = useState<TripMapItem[]>([]);
  const [flowStats, setFlowStats] = useState<MarketingFlowStat[]>([]);
  const [publicPending, setPublicPending] = useState<PublicTrip[]>([]);
  const [publicCompleted, setPublicCompleted] = useState<PublicTrip[]>([]);
  const [isDataLoading, setIsDataLoading] = useState(false);

  // Loading states
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isScanningMarketing, setIsScanningMarketing] = useState(false);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [scanningId, setScanningId] = useState<string | null>(null);

  // UI state
  const [selectedInsight, setSelectedInsight] = useState<MarketingInsight | null>(null);
  const [aiDialogOpenId, setAiDialogOpenId] = useState<string | null>(null);

  // --- EFFECT: SYNC PROPS ---
  useEffect(() => { setRecommendations(initialRecommendations); }, [initialRecommendations]);
  useEffect(() => { setInsights(initialInsights); }, [initialInsights]);

  // --- EFFECT: DEFERRED LOADING (SMART LOAD) ---
  useEffect(() => {
    const loadData = async () => {
      // 1. Charger les prospects si on est sur l'onglet Prospects, Radar ou si le dialogue IA est ouvert
      if ((tabParam === "prospects" || tabParam === "radar" || aiDialogOpenId) && requests.length === 0 && !isDataLoading) {
        setIsDataLoading(true);
        const res = await getMarketingSiteRequestsAction({ limit: 1000 });
        if (res.success) setRequests(res.data);
        
        // Charger aussi les trajets pour la carte si on est sur Radar
        if (tabParam === "radar") {
          const mapRes = await getMarketingMapTripsAction(100);
          if (mapRes.success) setTripsForMap(mapRes.data);
        }
        setIsDataLoading(false);
      }

      // 2. Charger les trajets publics SI le dialogue IA est ouvert (Besoin du hook useSiteRequestAI)
      if (aiDialogOpenId && publicPending.length === 0 && !isDataLoading) {
        const { getPublicPendingTrips, getPublicCompletedTrips } = await import("@/lib/queries/site-requests");
        const [pending, completed] = await Promise.all([getPublicPendingTrips(), getPublicCompletedTrips()]);
        setPublicPending(pending);
        setPublicCompleted(completed);
      }

      // 3. Charger les stats de flux si on est sur Observatoire
      if (tabParam === "history" && flowStats.length === 0 && !isDataLoading) {
        setIsDataLoading(true);
        const res = await getMarketingFlowStatsAction();
        if (res.success) setFlowStats(res.data);
        setIsDataLoading(false);
      }
    };

    loadData();
  }, [tabParam, requests.length, flowStats.length, isDataLoading, aiDialogOpenId, publicPending.length]);

  // --- HANDLERS: ACTIONS ---
  const handleGlobalScan = async () => {
    setIsRefreshing(true);
    const res = await runGlobalScanAction();
    if (res.success) {
      toast.success(`${res.count} nouvelles opportunités identifiées.`);
      updateParams({ sub: "to-treat" });
    }
    setIsRefreshing(false);
  };

  const handleMarketingScan = async () => {
    setIsScanningMarketing(true);
    const res = await runMarketingAIScanAction();
    if (res.success) {
      toast.success(`${res.count} rapports d'analyse IA générés.`);
      router.refresh();
    }
    setIsScanningMarketing(false);
  };

  const handleApplyRecommendation = async (id: string) => {
    const res = await updateRecommendationStatusAction(id, 'APPLIED');
    if (res.success) toast.success("Action marketing validée !");
  };

  const handleDismissRecommendation = async (id: string) => {
    const res = await updateRecommendationStatusAction(id, 'DISMISSED');
    if (res.success) setRecommendations(prev => prev.filter(r => r.id !== id));
  };

  const handleUpdateStatus = async (id: string, status: SiteTripRequestStatus) => {
    setUpdatingId(id);
    const result = await updateRequestStatusAction(id, status);
    if (result.success) toast.success("Statut mis à jour.");
    setUpdatingId(null);
  };

  const handleScanRequest = async (id: string) => {
    setScanningId(id);
    const result = await scanRequestMatchesAction(id, 30);
    if (result.success) toast.success(`Scan terminé : ${result.count} trajets analysés.`);
    setScanningId(null);
  };

  // --- MEMOS & AI MATCHING ---
  const aiRequest = useMemo(() => aiDialogOpenId ? requests.find(r => r.id === aiDialogOpenId) : null, [requests, aiDialogOpenId]);
  const aiMatching = useSiteRequestAI(aiRequest || null, publicPending, publicCompleted);

  return (
    <div className="space-y-8">
      <Tabs value={tabParam} onValueChange={(v) => updateParams({ tab: v })} className="space-y-8">
        {/* HEADER: TABS LIST & MAIN ACTIONS */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-card/30 p-2 rounded-3xl border border-white/5 backdrop-blur-sm shadow-xl">
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
              <History className="w-3.5 h-3.5" /> Observatoire
            </TabsTrigger>
          </TabsList>
          
          <div className="flex items-center gap-2">
            {tabParam === "strategy" && (
                <Button onClick={handleGlobalScan} disabled={isRefreshing} size="sm" className="bg-klando-gold hover:bg-klando-gold/90 text-klando-dark font-black rounded-2xl px-6 h-10 shadow-lg shadow-klando-gold/10">
                    {isRefreshing ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <RefreshCw className="w-4 h-4 mr-2" />}
                    Scan Opportunités
                </Button>
            )}
            {tabParam === "stats" && (
                <Button onClick={handleMarketingScan} disabled={isScanningMarketing} size="sm" className="bg-blue-600 hover:bg-blue-700 text-white font-black rounded-2xl px-6 h-10 shadow-lg shadow-blue-500/20">
                    {isScanningMarketing ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Sparkles className="w-4 h-4 mr-2" />}
                    Scan IA Stratégique
                </Button>
            )}
          </div>
        </div>

        {/* --- TABS CONTENT: SMART LOADING --- */}

        <TabsContent value="strategy" className="outline-none">
          {tabParam === "strategy" && (
            <StrategyTab 
              recommendations={recommendations}
              strategyTab={subTabParam}
              onStrategyTabChange={(v) => updateParams({ sub: v })}
              onApply={handleApplyRecommendation}
              onDismiss={handleDismissRecommendation}
              onGlobalScan={handleGlobalScan}
            />
          )}
        </TabsContent>

        <TabsContent value="stats" className="outline-none">
          {tabParam === "stats" && (
            <IntelligenceTab 
              insights={insights}
              isScanning={isScanningMarketing}
              onScan={handleMarketingScan}
              onSelect={setSelectedInsight}
            />
          )}
        </TabsContent>

        <TabsContent value="prospects" className="outline-none">
          {tabParam === "prospects" && (
            <SiteRequestTable 
              requests={requests} 
              onUpdateStatus={handleUpdateStatus}
              updatingId={updatingId}
              currentPage={pageParam}
              setCurrentPage={(v) => updateParams({ page: v })}
              statusFilter={statusParam}
              setStatusFilter={(v) => updateParams({ status: v, page: 1 })}
              onOpenIA={(id) => setAiDialogOpenId(id)}
              onScan={handleScanRequest}
              onSelectOnMap={(id) => updateParams({ id, tab: "radar" })}
              scanningId={scanningId}
              selectedId={selectedRequestId || undefined}
            />
          )}
        </TabsContent>

        <TabsContent value="radar" className="outline-none">
          {tabParam === "radar" && (
            <SiteRequestsMap 
              requests={requests}
              trips={tripsForMap}
              selectedRequestId={selectedRequestId}
              onSelectRequest={(id) => updateParams({ id })}
              onScan={handleScanRequest}
              onOpenIA={(id) => setAiDialogOpenId(id)}
              onUpdateStatus={handleUpdateStatus}
              scanningId={scanningId}
              aiMatchedTripId={aiMatchedTripId}
            />
          )}
        </TabsContent>

        <TabsContent value="history" className="outline-none">
          {tabParam === "history" && (
            <RequestHistoryTab requests={requests} flowStats={flowStats} />
          )}
        </TabsContent>
      </Tabs>

      {/* --- MODALS --- */}
      <InsightDetailModal insight={selectedInsight} onClose={() => setSelectedInsight(null)} />

      <MatchingDialog 
        isOpen={!!aiDialogOpenId}
        onClose={() => setAiDialogOpenId(null)}
        selectedRequest={aiRequest || null}
        {...aiMatching}
      />
    </div>
  );
}
