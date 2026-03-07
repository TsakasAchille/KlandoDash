"use client";

import { useState, useMemo, useEffect, useCallback } from "react";
import { 
  Rocket, 
  Target, 
  Zap, 
  Map as MapIcon, 
  CheckCircle2,
  TrendingUp,
  AlertTriangle,
  BarChart3,
  Sparkles,
  Loader2,
  Search,
  Users,
  Globe,
  CircleDot,
  ShieldCheck,
  CheckCircle,
  Filter,
  Eye,
  EyeOff
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { RefreshButton } from "@/components/refresh-button";
import { KPICard } from "@/components/home/KPICard";
import { CRMOpportunities } from "./crm-opportunities";
import dynamic from "next/dynamic";
import { TripMapItem } from "@/types/trip";
import { cn } from "@/lib/utils";
import { SiteTripRequest, SiteTripRequestStatus, SiteTripRequestsStats } from "@/types/site-request";
import { PublicTrip, useSiteRequestAI } from "@/app/site-requests/hooks/useSiteRequestAI";
import { updateRequestStatusAction, scanRequestMatchesAction } from "@/app/site-requests/actions";
import { toast } from "sonner";
import { SiteRequestTable } from "@/components/site-requests/site-request-table";
import { MatchingDialog } from "@/app/site-requests/components/MatchingDialog";
import { MiniStatCard } from "@/components/mini-stat-card";

const TripMap = dynamic(
  () => import("@/components/map/trip-map").then((mod) => mod.TripMap),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full flex flex-col items-center justify-center bg-slate-50 rounded-[2.5rem] border border-slate-200">
        <Loader2 className="w-10 h-10 text-klando-gold animate-spin mb-4" />
        <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 animate-pulse">Chargement du radar géographique...</p>
      </div>
    ),
  }
);

interface PilotageClientProps {
  metrics: any;
  crmData: any;
  tripsForMap: TripMapItem[];
  initialRequests: SiteTripRequest[];
  leadStats: SiteTripRequestsStats;
  publicPending: PublicTrip[];
  publicCompleted: PublicTrip[];
  drivers: Array<{ uid: string; display_name: string | null }>;
}

