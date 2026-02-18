"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { Filter, List, Map as MapIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { scanRequestMatchesAction } from "@/app/site-requests/actions";
import { toast } from "sonner";
import { ScanResultsDialog } from "@/app/site-requests/components/ScanResultsDialog";
import { MapFocusHeader } from "@/features/map/components/MapFocusHeader";

// Hooks
import { useMapFilters } from "./hooks/useMapFilters";
import { useMapSelection } from "./hooks/useMapSelection";
import { useMapUI } from "./hooks/useMapUI";
import { useSiteRequestRoutes } from "./hooks/useSiteRequestRoutes";

// Sub-components SOLID
import { MapSidebar } from "@/features/map/components/MapSidebar";
import { MapDetailsPopup } from "@/features/map/components/MapDetailsPopup";
import { FilterDrawer } from "@/features/map/components/FilterDrawer";

// Types
import { TripMapItem } from "@/types/trip";
import { SiteTripRequest } from "@/types/site-request";

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
  const [scanningId, setScanningId] = useState<string | null>(null);
  const [scanResults, setScanResults] = useState<any>(null);
  const [showScanDialog, setShowScanDialog] = useState(false);

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
      console.error(error);
      toast.error("Erreur lors du scan.");
    } finally {
      setScanningId(null);
    }
  };

  const {
    selectedTrip,
    selectedRequest,
    handleSelectTrip,
    handleSelectRequest,
    handleClosePopup,
  } = useMapSelection({ initialSelectedTrip, initialSelectedRequest });

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

  const {
    hoveredTripId,
    setHoveredTripId,
    hoveredRequestId,
    setHoveredRequestId,
    hiddenTripIds,
    hiddenRequestIds,
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
    handleShowAll,
    handleShowEverything,
    handleHideEverything
  } = useMapUI(filteredTrips, filteredRequests);

  useEffect(() => {
    if (selectedRequest && (selectedRequest.matches?.length || 0) > 0) {
      handleFilterChange({ showMatchesOnly: true });
      handleShowAll(); 
    } else {
      handleFilterChange({ showMatchesOnly: false });
    }
  }, [selectedRequest, handleFilterChange, handleShowAll]);

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
        <MapSidebar 
            activeTab={activeTab}
            isSidebarOpen={isSidebarOpen}
            handleShowEverything={handleShowEverything}
            handleHideEverything={handleHideEverything}
            setShowMobileFilters={setShowMobileFilters}
            sidebarTab={sidebarTab}
            setSidebarTab={setSidebarTab}
            filteredTrips={filteredTrips}
            filteredRequests={filteredRequests}
            selectedTripId={selectedTrip?.trip_id}
            selectedRequestId={selectedRequest?.id}
            hiddenTripIds={hiddenTripIds}
            hiddenRequestIds={hiddenRequestIds}
            onSelectTrip={handleSelectTrip}
            onSelectRequest={handleSelectRequest}
            onHoverTrip={setHoveredTripId}
            onHoverRequest={setHoveredRequestId}
            onToggleTripVisibility={handleToggleVisibility}
            onToggleRequestVisibility={handleToggleRequestVisibility}
            onScan={handleScan}
            scanningId={scanningId}
        />

        <div className={cn(
          "flex-1 relative transition-all duration-500",
          activeTab === "list" ? "hidden md:block" : "block"
        )}>
          <MapFocusHeader selectedRequest={selectedRequest} onClear={handleClosePopup} />

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

          {/* Floating Controls */}
          <div className="absolute top-4 left-4 z-[1000] flex flex-col gap-2">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="hidden md:flex p-3 bg-card/90 backdrop-blur-md border border-border/40 rounded-2xl shadow-xl hover:border-klando-gold/50 transition-all text-klando-gold group"
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

          <MapDetailsPopup 
            selectedTrip={selectedTrip}
            selectedRequest={selectedRequest}
            onClose={handleClosePopup}
          />
        </div>
      </div>

      <FilterDrawer 
        isOpen={showMobileFilters}
        onClose={() => setShowMobileFilters(false)}
        filters={filters}
        drivers={drivers}
        onFilterChange={handleFilterChange}
      />

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
