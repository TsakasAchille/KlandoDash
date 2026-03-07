"use client";

import { useState, useMemo, useEffect } from "react";
import { 
  Rocket, BarChart3, Users, Map as MapIcon, Sparkles, Globe, CircleDot, 
  ShieldCheck, CheckCircle
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { RefreshButton } from "@/components/refresh-button";
import { MiniStatCard } from "@/components/mini-stat-card";
import { PerformanceTab } from "@/features/marketing/components/pilotage/PerformanceTab";
import { ProspectsTab } from "@/features/marketing/components/pilotage/ProspectsTab";
import { RadarTab } from "@/features/marketing/components/pilotage/RadarTab";
import { CRMOpportunities } from "./crm-opportunities";
import { MatchingDialog } from "@/app/site-requests/components/MatchingDialog";
import { SiteTripRequest, SiteTripRequestsStats } from "@/types/site-request";
import { TripMapItem } from "@/types/trip";
import { PublicTrip, useSiteRequestAI } from "@/app/site-requests/hooks/useSiteRequestAI";
import { useSiteRequestRoutes } from "@/app/map/hooks/useSiteRequestRoutes";

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
  
  // Enriches requests with polylines using the hook
  const enrichedRequests = useSiteRequestRoutes(initialRequests);
  const [requests, setRequests] = useState<SiteTripRequest[]>(initialRequests);
  
  useEffect(() => {
    setRequests(enrichedRequests);
  }, [enrichedRequests]);

  const [selectedRequest, setSelectedRequest] = useState<SiteTripRequest | null>(null);
  const [aiDialogOpenId, setAiDialogOpenId] = useState<string | null>(null);

  // AI Matching Hook logic
  const aiRequest = useMemo(() => aiDialogOpenId ? requests.find(r => r.id === aiDialogOpenId) : null, [requests, aiDialogOpenId]);
  const aiMatching = useSiteRequestAI(aiRequest || null, publicPending, publicCompleted);

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 pb-16 px-4 sm:px-6 lg:px-8 pt-0 relative text-left">
      <div className="flex justify-end mb-2 -mt-10">
        <RefreshButton />
      </div>

      {/* LEAD SNAPSHOT */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 text-left">
        <MiniStatCard title="Prospects" value={leadStats.total} icon="Globe" color="purple" />
        <MiniStatCard title="Nouveaux" value={leadStats.new} icon="CircleDot" color="red" />
        <MiniStatCard title="Observés" value={leadStats.reviewed} icon="Zap" color="gold" />
        <MiniStatCard title="Validés" value={leadStats.validated} icon="ShieldCheck" color="green" />
        <MiniStatCard title="Contactés" value={leadStats.contacted} icon="CheckCircle" color="blue" />
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
        <TabsList className="bg-slate-100 p-1 rounded-2xl h-auto gap-1">
          <TabsTrigger value="perf" className="rounded-xl px-6 py-2.5 data-[state=active]:bg-white data-[state=active]:text-slate-900 shadow-sm font-black uppercase text-[10px] tracking-widest gap-2">
            <BarChart3 className="w-3.5 h-3.5" /> Performance
          </TabsTrigger>
          <TabsTrigger value="prospects" className="rounded-xl px-6 py-2.5 data-[state=active]:bg-white data-[state=active]:text-slate-900 shadow-sm font-black uppercase text-[10px] tracking-widest gap-2">
            <Users className="w-3.5 h-3.5" /> Prospects
          </TabsTrigger>
          <TabsTrigger value="radar" className="rounded-xl px-6 py-2.5 data-[state=active]:bg-white data-[state=active]:text-slate-900 shadow-sm font-black uppercase text-[10px] tracking-widest gap-2">
            <MapIcon className="w-3.5 h-3.5" /> Radar
          </TabsTrigger>
          <TabsTrigger value="crm" className="rounded-xl px-6 py-2.5 data-[state=active]:bg-indigo-600 data-[state=active]:text-white shadow-md font-black uppercase text-[10px] tracking-widest gap-2 relative">
            <Sparkles className="w-3.5 h-3.5" /> CRM Actions
            {crmData && (
              <div className="absolute -top-1 -right-1 flex h-4 w-4">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-4 w-4 bg-indigo-500 text-[8px] items-center justify-center font-bold text-white">
                  {(crmData.unmatched_demand?.length || 0) + (crmData.empty_trips?.length || 0)}
                </span>
              </div>
            )}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="perf">
          <PerformanceTab metrics={metrics} />
        </TabsContent>

        <TabsContent value="prospects">
          <ProspectsTab 
            requests={requests} 
            onRequestsUpdate={setRequests}
            onOpenIA={setAiDialogOpenId}
            onSelectOnMap={(id) => {
              const req = requests.find(r => r.id === id);
              if (req) {
                setSelectedRequest(req);
                setActiveTab("radar");
              }
            }}
          />
        </TabsContent>

        <TabsContent value="radar" forceMount className={activeTab !== "radar" ? "hidden" : ""}>
          <RadarTab
            corridors={metrics.corridors}
            tripsForMap={tripsForMap}
            requests={requests}
            drivers={drivers}
            selectedRequest={selectedRequest}
            onSelectRequest={setSelectedRequest}
          />
        </TabsContent>

        <TabsContent value="crm" className="outline-none animate-in slide-in-from-right-4 duration-500">
          <CRMOpportunities data={crmData} />
        </TabsContent>
      </Tabs>

      <MatchingDialog 
        isOpen={!!aiDialogOpenId}
        onClose={() => setAiDialogOpenId(null)}
        selectedRequest={aiRequest || null}
        {...aiMatching}
      />
    </div>
  );
}
