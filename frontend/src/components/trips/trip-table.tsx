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
import { ChevronLeft, ChevronRight } from "lucide-react";
import { TripTableRow } from "./sub-components/TripTableRow";
import { Button } from "@/components/ui/button";

interface TripTableProps {
  trips: Trip[];
  totalCount: number;
  currentPage: number;
  pageSize: number;
  selectedTripId: string | null;
  onSelectTrip: (trip: Trip) => void;
  onPageChange: (page: number) => void;
}

export function TripTable({ 
  trips, 
  totalCount,
  currentPage,
  pageSize,
  selectedTripId, 
  onSelectTrip,
  onPageChange
}: TripTableProps) {
  const totalPages = Math.ceil(totalCount / pageSize);

  const PaginationControls = ({ className }: { className?: string }) => (
    <div className={cn("flex items-center gap-2", className)}>
      <Button
        variant="outline"
        size="icon"
        className="h-8 w-8"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage <= 1}
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
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage >= totalPages}
      >
        <ChevronRight className="h-4 w-4" />
      </Button>
    </div>
  );

  return (
    <div className="space-y-4">
      {/* On affiche les infos de résumé car les filtres sont gérés par StatCards au dessus */}
      <div className="flex items-center justify-between px-6 py-2 bg-muted/20 rounded-2xl border border-border/10">
        <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
            {totalCount} trajets dans cette catégorie
        </p>
        {totalPages > 1 && <PaginationControls />}
      </div>

      <div className="rounded-[2.5rem] border border-border/40 bg-card/40 backdrop-blur-md overflow-hidden shadow-sm relative">
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
                    Aucun résultat trouvé dans cette catégorie.
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
