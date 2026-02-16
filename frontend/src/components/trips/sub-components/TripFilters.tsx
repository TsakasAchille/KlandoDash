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
    <div className="flex flex-col gap-4 bg-card/50 p-4 rounded-[2rem] border border-border/40 shadow-sm">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 flex-1">
          <div className="relative flex-1 max-w-xl">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Rechercher par ville de départ, d'arrivée ou ID de trajet..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-11 h-12 text-sm rounded-2xl bg-background/50 border-border/60 focus:border-klando-gold/50 transition-all"
            />
            {isPending && (
              <div className="absolute right-4 top-1/2 -translate-y-1/2">
                <Loader2 className="h-4 w-4 animate-spin text-klando-gold" />
              </div>
            )}
          </div>
          
          <div className="flex items-center gap-3">
            <Select value={statusFilter} onValueChange={(v) => updateFilters({ status: v, page: "1" })}>
              <SelectTrigger className="h-12 w-[180px] text-[10px] font-black uppercase tracking-widest rounded-2xl border-border/60 bg-background/50">
                <SelectValue placeholder="STATUT DU TRAJET" />
              </SelectTrigger>
              <SelectContent className="rounded-2xl border-border/60">
                <SelectItem value="all">TOUS LES TRAJETS</SelectItem>
                <SelectItem value="ACTIVE">TRAJETS ACTIFS</SelectItem>
                <SelectItem value="COMPLETED">TRAJETS TERMINÉS</SelectItem>
                <SelectItem value="PENDING">EN ATTENTE</SelectItem>
                <SelectItem value="CANCELLED">TRAJETS ANNULÉS</SelectItem>
              </SelectContent>
            </Select>

            <Button
              variant={showAdvanced ? "secondary" : "outline"}
              size="sm"
              className="h-12 w-12 rounded-2xl border-border/60 bg-background/50 relative p-0"
              onClick={() => setShowAdvanced(!showAdvanced)}
            >
              <Filter className="w-4 h-4" />
              {hasActiveFilters && (
                <span className="absolute top-3 right-3 flex h-2 w-2 rounded-full bg-klando-gold border-2 border-background" />
              )}
            </Button>
          </div>
        </div>

        <div className="flex items-center justify-between sm:justify-end gap-6 border-t lg:border-t-0 pt-4 lg:pt-0 px-2">
          <div className="flex flex-col items-end">
            <span className="text-[10px] font-black uppercase tracking-[0.2em] text-klando-gold leading-none mb-1">
              Base de données
            </span>
            <span className="text-sm font-black text-foreground">
              {totalCount} <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest ml-1">trajets trouvés</span>
            </span>
          </div>
          <div className="h-8 w-[1px] bg-border/40 hidden sm:block" />
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
