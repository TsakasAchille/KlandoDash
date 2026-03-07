"use client";

import { useState, useMemo } from "react";
import { 
  TrendingUp, Target, Globe, Facebook, Sparkles, 
  X, Eye, EyeOff, BarChart3, Loader2, Users, Car, Search
} from "lucide-react";
import dynamic from "next/dynamic";
import { TripMapItem } from "@/types/trip";
import { SiteTripRequest } from "@/types/site-request";
import { cn } from "@/lib/utils";
import { RadarControls } from "./radar-controls";
import { RadarSidebar } from "./radar-sidebar";

const TripMap = dynamic(
  () => import("@/components/map/trip-map").then((mod) => mod.TripMap),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full flex flex-col items-center justify-center bg-slate-50 rounded-[2.5rem] border border-slate-200">
        <Loader2 className="w-10 h-10 text-klando-gold animate-spin mb-4" />
        <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 animate-pulse">Chargement Radar...</p>
      </div>
    ),
  }
);

interface RadarTabProps {
  corridors: any[];
  tripsForMap: TripMapItem[];
  requests: SiteTripRequest[];
  drivers: Array<{ uid: string; display_name: string | null }>;
  selectedRequest: SiteTripRequest | null;
  onSelectRequest: (req: SiteTripRequest | null) => void;
}

export function RadarTab({ 
  corridors, 
  tripsForMap, 
  requests, 
  drivers,
  selectedRequest,
  onSelectRequest
}: RadarTabProps) {
  const [showFacebook, setShowFacebook] = useState(true);
  const [showSite, setShowSite] = useState(true);
  const [showRadarOnly, setShowRadarOnly] = useState(false);
  
  const [selectedCorridor, setSelectedCorridor] = useState<any | null>(null);
  const [selectedTrip, setSelectedTrip] = useState<TripMapItem | null>(null);
  const [hoveredTripId, setHoveredTripId] = useState<string | null>(null);
  const [hoveredRequestId, setHoveredRequestId] = useState<string | null>(null);

  const filteredRequests = useMemo(() => {
    return requests.filter(r => {
      const source = r.source || 'SITE';
      if (source === 'FACEBOOK' && !showFacebook) return false;
      if (source === 'SITE' && !showSite) return false;
      if (showRadarOnly && (!r.matches || r.matches.length === 0)) return false;
      return true;
    });
  }, [requests, showFacebook, showSite, showRadarOnly]);

  const facebookLeads = useMemo(() => filteredRequests.filter(r => (r.source || '').toUpperCase() === 'FACEBOOK'), [filteredRequests]);
  const siteLeads = useMemo(() => filteredRequests.filter(r => {
    const s = (r.source || 'SITE').toUpperCase();
    return s === 'SITE' || (s !== 'FACEBOOK' && s !== 'WHATSAPP');
  }), [filteredRequests]);
  const whatsappLeads = useMemo(() => filteredRequests.filter(r => (r.source || '').toUpperCase() === 'WHATSAPP'), [filteredRequests]);
  const matchedProspects = useMemo(() => requests.filter(r => r.matches && r.matches.length > 0), [requests]);

  const activeCorridors = useMemo(() => corridors.filter(c => c.origin && c.destination).sort((a, b) => b.trips_count - a.trips_count), [corridors]);

  const filteredTrips = useMemo(() => {
    if (selectedCorridor) {
      return tripsForMap.filter(t => {
        const dName = t.departure_name?.toLowerCase() || "";
        const aName = t.destination_name?.toLowerCase() || "";
        const cOrigin = selectedCorridor.origin?.toLowerCase() || "";
        const cDest = selectedCorridor.destination?.toLowerCase() || "";
        return (dName.includes(cOrigin) && aName.includes(cDest)) || (dName.includes(cDest) && aName.includes(cOrigin));
      });
    }
    return tripsForMap;
  }, [tripsForMap, selectedCorridor]);

  const selectedRequestId = selectedRequest?.id ?? null;
  const isFocusMode = !!selectedCorridor || !!selectedRequest;

  return (
    <div className="space-y-6 animate-in fade-in duration-500 text-left">
      <RadarControls 
        showFacebook={showFacebook} setShowFacebook={setShowFacebook}
        showSite={showSite} setShowSite={setShowSite}
        showRadarOnly={showRadarOnly} setShowRadarOnly={setShowRadarOnly}
        hasSelection={isFocusMode}
        onReset={() => { setSelectedCorridor(null); onSelectRequest(null); setSelectedTrip(null); }}
      />

      {/* GRILLE FIXE : Garantie que la carte a de l'espace (800px de haut) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 h-[800px] min-h-[800px]">
        
        {/* SIDEBAR (Toujours visible pour naviguer) */}
        <div className="lg:col-span-4 h-full min-h-0 bg-white border border-slate-200 rounded-[2.5rem] overflow-hidden shadow-xl flex flex-col">
          <div className="px-6 py-4 bg-slate-50/80 border-b border-slate-100 flex items-center justify-between shrink-0">
            <h2 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 flex items-center gap-2 text-left">
              <BarChart3 className="w-4 h-4 text-indigo-500" />
              Intelligence Radar
            </h2>
          </div>
          <div className="flex-1 overflow-hidden">
            <RadarSidebar 
              showFacebook={showFacebook}
              showSite={showSite}
              corridors={activeCorridors}
              facebookLeads={facebookLeads}
              siteLeads={siteLeads}
              whatsappLeads={whatsappLeads}
              matchedProspects={matchedProspects}
              selectedRequestId={selectedRequestId}
              selectedCorridor={selectedCorridor}
              onSelectCorridor={handleSelectCorridor}
              onSelectRequest={handleSelectRequest}
            />
          </div>
        </div>

        {/* CARTE (Prend le reste de l'espace) */}
        <div className="lg:col-span-8 bg-white border border-slate-200 rounded-[2.5rem] overflow-hidden shadow-xl relative h-full">
          <TripMap 
            key={`${selectedRequestId}-${selectedCorridor?.origin}`}
            trips={filteredTrips} 
            selectedTrip={selectedTrip} 
            selectedRequest={selectedRequest}
            siteRequests={filteredRequests}
            hoveredTripId={hoveredTripId} 
            hoveredRequestId={hoveredRequestId} 
            hiddenTripIds={new Set()} 
            hiddenRequestIds={new Set()} 
            onSelectTrip={setSelectedTrip} 
            onSelectRequest={onSelectRequest} 
            onHoverTrip={setHoveredTripId} 
            onHoverRequest={setHoveredRequestId} 
            flowMode={!isFocusMode} 
          />
          
          <div className="absolute top-6 left-6 z-[1000] flex flex-col gap-2 pointer-events-none text-left">
            <div className="bg-white/90 backdrop-blur-md px-4 py-2 rounded-2xl border border-slate-200 shadow-lg flex items-center gap-3">
               <div className={cn("p-2 rounded-xl", isFocusMode ? "bg-klando-gold/10 text-klando-dark" : "bg-indigo-600/10 text-indigo-600")}>
                  {isFocusMode ? <Target className="w-4 h-4" /> : <TrendingUp className="w-4 h-4" />}
               </div>
               <div className="text-left">
                  <p className="text-[8px] font-black uppercase text-slate-400 tracking-widest leading-none text-left">Radar Intelligence</p>
                  <p className="text-sm font-black text-slate-900 text-left">
                    {selectedRequest ? `${selectedRequest.origin_city} ➜ ${selectedRequest.destination_city}` : selectedCorridor ? `${selectedCorridor.origin} → ${selectedCorridor.destination}` : "Vue Multi-Couches"}
                  </p>
               </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