export function PilotageClient({ 
  metrics, 
  crmData, 
  tripsForMap,
  initialRequests,
  leadStats,
  publicPending,
  publicCompleted,
  drivers
}: PilotageClientProps) {
  const [activeTab, setActiveTab] = useState("perf");
  
  // --- RADAR STATE ---
  const [mapViewMode, setMapViewMode] = useState<'flux' | 'radar'>('flux');
  const [selectedCorridor, setSelectedCorridor] = useState<any | null>(null);
  const [selectedTrip, setSelectedTrip] = useState<TripMapItem | null>(null);
  const [selectedRequest, setSelectedRequest] = useState<SiteTripRequest | null>(null);
  const [hoveredTripId, setHoveredTripId] = useState<string | null>(null);
  const [hoveredRequestId, setHoveredRequestId] = useState<string | null>(null);
  
  // Filtering state
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState<'all' | 'optimal' | 'boost'>('all');
  const [radarDriverFilter, setRadarDriverFilter] = useState<string>("ALL");
  const [showRequestsOnMap, setShowRequestsOnMap] = useState(true);

  // Prospects state
  const [requests, setRequests] = useState<SiteTripRequest[]>(initialRequests);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [scanningId, setScanningId] = useState<string | null>(null);
  const [aiDialogOpenId, setAiDialogOpenId] = useState<string | null>(null);
  const [prospectsPage, setProspectsPage] = useState(1);
  const [prospectsStatus, setProspectsStatus] = useState("all");

  // --- LOGIQUE DE FILTRAGE RADAR ---
  
  // 1. Filtrer les Corridors (pour la liste de gauche en mode Flux)
  const filteredCorridors = useMemo(() => {
    return metrics.corridors.filter((c: any) => {
      const matchesSearch = 
        c.origin.toLowerCase().includes(searchQuery.toLowerCase()) || 
        c.destination.toLowerCase().includes(searchQuery.toLowerCase());
      const isOptimal = c.fill_rate > 50;
      const matchesStatus = filterStatus === 'all' || (filterStatus === 'optimal' && isOptimal) || (filterStatus === 'boost' && !isOptimal);
      return matchesSearch && matchesStatus;
    });
  }, [metrics.corridors, searchQuery, filterStatus]);

  // 2. Filtrer les trajets pour la carte
  const filteredTripsForMap = useMemo(() => {
    let base = tripsForMap;

    // En mode Flux, on ne montre que le corridor sélectionné
    if (mapViewMode === 'flux') {
      if (!selectedCorridor) return [];
      return base.filter(trip => {
        return (trip.departure_name?.toLowerCase().includes(selectedCorridor.origin.toLowerCase()) && 
                trip.destination_name?.toLowerCase().includes(selectedCorridor.destination.toLowerCase())) ||
               (trip.departure_name?.toLowerCase().includes(selectedCorridor.destination.toLowerCase()) && 
                trip.destination_name?.toLowerCase().includes(selectedCorridor.origin.toLowerCase()));
      });
    }

    // En mode Radar, on applique les filtres opérationnels
    if (radarDriverFilter !== "ALL") {
      base = base.filter(t => t.driver_id === radarDriverFilter);
    }
    
    return base;
  }, [tripsForMap, selectedCorridor, mapViewMode, radarDriverFilter]);

  // Auto-select first corridor on flux mode mount
  useEffect(() => {
    if (mapViewMode === 'flux' && filteredCorridors.length > 0 && !selectedCorridor) {
      setSelectedCorridor(filteredCorridors[0]);
    }
  }, [filteredCorridors, selectedCorridor, mapViewMode]);

  // --- HANDLERS ---
  const handleUpdateStatus = async (id: string, status: SiteTripRequestStatus) => {
    setUpdatingId(id);
    const result = await updateRequestStatusAction(id, status);
    if (result.success) {
      toast.success("Statut mis à jour.");
      setRequests(prev => prev.map(r => r.id === id ? { ...r, status } : r));
    }
    setUpdatingId(null);
  };

  const handleScanRequest = async (id: string) => {
    setScanningId(id);
    const result = await scanRequestMatchesAction(id, 30);
    if (result.success) {
      toast.success(`Scan terminé : ${result.count} trajets analysés.`);
    }
    setScanningId(null);
  };

  const aiRequest = useMemo(() => aiDialogOpenId ? requests.find(r => r.id === aiDialogOpenId) : null, [requests, aiDialogOpenId]);
  const aiMatching = useSiteRequestAI(aiRequest || null, publicPending, publicCompleted);

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 pb-16 px-4 sm:px-6 lg:px-8 pt-0 relative">
      <div className="flex justify-end mb-2 -mt-10">
        <RefreshButton />
      </div>

      {/* Mini Stats Lead Tracking */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <MiniStatCard title="Prospects" value={leadStats.total} icon="Globe" color="purple" />
        <MiniStatCard title="Nouveaux" value={leadStats.new} icon="CircleDot" color="red" />
        <MiniStatCard title="Observés" value={leadStats.reviewed} icon="Zap" color="gold" />
        <MiniStatCard title="Validés" value={leadStats.validated} icon="ShieldCheck" color="green" />
        <MiniStatCard title="Contactés" value={leadStats.contacted} icon="CheckCircle" color="blue" />
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
        <TabsList className="bg-slate-100 p-1 rounded-2xl h-auto gap-1">
          <TabsTrigger value="perf" className="rounded-xl px-6 py-2.5 data-[state=active]:bg-white data-[state=active]:text-slate-900 data-[state=active]:shadow-sm font-black uppercase text-[10px] tracking-widest gap-2">
            <BarChart3 className="w-3.5 h-3.5" /> Performance
          </TabsTrigger>
          <TabsTrigger value="prospects" className="rounded-xl px-6 py-2.5 data-[state=active]:bg-white data-[state=active]:text-slate-900 data-[state=active]:shadow-sm font-black uppercase text-[10px] tracking-widest gap-2">
            <Users className="w-3.5 h-3.5" /> Prospects
          </TabsTrigger>
          <TabsTrigger value="radar" className="rounded-xl px-6 py-2.5 data-[state=active]:bg-white data-[state=active]:text-slate-900 data-[state=active]:shadow-sm font-black uppercase text-[10px] tracking-widest gap-2">
            <MapIcon className="w-3.5 h-3.5" /> Radar Radar
          </TabsTrigger>
          <TabsTrigger value="crm" className="rounded-xl px-6 py-2.5 data-[state=active]:bg-indigo-600 data-[state=active]:text-white data-[state=active]:shadow-md font-black uppercase text-[10px] tracking-widest gap-2 relative">
            <Sparkles className="w-3.5 h-3.5" /> CRM Actions
            <div className="absolute -top-1 -right-1 flex h-4 w-4">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-4 w-4 bg-indigo-500 text-[8px] items-center justify-center font-bold text-white">
                {(crmData?.unmatched_demand?.length || 0) + (crmData?.empty_trips?.length || 0)}
              </span>
            </div>
          </TabsTrigger>
        </TabsList>

        {/* PERFORMANCE TAB */}
        <TabsContent value="perf" className="space-y-10 outline-none animate-in fade-in duration-500">
          <div className="space-y-6">
            <h2 className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground/60 flex items-center gap-2">
              <Zap className="w-4 h-4 text-klando-gold" />
              Acquisition & Engagement
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <KPICard title="Activation Passager" value={`${metrics.activation.passenger}%`} icon="Users" color="blue" description="Requête sous 72h" />
              <KPICard title="Activation Conducteur" value={`${metrics.activation.driver}%`} icon="Car" color="purple" description="Trajet sous 7j" />
              <KPICard title="Repeat Passager (W1)" value={`${metrics.retention.passenger_w1}%`} icon="RefreshCw" color="green" description="Actif W N-2 → N-1" />
              <KPICard title="Repeat Conducteur (W1)" value={`${metrics.retention.driver_w1}%`} icon="RefreshCw" color="orange" description="Actif W N-2 → N-1" />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="space-y-6">
              <h2 className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground/60 flex items-center gap-2">
                <Target className="w-4 h-4" />
                Liquidité (Match Rate)
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <KPICard title="Match Rate Demande" value={`${metrics.liquidity.match_rate_demand}%`} icon="Target" color="blue" />
                <KPICard title="Match Rate Offre" value={`${metrics.liquidity.match_rate_supply}%`} icon="Car" color="purple" />
              </div>
            </div>
            <div className="space-y-6">
              <h2 className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground/60 flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Efficacité
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <KPICard title="Fill Rate Moyen" value={`${metrics.efficiency.fill_rate}%`} icon="Users" color="green" />
                <KPICard title="Exécution (Realized)" value={`${metrics.efficiency.realized_published_ratio}%`} icon="CheckCircle2" color="blue" />
              </div>
            </div>
          </div>
        </TabsContent>

        {/* PROSPECTS TAB */}
        <TabsContent value="prospects" className="outline-none animate-in fade-in duration-500">
          <SiteRequestTable 
            requests={requests} 
            onUpdateStatus={handleUpdateStatus}
            updatingId={updatingId}
            currentPage={prospectsPage}
            setCurrentPage={setProspectsPage}
            statusFilter={prospectsStatus}
            setStatusFilter={setProspectsStatus}
            onOpenIA={setAiDialogOpenId}
            onScan={handleScanRequest}
            onSelectOnMap={(id) => { setActiveTab("radar"); setMapViewMode('radar'); }}
            scanningId={scanningId}
          />
        </TabsContent>

        {/* RADAR RADAR TAB (INTEGRATED) */}
        <TabsContent value="radar" className="outline-none animate-in fade-in duration-500 space-y-6">
          <div className="flex flex-col md:flex-row gap-4 items-center justify-between bg-white/50 backdrop-blur-sm p-4 rounded-3xl border border-slate-200">
            {/* View Mode Switcher */}
            <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-2xl shadow-xl">
              <button onClick={() => setMapViewMode('flux')} className={cn("px-4 py-2 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all flex items-center gap-2", mapViewMode === 'flux' ? "bg-klando-gold text-klando-dark shadow-inner" : "text-slate-400 hover:text-white")}>
                <TrendingUp className="w-3.5 h-3.5" /> Vue Flux
              </button>
              <button onClick={() => setMapViewMode('radar')} className={cn("px-4 py-2 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all flex items-center gap-2", mapViewMode === 'radar' ? "bg-klando-gold text-klando-dark shadow-inner" : "text-slate-400 hover:text-white")}>
                <Target className="w-3.5 h-3.5" /> Vue Radar
              </button>
            </div>

            {/* Contextual Controls */}
            {mapViewMode === 'flux' ? (
              <div className="flex flex-1 items-center gap-4 justify-end">
                <div className="flex items-center gap-3 bg-white px-4 py-2 rounded-2xl border border-slate-200 shadow-sm">
                  <Search className="w-4 h-4 text-slate-400" />
                  <input type="text" placeholder="Filtrer une ville..." className="text-xs font-bold bg-transparent border-none outline-none w-48" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
                </div>
                <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-2xl border border-slate-200">
                  <button onClick={() => setFilterStatus('all')} className={cn("px-3 py-1.5 rounded-xl text-[8px] font-black uppercase tracking-widest transition-all", filterStatus === 'all' ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-700")}>Tous</button>
                  <button onClick={() => setFilterStatus('optimal')} className={cn("px-3 py-1.5 rounded-xl text-[8px] font-black uppercase tracking-widest transition-all", filterStatus === 'optimal' ? "bg-green-600 text-white shadow-sm" : "text-green-600/60 hover:text-green-600")}>Optimaux</button>
                  <button onClick={() => setFilterStatus('boost')} className={cn("px-3 py-1.5 rounded-xl text-[8px] font-black uppercase tracking-widest transition-all", filterStatus === 'boost' ? "bg-orange-500 text-white shadow-sm" : "text-orange-500/60 hover:text-orange-500")}>À booster</button>
                </div>
              </div>
            ) : (
              <div className="flex flex-1 items-center gap-4 justify-end">
                <select value={radarDriverFilter} onChange={(e) => setRadarDriverFilter(e.target.value)} className="h-10 bg-white border border-slate-200 rounded-2xl px-4 text-[10px] font-black uppercase outline-none focus:border-klando-gold shadow-sm">
                  <option value="ALL">Tous les conducteurs</option>
                  {drivers.map(d => <option key={d.uid} value={d.uid}>{d.display_name}</option>)}
                </select>
                <button onClick={() => setShowRequestsOnMap(!showRequestsOnMap)} className={cn("h-10 px-4 rounded-2xl flex items-center gap-2 text-[10px] font-black uppercase tracking-widest transition-all shadow-sm border", showRequestsOnMap ? "bg-purple-50 border-purple-200 text-purple-700" : "bg-white border-slate-200 text-slate-400")}>
                  {showRequestsOnMap ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                  Demandes Prospects
                </button>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[750px]">
            {/* Left sidebar only in FLUX mode */}
            {mapViewMode === 'flux' && (
              <div className="lg:col-span-4 flex flex-col gap-4 min-h-0">
                <div className="bg-white border border-slate-200 rounded-[2.5rem] overflow-hidden shadow-xl flex flex-col h-full">
                  <div className="px-6 py-4 bg-slate-50/80 border-b border-slate-100 flex items-center justify-between">
                    <h2 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-indigo-500" /> Corridors ({filteredCorridors.length})
                    </h2>
                  </div>
                  <div className="flex-1 overflow-y-auto no-scrollbar">
                    <table className="w-full text-left border-collapse">
                      <tbody className="divide-y divide-slate-50">
                        {filteredCorridors.map((corridor: any, i: number) => (
                          <tr key={i} className={cn("hover:bg-slate-50/80 transition-all group cursor-pointer border-l-4", selectedCorridor?.origin === corridor.origin && selectedCorridor?.destination === corridor.destination ? "bg-indigo-50/50 border-l-indigo-500" : "border-l-transparent")} onClick={() => { setSelectedCorridor(corridor); setSelectedTrip(null); }}>
                            <td className="px-6 py-4">
                              <div className="flex flex-col gap-0.5 text-left">
                                <div className="flex items-center gap-1.5 font-black uppercase text-[11px] italic tracking-tight text-slate-900">
                                  <span>{corridor.origin}</span>
                                  <span className="text-muted-foreground/30">→</span>
                                  <span>{corridor.destination}</span>
                                </div>
                                <span className="text-[9px] font-bold text-slate-400">{corridor.total_bookings} résas sur {corridor.trips_count} trajets</span>
                              </div>
                            </td>
                            <td className="px-4 py-4 text-right">
                              <div className={cn("h-1.5 w-12 rounded-full overflow-hidden mb-1 ml-auto", corridor.fill_rate > 50 ? "bg-green-100" : "bg-orange-100")}>
                                <div className={cn("h-full", corridor.fill_rate > 50 ? "bg-green-500" : "bg-orange-500")} style={{ width: `${corridor.fill_rate}%` }} />
                              </div>
                              <span className="text-[9px] font-black italic">{corridor.fill_rate}%</span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            <div className={cn("bg-white border border-slate-200 rounded-[2.5rem] overflow-hidden shadow-xl relative min-h-[400px]", mapViewMode === 'flux' ? "lg:col-span-8" : "lg:col-span-12")}>
              <TripMap 
                trips={filteredTripsForMap} 
                selectedTrip={selectedTrip} 
                selectedRequest={selectedRequest}
                siteRequests={showRequestsOnMap ? requests : []}
                hoveredTripId={hoveredTripId} 
                hoveredRequestId={hoveredRequestId} 
                hiddenTripIds={new Set()} 
                hiddenRequestIds={new Set()} 
                onSelectTrip={setSelectedTrip} 
                onSelectRequest={setSelectedRequest} 
                onHoverTrip={setHoveredTripId} 
                onHoverRequest={setHoveredRequestId} 
                flowMode={mapViewMode === 'flux'} 
              />
              <div className="absolute top-6 left-6 z-[1000] flex flex-col gap-2">
                <div className="bg-white/90 backdrop-blur-md px-4 py-2 rounded-2xl border border-slate-200 shadow-lg flex items-center gap-3">
                   <div className={cn("p-2 rounded-xl", mapViewMode === 'flux' ? "bg-indigo-600/10 text-indigo-600" : "bg-klando-gold/10 text-klando-dark")}>
                      {mapViewMode === 'flux' ? <TrendingUp className="w-4 h-4" /> : <Target className="w-4 h-4" />}
                   </div>
                   <div className="text-left">
                      <p className="text-[8px] font-black uppercase text-slate-400 tracking-widest leading-none">{mapViewMode === 'flux' ? "Analyse Flux" : "Radar Opérationnel"}</p>
                      <p className="text-sm font-black text-slate-900">
                        {mapViewMode === 'flux' ? (selectedCorridor ? `${selectedCorridor.origin} → ${selectedCorridor.destination}` : 'Macro') : `${filteredTripsForMap.length} Trajets actifs`}
                      </p>
                   </div>
                </div>
              </div>
            </div>
          </div>
        </TabsContent>

        {/* CRM TAB */}
        <TabsContent value="crm" className="outline-none animate-in slide-in-from-right-4 duration-500">
          <CRMOpportunities data={crmData} />
        </TabsContent>
      </Tabs>

      {/* MODALS */}
      <MatchingDialog 
        isOpen={!!aiDialogOpenId}
        onClose={() => setAiDialogOpenId(null)}
        selectedRequest={aiRequest || null}
        {...aiMatching}
      />
    </div>
  );
}
