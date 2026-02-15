"use client";

import { useState, useEffect, useTransition } from "react";
import { UserListItem } from "@/types/user";
import { formatDate, cn } from "@/lib/utils";
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
import { ChevronLeft, ChevronRight, Star, Search, Loader2, Filter, X, Sparkles, User2, Calendar } from "lucide-react";
import Image from "next/image";
import { useRouter, useSearchParams } from "next/navigation";

interface UserTableProps {
  users: UserListItem[];
  totalCount: number;
  currentPage: number;
  pageSize: number;
  selectedUserId: string | null;
  initialSelectedId?: string | null;
  onSelectUser: (user: UserListItem) => void;
}

export function UserTable({ 
  users, 
  totalCount,
  currentPage,
  pageSize,
  selectedUserId, 
  onSelectUser 
}: UserTableProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [searchTerm, setSearchTerm] = useState(searchParams.get("search") || "");
  const roleFilter = searchParams.get("role") || "all";
  const verifiedFilter = searchParams.get("verified") || "all";
  const genderFilter = searchParams.get("gender") || "all";
  const minRatingFilter = searchParams.get("minRating") || "0";
  const isNewFilter = searchParams.get("isNew") === "true";

  // Calculate pagination
  const totalPages = Math.ceil(totalCount / pageSize);

  const updateFilters = (newParams: Record<string, string | null>) => {
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
      router.push(`/users?${params.toString()}`);
    });
  };

  const handlePageChange = (newPage: number) => {
    if (newPage < 1 || newPage > totalPages) return;
    updateFilters({ page: newPage.toString() });
  };

  const clearFilters = () => {
    setSearchTerm("");
    startTransition(() => {
      router.push("/users");
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
  }, [searchTerm]);

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
              {/* Filtre Rôle - Basé sur colonne role (driver / passenger) */}
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

              {/* Filtre Vérification - Basé sur is_driver_doc_validated */}
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

        {/* Advanced Filters Panel */}
        {showAdvanced && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 p-4 rounded-xl bg-secondary/20 border border-border/40 animate-in fade-in slide-in-from-top-2 duration-200">
            {/* Gender */}
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

            {/* Note Min */}
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

            {/* Nouveauté */}
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

            {/* Clear Actions */}
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

      {/* Tableau responsive */}
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
                <TableHead className="text-klando-gold font-black uppercase tracking-widest text-[9px] py-3">Membre</TableHead>
                <TableHead className="text-klando-gold font-black uppercase tracking-widest text-[9px] hidden sm:table-cell">Email</TableHead>
                <TableHead className="text-klando-gold font-black uppercase tracking-widest text-[9px] hidden md:table-cell">Téléphone</TableHead>
                <TableHead className="text-klando-gold font-black uppercase tracking-widest text-[9px]">Note</TableHead>
                <TableHead className="text-klando-gold font-black uppercase tracking-widest text-[9px]">Type</TableHead>
                <TableHead className="text-klando-gold font-black uppercase tracking-widest text-[9px] hidden lg:table-cell">Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-muted-foreground py-10 text-sm">
                    {hasActiveFilters ? "Aucun membre ne correspond à ces critères" : "Aucun utilisateur trouvé"}
                  </TableCell>
                </TableRow>
              ) : (
                users.map((user) => (
                  <TableRow
                    key={user.uid}
                    data-user-id={user.uid}
                    data-state={selectedUserId === user.uid ? "selected" : undefined}
                    className="cursor-pointer transition-colors hover:bg-secondary/20 border-b border-border/10 last:border-0"
                    onClick={() => onSelectUser(user)}
                  >
                    <TableCell className="py-3">
                      <div className="flex items-center gap-3">
                        <div className="relative flex-shrink-0">
                          {user.photo_url ? (
                            <Image
                              src={user.photo_url}
                              alt=""
                              width={32}
                              height={32}
                              className="w-8 h-8 rounded-lg object-cover border border-border/50"
                            />
                          ) : (
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-klando-burgundy to-klando-burgundy/60 flex items-center justify-center text-white text-[10px] font-black shadow-inner">
                              {(user.display_name || "?").charAt(0).toUpperCase()}
                            </div>
                          )}
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center gap-1.5 mb-0.5">
                            <p className="font-bold truncate text-xs uppercase tracking-tight leading-none">
                              {user.display_name || "Sans nom"}
                            </p>
                            {user.created_at && new Date(user.created_at) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) && (
                              <span className="h-1.5 w-1.5 rounded-full bg-blue-500" title="Nouveau membre" />
                            )}
                          </div>
                          <p className="text-[9px] sm:hidden text-muted-foreground truncate font-medium">
                            {user.email || "-"}
                          </p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="hidden sm:table-cell text-[11px] font-medium text-muted-foreground truncate max-w-[150px]">
                      {user.email || "-"}
                    </TableCell>
                    <TableCell className="hidden md:table-cell text-[11px] font-mono font-bold">
                      {user.phone_number || "-"}
                    </TableCell>
                    <TableCell>
                      {user.rating ? (
                        <div className="flex items-center gap-1">
                          <Star className="w-3 h-3 fill-klando-gold text-klando-gold" />
                          <span className="text-xs font-black">{user.rating.toFixed(1)}</span>
                        </div>
                      ) : (
                        <span className="text-muted-foreground text-[10px]">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1.5">
                        <span
                          className={cn(
                            "px-1.5 py-0.5 rounded text-[8px] font-black uppercase tracking-wider",
                            user.is_driver_doc_validated
                              ? "bg-green-500/10 text-green-500 border border-green-500/20"
                              : user.role === "driver"
                              ? "bg-blue-500/10 text-blue-500 border border-blue-500/20"
                              : user.role === "passenger"
                              ? "bg-purple-500/10 text-purple-500 border border-purple-500/20"
                              : "bg-secondary text-muted-foreground border border-border/50"
                          )}
                        >
                          {user.is_driver_doc_validated 
                            ? "Vérifié" 
                            : user.role === "driver" 
                            ? "Conducteur" 
                            : user.role === "passenger"
                            ? "Passager"
                            : "Membre"}
                        </span>
                        {user.gender && (
                          <span className={cn(
                            "text-[10px]",
                            user.gender.toLowerCase() === "man" ? "text-blue-400" : "text-pink-400"
                          )}>
                            {user.gender.toLowerCase() === "man" ? "♂" : "♀"}
                          </span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="hidden lg:table-cell text-[10px] font-mono text-muted-foreground">
                      {user.created_at ? formatDate(user.created_at) : "-"}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* Bottom pagination only if many pages */}
      {totalPages > 3 && (
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
