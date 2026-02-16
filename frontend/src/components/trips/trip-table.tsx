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

      <div className="rounded-[2.5rem] border border-border/40 bg-card/40 backdrop-blur-md overflow-hidden shadow-sm relative">
        {filterState.isPending && (
          <div className="absolute inset-0 bg-background/50 backdrop-blur-[1px] z-10 flex items-center justify-center">
            <Loader2 className="h-10 w-10 animate-spin text-klando-gold" />
          </div>
        )}
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/50 hover:bg-muted/50 border-b border-border/40">
                <TableHead className="text-klando-dark font-black uppercase tracking-[0.2em] text-[10px] py-5 px-6">Identité du Trajet</TableHead>
                <TableHead className="text-klando-dark font-black uppercase tracking-[0.2em] text-[10px] hidden sm:table-cell px-6 text-center">Logistique</TableHead>
                <TableHead className="text-klando-dark font-black uppercase tracking-[0.2em] text-[10px] hidden md:table-cell px-6 text-center">Calendrier</TableHead>
                <TableHead className="text-klando-dark font-black uppercase tracking-[0.2em] text-[10px] px-6 text-center">Réservation</TableHead>
                <TableHead className="text-klando-dark font-black uppercase tracking-[0.2em] text-[10px] px-6 text-right">État</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {trips.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-muted-foreground py-20 text-sm italic">
                    {filterState.hasActiveFilters ? "Aucun résultat pour cette recherche..." : "Aucun trajet dans la base."}
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
