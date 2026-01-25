"use client";

import { useState, useMemo } from "react";
import { Trip } from "@/types/trip";
import { formatDate, formatDistance, cn } from "@/lib/utils";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface TripTableProps {
  trips: Trip[];
  selectedTripId: string | null;
  onSelectTrip: (trip: Trip) => void;
}

const statusColors: Record<string, string> = {
  COMPLETED: "bg-green-500/20 text-green-400",
  ACTIVE: "bg-blue-500/20 text-blue-400",
  PENDING: "bg-yellow-500/20 text-yellow-400",
  CANCELLED: "bg-red-500/20 text-red-400",
  ARCHIVED: "bg-gray-500/20 text-gray-400",
};

const ITEMS_PER_PAGE = 5;

export function TripTable({ trips, selectedTripId, onSelectTrip }: TripTableProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>("all");

  // Filter trips by status
  const filteredTrips = useMemo(() => {
    if (statusFilter === "all") return trips;
    return trips.filter((trip) => trip.status === statusFilter);
  }, [trips, statusFilter]);

  // Calculate pagination
  const totalPages = Math.ceil(filteredTrips.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const paginatedTrips = filteredTrips.slice(startIndex, startIndex + ITEMS_PER_PAGE);

  // Get unique statuses for filter
  const statuses = useMemo(() => {
    const uniqueStatuses = Array.from(new Set(trips.map((t) => t.status)));
    return uniqueStatuses.sort();
  }, [trips]);

  // Reset to page 1 when filter changes
  const handleFilterChange = (value: string) => {
    setStatusFilter(value);
    setCurrentPage(1);
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex items-center gap-4">
        <Select value={statusFilter} onValueChange={handleFilterChange}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Statut" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous les statuts</SelectItem>
            {statuses.map((status) => (
              <SelectItem key={status} value={status}>
                {status}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <span className="text-sm text-muted-foreground">
          {filteredTrips.length} trajet{filteredTrips.length > 1 ? "s" : ""}
        </span>
      </div>

      {/* Table */}
      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow className="bg-klando-dark hover:bg-klando-dark">
              <TableHead className="text-klando-gold">Trajet</TableHead>
              <TableHead className="text-klando-gold">Distance</TableHead>
              <TableHead className="text-klando-gold">Date</TableHead>
              <TableHead className="text-klando-gold">Places</TableHead>
              <TableHead className="text-klando-gold">Statut</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedTrips.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-muted-foreground py-8">
                  Aucun trajet trouvé
                </TableCell>
              </TableRow>
            ) : (
              paginatedTrips.map((trip) => (
                <TableRow
                  key={trip.trip_id}
                  data-trip-id={trip.trip_id}
                  data-state={selectedTripId === trip.trip_id ? "selected" : undefined}
                  className="cursor-pointer transition-all"
                  onClick={() => onSelectTrip(trip)}
                >
                  <TableCell>
                    <div className="flex flex-col">
                      <span className="font-medium truncate max-w-[150px]">
                        {trip.departure_city}
                      </span>
                      <span className="text-muted-foreground text-xs truncate max-w-[150px]">
                        → {trip.destination_city}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>{formatDistance(trip.trip_distance)}</TableCell>
                  <TableCell className="text-sm">
                    {formatDate(trip.departure_schedule)}
                  </TableCell>
                  <TableCell>
                    {trip.passengers.length}/{trip.total_seats}
                  </TableCell>
                  <TableCell>
                    <span
                      className={cn(
                        "px-2 py-1 rounded-full text-xs font-medium",
                        statusColors[trip.status] || "bg-gray-500/20 text-gray-400"
                      )}
                    >
                      {trip.status}
                    </span>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">
            Page {currentPage} sur {totalPages}
          </span>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
