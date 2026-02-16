import { useState, useCallback } from "react";
import { TripMapItem } from "@/types/trip";

export function useMapUI(filteredTrips: TripMapItem[]) {
  const [hoveredTripId, setHoveredTripId] = useState<string | null>(null);
  const [hiddenTripIds, setHiddenTripIds] = useState<Set<string>>(new Set());
  const [displayMode, setDisplayMode] = useState<"all" | "last">("all");
  const [activeTab, setActiveTab] = useState<"map" | "list">("map");
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

  const handleShowOnlyLast = useCallback(() => {
    const allIds = new Set(filteredTrips.map((t) => t.trip_id));
    if (filteredTrips.length > 0) {
      allIds.delete(filteredTrips[0].trip_id);
    }
    setHiddenTripIds(allIds);
    setDisplayMode("last");
  }, [filteredTrips]);

  const handleShowAll = useCallback(() => {
    setHiddenTripIds(new Set());
    setDisplayMode("all");
  }, []);

  return {
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
  };
}
