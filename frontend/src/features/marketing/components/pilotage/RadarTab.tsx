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

/**
 * SOUS-COMPOSANT : Barre de Filtres (Layer Toggles)
 */
function RadarControls({ 
  showFlows, setShowFlows, 
  showFacebook, setShowFacebook, 
  showSite, setShowSite, 
  showRadarOnly, setShowRadarOnly,
  hasSelection, onReset
}: any) {
  return (
    <div className="flex flex-wrap gap-3 items-center justify-between bg-slate-900 p-4 rounded-[2rem] border border-white/5 shadow-2xl">
      <div className="flex flex-wrap gap-2 items-center">
        {/* Toggle FLUX */}
        <button 
          onClick={() => setShowFlows(!showFlows)}
          className={cn(
            "flex items-center gap-2 px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all border",
            showFlows ? "bg-indigo-600 text-white border-indigo-400" : "bg-white/5 text-slate-400 border-white/10 hover:text-white"
          )}
        >
          <TrendingUp className="w-3.5 h-3.5" /> Flux Klando
        </button>

        <div className="w-px h-6 bg-white/10 mx-1 hidden md:block" />

        {/* Toggle FACEBOOK */}
        <button 
          onClick={() => setShowFacebook(!showFacebook)}
          className={cn(
            "flex items-center gap-2 px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all border",
            showFacebook ? "bg-blue-600 text-white border-blue-400 shadow-lg shadow-blue-600/20" : "bg-white/5 text-slate-400 border-white/10 hover:text-white"
          )}
        >
          <Facebook className="w-3.5 h-3.5" /> Facebook
        </button>

        {/* Toggle SITE */}
        <button 
          onClick={() => setShowSite(!showSite)}
          className={cn(
            "flex items-center gap-2 px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all border",
            showSite ? "bg-emerald-600 text-white border-emerald-400 shadow-lg shadow-emerald-600/20" : "bg-white/5 text-slate-400 border-white/10 hover:text-white"
          )}
        >
          <Globe className="w-3.5 h-3.5" /> Site Web
        </button>

        {/* Toggle RADAR */}
        <button 
          onClick={() => setShowRadarOnly(!showRadarOnly)}
          className={cn(
            "flex items-center gap-2 px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all border",
            showRadarOnly ? "bg-klando-gold text-klando-dark border-yellow-400 shadow-lg shadow-yellow-600/20" : "bg-white/5 text-slate-400 border-white/10 hover:text-white"
          )}
        >
          <Target className="w-3.5 h-3.5" /> Radar Match
        </button>
      </div>

      {hasSelection && (
        <button 
          onClick={onReset}
          className="flex items-center gap-2 px-4 py-2 bg-white text-slate-900 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-slate-100 transition-all shadow-lg"
        >
          <X className="w-3.5 h-3.5" /> Reset Focus
        </button>
      )}
    </div>
  );
}

/**
 * COMPOSANT PRINCIPAL
 */
