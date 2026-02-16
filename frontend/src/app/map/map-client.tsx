"use client";

import { useMemo, useEffect } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { MapFilters } from "@/components/map/map-filters";
import { RecentTripsTable } from "@/components/map/recent-trips-table";
import { RecentRequestsTable } from "@/components/map/recent-requests-table";
import { TripMapPopup } from "@/components/map/trip-map-popup";
import { TripMapItem } from "@/types/trip";
import { SiteTripRequest } from "@/types/site-request";
import { X, Filter, List, Map as MapIcon, Users, Car, Eye, EyeOff, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";
import { scanRequestMatchesAction } from "@/app/site-requests/actions";
import { toast } from "sonner";
import { ScanResultsDialog } from "@/app/site-requests/components/ScanResultsDialog";

// Hooks
import { useMapFilters } from "./hooks/useMapFilters";
import { useMapSelection } from "./hooks/useMapSelection";
import { useMapUI } from "./hooks/useMapUI";
import { useSiteRequestRoutes } from "./hooks/useSiteRequestRoutes";

// Import dynamique pour éviter les erreurs SSR avec Leaflet
const TripMap = dynamic(
  () => import("@/components/map/trip-map").then((mod) => mod.TripMap),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full flex items-center justify-center bg-card/50 backdrop-blur-md rounded-lg border border-border/40">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-klando-gold/30 border-t-klando-gold rounded-full animate-spin" />
          <div className="text-klando-gold font-black uppercase tracking-widest text-xs">Initialisation de la carte...</div>
        </div>
      </div>
    ),
  }
);

interface MapClientProps {
  trips: TripMapItem[];
  drivers: Array<{ uid: string; display_name: string | null }>;
  siteRequests: SiteTripRequest[];
  initialSelectedTrip: TripMapItem | null;
  initialSelectedRequest: SiteTripRequest | null;
  initialStatusFilter: string;
  initialDriverFilter: string | null;
  initialShowRequests: boolean;
}

