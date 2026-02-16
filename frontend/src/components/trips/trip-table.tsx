"use client";

import { Trip } from "@/types/trip";
import { cn } from "@/lib/utils";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Loader2, ChevronLeft, ChevronRight } from "lucide-react";
import { useTripFilters } from "./hooks/useTripFilters";
import { TripFilters } from "./sub-components/TripFilters";
import { TripTableRow } from "./sub-components/TripTableRow";
import { Button } from "@/components/ui/button";

interface TripTableProps {
  trips: Trip[];
  totalCount: number;
  currentPage: number;
  pageSize: number;
  selectedTripId: string | null;
  initialSelectedId?: string | null;
  onSelectTrip: (trip: Trip) => void;
}

export function TripTable({ 
  trips, 
  totalCount,
  currentPage,
  pageSize,
  selectedTripId, 
  onSelectTrip 
}: TripTableProps) {
  const filterState = useTripFilters();
  const totalPages = Math.ceil(totalCount / pageSize);

  const PaginationControls = ({ className }: { className?: string }) => (
    <div className={cn("flex items-center gap-2", className)}>
      <Button
        variant="outline"
        size="icon"
        className="h-8 w-8"
        onClick={() => filterState.updateFilters({ page: (currentPage - 1).toString() })}
        disabled={currentPage <= 1 || filterState.isPending}
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
        onClick={() => filterState.updateFilters({ page: (currentPage + 1).toString() })}
        disabled={currentPage >= totalPages || filterState.isPending}
      >
        <ChevronRight className="h-4 w-4" />
      </Button>
    </div>
  );

  return (
    <div className="space-y-4">
      <TripFilters 
        {...filterState}
        totalCount={totalCount}
        currentPage={currentPage}
        totalPages={totalPages}
      />

      <div className="rounded-xl border border-border/40 bg-card overflow-hidden shadow-sm relative">
        {filterState.isPending && (
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
                    {filterState.hasActiveFilters ? "Aucun trajet ne correspond à ces critères" : "Aucun trajet trouvé"}
                  </TableCell>
                </TableRow>
              ) : (
                trips.map((trip) => (
                  <TripTableRow 
                    key={trip.trip_id}
                    trip={trip}
                    isSelected={selectedTripId === trip.trip_id}
                    onSelect={onSelectTrip}
                  />
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>

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
