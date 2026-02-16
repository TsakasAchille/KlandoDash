"use client";

import { Trip } from "@/types/trip";
import { formatDate, formatDistance, cn } from "@/lib/utils";
import { TableCell, TableRow } from "@/components/ui/table";

interface TripTableRowProps {
  trip: Trip;
  isSelected: boolean;
  onSelect: (trip: Trip) => void;
}

const statusColors: Record<string, string> = {
  COMPLETED: "bg-green-500/10 text-green-500 border-green-500/20",
  ACTIVE: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  PENDING: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
  CANCELLED: "bg-red-500/10 text-red-500 border-red-500/20",
  ARCHIVED: "bg-gray-500/10 text-gray-400 border-gray-500/20",
};

export function TripTableRow({ trip, isSelected, onSelect }: TripTableRowProps) {
  return (
    <TableRow
      key={trip.trip_id}
      data-trip-id={trip.trip_id}
      data-state={isSelected ? "selected" : undefined}
      className="cursor-pointer transition-colors hover:bg-secondary/20 border-b border-border/10 last:border-0"
      onClick={() => onSelect(trip)}
    >
      <TableCell className="py-5 px-6">
        <div className="flex flex-col min-w-0">
          <div className="flex items-center gap-2 mb-1.5">
            <span className="font-black truncate text-sm uppercase tracking-tight leading-none">
              {trip.departure_city}
            </span>
            <span className="text-klando-gold text-xs font-black">→</span>
            <span className="font-black truncate text-sm uppercase tracking-tight leading-none text-klando-gold">
              {trip.destination_city}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-[10px] text-muted-foreground font-mono truncate px-2 py-0.5 bg-muted rounded">
              #{trip.trip_id.substring(0, 8)}
            </span>
            <span className="text-xs text-foreground font-black">
              {trip.price_per_seat} <span className="text-[10px] text-muted-foreground ml-0.5">XOF / Place</span>
            </span>
          </div>
        </div>
      </TableCell>
      <TableCell className="hidden sm:table-cell text-xs font-black px-6 text-center">
        <div className="flex flex-col items-center">
          <span className="text-[10px] text-muted-foreground uppercase tracking-widest mb-1">Distance</span>
          {formatDistance(trip.trip_distance)}
        </div>
      </TableCell>
      <TableCell className="hidden md:table-cell text-xs font-bold text-foreground px-6 text-center">
        <div className="flex flex-col items-center">
          <span className="text-[10px] text-muted-foreground uppercase tracking-widest mb-1">Départ</span>
          {formatDate(trip.departure_schedule)}
        </div>
      </TableCell>
      <TableCell className="px-6 text-center">
        <div className="flex flex-col items-center">
          <span className="text-[10px] text-muted-foreground uppercase tracking-widest mb-1">Occupation</span>
          <div className="flex items-center gap-1.5">
            <div className="flex -space-x-1">
              {[...Array(Math.min(3, trip.passengers.length))].map((_, i) => (
                <div key={i} className="w-5 h-5 rounded-full bg-klando-gold/20 border-2 border-card flex items-center justify-center">
                  <span className="text-[8px] font-black text-klando-gold">P</span>
                </div>
              ))}
            </div>
            <span className="text-sm font-black text-klando-gold">{trip.passengers.length}</span>
            <span className="text-xs text-muted-foreground">/ {trip.total_seats}</span>
          </div>
        </div>
      </TableCell>
      <TableCell className="px-6 text-right">
        <span
          className={cn(
            "px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest border shadow-sm",
            statusColors[trip.status] || "bg-gray-500/10 text-gray-400 border-gray-500/20"
          )}
        >
          {trip.status}
        </span>
      </TableCell>
    </TableRow>
  );
}