export function MapClient({
  trips,
  drivers,
  siteRequests,
  initialSelectedTrip,
  initialSelectedRequest,
  initialStatusFilter,
  initialDriverFilter,
  initialShowRequests,
}: MapClientProps) {
  const router = useRouter();
  const [scanningId, setScanningId] = useState<string | null>(null);
  const [scanResults, setScanResults] = useState<any>(null);
  const [showScanDialog, setShowScanDialog] = useState(false);

  // 0. Enrichissement dynamique des tracés (Polylines) pour les demandes
  const enrichedRequests = useSiteRequestRoutes(siteRequests);

  const handleScan = async (id: string, radius: number = 5) => {
    setScanningId(id);
    try {
      const result = await scanRequestMatchesAction(id, radius);
      setScanResults(result);
      setShowScanDialog(true);
      if (result.success && result.count > 0) {
        toast.success(result.message);
      }
    } catch (error) {
      toast.error("Erreur lors du scan.");
    } finally {
      setScanningId(null);
    }
  };

  // 1. Sélection (déplacé avant Filtrage pour avoir selectedRequest disponible)
  const {
    selectedTrip,
    selectedRequest,
    handleSelectTrip,
    handleSelectRequest,
    handleClosePopup,
  } = useMapSelection({
    initialSelectedTrip,
    initialSelectedRequest
  });

  // 2. Filtrage
  const { 
    filters, 
    handleFilterChange, 
    filteredTrips, 
    filteredRequests 
  } = useMapFilters({
    trips,
    siteRequests: enrichedRequests,
    initialStatusFilter,
    initialDriverFilter,
    initialShowRequests,
    selectedRequest
  });

  // 3. UI & Visibilité
  const {
    hoveredTripId,
    setHoveredTripId,
    hoveredRequestId,
    setHoveredRequestId,
    hiddenTripIds,
    hiddenRequestIds,
    displayMode,
    activeTab,
    setActiveTab,
    sidebarTab,
    setSidebarTab,
    isSidebarOpen,
    setIsSidebarOpen,
    showMobileFilters,
    setShowMobileFilters,
    handleToggleVisibility,
    handleToggleRequestVisibility,
    handleShowOnlyLast,
    handleShowAll,
    handleHideAll
  } = useMapUI(filteredTrips, filteredRequests);

  // UX: Pre-fetch pages liées
  useEffect(() => {
    if (selectedTrip) {
      if (selectedTrip.driver?.uid) {
        router.prefetch(`/users?selected=${selectedTrip.driver.uid}`);
      }
      router.prefetch(`/trips?selected=${selectedTrip.trip_id}`);
    }
    if (selectedRequest) {
      router.prefetch(`/site-requests?id=${selectedRequest.id}`);
    }
  }, [selectedTrip, selectedRequest, router]);

  // 15 derniers éléments filtrés pour la barre latérale
  const recentTrips = useMemo(() => {
    return filteredTrips.slice(0, 15);
  }, [filteredTrips]);

  const recentRequests = useMemo(() => {
    return filteredRequests.slice(0, 15);
  }, [filteredRequests]);

  return (
    <div className="flex flex-col h-full relative">
      {/* Mobile Tab Switcher */}
      <div className="flex md:hidden bg-card border-b border-border/40 p-1 mx-4 my-2 rounded-xl z-20">
        <button
          onClick={() => setActiveTab("map")}
          className={cn(
            "flex-1 flex items-center justify-center gap-2 py-2 text-[10px] font-black uppercase tracking-widest rounded-lg transition-all",
            activeTab === "map" ? "bg-klando-gold text-klando-dark shadow-sm" : "text-muted-foreground"
          )}
        >
          <MapIcon className="w-3.5 h-3.5" /> Carte
        </button>
        <button
          onClick={() => setActiveTab("list")}
          className={cn(
            "flex-1 flex items-center justify-center gap-2 py-2 text-[10px] font-black uppercase tracking-widest rounded-lg transition-all",
            activeTab === "list" ? "bg-klando-gold text-klando-dark shadow-sm" : "text-muted-foreground"
          )}
        >
          <List className="w-3.5 h-3.5" /> Activité
        </button>
      </div>

      <div className="flex-1 flex flex-col md:flex-row min-h-0 relative">
        {/* Sidebar - Liste des trajets / demandes */}
        <div className={cn(
          "bg-background/95 backdrop-blur-md border-r border-border/40 flex flex-col transition-all duration-500 z-30",
          "md:w-[350px] lg:w-[400px]",
          activeTab === "list" ? "fixed inset-0 top-[120px] md:relative md:top-0 block" : "hidden md:flex",
          !isSidebarOpen && "md:w-0 md:opacity-0 md:pointer-events-none"
        )}>
          <div className="p-4 flex-1 overflow-hidden flex flex-col">
            {/* Sidebar Tabs */}
            <div className="flex bg-muted/30 p-1 rounded-xl mb-4">
              <button
                onClick={() => setSidebarTab("trips")}
                className={cn(
                  "flex-1 flex items-center justify-center gap-2 py-2 text-[9px] font-black uppercase tracking-widest rounded-lg transition-all",
                  sidebarTab === "trips" ? "bg-klando-gold text-klando-dark shadow-sm" : "text-muted-foreground hover:text-foreground"
                )}
              >
                <Car className="w-3 h-3" /> Trajets ({filteredTrips.length})
              </button>
              <button
                onClick={() => setSidebarTab("requests")}
                className={cn(
                  "flex-1 flex items-center justify-center gap-2 py-2 text-[9px] font-black uppercase tracking-widest rounded-lg transition-all",
                  sidebarTab === "requests" ? "bg-purple-500 text-white shadow-sm" : "text-muted-foreground hover:text-foreground"
                )}
              >
                <Users className="w-3 h-3" /> Demandes ({filteredRequests.length})
              </button>
            </div>

            <div className="flex items-center justify-between mb-4 px-2">
              <div className="flex flex-col gap-1">
                <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground italic">
                  {sidebarTab === "trips" ? "Offre disponible" : "Demande client"}
                </h3>
                <div className="flex gap-2">
                  <button 
                    onClick={handleShowAll}
                    className="text-[9px] font-black uppercase text-klando-gold hover:underline flex items-center gap-1"
                  >
                    <Eye className="w-2.5 h-2.5" /> Tout
                  </button>
                  <button 
                    onClick={handleHideAll}
                    className="text-[9px] font-black uppercase text-muted-foreground hover:text-foreground flex items-center gap-1"
                  >
                    <EyeOff className="w-2.5 h-2.5" /> Aucun
                  </button>
                  
                  {sidebarTab === "requests" && selectedRequest && (selectedRequest.matches?.length || 0) > 0 && (
                    <button 
                      onClick={() => handleFilterChange({ showMatchesOnly: !filters.showMatchesOnly })}
                      className={cn(
                        "text-[9px] font-black uppercase flex items-center gap-1 px-2 py-0.5 rounded-full transition-all",
                        filters.showMatchesOnly 
                          ? "bg-green-500 text-white shadow-sm" 
                          : "text-green-500 hover:bg-green-500/10"
                      )}
                    >
                      <Sparkles className="w-2.5 h-2.5" /> Matches
                    </button>
                  )}
                </div>
              </div>
              <button 
                onClick={() => setShowMobileFilters(true)}
                className="p-2 rounded-lg bg-secondary border border-border/50 md:hidden"
              >
                <Filter className="w-4 h-4 text-klando-gold" />
              </button>
            </div>

            {sidebarTab === "trips" ? (
              <RecentTripsTable
                trips={recentTrips}
                selectedTripId={selectedTrip?.trip_id}
                hiddenTripIds={hiddenTripIds}
                onSelectTrip={handleSelectTrip}
                onHoverTrip={setHoveredTripId}
                onToggleVisibility={handleToggleVisibility}
              />
            ) : (
              <div className="flex-1 flex flex-col min-h-0">
                <RecentRequestsTable
                  requests={recentRequests}
                  selectedRequestId={selectedRequest?.id}
                  hiddenRequestIds={hiddenRequestIds}
                  onSelectRequest={handleSelectRequest}
                  onHoverRequest={setHoveredRequestId}
                  onToggleVisibility={handleToggleRequestVisibility}
                  onScan={handleScan}
                  scanningId={scanningId}
                />
              </div>
            )}
          </div>
        </div>

        {/* Map Container */}
        <div className={cn(
          "flex-1 relative transition-all duration-500",
          activeTab === "list" ? "hidden md:block" : "block"
        )}>
          <TripMap
            trips={filteredTrips}
            siteRequests={filteredRequests}
            selectedTrip={selectedTrip}
            selectedRequest={selectedRequest}
            hoveredTripId={hoveredTripId}
            hoveredRequestId={hoveredRequestId}
            hiddenTripIds={hiddenTripIds}
            hiddenRequestIds={hiddenRequestIds}
            initialSelectedId={initialSelectedTrip?.trip_id}
            onSelectTrip={handleSelectTrip}
            onSelectRequest={handleSelectRequest}
            onHoverTrip={setHoveredTripId}
            onHoverRequest={setHoveredRequestId}
          />

          {/* Floating Controls Overlay */}
          <div className="absolute top-4 left-4 z-[1000] flex flex-col gap-2">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="hidden md:flex p-3 bg-card/90 backdrop-blur-md border border-border/40 rounded-2xl shadow-xl hover:border-klando-gold/50 transition-all text-klando-gold group"
              title={isSidebarOpen ? "Fermer le panneau" : "Ouvrir le panneau"}
            >
              <List className={cn("w-5 h-5 transition-transform duration-500", !isSidebarOpen && "rotate-180")} />
            </button>
          </div>

          <div className="absolute top-4 right-4 z-[1000] flex flex-col gap-2">
            <button
              onClick={() => setShowMobileFilters(true)}
              className="p-3 bg-card/90 backdrop-blur-md border border-border/40 rounded-2xl shadow-xl hover:border-klando-gold/50 transition-all text-klando-gold flex items-center gap-2"
            >
              <Filter className="w-5 h-5" />
              <span className="text-[10px] font-black uppercase tracking-widest hidden sm:block">Filtres Avancés</span>
            </button>
          </div>

          {/* Popup détails (overlay sur la carte) */}
          {(selectedTrip || selectedRequest) && (
            <div className="absolute bottom-6 left-4 right-4 md:left-auto md:right-6 md:w-[400px] z-[1001] animate-in slide-in-from-bottom-4 duration-500">
              {selectedTrip ? (
                <TripMapPopup trip={selectedTrip} onClose={handleClosePopup} />
              ) : (
                <div className="bg-card/95 backdrop-blur-md border border-purple-500/30 rounded-3xl p-6 shadow-2xl relative">
                  <button 
                    onClick={handleClosePopup}
                    className="absolute top-4 right-4 p-2 text-muted-foreground hover:text-foreground hover:bg-secondary rounded-xl transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-3 bg-purple-500/10 rounded-2xl text-purple-500">
                      <Users className="w-6 h-6" />
                    </div>
                    <div>
                      <h4 className="font-black uppercase tracking-tight text-lg">Demande Client</h4>
                      <p className="text-[10px] font-black text-purple-500 uppercase tracking-widest">{selectedRequest?.contact_info}</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="p-4 bg-secondary/30 rounded-2xl border border-border/40">
                      <p className="text-[10px] font-black uppercase text-muted-foreground mb-1">Départ</p>
                      <p className="font-bold uppercase text-xs">{selectedRequest?.origin_city}</p>
                    </div>
                    <div className="p-4 bg-secondary/30 rounded-2xl border border-border/40">
                      <p className="text-[10px] font-black uppercase text-muted-foreground mb-1">Arrivée</p>
                      <p className="font-bold uppercase text-xs">{selectedRequest?.destination_city}</p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <button 
                      onClick={() => router.push(`/site-requests?id=${selectedRequest?.id}`)}
                      className="flex-1 py-4 bg-purple-500 text-white font-black uppercase tracking-widest text-[10px] rounded-2xl hover:bg-purple-600 transition-all shadow-lg shadow-purple-500/20"
                    >
                      Voir dans le gestionnaire
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Modern Filter Drawer (Slide from right) */}
      {showMobileFilters && (
        <div className="fixed inset-0 z-[2000] flex justify-end">
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity animate-in fade-in duration-300"
            onClick={() => setShowMobileFilters(false)}
          />
          <div className="relative h-full w-full sm:w-[400px] bg-card border-l border-border/40 shadow-2xl animate-in slide-in-from-right duration-500 flex flex-col">
            <div className="p-6 border-b border-border/40 flex justify-between items-center bg-muted/30">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-klando-gold/10 rounded-xl">
                  <Filter className="w-5 h-5 text-klando-gold" />
                </div>
                <h3 className="text-xl font-black uppercase tracking-tight text-foreground">Configuration de l&apos;affichage</h3>
              </div>
              <button
                onClick={() => setShowMobileFilters(false)}
                className="p-2 text-muted-foreground hover:text-white transition-colors rounded-xl hover:bg-secondary"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <div className="p-6 flex-1 overflow-y-auto">
              <div className="space-y-8">
                <MapFilters
                  filters={filters}
                  drivers={drivers}
                  onFilterChange={handleFilterChange}
                />
              </div>
            </div>

            <div className="p-6 border-t border-border/40 bg-muted/20">
              <button
                onClick={() => setShowMobileFilters(false)}
                className="w-full py-4 bg-klando-gold text-klando-dark font-black uppercase tracking-[0.2em] rounded-2xl shadow-lg hover:shadow-klando-gold/20 transition-all"
              >
                Appliquer les filtres
              </button>
            </div>
          </div>
        </div>
      )}

      <ScanResultsDialog 
        isOpen={showScanDialog}
        onClose={() => setShowScanDialog(false)}
        results={scanResults}
        onRetry={() => {
          if (scanResults?.diagnostics?.origin) {
            const req = siteRequests.find(r => r.origin_city === scanResults.diagnostics.origin);
            if (req) handleScan(req.id, 15);
          }
        }}
      />
    </div>
  );
}
