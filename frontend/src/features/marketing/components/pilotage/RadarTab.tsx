"use client";

import { useState, useMemo } from "react";
import { TrendingUp, Target, BarChart3, Loader2 } from "lucide-react";
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
      <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f8fafc' }}>
        <Loader2 className="w-10 h-10 text-klando-gold animate-spin" />
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
  corridors, tripsForMap, requests, drivers, selectedRequest, onSelectRequest
}: RadarTabProps) {
  const [showFlows, setShowFlows] = useState(true);
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

  // 2. Calculer les axes unifiés (Offre + Demande) pour la navigation
  const activeAxes = useMemo(() => {
    const axesMap: Record<string, { origin: string, destination: string, trips: number, leads: number, fill: number }> = {};

    // On commence par les flux de l'application
    corridors.forEach(c => {
      if (!c.origin || !c.destination) return;
      const key = [c.origin.toLowerCase(), c.destination.toLowerCase()].sort().join(' - ');
      axesMap[key] = { origin: c.origin, destination: c.destination, trips: c.trips_count, leads: 0, fill: c.fill_rate };
    });

    // On enrichit avec les prospects filtrés (Facebook / Site)
    filteredRequests.forEach(r => {
      if (!r.origin_city || !r.destination_city) return;
      const key = [r.origin_city.toLowerCase(), r.destination_city.toLowerCase()].sort().join(' - ');
      if (!axesMap[key]) {
        axesMap[key] = { origin: r.origin_city, destination: r.destination_city, trips: 0, leads: 0, fill: 0 };
      }
      axesMap[key].leads++;
    });

    return Object.values(axesMap)
      .filter(a => (showFlows && a.trips > 0) || a.leads > 0)
      .sort((a, b) => (b.trips + b.leads) - (a.trips + a.leads));
  }, [corridors, filteredRequests, showFlows]);

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

  const isFocusMode = !!selectedCorridor || !!selectedRequest;

  // Focus mode: only show the selected item on the map
  const mapTrips = useMemo(() => {
    if (selectedRequest) return []; // Request selected → hide all trips
    return filteredTrips;
  }, [selectedRequest, filteredTrips]);

  const mapRequests = useMemo(() => {
    if (selectedRequest) return [selectedRequest]; // Only the selected request
    if (selectedCorridor) return []; // Corridor selected → hide requests
    return filteredRequests;
  }, [selectedRequest, selectedCorridor, filteredRequests]);

  return (
    <div>
      <RadarControls
        showFlows={showFlows} setShowFlows={setShowFlows}
        showFacebook={showFacebook} setShowFacebook={setShowFacebook}
        showSite={showSite} setShowSite={setShowSite}
        showRadarOnly={showRadarOnly} setShowRadarOnly={setShowRadarOnly}
        hasSelection={isFocusMode}
        onReset={() => { setSelectedCorridor(null); onSelectRequest(null); setSelectedTrip(null); }}
      />

      {/* INLINE STYLE : force le grid côte-à-côte, pas de Tailwind pour le sizing */}
      <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr', gap: '24px', height: '75vh', marginTop: '24px' }}>

        {/* SIDEBAR */}
        <div className="bg-white border border-slate-200 rounded-3xl shadow-xl flex flex-col" style={{ overflow: 'hidden', minHeight: 0 }}>
          <div className="px-6 py-4 bg-slate-50/80 border-b border-slate-100 shrink-0">
            <h2 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-indigo-500" />
              Intelligence Radar
            </h2>
          </div>
          <div style={{ flex: 1, overflow: 'hidden' }}>
            <RadarSidebar
              showFlows={showFlows}
              showFacebook={showFacebook}
              showSite={showSite}
              corridors={activeAxes}
              facebookLeads={facebookLeads}
              siteLeads={siteLeads}
              whatsappLeads={whatsappLeads}
              matchedProspects={matchedProspects}
              selectedRequestId={selectedRequest?.id ?? null}
              selectedCorridor={selectedCorridor}
              onSelectCorridor={(c) => { setSelectedCorridor(c); onSelectRequest(null); }}
              onSelectRequest={(r) => { onSelectRequest(r); setSelectedCorridor(null); }}
            />
          </div>
        </div>

        {/* CARTE - inline styles pour forcer les dimensions */}
        <div className="bg-white border border-slate-200 rounded-3xl shadow-xl" style={{ position: 'relative', overflow: 'hidden', minHeight: 0 }}>
          <TripMap
            trips={mapTrips}
            selectedTrip={selectedTrip}
            selectedRequest={selectedRequest}
            siteRequests={mapRequests}
            hoveredTripId={hoveredTripId}
            hoveredRequestId={hoveredRequestId}
            hiddenTripIds={new Set()}
            hiddenRequestIds={new Set()}
            onSelectTrip={setSelectedTrip}
            onSelectRequest={onSelectRequest}
            onHoverTrip={setHoveredTripId}
            onHoverRequest={setHoveredRequestId}
            flowMode={showFlows && !isFocusMode}
          />

          {/* Overlay badge */}
          <div style={{ position: 'absolute', top: 24, left: 24, zIndex: 1000, pointerEvents: 'none' }}>
            <div className="bg-white/90 backdrop-blur-md px-4 py-2 rounded-2xl border border-slate-200 shadow-lg flex items-center gap-3">
              <div className={cn("p-2 rounded-xl", isFocusMode ? "bg-klando-gold/10 text-klando-dark" : "bg-indigo-600/10 text-indigo-600")}>
                {isFocusMode ? <Target className="w-4 h-4" /> : <TrendingUp className="w-4 h-4" />}
              </div>
              <div>
                <p className="text-[8px] font-black uppercase text-slate-400 tracking-widest leading-none">Radar Intelligence</p>
                <p className="text-sm font-black text-slate-900">
                  {selectedRequest ? `${selectedRequest.origin_city} ➜ ${selectedRequest.destination_city}` : selectedCorridor ? `${selectedCorridor.origin} → ${selectedCorridor.destination}` : "Flux & Leads"}
                </p>
              </div>
            </div>
          </div>

          {/* Detail panel when a request is selected */}
          {selectedRequest && (
            <div style={{ position: 'absolute', bottom: 24, left: 24, right: 24, zIndex: 1000 }}>
              <div className="bg-white/95 backdrop-blur-md rounded-2xl border border-slate-200 shadow-xl px-5 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-purple-100">
                      <Target className="w-3.5 h-3.5 text-purple-600" />
                    </div>
                    <span className="text-xs font-black uppercase tracking-wide text-slate-900">
                      {selectedRequest.origin_city} ➜ {selectedRequest.destination_city}
                    </span>
                  </div>
                  <span className={cn(
                    "text-[9px] font-black uppercase px-2.5 py-1 rounded-full",
                    selectedRequest.source?.toUpperCase() === 'FACEBOOK' ? "bg-blue-100 text-blue-700" :
                    selectedRequest.source?.toUpperCase() === 'WHATSAPP' ? "bg-green-100 text-green-700" :
                    "bg-emerald-100 text-emerald-700"
                  )}>
                    {selectedRequest.source || 'Site'}
                  </span>
                </div>
                <div className="flex items-center gap-4 mt-2 text-[10px] text-slate-500">
                  {selectedRequest.desired_date && (
                    <span>📅 {new Date(selectedRequest.desired_date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}</span>
                  )}
                  {selectedRequest.contact_info && (
                    <span>📧 {selectedRequest.contact_info}</span>
                  )}
                  <span className={cn(
                    "font-bold uppercase",
                    selectedRequest.status === 'NEW' ? "text-red-500" :
                    selectedRequest.status === 'REVIEWED' ? "text-yellow-600" :
                    selectedRequest.status === 'CONTACTED' ? "text-blue-500" :
                    selectedRequest.status === 'VALIDATED' ? "text-green-600" : "text-slate-400"
                  )}>
                    {selectedRequest.status}
                  </span>
                </div>
                {selectedRequest.matches && selectedRequest.matches.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-slate-100 flex items-center gap-2">
                    <span className="text-[9px] font-black bg-klando-gold/20 text-klando-dark px-2 py-0.5 rounded-full">
                      {selectedRequest.matches.length} match{selectedRequest.matches.length > 1 ? 's' : ''}
                    </span>
                    <span className="text-[9px] font-bold text-klando-gold">
                      Meilleur : {Math.round(Math.max(...selectedRequest.matches.map(m => m.proximity_score)) * 100)}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Detail panel when a corridor is selected */}
          {selectedCorridor && !selectedRequest && (
            <div style={{ position: 'absolute', bottom: 24, left: 24, right: 24, zIndex: 1000 }}>
              <div className="bg-white/95 backdrop-blur-md rounded-2xl border border-slate-200 shadow-xl px-5 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-indigo-100">
                      <BarChart3 className="w-3.5 h-3.5 text-indigo-600" />
                    </div>
                    <span className="text-xs font-black uppercase tracking-wide text-slate-900">
                      {selectedCorridor.origin} → {selectedCorridor.destination}
                    </span>
                  </div>
                  <span className="text-[10px] font-black text-indigo-600">
                    {selectedCorridor.trips} trajet{selectedCorridor.trips > 1 ? 's' : ''}
                  </span>
                </div>
                <div className="flex items-center gap-3 mt-2">
                  <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${selectedCorridor.fill || 0}%` }} />
                  </div>
                  <span className="text-[10px] font-bold text-slate-500">{Math.round(selectedCorridor.fill || 0)}% remplissage</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
