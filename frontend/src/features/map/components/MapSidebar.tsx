"use client";

import { cn } from "@/lib/utils";
import { Eye, EyeOff, Filter, Car, Users } from "lucide-react";
import { RecentTripsTable } from "@/components/map/recent-trips-table";
import { RecentRequestsTable } from "@/components/map/recent-requests-table";
import { TripMapItem } from "@/types/trip";
import { SiteTripRequest } from "@/types/site-request";

interface MapSidebarProps {
  activeTab: string;
  isSidebarOpen: boolean;
  handleShowEverything: () => void;
  handleHideEverything: () => void;
  setShowMobileFilters: (val: boolean) => void;
  sidebarTab: "trips" | "requests";
  setSidebarTab: (val: "trips" | "requests") => void;
  filteredTrips: TripMapItem[];
  filteredRequests: SiteTripRequest[];
  selectedTripId?: string;
  selectedRequestId?: string;
  hiddenTripIds: Set<string>;
  hiddenRequestIds: Set<string>;
  onSelectTrip: (trip: TripMapItem) => void;
  onSelectRequest: (req: SiteTripRequest) => void;
  onHoverTrip: (id: string | null) => void;
  onHoverRequest: (id: string | null) => void;
  onToggleTripVisibility: (id: string) => void;
  onToggleRequestVisibility: (id: string) => void;
  onScan: (id: string) => void;
  scanningId: string | null;
}

export function MapSidebar({
  activeTab,
  isSidebarOpen,
  handleShowEverything,
  handleHideEverything,
  setShowMobileFilters,
  sidebarTab,
  setSidebarTab,
  filteredTrips,
  filteredRequests,
  selectedTripId,
  selectedRequestId,
  hiddenTripIds,
  hiddenRequestIds,
  onSelectTrip,
  onSelectRequest,
  onHoverTrip,
  onHoverRequest,
  onToggleTripVisibility,
  onToggleRequestVisibility,
  onScan,
  scanningId
}: MapSidebarProps) {
  return (
    <div className={cn(
      "bg-background/95 backdrop-blur-md border-r border-border/40 flex flex-col transition-all duration-500 z-30",
      "md:w-[350px] lg:w-[400px]",
      activeTab === "list" ? "fixed inset-0 top-[120px] md:relative md:top-0 block" : "hidden md:flex",
      !isSidebarOpen && "md:w-0 md:opacity-0 md:pointer-events-none"
    )}>
      <div className="p-4 flex-1 overflow-hidden flex flex-col">
        {/* 1. Global Toolbar */}
        <div className="flex items-center justify-between mb-4 px-2 text-left">
          <div className="flex items-center gap-2">
            <button 
              onClick={handleShowEverything}
              className="p-2 rounded-xl bg-secondary/50 hover:bg-secondary text-muted-foreground hover:text-klando-gold transition-all"
              title="Tout afficher"
            >
              <Eye className="w-4 h-4" />
            </button>
            <button 
              onClick={handleHideEverything}
              className="p-2 rounded-xl bg-secondary/50 hover:bg-secondary text-muted-foreground hover:text-foreground transition-all"
              title="Tout masquer"
            >
              <EyeOff className="w-4 h-4" />
            </button>
          </div>
          
          <div className="flex items-center gap-2">
            <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/60 italic mr-2">Exploration</h3>
            <button 
              onClick={() => setShowMobileFilters(true)}
              className="p-2 rounded-xl bg-klando-gold/10 border border-klando-gold/20 text-klando-gold hover:bg-klando-gold/20 transition-all"
              title="Filtres avancés"
            >
              <Filter className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* 2. Sidebar Tabs */}
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

        <div className="flex items-center justify-between mb-4 px-2 text-left">
          <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground italic">
            {sidebarTab === "trips" ? "Offre disponible" : "Demande client"}
          </h3>
          <button 
            onClick={() => setShowMobileFilters(true)}
            className="p-2 rounded-lg bg-secondary border border-border/50 md:hidden"
          >
            <Filter className="w-4 h-4 text-klando-gold" />
          </button>
        </div>

        {sidebarTab === "trips" ? (
          <RecentTripsTable
            trips={filteredTrips.slice(0, 15)}
            selectedTripId={selectedTripId}
            hiddenTripIds={hiddenTripIds}
            onSelectTrip={onSelectTrip}
            onHoverTrip={onHoverTrip}
            onToggleVisibility={onToggleTripVisibility}
          />
        ) : (
          <div className="flex-1 flex flex-col min-h-0">
            <RecentRequestsTable
              requests={filteredRequests.slice(0, 15)}
              selectedRequestId={selectedRequestId}
              hiddenRequestIds={hiddenRequestIds}
              onSelectRequest={onSelectRequest}
              onHoverRequest={onHoverRequest}
              onToggleVisibility={onToggleRequestVisibility}
              onScan={onScan}
              scanningId={scanningId}
            />
          </div>
        )}
      </div>
    </div>
  );
}
