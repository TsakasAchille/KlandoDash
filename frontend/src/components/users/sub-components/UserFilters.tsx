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
import { Search, Loader2, Filter, X, Sparkles, User2, Calendar, ChevronLeft, ChevronRight } from "lucide-react";

interface UserFiltersProps {
  searchTerm: string;
  setSearchTerm: (value: string) => void;
  roleFilter: string;
  verifiedFilter: string;
  genderFilter: string;
  minRatingFilter: string;
  isNewFilter: boolean;
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

export function UserFilters({
  searchTerm,
  setSearchTerm,
  roleFilter,
  verifiedFilter,
  genderFilter,
  minRatingFilter,
  isNewFilter,
  showAdvanced,
  setShowAdvanced,
  isPending,
  hasActiveFilters,
  totalCount,
  currentPage,
  totalPages,
  updateFilters,
  clearFilters
}: UserFiltersProps) {
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
              placeholder="Nom, email, tel..."
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
            <Select value={roleFilter} onValueChange={(v) => updateFilters({ role: v, page: "1" })}>
              <SelectTrigger className="h-9 w-[130px] text-xs font-bold uppercase tracking-wider border-klando-gold/20">
                <SelectValue placeholder="Rôle" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tout Rôle</SelectItem>
                <SelectItem value="driver">Conducteurs</SelectItem>
                <SelectItem value="passenger">Passagers</SelectItem>
              </SelectContent>
            </Select>

            <Select value={verifiedFilter} onValueChange={(v) => updateFilters({ verified: v, page: "1" })}>
              <SelectTrigger className="h-9 w-[110px] text-xs font-bold uppercase tracking-wider">
                <SelectValue placeholder="Vérif." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tout Statut</SelectItem>
                <SelectItem value="true">Vérifiés</SelectItem>
                <SelectItem value="false">Non vérifiés</SelectItem>
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
            {totalCount} membres
          </span>
          {totalPages > 1 && <PaginationControls />}
        </div>
      </div>

      {showAdvanced && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 p-4 rounded-xl bg-secondary/20 border border-border/40 animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
              <User2 className="w-3 h-3" /> Genre
            </label>
            <Select value={genderFilter} onValueChange={(v) => updateFilters({ gender: v, page: "1" })}>
              <SelectTrigger className="h-8 text-[11px] font-bold">
                <SelectValue placeholder="Genre" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous</SelectItem>
                <SelectItem value="man">Homme</SelectItem>
                <SelectItem value="woman">Femme</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
              <Sparkles className="w-3 h-3" /> Note minimale
            </label>
            <Select value={minRatingFilter} onValueChange={(v) => updateFilters({ minRating: v, page: "1" })}>
              <SelectTrigger className="h-8 text-[11px] font-bold">
                <SelectValue placeholder="Note" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="0">Toutes les notes</SelectItem>
                <SelectItem value="3">3.0 et +</SelectItem>
                <SelectItem value="4">4.0 et +</SelectItem>
                <SelectItem value="4.5">4.5 et +</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
              <Calendar className="w-3 h-3" /> Ancienneté
            </label>
            <Button
              variant={isNewFilter ? "default" : "outline"}
              size="sm"
              className={cn(
                "h-8 w-full text-[11px] font-bold",
                isNewFilter && "bg-klando-gold text-black hover:bg-klando-gold/90"
              )}
              onClick={() => updateFilters({ isNew: (!isNewFilter).toString(), page: "1" })}
            >
              Nouveaux membres (-30j)
            </Button>
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
