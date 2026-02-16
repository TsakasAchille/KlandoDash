"use client";

import { UserListItem } from "@/types/user";
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
import { useUserFilters } from "./hooks/useUserFilters";
import { UserFilters } from "./sub-components/UserFilters";
import { UserTableRow } from "./sub-components/UserTableRow";
import { Button } from "@/components/ui/button";

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
  const filterState = useUserFilters();
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
      <UserFilters 
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
                    {filterState.hasActiveFilters ? "Aucun membre ne correspond à ces critères" : "Aucun utilisateur trouvé"}
                  </TableCell>
                </TableRow>
              ) : (
                users.map((user) => (
                  <UserTableRow 
                    key={user.uid}
                    user={user}
                    isSelected={selectedUserId === user.uid}
                    onSelect={onSelectUser}
                  />
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>

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
