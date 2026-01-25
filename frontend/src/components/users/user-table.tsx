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
import { ChevronLeft, ChevronRight, Star } from "lucide-react";

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

  // Filter users by role
  const filteredUsers = useMemo(() => {
    if (roleFilter === "all") return users;
    return users.filter((user) => user.role === roleFilter);
  }, [users, roleFilter]);

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

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex items-center gap-4">
        <Select value={roleFilter} onValueChange={handleFilterChange}>
          <SelectTrigger className="w-40">
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
        <span className="text-sm text-muted-foreground">
          {filteredUsers.length} utilisateur{filteredUsers.length > 1 ? "s" : ""}
        </span>
      </div>

      {/* Table */}
      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow className="bg-klando-dark hover:bg-klando-dark">
              <TableHead className="text-klando-gold">Utilisateur</TableHead>
              <TableHead className="text-klando-gold">Email</TableHead>
              <TableHead className="text-klando-gold">Téléphone</TableHead>
              <TableHead className="text-klando-gold">Note</TableHead>
              <TableHead className="text-klando-gold">Rôle</TableHead>
              <TableHead className="text-klando-gold">Inscrit le</TableHead>
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
                          className="w-8 h-8 rounded-full object-cover"
                        />
                      ) : (
                        <div className="w-8 h-8 rounded-full bg-klando-burgundy flex items-center justify-center text-white text-sm font-semibold">
                          {(user.display_name || "?").charAt(0).toUpperCase()}
                        </div>
                      )}
                      <span className="font-medium truncate max-w-[150px]">
                        {user.display_name || "Sans nom"}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="text-sm truncate max-w-[180px]">
                    {user.email || "-"}
                  </TableCell>
                  <TableCell className="text-sm">
                    {user.phone_number || "-"}
                  </TableCell>
                  <TableCell>
                    {user.rating ? (
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 fill-klando-gold text-klando-gold" />
                        <span>{user.rating.toFixed(1)}</span>
                        <span className="text-muted-foreground text-xs">
                          ({user.rating_count || 0})
                        </span>
                      </div>
                    ) : (
                      <span className="text-muted-foreground">-</span>
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
                  <TableCell className="text-sm text-muted-foreground">
                    {user.created_at ? formatDate(user.created_at) : "-"}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
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
