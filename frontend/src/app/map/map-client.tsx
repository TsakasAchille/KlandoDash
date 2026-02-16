"use client";

import { useMemo, useEffect } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { MapFilters } from "@/components/map/map-filters";
import { RecentTripsTable } from "@/components/map/recent-trips-table";
import { TripMapPopup } from "@/components/map/trip-map-popup";
import { TripMapItem } from "@/types/trip";
import { SiteTripRequest } from "@/types/site-request";
import { X, Filter, List, Map as MapIcon, Users } from "lucide-react";
import { cn } from "@/lib/utils";

// Hooks
import { useMapFilters } from "./hooks/useMapFilters";
import { useMapSelection } from "./hooks/useMapSelection";
import { useMapUI } from "./hooks/useMapUI";

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
  initialStatusFilter: string;
  initialDriverFilter: string | null;
  initialShowRequests: boolean;
}

export function MapClient({
  trips,
  drivers,
  siteRequests,
  initialSelectedTrip,
  initialStatusFilter,
  initialDriverFilter,
  initialShowRequests,
}: MapClientProps) {
  const router = useRouter();

  // 1. Filtrage
  const { 
    filters, 
    handleFilterChange, 
    filteredTrips, 
    filteredRequests 
  } = useMapFilters({
    trips,
    siteRequests,
    initialStatusFilter,
    initialDriverFilter,
    initialShowRequests
  });

  // 2. Sélection
  const {
    selectedTrip,
    handleSelectTrip,
    handleClosePopup,
  } = useMapSelection({
    initialSelectedTrip
  });

  // 3. UI & Visibilité
  const {
    hoveredTripId,
    setHoveredTripId,
    hiddenTripIds,
    displayMode,
    activeTab,
    setActiveTab,
    isSidebarOpen,
    setIsSidebarOpen,
    showMobileFilters,
    setShowMobileFilters,
    handleToggleVisibility,
    handleShowOnlyLast,
    handleShowAll
  } = useMapUI(filteredTrips);

  // UX: Pre-fetch pages liées
  useEffect(() => {
    if (selectedTrip) {
      if (selectedTrip.driver?.uid) {
        router.prefetch(`/users?selected=${selectedTrip.driver.uid}`);
      }
      router.prefetch(`/trips?selected=${selectedTrip.trip_id}`);
    }
  }, [selectedTrip, router]);

  // 15 derniers trajets filtrés pour la barre latérale
  const recentTrips = useMemo(() => {
    return filteredTrips.slice(0, 15);
  }, [filteredTrips]);

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
        {/* Sidebar - Liste des trajets */}
        <div className={cn(
          "bg-background/95 backdrop-blur-md border-r border-border/40 flex flex-col transition-all duration-500 z-30",
          "md:w-[350px] lg:w-[400px]",
          activeTab === "list" ? "fixed inset-0 top-[120px] md:relative md:top-0 block" : "hidden md:flex",
          !isSidebarOpen && "md:w-0 md:opacity-0 md:pointer-events-none"
        )}>
          <div className="p-4 flex-1 overflow-hidden flex flex-col">
            <div className="flex items-center justify-between mb-4 px-2">
              <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-klando-gold">Activité Récente</h3>
              <button 
                onClick={() => setShowMobileFilters(true)}
                className="p-2 rounded-lg bg-secondary border border-border/50 md:hidden"
              >
                <Filter className="w-4 h-4 text-klando-gold" />
              </button>
            </div>
            <RecentTripsTable
              trips={recentTrips}
              selectedTripId={selectedTrip?.trip_id}
              hiddenTripIds={hiddenTripIds}
              displayMode={displayMode}
              onSelectTrip={handleSelectTrip}
              onHoverTrip={setHoveredTripId}
              onToggleVisibility={handleToggleVisibility}
              onShowOnlyLast={handleShowOnlyLast}
              onShowAll={handleShowAll}
            />
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
            hoveredTripId={hoveredTripId}
            hiddenTripIds={hiddenTripIds}
            initialSelectedId={initialSelectedTrip?.trip_id}
            onSelectTrip={handleSelectTrip}
            onHoverTrip={setHoveredTripId}
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
          {selectedTrip && (
            <div className="absolute bottom-6 left-4 right-4 md:left-auto md:right-6 md:w-[400px] z-[1001] animate-in slide-in-from-bottom-4 duration-500">
              <TripMapPopup trip={selectedTrip} onClose={handleClosePopup} />
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
                {/* Custom show requests toggle first */}
                <div className="space-y-4">
                  <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-klando-gold">Données à afficher</h4>
                  <label className="flex items-center justify-between p-4 rounded-2xl bg-secondary/50 border border-border/40 cursor-pointer group hover:border-klando-gold/30 transition-all">
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        "p-2 rounded-xl transition-colors",
                        filters.showRequests ? "bg-purple-500/20 text-purple-500" : "bg-muted text-muted-foreground"
                      )}>
                        <Users className="w-5 h-5" />
                      </div>
                      <div className="flex flex-col">
                        <span className="text-sm font-black uppercase tracking-tight">Demandes Clients</span>
                        <span className="text-[10px] text-muted-foreground">Afficher les intentions de voyage sur la carte</span>
                      </div>
                    </div>
                    <div 
                      className={cn(
                        "w-12 h-6 rounded-full relative transition-colors duration-300",
                        filters.showRequests ? "bg-klando-gold" : "bg-muted"
                      )}
                      onClick={(e) => {
                        e.preventDefault();
                        handleFilterChange({ showRequests: !filters.showRequests });
                      }}
                    >
                      <div className={cn(
                        "absolute top-1 w-4 h-4 bg-white rounded-full transition-all duration-300 shadow-sm",
                        filters.showRequests ? "left-7" : "left-1"
                      )} />
                    </div>
                  </label>
                </div>

                <div className="h-[1px] bg-border/40" />

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
    </div>
  );
}
