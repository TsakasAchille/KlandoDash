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
import { ChevronLeft, ChevronRight, Star, Search, Loader2 } from "lucide-react";
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

  const [searchTerm, setSearchTerm] = useState(searchParams.get("search") || "");
  const roleFilter = searchParams.get("role") || "all";

  // Calculate pagination
  const totalPages = Math.ceil(totalCount / pageSize);

  const updateFilters = (newParams: Record<string, string | null>) => {
    const params = new URLSearchParams(searchParams.toString());
    
    Object.entries(newParams).forEach(([key, value]) => {
      if (value === null || value === "all" || value === "") {
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

  const handleRoleChange = (value: string) => {
    updateFilters({ role: value, page: "1" });
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchTerm !== (searchParams.get("search") || "")) {
        updateFilters({ search: searchTerm, page: "1" });
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  const roles = ["admin", "user", "support"];

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
      {/* Top Bar: Search & Compact Pagination */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 flex-1">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Nom, email, tel..."
              value={searchTerm}
              onChange={handleSearchChange}
              className="pl-9 h-9 text-sm"
            />
            {isPending && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <Loader2 className="h-3 w-3 animate-spin text-muted-foreground" />
              </div>
            )}
          </div>
          <Select value={roleFilter} onValueChange={handleRoleChange}>
            <SelectTrigger className="h-9 w-full sm:w-32 text-xs font-bold uppercase tracking-wider">
              <SelectValue placeholder="Rôle" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous</SelectItem>
              {roles.map((role) => (
                <SelectItem key={role} value={role}>
                  {role}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center justify-between sm:justify-end gap-4 border-t lg:border-t-0 pt-3 lg:pt-0">
          <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
            {totalCount} membres
          </span>
          {totalPages > 1 && <PaginationControls />}
        </div>
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
                <TableHead className="text-klando-gold font-black uppercase tracking-widest text-[9px]">Rôle</TableHead>
                <TableHead className="text-klando-gold font-black uppercase tracking-widest text-[9px] hidden lg:table-cell">Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-muted-foreground py-10 text-sm">
                    Aucun utilisateur trouvé
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
                          <p className="font-bold truncate text-xs uppercase tracking-tight leading-none mb-1">
                            {user.display_name || "Sans nom"}
                          </p>
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
                      <span
                        className={cn(
                          "px-1.5 py-0.5 rounded text-[8px] font-black uppercase tracking-wider",
                          user.role === "admin"
                            ? "bg-purple-500/10 text-purple-400 border border-purple-500/20"
                            : "bg-secondary text-muted-foreground border border-border/50"
                        )}
                      >
                        {user.role || "user"}
                      </span>
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