export function RadarTab({ 
  corridors, 
  tripsForMap, 
  requests, 
  drivers,
  selectedRequest,
  onSelectRequest
}: RadarTabProps) {
  // Layer Toggles
  const [showFlows, setShowFlows] = useState(true);
  const [showFacebook, setShowFacebook] = useState(true);
  const [showSite, setShowSite] = useState(true);
  const [showRadarOnly, setShowRadarOnly] = useState(false);
  
  // Selection
  const [selectedCorridor, setSelectedCorridor] = useState<any | null>(null);
  const [selectedTrip, setSelectedTrip] = useState<TripMapItem | null>(null);
  const [hoveredTripId, setHoveredTripId] = useState<string | null>(null);
  const [hoveredRequestId, setHoveredRequestId] = useState<string | null>(null);

  // --- LOGIQUE DE FILTRAGE STRICTE ---

  // 1. Filtrer les Prospects selon les toggles actifs
  const filteredRequests = useMemo(() => {
    return requests.filter(r => {
      const source = r.source || 'SITE';
      // Si Facebook est off, on cache Facebook
      if (source === 'FACEBOOK' && !showFacebook) return false;
      // Si Site est off, on cache Site
      if (source === 'SITE' && !showSite) return false;
      // Filtre Radar Match
      if (showRadarOnly && (!r.matches || r.matches.length === 0)) return false;
      return true;
    });
  }, [requests, showFacebook, showSite, showRadarOnly]);

  // 2. Calculer le tableau des Axes en respectant STRICTEMENT les filtres
  const activeAxes = useMemo(() => {
    const axesMap: Record<string, { origin: string, dest: string, trips: number, leads: number, fill: number }> = {};

    // A. Uniquement si "Flux Klando" est coché, on injecte les corridors conducteurs
    if (showFlows) {
      corridors.forEach(c => {
        if (!c.origin || !c.destination) return;
        const key = [c.origin.toLowerCase(), c.destination.toLowerCase()].sort().join(' - ');
        axesMap[key] = { origin: c.origin, dest: c.destination, trips: c.trips_count, leads: 0, fill: c.fill_rate };
      });
    }

    // B. Injecter les leads (Prospects) filtrés
    filteredRequests.forEach(r => {
      if (!r.origin_city || !r.destination_city) return;
      const key = [r.origin_city.toLowerCase(), r.destination_city.toLowerCase()].sort().join(' - ');
      if (!axesMap[key]) {
        axesMap[key] = { origin: r.origin_city, dest: r.destination_city, trips: 0, leads: 0, fill: 0 };
      }
      axesMap[key].leads++;
    });

    // C. Résultat final trié par volume total
    return Object.values(axesMap)
      .filter(axis => axis.trips > 0 || axis.leads > 0) // Supprime les axes vides
      .sort((a, b) => (b.trips + b.leads) - (a.trips + a.leads));
  }, [corridors, filteredRequests, showFlows]);

  // 3. Filtrer les trajets pour la carte
  const filteredTrips = useMemo(() => {
    if (selectedCorridor) {
      return tripsForMap.filter(t => {
        const dName = t.departure_name?.toLowerCase() || "";
        const aName = t.destination_name?.toLowerCase() || "";
        const cOrigin = selectedCorridor.origin?.toLowerCase() || "";
        const cDest = selectedCorridor.destination?.toLowerCase() || "";

        return (dName.includes(cOrigin) && aName.includes(cDest)) ||
               (dName.includes(cDest) && aName.includes(cOrigin));
      });
    }
    return tripsForMap;
  }, [tripsForMap, selectedCorridor]);

  const isFocusMode = !!selectedCorridor || !!selectedRequest;

  return (
    <div className="space-y-6 animate-in fade-in duration-500 text-left">
      
      <RadarControls 
        showFlows={showFlows} setShowFlows={setShowFlows}
        showFacebook={showFacebook} setShowFacebook={setShowFacebook}
        showSite={showSite} setShowSite={setShowSite}
        showRadarOnly={showRadarOnly} setShowRadarOnly={setShowRadarOnly}
        hasSelection={isFocusMode}
        onReset={() => { setSelectedCorridor(null); onSelectRequest(null); setSelectedTrip(null); }}
      />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[750px]">
        {/* SIDEBAR D'ANALYSE */}
        {!selectedRequest && (
          <div className="lg:col-span-4 flex flex-col gap-4 min-h-0 text-left">
            <div className="bg-white border border-slate-200 rounded-[2.5rem] overflow-hidden shadow-xl flex flex-col h-full">
              <div className="px-6 py-4 bg-slate-50/80 border-b border-slate-100 flex items-center justify-between">
                <h2 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 flex items-center gap-2 text-left">
                  <BarChart3 className="w-4 h-4 text-indigo-500" /> 
                  Axes Actifs ({activeAxes.length})
                </h2>
              </div>
              <div className="flex-1 overflow-y-auto no-scrollbar">
                <table className="w-full text-left border-collapse">
                  <thead className="bg-slate-50/50 sticky top-0 z-10 border-b border-slate-100">
                    <tr>
                      <th className="px-6 py-3 text-[8px] font-black uppercase text-slate-400">Itinéraire</th>
                      <th className="px-2 py-3 text-[8px] font-black uppercase text-slate-400 text-center">Offre</th>
                      <th className="px-2 py-3 text-[8px] font-black uppercase text-slate-400 text-center">Leads</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {activeAxes.length > 0 ? activeAxes.map((axis, i) => (
                      <tr 
                        key={i} 
                        className={cn(
                          "hover:bg-slate-50/80 transition-all group cursor-pointer border-l-4",
                          selectedCorridor?.origin === axis.origin ? "bg-indigo-50/50 border-l-indigo-500" : "border-l-transparent"
                        )} 
                        onClick={() => { setSelectedCorridor(axis); onSelectRequest(null); }}
                      >
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-1.5 font-black uppercase text-[10px] italic tracking-tight text-slate-900 text-left">
                            <span>{axis.origin}</span>
                            <span className="text-muted-foreground/30">→</span>
                            <span>{axis.dest}</span>
                          </div>
                        </td>
                        <td className="px-2 py-4 text-center">
                          {axis.trips > 0 ? (
                            <div className="flex flex-col items-center">
                              <span className="text-[10px] font-black text-indigo-600 flex items-center gap-1">
                                <Car className="w-2.5 h-2.5" /> {axis.trips}
                              </span>
                              <div className="w-8 h-1 bg-slate-100 rounded-full mt-1 overflow-hidden">
                                <div className="h-full bg-indigo-500" style={{ width: `${axis.fill}%` }} />
                              </div>
                            </div>
                          ) : <span className="text-slate-200">-</span>}
                        </td>
                        <td className="px-2 py-4 text-center">
                          {axis.leads > 0 ? (
                            <span className="text-[10px] font-black text-pink-600 flex items-center justify-center gap-1">
                              <Users className="w-2.5 h-2.5" /> {axis.leads}
                            </span>
                          ) : <span className="text-slate-200">-</span>}
                        </td>
                      </tr>
                    )) : (
                      <tr>
                        <td colSpan={3} className="py-20 text-center">
                          <p className="text-[10px] font-black text-slate-300 uppercase tracking-widest italic">Aucun axe actif pour cette sélection</p>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* LA CARTE */}
        <div className={cn("bg-white border border-slate-200 rounded-[2.5rem] overflow-hidden shadow-xl relative min-h-[400px]", selectedRequest ? "lg:col-span-12" : "lg:col-span-8")}>
          <TripMap 
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
            flowMode={showFlows && !selectedCorridor && !selectedRequest} 
          />
          
          {/* Legend Overlay dynamique */}
          <div className="absolute top-6 left-6 z-[1000] flex flex-col gap-2 pointer-events-none text-left">
            <div className="bg-white/90 backdrop-blur-md px-4 py-2 rounded-2xl border border-slate-200 shadow-lg flex items-center gap-3">
               <div className={cn("p-2 rounded-xl", (selectedCorridor || selectedRequest) ? "bg-klando-gold/10 text-klando-dark" : "bg-indigo-600/10 text-indigo-600")}>
                  {(selectedCorridor || selectedRequest) ? <Target className="w-4 h-4" /> : <TrendingUp className="w-4 h-4" />}
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
