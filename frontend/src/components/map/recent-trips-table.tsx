"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableRow,
} from "@/components/ui/table";
import { TripMapItem } from "@/types/trip";
import { formatDate } from "@/lib/utils";
import { cn } from "@/lib/utils";

// Badge de statut
const statusStyles: Record<string, string> = {
  ACTIVE: "bg-blue-500/20 text-blue-400",
  COMPLETED: "bg-green-500/20 text-green-400",
  PENDING: "bg-yellow-500/20 text-yellow-400",
  CANCELLED: "bg-red-500/20 text-red-400",
  ARCHIVED: "bg-gray-500/20 text-gray-400",
};

// Couleurs des polylines (même palette que trip-map)
const POLYLINE_COLORS = [
  "#3B82F6", "#22C55E", "#EF4444", "#A855F7", "#F97316",
  "#06B6D4", "#EC4899", "#84CC16", "#6366F1", "#14B8A6",
  "#F59E0B", "#8B5CF6",
];

interface RecentTripsTableProps {
  trips: TripMapItem[];
  selectedTripId: string | undefined;
  hoveredTripId: string | null;
  hiddenTripIds: Set<string>;
  onSelectTrip: (trip: TripMapItem) => void;
  onHoverTrip: (tripId: string | null) => void;
  onToggleVisibility: (tripId: string) => void;
  onShowOnlyLast: () => void;
  onShowAll: () => void;
}

export function RecentTripsTable({
  trips,
  selectedTripId,
  hoveredTripId,
  hiddenTripIds,
  onSelectTrip,
  onHoverTrip,
  onToggleVisibility,
  onShowOnlyLast,
  onShowAll,
}: RecentTripsTableProps) {
  return (
    <Card className="bg-klando-dark border-gray-700 flex-1 overflow-hidden">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm text-klando-gold">
            10 Derniers Trajets
          </CardTitle>
        </div>
        {/* Boutons d'action */}
        <div className="flex gap-2 mt-2">
          <button
            onClick={onShowOnlyLast}
            className="flex-1 px-2 py-1 text-[10px] bg-klando-burgundy hover:bg-klando-burgundy/80 text-white rounded transition-colors"
          >
            Dernier seul
          </button>
          <button
            onClick={onShowAll}
            className="flex-1 px-2 py-1 text-[10px] bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors"
          >
            Tous
          </button>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="max-h-[400px] overflow-y-auto">
          <Table>
            <TableBody>
              {trips.length === 0 ? (
                <TableRow>
                  <TableCell className="text-center text-white py-8">
                    Aucun trajet trouvé
                  </TableCell>
                </TableRow>
              ) : (
                trips.map((trip, index) => {
                  const isHidden = hiddenTripIds.has(trip.trip_id);
                  const polylineColor = POLYLINE_COLORS[index % POLYLINE_COLORS.length];

                  return (
                    <TableRow
                      key={trip.trip_id}
                      className={cn(
                        "cursor-pointer transition-colors",
                        selectedTripId === trip.trip_id && "bg-klando-burgundy/30",
                        hoveredTripId === trip.trip_id &&
                          selectedTripId !== trip.trip_id &&
                          "bg-gray-800/50",
                        isHidden && "opacity-50"
                      )}
                      onMouseEnter={() => onHoverTrip(trip.trip_id)}
                      onMouseLeave={() => onHoverTrip(null)}
                    >
                      <TableCell className="py-2 px-2">
                        <div className="flex items-start gap-2">
                          {/* Checkbox + indicateur couleur */}
                          <div className="flex flex-col items-center gap-1 pt-0.5">
                            <input
                              type="checkbox"
                              checked={!isHidden}
                              onChange={(e) => {
                                e.stopPropagation();
                                onToggleVisibility(trip.trip_id);
                              }}
                              className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-klando-gold focus:ring-klando-gold cursor-pointer"
                            />
                            <div
                              className="w-3 h-3 rounded-full"
                              style={{ backgroundColor: polylineColor }}
                              title={`Couleur sur la carte`}
                            />
                          </div>

                          {/* Contenu */}
                          <div
                            className="flex-1 space-y-1 min-w-0"
                            onClick={() => onSelectTrip(trip)}
                          >
                            <div className="flex items-center justify-between gap-2">
                              <span className="text-xs font-medium text-white truncate max-w-[100px]">
                                {trip.departure_name || "N/A"}
                              </span>
                              <span
                                className={cn(
                                  "px-1.5 py-0.5 text-[10px] rounded flex-shrink-0",
                                  statusStyles[trip.status || "ACTIVE"] ||
                                    statusStyles.ACTIVE
                                )}
                              >
                                {trip.status || "N/A"}
                              </span>
                            </div>
                            <div className="text-xs text-white truncate">
                              → {trip.destination_name || "N/A"}
                            </div>
                            <div className="text-[10px] text-gray-300">
                              {formatDate(trip.departure_schedule || "")}
                            </div>
                          </div>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
