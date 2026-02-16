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
      <TableCell className="py-3">
        <div className="flex flex-col min-w-0">
          <div className="flex items-center gap-1.5 mb-0.5">
            <span className="font-bold truncate text-xs uppercase tracking-tight leading-none">
              {trip.departure_city}
            </span>
            <span className="text-klando-gold text-[10px] font-black">→</span>
            <span className="font-bold truncate text-xs uppercase tracking-tight leading-none">
              {trip.destination_city}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-muted-foreground font-mono truncate">
              ID: {trip.trip_id.substring(0, 8)}...
            </span>
            <span className="text-[10px] text-klando-gold font-black">
              {trip.price_per_seat} FCFA
            </span>
          </div>
        </div>
      </TableCell>
      <TableCell className="hidden sm:table-cell text-[11px] font-bold">
        {formatDistance(trip.trip_distance)}
      </TableCell>
      <TableCell className="hidden md:table-cell text-[10px] font-mono text-muted-foreground">
        {formatDate(trip.departure_schedule)}
      </TableCell>
      <TableCell>
        <div className="flex items-center gap-1">
          <span className="text-xs font-black text-klando-gold">{trip.passengers.length}</span>
          <span className="text-[10px] text-muted-foreground">/</span>
          <span className="text-xs font-medium">{trip.total_seats}</span>
        </div>
      </TableCell>
      <TableCell>
        <span
          className={cn(
            "px-1.5 py-0.5 rounded text-[8px] font-black uppercase tracking-wider whitespace-nowrap border",
            statusColors[trip.status] || "bg-gray-500/10 text-gray-400 border-gray-500/20"
          )}
        >
          {trip.status}
        </span>
      </TableCell>
    </TableRow>
  );
}
