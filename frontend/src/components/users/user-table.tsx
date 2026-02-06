"use client";

import { useState, useMemo } from "react";
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
import { ChevronLeft, ChevronRight, Star, Search } from "lucide-react";

interface UserTableProps {
  users: UserListItem[];
  selectedUserId: string | null;
  initialSelectedId?: string | null;
  onSelectUser: (user: UserListItem) => void;
}

const ITEMS_PER_PAGE = 10;

export function UserTable({ users, selectedUserId, initialSelectedId, onSelectUser }: UserTableProps) {
  // Calculer la page initiale basée sur l'utilisateur sélectionné
  const getInitialPage = () => {
    if (!initialSelectedId) return 1;
    const index = users.findIndex((u) => u.uid === initialSelectedId);
    if (index === -1) return 1;
    return Math.floor(index / ITEMS_PER_PAGE) + 1;
  };

  const [currentPage, setCurrentPage] = useState(getInitialPage);
  const [roleFilter, setRoleFilter] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState("");

  // Filter users by role and search term
  const filteredUsers = useMemo(() => {
    return users.filter((user) => {
      const matchesRole = roleFilter === "all" || user.role === roleFilter;
      const matchesSearch = 
        (user.display_name?.toLowerCase() || "").includes(searchTerm.toLowerCase()) ||
        (user.email?.toLowerCase() || "").includes(searchTerm.toLowerCase());
      
      return matchesRole && matchesSearch;
    });
  }, [users, roleFilter, searchTerm]);

  // Calculate pagination
  const totalPages = Math.ceil(filteredUsers.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const paginatedUsers = filteredUsers.slice(startIndex, startIndex + ITEMS_PER_PAGE);

  // Get unique roles for filter
  const roles = useMemo(() => {
    const uniqueRoles = Array.from(new Set(users.map((u) => u.role).filter(Boolean)));
    return uniqueRoles.sort();
  }, [users]);

  // Reset to page 1 when filter changes
  const handleFilterChange = (value: string) => {
    setRoleFilter(value);
    setCurrentPage(1);
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  return (
    <div className="space-y-4">
      {/* Filtres responsive */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Rechercher un nom ou email..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="pl-9 w-full"
          />
        </div>
        <div className="flex items-center gap-4">
          <Select value={roleFilter} onValueChange={handleFilterChange}>
            <SelectTrigger className="w-full sm:w-40">
              <SelectValue placeholder="Rôle" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous les rôles</SelectItem>
              {roles.map((role) => (
                <SelectItem key={role} value={role!}>
                  {role}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <span className="text-sm text-muted-foreground whitespace-nowrap">
            {filteredUsers.length} utilisateur{filteredUsers.length > 1 ? "s" : ""}
          </span>
        </div>
      </div>

      {/* Tableau responsive */}
      <div className="rounded-lg border bg-card overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="bg-klando-dark hover:bg-klando-dark">
              <TableHead className="text-klando-gold min-w-[100px]">Utilisateur</TableHead>
              <TableHead className="text-klando-gold min-w-[120px] hidden sm:table-cell">Email</TableHead>
              <TableHead className="text-klando-gold min-w-[100px] hidden md:table-cell">Téléphone</TableHead>
              <TableHead className="text-klando-gold min-w-[80px]">Note</TableHead>
              <TableHead className="text-klando-gold min-w-[80px]">Rôle</TableHead>
              <TableHead className="text-klando-gold min-w-[100px] hidden lg:table-cell">Inscrit le</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedUsers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                  Aucun utilisateur trouvé
                </TableCell>
              </TableRow>
            ) : (
              paginatedUsers.map((user) => (
                <TableRow
                  key={user.uid}
                  data-user-id={user.uid}
                  data-state={selectedUserId === user.uid ? "selected" : undefined}
                  className="cursor-pointer transition-all"
                  onClick={() => onSelectUser(user)}
                >
                  <TableCell>
                    <div className="flex items-center gap-3">
                      {user.photo_url ? (
                        <img
                          src={user.photo_url}
                          alt=""
                          className="w-8 h-8 sm:w-10 sm:h-10 rounded-full object-cover"
                        />
                      ) : (
                        <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-klando-burgundy flex items-center justify-center text-white text-sm sm:font-semibold">
                          {(user.display_name || "?").charAt(0).toUpperCase()}
                        </div>
                      )}
                      <div className="min-w-0 flex-1">
                        <span className="font-medium truncate text-sm sm:text-base">
                          {user.display_name || "Sans nom"}
                        </span>
                        {/* Email visible uniquement sur mobile dans la même cellule */}
                        <span className="text-xs sm:hidden text-muted-foreground block truncate">
                          {user.email || "-"}
                        </span>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="hidden sm:table-cell text-sm truncate max-w-[180px]">
                    {user.email || "-"}
                  </TableCell>
                  <TableCell className="hidden md:table-cell text-sm">
                    {user.phone_number || "-"}
                  </TableCell>
                  <TableCell>
                    {user.rating ? (
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 fill-klando-gold text-klando-gold" />
                        <span className="text-sm">{user.rating.toFixed(1)}</span>
                        <span className="text-muted-foreground text-xs">
                          ({user.rating_count || 0})
                        </span>
                      </div>
                    ) : (
                      <span className="text-muted-foreground text-sm">-</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <span
                      className={cn(
                        "px-2 py-1 rounded-full text-xs font-medium",
                        user.role === "admin"
                          ? "bg-purple-500/20 text-purple-400"
                          : "bg-secondary text-muted-foreground"
                      )}
                    >
                      {user.role || "user"}
                    </span>
                  </TableCell>
                  <TableCell className="hidden lg:table-cell text-sm text-muted-foreground">
                    {user.created_at ? formatDate(user.created_at) : "-"}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination responsive */}
      {totalPages > 1 && (
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <span className="text-sm text-muted-foreground">
            Page {currentPage} sur {totalPages}
          </span>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
