import { useState, useCallback } from "react";
import { TripMapItem } from "@/types/trip";
import { SiteTripRequest } from "@/types/site-request";

export function useMapUI(filteredTrips: TripMapItem[], filteredRequests: SiteTripRequest[]) {
  const [hoveredTripId, setHoveredTripId] = useState<string | null>(null);
  const [hoveredRequestId, setHoveredRequestId] = useState<string | null>(null);
  const [hiddenTripIds, setHiddenTripIds] = useState<Set<string>>(new Set());
  const [hiddenRequestIds, setHiddenRequestIds] = useState<Set<string>>(new Set());
  const [tripDisplayMode, setTripDisplayMode] = useState<"all" | "last" | "none">("all");
  const [requestDisplayMode, setRequestDisplayMode] = useState<"all" | "last" | "none">("all");
  const [activeTab, setActiveTab] = useState<"map" | "list">("map");
  const [sidebarTab, setSidebarTab] = useState<"trips" | "requests">("trips");
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [showMobileFilters, setShowMobileFilters] = useState(false);

  const handleToggleVisibility = useCallback((tripId: string) => {
    setHiddenTripIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(tripId)) {
        newSet.delete(tripId);
      } else {
        newSet.add(tripId);
      }
      return newSet;
    });
  }, []);

  const handleToggleRequestVisibility = useCallback((requestId: string) => {
    setHiddenRequestIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(requestId)) {
        newSet.delete(requestId);
      } else {
        newSet.add(requestId);
      }
      return newSet;
    });
  }, []);

  const handleShowOnlyLast = useCallback(() => {
    if (sidebarTab === "trips") {
      const allIds = new Set(filteredTrips.map((t) => t.trip_id));
      if (filteredTrips.length > 0) {
        allIds.delete(filteredTrips[0].trip_id);
      }
      setHiddenTripIds(allIds);
      setTripDisplayMode("last");
    } else {
      const allIds = new Set(filteredRequests.map((r) => r.id));
      if (filteredRequests.length > 0) {
        allIds.delete(filteredRequests[0].id);
      }
      setHiddenRequestIds(allIds);
      setRequestDisplayMode("last");
    }
  }, [sidebarTab, filteredTrips, filteredRequests]);

  const handleShowAll = useCallback(() => {
    if (sidebarTab === "trips") {
      setHiddenTripIds(new Set());
      setTripDisplayMode("all");
    } else {
      setHiddenRequestIds(new Set());
      setRequestDisplayMode("all");
    }
  }, [sidebarTab]);

  const handleHideAll = useCallback(() => {
    if (sidebarTab === "trips") {
      const allIds = new Set(filteredTrips.map((t) => t.trip_id));
      setHiddenTripIds(allIds);
      setTripDisplayMode("none");
    } else {
      const allIds = new Set(filteredRequests.map((r) => r.id));
      setHiddenRequestIds(allIds);
      setRequestDisplayMode("none");
    }
  }, [sidebarTab, filteredTrips, filteredRequests]);

  const handleShowEverything = useCallback(() => {
    setHiddenTripIds(new Set());
    setHiddenRequestIds(new Set());
    setTripDisplayMode("all");
    setRequestDisplayMode("all");
  }, []);

  const handleHideEverything = useCallback(() => {
    setHiddenTripIds(new Set(filteredTrips.map(t => t.trip_id)));
    setHiddenRequestIds(new Set(filteredRequests.map(r => r.id)));
    setTripDisplayMode("none");
    setRequestDisplayMode("none");
  }, [filteredTrips, filteredRequests]);

  return {
    hoveredTripId,
    setHoveredTripId,
    hoveredRequestId,
    setHoveredRequestId,
    hiddenTripIds,
    hiddenRequestIds,
    displayMode: sidebarTab === "trips" ? tripDisplayMode : requestDisplayMode,
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
    handleHideAll,
    handleShowEverything,
    handleHideEverything
  };
}
