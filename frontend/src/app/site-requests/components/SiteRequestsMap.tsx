import { useMemo, useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { SiteTripRequest } from "@/types/site-request";
import { TripMapItem } from "@/types/trip";
import { Card } from "@/components/ui/card";
import { Loader2, Globe, Radar, X, Eye, EyeOff } from "lucide-react";
import { CompactRequestsList } from "./CompactRequestsList";
import { MatchedTripsList } from "./MatchedTripsList";
import { cn } from "@/lib/utils";

const TripMap = dynamic(
  () => import("@/components/map/trip-map").then((mod) => mod.TripMap),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full flex items-center justify-center bg-slate-900 rounded-[3rem]">
        <div className="flex flex-col items-center gap-4 text-white">
          <Loader2 className="w-10 h-10 text-klando-gold animate-spin" />
          <p className="text-[10px] font-black uppercase tracking-widest animate-pulse">Initialisation du Desk...</p>
        </div>
      </div>
    ),
  }
);

interface SiteRequestsMapProps {
  requests: SiteTripRequest[];
  trips: TripMapItem[];
  selectedRequestId: string | null;
  onSelectRequest: (id: string) => void;
  onScan: (id: string) => void;
  onOpenIA: (id: string) => void;
  scanningId: string | null;
  aiMatchedTripId?: string | null; // Nouveau : ID du trajet identifié par l'IA
}

