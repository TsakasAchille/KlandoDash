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
import { Input } from "@/components/ui/input";
import { ChevronLeft, ChevronRight, Search } from "lucide-react";

interface TripTableProps {
  trips: Trip[];
  selectedTripId: string | null;
  initialSelectedId?: string | null;
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

export function TripTable({ trips, selectedTripId, initialSelectedId, onSelectTrip }: TripTableProps) {
  // Calculer la page initiale basée sur le trajet sélectionné
  const getInitialPage = () => {
    if (!initialSelectedId) return 1;
    const index = trips.findIndex((t) => t.trip_id === initialSelectedId);
    if (index === -1) return 1;
    return Math.floor(index / ITEMS_PER_PAGE) + 1;
  };

  const [currentPage, setCurrentPage] = useState(getInitialPage);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState("");

  // Filter trips by status and search term
  const filteredTrips = useMemo(() => {
    return trips.filter((trip) => {
      const matchesStatus = statusFilter === "all" || trip.status === statusFilter;
      const term = searchTerm.toLowerCase();
      const matchesSearch = 
        (trip.departure_city?.toLowerCase() || "").includes(term) ||
        (trip.destination_city?.toLowerCase() || "").includes(term) ||
        (trip.trip_id?.toLowerCase() || "").includes(term);
      
      return matchesStatus && matchesSearch;
    });
  }, [trips, statusFilter, searchTerm]);

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

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Rechercher une ville ou ID..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="pl-9 w-full"
          />
        </div>
        <div className="flex items-center gap-4">
          <Select value={statusFilter} onValueChange={handleFilterChange}>
            <SelectTrigger className="w-[180px]">
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
          <span className="text-sm text-muted-foreground whitespace-nowrap">
            {filteredTrips.length} trajet{filteredTrips.length > 1 ? "s" : ""}
          </span>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-2xl border border-border/40 bg-card overflow-x-auto lg:overflow-visible shadow-sm">
        <div className="min-w-[500px] lg:min-w-0"> {/* Largeur minimale seulement sur mobile */}
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/30 hover:bg-muted/30 border-b border-border/40">
                <TableHead className="text-klando-gold font-black uppercase tracking-widest text-[10px]">Trajet</TableHead>
                <TableHead className="text-klando-gold font-black uppercase tracking-widest text-[10px] hidden sm:table-cell">Distance</TableHead>
                <TableHead className="text-klando-gold font-black uppercase tracking-widest text-[10px] hidden md:table-cell">Date</TableHead>
                <TableHead className="text-klando-gold font-black uppercase tracking-widest text-[10px]">Places</TableHead>
                <TableHead className="text-klando-gold font-black uppercase tracking-widest text-[10px]">Statut</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginatedTrips.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-muted-foreground py-12">
                    Aucun trajet trouvé
                  </TableCell>
                </TableRow>
              ) : (
                paginatedTrips.map((trip) => (
                  <TableRow
                    key={trip.trip_id}
                    data-trip-id={trip.trip_id}
                    data-state={selectedTripId === trip.trip_id ? "selected" : undefined}
                    className="cursor-pointer transition-all duration-200 hover:bg-secondary/30 border-b border-border/20 last:border-0"
                    onClick={() => onSelectTrip(trip)}
                  >
                    <TableCell className="py-4">
                      <div className="flex flex-col min-w-0">
                        <div className="flex items-center gap-1 sm:block">
                          <span className="font-black text-sm truncate block sm:inline uppercase tracking-tight">
                            {trip.departure_city}
                          </span>
                          <span className="text-klando-gold text-xs sm:hidden font-bold mx-1">→</span>
                          <span className="text-muted-foreground text-[11px] truncate block sm:hidden font-medium">
                            {trip.destination_city}
                          </span>
                        </div>
                        <span className="text-muted-foreground text-[11px] truncate hidden sm:block font-medium">
                          → {trip.destination_city}
                        </span>
                        {/* Date visible seulement sur mobile ici */}
                        <span className="text-[10px] text-muted-foreground/60 md:hidden mt-1 font-mono">
                          {formatDate(trip.departure_schedule)}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell className="hidden sm:table-cell text-sm font-bold">
                      {formatDistance(trip.trip_distance)}
                    </TableCell>
                    <TableCell className="hidden md:table-cell text-xs font-mono text-muted-foreground">
                      {formatDate(trip.departure_schedule)}
                    </TableCell>
                    <TableCell className="text-sm font-black">
                      <span className="text-klando-gold">{trip.passengers.length}</span>
                      <span className="text-muted-foreground mx-0.5">/</span>
                      <span>{trip.total_seats}</span>
                    </TableCell>
                    <TableCell>
                      <span
                        className={cn(
                          "px-2.5 py-1 rounded-lg text-[9px] font-black uppercase tracking-wider whitespace-nowrap",
                          statusColors[trip.status] || "bg-gray-500/10 text-gray-400"
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
