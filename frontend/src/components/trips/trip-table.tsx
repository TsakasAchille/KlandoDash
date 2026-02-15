"use client";

import { useState, useEffect, useTransition, useCallback } from "react";
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
import { ChevronLeft, ChevronRight, Search, Loader2, Filter, X, Banknote } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";

interface TripTableProps {
  trips: Trip[];
  totalCount: number;
  currentPage: number;
  pageSize: number;
  selectedTripId: string | null;
  initialSelectedId?: string | null;
  onSelectTrip: (trip: Trip) => void;
}

const statusColors: Record<string, string> = {
  COMPLETED: "bg-green-500/10 text-green-500 border-green-500/20",
  ACTIVE: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  PENDING: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
  CANCELLED: "bg-red-500/10 text-red-500 border-red-500/20",
  ARCHIVED: "bg-gray-500/10 text-gray-400 border-gray-500/20",
};

export function TripTable({ 
  trips, 
  totalCount,
  currentPage,
  pageSize,
  selectedTripId, 
  onSelectTrip 
}: TripTableProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [searchTerm, setSearchTerm] = useState(searchParams.get("search") || "");
  const statusFilter = searchParams.get("status") || "all";
  const maxPriceFilter = searchParams.get("maxPrice") || "";

  // Calculate pagination
  const totalPages = Math.ceil(totalCount / pageSize);

  const updateFilters = useCallback((newParams: Record<string, string | null>) => {
    const params = new URLSearchParams(searchParams.toString());
    
    Object.entries(newParams).forEach(([key, value]) => {
      if (value === null || value === "all" || value === "" || value === "0" || value === "false") {
        params.delete(key);
      } else {
        params.set(key, value);
      }
    });

    if (!newParams.page && newParams.page !== undefined) {
      params.delete("page");
    }

    startTransition(() => {
      router.push(`/trips?${params.toString()}`);
    });
  }, [router, searchParams]);

  const handlePageChange = (newPage: number) => {
    if (newPage < 1 || newPage > totalPages) return;
    updateFilters({ page: newPage.toString() });
  };

  const clearFilters = () => {
    setSearchTerm("");
    startTransition(() => {
      router.push("/trips");
    });
  };

  const hasActiveFilters = searchParams.toString().length > 0 && !searchParams.has("selected");

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchTerm !== (searchParams.get("search") || "")) {
        updateFilters({ search: searchTerm, page: "1" });
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [searchTerm, searchParams, updateFilters]);

  const PaginationControls = ({ className }: { className?: string }) => (
    <div className={cn("flex items-center gap-2", className)}>
      <Button
        variant="outline"
        size="icon"
        className="h-8 w-8"
        onClick={() => handlePageChange(currentPage - 1)}
        disabled={currentPage <= 1 || isPending}
      >
        <ChevronLeft className="h-4 w-4" />
      </Button>
      <div className="text-[10px] font-black uppercase tracking-widest text-muted-foreground whitespace-nowrap px-2">
        {currentPage} / {totalPages || 1}
      </div>
      <Button
        variant="outline"
        size="icon"
        className="h-8 w-8"
        onClick={() => handlePageChange(currentPage + 1)}
        disabled={currentPage >= totalPages || isPending}
      >
        <ChevronRight className="h-4 w-4" />
      </Button>
    </div>
  );

  return (
    <div className="space-y-4">
      {/* Search and Main Filters */}
      <div className="flex flex-col gap-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 flex-1">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Départ, arrivée ou ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 h-9 text-sm"
              />
              {isPending && (
                <div className="absolute right-3 top-1/2 -translate-y-1/2">
                  <Loader2 className="h-3 w-3 animate-spin text-muted-foreground" />
                </div>
              )}
            </div>
            
            <div className="flex items-center gap-2">
              <Select value={statusFilter} onValueChange={(v) => updateFilters({ status: v, page: "1" })}>
                <SelectTrigger className="h-9 w-[140px] text-xs font-bold uppercase tracking-wider">
                  <SelectValue placeholder="Statut" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tous les trajets</SelectItem>
                  <SelectItem value="ACTIVE">Actifs</SelectItem>
                  <SelectItem value="COMPLETED">Terminés</SelectItem>
                  <SelectItem value="PENDING">En attente</SelectItem>
                  <SelectItem value="CANCELLED">Annulés</SelectItem>
                </SelectContent>
              </Select>

              <Button
                variant={showAdvanced ? "secondary" : "outline"}
                size="sm"
                className="h-9 gap-2 text-xs font-bold uppercase tracking-wider"
                onClick={() => setShowAdvanced(!showAdvanced)}
              >
                <Filter className="w-3.5 h-3.5" />
                {hasActiveFilters && (
                  <span className="flex h-2 w-2 rounded-full bg-klando-gold" />
                )}
              </Button>
            </div>
          </div>

          <div className="flex items-center justify-between sm:justify-end gap-4 border-t lg:border-t-0 pt-3 lg:pt-0">
            <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
              {totalCount} trajets
            </span>
            {totalPages > 1 && <PaginationControls />}
          </div>
        </div>

        {/* Advanced Filters Panel */}
        {showAdvanced && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 p-4 rounded-xl bg-secondary/20 border border-border/40 animate-in fade-in slide-in-from-top-2 duration-200">
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
                <Banknote className="w-3 h-3" /> Prix max (FCFA)
              </label>
              <Input
                type="number"
                placeholder="Ex: 5000"
                value={maxPriceFilter}
                onChange={(e) => updateFilters({ maxPrice: e.target.value, page: "1" })}
                className="h-8 text-xs font-bold"
              />
            </div>

            <div className="flex items-center">
              <p className="text-[10px] text-muted-foreground italic">
                La pagination est désormais gérée côté serveur pour plus de fluidité.
              </p>
            </div>

            <div className="flex flex-col justify-end gap-2">
              <Button
                variant="ghost"
                size="sm"
                className="h-8 text-[10px] font-black uppercase tracking-widest text-muted-foreground hover:text-foreground"
                onClick={clearFilters}
              >
                <X className="w-3 h-3 mr-2" />
                Réinitialiser tout
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="rounded-xl border border-border/40 bg-card overflow-hidden shadow-sm relative">
        {isPending && (
          <div className="absolute inset-0 bg-background/50 backdrop-blur-[1px] z-10 flex items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-klando-gold" />
          </div>
        )}
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/30 hover:bg-muted/30 border-b border-border/40">
                <TableHead className="text-klando-gold font-black uppercase tracking-widest text-[9px] py-3">Trajet</TableHead>
                <TableHead className="text-klando-gold font-black uppercase tracking-widest text-[9px] hidden sm:table-cell">Distance</TableHead>
                <TableHead className="text-klando-gold font-black uppercase tracking-widest text-[9px] hidden md:table-cell">Date</TableHead>
                <TableHead className="text-klando-gold font-black uppercase tracking-widest text-[9px]">Places</TableHead>
                <TableHead className="text-klando-gold font-black uppercase tracking-widest text-[9px]">Statut</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {trips.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-muted-foreground py-10 text-sm">
                    {hasActiveFilters ? "Aucun trajet ne correspond à ces critères" : "Aucun trajet trouvé"}
                  </TableCell>
                </TableRow>
              ) : (
                trips.map((trip) => (
                  <TableRow
                    key={trip.trip_id}
                    data-trip-id={trip.trip_id}
                    data-state={selectedTripId === trip.trip_id ? "selected" : undefined}
                    className="cursor-pointer transition-colors hover:bg-secondary/20 border-b border-border/10 last:border-0"
                    onClick={() => onSelectTrip(trip)}
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
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* Bottom pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-2">
          <p className="text-[10px] text-muted-foreground font-medium italic">
            Astuce: cliquez sur une ligne pour voir les détails
          </p>
          <PaginationControls />
        </div>
      )}
    </div>
  );
}
