"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Search, Loader2, Filter, X, Banknote, ChevronLeft, ChevronRight } from "lucide-react";

interface TripFiltersProps {
  searchTerm: string;
  setSearchTerm: (value: string) => void;
  statusFilter: string;
  maxPriceFilter: string;
  showAdvanced: boolean;
  setShowAdvanced: (value: boolean) => void;
  isPending: boolean;
  hasActiveFilters: boolean;
  totalCount: number;
  currentPage: number;
  totalPages: number;
  updateFilters: (params: Record<string, string | null>) => void;
  clearFilters: () => void;
}

export function TripFilters({
  searchTerm,
  setSearchTerm,
  statusFilter,
  maxPriceFilter,
  showAdvanced,
  setShowAdvanced,
  isPending,
  hasActiveFilters,
  totalCount,
  currentPage,
  totalPages,
  updateFilters,
  clearFilters
}: TripFiltersProps) {
  const handlePageChange = (newPage: number) => {
    if (newPage < 1 || newPage > totalPages) return;
    updateFilters({ page: newPage.toString() });
  };

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
  );
}