export function SiteRequestsMap({
  requests,
  trips,
  selectedRequestId,
  onSelectRequest,
  onScan,
  onOpenIA,
  scanningId,
  aiMatchedTripId,
}: SiteRequestsMapProps) {
  const [showAllTrips, setShowAllTrips] = useState(false);
  const [hiddenMatchedTripIds, setHiddenMatchedTripIds] = useState<Set<string>>(new Set());
  const [hiddenSiteRequestIds, setHiddenSiteRequestIds] = useState<Set<string>>(new Set());
  const [selectedMatchedTripId, setSelectedMatchedTripId] = useState<string | null>(null);

  const selectedRequest = useMemo(() => 
    selectedRequestId ? requests.find(r => r.id === selectedRequestId) || null : null
  , [requests, selectedRequestId]);

  // ISOLATION DES DEMANDES : Si un client est sélectionné, on cache les autres par défaut
  useEffect(() => {
    if (selectedRequestId) {
      const others = requests
        .filter(r => r.id !== selectedRequestId)
        .map(r => r.id);
      setHiddenSiteRequestIds(new Set(others));
    } else {
      setHiddenSiteRequestIds(new Set());
    }
  }, [selectedRequestId, requests.length]);

  // ISOLATION DES TRAJETS : Si un trajet est sélectionné, on cache les autres matches par défaut
  useEffect(() => {
    if (selectedMatchedTripId && selectedRequest?.matches) {
      const others = selectedRequest.matches
        .filter(m => m.trip_id !== selectedMatchedTripId)
        .map(m => m.trip_id);
      setHiddenMatchedTripIds(new Set(others));
    } else if (!selectedMatchedTripId && selectedRequest?.matches) {
      // Si rien n'est sélectionné, on réaffiche tous les matches de cette demande
      setHiddenMatchedTripIds(new Set());
    }
  }, [selectedMatchedTripId, selectedRequest?.id]);

  // Auto-sélection du meilleur match (IA > Scanner)
  useEffect(() => {
    if (aiMatchedTripId) {
      setSelectedMatchedTripId(aiMatchedTripId);
    } else if (selectedRequest && selectedRequest.matches && selectedRequest.matches.length > 0) {
      const bestMatchId = selectedRequest.matches[0].trip_id;
      if (!selectedMatchedTripId) {
        setSelectedMatchedTripId(bestMatchId);
      }
    } else {
      setSelectedMatchedTripId(null);
    }
  }, [selectedRequest?.id, selectedRequest?.matches?.length, aiMatchedTripId]);

  const handleToggleMatchedTripVisibility = (tripId: string) => {
    setHiddenMatchedTripIds(prev => {
      const next = new Set(prev);
      if (next.has(tripId)) next.delete(tripId);
      else next.add(tripId);
      return next;
    });
  };

  const handleToggleRequestVisibility = (reqId: string) => {
    setHiddenSiteRequestIds(prev => {
      const next = new Set(prev);
      if (next.has(reqId)) next.delete(reqId);
      else next.add(reqId);
      return next;
    });
  };

  const selectedMatchedTrip = useMemo(() => 
    selectedMatchedTripId ? trips.find(t => t.trip_id === selectedMatchedTripId) || null : null
  , [trips, selectedMatchedTripId]);

  // Filtrer les trajets
  const filteredTrips = useMemo(() => {
    if (showAllTrips) return trips;
    
    // On montre les matches du scanner ET le match IA si présent
    const matchedIds = selectedRequest?.matches?.map(m => m.trip_id) || [];
    if (aiMatchedTripId && !matchedIds.includes(aiMatchedTripId)) {
      matchedIds.push(aiMatchedTripId);
    }

    if (selectedRequest && matchedIds.length > 0) {
      return trips.filter(t => matchedIds.includes(t.trip_id) && !hiddenMatchedTripIds.has(t.trip_id));
    }
    
    return [];
  }, [trips, selectedRequest, showAllTrips, hiddenMatchedTripIds, aiMatchedTripId]);

  // Trajets réellement matchés pour la liste de droite avec enrichissement des distances
  const matchedTrips = useMemo(() => {
    const matches = selectedRequest?.matches || [];
    return trips
      .filter(t => matches.some(m => m.trip_id === t.trip_id))
      .map(t => {
        const matchInfo = matches.find(m => m.trip_id === t.trip_id);
        return {
          ...t,
          origin_distance: (matchInfo as any)?.origin_distance,
          destination_distance: (matchInfo as any)?.destination_distance
        };
      });
  }, [trips, selectedRequest]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between px-2">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-500/10 rounded-xl">
            <Globe className="w-5 h-5 text-purple-500" />
          </div>
          <div>
            <h3 className="font-black uppercase tracking-tight text-lg">Operational Matching Desk</h3>
            <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Traitez vos demandes avec une précision géographique</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6 h-[750px]">
        {/* LEFT: Requests List */}
        <div className="col-span-3 h-full overflow-hidden">
          <CompactRequestsList 
            requests={requests}
            selectedId={selectedRequestId}
            hiddenIds={hiddenSiteRequestIds}
            onSelect={onSelectRequest}
            onToggleVisibility={handleToggleRequestVisibility}
            onShowAll={() => setHiddenSiteRequestIds(new Set())}
            onHideAll={() => setHiddenSiteRequestIds(new Set(requests.map(r => r.id)))}
            onScan={onScan}
            onOpenIA={onOpenIA}
            scanningId={scanningId}
          />
        </div>

        {/* MIDDLE: Big Map */}
        <div className="col-span-6 h-full relative">
          <Card className="rounded-[3rem] overflow-hidden border-none shadow-2xl h-full relative bg-slate-900 border-2 border-slate-800">
            <TripMap 
              trips={filteredTrips}
              siteRequests={requests}
              selectedTrip={selectedMatchedTrip}
              selectedRequest={selectedRequest}
              hoveredTripId={null}
              hoveredRequestId={null}
              hiddenTripIds={new Set()}
              hiddenRequestIds={hiddenSiteRequestIds}
              onSelectTrip={(trip) => setSelectedMatchedTripId(trip.trip_id)} 
              onSelectRequest={(req) => onSelectRequest(req.id)}
              onHoverTrip={() => {}}
              onHoverRequest={() => {}}
            />
            
            {/* Overlay d'info */}
            {selectedRequest && (
              <div className="absolute top-6 left-6 right-6 z-40 pointer-events-none">
                <div className="bg-klando-dark/90 backdrop-blur-md border border-purple-500/30 rounded-2xl p-4 shadow-2xl flex items-center justify-between pointer-events-auto animate-in slide-in-from-top-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-purple-500/20 rounded-xl"><Radar className="w-5 h-5 text-purple-500" /></div>
                    <div>
                      <p className="text-[10px] font-black text-purple-400 uppercase tracking-widest leading-none mb-1">Focus Client</p>
                      <h4 className="text-sm font-black text-white uppercase">{selectedRequest.origin_city} ➜ {selectedRequest.destination_city}</h4>
                    </div>
                  </div>
                  <button onClick={() => onSelectRequest("")} className="p-2 hover:bg-white/10 rounded-xl text-white transition-colors">
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </Card>
        </div>

        <div className="col-span-3 h-full overflow-hidden">
          <MatchedTripsList 
            trips={matchedTrips} 
            hiddenIds={hiddenMatchedTripIds}
            onToggleVisibility={handleToggleMatchedTripVisibility}
            onShowAll={() => setHiddenMatchedTripIds(new Set())}
            onHideAll={() => setHiddenMatchedTripIds(new Set(matchedTrips.map(t => t.trip_id)))}
            selectedId={selectedMatchedTripId}
            onSelect={setSelectedMatchedTripId}
            onOpenIA={() => selectedRequestId && onOpenIA(selectedRequestId)}
          />
        </div>
      </div>
    </div>
  );
}

function Info({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}
